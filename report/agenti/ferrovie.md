# Agente FERROVIE - rapporto (2026-11-09)

Script: `raccolta/ferrovie/raccogli.py` (solo libreria standard, circa 4 secondi). Dato: `docs/data/ferrovie.json` (circa 760 KB, eseguito davvero il 2026-11-09).

## Fonti provate

| Fonte | Esito | Licenza |
|---|---|---|
| Natural Earth 10m railroads, GeoJSON su GitHub `nvkelso/natural-earth-vector` (raw.githubusercontent.com) | **funziona** (39,6 MB, 25.413 tratti) | pubblico dominio |
| Stesso file via cdn.jsdelivr.net | fallback nello script, non usato oggi | pubblico dominio |
| naciscdn.org (zip shapefile) | raggiungibile (HTTP 200), non usato: serve un lettore shapefile | pubblico dominio |
| OpenStreetMap via Overpass (overpass-api.de) | **non funziona** da questo ambiente (connessione chiusa dal proxy) | ODbL |
| Siti di notizie con WebFetch (kyivindependent.com, united24media.com, railwaynews.net) | **non raggiungibili** (dominio non consentito nella sessione); usati solo tramite ricerca web | - |
| File GIS dei corridoi TEN-T (DG MOVE) | non provati: tracciati ufficiali non inclusi | riuso Commissione UE (CC BY 4.0) |
| Corridoi e incidenti | schede curate nello script, ognuna con fonte, link e data | citazione |

## Cosa contiene `ferrovie.json`

Formato comune (`aggiornato`, `fonti`, `nota`, `elementi`, `errori`) più `collegamenti_ibrido`.

- **31 elementi `ferrovia-principale`**: linee Natural Earth con `category` 1 e 2, nel riquadro lon -11..135, lat 12..72 (Europa, Russia, Medio Oriente, Caucaso, Asia centrale, Cina). I tratti contigui sono uniti e semplificati con Douglas-Peucker (tolleranza circa 1 km, 3 decimali). In totale circa 404.600 km, 6.812 parti e 45.102 vertici. Gli elementi sono raggruppati per `macroarea` (un'etichetta per riquadri, non per confini), `binari` ed `elettrificazione`. Campi: `km`, `fonte`, `link`, `affidabilita`, `tracciato`, `g`.
- **9 elementi `corridoio-strategico`**: Cina-Europa, Middle Corridor/TITR, INSTC ovest, INSTC est, Ucraina-Polonia, rete RZD, Etihad/Hafeet Rail, Hejaz, TEN-T. Campi: `paesi`, `stato`, `nodi` (città con coordinate), `volumi[]` (voce, valore, unità, anno, trend, fonte, link, data_fonte, affidabilità). `g` è **schematico**: collega i nodi in linea retta e non segue il binario reale.
- **9 elementi `evento`** (incidenti, sabotaggi, attacchi): `lat`/`lon` stimati dal luogo indicato dalla fonte, con `precisione_km`. Sono nulli dove la fonte non indica un luogo.
- **`collegamenti_ibrido`**: punti di `ibrido.json` che citano la ferrovia nel testo, oppure sabotaggi a 2 km o meno da una linea.

## Fatti attuali (con numero, data e fonte)

1. **Cina-Europa**: 20.022 treni nel 2025 (+3,2%; erano 1.702 nel 2016). I treni di ritorno (10.124) hanno superato quelli in andata (9.898). I TEU sono circa 2,05 milioni (-1,3%). Fonti: [CGTN, 2026-06-19](https://news.cgtn.com/news/2026-06-19/China-Europe-freight-train-trips-up-10-8-fold-in-a-decade-1O6lmqO1Ka4/p.html) e [Railmarket](https://railmarket.com/news/freight-rail/51534). Nel primo trimestre 2026 i treni sono 5.460 (+29%) e i TEU 546.000 (+22%) ([Index1520](https://index1520.com/en/news/obemy-perevozok-po-marshrutu-kitay-evropa-vyrosli-na-chetvert-za-pervye-dva-mesyatsa-2026-goda/)).
2. **Middle Corridor (TITR)**: 4,7 milioni di tonnellate nel 2025 secondo l'Organizzazione degli Stati turchi, contro 4,484 Mt nel 2024 secondo il ministero dei Trasporti del Kazakhstan ([BESA, 2026](https://besacenter.org/azerbaijan-uses-the-middle-corridor-to-consolidate/)). Obiettivo per il 2030: 11,4 Mt. Le stime 2025 delle varie fonti vanno da 4,5 a 5,2 Mt e misurano cose diverse.
3. **INSTC**: 12,9 Mt di traffico ferroviario nel 2024 (RZD, [GRC](https://www.grc.net/single-commentary/302)). L'avvio dei lavori sul tratto mancante Rasht-Astara (162 km) è slittato al **2027**, con circa 3 anni di cantiere ([Interfax, 2026-10-15](https://interfax.com/newsroom/top-stories/119557/)). A febbraio era stato annunciato il 1 aprile 2026.
4. **Russia**: il carico sulla rete RZD è stato di circa 1,12 miliardi di tonnellate nel 2025. Per il 2026 è atteso un -1%, il quinto calo annuo consecutivo ([www1.ru, 2026-07-24](https://www1.ru/en/news/2026/07/24/424886-pogruzka-na-seti-rzd-padaet-piatyi-god-podriad-minus-1-v-2026-m.html)).
5. **Ucraina**: 1.534 attacchi russi alla rete ferroviaria nel 2026 al 24 agosto, già più dei 1.200 di tutto il 2025 ([Euromaidan Press, 2026-08-28](https://euromaidanpress.com/2026/08/28/russia-hunts-ukraine-locomotives-odesa-port-strikes/)). Oltre 200 locomotive colpite nel 2026 al 4 luglio, oltre 500 dal 2022 ([Euromaidan Press](https://euromaidanpress.com/2026/07/04/russia-has-hit-over-200-ukrainian-locomotives-this-year-its-targeting-logistics-that-keep-country-supplied/)).
6. **Confine UE**: a metà settembre 2026 un drone russo ha colpito la locomotiva del treno Kyiv-Varsavia a circa 2 km dalla Polonia, vicino a Yahodyn, senza feriti ([Boston Globe/AP, 2026-09-14](https://www.bostonglobe.com/2026/09/14/world/russian-strike-train-station-near-poland-seen-warning-ukraines-allies/)).
7. **Polonia**: il 16 novembre 2025 un'esplosione ha danneggiato la linea Varsavia-Lublino presso Mika. Il premier l'ha definita un sabotaggio "senza precedenti". Secondo Varsavia gli esecutori sono due ucraini al servizio dei servizi russi, transitati per la Bielorussia ([Notes from Poland, 2025-11-17](https://notesfrompoland.com/2025/11/17/poland-confirms-act-of-sabotage-behind-explosion-that-damaged-rail-line/)).
8. **Germania**: circa 2.200 atti contro la rete DB (furti, incendi, vandalismo) nel primo semestre 2026, +7% sul 2025, secondo un rapporto interno riportato da Bild ([Ground News](https://ground.news/article/german-rail-network-hit-by-2-200-criminal-acts-this-year-bild-reports)). In estate 2026 l'incendio di cavidotti presso Leverkusen ha chiuso la Colonia-Düsseldorf per circa 36 ore. Lo ha rivendicato "Kommando Angry Birds", di estrema sinistra, e l'autenticità della rivendicazione è in verifica ([blue News](https://www.bluewin.ch/en/news/letter-claiming-responsibility-after-fire-suspected-sabotage-on-railroad-line-li.3525182)). La data esatta va verificata.
9. **Russia occupata**: a marzo e aprile 2026 droni ucraini hanno colpito almeno 10 treni merci e cisterne, soprattutto nell'oblast di Luhansk ([ISW](https://x.com/TheStudyofWar/status/2059332424065044704)). Il deragliamento di 39 carri vicino a Ekaterinburg del 2026-10-26 **non** è attribuito ad attacchi: la causa non è stata comunicata ([RBC-Ukraine](https://newsukraine.rbc.ua/news/freight-train-derails-in-russia-s-urals-fuel-1793015713.html)).
10. **Golfo**: il servizio passeggeri di Etihad Rail era programmato dal 30 giugno 2026 e la rete dal 30 settembre 2026. L'avvio effettivo non è stato verificato. Hafeet Rail (EAU-Oman, verso Sohar) era al 30% a gennaio 2026 ([Etihad Rail](https://corporate.etihadrail.ae/en/newsroom/press/etihad-rail-board-of-directors-reviews-developments-of-the-national-rail-network-and-passenger-train-project)).

Valutazione, non fatto: il fianco est della NATO (Polonia, Germania, Baltici) è il punto in cui sabotaggio ibrido e logistica militare verso l'Ucraina si sovrappongono. Le linee Varsavia-Lublino-Hrubieszów e Lublino-Dorohusk/Yahodyn sono i colli di bottiglia da sorvegliare.

## Collegamenti con gli altri livelli

- **Attacchi ibridi (`ibrido.json`)**: due collegamenti calcolati in automatico.
  - IB-20261107-11 (bielorussi arrestati per incendi preparati vicino a una ferrovia nella zona di Norimberga): il testo cita la ferrovia, ed è anche in `ferrovie.json` come FR-INC-09.
  - IB-20261107-10 (incendio a Brașov accanto a Carfil/Romarm): è a 1,6 km da una linea, ma il collegamento è solo geometrico e va verificato.
  - Il sabotaggio della Varsavia-Lublino (novembre 2025) **non** è nel livello ibrido: è più vecchio della finestra di raccolta. Si propone di aggiungerlo lì.
- **Stretti e rotte**: Cina-Europa e Middle Corridor sono l'alternativa terrestre a Suez e al Mar Rosso. La crescita del +29% nel primo trimestre 2026 va letta insieme ai livelli rotte e stretti (valutazione: un legame causale non è dimostrato). Anche INSTC e Hafeet Rail (verso Sohar, fuori dallo Stretto di Hormuz) si collegano agli stretti.
- **Fronte (`fronte.json`)**: gli attacchi alle ferrovie ucraine e russe sono logistica del fronte.
- **Condotte**: molti corridoi corrono paralleli agli oleodotti BTC e ai gasdotti caucasici, quindi c'è un rischio comune nel nodo georgiano.
- **Italia**: quattro corridoi TEN-T attraversano l'Italia. Il traffico Cina-Europa arriva in Italia solo in piccola parte, ma su questo il dato manca.

## Proposta per la mappa

- Rete in grigio sottile (con spessore leggermente maggiore per il binario multiplo), visibile solo da zoom medio.
- Corridoi in colore acceso e tratteggio, perché sono schematici. Al clic, una scheda con volumi e trend.
- Incidenti come simboli con un cerchio di incertezza pari a `precisione_km`, colorati per categoria (sabotaggio, attacco militare, causa ignota).

## Limiti

- Natural Earth è generalizzata e ferma a circa il 2017. Mancano linee nuove come Baku-Tbilisi-Kars e Etihad Rail, ed è incompleta in Iran e nel Golfo. Le categorie 1 e 2 non equivalgono a "rilevanza strategica".
- La `macroarea` è assegnata per riquadri, quindi alcune linee di confine finiscono nel gruppo vicino.
- Corridoi e incidenti sono schede manuali nello script: non si aggiornano da soli e vanno riviste quando escono nuovi dati.
- Diverse cifre vengono da fonti ucraine o di parte (affidabilità media) e alcune date sono approssimate al mese. Non c'è un volume INSTC 2025 completo né volumi per il ramo orientale dell'INSTC e per l'Hejaz.
- Overpass e alcuni siti di notizie non sono raggiungibili da questo ambiente.
