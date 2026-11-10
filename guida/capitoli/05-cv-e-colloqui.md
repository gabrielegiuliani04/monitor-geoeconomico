# Capitolo 5 — Come presentarlo: CV, LinkedIn, colloqui

Questo è il capitolo da tenere aperto durante la ricerca di lavoro: come raccontare il Monitor a chi assume in un porto, in un'azienda di logistica o di shipping, in un operatore dell'eolico offshore o in un gestore di rete nei Paesi Bassi, in Danimarca e nel Baltico. Due regole:

1. **Dire solo quello che sai spiegare.** Un selezionatore può aprire il repository durante il colloquio: ogni frase del CV deve reggere a una domanda di approfondimento.
2. **Ogni numero ha una fonte e una data.** Molti cambiano ogni giorno: **prima di inviare un CV o pubblicare un post, ricontrollali nel file indicato** e aggiorna la data.

I testi da usare sono **in inglese**, perché lì selezione e colloqui si fanno in inglese; il commento è in italiano.

### I numeri da usare (al 10 novembre 2026)

| Numero | Valore | File e data del dato |
|---|---|---|
| Transiti a Hormuz | 4,4 navi al giorno contro 90,3 un anno prima (−95%), settimana al 1° novembre | `portwatch.json` |
| Navi sanzionate (USA, UK, UE) | 2.022 | `sanzioni-navi.json`, 9/11 |
| Porti nell'indice di rischio | 39 (30 Mare del Nord e Baltico, 9 italiani) | `port-risk.json`, 10/11 |
| Rotte con tempi di viaggio | 99 (11 origini × 9 porti europei) | `transit-times.json`, 10/11 |
| Tappe dell'eolico offshore 2023–2027 | 114 | `wind-calendar.json`, 10/11 |
| Livelli tematici della mappa | 42 | pannello *Layers*, 10/11 |
| File di dati | 66 file JSON di dati (67 con `health.json`) | `docs/data/` |
| Script Python | 37 in `raccolta/`, di cui 33 raccolgono o calcolano dati | conteggio del 10/11 |
| Aggiornamento automatico | 3 workflow: 17 passi di dati ogni giorno, mercati nei giorni feriali, 11–12 passi la domenica | `.github/workflows/` |
| Affermazioni verificate nei 4 report pubblicati | 416, di cui 91 corrette | `report/revisioni/*.md` |
| Fonti di dati distinte | oltre 50 | `DATA_LICENSES.md` |

> **Attenzione.** I testi in `vetrina/` (9 novembre) e il `README.md` hanno numeri vecchi: «15 collectors», «42 data files», «24 layers». Aggiornali prima di usarli (§5.6, settimana 1).

## 5.1 Che cosa dimostra il progetto

Un selezionatore non assume «un progetto»: assume competenze che il progetto rende visibili.

| Competenza | Prova concreta | File |
|---|---|---|
| **Analisi del rischio** | Cruscotto probabilità × impatto su 18 passaggi e infrastrutture; indice per 39 porti, ogni giorno; soglie verificate sulla serie storica | `rischio.json`, `port-risk.json`, `report/metodo-rischio.md` |
| **OSINT e verifica delle fonti** | Fonte, link, data e affidabilità su ogni dato; coordinate con precisione; fatti separati dalle valutazioni; PortWatch contro Lloyd's List a Hormuz (23 contro 116 transiti nella stessa settimana) | `METODO.md`, `report/revisioni/` |
| **Dati e automazione** | Script Python quasi tutti con la sola libreria standard; un formato comune per 66 file; tre workflow GitHub Actions; controllo di qualità ogni mattina | `raccolta/`, `.github/workflows/`, `health.json` |
| **Cartografia** | Mappa (canvas + d3) con 42 livelli tematici: stretti, rotte, porti, condotte, GNL, cavi, rete elettrica, eolico, AIS | `docs/index.html` |
| **Report con revisione** | 4 report con standard scritto e revisione indipendente: 416 affermazioni, 91 corrette | `report/STANDARD.md` |
| **Porti, energia e shipping** | Report *Northern Europe*; tempi di viaggio su 99 rotte; 114 tappe dell'eolico; filiera eolica (19 porti, 20 navi) | `docs/report/en/northern-europe-2026-11.html` |
| **Dati usati in modo responsabile** | Audit delle licenze file per file; modulo ISW spento senza consenso scritto; chiavi mascherate | `DATA_LICENSES.md`, `report/licenze.md` |
| **Lavorare con l'AI in modo controllato** | Regole comuni per le sessioni AI; una sola sessione può modificare la mappa; revisioni separate dalla scrittura | `raccolta/AGENTI.md`, `STATO.md` |

Per ogni annuncio scegli **le 3 competenze più vicine al ruolo**: un CV con otto competenze sembra un elenco, uno con tre sembra un profilo.

## 5.2 Il CV

Metti il progetto in una sezione **"Projects"** subito dopo l'esperienza (o dopo la formazione, se l'esperienza è poca), sempre con **due link**: la mappa e un report. Il link al codice solo per ruoli in cui conta. Date oneste: «2026» (il repository parte il 9 novembre 2026).

- Mappa: https://gabrielegiuliani04.github.io/monitor-geoeconomico/
- Report Nord Europa: https://gabrielegiuliani04.github.io/monitor-geoeconomico/report/en/northern-europe-2026-11.html
- Report Hormuz e Mar Rosso: https://gabrielegiuliani04.github.io/monitor-geoeconomico/report/en/hormuz-red-sea-2026-11.html
- Codice: https://github.com/gabrielegiuliani04/monitor-geoeconomico

Per ogni tipo di datore di lavoro: **A** una riga (CV di una pagina), **B** tre righe (standard), **C** blocco completo (quando il progetto è il punto di forza).

### 5.2.1 Autorità portuale (Port of Rotterdam, Port Esbjerg, Klaipėda, Gdańsk)

Cercano chi capisce flussi di navi, esposizione del porto alle rotte, energia nel porto (GNL, bunker, eolico) e sicurezza delle infrastrutture.

**A.** *Geo-economic Risk Monitor (personal project, 2026): open-source map and daily risk index for 39 European ports, built from IMF PortWatch port calls, chokepoint transits, security events and energy prices; every number with source and date.*

**B.**

- *Built a daily Port Risk Index for 39 North Sea, Baltic and Italian ports (probability × impact): traffic vs last year, nearby security events, dependence on disrupted chokepoints, war-risk listings.*
- *Wrote "Northern Europe: Ports and Energy" (Nov 2026): port calls, gas storage, offshore wind, shipping costs and Baltic security; 64 claims independently reviewed, 12 corrected.*

**C.**

- *Designed an open-source OSINT map that follows a disruption from the event to the ports and countries exposed (event → chokepoint → flows → freight → prices → exposure), with 42 thematic layers from 50+ public sources.*
- *Built a daily Port Risk Index for 39 ports, with thresholds calibrated on PortWatch history: a 20% drop in calls is amber because it happens in about one week in seven at a large port.*
- *Wrote "Northern Europe: Ports and Energy" (issue 1, Nov 2026). Showed that Rotterdam's −10.8% weekly drop was noise: traffic was −0.5% year to date (PortWatch, to 30 Oct 2026).*
- *Automated collection with Python and three GitHub Actions workflows (17 independent daily steps, plus a daily health check). Each data point carries source, date and a reliability level.*
- *Built with an AI coding assistant (Claude). I set the questions, schema, sources and review rules and checked the output.*

*Per Port Esbjerg* aggiungi: *"Mapped the offshore wind supply chain: 19 ports, 20 installation vessels, 8 bottlenecks; Esbjerg has shipped over 27.5 GW"* (`eolico-filiera.json`).

### 5.2.2 Operatore o installatore offshore (Ørsted, Vattenfall, Van Oord, DEME, Cadeler)

Cercano chi conosce aste, calendari dei progetti, navi e porti d'installazione, rete e rischi per le infrastrutture in mare.

**A.** *Geo-economic Risk Monitor (personal project, 2026): open-source monitor of North Sea and Baltic energy infrastructure, with an offshore wind calendar of 114 milestones (auctions, grid, first power, delays) and Baltic cable security.*

**B.**

- *Built an offshore wind calendar for 2023–2027 (114 milestones, 13 countries), validated daily; it flags dates that have passed without confirmation.*
- *Mapped the supply chain and its bottlenecks (auctions, HVDC cables and converter platforms, vessels, ports): about 7.2 GW of tenders drew no award in 2023–2025.*

**C.**

- *Designed an open-source map of energy infrastructure and shipping in the North Sea and Baltic: 180 wind farms, HVDC links, submarine cables and incidents, LNG terminals and AIS positions.*
- *Built an offshore wind calendar of 114 milestones and an "awarded vs target" comparison by country: Germany awarded 17.8 GW in 2023–26, but 16 GW of awarded sites still lack an FID.*
- *Analysed why auctions fail: 6.5 GW of negative-bid rounds got no bids (DK 2024, DE and NL 2025), while two-sided CfDs cleared in the UK (8.4 GW), Poland (3.4 GW) and Denmark (1.8 GW).*
- *Tracked Baltic infrastructure risk: six cable incidents since Nov 2024, sanctioned tankers in AIS, GNSS jamming (GPSJam).*
- *Automated with Python and GitHub Actions; built with an AI coding assistant (Claude) under my design and review rules.*

*Per Cadeler o Van Oord* sostituisci la riga sulle aste con le navi: *"Western vessels able to install 15 MW+ turbines go from zero in 2020 to over 25 by 2028; Cadeler reported 66% fleet utilisation in H1 2026"* (`eolico-filiera.json`).

### 5.2.3 Shipping e logistica (Maersk, DFDS, Kuehne+Nagel)

Cercano chi ragiona su rotte, tempi di transito, noli, carburante, ETS e stretti.

**A.** *Geo-economic Risk Monitor (personal project, 2026): open-source map linking chokepoint transits to transit times, freight rates and fuel costs on 99 Asia, Gulf and Atlantic routes to European ports.*

**B.**

- *Modelled sea transit times on 99 routes to 9 European ports, today vs 2023: Shanghai–Rotterdam takes 29.6 days via Suez and 40.1 via the Cape (+10.5); to Genoa the Cape adds 15.7 days.*
- *Tracked 13 chokepoints with IMF PortWatch (Hormuz −95% year on year) and broke down voyage costs into fuel, EU ETS and war-risk insurance.*

**C.**

- *Designed an open-source OSINT map that follows a disruption along the chain: event → chokepoint → flows → freight → prices → exposed ports.*
- *Modelled transit times (Dijkstra routing on open shipping lanes, three scenarios) for 99 routes: the Red Sea crisis hurt Mediterranean ports far more than northern ones (+15.7 to Genoa vs +10.5 days to Rotterdam via the Cape).*
- *Showed that fuel price, not distance, is now the largest extra cost: VLSFO in Singapore at $854/t vs $521.5/t on 27 Feb 2026 (+64%).*
- *Quantified EU ETS on shipping at the 9 Nov 2026 EEX auction price (€86.91/t CO₂): €275 per tonne of fuel on intra-EU voyages, €138 on extra-EU voyages.*
- *Automated with Python and GitHub Actions; built with an AI coding assistant (Claude) under my design and review rules.*

*Per DFDS* metti in evidenza l'ETS tra porti UE e il Baltico; *per Kuehne+Nagel* i tempi di transito e la catena verso il cliente finale.

### 5.2.4 Gestore di rete ed energia (TenneT, Energinet)

Cercano chi capisce interconnessioni, HVDC, sicurezza degli approvvigionamenti, connessione dell'eolico, rischio fisico e cyber.

**A.** *Geo-economic Risk Monitor (personal project, 2026): open-source map of North Sea and Baltic power and gas infrastructure (HVDC links, cables, LNG, storage) with daily risk scoring and a record of cable incidents.*

**B.**

- *Mapped HVDC interconnectors, offshore grid projects and Baltic cable incidents: Estlink 2 was out from 25 Dec 2024 to 18 Jun 2025, cutting Estonia–Finland capacity from 1,016 to 358 MW.*
- *Showed that grid connections, not vessels or turbines, are now the main delay in offshore wind: BalWin1 (2 GW) slipped a year, to 15 Sep 2031.*

**C.**

- *Designed an open-source map of energy infrastructure: high-voltage grid and HVDC links, submarine cables, pipelines and LNG terminals, offshore wind farms and hubs such as Bornholm Energy Island (3 GW, planned 2034).*
- *Built a probability × impact dashboard for 18 chokepoints and infrastructure systems, including Baltic cables, pipelines and power links, with written weights and thresholds tested on 2024–2026 data.*
- *Tracked gas security of supply: German and Dutch storage at 58.9% and 63.5% on 8 Nov 2026, against an EU goal of 90% (GIE AGSI+).*
- *Documented cyber incidents in energy, e.g. the 29 Dec 2025 attack on over 30 Polish wind and solar farms (CERT Polska): remote control was lost, production continued.*
- *Automated with Python and GitHub Actions; built with an AI coding assistant (Claude) under my design and review rules.*

*Per Energinet:* la dorsale danese dell'idrogeno chiude le prenotazioni di capacità il 1° dicembre 2026 e si costruisce solo con almeno 0,5 GW prenotati (`idrogeno.json`).

### 5.2.5 Consulenza del rischio (rischio paese, catena di fornitura, assicurazioni)

Cercano metodo, scrittura chiara, separazione tra fatti e valutazioni, controllo di qualità.

**A.** *Geo-economic Risk Monitor (personal project, 2026): open-source geo-economic risk monitor with probability × impact scoring of 18 chokepoints and 39 ports, and four reports with documented fact-checking (416 claims checked, 91 corrected).*

**B.**

- *Built risk scores with explicit weights and thresholds tested on historical data, scenario signals checked daily, and a rule that separates a disruption in progress from a risk.*
- *Wrote four reports (Hormuz and Red Sea, supply chain, AI supply chain, Northern Europe) under a written editorial standard, each independently reviewed: 416 claims checked, 91 corrected.*

**C.**

- *Designed an open-source OSINT monitor that follows a shock from the event to who pays for it, with 50+ public sources.*
- *Built an ISO 31000-style probability × impact dashboard for 18 units. Reading of 9 Nov 2026: Qatar LNG 24.0/25 and Hormuz 22.5 are critical; TransMed scores low on probability but 4.3/5 on impact, because one pipeline carries 34% of Italy's gas.*
- *Defined reliability rules: high/medium/low on every data point, facts separated from assessments, stated coordinate precision, an explicit "missing" for missing data.*
- *Independent reviews checked 416 claims and corrected 91, including a time-zone bug that shifted market dates by one day.*
- *Built with an AI coding assistant (Claude): I set the questions, rules and review process and decided what was published.*

### 5.2.6 Parole chiave per i sistemi ATS

I sistemi ATS filtrano i CV prima che li legga una persona. Usa **le parole esatte dell'annuncio** (se sono vere per te), mettile nella voce del progetto e nella sezione *Skills*, e niente tabelle, colonne o icone nel CV.

| Area | Parole chiave |
|---|---|
| Comuni | risk assessment · OSINT · source verification · data analysis · Python · JSON · GitHub Actions · data pipeline · data visualisation · GIS · mapping · reporting · fact-checking |
| Porti | port operations · port calls · AIS · IMF PortWatch · chokepoints · supply chain resilience · LNG terminal · bunkering · port security · critical infrastructure · offshore wind ports |
| Offshore | offshore wind · auctions · CfD · FID · HVDC · export cable · installation vessel (WTIV) · monopile · project milestones · grid connection · subsea infrastructure |
| Shipping | liner shipping · transit times · freight rates · Drewry WCI · SCFI · Red Sea diversion · VLSFO · EU ETS · FuelEU Maritime · war-risk insurance · Joint War Committee · sanctions screening |
| Rete ed energia | security of supply · gas storage · GIE AGSI+ · TTF · interconnectors · TSO · ENTSOG · grid resilience · hybrid threats · cable incidents · NIS2 · Cyber Resilience Act |
| Consulenza | geopolitical risk · country risk · scenario analysis · probability × impact matrix · ISO 31000 · early warning indicators · KRI · GPR index |

### 5.2.7 LinkedIn

Il post di lancio è in `vetrina/linkedin.md` (aggiorna numeri e data).

**Headline:** *Risk & data analyst in the making | Ports, shipping and offshore energy | OSINT, Python, GitHub Actions | Built an open-source Geo-economic Risk Monitor | Open to roles in NL, DK and the Baltic*

**About:** *I follow disruptions from the event to the people who pay for it. My project, the Geo-economic Risk Monitor, is an open-source map that links chokepoints, ports, energy infrastructure, freight and prices, with a source, a date and a reliability level on every number. It scores 39 European ports and 18 chokepoints every day, models transit times on 99 routes to European ports, and tracks 114 offshore wind milestones in the North Sea and the Baltic. I built it with an AI coding assistant: I set the questions, the data rules and the review process, and I check what gets published. I am looking for roles in port strategy, logistics, shipping and offshore energy in the Netherlands, Denmark and the Baltic region.*

**In evidenza (Featured)**, in quest'ordine: la mappa con l'immagine `docs/img/north-sea-baltic.jpg`, il report Nord Europa, il post di lancio. **Progetti:** la versione C più vicina ai ruoli che cerchi.

## 5.3 Il discorso: 30 secondi, 2 minuti, 5 minuti

Regola: **parti da un fatto, non dalla tecnologia.** La tecnologia arriva solo se chiedono «come».

**30 secondi** (networking, inizio di una telefonata):

> *I built an open-source map that follows a disruption from the event to the ports that feel it. Take Hormuz: in the last week of October about four ships a day went through, against ninety a year earlier. The map shows where that traffic went, what happened to freight, fuel and gas prices, and which European ports are most exposed. It scores 39 ports every day, and every number has a source and a date. I want to do this kind of work inside a port or an energy company.*

**2 minuti** («walk me through your project»):

> *The question behind it is simple: when something breaks at sea, who pays, and how fast? The map follows the chain: event, chokepoint, flows, freight, prices, exposure.*
>
> *[screen 1: map, North Sea and Baltic view] For this region it shows ports, offshore wind farms, HVDC links, submarine cables and AIS positions in the Gulf of Finland. In the snapshot of 9 November, 44 of the 109 ships seen there were on Western sanction lists.*
>
> *[screen 2: Terminal, Ports tab] Every day it scores 39 European ports on probability times impact. Rotterdam and Antwerp have the highest impact but quiet signals; the highest probability is in the Russian Gulf of Finland ports. Thresholds are calibrated on PortWatch history, so a 20% drop in calls is amber, not an alarm.*
>
> *[screen 3: Northern Europe report] I also write reports with a review step. In the first Northern Europe issue the review caught that Rotterdam's −10.8% week was noise: the year to date was −0.5%.*
>
> *Python collectors refresh the data every morning through GitHub Actions, and a health check flags stale or inconsistent files. I built it with an AI coding assistant; I set the questions, the rules and the review process. The limits matter: it is not real time and it is not a forecast. It shows signals, with their sources, so a team can decide faster.*

**5 minuti** (presentazione richiesta o secondo colloquio), cinque blocchi da un minuto:

| Minuto | Cosa dire | Cosa mostrare |
|---|---|---|
| 0–1 · *Problem* | "A map shows where things break, not how much it matters." Hormuz: 4.4 vs 90.3 ships a day (week to 1 Nov 2026) | Mappa, scheda di Hormuz |
| 1–2 · *Method* | La catena, lo schema di 25 campi, i tre livelli di affidabilità, fatti contro valutazioni: "If a number has no source and date, it is not on the map." | Una scheda con fonte, data, affidabilità |
| 2–3 · *Your region* | Port Risk Index, tempi di viaggio (+10,5 giorni via Capo), calendario eolico (gara IJmuiden Ver Gamma, 26 nov – 10 dic 2026), sicurezza del Baltico: scegli il più vicino all'azienda | Terminal → *Ports*, *Wind calendar*; report Nord Europa |
| 3–4 · *Quality* | Standard scritto; 416 affermazioni controllate, 91 corrette; l'errore di fuso orario (domanda 17); il controllo di qualità quotidiano | `report/revisioni/northern-europe-2026-11.md` |
| 4–5 · *Limits, next steps* | AIS, ritardo di PortWatch, prezzi Yahoo indicativi, licenze non commerciali: "Inside your company I would connect it to berth schedules and replace the non-commercial sources." | Sezione *Limits* del README |

> **Attenzione.** Prepara lo schermo prima: schede del browser già aperte nell'ordine, zoom sulla regione, notifiche spente. Se la connessione è lenta, tieni pronti gli screenshot in `docs/img/` o le immagini di questa guida.

## 5.4 Le 20 domande probabili

Le risposte sono tracce da dire con parole tue. Se non sai una cosa, dillo e spiega come la controlleresti: per un ruolo di rischio, sapere dove finisce la propria conoscenza è un punto a favore. Altre domande sono in `vetrina/colloquio.md`.

### A. Domande tecniche

**1. "How does the daily update work?"**
> *Three GitHub Actions workflows. The data one runs every day at 05:15 UTC with seventeen independent steps: flows and sanctions, gas storage, AIS, calendar, energy, Northern Europe ports, bunker, chokepoints, wind calendar, transit times, and last the two risk scores, because they read the files just written. Each step can fail without stopping the others; each file records its errors and the previous data stays. Before saving, a script masks anything that looks like an API key, a browser test checks the map and a health check flags stale or inconsistent files. Prices run on weekdays after the US close, slower sources every Sunday. The git history is the archive.*

**2. "How do you verify a source?"**
> *Five questions. Who produces it, and do they have a stake? Is it primary or a copy? Is there a second, independent source? When was it published, and when did the fact happen? How precise is it? Then a level: high, medium or low. When two sources disagree, I show both and explain why. At Hormuz, PortWatch counted 23 transits in a week where Lloyd's List Intelligence counted 116: they don't contradict each other, LLI also reconstructs ships with AIS switched off.*

Il confronto è nella stessa settimana (19–25 ottobre 2026): la revisione del report Hormuz ha corretto proprio questo punto. Raccontalo se ti chiedono.

**3. "Why these weights in the risk score?"**
> *Probability asks four questions: are flows falling (35%, the most direct measure), are there attacks nearby (30%), is the geopolitical climate worsening (15%), is the market pricing it (20%). Impact asks how much passes through, whether there are alternatives, how much buffer there is in stocks, and how expensive it already is. Stocks get 25% because they decide whether a blockage becomes rationing. The weights are judgements, written down so anyone can challenge them. The thresholds are tested: in normal chokepoints a fall of more than 30% on a year never happened between January 2024 and February 2026.*

Non confondere i pesi con quelli dell'indice dei porti (§3.2).

**4. "Is this a forecast? What does a score of 5 mean?"**
> *No, it is not a forecast and not a statistical probability. A 5 means a disruption is in progress, or every signal is on alert: if transits are 50% or more below the reference, probability is set to 5, because you don't estimate the probability of something that has already happened. The score says where to look. For the "when", I use scenarios with measurable signals, checked every day.*

**5. "What is the weakest part of the data?"**
> *AIS. The counts only see ships with the transponder on, so shadow-fleet tankers and ships in war zones are undercounted, and Russian ports are underestimated. PortWatch also lags by about a week, ten days for ports. Second, futures and stock prices come from Yahoo Finance, which is unofficial, so I use them as context. Third, some sources are non-commercial: fine for a personal project, not for a company.*

**6. "What would you do with more data, or a budget?"**
> *Four things. Berth waiting times or terminal data: today a strike, the weather and congestion all look like the same drop in calls. Licensed satellite AIS, to see the middle of Hormuz and the Red Sea. The prices I'm missing: tanker freight such as TD3C, current war-risk premiums, copper and steel for cables and monopiles. And a backtest: with a longer history I would count how often a "high" became a real disruption, and recalibrate.*

### B. Domande di dominio

**7. "What happens to Rotterdam if Hormuz closes?"**
> *It isn't hypothetical: Hormuz has been effectively closed since early March 2026. Rotterdam's traffic held up: 82.7 calls a day from January to the end of October, −0.5% on 2025. The shock comes through energy. TTF gas was €82/MWh on 9 November, +164% on a year; Dutch storage was 63.5% full on 8 November, about 19 points below the five-year average. Most Dutch LNG is American, about 77% in Q1 2026, so Gate keeps running, but at a higher price. Bunker fuel at Rotterdam costs 51% more than in late February. So for the port the risk is less about ships and more about energy cost, bunker business and refinery feedstock. Saudi crude now comes via Yanbu and the Red Sea, which is actually 8.6 days shorter.*

Fonti: report *Northern Europe* e la sua revisione, `esposizione-nord.json` (77%, IEEFA: il revisore non ha potuto aprire la fonte, dillo se chiedono), `transit-times.json`.

**8. "Why are offshore wind auctions failing?"**
> *Because of who carries the price risk. Rounds where the developer pays the state, or gets no subsidy, failed: Denmark 3 GW with no bids in December 2024, Germany 2.5 GW in August 2025, the Netherlands 1 GW in October 2025. Where the state offers a two-sided contract for difference, auctions cleared: the UK awarded 8.4 GW, Poland 3.4 GW, and Denmark came back in August 2026 with 1.8 GW to Vattenfall. An offshore farm is almost all upfront capital, so interest rates set the minimum price. And when auctions clear, the grid is the next bottleneck: BalWin1 slipped a year.*

**9. "What is the cyber risk for offshore wind?"**
> *The precedents are about remote control, not production. In February 2022 the attack on the KA-SAT satellite network cut remote control of about 5,800 Enercon turbines, which kept producing. On 29 December 2025 a destructive attack hit over 30 wind and solar farms in Poland: remote control was lost, production was not interrupted (CERT Polska). So the realistic risk is losing visibility and control across many sites at once, and attacks on manufacturers and service companies. Under the Cyber Resilience Act, manufacturers must report exploited vulnerabilities from 11 September 2026.*

Non sei un esperto di sicurezza informatica: se la domanda va sul tecnico, dillo e riporta il discorso sul rischio per l'operatore.

**10. "What is the shadow fleet risk in the Baltic?"**
> *Three risks: cables, spills and sanctions enforcement. In the AIS snapshot of 9 November, 44 of the 109 ships seen in the Gulf of Finland were on Western sanction lists. Since November 2024 six Baltic cable incidents have been recorded, mostly linked to dragged anchors; when Estlink 2 was cut, Estonia–Finland capacity fell from 1,016 to 358 MW for almost six months. About a third of Russia's seaborne oil exports passes the Danish straits. For a port or an offshore operator that means watching ship behaviour near cables and farms, AIS gaps and GNSS jamming.*

<div></div>

> **Attenzione.** Non usare il dato dei «292 passaggi di petroliere sanzionate nelle acque danesi nel 2025» senza dire che il revisore non ha potuto verificarlo.

**11. "Why did the Red Sea crisis hit Mediterranean ports harder than northern ones?"**
> *Geography. Going round the Cape adds about 10.5 days from Shanghai to Rotterdam, but 15.7 to Genoa, because Suez is the Mediterranean's front door. Today about 63% of Far East–Europe capacity is back on Red Sea services, so the average delay is about four days to North Europe and six to seven to Italy and Greece. For northern ports the bigger cost item now is fuel price, not distance.*

Sono giorni di sola navigazione a velocità fissa; UNCTAD dà 14–24 giorni. Se ti contestano il 10,5, spiega la differenza (§3.6).

**12. "For a TSO: where is the bottleneck in connecting offshore wind?"**
> *The grid. The delays in the calendar are mostly HVDC links and converter platforms, not vessels or turbines: BalWin1 slipped from September 2030 to September 2031, Hornsea 3's first power moved to Q1 2027 because of onshore grid works, and the Nederwiek II and IJmuiden Ver Gamma platforms are a year late. Cable makers' order books cover years of production: Prysmian about €16.5 bn, NKT €13.0 bn. A one-year platform delay blocks 2 GW of turbines already contracted.*

**13. "Rotterdam's calls fell 10.8% last week. Is traffic collapsing?"**
> *No, and this is why the review step exists. The first draft of my report led with that number. The review compared longer windows: over 30 days Rotterdam was +2.3%, and from January to the end of October −0.5%. A single week at a big port is noisy; in the port risk index a 20% drop happens in about one week in seven, so it's amber, not an alarm. The clear fall in the region was at Primorsk, −52% year to date, after drone strikes.*

**14. "How would you use this in our company?"**
> *Three uses. Early warning: watch the chokepoints and routes that feed your flows, so a fall in transits shows up before the change in arrivals. Exposure: which cargo, customers or energy supplies depend on one chokepoint, pipeline or cable, and what the alternatives are. Infrastructure risk: incidents near your assets, ship behaviour, and the milestones your projects depend on. Inside the company I would connect it to internal data, like berth schedules or project dates, and replace the non-commercial sources with licensed ones.*

### C. L'AI e gli errori

**15. "What did you do yourself, and what did the AI do?"** *(la domanda chiave)*
> *I'll be precise, because it matters. I defined the question and the chain, the goals, the regions and the priorities: for example, I decided to add a full North Sea and Baltic section because that's where I want to work, to put the whole site in English, and to drop a section that didn't fit. I chose the sources and the trade-offs on licences: I kept a module on the Ukrainian front switched off until the source gives written consent. I wrote the rules: source and date on every number, three reliability levels, facts separated from assessments, only one session allowed to change the map, a review before every report.*
> *The AI assistant, Claude through Claude Code, wrote almost all the code and the first drafts, in several parallel sessions under those rules. Separate review sessions then checked every number against the data files and the original sources: 416 claims across four reports, 91 corrected. I read the reports and the reviews, spot-check numbers and decide what goes out.*
> *I wouldn't claim I could rewrite the map's rendering code from scratch. I can explain how every number gets there, why each rule exists, and how I'd check it. Directing and checking fast automated work is becoming part of most analyst jobs.*

<div></div>

> **Attenzione.** Le decisioni citate sono vere e documentate in `STATO.md`. **I revisori sono sessioni AI separate**: se ti chiedono "who were the reviewers?", rispondi *"Separate AI sessions acting as strict reviewers against a written standard, with no access to change the data. I read their findings and decided on the corrections."* Non dire mai "independent experts". Il repository ha circa 100 commit in due giorni (9–10 novembre), molti con il messaggio «Lavori in corso degli agenti (da verificare)»; se qualcuno lo nota: *"It was built fast, in parallel sessions. The review came after, and that's where the corrections are."* Di' «I spot-check» solo se lo fai davvero (§5.6).

**16. "How do you know the AI didn't make numbers up?"**
> *Three safeguards. A rule in every instruction: never invent a number; if data is missing, write that it's missing. Structure: every data point has a source link and a date, so anything can be traced. And a separate review that recomputes the numbers with independent code and opens the original sources. It doesn't catch everything: in the Northern Europe report some claims stayed "not verifiable" because the source blocked access, and the report says so. I prefer a visible "not verified" to a confident number.*

**17. "Tell me about a mistake you found."**
> *The best one was in the price data. The review of the Hormuz report found that the price script converted Yahoo's timestamps with New York's winter UTC offset even in summer. So from 8 March to 1 November 2026 every trading day was recorded one day early. Eleven values fell on a Sunday, which is how it was spotted. The report had the date of Brent's peak close wrong by one day: 31 March, not 30. We fixed the script to use the exchange's own time zone, corrected the report and stated the error in the method section. In a market report a wrong date breaks the link between an event and a price move.*

Perché funziona: mostra un controllo di plausibilità (sedute di domenica), la correzione alla radice e la trasparenza.

**18. "Have you had a security problem?"**
> *Yes, a small one. A free API key for the gas storage data ended up in a public file, inside an error message written by a collector. I removed it, added a step that masks anything that looks like a key before every save, a daily check that turns red if it finds one, and I regenerated the key, because it stays in the git history. The lesson: in a public repository, errors and logs are outputs too.*

<div></div>

> **Attenzione.** «I regenerated the key» diventa vero solo dopo che l'hai fatto davvero (§4.5, §5.6). Fino ad allora di' "the key has to be regenerated".

### D. Motivazione e profilo

**19. "Why this region, and why does the project start from Italy?"**
> *I started from what I knew best: Italian ports and gas routes, where one pipeline, TransMed, carries 34% of the gas entering Italy. The method is the same anywhere, and I've applied it to the North Sea and the Baltic: 30 ports, offshore wind, HVDC links, cables, the shadow fleet. This region is where shipping, energy transition and security meet: the busiest ports, most of Europe's offshore wind, and the most active hybrid threats. That's the combination I want to work on.*

**20. "Can you code? What did you learn?"**
> *I can read Python, follow the data from a collector to the map, and run and fix the pipeline when a step fails. I'm not a software engineer and I don't present myself as one. What I learned is mostly analytical: a weekly number at a big port is noise; two sources that disagree often measure different things; and an explicit rule for missing data saves you from your own enthusiasm. I'm improving my Python and SQL, because I want to check the code, not only the output.*

Adatta la prima frase a quello che sai fare davvero: se oggi non sai lanciare uno script, imparalo nella settimana 1 (`python3 raccolta/rotte/tempi.py` e `python3 raccolta/porti/rischio_porti.py` girano senza rete in pochi secondi).

## 5.5 Cosa NON dire, e come tenere vivo il progetto

| Non dire | Perché | Di' invece |
|---|---|---|
| "Real-time monitoring" | Dati una volta al giorno; PortWatch in ritardo; l'AIS è un'istantanea | "Updated daily from open sources, with the date of each data point" |
| "It predicts disruptions" | Il punteggio non è una probabilità statistica | "It scores current signals and shows what to watch" |
| "It tracks all ships" | L'AIS gratuito copre bene il Baltico e male Hormuz | "It shows AIS positions where free coverage exists, and says where it doesn't" |
| "I built an AI that…" / "I coded everything" | Non c'è un modello AI nel progetto; il codice l'ha scritto l'assistente | "I built it with an AI coding assistant" (risposta 15) |
| "Reviewed by independent experts" | I revisori sono sessioni AI separate | "Independent review sessions against a written standard" |
| "Hormuz traffic is down 95%" senza data | Cambia ogni settimana | "−95% in the week to 1 November 2026, IMF PortWatch" |
| Numeri non verificati presentati come certi | Es. 292 passaggi nelle acque danesi | Citali con "not independently verified" |
| "Kerch is closed" da zero transiti AIS | Zero segnali non vuol dire zero navi | "No AIS signals recorded" |
| "Used by companies" | Non risulta da nessun file | Niente |
| "The data is free to use" | Codice MIT, dati no | "Code MIT, data under each source's licence" |
| Giudizi sulle aziende a cui ti candidi | Il file riporta fatti, non giudizi | Il fatto con la fonte |

E due cose da non fare: **non condividere dati non commerciali** come se un'azienda potesse usarli così come sono; **non fare il colloquio sul codice** se il ruolo è di analisi.

**Tenerlo vivo** (un progetto fermo da tre mesi sembra abbandonato):

| Quando | Cosa | Tempo |
|---|---|---|
| Ogni mattina o ogni lunedì | `report/qualita/<data>.md`: verde, giallo o rosso? GitHub → Actions: i workflow sono verdi? | 15 min |
| Ogni 2 settimane | Un post LinkedIn: un numero, uno screenshot, una lettura, un limite. Spunti con data: gara IJmuiden Ver Gamma (26/11–10/12/2026), risultati AR8 (27/11/2026–17/2/2027), dorsale danese dell'idrogeno (1/12/2026) | 1 ora |
| Ogni mese | Un nuovo numero di *Northern Europe: Ports and Energy* (n. 2 a dicembre), con revisione | 1–2 giorni |
| Ogni mese | Aggiornare CV, LinkedIn e `vetrina/` con i nuovi numeri; 3 righe in un registro «cosa è cambiato, cosa è stato corretto» | 45 min |
| Prima di ogni colloquio | Ricontrollare i 5 numeri che userai, aprire le schede, screenshot della classifica dei porti | 30 min |

**Messaggi dei commit:** da ora in poi chiari e in inglese («Port risk: added Esbjerg congestion note»), non «Lavori in corso (da verificare)». Chi apre la cronologia legge anche quelli.

## 5.6 Piano di 4 settimane

Obiettivo: profilo pronto, almeno 15 candidature mirate, almeno 10 contatti diretti con persone del settore, un secondo report pubblicato, il discorso provato ad alta voce.

**Settimana 1 — Mettere in ordine.** Lunedì: rigenerare la chiave AGSI e aggiornare il segreto; controllare che i workflow siano verdi. Lunedì–martedì: aggiornare i numeri in `README.md`, `vetrina/cv.md` e `vetrina/linkedin.md` (42 livelli, 66 file di dati, script e workflow attuali). Martedì: ricontrollare tu, sulla fonte originale, 10 numeri del report Nord Europa (scali di Rotterdam, stoccaggi, TTF, Estlink 2, BalWin1…), così «I spot-check» è vero. Mercoledì: lanciare in locale `tempi.py`, `rischio_porti.py` e il sito (`cd docs && python3 -m http.server 8000`). Giovedì: 3 CV di base (porti, offshore, shipping) e profilo LinkedIn. Venerdì: provare ad alta voce, registrandoti, i discorsi da 30 secondi e 2 minuti.

**Settimana 2 — Lancio e lista dei bersagli.** Pubblicare il post di lancio (martedì o mercoledì mattina). Lista di 20 organizzazioni in 5 gruppi: autorità portuali (Port of Rotterdam, Port Esbjerg, Klaipėda, Gdańsk, North Sea Port), offshore (Ørsted, Vattenfall, Van Oord, DEME, Cadeler), shipping e logistica (Maersk, DFDS, Kuehne+Nagel), reti (TenneT, Energinet), consulenza del rischio. Per ognuna una riga «che cosa del Monitor riguarda loro» (Esbjerg: rischio 3,2 in salita da 2,0; Rotterdam: impatto 5,0; Vattenfall: 1,8 GW vinti in Danimarca). Prime 5–7 candidature e 5 messaggi diretti:

> *Hi [name], I'm Gabriele, looking for roles in ports and offshore energy in [country]. I've built an open-source risk monitor for North Sea and Baltic ports; for [company/port] it flags [one specific, dated finding]. I'd really value 15 minutes of your view on what you would check first, or what I'm missing. Link: [map]. Thank you!*

**Settimana 3 — Approfondire.** Per le 3 aziende preferite, una scheda di una pagina «What the Monitor says about you» (3 numeri con data, 1 rischio, 1 cosa da osservare, 1 limite dei dati). Provare le 20 domande del §5.4, ogni risposta sotto i 90 secondi. Secondo post LinkedIn su un fatto con data. Altre 5–7 candidature e 5 messaggi.

**Settimana 4 — Secondo report e seguito.** Preparare il n. 2 di *Northern Europe* (dicembre), con revisione e una sezione su ciò che è cambiato. Aggiornare CV e LinkedIn. Un messaggio breve a chi non ha risposto dopo 7–10 giorni, con il link al report nuovo. Arrivare ad almeno 15 candidature e fare il bilancio: quali gruppi rispondono, quale numero o schermata ha funzionato.

### Lista di controllo prima di ogni colloquio

- I 5 numeri che userai sono ricontrollati nel file, con la data di oggi.
- Schede aperte nell'ordine: mappa (vista *North Sea and Baltic*) → Terminal (*Ports* o *Northern Europe*) → report in inglese → una revisione in `report/revisioni/`.
- La risposta 15 (AI) detta ad alta voce almeno una volta il giorno prima.
- Un esempio di errore (risposta 17) e uno di limite dei dati (risposta 5) pronti.
- Tre domande da fare a fine colloquio (in `vetrina/colloquio.md`), più una legata all'azienda: *"Which data do you rely on today to anticipate [arrivals / grid connection dates / vessel availability], and where is it weakest?"*
