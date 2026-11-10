# Capitolo 4 — Dati, fonti, licenze e limiti

> **A cosa serve questo capitolo.** Sapere da dove viene ogni numero del Geo-economic Risk Monitor, quanto è affidabile, sotto quale licenza si può usare e dove sono i limiti. Un selezionatore può chiederti "da dove prendi questo dato?", "puoi usarlo?" o "cosa succede se la fonte sbaglia?". Qui trovi la risposta, con il file del repository che la dimostra.
>
> **Regola del capitolo.** Ogni numero viene dai file del repository, letti il 10 novembre 2026: `docs/data/*.json`, i due workflow in `.github/workflows/`, `DATA_LICENSES.md`, `report/licenze.md`, i rapporti in `report/agenti/*.md`, `STATO.md` e `METODO.md`. Quando un'informazione non è scritta nei file, il capitolo lo dice.

---

## 4.1 I file di `docs/data/`: la tabella completa

La cartella contiene **66 file JSON**, più `health.json`, prodotto dal nuovo controllo di qualità (vedi §4.6). La maggior parte dei file segue lo schema comune di `raccolta/AGENTI.md`: `aggiornato`, `fonti[]` (nome, link, licenza, data del dato), `nota`, `elementi`, `errori`. **Il campo `fonti[]` di ogni file è il riferimento ufficiale per le licenze.** `DATA_LICENSES.md` lo riassume.

### Come leggere la colonna "Aggiornamento"

- **Q** = quotidiano, alle 05:15 UTC, dal workflow `aggiorna-dati.yml`. Ogni passo è indipendente (`continue-on-error: true`): se una fonte cade, le altre vanno avanti.
- **M** = mercati, dal lunedì al venerdì alle 21:30 UTC ("dopo la chiusura di Wall Street"), dal workflow `aggiorna-mercati.yml`.
- **C** = curato: voci scritte a mano o da uno script che **non** è nei workflow. Si aggiorna quando qualcuno rilancia lo script o rivede le voci.
- **S** = statico: base cartografica o file di lavoro scaricato una volta.

### Come leggere la colonna "Licenza"

La licenza viene da `DATA_LICENSES.md`. Dove il file non compare in `DATA_LICENSES.md` (oggi 24 file, segnati con **\***), la licenza viene dal campo `fonti[]` del file stesso e da `report/licenze.md`. "Fatti citati" vuol dire: date, cifre ed eventi presi da articoli o documenti, citati con link. Il testo è del progetto.

### A. Base cartografica e infrastrutture

| File | Contenuto in una riga | Fonte principale | Agg. | Elementi oggi | Licenza |
|---|---|---|---|---|---|
| `world.json` | Mondo 1:50m (TopoJSON) | Natural Earth | S | 1.896 archi | Pubblico dominio |
| `medio-oriente.json` | Dettaglio 1:10m del teatro mediorientale | Natural Earth | S | 1.434 archi | Pubblico dominio |
| `labels.json` | Etichette di paesi, città, mari, stretti | Natural Earth | S | 192 paesi, 1.291 città, 55 mari, 16 stretti | Pubblico dominio |
| `manifest.json` | Indice dei livelli e delle viste della mappa | Progetto | S | 16 livelli, 7 viste | MIT (codice) |
| `linee.json` | Oleodotti e gasdotti (file principale) | Global Energy Monitor | S (5/11) | 588 linee | CC BY 4.0 |
| `condotte.json` | Altre condotte GEM, con le tratte in mare | Global Energy Monitor | S (7/11) | 454 linee | CC BY 4.0 |
| `terminali-gnl.json` | Terminali GNL di import ed export | GEM, LNG Terminals Tracker | Q | 840 terminali | CC BY 4.0 |
| `nucleare.json` | Centrali nucleari, raggruppate per progetto | GEM, Global Nuclear Power Tracker | C | 167 centrali | CC BY 4.0 |
| `gas-italia.json` | Flussi fisici giornalieri di gas ai punti d'ingresso italiani | ENTSOG Transparency Platform | Q | 11 punti | Termini ENTSOG (riuso con citazione); CC BY 4.0 per le coordinate GEM |
| `cavi.json` | Cavi sottomarini e approdi | TeleGeography Submarine Cable Map | C | 713 cavi, 1.928 approdi | **CC BY-NC-SA 3.0** |
| `cavi-incidenti.json` | Incidenti a cavi sottomarini 2023–2026 | Stampa, una fonte per incidente | C | 14 | Fatti citati; id dei cavi CC BY-NC-SA 3.0 |
| `rete-elettrica.json` | Linee ≥380 kV e HVDC | OpenStreetMap via OpenInfraMap | C | 2.367 tratti | **ODbL 1.0** |
| `interconnessioni.json` | Interconnessioni elettriche strategiche | Terna, ENTSO-E, PyPSA-Eur, OSM | C | 16 | **ODbL 1.0** (geometrie); fatti citati |
| `ferrovie.json` | Rete ferroviaria principale, corridoi e incidenti | Natural Earth + schede curate | C | 49 voci | Pubblico dominio; fatti citati |
| `rotte.json` | Rotte marittime | Benden (2022), Global Shipping Lanes v1.3.1 | S (7/11) | 239 rotte | **CC BY-NC 4.0** (la più restrittiva delle tre dichiarate) |
| `stretti.json` | Quote mondiali di ciò che passa negli stretti | IEA, EIA, stampa | S (7/11) | 16 stretti | Fatti citati |
| `stretti-dettaglio.json` | Schede approfondite dei passaggi strategici | IEA, EIA, Lloyd's List, Howden Re e altre (100 fonti) | Q (parte automatica) | 13 schede | Fatti citati; IEA CC BY 4.0 |

### B. Navi, flussi, noli, sanzioni, porti

| File | Contenuto in una riga | Fonte principale | Agg. | Elementi oggi | Licenza |
|---|---|---|---|---|---|
| `portwatch.json` | Transiti giornalieri negli stretti e chiamate nei porti italiani | IMF PortWatch | Q | 22 (13 passaggi + 9 porti) | Termini FMI: riuso con citazione |
| `porti-nord.json`\* | Chiamate giornaliere nei porti del Mare del Nord e del Baltico | IMF PortWatch, autorità portuali | Q | 30 porti | Dati pubblici FMI, citare "IMF PortWatch" |
| `navi.json` | Ultime posizioni AIS di petroliere e navi militari | Digitraffic, aisstream.io, USNI | Q | 145 navi + 36 navi militari USA | Mista: CC BY 4.0 (Digitraffic), termini aisstream, **CC BY-NC 4.0** (GFW), fatti (USNI) |
| `sanzioni-navi.json` | Navi sanzionate da USA, Regno Unito e UE | OFAC, UK Sanctions List, OpenSanctions | Q | 2.022 navi | Mista: pubblico dominio, OGL v3.0, **CC BY-NC 4.0** (parte UE) |
| `noli.json` | Indici dei noli container | Drewry WCI, Freightos FBX, SSE (SCFI, CCFI) | Q | 4 indici | **Indici proprietari**: solo valori citati con fonte e data |
| `transit-times.json`\* | Giorni di mare e costi per 99 rotte verso 9 porti europei | Rotte Benden, PortWatch, bunker, war risk | Q | 99 rotte | Ereditata dalle fonti (Benden CC BY-NC 4.0 per i tracciati) |
| `port-risk.json`\* | Indice di rischio per 39 porti | Calcolato da altri file del progetto | Q | 39 porti | Calcolo del progetto su dati con le loro licenze |
| `assicurazioni.json`\* | Aree a rischio guerra e premi war risk | Joint War Committee, stampa assicurativa | C | 27 aree, 49 punti di premio | Documenti pubblici e fatti citati con link |
| `bunker-emissioni.json`\* | Prezzi del bunker, EUA, regole ETS e FuelEU | Ship & Bunker, EEX, MPA Singapore, EUR-Lex | Q | 24 punti | © Ship & Bunker (valori citati); dati pubblici EEX; © UE con citazione |

### C. Energia, scorte, macro, paesi, commercio

| File | Contenuto in una riga | Fonte principale | Agg. | Elementi oggi | Licenza |
|---|---|---|---|---|---|
| `scorte.json` | Gas UE, petrolio USA, scorte di emergenza UE, grano, oro | GIE AGSI+, Eurostat, EIA, USDA, FMI IRFCL | Q | 44 serie | Mista, tutte con citazione; FMI non commerciale senza permesso |
| `esposizione-nord.json`\* | Esposizione energetica di 10 paesi del Nord | Eurostat, IEEFA, GEM, AGSI+ | Q | 10 paesi | Eurostat CC BY 4.0; IEEFA citato |
| `offshore-nord.json`\* | Parchi eolici offshore, piattaforme, hub | EMODnet, Wikipedia, OSM | Q | 180 parchi, 471 piattaforme | CC BY 4.0 (EMODnet); CC BY-SA; ODbL |
| `paesi.json` | Schede di 33 paesi (macro, energia, commercio, spesa militare) | FMI WEO, Banca Mondiale, SIPRI, OWID, Eurostat, UN Comtrade | C | 33 paesi | Mista; **SIPRI non commerciale** |
| `commercio.json`\* | Primi capitoli HS, partner e voci strategiche per paese | UN Comtrade, USGS, EIA, WNA, CIA Factbook | C | 38 paesi, 58 dipendenze | Termini Comtrade (citazione, vietata la ridistribuzione massiva); pubblico dominio |
| `minerali.json`\* | Produttori e riserve di minerali critici, controlli all'export | USGS MCS 2026, EIA, WNA | C | 25 minerali | Pubblico dominio; WNA © con citazione |
| `gpr.json` | Indice di rischio geopolitico, giornaliero e mensile | Caldara e Iacoviello | Q | 18 serie | Libero per la ricerca, con citazione |
| `calendario.json` | Banche centrali, dati macro, energia, elezioni fino a novembre 2027 | Fed, BCE, BoE, BoJ, BLS, BEA, EIA, IFES | Q | 215 eventi | Fatti (date, tassi) con citazione |
| `italia-impatti.json`\* | Carburanti, accise, PUN, inflazione, scioperi, scenari per l'Italia | MASE, GME, Istat, Eurostat, ARERA, Yahoo (solo coefficienti) | Q | 15 indicatori del giorno, 8 serie, 4 scenari | Dati pubblici; Istat CC BY 3.0 IT; Eurostat CC BY 4.0 |
| `simulatore.json`\* | Regole e parametri del simulatore "E se…" | Schede degli stretti, prezzi, PortWatch, noli | C | 9 passaggi | Calcolo del progetto; Yahoo solo coefficienti |
| `rischio.json`\* | Cruscotto del rischio (probabilità × impatto) | Calcolato da 26 file del progetto | Q | 18 unità | Calcolo del progetto |

### D. Mercati

| File | Contenuto in una riga | Fonte principale | Agg. | Elementi oggi | Licenza |
|---|---|---|---|---|---|
| `prezzi.json` | Chiusure giornaliere di indici, titoli, materie prime, cambi, cripto e tassi USA | Yahoo Finance (29 serie), Tesoro USA (4 serie) | M | 33 serie | Tesoro: pubblico dominio. Yahoo: **nessuna licenza, solo uso personale** |
| `mercati.json` | Raccolta manuale dei mercati di una giornata, con link | Stampa e siti di mercato | C (9/11) | 1 giornata, 9 gruppi | Fatti citati |

### E. Militare, Ucraina, eventi

| File | Contenuto in una riga | Fonte principale | Agg. | Elementi oggi | Licenza |
|---|---|---|---|---|---|
| `fissi.json` | Basi e porti del Medio Oriente | World Port Index, OurAirports, Wikidata, stampa | C | 192 punti | Pubblico dominio / CC0; fatti citati |
| `italia.json` | Basi e comandi in Italia | OurAirports, WPI, Wikidata, OSM | C | 58 punti | Pubblico dominio / CC0; ODbL per 10 coordinate |
| `iran.json` | Siti militari iraniani | OurAirports, WPI, Wikidata, stampa datata | C | 53 punti | Pubblico dominio / CC0; fatti citati |
| `difesa.json` | Difese aeree e radar nel Golfo | Fonti di stampa e di analisi datate | C | 8 punti | Fatti citati |
| `basi-mondo.json`\* | Principali basi militari nel mondo | OurAirports, Wikidata, CRS, stampa | C | 181 basi | Pubblico dominio / CC0; descrizioni riassunte da Wikipedia |
| `mobili.json` | Unità navali mobili (portaerei, gruppi) | USNI e stampa | C | 53 punti | Fatti citati |
| `eventi.json` | Eventi militari e di sicurezza recenti | Stampa, comunicati, account OSINT | C | 126 punti | Fatti citati |
| `ibrido.json` | Minacce ibride (droni, sabotaggi, falsi allarmi) | Stampa e fonti ufficiali | C | 35 punti | Fatti citati |
| `baltico-sicurezza.json`\* | Sicurezza nel Baltico: eventi, flotta ombra, disturbo GNSS | Eventi curati, GPSJam, `navi.json` | Q | 48 eventi, 54 navi della flotta | Citazione; GPSJam senza licenza dichiarata |
| `fronte.json` | Solo link alle mappe del fronte | ISW, DeepState, @Majakovsk73 | C (5/11) | 0 aree, 0 punti, 4 link | Nessun dato ripubblicato |
| `fronte-storico.json` | Km² occupati dalla Russia, un'istantanea al mese dal 2022 | DeepStateMap, ISW/CTP | C | 60 istantanee (solo numeri) | DeepState: diritti riservati, si pubblicano solo valori derivati |
| `ucraina-storico.json` | Missili e droni russi lanciati e abbattuti; attacchi ucraini all'energia russa | Dataset di Petro Ivaniuk; Kyiv Independent e Wikipedia | Q | 20 serie, 258 punti | **CC BY-NC-SA 4.0** (serie); fatti citati |
| `attacchi-russi.json`\* | Attacchi russi in Ucraina geolocalizzati | Eventi curati (Kyiv Independent, Reuters, AP…) + Ivaniuk | C | 192 eventi, 25 oblast | **CC BY-NC-SA 4.0** (ereditata da Ivaniuk); fatti citati |
| `attacchi-analisti.json`\* | Attacchi a lungo raggio estratti dai post di due analisti | Telegram di Clément Molin e AMK Mapping, GeoNames, NASA FIRMS | C | 632 elementi | Diritti degli autori: solo fatti, estratto ≤160 caratteri e link |
| `cyber-energia.json`\* | Incidenti cyber contro l'energia (taglio difensivo) | CERT Polska, CISA, ESET, Mandiant e altri | C | 30 | Fatti citati |

### F. AI, transizione, notizie, altro

| File | Contenuto in una riga | Fonte principale | Agg. | Elementi oggi | Licenza |
|---|---|---|---|---|---|
| `ai.json` | Infrastrutture AI negli USA | Epoch AI, comunicati | C | 25 punti | CC BY 4.0; fatti citati |
| `ai-mondo.json`\* | Data center AI, fabbriche di chip, supercalcolatori fuori dagli USA | Epoch AI, TOP500, comunicati | C | 82 punti | CC BY 4.0 (Epoch); TOP500 con citazione |
| `investimenti.json`\* | Flussi di capitale per AI e infrastrutture 2024–2026 | Comunicati, Reuters/AFP | C | 64 voci | Fatti citati |
| `supply-chain-ai.json`\* | Catena del valore dell'AI, dalla miniera al data center | USGS, voci curate, Nominatim | C | 70 nodi, 34 archi | Pubblico dominio; fatti citati; ODbL |
| `dossier.json` | Dossier AI per paese | Ricerca web con fonti | C | 1 dossier (Stati Uniti) | Fatti citati |
| `idrogeno.json`\* | Progetti di idrogeno e ammoniaca nei porti | IEA, comunicati, porti | C | 41 progetti, 7 reti | IEA CC BY 4.0; fatti citati |
| `eolico-filiera.json`\* | Filiera dell'eolico offshore: porti base, navi, aste | WindEurope, stampa di settore (52 fonti) | C | 19 porti, 20 navi | © degli editori: fatti con link |
| `wind-calendar.json`\* | Scadenze dell'eolico offshore 2023–2027 | Governi, aziende, stampa (47 fonti) | Q (validazione) | 114 tappe | Fatti citati; DESNZ OGL v3.0 |
| `webcam.json`\* | Webcam pubbliche su stretti, porti, energia | Elenco curato, Port of Rotterdam | C | 45 webcam | Solo link: le immagini sono dei proprietari |
| `notizie.json` | Notizie OSINT degli ultimi 7 giorni, tutte "da verificare" | 35 fonti (UKMTO, JMIC, gCaptain, USNI…) | Q | 512 notizie | Titolo, data e link; gli articoli sono degli editori |
| `notizie-testate.json`\* | Notizie delle testate per argomento, ultimi 3 giorni | 93 feed di 57 testate | Q | 1.049 articoli | Titolo, sommario ≤300 caratteri e link |
| `report.json` | Testo dei report giornalieri | Progetto | C | 5 report | Testo del progetto |

**Due cose da sapere sulla tabella.**
1. **Alcuni file curati sono nella tabella delle cadenze del controllo di qualità come "daily", ma non sono nel workflow.** È il caso di `attacchi-russi.json` e `attacchi-analisti.json`: oggi non c'è un passo di `aggiorna-dati.yml` che li rigeneri. Lo stesso vale per `cavi.json`, `paesi.json`, `commercio.json`, `ferrovie.json` e la rete elettrica: `STATO.md` li dà come "non ancora nel workflow (dati statici o lenti)".
2. **Tra un giorno e l'altro i conteggi cambiano.** Quelli sopra sono del 10 novembre 2026, mattina. Per dire un numero in un colloquio, apri il file del giorno o `docs/data/health.json`, che li elenca tutti nel campo `counts`.

---

## 4.2 Le fonti principali, una per una

Per ogni fonte: **chi è**, **perché fidarsi** e **cosa dà al progetto**. Il "perché fidarsi" non vuol dire "è sempre giusta". Vuol dire che è una fonte primaria o riconosciuta, che pubblica il proprio metodo e che è citata dagli addetti ai lavori. I limiti sono nel §4.4.

### Navi, porti e stretti

**IMF PortWatch.** È la piattaforma del Fondo monetario internazionale con l'Università di Oxford. Stima i passaggi negli stretti e le chiamate nei porti a partire dai segnali AIS delle navi. È affidabile perché è un'istituzione pubblica, con un metodo dichiarato e uguale per tutti gli stretti, e permette confronti con gli anni precedenti. Dà al progetto i transiti giornalieri di 13 passaggi e 9 porti italiani (`portwatch.json`), con serie dal 1/1/2023, e i 30 porti del Nord (`porti-nord.json`). È la base del grafico dei transiti, del cruscotto del rischio, dei tempi di transito e del port risk index.

**Digitraffic (Fintraffic) e aisstream.io.** Digitraffic è il servizio di dati aperti dell'agenzia finlandese del traffico. Pubblica in CC BY 4.0 le posizioni AIS del Baltico settentrionale, senza chiave. aisstream.io è un servizio WebSocket gratuito con chiave personale, basato su ricevitori volontari a terra. Insieme danno `navi.json`: petroliere e navi militari negli stretti e ogni nave sanzionata vista. Nell'ultima esecuzione hanno dato 96 petroliere nel Golfo di Finlandia, di cui 38 sanzionate, e 19 negli Stretti danesi. Global Fishing Watch (interruzioni AIS, CC BY-NC 4.0) è previsto nel codice, ma `avvisi_ais` è ancora vuoto.

**USNI News Fleet and Marine Tracker.** È il tracker settimanale dello U.S. Naval Institute, con le aree in cui si trovano portaerei e gruppi anfibi USA. È affidabile perché viene da un istituto navale con fonti ufficiali e aggiornamenti regolari. Dà l'area di ogni unità: in `navi.json` (36 navi) e `mobili.json` la coordinata è il **centro dell'area**, con una precisione da 250 a 2.000 km.

**Joint War Committee (JWC).** È il comitato degli assicuratori marittimi di Londra (LMA e IUA) che pubblica le **circolari JWLA** con le "listed areas", le zone in cui serve una copertura separata per il rischio guerra. È la fonte primaria del mercato. Dà le 27 aree di `assicurazioni.json`. Lo script controlla online se la lista cambia: all'ultimo giro, "nessun cambiamento". I **premi**, invece, non vengono dal JWC: sono quotazioni riportate dalla stampa (Reuters, Bloomberg, S&P Global Platts, Howden Re).

### Energia e scorte

**Global Energy Monitor (GEM).** È un'organizzazione indipendente che censisce le infrastrutture energetiche del mondo: condotte, terminali GNL, centrali. È affidabile perché pubblica i dati progetto per progetto, con fonte e stato, sotto licenza aperta (CC BY 4.0). Dà al progetto le condotte (`linee.json`, `condotte.json`), 840 terminali GNL e 167 centrali nucleari. Attenzione: `linee.json` e `condotte.json` vengono da file di lavoro di GEM su GitHub scaricati il 5/11/2026, "non la release ufficiale" (campo `versione`).

**ENTSOG.** È l'associazione europea dei gestori delle reti di trasporto del gas. La sua Transparency Platform pubblica i flussi fisici ai punti di rete. È una fonte ufficiale per regolamento UE. Dà `gas-italia.json`: i flussi giornalieri in GWh/giorno agli 11 punti d'ingresso italiani, per gli ultimi 12 mesi.

**GIE AGSI+.** È la piattaforma di Gas Infrastructure Europe, l'associazione dei gestori di stoccaggi e terminali, con i livelli degli stoccaggi di gas paese per paese. È la fonte di riferimento per il riempimento degli stoccaggi in UE. Richiede una chiave gratuita (`AGSI_API_KEY`). Nell'ultimo `scorte.json` dà riempimento e TWh per paese (ultimo dato 8/11/2026). La chiamata sull'aggregato UE ha dato un errore, il cui testo è stato mascherato: vedi §4.5.

**Eurostat.** È l'istituto statistico dell'Unione europea, con licenza CC BY 4.0. Dà le scorte mensili di gas e di petrolio di emergenza (`scorte.json`) e la dipendenza dalle importazioni di energia (`paesi.json`, `esposizione-nord.json`). È ufficiale ma lento: l'ultimo dato è di agosto–settembre 2026.

**EIA (U.S. Energy Information Administration).** È l'agenzia statistica dell'energia del governo USA, e i suoi dati sono di pubblico dominio. Dà le scorte settimanali di petrolio USA (Weekly Petroleum Status Report), le date del calendario energetico e i dati internazionali su produzione e riserve (`commercio.json`, `minerali.json`). Molte analisi EIA su Hormuz sono citate tramite la stampa, perché eia.gov non era raggiungibile dalla sessione di lavoro (`report/agenti/stretti.md`).

**Ship & Bunker.** È un sito specializzato nei carburanti navali, con prezzi giornalieri per porto. È lo standard di fatto per i prezzi pubblici del bunker. Dà a `bunker-emissioni.json` i prezzi di VLSFO e degli altri carburanti nei principali hub. Sono medie di più fonti, non transazioni, e alcuni porti (tra cui Genova) sono a pagamento.

**EEX (European Energy Exchange).** È la borsa che gestisce le aste primarie dei permessi di emissione UE (EUA). Dà il prezzo dell'asta più recente: 86,91 € il 9/11/2026, il valore con cui `bunker-emissioni.json` calcola il costo ETS per tonnellata di carburante.

**EMODnet.** È la rete europea di dati marini finanziata dalla Commissione UE (licenza CC BY 4.0). Dà i poligoni dei parchi eolici offshore e delle piattaforme del Mare del Nord e del Baltico (`offshore-nord.json`: 180 parchi, 471 piattaforme).

### Macro, commercio, paesi

**Tesoro USA (U.S. Department of the Treasury).** Pubblica ogni giorno la curva dei rendimenti dei titoli di Stato. È la fonte ufficiale, di pubblico dominio. Dà a `prezzi.json` i rendimenti a 2, 10 e 30 anni e lo spread 10–2 anni, con circa un anno di storia (260 punti).

**Yahoo Finance.** Dà le altre 29 serie di `prezzi.json`: indici (S&P 500, FTSE MIB, DAX…), titoli AI e dei semiconduttori, oro, argento, Brent, WTI, TTF, Henry Hub, EUR/USD, Bitcoin, Ethereum. È usata perché è l'unica fonte gratuita e giornaliera per tutte queste serie: FRED e Stooq rifiutano il server cloud (`STATO.md`, *Decisioni prese*). **Perché solo 3 mesi.** Yahoo non dà una licenza sui dati: i suoi termini consentono l'uso personale e vietano la ridistribuzione, e molti dati sono a loro volta licenziati dalle borse (S&P, ICE per Brent e TTF, Nasdaq). Salvare ogni giorno un anno intero di chiusure in un repository pubblico era una ridistribuzione sistematica (`report/licenze.md`, §3). Lo script `raccolta/scarica_mercati.py` scarica 13 mesi solo per calcolare le variazioni, ma ne pubblica circa 3: `"serie": s[-66:]`, con il commento "pubblichiamo solo ~3 mesi". Ogni serie Yahoo nel file ha 66 punti; per esempio l'S&P 500 parte dal 7/8/2026. Il sito presenta questi valori come indicativi, non ufficiali (`METODO.md`).

**FMI (Fondo monetario internazionale).** Dà le stime e le previsioni del World Economic Outlook (ottobre 2026) nelle schede paese e le riserve d'oro delle banche centrali (IRFCL) in `scorte.json`. È la fonte di riferimento per la macroeconomia comparata. Per l'FMI l'"anno 2025" è in parte una stima e il 2026 è una previsione.

**Banca Mondiale.** Dà gli indicatori di sviluppo (World Development Indicators) delle schede paese, in CC BY 4.0. È la base statistica internazionale più usata per confronti tra paesi.

**UN Comtrade.** È la banca dati del commercio estero delle Nazioni Unite, costruita dalle dichiarazioni doganali dei paesi. Dà a `paesi.json` e `commercio.json` i primi capitoli esportati e importati, i primi 5 partner e le voci strategiche HS4. Quando un paese non dichiara, i dati sono ricostruiti dai partner ("specchio"). Il progetto usa l'API di anteprima, senza chiave.

**USGS (U.S. Geological Survey).** Pubblica ogni anno i Mineral Commodity Summaries, il riferimento mondiale su produzione e riserve dei minerali. Sono di pubblico dominio. Dà `minerali.json` (25 minerali) e la parte mineraria della catena del valore dell'AI.

**SIPRI.** È lo Stockholm International Peace Research Institute, la fonte di riferimento per la spesa militare (database Milex). Dà la spesa militare delle schede paese. La licenza è uso libero **non commerciale** con citazione: per questo `report/licenze.md` dice di non ripubblicare il file intero, solo estratti per paese.

### AI

**Epoch AI.** È un istituto di ricerca che misura lo sviluppo dell'intelligenza artificiale e pubblica dataset in CC BY 4.0. Dà al progetto i data center AI (MW, equivalenti H100, proprietari, osservazioni satellitari) e le quote del calcolo AI per paese (`ai-mondo.json`, `ai.json`). Copre bene USA, Malesia e Cina, poco l'Europa (`report/agenti/ai.md`).

### Ucraina e fronte

**ISW e DeepStateMap: perché solo link.** ISW (Institute for the Study of War, con l'AEI Critical Threats Project) è il centro studi statunitense che pubblica ogni giorno la valutazione del fronte. DeepStateMap è il progetto ucraino di mappatura del fronte più seguito. Sono due fonti autorevoli e indipendenti tra loro. Nessuna delle due, però, dà una licenza per ripubblicare le geometrie:
- l'accordo di DeepState consente l'API per volontariato e difesa dell'Ucraina, e **vieta di ridistribuire i dati dell'API o di farle da proxy**;
- gli item ArcGIS di ISW dicono: "You may not use this geodata without the written consent of ISW" (`report/agenti/isw.md`).

Per questo il sito mostra **link** alle loro mappe (`fronte.json`, `mappe_esterne`). `fronte-storico.json` pubblica solo **valori derivati**: km² occupati, variazioni mensili, momenti chiave, nessun poligono.

**Kyiv Independent.** È una testata ucraina in lingua inglese. È la fonte principale degli eventi curati. Per gli attacchi ucraini all'energia russa sono stati incrociati 251 suoi articoli con la lista di Wikipedia e 21 aggiunte manuali (`report/agenti/ucraina.md`). È usata anche per gli attacchi russi (`attacchi-russi.json`). È una testata di parte ucraina, ma con redazione e correzioni pubbliche: i fatti hanno link e affidabilità dichiarata.

**Dataset di Petro Ivaniuk (*Massive Missile Attacks on Ukraine*).** È un dataset su Kaggle che trascrive ogni giorno i comunicati dell'Aeronautica ucraina: missili e droni lanciati e abbattuti. Il progetto lo legge da una copia SQLite di un progetto terzo (Narretz/sbs-stats), perché Kaggle richiede una chiave. Dà le serie giornaliere di `ucraina-storico.json` dal 28/9/2022 e i conteggi per oblast di `attacchi-russi.json`. La licenza CC BY-NC-SA 4.0 è dichiarata dai progetti che lo riusano: la pagina Kaggle non è stata letta direttamente (`report/licenze.md`).

**Telegram di Clément Molin e AMK Mapping.** Sono due analisti OSINT che Gabriele segue per l'Ucraina e il militare (`STATO.md`, *Da fare* punto 6). Dai loro canali pubblici sono stati letti 1.704 post (Molin, dal 2023) e 2.523 post (AMK, dal 8/9/2026). Lo script ne estrae 632 attacchi a lungo raggio (`attacchi-analisti.json`). L'affidabilità è "media" se l'evento è segnalato da un solo analista, "alta" se lo stesso evento compare in un'altra fonte del progetto o nell'altro canale (±1 giorno, entro 30 km). Il file tiene un estratto di al massimo 160 caratteri e il link, mai il testo. Il nome del rapporto citato nella `nota` (`report/agenti/attacchi-analisti.md`) **non c'è ancora** nel repository.

### Notizie

**Testate giornalistiche.** `notizie-testate.json` legge 93 feed di 57 testate (generaliste e di settore, in inglese, italiano, danese/norvegese e olandese). `notizie.json` legge 35 fonti OSINT e ufficiali (UKMTO, JMIC, MARAD, NATO Shipping Centre, gCaptain, USNI…). Ogni testata ha affidabilità e paywall dichiarati. Si tengono solo titolo, data, link e un sommario breve del feed: il testo resta dell'editore. Le notizie OSINT sono tutte "da verificare" finché un evento non passa in `eventi.json` con le sue fonti.

---

## 4.3 Licenze e scelte prese

### Il quadro in tre righe

- **Il codice è MIT** (`LICENSE`). **I dati no**: ogni file resta sotto la licenza delle sue fonti (`DATA_LICENSES.md`).
- Il progetto è personale, gratuito, senza pubblicità né clienti. Le fonti **non commerciali** sono ammesse per questo uso, ma `report/licenze.md` lo chiama "una zona grigia" per un portfolio usato per cercare lavoro.
- **In un'azienda cambia tutto.** Usare l'osservatorio, o una sua copia, dentro un porto o un operatore logistico è uso commerciale: le fonti NC andrebbero tolte o sostituite.

### Cosa è non commerciale o share-alike

| Fonte | File | Licenza |
|---|---|---|
| TeleGeography | `cavi.json`, id in `cavi-incidenti.json` | CC BY-NC-SA 3.0 |
| Benden, Global Shipping Lanes | `rotte.json` (e i tracciati di `transit-times.json`) | CC BY-NC 4.0, la più restrittiva delle tre dichiarate dall'autore |
| Global Fishing Watch | `navi.json` (parte GFW) | CC BY-NC 4.0 |
| OpenSanctions (navi UE) | `sanzioni-navi.json` | CC BY-NC 4.0 |
| Petro Ivaniuk | `ucraina-storico.json`, `attacchi-russi.json` | CC BY-NC-SA 4.0 |
| SIPRI | `paesi.json` | Uso libero non commerciale (non CC) |
| FMI (IRFCL, WEO) | `scorte.json`, `paesi.json` | Riuso con citazione; uso commerciale con permesso |
| IFES ElectionGuide | `calendario.json` | Non commerciale con citazione (da verificare) |
| OpenStreetMap, PyPSA-Eur | `rete-elettrica.json`, `interconnessioni.json` | ODbL 1.0: share-alike per la banca dati |

### Cosa è stato tolto o limitato, e perché

| Cosa | Problema | Scelta presa | Dove si vede |
|---|---|---|---|
| **Aree del fronte di @Majakovsk73** (mappa "Ucraina (2025)" su Google My Maps: 28 aree e 91 punti) | Nessuna licenza dichiarata, quindi tutti i diritti riservati. Il permesso non è stato ottenuto | Aree e punti tolti dal sito. Resta un link alla sua mappa. Le copie private sono in `raccolta/fronte/privato/`, esclusa da git | `fronte.json`: `aree: []`, `punti: []`; commit "Fronte ucraino: tolte le aree e i punti senza licenza" |
| **Poligoni DeepState** | L'accordo vieta di ridistribuire i dati dell'API | Pubblicati solo km², variazioni e momenti chiave: "I poligoni mese per mese NON sono pubblicati" | `fronte-storico.json`, `nota`: nessuna istantanea ha geometrie |
| **ISW** | Le geodata richiedono "the written consent of ISW" | Il modulo `docs/isw-fronte.js` è pronto ma **non attivato**: il browser dovrebbe scaricare i poligoni dal server ISW, e anche questo è "uso della geodata". Restano i link e 2 istantanee del 2022 in km² | `report/agenti/isw.md`; `STATO.md` |
| **Baltic Dry da Trading Economics** | I termini di Trading Economics vietano lo scraping e la ridistribuzione; il BDI è © Baltic Exchange | Raccolta automatica tolta: "Baltic Dry tolto: i termini di Trading Economics vietano la raccolta automatica". Va citato a mano dalla stampa | `raccolta/flussi/raccogli.py`; `noli.json` ha 4 indici, senza il BDI |
| **Prezzi Yahoo** | Nessuna licenza; ridistribuzione vietata | Pubblicati solo ~3 mesi (66 punti per serie); le variazioni si calcolano sull'anno, in memoria | `raccolta/scarica_mercati.py`; `prezzi.json` |
| **Sezione analisti YouTube** (5 canali, `analisti.json`) | Contenuti con tutti i diritti riservati; descrizioni fino a 600 caratteri segnalate come "una copia" (`report/licenze.md`) | Tolta del tutto il 10/11/2026 su decisione di Gabriele: terminale, dati e raccolta quotidiana | Commit "Tolta la sezione sugli analisti economici"; `STATO.md`, punto 5 |
| **Noli Drewry, Freightos, SSE** | Indici proprietari | Si cita l'ultimo valore con fonte e data. La `nota` del file dice ancora che lo storico "si costruisce a ogni esecuzione" | `noli.json` |

### Come dirlo in un colloquio

Il rispetto delle licenze è un **argomento a favore**, non un punto debole da nascondere. Una formula possibile:

> "Ogni file dei dati ha un campo con fonte, link, licenza e data. Ho fatto un audit delle licenze e ho separato la licenza del codice (MIT) da quella dei dati, file per file. Dove una fonte non mi dava il permesso di ripubblicare, ho tolto il dato: i poligoni del fronte ucraino, il Baltic Dry preso in automatico da Trading Economics, gli storici completi di Yahoo. Al loro posto metto un link alla fonte, oppure pubblico solo valori derivati, come i km² occupati. So anche quali fonti sono non commerciali: se usassi lo strumento in azienda, saprei quali sostituire."

Se ti chiedono **"quali sostituiresti?"**, `report/licenze.md` dà già le alternative:
- OpenSanctions → atti UE su EUR-Lex;
- Yahoo per le materie prime → EIA (Brent, WTI, Henry Hub), BCE o Banca d'Italia (cambi), Banca Mondiale Pink Sheet (mensile);
- Baltic Dry → GSCPI della New York Fed e dati PortWatch;
- rete elettrica da tessere OpenInfraMap → Overpass o un estratto Geofabrik.

### Cose ancora aperte (meglio saperle prima che te le facciano notare)

- **La cronologia di git è pubblica.** Quello che è stato pubblicato prima delle correzioni (poligoni di @Majakovsk73, un anno di Yahoo, la chiave AGSI) resta nella storia del repository (`report/licenze.md`, §1).
- **Permessi chiesti: non risulta dai file.** `report/licenze.md` prepara i messaggi per @Majakovsk73, DeepState e ISW e indica dove conservare le risposte (`report/permessi/`). Quella cartella non esiste: nei file non c'è traccia di una richiesta inviata o di una risposta.
- **`DATA_LICENSES.md` non è completo.** Mancano 24 file (quelli con \* nella tabella del §4.1). C'è ancora una riga per `analisti.json`, che non esiste più. La riga di `noli.json` cita ancora il Baltic Exchange via Trading Economics, e anche il campo `fonti[]` di `noli.json` lo elenca ancora. Il controllo di qualità lo segnala (§4.6).
- **Ancora da fare in `report/licenze.md`:** OpenSanctions non è stato sostituito, la rete elettrica viene ancora dalle tessere OpenInfraMap, e i sommari delle notizie non sono stati accorciati (oggi fino a 300 caratteri per le testate).

---

## 4.4 Limiti onesti

I rapporti degli agenti (`report/agenti/*.md`) hanno quasi tutti una sezione "Limiti". Ecco i principali, raggruppati per tema, ciascuno con una risposta pronta.

### 1. Le navi: AIS spento, falso o assente

- **Il limite.** L'AIS si può spegnere o falsificare (spoofing). La flotta ombra trasmette spesso a intermittenza (`navi.md`). `navi.json` ha già registrato 4 petroliere sanzionate "nello stesso punto nell'entroterra russo" a 46–81 nodi. Per Hormuz, Bab el-Mandeb, Suez e Bosforo non c'è oggi nessuna posizione: `riepilogo_aree` dice "nessuna fonte gratuita attiva per quest'area". aisstream.io dipende da ricevitori a terra, scarsi nel mezzo di Hormuz e di Bab el-Mandeb.
- **Come rispondere.** "Lo so, ed è dichiarato nel dato: un'area senza fonte riporta zero con una nota che dice che non vuol dire zero navi. Le posizioni impossibili, sopra i 40 nodi, sono segnalate e non disegnate. Per i transiti negli stretti uso PortWatch, che è un'altra misura. Per le navi 'dark' servirebbero dati satellitari a pagamento: è un limite di budget, non di metodo."

### 2. PortWatch arriva in ritardo e vede solo l'AIS acceso

- **Il limite.** Circa **una settimana** di ritardo per gli stretti (`flussi.md`) e circa **10 giorni** per i porti del Nord (`nord.md`). Le navi con AIS spento non entrano nel conteggio, quindi i porti russi sono sottostimati. Mancano Dardanelli, Canale di Sicilia e Tiran; per gli Stretti danesi c'è solo l'Øresund, non il Grande Belt. Sui porti piccoli bastano pochi scali per cambiare molto le percentuali.
- **Come rispondere.** "È un indicatore strutturale, non in tempo reale. Lo uso per le tendenze settimanali e per confrontare con lo stesso periodo di uno, due e tre anni prima, non per dire cosa succede oggi. Per oggi guardo le notizie e gli avvisi UKMTO. Kerch a zero da agosto, per esempio, vuol dire 'nessun segnale', non per forza 'nessuna nave'."

### 3. Coordinate stimate

- **Il limite.** Molti punti hanno coordinate stimate: centro della città, dell'oblast o dell'area dichiarata.
  - Navi USA: centro dell'area USNI, precisione 250–2.000 km.
  - Attacchi in Ucraina: centro abitato (3–15 km) o oblast (60 km), "mai del punto d'impatto".
  - Incidenti ai cavi e cyber: lat/lon "SEMPRE stimati".
  - Quattro supercalcolatori TOP500 sono sul centroide del paese.
- **Come rispondere.** "Ogni punto ha due campi, `origine_coord` (fonte o stimata) e `precisione_km`, e la mappa li usa. Per scelta non pubblico più di quanto pubblica la fonte: è un'analisi, non un tracciamento operativo."

### 4. Il commercio è annuale e precedente alla crisi

- **Il limite.** I valori Comtrade sono **annuali, del 2024–2025, quindi precedenti alla crisi di Hormuz del 2026** (`commercio.md`). Sono quote in valore, non in volume, dalle dichiarazioni dell'importatore. Le importazioni dall'UE sono attribuite al paese di spedizione, non a quello d'origine. La quota dal Golfo è un proxy dell'esposizione, non una misura del transito (`paesi.md`).
- **Come rispondere.** "Il commercio mi dà la struttura dell'esposizione: chi dipende da cosa. Lo shock di oggi lo leggo in altri indicatori: PortWatch, noli, prezzi. Ho tenuto le due cose separate apposta."

### 5. Il simulatore usa regole semplici

- **Il limite.** `simulatore.json` elenca 10 limiti. Il simulatore non considera la domanda, le politiche (rilascio di riserve, razionamenti), le aspettative di mercato né gli effetti di secondo giro (inflazione, tassi, cambio). Non somma più passaggi chiusi insieme. Per Panama e Taiwan molte stime restano "non disponibili".
- **Come rispondere.** "È uno strumento per ragionare, non un modello di previsione. Ogni numero rimanda a una fonte o a un episodio storico documentato, e i limiti sono scritti nella pagina stessa. Preferisco un 'non disponibile' a un numero inventato."

### 6. Cruscotto del rischio e port risk index: valutazioni, non previsioni

- **Il limite.** Il punteggio è probabilità (1–5) × impatto (1–5). I giudizi strutturali (peso, alternative) "sono valutazioni con fonte e pesano il 55% dell'impatto" (`rischio.md`). Le soglie di noli e flotta ombra vanno ricalibrate con lo storico. Il port risk index ha un vero storico solo da oggi: il primo confronto è con un giorno ricostruito (`port-risk.md`). Hormuz e il GNL del Qatar condividono i transiti: i punteggi non vanno sommati.
- **Come rispondere.** "Le regole sono esplicite e ogni indicatore ha valore, soglia, fonte e data. È una valutazione strutturata: chiunque può non essere d'accordo con una soglia, ma vede quale."

### 7. Investimenti: annunci, non spesa

- **Il limite.** Molti progetti AI esteri "hanno solo annunci". Le somme "mescolano piani pluriennali, contributi pubblici, acquisizioni e lettere d'intenti… non indicano la spesa effettiva" (`ai.md`). Il campione (64 voci) è curato a mano e parziale. Lo stesso vale per l'idrogeno: 41 progetti, "non un censimento"; su Taranto, Brindisi e Genova "nulla oltre agli annunci".
- **Come rispondere.** "Distinguo lo stato del progetto (annunciato, FID, in costruzione, operativo) e uso la cifra della fonte, con la data. Il messaggio non è 'quanto si spende', ma 'dove va il capitale e quanto ne è ancora sulla carta'."

### 8. Fonti di parte, mappe OSINT e liste curate

- **Il limite.**
  - Le cifre di lanci e abbattimenti sono **dichiarazioni dell'Aeronautica ucraina**, non verificate da terzi. Il dataset non copre il periodo dal 24/2 al 27/9/2022 (`ucraina.md`).
  - Le mappe del fronte "sono valutazioni": tra DeepState e ISW ci sono differenze fino a 4.500 km², molto più dei saldi mensili del 2026, sotto i 100 km² (`fronte.md`).
  - I 192 attacchi russi geolocalizzati "non sono un censimento". I 258 attacchi ucraini all'energia russa sono meno della stima CNN di oltre 300.
- **Come rispondere.** "Ogni punto ha un'affidabilità a tre livelli (alta, media, bassa) e la rivendicazione di una parte in conflitto è 'bassa' finché non è confermata. Saldi mensili sotto il margine tra le mappe li leggo come 'fronte fermo', non come numeri precisi."

### 9. Prezzi e noli non ufficiali

- **Il limite.** Yahoo "non è ufficiale e può cambiare formato" (`METODO.md`). WCI e Baltic Dry erano letti dal testo delle pagine "e possono rompersi se il testo cambia" (`flussi.md`). I premi war risk sono quotazioni di stampa, spesso di seconda mano, che usano il valore centrale della forchetta (per Hormuz a marzo si andava dall'1% al 10%) (`assicurazioni.md`).
- **Come rispondere.** "Per i tassi uso il Tesoro, che è ufficiale. Per il resto i valori servono a dare il contesto e sono marcati come indicativi. Il controllo di qualità confronta lo stesso prezzo tra file diversi e segnala le differenze."

### 10. Dati lenti, siti bloccati, voci manuali

- **Il limite.**
  - Eurostat arriva con 2–3 mesi di ritardo: il controllo di qualità segnala 8 serie mensili di `scorte.json` ferme ad agosto (o a luglio per l'oro USA).
  - Natural Earth (ferrovie) è "ferma a circa il 2017".
  - Molte voci (stato degli stretti, basi, calendario, eolico) sono **curate a mano**: lo script segnala quando invecchiano, ma non le riscrive.
  - Varie fonti non erano raggiungibili dalla sessione cloud (eia.gov, Overpass, Reuters, AP, ISW) e sono citate tramite ristampe o motori di ricerca. 81 basi su 181 non sono state rilette su una fonte datata (`basi.md`).
- **Come rispondere.** "Ogni dato ha la sua data. La mappa fa cambiare colore agli eventi con l'età, e il controllo quotidiano segnala i file vecchi rispetto alla loro cadenza attesa. Quello che non ho potuto verificare è scritto nel rapporto, non nascosto."

> **Regola generale per le domande sui limiti.** Ammetti il limite, indica dove è dichiarato (campo del file o rapporto), spiega cosa hai fatto per contenerlo e cosa faresti con più risorse. Non difendere un numero oltre quello che la fonte dice.

---

## 4.5 Sicurezza: le chiavi API

### Come funziona

Le chiavi non sono mai nel codice né nei file: sono **segreti di GitHub** (Settings → Secrets and variables → Actions). Il workflow `aggiorna-dati.yml` le passa agli script come variabili d'ambiente:

```yaml
env:
  AISSTREAM_API_KEY: ${{ secrets.AISSTREAM_API_KEY }}
  GFW_API_KEY: ${{ secrets.GFW_API_KEY }}
  AGSI_API_KEY: ${{ secrets.AGSI_API_KEY }}
  BLS_API_KEY: ${{ secrets.BLS_API_KEY }}
```

Gli script leggono la chiave con `os.environ.get(...)`. Se manca, saltano quella fonte con un avviso, senza fallire (regola di `raccolta/AGENTI.md`). Gli script conoscono anche altre chiavi facoltative, oggi non passate dal workflow: `EIA_API_KEY`, `KAGGLE_USERNAME`/`KAGGLE_KEY`, `FIRMS_MAP_KEY`, `DATAGOVSG_API_KEY`, `GIE_API_KEY`.

### Il caso della chiave AGSI

- **Cosa è successo.** Al primo giro del workflow, il 9/11/2026, la chiamata ad AGSI+ ha dato un errore. Lo script ha scritto il messaggio d'errore nel campo `errori` di `docs/data/scorte.json`, e il messaggio conteneva la chiave. Il file è pubblico, quindi la chiave è finita su GitHub (`STATO.md`).
- **La correzione** (commit `9daa0a0`, 9/11/2026, "Sicurezza: tolta una chiave API finita in un messaggio d'errore; controllo automatico…"):
  1. la chiave è stata tolta da `scorte.json`;
  2. in `raccolta/scorte/raccogli.py` ogni avviso passa da una funzione `_nascondi()`, che sostituisce i valori delle variabili `*_KEY`/`*_TOKEN` e ogni stringa del tipo "api key: <16+ caratteri>" con `[chiave nascosta]`;
  3. lo script `raccolta/comune/nascondi_chiavi.py` gira **prima di ogni salvataggio** del workflow (passo "Nascondi eventuali chiavi nei file pubblici") su tutti i `docs/data/*.json` e le pagine HTML.
- **Funziona.** Oggi l'errore AGSI in `scorte.json` si legge così: `"AGSI+ EU: API key: [nascosta]"`.
- **Cosa resta da fare.** La chiave è ancora nella cronologia di git, quindi "va rigenerata" (`STATO.md`; `report/licenze.md`, punto 7). **Nei file non risulta che sia stata rigenerata**: verificalo sul tuo account AGSI.

### Il controllo automatico in più

Il nuovo controllo di qualità (§4.6) cerca in `docs/` tutto ciò che somiglia a una chiave o a un token. Se lo trova, lo stato generale diventa rosso e lo script esce con codice 2. Il primo giro di stamattina lo ha dimostrato bene: ha segnalato 15 "possibili segreti" in `ai-mondo.json`, che erano solo indirizzi di articoli del tipo `sk-hynix-…`, simili alle chiavi `sk-…`. Il giro successivo li ha riconosciuti come falsi allarmi ed è tornato verde. Un controllo che preferisce un falso allarme a una chiave persa è la scelta giusta.

### Cosa fare se succede di nuovo

1. **Rigenera subito la chiave** sul sito del fornitore. È il passo che conta: togliere il file non basta, perché la cronologia di git è pubblica.
2. **Aggiorna il segreto** su GitHub (Settings → Secrets and variables → Actions) con la chiave nuova.
3. **Togli il valore** dal file e fai un commit. Rilancia il workflow a mano (Actions → Run workflow) per vedere che il giro è pulito.
4. **Trova come è uscita** (messaggio d'errore, URL con la chiave dentro, log) e fai passare quel testo da `_nascondi()` o allarga lo schema di `nascondi_chiavi.py`. È anche il consiglio scritto nel controllo di qualità.
5. Riscrivere la cronologia di git è possibile, ma non sostituisce il punto 1.

**In un colloquio:** "Un errore di un'API ha scritto una chiave in un file pubblico. L'ho tolta, ho aggiunto un filtro che maschera le chiavi in ogni messaggio e un passo automatico che ripulisce i file prima di ogni salvataggio. Poi un controllo quotidiano che diventa rosso se trova qualcosa che somiglia a una chiave. La lezione: i messaggi d'errore sono dati come gli altri, e finiscono dove finiscono i dati."

---

## 4.6 Il controllo qualità quotidiano

**Stato: in costruzione.** `STATO.md` (10/11/2026) dice "controllo qualità quotidiano in costruzione (raccolta/qualita/)". Stamattina sono comparsi i primi file:
- `raccolta/qualita/controlla_tutto.py`, il controllo;
- `raccolta/qualita/fatti_chiave.json`, 21 cifre dei report da confrontare con i dati;
- `docs/data/health.json`, il risultato leggibile dalla macchina;
- `report/qualita/2026-11-10.md`, il rapporto in inglese.

**Non è ancora un passo del workflow `aggiorna-dati.yml`**, quindi per ora gira solo a mano. Lo script era in lavorazione mentre questo capitolo veniva scritto: tra un giro e l'altro i risultati sono cambiati.

### Cosa controlla

Usa solo la libreria standard, non modifica i file degli altri e dura pochi minuti (il giro senza rete: 6 secondi). Le aree sono queste:

| Area | Cosa verifica |
|---|---|
| a) Freschezza | La data di ogni file confrontata con la cadenza attesa: quotidiano, settimanale, mensile per i livelli curati, statico. Le serie interne rimaste indietro |
| b) Schema | Ogni JSON si apre; lat/lon numerici e nel range; campi `fonte`, `link`, `data_fonte`, `affidabilita` presenti; cali di elementi oltre il 20% rispetto al giorno prima |
| c) Errori | I campi `errori` e `avvisi` di ogni file |
| d) Link | Un campione a rotazione di circa 150 link di fonti al giorno; un link è "rotto" dopo 2 controlli falliti di fila |
| e) Coerenza | Lo stesso fatto in file diversi: transiti negli stretti, punteggi di rischio, Brent e TTF, stoccaggi di gas; le cifre dei report contro i dati (`fatti_chiave.json`) |
| f) Segreti | Qualunque cosa somigli a una chiave in `docs/` → rosso, codice di uscita 2 |
| g) Licenze | Ogni file di `docs/data` ha una riga in `DATA_LICENSES.md` |
| h) Validatori | Lancia i validatori del repository e ne legge l'esito |
| + Smoke test | Il risultato di un test con il browser (Playwright), se c'è |

**La regola del semaforo:** rosso se c'è un segreto, un file illeggibile o mancante, oppure 3 o più problemi gravi; giallo (amber) se c'è un problema grave o medio; verde altrimenti. Per ogni tipo di problema lo script scrive anche **cosa fare** (campo `fix`).

### Il primo risultato (10/11/2026, 06:40 UTC, giro senza rete)

**Stato generale: AMBER.** Problemi: 0 critici, 1 grave, 43 medi, 8 lievi, 4 informativi. Le cose più utili da sapere:

- **Tutti i 66 file si aprono.** I 10 validatori del repository finiscono senza errori.
- **Il problema grave:** `esposizione-nord.json` non ha gli stoccaggi di gas di Paesi Bassi e Germania, anche se `scorte.json` li ha. Il motivo: `raccolta/nord/raccogli.py` cerca la chiave `GIE_API_KEY`, ma il workflow passa `AGSI_API_KEY`. Lo script salta la fonte con un avviso e il campo `errori` resta vuoto.
- **Coerenza:** 114 confronti, 9 differenze. Per esempio il Brent del 9/11 è 91,70 in `prezzi.json` e 93,65 in `stretti-dettaglio.json`, che aveva letto un valore provvisorio. Una cifra del report Hormuz (Brent a 92,62) non corrisponde più al dato.
- **Licenze:** 42 file su 67 hanno una riga in `DATA_LICENSES.md`; 25 mancano (i 24 del §4.1 più lo stesso `health.json`). Una riga (`analisti.json`) non ha più il file.
- **Freschezza:** 8 serie mensili di `scorte.json` sono ferme ad agosto (o luglio). `report.json` non ha un campo `aggiornato`.
- **Schema:** in `navi.json` mancano `link` e `affidabilita` sui 145 elementi; in `esposizione-nord.json` e `stretti-dettaglio.json` mancano i campi di fonte sugli elementi.
- **Link:** 9.384 link distinti trovati, non ancora controllati perché il giro era senza rete.
- **Smoke test:** non ancora disponibile (`smoke.json` assente).

### Come usarlo (e come raccontarlo)

- **Ogni mattina:** apri `report/qualita/<data>.md`. Se è verde, i dati sono a posto. Se è giallo o rosso, la tabella dei problemi dice file, problema e correzione.
- **Prima di citare un numero in un colloquio:** controlla in `health.json` che quel file non sia segnato come vecchio o incoerente.
- **In un colloquio:** "Il sistema si controlla da solo ogni giorno: freschezza dei dati, coerenza dello stesso numero in file diversi, link rotti, chiavi esposte, licenze mancanti. Il primo giro ha trovato un bug reale, una variabile con il nome sbagliato che faceva saltare in silenzio gli stoccaggi di gas, e un falso allarme di sicurezza, gestito. Un monitor del rischio deve prima di tutto monitorare se stesso."

---

### In sintesi

| Domanda del selezionatore | Risposta breve | Dove sta la prova |
|---|---|---|
| Da dove vengono i dati? | Fonti istituzionali (FMI, ENTSOG, Eurostat, EIA, Tesoro, USGS) più OSINT curato, ogni dato con fonte, link e data | Campo `fonti[]` di ogni file; `METODO.md` |
| Sono affidabili? | Affidabilità dichiarata su tre livelli, coordinate con precisione dichiarata, fatti separati dalle valutazioni | `METODO.md`; campi `affidabilita`, `precisione_km` |
| Puoi usarli? | Codice MIT, dati con le licenze delle fonti; alcune sono non commerciali; ho tolto ciò che non potevo ripubblicare | `DATA_LICENSES.md`; `report/licenze.md` |
| Quali sono i limiti? | AIS, ritardi di PortWatch, coordinate stimate, dati annuali del commercio, regole semplici: tutti scritti | `report/agenti/*.md`, sezioni "Limiti" |
| E la sicurezza? | Chiavi come segreti GitHub, mascheramento automatico, controllo quotidiano | `raccolta/comune/nascondi_chiavi.py`; `raccolta/qualita/` |
