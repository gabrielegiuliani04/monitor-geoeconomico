# Agente DATI PAESI: rapporto

Aggiornato il 9 novembre 2026. Script `raccolta/paesi/raccogli.py` (solo libreria standard, circa 10 minuti, quasi tutti per le pause imposte da UN Comtrade). Eseguito due volte, la seconda dopo le correzioni descritte sotto. File prodotto: `docs/data/paesi.json` (circa 350 KB), 33 paesi, `errori: []`.

## Fonti provate

| Fonte | Esito | Licenza | Cosa dà |
|---|---|---|---|
| FMI DataMapper API (WEO ottobre 2026) | **funziona**, senza chiave. Ogni chiamata restituisce tutti i paesi, una per indicatore | Termini FMI: riuso con citazione | crescita, inflazione, debito pubblico/PIL, partite correnti/PIL (2025 e previsione 2026); PIL e popolazione di Taiwan |
| World Bank API v2 | **funziona** | CC BY 4.0 | PIL in USD, popolazione, dipendenza energetica dei paesi non coperti da Eurostat (EG.IMP.CONS.ZS, 2024) e, come riserva, spesa militare |
| SIPRI Milex xlsx (`SIPRI-Milex-data-1949-2025.xlsx`) | **funziona**. Lo script cerca da solo il file dell'anno più recente | Uso libero **non commerciale** con citazione (non CC): va bene per questo progetto | spesa militare in USD correnti e in % del PIL, fino al 2025 |
| Energy Institute Statistical Review (sito) | **non funziona**: risponde 403 al download diretto | – | – |
| Our World in Data, energy-data (GitHub) | **funziona**: copia degli stessi dati Energy Institute | CC BY 4.0 (OWID); dati di base dell'EI | produzione e consumo di petrolio e gas in TWh, fino al 2024 |
| EIA international API v2 | **serve una chiave** (`EIA_API_KEY`); la DEMO_KEY esaurisce subito il limite di chiamate. Lo script la salta con un avviso | Pubblico dominio | se c'è la chiave: produzione ed export di greggio in migliaia di barili al giorno |
| Eurostat `nrg_ind_id` | **funziona** | CC BY 4.0 | dipendenza dalle importazioni (totale, gas, petrolio, carbone) per UE, NO, UK, TR e UA, fino al 2024 |
| UN Comtrade, API pubblica di anteprima | **funziona senza chiave**, ma lenta: 1 periodo per chiamata, massimo 500 righe, errori 429 | Termini UN Comtrade: consultazione libera e riuso con citazione | principali partner commerciali, export e import di greggio (HS 2709), GNL (271111) e gas via gasdotto (271121), fornitori di greggio e GNL |
| Rating sovrano | **nessuna fonte aperta**: S&P, Moody's e Fitch sono proprietari | – | campo `rating_sovrano: null` |

## Cosa contiene `paesi.json`

Lo schema comune è `{aggiornato, fonti, nota, elementi, errori}`. Ogni elemento contiene:

- `paese` (ISO2), `iso3`, `nome` in italiano;
- `indicatori`: ogni voce è `{valore, anno, fonte, link, unita, nota}`.
  - **Economia:** `pil_usd`, `pil_usd_previsione`, `crescita_pil(_previsione)`, `inflazione(_previsione)`, `debito_pubblico_pil(_previsione)`, `partite_correnti_pil(_previsione)`, `popolazione`.
  - **Difesa:** `spesa_militare_usd`, `spesa_militare_pil`.
  - **Energia:** `petrolio_produzione`, `gas_produzione`, `petrolio_consumo`, `gas_consumo` (in TWh), `dipendenza_energetica`, e per i paesi Eurostat anche `dipendenza_gas`, `dipendenza_petrolio`, `dipendenza_carbone`.
  - **Commercio:** `export_merci_usd`, `import_merci_usd`, `partner_export`, `partner_import` (primi 5, con quota). Poi `export/import_greggio`, `_gnl`, `_gas_gasdotto` (USD e tonnellate), `fornitori_greggio`, `fornitori_gnl`.
  - **Esposizione a Hormuz:** `quota_greggio_golfo_persico` e `quota_gnl_golfo_persico` come `{min_pct, max_pct}`. Il minimo conta Iraq, Kuwait, Qatar, Bahrein e Iran, che non hanno uscite alternative. Il massimo aggiunge Arabia Saudita ed Emirati, che possono aggirare lo stretto in parte da Yanbu e da Fujairah. L'Oman è escluso. La quota non viene calcolata per i produttori del Golfo.
  - **Rating:** `rating_sovrano: null`.
- `serie`: ultimi 10 anni (2016–2025) di `pil_usd` (miliardi), `crescita`, `inflazione` e `spesa_militare_usd` (miliardi), con data convenzionale `AAAA-12-31`;
- `buchi`: l'elenco di ciò che manca per quel paese.

## Buchi nei dati

- **Taiwan:** non è nella World Bank. PIL e popolazione vengono dall'FMI. La dipendenza energetica manca (né Eurostat né World Bank la coprono). In Comtrade compare come "Other Asia, nes" (codice 490).
- **Il codice 490 nei dati degli esportatori del Golfo:** per Arabia Saudita (49,6% dell'export 2025) e Iran (21,7%) vale come "Taiwan", ma quasi certamente comprende destinazioni riservate. Il JSON lo segnala in una nota.
- **Comtrade, paesi assenti:** Russia e Libia non riportano dati dal 2023. Emirati e Iran sono fermi al 2023, Iraq, Qatar e Algeria al 2024.
- **Destinazioni riservate:** Iraq e Kuwait dichiarano i partner solo per il 4% e il 12% dell'export; il resto risulta "aree non specificate". Per questo i dati sui partner sono più affidabili dal lato degli importatori.
- **Origine del GNL tedesco** non dichiarata (100% "Areas nes"). La Turchia non ha voci utili sui fornitori di greggio.
- **Iran:** probabilmente sottostimato nei fornitori della Cina. Il greggio iraniano viene spesso dichiarato come malese: la Malesia risulta al 10,5% dell'import cinese.
- **Produzione di petrolio e gas** (Energy Institute via OWID): i piccoli produttori (Giappone, Corea, Turchia, Ucraina, Germania per il petrolio, Taiwan, Spagna, Francia) dopo il 2016 sono aggregati in "altri". Il dato è stato omesso e segnalato in `buchi`. Le unità sono TWh, non barili: i barili al giorno arrivano solo con `EIA_API_KEY`.
- **Spesa militare:** gli ultimi dati SIPRI sono del 2014 per gli Emirati e del 2022 per il Qatar. Lo Yemen è fermo al 2014 e anche il suo PIL World Bank al 2018.
- **Debito pubblico:** assente per lo Yemen.
- **Dipendenza energetica dell'Ucraina:** su Eurostat l'ultimo dato è del 2020.
- **Peso netto:** manca per alcune righe (per esempio il greggio importato dall'Italia e quello esportato dalla Nigeria).
- **Export di greggio di Russia, Iran e Libia:** mancano (vedi Comtrade). Si potrebbero ricostruire con i "dati specchio", cioè gli import dichiarati dai partner, ma la Cina non dichiara il greggio iraniano.
- **Rating sovrano:** assente per tutti i paesi.

## Fatti rilevanti per la mappa (dal file prodotto)

1. **L'Italia importa il 95,2% del gas e l'89,8% del petrolio che consuma.** La dipendenza energetica complessiva è del 73,9% (2024, Eurostat nrg_ind_id).
2. **Il GNL arriva all'Italia per il 45,3% dagli Stati Uniti e per il 32,6% dal Qatar** (2025, quote sul valore, UN Comtrade). Circa un terzo del GNL italiano passa quindi da Hormuz. L'Italia spende per il gas più via gasdotto (17,3 miliardi di USD) che come GNL (8,7 miliardi) (UN Comtrade 2025).
3. **Il greggio italiano viene soprattutto da Libia (24,5%), Azerbaigian (15,9%, oleodotto BTC e Ceyhan) e Kazakistan (12,5%, terminale CPC sul Mar Nero e Bosforo).** Dal Golfo Persico arriva solo il 5,6–10,2% (UN Comtrade 2025). Il rischio per l'Italia passa da Libia, Bosforo e Turchia più che da Hormuz.
4. **L'Italia è il primo cliente di Azerbaigian e Algeria:** compra il 45,3% dell'export azero (2025) e il 24,0% di quello algerino (2024) (UN Comtrade, dati dei due esportatori).
5. **Giappone:** dal Golfo arriva tra il 10,3% e il 93,0% del greggio importato. Gli Emirati pesano per il 43,3% e l'Arabia Saudita per il 39,5% (UN Comtrade 2025). La dipendenza energetica è dell'87,3% (World Bank, 2024). Il minimo è basso perché Emirati e Arabia Saudita possono usare in parte Fujairah e Yanbu.
6. **Corea del Sud:** dal Golfo arriva tra il 23,0% e il 68,8% del greggio. Il primo fornitore è l'Arabia Saudita (34,2%), poi gli Stati Uniti (17,1%) (UN Comtrade 2025). La dipendenza energetica è dell'83,2% (World Bank, 2024).
7. **India:** dal Golfo arriva tra il 22,6% e il 47,9% del greggio e tra il 47,3% e il 60,8% del GNL (il Qatar da solo pesa il 47,3%). La Russia resta il primo fornitore di greggio con il 32,7% (UN Comtrade 2025).
8. **Cina:** dal Golfo arriva tra il 16,0% e il 37,8% del greggio dichiarato (con l'Iran probabilmente nascosto sotto la Malesia) e circa il 28% del GNL, quasi tutto dal Qatar. La Russia è il primo fornitore di greggio con il 16,6% (UN Comtrade 2025). **Taiwan:** dal Golfo arriva tra il 19,5% e il 61,1% del greggio (2024).
9. **Spesa militare 2025 (SIPRI):** l'Ucraina spende il 39,6% del PIL (84,1 miliardi di USD). Seguono Algeria (8,8%), Israele (7,8%) e Russia (7,5%, 190 miliardi). Gli Stati Uniti spendono 954 miliardi (3,1%). L'Italia è all'1,89%, sotto il 2% NATO; la Polonia al 4,5%.
10. **Debito pubblico e inflazione 2025 (FMI, WEO ottobre 2026):** Giappone 204,8% del PIL, Libia 153,8%, Italia 137,1%, Stati Uniti 124,4%. L'inflazione è al 50,6% in Iran e al 34,9% in Turchia.
11. **Gas di Norvegia e Germania:** la Norvegia ha esportato gas via gasdotto per 52,9 miliardi di USD nel 2025 (UN Comtrade). La Germania dipende dalle importazioni per il 91,6% del gas (Eurostat 2024).

## Collegamenti con gli altri livelli della mappa

- **Stretti** (`stretti.json`): le quote del Golfo Persico danno a Hormuz un "chi è esposto" per paese. Il greggio del Kazakistan si collega al Bosforo, quello saudita verso Egitto e Polonia al Mar Rosso e a Suez.
- **Condotte** (`linee.json`): TAP e BTC portano all'Azerbaigian, Transmed e Greenstream all'Algeria e alla Libia.
- **Mercati e prezzi:** inflazione e partite correnti mostrano la sensibilità al prezzo del petrolio.

## Proposta di visualizzazione

- **Colore dei paesi** in base a un indicatore scelto, per esempio dipendenza energetica, spesa militare in % del PIL o quota di greggio dal Golfo. Per la quota dal Golfo si può disegnare una barra dal minimo al massimo.
- **Scheda al clic:** indicatori con anno e fonte, sparkline di PIL, inflazione e spesa militare, primi 5 partner e fornitori di energia, e l'elenco dei `buchi`.
- **Frecce dai fornitori all'importatore** quando si seleziona un paese, per esempio Qatar → Italia per il GNL.

## Limiti

- Comtrade usa le dichiarazioni dell'importatore e quote **sul valore**, non sui volumi.
- La quota dal Golfo Persico è un proxy dell'esposizione a Hormuz, non una misura del transito.
- I dati FMI del 2025 sono in parte stime e il 2026 è una previsione.
- Energia in TWh di energia primaria.
- Il rating sovrano non c'è.
- Su GitHub Actions lo script dura circa 10 minuti per i limiti di Comtrade. Si può impostare `EIA_API_KEY` come secret per avere i barili al giorno.
