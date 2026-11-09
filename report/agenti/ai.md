# Agente INFRASTRUTTURE AI E DIREZIONE DEGLI INVESTIMENTI: rapporto

Data: 2026-11-09. Script: `raccolta/ai/raccogli.py` (solo libreria standard, eseguito davvero il 2026-11-09, circa 20 secondi, 0 problemi di validazione). Voci curate a mano in `raccolta/ai/`: `punti_curati.json`, `flussi.json`, `epoch_coordinate.json`, `top500_siti.json`.

> **Nota di trasparenza.** Chi scrive è Claude, un modello di Anthropic. Anthropic è tra le società citate in questo livello (per esempio come cliente del campus Amazon di New Carlisle e di Colossus 2 nei dati di Epoch, e come concorrente di OpenAI, xAI, Mistral). I dati che la riguardano vengono solo da fonti pubbliche e sono trattati come quelli degli altri. Nel campione dei flussi non ho inserito investimenti in Anthropic o in altri laboratori di modelli, salvo la quota SoftBank in OpenAI, perché non sono infrastruttura geografica.

## 1. Fonti provate

| Fonte | Esito | Licenza |
|---|---|---|
| Epoch AI, *AI data centers*, `data_centers.zip` (96 siti, cronologie, chiller, torri di raffreddamento) | **funziona**, nessuna chiave, scaricato in automatico | CC BY 4.0 |
| Epoch AI, *AI chip imports*, `ai_chip_trade.zip` (`by_country.csv`, trimestri 2022 T1 - 2026 T2) | **funziona**, in automatico | CC BY 4.0 |
| Epoch AI, `gpu_clusters.csv` | funziona, ma è un archivio fermo al 2025 (482 cluster, tutti "esistenti"): usato solo per alcune coordinate | CC BY 4.0 |
| TOP500, pagina della lista (`/lists/top500/list/2026/06/`) | **funziona**, letta con espressioni regolari; la lista di novembre 2026 non è ancora uscita (404): lo script la prenderà da solo quando sarà pubblicata | nessuna licenza aperta dichiarata: uso con citazione |
| OpenStreetMap Nominatim (geocodifica una tantum di comuni e indirizzi) | funziona; usato a mano, non dallo script | ODbL 1.0 |
| Comunicati e stampa (Eni, Microsoft, Google, Amazon, TSMC via TrendForce, DCD, Reuters/AFP, Bloomberg, The Register, Tom's Hardware, Focus Taiwan e altri) | ricerche web: funzionano. Fonte, link e data per ogni riga | fatti citati con la fonte |
| IEA, *Energy and AI* | usata solo tramite sintesi di terzi: la pagina primaria non è uscita nelle ricerche | — |
| The Information | non consultata (a pagamento) | — |

Nessuna fonte richiede chiavi. Epoch e TOP500 sono pagine pubbliche: se cambiano formato, lo script riusa i dati precedenti e lo scrive in `errori`.

## 2. Cosa contengono i file

**`docs/data/ai-mondo.json`** (106 kB), 82 punti fuori dagli USA (gli USA restano in `ai.json`, che non ho toccato):
- `data-center-ai` (42): 19 siti dal tracker Epoch (automatici: MW IT attuali e previsti, equivalenti H100, proprietario, utilizzatori, costo di capitale stimato da Epoch, ultima osservazione satellitare) e 23 curati a mano (Italia, Francia, Germania, Regno Unito, Spagna, Svezia, Kenya, Arabia Saudita, India, Giappone, Corea, Brasile, Messico, Cile).
- `fab-chip` (20, curati): TSMC (Hsinchu, Kaohsiung, Taichung, Chiayi, Kumamoto, Dresda), Samsung Pyeongtaek, SK Hynix (Cheongju, Yongin, Indiana), Micron (Hiroshima, Singapore, Sanand), Intel (Leixlip, Magdeburgo cancellata, Kiryat Gat ferma), SMIC, Rapidus, Tata-PSMC, ASML. Con `nodo` e `stato`.
- `supercalcolo` (20, automatici): i primi 20 della TOP500 di giugno 2026, con Rmax, Rpeak, potenza. I tre già in `ai.json` (El Capitan, Frontier, Aurora) hanno `duplicato_ai_json: true`.
- `quote_paesi`: quote del calcolo AI per paese secondo Epoch (trimestre 2026 T2), con la serie degli ultimi 12 trimestri.
- Campi dei punti: quelli comuni (`lat`, `lon`, `nome`, `paese`, `categoria`, `stato`, `fonte`, `link`, `data_fonte`, `affidabilita`, `note`) più `mw`, `mw_tipo`, `proprietario`, `anno`, `importo` (miliardi nella valuta della fonte), `valuta`, `importo_usd_mld`, `origine_coord`, `precisione_km`, `origine_dato` (epoch / top500 / curato).
- `stato`: operativo, operativo-parziale, in-costruzione, annunciato, sospeso, cancellato.

**`docs/data/investimenti.json`** (69 kB), 64 flussi "da → a":
- Ogni flusso: `attore`, `da_paese`/`a_paese` (ISO; "US+AE" quando un consorzio misto non dichiara le quote), `da_lat/lon` (sede della società o capitale), `a_lat/lon` (il sito, preso dal punto della mappa con `a_rif`, oppure la capitale), `importo` e `valuta` originali, `importo_usd_mld`, `metodo_usd`, `anno`, `periodo`, `settore` (data center, chip, energia per AI, fondo), `stato` (annunciato, in corso, completato, sospeso, cancellato), `quadro`, fonte, link, data, affidabilità, note.
- `riepilogo`: totali per paese di origine e di destinazione, per settore e per stato, con l'avvertenza che annunci e spese non coincidono. Gli impegni-quadro dei governi sono sommati a parte. I cambi sono fissi e indicativi (EUR 1,10; GBP 1,30; JPY 1/150; KRW 1/1400; INR 1/88; BRL 0,18; SEK 0,10; CNY 0,14), usati solo quando la fonte non dà l'equivalente in dollari.
- `capex_2026`: guida di spesa 2026 di Amazon, Alphabet, Microsoft, Meta.

## 3. Mappa mondiale del calcolo AI per paese (Epoch)

Quota del calcolo AI arrivato dal 2022 (equivalenti H100), Epoch AI, trimestre 2026 T2:

| Paese | Quota cumulata | Quota del solo T2 2026 |
|---|---|---|
| Stati Uniti | 72,2% | 77,5% |
| Cina | 9,6% | 5,1% |
| Unione europea (aggregato) | 5,1% | 3,9% |
| Malesia | 2,4% | 2,3% |
| India | 1,6% | 3,3% |
| Giappone | 1,6% | 1,1% |
| Australia | 1,4% | 1,3% |
| Regno Unito | 1,2% | 1,0% |

- La quota americana sale da 57,5% (2023 T3) a 72,2%; la cinese scende dal 16,1% al 9,6% (controlli sull'export). L'UE resta tra il 5 e l'8%.
- L'India è il paese che cresce di più nell'ultimo trimestre (3,3% del nuovo calcolo, più della UE).
- **Johor (Malesia) è il polo extra-USA più grande nei dati di Epoch**: DayOne Nusajaya 473 MW IT, DayOne Kempas 422 MW, Bridge MY06 243 MW (utilizzatore probabile ByteDance), YTL 113 MW che salgono a 284. È il "cortile" di calcolo di Singapore e, in parte, di aziende cinesi.
- In Cina Epoch vede campus da 170-220 MW oggi (Huawei a Horinger e Wuhu, VNET e Envision a Ulanqab, Alibaba a Zhangbei), con piani fino a 450-700 MW nel 2027-2028.
- Il maggiore progetto fuori dagli USA per potenza prevista è **Stargate UAE** (1.000 MW IT nel 2028 secondo Epoch, dentro un campus da 5 GW).
- **Italia**: nessun sito AI di scala GW operativo. In mappa: il progetto Eni-Khazna di Ferrera Erbognone (500 MW, annunciato), Microsoft Italy North (Milano), Data4 Vittuone (100 MW), Aruba Ponte San Pietro, e i supercalcolatori HPC7 (6° al mondo, 571,5 PFlop/s), HPC6 (8°) di Eni e Leonardo (12°) del CINECA. **Stargate Italia non esiste**: nessun annuncio di OpenAI o del governo trovato.

## 4. Dove vanno i soldi e da dove arrivano

**Fatti (dal riepilogo, campione curato di 64 flussi).** I 58 progetti non-quadro e non cancellati sommano circa **1.038 mld USD** (5 senza importo). Gli impegni-quadro dei governi sommano altri **2.810 mld USD**, tenuti a parte.

- **Da dove**: Taiwan 293 mld (quasi tutto TSMC in Arizona, 265 mld), Stati Uniti 270 mld (30 voci: Microsoft, Amazon, Google, Oracle, Blackstone, Micron, Intel), India 110 (Reliance in casa), Cina 100 (Alibaba in casa 53, ByteDance in Brasile 37,7 e in Thailandia 8,8), Corea 55, consorzi USA-Emirati 41, Giappone 38, Emirati 33, Canada 31 (Brookfield in Francia e Svezia).
- **Verso dove**: Stati Uniti 345 mld, India 178, Giappone 60, Francia 54, Cina 53, Corea 51, Regno Unito 50, Brasile 40, Arabia Saudita 20, Qatar 20, Germania 18, Spagna 17, Malesia 17, Emirati 15. **Italia circa 6 mld USD** (Microsoft 4,3 mld EUR, AWS 1,2 mld EUR) più il progetto Eni-MGX-G42 senza cifra e l'impegno-quadro degli Emirati di 40 mld USD senza calendario.
- **Per settore**: data center 617 mld, chip 399 mld.
- **Per stato**: in corso 664 mld, annunciato 323, completato 50 (l'acquisto di Aligned da 40 mld è l'unico grande flusso chiuso del Golfo verso gli USA), sospeso 1 (Kenya). Cancellati ed esclusi: Intel Magdeburgo (30 mld EUR).
- **Impegni-quadro**: Emirati → USA 1.400 mld (10 anni), Saudi → USA 600, Giappone → USA 550 (primo blocco di 36 mld in energia, febbraio 2026), InvestAI UE 200 mld EUR, Emirati → Italia 40.
- **Capex 2026 dei quattro grandi** (guida dopo i conti di fine ottobre 2026): Amazon circa 220 mld, Alphabet 195-205, Microsoft 170-190 (fonti discordi; 25 mld attribuiti al rincaro della memoria), Meta 135-145: **720-760 mld USD**, in gran parte negli USA.

**Valutazione mia.** La direzione è chiara: i capitali del Golfo e dell'Asia (Taiwan, Giappone, Corea) vanno verso gli USA, mentre i gruppi americani portano data center in India, Giappone, Malesia, Europa e Golfo. La Cina investe all'estero soprattutto dove le regole americane non arrivano o arrivano meno (Thailandia, Brasile, Malesia, Golfo). Le cifre più grandi sono impegni politici legati ai negoziati sui dazi, non piani di cantiere.

## 5. Colli di bottiglia

- **Energia.** L'IEA stimava 415 TWh di consumo dei data center nel 2024 (1,5% dell'elettricità mondiale); secondo sintesi del suo aggiornamento 2026 circa 485 TWh nel 2025 (+17%) e 950 TWh al 2030 (dato da verificare sulla pagina IEA). Due progetti in mappa sono fermi per l'energia: **Stargate UK** (sospeso ad aprile 2026 per prezzi dell'energia e regole) e **Microsoft-G42 in Kenya** (rallentato a maggio 2026 per disaccordo sulla domanda elettrica). In Malesia il 78,6% della capacità IT è a Johor (MIDA), che secondo lo Straits Times (dato riportato da una sintesi, non verificato sull'originale) ha respinto quasi il 30% delle domande di nuovi data center.
- **Chip e impacchettamento.** Il 2 nm è in volume solo a Taiwan (Hsinchu e Kaohsiung dal 4° trimestre 2025). La capacità CoWoS di TSMC nel 2026 è stimata a 120.000-140.000 wafer al mese, con un divario tra domanda e offerta che scenderebbe dal 20% al 10% a fine 2026 (TrendForce, 2026-06-15). ASML prevede circa 65 scanner EUV nel 2026: un solo fornitore al mondo. In Europa la produzione avanzata arretra: Magdeburgo cancellata (luglio 2025), ESMC Dresda (28-12 nm, non per GPU) slitta verso il 2028.
- **Memoria HBM.** Prezzi contrattuali della DRAM +90-98% nel 1° trimestre 2026 (analisti); offerta HBM 2026 venduta; SK Hynix (58% del mercato HBM nel 1° trimestre 2026, Counterpoint) vede carenza fino al 2030 e produrrà HBM negli USA solo dal 2029. Microsoft attribuisce 25 mld del suo capex 2026 al rincaro della memoria; Meta ha alzato la forchetta per lo stesso motivo.
- **Acqua.** Epoch misura il consumo d'acqua solo per alcuni siti USA (per esempio circa 21 milioni di galloni al giorno a New Carlisle, campus Amazon usato da Anthropic, ottobre 2026); per i siti esteri il dato manca. Johor e il Golfo sono le aree da seguire (raffreddamento in clima caldo, desalinizzazione): **dato mancante**, non stimato.

## 6. Legami con gli altri livelli della mappa

Calcolato dallo script di prova sui file `rete-elettrica.json` (linee ≥380 kV, riquadro Europa-Medio Oriente) e `nucleare.json` (GEM):
- Quasi tutti i siti europei e del Golfo sono entro 0-15 km da una linea a 380-525 kV: la rete di trasmissione c'è, il vincolo è la capacità disponibile e i tempi di allaccio.
- **Italia senza nucleare vicino**: Ferrera Erbognone, Milano, Vittuone e Ponte San Pietro sono a 220-260 km dalla centrale svizzera di Gösgen (1.060 MW). Il progetto Eni punta sul gas con cattura della CO2: lega l'AI italiana al prezzo del gas (TTF a 82 EUR/MWh il 2026-11-09, +192% da inizio anno in `prezzi.json`) e quindi a Hormuz e ai terminali GNL.
- **Francia**: il campus di Fouju è a 55 km da Nogent (2.726 MW), quello di Cambrai a 111 km da Chooz (3.120 MW). È il vantaggio francese.
- **Emirati**: Stargate UAE è a 230 km da Barakah (5.668 MW, 4 reattori).
- **Finlandia**: Nebius a Mäntsälä è a 64 km da Loviisa.
- **Cavi**: Visakhapatnam (Google) e Sines (Microsoft, Start Campus) sono anche approdi di cavi sottomarini; Johor guarda lo Stretto di Malacca.
- **Stretti**: Taiwan (2 nm, CoWoS) e lo Stretto di Taiwan restano il punto singolo di fallimento della filiera; Hormuz pesa sui campus del Golfo e sul GNL che alimenta il progetto italiano.

## 7. Legami con i mercati (`prezzi.json`, chiusure al 2026-11-09, SK Hynix al 2026-11-06)

| Titolo | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|
| Nvidia (NVDA) | 176,41 USD | −23,1% | −5,4% | −6,2% |
| Broadcom (AVGO) | 318,82 USD | −11,8% | −7,9% | −8,8% |
| TSMC (TSM) | 390,13 USD | −13,9% | +28,4% | +36,2% |
| ASML | 1.510,10 USD | −15,2% | +41,1% | +48,5% |
| SK Hynix | 1.132.000 KRW | −34,3% | +73,9% | +90,9% |
| Western Digital (WDC) | 292,74 USD | −26,3% | +69,9% | +79,6% |
| Oracle (ORCL) | 118,92 USD | −15,9% | −39,0% | −50,3% |
| AMD | 505,52 USD | −16,9% | +136,1% | +116,5% |
| Indice semiconduttori (SOX) | 9.990,2 | −20,5% | +41,0% | +43,8% |

Lettura (mia): nell'ultimo mese c'è una correzione forte su tutto il comparto; da inizio anno vincono i colli di bottiglia fisici (memoria: SK Hynix, WDC; macchine: ASML; fonderia: TSMC) più dei progettisti di chip (Nvidia, Broadcom negativi). Oracle, molto esposta al debito per Stargate, ha dimezzato il valore in un anno. Alcune serie di `prezzi.json` sono marcate provvisorie.

## 8. Fatti attuali (numero, data, fonte)

1. Gli USA hanno il 72,2% del calcolo AI arrivato dal 2022 e il 77,5% di quello del 2° trimestre 2026; la Cina il 9,6% (Epoch AI, dati scaricati il 2026-11-09).
2. Il consorzio AIP-MGX-GIP ha chiuso il 2026-07-21 l'acquisto di Aligned Data Centers per circa 40 mld USD (WAM, DCD).
3. TSMC ha portato a 265 mld USD il piano in Arizona, con 100 mld in più a luglio 2026 (Città di Phoenix).
4. Il bando UE per fino a 7 gigafabbriche AI è aperto dal 2026-07-30, con fino a 10 mld EUR pubblici; nessun sito scelto (EuroHPC JU).
5. OpenAI ha sospeso Stargate UK ad aprile 2026 (The Register, 2026-04-09); il sito norvegese di Narvik è passato a Microsoft (ITPro, aprile 2026).
6. Google ha avviato il 2026-04-28 il cantiere del suo hub AI da 15 mld USD a Visakhapatnam (Google Cloud).
7. ESMC (TSMC) a Dresda: strutture completate a settembre 2026, macchinari solo nel 2° semestre 2027 (Focus Taiwan, 2026-09-15).
8. SK Hynix ha avviato il 2026-08-27 l'impianto HBM in Indiana, volume dal 3° trimestre 2029 (Korea Times/Reuters).
9. Capex 2026 dei quattro grandi gruppi USA: 720-760 mld USD (guida di fine ottobre 2026, fonti secondarie).
10. Il campus IA di Fouju (1,4 GW, MGX-Bpifrance-Mistral-Nvidia) è entrato in fase realizzativa con il contratto Eiffage per la sottostazione (2026-06-02).

## 9. Proposta per la mappa

- **Punti** (`ai-mondo.json`): cerchio per i data center con raggio proporzionale ai MW (usare `mw_previsto` come anello esterno tratteggiato); quadrato per le fab, triangolo per il supercalcolo. Colore per `stato` (pieno = operativo, vuoto = in costruzione/annunciato, grigio barrato = sospeso/cancellato). Nascondere i punti con `duplicato_ai_json` e attenuare quelli con `origine_coord` "centroide-paese" (posizione non reale).
- **Archi** (`investimenti.json`): linee curve da `da_lat/lon` a `a_lat/lon`, spessore proporzionale a `importo_usd_mld`, colore per settore, tratteggio per "annunciato". Impegni-quadro in un livello separato, spento di default. I flussi interni (stesso paese) come cerchi sul punto d'arrivo.
- **Pannello**: barre delle quote Epoch per paese con la serie trimestrale; tabella del riepilogo con l'avvertenza in evidenza; riquadro Italia (siti, flussi verso l'Italia, distanza dal nucleare, legame col TTF).

## 10. Limiti

- **Annunci contro realtà**: molti progetti esteri (Humain, Reliance, Scala, Stargate Argentina, ByteDance in Brasile) hanno solo annunci; lo stato è quello dell'ultima fonte trovata, con la data.
- **Coordinate**: tutte stimate; i siti esteri sono spesso a livello di comune (precisione 2-40 km); quattro dei primi 20 sistemi TOP500 (Eagle, ISEG2, Discovery 6, Maximus-02) sono sul centroide del paese perché la posizione non è pubblica.
- **Copertura**: il tracker Epoch copre bene USA, Malesia e Cina ma pochi siti europei; il campione dei flussi è curato a mano (64 voci) e parziale. Mancano, per mancanza di link verificati: impegno coreano di 350 mld USD negli USA, Oracle in Giappone, AWS cloud sovrano in Germania, CHIPS Act europeo, cifra dell'investimento proprio di Samsung a Taylor, Aruba in MW.
- **Somme**: mescolano piani pluriennali, contributi pubblici, acquisizioni e lettere d'intenti, con cambi fissi; non indicano la spesa effettiva.
- **Fonti deboli**: alcune pagine del tipo "tokenring/mammothtimes" e aggregatori sono state lette solo per orientarsi e non usate per i numeri. SMIC (stime SemiAnalysis), Scala AI City, Stargate Argentina e il costo di Kumamoto 2 hanno affidabilità bassa.
- **Licenze**: Epoch CC BY 4.0 (citare "Epoch AI"); TOP500 senza licenza aperta dichiarata (citare); OSM ODbL per le coordinate geocodificate.

## 11. Note per la regia

- `docs/index.html` non è stato toccato: i due file nuovi vanno aggiunti a `manifest.json` dal coordinatore.
- Lo script gira senza chiavi; a metà novembre 2026 (SC26) uscirà la nuova TOP500 e lo script la prenderà da solo. Se Epoch aggiunge siti fuori dagli USA, lo script li segnala in `errori` finché non si aggiunge una riga in `epoch_coordinate.json`.
- `python3 raccolta/ai/raccogli.py --valida` controlla i due file senza rete.
