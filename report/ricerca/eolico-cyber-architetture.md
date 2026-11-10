# Wind turbine control architectures and the "refrigerator-type" attack pattern: research notes

*Researcher 1 notes for the report "Could a cyberattack like the supermarket-refrigeration attack hit wind farms? Old vs new turbines". Written 10 November 2026. These are working notes, not the report.*

**Scope and safety line.** This is defensive, public-source analysis at architecture level. It contains no exploit details, no vulnerability identifiers, no credentials, no device addresses, no search queries for exposed systems and no attack sequences. Where a public source names a specific flaw or product weakness, these notes record only the class of weakness.

**Conventions** (following `report/STANDARD.md`):
- **Fact**: something a source reports, with the source and the date of the source or the event.
- *Assessment:* reasoning by the researcher. Marked in italics.
- **Reliability** of non-primary sources: high, medium or low.
- **Gap**: something not found or not verified.

**Access limits during this research.** Web search worked. Direct page fetches were blocked for several hosts (bleepingcomputer.com, labs.cloudsecurityalliance.org). Many claims below therefore rest on search-engine summaries of the cited pages, not on the full text. Where that matters, the entry says so. Full-text checks of the primary PDFs (CERT Polska, INL, DOE, DNV) remain to be done (see section 7).

---

## 0. Context carried over from the CYBER-ENERGIA agent (9 November 2026)

Source: `report/agenti/cyber-energia.md` and `docs/data/cyber-energia.json`, both dated 9 November 2026. They are the starting point for these notes and are not repeated in full here.

- **Refrigeration attack, wave 1.** On the night of 11–12 October 2026, attackers remotely changed set-points (temperature, defrost) on connected refrigeration controllers in French supermarkets. Store estimates range from 250–350 (early trade reports) to more than 1,000 (Al Jazeera, 9 November 2026). See section 2 for the sources.
- **Wave 2.** On 1–2 November 2026 more than 115 stores were hit in Belgium, the Netherlands, Luxembourg, Sweden, Ireland and Estonia ([SecurityWeek, 3 Nov 2026](https://securityweek.com/over-100-european-stores-hit-as-supermarket-fridge-attacks-resume)).
- **Attribution.** On 9 November 2026 France attributed the October attack to Iran's Islamic Revolutionary Guard Corps (IRGC) (Reuters via [Al-Monitor](https://www.al-monitor.com/originals/2026/11/french-officials-blame-iran-refrigerator-hacks-vow-retaliation), AP, BBC, Al Jazeera, all 9 Nov 2026, as recorded by the agent).
  - **Gap:** my own web search on 10 November did not surface the French attribution statement. It surfaced only earlier French attributions to Russia (APT28, FSB) and an Israeli vendor's IRGC-linked attribution for attacks in Israel. The attribution is therefore carried over from the agent's sources and was not re-verified here.
  - Any link between the IRGC and the November wave is unproven.
- **Energy precedents.** The agent's table covers KA-SAT/Enercon (24 Feb 2022), Vestas (19 Nov 2021), Nordex (31 Mar 2022), Deutsche Windtechnik (11–12 Apr 2022), the Danish energy firms (May 2023), Deye (Nov 2024), the Reuters report on undocumented radios in Chinese inverters (14 May 2025) and Poland (29 Dec 2025). Sections 1 and 2 add architecture-level detail to these.

---

## 1. Turbine generations and their control and communications architecture

### 1.0 Common reference architecture (all generations)

A wind plant has the same functional layers in every generation. What changes is how each layer is built and connected.

1. **Turbine controller.** A PLC or embedded computer in the nacelle and tower base runs yaw, pitch, the converter interface, start/stop and alarms.
2. **Protection or safety system.** Overspeed, vibration, emergency stop and the "safety chain" bring the rotor to a safe state.
   - DNV's standard **DNV-ST-0438** "Control and protection systems for wind turbines" (Ed. 2016-04, amended 2021-11) sets "minimum requirements" for both systems and is the design basis for DNV certification ([DNV](https://www.dnv.com/energy/standards-guidelines/dnv-st-0438-control-and-protection-systems-for-wind-turbines/)).
   - **Gap:** I could not retrieve the clause text on how far the protection system must be independent of the control system. That independence is the basis of the "safety systems limit damage" argument (section 2.3) and must be checked in DNV-ST-0438 or IEC 61400-1.
3. **Park network and SCADA.** A park server collects data from all turbines, sends commands and runs the **park/power plant controller (PPC)**, which meets grid-operator set-points (active and reactive power, curtailment).
4. **Grid connection and substation.** Protection relays, RTUs (remote terminal units) and the link to the TSO or DSO control centre (Transmission or Distribution System Operator).
5. **Remote access and service.** OEM (Original Equipment Manufacturer) or independent service provider (ISP) remote centres, owner control rooms, direct-marketer or aggregator links, and condition-monitoring (CMS) data feeds.
6. **WAN links.** Leased lines, DSL, cellular routers, satellite, or fibre with the export cable offshore.

**Academic baseline: University of Tulsa, 2017.**
- Staggs, Ferlemann and Shenoi, "Wind farm security: attack surface, targets, scenarios and mitigation", *International Journal of Critical Infrastructure Protection* 17 (2017) 3–14, DOI 10.1016/j.ijcip.2017.03.001 ([IDEAS/RePEc](https://ideas.repec.org/a/eee/ijocip/v17y2017icp3-14.html)). It identifies as structural exposures:
  - the large geographic spread and remoteness of assets;
  - **flat control networks**;
  - **insecure control protocols**.
- In the Black Hat USA talk (26 Jul 2017), Staggs summarised a two-year study of several US wind farms ([infocondb](https://infocondb.org/con/black-hat/black-hat-usa-2017/adventures-in-attacking-wind-farm-control-networks); [Boing Boing/Wired summary, 28 Jun 2017](https://boingboing.net/2017/06/28/red-teaming-wind-farms.html), reliability medium):
  - turbines were not segmented from each other;
  - software ran with excessive privileges;
  - there was no code signing and credentials were shared across machines;
  - operating systems ranged from old embedded Windows to various Linux and real-time systems;
  - physical access to the tower base was weakly protected.
- Important limit: the demonstrated attacks needed **physical access** to at least one turbine. They were not remote. The authors said that encrypting and authenticating turbine-to-substation traffic, for example with a VPN, would block what they showed (same sources).

**US national laboratories.**
- **DOE Roadmap for Wind Cybersecurity** (July 2020; NREL, INL and Sandia authors) ([DOE](https://www.energy.gov/eere/wind/downloads/roadmap-wind-cybersecurity)). DOE states that cyber readiness of US wind plants is generally behind that of coal and nuclear plants (same search summary, reliability medium for the exact wording).
- **INL, "Attack Surface of Wind Energy Technologies in the United States"** (OSTI 2297403, published 30 Jan 2024) ([OSTI](https://www.osti.gov/biblio/2297403)).
  - It maps the attack surface of a representative wind plant.
  - Its case studies cover the US, Germany, Denmark, Ukraine and Azerbaijan.
  - The access classes it names are third-party remote access, VPN appliances, wireless and temporary access points, and pivoting from the enterprise network ([Windtech summary](https://www.windtech-international.com/industry-news/inl-report-highlights-cyberattack-risks-for-us-wind-energy-systems)).
  - INL's Jake Gentle: the connectivity that makes wind work "also creates a larger attack surface for remote and synchronized attacks on multiple assets".
- **Sandia and INL, IEEE Access (Jan 2023)**, "Cybersecurity Resilience Demonstration for Wind Energy Sites in Co-Simulation Environment" ([DOAJ](https://doaj.org/article/d452c4d2686c443db47cf0bc860a2764)). It quantifies how layered controls, including encryption, reduce attacker reach in wind OT networks, and gives payback estimates.
- **Sandia, 2003 conference paper**, "Communication vulnerabilities and mitigations in wind power SCADA systems" ([OSTI 923575](https://www.osti.gov/biblio/923575-communication-vulnerabilities-mitigations-wind-power-scada-systems)). It is an early record that cheap, interoperable SCADA brings new vulnerabilities.

### 1.1 Legacy fleet, about 1995–2010 (mostly under 2–3 MW)

**What it looks like.**
- Proprietary turbine controllers from the original OEMs, including brands later merged or discontinued.
  - Examples: early Vestas, NEG Micon, Bonus (later Siemens), Enercon, Nordex and Tacke.
  - Emerson's retrofit case studies describe a NEG Micon NM48 legacy controller and a Vestas V44 whose original controller had "no remote connection" and spare-parts problems ([Emerson NM48](https://www.emerson.com/en/automation-systems/distributed-control-systems-dcs/ovation-distributed-control-system/wind-turbine-controls/neg-micon-nm48-wind-turbine-retrofit), [Emerson V44](https://www.emerson.com/en/automation-systems/distributed-control-systems-dcs/ovation-distributed-control-system/wind-turbine-controls/vestas-v44-wind-turbine-retrofit-solution); vendor material, reliability medium).
- Communications were serial or fieldbus inside the park (for example Modbus RTU over RS-485). They were later bridged to IP with **serial-to-Ethernet device servers** placed inside the turbine ([Moxa case study via IoT ONE](https://iotone.com/case-study/remote-monitoring-and-control-for-a-windmill-generator/c413); general data-path description in an [industry knowledge base](https://industrialmonitordirect.com/blogs/knowledgebase/configuring-data-collection-for-wind-turbine-plc-systems), reliability low-medium).
- Remote access was **retrofitted**: dial-up or ISDN, then GSM/3G/4G routers, DSL and, in parts of central Europe, **satellite**.
  - KA-SAT is the proof: 5,800 Enercon turbines (about 11 GW) in central Europe lost remote monitoring and control on 24 Feb 2022 because their satellite modems were wiped ([pv magazine, 1 Mar 2022](https://www.pv-magazine.com/2022/03/01/satellite-cyber-attack-paralyzes-11gw-of-german-wind-turbines); [Modern Power Systems](https://www.modernpowersystems.com/analysis/enercon-turbines-disrupted-by-satellite-cyber-attack-9935239/)).
  - Enercon noted that many farms **had no backup communications**. It developed LTE retrofit packages, and more than 95% of turbines were reconnected by 19 Apr 2022 ([EVWind/AEE](https://evwind.aeeolica.org/?p=85745)).
  - The Australian operator Blair Fox ran legacy SCADA over circuit-switched GSM data until the 3G shutdown forced a 4G/5G retrofit ([iTnews/IoT Hub](https://www.iothub.com.au/news/m2m-connectivity-installs-5g-devices-into-blair-foxs-wind-turbines-580856)). It is an illustration from outside Europe.
- Park SCADA servers often ran on Windows versions that are now out of support. Tulsa (2017) found old embedded Windows and other unpatched operating systems.

**Who operates it.**
- Ownership is fragmented: farmers, cooperatives, municipal utilities and small investment funds (see section 3).
- After warranty, service often moves from the OEM to **independent service providers (ISPs)** such as Deutsche Windtechnik, which runs a manufacturer-independent control centre and says it fixes about 70% of faults remotely ([Deutsche Windtechnik](https://www.deutsche-windtechnik.com/en/services/onshore-services/remote-data-monitoring/)).
- **Direct marketers and aggregators** in Germany must be able to remotely read and curtail plants above 25 kW that sell through direct marketing (§10b EEG) ([Vattenfall explainer](https://energysales.vattenfall.de/en/renewables/remote-controllability); [BMWK FAQ](https://www.bundeswirtschaftsministerium.de/Redaktion/DE/Dossier/ErneuerbareEnergien/faq-zur-energierechtsnovelle-zur-vermeidung-von-stromspitzen-und-zum-biomassepaket.html)). Using a smart-meter gateway for this is suspended until 1 Jan 2028 (BMWK).
  - *Assessment:* this creates a third remote-control path, besides the OEM/ISP and the owner, into old and new turbines alike. It also concentrates control in a few aggregator platforms.

**Patch and upgrade realities.**
- The original OEM may no longer exist or may no longer support the controller.
- Retrofits replace the controller or add a modern SCADA gateway ([SCADA International OneView Park Retrofit](https://stateofgreen.com/en/?p=123710), vendor).
- *Assessment:* in many cases patching the turbine controller is not an option. The realistic controls sit at the network boundary: isolation, a controlled remote-access gateway, and replacing exposed routers.

**Lifetime and repowering.**
- Germany has more than 30,000 onshore turbines, more than 10,000 of them over 20 years old ([Bundestag document 21/2972](https://dserver.bundestag.de/btd/21/029/2102972.pdf)).
  - GTAI gives "around 9,000" ([GTAI](https://www.gtai.de/en/invest/industries/energy/wind-energy)). The figures differ by cut-off date and method.
  - 557 turbines were decommissioned in 2024, at an average age of 22 years (GTAI).
- Continued operation after the 20-year EEG support period is common; BAM finds many old towers are structurally fit for more years ([BAM, 9 Apr 2025](https://www.bam.de/Content/EN/Press-Releases/2025/Energy/2025-04-09-wind-turbine-renew.html)).
- Denmark's fleet peaked in 2001 at more than 6,200 turbines, more than half under 500 kW (secondary source quoting older data; [search result summary](https://stateofgreen.com/en/news/a-renewable-transition-in-harmony-with-people-and-nature/), reliability medium). **Gap:** the current Danish age distribution from the Energistyrelsen register.

**Attack surface (concept level).**
- Internet-reachable web panels or routers.
- Vendor modems.
- Shared or unchanged credentials.
- No segmentation between turbines.
- Old operating systems.
- Unauthenticated fieldbus and SCADA protocols.

**Strengths.**
- Small unit size: each turbine is a few hundred kW to 2 MW.
- Simple, partly hardwired protection.
- Many plants are on distribution grids, with local protection.
- Heterogeneity: many different controllers make a single mass attack harder.

### 1.2 Generation 2010–2018 (about 2–4 MW onshore, 3–8 MW offshore)

**What it looks like.**
- IP-based park networks: Ethernet and fibre rings to each turbine, and a central park SCADA.
- Standardised data models from **IEC 61400-25**, the communications series for monitoring and control of wind power plants. It maps to web services, OPC XML-DA, IEC 61850 MMS, IEC 60870-5-104 and DNP3 ([IEC 61400-25 summary](https://www.wikipedia.org/wiki/61400-25); [IEC webstore 61400-25-2](https://webstore.iec.ch/publication/22813)).
  - An OPC UA mapping (61400-25-41) was proposed in 2015 ([NettedAutomation blog, 8 Oct 2015](https://blog.nettedautomation.com/2015/10/iec-61400-25-41-project-finally-approved.html)).
  - The third edition of 61400-25-2 was at draft stage in October 2024 ([dps.gov.al IEC project page](https://dps.gov.al/en/project/show/iec:proj:105228)).
- **Security of these protocols** is delegated to **IEC 62351**. Part 4 (2018 edition) adds TLS-based transport protection and X.509 certificate-based application authentication for MMS, with integrity for the data-transfer phase ([VDE Verlag](https://vde-verlag.de/iec-normen/248345/iec-62351-4-2018.html); [IPCOMM summary](https://www.ipcomm.de/protocol/IEC62351/en/sheet.html)).
  - **Gap:** whether and how IEC 61400-25-4 normatively references IEC 62351-4. A 2012 practitioner blog argued that a reference would suffice and showed an IEC 61850 device sending credentials unprotected ([NettedAutomation, 1 Oct 2012](https://blog.nettedautomation.com/2012/10/mms-iec-61850-8-1-iec-62351-security.html), reliability low, anecdotal).
  - *Assessment:* in this generation, deployed security often depends on whether the operator turned on optional protections. Having the standard does not mean those protections are deployed.
- **OEM remote service centres**:
  - Vestas Remote Operations Centres (USA, Spain, Germany, India, Philippines), 24/7, with remote resets ([Vestas ROC brochure, 2020](https://vestas.com/content/dam/vestas-com/global/en/brochures/ROC_202008.pdf.coredownload.inline.pdf)).
  - Siemens Gamesa remote centres (Brande, Pamplona, Newcastle, Chennai) said in 2020 that they monitor and operate more than 25,000 turbines in more than 1,000 farms, and that 85% of alarms are solved remotely within 10 minutes ([Siemens Gamesa journal, May 2020](https://www.siemensgamesa.com/explore/journal/2020/05/siemens-gamesa-remote-center-covid19)). These are 2020 figures, probably out of date.
  - *Assessment:* this is the most direct parallel to the refrigeration case. A single vendor-operated remote path reaches thousands of identical units.
- **Precedents in this generation** were all on the IT or vendor side:
  - Vestas (Nov 2021): internal IT hit; manufacturing, construction and service kept running ([offshoreWIND.biz, 22 Nov 2021](https://www.offshorewind.biz/2021/11/22/vestas-suffers-cyber-security-incident/)).
  - Nordex (31 Mar 2022): IT shut down and remote access to turbines deactivated as a precaution (SecurityWeek, in the agent's table).
  - Deutsche Windtechnik (11–12 Apr 2022): remote data-monitoring connections to turbines switched off for 1–2 days "for security reasons"; turbines "never in danger" ([company statement via Windfair](https://w3.windfair.net/wind-energy/pr/40525-deutsche-windtechnik-service-provider-cyber-attack-wind-turbine-security-it-system-external-hackers)). The "about 2,000 turbines" figure comes from press reports, not the company ([The Record](https://therecord.media/german-wind-farm-operator-confirms-cybersecurity-incident-after-ransomware-group)).
  - University of Twente professor Roland van Rijswijk-Deij notes that ransomware at two turbine makers caused loss of turbine control, and in one case delayed a farm's commissioning ([Topsector Energie interview](https://topsectorenergie.nl/en/news/how-do-we-defend-against-cyber-attacks-on-offshore-wind-farms-roland-van-rijswijk-deij); interview date not captured).

**Patch realities.**
- OEM-controlled, often under long-term service agreements.
- Patching is possible but scheduled, because of type certification and grid-code compliance testing.
- *Assessment:* the owner frequently cannot patch alone. Responsibility is split across the OEM, the ISP and the owner, as it was for the refrigeration controllers, which were maintained by refrigeration contractors.

**Strengths.** Standard protocols, a central SCADA, OEM security teams, and in the EU now NIS2 obligations for larger operators.

**Weaknesses.** Flat park networks (the Tulsa findings fit this generation), optional protocol security, OEM remote paths that cover whole fleets, and VPN appliances as a common entry point.
- Dragos's February 2024 Nordic report found that more than half of sampled VPN appliances at Nordic renewable asset owners came from one vendor family. That is a concentration risk ([Dragos Nordic report](https://hub.dragos.com/hubfs/Reports/Dragos_Report_Cyber_Threat_Perspective_Nordic_Feb24_Complete.pdf), via search summary).
- In Denmark in May 2023, 22 energy companies, including small utilities with wind and solar assets, were compromised through unpatched perimeter firewalls ([Help Net Security, 14 Nov 2023](https://www.helpnetsecurity.com/2023/11/14/danish-energy-sector-cyberattack/); [Industrial Cyber](https://industrialcyber.co/reports/sektorcert-reports-cyber-attack-against-danish-critical-infrastructure-raises-concerns-of-state-involvement/)).

### 1.3 Current generation: 10–15+ MW offshore and recent onshore (2019 onwards)

**What it looks like.**
- OT networks designed with **IEC 62443 zones and conduits**: IT, OT and vendor networks separated by controlled conduits.
  - DNV's case study on a 750 MW Dutch offshore farm (about 800,000 homes) describes segmentation "at various levels". It reports that **more than half of the OT systems' services had cloud-based connectivity** and so had to meet IEC 62443 zone and conduit requirements ([DNV case](https://www.dnv.com/cyber/insights/cases/designing-ot-cybersecurity-into-an-offshore-wind-farm-to-provide-800000-homes-with-clean-energy/); date not captured).
  - A 2026 CIGRE paper (D2-10677, by SEL) gives IEC 62443-3-2 and 3-3 as the design basis for offshore wind facilities ([e-cigre](https://www.e-cigre.org/publications/detail/d2-10677-2026-cybersecurity-design-considerations-for-offshore-wind-energy-facilities-based-on-iec-62443.html)).
  - Ørsted's OT presentation shows a corporate network, a separate wind network, jump hosts and substation control systems, under IEC 62443, NIS and NERC CIP ([DI presentation, 2019](https://www.danskindustri.dk/siteassets/di-digital/2019-dokumenter/orsted-ot-networks-mads-thorted-nielsen.pdf?v=240425)).
- **Cloud analytics and digital twins.**
  - Vestas Scipher Vx+ is a SaaS platform for multi-OEM live monitoring and remote operations ([Vestas](https://www.vestas.com/en/energy-solutions/service/digital-services/scipher/scipher-vx-0)).
  - Siemens Gamesa describes a digital model forecasting asset condition ([Siemens Gamesa digitalization](https://siemensgamesa.com/explore/innovations/digitalization)).
  - The University of Groningen WindCyber project studies security for offshore digital twins ([RUG](https://www.rug.nl/rechten/onderzoek/beurzen-prijzen-en-subsidies/persoonsgebonden-beurzen/rug-stimuleringsfonds/windcyber?lang=en)).
- **Remote fleet operation** from OEM and owner centres. More functions are software-defined: grid-forming and fast-frequency features, curtailment and noise modes. Firmware is updated remotely.
  - **Gap:** no public OEM document that describes OTA update signing and rollback for turbine controllers was found.
- **HVDC-connected offshore clusters.** A Concordia University and Hydro-Québec simulation paper (IEEE SmartGridComm 2023, published 2024) shows that corrupting sensor data inside a VSC-HVDC converter station network could amplify poorly damped oscillations and affect wider grid stability ([ScienceDaily, 24 Jan 2024](https://sciencedaily.com/releases/2024/01/240124132757.htm)). This is a simulation; no real incident is reported.

**IEC 62443 certification: who has what (as found by 10 Nov 2026).**

| Company | What is publicly certified | Source | Reliability |
|---|---|---|---|
| **Envision Energy** (CN) | TÜV SÜD certificate for its **wind farm control system** (SCADA, PPC, PLCs, network devices) to **IEC 62443-3-3 SL2**, announced at WindEnergy Hamburg in late September 2026. The company also claims 62443-4-1 (secure development), 4-2 SL2 (components) and 2-4 (integration and maintenance services). | [PR Newswire, Sep 2026](https://www.prnewswire.co.uk/news-releases/envision-energy-secures-tuv-sud-certificate-for-wind-farm-control-system-strengthening-long-term-resilience-for-future-energy-systems-302890246.html); [Windtech](https://www.windtech-international.com/product-news/envision-energy-receives-cybersecurity-certificate-for-wind-farm-control-system) | medium (company release) |
| **Siemens Energy** (not Siemens Gamesa) | **Omnivise T3000** control system, used at an EnBW offshore wind project in 2022, is IEC 62443-certified. Siemens Energy holds TÜV SÜD certificates for 62443-3-3 and 4-1. | [search summary of Siemens Energy/EnBW material](https://siemens-energy.com/us/en/home/products-services/service/cyber-security-services.html) | medium |
| **Vestas** | No public 62443 certificate found. Job postings require knowledge of IEC 62443 and IEC 62351 for "ICS components" product security. | [Vestas careers](https://careers.vestas.com/job/Aarhus-N-Senior-Specialist-Cyber-Security-Regi-8200/1274816001) | low (shows intent, not certification) |
| **Siemens Gamesa, Nordex, Enercon, GE Vernova, Goldwind, Mingyang** | No public 62443 certificate found in searches. Their public certificates are IEC 61400-22 / IECRE type certificates, which cover design and loads, not cyber. | [Nordex/TÜV SÜD](https://www.windtech-international.com/product-news/nordex-group-receives-iec-type-certification-for-n149-5-x-turbine-from-tuv-sud); [Goldwind/DNV, Jun 2024](https://www.windpowermonthly.com/article/1878233/goldwind-secures-type-certification-latest-onshore-platform) | **Gap** |

*Assessment:* "not found" does not mean "not certified". Certification may cover internal processes (62443-4-1) without a press release. The research question for section 7 is to check the TÜV SÜD, TÜV Rheinland, DNV, UL and ISASecure registries directly and to ask OEM product-security teams.

One trade article says 62443 certification is increasingly seen as a precondition for financing and grid connection in Europe ([OT Security Wire, 2026](https://otsecuritywire.com/articles/wind-energy-scada-turbine-controller-cybersecurity-attack-surface-2026/); reliability low).

**Regulatory envelope for current-generation plants.**
- **NIS2** covers electricity producers above national thresholds. **Germany** implemented NIS2 in December 2025 (per [openKRITIS](https://www.openkritis.de/it-sicherheitsgesetz/sektor_energie.html), reliability medium).
  - The KRITIS threshold for generation plants is **104 MW**, with 36 MW for primary-control providers and any size for black-start plants (openKRITIS).
  - A Bundestag submission notes that a 100 MW farm falls below the threshold, while its grid-connection substation may still be covered under a draft new category ([Bundestag lobby-register submission](https://www.lobbyregister.bundestag.de/media/c0/0d/776247/Stellungnahme-Gutachten-SG2606240132.pdf)).
  - *Assessment:* most farmer and cooperative plants sit far below these thresholds.
- **Network Code on Cybersecurity**, Regulation (EU) 2024/1366, and the **Cyber Resilience Act**: see the agent's section 5.
- **Offshore guidance.**
  - The Norwegian Offshore Norge guideline 104 sets OT baseline requirements, including segmentation ([Offshore Norge](https://www.offshorenorge.no/contentassets/15263fd7f781409286f319bbeb427d93/104---recommended-guidelines-on-cyber-security-baseline-requirements-for-operations-technology-systems.pdf)). It was written for oil and gas but is used as a reference.
  - The World Economic Forum mentions an "OT Cyber Security for Offshore Wind" joint industry project ([WEF](https://www.weforum.org/stories/cybersecurity/offshore-wind-industry-cybersecurity/)).
  - DNV-RP-0575 (2021) covers the cyber security of grid substations and protection devices. It was developed with Fingrid, Statnett and Svenska Kraftnät ([DNV, 2021](https://www.dnv.com/news/2021/new-dnv-recommended-practice-defends-power-grid-substations-from-growing-threat-of-cyber-attacks-207577/)).

**Strengths.** Segmentation by design, NIS2 operators, 24/7 SOCs (security operations centres) at large owners, protection relays at the export substation, physical inaccessibility offshore, and few owners with professional security teams.

**Weaknesses.** Large concentration: one farm is 1–2 GW behind one export system. Cloud dependencies and OEM fleet centres mean that compromising a vendor reaches many farms. Software-defined control raises the effect of a malicious set-point. The supply chain is long (van Rijswijk-Deij calls it "the biggest threat", [Topsector Energie](https://topsectorenergie.nl/en/knowledge-base/achieving-a-robust-and-resilient-offshore-energy-system-requires-strong-collaboration)). Vessels and crew transfer add access paths.

---

## 2. The "refrigerator-type" attack pattern, compared with wind turbines

### 2.1 What made the retail refrigeration controllers vulnerable (concept level, public reporting)

| Factor | What sources report | Source and date |
|---|---|---|
| **Legacy, end-of-life devices** | Danfoss told AFP and The Guardian that most affected units were "legacy" products that "no longer receive software or security updates", running outdated firmware. | [Betanews](https://betanews.com/article/danfoss-fridge-attack-france-supermarket/); [Facilities Dive](https://www.facilitiesdive.com/news/hack-of-danfoss-refrigeration-controllers-in-europe-causes-tens-of-millions/832832/); October 2026 |
| **Internet-reachable vendor controllers** | Store control panels were reachable from the internet so that maintenance contractors could adjust them remotely. Internet scanners counted about 1,825 exposed French control panels on 11 Oct 2026, down 71% to 537 by 14 Oct, as operators took them offline. One analysis puts the number of unique French devices at about 881, because scanners count services, not devices. | [Infosecurity Magazine, Oct 2026](https://www.infosecurity-magazine.com/news/france-expose-danfoss-controllers/) |
| **Weak authentication and basic hygiene** | ANSSI (France's national cybersecurity agency) said the attacks exploited basic failures such as weak passwords and missing elementary defences. Vulnerabilities in these web management interfaces had been published in 2025 (CISA advisories; Claroty research, August 2025). The exact initial access route has **not** been officially confirmed. | search summary of ANSSI statements (reliability medium); [Infosecurity](https://www.infosecurity-magazine.com/news/france-expose-danfoss-controllers/) |
| **Several vendors, same class** | CERT-FR alert CERTFR-2026-ALE-012 (12 Oct, updated 13 Oct 2026) covers Danfoss controllers and two other vendors' web supervisors (Copeland, Dixell). It warns that campaigns are probably still under way. | [The Star/Reuters, 14 Oct 2026](https://www.thestar.com.my/tech/tech-news/2026/10/14/copeland-dixell-refrigeration-systems-also-hacked-french-cybersecurity-agency-says); [SecurityWeek, 3 Nov 2026](https://securityweek.com/over-100-european-stores-hit-as-supermarket-fridge-attacks-resume) |
| **Third-party remote-monitoring software** | France's blood service EFS: three sites had temperature and defrost settings changed through its refrigeration supplier's remote-monitoring software. The supplier blamed "a component from a third-party supplier" (EFS statement, 3 Nov 2026). | [BleepingComputer via search](https://bleepingcomputer.com/news/security/cyberattack-disrupts-blood-storage-refrigeration-systems-in-france); [TechSpot](https://techspot.com/news/114470-wave-european-fridge-hacks-has-reached-france-blood.html) |
| **Scale, timing, physical effect** | Many identical devices changed overnight. The effect is physical (heat, defrost) rather than data theft. | agent file, 9 Nov 2026 |
| **CERT-FR's first recommendation** | Remove internet exposure. Sources note that, for unsupported devices, isolation is the only mitigation. | search summaries, Oct 2026 |

### 2.2 Structured comparison with wind

| Dimension | Retail refrigeration (Oct–Nov 2026) | Legacy wind (1995–2010) | Current wind (2019+) | Does the analogy hold? |
|---|---|---|---|---|
| Vendor or contractor remote access | Yes, a direct internet-facing web panel | Yes, retrofitted modems and routers, ISP and aggregator links | Yes, OEM fleet centres and cloud, but through controlled conduits | **Holds** for legacy; **partly** for current (the path exists but is gated) |
| End-of-life devices still in service | Yes, many | Yes: OEMs merged or gone, 20+ year operation | Not yet (units are under 7 years old) | **Holds** for legacy |
| Many identical units | Yes (hundreds of stores, one vendor family) | Yes within a park; heterogeneous across parks | Yes, large fleets per platform | **Holds** |
| Evidence of internet exposure | About 1,825 French panels before the attack | **605 exposed wind systems in 23 European countries, out of 8,547 wind and solar systems in 35 countries** (Modat and NCSC-NL, presented 6–9 Oct 2026). Germany (212) and Italy (192) account for 67% of the wind systems. Examples include a single turbine's web interface with start/stop/reset. One outlet reports 181 sites with possible full operational control (not confirmed elsewhere). | Not separated in that study | **Holds**, on a smaller scale than solar ([Security Magazine, 9 Oct 2026](https://www.securitymagazine.com/articles/102635-8-500-european-wind-solar-systems-exposed); [SWZ Maritime, 8 Oct 2026](https://swzmaritime.nl/news/2026/10/08/8500-wind-and-solar-systems-exposed-online/); [The Hague newsroom](https://thehague.com/newsroom/en/news/how-solar-and-wind-farms-can-be-turned-and-anyone)) |
| Safety layer independent of the network | Partly (food-safety alarms; no fast physical hazard) | Hardwired safety chain and overspeed protection (design principle; **gap**: clause text) | Same, plus certified protection | **Does not hold**: turbines are built to fail safe |
| Grid protection | n/a (a load, not a generator) | DSO protection, small units | TSO grid codes, export-substation protection | **Does not hold** |
| Physical separation | Stores in towns | Rural onshore | Offshore: tens of km; access by vessel or helicopter | **Does not hold** for offshore physical access; remote paths remain |
| Who is responsible | Store, refrigeration contractor, vendor | Farmer or cooperative, ISP, aggregator | Large utility, OEM, TSO | Split responsibility: **holds** for legacy |
| Regulatory floor | Little until the CRA (2027) | Mostly below NIS2/KRITIS thresholds | NIS2, KRITIS, network code | **Holds** for legacy, not for current |

### 2.3 Realistic impacts, from most to least likely

*Assessment, grounded in the precedents:*

1. **Loss of monitoring and remote control (KA-SAT type).** This is the documented outcome every time:
   - KA-SAT: 5,800 turbines, about 11 GW, weeks to recover;
   - Deutsche Windtechnik: 1–2 days;
   - Poland, 29 Dec 2025: more than 30 wind and PV farms lost remote control and monitoring at their grid-connection substations. Wipers damaged HMIs (operator screens) and RTUs, but **production continued** ([CERT Polska report, 30 Jan 2026](https://cert.pl/en/posts/2026/01/incident-report-energy-sector-2025/)). The initial access classes were exposed remote access/VPN and default or unchanged credentials, after months of reconnaissance ([Help Net Security, 6 Feb 2026](https://www.helpnetsecurity.com/2026/02/06/poland-cyberattacks-energy-sector-industrial-organizations/)).
   - Direct consequences: turbines run on in automatic mode, but owners cannot curtail when the TSO asks. That is a grid-operations issue, not a safety one.
2. **Forced stops and production loss.** An attacker with access to a park SCADA, an aggregator platform or an exposed panel can stop turbines; the Modat/NCSC-NL study cites start/stop interfaces on the open internet. The cost is lost revenue plus restart and inspection effort. In the refrigeration case the damage was stock loss; for wind it is energy not produced, and possibly balancing costs.
3. **Equipment damage.** Simulation studies show that manipulated set-points can, in principle, drive unsafe states such as rotor overspeed or abnormal loads:
   - IEEE 2011 SCADA attack simulation ([IEEE Xplore 5772593](https://ieeexplore.ieee.org/document/5772593));
   - reachability analysis treating overspeed as the unsafe state ([City, University of London, open access](https://openaccess.city.ac.uk/id/eprint/35350/1/Cyber-Safety%20Assessment%20of%20Wind%20Turbines%20A%20Reachability%20Analysis%20Approach%20Against%20Cyber%20Attacks.pdf));
   - Kulev and Sill Torres, *Ocean Engineering* 260 (2022), on offshore parameter manipulation ([DLR elib](https://elib.dlr.de/187902/)).
   - **Why mass physical damage is harder:** the protection system is designed to act on physical limits regardless of the commanded set-point (design principle; **gap**: verify in DNV-ST-0438 / IEC 61400-1). Damage needs controller-level reprogramming, not just a change of set-point. It is type-specific, so it does not scale across a heterogeneous fleet. No real-world cyber-induced turbine damage is publicly documented as of 10 Nov 2026.
   - *Assessment:* a Stuxnet-style, long-prepared operation against one OEM platform is the scenario that cannot be excluded (van Rijswijk-Deij cites Stuxnet as proof of concept). It requires state capability and time, unlike the refrigeration campaign.
4. **Grid stability from simultaneous disconnection.**
   - The Continental Europe **reference incident is 3,000 MW** in both directions (SO GL, Art. 153); frequency containment reserve is sized to it ([ENTSO-E explanatory note](https://consultations.entsoe.eu/system-operations/synchronous-area-operational-agreement-policy-1-lo/supporting_documents/Article_A1_Explanatory_Note_for_FCR%20Dimensioning.pdf)).
   - DNV for SolarPower Europe (29 Apr 2025) estimated that a targeted compromise of about **3 GW** of inverter capacity could significantly affect the European grid. Seven inverter brands could each remotely control more than 10 GW ([SolarPower Europe](https://www.solarpowereurope.org/press-releases/new-report-solar-sector-proposes-solutions-to-mitigate-critical-cybersecurity-risks)).
   - Forescout's SUN:DOWN (Mar 2025) modelled about 4.5 GW needed to bring frequency down to 49 Hz, where load shedding is mandatory ([Forescout](https://www.forescout.com/research-labs/sun-down-a-dark-side-to-solar-energy-grids/)).
   - Real-world, non-cyber analogues show the mechanism:
     - GB, 9 Aug 2019: a lightning strike was followed by near-simultaneous losses at a gas plant and an offshore wind farm, plus embedded generation, and low-frequency demand disconnection followed ([Ofgem](https://www.ofgem.gov.uk/publications/investigation-9-august-2019-power-outage); [E3C final report, Jan 2020](https://assets.publishing.service.gov.uk/media/5e0e1fa9e5274a0fa7b4d96a/e3c-gb-power-disruption-9-august-2019-final-report.pdf)). Exact MW figures: **gap**. Secondary sources give about 664 MW (gas) and about 406 MW (wind) for the first losses (reliability medium).
     - Iberia, 28 Apr 2025: the ENTSO-E expert panel's final report (about 20 Mar 2026) found an uncontrolled voltage rise and premature generator disconnection under overvoltage. It found renewables did not cause the event ([pv magazine, 23 Mar 2026](https://www.pv-magazine.com/2026/03/23/entso-e-report-finds-systemic-failures-behind-2025-iberian-blackout/)). Not cyber.
   - *Assessment:* a coordinated stop of more than 3 GW of wind within seconds would exceed the dimensioning incident. That would mean either one OEM or cloud platform controlling several large offshore farms, or many aggregated small units. The legacy fleet is fragmented across many controllers and owners, which lowers that risk. **Simultaneity and concentration** in current-generation vendor platforms and in inverter clouds raise it. A slow forced stop (minutes) is absorbed by reserves and redispatch. A fast synchronised change, or oscillation-inducing behaviour (Concordia HVDC study), is the harder case.

---

## 3. Weaker segment: inverters, solar, and small farmer- or cooperative-owned turbines

**Inverters and solar (facts).**
- Modat and NCSC-NL (Oct 2026): 7,942 of the 8,547 exposed systems are solar, in 34 countries; Spain alone has 2,766 (35%). The Netherlands had 132 solar and 9 wind systems exposed ([SWZ Maritime, 8 Oct 2026](https://swzmaritime.nl/news/2026/10/08/8500-wind-and-solar-systems-exposed-online/)).
- Forescout SUN:DOWN (Mar 2025): 46 new vulnerabilities in three inverter vendors. Monitors accounted for 38% of affected components, cloud back-ends 25%, inverters only 15%. Patch status is reported inconsistently between sources ([The Hacker News, Mar 2025](https://thehackernews.com/2025/03/researchers-uncover-46-critical-flaws.html); [Elektor](https://www.elektormagazine.com/news/solar-power-inverters-risks-and-realities)).
- DNV/SolarPower Europe (29 Apr 2025) found unsecured remote access with default credentials, unverified firmware updates and remote control through cloud servers often outside the EU. It recommends limiting remote control to entities in the EU or equivalent jurisdictions ([SolarPower Europe](https://www.solarpowereurope.org/press-releases/new-report-solar-sector-proposes-solutions-to-mitigate-critical-cybersecurity-risks)).
- BSI (Germany's federal cybersecurity agency) president Claudia Plattner: "we are running into a risk". The decisive question is how many inverters an attacker could switch off at once; about 3 GW is the threshold cited ([Stuttgarter Zeitung](https://www.stuttgarter-zeitung.de/inhalt.unsichere-wechselrichter-wenn-die-solaranlage-gehackt-wird.b507a063-6ffc-4162-b228-fd988c86fa5c.html)).
  - In October 2025 Plattner said the BSI lacked a sufficient legal basis to regulate home energy-management systems (via the same coverage).
  - The BSI is reported to prefer local control through the smart-meter gateway over control through the manufacturer's cloud (§14a EnWG) ([innobu](https://www.innobu.com/en/articles/chinese-inverters-security-risk-high-risk-list-2026.html), reliability low-medium).
- Undocumented communication components in some Chinese inverters and batteries (Reuters, 14 May 2025, anonymous sources; no manufacturers named; China rejects the claims) ([Utility Dive](https://www.utilitydive.com/news/rogue-communication-devices-found-on-chinese-made-solar-power-inverters/748242/)).
- Deye remote deactivation (Nov 2024), Lithuania's ban on remote access from high-risk countries for plants above 100 kW (12 Nov 2024), Dutch RDI inverter tests: see the agent's file.

**Small turbines owned by farmers and cooperatives (facts).**
- **Germany:** private individuals and farmers owned about 40.6–41% of onshore wind capacity (trend:research for AEE, 2016 data) ([AEE](https://www.unendlich-viel-energie.de/media/file/284.AEE_RenewsKompakt_Buergerenergie.pdf)). The share is falling (−9 points 2012–2016). Citizen wind farms up to 18 MW are exempt from tenders (EEG 2022). **Gap:** post-2019 share.
- **Denmark:** cooperative ownership dates from the late 1970s–1980s; most turbines in 1984–94 were built by cooperatives; residents within 4.5 km have a right to buy in ([Springer chapter, 2018](https://rd.springer.com/chapter/10.1007/978-3-319-93518-8_11); [IEA policy record](https://www.iea.org/policies/17800)). **Gap:** current number of cooperative or farmer-owned turbines and their age profile.
- **INL distributed wind work** (MIRACL project, with NREL, PNNL and Sandia):
  - Cybersecurity Guide for Distributed Wind (2021);
  - "Cybersecurity for Distributed Wind: What Operators Need to Know" (May 2022, OSTI 1869646) ([OSTI](https://www.osti.gov/biblio/1869646));
  - Culler et al., "A Cyber-Resilience Risk Management Architecture for Distributed Wind" (Oct 2021) ([OSTI 1846164](https://www.osti.gov/biblio/1846164)). It says there is "little to no existing guidance" for distributed wind, and its scope runs from 5 kW to multi-MW behind-the-meter and distribution-connected turbines.
  - INL's Stephen Bukowski says smaller DER (distributed energy resources) get less cyber attention partly because of regulation ([DOE](https://www.energy.gov/eere/wind/articles/inl-collaborates-national-labs-bolster-cybersecurity-and-resilience-distributed)).
- **Danish sector CERT:** SektorCERT's 2023 report shows that small utilities operating wind and solar were among the compromised entities. **Gap:** no SektorCERT advisory aimed specifically at small turbine owners was found.

*Assessment: why this segment is weaker, and why it resembles the refrigeration case most.*
- The **owners are not security organisations**: a farmer, a cooperative board or a small municipal utility.
- Devices are **old and out of support**.
- **Third parties hold remote access**: ISPs, aggregators or direct marketers under §10b EEG, and installers.
- Plants fall **below NIS2/KRITIS thresholds**.
- Remote access is installed **for convenience**, as in the supermarkets.
- The **impact per site is small**. The systemic risk comes from **aggregation**: one aggregator, installer or inverter cloud links thousands of these sites, so the platform, not the individual turbine, is the high-value target.
- *Assessment:* the inverter cloud is a larger aggregation risk than small turbines, because of capacity (hundreds of GW) and vendor concentration.

---

## 4. Old vs new turbines: summary comparison

| | Legacy (about 1995–2010) | 2010–2018 | Current (2019+, 10–15+ MW offshore) |
|---|---|---|---|
| Typical unit size | 0.2–2 MW | 2–4 MW onshore, 3–8 MW offshore | 5–7 MW onshore, 10–15+ MW offshore |
| Controller | Proprietary, OEM may be gone | OEM platform, supported | OEM platform, software-defined, OTA updates |
| In-park network | Serial or fieldbus, later bridged to IP | IP/Ethernet rings, often flat (Tulsa 2017) | Segmented zones and conduits (IEC 62443) |
| Protocols | Proprietary, Modbus, no authentication | IEC 61400-25 / 61850 / 104; IEC 62351 security optional | Same, with more TLS and certificates; cloud APIs |
| WAN / remote | Dial-up, GSM/3G/4G routers, satellite, DSL | VPN to OEM centre; ISP links | Fibre with export cable; OEM fleet centres; cloud |
| Who operates | Farmer, cooperative, small utility; ISP; aggregator | Utilities and funds; OEM service contracts | Large utilities (NIS2); OEM; TSO interface |
| Patching | Often impossible; boundary controls only | OEM-scheduled; grid-code testing | OEM-managed; secure development lifecycle claims (62443-4-1, where certified) |
| Cyber certification | None | Rare | Emerging: Envision farm control system 62443-3-3 SL2 (Sep 2026); Siemens Energy control system; others not public |
| Regulation | Mostly below thresholds | Partly in NIS2 | NIS2, KRITIS (≥104 MW in DE), network code |
| Main attack surface (concept) | Exposed panels and routers; shared credentials; old operating systems | VPN appliances; OEM/ISP IT; flat park networks | Supply chain; OEM and cloud platforms; vendor remote conduits; HVDC/substation OT |
| Strengths | Small, heterogeneous, hardwired protection | Standard protocols; OEM security teams | Segmentation, SOCs, physical inaccessibility, professional owners |
| Worst realistic impact (*assessment*) | Local stops; contributes to aggregated loss via aggregators | Fleet-wide loss of remote control (KA-SAT, Nordex, Deutsche Windtechnik precedents) | GW-scale loss at one point; low probability, high impact |
| Remaining life | 0–10 years; repowering under way (557 decommissioned in DE in 2024) | 10–20 years | 25–30+ years |
| Closest to the refrigeration case? | **Yes** | Partly (vendor remote path) | Mostly no, except through vendor or cloud compromise |

---

## 5. Points for the report authors (*assessment*)

- The analogy is strongest for the **legacy and small-owner segment** and for **solar inverters**, not for large offshore farms.
- The documented outcome of every wind cyber incident so far is **loss of remote monitoring and control, with production continuing**. No damage has been documented.
- The **3 GW reference incident** is the useful yardstick for "how much simultaneous loss matters" in Continental Europe.
- **OEM and cloud platform compromise** is the main path by which a current-generation fleet could be affected at scale. It is the same "control the vendor, control the fleet" logic as the refrigeration case.
- Mitigations to cite are common to all sources: take panels off the internet; gate vendor access through controlled, logged, time-limited conduits; segment; keep backup communications (an Enercon lesson); be able to run in manual or island mode; inventory end-of-life devices.

---

## 6. Sources consulted (by type)

- **Agencies and CERTs:** CERT Polska (30 Jan 2026), CERT-FR alert (12–13 Oct 2026), ANSSI (Oct 2026), NCSC-NL with Modat (Oct 2026), BSI (2025–2026), SektorCERT (Nov 2023), CISA (2025 advisories, cited only by class).
- **US national laboratories:** DOE Wind Cybersecurity Roadmap (Jul 2020), INL attack-surface report (Jan 2024), INL distributed wind guides (2021–2022), Sandia/INL IEEE Access (2023), Sandia (2003).
- **Standards bodies and classification societies:** IEC 61400-25, IEC 62351-4:2018, IEC 62443 (via CIGRE 2026 and DNV case), DNV-ST-0438, DNV-RP-0575, ENTSO-E SO GL reference incident.
- **Academic:** Staggs et al. (IJCIP 2017; Black Hat 2017), Concordia/Hydro-Québec (2023–2024), Kulev and Sill Torres (2022), City University reachability paper, University of Twente (van Rijswijk-Deij).
- **Industry:** DNV/SolarPower Europe (Apr 2025), Forescout (Mar 2025), Dragos (2023, Feb 2024), OEM pages (Vestas, Siemens Gamesa, Deutsche Windtechnik, Envision).
- **Press:** reliability medium; used for event facts.

---

## 7. Open questions

1. **Independence of turbine protection systems.** What exactly do IEC 61400-1 and DNV-ST-0438 require about separating the protection system from the control system and network? Can any networked parameter change protection thresholds? This is decisive for the "mass physical damage is hard" claim.
2. **OEM IEC 62443 status.** Do Vestas, Siemens Gamesa, Nordex, Enercon, GE Vernova or Goldwind hold 62443-4-1, 4-2, 3-3 or 2-4 certificates? Check the TÜV SÜD, TÜV Rheinland, DNV, UL and ISASecure registries and ask the OEMs.
3. **OTA updates.** How do OEMs sign, stage and roll back controller firmware updates sent from fleet centres? Is there a public statement?
4. **Concentration.** How many GW can each OEM fleet centre or cloud platform command at once, as opposed to only monitor? Is there any limit on simultaneous commands? The same question applies to German direct marketers and aggregators under §10b EEG.
5. **Wind exposure detail.** Which turbine generations and owner types make up the 605 exposed wind systems in the Modat/NCSC-NL study? Is the "181 sites with full control" figure confirmed?
6. **Legacy fleet size.** How many turbines of the 1995–2010 generation still run in DK, DE and NL? How many have retrofitted cellular or satellite links? What is the effect of 2G/3G shutdowns on legacy links?
7. **Ownership share.** What are the current (post-2019) shares of farmer and cooperative ownership in Germany and Denmark, and what share of those plants sits under any cyber regulation?
8. **Refrigeration access route.** Will ANSSI or CERT-FR confirm the initial access route (exposed interface vs. contractor platform vs. third-party software component)? The answer decides which wind segment the analogy fits best.
9. **Attribution.** Can the IRGC attribution (9 Nov 2026) be verified on primary French government sources? Is the October wave linked to the November wave and to the EFS incident?
10. **Poland follow-up.** Did the CERT Polska follow-up report name generic lessons for turbine-level (as opposed to substation-level) systems? The full text was not read.
11. **Grid yardstick.** What are the confirmed MW of the 9 Aug 2019 GB losses? What is the current Continental Europe FCR (frequency containment reserve) under the probabilistic method?
12. **IEC TC 88.** Is there a wind-specific cyber standard or technical specification in preparation? None was found.
