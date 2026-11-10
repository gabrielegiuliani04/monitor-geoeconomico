# Shipping transit times to European ports: today vs before the crisis

Agent: SHIPPING TRANSIT TIMES. Data as of 10 November 2026 (passage status 9 Nov, bunker prices 6 Nov, EUA auction 9 Nov, freight indices 5–6 Nov, PortWatch 1 Nov).
Files: `raccolta/rotte/tempi.py` (standard library only, no network, about 3 s), output `docs/data/transit-times.json` (99 routes, 260 KB).

## Headline

**Containers from Asia: a Suez-routed service takes about as long as in 2023. A Cape-routed service still takes 10.5 days more to North Europe and 16–20 days more to the Mediterranean.** The schedule mix today (63% of Far East–Europe capacity back on Red Sea services) gives a capacity-weighted average of about **+4 days to North Europe and +6–7 days to Italy and Greece**.
**Gulf energy: Hormuz is de facto closed.** Qatari LNG has no bypass. Saudi crude that is piped to Yanbu reaches Europe **8.6 days sooner** than it did from Ras Tanura, but loading at Yanbu costs 3% of hull value in war risk.
**The biggest cost increase on every lane is the price of fuel, not the extra distance.** VLSFO in Singapore is 854 $/t, against 521.5 $/t on 27 Feb 2026 (+64%).

### Headline table (sea time only, same speed in both scenarios)

Base = 2023 routing via Suez, Bab el-Mandeb and Hormuz. "Weighted" = Suez and Cape days, weighted by the 63/37 container capacity split. "Extra cost" = extra fuel at today's price + extra EU ETS + (war risk today − war risk pre-crisis). "Price effect" = fuel for the base voyage × (today's VLSFO − 27 Feb 2026 VLSFO). The per-unit column includes both.

| Lane | Cargo | Status today | nm base / today | Days base | Days today | Weighted | Cape-routed days (Δ) | Extra cost/voyage | Fuel price effect | Per unit | Freight today |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Shanghai → Rotterdam | container | Suez open | 10,674 / 10,674 | 29.6 | 29.6 | 33.5 | 40.1 (+10.5) | 0.26 M$ | 1.48 M$ | 273 $/FEU | WCI 3,615 $/FEU (5 Nov) |
| Shanghai → Hamburg | container | Suez open | 10,953 | 30.4 | 30.4 | 34.3 | 40.9 (+10.5) | 0.26 M$ | 1.52 M$ | 279 $/FEU | FBX11 3,422 $/FEU |
| Shanghai → Gdańsk | container | Suez open | 11,555 | 32.1 | 32.1 | 36.0 | 42.6 (+10.5) | 0.26 M$ | 1.60 M$ | 292 $/FEU | FBX11 3,422 $/FEU |
| Shanghai → Genoa | container | Suez open | 8,797 | 24.4 | 24.4 | 30.2 | 40.1 (+15.7) | 0.26 M$ | 1.22 M$ | 232 $/FEU | WCI 4,166 $/FEU (5 Nov) |
| Shanghai → Trieste | container | Suez open | 8,686 | 24.1 | 24.1 | 31.0 | 42.8 (+18.7) | 0.26 M$ | 1.20 M$ | 230 $/FEU | FBX13 4,324 $/FEU |
| Shanghai → Piraeus | container | Suez open | 8,004 | 22.2 | 22.2 | 29.5 | 41.8 (+19.6) | 0.26 M$ | 1.11 M$ | 215 $/FEU | FBX13 4,324 $/FEU |
| Singapore → Rotterdam | container | Suez open | 8,482 | 23.6 | 23.6 | 27.4 | 34.0 (+10.4) | 0.26 M$ | 1.18 M$ | 226 $/FEU | FBX11 3,422 $/FEU |
| Busan → Antwerp | container | Suez open | 11,049 | 30.7 | 30.7 | 34.6 | 41.2 (+10.5) | 0.26 M$ | 1.53 M$ | 281 $/FEU | FBX11 3,422 $/FEU |
| Nhava Sheva → Rotterdam | container | Suez open | 6,501 | 18.1 | 18.1 | 23.4 | 32.5 (+14.4) | 0.26 M$ | 0.94 M$ | 188 $/FEU | n/a |
| Jebel Ali → Rotterdam | container | re-routed via Khor Fakkan (land bridge) | 6,262 / 6,188 | 17.4 | 17.2 | 22.3 | 31.1 (+13.7) | −0.07 M$ (sea leg only) | 0.90 M$ | 131 $/FEU | n/a |
| Ras Laffan → Rotterdam | LNG | **blocked** (Hormuz) | 6,473 | 15.9 | 15.9 if it gets out | – | 28.2 (+12.3) | 15.95 M$ (war risk) | 0.60 M$ | 4.6 $/MMBtu | n/a |
| Ras Laffan → Klaipėda | LNG | **blocked** (Hormuz) | 7,411 | 18.2 | 18.2 if it gets out | – | 30.5 (+12.3) | 15.95 M$ | 0.69 M$ | 4.6 $/MMBtu | n/a |
| Ras Tanura → Rotterdam | crude | re-routed via East-West pipeline to Yanbu | 6,554 / 3,964 | 21.8 | 13.2 (−8.6) | – | 39.3 from Yanbu via Bab el-Mandeb | 2.33 M$ | 0.34 M$ | 2.7 $/bbl | n/a |
| Ras Tanura → Gdańsk | crude | re-routed via Yanbu | 7,435 / 4,845 | 24.8 | 16.1 (−8.7) | – | 42.2 | 2.33 M$ | 0.39 M$ | 2.7 $/bbl | n/a |
| Yanbu → Genoa | crude | Suez open; Yanbu in listed area | 2,087 | 7.0 | 7.0 | – | 39.2 (+32.2) | 3.00 M$ (war risk) | 0.11 M$ | 3.1 $/bbl | n/a |
| Sabine Pass → Klaipėda | LNG | unaffected | 6,161 | 15.1 | 15.1 | – | same | 0 | 0.42 M$ | 0.12 $/MMBtu | n/a |
| Sabine Pass → Rotterdam | LNG | unaffected | 5,223 | 12.8 | 12.8 | – | same | 0 | 0.35 M$ | 0.10 $/MMBtu | n/a |
| New York → Hamburg | container | unaffected | 3,633 | 10.1 | 10.1 | – | same | 0 | 0.38 M$ | 59 $/FEU | n/a |
| Santos → Rotterdam | container | unaffected | 5,430 | 15.1 | 15.1 | – | same | 0 | 0.57 M$ | 89 $/FEU | n/a |

All 99 origin–destination pairs (11 origins × 9 destinations) are in the JSON. For the Cape alternative of the Asian container lanes, the extra cost per voyage is about **1.46–1.48 M$ to North Europe** (1,560–1,575 t of extra VLSFO plus about 0.24 M$ of ETS, minus the Red Sea war-risk premium that is avoided) and **2.3–2.9 M$ to Genoa, Trieste and Piraeus**. The Suez toll that is saved is not deducted.

## Method

1. **Graph.** The graph has 1,775 vertices from the 239 Benden lanes in `docs/data/rotte.json`. Vertices shared between lanes are junctions. Each dangling lane end is snapped to the nearest point of another lane within 250 km, splitting that lane there.
   - **Added connectors.** The CIA-derived map has none of these lanes, so I added 9 open-ocean connectors by hand and declared them in the JSON `method`:
     - Florida Strait–Gibraltar
     - Cape Verde–Gibraltar
     - Alboran–Ligurian Sea
     - Port Said–south of Crete–Ionian
     - Messina–Tyrrhenian–Genoa
     - Sicily Channel–Messina
     - Kasos–Piraeus
     - Otranto–Adriatic–Trieste
     - India–Gulf of Aden
   - **Ports.** Ports are attached through hand-set approach waypoints (Elbe, Scheldt, Saronic Gulf, Gdańsk Bay, east of Bornholm). A route can never pass through another port's connector.
2. **Routing.** Dijkstra on great-circle edge lengths, in three scenarios:
   - all passages open (the 2023 base);
   - no Red Sea: edges within 120 km of Suez or Bab el-Mandeb are removed, which gives the Cape route;
   - today's state, read from `stretti-dettaglio.json`. Hormuz "chiuso di fatto" means Gulf origins move to their bypass port or are flagged as blocked. If Suez or Bab el-Mandeb ever reads "chiuso", every route switches to the Cape automatically.
3. **Passages and listed areas.** Passages on a route are detected with gate circles. Crossings of JWC listed areas are found with the polygons in `assicurazioni.json`.
4. **Speeds.** Days = nm / (kn × 24). The same speed is used today and in the base case, so the difference comes from distance only. Sea time only: no canal queue, no port time.

   | Vessel | Speed used | Source |
   |---|---|---|
   | Container ship | 15 kn (range 14–16) | Alphaliner, mid-April 2026: fleet average 15.22 kn, Far East–Europe faster because of Cape routings; BIMCO: 13.8 kn in Q1 2023; UNCTAD RMT 2024: going from 14 to 16 kn costs +31% fuel per mile |
   | Crude tanker | 12.5 kn (range 12–13) | S&P Global/CAS: VLCC laden 12.4 kn in week 38 and 12.1 kn in week 43 of 2025; Clarksons: record-low tanker speeds |
   | LNG carrier | 17 kn (range 16–18) | S&P Global: Qatar–NW Europe takes 16 days via Suez and 27 days via the Cape; carriers are designed for 19–19.5 kn but slow-steam in an oversupplied market (Vortexa) |

5. **Fuel and costs.**
   - **Daily consumption (my own hypotheses, declared in the JSON):**
     - container ship of 15,000 TEU: 150 t/day;
     - Suezmax tanker (1 million bbl; a laden VLCC cannot transit Suez): 45 t/day;
     - LNG carrier of 174,000 m³: 110 t/day, VLSFO-equivalent.
   - **Fuel price.** Ship & Bunker VLSFO at the origin's bunkering hub: Singapore for East Asia, Fujairah for the Gulf and India, Rotterdam for the Americas.
   - **ETS.** 3.1631 tCO2e per tonne of fuel × 50% (extra-EU voyage) × 100% (2026 phase-in) × EUA 86.91 € (EEX auction, 9 Nov) × 1.1222 USD/EUR.
   - **War risk.** Midpoint of the latest public quote, as % of hull value per transit:
     - Gulf/Hormuz 6–10% (FT via Insurance Business, 7 Oct 2026);
     - southern Red Sea 0.2–0.3% (Reuters, 24 Sep 2026);
     - Saudi-linked ships at Yanbu 3% (Reuters, 24 Sep 2026).
   - **Pre-crisis war risk:**
     - Red Sea 0.075% (Nov 2023);
     - Gulf 0.2% (27 Feb 2026);
     - Yanbu 0%: it was outside the listed area until JWLA-034 moved the line from 18°N to 25.5°N.
   - **Hull values:** container ship 150 M$, tanker 100 M$, LNG carrier 200 M$ (from `assicurazioni.json`).
6. **Freight.** Drewry WCI Shanghai–Rotterdam and Shanghai–Genoa, Freightos FBX11 and FBX13, and the CCFI Europe and Mediterranean sub-indices, taken from `noli.json`. There is no tanker or LNG freight index in the repository.

## Validation (error = computed − published)

| Pair | Published | Computed | Error |
|---|---|---|---|
| Shanghai–Rotterdam via Suez (Rodrigue, *Port Economics, Management and Policy*) | 10,600 nm | 10,674 nm | +0.7% |
| Shanghai–Rotterdam via Cape (same) | 13,800 nm | 14,440 nm | +4.6% |
| Singapore–Rotterdam via Suez (Rodrigue, *Geography of Transport Systems*; other tables give 8,288) | 8,440 nm | 8,482 nm | +0.5% |
| Singapore–Rotterdam via Cape (same; other tables give 11,755) | 11,940 nm | 12,247 nm | +2.6% |
| Gulf–Rotterdam, extra distance of the Cape (Lloyd's List) | +4,900 nm | +5,017 nm | +2.4% |
| New York–Rotterdam (calculator sites, 3,200–3,450 nm, low reliability) | 3,350 nm | 3,354 nm | +0.1% |
| Qatar–NW Europe via Suez (S&P Global), days | 16 d | 15.9 d | −0.8% |
| Qatar–NW Europe via Cape (S&P Global), days | 27 d | 28.2 d | +4.3% |

The mean absolute error on distances is **1.8%** and the maximum is 4.6%.
- The Benden lanes overestimate the Cape route by 2.6–4.6%, so Cape penalties are about 0.5–1.5 days too high.
- The two LNG day checks are not independent, because the LNG speed was chosen with that S&P figure in mind.

## Sources tried

| Source | Result | Licence |
|---|---|---|
| Repository files: `rotte.json`, `stretti-dettaglio.json`, `portwatch.json`, `noli.json`, `bunker-emissioni.json`, `assicurazioni.json`, `porti-nord.json` | worked; the script reads them every day and needs no network | Benden lanes: declared CC BY 4.0, CC BY-SA and CC BY-NC 4.0 in three places, so treat as non-commercial with citation. Drewry, Freightos and SSE values are © and cited. IMF PortWatch: cite IMF PortWatch |
| porteconomicsmanagement.org and transportgeography.org | **not reachable** from this sandbox (host not in the network allowlist) | – |
| Web search | worked | – |

The published distances from the two unreachable sites were taken from search-result excerpts. They should be re-checked on the pages themselves before they are quoted in public.

## Current facts (with date and source)

1. **Hormuz, 1 Nov 2026:** IMF PortWatch counts 4.4 transits per day (7-day average) against 89 three years earlier (−95%). Lloyd's List Intelligence counts about 120 non-Iranian transits per week, many of them AIS-dark (25 Oct).
2. **Suez, 1 Nov 2026:** PortWatch counts 43 transits per day, +10% on a year earlier but −43% on late 2023. October 2026 was the busiest month since the Red Sea crisis began, with 1,490 ships.
3. **Container capacity, October 2026:** Alphaliner puts 63% of Far East–Europe capacity on Red Sea services. Linerlytica expects a full return by Q1 2027.
4. **Bab el-Mandeb, 1 Nov 2026:** 27.3 transits per day (−66% on 2023). UKMTO reports no attacks in the Red Sea since 24 August. The Houthis threaten Saudi-linked ships (`stretti-dettaglio.json`, 9 Nov).
5. **VLSFO, 6 Nov 2026:** Singapore 854 $/t (+64% since 27 Feb), Fujairah 865 $/t (+67%), Rotterdam 739.5 $/t (+51%), all Ship & Bunker.
6. **War risk:**
   - Gulf/Hormuz 6–10% of hull per voyage (7 Oct), against 0.15–0.25% before the war.
   - Yanbu 3% for Saudi-linked tankers (24 Sep).
   - Red Sea 0.2–0.3% (24 Sep).
7. **EUA, 9 Nov 2026:** 86.91 € at the EEX auction. ETS on 1,575 t of extra Cape fuel comes to about 0.24 M$ per voyage.
8. **Freight, 5–6 Nov 2026:** WCI Shanghai–Rotterdam 3,615 $/FEU and Shanghai–Genoa 4,166 $/FEU (Drewry). FBX11 China–North Europe 3,422 $/FEU (−4.8% week on week).

## Interview talking points

- **Asia–Europe containers.** The "Cape penalty" is about 10.5 days to Rotterdam, Hamburg or Gdańsk but 16–20 days to Genoa, Trieste or Piraeus. The Red Sea crisis hurt Mediterranean ports twice as much as northern ones, and the return to Suez helps them most. Today's average delay (+4 days north, +6–7 days Mediterranean) is a scheduling mix, not physics: it falls to zero when the last 37% of capacity comes back.
- **Distance versus fuel price.** A Suez-routed box ship from Shanghai burns the same fuel as in 2023. That fuel now costs 1.1–1.6 M$ more per voyage than on 27 Feb 2026, about 175–250 $/FEU, or 5–7% of today's WCI/FBX rate. Fuel price is now a bigger cost item than rerouting.
- **ETS.** The 2026 phase-in is 100%, so every extra Cape day carries a carbon bill: about 23,000 $ per day for a 15,000 TEU ship. Per box, the ETS cost of the detour is small (about 40 $/FEU); what matters more is that carriers pass it on as surcharges (Maersk EMS Far East–North Europe: 170 $/FEU in Q4 2026).
- **Hormuz.** Saudi Arabia's East-West pipeline turns a closure into a *shorter* voyage to Europe (Yanbu–Rotterdam takes 13.2 days, against 21.8 days from Ras Tanura). The limits are pipeline capacity (about 5–7 mb/d) and the 3% war-risk premium at Yanbu, about 3 M$ per Suezmax voyage or 3 $/bbl. Qatar has no bypass. For Europe's Baltic LNG terminals (Klaipėda, Świnoujście), US LNG from Sabine Pass at 15 days is now the default supply chain.
- **War risk.** A blocked Qatari cargo that did get through would pay about 16 M$ (8% of a 200 M$ hull), about 4.4 $/MMBtu extra, more than the ocean freight itself. That is why insurers, not navies, decide when a chokepoint "reopens".
- **Northern Europe and the Baltic.** Gdańsk and Klaipėda are about 880–940 nm (2–2.5 days) beyond Rotterdam on every long-haul route and pass the Danish straits as well. Hub-and-feeder via Rotterdam, Antwerp, Hamburg or Bremerhaven remains the logic; the crisis does not change the geography of the Baltic gateway.

## Links to other map layers

- **Passages:** `stretti-dettaglio.json`, `portwatch.json`.
- **Insurance:** `assicurazioni.json`, polygons and premiums.
- **Fuel and ETS:** `bunker-emissioni.json`.
- **Freight:** `noli.json`.
- **Ports:** `porti-nord.json`; Rotterdam, Antwerp and Gdańsk port calls give the demand side.
- **Pipelines:** Petroline Abqaiq–Yanbu and ADCOP in `condotte.json` explain the bypasses.

## How to show it on the map (proposal; `index.html` not modified)

- One line per route from `routes[].g`, coloured by `extra_days` (or by `cape.extra_days_vs_base` for Asian container lanes).
- Dashed lines for `status` "blocked" or "re-routed".
- A popup with days base/today/Cape, the cost breakdown and the freight index.
- An origin selector, defaulting to Shanghai, that shows all nine European destinations as a fan of lines.

## Limits

- **Days are sea time only:**
  - no Suez queue (1–2 days);
  - no tolls (about 0.5–1 M$ per transit, saved on the Cape route);
  - no charter hire;
  - no bunkering detours;
  - no port congestion.
- **Consumptions and hull values are declared hypotheses.** Results scale linearly with them.
- **War-risk quotes are press quotes, 1–2 months old.** The Gulf quote is for tankers and is applied to LNG carriers. No public quote exists for the Gulf of Oman (Khor Fakkan), which is counted as 0.
- **Jebel Ali via Khor Fakkan covers the sea leg only.** Trucking and terminal costs of the land bridge are not included.
- **The Benden lanes are coarse.** The Danish straits lane cuts across Zealand on the map (the distance is close to the Great Belt route). The Kiel Canal is missing, which matters for small feeders to the Baltic, not for mainliners.
- **The 63% Red Sea share** is a hand-curated fact. It is set in `CONFIG` and comes from the Suez entry in `stretti-dettaglio.json`. It must be updated by hand.

## For the coordinator

- Add `python3 raccolta/rotte/tempi.py` to `.github/workflows/aggiorna-dati.yml` after the `bunker` and `stretti` steps. I did not modify the workflow.
- The script only reads repository files and writes `docs/data/transit-times.json`.
