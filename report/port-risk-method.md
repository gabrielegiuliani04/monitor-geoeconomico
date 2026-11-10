# Port Risk Index: method

Version 1 · 10 November 2026 · script [`raccolta/porti/rischio_porti.py`](../raccolta/porti/rischio_porti.py) · output [`docs/data/port-risk.json`](../docs/data/port-risk.json) · history [`raccolta/porti/history.json`](../raccolta/porti/history.json)

## 1. In one line

**Port risk = probability of disruption (1–5) × impact on European and Italian supply chains (1–5)**, scored each day with fixed rules on public data that the observatory already collects. It uses the same probability × impact matrix as the chokepoint dashboard ([`metodo-rischio.md`](metodo-rischio.md)), and it plugs into it: a port's exposure to chokepoints is read from that dashboard's scores.

Every number in the output carries its value, unit, thresholds, status (green / amber / red, or n/a), source, file and date, so a reader can redo the sum by hand.

## 2. What is scored (39 ports)

| Group | Ports | Data |
|---|---|---|
| North Sea and Baltic (30) | Rotterdam, Antwerp-Bruges, Hamburg, Bremen/Bremerhaven, Wilhelmshaven, Amsterdam, Eemshaven, Esbjerg, Aarhus, Copenhagen-Malmö, Gothenburg, Gdańsk, Gdynia, Świnoujście, Klaipėda, Riga, Ventspils, Tallinn, Helsinki, HaminaKotka, Primorsk, Ust-Luga, St Petersburg, Kaliningrad, Sköldvik, Vysotsk, Paldiski, Inkoo, Rostock, Brunsbüttel | `porti-nord.json` (PortWatch daily calls since 1 January 2025) |
| Italy (9) | Genoa, Trieste, Gioia Tauro, La Spezia, Livorno, Venice (Lido entrance), Venice (Malamocco entrance), Ravenna, Augusta | `portwatch.json` (PortWatch daily calls since 1 January 2023) |

Venice appears twice because PortWatch counts its two lagoon entrances as separate ports; they are kept apart so that each score matches one PortWatch series.

The viewpoint is **European and Italian**: impact measures how much an outage would hurt EU and Italian supply chains, not the port's own country.

## 3. Seven questions

**Probability** (that the port is, or becomes, disrupted over the next weeks)

| Question | Weight | Indicators (all from the repository) | Green | Amber | Red |
|---|---|---|---|---|---|
| **Is traffic falling?** | 30% | (a) PortWatch port calls, 7-day mean vs the same 7 days 52 weeks earlier; (b) the same for the port's main vessel type (tanker, container, dry bulk, general cargo, ro-ro); (c) **congestion/disruption proxy**: 7-day calls vs the previous 28 days | > −20% | −20% / −30% | ≤ −30% |
| | | *Small ports* (under 3 calls/day on average over 12 months): (a) uses 28-day windows; (c) uses wider bands | > −30% (c: > −35%) | −30 / −50% (c: −35 / −50%) | ≤ −50% |
| **Are there security events nearby?** | 30% | Events within 50 km in the last 90 days (`baltico-sicurezza`, `ibrido`, `eventi`, `cavi-incidenti`); the same over 12 months (North Sea and Baltic only); GNSS interference within 50 km (GPSJam, last 7 days); likely shadow-fleet or sanctioned tankers within 50 km (AIS snapshot, Baltic only); news headlines naming the port with disruption keywords (strike, closure, congestion, attack, drone, fire…) in the last 72 h | 0 | 90 days: 1 event · 12 months: 1–2 · GNSS: 2–10% of aircraft · ships: 1–4 · news: 1–2 | 90 days: ≥ 2 or any attack, sabotage or cable damage · 12 months: ≥ 3 · GNSS: > 10% · ships: ≥ 5 · news: ≥ 3 |
| **Do its trades depend on a disrupted chokepoint?** | 25% | Chokepoint scores (1–25) from `rischio.json` × dependency (1 = primary, 0.5 = secondary) | primary chokepoints low, secondary below high | a primary chokepoint medium (6–12) or a secondary one high/critical (≥ 12) | a primary chokepoint high or critical (≥ 12) |
| **Do war-risk underwriters list it?** | 15% | Inside a Joint War Committee listed area (`assicurazioni.json`, circular JWLA-035 of 16 September 2026): country listing or point inside a listed-waters polygon | not listed | — | listed |

**Impact** (how much an outage would hurt Europe and Italy)

| Question | Weight | Indicators | Green | Amber | Red |
|---|---|---|---|---|---|
| **How strategic is it?** | 45% | Count of five functions, each from a rule on repository data: **LNG import terminal** (operating, within 20 km, Global Energy Monitor via `terminali-gnl.json`; a terminal of ≥ 5 Mt/yr, about 6.8 bcm/yr, counts twice as a national-scale gas entry point); **oil and products hub** (≥ 3 tanker calls/day or ≥ 50% tankers, or a crude terminal named in `porti-nord.json`); **container gateway** (≥ 2 container calls/day); **offshore wind base port** (operating port in `eolico-filiera.json`, within 15 km); **military or dual use** (operating base within 15 km in `basi-mondo.json`/`italia.json`, or naval base / military logistics named in `porti-nord.json`) | 0–1 | 2 | ≥ 3 |
| **How much cargo does it handle?** | 30% | PortWatch estimated cargo (imports + exports), 30-day mean | < 50 kt/day | 50–200 kt/day | ≥ 200 kt/day |
| **How expensive is energy already?** | 25% | VLSFO bunker price at the nearest hub in the same sea basin with a public price (Ship & Bunker, `bunker-emissioni.json`) vs a year ago; TTF gas vs a year ago (`prezzi.json`); for LNG ports only, national gas storage vs the 5-year average (GIE AGSI+, `scorte.json`) | prices < +10%; storage ≥ −5% | +10 / +40%; −5 / −15% | > +40%; < −15% |

**Chokepoint dependencies are rules, not measured shares** (per-port cargo shares by chokepoint are not in the repository):

- *Baltic ports* (east of the Danish straits): Danish straits and the Baltic corridor are **primary** — geography: every ocean-going call passes the Øresund, the Great Belt or the Kiel Canal.
- *Genoa, Trieste, Gioia Tauro, La Spezia*: Red Sea / Asia–Europe container route **primary** (named in `stretti-dettaglio.json` as the first European landfall of the Suez route). Other Italian ports: primary if they are container gateways, otherwise secondary. North European container gateways: **secondary** (the Cape route is a working alternative for them).
- *LNG ports*: Qatar LNG **primary** in Italy (32.6% of Italian LNG from the Gulf, UN Comtrade, as used in `rischio.json`), **secondary** elsewhere (Dutch and German LNG was 77% and 89% US in Q1 2026, IEEFA via `esposizione-nord.json`).
- *Oil hubs outside Russia*: Strait of Hormuz **secondary**.

## 4. Why these thresholds

Measured on the PortWatch series in the repository (weekly snapshots, every Sunday; North Sea/Baltic from January 2026 against 2025, Italy from January 2024 against the year before). The script recomputes these shares every day in `port-risk.json → calibration`; values on 10 November 2026:

| Indicator | Weeks | Share of weeks amber or worse | Share red |
|---|---|---|---|
| Calls vs last year, ports ≥ 3 calls/day (−20 / −30%) | 1,978 | 15.3% | 4.9% |
| Calls vs last year, small ports, 28 days (−30 / −50%) | 597 | 9.9% | 4.0% |
| 7 days vs previous 28, ports ≥ 3 calls/day (−20 / −30%) | 3,332 | 6.6% | 1.9% |
| 7 days vs previous 28, small ports (−35 / −50%) | 1,162 | 9.8% | 4.5% |

A −10% amber (the chokepoint dashboard's threshold) would fire in about 30% of weeks for ports with ≥ 3 calls/day and about 44% for small ports: at port level daily calls are much noisier than at a chokepoint, so the bands are wider. The chosen bands make amber a 1-in-7 to 1-in-10 event and red a 1-in-20 to 1-in-50 event. In the same history, Primorsk's 7-day calls were more than 30% below the year before in 74% of weeks and Ust-Luga's in 26%: red catches real disruption (Ukrainian drone strikes on the Russian Baltic oil ports in March and July 2026, `baltico-sicurezza.json`), not just noise.

The size bands split the 39 ports into 5 red (≥ 200 kt/day: Rotterdam, Antwerp-Bruges, Hamburg, Gdańsk, Ust-Luga), 10 amber and 24 green. Price bands are those of the chokepoint dashboard ("how much does it cost already": +10/+40% on a year). Event, GNSS, shadow-fleet and news thresholds are **assessments** to be recalibrated when the history is longer.

## 5. How they combine

1. Each indicator scores **1 (green), 3 (amber), 5 (red)**. Indicators marked `scored: false` are shown but not counted (e.g. a vessel type with fewer than 3 calls/day a year earlier).
2. Inside a question: mean; across questions: weighted mean with the weights above.
3. Missing data (n/a): the question drops out and the weights are **renormalised**; `coverage` says how much of the weights is covered (below 0.7 the score is fragile). Without traffic and security data there is no score.
4. **Disruption-in-progress rule:** if 7-day calls are ≤ −50% on last year (ports with ≥ 3 calls/day), or an attack or sabotage on the port or its terminals is recorded within 20 km in the last 7 days, probability = 5.
5. **Viewpoint rule:** for Russian ports impact is capped at 3. EU trade with them is largely sanctioned, so an outage reaches Europe mainly through prices and through the shadow fleet in the Gulf of Finland, not through lost supply.
6. **Score = P × I** (1–25). Levels: **low** < 6 · **medium** 6–11.9 · **high** 12–19.9 · **critical** ≥ 20 (both axes at least 4).
7. **Trend:** difference with the saved day closest to 7 days ago (`raccolta/porti/history.json`); ±1 point = rising / falling. On the first day the 7-day-ago score is **reconstructed** by dropping the last 7 days from every PortWatch series, shifting the event windows and reading the chokepoint scores saved 7 days earlier (`raccolta/rischio/storico.json`); snapshot indicators (GNSS, AIS, news, vessel-type variation) are kept unchanged.
8. The **"why"** text and the **"watch"** list are generated from rules: they quote the indicators that push hardest and the threshold that would change the colour, not opinions.

## 6. What the score does NOT say

- **It is not a statistical probability.** "5" means "disruption in progress or every signal on alert", not "100%".
- **It does not measure congestion directly.** No free, machine-readable vessel-waiting-time source was found: MarineTraffic and Linerlytica port-congestion data are commercial products and were not used; Kuehne+Nagel publishes weekly text updates ("Port operational updates from around the world") with some waiting times, but not as a dataset, and the site could not be reached from the collection environment. The 7-day vs 28-day drop in calls is a **proxy**: it looks the same whether the cause is congestion, a strike, a storm or weaker demand.
- **AIS blind spots.** PortWatch counts only ships with AIS on; ro-ro, ferries and transhipment are under-estimated in the cargo figure (Helsinki and Gioia Tauro look smaller than they are); Russian ports are under-counted because of shadow-fleet AIS gaps; data arrive about a week late.
- **Event files cover different windows.** The Baltic security file goes back to 2022; the general event and hybrid files only start in September–October 2026. Italian ports have no 12-month security archive and no GNSS or AIS layer, so their security question rests on fewer indicators. A low count can mean little collection. Event titles are quoted as recorded in the source files (some in Italian).
- **Route dependencies and strategic roles are rules**, not measured trade shares. They change rarely and weigh heavily.
- **Common-mode indicators.** TTF and bunker prices are high for every port: they lift the level, they do not rank ports. Chokepoint scores are shared by many ports; ports in the same cluster (Ust-Luga, Primorsk, St Petersburg) are not independent. Do not add scores up.
- **It does not say when or how much in euros**, and it is not an assessment of the port's management, finances or physical resilience.

## 7. Sources

IMF PortWatch (port calls, vessel mix, cargo estimates); observatory chokepoint dashboard (`rischio.json`, itself from PortWatch, ENTSOG, GIE, GPR, prices and events); Joint War Committee listed areas (LMA/IUA); Global Energy Monitor (LNG terminals, CC BY 4.0); curated Baltic security, hybrid, event and cable files (agencies, authorities, OSINT); GPSJam (ADS-B Exchange); Digitraffic and aisstream.io crossed with sanctions lists; Ship & Bunker (bunker prices, public pages); Yahoo Finance (TTF); GIE AGSI+ (gas storage); WindEurope and port authorities via `eolico-filiera.json`; Wikidata/Wikipedia via `basi-mondo.json` and `italia.json`; RSS feeds via `notizie-testate.json`. Reference practice: ISO 31000 probability × impact matrix, early-warning indicators for supply chains.
