#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agente RETI ELETTRICHE dell'osservatorio geoeconomico.

Produce tre file in docs/data/:
  - rete-elettrica.json   linee >= 380 kV ed elettrodotti HVDC (ogni tensione) da OpenStreetMap
  - interconnessioni.json elettrodotti strategici (sottomarini e transfrontalieri) con MW, stato, fonte
  - nucleare.json         centrali nucleari (Europa, Ucraina, Russia, Medio Oriente, Nord Africa)

Solo libreria standard. Fonti:
  1. Overpass API (overpass-api.de): solo con ELETTRICITA_OVERPASS=1 (prova breve, poi riquadri da 10 gradi).
  2. Tessere vettoriali di OpenInfraMap (dati OpenStreetMap, ODbL), zoom 5: fonte usata di norma.
  3. PyPSA-Eur "Prebuilt Electricity Network" su Zenodo (ODbL): riserva per l'Europa e geometrie HVDC.
  4. Global Energy Monitor, Global Nuclear Power Tracker (CC BY 4.0), file geojson della mappa pubblica.
Uso: python3 raccolta/elettricita/raccogli.py
"""
import csv
import gzip
import io
import json
import math
import os
import re
import struct
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(BASE, "docs", "data")
UA = "monitor-geoeconomico/1.0 (osservatorio OSINT personale, non commerciale)"
OGGI = datetime.now(timezone.utc)
AGG = OGGI.strftime("%Y-%m-%dT%H:%MZ")

# riquadro dell'area: Europa, Ucraina, Russia europea, Turchia, Medio Oriente, Nord Africa
LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = -25.0, 65.0, 12.0, 72.0
ZOOM = 5
OIM_TILE = "https://openinframap.org/tiles/{z}/{x}/{y}.pbf"
OIM_TILEJSON = "https://openinframap.org/map.json"
ZENODO_CONCEPT = "12799201"  # PyPSA-Eur prebuilt network (tutte le versioni)
GEM_CONFIG = "https://globalenergymonitor.github.io/interim-maps/trackers/gnpt/config.js"

errori = {"rete": [], "inter": [], "nucleare": []}


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def get(url, data=None, timeout=90, tries=3, pause=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                b = r.read()
                if r.headers.get("Content-Encoding") == "gzip" or b[:2] == b"\x1f\x8b":
                    try:
                        b = gzip.decompress(b)
                    except OSError:
                        pass
                return b
        except Exception as e:  # rete instabile: riprova
            last = e
            time.sleep(pause * (i + 1))
    raise last


# ---------------------------------------------------------------- geometria
def dp(pts, tol):
    """Douglas-Peucker iterativo su liste di (lon, lat)."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        nn = dx * dx + dy * dy
        md, mi = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            if nn == 0:
                d = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / nn))
                d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2
            if d > md:
                md, mi = d, i
        if md > tol * tol and mi > 0:
            keep[mi] = True
            stack.append((a, mi))
            stack.append((mi, b))
    return [p for p, k in zip(pts, keep) if k]


def unisci_parti(parts, eps=0.02):
    """Unisce le parti che si toccano agli estremi (i pezzi tagliati ai bordi delle tessere)."""
    parts = [list(p) for p in parts if len(p) >= 2]
    changed = True
    while changed and len(parts) > 1:
        changed = False
        for i in range(len(parts)):
            for j in range(len(parts)):
                if i == j:
                    continue
                a, b = parts[i], parts[j]
                if abs(a[-1][0] - b[0][0]) < eps and abs(a[-1][1] - b[0][1]) < eps:
                    parts[i] = a + b[1:]
                elif abs(a[-1][0] - b[-1][0]) < eps and abs(a[-1][1] - b[-1][1]) < eps:
                    parts[i] = a + b[::-1][1:]
                else:
                    continue
                parts.pop(j)
                changed = True
                break
            if changed:
                break
    return parts


def lunghezza_km(parts):
    km = 0.0
    for p in parts:
        for (x1, y1), (x2, y2) in zip(p, p[1:]):
            km += 111.32 * math.hypot((x2 - x1) * math.cos(math.radians((y1 + y2) / 2)), y2 - y1)
    return km


def arrotonda(parts, nd=3):
    out = []
    for p in parts:
        q = []
        for x, y in p:
            c = [round(x, nd), round(y, nd)]
            if not q or q[-1] != c:
                q.append(c)
        if len(q) >= 2:
            out.append(q)
    return out


# ---------------------------------------------------------------- Mapbox Vector Tile (decoder minimo)
def _varint(b, i):
    r = s = 0
    while True:
        c = b[i]
        i += 1
        r |= (c & 0x7F) << s
        s += 7
        if c < 0x80:
            return r, i


def _fields(b):
    i, n = 0, len(b)
    while i < n:
        k, i = _varint(b, i)
        f, t = k >> 3, k & 7
        if t == 0:
            v, i = _varint(b, i)
        elif t == 2:
            l, i = _varint(b, i)
            v = b[i:i + l]
            i += l
        elif t == 5:
            v = b[i:i + 4]
            i += 4
        elif t == 1:
            v = b[i:i + 8]
            i += 8
        else:
            raise ValueError("wire type %d" % t)
        yield f, t, v


def _packed(b):
    out, i = [], 0
    while i < len(b):
        v, i = _varint(b, i)
        out.append(v)
    return out


def _value(b):
    for f, t, v in _fields(b):
        if f == 1:
            return v.decode("utf8", "replace")
        if f == 2:
            return struct.unpack("<f", v)[0]
        if f == 3:
            return struct.unpack("<d", v)[0]
        if f in (4, 5):
            return v
        if f == 6:
            return (v >> 1) ^ -(v & 1)
        if f == 7:
            return bool(v)
    return None


def mvt_layers(data, wanted):
    for f, t, v in _fields(data):
        if f != 3:
            continue
        name, keys, vals, feats, ext = None, [], [], [], 4096
        for f2, t2, v2 in _fields(v):
            if f2 == 1:
                name = v2.decode()
            elif f2 == 3:
                keys.append(v2.decode())
            elif f2 == 4:
                vals.append(_value(v2))
            elif f2 == 5:
                ext = v2
            elif f2 == 2:
                feats.append(v2)
        if name not in wanted:
            continue
        out = []
        for fb in feats:
            tags, geom, gt = [], [], 0
            for f3, t3, v3 in _fields(fb):
                if f3 == 2:
                    tags = _packed(v3)
                elif f3 == 3:
                    gt = v3
                elif f3 == 4:
                    geom = _packed(v3)
            props = {keys[tags[j]]: vals[tags[j + 1]] for j in range(0, len(tags) - 1, 2)}
            out.append((props, gt, geom))
        yield name, ext, out


def mvt_parts(geom):
    parts, x, y, i, cur = [], 0, 0, 0, None
    while i < len(geom):
        c = geom[i]
        i += 1
        cmd, cnt = c & 7, c >> 3
        if cmd in (1, 2):
            for _ in range(cnt):
                dx = (geom[i] >> 1) ^ -(geom[i] & 1)
                dy = (geom[i + 1] >> 1) ^ -(geom[i + 1] & 1)
                i += 2
                x += dx
                y += dy
                if cmd == 1:
                    cur = [(x, y)]
                    parts.append(cur)
                else:
                    cur.append((x, y))
    return parts


def tile_xy(lon, lat, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
    return x, y


def px2ll(tx, ty, z, px, py, ext):
    n = 2 ** z
    lon = (tx + px / ext) / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (ty + py / ext) / n))))
    return lon, lat


def tensione_kv(p):
    vs = []
    for k in ("voltage", "voltage_2", "voltage_3", "voltage_4"):
        v = p.get(k)
        if isinstance(v, (int, float)) and v > 0:
            vs.append(float(v))
    return max(vs) if vs else None


# ---------------------------------------------------------------- 1. RETE
def prova_overpass():
    q = '[out:json][timeout:25];way["power"="line"]["voltage"="380000"](45.0,9.0,45.2,9.2);out ids 1;'
    try:
        b = get("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": q}).encode(), timeout=40, tries=1)
        json.loads(b)
        return True
    except Exception as e:
        errori["rete"].append("Overpass API (overpass-api.de) non raggiungibile da questo ambiente: %s" % str(e)[:120])
        return False


def rete_overpass():
    """Overpass a riquadri da 10 gradi, con pause. Restituisce dict osm_id -> elemento grezzo."""
    feats = {}
    for lat in range(int(LAT_MIN), int(LAT_MAX), 10):
        for lon in range(int(LON_MIN), int(LON_MAX), 10):
            bb = "%d,%d,%d,%d" % (lat, lon, min(lat + 10, LAT_MAX), min(lon + 10, LON_MAX))
            q = ('[out:json][timeout:180];('
                 'way["power"~"^(line|cable)$"]["voltage"~"(^|;)(3[89][0-9]|[4-9][0-9][0-9]|1[0-9]{3})[0-9]{3}(;|$)"](%s);'
                 'way["power"~"^(line|cable)$"]["frequency"="0"](%s););out tags geom;') % (bb, bb)
            try:
                b = get("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": q}).encode(), timeout=240, tries=2, pause=10)
                for el in json.loads(b).get("elements", []):
                    t = el.get("tags", {})
                    vs = [float(v) / 1000 for v in re.findall(r"\d+", t.get("voltage", "")) if v.isdigit()]
                    pts = [(g["lon"], g["lat"]) for g in el.get("geometry", []) if g]
                    if len(pts) < 2:
                        continue
                    feats[el["id"]] = {
                        "props": {"name": t.get("name", ""), "operator": t.get("operator", ""),
                                  "frequency": t.get("frequency"), "construction": t.get("power") == "construction",
                                  "type": t.get("power")},
                        "kv": max(vs) if vs else None, "parts": [pts]}
            except Exception as e:
                errori["rete"].append("Overpass riquadro %s: %s" % (bb, str(e)[:100]))
            time.sleep(5)
    return feats


def rete_oim():
    """Tessere vettoriali OpenInfraMap, zoom 5, strato power_line. Restituisce (linee, sottostazioni)."""
    try:
        tj = json.loads(get(OIM_TILEJSON, timeout=30))
        url = tj.get("tiles", [OIM_TILE])[0]
    except Exception as e:
        errori["rete"].append("map.json di OpenInfraMap non letto (%s): uso l'indirizzo noto" % str(e)[:80])
        url = OIM_TILE
    x0, y1 = tile_xy(LON_MIN, LAT_MIN, ZOOM)
    x1, y0 = tile_xy(LON_MAX - 1e-9, LAT_MAX, ZOOM)
    feats, subs, ok, ko = {}, [], 0, 0
    for tx in range(x0, x1 + 1):
        for ty in range(y0, y1 + 1):
            u = url.replace("{z}", str(ZOOM)).replace("{x}", str(tx)).replace("{y}", str(ty))
            try:
                data = get(u, timeout=60)
                ok += 1
            except Exception as e:
                ko += 1
                errori["rete"].append("tessera %d/%d/%d: %s" % (ZOOM, tx, ty, str(e)[:80]))
                continue
            for name, ext, fl in mvt_layers(data, {"power_line", "power_substation_point"}):
                for p, gt, g in fl:
                    if name == "power_substation_point":
                        if p.get("name") and gt == 1 and len(g) >= 3:
                            px, py = (g[1] >> 1) ^ -(g[1] & 1), (g[2] >> 1) ^ -(g[2] & 1)
                            lon, lat = px2ll(tx, ty, ZOOM, px, py, ext)
                            subs.append({"nome": p.get("name"), "lon": lon, "lat": lat,
                                         "kv": tensione_kv(p), "operatore": p.get("operator", "")})
                        continue
                    if gt != 2 or p.get("disused"):
                        continue
                    kv = tensione_kv(p)
                    hvdc = str(p.get("frequency", "")).strip() == "0"
                    if not hvdc and (kv is None or kv < 380):
                        continue
                    oid = p.get("osm_id")
                    parts = [[px2ll(tx, ty, ZOOM, a, b, ext) for a, b in part] for part in mvt_parts(g)]
                    f = feats.setdefault(oid, {"props": p, "kv": kv, "parts": []})
                    f["parts"].extend(parts)
            time.sleep(1.0)
    log("OpenInfraMap: tessere lette %d, fallite %d, linee %d" % (ok, ko, len(feats)))
    if ok == 0:
        raise RuntimeError("nessuna tessera OpenInfraMap letta")
    return feats, subs


def zenodo_pypsa():
    """Scarica lines.csv e links.csv dell'ultima versione del dataset PyPSA-Eur su Zenodo."""
    meta = json.loads(get("https://zenodo.org/api/records/%s/versions/latest" % ZENODO_CONCEPT, timeout=60))
    files = {f["key"]: f["links"]["self"] for f in meta.get("files", [])}
    info = {"versione": meta.get("metadata", {}).get("version"), "data": meta.get("metadata", {}).get("publication_date"),
            "link": meta.get("links", {}).get("self_html") or ("https://zenodo.org/records/%s" % meta.get("id")),
            "doi": meta.get("doi")}
    out = {}
    for k in ("links.csv", "lines.csv"):
        if k in files:
            out[k] = get(files[k], timeout=300).decode("utf8", "replace")
    return info, out


def wkt_parts(s):
    s = s.strip().strip("'")
    parts = []
    for grp in re.findall(r"\(([^()]+)\)", s):
        pts = []
        for c in grp.split(","):
            xy = c.split()
            if len(xy) >= 2:
                pts.append((float(xy[0]), float(xy[1])))
        if len(pts) >= 2:
            parts.append(pts)
    return parts


def rete_da_pypsa(tabelle):
    csv.field_size_limit(10 ** 9)
    feats = {}
    for r in csv.DictReader(io.StringIO(tabelle.get("lines.csv", ""))):
        try:
            kv = float(r["voltage"])
        except ValueError:
            continue
        if kv < 380:
            continue
        feats[r["line_id"]] = {"props": {"name": "", "operator": "", "construction": r.get("under_construction") == "t",
                                          "type": "cable" if r.get("underground") == "t" else "line"},
                               "kv": kv, "parts": wkt_parts(r["geometry"])}
    for r in csv.DictReader(io.StringIO(tabelle.get("links.csv", ""))):
        feats[r["link_id"]] = {"props": {"name": "", "operator": "", "frequency": "0",
                                          "construction": r.get("under_construction") == "t",
                                          "type": "cable" if r.get("underground") == "t" else "line"},
                               "kv": float(r["voltage"] or 0), "parts": wkt_parts(r["geometry"]), "mw": r.get("p_nom")}
    return feats


def costruisci_rete(feats, tol=0.012):
    """Raggruppa per (nome, tensione, HVDC, operatore, stato), unisce, semplifica."""
    gruppi = {}
    for oid, f in feats.items():
        p = f["props"]
        hvdc = str(p.get("frequency", "")).strip() == "0"
        kv = int(round(f["kv"])) if f["kv"] else None
        nome = (p.get("name") or "").strip()
        op = (p.get("operator") or "").strip()
        stato = "in costruzione" if p.get("construction") else "in esercizio"
        cavo = p.get("type") == "cable"
        k = (nome, kv, hvdc, op, stato, cavo)
        g = gruppi.setdefault(k, {"ids": [], "parts": [], "mw": f.get("mw")})
        g["ids"].append(oid)
        g["parts"].extend(f["parts"])
    elementi = []
    for (nome, kv, hvdc, op, stato, cavo), g in gruppi.items():
        parts = unisci_parti(g["parts"])
        parts = [dp(p, tol) for p in parts]
        parts = arrotonda(parts, 3)
        if not parts:
            continue
        km = lunghezza_km(parts)
        if km < 3 and not hvdc:
            continue  # spezzoni minimi ai bordi delle tessere
        e = {"nome": nome, "tensione_kv": kv, "hvdc": hvdc, "operatore": op, "stato": stato,
             "tipo": "cavo" if cavo else "linea aerea", "km_mappa": round(km), "osm": len(g["ids"]), "g": parts}
        if g.get("mw"):
            e["mw"] = g["mw"]
        elementi.append(e)
    elementi.sort(key=lambda e: (-(e["hvdc"]), -(e["tensione_kv"] or 0), e["nome"]))
    return elementi


# ---------------------------------------------------------------- 2. INTERCONNESSIONI
# Fatti curati a mano: ogni voce ha fonte, link e data. Coordinate dei terminali solo se verificate
# (Wikipedia, coordinate delle stazioni di conversione) oppure prese dai dati OSM/PyPSA dallo script.
INTERCONNESSIONI = [
    {"id": "EL-IC-01", "nome": "SA.PE.I. (Sardegna - Lazio)", "paesi": ["IT"], "tipo": "HVDC sottomarino",
     "da": "Fiume Santo (SS)", "a": "Latina", "mw": 1000, "kv": 500, "km": 435, "stato": "in esercizio", "anno": "2011",
     "terminali": [[8.30583, 40.84139], [12.80694, 41.42972]], "osm_rel": "relation/8185711",
     "fonte": "Wikipedia (SAPEI), dati Terna", "link": "https://en.wikipedia.org/wiki/SAPEI", "data_fonte": "2026-11-09",
     "affidabilita": "alta", "note": "Due poli da 500 MW. Lega la Sardegna al continente; cavo record di profondita' (circa 1.640 m)."},
    {"id": "EL-IC-02", "nome": "MON.ITA (Italia - Montenegro)", "paesi": ["IT", "ME"], "tipo": "HVDC sottomarino",
     "da": "Cepagatti (PE)", "a": "Lastva (Kotor)", "mw": 600, "mw_progetto": 1200, "kv": 500, "km": 445,
     "stato": "in esercizio (1 polo su 2)", "anno": "2019",
     "osm_rel": "relation/8185767", "sottostazioni": ["Cepagatti", "Lastva"],
     "fonte": "Terna; PyPSA-Eur su OSM indica 1.200 MW di progetto", "link": "https://www.terna.it/it/progetti-territorio/progetti-incentivati/interconnessione-italia-montenegro",
     "data_fonte": "2026-11-09", "affidabilita": "media",
     "note": "Primo polo da 600 MW in esercizio da fine 2019; il secondo polo (altri 600 MW) non risulta completato. Porta dei Balcani verso l'Italia."},
    {"id": "EL-IC-03", "nome": "GRITA (Italia - Grecia)", "paesi": ["IT", "GR"], "tipo": "HVDC sottomarino",
     "da": "Galatina (LE)", "a": "Arachthos", "mw": 500, "kv": 400, "km": 313, "stato": "in esercizio", "anno": "2002",
     "terminali": [[18.13028, 40.16472], [20.96333, 39.18333]], "osm_rel": "relation/8185664",
     "fonte": "Wikipedia (HVDC Italy-Greece)", "link": "https://en.wikipedia.org/wiki/HVDC_Italy%E2%80%93Greece",
     "data_fonte": "2026-11-09", "affidabilita": "alta", "note": "Monopolare. Terna ha in programma un secondo collegamento (GRITA 2)."},
    {"id": "EL-IC-04", "nome": "Piemonte - Savoia (Piossasco - Grand'Ile)", "paesi": ["IT", "FR"], "tipo": "HVDC terrestre in cavo",
     "da": "Piossasco (TO)", "a": "Grand'Ile (Savoia)", "mw": 1200, "kv": 320, "km": 190, "stato": "in esercizio", "anno": "2022",
     "sottostazioni": ["Piossasco", "Grand'?[IÎ]le"],
     "fonte": "Terna / RTE", "link": "https://www.terna.it/it/progetti-territorio/progetti-incentivati/interconnessione-italia-francia",
     "data_fonte": "2026-11-09", "affidabilita": "media",
     "note": "Due moduli da 600 MW (VSC), cavo interrato lungo l'autostrada del Frejus e nella galleria di sicurezza. Non presente come linea nel dataset PyPSA-Eur."},
    {"id": "EL-IC-05", "nome": "ELMED (Italia - Tunisia)", "paesi": ["IT", "TN"], "tipo": "HVDC sottomarino",
     "da": "Partanna (TP)", "a": "Mlaabi (Menzel Temime)", "mw": 600, "km": 220, "stato": "in costruzione", "anno": "previsto 2028",
     "sottostazioni": ["Partanna", "Mlaabi"],
     "fonte": "Hitachi Energy, comunicato del 24 giugno 2026", "link": "https://www.hitachienergy.com/news-and-events/press-releases/2026/06/terna-steg-and-hitachi-energy-770-million-contract-for-elmed-converter-stations-the-first-direct-current-interconnection-between-europe-and-north-africa",
     "data_fonte": "2026-06-24", "affidabilita": "alta",
     "note": "Primo collegamento in corrente continua Europa - Nord Africa. Contratto da 770 milioni di euro per le stazioni di conversione a Hitachi Energy (giugno 2026). Investimento totale 1.420 milioni di euro, di cui 307 milioni dal programma UE CEF (primo finanziamento UE a un progetto con un paese terzo). Profondita' massima circa 800 m nel Canale di Sicilia. Data di entrata in esercizio non confermata da fonte del 2026."},
    {"id": "EL-IC-06", "nome": "Tyrrhenian Link - ramo est (Campania - Sicilia)", "paesi": ["IT"], "tipo": "HVDC sottomarino",
     "da": "Eboli (SA)", "a": "Termini Imerese (PA)", "mw": 1000, "kv": 500, "km": 490, "stato": "in costruzione",
     "anno": "primo polo previsto 2026, intera opera 2028", "sottostazioni": ["Eboli", "Termini Imerese"],
     "fonte": "QualEnergia / Terna (posa completata maggio 2025)", "link": "https://www.qualenergia.it/articoli/completata-la-posa-del-ramo-est-del-tyrrhenian-link-tra-campania-e-sicilia/",
     "data_fonte": "2025-05", "affidabilita": "media",
     "note": "Posato il primo cavo (circa 490 km) tra Termini Imerese e Battipaglia nel maggio 2025. A luglio 2026 consegnati i trasformatori alla stazione di Termini Imerese. Nessuna conferma trovata dell'entrata in esercizio al 2026-11-09."},
    {"id": "EL-IC-07", "nome": "Tyrrhenian Link - ramo ovest (Sicilia - Sardegna)", "paesi": ["IT"], "tipo": "HVDC sottomarino",
     "da": "Termini Imerese (PA)", "a": "Selargius (CA)", "mw": 1000, "kv": 500, "km": 480, "stato": "in costruzione",
     "anno": "previsto 2028", "sottostazioni": ["Selargius"],
     "fonte": "T&D World / Terna (posa ramo ovest, gennaio 2026)", "link": "https://tdworld.com/distributed-energy-resources/news/55342158/terna-completes-installation-of-the-western-branch-of-the-tyrrhenian-link",
     "data_fonte": "2026-01", "affidabilita": "media", "note": "Con il ramo est forma il collegamento Campania-Sicilia-Sardegna da 1.000 MW per ramo."},
    {"id": "EL-IC-08", "nome": "Estlink 1 (Estonia - Finlandia)", "paesi": ["EE", "FI"], "tipo": "HVDC sottomarino",
     "da": "Harku", "a": "Espoo", "mw": 350, "kv": 150, "km": 105, "stato": "in esercizio", "anno": "2006",
     "terminali": [[24.56028, 59.38472], [24.55167, 60.20389]], "osm_rel": "relation/8184630",
     "fonte": "Wikipedia (Estlink)", "link": "https://en.wikipedia.org/wiki/Estlink", "data_fonte": "2026-11-09", "affidabilita": "alta", "note": ""},
    {"id": "EL-IC-09", "nome": "Estlink 2 (Estonia - Finlandia)", "paesi": ["EE", "FI"], "tipo": "HVDC sottomarino",
     "da": "Puessi", "a": "Anttila", "mw": 650, "kv": 450, "km": 170, "stato": "in esercizio", "anno": "2014",
     "terminali": [[27.06389, 59.36722], [25.36694, 60.37667]], "osm_rel": "relation/6886400",
     "fonte": "Helsinki Times / Wikipedia", "link": "https://www.helsinkitimes.fi/finland/finland-news/domestic/27201-estlink-2-power-link-restored-after-six-month-outage.html",
     "data_fonte": "2025-06-20", "affidabilita": "alta",
     "note": "Danneggiato il 25 dicembre 2024 dall'ancora della petroliera Eagle S (flotta ombra russa, secondo le autorita' finlandesi); tornato in servizio a giugno 2025 dopo sei mesi."},
    {"id": "EL-IC-10", "nome": "NordBalt (Svezia - Lituania)", "paesi": ["SE", "LT"], "tipo": "HVDC sottomarino",
     "da": "Nybro", "a": "Klaipeda", "mw": 700, "kv": 300, "km": 450, "stato": "in esercizio", "anno": "2016",
     "terminali": [[15.85417, 56.76778], [21.25667, 55.68167]], "osm_rel": "relation/8185455",
     "fonte": "Wikipedia (NordBalt)", "link": "https://en.wikipedia.org/wiki/NordBalt", "data_fonte": "2026-11-09", "affidabilita": "alta", "note": ""},
    {"id": "EL-IC-11", "nome": "LitPol Link (Lituania - Polonia)", "paesi": ["LT", "PL"], "tipo": "AC 400 kV (ex back-to-back HVDC)",
     "da": "Alytus", "a": "Elk", "mw": 500, "kv": 400, "km": 163, "stato": "in esercizio", "anno": "2015",
     "terminali": [[23.96722, 54.43861], [22.32222, 53.77361]],
     "fonte": "Wikipedia (LitPol Link)", "link": "https://en.wikipedia.org/wiki/LitPol_Link", "data_fonte": "2026-11-09", "affidabilita": "media",
     "note": "Fino al 2025 unico ponte terrestre dei Baltici verso l'Europa continentale (stazione back-to-back ad Alytus); dopo la sincronizzazione del 9 febbraio 2025 e' la linea sincrona AC verso la Polonia."},
    {"id": "EL-IC-12", "nome": "Sincronizzazione dei Baltici con l'Europa continentale", "paesi": ["EE", "LV", "LT"], "tipo": "evento di rete",
     "stato": "completata", "anno": "2025", "mw": None,
     "fonte": "ENTSO-E", "link": "https://www.entsoe.eu/news/2025/02/09/entso-e-confirms-successful-synchronization-of-the-continental-european-electricity-system-with-the-systems-of-the-baltic-countries/",
     "data_fonte": "2025-02-09", "affidabilita": "alta",
     "note": "8 febbraio 2025: distacco dal sistema russo IPS/UPS (anello BRELL) e prova in isola. 9 febbraio 2025: sincronizzazione con l'Europa continentale. 28 novembre 2025: ENTSO-E dichiara concluso il progetto. Il punto e' messo sulla stazione di Alytus (LitPol)."},
    {"id": "EL-IC-13", "nome": "Ucraina e Moldova - ENTSO-E", "paesi": ["UA", "MD"], "tipo": "sincronizzazione AC",
     "stato": "in esercizio (sincronizzazione d'emergenza dal 16 marzo 2022)", "anno": "2022", "mw": 2450, "mw_export": 900,
     "fonte": "DiXi Group", "link": "https://dixigroup.org/en/the-last-month-of-winter-became-a-record-for-electricity-imports-to-ukraine/",
     "data_fonte": "2026-03", "affidabilita": "media",
     "note": "Limite d'importazione dall'UE verso Ucraina e Moldova portato a 2,45 GW da gennaio 2026 (prima 2,15 GW); circa 2,1 GW disponibili all'Ucraina. Limite d'esportazione 900 MW. Febbraio 2026: import record di 1.262,8 GWh. Nessun punto in mappa: il confine occidentale ucraino e' il fronte di scambio (PL, SK, HU, RO, MD)."},
    {"id": "EL-IC-14", "nome": "Francia - Spagna (Baixas - Santa Llogaia, INELFE)", "paesi": ["FR", "ES"], "tipo": "HVDC terrestre in cavo",
     "da": "Baixas", "a": "Santa Llogaia", "mw": 2000, "kv": 320, "km": 64, "stato": "in esercizio", "anno": "2015",
     "osm_rel": "relation/9934065",
     "fonte": "PyPSA-Eur su OpenStreetMap (2 collegamenti da 1.000 MW)", "link": "https://zenodo.org/records/23896564",
     "data_fonte": "2026-11-02", "affidabilita": "media",
     "note": "Il principale ponte della Penisola iberica verso il resto d'Europa; l'isolamento elettrico iberico e' uno dei fattori discussi dopo il blackout del 28 aprile 2025. In costruzione il collegamento sottomarino del Golfo di Biscaglia (2.000 MW)."},
    {"id": "EL-IC-15", "nome": "Great Sea Interconnector (Grecia - Cipro - Israele)", "paesi": ["GR", "CY", "IL"], "tipo": "HVDC sottomarino",
     "da": "Creta", "a": "Cipro", "mw": 1000, "stato": "rinviato", "anno": "oltre il 2029",
     "fonte": "Cyprus Mail", "link": "https://cyprus-mail.com/2026/10/24/nexans-prepares-for-possible-gsi-restart-in-2028-as-uncertainty-persists",
     "data_fonte": "2026-10-24", "affidabilita": "media",
     "note": "Nexans esclude il progetto dalla guida 2026; produzione forse ripresa nel 2028. Gennaio 2026: consegna oltre fine 2029. Agosto 2026: Meridiam entra nel capitale. Progetto di interesse comune UE. Nessun terminale in mappa."},
    {"id": "EL-IC-16", "nome": "Egitto - Arabia Saudita", "paesi": ["EG", "SA"], "tipo": "HVDC (aereo e sottomarino nel Mar Rosso)",
     "da": "Badr (Cairo est)", "a": "Tabuk / Medina est", "mw": 3000, "km": 1350, "stato": "in collaudo (stato attuale non confermato)",
     "anno": "previsto 2026",
     "fonte": "SolarQuarter (fase finale di prova, febbraio 2026)", "link": "https://solarquarter.com/2026/02/23/egypt-saudi-power-grid-interconnection-enters-final-testing-phase/",
     "data_fonte": "2026-02-23", "affidabilita": "bassa",
     "note": "Due fasi da 1.500 MW, tre stazioni di conversione (Badr, Tabuk, Medina est), costo circa 1,8 miliardi di dollari. Obiettivo del governo egiziano: piena operativita' ad aprile 2026; non trovata conferma dell'esercizio commerciale."},
]


def costruisci_interconnessioni(pypsa_links, sottostazioni):
    elementi = []
    for ic in INTERCONNESSIONI:
        e = {k: v for k, v in ic.items() if k not in ("terminali", "osm_rel", "sottostazioni")}
        e["categoria"] = "interconnessione-elettrica"
        e["g"] = []
        geo_fonte = None
        rel = ic.get("osm_rel")
        if rel and pypsa_links:
            for r in pypsa_links:
                if r["link_id"].startswith(rel + "-"):
                    parts = arrotonda([dp(p, 0.01) for p in wkt_parts(r["geometry"])], 3)
                    e["g"].extend(parts)
                    e.setdefault("mw_pypsa", 0)
                    e["mw_pypsa"] += int(float(r["p_nom"] or 0))
                    geo_fonte = "tracciato da PyPSA-Eur/OpenStreetMap (%s)" % rel
        punti = ic.get("terminali")
        if punti:
            e["terminali_fonte"] = "coordinate delle stazioni di conversione da Wikipedia"
        elif ic.get("sottostazioni") and sottostazioni:
            punti = []
            for pat in ic["sottostazioni"]:
                rx = re.compile(pat, re.I)
                cand = [s for s in sottostazioni if rx.search(s["nome"] or "")]
                if cand:
                    s = max(cand, key=lambda s: s["kv"] or 0)
                    punti.append([round(s["lon"], 4), round(s["lat"], 4)])
                    e.setdefault("terminali_osm", []).append(s["nome"])
            if punti:
                e["terminali_fonte"] = "sottostazioni OpenStreetMap trovate per nome (tessere OpenInfraMap)"
        if not punti and e["g"]:
            punti = [e["g"][0][0], e["g"][-1][-1]]
            e["terminali_fonte"] = "estremi del tracciato OSM"
        e["terminali"] = punti or []
        if punti:
            e["lon"], e["lat"] = punti[0][0], punti[0][1]
        elif ic["id"] == "EL-IC-12":
            e["lon"], e["lat"] = 23.96722, 54.43861
            e["terminali_fonte"] = "punto sulla stazione di Alytus (Wikipedia, LitPol Link)"
        else:
            e["lon"] = e["lat"] = None
        if not e["g"] and len(punti) == 2:
            e["g"] = [punti]
            e["tracciato"] = "schematico: retta tra i terminali, non il percorso reale"
        elif e["g"]:
            e["tracciato"] = geo_fonte
        else:
            e["tracciato"] = "mancante"
        elementi.append(e)
    return elementi


# ---------------------------------------------------------------- 3. NUCLEARE
PAESI = {
    "Albania": "AL", "Armenia": "AM", "Austria": "AT", "Belarus": "BY", "Belgium": "BE", "Bosnia and Herzegovina": "BA",
    "Bulgaria": "BG", "Croatia": "HR", "Cyprus": "CY", "Czechia": "CZ", "Czech Republic": "CZ", "Denmark": "DK",
    "Estonia": "EE", "Finland": "FI", "France": "FR", "Germany": "DE", "Greece": "GR", "Hungary": "HU", "Ireland": "IE",
    "Italy": "IT", "Kosovo": "XK", "Latvia": "LV", "Lithuania": "LT", "Luxembourg": "LU", "Moldova": "MD",
    "Montenegro": "ME", "Netherlands": "NL", "North Macedonia": "MK", "Norway": "NO", "Poland": "PL", "Portugal": "PT",
    "Romania": "RO", "Russia": "RU", "Serbia": "RS", "Slovakia": "SK", "Slovenia": "SI", "Spain": "ES", "Sweden": "SE",
    "Switzerland": "CH", "Ukraine": "UA", "United Kingdom": "GB", "Türkiye": "TR", "Turkey": "TR", "Georgia": "GE",
    "Azerbaijan": "AZ", "Kazakhstan": "KZ", "Uzbekistan": "UZ",
    "Iran": "IR", "Iraq": "IQ", "Israel": "IL", "Jordan": "JO", "Kuwait": "KW", "Lebanon": "LB", "Oman": "OM",
    "Qatar": "QA", "Saudi Arabia": "SA", "Syria": "SY", "United Arab Emirates": "AE", "Bahrain": "BH", "Yemen": "YE",
    "Egypt": "EG", "Libya": "LY", "Tunisia": "TN", "Algeria": "DZ", "Morocco": "MA", "Sudan": "SD",
}
STATI = {"operating": "in esercizio", "construction": "in costruzione", "pre-construction": "pre-costruzione",
         "announced": "annunciata", "mothballed": "ferma (in riserva)", "retired": "dismessa", "shelved": "sospesa",
         "cancelled": "cancellata"}
ORDINE = ["operating", "construction", "mothballed", "pre-construction", "announced", "shelved", "retired", "cancelled"]

ZAPORIZHZHIA = {
    "stato_attuale": "occupata dalla Russia dal marzo 2022; 6 reattori (6 x 1.000 MW) in arresto, nessuna produzione dal settembre 2022",
    "eventi": [
        {"data": "2026-08-20", "fatto": "Persa l'ultima linea esterna per attivita' militare: 26a perdita totale di alimentazione esterna secondo l'IAEA; raffreddamento con generatori diesel, circa 10 giorni di gasolio al 28 agosto",
         "fonte": "ANS Nuclear Newswire (citando l'IAEA)", "link": "https://www.ans.org/news/2026-09-09/article-8377/zaporizhzhia-restores-offsite-power-following-iaeabrokered-local-ceasefire/"},
        {"data": "2026-09-09", "fatto": "Alimentazione esterna ripristinata sulla linea 330 kV Ferosplavna-1 grazie al settimo cessate il fuoco locale mediato dall'IAEA",
         "fonte": "ANS Nuclear Newswire", "link": "https://www.ans.org/news/2026-09-09/article-8377/zaporizhzhia-restores-offsite-power-following-iaeabrokered-local-ceasefire/"},
        {"data": "2026-10-23", "fatto": "Secondo l'IAEA la linea principale 750 kV Dniprovska resta fuori servizio",
         "fonte": "The Moscow Times (citando l'IAEA)", "link": "https://www.themoscowtimes.com/2026/11/08/zaporizhzhia-nuclear-plant-relying-on-generators-again-after-losing-internal-power-supply-a94202"},
        {"data": "2026-11-08", "fatto": "Disconnessa anche la linea Ferosplavna: centrale di nuovo con i generatori diesel, gasolio per circa due settimane secondo l'IAEA; causa non nota",
         "fonte": "The Moscow Times (Reuters, IAEA)", "link": "https://www.themoscowtimes.com/2026/11/08/zaporizhzhia-nuclear-plant-relying-on-generators-again-after-losing-internal-power-supply-a94202"},
    ],
    "affidabilita": "alta",
}


def costruisci_nucleare():
    cfg = get(GEM_CONFIG, timeout=60).decode("utf8", "replace")
    m = re.search(r"(?:geojson|csv)\s*:\s*['\"]([^'\"]+)['\"]", cfg)
    if not m:
        raise RuntimeError("indirizzo del geojson GEM non trovato in config.js")
    url = m.group(1)
    data_file = (re.search(r"(\d{4}-\d{2})", url) or [None, ""])[1]
    gj = json.loads(get(url, timeout=180))
    impianti = {}
    for f in gj.get("features", []):
        p = f.get("properties", {})
        paese = PAESI.get(p.get("country-area1") or p.get("all-countries") or "")
        if not paese:
            continue
        st = p.get("status") or ""
        if st == "cancelled":
            continue
        pid = p.get("project-id") or p.get("name")
        try:
            lat, lon = float(p.get("Latitude")), float(p.get("Longitude"))
        except (TypeError, ValueError):
            continue
        cap = p.get("capacity")
        try:
            cap = float(cap)
        except (TypeError, ValueError):
            cap = None
        imp = impianti.setdefault(pid, {"nome": p.get("name"), "paese": paese, "lat": round(lat, 4), "lon": round(lon, 4),
                                        "regione": p.get("subnational", ""), "operatore": p.get("operator", ""),
                                        "precisione": p.get("location-accuracy", ""), "link": p.get("url", ""),
                                        "unita": {}, "reattori": set()})
        u = imp["unita"].setdefault(st, {"n": 0, "mw": 0.0})
        u["n"] += 1
        u["mw"] += cap or 0
        if p.get("reactor-type") and p.get("reactor-type") != "unknown":
            imp["reattori"].add(p.get("reactor-type"))
    elementi = []
    for pid, imp in impianti.items():
        stati = sorted(imp["unita"], key=lambda s: ORDINE.index(s) if s in ORDINE else 99)
        if not stati:
            continue
        principale = stati[0]
        mw_es = imp["unita"].get("operating", {}).get("mw", 0)
        mw_cos = imp["unita"].get("construction", {}).get("mw", 0)
        composizione = "; ".join("%d unita' %s (%s MW)" % (imp["unita"][s]["n"], STATI.get(s, s), format(int(imp["unita"][s]["mw"]), ",").replace(",", "."))
                                 for s in stati)
        e = {"id": "EL-NU-" + pid, "nome": imp["nome"], "paese": imp["paese"], "lat": imp["lat"], "lon": imp["lon"],
             "categoria": "centrale-nucleare", "stato": STATI.get(principale, principale), "gem_stato": principale,
             "mw_esercizio": int(mw_es), "mw_costruzione": int(mw_cos),
             "mw_totale_attivo": int(sum(imp["unita"][s]["mw"] for s in stati if s not in ("retired", "shelved"))),
             "unita": composizione, "reattori": ", ".join(sorted(imp["reattori"])), "operatore": imp["operatore"],
             "regione": imp["regione"], "fonte": "Global Energy Monitor, Global Nuclear Power Tracker",
             "link": imp["link"] or "https://globalenergymonitor.org/projects/global-nuclear-power-tracker/",
             "data_fonte": data_file, "affidabilita": "alta" if imp["precisione"] == "exact" else "media",
             "note": "Posizione %s secondo GEM." % (imp["precisione"] or "non indicata")}
        if "Zaporizhzhia" in (imp["nome"] or ""):
            e.update({"stato": "occupata, reattori in arresto", "stato_attuale": ZAPORIZHZHIA["stato_attuale"],
                      "eventi": ZAPORIZHZHIA["eventi"], "data_fonte": "2026-11-08",
                      "note": "GEM classifica le unita' come 'operating' (capacita' installata, non produzione). Stato reale dai bollettini IAEA riportati negli eventi."})
        elementi.append(e)
    elementi.sort(key=lambda e: (e["paese"], -e["mw_totale_attivo"]))
    return elementi, url, data_file


# ---------------------------------------------------------------- scrittura
def scrivi(nome, obj):
    path = os.path.join(OUT, nome)
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    with open(path, "w", encoding="utf8") as f:
        f.write(s)
    log("scritto %s: %.2f MB" % (path, len(s.encode()) / 1e6))
    return len(s.encode())


def vecchio(nome):
    try:
        with open(os.path.join(OUT, nome), encoding="utf8") as f:
            return json.load(f)
    except Exception:
        return None


def main():
    os.makedirs(OUT, exist_ok=True)

    # --- PyPSA-Eur (serve per interconnessioni e come riserva)
    pypsa_info, pypsa_tab, pypsa_links = None, {}, []
    try:
        pypsa_info, pypsa_tab = zenodo_pypsa()
        csv.field_size_limit(10 ** 9)
        pypsa_links = list(csv.DictReader(io.StringIO(pypsa_tab.get("links.csv", ""))))
        log("PyPSA-Eur versione %s del %s" % (pypsa_info["versione"], pypsa_info["data"]))
    except Exception as e:
        errori["rete"].append("Zenodo PyPSA-Eur non scaricato: %s" % str(e)[:120])

    # --- 1. rete
    fonti_rete, feats, subs, metodo = [], None, [], None
    if os.environ.get("ELETTRICITA_OVERPASS", "0") == "1" and prova_overpass():
        feats = rete_overpass()
        metodo = "overpass"
        fonti_rete.append({"nome": "OpenStreetMap via Overpass API", "link": "https://overpass-api.de/",
                           "licenza": "ODbL 1.0 (© OpenStreetMap contributors)", "data_dato": OGGI.strftime("%Y-%m-%d")})
    try:
        f2, subs = rete_oim()
        if not feats:
            feats, metodo = f2, "openinframap"
            fonti_rete.append({"nome": "OpenStreetMap via tessere vettoriali OpenInfraMap (zoom %d)" % ZOOM,
                               "link": "https://openinframap.org/", "licenza": "ODbL 1.0 (© OpenStreetMap contributors, OpenInfraMap)",
                               "data_dato": OGGI.strftime("%Y-%m-%d")})
    except Exception as e:
        errori["rete"].append("OpenInfraMap non disponibile: %s" % str(e)[:120])
    if not feats and pypsa_tab:
        feats, metodo = rete_da_pypsa(pypsa_tab), "pypsa"
        fonti_rete.append({"nome": "PyPSA-Eur Prebuilt Electricity Network (OpenStreetMap), v%s" % pypsa_info["versione"],
                           "link": pypsa_info["link"], "licenza": "ODbL 1.0", "data_dato": pypsa_info["data"]})
    if feats:
        tol = 0.012
        for _ in range(4):
            elementi = costruisci_rete(feats, tol)
            obj = {"aggiornato": AGG, "fonti": fonti_rete,
                   "nota": ("Linee elettriche con tensione >= 380 kV ed elettrodotti in corrente continua (HVDC, frequency=0) di ogni tensione, "
                            "riquadro lon %g..%g lat %g..%g (Europa, Ucraina, Russia europea, Turchia, Medio Oriente, Nord Africa). "
                            "Metodo: %s. Tratti dello stesso nome/tensione/operatore uniti e semplificati (Douglas-Peucker %.3f gradi), "
                            "coordinate a 3 decimali: il tracciato e' indicativo. km_mappa = lunghezza della geometria semplificata. "
                            "Copertura OSM disomogenea (buona in Europa e Turchia, piu' scarsa in Russia e in parte del Medio Oriente)."
                            ) % (LON_MIN, LON_MAX, LAT_MIN, LAT_MAX, metodo, tol),
                   "elementi": elementi, "errori": errori["rete"]}
            size = len(json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode())
            if size < 1.8e6:
                break
            tol *= 1.6
        scrivi("rete-elettrica.json", obj)
        log("rete: %d elementi, HVDC %d" % (len(elementi), sum(e["hvdc"] for e in elementi)))
    else:
        old = vecchio("rete-elettrica.json")
        if old:
            old["errori"] = errori["rete"] + ["nessuna fonte disponibile: mantenuto il file precedente"]
            scrivi("rete-elettrica.json", old)

    # --- 2. interconnessioni
    inter = costruisci_interconnessioni(pypsa_links, subs)
    fonti_ic = [{"nome": "Schede curate a mano (Terna, ENTSO-E, Wikipedia, stampa specializzata): fonte per voce", "link": "",
                 "licenza": "fatti con citazione; coordinate Wikipedia CC BY-SA", "data_dato": "2026-11-09"}]
    if pypsa_info:
        fonti_ic.append({"nome": "PyPSA-Eur Prebuilt Electricity Network v%s (tracciati e MW HVDC da OSM)" % pypsa_info["versione"],
                         "link": pypsa_info["link"], "licenza": "ODbL 1.0", "data_dato": pypsa_info["data"]})
    if subs:
        fonti_ic.append({"nome": "Sottostazioni OpenStreetMap (tessere OpenInfraMap)", "link": "https://openinframap.org/",
                         "licenza": "ODbL 1.0", "data_dato": OGGI.strftime("%Y-%m-%d")})
    scrivi("interconnessioni.json", {
        "aggiornato": AGG, "fonti": fonti_ic,
        "nota": "Interconnessioni elettriche strategiche. mw = capacita' nominale dichiarata dalla fonte della voce; mw_pypsa = somma dei collegamenti HVDC nel dataset PyPSA-Eur/OSM (controllo). "
                "g = tracciato OSM se disponibile, altrimenti retta tra i terminali (campo tracciato lo dice). Stati verificati al 2026-11-09 dove indicato.",
        "elementi": inter, "errori": errori["inter"]})

    # --- 3. nucleare
    try:
        nuc, url, data_file = costruisci_nucleare()
        scrivi("nucleare.json", {
            "aggiornato": AGG,
            "fonti": [{"nome": "Global Energy Monitor, Global Nuclear Power Tracker (file della mappa pubblica)", "link": url,
                       "licenza": "CC BY 4.0", "data_dato": data_file},
                      {"nome": "IAEA tramite ANS Nuclear Newswire e The Moscow Times (solo Zaporizhzhia)",
                       "link": "https://www.ans.org/news/2026-09-09/article-8377/zaporizhzhia-restores-offsite-power-following-iaeabrokered-local-ceasefire/",
                       "licenza": "citazione di fatti", "data_dato": "2026-11-08"}],
            "nota": "Una voce per centrale (progetto GEM), unita' raggruppate per stato; escluse le unita' cancellate. stato = stato prevalente "
                    "(ordine: in esercizio, in costruzione, in riserva, pre-costruzione, annunciata, sospesa, dismessa). "
                    "Paesi: Europa, Ucraina, Russia (anche asiatica), Bielorussia, Armenia, Turchia, Caucaso, Medio Oriente, Nord Africa.",
            "elementi": nuc, "errori": errori["nucleare"]})
        log("nucleare: %d centrali" % len(nuc))
    except Exception as e:
        errori["nucleare"].append("GEM nucleare non scaricato: %s" % str(e)[:150])
        old = vecchio("nucleare.json")
        if old:
            old["errori"] = errori["nucleare"]
            scrivi("nucleare.json", old)
        log("ERRORE nucleare:", e)
    log("errori:", json.dumps(errori, ensure_ascii=False)[:1500])


if __name__ == "__main__":
    main()
