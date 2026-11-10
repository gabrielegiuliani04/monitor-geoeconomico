#!/usr/bin/env python3
"""Build the report "Could a Refrigeration-Style Cyberattack Hit Wind Farms? Old vs New Turbines".

Standard library only. From the repository root:

    python3 report/build_wind_cyber.py                  # edition for the current month
    python3 report/build_wind_cyber.py --month 2026-11  # another edition label

What it does every time it runs:
1. reads raccolta/cyber/flotta_eta.json (fleet by commissioning period, by country; system figures
   and reserve sizes) and docs/data/cyber-energia.json, port-risk.json, wind-calendar.json;
2. takes curated facts from the two research notes (report/ricerca/eolico-cyber-architetture.md and
   eolico-cyber-esposizione.md, 10 November 2026) from the EXT dictionary below: each has a source,
   a link and a date;
3. recomputes every share and every order-of-magnitude scenario and draws four SVG charts
   (wide and narrow versions, with a data table for each);
4. writes report/wind-cyber-YYYY-MM.md, docs/report/en/wind-cyber-YYYY-MM.html and
   report/grafici/wcy-YYYY-MM-*.svg.

Rules (report/STANDARD.md): numbers in the text and charts come from the JSON files or from EXT.
Hand-written items are linking prose, assessments (marked "Assessment"), the English renderings of
the Italian curated incident text in cyber-energia.json, and the scenario simplifications (declared).
need() checks that a figure quoted from a JSON text field is still there; if not, the script warns.

SCOPE: defensive, architecture-level analysis. The report contains no exploit details, vulnerability
identifiers, credentials, vendor-specific weaknesses, lists or locations of exposed systems, or
attack steps. Keep it that way when editing.
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
FLEET_FILE = os.path.join(ROOT, "raccolta", "cyber", "flotta_eta.json")
OUT_SVG = os.path.join(ROOT, "report", "grafici")
OUT_HTML = os.path.join(ROOT, "docs", "report", "en")
WARN = []
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
R1 = "report/ricerca/eolico-cyber-architetture.md"
R2 = "report/ricerca/eolico-cyber-esposizione.md"

# ------------------------------------------------------------------------------------------------
# Curated facts from the research notes (10 November 2026). value, unit, source, link, date.
# ------------------------------------------------------------------------------------------------
EXT = {
    # Review 10-11-2026: the draft had 250-350 (no source found); cyber-energia.json and the agent file give 500-700, AP 700 (13-10-2026)
    "fr_stores_low": (500, "stores", "initial estimates (cyber-energia.json)", "https://aljazeera.com/news/2026/10/13/unprecedented-cyberattack-hits-french-supermarkets-causing-food-losses", "2026-10-13"),
    "fr_stores_low_hi": (700, "stores", "initial estimates (cyber-energia.json; AP, 13-10-2026)", "https://aljazeera.com/news/2026/10/13/unprecedented-cyberattack-hits-french-supermarkets-causing-food-losses", "2026-10-13"),
    "fr_stores_high": (1000, "stores", "Al Jazeera", "https://aljazeera.com/news/2026/10/13/unprecedented-cyberattack-hits-french-supermarkets-causing-food-losses", "2026-11-09"),
    "wave2_stores": (115, "stores", "SecurityWeek", "https://securityweek.com/over-100-european-stores-hit-as-supermarket-fridge-attacks-resume", "2026-11-03"),
    "fr_panels_before": (1825, "panels", "Infosecurity Magazine (internet-scanner counts)", "https://www.infosecurity-magazine.com/news/france-expose-danfoss-controllers/", "2026-10-11"),
    "fr_panels_after": (537, "panels", "Infosecurity Magazine (internet-scanner counts)", "https://www.infosecurity-magazine.com/news/france-expose-danfoss-controllers/", "2026-10-14"),
    "modat_total": (8547, "systems", "Modat and NCSC-NL via Security Magazine", "https://www.securitymagazine.com/articles/102635-8-500-european-wind-solar-systems-exposed", "2026-10-09"),
    "modat_countries": (35, "countries", "Modat and NCSC-NL via Security Magazine", "https://www.securitymagazine.com/articles/102635-8-500-european-wind-solar-systems-exposed", "2026-10-09"),
    "modat_wind": (605, "systems", "Modat and NCSC-NL via SWZ Maritime", "https://swzmaritime.nl/news/2026/10/08/8500-wind-and-solar-systems-exposed-online/", "2026-10-08"),
    "modat_wind_countries": (23, "countries", "Modat and NCSC-NL via SWZ Maritime", "https://swzmaritime.nl/news/2026/10/08/8500-wind-and-solar-systems-exposed-online/", "2026-10-08"),
    "spe_gw": (3, "GW", "DNV for SolarPower Europe", "https://www.solarpowereurope.org/press-releases/new-report-solar-sector-proposes-solutions-to-mitigate-critical-cybersecurity-risks", "2025-04-29"),
    # Review: the 7-brand figure is in the full report (p. on market concentration), not in the press release; it assumes remote access to 70% of each installed base, 2023 data
    "spe_brands": (7, "brands", "DNV for SolarPower Europe, full report", "https://api.solarpowereurope.org/uploads/SPE_2025_Solutions_for_PV_Cyber_Risks_to_Grid_Stability_032dc2ae5a.pdf", "2025-04-29"),
    "sundown_gw": (4.5, "GW", "Forescout SUN:DOWN, citing earlier research", "https://www.forescout.com/research-labs/sun-down-a-dark-side-to-solar-energy-grids/", "2025-03"),
    "vestas_gw": (161, "GW", "Vestas annual report 2025 via GreentechLead", "https://greentechlead.com/wind/vestas-reports-record-2025-revenue-of-eur-18-8-billion-sets-stronger-2026-outlook-52164", "2026-02-05"),
    "vestas_turbines": (56000, "turbines", "Vestas annual report 2025 via GreentechLead", "https://greentechlead.com/wind/vestas-reports-record-2025-revenue-of-eur-18-8-billion-sets-stronger-2026-outlook-52164", "2026-02-05"),
    "sg_turbines": (10000, "turbines", "Siemens Gamesa, offshore service logistics", "https://www.siemensgamesa.com/explore/innovations/offshore-service-logistics-part-1", "n/d"),
    "kasat_turbines": (5800, "turbines", "pv magazine", "https://www.pv-magazine.com/2022/03/01/satellite-cyber-attack-paralyzes-11gw-of-german-wind-turbines", "2022-03-01"),
    # Review: pv magazine (Handelsblatt) 11 GW; Enercon itself: 'more than 10 GW' in central Europe (EVWind, 21-04-2022)
    "kasat_gw": (11, "GW", "pv magazine", "https://www.pv-magazine.com/2022/03/01/satellite-cyber-attack-paralyzes-11gw-of-german-wind-turbines", "2022-03-01"),
    "enercon_de_gw": (27.8, "GW", "MaStR 10-11-2026, researcher's calculation (" + R2 + ")", "https://www.marktstammdatenregister.de/MaStR/Datendownload", "2026-11-10"),
    "enercon_de_turbines": (12356, "turbines", "MaStR 10-11-2026, researcher's calculation (" + R2 + ")", "https://www.marktstammdatenregister.de/MaStR/Datendownload", "2026-11-10"),
    "isp_turbines": (2000, "turbines", "The Record (press figure, not the company's)", "https://therecord.media/german-wind-farm-operator-confirms-cybersecurity-incident-after-ransomware-group", "2022-04"),
    "decom_gw": (16, "GW", "WindEurope, 2025 statistics and outlook 2026-2030", "https://www.rinnovabili.it/wp-content/uploads/2026/02/WindEurope-European-Stats-2025.pdf", "2026-02"),
    "kritis_mw": (104, "MW", "openKRITIS (reliability medium)", "https://www.openkritis.de/it-sicherheitsgesetz/sektor_energie.html", "2026"),
    "dnv_nl_mw": (750, "MW", "DNV case study (date not captured)", "https://www.dnv.com/cyber/insights/cases/designing-ot-cybersecurity-into-an-offshore-wind-farm-to-provide-800000-homes-with-clean-energy/", "n/d"),
    "gb2019_mw": (737, "MW", "Ofgem report on 9 August 2019", "https://www.ofgem.gov.uk/publications/investigation-9-august-2019-power-outage", "2020-01"),
    "gb2019_customers": (1.15, "million customers", "Ofgem report on 9 August 2019", "https://www.ofgem.gov.uk/publications/investigation-9-august-2019-power-outage", "2020-01"),
    "pl_sites": (30, "sites", "CERT Polska", "https://cert.pl/en/posts/2026/01/incident-report-energy-sector-2025/", "2026-01-30"),
    # Review: primary source read (CERT Polska follow-up, 8 Aug 2026) instead of The Hacker News, whose article reproduces device-level detail
    "chp_residents": (50000, "residents", "CERT Polska follow-up report", "https://cert.pl/en/posts/2026/08/incident-follow-up-report-energy-sector-2025/", "2026-08-08"),
    "uk_days": (4, "days", "Irish Times (original: The Sunday Telegraph)", "https://www.irishtimes.com/world/uk/2026/08/23/iran-linked-hackers-accused-of-cyberattack-that-shut-down-british-power-plant/", "2026-08-23"),
    "gamma_cn_max": (25, "% of turbines", "RVO draft permit IJmuiden Ver Gamma-B, rule 22", "https://www.rvo.nl/sites/default/files/2026-10/Concept-voorschriften-vergunning-IJmuiden-Ver-_kavel-Gamma-B_versie-oktober-2026.pdf", "2026-10"),
    "lt_kw": (100, "kW", "LRT", "https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-to-solar-and-wind-farm-systems", "2024-11-12"),
    "lt_existing": ("1 June 2026", "deadline", "pv magazine (the draft said 1 May 2026)", "https://www.pv-magazine.com/2026/06/05/lithuanias-grid-operators-can-now-disconnect-solar-plants-without-cybersecurity-measures/", "2026-06-05"),
    "spower_mw": (500, "MW", "Utility Dive (NERC lesson learned)", "https://www.utilitydive.com/news/first-cyber-attack-on-solar-wind-assets-revealed-widespread-grid-weaknesse/566505/", "2019-09"),
    "eeg_kw": (25, "kW", "Vattenfall explainer on section 10b EEG", "https://energysales.vattenfall.de/en/renewables/remote-controllability", "n/d"),
}


def X(k):
    return EXT[k][0]


def XL(k, label=None):
    v = EXT[k]
    return f"[{label or v[2]}]({v[3]})"


# ------------------------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------------------------
def warn(msg):
    WARN.append(msg)
    print("WARNING:", msg, file=sys.stderr)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def esc(s):
    return html.escape(str(s), quote=True)


def num(v, dec=0):
    if v is None:
        return "n/a"
    s = f"{v:,.{dec}f}"
    return s


def gw(mw, dec=1):
    return f"{mw / 1000:,.{dec}f}"


def pc(x, dec=0):
    return f"{100 * x:.{dec}f}%"


def date_en(s):
    try:
        d = dt.date.fromisoformat(s[:10])
        return f"{d.day} {MONTHS[d.month - 1]} {d.year}"
    except Exception:
        return s


def date_short(s):
    try:
        d = dt.date.fromisoformat(s[:10])
        return f"{d.day:02d} {MONTHS[d.month - 1][:3]} {d.year}"
    except Exception:
        return s


def need(text, token, where):
    if token not in (text or ""):
        warn(f"'{token}' no longer found in {where}: re-read the sentence that quotes it")


# ------------------------------------------------------------------------------------------------
# Computation
# ------------------------------------------------------------------------------------------------
PER = ["pre2010", "2010-2017", "2018+"]
PER_LABEL = {"pre2010": "before 2010", "2010-2017": "2010–2017", "2018+": "2018 and later"}
GEM_NAME = {"IT": "Italy", "NL": "Netherlands", "PL": "Poland", "LT": "Lithuania", "LV": "Latvia", "EE": "Estonia",
            "SE": "Sweden", "FI": "Finland", "EU": "EUROPE"}
LABEL = {"DK": "Denmark", "DE": "Germany", "GB": "UK", "IT": "Italy", "NL": "Netherlands", "PL": "Poland",
         "LT": "Lithuania", "LV": "Latvia", "EE": "Estonia", "SE": "Sweden", "FI": "Finland", "EU": "Europe"}


def shares(mw):
    tot = sum(mw[p] for p in PER)
    return {p: (mw[p] / tot if tot else 0) for p in PER}, tot


def compute():
    F = load(FLEET_FILE)
    CE = load(os.path.join(DATA, "cyber-energia.json"))
    PR = load(os.path.join(DATA, "port-risk.json"))
    WC = load(os.path.join(DATA, "wind-calendar.json"))
    V = {"F": F, "CE": CE, "PR": PR, "WC": WC}
    reg, gem = F["registri"], F["gem_progetti_10mw"]["paesi"]

    on, off = {}, {}
    on["DK"] = {p: reg["DK"]["onshore"][p]["mw"] for p in PER}
    on["DE"] = {p: reg["DE"]["onshore"][p]["mw"] for p in PER}
    on["GB"] = {p: reg["GB"]["dati"]["onshore"][p]["mw"] for p in PER}
    off["DK"] = {p: reg["DK"]["offshore"][p]["mw"] for p in PER}
    off["DE"] = {p: reg["DE"]["offshore"][p]["mw"] for p in PER}
    off["GB"] = {p: reg["GB"]["dati"]["offshore"][p]["mw"] for p in PER}
    for c in ["IT", "NL", "PL", "LT", "LV", "EE", "SE", "FI", "EU"]:
        on[c] = {p: gem[GEM_NAME[c]]["onshore"][p] for p in PER}
    for c in ["NL", "EU"]:
        off[c] = {p: gem[GEM_NAME[c]]["offshore"][p] for p in PER}
    V["on"], V["off"] = on, off
    V["on_sh"] = {c: shares(m) for c, m in on.items()}
    V["off_sh"] = {c: shares(m) for c, m in off.items()}
    V["on_src"] = {c: ("register" if c in ("DK", "DE", "GB") else "GEM ≥10 MW") for c in on}
    V["dk_turb_pre"] = reg["DK"]["onshore"]["pre2010"]["turbine"]
    V["de_turb_pre"] = reg["DE"]["onshore"]["pre2010"]["turbine"]

    # Denmark: size and age
    tz = reg["DK"]["per_taglia_onshore_turbine"]
    mz = reg["DK"]["per_taglia_onshore_mw"]
    V["dk_small_n"] = tz["<500kW"] + tz["500-999kW"]
    V["dk_small_mw"] = mz["<500kW"] + mz["500-999kW"]
    V["dk_on_n"] = sum(reg["DK"]["onshore"][p]["turbine"] for p in PER)
    V["dk_20y_on"] = reg["DK"]["oltre_20_anni_mw"]["onshore"]
    V["dk_20y_off"] = reg["DK"]["oltre_20_anni_mw"]["offshore"]
    V["dk_pre_avg_mw"] = on["DK"]["pre2010"] / V["dk_turb_pre"]

    # Germany
    de = reg["DE"]
    V["de_20y"] = de["oltre_20_anni_mw"]["onshore"]
    V["de_2000"] = de["fino_al_2000_mw"]["onshore"]
    V["de_orphan_on"] = de["marchi_non_piu_attivi_mw"]["onshore"]
    V["de_orphan_off"] = de["marchi_non_piu_attivi_mw"]["offshore"]
    V["de_orphan_on_tot"] = sum(V["de_orphan_on"].values())
    V["de_orphan_off_tot"] = sum(V["de_orphan_off"].values())
    V["de_nat_pre"] = de["persona_fisica_onshore_mw"]["pre2010"]
    V["de_nat_tot"] = sum(de["persona_fisica_onshore_mw"].values())
    V["de_dv"] = de["telecontrollo_direktvermarkter_quota_mw"]
    V["de_vensys"] = de["oem_cinesi"]["Vensys (Goldwind-controlled)"]
    V["de_ops"] = de["operatori_registrati"]
    V["de_on_tot"] = sum(on["DE"].values())
    V["de_off_tot"] = sum(off["DE"].values())
    V["de_all"] = V["de_on_tot"] + V["de_off_tot"]
    V["de_on_turb"] = sum(de["onshore"][p]["turbine"] for p in PER)

    # Offshore EMODnet: average farm size by period
    tot = F["offshore_emodnet"]["per_paese"]["TOT"]
    V["emod"] = {p: {"farms": tot[p]["parchi"], "mw": tot[p]["mw"], "turb": tot[p]["turbine"],
                     "avg": tot[p]["mw"] / tot[p]["parchi"]} for p in PER}

    # System and reserves
    S = F["sistema"]
    V["sys"] = S
    res = S["riserve"]
    V["ce_ref"], V["nordic"], V["gb_max"] = res["CE_incidente_riferimento_mw"], res["nordico_incidente_dimensionante_mw"], res["GB_perdita_infrequente_max_mw"]
    de25 = S["DE_2025"]
    V["de_cf_avg"] = de25["vento_twh"] * 1e6 / 8760 / V["de_all"]
    V["de_cf_peak"] = de25["max_vento_gw"] * 1000 / V["de_all"]
    V["de_avg_out_gw"] = de25["vento_twh"] * 1e6 / 8760 / 1000
    avg_turb_mw = V["de_on_tot"] / V["de_on_turb"]
    V["de_avg_turb"] = avg_turb_mw
    isp_mw = X("isp_turbines") * avg_turb_mw
    enc_mw = X("enercon_de_gw") * 1000
    hornsea = next((e for e in CE["elementi"] if e.get("id") == "OFF-HORNSEA-1-E-2"), None)
    V["hornsea_mw"] = hornsea["mw"] if hornsea else None
    if not hornsea:
        warn("Hornsea 1+2 concentration item missing from cyber-energia.json")
    V["isp_mw"], V["enc_mw"] = isp_mw, enc_mw
    V["scen"] = [
        {"k": "A", "name": "Remote monitoring lost (KA-SAT, Poland type)", "short": "A. Monitoring lost", "lo": 0, "hi": 0, "ref": "any"},
        {"k": "B", "name": f"One service provider's ≈{num(X('isp_turbines'))} German turbines stop", "short": "B. One service firm", "lo": isp_mw * V["de_cf_avg"], "hi": isp_mw * V["de_cf_peak"], "ref": "CE"},
        {"k": "C", "name": "One OEM's German onshore fleet stops (Enercon size)", "short": "C. One OEM fleet (DE)", "lo": enc_mw * V["de_cf_avg"], "hi": enc_mw * V["de_cf_peak"], "ref": "CE"},
        {"k": "D", "name": "All eastern-Danish (DK2) wind at its 2025 peak", "short": "D. All DK2 wind", "lo": S["DK_2025"]["max_vento_DK2_mw"], "hi": S["DK_2025"]["max_vento_DK2_mw"], "ref": "Nordic"},
        {"k": "E", "name": "Largest offshore cluster trips (Hornsea 1+2, GB)", "short": "E. Hornsea 1+2", "lo": V["hornsea_mw"] or 0, "hi": V["hornsea_mw"] or 0, "ref": "GB"},
    ]

    # Ports: offshore wind base ports in the Port Risk Index
    V["ports"] = sorted([p for p in PR["ports"] if "offshore wind base port" in (p.get("strategic_roles") or [])],
                        key=lambda p: -p["score"])
    V["pr_date"] = PR["reference_date"]

    # Calendar
    V["gamma"] = next((e for e in WC["elementi"] if e["id"] == "WC-NL-GAMMA-TENDER"), None)
    if not V["gamma"]:
        warn("WC-NL-GAMMA-TENDER missing from wind-calendar.json")

    # Guards on Italian text fields quoted in English
    el = {e.get("id"): e for e in CE["elementi"]}
    V["el"] = el
    need(el.get("CE-2022-KASAT", {}).get("effetto"), "5.800", "cyber-energia.json CE-2022-KASAT")
    need(el.get("CE-2022-DWT", {}).get("effetto"), "2.000", "cyber-energia.json CE-2022-DWT")
    need(el.get("CE-2025-PL", {}).get("nome"), "30", "cyber-energia.json CE-2025-PL")
    need(el.get("CE-2015-UA", {}).get("effetto"), "225.000", "cyber-energia.json CE-2015-UA")
    need(el.get("CE-2023-DK", {}).get("nome"), "22", "cyber-energia.json CE-2023-DK")
    need(el.get("CE-2026-BE-FRIGO", {}).get("nome"), "115", "cyber-energia.json CE-2026-BE-FRIGO")
    need(el.get("CE-2026-FR-FRIGO", {}).get("effetto"), "50 gradi", "cyber-energia.json CE-2026-FR-FRIGO")
    rules = " ".join(r["stato"] for r in CE["regole"])
    need(rules, "11-12-2027", "cyber-energia.json regole (CRA)")
    need(rules, "15-08-2026", "cyber-energia.json regole (NL NIS2)")
    need(rules, "1-07-2025", "cyber-energia.json regole (DK NIS2)")

    # Checks against the shares the brief and the notes quote
    for c, exp in [("DK", 49), ("DE", 26), ("GB", 22), ("IT", 38)]:
        got = round(100 * V["on_sh"][c][0]["pre2010"])
        if got != exp:
            warn(f"pre-2010 onshore share for {c} is now {got}%, the text was drafted for {exp}%")
    return V


# ------------------------------------------------------------------------------------------------
# SVG charts
# ------------------------------------------------------------------------------------------------
SVG_STYLE = """<style>
.wc-t{font:600 14px 'IBM Plex Sans',system-ui,sans-serif;fill:#1D272D}
.wc-l{font:12px 'IBM Plex Sans',system-ui,sans-serif;fill:#3b474e}
.wc-m{font:11px 'IBM Plex Mono',ui-monospace,monospace;fill:#5f6b72}
.wc-g{stroke:#d9dcd8;stroke-width:1}
.wc-z{stroke:#5f6b72;stroke-width:1.2}
.wc-s1{fill:#A61E6B}.wc-s2{fill:#2a78d6}.wc-s3{fill:#1baf7a}.wc-s0{fill:#9aa4aa}
.wc-k1{stroke:#A61E6B}.wc-k2{stroke:#2a78d6}.wc-k3{stroke:#1D272D}
.wc-bg{fill:#ffffff}.wc-gap{stroke:#ffffff;stroke-width:2}
@media (prefers-color-scheme:dark){
.wc-t{fill:#DAE0E2}.wc-l{fill:#c3cacd}.wc-m{fill:#99a5ab}.wc-g{stroke:#2f3b42}.wc-z{stroke:#99a5ab}
.wc-s1{fill:#d14f9a}.wc-s2{fill:#3987e5}.wc-s3{fill:#199e70}.wc-s0{fill:#5f6b72}
.wc-k1{stroke:#d14f9a}.wc-k2{stroke:#3987e5}.wc-k3{stroke:#DAE0E2}
.wc-bg{fill:#172127}.wc-gap{stroke:#172127}}
</style>"""


def svg_open(w, h, title, desc, uid):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" '
            f'aria-labelledby="{uid}-t {uid}-d" style="max-width:{w}px;height:auto;display:block">'
            f'<title id="{uid}-t">{esc(title)}</title><desc id="{uid}-d">{esc(desc)}</desc>{SVG_STYLE}'
            f'<rect class="wc-bg" x="0" y="0" width="{w}" height="{h}" rx="6"/>')


def legend(x, y, items, wide):
    o, cx = [], x
    for cls, lab in items:
        o.append(f'<rect class="{cls}" x="{cx}" y="{y - 9}" width="11" height="11" rx="2"/>'
                 f'<text class="wc-l" x="{cx + 16}" y="{y}">{esc(lab)}</text>')
        cx += 16 + len(lab) * (6.6 if wide else 6.2) + 14
    return "".join(o)


def stacked_share_chart(rows, title, sub, uid, wide, note_right="pre-2010"):
    """rows: list of (label, src, shares dict, total MW). 100% stacked horizontal bars."""
    w = 680 if wide else 360
    left = 118 if wide else 84
    right = 58 if wide else 44
    top = 82 if wide else 98
    rowh = 30 if wide else 30
    h = top + rowh * len(rows) + 40
    pw = w - left - right
    o = [svg_open(w, h, title, sub, uid), f'<text class="wc-t" x="16" y="24">{esc(title)}</text>',
         f'<text class="wc-m" x="16" y="42">{esc(sub)}</text>']
    leg = [("wc-s1", "before 2010"), ("wc-s2", "2010–2017"), ("wc-s3", "2018+")]
    o.append(legend(16, 66 if wide else 64, leg, wide) if wide else
             legend(16, 64, leg[:2], wide) + legend(16, 82, leg[2:], wide))
    for t in (0, 0.25, 0.5, 0.75, 1):
        x = left + pw * t
        o.append(f'<line class="wc-g" x1="{x:.1f}" y1="{top - 6}" x2="{x:.1f}" y2="{top + rowh * len(rows)}"/>')
        o.append(f'<text class="wc-m" x="{x:.1f}" y="{top + rowh * len(rows) + 16}" text-anchor="middle">{int(t * 100)}%</text>')
    o.append(f'<text class="wc-m" x="{w - 8}" y="{top - 10}" text-anchor="end">{esc(note_right)}</text>')
    for i, (lab, src, sh, tot) in enumerate(rows):
        y = top + i * rowh + 5
        bh = rowh - 12
        o.append(f'<text class="wc-l" x="{left - 8}" y="{y + bh - 4}" text-anchor="end">{esc(lab)}{"*" if src != "register" else ""}</text>')
        x0 = left
        for j, p in enumerate(PER):
            ww = pw * sh[p]
            if ww <= 0:
                continue
            o.append(f'<rect class="wc-s{j + 1}" x="{x0:.1f}" y="{y}" width="{ww:.1f}" height="{bh}" rx="2">'
                     f'<title>{esc(lab)}, {PER_LABEL[p]}: {pc(sh[p], 1)} of {num(tot)} MW ({src})</title></rect>')
            if j > 0:
                o.append(f'<line class="wc-gap" x1="{x0:.1f}" y1="{y}" x2="{x0:.1f}" y2="{y + bh}"/>')
            x0 += ww
        o.append(f'<text class="wc-l" x="{w - 8}" y="{y + bh - 4}" text-anchor="end"><tspan font-weight="600">{pc(sh["pre2010"])}</tspan></text>')
    o.append("</svg>")
    return "".join(o)


def chart_onshore(V, wide=True):
    order = ["DK", "DE", "GB"] + sorted(["IT", "NL", "PL", "LT", "LV", "EE", "SE", "FI"],
                                         key=lambda c: -V["on_sh"][c][0]["pre2010"]) + ["EU"]
    rows = [(LABEL[c], V["on_src"][c], V["on_sh"][c][0], V["on_sh"][c][1]) for c in order]
    t = "Onshore wind capacity by commissioning period" if wide else "Onshore wind by age"
    s = "share of MW in operation; * = GEM projects ≥10 MW (understates old fleets)" if wide else "share of MW; * = GEM ≥10 MW"
    return stacked_share_chart(rows, t, s, "wcy-on" + ("w" if wide else "n"), wide)


def chart_offshore(V, wide=True):
    order = ["DK", "DE", "GB", "NL", "EU"]
    rows = [(LABEL[c], "register" if c in ("DK", "DE", "GB") else "GEM ≥10 MW", V["off_sh"][c][0], V["off_sh"][c][1]) for c in order]
    t = "Offshore wind capacity by commissioning period" if wide else "Offshore wind by age"
    s = "share of MW in operation; * = GEM projects ≥10 MW" if wide else "share of MW; * = GEM ≥10 MW"
    return stacked_share_chart(rows, t, s, "wcy-off" + ("w" if wide else "n"), wide)


def chart_germany(V, wide=True):
    w = 680 if wide else 360
    left = 110 if wide else 84
    right = 70 if wide else 50
    top = 84 if wide else 100
    rowh = 40
    h = top + rowh * 3 + 40
    pw = w - left - right
    mx = 30000
    t = "Germany: onshore capacity by period and brand status" if wide else "Germany onshore: orphan brands"
    s = "MW in operation, MaStR 10-11-2026" if wide else "MW in operation, MaStR"
    o = [svg_open(w, h, t, s, "wcy-de" + ("w" if wide else "n")), f'<text class="wc-t" x="16" y="24">{esc(t)}</text>',
         f'<text class="wc-m" x="16" y="42">{esc(s)}</text>']
    leg = [("wc-s1", "brands no longer active"), ("wc-s2", "active brands")]
    o.append(legend(16, 66, leg, wide) if wide else legend(16, 64, leg[:1], wide) + legend(16, 82, leg[1:], wide))
    for g in range(0, mx + 1, 10000):
        x = left + pw * g / mx
        o.append(f'<line class="wc-g" x1="{x:.1f}" y1="{top - 6}" x2="{x:.1f}" y2="{top + rowh * 3}"/>'
                 f'<text class="wc-m" x="{x:.1f}" y="{top + rowh * 3 + 16}" text-anchor="middle">{g // 1000} GW</text>')
    for i, p in enumerate(PER):
        y = top + i * rowh + 8
        bh = rowh - 18
        totp = V["on"]["DE"][p]
        orp = V["de_orphan_on"][p]
        x1 = left + pw * orp / mx
        x2 = left + pw * totp / mx
        plab = PER_LABEL[p] if wide else {"pre2010": "pre-2010", "2010-2017": "2010–17", "2018+": "2018+"}[p]
        o.append(f'<text class="wc-l" x="{left - 8}" y="{y + bh - 6}" text-anchor="end">{esc(plab)}</text>')
        o.append(f'<rect class="wc-s1" x="{left}" y="{y}" width="{x1 - left:.1f}" height="{bh}" rx="2"><title>{PER_LABEL[p]}: {num(orp)} MW from brands no longer active</title></rect>')
        o.append(f'<rect class="wc-s2" x="{x1:.1f}" y="{y}" width="{x2 - x1:.1f}" height="{bh}" rx="2"><title>{PER_LABEL[p]}: {num(totp - orp)} MW from active brands</title></rect>')
        o.append(f'<line class="wc-gap" x1="{x1:.1f}" y1="{y}" x2="{x1:.1f}" y2="{y + bh}"/>')
        o.append(f'<text class="wc-l" x="{x2 + 6:.1f}" y="{y + bh - 6}">{gw(totp)} GW</text>')
    o.append("</svg>")
    return "".join(o)


def chart_scen(V, wide=True):
    w = 680 if wide else 360
    left = 196 if wide else 112
    right = 24 if wide else 14
    top = 112 if wide else 110
    rowh = 40 if wide else 44
    sc = V["scen"]
    h = top + rowh * len(sc) + 44
    pw = w - left - right
    mx = 20000
    t = "Order-of-magnitude loss scenarios vs reserve sizing" if wide else "Loss scenarios vs reserves"
    s = "GW lost at once; bar = average to 2025-peak output; ESTIMATES" if wide else "GW lost; avg → peak; ESTIMATES"
    o = [svg_open(w, h, t, s, "wcy-sc" + ("w" if wide else "n")), f'<text class="wc-t" x="16" y="24">{esc(t)}</text>',
         f'<text class="wc-m" x="16" y="42">{esc(s)}</text>']
    def X_(mw):
        return left + pw * mw / mx
    for g in range(0, mx + 1, 5000):
        o.append(f'<line class="wc-g" x1="{X_(g):.1f}" y1="{top - 6}" x2="{X_(g):.1f}" y2="{top + rowh * len(sc)}"/>'
                 f'<text class="wc-m" x="{X_(g):.1f}" y="{top + rowh * len(sc) + 16}" text-anchor="{'end' if g == mx else 'middle'}">{g // 1000}{" GW" if g == mx else ""}</text>')
    refs = sorted([(V["ce_ref"], "Continental Europe ref. incident", "CE", "wc-k1", "4 3"),
                   (V["gb_max"], "GB infrequent infeed loss", "GB", "wc-k3", "1 3"),
                   (V["nordic"], "Nordic dimensioning incident", "Nordic", "wc-k2", "6 2")])  # left line on top row: no label crossed
    for j, (mw, lab, sh_, cls, dash) in enumerate(refs):
        yy = 58 + j * 16
        x = X_(mw)
        o.append(f'<line class="{cls}" x1="{x:.1f}" y1="{yy + 3}" x2="{x:.1f}" y2="{top + rowh * len(sc)}" stroke-width="1.5" stroke-dasharray="{dash}"/>')
        txt = f"{lab}: {gw(mw, 2 if mw % 100 else 1)} GW" if wide else f"{sh_} {gw(mw, 2 if mw % 100 else 1)} GW"
        o.append(f'<text class="wc-m" x="{x + 4:.1f}" y="{yy}">{esc(txt)}</text>')
    for i, r in enumerate(sc):
        y = top + i * rowh + 10
        bh = 16
        lab = r["short"] if wide else r["short"].replace("One OEM fleet (DE)", "One OEM (DE)").replace("One service firm", "One ISP")
        o.append(f'<text class="wc-l" x="{left - 8}" y="{y + 12}" text-anchor="end">{esc(lab)}</text>')
        if r["hi"] <= 0:
            o.append(f'<circle class="wc-s0" cx="{left + 4}" cy="{y + 8}" r="4"><title>{esc(r["name"])}: ≈0 GW lost at once</title></circle>'
                     f'<text class="wc-l" x="{left + 14}" y="{y + 12}">{"≈0 GW: turbines keep producing" if wide else "≈0 GW"}</text>')
            continue
        x1, x2 = X_(r["lo"]), X_(r["hi"])
        if r["hi"] - r["lo"] < 50:
            o.append(f'<rect class="wc-s2" x="{left}" y="{y}" width="{x2 - left:.1f}" height="{bh}" rx="2"><title>{esc(r["name"])}: ≈{gw(r["hi"])} GW</title></rect>'
                     f'<text class="wc-l" x="{x2 + 6:.1f}" y="{y + 12}">≈{gw(r["hi"])}</text>')
        else:
            o.append(f'<rect class="wc-s2" x="{left}" y="{y}" width="{x1 - left:.1f}" height="{bh}" rx="2"><title>{esc(r["name"])}: ≈{gw(r["lo"])} GW at average output</title></rect>'
                     f'<rect class="wc-s1" x="{x1:.1f}" y="{y}" width="{x2 - x1:.1f}" height="{bh}" rx="2"><title>{esc(r["name"])}: up to ≈{gw(r["hi"])} GW at the 2025 peak</title></rect>'
                     f'<line class="wc-gap" x1="{x1:.1f}" y1="{y}" x2="{x1:.1f}" y2="{y + bh}"/>'
                     f'<text class="wc-l" x="{min(x2 + 6, w - 60):.1f}" y="{y + 12 if x2 + 60 < w else y - 3}">≈{gw(r["lo"])}–{gw(r["hi"])}</text>')
    yl = top + rowh * len(sc) + 34
    o.append(legend(16, yl, [("wc-s2", "average output"), ("wc-s1", "up to 2025 peak")], wide))
    o.append("</svg>")
    return "".join(o)


def table_html(head, rows):
    return ('<div class="tabella"><table><thead><tr>' + "".join(f'<th scope="col">{esc(x)}</th>' for x in head) +
            "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows) +
            "</tbody></table></div>")


def chart_tables(V):
    on_rows = [[LABEL[c], V["on_src"][c]] + [f"{num(V['on'][c][p])} ({pc(V['on_sh'][c][0][p], 1)})" for p in PER] + [num(V["on_sh"][c][1])]
               for c in V["on"]]
    off_rows = [[LABEL[c], "register" if c in ("DK", "DE", "GB") else "GEM ≥10 MW"] +
                [f"{num(V['off'][c][p])} ({pc(V['off_sh'][c][0][p], 1)})" for p in PER] + [num(V["off_sh"][c][1])] for c in V["off"]]
    de_rows = [[PER_LABEL[p], num(V["on"]["DE"][p]), num(V["de_orphan_on"][p]), num(V["on"]["DE"][p] - V["de_orphan_on"][p])] for p in PER]
    sc_rows = [[r["name"], f"{gw(r['lo'])}", f"{gw(r['hi'])}", r["ref"]] for r in V["scen"]]
    hd = ["Country", "Source", "MW before 2010", "MW 2010–2017", "MW 2018+", "MW total dated"]
    return {
        "onshore": table_html(hd, on_rows),
        "offshore": table_html(hd, off_rows),
        "germany": table_html(["Period", "MW total", "MW brands no longer active", "MW active brands"], de_rows),
        "scen": table_html(["Scenario (estimate)", "GW at average output", "GW at 2025 peak", "Compare with"], sc_rows),
    }


# ------------------------------------------------------------------------------------------------
# Text
# ------------------------------------------------------------------------------------------------
def L(text, url):
    return f"[{text}]({url})"


def DL(name):
    return f"[`{name}`](DATA/{name})"


FLEET_LINK = "[`raccolta/cyber/flotta_eta.json`](FLEET)"

# English renderings of the curated Italian incident entries in cyber-energia.json (hand-written)
PREC = {
    "CE-2015-UA": ("Western Ukraine: first blackout caused by a cyberattack", "About 225,000 customers lost power for a few hours; breakers opened remotely through the operators' own control systems", "Sandworm (GRU), per US and UK governments"),
    "CE-2016-UA": ("Kyiv: substation switched off by purpose-built grid malware", "About an hour of blackout in part of Kyiv; first malware written to speak grid protocols directly", "Sandworm (GRU)"),
    "CE-2021-VESTAS": ("Vestas: intrusion into corporate IT", "IT systems shut in several units; internal data compromised; company reported no impact on turbines", "not declared; some sources cite a ransomware group"),
    "CE-2022-KASAT": ("KA-SAT satellite network wiped: Enercon turbines lose remote link", "About 5,800 turbines (≈11 GW) without remote monitoring and control; they kept producing; over 95% reconnected by 19 Apr 2022", "Russia (GRU), per EU, US and UK (10 May 2022)"),
    "CE-2022-NORDEX": ("Nordex: ransomware on corporate IT", "Remote access to turbines switched off as a precaution; company says the incident stayed in internal IT", "claimed by a ransomware group"),
    "CE-2022-DWT": ("Deutsche Windtechnik (independent service provider): IT attack", "Remote monitoring of about 2,000 turbines switched off for about a day as a precaution; turbines kept running", "not confirmed; a ransomware group's claim reported"),
    "CE-2022-UA-IND2": ("Ukraine: second grid-malware attempt on high-voltage substations", "Detected and stopped before execution", "Sandworm (GRU)"),
    "CE-2023-DK": ("Denmark: 22 energy companies breached through unpatched perimeter firewalls", "Some firms isolated their networks ('island mode'); no customer impact", "not determined"),
    "CE-2023-IRGC-PLC": ("Water utilities (US and others): exposed industrial controllers defaced", "Screens replaced with political messages; plants moved to manual operation; no harm to drinking water", "CyberAv3ngers, linked to the IRGC"),
    "CE-2024-DEYE": ("Inverters remotely deactivated by their manufacturer in some markets", "Units blocked with an error message; maker cited an authorisation check, not an attack", "no attack: a manufacturer function"),
    "CE-2025-INVERTER": ("Reuters: undocumented communication parts in some Chinese inverters and batteries", "Possible channel around firewalls; makers not named; not confirmed by the US government", "n/a"),
    "CE-2025-NO": ("Norway: dam valve opened remotely for four hours", "About 500 litres per second released; no injuries", "pro-Russian hackers, per Norway's PST"),
    "CE-2025-PL": ("Poland: coordinated destructive attack on 30+ wind and solar farms and a CHP plant", "Remote control and communication with grid operators lost; control workstations wiped; power output not interrupted", "CERT Polska: a cluster it links to Russian services; ESET and Dragos: Sandworm"),
    "CE-2026-FR-FRIGO": ("France: supermarket refrigeration controllers tampered with remotely", "Overnight set-point changes (up to 50 °C or prolonged defrost); stock destroyed; mostly legacy controllers no longer updated", "see section 2: attribution reported, not confirmed by the monitor"),
    "CE-2026-BE-FRIGO": ("Second wave: 115+ stores in BE, NL, LU, SE, IE, EE", "Defrost functions triggered remotely", "not attributed"),
}
EXTRA_PREC = [
    ("2019-03-05", "sPower (USA): denial of service on vendor firewalls", f"Repeated reboots for about 12 hours; loss of visibility over about a dozen wind and solar sites (≈{X('spower_mw')} MW); no generation lost", "not attributed", EXT["spower_mw"][3], "high"),
    ("2026-08-08", "Poland follow-up (incident Dec 2025, disclosed 8 Aug 2026): second CHP plant reached over a private cellular network", f"A steam turbine and the process-water system of a CHP plant serving ≈{num(X('chp_residents'))} residents shut down briefly; heat supply not disrupted. CERT Polska calls the private cellular (APN) route the first such case observed; press accounts of the report place its start at a wind farm", "as for Poland 2025", EXT["chp_residents"][3], "high (route via wind farm: secondary)"),
    ("2026-08-23", "UK: small generator offline (incident in July, reported 23 Aug 2026)", f"Offline for {X('uk_days')} days; government said there was no risk to the wider energy system", "Iran-linked hackers blamed in press reports; no formal attribution", EXT["uk_days"][3], "medium"),
]


def blocks(V):
    B = []
    on, sh = V["on"], V["on_sh"]
    dk, de, gb, it = sh["DK"][0]["pre2010"], sh["DE"][0]["pre2010"], sh["GB"][0]["pre2010"], sh["IT"][0]["pre2010"]
    eu_off18 = V["off_sh"]["EU"][0]["2018+"]
    S = V["sys"]
    scC = V["scen"][2]
    scB = V["scen"][1]
    g = V["gamma"] or {}
    gdate = f"{date_en(g.get('period_start', ''))} to {date_en(g.get('period_end', ''))}" if g else "n/a"

    # 1 -----------------------------------------------------------------------------------------
    B.append(("h2", "key-points", "1. Key points"))
    B.append(("ul", [
        f"**Yes, a refrigeration-style attack could hit wind, but mainly the oldest and smallest turbines, and the likely effect is lost remote control, not damage.** "
        f"The pattern — series-made controllers, out of support, reachable remotely by contractors — fits pre-2010 onshore turbines and inverter clouds; it fits large offshore farms least (*assessment*, section 4).",
        f"**The old fleet is large where wind matters most.** Turbines commissioned before 2010 hold {pc(dk)} of onshore capacity in Denmark, {pc(de)} in Germany, "
        f"{pc(gb)} in the UK and {pc(it)} in Italy; offshore is young, with {pc(eu_off18)} of European capacity from 2018 or later (registers and GEM, 2026; {FLEET_LINK}).",
        f"**Concentration sits in control rooms, not parks.** {pc(V['de_dv'])} of German wind capacity is flagged as remotely controllable by its direct marketer (MaStR, 10 Nov 2026), "
        f"and one satellite-network attack in February 2022 cut the remote link to {num(X('kasat_turbines'))} Enercon turbines (≈{X('kasat_gw')} GW, gigawatts) in central Europe at once.",
        f"**One stopped OEM fleet could exceed the grid's design loss, but no real incident has cut output.** Continental Europe's reserves are sized for a {gw(V['ce_ref'])} GW loss; "
        f"one manufacturer's German fleet stopping at the 2025 peak would be ≈{gw(scC['hi'], 0)} GW (*estimate*). Every wind incident so far, including Poland in December 2025, removed monitoring, not generation.",
        "**Rules have arrived for big operators, not for farmers.** NIS2 is in force in Denmark, Germany, Poland, the Netherlands and Lithuania (2024–2026); the Dutch draft permit for IJmuiden Ver Gamma-B (October 2026) "
        "requires an EEA-based operator in control and a digital bill of materials down to software and firmware. Most small, old turbines sit below every threshold.",
    ]))
    B.append(("val", "*Assessment.* The direct answer for operators, regulators and investors: the analogy holds for the legacy, small-owner end of the fleet and for the shared platforms that reach it "
              "(service providers, direct marketers, inverter clouds). It breaks for modern offshore farms, whose realistic exposure is a vendor or supply-chain compromise, not an exposed panel. "
              "The impact most likely to matter is operational — losing the ability to curtail or restart turbines remotely — rather than physical."))

    # 2 -----------------------------------------------------------------------------------------
    el = V["el"]
    fr = el.get("CE-2026-FR-FRIGO", {})
    B.append(("h2", "refrigeration", "2. What happened in the refrigeration attacks, and why it worked"))
    B.append(("p", f"On the night of 11–12 October 2026, attackers remotely changed the set-points of connected refrigeration controllers in French supermarkets: temperatures were pushed up to 50 °C "
              f"or long defrost cycles were started, and stock was destroyed ({L('Al Jazeera, 13 Oct 2026', fr.get('link', '#'))}; {DL('cyber-energia.json')}). "
              f"Store counts range from initial estimates of {X('fr_stores_low')}–{X('fr_stores_low_hi')} (AP gave 700 on 13 Oct 2026) to more than {num(X('fr_stores_high'))} (Al Jazeera, 9 Nov 2026, as recorded in `report/agenti/cyber-energia.md`; article not re-read). "
              f"A second wave on 1–2 November hit more than {X('wave2_stores')} stores in Belgium, the Netherlands, Luxembourg, Sweden, Ireland and Estonia ({XL('wave2_stores', 'SecurityWeek, 3 Nov 2026')}). "
              "France's blood service reported that refrigeration settings at three sites were changed through a supplier's remote-monitoring software (EFS statement, 3 Nov 2026, via TechSpot)."))
    B.append(("p", "**Attribution, with its uncertainty.** Press reports on 9 November 2026 — Reuters (carried by Al-Monitor), AP, BBC and Al Jazeera, as recorded by the monitor's news agent — say French officials attributed the October attacks to Iran's "
              f"Islamic Revolutionary Guard Corps (IRGC) and asked for EU sanctions ({L('Al-Monitor, 9 Nov 2026', 'https://www.al-monitor.com/originals/2026/11/french-officials-blame-iran-refrigerator-hacks-vow-retaliation')}). "
              "**The monitor could not confirm this against a French government statement, and the reviewer could not open the press reports.** France's earlier public attributions of cyber operations pointed to Russian services "
              f"(in July 2026 the foreign minister blamed the FSB for a 'vast cyber campaign' in Europe: {L('AFP via LBCI, 13 Jul 2026', 'https://v7cdn.lbcgroup.tv/news/world-news/946246/paris-to-summon-russia-envoy-over-vast-cyber-campaign-in-europe-minist/en')}), pro-Russian groups had claimed some waves, "
              "and SentinelOne considers Russia-aligned groups credible suspects for the November wave. Any link between the IRGC and the November wave is unproven. Reliability of the attribution: medium (press reports only; no official text or technical evidence seen)."))
    B.append(("h3", "Why it worked: five conditions (concept level)"))
    B.append(("tab", ["Condition", "What public reporting says", "Source"], [
        ["End-of-life devices", "Most affected units were legacy products that no longer receive software or security updates", "maker's statements to AFP and The Guardian, Oct 2026 (via Facilities Dive)"],
        ["Reachable for contractors' convenience", f"Store control panels were reachable from the internet so maintenance contractors could adjust them remotely. Internet scanners counted ≈{num(X('fr_panels_before'))} exposed French panels on 11 Oct and {X('fr_panels_after')} by 14 Oct as operators took them offline", XL("fr_panels_before", "Infosecurity Magazine, Oct 2026")],
        ["Basic hygiene failures", "ANSSI (France's cybersecurity agency) cited weak passwords and missing elementary defences; the exact initial access route has not been officially confirmed", "ANSSI statements via press (medium)"],
        ["Many identical units, one change", "Hundreds of stores, a few vendor families, changed overnight; CERT-FR's alert covered three vendors' web supervisors", L("Reuters via The Star, 14 Oct 2026", "https://www.thestar.com.my/tech/tech-news/2026/10/14/copeland-dixell-refrigeration-systems-also-hacked-french-cybersecurity-agency-says")],
        ["Split responsibility", "Store, refrigeration contractor, device maker and a third-party software component each held part of the chain", "EFS statement, 3 Nov 2026; " + R1],
    ], "Concept level only: no product weaknesses, access routes or device details are described."))
    B.append(("val", f"*Assessment.* The decisive factor was not sophistication but reach: one remote path, unchanged for years, leading to many identical devices whose owners did not manage them. "
              f"The fastest fix also proved the point: the count of exposed French panels fell by {pc(1 - X('fr_panels_after') / X('fr_panels_before'))} in three days once CERT-FR asked operators to remove internet exposure."))

    # 3 -----------------------------------------------------------------------------------------
    B.append(("h2", "generations", "3. Three generations of turbines"))
    B.append(("p", "Every wind plant has the same layers: a turbine controller (a programmable controller in the nacelle and tower base for yaw, pitch, start and stop), a protection or 'safety chain' that brings the rotor to a safe state, "
              "a park network with SCADA (supervisory control and data acquisition) and a power plant controller that follows the grid operator's set-points, the substation, and remote paths for the manufacturer (OEM), "
              f"independent service providers (ISPs), the owner and power traders. What changes between generations is how each layer is built and connected ({R1}, section 1)."))
    B.append(("tab", ["", "Legacy, ≈1995–2010", "2010–2018", "Current, 2018+ (offshore 10–15+ MW)"], [
        ["Typical unit", "0.2–2 MW", "2–4 MW onshore, 3–8 MW offshore", "5–7 MW onshore, 10–15+ MW offshore"],
        ["Controller", "Proprietary; the OEM may no longer exist", "OEM platform, supported", "OEM platform, software-defined, remote firmware updates"],
        ["Park network", "Serial or fieldbus, later bridged to IP", "Ethernet/fibre rings, often flat (Tulsa study, 2017)", "Segmented zones and conduits (IEC 62443)"],
        ["Protocols", "Proprietary or legacy industrial protocols without authentication", "IEC 61400-25 / 61850 / 104; IEC 62351 security optional", "Same, with more encryption and certificates; cloud interfaces"],
        ["Remote paths", "Retrofitted dial-up, cellular routers, satellite, DSL", "VPN to OEM centre; ISP and trader links", "Fibre in the export cable; OEM fleet centres; cloud analytics"],
        ["Who operates", "Farmers, cooperatives, small utilities; ISPs; direct marketers", "Utilities and funds under OEM service contracts", "Large utilities under NIS2; OEM; TSO interface"],
        ["Patching reality", "Often impossible; only boundary controls", "OEM-scheduled, slowed by certification and grid-code testing", "OEM-managed; secure-development claims where certified"],
        ["Cyber certification", "None", "Rare", "Emerging: a Chinese OEM's farm control system to IEC 62443-3-3 SL2 (Sep 2026) and a Siemens Energy plant control system used offshore; turbine OEMs' certificates not public"],
        ["Exposure class (concept)", "Exposed panels and routers, shared credentials, old operating systems", "VPN appliances, OEM/ISP corporate IT, flat park networks", "Supply chain, OEM and cloud platforms, vendor conduits, substation and HVDC OT"],
        ["Strengths", "Small, varied, partly hardwired protection", "Standard protocols, OEM security teams", "Segmentation, security operations centres, remoteness, professional owners"],
        ["Remaining life", "0–10 years; repowering under way", "10–20 years", "25–30+ years"],
        ["Close to the refrigeration case?", "**Yes**", "Partly (vendor remote path)", "Mostly no, except via vendor or cloud compromise"],
    ], f"Source: {R1}, section 4 (Tulsa/Staggs et al. 2017; INL 2024; DOE 2020; IEC; DNV; CIGRE 2026; OEM material). Generation boundaries are approximate; the fleet data in section 5 use before 2010 / 2010–2017 / 2018+."))
    B.append(("h3", "Legacy fleet (≈1995–2010)"))
    B.append(("p", "Controllers came from the original manufacturers, several of which merged or disappeared. Remote access was added later — first dial-up, then cellular routers, DSL and, in central Europe, satellite. "
              f"The KA-SAT attack of 24 February 2022 showed what a single retrofitted link means: {num(X('kasat_turbines'))} Enercon turbines lost remote monitoring and control because their satellite modems were wiped, and many farms had no backup link ({XL('kasat_turbines', 'pv magazine, 1 Mar 2022')}). "
              f"It was not only a legacy problem: an average of ≈{X('kasat_gw') * 1000 / X('kasat_turbines'):.1f} MW per turbine points to a mix of older and middle-generation machines (*assessment*). "
              "After the warranty, service often passes to independent providers, and in Germany direct marketers must be able to read and curtail plants above "
              f"{X('eeg_kw')} kW (kilowatts) that sell through direct marketing ({XL('eeg_kw', 'section 10b EEG')}). Patching the 1990s controller is rarely possible; the realistic controls sit at the network boundary."))
    B.append(("h3", "Middle generation (2010–2018)"))
    B.append(("p", "IP park networks and standard data models (IEC 61400-25) arrived, with their security delegated to IEC 62351 and often left optional. OEM remote service centres began to reach whole fleets. "
              "All the documented incidents of this era were on the IT or vendor side: Vestas (November 2021), Nordex (March 2022) and Deutsche Windtechnik (April 2022) — in the last two, remote access to turbines was switched off as a precaution. "
              "In Denmark in May 2023, 22 energy companies, including small utilities with wind and solar assets, were breached through unpatched perimeter firewalls (SektorCERT, via Help Net Security, 14 Nov 2023). "
              "Patching is possible but scheduled by the OEM, and the owner rarely acts alone."))
    B.append(("h3", "Current generation (2018+, offshore 10–15+ MW)"))
    B.append(("p", f"OT (operational technology) networks are now designed with IEC 62443 zones and conduits. DNV's case study of a {X('dnv_nl_mw')} MW Dutch offshore farm reports segmentation 'at various levels' and that more than half of the OT services had cloud connectivity, "
              f"each subject to zone-and-conduit rules ({XL('dnv_nl_mw', 'DNV case study')}). More functions are software-defined — curtailment, grid-forming and fast-frequency response — and firmware is updated remotely. "
              "**Gap:** no public OEM document describing how controller firmware updates are signed and rolled back was found. Public IEC 62443 product or system certification is rare among the large Western OEMs (not found does not mean not certified)."))

    # 4 -----------------------------------------------------------------------------------------
    B.append(("h2", "analogy", "4. Where the analogy holds, and where it breaks"))
    B.append(("tab", ["Dimension", "Refrigeration, Oct–Nov 2026", "Legacy and small-owner wind", "Modern offshore wind", "Analogy"], [
        ["Contractor or vendor remote access", "Direct internet-facing panel", "Retrofitted modems, ISP and trader links", "OEM fleet centres and cloud, through controlled conduits", "Holds for legacy; partly for offshore"],
        ["End-of-life devices in service", "Many", "Yes: OEMs gone, 20+ years of operation", "Not yet", "Holds for legacy"],
        ["Many identical units", "Yes", "Within parks; varied across parks", "Large fleets per platform", "Holds"],
        ["Evidence of internet exposure", f"≈{num(X('fr_panels_before'))} French panels", f"{X('modat_wind')} wind systems in {X('modat_wind_countries')} countries (aggregate count)", "Not separated in public studies", "Holds, on a smaller scale than solar"],
        ["Safety layer independent of the network", "Partly (food-safety alarms)", "Hardwired safety chain (design principle)", "Same, plus certified protection", "Breaks — but see the open question below"],
        ["Grid protection", "n/a (a load)", "Distribution-grid protection, small units", "Grid codes, export-substation protection", "Breaks"],
        ["Owner's security capacity", "Store or small chain", "Farmer, cooperative, small utility", "Large utility with a security team", "Holds for legacy"],
        ["Regulatory floor", "Little until the CRA (2027)", "Mostly below NIS2 thresholds", "NIS2, network code, permit conditions", "Holds for legacy"],
    ], f"Sources: {R1}, section 2.2; exposure counts from {XL('modat_total', 'Modat and NCSC-NL via Security Magazine, 9 Oct 2026')}. Counts only; no locations, system types or access details are reported here."))
    B.append(("h3", "The weaker segment: legacy turbines, farmer and cooperative owners, inverters and clouds"))
    B.append(("p", f"Modat and the Dutch NCSC presented in October 2026 a scan finding {num(X('modat_total'))} wind and solar control systems reachable from the internet in {X('modat_countries')} countries; "
              f"{X('modat_wind')} of them were wind systems ({XL('modat_total', 'Security Magazine, 9 Oct 2026')}). Most of the rest were solar. For inverters the aggregation is larger: a DNV study for SolarPower Europe estimated that compromising about "
              f"{X('spe_gw')} GW of generation capacity could significantly affect the European grid ({XL('spe_gw', 'SolarPower Europe, 29 Apr 2025')}), and that {X('spe_brands')} inverter makers could each remotely manipulate more than 10 GW, "
              f"assuming remote access to 70% of each installed base (2023 data; {XL('spe_brands', 'full report')}). "
              f"Forescout, citing earlier research, puts at about {X('sundown_gw')} GW the capacity an attacker would need to push frequency down to the 49 Hz load-shedding level ({XL('sundown_gw', 'Forescout, Mar 2025')})."))
    B.append(("val", "*Assessment.* For small turbines the owner is not a security organisation, the device is out of support, a third party holds remote access, and the plant is below NIS2 thresholds — the refrigeration recipe. "
              "The impact per site is small; the systemic risk comes from aggregation in a service provider, a direct marketer's trading platform or an inverter cloud. Of these, the inverter cloud is the larger aggregation risk."))
    B.append(("h3", "Modern offshore farms"))
    B.append(("p", "Large offshore farms combine segmented OT, 24/7 security monitoring at large owners, protection relays at the export substation and physical remoteness. Their exposure is of a different class: "
              "a compromised OEM fleet centre or cloud service that reaches many farms, a long supply chain, and concentration — one farm is 1–2 GW behind one export system. "
              "A 2024 simulation by Concordia University and Hydro-Québec showed that corrupted sensor data inside an HVDC converter network could, in principle, amplify grid oscillations; no real incident is reported."))
    B.append(("p", "**Open question — how independent is the protection system?** The argument that 'turbines fail safe' rests on the protection system acting on physical limits (overspeed, vibration) regardless of commanded set-points. "
              "The research could not retrieve the clause text in DNV-ST-0438 or IEC 61400-1 on how far protection must be separated from the control system and network, nor whether any networked parameter can change protection thresholds. "
              "Until that is checked, 'mass physical damage is hard' is a design principle, not a verified fact. No cyber-induced turbine damage is publicly documented as of 10 November 2026."))

    # 5 -----------------------------------------------------------------------------------------
    em = V["emod"]
    B.append(("h2", "fleet", "5. Fleet age and concentration by country"))
    B.append(("p", f"Registers give every turbine in Denmark (Energistyrelsen, data to September 2026), Germany (Marktstammdatenregister, 10 Nov 2026) and the UK (REPD, sites ≥150 kW, Q2 2026). "
              f"For other countries the monitor uses Global Energy Monitor's tracker (February 2026), which only covers projects of at least 10 MW and so **understates old fleets** ({FLEET_LINK})."))
    B.append(("fig", "onshore", f"**Figure 1.** Onshore wind capacity by commissioning period, share of MW (megawatts) in operation. Registers: DK end-September 2026, DE 10 Nov 2026, UK Q2 2026; * = GEM projects ≥10 MW, February 2026. "
              f"Right-hand figure: share before 2010. Source: {FLEET_LINK}, read 10 Nov 2026."))
    B.append(("p", f"Denmark has {num(V['dk_turb_pre'])} onshore turbines from before 2010 ({gw(on['DK']['pre2010'])} GW), averaging {num(V['dk_pre_avg_mw'], 1)} MW each; {num(V['dk_small_n'])} of its {num(V['dk_on_n'])} onshore turbines "
              f"({gw(V['dk_small_mw'])} GW) are smaller than 1 MW. {gw(V['dk_20y_on'], 2)} GW onshore and {gw(V['dk_20y_off'], 2)} GW offshore are 20 or more years old. "
              f"Germany has {gw(on['DE']['pre2010'])} GW onshore from before 2010 ({num(V['de_turb_pre'])} turbines) and {gw(V['de_20y'])} GW already 20 or more years old, {gw(V['de_2000'])} GW of it from 2000 or earlier. "
              f"In the Baltic states, Sweden and Finland, {pc(min(sh[c][0]['2018+'] for c in ('LT','LV','EE','SE','FI')))}–{pc(max(sh[c][0]['2018+'] for c in ('LT','LV','EE','SE','FI')))} of the dated capacity is from 2018 or later (GEM). "
              f"Italy's pre-2010 share ({pc(it)}) is a GEM figure and probably low."))
    B.append(("fig", "germany", f"**Figure 2.** Germany: onshore capacity in operation by commissioning period, split by whether the brand is still active (MW; brands no longer active: NEG Micon, REpower/Senvion, Tacke, Fuhrländer, DeWind, BARD, Adwen, Südwind, AN, Enron; only brands with >50 MW per period counted). "
              f"Source: Marktstammdatenregister, 10 Nov 2026, via {FLEET_LINK}."))
    B.append(("p", f"**Orphan brands.** In Germany {gw(V['de_orphan_on_tot'])} GW onshore and {gw(V['de_orphan_off_tot'])} GW offshore come from brands that no longer exist; their controllers are maintained, if at all, by independent providers or retrofitters. "
              f"Natural persons are the registered operators of {gw(V['de_nat_tot'], 2)} GW of onshore capacity, {gw(V['de_nat_pre'], 2)} GW of it from before 2010 — a heavy understatement of citizen ownership, because citizen wind farms are usually registered as companies. "
              f"Germany has {num(V['de_ops'])} registered operators. Turbines from Chinese-owned makers are marginal: {V['de_vensys']['turbine']} units ({V['de_vensys']['mw']} MW) from Vensys, a German designer controlled by Goldwind, in Germany; none in the Danish register."))
    B.append(("fig", "offshore", f"**Figure 3.** Offshore wind capacity by commissioning period, share of MW in operation. DK includes Thor (2026). Source: {FLEET_LINK} (ENS, MaStR, REPD, GEM), read 10 Nov 2026."))
    B.append(("p", f"Offshore is young, and it is concentrated. In EMODnet's North Sea and Baltic data, the {em['pre2010']['farms']} farms built before 2010 total {gw(em['pre2010']['mw'])} GW (average {num(em['pre2010']['avg'])} MW per farm); "
              f"the {em['2010-2017']['farms']} farms of 2010–2017 average {num(em['2010-2017']['avg'])} MW and the {em['2018+']['farms']} farms from 2018 average {num(em['2018+']['avg'])} MW ({FLEET_LINK}; EMODnet lags the registers)."))
    B.append(("h3", "Control-room concentration"))
    B.append(("tab", ["Actor", "Public figure", "Source"], [
        ["Vestas", f"{X('vestas_gw')} GW and more than {num(X('vestas_turbines'))} turbines under active service (end-2025)", XL("vestas_gw", "Vestas AR 2025 via GreentechLead")],
        ["Siemens Gamesa", f"More than {num(X('sg_turbines'))} remotely connected turbines monitored from its Brande centre (company figure, undated page; the same count appears in 2021 coverage)", XL("sg_turbines", "Siemens Gamesa (undated page)")],
        ["Enercon (KA-SAT case)", f"{num(X('kasat_turbines'))} turbines (≈{X('kasat_gw')} GW) lost their remote link through one satellite network, 24 Feb 2022; today Enercon has {num(X('enercon_de_turbines'))} turbines and {X('enercon_de_gw')} GW onshore in Germany", XL("kasat_turbines", "pv magazine") + "; " + XL("enercon_de_gw", "MaStR")],
        ["Direct marketers (DE)", f"{pc(V['de_dv'], 1)} of German wind capacity flagged as remotely controllable by its direct marketer", "MaStR 10 Nov 2026, " + FLEET_LINK],
        ["Independent service providers", f"Deutsche Windtechnik switched off remote monitoring of ≈{num(X('isp_turbines'))} turbines in 2022; **no reliable public figure** for the ISP market share", DL("cyber-energia.json")],
        ["Orphan brands", f"{gw(V['de_orphan_on_tot'])} GW onshore in Germany with no active OEM", FLEET_LINK],
    ], "Figures are as published by each company and differ in scope (service, monitoring, control); none says how many turbines one centre can command at once."))
    B.append(("val", "*Assessment.* The direct marketers' remote-control channel is the closest wind equivalent to the refrigeration vendor cloud: a third command path, besides OEM/ISP and owner, into old and new turbines alike, concentrated in a few trading platforms. "
              f"The natural mitigation is repowering: WindEurope expects about {X('decom_gw')} GW to be decommissioned in Europe in 2026–2030 ({XL('decom_gw', 'WindEurope, Feb 2026')})."))

    # 6 -----------------------------------------------------------------------------------------
    dk25, de25 = S["DK_2025"], S["DE_2025"]
    B.append(("h2", "impact", "6. System impact: what a simultaneous loss would mean"))
    B.append(("p", f"Continental Europe — including Germany, the Netherlands, Poland, western Denmark (DK1), Italy and, since February 2025, the Baltic states — sizes its frequency containment reserve for a **reference incident of {num(V['ce_ref'])} MW** "
              f"(EU System Operation Guideline, art. 153). The Nordic system (Sweden, Finland, Norway, eastern Denmark) is sized for its largest single loss, **{num(V['nordic'])} MW**; Great Britain's infrequent infeed-loss limit is {num(V['gb_max'])} MW ({FLEET_LINK}; ENTSO-E; Fingrid; NESO)."))
    B.append(("p", f"Wind is large against these yardsticks. In 2025 wind met {pc(dk25['quota'])} of Danish gross consumption and exceeded consumption in {dk25['ore_vento_sopra_consumo']} hours; eastern Denmark's wind peaked at {num(dk25['max_vento_DK2_mw'])} MW (Energinet). "
              f"German wind peaked at {de25['max_vento_gw']} GW on 26 October 2025 against a load of {de25['carico_in_quel_momento_gw']} GW, and averaged ≈{num(V['de_avg_out_gw'])} GW over the year (Fraunhofer ISE Energy-Charts)."))
    B.append(("fig", "scen", f"**Figure 4.** Order-of-magnitude loss scenarios, GW (gigawatts) lost at once, against reserve sizing. *Estimates*, not network studies: each fleet is assumed to produce at the German average "
              f"({pc(V['de_cf_avg'])} of capacity in 2025) or at the 26 Oct 2025 peak ({pc(V['de_cf_peak'])}), with no ramp time and no interconnector help; German capacity from MaStR 10 Nov 2026 is applied to 2025 output. "
              f"B uses the average German onshore turbine ({num(V['de_avg_turb'], 2)} MW). Sources: {FLEET_LINK}; {DL('cyber-energia.json')} (Hornsea 1+2, {num(V['hornsea_mw'] or 0)} MW); Enercon fleet: {XL('enercon_de_gw', 'MaStR')}."))
    B.append(("val", f"*Assessment (estimates).* A stop of one service provider's turbines would be ≈{gw(scB['lo'])} GW at average output and ≈{gw(scB['hi'])} GW at peak — near the {gw(V['ce_ref'])} GW line only in the best wind. "
              f"One OEM's German onshore fleet stopping in high wind (≈{gw(scC['lo'])}–{gw(scC['hi'])} GW) would exceed the reference incident by a factor of {scC['lo'] / V['ce_ref']:.1f}–{scC['hi'] / V['ce_ref']:.1f}. "
              "But turbines do not stop instantly, control centres usually act park by park, and no public evidence shows one command could stop a national fleet. The worrying case is therefore a prepared, coordinated attack on many SCADA systems at once, or a manipulation of protection settings across many units — not a single click."))
    B.append(("h3", "Why every real incident so far removed monitoring, not generation"))
    B.append(("p", f"KA-SAT (2022), Deutsche Windtechnik (2022), Nordex (2022) and Poland (December 2025) all ended the same way: turbines kept producing in automatic mode while owners lost visibility and remote control. In Poland, more than {X('pl_sites')} wind and solar sites lost remote control at their grid-connection substations and control workstations were wiped, "
              f"yet output did not stop ({XL('pl_sites', 'CERT Polska, 30 Jan 2026')}). Turbines are designed to run unattended; the remote link is for optimisation, curtailment and restart."))
    B.append(("val", f"*Assessment.* The real system risk of 'monitoring lost' is indirect: the grid operator cannot curtail wind when supply exceeds demand — as in Denmark's {dk25['ore_vento_sopra_consumo']} such hours in 2025 — or restart plants after a blackout. "
              f"The non-cyber precedent shows how losses combine: on 9 August 2019 an offshore farm lost about {X('gb2019_mw')} MW alongside a gas plant after a lightning strike, and about {X('gb2019_customers')} million customers were disconnected in Great Britain ({XL('gb2019_mw', 'Ofgem, Jan 2020')}; Hornsea 1 deloaded by 737 MW)."))

    # 7 -----------------------------------------------------------------------------------------
    B.append(("h2", "precedents", "7. Precedents, 2015–2026"))
    rows = []
    for k, (case, eff, att) in PREC.items():
        e = el.get(k)
        if not e:
            warn(f"{k} missing from cyber-energia.json")
            continue
        rows.append((e["data_evento"], case, eff, att, e["link"], e.get("affidabilita", "")))
    rows += EXTRA_PREC
    rows.sort(key=lambda r: r[0])
    rel = {"alta": "high", "media": "medium", "bassa": "low"}
    B.append(("tab", ["Date", "Case", "Effect", "Attribution", "Reliability"],
              [[date_short(r[0]), L(r[1], r[4]), r[2], r[3], rel.get(r[5], r[5])] for r in rows],
              f"Sources: {DL('cyber-energia.json')} (curated entries, 9 Nov 2026) and {R2}, section 5. Reliability refers to the event, not the attribution. No successful cyberattack on a European offshore wind farm is known as of 10 November 2026."))

    # 8 -----------------------------------------------------------------------------------------
    B.append(("h2", "rules", "8. Rules and defences"))
    B.append(("tab", ["Country", "NIS2 law", "In force", "Note"], [
        ["Denmark", "Energy-sector act on strengthened preparedness (Act no. 258 of 6 Mar 2025); general NIS 2 Act (Act no. 434 of 6 May 2025)", "7 Mar 2025 (energy); 1 Jul 2025 (general)", "threat level for destructive attacks: medium"],
        ["Germany", "NIS2UmsuCG (amends BSIG and EnWG)", "6 Dec 2025", f"published in the Federal Law Gazette on 5 Dec 2025 (BGBl. 2025 I No. 301); KRITIS threshold for generation {X('kritis_mw')} MW"],
        ["Lithuania", "Amended Law on Cyber Security", "18 Oct 2024", "further amended in 2026 (not verified)"],
        ["Poland", "Amended KSC Act of 23 Jan 2026 (Dz.U. 2026 poz. 252)", "3 Apr 2026", "published 2 Mar 2026; in force one month later (official ELI register)"],
        ["Netherlands", "Cyberbeveiligingswet (with the CER law, Wwke)", "15 Aug 2026", "'thousands of organisations' in scope (Rijksoverheid); about 8,000 per cyber-energia.json"],
        ["Latvia, Estonia", "—", "—", "**Missing:** not covered by the research notes"],
    ], f"Sources: {R2}, section 4.1 (ECSO and other trackers, Rijksoverheid); {DL('cyber-energia.json')}; reviewer's checks of the Danish, German and Polish gazettes and registers, 10 Nov 2026. NIS2 transposition deadline: 17 Oct 2024."))
    B.append(("ul", [
        "**Cyber Resilience Act** (Regulation (EU) 2024/2847): reporting of actively exploited vulnerabilities since 11 Sep 2026; full application from 11 Dec 2027. It covers controllers, gateways and inverters sold as products — not the installed base.",
        "**Network Code on Cybersecurity** (Delegated Regulation (EU) 2024/1366): in force since 13 Jun 2024; national authorities are still designating high- and critical-impact entities. No final EU list was found.",
        "**Radio Equipment Directive** delegated act 2022/30: cybersecurity requirements for wireless equipment mandatory since 1 Aug 2025.",
        f"**Lithuania**: remote access from high-risk countries to solar, wind and storage above {X('lt_kw')} kW is banned; the law applied to new plants from 1 May 2025, existing plants had to comply by {X('lt_existing')}, and grid operators can now disconnect non-compliant plants ({XL('lt_kw', 'LRT, 12 Nov 2024')}; {XL('lt_existing', 'pv magazine, 5 Jun 2026')}).",
        f"**Netherlands, IJmuiden Ver Gamma-B draft permit** (October 2026): an operator based in the EEA keeps operational control and documents cybersecurity for itself and its ICT suppliers (rule 21); "
        f"at least 75% of turbines not from China (so no more than {X('gamma_cn_max')}% from China), drive trains and generators not from China, and digital bills of materials for hardware with digital functions and the software and firmware in it, with maker and country of origin (rule 22) ({XL('gamma_cn_max', 'RVO draft permit')}). "
        f"The joint application window for Gamma-A and Gamma-B runs {gdate} ({DL('wind-calendar.json')}).",
        "**United Kingdom**: the government blocked Mingyang's planned Ardersier turbine factory on 25 Mar 2026, saying it could not support the use of its turbines in UK offshore wind projects on national-security grounds ([Scottish Financial Review, 25 Mar 2026](https://scottishfinancialreview.com/2026/03/25/uk-govt-blocks-chinese-plan-for-1500-scots-jobs/)); in August 2026 a government source said there were no plans to reverse the decision ([energy-pedia, 12 Aug 2026](https://www.energy-pedia.com/news/united-kingdom/swinney-urges-burnham-to-rethink-%C2%A31-5bn-wind-factory-ban-204932)).",
        "**EU**: a Cybersecurity Act revision proposed in January 2026 would create a process to name high-risk suppliers; since April 2026 EU funds no longer go to projects using inverters from high-risk suppliers. Germany has no law excluding Chinese turbines; Denmark has no specific public measure.",
        "**Insurance**: the Lloyd's market's cyber-war clauses (LMA5564–5567, listed in the LMA model cyber clauses, version of 19 Mar 2026) exclude state-backed cyber operations, so attribution can decide cover — which is why the unconfirmed IRGC attribution matters for claims.",
    ]))
    B.append(("h3", "Good practices, by who you are"))
    B.append(("tab", ["Owners of old turbines (farmers, cooperatives, small utilities)", "Offshore and large operators", "Ports and O&M bases"], [
        ["Take control panels and routers off the open internet; it was the first CERT-FR instruction and it worked", "Treat OEM fleet centres and cloud services as untrusted conduits: gated, logged, time-limited, with a kill switch", "Port-side O&M bases and control rooms are part of the farm's OT: segment them from port IT and tenants"],
        ["Ask the service provider and direct marketer in writing: who can connect, from where, with what authentication, and how they notify incidents", "Contract for software bills of materials and signed, staged firmware updates; ask OEMs for their IEC 62443 status", "Plan for physical and cyber security of landfall substations and export-cable routes together"],
        ["Inventory end-of-life devices (controllers, modems, satellite and 2G/3G links) and budget replacement or repowering", "Rehearse manual and island operation, and loss of remote control across many farms at once", "Include wind clients in port crisis exercises: a loss of remote control means more vessel and technician trips"],
        ["Keep a backup communications link (the Enercon lesson) and a manual stop procedure", "Monitor OT networks for anomalous mass commands (many units changed together, at night)", "Share indicators with sector CERTs (SektorCERT, Z-CERT/NCSC, CERT Polska)"],
        ["Join sector information sharing even below NIS2 thresholds", "Check protection-system independence with the OEM and certifier (section 4)", "Watch GNSS interference near Baltic bases (port-risk.json)"],
    ], f"Sources: {DL('cyber-energia.json')} (good practices), {R1} section 5, {R2} section 6. Practices are generic and defensive."))
    prow = [[p["name"], p["country"], f"{p['score']:.1f}", p["level"]] for p in V["ports"]]
    B.append(("tab", ["Offshore wind base port", "Country", "Port Risk score (1–25)", "Level"], prow,
              f"Source: {DL('port-risk.json')}, reference date {date_en(V['pr_date'])}. The index has no cyber indicator: its security group covers physical events, GNSS interference and shadow-fleet tankers, so these scores say nothing about OT exposure."))

    # 9 -----------------------------------------------------------------------------------------
    B.append(("h2", "watch", "9. Indicators to watch and three scenarios"))
    B.append(("ul", [
        "**Official confirmation of the refrigeration access route** by ANSSI or CERT-FR (exposed interface, contractor platform or third-party component): it decides which wind segment the analogy fits best.",
        "**A French government statement** on the IRGC attribution, EU sanctions, and any link to the November wave.",
        "**Any sector-CERT report of tampering with wind or solar control panels** in DK, DE, NL, PL or the Baltic states — the first sign that the 'pick a brand of exposed controller' pattern has reached wind.",
        "**Follow-up on exposure counts** by NCSC-NL and Modat: a fall like France's after the refrigeration alert would show owners reacting.",
        f"**Gamma-A/B applications** ({gdate}): whether bidders accept the EEA-control, origin and bill-of-materials conditions without fewer bids.",
        "**Network Code designations** of high- and critical-impact entities, and whether aggregators and direct marketers are included.",
        "**OEM disclosures** on IEC 62443 certification and firmware signing; the Cybersecurity Act revision; CRA full application on 11 Dec 2027.",
    ]))
    B.append(("val", "*Assessment — scenario 1, base case: opportunistic tampering at the small end.* Hacktivists or state-linked groups change settings or stop a few small, internet-exposed turbines or solar sites, as with dams and water plants. "
              "Local loss of output, strong media attention, no grid effect. Recognise it by: claims with screenshots of wind panels; a national CERT alert naming wind; exposure counts falling afterwards."))
    B.append(("val", "*Assessment — scenario 2, escalation: a shared platform is compromised.* An ISP, direct-marketing platform or OEM service network is hit by ransomware or a wiper; thousands of turbines lose remote control for days (KA-SAT type). "
              f"Output continues, but curtailment and restart become manual; costs fall on balancing and O&M logistics, including ports. Recognise it by: an operator announcing remote access switched off; grid-operator notices of manual curtailment; more than ≈{num(X('isp_turbines'))} turbines affected."))
    B.append(("val", f"*Assessment — scenario 3, severe tail: a prepared, coordinated operation.* A state actor with long access to an OEM platform, many SCADA systems or substations causes a simultaneous loss of several GW, above the {gw(V['ce_ref'])} GW reference incident. "
              "Low likelihood, high impact; it needs time and capability unlike the refrigeration campaign. Recognise it by: government attribution of pre-positioning in wind OT; an OEM security advisory to all customers; frequency events with simultaneous wind trips."))

    # 10 ----------------------------------------------------------------------------------------
    B.append(("h2", "method", "10. Method, sources and limits"))
    B.append(("ul", [
        f"**Main material:** two research notes of 10 November 2026 ({R1}; {R2}), the curated incident and rules file {DL('cyber-energia.json')} (9 Nov 2026), {DL('port-risk.json')} and {DL('wind-calendar.json')} (10 Nov 2026), and the fleet aggregates in {FLEET_LINK} (10 Nov 2026).",
        "**Fleet data:** Energistyrelsen register (data to end-September 2026), Marktstammdatenregister export (10 Nov 2026, dl-de/by-2-0), DESNZ REPD (Q2 2026, OGL v3), Global Energy Monitor wind tracker (February 2026, CC BY 4.0, projects ≥10 MW), EMODnet (CC BY 4.0), WindEurope 2025 statistics.",
        "**Limits:** GEM understates old and small fleets (coverage 48–97% by country); the Danish register has no owner type; the German 'natural person' field understates citizen ownership; EMODnet lags the registers. No public data on ISP market share or on the share of turbines linked by satellite or cellular networks. **Missing:** NIS2 dates for Latvia and Estonia.",
        "**Scenarios** in section 6 are orders of magnitude with stated simplifications, not network studies. Section 9 scenarios are assessments without probabilities.",
        "**Unverified or secondary:** the IRGC attribution (press only); the UK July 2026 case (secondary sources); that the Polish APN route started at a wind farm (press reading of CERT Polska's report); the French exposed-panel counts (1,825 and 537); protection-system independence clauses (DNV-ST-0438, IEC 61400-1); OEM IEC 62443 status.",
        "**Scope:** defensive. The report deliberately omits exploit details, vulnerability identifiers, product weaknesses, lists or locations of exposed systems and attack steps.",
        "**Related reports, not repeated here:** [Offshore Wind in Northern Europe](offshore-wind-2026-11.html) (targets, auctions, ports) and [Northern Europe: Ports and Energy](northern-europe-2026-11.html) (ports, gas, Baltic security).",
    ]))
    B.append(("review",))
    return B


# ------------------------------------------------------------------------------------------------
# Rendering
# ------------------------------------------------------------------------------------------------
REVIEW = {
    "log": "report/revisioni/wind-cyber-2026-11.md",
    "title": "Review · 10 November 2026",
    "text": ("Independent review on 10 November 2026 under report/STANDARD.md: 100 claims checked against the data files, the research notes and, where reachable, the original sources "
             "(80 confirmed, 15 corrected, 5 not verifiable from here). Main corrections: the early French store count (500–700, not 250–350); Denmark's NIS2 law for energy "
             "(Act no. 258, in force 7 Mar 2025); German and Polish NIS2 dates confirmed in the official gazettes; Lithuania's deadline for existing plants (1 June 2026); "
             "the UK Mingyang statement (a government source, not Downing Street); the Polish follow-up, now from CERT Polska (heat supply not disrupted); "
             "the inverter-concentration figure and its assumption; the LMA clause date. Safety: two links whose articles reproduce device-level detail were replaced; "
             "no exploit details, identifiers, credentials or locations remain. Not verifiable from here: the IRGC attribution (press only), the 1,000-store and EFS figures, "
             "the French exposed-panel counts and ANSSI's wording, SentinelOne's assessment."),
}

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
.scope{font-size:14px;background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:10px 14px;margin:0 0 20px}
h2{font:600 24px/1.25 "IBM Plex Serif",Georgia,serif;margin:48px 0 12px;padding-top:8px;scroll-margin-top:16px}
h3{font:600 18px/1.3 "IBM Plex Sans",sans-serif;margin:28px 0 8px}
p,ul{margin:0 0 16px}
ul{padding-left:1.2em}
li{margin:0 0 10px}
strong{font-weight:600}
code{font:14px "IBM Plex Mono",ui-monospace,monospace;background:var(--band);padding:1px 4px;border-radius:3px;overflow-wrap:anywhere}
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
@media (max-width:600px){.wide{display:none}.narrow{display:block}td{min-width:9em}td:first-child{min-width:7em}}
details{margin-top:6px;font-size:13px}
summary{cursor:pointer;color:var(--soft)}
.review{margin:40px 0 0;padding:16px 18px;background:var(--card);border:1px dashed var(--soft);border-left:3px solid var(--soft);border-radius:0 8px 8px 0;font-size:15px}
.review h2{font:600 13px/1.4 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--soft);margin:0 0 10px;padding:0}
.review p{margin:0 0 10px}
footer{margin-top:56px;padding-top:16px;border-top:1px solid var(--rule);font-size:14px;color:var(--soft)}
footer .sig{font-weight:600;color:var(--ink)}
"""

SCOPE_NOTE = ("Scope: a defensive risk briefing for operators, regulators and investors. It discusses architectures, exposure classes and impacts; "
              "it contains no exploit details, vulnerability identifiers, product weaknesses, lists or locations of exposed systems, or attack steps.")


def fix_links(t, data_prefix, fleet_path, rep_prefix):
    t = t.replace("](DATA/", f"]({data_prefix}").replace("](FLEET)", f"]({fleet_path})")
    return re.sub(r"\]\(((?:offshore-wind|northern-europe)-[\d-]+\.html)\)", lambda m: f"]({rep_prefix}{m.group(1)})", t)


def inline_md(t):
    return fix_links(t, "../docs/data/", "../raccolta/cyber/flotta_eta.json", "../docs/report/en/")


def inline_html(t):
    t = esc(t)
    t = fix_links(t, "../../data/", "https://github.com/", "")
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    # the fleet file is not published under docs/: show the path, no dead link
    t = t.replace('<a href="https://github.com/"><code>raccolta/cyber/flotta_eta.json</code></a>', "<code>raccolta/cyber/flotta_eta.json</code>")
    return t


def render_md(B, meta, figs):
    o = [f"# {meta['title']}", "", f"*{meta['subtitle']}*", "",
         f"Gabriele Giuliani · Geo-economic Risk Monitor · {meta['edition']} · data read on {meta['read']}", "",
         f"*{SCOPE_NOTE}* Every number has a source and a date. Paragraphs marked *Assessment* are the monitor's reasoning, not facts.", "",
         "**Contents:** " + " · ".join(f"[{re.sub(r'^\d+\. ', '', b[2])}](#{b[1]})" for b in B if b[0] == "h2") + " · [Review](#review)", ""]
    for b in B:
        k = b[0]
        if k == "h2":
            o += [f'<a id="{b[1]}"></a>', "", f"## {b[2]}", ""]
        elif k == "h3":
            o += [f"### {b[1]}", ""]
        elif k in ("p", "val"):
            o += [inline_md(b[1]), ""]
        elif k == "ul":
            o += [f"- {inline_md(x)}" for x in b[1]] + [""]
        elif k == "tab":
            o += ["| " + " | ".join(b[1]) + " |", "|" + "---|" * len(b[1])]
            o += ["| " + " | ".join(inline_md(str(c)).replace("|", "/") for c in r) + " |" for r in b[2]]
            o += ["", f"*{inline_md(b[3])}*" if b[3] else "", ""]
        elif k == "fig":
            alt = re.sub(r"\*\*|\[|\]\([^)]*\)", "", b[2]).split(". ")[1] if ". " in b[2] else "chart"
            o += [f"![{alt}]({figs[b[1]]})", "", inline_md(b[2]), ""]
        elif k == "review":
            o += ['<a id="review"></a>', "", "---", "", f"### {REVIEW['title']}", "", REVIEW["text"], "", f"Review log: [{REVIEW['log']}](revisioni/wind-cyber-2026-11.md).", ""]
    o += ["---", "", "Gabriele Giuliani · Geo-economic Risk Monitor · " + meta["edition"], "", meta["ai_note"], ""]
    return "\n".join(o)


def render_html(B, meta, svg):
    o = ["<!doctype html>", '<html lang="en-GB">', "<head>", '<meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         f"<title>{esc(meta['short'])}</title>", f'<meta name="description" content="{esc(meta["subtitle"])}">',
         '<link rel="preconnect" href="https://fonts.googleapis.com">', '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@600&display=swap" rel="stylesheet">',
         f"<style>{CSS}</style>", "</head>", "<body>", '<main class="page">',
         '<a class="back" href="../../index.html">← Back to the map</a>',
         f'<p class="kicker">Risk briefing · {esc(meta["edition"])}</p>',
         f"<h1>{esc(meta['title'])}</h1>", f'<p class="sub">{esc(meta["subtitle"])}</p>',
         f'<p class="meta">Gabriele Giuliani · Geo-economic Risk Monitor · data read on {esc(meta["read"])}. Every number has a source and a date; '
         f'boxes marked <em>Assessment</em> are the monitor\'s reasoning, not facts. Related: <a href="offshore-wind-2026-11.html">Offshore Wind in Northern Europe</a> · '
         f'<a href="northern-europe-2026-11.html">Northern Europe: Ports and Energy</a>.</p>',
         f'<p class="scope">{esc(SCOPE_NOTE)}</p>',
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
            o.append(f"<p>{inline_html(b[1])}</p>")
        elif k == "val":
            m = re.match(r"^\*Assessment([^*]*?)\.\*\s*", b[1])
            tag = "Assessment" + (m.group(1) if m else "")
            txt = b[1][m.end():] if m else b[1]
            o.append(f'<aside class="assess"><span class="tag">{esc(tag)}</span>{inline_html(txt)}</aside>')
        elif k == "ul":
            o.append("<ul>" + "".join(f"<li>{inline_html(x)}</li>" for x in b[1]) + "</ul>")
        elif k == "tab":
            t = ['<div class="tabella"><table><thead><tr>' + "".join(f'<th scope="col">{esc(x)}</th>' for x in b[1]) + "</tr></thead><tbody>"]
            for r in b[2]:
                t.append("<tr>" + "".join(f"<td>{inline_html(str(c))}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            o.append("".join(t))
            if b[3]:
                o.append(f'<p class="note">{inline_html(b[3])}</p>')
        elif k == "fig":
            g = svg[b[1]]
            o.append(f'<figure><div class="chart"><div class="wide">{g["wide"]}</div><div class="narrow">{g["narrow"]}</div></div>'
                     f'<figcaption>{inline_html(b[2])}</figcaption>'
                     f'<details><summary>Chart data as a table</summary>{g["table"]}</details></figure>')
        elif k == "review":
            o.append(f'<aside class="review" id="review"><h2>{esc(REVIEW["title"])}</h2><p>{esc(REVIEW["text"])}</p>'
                     f'<p>Review log: <code>{esc(REVIEW["log"])}</code>.</p></aside>')
    o.append(f'<footer><p class="sig">Gabriele Giuliani · Geo-economic Risk Monitor</p><p>{esc(meta["edition"])}. {inline_html(meta["ai_note"])}</p>'
             '<p><a href="../../index.html">← Back to the map</a></p></footer>')
    o += ["</main>", "</body>", "</html>"]
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", help="edition YYYY-MM (default: current month)")
    args = ap.parse_args()
    today = dt.date.today()
    month = args.month or today.strftime("%Y-%m")
    y, m = map(int, month.split("-"))
    edition = f"{MONTHS[m - 1]} {y}"
    V = compute()
    B = blocks(V)
    meta = {"title": "Could a Refrigeration-Style Cyberattack Hit Wind Farms? Old vs New Turbines",
            "short": "Wind Farm Cyber Risk",
            "subtitle": f"What the October–November 2026 supermarket-refrigeration attacks mean for wind: three turbine generations, fleet age and control-room concentration by country, system impact, rules and defences — {edition}.",
            "edition": edition, "read": date_en(today.isoformat()),
            "ai_note": ("Note on AI use: this report was prepared with an AI assistant (Claude, Anthropic), which wrote the build script, the calculations, the charts and the draft text "
                        "from the monitor's data files and two research notes that were also prepared with AI assistance and cite their sources. Numbers come from the data files and linked sources; "
                        "assessments and estimates are marked. The independent review (10 November 2026) was also carried out with an AI assistant; its log lists every check. Gabriele Giuliani is responsible for publication.")}
    os.makedirs(OUT_SVG, exist_ok=True)
    os.makedirs(OUT_HTML, exist_ok=True)
    tabs = chart_tables(V)
    svg, figs = {}, {}
    for key, fn in [("onshore", chart_onshore), ("germany", chart_germany), ("offshore", chart_offshore), ("scen", chart_scen)]:
        svg[key] = {"wide": fn(V, True), "narrow": fn(V, False), "table": tabs[key]}
        name = f"wcy-{month}-{key}.svg"
        with open(os.path.join(OUT_SVG, name), "w", encoding="utf-8") as f:
            f.write(svg[key]["wide"])
        figs[key] = f"grafici/{name}"
    with open(os.path.join(ROOT, "report", f"wind-cyber-{month}.md"), "w", encoding="utf-8") as f:
        f.write(render_md(B, meta, figs))
    with open(os.path.join(OUT_HTML, f"wind-cyber-{month}.html"), "w", encoding="utf-8") as f:
        f.write(render_html(B, meta, svg))
    print(f"written: report/wind-cyber-{month}.md, docs/report/en/wind-cyber-{month}.html, {len(svg)} charts; {len(WARN)} warnings")


if __name__ == "__main__":
    main()
