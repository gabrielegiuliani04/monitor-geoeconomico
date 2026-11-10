#!/usr/bin/env python3
"""Build the monthly report "Northern Europe: Ports and Energy" from the monitor's data.

Standard library only. From the repository root:

    python3 report/build_northern_europe.py                  # edition for the current month
    python3 report/build_northern_europe.py --month 2026-12  # another edition
    python3 report/build_northern_europe.py --offline        # do not call Eurostat, use the cache

What it does every time it runs:
1. reads docs/data/*.json (porti-nord, offshore-nord, eolico-filiera, baltico-sicurezza,
   esposizione-nord, bunker-emissioni, assicurazioni, idrogeno, cavi-incidenti, navi,
   sanzioni-navi, rete-elettrica, interconnessioni, scorte, prezzi, noli, rischio, portwatch,
   terminali-gnl, stretti-dettaglio, cyber-energia, notizie-testate) and, WHEN THEY EXIST,
   port-risk.json, transit-times.json and wind-calendar.json (other agents produce them:
   each gets its own sub-section and its line in the method table as soon as it appears);
2. updates report/dati/eurostat-gas-nord.json with Eurostat monthly gas stocks for Denmark
   and Poland (AGSI+ daily data for those two countries need a key we do not have);
3. recomputes every number in the text and draws four SVG charts (wide and narrow);
4. writes report/northern-europe-YYYY-MM.md, docs/report/en/northern-europe-YYYY-MM.html
   and the SVGs in report/grafici/ne-YYYY-MM-*.svg.

Rules (report/STANDARD.md): no number from the data is typed by hand in the text or the
charts. The only hand-written items are:
- EXTERNAL: facts read on the web that the JSON files do not hold, each with source, link,
  date and reliability; the script warns when one is older than 60 days;
- THRESHOLDS: the watch-list thresholds, which are an assessment and are labelled as such;
- linking prose and assessments, marked "Assessment".
Curated facts quoted from text fields of the JSON files are checked with `need()`: if the
number is no longer in the source text, the script warns, so the sentence is re-read.
"""

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "data")
OUT_SVG = os.path.join(ROOT, "report", "grafici")
CACHE = os.path.join(ROOT, "report", "dati")
OUT_HTML = os.path.join(ROOT, "docs", "report", "en")

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
MON = [m[:3] for m in MONTHS]
WARN = []


def warn(msg):
    WARN.append(msg)
    print("WARNING:", msg, file=sys.stderr)


# =====================================================================================
# External facts (not in docs/data). Re-check at every edition.
# =====================================================================================
EXTERNAL = {
    "ieefa_eu_us_share": {
        "date": "2026-05", "share_2025": 58, "share_q1_2026": 63,
        "text": "the United States supplied 58% of Europe's LNG imports in 2025 and 63% in the first quarter of 2026",
        "source": "IEEFA European LNG Tracker (May 2026), as reported by the monitor's NORD agent (report/agenti/nord.md)",
        "link": "https://ieefa.org/european-lng-tracker", "reliability": "medium",
        "read": "page returns 403 to the session: not opened; figure taken from the agent report",
    },
}

# Watch-list thresholds: an ASSESSMENT of the monitor, not a forecast.
THRESHOLDS = {
    "ttf": 100.0,                 # EUR/MWh, front-month
    "storage_de": 50.0,           # % full on 1 December
    "storage_nl": 55.0,
    "eua": 95.0,                  # EUR/t at the EEX auction
    "rotterdam_30d": -10.0,       # % y/y, PortWatch 30-day average of calls
    "oresund_7d": -30.0,          # % y/y; red on the risk dashboard
    "gof_sanctioned": 50,         # sanctioned vessels in one AIS snapshot, Gulf of Finland
    "gnss_west": 3,               # high-interference cells west of 17°E in a week (one borderline cell seen in Nov 2026)
    "maersk_ets": 170,            # USD/FEU, Far East -> North Europe (Q4 2026 level)
    "redsea_war": 0.5,            # % of hull value
}

# Review box (rewritten after each edition's review; full log in report/revisioni/).
REVIEW = {
    "date": "2026-11-10",
    "log": "report/revisioni/northern-europe-2026-11.md",
    "checked": ("64 claims checked (over 150 numbers): 58 recomputed from the data files (porti-nord, scorte, prezzi, eolico-filiera, offshore-nord, "
                "bunker-emissioni, assicurazioni, noli, portwatch, baltico-sicurezza, navi, cavi-incidenti, idrogeno, esposizione-nord, rete-elettrica, "
                "interconnessioni, rischio, port-risk, transit-times, wind-calendar, Eurostat) and 6 also against the original source: 3 confirmed "
                "(Maersk surcharge, Pipeline Journal on the Danish hydrogen pipeline, HVDC World on BalWin1), 3 not reachable. "
                "No calculation errors in the data files; 12 errors or weaknesses in the draft, corrected (list below); 4 inconsistencies between files, declared."),
    "corrections": [
        "Ports: the draft led with 7-day changes (Rotterdam −10.8%); the report now leads with 30-day (+2.3%) and year-to-date (−0.5%) averages, which are less noisy.",
        "GPS jamming: the NORD agent wrote that all high-interference cells were east of 17°E; one cell at 55.8°N 16.96°E was high in the week to 8 November. "
        "Text and watch-list threshold corrected.",
        "Rotterdam bunker sales: bunker-emissioni.json says its −23.9% includes LNG, but the figure is oil and bio-blends only; with LNG it is −23.2%. Both are now stated.",
        "Storage projection: the slope used 13 days, not 14; recomputed (Germany −0.19 points a day, not −0.21).",
        "Baltic cables: the draft counted five incidents since November 2024 and gave 31 December 2025 as the last one; the Šventoji–Liepāja cable "
        "(2 January 2026, baltico-sicurezza.json) makes six.",
        "Copenhagen police statement: attributed to the agent report in the draft; it is in baltico-sicurezza.json (Wikipedia and sources, reliability medium).",
        "Detentions in 2026: one of the six is by Russia, not by a Western coastal state; wording corrected.",
        "Norway: «largest pipeline supplier» corrected to «largest gas supplier», as in the source.",
        "Key points: 2025 offshore additions given as 2.0 GW in the key points and 1.96 GW in the body; aligned to 1.96.",
        "Italian text from curated files (auction outcomes, bottleneck indicators, cable incidents, hydrogen projects, risk levels) translated into English.",
        "Charts: tick labels of the port chart were broken by a character substitution; value labels on the wind chart overlapped the target ticks. Fixed and checked at 1440 and 390 px.",
        "Transit times: the model's 10.5 extra days via the Cape (transit-times.json) and UNCTAD's 14–24 days are now both shown, with the reason they differ.",
        "Updated 10 Nov 2026 after the offshore wind review: the Dutch 21 GW target is shown for end-2032 (moved from 2030 in 2024; the March 2026 letter to "
        "Parliament still says 'around 2030'), not for 2030; the turbine bottleneck now quotes Siemens Gamesa's first profitable quarter since financial year 2022 "
        "(about +75 million € in April–June 2026, secondary summaries) instead of the Q2 loss of −44 million €, and GE Vernova's wind EBITDA of +72 million $ in Q3 2026 "
        "(2026 guidance: a loss of 400–500 million $); supply-chain investment since 2022 is 'at least 15 billion €' as in the WindEurope PDF, not 15.4 billion €. "
        "Corrected at the source in eolico-filiera.json. Brent: the note on files that disagree no longer gives 91.70 as the prezzi.json figure for 9 November; "
        "that was overnight trading of the next session, and the 9 November close is 92.57 (the report does not use Brent). "
        "Prices now skip the live session that prezzi.json marks as provisional: TTF is the 9 November close (82.50 €/MWh, not the 82.33 read overnight), "
        "with its year-to-date change, since the 1-year change cannot be recomputed exactly for that day.",
    ],
    "unverifiable": [
        "EU-wide US share of LNG (58% in 2025, 63% in Q1 2026) and the country shares: IEEFA page returns 403; figures from the agent report and esposizione-nord.json.",
        "292 shadow-fleet passages (Danish Maritime Authority via Euronews) and the Fitburg sentence of 42 months: Euronews not reachable from the session.",
        "Prices from Ship & Bunker, EEX auction results, WindEurope statistics and offshoreWIND.biz articles: checked only against the data files.",
        "IJmuiden Ver Gamma dates (26 November–10 December 2026): secondary source (RVO via trade press) in two files that agree.",
        "Inconsistent perimeters declared, not resolved: sanctioned ships in the Gulf of Finland (44 of 109 ships; 38 of 96 tankers; 45 tankers in the whole Baltic); "
        "hull value of a large container ship (221.7 vs 150 million $); German LNG capacity still counting the Mukran terminal; Brent (92.57, the 9 November close, in prezzi.json; 92.62, an intraday reading, in bunker-emissioni.json and rischio.json).",
    ],
}

OPTIONAL = {
    "port-risk.json": "port risk scores (PORT-RISK agent)",
    "transit-times.json": "transit times to Rotterdam (TRANSIT agent)",
    "wind-calendar.json": "offshore wind calendar (WIND-CALENDAR agent)",
}


# =====================================================================================
# Helpers
# =====================================================================================
def load(name, required=True):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        if required:
            raise SystemExit(f"missing data file: {p}")
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def d(s):
    return dt.date.fromisoformat(s[:10])


def num(v, dec=1):
    if v is None:
        return "n/a"
    s = f"{v:,.{dec}f}"
    return s


def pct(v, dec=1, sign=True):
    if v is None:
        return "n/a"
    if round(v, dec) == 0:
        return "0%"
    s = f"{v:+,.{dec}f}" if sign else f"{v:,.{dec}f}"
    return s.replace("-", "−") + "%"


def pp(v, dec=1):
    return (f"{v:+.{dec}f}".replace("-", "−")) + " pp"


def date_en(s, year=True):
    s = str(s)
    if len(s) == 7:
        y, m = s.split("-")
        return f"{MONTHS[int(m) - 1]} {y}"
    x = d(s)
    return f"{x.day} {MONTHS[x.month - 1]}" + (f" {x.year}" if year else "")


def date_short(s):
    x = d(s)
    return f"{x.day} {MON[x.month - 1]} {x.year}"


def esc(s):
    return html.escape(str(s), quote=True)


def link(text, url):
    return f"[{text}]({url})" if url else text


def data_link(name):
    return f"[{name}](DATA/{name})"


def last_close(s):
    """prezzi.json marks a live session as 'provvisorio': use the last completed session instead.
    1-day and 1-month changes are recomputed on the series; year-to-date and 1-year changes are
    rebased from the live point; the 1-year change is dropped (see long_change)."""
    ser = s.get("serie") or []
    if not s.get("provvisorio") or len(ser) < 3:
        return s
    live = ser[-1][1]
    (dc, vc), body = ser[-2], ser[:-1]
    out = dict(s, ultimo=vc, data=dc, serie=body, provvisorio=False, live_escluso=ser[-1])
    v = {}
    if body[-2][1]:
        v["1g"] = round(100 * (vc / body[-2][1] - 1), 2)
    lim = (dt.date.fromisoformat(dc) - dt.timedelta(days=30)).isoformat()
    m = [x for d_, x in body if d_ <= lim]
    if m and m[-1]:
        v["1m"] = round(100 * (vc / m[-1] - 1), 2)
    # year to date: same reference (last close of the previous year), so it can be rebased exactly;
    # the 1-year change cannot (its reference day shifts with the last point), so it is left out
    if (s.get("var") or {}).get("ytd") is not None and live and dc[:4] == ser[-1][0][:4]:
        ref = live / (1 + s["var"]["ytd"] / 100)
        v["ytd"] = round(100 * (vc / ref - 1), 2)
    out["var"] = v
    return out


def long_change(s, digits=0):
    """'+164% on a year', or the year-to-date change when the 1-year one is not available."""
    v = s.get("var") or {}
    if v.get("1a") is not None:
        return f"{pct(v['1a'], digits)} on a year"
    return f"{pct(v['ytd'], digits)} since the start of the year"


def need(text, *tokens, where=""):
    """Warn if a curated number quoted in the report is no longer in its source text."""
    t = str(text)
    for tok in tokens:
        if str(tok) not in t:
            warn(f"curated fact not found in source ({where}): «{tok}»")


def var(a, b):
    if a is None or b in (None, 0):
        return None
    return (a / b - 1) * 100


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


LEVEL = {"basso": "low", "medio": "medium", "alto": "high", "critico": "critical"}

# Small glossary to render Italian curated labels in English (names and places, not numbers).
IT2EN = [
    ("Terminale di import ammoniaca", "Ammonia import terminal"), ("Terminale ammoniaca + cracker", "Ammonia terminal + cracker"),
    ("Terminale ammoniaca", "Ammonia terminal"), ("Cracker di ammoniaca", "Ammonia cracker"),
    ("Pilota di bunkeraggio ammoniaca nave-nave", "Ship-to-ship ammonia bunkering pilot"),
    ("impianto di e-metanolo", "e-methanol plant"), ("e-metanolo", "e-methanol"), ("elettrolizzatore RWE di Lingen", "RWE electrolyser, Lingen"),
    ("Elettrolizzatore OranjeWind (RWE) presso centrale Magnum", "OranjeWind electrolyser (RWE) at Magnum power plant"),
    ("elettrolizzatore raffineria di Danzica", "electrolyser at Gdańsk refinery"), ("rete industriale dell'idrogeno di Amburgo", "Hamburg industrial hydrogen grid"),
    ("idrogeno blu con CCS", "blue hydrogen with CCS"), ("idrogeno blu", "blue hydrogen"), ("Acciaieria ArcelorMittal Brema: piano DRI a idrogeno", "ArcelorMittal Bremen steelworks: hydrogen DRI plan"),
    ("Cluster PtX di Esbjerg", "Esbjerg PtX cluster"), ("fase 1", "phase 1"), ("Kasso", "Kassø"),
    ("(entroterra, Ems)", "(inland, Ems)"), ("(Jutland meridionale)", "(southern Jutland)"), ("Amburgo", "Hamburg"),
    ("Zeebrugge (Anversa-Bruges)", "Zeebrugge (Antwerp-Bruges)"), ("Anversa", "Antwerp"), ("Danzica", "Gdańsk"), ("Brema", "Bremen"),
    ("Oernskoeldsvik", "Örnsköldsvik"), ("Brunsbuettel", "Brunsbüttel"),
    ("3 siti nel Mare del Nord (3 GW)", "three North Sea sites (3 GW)"), ("(senza sussidi)", "(no subsidy)"), ("Hesselo'", "Hesselø"),
    ("sito non pre-studiato", "site not pre-investigated"), ("Seconda asta offshore (riproposta, 0,7 GW)", "second offshore round (re-run, 0.7 GW)"),
    ("Sorvest F (1,5 GW)", "Sørvest F (1.5 GW)"), ("N-10.1 e N-10.2 (2,5 GW)", "N-10.1 and N-10.2 (2.5 GW)"),
    ("Prima asta CfD offshore", "first offshore CfD round"), (") e Gamma-B", ") and Gamma-B"), (") e Hesselø", ") and Hesselø"),
    ("Riforma WindSeeG (bozza)", "WindSeeG reform (draft)"), (" e ", " and "),
]


def it2en(t):
    for a, b in IT2EN:
        t = t.replace(a, b)
    return t


MECH = {"offerta negativa / senza sussidi": "negative bidding / no subsidy", "senza sussidi": "no subsidy", "offerta negativa": "negative bidding",
        "CfD": "CfD", "offerta negativa senza tetto": "uncapped negative bidding", "CfD a due vie, 25 anni": "two-sided CfD, 25 years",
        "sussidio temporaneo TOWOZ": "temporary subsidy (TOWOZ)", "CfD a due vie, 20 anni": "two-sided CfD, 20 years",
        "due fasi (offerta + CfD di riserva)": "two stages (bid + fallback CfD)"}
OUTCOME = [("nessuna offerta", "no bids"), ("annullat", "cancelled"), ("invalidat", "invalidated (fewer than two bids)"),
           ("aggiudicat", "awarded"), ("record", "awarded (record)"), ("Baltica 9", "awarded: Baltica 9, Baltic East, Bałtyk I"),
           ("in corso", "open: applications 26 Nov–10 Dec 2026"), ("in iter", "in parliament; rounds of 2–4.8 GW a year from 2027")]


def outcome_en(t):
    for k, v in OUTCOME:
        if t.startswith(k) or (k == "Baltica 9" and k in t):
            return v
    return t


BOTTLE_EN = {  # first indicator of each bottleneck card: English label and unit (value read from the file)
    "aste-ricavi": ("offshore capacity in failed negative-bidding rounds, 2024–2025", " GW"),
    "cavi-hvdc": ("Prysmian transmission order backlog", " billion €"),
    "convertitori-hvdc": ("new in-service date of Amprion's BalWin1 (2 GW) grid link", ""),
    "turbine": ("Siemens Gamesa profit before special items in Q3 of financial year 2026 (April–June), its first profitable quarter since financial year 2022", " million € (about; figure from secondary summaries)"),
    "navi": ("Western installation vessels (WTIV) for turbines of 15 MW or more by 2028, more than", ""),
    "porti": ("investment announced since 2022 in factories, ports and vessels", " billion €"),
    "fondazioni": ("European XXL monopile capacity from 2027", " million tonnes a year"),
}

CABLE_EN = {  # id -> (English label, vessel named in the source; checked with need())
    "CI-2023-02": ("Balticconnector gas pipeline and Finland–Estonia cables", "NewNew Polar Bear"),
    "CI-2024-02": ("BCS East-West Interlink (Lithuania–Gotland)", "Yi Peng 3"),
    "CI-2024-03": ("C-Lion1 (Helsinki–Rostock)", "Yi Peng 3"),
    "CI-2024-04": ("Estlink 2 power cable and four data cables", "Eagle S"),
    "CI-2025-02": ("Ventspils–Gotland data cable (LVRTC)", "Vezhen"),
    "CI-2025-05": ("Elisa and Arelion Helsinki–Tallinn cables", "Fitburg"),
}

PAESE = {"NL": "Netherlands", "BE": "Belgium", "DE": "Germany", "DK": "Denmark", "SE": "Sweden",
         "PL": "Poland", "LT": "Lithuania", "LV": "Latvia", "EE": "Estonia", "FI": "Finland",
         "RU": "Russia", "NO": "Norway", "GB": "United Kingdom", "FR": "France", "IE": "Ireland"}

PORT_EN = {
    "rotterdam": "Rotterdam", "anversa-bruges": "Antwerp-Bruges", "amburgo": "Hamburg",
    "brema-bremerhaven": "Bremen/Bremerhaven", "wilhelmshaven": "Wilhelmshaven", "amsterdam": "Amsterdam",
    "eemshaven": "Eemshaven", "esbjerg": "Esbjerg", "aarhus": "Aarhus", "copenaghen-malmo": "Copenhagen-Malmö",
    "goteborg": "Gothenburg", "danzica": "Gdańsk", "gdynia": "Gdynia", "swinoujscie": "Szczecin-Świnoujście",
    "klaipeda": "Klaipėda", "riga": "Riga", "ventspils": "Ventspils", "tallinn": "Tallinn", "helsinki": "Helsinki",
    "hamina-kotka": "HaminaKotka", "primorsk": "Primorsk", "ust-luga": "Ust-Luga",
    "san-pietroburgo": "St Petersburg", "kaliningrad": "Kaliningrad", "skoldvik": "Sköldvik",
    "vysotsk": "Vysotsk", "paldiski": "Paldiski", "inkoo": "Inkoo", "rostock": "Rostock", "brunsbuttel": "Brunsbüttel",
}


# =====================================================================================
# Eurostat monthly gas stocks (DK, PL): network with cache
# =====================================================================================
def eurostat_gas(offline):
    path = os.path.join(CACHE, "eurostat-gas-nord.json")
    cached = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cached = json.load(f)
    if offline:
        if not cached:
            warn("Eurostat cache missing and --offline: DK/PL storage omitted")
        return cached
    url = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_stk_gasm?"
           + urllib.parse.urlencode({"geo": ["DK", "PL"], "stk_flow": "STKCL_NAT", "unit": "TJ_GCV",
                                     "sinceTimePeriod": "2023-01", "lang": "en"}, doseq=True))
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "monitor-report/1.0"}), timeout=60) as r:
            j = json.loads(r.read().decode("utf-8"))
        ids, size = j["id"], j["size"]
        idx = {k: {v: c for c, v in j["dimension"][k]["category"]["index"].items()} for k in ids}
        out = {}
        for k, v in j["value"].items():
            k = int(k)
            co = {}
            for dim, n in zip(reversed(ids), reversed(size)):
                co[dim] = idx[dim][k % n]
                k //= n
            out.setdefault(co["geo"], []).append([co["time"], round(v / 3600.0, 2)])
        for s in out.values():
            s.sort()
        res = {"source": "Eurostat nrg_stk_gasm (STKCL_NAT, TJ GCV / 3600 = TWh)",
               "link": "https://ec.europa.eu/eurostat/databrowser/view/nrg_stk_gasm/default/table",
               "updated": j.get("updated", ""), "read": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
               "series": out}
        os.makedirs(CACHE, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        return res
    except Exception as ex:  # noqa: BLE001
        warn(f"Eurostat not reachable ({ex}); using cache" if cached else f"Eurostat not reachable ({ex}); no cache")
        return cached


# =====================================================================================
# Computation
# =====================================================================================
def compute(today, offline):
    V = {"today": today}
    F = {n: load(n) for n in [
        "porti-nord.json", "offshore-nord.json", "eolico-filiera.json", "baltico-sicurezza.json",
        "esposizione-nord.json", "bunker-emissioni.json", "assicurazioni.json", "idrogeno.json",
        "cavi-incidenti.json", "navi.json", "sanzioni-navi.json", "rete-elettrica.json",
        "interconnessioni.json", "scorte.json", "prezzi.json", "noli.json", "rischio.json",
        "portwatch.json", "terminali-gnl.json", "stretti-dettaglio.json", "cyber-energia.json",
        "notizie-testate.json"]}
    F["cavi.json"] = load("cavi.json", required=False)
    for n in OPTIONAL:
        F[n] = load(n, required=False)
        if F[n] is None:
            warn(f"{n} not found: section left as 'missing' (it is included automatically when it appears)")
    V["F"] = F

    # ---------------------------------------------------------------- ports
    pn = F["porti-nord.json"]
    ports = []
    for e in pn["elementi"]:
        ton = [t for t in (e.get("traffico_annuo") or [])
               if t.get("anno") == 2025 and re.match(r"milioni di t( \(|$)", t.get("unita", ""))]
        teu = [t for t in (e.get("traffico_annuo") or [])
               if t.get("anno") == 2025 and t.get("unita", "").startswith("milioni di TEU")]
        s = (e.get("serie") or {}).get("portcalls") or []
        last = e.get("ultima_data")
        ly = d(last)
        start, start_prev = f"{ly.year}-01-01", f"{ly.year - 1}-01-01"
        end_prev = (ly.replace(year=ly.year - 1)).isoformat()
        cur = [v for k, v in s if start <= k <= last]
        prev = [v for k, v in s if start_prev <= k <= end_prev]
        ytd = var(mean(cur), mean(prev)) if len(cur) > 200 and len(prev) > 200 else None
        m30, m30p = e.get("media30") or {}, e.get("media30_anno_prima") or {}
        types = {}
        for k in ["tanker", "container", "dry_bulk", "general_cargo", "roro"]:
            a, b = m30.get("portcalls_" + k), m30p.get("portcalls_" + k)
            types[k] = {"now": a, "prev": b, "var": var(a, b) if (b or 0) >= 1.0 else None}
        ports.append({
            "id": e["id"], "name": PORT_EN.get(e["id"], e["nome"]), "country": e["paese"],
            "mt": ton[0]["valore"] if ton else None, "mt_var": ton[0].get("var_pct") if ton else None,
            "mt_src": ton[0] if ton else None, "teu": teu[0] if teu else None,
            "calls7": e["media7"]["portcalls"], "var7": e["var7_anno_pct"]["portcalls"],
            "calls30": m30.get("portcalls"), "var30": var(m30.get("portcalls"), m30p.get("portcalls")),
            "var30_file": e.get("var30_anno_pct"), "ytd": ytd, "ytd_days": len(cur),
            "ytd_now": mean(cur), "ytd_prev": mean(prev), "types": types, "last": last,
            "p7": e.get("periodo_media7"), "traffic": e.get("traffico_annuo") or [], "raw": e})
    V["ports_all"] = ports
    top = sorted([p for p in ports if p["mt"]], key=lambda p: -p["mt"])[:10]
    V["top10"] = top
    V["ports_last"] = max(p["last"] for p in ports)
    V["no_total"] = [p["name"] for p in ports if not p["mt"] and p["id"] in ("primorsk", "goteborg", "wilhelmshaven")]
    for p in ports:
        if p["var30_file"] is not None and p["var30"] is not None and abs(round(p["var30"], 1) - p["var30_file"]) > 0.15:
            warn(f"30-day y/y recomputed differs from file for {p['name']}: {p['var30']:.1f} vs {p['var30_file']}")
    V["oresund"] = pn["stretti"][0]
    V["pmap"] = {p["id"]: p for p in ports}

    # ---------------------------------------------------------------- gas storage
    sc = F["scorte.json"]
    el = {e["id"]: e for e in sc["elementi"]}
    st = {}
    for c in ["nl", "de"]:
        e, t = el[f"gas_stoccaggio_pct_{c}"], el[f"gas_stoccaggio_twh_{c}"]
        u = e["ultimo"]
        s = e["serie"]
        last14 = [x for x in s if d(x[0]) >= d(u["data"]) - dt.timedelta(days=14)]
        slope = (last14[-1][1] - last14[0][1]) / max(1, (d(last14[-1][0]) - d(last14[0][0])).days)
        dec1 = dt.date(d(u["data"]).year, 12, 1)
        proj = u["valore"] + slope * (dec1 - d(u["data"])).days
        st[c] = {"pct": u["valore"], "date": u["data"], "yoy_pp": u["anno_scorso"]["variazione"],
                 "last_year": u["anno_scorso"]["valore"], "avg5": u["media_5_anni"]["valore"],
                 "vs5": u["media_5_anni"]["scarto"], "to_target": u["distanza_obiettivo_pp"],
                 "twh": t["ultimo"]["valore"], "twh_yoy": t["ultimo"]["anno_scorso"]["variazione_pct"],
                 "cap_note": t.get("note", ""), "series": s, "slope": slope, "proj_dec1": proj,
                 "link": e["link"]}
    V["storage"] = st
    V["eu_stock"] = el["gas_stock_mensile_twh_eu"]["ultimo"]
    eg = eurostat_gas(offline)
    V["eurostat"] = eg
    dkpl = {}
    if eg:
        for g in ["DK", "PL"]:
            s = eg["series"].get(g) or []
            if not s:
                continue
            lastm, lastv = s[-1]
            y = int(lastm[:4]) - 1
            prevm = f"{y}{lastm[4:]}"
            pv = dict(s).get(prevm)
            mx = max(v for k, v in s if k.startswith(str(y)))
            dkpl[g] = {"month": lastm, "twh": lastv, "prev_month": prevm, "prev": pv, "yoy": var(lastv, pv),
                       "max_prev_year": mx}
    V["dkpl"] = dkpl

    # ---------------------------------------------------------------- prices
    pr = {s["id"]: last_close(s) for s in F["prezzi.json"]["serie"]}
    V["ttf"], V["hh"], V["brent"], V["eurusd"] = pr["ttf"], pr["hh"], pr["brent"], pr["eurusd"]
    # TTF in USD/MMBtu: EUR/MWh x USD/EUR / 3.412 MMBtu per MWh
    V["ttf_usd_mmbtu"] = pr["ttf"]["ultimo"] * pr["eurusd"]["ultimo"] / 3.412
    V["spread"] = V["ttf_usd_mmbtu"] - pr["hh"]["ultimo"]

    # ---------------------------------------------------------------- LNG and exposure
    ex = {e["paese"]: e for e in F["esposizione-nord.json"]["elementi"]}
    V["exp"] = ex
    need(ex["NO"]["gas"], "30,9%", "89,3", "114,9", where="esposizione-nord NO")
    need(ex["DK"]["gas"], "2,8", "1,4", where="esposizione-nord DK")
    need(ex["NL"]["gas"], "1° ottobre 2024", where="esposizione-nord NL")
    need(ex["DE"]["gnl"].get("nota", ""), "Mukran", where="esposizione-nord DE")

    # ---------------------------------------------------------------- power links
    rete = F["rete-elettrica.json"]["elementi"]
    names = ["IJmuiden Ver", "Nederwiek", "NeuConnect", "Bornholm", "Eastern Green Link"]
    uc = {}
    for x in rete:
        if x.get("hvdc") and x.get("stato") == "in costruzione" and x.get("tipo") == "cavo":
            for n in names:
                if n.lower() in (x.get("nome") or "").lower():
                    key = re.sub(r"\s+onshore$", "", x["nome"]).replace("Kabeltracé ", "").replace("BEI-Interkonnektor ", "")
                    uc.setdefault(key, 0)
                    uc[key] += x.get("km_mappa") or 0
    V["hvdc_uc"] = uc
    ic = {e["id"]: e for e in F["interconnessioni.json"]["elementi"]}
    V["estlink2"] = ic.get("EL-IC-09")

    # ---------------------------------------------------------------- offshore wind
    ef = F["eolico-filiera.json"]
    ob = ef["obiettivi"]
    V["wind_eu"] = ob["europa"]
    V["wind_src"] = ob["fonte_installato"]
    V["wind_decl"] = {x["id"]: x for x in ob["dichiarazioni"]}
    V["wind_countries"] = [c for c in ob["paesi"] if c["paese"] in ("GB", "DE", "NL", "DK", "BE", "PL", "FR", "NO")]
    V["auctions"] = ef["aste"]
    V["bottle"] = {c["id"]: c for c in ef["colli_bottiglia"]}
    V["fleet"] = ef["flotta"]
    V["wind_ports"] = {e["id"]: e for e in ef["elementi"]}
    V["wind_news"] = ef["notizie_recenti"]
    on = F["offshore-nord.json"]
    bal = {}
    for r in on["riepilogo_mw"]:
        if r["mare"] == "Baltico":
            bal[r["stato"]] = bal.get(r["stato"], 0) + r["mw"]
    V["baltic_mw"] = bal
    ns = {}
    for r in on["riepilogo_mw"]:
        if r["mare"] == "Mare del Nord":
            ns[r["stato"]] = ns.get(r["stato"], 0) + r["mw"]
    V["northsea_mw"] = ns
    V["hubs"] = on["hub"]

    # ---------------------------------------------------------------- costs
    be = F["bunker-emissioni.json"]
    hubs = {e["nome"]: e for e in be["elementi"] if e.get("tipo") == "hub_bunker"}
    V["bunker"] = {k: hubs[k]["prezzi"]["VLSFO"] for k in ["Rotterdam", "Anversa", "Gibilterra", "Singapore", "Fujairah"] if k in hubs}
    V["bunker_link"] = {k: hubs[k]["link"] for k in hubs}
    V["rtm_hub"] = hubs.get("Rotterdam")
    V["eua"] = be["eua"]["asta_ultima"]
    V["eua_mean"] = be["eua"]["media_aste_anno"]
    ex_c = {e["id"]: e for e in be["esempi_costo"]}
    V["ex_asia"], V["ex_intra"], V["ex_tanger"] = ex_c["asia-rotterdam"], ex_c["intra-ue"], ex_c.get("deviazione-tanger")
    a = V["ex_asia"]
    chk = 4000 * a["prezzo_bunker_usd_t"] / a["eurusd"]
    if abs(chk - a["costo_carburante_eur"]) > 2:
        warn(f"fuel cost in bunker example does not recompute: {chk:.0f} vs {a['costo_carburante_eur']}")
    V["maersk"] = be["sovrapprezzo_vettori"]
    V["rtm_vol"] = be["volumi"]["rotterdam"]
    q = {x["periodo"]: x for x in V["rtm_vol"]["trimestri"]}
    yy = max(int(k[:4]) for k in q)
    tot = lambda y_: sum((q.get(f"{y_}-T{i}") or {}).get("fossili_t", 0) + (q.get(f"{y_}-T{i}") or {}).get("bio_t", 0)
                         + 0.45 * (q.get(f"{y_}-T{i}") or {}).get("gnl_m3", 0) for i in (1, 2, 3))
    V["rtm_bunker_9m_lng"] = var(tot(yy), tot(yy - 1))
    tot2 = lambda y_: sum((q.get(f"{y_}-T{i}") or {}).get("fossili_t", 0) + (q.get(f"{y_}-T{i}") or {}).get("bio_t", 0) for i in (1, 2, 3))
    V["rtm_bunker_9m"] = var(tot2(yy), tot2(yy - 1))
    V["rtm_bunker_9m_t"] = (tot2(yy), tot2(yy - 1))
    V["rtm_bunker_year"] = yy
    ops = {e["id"]: e for e in be["elementi"] if e.get("tipo") == "porto_ops"}
    V["ops_rtm"] = ops.get("ops-rotterdam")
    # insurance: Red Sea war-risk premium for a large container ship (assicurazioni.json example)
    ass = F["assicurazioni.json"]
    exs = {e["id"]: e for e in ass["esempi_costo"]}
    rs = exs["mar-rosso-portacontainer-contro-capo"]["ingressi"]
    hull = rs["valore_nave_musd"]["valore"]
    lo, hi = rs["premio_set2026_min_pct"]["valore"], rs["premio_set2026_max_pct"]["valore"]
    fx = a["eurusd"]
    V["ins"] = {"hull_musd": hull, "lo": lo, "hi": hi, "mid": (lo + hi) / 2,
                "lo_eur": hull * 1e6 * lo / 100 / fx, "hi_eur": hull * 1e6 * hi / 100 / fx,
                "mid_eur": hull * 1e6 * (lo + hi) / 2 / 100 / fx, "src": rs["premio_set2026_min_pct"],
                "hull_src": rs["valore_nave_musd"], "teu": rs["teu"]["valore"]}
    V["war_last"] = ass["ultimo_premio"]
    V["jwc"] = ass["circolare_in_vigore"]
    V["jwc_russia"] = next((e for e in ass["elementi"] if e.get("id") == "russia"), None)
    nl = {e["id"]: e for e in F["noli.json"]["elementi"]}
    V["wci"], V["fbx"], V["ccfi"] = nl["wci"], nl["fbx"], nl["ccfi"]
    pw = {e["id"]: e for e in F["portwatch.json"]["elementi"]}
    V["suez"], V["cape"], V["bab"] = pw["chokepoint1"], pw["chokepoint7"], pw["chokepoint4"]
    sd = json.dumps(F["stretti-dettaglio.json"], ensure_ascii=False)
    V["unctad_cape"] = "14–24" if "14–24 giorni in più" in sd else None
    if not V["unctad_cape"]:
        warn("UNCTAD 14–24 days not found in stretti-dettaglio.json")
    V["bimco"] = ("753.000" in sd and "1.457.000" in sd)
    if not V["bimco"]:
        warn("BIMCO 753,000 / 1,457,000 TEU not found in stretti-dettaglio.json")

    # ---------------------------------------------------------------- security
    bs = F["baltico-sicurezza.json"]
    V["bs"] = bs
    V["gof"] = bs["flotta_per_area"]["Golfo di Finlandia"]
    V["dk_ais"] = bs["flotta_per_area"]["Stretti danesi"]
    V["gnss"] = bs["gnss"]
    cells = bs["gnss"]["celle"]
    V["gnss_west"] = [c for c in cells if c["lon"] < 17 and c["livello"] == "alto"]
    gd = bs["gnss"]["serie_giornaliera"]
    V["gnss_min"], V["gnss_max"] = min(x[1] for x in gd), max(x[1] for x in gd)
    V["ev"] = sorted(bs["eventi"], key=lambda e: e.get("data", ""))
    nv = F["navi.json"]
    gof_tank = [x for x in nv["elementi"] if x.get("area") == "Golfo di Finlandia" and "petroliera" in (x.get("tipo") or "")]
    bal_tank = [x for x in nv["elementi"] if x.get("area", "").startswith("Baltico") and "petroliera" in (x.get("tipo") or "")]
    V["gof_tankers"] = len(gof_tank)
    V["gof_tankers_sanc"] = sum(1 for x in gof_tank if (x.get("sanzionata") or "").startswith("sì"))
    V["bal_tankers_sanc"] = sum(1 for x in bal_tank if (x.get("sanzionata") or "").startswith("sì"))
    V["navi_date"] = nv["aggiornato"]
    ci = [e for e in F["cavi-incidenti.json"]["elementi"]
          if any(w in e["nome"] for w in ["Baltico", "Golfo di Finlandia", "Estlink", "Balticconnector"])]
    V["cables"] = sorted(ci, key=lambda e: e["data_evento"])
    V["cables_extra"] = [e for e in bs["eventi"] if e["categoria"] == "danno-cavo" and not e.get("rif")]
    V["last_cable"] = max([c["data_evento"] for c in V["cables"]] + [e["data"] for e in V["cables_extra"]])
    V["sanc_count"] = F["sanzioni-navi.json"]["conteggi"]
    rk = {u["id"]: u for u in F["rischio.json"]["unita"]}
    V["risk"] = rk
    cy = {e["id"]: e for e in F["cyber-energia.json"]["elementi"]}
    V["cyber_pl"] = cy.get("CE-2025-PL")

    # ---------------------------------------------------------------- hydrogen
    h2 = F["idrogeno.json"]
    V["h2"] = h2
    V["h2_north"] = [e for e in h2["elementi"] if e.get("focus") == "nord-europa"]
    V["h2_real"] = h2["realta"]
    V["h2_pipes"] = {p["id"]: p for p in h2["pipeline"]}
    V["h2_gas"] = h2["collegamenti"]["gas"]

    # ---------------------------------------------------------------- news signal
    nt = F["notizie-testate.json"]
    V["news"] = nt["riepilogo"]["per_argomento"]
    V["news_date"] = nt["aggiornato"]

    # ---------------------------------------------------------------- staleness of externals
    for k, f in EXTERNAL.items():
        dd = d(f["date"] + ("-01" if len(f["date"]) == 7 else ""))
        if (today - dd).days > 60:
            warn(f"external fact '{k}' is {(today - dd).days} days old: re-check it")
    return V


# =====================================================================================
# SVG charts
# =====================================================================================
SVG_STYLE = """<style>
.ne-t{font:600 14px 'IBM Plex Sans',system-ui,sans-serif;fill:#1D272D}
.ne-l{font:12px 'IBM Plex Sans',system-ui,sans-serif;fill:#3b474e}
.ne-m{font:11px 'IBM Plex Mono',ui-monospace,monospace;fill:#5f6b72}
.ne-g{stroke:#d9dcd8;stroke-width:1}
.ne-z{stroke:#5f6b72;stroke-width:1.2}
.ne-s1{fill:#A61E6B}.ne-s2{fill:#2a78d6}.ne-s3{fill:#eda100}.ne-s4{fill:#1baf7a}
.ne-k1{stroke:#A61E6B}.ne-k2{stroke:#2a78d6}.ne-k3{stroke:#eda100}
.ne-bg{fill:#ffffff}
.ne-h{paint-order:stroke;stroke:#ffffff;stroke-width:4px;stroke-linejoin:round}
@media (prefers-color-scheme:dark){
.ne-t{fill:#DAE0E2}.ne-l{fill:#c3cacd}.ne-m{fill:#99a5ab}.ne-g{stroke:#2f3b42}.ne-z{stroke:#99a5ab}
.ne-s1{fill:#d14f9a}.ne-s2{fill:#3987e5}.ne-s3{fill:#c98500}.ne-s4{fill:#199e70}
.ne-k1{stroke:#d14f9a}.ne-k2{stroke:#3987e5}.ne-k3{stroke:#c98500}.ne-bg{fill:#172127}.ne-h{stroke:#172127}}
</style>"""


def svg_open(w, h, title, desc, uid):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" '
            f'aria-labelledby="{uid}-t {uid}-d" style="max-width:{w}px;height:auto;display:block">'
            f'<title id="{uid}-t">{esc(title)}</title><desc id="{uid}-d">{esc(desc)}</desc>{SVG_STYLE}'
            f'<rect class="ne-bg" x="0" y="0" width="{w}" height="{h}" rx="6"/>')


def bar_path(x0, x1, y, h, r=4):
    """Horizontal bar from baseline x0 to x1 with rounded data end."""
    if abs(x1 - x0) < 0.5:
        return f'M{x0:.1f},{y:.1f}h0.5v{h:.1f}h-0.5z'
    r = min(r, abs(x1 - x0), h / 2)
    if x1 >= x0:
        return (f'M{x0:.1f},{y:.1f}H{x1 - r:.1f}Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f}V{y + h - r:.1f}'
                f'Q{x1:.1f},{y + h:.1f} {x1 - r:.1f},{y + h:.1f}H{x0:.1f}Z')
    return (f'M{x0:.1f},{y:.1f}H{x1 + r:.1f}Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f}V{y + h - r:.1f}'
            f'Q{x1:.1f},{y + h:.1f} {x1 + r:.1f},{y + h:.1f}H{x0:.1f}Z')


def ticks(lo, hi, step):
    t = []
    v = (int(lo // step)) * step
    while v <= hi + 1e-9:
        if v >= lo - 1e-9:
            t.append(round(v, 6))
        v += step
    return t


def chart_ports(V, wide=True):
    P = V["top10"]
    w = 680 if wide else 360
    left = 150 if wide else 104
    right = 56 if wide else 40
    rowh = 34 if wide else 36
    top = 66
    h = top + rowh * len(P) + 34
    vals = [p["var30"] for p in P] + [p["ytd"] for p in P if p["ytd"] is not None]
    lo, hi = min(-10, min(vals) - (6 if wide else 12)), max(10, max(vals) + (4 if wide else 8))
    step = 10 if hi - lo <= 80 else 20
    lo, hi = step * (lo // step), step * (-(-hi // step))
    X = lambda v: left + (v - lo) / (hi - lo) * (w - left - right)
    o = [svg_open(w, h, "Port calls, change on a year earlier",
                  "Bars: last 30 days and year to date versus the same days of the previous year, ten largest ports.", "ch1" + ("w" if wide else "n"))]
    o.append(f'<text class="ne-t" x="12" y="22">Port calls vs a year earlier, %</text>')
    o.append(f'<rect class="ne-s1" x="12" y="34" width="12" height="10" rx="2"/><text class="ne-l" x="30" y="43">last 30 days</text>')
    o.append(f'<rect class="ne-s2" x="{120 if wide else 110}" y="34" width="12" height="10" rx="2"/><text class="ne-l" x="{138 if wide else 128}" y="43">1 Jan to latest day</text>')
    for t in ticks(lo, hi, step):
        x = X(t)
        o.append(f'<line class="{"ne-z" if t == 0 else "ne-g"}" x1="{x:.1f}" x2="{x:.1f}" y1="{top - 8}" y2="{h - 26}"/>')
        lab = "0" if t == 0 else f"{int(t):+d}".replace("-", "−")
        o.append(f'<text class="ne-m" x="{x:.1f}" y="{h - 10}" text-anchor="middle">{lab}</text>')
    for i, p in enumerate(P):
        y = top + i * rowh
        nm = p["name"] if wide or len(p["name"]) < 14 else p["name"].replace("Szczecin-", "Szcz.-").replace("Bremen/", "")
        o.append(f'<text class="ne-l" x="{left - 8}" y="{y + 17}" text-anchor="end">{esc(nm)}</text>')
        for j, (k, cls) in enumerate([("var30", "ne-s1"), ("ytd", "ne-s2")]):
            v = p[k]
            if v is None:
                continue
            yy = y + 4 + j * 13
            o.append(f'<path class="{cls}" d="{bar_path(X(0), X(v), yy, 11)}"><title>{esc(p["name"])}: {pct(v)} '
                     f'({"last 30 days" if k == "var30" else "year to date"})</title></path>')
            tx = X(v) + (4 if v >= 0 else -4)
            o.append(f'<text class="ne-m" x="{tx:.1f}" y="{yy + 9.5}" text-anchor="{"start" if v >= 0 else "end"}">{pct(v, 0)}</text>')
    o.append("</svg>")
    return "".join(o)


def chart_storage(V, wide=True):
    st = V["storage"]
    w = 680 if wide else 360
    panels = [("de", "Germany"), ("nl", "Netherlands")]
    pw_, ph = (310, 200) if wide else (330, 170)
    h = 60 + (ph + 40) * (1 if wide else 2) + 20
    o = [svg_open(w, h, "Gas storage fill, Germany and the Netherlands",
                  "Daily fill level in per cent, current year against previous year, with the EU 90% target.", "ch2" + ("w" if wide else "n"))]
    yr = d(st["de"]["date"]).year
    o.append(f'<text class="ne-t" x="12" y="22">Gas storage fill, % of capacity</text>')
    o.append(f'<line class="ne-k1" x1="12" x2="30" y1="39" y2="39" stroke-width="2.5"/><text class="ne-l" x="35" y="43">{yr}</text>')
    o.append(f'<line class="ne-k2" x1="80" x2="98" y1="39" y2="39" stroke-width="2" stroke-dasharray="5 3"/><text class="ne-l" x="103" y="43">{yr - 1}</text>')
    o.append(f'<line class="ne-z" x1="150" x2="168" y1="39" y2="39" stroke-dasharray="2 3"/><text class="ne-l" x="173" y="43">EU target 90%</text>')
    for i, (c, name) in enumerate(panels):
        ox = 12 + (i * (pw_ + 34) if wide else 0)
        oy = 60 + (0 if wide else i * (ph + 40))
        x0, x1, y0, y1 = ox + 30, ox + pw_ - 6, oy + 18, oy + ph
        X = lambda doy: x0 + (doy - 1) / 365 * (x1 - x0)
        Y = lambda v: y1 - v / 100 * (y1 - y0)
        o.append(f'<text class="ne-l" x="{ox}" y="{oy + 8}" font-weight="600">{name}</text>')
        for t in [0, 25, 50, 75, 100]:
            o.append(f'<line class="ne-g" x1="{x0}" x2="{x1}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/><text class="ne-m" x="{x0 - 4}" y="{Y(t) + 4:.1f}" text-anchor="end">{t}</text>')
        o.append(f'<line class="ne-z" x1="{x0}" x2="{x1}" y1="{Y(90):.1f}" y2="{Y(90):.1f}" stroke-dasharray="2 3"/>')
        for m in [1, 4, 7, 10]:
            doy = dt.date(yr, m, 1).timetuple().tm_yday
            o.append(f'<text class="ne-m" x="{X(doy):.1f}" y="{y1 + 14}" text-anchor="middle">{MON[m - 1]}</text>')
        for y, cls, dash, sw in [(yr - 1, "ne-k2", ' stroke-dasharray="5 3"', 2), (yr, "ne-k1", "", 2.5)]:
            pts = [(dt.date.fromisoformat(k).timetuple().tm_yday, v) for k, v in st[c]["series"] if k.startswith(str(y))]
            if not pts:
                continue
            path = "M" + " L".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in pts)
            o.append(f'<path d="{path}" fill="none" class="{cls}" stroke-width="{sw}"{dash} stroke-linejoin="round"/>')
        lx, lv = st[c]["date"], st[c]["pct"]
        xx, yy = X(d(lx).timetuple().tm_yday), Y(lv)
        o.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="4" class="ne-s1"><title>{name}, {date_en(lx)}: {num(lv, 2)}%</title></circle>')
        o.append(f'<text class="ne-m ne-h" x="{xx - 8:.1f}" y="{yy - 12:.1f}" text-anchor="end">{num(lv, 1)}%</text>')
    o.append("</svg>")
    return "".join(o)


def chart_wind(V, wide=True):
    C = sorted(V["wind_countries"], key=lambda c: -(c["obiettivo_2030_gw"] or 0))
    w = 680 if wide else 360
    left = 118 if wide else 84
    right = 30
    rowh = 40
    top = 70
    h = top + rowh * len(C) + 34
    hi = max(max(c["obiettivo_2030_gw"] or 0 for c in C), max(c["previsione_2030_mw"] / 1000 for c in C))
    hi = 10 * (-(-hi // 10))
    X = lambda v: left + v / hi * (w - left - right)
    o = [svg_open(w, h, "Offshore wind: installed, 2030 forecast and national target",
                  "GW by country: installed at end-2025, WindEurope 2030 forecast, national target (2030; Netherlands end-2032).", "ch3" + ("w" if wide else "n"))]
    o.append('<text class="ne-t" x="12" y="22">Offshore wind, GW</text>')
    o.append('<rect class="ne-s2" x="12" y="34" width="12" height="10" rx="2"/><text class="ne-l" x="30" y="43">installed end-2025</text>')
    o.append(f'<rect class="ne-s3" x="{150 if wide else 140}" y="34" width="12" height="10" rx="2"/><text class="ne-l" x="{168 if wide else 158}" y="43">forecast 2030</text>')
    lx = 280 if wide else 12
    ly = 34 if wide else 52
    o.append(f'<line class="ne-k1" x1="{lx + 6}" x2="{lx + 6}" y1="{ly - 2}" y2="{ly + 12}" stroke-width="3"/><text class="ne-l" x="{lx + 16}" y="{ly + 9}">target (2030; NL end-2032)</text>')
    for t in ticks(0, hi, 10):
        o.append(f'<line class="ne-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 6}" y2="{h - 26}"/><text class="ne-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{int(t)}</text>')
    names = {"GB": "UK", "DE": "Germany", "NL": "Netherlands", "DK": "Denmark", "BE": "Belgium", "PL": "Poland", "FR": "France", "NO": "Norway"}
    for i, c in enumerate(C):
        y = top + i * rowh
        inst, fc, tg = c["installato_fine2025_mw"] / 1000, c["previsione_2030_mw"] / 1000, c["obiettivo_2030_gw"]
        o.append(f'<text class="ne-l" x="{left - 8}" y="{y + 19}" text-anchor="end">{names[c["paese"]]}</text>')
        o.append(f'<path class="ne-s2" d="{bar_path(X(0), X(inst), y + 4, 12)}"><title>{names[c["paese"]]}: {num(inst, 1)} GW installed (end-2025)</title></path>')
        o.append(f'<path class="ne-s3" d="{bar_path(X(0), X(fc), y + 18, 12)}"><title>{names[c["paese"]]}: {num(fc, 1)} GW forecast for 2030</title></path>')
        lx_ = X(fc) + 4
        if tg and 0 <= X(tg) - X(fc) <= 28:
            lx_ = X(tg) + 5
        o.append(f'<text class="ne-m" x="{lx_:.1f}" y="{y + 28}">{num(fc, 1)}</text>')
        if tg:
            o.append(f'<line class="ne-k1" x1="{X(tg):.1f}" x2="{X(tg):.1f}" y1="{y + 1}" y2="{y + 33}" stroke-width="3"><title>{names[c["paese"]]}: target {num(tg, 1)} GW {"by end-" + str(c["anno_obiettivo"]) if c.get("anno_obiettivo") else "in 2030"}</title></line>')
            o.append(f'<text class="ne-m" x="{X(tg) + 5:.1f}" y="{y + 13}">{num(tg, 1) if tg % 1 else int(tg)}</text>')
    o.append("</svg>")
    return "".join(o)


def chart_costs(V, wide=True):
    a, b, ins = V["ex_asia"], V["ex_intra"], V["ins"]
    rows = [("Asia → Rotterdam", "last extra-EU leg, 4,000 t VLSFO",
             [("fuel", a["costo_carburante_eur"], "ne-s2"), ("EU ETS", a["costo_ets_eur"], "ne-s1"),
              ("FuelEU (max)", a["costo_fueleu_max_eur"], "ne-s3"), ("war risk, Red Sea", ins["mid_eur"], "ne-s4")]),
            ("Rotterdam → Genoa", "intra-EU voyage, 1,000 t VLSFO",
             [("fuel", b["costo_carburante_eur"], "ne-s2"), ("EU ETS", b["costo_ets_eur"], "ne-s1"),
              ("FuelEU (max)", b["costo_fueleu_max_eur"], "ne-s3")])]
    w = 680 if wide else 360
    left, right = 16, 20
    top = 92 if wide else 110
    h = top + 2 * 74 + 30
    tot = max(sum(x[1] for x in r[2]) for r in rows) / 1e6
    hi = (int(tot) + 1)
    X = lambda v: left + v / hi * (w - left - right)
    o = [svg_open(w, h, "Cost stack of a voyage", "Stacked bars in million euro: fuel, EU ETS, FuelEU penalty cap and war-risk premium.", "ch4" + ("w" if wide else "n"))]
    o.append('<text class="ne-t" x="12" y="22">Cost stack of a voyage, € million</text>')
    leg = [("fuel", "ne-s2"), ("EU ETS", "ne-s1"), ("FuelEU (max penalty)", "ne-s3"), ("war risk, Red Sea", "ne-s4")]
    x, y = 12, 40
    for nm, cls in leg:
        wd = 30 + len(nm) * 6.6
        if x + wd > w - 10:
            x, y = 12, y + 18
        o.append(f'<rect class="{cls}" x="{x}" y="{y}" width="12" height="10" rx="2"/><text class="ne-l" x="{x + 17}" y="{y + 9}">{nm}</text>')
        x += wd + 8
    for t in ticks(0, hi, 1 if hi <= 6 else 2):
        o.append(f'<line class="ne-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 8}" y2="{h - 26}"/><text class="ne-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{int(t)}</text>')
    for i, (nm, sub, segs) in enumerate(rows):
        y = top + i * 74
        o.append(f'<text class="ne-l" x="{left}" y="{y + 4}" font-weight="600">{esc(nm)}</text><text class="ne-m" x="{left}" y="{y + 18}">{esc(sub)}</text>')
        x0 = 0.0
        for k, (lab, v, cls) in enumerate(segs):
            xa, xb = X(x0 / 1e6), X((x0 + v) / 1e6)
            gap = 1 if k else 0
            last = k == len(segs) - 1
            dpath = bar_path(xa + gap, xb, y + 26, 22) if last else f'M{xa + gap:.1f},{y + 26}H{xb - 1:.1f}V{y + 48}H{xa + gap:.1f}Z'
            o.append(f'<path class="{cls}" d="{dpath}"><title>{esc(nm)}: {lab} € {num(v / 1e6, 2)} million</title></path>')
            x0 += v
        o.append(f'<text class="ne-m" x="{X(x0 / 1e6) + 5:.1f}" y="{y + 41}">{num(x0 / 1e6, 2)}</text>')
    o.append("</svg>")
    return "".join(o)


def table_html(head, rows):
    return ('<div class="tabella"><table><thead><tr>' + "".join(f"<th>{esc(x)}</th>" for x in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")


# =====================================================================================
# Text blocks
# =====================================================================================
def blocks(V, edition):
    B = []
    F = V["F"]
    T = V["top10"]
    pm = V["pmap"]
    rtm, anr = pm["rotterdam"], pm["anversa-bruges"]
    st = V["storage"]
    ttf = V["ttf"]
    eu = V["wind_eu"]
    esb = V["wind_decl"]["esbjerg"]["calcolo"]
    mar = V["wind_decl"]["marienborg"]
    a, b = V["ex_asia"], V["ex_intra"]
    eua = V["eua"]
    gof = V["gof"]
    prim, ust = pm["primorsk"], pm["ust-luga"]
    ores = V["oresund"]
    gmin, gmax = V["gnss_min"], V["gnss_max"]
    pn_link = data_link("porti-nord.json")
    gamma = next(x for x in V["auctions"] if "Gamma" in x["nome"])
    need(gamma["esito"], "26/11-10/12/2026", where="eolico-filiera aste Gamma")
    flat = [p for p in T if p["ytd"] is not None and abs(p["ytd"]) < 5]
    fuel_share_intra = (b["ets_per_t_carburante_bruciato_eur"] + b["fueleu_per_t_carburante_bruciato_eur"]) / (b["costo_carburante_eur"] / 1000) * 100
    fuel_eur_t_ext = a["costo_carburante_eur"] / 4000
    fuel_share_ext = (a["ets_per_t_carburante_bruciato_eur"] + a["fueleu_per_t_carburante_bruciato_eur"]) / fuel_eur_t_ext * 100
    V["shares"] = (fuel_share_intra, fuel_share_ext)

    n_cab = len([c for c in V["cables"] if c["data_evento"] >= "2024-11"]) + len(V["cables_extra"])
    # ------------------------------------------------------------------ 1
    B.append(("h2", "key-points", "1. Key points"))
    B.append(("ul", [
        f"**Rotterdam's traffic is flat on the year; the weekly drop is noise.** From 1 January to {date_en(rtm['last'])}, Rotterdam averaged "
        f"{num(rtm['ytd_now'])} ship calls a day, {pct(rtm['ytd'])} on the same days of 2025; Antwerp-Bruges {pct(anr['ytd'])}. "
        f"The {pct(rtm['var7'])} in Rotterdam's latest week is noise. The clear fall is at Russia's oil port of Primorsk, {pct(prim['ytd'], 0)} (IMF PortWatch).",
        f"**German and Dutch gas storage is far below normal before winter.** On {date_en(st['de']['date'])} Germany was "
        f"{num(st['de']['pct'])}% full and the Netherlands {num(st['nl']['pct'])}%, against an EU goal of 90%. Germany is "
        f"{num(abs(st['de']['yoy_pp']))} points below a year ago (GIE AGSI+). The TTF gas price is {num(ttf['ultimo'], 2)} €/MWh, "
        f"{long_change(ttf)}.",
        f"**Offshore wind will reach under half of the North Sea goal for 2030.** Europe connected only "
        f"{num(eu['aggiunto_2025_mw'] / 1000, 2)} GW in 2025. For Denmark, Germany, the Netherlands and Belgium WindEurope expects "
        f"{num(esb['previsione_2030_gw_paesi'])} GW in 2030, {num(esb['quota_obiettivo_2030_previsto_pct'], 0)}% of the 65 GW promised at Esbjerg.",
        f"**Carbon rules now add a fifth to a half of fuel costs.** At the EU auction price of {num(eua['prezzo_eur'], 2)} €/t "
        f"({date_en(eua['data'])}), the EU ETS costs {num(b['ets_per_t_carburante_bruciato_eur'], 0)} € per tonne of fuel burnt "
        f"on voyages between EU ports and {num(a['ets_per_t_carburante_bruciato_eur'], 0)} € on voyages to or from outside the EU (bunker-emissioni.json).",
        f"**Sabotage risk sits in the Baltic, above all the Gulf of Finland.** In the AIS snapshot of {date_en(V['navi_date'])}, "
        f"{gof['sanzionate']} of the {gof['navi']} ships seen there were on Western sanction lists. Since November 2024 "
        f"{WORDS.get(n_cab, n_cab)} Baltic cable incidents have been recorded. GPS jamming hit {gmin}–{gmax} areas a day "
        f"in the week to {date_en(V['gnss']['periodo'][1])} (GPSJam).",
    ]))

    # ------------------------------------------------------------------ 2 ports
    B.append(("h2", "ports", "2. Port traffic: the ten biggest North Sea and Baltic ports"))
    B.append(("p", f"The ten ports are the largest by tonnes handled in 2025 among the 30 in {pn_link}, with the annual figure "
                   f"from each port authority. **Ship calls** are estimated by IMF PortWatch from AIS transponder signals; the latest "
                   f"day available is {date_en(V['ports_last'])} (about ten days' delay). Changes compare the same days of the previous year."))
    rows = []
    for p in T:
        src = p["mt_src"]
        ty = p["types"]
        rows.append([p["name"], PAESE.get(p["country"], p["country"]),
                     link(num(p["mt"], 1), src.get("link")) + (f" ({pct(p['mt_var'], 1)})" if p["mt_var"] is not None else ""),
                     num(p["calls30"]), pct(p["var30"]), pct(p["ytd"]),
                     pct(ty["tanker"]["var"], 0), pct(ty["container"]["var"], 0), pct(ty["dry_bulk"]["var"], 0)])
    B.append(("tab", ["Port", "Country", "2025, Mt (y/y)", "Calls/day, 30 days", "30 days y/y", "Year to date y/y",
                      "Tankers 30d", "Container 30d", "Dry bulk 30d"], rows,
              f"Mt = million tonnes, as published by each port (links). Calls: PortWatch, 30 days to {date_en(V['ports_last'])} and 1 January to "
              f"{date_en(V['ports_last'])}, both against the same days of 2025 ({pn_link}). By vessel type, 30-day averages; "
              f"«n/a» where the year-earlier base is under one call a day. Primorsk and Gothenburg are missing from the ranking because the "
              f"file has no 2025 total in tonnes for them; Wilhelmshaven reports only containers."))
    B.append(("fig", "ports", f"**Port calls, change on a year earlier, %.** Ten largest ports by 2025 tonnage. Pink: 30-day average to "
                              f"{date_en(V['ports_last'])}; blue: 1 January to {date_en(V['ports_last'])}. Source: IMF PortWatch via {pn_link}, data to "
                              f"{date_en(V['ports_last'])}."))
    up = sorted([p for p in T if p["ytd"] is not None], key=lambda p: -p["ytd"])
    B.append(("p", f"**What the numbers say.** Over the year to date {WORDS.get(len(flat), len(flat))} of the ten ports are within ±5% of 2025. The biggest falls are "
                   f"{up[-1]['name']} ({pct(up[-1]['ytd'])}) and {up[-2]['name']} ({pct(up[-2]['ytd'])}); the biggest rise is "
                   f"{up[0]['name']} ({pct(up[0]['ytd'])}). The weekly figures swing much more: Rotterdam is {pct(rtm['var7'])} on the "
                   f"week to {date_en(rtm['p7'][1])} but {pct(rtm['var30'])} on 30 days. Calls count ships, not cargo: a port can handle fewer, larger ships."))
    rtm_teu = rtm["teu"]
    gd = pm["danzica"]["teu"]
    ham = pm["amburgo"]["teu"]
    wil = [t for t in pm["wilhelmshaven"]["traffic"] if "TEU" in t["unita"]][0]
    B.append(("p", f"**Containers moved east and to deep water in 2025.** Rotterdam handled {num(rtm_teu['valore'], 2)} million TEU "
                   f"({pct(rtm_teu['var_pct'])}), Hamburg {num(ham['valore'], 1)} million ({pct(ham['var_pct'])}), Wilhelmshaven "
                   f"{num(wil['valore'], 2)} million ({pct(wil['var_pct'], 0)}) and Gdańsk {num(gd['valore'], 2)} million ({pct(gd['var_pct'], 0)}), "
                   f"according to the port authorities ({pn_link}). TEU is the 20-foot container unit."))
    B.append(("p", f"**Russia's Baltic oil ports.** Primorsk averaged {num(prim['ytd_now'])} calls a day this year against "
                   f"{num(prim['ytd_prev'])} in 2025 ({pct(prim['ytd'], 0)}); Ust-Luga {pct(ust['ytd'])}. Ukrainian drones hit Primorsk on "
                   f"23 March and Ust-Luga on 29 March, and the Baltic oil ports again in July 2026 (baltico-sicurezza.json). PortWatch does not see ships with AIS switched off, so "
                   f"Russian ports are undercounted."))
    rv = V["rtm_vol"]["trimestri"]
    if abs(V["rtm_vol"].get("calcolato", {}).get("var_9_mesi_pct", 0) - round(V["rtm_bunker_9m"], 1)) > 0.05:
        warn("Rotterdam bunker 9-month change differs from the file's own calculation")
    B.append(("val", f"*Assessment.* Three forces probably drive the pattern. First, some Asia–Europe services have returned to Suez "
                     f"(transits {pct(V['suez']['var7_anno_pct']['n_total'])} on a year, portwatch.json); this may add Mediterranean calls before "
                     f"the North Sea and keep Rotterdam and Antwerp flat. Second, the Baltic is redistributing: Polish ports hold or gain, ports that "
                     f"lived on Russian transit (HaminaKotka {pct(pm['hamina-kotka']['ytd'], 0)}, Riga {pct(pm['riga']['ytd'], 0)} year to date) lose. "
                     f"Third, energy: tanker calls follow the oil and LNG trade, and Rotterdam lost bunker sales "
                     f"({pct(V['rtm_bunker_9m'])} in tonnes of oil and bio-blends in the first nine months of {V['rtm_bunker_year']}, {pct(V['rtm_bunker_9m_lng'])} counting LNG; Port of Rotterdam via bunker-emissioni.json). These are links we draw; the data do not prove causation."))

    # ------------------------------------------------------------------ 3 energy
    B.append(("h2", "energy", "3. Energy: gas storage, LNG, TTF and power links"))
    B.append(("h3", "Gas storage"))
    dkpl = V["dkpl"]
    rows = []
    for c, name in [("de", "Germany"), ("nl", "Netherlands")]:
        s = st[c]
        rows.append([name, f"{num(s['pct'], 2)}% ({date_short(s['date'])})", f"{num(s['twh'], 1)} TWh", pp(s["yoy_pp"]),
                     pp(s["vs5"]), pp(s["to_target"]), "GIE AGSI+ (daily)"])
    for g, name in [("DK", "Denmark"), ("PL", "Poland")]:
        if g in dkpl:
            x = dkpl[g]
            rows.append([name, "n/a (no fill % without capacity)", f"{num(x['twh'], 2)} TWh (end {date_en(x['month'])})",
                         pct(x["yoy"]) + " in TWh", "n/a", "n/a", "Eurostat (monthly)"])
        else:
            rows.append([name, "missing", "missing", "", "", "", "—"])
    B.append(("tab", ["Country", "Fill", "Gas in storage", "vs a year ago", "vs 5-year average", "vs 90% target", "Source"], rows,
              f"pp = percentage points. Germany and the Netherlands: {data_link('scorte.json')} (GIE AGSI+, {date_en(st['de']['date'])}). "
              f"Denmark and Poland: Eurostat nrg_stk_gasm, end-of-month stock on national territory, read by this script "
              f"(report/dati/eurostat-gas-nord.json); AGSI+ daily fill for these two countries needs an API key the monitor does not have."))
    B.append(("fig", "storage", f"**Gas storage fill, % of working capacity, Germany and the Netherlands,** daily, {d(st['de']['date']).year} "
                                f"against {d(st['de']['date']).year - 1}; dotted line: EU 90% target. Source: GIE AGSI+ via {data_link('scorte.json')}, data to {date_en(st['de']['date'])}."))
    de, nl = st["de"], st["nl"]
    B.append(("p", f"Both countries are drawing gas already: over the last two weeks German storage fell by "
                   f"{num(abs(de['slope']), 2)} points a day and Dutch by {num(abs(nl['slope']), 2)}. At that pace Germany would be near "
                   f"{num(de['proj_dec1'], 0)}% and the Netherlands near {num(nl['proj_dec1'], 0)}% on 1 December (straight-line projection by this script, "
                   f"not a forecast: cold weather speeds withdrawals). The EU as a whole held {num(V['eu_stock']['valore'], 0)} TWh at the end of "
                   f"{date_en(V['eu_stock']['data'][:7])}, {pct(V['eu_stock']['anno_scorso']['variazione_pct'])} on a year (Eurostat, {data_link('scorte.json')})."))
    if "DK" in dkpl and "PL" in dkpl:
        B.append(("p", f"Denmark and Poland look better. At the end of {date_en(dkpl['DK']['month'])} Danish stocks were {num(dkpl['DK']['twh'], 2)} TWh, "
                       f"{pct(dkpl['DK']['yoy'], 0)} on a year; Polish stocks {num(dkpl['PL']['twh'], 1)} TWh, {pct(dkpl['PL']['yoy'])} "
                       f"(Eurostat, updated {date_en(V['eurostat']['updated'][:10])}). Denmark is a net gas exporter again thanks to the Tyra field "
                       f"(up to 2.8 bcm a year against consumption of 1.4 bcm, {data_link('esposizione-nord.json')}); Poland receives Norwegian gas through Baltic Pipe."))
    B.append(("h3", "LNG and the US share"))
    ex = V["exp"]
    rows = []
    for c in ["DE", "NL", "PL", "LT"]:
        g = ex[c]["gnl"]
        rg = ex[c]["gnl_rigassificazione_operativa"] or {}
        rows.append([PAESE[c], f"{g['quota_usa_pct']}%" + (f" (Qatar {g['quota_qatar_pct']}%)" if g.get("quota_qatar_pct") else ""),
                     re.sub(r"(\d),(\d)", r"\1.\2", g["periodo"]).replace("1° trimestre", "Q1").replace("anno", "year").replace("carichi", "cargoes").replace("rigassificati", "regasified").replace("la più alta in Europa", "highest in Europe"),
                     f"{num(rg.get('mld_m3_anno'), 1)} bcm/y ({rg.get('terminali')})", link(re.sub(r",? maggio 2026", ", May 2026", g["fonte"].split(" (")[0]), g.get("link"))])
    B.append(("tab", ["Country", "US share of LNG", "Period", "Operating import capacity (terminals)", "Source"], rows,
              f"bcm = billion cubic metres. Capacity: Global Energy Monitor via {data_link('terminali-gnl.json')} and {data_link('esposizione-nord.json')}. "
              f"Germany's figure still counts the Mukran floating terminal, which IEEFA reports has left for Egypt: the real German capacity is lower."))
    E = EXTERNAL["ieefa_eu_us_share"]
    B.append(("p", f"Europe-wide, {E['text']} ({link('IEEFA', E['link'])}, {date_en(E['date'])}; not verified against the source in review). "
                   f"Norway remains the EU's largest gas supplier: 30.9% of EU gas imports in 2025, 89.3 bcm ({data_link('esposizione-nord.json')}, Council of the EU). "
                   f"The Netherlands closed the Groningen field by law on 1 October 2024."))
    B.append(("h3", "TTF price"))
    B.append(("p", f"The **TTF**, the Dutch hub price that sets gas prices for most of Europe, closed at {num(ttf['ultimo'], 2)} €/MWh on "
                   f"{date_en(ttf['data'])} (front-month future, {'provisional close' if ttf.get('provvisorio') else 'daily close; the live session of the day of reading is left out'}): {pct(ttf['var']['1g'])} on the day, {pct(ttf['var']['1m'])} on a month "
                   f"and {long_change(ttf)}. US Henry Hub was {num(V['hh']['ultimo'], 3)} $/MMBtu. Converted at "
                   f"{num(V['eurusd']['ultimo'], 4)} $/€, TTF equals {num(V['ttf_usd_mmbtu'], 1)} $/MMBtu: the transatlantic gap of about "
                   f"{num(V['spread'], 0)} $/MMBtu is what pulls US cargoes to Europe (calculation by this script; {data_link('prezzi.json')}, Yahoo Finance)."))
    B.append(("h3", "Power links"))
    uc = V["hvdc_uc"]
    e2 = V["estlink2"]
    need(e2.get("note", ""), "25 dicembre 2024", "giugno 2025", where="interconnessioni Estlink 2")
    need(ex["NL"]["cavi_interconnessioni"], "NorNed (700 MW", "COBRAcable (700 MW", where="esposizione NL")
    need(ex["DK"]["cavi_interconnessioni"], "Viking Link (1,4 GW", where="esposizione DK")
    need(ex["DE"]["cavi_interconnessioni"], "NordLink (1,4 GW", where="esposizione DE")
    B.append(("p", f"North Sea countries trade power through subsea direct-current (HVDC) cables: NorNed (700 MW) and COBRAcable (700 MW) from the "
                   f"Netherlands, Viking Link (1.4 GW, Denmark–UK) and NordLink (1.4 GW, Norway–Germany) ({data_link('esposizione-nord.json')}). "
                   f"OpenStreetMap shows these HVDC export and interconnector cables under construction: "
                   + ", ".join(sorted(k.replace("Bornholm-Deutschland", "Bornholm–Germany") for k in uc)) + f" ({data_link('rete-elettrica.json')}). In the Baltic, Estlink 2 (650 MW, Estonia–Finland) was cut by "
                   f"the anchor of the Eagle S on 25 December 2024 and restored in June 2025 ({data_link('interconnessioni.json')})."))
    B.append(("val", f"*Assessment.* The winter risk for North-West Europe is storage, not supply routes. German storage is "
                     f"{num(abs(de['vs5']), 0)} points below its five-year average and most LNG comes from the US. So the TTF depends on two "
                     f"things a port or energy company cannot control: winter temperatures and the Qatar outage linked to the Strait of Hormuz "
                     f"(rated «{LEVEL.get(V['risk']['gnl-qatar']['livello'])}» on the monitor's {data_link('rischio.json')})."))

    # ------------------------------------------------------------------ 4 wind
    B.append(("h2", "wind", "4. Offshore wind: installed, auctions, bottlenecks"))
    ws = V["wind_src"]
    B.append(("p", f"Europe had {num(eu['installato_fine2025_mw'] / 1000)} GW of offshore wind at the end of 2025 and added "
                   f"{num(eu['aggiunto_2025_mw'] / 1000, 2)} GW during the year, the lowest since 2016. WindEurope expects "
                   f"{num(eu['previsione_2030_mw'] / 1000)} GW in 2030 ({link('WindEurope', ws['link'])}, {date_en(ws['data_fonte'])}, via {data_link('eolico-filiera.json')})."))
    nl_t = next(c for c in V["wind_countries"] if c["paese"] == "NL")
    need(f"{nl_t['obiettivo_2030_gw']} {nl_t.get('anno_obiettivo')} {nl_t['fonte_obiettivo']}", "21 2032", "intorno al 2030", where="Dutch target year")
    B.append(("fig", "wind", f"**Offshore wind by country, GW:** installed at the end of 2025, WindEurope forecast for 2030 and national target "
                             f"(pink tick). Targets are for 2030 except the Dutch 21 GW, due by end-2032 since 2024 (the March 2026 letter to Parliament still says "
                             f"'around 2030'). National totals, so Germany and Denmark include the Baltic and the UK the Irish Sea. "
                             f"Source: WindEurope 2025 Statistics (February 2026) and national targets, via {data_link('eolico-filiera.json')}."))
    rows = []
    for k in ["esbjerg", "ostenda", "marienborg"]:
        x = V["wind_decl"][k]
        c = x["calcolo"]
        rows.append([{"esbjerg": "Esbjerg (2022)", "ostenda": "Ostend (2023)", "marienborg": "Marienborg, Baltic (2022)"}[k],
                     f"{num(x['obiettivo_2030_gw'], 1)} GW", f"{num(c['installato_fine2025_gw_paesi'], 2)} GW",
                     f"{num(c['previsione_2030_gw_paesi'], 2)} GW", f"{num(c['quota_obiettivo_2030_previsto_pct'], 0)}%"])
    B.append(("tab", ["Declaration", "2030 goal", "Installed end-2025", "Forecast 2030", "Forecast as % of goal"], rows,
              "Sums of national WindEurope figures for the signatories (Marienborg: only countries with a mainly Baltic coast, "
              "without Germany and Denmark). Calculation in eolico-filiera.json; national totals overstate the single sea basin."))
    bm = V["baltic_mw"]
    B.append(("p", f"For the Baltic as a whole the EMODnet map gives {num(bm.get('operativo', 0) / 1000, 1)} GW operating and "
                   f"{num(bm.get('in costruzione', 0) / 1000, 1)} GW under construction, mostly Polish, against the "
                   f"{num(mar['obiettivo_2030_gw'], 1)} GW promised at Marienborg ({data_link('offshore-nord.json')}; EMODnet status can lag reality)."))
    B.append(("h3", "Auctions"))
    rows = []
    for x in V["auctions"]:
        rows.append([x["data"], PAESE.get(x["paese"], x["paese"]), it2en(x["nome"]), num(x["gw"], 1) if x.get("gw") else "—",
                     MECH.get(x["meccanismo"], x["meccanismo"]), link(outcome_en(x["esito"]), x["link"])])
    B.append(("tab", ["Date", "Country", "Round", "GW", "Mechanism", "Outcome"], rows,
              f"From {data_link('eolico-filiera.json')} (curated, one source per round). Negative bidding: the developer pays the state for the site. "
              "Two-sided CfD: the state guarantees a strike price and pays or collects the difference with the market price."))
    B.append(("p", f"The pattern is clear in the data: rounds where the developer pays the state for the site failed in Denmark (3 GW, December 2024), "
                   f"Germany (2.5 GW, August 2025) and the Netherlands (1 GW, October 2025), with no bids. Rounds with a **two-sided contract for "
                   f"difference (CfD)** worked. Under a CfD the state guarantees a fixed price and pays or collects the difference with the market. The UK "
                   f"awarded 8.4 GW in January 2026, Poland 3.4 GW in December 2025 and Denmark 1.8 GW in August 2026, signed on 6 November 2026. "
                   f"Next: the Dutch IJmuiden Ver Gamma-A and Gamma-B rounds (2 GW) take applications from 26 November to 10 December 2026 (RVO, secondary source)."))
    B.append(("h3", "Bottlenecks"))
    bt = V["bottle"]
    items = []
    for k, label in [("aste-ricavi", "Auctions and cost of capital"), ("cavi-hvdc", "HVDC cables"),
                     ("convertitori-hvdc", "HVDC converter platforms"), ("turbine", "Turbines"), ("navi", "Vessels"),
                     ("porti", "Ports"), ("fondazioni", "Foundations")]:
        c = bt[k]
        ind = c["indicatori"][0]
        tens = {"alta": "high", "media": "medium", "eccesso di capacita'": "overcapacity"}.get(c["tensione"], c["tensione"])
        val = ind["valore"]
        lab, unit = BOTTLE_EN[k]
        if k == "convertitori-hvdc":
            val = date_en(val)
        extra = ""
        if k == "turbine":
            need(ind["nome"], "Q3 esercizio 2026", where="eolico-filiera turbine Siemens Gamesa Q3")
            val = f"+{val}"
            gev = next(i for i in c["indicatori"] if i["nome"] == "GE Vernova: EBITDA segmento eolico Q3 2026")
            need(gev["nota"], "-61", "400-500", where="eolico-filiera turbine GE Vernova Q3")
            extra = (f" GE Vernova's wind segment earned +{num(gev['valore'], 0)} million $ (EBITDA) in Q3 2026, against −61 million a year earlier, "
                     f"but GE now guides a 2026 wind loss of 400–500 million $ ({link('GE Vernova', gev.get('link'))}, {date_en(gev['data'])}).")
        if k == "porti":
            need(ind["unita"], "almeno", where="eolico-filiera porti investimenti")
            val = f"at least {num(val, 0)}"
        items.append(f"**{label}** — strain: {tens}. {lab}: {val}{unit} ({link(ind['fonte'], ind.get('link'))}, {date_en(ind['data'])}).{extra}")
    B.append(("ul", items))
    B.append(("p", "In plain terms: Prysmian holds about 16.5 billion € of "
                   "transmission orders (29 October 2026) and NKT 13.0 billion (30 June 2026). New HVDC cable capacity is booked for years. "
                   "Amprion's 2 GW BalWin1 grid link slipped from September 2030 to 15 September 2031 because of extra work on the offshore converter "
                   "platform. European monopile factories, by contrast, will run at about 32% of capacity in 2026 and 19% in 2028 (Rystad)."))
    for tok in ["16.5", "13.0"]:
        need(json.dumps([bt["cavi-hvdc"]["indicatori"]]), tok, where="eolico-filiera cavi")
    need(json.dumps(bt["convertitori-hvdc"]), "2031-09-15", "16/09/2030", where="eolico-filiera convertitori")
    need(json.dumps(bt["fondazioni"]), "32%", "19", where="eolico-filiera fondazioni")
    B.append(("h3", "Ports and vessels"))
    wp = V["wind_ports"]
    esb_p = [t for t in pm["esbjerg"]["traffic"] if "GW" in t["unita"]][0]
    fl = {x["indicatore"][:20]: x for x in V["fleet"]}
    cad = next(x for x in V["fleet"] if x["indicatore"].startswith("Cadeler"))
    need(cad["valore"], "66%", "2,5 miliardi", where="flotta Cadeler")
    need(json.dumps(bt["porti"]), "45", "1250", where="colli porti")
    B.append(("p", f"Esbjerg has shipped over {num(esb_p['valore'], 1)} GW of offshore wind in total ({link('Port Esbjerg', esb_p.get('link'))}). "
                   f"Rotterdam plans a 45-hectare wind terminal for mid-2029 and Cuxhaven a 1,250-metre heavy-load quay for about 2028, while the "
                   f"Bremerhaven terminal was never built ({data_link('eolico-filiera.json')}). Vessels are no longer the main constraint. Western installation "
                   f"ships able to handle 15 MW turbines go from zero in 2020 to more than 25 by 2028 (Intelatus). Cadeler, the market leader, used its "
                   f"fleet at 66% in the first half of 2026 and had a 2.5 billion € order book."))
    wc = F.get("wind-calendar.json")
    if wc:
        B += wind_calendar_section(wc)
    else:
        B.append(("p", "**Missing:** a dated calendar of offshore wind milestones (wind-calendar.json, being prepared by another agent; this report includes it automatically when it appears)."))
    B.append(("val", "*Assessment.* For a port the binding constraint is now the auction pipeline and the grid, not ships or steel. "
                     "Work is secured until 2027–2028; after that, demand depends on whether the Dutch December round attracts bids and on the "
                     "German auction reform, meant to take effect on 1 January 2027 if the Bundestag adopts it in time."))

    # ------------------------------------------------------------------ 5 costs
    B.append(("h2", "costs", "5. Shipping costs: fuel, carbon, insurance, freight, time"))
    bk = V["bunker"]
    rows = []
    for k, n in [("Rotterdam", "Rotterdam"), ("Anversa", "Antwerp"), ("Gibilterra", "Gibraltar"), ("Singapore", "Singapore"), ("Fujairah", "Fujairah")]:
        x = bk[k]
        rows.append([n, f"{num(x['ultimo'], 1)}", date_short(x["data"]), f"{num(x['valore_prima_guerra'], 1)}",
                     pct(x["var_da_prima_guerra_pct"], 0), pct(x["var_1a_pct"], 0)])
    B.append(("tab", ["Bunker hub", "VLSFO, $/t", "Date", "27 Feb 2026, $/t", "Since 27 Feb", "On a year"], rows,
              f"VLSFO = very low sulphur fuel oil, the standard marine fuel. 27 February 2026 is the last price before the war with Iran. "
              f"Source: Ship & Bunker via {data_link('bunker-emissioni.json')} (averages of quotes, not transactions)."))
    B.append(("p", f"**EU ETS and FuelEU.** Since 2026 shipping surrenders emission allowances (EUA) for 100% of its emissions, counted in full on "
                   f"voyages between EU ports and at half on voyages to or from outside the EU. At {num(eua['prezzo_eur'], 2)} €/t "
                   f"(EEX auction, {date_en(eua['data'])}; 2026 auction average {num(V['eua_mean'], 2)} €) that is {num(b['ets_per_t_carburante_bruciato_eur'], 0)} € "
                   f"per tonne of VLSFO burnt intra-EU and {num(a['ets_per_t_carburante_bruciato_eur'], 0)} € on extra-EU legs. **FuelEU Maritime** limits the "
                   f"greenhouse intensity of fuel; a ship running only on fossil fuel pays at most {num(b['fueleu_per_t_carburante_bruciato_eur'], 0)} € and "
                   f"{num(a['fueleu_per_t_carburante_bruciato_eur'], 0)} € per tonne. Together they equal about {num(fuel_share_intra, 0)}% of the fuel bill intra-EU "
                   f"and {num(fuel_share_ext, 0)}% on extra-EU legs ({data_link('bunker-emissioni.json')})."))
    ms = V["maersk"]
    B.append(("p", f"What carriers charge: Maersk's emissions surcharge for the fourth quarter is {ms['valori_usd_per_feu']['Estremo Oriente -> Nord Europa']} $ per "
                   f"40-foot container (FEU) from the Far East to North Europe, {num(ms['confronto_nolo']['quota_pct'], 1)}% of the Drewry Shanghai–Rotterdam "
                   f"rate of {num(ms['confronto_nolo']['wci_shanghai_rotterdam_usd_feu'], 0)} $ ({link('Maersk', ms['link'])}, {date_en(ms['data_fonte'])})."))
    ins = V["ins"]
    B.append(("fig", "costs", f"**Cost stack of a voyage, € million.** Top: last leg from an Asian port to Rotterdam burning 4,000 t of VLSFO bought in "
                              f"Singapore (an illustrative assumption, not a real ship), with ETS at 50% and the FuelEU penalty cap, plus one Red Sea war-risk "
                              f"premium at {num(ins['mid'], 2)}% of a {num(ins['hull_musd'], 1)} million $ hull. Bottom: an intra-EU voyage burning 1,000 t. "
                              f"Sources: {data_link('bunker-emissioni.json')} (bunker {date_en(a['prezzo_bunker_usd_t'] and V['bunker']['Singapore']['data'])}, "
                              f"EUA {date_en(eua['data'])}) and {data_link('assicurazioni.json')} (premium 24 September 2026)."))
    tot_a = a["costo_carburante_eur"] + a["costo_ets_eur"] + a["costo_fueleu_max_eur"] + ins["mid_eur"]
    B.append(("p", f"In the Asia–Rotterdam example fuel is {num(a['costo_carburante_eur'] / 1e6, 2)} million €, the ETS {num(a['costo_ets_eur'] / 1e6, 2)} million, "
                   f"FuelEU at most {num(a['costo_fueleu_max_eur'] / 1e6, 2)} million and one war-risk premium {num(ins['lo_eur'] / 1e6, 2)}–{num(ins['hi_eur'] / 1e6, 2)} million: "
                   f"{num(tot_a / 1e6, 2)} million in total with the mid premium. The insurance figure is approximate: the last public Red Sea quote "
                   f"({num(ins['lo'], 1)}–{num(ins['hi'], 1)}% of hull value, {date_en(V['war_last']['mar-rosso']['data'])}) is for tankers without Saudi ties, "
                   f"and the hull value is the price of a new {num(ins['teu'], 0)}-TEU ship, a maximum."))
    jr = V["jwc_russia"]
    need(jr["riferimento"], "Baltico compreso", where="assicurazioni russia")
    B.append(("p", f"**War-risk insurance in the Baltic.** The Joint War Committee of the London market lists all Russian ports, the Baltic ones included "
                   f"(Primorsk, Ust-Luga), as areas of heightened risk (circular {V['jwc']['id']} of {date_en(V['jwc']['data'])}, {data_link('assicurazioni.json')}): "
                   f"a ship calling there must notify its insurer and pay an additional premium. **Missing:** no public premium for Baltic calls was found. "
                   f"The coastal states face a different insurance risk: shadow-fleet tankers with unknown cover sail through Danish waters."))
    wci, fbx, ccfi = V["wci"], V["fbx"], V["ccfi"]
    B.append(("p", f"**Freight.** Drewry's index puts a 40-foot container from Shanghai at {num(wci['rotte']['Shanghai-Rotterdam'], 0)} $ to Rotterdam and "
                   f"{num(wci['rotte']['Shanghai-Genoa'], 0)} $ to Genoa ({date_en(wci['data'])}). The Freightos China–North Europe index (FBX11) is "
                   f"{num(fbx['rotte']['FBX11']['valore'], 0)} $ ({fbx['rotte']['FBX11']['var'].replace('-', '−')} on the week to {date_en(fbx['data'])}) and the "
                   f"Shanghai CCFI Europe index {num(ccfi['rotte']['EUROPE']['valore'], 2)} points ({pct(ccfi['rotte']['EUROPE']['var_pct'], 2)}) ({data_link('noli.json')})."))
    sz, cp = V["suez"], V["cape"]
    tt = F.get("transit-times.json")
    B.append(("h3", "Transit times to Rotterdam"))
    B.append(("p", f"Ships rerouted around the Cape of Good Hope need roughly 7,000 km and 14–24 days more between Asia "
                   f"and Europe than via Suez (UNCTAD 2024, in {data_link('stretti-dettaglio.json')}). In the week to {date_en(sz['ultima_data'])} the Suez Canal "
                   f"saw {num(sz['media7']['n_total'])} transits a day ({pct(sz['var7_anno_pct']['n_total'])} on a year) and the Cape {num(cp['media7']['n_total'])} "
                   f"({pct(cp['var7_anno_pct']['n_total'])}) ({data_link('portwatch.json')}). BIMCO counts 753,000 TEU a week of container capacity through Suez in early "
                   f"October 2026 against 1,457,000 in 2023: just over half of the pre-crisis level."))
    if tt:
        B += transit_section(tt)
    else:
        B.append(("p", "**Missing:** measured door-to-door or port-to-port transit times to Rotterdam (transit-times.json, being prepared by another agent; included automatically when it appears)."))
    fr = dict(V["h2_real"]["marittimo"]["fueleu"]["riduzione_intensita_ghg"])
    B.append(("val", f"*Assessment.* Fuel still dominates the voyage bill, but carbon is the cost that rises by rule: FuelEU's target tightens from "
                     f"{pct(fr['2025'], 0)} today to {pct(fr['2030'], 0)} in 2030 and {pct(fr['2035'], 1)} in 2035. For North Sea ports the competitive question is less the bunker price than "
                     f"where carriers place their last non-EU call before Europe."))

    # ------------------------------------------------------------------ 6 security
    B.append(("h2", "security", "6. Security: cables, drones, GPS jamming, shadow fleet"))
    B.append(("h3", "Cables and pipelines"))
    rows = []
    for c in V["cables"]:
        lab, ship = CABLE_EN.get(c["id"], (c["nome"], ""))
        need(c["causa"] + c["nome"], ship, where=f"cavi-incidenti {c['id']}")
        rows.append([date_short(c["data_evento"]), lab, f"anchor of the {ship} (suspected)" if ship else c["causa"][:80], link("source", c["link"])])
    for e in V["cables_extra"]:
        rows.append([date_short(e["data"]), "Šventoji (LT) – Liepāja (LV) data cable" if "Šventoji" in e["nome"] else e["nome"], "under investigation", link("source", e["link"])])
    B.append(("tab", ["Date", "Cable or pipeline", "Suspected cause", "Link"], rows,
              f"Baltic incidents in {data_link('cavi-incidenti.json')}, plus the Šventoji–Liepāja cable recorded so far only in {data_link('baltico-sicurezza.json')}. "
              "Causes are hypotheses of investigators or the press unless a court has ruled; intent is not proven in most cases."))
    fi = V["exp"]["FI"]["rischi"]
    need(json.dumps(fi, ensure_ascii=False), "42 mesi", "5 novembre 2026", where="esposizione FI")
    B.append(("p", f"On 5 November 2026 a Helsinki court sentenced the captain of the Fitburg to 42 months for the damage to the Helsinki–Tallinn cables "
                   f"(first instance, not final; {data_link('baltico-sicurezza.json')}, Euronews). The monitor's risk dashboard rates the Baltic cable "
                   f"corridor «{LEVEL.get(V['risk']['baltico']['livello'])}» ({num(V['risk']['baltico']['punteggio'], 1)} out of 25) ({data_link('rischio.json')})."))
    B.append(("h3", "Drones"))
    dr = [e for e in V["ev"] if e["categoria"].startswith("droni") and e["data"] >= "2025-09"]
    B.append(("p", f"{data_link('baltico-sicurezza.json')} records {len(dr)} drone events around North Sea and Baltic airports, bases, ports and energy sites "
                   f"since September 2025. Copenhagen airport closed for nearly four hours on 22 September 2025; drones flew over the Antwerp port area on "
                   f"6 November 2025 and over the Doel nuclear plant on 9 November 2025; on 4 August 2026 a drone carrying explosives hit an Antonov An-124 "
                   f"at Leipzig. On 18 October 2026 Lithuania closed Kaunas airport after detecting an unidentified flying object. On 25 June 2026 Copenhagen "
                   f"police said they could neither prove nor rule out that drones had been there on 22 September 2025 (Wikipedia and sources cited, "
                   f"reliability medium): an alarm alone can shut a hub."))
    need(" ".join(e["nome"] + " " + (e.get("esito") or "") for e in V["ev"]), "quasi quattro ore", "Anversa", "Doel", "Lipsia", "Kaunas",
         "25 giugno 2026", "né provare né escludere", where="droni")
    B.append(("h3", "GPS jamming (GNSS interference)"))
    gw = V["gnss_west"]
    B.append(("p", f"GNSS satellite navigation signals are jammed or spoofed daily in the eastern Baltic. GPSJam, which reads the navigation quality "
                   f"reported by aircraft, showed {gmin} to {gmax} map cells a day at a high level (over 10% of aircraft affected) between "
                   f"{date_en(V['gnss']['periodo'][0], False)} and {date_en(V['gnss']['periodo'][1])}. "
                   + (f"All were east of 17°E (Kaliningrad, Lithuania, the Gulf of Finland, eastern Poland). " if not gw else
                      f"Almost all were east of 17°E (Kaliningrad, Lithuania, the Gulf of Finland, eastern Poland); "
                      + ("one" if len(gw) == 1 else WORDS.get(len(gw), str(len(gw))))
                      + f" lay just west of it, at {', '.join(f'{c['lat']:.1f}°N {c['lon']:.2f}°E ({num(c['pct_aerei_disturbati'], 1)}% of {c['aerei']} aircraft)' for c in gw)}. ")
                   + f"Aircraft data show where interference reaches, not where the jammers are, and say nothing directly about ships ({data_link('baltico-sicurezza.json')})."))
    B.append(("h3", "Shadow fleet in the Danish straits and the Gulf of Finland"))
    sh = next(e for e in V["ev"] if e["categoria"] == "flotta-ombra-transiti" and e["data"].startswith("2025"))
    need(sh["nome"], "292", where="flotta ombra DK")
    B.append(("p", f"The Danish Maritime Authority counted 292 passages of EU-sanctioned tankers through Danish waters in 2025, almost one a day "
                   f"({link('Euronews', sh['link'])}). PortWatch measures only the Øresund, not the Great Belt used by the largest tankers: there, "
                   f"{num(ores['media7']['n_total'])} transits a day in the week to {date_en(ores['ultima_data'])}, {pct(ores['var7_anno_pct']['n_total'])} on a year "
                   f"(tankers {pct(ores['var7_anno_pct']['n_tanker'])}) ({pn_link})."))
    B.append(("p", f"In the AIS snapshot of {date_en(V['navi_date'])} the monitor saw {gof['navi']} ships in the Gulf of Finland: {gof['sanzionate']} on US, "
                   f"UK or EU sanction lists and {gof['flotta_ombra_probabile']} probable shadow fleet. Counting tankers only, {V['gof_tankers_sanc']} of "
                   f"{V['gof_tankers']} were sanctioned there and {V['bal_tankers_sanc']} more in the rest of the Baltic ({data_link('navi.json')}, "
                   f"{data_link('baltico-sicurezza.json')}). The Danish straits snapshot showed {V['dk_ais']['navi']} ships and {V['dk_ais']['sanzionate']} "
                   f"sanctioned, but coverage there is thinner. Ships with AIS off are not counted."))
    det = [e for e in V["ev"] if e["categoria"] in ("fermo-petroliera", "respingimento-petroliera", "fermo-nave") and e["data"] >= "2026"]
    B.append(("p", f"Coastal states have become more active: {data_link('baltico-sicurezza.json')} lists {len(det)} detentions, boardings or refusals of entry "
                   f"in 2026, one of them by Russia. They include Swedish detentions of tankers off Gotland and Trelleborg and Germany's refusal of the tanker Tavian. Russia detained a "
                   f"Greek-owned tanker leaving an Estonian port on 26 July 2026. The Danish straits are rated «{LEVEL.get(V['risk']['stretti-danesi']['livello'])}» on "
                   f"the risk dashboard ({num(V['risk']['stretti-danesi']['punteggio'], 1)} out of 25, from {num(V['risk']['stretti-danesi']['punteggio_7g_fa'], 1)} a week earlier)."))
    cp_ = V["cyber_pl"]
    if cp_:
        B.append(("p", f"Cyber: on 29 December 2025 a destructive attack hit more than 30 wind and solar farms in Poland; the plants lost remote control "
                       f"and communication, but power output did not stop ({data_link('cyber-energia.json')})."))
    pr_ = F.get("port-risk.json")
    if pr_:
        B += port_risk_section(pr_, V)
    else:
        B.append(("p", "**Missing:** a port-by-port risk score (port-risk.json, being prepared by another agent; included automatically when it appears)."))
    B.append(("val", "*Assessment.* The pattern of incidents points to deniable pressure: anchors dragged by merchant ships, unattributed drones, "
                     "jamming that degrades navigation without stopping it. The practical exposure for ports and offshore operators is downtime "
                     "(airport and airspace closures, cable repairs that take months) rather than physical damage to terminals."))

    # ------------------------------------------------------------------ 7 hydrogen
    B.append(("h2", "hydrogen", "7. Hydrogen and new fuels in ports: a reality check"))
    rr = V["h2_real"]
    cap = rr["capacita_reale"][0]
    sp = rr["sintesi_progetti"]["mw_per_stato_nord_europa"]
    B.append(("p", f"Europe had {cap['valore']} MW of electrolysers in operation in July 2025 (Hydrogen Europe, {data_link('idrogeno.json')}), against the "
                   f"90–100 GW the European Commission estimated for its 2030 goal of 10 million tonnes of domestic renewable hydrogen. Among the "
                   f"North-West European port projects tracked by the monitor, {sp.get('operativo', 0)} MW operate, {sp.get('in costruzione', 0)} MW are "
                   f"under construction, {sp.get('sviluppo', 0)} MW are in development and {sp.get('sospeso', 0)} MW are suspended (a sample, not a census)."))
    rows = []
    sten = {"operativo": "operating", "in costruzione": "under construction", "sviluppo": "development", "sospeso": "suspended",
            "cancellato": "cancelled", "annunciato": "announced"}
    cat = {"elettrolizzatore": "electrolyser", "terminale-import": "import terminal", "bunkeraggio": "bunkering", "e-fuel": "e-fuel",
           "idrogeno-blu": "blue hydrogen", "rete-h2-locale": "local H2 grid", "domanda-industriale": "industrial demand"}
    for e in sorted(V["h2_north"], key=lambda e: (list(sten).index(e["stato"]), -(e.get("mw") or 0))):
        rows.append([it2en(e["nome"]), it2en(e.get("porto") or ""), cat.get(e["categoria"], e["categoria"]), sten.get(e["stato"], e["stato"]),
                     num(e["mw"], 0) if e.get("mw") else "—", str(e.get("anno") or "—")])
    B.append(("tab", ["Project", "Port", "Type", "Status", "MW", "Year"], rows, f"Source: {data_link('idrogeno.json')}, one source per project (dates 2022–2026)."))
    g = V["h2_gas"]
    dhb = V["h2_pipes"]["dk-dhb1"]
    drc = V["h2_pipes"]["nl-delta-rhine-corridor"]
    need(dhb["note"], "0,5 GW", "1/12/2026", where="DHB1")
    need(drc["note"], "2031-2032", where="Delta Rhine Corridor")
    need(json.dumps(V["h2_north"], ensure_ascii=False), "42.000 t/anno", "800 m3", where="idrogeno elementi")
    B.append(("p", f"**Costs.** The IEA put hydrogen from offshore wind at 5.3–7 €/kg in 2024. Grey hydrogen made from gas would cost about "
                   f"{num(g['h2_grigio_stima_eur_kg'], 1)} €/kg at today's TTF ({num(g['ttf_ultimo_eur_mwh'], 2)} €/MWh), an interpolation by the monitor that ignores "
                   f"the carbon price. Expensive gas narrows the gap but does not close it."))
    B.append(("p", f"**Pipes.** The Delta Rhine Corridor from Rotterdam to Germany is now expected in {drc['anno'] - 1}–{drc['anno']}, about four years late; until "
                   f"then hydrogen derivatives move by barge. Denmark's first hydrogen pipeline (Esbjerg–German border) is built only if the market books at least "
                   f"0.5 GW by 1 December 2026 ({link('Pipeline Journal', dhb['link'])}). Germany's core network has its first operating stretches (Lubmin–Bobbau, "
                   f"Lingen–Marl)."))
    B.append(("p", f"**Ship fuels.** Rotterdam ran an 800 m³ ship-to-ship ammonia bunkering pilot in April 2025. In the third quarter of 2026 the port sold "
                   f"23,613 m³ of bio-LNG and 4,166 t of bio-methanol, next to 215,420 m³ of fossil LNG ({data_link('bunker-emissioni.json')}). Kassø in Denmark "
                   f"can make up to 42,000 t a year of e-methanol."))
    need(V["ops_rtm"]["carburanti_alternativi"], "23.613", "4.166", "215.420", where="OPS Rotterdam")
    B.append(("val", "*Assessment.* Before 2030 North Sea ports will be local hydrogen producers for refineries and developers of ammonia import "
                     "terminals, not import hubs. The test to watch is commercial: offtake contracts and pipeline bookings, such as the Danish "
                     "1 December deadline, say more than new announcements."))

    # ------------------------------------------------------------------ 8 watch
    B.append(("h2", "watch", "8. What to watch next month"))
    B.append(("p", "Thresholds are the monitor's **assessment** of when a change becomes material for ports and energy companies in the region; "
                   "they are not forecasts. «Now» is the latest value in the data."))
    rk = V["risk"]
    rows = [
        ["TTF front-month", f"{num(ttf['ultimo'], 2)} €/MWh ({date_short(ttf['data'])})", f"above {num(THRESHOLDS['ttf'], 0)} €/MWh", "prezzi.json", "daily"],
        ["German gas storage", f"{num(st['de']['pct'], 1)}% ({date_short(st['de']['date'])})", f"below {num(THRESHOLDS['storage_de'], 0)}% on 1 Dec", "scorte.json", "daily"],
        ["Dutch gas storage", f"{num(st['nl']['pct'], 1)}%", f"below {num(THRESHOLDS['storage_nl'], 0)}% on 1 Dec", "scorte.json", "daily"],
        ["EUA auction price", f"{num(eua['prezzo_eur'], 2)} €/t ({date_short(eua['data'])})", f"above {num(THRESHOLDS['eua'], 0)} €/t", "bunker-emissioni.json", "daily"],
        ["Rotterdam calls, 30 days y/y", pct(rtm["var30"]), f"below {pct(THRESHOLDS['rotterdam_30d'], 0)}", "porti-nord.json", "weekly"],
        ["Øresund transits, 7 days y/y", pct(ores["var7_anno_pct"]["n_total"]), f"below {pct(THRESHOLDS['oresund_7d'], 0)} (dashboard red)", "porti-nord.json", "weekly"],
        ["Sanctioned ships in the Gulf of Finland (AIS snapshot)", f"{gof['sanzionate']}", f"above {THRESHOLDS['gof_sanctioned']}", "baltico-sicurezza.json", "daily"],
        ["High GPS-interference cells west of 17°E (week)", f"{len(V['gnss_west'])}", f"{THRESHOLDS['gnss_west']} or more, or any west of 15°E (Bornholm, Øresund, German ports)", "baltico-sicurezza.json", "daily"],
        ["New Baltic cable or pipeline incident", f"last: {date_short(V['last_cable'])}", "any", "cavi-incidenti.json", "on event"],
        ["IJmuiden Ver Gamma bids", "window 26 Nov–10 Dec", "no bids or Gamma-B withdrawn", "eolico-filiera.json", "10 Dec"],
        ["Danish hydrogen backbone bookings", "deadline 1 Dec", "under 0.5 GW booked (project not built)", "idrogeno.json", "1 Dec"],
        ["Maersk ETS surcharge Q1 2027, Far East → N. Europe", f"{THRESHOLDS['maersk_ets']} $/FEU (Q4)", f"above {THRESHOLDS['maersk_ets']} $/FEU", "bunker-emissioni.json", "about 1 Dec"],
        ["Red Sea war-risk quote", f"{num(V['war_last']['mar-rosso']['min'], 1)}–{num(V['war_last']['mar-rosso']['max'], 1)}% ({date_short(V['war_last']['mar-rosso']['data'])})",
         f"above {num(THRESHOLDS['redsea_war'], 1)}% of hull value", "assicurazioni.json", "on quote"],
    ]
    if wc:
        E = {e["id"]: e for e in wc.get("elementi", [])}
        for i in wc.get("riepilogo", {}).get("next_90_days", {}).get("items") or []:
            e = E.get(i["id"])
            if e and e["country"] in ("GB", "DE") and e["type"] in ("auction", "policy") and e["date"] <= "2026-12-31":
                rows.append([e["project"], e["status_effective"] + f" ({e['date']})",
                             "no adoption in December" if e["country"] == "DE" else "results slip into 2027", "wind-calendar.json", "on event"])
    B.append(("tab", ["Indicator", "Now", "Threshold (assessment)", "File", "Frequency"], rows,
              f"Also on the calendar: the IMO vote on the global Net-Zero Framework, planned to resume on 4 December 2026 ({data_link('bunker-emissioni.json')}). "
              f"Risk dashboard levels for reference: Danish straits «{LEVEL[rk['stretti-danesi']['livello']]}», Baltic cables «{LEVEL[rk['baltico']['livello']]}», "
              f"Red Sea container route «{LEVEL[rk['mar-rosso-container']['livello']]}», Qatar LNG «{LEVEL[rk['gnl-qatar']['livello']]}» ({data_link('rischio.json')})."))

    # ------------------------------------------------------------------ 9 method
    B.append(("h2", "method", "9. Method, sources and limits"))
    rows = []
    for n in ["porti-nord.json", "scorte.json", "prezzi.json", "eolico-filiera.json", "offshore-nord.json", "bunker-emissioni.json",
              "assicurazioni.json", "noli.json", "portwatch.json", "baltico-sicurezza.json", "navi.json", "cavi-incidenti.json",
              "idrogeno.json", "esposizione-nord.json", "rete-elettrica.json", "rischio.json"]:
        fs = [(f.get("nome") or f.get("name") or f.get("fonte") or "") if isinstance(f, dict) else str(f) for f in (F[n].get("fonti") or [])[:2]]
        rows.append([data_link(n), F[n].get("aggiornato", ""), "; ".join(x.split(" (")[0][:70] for x in fs if x) or "Yahoo Finance, US Treasury"])
    for n, what in OPTIONAL.items():
        rows.append([data_link(n) if F[n] else n, (F[n].get("aggiornato") or F[n].get("updated") or "present") if F[n] else "not available at build time", what])
    if V["eurostat"]:
        rows.append(["report/dati/eurostat-gas-nord.json", V["eurostat"]["read"], "Eurostat nrg_stk_gasm (DK, PL)"])
    B.append(("tab", ["File", "Updated", "Main sources"], rows, "Each file lists its sources, licences and the date of each datum; the text cites the date of the datum, not of the reading."))
    B.append(("ul", [
        "**Coverage.** PortWatch counts ships with AIS on; it sees about ten days late and undercounts Russian ports. Port tonnages are curated by hand from port authorities, some via trade press.",
        "**Seven days is too short.** Weekly port-call changes swing by ±10–30% on small numbers; the report leads with 30-day and year-to-date averages.",
        "**Conflicting counts.** baltico-sicurezza.json counts all sanctioned ships in the Gulf of Finland (44 of 109); navi.json counts tankers (38 of 96 sanctioned) and the risk dashboard counts sanctioned tankers in the whole Baltic (45). They are different perimeters of the same snapshot.",
        "**Offshore wind** totals differ between WindEurope (national, end-2025) and EMODnet (map polygons, status sometimes late, duplicates removed).",
        "**Brent** in prezzi.json gives 92.57 $/bbl as the 9 November close (an earlier run recorded 91.70, a price from the next session's overnight trading); bunker-emissioni.json and rischio.json still quote 92.62, an intraday reading of 9 November. This report does not use Brent.",
        "**Missing:** AGSI+ daily fill for Denmark and Poland; monthly LNG import volumes by country and origin; any public war-risk premium for Baltic calls"
        + "".join(f"; {n} at build time" for n in OPTIONAL if not F[n]) + ".",
        "**Hand-written items:** the external fact on the EU-wide US LNG share and the thresholds of section 8. Figures quoted from curated text fields "
        "of the files (for example the 292 tanker passages or the Fitburg sentence) are typed in the script and checked against the source text at every "
        "run; all other numbers are computed by report/build_northern_europe.py from the files above.",
        "**Different assumptions between files.** The cost stack uses a 221.7 million $ hull (assicurazioni.json); transit-times.json uses 150 million $ "
        "for the same ship type, so its Red Sea premium is lower. Port-risk.json computes its own 7-day port-call changes, which can differ by a few tenths from porti-nord.json.",
    ]))
    B.append(("p", "**Glossary.** AIS: transponder by which ships broadcast identity and position. TEU/FEU: 20-/40-foot container. TTF: Dutch gas hub price. "
                   "LNG: liquefied natural gas. HVDC: high-voltage direct current. CfD: contract for difference. EUA: EU emission allowance (1 t CO₂e). "
                   "FuelEU Maritime: EU rule on the greenhouse intensity of ship fuel. War risk: separate insurance for war, mines and seizure. "
                   "Shadow fleet: old tankers with opaque ownership used to move sanctioned oil. GNSS: satellite navigation (GPS, Galileo)."))
    B.append(("review",))
    return B


def wind_calendar_section(wc):
    """wind-calendar.json (WIND-CALENDAR agent): milestones in the next 90 days and items at risk."""
    E = {e["id"]: e for e in wc.get("elementi", [])}
    nxt = [E[i["id"]] for i in (wc.get("riepilogo", {}).get("next_90_days", {}).get("items") or []) if i["id"] in E]
    risk = [e for e in E.values() if e.get("status_effective") in ("at risk", "unconfirmed") and e not in nxt and e.get("country") != "FR"]
    rows = [[e["date"], PAESE.get(e["country"], e["country"]), e["type"], e["project"], num(e["capacity_mw"], 0) if e.get("capacity_mw") else "—",
             e["status_effective"], link(e["source"], e.get("link"))] for e in nxt]
    rs = wc.get("riepilogo", {}).get("by_status_effective", {})
    out = [("h3", "Offshore wind calendar: the next 90 days"),
           ("tab", ["Date", "Country", "Type", "Milestone", "MW", "Status", "Source"], rows,
            f"Source: {data_link('wind-calendar.json')} (curated, {wc['riepilogo']['items']} milestones, reference date {date_en(wc['riferimento'])}; "
            f"«unconfirmed» = a scheduled date has passed without confirmation). Across the calendar: {rs.get('done', 0)} done, {rs.get('scheduled', 0)} scheduled, "
            f"{rs.get('at risk', 0)} at risk, {rs.get('unconfirmed', 0)} unconfirmed.")]
    if risk:
        out.append(("p", "**Also flagged at risk or unconfirmed in the calendar:**"))
        out.append(("ul", [f"{e['project']} ({PAESE.get(e['country'], e['country'])}, {e['date']}): {re.split(r'(?<=[a-z0-9)])[.] ', e['summary'])[0].rstrip('.')}."
                           for e in sorted(risk, key=lambda e: e["date"])[:5]]))
    return out


def transit_section(tt):
    """transit-times.json (TRANSIT agent): sea days to Rotterdam today, base and via the Cape."""
    R = [r for r in tt.get("routes", []) if r.get("to") == "rotterdam"]
    if not R:
        warn("transit-times.json: no route to Rotterdam")
        return []
    st = {"normal": "normal", }
    rows = []
    for r in R:
        cape = r.get("cape") or {}
        lo, hi = (r.get("days_today_range") or [None, None])[:2]
        rows.append([r["from_name"], r["cargo"], r["status"], num(r["nm_today"], 0), f"{num(r['days_today'])} ({num(lo)}–{num(hi)})",
                     num(r["days_base"]), num(cape.get("days")) if cape else "—",
                     f"{num(cape.get('extra_days_vs_base'))}" if cape else "—"])
    sh = next((r for r in R if r["from"] == "shanghai"), R[0])
    v = (tt.get("method") or {}).get("vessels", {}).get("container", {})
    out = [("p", f"The monitor's routing model (transit-times.json, updated {date_en(tt['updated'][:10])}) puts a ~15,000 TEU container ship from "
                 f"{sh['from_name']} to Rotterdam at {num(sh['days_today'])} days at sea via Suez today ({num(sh['nm_today'], 0)} nautical miles at "
                 f"{num(v.get('speed_kn'), 0)} knots), and {num(sh['cape']['days'])} days via the Cape, {num(sh['cape']['extra_days_vs_base'])} days more. "
                 f"Sea time only: no canal waiting, port time or bunkering stops; distances are within 5% of published ones. The model's extra days via the Cape "
                 f"are fewer than UNCTAD's 14–24 because they are sea days at one fixed speed from one origin; UNCTAD's range covers several origins and speeds."),
           ("tab", ["Origin", "Cargo", "Status today", "Nautical miles today", "Days today (speed range)", "Days, pre-crisis route", "Days via Cape", "Extra days via Cape"],
            rows, f"Source: {data_link('transit-times.json')} (Benden shipping lanes, Dijkstra routing; speeds from Alphaliner/UNCTAD; "
                  "statuses from stretti-dettaglio.json). «Blocked»/«re-routed» refer to the Strait of Hormuz being de facto closed.")]
    return out


def port_risk_section(pr, V):
    """port-risk.json (PORT-RISK agent): probability x impact score for the ten largest ports."""
    P = {x.get("source_id") or x["id"]: x for x in pr.get("ports", [])}
    rows = []
    for p in V["top10"]:
        x = P.get(p["id"])
        if not x:
            continue
        rows.append([p["name"], num(x["score"], 1), x["level"], f"{num(x['probability'], 1)} × {num(x['impact'], 1)}", x["trend"]])
    if not rows:
        warn("port-risk.json: none of the ten ports found")
        return []
    lv = pr.get("rules", {}).get("levels", {})
    return [("h3", "Port risk scores"),
            ("p", f"The monitor's Port Risk Index scores each port as probability of disruption (1–5) times impact on European supply chains (1–5). "
                  f"Levels: low {lv.get('low', '')}, medium {lv.get('medium', '')}, high {lv.get('high', '')}. Russian ports have impact capped at 3. "
                  f"It is a rule-based assessment, not a forecast."),
            ("tab", ["Port", "Score /25", "Level", "Probability × impact", "Trend"], rows,
             f"Source: {data_link('port-risk.json')}, reference date {date_en(pr.get('reference_date', pr.get('updated', '')[:10]))}; method in {pr.get('method', '')}.")]


def optional_section(js, name, title):
    """Generic renderer for files produced by other agents, whose schema is not fixed yet."""
    B = [("h3", title)]
    items = js.get("elementi") or js.get("items") or js.get("ports") or js.get("rotte") or js.get("routes") or js.get("eventi") or []
    if isinstance(items, dict):
        items = list(items.values())
    note = js.get("nota") or js.get("note") or ""
    if note:
        B.append(("p", f"{data_link(name)}: {note[:400]}"))
    if not items:
        warn(f"{name}: no list of items found; rendered note only")
        return B
    namek = next((k for k in ["nome", "porto", "name", "rotta", "route", "titolo", "progetto", "evento"] if k in items[0]), None)
    numk = [k for k, v in items[0].items() if isinstance(v, (int, float)) and k not in ("lat", "lon", "precisione_km")][:4]
    datek = next((k for k in ["data", "date", "data_fonte", "quando"] if k in items[0]), None)
    head = [namek or "item"] + numk + ([datek] if datek else []) + ["source"]
    rows = []
    for it in items[:15]:
        rows.append([str(it.get(namek, ""))] + [num(it.get(k), 1) if isinstance(it.get(k), (int, float)) else "" for k in numk]
                    + ([str(it.get(datek, ""))] if datek else []) + [link(it.get("fonte") or it.get("source") or "", it.get("link"))])
    B.append(("tab", head, rows, f"First {len(rows)} items of {data_link(name)} (fields as named in the file; read automatically, check before quoting)."))
    warn(f"{name} rendered with the generic adapter: review its fields before publishing")
    return B


# =====================================================================================
# Rendering
# =====================================================================================
def inline_md(t, data_prefix):
    return t.replace("](DATA/", f"]({data_prefix}")


def inline_html(t, data_prefix):
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2).replace("DATA/", data_prefix)}">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def review_parts():
    R = REVIEW
    parts = [("p", f"Independent check of every number against the data files or the cited source, done before publication with a second pass "
                   f"by an AI assistant (Claude) acting as reviewer under report/STANDARD.md. Full log: {R['log']}."),
             ("p", f"**Claims checked.** {R['checked']}")]
    if R["corrections"]:
        parts += [("p", "**Corrections.**"), ("ul", R["corrections"])]
    if R["unverifiable"]:
        parts += [("p", "**Still unverifiable.**"), ("ul", R["unverifiable"])]
    return parts


def render_md(B, meta, figs):
    P = "../docs/data/"
    o = [f"# {meta['title']}", "", f"*{meta['subtitle']}*", "",
         f"Gabriele Giuliani · Geo-economic Risk Monitor · Issue no. 1 · {meta['edition']} · data read on {meta['read']}", "",
         "Every number has a source and a date. Paragraphs marked *Assessment* are the monitor's reasoning, not facts.", "",
         "**Contents:** " + " · ".join(f"[{re.sub(r'^\d+\. ', '', b[2])}](#{b[1]})" for b in B if b[0] == "h2"), ""]
    for b in B:
        k = b[0]
        if k == "h2":
            o += [f'<a id="{b[1]}"></a>', "", f"## {b[2]}", ""]
        elif k == "h3":
            o += [f"### {b[1]}", ""]
        elif k == "p":
            o += [inline_md(b[1], P), ""]
        elif k == "val":
            o += [inline_md(b[1], P), ""]
        elif k == "ul":
            o += [f"- {inline_md(x, P)}" for x in b[1]] + [""]
        elif k == "tab":
            o += ["| " + " | ".join(b[1]) + " |", "|" + "---|" * len(b[1])]
            o += ["| " + " | ".join(inline_md(str(c), P).replace("|", "/") for c in r) + " |" for r in b[2]]
            o += ["", f"*{inline_md(b[3], P)}*" if b[3] else "", ""]
        elif k == "fig":
            o += [f"![{re.sub(r'[*]', '', b[2])[:120]}]({figs[b[1]]})", "", inline_md(b[2], P), ""]
        elif k == "review":
            o += ['<a id="review"></a>', "", "---", "", f"### Review · {date_en(REVIEW['date'])}", ""]
            for kk, x in review_parts():
                o += ([inline_md(x, P), ""] if kk == "p" else [f"- {inline_md(y, P)}" for y in x] + [""])
    o += ["---", "", "Gabriele Giuliani · Geo-economic Risk Monitor · " + meta["edition"], "", meta["ai_note"], ""]
    return "\n".join(o)


CSS = """
:root{--paper:#F6F5F0;--card:#FFFFFF;--ink:#1D272D;--soft:#4f5d66;--rule:#DCDFDD;--accent:#A61E6B;--band:#ECE9E0;color-scheme:light dark}
@media (prefers-color-scheme:dark){:root{--paper:#10181D;--card:#172127;--ink:#DAE0E2;--soft:#A0ABB1;--rule:#2B373E;--accent:#e06aab;--band:#1A252C}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 "IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
.page{max-width:70ch;margin:0 auto;padding:24px 16px 64px}
a{color:var(--accent);text-underline-offset:2px}
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
@media (max-width:600px){.wide{display:none}.narrow{display:block}td{min-width:6em}td:first-child{min-width:8em}}
details{margin-top:6px;font-size:13px}
summary{cursor:pointer;color:var(--soft)}
.review{margin:40px 0 0;padding:16px 18px;background:var(--card);border:1px solid var(--rule);border-left:3px solid var(--soft);border-radius:0 8px 8px 0;font-size:15px}
.review h2{font:600 13px/1.4 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--soft);margin:0 0 10px;padding:0}
.review p,.review ul{margin:0 0 10px}
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
         f'<p class="kicker">Monthly report · Issue no. 1 · {esc(meta["edition"])}</p>',
         f"<h1>{esc(meta['title'])}</h1>", f'<p class="sub">{esc(meta["subtitle"])}</p>',
         f'<p class="meta">Gabriele Giuliani · Geo-economic Risk Monitor · data read on {esc(meta["read"])}. Every number has a source and a date; '
         f'boxes marked <em>Assessment</em> are the monitor\'s reasoning, not facts.</p>',
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
            txt = re.sub(r"^\*Assessment\.\*\s*", "", b[1])
            o.append(f'<aside class="assess"><span class="tag">Assessment</span>{inline_html(txt, P)}</aside>')
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
            parts = []
            for kk, x in review_parts():
                parts.append(f"<p>{inline_html(x, P)}</p>" if kk == "p" else "<ul>" + "".join(f"<li>{inline_html(y, P)}</li>" for y in x) + "</ul>")
            o.append(f'<aside class="review" id="review"><h2>Review · {esc(date_en(REVIEW["date"]))}</h2>' + "".join(parts) + "</aside>")
    o.append(f'<footer><p class="sig">Gabriele Giuliani · Geo-economic Risk Monitor</p><p>{esc(meta["edition"])}. {inline_html(meta["ai_note"], P)}</p>'
             '<p><a href="../../index.html">← Back to the map</a></p></footer>')
    o += ["</main>", "</body>", "</html>"]
    return "\n".join(o)


WIND_NAMES = {"GB": "United Kingdom", "DE": "Germany", "NL": "Netherlands", "DK": "Denmark", "BE": "Belgium", "PL": "Poland", "FR": "France", "NO": "Norway"}


def chart_tables(V):
    T = V["top10"]
    st = V["storage"]
    a, b, ins = V["ex_asia"], V["ex_intra"], V["ins"]
    return {
        "ports": table_html(["Port", "30 days y/y", "Year to date y/y"], [[p["name"], pct(p["var30"]), pct(p["ytd"])] for p in T]),
        "storage": table_html(["Country", "Latest", "Same day last year", "5-year average"],
                              [[n, f"{num(st[c]['pct'], 2)}%", f"{num(st[c]['last_year'], 2)}%", f"{num(st[c]['avg5'], 2)}%"] for c, n in [("de", "Germany"), ("nl", "Netherlands")]]),
        "wind": table_html(["Country", "Installed end-2025, GW", "Forecast 2030, GW", "Target, GW (2030 unless stated)"],
                           [[WIND_NAMES.get(c["paese"], c["nome"]), num(c["installato_fine2025_mw"] / 1000, 2), num(c["previsione_2030_mw"] / 1000, 2),
                             (num(c["obiettivo_2030_gw"], 1) + (f" (end-{c['anno_obiettivo']})" if c.get("anno_obiettivo") else "")) if c["obiettivo_2030_gw"] else "—"]
                            for c in V["wind_countries"]]),
        "costs": table_html(["Item", "Asia → Rotterdam, € m", "Rotterdam → Genoa, € m"],
                            [["Fuel", num(a["costo_carburante_eur"] / 1e6, 3), num(b["costo_carburante_eur"] / 1e6, 3)],
                             ["EU ETS", num(a["costo_ets_eur"] / 1e6, 3), num(b["costo_ets_eur"] / 1e6, 3)],
                             ["FuelEU (max)", num(a["costo_fueleu_max_eur"] / 1e6, 3), num(b["costo_fueleu_max_eur"] / 1e6, 3)],
                             ["War risk, Red Sea (mid; range)", f"{num(ins['mid_eur'] / 1e6, 3)} ({num(ins['lo_eur'] / 1e6, 2)}–{num(ins['hi_eur'] / 1e6, 2)})", "—"]]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", help="edition YYYY-MM (default: current month)")
    ap.add_argument("--offline", action="store_true", help="do not call Eurostat; use the cache")
    args = ap.parse_args()
    today = dt.date.today()
    month = args.month or today.strftime("%Y-%m")
    y, m = map(int, month.split("-"))
    V = compute(today, args.offline)
    B = blocks(V, month)
    edition = f"{MONTHS[m - 1]} {y}"
    meta = {"title": "Northern Europe: Ports and Energy",
            "short": "Northern Europe: Ports and Energy",
            "subtitle": f"Port traffic, gas, offshore wind, shipping costs and Baltic security in the North Sea and Baltic, {edition}.",
            "edition": edition, "read": date_en(today.isoformat()),
            "ai_note": ("Note on AI use: this report was prepared with an AI assistant (Claude, Anthropic), which wrote the build script, "
                        "the calculations and the draft text from the monitor's data files and the sources cited, and then reviewed it against "
                        "report/STANDARD.md. Numbers come from the data files and linked sources; assessments are marked. Gabriele Giuliani is "
                        "responsible for publication.")}
    os.makedirs(OUT_SVG, exist_ok=True)
    os.makedirs(OUT_HTML, exist_ok=True)
    svg, figs = {}, {}
    tabs = chart_tables(V)
    for key, fn in [("ports", chart_ports), ("storage", chart_storage), ("wind", chart_wind), ("costs", chart_costs)]:
        svg[key] = {"wide": fn(V, True), "narrow": fn(V, False), "table": tabs[key]}
        name = f"ne-{month}-{key}.svg"
        with open(os.path.join(OUT_SVG, name), "w", encoding="utf-8") as f:
            f.write(svg[key]["wide"])
        figs[key] = f"grafici/{name}"
    md = render_md(B, meta, figs)
    with open(os.path.join(ROOT, "report", f"northern-europe-{month}.md"), "w", encoding="utf-8") as f:
        f.write(md)
    with open(os.path.join(OUT_HTML, f"northern-europe-{month}.html"), "w", encoding="utf-8") as f:
        f.write(render_html(B, meta, svg))
    print(f"written: report/northern-europe-{month}.md, docs/report/en/northern-europe-{month}.html, {len(svg)} charts; {len(WARN)} warnings")


if __name__ == "__main__":
    main()
