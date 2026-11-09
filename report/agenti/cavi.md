# Agente CAVI SOTTOMARINI: rapporto

Data: 2026-11-09. Script: `raccolta/cavi/raccogli.py` (solo libreria standard, eseguito davvero il 2026-11-09, circa 25 secondi). Incidenti curati a mano in `raccolta/cavi/incidenti.json`. Lo script li controlla e li copia.

## 1. Fonti provate

| Fonte | Esito | Licenza |
|---|---|---|
| TeleGeography, API v3 `cable/all.json` (713 cavi) | funziona | CC BY-NC-SA 3.0 |
| TeleGeography `cable/cable-geo.json` (734 geometrie, 14.463 vertici) | funziona | CC BY-NC-SA 3.0 |
| TeleGeography `landing-point/landing-point-geo.json` (1.928 approdi) | funziona | CC BY-NC-SA 3.0 |
| TeleGeography `cable/<id>.json` (proprietari, anno RFS, lunghezza, approdi con paese): 713 richieste, 6 in parallelo | funziona, nessuna chiave | CC BY-NC-SA 3.0 |
| Notizie sugli incidenti (WebSearch) | funziona | fatti citati con la fonte |
| Lettura diretta di alcuni siti (windward.ai, tomshardware.com, abc.net.au, thediplomat.com) | **non funziona**: il dominio è bloccato dalla rete di questa sessione. Ho usato solo quello che riportano le ricerche, con link alla fonte originale | — |

**Licenza da segnalare.** I dati TeleGeography sono **CC BY-NC-SA**: si possono usare solo in modo non commerciale e citando TeleGeography. Anche un file derivato come `cavi.json` va condiviso con la stessa licenza. Per questo progetto personale va bene. Se il progetto diventasse commerciale non andrebbe più bene. Inoltre l'API v3 non è documentata e potrebbe cambiare senza preavviso.

## 2. Cosa contengono i file

**`docs/data/cavi.json`** (1,27 MB):
- `elementi`: 713 cavi, di cui 608 attivi e 105 pianificati. Ogni cavo ha `id`, `nome`, `stato`, `anno` (entrata in servizio, RFS), `proprietari`, `fornitori`, `km`, `paesi` (codici ISO2), `n_approdi`, `approdi_it`, `s`, `colore` (il colore di TeleGeography), `link` e `g`.
  - `s` è la lista dei passaggi strategici che il cavo attraversa.
  - `g` è la geometria, semplificata con Douglas-Peucker (0,02°) e arrotondata a 3 decimali.
- `approdi`: 1.928 punti con `lat`, `lon`, `paese` ISO2, `cavi` (gli id dei cavi che vi approdano) e `stato` ("da definire" se l'approdo non è ancora fissato).
- `riepilogo`: numero di cavi per passaggio e quadro dell'Italia.

**Come è calcolato `s`.** Ho disegnato a mano dei poligoni grossolani e controllato quali cavi ci passano, con la linea originale infittita ogni 0,1°. I nomi dei passaggi sono quelli di `labels.json`.

| Passaggio | Cavi (attivi + pianificati) |
|---|---|
| Mar Rosso | 24 |
| Bab el-Mandeb | 16 |
| Canale di Suez | 14 |
| Stretto di Hormuz | 7 |
| Stretto di Malacca | 28 |
| Stretto di Taiwan | 4 |
| Stretto di Luzon | 13 |
| Mar Baltico | 34 |
| Stretti danesi | 12 |
| Stretto di Gibilterra | 5 |
| Canale di Sicilia | 29 |
| Mar Mediterraneo | 84 |

"Canale di Suez" vuol dire che il cavo passa sia nel Mar Rosso sia nel Mediterraneo, cioè attraversa l'Egitto via terra.

**`docs/data/cavi-incidenti.json`**: 14 incidenti tra febbraio 2023 e agosto 2026, ognuno come punto.
- Campi: `data_evento`, `zona`, `cavi`, `cavi_id` (il collegamento a `cavi.json` dove è certo), `s`, `causa`, `esito`, `categoria`, `stato`, `fonte`, `link`, `data_fonte`, `affidabilita`.
- **Le coordinate sono tutte stimate** (`origine_coord: stimata`, con `precisione_km` tra 5 e 60). Le fonti indicano una zona, quasi mai un punto preciso.
- `affidabilita` dice quanto è sicuro che il fatto sia avvenuto. La causa è spesso solo un'ipotesi ed è descritta nel campo `causa`.

## 3. Fatti attuali rilevanti

1. **Mar Rosso, 24 febbraio 2024.** Tre cavi tagliati: AAE-1, Seacom e EIG. Causa ritenuta probabile: l'ancora della Rubymar, nave colpita dagli Houthi il 18 febbraio e affondata il 2 marzo. La riparazione è partita solo a luglio 2024 (Kentik; Data Center Dynamics).
2. **Mar Rosso, 6 settembre 2025.** SMW4 e IMEWE tagliati vicino a Gedda, e il Kuwait ha segnalato un danno a FALCON. Ci sono stati rallentamenti in India, Pakistan ed Emirati e latenza più alta su Microsoft Azure. Causa non accertata (AP/Arab News, 7 settembre 2025).
3. **Baltico, 25 dicembre 2024.** L'elettrodotto Estlink 2 e 4 cavi dati sono stati danneggiati. Secondo l'accusa, la Eagle S (flotta ombra russa) ha trascinato un'ancora da 11 t per circa 90 km. Estlink 2 è rimasto fermo circa 6 mesi, con almeno 60 milioni di euro di riparazioni.
   - Il 3 ottobre 2025 il tribunale si è dichiarato senza giurisdizione.
   - Il 27 agosto 2026 la Corte d'appello di Helsinki ha riaperto il caso (The Record).
4. **Baltico, 17–18 novembre 2024.** Danneggiati BCS East-West Interlink e C-Lion1. È sospettata la Yi Peng 3, nave cinese con comandante russo. Entrambi ripristinati il 28 novembre.
5. **Baltico, 31 dicembre 2025.** Danneggiati i cavi Elisa e Arelion tra Helsinki e Tallinn. Il 5 novembre 2026 il tribunale di Helsinki ha condannato il comandante della Fitburg a 42 mesi e il nostromo a 34, per danneggiamento aggravato. Prima condanna di questo tipo nel Baltico; la sentenza non è definitiva (Euronews, Meduza).
6. **Taiwan.**
   - 25 febbraio 2025: tagliato il cavo Taiwan-Penghu n. 3. Il comandante cinese della Hong Tai 58 è stato condannato a 3 anni il 12 giugno 2025 (Taipei Times).
   - 3 gennaio 2025: cavo danneggiato al largo di Yehliu, sospettata la Shunxin-39 con due identità AIS. Il Financial Times lo indica come il cavo TPE.
   - 29 aprile 2026: Dongyin (Matsu) isolata. Causa probabile: relitti spostati dal mare grosso (ministero degli affari digitali di Taiwan).
7. **Siria, 14 giugno 2026.** Interrotto il collegamento Tartus-Alessandria (Aletar). Kentik ha mostrato che la fibra era stata segata a terra, in un pozzetto, non in mare. Il traffico è passato su Ugarit (Cipro) e via Turchia; ripristino il 17 giugno.
8. **Australia, 8–9 agosto 2026.** Guasti a Indigo West e Indigo Central dentro la zona protetta di Perth. SUBCO ha denunciato il fatto alla polizia federale australiana (AFP); la causa non è accertata (iTnews).
9. **Hormuz, 2026.** Nessun taglio confermato. A marzo 2026 il costruttore ASN ha dichiarato forza maggiore per la posa di 2Africa Pearls nel Golfo. TeleGeography (Alan Mauldin, citato dal FT) dice che tutti i progetti di cavi nel Golfo e a Hormuz sono "rinviati a tempo indeterminato", compresi SEA-ME-WE 6 e Fibre in Gulf. Secondo Dawn/Reuters, a maggio 2026 i Pasdaran (IRGC) hanno minacciato di chiedere "permessi" per i cavi che attraversano lo stretto.

## 4. Focus Italia

Dati TeleGeography del 2026-11-09:
- **55 approdi** in Italia e **37 cavi**, di cui 32 attivi e 5 pianificati.
- La Sicilia ha **19 cavi**.
- Approdi principali per numero di cavi: **Mazara del Vallo 8**, **Genova 7**, **Catania 5**, **Bari 4**, Palermo 2. Molti approdi minori servono il "Piano Isole Minori" di Infratel (2024).

| Approdo | Cavi |
|---|---|
| Mazara del Vallo | Medusa (2026), MENA/GBI, Unitirreno, Janna, Italy-Libya, GO-1 (Malta), Didon e Hannibal (Tunisia) |
| Genova | 2Africa, Blue (Google-Sparkle), Medloop, Unitirreno, Andromeda; pianificati EMC West-1 (2027) e Barracuda (2028) |
| Catania | SeaMeWe-5, IMEWE, MedNautilus, Epic Malta-Sicily, Italy-Malta |
| Bari | AAE-1, Jonah (Israele), Italy-Albania, OTEGLOBE |
| Palermo | SeaMeWe-4 e Blue; vi ha sede il Sicily Hub di Sparkle, data center neutrale collegato agli approdi siciliani. Il ministro Urso propone Palermo come centro europeo di controllo dei cavi del Mediterraneo (Milano Finanza, settembre 2026) |

**Dipendenza dal Mar Rosso.** I cavi che collegano direttamente l'Italia all'Asia passano tutti dal Mar Rosso e dall'Egitto.
- Attivi: 2Africa (Genova), AAE-1 (Bari), SeaMeWe-4 (Palermo), SeaMeWe-5 e IMEWE (Catania), MENA/GBI (Mazara).
- Pianificati: IEX (Savona) e EMC West-1 (Genova).
- Per 6 dei 6 cavi attivi il calcolo dà Bab el-Mandeb. È un'approssimazione: 2Africa e MENA/GBI hanno anche approdi interni al Mar Rosso.

**Tre di questi cavi sono stati colpiti negli incidenti 2024–2025: AAE-1, SeaMeWe-4 e IMEWE.** Il rischio per l'Italia è soprattutto di capacità e di latenza verso Asia e Golfo, non di isolamento: il traffico verso il resto d'Europa passa via terra e su altri cavi.

**Proprietà.** La vendita di Sparkle (stazioni di approdo e dorsale di backhaul) da TIM al MEF (70%) e a Retelit (30%), per 700 milioni di euro, è stata firmata il 14 aprile 2025 e approvata dalla Commissione UE ad aprile 2026. Il closing aspettava ancora il via libera della FCC statunitense (FinanzaOnline, Corriere Comunicazioni). È una valutazione: lo Stato si riprende il controllo dell'hub siciliano.

## 5. Collegamenti con gli altri livelli della mappa

- **Stretti (`stretti.json`, `labels.json`)**: il campo `s` usa gli stessi nomi, quindi nel pannello di uno stretto si può aggiungere la riga "cavi dati: N" accanto a petrolio e GNL. Bab el-Mandeb, Suez e Hormuz sono colli di bottiglia sia energetici sia digitali.
- **Condotte (`condotte.json`, `linee.json`)**: Balticconnector (2023) ed Estlink 2 (2024) mostrano che gasdotti, elettrodotti e cavi dati vengono colpiti dagli stessi trascinamenti d'ancora. Si possono mostrare insieme come "infrastruttura sottomarina".
- **Attacchi ibridi (`ibrido.json`)**: la scheda IB-20261107-25 (condanna Fitburg, 5 novembre 2026) è lo stesso fatto di CI-2025-05. Si può collegare tramite id o mostrare un solo simbolo. Gli incidenti del Baltico (2023–2025) e di Taiwan rientrano nella categoria `sabotaggio` del dossier ibrido. Mar Rosso, Matsu 2026 e Perth hanno invece causa accidentale o ignota e non vanno presentati come sabotaggi.
- **Dossier AI e data center (`ai.json`)**: oggi contiene solo siti negli Stati Uniti. I collegamenti utili sono due.
  - I piani di AI del Golfo (Emirati, Arabia Saudita, Qatar) dipendono da cavi che passano da Hormuz e dal Mar Rosso, e tutti i nuovi progetti nel Golfo sono fermi (punto 9).
  - In Italia, i cavi diretti in Asia arrivano in Sicilia e a Genova e Bari, ma i data center sono a Milano: il backhaul terrestre Sicilia-Nord è un punto critico da mostrare quando il dossier AI includerà l'Italia.
- **Mercati**: nessun effetto diretto misurabile sui prezzi. Gli effetti sono sui costi di riparazione (Seacom ha visto calare i margini per la riparazione 2024) e sui tempi, perché le navi posacavi sono poche e serve il permesso di lavorare in zone di guerra.

## 6. Proposta di visualizzazione sulla mappa

- **Cavi**: linee sottili con il `colore` di TeleGeography (oppure grigio, con l'Italia in evidenza), tratteggiate se `stato = pianificato`. Al clic: nome, anno, proprietari, km, passaggi `s` e link a TeleGeography.
- **Filtro "passa da…"** sui valori di `s`: per esempio "mostra solo i cavi da Bab el-Mandeb".
- **Approdi**: punti piccoli, visibili solo con lo zoom; i 5 hub italiani sempre visibili con etichetta.
- **Incidenti**: icona "cavo spezzato" con un cerchio di raggio `precisione_km`. Rosso se c'è un sospetto di intenzionalità o un sabotaggio, grigio se la causa è naturale o ignota. Al clic: causa, esito e fonte.
- **Didascalia obbligatoria**: "Dati TeleGeography, CC BY-NC-SA".

## 7. Limiti

- I tracciati TeleGeography sono **schematici**, non la posa reale. Alcuni cavi sono disegnati a pezzi: Tata TGN-Gulf, per esempio, risulta senza Hormuz.
- I poligoni dei passaggi sono grossolani, quindi ci possono essere falsi positivi lungo le coste (Fuzhou, Musandam, Kattegat).
- TeleGeography mostra 2Africa come "attivo" nel suo insieme, anche se il segmento del Golfo (Pearls) è fermo. `stato` vale per il sistema, non per i singoli segmenti.
- Mancano i cavi dismessi, militari e privati non dichiarati, e mancano gli elettrodotti (Estlink, Elmed Italia-Tunisia in costruzione).
- Le date e le cause degli incidenti vengono dalla stampa. Le coordinate sono stime e non posizioni pubblicate. Le pagine di windward.ai, tomshardware.com, abc.net.au e thediplomat.com non erano raggiungibili da questa sessione e vanno abilitate in rete se si vuole verificarle direttamente.
- Lo script fa circa 716 richieste al giorno a un'API non documentata. Se TeleGeography le limita, conviene scaricare i dettagli una volta alla settimana.
