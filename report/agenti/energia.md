# Agente ENERGIA: terminali GNL, gas in Italia, condotte strategiche

Rapporto del 9 novembre 2026. Script: `raccolta/energia/raccogli.py`, solo libreria standard. L'ho eseguito davvero e gira in circa 30 secondi.

## File prodotti

| File | Dimensione | Contenuto |
|---|---|---|
| `docs/data/terminali-gnl.json` | 639 KB | 840 terminali GNL del mondo, un punto per progetto GEM. Le fasi e gli ampliamenti sono in `unita`. Operativi: 256, cioè 197 di rigassificazione e 59 di liquefazione. Ogni punto ha tipo (`import`/`export`), stato, capacità in Mt/a per stato, proprietario e link alla scheda gem.wiki. |
| `docs/data/gas-italia.json` | 163 KB | 11 punti di ingresso del gas in Italia: 6 gasdotti (Mazara, Gela, Melendugno, Passo Gries, Tarvisio, Gorizia) e 5 terminali GNL (Panigaglia, OLT Livorno, Adriatic LNG, Piombino, Ravenna). Per ognuno c'è il flusso fisico giornaliero degli ultimi 12 mesi, dal 2025-11-08 al 2026-11-08, in GWh/giorno, con entrate e uscite. Contiene anche: `serie_nazionali` (produzione nazionale, stoccaggi Stogit, TurkStream verso l'UE a Strandzha 2), `ingressi_totali` (serie giornaliera) e `quote_12_mesi`. |

Il formato è quello di AGENTI.md: `aggiornato`, `fonti`, `nota`, `elementi`, `errori`. I punti hanno lat/lon, nome, paese, categoria, stato, fonte, link, data_fonte, affidabilita e note. Le serie sono nella forma `[["AAAA-MM-GG", valore], ...]`.

Categorie per la mappa:
- `gnl-rigassificazione` e `gnl-liquefazione` in terminali-gnl.json;
- `gas-ingresso-gasdotto` e `gas-ingresso-gnl` in gas-italia.json.

Note sui dati:
- **Coordinate dei punti italiani.** Per i gasdotti sono l'estremo, lato Italia, del tracciato GEM (per esempio la fine del segmento Tunisia–Italia del TransMed). Per i rigassificatori sono quelle del terminale GEM. Se GEM non le fornisce, il codice usa coordinate di riserva prese dallo stesso file.
- **Melendugno.** La coordinata è il punto più occidentale del TAP: il terminale di ricezione, nell'entroterra, non l'approdo sulla costa.

## Fonti provate

| Fonte | Esito | Licenza | Note |
|---|---|---|---|
| GEM, Global Gas Infrastructure Tracker + LNG Terminals: file della mappa pubblica `publicgemdata.nyc3.cdn.digitaloceanspaces.com/Current_maps/ggit-lng/` | **Funziona** | CC BY 4.0 per i dati GEM. Le schede gem.wiki sono CC BY-NC-SA. | Lo script elenca il bucket (S3 pubblico) e prende il `.geojson` più recente, quindi non dipende da un nome di file fisso. File attuale: `ggit-lng_map_2026-10.geojson`, 195 MB, caricato il 23/10/2026; si scarica in circa 7 secondi. Contiene anche i gasdotti. Il link in `maps/trackers/ggit/config.js` su GitHub punta a un file non più esistente (404). Il repo `goit-ggit-data-ops` contiene solo le linee. |
| ENTSOG Transparency Platform, API `operationaldata` (Physical Flow, giornaliero) | **Funziona**, senza chiave | Dati pubblici, riuso con citazione | Dati di Snam Rete Gas (`IT-TSO-0001`). Una chiamata per punto e direzione, meno di 2 secondi ciascuna. Per Sardinia LNG (`LNG-00059`) e IP Greece-Italy (`ITP-00531`) non ci sono dati. |
| Snam, pagine "dati operativi" | **Non funziona** in modo stabile | — | Il vecchio URL rimanda a "informazioni commerciali" e le pagine interne danno 404. ENTSOG ha gli stessi dati di Snam in forma machine-readable, quindi Snam non serve. |
| Wikidata, coordinate dei comuni | **Non usato** | CC0 | Ha risposto con un limite di richieste (rate limit). Ho preso le coordinate dai tracciati GEM. |
| spglobal.com, hellenicshippingnews.com | **Bloccati** dalla rete di questa sessione | — | Li cito solo tramite i risultati di ricerca. |

## Fatti sul gas in Italia (dati ENTSOG nel file, calcolati da me)

1. **Mazara del Vallo (gas algerino via TransMed) è il primo ingresso.** Negli ultimi 12 mesi (8/11/2025–8/11/2026) ha portato 220,5 TWh, circa 20,9 miliardi di Smc: il 34% degli ingressi da gasdotti e GNL. L'8/11/2026 il flusso era di 630 GWh, circa 59,6 milioni di Smc. A settembre 2026 c'è stato un calo a 11,3 TWh nel mese, contro 16,9 ad agosto e 20,2 a ottobre; la causa non è documentata nel dato.
2. **TAP (Melendugno) è il secondo ingresso:** 106,6 TWh in 12 mesi (16,5%). Nell'ottobre 2026 ha toccato il massimo mensile del periodo, 9,8 TWh.
3. **Il GNL pesa per circa un terzo.** Adriatic LNG ha portato 91,3 TWh (14,1%), Piombino 45,0, OLT Livorno 43,7, Ravenna 22,5 e Panigaglia 9,8.
   - OLT Livorno è quasi fermo da ottobre: 0,8 TWh in ottobre contro circa 4 al mese prima. Il dato dell'8/11 indica una ripresa (105 GWh).
   - Anche Piombino è in calo: 2,1 TWh in ottobre contro circa 4.
4. **Il gas russo residuo arriva poco e in modo irregolare.** Da Tarvisio sono entrati 17,5 TWh in 12 mesi, con lunghi periodi a zero (marzo e maggio 2026); dalla stessa frontiera sono usciti verso l'Austria 10,2 TWh. Passo Gries (gas dal Nord Europa) ha portato 84,3 TWh.
5. **La Libia è marginale:** Greenstream (Gela) ha portato 5,1 TWh in 12 mesi, lo 0,8%.
6. **Ingressi totali e stoccaggi.** Gli ingressi totali da gasdotti e GNL sono stati di 52,6 TWh a ottobre 2026 e di 60,0 TWh a gennaio 2026. Gli stoccaggi Stogit sono passati all'erogazione a inizio novembre: 431 GWh erogati l'8/11.
7. **TurkStream verso l'UE (Strandzha 2, Bulgaria) non è stato interrotto in modo duraturo dalla guerra.** Il dato ENTSOG nel file dà una media di 539 GWh/giorno a ottobre 2026 e 570 a novembre. Il minimo è di giugno 2026, 374 GWh/giorno.

## Fatti sui terminali GNL (GEM, file di ottobre 2026)

8. **Capacità di liquefazione operativa nel mondo: 570 Mt/a.**
   - Gli Stati Uniti ne hanno 150, l'Australia 82, il Qatar 77, la Russia 42.
   - Dentro il Golfo, quindi dietro Hormuz, ci sono 82,9 Mt/a, il 14,5% del totale: QatarEnergy LNG Nord 40,8 e Sud 36,3, più Das Island (Emirati) 5,8. Ras Laffan non ha uscite alternative a Hormuz.
   - In costruzione nel mondo ci sono 267 Mt/a di nuova capacità di liquefazione.
9. **L'Italia ha 21,8 Mt/a di rigassificazione operativa** secondo GEM: Adriatic LNG 6,99, Piombino, Ravenna e OLT 3,67 ciascuno, Panigaglia 2,57, più piccoli depositi (Ravenna e Oristano HIGAS). Sono in progetto Porto Torres, Oristano, Taranto e Gioia Tauro.

## Condotte strategiche: stato attuale

Le notizie qui sotto vengono dai risultati di ricerca web. Le date sono quelle degli articoli. Dove le fonti divergono lo segnalo.

- **Druzhba (petrolio russo verso Ungheria e Slovacchia).** È stata ferma dal 27/1/2026. Il gestore ucraino ha chiuso la forza maggiore il 21/4/2026 ([oenergetice.cz](https://oenergetice.cz/en/oil/mol-resumes-receiving-oil-from-druzhba-after-three-months-with-flows-also-reaching-slovakia); [Enerdata](https://www.enerdata.net/publications/daily-energy-news/russian-oil-transit-resumes-druzhba-pipeline-hungary-lifts-eur90bn-loan-veto.html)). A maggio i flussi erano tornati normali ([bne IntelliNews](https://www.intellinews.com/russian-oil-flows-through-druzhba-return-to-normal-as-hungary-and-slovakia-resume-russian-oil-and-gas-imports-446680/)). Il Moscow Times dell'1/8/2026 riporta un nuovo stop dopo danni sul territorio ucraino ([link](https://www.themoscowtimes.com/2026/08/01/oil-supplies-to-hungary-and-slovakia-halted-after-damage-to-druzhba-pipeline)). Lo stato a novembre non è confermato.
- **TurkStream.** Gazprom e Mosca hanno denunciato attacchi con droni alla stazione di compressione di Russkaya, vicino ad Anapa, a gennaio, marzo, aprile e maggio 2026, dicendo che l'esercizio era normale ([Moscow Times 11/3](https://www.themoscowtimes.com/2026/03/11/gazprom-says-ukrainian-drones-attacked-turkstream-blue-stream-pipeline-facilities-a92204); [Kyiv Independent](https://kyivindependent.com/russias-gazprom-claims-ukrainian-strikes-on-turkstream-pipeline/)). I dati ENTSOG confermano che il gas arriva in Bulgaria (fatto 7).
- **Nord Stream.** È fermo. Il 13/1/2026 Nord Stream 2 AG ha fatto ricorso contro le sanzioni UE e contro il regolamento UE 2026/261, che elimina gradualmente il gas russo ([Correctiv](https://correctiv.org/aktuelles/russland/2026/01/13/nord-stream-2-pipeline-betreiber-klagt-gegen-eu-sanktionen/); [OE Digital](https://www.oedigital.com/amp/news/540583-nord-stream-2-challenges-eu-s-russian-gas-phase-out-in-court)). Il 29/10/2026 il Moscow Times scrive che l'UE è contraria al riavvio anche dopo la guerra ([link](https://ru.themoscowtimes.com/2026/10/29/es-vistupaet-protiv-perezapuska-severnogo-potoka-posle-okonchaniya-voini-dazhe-nesmotrya-na-popitki-rossii-i-ssha-reanimirovat-proekt-a209980)).
- **CPC (Tengiz–Novorossiysk, circa l'1,5% del petrolio mondiale).**
  - 6/4/2026: un attacco di droni danneggia un punto di ormeggio e incendia quattro serbatoi ([Arab News](https://www.arabnews.com/node/2638975)).
  - 19–20/7/2026: i carichi sono sospesi dopo droni sulle petroliere.
  - Fine luglio 2026: viene colpita la stazione di pompaggio Kropotkinskaya e il pompaggio scende ([Moscow Times 27/7](https://www.themoscowtimes.com/2026/07/27/ukrainian-drones-hit-major-pipeline-in-southern-russia-disrupting-oil-supplies)).
  - Non ho trovato aggiornamenti dopo agosto.
- **Kirkuk–Ceyhan.**
  - 18/3/2026: riprendono le esportazioni dopo l'accordo Baghdad–Erbil ([The Star](https://www.thestar.com.my/news/world/2026/03/18/iraqi-government-kurdish-authorities-reach-deal-to-resume-oil-exports-to-turkey039s-ceyhan-port)).
  - 31/7: accordo Iraq–Turchia di un anno, con una capacità di circa 750.000 barili al giorno.
  - Fine ottobre: Baghdad sposta greggio di Bassora verso nord a causa di Hormuz. Secondo Shafaq e OilPrice le esportazioni verso Ceyhan passano da 350.000 a circa 500.000 barili al giorno, con un obiettivo di 600.000 ([Iraqi News 31/10](https://iraqinews.com/iraq/iraq-to-raise-oil-exports-via-turkey-to-600000-barrels-per-day); [Shafaq](https://shafaq.com/en/Economy/Iraq-s-oil-exports-via-Turkiye-reach-500-000-bpd)). Sono cifre da fonti anonime.
- **East–West / Petroline (da Abqaiq a Yanbu, capacità nominale 7 milioni di barili al giorno).**
  - Marzo 2026: dopo la chiusura di Hormuz arriva a pieno regime ([Fortune 28/3](https://fortune.com/2026/03/28/saudi-arabia-east-west-oil-pipeline-strait-hormuz-bypass-7-million-barrels-yanbu-red-sea)). Wood Mackenzie stima un picco di circa 4,07 milioni di barili al giorno di greggio esportato a marzo e un calo del 41% a giugno ([World Pipelines 24/7](https://www.worldpipelines.com/special-reports/24072026/saudi-arabias-red-sea-crude-bypass-peaks-in-march-and-declines-41-by-june-wood-mackenzie-data-shows/)).
  - 11–13/9: viene fermato dopo attacchi con droni partiti dall'Iraq ([Al-Monitor](https://al-monitor.com/originals/2026/09/saudi-running-out-oil-export-options-iran-allies-choke-routes)).
  - Circa 22/9: riparte a basso regime ([The National](https://thenationalnews.com/business/energy/2026/09/22/saudi-arabia-restarts-east-west-pipeline-for-crude-exports/); [OilPrice](https://oilprice.com/Energy/Energy-General/Aramco-Restores-East-West-Pipeline-as-War-Risk-Closes-In-on-Yanbu.html)).
  - 6/10: Reuters, ripreso da altre testate, riferisce flussi non interrotti.
  - Rischio aggiuntivo: dal 20/7 gli Houthi dichiarano un blocco delle navi saudite.
- **Habshan–Fujairah (ADCOP, fino a circa 1,8 milioni di barili al giorno).**
  - 14/3/2026: droni su Fujairah, carichi sospesi.
  - 18/3 e 7/4: attacchi a Habshan.
  - Circa 30/3: incendi su due stazioni di pompaggio visti da satellite.
  - 4/5: nuovo attacco a Fujairah ([Al Jazeera 5/5](https://www.aljazeera.com/news/2026/5/5/whats-the-significance-of-uaes-fujairah-hit-on-monday); [bne](https://www.intellinews.com/fires-reported-at-pumping-stations-along-uae-s-adcop-pipeline-434587/)).
  - Il volume trasportato oggi non è pubblico.
- **Goreh–Jask (Iran, 1 milione di barili al giorno di progetto, circa 350.000 effettivi).** A marzo ha gestito circa il 4,4% dell'export iraniano; Kharg ne gestiva circa il 90% ([bne](https://www.intellinews.com/iran-ramps-up-jask-exports-but-still-heavily-reliant-on-kharg-island-435645/)). Ad agosto l'Iran usa di più Jask contro il blocco navale USA ([S&P Global 5/8](https://www.spglobal.com/energy/en/news-research/latest-news/crude-oil/080526-iran-turns-to-crude-exports-via-jask-terminal-amid-hormuz-disruptions)). In GEM il terminale GNL iraniano risulta "in costruzione".
- **EastMed (gasdotto Israele–Cipro–Grecia).** Nessuna decisione di investimento. Il formato "3+1" (USA, Grecia, Cipro, Israele) lo ha rimesso in agenda ([iefimerida](https://www.iefimerida.gr/english/us-greece-cyprus-israel-renew-energy-pact-eastmed-pipeline-returns-agenda)). Le alternative concrete sono il GNL egiziano, un gasdotto Israele–Cipro (Energean) e il cavo elettrico GSI.

## Collegamenti con stretti e prezzi

- **Hormuz e GNL.**
  - QatarEnergy ha dichiarato forza maggiore dopo gli attacchi di marzo a Ras Laffan e l'ha prorogata fino a novembre ([Euronews 31/8](https://www.euronews.com/2026/08/31/qatarenergy-extends-lng-cancellations-into-november-as-hormuz-disruption-drags-on); [The National 28/9](https://thenationalnews.com/business/energy/2026/09/28/qatar-extends-lng-force-majeure-as-hormuz-disruption-threatens-winter-supply)).
  - Due treni di liquefazione, circa 12,8 Mt/a, sono fuori servizio; per altri due la riparazione può richiedere 3–5 anni ([Cyprus Mail 12/10](https://cyprus-mail.com/2026/10/12/qatar-lng-exports-remain-severely-disrupted-despite-recovery-in-gulf-oil-shipments)).
  - A ottobre i transiti di metaniere a Hormuz sono risaliti a 32 (S&P Global, 2/11).
  - In mappa: i 3 terminali dietro Hormuz valgono il 14,5% della liquefazione mondiale (fatto 8).
- **Hormuz e petrolio.** Le vie di aggiramento sono East–West (verso il Mar Rosso), Habshan–Fujairah (Golfo di Oman), Goreh–Jask (Golfo di Oman) e Kirkuk–Ceyhan (Mediterraneo). Tutte sono state colpite o limitate nel 2026.
- **Bab el-Mandeb.**
  - È il collo di bottiglia del greggio saudita da Yanbu verso Suez e l'Europa.
  - Secondo S&P Global, a ottobre i transiti totali sono 1.196, ma quelli legati all'Arabia Saudita scendono a 21 (52 a settembre).
  - Ad agosto due metaniere qatariote sono state colpite ([Cyprus Shipping News 6/8](https://cyprusshippingnews.com/2026/08/06/a-second-qatari-lng-carrier-struck-as-22-chinese-vessels-cross-the-red-sea-unharmed/)).
- **Bosforo.** CPC e Novorossiysk caricano nel Mar Nero; il greggio CPC (Kazakistan) passa poi dal Bosforo verso il Mediterraneo, cioè verso Trieste, Augusta e Sarroch. TurkStream è il gas che arriva sulla sponda europea della Turchia.
- **Prezzi** (da `docs/data/prezzi.json`, Yahoo Finance, 9/11/2026):
  - Brent: 93,65 USD/barile, −4,75% in un giorno sulla mediazione del Qatar, +54% da inizio anno.
  - TTF: 82,33 EUR/MWh, +192% da inizio anno, +164% in un anno.
  - Henry Hub: 3,24 USD/MMBtu, −12% da inizio anno.
  - Valutazione: lo scarto tra TTF e Henry Hub è la misura del premio GNL dovuto a Hormuz. L'Italia è esposta soprattutto via TTF/PSV, mentre i volumi tengono grazie ad Algeria e TAP.
- **Italia esposta.**
  - Il 34% degli ingressi viene dall'Algeria con un solo tubo, che attraversa il Canale di Sicilia ed è anche in `condotte.json`.
  - Circa il 33% arriva come GNL, comprato a prezzi spot.
  - Il Qatar era il primo fornitore di Adriatic LNG prima della guerra (valutazione da verificare con dati Kpler o GIIGNL, che non ho).

## Proposta per la mappa

- **Terminali GNL.**
  - Cerchio proporzionale a `capacita_operativa_mtpa`, oppure a `capacita_totale_mtpa` se il terminale non è operativo.
  - Colore per `tipo`: liquefazione o rigassificazione.
  - Contorno tratteggiato se non operativo.
  - Filtro per stato. Di default mostrare solo operativi e in costruzione: tra i 840 ci sono anche molti cancellati.
- **Gas Italia.**
  - Freccia o cerchio in ogni punto, con spessore uguale a `flussi.entry.riassunto.media_30g_gwh`.
  - Nel popup, un grafico a linee di 12 mesi (`flussi.entry.serie`, con `exit` se presente) e la quota sui 12 mesi.
  - Nel pannello Italia, un riquadro a parte con `ingressi_totali` e TurkStream.
- **Collegamenti tra livelli.**
  - Mazara, Gela e Melendugno si uniscono alle linee TransMed, Greenstream e TAP di `condotte.json` (stessi nomi GEM).
  - I terminali del Golfo si collegano a Hormuz in `stretti.json`.

## Limiti

- **Dati ENTSOG.** Gli ultimi giorni possono essere provvisori. La conversione da kWh a Smc usa un potere calorifico fisso ed è indicativa.
- **Gaps nella serie del gas.** Mancano i flussi del GNL di piccola taglia e della Sardegna.
- **Dati GEM.** La capacità dei terminali è quella di targa, non l'uso effettivo. Lo stato si aggiorna con le release GEM, circa ogni mese. Il file sorgente pesa 195 MB a ogni esecuzione: su GitHub Actions va bene, ma è lento.
- **Notizie sulle condotte.** Vengono da ricerche web e non le ho verificate sulle fonti primarie: due siti (spglobal.com e hellenicshippingnews.com) sono bloccati dalla rete di questa sessione. Restano aperti lo stato di Druzhba dopo l'1/8 e quello di CPC dopo luglio.
- **Gasdotti in `gas-italia.json`.** Non contengono le linee: quelle sono in `linee.json` e `condotte.json`, che non ho toccato.
