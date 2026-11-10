#!/usr/bin/env python3
"""Naval deployments for the "Ships" layer: rebuilds docs/data/mobili.json.

Standard library only. Steps:
  1. read the current docs/data/mobili.json (the base);
  2. keep every non-ship item (aircraft, mobile air defence, ...) unchanged;
  3. keep the existing ship items, refreshed from the latest USNI News
     "Fleet and Marine Tracker" when the tracker is newer than the item;
  4. add US ships named in the tracker that are not yet in the file (ids NU-...);
  5. add the curated items of raccolta/mobili/navi_curate.json (ids NV-...);
  6. validate (schema, dates, coordinates, symbol inside its circle, symbol at sea)
     and write the file in the same schema: {"aggiornato", "schema", "punti"}.

Positions are area-level: lat/lon is the centre of the area named by the source,
precisione_km its radius, 'sim' only where the symbol sits inside the circle.
If USNI cannot be reached the script keeps the existing items and still writes
the curated ones. Usage: python3 raccolta/mobili/raccogli.py [--secco] (dry run).
"""
import datetime as dt
import hashlib
import html
import json
import math
import os
import re
import sys
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.normpath(os.path.join(QUI, "..", ".."))
USCITA = os.path.join(RADICE, "docs", "data", "mobili.json")
CURATE = os.path.join(QUI, "navi_curate.json")
MONDO = os.path.join(RADICE, "docs", "data", "world.json")
UA = "Mozilla/5.0 (compatible; monitor-geoeconomico/1.0; open-data research)"
SCHEMA_DEFAULT = "regole/02_schema-dati.md v2.1 + extra di mappa"
NAVE = re.compile(r"^(nave|sottomarino)")
CATEGORIE_NAVE = {"nave-portaerei", "nave-anfibia", "nave-scorta", "sottomarino", "nave-ausiliaria"}
SAGOME = {"portaerei", "anfibia", "lpd", "incrociatore", "caccia", "fregata", "rifornitore", "sottomarino"}
TEATRI = {"MO", "RU-UA", "IT", "NATO", "ALTRO"}
ORDINE = ["id", "classe", "categoria", "nome", "identificativo", "appartenenza", "stato", "data_evento", "ora_utc",
          "lat", "lon", "origine_coord", "precisione_km", "teatro", "paese", "regione", "attore", "bersaglio", "mezzo",
          "esito", "fonte", "link", "data_fonte", "affidabilita", "note", "fonti", "sagoma", "breve", "dettaglio",
          "ids", "gruppo", "capo", "sim", "storico", "dubbia", "sempre"]
PREFISSI = ("USNS", "USS", "HMS", "RFA", "JS", "INS", "HMAS", "HMCS", "ROKS", "HDMS", "FGS", "FS", "NRP", "LNS",
            "ORP", "FNS", "HS", "ESPS", "ITS", "TCG", "BNS", "KNM", "HNLMS", "HNoMS", "CNS", "RFS")

# ---------------------------------------------------------------- USNI areas
# Centre of the area named in a tracker heading or sentence (NOT a ship position), radius in km, theatre.
AREE = {
    "arabian sea": (16.0, 62.0, 800, "MO"), "red sea": (20.5, 38.5, 800, "MO"), "gulf of aden": (12.5, 47.5, 400, "MO"),
    "gulf of oman": (24.5, 58.8, 250, "MO"), "persian gulf": (27.0, 51.5, 400, "MO"), "arabian gulf": (27.0, 51.5, 400, "MO"),
    "north arabian sea": (21.0, 63.0, 500, "MO"), "middle east": (16.0, 62.0, 1000, "MO"),
    "mediterranean sea": (35.0, 18.0, 1200, "NATO"), "eastern mediterranean": (34.0, 30.0, 500, "NATO"),
    "western mediterranean": (38.5, 5.0, 500, "NATO"), "black sea": (43.0, 34.0, 400, "RU-UA"),
    "baltic sea": (57.0, 19.0, 500, "NATO"), "north sea": (56.0, 3.0, 500, "NATO"), "norwegian sea": (67.0, 4.0, 500, "NATO"),
    "north atlantic": (50.0, -30.0, 1500, "NATO"), "eastern atlantic": (40.0, -15.0, 1000, "NATO"),
    "atlantic": (35.0, -45.0, 2000, "NATO"), "western atlantic": (35.2, -72.5, 800, "ALTRO"),
    "caribbean sea": (15.0, -75.0, 900, "ALTRO"), "central caribbean": (15.0, -75.0, 700, "ALTRO"),
    "eastern pacific": (25.0, -125.0, 2000, "ALTRO"), "pacific ocean": (20.0, -160.0, 2500, "ALTRO"),
    "western pacific": (20.0, 135.0, 1500, "ALTRO"), "philippine sea": (20.0, 130.0, 800, "ALTRO"),
    "south china sea": (12.0, 114.0, 800, "ALTRO"), "east china sea": (29.0, 125.0, 500, "ALTRO"),
    "sea of japan": (40.0, 135.0, 600, "ALTRO"), "indian ocean": (-5.0, 75.0, 2000, "ALTRO"),
    "andaman sea": (9.5, 96.0, 400, "ALTRO"), "laccadive sea": (10.0, 73.5, 500, "MO"), "bay of bengal": (15.0, 88.0, 600, "ALTRO"),
    "strait of malacca": (3.2, 100.6, 250, "ALTRO"), "malacca strait": (3.2, 100.6, 250, "ALTRO"),
    "gulf of mexico": (25.0, -90.0, 700, "ALTRO"), "arctic": (75.0, 10.0, 1000, "NATO"),
}
# Ports: (lat, lon, country). Precision 3 km.
PORTI = {
    "sasebo": (33.16, 129.713, "JP"), "yokosuka": (35.29, 139.67, "JP"), "norfolk": (36.946, -76.33, "US"),
    "bremerton": (47.555, -122.635, "US"), "san diego": (32.705, -117.19, "US"), "singapore": (1.33, 104.02, "SG"),
    "pearl harbor": (21.35, -157.95, "US"), "mayport": (30.39, -81.41, "US"), "rota": (36.62, -6.33, "ES"),
    "bahrain": (26.21, 50.61, "BH"), "manama": (26.21, 50.61, "BH"), "souda bay": (35.49, 24.08, "GR"),
    "guam": (13.44, 144.65, "US"), "apra harbor": (13.44, 144.65, "US"), "everett": (47.99, -122.22, "US"),
    "busan": (35.10, 129.04, "KR"), "duqm": (19.67, 57.70, "OM"), "djibouti": (11.60, 43.14, "DJ"),
    "naples": (40.84, 14.26, "IT"), "augusta": (37.20, 15.22, "IT"), "split": (43.50, 16.43, "HR"),
    "gibraltar": (36.14, -5.36, "GB"), "portsmouth": (50.80, -1.11, "GB"), "newport news": (36.985, -76.43, "US"),
    "north island": (32.70, -117.17, "US"), "kitsap": (47.56, -122.64, "US"), "jebel ali": (25.01, 55.06, "AE"),
    "changi": (1.33, 104.02, "SG"), "subic bay": (14.80, 120.28, "PH"), "manila": (14.58, 120.96, "PH"),
    "darwin": (-12.43, 130.87, "AU"), "stirling": (-32.24, 115.69, "AU"), "okinawa": (26.33, 127.80, "JP"),
}
PORTO_RE = re.compile(r"(?:is in port (?:in|at)|in port (?:in|at)|arrived \w+ (?:in|at)|returned \w+ to|returned (?:home )?to|"
                      r"pulled in(?:to)? (?:to )?|docked (?:in|into|at)|moored (?:in|at))\s+(?:Naval Station |Naval Base |"
                      r"Commander,? Fleet Activities |Naval Support Activity |NS |HMAS )?([A-Z][A-Za-z .]+)")
SCAFO_RE = re.compile(r"\b(USS|USNS)\s+([A-Z][^()]{1,45}?)\s*\(((?:T-)?[A-Z]{2,4}-\d{1,3})\)")
CLASSI = [(r"^CVN-(6[89]|7\d)$", "Nimitz class"), (r"^CVN-(78|79|8\d)$", "Gerald R. Ford class"),
          (r"^DDG-(5[1-9]|[6-9]\d|1[0-4]\d)$", "Arleigh Burke class"), (r"^DDG-10\d{2}$", "Zumwalt class"),
          (r"^CG-", "Ticonderoga class"), (r"^LHD-", "Wasp class"), (r"^LHA-", "America class"),
          (r"^LPD-", "San Antonio class"), (r"^LSD-4[1-9]|^LSD-5", "Whidbey Island / Harpers Ferry class"),
          (r"^SSN-7[5-9]\d", "Virginia / Los Angeles class"), (r"^ESB-", "Lewis B. Puller-class expeditionary sea base"),
          (r"^T-AO-", "Henry J. Kaiser / John Lewis class"), (r"^T-AKE-", "Lewis and Clark class"),
          (r"^T-EPF-", "Spearhead-class expeditionary fast transport")]
MESI = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def log(*a):
    print("[mobili]", *a, file=sys.stderr)


def get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json,text/html"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def km(a_lat, a_lon, b_lat, b_lon):
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dl = math.radians(b_lon - a_lon)
    c = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    return 6371.0 * math.acos(max(-1.0, min(1.0, c)))


def breve_da(nome):
    parti = nome.split(" ", 1)
    return parti[1] if len(parti) == 2 and parti[0] in PREFISSI else nome


def norm_hull(s):
    return re.sub(r"\s+", "", (s or "")).upper()


# ---------------------------------------------------------------- land mask (world.json, TopoJSON)
class Terra:
    def __init__(self, path):
        self.anelli = []
        try:
            topo = json.load(open(path, encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            log("land mask not available:", e)
            return
        sx, sy = topo["transform"]["scale"]
        tx, ty = topo["transform"]["translate"]
        archi = []
        for arc in topo["arcs"]:
            x = y = 0
            pts = []
            for dx, dy in arc:
                x += dx
                y += dy
                pts.append((x * sx + tx, y * sy + ty))
            archi.append(pts)

        def anello(idx):
            out = []
            for i in idx:
                pts = archi[i] if i >= 0 else archi[~i][::-1]
                out.extend(pts if not out else pts[1:])
            return out

        for g in topo["objects"]["land"]["geometries"]:
            polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"] if g["type"] == "MultiPolygon" else []
            for poly in polys:
                rings = [anello(r) for r in poly]
                for r in rings:
                    if len(r) > 2:
                        xs = [p[0] for p in r]
                        ys = [p[1] for p in r]
                        self.anelli.append((min(xs), max(xs), min(ys), max(ys), r))

    def a_terra(self, lat, lon):
        dentro = False
        for x0, x1, y0, y1, r in self.anelli:
            if not (x0 <= lon <= x1 and y0 <= lat <= y1):
                continue
            c = False
            j = len(r) - 1
            for i in range(len(r)):
                xi, yi = r[i]
                xj, yj = r[j]
                if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
                    c = not c
                j = i
            dentro ^= c
        return dentro


# ---------------------------------------------------------------- USNI Fleet and Marine Tracker
def data_usni(post):
    return post["date_gmt"][:10]


def area_titolo(titolo):
    h = re.sub(r"^in (the )?", "", titolo.lower()).strip()
    return h if h in AREE else None


def area_da_testo(testo, titolo, ereditata):
    """Area for a ship: a more specific area named in its sentence; else the heading area if the sentence names it;
    else the area of the capital ship named earlier in the section (USNI charts the capital ship); else the heading."""
    t = testo.lower()
    h = area_titolo(titolo)
    for k in sorted(AREE, key=len, reverse=True):
        if k in t and k != h:
            return k
    if h and h in t:
        return h
    return ereditata or h


def etichetta(area):
    return " ".join(w if w in ("of", "the", "and") else w.capitalize() for w in area.split())


def usni_tracker(errori):
    api = ("https://news.usni.org/wp-json/wp/v2/posts?search=%22fleet+and+marine+tracker%22&orderby=date"
           "&per_page=5&_fields=date_gmt,link,slug,title,content")
    try:
        posts = json.loads(get(api))
    except Exception as e:  # noqa: BLE001
        errori.append("USNI not reachable: %s" % e)
        return None
    posts = [p for p in posts if p.get("slug", "").startswith("usni-news-fleet-and-marine-tracker")]
    if not posts:
        errori.append("USNI: no Fleet and Marine Tracker post found")
        return None
    post = max(posts, key=data_usni)
    c = post["content"]["rendered"]
    c = re.sub(r"(?s)<figure.*?</figure>", " ", c)              # photo captions name ships elsewhere
    sezioni = re.split(r"(?s)<h2[^>]*>(.*?)</h2>", c)
    navi = {}
    for i in range(1, len(sezioni) - 1, 2):
        titolo = html.unescape(re.sub(r"<[^>]+>", "", sezioni[i])).strip()
        corpo = sezioni[i + 1]
        generico = False
        ereditata = None
        for par in re.findall(r"(?s)<(?:p|li)[^>]*>(.*?)</(?:p|li)>", corpo):
            testo = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", par))).strip()
            testo = re.sub(r"\s+([,.)])", r"\1", testo)
            if "in the region include" in testo:
                generico = True
            for m in SCAFO_RE.finditer(testo):
                pref, nome, scafo = m.group(1), re.sub(r"\s+", " ", m.group(2)).strip(" ,"), m.group(3)
                if scafo in navi:
                    continue
                porto = None
                mp = PORTO_RE.search(testo)
                if mp and not ("departed" in testo and "returned" not in testo):
                    luogo = mp.group(1).lower()
                    porto = next((k for k in sorted(PORTI, key=len, reverse=True) if luogo.startswith(k)), None)
                area = area_da_testo(testo, titolo, ereditata)
                if area and area != area_titolo(titolo) and not porto and not generico:
                    ereditata = area
                navi[scafo] = {"nome": "%s %s" % (pref, nome), "scafo": scafo, "titolo": titolo, "porto": porto,
                               "area": area, "generico": generico and not porto, "frase": testo[:300]}
    titolo_post = html.unescape(re.sub(r"<[^>]+>", "", post["title"]["rendered"]))
    log("USNI: %s, %d hulls" % (titolo_post, len(navi)))
    return {"data": data_usni(post), "link": post["link"], "titolo": titolo_post, "navi": navi}


def posizione_usni(n, data_txt):
    """(lat, lon, precisione_km, regione, teatro, paese) for a tracker entry, or None."""
    d = dt.date.fromisoformat(data_txt)
    quando = "%d %s" % (d.day, d.strftime("%b"))
    if n["porto"]:
        lat, lon, paese = PORTI[n["porto"]]
        teatro = "MO" if paese in ("BH", "AE", "OM", "DJ") else "NATO" if paese in ("ES", "IT", "GR", "GB", "HR") else "ALTRO"
        return lat, lon, 3, "%s (USNI, %s)" % (etichetta(n["porto"]), quando), teatro, paese
    if not n["area"]:
        return None
    lat, lon, prec, teatro = AREE[n["area"]]
    if n["generico"]:
        return lat, lon, max(prec, 1000), "%s region, sea not specified (USNI, %s)" % (n["titolo"].replace("In the ", ""), quando), teatro, ""
    return lat, lon, prec, "%s (USNI, %s)" % (etichetta(n["area"]), quando), teatro, ""


def tipo_da_scafo(scafo):
    s = scafo.upper()
    if s.startswith("CVN"):
        return "nave-portaerei", "portaerei"
    if s.startswith(("LHD", "LHA")):
        return "nave-anfibia", "anfibia"
    if s.startswith(("LPD", "LSD")):
        return "nave-anfibia", "lpd"
    if s.startswith("CG"):
        return "nave-scorta", "incrociatore"
    if s.startswith(("DDG", "DD-")):
        return "nave-scorta", "caccia"
    if s.startswith(("LCS", "FFG")):
        return "nave-scorta", "fregata"
    if s.startswith(("SSN", "SSGN", "SSBN")):
        return "sottomarino", "sottomarino"
    return "nave-ausiliaria", "rifornitore"


def dettaglio_da_scafo(scafo):
    if scafo.startswith("LCS-"):
        n = int(scafo.split("-")[1])
        return "Freedom-class littoral combat ship" if n % 2 else "Independence-class littoral combat ship"
    for rx, txt in CLASSI:
        if re.search(rx, scafo):
            return txt
    return ""


def fonte_usni(tr):
    d = dt.date.fromisoformat(tr["data"])
    return {"fonte": "USNI News, Fleet and Marine Tracker of %d %s %d" % (d.day, d.strftime("%B"), d.year),
            "link": tr["link"], "data_fonte": tr["data"]}


def applica_usni(navi, tr, errori):
    """Refresh existing ship items from the tracker; return new NU- items."""
    if not tr:
        return []
    per_scafo = {}
    for p in navi:
        if p.get("appartenenza") == "US" and p.get("identificativo"):
            per_scafo.setdefault(norm_hull(p["identificativo"]), p)
    nuovi = []
    fu = fonte_usni(tr)
    for scafo, n in tr["navi"].items():
        pos = posizione_usni(n, tr["data"])
        if not pos:
            errori.append("USNI: no known area for %s (%s, heading '%s')" % (n["nome"], scafo, n["titolo"]))
            continue
        lat, lon, prec, regione, teatro, paese = pos
        p = per_scafo.get(norm_hull(scafo))
        if p and not p["id"].startswith("NU-"):
            if tr["data"] <= p.get("data_evento", ""):
                continue
            spostata = km(p["lat"], p["lon"], lat, lon) > 150 or (prec <= 3) != (p.get("precisione_km", 0) <= 3)
            if spostata:
                p.setdefault("storico", []).insert(0, {
                    "data_evento": p["data_evento"], "lat": p["lat"], "lon": p["lon"],
                    "origine_coord": p.get("origine_coord", "stimata"), "precisione_km": p["precisione_km"],
                    "affidabilita": p.get("affidabilita", "media"), "nota": p.get("regione", "")})
                p.update({"lat": lat, "lon": lon, "precisione_km": prec, "regione": regione, "teatro": teatro, "paese": paese})
                p.pop("sim", None)
            p.update({"data_evento": tr["data"], "fonte": fu["fonte"], "link": fu["link"], "data_fonte": fu["data_fonte"]})
            if not any(f.get("link") == fu["link"] for f in p.get("fonti", [])):
                p.setdefault("fonti", []).insert(0, fu)
            frase = "[USNI %s] %s" % (tr["data"], n["frase"])
            note = re.sub(r"\s*\[USNI \d{4}-\d{2}-\d{2}\][^\[]*$", "", p.get("note", ""))
            p["note"] = (note + " " + frase).strip()
            continue
        cat, sag = tipo_da_scafo(scafo)
        nuovi.append({
            "id": "NU-" + scafo, "classe": "mobile", "categoria": cat, "nome": n["nome"], "identificativo": scafo,
            "appartenenza": "US", "stato": "operativo", "data_evento": tr["data"], "ora_utc": "",
            "lat": lat, "lon": lon, "origine_coord": "stimata", "precisione_km": prec, "teatro": teatro, "paese": paese,
            "regione": regione, "attore": "", "bersaglio": "", "mezzo": "", "esito": "",
            "fonte": fu["fonte"], "link": fu["link"], "data_fonte": fu["data_fonte"],
            "affidabilita": "alta" if prec <= 3 else "media",
            "note": "Listed by the USNI News Fleet and Marine Tracker of %s under '%s'. Area-level position: the circle is "
                    "the area named by USNI, not a ship fix. Source sentence: %s" % (tr["data"], n["titolo"], n["frase"]),
            "fonti": [fu], "sagoma": sag, "breve": breve_da(n["nome"]), "dettaglio": dettaglio_da_scafo(scafo)})
    return nuovi


# ---------------------------------------------------------------- curated items
def da_curata(c, rif):
    fonti = [dict(rif[k]) for k in c["src"]]
    p = {"id": c["id"], "classe": "mobile", "categoria": c["categoria"], "nome": c["nome"],
         "identificativo": c.get("identificativo", ""), "appartenenza": c["appartenenza"], "stato": c.get("stato", "operativo"),
         "data_evento": c["data_evento"], "ora_utc": c.get("ora_utc", ""), "lat": c["lat"], "lon": c["lon"],
         "origine_coord": c.get("origine_coord", "stimata"), "precisione_km": c["precisione_km"], "teatro": c["teatro"],
         "paese": c.get("paese", ""), "regione": c["regione"], "attore": "", "bersaglio": "", "mezzo": "", "esito": "",
         "fonte": fonti[0]["fonte"], "link": fonti[0]["link"], "data_fonte": fonti[0]["data_fonte"],
         "affidabilita": c["affidabilita"], "note": c["note"], "fonti": fonti, "sagoma": c.get("sagoma"),
         "breve": c.get("breve") or breve_da(c["nome"]), "dettaglio": c.get("dettaglio", "")}
    for k in ("gruppo", "capo", "sim", "dubbia", "sempre"):
        if k in c:
            p[k] = c[k]
    if not p["sagoma"]:
        p.pop("sagoma")
    return p


# ---------------------------------------------------------------- symbol placement and checks
def distribuisci(punti, terra):
    """Give a 'sim' to ships that share an area centre and have none, so symbols do not stack.
    Deterministic, inside the circle, at sea when the land mask is available."""
    occupati = {}
    for p in punti:
        if NAVE.match(p["categoria"]) and p.get("precisione_km", 0) > 10:
            key = (round(p["lat"], 2), round(p["lon"], 2))
            occupati.setdefault(key, []).append(p)
    for key, gruppo in occupati.items():
        liberi = [p for p in gruppo if "sim" not in p and p["id"].startswith(("NV-", "NU-"))]   # existing items untouched
        if len(gruppo) < 2 or not liberi:
            continue
        # the lead ship of a group (capo) or the first one stays on the centre
        resta = next((p for p in liberi if p.get("capo")), None)
        if resta is None and len(liberi) == len(gruppo) and not any(p.get("capo") for p in gruppo):
            resta = liberi[0]
        for p in liberi:
            if p is resta:
                continue
            r_deg = min(2.5, p["precisione_km"] / 111.0 * 0.45)
            h = int(hashlib.md5(p["id"].encode()).hexdigest(), 16)
            base = (h % 360) * math.pi / 180
            frac = 0.45 + (h >> 9) % 40 / 100.0
            for t in range(16):
                a = base + t * math.pi / 8
                lat = p["lat"] + r_deg * frac * math.sin(a)
                lon = p["lon"] + r_deg * frac * math.cos(a) / max(0.2, math.cos(math.radians(p["lat"])))
                if not terra.anelli or not terra.a_terra(lat, lon):
                    p["sim"] = [round(lat, 2), round(lon, 2)]
                    break


def valida(punti, terra, errori):
    oggi = dt.date.today()
    visti = set()
    avvisi = 0
    for p in punti:
        pid = p.get("id")
        if pid in visti:
            errori.append("duplicate id %s" % pid)
        visti.add(pid)
        if not NAVE.match(p.get("categoria", "")):
            continue
        for k in ("nome", "appartenenza", "data_evento", "lat", "lon", "precisione_km", "fonte", "link", "data_fonte",
                  "affidabilita", "teatro", "regione"):
            if p.get(k) in (None, ""):
                errori.append("%s: missing %s" % (pid, k))
        if p.get("categoria") not in CATEGORIE_NAVE:
            errori.append("%s: unknown category %s" % (pid, p.get("categoria")))
        if p.get("sagoma") and p["sagoma"] not in SAGOME:
            errori.append("%s: unknown silhouette %s" % (pid, p["sagoma"]))
        if p.get("teatro") not in TEATRI:
            errori.append("%s: unknown theatre %s" % (pid, p.get("teatro")))
        if p.get("affidabilita") not in ("alta", "media", "bassa"):
            errori.append("%s: affidabilita %s" % (pid, p.get("affidabilita")))
        try:
            d = dt.date.fromisoformat(p["data_evento"])
            if d > oggi + dt.timedelta(days=1):
                errori.append("%s: date in the future %s" % (pid, d))
        except Exception:  # noqa: BLE001
            errori.append("%s: bad date %s" % (pid, p.get("data_evento")))
        if not (isinstance(p.get("lat"), (int, float)) and -90 <= p["lat"] <= 90 and isinstance(p.get("lon"), (int, float)) and -180 <= p["lon"] <= 180):
            errori.append("%s: bad coordinates" % pid)
            continue
        if not str(p.get("link", "")).startswith("http"):
            errori.append("%s: link is not a URL" % pid)
        if "sim" in p:
            dist = km(p["lat"], p["lon"], p["sim"][0], p["sim"][1])
            if dist > max(p["precisione_km"], 5) * 1.05:
                log("WARNING %s: symbol %.0f km from the centre, radius %s km" % (pid, dist, p["precisione_km"]))
                avvisi += 1
        if terra.anelli and p["precisione_km"] > 10:
            s = p.get("sim") or [p["lat"], p["lon"]]
            if terra.a_terra(s[0], s[1]):
                log("WARNING %s (%s): symbol on land at %s" % (pid, p["nome"], s))
                avvisi += 1
    return avvisi


def ordina(p):
    return {k: p[k] for k in ORDINE if k in p} | {k: v for k, v in p.items() if k not in ORDINE}


# ---------------------------------------------------------------- main
def main():
    secco = "--secco" in sys.argv
    errori = []
    try:
        base = json.load(open(USCITA, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        log("base file not readable (%s): starting empty" % e)
        base = {"aggiornato": "", "schema": SCHEMA_DEFAULT, "punti": []}
    cur = json.load(open(CURATE, encoding="utf-8"))
    rif = cur["fonti_rif"]

    altri = [p for p in base.get("punti", []) if not NAVE.match(p.get("categoria", ""))]
    navi = [p for p in base.get("punti", []) if NAVE.match(p.get("categoria", "")) and not p["id"].startswith(("NV-", "NU-"))]
    nu_vecchi = {p["id"]: p for p in base.get("punti", []) if p["id"].startswith("NU-")}

    for c in cur.get("correzioni", []):
        p = next((q for q in navi if q["id"] == c["id"]), None)
        if p:
            p.update(c["campi"])
        else:
            log("correction for missing id %s skipped" % c["id"])

    tr = usni_tracker(errori)
    nuovi_nu = applica_usni(navi, tr, errori)
    ids_nu = {p["id"] for p in nuovi_nu}
    for pid, p in nu_vecchi.items():          # a ship that left the tracker keeps its last USNI item and ages out
        if pid not in ids_nu:
            nuovi_nu.append(p)

    esistenti = {(norm_hull(p.get("identificativo")), p.get("appartenenza")) for p in navi + nuovi_nu if p.get("identificativo")}
    curate = []
    for c in cur["elementi"]:
        key = (norm_hull(c.get("identificativo")), c["appartenenza"])
        if key[0] and key in esistenti:
            log("curated %s skipped: already in the file" % c["id"])
            continue
        curate.append(da_curata(c, rif))

    terra = Terra(MONDO)
    navi_tutte = navi + nuovi_nu + curate
    distribuisci(navi_tutte, terra)
    punti = [ordina(p) for p in navi_tutte] + altri
    avvisi = valida(punti, terra, errori)

    out = {"aggiornato": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
           "schema": base.get("schema", SCHEMA_DEFAULT), "punti": punti}
    from collections import Counter
    cnt = Counter(p["appartenenza"] for p in punti if NAVE.match(p["categoria"]))
    log("ships %d (existing %d, new from USNI %d, curated %d), other items kept %d; warnings %d; errors %d" % (
        len(navi_tutte), len(navi), len([p for p in nuovi_nu if p["id"] in ids_nu]), len(curate), len(altri), avvisi, len(errori)))
    log("by navy: " + ", ".join("%s %d" % kv for kv in cnt.most_common()))
    for e in errori:
        log("ERROR/NOTE:", e)
    if secco:
        log("dry run: nothing written")
        return 0
    tmp = USCITA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, USCITA)
    log("written %s (%d bytes)" % (USCITA, os.path.getsize(USCITA)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
