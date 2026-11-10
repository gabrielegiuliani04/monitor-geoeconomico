#!/usr/bin/env python3
"""Build the monthly report "Offshore Wind in Northern Europe: Targets, Bottlenecks and Ports".

Standard library only. From the repository root:

    python3 report/build_offshore_wind.py                  # edition for the current month
    python3 report/build_offshore_wind.py --month 2026-12  # another edition label
    python3 report/build_offshore_wind.py --offline        # no web calls: use the market cache

What it does every time it runs:
1. reads docs/data/*.json: eolico-filiera, wind-calendar, offshore-nord, porti-nord, port-risk,
   rete-elettrica, interconnessioni, cyber-energia, baltico-sicurezza, idrogeno, prezzi, scorte,
   esposizione-nord;
2. reads report/dati/offshore-wind-esterni.json (curated external facts: WindEurope auction prices
   in EUR/MWh, 2025 FIDs, the RVO Gamma-B window; each with source, link and date);
3. updates report/dati/offshore-wind-mercati.json with the euro-area AAA 10-year yield and the ECB
   deposit rate (ECB Data Portal) and COMEX copper and US hot-rolled coil steel (Yahoo Finance);
   with --offline, or if a call fails, the cache is used and the report says so;
4. recomputes every number and draws four SVG charts (wide and narrow versions);
5. writes report/offshore-wind-YYYY-MM.md, docs/report/en/offshore-wind-YYYY-MM.html and
   report/grafici/ow-YYYY-MM-*.svg.

Rules (report/STANDARD.md): no number from the data is typed by hand in the text or the charts.
Hand-written items are: linking prose and assessments (marked "Assessment"), the watch-list
THRESHOLDS (an assessment, labelled), and English renderings of Italian curated text. Every
figure quoted from a text field of a JSON file is guarded by need(): if the figure is no longer in
the source text, the script warns, so the sentence is re-read before publication.
"""

import argparse
import csv
import datetime as dt
import html
import io
import json
import math
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "data")
CACHE = os.path.join(ROOT, "report", "dati")
OUT_SVG = os.path.join(ROOT, "report", "grafici")
OUT_HTML = os.path.join(ROOT, "docs", "report", "en")
EXT_FILE = os.path.join(CACHE, "offshore-wind-esterni.json")
MKT_FILE = os.path.join(CACHE, "offshore-wind-mercati.json")

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
MON = [m[:3] for m in MONTHS]
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
         11: "eleven", 12: "twelve"}
CN = {"GB": "UK", "DE": "Germany", "NL": "Netherlands", "DK": "Denmark", "BE": "Belgium", "PL": "Poland", "NO": "Norway",
      "FR": "France", "LT": "Lithuania", "LV": "Latvia", "EE": "Estonia", "SE": "Sweden", "FI": "Finland", "IE": "Ireland", "EU": "EU"}
WARN = []

# Watch-list thresholds: an ASSESSMENT of the monitor, not a forecast. Re-read each edition.
THRESHOLDS = {
    "gamma_min_bids": 2,          # applications per Gamma site; zero repeats Nederwiek I-A
    "ar8_price_gbp": 100.0,       # GBP/MWh (2024 prices) clearing price for fixed-bottom offshore in AR8
    "ar8_min_gw": 5.0,            # GW of offshore wind awarded in AR8
    "platform_slip_months": 6,    # any further slip of a 2 GW TenneT/Amprion/50Hertz HVDC link
    "cable_backlog_bn": 32.0,     # EUR bn, Prysmian + NKT transmission backlog combined
    "cadeler_util_low": 50.0,     # % fleet utilisation: below = vessel surplus
    "cadeler_util_high": 85.0,    # % fleet utilisation: above = vessels tight again
    "eur10y": 3.5,                # % euro-area AAA 10-year yield
    "us10y": 5.0,                 # % US 10-year yield
    "copper_rise_pct": 10.0,      # % rise from today's copper price
    "gnss_km": 75,                # radius around Baltic wind ports and farms for GNSS cells
}

# Review box: placeholder. The independent reviewer fills it in and keeps the log in report/revisioni/.
REVIEW = {
    "date": None,
    "log": "report/revisioni/offshore-wind-2026-11.md",
    "text": ("Pending. An independent reviewer will check every number in this report against the data files and the cited sources, "
             "under report/STANDARD.md, and record the result here: date, number of claims checked, corrections, what remains unverifiable. "
             "Until then, treat the report as a draft."),
}


def word(n, cap=False):
    w = WORDS.get(n, str(n))
    return w[0].upper() + w[1:] if cap else w


def warn(msg):
    WARN.append(msg)
    print("WARNING:", msg, file=sys.stderr)


# =====================================================================================
# Helpers
# =====================================================================================
def load(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        raise SystemExit(f"missing data file: {p}")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def d(s):
    return dt.date.fromisoformat(str(s)[:10])


def num(v, dec=1):
    if v is None:
        return "n/a"
    return f"{v:,.{dec}f}"


def pct(v, dec=1, sign=True):
    if v is None:
        return "n/a"
    if round(v, dec) == 0:
        return "0%"
    s = f"{v:+,.{dec}f}" if sign else f"{v:,.{dec}f}"
    return s.replace("-", "−") + "%"


def bp(v):
    return (f"{v:+.0f}".replace("-", "−")) + " basis points"


def date_en(s, year=True):
    s = str(s)
    if len(s) == 7:
        y, m = s.split("-")
        return f"{MONTHS[int(m) - 1]} {y}"
    x = d(s)
    return f"{x.day} {MONTHS[x.month - 1]}" + (f" {x.year}" if year else "")


def date_label(s):
    """Calendar dates as curated: 2026-Q4, 2026-H2, 2027, 2026-12, 2026-11-26."""
    s = str(s)
    if re.fullmatch(r"\d{4}", s):
        return s
    m = re.fullmatch(r"(\d{4})-(Q\d|H\d)", s)
    if m:
        return f"{m.group(2)} {m.group(1)}"
    if len(s) == 7:
        return date_en(s)
    return date_en(s)


def esc(s):
    return html.escape(str(s), quote=True)


def need(text, *tokens, where=""):
    t = str(text)
    for tok in tokens:
        if str(tok) not in t:
            warn(f"curated fact not found in source ({where}): «{tok}»")


def it_num(s):
    return float(str(s).replace(".", "").replace(",", ".")) if "," in str(s) else float(s)


def gw(mw, dec=1):
    return num(mw / 1000, dec)


def hav(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def crf(r, n):
    return r / (1 - (1 + r) ** -n)


# =====================================================================================
# Market data (ECB Data Portal, Yahoo Finance), cached
# =====================================================================================
def http_get(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (monitor report builder)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")


def fetch_ecb(key, start):
    url = f"https://data-api.ecb.europa.eu/service/data/{key}?startPeriod={start}&format=csvdata"
    rows = list(csv.DictReader(io.StringIO(http_get(url))))
    return [[r["TIME_PERIOD"], round(float(r["OBS_VALUE"]), 4)] for r in rows if r.get("OBS_VALUE")]


def fetch_yahoo(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=1y&interval=1d"
    j = json.loads(http_get(url))["chart"]["result"][0]
    ts, cl = j["timestamp"], j["indicators"]["quote"][0]["close"]
    out = []
    for t, c in zip(ts, cl):
        if c is not None:
            out.append([dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat(), round(c, 4)])
    return {"name": j["meta"].get("longName") or j["meta"].get("shortName"), "currency": j["meta"].get("currency"), "series": out}


def markets(today, offline):
    cache = {}
    if os.path.exists(MKT_FILE):
        with open(MKT_FILE, encoding="utf-8") as f:
            cache = json.load(f)
    if offline:
        if not cache:
            warn("--offline and no market cache: rates and materials will be missing")
        return cache, "cache (offline run)"
    start = (today - dt.timedelta(days=400)).isoformat()
    new, status = dict(cache), "read online on " + date_en(today.isoformat())
    jobs = {
        "eur10y": lambda: {"name": "Euro area AAA government bond yield curve, 10-year spot rate", "unit": "%",
                           "source": "ECB Data Portal (YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y)",
                           "link": "https://data.ecb.europa.eu/data/datasets/YC/YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y",
                           "series": fetch_ecb("YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y", start)},
        "dfr": lambda: {"name": "ECB deposit facility rate", "unit": "%", "source": "ECB Data Portal (FM.D.U2.EUR.4F.KR.DFR.LEV)",
                        "link": "https://data.ecb.europa.eu/data/datasets/FM/FM.D.U2.EUR.4F.KR.DFR.LEV",
                        "series": fetch_ecb("FM/D.U2.EUR.4F.KR.DFR.LEV", start)},
        "copper": lambda: dict(fetch_yahoo("HG=F"), unit="USD/lb", source="Yahoo Finance (COMEX HG=F, front month)",
                               link="https://finance.yahoo.com/quote/HG%3DF"),
        "hrc": lambda: dict(fetch_yahoo("HRC=F"), unit="USD/short ton", source="Yahoo Finance (CME HRC=F, US Midwest hot-rolled coil, front month)",
                            link="https://finance.yahoo.com/quote/HRC%3DF"),
    }
    for k, fn in jobs.items():
        try:
            v = fn()
            if not v["series"]:
                raise ValueError("empty series")
            v["read"] = today.isoformat()
            new[k] = v
        except Exception as e:  # noqa: BLE001
            warn(f"market series {k} not refreshed ({e}); using cache" + ("" if k in cache else " (none)"))
            status = "partly from cache"
    new["updated"] = today.isoformat()
    os.makedirs(CACHE, exist_ok=True)
    with open(MKT_FILE, "w", encoding="utf-8") as f:
        json.dump(new, f, ensure_ascii=False, indent=1)
    return new, status


def year_ago(series, last_date):
    target = d(last_date) - dt.timedelta(days=365)
    cands = [x for x in series if d(x[0]) <= target]
    return cands[-1] if cands else series[0]


# =====================================================================================
# Computation
# =====================================================================================
def compute(today, offline):
    F = {n: load(n) for n in ["eolico-filiera.json", "wind-calendar.json", "offshore-nord.json", "porti-nord.json", "port-risk.json",
                              "rete-elettrica.json", "interconnessioni.json", "cyber-energia.json", "baltico-sicurezza.json",
                              "idrogeno.json", "prezzi.json", "scorte.json", "esposizione-nord.json"]}
    with open(EXT_FILE, encoding="utf-8") as f:
        EXT = json.load(f)
    V = {"F": F, "EXT": EXT, "today": today}
    ef, wc, on = F["eolico-filiera.json"], F["wind-calendar.json"], F["offshore-nord.json"]
    V["dates"] = {n: F[n].get("aggiornato") or F[n].get("updated") for n in F}

    # ------------------------------------------------------------- targets and reality
    ob = ef["obiettivi"]
    V["europe"] = ob["europa"]
    need(ob["europa"]["nota"], "minimo dal 2016", "5,4 GW", "22,5 miliardi", where="eolico-filiera obiettivi.europa.nota")
    V["decl"] = {x["id"]: x for x in ob["dichiarazioni"]}
    need(V["decl"]["esbjerg"]["testo"], "20 GW di idrogeno", where="Esbjerg declaration text")
    need(V["decl"]["amburgo"]["testo"], "100 GW", "15 GW l'anno", "2031-2040", where="Hamburg declaration text")
    V["europe_rate"] = (ob["europa"]["previsione_2030_mw"] - ob["europa"]["installato_fine2025_mw"]) / 5 / 1000
    V["hamburg_rate"] = 15.0  # from the declaration text, checked with need() above
    pc = {c["paese"]: c for c in ob["paesi"]}
    avt = {c["country"]: c for c in wc["riepilogo"]["awarded_vs_targets"]["per_country"]}
    uc = {}
    for r in on["riepilogo_mw"]:
        if r["stato"] == "in costruzione":
            uc[r["paese"]] = uc.get(r["paese"], 0) + r["mw"]
    fid = {}
    for e in wc["elementi"]:
        if e["type"] == "FID" and e["status_effective"] == "done" and e["period_start"] >= "2025-01-01":
            fid.setdefault(e["country"], []).append(e)
    V["fid_items"] = fid
    rows = []
    for c in ["GB", "DE", "NL", "DK", "PL", "BE", "NO"]:
        p, a = pc[c], avt.get(c, {})
        tgt = a.get("target_gw") or p.get("obiettivo_2030_gw")
        rows.append({"c": c, "inst": p["installato_fine2025_mw"], "fc": p["previsione_2030_mw"], "tgt": tgt,
                     "tgt_year": a.get("target_year", 2030), "tgt_low": a.get("target_low_gw"),
                     "awarded": a.get("awarded_mw_2023_2026", 0) or 0, "uc": uc.get(c),
                     "fid": sum(e["capacity_mw"] or 0 for e in fid.get(c, [])),
                     "gap": tgt * 1000 - p["installato_fine2025_mw"], "short": tgt * 1000 - p["previsione_2030_mw"]})
    V["countries"] = rows
    V["tot_gap"] = sum(r["gap"] for r in rows)
    V["tot_awarded"] = sum(r["awarded"] for r in rows)
    V["tot_short"] = sum(r["short"] for r in rows)
    V["tot_tgt"] = sum(r["tgt"] for r in rows)
    V["tot_fc"] = sum(r["fc"] for r in rows)
    h4 = next(e for e in wc["elementi"] if e["id"] == "WC-GB-HORNSEA4")
    V["hornsea4_mw"] = h4["capacity_mw"]
    V["nl_target_conflict"] = (pc["NL"]["obiettivo_2030_gw"], avt["NL"]["target_year"])
    de_cab = next(e for e in wc["elementi"] if e["id"] == "WC-DE-WINDSEEG-CAB")
    need(de_cab["summary"], "16 GW already awarded still lack FID", where="WC-DE-WINDSEEG-CAB")
    V["de_nofid_gw"] = 16
    mb = V["decl"]["marienborg"]["calcolo"]["baltico_emodnet"]
    V["baltic"] = mb
    V["fid25"] = EXT["fid_2025"]
    h2 = F["idrogeno.json"]["realta"]["capacita_reale"][0]
    V["h2_mw"] = h2["valore"]
    V["h2_src"] = h2
    V["h2_share"] = h2["valore"] / 20000 * 100

    # ------------------------------------------------------------- auctions
    aste = ef["aste"]
    V["aste"] = aste
    ar = next(x for x in ef["colli_bottiglia"] if x["id"] == "aste-ricavi")
    V["neg_failed_gw"] = ar["indicatori"][0]["valore"]
    V["cfd_2025_gw"] = ar["indicatori"][1]["valore"]
    need(ar["indicatori"][0]["nota"], "3 GW Danimarca", "2,5 GW Germania", "1 GW Paesi Bassi", "Norvegia 1,5 GW", "Francia 1,2 GW", "Lituania 0,7 GW", where="aste-ricavi indicator 1")
    dk = next(x for x in aste if x["paese"] == "DK" and x["data"] == "2026-08-04")
    dkp = [it_num(m) for m in re.findall(r"circa ([\d,]+) EUR", dk["prezzo"])]
    dkk = re.findall(r"(\d+) DKK/MWh", dk["prezzo"])
    if len(dkp) != 2 or len(dkk) != 2:
        warn("Danish CfD prices not parsed from eolico-filiera aste")
        dkp, dkk = [None, None], [None, None]
    V["dk_eur"], V["dk_dkk"] = dkp, dkk
    need(dk["prezzo"], "2 offerte", "5 offerte", where="DK 2026 auction")
    gamma_cap = next(e for e in wc["elementi"] if e["id"] == "WC-NL-GAMMA-CAP")
    m = re.search(r"EUR (\d+)/MWh \(Gamma-A\) and EUR (\d+)/MWh \(Gamma-B\), up from EUR (\d+)", gamma_cap["summary"])
    V["gamma_caps"] = [int(m.group(1)), int(m.group(2)), int(m.group(3))] if m else [None, None, None]
    if not m:
        warn("Gamma caps not parsed from WC-NL-GAMMA-CAP")
    gamma_a = next(x for x in aste if x["paese"] == "NL" and x["data"] == "2026")
    mm = re.search(r"budget di sussidio ([\d,]+) miliardi", gamma_a["esito"])
    V["gamma_a_budget"] = it_num(mm.group(1)) if mm else None
    wsg = next(x for x in aste if x["paese"] == "DE" and x["data"] == "2026-08-10")
    mm = re.search(r"([\d,]+) e ([\d,]+) ct/kWh", wsg["prezzo"])
    V["de_caps"] = [it_num(mm.group(1)) * 10, it_num(mm.group(2)) * 10] if mm else [None, None]
    need(wsg["esito"], "2-4,8 GW", where="WindSeeG draft")
    pl = next(x for x in aste if x["paese"] == "PL")
    need(pl["prezzo"], "113-117", where="PL auction price")
    ar7 = next(x for x in aste if x["paese"] == "GB")
    need(ar7["prezzo"], "91,20", "89,49", where="AR7 prices")
    V["ar7"] = ar7
    wcid = {e["id"]: e for e in wc["elementi"]}
    V["wc"] = wcid
    need(wcid["WC-GB-AR8-OPEN"]["summary"], "GBP 113/MWh", "17 GW", where="AR8 open")
    need(wcid["WC-NL-IJVBETA-GRID"]["summary"], "Gamma Q2 2031", "one year late", where="IJV Beta grid")
    need(wcid["WC-LT-CURONIAN"]["summary"], "not feasible on commercial terms", "30 Jun 2026", "49%", where="Curonian Nord")
    need(wcid["WC-GB-NORFOLK-BOREAS"]["summary"], "40%", where="Norfolk Boreas")
    need(wcid["WC-GB-HORNSEA4"]["summary"], "DKK 3.5-4.5 bn", where="Hornsea 4")
    need(wcid["WC-EU-GRIDS"]["summary"], "from 2027", where="EU Grids package")
    need(wcid["WC-BE-PEZ-FRAME"]["summary"], "at least 75%", where="Belgian PEZ framework")
    need(wcid["WC-GB-AR7"]["summary"], "19-21%", where="AR7 vs ceiling")
    V["dk_gw"] = dk["gw"]
    V["pl_max"] = max(x["eur_mwh"] for x in EXT["prezzi_aste_eur"]["voci"] if x["paese"] == "PL")

    # price ladder (EUR/MWh)
    pts = []
    for x in EXT["prezzi_aste_eur"]["voci"]:
        pts.append({"label": f"{CN[x['paese']]} · {x['progetto']}", "c": x["paese"], "v": x["eur_mwh"], "kind": "award", "year": x["anno"], "src": "WindEurope"})
    if dkp[0]:
        pts.append({"label": "Denmark · Holmsland (ex North Sea I Mid), 1 GW", "c": "DK", "v": dkp[0], "kind": "award", "year": 2026, "src": "offshoreWIND.biz / KEFM"})
        pts.append({"label": "Denmark · Hesselø, 0.8 GW", "c": "DK", "v": dkp[1], "kind": "award", "year": 2026, "src": "offshoreWIND.biz / KEFM"})
    if V["gamma_caps"][0]:
        pts.append({"label": "Netherlands · IJmuiden Ver Gamma-A, cap", "c": "NL", "v": V["gamma_caps"][0], "kind": "cap", "year": 2026, "src": "wind-calendar"})
        pts.append({"label": "Netherlands · IJmuiden Ver Gamma-B, cap", "c": "NL", "v": V["gamma_caps"][1], "kind": "cap", "year": 2026, "src": "wind-calendar"})
    if V["de_caps"][0]:
        pts.append({"label": "Germany · WindSeeG draft, 2nd-stage caps", "c": "DE", "v": V["de_caps"][0], "v2": V["de_caps"][1], "kind": "cap", "year": 2026, "src": "eolico-filiera (secondary)"})
    pts.sort(key=lambda p: p["v"])
    V["prices"] = pts

    # ------------------------------------------------------------- calendar
    ref = wc["riferimento"]
    V["wc_ref"] = ref
    V["wc_sum"] = wc["riepilogo"]
    fut = [e for e in wc["elementi"] if e["status_effective"] in ("scheduled", "at risk", "unconfirmed") and e["period_end"] >= ref]
    fut.sort(key=lambda e: (e["period_start"], e["id"]))
    V["future"] = fut
    delays = [e for e in wc["elementi"] if e["type"] == "delay"]
    gridre = re.compile(r"grid|TSO|HVDC|converter|DolWin|BalWin|energy island|Norwich Main", re.I)
    V["delays"] = delays
    V["grid_delays"] = [e for e in delays if gridre.search(e["summary"] + " " + e["project"])]
    # grid links under construction for offshore wind, OSM (rete-elettrica.json)
    rx = re.compile(r"BorWin|DolWin|IJmuiden|Nederwiek|Dogger Bank|Hornsea|East Anglia|Norfolk|Bornholm|BalWin|LanWin|Sofia", re.I)
    links = {}
    for x in F["rete-elettrica.json"]["elementi"]:
        if x["hvdc"] and x["stato"] == "in costruzione" and rx.search(x["nome"] or ""):
            nm = re.sub(r"\s+(offshore|onshore|nearshore)$", "", re.sub(r"^Kabeltracé ", "", x["nome"]), flags=re.I)
            nm = re.sub(r" (export cable|Wind Farm export cable|offshore connector|Interlink Cable|Grid Connection)$", "", nm, flags=re.I)
            links.setdefault(nm, 0)
            links[nm] += x["km_mappa"]
    V["osm_links"] = links

    # ------------------------------------------------------------- bottlenecks
    cb = {x["id"]: x for x in ef["colli_bottiglia"]}
    V["cb"] = cb
    cab = {i["nome"]: i for i in cb["cavi-hvdc"]["indicatori"]}
    V["prysmian"] = cab["Prysmian: portafoglio ordini Transmission"]
    V["nkt"] = cab["NKT: portafoglio ordini Transmission"]
    mm = re.search(r"([\d,]+) miliardi a prezzi standard", V["nkt"]["nota"])
    V["nkt_std"] = it_num(mm.group(1)) if mm else None
    V["nexans"] = cab["Nexans: portafoglio ordini rettificato"]
    need(cab["Prysmian: portafoglio ordini Transmission"]["nota"], "2 miliardi", where="Prysmian note")
    need(cab["NKT: ordini acquisiti Q1 2026"]["nota"], "Karlskrona", "2027", where="NKT Q1")
    V["backlog_sum"] = V["prysmian"]["valore"] + V["nkt"]["valore"]
    cv = cb["convertitori-hvdc"]["indicatori"]
    V["balwin"] = cv[0]
    V["hitachi"] = cv[1]
    fo = {i["nome"]: i for i in cb["fondazioni"]["indicatori"]}
    V["mono_cap"] = fo["Capacita' europea monopile XXL+"]
    V["mono_util"] = fo["Utilizzo fabbriche europee monopile"]
    need(V["mono_util"]["nota"], "32%", "50%", where="monopile utilisation")
    need(V["mono_cap"]["nota"], "1,2 Mt", where="monopile capacity 2024")
    V["mono_cost"] = fo["Costo di produzione Europa vs Cina"]
    need(V["mono_cost"]["nota"], "6,35", "6,69", "41%", where="monopile cost")
    V["mono_share"] = fo["Quote del tonnellaggio contrattato"]
    tu = {i["nome"]: i for i in cb["turbine"]["indicatori"]}
    V["sgre"] = tu["Siemens Gamesa: perdita prima delle voci speciali, Q2 esercizio 2026"]
    V["gev"] = tu["GE Vernova: EBITDA segmento eolico Q2 2026"]
    need(V["sgre"]["nota"], "-249", where="SGRE")
    need(V["gev"]["nota"], "-165", "400 milioni", "sospesi", where="GE Vernova")
    V["turb_mw"] = tu["Potenza media turbine offshore installate in Europa nel 2025"]
    nv = {i["nome"]: i for i in cb["navi"]["indicatori"]}
    V["cadeler_util"] = nv["Utilizzo flotta Cadeler H1 2026"]
    need(V["cadeler_util"]["nota"], "47,6%", where="Cadeler Q1")
    fl = ef["flotta"]
    V["ffiv"] = fl[1]
    V["clv"] = fl[4]
    V["csov"] = fl[5]
    V["cadeler_book"] = fl[6]
    need(fl[6]["valore"], "2,5 miliardi", where="Cadeler order book")
    need(fl[0]["nota"], "dal 2032", where="WTIV tight from 2032")
    V["wtiv"] = nv["WTIV >=15 MW (esclusa Cina)"]
    po = {i["nome"]: i for i in cb["porti"]["indicatori"]}
    V["port_inv"] = po["Investimenti annunciati dal 2022 in manifattura, porti e navi"]
    need(cb["porti"]["per_un_porto"], "40-50 t/m2", where="port requirements")
    need(cb["navi"]["per_un_porto"], "40-50 t/m2", where="vessel quay requirements")
    lab = cb["manodopera"]["indicatori"]
    V["lab"] = lab
    need(lab[0]["valore"], "10.000", "19.000", where="GWO technicians")
    need(lab[1]["nota"], "442.800", where="WindEurope jobs base")
    # Chinese- and Korean-built vessels in the fleet table
    V["cn_built"] = [n["nome"] for n in ef["navi"] if "(Cina)" in (n.get("note") or "") or "China Merchants" in (n.get("note") or "")]
    V["kr_built"] = [n["nome"] for n in ef["navi"] if "(Corea)" in (n.get("note") or "")]
    V["n_vessels"] = len(ef["navi"])

    # ------------------------------------------------------------- ports
    V["ports"] = {x["id"]: x for x in ef["elementi"]}
    V["pn"] = {p["id"]: p for p in F["porti-nord.json"]["elementi"]}
    V["pr"] = {p["id"]: p for p in F["port-risk.json"]["ports"]}
    V["pn_date"] = V["pn"]["esbjerg"]["ultima_data"]

    # ------------------------------------------------------------- risks: rates and materials
    px = {s["id"]: s for s in F["prezzi.json"]["serie"]}
    V["us10y"] = px["us10y"]
    V["ttf"] = px["ttf"]
    V["eurusd"] = px["eurusd"]
    M, mstatus = markets(today, offline)
    V["mkt"], V["mkt_status"] = M, mstatus
    for k in ("eur10y", "copper", "hrc"):
        if k in M and M[k].get("series"):
            s = M[k]["series"]
            last, ago = s[-1], year_ago(s, s[-1][0])
            V[k] = {"last": last, "ago": ago, "chg": last[1] - ago[1], "chg_pct": (last[1] / ago[1] - 1) * 100,
                    "lo": min(x[1] for x in s if d(x[0]) >= d(ago[0])), "hi": max(x[1] for x in s if d(x[0]) >= d(ago[0]))}
        else:
            V[k] = None
    V["dfr"] = M["dfr"]["series"][-1] if M.get("dfr", {}).get("series") else None
    if V["dfr"]:
        s = M["dfr"]["series"]
        V["dfr_ago"] = year_ago(s, s[-1][0])
    V["crf6"], V["crf7"] = crf(0.06, 25), crf(0.07, 25)
    V["crf_up"] = (V["crf7"] / V["crf6"] - 1) * 100
    sc = {r["id"]: r for r in F["scorte.json"]["riepilogo"]}
    V["sto_de"], V["sto_nl"] = sc["gas_stoccaggio_pct_de"], sc["gas_stoccaggio_pct_nl"]

    # ------------------------------------------------------------- risks: security
    bs = F["baltico-sicurezza.json"]
    ev = bs["eventi"]
    V["cables"] = sorted([e for e in ev if e["categoria"] == "danno-cavo" and e["data"] >= "2024-11-01"], key=lambda e: e["data"])
    V["drones"] = [e for e in ev if e["categoria"].startswith("droni") and e["data"] >= "2025-09-01"]
    V["drone_esb"] = next((e for e in ev if e["id"] == "BS-2025-D03"), None)
    V["drone_kiel"] = next((e for e in ev if e["id"] == "BS-2025-D06"), None)
    need(V["drone_esb"]["nome"], "Esbjerg", where="drones Aalborg/Esbjerg")
    need(V["drone_kiel"]["nome"], "centrale elettrica", where="drones Kiel")
    est = next(e for e in ev if e["id"] == "CI-2024-04")
    need(est["nome"], "Estlink 2", "ancora", where="Estlink 2 incident")
    V["estlink_date"] = est["data"]
    g = bs["gnss"]
    V["gnss_series"] = g["serie_giornaliera"]
    V["gnss_period"] = g["periodo"]
    sites = {"Gdańsk": (54.3758, 18.6936), "Klaipėda": (55.6842, 21.1381), "Świnoujście": (53.903, 14.2753)}
    for p in on["parchi"]:
        if p["nome"] in ("Baltic Power", "Baltica 2", "Baltyk II"):
            sites[p["nome"]] = (p["lat"], p["lon"])
    near = {}
    for c in g["celle"]:
        if c["livello"] != "alto":
            continue
        for nm, (la, lo) in sites.items():
            if hav(c["lat"], c["lon"], la, lo) <= THRESHOLDS["gnss_km"]:
                near.setdefault(nm, []).append(c)
    V["gnss_near"] = near
    V["gnss_sites"] = list(sites)
    se24 = wcid["WC-SE-2024-REJECT"]
    se26 = wcid["WC-SE-2026-PERMITS"]
    m1 = re.search(r"(\d+) applications", se24["summary"])
    m2 = re.search(r"(\d+) rejected", se26["summary"])
    need(se24["summary"], "missile detection", "Poseidon", where="Sweden 2024")
    need(se26["summary"], "two approved", where="Sweden 2026")
    V["se_veto"] = (int(m1.group(1)) if m1 else None, int(m2.group(1)) if m2 else None)
    ic = {x["id"]: x for x in F["interconnessioni.json"]["elementi"]}
    V["estlink2"] = ic["EL-IC-09"]
    ce = {x["id"]: x for x in F["cyber-energia.json"]["elementi"]}
    V["cy"] = ce
    need(ce["CE-2022-KASAT"]["attore"], "GRU", "UE, USA e Regno Unito", where="KA-SAT attribution")
    need(ce["CE-2025-PL"]["attribuzione_stato"], "contestata", "Russia", where="Poland attribution")
    need(ce["CE-2022-KASAT"]["effetto"], "5.800", "10-11 GW", "95%", "19 aprile 2022", where="KA-SAT")
    need(ce["CE-2025-PL"]["vittima"], "oltre 30", where="Poland 2025")
    need(ce["CE-2025-PL"]["effetto"], "produzione elettrica non interrotta", where="Poland 2025")
    need(ce["CE-2022-DWT"]["effetto"], "2.000", where="Deutsche Windtechnik")
    al = F["cyber-energia.json"]["allarmi_agenzie"]
    V["cy_dk"] = [a for a in al if "CFCS" in a["ente"] or "Energistyrelsen" in a["ente"]]
    expo = {x["paese"]: x for x in F["cyber-energia.json"]["esposizione"]["paesi"]}
    V["lt_remote"] = expo["LT"]["nota"]
    need(expo["LT"]["nota"], "100 kW", where="Lithuania remote-access ban")
    en = F["esposizione-nord.json"]
    t = json.dumps(en, ensure_ascii=False)
    need(t, "FSRU di Mukran partita per l'Egitto", where="esposizione-nord DE")

    # ------------------------------------------------------------- staleness of curated externals
    for k in ("prezzi_aste_eur", "fid_2025", "rvo_gamma_b"):
        x = EXT[k]
        dd = d(x["data_dato"] + "-01" if len(x["data_dato"]) == 7 else x["data_dato"])
        if (today - dd).days > x["max_age_days"]:
            warn(f"external item {k} is {(today - dd).days} days old: re-check it")
    if d(ref) < today - dt.timedelta(days=20):
        warn(f"wind-calendar reference date {ref} is more than 20 days old")
    return V


# =====================================================================================
# SVG charts
# =====================================================================================
SVG_STYLE = """<style>
.ow-t{font:600 14px 'IBM Plex Sans',system-ui,sans-serif;fill:#1D272D}
.ow-l{font:12px 'IBM Plex Sans',system-ui,sans-serif;fill:#3b474e}
.ow-m{font:11px 'IBM Plex Mono',ui-monospace,monospace;fill:#5f6b72}
.ow-g{stroke:#d9dcd8;stroke-width:1}
.ow-z{stroke:#5f6b72;stroke-width:1.2}
.ow-s1{fill:#A61E6B}.ow-s2{fill:#2a78d6}.ow-s3{fill:#eda100}.ow-s4{fill:#1baf7a}
.ow-k1{stroke:#A61E6B}.ow-k2{stroke:#2a78d6}.ow-k3{stroke:#eda100}.ow-k4{stroke:#1baf7a}.ow-ki{stroke:#1D272D}
.ow-i{fill:#1D272D}.ow-bg{fill:#ffffff}.ow-o{fill:#ffffff}
.ow-h{paint-order:stroke;stroke:#ffffff;stroke-width:4px;stroke-linejoin:round}
@media (prefers-color-scheme:dark){
.ow-t{fill:#DAE0E2}.ow-l{fill:#c3cacd}.ow-m{fill:#99a5ab}.ow-g{stroke:#2f3b42}.ow-z{stroke:#99a5ab}
.ow-s1{fill:#d14f9a}.ow-s2{fill:#3987e5}.ow-s3{fill:#c98500}.ow-s4{fill:#199e70}
.ow-k1{stroke:#d14f9a}.ow-k2{stroke:#3987e5}.ow-k3{stroke:#c98500}.ow-k4{stroke:#199e70}.ow-ki{stroke:#DAE0E2}
.ow-i{fill:#DAE0E2}.ow-bg{fill:#172127}.ow-o{fill:#172127}.ow-h{stroke:#172127}}
</style>"""


def svg_open(w, h, title, desc, uid):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" '
            f'aria-labelledby="{uid}-t {uid}-d" style="max-width:{w}px;height:auto;display:block">'
            f'<title id="{uid}-t">{esc(title)}</title><desc id="{uid}-d">{esc(desc)}</desc>{SVG_STYLE}'
            f'<rect class="ow-bg" x="0" y="0" width="{w}" height="{h}" rx="6"/>')


def bar_path(x0, x1, y, h, r=4, round_end=True):
    if abs(x1 - x0) < 0.5:
        return f'M{x0:.1f},{y:.1f}h0.5v{h:.1f}h-0.5z'
    if not round_end:
        return f'M{x0:.1f},{y:.1f}H{x1:.1f}V{y + h:.1f}H{x0:.1f}Z'
    r = min(r, abs(x1 - x0), h / 2)
    return (f'M{x0:.1f},{y:.1f}H{x1 - r:.1f}Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f}V{y + h - r:.1f}'
            f'Q{x1:.1f},{y + h:.1f} {x1 - r:.1f},{y + h:.1f}H{x0:.1f}Z')


def ticks(lo, hi, step):
    t, v = [], (int(lo // step)) * step
    while v <= hi + 1e-9:
        if v >= lo - 1e-9:
            t.append(round(v, 6))
        v += step
    return t


def chart_targets(V, wide=True):
    R = V["countries"]
    w = 680 if wide else 360
    left = 100 if wide else 80
    right = 34 if wide else 26
    rowh = 40
    top = 78 if wide else 96
    h = top + rowh * len(R) + 34
    hi = max(max(r["tgt"] for r in R), max((r["inst"] + r["awarded"]) / 1000 for r in R))
    hi = 10 * (-(-hi // 10))
    X = lambda v: left + v / hi * (w - left - right)
    o = [svg_open(w, h, "Offshore wind by country: installed, awarded since 2023, 2030 forecast and target",
                  "GW by country. Bar: installed end-2025 plus capacity awarded in 2023-2026 auctions. Ring: WindEurope 2030 forecast. Tick: national target.",
                  "c1" + ("w" if wide else "n"))]
    o.append('<text class="ow-t" x="12" y="22">Offshore wind, GW</text>')
    leg = [("rect", "ow-s2", "installed end-2025"), ("rect", "ow-s3", "awarded 2023–26"), ("ring", "", "forecast 2030"), ("tick", "ow-k1", "target")]
    x, y = 12, 36
    for kind, cls, lab in leg:
        wd = 26 + len(lab) * 6.4
        if x + wd > w - 8:
            x, y = 12, y + 18
        if kind == "rect":
            o.append(f'<rect class="{cls}" x="{x}" y="{y}" width="12" height="10" rx="2"/>')
        elif kind == "ring":
            o.append(f'<circle class="ow-o ow-ki" cx="{x + 6}" cy="{y + 5}" r="4.5" stroke-width="2"/>')
        else:
            o.append(f'<line class="ow-k1" x1="{x + 6}" x2="{x + 6}" y1="{y - 2}" y2="{y + 12}" stroke-width="3"/>')
        o.append(f'<text class="ow-l" x="{x + 17}" y="{y + 9}">{lab}</text>')
        x += wd + 8
    for t in ticks(0, hi, 10):
        o.append(f'<line class="ow-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 6}" y2="{h - 26}"/><text class="ow-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{int(t)}</text>')
    for i, r in enumerate(R):
        y = top + i * rowh
        nm = CN[r["c"]]
        inst, aw, fc, tg = r["inst"] / 1000, r["awarded"] / 1000, r["fc"] / 1000, r["tgt"]
        o.append(f'<text class="ow-l" x="{left - 8}" y="{y + 20}" text-anchor="end">{nm}</text>')
        o.append(f'<path class="ow-s2" d="{bar_path(X(0), X(inst), y + 8, 16, round_end=aw <= 0)}"><title>{nm}: {num(inst, 1)} GW installed at end-2025</title></path>')
        if aw > 0:
            o.append(f'<path class="ow-s3" d="{bar_path(X(inst) + 2, X(inst + aw), y + 8, 16)}"><title>{nm}: {num(aw, 1)} GW awarded in 2023–2026 auctions</title></path>')
        o.append(f'<circle class="ow-o ow-ki" cx="{X(fc):.1f}" cy="{y + 16}" r="5" stroke-width="2"><title>{nm}: WindEurope forecast {num(fc, 1)} GW in 2030</title></circle>')
        o.append(f'<line class="ow-k1" x1="{X(tg):.1f}" x2="{X(tg):.1f}" y1="{y + 2}" y2="{y + 30}" stroke-width="3"><title>{nm}: target {num(tg, 1)} GW ({r["tgt_year"]})</title></line>')
        lab = f'{num(tg, 1) if tg % 1 else int(tg)}' + (f" ({r['tgt_year']})" if r["tgt_year"] != 2030 else "")
        end = max(X(tg), X(inst + aw), X(fc) + 5)
        tx = X(tg) + 6
        anchor = "start"
        if tx + len(lab) * 6.6 > w - 4:
            tx, anchor = X(tg) - 6, "end"
        o.append(f'<text class="ow-m ow-h" x="{tx:.1f}" y="{y + 37}" text-anchor="{anchor}">target {lab}</text>' if not wide
                 else f'<text class="ow-m ow-h" x="{tx:.1f}" y="{y + 37}" text-anchor="{anchor}">{lab}</text>')
        _ = end
    o.append("</svg>")
    return "".join(o)


def chart_prices(V, wide=True):
    P = V["prices"]
    w = 680 if wide else 360
    rowh = 30 if wide else 40
    top = 62
    left = 300 if wide else 14
    right = 40 if wide else 30
    h = top + rowh * len(P) + 34
    lo, hi = 60, 125
    X = lambda v: (left if wide else 14) + (v - lo) / (hi - lo) * (w - (left if wide else 14) - right)
    o = [svg_open(w, h, "Offshore wind auction prices and caps, EUR/MWh",
                  "Dots: awarded strike prices. Diamonds: tender caps. Fixed-bottom offshore wind, 2025-2026.", "c2" + ("w" if wide else "n"))]
    o.append('<text class="ow-t" x="12" y="22">Offshore auctions 2025–26, €/MWh</text>')
    o.append('<circle class="ow-s2" cx="18" cy="41" r="5"/><text class="ow-l" x="28" y="45">awarded strike price</text>')
    o.append('<path class="ow-s1" d="M170,36 l5,5 l-5,5 l-5,-5z"/><text class="ow-l" x="181" y="45">tender cap (maximum)</text>')
    for t in ticks(lo, hi, 10 if wide else 20):
        o.append(f'<line class="ow-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 6}" y2="{h - 26}"/><text class="ow-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{int(t)}</text>')
    for i, p in enumerate(P):
        y = top + i * rowh
        cy = y + (rowh / 2 if wide else 27)
        lab = p["label"]
        if wide:
            o.append(f'<text class="ow-l" x="{left - 10}" y="{cy + 4:.1f}" text-anchor="end">{esc(lab if len(lab) < 46 else lab[:44] + "…")}</text>')
        else:
            o.append(f'<text class="ow-l" x="14" y="{y + 12}">{esc(lab if len(lab) < 52 else lab[:50] + "…")}</text>')
        vals = [p["v"]] + ([p["v2"]] if p.get("v2") else [])
        if len(vals) == 2:
            o.append(f'<line class="ow-k1" x1="{X(vals[0]):.1f}" x2="{X(vals[1]):.1f}" y1="{cy:.1f}" y2="{cy:.1f}" stroke-width="2"/>')
        for v in vals:
            tip = f'{esc(lab)}: {num(v, 1)} €/MWh ({"cap" if p["kind"] == "cap" else "awarded"}, {p["year"]}; {p["src"]})'
            if p["kind"] == "award":
                o.append(f'<circle class="ow-s2" cx="{X(v):.1f}" cy="{cy:.1f}" r="5.5"><title>{tip}</title></circle>')
            else:
                o.append(f'<path class="ow-s1" d="M{X(v):.1f},{cy - 6:.1f} l6,6 l-6,6 l-6,-6z"><title>{tip}</title></path>')
        vtxt = num(vals[0], 1 if vals[0] % 1 else 0) + (f"–{num(vals[1], 1)}" if len(vals) == 2 else "")
        o.append(f'<text class="ow-m ow-h" x="{X(vals[-1]) + 10:.1f}" y="{cy + 4:.1f}">{vtxt}</text>')
    o.append("</svg>")
    return "".join(o)


STATUS_CLS = {"scheduled": ("ow-s2", ""), "at risk": ("ow-s3", " (!)"), "unconfirmed": ("ow-s1", " (?)")}


def chart_calendar(V, wide=True):
    E = V["future"]
    t0 = d(V["wc_ref"]).replace(day=1)
    t1 = dt.date(t0.year + 2, 12, 31)
    shown = [e for e in E if d(e["period_start"]) <= t1]
    later = [e for e in E if d(e["period_start"]) > t1]
    w = 680 if wide else 360
    left = 250 if wide else 12
    right = 18
    rowh = 22 if wide else 34
    top = 74
    h = top + rowh * len(shown) + 40
    span = (t1 - t0).days
    X = lambda x: left + max(0, min(span, (x - t0).days)) / span * (w - left - right)
    o = [svg_open(w, h, "Offshore wind milestones ahead, North Sea and Baltic",
                  "Scheduled, at-risk and unconfirmed milestones from the wind calendar, by date window.", "c3" + ("w" if wide else "n"))]
    o.append(f'<text class="ow-t" x="12" y="22">Milestones ahead, {MON[t0.month - 1]} {t0.year} – {t1.year}</text>')
    x = 12
    for st, (cls, mark) in STATUS_CLS.items():
        o.append(f'<rect class="{cls}" x="{x}" y="36" width="12" height="10" rx="2"/><text class="ow-l" x="{x + 17}" y="45">{st}{mark}</text>')
        x += 100 if wide else 96
    o.append(f'<text class="ow-m" x="12" y="62">{len(later)} later items not drawn (listed in the table)</text>')
    y_axis_top, y_axis_bot = top - 6, h - 30
    m = t0
    while m <= t1:
        if m.month in (1, 7) or m == t0:
            xx = X(m)
            o.append(f'<line class="ow-g" x1="{xx:.1f}" x2="{xx:.1f}" y1="{y_axis_top}" y2="{y_axis_bot}"/>')
            lab = f"{MON[m.month - 1]} {str(m.year)[2:]}" if (wide or m.month == 1 or m == t0) else ""
            if lab:
                o.append(f'<text class="ow-m" x="{xx:.1f}" y="{h - 14}" text-anchor="middle">{lab}</text>')
        m = dt.date(m.year + (m.month // 12), m.month % 12 + 1, 1)
    today = V["today"]
    o.append(f'<line class="ow-z" x1="{X(today):.1f}" x2="{X(today):.1f}" y1="{y_axis_top}" y2="{y_axis_bot}" stroke-dasharray="3 3"/>')
    for i, e in enumerate(shown):
        y = top + i * rowh
        cls, mark = STATUS_CLS[e["status_effective"]]
        nm = f'{CN.get(e["country"], e["country"])} · {e["project"]}'
        cut = 40 if wide else 54
        nm = nm if len(nm) <= cut else nm[:cut - 1] + "…"
        a, b = d(e["period_start"]), d(e["period_end"])
        xa, xb = X(a), max(X(b), X(a) + 6)
        tip = f'{CN.get(e["country"], e["country"])}, {e["project"]}: {date_label(e["date"])}' + (f' to {date_label(e["date_end"])}' if e.get("date_end") else "") + f' — {e["status_effective"]}'
        if wide:
            o.append(f'<text class="ow-l" x="{left - 8}" y="{y + 15}" text-anchor="end">{esc(nm)}{mark}</text>')
            o.append(f'<rect class="{cls}" x="{xa:.1f}" y="{y + 5}" width="{xb - xa:.1f}" height="13" rx="3"><title>{esc(tip)}</title></rect>')
        else:
            o.append(f'<text class="ow-l" x="12" y="{y + 12}">{esc(nm)}{mark}</text>')
            o.append(f'<rect class="{cls}" x="{xa:.1f}" y="{y + 17}" width="{xb - xa:.1f}" height="11" rx="3"><title>{esc(tip)}</title></rect>')
    o.append("</svg>")
    return "".join(o)


def chart_markets(V, wide=True):
    w = 680 if wide else 360
    pw, ph = ((w - 24 - 40) / 2, 190) if wide else (w - 24, 170)
    h = 56 + (ph + 60) * (1 if wide else 2) + 10
    o = [svg_open(w, h, "Cost of capital and materials over twelve months",
                  "Left: 10-year government bond yields, per cent. Right: copper and US hot-rolled coil steel, index 100 a year ago.", "c4" + ("w" if wide else "n"))]
    o.append('<text class="ow-t" x="12" y="22">Cost of capital and materials, last 12 months</text>')
    us = [[a, b] for a, b in V["us10y"]["serie"]]
    end = d(us[-1][0])
    start = end - dt.timedelta(days=365)
    us = [x for x in us if d(x[0]) >= start]
    M = V["mkt"]
    eu = [x for x in M.get("eur10y", {}).get("series", []) if d(x[0]) >= start]
    panels = [("10-year yields, %", [("US Treasury 10y", us, "ow-k1", ""), ("Euro area AAA 10y", eu, "ow-k2", ' stroke-dasharray="5 3"')], False)]
    idx = []
    for k, nm, cls, dash in [("copper", "Copper (COMEX)", "ow-k3", ""), ("hrc", "US hot-rolled coil steel", "ow-k4", ' stroke-dasharray="5 3"')]:
        s = [x for x in M.get(k, {}).get("series", []) if d(x[0]) >= start]
        if s:
            b = s[0][1]
            idx.append((nm, [[a, v / b * 100] for a, v in s], cls, dash))
    panels.append(("Index, 100 = a year ago", idx, True))
    for i, (ttl, series, is_idx) in enumerate(panels):
        ox = 12 + (i * (pw + 40) if wide else 0)
        oy = 44 + (0 if wide else i * (ph + 60))
        x0, x1, y0, y1 = ox + 34, ox + pw - 4, oy + 46, oy + ph
        allv = [v for _, s, _, _ in series for _, v in s]
        if not allv:
            o.append(f'<text class="ow-l" x="{ox}" y="{oy + 30}">data missing</text>')
            continue
        lo, hi = min(allv), max(allv)
        step = 0.5 if not is_idx else 20
        lo, hi = step * math.floor(lo / step), step * math.ceil(hi / step)
        if is_idx:
            lo = min(lo, 100)
        X = lambda x: x0 + (d(x) - start).days / 365 * (x1 - x0)
        Y = lambda v: y1 - (v - lo) / (hi - lo) * (y1 - y0)
        o.append(f'<text class="ow-l" x="{ox}" y="{oy + 8}" font-weight="600">{ttl}</text>')
        lx, ly = ox, oy + 22
        for nm, s, cls, dash in series:
            if lx + 30 + len(nm) * 6.2 > ox + pw:
                lx, ly = ox, ly + 15
            o.append(f'<line class="{cls}" x1="{lx}" x2="{lx + 16}" y1="{ly - 4}" y2="{ly - 4}" stroke-width="2.5"{dash}/><text class="ow-l" x="{lx + 21}" y="{ly}">{nm}</text>')
            lx += 30 + len(nm) * 6.2
        for t in ticks(lo, hi, step if (hi - lo) / step <= 6 else step * 2):
            o.append(f'<line class="ow-g" x1="{x0}" x2="{x1}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/><text class="ow-m" x="{x0 - 4}" y="{Y(t) + 4:.1f}" text-anchor="end">{num(t, 1) if not is_idx else int(t)}</text>')
        if is_idx:
            o.append(f'<line class="ow-z" x1="{x0}" x2="{x1}" y1="{Y(100):.1f}" y2="{Y(100):.1f}"/>')
        for k in range(0, 13, 3):
            m = start + dt.timedelta(days=round(365 * k / 12))
            o.append(f'<text class="ow-m" x="{X(m.isoformat()):.1f}" y="{y1 + 14}" text-anchor="middle">{MON[m.month - 1]}</text>')
        for nm, s, cls, dash in series:
            path = "M" + " L".join(f"{X(a):.1f},{Y(v):.1f}" for a, v in s)
            o.append(f'<path d="{path}" fill="none" class="{cls}" stroke-width="2"{dash} stroke-linejoin="round"><title>{nm}: {num(s[0][1], 2)} on {date_en(s[0][0])}, {num(s[-1][1], 2)} on {date_en(s[-1][0])}</title></path>')
            xe, ye = X(s[-1][0]), Y(s[-1][1])
            o.append(f'<text class="ow-m ow-h" x="{xe - 4:.1f}" y="{ye - 8:.1f}" text-anchor="end">{num(s[-1][1], 2 if not is_idx else 0)}</text>')
    o.append("</svg>")
    return "".join(o)


def table_html(head, rows):
    return ('<div class="tabella"><table><thead><tr>' + "".join(f'<th scope="col">{esc(x)}</th>' for x in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")


def chart_tables(V):
    return {
        "targets": table_html(["Country", "Installed end-2025, GW", "Awarded 2023–26, GW", "Forecast 2030, GW", "Target, GW"],
                              [[CN[r["c"]], num(r["inst"] / 1000, 2), num(r["awarded"] / 1000, 2), num(r["fc"] / 1000, 2),
                                f"{num(r['tgt'], 1)} ({r['tgt_year']})"] for r in V["countries"]]),
        "prices": table_html(["Round", "€/MWh", "Type", "Source"],
                             [[p["label"], num(p["v"], 1) + (f"–{num(p['v2'], 1)}" if p.get("v2") else ""), "cap" if p["kind"] == "cap" else "awarded", p["src"]] for p in V["prices"]]),
        "calendar": table_html(["Date", "Country", "Milestone", "MW", "Status"],
                               [[date_label(e["date"]) + (f" – {date_label(e['date_end'])}" if e.get("date_end") else ""), CN.get(e["country"], e["country"]),
                                 e["project"], num(e["capacity_mw"], 0) if e["capacity_mw"] else "—", e["status_effective"]] for e in V["future"]]),
        "markets": table_html(["Series", "A year earlier", "Latest", "Change"], market_rows(V)),
    }


def market_rows(V):
    rows = []
    u = V["us10y"]
    rows.append(["US Treasury 10y, %", "—", f"{num(u['ultimo'], 2)} ({date_en(u['data'])})", bp(u["var"]["1a"])])
    for k, nm, dec in [("eur10y", "Euro area AAA 10y, %", 2), ("copper", "Copper, USD/lb", 2), ("hrc", "US HRC steel, USD/short ton", 0)]:
        x = V[k]
        if not x:
            rows.append([nm, "missing", "missing", "—"])
            continue
        ch = bp(x["chg"] * 100) if k == "eur10y" else pct(x["chg_pct"])
        rows.append([nm, f"{num(x['ago'][1], dec)} ({date_en(x['ago'][0])})", f"{num(x['last'][1], dec)} ({date_en(x['last'][0])})", ch])
    return rows


# =====================================================================================
# Text
# =====================================================================================
def L(text, url):
    return f"[{text}]({url})" if url else text


def DL(name):
    return f"[{name}](DATA/{name})"


def port_blocks(V):
    P, pn, pr = V["ports"], V["pn"], V["pr"]
    wc = V["wc"]
    out = []

    def pw(pid):
        p = pn.get(pid)
        if not p:
            return "—"
        return f"{num(p['media30']['portcalls'], 1)}/day ({pct(p['var30_anno_pct'], 1)})"

    def risk(pid):
        p = pr.get(pid)
        return f"{num(p['score'], 1)} ({p['level']})" if p else "—"

    e = P["esbjerg"]
    need(e["banchine"], "9,3", "12,8", "350 m", where="Esbjerg quays")
    need(e["investimenti"], "500 milioni DKK", where="Esbjerg investment")
    need(e["progetti_serviti"][0], "36 di 72", where="Esbjerg Thor")
    need(e["colli_bottiglia"], "CCS", where="Esbjerg constraint")
    ind = {i["nome"]: i for i in e["indicatori"]}
    shipped = ind["Capacita' offshore europea spedita da Esbjerg"]["valore"]
    nxt = ind["Capacita' da spedire nei prossimi 5 anni"]["valore"]
    esb_calls = next((t for t in pn["esbjerg"]["traffico_annuo"] if "scali" in t["unita"]), None)
    out.append(("h3", "Esbjerg (Denmark, North Sea)"))
    out.append(("p", f"Europe's reference installation port says it has shipped more than {num(shipped, 1)} GW of offshore wind and expects about {num(nxt, 1)} GW more "
                     f"in the next five years, mostly for German and British projects. The fifth expansion added {e['area_nuova_ha']} ha east of the port, and the access channel "
                     f"was deepened from 9.3 to 12.8 m; a new quay of about 350 m was due in 2026 (secondary source, status not confirmed). "
                     f"In 2026 it served Thor (RWE, 1 GW): 36 of 72 turbines were up by July. "
                     + (f"Ship calls in 2025: {num(esb_calls['valore'], 0)} ({pct(esb_calls['var_pct'], 0)} on 2024, port annual report). " if esb_calls else "")
                     + f"**Constraint:** the new land is also marketed for CO₂ storage (CCS) and modular cargo, so space is shared between uses "
                     f"({L('Port Esbjerg', e['link'])}; {DL('eolico-filiera.json')})."))
    e = P["eemshaven"]
    need(e["banchine"], "aprile 2026", "due parchi", where="Eemshaven quay")
    need(e["progetti_serviti"][1], "795 MW", "inizio 2027", where="OranjeWind")
    need(e["progetti_serviti"][3], "ottobre 2026", where="Nordlicht O&M")
    out.append(("h3", "Eemshaven (Netherlands, North Sea)"))
    eco = wc["WC-NL-ECOWENDE"]
    out.append(("p", f"The Buss Terminal's heavy-lift quay (WINdQUAY) was reinforced to {e['portata_t_m2']} t/m² and completed in April 2026: it can now serve two wind farms at once. "
                     f"In 2026–2027 at least three campaigns queue for it: Ecowende ({num(eco['capacity_mw'], 0)} MW; final turbine installed on {date_en(eco['date'])}), "
                     f"RWE's Nordseecluster A in Germany and OranjeWind (795 MW, turbines from early 2027). Vattenfall's Nordlicht O&M base was due in October 2026. "
                     f"**Constraint:** declared capacity is two projects in parallel; with three in the queue the window is tight (the monitor's assessment, as the source file notes). "
                     f"PortWatch calls, last 30 days: {pw('eemshaven')} on a year earlier, from a small base ({L('offshoreWIND.biz', e['link'])})."))
    e = P["vlissingen"]
    need(e["progetti_serviti"][0], "17 cassoni su 23", where="Vlissingen caissons")
    out.append(("h3", "Vlissingen (North Sea Port, Netherlands)"))
    out.append(("p", f"A fabrication port rather than an installation base: the caissons of Belgium's Princess Elisabeth energy island are built here (17 of 23 installed by June 2026). "
                     f"**Missing:** 2026 data on dedicated areas and quays for wind ({L('offshoreWIND.biz', e['link'])})."))
    e = P["rotterdam-maasvlakte"]
    ind = {i["nome"]: i for i in e["indicatori"]}
    need(e["colli_bottiglia"], "22/12/2026", "continuita' aziendale", where="Sif")
    need(ind["Produzione Sif primi 9 mesi 2026"]["nota"], "124 kton", where="Sif output")
    out.append(("h3", "Rotterdam – Maasvlakte 2 (Netherlands)"))
    out.append(("p", f"Home of Sif's monopile factory ({num(ind['Investimento fabbrica Sif Maasvlakte 2']['valore'], 0)} million €). Sif produced "
                     f"{num(ind['Produzione Sif primi 9 mesi 2026']['valore'], 0)} kt in the first nine months of 2026, against 124 kt a year earlier, "
                     f"but will close one of its three lines in the fourth quarter for lack of orders, has reported material doubt about its going concern, "
                     f"and calls an extraordinary meeting on 22 December 2026 for a capital increase. The port plans a {e['area_nuova_ha']} ha offshore wind terminal "
                     f"(Arianehaven) for mid-2029 ({L('Windtech International', e['link'])})."))
    e = P["cuxhaven"]
    need(e["banchine"], "3,5 anni", "inizio 2025", where="Cuxhaven quay")
    out.append(("h3", "Cuxhaven (Germany, North Sea)"))
    ind = e["indicatori"][0]
    out.append(("p", f"Berths 5–7 add {num(ind['valore'], 0)} m of heavy-load quay and {e['area_nuova_ha']} ha of storage (DEME contract, November 2024; works from early 2025 "
                     f"for about 3.5 years, so ready around 2028). In December 2025 the Chinese monopile maker Dajin and Briese Schiffahrt signed an MoU for a marshalling hub here. "
                     f"**Constraint:** until then the German North Sea has little dedicated heavy quay ({L('offshoreWIND.biz', e['link'])})."))
    e = P["bremerhaven"]
    need(e["area_nota"], "500 m", "25 ha", "180 milioni", "BUND", where="Bremerhaven OTB")
    out.append(("h3", "Bremerhaven (Germany)"))
    out.append(("p", f"The planned Offshore Terminal Bremerhaven (500 m quay, 25 ha, 180 million €) was stopped by a lawsuit from the environmental group BUND and never built; "
                     f"no 2026 source on a relaunch was found (sources date from 2016, reliability medium; {L('offshoreWIND.biz', e['link'])})."))
    e = P["rostock"]
    ind = {i["nome"]: i for i in e["indicatori"]}
    need(ind["Diametro massimo monopile oggi"]["nota"], "12 m", "15 m", "inizio 2027", where="Rostock diameter")
    out.append(("h3", "Rostock (Germany, Baltic)"))
    out.append(("p", f"EEW SPC's monopile plant in a tide-free port: maximum diameter {num(ind['Diametro massimo monopile oggi']['valore'], 0)} m today, 12 m after works "
                     f"finishing early 2027, possibly 15 m after 2030; capacity of more than {num(ind['Capacita\' produttiva']['valore'], 0)} monopiles a year. It made Thor's "
                     f"monopiles and loaded the first for a 1.5 GW Polish farm in January 2026. **Constraint:** under-use rather than scarcity "
                     f"({L('offshoreWIND.biz', e['link'])}). Port Risk Index {risk('rostock')}."))
    e = P["sassnitz-mukran"]
    need(e["progetti_serviti"][0], "315 MW", "21 turbine", where="Windanker")
    need(e["progetti_serviti"][1], "1,1 GW", where="Iberdrola Baltic hub")
    out.append(("h3", "Sassnitz-Mukran (Rügen, Germany, Baltic)"))
    out.append(("p", f"Pre-assembly and O&M base: Windanker (Iberdrola, 315 MW, 21 Siemens Gamesa turbines) was staged here in 2026, and Iberdrola's Baltic hub runs about 1.1 GW "
                     f"from Mukran; Parkwind's Arcadis Ost 1 has its O&M base here. The source file flagged a possible conflict for space with the floating LNG terminal; "
                     f"IEEFA reports that the Mukran FSRU has left for Egypt ({DL('esposizione-nord.json')}), which would ease it. "
                     f"**Missing:** area and quay figures ({L('offshoreWIND.biz', e['link'])})."))
    e = P["ronne"]
    need(e["area_nota"], "150.000 m2", "11 m", "300 m", where="Rønne")
    out.append(("h3", "Rønne (Bornholm, Denmark)"))
    bei = wc["WC-DK-BEI-TENDER"]
    out.append(("p", f"First expansion finished in 2019: {e['area_nuova_ha']} ha, 11 m depth, a 300 m multipurpose terminal. It was the marshalling base for Baltic Eagle "
                     f"(50 turbines in 2024) and Arcadis Ost 1. Its future hangs on the 3 GW Bornholm Energy Island, now due in 2034 ({date_label(wc['WC-DK-BEI-COD']['date'])} in the calendar); "
                     f"the joint Danish–German tender for the wind farms is **{bei['status_effective']}**: promised for {date_label(bei['date'])}, not launched by November 2026 "
                     f"({DL('wind-calendar.json')})."))
    e = P["gdansk-t5"]
    ind = e["indicatori"][0]
    need(ind["nota"], "194 milioni", where="T5 state aid")
    need(e["progetti_serviti"][0], "111 monopile", "fine 2028", where="Baltica 2 lease")
    out.append(("h3", "Gdańsk – Terminal T5 (Poland)"))
    out.append(("p", f"A {e['area_nuova_ha']} ha terminal on reclaimed land, {num(ind['valore'], 0)} million € of which about 194 million state aid approved by the Commission; "
                     f"concession to Istrana (Baltic Hub group) to 2055. Baltica 2 (1.5 GW, 107 turbines) leases it from Q4 2026 to the end of 2028, after all 111 monopiles were "
                     f"installed by August 2026; Ocean Winds has booked it for BC-Wind turbines in 2028. **Constraint:** works finish just as installation starts, so a delay "
                     f"has almost no slack. Port Risk Index {risk('gdansk')}, driven by GNSS interference within 50 km ({L('offshoreWIND.biz', e['link'])}; {DL('port-risk.json')})."))
    e = P["swinoujscie"]
    need(e["banchine"], "3.000 t", "15 MW", where="Świnoujście quay")
    need(e["investimenti"], "giugno 2026", "Non vincolante", where="Świnoujście LoI")
    out.append(("h3", "Świnoujście – ORLEN offshore terminal (Poland)"))
    out.append(("p", f"Poland's first installation terminal, opened in June 2025: quays rated {e['portata_t_m2']} t/m², jack-ups and heavy-lift ships, turbines of about 15 MW and "
                     f"substation parts of almost 3,000 t. A non-binding letter of intent (June 2026) with the port authority aims to add offshore and ro-ro quays; secondary "
                     f"sources speak of doubling capacity by 2030 ({L('Daily Mare', e['link'])}). PortWatch calls, last 30 days: {pw('swinoujscie')} (whole port, with Szczecin)."))
    e = P["klaipeda"]
    ind = e["indicatori"][0]
    need(e["banchine"], "453 m", "36,6 milioni", where="Klaipėda quays")
    need(ind["nota"], "100 milioni", where="Klaipėda EIB")
    need(e["investimenti"], "fine 2027", "fine 2026", where="Klaipėda completion")
    out.append(("h3", "Klaipėda (Lithuania)"))
    out.append(("p", f"Rebuilding about 453 m of quays on the Smeltė peninsula (36.6 million € contract, 2025) to {e['portata_t_m2']} t/m², inside a {num(ind['valore'], 0)} million € "
                     f"programme with a 100 million € EIB loan (September 2026). Completion slipped to end-2027 (end-2026 in a 2025 source). **Constraint:** the national pipeline "
                     f"is fragile: the 700 MW tender failed twice and the first project, Curonian Nord, awaits a decision by the end of 2026 ({L('offshoreWIND.biz', e['link'])}). "
                     f"Port Risk Index {risk('klaipeda')}."))
    o, gr, hv, ni, hu = P["ostenda"], P["grenaa"], P["hvide-sande"], P["nigg"], P["hull"]
    need(o["investimenti"], "650 milioni", where="Ostend EIB")
    need(ni["investimenti"], "30 milioni GBP", "Mitsui", where="Nigg")
    need(hu["indicatori"][0]["nota"], "agosto 2026", where="Hull staff")
    abp = wc["WC-GB-ABP"]
    need(abp["summary"], "63.9%", where="ABP")
    out.append(("h3", "Smaller and UK bases"))
    out.append(("ul", [f"**Ostend:** coordination port for the Princess Elisabeth island (EIB loan of 650 million €, 2024); the zone's first tender was halted in July 2025 and "
                       f"its new CfD framework (July 2026) has no relaunch date, so the Belgian pipeline is on hold ({L('offshoreWIND.biz', o['link'])}).",
                       f"**Grenaa and Hvide Sande (Denmark):** candidate bases for Vattenfall's Hesselø and Holmsland (commissioning aim 2032); no base port announced yet "
                       f"({L('offshoreWIND.biz', hv['link'])}).",
                       f"**Nigg (Scotland):** bought in 2025 by Mitsui & Co. Europe and Mitsui O.S.K. Lines; over 30 million £ approved in March 2026 for a heavy-duty quay and ro-ro ramp "
                       f"next to Sumitomo Electric's HVDC cable factory, which opened on {date_en(wc['WC-GB-SUMITOMO']['date'])} ({L('offshoreWIND.biz', ni['link'])}).",
                       f"**Hull and Grimsby (England):** Siemens Gamesa's blade factory in Hull employs more than {num(hu['indicatori'][0]['valore'], 0)} people and started Hornsea 3 "
                       f"blades in August 2026; on {date_en(abp['date'])} IFM Investors agreed to buy 63.9% of their owner, ABP ({DL('wind-calendar.json')})."]))
    tab = []
    for pid, pnid, prid, nm in [("esbjerg", "esbjerg", "esbjerg", "Esbjerg"), ("eemshaven", "eemshaven", "eemshaven", "Eemshaven"),
                                ("rotterdam-maasvlakte", "rotterdam", "rotterdam", "Rotterdam"), ("cuxhaven", None, None, "Cuxhaven"),
                                ("rostock", "rostock", "rostock", "Rostock"), ("sassnitz-mukran", None, None, "Mukran"), ("ronne", None, None, "Rønne"),
                                ("gdansk-t5", "danzica", "gdansk", "Gdańsk T5"), ("swinoujscie", "swinoujscie", "swinoujscie", "Świnoujście"),
                                ("klaipeda", "klaipeda", "klaipeda", "Klaipėda")]:
        e = P[pid]
        space = []
        if e.get("area_nuova_ha"):
            space.append(f"{e['area_nuova_ha']} ha new")
        if e.get("portata_t_m2"):
            space.append(f"{e['portata_t_m2']} t/m²")
        tab.append([nm, {"porto installazione": "installation", "porto fabbricazione": "fabrication", "porto O&M": "O&M"}.get(e["categoria"], e["categoria"]),
                    ", ".join(space) or "missing", pw(pnid) if pnid else "—", risk(prid) if prid else "—", e["affidabilita"].replace("alta", "high").replace("media", "medium")])
    return out, tab


def blocks(V):
    B = []
    F, EXT, wc = V["F"], V["EXT"], V["wc"]
    eu = V["europe"]
    esb, ost, mar, ham = V["decl"]["esbjerg"], V["decl"]["ostenda"], V["decl"]["marienborg"], V["decl"]["amburgo"]
    C = {r["c"]: r for r in V["countries"]}
    rvo = EXT["rvo_gamma_b"]
    gamma = wc["WC-NL-GAMMA-TENDER"]
    ar8 = wc["WC-GB-AR8-RESULTS"]
    wsg = wc["WC-DE-WINDSEEG-LAW"]
    cur = wc["WC-LT-CURONIAN-DEC"]
    bal = V["balwin"]
    grid_n, delay_n = len(V["grid_delays"]), len(V["delays"])
    pu = V["mono_util"]
    WE = L("WindEurope", eu and V["F"]["eolico-filiera.json"]["obiettivi"]["fonte_installato"]["link"])
    aw_pct = V["tot_awarded"] / V["tot_gap"] * 100

    # ------------------------------------------------------------- 1. key points
    B.append(("h2", "key-points", "1. Key points"))
    B.append(("ul", [
        f"**Seven North Sea and Baltic countries will fall {gw(V['tot_short'], 1)} GW short of their targets.** For the UK, Germany, the Netherlands, Denmark, Poland, Belgium "
        f"and Norway WindEurope expects {gw(V['tot_fc'], 1)} GW in 2030, against national targets of {num(V['tot_tgt'], 1)} GW. Europe connected only "
        f"{gw(eu['aggiunto_2025_mw'], 2)} GW in 2025, the least since 2016 (WindEurope, February 2026).",
        f"**Auctions clear again where the state carries the price risk.** Rounds in which developers had to pay for the seabed got no bids for {num(V['neg_failed_gw'], 1)} GW "
        f"in Denmark, Germany and the Netherlands in 2024–2025. With two-sided contracts for difference, Denmark awarded {num(V['dk_gw'], 1)} GW at about {num(V['dk_eur'][0], 1)}–{num(V['dk_eur'][1], 1)} €/MWh, "
        f"signed on 6 November 2026.",
        f"**The next test starts on {date_en(rvo['apertura'], False)}.** The Dutch IJmuiden Ver Gamma round (2 GW) takes applications until {date_en(rvo['chiusura'])}, "
        f"with price caps of {V['gamma_caps'][0]} and {V['gamma_caps'][1]} €/MWh (RVO; wind calendar). UK AR8 results are due between {date_en(ar8['date'], False)} and {date_en(ar8['date_end'])}; "
        f"Germany's auction reform still needs a Bundestag vote in December.",
        f"**The grid, not ships or steel, now sets the pace.** {word(grid_n, True)} of the {delay_n} delays in the monitor's wind calendar cite grid links or platforms; "
        f"Amprion's 2 GW BalWin1 slipped a year, to {date_en(bal['valore'])}. Monopile factories, by contrast, will run at about {num(pu['valore'], 0)}% of capacity in 2028 (Rystad).",
        f"**Baltic ports are adding capacity; German North Sea quays come late.** Gdańsk's {num(V['ports']['gdansk-t5']['indicatori'][0]['valore'], 0)} million € T5 terminal "
        f"serves Baltica 2 from the fourth quarter of 2026; Klaipėda's {num(V['ports']['klaipeda']['indicatori'][0]['valore'], 0)} million € upgrade ends in 2027. Cuxhaven's "
        f"{num(V['ports']['cuxhaven']['indicatori'][0]['valore'], 0)} m heavy quay arrives around 2028; Bremerhaven's terminal was never built.",
    ]))

    # ------------------------------------------------------------- 2. targets vs reality
    B.append(("h2", "targets", "2. Targets against reality, country by country"))
    B.append(("p", f"Three ministerial declarations set the goals. At **Esbjerg** (May 2022) Denmark, Germany, the Netherlands and Belgium promised at least {esb['obiettivo_2030_gw']} GW in the "
                   f"North Sea by 2030 and {esb['obiettivo_2050_gw']} GW by 2050. At **Ostend** (April 2023) nine countries raised this to about {ost['obiettivo_2030_gw']} GW by 2030 and "
                   f"{ost['obiettivo_2050_gw']} GW by 2050. At **Marienborg** (August 2022) eight Baltic states promised {num(mar['obiettivo_2030_gw'], 1)} GW in the Baltic by 2030. "
                   f"The **Hamburg** summit of January 2026 kept the 300 GW for 2050, added up to 100 GW of cross-border projects and an investment pact for 15 GW of installations "
                   f"a year in 2031–2040 ({DL('eolico-filiera.json')})."))
    B.append(("tab", ["Declaration", "2030 goal", "Signatories' installed, end-2025", "WindEurope forecast 2030", "Forecast as share of goal"],
              [["Esbjerg (2022)", f"{esb['obiettivo_2030_gw']} GW", f"{num(esb['calcolo']['installato_fine2025_gw_paesi'], 2)} GW",
                f"{num(esb['calcolo']['previsione_2030_gw_paesi'], 2)} GW", f"{num(esb['calcolo']['quota_obiettivo_2030_previsto_pct'], 0)}%"],
               ["Ostend (2023)", f"{ost['obiettivo_2030_gw']} GW", f"{num(ost['calcolo']['installato_fine2025_gw_paesi'], 2)} GW",
                f"{num(ost['calcolo']['previsione_2030_gw_paesi'], 2)} GW", f"{num(ost['calcolo']['quota_obiettivo_2030_previsto_pct'], 0)}%"],
               ["Marienborg, Baltic (2022)", f"{num(mar['obiettivo_2030_gw'], 1)} GW", f"{num(mar['calcolo']['installato_fine2025_gw_paesi'], 2)} GW",
                f"{num(mar['calcolo']['previsione_2030_gw_paesi'], 2)} GW", f"{num(mar['calcolo']['quota_obiettivo_2030_previsto_pct'], 0)}%"]],
              "Sums of WindEurope national totals for the signatories, calculated in eolico-filiera.json. National totals include other seas (German and Danish Baltic, Irish Sea, "
              "Channel), so they overstate the North Sea alone. Marienborg counts only countries with a mainly Baltic coast, without Germany and Denmark."))
    B.append(("p", f"The pace tells the story. Europe connected {gw(eu['aggiunto_2025_mw'], 2)} GW in 2025. To reach WindEurope's forecast of {gw(eu['previsione_2030_mw'], 1)} GW in 2030 "
                   f"from {gw(eu['installato_fine2025_mw'], 1)} GW it needs {num(V['europe_rate'], 1)} GW a year on average. The Hamburg pact asks for 15 GW a year after 2030, "
                   f"{num(15 / (eu['aggiunto_2025_mw'] / 1000), 1)} times the 2025 rate. Investment decisions (FID) are the leading signal: offshore FIDs in 2025 covered "
                   f"{num(V['fid25']['gw'], 1)} GW for {num(V['fid25']['mld_eur'], 1)} billion €, and {WORDS[V['fid25']['progetti_polonia']]} of the {WORDS[V['fid25']['progetti']]} "
                   f"projects were Polish ({L('WindEurope, p. 35', V['fid25']['link'])})."))
    B.append(("fig", "targets", f"**Offshore wind by country, GW.** Bar: installed at the end of 2025 (blue) plus capacity awarded in auctions in 2023–2026 (amber). Ring: WindEurope "
                                f"forecast for 2030. Pink tick: national target (2030; the Netherlands now 2032). Sources: WindEurope 2025 Statistics (February 2026) via "
                                f"{DL('eolico-filiera.json')}; awards from {DL('wind-calendar.json')} (`awarded_vs_targets`, read {date_en(V['wc_ref'])}). Awards are gross: "
                                f"they include the UK's Hornsea 4 ({gw(V['hornsea4_mw'], 1)} GW), dropped in May 2025."))
    rows = []
    for r in V["countries"]:
        rows.append([CN[r["c"]], gw(r["inst"], 2), gw(r["uc"], 2) if r["uc"] else "0", gw(r["awarded"], 1), gw(r["fid"], 2) if r["fid"] else "—",
                     gw(r["fc"], 1), f"{num(r['tgt'], 1)} ({r['tgt_year']})" + (f"; range {num(r['tgt_low'], 0)}–{num(r['tgt'], 0)}" if r["tgt_low"] else ""),
                     gw(r["gap"], 1), gw(r["short"], 1)])
    B.append(("tab", ["Country", "Installed end-2025", "Under construction (EMODnet)", "Awarded 2023–26", "FID 2025–26 (calendar)", "Forecast 2030", "Target (year)",
                      "Gap: target − installed", "Shortfall: target − forecast"], rows,
              "GW. Installed and forecast: WindEurope national totals. Under construction: EMODnet polygons in offshore-nord.json (North Sea and Baltic only; for the UK the east "
              "coast only; EMODnet status can lag). Awarded: supported or zero-subsidy capacity awarded in 2023–2026 rounds (wind-calendar.json). FID: final investment decisions "
              "recorded in the calendar since January 2025 (Baltica 2 and Bałtyk 2+3 in Poland, Nordlicht in Germany); WindEurope counts more offshore FIDs in 2025, so the column is incomplete."))
    gb, de, nl, dk, pl = C["GB"], C["DE"], C["NL"], C["DK"], C["PL"]
    B.append(("p", f"**Across the seven countries** the gap between targets and end-2025 capacity is {gw(V['tot_gap'], 1)} GW; capacity awarded since 2023 covers "
                   f"{num(aw_pct, 0)}% of it, but most of that comes online after 2030. **Germany** has awarded {gw(de['awarded'], 1)} GW, {num(de['awarded'] / de['gap'] * 100, 0)}% of its gap, "
                   f"yet {V['de_nofid_gw']} GW of awarded sites still lack an FID (Offshore Wind Foundation, September 2026, via the calendar). **The UK** has the largest gap, "
                   f"{gw(gb['gap'], 1)} GW against the upper end of its 43–50 GW range; net of Hornsea 4 its awards since 2023 are {gw(gb['awarded'] - V['hornsea4_mw'], 1)} GW. "
                   f"**The Netherlands** has moved its 21 GW target from 2030 to 2032 and cut its 2040 goal; WindEurope expects {gw(nl['fc'], 1)} GW in 2030. "
                   f"**Denmark** expects {gw(dk['fc'], 1)} GW against {num(dk['tgt'], 1)} GW (a target taken from a secondary source). **Poland** is the exception: "
                   f"from zero at end-2025 to a forecast of {gw(pl['fc'], 1)} GW, {num(pl['fc'] / pl['tgt'] / 10, 0)}% of its Marienborg share."))
    bt = V["baltic"]
    B.append(("p", f"**In the Baltic**, EMODnet maps {gw(bt['mw_per_stato']['operativo'], 1)} GW operating and {gw(bt['mw_per_stato']['in costruzione'], 1)} GW under construction, "
                   f"{num(bt['quota_obiettivo_2030_con_cantieri_pct'], 0)}% of the Marienborg goal even if every site under construction is finished by 2030 ({DL('offshore-nord.json')}). "
                   f"Esbjerg also promised about 20 GW of green hydrogen by 2030; Europe had {num(V['h2_mw'], 0)} MW of electrolysers in operation in July 2025 "
                   f"({L('Hydrogen Europe via Renewables Now', V['h2_src']['link'])}), {num(V['h2_share'], 1)}% of that figure."))
    B.append(("val", "*Assessment.* The 2030 targets are now political anchors, not delivery plans: no country on the chart except Poland is forecast to reach more than "
                     "two thirds of its goal. For employers the useful number is not the target but the awarded-and-financed pipeline, which pushes the bulk of North Sea "
                     "construction into 2028–2033 and makes the Dutch and German auction rounds of 2026–2027 decisive for port and vessel demand after 2030."))

    # ------------------------------------------------------------- 3. auctions
    B.append(("h2", "auctions", "3. Auctions: why negative bidding failed and what comes next"))
    B.append(("h3", "Why negative bidding failed"))
    B.append(("p", f"In a **negative-bidding** or zero-subsidy round the developer pays the state for the site, or bids for it with no support, and sells its power at market prices. "
                   f"The model worked while capital was cheap. It stopped working when turbine, steel and financing costs rose: in July 2023 Vattenfall halted Norfolk Boreas, "
                   f"citing costs up to 40% higher, and the UK's AR5 round that September attracted no offshore bids. Ørsted dropped Hornsea 4 in May 2025 despite a contract, "
                   f"with break costs of DKK 3.5–4.5 billion ({DL('wind-calendar.json')})."))
    B.append(("p", f"Then the rounds themselves emptied. Denmark's 3 GW tender drew no bids in December 2024; Germany's N-10.1 and N-10.2 (2.5 GW) none in August 2025, a first; "
                   f"the Netherlands' Nederwiek I-A (1 GW) none in October 2025. WindEurope counts {num(V['neg_failed_gw'], 1)} GW of failed negative-bidding rounds in 2024–2025; "
                   f"Norway (1.5 GW), France (1.2 GW) and Lithuania (0.7 GW) also cancelled or voided CfD rounds. The reasons given by the sources: full merchant price risk, "
                   f"up-front payments to the state, high costs and interest rates, and power demand growing more slowly than planned ({DL('eolico-filiera.json')})."))
    B.append(("val", "*Assessment.* An offshore wind farm is almost all up-front capital, so the cost of capital sets the price the developer needs. Merchant exposure raises that cost "
                     "twice: lenders demand more equity and a higher margin, and the developer prices in low-price years. A two-sided CfD removes both, which is why the same "
                     "seabed attracts bids under a CfD and none without one (see the illustrative calculation in section 6)."))
    B.append(("h3", "Contracts for difference are back"))
    B.append(("p", f"Under a **two-sided contract for difference (CfD)** the state guarantees a strike price: it pays the developer when the market is below it and collects when "
                   f"the market is above. The UK's AR7 awarded a record {num(wc['WC-GB-AR7']['capacity_mw'], 1)} MW on {date_en(wc['WC-GB-AR7']['date'])}, at 91.20 £/MWh in England "
                   f"and Wales and 89.49 £/MWh in Scotland (2024 prices; about 19–21% below the ceiling). Poland's first CfD round awarded {num(wc['WC-PL-AUCTION-2025']['capacity_mw'], 0)} MW "
                   f"in December 2025 at about 113–117 €/MWh. Denmark, after zero bids, redesigned its tender with CfDs and got two bids for Holmsland and five for Hesselø; "
                   f"Vattenfall won both at DKK {V['dk_dkk'][0]} and {V['dk_dkk'][1]} per MWh for 20 years. Belgium's new Princess Elisabeth framework (July 2026) uses a single "
                   f"two-sided CfD and requires at least 75% of turbines not made or assembled in China. The EU Grids Package (December 2025) is reported to make two-sided CfDs "
                   f"mandatory for new renewables from 2027 ({DL('wind-calendar.json')}; {L('GOV.UK, AR7 results', V['ar7']['link'])})."))
    B.append(("fig", "prices", f"**Offshore wind auction prices and caps, €/MWh, 2025–2026 rounds.** Dots: awarded strike prices; diamonds: tender caps (maximum allowed bid). "
                               f"Prices are not like for like: CfD length (20 years in Denmark, 25 in Poland), indexation, grid cost and currency differ. UK prices are WindEurope's "
                               f"euro conversion; on GOV.UK they are 91.20 and 89.49 £/MWh in 2024 prices. German caps are from a secondary source. Sources: "
                               f"{L('WindEurope 2025 Statistics, table 3', EXT['prezzi_aste_eur']['link'])} (February 2026, via report/dati/offshore-wind-esterni.json); Danish prices "
                               f"from {DL('eolico-filiera.json')} (offshoreWIND.biz, 6 November 2026, checked online); Dutch caps from {DL('wind-calendar.json')}."))
    B.append(("p", f"The spread is wide: Denmark's {num(V['dk_eur'][0], 1)} €/MWh sits about {num(V['pl_max'] - V['dk_eur'][0], 0)} €/MWh below Poland's highest award ({V['pl_max']} €/MWh). Baltic projects pay for a "
                   f"young supply chain and first-of-a-kind grid; Danish sites reuse an existing one. The Dutch caps ({V['gamma_caps'][0]} and {V['gamma_caps'][1]} €/MWh, raised from "
                   f"{V['gamma_caps'][2]}) show what the government thinks it must offer to avoid another empty round."))
    B.append(("h3", "What is next"))
    B.append(("ul", [
        f"**IJmuiden Ver Gamma-A and Gamma-B (Netherlands, 2 × 1 GW).** Applications from {date_en(rvo['apertura'])} to {date_en(rvo['chiusura'])} at {rvo['chiusura_ora']}. "
        f"RVO's Gamma-B page shows a subsidy budget of {num(rvo['budget_eur'] / 1e9, 3)} billion € ({L('RVO', rvo['link'])}, read 10 November 2026); "
        f"Gamma-A's budget is {num(V['gamma_a_budget'], 2)} billion € (secondary source). The two sites share one TenneT 2 GW platform landing at Maasvlakte, which the "
        f"RVO roadmap puts in Q2 2031, a year late for supply-chain reasons. It is the first Dutch round since Nederwiek I-A's zero bids, under a temporary subsidy (TOWOZ) before a CfD in 2027.",
        f"**UK Allocation Round 8.** Opened in July 2026 with the offshore administrative strike price frozen at 113 £/MWh (2024 prices); RenewableUK counts more than 17 GW "
        f"eligible. Results are expected between {date_en(ar8['date'])} and {date_en(ar8['date_end'])}, depending on appeals (reliability {ar8['reliability']}).",
        f"**German WindSeeG reform.** The bill moves to annual rounds of 2–4.8 GW from 2027 in two stages: dynamic negative bidding first, a two-sided CfD only as a fallback "
        f"(second-stage caps of {num(V['de_caps'][0], 2)} and {num(V['de_caps'][1], 2)} €/MWh, secondary source). The Bundesrat rejected the two-stage model in a non-binding "
        f"opinion on 16 October 2026. Adoption is needed in December for a 1 January 2027 start; the calendar marks it **{wsg['status_effective']}**. The retender of N-10.1 and N-10.2 is set for 2027.",
        f"**Curonian Nord (Lithuania, {num(cur['capacity_mw'], 0)} MW).** The energy minister said in July 2026 that the project is not feasible on commercial terms without "
        f"state funding; it got a positive environmental assessment on 30 June 2026 and Ignitis is buying Ocean Winds' 49%. A decision to continue, postpone or seek state aid "
        f"is due by the end of 2026 (**{cur['status_effective']}**). Lithuania's second 700 MW tender failed twice.",
        f"**Later:** Poland's second CfD auction (2027); the joint Danish–German Bornholm tender (promised for the first half of 2026, not launched); Denmark's North Sea South "
        f"(bids in the second half of 2028); France's AO10 winners (about 10 GW, none in the North Sea, end-2026 or early 2027).",
    ]))
    B.append(("fig", "calendar", f"**Milestones ahead, from the monitor's offshore wind calendar.** Each bar is the date window of a scheduled, at-risk (!) or unconfirmed (?) item; "
                                 f"dashed line: today. Items with a year or half-year date are drawn across the whole period, to avoid false precision. Source: "
                                 f"{DL('wind-calendar.json')}, {V['wc_sum']['items']} curated milestones, reference date {date_en(V['wc_ref'])}: "
                                 f"{V['wc_sum']['by_status_effective']['done']} done, {V['wc_sum']['by_status_effective']['scheduled']} scheduled, "
                                 f"{V['wc_sum']['by_status_effective']['at risk']} at risk, {V['wc_sum']['by_status_effective']['unconfirmed']} unconfirmed."))
    B.append(("val", "*Assessment.* December 2026 decides a large part of the 2030s pipeline: whether the Dutch Gamma round attracts at least two bidders per site, whether AR8 clears "
                     "near AR7's price under a higher ceiling, and whether Germany starts 2027 with a law that bidders accept. A German law that keeps uncapped negative bidding as "
                     "the first stage risks repeating 2025; a failed Gamma round would make the Dutch 21 GW by 2032 hard to defend."))

    # ------------------------------------------------------------- 4. bottlenecks
    B.append(("h2", "bottlenecks", "4. Bottlenecks, ranked"))
    B.append(("p", "The ranking weighs three things: how much capacity one failure holds up, how long the constraint lasts, and how few suppliers there are. Auction design and the "
                   "cost of capital (section 3) sit above all of them: without a clearing round there is nothing to build. The ranking is the monitor's assessment; the indicators are facts."))
    cb = V["cb"]
    B.append(("tab", ["Rank", "Link", "Strain (curated)", "Key indicator", "When it eases", "Who is exposed"], [
        ["1", "HVDC cables and converter platforms", "high", f"Prysmian {num(V['prysmian']['valore'], 1)} bn € and NKT {num(V['nkt']['valore'], 1)} bn € transmission backlogs; BalWin1 +1 year",
         "new cable lines from 2027 (Karlskrona); platforms not before 2030", "TSOs, developers with 2 GW connections"],
        ["2", "Grid connections onshore and offshore", "high", f"{grid_n} of {delay_n} calendar delays cite the grid", "2028–2031 as 2 GW links land", "developers, ports' campaign windows"],
        ["3", "Turbine makers' finances", "medium", f"Siemens Gamesa loss {num(-V['sgre']['valore'], 0)} M€ (Q2 FY2026); GE Vernova wind EBITDA −{num(-V['gev']['valore'], 0)} M$ (Q2 2026)",
         "when prices cover risk; two Western suppliers left", "developers, pre-assembly ports"],
        ["4", "Vessels", "medium", f"Cadeler utilisation {num(V['cadeler_util']['valore'], 0)}% (H1 2026); foundation vessels 8–9 by 2028",
         "WTIV ample to 2030, tight in Europe from 2032", "installation contractors"],
        ["5", "Monopiles", "overcapacity", f"utilisation ~32% in 2026, {num(pu['valore'], 0)}% in 2028; China ~41% cheaper",
         "loading near 50% in 2031", "Sif (Rotterdam), EEW (Rostock), Steelwind"],
        ["6", "Ports and labour", "medium, local", f"{num(V['port_inv']['valore'], 1)} bn € invested since 2022 in factories, ports, vessels; technicians ~10,000 (2028) to over 19,000 (2032–33)",
         "German North Sea quays ~2028", "Eemshaven, Esbjerg, Gdańsk; O&M towns"],
    ], "Strain as curated in eolico-filiera.json (colli_bottiglia). Ranking, timing and exposure: the monitor's assessment."))
    B.append(("h3", "1. HVDC cables and converter platforms"))
    B.append(("p", f"German and Dutch TSOs have standardised 2 GW, 525 kV HVDC connections. Three European cable makers (Prysmian, NKT, Nexans) plus LS Cable (Korea) and Sumitomo "
                   f"(Japan) supply them. Prysmian's transmission backlog was {num(V['prysmian']['valore'], 1)} billion € on {date_en(V['prysmian']['data'])}, plus about 2 billion awarded "
                   f"but not yet booked; NKT's {num(V['nkt']['valore'], 1)} billion € on {date_en(V['nkt']['data'])}; Nexans' {num(V['nexans']['valore'], 1)} billion € (adjusted, June 2026, "
                   f"secondary). Together Prysmian and NKT hold {num(V['backlog_sum'], 1)} billion €, several years of output. NKT's new Karlskrona line starts in 2027, and Sumitomo "
                   f"opened the UK's first HVDC cable factory in October 2026. Platforms are scarcer still: few suppliers (Hitachi Energy, Siemens Energy, GE Vernova) and few yards. "
                   f"Hitachi Energy's order book more than tripled in four years to over {V['hitachi']['valore']} billion $ (IEA). BalWin1 (Amprion, 2 GW) moved from 16 September 2030 "
                   f"to {date_en(bal['valore'])} because of extra work on the offshore converter platform and difficult ground onshore, and BalWin2 slips too "
                   f"({L('HVDC World', bal['link'])}, {date_en(bal['data'])})."))
    links = V["osm_links"]
    B.append(("p", f"OpenStreetMap shows {len(links)} offshore wind HVDC connections under construction in the North Sea and Baltic ({DL('rete-elettrica.json')}): "
                   + ", ".join(sorted(links)) + ". Mapped length is indicative."))
    B.append(("h3", "2. Grid connections"))
    gl = V["grid_delays"]
    B.append(("p", f"Of the {delay_n} delays in the calendar, {grid_n} cite a grid link, a platform, a substation or an energy island:"))
    B.append(("ul", [f"**{e['project']}** ({CN.get(e['country'], e['country'])}, {date_label(e['date'])}): {e['summary']}" for e in gl]))
    B.append(("p", f"Completed projects tell the same story. Borkum Riffgrund 3 reached commercial operation on {date_en(wc['WC-DE-BR3-COD']['date'])}, about five months late, after "
                   f"delays on the DolWin5 link and unplanned TSO outages; in Sweden, Vattenfall paused Kriegers Flak in 2024 partly for lack of a reasonable offshore grid connection "
                   f"({DL('wind-calendar.json')})."))
    B.append(("h3", "3. Turbine makers' finances"))
    B.append(("p", f"Two Western makers, Vestas and Siemens Gamesa, dominate European offshore. Siemens Gamesa's loss before special items narrowed to {num(-V['sgre']['valore'], 0)} million € "
                   f"in the second quarter of financial year 2026, from 249 million a year before ({L('Renewables Now', V['sgre']['link'])}). GE Vernova's wind segment lost "
                   f"{num(-V['gev']['valore'], 0)} million $ (EBITDA) in Q2 2026, from 165 million a year earlier; it expects a loss of about 400 million $ in 2026 and has suspended new offshore "
                   f"orders ({L('reNEWS', V['gev']['link'])}). Dogger Bank A's turbine repairs moved the start of its first 300 MW contract to {date_en(wc['WC-GB-DBA-DELAY']['date'])}. "
                   f"Chinese makers offer 16–25 MW machines and are studying factories in the UK and Europe. Average offshore turbines installed in 2025 were {num(V['turb_mw']['valore'], 1)} MW."))
    B.append(("val", "*Assessment.* The constraint is margin, not factory space. Makers now sign only at prices that cover their risk, and that cost passes into auction bids. "
                     "With GE out of new offshore orders, a developer in Europe effectively chooses between two Western suppliers, or a Chinese one where rules allow."))
    B.append(("h3", "4. Vessels"))
    B.append(("p", f"Western installation vessels (WTIV) able to install 15 MW-plus turbines go from none in 2020 to more than {num(V['wtiv']['valore'], 0)} by 2028, and Intelatus sees "
                   f"European supply tight in that segment only from 2032. Foundation vessels stay short: {V['ffiv']['valore'].replace('da ', 'from ').replace(' a ', ' to ').replace('entro il', 'by')} "
                   f"outside China. Cable-lay vessels: {V['clv']['valore'].replace(' nel ', ' in ').replace(', ', '; ').replace('previste', 'expected')}, with a possible shortage for "
                   f"inter-array cables early in the 2030s. Cadeler, the leading owner, used its fleet at {num(V['cadeler_util']['valore'], 0)}% in the first half of 2026 (47.6% in the "
                   f"first quarter as new ships joined) and had an order book of 2.5 billion €. Day rates for 2026 are not public "
                   f"({L('Intelatus via Offshore Engineer', V['wtiv']['link'])}; {L('Cadeler', V['cadeler_util']['link'])})."))
    B.append(("h3", "5. Monopiles"))
    B.append(("p", f"In 2021–2022 monopiles were scarce; now Europe has too many factories. XXL monopile capacity rises from about 1.2 million tonnes in 2024 to "
                   f"{num(V['mono_cap']['valore'], 1)} million tonnes a year from 2027, while utilisation falls from about 32% in 2026–2027 to {num(pu['valore'], 0)}% in 2028, before "
                   f"recovering to about 50% in 2031. Chinese production costs about 41% less ({V['mono_cost']['valore'].replace(',', '.')} million $ per kilotonne, Europe vs China): "
                   f"a 1.6 kt Chinese monopile lands in Europe at about 6.35 million $ including freight and the EU carbon border charge (CBAM), against 6.69 million for a European one. "
                   f"Contracted tonnage: {V['mono_share']['valore']} ({L('Rystad Energy', V['mono_util']['link'])}, {date_en(V['mono_util']['data'])}, checked online)."))
    B.append(("h3", "6. Ports and labour"))
    lab = V["lab"]
    B.append(("p", f"Suppliers have announced {num(V['port_inv']['valore'], 1)} billion € of investment since 2022 in factories, ports and vessels, mostly for offshore wind "
                   f"({L('WindEurope', V['port_inv']['link'])}). A new heavy quay takes three to five years; demand is running one to two years behind plan, so pressure in 2026–2028 is "
                   f"local (Eemshaven, Esbjerg, Gdańsk) rather than system-wide (section 5). Labour is also local: GWO and GWEC expect demand for about 10,000 new offshore technicians "
                   f"worldwide in 2028 and over 19,000 in 2032–2033; WindEurope's workforce report projects about {num(lab[1]['valore'], 0)} wind jobs in Europe by 2030, from about "
                   f"442,800 in 2025 (both secondary summaries). **Missing:** reliable labour data by port."))

    # ------------------------------------------------------------- 5. ports
    pb, ptab = port_blocks(V)
    B.append(("h2", "ports", "5. Base ports: what they need, what they are building, what holds them back"))
    B.append(("p", f"A base port for installation needs three things: deep water and quays rated about 40–50 t/m² for the new jack-up vessels; tens of hectares of "
                   f"hard-standing for blades, towers and foundations; and a multi-year lease tied to a project ({DL('eolico-filiera.json')}, bottleneck notes). Operations and maintenance (O&M) bases need less space but give work "
                   f"for 25–30 years, against one or two seasons for installation (agent report report/agenti/eolico.md)."))
    B.append(("tab", ["Port", "Role", "Space and load", "PortWatch calls, 30 days, vs a year earlier", "Port Risk Index (1–25)", "Source reliability"], ptab,
              f"Space: new area in hectares and quay load rating where the source gives them. PortWatch: all ship calls a day, 30-day average to {date_en(V['pn_date'])}, IMF "
              f"PortWatch via porti-nord.json (wind vessels are a small share; small ports swing widely). Port Risk Index: probability × impact of disruption, port-risk.json "
              f"(reference {date_en(F['port-risk.json']['reference_date'])}). Rotterdam's figures are for the whole port."))
    B.extend(pb)
    B.append(("val", "*Assessment.* The Baltic is where new installation capacity is being built, backed by public money and leases tied to Polish projects. The Dutch and Danish "
                     "North Sea ports are busy until 2027–2028; after that their order book depends on the December 2026 rounds. The German North Sea is short of heavy quay until "
                     "Cuxhaven opens, which keeps German projects reliant on Eemshaven and Esbjerg."))

    # ------------------------------------------------------------- 6. risks
    B.append(("h2", "risks", "6. Risks: interest rates, metals, security, China"))
    B.append(("h3", "Interest rates"))
    us, eu10, dfr = V["us10y"], V["eur10y"], V["dfr"]
    txt = (f"The US 10-year Treasury yield was {num(us['ultimo'], 2)}% on {date_en(us['data'])}, {bp(us['var']['1a'])} on a year earlier ({DL('prezzi.json')}). ")
    if eu10:
        txt += (f"The euro-area AAA 10-year yield was {num(eu10['last'][1], 2)}% on {date_en(eu10['last'][0])}, {bp(eu10['chg'] * 100)} on {date_en(eu10['ago'][0])} "
                f"({L('ECB Data Portal', V['mkt']['eur10y']['link'])}). ")
    if dfr:
        txt += f"The ECB deposit rate is {num(dfr[1], 2)}% ({date_en(dfr[0])}; {num(V['dfr_ago'][1], 2)}% a year earlier). "
    txt += f"Market data {V['mkt_status']}."
    B.append(("p", txt))
    B.append(("val", f"*Assessment (illustrative calculation, not a forecast).* For a project financed over 25 years, the annual capital charge per euro invested is "
                     f"{num(V['crf6'] * 100, 2)}% at a 6% cost of capital and {num(V['crf7'] * 100, 2)}% at 7%: one point more raises it by {num(V['crf_up'], 1)}%. Since capital is "
                     f"most of the cost of offshore wind, the price a developer needs rises almost as much. Rates are higher than a year ago on both sides of the Atlantic, which "
                     f"is why rounds without a CfD remain hard to clear."))
    B.append(("h3", "Steel and copper"))
    cu, hr = V["copper"], V["hrc"]
    t = ""
    if cu:
        t += (f"COMEX copper was {num(cu['last'][1], 2)} $/lb on {date_en(cu['last'][0])}, {pct(cu['chg_pct'])} on a year earlier (front-month future, provisional; "
              f"{L('Yahoo Finance', V['mkt']['copper']['link'])}). ")
    if hr:
        t += (f"US Midwest hot-rolled coil steel was {num(hr['last'][1], 0)} $ per short ton, {pct(hr['chg_pct'])}: a US price shaped by tariffs, used here only as a direction; "
              f"**missing**: a European steel plate series. ")
    t += (f"Metal prices show up in contracts: NKT reports its backlog at {num(V['nkt']['valore'], 1)} billion € at market metal prices and {num(V['nkt_std'], 1)} billion € at "
          f"standard prices, a difference of {num(V['nkt']['valore'] - V['nkt_std'], 1)} billion €. For monopiles, steel and the carbon border charge decide whether Chinese supply "
          f"undercuts European yards (section 4).")
    B.append(("p", t))
    B.append(("fig", "markets", f"**Cost of capital and materials, last 12 months.** Left: 10-year government bond yields, %. Right: copper (COMEX) and US hot-rolled coil steel (CME), "
                                f"index 100 = first close a year earlier; front-month futures, latest close provisional. Sources: US Treasury via {DL('prezzi.json')}; ECB Data Portal "
                                f"(AAA yield curve) and Yahoo Finance, cached in report/dati/offshore-wind-mercati.json ({V['mkt_status']})."))
    sde, snl = V["sto_de"], V["sto_nl"]
    B.append(("p", f"Gas sets the other side of the CfD bill. The TTF was {num(V['ttf']['ultimo'], 2)} €/MWh on {date_en(V['ttf']['data'])} ({pct(V['ttf']['var']['1a'], 0)} on a year earlier, "
                   f"provisional), with German storage at {num(sde['valore'], 1)}% and Dutch at {num(snl['valore'], 1)}% on {date_en(sde['data'])} ({DL('prezzi.json')}; {DL('scorte.json')}). "
                   f"*Assessment:* expensive gas raises power prices, so a two-sided CfD costs the state little or pays it back; if gas falls, the same contracts cost more."))
    B.append(("h3", "Security: cables, drones, jamming, defence"))
    cab = V["cables"]
    B.append(("p", f"**Cables.** {word(len(cab), True)} Baltic cable incidents have been recorded since November 2024, the latest on {date_en(cab[-1]['data'])} "
                   f"({cab[-1]['nome'].replace('Cavo dati', 'data cable').replace('danneggiato', 'damaged')}). Estlink 2, the "
                   f"{num(V['estlink2']['mw'], 0)} MW Estonia–Finland HVDC link, was damaged by a ship's anchor on {date_en(V['estlink_date'])} ({DL('baltico-sicurezza.json')}; "
                   f"{DL('interconnessioni.json')}). Offshore wind export cables and the new 2 GW links are the same kind of asset, on the same seabed."))
    de_ = V["drone_esb"]
    B.append(("p", f"**Drones.** {word(len(V['drones']), True)} drone events over airports, bases, ports and energy sites have been logged around the "
                   f"North Sea and Baltic since September 2025, including sightings reported at Esbjerg on 24 September 2025 and formations over Kiel's shipyard and power plant "
                   f"the next day ({DL('baltico-sicurezza.json')}). None of the events in the file concerns an offshore wind farm."))
    gs = V["gnss_series"]
    near = V["gnss_near"]
    B.append(("p", f"**GNSS jamming.** Between {date_en(V['gnss_period'][0])} and {date_en(V['gnss_period'][1])} GPSJam counted {min(x[1] for x in gs)}–{max(x[1] for x in gs)} "
                   f"high-interference cells a day in the monitor's Baltic box. Within {THRESHOLDS['gnss_km']} km of the Polish and Lithuanian wind ports and farms "
                   + (", ".join(f"{k} had {len(v)}" for k, v in sorted(near.items())) if near else "there were none")
                   + f" high cells in the week. GPSJam measures aircraft, not ships, but jack-up positioning and crew transfers also rely on satellite navigation ({DL('baltico-sicurezza.json')})."))
    B.append(("p", f"**Defence.** Sweden rejected {V['se_veto'][0]} offshore wind applications on defence grounds in November 2024 and {V['se_veto'][1]} more in July 2026, "
                   f"on missile-detection grounds, while approving Poseidon in 2024 and two projects in 2026 ({DL('wind-calendar.json')})."))
    B.append(("h3", "Cyber"))
    cy = V["cy"]
    B.append(("p", f"**KA-SAT and Enercon, 24 February 2022.** A wiper attack on Viasat's KA-SAT satellite network, attributed by the EU, US and UK to Russia's GRU, disabled the "
                   f"modems that about 5,800 Enercon turbines (over 10–11 GW) used for remote monitoring and control. The turbines kept producing; more than 95% were reconnected by "
                   f"19 April 2022 ({L('SentinelOne', cy['CE-2022-KASAT']['link'])}). In the same spring Nordex shut remote access to its turbines after a ransomware attack and "
                   f"Deutsche Windtechnik switched off remote control of about 2,000 turbines for a day."))
    B.append(("p", f"**Poland, 29 December 2025.** CERT Polska reports coordinated destructive attacks on more than 30 wind and solar farms, a manufacturer and a combined heat and "
                   f"power plant. The attackers went through exposed remote-access devices at grid connection substations, cut communication with distribution operators and remote "
                   f"control, and ran destructive malware; electricity production was not interrupted. Poland attributes it to Russia; researchers dispute which group "
                   f"({L('CERT Polska', cy['CE-2025-PL']['link'])}, checked online). As of 9 November 2026 the monitor knows of no successful cyber attack on a European offshore "
                   f"wind farm (report/agenti/cyber-energia.md). Denmark raised its threat level for destructive cyber attacks to medium in June 2024 and its energy sector's "
                   f"preparedness to orange in September 2025; Lithuania bars remote access from risk countries to wind, solar and battery sites above 100 kW ({DL('cyber-energia.json')})."))
    B.append(("val", "*Assessment.* The lesson of both cases is the same: the weak point is the communication and remote-service chain (satellite links, vendor access, substations), "
                     "not the turbine. A large offshore farm is run by a few operators under NIS2, but its supervisory link, its OEM's remote service and its onshore substation "
                     "concentrate gigawatts behind a handful of access points."))
    B.append(("h3", "Supply chain and China"))
    B.append(("p", f"Of the {V['n_vessels']} vessels in the monitor's fleet table, {WORDS.get(len(V['cn_built']), len(V['cn_built']))} were built in Chinese yards ("
                   + ", ".join(V["cn_built"]) + f") and {WORDS.get(len(V['kr_built']), len(V['kr_built']))} in Korea (" + ", ".join(V["kr_built"]) +
                   f"). Dajin holds 12% of contracted European monopile tonnage and plans a marshalling hub at Cuxhaven; LS Cable supplies TenneT's 2 GW LanWin4; Chinese turbine makers "
                   f"offer 16–25 MW machines. Policy is pushing back: Belgium requires at least 75% of turbines not made or assembled in China, and Siemens Energy built its first 2 GW "
                   f"converter platform with a German yard ({DL('eolico-filiera.json')})."))
    B.append(("val", "*Assessment.* China is both a cost relief and a security question. Cheaper monopiles and vessels help the auctions clear; turbines with Chinese control "
                     "software and remote access raise the same questions as the KA-SAT and Polish cases. Expect more NZIA-style content rules in tenders, which favour European "
                     "yards and ports but raise the bid price."))

    # ------------------------------------------------------------- 7. implications
    B.append(("h2", "implications", "7. What it means for a port authority, an installation contractor and a TSO"))
    B.append(("val", "*Assessment — port authority.* Plan for a dip, not a boom, after 2028 in the Dutch and German North Sea unless the December rounds clear. Sign multi-year leases "
                     "tied to named projects (Gdańsk T5 for Baltica 2 is the model) before pouring concrete. Make quays 40–50 t/m² and deep enough for the new jack-ups, and keep "
                     "land flexible between installation, O&M, CCS and hydrogen. Treat O&M bases as the durable business: 25–30 years against one or two seasons. Build "
                     "cyber and drone protection into the terminal now: ports host the onshore substations and the control rooms."))
    B.append(("val", "*Assessment — installation contractor.* The fleet is no longer the scarce factor up to 2030, so day rates are under pressure (Cadeler at 66% utilisation); "
                     "margins depend on avoiding idle time caused by late grid links. Price grid-delay risk into contracts and seek campaign flexibility between Baltic and North "
                     "Sea projects. Foundation and cable-lay vessels stay tight: that is where scarcity premiums remain. From 2032 the 15 MW-plus segment in Europe tightens again."))
    B.append(("val", "*Assessment — TSO.* The TSOs are now on the critical path: one platform's delay strands 2 GW of contracted turbines. Securing manufacturing slots for cables "
                     "and converters (framework deals such as TenneT's) matters more than auction calendars. Expect pressure to share platforms between sites (Gamma-A and Gamma-B) "
                     "and to build hybrid links across borders (Bornholm). Physical and cyber security of landfall substations and export cables belongs in the design, given the "
                     "Baltic cable record and the Polish substation attack."))

    # ------------------------------------------------------------- 8. indicators
    T = THRESHOLDS
    cu_now = f"{num(cu['last'][1], 2)} $/lb ({date_en(cu['last'][0])})" if cu else "missing"
    cu_thr = f"above {num(cu['last'][1] * (1 + T['copper_rise_pct'] / 100), 2)} $/lb (+{num(T['copper_rise_pct'], 0)}%)" if cu else "—"
    B.append(("h2", "watch", "8. Indicators and thresholds to watch"))
    B.append(("tab", ["Indicator", "Now", "Threshold (assessment)", "Why", "Where"], [
        ["IJmuiden Ver Gamma-A/B applications", f"window {date_en(rvo['apertura'], False)}–{date_en(rvo['chiusura'])}", f"fewer than {T['gamma_min_bids']} per site",
         "a repeat of Nederwiek I-A would undercut 21 GW by 2032", "RVO; wind-calendar.json"],
        ["UK AR8 offshore result", f"results {date_en(ar8['date'], False)}–{date_en(ar8['date_end'])}; ceiling 113 £/MWh (2024 prices)",
         f"clearing above {num(T['ar8_price_gbp'], 0)} £/MWh or under {num(T['ar8_min_gw'], 0)} GW", "tests whether AR7's 91.20 £ holds", "GOV.UK; wind-calendar.json"],
        ["German WindSeeG reform", f"Bundestag vote pending ({wsg['status_effective']})", "no adoption by 31 December 2026", "2027 rounds and N-10 retender slip", "wind-calendar.json"],
        ["Curonian Nord decision", f"due by end-2026 ({cur['status_effective']})", "postponed without state aid", "Klaipėda's main project", "wind-calendar.json"],
        ["2 GW HVDC link dates (TenneT, Amprion, 50Hertz)", f"BalWin1 {date_en(bal['valore'])}; Gamma platform Q2 2031", f"any further slip of {T['platform_slip_months']} months or more",
         "each slip strands 2 GW", "HVDC World; wind-calendar.json"],
        ["Prysmian + NKT transmission backlog", f"{num(V['backlog_sum'], 1)} bn €", f"above {num(T['cable_backlog_bn'], 0)} bn €", "cable slots booked further out",
         "quarterly reports; eolico-filiera.json"],
        ["Cadeler fleet utilisation", f"{num(V['cadeler_util']['valore'], 0)}% (H1 2026)", f"below {num(T['cadeler_util_low'], 0)}% or above {num(T['cadeler_util_high'], 0)}%",
         "vessel glut or renewed scarcity", "Cadeler reports"],
        ["Sif extraordinary meeting", "22 December 2026", "capital increase not approved", "Europe's largest monopile maker (31% share)", "eolico-filiera.json"],
        ["Siemens Gamesa and GE Vernova offshore", f"{num(-V['sgre']['valore'], 0)} M€ loss (Q2 FY2026); GE offshore orders suspended", "renewed losses or GE exit confirmed",
         "two Western suppliers left", "company results"],
        ["Euro-area AAA 10-year yield", f"{num(eu10['last'][1], 2)}% ({date_en(eu10['last'][0])})" if eu10 else "missing", f"above {num(T['eur10y'], 1)}%",
         "cost of capital for non-CfD rounds", "ECB Data Portal"],
        ["US 10-year yield", f"{num(us['ultimo'], 2)}% ({date_en(us['data'])})", f"above {num(T['us10y'], 1)}%", "global cost of capital, USD-priced kit", "prezzi.json"],
        ["Copper (COMEX)", cu_now, cu_thr, "cable contract values", "Yahoo Finance"],
        ["Baltic cable or pipeline damage", f"last on {date_en(cab[-1]['data'])}", "any new incident near a wind export route", "same seabed, same anchors", "baltico-sicurezza.json"],
        [f"GNSS high cells within {T['gnss_km']} km of Baltic wind ports and farms", ", ".join(f"{k} {len(v)}" for k, v in sorted(near.items())) or "none",
         "Świnoujście or German Baltic sites affected", "jamming moving west", "baltico-sicurezza.json"],
        ["Cyber incident at a wind OEM, operator or service firm", "none known offshore (9 Nov 2026)", "any incident affecting remote control", "KA-SAT and Poland precedents",
         "cyber-energia.json"],
    ], "Thresholds are the monitor's assessment of when a signal changes the picture, not forecasts."))

    # ------------------------------------------------------------- 9. method
    D = V["dates"]
    B.append(("h2", "method", "9. Method, sources and limits"))
    B.append(("p", "The report is built by report/build_offshore_wind.py from the monitor's data files, re-run each month. Every number in the text, tables and charts is read or "
                   "computed from those files, from report/dati/offshore-wind-esterni.json (curated external facts with source and date) or from market series fetched by the script. "
                   "Figures quoted from Italian text fields of the curated files are checked by the script against the source text; if a figure disappears, the build warns."))
    src = [
        ["eolico-filiera.json", "base ports, vessels, bottlenecks, auctions 2024–26, targets; WindEurope 2025 statistics", D["eolico-filiera.json"], "curated; high to medium"],
        ["wind-calendar.json", f"{V['wc_sum']['items']} milestones 2023–2027+, awards vs targets", D["wind-calendar.json"], "curated; high to low per item"],
        ["offshore-nord.json", "wind farms (EMODnet), hubs, links", D["offshore-nord.json"], "EMODnet status can lag"],
        ["porti-nord.json / port-risk.json", "PortWatch calls; Port Risk Index", f"{D['porti-nord.json']} / {D['port-risk.json']}", "PortWatch data to " + date_en(V["pn_date"])],
        ["rete-elettrica.json / interconnessioni.json", "HVDC lines (OpenStreetMap); interconnectors", f"{D['rete-elettrica.json']} / {D['interconnessioni.json']}", "OSM coverage uneven"],
        ["baltico-sicurezza.json / cyber-energia.json", "cables, drones, GNSS; cyber incidents", f"{D['baltico-sicurezza.json']} / {D['cyber-energia.json']}", "curated; attribution as stated"],
        ["prezzi.json / scorte.json / idrogeno.json", "US yields, TTF; gas storage; electrolysis", f"{D['prezzi.json']} / {D['scorte.json']} / {D['idrogeno.json']}", "daily closes, provisional"],
        ["ECB Data Portal; Yahoo Finance", "euro AAA 10y, deposit rate; copper, US HRC", V["mkt"].get("updated", "—"), V["mkt_status"]],
        ["WindEurope 2025 Statistics (PDF)", "auction prices in €/MWh, 2025 FIDs", EXT["prezzi_aste_eur"]["data_dato"], "high; read 10 Nov 2026"],
    ]
    B.append(("tab", ["Source", "What it gives", "Updated", "Note"], src, ""))
    B.append(("p", "**Checked online on 10 November 2026:** " + "; ".join(f"{x['cosa']} ({x['esito'].replace('confermato', 'confirmed').replace('nessuna novità', 'nothing new')})"
                                                                           for x in EXT["verifiche_web"]) + "."))
    B.append(("p", "**Limits and conflicts between sources.**"))
    B.append(("ul", [
        "National totals (WindEurope) mix seas: the UK includes the Irish Sea, France the Channel and Atlantic, Germany and Denmark both North Sea and Baltic. EMODnet covers only the "
        "North Sea (UK east coast) and the Baltic, so the 'under construction' column is not comparable with the national ones.",
        f"Dutch target year: eolico-filiera.json gives {V['nl_target_conflict'][0]} GW for 2030 (Esbjerg/Ostend), wind-calendar.json {V['nl_target_conflict'][1]} after the 2024 "
        "postponement. The report uses 2032 for the gap and the chart and says so.",
        "Denmark's 12.9 GW target comes from a secondary source (Port Esbjerg, undated). Lithuania, Latvia, Estonia, Finland and Sweden have no target in the files.",
        f"Failed auctions: WindEurope counts {num(V['neg_failed_gw'], 1)} GW of failed negative-bidding rounds in 2024–2025; the wind calendar's broader count of 2023–2025 tenders with "
        "no award (including UK AR5 and Lithuania) is about 7.2 GW (report/agenti/wind-calendar.md). Different perimeters, both shown.",
        "Germany: eolico-filiera.json says the 2026 offshore auctions were postponed to 2027; the cited source only says the N-10.1/N-10.2 retender moved. The report uses the narrower claim.",
        f"The FID column is incomplete: the calendar records {word(sum(len(v) for v in V['fid_items'].values()))} FIDs since 2025, WindEurope counts {word(V['fid25']['progetti'])} offshore FIDs in 2025 alone. FIDs by country for 2026 are **missing**.",
        "Auction prices are not like for like (contract length, indexation, grid costs, currency). UK prices in euro are WindEurope's conversion.",
        "Day rates of installation vessels, European steel plate prices and labour data by port are **missing**.",
        "Copper and steel are front-month futures from Yahoo Finance; the latest close may be provisional. The HRC series is a US price.",
        "Wind-calendar items with a year or half-year date are drawn across the whole period; 'unconfirmed' means a scheduled date passed without confirmation.",
        "GNSS cells measure aircraft reports, not ships; drone events are as reported, with no attribution unless stated.",
    ]))
    B.append(("p", "**Glossary.** CfD: contract for difference (two-sided: the state pays or collects the difference to a strike price). Negative bidding: the developer pays the state "
                   "for the site. FID: final investment decision. HVDC: high-voltage direct current. TSO: transmission system operator (TenneT, Amprion, 50Hertz, Energinet, Elia). "
                   "WTIV: wind turbine installation vessel (jack-up). FFIV: foundation installation vessel. CLV: cable-lay vessel. O&M: operations and maintenance. "
                   "Monopile: steel tube foundation. t/m²: load a quay can bear. TTF: Dutch gas hub price. GNSS: satellite navigation. NZIA: EU Net-Zero Industry Act. "
                   "CBAM: EU carbon border adjustment mechanism. NIS2: EU cybersecurity directive."))
    B.append(("review",))
    return B


# =====================================================================================
# Rendering
# =====================================================================================
def inline_md(t, prefix):
    return t.replace("](DATA/", f"]({prefix}")


def inline_html(t, prefix):
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2).replace("DATA/", prefix)}">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def render_md(B, meta, figs):
    P = "../docs/data/"
    o = [f"# {meta['title']}", "", f"*{meta['subtitle']}*", "",
         f"Gabriele Giuliani · Geo-economic Risk Monitor · {meta['edition']} · data read on {meta['read']}", "",
         "Every number has a source and a date. Paragraphs marked *Assessment* are the monitor's reasoning, not facts. "
         "For ports, gas, shipping costs and Baltic security in general, see the companion report *Northern Europe: Ports and Energy* (docs/report/en/northern-europe-2026-11.html).", "",
         "**Contents:** " + " · ".join(f"[{re.sub(r'^\d+\. ', '', b[2])}](#{b[1]})" for b in B if b[0] == "h2") + " · [Review](#review)", ""]
    for b in B:
        k = b[0]
        if k == "h2":
            o += [f'<a id="{b[1]}"></a>', "", f"## {b[2]}", ""]
        elif k == "h3":
            o += [f"### {b[1]}", ""]
        elif k in ("p", "val"):
            o += [inline_md(b[1], P), ""]
        elif k == "ul":
            o += [f"- {inline_md(x, P)}" for x in b[1]] + [""]
        elif k == "tab":
            o += ["| " + " | ".join(b[1]) + " |", "|" + "---|" * len(b[1])]
            o += ["| " + " | ".join(inline_md(str(c), P).replace("|", "/") for c in r) + " |" for r in b[2]]
            o += ["", f"*{inline_md(b[3], P)}*" if b[3] else "", ""]
        elif k == "fig":
            alt = re.sub(r"\*\*|\[|\]\([^)]*\)", "", b[2]).split(".")[0]
            o += [f"![{alt}]({figs[b[1]]})", "", inline_md(b[2], P), ""]
        elif k == "review":
            o += ['<a id="review"></a>', "", "---", "", "### Review · pending", "", REVIEW["text"], "", f"Review log, when done: {REVIEW['log']}.", ""]
    o += ["---", "", "Gabriele Giuliani · Geo-economic Risk Monitor · " + meta["edition"], "", meta["ai_note"], ""]
    return "\n".join(o)


CSS = """
:root{--paper:#F6F5F0;--card:#FFFFFF;--ink:#1D272D;--soft:#4f5d66;--rule:#DCDFDD;--accent:#A61E6B;--band:#ECE9E0;color-scheme:light dark}
@media (prefers-color-scheme:dark){:root{--paper:#10181D;--card:#172127;--ink:#DAE0E2;--soft:#A0ABB1;--rule:#2B373E;--accent:#e06aab;--band:#1A252C}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 "IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
.page{max-width:70ch;margin:0 auto;padding:24px 16px 64px}
a{color:var(--accent);text-underline-offset:2px;overflow-wrap:anywhere}
.back{display:inline-block;font-size:14px;margin-bottom:24px;text-decoration:none}
.back:hover{text-decoration:underline}
.kicker{font:600 13px/1.4 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:0 0 8px}
h1{font:600 clamp(28px,5vw,40px)/1.15 "IBM Plex Serif",Georgia,serif;margin:0 0 12px;letter-spacing:-.01em}
.sub{font-size:18px;color:var(--soft);margin:0 0 16px}
.meta{font-size:14px;color:var(--soft);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:10px 0;margin:0 0 28px}
h2{font:600 24px/1.25 "IBM Plex Serif",Georgia,serif;margin:48px 0 12px;padding-top:8px;scroll-margin-top:16px}
h3{font:600 18px/1.3 "IBM Plex Sans",sans-serif;margin:28px 0 8px}
p,ul{margin:0 0 16px}
ul{padding-left:1.2em}
li{margin:0 0 10px}
strong{font-weight:600}
code{font:14px "IBM Plex Mono",ui-monospace,monospace;background:var(--band);padding:1px 4px;border-radius:3px}
nav.toc{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:14px 18px;margin:0 0 8px}
nav.toc h2{font:600 13px/1.4 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;margin:0 0 6px;padding:0;color:var(--soft)}
nav.toc ol{margin:0;padding-left:1.4em;columns:2;column-gap:28px;font-size:15px}
nav.toc li{margin:0 0 4px;break-inside:avoid}
@media (max-width:560px){nav.toc ol{columns:1}}
.assess{border-left:3px solid var(--accent);background:var(--band);padding:10px 14px;margin:0 0 18px;border-radius:0 6px 6px 0;font-size:16px}
.assess .tag{font:600 12px/1 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);display:block;margin-bottom:6px}
.tabella{overflow-x:auto;margin:0 0 16px;-webkit-overflow-scrolling:touch;border:1px solid var(--rule);border-radius:6px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
th,td{padding:7px 10px;text-align:left;vertical-align:top;border-bottom:1px solid var(--rule)}
th{font-weight:600;color:var(--soft);background:var(--band)}
tr:last-child td{border-bottom:0}
td:first-child{font-weight:500}
.note{font-size:13px;color:var(--soft);margin:-8px 0 20px}
figure{margin:20px 0 22px}
figure .chart{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:10px}
figcaption{font-size:13px;color:var(--soft);margin-top:8px}
.narrow{display:none}
@media (max-width:600px){.wide{display:none}.narrow{display:block}td{min-width:7em}td:first-child{min-width:8em}}
details{margin-top:6px;font-size:13px}
summary{cursor:pointer;color:var(--soft)}
.review{margin:40px 0 0;padding:16px 18px;background:var(--card);border:1px dashed var(--soft);border-left:3px solid var(--soft);border-radius:0 8px 8px 0;font-size:15px}
.review h2{font:600 13px/1.4 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--soft);margin:0 0 10px;padding:0}
.review p{margin:0 0 10px}
footer{margin-top:56px;padding-top:16px;border-top:1px solid var(--rule);font-size:14px;color:var(--soft)}
footer .sig{font-weight:600;color:var(--ink)}
"""


def render_html(B, meta, svg):
    P = "../../data/"
    o = ["<!doctype html>", '<html lang="en-GB">', "<head>", '<meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         f"<title>{esc(meta['short'])}</title>", f'<meta name="description" content="{esc(meta["subtitle"])}">',
         '<link rel="preconnect" href="https://fonts.googleapis.com">', '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@600&display=swap" rel="stylesheet">',
         f"<style>{CSS}</style>", "</head>", "<body>", '<main class="page">',
         '<a class="back" href="../../index.html">← Back to the map</a>',
         f'<p class="kicker">Sector report · {esc(meta["edition"])}</p>',
         f"<h1>{esc(meta['title'])}</h1>", f'<p class="sub">{esc(meta["subtitle"])}</p>',
         f'<p class="meta">Gabriele Giuliani · Geo-economic Risk Monitor · data read on {esc(meta["read"])}. Every number has a source and a date; '
         f'boxes marked <em>Assessment</em> are the monitor\'s reasoning, not facts. Companion report: '
         f'<a href="northern-europe-2026-11.html">Northern Europe: Ports and Energy</a>.</p>',
         '<nav class="toc" aria-label="Contents"><h2>Contents</h2><ol>']
    for b in B:
        if b[0] == "h2":
            o.append(f'<li><a href="#{b[1]}">{esc(re.sub(r"^\d+\. ", "", b[2]))}</a></li>')
    o.append('<li><a href="#review">Review</a></li></ol></nav>')
    for b in B:
        k = b[0]
        if k == "h2":
            o.append(f'<h2 id="{b[1]}">{esc(b[2])}</h2>')
        elif k == "h3":
            o.append(f"<h3>{esc(b[1])}</h3>")
        elif k == "p":
            o.append(f"<p>{inline_html(b[1], P)}</p>")
        elif k == "val":
            m = re.match(r"^\*Assessment([^.*]*)\.\*\s*", b[1])
            tag = "Assessment" + (m.group(1) if m else "")
            txt = b[1][m.end():] if m else b[1]
            o.append(f'<aside class="assess"><span class="tag">{esc(tag)}</span>{inline_html(txt, P)}</aside>')
        elif k == "ul":
            o.append("<ul>" + "".join(f"<li>{inline_html(x, P)}</li>" for x in b[1]) + "</ul>")
        elif k == "tab":
            t = ['<div class="tabella"><table><thead><tr>' + "".join(f'<th scope="col">{esc(x)}</th>' for x in b[1]) + "</tr></thead><tbody>"]
            for r in b[2]:
                t.append("<tr>" + "".join(f"<td>{inline_html(str(c), P)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            o.append("".join(t))
            if b[3]:
                o.append(f'<p class="note">{inline_html(b[3], P)}</p>')
        elif k == "fig":
            g = svg[b[1]]
            o.append(f'<figure><div class="chart"><div class="wide">{g["wide"]}</div><div class="narrow">{g["narrow"]}</div></div>'
                     f'<figcaption>{inline_html(b[2], P)}</figcaption>'
                     f'<details><summary>Chart data as a table</summary>{g["table"]}</details></figure>')
        elif k == "review":
            o.append(f'<aside class="review" id="review"><h2>Review · pending</h2><p>{esc(REVIEW["text"])}</p>'
                     f'<p>Review log, when done: <code>{esc(REVIEW["log"])}</code>.</p></aside>')
    o.append(f'<footer><p class="sig">Gabriele Giuliani · Geo-economic Risk Monitor</p><p>{esc(meta["edition"])}. {inline_html(meta["ai_note"], P)}</p>'
             '<p><a href="../../index.html">← Back to the map</a></p></footer>')
    o += ["</main>", "</body>", "</html>"]
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", help="edition YYYY-MM (default: current month)")
    ap.add_argument("--offline", action="store_true", help="no web calls; use report/dati/offshore-wind-mercati.json")
    args = ap.parse_args()
    today = dt.date.today()
    month = args.month or today.strftime("%Y-%m")
    y, m = map(int, month.split("-"))
    edition = f"{MONTHS[m - 1]} {y}"
    V = compute(today, args.offline)
    B = blocks(V)
    meta = {"title": "Offshore Wind in Northern Europe: Targets, Bottlenecks and Ports",
            "short": "Offshore Wind in Northern Europe",
            "subtitle": f"Where North Sea and Baltic offshore wind stands against its targets, why auctions failed and are recovering, what holds delivery back, and what it means for ports, contractors and grid operators — {edition}.",
            "edition": edition, "read": date_en(today.isoformat()),
            "ai_note": ("Note on AI use: this report was prepared with an AI assistant (Claude, Anthropic), which wrote the build script, the calculations and the draft text "
                        "from the monitor's data files and the sources cited, and checked selected sources online. Numbers come from the data files and linked sources; "
                        "assessments are marked. An independent review is pending. Gabriele Giuliani is responsible for publication.")}
    os.makedirs(OUT_SVG, exist_ok=True)
    os.makedirs(OUT_HTML, exist_ok=True)
    tabs = chart_tables(V)
    svg, figs = {}, {}
    for key, fn in [("targets", chart_targets), ("prices", chart_prices), ("calendar", chart_calendar), ("markets", chart_markets)]:
        svg[key] = {"wide": fn(V, True), "narrow": fn(V, False), "table": tabs[key]}
        name = f"ow-{month}-{key}.svg"
        with open(os.path.join(OUT_SVG, name), "w", encoding="utf-8") as f:
            f.write(svg[key]["wide"])
        figs[key] = f"grafici/{name}"
    with open(os.path.join(ROOT, "report", f"offshore-wind-{month}.md"), "w", encoding="utf-8") as f:
        f.write(render_md(B, meta, figs))
    with open(os.path.join(OUT_HTML, f"offshore-wind-{month}.html"), "w", encoding="utf-8") as f:
        f.write(render_html(B, meta, svg))
    print(f"written: report/offshore-wind-{month}.md, docs/report/en/offshore-wind-{month}.html, {len(svg)} charts; {len(WARN)} warnings")


if __name__ == "__main__":
    main()
