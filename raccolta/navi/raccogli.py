#!/usr/bin/env python3
"""Raccolta delle posizioni di navi da fonti aperte -> docs/data/navi.json

Obiettivi: (a) petroliere e gasiere negli stretti, (b) flotta ombra / navi
sanzionate, (c) navi militari principali (USA, da USNI News).

Fonti (ognuna si salta con un avviso se non disponibile, senza far fallire lo script):
  1. Digitraffic (Fintraffic, Finlandia)  - AIS in tempo reale, Golfo di Finlandia e Baltico
     settentrionale, nessuna chiave, CC BY 4.0. Funziona.
  2. Danish Maritime Authority (DMA)      - AIS storici giornalieri (CSV zip), Stretti danesi,
     nessuna chiave. File grande (centinaia di MB): scaricato su file temporaneo, letto in
     streaming, si salva solo il riassunto. Disattivabile con NAVI_DMA=0.
  3. aisstream.io                         - WebSocket AIS globale. Chiave gratuita in
     AISSTREAM_API_KEY; serve il pacchetto `websockets` (requirements.txt). Durata della
     raccolta in AISSTREAM_MINUTI (predefinito 10).
  4. Global Fishing Watch API v3          - eventi "AIS gap" (transponder spento) e incontri
     in mare. Chiave gratuita non commerciale in GFW_API_KEY.
  5. USNI News Fleet and Marine Tracker   - aree dichiarate di portaerei e gruppi anfibi USA
     (API WordPress pubblica del sito). Le coordinate sono il CENTRO DELL'AREA dichiarata.

Navi sanzionate: se esiste docs/data/sanzioni-navi.json (prodotto da un altro agente) gli
IMO/MMSI vengono incrociati; altrimenti il campo "sanzionata" resta "non verificato".

Le scie: a ogni esecuzione si rilegge il navi.json precedente e si aggiungono le nuove
posizioni (massimo SCIA_MAX punti per nave, solo ultimi SCIA_GIORNI giorni).
Nessun dato personale: si salvano solo identificativi della nave (MMSI, IMO, nome).
"""
import csv
import datetime as dt
import gzip
import html
import io
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile

RADICE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
USCITA = os.path.join(RADICE, "docs", "data", "navi.json")
SANZIONI = os.path.join(RADICE, "docs", "data", "sanzioni-navi.json")
UA = "monitor-geoeconomico/1.0 (osservatorio OSINT non commerciale)"
SCIA_MAX = 12
SCIA_GIORNI = 7

# Riquadri: (lat_min, lon_min, lat_max, lon_max). Volutamente larghi attorno al passaggio.
AREE = {
    "Stretto di Hormuz": (25.0, 55.3, 27.2, 57.8),
    "Bab el-Mandeb": (11.8, 42.6, 13.8, 44.2),
    "Canale di Suez": (29.5, 32.1, 31.7, 32.8),
    "Bosforo": (40.95, 28.85, 41.35, 29.25),
    "Stretti danesi": (54.3, 9.6, 57.9, 13.2),
    "Golfo di Finlandia": (59.15, 22.5, 60.9, 30.6),
}

# Centri approssimati delle aree citate da USNI (centro geografico dell'area, NON posizione).
AREE_USNI = {
    "arabian sea": (16.0, 63.0, 800), "gulf of oman": (24.5, 58.5, 250),
    "red sea": (20.0, 38.5, 700), "gulf of aden": (12.5, 48.0, 400),
    "persian gulf": (27.0, 51.5, 400), "arabian gulf": (27.0, 51.5, 400),
    "indian ocean": (-5.0, 75.0, 2000), "mediterranean sea": (35.0, 18.0, 1200),
    "eastern mediterranean": (34.0, 30.0, 400), "south china sea": (13.0, 114.0, 900),
    "east china sea": (29.0, 125.0, 500), "philippine sea": (20.0, 132.0, 1000),
    "japan": (34.5, 134.0, 800), "western pacific": (20.0, 140.0, 2000),
    "eastern pacific": (25.0, -125.0, 2000), "pacific": (20.0, -150.0, 3000),
    "western atlantic": (34.0, -70.0, 1500), "atlantic": (35.0, -40.0, 3000),
    "north atlantic": (55.0, -25.0, 1500), "eastern atlantic": (40.0, -15.0, 1500),
    "caribbean": (15.0, -75.0, 900), "north sea": (56.0, 3.0, 400),
    "baltic sea": (57.0, 19.0, 500), "norwegian sea": (68.0, 5.0, 600),
    "black sea": (43.5, 34.0, 500), "sea of japan": (40.0, 135.0, 600),
    "gulf of mexico": (25.0, -90.0, 800), "south pacific": (-20.0, -150.0, 3000),
}

TIPI_AIS = {3: "speciale", 35: "militare", 6: "passeggeri", 7: "cargo", 8: "petroliera/gasiera", 9: "altro"}


# ------------------------------------------------------------------ utilità
def ora_iso(ts=None):
    t = ts or dt.datetime.now(dt.timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%MZ")


def scarica(url, intestazioni=None, dati=None, timeout=60):
    h = {"User-Agent": UA, "Accept-Encoding": "gzip"}
    h.update(intestazioni or {})
    req = urllib.request.Request(url, headers=h, data=dati)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        b = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            b = gzip.decompress(b)
    return b


def area_di(lat, lon):
    for nome, (a, b, c, d) in AREE.items():
        if a <= lat <= c and b <= lon <= d:
            return nome
    return None


def tipo_testo(codice):
    try:
        c = int(codice)
    except (TypeError, ValueError):
        return ""
    if c == 35:
        return "militare"
    if 80 <= c <= 89:
        return "petroliera/gasiera (AIS %d)" % c
    return TIPI_AIS.get(c // 10, "altro") + " (AIS %d)" % c


def bandiera_da_mmsi(mmsi):
    """Paese di bandiera dichiarato dal MID (prime 3 cifre dell'MMSI): tabella ridotta."""
    mid = {
        "209": "CY", "210": "CY", "212": "CY", "215": "MT", "229": "MT", "248": "MT", "249": "MT",
        "256": "MT", "211": "DE", "218": "DE", "219": "DK", "220": "DK", "230": "FI", "231": "FO",
        "232": "GB", "235": "GB", "236": "GI", "237": "GR", "239": "GR", "240": "GR", "241": "GR",
        "244": "NL", "245": "NL", "246": "NL", "247": "IT", "257": "NO", "258": "NO", "259": "NO",
        "265": "SE", "266": "SE", "273": "RU", "275": "LV", "276": "EE", "277": "LT", "261": "PL",
        "304": "AG", "305": "AG", "308": "BS", "309": "BS", "311": "BS", "312": "BZ", "314": "BB",
        "341": "KN", "351": "PA", "352": "PA", "353": "PA", "354": "PA", "355": "PA", "356": "PA",
        "357": "PA", "370": "PA", "371": "PA", "372": "PA", "373": "PA", "374": "PA", "412": "CN",
        "413": "CN", "414": "CN", "422": "IR", "470": "AE", "471": "AE", "403": "SA", "477": "HK",
        "511": "PW", "518": "CK", "538": "MH", "563": "SG", "564": "SG", "565": "SG", "566": "SG",
        "572": "TV", "577": "VU", "613": "CM", "620": "KM", "626": "GA", "636": "LR", "637": "LR",
        "667": "SL", "671": "TG", "677": "TZ", "325": "JM",
        "205": "BE", "207": "BG", "224": "ES", "225": "ES", "226": "FR", "227": "FR", "228": "FR",
        "238": "HR", "250": "IE", "255": "PT", "263": "PT", "271": "TR", "272": "UA", "338": "US",
        "366": "US", "367": "US", "368": "US", "369": "US", "376": "VC", "377": "VC", "378": "VG",
        "419": "IN", "431": "JP", "440": "KR", "441": "KR", "445": "KP", "461": "OM", "463": "PK",
        "466": "QA", "468": "SY", "525": "ID", "533": "MY", "548": "PH", "574": "VN", "601": "ZA",
        "629": "GM", "631": "GQ", "657": "NG", "457": "MN", "447": "KW", "423": "AZ",
    }
    return mid.get(str(mmsi)[:3], "")


# ------------------------------------------------------------------ sanzioni
def carica_sanzioni(errori):
    """Legge docs/data/sanzioni-navi.json con tolleranza sullo schema (prodotto da altro agente)."""
    if not os.path.exists(SANZIONI):
        errori.append("sanzioni-navi.json assente: navi non incrociate con le liste di sanzioni")
        return {}, {}
    try:
        d = json.load(open(SANZIONI, encoding="utf-8"))
    except Exception as e:
        errori.append("sanzioni-navi.json illeggibile: %s" % e)
        return {}, {}
    voci = d.get("elementi") or d.get("navi") or (d if isinstance(d, list) else [])
    per_imo, per_mmsi = {}, {}
    for v in voci:
        if not isinstance(v, dict):
            continue
        da = v.get("sanzionata_da") or v.get("programmi") or v.get("liste") or v.get("autorita") or v.get("fonte") or ""
        if isinstance(da, list):
            da = ", ".join(str(x) for x in da)
        info = {"nome": v.get("nome") or v.get("name") or "", "da": str(da)}
        imo = re.sub(r"\D", "", str(v.get("imo") or v.get("IMO") or ""))
        mmsi = re.sub(r"\D", "", str(v.get("mmsi") or v.get("MMSI") or ""))
        if len(imo) == 7:
            per_imo[imo] = info
        if len(mmsi) == 9:
            per_mmsi[mmsi] = info
    return per_imo, per_mmsi


def verifica_sanzione(imo, mmsi, sanz):
    per_imo, per_mmsi = sanz
    if not per_imo and not per_mmsi:
        return "non verificato"
    info = per_imo.get(str(imo)) or per_mmsi.get(str(mmsi))
    if info:
        return "sì: " + (info["da"] or "lista sanzioni")
    return "no"


def nave(mmsi, imo, nome, tipo, lat, lon, sog, cog, t, area, fonte, sanz, **extra):
    imo = str(imo) if imo and str(imo) not in ("0", "Unknown") else ""
    r = {
        "mmsi": str(mmsi), "imo": imo, "nome": (nome or "").strip(), "tipo": tipo,
        "bandiera": bandiera_da_mmsi(mmsi), "lat": round(lat, 4), "lon": round(lon, 4),
        "velocita_nodi": sog, "rotta_gradi": cog, "ora_utc": t, "area": area,
        "sanzionata": verifica_sanzione(imo, mmsi, sanz), "fonte": fonte,
    }
    r.update(extra)
    return r


# ------------------------------------------------------------------ 1. Digitraffic
def fonte_digitraffic(sanz, errori):
    base = "https://meri.digitraffic.fi/api/ais/v1/"
    h = {"Digitraffic-User": "monitor-geoeconomico"}
    try:
        meta = json.loads(scarica(base + "vessels", h))
        pos = json.loads(scarica(base + "locations", h))
    except Exception as e:
        errori.append("Digitraffic non raggiungibile: %s" % e)
        return [], None
    per_mmsi = {m["mmsi"]: m for m in meta}
    out = []
    agg = pos.get("dataUpdatedTime", "")
    for f in pos.get("features", []):
        p = f["properties"]
        lon, lat = f["geometry"]["coordinates"]
        m = per_mmsi.get(f["mmsi"], {})
        st = m.get("shipType", 0) or 0
        imo = m.get("imo") or ""
        sanzionata = verifica_sanzione(imo, f["mmsi"], sanz).startswith("sì")
        area = area_di(lat, lon)
        cisterna = 80 <= st <= 89
        militare = st == 35
        if not ((cisterna and area) or sanzionata or (militare and area)):
            continue
        t = dt.datetime.fromtimestamp(p["timestampExternal"] / 1000, dt.timezone.utc)
        out.append(nave(f["mmsi"], imo, m.get("name"), tipo_testo(st), lat, lon,
                        p.get("sog"), p.get("cog"), ora_iso(t), area or "Baltico (copertura Digitraffic)",
                        "Digitraffic (Fintraffic)", sanz, destinazione=(m.get("destination") or "").strip(),
                        pescaggio_m=(m.get("draught") or 0) / 10 or None))
    return out, agg


# ------------------------------------------------------------------ 2. DMA (Stretti danesi)
def fonte_dma(sanz, errori, giorno=None):
    if os.environ.get("NAVI_DMA", "1") == "0":
        errori.append("DMA saltata (NAVI_DMA=0)")
        return [], None
    indici = ["http://aisdata.ais.dk/", "https://web.ais.dk/aisdata/"]
    elenco, base = [], None
    for u in indici:
        try:
            txt = scarica(u, timeout=60).decode("utf-8", "replace")
            elenco = sorted(set(re.findall(r"aisdk-(\d{4}-\d{2}-\d{2})\.zip", txt)))
            base = u
            if elenco:
                break
        except Exception as e:
            errori.append("DMA indice %s non raggiungibile: %s" % (u, e))
    if not elenco:
        return [], None
    giorno = giorno or elenco[-1]
    url = base + "aisdk-%s.zip" % giorno
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=600) as r:
            while True:
                b = r.read(1 << 20)
                if not b:
                    break
                tmp.write(b)
        tmp.close()
        return elabora_dma(tmp.name, sanz, giorno, url), giorno
    except Exception as e:
        errori.append("DMA %s: %s" % (url, e))
        return [], None
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


def elabora_dma(percorso_zip, sanz, giorno, url):
    """Legge il CSV DMA in streaming; tiene petroliere (Ship type 'Tanker') e navi sanzionate
    nel riquadro Stretti danesi. Restituisce una voce per nave con ultima posizione e stima
    del transito (nave vista sia a sud di 55,7°N sia a nord di 56,5°N nello stesso giorno)."""
    lat0, lon0, lat1, lon1 = AREE["Stretti danesi"]
    navi = {}
    with zipfile.ZipFile(percorso_zip) as z:
        nome_csv = [n for n in z.namelist() if n.endswith(".csv")][0]
        with z.open(nome_csv) as fb:
            rd = csv.reader(io.TextIOWrapper(fb, encoding="utf-8", errors="replace"))
            intest = [c.strip().lstrip("#").strip() for c in next(rd)]
            ix = {c: i for i, c in enumerate(intest)}
            for row in rd:
                try:
                    tipo = row[ix["Ship type"]]
                    mmsi = row[ix["MMSI"]]
                    imo = row[ix["IMO"]].replace("IMO", "").strip()
                    imo = imo if imo.isdigit() else ""
                    cisterna = tipo == "Tanker"
                    if not cisterna and not verifica_sanzione(imo, mmsi, sanz).startswith("sì"):
                        continue
                    lat = float(row[ix["Latitude"]]); lon = float(row[ix["Longitude"]])
                except (ValueError, IndexError, KeyError):
                    continue
                if not (lat0 <= lat <= lat1 and lon0 <= lon <= lon1):
                    continue
                n = navi.setdefault(mmsi, {"imo": imo, "nome": "", "tipo": tipo, "min_lat": lat, "max_lat": lat,
                                           "n": 0, "dest": ""})
                n["n"] += 1
                n["min_lat"] = min(n["min_lat"], lat); n["max_lat"] = max(n["max_lat"], lat)
                n["imo"] = n["imo"] or imo
                n["nome"] = row[ix["Name"]] or n["nome"]
                if "Destination" in ix:
                    n["dest"] = row[ix["Destination"]] or n["dest"]
                t = dt.datetime.strptime(row[ix["Timestamp"]], "%d/%m/%Y %H:%M:%S")
                if "t" not in n or t >= n["t"]:
                    def num(k):
                        try:
                            return float(row[ix[k]])
                        except (ValueError, KeyError):
                            return None
                    n.update(t=t, lat=lat, lon=lon, sog=num("SOG"), cog=num("COG"))
    out = []
    for mmsi, n in navi.items():
        if "t" not in n:
            continue
        out.append(nave(mmsi, n["imo"], n["nome"], "petroliera/gasiera" if n["tipo"] == "Tanker" else n["tipo"],
                        n["lat"], n["lon"], n["sog"], n["cog"], n["t"].strftime("%Y-%m-%dT%H:%MZ"),
                        "Stretti danesi", "Danish Maritime Authority (AIS storici %s)" % giorno, sanz,
                        transito_stimato=n["min_lat"] < 55.7 and n["max_lat"] > 56.5,
                        segnali_giorno=n["n"], destinazione=n["dest"].strip()))
    return out


# ------------------------------------------------------------------ 3. aisstream.io
def fonte_aisstream(sanz, errori):
    chiave = os.environ.get("AISSTREAM_API_KEY")
    if not chiave:
        errori.append("aisstream.io saltato: manca AISSTREAM_API_KEY (chiave gratuita su aisstream.io)")
        return []
    try:
        import asyncio
        import websockets  # pacchetto esterno, vedi requirements.txt
    except ImportError:
        errori.append("aisstream.io saltato: pacchetto 'websockets' non installato")
        return []
    minuti = float(os.environ.get("AISSTREAM_MINUTI", "10"))
    riquadri = [[[a, b], [c, d]] for (a, b, c, d) in AREE.values()]
    statici, ultime = {}, {}

    async def raccogli():
        async with websockets.connect("wss://stream.aisstream.io/v0/stream", open_timeout=30) as ws:
            sub = {"APIKey": chiave, "BoundingBoxes": riquadri,
                   "FilterMessageTypes": ["PositionReport", "ShipStaticData"]}
            # Filtro MMSI facoltativo (aisstream accetta al massimo 50 MMSI): solo se richiesto
            if os.environ.get("AISSTREAM_SOLO_SANZIONATE") == "1" and sanz[1]:
                sub["FiltersShipMMSI"] = list(sanz[1])[:50]
            await ws.send(json.dumps(sub))
            fine = asyncio.get_event_loop().time() + minuti * 60
            while True:
                resto = fine - asyncio.get_event_loop().time()
                if resto <= 0:
                    break
                try:
                    msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=resto))
                except asyncio.TimeoutError:
                    break
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                md = msg.get("MetaData", {})
                mmsi = md.get("MMSI")
                if msg.get("MessageType") == "ShipStaticData":
                    s = msg["Message"]["ShipStaticData"]
                    statici[mmsi] = {"tipo": s.get("Type"), "imo": s.get("ImoNumber"), "nome": s.get("Name"),
                                     "dest": s.get("Destination")}
                elif msg.get("MessageType") == "PositionReport":
                    p = msg["Message"]["PositionReport"]
                    ultime[mmsi] = {"lat": p["Latitude"], "lon": p["Longitude"], "sog": p.get("Sog"),
                                    "cog": p.get("Cog"), "t": md.get("time_utc", ""), "nome": md.get("ShipName")}
    try:
        asyncio.run(raccogli())
    except Exception as e:
        errori.append("aisstream.io errore: %s" % e)
    out = []
    for mmsi, p in ultime.items():
        s = statici.get(mmsi, {})
        st = s.get("tipo") or 0
        imo = s.get("imo") or ""
        sanzionata = verifica_sanzione(imo, mmsi, sanz).startswith("sì")
        if not (80 <= st <= 89 or st == 35 or sanzionata):
            continue  # navi senza messaggio statico ricevuto restano escluse (tipo ignoto)
        t = p["t"][:16].replace(" ", "T") + "Z" if p["t"] else ""
        out.append(nave(mmsi, imo, s.get("nome") or p.get("nome"), tipo_testo(st), p["lat"], p["lon"],
                        p["sog"], p["cog"], t, area_di(p["lat"], p["lon"]) or "", "aisstream.io", sanz,
                        destinazione=(s.get("dest") or "").strip()))
    return out


# ------------------------------------------------------------------ 4. Global Fishing Watch
def fonte_gfw(sanz, errori):
    """Eventi 'gap' (AIS spento) e incontri in mare negli ultimi 30 giorni dentro i riquadri."""
    chiave = os.environ.get("GFW_API_KEY")
    if not chiave:
        errori.append("Global Fishing Watch saltato: manca GFW_API_KEY (chiave gratuita non commerciale)")
        return []
    oggi = dt.date.today()
    h = {"Authorization": "Bearer " + chiave, "Content-Type": "application/json"}
    avvisi = []
    for ds, tipo in (("public-global-gaps-events:latest", "AIS spento"),
                     ("public-global-encounters-events:latest", "incontro in mare")):
        for area, (a, b, c, d) in AREE.items():
            corpo = {"datasets": [ds], "startDate": str(oggi - dt.timedelta(days=30)), "endDate": str(oggi),
                     "geometry": {"type": "Polygon", "coordinates": [[[b, a], [d, a], [d, c], [b, c], [b, a]]]}}
            try:
                r = json.loads(scarica("https://gateway.api.globalfishingwatch.org/v3/events?limit=50&offset=0",
                                       h, json.dumps(corpo).encode()))
            except Exception as e:
                errori.append("GFW %s %s: %s" % (tipo, area, e))
                continue
            for ev in r.get("entries", []):
                v = ev.get("vessel", {}) or {}
                pos = ev.get("position", {}) or {}
                if pos.get("lat") is None:
                    continue
                avvisi.append({"tipo_evento": tipo, "area": area, "inizio": ev.get("start"), "fine": ev.get("end"),
                               "lat": round(pos["lat"], 4), "lon": round(pos["lon"], 4),
                               "mmsi": str(v.get("ssvid", "")), "nome": v.get("name", ""),
                               "bandiera": v.get("flag", ""),
                               "sanzionata": verifica_sanzione("", v.get("ssvid", ""), sanz),
                               "fonte": "Global Fishing Watch", "id_evento": ev.get("id")})
    return avvisi


# ------------------------------------------------------------------ 5. USNI Fleet Tracker
def fonte_usni(errori):
    api = ("https://news.usni.org/wp-json/wp/v2/posts?search=%s&orderby=date&per_page=10&_fields=date_gmt,link,slug,title,content"
           % urllib.parse.quote("fleet and marine tracker"))
    try:
        posts = json.loads(scarica(api))
    except Exception as e:
        errori.append("USNI non raggiungibile: %s" % e)
        return [], None
    posts = [p for p in posts if p.get("slug", "").startswith("usni-news-fleet-and-marine-tracker")]
    if not posts:
        errori.append("USNI: nessun Fleet and Marine Tracker trovato")
        return [], None
    p = max(posts, key=lambda x: x["date_gmt"])
    h = p["content"]["rendered"]
    h = re.sub(r"<figure.*?</figure>", " ", h, flags=re.S)  # via le didascalie delle foto
    m = re.search(r"as of ([A-Z][a-z]+\.? \d{1,2}, \d{4})", re.sub(r"<[^>]+>", "", h))
    data_dichiarata = m.group(1) if m else p["date_gmt"][:10]
    pezzi = re.split(r"<h[1-6][^>]*>(.*?)</h[1-6]>", h)
    out, visti, regione = [], set(), None
    for i, pezzo in enumerate(pezzi):
        if i % 2 == 1:
            t = html.unescape(re.sub(r"<[^>]+>", "", pezzo)).strip()
            if re.match(r"^(In|At|Off|Near) ", t):
                regione = re.sub(r"^(In|At|Off|Near) (the )?", "", t).strip()
            continue
        if not regione:
            continue
        testo = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", pezzo)))
        for nm, scafo, numero in re.findall(r"USS\s+([A-Z][\w.'\- ]{1,40}?)\s*\((CVN|LHA|LHD|LPD|LSD|DDG|CG|LCS|SSN|SSGN)-(\d+)\)", testo):
            sigla = "%s-%s" % (scafo, numero)
            if sigla in visti:
                continue
            visti.add(sigla)
            cat = {"CVN": "nave-portaerei", "LHA": "nave-anfibia", "LHD": "nave-anfibia", "LPD": "nave-anfibia",
                   "LSD": "nave-anfibia", "SSN": "sottomarino", "SSGN": "sottomarino"}.get(scafo, "nave-scorta")
            centro = AREE_USNI.get(regione.lower())
            if not centro:
                for k, v in AREE_USNI.items():
                    if k in regione.lower():
                        centro = v
                        break
            voce = {"mmsi": "", "imo": "", "nome": "USS " + nm.strip(), "identificativo": sigla, "tipo": cat,
                    "bandiera": "US", "lat": centro[0] if centro else None, "lon": centro[1] if centro else None,
                    "velocita_nodi": None, "rotta_gradi": None, "ora_utc": "", "area": regione,
                    "sanzionata": "no", "fonte": "USNI News Fleet and Marine Tracker", "link": p["link"],
                    "data_fonte": data_dichiarata, "origine_coord": "centro dell'area dichiarata" if centro else "assente",
                    "precisione_km": centro[2] if centro else None,
                    "note": "Area dichiarata da USNI; la coordinata è il centro dell'area, non la posizione della nave."}
            out.append(voce)
    return out, {"data": data_dichiarata, "link": p["link"], "pubblicato_utc": p["date_gmt"]}


# ------------------------------------------------------------------ riepilogo e scie
def riepilogo(navi):
    r = {}
    for a in AREE:
        sel = [n for n in navi if n["area"] == a and n["tipo"].startswith("petroliera")]
        r[a] = {"petroliere_viste": len(sel),
                "sanzionate": sum(1 for n in sel if n["sanzionata"].startswith("sì")),
                "transiti_stimati": sum(1 for n in sel if n.get("transito_stimato")) if a == "Stretti danesi" else None,
                "fonti": sorted({n["fonte"] for n in sel})}
        if not sel:
            r[a]["nota"] = "nessuna fonte gratuita attiva per quest'area in questa esecuzione"
    return r


def aggiorna_scie(navi):
    prec = {}
    try:
        for n in json.load(open(USCITA, encoding="utf-8")).get("elementi", []):
            if n.get("mmsi"):
                prec[n["mmsi"]] = n.get("scia", [])
    except Exception:
        pass
    limite = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=SCIA_GIORNI)).strftime("%Y-%m-%dT%H:%MZ")
    for n in navi:
        if not n.get("mmsi"):
            continue
        s = [p for p in prec.get(n["mmsi"], []) if p[2] >= limite]
        punto = [n["lon"], n["lat"], n["ora_utc"]]
        if not s or s[-1][2] != punto[2]:
            s.append(punto)
        n["scia"] = s[-SCIA_MAX:]


def main():
    errori, fonti = [], []
    sanz = carica_sanzioni(errori)
    navi = []

    dg, agg = fonte_digitraffic(sanz, errori)
    navi += dg
    if agg:
        fonti.append({"nome": "Digitraffic, AIS marittimo (Fintraffic)", "link": "https://meri.digitraffic.fi/api/ais/v1/locations",
                      "licenza": "CC BY 4.0", "data_dato": agg})

    dm, giorno = fonte_dma(sanz, errori, os.environ.get("NAVI_DMA_GIORNO"))
    navi += dm
    if giorno:
        fonti.append({"nome": "Danish Maritime Authority, AIS storici", "link": "http://aisdata.ais.dk/",
                      "licenza": "uso libero con citazione della fonte (DMA)", "data_dato": giorno})

    ais = fonte_aisstream(sanz, errori)
    navi += ais
    if ais:
        fonti.append({"nome": "aisstream.io", "link": "https://aisstream.io", "licenza": "termini aisstream.io",
                      "data_dato": ora_iso()})

    avvisi = fonte_gfw(sanz, errori)
    if avvisi:
        fonti.append({"nome": "Global Fishing Watch API v3", "link": "https://globalfishingwatch.org/our-apis/",
                      "licenza": "CC BY-NC 4.0 (non commerciale)", "data_dato": ora_iso()})

    mil, info_usni = fonte_usni(errori)
    if info_usni:
        fonti.append({"nome": "USNI News Fleet and Marine Tracker", "link": info_usni["link"],
                      "licenza": "articolo protetto da copyright: si estraggono solo i fatti (nave, area)",
                      "data_dato": info_usni["data"]})

    # avviso semplice di "silenzio AIS": nave sanzionata con ultima posizione più vecchia di 6 ore
    adesso = dt.datetime.now(dt.timezone.utc)
    for n in navi:
        try:
            t = dt.datetime.strptime(n["ora_utc"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=dt.timezone.utc)
            ore = (adesso - t).total_seconds() / 3600
            if n["sanzionata"].startswith("sì") and ore > 6 and "Danish" not in n["fonte"]:
                n["avviso_ais"] = "nessuna posizione da %.0f ore" % ore
        except ValueError:
            pass

    aggiorna_scie(navi)
    navi.sort(key=lambda n: (n["area"], n["nome"]))
    dati = {
        "aggiornato": ora_iso(),
        "fonti": fonti,
        "nota": ("Ultime posizioni AIS raccolte davvero da fonti aperte. Riepilogo per area solo dalle fonti attive: "
                 "un'area senza fonte non significa zero navi. Navi militari USA: area dichiarata da USNI, coordinate "
                 "= centro dell'area. 'sanzionata' = incrocio IMO/MMSI con docs/data/sanzioni-navi.json "
                 "('non verificato' se il file manca). 'scia' = [lon, lat, ora_utc] delle ultime esecuzioni."),
        "riepilogo_aree": riepilogo(navi),
        "elementi": navi,
        "militari_usni": mil,
        "avvisi_ais": avvisi,
        "errori": errori,
    }
    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    with open(USCITA, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=1)
    print("navi: %d, militari USNI: %d, avvisi GFW: %d, errori: %d" % (len(navi), len(mil), len(avvisi), len(errori)))
    for e in errori:
        print("  avviso:", e, file=sys.stderr)


if __name__ == "__main__":
    main()
