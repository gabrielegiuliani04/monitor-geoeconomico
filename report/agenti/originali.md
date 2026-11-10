# Revisione dei livelli originali della mappa (10 novembre 2026)

Agente: revisione dei livelli originali. File rivisti: `fissi.json`, `italia.json`, `iran.json`, `difesa.json`, `mobili.json`, `eventi.json`, `ibrido.json` e i metadati di licenza di `linee.json` e `condotte.json`.
Copia dei file prima delle modifiche: `raccolta/originali/backup/` (non pubblicata nel sito).
Controllo automatico: `raccolta/originali/controlla.py` (solo libreria standard), rapporto completo in `raccolta/originali/controllo.json`.
Schema e nomi dei campi non sono cambiati. `docs/index.html` non è stato toccato. Nessun commit.

In questo testo **verificato** vuol dire che ho confrontato il punto con una fonte esterna: archivio di coordinate, fonte datata 2025-2026 o seconda fonte indipendente. Il controllo automatico dello schema vale per tutti i punti e lo conto a parte.

## Riepilogo

| File | Punti | Verificati | Corretti | Aggiornati | Rimossi | Da rivedere (data_fonte > 90 giorni) |
|---|---|---|---|---|---|---|
| fissi.json | 192 (33 basi, 159 porti) | 63 (33%) | 159 porti (link WPI) | 3 | 0 | 169 (156 porti WPI, 13 basi) |
| italia.json | 58 | 58 (100%) | 12 (10 coordinate, 2 nomi o categorie) | 58 (stato e fonti) | 0 | 19 |
| iran.json | 53 | 45 (85%) | 4 (link WPI) | 9 | 0 | 41 |
| difesa.json | 8 | 8 (100%) | 0 | 4 | 0 | 8 |
| mobili.json | 53 | 53 (100%) | 1 (affidabilità) | 25 posizioni, 2 marcate come datate | 0 | 0 |
| eventi.json | 126 | 25 (20%) | 7 (affidabilità) | 9 (seconda fonte) | 0 | 0 |
| ibrido.json | 36 → 35 | 21 (58%) | 13 (affidabilità) | 15 | 1 | 0 |
| linee.json | 588 linee | metadati | licenza | — | 0 | 0 |
| condotte.json | 454 linee | metadati | licenza | — | 0 | 0 |

`controlla.py` al 10 novembre: **0 errori** su tutti i file. Restano 164 avvisi:
- 155 porti WPI con una sola fonte: va bene, il WPI è una fonte primaria;
- 4 basi italiane «alta» con una sola fonte primaria (Aeronautica Militare, NATO);
- RAF Akrotiri, con il solo Forces News;
- due avvisi UKMTO, fonte primaria;
- una fonte senza data (Camp Arifjan);
- due basi di Gibuti con le stesse coordinate della base giapponese di `basi-mondo.json`.

## Duplicati con `basi-mondo.json`

Nessun duplicato: nessuna base dei quattro file fissi sta entro 10 km da una base di `basi-mondo.json` con lo stesso utilizzatore.

Unico caso da segnalare, già noto al rapporto `basi.md`: **Camp Lemonnier** (US) e **Forze francesi a Gibuti** (FR) in `fissi.json` hanno le stesse coordinate della base giapponese **BM-135** in `basi-mondo.json`, cioè quelle dell'aeroporto di Gibuti. Sono basi diverse e restano tutte e tre.

## fissi.json

**Verificati (63):**
- le coordinate delle 19 basi con codice ICAO, confrontate con OurAirports: scarto 0-0,01 km;
- 44 porti WPI, 28% del totale, confrontati con OpenStreetMap: entro 10 km, cioè il margine di arrotondamento del WPI, tranne alcuni casi in cui il geocodificatore ha trovato la regione o la città invece del porto (Gibuti, Bushehr, Latakia, Alanya). Ho ricontrollato quei casi a mano: le coordinate sono plausibili;
- lo stato di Isa, Diego Garcia, Muwaffaq Salti, Tower 22, Incirlik e Kürecik, cercando fonti successive al 1° ottobre 2026;
- l'assenza di duplicati per tutte le 33 basi.

**Corretti:**
- 317 link al World Port Index (159 porti, più le fonti delle basi) puntavano alla copia di terzi `github.com/Yusnelkis/world-port-index-dashboard`. Ora puntano alla fonte ufficiale NGA, `https://msi.nga.mil/Publications/WPI`;
- in `archivi.porti` ho annotato che i valori sono stati letti il 16 marzo 2026 dalla copia di terzi. Il sito NGA rispondeva 503 il 9 e il 10 novembre, quindi non ho potuto rileggere i dati dalla fonte ufficiale.

**Aggiornati:**
- **Isa Air Base:** affidabilità da media ad alta. Il Washington Post (6 maggio 2026) documenta danni ai Patriot di Isa e Riffa: seconda fonte indipendente oltre a Wikipedia.
- **Diego Garcia:** data_fonte al 6 ottobre 2026. Al Jazeera la indica ancora tra le basi avanzate dei bombardieri USA.
- **Muwaffaq Salti:** aggiunto l'attacco missilistico iraniano del 22 luglio 2026, con quattro missili intercettati dalla Giordania (AP).

**Da rivedere:** per queste basi non ho trovato fonti successive a quelle già presenti.
- Camp de la Paix e Prince Hassan: fonte del 4 marzo 2026;
- Incirlik: 28 febbraio 2026;
- Kürecik: 10 marzo 2026;
- forze francesi e base italiana a Gibuti;
- comando Qatar-Turchia: 23 marzo 2026;
- Nevatim, Ramon, Ovda e Palmachim;
- Ain al-Asad e Al-Tanf: lasciate, quindi lo stato non dovrebbe cambiare.

## italia.json: tutte le 58 basi verificate

**Coordinate:**
- 35 punti avevano coordinate da OurAirports o Wikidata: tutte confermate, con scarto inferiore a 0,2 km;
- 23 punti erano stimati sul centro di una città. Per 10 ho trovato la caserma o l'area e ho corretto le coordinate (sotto, origine `fonte`). Gli altri 13 restano stimati, perché nessuna fonte nomina la caserma.

**Stato:**
- 45 basi: `operativo`, con fonti datate 2025-2026, delle quali 27 con affidabilità alta;
- 13 basi: stato vuoto, con la nota che spiega perché. Sono Piacenza, La Maddalena, Grottaglie e 10 comandi dell'Esercito senza notizie datate: Julia, Pozzuolo, Ariete, Granatieri, Aosta, Sassari, Garibaldi, Friuli, BIT e Brigata sostegno AVES.

In ogni nota la frase «Stato non verificato: nessuna fonte datata letta» è stata sostituita con l'esito della verifica. In `archivi.stato` c'è il riepilogo.

> **Per il coordinatore:** l'avviso «stato non ancora verificato» è scritto in `docs/index.html`, riga 350 (`<p class="hint">Italiane, USA e NATO. Posizioni da archivi aperti, stato non ancora verificato</p>`). Non posso modificarlo: va cambiato, per esempio in «stato verificato il 10 novembre 2026 su fonti datate».

**Correzioni di contenuto:**
- **Divisione «Vittorio Veneto»:** dal 15 giugno 2025 è la **Multinational Division South (MND-S)**, nella Caserma Predieri di Firenze-Rovezzano (fonti: Esercito Italiano, fonte primaria; La Nazione, 11 luglio 2025). Ho rinominato il punto e l'ho spostato sulla caserma.
- **Ancona:** non è una base navale. Ci sono il Centro di selezione e la Direzione di Commissariato della Marina (atti del 2026). Il punto ora si chiama «Marina Militare ad Ancona (Centro di selezione e Commissariato)», categoria `comando`.
- **La Maddalena:** la base USA di Santo Stefano è chiusa da gennaio 2008. Ho tolto dalla nota il dubbio «va confermato quando è stata lasciata».
- **Piacenza San Damiano:** non è più una base operativa di volo (MeteoWeb, maggio 2026); resta un presidio dell'Aeronautica. Stato lasciato vuoto.
- **Brigata sostegno AVES:** affidabilità bassa. Dal 2023 i reparti dell'Aviazione dell'Esercito dipendono dalla brigata «Friuli»: va confermato che la brigata esista ancora.

**Coordinate corrette (10), con la fonte:**

| Punto | Nuova posizione | Fonte |
|---|---|---|
| Poligono di Monte Romano | il poligono | OpenStreetMap |
| COMFOP Nord | Caserma Salomone, Padova | Wikipedia + OSM |
| COMFOP Sud | Palazzo Salerno, Napoli | Wikipedia + OSM |
| COMFOSE | San Piero a Grado | Wikipedia + OSM |
| MND-S | Caserma Predieri | OSM |
| Ariete | Caserma Mittica, Pordenone | Wikipedia/prefettura + OSM |
| Folgore | viale Marconi 20, Livorno | bando dell'Esercito 2026 + OSM |
| Sassari | Caserma La Marmora | Wikipedia + OSM |
| Garibaldi | Caserma Ferrari-Orsi, Caserta | OSM |
| BIT | Caserma Santa Barbara, Anzio | Wikipedia + OSM |

**Licenza:** queste 10 coordinate vengono da OpenStreetMap, che è **ODbL** (attribuzione e share-alike per la banca dati). Va aggiunto in `DATA_LICENSES.md` e in `report/licenze.md` alla riga di `italia.json`.

**Fatti verificati su alcune basi:**
- Sigonella: «pienamente operativa» durante l'eruzione dell'Etna (Stars and Stripes, 20 agosto 2026). A marzo 2026 l'Italia ha negato l'atterraggio ad aerei USA diretti contro l'Iran (Al-Monitor; The Aviationist, 8 aprile).
- Augusta: il 15 giugno 2026 vi sono partiti i cacciamine italiani per Hormuz. Il 25 ottobre il cacciatorpediniere USS Stout ha perso l'alimentazione nella rada di Augusta (USNI News, 5 novembre).
- Niscemi: una frana a marzo 2026 al margine dell'area del MUOS (Catania LiveUniversity, 9 marzo). Il 31 ottobre lo US Space Force ha esteso il programma MUOS fino al 2040 (SatNews).
- Trapani: a gennaio 2026 è stato approvato il centro di addestramento F-35 da 112,6 milioni di euro (The Aviationist, 7 gennaio).
- Cameri: il 22 luglio 2026 ha volato il primo F-35 polacco assemblato alla FACO (The Aviationist).
- Gaeta: il 31 luglio 2026 la USS Mount Whitney ha cambiato comandante (Stars and Stripes); la data della sua radiazione non è chiara.
- JFC Naples: 75 anni, festeggiati a giugno 2026 (Report Difesa). Il comando passa a guida europea (Wanted in Rome, 11 febbraio 2026).

**Da rivedere:** 19 punti hanno la data_fonte più recente oltre i 90 giorni, ma sono comunque verificati con fonti del 2025-2026. Tra questi:
- Ghedi: fonte del 7 gennaio 2026;
- Cagliari: agosto 2025;
- Caserma Ederle: settembre 2025;
- Comando Truppe Alpine: dicembre 2025.

## iran.json

**Verificati (45):** le coordinate di tutti i 45 siti che citano OurAirports (20) o Wikidata (25), tutte confermate. Lo stato di 10 siti, con fonti di luglio-novembre 2026.

**Corretti:** 4 link al WPI, portati a NGA.

**Aggiornati (9):**
- **Bandar Abbas, Imam Ali (Chabahar) e Qeshm:** raid USA del 1° settembre 2026 contro siti dei Pasdaran (Al-Monitor, che cita il CENTCOM).
- **Dezful:** il Wall Street Journal (24 luglio) vede gli ingressi dei tunnel scavati di nuovo. È la seconda fonte indipendente oltre alla CNN: affidabilità alta.
- **Bandar Anzali:** da `danneggiato` a `in-riparazione`. Ricostruzione parziale del cantiere dei Pasdaran secondo il WSJ, su immagini Planet di luglio. Affidabilità alta.
- **Kermanshah:** aggiunta la fonte WSJ.
- **Shahroud e Garmdareh:** da stato vuoto a `in-riparazione`. Un'inchiesta BBC con la società MAIAR, ripresa da Arab News il 6 novembre 2026, li indica come siti colpiti nell'ultimo anno e ora in costruzione. È una sola fonte (Arab News riprende la BBC): affidabilità media.
- **Fordow:** MAIAR segnala lavori agli ingressi dei tunnel. Lo stato resta `fuori-servizio`.

**Da rivedere:** 41 siti, quasi tutti con fonti di marzo 2026 (Alma, FDD). In particolare le 17 basi aeree tattiche e le basi missilistiche di Tabriz, Khorramabad, Isfahan, Shiraz, Borazjan, Khormuj, Jam, Lar e Hajiabad: dopo la tregua dell'8 aprile e le riparazioni documentate a luglio e novembre, lo stato `danneggiato` potrebbe essere superato.

## difesa.json

**Verificati:** tutti gli 8 siti. Le coordinate delle due batterie THAAD stanno sulle basi indicate da OurAirports.

**Aggiornati (4):**
- **Radar di Jask:** aggiunti i raid del CENTCOM del 9-10 giugno 2026, con obiettivi anche a Jask (investingLive). Non è detto che il radar sia stato colpito: stato vuoto.
- **Ruwais/Sader:** il 20 marzo 2026 è stata approvata la vendita d'urgenza agli Emirati di radar e nodi di comando THAAD per 4,5 miliardi di dollari (Army Recognition).
- **Muwaffaq Salti e Prince Sultan:** aggiunto il rapporto CRS IF12645 del 23 giugno 2026. Secondo il CRS il danno ai radar è «riportato da alcune fonti», non confermato.

**Da rivedere:** tutti gli 8 siti, perché nessuna fonte ha meno di 90 giorni. Lo stato dei radar colpiti a marzo, cioè riparati, sostituiti o ritirati, non è pubblico.

## mobili.json (navi e aerei)

**Verificati:** le date di tutti i 53 elementi. Le posizioni delle navi USA sono confrontate con il **Fleet and Marine Tracker USNI del 9 novembre 2026**. La pagina web di USNI risponde 403 a questa sessione; il testo l'ho letto dal feed RSS di news.usni.org.

**Aggiornati (25):** la posizione precedente è conservata in `storico[]`.
- **Bush e Donald Cook:** dal Golfo di Oman (7 novembre) al Mar Arabico (USNI, 9 novembre). Per la Bush, affidabilità alta.
- **George Washington, Shoup e Ross:** Mar Arabico, al 9 novembre. **John Paul Jones e Carl M. Levin:** «nella regione», al 9 novembre.
- **Boxer, Comstock e Portland:** dall'Oceano Indiano generico al Mar delle Laccadive.
- **Jason Dunham e Gonzalez:** ancora nel Mar Rosso.
- **Theodore Roosevelt, Chosin, Decatur e Paul Hamilton:** dallo Stretto di Malacca al **Mare delle Andamane**. Sono ripartiti da Singapore il 9 novembre; sono attesi in Medio Oriente per dare il cambio alla George Washington (USNI, 6 novembre).
- **Makin Island, Anchorage e John P. Murtha:** da Yokosuka, con il «?», al **Mar del Giappone**. Sono partiti il 7 novembre. Il dato «verso l'area CENTCOM» non è confermato da USNI.
- **Tripoli:** a Sasebo.
- **Nimitz:** nell'Atlantico occidentale.
- **Eisenhower:** a Norfolk. È uscita il 4 ed è rientrata il 5 novembre.
- **Ronald Reagan:** dal Pacifico orientale a **Bremerton**, dove è arrivata il 3 novembre.

**Marcati come datati:** posizioni con più di 14 giorni. Hanno ora `dubbia: 1` e la nota comincia con «Dato datato».
- **Charles de Gaulle:** dato del 5 ottobre. Ferma a Tolone, con il ritorno in mare previsto a inizio dicembre (una sola fonte).
- **Trieste:** dato del 14 settembre. Era nel cantiere di Trieste; la partenza era prevista verso metà novembre e non è confermata.

**Corretti:** la Liaoning passa da affidabilità alta a media. In `fonti[]` c'è solo The Boston Report.

**Riservatezza:** non ho aggiunto dettagli oltre quelli pubblici. Le posizioni sono quelle del tracker USNI e dei comunicati, cioè mari e porti, non coordinate precise in mare.

## eventi.json

**Verificati (25):**
- 9 eventi con una seconda fonte indipendente:
  - attacco a DTEK Odesa del 2 novembre;
  - impianti energetici di Bila Tserkva e Obukhiv del 6 novembre;
  - sottostazioni di Vinnytsia, Rivne, Kharkiv e Dnipro del 7 novembre (Interfax, che cita Zelensky);
  - hotel di Kremenchuk dell'8 novembre (AMK Mapping).
- 3 eventi confrontati con `notizie.json`, già con più fonti: Aramco a Riyadh, raffineria di Kirishi, Khor Mor;
- 13 eventi controllati nelle coordinate:
  - aeroporti e basi, con OurAirports: Gvardeyskoe, King Khalid, Dubai World Central;
  - raffinerie e centrali, a mano: Kirishi, Ryazan, YANOS, Kstovo, centrale di Zaporizhzhia, Akhtubinsk, Marinovka e altri.

La regola dell'affidabilità è stata controllata su tutti i 126 eventi.

**Corretti (7):** affidabilità da alta a media. Avevano una sola fonte secondaria e non ho trovato una seconda fonte:
- GI-20261105-15 e GI-20261105-16, Bucha e Dnipro;
- GI-20261106-05, Kiev;
- GI-20261107-13 e GI-20261107-14, Bucha e Obukhiv;
- GI-20261109-13 e GI-20261109-14, Sumy e Kharkiv.

Restano alta con una sola fonte i due avvisi **UKMTO**: è una fonte primaria.

**Da rivedere:** nessuno per data. Il 20% di verifica sul contenuto è sotto il 30% chiesto: va completato per gli eventi del fronte ucraino (FR-…) che hanno una sola fonte.

## ibrido.json

**Verificati (21):**
- 14 eventi negli aeroporti, con le coordinate confrontate con OurAirports: scarto ≤ 1,6 km;
- 12 eventi con una seconda fonte indipendente:
  - OS82 a Sofia;
  - Starlink in Lituania (due eventi);
  - droni a Jersey;
  - minacce di bomba del 2 e 3 novembre (Wizz Air a Budapest, LOT a Modlin, Ryanair a Fiumicino, Crown Iris a Syros);
  - Aer Lingus a Évreux;
  - Finnair a Fiumicino;
  - arresto a Reutlingen;
  - condanna dell'equipaggio della Fitburg.

**Aggiornati:**
- **Frigoriferi dei supermercati francesi (IB-20261107-06):** il 9 novembre 2026 la Francia ha attribuito l'attacco dell'11-12 ottobre ai **Pasdaran iraniani**, unità informatica Shahid Kaveh. Ha chiesto mandati d'arresto, ha convocato l'ambasciatore e chiede sanzioni UE. Fonti: Al Jazeera, Al-Monitor/AFP, e in `notizie.json` anche AP e BBC. Ho compilato il campo `attribuito`.
- **IB-20261107-15 e IB-20261107-16:** nella nota ho scritto che l'attribuzione non riguarda ancora gli episodi del 2 novembre.

**Rimosso (1):** **IB-20261107-07**, l'ucraino arrestato in Polonia per i pacchi esplosivi. L'unica fonte, Ukrainska Pravda su Yahoo, è del **21 ottobre 2025**: l'evento è di ottobre 2025, non di ottobre 2026. La data era sbagliata e il punto non era aggiornabile.

**Corretti (13):** affidabilità da alta a media. Avevano una sola fonte secondaria:
- IB-20261107-05, 10, 11, 15, 19, 21, 26, 27, 28 e 29;
- IB-20261108-03, 04 e 05.

## linee.json e condotte.json

Il campo `licenza` diceva «le schede di gem.wiki sono CC BY-NC-SA; uso personale e non commerciale». Ora dice:

> CC BY 4.0 (Global Energy Monitor): dati del Global Oil Infrastructure Tracker e del Global Gas Infrastructure Tracker, con attribuzione a Global Energy Monitor, link e versione. I link alle schede di gem.wiki sono solo riferimenti: i testi di gem.wiki (CC BY-NC-SA) non sono riprodotti.

Geometrie e campi delle linee non sono cambiati. `controlla.py` non trova vertici fuori range né con più di 4 decimali.

## controlla.py

```
python3 raccolta/originali/controlla.py [--oggi AAAA-MM-GG] [--json file] [--rete] [--max N]
```

**Errori (bloccano):**
- campi delle 25 colonne dello schema, più `fonti[]`, mancanti o vuoti;
- `lat` e `lon` non numerici, fuori range o pari a 0,0;
- date non valide o nel futuro (`data_evento`, `data_fonte`, date in `fonti[]`);
- link non http(s);
- link a copie di terzi del WPI;
- `stato` fuori dalle voci che la mappa conosce;
- `affidabilita` fuori da alta, media e bassa;
- paese non ISO a 2 lettere;
- id duplicati;
- posizioni in `mobili.json` più vecchie di 14 giorni senza `dubbia`;
- duplicati con lo stesso utilizzatore entro 2 km da `basi-mondo.json`;
- per `linee.json` e `condotte.json`: licenza diversa da CC BY 4.0, geometrie non valide.

**Avvisi (non bloccano):**
- affidabilità alta con un solo dominio di fonte, oltre agli archivi di coordinate;
- fonti senza data o senza link;
- link principale assente da `fonti[]`.

**Da rivedere:** i punti con `data_fonte` più vecchia di 90 giorni.

L'opzione `--rete` prova un link per dominio con una richiesta HEAD. L'uscita è 1 se ci sono errori. Il controllo del 10 novembre dà 0 errori.

## Limiti e fonti non raggiungibili

- `msi.nga.mil` risponde 503: i porti non sono stati riletti dalla fonte ufficiale.
- `news.usni.org`: la pagina risponde 403, il feed RSS funziona.
- `aeronautica.difesa.it` chiude la connessione e `army.mil` risponde 403. Per queste fonti, segnate «letta tramite motore di ricerca», ho usato titolo, data e testo riportati dal motore di ricerca.
- Alcune date indicate dai riassunti del motore di ricerca erano sbagliate. Due articoli di defensa.com presentati come 2026 erano del 2022 e del 2023, e un articolo dell'Unione Sarda su Teulada era del 2025. Le ho controllate leggendo la data sulla pagina e non le ho usate come fonti 2026. Il piano F-35 di Decimomannu (Unione Sarda) è citato con la sua data vera, 6 ottobre 2024.
