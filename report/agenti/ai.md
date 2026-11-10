# Agente INFRASTRUTTURE AI E DIREZIONE DEGLI INVESTIMENTI: rapporto

Data: 2026-11-10 (seconda passata, espansione dei livelli). Script: `raccolta/ai/raccogli.py` (solo libreria standard, eseguito davvero il 2026-11-10, pochi secondi, `--valida`: 0 problemi). File curati in `raccolta/ai/`: `punti_curati.json` (147 voci), `epoch_coordinate.json` (96 siti), `top500_siti.json` (43 siti), `ai_selezione.json` (66 voci di `ai.json`), `flussi.json` (invariato).

> **Nota di trasparenza.** Chi scrive è Claude, un modello di Anthropic. Anthropic compare nei dati di Epoch come utilizzatrice di alcuni campus (New Carlisle, Lake Mariner, Barber Lake). Questi siti sono trattati come gli altri e la cosa è scritta nelle loro note.

## 1. Cosa è cambiato rispetto al 2026-11-09

- **`ai-mondo.json` passa da 82 a 301 punti e ora copre tutto il mondo, USA compresi** (prima gli USA erano esclusi). Testi dei punti in inglese.
- **`ai.json` è generato dallo script** come selezione curata di **66 siti** (era 25, solo USA) nello schema dei punti fissi (`classe: fisso`, categorie `data-center` / `fab-chip` / `supercomputer` lette da `AI_CAT` della mappa). Gli id `AI-20261109-01…25` sono conservati (li usano `investimenti.json` e il dossier USA); i nuovi sono `AI-20261110-01…41`. Ogni voce ha `rif_ai_mondo` = id del punto da cui è copiata; il punto corrispondente in `ai-mondo.json` ha `duplicato_ai_json: true`.
- **Nuove categorie in `ai-mondo.json`** (da stilizzare): `packaging` (impacchettamento avanzato e assemblaggio memoria, 13), `attrezzature` (macchine e materiali senza alternative, 5), `hub-data-center` (poli metropolitani, non siti singoli; `mw` = capacità del mercato, 10). Restano `data-center-ai`, `fab-chip`, `supercalcolo`.
- **Nuovi campi**: `tipo` (es. "memory", "logic foundry", "GPU cluster (Epoch archive, 2025)", "EuroHPC AI Factory"), `energia` (fornitori di energia secondo Epoch), `nome_en` (nome inglese per le 10 voci il cui `nome` resta in italiano perché `raccolta/supply-chain-ai/nodi.json` le cita per nome), `senza_posizione` (lista dei sistemi TOP500 con sito non pubblico, **non disegnati**), `conteggi` per categoria/paese/origine/stato.
- **Regola sulle coordinate più severa**: niente più punti sul centroide del paese. Ogni punto ha `origine_coord` (indirizzo o comune geocodificato con OSM Nominatim, o coordinate Epoch) e `precisione_km` (1 km per un edificio, 2 per una via, 5-8 per un comune, 12-15 per una città, 20-40 per province e mercati metropolitani).
- `investimenti.json`: logica invariata; 64 flussi, 1.038,3 mld USD di progetti e 2.810 mld di impegni-quadro (come prima). I due flussi che puntano a `AI-20261109-17` (TSMC Arizona) e `-20` (Samsung Taylor) si risolvono ancora.

## 2. Fonti provate

| Fonte | Esito | Licenza |
|---|---|---|
| Epoch AI, *AI data centers* (`data_centers.zip`): **tutti i 96 siti** (77 USA, 5 Cina, 4 Malesia, 2 Norvegia, 1 ciascuno Regno Unito, Indonesia, Finlandia, Australia, Portogallo, Islanda, Svezia, Emirati), con MW IT attuali e previsti, H100e, proprietario, utilizzatori, costo stimato | **funziona**, automatico | CC BY 4.0 |
| Epoch AI, *GPU clusters* (`gpu_clusters.csv`, 482 cluster, archivio fermo al 2025, con latitudine/longitudine) | **funziona**, ora automatico. Usati 25 cluster: scartati 270 sul centroide del paese (tutti i 188 cinesi), 34 senza coordinate, 30 superati o dismessi, 87 sotto 500 H100e, 36 doppioni di siti già in mappa (entro 8 km o stesso nome di un sistema TOP500) | CC BY 4.0 |
| Epoch AI, *AI chip imports* (quote per paese) | funziona, automatico (trimestre 2026 T2) | CC BY 4.0 |
| TOP500, lista di giugno 2026 | funziona; ora i **primi 50**. 33 disegnati, 17 senza sito pubblico (Eagle, ISEG2, Discovery 6, Maximus-02, i tre CHIE di SoftBank, Selene ed Eos di Nvidia, SSC-24 Samsung, Njoerd, i Core42, Kakao, Yotta, FPT) elencati in `senza_posizione`. Corretto il caso dei sistemi senza nome (rango 32). La lista di novembre 2026 non è ancora uscita: lo script la prenderà da sola | uso con citazione |
| OSM Nominatim (geocodifica una tantum di 77 indirizzi Epoch USA, 14 siti TOP500, 104 voci curate) | funziona; usato a mano, non dallo script | ODbL 1.0 |
| Wikipedia, *List of semiconductor fabrication plants* | funziona (pagina HTML); base per 20 fabbriche di lunga data (nodi e wafer/mese **datati**, affidabilità "media") | CC BY-SA 4.0 |
| Stampa e comunicati (Microsoft, Google, SoftBank, KDDI, Meta, EuroHPC, TrendForce, Tom's Hardware, DCD, Focus Taiwan, Asia Economy, JLL, CBRE via W.Media e Real Estate Asia, Cushman & Wakefield via EdgeProp, CSO irlandese, MeitY via TelecomTalk e altri) | ricerche web: funzionano; fonte, link e data per riga | fatti con citazione |
| API di Wikipedia | **non funziona** (limite di richieste sull'IP condiviso): usata la pagina HTML | — |
| Pagine societarie di TSMC, Kioxia, Shin-Etsu, SUMCO, ASE, GlobalFoundries | 403/404 o irraggiungibili dal proxy: non usate. Per questo Shin-Etsu e SUMCO (wafer di silicio) **non sono in mappa**: nessuna fonte raggiungibile indica lo stabilimento | — |

## 3. Cosa contengono i file

**`docs/data/ai-mondo.json`** (370 kB, sotto il limite di 1,5 MB): **301 punti** in 42 paesi.

| Categoria | Punti | Origine |
|---|---|---|
| `data-center-ai` | 187 | 96 Epoch tracker, 25 Epoch GPU clusters, 66 curati |
| `fab-chip` | 53 | curati (logica e memoria) |
| `supercalcolo` | 33 | TOP500 (primi 50 meno 17 senza posizione) |
| `packaging` | 13 | curati (CoWoS TSMC AP3/AP5/AP6/AP7/AP8, ASE, SPIL, Amkor Peoria, HBM SK Hynix Cheongju e Indiana, Samsung Onyang, Micron Singapore e Sanand) |
| `hub-data-center` | 10 | curati (Frankfurt, Amsterdam, Londra/Slough, Parigi, Dublino, Northern Virginia, Singapore, Johor, Greater Tokyo/Inzai, Mumbai) |
| `attrezzature` | 5 | curati (ASML Veldhoven, Zeiss Oberkochen, TRUMPF Ditzingen, Tokyo Electron Nirasaki, Ajinomoto ABF Kawasaki) |

Per paese (primi): USA 115, Taiwan 21, Cina 18, Giappone 17, Corea 13, Germania 9, India 8, Italia 7, Francia 7, Svezia 7, Finlandia 7, Regno Unito 6, Singapore 6, Danimarca 6, Malesia 6, Paesi Bassi 5, Spagna 4, Arabia Saudita 4, Brasile 4, Norvegia 3; poi Irlanda, Israele, Estonia, Lituania, Islanda, Canada (2 ciascuno) e altri 12 paesi con 1.
Per stato: operativo 165, operativo-parziale 50, in-costruzione 67, annunciato 15, sospeso 3, cancellato 1.

**Nordici, Paesi Bassi, Danimarca, Baltici** (richiesta del titolare): Meta Odense; Microsoft Denmark East (Høje-Taastrup, Køge, Roskilde); Google Fredericia; Google Hamina più i nuovi Kajaani, Vaala, Muhos (13 mld EUR, 2027-2028); Nebius Mäntsälä e Lappeenranta (310 MW); Microsoft Gävle, Sandviken, Staffanstorp; EcoDataCenter Borlänge (Mistral); Brookfield Strängnäs; Narvik (ex Stargate Norway, ora Nscale per Microsoft); CoreWeave e Hyperstack in Norvegia; Google Eemshaven e Winschoten; Microsoft Middenmeer; hub di Amsterdam; Estonia (Sunly Risti 180 MW, Greenergy/Nebius vicino a Tallinn), Lettonia (Delska Riga 10 MW), Lituania (Delska Vilnius, LitAI Factory); Verne/Nebius e Nscale in Islanda; supercalcolatori LUMI, Arrhenius, Gefion.

**Fabbriche e memoria**: TSMC Fab 12, 14, 15, 18, 20, 22, 25, Arizona, Kumamoto (JASM), Dresda (ESMC); Samsung Pyeongtaek, Hwaseong, Giheung, Austin, Taylor, Xi'an; SK Hynix Icheon, Cheongju, Yongin, Wuxi, Dalian (ex Intel), Indiana; Micron Taichung, Taoyuan, Tongluo, Tainan, Hiroshima, Boise, Clay, Manassas, Singapore; Intel Ocotillo, Hillsboro, Ohio, Leixlip, Kiryat Gat (Fab 28 e Fab 38 ferma), Magdeburgo (cancellata); GlobalFoundries Dresda, Malta, Essex Junction, Singapore; SMIC Shanghai, Lingang, Pechino, Shenzhen, Tianjin; CXMT Hefei e Shanghai; YMTC Wuhan; Kioxia Yokkaichi e Kitakami; Rapidus Chitose; Tata Dholera.

**`docs/data/ai.json`** (93 kB): 66 siti = 40 data center/hub, 20 fab/packaging/attrezzature, 6 supercalcolatori; teatri NATO 41, ALTRO 20, MO 3, IT 2. Contiene i 25 siti del dossier USA (stessi id, coordinate ora dall'indirizzo Epoch) e 41 siti mondiali (Golfo, Nordici, Paesi Bassi, poli europei, Asia, catena dei chip). I nomi legati a `supply-chain-ai` e ai flussi sono conservati.

**Proposta: tenere due livelli, non fonderli.** `ai.json` è il livello "di sintesi" con le targhette dei punti fissi e il legame col dossier USA; `ai-mondo.json` è l'inventario completo. Per non disegnare due volte lo stesso sito quando sono accesi entrambi, basta saltare in `xai` i punti con `duplicato_ai_json: true` (66 punti).

## 4. Quote di calcolo AI per paese (Epoch, trimestre 2026 T2)

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

Nel tracker Epoch dei data center gli USA pesano l'83,6% della potenza IT attuale (12.640 di 15.122 MW) e l'86,3% degli H100 equivalenti (13,6 di 15,8 milioni). I progetti con più MW previsti sono tutti americani: Microsoft Fairwater Wisconsin (2.263 MW entro maggio 2028), Amazon-Anthropic New Carlisle (1.925 MW, marzo 2028), Stargate New Mexico (1.750 MW, fine 2028), Meta Hyperion (1.632 MW, 2028), xAI Colossus 2 (1.531 MW, febbraio 2027).

## 5. Dove vanno i soldi e da dove arrivano

**Fatti (dal riepilogo, campione curato di 64 flussi).** I 58 progetti non-quadro e non cancellati sommano circa **1.038 mld USD** (5 senza importo). Gli impegni-quadro dei governi sommano altri **2.810 mld USD**, tenuti a parte.

- **Da dove**: Taiwan 293 mld (quasi tutto TSMC in Arizona, 265 mld), Stati Uniti 270 mld (30 voci: Microsoft, Amazon, Google, Oracle, Blackstone, Micron, Intel), India 110 (Reliance in casa), Cina 100 (Alibaba in casa 53, ByteDance in Brasile 37,7 e in Thailandia 8,8), Corea 55, consorzi USA-Emirati 41, Giappone 38, Emirati 33, Canada 31 (Brookfield in Francia e Svezia).
- **Verso dove**: Stati Uniti 345 mld, India 178, Giappone 60, Francia 54, Cina 53, Corea 51, Regno Unito 50, Brasile 40, Arabia Saudita 20, Qatar 20, Germania 18, Spagna 17, Malesia 17, Emirati 15. **Italia circa 6 mld USD** (Microsoft 4,3 mld EUR, AWS 1,2 mld EUR) più il progetto Eni-MGX-G42 senza cifra e l'impegno-quadro degli Emirati di 40 mld USD senza calendario.
- **Per settore**: data center 617 mld, chip 399 mld.
- **Per stato**: in corso 664 mld, annunciato 323, completato 50 (l'acquisto di Aligned da 40 mld è l'unico grande flusso chiuso del Golfo verso gli USA), sospeso 1 (Kenya). Cancellati ed esclusi: Intel Magdeburgo (30 mld EUR).
- **Impegni-quadro**: Emirati → USA 1.400 mld (10 anni), Saudi → USA 600, Giappone → USA 550 (primo blocco di 36 mld in energia, febbraio 2026), InvestAI UE 200 mld EUR, Emirati → Italia 40.
- **Capex 2026 dei quattro grandi** (guida dopo i conti di fine ottobre 2026): Amazon circa 220 mld, Alphabet 195-205, Microsoft 170-190 (fonti discordi; 25 mld attribuiti al rincaro della memoria), Meta 135-145: **720-760 mld USD**, in gran parte negli USA.

**Valutazione mia.** La direzione è chiara: i capitali del Golfo e dell'Asia (Taiwan, Giappone, Corea) vanno verso gli USA, mentre i gruppi americani portano data center in India, Giappone, Malesia, Europa e Golfo. La Cina investe all'estero soprattutto dove le regole americane non arrivano o arrivano meno (Thailandia, Brasile, Malesia, Golfo). Le cifre più grandi sono impegni politici legati ai negoziati sui dazi, non piani di cantiere.

## 6. Colli di bottiglia

- **Energia.** L'IEA stimava 415 TWh di consumo dei data center nel 2024 (1,5% dell'elettricità mondiale); secondo sintesi del suo aggiornamento 2026 circa 485 TWh nel 2025 (+17%) e 950 TWh al 2030 (dato da verificare sulla pagina IEA). Due progetti in mappa sono fermi per l'energia: **Stargate UK** (sospeso ad aprile 2026 per prezzi dell'energia e regole) e **Microsoft-G42 in Kenya** (rallentato a maggio 2026 per disaccordo sulla domanda elettrica). In Malesia il 78,6% della capacità IT è a Johor (MIDA), che secondo lo Straits Times (dato riportato da una sintesi, non verificato sull'originale) ha respinto quasi il 30% delle domande di nuovi data center.
- **Chip e impacchettamento.** Il 2 nm è in volume solo a Taiwan (Hsinchu e Kaohsiung dal 4° trimestre 2025). La capacità CoWoS di TSMC nel 2026 è stimata a 120.000-140.000 wafer al mese, con un divario tra domanda e offerta che scenderebbe dal 20% al 10% a fine 2026 (TrendForce, 2026-06-15). ASML prevede circa 65 scanner EUV nel 2026: un solo fornitore al mondo. In Europa la produzione avanzata arretra: Magdeburgo cancellata (luglio 2025), ESMC Dresda (28-12 nm, non per GPU) slitta verso il 2028.
- **Memoria HBM.** Prezzi contrattuali della DRAM +90-98% nel 1° trimestre 2026 (analisti); offerta HBM 2026 venduta; SK Hynix (58% del mercato HBM nel 1° trimestre 2026, Counterpoint) vede carenza fino al 2030 e produrrà HBM negli USA solo dal 2029. Microsoft attribuisce 25 mld del suo capex 2026 al rincaro della memoria; Meta ha alzato la forchetta per lo stesso motivo.
- **Acqua.** Epoch misura il consumo d'acqua solo per alcuni siti USA (per esempio circa 21 milioni di galloni al giorno a New Carlisle, campus Amazon usato da Anthropic, ottobre 2026); per i siti esteri il dato manca. Johor e il Golfo sono le aree da seguire (raffreddamento in clima caldo, desalinizzazione): **dato mancante**, non stimato.

## 7. Legami con gli altri livelli della mappa

Calcolato dallo script di prova sui file `rete-elettrica.json` (linee ≥380 kV, riquadro Europa-Medio Oriente) e `nucleare.json` (GEM):
- Quasi tutti i siti europei e del Golfo sono entro 0-15 km da una linea a 380-525 kV: la rete di trasmissione c'è, il vincolo è la capacità disponibile e i tempi di allaccio.
- **Italia senza nucleare vicino**: Ferrera Erbognone, Milano, Vittuone e Ponte San Pietro sono a 220-260 km dalla centrale svizzera di Gösgen (1.060 MW). Il progetto Eni punta sul gas con cattura della CO2: lega l'AI italiana al prezzo del gas (TTF a 82 EUR/MWh il 2026-11-09, +192% da inizio anno in `prezzi.json`) e quindi a Hormuz e ai terminali GNL.
- **Francia**: il campus di Fouju è a 55 km da Nogent (2.726 MW), quello di Cambrai a 111 km da Chooz (3.120 MW). È il vantaggio francese.
- **Emirati**: Stargate UAE è a 230 km da Barakah (5.668 MW, 4 reattori).
- **Finlandia**: Nebius a Mäntsälä è a 64 km da Loviisa.
- **Cavi**: Visakhapatnam (Google) e Sines (Microsoft, Start Campus) sono anche approdi di cavi sottomarini; Johor guarda lo Stretto di Malacca.
- **Stretti**: Taiwan (2 nm, CoWoS) e lo Stretto di Taiwan restano il punto singolo di fallimento della filiera; Hormuz pesa sui campus del Golfo e sul GNL che alimenta il progetto italiano.

## 8. Legami con i mercati (`prezzi.json`, chiusure al 2026-11-09, SK Hynix al 2026-11-06)

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

## 9. Otto fatti attuali (numero, data, fonte)

1. **Google investirà almeno 13 mld EUR in Finlandia nel 2027-2028**, il suo maggiore investimento singolo in Europa: ampliamento di Hamina e tre nuovi data center a Kajaani, Vaala e Muhos, con un contratto di 22 anni con Fortum legato alla centrale nucleare di Loviisa (Google, 2026-09-09).
2. **Microsoft ha aperto la regione cloud Denmark East** con campus a Høje-Taastrup, Køge e Roskilde; Høje-Taastrup recupera il calore per circa 6.000 case (Microsoft, 2026-03-27).
3. **Il polo di Frankfurt ha 997 MW di capacità IT operativa** (JLL); CBRE conta 1,2 GW nel 1° trimestre 2026 e i nuovi allacci grandi nella regione Reno-Meno richiedono fino a 13 anni (JLL, 2026).
4. **Johor ha raggiunto 1.110 MW di capacità IT operativa** nel 1° semestre 2026 (+24% sul semestre), con 602 MW in costruzione e un tasso di sfitto dello 0,7% (Cushman & Wakefield e Knight Frank, via EdgeProp, 2026).
5. **Nessuna gigafabbrica AI dell'UE è stata ancora scelta**: il bando EuroHPC per fino a 7 siti è aperto dal 2026-07-30 con scadenze tra novembre 2026 e febbraio 2027; le 19 "AI Factories" già selezionate sono in mappa dove il sito è noto (EuroHPC JU, 2025-10-10 e 2026-07-30).
6. **DataVolt e Humain hanno avviato ad agosto 2026 il cantiere di 100 MW** del primo lotto da 360 MW del campus di Oxagon (NEOM), obiettivo 1,5 GW; a ottobre Nebius ha firmato un accordo preliminare per 50 MW (AGBI, 2026-08; Baxtel, 2026-10).
7. **Micron avvia a metà ottobre 2026 la produzione HBM nel secondo impianto di impacchettamento di Taichung** e dichiara oltre NT$1.600 mld (circa 50 mld USD) investiti a Taiwan (Focus Taiwan, 2026-10-01).
8. **Microsoft si è ritirata a ottobre 2026 dal campus Nscale di Loughton** (50 MW, 23.040 GPU GB300) per ritardi dell'allaccio elettrico, che potrebbe arrivare solo negli anni 2030 (Computing, 2026-10).

Altri fatti utili, sempre con fonte nel file: il Centro nazionale di calcolo AI coreano a Haenam è in costruzione dal 2026-08-03 (2,4 trilioni KRW, Asia Economy); KDDI ha avviato il data center AI di Sakai il 2026-01-22 (Adnkronos); CXMT è stimata a circa 320.000 wafer/mese di DRAM ma solo 5.000 di HBM (Tom's Hardware/SemiAnalysis); i data center hanno usato il 22% dell'elettricità misurata dell'Irlanda nel 2024 (CSO).

## 10. Proposta per la mappa (al coordinatore)

- **Nuove categorie da stilizzare in `xai`**: `packaging` (suggerito: triangolo vuoto o rombo, stesso colore delle fab), `attrezzature` (suggerito: stella o croce), `hub-data-center` (suggerito: cerchio grande sfumato, raggio fisso, perché `mw` è la capacità di un mercato metropolitano, non di un sito). Oggi cadono nel quadrato da 4 px.
- In `xai` saltare i punti con `duplicato_ai_json: true` quando è acceso anche il livello `ai`, oppure sempre.
- Per i `data-center-ai` si può usare `mw_previsto` come anello tratteggiato; per i cluster Epoch 2025 (`origine_dato: "epoch-gpu"`) un tono più chiaro, perché lo stato è "esisteva nel 2025".
- `ai.json` usa solo categorie già note alla mappa: nessuna modifica necessaria per il livello fisso.

## 11. Limiti

- **Coordinate stimate.** Gli indirizzi Epoch USA sono geocodificati a livello di edificio o via quando possibile (precisione 1-2 km), altrimenti al comune; otto siti Epoch non hanno indirizzo (es. Stargate Milam, Google Mesa) e stanno sul comune o sulla contea (fino a 40 km). Molti siti curati in Asia e nel Golfo sono al livello di città (12-30 km). Alcuni punti coincidono (Fab 14, Fab 18 e AP8 nel parco scientifico di Tainan; tre voci di Navi Mumbai).
- **Assunzioni da verificare** (scritte nelle note): sito di ABCI-Q (Tsukuba, 40 km), Gefion (area di Copenaghen), NHN Cloud a Gwangju, DAEDALUS a Lavrio, Cassava AI Factory a Città del Capo, Explorer-WUS3 nell'area di Phoenix.
- **Non in mappa per mancanza di sito**: data center xAI-Humain da 500 MW in Arabia Saudita, OpenAI-Tata HyperVault in India (100 MW → 1 GW), Schwarz 240 MW nel Meclemburgo, Stargate Korea in South Jeolla, Nebius in Israele e in Pennsylvania, 17 sistemi TOP500; Shin-Etsu e SUMCO (wafer) per mancanza di fonte raggiungibile sullo stabilimento.
- **Dati datati**: i wafer/mese e i nodi presi da Wikipedia sono storici; l'archivio GPU clusters di Epoch è fermo al 2025; molti progetti esteri sono solo annunci (stato = ultima fonte, con data).
- **Hub**: i MW dei mercati vengono da consulenti diversi (JLL, CBRE, Cushman & Wakefield, MeitY) con definizioni diverse (IT operativa, inventario, capacità totale): non vanno sommati tra loro né con i siti singoli. Per Amsterdam e Londra non è indicato un MW coerente.
- **Nomi in italiano**: 10 punti curati mantengono il `nome` italiano perché `supply-chain-ai/nodi.json` li cita per nome; il nome inglese è in `nome_en` (usato in `ai.json`). Quando il coordinatore aggiorna `nodi.json`, si possono sostituire.
- **Licenze**: Epoch CC BY 4.0 (citare "Epoch AI"); TOP500 senza licenza aperta dichiarata (citare); Wikipedia CC BY-SA 4.0; OSM ODbL per le coordinate.

## 12. Note per la regia

- `docs/index.html` e i workflow non sono stati toccati. Lo script gira senza chiavi in pochi secondi e non usa Nominatim (le coordinate sono nei file curati).
- Se Epoch aggiunge un sito, lo script lo segnala in `errori` finché non si aggiunge una riga a `epoch_coordinate.json`; un sito TOP500 nuovo va aggiunto a `top500_siti.json` (o marcato `posizione_sconosciuta`).
- `python3 raccolta/ai/raccogli.py --valida` controlla i tre file (`ai-mondo.json`, `ai.json`, `investimenti.json`) senza rete, compreso il limite di 1,5 MB.
- Lo User-Agent dello script è ora generico (non contiene il nome del progetto).
