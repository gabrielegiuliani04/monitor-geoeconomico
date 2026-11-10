#!/usr/bin/env python3
"""Build the monthly report "Asia–Europe Logistics: Routes, Costs and Port Risk" from the monitor's data.

Standard library only, no network. From the repository root:

    python3 report/build_logistics.py                  # edition for the current month
    python3 report/build_logistics.py --month 2026-12  # another edition label

What it does every time it runs:
1. reads docs/data/*.json: transit-times, port-risk, porti-nord, portwatch, noli, bunker-emissioni,
   assicurazioni, stretti-dettaglio, rischio, ferrovie, supply-chain-ai, commercio, minerali,
   sanzioni-navi, navi, calendario, prezzi;
2. recomputes every number in the text: lane days and nautical miles, the cost stack of an
   Asia–North Europe voyage (per voyage and per FEU) for 2023 and today, the Cape break-even
   war-risk premium, port risk rankings and congestion proxies;
3. draws four SVG charts (wide and narrow versions) from those numbers;
4. writes report/asia-europe-logistics-YYYY-MM.md, docs/report/en/asia-europe-logistics-YYYY-MM.html
   and the SVGs in report/grafici/ael-YYYY-MM-*.svg.

Rules (report/STANDARD.md): no number from the data is typed by hand in the text or the charts.
The only hand-written inputs are:
- EXTERNAL: facts the JSON files do not hold (2023 baselines), each with source, link, date,
  reliability and how it was read; the script warns when they are older than the edition allows;
- THRESHOLDS: scenario thresholds, an assessment, labelled as such;
- linking prose and assessments, marked "Assessment".
Curated facts quoted from text fields are checked with need(): if the figure disappears from the
source text at the next run, the script warns, so the sentence is re-read.
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
SLUG = "asia-europe-logistics"

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
    "vlsfo_sg_2023": {
        "value": 668.5, "unit": "$/t", "date": "2023-10",
        "text": "Singapore VLSFO, October 2023 monthly average",
        "source": "Ship & Bunker monthly price review, as quoted by PortNews",
        "link": "https://en.portnews.ru/news/356287", "reliability": "medium",
        "read": "search-result excerpt; the page itself was not reachable from the session",
    },
    "wci_sh_rtm_2023": {
        "value": 1048.0, "unit": "$/FEU", "date": "2023-11-02",
        "text": "Drewry WCI Shanghai–Rotterdam, 2 November 2023 (range in November 2023: 1,048–1,272 $/FEU)",
        "range": [1048.0, 1272.0],
        "source": "Drewry World Container Index, as reprinted by Air Freight News and Hellenic Shipping News",
        "link": "https://www.hellenicshippingnews.com/drewry-world-container-index-up-7-this-week/", "reliability": "medium",
        "read": "search-result excerpts; Drewry's archive and the reprints were not opened from the session",
    },
}

# Scenario thresholds for Q1 2027: an ASSESSMENT of the monitor, not a forecast.
# Thresholds marked "rischio.json" are read from the risk dashboard; the others are set here.
THRESHOLDS = {
    "fbx11_low": 3000,     # $/FEU: rates falling as capacity returns
    "fbx11_high": 4500,    # $/FEU: rates repricing a relapse
    "redsea_war_high": 0.5,  # % of hull: Red Sea premium at which Cape becomes cheaper once the Suez toll is counted (computed band shown in text)
    "vlsfo_sg_high": 1000,   # $/t Singapore VLSFO
    "gof_sanctioned": 50,    # sanctioned tankers in one AIS snapshot, Gulf of Finland
}

REVIEW = None  # placeholder: filled in after the independent review (log in report/revisioni/)


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


def num(v, dec=0):
    if v is None:
        return "n/a"
    return f"{v:,.{dec}f}".replace("-", "−")


def pct(v, dec=1, sign=True):
    if v is None:
        return "n/a"
    if round(v, dec) == 0:
        return "0%"
    s = f"{v:+,.{dec}f}" if sign else f"{v:,.{dec}f}"
    return s.replace("-", "−") + "%"


def musd(v, dec=2):
    return f"{v / 1e6:,.{dec}f} M$".replace("-", "−")


def date_en(s, year=True):
    s = str(s)
    if len(s) == 7:
        y, m = s.split("-")
        return f"{MONTHS[int(m) - 1]} {y}"
    x = d(s)
    return f"{x.day} {MONTHS[x.month - 1]}" + (f" {x.year}" if year else "")


def esc(s):
    return html.escape(str(s), quote=True)


def dl(name):
    return f"[{name}](DATA/{name})"


def need(text, *tokens, where=""):
    t = str(text)
    for tok in tokens:
        if str(tok) not in t:
            warn(f"curated fact not found in source ({where}): «{tok}»")


def first_pct(t):
    m = re.search(r"([+−-]?\d+(?:,\d+)?)%", t)
    return (m.group(1).replace(",", ".").replace("-", "−") + "%") if m else "n/a"


IT_MON = {"gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
          "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12}


def it_period(t):
    for k, v in IT_MON.items():
        t = t.replace(f" {k}", f" {MONTHS[v - 1]}")
    return t.replace(" - ", "–")


SIG_EN = {
    "Suez tra 40 e 50 navi al giorno": "Suez between 40 and 50 ships a day",
    "Bab el-Mandeb tra 25 e 35 navi al giorno": "Bab el-Mandeb between 25 and 35 ships a day",
    "Nessun attacco a navi nel Mar Rosso e Golfo di Aden negli ultimi 30 giorni": "no attack on ships in the Red Sea or Gulf of Aden in the last 30 days",
    "Premio Genova su Rotterdam tra 5 e 20%": "Genoa premium over Rotterdam between 5% and 20%",
    "Almeno un attacco a navi nel Mar Rosso o Golfo di Aden negli ultimi 30 giorni": "at least one attack on ships in the Red Sea or Gulf of Aden in the last 30 days",
    "Bab el-Mandeb sotto 20 navi al giorno": "Bab el-Mandeb below 20 ships a day",
    "Suez sotto 35 navi al giorno": "Suez below 35 ships a day",
    "Shanghai–Genova sopra 5.000 $/FEU": "WCI Shanghai–Genoa above 5,000 $/FEU",
    "Premio Genova su Rotterdam oltre il 20%": "Genoa premium over Rotterdam above 20%",
    "Suez sopra 50 navi al giorno": "Suez above 50 ships a day",
    "Bab el-Mandeb sopra 35 navi al giorno": "Bab el-Mandeb above 35 ships a day",
    "WCI composito sotto 4.000 $/FEU": "WCI composite below 4,000 $/FEU",
    "Premio Genova su Rotterdam sotto il 5%": "Genoa premium over Rotterdam below 5%",
}


def sig_en(t):
    if t not in SIG_EN:
        warn(f"scenario signal without translation: «{t}»")
    return SIG_EN.get(t, t)


def var(a, b):
    if a is None or b in (None, 0):
        return None
    return (a / b - 1) * 100


LEVEL = {"basso": "low", "medio": "medium", "alto": "high", "critico": "critical"}
CC = {"NL": "NL", "BE": "BE", "DE": "DE", "DK": "DK", "SE": "SE", "PL": "PL", "LT": "LT", "LV": "LV",
      "EE": "EE", "FI": "FI", "RU": "RU", "IT": "IT"}
SHORT = {"Antwerp-Bruges (Antwerp + Zeebrugge)": "Antwerp-Bruges", "Wilhelmshaven (JadeWeserPort)": "Wilhelmshaven",
         "Świnoujście (with Szczecin)": "Świnoujście", "Eemshaven (Groningen Seaports)": "Eemshaven",
         "Bremen / Bremerhaven": "Bremerhaven", "Tallinn (Muuga and Old City Harbour)": "Tallinn",
         "Copenhagen-Malmö (CMP)": "Copenhagen-Malmö", "Sköldvik (Porvoo)": "Sköldvik",
         "St Petersburg (Big Port, with Bronka)": "St Petersburg", "Kaliningrad and Baltiysk": "Kaliningrad"}


def short(n):
    return SHORT.get(n, n)


# =====================================================================================
# Computation
# =====================================================================================
def compute(today):
    V = {"today": today}
    names = ["transit-times.json", "port-risk.json", "porti-nord.json", "portwatch.json", "noli.json",
             "bunker-emissioni.json", "assicurazioni.json", "stretti-dettaglio.json", "rischio.json",
             "ferrovie.json", "supply-chain-ai.json", "commercio.json", "minerali.json",
             "sanzioni-navi.json", "navi.json", "calendario.json", "prezzi.json"]
    F = {n: load(n) for n in names}
    V["F"] = F
    for k, e in EXTERNAL.items():
        age = (today - d(e["date"] + ("-15" if len(e["date"]) == 7 else ""))).days
        if age > 365 * 4:
            warn(f"external fact {k} is {age} days old")

    # ------------------------------------------------------------ routes (transit-times.json)
    tt = F["transit-times.json"]
    R = {(r["from"], r["to"]): r for r in tt["routes"]}
    V["R"] = R
    V["tt"] = tt
    m = tt["method"]
    share = m["container_red_sea_share"]["value_pct"] / 100
    V["share"] = share
    V["share_src"] = m["container_red_sea_share"]
    veh = m["vessels"]["container"]
    V["veh"] = veh
    V["passages"] = tt["passages_today"]
    V["pw"] = tt["portwatch_transits_per_day"]
    V["validation"] = tt["validation"]
    lanes = [("shanghai", "rotterdam"), ("shanghai", "hamburg"), ("shanghai", "gdansk"), ("shanghai", "klaipeda"),
             ("shanghai", "esbjerg"), ("busan", "antwerp"), ("singapore", "rotterdam"), ("nhava_sheva", "rotterdam"),
             ("jebel_ali", "rotterdam"), ("shanghai", "genoa"), ("shanghai", "piraeus")]
    L = []
    for k in lanes:
        r = R[k]
        cape = r["cape"]
        L.append({"key": k, "from": r["from_name"].split(" (")[0].replace("Mumbai / Nhava Sheva", "Nhava Sheva"),
                  "to": r["to_name"], "nm_base": r["nm_base"], "nm_today": r["nm_today"], "nm_cape": cape["nm"],
                  "d_base": r["days_base"], "d_today": r["days_today"], "d_cape": cape["days"],
                  "d_w": share * r["days_today"] + (1 - share) * cape["days"],
                  "status": r["status"], "loads": r["loads_today_at"]})
    V["lanes"] = L
    sh = R[("shanghai", "rotterdam")]
    V["baltic_extra"] = {t: R[("shanghai", t)]["nm_today"] - sh["nm_today"] for t in ("gdansk", "klaipeda", "hamburg")}
    V["baltic_extra_days"] = {t: R[("shanghai", t)]["days_today"] - sh["days_today"] for t in ("gdansk", "klaipeda")}
    V["med_cape_penalty"] = {t: R[("shanghai", t)]["cape"]["extra_days_vs_base"] for t in ("genoa", "trieste", "piraeus", "rotterdam")}
    V["rt"], V["yanbu"], V["laffan"], V["jebel"] = R[("ras_tanura", "rotterdam")], R[("yanbu", "rotterdam")], R[("ras_laffan", "rotterdam")], R[("jebel_ali", "rotterdam")]

    # ------------------------------------------------------------ cost stack
    be = F["bunker-emissioni.json"]
    ex = {e["id"]: e for e in be["esempi_costo"]}["asia-rotterdam"]
    m_t = re.search(r"Carburante: (\d+) t", ex["calcolo"][0])
    cov_ex = float(m_t.group(1)) if m_t else 4000.0
    ets_t_eur = ex["costo_ets_eur"] / cov_ex          # € per t of fuel on an extra-EU leg (50% coverage, 2026 phase-in)
    fueleu_t_eur = ex["costo_fueleu_max_eur"] / cov_ex
    eurusd, eua = ex["eurusd"], ex["eua_eur"]
    if abs(eua - be["eua"]["asta_ultima"]["prezzo_eur"]) > 0.005:
        warn("EUA in the cost example differs from the latest auction")
    need(" ".join(ex["calcolo"]), "3.1631", "50%", "100%", where="bunker-emissioni asia-rotterdam")
    need(veh["unit_note"], "15,000 TEU x 85%", where="transit-times container unit_note")
    need(m["war_risk"], "Red Sea 0.075%", where="transit-times war_risk")
    fd = veh["fuel_t_day"]
    units = veh["units_per_voyage"]
    hull = veh["hull_value_musd"] * 1e6
    sg = R[("singapore", "rotterdam")]
    p_now = sh["fuel_price"]["vlsfo_usd_t"]
    p_prewar = sh["fuel_price"]["prewar_usd_t"]
    p_2023 = EXTERNAL["vlsfo_sg_2023"]["value"]
    war_today = sum(i["usd"] for i in sh["war_risk_items"])
    war_today_pct = sum(i["pct_hull"] for i in sh["war_risk_items"])
    war_base = sh["cost_breakdown_usd"]["war_risk_base"]
    war_base_pct = war_base / hull * 100
    cape_war = 0.0 if not sh["cape"]["listed_areas"] else None
    if cape_war is None:
        warn("Cape route crosses a listed area: war risk on the Cape not modelled")
        cape_war = 0.0
    T = {
        "2023": {"days": sh["days_base"], "cov_days": sg["days_base"], "price": p_2023, "ets": 0.0, "fueleu": 0.0, "war": war_base},
        "suez": {"days": sh["days_today"], "cov_days": sg["days_today"], "price": p_now, "ets": None, "fueleu": None, "war": war_today},
        "cape": {"days": sh["cape"]["days"], "cov_days": sg["cape"]["days"], "price": p_now, "ets": None, "fueleu": None, "war": cape_war},
    }
    for k, t in T.items():
        t["fuel_t"] = t["days"] * fd
        t["cov_t"] = t["cov_days"] * fd
        t["fuel"] = t["fuel_t"] * t["price"]
        if t["ets"] is None:
            t["ets"] = t["cov_t"] * ets_t_eur * eurusd
            t["fueleu"] = t["cov_t"] * fueleu_t_eur * eurusd
        t["total"] = t["fuel"] + t["ets"] + t["fueleu"] + t["war"]
    w = {k: share * T["suez"][k] + (1 - share) * T["cape"][k] for k in ("days", "fuel_t", "cov_t", "fuel", "ets", "fueleu", "war", "total")}
    T["today"] = w
    for t in T.values():
        t["feu"] = {k: t[k] / units for k in ("fuel", "ets", "fueleu", "war", "total")}
    V["T"] = T
    V["cost_in"] = {"fd": fd, "units": units, "hull": hull, "p_now": p_now, "p_prewar": p_prewar, "p_2023": p_2023,
                    "p_date": sh["fuel_price"]["date"], "prewar_date": sh["fuel_price"]["prewar_date"],
                    "ets_t_eur": ets_t_eur, "fueleu_t_eur": fueleu_t_eur, "eurusd": eurusd, "eua": eua,
                    "eua_date": be["eua"]["asta_ultima"]["data"], "cov_ex": cov_ex,
                    "war_today_pct": war_today_pct, "war_base_pct": war_base_pct,
                    "war_src": sh["war_risk_items"][0]["source"], "speed": veh["speed_kn"]}
    # cross-checks against the transit-times model
    pe = T["suez"]["fuel_t"] * (p_now - p_prewar)
    if abs(pe - sh["cost_breakdown_usd"]["fuel_price_effect_whole_voyage"]) > 50:
        warn(f"fuel price effect does not match transit-times.json: {pe:.0f}")
    if abs((T["cape"]["fuel_t"] - T["suez"]["fuel_t"]) - sh["cape"]["extra_fuel_t"]) > 1:
        warn("extra Cape fuel does not match transit-times.json")
    # waterfall per FEU
    W = []
    W.append(("2023 voyage", T["2023"]["feu"]["total"], "total"))
    W.append(("Fuel price, 2023 → today", T["suez"]["feu"]["fuel"] - T["2023"]["feu"]["fuel"], "fuel"))
    W.append((f"Cape share ({round((1 - share) * 100)}% of capacity)", w["fuel"] / units - T["suez"]["feu"]["fuel"], "cape"))
    W.append(("EU ETS", w["ets"] / units, "ets"))
    W.append(("FuelEU (max penalty)", w["fueleu"] / units, "fueleu"))
    W.append(("War risk, change", (w["war"] - T["2023"]["war"]) / units, "war"))
    W.append(("Today, capacity-weighted", w["total"] / units, "total"))
    if abs(sum(x[1] for x in W[:-1]) - W[-1][1]) > 0.01:
        warn("waterfall does not add up")
    V["W"] = W
    # Cape break-even war-risk premium
    extra = (T["cape"]["fuel"] + T["cape"]["ets"] + T["cape"]["fueleu"]) - (T["suez"]["fuel"] + T["suez"]["ets"] + T["suez"]["fueleu"])
    mt = re.search(r"~([\d.]+)-([\d.]+) M\$ per transit", m["extra_cost_usd"])
    toll = (float(mt.group(1)) * 1e6, float(mt.group(2)) * 1e6) if mt else (0.5e6, 1e6)
    if not mt:
        warn("Suez toll range not found in transit-times method text")
    V["breakeven"] = {"extra": extra, "pct": extra / hull * 100, "toll": toll,
                      "pct_toll": ((extra - toll[1]) / hull * 100, (extra - toll[0]) / hull * 100)}
    # freight
    no = {e["id"]: e for e in F["noli.json"]["elementi"]}
    V["no"] = no
    wci = no["wci"]
    V["wci_rtm"], V["wci_goa"], V["wci_date"] = wci["rotte"]["Shanghai-Rotterdam"], wci["rotte"]["Shanghai-Genoa"], wci["data"]
    V["wci_comp"] = wci["valore"]
    V["wci_2023"] = EXTERNAL["wci_sh_rtm_2023"]["value"]
    fbx = no["fbx"]
    V["fbx"] = fbx
    V["fbx11"], V["fbx13"] = fbx["rotte"]["FBX11"], fbx["rotte"]["FBX13"]
    V["fbx_series"] = fbx["storico"]
    V["ccfi"] = no["ccfi"]
    V["genoa_premium"] = var(V["wci_goa"], V["wci_rtm"])
    V["maersk"] = be["sovrapprezzo_vettori"]
    V["be"] = be
    V["vlsfo_sg"] = {e["nome"]: e for e in be["elementi"] if e.get("tipo") == "hub_bunker"}["Singapore"]["prezzi"]["VLSFO"]

    # ------------------------------------------------------------ insurance
    ass = F["assicurazioni.json"]
    V["ass"] = ass
    V["prem_last"] = ass["ultimo_premio"]
    V["jwla"] = ass["circolare_in_vigore"]
    V["rs_series"] = ass["serie_premi"]["mar-rosso"]

    # ------------------------------------------------------------ risk dashboard
    ri = F["rischio.json"]
    V["risk"] = {u["id"]: u for u in ri["unita"]}
    V["risk_sc"] = {s["unita"]: s for s in ri["scenari"]}
    V["risk_date"] = ri["data_riferimento"]

    # ------------------------------------------------------------ ports
    pr = F["port-risk.json"]
    V["pr"] = pr
    P = pr["ports"]
    for p in P:
        p["ind"] = {i["name"]: i for i in p["indicators"]}
    V["ports_ns"] = sorted([p for p in P if p["region"] == "North Sea / Baltic" and p["country"] != "RU"], key=lambda p: (-p["score"], p["name"]))
    V["ports_ru"] = sorted([p for p in P if p["country"] == "RU"], key=lambda p: -p["score"])
    V["ports_it"] = sorted([p for p in P if p["region"] == "Italy"], key=lambda p: (-p["score"], p["name"]))
    V["moved"] = sorted([p for p in P if abs(p["score"] - p["score_7d_ago"]) >= 0.5], key=lambda p: -(p["score"] - p["score_7d_ago"]))
    pn = {e["id"]: e for e in F["porti-nord.json"]["elementi"]}
    pw = {e["id"]: e for e in F["portwatch.json"]["elementi"]}
    V["pn"], V["pw_el"] = pn, pw
    C = []
    for p in P:
        if "container gateway" not in p["strategic_roles"]:
            continue
        src = pn.get(p["source_id"]) or pw.get(p["source_id"])
        a, b = src["media30"].get("portcalls_container"), src["media30_anno_prima"].get("portcalls_container")
        prox = next((i for i in p["indicators"] if i["name"].startswith("Short-term disruption proxy")), None)
        C.append({"name": short(p["name"]), "country": p["country"], "region": p["region"],
                  "c30": a, "c30p": b, "c30var": var(a, b), "proxy": prox["value"] if prox else None,
                  "proxy_text": prox["text"] if prox else "", "date": src["ultima_data"], "score": p["score"]})
    C.sort(key=lambda c: (c["region"] != "North Sea / Baltic", -(c["c30"] or 0)))
    V["cong"] = C
    V["ports_date"] = max(c["date"] for c in C)
    V["pr_by"] = {p["id"]: p for p in P}

    # ------------------------------------------------------------ rail, air, dependencies
    fe = {e["id"]: e for e in F["ferrovie.json"]["elementi"]}
    V["rail"] = {k: fe[k] for k in ("FR-COR-01", "FR-COR-02", "FR-COR-03")}
    sca = F["supply-chain-ai.json"]
    V["ai_nodes"] = {e["id"]: e for e in sca["elementi"]}
    V["ai_arcs"] = {a["id"]: a for a in sca["archi"]}
    need(V["ai_nodes"]["ams"]["quota"], "40 container", "20 camion", "3 Boeing 747", where="supply-chain-ai ams")
    need(V["ai_nodes"]["ams"]["note"], "43 container", where="supply-chain-ai ams note")
    need(V["ai_nodes"]["veldhoven"]["note"], "11,7 mld EUR", "113", where="supply-chain-ai veldhoven")
    co = F["commercio.json"]
    V["dep"] = {(x["iso2"], x["hs"]): x for x in co["dipendenze"]}
    V["imp_partner"] = {e["iso2"]: e for e in co["elementi"]}

    # ------------------------------------------------------------ sanctions
    sn = F["sanzioni-navi.json"]
    V["sanc"] = sn["conteggi"]
    el = sn["elementi"]
    cont = [e for e in el if "ontainer" in (e.get("tipo_nave") or "")]
    V["sanc_cont"] = {"n": len(cont), "iran": sum("Iran" in e["ambito"] for e in cont),
                      "russia": sum("Russia" in e["ambito"] for e in cont),
                      "only_us": sum(e["sanzionata_da"] == ["USA"] for e in cont)}
    eu = [e for e in el if "Unione europea" in e["sanzionata_da"]]
    V["sanc_eu_ru"] = sum("Russia" in e["ambito"] for e in eu)
    V["sanc_lists_date"] = {f["nome"].split(",")[0].split(" (")[0]: f["data_dato"] for f in sn["fonti"]}
    recent = sorted([e for e in el if (e.get("prima_designazione") or "") >= (today - dt.timedelta(days=90)).isoformat()],
                    key=lambda e: e["prima_designazione"])
    V["sanc_recent"] = recent
    nv = F["navi.json"]
    V["navi_areas"] = nv["riepilogo_aree"]
    V["navi_date"] = nv["aggiornato"]
    V["shadow_ports"] = []
    for pid in ("ust-luga", "primorsk", "st-petersburg", "tallinn"):
        p = V["pr_by"][pid]
        i = next((x for x in p["indicators"] if x["name"].startswith("Likely shadow-fleet")), None)
        if i:
            V["shadow_ports"].append((short(p["name"]), i["value"], i["date"]))
    gof = V["risk_sc"]["baltico"]["scenari"][0]["segnali"]
    V["shadow_visible"] = next((g["valore"] for g in gof if "Flotta ombra" in g["descrizione"]), None)

    # ------------------------------------------------------------ calendar
    cal = F["calendario.json"]["elementi"]
    V["cal"] = [e for e in cal if today.isoformat() <= (e.get("data") or "") <= "2027-03-31"
                and (e.get("categoria") == "sanzioni" and "Russia" in (e.get("titolo") or "")
                     or "OPEC" in (e.get("titolo") or ""))]
    V["imo"] = be["regole"]["imo"]["net_zero_framework"]["cronologia"]
    return V


# =====================================================================================
# SVG charts (no <style> inside: the page and the standalone files add their own)
# =====================================================================================
SVG_CSS_LIGHT = (".ael-t{font:600 14px 'IBM Plex Sans',system-ui,sans-serif;fill:#1D272D}"
                 ".ael-l{font:12px 'IBM Plex Sans',system-ui,sans-serif;fill:#3b474e}"
                 ".ael-m{font:11px 'IBM Plex Mono',ui-monospace,monospace;fill:#5f6b72}"
                 ".ael-g{stroke:#d9dcd8;stroke-width:1}.ael-z{stroke:#5f6b72;stroke-width:1.2}"
                 ".ael-s1{fill:#A61E6B}.ael-s2{fill:#2a78d6}.ael-s3{fill:#eda100}.ael-s4{fill:#1baf7a}.ael-s0{fill:#4f5d66}.ael-s5{fill:#b9c0c4}"
                 ".ael-k1{stroke:#A61E6B}.ael-k2{stroke:#2a78d6}.ael-k3{stroke:#eda100}.ael-k0{stroke:#8a959b}"
                 ".ael-bg{fill:#ffffff}.ael-ring{stroke:#ffffff}")
SVG_CSS_DARK = (".ael-t{fill:#DAE0E2}.ael-l{fill:#c3cacd}.ael-m{fill:#99a5ab}.ael-g{stroke:#2f3b42}.ael-z{stroke:#99a5ab}"
                ".ael-s1{fill:#d14f9a}.ael-s2{fill:#3987e5}.ael-s3{fill:#c98500}.ael-s4{fill:#199e70}.ael-s0{fill:#A0ABB1}.ael-s5{fill:#4a575e}"
                ".ael-k1{stroke:#d14f9a}.ael-k2{stroke:#3987e5}.ael-k3{stroke:#c98500}.ael-k0{stroke:#6f7c83}"
                ".ael-bg{fill:#172127}.ael-ring{stroke:#172127}")


def svg_open(w, h, title, desc, uid):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" '
            f'aria-labelledby="{uid}-t {uid}-d" style="max-width:{w}px;height:auto;display:block">'
            f'<title id="{uid}-t">{esc(title)}</title><desc id="{uid}-d">{esc(desc)}</desc>'
            f'<rect class="ael-bg" x="0" y="0" width="{w}" height="{h}" rx="6"/>')


def standalone(svg):
    st = f"<style>{SVG_CSS_LIGHT}@media (prefers-color-scheme:dark){{{SVG_CSS_DARK}}}</style>"
    return svg.replace("</desc>", "</desc>" + st, 1)


def bar_path(x0, x1, y, h, r=4):
    if abs(x1 - x0) < 0.5:
        return f'M{x0:.1f},{y:.1f}h0.8v{h:.1f}h-0.8z'
    r = min(r, abs(x1 - x0), h / 2)
    if x1 >= x0:
        return (f'M{x0:.1f},{y:.1f}H{x1 - r:.1f}Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f}V{y + h - r:.1f}'
                f'Q{x1:.1f},{y + h:.1f} {x1 - r:.1f},{y + h:.1f}H{x0:.1f}Z')
    return (f'M{x0:.1f},{y:.1f}H{x1 + r:.1f}Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f}V{y + h - r:.1f}'
            f'Q{x1:.1f},{y + h:.1f} {x1 + r:.1f},{y + h:.1f}H{x0:.1f}Z')


def ticks(lo, hi, step):
    t, v = [], (int(lo // step)) * step
    while v <= hi + 1e-9:
        if v >= lo - 1e-9:
            t.append(round(v, 6))
        v += step
    return t


def legend(o, items, x0, y0, w, wide):
    x, y = x0, y0
    for nm, kind, cls in items:
        wd = 26 + len(nm) * 6.4
        if x + wd > w - 8:
            x, y = x0, y + 18
        if kind == "dot":
            o.append(f'<circle class="{cls}" cx="{x + 6}" cy="{y + 5}" r="5"/>')
        elif kind == "dia":
            o.append(f'<path class="{cls}" d="M{x + 6},{y - 1}l6,6l-6,6l-6,-6z"/>')
        elif kind == "tick":
            o.append(f'<line class="{cls}" x1="{x + 6}" x2="{x + 6}" y1="{y - 2}" y2="{y + 12}" stroke-width="3"/>')
        else:
            o.append(f'<rect class="{cls}" x="{x}" y="{y}" width="12" height="10" rx="2"/>')
        o.append(f'<text class="ael-l" x="{x + 18}" y="{y + 9}">{esc(nm)}</text>')
        x += wd + 10
    return y


def chart_lanes(V, wide=True):
    L = V["lanes"]
    w = 680 if wide else 360
    left = 196 if wide else 112
    right = 40 if wide else 30
    rowh = 30 if wide else 34
    o = []
    top0 = 34
    leg = []
    leg_y_end = legend(leg, [("via Suez (2023 and today's Suez services)", "dot", "ael-s2"),
                             (f"capacity-weighted today ({round(V['share'] * 100)}% Suez)", "tick", "ael-k1"),
                             ("via the Cape", "dia", "ael-s3")], 12, top0, w, wide)
    top = leg_y_end + 34
    h = top + rowh * len(L) + 30
    hi = 45
    X = lambda v: left + v / hi * (w - left - right)
    o.append(svg_open(w, h, "Sea days by lane: Suez, Cape and today's mix",
                      "Days at sea from Asia to European ports via Suez and via the Cape, and the capacity-weighted average today.",
                      "ch1" + ("w" if wide else "n")))
    o.append('<text class="ael-t" x="12" y="22">Days at sea, Asia → Europe, at 15 kn</text>')
    o += leg
    for t in ticks(0, hi, 5 if wide else 10):
        o.append(f'<line class="ael-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 10}" y2="{h - 26}"/>'
                 f'<text class="ael-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{int(t)}</text>')
    for i, l in enumerate(L):
        y = top + i * rowh + rowh / 2
        nm = f"{l['from']} → {l['to']}"
        if not wide:
            nm = nm.replace("Shanghai", "Sha.").replace("Singapore", "Sin.").replace("Nhava Sheva", "Nhava S.").replace("Jebel Ali", "J. Ali")
        o.append(f'<text class="ael-l" x="{left - 8}" y="{y + 4:.1f}" text-anchor="end">{esc(nm)}</text>')
        a, b, c = X(l["d_today"]), X(l["d_cape"]), X(l["d_w"])
        o.append(f'<line class="ael-k0" x1="{a:.1f}" x2="{b:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke-width="2"/>')
        o.append(f'<circle class="ael-s2 ael-ring" cx="{a:.1f}" cy="{y:.1f}" r="5" stroke-width="2"><title>{esc(nm)}: {num(l["d_today"], 1)} days via Suez ({num(l["nm_today"])} nm)</title></circle>')
        o.append(f'<path class="ael-s3 ael-ring" stroke-width="2" d="M{b:.1f},{y - 6:.1f}l6,6l-6,6l-6,-6z"><title>{esc(nm)}: {num(l["d_cape"], 1)} days via the Cape ({num(l["nm_cape"])} nm)</title></path>')
        o.append(f'<line class="ael-k1" x1="{c:.1f}" x2="{c:.1f}" y1="{y - 8:.1f}" y2="{y + 8:.1f}" stroke-width="3"><title>{esc(nm)}: {num(l["d_w"], 1)} days, capacity-weighted</title></line>')
        o.append(f'<text class="ael-m" x="{a - 8:.1f}" y="{y + 4:.1f}" text-anchor="end">{num(l["d_today"], 1)}</text>')
        o.append(f'<text class="ael-m" x="{b + 9:.1f}" y="{y + 4:.1f}">{num(l["d_cape"], 1)}</text>')
    o.append("</svg>")
    return "".join(o)


def chart_waterfall(V, wide=True):
    W = V["W"]
    w = 680 if wide else 360
    left = 200 if wide else 118
    right = 54 if wide else 44
    rowh = 34
    top = 48
    h = top + rowh * len(W) + 30
    hi = max(W[-1][1], max(sum(x[1] for x in W[:i + 1]) for i in range(len(W) - 1)))
    step = 100 if wide else 200
    hi = step * (-(-hi // step))
    X = lambda v: left + v / hi * (w - left - right)
    cls = {"total": "ael-s0", "fuel": "ael-s2", "cape": "ael-s4", "ets": "ael-s1", "fueleu": "ael-s3", "war": "ael-s5"}
    o = [svg_open(w, h, "Cost stack per FEU, Shanghai–Rotterdam, 2023 to today",
                  "Waterfall in dollars per FEU: 2023 voyage cost, then the change from fuel price, Cape share, EU ETS, FuelEU and war risk, to today's capacity-weighted cost.",
                  "ch2" + ("w" if wide else "n"))]
    o.append('<text class="ael-t" x="12" y="22">Voyage cost per FEU, Shanghai → Rotterdam, $</text>')
    o.append('<text class="ael-m" x="12" y="38">fuel, EU ETS, FuelEU and war risk only (no charter, port or canal costs)</text>')
    for t in ticks(0, hi, step):
        o.append(f'<line class="ael-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 4}" y2="{h - 26}"/>'
                 f'<text class="ael-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{int(t)}</text>')
    run = 0.0
    for i, (lab, v, k) in enumerate(W):
        y = top + i * rowh + 6
        if k == "total":
            x0, x1 = X(0), X(v)
            run = v
            txt = num(v)
        else:
            x0, x1 = X(run), X(run + v)
            run += v
            txt = ("+" if v >= 0 else "−") + num(abs(v))
        nm = lab if wide else lab.replace(", 2023 → today", "").replace(" (max penalty)", " (max)").replace(", capacity-weighted", "").replace(" of capacity", "").replace(", change", "")
        o.append(f'<text class="ael-l" x="{left - 8}" y="{y + 15}" text-anchor="end"{" font-weight=\"600\"" if k == "total" else ""}>{esc(nm)}</text>')
        if k == "total":
            o.append(f'<path class="{cls[k]}" d="{bar_path(x0, x1, y, 20)}"><title>{esc(lab)}: {num(v)} $/FEU</title></path>')
        else:
            a, b = min(x0, x1), max(x0, x1)
            o.append(f'<rect class="{cls[k]}" x="{a:.1f}" y="{y}" width="{max(b - a, 1):.1f}" height="20" rx="2"><title>{esc(lab)}: {txt} $/FEU</title></rect>')
            if i + 1 < len(W):
                o.append(f'<line class="ael-k0" x1="{X(run):.1f}" x2="{X(run):.1f}" y1="{y + 20}" y2="{y + rowh + 6}" stroke-dasharray="2 2"/>')
        o.append(f'<text class="ael-m" x="{max(x0, x1) + 5:.1f}" y="{y + 14}">{txt}</text>')
    o.append("</svg>")
    return "".join(o)


def chart_rate(V, wide=True):
    T = V["T"]
    rows = [("Nov 2023", V["wci_2023"], T["2023"]["feu"]), ("Nov 2026", V["wci_rtm"], T["today"]["feu"])]
    w = 680 if wide else 360
    left = 80 if wide else 70
    right = 50 if wide else 40
    top = 58 if wide else 76
    rowh = 52
    h = top + rowh * 2 + 32
    hi = 1000 * (-(-max(r[1] for r in rows) // 1000))
    X = lambda v: left + v / hi * (w - left - right)
    o = [svg_open(w, h, "Freight rate versus voyage cost per FEU",
                  "Drewry WCI Shanghai–Rotterdam split into the voyage cost items computed in this report and the rest of the rate.",
                  "ch3" + ("w" if wide else "n"))]
    o.append('<text class="ael-t" x="12" y="22">WCI Shanghai → Rotterdam, $/FEU, and what the cost stack explains</text>' if wide else
             '<text class="ael-t" x="12" y="22">WCI Shanghai → Rotterdam, $/FEU</text>')
    legend(o, [("fuel", "box", "ael-s2"), ("EU ETS + FuelEU", "box", "ael-s1"), ("war risk", "box", "ael-s3"),
               ("rest of the rate", "box", "ael-s5")], 12, 36, w, wide)
    for t in ticks(0, hi, 1000):
        o.append(f'<line class="ael-g" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 6}" y2="{h - 26}"/>'
                 f'<text class="ael-m" x="{X(t):.1f}" y="{h - 10}" text-anchor="middle">{num(t)}</text>')
    for i, (lab, rate, c) in enumerate(rows):
        y = top + i * rowh + 8
        o.append(f'<text class="ael-l" x="{left - 8}" y="{y + 17}" text-anchor="end">{lab}</text>')
        segs = [("fuel", c["fuel"], "ael-s2"), ("EU ETS + FuelEU", c["ets"] + c["fueleu"], "ael-s1"),
                ("war risk", c["war"], "ael-s3"), ("rest of the rate", rate - c["total"], "ael-s5")]
        x0 = 0.0
        for k, (nm, v, cl) in enumerate(segs):
            if v <= 0:
                continue
            a, b = X(x0) + (1 if k else 0), X(x0 + v)
            last = k == len(segs) - 1
            dp = bar_path(a, b, y, 24) if last else f'M{a:.1f},{y}H{max(a + 0.8, b - 1):.1f}V{y + 24}H{a:.1f}Z'
            o.append(f'<path class="{cl}" d="{dp}"><title>{lab}: {nm} {num(v)} $/FEU</title></path>')
            x0 += v
        o.append(f'<text class="ael-m" x="{X(rate) + 5:.1f}" y="{y + 16}">{num(rate)}</text>')
        o.append(f'<text class="ael-m" x="{X(0)}" y="{y + 38}">cost items {num(c["total"])} = {num(c["total"] / rate * 100)}% of the rate</text>')
    o.append("</svg>")
    return "".join(o)


def chart_cong(V, wide=True):
    C = V["cong"]
    w = 680 if wide else 360
    left = 130 if wide else 96
    right = 48 if wide else 40
    rowh = 34 if wide else 36
    top = 66 if wide else 84
    h = top + rowh * len(C) + 34
    vals = [c["c30var"] for c in C if c["c30var"] is not None] + [c["proxy"] for c in C if c["proxy"] is not None]
    lo, hi = min(-30, min(vals) - 6), max(30, max(vals) + 6)
    step = 10 if wide else 20
    lo, hi = step * (lo // step), step * (-(-hi // step))
    X = lambda v: left + (v - lo) / (hi - lo) * (w - left - right)
    o = [svg_open(w, h, "Congestion and disruption proxies, container gateways",
                  "Container calls, 30-day mean vs a year earlier, and all calls, last 7 days vs the previous 28 days.", "ch4" + ("w" if wide else "n"))]
    o.append('<text class="ael-t" x="12" y="22">Container gateways: change in port calls, %</text>')
    legend(o, [("container calls, 30 days vs a year earlier", "box", "ael-s2"),
               ("all calls, 7 days vs previous 28 days", "box", "ael-s3")], 12, 34, w, wide)
    for t in ticks(lo, hi, step):
        x = X(t)
        o.append(f'<line class="{"ael-z" if t == 0 else "ael-g"}" x1="{x:.1f}" x2="{x:.1f}" y1="{top - 8}" y2="{h - 26}"/>')
        lab = "0" if t == 0 else f"{int(t):+d}".replace("-", "−")
        o.append(f'<text class="ael-m" x="{x:.1f}" y="{h - 10}" text-anchor="middle">{lab}</text>')
    lastreg = None
    for i, c in enumerate(C):
        y = top + i * rowh
        if c["region"] != lastreg and i:
            o.append(f'<line class="ael-z" x1="12" x2="{w - 12}" y1="{y - 2}" y2="{y - 2}" stroke-dasharray="3 3"/>')
        lastreg = c["region"]
        o.append(f'<text class="ael-l" x="{left - 8}" y="{y + 17}" text-anchor="end">{esc(c["name"])}</text>')
        for j, (k, cl) in enumerate([("c30var", "ael-s2"), ("proxy", "ael-s3")]):
            v = c[k]
            if v is None:
                continue
            yy = y + 4 + j * 13
            o.append(f'<path class="{cl}" d="{bar_path(X(0), X(v), yy, 11)}"><title>{esc(c["name"])}: {pct(v)}</title></path>')
            tx = X(v) + (4 if v >= 0 else -4)
            o.append(f'<text class="ael-m" x="{tx:.1f}" y="{yy + 9.5}" text-anchor="{"start" if v >= 0 else "end"}">{pct(v, 0)}</text>')
    o.append("</svg>")
    return "".join(o)


def table_html(head, rows):
    return ('<div class="tabella"><table><thead><tr>' + "".join(f'<th scope="col">{esc(x)}</th>' for x in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")


def chart_tables(V):
    T = V["T"]
    return {
        "lanes": table_html(["Lane", "nm 2023 / today", "Days via Suez", "Days via Cape", "Weighted today"],
                            [[f"{l['from']} → {l['to']}", f"{num(l['nm_base'])} / {num(l['nm_today'])}", num(l["d_today"], 1),
                              num(l["d_cape"], 1), num(l["d_w"], 1)] for l in V["lanes"]]),
        "waterfall": table_html(["Step", "$/FEU"], [[a, num(b, 1)] for a, b, _ in V["W"]]),
        "rate": table_html(["", "WCI $/FEU", "Cost items $/FEU", "Share"],
                           [["Nov 2023", num(V["wci_2023"]), num(T["2023"]["feu"]["total"], 1), f"{num(T['2023']['feu']['total'] / V['wci_2023'] * 100)}%"],
                            ["Nov 2026", num(V["wci_rtm"]), num(T["today"]["feu"]["total"], 1), f"{num(T['today']['feu']['total'] / V['wci_rtm'] * 100)}%"]]),
        "cong": table_html(["Port", "Container calls/day, 30 d", "Year earlier", "Change", "7 d vs previous 28 d"],
                           [[c["name"], num(c["c30"], 1), num(c["c30p"], 1), pct(c["c30var"]), pct(c["proxy"])] for c in V["cong"]]),
    }


# =====================================================================================
# Text blocks
# =====================================================================================
def blocks(V, edition):
    B = []
    T, ci, R = V["T"], V["cost_in"], V["R"]
    sh, sg = R[("shanghai", "rotterdam")], R[("singapore", "rotterdam")]
    share = V["share"]
    S, Cp = round(share * 100), round((1 - share) * 100)
    pw = V["pw"]
    hz, bab, sz, cape = pw["Strait of Hormuz"], pw["Bab el-Mandeb"], pw["Suez Canal"], pw["Cape of Good Hope"]
    L = {l["key"]: l for l in V["lanes"]}
    lr = L[("shanghai", "rotterdam")]
    t23, tw, ts, tc = T["2023"], T["today"], T["suez"], T["cape"]
    up = var(tw["feu"]["total"], t23["feu"]["total"])
    rate_up = V["wci_rtm"] - V["wci_2023"]
    cost_up = tw["feu"]["total"] - t23["feu"]["total"]
    be_ = V["breakeven"]
    E1, E2 = EXTERNAL["vlsfo_sg_2023"], EXTERNAL["wci_sh_rtm_2023"]
    risk = V["risk"]
    rs_c = risk["mar-rosso-container"]
    pr = V["pr"]
    rtm, ant = V["pr_by"]["rotterdam"], V["pr_by"]["antwerp-bruges"]
    ex_ = V["baltic_extra"]
    maersk = V["maersk"]
    ems = maersk["valori_usd_per_feu"]["Estremo Oriente -> Nord Europa"]
    ets_fe_w = tw["feu"]["ets"] + tw["feu"]["fueleu"]
    rail1 = {v["voce"]: v for v in V["rail"]["FR-COR-01"]["volumi"]}
    rail2 = {v["voce"]: v for v in V["rail"]["FR-COR-02"]["volumi"]}
    rail3 = {v["voce"]: v for v in V["rail"]["FR-COR-03"]["volumi"]}
    teu25 = rail1["TEU trasportati nel 2025"]["valore"]
    sz_teu = V["F"]["stretti-dettaglio.json"]
    suez_el = next(e for e in sz_teu["elementi"] if e["id"] == "suez")
    bimco = next(f for f in suez_el["flussi"] if f["voce"] == "Container")
    need(bimco["valore"], "753.000", "1.457.000", where="stretti-dettaglio suez container")
    teu_week_suez = 753000
    sanc = V["sanc"]
    gof = V["navi_areas"]["Golfo di Finlandia"]
    dk = V["navi_areas"]["Stretti danesi"]

    # ---------------------------------------------------------------- 1. key points
    B.append(("h2", "key-points", "1. Key points"))
    B.append(("ul", [
        f"**Suez is back for {S}% of Asia–Europe container capacity; the rest still sails round the Cape.** A Shanghai–Rotterdam voyage takes "
        f"{num(lr['d_today'], 1)} days at sea via Suez and {num(lr['d_cape'], 1)} via the Cape, so today's mix averages {num(lr['d_w'], 1)} days "
        f"(Alphaliner via {dl('transit-times.json')}, October 2026; model at 15 knots). Hormuz is de facto closed: "
        f"{num(hz['transits_7d_avg'], 1)} transits a day against {num(hz['transits_7d_avg_3y_ago'], 1)} three years ago (IMF PortWatch, week to {date_en(hz['date'])}).",
        f"**The cost of moving one box from Shanghai to Rotterdam has risen by about {num(up, 0)}% since late 2023.** Fuel, EU ETS, FuelEU and war risk "
        f"come to about {num(tw['feu']['total'])} $ per 40-foot container (FEU) today against {num(t23['feu']['total'])} $ in 2023. "
        f"The largest single increase is the fuel price (+{num(V['W'][1][1])} $/FEU), not the detour (+{num(V['W'][2][1])} $/FEU) "
        f"(calculation in section 3; fuel price of {date_en(ci['p_date'])}, carbon price of {date_en(ci['eua_date'])}).",
        f"**Freight rates have risen far more than these costs.** The Drewry WCI Shanghai–Rotterdam is {num(V['wci_rtm'])} $/FEU ({date_en(V['wci_date'])}), "
        f"against {num(V['wci_2023'])} $ on {date_en(E2['date'])}: +{num(rate_up)} $, of which the cost items explain about {num(cost_up)} $ "
        f"({num(cost_up / rate_up * 100)}%). Capacity and demand, not fuel or carbon, set the rate.",
        f"**No North Sea or Baltic port is at high risk; Rotterdam and Antwerp-Bruges carry the most impact.** Both score {num(rtm['score'], 1)} of 25 "
        f"(medium) on the monitor's Port Risk Index: impact {num(rtm['impact'], 1)} of 5, probability {num(rtm['probability'], 1)} ({dl('port-risk.json')}, "
        f"{date_en(pr['reference_date'])}). The highest scores are the Russian Gulf of Finland ports, at {num(V['ports_ru'][0]['score'], 1)}.",
        f"**For Q1 2027 the signal to watch is the Red Sea war-risk premium, not Suez traffic.** In this model the Cape becomes cheaper than Suez "
        f"when the premium passes about {num(be_['pct_toll'][0], 2)}–{num(be_['pct'], 2)}% of hull value, depending on the canal toll. "
        f"The last public quote is {num(V['prem_last']['mar-rosso']['min'], 1)}–{num(V['prem_last']['mar-rosso']['max'], 1)}% "
        f"({date_en(V['prem_last']['mar-rosso']['data'])}, {dl('assicurazioni.json')}).",
    ]))
    B.append(("val", "*Assessment.* For Dutch, Danish and Baltic logistics the corridor is now a cost problem more than a capacity problem. "
                     "Ships are getting through, but each box carries a higher fuel bill and a new carbon bill. The schedule mix "
                     f"({S}/{Cp}) still adds about {num(lr['d_w'] - lr['d_today'], 1)} days on average, and it could flip back within weeks if the "
                     "Red Sea relapses. The full return to Suez expected by Q1 2027 would lower costs, but it would also bring back the bunching "
                     "of arrivals at North Sea hubs seen when routings change."))

    # ---------------------------------------------------------------- 2. route map
    B.append(("h2", "routes", f"2. The route map today: Suez back for {S}% of capacity, Cape for the rest, Hormuz closed"))
    B.append(("p", f"**Passages, {date_en(V['passages']['Suez Canal']['date'])}.** Suez is «{V['passages']['Suez Canal']['level']}»; "
                   f"Bab el-Mandeb «{V['passages']['Bab el-Mandeb']['level']}»; Hormuz «{V['passages']['Strait of Hormuz']['level']}» "
                   f"({dl('stretti-dettaglio.json')}, via {dl('transit-times.json')}). IMF PortWatch counts transits of ships with AIS on "
                   f"(the Automatic Identification System, the ship's position transponder). In the week to {date_en(sz['date'])}: "
                   f"Suez {num(sz['transits_7d_avg'], 1)} a day ({pct(sz['var_vs_1y_pct'])} on a year earlier, {pct(sz['var_vs_3y_pct'])} on three years earlier); "
                   f"Bab el-Mandeb {num(bab['transits_7d_avg'], 1)} ({pct(bab['var_vs_3y_pct'])} on three years); "
                   f"Cape of Good Hope {num(cape['transits_7d_avg'], 1)} ({pct(cape['var_vs_3y_pct'])}); Hormuz {num(hz['transits_7d_avg'], 1)} "
                   f"({pct(hz['var_vs_3y_pct'])})."))
    B.append(("p", f"**The {S}/{Cp} split.** {S}% of Far East–Europe container capacity was on Red Sea services in October 2026 (Alphaliner); "
                   f"Linerlytica expects a full return by Q1 2027 ([Seatrade Maritime](https://www.seatrade-maritime.com/containers/full-suez-return-for-container-carriers-expected-by-q1-2027), "
                   f"in {dl('stretti-dettaglio.json')}, reliability medium). BIMCO counts 753,000 TEU a week through Suez in the first two weeks of October 2026, "
                   f"against 1,457,000 in the same weeks of 2023 ([BIMCO](https://www.bimco.org/news-insights/market-analysis/shipping-number-of-the-week/2026/1014-snow/), "
                   f"14 October 2026). The report uses the {S}% share as the weight of Suez routings for all Asia–Europe lanes, as the transit model does."))
    B.append(("fig", "lanes", f"**Days at sea by lane.** Sea time only at 15 knots (no canal queue, port time or bunkering stops). Dot: route via Suez, the 2023 "
                              f"routing and today's Suez services; diamond: via the Cape; bar: capacity-weighted average with {S}% via Suez. "
                              f"Jebel Ali loads at Khor Fakkan today (land bridge), so its Suez point is the sea leg from there. Source: "
                              f"{dl('transit-times.json')} (routes on Benden shipping lanes, Dijkstra shortest path), updated {V['tt']['updated'][:10]}."))
    cv = [r["error_pct"] for r in V["validation"]["rows"] if "Cape" in r["pair"] and "published_nm" in r]
    rows = []
    for l in V["lanes"]:
        rows.append([f"{l['from']} → {l['to']}", f"{num(l['nm_base'])}", f"{num(l['nm_today'])}" if l["nm_today"] != l["nm_base"] else "same",
                     num(l["d_today"], 1), f"{num(l['nm_cape'])} nm, {num(l['d_cape'], 1)} d", f"+{num(l['d_cape'] - l['d_today'], 1)}", num(l["d_w"], 1)])
    B.append(("tab", ["Lane", "nm 2023", "nm today", "Days via Suez", "Via the Cape", "Cape penalty, days", f"Weighted today ({S}% Suez)"], rows,
              f"Nautical miles (nm) and days from {dl('transit-times.json')}. «2023» is the routing with every passage open; the Suez route today is the same, except "
              f"from Jebel Ali. The model's distances are within {num(V['validation']['max_abs_error_nm_pct'], 1)}% of published references; "
              f"the Cape route is overstated by {num(min(cv), 1)}–{num(max(cv), 1)}%, so Cape penalties are slightly too high (validation in the same file)."))
    B.append(("p", f"**North versus south.** The Cape penalty is {num(V['med_cape_penalty']['rotterdam'], 1)} days to Rotterdam but "
                   f"{num(V['med_cape_penalty']['genoa'], 1)} to Genoa, {num(V['med_cape_penalty']['trieste'], 1)} to Trieste and "
                   f"{num(V['med_cape_penalty']['piraeus'], 1)} to Piraeus. Gdańsk and Klaipėda sit {num(ex_['gdansk'])} and {num(ex_['klaipeda'])} nm "
                   f"beyond Rotterdam on the same voyage ({num(V['baltic_extra_days']['gdansk'], 1)} and {num(V['baltic_extra_days']['klaipeda'], 1)} more days), "
                   f"and pass the Danish straits."))
    rt, yb, lf = V["rt"], V["yanbu"], V["laffan"]
    B.append(("p", f"**Hormuz.** Qatari LNG to Rotterdam is «{lf['status']}»: Qatar has no export terminal outside the Gulf. "
                   f"Saudi crude piped to Yanbu reaches Rotterdam in {num(rt['days_today'], 1)} days, against {num(rt['days_base'], 1)} from Ras Tanura "
                   f"via Hormuz, but Yanbu carries a war-risk premium of {num(rt['war_risk_items'][0]['pct_hull'], 1)}% of hull value for Saudi-linked ships "
                   f"({rt['war_risk_items'][0]['source']}). Jebel Ali boxes are trucked to Khor Fakkan on the Gulf of Oman; the sea leg to Rotterdam is "
                   f"{num(V['jebel']['days_today'], 1)} days ({dl('transit-times.json')})."))
    B.append(("val", "*Assessment.* The return to Suez helps the Mediterranean about twice as much as the North Sea, because the Cape penalty to Genoa or "
                     f"Piraeus is {num(V['med_cape_penalty']['genoa'], 0)}–{num(V['med_cape_penalty']['piraeus'], 0)} days against about {num(V['med_cape_penalty']['rotterdam'], 0)} to Rotterdam. "
                     "For Rotterdam, Antwerp, Hamburg and the Baltic feeders the routing question is "
                     f"mainly one of schedule reliability: services are being moved between two routes that differ by {num(lr['d_cape'] - lr['d_today'], 0)} days."))

    # ---------------------------------------------------------------- 3. cost stack
    jul = [v for dd, v in V["rs_series"] if dd.startswith("2026-07") and v >= 0.5] or [0]
    B.append(("h2", "costs", "3. Cost stack of an Asia–North Europe voyage, today against 2023"))
    B.append(("p", f"One voyage Shanghai → Rotterdam with a container ship of about 15,000 TEU (twenty-foot equivalent units), at {num(ci['speed'])} knots, "
                   f"burning {num(ci['fd'])} t of very-low-sulphur fuel oil (VLSFO) a day and carrying {num(ci['units'])} FEU "
                   f"(15,000 TEU × 85% utilisation ÷ 2). Hull value {musd(ci['hull'], 0)}. These are the transit model's declared hypotheses "
                   f"({dl('transit-times.json')}), not the data of a real ship. Four scenarios: **2023** (Suez, 2023 fuel price, no carbon rules, "
                   f"pre-crisis war risk), **today via Suez**, **today via the Cape**, and **today weighted** {S}/{Cp}."))
    B.append(("h3", "The calculation"))
    B.append(("ul", [
        f"**Fuel** = sea days × {num(ci['fd'])} t/day × VLSFO price. Suez {num(ts['days'], 1)} d → {num(ts['fuel_t'])} t; Cape {num(tc['days'], 1)} d → {num(tc['fuel_t'])} t. "
        f"Price today: Singapore {num(ci['p_now'], 1)} $/t ({date_en(ci['p_date'])}, Ship & Bunker in {dl('bunker-emissioni.json')}). "
        f"Price 2023: {num(ci['p_2023'], 1)} $/t, {E1['text']} ([{E1['source']}]({E1['link']}), reliability {E1['reliability']}: {E1['read']}). "
        f"Fuel today via Suez: {num(ts['fuel_t'])} × {num(ci['p_now'], 1)} = {musd(ts['fuel'])}.",
        f"**EU ETS** (the EU Emissions Trading System, which since 2024 makes ships buy allowances for their emissions). It covers 50% of the last voyage into "
        f"the EU from a non-EU port; a call at Tanger Med or East Port Said does not break the voyage. Assumption: the last non-EU call is Singapore, so the "
        f"covered leg is Singapore → Rotterdam, {num(ts['cov_days'], 1)} d via Suez ({num(ts['cov_t'])} t) or {num(tc['cov_days'], 1)} d via the Cape ({num(tc['cov_t'])} t). "
        f"Cost per tonne burnt: 3.1631 t CO2e × 50% × 100% phase-in (2026) × {num(ci['eua'], 2)} €/allowance (EEX auction, {date_en(ci['eua_date'])}) = "
        f"{num(ci['ets_t_eur'], 2)} €/t, or {num(ci['ets_t_eur'] * ci['eurusd'], 2)} $/t at {num(ci['eurusd'], 4)} $/€. Via Suez: {musd(ts['ets'])}. "
        f"In 2023 maritime ETS did not exist (in force from 1 January 2024).",
        f"**FuelEU Maritime** (the EU rule capping the greenhouse-gas intensity of ship fuel, in force since 2025). For VLSFO the 2026 limit is exceeded, and the "
        f"maximum cost is the penalty: {num(ci['fueleu_t_eur'], 2)} €/t on the same 50% leg ({dl('bunker-emissioni.json')}, example «asia-rotterdam»). "
        f"Via Suez: {musd(ts['fueleu'])}. Pooling or bio-blends can cost less; zero in 2023.",
        f"**War risk** = premium × hull value. Today via Suez: {num(ci['war_today_pct'], 2)}% × {musd(ci['hull'], 0)} = {musd(ts['war'])} "
        f"(midpoint of {ci['war_src']}). Via the Cape: no listed area on the route, so zero. 2023: {num(ci['war_base_pct'], 3)}%, the pre-crisis level "
        f"(less than 0.1% in late 2023, Moody's via {dl('assicurazioni.json')}) = {musd(t23['war'])}.",
        f"**Per FEU** = voyage cost ÷ {num(ci['units'])} FEU. **Weighted** = {S}% × Suez + {Cp}% × Cape.",
    ]))
    rows = []
    for lab, k in [("Fuel", "fuel"), ("EU ETS", "ets"), ("FuelEU (max penalty)", "fueleu"), ("War risk", "war"), ("Total", "total")]:
        rows.append([lab] + [f"{musd(T[s][k])} · {num(T[s]['feu'][k])} $" for s in ("2023", "suez", "cape", "today")])
    B.append(("tab", ["Item (per voyage · per FEU)", "2023 via Suez", "Today via Suez", "Today via the Cape", f"Today weighted {S}/{Cp}"], rows,
              f"Calculated by report/build_logistics.py from {dl('transit-times.json')}, {dl('bunker-emissioni.json')} and {dl('assicurazioni.json')}; "
              f"2023 fuel price from outside the repository (see above). Not included: charter hire of the extra days, Suez Canal tolls "
              f"(about {musd(be_['toll'][0], 1)}–{musd(be_['toll'][1], 1)} per transit according to the transit model's notes), port and terminal costs, "
              f"cargo inventory cost. These are the costs that changed most, not the full cost of a voyage."))
    B.append(("fig", "waterfall", f"**From 2023 to today, $ per FEU.** Shanghai → Rotterdam, capacity-weighted {S}/{Cp}. Steps: fuel price on the Suez voyage "
                                  f"({num(ci['p_2023'], 1)} → {num(ci['p_now'], 1)} $/t); extra Cape fuel for {Cp}% of capacity; EU ETS and FuelEU on the covered leg; "
                                  f"change in war risk. Sources and calculation in the table above; data of {date_en(ci['p_date'])} (fuel), {date_en(ci['eua_date'])} (EUA), "
                                  f"{date_en(V['prem_last']['mar-rosso']['data'])} (war risk), {date_en(E1['date'])} (2023 fuel)."))
    B.append(("p", f"**Reading.** The stack rises from {num(t23['feu']['total'])} to {num(tw['feu']['total'])} $/FEU ({pct(up, 0)}). Fuel price adds "
                   f"{num(V['W'][1][1])} $, the Cape share {num(V['W'][2][1])} $, carbon rules {num(V['W'][3][1] + V['W'][4][1])} $ together, war risk "
                   f"{num(V['W'][5][1])} $. Since the eve of the Iran war, the Suez voyage's fuel bill alone has grown by "
                   f"{musd(ts['fuel_t'] * (ci['p_now'] - ci['p_prewar']))} (Singapore VLSFO {num(ci['p_prewar'], 1)} $/t on {date_en(ci['prewar_date'])}), the same figure "
                   f"as in {dl('transit-times.json')}."))
    B.append(("p", f"**When does the Cape pay?** Via the Cape the voyage costs {musd(be_['extra'])} more in fuel, ETS and FuelEU than via Suez. The Cape avoids the Red "
                   f"Sea premium and the canal toll. Without the toll, the break-even premium is {num(be_['pct'], 2)}% of a {musd(ci['hull'], 0)} hull; with a toll of "
                   f"{musd(be_['toll'][0], 1)}–{musd(be_['toll'][1], 1)} it falls to {num(be_['pct_toll'][0], 2)}–{num(be_['pct_toll'][1], 2)}%. "
                   f"{dl('assicurazioni.json')} finds 0.32% for a new 221.7 M$ ship, using UNCTAD's 2024 extra Cape cost of 0.7 M$: a different ship value and "
                   f"cost base, shown here rather than reconciled."))
    B.append(("val", "*Assessment.* Carriers decide the route on the whole voyage economics (charter cost of ten more days, schedule, crew safety), not on "
                     f"this stack alone. Even so, a Red Sea premium back above about 0.5% would make the Cape competitive again for most "
                     f"large ships, and the July 2026 quotes ({num(min(jul), 2)}–{num(max(jul), 2)}%) were above that line."))

    # ---------------------------------------------------------------- 4. freight
    B.append(("h2", "freight", "4. Freight rates and what drives them"))
    fb = V["fbx_series"]
    fbmax = max(fb, key=lambda x: x[1])
    ccfi = V["ccfi"]["rotte"]
    B.append(("tab", ["Index", "Value", "Date", "Note"], [
        ["Drewry WCI Shanghai–Rotterdam", f"{num(V['wci_rtm'])} $/FEU", date_en(V["wci_date"]), f"{num(V['wci_2023'])} $ on {date_en(E2['date'])} (secondary source)"],
        ["Drewry WCI Shanghai–Genoa", f"{num(V['wci_goa'])} $/FEU", date_en(V["wci_date"]), f"premium over Rotterdam {pct(V['genoa_premium'])}"],
        ["Freightos FBX11 China–North Europe", f"{num(V['fbx11']['valore'])} $/FEU", date_en(V["fbx"]["data"]), f"{V['fbx11']['var'].replace('-', '−')} on the week"],
        ["Freightos FBX13 China–Mediterranean", f"{num(V['fbx13']['valore'])} $/FEU", date_en(V["fbx"]["data"]), f"{V['fbx13']['var'].replace('-', '−')} on the week"],
        ["Freightos FBX global", f"{num(V['fbx']['valore'], 1)} $/FEU", date_en(V["fbx"]["data"]), f"{pct(var(V['fbx']['valore'], fbmax[1]))} since {date_en(fbmax[0])} ({num(fbmax[1], 1)}), the high of the series kept since then"],
        ["CCFI Europe", f"{num(ccfi['EUROPE']['valore'], 2)} points", date_en(V["ccfi"]["data"]), f"{pct(ccfi['EUROPE']['var_pct'], 2)} on the week"],
        ["Maersk emissions surcharge, Far East → North Europe", f"{num(ems)} $/FEU", "Q4 2026", f"based on an average EUA of {num(maersk['eua_medio_usato_eur'], 2)} € over {it_period(maersk['periodo_eua'])}"],
    ], f"Freight indices from {dl('noli.json')} (Drewry, Freightos/Baltic Exchange, Shanghai Shipping Exchange; © the publishers, values cited). WCI and FBX "
       f"measure spot rates with different methods and dates, so they differ by {num(abs(V['wci_rtm'] - V['fbx11']['valore']))} $ on the same lane. "
       f"Surcharge from {dl('bunker-emissioni.json')} ([Maersk]({maersk['link']}), {date_en(maersk['data_fonte'])})."))
    B.append(("fig", "rate", f"**How much of the freight rate the cost stack explains.** Drewry WCI Shanghai–Rotterdam on {date_en(E2['date'])} "
                             f"(secondary source, reliability medium) and {date_en(V['wci_date'])} ({dl('noli.json')}), split into the cost items of section 3 "
                             f"(capacity-weighted today) and the rest, which covers charter, port, canal, overheads and margin. Carrier costs and spot prices are "
                             f"different things: the split is an order of magnitude."))
    B.append(("p", f"**What drives the rate.** (1) *Capacity released by the Suez return.* Each ship moved back from the Cape to Suez saves about "
                   f"{num(V['med_cape_penalty']['rotterdam'], 1)} days each way, so the same fleet offers more weekly slots. (2) *Fuel.* Singapore VLSFO is "
                   f"up {pct(V['vlsfo_sg']['var_da_prima_guerra_pct'], sign=False)} since {date_en(V['vlsfo_sg']['data_prima_guerra'])} and {pct(V['vlsfo_sg']['var_1a_pct'], sign=False)} on a year earlier "
                   f"({dl('bunker-emissioni.json')}). (3) *Carbon.* Maersk charges {num(ems)} $/FEU from the Far East to North Europe for ETS and FuelEU; the "
                   f"model's own ETS + FuelEU cost is {num(ets_fe_w)} $/FEU at today's EUA. A surcharge is a price, not a cost: it can include other lanes, "
                   f"feeder legs and a margin. (4) *War risk*, now {num(tw['feu']['war'])} $/FEU in the weighted case. (5) *The Mediterranean premium*: "
                   f"Shanghai–Genoa costs {pct(V['genoa_premium'], sign=False)} more than Shanghai–Rotterdam, inside the 5–20% band the risk dashboard reads as "
                   f"«gradual return under threat» ({dl('rischio.json')}, {date_en(V['risk_date'])})."))
    B.append(("val", "*Assessment.* Spot rates are drifting down (FBX global from its August high, FBX11 down on the week) while the CCFI, which weights "
                     f"contract rates, edges up. The cost floor computed here, about {num(round(tw['feu']['total'], -1))} $/FEU for fuel, carbon and war risk, is "
                     f"{num(tw['feu']['total'] / V['wci_rtm'] * 100)}% of today's WCI. That leaves room for spot rates to fall as Cape capacity returns. Fuel would have to rise sharply to stop that."))

    # ---------------------------------------------------------------- 5. ports
    B.append(("h2", "ports", "5. Ports: risk ranking for the North Sea, the Baltic and the Mediterranean"))
    B.append(("p", f"The **Port Risk Index** scores 39 ports every day: probability of disruption (1–5: traffic, security events, exposure to disrupted chokepoints, "
                   f"war-risk listing) × impact on European supply chains (1–5: strategic role, cargo handled, energy cost) = 1–25. Low below 6, medium 6–11.9, "
                   f"high 12–19.9, critical 20 and above. It is a rule-based assessment, not a forecast (method in report/port-risk-method.md; {dl('port-risk.json')}, "
                   f"{date_en(pr['reference_date'])}; PortWatch calls to {date_en(V['ports_date'])})."))
    rows = [[short(p["name"]), p["country"], num(p["probability"], 1), num(p["impact"], 1), num(p["score"], 1), p["level"], f"{p['trend']} ({num(p['score_7d_ago'], 1)})"]
            for p in V["ports_ns"]]
    B.append(("tab", ["North Sea and Baltic (non-Russian)", "Country", "P", "I", "Score", "Level", "Trend (7 days ago)"], rows,
              f"{dl('port-risk.json')}. The 7-day-ago score is reconstructed for this first week. Russian ports: "
              + "; ".join(f"{short(p['name'])} {num(p['score'], 1)}" for p in V["ports_ru"]) + " (impact capped at 3 by rule)."))
    rows = [[short(p["name"]), num(p["probability"], 1), num(p["impact"], 1), num(p["score"], 1), p["level"], f"{p['trend']} ({num(p['score_7d_ago'], 1)})"]
            for p in V["ports_it"]]
    B.append(("tab", ["Mediterranean (Italian ports only)", "P", "I", "Score", "Level", "Trend (7 days ago)"], rows,
              f"{dl('port-risk.json')}. **Missing:** the index scores no non-Italian Mediterranean port (Piraeus, Valencia, Algeciras, Tanger Med, Koper)."))
    mv = V["moved"]
    B.append(("p", "**What changed in a week** (score moves of 0.5 or more): " + "; ".join(
        f"{short(p['name'])} {num(p['score_7d_ago'], 1)} → {num(p['score'], 1)}" for p in mv) + ". "
        f"Rotterdam and Antwerp-Bruges rank high on impact ({num(rtm['impact'], 1)}) and low on probability: Rotterdam's only amber is "
        f"«{rtm['ind']['Exposure to disrupted chokepoints']['text']}»."))
    dkp = [V["pr_by"][k] for k in ("copenhagen-malmo", "esbjerg", "aarhus")]
    B.append(("p", "**Denmark.** " + ", ".join(f"{short(p['name'])} {num(p['score'], 1)}" for p in dkp) +
              f": all low. Esbjerg rose from {num(dkp[1]['score_7d_ago'], 1)}: «{dkp[1]['ind']['Short-term disruption proxy: 7-day calls vs the previous 28 days']['text'].replace('-', '−')}». "
              "It is an offshore-wind base, not a container gateway."))
    B.append(("fig", "cong", f"**Congestion proxies for the container gateways.** Blue: container calls a day, 30-day mean against the same days a year earlier; "
                             f"amber: all calls, last 7 days against the previous 28, the index's short-term disruption proxy. Above the dashed line: North Sea "
                             f"and Baltic; below: Italy. Source: IMF PortWatch via {dl('porti-nord.json')}, {dl('portwatch.json')} and {dl('port-risk.json')}, "
                             f"data to {date_en(V['ports_date'])}."))
    c = {x["name"]: x for x in V["cong"]}
    B.append(("p", f"**Reading.** Over 30 days, container calls are {pct(c['Rotterdam']['c30var'])} at Rotterdam and {pct(c['Antwerp-Bruges']['c30var'])} at "
                   f"Antwerp-Bruges, but {pct(c['Bremerhaven']['c30var'])} at Bremerhaven and {pct(c['Gdańsk']['c30var'])} at Gdańsk. The last week is below the "
                   f"previous four at most northern hubs (Rotterdam {pct(c['Rotterdam']['proxy'])}, Hamburg {pct(c['Hamburg']['proxy'])}, Bremerhaven "
                   f"{pct(c['Bremerhaven']['proxy'])}), while the Italian gateways are flat or up. A fall in calls is what congestion, strikes, weather or weaker "
                   f"demand all look like in AIS data. **Missing:** vessel waiting times and berth occupancy: no free source is in the repository."))
    pxs = [abs(c[n]["proxy"]) for n in ("Rotterdam", "Hamburg", "Bremerhaven")]
    B.append(("val", f"*Assessment.* A drop of {num(min(pxs))}–{num(max(pxs))}% in a week at three North Sea hubs at once is more likely a schedule effect than port trouble. Ships "
                     "switching from the Cape to Suez arrive in a different order, and blank sailings follow. It is worth watching in the next PortWatch "
                     "release: two more weeks below −20% would cross the index's amber line."))

    # ---------------------------------------------------------------- 6. alternatives
    B.append(("h2", "alternatives", "6. Alternatives: rail, air and nearshoring"))
    B.append(("p", f"**China–Europe rail.** {num(rail1['treni nel 2025']['valore'])} trains in 2025 ({first_pct(rail1['treni nel 2025']['trend'])} on 2024), "
                   f"carrying about {num(teu25 / 1e6, 2)} million TEU ({first_pct(rail1['TEU trasportati nel 2025']['trend'])} on 2024); "
                   f"{num(rail1['treni gennaio-marzo 2026']['valore'])} trains in Q1 2026 ({first_pct(rail1['treni gennaio-marzo 2026']['trend'])} on Q1 2025) "
                   f"([CGTN]({rail1['treni nel 2025']['link']}), [Railmarket]({rail1['TEU trasportati nel 2025']['link']}), "
                   f"[Index1520]({rail1['treni gennaio-marzo 2026']['link']}), in {dl('ferrovie.json')}; TEU figure reliability medium). "
                   f"The northern route crosses Russia and Belarus, with sanctions and border risk at the Belarus–Poland crossing."))
    B.append(("p", f"**Middle Corridor** (Trans-Caspian route via Kazakhstan, the Caspian, Azerbaijan and Georgia): {num(rail2['merci 2025']['valore'], 1)} million tonnes in 2025 "
                   f"(Organisation of Turkic States via [BESA]({rail2['merci 2025']['link']}); other 2025 estimates 4.5–5.2 Mt), target "
                   f"{num(rail2['obiettivo 2030']['valore'], 1)} Mt by 2030 (reliability low). **INSTC** (North–South corridor, Russia–Iran–India): "
                   f"{num(rail3[next(k for k in rail3 if 'traffico' in k)]['valore'], 1)} Mt by rail in 2024; work on the missing Rasht–Astara link has slipped to "
                   f"{rail3['avvio lavori Rasht-Astara']['valore']} ([Interfax]({rail3['avvio lavori Rasht-Astara']['link']}), {date_en(rail3['avvio lavori Rasht-Astara']['data_fonte'])}). "
                   f"It runs through Iran, so it is no alternative for EU shippers under current sanctions."))
    B.append(("val", f"*Assessment.* Rail is a niche for time-sensitive cargo, not a substitute. {num(teu25 / 1e6, 2)} million TEU a year is about "
                     f"{num(teu25 / 52 / 1000)},000 TEU a week, roughly {num(teu25 / 52 / teu_week_suez * 100)}% of the capacity that passed Suez each week in "
                     f"early October 2026. The two figures measure different things: loaded boxes on trains against ship capacity. **Missing:** rail transit "
                     f"times and $/FEU rates for 2026."))
    ams, vel = V["ai_nodes"]["ams"], V["ai_nodes"]["veldhoven"]
    B.append(("p", f"**Air for high-value cargo: chips and lithography.** Every EUV (extreme-ultraviolet) lithography scanner in the world is assembled by ASML at "
                   f"Veldhoven, near Eindhoven; ASML sold 113 new lithography systems in Q3 2026 with revenue of 11.7 billion € "
                   f"([ASML results]({vel['link']}), {date_en(vel['data_fonte'])}). One EUV machine travels as about 40 containers, 20 trucks and three Boeing 747 "
                   f"freighters ([Asia Times]({ams['link']}), 2021, reliability medium); a High-NA EXE:5000 went to Oregon in 43 containers. Schiphol as the departure "
                   f"airport is an assessment: ASML does not publish the airports it uses ({dl('supply-chain-ai.json')}). Chips and AI servers fly because they are "
                   f"light and valuable: AI-related cargo is 40–50% of EVA Air's freight ([DIGITIMES]({V['ai_nodes']['tpe']['link']}), reliability medium). "
                   f"**Missing:** an air-cargo rate series (Asia–Europe $/kg) in the repository."))
    dep = V["dep"]
    mag, gra = dep[("EU", "850511")], dep[("EU", "380110")]
    ip = V["imp_partner"]
    cn_share = {k: next((p["quota"] for p in ip[k]["import_partner"] if p["iso2"] == "CN"), None) for k in ("DE", "NL", "PL")}
    B.append(("p", f"**Dependence that a shorter route does not remove.** EU imports from outside the EU of NdFeB permanent magnets: "
                   f"{num(mag['fornitori'][0]['quota'], 1)}% from China; artificial graphite {num(gra['fornitori'][0]['quota'], 1)}% from China "
                   f"(UN Comtrade {mag['anno']}, {dl('commercio.json')}). China's share of total imports in {ip['DE']['anno']}: Germany {num(cn_share['DE'], 1)}%, "
                   f"Poland {num(cn_share['PL'], 1)}%, the Netherlands {num(cn_share['NL'], 1)}% (same file; Dutch figures include goods re-exported through Rotterdam)."))
    gib = next(e for e in V["F"]["stretti-dettaglio.json"]["elementi"] if e["id"] == "gibilterra")
    tmv = next(f["valore"] for f in gib["flussi"] if f["voce"] == "Container a Tanger Med")
    tm = re.search(r"([\d,]+) milioni di TEU nel 2025 \(([+−-][\d,]+%)\)", tmv)
    if not tm:
        warn("Tanger Med figure not parsed")
    B.append(("val", "*Assessment.* **Nearshoring signals.** The repository holds no data that measures nearshoring directly: no import share series by "
                     "origin over time, no factory-announcement tracker. What it shows is consistent with *hedging*, not relocation: rail volumes up "
                     f"while sea capacity returns, carriers adding Mediterranean transhipment (Tanger Med {tm.group(1).replace(',', '.')} million TEU in 2025, {tm.group(2).replace(',', '.')}, Port Strategy in "
                     f"{dl('stretti-dettaglio.json')}), and dependencies on China for magnets and graphite still above {num(10 * (min(mag['fornitori'][0]['quota'], gra['fornitori'][0]['quota']) // 10))}%. For a logistics employer, the "
                     "practical consequence is more routing options to price, not fewer Asian boxes."))

    # ---------------------------------------------------------------- 7. sanctions
    B.append(("h2", "sanctions", "7. Sanctions and the shadow fleet: compliance risk for shippers and ports"))
    B.append(("p", f"**The lists.** {num(sanc['navi_totali'])} ships are sanctioned by at least one of the US (OFAC, {num(sanc['per_chi']['USA'])}), the UK "
                   f"({num(sanc['per_chi']['Regno Unito'])}) and the EU ({num(sanc['per_chi']['Unione europea'])}); {num(sanc['da_tutti_e_tre'])} by all three. "
                   f"{num(sanc['ambito_russia'])} are linked to Russia and {num(sanc['ambito_iran'])} to Iran; {num(sanc['flotta_ombra_probabile'])} are tankers "
                   f"(or of unknown type) sanctioned for Russia or Iran, which the monitor counts as probable shadow fleet ({dl('sanzioni-navi.json')}: OFAC "
                   f"{date_en(V['sanc_lists_date']['OFAC SDN List'])}, UK {date_en(V['sanc_lists_date']['UK Sanctions List'])}, EU via OpenSanctions "
                   f"{date_en(V['sanc_lists_date']['UE'])}). Of the {num(V['sanc_eu_ru'])} Russia-linked ships on EU lists, most are under the port-access ban "
                   f"of Regulation 833/2014."))
    rec = V["sanc_recent"]
    if rec:
        typ = sorted(set(e.get("tipo_nave") or "type not given" for e in rec))
        rec_txt = (f"{len(rec)} ships, between {date_en(rec[0]['prima_designazione'])} and {date_en(rec[-1]['prima_designazione'])} "
                   f"({', '.join(sorted(set(x for e in rec for x in e['sanzionata_da'])) ).replace('Regno Unito', 'UK').replace('Unione europea', 'EU')}; "
                   f"scope {', '.join(sorted(set(a for e in rec for a in e['ambito'])))}; types: {', '.join(typ)})")
    else:
        rec_txt = "none"
    B.append(("p", f"**Container ships are on the lists too.** {V['sanc_cont']['n']} container ships are sanctioned: {V['sanc_cont']['iran']} linked to Iran and "
                   f"{V['sanc_cont']['russia']} to Russia, all by the US only. A box on one of them can breach US secondary-sanctions rules even when the EU "
                   f"lists do not name the ship. New first designations in the last 90 days: {rec_txt} ({dl('sanzioni-navi.json')})."))
    B.append(("p", f"**Baltic exposure.** In the AIS snapshot of {date_en(V['navi_date'])} {gof['sanzionate']} of {gof['petroliere_viste']} tankers seen in the "
                   f"Gulf of Finland were sanctioned; in the Danish straits {dk['sanzionate']} of {dk['petroliere_viste']} ({dl('navi.json')}). The Port Risk Index "
                   f"counts likely shadow-fleet or sanctioned tankers within 50 km of " + ", ".join(f"{n} ({v})" for n, v, _ in V["shadow_ports"]) +
              f" ({dl('port-risk.json')}). Russia as a whole is a Joint War Committee listed area under {V['jwla']['id']} ({date_en(V['jwla']['data'])})."))
    B.append(("val", "*Assessment.* For shippers and ports in the Netherlands, Denmark and the Baltic the compliance risk sits in three places. "
                     "(1) **Screening by IMO number, not by name**: sanctioned ships change name and flag often, and the flag is frequently false. "
                     "(2) **US-only listings**: the container ships on the lists are almost all US designations for Iran, which an EU-only screening misses. "
                     "(3) **Ship-to-ship transfers and bunkering** near the Gulf of Finland and Skagen, where sanctioned tankers meet others. Ports are "
                     "also exposed operationally: an old, poorly insured tanker at anchor near a cable or a fairway is a spill and liability risk."))

    # ---------------------------------------------------------------- 8. scenarios
    sc = V["risk_sc"]["mar-rosso-container"]
    sig = {s["id"]: s for s in sc["scenari"]}
    def sigs(sid):
        out = []
        for g in sig[sid]["segnali"]:
            v = g["valore"]
            vs = num(v, 1) if isinstance(v, float) and abs(v) < 100 else num(v)
            if "Premio" in g["descrizione"]:
                vs += "%"
            out.append(f"{sig_en(g['descrizione'])} (now {vs}{', met' if g['attivo'] else ''})")
        return "; ".join(out)
    all_suez = ts["feu"]["total"]
    all_cape = tc["feu"]["total"]
    B.append(("h2", "scenarios", "8. Scenarios for Q1 2027"))
    B.append(("val", f"*Assessment.* These scenarios are the monitor's reasoning, without probabilities: each comes with observable thresholds. The first three "
                     f"follow the Red Sea scenarios of the risk dashboard ({dl('rischio.json')}, {date_en(V['risk_date'])}); the cost per FEU uses the section 3 "
                     f"model at today's fuel and EUA prices. Try each case on the [«What if» simulator](../../simulatore.html), which estimates the effect of a "
                     f"slowdown or closure of a passage."))
    B.append(("tab", ["Scenario", "Route mix", "Cost items, $/FEU", "Indicators and thresholds", "Simulator"], [
        ["A. Gradual return under threat (base: the dashboard's current reading, " + f"{sig['mar-rosso-base']['segnali_attivi']} of {sig['mar-rosso-base']['segnali_valutabili']} signals met)",
         f"{S}% Suez, rising slowly", num(tw["feu"]["total"]), sigs("mar-rosso-base"), "[Bab el-Mandeb −25%, 1 month](../../simulatore.html#bab-el-mandeb/r25/1m)"],
        ["B. Full return by Q1 2027 (better)", "100% Suez", num(all_suez),
         sigs("mar-rosso-migliorativo") + f"; FBX11 below {num(THRESHOLDS['fbx11_low'])} $/FEU (set here; now {num(V['fbx11']['valore'])})", "—"],
        ["C. Houthi attacks resume (worse)", "back to the Cape", num(all_cape),
         sigs("mar-rosso-peggiorativo") + f"; Red Sea war risk above {num(THRESHOLDS['redsea_war_high'], 1)}% of hull (set here); FBX11 above {num(THRESHOLDS['fbx11_high'])} $/FEU",
         "[Bab el-Mandeb closed, 3 months](../../simulatore.html#bab-el-mandeb/chiuso/3m)"],
        ["D. Gulf escalation spills over (overlay on A–C)", "unchanged for boxes; LNG and crude repriced",
         f"+{num(ts['fuel_t'] * (THRESHOLDS['vlsfo_sg_high'] - ci['p_now']) / ci['units'])} on the Suez voyage if VLSFO reaches {num(THRESHOLDS['vlsfo_sg_high'])} $/t",
         f"Singapore VLSFO above {num(THRESHOLDS['vlsfo_sg_high'])} $/t (now {num(ci['p_now'], 1)}; high of the year {num(V['vlsfo_sg']['massimo_anno'][1], 1)} on {date_en(V['vlsfo_sg']['massimo_anno'][0])}); "
         f"Hormuz below 5 ships a day (now {num(hz['transits_7d_avg'], 1)})", "[Hormuz closed, 3 months](../../simulatore.html#hormuz/chiuso/3m)"],
        ["E. Baltic incident (overlay)", "feeders to Gdańsk, Klaipėda delayed", "not modelled",
         f"a cable or pipeline incident within 30 days; Danish straits below −30% on a year (now {pct(pw['Danish straits (Oresund)']['var_vs_1y_pct'])}); "
         f"sanctioned tankers in the Gulf of Finland above {THRESHOLDS['gof_sanctioned']} (now {gof['sanzionate']})",
         "[Danish straits −25%, 1 month](../../simulatore.html#stretti-danesi/r25/1m)"],
    ], "Signal texts translated from rischio.json; values from rischio.json, noli.json, bunker-emissioni.json, transit-times.json, navi.json. "
       "Thresholds marked «set here» are this report's assessment, in THRESHOLDS in report/build_logistics.py."))
    cal = V["cal"]
    imo_next = next((x for x in V["imo"] if x["data"] >= V["today"].isoformat()), None)
    if imo_next:
        need(imo_next["fatto"], "ISWG-GHG 23", "MEPC 85", "4 dicembre 2026", where="bunker-emissioni imo")
    cal_txt = []
    for e in cal:
        t = e["titolo"]
        if "OPEC" in t:
            t = "OPEC+ ministerial meeting on 2027 output quotas"
        elif "annexation" in t:
            t = "EU sanctions over Russia's annexation of Ukrainian territory up for renewal"
        elif "Belarus" in t:
            t = "EU sanctions on Belarus (involvement in the Russian aggression) up for renewal"
        elif "Russia" in t:
            t = "EU sanctions regime on Russia up for renewal"
        cal_txt.append(f"{date_en(e['data'])}: {t}")
    B.append(("p", "**Dates in the window.** "
              + (f"IMO, from {date_en(imo_next['data'])}: ISWG-GHG 23, MEPC 85 and, on 4 December 2026 if confirmed, the resumed extraordinary session that "
                 f"may vote the Net-Zero Framework, a global carbon price for shipping. " if imo_next else "")
              + "; ".join(cal_txt) + f" ({dl('calendario.json')}, {dl('bunker-emissioni.json')})."))

    # ---------------------------------------------------------------- 9. method
    B.append(("h2", "method", "9. Method, sources and limits"))
    B.append(("tab", ["Source", "What", "Date of the data"], [
        [dl("transit-times.json"), "99 routes, nm and days today vs 2023, Cape alternative, vessel hypotheses", V["tt"]["updated"][:10]],
        [dl("bunker-emissioni.json"), "VLSFO prices (Ship & Bunker), EUA auction (EEX), ETS and FuelEU rules and cost example, Maersk surcharge", f"{ci['p_date']} / {ci['eua_date']}"],
        [dl("assicurazioni.json"), "war-risk premiums (press quotes), JWC listed areas", f"{V['prem_last']['mar-rosso']['data']} / {V['jwla']['data']}"],
        [dl("noli.json"), "WCI, FBX, CCFI", f"{V['wci_date']} / {V['fbx']['data']}"],
        [dl("port-risk.json"), "Port Risk Index, 39 ports", pr["reference_date"]],
        [f"{dl('porti-nord.json')}, {dl('portwatch.json')}", "IMF PortWatch port calls and chokepoint transits", V["ports_date"]],
        [f"{dl('stretti-dettaglio.json')}, {dl('rischio.json')}", "passage status, risk dashboard and scenario signals", V["risk_date"]],
        [f"{dl('ferrovie.json')}, {dl('supply-chain-ai.json')}, {dl('commercio.json')}", "rail corridors, EUV logistics, trade dependencies", "2025–2026 (per item)"],
        [f"{dl('sanzioni-navi.json')}, {dl('navi.json')}", "sanctioned ships (OFAC, UK, EU), AIS snapshot", V["navi_date"][:10]],
        [f"[{E1['source']}]({E1['link']})", E1["text"] + f" (reliability {E1['reliability']}; {E1['read']})", E1["date"]],
        [f"[{E2['source']}]({E2['link']})", E2["text"] + f" (reliability {E2['reliability']}; {E2['read']})", E2["date"]],
    ], ""))
    B.append(("ul", [
        "**Model, not ship data.** Daily consumption, hull value, utilisation and speed are declared hypotheses of the transit model. A real service calls at several "
        "ports, sails faster on the Cape to keep a weekly schedule and has its own MRV emissions data. The cost stack is an order of magnitude for comparison.",
        "**Same speed in every scenario**, so the Cape penalty is distance only; faster Cape sailing would raise fuel per mile (UNCTAD: 14 → 16 knots = +31% fuel per mile).",
        f"**2023 baselines from outside the repository**: the fuel price ({date_en(E1['date'])}) and the WCI ({date_en(E2['date'])}) come from search-result excerpts of "
        "secondary sources. They should be checked against the publishers before quotation.",
        "**War-risk premiums** are press quotes for tankers; no public quote exists for container ships. The last Red Sea quote is from "
        f"{date_en(V['prem_last']['mar-rosso']['data'])}.",
        "**AIS** counts only ships with the transponder on, about a week late. The congestion proxy is not waiting-time data.",
        f"**Inconsistent perimeters, declared not resolved:** hull value 150 M$ here (transit model) against 221.7 M$ (new ship) in {dl('assicurazioni.json')}; "
        f"the {S}% Suez share is for Far East–Europe capacity and is applied to every Asian origin.",
        "**Not repeated here**: the Italian report *Supply chain e logistica — novembre 2026* covers strait-by-strait transits, Italian ports and energy prices.",
        "**AI assistance.** An AI assistant (Claude, Anthropic) wrote the build script, ran the calculations and drafted the text from the monitor's data files "
        "and the cited sources. Every figure is generated from the files; the two external 2023 values are flagged. Gabriele Giuliani is responsible for publication.",
    ]))
    B.append(("review",))
    return B


# =====================================================================================
# Rendering
# =====================================================================================
def inline_md(t, data_prefix):
    return t.replace("](DATA/", f"]({data_prefix}").replace("](../../simulatore.html", "](../docs/simulatore.html")


def inline_html(t, data_prefix):
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2).replace("DATA/", data_prefix)}">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def review_parts():
    if not REVIEW:
        return [("p", "**Pending.** This edition has not yet been reviewed. An independent reviewer will check every number against the data files "
                      "and the cited sources under report/STANDARD.md, and check the text against the charts and the other reports. The log will be in "
                      f"report/revisioni/{SLUG}-2026-11.md; this box will then give the date, the number of claims checked, the corrections and what "
                      "remains unverifiable.")]
    R = REVIEW
    parts = [("p", f"**Claims checked.** {R['checked']}")]
    if R.get("corrections"):
        parts += [("p", "**Corrections.**"), ("ul", R["corrections"])]
    if R.get("unverifiable"):
        parts += [("p", "**Still unverifiable.**"), ("ul", R["unverifiable"])]
    return parts


def render_md(B, meta, figs):
    P = "../docs/data/"
    o = [f"# {meta['title']}", "", f"*{meta['subtitle']}*", "",
         f"Gabriele Giuliani · Geo-economic Risk Monitor · {meta['edition']} · data read on {meta['read']}", "",
         "Every number has a source and a date. Paragraphs marked *Assessment* are the monitor's reasoning, not facts.", "",
         "**Contents:** " + " · ".join(f"[{re.sub(r'^\d+\. ', '', b[2]).split(':')[0]}](#{b[1]})" for b in B if b[0] == "h2") + " · [Review](#review)", ""]
    for b in B:
        k = b[0]
        if k == "h2":
            o += [f'<a id="{b[1]}"></a>', "", f"## {b[2]}", ""]
        elif k == "h3":
            o += [f"### {b[1]}", ""]
        elif k in ("p", "val"):
            o += [("> " if k == "val" else "") + inline_md(b[1], P), ""]
        elif k == "ul":
            o += [f"- {inline_md(x, P)}" for x in b[1]] + [""]
        elif k == "tab":
            o += ["| " + " | ".join(b[1]) + " |", "|" + "---|" * len(b[1])]
            o += ["| " + " | ".join(inline_md(str(c), P).replace("|", "/") for c in r) + " |" for r in b[2]]
            o += [""] + ([f"<small>{inline_md(b[3], P)}</small>", ""] if b[3] else [])
        elif k == "fig":
            o += [f"![{re.sub(r'[*]', '', b[2]).split('.')[0]}]({figs[b[1]]})", "", f"<small>{inline_md(b[2], P)}</small>", ""]
        elif k == "review":
            o += ['<a id="review"></a>', "", "---", "", "### Review", ""]
            for kk, x in review_parts():
                o += ([inline_md(x, P), ""] if kk == "p" else [f"- {inline_md(y, P)}" for y in x] + [""])
    o += ["---", "", "Gabriele Giuliani · Geo-economic Risk Monitor · " + meta["edition"], "", meta["ai_note"], ""]
    return "\n".join(o)


CSS = """
:root{--paper:#F6F5F0;--card:#FFFFFF;--ink:#1D272D;--soft:#4f5d66;--rule:#DCDFDD;--accent:#A61E6B;--band:#ECE9E0;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#10181D;--card:#172127;--ink:#DAE0E2;--soft:#A0ABB1;--rule:#2B373E;--accent:#e06aab;--band:#1A252C;color-scheme:dark}}
:root[data-theme="dark"]{--paper:#10181D;--card:#172127;--ink:#DAE0E2;--soft:#A0ABB1;--rule:#2B373E;--accent:#e06aab;--band:#1A252C;color-scheme:dark}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 "IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
.page{max-width:70ch;margin:0 auto;padding:24px 16px 64px}
a{color:var(--accent);text-underline-offset:2px}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:24px}
.back{font-size:14px;text-decoration:none}
.back:hover{text-decoration:underline}
.theme{font:13px "IBM Plex Mono",monospace;background:var(--card);color:var(--soft);border:1px solid var(--rule);border-radius:6px;padding:4px 10px;cursor:pointer}
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
.review{margin:40px 0 0;padding:16px 18px;background:var(--card);border:1px dashed var(--soft);border-left:3px solid var(--soft);border-radius:0 8px 8px 0;font-size:15px}
.review h2{font:600 13px/1.4 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--soft);margin:0 0 10px;padding:0}
.review p,.review ul{margin:0 0 10px}
footer{margin-top:56px;padding-top:16px;border-top:1px solid var(--rule);font-size:14px;color:var(--soft)}
footer .sig{font-weight:600;color:var(--ink)}
"""


def chart_css():
    light = SVG_CSS_LIGHT
    dark = SVG_CSS_DARK
    scoped_dark = re.sub(r"(\.ael-[a-z0-9]+)", r':root[data-theme="dark"] \1', dark)
    auto_dark = re.sub(r"(\.ael-[a-z0-9]+)", r':root:not([data-theme="light"]) \1', dark)
    return f"{light}@media (prefers-color-scheme:dark){{{auto_dark}}}{scoped_dark}"


JS = """(function(){var r=document.documentElement,b=document.getElementById('theme');
function cur(){return r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')}
try{var s=localStorage.getItem('ael-theme');if(s)r.setAttribute('data-theme',s)}catch(e){}
function lab(){b.textContent=cur()==='dark'?'Light theme':'Dark theme'}lab();
b.addEventListener('click',function(){var n=cur()==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('ael-theme',n)}catch(e){}lab()});})();"""


def render_html(B, meta, svg):
    P = "../../data/"
    o = ["<!doctype html>", '<html lang="en-GB">', "<head>", '<meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         f"<title>{esc(meta['short'])}</title>", f'<meta name="description" content="{esc(meta["subtitle"])}">',
         '<link rel="preconnect" href="https://fonts.googleapis.com">', '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@600&display=swap" rel="stylesheet">',
         f"<style>{CSS}{chart_css()}</style>", "</head>", "<body>", '<main class="page">',
         '<div class="top"><a class="back" href="../../index.html">← Back to the map</a><button class="theme" id="theme" type="button">Dark theme</button></div>',
         f'<p class="kicker">Monthly report · {esc(meta["edition"])}</p>',
         f"<h1>{esc(meta['title'])}</h1>", f'<p class="sub">{esc(meta["subtitle"])}</p>',
         f'<p class="meta">Gabriele Giuliani · Geo-economic Risk Monitor · data read on {esc(meta["read"])}. Every number has a source and a date; '
         f'boxes marked <em>Assessment</em> are the monitor\'s reasoning, not facts.</p>',
         '<nav class="toc" aria-label="Contents"><h2>Contents</h2><ol>']
    for b in B:
        if b[0] == "h2":
            o.append(f'<li><a href="#{b[1]}">{esc(re.sub(r"^\d+\. ", "", b[2]).split(":")[0])}</a></li>')
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
            o.append('<aside class="review" id="review"><h2>Review</h2>' + "".join(parts) + "</aside>")
    o.append(f'<footer><p class="sig">Gabriele Giuliani · Geo-economic Risk Monitor</p><p>{esc(meta["edition"])}. {inline_html(meta["ai_note"], P)}</p>'
             '<p><a href="../../index.html">← Back to the map</a></p></footer>')
    o += ["</main>", f"<script>{JS}</script>", "</body>", "</html>"]
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", help="edition YYYY-MM (default: current month)")
    args = ap.parse_args()
    today = dt.date.today()
    month = args.month or today.strftime("%Y-%m")
    y, m = map(int, month.split("-"))
    edition = f"{MONTHS[m - 1]} {y}"
    V = compute(today)
    B = blocks(V, month)
    meta = {"title": f"Asia–Europe Logistics: Routes, Costs and Port Risk — {edition}",
            "short": "Asia–Europe Logistics",
            "subtitle": f"Sea routes, the cost of a container from Asia to Northern Europe, freight rates, port risk, alternatives, sanctions and Q1 2027 scenarios, {edition}.",
            "edition": edition, "read": date_en(today.isoformat()),
            "ai_note": ("Note on AI use: this report was prepared with an AI assistant (Claude, Anthropic), which wrote the build script "
                        "(report/build_logistics.py), the calculations and the draft text from the monitor's data files and the sources cited. "
                        "Numbers come from the data files and linked sources; assessments are marked. An independent review is pending. "
                        "Gabriele Giuliani is responsible for publication.")}
    os.makedirs(OUT_SVG, exist_ok=True)
    os.makedirs(OUT_HTML, exist_ok=True)
    svg, figs = {}, {}
    tabs = chart_tables(V)
    for key, fn in [("lanes", chart_lanes), ("waterfall", chart_waterfall), ("rate", chart_rate), ("cong", chart_cong)]:
        svg[key] = {"wide": fn(V, True), "narrow": fn(V, False), "table": tabs[key]}
        name = f"ael-{month}-{key}.svg"
        with open(os.path.join(OUT_SVG, name), "w", encoding="utf-8") as f:
            f.write(standalone(svg[key]["wide"]))
        figs[key] = f"grafici/{name}"
    with open(os.path.join(ROOT, "report", f"{SLUG}-{month}.md"), "w", encoding="utf-8") as f:
        f.write(render_md(B, meta, figs))
    with open(os.path.join(OUT_HTML, f"{SLUG}-{month}.html"), "w", encoding="utf-8") as f:
        f.write(render_html(B, meta, svg))
    print(f"written: report/{SLUG}-{month}.md, docs/report/en/{SLUG}-{month}.html, {len(svg)} charts; {len(WARN)} warnings")


if __name__ == "__main__":
    main()
