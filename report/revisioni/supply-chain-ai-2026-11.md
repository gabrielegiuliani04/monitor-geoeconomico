# Revisione: «La catena dell'AI, dalla miniera al data center» (novembre 2026)

**Revisore:** revisione indipendente (fact-checking ed editing), svolta con un assistente AI · **Date:** 9 novembre 2026 sera e 10 novembre 2026
**Testo rivisto:** [`report/supply-chain-ai-2026-11.md`](../supply-chain-ai-2026-11.md) e [`docs/report/supply-chain-ai-2026-11.html`](../../docs/report/supply-chain-ai-2026-11.html), generati da [`report/costruisci_supply_chain_ai.py`](../costruisci_supply_chain_ai.py) a partire da [`docs/data/supply-chain-ai.json`](../../docs/data/supply-chain-ai.json) (voci curate in [`raccolta/supply-chain-ai/`](../../raccolta/supply-chain-ai/))
**Standard di riferimento:** [`report/STANDARD.md`](../STANDARD.md)

## Sintesi

- Affermazioni verificate: **110** (ogni numero del testo, delle tabelle per anello e dei fatti datati): **62 confermate, 32 corrette, 16 non verificabili da qui**.
- Le correzioni sono fatte **alla fonte** (voci curate e script), poi i file sono stati rigenerati: `raccogli.py --oggi 2026-11-10`, poi `costruisci_supply_chain_ai.py`. Nessuna modifica a mano del Markdown o della pagina.
- **Scadenza cinese del 10 novembre sulle terre rare.** Il 9 novembre le fonti erano in conflitto. Stato al 10 novembre: il MOFCOM ha **annunciato** la proroga di due mesi, fino al 10 gennaio 2027, con una breve dichiarazione del 9 novembre (Reuters, ripreso da The Star); Shanghai Metals Market ne riporta il testo come annuncio MOFCOM-Dogane n. 58 del 2026. Ma l'elenco ufficiale degli annunci 2026 sul sito del MOFCOM, letto il 9 e il 10 novembre, si ferma al n. 52 del 26 ottobre: **il testo non è verificato sulla fonte primaria**. Tech Times, che scriveva «nessuna proroga pubblicata», è uscito il 9 novembre prima dell'annuncio. Nel report la misura ora risulta «sospesa fino al 10 gennaio 2027; proroga annunciata, testo primario non reperito», nel testo, nella tabella dei controlli, nell'indicatore e in un riquadro in testa. Il divieto verso gli USA su gallio e germanio resta sospeso fino al 27 novembre: nessuna proroga trovata.
- **Data di riferimento spostata al 10 novembre.** Nella notte `prezzi.json` è stato aggiornato (03:40 UTC): le chiusure USA del 9 novembre sono ora definitive e diverse dalla lettura provvisoria delle 19:47 usata dalla prima versione; SK Hynix è alla seduta del 10 novembre, ancora provvisoria. Il report lo dice tabella per tabella.
- **Pagina più corta su telefono.** Altezza a 390 px: da circa 69.000 px a **circa 23.000 px** (Playwright, Chromium, tutto chiuso; 79.000 px con tutti i blocchi aperti). A 1440 px: circa 14.000 px. Riassunto in alto (In breve + riquadro delle scadenze), un solo blocco comprimibile per anello con indicatori, nodi, titoli e cose da seguire, paragrafi di approfondimento comprimibili (le valutazioni restano visibili), tabelle lunghe (tutti gli indicatori, i 34 collegamenti) nell'appendice in fondo. Nessun contenuto tolto, salvo le cifre non verificate o sbagliate elencate sotto. Nessuno scorrimento orizzontale a 390 px, temi chiaro e scuro controllati.

Metodo: lettura diretta dei file con Python; confronto delle quote USGS con le tabelle dei PDF (scaricati e convertiti in testo); 109 link del report e del file di dati scaricati il 9 novembre (86 raggiungibili, 17 con 403, 1 con 404, 1 con 429, 2 senza risposta, 2 vuoti), più ricerche mirate il 10 novembre (comunicato ASML depositato alla SEC, elenco annunci MOFCOM, Reuters, Counterpoint via SamMobile, sommario IEA, Trading Economics). Coerenza controllata con `ai-mondo.json`, `investimenti.json`, `minerali.json`, `commercio.json`, `portwatch.json`, `prezzi.json`, `cavi-incidenti.json`, `stretti-dettaglio.json`.

## 1. Tabella di verifica

Esiti: **ok** = corrisponde; **corretto** = sbagliato, impreciso o senza fonte, corretto alla fonte; **n.v.** = non verificabile da qui (pagina bloccata o a pagamento, fonte non indicata).

### In breve e materie prime

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 1 | Gallio, quota cinese della produzione primaria | 99% | «China accounted for 99%» (2025) | USGS MCS 2026 Gallium; minerali.json | ok |
| 2 | Terre rare, quota cinese dell'estrazione | 69,2% | 270.000 / 390.000 t = 69,2%; identico in minerali.json | USGS MCS 2026 Rare Earths | ok |
| 3 | Terre rare, USA e Australia | 13,1% e 7,4% | 51.000 e 29.000 t su 390.000 | USGS | ok |
| 4 | Silicio metallico: Cina, Brasile, Norvegia | 87,0 / 3,9 / 2,8% | 4.000, 180, 130 su 4.600 (migliaia di t) | USGS MCS 2026 Silicon; minerali.json | ok |
| 5 | Rame: Cile, Congo, Perù (miniera) | 23,0 / 13,9 / 11,7% | 5.300, 3.200, 2.700 su 23.000 | USGS MCS 2026 Copper | ok |
| 6 | Rame raffinato: Cina | 48,3% | 14.000 su 29.000 | USGS; minerali.json (rame-raffinato) | ok |
| 7 | Tantalio: Congo, Ruanda, Nigeria; Congo+Ruanda | 52 / 16 / 15,6%; 68% | 1.300, 400, 390 su 2.500 | USGS MCS 2026 Tantalum | ok |
| 8 | Fluorite: Cina, Messico, Mongolia | 60 / 15 / 15% | 6.000, 1.500, 1.500 su 10.000 | USGS MCS 2026 Fluorspar | ok |
| 9 | Elio: USA, Qatar, Russia | 42,6 / 33,2 / 9,5% | 81, 63, 18 su 190 milioni di m³ | USGS MCS 2026 Helium | ok |
| 10 | Neon: «primo produttore» Stati Uniti 13,8% | Stati Uniti 13,8% come primo produttore | 110 su 800 milioni di litri, ma USGS pubblica solo gli USA e «altri paesi» 700 | USGS MCS 2026 Helium | corretto (presentato come unico dato pubblicato, non come primo produttore) |
| 11 | Groenlandia, riserve di terre rare | 1,5 milioni di t | 1.500.000 t, produzione nulla | USGS | ok |
| 12 | Germanio: quota mondiale mancante | dato mancante | «global production data were limited» | USGS MCS 2026 Germanium | ok |
| 13 | Quarzo di Spruce Pine: 70–90% (Everstream), oltre 80% (BloombergNEF) | 70–90%; 80% | la pagina BNN Bloomberg non restituisce l'articolo; USGS conferma solo due produttori a Spruce Pine | BNN Bloomberg; USGS Quartz | n.v. |
| 14 | Altre materie sotto licenza cinese: magnesio, tungsteno, grafite, antimonio | assente | 86,4 / 78,7 / 77,8 / 36,1% | minerali.json (USGS 2025) | corretto (aggiunto) |
| 15 | Coerenza delle quote con minerali.json | — | gallio, silicio, terre rare, rame identiche (controllo ora automatico in raccogli.py) | minerali.json | ok |
| 16 | Licenze cinesi su gallio e germanio | 3 luglio 2023, in vigore | annuncio 3/7, in vigore dal 1/8/2023 | USGS Gallium; Tech Times | ok |
| 17 | Divieto verso gli USA (dicembre 2024) sospeso fino al 27/11/2026 | 27 novembre 2026 | sospeso il 9/11/2025 fino al 27/11/2026 (annuncio 72) | Fastmarkets 11/11/2025; Tech Times 9/11/2026 | ok |
| 18 | Giorni alla scadenza del 27 novembre | 18 (al 9/11) | 17 al 10/11 | calcolo | corretto (data di riferimento 10/11) |
| 19 | Data della fonte per le scadenze | 2026-11-09 per Fastmarkets | articolo dell'11/11/2025: lo script scriveva il giorno del calcolo | raccogli.py | corretto (nello script) |
| 20 | Licenze di aprile 2025 su sette terre rare | 7 elementi, in vigore | samario, gadolinio, terbio, disprosio, lutezio, scandio, ittrio; mai sospese | USGS; Tech Times | ok |
| 21 | Misure di ottobre 2025: cinque terre rare, regola dello 0,1%, annunci 55–62, sospese fino al 10/11/2026 | incerto fino al 10/11 | sospese dall'annuncio 70 fino al 10/11/2026 | Tech Times | ok |
| 22 | Proroga al 10 gennaio 2027 | «le fonti non concordano» | il MOFCOM l'ha annunciata il 9/11 con una breve dichiarazione (Reuters); SMM ne riporta il testo come annuncio n. 58/2026; l'elenco ufficiale MOFCOM, letto il 9 e il 10/11, si ferma al n. 52 del 26/10 | Reuters via The Star 9/11; SMM 9/11; mofcom.gov.cn | corretto (stato: proroga annunciata, non verificata sulla fonte primaria) |
| 23 | Tech Times: «nessun testo sposta la data» | fonte in conflitto | articolo basato su verifiche fino al 7/11, uscito prima dell'annuncio | Tech Times 9/11 | corretto (spiegata la divergenza) |
| 24 | Divieto cinese di export di elio | assente | annuncio MOFCOM-Dogane n. 29 del 10/7/2026, in vigore | mofcom.gov.cn | corretto (aggiunto) |
| 25 | Cina, quota dell'elio mondiale | assente | 3 su 190 = 1,6% | USGS | ok (aggiunto) |
| 26 | Qatar: produzione di elio ferma «da marzo» | in gran parte ferma da marzo | QatarGas ferma il 2 marzo, forza maggiore il 4; stato attuale senza fonte primaria | AP via WTOP, marzo 2026 | corretto (data precisata; stato attuale n.v.) |
| 27 | Perché lo shock non ha colpito i chip | scorte, carichi in viaggio, elio americano | contratti di lungo periodo, fornitori diversi, caverne di stoccaggio, scorte negli impianti | Morningstar/Dow Jones 25/6/2026 | corretto |
| 28 | Rubaya, quota mondiale | circa 15% del coltan (stampa di settore) | «around 15% of global tantalum supply» (Global Witness); frana con oltre 200 morti a fine gennaio 2026 | IntelliNews; Argus 12/2/2026 | corretto (fonte e perimetro) |
| 29 | Rubaya in mano a M23 da aprile 2024 | aprile 2024 | aprile 2024 | IntelliNews (Global Witness) | ok |
| 30 | Narva: 2.000 t/anno, poi 5.000 | 2.000 / 5.000 | identici | SMM 2025 | ok |
| 31 | Sillamäe: terbio e disprosio dal 2026 | — | prima produzione di ossidi di terbio e disprosio | SMM 2026 | ok |

### Logistica e Hormuz

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 32 | Hormuz, navi al giorno, settimana 26/10–1/11 | 4,4 | 4,4 (90,3 un anno prima) | portwatch.json | ok |
| 33 | Hormuz, variazione su un anno | −95% | −95,1% | portwatch.json | ok |
| 34 | Stretto di Taiwan, navi al giorno e variazione | 247; +7,1% | 247,0; +7,1% sulla stessa settimana 2025 | portwatch.json | ok (aggiunto il termine di confronto) |
| 35 | Danni a cavi intorno a Taiwan, ultimi 365 giorni | 1 | 1 (Matsu, 29/4/2026) | cavi-incidenti.json | ok |
| 36 | «Ci passa metà delle portacontainer del mondo» | metà; fonte CSIS | il 48% delle 5.400 portacontainer è passato almeno una volta tra gennaio e luglio 2022; CSIS non lo dice | Bloomberg via SupplyChainBrain (stretti-dettaglio.json) | corretto |
| 37 | Bloomberg Economics: 10.600 miliardi, 9,6% del PIL | «un blocco o un conflitto» | cifre giuste, ma riferite a una guerra USA–Cina, scenario estremo | Insurance Journal 12/2/2026 | corretto |
| 38 | Rhodium: fino a 1.600 miliardi di ricavi l'anno | 1.600 mld | «as much as $1.6 trillion… in the event of a blockade»; studio del 2022 | Rhodium | ok (precisato blocco e anno) |
| 39 | TSMC: oltre il 70% delle macchine recuperate in 10 ore (aprile 2024) | 70%, 10 ore | identici | Tom's Hardware | ok |
| 40 | EUV: circa 40 container, 20 camion, 3 Boeing 747 | 40 / 20 / 3 | Asia Times (429) e DHL non raggiungibili | — | n.v. |
| 41 | High-NA in Oregon in 43 container | 43 | fonte non indicata nel testo | — | n.v. |
| 42 | EVA Air: AI 40–50% del cargo; Nord America 70% | 40–50%; 70% | DIGITIMES: 403 | — | n.v. |

### Macchine per fare chip

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 43 | ASML 3° trimestre 2026: 113 sistemi nuovi, 11,7 miliardi di euro | 113; 11,7 | 113 nuovi (86 nel 2°), 8 usati; 11.662 milioni | comunicato ASML 14/10/2026 (SEC, 6-K) | ok (link sostituito: Seeking Alpha 403) |
| 44 | Guida 2026 | 44–45 miliardi | 44–45 miliardi di euro | comunicato ASML | ok |
| 45 | Cina circa il 20% delle vendite 2026 | 20% | il comunicato di ottobre non dà la quota; il 20% è nella trascrizione di luglio (ai-mondo.json); XenoSpectrum 403 | ai-mondo.json | n.v. su fonte primaria (marcato) |
| 46 | Quota di ASML in Carl Zeiss SMT | 24,9% | la fonte citata dice 25% | The Value Edge | corretto («circa un quarto») |
| 47 | Affidabilità di The Value Edge | media | l'autore dichiara un'analisi generata con ChatGPT Deep Research | The Value Edge | corretto (bassa) |
| 48 | BIS 2/12/2024: 24 tipi di macchine, 3 software, HBM, 140 entità | 24 tipi, HBM, 140 | 24 tipi, 3 software, HBM, 140 entità + 14 modifiche | BIS | ok (aggiunti i software) |
| 49 | Giappone: 23 tipi «sotto licenza fuori dai 42 paesi amici» | fuori dai 42 | licenza verso tutti i paesi; procedura semplificata per 42 | Hogan Lovells | corretto |
| 50 | Paesi Bassi: NXT:1970i e 1980i dal 7/9/2024 | 7 settembre 2024 | effettiva dal 7 settembre | Export Compliance Daily | ok |
| 51 | Paesi Bassi: DUV più avanzate dal 1/9/2023 | 1 settembre 2023 | non riletto nella fonte | Hogan Lovells | n.v. |
| 52 | MATCH Act: allineamento degli alleati «entro 150 giorni» | 150 giorni | la fonte dice: divieto di tutte le DUV a immersione verso la Cina, più limiti all'assistenza e meccanismi di pressione sugli alleati; nessun termine di 150 giorni | Bits&Chips | corretto |
| 53 | Affiliates Rule sospesa fino al 10/1/2027 (FR Doc. 2026-22793) | 10 gennaio 2027 | regola BIS pubblicata il 9/11 | Tech Times | ok |
| 54 | H200: dazio del 25%, nessuna spedizione a maggio | 25% | TechRepublic: 403 | — | n.v. |
| 55 | Applied Materials: Cina 35% delle vendite | 35% | TipRanks: 403 | — | n.v. |
| 56 | ASML in borsa: 1 mese, da inizio anno, 1 anno | −15% / +42% / +49% (lettura provvisoria) | −15,0 / +41,4 / +48,8 (chiusura del 9/11) | prezzi.json delle 03:40 UTC del 10/11 | corretto (chiusura definitiva) |

### Wafer e fabbricazione

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 57 | Quote di fonderia 2° trimestre 2026: TSMC, Samsung, SMIC | 72,5 / 5,9 / 5,4% | identici | TrendForce 9/9/2026 | ok |
| 58 | SMIC, ricavi sul trimestre | +20% | +20% QoQ | TrendForce | ok |
| 59 | 2 nm in volume a Hsinchu e Kaohsiung dalla fine del 2025 | — | Fab 20 dal 4° trim. 2025, Fab 22 P1 dal 2° sem. 2025 | ai-mondo.json | ok |
| 60 | Piano TSMC in Arizona | 265 miliardi di dollari | 65 + 100 + 100 | investimenti.json (INV-50); BetaNews 403 | ok |
| 61 | Arizona: 3 nm nel 2° semestre 2027 | 2° sem. 2027 | non riletto | BetaNews 403 | n.v. |
| 62 | ESMC: 28–12 nm, macchinari nel 2° semestre 2027 | — | identico | ai-mondo.json (Focus Taiwan) | ok |
| 63 | Nexperia Dongguan: oltre 50 miliardi di pezzi l'anno | 50 mld | fonte di affidabilità bassa, non ricontrollata | Model Diplomat | n.v. |
| 64 | Nexperia: link WTOP del febbraio 2026 | — | il link restituisce 404 | WTOP | n.v. (link da sostituire) |
| 65 | TSMC (ADR) e SOX in borsa | −14% / +29% / +36%; −20% / +42% / +45% | −14,3 / +27,9 / +35,6; −20,2 / +41,7 / +44,4 (chiusura del 9/11) | prezzi.json | corretto (chiusura definitiva) |

### Packaging e memoria

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 66 | Capacità CoWoS di TSMC a fine 2026 | 125.000–130.000 wafer al mese (KGI) | la nota KGI dà solo 170.000 a fine 2027; 120.000–130.000 nel 2026 (da 65.000–75.000) è di Tom's Hardware; ai-mondo.json cita TrendForce 120.000–140.000 | KGI 9/3/2026; Tom's Hardware maggio 2026; ai-mondo.json | corretto (fonte riattribuita) |
| 67 | Nvidia circa il 60% del CoWoS 2026 | 60% | «roughly 60% of CoWoS allocation»; Broadcom 15%, AMD 11% | Tom's Hardware | ok (fonte esplicitata) |
| 68 | Broadcom «oltre 240.000 wafer» CoWoS nel 2026 | 240.000 | circa 150.000 wafer (15%) | Tom's Hardware | corretto |
| 69 | Divario domanda–offerta CoWoS dal 20% al 10% a fine 2026 | 10% | identico | ai-mondo.json (TrendForce) | ok |
| 70 | HBM 2° trim. 2026: SK Hynix, Samsung, Micron (e 1° trim.) | 50 / 33 / 18 (58 / 21 / 21) | identici; pagina Counterpoint 403, cifre lette tramite SamMobile | Counterpoint via SamMobile 3/9/2026 | ok |
| 71 | Samsung recupera dodici punti | 12 | da 21 a 33 | calcolo | ok |
| 72 | DRAM, prezzi contrattuali 4° trim. 2026 | +20% sul trimestre | «about 20% quarter-on-quarter» | TrendForce 20/10/2026 | ok |
| 73 | Huawei sotto il 4% del calcolo di Nvidia nel 2026 | <4% | «less than 4%»; l'HBM è il vincolo | Epoch AI | ok |
| 74 | CXMT 10% del mercato DRAM+HBM | 10% | HuaweiCentral: 403 | — | n.v. |
| 75 | SK Hynix in Indiana dal 2029, carenza fino al 2030 | 2029; 2030 | HBM4E dal 3° trim. 2029; carenza fino a fine 2030 | Korea Times 28/8/2026 | ok |
| 76 | SK Hynix in borsa | 1.132.000 KRW; −34% / +74% / +91% (seduta del 6/11) | 1.215.000; −27,7 / +86,6 / +100,5 (seduta del 10/11, provvisoria); la tabella diceva «chiusure al 9 novembre» | prezzi.json | corretto (data della seduta indicata) |
| 77 | Western Digital in borsa | −27% / +68% / +78% | −27,1 / +68,2 / +77,8 | prezzi.json | ok |

### Progetto dei chip

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 78 | Quota di Nvidia 2026 | 75–86%, IDC 81% | forchetta 70–86%; IDC 81%, Silicon Analysts 75%; Tom's Hardware circa 70% | commandlinux; Tom's Hardware | corretto |
| 79 | Quota di AMD | circa 10% | 5–7% | commandlinux (Silicon Analysts, IDC) | corretto |
| 80 | Broadcom «60–80% degli ASIC su misura» | 60–80% | Broadcom e Marvell insieme circa il 95% della co-progettazione | Tom's Hardware | corretto |
| 81 | Huawei: circa 12 miliardi di ricavi da chip AI nel 2026 | 12 mld | non presente nella fonte citata (Epoch AI) | Epoch AI | corretto (tolto) |
| 82 | Nvidia, AMD, Broadcom, Alphabet in borsa | −23% / −4,9%; +138%; −7,3%; −7,3% | −22,1 / −4,2 / −5,0; +137,5; −7,7; chiusure del 9/11 | prezzi.json | corretto (chiusura definitiva) |
| 83 | Valutazione «in borsa vincono i colli fisici» | Nvidia e Broadcom in calo, memoria e macchine in salita | vero, ma AMD è a +137% da inizio anno | prezzi.json | corretto (aggiunta l'eccezione) |

### Server, rete, energia

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 84 | Foxconn «circa 40% dei server AI» | 40% | «oltre il 44%» dei rack (circa 3.700; Quanta 2.100, Wistron 1.300–1.400); il 40% non è nella fonte | TechNews 12/5/2026 | corretto |
| 85 | Export di Taiwan: macchine per elaborazione dati gennaio–agosto 2026 | 192,6 mld, +87,5% | identici; 62,8% verso gli USA; 33,5% dell'export totale | STAT Times (Ministero delle Finanze) | ok |
| 86 | InnoLight 27%, Coherent 17% dei transceiver | 27% / 17% | Counterpoint: 403 | — | n.v. |
| 87 | InnoLight 50–60% dell'1,6T; EML vincolo dell'1,6T (Yole) | 50–60% | Yole: pagina non restituita (202) | — | n.v. |
| 88 | Carenza di chip EML da 200G | oltre il 60% | «缺口超過 60%»; blog del 12/10/2026 | cnyes | ok (data precisata, affidabilità bassa) |
| 89 | Trasformatori elevatori oltre 160 settimane nel 1° trim. 2026 | 160 | «surpassed 160 weeks… compared with 143 weeks in 2024» (Wood Mackenzie) | Reuters via Kitco 9/7/2026 | ok |
| 90 | Foxconn a Houston, Wistron a Dallas | — | confermato | blog Nvidia 14/4/2025 | ok |
| 91 | Foxconn Guadalajara per Stargate | — | server per Stargate, impianto completo nel 2026 | Expansión 7/4/2025 | ok |
| 92 | IEA: 485 TWh nel 2025, 950 nel 2030, circa 3% | 485 / 950 / 3% | identici; +17% nel 2025, siti AI +50%; pagina IEA 403, letta tramite il sommario citato dalla stampa | IEA, Key questions on energy and AI | ok (aggiunte le crescite) |
| 93 | Taiwan: GNL per 12–14 giorni, minimo legale 11; gas al 50,5% a luglio | 12–14; 50,5% | Focus Taiwan non raggiungibile da qui | — | n.v. |
| 94 | Fouju 1,4 GW «vicino al nucleare di Nogent» | vicino | sottostazione da 1,4 GW; Nogent-sur-Seine a circa 55 km in linea d'aria (calcolo) | Eiffage 2/6/2026 | corretto (distanza esplicitata) |
| 95 | Colossus 2 «il più grande campus AI operativo (Epoch)» | il più grande | per potenza: New Carlisle 1.037 MW, Colossus 2 946 MW, Abilene 824, Fairwater Atlanta 636, Nusajaya 473 | Epoch AI, AI data centers | corretto |
| 96 | DayOne Nusajaya primo polo fuori dagli USA nei dati Epoch | — | primo sito non USA dell'elenco (473 MW) | Epoch AI | ok |
| 97 | Stargate UAE 5 GW, 1.000 MW IT nel 2028 | 5 GW | non ricontrollato | Epoch AI | n.v. |
| 98 | Ferrera Erbognone, 500 MW a gas con cattura della CO2 | — | 500 MW prima fase | ai-mondo.json; investimenti.json | ok |
| 99 | Spese in conto capitale 2026 dei grandi cloud | assente | Amazon 220; Alphabet 195–205; Microsoft 170–190; Meta 135–145 mld USD | investimenti.json (capex_2026) | ok (aggiunto) |
| 100 | TTF e Henry Hub | 82,3 €/MWh; 3,2 $/MMBtu | 82,33 (provvisorio); 3,20 | prezzi.json | ok |
| 101 | Microsoft, Amazon, Meta, Oracle in borsa | chiusure del 9/11 | valori ripresi da prezzi.json alla rigenerazione | prezzi.json | ok |

### Europa e Italia

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 102 | UE: magneti NdFeB dalla Cina | assente | 88,3% dell'import extra-UE 2025 (1.061 su 1.201 milioni di USD) | commercio.json (UN Comtrade) | ok (aggiunto) |
| 103 | Italia: magneti NdFeB dalla Cina | assente | 80,1% (91,9 milioni di USD) | commercio.json | ok (aggiunto) |
| 104 | UE: metalli e composti delle terre rare dalla Cina | assente | 78,4% e 39,2% | commercio.json | ok (aggiunto) |
| 105 | Silicio oltre il 99,99%: UE dagli USA, Italia dalla Danimarca | assente | 73,3% e 58,3% (paese di spedizione) | commercio.json | ok (aggiunto) |
| 106 | Veldhoven a 10,8 km da una linea da 380 kV | 10,8 | calcolato dallo script su rete-elettrica.json | rete-elettrica.json | ok |
| 107 | Sillamäe 37,6 km e Narva 63,7 km da Estlink 2 | 37,6 / 63,7 | calcolati dallo script | rete-elettrica.json | ok |

### Struttura e conteggi

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 108 | Nodi, collegamenti, colli di bottiglia | 70 / 34 / 13 | 70 / 34 / 13 | supply-chain-ai.json | ok |
| 109 | Riepilogo degli indicatori congiunturali | 5 critici, 5 attenzione, 3 normali (9/11) | 4 critici, 6 attenzione, 3 non misurati o normali con i dati del 10/11 (prezzi definitivi, scadenza cinese spostata) | supply-chain-ai.json | corretto (rigenerato) |
| 110 | Stati degli indicatori nel Markdown | «{stato:critico}» | il segnaposto non veniva tradotto | costruisci_supply_chain_ai.py | corretto (nello script) |

## 2. Coerenza con gli altri file

- **`minerali.json`.** Le quote del primo produttore coincidono per gallio (99,0), silicio (87,0), terre rare (69,2) e rame (23,0): `raccogli.py` ora lo controlla e segnala ogni differenza in `avvisi`. Da `minerali.json` il report prende anche le quote cinesi di magnesio, tungsteno, grafite e antimonio, materie sotto licenza cinese che prima mancavano.
- **`commercio.json`.** Nuovo legame (`confronti.dipendenze_ue_italia` nel file di dati) per sette voci doganali della catena. Entrano nella nuova sezione «Europa e Italia»: magneti NdFeB (UE 88,3% dalla Cina, Italia 80,1%), metalli e composti delle terre rare, silicio ad altissima purezza (UE 73,3% dagli USA), rame raffinato, grafite artificiale, gallio e germanio (voce mista: per l'UE prima il Brasile, Cina 28,5%). Per l'Italia il dato doganale indica il paese di spedizione, non di origine: lo si dice nel testo.
- **`ai-mondo.json`.** Coerente su CoWoS (divario dal 20 al 10%), quota HBM di SK Hynix nel 1° trimestre (58%), ESMC, Fab 20 e 22, ASML (Cina circa 20%). Una sola differenza di fonte: per la capacità CoWoS 2026 `ai-mondo.json` cita TrendForce (120.000–140.000), il report Tom's Hardware (120.000–130.000); entrambe sono stime e la forchetta del report sta dentro quella di TrendForce.
- **`investimenti.json`.** Coerente sul piano TSMC in Arizona (265 miliardi) e su Ferrera Erbognone; il report ora riprende le spese in conto capitale 2026 dei grandi cloud.
- **`stretti-dettaglio.json`.** La frase «metà delle portacontainer» è il 48% del 2022 citato lì con la fonte Bloomberg/SupplyChainBrain; il nodo del report citava invece CSIS, che non lo dice.

## 3. Correzioni nello script e nei dati

1. `costruisci_supply_chain_ai.py`: nel Markdown gli stati degli indicatori uscivano come segnaposto («{stato:critico}»): ora sono tradotti (■ critico, ▲ attenzione, ● normale).
2. Nuovi blocchi comprimibili (`<details>`), riquadro delle scadenze e riquadro «Revisione»; indice con titoli brevi; appendice in fondo; campo `visibili` in `anelli.json` per scegliere i paragrafi sempre in vista.
3. Tabelle dei titoli: data della seduta quando diversa dalle chiusure USA (SK Hynix), titoli senza prezzo in una riga di testo invece che in righe vuote; nota sulle variazioni (un mese, 31 dicembre, un anno).
4. Neon: USGS pubblica solo gli USA; la tabella non lo presenta più come «primo produttore».
5. `raccogli.py`: la data delle scadenze è quella della fonte, non del calcolo; campo `verifica` propagato agli indicatori; confronto automatico con `minerali.json`; legami con `commercio.json` e `investimenti.json` nel nuovo blocco `confronti`.
6. Voci curate: `controlli.json` (stato e fonti della proroga cinese con `fonti_discordanti`; nuovo divieto cinese di export di elio; Giappone e MATCH Act riformulati); `nodi.json` (CoWoS, Nvidia, AMD, Broadcom, Foxconn, Stretto di Taiwan, Colossus 2, New Carlisle, Fouju, Rubaya, Huawei; affidabilità bassa per The Value Edge); `colli.json` (forchetta Nvidia, data del blog cnyes); `anelli.json` (testi corretti come nella tabella).

## 4. Che cosa resta da fare

- **Ricontrollare il sito del MOFCOM** per il testo della proroga (annuncio n. 58 del 2026 secondo SMM) e il 27 novembre per il divieto verso gli USA; poi rilanciare `raccogli.py` e lo script del report.
- Sostituire il link WTOP su Nexperia (404).
- Fonti non raggiungibili da qui da rileggere a mano: Counterpoint (transceiver, CXMT), TechRepublic (H200), TipRanks, DIGITIMES (EVA Air), USITC (neon), Focus Taiwan (scorte di GNL), BNN Bloomberg (quarzo), Yole, Asia Times e DHL (trasporto delle EUV).
- I grafici SVG sono rigenerati dai dati del 10 novembre (diagramma e concentrazioni); il diagramma dipende dagli stati degli indicatori e cambia con i prezzi.
- Le voci congiunturali manuali più vecchie di 120 giorni (divario CoWoS del 15 giugno, scorte di GNL di Taiwan del 21 marzo) sono segnalate da `raccogli.py` e vanno aggiornate.

## 5. Piccole correzioni segnalate da un altro revisore (10 novembre)

- **Baltic Dry nel report Hormuz.** «2.854 punti il 9 novembre, +37% su un anno» veniva da Trading Economics, che ricava il valore da un contratto derivato (CFD) che replica l'indice, non dall'indice del Baltic Exchange; il dato è stato tolto dalla raccolta automatica. Sostituito in `report/hormuz-mar-rosso-2026-11.md` e `docs/report/hormuz-mar-rosso-2026-11.html` con «2.805 punti il 6 novembre (Baltic Exchange, ripreso da Trading Economics; variazione annua non verificata)»: 2.854 / 1,0175 = 2.805, coerente con il +1,75% giornaliero indicato da Trading Economics. Aggiornati il riquadro «Revisione», la riga delle fonti e la riga 134 della [revisione del report Hormuz](hormuz-mar-rosso-2026-11.md).
- **Cavo lituano datato gennaio 2026.** In `raccolta/nord/esposizione.json` e `docs/data/esposizione-nord.json` la Lituania citava «cavi verso Gotland e Lettonia danneggiati (novembre 2024, gennaio 2026)» e la Lettonia «2025-2026». In `cavi-incidenti.json` gli incidenti sono il BCS East-West Interlink Lituania–Gotland (17 novembre 2024) e il cavo lettone Ventspils–Gotland (26 gennaio 2025): nessun cavo lituano a gennaio 2026. Corretto in entrambi i file, con i nomi dei cavi.
- **Trading Economics in `noli.json`.** Era ancora tra le `fonti`, con data 9 novembre, benché nessun elemento la usi (WCI, FBX, SCFI, CCFI). Marcata `"attiva": false` con una nota: non è più usata in automatico; il Baltic Dry va citato a mano. La funzione `noli_bdi()` in `raccolta/flussi/raccogli.py` non è più chiamata: alla prossima esecuzione la voce sparirà dalle fonti.

## 6. Trasparenza

Revisione svolta con un assistente AI (Claude, di Anthropic), che ha letto i file, scaricato le fonti, corretto voci e script e rigenerato i file. Anthropic compare nel report come cliente della catena (campus di New Carlisle): nessuna voce che la riguarda è stata modificata in questa revisione, salvo la riga di New Carlisle, per la potenza nei dati Epoch. Restano responsabilità dell'autore le scelte, le valutazioni e la pubblicazione.
