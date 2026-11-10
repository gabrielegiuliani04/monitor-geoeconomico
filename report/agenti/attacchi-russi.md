# Agente ATTACCHI RUSSI IN UCRAINA: dove, con che cosa, contro che cosa (24/2/2022 – oggi)

Rapporto del 10 novembre 2026. Script: `raccolta/ucraina/attacchi_russi.py`, solo libreria standard. L'ho eseguito davvero: impiega meno di 10 secondi, non dà errori e scrive `docs/data/attacchi-russi.json` (0,13 MB). Con `--solo-valida` controlla solo la parte curata: oggi 192 eventi validi su 192.

## File prodotti

| File | Contenuto |
|---|---|
| `docs/data/attacchi-russi.json` | **elementi**: 192 attacchi russi geolocalizzati, dal 2/3/2022 al 30/10/2026, nel formato `{id, data, lat, lon, precisione_km, origine_coord, citta, oblast, categoria, mezzi, quanti, effetto, fonte, link, data_fonte, affidabilita}`. **per_oblast**: 25 voci (24 oblast più Kyiv città; Crimea esclusa), ciascuna con il centroide (lat, lon) e due serie mensili `[AAAA-MM-01, n]`: `giorni_citati` dal dataset Ivaniuk ed `eventi_curati`, più i totali. **riepilogo**: eventi per anno e categoria, eventi per anno e oblast, giorni citati per anno e oblast. |
| `raccolta/ucraina/attacchi_russi_curati.json` | La parte curata a mano, che lo script legge e valida: campi obbligatori, data compresa tra il 24/2/2022 e oggi, coordinate dentro i confini dell'Ucraina, vocabolari di categoria e affidabilità, oblast nota, link, id univoci. Gli eventi non validi vengono scartati e finiscono in `errori`. |
| `raccolta/ucraina/attacchi_russi.py` | Parte automatica. (1) Scarica la copia SQLite del dataset Ivaniuk, oppure Kaggle se ci sono `KAGGLE_USERNAME` e `KAGGLE_KEY`, e ne estrae le oblast citate per giorno dai campi `target`, `target_main` e `affected region`. (2) Con `VIINA=1` aggiunge, a titolo opzionale, i conteggi mensili VIINA (vedi sotto). (3) Valida la parte curata e scrive il file. |

**Per la mappa.** Con il cursore del periodo si filtrano gli `elementi` per `data` e si colorano per `categoria`; l'icona può dipendere da `mezzi` e l'opacità da `affidabilita`. Per lo stesso periodo si sommano `per_oblast.giorni_citati` e `per_oblast.eventi_curati`, disegnando cerchi proporzionali sul centroide dell'oblast. Va mostrata `precisione_km`, perché il punto è il centro abitato e non il luogo dell'impatto. Le ondate nazionali contro la rete restano in `ucraina-storico.json`, alla voce `ondate_rete_ucraina`.

## Fonti provate

| Fonte | Esito | Licenza | Uso |
|---|---|---|---|
| Dataset di Petro Ivaniuk (*Massive Missile Attacks on Ukraine*), copia SQLite di Narretz/sbs-stats su R2 | **funziona** (copia del 7/11/2026, dati fino al 6/11/2026) | **CC BY-NC-SA 4.0**: va citato, uso non commerciale, i derivati con la stessa licenza | Usato. Non contiene un campo `regioni`. Contiene invece `target` (4.336 righe; circa 1.300 nominano un'oblast o una città), `target_main` (175 righe, dal 6/2025 all'11/2026) e `affected region` (217 righe, dall'1/2025 al 7/2026). `launch_place` indica i luoghi di lancio in Russia o nei territori occupati, quindi non serve allo scopo. |
| Kaggle (originale Ivaniuk) | **serve una chiave** | come sopra | Lo script lo usa se trova le chiavi. |
| VIINA 2.0 (Zhukov e Ayers, GitHub `zhukovyuri/VIINA`) | **licenza aperta, ma non scaricabile da qui**: i file stanno su Git LFS, da questo ambiente arriva solo il puntatore (errori 403/404) e la richiesta di accesso al repository mi è stata negata | **ODbL** (ripubblicabile con attribuzione e share-alike) | È la migliore fonte automatica aperta con luogo: eventi geocodificati da notizie e classificati con un modello BERT (attore, attacco aereo, drone, artiglieria). Nello script è opzionale (`VIINA=1`) e **non è stato provato**. Va attivato su GitHub Actions, dove `github.com/.../raw/` dovrebbe funzionare. |
| Telegram delle amministrazioni militari regionali (`t.me/s/odeskaODA`, `t.me/s/kpszsu`) | **funziona** (HTML statico) | — | Non integrato: i testi sono in ucraino e senza struttura, e non ho trovato progetti aperti che li trasformino in dati strutturati con licenza. Si possono aggiungere in futuro con estrazione a parole chiave e revisione manuale. |
| KSE, rapporti *Russia will pay* (danni all'energia) | il sito funziona | rapporti PDF, nessuna licenza sui dati | Solo dati aggregati in PDF, senza punti: non usato. |
| UN HRMMU / OHCHR (vittime civili per oblast) | la pagina OHCHR dà **404**; su HDX il dataset aperto (CC BY) copre solo il 2016–2021 | CC BY (HDX) | I rapporti mensili 2022–2026 sono PDF e non li ho trasformati in dati: non usati. |
| Energy Map (DiXi Group), dataset *massive strikes on critical infrastructure* | il dominio reindirizza a `energy-map.info`, con accesso tramite login e piani a pagamento | termini di servizio, nessuna licenza aperta trovata | Non usato. |
| CIR *Eyes on Russia*, Bellingcat *civilian harm* | nessun download aperto trovato; l'API di Bellingcat dà 404 | — | Non usati. |
| **ACLED** | — | **vieta di ripubblicare i dati grezzi** | **Escluso** come da regole. |
| Kyiv Independent (sitemap con 51.536 articoli, pagine di tag, articoli) | **funziona** | diritti riservati | È la fonte di 180 eventi su 192. Riporto solo fatti, con link e testi miei brevi. |
| Wikipedia, *Odesa strikes (2022–present)* | **funziona** (API REST; la ricerca va in limite 429) | CC BY-SA per i testi | Da qui vengono gli altri 12 eventi, con il link alla fonte citata da Wikipedia: Reuters (4), Ukrainska Pravda (4), AP, ABC, France 24 e United24 (1 ciascuno). |
| OpenStreetMap Nominatim | **funziona** (1 richiesta al secondo) | ODbL | Coordinate dei centri abitati e centroidi delle oblast. Ho corretto a mano omonimi sbagliati con una ricerca strutturata per città e oblast: Dnipro, Hroza, Kherson, Poltava, Ternopil, Vinnytsia, Zhytomyr e Chernihiv. |

**Licenze del file.** I valori di `per_oblast.giorni_citati` e il `riepilogo` derivano da Ivaniuk e quindi sono **CC BY-NC-SA 4.0**. Le coordinate sono ODbL. Gli eventi curati sono fatti con link alla fonte. Il file va dichiarato CC BY-NC-SA in `DATA_LICENSES.md`, compito che spetta al coordinatore. Se si attiva VIINA, anche quella parte va offerta sotto ODbL.

## Cosa mostra il dato

**Eventi curati per anno e categoria.** Sono eventi chiave scelti dando priorità a porti, energia, ferrovie e logistica, quindi **non sono un campione statistico**.

| Anno | Eventi | Energia | Porti | Ferrovie | Grano/logistica | Industria | Civile | Oblast più presenti |
|---|---|---|---|---|---|---|---|---|
| 2022 | 33 | 15 | 2 | 5 | 5 | 3 | 2 | Dnipropetrovsk 9, Mykolaiv 4, Lviv 4 |
| 2023 | 30 | 6 | 9 | 2 | 5 | 1 | 6 | **Odesa 15** |
| 2024 | 24 | 10 | 6 | 1 | 3 | 0 | 3 | Odesa 11, Kharkiv 4 |
| 2025 | 38 | 12 | 5 | 4 | 2 | 2 | 13 | Odesa 7, Kyiv 7, Dnipropetrovsk 6 |
| 2026 | 67 | 20 | 7 | **10** | 7 | **10** | 11 | Odesa 14, Kyiv 12, Dnipropetrovsk 10 |

**Oblast citate nei comunicati dell'Aeronautica (dataset Ivaniuk, giorni per anno).** Le prime tre di ogni anno:
- 2022 (dal 28/9): Mykolaiv 15, Odesa 8, Dnipropetrovsk 3
- 2023: Dnipropetrovsk 54, Odesa 38, Mykolaiv 36
- 2024: Odesa 105, Dnipropetrovsk 78, Kherson 76
- 2025: Kharkiv 121, Odesa 117, Sumy 114, poi Kyiv 91
- 2026: Odesa 96, Kyiv 60, Rivne 36, poi Khmelnytskyi e Volyn

Nel complesso del periodo l'oblast più citata è **Odesa (364 giorni)**, seguita da Dnipropetrovsk (255) e Kharkiv (200). La geografia dipende anche da chi scrive i comunicati: il comando Sud riporta più spesso, mentre nel 2026 compaiono molto le oblast occidentali perché il comando Ovest indica i suoi bersagli principali.

**Cambi di strategia.** Fatti dalle fonti indicate; le interpretazioni sono segnalate come tali.
1. **Energia, 2022–23.** Dal 10/10/2022 gli attacchi si spostano su centrali e sottostazioni in tutto il paese: Burshtyn (10 e 19/10), Ladyzhyn (11/10), quattro sottostazioni nell'oblast di Lviv (11/10), Lutsk (22/10). A fine dicembre 2022 il governo dice che tutte le centrali termiche e idroelettriche sono state danneggiate ([KI 11/12/2022](https://kyivindependent.com/pm-all-of-ukraines-thermal-hydroelectric-power-stations-damaged-by-russian-attacks/)). Nel 2024 la campagna torna sulla generazione:
   - DniproHES colpita il 22/3 e di nuovo l'1/6, quando è «in condizioni critiche»;
   - Zmiiv e Trypillia distrutte (22/3 e 11/4);
   - DTEK dichiara di aver perso circa il 90% della sua capacità ([KI 29/6/2024](https://kyivindependent.com/dtek-90-of-companys-energy-generating-capacity-lost-due-to-russian-strikes/)).
2. **Porti di Odesa e del Danubio, luglio–settembre 2023.** Dopo l'uscita russa dall'accordo sul grano: 60.000 tonnellate di grano distrutte a Chornomorsk il 19/7, poi Reni e Izmail il 24/7, Izmail il 2/8, il 23/8 (20 Shahed) e il 13/9. Il ministero segnala 105 strutture portuali danneggiate in due mesi ([KI 13/9/2023](https://kyivindependent.com/minister-russias-attacks-on-ukrainian-ports-damage-105-port-infrastructure-facilities-in-2-months/)). Da luglio 2023 a novembre 2024 le strutture portuali danneggiate sono 321 e le navi straniere 20 (Zelensky, [KI 23/11/2024](https://kyivindependent.com/russia-damaged-over-300-port-facilities-20-foreign-vessels-in-the-past-year-zelensky-says/)).
3. **Navi e porti, 2024–2026.** Nell'ottobre 2024 vengono colpite navi civili a Odesa e Pivdennyi: le navi Paresa, Optima e NS Moon, e una nave di aiuti con 8 morti il 9/10. Nel 2026 gli attacchi diventano più intensi: oltre 800 droni contro i porti da inizio anno, più di 10 volte il 2025 (Kuleba, [KI 4/5/2026](https://kyivindependent.com/russia-launched-over-800-drones-on-ukraines-port-infrastructure-this-year-minister-says/)). A luglio vengono colpite navi cargo, tra cui la Golden Leo, con 10 morti il 19/7; il 9/8 Odesa subisce un attacco con 11 missili e fino a 100 droni.
4. **Rete e gas, 2024–2026.** Nel 2025 Naftogaz subisce 229 attacchi, più che nei tre anni precedenti messi insieme; a ottobre è fuori uso quasi il 60% della produzione di gas ([KI 17/2/2026](https://kyivindependent.com/russia-launched-229-attacks-on-ukraines-naftogaz-in-2025-more-than-previous-three-years-combined/)). L'8/11/2025 tutte le centrali Centrenergo sono ferme. Nel 2026:
   - il 13/1 il 70% di Kyiv resta senza corrente;
   - il 7/2 l'attacco alle sottostazioni collegate alle centrali nucleari dimezza la produzione nucleare ([KI 9/2/2026](https://kyivindependent.com/ukraine-repairs-nuclear-substation-but-situation-remains-critical-after-mass-attack/));
   - da settembre risultano oltre 800 impianti energetici danneggiati ([KI 30/10/2026](https://kyivindependent.com/russia-has-damaged-more-than-800-ukrainian-energy-assets-since-september/));
   - la Russia continua gli attacchi anche dopo la «tregua energetica» annunciata da Trump l'11/10 (CHP-5 di Kharkiv, centrali di Kyiv il 14/10).
5. **Ferrovie, 2025–2026.** Nel 2025 le infrastrutture ferroviarie sono state attaccate quasi 1.200 volte, più che nel 2023 e nel 2024 messi insieme (Ukrzaliznytsia, [KI 24/4/2026](https://kyivindependent.com/russia-attacks-ukrainian-railway-infrastructure-more-than-1-000-times-in-2025-ukrzaliznytsia-says/)). Le locomotive distrutte o danneggiate sono oltre 500, più della metà nel 2026 (Sybiha, [KI 15/9/2026](https://kyivindependent.com/over-500-train-locomotives-destroyed-or-damaged-by-russian-attacks-in-total-sybiha-says/)). Dai droni sulla linea si passa ai treni passeggeri e alle stazioni:
   - Shostka, 4/10/2025;
   - Barvinkove, 27/1/2026, 5 morti;
   - Brovary, 5/8/2026, 8 morti sul marciapiede;
   - Dnipro, 29/10/2026, 15 morti.
6. **Industria, 2026.** Sono colpite fabbriche di proprietà occidentale o grandi industrie: Flex a Mukachevo (21/8/2025), Mondelez a Trostianets (21/2/2026), Coca-Cola nell'oblast di Kyiv (3/9), Zaporizhstal quattro volte in un mese, Interpipe a Dnipro (22/9), Roshen a Vinnytsia (12/10), Kromberg & Schubert a Lutsk (17/10). *Valutazione:* la scelta di bersagli economici è più frequente nel 2026 che negli anni precedenti, ma il campione curato è troppo piccolo per misurarla.

**Mezzi indicati dalle fonti negli eventi:**

| Mezzo | Eventi |
|---|---|
| missili di tipo non indicato | 49 |
| missili e droni insieme | 40 |
| droni di tipo non indicato | 29 |
| non indicato | 20 |
| missili balistici | 15 (Iskander-M, Oreshnik su Dnipro il 21/11/2024) |
| Shahed/Geran nominati | 8 |
| bombe plananti | 4 (Zaporizhzhia, Pavlohrad, Kherson, Velykyi Burluk) |
| droni FPV | 1 (centrale di Kherson) |

## Collegamenti con gli altri livelli

- **Grano e noli.** `porti-nord.json`, `noli.json` e i prezzi del grano: gli attacchi ai porti di Odesa, Chornomorsk, Pivdennyi e Izmail alzano assicurazioni e noli. KI riporta, il 24/7/2026, che il corridoio del Mar Nero muove il 90% dell'export agricolo ucraino.
- **Energia e rete.** Con `rete-elettrica.json` e `interconnessioni.json`: le importazioni di elettricità dall'UE salgono dopo le ondate. Con `ucraina-storico.json`, alla voce `ondate_rete_ucraina`, si vedono i lanci del giorno.
- **Ferrovie.** Con `ferrovie.json`: la linea Kyiv–Varsavia è stata colpita il 13/9/2026, e le ferrovie portano gli aiuti e l'export verso la Polonia.
- **Danubio.** Reni e Izmail distano circa 200 m dalla Romania: c'è un collegamento con i livelli NATO e Baltico-sicurezza.

## Limiti

- **Non è un censimento.** I 192 eventi sono una selezione: dove ci sono molti eventi c'è stata anche più attenzione nella cura. Il 2024 è meno coperto, e mancano quasi del tutto gli attacchi di artiglieria e di droni FPV sulla linea del fronte. Per contare gli attacchi servirebbe VIINA (ODbL) attivato da GitHub Actions.
- **Coordinate approssimate.** Sono del centro abitato (3–15 km) o dell'oblast (60 km), mai del punto d'impatto. Per scelta non riporto nulla oltre quanto pubblicato. Gli attacchi senza luogo dichiarato (per esempio «una centrale DTEK») li ho esclusi, insieme alle ondate nazionali, che restano in `ucraina-storico.json`.
- **Date.** La data è quella dell'attacco secondo l'articolo; per gli attacchi notturni può spostarsi di ±1 giorno. `data_fonte` è la data di pubblicazione.
- **Ivaniuk.** I campi di luogo indicano bersaglio o direzione dichiarati dall'Aeronautica, non i colpi andati a segno. Sono compilati in modo disuguale: soprattutto il comando Sud tra il 2023 e il 2024, il comando Ovest nel 2026, e `affected region` solo nel 2025. Il dataset non copre il periodo dal 24/2 al 27/9/2022.
- **Fonti.** Le cifre delle vittime sono quelle del primo articolo e possono essere state aggiornate in seguito. Un evento (Bakhmach, 20/9/2025) viene da canali Telegram russi ripresi da KI: l'ho segnato con affidabilità bassa. Reuters, AP e ISW non sono leggibili da qui: li cito tramite i riferimenti di Wikipedia.
