# Agente NOTIZIE OSINT: rapporto

Data: 2026-11-09. Script: `raccolta/notizie/raccogli.py` (solo libreria standard, nessuna chiave). Elenco fonti: `raccolta/notizie/fonti.json`. Eseguito davvero più volte il 2026-11-09 (ultimo giro 19:48 UTC, circa 65 secondi, 35 fonti, 0 errori). Produce `docs/data/notizie.json` (512 notizie, circa 600 KB).

Tutto quello che c'è in questo file è **materia prima da verificare**. Lo script non copia gli articoli: tiene solo il titolo, un sommario di al massimo 400 caratteri (quando il feed lo dà) e il link.

## 1. Fonti provate

Legenda: **funziona** = letta direttamente; **indiretta** = sito bloccato, titoli letti con una ricerca Google News RSS (`site:` o parole chiave), con il link che passa da news.google.com; **bloccata** = 403/Cloudflare; **a pagamento** = solo titolo.

### Sicurezza marittima
| Fonte | Esito | Note |
|---|---|---|
| UKMTO (ukmto.org, incidenti e avvisi) | bloccata (Cloudflare) → **indiretta** | ricerca "UKMTO": 26 articoli in 7 giorni che citano gli avvisi |
| JMIC (note su ukmto.org) | bloccata → **indiretta** | 8 articoli |
| MARAD, avvisi MSCI (maritime.dot.gov) | bloccata (403) → indiretta | nessun avviso nuovo negli ultimi 30 giorni tra i titoli trovati |
| NATO Shipping Centre (shipping.nato.int) | bloccata (403) → indiretta | 0 risultati: nessuna copertura utile |
| IMB Piracy Reporting Centre (icc-ccs.org) | pagina non trovata (404) → indiretta | 4 articoli su pirateria e ReCAAP |
| gCaptain, The Maritime Executive (RSS) | **funziona** | |
| USNI News (RSS) | **funziona** | anche il Fleet Tracker settimanale |

### Conflitti e OSINT
| Fonte | Esito | Note |
|---|---|---|
| ISW (understandingwar.org) | bloccata (403) → **indiretta** | arrivano i titoli dei rapporti giornalieri (Russian Offensive Campaign Assessment, Iran Update, mappe del terreno) |
| Kyiv Independent (RSS) | **funziona** | `/news-archive/rss/` |
| Meduza in inglese (RSS) | **funziona** | |
| Al-Monitor (RSS) | **funziona** | |
| Times of Israel | RSS bloccato (403) → **indiretta** | 100 titoli al giorno: tengo solo quelli con un tema |
| Jerusalem Post (RSS) | **funziona** | alternativa diretta a Times of Israel |
| Oryx (Blogger/Atom) | **funziona** | aggiorna di rado: 0 post negli ultimi 7 giorni |
| Clément Molin | **funziona via Thread Reader** (threadreaderapp.com/user/clement_molin) | è solo su X; il Substack esiste ma è vuoto; nessun canale Telegram trovato. 1 thread negli ultimi 7 giorni (3 novembre) |
| AMK Mapping | **funziona** su Telegram (t.me/s/AMK_Mapping) | il Substack è vuoto |
| BBC World, Al Jazeera (RSS) | **funziona** | utili come seconda fonte |
| AP News | RSS bloccato (403) → **indiretta** | |
| IAEA (RSS) | **funziona** | il feed non ha date: le voci restano "senza data della fonte" |

**Canali Telegram (letti come HTML da t.me/s/...) e affidabilità dichiarata**
| Canale | Affidabilità | Perché |
|---|---|---|
| AMK Mapping | media | mappatore indipendente, elenca bersagli e usa dati NASA FIRMS; riprende anche fonti di parte |
| DeepState (DeepStateUA, in ucraino) | media (alta sui cambi di linea) | è il progetto che pubblica deepstatemap.live; è di parte ucraina |
| WarTranslated | media | traduce fonti ucraine e russe: buono per le dichiarazioni, meno per i fatti sul terreno |
| Scartati: Rybar in English (propaganda russa), OSINTdefender (aggregatore veloce con errori), Military Summary (commento filorusso) | — | funzionano, ma non li uso |

### Energia e logistica
| Fonte | Esito | Note |
|---|---|---|
| EIA Today in Energy (RSS) | **funziona** | |
| OilPrice (RSS) | **funziona** | affidabilità media: titoli enfatici |
| Splash247, Hellenic Shipping News, LNG Prime (RSS) | **funziona** | Hellenic ripubblica testi di terzi |
| Lloyd's List | RSS bloccato e **a pagamento** → indiretta | solo titoli |
| Reuters | feed ufficiale chiuso (502) → **indiretta** | articoli spesso a pagamento: solo titolo |

### Macro e banche centrali
| Fonte | Esito | Note |
|---|---|---|
| Federal Reserve (press_all.xml) | **funziona** | |
| BCE (rss/press.html) | **funziona** | |
| Bank of England (rss/news) | **funziona** | |
| Banca d'Italia | nessun RSS (404) → **pagina HTML dei comunicati** | solo la data, senza ora |
| OPEC (opec.org) | bloccata (403) → indiretta | pochi titoli e generici: per l'OPEC servono Reuters e OilPrice |

**Licenze.** Le notizie appartengono agli editori. Le usiamo come segnalazione (titolo, sommario breve e link) per un progetto personale e non commerciale. I dati di Fed, EIA e IAEA sono pubblici. Il passaggio da Google News è un uso non ufficiale e non garantito.

## 2. Cosa contiene `docs/data/notizie.json`

Il formato è quello di AGENTI.md (`aggiornato`, `fonti`, `nota`, `elementi`, `errori`). In più ci sono `riepilogo`, `stato_fonti` (esito di ogni fonte a ogni giro) e `in_evidenza` (gli id delle 25 storie con punteggio più alto delle ultime 48 ore, una per gruppo).

Ogni notizia contiene:
- **Dati di base:** `id`, `titolo`, `data_utc`, `data_fonte`, `link` (più `link_x` per i thread di X), `fonte`, `via` (per Google News), `editore` (dominio), `famiglia`, `lingua`, `affidabilita`, `sommario` (al massimo 400 caratteri), `stato` (sempre "da verificare").
- **Classificazione:**
  - `temi`: 17 temi a parole chiave (inglese, italiano, più qualche parola ucraina e francese): hormuz, mar_rosso_houthi, ucraina_fronte, guerra_iran, attacchi_energia, droni_missili, cavi_sottomarini, sabotaggi_ibrido, flotta_ombra_sanzioni, gnl_gas, petrolio, banche_centrali, sicurezza_marittima, nucleare, logistica_noli, elettricita_blackout, diplomazia_negoziati.
  - `luoghi`: fino a 6 toponimi di `labels.json` (paesi, città, stretti, mari, regioni), con nomi inglesi e ucraini tradotti nei nomi di `labels.json`.
  - `lat`, `lon`, `precisione_km` e `origine_coord`: vengono dal luogo più preciso citato nel titolo. La precisione dichiarata è 15 km per una città, 50 per uno stretto, 100 per una regione, 300 per un mare e 500 per un paese. **È il centro del toponimo, non il punto del fatto.**
  - `paese` (ISO2) e `teatro` proposto (RU-UA, MO, NATO).
- **Eventi:**
  - `possibile_evento`: il titolo contiene un verbo da evento (attacco, sequestro, esplosione o incendio, sabotaggio, chiusura, blackout, intercettazione, avanzamento, incidente, ibrido), tocca un tema operativo e non sembra un'analisi o una notizia di mercato.
  - `categoria_proposta` e `motivi_evento`.
  - `forse_gia_in_mappa`: id degli eventi di `eventi.json` e `ibrido.json` entro ±2 giorni, vicini al punto o con lo stesso nome proprio. I due file vengono solo letti, mai modificati.
- **Doppioni e gruppi:**
  - Le notizie con lo stesso titolo normalizzato vengono tolte; gli altri editori finiscono in `anche_su`.
  - `gruppo` unisce titoli simili (Jaccard ≥ 0,4 entro 2 giorni) e `n_editori_gruppo` conta gli editori diversi del gruppo.
  - `punteggio` serve solo per ordinare.

**Finestra.** Il file tiene 7 giorni. A ogni giro unisce le notizie del file precedente e ricalcola la loro classificazione con le regole aggiornate.

## 3. Numeri di oggi (giro delle 19:48 UTC del 9 novembre)

| Famiglia | Oggi (9 nov, UTC) | Ultime 24 ore | Ultimi 7 giorni |
|---|---|---|---|
| Conflitti e OSINT | 135 | 144 | 234 |
| Energia e logistica | 114 | 117 | 139 |
| Sicurezza marittima | 26 | 32 | 125 |
| Macro e banche centrali | 0 | 0 | 14 |
| **Totale** | 275 | 293 | 512 |

Altri numeri del file:
- Possibili eventi: 76, di cui 49 forse già in mappa.
- Notizie con coordinate: 337. Notizie senza data della fonte (IAEA): 15.
- Temi più frequenti: guerra_iran 80, petrolio 57, hormuz 41, droni_missili 34.

## 4. I 10 fatti più rilevanti delle ultime 48 ore (tutti da verificare)

Sono ordinati per peso geoeconomico. Il "forse in mappa" viene dal campo `forse_gia_in_mappa`.

1. **Hormuz, petroliere in fiamme (8–9 nov).** L'Iran dice che 3 petroliere hanno preso fuoco nello stretto; Al Jazeera scrive che l'IRGC le ha colpite per i loro "legami con gli USA". Un avviso UKMTO, ripreso dai media, segnala una petroliera in fiamme al largo dell'Oman con l'equipaggio evacuato.
   - Fonti: [Times of Israel](https://news.google.com/rss/articles/CBMikAFBVV95cUxQckxoUkQ3Qmd6U2tuNzdRMDh2MXF3S3RoTjlxWFFQN1pYVFllM3g1dFNQelRaZjlXaWxaaExGU21QbDBxOF80dnBEdjBIX1JUTFhyS1R3ME9NeEUtQklET251dl9QOG1XLTF3MGF2SF9JWDMtSldRTmNiRWplVUJkLXdCYXZoV0hHT0JBV2ZoWDA?oc=5), [Al Jazeera](https://www.aljazeera.com/video/newsfeed/2026/11/9/irgc-strikes-three-tankers-near-hormuz-over-us?traffic_source=rss), [Maritime Executive](https://maritime-executive.com/article/tanker-burns-after-strike-in-strait-of-hormuz).
   - Gruppo UKMTO: 5 editori. Forse in mappa.
2. **Gli USA colpiscono una portarinfuse che forzava il blocco all'Iran, Golfo di Oman (7–8 nov).** UKMTO segnala un "incidente con forze militari" a est di Khor Fakkan. Lloyd's List la chiama "nuova escalation".
   - Fonti: [AP](https://news.google.com/rss/articles/CBMirAFBVV95cUxQeW5HVVl6cDF0V1htbGY0eU9zSmtxbjdEOW9ETW02b0JLVlJwSW1oODJBSDRFOXBrMXpfRElCa0NXeHdrUTlUYlo2MmZadHFZellGd2dkUFNyWG5BNy1INUhwa3hGRDRMX3hIcFpFMmRzdEtGRjJSUXZJTXZ1OHV5QjlSTUJvOW9mTURuX0wwVDRyQkRyR2tZaDhCRjZZTHpnZmFoSnpHRDZ5R01r?oc=5) (alta), [Lloyd's List](https://news.google.com/rss/articles/CBMirgFBVV95cUxNTU5leHNTdmExcGhfaUMxNEhubXR4TjFlckdUQmFnU1RwcWJIM3NSeDRIN3V4MzhQdThjR25zOXNKN2g4cU02azNyWXZocS0tdVJOTlR5V1FrQW1weTd6MmZWSXktWlFXbVdaOFBJc1ExSElZdFVCZ2xtemFmbzFsNzFFbXNma1RMOV9TeldxcVhtMzVXVUpyaXB6U1luRC1NYXFCOHJ4NUI5Vm5uUGc?oc=5) (alta), [Middle East Eye su UKMTO](https://news.google.com/rss/articles/CBMiwAFBVV95cUxPall0VFBlZEttLW92R3VZeVc3UW9HaGtnbGVIVEpyWGxEcGxaRkRMMXhPTzhVNDBqZ2llbkVLelYyR0llU2tjR09uTmlvbWg2dDNzdk9FMDJCemRWTG8zTlZ3ekpFUW1ITHk2YTlOZjl4VVpaYzZnQU5xS1dtX1FyUnFXTEtxM0VEc2xQYVJPanZsbjBhYUVwSC1wUHNkUU9RdEhJOFdTbkJETWEwMXluZUxOaW85dS11blN0YTBzLU4?oc=5) (gruppo di 8 editori).
   - Da controllare se è la stessa nave dell'incendio con **22 marittimi salvati dagli Emirati** vicino a Khor Fakkan (8 nov, solo fonti di affidabilità bassa).
3. **Attacco houthi a Riad: danneggiato un edificio di Saudi Aramco nel quartiere finanziario (8 nov).** I sauditi dicono di aver intercettato missili da crociera.
   - Fonti: [Reuters](https://news.google.com/rss/articles/CBMiwgFBVV95cUxOMEd1Mi1tMEV0cUFGYkd2V01lQ1NkczNNYzZXTlpTOXByR3BaSk82N21DOEpTeEtNMlJ1bFJ3S2pLTVZBOUp5cDFwOUpGakNxMTR1a2RyaHJBcDNOZUJqR1dDZllfejBPWGZ3UVYyT2s3Uk9XaFE3LW1qQkxtNHhlcmFRcGk0bDlWeHZyQmNNOEJyT1lWeVZlTEJlZ0xpRHF6UUs0RnRTWExlbEJ4eDc4YTY4d0VfM2x3dllKUGhZa1Z4QQ?oc=5), [AP](https://news.google.com/rss/articles/CBMikgFBVV95cUxOU1hPV0p1dkZfcU92OEJVMkYtQTNHb3hKSDdGZHp5U1RkUTZlc2dzTU9oNjQ4dk5nUGZ6WVhkTlk2VTJ0cFkxOHozbE9aWUJObXFUYVBCZEwtaktnOGExQjVfUlhNdFlxRV9KeHMzS1Rsc2c3OFAxNHF6RjM2X0FRamhCalJsTk1BY1g2NFhHX2ZnUQ?oc=5), [Maritime Executive](https://maritime-executive.com/article/houthi-forces-hit-saudi-aramco-s-headquarters-building).
   - Due agenzie indipendenti: candidato ad "alta". Forse in mappa.
4. **Iraq: il giacimento di gas di Khor Mor (Kurdistan) è fermo dopo un attacco di droni (8 nov).** La notizia viene dall'operatore.
   - Fonti: [Reuters](https://news.google.com/rss/articles/CBMixwFBVV95cUxOSjc4dFNBUmN3UHp3Uk5FLUhNOElWeTVLRDNzSHZsSTAyUWZ4elN0eHdYUVJ5MDZBb0Y3MDNaNzlWbTRHMnctUFY5dGdNWWtKUnZTdHRPeXl1UUhlUE9mdTU0d2ZWTk9Hak9HaHVXaVBJQ3BoVXdfZnFxelF2aUc1MEV1U0JFQ1lDQ0s3RXhtRnk2dmoxZ2h4a3FRazE4Y3VpbGlDYW1zdE1DcDYxU3R4aE9zOWxkdTNuRVFxMzRlTDEtMDNHRmpr?oc=5), [Times of Israel](https://news.google.com/rss/articles/CBMiwwFBVV95cUxPWUh1cHgxb2FTTnlvRWFURE54S1BVdHhsaFJYX1lBNW0yYnNhVjdRdFBzSktBeWJab3M1OHdDZTFKV1dzd0Q5Rl9ENVpCZVR2ZkZVQUk2VTY0eHJzTUtqdlJmNnREMHJJajJ2ZzN6cjFRX29vZC1FdDJUWHhpWS0ydGRRRHh3YS1yTzlWYnVFdnM2c3RGandOaUc4aURaLTYzdi1Sc1Rlby13ZU80U29FTG1RSHBtYk1seW5OOENQMWoxY28?oc=5).
   - Forse in mappa (X-20261108-04).
5. **Qeshm (Iran): esplosioni sull'isola nello Stretto di Hormuz (7–8 nov).** Un funzionario iraniano dice che sono attacchi USA, senza danni gravi alle infrastrutture.
   - Fonti: [Reuters](https://news.google.com/rss/articles/CBMisAFBVV95cUxObzVlZDVLRWxGVlQ1a2V1cTY5NXBjcjlJVzVqbjBKRGpRLUpnWndzNlM5bFpUYjJaUU5UeG1OS2E3c205RVVNMDJaUWxoWFN2ODc1bVhnc096VFlpOFo1N1YwR2JGS2JQYURyQ3NHZEVZaFhvQU5IaWZ1VFZHRjZNTkstbVhiOTUyTDJKTjAySmE0N3FiUzZLUGJKdDdrcGllOTNmMEdHUC1DanlqZ3V5MA?oc=5) (esplosioni nel sud dell'Iran secondo i media iraniani), [Times of Israel](https://news.google.com/rss/articles/CBMiwgFBVV95cUxQdXcwRjNZQ0lsdHZMaDVmdURqOTk2bDQ0SFlLQjBGdkxQZmt6VmtDRTkzTUdLUTliRmYtLTdITGVpQkVPRzU3bmRObTBHcDhsX1lCY2IwMU1Ba3hzOXloQ1NQaHkwdWVFR3RlYnI3TXBOWm9Eakd5TUtCdXJoVzkwSTlHUEd6SnM0WmZJSTRxN2ItSWV6SU04d0pTUFVLaTkxdDJuMm9JN3hxdVlZc2JiN2d2QzlZaGVPZVdfelUyMFJTdw?oc=5).
   - Le fonti primarie sono iraniane: "media" finché non c'è una conferma indipendente.
6. **Raffineria di Kirishi (regione di Leningrado) colpita da droni ucraini nella notte tra l'8 e il 9 novembre.**
   - Ci sono incendi visibili nei dati NASA FIRMS. Lo stesso giorno la regione raccomanda di limitare la vendita di carburante.
   - Fonti: [Meduza](https://meduza.io/en/news/2026/11/09/ukrainian-drones-strike-russia-s-leningrad-region-sparking-fire-at-one-of-the-country-s-largest-oil-refineries), [AMK Mapping](https://t.me/AMK_Mapping/40470), [Reuters sulle carenze di carburante](https://news.google.com/rss/articles/CBMivwFBVV95cUxPcnFSWF9iWmo0LUNjUmNYMVVKYzBwNVlJdlJsbVkxWnJ1Z2NYckF0OFFFdUNwdVZqd1VESWdzbEdRQmF6VGliV0tpYmVvNE9nS2l5LVczdWNhVXZjT0hTTTlnMzNIWnV2LS1nQWNKRGlYNzdUMkV1V3NabzVNUkhmWENLblNYRGJCUTJhMEVXU1dYXzU2Z1YxdTUycDZqNEFVbGRJZVlKOS0zaEcwVEdOZWZCbTR5VFIzaGhWZGZFZw?oc=5).
   - Forse in mappa (X-20261109-01).
7. **Lo Stato maggiore ucraino rivendica due attacchi (9 nov):** un impianto di San Pietroburgo che produce carburante per missili e una stazione russa di disturbo delle comunicazioni satellitari.
   - Fonte: [Kyiv Independent 1](https://kyivindependent.com/ukraine-strikes-st-petersburg-plant-producing-missile-fuel-general-staff-says/), [Kyiv Independent 2](https://kyivindependent.com/ukraine-strikes-russian-satellite-communications-jamming-station-general-staff-says/).
   - È una sola fonte, che riporta una rivendicazione governativa.
8. **Mar Nero: Mosca dice di aver colpito tre navi mercantili e sottostazioni elettriche in Ucraina (8 nov).** Secondo Lloyd's List l'attività navale nel Mar Nero è crollata.
   - Fonti: [Reuters](https://news.google.com/rss/articles/CBMiqAFBVV95cUxPN3I3aVRlN2tQellIUkRxQVR6VFhUWkRfZlJQUWsyR3g0S0w2Wlg1cUt6SW9fc081c1hfcTdPSTJwZzJIWUVtQXN1SVJiRm9zTWJKYjM2RTV3TWVBa001Y1RmeVhEOHVnb3pCSUt5T3BxU19VeDhXNGdmNkg0SlNHUWszcHI3X1hsbjJiWFN5MXlEcHdVM21wNTJrRHlVeTFQZl9CYlRwMmY?oc=5), [gCaptain](https://gcaptain.com/russia-says-it-hit-three-cargo-ships-in-black-sea/).
   - Rivendicazione russa: servono i nomi delle navi.
9. **Ondata russa sull'energia ucraina (7–9 nov).**
   - Secondo AMK Mapping: oltre 1.000 droni Geran in 72 ore, sottostazioni colpite nella regione di Dnipropetrovsk (Dnipro, Kryvyi Rih) e un missile S8000 Banderol sull'hotel "Pantagruel" di Kremenchuk.
   - AP scrive che i due paesi "si colpiscono a lunga distanza alla vigilia dei colloqui mediati dagli USA".
   - Fonti: [AMK 1](https://t.me/AMK_Mapping/40471), [AMK 2](https://t.me/AMK_Mapping/40474), [AP](https://news.google.com/rss/articles/CBMilAFBVV95cUxOSzJmdDczN2hxRVpiY0V5UzZWZlFBR3oxaUlhWW96SzNvUEcxd3Q5clI3M1FXUTZqMkF5dmpZV29xdjFZV1hBNDZpeXVwalQ4X1lISlZGY1lIWVZ2UXpYUUExQXl0aVlZazNycEFHQ25xclZiNHQyOW5nWlFoYlFPU3VyeTZwa0hPUkNMeTJ5ck9UVk95?oc=5).
   - Il numero di droni è di AMK e non è verificato.
10. **La Francia attribuisce all'IRGC iraniano il cyberattacco di ottobre ai frigoriferi dei supermercati (9 nov)** e chiede sanzioni UE. È un evento ibrido in Europa.
    - Fonti: [AP](https://news.google.com/rss/articles/CBMirgFBVV95cUxQX3MxdFVOdmN3Y2lHVWlZVHRIdjJLbElKcTl6YnN0N3RwZXZXalAySVdselJLaEVMSXp5Q3MzVU9UNWxBSmhMWXJCYzF2bV94bEgzM0x2UUpwbS1CWUgtaDBpVmEwRTluSGNtVlE1N2QyWTJURWg5OUpFTy1WQm41RWEyYUxfWXhoZjVEUVNVbldOX3UySFh1VjctSWNqN0NPaTMwVlprWF82UVg0OVE?oc=5), [BBC](https://www.bbc.co.uk/news/articles/cmg474vk6dyqo), [Al-Monitor](https://www.al-monitor.com/originals/2026/11/france-blames-iran-supermarket-fridge-hack-seeks-eu-sanctions) (gruppo di 4 editori).
    - L'attacco è già in `ibrido.json`; l'attribuzione è nuova.

Da tenere d'occhio, perché vengono da una sola fonte:
- "Saudi Pipeline Attacked" ([OilPrice](https://oilprice.com/Latest-Energy-News/World-News/Saudi-Pipeline-Attacked-as-OPEC-Output-Climbs-to-90-of-Pre-War-Levels.html), 9 nov), da incrociare con Reuters o Aramco.
- DeepState (8 nov): "il nemico è avanzato vicino a Luhivske" ([t.me/DeepStateUA/23984](https://t.me/DeepStateUA/23984)), da confrontare con ISW.
- Per la macro: la Bank of England ha alzato il tasso al 4% ([BoE, 5 nov](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/november-2026)).

## 5. Proposta per il coordinatore: dalla notizia all'evento verificato

1. **Ogni giorno** lancia `raccogli.py` (circa 1 minuto) e legge `in_evidenza`, poi le notizie con `possibile_evento: true` delle ultime 48 ore.
2. **Prima di tutto controlla `forse_gia_in_mappa`.** Se l'evento esiste già, aggiunge la nuova fonte a `fonti[]` e `ids[]` dell'evento invece di crearne un altro. La regola è larga (±2 giorni, stesso posto o nome): conferma sempre a mano.
3. **Affidabilità, con la regola delle due fonti indipendenti:**
   - **alta** = almeno **due fonti indipendenti**, di cui almeno una primaria o di alta affidabilità. Fonti primarie: avviso UKMTO, MARAD o JMIC, comunicato ufficiale, operatore dell'impianto, foto o video geolocalizzati, dati satellitari FIRMS o Sentinel. Fonti alta: Reuters, AP, BBC, Lloyd's List, ISW.
   - **Indipendenti** vuol dire editori diversi che **non** riprendono la stessa agenzia. Due articoli che citano entrambi "Reuters" o "UKMTO says" valgono una fonte sola, quella originale. `n_editori_gruppo` è solo un indizio, non una prova.
   - **media** = una sola fonte affidabile, oppure due fonti della stessa parte (per esempio Stato maggiore ucraino e Kyiv Independent).
   - **bassa** = solo Telegram o aggregatori, solo rivendicazioni di una parte in guerra, oppure un titolo senza dettagli.
   - Le rivendicazioni (per esempio "Russia says", "General Staff says", "Iran says") restano "media" anche se le riprendono molte testate, finché non arriva un riscontro indipendente: immagini, FIRMS, operatore, terza parte.
4. **Coordinate.** `lat` e `lon` di `notizie.json` indicano solo la zona (precisione da 15 a 500 km). Per l'evento il coordinatore cerca il luogo esatto nell'articolo o nell'avviso (per esempio "X miglia nautiche a est di Khor Fakkan") e scrive `origine_coord` e `precisione_km` veri. Le notizie con precisione da paese (500 km) non vanno in mappa così come sono.
5. **Mappatura dei campi verso lo schema di `eventi.json`:**
   - `categoria_proposta` → `categoria`. Le voci "ibrido" e "sabotaggio" vanno in `ibrido.json`.
   - `teatro` → `teatro`.
   - `data_fonte` → `data_fonte`. `data_evento` va letta nel testo: spesso è il giorno prima.
   - `link` → `fonti[]`. Per le voci di Google News conviene aprire il link e salvare l'URL finale dell'editore.
   - `breve` → titolo in italiano di al massimo 6 parole.
   - L'id resta quello del coordinatore (per esempio `NZ-AAAAMMGG-nn`), con `ids` che puntano agli `id` di `notizie.json`.
6. **Escludere:** analisi, rubriche di mercato e notizie senza un fatto datato e localizzabile. Restano nel file come contesto per i report giornalieri.

## 6. Collegamenti con gli altri livelli della mappa

- Le notizie con i temi `hormuz` e `mar_rosso_houthi` sono legate a `stretti.json`, `rotte.json` e ai noli.
- `attacchi_energia` è legato a `linee.json` e ai terminali; `cavi_sottomarini` a `cavi.json`.
- `banche_centrali` e `petrolio` si collegano a `prezzi.json` e al calendario.

Sulla mappa si potrebbe aggiungere un pannello "Notizie da verificare": un elenco filtrabile per famiglia e tema, dove il clic sul toponimo centra la mappa. Non metterei punti finché il coordinatore non li ha verificati.

## 7. Limiti

- **Siti bloccati.** UKMTO, MARAD, NATO Shipping Centre, ISW, Times of Israel, AP, Lloyd's List e OPEC non sono leggibili da qui: arrivano solo attraverso Google News.
  - Google News limita le richieste: a volte risponde 503. Lo script fa una richiesta ogni 4 secondi e riprova dopo 30.
  - I suoi link sono reindirizzamenti, non l'URL dell'articolo.
  - Su GitHub Actions gli indirizzi sono diversi e alcuni siti bloccati qui potrebbero funzionare: lo stato di ogni fonte si vede in `stato_fonti`.
- **Classificazione grezza.** Temi e luoghi sono assegnati con parole chiave, quindi ci sono falsi positivi. Ho escluso a mano le città di `labels.json` che sono anche parole comuni (per esempio Duma, Batman, Victoria, Medina, Tripoli). I luoghi minori, come Kirishi o Khor Mor, non sono in `labels.json` e quindi restano senza coordinate.
- **Gruppi prudenti.** Unisco solo titoli molto simili: la stessa storia raccontata con parole diverse resta in gruppi separati (per esempio Kirishi su Meduza e su AMK). Il conteggio delle fonti indipendenti va fatto a mano.
- **Telegram.** L'anteprima t.me/s/ mostra solo gli ultimi 15–20 messaggi: lo script va lanciato almeno una volta al giorno, ma l'unione con il file precedente evita di perdere notizie. DeepState è in ucraino e per ora non traduco i messaggi.
- **Date.** IAEA non ha date nel feed e la Banca d'Italia dà solo il giorno, senza ora (`solo_data`).
