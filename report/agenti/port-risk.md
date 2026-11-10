# Port Risk Index — agent report

10 November 2026 · script `raccolta/porti/rischio_porti.py` (standard library, no network) · output `docs/data/port-risk.json` (39 ports, 0 errors) · history `raccolta/porti/history.json` · method [`report/port-risk-method.md`](../port-risk-method.md)

Score = probability (1–5) × impact on European/Italian supply chains (1–5). Inputs are the observatory's own files as updated on 9 November 2026. PortWatch calls run to **30 October 2026** (about a week's lag), chokepoint scores are from 9 November, the JWC circular from 16 September, bunker prices from 6 November and the TTF price from 9 November. Trend compares with a reconstructed score for 3 November.

## 1. Today's ranking

| # | Port | Country | P | I | Score | Level | Trend (7 d ago) |
|---|---|---|---|---|---|---|---|
| 1 | Ust-Luga | RU | 3.1 | 3.0 | 9.3 | medium | stable (8.7) |
| 2 | St Petersburg (Big Port, with Bronka) | RU | 3.1 | 3.0 | 9.3 | medium | rising (7.8) |
| 3 | Primorsk | RU | 3.3 | 2.6 | 8.6 | medium | stable (8.6) |
| 4 | Rotterdam | NL | 1.5 | 5.0 | 7.5 | medium | stable (7.5) |
| 5 | Antwerp-Bruges | BE | 1.5 | 5.0 | 7.5 | medium | stable (8.0) |
| 6 | Klaipėda | LT | 1.7 | 4.4 | 7.5 | medium | stable (7.5) |
| 7 | La Spezia | IT | 2.0 | 3.6 | 7.2 | medium | stable (7.2) |
| 8 | Gdańsk | PL | 1.7 | 4.1 | 7.0 | medium | stable (7.0) |
| 9 | Wilhelmshaven | DE | 1.5 | 4.4 | 6.6 | medium | falling (7.9) |
| 10 | Hamburg | DE | 1.5 | 4.1 | 6.1 | medium | stable (6.1) |
| 11 | Świnoujście | PL | 1.6 | 3.8 | 6.1 | medium | stable (6.1) |
| 12 | Eemshaven | NL | 1.5 | 3.8 | 5.7 | low | stable (5.7) |
| 13 | Livorno | IT | 2.0 | 2.7 | 5.4 | low | stable (5.4) |
| 14 | Bremen / Bremerhaven | DE | 1.5 | 3.5 | 5.2 | low | stable (6.0) |
| 15 | Genoa | IT | 2.0 | 2.6 | 5.2 | low | stable (5.7) |
| 16 | Trieste | IT | 2.0 | 2.6 | 5.2 | low | stable (5.2) |
| 17 | Gioia Tauro | IT | 2.0 | 2.6 | 5.2 | low | stable (5.2) |
| 18 | Augusta | IT | 1.5 | 3.5 | 5.2 | low | stable (5.2) |
| 19 | Gdynia | PL | 1.7 | 2.9 | 4.9 | low | stable (4.9) |
| 20 | Venice (Lido entrance) | IT | 2.4 | 2.0 | 4.8 | low | rising (3.6) |
| 21 | Ravenna | IT | 2.6 | 1.8 | 4.7 | low | rising (3.6) |
| 22 | Tallinn | EE | 2.3 | 2.0 | 4.6 | low | stable (4.6) |
| 23 | Kaliningrad and Baltiysk | RU | 2.3 | 2.0 | 4.6 | low | stable (4.6) |
| 24 | Vysotsk | RU | 2.2 | 2.0 | 4.4 | low | stable (4.4) |
| 25 | Rostock | DE | 1.5 | 2.9 | 4.3 | low | stable (4.3) |
| 26 | Venice (Malamocco entrance) | IT | 2.1 | 2.0 | 4.2 | low | rising (3.0) |
| 27 | Riga | LV | 2.0 | 2.0 | 4.0 | low | stable (3.4) |
| 28 | Helsinki | FI | 2.0 | 2.0 | 4.0 | low | stable (4.0) |
| 29 | Sköldvik (Porvoo) | FI | 2.0 | 2.0 | 4.0 | low | stable (4.0) |
| 30 | Amsterdam | NL | 1.5 | 2.6 | 3.9 | low | stable (3.9) |
| 31 | Gothenburg | SE | 1.5 | 2.6 | 3.9 | low | stable (3.9) |
| 32 | HaminaKotka | FI | 1.9 | 2.0 | 3.8 | low | stable (3.8) |
| 33 | Copenhagen-Malmö (CMP) | DK | 1.8 | 2.0 | 3.6 | low | stable (4.2) |
| 34 | Paldiski | EE | 1.7 | 2.0 | 3.4 | low | stable (3.4) |
| 35 | Inkoo | FI | 1.7 | 2.0 | 3.4 | low | stable (3.4) |
| 36 | Brunsbüttel | DE | 1.7 | 2.0 | 3.4 | low | stable (3.8) |
| 37 | Esbjerg | DK | 1.6 | 2.0 | 3.2 | low | rising (2.0) |
| 38 | Ventspils | LV | 1.6 | 2.0 | 3.2 | low | stable (3.2) |
| 39 | Aarhus | DK | 1.0 | 2.0 | 2.0 | low | stable (2.0) |

**Reading.** No port is high or critical. The risk sits in two different places: Russian Gulf of Finland ports have the **highest probability** (P 3.1–3.3), while Rotterdam and Antwerp-Bruges have the **highest impact** (I 5.0) but quiet signals. Italian ports cluster at 5.2. All of them depend on the Red Sea container route, which the chokepoint dashboard scores 18.0/25 (high), so a Red Sea relapse would move all of them together. Energy costs are red for every port (TTF 82.33 EUR/MWh, +163.9% on a year, Yahoo Finance, 9 November 2026), so they lift the level but do not rank ports.

## 2. Five ports to watch, and why

1. **Rotterdam (7.5, medium): highest impact, one trigger from high.** It has all five strategic functions bar military: Gate LNG at 11.8 Mt/yr (Global Energy Monitor), 42.7 tanker calls/day, container gateway and an offshore wind base. It handles 917 kt/day of estimated cargo (PortWatch, 30-day mean to 30 October 2026). Probability is low (1.5): calls are −10.8% on a year (74.1 vs 83.1/day), inside the noise band. Its only amber is dependence on the Red Sea, Hormuz and Qatar LNG. Dutch gas storage is 63.5% full, −22.9% on the 5-year average (GIE AGSI+, 8 November). *Watch:* an LNG supply shock hits through Gate; 7-day calls under 41.5/day trigger the disruption rule.
2. **Ust-Luga and the Gulf of Finland cluster (9.3, top of the ranking).** Calls are −28.8% on a year (6.0 vs 8.4/day), just short of red at −30%. The AIS snapshot of 9 November shows 22 likely shadow-fleet or sanctioned tankers within 50 km (Digitraffic), 38.9% of aircraft nearby report GNSS interference (GPSJam, week to 8 November), and Russia is a JWC listed area (JWLA-035). Primorsk (8.6): 28-day calls −52.9% on a year, with two drone strikes in 2026 (23 March and 21 July, `baltico-sicurezza.json`). *Why it matters to the EU:* shadow-fleet anchors near Finnish and Estonian cables, oil-spill risk, and price spillover. Impact is capped at 3 by rule.
3. **Klaipėda (7.5): the Baltic energy-security port.** It has an LNG FSRU (2.9 Mt/yr), a container gateway (2.9 container calls/day) and a naval base (`porti-nord.json`). 60% of aircraft in the nearest GNSS cell report interference (GPSJam). It depends on the Danish straits and the Baltic corridor (chokepoint scores 8.3 and 9.0/25). Calls are −16.9% on a year: still green, but the trigger is close. *Watch:* cable or pipeline incidents in the Baltic (12-month count within 50 km is 0 today).
4. **La Spezia (7.2): Italy's most exposed port.** It is the only Italian port with three strategic functions: Panigaglia LNG (2.6 Mt/yr), container gateway (92% of calls are container ships) and the La Spezia naval base (`italia.json`). Both of its primary chokepoints are high or critical: Red Sea container route 18.0/25 and Qatar LNG 24.0/25 (`rischio.json`, 9 November). Its traffic is growing (+26.0% on a year, 28-day mean). The risk is structural, not visible in the flows. *Watch:* Red Sea attacks resuming or Gulf LNG cargoes being diverted.
5. **Ravenna and Venice (4.7 and 4.8, rising): falling traffic in the Adriatic.** Ravenna's calls are −40.0% on a year (5.6 vs 9.3/day) and general cargo is −45.8%. Venice-Lido is −38.5% (4.6 vs 7.4/day) and Malamocco −51.5% against the previous 28 days. Both rose by more than one point on 3 November. Ravenna also hosts the Ravenna FSRU (4.7 Mt/yr with the onshore terminal) and depends on Qatar LNG (24.0/25). *Caveat:* the cause is not in the data (demand, weather or a closure would all look the same). This is the case where a congestion or port-status source would add most.

Honourable mention for the Denmark target: **Esbjerg** (3.2, rising from 2.0). Calls are 2.0/day against 3.5 in the previous 28 days (−42.9%, red on the disruption proxy). It is Europe's main offshore wind installation port (`eolico-filiera.json`), but its cargo volume is small, so impact stays low.

## 3. The 2-minute interview answer

> "I built a daily risk index for 39 European ports — the 30 main North Sea and Baltic ports and 9 Italian ones — using only public data: IMF PortWatch ship calls from AIS, war-risk insurance listings, security incidents, GNSS jamming, LNG terminal data and energy prices.
>
> It's the classic probability-times-impact matrix. Probability asks four questions: is traffic falling against last year, are there security events nearby, does the port depend on a chokepoint that's currently disrupted, and do war-risk underwriters list the area? Impact asks how strategic the port is, so LNG, oil, containers, offshore wind and military roles, how much cargo it handles, and how expensive energy already is. Each indicator is green, amber or red against a threshold I calibrated on the history. For example, a 20% drop in calls happens in about one week in seven at a big port, so that's amber, not an alarm. Every number carries its source and date.
>
> Today it says two things. Rotterdam and Antwerp have the highest impact but quiet signals: calls are down 11 to 12% on last year, within normal noise. The highest probability is in the Russian Gulf of Finland ports, with 22 shadow-fleet tankers near Ust-Luga, heavy GNSS jamming and a war-risk listing. For Italy, La Spezia is most exposed because both its container trade and its LNG depend on the Red Sea and the Gulf.
>
> What I'd stress is what it doesn't do. It's not a forecast, and it can't see congestion directly, only a drop in calls, which could also be a strike or weather. That's exactly where a logistics team's own data, like berth waiting times or terminal slots, would make it sharper."

## 4. Sources tried

| Source | Status | Used for |
|---|---|---|
| IMF PortWatch via `porti-nord.json`, `portwatch.json` | works (public, cite "IMF PortWatch") | calls, vessel mix, cargo estimate |
| Observatory chokepoint dashboard `rischio.json` + `raccolta/rischio/storico.json` | works | chokepoint exposure and its 7-day-ago value |
| JWC listed areas via `assicurazioni.json` | works (public circulars) | insurance |
| `baltico-sicurezza.json`, `ibrido.json`, `eventi.json`, `cavi-incidenti.json` | works; general files only start in Sept–Oct 2026 | security events |
| GPSJam via `baltico-sicurezza.json` | works; no declared licence (personal use with citation) | GNSS interference |
| Digitraffic/aisstream via `baltico-sicurezza.json` | works; Baltic only | shadow fleet |
| Global Energy Monitor via `terminali-gnl.json` | works (CC BY 4.0) | LNG role |
| Ship & Bunker via `bunker-emissioni.json` | public for 7 hubs; Genoa, Hamburg, Gdańsk and Skaw are subscriber-only | bunker cost |
| `prezzi.json` (TTF), `scorte.json` (AGSI+) | works | energy cost, gas buffer |
| Kuehne+Nagel "Port operational updates" (weekly, public text) | found by search; host not reachable from the collection environment; text, not a dataset | **not used** |
| MarineTraffic, Linerlytica port congestion | commercial | **not used** |

## 5. For the coordinator: showing it on the map

Put one circle per port at `lat`/`lon`, coloured by `level`, sized by `impact`, with a small arrow for `trend`. The popup shows `why`, the indicator table (`indicators[]` with status dot, text, source and date) and `watch`. Add a "Ports" tab with the ranking, sortable by P, I and score. Link chokepoint exposure to the chokepoint layer through `indicators[].dependencies[].chokepoint`, which uses the `rischio.json` unit ids. `source_id` matches the ids in `porti-nord.json` and `portwatch.json`.

## 6. Limits

The congestion proxy is not waiting-time data. AIS gaps affect Russian and ro-ro/ferry ports. Italian ports have fewer security indicators (no 12-month archive, no GNSS or AIS layer). Route dependencies and strategic roles are explicit rules, not measured cargo shares. The first trend is against a reconstructed day; real history starts today. See section 6 of the method.
