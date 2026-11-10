# Review: "Offshore Wind in Northern Europe: Targets, Bottlenecks and Ports" (November 2026)

**Reviewer:** independent review (fact-check and edit), done with an AI assistant · **Date:** 10 November 2026
**Text reviewed:** [`report/offshore-wind-2026-11.md`](../offshore-wind-2026-11.md) and [`docs/report/en/offshore-wind-2026-11.html`](../../docs/report/en/offshore-wind-2026-11.html), both built by [`report/build_offshore_wind.py`](../build_offshore_wind.py)
**Standard:** [`report/STANDARD.md`](../STANDARD.md)

## Summary

- Claims checked: **123** (table below; a row can group several figures from one source): **88** confirmed, **25** corrected, **10** not verifiable from here (rows 24, 52 and 81 are counted as confirmed but include one secondary-only detail each).
- Corrections were made at the source: text constants in `report/build_offshore_wind.py` and new curated items in `report/dati/offshore-wind-esterni.json` (`rvo_roadmap`, `turbine_trimestre`, `cadeler_h1`, `windeurope_filiera`, a rewritten `verifiche_web`). `docs/data/` was not touched. The report was rebuilt online on 10 November 2026, around 11:15 UTC: the ECB deposit-rate call timed out (504), so that series comes from the cache (unchanged at 2.50%). The euro AAA yield and copper changed with the new readings (3.27% on 9 November; 6.31 $/lb).
- The most serious problems were **out-of-date facts** and **one wrong date**:
  1. The turbine section used Q2 losses. Siemens Gamesa reported its first positive quarter since FY2022 in Q3 FY2026 (5 August 2026), and GE Vernova's wind segment earned +72 M$ EBITDA in Q3 2026 (28 October 2026). The table, the text and the watch list now show this.
  2. The IJmuiden Ver Gamma farms are due in **Q2 2032** in RVO's current roadmap, not Q2 2031. The 2031 date is the earlier plan, before the one-year platform slip.
  3. In the data file, supply-chain investment (15.4 bn €) and the jobs base year (2025) do not match the WindEurope PDF the file cites. The PDF says "at least €15bn", and 442,800 jobs is the 2024 figure.
- Two assessments rested on evidence that does not hold:
  - "Day rates are under pressure (Cadeler at 66%)": Cadeler's 66% is level with 67% a year earlier, and the company says its 2026 book is substantially filled.
  - "Gdańsk's risk is driven by GNSS": the score is 1.7 × 4.1, so it comes from impact (port size and energy role).

Method: data values were read directly from `docs/data/*.json` with Python. All arithmetic was recomputed. Sources were downloaded with curl and read in full on 10 November 2026: 26 pages and PDFs, including the WindEurope 2025 Statistics PDF (64 pages), GOV.UK AR6 and AR7 results, the RVO Gamma-B page and roadmap, the Dutch letter to Parliament of 16 March 2026, the Prysmian Q3 2026 release, NKT H1 2026, Cadeler H1 2026 (SEC), the GE Vernova Q3 2026 8-K, the Siemens Energy Q3 FY2026 release, Rystad, HVDC World, CERT Polska, offshoreWIND.biz (6 November) and Al-Monitor/Reuters (9 November). Renewables Now and reNEWS returned 403. Search results were used for those two and for the Danish August award.

## 1. Verification table

Outcomes: **ok** = matches; **corrected** = wrong, out of date or imprecise, fixed in the script or the external file; **n.v.** = not verifiable from here (secondary source only, or not found).

### Key points and section 2 (targets)

| # | Claim | Value in report | Verified value | Source | Outcome |
|---|---|---|---|---|---|
| 1 | Shortfall of seven countries vs targets | 60.4 GW "will fall short" | 60.38 GW = Σ(target − WindEurope 2030 forecast). The Dutch target is for 2032, so this mixes years | eolico-filiera.json, wind-calendar.json; recomputed | corrected (wording "forecast to miss"; Dutch 2032 stated) |
| 2 | WindEurope 2030 forecast, seven countries | 68.4 GW | 31.96+16.52+8.38+4.01+4.93+2.17+0.45 = 68.42 | WindEurope Table 4, pp. 44–45 | ok |
| 3 | Sum of national targets | 128.8 GW | 50+30+21+12.9+5.9+6+3 = 128.8 | wind-calendar.json `awarded_vs_targets` | ok |
| 4 | Offshore connected in 2025, lowest since 2016 | 1.96 GW | 1,049+503+408 = 1,960 MW; series 2016–2025: 1.5, 3.2, 2.7, 3.7, 2.9, 2.9, 2.5, 3.7, 2.6, 2.0 | WindEurope pp. 11, 16 | ok ("least" → "lowest") |
| 5 | Failed negative-bidding rounds 2024–25 | 6.5 GW DK/DE/NL | "6.5 GW of negative bidding rounds: 3 GW Denmark, 2.5 GW Germany, 1 GW Netherlands" | WindEurope p. 25 | ok (Danish round was zero-subsidy: wording widened) |
| 6 | Denmark 1.8 GW at 67.6–72.7 €/MWh, "signed on 6 November" | — | DKK 504 (Holmsland) and 542 (Hesselø), 20 years, two and five bids, awarded August 2026. The final agreements were reported on 5–6 November (energyglobal 5/11, offshoreWIND.biz 6/11). The euro figures differ slightly between sources (67.4–72.5) | offshoreWIND.biz 4/8 and 6/11 | corrected (award in August, signature in November) |
| 7 | Gamma window and caps | 26/11–10/12 2026; 117 and 116 €/MWh | Gamma-B: 26/11 00:00 to 10/12 17:00; max €0.116/kWh; budget €4.698 bn. The Gamma-A cap of 117 comes from the Rijksoverheid release via the calendar. In March the Gamma-B cap was €103 | RVO page (checked 30/10/2026); letter 16/3/2026 | ok |
| 8 | AR8 results 27 Nov 2026–17 Feb 2027 | — | law-firm summary of the framework (medium reliability) | wind-calendar.json (Foot Anstey) | n.v. |
| 9 | Germany "still needs a Bundestag vote in December" | — | the calendar says trade press conflicts on whether the Bundestag has voted; adoption is needed in December | wind-calendar.json WC-DE-WINDSEEG-LAW | corrected ("must pass … in December") |
| 10 | 5 of 11 calendar delays cite the grid | 5/11 | 11 items of type "delay". The 5 that match: North Sea Energy Island, PEZ lot 1, Sørlige Nordsjø II, Hornsea 3, BalWin1. Two of the five are energy islands | wind-calendar.json | corrected ("platforms or energy islands"; heading no longer an assessment presented as fact) |
| 11 | BalWin1 16/9/2030 → 15/9/2031 | — | identical; causes: converter platform design and manufacturing, onshore ground. It returns to the original 2031 target. It connects Windbostel Ost in the **North Sea** | HVDC World 8/7/2026 | ok (context added) |
| 12 | Monopile utilisation 19% in 2028 | 19% | "around 32% in 2026 and 2027 before falling to just 19% in 2028" | Rystad 18/9/2026 | ok ("will run" → "expected to run") |
| 13 | Gdańsk T5 253 M€; Klaipėda 201 M€ to 2027; Cuxhaven 1,250 m ~2028; Bremerhaven never built | — | identical in the data file | eolico-filiera.json | ok |
| 14 | Esbjerg 65 GW (2030) / 150 GW (2050); Ostend 120/300; Marienborg 19.6; Hamburg 300 GW, 100 GW cross-border, 15 GW a year 2031–40 | — | identical; texts guarded by need() | eolico-filiera.json `dichiarazioni` | ok |
| 15 | Declaration table: 19.27/31.08/48%; 38.29/66.94/56%; 0.26/5.82/30% | — | 47.8% → 48%; 55.8% → 56%; 29.7% → 30% | eolico-filiera.json `calcolo` | ok |
| 16 | 6.8 GW a year needed to reach 72.8 GW from 38.6 GW | 6.8 | (72,830−38,617)/5 = 6.84 | WindEurope; recomputed | ok |
| 17 | Hamburg 15 GW a year = 7.7 × 2025 | 7.7 | 15/1.96 = 7.65 | recomputed | ok |
| 18 | FID 2025: 5.4 GW, 22.5 bn €, four of six projects Polish | — | "€22.5bn, financing approximately 5.4 GW … four of the six projects" | WindEurope p. 35 | ok |
| 19 | Country table: installed, forecast (UK 16.98/32.0; DE 9.62/16.5; NL 4.74/8.4; DK 2.65/4.0; PL 0/4.9; BE 2.26/2.2; NO 0.10/0.5) | — | identical to Tables 1 and 4 of the PDF | WindEurope pp. 11–12, 44–45 | ok |
| 20 | Belgium forecast below installed | 2.2 vs 2.26 | the PDF really gives 2,170 MW for 2030 against 2,261 MW installed | WindEurope | ok (limit added) |
| 21 | Under construction (EMODnet) by country | — | sums of `riepilogo_mw` | offshore-nord.json | ok |
| 22 | Awarded 2023–26 by country (UK 13.8, DE 17.8, NL 4.0, DK 1.8, PL 3.4, BE 0, NO 1.5) | — | identical; UK AR6 = 400 floating + 3,363.07 + 1,578.51 = 5,341.6 MW; AR7 8,437.5 | wind-calendar.json; GOV.UK AR6 and AR7 | ok |
| 23 | FID column (DE 1.60; PL 2.94) | — | calendar FID items since 2025 | wind-calendar.json | ok |
| 24 | Targets: UK 50 (43–50), DE 30, NL 21 (2032), DK 12.9, PL 5.9, BE 6, NO 3 | — | identical; DK 12.9 comes from a secondary source (Port Esbjerg) | wind-calendar.json | ok / n.v. for DK |
| 25 | Gap target − installed: 33.0, 20.4, 16.3, 10.2, 5.9, 3.7, 2.9; total 92.4 | — | 92.44 | recomputed | ok |
| 26 | Awards cover 46% of the gap | 46% | 42.31/92.44 = 45.8%. Gross: it includes Hornsea 4 (2.4 GW, dropped), so 43% net. It is an upper bound (many sites lack an FID) | recomputed | corrected (gross/net and upper bound stated; difference from the 60.4 GW explained) |
| 27 | Germany 17.8 GW = 87% of gap; 16 GW without FID | — | 87.4%; "16 GW already awarded still lack FID" (Offshore Wind Foundation) | wind-calendar.json | ok |
| 28 | UK net of Hornsea 4: 11.4 GW | 11.4 | 13.78 − 2.4 = 11.38 | recomputed | ok |
| 29 | Netherlands: 21 GW moved from 2030 to 2032; 2040 goal cut | — | 2024 planning update: 21 GW at end-2032. July 2025: 30–40 GW for 2040. **But** RVO's roadmap page (checked 19/8/2026) cites a "23 GW" goal with no year and dates only Alpha (Q3 2029), Beta (Q4 2029) and Gamma-A/B (Q2 2032), so 4.7 + 5.5 + 2 ≈ 12.2 GW. The March 2026 letter still writes "approximately 21 GW around 2030" | RVO roadmap; letter 16/3/2026; WC-NL-TARGET | corrected (current position stated, with the conflict) |
| 30 | Denmark 4.0 vs 12.9 GW; Poland 4.9 GW = 84% of 5.9 | — | 4.01; 83.6% | recomputed | ok |
| 31 | Baltic EMODnet 2.7 GW operating, 3.8 under construction, 33% of Marienborg | — | 2,694; 3,834; 33.3% | eolico-filiera.json `baltico_emodnet` | ok |
| 32 | 571 MW electrolysers (July 2025) = 2.9% of 20 GW | — | 571; 2.86% | idrogeno.json (Hydrogen Europe via Renewables Now, medium) | ok |
| 33 | "No country except Poland above two thirds of its goal" | — | UK 63.9%, DE 55.1, NL 39.9, DK 31.1, BE 36, NO 15 | recomputed | ok |

### Section 3 (auctions)

| # | Claim | Value in report | Verified value | Source | Outcome |
|---|---|---|---|---|---|
| 34 | Norfolk Boreas halted July 2023, costs up to 40% | — | identical | wind-calendar.json | ok |
| 35 | AR5 (September 2023) without offshore bids | — | identical | wind-calendar.json | ok |
| 36 | Hornsea 4 dropped May 2025, DKK 3.5–4.5 bn | — | identical | wind-calendar.json (OE Digital) | ok |
| 37 | DK 3 GW no bids Dec 2024; N-10.1/10.2 (2.5 GW) Aug 2025; Nederwiek I-A (1 GW) Oct 2025 | — | identical | wind-calendar.json; WindEurope p. 27 | ok |
| 38 | Norway 1.5, France 1.2, Lithuania 0.7 cancelled or void | — | identical | WindEurope p. 25 | ok |
| 39 | AR7 8,437.5 MW on 14/1/2026, 91.20 and 89.49 £/MWh, 19–21% below ceiling | — | identical; 192.5 MW of it is floating (216.49 £); savings 19.29% and 20.81% on 113 £ | GOV.UK AR7 | ok (floating share and ceiling added) |
| 40 | Poland 3,435 MW, Dec 2025, 113–117 €/MWh | — | 900+975+1,560 at 113/116/117 | WindEurope Table 3 | ok |
| 41 | Danish CfD DKK 504/542, two and five bids, 20 years | — | identical | offshoreWIND.biz 4/8/2026 (via search) | ok |
| 42 | Belgium PEZ framework July 2026, ≥75% not Chinese | — | identical | wind-calendar.json | ok |
| 43 | EU Grids Package Dec 2025, two-sided CfD "reported" mandatory from 2027 | — | identical; already marked as reported | wind-calendar.json | ok |
| 44 | Price chart: UK 109/107, IE 99, FR 66, PL 113–117 €/MWh | — | identical to WindEurope Table 3 | offshore-wind-esterni.json; PDF p. 27 | ok |
| 45 | Chart caption: Danish prices "offshoreWIND.biz, 6 November 2026" | — | the prices are in the 4 August article; the 6 November article has none | offshoreWIND.biz | corrected |
| 46 | DK 67.6 €/MWh is 49 €/MWh below Poland's 117 | 49 | 49.4 | recomputed | ok |
| 47 | Dutch caps 117/116, raised from 104 | — | Rijksoverheid 15/6/2026 via calendar; the March letter proposed 103 for Gamma-B | wind-calendar.json; letter | ok |
| 48 | Gamma-B budget 4.698 bn € | — | €4,698,000,000 | RVO | ok |
| 49 | Gamma-A budget 3.98 bn € | — | secondary; not found on RVO (Gamma-A page 404) | eolico-filiera.json | n.v. |
| 50 | Gamma platform "Q2 2031, a year late" | Q2 2031 | the RVO roadmap now gives the Gamma farms Q2 2032. Q2 2031 was the plan before the one-year platform slip. Permits are expected in Q1 2027 | RVO roadmap; letter 16/3/2026 | corrected |
| 51 | AR8: opened July 2026, ASP 113 £ frozen, >17 GW eligible | — | calendar, offshoreWIND.biz/Enerdata (medium) | wind-calendar.json | ok (on file) |
| 52 | WindSeeG: rounds of 2–4.8 GW, caps 94.87/96.72 €/MWh, Bundesrat 16/10 | — | the caps come from a secondary source, already flagged | eolico-filiera.json | n.v. (caps) / ok |
| 53 | Curonian Nord: minister July 2026, EIA 30/6, Ignitis buying 49%, decision end-2026 | — | identical | wind-calendar.json (LRT, Windtech) | ok |
| 54 | Calendar: 114 items, 84 done, 18 scheduled, 8 at risk, 4 unconfirmed | — | identical | wind-calendar.json `riepilogo` | ok |
| 55 | Assessment "a failed Gamma round would make 21 GW by 2032 hard to defend" | — | on RVO's dated sites 21 GW by end-2032 is already out of reach (≈12.2 GW dated) | RVO roadmap | corrected (assessment rewritten) |

### Section 4 (bottlenecks)

| # | Claim | Value in report | Verified value | Source | Outcome |
|---|---|---|---|---|---|
| 56 | Prysmian backlog 16.5 bn € on 29/10/2026, plus ~2 bn not booked | — | identical; the backlog "now includes the contribution from Xtera" (telecom) | Prysmian Q3 2026 release | ok (Xtera added) |
| 57 | NKT 13.0 bn € on 30/6/2026; 11.6 bn at standard metal prices; 1.4 bn difference | — | identical; TenneT framework (>2.5 bn) excluded; no Q3 2026 report found on 10/11 | NKT H1 2026 | ok |
| 58 | Nexans 7.7 bn € adjusted, June 2026 | — | secondary, already flagged | eolico-filiera.json | n.v. |
| 59 | Prysmian + NKT 29.5 bn € | 29.5 | 16.5+13.0; different dates | recomputed | corrected (dates stated) |
| 60 | Karlskrona 2027; Sumitomo UK factory October 2026 | — | NKT H1: Karlskrona "operational in 2027"; Sumitomo 21/10 in the calendar | NKT; wind-calendar.json | ok |
| 61 | Hitachi Energy order book >30 bn $ (IEA) | — | 2025 IEA report; not reread | eolico-filiera.json | n.v. |
| 62 | 14 OSM HVDC links under construction | 14 | recomputed by the script | rete-elettrica.json | ok |
| 63 | Five grid delays (texts) | — | identical summaries | wind-calendar.json | ok |
| 64 | Borkum Riffgrund 3 COD 31/8/2026, ~5 months late; Kriegers Flak paused 2024 | — | identical | wind-calendar.json (Ørsted) | ok |
| 65 | Siemens Gamesa −44 M€ (Q2 FY2026), from −249 | — | correct for Q2. **Out of date:** Q3 FY2026 (Apr–Jun) was positive, "first time since fiscal year 2022", about +75 M€ before special items (secondary summaries) | Siemens Energy 5/8/2026; search | corrected |
| 66 | GE Vernova wind EBITDA −275 M$ (Q2 2026), from −165; 2026 loss ~400 M$ | — | correct for Q2. **Out of date:** Q3 2026 = +72 M$ (−61 a year earlier), margin 2.6%; guidance now **400–500 M$** of losses | GE Vernova 8-K, 28/10/2026 | corrected |
| 67 | GE "has suspended new offshore orders" | — | reNEWS (403); not in the Q3 release | eolico-filiera.json | n.v. (attributed to reNEWS) |
| 68 | Dogger Bank A first 300 MW CfD start 31/7/2027 | — | identical | wind-calendar.json | ok |
| 69 | Average offshore turbine 2025: 10.7 MW | 10.7 | "10.7 MW for offshore" | WindEurope p. 9 | ok |
| 70 | WTIV ≥15 MW: from none in 2020 to >25 by 2028; tight from 2032 | — | identical | eolico-filiera.json (Intelatus via OE Digital) | ok |
| 71 | Foundation vessels 8–9 by 2028; CLV 37 (2025), 48 (2030) | — | identical | eolico-filiera.json | ok |
| 72 | Cadeler 66% H1 2026 | 66% | 66% (67% in H1 2025), ten vessels | Cadeler H1 report (SEC) | ok (comparison added) |
| 73 | Cadeler 47.6% in Q1 | 47.6% | not in the H1 report; the figure comes from the Q1 report via the data file | eolico-filiera.json | n.v. |
| 74 | Cadeler order book 2.5 bn € | 2.5 | 2.5 bn at 30/6; 2,487 M€ at 25/8, 77% with FID | Cadeler H1 report | ok (detail added) |
| 75 | Monopiles: 1.2 Mt (2024) → 2.7 Mt (2027); 32% → 19% → ~50% (2031); 3.46 vs 2.03 M$/kt; 6.35 vs 6.69 M$; Sif 31%, EEW 22%, Dajin 12% | — | identical | Rystad 18/9/2026 | ok |
| 76 | Supply-chain investment since 2022 | 15.4 bn € | "at least €15bn"; 15.4 appears in the PDF only as 2017 onshore investment (Fig. 17). "70% focused on offshore" | WindEurope p. 35 | corrected |
| 77 | Technicians ~10,000 (2028), >19,000 (2032–33) | — | GWO page; not reread | eolico-filiera.json | n.v. |
| 78 | 607,000 jobs by 2030 "from 442,800 in 2025" | 2025 | 442,800 is **2024** (2025: 484,700); "607,000 — a 37% increase" | WindEurope p. 51, Fig. 27 | corrected |

### Section 5 (ports)

| # | Claim | Value in report | Verified value | Source | Outcome |
|---|---|---|---|---|---|
| 79 | Port table: PortWatch 30 days to 30/10 (Esbjerg 3.3 −8.3%; Eemshaven 2.8 +55.6%; Rotterdam 81.4 +2.3%; Rostock 6.3 +5.0%; Gdańsk 9.5 −5.0%; Świnoujście 9.7 +40.6%; Klaipėda 8.3 −3.5%) | — | identical | porti-nord.json | ok |
| 80 | Port Risk Index: 3.2, 5.7, 7.5, 4.3, 7.0, 6.1, 7.5 | — | identical | port-risk.json | ok |
| 81 | Esbjerg: 27.5 GW shipped, 13.5 GW next 5 years, 57 ha, channel 9.3→12.8 m, Thor 36/72, 5,426 calls (−5%) | — | identical; the 350 m quay is "secondary, status not confirmed" | eolico-filiera.json; porti-nord.json; Port Esbjerg | ok / n.v. (quay) |
| 82 | Eemshaven 40 t/m², April 2026, Ecowende 760 MW final turbine 2/11, OranjeWind 795 MW | — | identical | eolico-filiera.json; wind-calendar.json | ok |
| 83 | Vlissingen 17 of 23 caissons by June 2026 | — | identical | eolico-filiera.json | ok |
| 84 | Sif: 328 M€ factory; 211 kt vs 124 kt; line closure; EGM 22/12/2026; Arianehaven 45 ha mid-2029 | — | identical | eolico-filiera.json (Windtech) | ok |
| 85 | Cuxhaven 1,250 m, 38 ha, ~3.5 years from early 2025; Dajin–Briese MoU Dec 2025 | — | identical | eolico-filiera.json | ok |
| 86 | Bremerhaven OTB 500 m, 25 ha, 180 M€, BUND | — | identical (2016 sources) | eolico-filiera.json | ok |
| 87 | Rostock EEW 10 m → 12 m (early 2027) → 15 m; >100 monopiles a year | — | identical | eolico-filiera.json | ok |
| 88 | Mukran: Windanker 315 MW, 21 turbines; Iberdrola 1.1 GW; FSRU left for Egypt (IEEFA) | — | identical | eolico-filiera.json; esposizione-nord.json | ok |
| 89 | Rønne 15 ha, 11 m, 300 m; Bornholm island 2034; joint tender unconfirmed | — | identical | eolico-filiera.json; wind-calendar.json | ok |
| 90 | Gdańsk T5 21 ha, 253 M€ (194 M€ state aid), 111 monopiles by August 2026 | — | identical | eolico-filiera.json | ok |
| 91 | Gdańsk risk "driven by GNSS interference within 50 km" | — | score = probability 1.7 × impact 4.1. GNSS is the only red probability indicator, but the level comes from impact (size, energy) | port-risk.json | corrected |
| 92 | Świnoujście 50 t/m², June 2025, LoI June 2026 | — | identical | eolico-filiera.json | ok |
| 93 | Klaipėda 453 m, 36.6 M€, 201 M€ programme, 100 M€ EIB, end-2027 | — | identical | eolico-filiera.json | ok |
| 94 | Ostend 650 M€ EIB; Nigg >30 M£, Mitsui; Hull >1,400 staff; ABP 63.9% to IFM on 22/10 | — | identical | eolico-filiera.json; wind-calendar.json | ok |
| 95 | Grenaa and Hvide Sande candidate bases; no base port announced | — | the cited 6/11 article names Hvide Sande only as the location; "candidate" comes from the data file | eolico-filiera.json | n.v. |

### Section 6 (risks)

| # | Claim | Value in report | Verified value | Source | Outcome |
|---|---|---|---|---|---|
| 96 | US 10-year 4.88% on 9/11, +77 bp | — | 4.88; var 1a = 77 | prezzi.json | ok |
| 97 | Euro AAA 10-year | 3.29% (6/11), +55 bp | rebuilt online: 3.27% on 9/11, +52 bp on 7/11/2025 | ECB Data Portal (fetched by the script) | corrected (new reading) |
| 98 | ECB deposit rate 2.50% (2.00% a year earlier) | — | cache (the ECB call returned 504); 2.50% since 16/9/2026 | offshore-wind-mercati.json | ok |
| 99 | Capital charge 7.82% / 8.58%, +9.7% | — | crf(6%,25) = 0.07823; crf(7%,25) = 0.08581; +9.69% | recomputed | ok |
| 100 | Copper 6.33 $/lb, +24.4% | — | rebuilt: 6.31 $/lb (10/11, provisional), +24.1% | Yahoo Finance | corrected (new reading) |
| 101 | US HRC 1,413 $/st, +66.0% | — | identical; in the final build this series came from the cache (Yahoo returned 429) | Yahoo Finance | ok |
| 102 | TTF 82.33 €/MWh (9/11), +164%; DE storage 58.9%, NL 63.5% (8/11) | — | 82.33, +163.88%; 58.94; 63.51 | prezzi.json; scorte.json | ok (same as the Northern Europe report) |
| 103 | Six Baltic cable incidents since November 2024, latest 2/1/2026 | 6 | 6 | baltico-sicurezza.json; Northern Europe report | ok |
| 104 | Estlink 2, 650 MW, anchor, 25/12/2024 | — | identical | interconnessioni.json | ok |
| 105 | 15 drone events since September 2025; Esbjerg 24/9/2025; Kiel | — | identical (same 15 in the Northern Europe report) | baltico-sicurezza.json | ok |
| 106 | GPSJam 214–246 high cells a day, 2–8 November; near sites 6/3/2/9/10 | — | recomputed by the script (haversine, 75 km) | baltico-sicurezza.json | ok |
| 107 | Sweden: 13 rejected (Nov 2024), 11 (July 2026); Poseidon; two approved | — | identical | wind-calendar.json | ok |
| 108 | KA-SAT: GRU (EU, US, UK); 5,800 Enercon turbines, 10–11 GW; >95% by 19/4/2022; Nordex; Deutsche Windtechnik ~2,000 | — | identical in the data file (need() guards) | cyber-energia.json; SentinelOne | ok |
| 109 | CERT Polska: 29/12/2025, >30 wind and PV farms, a manufacturer, a CHP plant; RTUs; production not interrupted | — | "more than 30 wind and photovoltaic farms, a private company from the manufacturing sector, and a large combined heat and power plant"; RTUs damaged, communication with DSO lost | CERT Polska, 30/1/2026 | ok |
| 110 | Poland attributes it to Russia, researchers dispute the group | — | data file ("contestata") | cyber-energia.json | ok |
| 111 | Denmark threat level medium (June 2024), energy orange (Sept 2025); Lithuania ban above 100 kW | — | identical | cyber-energia.json | ok |
| 112 | French attribution of the supermarket attacks to the IRGC (9/11/2026) | not in the report | Reuters (Satter, Stargardter) via Al-Monitor, 9/11: "French officials … accused Iran's Revolutionary Guards". No primary French government statement found | Al-Monitor; search | n.v. (not used; a limit now says why) |
| 113 | Fleet: 20 vessels, 4 Chinese-built (Voltaire, Les Alizés, Boreas, Seaway Ventus), 1 Korean (Wind Maker) | — | recomputed from `navi` | eolico-filiera.json | ok |
| 114 | LS Cable LanWin4; Siemens Energy first 2 GW platform in a German yard | — | identical | eolico-filiera.json | ok |

### Sections 7–9 (implications, watch list, method)

| # | Claim | Value in report | Verified value | Source | Outcome |
|---|---|---|---|---|---|
| 115 | "Day rates are under pressure (Cadeler at 66%)" | — | not supported: utilisation is level year on year and the 2026 book is substantially filled; day rates are not public | Cadeler H1 report | corrected (assessment rewritten) |
| 116 | Watch list: Gamma "a repeat … would undercut 21 GW by 2032" | — | see rows 29 and 55 | RVO | corrected |
| 117 | Watch list: "Gamma platform Q2 2031" | — | Q2 2032 (farms) | RVO roadmap | corrected |
| 118 | Watch list: SGRE/GE "44 M€ loss" | — | both positive in the latest quarter | rows 65–66 | corrected |
| 119 | Copper threshold +10% | 6.96 | 6.31 × 1.1 = 6.94 | recomputed | corrected (follows row 100) |
| 120 | Failed auctions 6.5 vs 7.2 GW, "including UK AR5 and Lithuania" | — | 7.2 = 3 + 2.5 + 1 + 0.7 (Lithuania once). AR5 adds no GW (no offshore volume). With Norway and France, 9.9 GW failed in 2024–2025 | report/agenti/wind-calendar.md; WindEurope p. 25 | corrected (perimeters explained) |
| 121 | Dutch target conflict 2030 vs 2032 | — | see row 29 | RVO; letter | corrected (government's own sources quoted) |
| 122 | "Checked online" list | — | the Danish item cited the 6/11 article for prices that are not in it | esterni | corrected (list rewritten from this review) |
| 123 | Source table dates (eolico-filiera 2026-11-10T06:25Z etc.) | — | `aggiornato` fields of the files | docs/data | ok |

**Count:** 123 rows · ok 88 · corrected 25 · n.v. 10.

## 2. The conflicts the author listed

1. **Netherlands, 21 GW in 2030 or 2032.** The Dutch government moved the 21 GW goal to the end of 2032 in its 2024 planning update, and kept it there in July 2025 when it cut 2040 to 30–40 GW. There is no formal change since then. The government's own documents are no longer consistent, though. The 16 March 2026 letter to Parliament still describes "the Roadmap for approximately 21 GW … around 2030" in its appendix. RVO's roadmap page (checked 19 August 2026) speaks of a 23 GW goal with no year, and gives commissioning dates only for about 12.2 GW, the last being Gamma-A/B in Q2 2032. The other ~9 GW (Nederwiek, Doordewind, Waddeneilanden, HKW VIII) are "to be determined". The report now uses end-2032 as the latest formal date, quotes the conflict, and assesses 21 GW by 2032 as out of reach on RVO's own dated plan. The gap (16.3 GW) does not depend on the year. The Dutch shortfall (12.6 GW) compares a 2030 forecast with a 2032 target, and the text now says so.
2. **Failed rounds, 6.5 GW vs 7.2 GW.** Both are right; they measure different things. WindEurope's 6.5 GW covers only zero-subsidy and negative-bidding rounds in 2024–2025 that drew no bids: Denmark 3, Germany 2.5, the Netherlands 1. The calendar's 7.2 GW covers 2023–2025 tenders with no award. It adds Lithuania's 0.7 GW CfD tender (counted once, although it failed in 2024 and 2025). UK AR5 (2023) is named but adds nothing, because it had no set offshore volume. Neither count includes the CfD rounds that Norway (Sørvest F, 1.5 GW) and France (AO7 Oléron, 1.2 GW) cancelled. On WindEurope's full list, 9.9 GW failed or was cancelled in 2024–2025.
3. **60.4 GW gap and 46% coverage.** These are two different measures, and the old text let them be read as one.
   - **60.4 GW** is the shortfall: Σ(target − WindEurope 2030 forecast) for the seven countries. It is 128.8 − 68.4 GW, with the Dutch target for 2032 and Belgium's forecast below its installed base.
   - **46%** is gross awards since 2023 (42.3 GW) divided by the gap from end-2025 capacity (92.4 GW). Net of Hornsea 4 (dropped) it is 43%.
   - The 46% is an upper bound on delivery, not a forecast: most awards come online after 2030, and in Germany alone 16 GW of awarded sites lack an FID. All three numbers are now in the text with their definitions.

## 3. Cyber paragraph

The report does **not** mention the French attribution of the October–November 2026 supermarket-refrigeration attacks to Iran's IRGC. I checked the Markdown, the HTML and the script. The claim sits only in `docs/data/cyber-energia.json`, and the script never reads those fields.

I found a Reuters story republished by Al-Monitor on 9 November 2026 ("French officials blame Iran for refrigerator hacks, vow retaliation"). I found no primary French government statement (Quai d'Orsay, ANSSI or Élysée). A web search turned up only the October attack coverage, with no attribution. Earlier French attributions in 2026 concerned Russia (July 2026).

So the claim stays unconfirmed. Because it does not concern wind, I did not add it to the text. A limits line now records it as "reported by Reuters via Al-Monitor and AP on 9 November 2026; no primary French government statement found; not independently confirmed; not used", so a reader of `cyber-energia.json` knows why it is missing.

## 4. Logic, consistency, readability

- **Assessments presented as facts.** The heading "The grid, not ships or steel, now sets the pace" was a judgement resting on a 5-of-11 count from a curated list. It now reads "Grid links are the most common cause of delay", which the count supports. "Will run at 19%" and "will fall short" are forecasts, now worded as forecasts.
- **Out-of-date company data.** Siemens Gamesa's Q3 FY2026 profit was published 5 August, and GE Vernova's Q3 wind profit on 28 October. Both came before the data files were built. The "Turbine makers' finances" row still ranks medium strain (curated). The assessment now says one profitable quarter does not end the margin constraint. GE's raised 2026 loss guidance supports that.
- **Consistency with docs/report/en/northern-europe-2026-11.html.** The shared numbers match: 1.96 GW, 72.8 GW, declarations table, TTF, storage, six cable incidents, 15 drone events, GPSJam 214–246, Prysmian 16.5 bn €, BalWin1, Cadeler 66%. **Three items in the Northern Europe report are now inconsistent with this one, and its owner should fix them** (outside this review's scope, so not changed):
  - (a) it still gives the Dutch target as "21 GW in 2030";
  - (b) it quotes Siemens Gamesa's Q2 loss (−44 M€) as current;
  - (c) it quotes "15.4 billion €" of supply-chain investment.

  All three come from `eolico-filiera.json`. The two data-file errors (15.4 bn €, jobs base year 2025) should be corrected by the agent that maintains that file.
- **Consistency with the wind calendar.** Dates, statuses and counts match `wind-calendar.json`, with one exception. The calendar item WC-NL-IJVBETA-GRID still quotes the RVO "Gamma Q2 2031" date, and the report now uses RVO's current Q2 2032. This should be flagged to the calendar's maintainer.
- **Key points (60-second test).** There are five points of 48–58 words. Each has a verb, a figure and a source, and each figure appears in the body. Someone at Ørsted, Cadeler, Van Oord, DEME, TenneT or Port Esbjerg gets the shortfall, the auction model, the December tests, the grid and the ports. The Cadeler and TenneT angles are covered in sections 4 and 7, and the review box points to the corrections.
- **Tone.** No alarmist wording found.

## 5. Charts and page

- The charts were rebuilt by the script with the corrected data (four SVGs, wide and narrow). The targets chart is unchanged. The prices chart caption was corrected (row 45). The markets chart uses the new readings (rows 97, 100).
- Playwright (Chromium) at 1440 px and 390 px, light and dark: no console errors, no horizontal page scroll (scrollWidth = viewport). Wide tables scroll inside their own container at 390 px. Screenshots: `/tmp/claude-0/-home-user-monitor-geoeconomico/f58f0587-e0c2-5682-b8ba-39bc1c573ea8/scratchpad/rev-wind/` (`ow-1440-light-*.png`, `ow-390-light-*.png`, `ow-390-dark-*.png`; top, full page, key points, review box).

## 6. What remains open

- Not verifiable from here (n.v. rows): Danish 12.9 GW target (secondary); WindSeeG second-stage caps; Nexans backlog; Gamma-A budget; AR8 timetable; Esbjerg's 350 m quay; Hitachi order book; GWO technician demand; Cadeler Q1 47.6%; GE's suspension of offshore orders (reNEWS 403); Grenaa/Hvide Sande as candidate bases; the French IRGC attribution.
- NKT's Q3 2026 report was not found on 10 November. Siemens Energy's FY2026 results (due mid-November) will replace the Q3 Siemens Gamesa figure. Re-read both in the December edition.
- In the final build the ECB deposit-rate series (ECB API 504) and US HRC (Yahoo 429) came from the cache, read earlier the same day; the report says "partly from cache".
