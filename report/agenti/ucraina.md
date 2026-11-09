# Agente STORICO DEGLI ATTACCHI IN UCRAINA: missili e droni russi, attacchi ucraini all'energia russa

Rapporto del 9 novembre 2026. Script: `raccolta/ucraina/raccogli.py`, solo libreria standard. L'ho eseguito davvero: gira in circa 10 secondi e scrive `docs/data/ucraina-storico.json` (0,65 MB).

## File prodotti

| File | Contenuto |
|---|---|
| `docs/data/ucraina-storico.json` | **serie**: lanci e abbattimenti giornalieri dal 28/9/2022 al 6/11/2026, 1.272 giorni con dati, totale e per tipo (Shahed/Geran, altri droni, Kh-101, Kalibr, Iskander-K, Iskander-M/KN-23, Kinzhal, Kh-22/32, Kh-59/69, S-300/400, Zircon/Oniks, Kh-31/35, Banderol, missili misti) e per categoria (drone, crociera, balistico). **mensile**: per ogni gruppo `[mese, lanciati, abbattuti, % abbattuti]`. **riepilogo**: totali, 20 giorni di picco, giorni con cifre non divulgate. **ondate_rete_ucraina**: 18 grandi ondate contro la rete ucraina con i danni dichiarati e i numeri del dataset del giorno prima e del giorno stesso. **elementi**: 258 punti degli attacchi ucraini a raffinerie, depositi, porti, stazioni di pompaggio e basi aeree in Russia (e 1 in Crimea occupata), dal 25/2/2022 al 9/11/2026. |
| `raccolta/ucraina/attacchi_energia_russia.json` | i 258 punti curati, letti dallo script. Ogni punto: lat/lon, origine e precisione della coordinata, data, bersaglio, mezzo, esito, rivendicazione, fonte principale e lista `fonti`, affidabilità, note con un estratto della fonte. |
| `raccolta/ucraina/ondate_rete_ucraina.json` | le 18 ondate curate, lette dallo script. |

Formato come in AGENTI.md (`aggiornato`, `fonti`, `nota`, `elementi`, `errori`; serie `[["AAAA-MM-GG", valore]]`). Esecuzione di oggi: nessun errore.

Come ho costruito i punti. Ho incrociato tre insiemi: 251 articoli del Kyiv Independent (tag *oil-refineries*, marzo 2024 – novembre 2026), la lista di Wikipedia *Attacks in Russia during the Russo-Ukrainian war* con le fonti citate (2022–2026), e 21 aggiunte fatte a mano (operazione Ragnatela, Primorsk e Ust-Luga 2026, Omsk, Šeschacharis, la campagna di fine ottobre e novembre 2026). Ho collegato gli impianti con espressioni regolari, ho unito gli eventi sullo stesso impianto nello stesso giorno o in quello dopo e ne ho scartati a mano 47 sbagliati, per esempio articoli di analisi o regioni citate solo come sfondo. Il campo `esito` dei punti non aggiunti a mano viene da parole chiave del testo della fonte, quindi va letto con l'estratto nelle `note`. Le coordinate vengono da OpenStreetMap Nominatim: quelle dell'impianto se trovato, con precisione di 2–3 km, altrimenti quelle del centro abitato, con 10 km, o della regione, con 30 km.

## Fonti provate

| Fonte | Esito | Licenza | Note |
|---|---|---|---|
| Kaggle, *Massive Missile Attacks on Ukraine* (piterfm = Petro Ivaniuk) | **serve chiave** | CC BY-NC-SA 4.0 (dichiarata dai progetti che lo riusano; kaggle.com non è leggibile da qui, quindi non l'ho vista sulla pagina) | Da qui l'API senza autenticazione risponde 404. Lo script la usa se ci sono `KAGGLE_USERNAME` e `KAGGLE_KEY`; altrimenti la salta senza fallire. |
| GitHub `PetroIvaniuk/2022-Ukraine-Russia-War-Dataset` | **non contiene il dataset** | MIT | Il repository ha solo le perdite russe (personale, equipaggiamento). I file sui missili sono soltanto su Kaggle: non esiste una versione «GitHub raw» dell'autore. |
| Copia SQLite di Narretz/sbs-stats su Cloudflare R2 (`ru-air-attacks-gsua.db`) | **funziona, senza login** (fonte usata) | codice MIT; dati CC BY-NC-SA dell'autore | Si aggiorna ogni giorno dalla stessa API Kaggle: copia del 7/11/2026 12:45 UTC, dati fino al 6/11/2026. Tiene le versioni corrette delle righe e segna quelle tolte a monte. |
| Copia CSV su GitHub (`ShadenAlrshoud/air-attacks-eda-dashboard`) | **funziona** (riserva) | come sopra | Ferma al 24/10/2026. Provata: 4.285 righe. |
| Hugging Face | nessuna copia trovata | — | — |
| Kyiv Independent (pagine di tag e articoli) | **funziona** | diritti riservati: solo link e brevi estratti | Fonte principale dei punti 2024–2026. |
| Wikipedia (pagine) | **funziona**; l'API va in limite di richieste (429) | CC BY-SA | Lista *Attacks in Russia…*, *2025–2026 Russian fuel crisis*, *Russian strikes against Ukrainian infrastructure*. |
| The Moscow Times, Meduza (API `meduza.io/api/w5`) | **funziona** | diritti riservati | — |
| Reuters, AP, ISW, Euromaidan Press | **bloccati** da qui (401/403/rete) | — | Reuters e AP li cito attraverso ristampe datate: Internazionale, US News, ABC, NPR, PBS, NV. |
| OpenStreetMap Nominatim | **funziona**, con limite di frequenza | ODbL | Coordinate degli impianti. |
| Yahoo Finance (chart API) | **funziona** | uso personale | Chiusure mensili di Brent (BZ=F) e gasolio NY Harbor ULSD (HO=F), solo per il rapporto. |
| FRED (St. Louis Fed) | **non funziona** da qui (connessione chiusa) | pubblico dominio | — |
| Telegram `t.me/s/<canale>` | **funziona** | — | Clément Molin e AMK Mapping. |
| X via xcancel / nitter | **non funziona** (451; RSS di nitter 410) | — | — |

**Licenza da segnalare:** il dataset dei missili è CC BY-NC-SA, cioè non commerciale e da ridistribuire con la stessa licenza. Va bene per il progetto, che è personale e non commerciale, ma `ucraina-storico.json` eredita la condizione.

## Tendenze dei lanci russi (dati dell'Aeronautica ucraina, calcolati da me)

| Anno | Lanciati | Abbattuti | % | di cui droni | balistici lanciati / abbattuti |
|---|---|---|---|---|---|
| 2022 (dal 28/9) | 1.157 | 909 | 78,6 | 459 | 43 / 0 |
| 2023 | 4.812 | 3.843 | 79,9 | 3.392 | 236 / 57 |
| 2024 | 14.112 | 9.554 | 67,7 | 11.890 | 631 / 67 |
| 2025 | 58.775 | 40.058 | 68,2 | 56.758 | 749 / 169 |
| 2026 (al 6/11) | 77.439 | 68.635 | 88,6 | 75.301 | 804 / 240 (minimo: cifre in parte non divulgate) |

- **Lanci al mese.** Media mensile: circa 1.200 nel 2024, 4.900 nel 2025 e 7.600 nel 2026. Il mese record è maggio 2026, con 10.098 lanci; seguono aprile 2026 (8.187), settembre 2026 (8.106) e marzo 2026 (8.035). Ottobre 2026 ne ha 7.176.
- **Picchi giornalieri.** Notte del 13/5/2026: 1.449 lanciati e 1.374 abbattuti. Poi 12/9/2026 (903), 6/9/2025 (832), 8/7/2025 (811) e 1/6/2026 (783).
- **Composizione.** Dal 2025 i droni sono il 97% dei lanci; gli Shahed/Geran sono 54.796 nel 2025 e 61.467 nel 2026. I missili da crociera restano stabili, circa 1.200–1.600 l'anno. I Kh-101 calano: 707 nel 2023, 381 nel 2026.
- **Tasso di abbattimento.** Contro i droni è sceso dal 94% del 2022 al 68–70% del 2024–25 ed è risalito all'87–90% nel 2026. Il salto di agosto 2025 (da 58% a 84% in un mese) è in buona parte **un cambio di conteggio**: fino a luglio 2025 i droni «persi in volo» per guerra elettronica erano separati, nella colonna `not_reach_goal` (2.000 a luglio 2025), mentre da agosto non lo sono più. Il calo del 2024–25 riflette anche le esche senza carica. Per la difesa aerea il dato critico sono i balistici: Iskander-M/KN-23 abbattuti al 13–23%, Kinzhal al 27–35%, S-300/400 usati contro terra quasi mai.
- **Dati nascosti.** Dal 13/8/2026 l'Aeronautica non pubblica alcune cifre sui balistici, per motivi di sicurezza operativa: 13 giorni sono in `giorni_non_divulgati`. In quei giorni i lanciati vanno letti come un minimo.

## Fatti attuali rilevanti

1. **6–7 novembre 2026: oltre 1.000 droni Geran-2/4/5 e missili S8000 Banderol in 72 ore**, con esplosioni in circa 279 località, di cui 189 città e paesi; colpite in particolare le sottostazioni di Dnipropetrovsk. Fonte: AMK Mapping, Telegram, 9/11/2026 ([post](https://t.me/AMK_Mapping/40474)). Il dataset registra 603 lanci il 31/10, 527 l'1/11 e 576 il 2/11/2026.
2. **Campagna russa contro la rete:** dall'1/11/2026 oltre 2.000 droni e 100 missili contro l'energia ucraina, e almeno 80 sottostazioni colpite da fine settembre. È una valutazione di Clément Molin ([3/11/2026](https://t.me/clement_molin/1958)). Il 7/11/2026 risultano danneggiate una centrale DTEK e sottostazioni Ukrenergo che alimentano Kyiv ([Anadolu](https://www.anews.com.tr/europe/2026/11/07/electricity-suppliers-warn-of-further-power-cuts-in-kiev)).
3. **Kirishi, 9/11/2026.** È la seconda raffineria russa (circa 350.000 barili/giorno, circa 7% della raffinazione nel 2024). Il governatore conta 113 droni abbattuti e una donna uccisa da detriti a Vsevoložsk ([Moscow Times](https://www.themoscowtimes.com/2026/11/09/ukrainian-drone-attack-kills-woman-sparks-fire-at-leningrad-region-refinery-a94204)); incendi multipli rilevati da NASA FIRMS ([AMK](https://t.me/AMK_Mapping/40470)). Secondo Molin è l'8ª raffineria colpita in 10 giorni ([post](https://t.me/clement_molin/1976)): le altre sono Novokujbyševsk (30/10), Ufa (31/10), Kstovo (1/11), Jaroslavl (3/11), Riazan (5/11), Afipskij (6/11) e Saratov (7/11), più il nodo di oleodotti di Prosvet (2/11).
4. **Questa campagna ucraina contraddice la «tregua energetica» annunciata da Trump l'11/10/2026.** Kyiv ha ripreso gli attacchi il 15/10 ([Kyiv Independent](https://kyivindependent.com/moscow-closes-sky-multiple-nights-in-row-as-ukraine-resumes-refinery-strikes/)). Rosneft è tornata a limitare a 30 litri le vendite di benzina in diverse regioni ([Moscow Times, 9/11/2026](https://www.themoscowtimes.com/2026/11/09/ukrainian-drone-attack-kills-woman-sparks-fire-at-leningrad-region-refinery-a94204)).
5. **Nel file ci sono 258 attacchi ucraini a obiettivi energetici e aerei in Russia.** Per anno: 9 nel 2022, 12 nel 2023, 65 nel 2024, 69 nel 2025 e 103 nel 2026. Gli impianti più colpiti sono Saratov (14), Volgograd, Riazan e Jaroslavl (13 ciascuno), Tuapse (11). Secondo Molin, nel 2026 sono state colpite almeno 28 raffinerie su circa 48, con 81 attacchi in otto mesi, e circa 130 attacchi all'intera filiera petrolifera ([26/8/2026](https://t.me/clement_molin/1641)).
6. **Operazione Ragnatela, 1/6/2025.** Droni FPV lanciati da camion hanno colpito bombardieri a Olenja e Belaja; l'SBU rivendica 41 aerei colpiti anche a Djagilevo e Ivanovo ([Kyiv Independent](https://kyivindependent.com/enemy-bombers-are-burning-en-masse-ukraines-sbu-drones-hit-more-than-40-russian-aircraft/)). La cifra è una rivendicazione di parte; i danni a Olenja e Belaja sono visibili in immagini satellitari.
7. **Porti petroliferi.**
   - Primorsk è stato colpito il 12/9/2025 e il 23/3, il 5/4 e il 3/5/2026; Reuters stima perso almeno il 40% dello stoccaggio ([Moscow Times](https://www.themoscowtimes.com/2026/03/23/ukraine-strikes-primorsk-port-in-northwestern-russia-damaging-fuel-reservoirs-a92302); [US News/Reuters](https://www.usnews.com/news/world/articles/2026-05-03/russias-primorsk-port-hit-as-ukraine-launches-wave-of-drone-strikes)).
   - Il 14/8/2026 il terminale Šeschacharis di Novorossijsk, con capacità di circa 700.000 b/g, ha sospeso l'export di greggio ([NV/Reuters](https://english.nv.ua/business/russian-oil-exports-from-sheskharis-terminal-halted-after-drone-attack-reuters-50632826.html)).
   - Ust-Luga è stata colpita il 21/1/2024, il 24/8/2025 e nel 2026 il 26/3, il 7/4, il 10/7, il 15/8 e l'1/9.
8. **Omsk, 6/7/2026.** La più grande raffineria russa si è fermata dopo i danni all'unità CDU-10, circa 38% della capacità ([Reuters via Internazionale](https://www.internazionale.it/ultime-notizie-reuters/2026/07/07/russia-s-largest-oil-refinery-halts-processing-after-drone-attack-sources-say)).

## Effetti sulla raffinazione e sull'export russo

- **2024.** Le raffinerie russe hanno lavorato circa 267 milioni di tonnellate, il minimo dal 2012 (Reuters, via [Kyiv Independent 17/1/2025](https://kyivindependent.com/russias-marine-oil-exports-decline-9-1-in-2024-amid-ukraines-attacks-reuters-reports/)). Nel marzo 2024 Gunvor stimava 600.000 b/g di capacità persi ([KI](https://kyivindependent.com/gunvor-russia-has-lost-600-000-barrels-of-daily-oil-refining-capacity-due-to-drone-attacks/)).
- **2025.**
  - Ad agosto 10 raffinerie sono state colpite e il 17% della capacità nazionale, 1,1 milioni b/g, si è fermato. In compenso Mosca ha esportato più greggio da Primorsk, Ust-Luga e Novorossijsk (Reuters, via [KI 27/8/2025](https://kyivindependent.com/russia-boosts-oil-exports-following-ukrainian-strikes-on-refineries-reuters-reports/)).
  - L'export di gasolio è sceso al minimo da 5 anni (FT, via [KI 23/9/2025](https://kyivindependent.com/ukrainian-drone-attack-on-oil-refineries-drop-russian-diesel-exports-to-5-year-low-ft-reports/)).
  - Sull'intero anno, secondo Reuters (novembre 2025, citata da [Wikipedia](https://en.wikipedia.org/wiki/2025%E2%80%932026_Russian_fuel_crisis)), la lavorazione è calata solo del 3% grazie alla capacità di riserva: nel picco tra agosto e ottobre era fuori uso il 20% della capacità, ma il volume è sceso del 6%.
- **2026.**
  - A maggio le raffinerie colpite nella Russia centrale valevano il 30% della benzina e il 25% del gasolio russi (Reuters, via [KI 21/5/2026](https://kyivindependent.com/central-russias-major-oil-refineries-halt-production-following-ukrainian-drone-attacks-reuters-reports/)).
  - A luglio la produzione di benzina era di 75.000–80.000 t/giorno contro una domanda di 115.000–120.000 ([Wikipedia](https://en.wikipedia.org/wiki/2025%E2%80%932026_Russian_fuel_crisis)). A settembre 3 dei 6 principali produttori di gasolio erano fermi o ridotti (Reuters, via [KI 16/9/2026](https://kyivindependent.com/ukraines-drone-strikes-force-russias-6-largest-diesel-refineries-to-halt-or-slash-output-reuters-reports/)).
  - Le stime di capacità fuori uso divergono. Lo Stato maggiore ucraino parlava di 42,7% il 4/7 e di 45% il 21/9; il ministero della Difesa ucraino di «oltre la metà» il 4/10. La IEA a luglio diceva «oltre il 20%». *Le cifre ucraine sono di parte.*
  - Mosca ha vietato l'export di benzina e carburante per aerei e poi, a tratti, di gasolio. A luglio-agosto 2026 importava benzina da India e Marocco e ha autorizzato carburanti Euro-2/3/4.
  - Molin riferisce che Putin ha stimato in circa l'1% del PIL il costo degli attacchi alle raffinerie nel 2026 ([3/10/2026](https://t.me/clement_molin/1835)).

## Collegamenti con i prezzi di gasolio e Brent

- Ho calcolato le chiusure mensili da Yahoo Finance: Brent (BZ=F) e gasolio NY Harbor ULSD (HO=F × 42, in $/barile). Il margine del gasolio, cioè ULSD meno Brent, era di circa 16–22 $/b tra aprile e novembre 2024. È salito a 31–37 $/b tra settembre e novembre 2025, nel pieno della campagna sulle raffinerie, e a 83–105 $/b tra luglio e novembre 2026: 104,7 a settembre e 85,7 a inizio novembre.
- Dal 2024 la correlazione tra il numero mensile di raffinerie colpite (dal mio file) e il margine del gasolio è 0,67; con il Brent è solo 0,35 (30 mesi). **Correlazione non vuol dire causa.** Nel 2026 il Brent e i margini sono spinti soprattutto dalla guerra con l'Iran e dalla crisi di Hormuz: Brent a 114 $ ad aprile 2026. Gli attacchi ucraini incidono più sui **prodotti raffinati** (gasolio, benzina) che sul greggio, perché la Russia può esportare il greggio che non riesce a raffinare.
- Per l'Italia e l'Europa conta il gasolio. La Russia era un esportatore chiave di diesel verso Turchia, Brasile e Africa, e meno export russo significa margini più alti anche nel Mediterraneo. Già a febbraio 2025 l'export russo di diesel verso l'Africa si era dimezzato, da 1,27 a 0,684 milioni di tonnellate (RBC, via [KI](https://kyivindependent.com/russian-diesel-exports-to-africa-reportedly-plummet-amid-ukrainian-drone-strikes/)).

## Fonti OSINT seguite

| Analista | Cosa pubblica | Frequenza | Dove si legge senza login | Raccolta automatica | Come integrarlo |
|---|---|---|---|---|---|
| **Clément Molin** (francese, @clement_molin su X, circa 140.000 follower al 6/11/2026) | Mappe e sintesi: attacchi ucraini a raffinerie e logistica, attacchi russi alla rete, bombe KAB, andamento del fronte, bilanci mensili degli attacchi in profondità (per esempio «ottobre 2026: circa 75 bersagli, 21 energetici»). | Più post al giorno, quasi sempre in inglese. | **Telegram pubblico `t.me/s/clement_molin`**, che rilancia i post di X (circa 1.977 messaggi, molti dal maggio 2026). Anche threadreaderapp.com per i thread. | **Sì**: la pagina `t.me/s/` è HTML statico, impaginabile con `?before=<id>`, leggibile con urllib. Ho scaricato 96 pagine (904 post) senza problemi. Nessun RSS nativo. | Ogni giorno leggere `t.me/s/clement_molin` e filtrare per parole chiave (refinery, airbase, port, substation, KAB). I punti vanno inseriti con affidabilità **media** finché manca una seconda fonte indipendente, tenendo distinti i fatti (luogo, data, foto) dalle valutazioni (strategia, perdite). |
| **AMK Mapping** (@AMK_Mapping_ su X) | Aggregatore di notizie e geolocalizzazioni: Ucraina (impatti dei Geran per località, Banderol, FIRMS sulle raffinerie con coordinate), Medio Oriente, Yemen e Arabia Saudita. Fornisce dati a Molin. | Decine di post al giorno (oltre 40.000 messaggi). | **Telegram pubblico `t.me/s/AMK_Mapping`**. Il Substack `amkmapping.substack.com` ha un solo post segnaposto (13/1/2025). | **Sì**, come sopra; un feed RSS c'è solo per il Substack, vuoto. | Raccolta giornaliera dei post con «Coordinates:» o «FIRMS», che hanno coordinate già pronte. Utile per la notte di attacchi russi (elenco di località colpite) e per confermare gli incendi alle raffinerie. Affidabilità media; alta solo se coincide con FIRMS o con fonti ufficiali. |
| **Davide Montingelli** (grafia verificata: profilo X «Davide Montingelli», @DaviMontingelli; anche su LinkedIn) | Analista militare italiano. Pubblica mappe del fronte (per esempio Dobropillja, Lyman) e analisi; è ospite frequente di altri canali YouTube, come le dirette di Parabellum (Mirko Campochiari, 18/6/2024) e video su Vuhledar e Kupjansk. | Non misurabile da qui. | Solo **X**, che da qui non è leggibile (xcancel 451, nitter RSS 410), e LinkedIn. Il canale YouTube @DavideMontingelli esiste, ma con 4 iscritti e un feed vuoto: i video sono sui canali che lo ospitano. Non ho trovato né Telegram né Substack. | **No**, al momento. | Non ho trovato suoi rapporti accessibili su attacchi in profondità da usare come fonte: non lo cito nei punti. Per integrarlo servirebbe un accesso a X, cioè un'API a pagamento o un mirror che funzioni, oppure il feed RSS dei canali YouTube che lo ospitano, con trascrizione manuale. |

Valutazioni di questi analisti riportate solo come tali:
- Molin, 6/11/2026: nel 2026 il fronte va meglio per Kyiv, con controffensive a Lyman e a sud. La Russia, che non riesce più ad avanzare, punta sugli attacchi in profondità.
- Molin, 20/9/2026: nel 2026 i guadagni russi netti sono di circa 650 km², contro 1.900 nello stesso periodo del 2024 e 3.100 nel 2025.
- Sono valutazioni, non fatti verificati: andrebbero confrontate con `fronte.json`.

## Collegamenti con gli altri livelli della mappa

- **Oleodotti (`linee.json`).** Unecha, sul Druzhba, colpita il 13 e il 21/8/2025 con forniture a Ungheria e Slovacchia sospese fino al 28/8 ([Reuters](https://www.reuters.com/business/energy/ukrainian-attack-suspends-russian-oil-flows-hungary-slovakia-2025-08-22)). Altri nodi: Kavkazskaja, sul CPC (19/3/2025), Prosvet e Vtorovo, che riforniscono Mosca.
- **Stretti e porti (`stretti.json`, `fissi.json`).** Il Bosforo per l'export da Novorossijsk, Tuapse e CPC (con greggio kazako); il Baltico e gli stretti danesi per Primorsk e Ust-Luga. A luglio 2026 la Russia ha sospeso la navigazione civile nello stretto di Kerč e nel canale Don–Azov dopo gli attacchi alle petroliere (Wikipedia, crisi dei carburanti).
- **Mercati (`prezzi.json`).** Brent e, soprattutto, margini del gasolio; il TTF solo indirettamente.
- **Eventi (`eventi.json`).** I punti hanno `classe: evento` e i campi data, fonte e affidabilità compatibili.

## Proposta per la mappa

- Livello **«Attacchi ucraini all'energia russa»**: cerchi colorati per categoria (raffineria, porto, deposito, pompaggio, base aerea). Il raggio cresce col numero di attacchi allo stesso impianto, l'opacità dipende dall'affidabilità, e un cursore temporale usa `data_evento`. Al clic: elenco degli attacchi all'impianto con fonte e link.
- **Pannello Ucraina**: grafico a barre mensile dei lanci (droni e missili impilati) con la linea della percentuale di abbattimento. Va segnata la discontinuità di agosto 2025 e vanno indicati i mesi con cifre non divulgate. Sopra, segnaposto per le 18 ondate contro la rete.

## Limiti

- **Dal 24/2 al 27/9/2022 i lanci russi non sono coperti:** il dataset parte dal 28/9/2022.
- Le cifre dei lanci e degli abbattimenti sono dichiarazioni dell'Aeronautica ucraina, non verificate da terzi. Le categorie di conteggio cambiano nel tempo (droni persi per guerra elettronica, esche, cifre nascoste dal 13/8/2026). I gruppi per tipo sono miei: i modelli riportati insieme (per esempio «Kh-101 and Kalibr») finiscono in «missili misti».
- **Gli attacchi ucraini non sono esaustivi:** secondo una stima CNN di giugno 2026 gli attacchi a impianti petroliferi sono oltre 300, il file ne ha 258 e include anche le basi aeree. Mancano soprattutto febbraio–luglio 2025 e i molti attacchi a depositi minori. La data è quella dell'articolo o del rapporto (notte dell'attacco ±1 giorno). L'esito automatico può riprendere frasi di contesto.
- Molte coordinate sono del centro abitato (10–30 km): `origine_coord` e `precisione_km` lo dicono punto per punto.
- Reuters, AP, ISW ed Euromaidan Press non sono leggibili direttamente da qui; li cito tramite ristampe.
- La copia R2 del dataset è di un progetto terzo. Se sparisce, lo script passa alla copia GitHub (più vecchia). Con una chiave Kaggle gratuita (`KAGGLE_USERNAME` e `KAGGLE_KEY`) usa la fonte originale.
