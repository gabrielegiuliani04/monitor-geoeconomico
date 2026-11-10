#!/usr/bin/env python3
"""Military aircraft layer -> docs/data/aerei.json

Two parts, both written in the schema of the aircraft items of docs/data/mobili.json
(classe "mobile", categorie aereo-cisterna / aereo-ricognizione / aereo-trasporto /
aereo-bombardiere, plus aereo-caccia which docs/index.html already draws), under the key "punti":

  1. SNAPSHOT (automatic, every run): military aircraft broadcasting ADS-B/MLAT, from public
     aggregators that allow keyless use:
       - adsb.lol      https://api.adsb.lol/v2/mil (+ a few /v2/type/<ICAO type> queries)
                       licence ODbL 1.0 -> attribution "adsb.lol contributors, ODbL 1.0", share-alike
       - adsb.fi       https://opendata.adsb.fi/api/v2/mil
                       personal, non-commercial use only; must cite adsb.fi with a link; 1 request/s
     Only strategically relevant types are kept (tankers, ISR/AWACS, strategic airlifters, bombers).
     Aircraft parked at the same base are merged into one item; aircraft flying close together
     (formations, tanker + receivers) are merged too. Every snapshot item carries the UTC time of the
     position and the note that it is a snapshot at collection time, not a live position.
     Excluded on purpose: anything not flagged military, aircraft whose owners asked for privacy
     (adsb.lol/adsb.fi dbFlags 4 = PIA, 8 = LADD), VIP/government transport callsigns (SAM, EXEC,
     SPAR, VENUS...), and every type not in the whitelist (so no business jets or helicopters).

  2. CURATED (by hand, raccolta/aerei/curati.json): deployments reported by open sources in the
     last ~60 days, each at the base with an honest precision radius. This script validates them
     (fields, categories, dates, links, coordinates) and copies them into the output.

Standard library only. Exit code 0 even when a source fails (the error goes into "errori");
exit code 1 only if curati.json is missing or not valid JSON.

Usage:
  python3 raccolta/aerei/raccogli.py            # fetch snapshot, validate curated, write
  python3 raccolta/aerei/raccogli.py --offline  # curated only (no network), keeps the old snapshot out
"""
import datetime as dt
import json
import math
import os
import re
import sys
import time
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
CURATO = os.path.join(QUI, "curati.json")
USCITA = os.path.join(RADICE, "docs", "data", "aerei.json")
ADESSO = dt.datetime.now(dt.timezone.utc)
OGGI = ADESSO.date()
UA = "monitor-geoeconomico/1.0 (personal non-commercial OSINT map; python-urllib)"

URL_LOL_MIL = "https://api.adsb.lol/v2/mil"
URL_LOL_TYPE = "https://api.adsb.lol/v2/type/{}"
URL_FI_MIL = "https://opendata.adsb.fi/api/v2/mil"
# extra type queries on adsb.lol, to catch strategic aircraft not flagged military in the database
TIPI_EXTRA = ["K35R", "R135", "E3TF", "P8", "Q4", "B52", "C17", "C5M"]

FONTE_LOL = {"nome": "adsb.lol, /v2/mil and /v2/type", "link": "https://www.adsb.lol/docs/open-data/api/",
             "licenza": "ODbL 1.0 (attribution: adsb.lol contributors; share-alike on derived databases)"}
FONTE_FI = {"nome": "adsb.fi open data, /api/v2/mil", "link": "https://github.com/adsbfi/opendata",
            "licenza": "adsb.fi terms: personal, non-commercial use; cite adsb.fi with a link to https://adsb.fi"}
FONTE_OA = {"nome": "OurAirports (base coordinates)", "link": "https://ourairports.com/data/",
            "licenza": "public domain"}

# ---------------------------------------------------------------- what we keep
# ICAO type designator -> (categoria, label). Types listed in AMBIGUI also exist as VIP/airliner
# airframes and are kept only when the description or registration says tanker/ISR.
TIPI = {
    "K35R": ("aereo-cisterna", "KC-135R/T Stratotanker"), "K35E": ("aereo-cisterna", "KC-135E Stratotanker"),
    "KC46": ("aereo-cisterna", "KC-46A Pegasus"), "IL78": ("aereo-cisterna", "Il-78 tanker"),
    "R135": ("aereo-ricognizione", "RC-135 family"), "E3TF": ("aereo-ricognizione", "E-3 Sentry AWACS"),
    "E3CF": ("aereo-ricognizione", "E-3D/F Sentry AWACS"), "E767": ("aereo-ricognizione", "E-767 AWACS"),
    "E737": ("aereo-ricognizione", "E-7 Wedgetail"), "P8": ("aereo-ricognizione", "P-8 Poseidon"),
    "Q4": ("aereo-ricognizione", "RQ-4 Global Hawk / MQ-4C Triton"), "U2": ("aereo-ricognizione", "U-2"),
    "E6": ("aereo-ricognizione", "E-6B Mercury"), "A50": ("aereo-ricognizione", "A-50 AWACS"),
    "IL20": ("aereo-ricognizione", "Il-20 reconnaissance"), "P1": ("aereo-ricognizione", "Kawasaki P-1"),
    "C17": ("aereo-trasporto", "C-17 Globemaster III"), "C5M": ("aereo-trasporto", "C-5M Super Galaxy"),
    "C5": ("aereo-trasporto", "C-5 Galaxy"), "A400": ("aereo-trasporto", "A400M Atlas"),
    "IL76": ("aereo-trasporto", "Il-76"), "A124": ("aereo-trasporto", "An-124 Ruslan"),
    "B52": ("aereo-bombardiere", "B-52H Stratofortress"), "B1": ("aereo-bombardiere", "B-1B Lancer"),
    "B2": ("aereo-bombardiere", "B-2 Spirit"), "T160": ("aereo-bombardiere", "Tu-160"),
    "TU95": ("aereo-bombardiere", "Tu-95"), "TU22": ("aereo-bombardiere", "Tu-22M"),
    "H6": ("aereo-bombardiere", "H-6"),
}
AMBIGUI = {  # type -> list of (regex on description/registration, categoria, label)
    "A332": [(r"MRTT|VOYAGER|KC-?30|KC-?2\b", "aereo-cisterna", "A330 MRTT")],
    "B762": [(r"KC-?46", "aereo-cisterna", "KC-46A Pegasus"), (r"KC-?767", "aereo-cisterna", "KC-767"),
             (r"E-?767", "aereo-ricognizione", "E-767 AWACS")],
    "B763": [(r"KC-?767", "aereo-cisterna", "KC-767")],
    "B737": [(r"E-?7|WEDGETAIL|PEACE EAGLE", "aereo-ricognizione", "E-7 Wedgetail"),
             (r"P-?8", "aereo-ricognizione", "P-8 Poseidon")],
    "B738": [(r"P-?8|POSEIDON", "aereo-ricognizione", "P-8 Poseidon")],
    "B703": [(r"E-?3|KE-?3", "aereo-ricognizione", "E-3/KE-3")],
    "GLEX": [(r"GLOBALEYE|SENTINEL|E-?11", "aereo-ricognizione", "ISR Global Express")],
}
# registrations of known MRTT/KC fleets, used when the aggregator gives no description
REG_CISTERNA = r"^(ZZ33\d|T-05\d|T-06\d|MRTT\d+|F-UJC\w|A39-\d+|MM6222\d|TK\.?\d|\d{2}-46\d{3})"
# types that are military whatever the database flag says
SEMPRE_MIL = {"K35R", "K35E", "KC46", "R135", "E3TF", "E3CF", "E767", "E6", "U2", "Q4", "B52", "B1", "B2",
              "C17", "C5M", "C5", "A400", "T160", "TU95", "TU22", "A50", "IL78", "P8"}
ESCLUDI_CALLSIGN = re.compile(r"^(SAM\d|EXEC|SPAR|VENUS|AF1$|AF2$)")
ESCLUDI_OPERATORE = re.compile(r"VIP|GOVT|GOVERNMENT|ROYAL FLIGHT|PRESIDEN|MINIST", re.I)

# ---------------------------------------------------------------- ICAO 24-bit address blocks -> country
# ICAO Annex 10 vol. III allocation (largest users; anything else -> "")
BLOCCHI = [
    ("A00000", "AFFFFF", "US"), ("400000", "43FFFF", "GB"), ("380000", "3BFFFF", "FR"), ("3C0000", "3FFFFF", "DE"),
    ("300000", "33FFFF", "IT"), ("340000", "37FFFF", "ES"), ("480000", "487FFF", "NL"), ("448000", "44FFFF", "BE"),
    ("4D0000", "4D03FF", "LU"), ("488000", "48FFFF", "PL"), ("4B8000", "4BFFFF", "TR"), ("468000", "46FFFF", "GR"),
    ("478000", "47FFFF", "NO"), ("458000", "45FFFF", "DK"), ("4A8000", "4AFFFF", "SE"), ("460000", "467FFF", "FI"),
    ("4A0000", "4A7FFF", "RO"), ("450000", "457FFF", "BG"), ("490000", "497FFF", "PT"), ("498000", "49FFFF", "CZ"),
    ("470000", "477FFF", "HU"), ("440000", "447FFF", "AT"), ("4B0000", "4B7FFF", "CH"), ("4CA000", "4CAFFF", "IE"),
    ("511000", "5113FF", "EE"), ("502C00", "502FFF", "LV"), ("503C00", "503FFF", "LT"), ("505C00", "505FFF", "SK"),
    ("506C00", "506FFF", "SI"), ("501C00", "501FFF", "HR"), ("508000", "50FFFF", "UA"), ("510000", "5103FF", "BY"),
    ("C00000", "C3FFFF", "CA"), ("7C0000", "7FFFFF", "AU"), ("840000", "87FFFF", "JP"), ("718000", "71FFFF", "KR"),
    ("738000", "73FFFF", "IL"), ("710000", "717FFF", "SA"), ("896000", "896FFF", "AE"), ("06A000", "06A3FF", "QA"),
    ("706000", "706FFF", "KW"), ("70C000", "70C3FF", "OM"), ("894000", "894FFF", "BH"), ("740000", "747FFF", "JO"),
    ("010000", "017FFF", "EG"), ("728000", "72FFFF", "IQ"), ("730000", "737FFF", "IR"), ("100000", "1FFFFF", "RU"),
    ("780000", "7BFFFF", "CN"), ("800000", "83FFFF", "IN"), ("760000", "767FFF", "PK"), ("768000", "76FFFF", "SG"),
    ("C80000", "C87FFF", "NZ"),
]
BLOCCHI = [(int(a, 16), int(b, 16), c) for a, b, c in BLOCCHI]


def paese_da_hex(h):
    try:
        v = int(h, 16)
    except (TypeError, ValueError):
        return ""
    for a, b, c in BLOCCHI:
        if a <= v <= b:
            return c
    return ""


def appartenenza(ac):
    reg = (ac.get("r") or "").upper()
    if reg.startswith("LX-N") or re.match(r"^T-0[56]\d$", reg) or reg.startswith("MM-AV-SA"):
        return "NATO"          # NATO E-3A (Luxembourg register), MMF A330 MRTT, NATO AGS RQ-4D
    return paese_da_hex(ac.get("hex", ""))


# ---------------------------------------------------------------- military airfields (OurAirports, public domain)
BASI = {
    "BGTL": ["Pituffik Space Base", 76.5306, -68.7005, "GL"], "BIKF": ["Keflavík", 63.985, -22.6056, "IS"],
    "EDDK": ["Cologne Bonn", 50.8659, 7.1427, "DE"], "EEEI": ["Ämari Air Base", 59.2596, 24.2048, "EE"],
    "EGPK": ["Glasgow Prestwick", 55.5015, -4.5772, "GB"], "EGQS": ["RAF Lossiemouth", 57.7052, -3.3392, "GB"],
    "EGUL": ["RAF Lakenheath", 52.4095, 0.5612, "GB"], "EGUN": ["RAF Mildenhall", 52.3619, 0.4864, "GB"],
    "EGVA": ["RAF Fairford", 51.6836, -1.7892, "GB"], "EGVN": ["RAF Brize Norton", 51.75, -1.5836, "GB"],
    "EGXW": ["RAF Waddington", 53.1662, -0.5238, "GB"], "EHEH": ["Eindhoven", 51.4501, 5.3745, "NL"],
    "ENAN": ["Andøya", 69.2952, 16.1394, "NO"], "ENBO": ["Bodø", 67.2692, 14.3653, "NO"],
    "EPKS": ["Poznań-Krzesiny Air Base", 52.3317, 16.9664, "PL"], "EPLK": ["Łask Air Base", 51.5517, 19.1791, "PL"],
    "EPMB": ["Malbork Air Base", 54.0266, 19.1357, "PL"], "EPRZ": ["Rzeszów-Jasionka", 50.1098, 22.0242, "PL"],
    "ESPA": ["Luleå", 65.5438, 22.122, "SE"], "ETAD": ["Spangdahlem Air Base", 49.9765, 6.6984, "DE"],
    "ETAR": ["Ramstein Air Base", 49.4369, 7.6003, "DE"], "ETNG": ["NATO Air Base Geilenkirchen", 50.9608, 6.0424, "DE"],
    "ETNW": ["Wunstorf Air Base", 52.4573, 9.4272, "DE"], "ETSN": ["Neuburg Air Base", 48.711, 11.2115, "DE"],
    "EVLA": ["Liepāja", 56.5175, 21.0969, "LV"], "EYSA": ["Šiauliai Air Base", 55.8939, 23.395, "LT"],
    "FJDG": ["Diego Garcia", -7.3133, 72.4111, "IO"], "HDAM": ["Djibouti-Ambouli", 11.5473, 43.1595, "DJ"],
    "KCHS": ["Joint Base Charleston", 32.8962, -80.0382, "US"], "KDOV": ["Dover AFB", 39.1295, -75.466, "US"],
    "KPSM": ["Pease (Portsmouth NH)", 43.0779, -70.8233, "US"], "KSUU": ["Travis AFB", 38.2627, -121.927, "US"],
    "KWRI": ["Joint Base McGuire", 40.0156, -74.5917, "US"], "LBSF": ["Sofia", 42.6964, 23.4177, "BG"],
    "LBWN": ["Varna", 43.2321, 27.8251, "BG"], "LCRA": ["RAF Akrotiri", 34.5904, 32.9879, "CY"],
    "LEMO": ["Morón Air Base", 37.1749, -5.6159, "ES"], "LERT": ["Rota Naval Station", 36.6452, -6.3495, "ES"],
    "LETO": ["Torrejón Air Base", 40.4879, -3.4568, "ES"], "LEZG": ["Zaragoza Air Base", 41.6662, -1.0415, "ES"],
    "LFMI": ["Istres-Le Tubé Air Base", 43.5227, 4.9238, "FR"], "LFOA": ["Avord Air Base", 47.0533, 2.6325, "FR"],
    "LGEL": ["Elefsis Air Base", 38.0638, 23.556, "GR"], "LGSA": ["Souda Bay (Chania)", 35.5312, 24.1507, "GR"],
    "LGTS": ["Thessaloniki", 40.5193, 22.97, "GR"], "LHKE": ["Kecskemét Air Base", 46.9175, 19.7492, "HU"],
    "LIBA": ["Amendola Air Base", 41.5384, 15.7172, "IT"], "LICG": ["Pantelleria", 36.8165, 11.9689, "IT"],
    "LICT": ["Trapani-Birgi", 37.9114, 12.488, "IT"], "LICZ": ["NAS Sigonella", 37.4017, 14.9224, "IT"],
    "LIPA": ["Aviano Air Base", 46.0319, 12.5965, "IT"], "LIPL": ["Ghedi Air Base", 45.4326, 10.2686, "IT"],
    "LIRE": ["Pratica di Mare Air Base", 41.6545, 12.4452, "IT"], "LIRP": ["Pisa San Giusto", 43.6839, 10.3927, "IT"],
    "LLBG": ["Ben Gurion", 32.0114, 34.8867, "IL"], "LLNV": ["Nevatim Air Base", 31.2083, 35.0123, "IL"],
    "LLOV": ["Ovda", 29.9403, 34.9358, "IL"], "LPLA": ["Lajes Field", 38.7618, -27.0908, "PT"],
    "LPMT": ["Montijo Air Base", 38.7093, -9.0337, "PT"], "LRCK": ["Mihail Kogălniceanu", 44.3622, 28.4883, "RO"],
    "LRFT": ["Fetești-Borcea Air Base", 44.3923, 27.7267, "RO"], "LROP": ["Bucharest Otopeni", 44.5718, 26.1033, "RO"],
    "LTAG": ["İncirlik Air Base", 37.0021, 35.4259, "TR"], "LTAN": ["Konya Air Base", 37.979, 32.5619, "TR"],
    "LTBQ": ["Cengiz Topel", 40.735, 30.0833, "TR"], "LTCE": ["Erzurum", 39.9565, 41.1702, "TR"],
    "OBBI": ["Bahrain International", 26.2673, 50.6376, "BH"], "OEPS": ["Prince Sultan Air Base", 24.0627, 47.5805, "SA"],
    "OETF": ["Taif (King Fahd Air Base)", 21.4847, 40.5441, "SA"], "OJMS": ["Muwaffaq Salti Air Base", 31.8256, 36.782, "JO"],
    "OKAS": ["Ali Al Salem Air Base", 29.3469, 47.5201, "KW"], "OMAM": ["Al Dhafra Air Base", 24.2482, 54.5477, "AE"],
    "OTBH": ["Al Udeid Air Base", 25.1173, 51.315, "QA"], "OTHH": ["Hamad International", 25.2731, 51.6081, "QA"],
    "PGUA": ["Andersen AFB, Guam", 13.584, 144.93, "GU"], "RJSM": ["Misawa Air Base", 40.7032, 141.368, "JP"],
    "RJTY": ["Yokota Air Base", 35.7485, 139.348, "JP"], "RODN": ["Kadena Air Base", 26.3517, 127.7694, "JP"],
    "YPDN": ["RAAF Darwin", -12.415, 130.8818, "AU"], "YPTN": ["RAAF Tindal", -14.5211, 132.378, "AU"],
}

CATEGORIE = {"aereo-cisterna", "aereo-ricognizione", "aereo-trasporto", "aereo-bombardiere", "aereo-caccia"}
STATI = {"operativo", "lasciata", "danneggiato", "in-manutenzione", "fuori-servizio"}
TEATRI = {"MO", "RU-UA", "IT", "NATO", "ALTRO"}
AFFIDABILITA = {"alta", "media", "bassa"}
CAMPI_CURATI = ["id", "categoria", "nome", "breve", "dettaglio", "appartenenza", "stato", "data_evento",
                "precisione_km", "teatro", "regione", "affidabilita", "note", "fonti"]


def km(lat1, lon1, lat2, lon2):
    r = math.pi / 180
    a = math.sin((lat2 - lat1) * r / 2) ** 2 + math.cos(lat1 * r) * math.cos(lat2 * r) * math.sin((lon2 - lon1) * r / 2) ** 2
    return 12742 * math.asin(math.sqrt(min(1, a)))


def base_vicina(lat, lon):
    best = None
    for icao, (nome, la, lo, pa) in BASI.items():
        d = km(lat, lon, la, lo)
        if best is None or d < best[0]:
            best = (d, icao, nome, pa)
    return best


def teatro(lat, lon):
    if 36 <= lat <= 47.2 and 6.6 <= lon <= 18.6:
        return "IT"
    if 44 <= lat <= 56 and 30 <= lon <= 50:
        return "RU-UA"
    if 12 <= lat <= 38.5 and 32 <= lon <= 63:
        return "MO"
    if 30 <= lat <= 72 and -30 <= lon <= 45:
        return "NATO"
    return "ALTRO"


def scarica(url, errori, tentativi=2):
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001 - every failure is recorded, none is fatal
            if i == tentativi - 1:
                errori.append(f"{url}: {type(e).__name__}: {e}")
            time.sleep(3)
    return None


# ---------------------------------------------------------------- snapshot
def classifica(ac):
    t = (ac.get("t") or "").upper()
    testo = " ".join([(ac.get("desc") or ""), (ac.get("r") or "")]).upper()
    if t in TIPI:
        cat, lab = TIPI[t]
        if t == "R135" and "TC-135" in testo:
            return None            # trainer, not an ISR sortie
        return cat, lab
    for rx, cat, lab in AMBIGUI.get(t, []):
        if re.search(rx, testo):
            return cat, lab
    if t == "A332" and re.match(REG_CISTERNA, (ac.get("r") or "").upper()):
        return "aereo-cisterna", "A330 MRTT"
    if t == "B762" and re.match(REG_CISTERNA, (ac.get("r") or "").upper()):
        return "aereo-cisterna", "KC-46A / KC-767"
    return None


def escluso(ac):
    flags = ac.get("dbFlags") or 0
    if flags & 4 or flags & 8:                       # privacy (PIA) or LADD: never shown
        return "privacy"
    cs = (ac.get("flight") or "").strip().upper()
    if cs and ESCLUDI_CALLSIGN.match(cs):
        return "vip-callsign"
    if ESCLUDI_OPERATORE.search(ac.get("ownOp") or ""):
        return "vip-operator"
    t = (ac.get("t") or "").upper()
    if not (flags & 1) and t not in SEMPRE_MIL:
        return "not-military"
    return None


def raccogli_snapshot(errori, avvisi, fonti):
    visti = {}            # hex -> (aircraft dict, source key, timestamp ms)
    lol = scarica(URL_LOL_MIL, errori)
    if lol and isinstance(lol.get("ac"), list):
        for ac in lol["ac"]:
            visti[ac.get("hex")] = (ac, "lol", lol.get("now"))
        for t in TIPI_EXTRA:
            time.sleep(3)
            d = scarica(URL_LOL_TYPE.format(t), avvisi, tentativi=1)   # optional extra: a failure is only a warning
            for ac in (d or {}).get("ac", []):
                visti.setdefault(ac.get("hex"), (ac, "lol", d.get("now")))
    time.sleep(1.2)                                   # adsb.fi: 1 request per second
    fi = scarica(URL_FI_MIL, errori)
    if fi and isinstance(fi.get("ac"), list):
        for ac in fi["ac"]:
            h = ac.get("hex")
            if h in visti:                            # enrich with description / operator only
                base = visti[h][0]
                for k in ("desc", "ownOp", "year"):
                    if ac.get(k) and not base.get(k):
                        base[k] = ac[k]
            else:
                visti[h] = (ac, "fi", fi.get("now"))
    usati = set()
    tenuti, scarti = [], {}
    for h, (ac, src, now) in visti.items():
        ac["flight"] = (ac.get("flight") or "").replace("@", "").strip()
        if not isinstance(ac.get("lat"), (int, float)) or not isinstance(ac.get("lon"), (int, float)):
            scarti["no-position"] = scarti.get("no-position", 0) + 1
            continue
        motivo = escluso(ac)
        if motivo:
            scarti[motivo] = scarti.get(motivo, 0) + 1
            continue
        cl = classifica(ac)
        if not cl:
            scarti["type-not-kept"] = scarti.get("type-not-kept", 0) + 1
            continue
        seen = float(ac.get("seen_pos") or ac.get("seen") or 0)
        ts = dt.datetime.fromtimestamp((now or ADESSO.timestamp() * 1000) / 1000 - seen, dt.timezone.utc)
        if seen > 600:
            scarti["position-older-than-10-min"] = scarti.get("position-older-than-10-min", 0) + 1
            continue
        alt = ac.get("alt_baro")
        a_terra = alt == "ground" or (isinstance(alt, (int, float)) and alt < 1500 and (ac.get("gs") or 0) < 60)
        tenuti.append({"ac": ac, "src": src, "cat": cl[0], "lab": cl[1], "ts": ts, "terra": a_terra,
                       "app": appartenenza(ac), "lat": ac["lat"], "lon": ac["lon"]})
        usati.add(src)
    if "lol" in usati or lol:
        fonti.append(dict(FONTE_LOL, data_dato=ADESSO.strftime("%Y-%m-%dT%H:%MZ")))
    if "fi" in usati or fi:
        fonti.append(dict(FONTE_FI, data_dato=ADESSO.strftime("%Y-%m-%dT%H:%MZ")))
    avvisi.append("snapshot: %d military aircraft received, %d kept; dropped: %s" % (
        len(visti), len(tenuti), ", ".join(f"{k} {v}" for k, v in sorted(scarti.items())) or "none"))
    return raggruppa(tenuti)


def raggruppa(tenuti):
    """Parked aircraft at the same base -> one item; aircraft in flight within 30 km of each other,
    same category and owner -> one item (formations). Everything else -> one item per aircraft."""
    gruppi = []
    for x in sorted(tenuti, key=lambda x: (x["cat"], x["app"], x["ac"].get("hex", ""))):
        b = base_vicina(x["lat"], x["lon"])
        x["base"] = b if b and b[0] <= 6 else None
        x["vicina"] = b
        for g in gruppi:
            y = g[0]
            if y["cat"] != x["cat"] or y["app"] != x["app"] or y["terra"] != x["terra"]:
                continue
            if x["terra"] and x["base"] and y["base"] and x["base"][1] == y["base"][1]:
                g.append(x); break
            if not x["terra"] and km(x["lat"], x["lon"], y["lat"], y["lon"]) <= 30:
                g.append(x); break
        else:
            gruppi.append([x])
    return [elemento_snapshot(g) for g in gruppi]


def sigla(x):
    ac = x["ac"]
    parti = [p for p in [(ac.get("flight") or "").strip(), ac.get("r") or ""] if p]
    return (" / ".join(parti) + f" (hex {ac.get('hex','')})").strip()


def elemento_snapshot(g):
    x = g[0]
    ac = x["ac"]
    n = len(g)
    lat = round(sum(y["lat"] for y in g) / n, 2)
    lon = round(sum(y["lon"] for y in g) / n, 2)
    ts = max(y["ts"] for y in g)
    labs = sorted({y["lab"] for y in g})
    lab = labs[0] if len(labs) == 1 else " / ".join(labs)
    src = "adsb.lol" if all(y["src"] == "lol" for y in g) else "adsb.fi" if all(y["src"] == "fi" for y in g) else "adsb.lol and adsb.fi"
    mlat = any(ac2["ac"].get("mlat") or ac2["ac"].get("tisb") for ac2 in g)
    if x["terra"] and x["base"]:
        regione = f"on the ground at {x['base'][2]}"
        paese = x["base"][3]
        prec = 3
    elif x["terra"]:
        regione = "on the ground"
        paese = ""
        prec = 3
    else:
        v = x["vicina"]
        quote = [y["ac"].get("alt_baro") for y in g if isinstance(y["ac"].get("alt_baro"), (int, float))]
        q = f" at about {int(round(max(quote) / 100.0) * 100):,} ft".replace(",", " ") if quote else ""
        regione = f"in flight{q}" + (f", about {int(v[0])} km from {v[2]}" if v and v[0] <= 500 else "")
        paese = ""
        prec = 2 if n == 1 else max(2, int(max(km(lat, lon, y["lat"], y["lon"]) for y in g)) + 2)
    ident = "; ".join(sigla(y) for y in g[:12]) + (f"; +{n - 12} more" if n > 12 else "")
    if n == 1:
        nome = f"{lab} ({(ac.get('flight') or '').strip() or ac.get('r') or ac.get('hex')})"
        breve = f"{lab.split(' ')[0]} {(ac.get('flight') or '').strip() or ac.get('r') or ''}".strip()
    else:
        nome = f"{n} × {lab}" + (f" at {x['base'][2]}" if x["terra"] and x["base"] else " flying together")
        breve = f"{n} × {lab.split(' ')[0]}"
    dett = []
    for y in g[:6]:
        a = y["ac"]
        bits = [p for p in [
            f"{a.get('alt_baro')} ft" if isinstance(a.get("alt_baro"), (int, float)) else ("on ground" if a.get("alt_baro") == "ground" else ""),
            f"{int(a['gs'])} kt" if isinstance(a.get("gs"), (int, float)) else "",
            f"track {int(a['track'])}°" if isinstance(a.get("track"), (int, float)) else "",
            f"squawk {a['squawk']}" if a.get("squawk") else ""] if p]
        dett.append(f"{(a.get('flight') or '').strip() or a.get('r') or a.get('hex')}: " + ", ".join(bits))
    hexes = "-".join(sorted(y["ac"].get("hex", "") for y in g))[:40]
    t = ts.strftime("%H:%M")
    elem = {
        "id": f"AE-S-{ts.strftime('%Y%m%d')}-{hexes}",
        "classe": "mobile", "categoria": x["cat"], "nome": nome, "identificativo": ident,
        "appartenenza": x["app"], "stato": "operativo",
        "data_evento": ts.strftime("%Y-%m-%d"), "ora_utc": t,
        "lat": lat, "lon": lon, "origine_coord": "fonte", "precisione_km": prec,
        "teatro": teatro(lat, lon), "paese": paese, "regione": regione,
        "attore": "", "bersaglio": "", "mezzo": "", "esito": "",
        "fonte": f"{src} ADS-B snapshot",
        "link": f"https://globe.adsb.lol/?icao={ac.get('hex','')}" if x["src"] == "lol" else f"https://globe.adsb.fi/?icao={ac.get('hex','')}",
        "data_fonte": ts.strftime("%Y-%m-%d"),
        "affidabilita": "media" if mlat else "alta",
        "note": (f"Snapshot at {t} UTC on {ts.strftime('%d %b %Y')}: the position is where the aircraft was when the data was "
                 f"collected, not where it is now. " + "; ".join(dett) + (". Some positions are MLAT/TIS-B, less precise." if mlat else ".")
                 + " Owner from the ICAO address block or registration. Data: "
                 + ("adsb.lol contributors, ODbL 1.0" if "lol" in src else "")
                 + (" and " if src == "adsb.lol and adsb.fi" else "")
                 + ("adsb.fi (https://adsb.fi), non-commercial use" if "fi" in src else "") + "."),
        "fonti": [{"fonte": f"{src} ADS-B snapshot",
                   "link": f"https://globe.adsb.lol/?icao={ac.get('hex','')}" if x["src"] == "lol" else f"https://globe.adsb.fi/?icao={ac.get('hex','')}",
                   "data_fonte": ts.strftime("%Y-%m-%d")}],
        "breve": breve, "dettaglio": "ADS-B snapshot, " + ("parked" if x["terra"] else "in flight"),
        "istantanea": 1, "n_aerei": n,
    }
    return elem


# ---------------------------------------------------------------- curated
def valida_curati(dati, errori, avvisi):
    out, ids = [], set()
    for i, e in enumerate(dati.get("elementi", [])):
        dove = e.get("id") or f"#{i}"
        mancano = [c for c in CAMPI_CURATI if e.get(c) in (None, "", [])]
        if mancano:
            errori.append(f"curati {dove}: missing fields {mancano}"); continue
        if e["id"] in ids:
            errori.append(f"curati {dove}: duplicate id"); continue
        if e["categoria"] not in CATEGORIE or e["stato"] not in STATI or e["teatro"] not in TEATRI or e["affidabilita"] not in AFFIDABILITA:
            errori.append(f"curati {dove}: categoria/stato/teatro/affidabilita not allowed"); continue
        try:
            d = dt.date.fromisoformat(e["data_evento"])
            fds = [dt.date.fromisoformat(f["data_fonte"]) for f in e["fonti"]]
        except (ValueError, KeyError, TypeError):
            errori.append(f"curati {dove}: bad date"); continue
        if d > OGGI or any(f > OGGI for f in fds):
            errori.append(f"curati {dove}: date in the future"); continue
        if any(not str(f.get("link", "")).startswith(("http://", "https://")) or not f.get("fonte") for f in e["fonti"]):
            errori.append(f"curati {dove}: every source needs a name and an http(s) link"); continue
        rif = e.get("rif_coord")
        if rif:
            if rif not in BASI:
                errori.append(f"curati {dove}: rif_coord {rif} not in the base table"); continue
            lat, lon = BASI[rif][1], BASI[rif][2]
            origine = "stimata"
        else:
            lat, lon, origine = e.get("lat"), e.get("lon"), e.get("origine_coord", "stimata")
        if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and -90 <= lat <= 90 and -180 <= lon <= 180):
            errori.append(f"curati {dove}: no valid coordinates"); continue
        eta = (OGGI - d).days
        if eta > 60:
            avvisi.append(f"curati {dove}: last report {eta} days old, the map will not draw it (limit 60 days)")
        ids.add(e["id"])
        f0 = e["fonti"][0]
        el = {
            "id": e["id"], "classe": "mobile", "categoria": e["categoria"], "nome": e["nome"],
            "identificativo": e.get("identificativo", ""), "appartenenza": e["appartenenza"], "stato": e["stato"],
            "data_evento": e["data_evento"], "ora_utc": e.get("ora_utc", ""),
            "lat": round(lat, 4), "lon": round(lon, 4), "origine_coord": origine, "precisione_km": e["precisione_km"],
            "teatro": e["teatro"], "paese": e.get("paese", ""), "regione": e["regione"],
            "attore": "", "bersaglio": "", "mezzo": "", "esito": "",
            "fonte": f0["fonte"], "link": f0["link"], "data_fonte": f0["data_fonte"],
            "affidabilita": e["affidabilita"],
            "note": e["note"] + (f" Base coordinates: OurAirports ({rif})." if rif else ""),
            "fonti": e["fonti"], "breve": e["breve"], "dettaglio": e["dettaglio"],
        }
        for k in ("dubbia", "sim", "storico"):
            if k in e:
                el[k] = e[k]
        out.append(el)
    return out


def main():
    offline = "--offline" in sys.argv
    errori, avvisi, fonti = [], [], []
    try:
        with open(CURATO, encoding="utf-8") as f:
            curati = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"curati.json missing or invalid: {e}", file=sys.stderr)
        return 1
    punti_curati = valida_curati(curati, errori, avvisi)
    punti_snap = [] if offline else raccogli_snapshot(errori, avvisi, fonti)
    fonti.append(dict(FONTE_OA, data_dato=OGGI.isoformat()))
    viste = {}
    for p in punti_curati:
        for f in p["fonti"]:
            viste.setdefault(f["link"], {"nome": f["fonte"], "link": f["link"], "licenza": "quoted facts with link; copyright of the publisher", "data_dato": f["data_fonte"]})
    fonti.extend(viste.values())
    out = {
        "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "schema": "same as the aircraft items of docs/data/mobili.json (regole/02_schema-dati.md v2.1 + map extras); extra fields istantanea, n_aerei",
        "nota": ("Military aircraft. Items with istantanea=1 are an automatic ADS-B snapshot taken at the time in ora_utc: "
                 "positions are where the aircraft were at collection time, not live, and many military aircraft fly with "
                 "transponders off, so absence means nothing. Snapshot data: adsb.lol contributors (ODbL 1.0) and adsb.fi "
                 "(https://adsb.fi, personal non-commercial use). The other items are curated deployments from open sources "
                 "(last ~60 days), placed at the base named by the source, with base coordinates from OurAirports."),
        "fonti": fonti,
        "conteggi": {"istantanea": len(punti_snap), "curati": len(punti_curati),
                     "aerei_istantanea": sum(p.get("n_aerei", 1) for p in punti_snap)},
        "punti": punti_snap + punti_curati,
        "errori": errori,
        "avvisi": avvisi,
    }
    with open(USCITA, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"aerei.json: {len(punti_snap)} snapshot items ({out['conteggi']['aerei_istantanea']} aircraft), "
          f"{len(punti_curati)} curated items, {len(errori)} errors, {len(avvisi)} warnings")
    for m in errori + avvisi:
        print(" -", m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
