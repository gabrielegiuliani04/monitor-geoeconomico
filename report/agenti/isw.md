# Fronte ucraino ISW/CTP caricato dal browser

Rapporto del 9 novembre 2026. Modulo: `docs/isw-fronte.js`. Il modulo non è ancora integrato in `docs/index.html` e nel repository non è stato copiato nessun dato ISW.

## Avvertenza sulla licenza, da leggere prima di attivarlo

Gli item ArcGIS di ISW hanno un campo `licenseInfo`, e questo campo **vieta l'uso**. Il testo compare nella web map della mappa interattiva (`9f04944a…`), in `VIEW_RussiaCoTinUkraine_V3` e in `Assessed_Russian_Gains_in_the_Past_24_Hours_view`:

> «This geodata is the exclusive intellectual property of the Institute for the Study of War (ISW). You may not use this geodata without the written consent of ISW.»

Non sono riuscito a leggere le condizioni sul sito: understandingwar.org risponde 403 con curl e non è raggiungibile da questa sessione. Anche la ricerca web non ha trovato una pagina di termini ISW. Non ho prove di una regola del tipo «citare e basta» per i dati geografici. La citazione obbligatoria che si legge spesso riguarda le **immagini** delle mappe e i rapporti, non i poligoni.

Il browser scarica i poligoni dal server di ISW e il nostro sito li ridisegna con il suo stile, senza copiarli nel repository. Secondo il testo sopra, anche così si tratta di **uso della geodata**, e serve il consenso scritto di ISW. Il fatto che il servizio sia pubblico, senza login e con CORS aperto è solo una scelta tecnica e non dà una licenza. Per questo **non consiglio di attivarlo sul sito pubblico senza un permesso scritto**. Si può chiedere tramite il contatto press/media di understandingwar.org, spiegando: progetto non commerciale, caricamento dal loro server, attribuzione e link. Nel frattempo, l'alternativa sicura è quella già presente in `fronte.json` (`mappe_esterne`): un link alla mappa interattiva. Il modulo restituisce comunque il testo di licenza nel campo `licenza`, così si può mostrarlo.

## 1. Quale layer contiene la valutazione più recente

| Fonte | Ultima modifica | Contenuto |
|---|---|---|
| **Web map «Assessed Control of Terrain in Ukraine»**, item `9f04944a2fe84edab9da31750c2b15eb` (proprietario `gbarros_understandingwar`). È la mappa usata dalla StoryMap «Interactive Map: Russia's Invasion of Ukraine» (`36a7f6a6f5a9448496de641cf64bd375`) | item modificato l'8/11/2026 alle 18:26 UTC, StoryMap il 9/11 alle 19:59; tutti i feature hanno `pub_date = "2026-11-08"` | **I layer principali non sono FeatureServer**: sono *feature collection* salvate dentro il JSON della web map, già in EPSG:4326. Contiene: Assessed Russian-Controlled Terrain (9 feature, circa 115.400 km² compresa la Crimea), Assessed Russian Advances (50), Assessed Russian Infiltration Areas (190), Claimed Ukrainian Counteroffensives (71, circa 70.000 km² cumulati, quindi include anche le liberazioni del 2022), Claimed Russian Territory (72), Russian-controlled before 24/2/2022 (2). I layer su territorio russo (`Russian_Advances_in_Russia_View/4` ecc.) sono invece FeatureServer normali. |
| `VIEW_RussiaCoTinUkraine_V3/FeatureServer/49` (controllo russo) | `lastEditDate` 29/9/2026, come l'`EditDate` dei feature | 10 feature. **Fermo da sei settimane**: ISW sembra aver spostato l'aggiornamento quotidiano nella web map. |
| `View_AssessedRussianInfiltrationAreasinUkraine_V4/0` (infiltrazioni) | 29/9/2026 | 157 feature |
| `AssessedRussianAdvanceInUkraine_V2_view/0` (avanzate) | 28/9/2026 | **0 feature** |
| `ClaimedRussianTerritoryinUkraine_V2_view/0` (rivendicazioni russe) | 28/9/2026 | 82 feature |
| `MDS_Claimed_Ukrainian_Counteroffensives_V3_view/0` (controffensive) | 6/11/2026 | 68 feature |
| `Assessed_Russian_Gains_in_the_Past_24_Hours_view/0` | 9/11/2026 alle 13:40 | **0 feature** oggi: viene svuotato e riempito |
| `MDS_ClaimedUkrainianCounteroffensivesinthePast24HoursV2_view/13` | 9/11/2026 | 0 feature |
| `Reported_Ukrainian_Territorial_Gains_in_the_Past_24_Hours_view/1` | 12/10/2026 | 4 feature |
| `Assessed_Russian_Control_November`, `Russian_Assessed_Control_of_Terrain_…_to_November` ecc. | timelapse del **2022** | sono vecchi; molti mostrano `lastEditDate` 27/10/2026 solo per una modifica di sistema in blocco (circa 150 servizi con la stessa data) |
| Timelapse mensili (`Ukraine_Timelapse_April_2026_WFL1`, `…_May_2026_view`, `Russo_Ukraine_War_November_2025_Timelapse`…) | dati fino a fine mese, l'ultimo è maggio 2026 | nomi irregolari (WFL1, _view, tutto maiuscolo, Merge), id dei layer casuali, a volte senza campo data. **Non adatti** a cercare «l'ultimo» in automatico. |

**Come cambiano i nomi:** i timelapse sono un servizio al mese con nomi diversi ogni volta. I layer «live» sono viste `_V2`/`_V3`/`_V4` che ogni tanto vengono ricreate, con id di layer non zero (49, 820, 13…). La data di modifica (`lastEditDate`) delle viste può essere falsata da modifiche in blocco. La fonte stabile è la catena **StoryMap → web map**: la StoryMap ha un id fisso ed è il prodotto pubblico di ISW.

## Strategia del modulo (`window.caricaFronteISW()`)

1. Legge `arcgis.com/sharing/rest/content/items/<StoryMap>/data` (pochi KB) e prende la risorsa `type: "webmap"` → `itemId`. Se non ci riesce, usa l'id noto `9f04944a…`.
2. Scarica `items/<webmap>/data?f=json` (1,7 MB compressi, 4,3 MB senza compressione, circa 0,5 s). Assegna il tipo dal titolo del layer con un'espressione regolare: controllo → `ru`, infiltrazioni → `contesa`, avanzate (e guadagni delle 24 ore, se presenti) → `avanzata`, controffensive ucraine rivendicate → `controffensiva`. Salta le rivendicazioni russe e il «prima del 24/2». Semplifica i poligoni nel browser (Douglas-Peucker con tolleranza 0,002°, 4 decimali), raggruppa i buchi negli anelli esterni e tiene il senso di rotazione di Esri, così i buchi restano buchi con il riempimento nonzero di `buildFront`. `d` = `pub_date`.
3. Se il punto 2 fallisce, ripiega sui FeatureServer: elenca i servizi dell'organizzazione, seleziona i candidati per nome con un'espressione regolare (`VIEW_RussiaCoTinUkraine_V\d+`, `View_AssessedRussianInfiltrationAreasinUkraine_V\d+`, …), per ogni tipo prende quello con la data di modifica più recente e lo interroga con `f=geojson&maxAllowableOffset=0.002&geometryPrecision=4&outSR=4326`.
4. Tempo massimo complessivo 12 s, ogni richiesta ha un timeout con `AbortController`. Se qualcosa va storto restituisce `null` e scrive un `console.warn`.

Risultato: `{aree, data_valutazione, data, fonte:'ISW/CTP', autore, link, attribuzione, licenza, origine}`. `data` e `autore` servono a `buildFront`, che costruisce il testo di credito da `fr.data` e `fr.fonte`.

**Per l'integrazione:** `buildFront` oggi disegna solo `ru`, `contesa`, `cleared` e `avanzata`. Le aree `controffensiva` sono circa 70.000 km² cumulati e vanno decise a parte: si possono non disegnare, oppure mapparle su `cleared`. Le `avanzata` hanno tutte la stessa `d` (il giorno della valutazione), quindi la scala di colori per età le mostra tutte come «nuove». Ai dati del 24/2/2022 non serve aggiungere la Crimea: il layer di controllo la include già.

## 2. GeoJSON e CORS (prove con curl, Origin `https://gabrielegiuliani04.github.io`)

- `items/<id>/data` e `items/<id>?f=json` su www.arcgis.com: `access-control-allow-origin: https://gabrielegiuliani04.github.io` (rimanda l'origine), compressione gzip, `cache-control: max-age=0, must-revalidate`.
- FeatureServer `…/query?…&f=geojson&maxAllowableOffset=0.01&geometryPrecision=3&outSR=4326`: `access-control-allow-origin: *`, cache 15-60 minuti. Dimensioni, compresso / non compresso: controllo 3,8 / 12 KB (0,5 s), infiltrazioni 12,6 / 70 KB, controffensive 10,8 / 50 KB, rivendicazioni 9,4 / 43 KB. Con una tolleranza di 0,01° il disegno è grossolano (circa 1 km). Il modulo usa 0,002°.
- Anche l'elenco dei servizi (`rest/services?f=json`) ha `access-control-allow-origin: *`.

## 5. Prova con Playwright

Ho usato Chromium headless su una pagina locale (`python3 -m http.server`, solo `<script src="isw-fronte.js">`).

- **Percorso principale (web map): 670 ms.** Data 2026-11-08. Aree: `ru` 7 poligoni, `avanzata@2026-11-08` 45, `contesa` 111, `controffensiva` 49. In tutto 7.814 vertici, 140 KB di JSON in memoria. Coordinate `[lon,lat]`, per esempio `[35.1644,51.101]`.
- **Ripiego (FeatureServer): 2,1 s.** Data 2026-09-29: il servizio di controllo è fermo a quella data, le controffensive sono del 6/11. Aree: `ru` 8, `contesa` 92, `controffensiva` 40; nessuna avanzata, perché i servizi sono vuoti. In tutto 6.003 vertici.

Entrambi i percorsi restano sotto i 5 s. Non ho fatto commit e non ho modificato `docs/index.html`.
