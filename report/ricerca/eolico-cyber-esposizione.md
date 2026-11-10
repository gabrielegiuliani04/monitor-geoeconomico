# Wind farms and a "supermarket-fridge" style cyberattack: fleet age, operation, systemic impact, rules

*Researcher 2, 10 November 2026. Defensive scope only: no exploit details, no lists of vulnerable systems, models-to-attack or addresses. Every figure has a source and a date. "Assessment" marks my own judgement, not a fact.*
*Chart data: `raccolta/cyber/flotta_eta.json`. Raw registers are cached in `raccolta/cyber/cache/` (git-ignored, about 310 MB); only aggregates are stored in the repository.*

## Key findings (in short)

1. **The European fleet is two fleets.** In Denmark, **49% of onshore capacity (2.3 GW, 3,335 turbines) dates from before 2010**. Germany has 18.9 GW (26%, 13,590 turbines) of that age, and **11.9 GW is already 20 or more years old**. In Poland, the Baltic states, Sweden and Finland, 65-80% of the fleet is from 2018 or later. Offshore is young everywhere: about 60% dates from 2018 or later.
2. **Old turbines look most like the fridge controllers.** Many come from brands that no longer exist (NEG Micon, Bonus, Micon, Nordtank, REpower/Senvion, Tacke, Fuhrländer). They run on old controllers, are often maintained by independent service firms, and use retrofitted modems. In Germany, about **7.5 GW onshore and 2.3 GW offshore** are from brands that are no longer active. *Assessment:* in most cases the security weakness is the remote-access link added later, not the 1990s turbine itself.
3. **Concentration sits in the control rooms, not in the parks.** Vestas has **161 GW under active service** (FY2025). Siemens Gamesa says it has **more than 10,000 turbines connected** to its Brande centre. One satellite network outage (KA-SAT, 2022) cut remote control of **5,800 Enercon turbines**. In Germany, Enercon alone accounts for **27.8 GW** onshore, and **96% of German wind capacity** is marked in the register as remotely controllable by its direct marketer.
4. **System scale.** At the 2025 peak, German wind produced **51.5 GW** (26-10-2025). If one large OEM fleet (around a third of German capacity) stopped at the same moment in high wind, the loss could be about **15-18 GW**. Even at average output it would be about **5 GW**. That is well above the **3 GW reference incident** that Continental Europe's reserves are sized for. In the Nordic area, the peak wind output of eastern Denmark alone (DK2, **1,567 MW**) is above the **1,450 MW dimensioning incident**. *Assessment:* such a stop needs a very deep compromise. Past incidents removed **monitoring**, not **generation**.
5. **2025-2026 changed the threat picture.** In Poland (29-12-2025), more than 30 wind and solar sites were hit by destructive malware, and in a follow-up a CHP plant was reached through a wind farm's network (disclosed 08-08-2026). In the UK, a small generator was offline for 4 days, with an Iran-linked group suspected (reported 22-08-2026). France attributed the fridge attacks to the IRGC (09-11-2026). **No successful cyberattack on a European offshore wind farm is known** as of 10-11-2026.
6. **The rules are mostly in force, but not yet enforced.**
   - **NIS2** is in force in DK (01-07-2025), DE (06-12-2025), PL (03-04-2026), NL (15-08-2026) and LT (2024).
   - **Cyber Resilience Act:** reporting duties since 11-09-2026, full application from 11-12-2027.
   - **Network Code on Cybersecurity:** in force, but the designation of high/critical-impact entities is still in progress.
   - **High-risk vendors:**
     - Lithuania: compliance deadline 01-05-2026, and grid operators can now disconnect plants that do not comply.
     - UK: blocked Mingyang's factory (03-2026).
     - Netherlands: the IJmuiden Ver Gamma-B draft permit (10-2026) requires EEA operational control, at least 75% of turbines not from China, and a digital bill of materials including firmware.
     - EU: Cybersecurity Act revision proposed (01-2026).

---

## 1. Fleet age

### 1.1 Method and sources

- **Periods:** before 2010 / 2010-2017 / 2018 and later, by grid-connection or commissioning date. MW = rated power of units **in operation** on the register date.
- **Registers (complete, every turbine):**
  - **Denmark.** Energistyrelsen, *Stamdataregister for vindkraftanlæg*, file "Vinddata 2026-09.xlsx" (data to end-September 2026, uploaded October 2026), [ens.dk data overview](https://ens.dk/analyser-og-statistik/data-oversigt-over-energisektoren). Downloaded on 10-11-2026: 7,179 rows, of which 7,018 active. It covers every turbine, including household ones, with grid date, kW, manufacturer, model and land/sea. **It has no owner-type field**, despite what the brief assumed.
  - **Germany.** Bundesnetzagentur, *Marktstammdatenregister*, full export of 10-11-2026 (EinheitenWind.xml, 44,367 records, of which 32,286 in operation), [download page](https://www.marktstammdatenregister.de/MaStR/Datendownload). Licence dl-de/by-2-0. Owner type (natural person or organisation) comes from the public unit list on the same portal.
  - **United Kingdom.** DESNZ *Renewable Energy Planning Database* Q2 2026 (sites of at least 150 kW, OGL v3), [gov.uk](https://www.gov.uk/government/publications/renewable-energy-planning-database-monthly-extract).
- **Other countries.** Global Energy Monitor, *Global Wind Power Tracker*, February 2026 version (CC BY 4.0). I used the public map file linked from [the tracker page](https://globalenergymonitor.org/projects/global-wind-power-tracker/). **Threshold: project phases of at least 10 MW.** Small and older turbines are missing, so the old share is **understated**. Coverage against WindEurope end-2025 onshore totals:

  | Country | GEM coverage |
  |---|---|
  | DK | 48% |
  | DE | 61% |
  | LT | 52% |
  | NL | 74% |
  | IT | 77% |
  | PL | 80% |
  | SE | 89% |
  | FI | 90% |
  | EE | 97% |
  | Europe | 81% |
- **Offshore.** EMODnet via `docs/data/offshore-nord.json`, covering the North Sea (GB east coast only) and the Baltic, 122 farms marked operational. Corrections:
  - I added years for 8 farms that had none.
  - Hornsea 2 is counted once: EMODnet lists it as three 1,386 MW phases.
  - EMODnet lags reality: it gives 7.7 GW for Germany against 11.7 GW in MaStR, and does not include Thor.
- **Totals for context.** WindEurope, *Wind energy in Europe – 2025 Statistics*, table 1 ([PDF copy](https://www.rinnovabili.it/wp-content/uploads/2026/02/WindEurope-European-Stats-2025.pdf), 02-2026): Europe has 304.0 GW (265.4 GW onshore, 38.6 GW offshore). Europe decommissioned 0.9 GW in 2025, and WindEurope expects about 16 GW to be decommissioned in 2026-2030.

### 1.2 Table by country and period (share of capacity with a known date)

| Country | Source | Onshore <2010 | Onshore 2010-17 | Onshore 2018+ | Onshore total | Offshore <2010 | Offshore 2010-17 | Offshore 2018+ | Offshore total |
|---|---|---|---|---|---|---|---|---|---|
| **Denmark** | ENS register 09-2026 | **48.6%** (2,326 MW; 3,335 turbines) | 35.1% (1,683; 562) | 16.4% (785; 226) | 4,793 MW (+22 MW micro) | 17.2% (636; 294) | 16.6% (615; 202) | 66.2% (2,445; 239, incl. Thor 2026) | 3,695 MW |
| **Germany** | MaStR 10-11-2026 | **26.4%** (18,931; 13,590) | 37.6% (26,984; 10,722) | 36.0% (25,845; 6,153) | 71,760 MW | 0.3% (35; 7) | 46.9% (5,488; 1,160) | 52.7% (6,166; 654) | 11,689 MW |
| **UK** | REPD Q2 2026 | 21.9% (3,390) | 56.2% (8,718) | 21.8% (3,374) | 15,508 MW | 5.9% (947) | 34.8% (5,568) | 59.3% (9,496) | 16,011 MW |
| Netherlands | GEM ≥10 MW | 10.1% (408) | 24.4% (984) | 65.6% (2,649) | 4,041 dated (+1,145 n/d) | 8.7% (595) | 17.5% (1,197) | 73.8% (5,044) | 6,836 |
| Poland | GEM | 8.6% (706) | 47.0% (3,878) | 44.4% (3,661) | 8,245 (+718 n/d) | – | – | – | 0 (Baltic Power in commissioning) |
| Lithuania | GEM | 6.4% (80) | 26.5% (333) | 67.2% (845) | 1,258 (+50) | – | – | – | 0 |
| Latvia | GEM | 20% (20) | 21% (21) | 59% (59) | 100 | – | – | – | 0 |
| Estonia | GEM | 11.3% (78) | 26.3% (181) | 62.4% (429) | 688 | – | – | – | 0 |
| Sweden | GEM | 2.6% (431) | 26.4% (4,295) | 71.0% (11,573) | 16,299 (+97) | 140 MW | 48 MW | – | 188 |
| Finland | GEM | 0.1% (12) | 20.4% (1,741) | 79.4% (6,764) | 8,517 | – | 42 MW | – | 42 (WindEurope: 71) |
| Italy | GEM | **37.6%** (3,091) | 40.2% (3,303) | 22.2% (1,822) | 8,216 (+2,195 n/d) | – | – | 30 MW (Taranto) | 30 |
| **Europe** | GEM | 25.1% (49.3 GW) | 37.1% (72.8 GW) | 37.8% (74.3 GW) | 196.5 GW dated (+18.3 n/d) | 6.2% (2.4 GW) | 34.7% (13.6 GW) | 59.1% (23.2 GW) | 39.2 GW |

How to read the table:
- **The GEM numbers understate the old fleet.** Germany shows this clearly. GEM puts 11.5 GW onshore before 2010. The register puts it at 18.9 GW: small parks of 1-5 turbines from the 1990s and 2000s are missing from GEM. Assuming the 50 GW missing from GEM for Europe (WindEurope total minus GEM) is mostly older and smaller, Europe's pre-2010 onshore share is probably **around 30% (60-70 GW)**, not 25%. This is a rough estimate, not a measurement.
- **Age past 20 years** (commissioned in or before 2005):
  - Germany: 11.9 GW onshore (9,861 turbines; 2.5 GW of it from 2000 or earlier).
  - Denmark: 2.14 GW onshore (45% of onshore) and 0.40 GW offshore (Horns Rev 1, Nysted, Middelgrunden, Samsø and others).
- **Size in Denmark:** 2,953 onshore turbines (72% of the onshore count, 1.7 GW) are smaller than 1 MW.

### 1.3 Offshore by commissioning period (EMODnet, North Sea and Baltic, operational farms)

| Country | <2010 | 2010-2017 | 2018+ |
|---|---|---|---|
| GB (east coast) | 3 farms, 265 MW | 11 farms, 2,938 MW | 15 farms, 9,109 MW |
| DE | 3 farms, 37 MW | 18 farms, 4,997 MW | 9 farms, 2,681 MW |
| NL | 4 farms, 595 MW | 6 farms, 1,146 MW | 12 farms, 5,479 MW |
| DK | 8 farms, 641 MW | 3 farms, 617 MW | 4 farms, 1,191 MW (Thor missing) |
| BE | – | 2 farms, 195 MW | 5 farms, 1,385 MW |
| SE | 2 farms, 110 MW | 1 farm, 48 MW | – |
| FI | – | 4 farms, 113 MW | – |
| **Total** | **20 farms, 1.6 GW (544 turbines)** | **45 farms, 10.1 GW (2,394)** | **45 farms, 19.8 GW (2,402)** |

**Offshore "old" means about 1.6 GW in 20 small parks.** The large capacity concentrations (Hornsea, Borssele, Hollandse Kust, Gode Wind and others) were built from 2015 onward. Their control and communication systems were designed for the IEC 62443 era, and most are owned by large operators that fall under NIS2.

### 1.4 Who made the old turbines (registers)

| | Main brands before 2010 (onshore) |
|---|---|
| Denmark | NEG Micon 779 MW (997 turbines), Vestas 713 MW (1,082), Bonus 305 MW (423), Micon 130 MW, Nordex 117 MW, Siemens 107 MW, Nordtank 80 MW, Wind World 44 MW |
| Germany | Enercon 7.8 GW (5,512), Vestas 4.2 GW (2,518), NEG Micon 1.0 GW, GE 0.9 GW, Nordex 0.8 GW, REpower 0.7 GW, Siemens 0.5 GW, Senvion 0.4 GW |

Other register facts:
- **Germany, brands no longer active** (Senvion, REpower, NEG Micon, Tacke, Fuhrländer, DeWind, BARD, Adwen, Südwind, AN, Enron): 3.8 GW onshore before 2010, 3.4 GW in 2010-17 and 0.3 GW from 2018. Offshore: 2.1 GW in 2010-17 (Adwen, BARD, Senvion) and 0.2 GW from 2018.
- **Chinese OEMs:**
  - Germany: 155 Vensys turbines (Goldwind-controlled), 393 MW, out of 83.4 GW.
  - Denmark: none in the register.
  - Europe 2025: Chinese makers installed 446 MW (GWEC, via `cyber-energia.json`).

Assessment: the "fridge" pattern has three parts: a device made in series, no longer supported, and reachable remotely. In wind, it fits best the **small, old, single-owner onshore turbines**, especially in DK, DE and IT, and the **products of vanished brands**, whose controllers no OEM updates any more. It fits large modern offshore farms least.

---

## 2. Ownership and operation

### 2.1 Small, cooperative and farmer owners

| | Figure | Source and date |
|---|---|---|
| DE, natural persons as registered operators (onshore, in operation) | 2,120 turbines (6.9% of the count), 1.03 GW (**1.4% of capacity**). Before 2010: 1,137 turbines, 0.72 GW (3.8% of that vintage) | MaStR 10-11-2026, own calculation |
| DE, "Bürgerenergie" flag (EEG definition, only for newer units) | 105 turbines, 445 MW since 2018 (1.7% of that vintage) | MaStR 10-11-2026 |
| DE, private individuals and farmers as owners (economic ownership, including GmbH & Co. KG citizen parks) | **40.6% of onshore wind capacity (2019)**, falling. Only a quarter of new build in 2019 | trend:research for AEE, via [Solarserver 21-12-2020](https://www.solarserver.de/2020/12/21/studie-zeigt-buergerenergie-verliert-marktanteile/) (no newer survey found) |
| DE, number of registered operators of units in operation | 10,695 | MaStR 10-11-2026 |
| DK, cooperatives | Historically dominant. Reports say up to about 150,000 households held shares at the peak and about 50,000 do today; Middelgrunden has about 8,700 co-owners. Figures vary between sources (medium-low reliability) | [Australia Institute](https://australiainstitute.org.au/report/community-owned-wind-lessons-from-denmark/); [AAU, "The past, present and uncertain future of community energy in Denmark"](https://vbn.aau.dk/ws/files/316721850/The_past_present_and_uncertain_future_of_community_energy_in_Denmark.pdf) |

The Danish register has no owner type, so the cooperative share of today's 4.8 GW onshore cannot be measured with public data. Assessment: the 3,335 turbines from before 2010, averaging 0.7 MW, are mostly owned by farmers, cooperatives and small companies.

**Why ownership matters for cyber** (assessment):
- **NIS2 applies to medium and large companies.** A single turbine held in a small company or by a farmer is usually **outside NIS2**, unless it is designated, or unless its service company or aggregator is in scope (for example as a managed service provider). So the protection of these turbines depends on **contracts with the OEM, the independent service provider (ISP) or the park manager**, not on the owner.
- **They are many but small.** One owner cannot cause a system problem. A **shared service provider** looking after thousands of such turbines can.

### 2.2 OEM service vs independent service providers (ISPs); remote control centres

| Actor | Public statement | Source |
|---|---|---|
| Vestas | **161 GW under active service, more than 56,000 turbines** (end-2025); homepage shows 164 GW "under service". Non-Vestas fleet under service: 7.8 GW (30-06-2025). Remote Operations Centres in the USA, Spain, Germany, India and the Philippines, plus an offshore centre in Esbjerg | Vestas AR 2025 (05-02-2026) as reported by [GreentechLead](https://greentechlead.com/wind/vestas-reports-record-2025-revenue-of-eur-18-8-billion-sets-stronger-2026-outlook-52164); [Vestas track record](https://www.vestas.com/content/dam/vestas-com/global/en/brochures/Track%20Record-onepage.pdf.coredownload.inline.pdf); [ROC brochure 2020](https://vestas.com/content/dam/vestas-com/global/en/brochures/ROC_202008.pdf.coredownload.inline.pdf) |
| Siemens Gamesa | **More than 10,000 remotely connected turbines** monitored by about 130 experts at the Brande Remote Diagnostic Center (DK). In 2014 the company said the centre covered "about 30 GW" and that 85% of alarms were solved remotely | [Siemens Gamesa, offshore service logistics](https://www.siemensgamesa.com/explore/innovations/offshore-service-logistics-part-1); [Windtech 2014](https://www.windtech-international.com/company-news/siemens-opens-new-remote-diagnostics-center-for-wind-turbines-in-denmark) |
| Enercon | KA-SAT, 24-02-2022: remote monitoring and control lost for **about 5,800 turbines (about 11 GW)** in central Europe. The turbines ran on in automatic mode. Over 95% were reconnected by 19-04-2022, and Enercon then offered LTE retrofits | [Power Technology](https://www.power-technology.com/news/enercon-turbine-disruption); [Modern Power Systems](https://modernpowersystems.com/features/featureenercon-turbines-disrupted-by-satellite-cyber-attack-9935239/) |
| Enercon fleet in DE today | **12,356 turbines, 27.8 GW onshore** (39% of German onshore capacity). The 5,800 turbines of 2022 equal **almost half of today's German Enercon fleet by count** | MaStR, own calculation |
| Ørsted | Global 24/7 Control and Monitoring Centre at Barrow-in-Furness, also to serve US and APAC projects. East Coast hub in Grimsby | [Ørsted vacancy](https://orsted.com/en/careers/vacancies-list/2026/09/32670-asset-surveillance-lead); [offshoreWIND.biz 2019](https://offshorewind.biz/2019/09/27/orsted-unveils-uk-east-coast-om-hub) |
| Deutsche Windtechnik (ISP) | Remote monitoring of about 2,000 turbines switched off for about 1 day after the April 2022 attack | `cyber-energia.json` ([The Record](https://therecord.media/german-wind-farm-operator-confirms-cybersecurity-incident-after-ransomware-group)) |
| ISP market share | **No reliable public figure found.** Market-research summaries only say the ISP share is growing after warranties end (low reliability) | e.g. [Windpower Engineering](https://www.windpowerengineering.com/oems-forecast-secure-50-growing-wind-om-market/) |

**German fleet by OEM group** (MaStR, in operation):

| OEM group | Onshore | Offshore |
|---|---|---|
| Enercon | 27.8 GW | – |
| Vestas | 18.3 GW | 2.7 GW |
| Nordex/Acciona | 10.6 GW | – |
| Senvion/REpower | 4.5 GW | 0.9 GW |
| GE | 3.9 GW | 0.4 GW |
| Siemens Gamesa | 2.0 GW | 7.2 GW |

**Remote control by third parties (Germany):**
- **96.3% of German wind capacity** (onshore and offshore) is marked in MaStR as **remotely controllable by its direct marketer** (FernsteuerbarkeitDv). The direct marketer is the aggregator that sells the power and can curtail it.
- So besides the OEM and ISP control rooms, there is a **third channel of commands**: the trading platforms. *Assessment:* this is the closest equivalent to the "vendor cloud" of the fridge controllers. The Dutch RDI has already flagged aggregator platforms as a system risk (`cyber-energia.json`).

### 2.3 Links: satellite, 4G/LTE, private APN

- **Satellite:** the KA-SAT case showed that many remote parks depended on a single satellite network, without a backup link (sources above).
- **Private cellular networks:** CERT Polska describes, at a conceptual level, how in December 2025 an attacker moved from wind farm substations through a **private cellular network (APN) run by the grid operator** to a CHP plant. It recommends isolating devices from each other on such networks and treating them as untrusted. Report and follow-up (08-08-2026): [CERT Polska](https://cert.pl/en/posts/2026/01/incident-report-energy-sector-2025/); follow-up via [The Hacker News](https://thehackernews.com/2026/08/hackers-breach-polish-power-plant.html), secondary source and not read in full (host blocked here).
- **Quantity:** I found no public statistic on what share of the European fleet uses satellite, 4G or fibre. **Data missing.**

---

## 3. Systemic impact

### 3.1 How much power comes from wind (own calculations from public data, year 2025)

| | Wind / demand | Peak | Notes | Source |
|---|---|---|---|---|
| **Denmark** | 19.1 TWh / 40.5 TWh gross consumption = **47%** (WindEurope: 50% of demand; Energinet: about 60% of domestic production) | max hour **6,485 MW** (24-01-2025 16:00 UTC), against 6,449 MW consumption | Wind above consumption in **588 hours**; max ratio **149%** (11-10-2025 03:00 UTC). DK1 max 4,946 MW, **DK2 max 1,567 MW** | [Energi Data Service, ProductionConsumptionSettlement](https://www.energidataservice.dk/tso-electricity/ProductionConsumptionSettlement) (Energinet), downloaded 10-11-2026 |
| **Germany** | 131.2 TWh / 465.8 TWh load = **28%** | max quarter-hour **51.5 GW** (26-10-2025 16:30 UTC), with load at 57.4 GW; offshore max 8.3 GW | Wind above load in 12 quarter-hours; wind at least 60% of load in 8.3% of quarter-hours; average wind output about 15 GW | [Fraunhofer ISE Energy-Charts API](https://api.energy-charts.info/) (public net generation) |
| **Netherlands** | Ember: wind 25% of electricity; WindEurope: 29% of demand | Energy-Charts gives max 6.9 GW and offshore max 4.5 GW, but its wind series looks incomplete (19% share), so it is not used for the share | | [Ember NL](https://ember-energy.org/countries-and-regions/the-netherlands/); WindEurope 2025 |

### 3.2 Reserves: what a simultaneous loss of X GW means

| Synchronous area | Sized for | Source |
|---|---|---|
| Continental Europe (incl. DE, NL, PL, DK1, IT, Baltics since 02-2025) | **Reference incident 3,000 MW** in each direction (FCR). Deeper frequency falls trigger automatic load shedding | SO GL art. 153; [ENTSO-E explanatory note on FCR dimensioning](https://consultations.entsoe.eu/system-operations/synchronous-area-operational-agreement-policy-1-lo/supporting_documents/Article_A1_Explanatory_Note_for_FCR%20Dimensioning.pdf) |
| Nordic (SE, FI, NO, DK2) | Largest single loss: **Oskarshamn 3, max 1,450 MW**. FCR-D up 1,450 MW, down 1,400 MW (Olkiluoto 3 is limited to a net 1,300 MW by a protection scheme) | [Fingrid, minimum inertia 2025](https://www.fingrid.fi/globalassets/dokumentit/fi/tiedotteet/2025---requirements-for-minimum-inertia-in-the-nordic-power-system.pdf); [Fingrid reserves](https://www.fingrid.fi/en/electricity-market/reserves/power-system-reserves/); [Nordic FCR dimensioning, 2023](https://www.fingrid.fi/globalassets/dokumentit/en/news/electricity-market/2023/153---explanatory-document-for-nordic-fcr-dimensioning-proposal.pdf) |
| Great Britain | Normal infeed loss 1,320 MW; infrequent 1,800 MW. Real case: 14-03-2025, about 1,877 MW lost at Drax | [NESO grid-forming presentation (ESIG)](https://www.esig.energy/attachment/serve/session-5b-gb-grid-forming-deployments-experience-xiaoyao-zhou-1); academic summary [arXiv 2005.04053](https://arxiv.org/pdf/2005.04053) |

**Order-of-magnitude scenarios** (assessment, simplified: same capacity factor for every fleet, no ramp-down time, no response from interconnectors):

| Scenario | Lost generation | Against reserves |
|---|---|---|
| A. Remote monitoring lost (KA-SAT, Poland 2025, Deutsche Windtechnik 2022) | **≈ 0 GW at once**: the turbines keep producing | The risk is indirect: the TSO cannot curtail or restart remotely. That is critical in the 588 Danish hours with wind above consumption, and during storms or blackout restoration |
| B. All turbines of **one German ISP** with about 2,000 turbines stop (≈ 4-5 GW installed) | ≈ 0.9 GW at average output; ≈ 3 GW at the 2025 peak | Average case within the 3 GW; the peak case reaches it |
| C. **Enercon's German onshore fleet** (27.8 GW) stops in high wind | ≈ 5 GW at average output (≈ 19% load factor); **≈ 15-18 GW** at the 26-10-2025 peak | **about 1.7-6 times the CE reference incident** |
| D. A malicious stop of **all DK2 wind** at peak | ≈ 1.57 GW | Above the Nordic 1,450 MW dimensioning incident |
| E. Largest single offshore cluster (Hornsea 1+2, about 2.5 GW, GB) trips | up to about 2.5 GW | Above the GB 1,800 MW infrequent-loss limit. Non-cyber precedent: 09-08-2019, Hornsea 1 lost about 737 MW together with Little Barford, and about 1.1 million customers were disconnected (Ofgem report, 01-2020) |

**Caveats for C-E** (assessment):
- **Turbines do not stop instantly.** Blade pitching takes seconds to minutes. Even so, a loss of several GW in less than about 15 minutes would use up FCR and aFRR.
- **One command would probably not reach all turbines at once.** Control centres usually work park by park, and turbines have local safety systems. I found no public evidence that one OEM command could stop a whole national fleet. Precisely for this reason, the realistic and worrying case is a **coordinated attack on many SCADA systems at once** (Poland-style), not a single click.
- **Settings errors matter as well.** A mass disconnection can also come from misconfigured frequency or voltage protection, as the German "50.2 Hz" PV retrofit showed. *Assessment:* manipulating settings is closer to the "fridge parameter" model than a stop command.

---

## 4. Regulation and status, 2025-2026

### 4.1 NIS2 (Directive 2022/2555; transposition deadline 17-10-2024)

| Country | Act | In force | Source |
|---|---|---|---|
| DK | NIS 2 Act, Act no. 434 of 06-05-2025 | **01-07-2025** | [ECSO tracker](https://ecs-org.eu/nis2-tracker/); [nis2scoring](https://www.nis2scoring.eu/en/nis2-transposition-status/) |
| NL | Cyberbeveiligingswet (Stb. 2026, 187; entry-into-force decree Stb. 2026, 189) and Wwke (CER) | **15-08-2026** | [Rijksoverheid 15-08-2026](https://www.rijksoverheid.nl/actueel/nieuws/2026/08/15/cyberbeveiligingswet-en-wet-weerbaarheid-kritieke-entiteiten-vanaf-vandaag-van-kracht); [NJB](https://www.njb.nl/wetgeving/staatsbladen/cyberbeveiligingswet/) |
| DE | NIS2UmsuCG (amends BSIG and EnWG) | **06-12-2025** (most trackers; one gives a different date, to be checked in the BGBl) | [ECSO tracker](https://ecs-org.eu/nis2-tracker/); [directive-nis2.eu](https://directive-nis2.eu/transposition) |
| PL | Amendment to the KSC Act of 23-01-2026 (Dz.U. 2026 poz. 252) | **03-04-2026** (one tracker: 02-04-2026) | as above |
| LT | Amended Law on Cyber Security | **18-10-2024**; further amended in 2026 (law XV-1076, not verified) | as above |

### 4.2 Other EU rules

| Rule | Status | Source |
|---|---|---|
| **Network Code on Cybersecurity** (Delegated Reg. 2024/1366) | In force since 13-06-2024. Methodology proposals were due 13-03-2025. An EU-wide risk assessment is due 9 months after methodologies are approved. National authorities designate high- and critical-impact entities using the ECII index (provisional in 2025). Regional reports are due 30 months and cross-border reports 40 months after notification. Spain approved its methodologies (pv magazine, 05-11-2026). I found **no final EU list** of designated entities | [Industrial Cyber](https://industrialcyber.co/news/eu-releases-network-code-on-cybersecurity-for-electricity-sector-to-boost-resilience-cross-border-protection); [EU DSO Entity, provisional standards 06-2025](https://eudsoentity.eu/wp-content/uploads/2025/06/Provisional-list-of-standards.pdf); [pv magazine 05-11-2026](https://www.pv-magazine.com/2026/11/05/spain-approves-methodologies-to-strengthen-electricity-system-cybersecurity/) |
| **Cyber Resilience Act** (Reg. 2024/2847) | In force since 10-12-2024. Reporting of actively exploited vulnerabilities from **11-09-2026**; full application from **11-12-2027**. Covers controllers, gateways and inverters sold as products | `cyber-energia.json` (EUR-Lex) |
| **Radio Equipment Directive**, delegated act 2022/30 | Cybersecurity requirements for wireless equipment mandatory since **01-08-2025** | `cyber-energia.json` |
| **NZIA**, Implementing Reg. 2025/1176 (non-price criteria in renewable auctions) | Already used in Dutch offshore permits: cybersecurity measures for the operator and its ICT suppliers, and operational control from the EEA (see 4.3) | [RVO, draft permit IJmuiden Ver Gamma-B, 10-2026](https://www.rvo.nl/sites/default/files/2026-10/Concept-voorschriften-vergunning-IJmuiden-Ver-_kavel-Gamma-B_versie-oktober-2026.pdf) |
| **Cybersecurity Act revision ("CSA2")** | Proposed in **01-2026**. It would set up an EU process to name high-risk suppliers, restrict their components in key ICT assets, and phase them out within at most 36 months for telecoms. A Parliament draft would assess individual companies rather than countries (09-2026). WindEurope asks for a phase-out period of at least 36 months, because wind assets last 20-30 years | [Euronews 20-01-2026](https://www.euronews.com/2026/01/20/brussels-pushes-for-stronger-cybersecurity-oversight-of-high-risk-technology-suppliers); [pv magazine 28-09-2026](https://www.pv-magazine.com/2026/09/28/eu-inverter-restrictions-could-shift-from-countries-to-individual-high-risk-suppliers/); [WindEurope response](https://windeurope.org/data/products/windeurope-response-to-the-public-consultation-on-the-revision-of-the-cybersecurity-act-and-nis2-amendments/) |
| **EU funding** | Since 04-2026, no EU funds for projects using inverters from high-risk suppliers. For projects outside the EU and not connected to the EU grid, phase-out by 15-04-2027 | [pv magazine 23-04-2026](https://www.pv-magazine.com/2026/04/23/eu-moves-to-restrict-funding-for-projects-using-inverters-from-high-risk-suppliers/); [Euronews 04-05-2026](https://euronews.com/2026/05/04/eu-moves-to-ban-high-risk-inverters-from-china-over-cybersecurity-threats) |

### 4.3 National measures on high-risk vendors

| Country | Measure | Date | Source |
|---|---|---|---|
| **Lithuania** | Ban on remote access from high-risk countries to solar, wind and storage above 100 kW. The equipment itself is not banned. New plants covered from 01-05-2025; existing ones had to comply by **01-05-2026**. Grid operators can now disconnect non-compliant plants, which then need an audit | law 11/12-11-2024; disconnection power reported 05-06-2026 | [LRT 12-11-2024](https://www.lrt.lt/en/news-in-english/19/2411602/lithuania-passes-law-to-block-chinese-access-tosolar-and-wind-farm-systems); [pv magazine 05-06-2026](https://www.pv-magazine.com/2026/06/05/lithuanias-grid-operators-can-now-disconnect-solar-plants-without-cybersecurity-measures/) |
| **Germany** | Waterkant (about 270-300 MW, Luxcara) chose Mingyang (07-2024). The federal government said it would examine the deal; a defence ministry analysis warned of risks (2025). Luxcara then reserved 19 Siemens Gamesa turbines, saying the reason was operational and better security was "a side effect". **No German law** excludes Chinese turbines | 2024-2025 | [OE Digital](https://www.oedigital.com/news/514969-germany-to-examine-security-impact-of-chinese-wind-turbine-deal); [Offshore Magazine](https://www.offshore-mag.com/special-reports/news/55293138/luxcara-germany-could-halt-offshore-wind-project-over-chinese-wind-turbine-concerns); [MarketScreener/Reuters](https://www.marketscreener.com/news/germany-s-luxcara-may-drop-chinese-turbine-deal-for-north-sea-wind-farm-ce7c50d8d88df023) (exact date of the switch not verified) |
| **Netherlands** | IJmuiden Ver Gamma-B draft permit (10-2026). Rule 21: an EEA-based operator keeps operational control, and the operator documents cybersecurity measures for itself and its ICT suppliers (Reg. 2025/1176). Rule 22: at least 75% of turbines not from China, with no more than four of nine main components from China; magnets no more than 85% from one third country; drive trains and generators not from China; a **digital bill of materials including software and firmware** with origin | 10-2026 (draft; Gamma-A window 26-11 to 10-12-2026) | [RVO PDF](https://www.rvo.nl/sites/default/files/2026-10/Concept-voorschriften-vergunning-IJmuiden-Ver-_kavel-Gamma-B_versie-oktober-2026.pdf), read 10-11-2026 |
| **United Kingdom** | Mingyang's Ardersier factory blocked on national security grounds; Downing Street not reconsidering (08-2026) | about 25-03-2026 | [Scottish Financial Review 25-03-2026](https://scottishfinancialreview.com/2026/03/25/uk-govt-blocks-chinese-plan-for-1500-scots-jobs/); [energy-pedia](https://www.energy-pedia.com/news/united-kingdom/swinney-urges-burnham-to-rethink-%C2%A31-5bn-wind-factory-ban-204932) |
| Norway | Mingyang excluded from a 1.5 GW tender, without public reasons | 2025 | [bne IntelliNews](https://bne.eu/adoption-of-chinese-wind-technology-sparks-security-fears-in-europe-370086) |
| **Denmark** | **No specific public measure found** on Chinese turbines. The register lists no Chinese turbines in operation. National threat level for destructive attacks is MEDIUM (FE-DDIS/SektorCERT, in `cyber-energia.json`) | – | gap |
| Poland | Public warnings on Chinese access (cited by a TNO-based report); no law found | – | [OIES 10-2025](https://www.oxfordenergy.org/wpcms/wp-content/uploads/2025/10/CE17-Chinese-participation-in-Europes-offshore-wind-sector.pdf) |

### 4.4 Insurers

- **Lloyd's cyber war clauses:** the LMA 5564-5567 clauses exclude state-backed cyber operations; LMA 5567 is the broadest of them. Attribution is decisive: without a state attribution, the insurer must prove it. A new edition of the clauses was published on 19-03-2026. Sources: [LMA clauses](https://lmalloyds.com/wp-content/uploads/2025/06/Cyber-Clauses-19-March-2026.pdf); [Marsh](https://www.marsh.com/uk/services/cyber-risk/insights/new-cyber-war-exclusion-language-raises-concerns.html).
- *Assessment:* France's attribution of the fridge attacks to the IRGC (09-11-2026) is exactly the case where these clauses can **exclude cover**.
- **Wind-specific OT cyber requirements from insurers:** **I found no public standard.** The Joint Renewable Energy Underwriting Committee (02-2026) is working on turbine damage wordings, not cyber. **Gap**: to be checked with brokers (Marsh, Aon, GCube).

---

## 5. Incidents and near misses in wind and solar, 2015-2026, not already in `cyber-energia.json`

| Date | Case | Effect | Attribution | Source |
|---|---|---|---|---|
| 05-03-2019 | **sPower (USA)**: denial of service on vendor firewalls, repeated reboots for about 12 hours | Loss of visibility over about a dozen wind and solar sites (about 500 MW); no generation lost | not attributed | [Utility Dive](https://www.utilitydive.com/news/first-cyber-attack-on-solar-wind-assets-revealed-widespread-grid-weaknesse/566505/) (NERC lesson learned, 09-2019) |
| 05-2024 | **Japan, about 800 solar monitoring devices** hijacked and used for bank fraud | No effect on the grid; a patch had been available since 12-2023 | criminal | [CSO Online](https://www.csoonline.com/article/2119281/hijack-of-monitoring-devices-highlights-cyber-threat-to-solar-power-infrastructure.html) |
| 09-2024 | Pro-Russian group "Just Evil" claims access to the solar monitoring platform of a Lithuanian utility | claim judged credible by Cyble | pro-Russian hacktivists | [Cyble](https://cyble.com/blog/solar-monitoring-solutions-in-hacktivists-crosshairs/) |
| 06-09/2025 | "TwoNet" claims access to solar control panels in DE (3, then 4), IT and CZ. Forescout notes that exposure does not prove compromise | claims; effect unknown | pro-Russian hacktivists | [Forescout](https://www.forescout.com/blog/anatomy-of-a-hacktivist-attack-russian-aligned-group-targets-otics/) |
| 30-01-2026 (report on 29-12-2025) | **Poland, attribution details**: entry through exposed VPN and firewall access and default passwords on field devices. CERT Polska points to a cluster it links to the **FSB (Centre 16 / Berserk Bear)**; ESET and Dragos point to **Sandworm (GRU)** | (main incident already in JSON) | Russian state, contested between agencies | [TechCrunch 30-01-2026](https://techcrunch.com/2026/01/30/russian-hackers-breached-polish-power-grid-thanks-to-bad-security-report-says/); [Help Net Security 06-02-2026](https://www.helpnetsecurity.com/2026/02/06/poland-cyberattacks-energy-sector-industrial-organizations/); [SecurityWeek](https://www.securityweek.com/default-ics-credentials-exploited-in-destructive-attack-on-polish-energy-facilities/) |
| 08-08-2026 (incident 12-2025) | **Poland, follow-up**: a CHP plant serving about 50,000 residents was reached **from wind farm substations through the grid operator's private APN**; a steam turbine was shut down. Accounts disagree on whether customers lost heat or power | first known case where **wind farm networks served as the way in** to another plant | as above | via [The Hacker News](https://thehackernews.com/2026/08/hackers-breach-polish-power-plant.html) (not read in full; host blocked) |
| 07-04-2026 (updated 22-07-2026) | CISA advisory AA26-097A: Iranian-affiliated actors exploiting PLCs in US critical infrastructure, including energy | advisory | Iran | cited by [GMU ISEAI](https://iseai.gmu.edu/iran-linked-hackers-blamed-for-cyberattack-that-shut-down-uk-power-plant/) |
| 07-2026 (reported 22-08-2026) | **UK, small generator offline for 4 days**; one outlet says about 15 MW of gas peaking capacity (not confirmed). Government: "no threat to the wider grid" | first suspected Iran-linked case of shutting down UK generation | suspected Iran/IRGC; **no formal attribution** | [Irish Times 23-08-2026](https://www.irishtimes.com/world/uk/2026/08/23/iran-linked-hackers-accused-of-cyberattack-that-shut-down-british-power-plant/); [Help Net Security 24-08-2026](https://www.helpnetsecurity.com/2026/08/24/uk-power-plant-cyberattack/) (original: The Telegraph) |

As of 10-11-2026 I found **no confirmed case** of an Iranian group attacking wind turbines or inverters in Europe. The Iranian pattern so far is different: it chooses a **brand of exposed controller**, as with the CyberAv3ngers (2023), the US water sector (2026) and the fridges (2026). *Assessment:* if that model reaches wind, the first targets would be **small, old, internet-exposed parks**, not offshore farms.

---

## 6. What this means: old vs new turbines (assessment)

| | Old turbines (<2010, mostly onshore, small owners) | New turbines (2018+, large parks, offshore) |
|---|---|---|
| Likelihood of a "fridge"-type attack | **Higher**: devices made in series, end-of-life controllers, remote links added later, owners outside NIS2, vanished OEMs | **Lower**: designed under IEC 62443, NIS2 operators, monitored SOCs |
| Impact per site | Very small (0.1-5 MW) | Large (0.3-1.4 GW per farm) |
| System impact | Only if thousands are hit together through a **shared service provider, aggregator or platform** | Through a **concentrated OEM control centre**, or a targeted attack on substations and HVDC |
| Lessons from real cases | Poland 2025: default passwords on field devices, exposed VPN access | KA-SAT 2022, Nordex and Vestas: dependence on the vendor's IT and communications |
| Natural mitigation | The **repowering** wave: 16 GW to be decommissioned in 2026-2030 (WindEurope) | NL procurement rules (EEA control, digital bill of materials), CSA2, CRA |

## Limits and gaps

- **Ownership:** the Danish register has no owner type, and the German "natural person" field heavily understates citizen ownership. The latest economic-ownership survey for Germany is from 2019.
- **ISP share and links:** I found no public data on the ISP share of O&M, or on the share of turbines connected by satellite or 4G.
- **GEM threshold:** the 10 MW threshold understates old fleets (NL, PL, IT, SE). NL and IT have 1.1-2.2 GW without a year.
- **EMODnet** lags reality; use MaStR and ENS for Germany and Denmark.
- **Sources read only in secondary form:** WebFetch was blocked for thehackernews.com, envirotecmagazine.com and renewable-energy-industry.com. The Polish 08-2026 follow-up and the UK 07-2026 case rest on secondary reports.
- **Dates to verify** in official gazettes: German NIS2UmsuCG (06-12-2025), Polish KSC (03-04-2026), the 2026 Lithuanian amendment, and the date Luxcara switched to Siemens Gamesa.
- **Scenarios C-E** are orders of magnitude, not network studies.
