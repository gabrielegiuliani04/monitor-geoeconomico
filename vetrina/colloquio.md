# Colloquio: 10 domande probabili e risposte-guida

Le risposte sono in inglese, perché i colloqui nei Paesi Bassi, in Danimarca e nel Baltico saranno quasi sempre in inglese. Sotto ognuna c'è una nota in italiano su cosa tenere a mente. Sono tracce da dire con parole proprie, non da imparare a memoria. Regola generale: **dire solo quello che si sa spiegare**. Se una domanda va su una parte del codice che non conosci bene, dillo e spiega come la controlleresti.

---

## 1. "Walk me through the project in two minutes."

> It is an open-source map that follows a disruption along the chain: event, chokepoint, flows, freight, prices, and who is exposed. For example, Hormuz: IMF PortWatch shows transits down 95% year on year, 4.4 ships a day against 90.3. On the map you can see where the traffic went (Cape of Good Hope, Saudi crude out of Yanbu through the Red Sea), what freight and gas prices did, and which Italian ports and gas routes are most exposed. It has 24 layers from more than 50 public sources, refreshed every day by GitHub Actions. Every number has a source, a date and a reliability level.

*Nota:* partire da un esempio concreto (Hormuz), non dalla tecnologia. Finire con la regola sulle fonti.

## 2. "What did you do yourself, and what did the AI do?"

> I designed it, and the AI wrote most of the code. I defined the question and the chain, the data schema, the reliability rules, which sources to use and what to do when a source is blocked or non-commercial, and the workflow: one collector per domain, a written report for each one, one coordinating session that is the only one allowed to change the map. Claude, through Claude Code, wrote the map page, the Python collectors and the workflows, ran them, and drafted the reports. My job was to review: read the reports, spot-check numbers against the sources, and decide what goes on the map. I would not claim I could rewrite the map's rendering code from scratch tomorrow. I can explain how the data flows, why each rule exists, and how I would check any number on it.

*Nota:* è la domanda più importante. Essere precisi e calmi, senza scusarsi. Il valore che si mostra è il giudizio (domanda, fonti, regole, verifica), che è quello che un porto o un operatore cerca in un analista. Non esagerare la parte di codice.

## 3. "How do you verify a source?"

> Five questions. Who produces it, and do they have a stake (a party to a conflict gets "low" by default)? Is it primary or a copy? I go back to the original where I can, for example the EU Official Journal rather than an aggregator. Is there a second, independent source? Reuters picked up by ten outlets is still one source. When was it published, and when did the fact happen? Those are two different dates, and both are stored. How precise is it? If an attack is reported "off Fujairah", the point is marked as estimated, with a precision in km. Then the level: high means official or several independent sources, medium means credible but unconfirmed, low means unverified or a claim.

*Nota:* avere pronto un esempio: PortWatch (4,4 navi/giorno) contro Lloyd's List Intelligence (circa 5 volte di più, perché ricostruisce anche le navi con AIS spento). Le due fonti non si contraddicono: misurano cose diverse.

## 4. "How would you use this in a port, or for an offshore operator?"

> Three uses. First, early warning: watch the chokepoints and routes that feed your port, so a fall in transits at Suez or Bab el-Mandeb shows up as an expected change in arrivals two or three weeks later. Second, exposure: which of your cargo flows, customers or energy supplies depend on a single chokepoint, a pipeline or a cable, and what the alternatives are. Third, infrastructure risk: for an offshore operator in the North Sea or the Baltic, the incidents on cables and pipelines since 2023, ship behaviour near critical assets (AIS gaps, sanctioned tankers), and the interconnectors those assets depend on. In a company I would connect it to internal data, like port calls and berth schedules, and replace the non-commercial sources with licensed ones.

*Nota:* adattare al ruolo. Porto: arrivi, congestione, rotte. Offshore: cavi, condotte, flotta ombra nel Baltico, sorveglianza delle infrastrutture. Ricordare che le licenze NC andrebbero sostituite in azienda (vedi domanda 8).

## 5. "What is the weakest part of the data?"

> AIS. The counts only see ships with their transponder on, so shadow fleet tankers and ships in war zones are missed or undercounted. Free AIS coverage is good in the Baltic and poor in the middle of Hormuz. PortWatch also lags about a week. Second, market prices for stocks and futures come from Yahoo Finance, which is unofficial. I show them for context only and I plan to move to official series (Treasury, EIA, ECB). Third, some positions are estimates. The map states their precision instead of hiding it.

*Nota:* rispondere subito, senza esitare: conoscere i limiti è un punto di forza.

## 6. "Tell me about one finding that surprised you."

> Kerch had zero recorded transits from August, against 24 a day a year earlier. The obvious reading is "closed", and Kerch was in fact closed on 10 July. But zero AIS signals is not the same as zero ships, so the data says "no signals", not "no ships". Another one: tanker traffic through Suez grew 22% while Bab el-Mandeb fell. That suggests Saudi crude loaded at Yanbu on the Red Sea and going north. I marked it as an assessment to verify, not a fact.

*Nota:* scegliere un esempio che mostri prudenza nell'interpretazione, non solo un numero impressionante.

## 7. "How does the automation work, and what happens when a source breaks?"

> Two GitHub Actions workflows. One runs every day at 05:15 UTC and calls the collectors one by one: flows and sanctions, storage, AIS, calendar, energy, chokepoints. Each step is independent, so one broken source does not stop the others. Each collector writes the same envelope: timestamp, sources, a note on what the data means, the elements, and an errors list. If a source fails, the error is written in the file and the previous data stays. Before committing, a script masks anything that looks like an API key. The git history is the archive. The second workflow updates prices after the US close.

*Nota:* se chiedono un incidente reale: una chiave API è finita per errore in un file pubblico; è stata tolta, è stato aggiunto il controllo automatico, e la chiave va rigenerata perché resta nella cronologia. Raccontarlo come lezione imparata.

## 8. "Did you check the licenses?"

> Yes, I did a full audit. The code is MIT, but the data stays under each source's license, so there is a separate data license file. Most sources are public domain or CC BY. Some are non-commercial, like TeleGeography for cables, OpenSanctions and Global Fishing Watch. Those are fine for a personal project, but a company would need to license them or use primary sources instead, for example EUR-Lex for EU sanctions. Two sources, the front-line maps, have no open license, so I need to ask the authors' permission. I flagged that as the top risk.

*Nota:* dire che non si è avvocati, ma che si sa dove sono i rischi. Mostra serietà con i dati, apprezzata in porti ed energia.

## 9. "Why Italy, and what about our region?"

> I started from where I know the exposure best: Italian ports, gas routes like the TransMed, which carried 34% of the gas entering Italy over 12 months, and the Suez route. The method is the same anywhere. The map already has a North Sea and Baltic view with cables, the HVDC grid, LNG terminals and AIS in the Gulf of Finland. For Rotterdam or Danish ports I would add their PortWatch series, the Øresund and Danish straits data (PortWatch measures Øresund), and the cable and pipeline incidents in the Baltic since 2023.

*Nota:* dimostrare che il metodo è trasferibile e che si conosce già un po' la regione (Øresund −21% su un anno, flotta ombra negli stretti danesi: circa un terzo del petrolio russo via mare passa di lì).

## 10. "What would you do next?"

> Three things. Replace the weak or restricted sources: official price series instead of Yahoo, EUR-Lex instead of OpenSanctions, and get permission or switch for the front-line data. Add a simple alert: flag a chokepoint when its seven-day average drops more than, say, 20% against the same week a year earlier, and link it to the ports and prices it affects. And write a second case study on the Baltic: cable and pipeline incidents, the shadow fleet and the Danish straits, because that is the region I want to work in.

*Nota:* chiudere con un piano concreto e legato al ruolo. Se il colloquio è per un porto specifico, proporre il caso di studio su quel porto.

---

## Domande da fare a fine colloquio
- "Which data do you rely on today to anticipate changes in arrivals or in energy supply, and where is it weakest?"
- "How does the team handle information that is useful but not yet confirmed?"
- "If I joined, what would a good first three months look like?"
