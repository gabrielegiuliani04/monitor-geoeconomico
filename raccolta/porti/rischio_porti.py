#!/usr/bin/env python3
"""Port Risk Index: a daily, transparent risk score for 39 ports (30 North Sea/Baltic + 9 Italian).

Reads only the JSON files already produced by the other collectors in docs/data/ (no network),
applies the rules in report/port-risk-method.md and writes docs/data/port-risk.json.
Score history for the 7-day trend is kept in raccolta/porti/history.json.

Standard library only. A missing file or field turns the indicator into "n/a" and the script
carries on: it must never fail in the daily workflow. Same conventions as raccolta/rischio/calcola.py
(probability 1-5 x impact 1-5, green/amber/red = 1/3/5, weights renormalised when data are missing).

Usage:  python3 raccolta/porti/rischio_porti.py             (reference date = today, UTC)
        python3 raccolta/porti/rischio_porti.py 2026-11-10  (explicit reference date)
"""
import datetime as dt
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
DATA = os.environ.get("PORT_RISK_DATA") or os.path.join(ROOT, "docs", "data")
OUTPUT = os.environ.get("PORT_RISK_OUTPUT") or os.path.join(DATA, "port-risk.json")
HISTORY = os.environ.get("PORT_RISK_HISTORY") or os.path.join(HERE, "history.json")
CHOKE_HISTORY = os.path.join(ROOT, "raccolta", "rischio", "storico.json")   # read-only: chokepoint scores of past days
METHOD_LINK = "report/port-risk-method.md"

# ---------------------------------------------------------------- general rules (see the method)
POINTS = {"green": 1, "amber": 3, "red": 5}
W_PROB = {"traffic": 0.30, "security": 0.30, "chokepoints": 0.25, "insurance": 0.15}
W_IMP = {"role": 0.45, "size": 0.30, "energy": 0.25}
GROUP_NAMES = {
    "traffic": "Is traffic falling?", "security": "Are there security events nearby?",
    "chokepoints": "Do its trades depend on a disrupted chokepoint?", "insurance": "Do war-risk underwriters list it?",
    "role": "How strategic is it?", "size": "How much cargo does it handle?", "energy": "How expensive is energy already?",
}
LEVELS = [(20, "critical"), (12, "high"), (6, "medium"), (0, "low")]
TREND_STEP = 1.0              # score change (1-25 scale) needed to call a trend rising/falling
SMALL_PORT = 3.0              # calls/day a year earlier: below this the 7-day comparison is too noisy
TRAFFIC_THRESHOLDS = {        # (amber, red) in % ; calibrated on the PortWatch series (see method, section 4)
    "yoy_big": (-20, -30), "yoy_small": (-30, -50), "mom_big": (-20, -30), "mom_small": (-35, -50)}
DISRUPTION = -50.0            # big port, 7-day calls <= -50% year on year: disruption in progress, P = 5
RADIUS_KM = 50
EVENT_PRECISION_MAX_KM = 60   # events geolocated more vaguely than this are not attributed to a port
WINDOW_RECENT = 90
WINDOW_YEAR = 365
NEWS_HOURS = 72
RU_IMPACT_CAP = 3.0           # viewpoint rule: impact is measured for Europe; EU trade with Russian ports is sanctioned

EXCLUDED_CATEGORIES = {"esercitazione", "rischieramento", "avanzamento", "falso-allarme", "spionaggio", "nato"}
JUDICIAL = ("condann", "arrest", "processo", "sentenza", "court", "convict")
VIOLENT = ("attacco", "sabotaggio", "droni-porto", "danno-cavo", "sabotaggio-condotte")
PORT_TARGET = re.compile(r"port|terminal|attacco-porto", re.I)
NEWS_KEYWORDS = re.compile(
    r"\b(strike|strikes|walkout|sciopero|scioperi|staking|strejke|strejk|closed|closure|chiuso|chiusura|blocked|blockade|"
    r"blocco|congestion|congestione|queue|waiting|attack|attacco|drone|droni|explosion|esplosione|fire|incendio|"
    r"collision|collisione|sabotage|sabotaggio|evacuat)\w*", re.I)

# Baltic ports: every ocean-going call passes the Danish straits (Øresund, Great Belt) or the Kiel Canal.
BALTIC = {"copenaghen-malmo", "danzica", "gdynia", "swinoujscie", "klaipeda", "riga", "ventspils", "tallinn", "helsinki",
          "hamina-kotka", "primorsk", "ust-luga", "san-pietroburgo", "kaliningrad", "skoldvik", "vysotsk", "paldiski",
          "inkoo", "rostock"}
# Italian container gateways named by the chokepoint file as the first European landfall of the Suez route.
SUEZ_FIRST_LANDFALL = {"genoa", "trieste", "gioia-tauro", "la-spezia"}

NAMES_EN = {
    "rotterdam": "Rotterdam", "anversa-bruges": "Antwerp-Bruges (Antwerp + Zeebrugge)", "amburgo": "Hamburg",
    "brema-bremerhaven": "Bremen / Bremerhaven", "wilhelmshaven": "Wilhelmshaven (JadeWeserPort)", "amsterdam": "Amsterdam",
    "eemshaven": "Eemshaven (Groningen Seaports)", "esbjerg": "Esbjerg", "aarhus": "Aarhus",
    "copenaghen-malmo": "Copenhagen-Malmö (CMP)", "goteborg": "Gothenburg", "danzica": "Gdańsk", "gdynia": "Gdynia",
    "swinoujscie": "Świnoujście (with Szczecin)", "klaipeda": "Klaipėda", "riga": "Riga", "ventspils": "Ventspils",
    "tallinn": "Tallinn (Muuga and Old City Harbour)", "helsinki": "Helsinki", "hamina-kotka": "HaminaKotka",
    "primorsk": "Primorsk", "ust-luga": "Ust-Luga", "san-pietroburgo": "St Petersburg (Big Port, with Bronka)",
    "kaliningrad": "Kaliningrad and Baltiysk", "skoldvik": "Sköldvik (Porvoo)", "vysotsk": "Vysotsk", "paldiski": "Paldiski",
    "inkoo": "Inkoo", "rostock": "Rostock", "brunsbuttel": "Brunsbüttel",
    "Genova": "Genoa", "Trieste": "Trieste", "Gioia Tauro": "Gioia Tauro", "La Spezia": "La Spezia", "Livorno": "Livorno",
    "Venezia (Lido)": "Venice (Lido entrance)", "Venezia (Malamocco)": "Venice (Malamocco entrance)", "Ravenna": "Ravenna",
    "Augusta": "Augusta",
}
IDS_EN = {"anversa-bruges": "antwerp-bruges", "amburgo": "hamburg", "brema-bremerhaven": "bremen-bremerhaven",
          "copenaghen-malmo": "copenhagen-malmo", "goteborg": "gothenburg", "danzica": "gdansk",
          "san-pietroburgo": "st-petersburg", "Genova": "genoa", "Trieste": "trieste", "Gioia Tauro": "gioia-tauro",
          "La Spezia": "la-spezia", "Livorno": "livorno", "Venezia (Lido)": "venice-lido",
          "Venezia (Malamocco)": "venice-malamocco", "Ravenna": "ravenna", "Augusta": "augusta"}
# name variants searched in the news headlines (English, Italian and local spellings)
ALIASES = {
    "rotterdam": ["Rotterdam"], "antwerp-bruges": ["Antwerp", "Anversa", "Antwerpen", "Zeebrugge"],
    "hamburg": ["Hamburg", "Amburgo"], "bremen-bremerhaven": ["Bremerhaven"], "wilhelmshaven": ["Wilhelmshaven"],
    "amsterdam": ["port of Amsterdam", "haven van Amsterdam", "porto di Amsterdam"], "eemshaven": ["Eemshaven"],
    "esbjerg": ["Esbjerg"], "aarhus": ["Aarhus"], "copenhagen-malmo": ["Copenhagen Malmö Port", "CMP"],
    "gothenburg": ["Gothenburg", "Göteborg"], "gdansk": ["Gdańsk", "Gdansk", "Danzica"], "gdynia": ["Gdynia"],
    "swinoujscie": ["Świnoujście", "Swinoujscie"], "klaipeda": ["Klaipėda", "Klaipeda"], "riga": ["port of Riga", "Riga port"],
    "ventspils": ["Ventspils"], "tallinn": ["Muuga", "port of Tallinn"], "helsinki": ["port of Helsinki"],
    "hamina-kotka": ["HaminaKotka", "Kotka", "Hamina"], "primorsk": ["Primorsk"], "ust-luga": ["Ust-Luga", "Ust Luga"],
    "st-petersburg": ["port of St Petersburg", "Bronka"], "kaliningrad": ["Kaliningrad", "Baltiysk"],
    "skoldvik": ["Sköldvik", "Porvoo"], "vysotsk": ["Vysotsk"], "paldiski": ["Paldiski"], "inkoo": ["Inkoo"],
    "rostock": ["Rostock"], "brunsbuttel": ["Brunsbüttel", "Brunsbuettel"],
    "genoa": ["porto di Genova", "port of Genoa", "Genoa port"], "trieste": ["porto di Trieste", "port of Trieste"],
    "gioia-tauro": ["Gioia Tauro"], "la-spezia": ["La Spezia"], "livorno": ["porto di Livorno", "port of Livorno"],
    "venice-lido": ["porto di Venezia", "port of Venice"], "venice-malamocco": ["Malamocco"],
    "ravenna": ["porto di Ravenna", "port of Ravenna"], "augusta": ["porto di Augusta", "Augusta"],
}
CHOKE_EN = {"hormuz": "Strait of Hormuz", "bab-el-mandeb": "Bab el-Mandeb", "suez": "Suez Canal",
            "stretti-danesi": "Danish straits", "baltico": "Baltic (cables, pipelines, power links)",
            "mar-rosso-container": "Red Sea (Asia–Europe container route)", "gnl-qatar": "Qatar LNG (Ras Laffan → Hormuz)",
            "stretti-turchi": "Turkish straits", "gibilterra": "Strait of Gibraltar", "canale-di-sicilia": "Sicily Channel"}
WIND_EN = {"installazione": "installation", "fabbricazione": "manufacturing", "O&M": "operations and maintenance"}
LNG_RADIUS_KM = 20
LNG_NATIONAL_MTPA = 5.0       # operating import capacity ≥ 5 Mt/yr (≈ 6.8 bcm/yr) counts as two strategic functions
EXTRA_LNG = {"anversa-bruges": "Zeebrugge LNG Terminal",   # Zeebrugge is part of the merged Port of Antwerp-Bruges
             "port655": "Toscana FSRU"}                     # OLT floating terminal moored offshore Livorno (28 km)
HUBS_EN = {"Anversa": "Antwerp", "Pireo": "Piraeus", "Gibilterra": "Gibraltar", "Amburgo": "Hamburg", "Danzica": "Gdańsk",
           "Genova": "Genoa", "Istanbul": "Istanbul"}
TYPE_NAMES = {"tanker": "tanker", "container": "container", "dry_bulk": "dry bulk", "general_cargo": "general cargo",
              "roro": "ro-ro"}

# ---------------------------------------------------------------- utilities
ERRORS = []
_CACHE = {}


def load(name):
    """docs/data/<name>; None (with an error noted) if missing or unreadable."""
    if name in _CACHE:
        return _CACHE[name]
    try:
        with open(os.path.join(DATA, name), encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        ERRORS.append(f"{name}: file missing, related indicators n/a")
        data = None
    except Exception as e:  # corrupt or half-written file
        ERRORS.append(f"{name}: unreadable ({e.__class__.__name__}), related indicators n/a")
        data = None
    _CACHE[name] = data
    return data


def file_date(name):
    d = load(name)
    return str((d or {}).get("aggiornato", "")) if isinstance(d, dict) else ""


def day(s):
    return dt.date.fromisoformat(str(s)[:10])


def km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def in_polygon(lon, lat, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def fmt(x, dec=1):
    return "n/a" if x is None else f"{x:,.{dec}f}"


def pct(x):
    return "n/a" if x is None else ("+" if x > 0 else "") + fmt(x) + "%"


def plural(n, one, many):
    return f"{n} {one if n == 1 else many}"


def short(t, n):
    t = str(t or "")
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0].rstrip(",;:(") + "…"


def classify(value, amber, red, direction):
    """direction='low_bad': lower is worse; 'high_bad': higher is worse."""
    if value is None:
        return "n/a"
    if direction == "low_bad":
        return "red" if value <= red else "amber" if value <= amber else "green"
    return "red" if value >= red else "amber" if value >= amber else "green"


def ind(name, group, value, unit, status, text, thresholds, source, date, file, note="", link="", kind="data", scored=True):
    return {"name": name, "group": group, "value": None if value is None else round(value, 2), "unit": unit,
            "status": status, "text": text, "thresholds": thresholds, "source": source, "link": link, "date": date,
            "file": file, "kind": kind, "scored": scored, "note": note}


def na(name, group, reason, source="", file=""):
    return ind(name, group, None, "", "n/a", "n/a", {}, source, "", file, reason, scored=False)


def cut(series, lag):
    """The series as it was 'lag' days ago (drops the last 'lag' days of data)."""
    series = [p for p in (series or []) if p and p[1] is not None]
    if not series or lag <= 0:
        return series
    limit = day(series[-1][0]) - dt.timedelta(days=lag)
    return [p for p in series if day(p[0]) <= limit]


def window_mean(daymap, end, days, offset=0):
    vals = [daymap.get(end - dt.timedelta(days=offset + k)) for k in range(days)]
    vals = [v for v in vals if v is not None]
    return (sum(vals) / len(vals)) if len(vals) >= max(1, int(days * 0.8)) else None


# ---------------------------------------------------------------- ports
def ports():
    out = []
    pn = load("porti-nord.json")
    for e in (pn or {}).get("elementi", []):
        out.append({"src": e, "source_id": e["id"], "id": IDS_EN.get(e["id"], e["id"]), "name": NAMES_EN.get(e["id"], e["nome"]),
                    "country": e.get("paese"), "lat": e.get("lat"), "lon": e.get("lon"), "file": "porti-nord.json",
                    "spec": " ; ".join(e.get("specializzazione") or []), "region": "north"})
    pw = load("portwatch.json")
    for e in (pw or {}).get("elementi", []):
        if e.get("tipo") == "porto" and e.get("paese") == "IT":
            out.append({"src": e, "source_id": e["id"], "id": IDS_EN.get(e["nome"], e["id"]), "name": NAMES_EN.get(e["nome"], e["nome"]),
                        "country": "IT", "lat": e.get("lat"), "lon": e.get("lon"), "file": "portwatch.json", "spec": "",
                        "region": "italy"})
    if not out:
        ERRORS.append("no port list available (porti-nord.json and portwatch.json missing)")
    return out


# ---------------------------------------------------------------- probability: traffic
PW_SOURCE = "IMF PortWatch (IMF and University of Oxford), AIS-based daily port calls"
PW_LINK = "https://portwatch.imf.org/"


def calls_daymap(p, lag):
    s = cut(((p["src"].get("serie") or {}).get("portcalls")), lag)
    return {day(d): v for d, v in s}, (day(s[-1][0]) if s else None)


def is_small(dm, end):
    """Small port: fewer than SMALL_PORT calls/day on average over the last 365 days (7-day comparisons too noisy)."""
    m = window_mean(dm, end, 365)
    return m is not None and m < SMALL_PORT


def i_calls_yoy(p, lag):
    name = "Port calls vs same period last year"
    dm, end = calls_daymap(p, lag)
    if not end:
        return na(name, "traffic", "no PortWatch call series", PW_SOURCE, p["file"])
    base7 = window_mean(dm, end, 7, 364)
    if base7 is None:
        return na(name, "traffic", "no data for the same week a year earlier", PW_SOURCE, p["file"])
    if not is_small(dm, end):
        now, base, win, (amb, red) = window_mean(dm, end, 7), base7, 7, TRAFFIC_THRESHOLDS["yoy_big"]
    else:
        now, base, win, (amb, red) = window_mean(dm, end, 28), window_mean(dm, end, 28, 364), 28, TRAFFIC_THRESHOLDS["yoy_small"]
    if now is None or not base:
        return na(name, "traffic", "window incomplete", PW_SOURCE, p["file"])
    var = (now / base - 1) * 100
    out = ind(f"Port calls, {win}-day mean vs a year earlier", "traffic", var, "% vs last year",
              classify(var, amb, red, "low_bad"),
              f"{fmt(now)} calls/day vs {fmt(base)} a year earlier: {pct(var)}",
              {"green": f"> {amb}%", "amber": f"{amb}% to {red}%", "red": f"≤ {red}%",
               "disruption": f"≤ {DISRUPTION:.0f}% on the 7-day mean (ports with ≥ {SMALL_PORT:.0f} calls/day): P = 5"},
              PW_SOURCE, end.isoformat(), p["file"],
              ("Small port (< 3 calls/day on average over 12 months): 28-day window to reduce noise. " if win == 28 else "")
              + "Counts only ships with AIS on; data arrive about a week late.", PW_LINK)
    out["disruption"] = win == 7 and var <= DISRUPTION
    out["now"], out["base"] = round(now, 1), round(base, 1)
    return out


def main_type(p):
    m = p["src"].get("media30") or {}
    types = {k.replace("portcalls_", ""): v for k, v in m.items() if k.startswith("portcalls_") and v is not None}
    if not types:
        return None, {}
    tot = sum(types.values()) or 1
    return max(types, key=types.get), {k: round(v / tot * 100) for k, v in types.items()}


def i_type_yoy(p):
    t, mix = main_type(p)
    name = "Main vessel type, 7-day calls vs a year earlier"
    if not t:
        return na(name, "traffic", "no vessel-type breakdown", PW_SOURCE, p["file"])
    var = (p["src"].get("var7_anno_pct") or {}).get("portcalls_" + t)
    now = (p["src"].get("media7") or {}).get("portcalls_" + t)
    base = (p["src"].get("media7_anno_prima") or {}).get("portcalls_" + t)
    if var is None or base is None:
        return na(f"{TYPE_NAMES.get(t, t).capitalize()} calls vs a year earlier", "traffic", "variation not available", PW_SOURCE, p["file"])
    amb, red = TRAFFIC_THRESHOLDS["yoy_big"]
    scored = base >= SMALL_PORT
    out = ind(f"{TYPE_NAMES.get(t, t).capitalize()} calls (main type, {mix.get(t)}% of calls), 7-day mean vs a year earlier",
              "traffic", var, "% vs last year", classify(var, amb, red, "low_bad"),
              f"{fmt(now)} vs {fmt(base)} calls/day: {pct(var)}",
              {"green": f"> {amb}%", "amber": f"{amb}% to {red}%", "red": f"≤ {red}%"},
              PW_SOURCE, p["src"].get("ultima_data", ""), p["file"],
              ("Shown but not scored: fewer than 3 calls/day of this type a year earlier, too noisy. " if not scored else "")
              + "Pre-computed by the PortWatch collector: in the reconstructed 7-day-ago score it stays the same.",
              PW_LINK, scored=scored)
    out["fixed"] = True
    out["mix_pct"] = mix
    return out


def i_momentum(p, lag):
    name = "Short-term disruption proxy: 7-day calls vs the previous 28 days"
    dm, end = calls_daymap(p, lag)
    if not end:
        return na(name, "traffic", "no PortWatch call series", PW_SOURCE, p["file"])
    now, prev = window_mean(dm, end, 7), window_mean(dm, end, 28, 7)
    if now is None or not prev:
        return na(name, "traffic", "window incomplete", PW_SOURCE, p["file"])
    amb, red = TRAFFIC_THRESHOLDS["mom_small" if is_small(dm, end) else "mom_big"]
    var = (now / prev - 1) * 100
    return ind(name, "traffic", var, "% vs previous 28 days", classify(var, amb, red, "low_bad"),
               f"{fmt(now)} calls/day vs {fmt(prev)} in the previous 28 days: {pct(var)}",
               {"green": f"> {amb}%", "amber": f"{amb}% to {red}%", "red": f"≤ {red}%"},
               PW_SOURCE, end.isoformat(), p["file"],
               "A sudden drop in calls is what congestion, strikes, closures or bad weather look like in AIS data; "
               "it cannot tell them apart from weaker demand. No free vessel-waiting-time source is in the repository.",
               PW_LINK)


# ---------------------------------------------------------------- probability: security
def collect_events(today):
    """All dated, geolocated security events, de-duplicated across files."""
    raw = []
    bs = load("baltico-sicurezza.json")
    for x in (bs or {}).get("eventi", []):
        raw.append((x.get("rif") or x.get("id"), x, "baltico-sicurezza.json", x.get("data")))
    for x in (load("ibrido.json") or {}).get("punti", []):
        raw.append((x.get("id"), x, "ibrido.json", x.get("data_evento")))
    for x in (load("eventi.json") or {}).get("punti", []):
        raw.append((x.get("id"), x, "eventi.json", x.get("data_evento") or x.get("data")))
    for x in (load("cavi-incidenti.json") or {}).get("elementi", []):
        raw.append((x.get("id"), x, "cavi-incidenti.json", x.get("data_evento")))
    seen, out = set(), []
    for key, x, f, d in raw:
        if key in seen:
            continue
        try:
            lat, lon = float(x.get("lat")), float(x.get("lon"))
            if len(str(d)) == 7:
                d = str(d) + "-01"   # month-only dates: first day of the month
            dd = day(d)
        except Exception:
            continue
        if dd > today:
            continue
        seen.add(key)
        out.append({**x, "_id": key, "_file": f, "_lat": lat, "_lon": lon, "_d": dd})
    return out


def eligible(e):
    if e.get("affidabilita") == "bassa" or e.get("categoria") in EXCLUDED_CATEGORIES:
        return False
    try:
        if float(e.get("precisione_km") or 0) > EVENT_PRECISION_MAX_KM:
            return False
    except (TypeError, ValueError):
        pass
    name = str(e.get("nome", "")).lower()
    if e["_file"] != "cavi-incidenti.json" and any(k in name for k in JUDICIAL):
        return False   # court outcome of a past event, not a new event on the ground
    return True


def near(events, p, today, days, radius=RADIUS_KM):
    since = today - dt.timedelta(days=days)
    return [e for e in events if since <= e["_d"] <= today and eligible(e)
            and km(p["lat"], p["lon"], e["_lat"], e["_lon"]) <= radius]


def coverage_start(events, files):
    ds = [e["_d"] for e in events if e["_file"] in files]
    return min(ds).isoformat() if ds else None


def i_events_recent(events, p, today, lag):
    name = f"Security events within {RADIUS_KM} km, last {WINDOW_RECENT} days"
    if not any(load(n) for n in ("baltico-sicurezza.json", "ibrido.json", "eventi.json", "cavi-incidenti.json")):
        return na(name, "security", "all event files missing", "", "baltico-sicurezza.json")
    ref = today - dt.timedelta(days=lag)
    sel = sorted(near(events, p, ref, WINDOW_RECENT), key=lambda e: e["_d"], reverse=True)
    n = len(sel)
    violent = [e for e in sel if any(str(e.get("categoria", "")).startswith(v) for v in VIOLENT)]
    status = "red" if n >= 2 or violent else "amber" if n == 1 else "green"
    text = plural(n, "event", "events") + ("" if not sel else ": " + "; ".join(
        f"{e['_d'].isoformat()} {short(e.get('breve') or e.get('nome'), 70)} ({e['_file']}, {e.get('affidabilita', '')})" for e in sel[:3]))
    start = coverage_start(events, {"ibrido.json", "eventi.json"})
    out = ind(name, "security", n, "events", status, text,
              {"green": "none", "amber": "1 event", "red": "2 or more, or any attack/sabotage/cable damage"},
              "Curated event files: baltico-sicurezza, ibrido, eventi, cavi-incidenti (agencies, authorities, OSINT; medium/high reliability)",
              ref.isoformat(), "baltico-sicurezza.json, ibrido.json, eventi.json, cavi-incidenti.json",
              f"Excluded: low reliability, exercises, false alarms, espionage arrests, court outcomes, points geolocated worse than "
              f"{EVENT_PRECISION_MAX_KM} km. The general event files only start on {start or 'n/a'}: outside the Baltic a "
              "low count can mean little collection.")
    out["ids"] = [e["_id"] for e in sel[:5]]
    out["port_attack_7d"] = [e.get("nome") for e in sel if e["_d"] >= ref - dt.timedelta(days=7)
                             and any(str(e.get("categoria", "")).startswith(v) for v in ("attacco", "sabotaggio"))
                             and PORT_TARGET.search(str(e.get("bersaglio", "")) + " " + str(e.get("categoria", "")))
                             and km(p["lat"], p["lon"], e["_lat"], e["_lon"]) <= 20]
    return out


def i_events_year(events, p, today, lag):
    name = f"Security events within {RADIUS_KM} km, last 12 months"
    if p["region"] != "north":
        return na(name, "security", "no 12-month security archive for the Mediterranean in the repository "
                                    "(baltico-sicurezza.json covers the North Sea and Baltic only)", "", "baltico-sicurezza.json")
    if not load("baltico-sicurezza.json"):
        return na(name, "security", "baltico-sicurezza.json missing", "", "baltico-sicurezza.json")
    ref = today - dt.timedelta(days=lag)
    sel = sorted(near(events, p, ref, WINDOW_YEAR), key=lambda e: e["_d"], reverse=True)
    n = len(sel)
    return ind(name, "security", n, "events", classify(n, 1, 3, "high_bad"),
               plural(n, "event", "events") + ("" if not sel else ": " + "; ".join(
                   f"{e['_d'].isoformat()} {short(e.get('breve') or e.get('nome'), 70)}" for e in sel[:3])),
               {"green": "none", "amber": "1–2", "red": "3 or more"},
               "Baltic security file (curated, one source per event) plus hybrid and cable files", ref.isoformat(),
               "baltico-sicurezza.json, cavi-incidenti.json", "Same exclusions as the 90-day count. Measures how exposed "
               "the area is to hybrid pressure, not today's threat.")


def i_gnss(p):
    name = f"GNSS interference within {RADIUS_KM} km (last 7 days)"
    bs = load("baltico-sicurezza.json")
    g = (bs or {}).get("gnss") or {}
    cells = g.get("celle") or []
    if not cells:
        return na(name, "security", "no GNSS cells in baltico-sicurezza.json", "GPSJam", "baltico-sicurezza.json")
    lat0, lat1 = min(c["lat"] for c in cells), max(c["lat"] for c in cells)
    lon0, lon1 = min(c["lon"] for c in cells), max(c["lon"] for c in cells)
    if not (lat0 - 1 <= p["lat"] <= lat1 + 1 and lon0 - 1 <= p["lon"] <= lon1 + 1):
        return na(name, "security", "port outside the area monitored by the repository's GNSS layer (North Sea and Baltic)",
                  "GPSJam", "baltico-sicurezza.json")
    sel = [c for c in cells if km(p["lat"], p["lon"], c["lat"], c["lon"]) <= RADIUS_KM]
    worst = max(sel, key=lambda c: c.get("pct_aerei_disturbati") or 0) if sel else None
    lvl = (worst or {}).get("livello")
    status = "red" if lvl == "alto" else "amber" if lvl == "medio" else "green"
    val = (worst or {}).get("pct_aerei_disturbati", 0.0)
    return ind(name, "security", val, "% of aircraft reporting degraded navigation (worst nearby cell)", status,
               (f"worst cell: {fmt(val)}% of {worst.get('aerei')} aircraft affected ({'high' if lvl == 'alto' else 'medium'})" if worst
                else "no affected cell nearby"),
               {"green": "no cell above 2%", "amber": "2–10% of aircraft", "red": "over 10% of aircraft"},
               "GPSJam (John Wiseman), ADS-B Exchange data, H3 cells", str((g.get("periodo") or ["", ""])[-1]),
               "baltico-sicurezza.json", "Measures the effect on aircraft, used as a proxy for ships near the coast; "
                                         "a snapshot, kept unchanged in the reconstructed 7-day-ago score.", "https://gpsjam.org/")


def i_shadow(p):
    name = f"Likely shadow-fleet or sanctioned tankers within {RADIUS_KM} km (AIS snapshot)"
    if p["source_id"] not in BALTIC:
        return na(name, "security", "outside the Baltic AIS coverage used by the repository (Digitraffic)", "Digitraffic", "baltico-sicurezza.json")
    bs = load("baltico-sicurezza.json")
    if not bs:
        return na(name, "security", "baltico-sicurezza.json missing", "Digitraffic", "baltico-sicurezza.json")
    sel = [x for x in bs.get("flotta_vista", []) if x.get("flotta_ombra_probabile")
           and km(p["lat"], p["lon"], x["lat"], x["lon"]) <= RADIUS_KM]
    n = len(sel)
    d = max((x.get("data", "") for x in bs.get("flotta_vista", [])), default="")
    return ind(name, "security", n, "ships", classify(n, 1, 5, "high_bad"),
               plural(n, "ship", "ships") + (": " + ", ".join(x["nome"] for x in sel[:5]) if sel else ""),
               {"green": "none", "amber": "1–4", "red": "5 or more"},
               "Digitraffic (Fintraffic) and aisstream.io positions crossed with sanctions lists", d, "baltico-sicurezza.json",
               "One moment, not an average; good coverage only in the Gulf of Finland; ships with AIS off are missing. "
               "Thresholds are an assessment. Risk: dragged anchors on cables and pipelines, oil spills.",
               "https://www.digitraffic.fi/")


def i_news(p):
    name = f"News headlines naming the port with disruption keywords (last {NEWS_HOURS} h)"
    nt = load("notizie-testate.json")
    if not nt:
        return na(name, "security", "notizie-testate.json missing", "", "notizie-testate.json")
    items = nt.get("elementi", [])
    try:
        latest = max(dt.datetime.fromisoformat(x["data_utc"].replace("Z", "+00:00")) for x in items if x.get("data_utc"))
    except ValueError:
        return na(name, "security", "no dated articles", "", "notizie-testate.json")
    since = latest - dt.timedelta(hours=NEWS_HOURS)
    pats = [re.compile(r"(?<!\w)" + re.escape(a) + r"(?!\w)") for a in ALIASES.get(p["id"], [p["name"]])]
    sel = []
    for x in items:
        try:
            t = dt.datetime.fromisoformat(x["data_utc"].replace("Z", "+00:00"))
        except Exception:
            continue
        txt = f"{x.get('titolo', '')} {x.get('sommario', '')}"
        if t >= since and any(pt.search(txt) for pt in pats) and NEWS_KEYWORDS.search(txt):
            sel.append(x)
    n = len(sel)
    out = ind(name, "security", n, "articles", classify(n, 1, 3, "high_bad"),
              plural(n, "article", "articles") + (": " + "; ".join(f"{x.get('testata')}: {short(x.get('titolo'), 80)}" for x in sel[:3]) if sel else ""),
              {"green": "none", "amber": "1–2", "red": "3 or more"},
              "RSS feeds of 90+ general and trade outlets (title and summary only)", latest.date().isoformat(),
              "notizie-testate.json", "Keyword match (strike, closure, congestion, attack, drone, fire, collision…): catches "
                                      "strikes and closures before AIS does, but can match unrelated stories. Kept unchanged in the "
                                      "reconstructed score.")
    out["fixed"] = True
    out["links"] = [x.get("link") for x in sel[:3]]
    return out


# ---------------------------------------------------------------- probability: chokepoints and insurance
def choke_scores(lag, today):
    """Chokepoint scores from the observatory's chokepoint dashboard (today, or the saved day ~7 days earlier)."""
    r = load("rischio.json")
    if not r:
        return {}, ""
    if lag <= 0:
        return {u["id"]: {"s": u.get("punteggio"), "level": u.get("livello"), "name": u.get("nome")}
                for u in (r or {}).get("unita", [])}, (r or {}).get("data_riferimento", "")
    try:
        with open(CHOKE_HISTORY, encoding="utf-8") as f:
            st = json.load(f)
        target = today - dt.timedelta(days=lag)
        cand = [g for g in st.get("giorni", []) if abs((day(g["data"]) - target).days) <= 3]
        if cand:
            g = min(cand, key=lambda g: abs((day(g["data"]) - target).days))
            names = {u["id"]: u.get("nome") for u in (r or {}).get("unita", [])}
            return {k: {"s": v.get("s"), "level": v.get("livello"), "name": names.get(k, k)} for k, v in g["unita"].items()}, g["data"]
    except Exception:
        pass
    return choke_scores(0, today)


def dependencies(p, roles):
    """Which chokepoints the port's trades depend on: list of (chokepoint unit id, 'primary'/'secondary', reason)."""
    deps = []
    if p["source_id"] in BALTIC:
        deps.append(("baltico", "primary", "Baltic port: every ocean-going call passes the Danish straits or the Kiel Canal"))
        deps.append(("stretti-danesi", "primary", "Danish straits"))
    if p["id"] in SUEZ_FIRST_LANDFALL:
        deps.append(("mar-rosso-container", "primary", "named by stretti-dettaglio.json as first European landfall of the Suez route"))
    elif p["region"] == "italy":
        deps.append(("mar-rosso-container", "primary" if "container" in roles else "secondary",
                     "Mediterranean port: Asia–Europe services come through Suez"))
    elif "container" in roles:
        deps.append(("mar-rosso-container", "secondary", "North European container port: Asia services can use the Cape route"))
    if "lng" in roles:
        if p["country"] == "IT":
            deps.append(("gnl-qatar", "primary", "Italian LNG: 32.6% from the Gulf (UN Comtrade, via rischio.json)"))
        else:
            deps.append(("gnl-qatar", "secondary", "LNG terminal: Europe's LNG price is set with Qatar's supply"))
    if "oil" in roles and p["country"] != "RU":
        deps.append(("hormuz", "secondary", "oil and products port: Gulf crude and Brent prices"))
    return deps


def i_chokepoints(p, roles, scores, sdate):
    name = "Exposure to disrupted chokepoints"
    if not scores:
        return na(name, "chokepoints", "rischio.json missing: chokepoint scores unavailable", "", "rischio.json")
    deps = dependencies(p, roles)
    if not deps:
        return ind(name, "chokepoints", 0, "weighted chokepoint score", "green",
                   "no dependency on a scored chokepoint identified", {}, "Observatory chokepoint dashboard",
                   sdate, "rischio.json", "Dependencies are rules, not measured trade shares (see method).", kind="rule")
    rows, worst_p, worst_s, val = [], 0, 0, 0
    for cid, kind, why in deps:
        s = (scores.get(cid) or {}).get("s")
        if s is None:
            continue
        w = 1.0 if kind == "primary" else 0.5
        val = max(val, s * w)
        if kind == "primary":
            worst_p = max(worst_p, s)
        else:
            worst_s = max(worst_s, s)
        rows.append(f"{CHOKE_EN.get(cid, (scores.get(cid) or {}).get('name', cid))} {fmt(s)}/25 ({kind})")
    status = "red" if worst_p >= 12 else "amber" if worst_p >= 6 or worst_s >= 12 else "green"
    out = ind(name, "chokepoints", val, "max of chokepoint score × dependency (1 primary, 0.5 secondary)", status,
              "; ".join(rows), {"green": "primary chokepoints low, secondary below high",
                                "amber": "a primary chokepoint medium (6–12), or a secondary one high/critical (≥ 12)",
                                "red": "a primary chokepoint high or critical (≥ 12)"},
              "Observatory chokepoint dashboard (PortWatch, events, prices) and route rules from stretti-dettaglio.json",
              sdate, "rischio.json, stretti-dettaglio.json",
              "Route dependency is a transparent rule (geography, vessel mix, LNG origin), not a measured share of each "
              "port's cargo: per-port trade shares by chokepoint are not in the repository.", kind="rule")
    out["dependencies"] = [{"chokepoint": c, "dependency": k, "reason": r} for c, k, r in deps]
    return out


def i_jwc(p):
    name = "Inside a Joint War Committee listed area"
    a = load("assicurazioni.json")
    if not a:
        return na(name, "insurance", "assicurazioni.json missing", "Joint War Committee", "assicurazioni.json")
    hit = None
    for e in a.get("elementi", []):
        if e.get("tipo") == "paese" and e.get("paese") == p["country"]:
            hit = e
        elif e.get("tipo") == "acque":
            for ring in e.get("g") or []:
                if ring and in_polygon(p["lon"], p["lat"], ring):
                    hit = e
        if hit:
            break
    circ = a.get("circolare_in_vigore") or {}
    return ind(name, "insurance", 1 if hit else 0, "yes = 1", "red" if hit else "green",
               (f"yes: {hit['nome']} (listed since {short(hit.get('data_inserimento', ''), 60)})" if hit else
                f"no: not in the listed areas of circular {circ.get('id', '')}"),
               {"green": "not listed", "red": "listed: additional war-risk premium needed for each call"},
               "Joint War Committee (LMA/IUA), JWC Listed Areas", circ.get("data", ""), "assicurazioni.json",
               "Binary: the listing does not say how much the premium is; Baltic and North Sea waters outside Russia are not listed.",
               circ.get("link", ""))


# ---------------------------------------------------------------- impact
def roles_of(p):
    """Strategic functions, each derived from a repository file. Returns {role: evidence}."""
    roles = {}
    spec = p["spec"].lower()
    gnl = load("terminali-gnl.json")
    terms = [t for t in (gnl or {}).get("elementi", []) if t.get("tipo") == "import" and t.get("stato") == "operativo"
             and t.get("lat") is not None and (km(p["lat"], p["lon"], t["lat"], t["lon"]) <= LNG_RADIUS_KM
                                               or t.get("nome") == EXTRA_LNG.get(p["source_id"]))]
    if terms:
        cap = sum(t.get("capacita_operativa_mtpa") or 0 for t in terms)
        roles["lng"] = ", ".join(t["nome"] for t in terms) + f" ({fmt(cap)} Mt/yr operating, Global Energy Monitor)"
        if cap >= LNG_NATIONAL_MTPA:
            roles["lng_national"] = f"national-scale LNG entry point (≥ {LNG_NATIONAL_MTPA:.0f} Mt/yr)"
    if "lng" not in roles and re.search(r"\bgnl\b", spec) and not re.search(r"gnl[^;]*(in costruzione|in progetto|piccola scala)", spec):
        roles["lng"] = "LNG terminal named in porti-nord.json"
    m30 = p["src"].get("media30") or {}
    tank, tot = m30.get("portcalls_tanker") or 0, m30.get("portcalls") or 0
    if tank >= 3 or (tot >= 1 and tank / tot >= 0.5):
        roles["oil"] = f"{fmt(tank)} tanker calls/day ({round(tank / tot * 100) if tot else 0}% of calls, PortWatch 30 days)"
    elif "greggio" in spec:
        roles["oil"] = "crude terminal named in porti-nord.json"
    cont = m30.get("portcalls_container") or 0
    if cont >= 2:
        roles["container"] = f"{fmt(cont)} container calls/day (PortWatch 30 days)"
    wind = load("eolico-filiera.json")
    for w in (wind or {}).get("elementi", []):
        if (w.get("id_porti_nord") == p["source_id"] or km(p["lat"], p["lon"], w["lat"], w["lon"]) <= 15) \
                and str(w.get("stato", "")).startswith("operativo"):
            c = w.get("categoria", "").replace("porto ", "")
            roles["wind"] = f"offshore wind {WIND_EN.get(c, c)} port ({w['nome']}, eolico-filiera.json)"
            break
    bases = ((load("basi-mondo.json") or {}).get("elementi", []) + (load("italia.json") or {}).get("punti", []))
    for b in bases:
        try:
            if str(b.get("stato", "")).startswith("operativ") and km(p["lat"], p["lon"], float(b["lat"]), float(b["lon"])) <= 15:
                roles["military"] = f"{b['nome']} within 15 km ({'italia.json' if 'IT' == b.get('paese') else 'basi-mondo.json'})"
                break
        except (TypeError, ValueError, KeyError):
            continue
    if "military" not in roles and re.search(r"militar|navale|nato|flotta", spec):
        roles["military"] = "military logistics or naval base named in porti-nord.json"
    return roles


ROLE_NAMES = {"lng": "LNG import terminal", "lng_national": "national-scale LNG entry point", "oil": "oil and products hub", "container": "container gateway",
              "wind": "offshore wind base port", "military": "military or dual-use port"}


def i_role(p, roles):
    n = len(roles)
    return ind("Strategic functions (LNG, oil, container, offshore wind, military/dual use)", "role", n, "functions (a national-scale LNG terminal counts twice)",
               "red" if n >= 3 else "amber" if n == 2 else "green",
               ("; ".join(f"{ROLE_NAMES[k]}: {v}" for k, v in roles.items()) if roles else "none of the five functions found"),
               {"green": "0–1 functions", "amber": "2", "red": "3 or more"},
               "Global Energy Monitor (LNG), IMF PortWatch (vessel mix), eolico-filiera, basi-mondo/italia (bases), porti-nord",
               file_date("terminali-gnl.json")[:10], "terminali-gnl.json, eolico-filiera.json, basi-mondo.json, italia.json, porti-nord.json",
               "Each function comes from a rule on repository data (LNG within 20 km, bases and wind ports within 15 km, "
               "PortWatch vessel-mix thresholds); "
               "PortWatch under-counts ro-ro and ferry traffic.", kind="rule")


def i_size(p):
    m30 = p["src"].get("media30") or {}
    if m30.get("import") is None and m30.get("export") is None:
        return na("Estimated cargo handled", "size", "no PortWatch cargo estimate", PW_SOURCE, p["file"])
    kt = ((m30.get("import") or 0) + (m30.get("export") or 0)) / 1000
    return ind("Estimated cargo handled, 30-day mean (imports + exports)", "size", kt, "thousand t/day",
               classify(kt, 50, 200, "high_bad"), f"{fmt(kt, 0)} thousand t/day",
               {"green": "< 50 kt/day", "amber": "50–200 kt/day", "red": "≥ 200 kt/day"},
               PW_SOURCE, p["src"].get("ultima_data", ""), p["file"],
               "PortWatch estimate from AIS draught changes: transhipment and ro-ro are under-estimated.", PW_LINK)


def nearest_hub(p):
    b = load("bunker-emissioni.json")
    best = None
    for h in (b or {}).get("elementi", []):
        v = ((h.get("prezzi") or {}).get("VLSFO") or {})
        same_basin = (h["lat"] < 46) == (p["lat"] < 46)    # Mediterranean ports use Mediterranean hubs
        if h.get("tipo") == "hub_bunker" and v.get("ultimo") is not None and same_basin:
            d = km(p["lat"], p["lon"], h["lat"], h["lon"])
            if not best or d < best[0]:
                best = (d, h, v)
    return best


def i_bunker(p):
    name = "Bunker fuel (VLSFO) at the nearest hub with a public price, vs a year ago"
    best = nearest_hub(p)
    if not best:
        return na(name, "energy", "no public bunker price in bunker-emissioni.json", "Ship & Bunker", "bunker-emissioni.json")
    d, h, v = best
    var = v.get("var_1a_pct")
    return ind(f"Bunker fuel (VLSFO) at {HUBS_EN.get(h['nome'], h['nome'])}, vs a year ago", "energy", var, "% vs a year ago",
               classify(var, 10, 40, "high_bad"),
               f"{fmt(v['ultimo'], 1)} USD/t, {pct(var)} on a year (hub {fmt(d, 0)} km away)",
               {"green": "< +10%", "amber": "+10% to +40%", "red": "> +40%"},
               "Ship & Bunker (public port price page)", v.get("data", ""), "bunker-emissioni.json",
               "Nearest hub in the same sea basin with a public price, not the port's own price (Genoa, Hamburg, Gdańsk "
               "and Skaw are subscriber-only).", h.get("link", ""))


def i_ttf():
    name = "TTF gas price vs a year ago"
    pr = load("prezzi.json")
    el = next((s for s in (pr or {}).get("serie", []) if s.get("id") == "ttf"), None)
    var = ((el or {}).get("var") or {}).get("1a")
    if var is None:
        return na(name, "energy", "TTF series missing in prezzi.json", "Yahoo Finance", "prezzi.json")
    return ind(name, "energy", var, "% vs a year ago", classify(var, 10, 40, "high_bad"),
               f"{fmt(el.get('ultimo'), 2)} EUR/MWh, {pct(var)} on a year",
               {"green": "< +10%", "amber": "+10% to +40%", "red": "> +40%"},
               "Yahoo Finance (front-month TTF future)", el.get("data", ""), "prezzi.json",
               "Common to every European port: it raises the level, it does not rank ports. Not an official price.",
               el.get("link", ""))


def i_storage(p):
    s = load("scorte.json")
    el = next((x for x in (s or {}).get("elementi", []) if x.get("id") == f"gas_stoccaggio_pct_{str(p['country']).lower()}"), None)
    if not el:
        return None
    u = el.get("ultimo") or {}
    gap = (u.get("media_5_anni") or {}).get("scarto_pct")
    return ind(f"Gas storage in {p['country']} vs the 5-year average (LNG port buffer)", "energy", gap, "% vs 5-year average",
               classify(gap, -5, -15, "low_bad"), f"{fmt(u.get('valore'))}% full, {pct(gap)} vs the 5-year average",
               {"green": "≥ −5%", "amber": "−5% to −15%", "red": "< −15%"},
               el.get("fonte", "GIE AGSI+"), u.get("data", ""), "scorte.json",
               "Counted only for LNG ports: low storage makes an outage at the terminal hurt more.", el.get("link", ""))


# ---------------------------------------------------------------- scoring
def group_score(lst, weights):
    by = {}
    for x in lst:
        if x["status"] in POINTS and x.get("scored", True):
            by.setdefault(x["group"], []).append(POINTS[x["status"]])
    used = {g: w for g, w in weights.items() if g in by}
    tot = sum(used.values())
    if not tot:
        return None, {}, 0.0
    score = sum(sum(by[g]) / len(by[g]) * w for g, w in used.items()) / tot
    return score, {g: round(w / tot, 3) for g, w in used.items()}, tot


def level(s):
    return next(n for t, n in LEVELS if s >= t)


def evaluate(p, today, events, lag=0, current=None):
    roles = roles_of(p)
    scores, sdate = choke_scores(lag, today)
    yoy = i_calls_yoy(p, lag)
    prob = [yoy, i_type_yoy(p), i_momentum(p, lag),
            i_events_recent(events, p, today, lag), i_events_year(events, p, today, lag), i_gnss(p), i_shadow(p), i_news(p),
            i_chokepoints(p, roles, scores, sdate), i_jwc(p)]
    imp = [i_role(p, roles), i_size(p), i_bunker(p), i_ttf()]
    if "lng" in roles:
        st = i_storage(p)
        if st:
            imp.append(st)
    P, wp, cp = group_score(prob, W_PROB)
    I, wi, ci = group_score(imp, W_IMP)
    rule = None
    sec = prob[3]
    if yoy.get("disruption"):
        rule = f"port calls {pct(yoy['value'])} on a year (≤ {DISRUPTION:.0f}%)"
    elif sec.get("port_attack_7d"):
        rule = "attack on the port or its terminals in the last 7 days: " + short(sec["port_attack_7d"][0], 80)
    if rule and P is not None:
        P = 5.0
    cap = None
    if I is not None and p["country"] == "RU" and I > RU_IMPACT_CAP:
        cap = f"impact capped at {RU_IMPACT_CAP:.0f}: Russian port, EU trade with it is largely sanctioned"
        I = RU_IMPACT_CAP
    if P is None or I is None or P is not None and "traffic" not in wp and "security" not in wp:
        S = None
    else:
        P, I = round(P, 1), round(I, 1)
        S = round(P * I, 1)
        if S >= 20 and (P < 4 or I < 4):
            S = 19.9
    return {"p": P, "i": I, "s": S, "prob": prob, "imp": imp, "w_p": wp, "w_i": wi, "roles": roles,
            "coverage": round((cp + ci) / 2, 2), "rule": rule, "cap": cap}


# ---------------------------------------------------------------- text from rules
def why(p, r, trend):
    if r["s"] is None:
        return "Score not computable today: traffic and security data are both missing (see errors)."
    out = []
    hot = sorted([x for x in r["prob"] if x["status"] in ("red", "amber") and x.get("scored", True)],
                 key=lambda x: -POINTS[x["status"]] * W_PROB.get(x["group"], 0))
    if r["rule"]:
        out.append(f"Disruption already in progress ({r['rule']}): by rule probability is 5.")
    elif hot:
        out.append(f"Probability {fmt(r['p'])}/5 is driven by " + " and by ".join(
            f"{x['name']} ({short(x['text'], 110)})" for x in hot[:2]) + ".")
    else:
        out.append(f"No early-warning indicator is amber or red: probability {fmt(r['p'])}/5.")
    hi = [x for x in r["imp"] if x["status"] == "red" and x["group"] in ("role", "size")]
    if r["cap"]:
        out.append(f"Impact {fmt(r['i'])}/5: {r['cap']}.")
    elif hi:
        out.append(f"Impact {fmt(r['i'])}/5; in the red: " + "; ".join(f"{x['name'].split(' (')[0].split(',')[0]}: {short(x['text'], 120)}" for x in hi) + ".")
    else:
        out.append(f"Impact {fmt(r['i'])}/5: neither its strategic role nor its size is in the red; energy costs are high everywhere.")
    if trend.get("before") is not None and trend["trend"] != "stable":
        out.append(f"The score is {trend['trend']} on 7 days ago ({fmt(trend['before'])} → {fmt(r['s'])}).")
    if r["coverage"] < 0.7:
        out.append(f"Caution: only {round(r['coverage'] * 100)}% of the weights have data.")
    return " ".join(out)


def watch(p, r):
    out = []
    for x in r["prob"]:
        if x["status"] == "n/a":
            continue
        if x["group"] == "traffic" and x.get("scored", True) and x["status"] != "green":
            out.append(f"{x['name']}: today {pct(x['value'])}; red at {x['thresholds'].get('red', '')}.")
        elif x["group"] == "security" and x["status"] == "amber":
            out.append(f"{x['name']}: {short(x['text'], 90)}; red with {x['thresholds'].get('red', '')}.")
        elif x["group"] == "chokepoints" and x["status"] != "green":
            out.append(f"Chokepoints: {short(x['text'], 140)}. A primary chokepoint at ≥ 12/25 turns this red.")
    t = next((x for x in r["prob"] if x["name"].startswith("Port calls") and x["status"] == "green"), None)
    if t and t.get("base") and not r["rule"]:
        out.append(f"Disruption trigger: 7-day calls below {fmt(t['base'] * 0.5)}/day (−50% on last year).")
    if "lng" in r["roles"]:
        st = next((x for x in r["imp"] if x["name"].startswith("Gas storage")), None)
        if st and st["status"] != "green":
            out.append(f"{st['name']}: {st['text']}.")
    return out[:6]


# ---------------------------------------------------------------- calibration (shown in the output)
def calibration(port_list):
    """Share of weeks in the PortWatch history that would have breached each traffic threshold."""
    acc = {k: [] for k in ("yoy_big", "yoy_small", "mom_big", "mom_small")}
    for p in port_list:
        s = ((p["src"].get("serie") or {}).get("portcalls")) or []
        dm = {day(d): v for d, v in s if v is not None}
        for d in sorted(dm):
            if d.weekday() != 6:
                continue
            b7 = window_mean(dm, d, 7, 364)
            if b7:
                if b7 >= SMALL_PORT:
                    acc["yoy_big"].append((window_mean(dm, d, 7) / b7 - 1) * 100)
                else:
                    b28 = window_mean(dm, d, 28, 364)
                    n28 = window_mean(dm, d, 28)
                    if b28 and n28 is not None:
                        acc["yoy_small"].append((n28 / b28 - 1) * 100)
            prev = window_mean(dm, d, 28, 7)
            now = window_mean(dm, d, 7)
            if prev and now is not None:
                acc["mom_big" if prev >= SMALL_PORT else "mom_small"].append((now / prev - 1) * 100)
    out = {}
    for k, vals in acc.items():
        amb, red = TRAFFIC_THRESHOLDS[k]
        n = len(vals)
        out[k] = {"weeks": n, "amber_or_worse_share": round(sum(v <= amb for v in vals) / n, 3) if n else None,
                  "red_share": round(sum(v <= red for v in vals) / n, 3) if n else None, "thresholds": [amb, red]}
    return out


# ---------------------------------------------------------------- history and trend
def read_history():
    try:
        with open(HISTORY, encoding="utf-8") as f:
            h = json.load(f)
        if isinstance(h.get("days"), list):
            return h
    except Exception:
        pass
    return {"note": "Daily Port Risk Index scores. 'reconstructed': true = computed afterwards by dropping the last 7 days "
                    "of every series (indicators without a series kept unchanged).", "days": []}


def save_day(h, date, scores, reconstructed=False):
    h["days"] = [d for d in h["days"] if d.get("date") != date]
    h["days"].append({"date": date, "reconstructed": reconstructed, "ports": scores})
    h["days"].sort(key=lambda d: d["date"])
    h["days"] = h["days"][-400:]


def ref_7d(h, today):
    cand = [d for d in h["days"] if 5 <= (today - day(d["date"])).days <= 10]
    return min(cand, key=lambda d: abs((today - day(d["date"])).days - 7)) if cand else None


# ---------------------------------------------------------------- main
def main():
    today = day(sys.argv[1]) if len(sys.argv) > 1 else dt.datetime.now(dt.timezone.utc).date()
    events = collect_events(today)
    plist = ports()
    hist = read_history()
    results = {}
    for p in plist:
        try:
            results[p["id"]] = evaluate(p, today, events)
        except Exception as e:  # one broken port must not stop the others
            ERRORS.append(f"{p['id']}: computation failed ({e.__class__.__name__}: {e})")
    if not ref_7d(hist, today):
        rec = {}
        for p in plist:
            if p["id"] in results:
                try:
                    r7 = evaluate(p, today, events, lag=7)
                    rec[p["id"]] = {"p": r7["p"], "i": r7["i"], "score": r7["s"], "level": level(r7["s"]) if r7["s"] is not None else "n/a"}
                except Exception as e:
                    ERRORS.append(f"{p['id']}: 7-day reconstruction failed ({e})")
        save_day(hist, (today - dt.timedelta(days=7)).isoformat(), rec, reconstructed=True)
    base = ref_7d(hist, today)

    out_ports, saved = [], {}
    for p in plist:
        r = results.get(p["id"])
        if not r:
            continue
        before = ((base or {}).get("ports") or {}).get(p["id"], {}).get("score")
        if r["s"] is None or before is None:
            trend = {"trend": "n/a", "before": None}
        else:
            d = r["s"] - before
            trend = {"trend": "rising" if d >= TREND_STEP else "falling" if d <= -TREND_STEP else "stable", "before": before}
        lvl = level(r["s"]) if r["s"] is not None else "n/a"
        saved[p["id"]] = {"p": r["p"], "i": r["i"], "score": r["s"], "level": lvl}
        indicators = []
        for axis, lst in (("probability", r["prob"]), ("impact", r["imp"])):
            for x in lst:
                x = {k: v for k, v in x.items() if k not in ("port_attack_7d", "fixed", "base", "now")}
                x["axis"] = axis
                x["question"] = GROUP_NAMES.get(x["group"], x["group"])
                indicators.append(x)
        out_ports.append({
            "id": p["id"], "source_id": p["source_id"], "name": p["name"], "country": p["country"],
            "region": "North Sea / Baltic" if p["region"] == "north" else "Italy",
            "lat": p["lat"], "lon": p["lon"], "probability": r["p"], "impact": r["i"], "score": r["s"], "level": lvl,
            "trend": trend["trend"], "score_7d_ago": trend["before"],
            "date_7d_ago": base["date"] if base and trend["before"] is not None else None,
            "history_reconstructed": bool(base and base.get("reconstructed")),
            "disruption_rule": r["rule"], "impact_cap": r["cap"], "coverage": r["coverage"],
            "weights_used": {"probability": r["w_p"], "impact": r["w_i"]},
            "strategic_roles": [ROLE_NAMES[k] for k in r["roles"]],
            "indicators": indicators, "why": why(p, r, trend), "watch": watch(p, r),
        })
    out_ports.sort(key=lambda x: -(x["score"] or 0))
    for i, x in enumerate(out_ports, 1):
        x["rank"] = i
    save_day(hist, today.isoformat(), saved)
    hist["updated"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

    files = sorted({f for x in out_ports for i in x["indicators"] for f in str(i.get("file", "")).split(", ") if f.endswith(".json")})
    out = {
        "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "reference_date": today.isoformat(),
        "method": METHOD_LINK,
        "note": "Port Risk Index: probability of disruption (1–5) × impact on European and Italian supply chains (1–5) = "
                "score 1–25. Every indicator carries value, thresholds, status, source and date. It is a rule-based "
                "assessment, not a forecast: see the method for what the score does NOT say.",
        "rules": {
            "points": POINTS, "weights_probability": W_PROB, "weights_impact": W_IMP,
            "levels": {"low": "< 6", "medium": "6–11.9", "high": "12–19.9", "critical": "≥ 20 (both axes ≥ 4)"},
            "disruption_rule": f"7-day calls ≤ {DISRUPTION:.0f}% on last year (ports with ≥ {SMALL_PORT:.0f} calls/day), or an attack "
                               "on the port or its terminals within 20 km in the last 7 days: probability = 5",
            "russia_rule": f"impact capped at {RU_IMPACT_CAP:.0f} for Russian ports (European viewpoint)",
            "trend": f"score difference with the saved day closest to 7 days ago: ±{TREND_STEP}",
            "radius_km": RADIUS_KM, "coverage": "share of weights covered by groups with data; below 0.7 the score is fragile",
        },
        "calibration": calibration(plist),
        "sources": [{"file": f, "updated": file_date(f)} for f in files],
        "ports": out_ports,
        "errors": ERRORS,
    }
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    tmp = OUTPUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, OUTPUT)
    tmp = HISTORY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=1)
    os.replace(tmp, HISTORY)

    print(f"port-risk.json: {len(out_ports)} ports, {len(ERRORS)} warnings")
    for x in out_ports:
        print(f"  {x['rank']:2} {x['name'][:38]:38} {x['country']}  P {fmt(x['probability'])}  I {fmt(x['impact'])}  "
              f"= {fmt(x['score']):>5}  {x['level']:8} {x['trend']}")
    for e in ERRORS:
        print("  warning:", e)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # last safety net: the workflow must not fail
        print(f"port risk index not computed: {e.__class__.__name__}: {e}", file=sys.stderr)
        sys.exit(0)
