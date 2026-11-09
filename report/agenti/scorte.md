# Scorte e depositi strategici – rapporto agente

Aggiornato: 9 novembre 2026. File dati: `docs/data/scorte.json` (34 serie, ~82 KB). Script: `raccolta/scorte/raccogli.py` (solo libreria standard, ~15 s, eseguito davvero).

## Fonti provate

| Fonte | Esito | Chiave | Licenza |
|---|---|---|---|
| GIE AGSI+ API (`https://agsi.gie.eu/api`) – stoccaggi gas giornalieri per paese e UE | **Serve la chiave**: senza header `x-key` risponde `"Invalid or missing API key"` (provato 9/11/2026). Codice pronto, si attiva da solo se c'è `AGSI_API_KEY`. | Sì, gratuita | uso libero citando GIE AGSI+ |
| GIE ALSI (GNL) | Anche questa chiede la chiave (stessa chiave di AGSI) | Sì | idem |
| Eurostat `nrg_stk_gasm` – gas in stoccaggio a fine mese | **Funziona** senza chiave. Ripiego per il gas. Ritardo di 2–3 mesi, non dà la % di riempimento | No | CC BY 4.0 |
| EIA LeafHandler (`/dnav/pet/hist/LeafHandler.ashx?n=PET&s=...&f=W`) | **Funziona** senza chiave (tabella HTML con lo storico completo dal 1982). Il file `hist_xls/*.xls` si scarica, ma è un vecchio XLS binario che la libreria standard non legge | No | pubblico dominio |
| EIA API v2 | Ripiego nello script se c'è `EIA_API_KEY` (non provata: chiave assente) | Sì, gratuita | pubblico dominio |
| Eurostat `nrg_stk_oem` – scorte petrolifere di emergenza in giorni | **Funziona** (paesi UE, nessun aggregato UE) | No | CC BY 4.0 |
| USDA FAS PSD, zip `psd_grains_pulses_csv.zip` | **Funziona** (a volte la connessione si interrompe: lo script riprova) | No | pubblico dominio |
| FMI IRFCL via SDMX (`api.imf.org/external/sdmx/2.1`) – oro in once troy | **Funziona** | No | © FMI: riuso con citazione per uso non commerciale (non è CC) |
| World Gold Council | Non usato: i dati richiedono la registrazione | – | proprietaria |

**Come ottenere la chiave AGSI (gratuita):** registrarsi su https://agsi.gie.eu/account e copiare la chiave API dal profilo. Va salvata come secret `AGSI_API_KEY` su GitHub Actions. Con la chiave lo script aggiunge 12 serie giornaliere (riempimento % e TWh per IT, DE, FR, NL, AT e UE) con il confronto con l'anno scorso, con la media dei 5 anni e con la distanza dall'obiettivo del 90%. **Attenzione:** questo ramo del codice è scritto sulla base della documentazione (campi `gasDayStart`, `full`, `gasInStorage`, `workingGasVolume`; `type=eu` per l'aggregato), ma senza chiave non è stato possibile provarlo. Va verificato alla prima esecuzione con la chiave.

**Altre opzioni senza chiave per il gas giornaliero:** non ne ho trovata una ufficiale e stabile. I siti terzi (Bruegel, energy-charts) prendono comunque i dati da AGSI. Gli endpoint interni del sito AGSI non sono stati usati.

## Cosa c'è nel file

`elementi[]`: una serie per oggetto (`id`, `nome`, `gruppo`, `paese`, `unita`, `frequenza`, `fonte`, `link`, `affidabilita`, `data_fonte`, `note`, `serie` = `[[data, valore]]`, `ultimo`). `ultimo` contiene il valore, il dato precedente, `anno_scorso` (variazione assoluta e %) e `media_5_anni` (scarto assoluto e %, calcolato sulla stessa data dei 5 anni precedenti). `riepilogo[]` riporta gli stessi "ultimi valori" in forma compatta. Le serie mensili e annuali sono datate al primo giorno del periodo.

- Gas UE (Eurostat, mensile, TWh PCS): IT, DE, FR, NL, AT, UE-27, dal 2023.
- Petrolio USA (EIA, settimanale, milioni di barili): SPR, greggio commerciale, benzina, distillati, Cushing, dal 2023.
- Scorte petrolifere di emergenza (Eurostat, giorni): IT, DE, FR, NL, AT.
- Grano, scorte finali (USDA PSD, Mt, anno commerciale): mondo (somma dei paesi), Cina, USA, UE, Russia, India, dal 2011, con il rapporto scorte/consumo.
- Oro (FMI, tonnellate, mensile): IT, DE, FR, NL, US, CN, RU, IN, TR, PL, JP, CH, dal 2023.

## Fatti attuali (con numero, data e fonte)

1. **La riserva strategica USA (SPR) è al minimo da ottobre 1982:** 282,2 milioni di barili nella settimana al 30/10/2026, contro 409,6 un anno prima (−127 Mb, −31%) e 415,4 il 6/3/2026. Il prelievo è di circa 133 Mb da marzo, cioè dall'inizio della crisi di Hormuz. Il calo continua anche se rallentato (−0,4 Mb nell'ultima settimana). Fonte: EIA WCSSTUS1, rilascio del 4/11/2026.
2. **Le scorte commerciali USA sono sotto la norma, soprattutto il gasolio:** greggio a 409,8 Mb (−2,7% sull'anno, −4,3% sulla media 5 anni); distillati a 99,3 Mb (−11% sull'anno, −13,3% sulla media 5 anni, −3,6 Mb in una settimana). Cushing invece è sopra la media (27,3 Mb, +9%). Fonte: EIA, settimana al 30/10/2026.
3. **Il gas nell'UE a fine agosto 2026 era a 729 TWh**, contro 904 TWh un anno prima (−19,4%) e una media 5 anni di 964 TWh (−24,3%). Il minimo di fine inverno è stato 345 TWh (fine marzo 2026). Fonte: Eurostat nrg_stk_gasm.
4. **La Germania è il punto debole:** 127,7 TWh a fine agosto 2026, −25,9% sull'anno e −36,7% sulla media 5 anni. Seguono i Paesi Bassi (87,1 TWh a fine settembre, −26% sulla media 5 anni). **L'Italia tiene:** 178,9 TWh a fine settembre, −5,6% sull'anno e −4,7% sulla media 5 anni. Fonte: Eurostat.
5. **Dato più recente (da fonte secondaria, non scaricato dallo script):** l'UE era al 74,56% di riempimento il 1/11/2026, con un picco del 74,96% il 27/10 (dati AGSI ripresi da oenergetice.cz). Secondo la stampa italiana, che cita Snam, l'Italia ha raggiunto il 90% il 20/10/2026. Il dato UE resta molto sotto l'obiettivo del 90%, che dalla riforma del 2025 si può raggiungere fra il 1/10 e il 1/12, con deroghe fino a −10 pp (+5 pp in condizioni di mercato difficili). Da verificare con AGSI appena c'è la chiave.
6. **IEA, Global Gas Security Review del 3/11/2026:** gli stoccaggi UE entrano nell'inverno al livello più basso dal 2013. Con un inverno freddo e Hormuz ancora bloccato potrebbero scendere sotto il 10% a fine marzo 2027. I carichi di GNL da Qatar e EAU sono calati di oltre 60 miliardi di m³ fra marzo e ottobre. Il GNL globale scende del 3% nel 2026, il calo più forte mai registrato. Fonte: iea.org.
7. **Le scorte petrolifere di emergenza dell'Italia sono scese a 77,2 giorni** (agosto 2026), contro 90,5 un anno prima: sono sotto la soglia di circa 90 giorni prevista dalla direttiva 2009/119/CE dall'aprile 2026, verosimilmente per i rilasci coordinati. Germania 97,1, Francia 96,5, Paesi Bassi 95,5, Austria 89,0. Fonte: Eurostat nrg_stk_oem. Il valore di giugno (89,7) è un'anomalia da verificare.
8. **Grano, campagna 2026/27 (USDA, ottobre 2026):** le scorte finali mondiali sono 276,0 Mt (−2,0% sull'anno), con un rapporto scorte/consumo del 33,5%. La Cina detiene 119,2 Mt (43% del totale). L'**UE scende a 11,7 Mt (−38%)**, con un rapporto scorte/consumo di appena il 10%. Russia (19,1 Mt, +59%) e India (29,5 Mt) salgono. Fonte: USDA PSD.
9. **Oro delle banche centrali (FMI IRFCL):** la Polonia è a 672,9 t (+157,5 t in un anno, settembre 2026); la Cina a 2.409,6 t (+106 t); la Russia scende a 2.264,3 t (−65 t, probabili vendite per finanziare il bilancio). L'Italia è stabile a 2.451,8 t (terza al mondo dopo USA 8.133,5 t e Germania 3.349,1 t).
10. **Mercati (da `prezzi.json`, 9/11/2026):** TTF a 82,3 €/MWh (+164% sull'anno, +192% da inizio anno); Brent a 93,7 $/b (+47% sull'anno); oro a 4.116 $/oz.

## Collegamenti con gli altri livelli della mappa

- **Hormuz → GNL → stoccaggi UE → TTF.** Senza il GNL del Qatar l'UE ha riempito poco (−24% sulla media 5 anni ad agosto). Il TTF a 82 €/MWh riflette scorte basse e la domanda di iniezioni nell'estate 2027. *Valutazione:* un inverno freddo è il principale rischio di prezzo fra gennaio e marzo 2027. Il rischio è più alto per la Germania e per l'Europa centrale (Austria), dipendenti dai flussi da nord-ovest.
- **Italia esposta, ma più protetta sul gas:** stoccaggi vicini al 90%, gasdotti da Algeria e Azerbaigian (TAP) e rigassificatori. Sul petrolio invece le scorte di emergenza sono sotto norma (77 giorni). Da collegare a `italia.json` e `condotte.json`.
- **Petrolio:** il prelievo dalla SPR USA (−133 Mb da marzo) e le scorte di emergenza europee sono stati il cuscinetto contro la chiusura di Hormuz. *Valutazione:* questo margine si è ridotto. Una nuova crisi troverebbe meno barili pronti, quindi un Brent più sensibile, e la ricostituzione delle scorte sosterrà la domanda nel 2027.
- **Gasolio:** le scorte di distillati USA sono a −13% sulla media 5 anni. I distillati del Golfo passano da Hormuz: c'è rischio sul gasolio europeo in inverno, con il riscaldamento e l'autotrasporto.
- **Grano:** scorte UE molto basse e Russia più forte come esportatore. Collegare a Mar Nero/Bosforo (`stretti.json`) e al Mediterraneo (Egitto, Nord Africa).
- **Oro:** gli acquisti di Polonia e Cina e le vendite russe sono un indicatore di "de-dollarizzazione" e di finanza di guerra.

## Proposta di visualizzazione

- Pannello "Scorte" con indicatori: gas UE (% e distanza dal 90%), SPR (Mb e minimo dal 1982), giorni di scorte petrolifere IT, scorte/consumo di grano. Ogni indicatore con una mini-serie e il confronto con l'anno scorso e con la media 5 anni.
- Sulla mappa: colorare i paesi UE in base allo scarto dalla media 5 anni degli stoccaggi gas (verde/giallo/rosso). Mostrare un punto per la SPR (siti costieri di Texas e Louisiana) e uno per Cushing, con un popup e il link alla serie.
- Grafico "stagionale" del gas: anno corrente, anno scorso e fascia min–max dei 5 anni.

## Limiti

- Senza `AGSI_API_KEY` il gas arriva solo da Eurostat: mensile, in ritardo di 2–3 mesi (ultimo dato agosto/settembre 2026), in TWh PCS (potere calorifico superiore, circa il 10% sopra il potere calorifico inferiore). Non dà la % di riempimento e i TWh non sono direttamente confrontabili con AGSI. Il ramo AGSI non è stato provato.
- Eurostat `nrg_stk_oem` non ha l'aggregato UE e il dato IEA (giorni di import dei paesi IEA) non è scaricabile liberamente: manca il totale UE/IEA.
- Il totale mondiale del grano è la somma dei paesi PSD e può differire leggermente dal totale WASDE pubblicato. L'ultimo anno è una proiezione e cambia ogni mese (il WASDE esce intorno al 10 del mese).
- I dati sull'oro sono dichiarati dalle autorità, con 1–3 mesi di ritardo (USA a luglio 2026). Per l'oro non c'è la media 5 anni, perché lo storico nel file parte dal 2023. La licenza FMI non è CC.
- I fatti 5 e 6 vengono da fonti secondarie e da comunicati (IEA), non dallo script.

Fonti web citate: [IEA – Low storage buffers in Europe…](https://www.iea.org/news/low-storage-buffers-in-europe-could-prolong-global-gas-market-tightness-well-into-2027), [IEA Global Gas Security Review 2026](https://www.iea.org/reports/global-gas-security-review-2026/executive-summary), [oenergetice.cz – EU gas storage less than three-quarters full](https://oenergetice.cz/en/natural-gas/eu-gas-storage-is-less-than-three-quarters-full-how-much-will-be-left-after-winter), [S&P Global – regole stoccaggi più flessibili](https://www.spglobal.com/commodity-insights/en/news-research/latest-news/natural-gas/062525-eu-gas-storage-rules-to-be-made-more-flexible-under-provisional-agreement), [Consiglio UE – proroga di 2 anni](https://www.globalsecurity.org/military/library/news/2025/07/mil-250718-eeas01.htm), [QuiFinanza – stoccaggi Italia vicini al 90%](https://quifinanza.it/economia/stoccaggi-gas-europa-italia-inverno/1019855/amp/).
