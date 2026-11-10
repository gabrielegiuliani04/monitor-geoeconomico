# Offshore wind calendar: North Sea and Baltic, 2023-2027

Updated 10 November 2026. File: `docs/data/wind-calendar.json`, built by `raccolta/eolico/calendario.py` from the curated items in `raccolta/eolico/calendario_voci.json`.

**In one sentence:** the auction cycle has restarted where states carry price risk (UK, Denmark, Poland). It is still stalled where they do not (German negative bidding, the Dutch zero-subsidy model, the Baltic states). Delivery is now held back by grid connections more than by turbines or vessels.

The file holds 114 items: 84 done, 18 scheduled, 8 at risk and 4 unconfirmed. It covers 13 countries plus EU-level items. There are 36 auctions, 23 policy items, 11 delays, 9 grid items, 9 construction items, 8 commissioning items, 7 first-power items, 6 cancellations and 4 FIDs.

---

## 1. What's coming (next 90 days, 10 Nov 2026 to 8 Feb 2027)

| When | Country | Milestone | Why it matters |
|---|---|---|---|
| 26 Nov to 10 Dec 2026 | NL | **IJmuiden Ver Gamma-A + Gamma-B tender** (2 GW). Subsidised permit with caps of EUR 117 and 116/MWh | This is the first Dutch tender since Nederwiek I-A got zero bids. If it fails, the 21 GW by 2032 target loses credibility. |
| 27 Nov 2026 to 17 Feb 2027 (window) | GB | **AR8 results**. Ceiling GBP 113/MWh (2024 prices); more than 17 GW eligible | Shows whether AR7's GBP 91 clearing price holds. The timing depends on qualification appeals. |
| Dec 2026 | DE | **Bundestag vote on the WindSeeG reform**, due to take effect 1 Jan 2027 | Sets the design of the two-stage model, with a CfD only as fallback. The Bundesrat (upper house) opposed the model on 16 Oct. |
| Dec 2026 | LT | **Curonian Nord (700 MW) decision**: continue, postpone or seek state aid | The minister has said the project is "not feasible on commercial terms". |
| End-2026 / early 2027 | FR | **AO10 first winners** (about 10 GW; none in the North Sea) | Political risk from the presidential campaign. |
| Q4 2026 | PL | **Gdansk T5** starts serving Baltica 2 | First Polish installation-port lease. |
| Q1 2027 | GB | **Hornsea 3 first power** (2.9 GW) | Delayed by grid works at Norwich Main. |
| Late 2026 (broad date) | GB / PL | Full operation of Sofia (1.4 GW) and East Anglia Three (1.4 GW); commercial operation of Baltic Power (1.14 GW); Dogger Bank B | All four have year-end targets with no confirmation yet. East Anglia Three and Dogger Bank B are flagged "at risk". |

## 2. What slipped

**Dates that have passed without confirmation.** The script flags these automatically as "unconfirmed":
- **He Dreiht full 960 MW** was expected in October 2026 (EnBW at the inauguration). No confirmation found. The original target was summer 2026.
- **Bornholm joint DK-DE tender.** In January 2026 the governments said it would launch "in the coming months". Nothing launched by November.
- **Swedish state-led support system**, proposed to start 1 Jul 2026. Adoption not confirmed. Meanwhile 11 more projects were rejected on defence grounds in July 2026.
- **AO10 bid deadline (12 Oct 2026).** The number of bids has not been published.

**Confirmed delays (2025-2026):**
- **Grid:** BalWin1 slips from 16 Sep 2030 to 15 Sep 2031, and BalWin2 is pending. Hornsea 3 first power moves to Q1 2027, with commissioning in Q4 2027 to Q1 2028. Borkum Riffgrund 3 reached COD on 31 Aug 2026 instead of Q1 2026 (DolWin5 and grid outages). The Nederwiek II and IJmuiden Ver Gamma platforms are one year late. Princess Elisabeth Island phase 1 now has a deadline of 1 Oct 2031.
- **Projects:** Zeevonk (2 GW) moves to 2032 in two phases. The Dogger Bank A CfD start moves to 31 Jul 2027 because of turbine repairs. Sorlige Nordsjo II's licence deadline is extended by 12 months over a grid route review. Dunkerque has slid from 2026 to roughly 2027-2028 (low-reliability source).
- **Cancellations:** Norfolk Boreas (Vattenfall, July 2023; restarted by RWE). Swedish Kriegers Flak paused (September 2024). **Hornsea 4** dropped despite its AR6 CfD (May 2025, DKK 3.5-4.5 bn break costs). Sorvest F tender cancelled (2025). Estonian CfD auction dropped (February 2025). Vattenfall will not build Vidar for now, despite its July 2026 permit.
- **Failed auctions:** UK AR5 got zero offshore bids (2023). Denmark's 3 GW tender got zero bids (December 2024). Germany's N-10.1/N-10.2 (2.5 GW) got zero bids (August 2025). The Netherlands' Nederwiek I-A (1 GW) got zero bids (October 2025). Lithuania's second 700 MW tender failed twice (2024; void in October 2025). In total, **about 7.2 GW of tenders drew no award** between 2023 and 2025.

## 3. GW awarded vs targets (auctions with revenue support or zero-subsidy permits)

| Country | Awarded 2023 | 2024 | 2025 | 2026 | Total 2023-26 | Target | Gap vs end-2025 installed | Awarded as % of gap |
|---|---|---|---|---|---|---|---|---|
| GB | 0 | 5.34 | – | 8.44 | **13.8 GW** | 43-50 GW (2030) | 33.0 GW | 42% |
| DE | 8.8 | 8.0 | 1.0 (2.5 failed) | – | **17.8 GW** | 30 GW (2030) | 20.4 GW | 87% |
| NL | – | 4.0 | 0 (1 failed) | 2 GW in tender | **4.0 GW** | 21 GW (2032) | 16.3 GW | 25% |
| DK | – | 0 (3 failed) | – | 1.8 | **1.8 GW** | 12.9 GW (2030) | 10.2 GW | 18% |
| PL | – | – | 3.4 | – | **3.4 GW** | 5.9 GW (2030) | 5.9 GW | 58% |
| NO | – | 1.5 | – | – | **1.5 GW** | 3 GW (2030) | 2.9 GW | 52% |
| BE / FR (North Sea) / LT / EE / LV / FI / SE | 0 | 0 | 0 | 0 | **0** | – | – | – |

How to read this: Germany has awarded almost enough capacity to cover its 2030 gap. But 16 GW of awarded sites still lack an FID (Offshore Wind Foundation, September 2026), and BalWin-type delays push delivery into the 2030s. Awarded capacity is an upper bound for what will be built: most of it comes online after 2030. The script calculates these figures. Installed capacity at end-2025 comes from WindEurope via `eolico-filiera.json`.

## 4. Ten current facts (number, date, source)

1. **AR7 (UK) awarded 8,437.5 MW** on 14 Jan 2026, at GBP 91.20/MWh (England and Wales) and 89.49 (Scotland), 2024 prices. RWE's Dogger Bank South and Norfolk Vanguard projects account for 6.1 GW of it in the North Sea (GOV.UK results table).
2. **Denmark is back:** Vattenfall won 1.8 GW at DKK 504 and 542/MWh under two-sided CfDs (4 Aug 2026), after zero bids in 2024. Final agreements were signed on 6 Nov 2026, with commissioning in 2032 (KEFM; offshoreWIND.biz).
3. **Poland's first CfD auction awarded 3,435 MW** on 17 Dec 2025, at about EUR 113-117/MWh. **Baltic Power delivered Poland's first offshore power** on 10 Jul 2026 (Notes from Poland; gov.pl).
4. **German negative bidding broke down:** EUR 12.6 bn was paid for 7 GW in 2023, then zero bids for 2.5 GW in August 2025. The reform bill targets 1 Jan 2027 (offshoreWIND.biz).
5. **Hornsea 3 (2.9 GW):** a grid delay at Norwich Main pushes first power to Q1 2027 (Orsted Q1 2026 call).
6. **BalWin1 (2 GW) slips one year to 15 Sep 2031** (Amprion via Windtech, July 2026).
7. **Belgium's PEZ lot 1 (700 MW) has a new framework** (18 Jul 2026): a two-sided CfD with no cap and NZIA rules, which require at least 75% of turbines not to be made or assembled in China.
8. **The Netherlands raised its Gamma caps** to EUR 117/116 per MWh (15 Jun 2026). The 2040 target was cut from 50 GW to 30-40 GW (July 2025).
9. **Sweden approved 2 projects and rejected 11** on defence grounds (July 2026). Vattenfall is not proceeding with the 2 GW Vidar.
10. **Thor (1.08 GW)** produced first power on 17 Mar 2026, and full commissioning is due in spring 2027. Borkum Riffgrund 3 (913 MW) reached COD on 31 Aug 2026.

## 5. Interview talking points (NL / DK / Baltic offshore and port roles)

- **"Who carries price risk decides whether auctions clear."** Zero-subsidy and negative-bidding designs failed in DK (2024), DE (2025) and NL (2025). Two-sided CfDs cleared in GB, DK and PL. The EU Grids Package pushes two-sided CfDs as the norm. Ask a port or developer: which pipeline sits behind your 2028-2032 throughput assumptions?
- **"Grid is the new bottleneck."** BalWin1, Hornsea 3, DolWin5/Borkum Riffgrund 3 and Princess Elisabeth all slipped because of HVDC links or substations, not vessels. For a port, a one-year platform delay moves a whole marshalling campaign.
- **"Ports need project-linked leases."** Examples: Gdansk T5 for Baltica 2 (Q4 2026 to 2028), Eemshaven's dual-project upgrade, Klaipeda's EUR 201 m upgrade (EUR 100 m from the EIB), Raahe's MoU. The Dutch busy years are 2027-2028 (OranjeWind turbines in 2027; Ecowende done in November 2026). After that, utilisation depends on the outcomes of Gamma and Nederwiek.
- **"The Baltic is real, but uneven."** Poland has about 4.1 GW at FID (Baltic Power, Baltica 2, Baltyk 2/3) plus 3.4 GW awarded in December 2025. Lithuania, Estonia and Sweden have stalled for financial or defence reasons. Bornholm (3 GW, 2034) is the cross-border anchor, but its tender is late.
- **"Security now shapes siting."** Sweden's defence vetoes and Belgium's limits on Chinese content both reshape supplier and port choices. Pair this with the Baltic cable incidents covered in other layers.
- **Numbers to quote:** AR7 GBP 91.20; DK DKK 504; PL about EUR 115; NL cap EUR 117. Failed auctions: 7.2 GW in 2023-2025. Germany has 16 GW awarded without FID.

## 6. Links with other layers

- `eolico-filiera.json`: ports, vessels and bottlenecks. The calendar dates explain when each port's campaigns start and end, and the installed-capacity data feeds the target gaps here.
- `offshore-nord.json`: farm polygons and hubs (Bornholm, IJmuiden Ver, Princess Elisabeth). Calendar `project` names match the farm names there.
- `cavi-incidenti.json` / `baltico-sicurezza.json`: Baltic cable security alongside Swedish defence vetoes. `rete-elettrica.json`: HVDC links.
- `prezzi.json`: TTF and rates. Interest rates explain the failed negative-bidding rounds, and gas prices make CfDs cheap for the state. `calendario.json`: the macro calendar; the next-90-day wind items could be merged into it as category `eolico`.

## 7. Map and UI proposal

- **Timeline panel** "Offshore wind milestones": a horizontal timeline from 2023 to 2028, coloured by `status_effective` (done grey, scheduled blue, at risk orange, unconfirmed red outline). Filter by country and type. Drawing low-precision dates (`precision` year or half) as bars rather than points avoids false precision.
- **Map badges:** a small marker on each farm or hub in `offshore-nord.json` showing the next milestone date, matched by project name.
- **"Awarded vs target" bars** per country, from `riepilogo.awarded_vs_targets`.
- **"New in the feed" box** from `candidati_rss`, marked as unverified.

## 8. Sources tried

| Source | Result | Licence / note |
|---|---|---|
| GOV.UK (AR6, AR7 results pages; Clean Power 2030) | works; tables parsed | Open Government Licence v3.0 |
| offshoreWIND.biz articles and RSS (`/feed`) | works with curl (`/feed/` redirects; `/rss` 404) | (c) Navingo: facts and links only |
| Orsted Q1 2026 earnings call transcript (PDF) | works | (c) Orsted |
| RWE, Equinor, Vattenfall, KEFM, BMWE, Bundesnetzagentur, rijksoverheid.nl, rvo.nl, regjeringen.no, LRT, ERR | work (link check passed) | official or company pages, citation |
| **english.rvo.nl** | **does not resolve from this session** (not in the network allowlist). rvo.nl (Dutch) works | – |
| gov.pl, investinlatvia.org | connection reset (intermittent) | – |
| windeurope.org | 503 during the link check (seen before) | – |
| vozpopuli.com (Hornsea 3 summary) | 404, so replaced by the Orsted transcript | – |
| DESNZ AR8 timetable, BNetzA 2026 tender schedule, Danish Bornholm tender page | not found or not checked directly; secondary sources used, marked `medium` | – |

## 9. Limits

- The items are curated by hand. The script validates them, flags stale dates and suggests RSS candidates, but it never adds facts by itself. With `CONTROLLA_LINK=1` it checks links; the last run found 0 broken links after fixes, apart from intermittent gov.pl and windeurope.org.
- **Conflicts noted, not resolved:** whether the Bundestag has already voted on the WindSeeG reform; Bornholm's split (2 GW to DE plus 1.2 GW to DK does not equal 3 GW); German 2024 site numbers (left out); Nordseecluster A's capacity (660 MW, from RWE project data); Inch Cape's capacity (1,080 MW, as commonly quoted).
- `eolico-filiera.json` says "Germany postponed its 2026 offshore auctions to 2027". The cited source (offshoreWIND.biz, 12 Aug 2026) only says the **N-10.1/N-10.2 retender** moved to 2027. The calendar uses the narrower claim.
- Installed capacity and targets are national figures (WindEurope). GB includes the Irish Sea, FR covers the Channel and Atlantic, and DE/DK mix North Sea and Baltic. AR7's Awel y Mor (775 MW, Irish Sea) is counted in the GB total.
- The Denmark 12.9 GW target comes from a secondary source (Port Esbjerg, undated). Lithuania, Latvia, Estonia, Finland and Sweden have no target in the file.
- The RSS feed covers only about three weeks (50 items). Candidates are keyword matches and include noise, such as vessel and survey contracts.
- Source dates given as a month or year are treated as the end of that period in the age checks (`needs_recheck` after 180 days).
