# Capitolo 4 — Dati, fonti, licenze e limiti

Un selezionatore può chiederti «da dove prendi questo dato?», «puoi usarlo?» o «cosa succede se la fonte sbaglia?». Qui trovi le risposte, con il file del repository che le dimostra. Conteggi al 10 novembre 2026 (mattina); per il numero del giorno apri il file o `docs/data/health.json`, che li elenca tutti nel campo `counts`.

## 4.1 I file di `docs/data/`

La cartella contiene **67 file JSON**: 66 di dati più `health.json`, scritto dal controllo di qualità (§4.6). Il campo `fonti[]` di ogni file è il riferimento per fonte e licenza; `DATA_LICENSES.md` lo riassume e dal 10 novembre copre **tutti** i file.

**Aggiornamento:** **Q** = ogni giorno alle 04:37 UTC (`aggiorna-dati.yml`); **M** = mercati, lun–ven alle 21:30 UTC (`aggiorna-mercati.yml`); **S** = ogni domenica (`aggiorna-settimanale.yml`; *mens.* = solo la prima domenica del mese); **C** = curato o lanciato a mano; **F** = fisso (base cartografica o file scaricato una volta).

### A. Base cartografica e infrastrutture

| File | Contenuto | Fonte principale | Agg. | Elementi | Licenza |
|---|---|---|---|---|---|
| `world.json`, `medio-oriente.json`, `labels.json` | Mondo 1:50m, Medio Oriente 1:10m, etichette | Natural Earth | F | — | Pubblico dominio |
| `manifest.json` | Livelli e viste della mappa | Progetto | F | 7 viste | MIT |
| `linee.json`, `condotte.json` | Oleodotti e gasdotti; condotte in mare | Global Energy Monitor | F | 588; 454 | CC BY 4.0 |
| `terminali-gnl.json` | Terminali GNL | GEM | Q | 840 | CC BY 4.0 |
| `nucleare.json`, `rete-elettrica.json`, `interconnessioni.json` | Centrali; linee ≥380 kV e HVDC; interconnessioni | GEM; OpenStreetMap via OpenInfraMap; Terna, ENTSO-E, PyPSA-Eur | S | 167; 2.367; 16 | CC BY 4.0; **ODbL 1.0** |
| `gas-italia.json` | Flussi giornalieri ai punti d'ingresso italiani | ENTSOG | Q | 11 | Riuso con citazione |
| `cavi.json`, `cavi-incidenti.json` | Cavi sottomarini; incidenti 2023–2026 | TeleGeography; stampa | S | 713; 14 | **CC BY-NC-SA 3.0** |
| `ferrovie.json` | Rete, corridoi, incidenti | Natural Earth + schede curate | S | 49 | Pubblico dominio; fatti citati |
| `rotte.json` | Rotte marittime | Benden (2022) | F | 239 | **CC BY-NC 4.0** |
| `stretti.json`, `stretti-dettaglio.json` | Quote mondiali; 13 schede approfondite (circa 100 fonti) | IEA, EIA, Lloyd's List, stampa | F; Q (parte automatica) | 16; 13 | Fatti citati |

### B. Navi, flussi, noli, porti

| File | Contenuto | Fonte principale | Agg. | Elementi | Licenza |
|---|---|---|---|---|---|
| `portwatch.json` | Transiti negli stretti e approdi nei porti italiani | IMF PortWatch | Q | 13 passaggi + 9 porti | Termini FMI, citazione |
| `porti-nord.json` | Porti del Mare del Nord e del Baltico | PortWatch, autorità portuali | Q | 30 | Citazione |
| `navi.json` | Ultime posizioni AIS | Digitraffic, aisstream.io, USNI | Q | 145 + 36 militari USA | CC BY 4.0; termini aisstream; **CC BY-NC 4.0** (GFW) |
| `sanzioni-navi.json` | Navi sanzionate da USA, Regno Unito, UE | OFAC, UK, OpenSanctions | Q | 2.022 | Pubblico dominio; OGL; **CC BY-NC 4.0** |
| `noli.json` | Indici dei noli container | Drewry, Freightos, SSE | Q | 4 | **Indici proprietari**: solo valori citati |
| `transit-times.json`, `port-risk.json`, `rischio.json` | Tempi di viaggio; indice dei porti; cruscotto | Calcoli del progetto su altri file | Q | 99; 39; 18 | Licenze delle fonti di partenza |
| `assicurazioni.json` | Aree war risk e premi | Joint War Committee, stampa | S | 27 aree | Documenti pubblici, fatti citati |
| `bunker-emissioni.json` | Bunker, EUA, ETS, FuelEU | Ship & Bunker, EEX, EUR-Lex | Q | 24 porti | Valori citati |

### C. Energia, scorte, Paesi, mercati

| File | Contenuto | Fonte principale | Agg. | Elementi | Licenza |
|---|---|---|---|---|---|
| `scorte.json` | Gas UE, petrolio USA, scorte di emergenza, grano, oro | GIE AGSI+, Eurostat, EIA, USDA, FMI | Q | 44 serie | Citazione; FMI non commerciale senza permesso |
| `esposizione-nord.json`, `offshore-nord.json` | 10 Paesi del Nord; parchi eolici e piattaforme | Eurostat, IEEFA, EMODnet | Q | 10; 180 parchi | CC BY 4.0 |
| `paesi.json`; `commercio.json`, `minerali.json` | 33 schede Paese; commercio e minerali critici | FMI, Banca Mondiale, SIPRI, UN Comtrade, USGS | S; mens. | 33; 38 Paesi; 25 minerali | Mista; **SIPRI non commerciale** |
| `gpr.json`, `calendario.json` | Rischio geopolitico; agenda | Caldara-Iacoviello; Fed, BCE, EIA… | Q | 18 serie; 215 eventi | Citazione |
| `italia-impatti.json`, `simulatore.json` | Impatti in Italia; regole del simulatore | MASE, GME, Istat; progetto | Q; C | 99; 9 passaggi | Dati pubblici |
| `prezzi.json` | Chiusure di indici, materie prime, cambi, tassi | Yahoo Finance (29), Tesoro USA (4) | M | 33 serie | Tesoro: pubblico dominio. Yahoo: **solo uso personale** |
| `mercati.json` | Mercati di una giornata | Stampa | C | 1 | Fatti citati |

### D. Militare, Ucraina, eventi

| File | Contenuto | Fonte principale | Agg. | Elementi | Licenza |
|---|---|---|---|---|---|
| `fissi.json`, `italia.json`, `iran.json`, `difesa.json`, `mobili.json` | Basi, porti, siti militari, difese, unità mobili | OurAirports, WPI, Wikidata, USNI, stampa | C | 192; 58; 53; 8; 53 | Pubblico dominio / CC0; fatti citati |
| `basi-mondo.json` | Basi militari nel mondo | OurAirports, Wikidata, CRS | S | 181 | CC0; fatti citati |
| `eventi.json`, `ibrido.json`, `baltico-sicurezza.json` | Eventi recenti; minacce ibride; sicurezza Baltico | Stampa, comunicati, OSINT, GPSJam | C; C; Q | 126; 35; 48 eventi | Fatti citati |
| `fronte.json`, `fronte-storico.json` | Link alle mappe del fronte; km² mensili | ISW, DeepState | C | 4 link; 60 istantanee | Nessuna geometria ripubblicata |
| `ucraina-storico.json`, `attacchi-russi.json` | Lanci e abbattimenti, attacchi ucraini in Russia; attacchi russi | Dataset Ivaniuk; Kyiv Independent | Q | 258; 192 | **CC BY-NC-SA 4.0** |
| `attacchi-analisti.json`, `cyber-energia.json` | Attacchi dai Telegram di Molin e AMK; incidenti cyber | Canali pubblici; CERT Polska, CISA… | Q; C | 4.093; 30 | Solo fatti, estratto ≤160 caratteri e link |

### E. AI, transizione, notizie

| File | Contenuto | Agg. | Elementi | Licenza |
|---|---|---|---|---|
| `ai.json`, `dossier.json` | Infrastrutture AI USA; dossier | C | 25; 1 | CC BY 4.0 (Epoch); fatti citati |
| `ai-mondo.json`, `investimenti.json`, `supply-chain-ai.json` | AI fuori dagli USA; investimenti; catena del valore | S | 82; 64; 70 nodi | CC BY 4.0; fatti citati; ODbL |
| `idrogeno.json`, `eolico-filiera.json`, `webcam.json` | Idrogeno nei porti; filiera eolica; webcam | S | 41; 19 porti; 45 | Fatti citati; solo link per le webcam |
| `wind-calendar.json` | Calendario eolico 2023–2027 | Q (validazione) | 114 | Fatti citati |
| `notizie.json`, `notizie-testate.json` | Notizie OSINT 7 giorni; testate 3 giorni | Q | 512; 1.049 | Titolo, data, link, sommario breve |
| `report.json` | Report giornalieri | C | 5 | Testo del progetto |

## 4.2 Le fonti principali

Per ogni fonte: chi è, perché fidarsi, cosa dà. «Perché fidarsi» non vuol dire «è sempre giusta»: vuol dire fonte primaria o riconosciuta, con un metodo pubblico. I limiti sono nel §4.4.

**Navi, porti, stretti.** **IMF PortWatch** (Fondo monetario internazionale con l'Università di Oxford) stima transiti e approdi dai segnali AIS con un metodo uguale per tutti, con serie dal 2023: è la base dei transiti, del rischio, dei tempi di viaggio e del Port Risk Index. **Digitraffic** (agenzia finlandese del traffico, CC BY 4.0) e **aisstream.io** (ricevitori volontari, chiave gratuita) danno le posizioni AIS: nell'ultima esecuzione 96 petroliere nel Golfo di Finlandia, 38 sanzionate, e 19 negli Stretti danesi. **USNI Fleet Tracker** dà l'area di portaerei e gruppi USA (in mappa al centro dell'area, precisione 250–2.000 km). Il **Joint War Committee** (assicuratori di Londra) pubblica le circolari con le *listed areas*: è la fonte primaria del mercato; i **premi**, invece, sono quotazioni riportate dalla stampa.

**Energia e scorte.** **Global Energy Monitor** censisce condotte, terminali GNL e centrali, progetto per progetto, in CC BY 4.0 (condotte da file di lavoro del 5 novembre 2026, non dalla release ufficiale). **ENTSOG** pubblica per regolamento UE i flussi fisici del gas. **GIE AGSI+** è il riferimento per il riempimento degli stoccaggi (chiave gratuita). **Eurostat** è ufficiale ma lento (ultimo dato agosto–settembre 2026). **EIA** (governo USA, pubblico dominio) dà le scorte settimanali di petrolio USA. **Ship & Bunker** è lo standard di fatto per i prezzi pubblici del bunker (medie, non transazioni). **EEX** gestisce le aste delle quote EUA: 86,91 € il 9 novembre. **EMODnet** (Commissione UE) dà i poligoni dei parchi eolici.

**Macro, commercio, Paesi.** **Tesoro USA**: curva dei rendimenti, ufficiale. **Yahoo Finance**: le altre 29 serie di `prezzi.json`, perché è l'unica fonte gratuita e giornaliera per tutte (FRED e Stooq rifiutano il server cloud). **FMI** (WEO ottobre 2026, riserve d'oro), **Banca Mondiale**, **UN Comtrade** (commercio dalle dichiarazioni doganali), **USGS** (minerali, pubblico dominio), **SIPRI** (spesa militare, uso non commerciale). **Epoch AI** (CC BY 4.0) per i data center AI.

**Ucraina.** **ISW** e **DeepStateMap** sono autorevoli e indipendenti tra loro, ma nessuno dei due permette di ripubblicare le geometrie: il sito mostra solo **link** e, per lo storico, valori derivati (km²). Il **Kyiv Independent** è la fonte principale degli eventi curati (di parte ucraina, ma con redazione e correzioni pubbliche). Il **dataset di Petro Ivaniuk** trascrive i comunicati dell'Aeronautica ucraina (CC BY-NC-SA 4.0). I canali Telegram di **Clément Molin** e **AMK Mapping**: al 10 novembre 4.093 attacchi geolocalizzati 2024–2026, aggiornati ogni giorno; affidabilità «media» se segnalati da un solo analista, «alta» se confermati da un'altra fonte.

**Notizie.** 93 feed di 57 testate e 35 fonti OSINT e ufficiali (UKMTO, JMIC, MARAD, gCaptain, USNI…), ognuna con affidabilità e paywall dichiarati. Si tengono solo titolo, data, link e un sommario breve.

## 4.3 Licenze e scelte prese

- **Il codice è MIT** (`LICENSE`). **I dati no**: ogni file resta sotto la licenza delle sue fonti.
- Il progetto è personale e gratuito: le fonti **non commerciali** sono ammesse, ma `report/licenze.md` lo chiama «una zona grigia» per un portfolio usato per cercare lavoro.
- **In un'azienda cambia tutto**: usarlo dentro un porto o un operatore è uso commerciale, e le fonti NC vanno sostituite.

**Non commerciali o share-alike:** TeleGeography (cavi, CC BY-NC-SA 3.0); Benden (rotte e tracciati dei tempi di viaggio, CC BY-NC 4.0); Global Fishing Watch e OpenSanctions (CC BY-NC 4.0); Ivaniuk (CC BY-NC-SA 4.0); SIPRI (non commerciale); FMI (uso commerciale con permesso); IFES ElectionGuide (da verificare); OpenStreetMap e PyPSA-Eur (ODbL, share-alike).

| Cosa è stato tolto o limitato | Perché | Scelta |
|---|---|---|
| Aree del fronte di @Majakovsk73 (28 aree, 91 punti) | Nessuna licenza dichiarata, permesso non ottenuto | Tolte; resta un link. Copie private in `raccolta/fronte/privato/`, escluse da git |
| Poligoni DeepState | L'accordo vieta di ridistribuire i dati dell'API | Solo km², variazioni, momenti chiave |
| ISW | Serve «the written consent of ISW» | Modulo `docs/isw-fronte.js` pronto ma **non attivo** |
| Baltic Dry da Trading Economics | Termini che vietano la raccolta automatica | Raccolta tolta; da citare a mano |
| Prezzi Yahoo | Nessuna licenza, ridistribuzione vietata | Pubblicati solo ~3 mesi (66 punti per serie) |
| Sezione analisti YouTube | Contenuti con tutti i diritti riservati | Tolta del tutto il 10 novembre su tua decisione |
| Noli Drewry, Freightos, SSE | Indici proprietari | Solo l'ultimo valore con fonte e data |

> **Cosa dire al colloquio.** «Ogni file ha un campo con fonte, link, licenza e data. Ho separato la licenza del codice (MIT) da quella dei dati, file per file. Dove una fonte non mi dava il permesso di ripubblicare, ho tolto il dato: i poligoni del fronte, il Baltic Dry preso in automatico, gli storici completi di Yahoo. Al loro posto metto un link o valori derivati. So anche quali fonti sono non commerciali: in azienda saprei quali sostituire.» Alternative già indicate in `report/licenze.md`: atti UE su EUR-Lex al posto di OpenSanctions; EIA, BCE e Banca Mondiale al posto di Yahoo per materie prime e cambi; GSCPI della New York Fed e PortWatch al posto del Baltic Dry; un estratto Geofabrik al posto delle tessere OpenInfraMap.

<div></div>

> **Attenzione.** Cose ancora aperte: la **cronologia di git è pubblica**, quindi ciò che era stato pubblicato prima delle correzioni (poligoni di @Majakovsk73, un anno di Yahoo, la chiave AGSI) resta nella storia del repository; nei file non c'è traccia di richieste di permesso inviate a @Majakovsk73, DeepState o ISW (la cartella `report/permessi/` prevista non esiste); la riga di `noli.json` in `DATA_LICENSES.md` e il suo campo `fonti[]` citano ancora il Baltic Exchange via Trading Economics; OpenSanctions non è ancora stato sostituito.

## 4.4 Limiti onesti, con la risposta pronta

| Limite | Come rispondere |
|---|---|
| **AIS spento, falso o assente.** La flotta ombra trasmette a intermittenza; `navi.json` ha registrato petroliere «nell'entroterra russo» a 46–81 nodi; per Hormuz, Bab el-Mandeb, Suez e Bosforo oggi non c'è nessuna fonte gratuita | «È dichiarato nel dato: un'area senza fonte dice che non vuol dire zero navi; le posizioni impossibili sono segnalate e non disegnate. Per gli stretti uso PortWatch, che è un'altra misura. Per le navi *dark* servirebbero dati satellitari a pagamento: limite di budget, non di metodo.» |
| **PortWatch in ritardo.** Circa una settimana per gli stretti, circa 10 giorni per i porti del Nord; mancano Dardanelli, Canale di Sicilia, Grande Belt | «È un indicatore strutturale: lo uso per le tendenze e i confronti con gli anni prima, non per dire cosa succede oggi. Kerch a zero vuol dire "nessun segnale", non per forza "nessuna nave".» |
| **Coordinate stimate.** Navi USA al centro dell'area; attacchi in Ucraina al centro abitato o all'oblast; incidenti ai cavi sempre stimati | «Ogni punto ha `origine_coord` e `precisione_km`. Non pubblico più di quanto pubblica la fonte: è analisi, non tracciamento.» |
| **Commercio annuale e precedente alla crisi.** Comtrade 2024–2025, quote in valore, Paese di spedizione per gli acquisti intra-UE | «Il commercio dà la struttura dell'esposizione; lo shock lo leggo in PortWatch, noli e prezzi.» |
| **Simulatore a regole semplici.** `simulatore.json` elenca 10 limiti | «È uno strumento per ragionare, non per prevedere: preferisco un "non disponibile" a un numero inventato.» |
| **Rischio: valutazioni, non previsioni.** I giudizi strutturali pesano il 55% dell'impatto; il Port Risk Index ha uno storico vero solo da novembre 2026 | «Le regole sono esplicite: si può non essere d'accordo con una soglia, ma si vede quale.» |
| **Investimenti: annunci, non spesa.** 64 voci curate; idrogeno «non un censimento» | «Distinguo lo stato del progetto (annunciato, FID, costruzione, operativo).» |
| **Fonti di parte.** Lanci e abbattimenti sono dichiarazioni ucraine; tra DeepState e ISW ci sono differenze fino a 4.500 km² | «Affidabilità a tre livelli; saldi mensili sotto il margine li leggo come "fronte fermo".» |
| **Prezzi non ufficiali.** Yahoo «può cambiare formato»; premi war risk di seconda mano | «I tassi vengono dal Tesoro; il resto è contesto, marcato come indicativo, e il controllo di qualità confronta lo stesso prezzo tra file diversi.» |
| **Dati lenti e voci manuali.** Eurostat con 2–3 mesi di ritardo; ferrovie Natural Earth ferme al 2017 circa; fonti non raggiungibili dalla sessione cloud (eia.gov, Overpass, Reuters) citate tramite ristampe | «Ogni dato ha la sua data e il controllo quotidiano segnala i file vecchi rispetto alla loro cadenza.» |

> **Cosa dire al colloquio.** Regola generale per le domande sui limiti: ammetti il limite, indica dove è dichiarato (campo del file o rapporto), spiega cosa hai fatto per contenerlo e cosa faresti con più risorse. Non difendere un numero oltre quello che la fonte dice.

## 4.5 Sicurezza: le chiavi API

Le chiavi sono **segreti di GitHub** (*Settings → Secrets and variables → Actions*), passate agli script come variabili d'ambiente (`AISSTREAM_API_KEY`, `GFW_API_KEY`, `AGSI_API_KEY`, `BLS_API_KEY`). Se manca una chiave, lo script salta la fonte con un avviso. Altre chiavi facoltative sono riconosciute ma non passate dal workflow (`EIA_API_KEY`, `FIRMS_MAP_KEY`…).

**Il caso della chiave AGSI.** Al primo giro del workflow, il 9 novembre 2026, la chiamata ad AGSI+ ha dato un errore; lo script ha scritto il messaggio nel campo `errori` di `scorte.json`, e il messaggio conteneva la chiave. La correzione (commit `9daa0a0`, 9 novembre): chiave tolta dal file; in `raccolta/scorte/raccogli.py` ogni avviso passa da una funzione che maschera i valori `*_KEY`/`*_TOKEN`; lo script `raccolta/comune/nascondi_chiavi.py` gira **prima di ogni salvataggio** su tutti i file pubblici. Oggi l'errore si legge così: `AGSI+ EU: API key: [nascosta]`.

> **Attenzione.** La chiave resta nella cronologia di git, quindi **va rigenerata** sul sito di GIE e aggiornata nei Secrets (`STATO.md`). Nei file non risulta che sia stato fatto: è la prima cosa da fare (§5.6).

**Se succede di nuovo:** (1) rigenera subito la chiave, è il passo che conta; (2) aggiorna il segreto su GitHub; (3) togli il valore dal file e rilancia il workflow a mano; (4) trova come è uscita e allarga il mascheramento; (5) riscrivere la cronologia di git è possibile, ma non sostituisce il punto 1.

## 4.6 Il controllo di qualità quotidiano

Dal 10 novembre 2026 è un passo di `aggiorna-dati.yml`, subito dopo un test con il browser (*smoke test*, `raccolta/qualita/smoke.js`). Lo script `raccolta/qualita/controlla_tutto.py` usa solo la libreria standard, non modifica i file degli altri e scrive `docs/data/health.json` e un rapporto leggibile in `report/qualita/<data>.md`.

| Area | Cosa verifica |
|---|---|
| Freschezza | data di ogni file contro la cadenza attesa (quotidiano, settimanale, mensile, statico) |
| Schema | ogni JSON si apre; coordinate valide; campi di fonte presenti; cali di elementi oltre il 20% sul giorno prima |
| Errori | i campi `errori` e `avvisi` di ogni file |
| Link | un campione a rotazione di circa 150 link al giorno; «rotto» dopo 2 controlli falliti di fila |
| Coerenza | lo stesso fatto in file diversi (transiti, rischio, Brent e TTF, stoccaggi) e le cifre chiave dei report contro i dati (`fatti_chiave.json`) |
| Segreti | qualunque cosa somigli a una chiave in `docs/` → rosso |
| Licenze | ogni file ha una riga in `DATA_LICENSES.md` |
| Validatori e smoke test | i 10 validatori del repository e il test con il browser |

**Semaforo:** rosso se c'è un segreto, un file illeggibile o mancante, o 3 o più problemi gravi; giallo (*amber*) con un problema grave o medio; verde altrimenti. Per ogni problema lo script scrive anche **cosa fare** (campo `fix`).

**Il risultato del 10 novembre 2026, 06:52 UTC: AMBER** (0 critici, 1 grave, 39 medi, 3 lievi, 4 informativi). Tutti i file si aprono; i 10 validatori finiscono senza errori; nessun segreto; smoke test 46 superati su 46; 150 link controllati, nessuno rotto. Il problema grave è quello di `esposizione-nord.json` senza gli stoccaggi di Paesi Bassi e Germania: lo script del Nord cercava `GIE_API_KEY` mentre il workflow passa `AGSI_API_KEY`. Lo script è stato corretto lo stesso giorno (ora legge entrambe); il dato si sistema al giro successivo. Il primo giro del mattino aveva anche dato un falso allarme (indirizzi di articoli `sk-hynix-…` scambiati per chiavi `sk-…`), poi corretto: un controllo che preferisce un falso allarme a una chiave persa è la scelta giusta.

> **Cosa dire al colloquio.** «Il sistema si controlla da solo ogni mattina: freschezza, coerenza dello stesso numero in file diversi, link rotti, chiavi esposte, licenze mancanti, più un test della mappa nel browser. Il primo giro ha trovato un bug reale, una variabile con il nome sbagliato che faceva saltare in silenzio gli stoccaggi di gas. Un monitor del rischio deve prima di tutto monitorare se stesso.»

**Come usarlo:** ogni mattina apri `report/qualita/<data>.md`; prima di citare un numero in un colloquio controlla in `health.json` che quel file non sia segnato come vecchio o incoerente.
