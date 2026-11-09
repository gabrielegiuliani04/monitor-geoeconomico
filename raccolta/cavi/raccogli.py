#!/usr/bin/env python3
"""Cavi sottomarini del mondo e punti di approdo (TeleGeography) + incidenti curati a mano.

Fonti:
  - TeleGeography, Submarine Cable Map, API v3 (non documentata ma pubblica):
      /api/v3/cable/all.json, /api/v3/cable/cable-geo.json,
      /api/v3/landing-point/landing-point-geo.json, /api/v3/cable/<id>.json
    Licenza CC BY-NC-SA 3.0: uso personale e non commerciale, con citazione,
    i derivati vanno condivisi con la stessa licenza.
  - raccolta/cavi/incidenti.json: incidenti 2023-2026 curati a mano (fonte per fonte).

Produce:
  docs/data/cavi.json            linee (cavi) + approdi
  docs/data/cavi-incidenti.json  incidenti come punti (coordinate stimate)

Uso:  python3 raccolta/cavi/raccogli.py   (dalla radice del repository)
Solo libreria standard.
"""
import concurrent.futures as cf
import json
import math
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
OUT_CAVI = os.path.join(RADICE, "docs", "data", "cavi.json")
OUT_INC = os.path.join(RADICE, "docs", "data", "cavi-incidenti.json")
IN_INC = os.path.join(QUI, "incidenti.json")

BASE = "https://www.submarinecablemap.com/api/v3"
UA = {"User-Agent": "Mozilla/5.0 (monitor-geoeconomico OSINT, uso non commerciale)"}
LICENZA = "CC BY-NC-SA 3.0 (TeleGeography): uso non commerciale, citare la fonte, condividere allo stesso modo"
TOLLERANZA = 0.02     # gradi, semplificazione Douglas-Peucker delle linee
DECIMALI = 3          # decimali delle coordinate in uscita (max 4 per le regole)
PASSO = 0.1           # gradi, densificazione per il controllo dei passaggi

# Nome del paese come lo scrive TeleGeography -> ISO 3166-1 alfa-2
ISO = {
 "Albania": "AL", "Algeria": "DZ", "American Samoa": "AS", "Angola": "AO", "Anguilla": "AI",
 "Antigua and Barbuda": "AG", "Argentina": "AR", "Aruba": "AW", "Australia": "AU", "Azerbaijan": "AZ",
 "Bahamas": "BS", "Bahrain": "BH", "Bangladesh": "BD", "Barbados": "BB", "Belgium": "BE", "Belize": "BZ",
 "Benin": "BJ", "Bermuda": "BM", "Bonaire, Sint Eustatius and Saba": "BQ", "Brazil": "BR",
 "British Indian Ocean Territory": "IO", "Brunei": "BN", "Bulgaria": "BG", "Cambodia": "KH",
 "Cameroon": "CM", "Canada": "CA", "Cape Verde": "CV", "Cayman Islands": "KY", "Chile": "CL", "China": "CN",
 "Christmas Island": "CX", "Cocos (Keeling) Islands": "CC", "Colombia": "CO", "Comoros": "KM",
 "Congo, Dem. Rep.": "CD", "Congo, Rep.": "CG", "Cook Islands": "CK", "Costa Rica": "CR", "Croatia": "HR",
 "Cuba": "CU", "Curaçao": "CW", "Cyprus": "CY", "Côte d'Ivoire": "CI", "Denmark": "DK", "Djibouti": "DJ",
 "Dominica": "DM", "Dominican Republic": "DO", "Ecuador": "EC", "Egypt": "EG", "Equatorial Guinea": "GQ",
 "Eritrea": "ER", "Estonia": "EE", "Faroe Islands": "FO", "Fiji": "FJ", "Finland": "FI", "France": "FR",
 "French Guiana": "GF", "French Polynesia": "PF", "Gabon": "GA", "Gambia": "GM", "Georgia": "GE",
 "Germany": "DE", "Ghana": "GH", "Gibraltar": "GI", "Greece": "GR", "Greenland": "GL", "Grenada": "GD",
 "Guadeloupe": "GP", "Guam": "GU", "Guatemala": "GT", "Guernsey": "GG", "Guinea": "GN",
 "Guinea-Bissau": "GW", "Guyana": "GY", "Haiti": "HT", "Honduras": "HN", "Hong Kong": "HK",
 "Iceland": "IS", "India": "IN", "Indonesia": "ID", "Iran": "IR", "Iraq": "IQ", "Ireland": "IE",
 "Isle of Man": "IM", "Israel": "IL", "Italy": "IT", "Jamaica": "JM", "Japan": "JP", "Jersey": "JE",
 "Jordan": "JO", "Kazakhstan": "KZ", "Kenya": "KE", "Kiribati": "KI", "Kuwait": "KW", "Latvia": "LV",
 "Lebanon": "LB", "Liberia": "LR", "Libya": "LY", "Lithuania": "LT", "Madagascar": "MG", "Malaysia": "MY",
 "Maldives": "MV", "Malta": "MT", "Marshall Islands": "MH", "Martinique": "MQ", "Mauritania": "MR",
 "Mauritius": "MU", "Mayotte": "YT", "Mexico": "MX", "Micronesia": "FM", "Monaco": "MC",
 "Montenegro": "ME", "Montserrat": "MS", "Morocco": "MA", "Mozambique": "MZ", "Myanmar": "MM",
 "Namibia": "NA", "Nauru": "NR", "Netherlands": "NL", "New Caledonia": "NC", "New Zealand": "NZ",
 "Nicaragua": "NI", "Nigeria": "NG", "Niue": "NU", "Northern Mariana Islands": "MP", "Norway": "NO",
 "Oman": "OM", "Pakistan": "PK", "Palau": "PW", "Panama": "PA", "Papua New Guinea": "PG", "Peru": "PE",
 "Philippines": "PH", "Poland": "PL", "Portugal": "PT", "Puerto Rico": "PR", "Qatar": "QA",
 "Romania": "RO", "Russia": "RU", "Réunion": "RE", "Saint Barthélemy": "BL",
 "Saint Helena, Ascension and Tristan da Cunha": "SH", "Saint Kitts and Nevis": "KN",
 "Saint Lucia": "LC", "Saint Martin": "MF", "Saint Pierre and Miquelon": "PM",
 "Saint Vincent and the Grenadines": "VC", "Samoa": "WS", "Sao Tome and Principe": "ST",
 "Saudi Arabia": "SA", "Senegal": "SN", "Seychelles": "SC", "Sierra Leone": "SL", "Singapore": "SG",
 "Sint Maarten": "SX", "Slovenia": "SI", "Solomon Islands": "SB", "Somalia": "SO", "South Africa": "ZA",
 "South Korea": "KR", "Spain": "ES", "Sri Lanka": "LK", "Sudan": "SD", "Suriname": "SR", "Sweden": "SE",
 "Syria": "SY", "Taiwan": "TW", "Tanzania": "TZ", "Thailand": "TH", "Timor-Leste": "TL", "Togo": "TG",
 "Tokelau": "TK", "Tonga": "TO", "Trinidad and Tobago": "TT", "Tunisia": "TN", "Turkey": "TR",
 "Turks and Caicos Islands": "TC", "Tuvalu": "TV", "Uganda": "UG", "Ukraine": "UA",
 "United Arab Emirates": "AE", "United Kingdom": "GB", "United States": "US", "Uruguay": "UY",
 "Vanuatu": "VU", "Venezuela": "VE", "Vietnam": "VN", "Virgin Islands (U.K.)": "VG",
 "Virgin Islands (U.S.)": "VI", "Wallis and Futuna": "WF", "Yemen": "YE", "Western Sahara": "EH",
 "North Korea": "KP", "Belarus": "BY", "Mongolia": "MN", "Bhutan": "BT", "Nepal": "NP",
 "Laos": "LA", "Afghanistan": "AF", "Ethiopia": "ET", "South Sudan": "SS", "Falkland Islands": "FK",
 "Pitcairn Islands": "PN", "Norfolk Island": "NF", "Svalbard and Jan Mayen": "SJ",
 "Bosnia and Herzegovina": "BA", "El Salvador": "SV", "Macau": "MO",
}

# ---------------------------------------------------------------------------
# Passaggi strategici: poligoni approssimati [lon, lat] (disegnati a mano, grossolani).
# Nomi come in docs/data/labels.json (straits e seas). Un cavo "attraversa" un passaggio
# se un punto della sua linea densificata cade nel poligono.
# ---------------------------------------------------------------------------
def box(lo1, la1, lo2, la2):
    return [(lo1, la1), (lo2, la1), (lo2, la2), (lo1, la2)]

PASSAGGI = {
    "Mar Rosso": [[(32.4, 30.0), (32.6, 29.0), (33.8, 27.0), (35.2, 24.0), (37.0, 20.0), (38.6, 17.0),
                   (41.0, 14.0), (43.2, 12.4), (43.6, 12.7), (42.6, 14.8), (41.0, 17.5), (39.6, 20.5),
                   (38.6, 23.0), (37.0, 25.5), (35.3, 28.0), (34.9, 29.5), (34.4, 28.2), (33.8, 28.0),
                   (33.0, 29.8)]],
    "Bab el-Mandeb": [box(42.8, 12.2, 44.0, 13.2)],
    "Stretto di Hormuz": [box(55.6, 25.3, 57.2, 27.0)],
    "Stretto di Malacca": [box(98.0, 0.8, 103.5, 5.5)],
    "Stretto di Taiwan": [box(118.8, 22.3, 120.05, 26.3)],
    "Stretto di Luzon": [box(119.5, 18.8, 122.5, 22.0)],
    "Mar Baltico": [box(12.0, 53.8, 30.5, 55.9), box(13.0, 55.9, 30.5, 60.8), box(16.8, 60.8, 25.8, 66.0),
                    box(9.8, 53.9, 12.0, 55.0)],
    "Stretti danesi": [box(10.5, 54.6, 12.9, 56.2)],
    "Stretto di Gibilterra": [box(-6.0, 35.7, -5.0, 36.2)],
    "Canale di Sicilia": [box(10.8, 35.6, 14.6, 37.8)],
    "Mar Mediterraneo": [box(-5.6, 35.0, 3.0, 42.0), box(3.0, 36.0, 16.0, 44.5), box(12.0, 39.5, 20.0, 46.0),
                         box(-2.0, 30.5, 36.0, 37.5), box(19.0, 35.0, 26.6, 41.0), box(26.6, 31.0, 36.5, 37.0)],
}
ORDINE = ["Canale di Suez", "Mar Rosso", "Bab el-Mandeb", "Stretto di Hormuz", "Stretto di Malacca",
          "Stretto di Taiwan", "Stretto di Luzon", "Mar Baltico", "Stretti danesi",
          "Stretto di Gibilterra", "Canale di Sicilia", "Mar Mediterraneo"]


def dentro(lon, lat, poly):
    ins = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            ins = not ins
        j = i
    return ins


def densifica(parte):
    out = [parte[0]]
    for (x1, y1), (x2, y2) in zip(parte, parte[1:]):
        d = max(abs(x2 - x1), abs(y2 - y1))
        n = int(d / PASSO)
        for k in range(1, n + 1):
            t = k / (n + 1)
            out.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
        out.append((x2, y2))
    return out


def passaggi(parti):
    trovati = set()
    for parte in parti:
        for lon, lat in densifica(parte):
            for nome, polys in PASSAGGI.items():
                if nome in trovati:
                    continue
                for p in polys:
                    if dentro(lon, lat, p):
                        trovati.add(nome)
                        break
    # Suez: il cavo passa sia nel Mar Rosso sia nel Mediterraneo (attraversa l'Egitto)
    if "Mar Rosso" in trovati and "Mar Mediterraneo" in trovati:
        trovati.add("Canale di Suez")
    return [n for n in ORDINE if n in trovati]


# ---------------------------------------------------------------------------
def dp(punti, tol):
    """Douglas-Peucker iterativo."""
    if len(punti) < 3:
        return punti
    tieni = [False] * len(punti)
    tieni[0] = tieni[-1] = True
    pila = [(0, len(punti) - 1)]
    while pila:
        a, b = pila.pop()
        x1, y1 = punti[a]
        x2, y2 = punti[b]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        dmax, imax = 0.0, -1
        for i in range(a + 1, b):
            x, y = punti[i]
            d = math.hypot(x - x1, y - y1) if L == 0 else abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L
            if d > dmax:
                dmax, imax = d, i
        if dmax > tol and imax > 0:
            tieni[imax] = True
            pila.append((a, imax))
            pila.append((imax, b))
    return [p for p, k in zip(punti, tieni) if k]


def arrotonda(parte):
    out = []
    for x, y in parte:
        q = [round(x, DECIMALI), round(y, DECIMALI)]
        if not out or out[-1] != q:
            out.append(q)
    return out


def get_json(url, tries=4):
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa
            err = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"{url}: {err}")


def km(testo):
    if not testo:
        return None
    m = re.search(r"([\d,\.]+)\s*km", testo)
    if not m:
        return None
    try:
        return int(float(m.group(1).replace(",", "")))
    except ValueError:
        return None


def adesso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def main():
    errori = []
    oggi = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    elenco = get_json(f"{BASE}/cable/all.json")
    geo = get_json(f"{BASE}/cable/cable-geo.json")
    lpgeo = get_json(f"{BASE}/landing-point/landing-point-geo.json")
    print(f"cavi in elenco: {len(elenco)}, feature geo: {len(geo['features'])}, approdi: {len(lpgeo['features'])}")

    def det(cid):
        try:
            return cid, get_json(f"{BASE}/cable/{cid}.json")
        except Exception as e:  # noqa
            return cid, e

    dettagli = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for cid, d in ex.map(det, [c["id"] for c in elenco]):
            if isinstance(d, Exception):
                errori.append(f"dettaglio non scaricato: {cid}: {d}")
            else:
                dettagli[cid] = d
    print(f"dettagli scaricati: {len(dettagli)}")

    # geometrie per cavo (un cavo può avere più feature)
    geom = {}
    for f in geo["features"]:
        cid = f["properties"]["id"]
        g = f["geometry"]
        parti = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        geom.setdefault(cid, {"colore": f["properties"].get("color"), "parti": []})
        geom[cid]["parti"].extend([[tuple(p[:2]) for p in parte] for parte in parti if len(parte) > 1])

    # paese degli approdi dai dettagli
    paese_lp, cavi_lp = {}, {}
    for cid, d in dettagli.items():
        for lp in d.get("landing_points") or []:
            paese_lp[lp["id"]] = lp.get("country")
            cavi_lp.setdefault(lp["id"], []).append(cid)

    nomi_lp = {f["properties"]["id"]: f["properties"]["name"] for f in lpgeo["features"]}
    senza_iso = set()

    def iso(nome_paese):
        if not nome_paese:
            return ""
        c = ISO.get(nome_paese)
        if not c:
            senza_iso.add(nome_paese)
            return ""
        return c

    linee = []
    conta_s = {}
    for c in elenco:
        cid = c["id"]
        d = dettagli.get(cid, {})
        gm = geom.get(cid)
        if not gm:
            errori.append(f"geometria mancante: {cid}")
            continue
        s = passaggi(gm["parti"])
        for n in s:
            conta_s[n] = conta_s.get(n, 0) + 1
        g = [arrotonda(dp(p, TOLLERANZA)) for p in gm["parti"]]
        g = [p for p in g if len(p) > 1]
        lps = d.get("landing_points") or []
        paesi = sorted({iso(lp.get("country")) for lp in lps} - {""})
        approdi_it = [nomi_lp.get(lp["id"], lp.get("name", "")).replace(", Italy", "")
                      for lp in lps if lp.get("country") == "Italy"]
        pianificato = d.get("is_planned")
        linee.append({
            "id": cid,
            "categoria": "cavo-sottomarino",
            "nome": c["name"],
            "stato": "pianificato" if pianificato else ("attivo" if pianificato is False else ""),
            "anno": d.get("rfs_year"),
            "rfs": d.get("rfs") or "",
            "proprietari": d.get("owners") or "",
            "fornitori": d.get("suppliers") or "",
            "km": km(d.get("length")),
            "paesi": paesi,
            "n_approdi": len(lps),
            "approdi_it": approdi_it,
            "s": s,
            "colore": gm["colore"],
            "sito": d.get("url") or "",
            "link": f"https://www.submarinecablemap.com/submarine-cable/{cid}",
            "fonte": "TeleGeography Submarine Cable Map",
            "data_fonte": oggi,
            "affidabilita": "media",
            "g": g,
        })

    approdi = []
    for f in lpgeo["features"]:
        p = f["properties"]
        lon, lat = f["geometry"]["coordinates"][:2]
        nome_paese = paese_lp.get(p["id"])
        if not nome_paese and "," in p["name"]:
            nome_paese = p["name"].rsplit(",", 1)[1].strip()
        approdi.append({
            "id": p["id"],
            "nome": p["name"],
            "lat": round(lat, 4), "lon": round(lon, 4),
            "paese": iso(nome_paese),
            "categoria": "approdo-cavo",
            "stato": "da definire" if p.get("is_tbd") else "",
            "cavi": sorted(cavi_lp.get(p["id"], [])),
            "fonte": "TeleGeography Submarine Cable Map",
            "link": f"https://www.submarinecablemap.com/landing-point/{p['id']}",
            "data_fonte": oggi,
            "affidabilita": "media",
            "note": "",
        })
    if senza_iso:
        errori.append("paesi senza codice ISO (aggiungere a ISO): " + ", ".join(sorted(senza_iso)))

    ita = [a for a in approdi if a["paese"] == "IT"]
    riepilogo = {
        "cavi": len(linee),
        "attivi": sum(1 for l in linee if l["stato"] == "attivo"),
        "pianificati": sum(1 for l in linee if l["stato"] == "pianificato"),
        "approdi": len(approdi),
        "cavi_per_passaggio": {n: conta_s.get(n, 0) for n in ORDINE},
        "italia": {
            "approdi": len(ita),
            "cavi": len({c for a in ita for c in a["cavi"]}),
            "per_approdo": {a["nome"].replace(", Italy", ""): len(a["cavi"]) for a in
                            sorted(ita, key=lambda a: -len(a["cavi"]))},
        },
    }

    out = {
        "aggiornato": adesso(),
        "fonti": [{"nome": "TeleGeography, Submarine Cable Map (API v3)",
                   "link": "https://www.submarinecablemap.com/",
                   "licenza": LICENZA, "data_dato": oggi}],
        "nota": ("Cavi sottomarini (elementi = linee, g = parti -> [lon, lat], semplificate con Douglas-Peucker "
                 f"{TOLLERANZA} gradi e {DECIMALI} decimali) e punti di approdo (approdi). I tracciati di "
                 "TeleGeography sono schematici, non la posa reale. stato: attivo / pianificato (is_planned). "
                 "anno = anno di entrata in servizio (RFS). s = passaggi strategici attraversati, calcolati "
                 "con poligoni approssimati disegnati a mano (nomi come in labels.json); 'Canale di Suez' "
                 "significa che il cavo passa sia nel Mar Rosso sia nel Mediterraneo, cioè attraversa l'Egitto. "
                 "TeleGeography non elenca i cavi dismessi né i cavi militari. Licenza CC BY-NC-SA."),
        "riepilogo": riepilogo,
        "elementi": linee,
        "approdi": approdi,
        "errori": errori,
    }
    with open(OUT_CAVI, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"scritto {OUT_CAVI}: {os.path.getsize(OUT_CAVI)/1e6:.2f} MB, {len(linee)} cavi, {len(approdi)} approdi")
    print(json.dumps(riepilogo["cavi_per_passaggio"], ensure_ascii=False))
    print(json.dumps(riepilogo["italia"], ensure_ascii=False))

    # ---------------- incidenti (curati a mano) ----------------
    err_inc = []
    try:
        with open(IN_INC, encoding="utf-8") as fh:
            inc = json.load(fh)
        elementi = inc.get("elementi", [])
    except Exception as e:  # noqa
        inc, elementi = {"nota": ""}, []
        err_inc.append(f"incidenti.json illeggibile: {e}")
    nomi_cavi = {l["nome"].lower(): l["id"] for l in linee}
    for e in elementi:
        for k in ("lat", "lon", "nome", "data_evento", "fonte", "link", "affidabilita"):
            if e.get(k) in (None, ""):
                err_inc.append(f"{e.get('id')}: manca {k}")
        e.setdefault("origine_coord", "stimata")
        # collega ai cavi di TeleGeography quando il nome coincide in parte
        legati = []
        for nome_c in e.get("cavi", []):
            base = nome_c.split(" (")[0].lower()
            for n, cid in nomi_cavi.items():
                if base and (base == n or base in n.split(" (")[0]) and cid not in legati and len(base) > 3:
                    legati.append(cid)
        e["cavi_id"] = legati
    elementi.sort(key=lambda e: e.get("data_evento", ""), reverse=True)
    out_inc = {
        "aggiornato": adesso(),
        "fonti": [{"nome": "Curato a mano dall'agente CAVI da notizie e analisti (una fonte per incidente)",
                   "link": "raccolta/cavi/incidenti.json", "licenza": "fatti con citazione delle fonti",
                   "data_dato": max((e.get("data_fonte", "") for e in elementi), default="")}],
        "nota": inc.get("nota", ""),
        "elementi": elementi,
        "errori": err_inc,
    }
    with open(OUT_INC, "w", encoding="utf-8") as fh:
        json.dump(out_inc, fh, ensure_ascii=False, indent=1)
    print(f"scritto {OUT_INC}: {len(elementi)} incidenti, errori {len(err_inc)}")
    if errori:
        print("avvisi:", *errori[:10], sep="\n  ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
