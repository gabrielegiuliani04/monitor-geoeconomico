# Agente EVOLUZIONE DEL FRONTE UCRAINO: aree russe in Ucraina dal 24/2/2022 a oggi

Rapporto del 9 novembre 2026. Script: `raccolta/fronte/raccogli.py`, che richiede **shapely** (`raccolta/fronte/requirements.txt`). L'ho eseguito davvero: la ricostruzione completa scarica 57 mappe DeepState e alcune query ISW e dura circa un minuto. Un aggiornamento normale, quando non c'è un mese nuovo, scarica solo l'elenco degli aggiornamenti e dura meno di un secondo. Scrive `docs/data/fronte-storico.json`, 0,85 MB. Esecuzione di oggi: nessun errore.

## File prodotti

| File | Contenuto |
|---|---|
| `docs/data/fronte-storico.json` | **istantanee** (60): 23/2/2022 (prima dell'invasione), 24/2 e 1/3/2022 (ISW), poi il 1° di ogni mese da aprile 2022 a novembre 2026 (DeepState), più l'ultima mappa DeepState (8/11/2026, `ultima: true`). Ogni istantanea ha: `data`, `data_fonte`, `fonte`, `id_fonte`, `km2`, `km2_var`, `pct_ucraina`, `km2_grigia`, `g` (parti esterne `[[lon,lat],...]`), `buchi`, `g_grigia` (zona grigia, separata). Poi `serie_km2`, `serie_var_km2`, `serie_grigia_km2`, `per_anno`, `massimo`, `momenti_chiave` (19, con fonte, link e km² prima e dopo), `confronto_isw` (6 date), `errori`. |
| `raccolta/fronte/raccogli.py` | Tiene le istantanee già salvate e aggiunge quella del 1° del mese quando manca: l'ultimo aggiornamento DeepState pubblicato entro quel giorno. Sostituisce l'istantanea «ultima» e ricalcola serie e riepiloghi. Opzioni `--ricostruisci` e `--senza-confronto`. |
| `raccolta/fronte/momenti.json` | I momenti chiave, curati a mano e letti dallo script. |
| `raccolta/fronte/ucraina.json` | Contorno semplificato dell'Ucraina (Natural Earth, pubblico dominio). Serve solo a scartare i poligoni fuori dall'Ucraina, per esempio la Transnistria e le zone grigie in Russia. |

**Metodo.** Unisco le categorie DeepState «occupato», «Crimea occupata», «ORDLO» e «isola di Tuzla». Le categorie «stato sconosciuto/conteso» formano la zona grigia: resta separata e non è sommata ai km². Escludo «liberato» e i poligoni ironici di DeepState fuori dall'Ucraina (Carelia, Curili, Prussia…). Gli aggiornamenti del 2022-2023 non hanno l'etichetta `geoJSON.status.*`: li classifico dal nome ucraino e dal colore del riempimento, e leggo anche i `GeometryCollection`. Calcolo le aree sui poligoni originali, in una proiezione equivalente di Lambert centrata sull'Ucraina. Per il file semplifico le geometrie: 1,5 km per le aree russe, 1 km per la zona grigia, coordinate a 3 decimali, parti sotto 0,5 km² tolte. Le dimensioni stanno nel limite: 0,85 MB con tutte le istantanee mensili, quindi non ho dovuto passare a una ogni due mesi.

## Fonti provate

| Fonte | Esito | Licenza / condizioni |
|---|---|---|
| **DeepStateMap**, API dello storico (`/api/history/public`, 1.806 aggiornamenti dal 3/4/2022 all'8/11/2026; `/api/history/<id>/geojson`) | **funziona**, senza chiave (fonte principale) | Diritti riservati a DEEPSTATEUATECH LLC. L'[accordo di licenza](https://deepstatemap.live/license-en.html) (aggiornato al 3/9/2025) dice: API gratuita per «attività di volontariato e di beneficenza» e per la difesa dell'Ucraina; uso commerciale solo con permesso; **vietato ridistribuire, pubblicare o fare da proxy all'API**; i materiali visivi e testuali si possono usare liberamente se citano DeepStateMap o hanno un link. |
| **ISW / AEI Critical Threats Project**, servizi ArcGIS pubblici (`services5.arcgis.com/SaBe5HMtmnbqSWlu`): `UkraineCoTTimelapse_Full_Length_view` (controllo giornaliero dal 24/2/2022 al 31/12/2024) e i servizi mensili 2025-2026 (`Russo_Ukraine_War_November_2025_Timelapse`, `Ukraine_Timelapse_April_2026_WFL1`…) | **funziona**, senza login | Il campo copyright dice «Institute for the Study of War and American Enterprise Institute's Critical Threats Project». Non c'è una licenza aperta dichiarata. Non ho potuto leggere le condizioni sul sito: understandingwar.org da qui risponde 403. |
| Natural Earth 1:10m, versione con il punto di vista ucraino | **funziona** | pubblico dominio |
| geoBoundaries UKR ADM0 | funziona, **non usato** | ODbL. Il confine include le acque territoriali: 638.000 km² invece di circa 600.000. |
| Wikipedia (API) | va in limite di richieste (429); la pagina della battaglia di Kostiantynivka si legge | CC BY-SA |
| Archivi su GitHub di DeepState o ISW | **non provati**: raw.githubusercontent da qui è bloccato | — |
| Ricerca web (Kyiv Independent, Ukrinform, NPR, Meduza, Irish Times/Reuters, Novaya Gazeta Europe, Euromaidan Press, Ukrainska Pravda, NV) | **funziona** | Diritti riservati: uso solo link e brevi citazioni nei momenti chiave. |

**Licenza da segnalare.** DeepState non è una licenza aperta. Il file salva poligoni *derivati*, cioè uniti, semplificati e citati con link, per un progetto personale e non commerciale: rientra nello spirito del punto 3 dell'accordo (materiali visivi con riferimento), ma il progetto non è un'attività di volontariato in senso stretto, e lo script interroga l'API ogni mese. Se il progetto diventa pubblico, consiglio di chiedere il permesso da https://api.deepstatemap.live/request. Non esporre mai l'API attraverso il sito. ISW/CTP: citare sempre «ISW / AEI Critical Threats Project».

## L'andamento in numeri (DeepState salvo indicazione)

- **Prima dell'invasione** (Crimea e ORDLO su DeepState): **43.309 km²**, il 7,2% dell'Ucraina.
- **Prime settimane** (ISW): 79.516 km² a fine 24/2, 119.084 il 27/2. **Picco: 132.782 km² (22,0%) tra il 23 e il 28/3/2022.**
- **Dopo la ritirata da Kyiv:** 106.498 km² sulla prima mappa DeepState (3/4/2022). ISW scende da 122.607 (2/4) a 98.502 (4/4).
- **Massimo DeepState:** **124.830 km² il 1/9/2022** (20,7%), subito prima della controffensiva di Kharkiv.
- **Settembre 2022:** −9.724 km² (115.106 il 1/10). **Ottobre-novembre 2022:** −2.140 e −4.701 (Kherson). Al 1/1/2023: 108.460.
- **2023, fronte quasi fermo:** 108.460 → 108.269 km² (**−191**). Mesi in perdita per la Russia: giugno (−312), luglio (−86), agosto (−234) e settembre (−179) 2023, cioè la controffensiva ucraina, circa −810 km² in quattro mesi. Da ottobre 2023 la Russia guadagna terreno **ogni mese** fino a oggi.
- **Oggi (8/11/2026): 116.864 km², il 19,4% dell'Ucraina.** In più ci sono 1.704 km² di zona grigia, che a metà 2023 era di 403 km². Rispetto a prima dell'invasione: +73.555 km². Rispetto al massimo del settembre 2022: −7.966 km².

**Mesi record** (la data dell'istantanea chiude il mese precedente): novembre 2024 **+705 km²**, luglio 2025 +561, giugno 2025 +546, ottobre 2024 +518, novembre 2025 +502, dicembre 2025 +436.

## Ritmi di avanzata per anno (`per_anno`)

| Anno | Inizio → fine (km²) | Netto | km²/giorno | km²/mese |
|---|---|---|---|---|
| 2022 (dal 23/2) | 43.309 → 108.460 | +65.151 | +208,8 | +6.356 |
| 2022 (dal 3/4, solo DeepState) | 106.498 → 108.460 | +1.962 | — | picco a settembre, poi −18.300 tra settembre e dicembre |
| 2023 | 108.460 → 108.269 | **−191** | −0,5 | −16 |
| 2024 | 108.269 → 111.581 | **+3.312** | +9,0 | +275 |
| 2025 | 111.581 → 115.906 | **+4.325** | +11,8 | +361 |
| 2026 (al 1/11) | 115.906 → 116.843 | **+937** | +3,1 | +94 |

Il 2025 è l'anno con l'avanzata russa più veloce dopo il 2022. Nel 2026 il ritmo crolla. Gennaio vale ancora +247 km² e marzo +193, ma da maggio i saldi sono quasi nulli: +14 a maggio, +83 a giugno, +38 a luglio, +22 ad agosto, +53 a settembre e +59 a ottobre. In quei mesi c'è la controffensiva ucraina di Oleksandrivka, e la Russia resta ferma davanti a Kostiantynivka.

## Momenti chiave (in `momenti_chiave`, ciascuno con fonte e link)

Le date «sulla mappa» sono quelle in cui il centro della città entra nell'area russa di DeepState (o ne esce). Le ho trovate con una ricerca binaria nello storico dell'API, sono un dato mio, e arrivano spesso prima o dopo l'annuncio ufficiale.

- **2/4/2022, ritirata da Kyiv:** Maliar annuncia liberata tutta la regione di Kyiv (Ukrinform).
- **12/4/2022 Mariupol, 30/5 Sievierodonetsk, 3/7 Lysychansk:** date sulla mappa.
- **10/9/2022, controffensiva di Kharkiv:** Izium e Kupiansk; Zelensky: oltre 6.000 km² dall'inizio di settembre (Kyiv Independent). **1/10/2022, Lyman.**
- **11/11/2022, Kherson:** riva destra del Dnipro liberata (NPR).
- **20/5/2023, Bakhmut:** Prigozhin rivendica la città (Meduza); sulla mappa il centro è russo dal 4/4/2023.
- **Giugno-settembre 2023, controffensiva:** Robotyne liberata il 28/8/2023 (Kyiv Independent). È l'unico anno con saldo negativo per la Russia.
- **17/2/2024, Avdiivka:** ritiro ucraino deciso da Syrskyi (Irish Times/Reuters).
- **6/8/2024, Kursk:** l'Ucraina entra in Russia, fino a circa 1.300 km² (AP). Sudzha torna russa il 13/3/2025 (Novaya Gazeta Europe); il 26/4/2025 Mosca dichiara ripresa tutta la regione (Euromaidan Press). Queste aree sono in Russia e **non** entrano nei km².
- **1/10/2024 Vuhledar, 27/10 Selydove, 29/11 Kurakhove, 23/1/2025 Velyka Novosilka, 29/4/2025 Toretsk, 14/5/2025 Chasiv Yar:** date sulla mappa.
- **Pokrovsk:** centro russo sulla mappa dal 20/11/2025, Myrnohrad dal 28/12/2025. L'8/12/2025 Ukrainska Pravda scrive che la maggior parte della città è russa. **Siversk** occupata il 23/12/2025, **Huliaipole** il 15/1/2026, Rodynske il 4/7/2026.
- **12/8/2026, controffensiva di Oleksandrivka:** Zelensky annuncia 26 località e circa 745 km² da gennaio (Kyiv Independent). ISW ne stima circa 627. DeepState segna 19 villaggi liberati.
- **Ottobre-novembre 2026, Kostiantynivka:** la città resta contesa. Il centro è fuori dall'area russa di DeepState all'8/11/2026. ISW valuta perdite nette russe a settembre e ottobre 2026.

## Confronto DeepState / ISW (`confronto_isw`, calcolato dallo script)

| Data | DeepState km² | ISW km² | Differenza | Solo DeepState | Solo ISW |
|---|---|---|---|---|---|
| 3/4/2022 | 106.588 | 103.345 | +3.243 | 16.984 | 13.741 |
| 1/9/2022 | 124.830 | 120.371 | +4.459 | 5.218 | 759 |
| 1/6/2023 | 108.970 | 106.435 | +2.535 | 2.893 | 357 |
| 1/12/2024 | 111.193 | 109.387 | +1.806 | 1.989 | 183 |
| 1/11/2025 | 114.968 | 112.101 | +2.868 | 3.013 | 145 |
| 1/4/2026 | 116.433 | 112.683 | +3.750 | 3.909 | 159 |

DeepState dà alla Russia sempre **1.800–4.500 km² in più** di ISW, l'1,6–3,7%. Il territorio russo di ISW sta quasi tutto dentro quello di DeepState. La differenza è la fascia di fronte che DeepState colora già russa e che ISW lascia fuori: ISW la mette tra le «avanzate» o le «infiltrazioni», che qui non conto. Il 3/4/2022 le due mappe si sovrappongono poco (14–17.000 km² di disaccordo per parte): il fronte nord si stava ritirando e ciascuna l'ha disegnato a modo suo. Il cambio di fonte tra marzo (ISW) e aprile 2022 (DeepState) è segnato con `cambio_fonte: true`.

**Confronto con la mappa di @Majakovsk73** (`fronte.json`, 5/11/2026, non modificato). Le sue aree «ru» e «avanzata» fanno 122.534 km², DeepState ne dà 116.855 il 4/11/2026. Ma 6.839 km² delle sue aree non sono in DeepState. Sono soprattutto acque: estuario Dnipro-Bug e Kinburn (2.181 km²), laguna del Sivash (1.950), costa d'Azov, bacino di Kachovka (720) e costa meridionale della Crimea. Sulla terraferma le due mappe sono vicine: 1.156 km² russi per DeepState non sono russi per l'autore. Delle sue zone «contese» (2.644 km²), 1.201 coincidono con la zona grigia di DeepState. **Non sommare le due fonti.**

**Altre stime per la stessa epoca, citate da fonti secondarie e non verificate da me.** Per Russia Matters, su dati DeepState, la Russia ha un saldo di +18 miglia² (circa 47 km²) dal 29/9 al 26/10/2026 e un saldo negativo nelle quattro settimane prima. Io ho +53 km² a settembre: le stesse mappe danno saldi diversi a seconda di come si tratta la zona grigia e di quale aggiornamento si prende come riferimento.

## Collegamenti con la mappa

- **Livello `fronte.json`** (aree dell'autore di oggi): `fronte-storico.json` è il suo passato, ma da un'altra fonte. Con il cursore conviene mostrare una sola fonte per volta e indicare la fonte nella legenda.
- **`ucraina-storico.json`** (lanci e attacchi): i mesi del 2026 con avanzata quasi nulla, da maggio a ottobre, sono anche i mesi record dei lanci russi (10.098 a maggio 2026). La guerra si sposta dal terreno al cielo. Gli attacchi ucraini alle raffinerie possono essere messi a confronto con la serie mensile dei km².
- **Energia:** la centrale nucleare di Zaporizhzhia e Kachovka restano dentro l'area russa per tutta la serie dal 2022. Il Donbas di Pokrovsk, il principale bacino di carbone da coke dell'Ucraina, passa russo tra novembre 2025 e gennaio 2026.

## Proposta di visualizzazione

Un cursore mensile, da febbraio 2022 a novembre 2026, sul livello Ucraina:
- poligono rosso con riempimento pari-dispari, `g` più `buchi`;
- zona grigia tratteggiata, `g_grigia`;
- etichetta con data, km², % e variazione sul mese.

Sotto, un piccolo grafico a barre di `serie_var_km2`, verde per le perdite russe e rosso per i guadagni, con un segno per ogni momento chiave. Le prime tre istantanee (23/2, 24/2 e 1/3/2022) vanno marcate come «ISW / prima dell'invasione», con un avviso al passaggio ad aprile 2022.

## Limiti

- **Mappe OSINT, non dati ufficiali.** DeepState è un progetto ucraino, ISW un centro studi statunitense: entrambi valutano. Le differenze tra mappe arrivano fino a 4.500 km², molto più dei saldi mensili del 2026, che sono sotto i 100 km². I saldi mensili piccoli vanno letti come «fronte fermo», non come numeri precisi.
- **Prima del 3/4/2022 non c'è DeepState.** Febbraio e marzo vengono da ISW, che per il 2022 separa «controllo» e «avanzate»: le avanzate sono in `g_grigia`. Il picco di marzo 2022 esiste solo nella serie ISW.
- **Istantanea del 1° del mese:** un'istantanea al mese non vede ciò che succede dentro il mese. Per esempio, la massima estensione di marzo 2022 sta tra due istantanee. DeepState a volte corregge mappe vecchie: il file salva l'aggiornamento come era quel giorno.
- **Kursk e le zone russe di confine** sono fuori dal calcolo: il file misura solo il territorio ucraino.
- **Classificazione 2022-2023:** dedotta dai nomi ucraini e dai colori, perché mancano le etichette. L'ho verificata: non ci sono sovrapposizioni tra aree occupate, liberate e grigie, e ogni mappa ha Crimea e ORDLO. Se DeepState cambia nomi o colori, lo script potrebbe perdere categorie: il controllo veloce è che `km2` non scenda di colpo di 15–25.000 km².
- **Semplificazione:** le geometrie del file perdono i dettagli sotto 1,5 km. I km² sono calcolati prima della semplificazione.
- Lo script dipende da shapely, non solo dalla libreria standard. È un'eccezione alle regole di AGENTI.md, concessa per questo compito.
