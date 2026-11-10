# Capitolo 5 — Come presentarlo: CV, LinkedIn, colloqui

Questo è il capitolo da tenere aperto durante la ricerca di lavoro. Gli altri capitoli spiegano come è fatto il Monitor. Questo spiega come raccontarlo a chi assume in un porto, in un'azienda di logistica o di shipping, in un operatore dell'eolico offshore o in un gestore di rete nei Paesi Bassi, in Danimarca e nel Baltico.

Due regole valgono per tutto il capitolo.

1. **Dire solo quello che sai spiegare.** Un selezionatore può aprire il repository durante il colloquio. Ogni frase del CV deve reggere a una domanda di approfondimento.
2. **Ogni numero ha una fonte e una data.** I numeri qui sotto vengono dai file del repository, con la data del dato tra parentesi. Molti cambiano ogni giorno (transiti, prezzi, navi). **Prima di inviare un CV o pubblicare un post, ricontrolla i numeri nel file indicato.** Se un numero è cambiato, usa quello nuovo con la sua data.

I testi da usare (righe del CV, profilo LinkedIn, discorsi, risposte) sono **in inglese**, perché in questi Paesi selezione e colloqui si fanno quasi sempre in inglese. Sotto ogni testo c'è la traduzione italiana, per controllare che il senso sia quello giusto.

**Dove si trovano i numeri** (data di riferimento del capitolo: 10 novembre 2026)

| Numero | Valore | File e data del dato |
|---|---|---|
| Transiti a Hormuz, settimana al 1/11/2026 | 4,4 navi/giorno contro 90,3 un anno prima (−95%) | `docs/data/portwatch.json` (IMF PortWatch), letto il 9/11 |
| Navi sanzionate (USA, Regno Unito, UE) | 2.022 | `docs/data/sanzioni-navi.json`, 9/11 |
| Porti nell'indice di rischio | 39 (30 nel Mare del Nord e nel Baltico, 9 italiani) | `docs/data/port-risk.json`, 10/11 |
| Rotte con tempi di viaggio | 99 (11 origini × 9 porti europei) | `docs/data/transit-times.json`, 10/11 |
| Scadenze dell'eolico offshore 2023–2027 | 114 | `docs/data/wind-calendar.json`, 10/11 |
| File di dati | 66 file JSON | `docs/data/`, conteggio del 10/11 |
| Script di raccolta | 25 `raccogli.py` (35 file Python in `raccolta/*/`) | conteggio del 10/11 |
| Passi dell'aggiornamento quotidiano | 16 passi di dati + mascheramento delle chiavi, ogni giorno alle 05:15 UTC | `.github/workflows/aggiorna-dati.yml`, 10/11 |
| Affermazioni verificate nei 4 report | 416, di cui 91 corrette | `report/revisioni/*.md`, 9–10/11 |
| Livelli tematici sulla mappa | 41 (48 interruttori meno 7 di base: confini, città, mari...) | `docs/index.html`, 10/11 (in `vetrina/cv.md` c'è ancora "24 livelli" del 9/11: va aggiornato) |
| Fonti di dati distinte | oltre 50 | `DATA_LICENSES.md` e `vetrina/cv.md`, 9/11 |

> **Attenzione ai numeri vecchi in `vetrina/`.** `vetrina/cv.md` (9/11) parla di 15 raccoglitori e 42 file di dati. Il 10/11 sono 25 e 66. Prima di usare quei testi, aggiorna i conteggi.

---

## 5.1 Che cosa dimostra il progetto

Un selezionatore non assume "un progetto". Assume competenze che il progetto rende visibili. La tabella collega ogni competenza a una prova che si può aprire e controllare.

| Competenza | Prova concreta nel progetto | Numero o file |
|---|---|---|
| **Analisi del rischio** | Cruscotto probabilità × impatto su 18 passaggi e infrastrutture, con pesi e soglie scritti. Indice di rischio per 39 porti europei, calcolato ogni giorno. Soglie verificate sulla serie storica: un calo dei transiti oltre −30% su un anno non capita mai nei passaggi "normali" tra gennaio 2024 e febbraio 2026 | `docs/data/rischio.json` (9/11), `docs/data/port-risk.json` (10/11), `report/metodo-rischio.md`, `report/port-risk-method.md` |
| **OSINT e verifica delle fonti** | Ogni dato porta fonte, link, data e affidabilità alta/media/bassa. Le coordinate dichiarano se sono della fonte o stimate, con la precisione in km. Fatti e valutazioni sono separati. Esempio di controllo incrociato: PortWatch contro Lloyd's List Intelligence a Hormuz, 23 contro 116 transiti nella stessa settimana (circa 5 volte) | `METODO.md`, `raccolta/AGENTI.md`, `report/revisioni/hormuz-mar-rosso-2026-11.md` (9/11) |
| **Dati e automazione** | 25 raccoglitori in Python, quasi tutti solo con la libreria standard. 66 file JSON con lo stesso formato (`aggiornato`, `fonti`, `nota`, `elementi`, `errori`). Due workflow GitHub Actions: dati ogni giorno alle 05:15 UTC (16 passi indipendenti), prezzi nei giorni feriali alle 21:30 UTC. La cronologia git fa da archivio | `.github/workflows/`, `raccolta/`, `docs/data/` (10/11) |
| **Cartografia** | Mappa statica (canvas + d3) con 41 livelli tematici: stretti, rotte, porti, condotte, terminali GNL, cavi, rete elettrica, parchi eolici, posizioni AIS. Regole di precisione: un evento "vicino a Hormuz" non viene disegnato come un punto esatto | `docs/index.html`; 713 cavi in `cavi.json`, 840 terminali in `terminali-gnl.json` (9/11) |
| **Report con revisione** | 4 report con uno standard editoriale scritto. Ogni report passa una revisione indipendente: 416 affermazioni controllate, 91 corrette (Hormuz 183/38; supply chain 59/9; AI 110/32; Nord Europa 64/12) | `report/STANDARD.md`, `report/revisioni/*.md` (9–10/11) |
| **Conoscenza di porti, energia e shipping** | Report "Northern Europe: Ports and Energy" (porti, stoccaggi di gas, eolico, costi del trasporto, sicurezza del Baltico). Tempi di viaggio su 99 rotte. Calendario di 114 scadenze dell'eolico offshore. Filiera dell'eolico: 19 porti, 20 navi, 8 colli di bottiglia | `docs/report/en/northern-europe-2026-11.html`, `transit-times.json`, `wind-calendar.json` (10/11), `eolico-filiera.json` (9/11) |
| **Dati usati in modo responsabile** (in più) | Verifica delle licenze file per file. Le fonti non commerciali sono segnalate. Il modulo ISW sul fronte ucraino non è attivo senza il consenso scritto dell'ISW. Le chiavi API vengono mascherate prima di ogni salvataggio | `DATA_LICENSES.md`, `report/licenze.md`, `raccolta/comune/nascondi_chiavi.py` |
| **Lavorare con l'AI in modo controllato** (in più) | Regole comuni per le sessioni AI. Una sola sessione di regia può modificare la mappa. Ogni sessione scrive un rapporto. Le revisioni sono separate dalla scrittura | `raccolta/AGENTI.md`, `STATO.md` |

**Come usarla.** Per ogni annuncio, scegli le 3 competenze più vicine al ruolo e portale nel CV e nel discorso. Non elencarle tutte: un CV con otto competenze sembra un elenco, uno con tre sembra un profilo.

---

## 5.2 Il CV

### Dove metterlo

- In una sezione **"Projects"** (o "Selected projects") subito dopo l'esperienza, oppure subito dopo la formazione se l'esperienza è poca.
- Metti sempre i **due link**: la mappa e un report. Il link al codice va solo per ruoli dove conta (dati, analisi).
- Tieni le date oneste: "2026". Il repository pubblico parte dal 9 novembre 2026 (primo commit). Non scrivere "2025–2026".

**Link da usare**
- Mappa: https://gabrielegiuliani04.github.io/monitor-geoeconomico/
- Report Nord Europa (inglese): https://gabrielegiuliani04.github.io/monitor-geoeconomico/report/en/northern-europe-2026-11.html
- Report Hormuz e Mar Rosso (inglese): https://gabrielegiuliani04.github.io/monitor-geoeconomico/report/en/hormuz-red-sea-2026-11.html
- Codice: https://github.com/gabrielegiuliani04/monitor-geoeconomico

Per ogni tipo di datore di lavoro ci sono tre versioni: **A** una riga (CV di una pagina, sezione "Projects" breve), **B** tre righe (versione standard), **C** blocco completo (CV di due pagine o candidatura in cui il progetto è il punto di forza principale).

### 5.2.1 Autorità portuale (Port of Rotterdam, Port Esbjerg, Klaipėda, Gdańsk...)

Cosa cercano: chi capisce flussi di navi, esposizione del porto alle rotte, energia nel porto (GNL, bunker, eolico), sicurezza delle infrastrutture.

**A — One line**
> **Geo-economic Risk Monitor** (personal project, 2026): open-source map and daily risk index for 39 European ports, built from IMF PortWatch port calls, chokepoint transits, security events and energy prices; every number with source and date.

*Monitor geoeconomico (progetto personale, 2026): mappa open source e indice di rischio quotidiano per 39 porti europei, costruiti con gli scali IMF PortWatch, i transiti negli stretti, gli eventi di sicurezza e i prezzi dell'energia; ogni numero con fonte e data.*

**B — Three lines**
> **Geo-economic Risk Monitor** · personal project, 2026 · [map] · [report]
> - Built a daily Port Risk Index for 39 North Sea, Baltic and Italian ports (probability × impact): traffic vs last year, nearby security events, dependence on disrupted chokepoints, war-risk listings.
> - Wrote "Northern Europe: Ports and Energy" (Nov 2026): port calls, gas storage, offshore wind, shipping costs and Baltic security; 64 claims independently reviewed, 12 corrected.

*- Ho costruito un indice quotidiano di rischio per 39 porti del Mare del Nord, del Baltico e italiani (probabilità × impatto): traffico rispetto all'anno prima, eventi di sicurezza vicini, dipendenza da stretti in crisi, aree segnalate dagli assicuratori del rischio guerra.*
*- Ho scritto "Northern Europe: Ports and Energy" (novembre 2026): scali, stoccaggi di gas, eolico offshore, costi del trasporto e sicurezza del Baltico; 64 affermazioni sottoposte a revisione indipendente, 12 corrette.*

**C — Full block**
> **Geo-economic Risk Monitor** · personal project, 2026 · [map] · [Northern Europe report] · [GitHub]
> - Designed an open-source OSINT map that follows a disruption from the event to the ports and countries exposed (event → chokepoint → flows → freight → prices → exposure), with 41 thematic layers from 50+ public sources.
> - Built a daily Port Risk Index for 39 ports. Thresholds are calibrated on PortWatch history: a 20% drop in calls is amber because it happens in about one week in seven at a large port.
> - Wrote "Northern Europe: Ports and Energy" (issue 1, Nov 2026), covering the ten largest North Sea and Baltic ports, gas storage, offshore wind and Baltic security. Showed that Rotterdam's −10.8% weekly drop was noise: traffic was −0.5% year to date (PortWatch, to 30 Oct 2026).
> - Automated collection with 25 Python collectors and GitHub Actions (daily, 16 independent steps). Each data point carries source, date and a reliability level.
> - Built with an AI coding assistant (Claude). I set the questions, schema, sources and review rules and checked the output.

*- Ho progettato una mappa OSINT open source che segue una crisi dall'evento fino ai porti e ai Paesi esposti (evento → stretto → flussi → noli → prezzi → esposizione), con 41 livelli tematici da oltre 50 fonti pubbliche.*
*- Ho costruito un indice quotidiano di rischio per 39 porti. Le soglie sono tarate sulla serie PortWatch: un calo del 20% degli scali è giallo perché in un grande porto capita circa una settimana su sette.*
*- Ho scritto "Northern Europe: Ports and Energy" (n. 1, novembre 2026) sui dieci maggiori porti del Mare del Nord e del Baltico, gli stoccaggi di gas, l'eolico offshore e la sicurezza del Baltico. Ho mostrato che il −10,8% settimanale di Rotterdam era rumore: dall'inizio dell'anno il traffico era −0,5% (PortWatch, al 30/10/2026).*
*- Ho automatizzato la raccolta con 25 script Python e GitHub Actions (ogni giorno, 16 passi indipendenti). Ogni dato ha fonte, data e livello di affidabilità.*
*- Realizzato con un assistente AI (Claude): io ho definito domande, schema, fonti e regole di revisione e ho controllato i risultati.*

*Per Port Esbjerg:* aggiungi una riga sull'eolico: "Mapped the offshore wind supply chain: 19 ports, 20 installation vessels, 8 bottlenecks; Esbjerg has shipped over 27.5 GW" (`eolico-filiera.json`, 9/11). *Ho mappato la filiera dell'eolico offshore: 19 porti, 20 navi d'installazione, 8 colli di bottiglia; Esbjerg ha spedito oltre 27,5 GW.*

### 5.2.2 Operatore o installatore offshore (Ørsted, Vattenfall, Van Oord, DEME, Cadeler)

Cosa cercano: chi conosce aste, calendari dei progetti, navi e porti d'installazione, rete, rischi per le infrastrutture in mare.

**A — One line**
> **Geo-economic Risk Monitor** (personal project, 2026): open-source monitor of North Sea and Baltic energy infrastructure, with an offshore wind calendar of 114 milestones (auctions, grid, first power, delays) and Baltic cable security.

*Monitor geoeconomico (progetto personale, 2026): osservatorio open source delle infrastrutture energetiche del Mare del Nord e del Baltico, con un calendario dell'eolico offshore di 114 scadenze (aste, rete, prima energia, ritardi) e la sicurezza dei cavi nel Baltico.*

**B — Three lines**
> **Geo-economic Risk Monitor** · personal project, 2026 · [map] · [report]
> - Built an offshore wind calendar for 2023–2027 (114 milestones, 13 countries), validated daily. It flags dates that have passed without confirmation.
> - Mapped the supply chain and its bottlenecks (auctions, HVDC cables and converter platforms, vessels, ports): about 7.2 GW of tenders drew no award in 2023–2025.

*- Ho costruito un calendario dell'eolico offshore 2023–2027 (114 scadenze, 13 Paesi), controllato ogni giorno. Segnala le date passate senza conferma.*
*- Ho mappato la filiera e i suoi colli di bottiglia (aste, cavi HVDC e piattaforme di conversione, navi, porti): nel 2023–2025 circa 7,2 GW di gare non sono stati assegnati.*

**C — Full block**
> **Geo-economic Risk Monitor** · personal project, 2026 · [map] · [Northern Europe report] · [GitHub]
> - Designed an open-source OSINT map of energy infrastructure and shipping in the North Sea and Baltic: 180 wind farms, HVDC links, submarine cables and incidents, LNG terminals and AIS positions.
> - Built an offshore wind calendar of 114 milestones and an "awarded vs target" comparison by country. Example: Germany awarded 17.8 GW in 2023–26, but 16 GW of awarded sites still lack an FID.
> - Analysed why auctions fail: 6.5 GW of negative-bid rounds got no bids (DK 2024, DE and NL 2025), while two-sided CfDs cleared in the UK (8.4 GW), Poland (3.4 GW) and Denmark (1.8 GW).
> - Tracked Baltic infrastructure risk: six cable incidents since Nov 2024, sanctioned tankers in AIS, GNSS jamming (GPSJam).
> - Automated with Python and GitHub Actions; built with an AI coding assistant (Claude) under my design and review rules.

*- Ho progettato una mappa OSINT delle infrastrutture energetiche e del trasporto marittimo nel Mare del Nord e nel Baltico: 180 parchi eolici, collegamenti HVDC, cavi sottomarini e incidenti, terminali GNL e posizioni AIS.*
*- Ho costruito un calendario dell'eolico offshore di 114 scadenze e un confronto "assegnato contro obiettivo" per Paese. Esempio: la Germania ha assegnato 17,8 GW nel 2023–26, ma 16 GW di siti assegnati non hanno ancora la decisione finale d'investimento.*
*- Ho analizzato perché le aste falliscono: 6,5 GW di aste a offerta negativa non hanno ricevuto offerte (DK 2024, DE e NL 2025), mentre i CfD a due vie hanno funzionato nel Regno Unito (8,4 GW), in Polonia (3,4 GW) e in Danimarca (1,8 GW).*
*- Ho seguito il rischio per le infrastrutture del Baltico: sei incidenti ai cavi da novembre 2024, petroliere sanzionate nell'AIS, disturbo GNSS (GPSJam).*
*- Automatizzato con Python e GitHub Actions; realizzato con un assistente AI (Claude) secondo il mio progetto e le mie regole di revisione.*

Fonti: `offshore-nord.json` (180 parchi, 9/11), `wind-calendar.json` (10/11), `eolico-filiera.json` (9/11), `report/revisioni/northern-europe-2026-11.md` (sei incidenti, 10/11).

*Per Cadeler o Van Oord:* sostituisci la riga sulle aste con una sulle navi: "Tracked the installation fleet: Western vessels able to install 15 MW+ turbines go from zero in 2020 to over 25 by 2028; Cadeler reported 66% fleet utilisation in H1 2026" (`eolico-filiera.json`, 9/11). *Ho seguito la flotta d'installazione: le navi occidentali capaci di installare turbine da 15 MW e oltre passano da zero nel 2020 a più di 25 nel 2028; Cadeler ha dichiarato un utilizzo della flotta del 66% nel primo semestre 2026.*

### 5.2.3 Shipping e logistica (Maersk, DFDS, Kuehne+Nagel)

Cosa cercano: chi ragiona su rotte, tempi di transito, noli, carburante, ETS, stretti.

**A — One line**
> **Geo-economic Risk Monitor** (personal project, 2026): open-source map linking chokepoint transits to transit times, freight rates and fuel costs on 99 Asia, Gulf and Atlantic routes to European ports.

*Monitor geoeconomico (progetto personale, 2026): mappa open source che collega i transiti negli stretti a tempi di viaggio, noli e costi del carburante su 99 rotte dall'Asia, dal Golfo e dall'Atlantico verso i porti europei.*

**B — Three lines**
> **Geo-economic Risk Monitor** · personal project, 2026 · [map] · [report]
> - Modelled sea transit times on 99 routes to 9 European ports, today vs 2023. Shanghai–Rotterdam takes 29.6 days via Suez and 40.1 via the Cape (+10.5); to Genoa the Cape adds 15.7 days.
> - Tracked 13 chokepoints with IMF PortWatch (Hormuz −95% year on year) and broke down voyage costs into fuel, EU ETS and war-risk insurance.

*- Ho modellato i tempi di navigazione su 99 rotte verso 9 porti europei, oggi contro il 2023. Shanghai–Rotterdam richiede 29,6 giorni via Suez e 40,1 via Capo di Buona Speranza (+10,5); verso Genova il Capo aggiunge 15,7 giorni.*
*- Ho monitorato 13 stretti con IMF PortWatch (Hormuz −95% su un anno) e scomposto i costi del viaggio in carburante, ETS europeo e assicurazione del rischio guerra.*

**C — Full block**
> **Geo-economic Risk Monitor** · personal project, 2026 · [map] · [reports] · [GitHub]
> - Designed an open-source OSINT map that follows a disruption along the chain: event → chokepoint → flows → freight → prices → exposed ports.
> - Modelled transit times (Dijkstra routing on open shipping lanes, three scenarios) for 99 routes. Finding: the Red Sea crisis hurt Mediterranean ports about twice as much as northern ones (+16–20 vs +10.5 days via the Cape).
> - Showed that fuel price, not distance, is now the largest extra cost: VLSFO in Singapore at 854 $/t vs 521.5 $/t on 27 Feb 2026 (+64%).
> - Quantified EU ETS on shipping at the 9 Nov 2026 auction price: 275 € per tonne of fuel on intra-EU voyages, 138 € on extra-EU voyages.
> - Automated with 25 Python collectors and GitHub Actions; built with an AI coding assistant (Claude) under my design and review rules.

*- Ho progettato una mappa OSINT open source che segue una crisi lungo la catena: evento → stretto → flussi → noli → prezzi → porti esposti.*
*- Ho modellato i tempi di viaggio (percorso minimo con Dijkstra su rotte marittime aperte, tre scenari) per 99 rotte. Risultato: la crisi del Mar Rosso ha colpito i porti del Mediterraneo circa il doppio di quelli del Nord (+16–20 contro +10,5 giorni via Capo).*
*- Ho mostrato che oggi il costo in più più grande è il prezzo del carburante, non la distanza: VLSFO a Singapore a 854 $/t contro 521,5 $/t del 27/2/2026 (+64%).*
*- Ho quantificato l'ETS europeo sul trasporto marittimo al prezzo d'asta del 9/11/2026: 275 € per tonnellata di carburante nei viaggi tra porti UE, 138 € nei viaggi da o verso l'esterno.*
*- Automatizzato con 25 script Python e GitHub Actions; realizzato con un assistente AI (Claude) secondo il mio progetto e le mie regole di revisione.*

Fonti: `transit-times.json` (10/11), `report/agenti/transit-times.md` (10/11), `report/northern-europe-2026-11.md` (ETS, 9/11).

*Per DFDS (traghetti e ro-ro a corto raggio):* metti in evidenza la riga sull'ETS tra porti UE (275 €/t), perché riguarda direttamente le linee interne all'UE, e il Baltico (Øresund −20,5% su un anno nella settimana al 1/11, `porti-nord.json`). *Per Kuehne+Nagel:* metti in evidenza i tempi di transito e la catena verso il cliente finale.

### 5.2.4 Gestore di rete ed energia (TenneT, Energinet)

Cosa cercano: chi capisce interconnessioni, HVDC, sicurezza degli approvvigionamenti di gas, collegamento dell'eolico, rischio fisico e cyber sulle infrastrutture.

**A — One line**
> **Geo-economic Risk Monitor** (personal project, 2026): open-source map of North Sea and Baltic power and gas infrastructure (HVDC links, cables, LNG, storage) with daily risk scoring and a record of cable incidents.

*Monitor geoeconomico (progetto personale, 2026): mappa open source delle infrastrutture elettriche e del gas del Mare del Nord e del Baltico (collegamenti HVDC, cavi, GNL, stoccaggi), con un punteggio di rischio quotidiano e l'archivio degli incidenti ai cavi.*

**B — Three lines**
> **Geo-economic Risk Monitor** · personal project, 2026 · [map] · [report]
> - Mapped HVDC interconnectors, offshore grid projects and Baltic cable incidents. Example: Estlink 2 was out from 25 Dec 2024 to 18 Jun 2025, cutting Estonia–Finland capacity from 1,016 to 358 MW.
> - Showed that grid connections, not vessels or turbines, are now the main delay in offshore wind: BalWin1 (2 GW) slipped a year, to 15 Sep 2031.

*- Ho mappato le interconnessioni HVDC, i progetti di rete in mare e gli incidenti ai cavi del Baltico. Esempio: Estlink 2 è rimasto fuori servizio dal 25/12/2024 al 18/6/2025 e la capacità Estonia–Finlandia è scesa da 1.016 a 358 MW.*
*- Ho mostrato che oggi il ritardo principale dell'eolico offshore viene dai collegamenti alla rete, non dalle navi o dalle turbine: BalWin1 (2 GW) è slittato di un anno, al 15/9/2031.*

**C — Full block**
> **Geo-economic Risk Monitor** · personal project, 2026 · [map] · [Northern Europe report] · [GitHub]
> - Designed an open-source map of energy infrastructure: high-voltage grid and HVDC links (OpenStreetMap), submarine cables, pipelines and LNG terminals, offshore wind farms and hubs such as Bornholm Energy Island (3 GW, planned 2034).
> - Built a probability × impact dashboard for 18 chokepoints and infrastructure systems, including Baltic cables, pipelines and power links, with written weights and thresholds tested on 2024–2026 data.
> - Tracked gas security of supply: German and Dutch storage at 58.9% and 63.5% on 8 Nov 2026, against an EU goal of 90% (GIE AGSI+).
> - Documented cyber incidents in energy, e.g. the 29 Dec 2025 attack on over 30 Polish wind and solar farms (CERT Polska): control was lost, production continued.
> - Automated with Python and GitHub Actions; built with an AI coding assistant (Claude) under my design and review rules.

*- Ho progettato una mappa open source delle infrastrutture energetiche: rete ad alta tensione e collegamenti HVDC (OpenStreetMap), cavi sottomarini, condotte e terminali GNL, parchi eolici offshore e hub come l'isola energetica di Bornholm (3 GW, prevista nel 2034).*
*- Ho costruito un cruscotto probabilità × impatto per 18 stretti e sistemi infrastrutturali, compresi cavi, condotte ed elettrodotti del Baltico, con pesi e soglie scritti e provati sui dati 2024–2026.*
*- Ho seguito la sicurezza degli approvvigionamenti di gas: stoccaggi tedeschi e olandesi al 58,9% e al 63,5% l'8/11/2026, contro l'obiettivo UE del 90% (GIE AGSI+).*
*- Ho documentato gli incidenti cyber nell'energia, per esempio l'attacco del 29/12/2025 a oltre 30 parchi eolici e solari polacchi (CERT Polska): perso il controllo remoto, produzione continuata.*
*- Automatizzato con Python e GitHub Actions; realizzato con un assistente AI (Claude) secondo il mio progetto e le mie regole di revisione.*

Fonti: `interconnessioni.json`, `offshore-nord.json` (9/11), `wind-calendar.json` (10/11), `scorte.json` (8/11), `report/agenti/cyber-energia.md`.

*Per Energinet:* puoi aggiungere la dorsale danese dell'idrogeno: le prenotazioni di capacità chiudono il 1/12/2026 e si costruisce solo se il mercato prenota almeno 0,5 GW (`idrogeno.json`). È una scadenza da citare se il colloquio cade in quei giorni.

### 5.2.5 Consulenza del rischio (rischio paese, rischio della catena di fornitura, assicurazioni)

Cosa cercano: metodo, scrittura chiara, separazione tra fatti e valutazioni, controllo di qualità.

**A — One line**
> **Geo-economic Risk Monitor** (personal project, 2026): open-source geo-economic risk monitor with probability × impact scoring of 18 chokepoints and 39 ports, and four reports with documented fact-checking (416 claims checked, 91 corrected).

*Monitor geoeconomico (progetto personale, 2026): osservatorio open source del rischio geoeconomico con punteggi probabilità × impatto per 18 stretti e 39 porti e quattro report con verifica documentata (416 affermazioni controllate, 91 corrette).*

**B — Three lines**
> **Geo-economic Risk Monitor** · personal project, 2026 · [map] · [report]
> - Built risk scores with explicit weights and thresholds tested on historical data, scenario signals checked daily, and a rule that separates a disruption in progress from a risk.
> - Wrote four reports (Hormuz and Red Sea, supply chain, AI supply chain, Northern Europe) under a written editorial standard, each with an independent review: 416 claims checked, 91 corrected.

*- Ho costruito punteggi di rischio con pesi espliciti e soglie provate sui dati storici, segnali di scenario controllati ogni giorno e una regola che distingue una crisi in corso da un rischio.*
*- Ho scritto quattro report (Hormuz e Mar Rosso, supply chain, catena dell'AI, Nord Europa) secondo uno standard editoriale scritto, ognuno con una revisione indipendente: 416 affermazioni controllate, 91 corrette.*

**C — Full block**
> **Geo-economic Risk Monitor** · personal project, 2026 · [map] · [reports] · [GitHub]
> - Designed an open-source OSINT monitor that follows a shock from the event to who pays for it (event → chokepoint → flows → freight → prices → exposure), with 50+ public sources.
> - Built a probability × impact dashboard (ISO 31000-style) for 18 units. Today's reading: Qatar LNG 24.0/25 and Hormuz 22.5 are critical; TransMed scores low on probability but 4.3/5 on impact, because one pipeline carries 34% of Italy's gas.
> - Defined reliability rules: high/medium/low on every data point, facts separated from assessments, stated coordinate precision, and an explicit "missing" for missing data.
> - Wrote four reports under a written editorial standard; independent reviews checked 416 claims and corrected 91, including a time-zone bug that shifted market dates by one day.
> - Built with an AI coding assistant (Claude): I set the questions, rules and review process and decided what was published.

*- Ho progettato un osservatorio OSINT open source che segue uno shock dall'evento fino a chi ne paga il costo (evento → stretto → flussi → noli → prezzi → esposizione), con oltre 50 fonti pubbliche.*
*- Ho costruito un cruscotto probabilità × impatto (sul modello ISO 31000) per 18 unità. Lettura di oggi: GNL del Qatar 24,0/25 e Hormuz 22,5 sono critici; il TransMed ha probabilità bassa ma impatto 4,3/5, perché un solo gasdotto porta il 34% del gas italiano.*
*- Ho definito le regole di affidabilità: alta/media/bassa per ogni dato, fatti separati dalle valutazioni, precisione delle coordinate dichiarata, "manca" scritto esplicitamente quando un dato manca.*
*- Ho scritto quattro report secondo uno standard editoriale scritto; le revisioni indipendenti hanno controllato 416 affermazioni e ne hanno corrette 91, compreso un errore di fuso orario che spostava di un giorno le date di mercato.*
*- Realizzato con un assistente AI (Claude): io ho definito domande, regole e processo di revisione e ho deciso cosa pubblicare.*

Fonti: `rischio.json` e `report/agenti/rischio.md` (9/11), `report/revisioni/*.md` (9–10/11).

### 5.2.6 Parole chiave per i sistemi ATS

I sistemi ATS (i programmi che filtrano i CV prima che li legga una persona) cercano le parole dell'annuncio. Tre regole:
- **Usa le parole esatte dell'annuncio**, se sono vere per te. Se l'annuncio dice "risk assessment", non scrivere solo "risk analysis".
- **Metti le parole chiave in due punti**: nella voce del progetto e nella sezione "Skills".
- **Niente tabelle, colonne o icone nel CV**: molti ATS non le leggono. PDF semplice o Word, una colonna.

| Area | Parole chiave (inglese) |
|---|---|
| Comuni a tutti | risk assessment · risk analysis · OSINT · open-source intelligence · source verification · data analysis · Python · JSON · GitHub Actions · automation · data pipeline · data visualisation · GIS · mapping · reporting · fact-checking · stakeholder communication |
| Porti | port operations · port calls · AIS · IMF PortWatch · vessel traffic · chokepoints · supply chain resilience · LNG terminal · bunkering · port security · critical infrastructure · energy transition · offshore wind ports |
| Offshore | offshore wind · auctions · CfD (contract for difference) · FID · HVDC · export cable · inter-array cable · installation vessel (WTIV) · monopile · supply chain · project milestones · grid connection · subsea infrastructure · North Sea · Baltic Sea |
| Shipping e logistica | shipping · liner shipping · transit times · freight rates · Drewry WCI · Freightos FBX · SCFI · Red Sea diversion · Cape of Good Hope · bunker fuel (VLSFO) · EU ETS · FuelEU Maritime · war-risk insurance · Joint War Committee · sanctions screening |
| Rete ed energia | security of supply · gas storage · GIE AGSI+ · TTF · interconnectors · HVDC · transmission system operator (TSO) · ENTSOG · grid resilience · hybrid threats · cable incidents · cyber security · NIS2 · Cyber Resilience Act |
| Consulenza del rischio | geopolitical risk · country risk · supply chain risk · scenario analysis · probability × impact matrix · ISO 31000 · early warning indicators · key risk indicators (KRI) · geopolitical risk index (GPR) · editorial standards |

### 5.2.7 LinkedIn: profilo e sezione Progetti

Il post di lancio è già pronto in `vetrina/linkedin.md` (aggiorna i numeri e la data). Qui servono le parti fisse del profilo.

**Headline (titolo sotto il nome, massimo 220 caratteri)**
> Risk & data analyst in the making | Ports, shipping and offshore energy | OSINT, Python, GitHub Actions | Built an open-source Geo-economic Risk Monitor | Open to roles in NL, DK and the Baltic

*Analista di rischio e dati in formazione | Porti, shipping ed energia offshore | OSINT, Python, GitHub Actions | Ho costruito un Monitor geoeconomico open source | Disponibile per ruoli in Paesi Bassi, Danimarca e Baltico*

**About (sezione "Informazioni")**
> I follow disruptions from the event to the people who pay for it. My project, the Geo-economic Risk Monitor, is an open-source map that links chokepoints, ports, energy infrastructure, freight and prices, with a source, a date and a reliability level on every number. It scores 39 European ports and 18 chokepoints every day, models transit times on 99 routes to European ports, and tracks 114 offshore wind milestones in the North Sea and the Baltic.
> I built it with an AI coding assistant. I set the questions, the data rules and the review process, and I check what gets published.
> I am looking for roles in port strategy, logistics, shipping and offshore energy in the Netherlands, Denmark and the Baltic region.

*Seguo le crisi dall'evento fino a chi ne paga il costo. Il mio progetto, il Monitor geoeconomico, è una mappa open source che collega stretti, porti, infrastrutture energetiche, noli e prezzi, con fonte, data e livello di affidabilità per ogni numero. Ogni giorno assegna un punteggio di rischio a 39 porti europei e a 18 stretti, modella i tempi di viaggio su 99 rotte verso i porti europei e segue 114 scadenze dell'eolico offshore nel Mare del Nord e nel Baltico.*
*L'ho costruito con un assistente AI. Io ho definito le domande, le regole sui dati e il processo di revisione, e controllo ciò che viene pubblicato.*
*Cerco ruoli in strategia portuale, logistica, shipping ed energia offshore nei Paesi Bassi, in Danimarca e nella regione del Baltico.*

**Sezione "In evidenza" (Featured)**, in quest'ordine: 1) la mappa, con l'immagine `docs/img/north-sea-baltic.jpg`; 2) il report Nord Europa in inglese; 3) il post di lancio. **Sezione "Progetti"**: incolla la versione C più vicina ai ruoli che cerchi.

---

## 5.3 Il discorso di 30 secondi, 2 minuti e 5 minuti

Regola: **parti da un fatto, non dalla tecnologia.** La tecnologia arriva solo se chiedono "come".

### 30 secondi (networking, inizio di una telefonata, "tell me about yourself" breve)

> I built an open-source map that follows a disruption from the event to the ports that feel it. Take Hormuz: in the last week of October about four ships a day went through, against ninety a year earlier. The map shows where that traffic went, what happened to freight, fuel and gas prices, and which European ports are most exposed. It scores 39 ports every day, and every number has a source and a date. I want to do this kind of work inside a port or an energy company.

*Ho costruito una mappa open source che segue una crisi dall'evento fino ai porti che la subiscono. Prendi Hormuz: nell'ultima settimana di ottobre passavano circa quattro navi al giorno, contro novanta un anno prima. La mappa mostra dove è andato quel traffico, cosa è successo a noli, carburante e prezzo del gas e quali porti europei sono più esposti. Ogni giorno assegna un punteggio di rischio a 39 porti, e ogni numero ha una fonte e una data. Voglio fare questo lavoro dentro un porto o un'azienda dell'energia.*

**Sullo schermo:** niente. Se sei in videochiamata, al massimo la mappa aperta sulla vista Mare del Nord e Baltico.

### 2 minuti (la risposta a "walk me through your project")

> The question behind it is simple: when something breaks at sea, who pays, and how fast? The map follows the chain: event, chokepoint, flows, freight, prices, exposure.
>
> *[screen 1: map, North Sea and Baltic view]* For this region it shows ports, offshore wind farms, HVDC links, submarine cables and live AIS positions in the Gulf of Finland. In the snapshot of 9 November, 44 of the 109 ships seen there were on Western sanction lists.
>
> *[screen 2: Terminal, Ports tab or port-risk ranking]* Every day it scores 39 European ports on probability times impact. Rotterdam and Antwerp have the highest impact but quiet signals. The highest probability is in the Russian Gulf of Finland ports. The thresholds are calibrated on PortWatch history, so a 20% drop in calls is amber, not an alarm.
>
> *[screen 3: Northern Europe report, key points]* I also write reports with a review step. In the first Northern Europe issue the review caught that Rotterdam's −10.8% week was noise: the year to date was −0.5%.
>
> Twenty-five Python collectors refresh the data every morning through GitHub Actions. I built it with an AI coding assistant. I set the questions, the rules and the review process. What I'd stress is the limits: it is not real time and it is not a forecast. It shows signals, with their sources, so a team can decide faster.

*La domanda di partenza è semplice: quando qualcosa si rompe in mare, chi paga, e quanto in fretta? La mappa segue la catena: evento, stretto, flussi, noli, prezzi, esposizione.*
*[schermo 1: mappa, vista Mare del Nord e Baltico] Per questa regione mostra porti, parchi eolici offshore, collegamenti HVDC, cavi sottomarini e posizioni AIS nel Golfo di Finlandia. Nell'istantanea del 9 novembre, 44 delle 109 navi viste lì erano nelle liste di sanzioni occidentali.*
*[schermo 2: Terminale, scheda dei porti o classifica del rischio porti] Ogni giorno assegna un punteggio probabilità per impatto a 39 porti europei. Rotterdam e Anversa hanno l'impatto più alto ma segnali tranquilli. La probabilità più alta è nei porti russi del Golfo di Finlandia. Le soglie sono tarate sulla serie PortWatch, quindi un calo del 20% degli scali è giallo, non un allarme.*
*[schermo 3: report Nord Europa, punti chiave] Scrivo anche report con una fase di revisione. Nel primo numero sul Nord Europa la revisione ha visto che il −10,8% settimanale di Rotterdam era rumore: dall'inizio dell'anno era −0,5%.*
*Venticinque script Python aggiornano i dati ogni mattina con GitHub Actions. L'ho costruito con un assistente AI: io ho definito domande, regole e processo di revisione. Sottolineo i limiti: non è in tempo reale e non è una previsione. Mostra segnali con le loro fonti, così una squadra può decidere più in fretta.*

Fonti: `baltico-sicurezza.json` (9/11), `port-risk.json` (10/11), `report/revisioni/northern-europe-2026-11.md` (10/11).

### 5 minuti (presentazione richiesta, o secondo colloquio)

Struttura in cinque blocchi da circa un minuto. Testo da dire con parole tue; qui sotto i punti in inglese e cosa mostrare.

| Minuto | Cosa dire (inglese) | Cosa mostrare |
|---|---|---|
| 0:00–1:00 · **Problem** | "A map shows where things break, not how much it matters. I wanted one place to follow a shock from the event to the exposed port, with numbers anyone can check." Hormuz: 4.4 vs 90.3 ships a day (week to 1 Nov 2026, IMF PortWatch). | Mappa, vista Europa–Medio Oriente, scheda dello Stretto di Hormuz |
| 1:00–2:00 · **Method** | The chain, the 25-field data schema, the three reliability levels, facts vs assessments. "If a number has no source and date, it is not on the map. If coverage is missing, the map says so." | `METODO.md` o la pagina dei crediti; un popup con fonte, data e affidabilità |
| 2:00–3:00 · **Your region** | Port Risk Index (39 ports), transit times (Shanghai–Rotterdam +10.5 days via the Cape), offshore wind calendar (IJmuiden Ver Gamma tender 26 Nov–10 Dec 2026), Baltic security. Choose the one closest to the company. | Terminale, scheda Nord Europa; report Nord Europa |
| 3:00–4:00 · **Quality** | Written editorial standard; independent reviews: 416 claims checked, 91 corrected across four reports. One example: the time-zone bug in prices (see 5.4, question 17). | `report/revisioni/northern-europe-2026-11.md`, tabella di verifica |
| 4:00–5:00 · **Limits and next steps** | AIS gaps, PortWatch lag of about ten days, Yahoo prices indicative only, non-commercial licences. "Inside your company I would connect it to berth schedules or internal port calls and replace the non-commercial sources." | Sezione "Limits" del README |

**Prepara lo schermo prima** (5.6, settimana 1): schede del browser già aperte, nell'ordine; zoom già sulla regione; nessuna notifica attiva. Se la connessione è lenta, tieni pronti gli screenshot in `docs/img/`.

---

## 5.4 Le 20 domande probabili, con risposte guida oneste

Le risposte sono tracce da dire con parole tue, non testi da imparare a memoria. Se non sai una cosa, dillo e spiega come la controlleresti: in un colloquio per un ruolo di rischio, sapere dove finisce la propria conoscenza è un punto a favore. Altre 10 domande, con altre risposte, sono in `vetrina/colloquio.md`.

### A. Domande tecniche

**1. "How does the daily update work?"**
> Two GitHub Actions workflows. The data one runs every day at 05:15 UTC with sixteen independent steps, including flows and sanctions, gas storage, AIS, calendar, energy, Northern Europe ports, bunker, chokepoints, wind calendar, transit times, and last the two risk scores, because they read the files just written. Each step can fail without stopping the others. Each file records its errors, and the previous data stays. Before saving, a script masks anything that looks like an API key. Prices run on weekdays at 21:30 UTC, after the US close. The git history is the archive.

*Due workflow di GitHub Actions. Quello dei dati gira ogni giorno alle 05:15 UTC con sedici passi indipendenti, tra cui flussi e sanzioni, stoccaggi di gas, AIS, calendario, energia, porti del Nord Europa, bunker, stretti, calendario dell'eolico, tempi di viaggio e per ultimi i due punteggi di rischio, perché leggono i file appena scritti. Ogni passo può fallire senza fermare gli altri. Ogni file registra i propri errori, e i dati precedenti restano. Prima di salvare, uno script maschera tutto ciò che sembra una chiave API. I prezzi girano nei giorni feriali alle 21:30 UTC, dopo la chiusura di Wall Street. La cronologia git fa da archivio.*

**2. "How do you verify a source?"**
> Five questions. Who produces it, and do they have a stake? Is it primary or a copy? Is there a second, independent source? When was it published, and when did the fact happen? How precise is it? Then a level: high, medium or low. When two sources disagree, I show both and explain why. At Hormuz, PortWatch counted 23 transits in a week where Lloyd's List Intelligence counted 116. They don't contradict each other: LLI also reconstructs ships with AIS switched off.

*Cinque domande. Chi la produce, e ha un interesse? È primaria o una copia? C'è una seconda fonte indipendente? Quando è stata pubblicata, e quando è successo il fatto? Quanto è precisa? Poi un livello: alta, media o bassa. Quando due fonti non concordano, le mostro entrambe e spiego perché. A Hormuz PortWatch ha contato 23 transiti in una settimana in cui Lloyd's List Intelligence ne contava 116. Non si contraddicono: LLI ricostruisce anche le navi con l'AIS spento.*

*Nota:* il confronto è nella stessa settimana (19–25 ottobre 2026); la revisione ha corretto proprio questo punto (`report/revisioni/hormuz-mar-rosso-2026-11.md`, riga 6). Se ti chiedono, raccontalo.

**3. "Why these weights in the risk score?"**
> Probability asks four questions. Are flows falling, 35%: that is the most direct measure of a disruption. Are there attacks nearby, 30%. Is the geopolitical climate worsening, 15%. Is the market pricing it, 20%. Impact asks how much passes through, whether there are alternatives, how much buffer there is in stocks, and how expensive it already is. Stocks get 25% because they decide whether a blockage becomes rationing. The weights are judgements, and they are written down so anyone can challenge them. The thresholds are tested: in normal chokepoints, a fall of more than 30% on a year never happened between January 2024 and February 2026.

*La probabilità fa quattro domande. I flussi calano? 35%: è la misura più diretta di una crisi. Ci sono attacchi vicino? 30%. Il clima geopolitico peggiora? 15%. Il mercato lo prezza? 20%. L'impatto chiede quanto passa, se ci sono alternative, quanto cuscinetto c'è nelle scorte e quanto costa già. Le scorte pesano il 25% perché decidono se un blocco diventa un razionamento. I pesi sono giudizi, e sono scritti perché chiunque possa contestarli. Le soglie sono provate: negli stretti "normali" un calo oltre il 30% su un anno non è mai successo tra gennaio 2024 e febbraio 2026.*

*Nota:* i pesi dell'indice dei porti sono diversi (traffico 30%, sicurezza 30%, dipendenza dagli stretti 25%, assicurazioni 15%; impatto: funzioni strategiche 45%, merci 30%, costo dell'energia 25%; `report/port-risk-method.md`). Non confonderli.

**4. "Is this a forecast? What does a score of 5 mean?"**
> No, it is not a forecast and not a statistical probability. A 5 means a disruption is in progress, or every signal is on alert. If transits are 50% or more below the reference, the probability is set to 5, because you don't estimate the probability of something that has already happened. The score says where to look. For the "when", I use scenarios with measurable signals, which the script checks every day.

*No, non è una previsione e non è una probabilità statistica. Un 5 vuol dire che c'è una crisi in corso, o che tutti i segnali sono in allerta. Se i transiti sono almeno il 50% sotto il riferimento, la probabilità è 5, perché non si stima la probabilità di un fatto già avvenuto. Il punteggio dice dove guardare. Per il "quando" uso scenari con segnali misurabili, che lo script controlla ogni giorno.*

**5. "What is the weakest part of the data?"**
> AIS. The counts only see ships with the transponder on, so shadow-fleet tankers and ships in war zones are undercounted, and Russian ports are underestimated. PortWatch also lags about ten days. Second, market prices for futures and stocks come from Yahoo Finance, which is unofficial, so I use them only as context. Third, some sources are non-commercial: fine for a personal project, not for a company.

*L'AIS. I conteggi vedono solo le navi con il transponder acceso, quindi le petroliere della flotta ombra e le navi nelle zone di guerra sono sottostimate, e i porti russi anche. PortWatch arriva con circa dieci giorni di ritardo. Secondo, i prezzi dei future e delle azioni vengono da Yahoo Finance, che non è ufficiale, quindi li uso solo come contesto. Terzo, alcune fonti hanno licenza non commerciale: vanno bene per un progetto personale, non per un'azienda.*

**6. "What would you do with more data, or a budget?"**
> Four things, in order. First, berth waiting times or terminal data: today I can only see a drop in calls, and a strike, the weather and congestion all look the same. Second, licensed satellite AIS, to see the middle of Hormuz and the Red Sea. Third, the prices I'm missing: tanker freight such as TD3C, current war-risk premiums, copper and steel for the cable and monopile chain. Fourth, a backtest: with a longer history I would count how often a "high" became a real disruption, and recalibrate.

*Quattro cose, in ordine. Primo, tempi di attesa in banchina o dati dei terminal: oggi vedo solo un calo degli scali, e uno sciopero, il meteo e la congestione hanno lo stesso aspetto. Secondo, AIS satellitare con licenza, per vedere il centro di Hormuz e del Mar Rosso. Terzo, i prezzi che mancano: noli delle petroliere come il TD3C, premi war risk aggiornati, rame e acciaio per la filiera di cavi e monopile. Quarto, un controllo a posteriori: con uno storico più lungo conterei quante volte un "alto" è diventato una crisi vera, e ricalibrerei.*

### B. Domande di dominio

**7. "What happens to Rotterdam if Hormuz closes?"**
> It isn't hypothetical: Hormuz has been effectively closed since early March 2026. What the data shows is that Rotterdam's traffic held up: 82.7 calls a day from January to the end of October, −0.5% on 2025. The shock comes through prices and energy. TTF gas was 82 €/MWh on 9 November, +164% on a year. Dutch storage was 63.5% full on 8 November, about 19 points below the five-year average. Most Dutch LNG is American, about 77% in Q1 2026, so Gate terminal keeps running, but at a higher price. Bunker fuel at Rotterdam costs 51% more than in late February, and bunker sales fell about 24% in nine months. So for the port the risk is less about ships and more about energy cost, bunker business and refinery feedstock. Saudi crude now comes via Yanbu and the Red Sea, which is actually 8.6 days shorter.

*Non è un'ipotesi: Hormuz è chiuso di fatto da inizio marzo 2026. I dati mostrano che il traffico di Rotterdam ha tenuto: 82,7 scali al giorno da gennaio a fine ottobre, −0,5% sul 2025. Lo shock passa dai prezzi e dall'energia. Il gas TTF era a 82 €/MWh il 9 novembre, +164% su un anno. Gli stoccaggi olandesi erano al 63,5% l'8 novembre, circa 19 punti sotto la media dei cinque anni. Gran parte del GNL olandese è americano, circa il 77% nel primo trimestre 2026, quindi il terminal Gate continua a lavorare, ma a un prezzo più alto. Il carburante per navi a Rotterdam costa il 51% in più di fine febbraio, e le vendite di bunker sono scese di circa il 24% in nove mesi. Quindi per il porto il rischio riguarda meno le navi e più il costo dell'energia, il business del bunker e il greggio per le raffinerie. Il greggio saudita ora arriva da Yanbu e dal Mar Rosso, un viaggio che è addirittura 8,6 giorni più corto.*

Fonti: `report/northern-europe-2026-11.md` e la sua revisione (traffico, stoccaggi, TTF, bunker; dati al 30/10–9/11), `esposizione-nord.json` (77%, IEEFA, maggio 2026: il revisore non ha potuto aprire la fonte, dillo se chiedono), `transit-times.json` (Yanbu, 10/11), `port-risk.json` (Gate 11,8 Mt/anno).

**8. "Why are offshore wind auctions failing?"**
> Because of who carries the price risk. Rounds where the developer pays the state, or gets no subsidy, failed: Denmark 3 GW with no bids in December 2024, Germany 2.5 GW in August 2025, the Netherlands 1 GW in October 2025. Where the state offers a two-sided contract for difference, auctions cleared: the UK awarded 8.4 GW at £91.20, Poland 3.4 GW, and Denmark came back in August 2026 with 1.8 GW to Vattenfall. An offshore farm is almost all upfront capital, so interest rates decide the minimum price; the US 10-year was 4.86% on 6 November. And when auctions clear, the grid is the next bottleneck: BalWin1 slipped a year.

*Dipende da chi porta il rischio di prezzo. Le aste in cui lo sviluppatore paga lo Stato, o non ha sussidi, sono fallite: Danimarca 3 GW senza offerte a dicembre 2024, Germania 2,5 GW ad agosto 2025, Paesi Bassi 1 GW a ottobre 2025. Dove lo Stato offre un contratto per differenza a due vie, le aste hanno funzionato: il Regno Unito ha assegnato 8,4 GW a 91,20 £, la Polonia 3,4 GW, e la Danimarca è tornata ad agosto 2026 con 1,8 GW a Vattenfall. Un parco offshore è quasi tutto capitale iniziale, quindi i tassi decidono il prezzo minimo; il decennale USA era al 4,86% il 6 novembre. E quando le aste funzionano, il collo di bottiglia successivo è la rete: BalWin1 è slittato di un anno.*

Fonti: `report/agenti/eolico.md` (9/11), `report/agenti/wind-calendar.md` (10/11). Nota: il tasso usato è quello USA perché i tassi BCE non sono nel file; se ti chiedono, dillo.

**9. "What is the cyber risk for offshore wind?"**
> The precedents are about remote control, not production. In February 2022 the attack on the KA-SAT satellite network cut remote control of about 5,800 Enercon turbines, which kept producing. On 29 December 2025 a destructive attack hit over 30 wind and solar farms in Poland: communication and remote control were lost, production was not interrupted (CERT Polska). So the realistic risk is losing visibility and control across many sites at once, and attacks on manufacturers and service companies. Regulation is catching up: under the Cyber Resilience Act, manufacturers must report exploited vulnerabilities from 11 September 2026.

*I precedenti riguardano il controllo remoto, non la produzione. A febbraio 2022 l'attacco alla rete satellitare KA-SAT ha tolto il controllo remoto a circa 5.800 turbine Enercon, che hanno continuato a produrre. Il 29 dicembre 2025 un attacco distruttivo ha colpito oltre 30 parchi eolici e solari in Polonia: persi comunicazione e controllo remoto, produzione non interrotta (CERT Polska). Quindi il rischio realistico è perdere visibilità e controllo su molti siti insieme, e gli attacchi a produttori e manutentori. Le regole si stanno adeguando: con il Cyber Resilience Act i produttori devono segnalare le vulnerabilità sfruttate dall'11 settembre 2026.*

Fonte: `report/agenti/cyber-energia.md`. *Nota:* non sei un esperto di sicurezza informatica. Se la domanda va sul tecnico (protocolli, segmentazione delle reti), dillo e riporta il discorso sul rischio per l'operatore.

**10. "What is the shadow fleet risk in the Baltic?"**
> Three risks: cables, spills and sanctions enforcement. In the AIS snapshot of 9 November, 44 of the 109 ships in the Gulf of Finland were on Western sanction lists. Since November 2024 six Baltic cable incidents have been recorded, mostly linked to dragged anchors. When Estlink 2 was cut, Estonia–Finland capacity fell from 1,016 to 358 MW for almost six months. About a third of Russia's seaborne oil exports passes the Danish straits. For a port or an offshore operator that means watching ship behaviour near cables and farms, AIS gaps, and GNSS jamming, which hit 214 to 246 map cells a day in the first week of November.

*Tre rischi: cavi, sversamenti e applicazione delle sanzioni. Nell'istantanea AIS del 9 novembre, 44 delle 109 navi nel Golfo di Finlandia erano nelle liste di sanzioni occidentali. Da novembre 2024 sono stati registrati sei incidenti ai cavi del Baltico, per lo più legati ad ancore trascinate. Quando Estlink 2 si è interrotto, la capacità Estonia–Finlandia è scesa da 1.016 a 358 MW per quasi sei mesi. Circa un terzo dell'export russo di petrolio via mare passa dagli Stretti danesi. Per un porto o un operatore offshore significa sorvegliare il comportamento delle navi vicino a cavi e parchi, i buchi nell'AIS e il disturbo GNSS, che ha toccato da 214 a 246 celle della mappa al giorno nella prima settimana di novembre.*

Fonti: `baltico-sicurezza.json` (9/11), revisione Nord Europa (sei incidenti), `report/agenti/nord.md` (Estlink 2), `stretti-dettaglio.json` (un terzo). *Non usare* il dato dei "292 passaggi di petroliere sanzionate nelle acque danesi nel 2025" senza dire che il revisore non ha potuto verificarlo (Euronews non raggiungibile).

**11. "Why did the Red Sea crisis hit Mediterranean ports harder than northern ones?"**
> Geography. Going round the Cape adds about 10.5 days from Shanghai to Rotterdam, Hamburg or Gdańsk, but 16 to 20 days to Genoa, Trieste or Piraeus, because Suez is the Mediterranean's front door. Today about 63% of Far East–Europe capacity is back on Red Sea services, so the average delay is about +4 days to North Europe and +6 to 7 to Italy and Greece. That is a scheduling mix, and it goes to zero when the rest of the capacity returns. For northern ports, the bigger cost item now is fuel price, not distance.

*Geografia. Girare intorno al Capo aggiunge circa 10,5 giorni da Shanghai a Rotterdam, Amburgo o Danzica, ma da 16 a 20 giorni verso Genova, Trieste o il Pireo, perché Suez è la porta d'ingresso del Mediterraneo. Oggi circa il 63% della capacità Estremo Oriente–Europa è tornato sui servizi via Mar Rosso, quindi il ritardo medio è di circa +4 giorni verso il Nord Europa e +6–7 verso Italia e Grecia. È un effetto del mix di servizi, e va a zero quando torna il resto della capacità. Per i porti del Nord oggi la voce di costo più grande è il prezzo del carburante, non la distanza.*

Fonte: `report/agenti/transit-times.md` (10/11). *Nota:* sono giorni di sola navigazione a velocità fissa; UNCTAD dà +14–24 giorni perché considera più origini e velocità. Se ti contestano il 10,5, spiega la differenza.

**12. "For a TSO: where is the bottleneck in connecting offshore wind?"**
> The grid. The delays in the calendar are mostly HVDC links and converter platforms, not vessels or turbines: BalWin1 slipped from September 2030 to September 2031, Hornsea 3's first power moved to Q1 2027 because of grid works onshore, and the Nederwiek II and IJmuiden Ver Gamma platforms are a year late. Cable makers' order books cover years of production: Prysmian about €16.5 bn, NKT €13.0 bn. A one-year platform delay blocks 2 GW of turbines that are already contracted.

*La rete. I ritardi nel calendario vengono soprattutto da collegamenti HVDC e piattaforme di conversione, non da navi o turbine: BalWin1 è slittato da settembre 2030 a settembre 2031, la prima energia di Hornsea 3 è passata al primo trimestre 2027 per i lavori sulla rete a terra, e le piattaforme di Nederwiek II e IJmuiden Ver Gamma sono in ritardo di un anno. I portafogli ordini dei produttori di cavi coprono anni di produzione: Prysmian circa 16,5 miliardi €, NKT 13,0 miliardi. Un anno di ritardo su una piattaforma blocca 2 GW di turbine già contrattate.*

Fonti: `wind-calendar.json` (10/11), `eolico-filiera.json` (9/11).

**13. "Rotterdam's calls fell 10.8% last week. Is traffic collapsing?"**
> No, and this is a good example of why the review step exists. The first draft of my report led with that number. The review compared longer windows: over 30 days Rotterdam was +2.3%, and from January to the end of October −0.5%. A single week at a big port is noisy. In the port risk index, a 20% drop happens in about one week in seven, so it's amber, not an alarm. The clear fall in the region was at Primorsk, −52% year to date, after drone strikes.

*No, ed è un buon esempio del perché esiste la revisione. La prima bozza del report partiva da quel numero. La revisione ha confrontato finestre più lunghe: su 30 giorni Rotterdam era +2,3%, e da gennaio a fine ottobre −0,5%. Una sola settimana in un grande porto è rumorosa. Nell'indice di rischio dei porti un calo del 20% capita circa una settimana su sette, quindi è giallo, non un allarme. Il calo netto della regione era a Primorsk, −52% dall'inizio dell'anno, dopo gli attacchi con droni.*

Fonte: `report/revisioni/northern-europe-2026-11.md`, correzione 1 (10/11).

**14. "How would you use this in our company?"**
> Three uses. Early warning: watch the chokepoints and routes that feed your flows, so a fall in transits shows up before the change in arrivals. Exposure: which cargo, customers or energy supplies depend on one chokepoint, pipeline or cable, and what the alternatives are. Infrastructure risk: incidents near your assets, ship behaviour, and the milestones your projects depend on. Inside the company I would connect it to internal data, like berth schedules or project dates, and replace the non-commercial sources with licensed ones.

*Tre usi. Allerta precoce: sorvegliare gli stretti e le rotte da cui dipendono i vostri flussi, così un calo dei transiti si vede prima del cambiamento negli arrivi. Esposizione: quali merci, clienti o forniture di energia dipendono da un solo stretto, gasdotto o cavo, e quali sono le alternative. Rischio infrastrutturale: incidenti vicino ai vostri impianti, comportamento delle navi e scadenze da cui dipendono i vostri progetti. In azienda lo collegherei ai dati interni, come il calendario delle banchine o le date dei progetti, e sostituirei le fonti non commerciali con fonti con licenza.*

*Adatta l'esempio:* per Kuehne+Nagel puoi dire che hai cercato i loro "Port operational updates" come fonte di congestione, ma non erano raggiungibili dall'ambiente di raccolta e sono testo, non dati (`report/agenti/port-risk.md`, sezione 4). Mostra che conosci i loro prodotti.

### C. L'AI e gli errori

**15. "What did you do yourself, and what did the AI do?"** *(la domanda chiave)*
> I'll be precise, because it matters. I defined the question and the chain, the goals, the regions and the priorities: for example, I decided to add a full North Sea and Baltic section because that's where I want to work, to put the whole site in English, and to drop a section that didn't fit the project. I chose the preferred sources and the trade-offs on licences: I kept a module on the Ukrainian front switched off until the source gives written consent. I wrote the rules: source and date on every number, three reliability levels, facts separated from assessments, one session only allowed to change the map, and a review before every report.
> The AI assistant, Claude through Claude Code, wrote almost all the code and the first drafts, working in several parallel sessions under those rules. Then separate review sessions checked every number against the data files and the original sources: 416 claims across four reports, 91 corrected. I read the reports and the reviews, spot-check numbers and decide what goes out.
> I wouldn't claim I could rewrite the map's rendering code from scratch. I can explain how every number gets there, why each rule exists, and how I'd check it. I think that's the skill that transfers: directing and checking fast automated work is becoming part of most analyst jobs.

*Sarò preciso, perché conta. Ho definito la domanda e la catena, gli obiettivi, le regioni e le priorità: per esempio ho deciso di aggiungere una sezione completa su Mare del Nord e Baltico perché è lì che voglio lavorare, di mettere tutto il sito in inglese e di togliere una sezione che non c'entrava con il progetto. Ho scelto le fonti preferite e i compromessi sulle licenze: ho tenuto spento un modulo sul fronte ucraino finché la fonte non dà un consenso scritto. Ho scritto le regole: fonte e data per ogni numero, tre livelli di affidabilità, fatti separati dalle valutazioni, una sola sessione autorizzata a modificare la mappa, una revisione prima di ogni report.*
*L'assistente AI, Claude con Claude Code, ha scritto quasi tutto il codice e le prime bozze, lavorando in più sessioni parallele secondo quelle regole. Poi sessioni di revisione separate hanno controllato ogni numero contro i file di dati e le fonti originali: 416 affermazioni in quattro report, 91 corrette. Io leggo i rapporti e le revisioni, ricontrollo i numeri a campione e decido cosa esce.*
*Non direi che saprei riscrivere da zero il codice che disegna la mappa. So spiegare come arriva ogni numero, perché esiste ogni regola e come lo controllerei. Credo che sia questa la competenza che si trasferisce: dirigere e controllare un lavoro automatico veloce sta diventando parte di quasi ogni lavoro da analista.*

*Note:*
- Le decisioni citate sono vere e documentate in `STATO.md`: sezione Nord Europa, sito in inglese e rimozione della sezione sugli analisti YouTube (10/11), modulo ISW non attivo, fonti OSINT preferite (Clément Molin, AMK Mapping).
- **Le revisioni sono fatte da sessioni AI separate**, con lo standard scritto (`report/STANDARD.md`). Se ti chiedono "who were the reviewers?", rispondi così: "Separate AI sessions acting as strict reviewers against a written standard, with no access to change the data. I read their findings and decided on the corrections." *(Sessioni AI separate che fanno da revisori severi secondo uno standard scritto, senza poter modificare i dati. Io ho letto i loro risultati e deciso le correzioni.)* Non dire "independent experts".
- Il repository parte dal 9 novembre 2026 e ha 76 commit al 10 novembre, molti con il messaggio "Lavori in corso degli agenti (da verificare)". Se qualcuno lo nota: "It was built fast, in parallel sessions. The review came after, and that's where the corrections are." *(È stato costruito in fretta, in sessioni parallele. La revisione è venuta dopo, ed è lì che ci sono le correzioni.)*
- Di' "ricontrollo a campione" solo se lo fai davvero. Prima dei colloqui, ricontrolla tu almeno 10 numeri del report Nord Europa sulla fonte originale (5.6, settimana 1): così la frase è vera e hai esempi personali da raccontare.

**16. "How do you know the AI didn't make numbers up?"**
> Three safeguards. First, a rule in every instruction: never invent a number; if data is missing, write that it's missing. Second, structure: every data point has a source link and a date, so anything can be traced. Third, a separate review that recomputes the numbers with independent code and opens the original sources. It doesn't catch everything: in the Northern Europe report some claims stayed "not verifiable" because the source blocked access, and the report says so. I prefer a visible "not verified" to a confident number.

*Tre protezioni. Primo, una regola in ogni istruzione: mai inventare un numero; se un dato manca, si scrive che manca. Secondo, la struttura: ogni dato ha il link alla fonte e la data, quindi tutto si può ricostruire. Terzo, una revisione separata che ricalcola i numeri con codice indipendente e apre le fonti originali. Non trova tutto: nel report Nord Europa alcune affermazioni sono rimaste "non verificabili" perché la fonte bloccava l'accesso, e il report lo dice. Preferisco un "non verificato" visibile a un numero sicuro di sé.*

**17. "Tell me about a mistake you found."**
> The best one was in the price data. The review of the Hormuz report found that the price script converted Yahoo's timestamps with New York's current UTC offset, winter time, even in summer months. So from 8 March to 1 November 2026 every trading day for Brent, TTF and the others was recorded one day early. Eleven values fell on a Sunday, which is how it was spotted. The report had the date of Brent's peak close wrong by one day: 31 March, not 30. We fixed the script to use the exchange's own time zone, corrected the report and stated the error in the method section. Small error, but in a market report a wrong date breaks the link between an event and a price move.

*Il migliore era nei dati dei prezzi. La revisione del report su Hormuz ha trovato che lo script dei prezzi convertiva gli orari di Yahoo con lo scarto UTC attuale di New York, l'ora solare, anche nei mesi estivi. Così dall'8 marzo al 1° novembre 2026 ogni seduta di Brent, TTF e delle altre serie era registrata un giorno prima. Undici valori cadevano di domenica, ed è così che è emerso. Il report aveva sbagliato di un giorno la data della massima chiusura del Brent: 31 marzo, non 30. Abbiamo corretto lo script perché usi il fuso della borsa, corretto il report e dichiarato l'errore nella sezione sul metodo. Un errore piccolo, ma in un report di mercato una data sbagliata rompe il legame tra un evento e un movimento di prezzo.*

Fonte: `report/revisioni/hormuz-mar-rosso-2026-11.md` (9/11); correzione in `raccolta/scarica_mercati.py` (righe 98–107). *Perché funziona:* mostra un controllo di plausibilità (sedute di domenica), la correzione alla radice e la trasparenza.

**18. "Have you had a security problem?"**
> Yes, a small one. A free API key for the gas storage data ended up in a public file, inside an error message written by a collector. I removed it, added a step that masks anything that looks like a key before every save, and the key has to be regenerated, because it stays in the git history. The lesson: in a public repository, errors and logs are outputs too, and they need the same checks as the data.

*Sì, uno piccolo. Una chiave API gratuita per i dati degli stoccaggi di gas è finita in un file pubblico, dentro un messaggio d'errore scritto da uno script di raccolta. L'ho tolta, ho aggiunto un passo che maschera tutto ciò che sembra una chiave prima di ogni salvataggio, e la chiave va rigenerata, perché resta nella cronologia git. La lezione: in un repository pubblico anche gli errori e i log sono un output, e vanno controllati come i dati.*

*Prima di qualsiasi colloquio:* **rigenera davvero la chiave AGSI** sul sito di GIE e aggiorna il segreto su GitHub (`STATO.md` la segnala ancora da rigenerare al 9/11). Così puoi dire "I regenerated it" e non "it has to be". Fonte: `STATO.md`, commit "Sicurezza: tolta una chiave API finita in un messaggio d'errore".

### D. Motivazione e profilo

**19. "Why this region, and why does the project start from Italy?"**
> I started from what I knew best: Italian ports and gas routes, where one pipeline, TransMed, carries 34% of the gas entering Italy. The method is the same anywhere, and I've applied it to the North Sea and the Baltic: 30 ports, offshore wind, HVDC links, cables, the shadow fleet. This region is where shipping, energy transition and security meet: the busiest ports, most of Europe's offshore wind, and the most active hybrid threats. That's the combination I want to work on.

*Sono partito da ciò che conoscevo meglio: i porti e le rotte del gas italiani, dove un solo gasdotto, il TransMed, porta il 34% del gas che entra in Italia. Il metodo è lo stesso ovunque, e l'ho applicato al Mare del Nord e al Baltico: 30 porti, eolico offshore, collegamenti HVDC, cavi, flotta ombra. Questa regione è dove si incontrano shipping, transizione energetica e sicurezza: i porti più trafficati, la maggior parte dell'eolico offshore europeo e le minacce ibride più attive. È questa combinazione su cui voglio lavorare.*

**20. "Can you code? What did you learn?"**
> I can read Python, follow the data from a collector to the map, and run and fix the pipeline when a step fails. I'm not a software engineer and I don't present myself as one. What I learned is mostly analytical: a weekly number at a big port is noise; two sources that disagree often measure different things; and an explicit rule for missing data saves you from your own enthusiasm. On the technical side I'm improving my Python and SQL, because I want to be able to check the code, not only the output.

*So leggere Python, seguire i dati da uno script di raccolta fino alla mappa, e lanciare e sistemare la catena quando un passo fallisce. Non sono un ingegnere del software e non mi presento come tale. Quello che ho imparato è soprattutto analitico: un numero settimanale in un grande porto è rumore; due fonti in disaccordo spesso misurano cose diverse; e una regola esplicita per i dati mancanti ti salva dal tuo stesso entusiasmo. Sul piano tecnico sto migliorando Python e SQL, perché voglio poter controllare il codice, non solo il risultato.*

*Nota:* adatta la prima frase a quello che sai fare davvero. Se oggi non sai lanciare uno script, impara a farlo nella settimana 1 (`python3 raccolta/rotte/tempi.py`, `python3 raccolta/porti/rischio_porti.py`: girano senza rete e in pochi secondi). Se dici "I'm improving my SQL", deve essere vero: iscriviti a un corso.

---

## 5.5 Cosa NON dire, e come tenere vivo il progetto

### Frasi da evitare

| Non dire | Perché | Di' invece |
|---|---|---|
| "Real-time monitoring" | I dati arrivano una volta al giorno; PortWatch ha circa dieci giorni di ritardo; l'AIS è un'istantanea | "Updated daily from open sources, with the date of each data point" |
| "It predicts disruptions" / "forecast" | Il punteggio non è una probabilità statistica; gli scenari non hanno probabilità numeriche | "It scores current signals and shows what to watch" |
| "It tracks all ships" | L'AIS gratuito copre bene il Baltico e male il centro di Hormuz; le navi con AIS spento mancano | "It shows AIS positions where free coverage exists, and says where it doesn't" |
| "I built an AI that..." | Non c'è un modello di AI nel progetto: l'AI ha aiutato a scriverlo | "I built it with an AI coding assistant" |
| "I coded everything" | Non è vero e si vede dalla cronologia | La risposta 15 |
| "Reviewed by independent experts" | I revisori sono sessioni AI separate | "Independent review sessions against a written standard" |
| "Hormuz traffic is down 95%" senza data | Il numero cambia ogni settimana | "−95% in the week to 1 November 2026, IMF PortWatch" |
| Numeri che il revisore non ha potuto verificare, presentati come certi | Es. 292 passaggi nelle acque danesi; quota USA del GNL UE 58% | Citali con la fonte e "not independently verified" |
| "Kerch is closed" partendo da zero transiti AIS | Zero segnali non vuol dire zero navi | "No AIS signals recorded" |
| "Used by companies" / "used by analysts" | Non risulta da nessun file | Niente: se qualcuno ti dà un parere, cita quello |
| "Comprehensive", "cutting-edge", "unique" | Parole vuote; un selezionatore le salta | Un numero con data |
| "The data is free to use" | Il codice è MIT, i dati no; alcune fonti sono non commerciali | "Code MIT, data under each source's licence" |
| Giudizi su un'azienda a cui ti candidi ("Sif is going bankrupt") | Il file dice "dubbi sulla continuità aziendale", non fallimento | Riporta il fatto con la fonte, senza giudicare |

E due cose da non fare:
- **Non condividere dati non commerciali** (TeleGeography, OpenSanctions, Global Fishing Watch) come se un'azienda potesse usarli così come sono.
- **Non fare il colloquio sul codice** se il ruolo è di analisi. Porta sempre il discorso su decisione, rischio e verifica.

### Come tenere vivo il progetto durante la ricerca

Un progetto fermo da tre mesi sembra abbandonato. Bastano poche ore al mese, con un calendario fisso.

| Quando | Cosa | Tempo |
|---|---|---|
| Ogni lunedì | Aprire GitHub → Actions: i due workflow sono verdi? Leggere il campo `errori` dei file principali (`port-risk.json`, `rischio.json`, `portwatch.json`) | 15 min |
| Ogni 2 settimane | Un post LinkedIn breve: un numero, un grafico o uno screenshot, una lettura, un limite. Esempi di spunti con data già nei file: esito della gara IJmuiden Ver Gamma (domande dal 26/11 al 10/12/2026); risultati britannici AR8 (finestra dal 27/11/2026 al 17/2/2027); prenotazioni della dorsale danese dell'idrogeno (scadenza 1/12/2026); assemblea di Sif (22/12/2026) | 1 ora |
| Ogni mese | Un numero del report "Northern Europe: Ports and Energy" (il n. 2 a dicembre), con revisione e riquadro "Review", in inglese | 1–2 giorni |
| Ogni mese, dopo il report | Aggiornare i numeri del CV e del profilo LinkedIn con la nuova data; aggiornare `vetrina/` | 30 min |
| Ogni mese | Scrivere 3 righe in un registro: cosa è cambiato, cosa è stato corretto. Serve nei colloqui ("what changed since you started?") | 15 min |
| Prima di ogni colloquio | Ricontrollare i 5 numeri che userai, aprire le schede, fare uno screenshot della classifica dei porti del giorno | 30 min |

**Messaggi dei commit.** Da ora in poi, messaggi chiari e in inglese ("Port risk: added Esbjerg congestion note"), non "Lavori in corso (da verificare)". Chi apre la cronologia legge anche quelli.

---

## 5.6 Piano di 4 settimane

Obiettivo: alla fine delle quattro settimane, profilo pronto, almeno 15 candidature mirate, almeno 10 contatti diretti con persone del settore, un secondo report pubblicato e il discorso provato ad alta voce.

### Settimana 1 — Mettere in ordine

| Giorno | Attività | Risultato |
|---|---|---|
| Lun | Rigenerare la chiave AGSI e aggiornare il segreto su GitHub. Controllare che i workflow siano verdi | Risposta 18 vera al passato |
| Lun–Mar | Aggiornare i numeri in `vetrina/cv.md` e `vetrina/linkedin.md` (25 script, 66 file, livelli ricontati), con la data | Testi coerenti con il sito |
| Mar | Ricontrollare tu, sulla fonte originale, 10 numeri del report Nord Europa (per esempio scali di Rotterdam, stoccaggi, TTF, Estlink 2, BalWin1). Annotare cosa hai trovato | "I spot-check" diventa vero, con esempi tuoi |
| Mer | Imparare a lanciare in locale `tempi.py` e `rischio_porti.py` e il sito (`cd docs && python3 -m http.server 8000`) | Risposta 20 vera |
| Gio | Scrivere 3 CV di base (porti, offshore, shipping) con le versioni B o C del 5.2; aggiornare il profilo LinkedIn (titolo, Informazioni, In evidenza) | CV pronti, profilo pronto |
| Ven | Provare ad alta voce, registrandoti, il discorso da 30 secondi e da 2 minuti. Preparare le schede del browser per la demo | Discorso sotto i tempi |

### Settimana 2 — Lancio e lista dei bersagli

| Attività | Risultato |
|---|---|
| Pubblicare il post di lancio (`vetrina/linkedin.md`) di martedì o mercoledì mattina, con i numeri aggiornati e il link al report in inglese | Post pubblico |
| Fare una lista di 20 organizzazioni in 5 gruppi: autorità portuali (Port of Rotterdam, Port Esbjerg, Klaipėda, Gdańsk, North Sea Port...), offshore (Ørsted, Vattenfall, Van Oord, DEME, Cadeler), shipping e logistica (Maersk, DFDS, Kuehne+Nagel), reti (TenneT, Energinet), consulenza del rischio | Foglio con nome, ruolo aperto, persona da contattare |
| Per ognuna, una riga: "che cosa del Monitor riguarda loro" (es. Esbjerg: rischio porti 3,2 in salita da 2,0 e scali −42,9% sui 28 giorni precedenti; Rotterdam: impatto 5,0; Vattenfall: 1,8 GW vinti in Danimarca) | Gancio per ogni messaggio |
| Inviare le prime 5–7 candidature, con la versione del CV giusta | Candidature inviate |
| Inviare 5 messaggi diretti a persone del settore (modello qui sotto) | 5 contatti |

**Modello di messaggio a una persona del settore** (massimo 600 caratteri; personalizza la seconda frase)
> Hi [name], I'm Gabriele, looking for roles in ports and offshore energy in [country]. I've built an open-source risk monitor for North Sea and Baltic ports; for [company/port] it flags [one specific, dated finding]. I'd really value 15 minutes of your view on what you would check first, or what I'm missing. Link: [map]. Thank you!

*Ciao [nome], sono Gabriele e cerco ruoli nei porti e nell'energia offshore in [Paese]. Ho costruito un osservatorio open source del rischio per i porti del Mare del Nord e del Baltico; per [azienda/porto] segnala [un risultato specifico, con data]. Mi sarebbe molto utile un tuo parere di 15 minuti su cosa controlleresti per primo, o su cosa mi manca. Link: [mappa]. Grazie!*

Esempio di gancio per Port Esbjerg: "it flags Esbjerg at 3.2, rising from 2.0, with calls at 2.0 a day against 3.5 in the previous 28 days (IMF PortWatch to 30 Oct 2026)". Controlla prima che il dato sia ancora quello.

### Settimana 3 — Approfondire sui bersagli migliori

| Attività | Risultato |
|---|---|
| Per le 3 aziende che preferisci, preparare una scheda di una pagina "What the Monitor says about you" (3 numeri con data, 1 rischio, 1 cosa da osservare, 1 limite dei dati). Da portare al colloquio o allegare a un messaggio di ringraziamento | 3 schede |
| Provare le 20 domande del 5.4 con un amico o registrandoti; cronometrare: ogni risposta sotto i 90 secondi | Risposte fluide |
| Secondo post LinkedIn, su un fatto con data (es. la gara IJmuiden Ver Gamma, aperta dal 26/11 al 10/12/2026: "the first Dutch tender since Nederwiek I-A got zero bids") | Post 2 |
| Altre 5–7 candidature e 5 messaggi; rispondere a chi ha commentato il post di lancio | Totale: circa 12 candidature, 10 contatti |

### Settimana 4 — Secondo report e seguito

| Attività | Risultato |
|---|---|
| Preparare il n. 2 di "Northern Europe: Ports and Energy" (dicembre): stessi capitoli, numeri nuovi, revisione e riquadro "Review", più una sezione su ciò che è cambiato rispetto al n. 1 | Report 2 pubblicato |
| Aggiornare CV e LinkedIn con i numeri del report 2 e con la data | Profilo aggiornato |
| Seguito: un messaggio breve a chi non ha risposto dopo 7–10 giorni, con il link al report nuovo (un motivo nuovo per scrivere) | Seguiti inviati |
| Ultime candidature (per arrivare almeno a 15) | Obiettivo raggiunto |
| Bilancio: quali gruppi rispondono di più? Quale numero o quale schermata ha funzionato nei colloqui? Spostare il tempo su quel gruppo nelle settimane successive | Piano per il mese 2 |

### Lista di controllo prima di ogni colloquio

- [ ] I 5 numeri che userai sono ricontrollati nel file, con la data di oggi.
- [ ] Schede aperte nell'ordine: mappa (vista Mare del Nord e Baltico) → Terminale (porti o Nord Europa) → report in inglese → una revisione in `report/revisioni/`.
- [ ] Screenshot di riserva in `docs/img/`.
- [ ] La risposta 15 (AI) detta ad alta voce almeno una volta il giorno prima.
- [ ] Un esempio di errore (risposta 17) e uno di limite dei dati (risposta 5) pronti.
- [ ] Tre domande da fare a fine colloquio (in `vetrina/colloquio.md`), più una legata all'azienda: "Which data do you rely on today to anticipate [arrivals / grid connection dates / vessel availability], and where is it weakest?" *(Su quali dati vi basate oggi per anticipare [arrivi / date di connessione alla rete / disponibilità delle navi], e dove sono più deboli?)*

---

*Fonti del capitolo: `vetrina/cv.md`, `vetrina/linkedin.md`, `vetrina/colloquio.md`, `README.md`, `STATO.md` (9/11/2026); `report/agenti/port-risk.md`, `transit-times.md`, `wind-calendar.md` (10/11/2026); `report/agenti/rischio.md`, `nord.md`, `eolico.md` (9/11/2026); `report/agenti/cyber-energia.md`; `report/revisioni/*.md` (9–10/11/2026); `report/northern-europe-2026-11.md`; `report/metodo-rischio.md`; `report/port-risk-method.md`; `report/STANDARD.md`; `raccolta/AGENTI.md`; `.github/workflows/*.yml`; file in `docs/data/` con le date indicate nel testo. Conteggi di file, script, livelli e commit fatti sul repository il 10/11/2026.*
