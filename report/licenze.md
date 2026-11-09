# Audit delle licenze delle fonti

Rapporto dell'agente Vetrina e licenze, 9 novembre 2026.
Base: `STATO.md`, `METODO.md`, `raccolta/AGENTI.md`, `docs/data/manifest.json`, i rapporti in `report/agenti/*.md` e il campo `fonti[]` di ogni file in `docs/data/` (42 file).

> **Avvertenza.** Non sono un avvocato e questo non è un parere legale. È una lettura delle licenze come le dichiarano le fonti, al 9/11/2026, per un progetto personale pubblicato in un repository pubblico. Dove una licenza è ambigua lo scrivo. Per un uso commerciale, o se un titolare dei diritti scrive, serve un parere vero.

## 1. Il punto di partenza: cosa vuol dire "non commerciale" qui

Il progetto è personale, gratuito, senza pubblicità né clienti. Le licenze CC BY-NC dicono che è commerciale un uso "principalmente diretto a ottenere un vantaggio commerciale o un compenso". Un portfolio personale usato per cercare lavoro di solito **non** rientra in questa definizione, ma è una zona grigia.

La conseguenza pratica è più importante della teoria: **se Gabriele usa l'osservatorio, o una sua copia, dentro un'azienda (un porto, un operatore logistico od offshore), quello è uso commerciale.** Le fonti NC (TeleGeography, OpenSanctions, Global Fishing Watch, Benden su Zenodo, il dataset di Petro Ivaniuk, SIPRI, IFES) andrebbero tolte o sostituite. Conviene saperlo dire in un colloquio.

Seconda conseguenza: il **codice** può essere MIT, ma i **dati** no. In `docs/data/` convivono file CC BY, ODbL (share-alike per le banche dati), CC BY-NC-SA (share-alike e non commerciale) e file senza licenza aperta. Per questo ho separato `LICENSE` (codice) e `DATA_LICENSES.md` (dati, file per file).

Terzo punto: la cronologia di git è pubblica e "è anche l'archivio storico" (README). Quello che è già stato pubblicato resta nella cronologia, anche se si toglie un file oggi.

## 2. Tabella delle fonti

Legenda rischio: **basso** = licenza aperta e rispettata, o solo fatti citati con link; **medio** = licenza con condizioni (NC, SA) o termini ambigui, rispettabili con qualche intervento; **alto** = termini che vietano o non autorizzano quello che il repository fa oggi (copiare e ridistribuire).

### 2.1 Cartografia e infrastrutture

| Fonte | File | Licenza | Cosa permette | Obblighi | Ripubblicare nel repo | Rischio | Azione |
|---|---|---|---|---|---|---|---|
| Natural Earth | world.json, medio-oriente.json, labels.json, ferrovie.json, filtro di fronte-storico.json | Pubblico dominio | Tutto | Nessuno (citare è cortesia) | Sì | basso | Nessuna |
| Global Energy Monitor (oleodotti, gasdotti, GNL, nucleare) | linee.json, condotte.json, terminali-gnl.json, nucleare.json, gas-italia.json (coordinate) | CC BY 4.0 per i dati dei tracker; CC BY-NC-SA solo per i testi di gem.wiki | Uso anche commerciale, modifiche | Attribuzione a GEM con link e versione | Sì | basso | In `linee.json` e `condotte.json` il campo `licenza` cita solo gem.wiki (CC BY-NC-SA): correggerlo in "CC BY 4.0 (Global Energy Monitor)" se non si usano testi di gem.wiki (richiesta alla sessione Raccolta, file non toccati qui) |
| Benden (2022), Global Shipping Lanes v1.3.1 | rotte.json | **Dichiarata in tre modi**: CC BY 4.0 (LICENSE su GitHub), CC BY-SA (README), CC BY-NC 4.0 (Zenodo). Tracciati derivati da una carta CIA (pubblico dominio) | Con la lettura più restrittiva: uso non commerciale con attribuzione | Citazione con DOI 10.5281/zenodo.6361763 | Sì, per uso non commerciale | medio | Applicare la più restrittiva (CC BY-NC 4.0) finché l'autore non chiarisce. Chiedere all'autore quale vale (issue su GitHub). Alternativa: ridisegnare le rotte principali dalla carta CIA "World Oil Transit Chokepoints" (pubblico dominio) |
| World Port Index (NGA) | fissi.json (porti), iran.json | Pubblico dominio (governo USA) | Tutto | Nessuno | Sì | basso | 321 link puntano a un repository di terzi (`Yusnelkis/world-port-index-dashboard`), non a NGA: sostituire il link con `msi.nga.mil` (Pub. 150) |
| OurAirports | fissi.json, iran.json, italia.json | Pubblico dominio | Tutto | Nessuno | Sì | basso | Nessuna |
| Wikidata | fissi.json, iran.json, coordinate varie | CC0 | Tutto | Nessuno | Sì | basso | Nessuna |
| Wikipedia (coordinate, liste) | interconnessioni.json, ucraina-storico.json, calendario | CC BY-SA 4.0 per i testi | Si usano fatti (date, coordinate), non testi | Se si copia testo: attribuzione e stessa licenza | Sì (fatti) | basso | Non copiare frasi; citare la pagina |
| TeleGeography, Submarine Cable Map | cavi.json, cavi-incidenti.json (id) | **CC BY-NC-SA 3.0** | Uso non commerciale, anche modificato | Attribuzione "TeleGeography", **non commerciale**, **stessa licenza per il derivato** | Sì, se `cavi.json` è dichiarato CC BY-NC-SA 3.0 | medio | Dichiarare `cavi.json` CC BY-NC-SA 3.0 in DATA_LICENSES.md (fatto) e didascalia "Dati TeleGeography, CC BY-NC-SA" sulla mappa. L'API v3 non è documentata: scaricare con moderazione (settimanale) |
| OpenStreetMap via tessere OpenInfraMap | rete-elettrica.json, interconnessioni.json | **ODbL 1.0** | Uso anche commerciale | Attribuzione "© OpenStreetMap contributors"; **la banca dati derivata va offerta sotto ODbL** | Sì, se il file è dichiarato ODbL | medio | Dichiarare i due file ODbL (fatto in DATA_LICENSES.md). Le tessere vettoriali di OpenInfraMap sono pensate per la loro mappa, non per lo scaricamento: passare a Overpass da GitHub Actions o a un estratto Geofabrik, e citare anche OpenInfraMap |
| PyPSA-Eur Prebuilt Network (Zenodo) | interconnessioni.json | ODbL 1.0 (dati OSM) | Come sopra | Attribuzione PyPSA-Eur e OSM | Sì | basso | Citare il record Zenodo 23896564 |
| OpenStreetMap Nominatim | coordinate di ucraina-storico.json | ODbL 1.0; policy di Nominatim (max 1 richiesta/s, niente uso massivo) | Coordinate puntuali | Attribuzione OSM | Sì | basso | Citare "© OpenStreetMap contributors" |
| Epoch AI | ai.json | CC BY 4.0 per i dataset di Epoch; i post del blog sono citati | Uso anche commerciale | Attribuzione | Sì | basso | Nessuna |

### 2.2 Navi, flussi, sanzioni

| Fonte | File | Licenza | Cosa permette | Obblighi | Ripubblicare | Rischio | Azione |
|---|---|---|---|---|---|---|---|
| Digitraffic (Fintraffic) | navi.json | CC BY 4.0 | Uso anche commerciale | "Fonte: Fintraffic / digitraffic.fi, licenza CC BY 4.0" | Sì | basso | Usare la formula di attribuzione indicata da Fintraffic |
| aisstream.io | navi.json | Termini del servizio (nessuna licenza aperta sui dati) | Uso tramite chiave personale | Rispettare i termini | Da verificare: ripubblicare posizioni grezze può non essere consentito | medio | Leggere i termini; pubblicare solo conteggi per area e poche posizioni, non flussi grezzi |
| Global Fishing Watch API v3 | navi.json | CC BY-NC 4.0 + termini dell'API | Uso non commerciale | Attribuzione GFW, non commerciale | Sì, non commerciale | medio | Dichiarare la parte GFW CC BY-NC; in un uso aziendale serve un accordo con GFW |
| USNI News Fleet Tracker | navi.json | Copyright | Si estraggono solo fatti (nave, area) | Link all'articolo | Sì (fatti) | basso | Nessuna |
| IMF PortWatch | portwatch.json | Dati pubblici FMI; termini d'uso FMI (riuso con citazione) | Riuso con citazione | "Source: IMF PortWatch" | Sì | basso | Verificare che i termini di PortWatch non limitino l'uso commerciale prima di usarlo in azienda |
| Drewry WCI | noli.json | © Drewry | Citare il valore pubblicato | Fonte e data | Ultimo valore sì; **costruire uno storico** dai valori settimanali è più delicato | medio | Tenere nel repo solo l'ultimo valore con data e link; lo storico solo se Drewry lo consente |
| Freightos FBX | noli.json | © Freightos / Baltic Exchange; dati estratti dalla pagina "Terminal" | Uso editoriale con citazione | Fonte | Lo storico di circa 3 mesi copiato dalla pagina è una copia della loro serie | medio | Come sopra: solo ultimo valore; chiedere a Freightos (hanno un programma per media e ricerca) |
| Shanghai Shipping Exchange (SCFI, CCFI) | noli.json | © SSE | Citare il valore | Fonte | Ultimo valore sì | medio | Solo ultimo valore e variazione |
| Baltic Dry via Trading Economics | noli.json | © Baltic Exchange; i termini di Trading Economics vietano lo scraping e la ridistribuzione | Nulla di esplicito | — | **No** in forma automatica | **alto** | Togliere la raccolta automatica da Trading Economics; citare il BDI a mano da un articolo di stampa con link, oppure sostituirlo con un indice gratuito (vedi §4) |
| Caldara e Iacoviello, GPR | gpr.json | Dati liberi per la ricerca, con citazione (AER 2022) | Ricerca e analisi | Citare l'articolo | Sì | basso | Nessuna |
| OFAC SDN | sanzioni-navi.json | Pubblico dominio | Tutto | Nessuno | Sì | basso | Nessuna |
| UK Sanctions List (FCDO) | sanzioni-navi.json | Open Government Licence v3.0 | Uso anche commerciale | "Contains public sector information licensed under the Open Government Licence v3.0" | Sì | basso | Aggiungere la formula OGL |
| OpenSanctions (`eu_journal_sanctions`) | sanzioni-navi.json | **CC BY-NC 4.0** | Uso non commerciale | Attribuzione, non commerciale | Sì, non commerciale | medio | Sostituire con la fonte primaria: atti dell'UE su EUR-Lex (riuso libero, decisione 2011/833/UE) o la EU Sanctions Map. Così il file torna riusabile |

### 2.3 Energia, scorte, macro, paesi

| Fonte | File | Licenza | Ripubblicare | Rischio | Azione |
|---|---|---|---|---|---|
| ENTSOG Transparency Platform | gas-italia.json | Dati pubblici, riuso con citazione | Sì | basso | Citare "ENTSOG Transparency Platform" |
| GIE AGSI+ | scorte.json | Uso libero con citazione (condizioni GIE) | Sì | basso | Citare GIE AGSI+. **Problema di sicurezza, non di licenza: la chiave AGSI è nella cronologia git, va rigenerata** |
| Eurostat | scorte.json, paesi.json, calendario.json | CC BY 4.0 | Sì | basso | Citare Eurostat e il codice del dataset |
| EIA | scorte.json, calendario.json, (paesi.json con chiave) | Pubblico dominio | Sì | basso | Nessuna. Alcune pagine "Today in Energy" sono citate, non copiate: va bene |
| USDA FAS PSD | scorte.json | Pubblico dominio | Sì | basso | Nessuna |
| FMI (DataMapper WEO, IRFCL) | paesi.json, scorte.json | Termini FMI: riuso con citazione; l'uso commerciale può richiedere permesso | Sì (estratti) | basso | Citare "IMF, World Economic Outlook, ottobre 2026" |
| Banca Mondiale (WDI) | paesi.json | CC BY 4.0 | Sì | basso | Nessuna |
| Our World in Data / Energy Institute | paesi.json | CC BY 4.0 (OWID); dati di base Energy Institute, citare | Sì | basso | Citare anche Energy Institute Statistical Review |
| SIPRI Milex | paesi.json | Uso libero non commerciale con citazione (non CC) | Sì, estratti per paese | basso-medio | Non ripubblicare il file xlsx intero; citare SIPRI |
| UN Comtrade (API di anteprima) | paesi.json | Termini UN Comtrade: consultazione libera, riuso con citazione; vietata la ridistribuzione massiva | Sì, pochi valori per paese | basso | Tenere solo gli aggregati che servono |
| IEA (factsheet Hormuz) | stretti-dettaglio.json | CC BY 4.0 (dichiarato sul PDF) | Sì | basso | Nessuna |
| Fed, BLS, BEA, OFAC | calendario.json | Pubblico dominio | Sì | basso | Nessuna |
| BCE | calendario.json | Riuso con citazione | Sì | basso | Citare "Fonte: BCE" |
| Bank of England, Bank of Japan | calendario.json | Termini dei siti, riuso con citazione | Sì (date, tassi) | basso | Nessuna |
| IFES ElectionGuide | calendario.json | Termini IFES: uso non commerciale con citazione (da verificare) | Sì (date) | basso | Le date delle elezioni sono fatti: in caso di dubbio citarle da fonti ufficiali |

### 2.4 Mercati

| Fonte | File | Licenza | Ripubblicare | Rischio | Azione |
|---|---|---|---|---|---|
| U.S. Department of the Treasury (curva dei rendimenti) | prezzi.json (tassi, curva) | Pubblico dominio | Sì | basso | Nessuna |
| **Yahoo Finance** (chart API non documentata) | prezzi.json (25 serie su 29: indici, titoli, materie prime, EUR/USD, cripto); ucraina-storico (solo per il rapporto) | **Nessuna licenza**: i termini di Yahoo consentono l'uso personale e vietano la ridistribuzione; molti dati sono a loro volta licenziati dalle borse (S&P, ICE per Brent e TTF, Nasdaq) | **No** per le serie complete scaricate ogni giorno e salvate in un repository pubblico | **alto** | Vedi §3 |
| Stampa finanziaria (mercati.json) | mercati.json | Copyright degli editori; si riportano valori con link | Sì (fatti puntuali) | basso | Nessuna |

### 2.5 Ucraina e militare

| Fonte | File | Licenza | Ripubblicare | Rischio | Azione |
|---|---|---|---|---|---|
| **@Majakovsk73**, mappa "Ucraina (2025)" su Google My Maps | fronte.json (28 aree, 91 punti) | **Nessuna licenza dichiarata = tutti i diritti riservati** | **No**, senza permesso: le aree sono copiate dai poligoni dell'autore | **alto** | Chiedere il permesso (§5). Nel frattempo: tenere il link alla sua mappa e togliere i poligoni dal repo, oppure tenerli solo con un permesso scritto |
| **DeepStateMap** (API dello storico) | fronte-storico.json | Diritti riservati; accordo di licenza (`deepstatemap.live/license-en.html`): API gratuita per volontariato e difesa dell'Ucraina, uso commerciale solo con permesso, **vietato ridistribuire o fare da proxy ai dati dell'API**; materiali visivi e testuali usabili citando DeepState con link | Salvare ogni mese i poligoni (anche semplificati) in un file pubblico è vicino alla "ridistribuzione" vietata | **alto** | Scrivere a DeepState per un permesso. Senza permesso: pubblicare solo i km² e le variazioni mensili (dati derivati, non le geometrie) e mostrare le aree con un link o un'immagine citata |
| **ISW e AEI Critical Threats** (ArcGIS) | fronte-storico.json (2 istantanee del 2022 e confronti) | © ISW/CTP, nessuna licenza aperta | Uso limitato con citazione | medio | Tenere solo le 2 istantanee del 2022 e i confronti in km², citare ISW/CTP; chiedere se servono di più |
| **Petro Ivaniuk (piterfm)**, *Massive Missile Attacks on Ukraine* (Kaggle), letto dalla copia di Narretz/sbs-stats | ucraina-storico.json | **CC BY-NC-SA 4.0** (dichiarata dai progetti che lo riusano; la pagina Kaggle non è stata letta direttamente) | Sì, se il file derivato è CC BY-NC-SA 4.0 | medio | Verificare la licenza sulla pagina Kaggle; dichiarare `ucraina-storico.json` CC BY-NC-SA 4.0 (fatto); citare "Petro Ivaniuk, Kaggle" e la copia usata |
| Kyiv Independent, Moscow Times, Meduza, Reuters/AP (via ristampe) | ucraina-storico.json, eventi.json | Copyright: link e brevi estratti | Sì, se gli estratti sono brevi (diritto di citazione) | basso-medio | Tenere gli estratti nelle `note` sotto una o due frasi |
| Clément Molin, AMK Mapping (Telegram), X, siti di analisi | eventi.json, fronte | Copyright degli autori; si usano fatti con link | Sì (fatti) | basso | Nessuna |

### 2.6 Notizie e video

| Fonte | File | Licenza | Ripubblicare | Rischio | Azione |
|---|---|---|---|---|---|
| Google News RSS (UKMTO, JMIC, MARAD, DeepState, ISW e altri, 35 feed) | notizie.json | Titoli e sommari degli editori | Titolo + link sì; sommari brevi | basso-medio | Tenere solo titolo, data, editore e link; tagliare i sommari |
| YouTube, 5 canali di analisti (RSS) | analisti.json | Tutti i diritti riservati | Titolo, link e miniatura (URL) sì; descrizioni fino a 600 caratteri sono una copia | basso-medio | Ridurre la descrizione a circa 200 caratteri o salvare solo i temi riconosciuti |

## 3. Yahoo Finance: cosa fare

**Il problema.** `prezzi.json` contiene circa un anno di chiusure giornaliere (260–397 punti per serie) di 25 strumenti presi da Yahoo, scaricati ogni sera da GitHub Actions e salvati in un repository pubblico, con la cronologia di git che fa da archivio. È una ridistribuzione sistematica di dati che Yahoo non licenzia e che in parte appartengono a S&P Dow Jones Indices, ICE (Brent, TTF) e Nasdaq. Il rischio pratico (che qualcuno se ne accorga e scriva) è basso per un progetto piccolo, ma il rischio di immagine in un colloquio è reale: è il primo punto debole che un recruiter tecnico noterebbe.

**Proposta in tre livelli.**

1. **Serie ufficiali e riusabili, da tenere complete nel repository:**
   - Tassi USA: Tesoro USA (già così).
   - Brent, WTI, Henry Hub spot giornalieri: **EIA** (pubblico dominio; API v2 con chiave gratuita `EIA_API_KEY`, o i file storici su eia.gov).
   - EUR/USD e altri cambi: **BCE**, tassi di riferimento giornalieri (Data Portal, serie `EXR.D.USD.EUR.SP00.A`), riuso con citazione; in alternativa **Banca d'Italia**, cambi di riferimento (API pubblica).
   - Tassi dell'area euro e rendimenti dei titoli di Stato: BCE (curva dei rendimenti dell'area euro, `YC`), Banca d'Italia.
   - Gas TTF, oro, fertilizzanti: **Banca Mondiale, Pink Sheet** (mensile, CC BY 4.0). È mensile, quindi non sostituisce il giornaliero, ma è la base pulita per lo storico.
   - Pressione sulle catene di fornitura: **New York Fed, Global Supply Chain Pressure Index** (mensile, gratuito con citazione), utile anche per i noli.
2. **Yahoo solo per i valori derivati**, senza serie complete: ultimo valore, data, variazione a 1 giorno, 1 mese, da inizio anno e 1 anno, e al massimo una mini-serie ridotta per lo sparkline (per esempio 13 punti settimanali, normalizzati a 100). Lo storico completo resta fuori dal repository (cartella ignorata da git o cache di Actions).
3. **Dire chiaramente sul sito** che indici, titoli e futures sono "valori indicativi da Yahoo Finance, non ufficiali, solo per contesto", come già fa in parte `METODO.md`.

Nota onesta: anche i valori derivati vengono da Yahoo, quindi il livello 2 riduce il rischio ma non lo azzera. Per titoli e indici azionari non esiste una fonte ufficiale gratuita giornaliera con licenza aperta. L'alternativa pulita è mostrare meno titoli e più serie ufficiali.

## 4. Noli e Baltic Dry
- Tenere nel repository solo l'ultimo valore pubblico di WCI, FBX, SCFI e CCFI, con data e link, e non lo storico ricostruito.
- Togliere la lettura automatica del Baltic Dry da Trading Economics. In alternativa: citare il BDI a mano da un articolo con link, oppure usare indicatori gratuiti come il GSCPI della New York Fed e i dati di PortWatch, che il progetto ha già.

## 5. @Majakovsk73: cosa chiedere all'autore

Messaggio breve e cortese (su X o dove l'autore è raggiungibile), con:
1. Chi sei e cos'è il progetto: personale, non commerciale, pubblico su GitHub e GitHub Pages, link al sito.
2. Cosa usi: i poligoni della mappa "Ucraina (2025)" su Google My Maps, scaricati il 5/11/2026 (28 aree, avanzate giornaliere con data), più i punti dei colpi.
3. **Permesso di copiare e ripubblicare i poligoni** in un file pubblico (`docs/data/fronte.json`), modificati (semplificati, tipo d'area dedotto dal colore).
4. **Come vuole essere citato** (nome, handle, link) e se va bene la dicitura attuale "Fronte: @Majakovsk73".
5. **Frequenza**: se va bene scaricare la mappa ogni giorno o ogni settimana.
6. **Licenza**: se è disposto a indicarne una (per esempio CC BY-NC 4.0) per evitare dubbi futuri.
7. **Uso futuro**: se il permesso vale anche se il progetto viene mostrato a datori di lavoro, e cosa succede se un giorno diventasse uso professionale.
8. **Correzioni e ritiro**: impegno a togliere i dati se l'autore lo chiede, e a correggere le avanzate segnalate come sbagliate.

Conservare la risposta (screenshot o link) in `report/permessi/`. Finché non risponde: link alla sua mappa sì, poligoni nel repository no.

Lo stesso schema vale per **DeepState** (email dal sito: chiedere in particolare il punto 3, perché il loro accordo vieta di ridistribuire i dati dell'API) e, se servono più dati, per **ISW/CTP**.

## 6. Cose fatte in questo giro
- `LICENSE`: MIT per il codice, con la nota che i dati non sono coperti.
- `DATA_LICENSES.md`: licenza file per file di `docs/data/`.
- `docs/crediti.html`: pagina dei crediti del sito (va collegata dalla mappa: richiesta alla Regia in `STATO.md`).
- `METODO.md`: tabella delle licenze corretta (Benden, Yahoo, licenze NC e share-alike).

## 7. Da fare (in ordine di rischio)
1. Scrivere a @Majakovsk73 e a DeepState; nel frattempo togliere dal repository i poligoni di `fronte.json` e `fronte-storico.json` o tenere solo i km².
2. `prezzi.json`: passare a EIA/BCE/Banca d'Italia/Tesoro per le serie complete e tenere Yahoo solo per i valori derivati.
3. Togliere il Baltic Dry da Trading Economics; noli solo con l'ultimo valore.
4. Sostituire OpenSanctions con EUR-Lex per le navi UE.
5. Rete elettrica: Overpass o Geofabrik al posto delle tessere OpenInfraMap; file dichiarati ODbL.
6. Correggere il campo `licenza` di `linee.json` e `condotte.json` (GEM è CC BY 4.0).
7. Rigenerare la chiave AGSI (è nella cronologia git).
8. Accorciare descrizioni YouTube e sommari di Google News.

## 8. Proposta per il campo "About" del repository GitHub

- **Description** (max ~350 caratteri):
  `Geo-economic risk monitor: an OSINT map linking events to chokepoints, energy and trade flows, freight rates, prices and exposed countries. Daily data collection with GitHub Actions, every data point with source, date and reliability. Personal project.`
- **Website / homepage**: `https://gabrielegiuliani04.github.io/monitor-geoeconomico/`
- **Topics** (minuscolo, trattini):
  `osint`, `geoeconomics`, `maritime`, `shipping`, `chokepoints`, `ais`, `energy`, `lng`, `ports`, `logistics`, `supply-chain`, `geopolitical-risk`, `data-visualization`, `d3`, `github-actions`, `open-data`, `python`, `strait-of-hormuz`, `baltic-sea`, `north-sea`
- Spuntare "Include in the home page: Releases" no; "Packages" no; "Deployments" sì (mostra GitHub Pages).
- Social preview (Settings → Social preview): `docs/img/north-sea-baltic.jpg` ridotta a 1280×640.
