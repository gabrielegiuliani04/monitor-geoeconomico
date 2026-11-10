# Agente ATTACCHI DA ANALISTI OSINT: Clément Molin e AMK Mapping (Telegram)

Rapporto del 10 novembre 2026. Script: `raccolta/ucraina/telegram_analisti.py`, solo libreria standard (`html.parser`, `urllib`, `csv`, `gzip`, `zipfile`). L'ho eseguito davvero. Ha scritto `docs/data/attacchi-analisti.json`: **4.093 attacchi, 1,95 MB**.

## Cosa fa lo script

| Passo | Comando | Note |
|---|---|---|
| 1. Scarica | `python3 raccolta/ucraina/telegram_analisti.py scarica` | Legge le pagine pubbliche `t.me/s/<canale>` all'indietro con `?before=<id>`, con una pausa di 1,5–2 s tra le pagine. Per ogni post salva canale, id, data UTC, link `https://t.me/<canale>/<id>`, testo e la presenza di immagini o video. La cache è in `raccolta/ucraina/cache_telegram/` (39 MB, **esclusa da git** con una riga aggiunta a `.gitignore`). Gli aggiornamenti sono incrementali: lo script si ferma al primo post già in cache, quindi un'esecuzione quotidiana legge 1–2 pagine. Una pagina vuota viene riprovata 3 volte prima di concludere che la cronologia è finita. |
| 2. Gazetteer | `… gazetteer` | `raccolta/ucraina/gazetteer.json` (6.957 voci) costruito da **GeoNames** (CC BY 4.0: `UA.zip`, `RU.zip`, `admin1CodesASCII.txt`). Contiene i luoghi abitati ucraini da 1.000 abitanti in su; quelli russi da 15.000, o da 3.000 a ovest degli Urali, più alcuni piccoli porti energetici come Ust-Luga e Taman; le 110 regioni (ADM1) di UA e RU; le città di `docs/data/labels.json`. Ci sono poi alias scritti a mano per le grafie degli analisti (Kyiv/Kiev, Zaporizhzhia, Riazan, Novokuibyshevsk…) e un elenco di 58 impianti (raffinerie, porti petroliferi, basi aeree) di cui uso le coordinate OSM già presenti in `docs/data/ucraina-storico.json`. |
| 3. Estrai | `… estrai` | Applica le regole, gli incroci e la verifica FIRMS, poi scrive il JSON. |
| Controllo | `… campione` | Stampa 40 attacchi estratti a caso (seme fisso) con il testo, per il controllo manuale. |

Senza argomenti lo script esegue scarica, gazetteer (solo se manca) ed estrai. Legge `FIRMS_MAP_KEY` se c'è; se manca dà un avviso e non fallisce.

## Post letti

| Canale (nome esatto verificato) | Post letti | Periodo | Note |
|---|---|---|---|
| `t.me/s/clement_molin` | 1.704 (919 con testo) | dall'1/7/2023 al 9/11/2026 | Fino al 2025 il canale è quasi vuoto: 18 post nel 2023, in francese, sulle rivolte in Francia, e 56 nel 2025. **È attivo davvero solo dal maggio 2026** (oltre 1.600 post), soprattutto come copia dei suoi post su X: analisi del fronte, mappe e bilanci, con pochi singoli attacchi. |
| `t.me/s/AMK_Mapping` | 35.304 (35.234 con testo; 12.290 con immagini, 4.582 con video) | dal 12/6/2024 al 10/11/2026 | Cronologia completa dal post n. 1, senza buchi oltre i 60 id. Contiene molte notizie brevi del tipo «Explosions in X», tracciamento dei missili in volo, conseguenze degli attacchi e verifiche NASA FIRMS. Una parte riguarda il Medio Oriente, il Sudan e altri fronti: quei post vengono scartati perché il luogo non è in UA/RU. |

Lo scaricamento completo ha richiesto circa 2.000 pagine. Per finire in tempo ho usato una sola volta due processi paralleli su intervalli di id separati, ognuno con la stessa pausa di 1,5–2 s, e poi ho unito i risultati. Lo script in sé lavora in sequenza.

## Regole di estrazione (trasparenti, nel codice)

Un post diventa un attacco se supera tutti questi filtri:
1. **Parola d'attacco**, in inglese o francese: strike, struck, hit, attack, drone, missile, Shahed, Geran, Iskander, Kh-101, Kalibr, KAB, refinery, oil depot, substation, explosion, fire, frappe, raffinerie, dépôt, incendie…
2. **Impatto avvenuto**: struck, impacted, damaged, «fire broke out», «explosions heard», aftermath, «strike on…», frappé, touché… Una semplice menzione non basta.
3. **Esclusioni**:
   - allerte e tracciamento di lanci (threat, flying towards, air raid alerts, «may carry out»);
   - monitoraggio dei bombardieri strategici;
   - post sul fronte terrestre (advance, assault, treeline, brigade, km²…), a meno che non citino un'infrastruttura;
   - sintesi e statistiche (almeno 3 mesi citati o almeno 25 numeri);
   - post che nominano solo luoghi di lancio («launched from near …»).
4. **Luogo**, in quest'ordine:
   - un impianto noto (coordinate OSM, 2–10 km);
   - coordinate scritte nel post (AMK le pubblica spesso: precisione 1 km);
   - una città del gazetteer (10 km). Si preferiscono le città precedute da in/on/at/near; un omonimo si risolve con l'oblast scritta subito dopo («Mykhailivka, Dnipropetrovsk Oblast»);
   - altrimenti la regione (punto GeoNames dell'ADM1, 80 km).
5. **Direzione**:
   - «Russian Geran/KAB/missile…» senza attore ucraino esplicito vale **RU>UA**, anche quando colpisce forze ucraine in Russia (saliente di Kursk);
   - «Ukrainian drones/SBU/GUR…» su un luogo in Russia o nei territori occupati vale **UA>RU**;
   - negli altri casi decide il paese del luogo. Sono considerati occupati Crimea, Sebastopoli, l'oblast di Luhansk e un elenco di città occupate di Donetsk, Zaporizhzhia e Kherson.
6. **Categoria**: la prima che corrisponde, in quest'ordine: raffineria/deposito, energia, porto, ferrovia, aeroporto, industria, civile (edifici civili espliciti), militare, civile (morti o feriti generici). Se nessuna corrisponde, `altro`. Quasi sempre `altro` è «Explosions in X».
7. **Mezzi**: Shahed/Geran, Iskander, Kh-101/555, Kalibr, Kinzhal, Kh-22/32, Kh-59/69, S-300/400, KAB, missili, droni, artiglieria/MLRS, Storm Shadow/SCALP/ATACMS.
8. **Deduplica**: post dello stesso canale con stessa data, luogo, categoria e direzione diventano un solo attacco. Gli altri link finiscono in `altri_post`.

## Cosa contiene `docs/data/attacchi-analisti.json`

Il formato è quello di AGENTI.md: `aggiornato`, `fonti`, `nota`, `elementi`, `errori`, più `legenda`, `canali`, `categorie` e `riepilogo`. Ogni elemento ha questi campi:
- `id` (`amk-<n>` / `cm-<n>`), `data` (UTC del post), `direzione` (`RU>UA` / `UA>RU`);
- `lat`, `lon`, `precisione_km`, `nome`, `oblast`, `paese`;
- `categoria`, `mezzi`, `fonte`, `link`;
- `estratto`: al massimo 160 caratteri;
- `affidabilita`: `media`, oppure `alta` se corroborato;
- quando servono: `corroborato_da`, `firms` (e `firms_focolaio`), `territorio_occupato`, `luoghi_citati`, `immagini`, `video`, `altri_post`.

**Attacchi estratti: 4.093.** Di questi, 3.996 vengono da AMK Mapping e 97 da Clément Molin. In tutto sono stati accettati 4.951 post, prima della deduplica.

| Anno | RU>UA | UA>RU | Totale |
|---|---|---|---|
| 2023 | 1 | 1 | 2 (Molin, irrilevanti) |
| 2024 (da giugno) | 291 | 75 | 366 |
| 2025 | 1.179 | 248 | 1.427 |
| 2026 (al 10/11) | 1.810 | 488 | 2.298 |

| Categoria | Totale | di cui RU>UA |
|---|---|---|
| altro (esplosioni senza bersaglio indicato) | 1.721 | 1.565 |
| energia | 508 | 408 |
| industria | 438 | 331 |
| civile | 385 | 344 |
| raffineria/deposito | 325 | 117 |
| militare | 199 | 123 |
| aeroporto | 196 | 124 |
| porto | 171 | 128 |
| ferrovia | 150 | 141 |

**Corroborazione.** 451 attacchi hanno affidabilità `alta`: lo stesso evento, a ±1 giorno ed entro 30 km, compare in `attacchi-russi.json` (279 abbinamenti), in `ucraina-storico.json` (102) o nell'altro canale (139). Gli altri 3.642 restano `media`: sono segnalati da un analista OSINT e non corroborati.

**Precisione del luogo.** 486 punti hanno le coordinate scritte nel post (1 km) e 121 le coordinate dell'impianto (2–3 km). Gli altri sono 3.076 centri abitati (10 km), 406 regioni (80 km) e 4 impianti a 30 km.

## Verifica satellitare NASA FIRMS

La verifica riguarda gli attacchi `energia` e `raffineria/deposito` con un luogo preciso almeno a 10 km. Un attacco ha `firms: true` se c'è un focolaio VIIRS/MODIS entro 5 km, dal giorno prima a 2 giorni dopo.

| Fonte FIRMS | Esito |
|---|---|
| CSV pubblici globali degli ultimi 7 giorni (VIIRS NOAA-20, NOAA-21, MODIS; SNPP oggi vuoto) | **funziona**, senza chiave |
| Archivi annuali per paese (`/data/country/{viirs-snpp,modis}/<anno>/…_Ukraine.csv`, `…_Russian_Federation.csv`) | **funziona per 2022–2025**, senza chiave. Ne tengo in cache solo le righe del riquadro tra 22–62°E e 43–62°N. **Il 2026 non esiste ancora (404).** |
| API area (`/api/area/csv/<MAP_KEY>/…`) | **serve una chiave** (`FIRMS_MAP_KEY`, gratuita), oggi assente. Lo script la usa se la trova, per finestre di 10 giorni attorno agli attacchi. |

**Risultato:**
- 289 attacchi energetici verificabili; **56 con un focolaio** (`firms: true`) e 233 senza;
- altri 463 attacchi del 2026 (gennaio–inizio novembre) hanno `firms: null`, cioè nessun dato FIRMS disponibile senza chiave;
- tra i positivi recenti c'è Kirishi il 9/11/2026, segnalata da entrambi i canali (focolaio VIIRS NOAA-20 a meno di 5 km).

*Valutazione:* un `false` non smentisce l'attacco. Molti colpi su sottostazioni non producono incendi visibili, e nuvole o orari dei passaggi del satellite fanno perdere eventi. **Attivando `FIRMS_MAP_KEY` su GitHub Actions si copre anche il 2026.**

## Precisione delle regole (controllo manuale)

Ho controllato a mano 40 attacchi estratti a caso (`… campione`), leggendo il testo completo. Un caso è giusto se il post descrive davvero un attacco avvenuto, con la direzione giusta e il luogo entro circa 30 km.

- **Versione finale delle regole: 36 giusti su 40 (90%).** Gli errori:
  - un post politico (Merz che condanna l'attacco su Sumy);
  - un bilancio della distruzione di Bilozerske, che non è un singolo attacco;
  - un'esplosione attribuita a Severomorsk mentre il video era della base di Olenja (circa 80 km);
  - un attacco ucraino a Stavky (Kherson occupata) classificato RU>UA, perché il villaggio non è nell'elenco delle zone occupate.
- La **categoria** è discutibile in circa 4 dei 36 casi giusti, per esempio un dormitorio a Starobilsk classificato «militare» o un centro commerciale classificato «energia» perché il post cita blackout. Va trattata come indicativa.
- Un primo campione, preso con regole meno strette, aveva dato 33 giusti su 40 (82,5%). Gli errori erano allerte di raid aerei, monitoraggio dei bombardieri, una frase dove «Smotrich» veniva letto come la località Smotrych e un'analisi strategica. Dopo quel controllo ho aggiunto i filtri corrispondenti.

## Limiti

- **Copertura temporale.** AMK parte dal 12/6/2024 e Molin di fatto dal maggio 2026. Per il 2022–metà 2024 restano `attacchi-russi.json` e `ucraina-storico.json`.
- **Non sono «tutti» gli attacchi.** Sono gli attacchi che i due analisti hanno scritto su Telegram e che le regole riconoscono. I post fatti solo di immagini (circa 70 su Molin) o i lunghi elenchi di AMK («explosions in/near the following locations: …» con decine di località) danno un solo punto: il primo luogo pertinente, con il numero dei luoghi in `luoghi_citati`.
- **Un elemento è un post, non un evento fisico.** La stessa ondata può generare più elementi se tocca luoghi o categorie diversi, e AMK pubblica spesso post successivi sullo stesso attacco.
- **Ritardo del post.** La data è quella del post in UTC: un attacco notturno può comparire il giorno dopo. Per questo gli incroci usano ±1 giorno.
- **Luoghi.** Omonimi non risolti, quartieri non presenti nel gazetteer (si usa la città), luoghi citati come contesto. La precisione di 10 o 80 km va mostrata sulla mappa.
- **Direzione.** Le regole funzionano bene sui testi di AMK, che scrive in modo regolare, meno sulle analisi discorsive di Molin. Gli attacchi ucraini su villaggi occupati fuori dall'elenco possono finire come RU>UA.
- **Affidabilità.** Gli analisti riportano spesso rivendicazioni di parte (MoD russo, canali ucraini). L'estratto lo mostra, ma il campo `affidabilita` non distingue questi casi.

## Diritti e uso dei contenuti

I post sono opere dei loro autori e Telegram non indica una licenza. Il file riporta **fatti** (data, luogo, tipo di bersaglio, mezzi) con **citazione dell'autore e link al post originale**. Del testo si tiene solo un **estratto di massimo 160 caratteri**, utile a capire di cosa si parla. Testi completi, immagini e video non vengono ripubblicati: i testi restano solo nella cache locale, fuori da git, e servono a rigenerare l'estrazione. Chi vuole il contenuto va al post. Le coordinate GeoNames sono CC BY 4.0 (vanno citate); quelle degli impianti vengono da OSM (ODbL) attraverso `ucraina-storico.json`. I dati FIRMS sono della NASA, a uso libero con citazione.

## Proposta per la mappa

Un livello «Attacchi (analisti OSINT)» collegato al cursore del periodo:
- colore per `direzione`, con RU>UA e UA>RU ben distinti;
- icona per `categoria`;
- opacità per `affidabilita`, un anello per `firms: true`;
- raggio di incertezza da `precisione_km`;
- nel popup: estratto, link al post e `corroborato_da`.

I punti `altro` (esplosioni) vanno tenuti nascosti di default, perché sono il 42% del totale. Con `affidabilita: "alta"` si collegano agli eventi curati di `attacchi-russi.json` e `ucraina-storico.json`; i punti su raffinerie e porti petroliferi russi si collegano ai livelli energia e stretti (Novorossiysk, Ust-Luga, Primorsk, Tuapse).
