#!/usr/bin/env python3
"""Build the report "Italy and the Gulf Shock: Fuel, Freight, Prices and the Risk of a Truck Strike".

Standard library only. From the repository root:

    python3 report/build_italy.py                  # edition for the current month
    python3 report/build_italy.py --month 2026-11  # a given edition

What it does every time it runs:
1. reads docs/data/*.json: italia-impatti (fuel prices MASE, excise, PUN/GME, ARERA, Istat NIC,
   HICP weights, consumer confidence, fuel sales, haulage rules and precedents, transmission rules,
   scenarios), gas-italia, scorte, paesi, commercio, portwatch, port-risk, transit-times,
   rischio, prezzi, noli, calendario, notizie-testate;
2. recomputes every number used in the text and draws ten inline SVG charts (wide and narrow);
3. writes report/italy-gulf-shock-YYYY-MM.md, docs/report/en/italy-gulf-shock-YYYY-MM.html
   and the wide SVGs in report/grafici/it-YYYY-MM-*.svg.

Rules (report/STANDARD.md): no number from the data is typed by hand in the text or the charts.
Hand-written items are:
- EXTERNAL: facts the JSON files do not hold, each with source, link, date and reliability;
- the translation of curated Italian labels (names, not numbers);
- linking prose and assessments, marked "Assessment".
Curated figures quoted from text fields of the JSON files are guarded by `need()`: if the figure
disappears from the source text at the next run, the script warns so the sentence is re-read.
"""

import argparse
import datetime as dt
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "data")
OUT_SVG = os.path.join(ROOT, "report", "grafici")
OUT_HTML = os.path.join(ROOT, "docs", "report", "en")
SLUG = "italy-gulf-shock"

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
    "qatar_fm": {
        "date": "2026-10-31",
        "text": "QatarEnergy has been in force majeure since 4 March 2026; for the cargoes due to Edison (the Adriatic LNG terminal) it was extended to the end of December",
        "source": "gasworld (end of October 2026), as cited in the monitor's Hormuz report (report/hormuz-mar-rosso-2026-11.md)",
        "link": "https://www.gasworld.com/story/qatarenergy-extends-lng-force-majeure-on-edison-cargoes-to-end-december/2262726.article/",
        "reliability": "medium (trade press)",
    },
    "qatar_trains": {
        "date": "2026-10-12",
        "text": "Iranian missile attacks knocked out about 17% of Qatar's export capacity; Qatar's LNG exports were 1.6 million tonnes in September, under a quarter of the pre-war average, and on track for 0.6 million in October (Kpler)",
        "source": "Reuters column republished by Cyprus Mail, 12 October 2026 (re-read 10 November 2026). The column gives 17% of capacity, not the trains: "
                  "trains 4 and 6, about 12.8 Mt a year, come from Global LNG Hub as cited in report/hormuz-mar-rosso-2026-11.md",
        "link": "https://cyprus-mail.com/2026/10/12/qatar-lng-exports-remain-severely-disrupted-despite-recovery-in-gulf-oil-shipments",
        "reliability": "medium (Reuters opinion column quoting Kpler)",
    },
    "iea_storage": {
        "date": "2026-11-03",
        "text": "EU storage enters the winter at its lowest level since 2013",
        "source": "IEA, Global Gas Security Review 2026 (3 November 2026), via the SCORTE agent (report/agenti/scorte.md)",
        "link": "https://www.iea.org/reports/global-gas-security-review-2026/executive-summary",
        "reliability": "high (primary); iea.org not reachable from this environment, sentence confirmed by search on 10 November 2026 (IEA press release, WAM)",
    },
    "mimit_9nov": {
        "date": "2026-11-09",
        "text": "the Mimit self-service average on ordinary roads was €2.232 for diesel on 9 November, against €2.224 on 7 November, the last day of the cut; petrol was €2.000",
        "self_7nov": 2.224, "self_9nov": 2.232,
        "source": "ANSA, 9 November 2026 (9 Nov figures, self-service, ordinary road network; motorways: diesel 2.287); Rai News, 8 November 2026 (7 Nov figure). "
                  "ANSA quotes the ministry: thanks to the price cap joined by the main companies, self-service diesel stays below €2.20 on most of the network",
        "link": "https://www.ansa.it/sito/notizie/economia/2026/11/09/mimit-prezzo-benzina-stabile-a-2000-euro-gasolio-in-leggero-aumento-a-2232_9d0752c9-8a30-4d1f-9149-b033ff112a55.html",
        "reliability": "high (agency quoting the ministry)",
    },
}

EXTERNAL.update({
    "brent_close_9nov": {
        "date": "2026-11-09",
        "value": 92.57,
        "text": "Brent's final close for the 9 November session was 92.57 dollars (Yahoo Finance daily bar, read 10 November 2026 at 06:49 UTC)",
        "source": "Yahoo Finance BZ=F, daily and hourly chart data, read by the reviewer on 10 November 2026. prezzi.json (read 03:40 UTC on 10 November) "
                  "records 91.70 under 9 November: the hourly bars show that 91.70 is a price from the overnight trading of the 10 November session "
                  "(91.73 at 02:00 and 91.57 at 03:00 UTC), not the 9 November close. 92.62, used by the risk dashboard and the Hormuz report, is the "
                  "intraday reading of 19:47 UTC on 9 November.",
        "link": "https://finance.yahoo.com/quote/BZ%3DF",
        "reliability": "medium (futures quote, not an official settlement price)",
    },
    "excise_refund": {
        "date": "2026-11-10",
        "rate": 0.40322,
        "text": "the refund covers the excise above a fixed reference rate of €403.22 per 1,000 litres (art. 24-ter of the excise code; trucks of 7.5 tonnes or more, Euro V or cleaner)",
        "source": "Legislative decree 504/1995, art. 24-ter and Table A point 4-bis, as summarised by Assolombarda and customs agency (ADM) circulars; Federtrasporti (Teleborsa, 10 September 2026) quotes 26.5 cents",
        "link": "https://www.assolombarda.it/servizi/fisco/informazioni/credito-d2019imposta-per-gli-autotrasportatori-rimborso-accise-dal-1deg-al-31-dicembre-2022",
        "reliability": "high (law); page not opened, confirmed by search",
    },
    "bill_decree": {
        "date": "2026-11-09",
        "text": "a cap of €58.9/MWh on the gas used to generate electricity, from January 2027 for 18 months, which the energy minister says will cut the wholesale power price by about 15 €/MWh on average",
        "source": "ANSA and Corriere della Sera, 9 November 2026 (Corriere gives 59 €/MWh)",
        "link": "https://www.ansa.it/sito/notizie/economia/2026/11/09/dal-cdm-ok-al-decreto-bollette-15-euro-in-meno-al-megawattora_cbf74d76-2c12-4718-89af-73ab9c1e6fec.html",
        "reliability": "high (agency)",
    },
    # MASE weekly national average diesel price (€/l) for weeks before January 2022, which italia-impatti.json does not keep.
    # Read by the reviewer from the MASE weekly CSV (sisen.mase.gov.it, GASOLIO_AUTO, €/1000 l) on 10 November 2026.
    "mase_diesel_pre2022": {
        "link": "https://sisen.mase.gov.it/dgsaie/prezzi-settimanali-carburanti",
        "values": {"2006-12-11": 1.11387, "2007-12-10": 1.29003, "2011-01-17": 1.34035, "2011-01-24": 1.34945,
                   "2012-01-16": 1.68151, "2012-01-23": 1.68700, "2021-03-15": 1.43607},
    },
})

# Review box, filled in by the independent review (report/revisioni/<slug>.md).
REVIEW = {
    "status": "done",
    "date": "10 November 2026",
    "log": "report/revisioni/italy-gulf-shock-2026-11.md",
    "claims": 214,
    "ok": 168,
    "corrected": 33,
    "unverified": 13,
}

PORT_EN = {"Genova": "Genoa", "Venezia (Lido)": "Venice (Lido)", "Venezia (Malamocco)": "Venice (Malamocco)"}
LEVEL = {"basso": "low", "medio": "medium", "alto": "high", "critico": "critical"}


# =====================================================================================
# Helpers
# =====================================================================================
def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


def d(s):
    return dt.date.fromisoformat(s[:10]) if len(s) >= 10 else dt.date.fromisoformat(s[:7] + "-01")


def num(v, dec=1):
    if v is None:
        return "n/a"
    s = f"{v:,.{dec}f}"
    return s.replace("-", "−")


def pct(v, dec=1, sign=True):
    if v is None:
        return "n/a"
    s = f"{v:+,.{dec}f}%" if sign else f"{v:,.{dec}f}%"
    return s.replace("-", "−")


def pts(v, dec=1):
    return (f"{v:+.{dec}f}").replace("-", "−")


def eur(v, dec=3):
    return f"€{num(v, dec)}"


def date_en(s, year=True):
    x = d(s)
    return f"{x.day} {MONTHS[x.month - 1]}" + (f" {x.year}" if year else "")


def month_en(s, year=True):
    x = d(s)
    return MONTHS[x.month - 1] + (f" {x.year}" if year else "")


def esc(s):
    return html.escape(str(s), quote=True)


def link(text, url):
    return f"[{text}]({url})"


def dl(name):
    return f"[`{name}`](DATA/{name})"


def need(text, *tokens, where=""):
    for t in tokens:
        if t not in (text or ""):
            warn(f"curated figure '{t}' no longer found in {where}: re-read the sentence")


def var(a, b):
    return (a / b - 1) * 100 if b else None


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def at(series, date):
    for k, v in series:
        if k == date:
            return v
    return None


def before(series, date):
    """Value at the latest key <= date."""
    best = None
    for k, v in series:
        if k <= date:
            best = (k, v)
    return best


def week_back(series, date, weeks):
    target = (d(date) - dt.timedelta(weeks=weeks)).isoformat()
    return before(series, target)


# =====================================================================================
# Computation
# =====================================================================================
def compute(today):
    V = {}
    ii = load("italia-impatti.json")
    V["ii"] = ii
    S = ii["serie"]
    o = ii["oggi"]
    cs = S["carburanti_settimanali"]
    dsl, ptr = cs["gasolio"], cs["benzina"]
    V["dsl"], V["ptr"] = dsl, ptr
    V["dsl_net"], V["dsl_exc"] = cs["gasolio_netto"], cs["gasolio_accisa"]
    g, b = o["gasolio_settimanale"], o["benzina_settimanale"]
    V["g"], V["b"] = g, b
    last = g["data"]
    V["last_fuel"] = last
    # post-expiry estimate recomputed: net unchanged + ordinary excise, with 22% VAT
    ordinary = ii["accise"]["ordinaria_gasolio_eur_l"]
    est = round((g["netto"] + ordinary) * 1.22, 3)
    if abs(est - g["stima_dopo_fine_taglio_accise"]) > 0.002:
        warn(f"post-expiry diesel estimate {est} differs from file {g['stima_dopo_fine_taglio_accise']}")
    V["dsl_post"] = g["stima_dopo_fine_taglio_accise"]
    V["cut_cents_vat"] = round((ordinary - g["accisa"]) * 1.22 * 100, 1)
    V["ordinary"] = ordinary
    base = ii["regole_trasmissione"]["per_il_simulatore"]["base_condizioni_normali"]
    today_b = ii["regole_trasmissione"]["per_il_simulatore"]["base_oggi"]
    V["base_n"], V["base_t"] = base, today_b
    V["pre"] = base["data_carburanti"]
    pre_d, pre_p = at(dsl, V["pre"]), at(ptr, V["pre"])
    V["pre_d"], V["pre_p"] = pre_d, pre_p
    pre_net = at(cs["gasolio_netto"], V["pre"])
    V["pre_net"] = pre_net
    V["net_var"] = var(g["netto"], pre_net)
    V["brent_eur_var"] = var(today_b["brent"] / today_b["eurusd"], base["brent"] / base["eurusd"])
    V["brent_usd_var"] = var(today_b["brent"], base["brent"])
    mx = max(dsl, key=lambda x: x[1])
    V["dsl_max"] = mx
    V["dsl_first"] = dsl[0][0]
    yago = before(dsl, (d(last) - dt.timedelta(days=364)).isoformat())
    V["dsl_yago"] = yago
    V["dsl_yoy"] = var(g["eur_l"], yago[1])
    w8 = week_back(dsl, last, 8)
    V["dsl_8w"] = w8
    V["dsl_8w_var"] = var(g["eur_l"], w8[1])
    V["gap_now"] = (g["eur_l"] - b["eur_l"]) * 100
    V["gap_pre"] = (pre_d - pre_p) * 100
    V["exc_aligned"] = [c for c in ii["accise"]["cambi"] if c["data_rilevazione"] == "2026-01-05"]
    # first week >= 2.10 in the run-up to the current level (since July 2026)
    hi = ii["soglie_fermo"]["soglie_eur_l"][1]
    lo = ii["soglie_fermo"]["soglie_eur_l"][0]
    V["thr"] = (lo, hi)
    V["thr_pct"] = ii["soglie_fermo"]["soglie_aumento_pct"]
    below = [k for k, v in dsl if v < hi]
    after = [k for k, v in dsl if v >= hi and (not below or k > below[-1])]
    V["above_since"] = after[0] if after else None
    # pass-through rules
    R = {r["id"]: r for r in ii["regole_trasmissione"]["regole"]}
    V["R"] = R
    V["est"] = ii["regole_trasmissione"]["stimate"]
    # electricity and gas
    gme = S["gme"]
    V["pun_m"] = gme["mensile"]
    V["pun_y"] = dict(gme["annuale"])
    V["pun_oct"] = o["pun_ultimo_mese_completo"]
    V["pun_nov"] = o["pun_mese_in_corso_parziale"]
    V["pun_day"] = o["pun_ultimo_giorno"]
    V["mgp_day"] = o["gas_mgp_ultimo_giorno"]
    V["pun_days_nov"] = len([x for x in gme["giornaliero"] if x[0].startswith(V["pun_nov"][0])])
    V["arera"] = o["arera_cmem_ultimo"]
    V["cmem"] = S["arera_cmem"]
    pt = R["ttf_pun"]["coeff"]
    V["pun_ttf"] = pt
    oct_ttf = [p for p in pt["punti"] if p[0] == V["pun_oct"][0]]
    V["oct_ttf"] = oct_ttf[0][2] if oct_ttf else None
    V["pun_fit_oct"] = pt["a"] + pt["b"] * V["oct_ttf"] if V["oct_ttf"] else None
    # inflation
    nic = S["inflazione_nic"]
    V["nic"] = nic
    V["nic_last"] = nic["generale"][-1]
    V["nic_feb"] = at(nic["generale"], "2026-02")
    prev_hi = [x for x in nic["generale"] if x[1] >= V["nic_last"][1] and x[0] < "2026-01"]
    V["nic_prev_hi"] = prev_hi[-1] if prev_hi else None
    V["nic_max"] = max(nic["generale"], key=lambda x: x[1])
    hicp = S["hicp"]
    V["hicp"] = hicp
    V["hicp_last"] = hicp["generale"][-1]
    W = ii["pesi_hicp_millesimi"]
    V["W"] = {k: v["2026"] for k, v in W.items()}
    V["energy_contrib"] = V["W"]["NRG"] / 1000 * hicp["energia"][-1][1]
    conf = S["fiducia_consumatori"]
    V["conf"] = conf
    V["conf_min"] = min(conf["clima"], key=lambda x: x[1])
    sales = S["vendite_carburanti_kt"]
    V["sales"] = sales
    V["sales_last"] = sales[-1]
    V["sales_may"] = [s for s in sales if s["mese"] == "2026-05"][0]
    lit = {x["id"]: x for x in ii["regole_trasmissione"]["letteratura"]}
    V["lit"] = lit
    # haulage
    V["hau"] = ii["autotrasporto"]
    V["prec"] = ii["precedenti"]
    V["strikes"] = ii["scioperi_proclamati"]
    V["measures"] = {m["id"]: m for m in ii["misure_governo"]}
    V["scen"] = {s["id"]: s for s in ii["scenari"]}
    V["notice_days"] = 25
    V["earliest"] = (today + dt.timedelta(days=V["notice_days"])).isoformat()
    # precedents: diesel in the MASE survey of the week the protest began (a weekend start counts from the next Monday),
    # change on the same week a year earlier and over 8 weeks, recomputed from the weekly series (review, 10/11/2026:
    # the curated values in the file mixed different reference weeks).
    allw = sorted(list(EXTERNAL["mase_diesel_pre2022"]["values"].items()) + [tuple(x) for x in dsl])
    wk_map = dict(allw)
    for p in V["prec"]:
        gd = p.get("gasolio_alla_data")
        p["_8w"] = None
        if not gd:
            continue
        st0 = d(p["data_inizio"])
        if st0.weekday() >= 5:
            st0 += dt.timedelta(days=7 - st0.weekday())
        wk = (st0 - dt.timedelta(days=st0.weekday())).isoformat()
        val = wk_map.get(wk)
        ya = before(allw, (d(wk) - dt.timedelta(days=364)).isoformat())
        if val is None or ya is None:
            if p["id"] in PREC_EN:
                warn(f"precedent {p['id']}: week {wk} not in the MASE series; curated value kept")
        else:
            p["gasolio_alla_data"] = dict(gd, settimana=wk, eur_l=round(val, 3), var_pct_un_anno=round(var(val, ya[1]), 1), un_anno_prima=round(ya[1], 3))
            gd = p["gasolio_alla_data"]
        if gd["settimana"] >= dsl[0][0]:
            b8 = week_back(dsl, gd["settimana"], 8)
            p["_8w"] = var(gd["eur_l"], b8[1]) if b8 else None
    # gas Italy
    gi = load("gas-italia.json")
    V["gas_q"] = gi["quote_12_mesi"]
    V["gas_el"] = {e["id"]: e for e in gi["elementi"]}
    lng_ids = {e["id"] for e in gi["elementi"] if e["categoria"] == "gas-ingresso-gnl"}
    V["lng_ids"] = lng_ids
    V["lng_share"] = sum(q["quota_ingressi_pct"] for q in V["gas_q"] if q["id"] in lng_ids)
    m = V["gas_el"]["mazara"]["flussi"]["entry"]["riassunto"]
    V["mazara"] = m
    V["gas_period"] = (gi["elementi"][0]["flussi"]["entry"]["serie"][0][0], m["ultimo_giorno"])

    def monthly(eid):
        out = {}
        for t, v in V["gas_el"][eid]["flussi"]["entry"]["serie"]:
            out[t[:7]] = out.get(t[:7], 0) + v / 1000
        return out
    V["olt_m"] = monthly("olt")
    V["maz_m"] = monthly("mazara")
    # storage and stocks
    sc = load("scorte.json")
    E = {e["id"]: e for e in sc["elementi"]}
    V["st"] = {c: E[f"gas_stoccaggio_pct_{c}"]["ultimo"] for c in ("it", "de", "fr", "nl", "at")}
    V["st_twh"] = E["gas_stoccaggio_twh_it"]["ultimo"]
    need(E["gas_stoccaggio_twh_it"]["note"], "203.4", where="scorte.json gas_stoccaggio_twh_it")
    V["st_cap"] = 203.4
    V["oil_days"] = {c: E[f"petrolio_emergenza_giorni_{c}"]["ultimo"] for c in ("it", "de", "fr", "nl")}
    V["oil_it_series"] = E["petrolio_emergenza_giorni_it"]["serie"]
    # countries and trade
    pa = {e["paese"]: e for e in load("paesi.json")["elementi"]}["IT"]["indicatori"]
    V["pa"] = pa
    co = [e for e in load("commercio.json")["elementi"] if e["iso2"] == "IT"][0]
    V["hs27"] = [p for p in co["import_prodotti"] if p["hs"] == "27"][0]
    V["co_year"] = co["anno"]
    # ports
    pw = load("portwatch.json")
    ports = []
    for e in pw["elementi"]:
        if e["tipo"] != "porto":
            continue
        s = e["serie"]["portcalls"]
        lastd = e["ultima_data"]
        y0 = lastd[:4]
        a = [v for t, v in s if f"{y0}-01-01" <= t <= lastd]
        py = str(int(y0) - 1)
        b2 = [v for t, v in s if f"{py}-01-01" <= t <= f"{py}{lastd[4:]}"]
        ports.append({"name": PORT_EN.get(e["nome"], e["nome"]), "ytd_now": mean(a), "ytd_prev": mean(b2),
                      "ytd": var(mean(a), mean(b2)), "n": len(a), "var30": e["var30_anno_pct"],
                      "m30": e["media30"], "m30p": e["media30_anno_prima"], "last": lastd})
    ports.sort(key=lambda p: -p["ytd_now"])
    V["ports"] = ports
    V["pw_last"] = ports[0]["last"]
    pr = load("port-risk.json")
    V["pr"] = pr
    V["pr_it"] = sorted([p for p in pr["ports"] if p["country"] == "IT"], key=lambda p: p["rank"])
    V["pr_n"] = len(pr["ports"])
    tt = load("transit-times.json")
    V["tt"] = tt
    V["routes"] = {(r["from"], r["to"]): r for r in tt["routes"]}
    no = {e["id"]: e for e in load("noli.json")["elementi"]}
    V["wci"] = no["wci"]
    V["fbx"] = no["fbx"]
    # risk dashboard
    ri = load("rischio.json")
    V["ri"] = {u["id"]: u for u in ri["unita"]}
    V["ri_date"] = ri["data_riferimento"]
    # prices
    pz = {e["id"]: e for e in load("prezzi.json")["serie"]}
    V["brent"], V["ttf"], V["eurusd"] = pz["brent"], pz["ttf"], pz["eurusd"]
    V["brent_close"] = EXTERNAL["brent_close_9nov"]["value"] if pz["brent"]["data"] == EXTERNAL["brent_close_9nov"]["date"] else pz["brent"]["ultimo"]
    V["brent_eur_var_close"] = var(V["brent_close"] / today_b["eurusd"], base["brent"] / base["eurusd"])
    if abs(pz["brent"]["ultimo"] - o["brent"]) > 0.01:
        warn("Brent in prezzi.json differs from italia-impatti.json")
    # calendar
    cal = load("calendario.json")["elementi"]
    V["cal"] = cal
    # news
    nt = load("notizie-testate.json")
    V["news_it"] = [e for e in nt["elementi"] if "italia" in e.get("argomenti", [])]
    return V


# =====================================================================================
# SVG charts
# =====================================================================================
SVG_STYLE = """<style>
.it-t{font:600 14px 'IBM Plex Sans',system-ui,sans-serif;fill:#1D272D}
.it-l{font:12px 'IBM Plex Sans',system-ui,sans-serif;fill:#3b474e}
.it-m{font:11px 'IBM Plex Mono',ui-monospace,monospace;fill:#5f6b72}
.it-g{stroke:#d9dcd8;stroke-width:1}
.it-z{stroke:#5f6b72;stroke-width:1.2}
.it-s1{fill:#A61E6B}.it-s2{fill:#2a78d6}.it-s3{fill:#eda100}.it-s4{fill:#1baf7a}.it-s5{fill:#8a959b}
.it-k1{stroke:#A61E6B}.it-k2{stroke:#2a78d6}.it-k3{stroke:#eda100}.it-k4{stroke:#1baf7a}.it-k5{stroke:#8a959b}
.it-bg{fill:#ffffff}
.it-h{paint-order:stroke;stroke:#ffffff;stroke-width:4px;stroke-linejoin:round}
.it-o{stroke:#ffffff}
@media (prefers-color-scheme:dark){
.it-t{fill:#DAE0E2}.it-l{fill:#c3cacd}.it-m{fill:#99a5ab}.it-g{stroke:#2f3b42}.it-z{stroke:#99a5ab}
.it-s1{fill:#d14f9a}.it-s2{fill:#3987e5}.it-s3{fill:#c98500}.it-s4{fill:#199e70}.it-s5{fill:#7d888e}
.it-k1{stroke:#d14f9a}.it-k2{stroke:#3987e5}.it-k3{stroke:#c98500}.it-k4{stroke:#199e70}.it-k5{stroke:#7d888e}
.it-bg{fill:#172127}.it-h{stroke:#172127}.it-o{stroke:#172127}}
</style>"""
_style_done = {"v": False}


def svg_open(w, h, title, desc, uid):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" '
            f'aria-labelledby="{uid}-t {uid}-d" style="max-width:{w}px;height:auto;display:block">'
            f'<title id="{uid}-t">{esc(title)}</title><desc id="{uid}-d">{esc(desc)}</desc>{SVG_STYLE}'
            f'<rect class="it-bg" x="0" y="0" width="{w}" height="{h}" rx="6"/>')


def bar_path(x0, x1, y, h, r=4):
    if abs(x1 - x0) < 0.5:
        return f'M{x0:.1f},{y:.1f}h0.5v{h:.1f}h-0.5z'
    r = min(r, abs(x1 - x0), h / 2)
    if x1 >= x0:
        return (f'M{x0:.1f},{y:.1f}H{x1 - r:.1f}Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f}V{y + h - r:.1f}'
                f'Q{x1:.1f},{y + h:.1f} {x1 - r:.1f},{y + h:.1f}H{x0:.1f}Z')
    return (f'M{x0:.1f},{y:.1f}H{x1 + r:.1f}Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f}V{y + h - r:.1f}'
            f'Q{x1:.1f},{y + h:.1f} {x1 + r:.1f},{y + h:.1f}H{x0:.1f}Z')


def vbar_path(x, w, y0, y1, r=3):
    """Vertical bar from baseline y0 to y1 (y1 < y0 means up), rounded data end."""
    hgt = abs(y0 - y1)
    if hgt < 0.5:
        return f'M{x:.1f},{y0:.1f}h{w:.1f}v-0.5h-{w:.1f}z'
    r = min(r, w / 2, hgt)
    if y1 < y0:
        return (f'M{x:.1f},{y0:.1f}V{y1 + r:.1f}Q{x:.1f},{y1:.1f} {x + r:.1f},{y1:.1f}H{x + w - r:.1f}'
                f'Q{x + w:.1f},{y1:.1f} {x + w:.1f},{y1 + r:.1f}V{y0:.1f}Z')
    return (f'M{x:.1f},{y0:.1f}V{y1 - r:.1f}Q{x:.1f},{y1:.1f} {x + r:.1f},{y1:.1f}H{x + w - r:.1f}'
            f'Q{x + w:.1f},{y1:.1f} {x + w:.1f},{y1 - r:.1f}V{y0:.1f}Z')


def ticks(lo, hi, step):
    t, v = [], (int(lo // step)) * step
    while v <= hi + 1e-9:
        if v >= lo - 1e-9:
            t.append(round(v, 6))
        v += step
    return t


def legend(items, x, y, w, kind="rect"):
    o = []
    for nm, cls, dash in items:
        wd = 30 + len(nm) * 6.4
        if x + wd > w - 8:
            x, y = 12, y + 18
        if kind == "line":
            o.append(f'<line class="{cls.replace("s", "k")}" x1="{x}" x2="{x + 18}" y1="{y + 5}" y2="{y + 5}" stroke-width="2.5"{dash}/>')
            o.append(f'<text class="it-l" x="{x + 23}" y="{y + 9}">{esc(nm)}</text>')
            wd += 8
        else:
            o.append(f'<rect class="{cls}" x="{x}" y="{y}" width="12" height="10" rx="2"/><text class="it-l" x="{x + 17}" y="{y + 9}">{esc(nm)}</text>')
        x += wd + 6
    return "".join(o), y


def line_chart(uid, wide, title, desc, series, y_lo, y_hi, y_step, x_lo, x_hi, x_ticks, hlines=(), events=(), unit_fmt=lambda v: num(v, 2), monthly=False, label_last=None):
    w = 680 if wide else 360
    left, right = (44 if wide else 38), (60 if wide else 46)
    leg, ly = legend([(s[0], s[1], s[3]) for s in series], 12, 32, w, "line")
    top = ly + 30
    h = top + (240 if wide else 200) + 30
    y0, y1 = h - 30, top
    X = lambda t: left + (t - x_lo) / (x_hi - x_lo) * (w - left - right)
    Y = lambda v: y0 - (v - y_lo) / (y_hi - y_lo) * (y0 - y1)
    o = [svg_open(w, h, title, desc, uid), f'<text class="it-t" x="12" y="20">{esc(title)}</text>', leg]
    for t in ticks(y_lo, y_hi, y_step):
        o.append(f'<line class="{"it-z" if t == 0 else "it-g"}" x1="{left}" x2="{w - right}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/>'
                 f'<text class="it-m" x="{left - 5}" y="{Y(t) + 4:.1f}" text-anchor="end">{unit_fmt(t) if not float(t).is_integer() else num(t, 0) if y_step >= 1 else unit_fmt(t)}</text>')
    for lab, xt in x_ticks:
        o.append(f'<line class="it-g" x1="{X(xt):.1f}" x2="{X(xt):.1f}" y1="{y0}" y2="{y0 + 4}"/><text class="it-m" x="{X(xt):.1f}" y="{y0 + 16}" text-anchor="middle">{esc(lab)}</text>')
    for val, lab in hlines:
        o.append(f'<line class="it-z" x1="{left}" x2="{w - right}" y1="{Y(val):.1f}" y2="{Y(val):.1f}" stroke-dasharray="3 3"/>'
                 f'<text class="it-m it-h" x="{w - right + 3}" y="{Y(val) + 4:.1f}">{esc(lab)}</text>')
    for xt, n in events:
        o.append(f'<line class="it-g" x1="{X(xt):.1f}" x2="{X(xt):.1f}" y1="{y1 - 4}" y2="{y0}" stroke-dasharray="2 2"/>'
                 f'<circle cx="{X(xt):.1f}" cy="{y1 - 6}" r="7" class="it-s5"/><text class="it-m" x="{X(xt):.1f}" y="{y1 - 2.5}" text-anchor="middle" style="fill:#fff;font-size:9.5px">{n}</text>')
    for si, (nm, cls, pts_, dash) in enumerate(series):
        if not pts_:
            continue
        path = "M" + " L".join(f"{X(a):.1f},{Y(v):.1f}" for a, v in pts_)
        o.append(f'<path d="{path}" fill="none" class="{cls.replace("s", "k")}" stroke-width="2" stroke-linejoin="round"{dash}/>')
        for a, v in pts_[-1:]:
            o.append(f'<circle cx="{X(a):.1f}" cy="{Y(v):.1f}" r="3.5" class="{cls}"/>')
            if label_last is None or si in label_last:
                o.append(f'<text class="it-m it-h" x="{X(a) + 6:.1f}" y="{Y(v) + 4:.1f}">{unit_fmt(v)}</text>')
        # hover targets (one per point, thinned for long series)
        step = max(1, len(pts_) // 120)
        for a, v in pts_[::step]:
            o.append(f'<circle cx="{X(a):.1f}" cy="{Y(v):.1f}" r="5" fill="transparent"><title>{esc(nm)}: {unit_fmt(v)}</title></circle>')
    o.append("</svg>")
    return "".join(o)


def ordinal(s):
    return d(s).toordinal()


def chart_pump(V, wide):
    dsl, ptr = V["dsl"], V["ptr"]
    s = [("diesel", "it-s1", [(ordinal(k), v) for k, v in dsl], ""),
         ("petrol", "it-s2", [(ordinal(k), v) for k, v in ptr], ' stroke-dasharray="5 3"')]
    x_lo, x_hi = ordinal(dsl[0][0]), ordinal(dsl[-1][0]) + 20
    xt = [(str(y) if wide else f"'{str(y)[2:]}", ordinal(f"{y}-01-01")) for y in range(2022, 2027)]
    ev = [(ordinal("2022-03-22"), 1), (ordinal("2023-01-01"), 2), (ordinal("2026-02-28"), 3), (ordinal("2026-09-28"), 4)]
    lo, hi = V["thr"]
    return line_chart("c1" + ("w" if wide else "n"), wide, "Weekly pump prices, €/litre",
                      "Diesel and petrol, national weekly average (MASE), January 2022 to the latest week, with the monitor's 1.90 and 2.10 diesel thresholds.",
                      s, 1.5, 2.4, 0.1, x_lo, x_hi, xt, hlines=[(lo, num(lo, 2)), (hi, num(hi, 2))], events=ev,
                      unit_fmt=lambda v: num(v, 2) if abs(v * 10 - round(v * 10)) > 1e-6 else num(v, 1))


def chart_breakdown(V, wide):
    cs = V["ii"]["serie"]["carburanti_settimanali"]
    weeks = [V["pre"], "2026-04-13", V["dsl_max"][0], V["last_fuel"]]
    rows = []
    for k in weeks:
        net, exc, tot = at(cs["gasolio_netto"], k), at(cs["gasolio_accisa"], k), at(cs["gasolio"], k)
        rows.append((date_en(k, True) if wide else d(k).strftime("%d/%m/%y"), net, exc, tot - net - exc, tot))
    g = V["g"]
    net, exc = g["netto"], V["ordinary"]
    rows.append(("after 8 Nov (est.)" if wide else "post-8/11 est.", net, exc, V["dsl_post"] - net - exc, V["dsl_post"]))
    w = 680 if wide else 360
    left = 132 if wide else 92
    right = 48
    leg, ly = legend([("net of tax", "it-s2", ""), ("excise", "it-s1", ""), ("VAT 22%", "it-s3", "")], 12, 32, w)
    top = ly + 30
    rowh = 34
    h = top + rowh * len(rows) + 30
    hi = 2.5
    X = lambda v: left + v / hi * (w - left - right)
    o = [svg_open(w, h, "Diesel price breakdown, €/litre", "Stacked: net price, excise, VAT, for selected weeks (MASE).", "c2" + ("w" if wide else "n")),
         '<text class="it-t" x="12" y="20">What a litre of diesel is made of, €/litre</text>', leg]
    for t in ticks(0, hi, 0.5):
        o.append(f'<line class="it-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 6}" y2="{h - 26}"/><text class="it-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{num(t, 1)}</text>')
    for i, (lab, net, exc, vat, tot) in enumerate(rows):
        y = top + i * rowh
        o.append(f'<text class="it-l" x="{left - 8}" y="{y + 17}" text-anchor="end">{esc(lab)}</text>')
        x0 = 0
        for k, (v, cls, nm) in enumerate([(net, "it-s2", "net"), (exc, "it-s1", "excise"), (vat, "it-s3", "VAT")]):
            xa, xb = X(x0) + (1 if k else 0), X(x0 + v) - (1 if k < 2 else 0)
            dpath = bar_path(xa, xb, y + 4, 20) if k == 2 else f'M{xa:.1f},{y + 4}H{xb:.1f}V{y + 24}H{xa:.1f}Z'
            o.append(f'<path class="{cls}" d="{dpath}"><title>{esc(lab)}: {nm} €{num(v, 3)}</title></path>')
            x0 += v
        o.append(f'<text class="it-m" x="{X(tot) + 5:.1f}" y="{y + 18}">{num(tot, 3)}</text>')
    o.append("</svg>")
    return "".join(o), rows


def chart_gas(V, wide):
    Q = V["gas_q"]
    w = 680 if wide else 360
    left = 186 if wide else 126
    right = 50
    top = 54
    rowh = 26
    h = top + rowh * len(Q) + 30
    hi = 40
    X = lambda v: left + v / hi * (w - left - right)
    short = {"mazara": "Mazara (TransMed)", "melendugno": "Melendugno (TAP)", "adriatic": "Adriatic LNG", "gries": "Passo Gries",
             "piombino": "Piombino LNG", "olt": "OLT Livorno LNG", "ravenna": "Ravenna LNG", "tarvisio": "Tarvisio (TAG)",
             "panigaglia": "Panigaglia LNG", "gela": "Gela (Greenstream)", "gorizia": "Gorizia"}
    leg, _ = legend([("pipeline", "it-s2", ""), ("LNG terminal", "it-s1", "")], 12, 30, w)
    o = [svg_open(w, h, "Gas entering Italy by entry point, 12 months", "Share of physical entries by pipeline and LNG terminal (ENTSOG).", "c3" + ("w" if wide else "n")),
         '<text class="it-t" x="12" y="20">Gas entering Italy, share of entries, %</text>', leg]
    for t in ticks(0, hi, 10):
        o.append(f'<line class="it-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 6}" y2="{h - 26}"/><text class="it-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{int(t)}</text>')
    for i, q in enumerate(Q):
        y = top + i * rowh
        cls = "it-s1" if q["id"] in V["lng_ids"] else "it-s2"
        nm = short.get(q["id"], q["nome"])
        o.append(f'<text class="it-l" x="{left - 8}" y="{y + 14}" text-anchor="end">{esc(nm)}</text>')
        o.append(f'<path class="{cls}" d="{bar_path(X(0), X(q["quota_ingressi_pct"]), y + 3, 15)}"><title>{esc(nm)}: {num(q["quota_ingressi_pct"], 1)}% ({num(q["twh_12m"], 1)} TWh)</title></path>')
        o.append(f'<text class="it-m" x="{X(q["quota_ingressi_pct"]) + 5:.1f}" y="{y + 14}">{num(q["quota_ingressi_pct"], 1)}</text>')
    o.append("</svg>")
    return "".join(o), short


def chart_pun(V, wide):
    M = V["pun_m"]
    w = 680 if wide else 360
    left, right = 42, (78 if wide else 62)
    top = 52
    h = top + (220 if wide else 190) + 34
    y0, y1 = h - 34, top
    hi = 320
    Y = lambda v: y0 - v / hi * (y0 - y1)
    bw = (w - left - right) / len(M)
    o = [svg_open(w, h, "Wholesale electricity price (PUN), monthly average", "Monthly PUN in €/MWh (GME); latest month partial; 2022 and 2025 annual averages as reference lines.", "c4" + ("w" if wide else "n")),
         '<text class="it-t" x="12" y="20">Wholesale electricity (PUN), €/MWh</text>']
    leg, _ = legend([("monthly average", "it-s1", ""), ("month in progress (partial)", "it-s5", "")], 12, 30, w)
    o.append(leg)
    for t in ticks(0, hi, 50 if wide else 100):
        o.append(f'<line class="it-g" x1="{left}" x2="{w - right}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/><text class="it-m" x="{left - 5}" y="{Y(t) + 4:.1f}" text-anchor="end">{int(t)}</text>')
    for yr in ("2022", "2025"):
        v = V["pun_y"][yr]
        o.append(f'<line class="it-z" x1="{left}" x2="{w - right}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke-dasharray="3 3"/>'
                 f'<text class="it-m it-h" x="{w - right + 3}" y="{Y(v) + 4:.1f}">{yr} avg</text>')
    for i, (m, v) in enumerate(M):
        x = left + i * bw + 2
        cls = "it-s5" if m == V["pun_nov"][0] else "it-s1"
        o.append(f'<path class="{cls}" d="{vbar_path(x, bw - 4, y0, Y(v))}"><title>{month_en(m)}: {num(v, 2)} €/MWh{" (partial)" if cls == "it-s5" else ""}</title></path>')
        if wide or i % 2 == 0:
            lab = MON[d(m).month - 1] + ("" if wide else "")
            o.append(f'<text class="it-m" x="{x + (bw - 4) / 2:.1f}" y="{y0 + 14}" text-anchor="middle">{lab}</text>')
        if m.endswith("-01") or i == 0:
            o.append(f'<text class="it-m" x="{x + (bw - 4) / 2:.1f}" y="{y0 + 27}" text-anchor="middle">{m[:4]}</text>')
        if i >= len(M) - 2 or (wide and i == 0):
            o.append(f'<text class="it-m it-h" x="{x + (bw - 4) / 2:.1f}" y="{Y(v) - 5:.1f}" text-anchor="middle">{num(v, 0)}</text>')
    o.append("</svg>")
    return "".join(o)


def chart_infl(V, wide):
    n = V["nic"]
    mk = lambda key: [(ordinal(k + "-01"), v) for k, v in n[key]]
    s = [("energy", "it-s1", mk("energetici"), ""), ("headline", "it-s2", mk("generale")[-10:], ""),
         ("food", "it-s3", mk("alimentari"), ' stroke-dasharray="5 3"'), ("core", "it-s4", mk("componente_di_fondo"), ' stroke-dasharray="2 3"')]
    x_lo, x_hi = ordinal("2026-01-01"), ordinal(n["generale"][-1][0] + "-01") + 12
    xt = [(MON[m - 1] if wide or m % 3 == 1 else "", ordinal(f"2026-{m:02d}-01")) for m in range(1, 11)]
    return line_chart("c5" + ("w" if wide else "n"), wide, "Consumer prices (NIC), % on a year earlier, 2026",
                      "Istat NIC annual rates: headline, energy, food, core, January to October 2026 (October preliminary).",
                      s, -10, 35, 5, x_lo, x_hi, xt, events=[(ordinal("2026-02-28"), 1)], unit_fmt=lambda v: num(v, 1), label_last=(0, 1))


def chart_sales(V, wide):
    S = [x for x in V["sales"] if x["mese"] >= "2026-01"]
    keys = [("gasolio_motori", "road diesel", "it-s1"), ("gasolio_extrarete", "diesel to fleets (off-network)", "it-s3"), ("benzina", "petrol", "it-s2")]
    w = 680 if wide else 360
    left, right = 40, 12
    leg, ly = legend([(k[1], k[2], "") for k in keys], 12, 30, w)
    top = ly + 34
    h = top + (220 if wide else 200) + 30
    y0, y1 = h - 30, top
    lo, hi = -16, 12
    Y = lambda v: y0 - (v - lo) / (hi - lo) * (y0 - y1)
    gw = (w - left - right) / len(S)
    bw = (gw - 6) / 3
    o = [svg_open(w, h, "Fuel sales, % on the same month a year earlier", "MASE monthly sales: road diesel, off-network diesel and petrol, 2026.", "c6" + ("w" if wide else "n")),
         '<text class="it-t" x="12" y="20">Fuel sales, % on a year earlier</text>', leg]
    for t in ticks(lo, hi, 4):
        o.append(f'<line class="{"it-z" if t == 0 else "it-g"}" x1="{left}" x2="{w - right}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/><text class="it-m" x="{left - 5}" y="{Y(t) + 4:.1f}" text-anchor="end">{num(t, 0)}</text>')
    ev = d("2026-02-28")
    for i, s in enumerate(S):
        gx = left + i * gw + 3
        for j, (k, nm, cls) in enumerate(keys):
            v = s[k]["var_pct"]
            x = gx + j * bw
            o.append(f'<path class="{cls}" d="{vbar_path(x + 0.5, bw - 1, Y(0), Y(v), 2)}"><title>{month_en(s["mese"])}, {nm}: {pct(v)}</title></path>')
        o.append(f'<text class="it-m" x="{gx + (gw - 6) / 2:.1f}" y="{y0 + 16}" text-anchor="middle">{MON[d(s["mese"]).month - 1] if wide else MON[d(s["mese"]).month - 1][0]}</text>')
        if s["mese"] == "2026-03":
            o.append(f'<line class="it-g" x1="{gx - 3:.1f}" x2="{gx - 3:.1f}" y1="{y1 - 6}" y2="{y0}" stroke-dasharray="2 2"/>'
                     f'<circle cx="{gx - 3:.1f}" cy="{y1 - 8}" r="7" class="it-s5"/><text class="it-m" x="{gx - 3:.1f}" y="{y1 - 4.5}" text-anchor="middle" style="fill:#fff;font-size:9.5px">1</text>')
    o.append("</svg>")
    return "".join(o)


def chart_protests(V, wide):
    P = [p for p in V["prec"] if p["paese"] == "IT" and p["tipo"].startswith("protesta-autotrasporto") or p["id"] == "trattori-2024"]
    P = [p for p in P if p.get("gasolio_alla_data")]
    names = PREC_EN
    w = 680 if wide else 360
    left = 196 if wide else 112
    right = 70 if wide else 58
    top = 58
    rowh = 30
    rows = P + [None]
    h = top + rowh * len(rows) + 30
    lo_, hi_ = 1.0, 2.5
    X = lambda v: left + (v - lo_) / (hi_ - lo_) * (w - left - right)
    leg, _ = legend([("haulage protest", "it-s1", ""), ("other protest", "it-s5", ""), ("today", "it-s2", "")], 12, 30, w)
    o = [svg_open(w, h, "Diesel price at the start of each protest", "Weekly diesel price (MASE) in the week each protest began, with the change on a year earlier.", "c8" + ("w" if wide else "n")),
         '<text class="it-t" x="12" y="20">Diesel at the start of each protest, €/litre</text>', leg]
    for t in ticks(lo_, hi_, 0.25 if wide else 0.5):
        o.append(f'<line class="it-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 6}" y2="{h - 26}"/><text class="it-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{num(t, 2)}</text>')
    for val in V["thr"]:
        o.append(f'<line class="it-z" x1="{X(val):.1f}" x2="{X(val):.1f}" y1="{top - 6}" y2="{h - 26}" stroke-dasharray="3 3"/>')
    for i, p in enumerate(rows):
        y = top + i * rowh
        if p is None:
            v, yoy, nm, cls = V["g"]["eur_l"], V["dsl_yoy"], ("Today (week of " + date_en(V["last_fuel"], False) + ")") if wide else "Today", "it-s2"
        else:
            gd = p["gasolio_alla_data"]
            v, yoy = gd["eur_l"], gd["var_pct_un_anno"]
            nm = names[p["id"]][1 if wide else 2]
            cls = "it-s5" if p["id"] == "trattori-2024" else "it-s1"
        o.append(f'<text class="it-l" x="{left - 8}" y="{y + 16}" text-anchor="end">{esc(nm)}</text>')
        o.append(f'<line class="it-g" x1="{X(lo_):.1f}" x2="{X(v):.1f}" y1="{y + 12}" y2="{y + 12}"/>')
        o.append(f'<circle cx="{X(v):.1f}" cy="{y + 12}" r="6" class="{cls} it-o" stroke-width="2"><title>{esc(nm)}: €{num(v, 3)}/l, {pct(yoy)} on a year</title></circle>')
        o.append(f'<text class="it-m" x="{X(v) + 10:.1f}" y="{y + 16}">{num(v, 2)} ({pct(yoy, 0)})</text>')
    o.append("</svg>")
    return "".join(o), P


PREC_EN = {
    "fermo-tir-2007": ("National truck stoppage", "Dec 2007, national stoppage", "Dec 2007"),
    "forconi-sicilia-2012": ("Forconi blockades, Sicily", "Jan 2012, Forconi, Sicily", "Jan 2012 Sicily"),
    "blocchi-tir-gennaio-2012": ("Truck blockades across Italy", "Jan 2012, blockades in Italy", "Jan 2012 Italy"),
    "blocchi-tir-marzo-2022": ("Truckers' protest", "Mar 2022, truckers' protest", "Mar 2022"),
    "trattori-2024": ("Tractor protests (farm income tax, EU farm policy)", "Jan 2024, tractors (not fuel)", "Jan 2024 tractors"),
    "fermo-trasportounito-aprile-2026": ("Trasportounito stoppage (suspended on day one)", "Apr 2026, Trasportounito", "Apr 2026"),
    "fermo-unatras-maggio-2026": ("Unatras national stoppage (suspended)", "May 2026, Unatras (suspended)", "May 2026"),
    "fermi-regionali-ottobre-2026": ("Regional stoppages, Sicily and Calabria", "Oct 2026, Sicily and Calabria", "Oct 2026"),
}


def chart_ports(V, wide):
    P = V["ports"]
    w = 680 if wide else 360
    left = 132 if wide else 100
    right = 40
    leg, ly = legend([("1 Jan to latest day", "it-s2", ""), ("last 30 days", "it-s1", "")], 12, 30, w)
    top = ly + 30
    rowh = 34
    h = top + rowh * len(P) + 30
    lo, hi = -30, 40
    X = lambda v: left + (v - lo) / (hi - lo) * (w - left - right)
    o = [svg_open(w, h, "Italian ports: ship calls vs a year earlier", "PortWatch ship calls per day, year to date and last 30 days, change on the same days of 2025.", "c7" + ("w" if wide else "n")),
         '<text class="it-t" x="12" y="20">Ship calls vs a year earlier, %</text>', leg]
    for t in ticks(lo, hi, 10 if wide else 20):
        o.append(f'<line class="{"it-z" if t == 0 else "it-g"}" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 6}" y2="{h - 26}"/><text class="it-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{"0" if t == 0 else f"{int(t):+d}".replace("-", "−")}</text>')
    for i, p in enumerate(P):
        y = top + i * rowh
        pn = p["name"] if wide else p["name"].replace("Malamocco", "Mal.")
        o.append(f'<text class="it-l" x="{left - 8}" y="{y + 17}" text-anchor="end">{esc(pn)}</text>')
        for j, (k, cls) in enumerate([("ytd", "it-s2"), ("var30", "it-s1")]):
            v = p[k]
            yy = y + 4 + j * 13
            o.append(f'<path class="{cls}" d="{bar_path(X(0), X(v), yy, 11)}"><title>{esc(p["name"])}: {pct(v)} ({"year to date" if k == "ytd" else "last 30 days"})</title></path>')
            o.append(f'<text class="it-m" x="{X(v) + (4 if v >= 0 else -4):.1f}" y="{yy + 9.5}" text-anchor="{"start" if v >= 0 else "end"}">{"0%" if abs(v) < 0.5 else pct(v, 0)}</text>')
    o.append("</svg>")
    return "".join(o)


def chart_transit(V, wide):
    R = V["routes"]
    rows = [("Shanghai → Genoa", R[("shanghai", "genoa")]), ("Shanghai → Trieste", R[("shanghai", "trieste")]),
            ("Shanghai → Rotterdam", R[("shanghai", "rotterdam")]), ("Singapore → Genoa", R[("singapore", "genoa")]),
            ("Mumbai → Genoa", R[("nhava_sheva", "genoa")] if ("nhava_sheva", "genoa") in R else None)]
    rows = [r for r in rows if r[1]]
    w = 680 if wide else 360
    left = 150 if wide else 132
    right = 30
    leg, ly = legend([("via Suez", "it-s2", ""), ("today's mix (63% Suez)", "it-s1", ""), ("via the Cape", "it-s3", "")], 12, 30, w)
    top = ly + 30
    rowh = 32
    h = top + rowh * len(rows) + 30
    hi = 45
    X = lambda v: left + v / hi * (w - left - right)
    o = [svg_open(w, h, "Container transit times to Genoa and Trieste", "Sea days via Suez, via the Cape, and today's weighted mix (transit-times.json model).", "c9" + ("w" if wide else "n")),
         '<text class="it-t" x="12" y="20">Container transit time, days at sea</text>', leg]
    for t in ticks(0, hi, 10 if wide else 15):
        o.append(f'<line class="it-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 6}" y2="{h - 26}"/><text class="it-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{int(t)}</text>')
    for i, (nm, r) in enumerate(rows):
        y = top + i * rowh + 12
        a, c, m = r["days_base"], r["cape"]["days"], r.get("days_today_weighted")
        o.append(f'<text class="it-l" x="{left - 8}" y="{y + 4}" text-anchor="end">{esc(nm)}</text>')
        o.append(f'<line class="it-g" x1="{X(a):.1f}" x2="{X(c):.1f}" y1="{y}" y2="{y}" stroke-width="3"/>')
        for v, cls, lab in [(a, "it-s2", "via Suez"), (c, "it-s3", "via the Cape"), (m, "it-s1", "today's mix")]:
            if v is None:
                continue
            o.append(f'<circle cx="{X(v):.1f}" cy="{y}" r="6" class="{cls} it-o" stroke-width="2"><title>{esc(nm)}: {num(v, 1)} days {lab}</title></circle>')
        o.append(f'<text class="it-m" x="{X(a):.1f}" y="{y - 9}" text-anchor="middle">{num(a, 1)}</text>')
        o.append(f'<text class="it-m" x="{X(c):.1f}" y="{y - 9}" text-anchor="middle">{num(c, 1)}</text>')
    o.append("</svg>")
    return "".join(o), rows


def chart_scen(V, wide):
    S = V["scen"]
    names = {"hormuz_1m": "Hormuz closed, 1 month", "hormuz_3m": "Hormuz closed, 3 months", "mar_rosso_1m": "Red Sea via the Cape, 1 month", "transmed_1m": "TransMed shut, 1 month"}
    shortn = {"hormuz_1m": "Hormuz 1 m", "hormuz_3m": "Hormuz 3 m", "mar_rosso_1m": "Red Sea 1 m", "transmed_1m": "TransMed 1 m"}
    w = 680 if wide else 360
    left = 200 if wide else 92
    right = 24
    leg, ly = legend([("from pre-war prices (Feb 2026)", "it-s2", ""), ("from today's prices", "it-s1", ""), ("observed in 2026 (no excise cut)", "it-s3", "")], 12, 30, w)
    top = ly + 30
    rowh = 46
    h = top + rowh * len(S) + 30
    lo, hi = (1.3, 3.2) if wide else (1.5, 3.2)
    X = lambda v: left + (v - lo) / (hi - lo) * (w - left - right)
    o = [svg_open(w, h, "Scenario ranges for the diesel price", "Assessment: diesel €/litre ranges from the transmission rules, two starting points; observed 2026 values for the Hormuz scenarios.", "c10" + ("w" if wide else "n")),
         '<text class="it-t" x="12" y="20">Diesel in each scenario, €/litre (assessment)</text>', leg]
    for t in ticks(1.5, hi, 0.25 if wide else 0.5):
        o.append(f'<line class="it-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 6}" y2="{h - 26}"/><text class="it-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{num(t, 2)}</text>')
    for val in V["thr"]:
        o.append(f'<line class="it-z" x1="{X(val):.1f}" x2="{X(val):.1f}" y1="{top - 6}" y2="{h - 26}" stroke-dasharray="3 3"/>')
    for i, (k, s) in enumerate(S.items()):
        y = top + i * rowh
        o.append(f'<text class="it-l" x="{left - 8}" y="{y + 18}" text-anchor="end">{esc(names[k] if wide else shortn[k])}</text>')
        for j, (base, cls) in enumerate([("da_condizioni_normali", "it-s2"), ("da_oggi", "it-s1")]):
            a, b = s[base]["gasolio_eur_l"]
            yy = y + 4 + j * 15
            xa, xb = X(a), max(X(b), X(a) + 4)
            o.append(f'<path class="{cls}" d="M{xa:.1f},{yy}H{xb:.1f}V{yy + 11}H{xa:.1f}Z" rx="2"><title>{esc(names[k])}, {"from pre-war prices" if j == 0 else "from today"}: €{num(a, 2)}–{num(b, 2)}</title></path>')
            lab = num(a, 2) if num(a, 2) == num(b, 2) else f"{num(a, 2)}–{num(b, 2)}"
            if wide or j == 1:
                o.append(f'<text class="it-m it-h" x="{xa - 4:.1f}" y="{yy + 9.5}" text-anchor="end">{lab}</text>')
        ob = s.get("osservato", {}).get("gasolio")
        if ob and k.startswith("hormuz"):
            for v in (ob["media_senza_tagli_accise"], ob["max_senza_tagli_accise"]):
                o.append(f'<path class="it-s3 it-o" stroke-width="1.5" d="M{X(v):.1f},{y + 2} l5,7 l-5,7 l-5,-7z"><title>{esc(names[k])}: observed €{num(v, 3)} (average and peak without excise cuts)</title></path>')
    o.append("</svg>")
    return "".join(o), names


def table_html(head, rows):
    return ('<div class="tabella"><table><thead><tr>' + "".join(f"<th>{esc(x)}</th>" for x in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")


# =====================================================================================
# Text blocks
# =====================================================================================
def blocks(V, edition, today):
    ii, g, b = V["ii"], V["g"], V["b"]
    R, est, lit = V["R"], V["est"], V["lit"]
    B = []
    P = lambda t: B.append(("p", t))
    A = lambda t: B.append(("val", "*Assessment.* " + t[0].upper() + t[1:]))
    H2 = lambda i, t: B.append(("h2", i, t))
    H3 = lambda t: B.append(("h3", t))
    UL = lambda x: B.append(("ul", x))
    TAB = lambda h, r, n="": B.append(("tab", h, r, n))
    FIG = lambda k, c: B.append(("fig", k, c))
    st, it = V["st"], V["st"]["it"]
    sh = {q["id"]: q for q in V["gas_q"]}
    pa = V["pa"]
    nic = V["nic"]
    hau = V["hau"]
    sc = V["scen"]
    brent, ttf = V["brent"], V["ttf"]
    lastd = V["last_fuel"]
    sales = V["sales_last"]
    Ra = V["ri"]
    lo, hi = V["thr"]
    # ------------------------------------------------------------------ 1
    H2("key", "1. Key points")
    mm9 = EXTERNAL["mimit_9nov"]
    k1 = (f"**Diesel has risen less than the end of the excise cut implies.** The {num(V['cut_cents_vat'], 1)}-cent cut expired on 8 November. "
          f"Diesel averaged €{num(g['eur_l'], 3)} a litre in the week of {date_en(lastd, False)} (MASE), {pct(V['dsl_yoy'], 0)} on a year; full excise would make it "
          f"€{num(V['dsl_post'], 3)} (calculation). Self-service diesel rose only from €{num(mm9['self_7nov'], 3)} to €{num(mm9['self_9nov'], 3)} between 7 and 9 November (Mimit).")
    W_ = V["W"]
    eg = (W_['CP0451'] * nic['elettricita'][-1][1] + W_['CP0452'] * nic['gas'][-1][1]) / 1000
    fu = W_['FUEL'] * nic['carburanti'][-1][1] / 1000
    k2 = (f"**Gas and power bills now push inflation more than fuel does.** Consumer prices (Istat NIC, preliminary) were up {num(V['nic_last'][1], 1)}% on a year in "
          f"{month_en(V['nic_last'][0])}, from {num(V['nic_feb'], 1)}% in February. Electricity (+{num(nic['elettricita'][-1][1], 1)}%) and gas (+{num(nic['gas'][-1][1], 1)}%) "
          f"account for about {num(eg, 1)} points, fuels for about {num(fu, 1)} (calculation). The wholesale power price (PUN) averaged {num(V['pun_oct'][1], 1)} €/MWh in October.")
    k3 = (f"**Italy has the gas; the problem is its price.** Storage was {num(it['valore'], 1)}% full on {date_en(it['data'], False)} "
          f"(Germany {num(st['de']['valore'], 1)}%). Algeria's TransMed pipeline, flowing normally, brought {num(sh['mazara']['quota_ingressi_pct'], 0)}% of imported gas over 12 months; "
          f"Qatar, in force majeure since March, supplied {num(pa['quota_gnl_golfo_persico']['valore']['min_pct'], 1)}% of LNG imports by value in 2025. "
          f"The Dutch TTF gas price, which Italy's follows, was {pct(ttf['var']['1a'], 0)} on a year on {date_en(ttf['data'], False)}.")
    k4 = (f"**No national truck stoppage had been called by 9 November, and none can lawfully start before {date_en(V['earliest'], False)}.** "
          f"Hauliers must give the Strike Guarantee Commission {V['notice_days']} days' notice. Diesel has been above the monitor's €{num(hi, 2)} alert level since the week of "
          f"{date_en(V['above_since'], False)}. *Assessment:* the risk that a stoppage is called before the end of the year is high; wildcat blockades need no notice.")
    s1 = sc["hormuz_1m"]
    k5 = (f"**A second Hormuz shock would put diesel at €{num(s1['da_oggi']['gasolio_eur_l'][0], 2)}–{num(s1['da_oggi']['gasolio_eur_l'][1], 2)} within a month** "
          f"(*assessment*: Brent up {num(s1['ingresso']['brent_pct'][0], 0)}–{num(s1['ingresso']['brent_pct'][1], 0)}% as in March 2026, no new tax cuts). Tested on 2026: from pre-war prices the rule gave "
          f"€{num(s1['da_condizioni_normali']['gasolio_eur_l'][0], 2)}–{num(s1['da_condizioni_normali']['gasolio_eur_l'][1], 2)}; diesel averaged "
          f"€{num(s1['osservato']['gasolio']['media_senza_tagli_accise'], 2)} once the excise cuts are added back. A TransMed outage would hit bills, not pumps.")
    UL([k1, k2, k3, k4, k5])
    for k in (k1, k2, k3, k4, k5):
        nw = len(re.sub(r"[*\[\]()`]", "", k).split())
        if nw > 66:
            warn(f"key point over 60 words ({nw}): {k[:60]}")
    B.append(("gloss", [
        ("MASE", "Ministry of the Environment and Energy Security; publishes the weekly national average of fuel prices, with tax and excise broken out"),
        ("Mimit", "Ministry of Enterprises and Made in Italy; runs the daily fuel-price observatory fed by every filling station; the daily national averages quoted in the press are for self-service"),
        ("ARERA", "the energy regulator; sets the gas price for 'vulnerable' households still on regulated terms"),
        ("GME", "the operator of Italy's power and gas exchanges"),
        ("PUN", "the national wholesale electricity price, set daily on the GME exchange, in €/MWh"),
        ("PSV / TTF", "the Italian and Dutch wholesale gas prices; the Italian one tracks the Dutch one closely"),
        ("Istat, NIC, HICP", "the national statistics institute; NIC is its consumer price index for the whole population, HICP the EU-harmonised version"),
        ("Excise (accisa)", "a fixed tax per litre on fuel; VAT at 22% is charged on top of it"),
        ("Fermo", "a stoppage of road hauliers: firms keep their trucks off the road; it is treated like a strike"),
        ("Unatras", "the joint committee of the main road-haulage associations; Trasportounito and Federtrasporti are associations outside it"),
        ("Excise refund (rimborso accise)", "hauliers with trucks of 7.5 tonnes or more get back, every quarter, the diesel excise above a fixed reference rate"),
        ("CNR", "Comité national routier, the French road-haulage cost observatory, used here for want of an Italian figure"),
        ("Law 146/1990", "the law on strikes in essential public services; an independent Strike Guarantee Commission (Commissione di garanzia) enforces notice and minimum services"),
        ("Precettazione", "an order by a minister or prefect that obliges workers or firms to keep an essential service running during a strike"),
        ("ENTSOG, GIE AGSI+, PortWatch", "the European gas network operators' flow platform; the European gas storage database; the IMF's ship-tracking service"),
        ("LNG, FSRU", "liquefied natural gas; a floating storage and regasification unit is a ship-based import terminal"),
        ("FEU, AIS", "a 40-foot container; the transponder ships use to broadcast position, the basis of PortWatch counts"),
    ]))
    # ------------------------------------------------------------------ 2
    H2("supply", "2. Where Italy's energy comes from and what the Gulf crisis changed")
    P(f"Italy imports {num(pa['dipendenza_energetica']['valore'], 1)}% of the energy it uses, {num(pa['dipendenza_gas']['valore'], 1)}% of its gas and "
      f"{num(pa['dipendenza_petrolio']['valore'], 1)}% of its oil (net imports over gross supply, {pa['dipendenza_energetica']['anno']}, Eurostat via {dl('paesi.json')}). "
      f"Fuels (HS chapter 27) were {num(V['hs27']['quota'], 1)}% of the value of everything Italy imported in {V['co_year']}, "
      f"{num(V['hs27']['valore_usd'] / 1e9, 1)} billion dollars (UN Comtrade, {dl('commercio.json')}).")
    H3("Gas: six pipelines, five LNG terminals")
    p0, p1 = V["gas_period"]
    P(f"In the 12 months to {date_en(p1)} the largest entry point was **Mazara del Vallo**, where Algerian gas arrives through the TransMed pipeline system "
      f"(several parallel lines under the Sicily Channel): {num(sh['mazara']['twh_12m'], 1)} TWh, {num(sh['mazara']['quota_ingressi_pct'], 1)}% of all gas entering by pipe and ship. "
      f"Next came the TAP pipeline from Azerbaijan at Melendugno ({num(sh['melendugno']['quota_ingressi_pct'], 1)}%) and the five LNG terminals together "
      f"({num(V['lng_share'], 1)}%; Adriatic LNG alone {num(sh['adriatic']['quota_ingressi_pct'], 1)}%). Residual Russian gas through Tarvisio was "
      f"{num(sh['tarvisio']['quota_ingressi_pct'], 1)}% (ENTSOG daily physical flows, {dl('gas-italia.json')}). National production and storage are not in these shares.")
    FIG("gas", f"*Share of gas entering Italy by entry point, 12 months to {date_en(p1)}, % of physical entries (pipelines and LNG terminals; national production and storage excluded). "
               f"Source: ENTSOG Transparency Platform (Snam Rete Gas data), {dl('gas-italia.json')}, data to {date_en(p1)}; the last days may be revised.*")
    om = V["olt_m"]
    mm = V["maz_m"]
    P(f"Two movements stand out. OLT, the floating terminal off Livorno, delivered {num(om.get('2026-10'), 1)} TWh in October against "
      f"{num(om.get('2026-09'), 1)} in September; it restarted on {date_en(V['gas_el']['olt']['flussi']['entry']['riassunto']['ultimo_giorno'], False)} "
      f"({num(V['gas_el']['olt']['flussi']['entry']['riassunto']['ultimo_gwh'], 0)} GWh). Mazara dipped to {num(mm.get('2026-09'), 1)} TWh in September, from "
      f"{num(mm.get('2026-08'), 1)} in August, and recovered to {num(mm.get('2026-10'), 1)} in October. **Missing:** the cause of either change is not in the data.")
    q = Ra["gnl-qatar"]
    fl = [x for x in pa["fornitori_gnl"]["valore"]]
    P(f"**LNG from Qatar.** In {pa['fornitori_gnl']['anno']} the United States supplied {num(fl[0]['quota_pct'], 1)}% of the value of Italy's LNG imports, "
      f"Qatar {num(fl[1]['quota_pct'], 1)}% and Algeria {num(fl[2]['quota_pct'], 1)}% (UN Comtrade, {dl('paesi.json')}). "
      f"{EXTERNAL['qatar_fm']['text'][0].upper() + EXTERNAL['qatar_fm']['text'][1:]} ({link('gasworld', EXTERNAL['qatar_fm']['link'])}), and "
      f"{EXTERNAL['qatar_trains']['text']} ({link('Reuters via Cyprus Mail, 12 October 2026', EXTERNAL['qatar_trains']['link'])}; the monitor's Hormuz report identifies "
      f"the damaged units as trains 4 and 6, about 12.8 Mt a year). The monitor's risk dashboard rates Qatari LNG "
      f"**{LEVEL[q['livello']]}**, {num(q['punteggio'], 1)} out of 25 ({dl('rischio.json')}, {date_en(V['ri_date'])}). **Missing:** the origin of the cargoes that reached "
      f"Italian terminals in 2026 (it would need Kpler or GIIGNL data).")
    tm = Ra["transmed"]
    m = V["mazara"]
    P(f"**TransMed.** The same dashboard rates the pipeline **{LEVEL[tm['livello']]}** at {num(tm['punteggio'], 1)} out of 25 "
      f"(probability {num(tm['probabilita'], 1)} of 5, impact {num(tm['impatto'], 1)} of 5), down from {num(tm['punteggio_7g_fa'], 1)} a week earlier. "
      f"Flows were normal: {num(m['media_7g_gwh'], 1)} GWh a day over the last seven days against a 12-month average of {num(m['media_365g_gwh'], 1)}. "
      f"It is Italy's largest single gas dependency, not its most likely disruption.")
    H3("Crude oil: little from the Gulf")
    fg = pa["fornitori_greggio"]["valore"]
    TAB(["Supplier", f"Share of crude imports, {pa['fornitori_greggio']['anno']}", "How it reaches Italy"],
        [[x["nome"].replace("Libia", "Libya").replace("Azerbaigian", "Azerbaijan").replace("Kazakistan", "Kazakhstan").replace("Stati Uniti", "United States"),
          f"{num(x['quota_pct'], 1)}%", {"LY": "Mediterranean", "AZ": "pipeline to Ceyhan (Turkey), then tanker", "KZ": "CPC pipeline to the Black Sea, then the Turkish Straits",
                                          "US": "Atlantic, Gibraltar", "NG": "Atlantic, Gibraltar"}.get(x["paese"], "")] for x in fg],
        f"Share of the value of crude imports (UN Comtrade, as declared by Italy), {dl('paesi.json')}. Routes are the usual ones, added by the monitor.")
    gq = pa["quota_greggio_golfo_persico"]["valore"]
    P(f"Between {num(gq['min_pct'], 1)}% and {num(gq['max_pct'], 1)}% of Italy's crude came from the Gulf in {pa['quota_greggio_golfo_persico']['anno']} "
      f"(the lower figure counts only suppliers with no route around Hormuz; the higher one adds Saudi Arabia and the UAE). The exposure is through price and refined products. "
      f"The president of the fuel industry association Unem said in April that falls in diesel prices would prove temporary, citing among other things the closure of more than 30 European "
      f"refineries in fifteen years ({link('Il Fatto Quotidiano, 17 April 2026', lit['unem-raffinazione']['link'])}; reliability medium).")
    need(lit["unem-raffinazione"]["testo"], "30 raffinerie", where="italia-impatti.json letteratura unem")
    H3("Emergency stocks: oil below the norm, gas close to target")
    od = V["oil_days"]
    ser = V["oil_it_series"]
    P(f"Italy's emergency oil stocks covered **{num(od['it']['valore'], 1)} days** in {month_en(od['it']['data'])}, against {num(od['it']['anno_scorso']['valore'], 1)} a year earlier "
      f"and a five-year average of {num(od['it']['media_5_anni']['valore'], 1)} (Eurostat, {dl('scorte.json')}). EU law (directive 2009/119/EC) requires the larger of "
      f"90 days of net imports or 61 days of consumption. The series fell from {num(at(ser, '2026-03-01'), 1)} days in March to {num(at(ser, '2026-04-01'), 1)} in April 2026. "
      f"Germany held {num(od['de']['valore'], 1)}, France {num(od['fr']['valore'], 1)} and the Netherlands {num(od['nl']['valore'], 1)} days. The June figure "
      f"({num(at(ser, '2026-06-01'), 1)}, between {num(at(ser, '2026-05-01'), 1)} in May and {num(at(ser, '2026-07-01'), 1)} in July) is almost certainly a reporting anomaly and is not used. "
      f"**Missing:** whether the spring drawdown was part of a coordinated stock release (the Hormuz report suggests it probably was).")
    P(f"Gas storage was **{num(it['valore'], 1)}%** full on {date_en(it['data'])} ({num(V['st_twh']['valore'], 1)} TWh of about {num(V['st_cap'], 1)}), "
      f"{pts(it['anno_scorso']['variazione'], 1)} points on a year earlier and {pts(it['media_5_anni']['scarto'], 1)} on the five-year average; winter withdrawals began on "
      f"1 November and took {num(abs(it['precedente']['variazione']), 2)} points on the last day. Germany was at {num(st['de']['valore'], 1)}%, the Netherlands "
      f"{num(st['nl']['valore'], 1)}%, Austria {num(st['at']['valore'], 1)}% and France {num(st['fr']['valore'], 1)}% (GIE AGSI+, {dl('scorte.json')}). "
      f"For the IEA, {EXTERNAL['iea_storage']['text']} ({link('IEA, 3 November 2026', EXTERNAL['iea_storage']['link'])}).")
    A("Italy's physical position is better than northern Europe's: full storage, two large pipelines from the south and five LNG terminals. Its weak points are the price, "
      "which follows the Dutch TTF, and the oil stocks, which were drawn down in spring and have not been rebuilt. A cold winter would test Germany and Austria first; Italy "
      "would feel it through the price.")
    # ------------------------------------------------------------------ 3
    H2("pump", "3. At the pump and in the bill")
    H3("Diesel and petrol")
    P(f"On {date_en(lastd)} a litre of diesel cost **€{num(g['eur_l'], 3)}** on average: €{num(g['netto'], 3)} for the fuel itself, €{num(g['accisa'], 4)} of excise and "
      f"€{num(g['iva'], 4)} of VAT. Petrol cost **€{num(b['eur_l'], 3)}** (net €{num(b['netto'], 3)}, excise €{num(b['accisa'], 4)}) (MASE weekly national average, {dl('italia-impatti.json')}). "
      f"The MASE average mixes self-service and attended pumps.")
    P(f"That survey still included the last diesel excise cut, {num(V['cut_cents_vat'], 1)} cents a litre with VAT, in force from 28 October to 7 November and not renewed "
      f"({link('Rai News, 8 November 2026', V['measures']['accise-marzo-2026']['link2'])}). With the ordinary excise of €{num(V['ordinary'], 4)} and an unchanged net price, diesel "
      f"comes to **€{num(V['dsl_post'], 3)}** (calculation, mixed self-service and attended). The daily readings after the expiry show a much smaller rise: {EXTERNAL['mimit_9nov']['text']} "
      f"({link('ANSA', EXTERNAL['mimit_9nov']['link'])}; Rai News). The ministry credits the voluntary price caps: since 28 September Eni/Enilive and IP have capped prices at about 4,100 of "
      f"20,000 stations (diesel €2.19, petrol €1.99; {link('La Prealpina, 28 September 2026', V['measures']['tetto-eni-ip-2026']['link'])}), and by 9 November, according to the ministry, "
      f"the main companies had joined, keeping self-service diesel below €2.20 on most of the network. *Assessment:* the €{num(V['dsl_post'], 2)} estimate is an upper bound while the caps last.")
    need(V["measures"]["tetto-eni-ip-2026"]["testo"], "4.100", "2,19", "1,99", where="misure_governo tetto-eni-ip-2026")
    FIG("pump", f"*Weekly national average pump prices, €/litre, {month_en(V['dsl_first'])} to {date_en(lastd)}. Dashed lines: the monitor's diesel alert levels "
                f"(€{num(lo, 2)} and €{num(hi, 2)}; an assessment). Events: 1 = excise cut of 25 cents (30.5 with VAT), 22 March 2022; 2 = cut fully withdrawn, 1 January 2023; "
                f"3 = war on Iran begins, 28 February 2026, followed by an excise cut of 20 cents (24.4 with VAT) in the MASE survey of 23 March; 4 = Eni/IP price caps, 28 September 2026. "
                f"Source: MASE, DGSAIE weekly prices, {dl('italia-impatti.json')}, data to {date_en(lastd)}.*")
    mx = V["dsl_max"]
    P(f"In the last week before the war ({date_en(V['pre'])}) diesel cost €{num(V['pre_d'], 3)} and petrol €{num(V['pre_p'], 3)}. Diesel peaked at **€{num(mx[1], 3)}** in the week of "
      f"{date_en(mx[0])}, the highest weekly average in the file's series (which starts in {month_en(V['dsl_first'])}). Since February the net price of diesel has risen "
      f"{pct(V['net_var'], 0, False)}, while Brent crude in euro rose {pct(V['brent_eur_var_close'], 0, False)} (from a pre-war weekly average of {num(V['base_n']['brent'], 2)} to the "
      f"9 November close of {num(V['brent_close'], 2)} dollars a barrel; calculation on {dl('italia-impatti.json')} and Yahoo Finance).")
    cs_ = ii["serie"]["carburanti_settimanali"]
    gap_now = (at(cs_["gasolio"], lastd) - at(cs_["benzina"], lastd)) * 100
    gapn_now = (at(cs_["gasolio_netto"], lastd) - at(cs_["benzina_netto"], lastd)) * 100
    gapn_pre = (at(cs_["gasolio_netto"], V["pre"]) - at(cs_["benzina_netto"], V["pre"])) * 100
    P(f"Since January 2026 diesel and petrol carry the same ordinary excise (€{num(V['ordinary'], 4)}). On {date_en(lastd, False)} diesel cost {num(gap_now, 1)} cents more than petrol, "
      f"against {num(V['gap_pre'], 1)} cents before the war, even though its excise was {num((V['ordinary'] - g['accisa']) * 100, 0)} cents lower that week. Before tax the gap is "
      f"{num(gapn_now, 1)} cents, against {num(gapn_pre, 1)} before the war (calculation).")
    A("diesel has risen about twice as fast as crude because the refining margin on diesel widened: Europe imports diesel, and part of it came from Gulf refineries. "
      "That is why haulage, which runs on diesel, is under more pressure than private motoring.")
    FIG("breakdown", f"*Diesel price per litre split into net price, excise and VAT, for the last pre-war week, the April and September peaks, the latest survey ({date_en(lastd)}) and the "
                     f"estimate after the cut expired (net price unchanged, ordinary excise, VAT 22%; calculation). Source: MASE, {dl('italia-impatti.json')}.*")
    ex = [c for c in ii["accise"]["cambi"] if c["data_rilevazione"] >= "2026-01-01"]
    prod = {"benzina": "petrol", "gasolio": "diesel"}
    TAB(["MASE survey", "Fuel", "Excise from → to, €/l", "Change with VAT, cents"],
        [[date_en(c["data_rilevazione"]), prod[c["prodotto"]], f"{num(c['da_eur_l'], 4)} → {num(c['a_eur_l'], 4)}", pts(c["variazione_cent_con_iva"], 1)] for c in ex],
        f"Excise changes in 2026 as recorded in the MASE weekly series (field ACCISA), {dl('italia-impatti.json')}. Dates are the Monday surveys that first show the change, "
        f"not the legal start dates. In 2022 the cut was 25 cents (30.5 with VAT) from 22 March, reduced to 15 in December and ended on 1 January 2023.")
    r = R
    P(f"**How crude reaches the pump.** At constant refining margins, 10 dollars a barrel on Brent is worth {num(r['brent_pompa_teorico']['cent_l_per_10_usd_bbl'], 1)} cents a litre with VAT "
      f"(at {num(V['base_t']['eurusd'], 4)} dollars per euro). Estimated on the Italian data, the net price of diesel moves {num(est['gasolio']['diff_4_sett']['b'], 2)} times the change "
      f"in Brent after 4 weeks, {num(est['gasolio']['diff_8_sett']['b'], 2)} after 8 and {num(est['gasolio']['livello']['b'], 2)} in the long run; for petrol "
      f"{num(est['benzina']['diff_4_sett']['b'], 2)}, {num(est['benzina']['diff_8_sett']['b'], 2)} and {num(est['benzina']['livello']['b'], 2)}. About 35% of the long-run effect on diesel "
      f"passes in one week, 74% in four. Excise cuts pass faster but unevenly: in the first three days of the March 2026 cut only 60% of stations applied it "
      f"({link('Mimit observatory via Today.it', lit['accise-applicazione-2026']['link'])}). These are the monitor's regressions (fit R² {num(est['gasolio']['diff_4_sett']['r2'], 2)} at 4 weeks), "
      f"reliability medium.")
    need(r["ritardo"]["testo"], "35%", "74%", where="regole ritardo")
    need(lit["accise-applicazione-2026"]["testo"], "60%", where="letteratura accise-applicazione-2026")
    H3("Electricity: the PUN")
    py = V["pun_y"]
    P(f"The PUN averaged **{num(V['pun_oct'][1], 2)} €/MWh** in October 2026 and {num(V['pun_nov'][1], 2)} in the first {V['pun_days_nov']} days of November "
      f"({num(V['pun_day'][1], 2)} on {date_en(V['pun_day'][0], False)}). Annual averages were {num(py['2022'], 1)} in 2022, {num(py['2023'], 1)} in 2023, "
      f"{num(py['2024'], 1)} in 2024 and {num(py['2025'], 1)} in 2025 (GME, {dl('italia-impatti.json')}). Gas sets the power price in most hours: on 18 monthly and annual "
      f"points the monitor fits PUN ≈ {num(V['pun_ttf']['a'], 1)} + {num(V['pun_ttf']['b'], 2)} × TTF (R² {num(V['pun_ttf']['r2'], 2)}), so 10 €/MWh on gas adds about 20 on power. "
      f"With October's TTF of {num(V['oct_ttf'], 1)} the formula gives {num(V['pun_fit_oct'], 0)}, against an actual {num(V['pun_oct'][1], 0)}.")
    FIG("pun", f"*Monthly average PUN, €/MWh, {month_en(V['pun_m'][0][0])} to {month_en(V['pun_m'][-1][0])} ({month_en(V['pun_nov'][0], False)} partial, {V['pun_days_nov']} days). "
               f"Dashed lines: annual averages of 2022 and 2025. Source: GME, {dl('italia-impatti.json')}, read on {date_en(V['pun_day'][0])}.*")
    H3("Regulated gas")
    a = V["arera"]
    cm = {k: v for k, v in V["cmem"]}
    P(f"For 'vulnerable' households (the elderly, the disabled, people on social bonuses and others still on regulated terms) ARERA sets the gas cost as the monthly average of "
      f"the Italian wholesale price, so wholesale changes reach the bill in full a month later. The October 2026 value was **{num(a['cmem_eur_mwh'], 2)} €/MWh**, against "
      f"{num(cm.get('2026-04'), 2)} in April and {num(cm.get('2026-05'), 2)} in May; the typical customer's bill rose {num(a['var_spesa_utente_tipo_pct'], 1)}% on September "
      f"({link('ARERA, 3 November 2026', a['link'])}), and the reference price was {num(a['prezzo_riferimento_cliente_tipo_cent_smc'], 2)} cents per cubic metre "
      f"(Sky TG24, not reachable from here). About 2.3 million households are still on this service (ARERA). Rule of thumb: 10 €/MWh on wholesale gas adds 10.6 cents per cubic metre plus VAT, about 7% of the bill. **Missing:** the June and August values.")
    need(R["ttf_gas_vulnerabili"]["testo"], "10.6", where="regole ttf_gas_vulnerabili")
    db = V["measures"]["decreto-bollette-2026"]
    need(db["testo"], "15 euro", "30 euro", where="misure_governo decreto-bollette-2026")
    P(f"On 9 November the cabinet approved a decree on energy bills: {EXTERNAL['bill_decree']['text']} ({link('ANSA', db['link'])}; {link('Corriere della Sera', db['link2'])}). "
      f"It applies to customers on variable-price power contracts, almost 18 million according to the Corriere. **Missing:** the published text of the decree and an official estimate "
      f"of the saving per household.")
    # ------------------------------------------------------------------ 4
    H2("households", "4. Inflation and households")
    nl = V["nic_last"]
    ph = V["nic_prev_hi"]
    P(f"Istat's preliminary estimate puts consumer price inflation (NIC) at **{num(nl[1], 1)}%** in {month_en(nl[0])}, the highest since {month_en(ph[0])} ({num(ph[1], 1)}%); "
      f"the 2022 peak was {num(V['nic_max'][1], 1)}% in {month_en(V['nic_max'][0])}. The EU-harmonised index (HICP) was {num(V['hicp_last'][1], 1)}% "
      f"(Istat and Eurostat, {dl('italia-impatti.json')}). Energy items rose {num(nic['energetici'][-1][1], 1)}%: regulated energy {num(nic['energetici_regolamentati'][-1][1], 1)}% "
      f"(from {num(nic['energetici_regolamentati'][-2][1], 1)}% in September), electricity {num(nic['elettricita'][-1][1], 1)}%, gas {num(nic['gas'][-1][1], 1)}%, fuels "
      f"{num(nic['carburanti'][-1][1], 1)}%. Food rose {num(nic['alimentari'][-1][1], 1)}% and core inflation (excluding energy and fresh food) {num(nic['componente_di_fondo'][-1][1], 1)}%.")
    FIG("infl", f"*Consumer prices, Istat NIC, % change on the same month a year earlier, January–{month_en(nl[0])} (latest month preliminary). Event 1 = war on Iran begins, "
                f"28 February 2026. Source: Istat, dataflow 167_745, {dl('italia-impatti.json')}.*")
    W = V["W"]
    P(f"Energy weighs {num(W['NRG'] / 10, 1)}% of the 2026 HICP basket (fuels {num(W['FUEL'] / 10, 1)}%, electricity {num(W['CP0451'] / 10, 1)}%, gas {num(W['CP0452'] / 10, 1)}%) "
      f"and food {num(W['FOOD'] / 10, 1)}% (Eurostat). A 10% rise in consumer energy prices therefore adds about 1.1 points of inflation directly. Weight times annual rate gives "
      f"energy about {num(V['energy_contrib'], 1)} of the {num(V['hicp_last'][1], 1)} points of HICP inflation in October: electricity and gas about "
      f"{num((W['CP0451'] * nic['elettricita'][-1][1] + W['CP0452'] * nic['gas'][-1][1]) / 1000, 1)}, fuels about {num(W['FUEL'] * nic['carburanti'][-1][1] / 1000, 1)} "
      f"(weights × NIC annual rates; approximation, calculation).")
    A("more than half of Italian inflation is the direct effect of energy. Indirect effects (transport, food) come later; food inflation has started to rise "
      f"({num(nic['alimentari'][-3][1], 1)}% in August, {num(nic['alimentari'][-1][1], 1)}% in October) and freight transport services in the HICP rose "
      f"{num(V['hicp']['trasporto_merci'][-1][1], 1)}% in {month_en(V['hicp']['trasporto_merci'][-1][0])}.")
    cf = V["conf"]
    P(f"Consumer confidence (Istat, 2021 = 100) was **{num(cf['clima'][-1][1], 1)}** in {month_en(cf['clima'][-1][0])}, against {num(at(cf['clima'], '2026-02'), 1)} in February; "
      f"the judgement on the economy fell to {num(cf['clima_economico'][-1][1], 1)}, close to April's {num(at(cf['clima_economico'], '2026-04'), 1)}. The low of 2022 was "
      f"{num(V['conf_min'][1], 1)} ({month_en(V['conf_min'][0])}). The file holds the series not adjusted for season; Istat's press release uses the adjusted one, which can differ.")
    sm = V["sales_may"]
    P(f"**Fuel sales.** Road diesel sales fell {pct(-sales['gasolio_motori']['var_pct'], 1, False)} in {month_en(sales['mese'])} on a year earlier and diesel sold off the retail network "
      f"(to fleets and hauliers) {pct(-sales['gasolio_extrarete']['var_pct'], 1, False)}; in May the falls were {pct(-sm['gasolio_motori']['var_pct'], 1, False)} and {pct(-sm['gasolio_extrarete']['var_pct'], 1, False)}. "
      f"Petrol sales rose {pct(sales['benzina']['var_pct'], 1, False)} (MASE, {dl('italia-impatti.json')}). Diesel was already falling and petrol rising in January and February, before the war.")
    FIG("sales", f"*Fuel sales by month, % on the same month a year earlier, January–{month_en(sales['mese'])}: road diesel, off-network diesel (fleets, hauliers) and petrol. "
                 f"Event 1 = first full month of the war (March 2026). Source: MASE, DGSAIE, petroleum consumption (provisional), {dl('italia-impatti.json')}.*")
    el = lit["elasticita-benzina"]
    A(f"three things are mixed in the diesel figures: a long shift of the car fleet from diesel to petrol and hybrids (visible before the war), weaker economic activity, "
      f"and genuine saving. The literature puts the short-run price elasticity of petrol demand at {num(el['valore_breve'], 2)} "
      f"({link('Havranek, Irsova and Janda, 2012', el['link'])}): a 10% price rise cuts consumption by about 1%. Off-network diesel, the hauliers' fuel, falling faster than road "
      "diesel points to less freight moved.")
    ecb = lit["bce-pil-petrolio"]
    P(f"The IMF expects Italian growth of {num(pa['crescita_pil_previsione']['valore'], 1)}% and average inflation of {num(pa['inflazione_previsione']['valore'], 1)}% in 2026 "
      f"(World Economic Outlook, October 2026, {dl('paesi.json')}). For the ECB, a geopolitical supply shock that raises the real oil price by 10% lowers euro-area growth by about "
      f"0.2–0.3 points in each of the first three years ({link('ECB Economic Bulletin 4/2026', ecb['link'])}).")
    need(ecb["testo"], "0,2-0,3", where="letteratura bce-pil-petrolio")
    P("**Queues and empty shelves.** In 2026 the queues and 'sold out' signs at filling stations came from price changes, not shortages: after the March excise cut, drivers rushed "
      "to the stations that had applied it; on 28 September they rushed to the Eni and IP stations with capped prices (sources in the precedents of "
      f"{dl('italia-impatti.json')}). Food hoarding is documented only when trucks stopped: Sicily in January 2012 (water, milk) and March 2022 (pasta, flour, oil, sugar, rice).")
    # ------------------------------------------------------------------ 5
    H2("haulage", "5. Road haulage and the risk of a stoppage")
    pw = hau["peso_gasolio_sui_costi"]
    need(pw[0]["testo"], "20,9%", "22,1%", "24,4%", where="autotrasporto peso_gasolio_sui_costi")
    need(pw[1]["testo"], "4,2%", where="autotrasporto peso_gasolio CNR comunicato")
    exvat_pre, exvat_now = V["pre_d"] / 1.22, V["dsl_post"] / 1.22
    dv = var(exvat_now, exvat_pre)
    V["haul_cost"] = dv * pw[0]["valore_pct"] / 100
    rr = EXTERNAL["excise_refund"]["rate"]
    ref_pre, ref_now = V["pre_net"] + rr, g["netto"] + rr
    dvr = var(ref_now, ref_pre)
    V["haul_cost_ref"] = dvr * pw[0]["valore_pct"] / 100
    H3("How much diesel weighs")
    P(f"There is no up-to-date official Italian figure for the share of diesel in a haulier's costs (the association Federtrasporti noted the gap in September). The closest reference "
      f"is French: diesel is **{num(pw[0]['valore_pct'], 1)}%** of the cost of a long-haul articulated truck in 2026, after 22.1% in 2025 and 24.4% in 2024 "
      f"(Comité national routier, {link('CNR', pw[0]['link'])}; reliability medium: read from a research summary, the PDF is blocked from this environment and was not verified). The CNR estimated that the March 2026 rise alone added 4.2% "
      f"to the total cost ({link('CNR, 27 March 2026', pw[1]['link'])}). Excluding VAT, which firms recover, diesel has gone from €{num(exvat_pre, 3)} to about €{num(exvat_now, 3)} "
      f"a litre since February ({pct(dv, 0)}); with the French weight that is roughly **{pct(V['haul_cost'], 0)} on total cost**. For a truck that gets the excise refund "
      f"the litre has gone from €{num(ref_pre, 3)} to €{num(ref_now, 3)} net of tax and refund ({pct(dvr, 0)}), about **{pct(V['haul_cost_ref'], 0)}** on total cost "
      f"(calculation; the refund makes the percentage rise larger, because the excise it leaves is fixed).")
    cna = [x for x in hau["associazioni"] if x["nome"] == "CNA Fita"][0]
    d1 = [x for x in hau["dichiarazioni_2026"] if x["data"] == "2026-04-17"][0]
    need(pw[2]["testo"], "100 euro", "2.000 euro", where="peso_gasolio CNA Fermo")
    need(d1["testo"], "40 centesimi", "9.000 euro", where="dichiarazioni Unatras 17/4")
    P(f"The associations' own figures: about €100 a day and €2,000 a month more for a firm with one heavy truck (CNA Fermo, {link('Logisticamente.it, October 2026', pw[2]['link'])}); "
      f"up to 40 cents a litre of extra burden and an average loss of about €9,000 a month per firm (Unatras, {link('Il Fatto Quotidiano, 17 April 2026', d1['link'])}). "
      f"These are claims by parties to the dispute.")
    H3("The excise refund, and why tax cuts annoyed hauliers")
    mr = hau["meccanismo_rimborso_accise"]
    need(mr["testo"], "26,5", where="meccanismo_rimborso_accise")
    d2 = [x for x in hau["dichiarazioni_2026"] if x["data"] == "2026-05-23"][0]
    P(f"Hauliers with heavy trucks get back part of the excise on diesel: {EXTERNAL['excise_refund']['text']}. At the ordinary excise that is "
      f"{num((V['ordinary'] - rr) * 100, 1)} cents a litre (26.5 according to Federtrasporti). Because the haulier's own excise is fixed at the reference rate, a general cut "
      f"shrinks the refund by the same amount, as long as the cut is smaller than the refundable part. In April Unatras put about 20 of its 40 cents of extra burden down to "
      f"this lost refund and asked for compensation of 200 euros per 1,000 litres ({link('Il Fatto Quotidiano, 17 April 2026', d1['link'])}); in May it called the general cut "
      f"'a wrong decision that shifted the 20-cent reduction onto haulage firms' ({link('Shipping Italy, 23 May 2026', d2['link'])}). It was one of the two grievances behind the "
      f"stoppage called for 25–29 May; the other was clients' pressure on rates.")
    cr = V["measures"]["credito-autotrasporto-2026"]
    need(cr["testo"], "242,2", "480", "300 milioni", where="misure credito-autotrasporto-2026")
    d4 = [x for x in hau["dichiarazioni_2026"] if x["data"] == "2026-10-21"][0]
    need(d4["testo"], "434", where="dichiarazioni Unatras 21/10")
    P(f"The government suspended that stoppage on 22 May with a package: a tax credit on diesel of 300 million euros (200 of them new), the quarterly excise refund paid in "
      f"30 days instead of 60, a two-week extension of the excise cut to 6 June, and a standing table with the sector. By November 242.2 million of the 480 million allocated had been "
      f"granted, to be used by 31 December 2026 (Ministry of Transport via {link('TrasportoEuropa', [x for x in hau['dichiarazioni_2026'] if x['data'] == '2026-11-09'][0]['link'])}, 9 November). "
      f"On 21 October Unatras said firms had not yet received the credit and put the funds allocated at 434 million ({link('Logisticamente.it', d4['link'])}). Both figures are "
      f"allocations: the sources do not explain the 46-million difference (a later top-up is possible but not documented).")
    A("for a truck that qualifies for the refund, a general excise cut of up to about 27 cents is worth nothing in final cost: the price at the pump falls, the refund falls with it "
      "(VAT is recovered anyway). It only reduces the cash the firm advances until the quarterly refund. By the same logic the expiry of the cut on 8 November raises motorists' costs, "
      "not hauliers' final costs. The grievances that move hauliers are the tax credit, which must be used by 31 December, and clients' pressure on rates, not the expiry itself.")
    H3("The rules on stoppages")
    rl = {x["id"]: x for x in hau["regole_scioperi"]}
    need(rl["preavviso-25-giorni"]["testo"], "25 giorni", "10", where="regole_scioperi preavviso")
    P(f"Law 146 of 1990, amended in 2000, governs strikes in essential public services: notice, duration, minimum services, conciliation. The Strike Guarantee Commission reviews "
      f"each call, can ask for it to be withdrawn and can refer it for a *precettazione*, an order by the minister or the prefect that requires the service to run "
      f"({link('Normattiva', rl['legge-146-1990']['link'])}). For haulage stoppages the sector's self-regulation code requires **{V['notice_days']} days' notice** to the Commission "
      f"(the law sets a minimum of 10) and minimum services; a rule of 'objective spacing' forbids stoppages in the same sector too close together. In March 2022 and April 2026 "
      f"the Commission challenged stoppages called with less than 25 days' notice (Trasportounito gave 20 days in April 2026, according to Unatras; "
      f"{link('LaPresse, 20 April 2026', rl['preavviso-25-giorni']['link'])}). The one national stoppage called with proper notice in 2026 (Unatras, 25–29 May, later suspended) "
      f"was for five days; the maximum duration allowed by the code is **not verified** (the Commission's site was not reachable from this environment).")
    H3("Precedents: what triggered past protests")
    rows = []
    for p in V["prec"]:
        if p["id"] not in PREC_EN:
            continue
        gd = p["gasolio_alla_data"]
        a_, b_ = d(p["data_inizio"]), d(p["data_fine"]) if p.get("data_fine") else None
        if not b_ or b_ == a_:
            when = date_en(p["data_inizio"])
        elif a_.month == b_.month:
            when = f"{a_.day}–{b_.day} {MONTHS[b_.month - 1]} {b_.year}"
        else:
            when = f"{date_en(p['data_inizio'], False)} – {date_en(p['data_fine'])}"
        rows.append([when, PREC_EN[p["id"]][0], f"€{num(gd['eur_l'], 3)}", pct(gd["var_pct_un_anno"]), pct(p["_8w"]) if p["_8w"] is not None else "—",
                     link(p["fonte"].split(",")[0], p["link"])])
    TAB(["When", "What", "Diesel that week", "On a year", "In 8 weeks", "Source"], rows,
        f"Diesel: MASE weekly national average in the week the protest began ({dl('italia-impatti.json')}); the 8-week change is computed only where the weekly series in the file "
        f"covers it (from {month_en(V['dsl_first'])}); a weekend start counts from the next Monday. Weeks before 2022 come from the MASE weekly file ({link('MASE', EXTERNAL['mase_diesel_pre2022']['link'])}). "
        f"Sources are news reports (reliability medium, LaPresse and Shipping Italy high).")
    FIG("protests", f"*Diesel price in the week each protest began, €/litre, with the change on a year earlier in brackets; 'today' is the MASE survey of {date_en(lastd)}. "
                    f"Dashed lines: the monitor's alert levels €{num(lo, 2)} and €{num(hi, 2)}. The 2024 tractor protest was about farm income tax and EU farm policy, "
                    f"not fuel. Source: MASE weekly prices, curated precedents in {dl('italia-impatti.json')}.*")
    P("What happened: in December 2007 the stoppage lasted three days, with milk, medicines and petrol guaranteed from 12 December; in January 2012 the Forconi blockades left most of "
      "Sicily's filling stations dry by the fourth day, and about 60 pickets then blocked motorway toll gates across Italy; in March 2022 a stoppage was blocked by the Commission "
      "for lack of notice, and the excise cut followed on 22 March; in April 2026 Trasportounito's stoppage was suspended on its first day after a truck driver was killed on the "
      "A1 motorway; in May Unatras's was suspended after the government package; in October regional stoppages ran in Sicily and Calabria (16–20 October, in the ministry's strike calendar) after protests and blockades that began in Puglia.")
    sf = ii["soglie_fermo"]
    yy = [p["gasolio_alla_data"]["var_pct_un_anno"] for p in V["prec"] if p["id"] in PREC_EN and p["id"] != "trattori-2024"]
    tp = V["thr_pct"]
    A(f"the monitor's thresholds, built on these precedents, rate the risk **low** with diesel below €{num(lo, 2)} and an 8-week rise below {tp[0]}%, **medium** between "
      f"€{num(lo, 2)} and €{num(hi, 2)} or a rise of {tp[0]}–{tp[1]}%, and **high** from €{num(hi, 2)} or a rise above {tp[1]}%. Protests started at or near a new price peak and, "
      f"in every haulage case, with diesel {num(min(yy), 0)}–{num(max(yy), 0)}% above a year earlier. The November supply-chain report uses €1.90 and €2.20; the upper level here is lower because March 2022 "
      f"and April 2026 started below €2.20.")
    H3("Where things stand")
    sp = V["strikes"]
    need(sp["autotrasporto"], "9 novembre", where="scioperi_proclamati autotrasporto")
    gen = [x for x in sp["elementi"] if x["ambito"] == "nazionale"]
    P(f"**No national haulage stoppage had been called** in the sources consulted on 9 November (Rai News list of 8 November; the Ministry of Transport's strike calendar was "
      f"not reachable from this environment). Unatras raised the possibility in October, and a meeting at the ministry was set for 27 October; its outcome was not found. "
      f"Other national actions this month: a general strike by the CGIL union on {date_en(gen[0]['data_inizio'], False)} and rail strikes, including freight, from 21:00 on "
      f"20 November to 20:00 on 21 November ({link('Rai News, 8 November 2026', sp['link'])}). With {V['notice_days']} days' notice, a stoppage called on "
      f"{date_en(today.isoformat(), False)} could not start before **{date_en(V['earliest'])}**.")
    P(f"Against the thresholds: diesel at €{num(g['eur_l'], 3)} (about €{num(V['dsl_post'], 2)} after the expiry) is in the high band, where it has been since the week of "
      f"{date_en(V['above_since'])}; the 8-week change is {pct(V['dsl_8w_var'])} (from €{num(V['dsl_8w'][1], 3)} on {date_en(V['dsl_8w'][0], False)}), in the low band; the change on a "
      f"year is {pct(V['dsl_yoy'])}, inside the range of past protests.")
    A(f"the level of diesel alone has not been enough: it has been above €{num(hi, 2)} for more than two months without a national call. The 2026 calls came from a policy "
      f"grievance on top of the price (the refund cut in May, unpaid credits in October). The risk that a national stoppage is **called** before the end of the year is rated "
      f"**high**; a lawful stoppage before {date_en(V['earliest'], False)} is ruled out by the notice rule. Wildcat blockades, like Sicily in 2012 or the protests in Puglia in October 2026, need "
      f"no notice and remain possible at any time. Signals that would raise the risk: a filing with the Commission; credits not usable by 31 December; a new general excise "
      f"cut without compensation for hauliers; diesel up more than {tp[0]}% in 8 weeks. Signals that would lower it: the credit extended into 2027, or an automatic fuel surcharge on "
      f"haulage rates, which Federtrasporti has proposed.")
    # ------------------------------------------------------------------ 6
    H2("ports", "6. Ports and freight")
    PP = V["ports"]
    pmap = {p["name"]: p for p in PP}
    P(f"From 1 January to {date_en(V['pw_last'])} the busiest Italian ports in the PortWatch sample had about the same number of ship calls as a year earlier: Genoa "
      f"{pct(pmap['Genoa']['ytd'])}, Trieste {pct(pmap['Trieste']['ytd'])}, Gioia Tauro {pct(pmap['Gioia Tauro']['ytd'])} (calls per day, same days of 2025; IMF PortWatch, "
      f"{dl('portwatch.json')}). The largest falls are in the northern Adriatic: Ravenna {pct(pmap['Ravenna']['ytd'])} for the year and {pct(pmap['Ravenna']['var30'])} in the last "
      f"30 days, Venice (Lido) {pct(pmap['Venice (Lido)']['ytd'])} and {pct(pmap['Venice (Lido)']['var30'])}. La Spezia is up, {pct(pmap['La Spezia']['ytd'])} for the year.")
    FIG("ports", f"*Ship calls per day, change on the same days of 2025, %: 1 January to {date_en(V['pw_last'])} and the last 30 days. Ports ordered by calls per day this year. "
                 f"PortWatch counts only ships with AIS switched on; data arrive about a week late. Source: IMF PortWatch, {dl('portwatch.json')}, data to {date_en(V['pw_last'])}.*")
    rv = pmap["Ravenna"]
    P(f"The numbers are small: Ravenna had {num(rv['m30']['portcalls'], 1)} calls a day in the last 30 days against {num(rv['m30p']['portcalls'], 1)} a year earlier, with tankers "
      f"at {num(rv['m30']['portcalls_tanker'], 1)} against {num(rv['m30p']['portcalls_tanker'], 1)}. Weekly figures swing widely; the year-to-date figure is the one to lead with.")
    H3("Transit times and costs to Genoa and Trieste")
    Rt = V["routes"]
    sg, stt, sr = Rt[("shanghai", "genoa")], Rt[("shanghai", "trieste")], Rt[("shanghai", "rotterdam")]
    wci = V["wci"]
    fbx13 = V["fbx"]["rotte"]["FBX13"]
    P(f"A 15,000-TEU container ship from Shanghai takes **{num(sg['days_base'], 1)} days** to Genoa via Suez and {num(sg['cape']['days'], 1)} via the Cape of Good Hope "
      f"({num(sg['cape']['extra_days_vs_base'], 1)} more); to Trieste {num(stt['days_base'], 1)} and {num(stt['cape']['days'], 1)} ({num(stt['cape']['extra_days_vs_base'], 1)} more). "
      f"Northern Europe gains less from Suez: Shanghai–Rotterdam is {num(sr['days_base'], 1)} days against {num(sr['cape']['days'], 1)}. With {sg['red_sea_share_pct']}% of "
      f"Far East–Europe capacity back on Suez services in October, the weighted average is {num(sg['days_today_weighted'], 1)} days to Genoa and "
      f"{num(stt['days_today_weighted'], 1)} to Trieste (model in {dl('transit-times.json')}: sea days at a fixed speed, no port time).")
    FIG("transit", f"*Days at sea from Asian ports, via Suez, via the Cape and today's mix ({sg['red_sea_share_pct']}% of capacity via Suez). Model: Benden shipping lanes, fixed speed "
                   f"per ship type, no waiting or port time. Source: {dl('transit-times.json')}, updated {date_en(V['tt']['updated'][:10])}.*")
    wr = sg["war_risk_items"][0]
    P(f"Spot freight from Shanghai to Genoa was **{num(wci['rotte']['Shanghai-Genoa'], 0)} dollars per FEU** on {date_en(wci['data'])}, against "
      f"{num(wci['rotte']['Shanghai-Rotterdam'], 0)} to Rotterdam (Drewry WCI, {dl('noli.json')}); the Freightos China–Mediterranean index was {num(fbx13['valore'], 0)} "
      f"on {date_en(V['fbx']['data'], False)} ({fbx13['var'].replace('-', '−')} on the week). The Red Sea war-risk premium, about {num(wr['pct_hull'], 2)}% of hull value per voyage (Reuters via Insurance Journal), "
      f"adds {num(sg['cost_breakdown_usd']['war_risk_extra'], 0)} dollars to a Suez voyage compared with before the war; with dearer bunker fuel the model puts the extra cost at "
      f"about {num(sg['extra_cost_per_unit_incl_price_effect'], 0)} dollars per FEU to Genoa.")
    rl_ = Rt[("ras_laffan", "genoa")] if ("ras_laffan", "genoa") in Rt else None
    yb = Rt.get(("yanbu", "genoa"))
    if rl_ and yb:
        P(f"For energy cargoes the routes have changed more. The model treats LNG from Ras Laffan as **blocked**: Qatar has no export terminal outside the Gulf, and the "
          f"few cargoes still leaving (1.6 million tonnes in September, Kpler via Reuters) cross Hormuz under war risk. Saudi crude is piped to Yanbu on the "
          f"Red Sea and reaches Genoa in {num(yb['days_base'], 1)} days via Suez, inside the war-risk area. LNG from the US Gulf (Sabine Pass) takes "
          f"{num(Rt[('sabine_pass', 'genoa')]['days_base'], 1) if ('sabine_pass', 'genoa') in Rt else 'n/a'} days to Genoa ({dl('transit-times.json')}).")
    H3("La Spezia's exposure")
    ls = [p for p in V["pr_it"] if p["id"] == "la-spezia"][0]
    nxt = [p for p in V["pr_it"] if p["id"] != "la-spezia"][0]
    pan = sh["panigaglia"]
    ind = {i["group"] + ":" + i["name"][:20]: i for i in ls["indicators"]}
    cont = [i for i in ls["indicators"] if i["name"].startswith("Port calls")][0]
    P(f"In the monitor's Port Risk Index La Spezia scores **{num(ls['score'], 1)} out of 25 ({ls['level']})**, rank {ls['rank']} of {V['pr_n']} ports and the highest in Italy "
      f"(next is {nxt['name']} at {num(nxt['score'], 1)}) ({dl('port-risk.json')}, {date_en(V['pr']['reference_date'])}). The score is probability {num(ls['probability'], 1)} of 5 times "
      f"impact {num(ls['impact'], 1)} of 5. Impact is high because the index counts three strategic roles (the Panigaglia LNG terminal, a container gateway, the naval base). "
      f"Probability comes almost entirely from a rule that gives the port a primary dependency on Qatari LNG and on the Red Sea container route, not from its traffic, which is "
      f"rising: {cont['text'].split(':')[0]} over 28 days ({cont['text'].split(': ')[-1]}).")
    A(f"the index describes a structural exposure rather than a current disruption. Panigaglia is a small terminal: it delivered {num(pan['twh_12m'], 1)} TWh in 12 months, "
      f"{num(pan['quota_ingressi_pct'], 1)}% of gas entering Italy (ENTSOG). The Qatar dependency is a rule that applies Italy's national share of LNG from the Gulf (32.6% by value in 2025) "
      f"to every Italian LNG port; it is not an observed flow, since the repository does not show where Panigaglia's cargoes come from. La Spezia's score would fall mainly if the "
      f"Qatari LNG and Red Sea scores in the risk dashboard fell; a collapse in its own calls (below half of last year's level) would raise it.")
    # ------------------------------------------------------------------ 7
    H2("scenarios", "7. Scenarios: what a new shock would do")
    A("everything in this section is the monitor's reasoning. The scenarios have no probabilities. They show what the transmission rules give when a shock of a known shape hits Italian prices, "
      "with no new government measures and excise unchanged.")
    P(f"**Method.** The changes in Brent and TTF come from the monitor's simulator: for Hormuz, the average and the peak change in the 2026 episode over 30 or 91 days; for the Red Sea, "
      f"the 2023–24 episode; for TransMed, the loss of the {num(20.86, 2)} billion cubic metres it carried in the last 12 months, net of 7.9 of spare LNG terminal capacity (low end) or with no bypass (high end). Italian prices then follow the rules of section 3 "
      f"({dl('italia-impatti.json')}, field `scenari`). There are two starting points: **pre-war prices** (week of {date_en(V['pre'])}: Brent {num(V['base_n']['brent'], 2)} dollars, "
      f"TTF {num(V['base_n']['ttf'], 2)} €/MWh, diesel €{num(V['base_n']['gasolio'], 3)}) and **today's prices** (Brent {num(V['base_t']['brent'], 1)}, TTF {num(V['base_t']['ttf'], 2)}, "
      f"diesel €{num(V['base_t']['gasolio'], 3)} after the expiry). The simulator's Brent base, {num(V['base_t']['brent'], 2)}, is an overnight price of 10 November, not the "
      f"9 November close of {num(V['brent_close'], 2)}; the difference moves the diesel results by less than half a cent. Because Hormuz is already closed in practice, the 'today' version is a *second* shock on top of the first.")
    need(sc["transmed_1m"]["ingresso"]["origine"], "20.86", where="scenari transmed origine")
    nm_ = {"hormuz_1m": "Hormuz closed, 1 month", "hormuz_3m": "Hormuz closed, 3 months", "mar_rosso_1m": "Red Sea: ships via the Cape, 1 month", "transmed_1m": "TransMed shut, 1 month"}
    rows = []
    for k, s in sc.items():
        for base, lab in [("da_condizioni_normali", "pre-war"), ("da_oggi", "today")]:
            x = s[base]
            gv = x["gas_vulnerabili_spesa_pct"]
            gas = (f"{pct(gv[0], 0)} to {pct(gv[1], 0)} of the bill" if gv[0] is not None and gv[1] else
                   (f"+{num(x['gas_vulnerabili_aumento_cent_smc'][0], 0)} to +{num(x['gas_vulnerabili_aumento_cent_smc'][1], 0)} c/m³" if x["gas_vulnerabili_aumento_cent_smc"][1] else "unchanged"))
            rng = lambda a, dec=2: f"{num(a[0], dec)}–{num(a[1], dec)}" if a[0] != a[1] else num(a[0], dec)
            inf = x["inflazione_effetto_diretto_punti"]
            infs = f"+{num(inf[0], 1)}" if num(inf[0], 1) == num(inf[1], 1) else f"+{num(inf[0], 1)} to +{num(inf[1], 1)}"
            rows.append([nm_[k] if base == "da_condizioni_normali" else "", lab, rng(x["gasolio_eur_l"]), rng(x["benzina_eur_l"]), rng(x["pun_eur_mwh"], 0), gas,
                         infs, LEVEL.get(x["rischio_fermo_tir"], x["rischio_fermo_tir"])])
    TAB(["Scenario", "Start", "Diesel €/l", "Petrol €/l", "PUN €/MWh", "Regulated gas", "Inflation, points (direct)", "Stoppage risk"], rows,
        f"Assessment. Ranges: average to peak of the input shock, 4-week to 8-week coefficients (1 month) or 8–13-week to long-run (3 months). Inflation: direct effect of energy only. "
        f"Stoppage risk from the monitor's thresholds; 'high' for every scenario from today because diesel is already above €{num(hi, 2)}. Source: {dl('italia-impatti.json')}.")
    FIG("scen", f"*Assessment. Diesel price ranges in each scenario, €/litre, from pre-war prices and from today's; diamonds: what diesel actually did in 2026 without the excise cuts "
                f"(average and peak over 4 weeks to 1 April and 13 weeks to 1 June). Dashed lines: alert levels €{num(lo, 2)} and €{num(hi, 2)}. Source: {dl('italia-impatti.json')}.*")
    H3("Backtest on February–March 2026")
    o1, o3 = sc["hormuz_1m"]["osservato"], sc["hormuz_3m"]["osservato"]
    n1, n3 = sc["hormuz_1m"]["da_condizioni_normali"], sc["hormuz_3m"]["da_condizioni_normali"]
    g1, g3 = o1["gasolio"], o3["gasolio"]
    P(f"Applied to the prices of {date_en(V['pre'])}, the rule gave diesel at €{num(n1['gasolio_eur_l'][0], 2)}–{num(n1['gasolio_eur_l'][1], 2)} after one month of Hormuz. "
      f"What happened (MASE, {g1['n_settimane']} weeks to {date_en(g1['fino_a'], False)}): an average of €{num(g1['media_eur_l'], 3)} and a peak of €{num(g1['max_eur_l'], 3)} "
      f"with the excise cuts, **€{num(g1['media_senza_tagli_accise'], 3)} and €{num(g1['max_senza_tagli_accise'], 3)} without them** (observed net price plus the pre-war excise, "
      f"with VAT). At three months the rule gave €{num(n3['gasolio_eur_l'][0], 2)}–{num(n3['gasolio_eur_l'][1], 2)}; without the cuts diesel averaged "
      f"€{num(g3['media_senza_tagli_accise'], 3)} and peaked at €{num(g3['max_senza_tagli_accise'], 3)} on the week of {date_en(g3['data_max'], False)}: the average falls inside the range, the peak above it.")
    i1, i3 = o1["inflazione"], o3["inflazione"]
    P(f"Inflation rose from {num(i1['prima']['nic_generale'], 1)}% in February to {num(i1['nic_generale'][0], 1)}% in March, {num(i1['nic_generale'][-1], 1)}% in {month_en(i1['mesi'][-1], False)} and "
      f"{num(i3['nic_generale'][-1], 1)}% in {month_en(i3['mesi'][-1], False)}: {pts(i1['nic_generale'][-1] - i1['prima']['nic_generale'], 1)} and "
      f"{pts(i3['nic_generale'][-1] - i3['prima']['nic_generale'], 1)} points, against a direct effect of +{num(n1['inflazione_effetto_diretto_punti'][0], 1)} to "
      f"+{num(n1['inflazione_effetto_diretto_punti'][1], 1)} (1 month) and +{num(n3['inflazione_effetto_diretto_punti'][0], 1)} to +{num(n3['inflazione_effetto_diretto_punti'][1], 1)} "
      f"(3 months) in the rule, which ignores the excise cuts. The PUN was overestimated: the rule gave {num(n1['pun_eur_mwh'][0], 0)}–{num(n1['pun_eur_mwh'][1], 0)} €/MWh, March "
      f"averaged {num(o1['pun_mensile'][0][1], 1)}.")
    orr = sc["mar_rosso_1m"]["osservato"]["gasolio"]
    P(f"For the Red Sea, the 2023–24 episode: diesel was €{num(orr['base']['eur_l'], 3)} in the week of {date_en(orr['base']['data'])} and averaged €{num(orr['media_eur_l'], 3)} "
      f"in the next {orr['n_settimane']} weeks; the small rise the rule implies did not happen.")
    A("the rule is good enough for orders of magnitude on fuel at one to three months, underestimates the peak at three months and overestimates power in spring, when solar "
      "and hydro cut the hours in which gas sets the price. Excise cuts weigh heavily on the outcome: in 2026 they took "
      f"{num((g1['media_senza_tagli_accise'] - g1['media_eur_l']) * 100, 0)}–{num((g3['media_senza_tagli_accise'] - g3['media_eur_l']) * 100, 0)} cents off the average diesel price.")
    H3("Likely government measures")
    MP = {"hormuz_1m": ["an excise cut on fuel (2022: 30.5 cents with VAT; 2026: 24.4)", "a tax credit and faster excise refunds for hauliers (2026: 300 million euros)",
                        "pressure for voluntary price caps (Eni and IP, September 2026)"],
          "hormuz_3m": ["repeated extensions of the excise cut in decreasing amounts (2026)", "tax credits for energy-intensive firms and larger social bonuses on bills (2022)",
                        "decrees on bills (November 2026: −15 €/MWh from January)", "aid to hauliers to head off a stoppage (May 2026)"],
          "mar_rosso_1m": ["no fuel measures in 2023–24", "possible support to ports"],
          "transmed_1m": ["maximum use of the LNG terminals", "tax credits for energy- and gas-intensive firms (2022)", "larger social bonuses on power and gas (2022)",
                          "a possible cut in the system charges on bills (2022)"]}
    for k, s in sc.items():
        if len(s["misure_probabili"]) != len(MP[k]):
            warn(f"misure_probabili for {k} changed: re-translate")
    UL([f"**{nm_[k]}:** " + "; ".join(MP[k]) + "." for k in sc])
    P(f"Measures are drawn from what governments did in 2022 and 2026 ({dl('italia-impatti.json')}, field `misure_governo`). *Assessment:* in the TransMed case Italy's "
      f"storage, at about {num(it['valore'], 0)}%, makes it a problem of price, not quantity, unless the winter is cold; the energy-intensive industries (paper, ceramics, glass, steel) "
      f"would be hit first. In the Hormuz cases, physical fuel shortages are unlikely in the first month thanks to emergency stocks, but queues appear wherever prices or "
      f"excise change. Shortages on shelves have come only with truck stoppages (2012, 2022).")
    H3("Indicators to watch")
    TAB(["Indicator", "Now", "Threshold that matters (assessment)", "Source"],
        [["Diesel, weekly average", f"€{num(g['eur_l'], 3)} ({date_en(lastd, False)}); ≈€{num(V['dsl_post'], 2)} after 8 Nov", f"8-week rise above {tp[0]}%", "MASE"],
         ["Stoppage filed with the Strike Commission", "none (9 Nov)", f"any filing; start ≥ {V['notice_days']} days later", "MIT, Commissione di garanzia"],
         ["Haulage tax credit used", "242.2 of 480 million granted", "deadline 31 December 2026", "Ministry of Transport"],
         ["Off-network diesel sales", f"{pct(sales['gasolio_extrarete']['var_pct'])} ({month_en(sales['mese'], False)})", "below −10% on a year", "MASE"],
         ["PUN, monthly", f"{num(V['pun_oct'][1], 1)} €/MWh (Oct)", f"above the 2022 average ({num(py['2022'], 0)})", "GME"],
         ["Regulated gas (ARERA)", f"{num(a['cmem_eur_mwh'], 2)} €/MWh (Oct)", "+10 €/MWh ≈ +7% on the bill", "ARERA"],
         ["NIC inflation", f"{num(nl[1], 1)}% ({month_en(nl[0], False)}, prelim.)", "food above 3%", "Istat"],
         ["Gas storage Italy", f"{num(it['valore'], 1)}% ({date_en(it['data'], False)})", "falling faster than last winter", "GIE AGSI+"],
         ["Mazara del Vallo flow", f"{num(m['media_7g_gwh'], 0)} GWh/day (7 days)", "below 70% of the annual average", "ENTSOG"],
         ["Hormuz tanker and LNG transits, 7 days", f"{pct(q['indicatori'][0]['valore'], 1)} on the 2025 average", "above −30% for two weeks = disruption over", "IMF PortWatch, rischio.json"]],
        "Thresholds are the monitor's assessment; the last two follow report/metodo-rischio.md.")
    cal_rows = []
    for e in sorted(V["cal"], key=lambda x: x["data"]):
        t = e.get("titolo") or ""
        if "2026-11-10" <= e["data"] <= "2026-12-31" and any(w in t for w in ("IEA Oil Market", "HICP", "OPEC+", "BCE:")):
            tt_ = t.replace("Eurozona/UE: inflazione HICP, dato definitivo", "Euro area: HICP inflation, final").replace("Eurozona: inflazione HICP, stima flash", "Euro area: HICP inflation, flash estimate") \
                   .replace("BCE: decisione di politica monetaria (con conferenza stampa)", "ECB monetary policy decision").replace("novembre", "November") \
                   .replace("OPEC+: 42a riunione ministeriale OPEC e non-OPEC (ONOMM) e 69a riunione JMMC - quote 2027", "OPEC+ ministerial meeting: 2027 quotas")
            cal_rows.append([date_en(e["data"]), tt_, f"{dl('calendario.json')}"])
    cal_rows += [[date_en("2026-11-20"), "CGIL general strike; rail strikes incl. freight (21:00 on 20 Nov to 20:00 on 21 Nov)", "Rai News"],
                 [date_en(V["earliest"]), "earliest start of a haulage stoppage called today", "calculation (25 days' notice)"],
                 ["1 December 2026", "end of the window for the EU 90% storage target", dl("scorte.json")],
                 ["31 December 2026", "deadline to use the haulage tax credit; end of Qatar's force-majeure extension for Edison", "TrasportoEuropa; gasworld"],
                 ["January 2027", "bill decree takes effect", "ANSA"]]
    cal_rows.sort(key=lambda r: dt.datetime.strptime(r[0], "%d %B %Y") if r[0][0].isdigit() else dt.datetime(2027, 1, 1))
    TAB(["Date", "What", "Source"], cal_rows, "Missing: Istat's release dates for the November inflation estimate and ARERA's November gas value are not in the calendar file.")
    # ------------------------------------------------------------------ 8
    H2("method", "8. Method, sources and limits")
    P("**How it is made.** Text, tables and charts are generated by `report/build_italy.py` from the files in `docs/data/` (standard library only; it can be re-run every month). "
      "No number from the data is typed by hand. Facts the files do not hold are kept in one table in the script (`EXTERNAL`) with source, link, date and reliability. "
      "Paragraphs marked *Assessment* are the monitor's reasoning on the sources cited.")
    TAB(["Source", "What", "Date of the data", "File"],
        [["MASE, DGSAIE", "weekly fuel prices with excise and VAT; monthly fuel sales", f"{date_en(lastd)}; {month_en(sales['mese'])}", dl("italia-impatti.json")],
         ["GME", "PUN and gas exchange prices", date_en(V["pun_day"][0]), dl("italia-impatti.json")],
         ["ARERA", "regulated gas for vulnerable customers", month_en(a["mese"]), dl("italia-impatti.json")],
         ["Istat, Eurostat", "NIC and HICP inflation, basket weights, consumer confidence", month_en(nl[0]), dl("italia-impatti.json")],
         ["Curated news sources", "haulage rules, precedents, statements, measures, strikes", "to 9 November 2026", dl("italia-impatti.json")],
         ["ENTSOG", "gas physical flows by entry point", date_en(V["gas_period"][1]), dl("gas-italia.json")],
         ["GIE AGSI+, Eurostat", "gas storage; emergency oil stocks", f"{date_en(it['data'])}; {month_en(V['oil_days']['it']['data'])}", dl("scorte.json")],
         ["UN Comtrade, Eurostat, IMF", "suppliers, import shares, dependence, forecasts", "2024–2025; WEO October 2026", f"{dl('paesi.json')}, {dl('commercio.json')}"],
         ["IMF PortWatch", "ship calls at Italian ports", date_en(V["pw_last"]), dl("portwatch.json")],
         ["Monitor's models", "Port Risk Index; transit times; risk dashboard", date_en(V["pr"]["reference_date"]), f"{dl('port-risk.json')}, {dl('transit-times.json')}, {dl('rischio.json')}"],
         ["Yahoo Finance; Drewry, Freightos", "Brent, TTF; container freight", f"{date_en(brent['data'])}; {date_en(wci['data'])}", f"{dl('prezzi.json')}, {dl('noli.json')}"]], "")
    P("**Limits.**")
    UL([f"The Mimit daily price file could not be downloaded from this environment; the report uses the MASE weekly average (self-service and attended together) and one daily figure from ANSA.",
        f"The pass-through coefficients are simple regressions estimated by the data collector on {est['n_settimane']} MASE weeks from {date_en(est['periodo'][0])} to {date_en(est['periodo'][1])}, "
        f"a period with two large crises. The file keeps only the {len(V['dsl'])} weeks from {month_en(V['dsl_first'])}, so the coefficients cannot be re-estimated from the repository "
        f"alone (the MASE file has the missing weeks). They work for large shocks, less for small moves, and treat rises and falls alike, whereas pump prices usually fall more slowly than they rise.",
        "Inflation in the scenarios is the direct effect of energy only. The ratio from the PUN to household power prices (0.75) comes from a single year, 2022 (reliability low).",
        "The stoppage thresholds are a judgement on precedents, not a model. The diesel weight in haulage costs is French (CNR, long-haul articulated truck); it was read from a summary, "
        "not the PDF, and Italian trucks, wages and tolls differ.",
        f"Brent: {dl('prezzi.json')} records {num(brent['ultimo'], 2)} dollars under {date_en(brent['data'])} ({pct(brent['var']['1g'])} on the day), but that is a price read at 03:40 UTC "
        f"on 10 November, during the next session's overnight trading. The 9 November close was {num(V['brent_close'], 2)} (Yahoo Finance, read 10 November, −5.8% on the day); "
        f"the risk dashboard and the Hormuz report use 92.62, an intraday reading of the same session. This report quotes the close; the scenarios keep the simulator's "
        f"{num(brent['ultimo'], 2)}. The TTF close was 82.50 against 82.33 in the file; the +164% on a year is unchanged.",
        "The haulage tax credit appears as 480 million euros allocated (Ministry of Transport, 9 November) and as 434 million allocated (Unatras, 21 October): the sources do not explain the difference.",
        "The emergency-stock series has an anomalous June 2026 value (89.7 days between 76.6 and 77.3), not used. The diesel prices at the start of past protests were recomputed "
        "from the MASE weekly series by the review; the curated values in the data file use inconsistent reference weeks. Consumer confidence is not seasonally adjusted. Comtrade shares are by value and rely on the importer's declaration.",
        "PortWatch counts only ships with AIS on and arrives a week late. The transit-time model has no port or waiting time.",
        "**Missing:** an official Italian figure for diesel in haulage costs; the text of the haulage self-regulation code (maximum durations); the official strike calendar; the outcome of the "
        "27 October meeting; the origin of LNG cargoes in 2026; the ARERA values for June and August 2026; the text of the 9 November bill decree."])
    B.append(("review",))
    return B


# =====================================================================================
# Rendering
# =====================================================================================
def inline_md(t, P):
    return t.replace("](DATA/", f"]({P}")


def inline_html(t, P):
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2).replace("DATA/", P)}">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def review_parts():
    r = REVIEW
    return [
        ("p", f"**Reviewed on {r['date']}** by an independent fact-check and edit (carried out with an AI assistant). {r['claims']} claims checked against the data files and the cited "
              f"sources: {r['ok']} confirmed, {r['corrected']} corrected, {r['unverified']} not verifiable from here. Full table in `{r['log']}`."),
        ("p", "**Main corrections.** Brent: the 91.70 dollars in prezzi.json is an overnight price of 10 November; the 9 November close was 92.57. The key point on diesel claimed "
              "a return to about €2.29 after the excise cut ended; daily self-service prices rose less than a cent. The Unatras figure of 434 million is an allocation, "
              "not unpaid credit. The diesel prices and year-on-year changes at past protests were recomputed on the same MASE week. Unem, the Qatar trains and the bill decree "
              "were re-attributed to what the sources say. The haulage-cost estimate now shows the case with the excise refund (about +9% on total cost). La Spezia's risk "
              "is explained by the rule that drives it."),
        ("p", "**Not verifiable from here:** the CNR diesel weight (PDF blocked), the Sky TG24 reference gas price, the maximum stoppage duration in the haulage code, the "
              "outcome of the 27 October meeting, the Corriere estimate of under 30 euros a year (dropped), the origin of Panigaglia's cargoes, the official strike calendar."),
    ]


def render_md(B, meta, figs):
    P = "../docs/data/"
    o = [f"# {meta['title']}", "", f"*{meta['subtitle']}*", "",
         f"Gabriele Giuliani · Geo-economic Risk Monitor · {meta['edition']} · data read on {meta['read']}", "",
         "Every number has a source and a date. Paragraphs marked *Assessment* are the monitor's reasoning, not facts.", "",
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
        elif k == "gloss":
            o += ["> **Words used in this report.** " + " ".join(f"*{a}*: {c}." for a, c in b[1]), ""]
        elif k == "tab":
            o += ["| " + " | ".join(b[1]) + " |", "|" + "---|" * len(b[1])]
            o += ["| " + " | ".join(inline_md(str(c), P).replace("|", "/") for c in r) + " |" for r in b[2]]
            o += ["", f"*{inline_md(b[3], P)}*" if b[3] else "", ""]
        elif k == "fig":
            o += [f"![{re.sub(r'[*`]', '', b[2])[:110]}]({figs[b[1]]})", "", inline_md(b[2], P), ""]
        elif k == "review":
            o += ['<a id="review"></a>', "", "---", "", f"### Review · {REVIEW['date']}", ""]
            for kk, x in review_parts():
                o += [inline_md(x, P), ""]
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
.keys li{margin-bottom:14px}
.gloss{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:12px 16px;margin:8px 0 16px;font-size:14px}
.gloss summary{font:600 13px/1.4 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--soft)}
.gloss dl{margin:10px 0 0;display:grid;grid-template-columns:max-content 1fr;gap:6px 14px}
.gloss dt{font-weight:600}.gloss dd{margin:0}
@media (max-width:560px){.gloss dl{grid-template-columns:1fr}.gloss dd{margin-bottom:6px}}
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
.review{margin:40px 0 0;padding:16px 18px;background:var(--card);border:1px dashed var(--soft);border-left:3px solid var(--soft);border-radius:0 8px 8px 0;font-size:15px}
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
         f'<p class="kicker">Country report · Italy · {esc(meta["edition"])}</p>',
         f"<h1>{esc(meta['title'])}</h1>", f'<p class="sub">{esc(meta["subtitle"])}</p>',
         f'<p class="meta">Gabriele Giuliani · Geo-economic Risk Monitor · data read on {esc(meta["read"])}. Every number has a source and a date; '
         f'boxes marked <em>Assessment</em> are the monitor\'s reasoning, not facts.</p>',
         '<nav class="toc" aria-label="Contents"><h2>Contents</h2><ol>']
    for b in B:
        if b[0] == "h2":
            o.append(f'<li><a href="#{b[1]}">{esc(re.sub(r"^\d+\. ", "", b[2]))}</a></li>')
    o.append('<li><a href="#review">Review</a></li></ol></nav>')
    first_ul = True
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
            txt = txt[0].upper() + txt[1:]
            o.append(f'<aside class="assess"><span class="tag">Assessment</span>{inline_html(txt, P)}</aside>')
        elif k == "ul":
            cls = ' class="keys"' if first_ul else ""
            first_ul = False
            o.append(f"<ul{cls}>" + "".join(f"<li>{inline_html(x, P)}</li>" for x in b[1]) + "</ul>")
        elif k == "gloss":
            o.append('<details class="gloss"><summary>Words and institutions used in this report</summary><dl>' +
                     "".join(f"<dt>{esc(a)}</dt><dd>{esc(c)}</dd>" for a, c in b[1]) + "</dl></details>")
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
                     f'<figcaption>{inline_html(b[2].strip("*"), P)}</figcaption>'
                     f'<details><summary>Chart data as a table</summary>{g["table"]}</details></figure>')
        elif k == "review":
            parts = "".join(f"<p>{inline_html(x, P)}</p>" for kk, x in review_parts())
            o.append(f'<aside class="review" id="review"><h2>Review · {esc(REVIEW["date"])}</h2>{parts}</aside>')
    o.append(f'<footer><p class="sig">Gabriele Giuliani · Geo-economic Risk Monitor</p><p>{esc(meta["edition"])}. {inline_html(meta["ai_note"], P)}</p>'
             '<p><a href="../../index.html">← Back to the map</a></p></footer>')
    o += ["</main>", "</body>", "</html>"]
    return "\n".join(o)


def charts(V):
    out = {}
    tw = lambda f: (f(V, True), f(V, False))
    w, n = tw(chart_pump)
    dsl, ptr = V["dsl"], V["ptr"]
    sel = [k for k, _ in dsl if k.endswith(("-01-03", "-01-02", "-01-01")) or k in (V["pre"], V["dsl_max"][0], V["last_fuel"], "2022-03-14", "2022-03-28", "2026-04-13")]
    out["pump"] = (w, n, table_html(["Week", "Diesel €/l", "Petrol €/l"], [[date_en(k), num(at(dsl, k), 3), num(at(ptr, k), 3)] for k in sorted(set(sel))]))
    (w, rows), (n, _) = chart_breakdown(V, True), chart_breakdown(V, False)
    out["breakdown"] = (w, n, table_html(["Week", "Net", "Excise", "VAT", "Total, €/l"], [[r[0], num(r[1], 3), num(r[2], 4), num(r[3], 4), num(r[4], 3)] for r in rows]))
    (w, short), (n, _) = chart_gas(V, True), chart_gas(V, False)
    out["gas"] = (w, n, table_html(["Entry point", "TWh, 12 months", "Share, %"], [[q["nome"], num(q["twh_12m"], 1), num(q["quota_ingressi_pct"], 1)] for q in V["gas_q"]]))
    out["pun"] = (chart_pun(V, True), chart_pun(V, False), table_html(["Month", "PUN €/MWh"], [[month_en(m), num(v, 2)] for m, v in V["pun_m"]]))
    nic = V["nic"]
    out["infl"] = (chart_infl(V, True), chart_infl(V, False),
                   table_html(["Month", "Headline", "Energy", "Food", "Core"], [[month_en(m), num(at(nic["generale"], m), 1), num(v, 1), num(at(nic["alimentari"], m), 1), num(at(nic["componente_di_fondo"], m), 1)] for m, v in nic["energetici"]]))
    out["sales"] = (chart_sales(V, True), chart_sales(V, False),
                    table_html(["Month", "Road diesel", "Off-network diesel", "Petrol"], [[month_en(s["mese"]), pct(s["gasolio_motori"]["var_pct"]), pct(s["gasolio_extrarete"]["var_pct"]), pct(s["benzina"]["var_pct"])] for s in V["sales"] if s["mese"] >= "2026-01"]))
    (w, P), (n, _) = chart_protests(V, True), chart_protests(V, False)
    out["protests"] = (w, n, table_html(["Protest", "Diesel €/l", "On a year"], [[PREC_EN[p["id"]][1], num(p["gasolio_alla_data"]["eur_l"], 3), pct(p["gasolio_alla_data"]["var_pct_un_anno"])] for p in P] + [["Today", num(V["g"]["eur_l"], 3), pct(V["dsl_yoy"])]]))
    out["ports"] = (chart_ports(V, True), chart_ports(V, False),
                    table_html(["Port", "Calls/day 2026", "Year to date", "Last 30 days"], [[p["name"], num(p["ytd_now"], 2), pct(p["ytd"]), pct(p["var30"])] for p in V["ports"]]))
    (w, rows), (n, _) = chart_transit(V, True), chart_transit(V, False)
    out["transit"] = (w, n, table_html(["Route", "Via Suez", "Today's mix", "Via the Cape"], [[nm, num(r["days_base"], 1), num(r.get("days_today_weighted"), 1), num(r["cape"]["days"], 1)] for nm, r in rows]))
    (w, names), (n, _) = chart_scen(V, True), chart_scen(V, False)
    out["scen"] = (w, n, table_html(["Scenario", "From pre-war, €/l", "From today, €/l"], [[names[k], "–".join(num(x, 2) for x in s["da_condizioni_normali"]["gasolio_eur_l"]), "–".join(num(x, 2) for x in s["da_oggi"]["gasolio_eur_l"])] for k, s in V["scen"].items()]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", help="edition YYYY-MM (default: current month)")
    args = ap.parse_args()
    today = dt.date.today()
    month = args.month or today.strftime("%Y-%m")
    y, m = map(int, month.split("-"))
    V = compute(today)
    edition = f"{MONTHS[m - 1]} {y}"
    B = blocks(V, edition, today)
    meta = {"title": f"Italy and the Gulf Shock: Fuel, Freight, Prices and the Risk of a Truck Strike — {edition}",
            "short": "Italy and the Gulf Shock",
            "subtitle": f"How the closure of Hormuz reaches Italian pumps, bills, prices, ports and road haulage, and what a new shock would do. {edition}.",
            "edition": edition, "read": date_en(today.isoformat()),
            "ai_note": ("Note on AI use: this report was prepared with an AI assistant (Claude, Anthropic), which wrote the build script, the calculations, the charts "
                        "and the draft text from the monitor's data files and the sources cited. Numbers come from the data files and linked sources; assessments are marked. "
                        "An independent review (10 November 2026, report/revisioni/italy-gulf-shock-2026-11.md) checked the numbers against the data and the sources. "
                        "Gabriele Giuliani is responsible for publication.")}
    os.makedirs(OUT_SVG, exist_ok=True)
    os.makedirs(OUT_HTML, exist_ok=True)
    C = charts(V)
    svg, figs = {}, {}
    for key, (w, n, t) in C.items():
        svg[key] = {"wide": w, "narrow": n, "table": t}
        name = f"it-{month}-{key}.svg"
        with open(os.path.join(OUT_SVG, name), "w", encoding="utf-8") as f:
            f.write(w)
        figs[key] = f"grafici/{name}"
    with open(os.path.join(ROOT, "report", f"{SLUG}-{month}.md"), "w", encoding="utf-8") as f:
        f.write(render_md(B, meta, figs))
    with open(os.path.join(OUT_HTML, f"{SLUG}-{month}.html"), "w", encoding="utf-8") as f:
        f.write(render_html(B, meta, svg))
    print(f"written: report/{SLUG}-{month}.md, docs/report/en/{SLUG}-{month}.html, {len(svg)} charts; {len(WARN)} warnings")


if __name__ == "__main__":
    main()
