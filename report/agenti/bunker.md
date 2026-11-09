# Bunker, carburanti navali ed emissioni: rapporto dell'agente (9 novembre 2026)

File prodotto: `docs/data/bunker-emissioni.json` (84 KB): 24 punti sulla mappa (15 hub del bunker, 7 porti con lo stato dell'allaccio elettrico in banchina, 2 porti di trasbordo extra UE), più EUA, volumi, regole, esempi di costo con il calcolo.
Script: `raccolta/bunker/raccogli.py` (solo libreria standard, circa 12 secondi). Voci curate a mano in `raccolta/bunker/`: `hub.json`, `volumi.json`, `regole.json`, `ops.json`, `esempi.json`.

Nel testo un **fatto** è un dato con fonte e data. Una **valutazione** è un ragionamento dell'osservatorio sulle fonti. I prezzi del bunker sono quelli di **venerdì 6 novembre 2026**, l'ultima chiusura su Ship & Bunker. Il prezzo EUA è quello dell'asta EEX di **lunedì 9 novembre**.

---

## 1. In breve: quanto pesano oggi carburante, ETS e FuelEU

**Per ogni tonnellata di VLSFO bruciata in un viaggio coperto dalle regole UE.** È il calcolo dello script, con EUA a 86,91 € (asta EEX del 9/11) e cambio 1,1222 USD/EUR.

| | Viaggio tra porti UE (100%) | Viaggio da o verso un porto extra UE (50%) |
|---|---|---|
| Carburante, VLSFO | 659 €/t (Rotterdam, 739,5 $) | 761 €/t (Singapore, 854 $) |
| EU ETS 2026 (100% di phase-in, CO2 + CH4 + N2O) | **275 €/t** | **137 €/t** |
| FuelEU, penale massima se la nave usa solo combustibile fossile | **62 €/t** | **31 €/t** |
| ETS + FuelEU, in % del carburante | circa 51% | circa 22% |

**Esempio: tratta extra UE verso Rotterdam.** Il consumo è un'**ipotesi didattica** di 4.000 t di VLSFO, comprato a Singapore:
- carburante: 3,04 milioni di euro;
- ETS: 0,55 milioni (14,8% del totale);
- FuelEU: al massimo 0,12 milioni (3,3%).

Il calcolo, passo per passo, è in `esempi_costo[].calcolo`.

**Cosa fa pagare un vettore.** Per il 4° trimestre 2026 Maersk applica un sovrapprezzo ETS+FuelEU di **170 USD per container da 40 piedi** da Estremo Oriente a Nord Europa. È calcolato su un EUA medio di 78,97 € ([Maersk, 1/9/2026](https://www.maersk.com/news/articles/2026/09/01/emissions-surcharge-ems-ess)). Vale il **4,7%** del nolo Drewry Shanghai–Rotterdam, 3.615 USD al 5/11 (`noli.json`).

*Valutazione.* Oggi il peso del costo viaggio dipende soprattutto dal **carburante**, salito con la guerra all'Iran. Il VLSFO a Rotterdam è a +51% dal 27 febbraio. L'**ETS** vale da un quinto a metà del costo del carburante, secondo quanta parte del viaggio è dentro l'UE. **FuelEU** nel 2026 pesa ancora poco: l'obiettivo è −2%. Il salto arriva nel 2030 (−6%) e soprattutto nel 2035 (−14,5%).

---

## 2. Fatti attuali (numero, data, fonte)

1. **Bunker ancora alti dopo lo shock di Hormuz.** Il 6/11/2026 il VLSFO costa 739,5 $/t a Rotterdam, 854 a Singapore, 865 a Fujairah e 810 a Gibilterra. Il 27/2, prima della guerra, costava rispettivamente 489,5, 521,5, 519,5 e 520,5 $/t. Il massimo del 2026 a Fujairah è stato 1.275 $/t il 12 giugno. Fonte: [Ship & Bunker](https://shipandbunker.com/prices/emea/me/ae-fjr-fujairah), serie nelle pagine pubbliche.
2. **Il gas naturale liquefatto (GNL) come carburante costa il doppio dell'olio combustibile.** A Rotterdam il 6/11 il GNL costa 1.793 $/t. A parità di energia sono 1.443,5 $/t, contro 598 dell'HSFO. Il 27/2 era a 563 $/t equivalenti. Valutazione: la crisi del GNL qatarino (TTF a +164% in un anno, `prezzi.json`) toglie per ora il vantaggio di costo alle navi dual-fuel GNL. Fonte: [Ship & Bunker, Rotterdam](https://shipandbunker.com/prices/emea/nwe/nl-rtm-rotterdam).
3. **Fujairah ha perso più di metà delle vendite.**
   - Gennaio 2026: 635.835 m³ ([WAM](https://www.wam.ae/en/article/173d8j6-fujairah-bunker-sales-reach-four-month-high)).
   - Marzo: 158.852 m³, −71,1% sul mese prima, il minimo storico, con porto e navi sotto attacco ([Ship & Bunker, 16/4](https://shipandbunker.com/news/emea/321874-fujairah-march-bunker-sales-sink-by-71-from-february-as-iran-war-breaks-out)).
   - Gennaio–agosto: 2,12 milioni di m³, contro 4,96 nel 2025 (−57,3%) ([Ship & Bunker, 21/9](https://shipandbunker.com/news/emea/764284-fujairah-bunker-sales-more-than-halve-from-last-year)).
   - Settembre: 231.000 t, +5% sul mese prima ([Engine, 19/10](https://engine.online/news/fujairah-bunker-sales-increased-in-september-82e8)).
   - Tutto il 2025: 7,4 milioni di m³ ([Reuters via Baird Maritime](https://www.bairdmaritime.com/shipping/tankers/bunker-hub-fujairah-logs-softer-marine-fuel-sales-in-2025)).
   - Dati: FOIZ / S&P Global.
4. **Singapore regge e cresce.** A settembre 2026 l'MPA conta 4,73 milioni di t vendute (−0,8% su un anno). Da gennaio a settembre sono 42,49 milioni di t (+2,1%). Nel 2025 erano state 56,77 milioni di t, il valore più alto dal 2020 nel dataset. Fonte: [MPA via data.gov.sg](https://data.gov.sg/collections/388/view), dati scaricati dallo script.
5. **Rotterdam perde volumi.** Nei primi nove mesi del 2026 ha venduto 5,63 milioni di t, contro 7,40 nel 2025 (−23,9%; fossili più bio, GNL a 0,45 t/m³). Nel 2025 il totale era 9,82 milioni di t. Il calo viene attribuito al recepimento olandese di **RED III** dal 1/1/2026 e allo spostamento dei volumi fuori dall'area ARA. Il Belgio potrebbe recepire RED III solo nel 2027: il VLSFO di Anversa costa 9 $/t meno di quello di Rotterdam. Fonti: [Port of Rotterdam, PDF ufficiale](https://www.portofrotterdam.com/sites/default/files/2026-10/bunker-sales-2024-2026.pdf); [Ship & Bunker, 23/10](https://shipandbunker.com/news/emea/661476-analysis-rotterdam-bunker-sales-down-249-in-first-nine-months-as-red-iii-bites).
6. **EUA.** All'asta EEX del 9/11/2026 la quota è stata aggiudicata a 86,91 €/t (cover ratio 1,74), +8,5% su un anno. Nelle aste EU del 2026 il minimo è 62,19 € (19 marzo, durante lo shock della guerra) e il massimo 91,32 € (15 gennaio); la media è 78,81 €. Fonte: [EEX, risultati delle aste](https://public.eex-group.com/eex/eua-auction-report/emission-spot-primary-market-auction-report-2026-data.xlsx).
7. **Dal 2026 l'ETS marittimo è a pieno regime.** Le quote coprono il 100% delle emissioni 2026, contro il 40% nel 2024 e il 70% nel 2025. Entrano anche CH4 e N2O. Le navi offshore sopra 5.000 GT entrano dal 2027. Fonte: [Commissione europea, FAQ](https://climate.ec.europa.eu/eu-action/transport-decarbonisation/reducing-emissions-shipping-sector/faq-maritime-transport-eu-emissions-trading-system-ets_en).
8. **Porti di trasbordo usati per eludere l'ETS.**
   - **Oggi** la lista dei porti di trasbordo vicini comprende solo **East Port Said e Tanger Med**. Per l'ETS è nel [Reg. di esecuzione 2023/2297](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32023R2297), per FuelEU nel [Reg. 2025/1127](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32025R1127).
   - **La proposta della Commissione del 17/7/2026** porta la soglia di trasbordo dal 65% al 50% e rivede la lista ogni anno. Esclude come porto di scalo gli impianti di trasbordo a meno di 150 miglia nautiche dall'UE. Porta nell'ETS le navi da 400 GT dal 2029. Crea il meccanismo SMAP: 110 milioni di quote tra il 2028 e il 2040.
   - Fonti: [El Estrecho Digital](https://www.elestrechodigital.com/en/imprimir/the-european-commission-reduces-the-threshold-for-neighboring-transshipment-ports-to-50-in-its-review-of-the-maritime-ets), [WSC](https://www.worldshipping.org/news/wsc-ets-rightly-reinvests-more-into-maritime-decarbonisation-but-new-port-rules-risk-targeting-competition-rather-than-emissions). Il testo della proposta non è stato letto direttamente.
9. **Il quadro globale IMO (Net-Zero Framework) è ancora rinviato.**
   - Approvato a MEPC 83 (aprile 2025).
   - Il 17/10/2025 la sessione straordinaria è stata aggiornata di 12 mesi (57 voti a favore del rinvio, 49 contrari). Il conteggio dei voti è di [Ship Technology](https://www.ship-technology.com/news/imos-net-zero-strategy-adoption-pushed-back-another-year-by-saudi-vote/), non del resoconto IMO.
   - MEPC 84 (27/4–1/5/2026) non ha votato. Ha fissato la ripresa al **4 dicembre 2026**, da confermare a MEPC 85 (30/11–3/12).
   - ISWG-GHG 22 (1–4/9) si è chiuso senza accordo.
   - Fonte: [IMO, MEPC 84](https://www.imo.org/en/MediaCentre/MeetingSummaries/Pages/Temporary-MEPC-84th-session.aspx), [IMO, anteprima MEPC 85](https://www.imo.org/en/MediaCentre/MeetingSummaries/Pages/PREVIEW-MEPC-85.aspx).
10. **L'allaccio elettrico in banchina (OPS) è in ritardo, tranne ad Amburgo ed Esbjerg.** A settembre 2025 i punti di connessione richiesti da AFIR per il 2030 erano:

    | Porto | Punti pronti o impegnati | Richiesti al 2030 |
    |---|---|---|
    | Amburgo | 14 | 25 |
    | Rotterdam | 7 | 8 |
    | Anversa-Bruges | 2 | 28 |

    Fonte: [Interreg BREEZE, aprile 2026](https://www.interregeurope.eu/sites/default/files/2026-04/OPS%20Analysis%20BREEZE.pdf). In Italia gli impianti di Trieste sono in collaudo e a Genova le banchine crociere sono in costruzione (dettagli al punto 4).

---

## 3. Le regole in sintesi

**EU ETS marittimo** (direttiva 2023/959)
- **Navi coperte:** cargo e passeggeri oltre 5.000 GT.
- **Copertura:** 100% delle emissioni nei viaggi intra UE e all'ormeggio; 50% nei viaggi da o verso porti extra UE.
- **Phase-in:** 40% nel 2024, 70% nel 2025, 100% dal 2026. Le quote si restituiscono entro il 30 settembre dell'anno dopo.
- **Gas:** CH4 e N2O dal 2026.
- **Sanzione:** 100 € per tonnellata non coperta, indicizzati all'inflazione.

**FuelEU Maritime** (regolamento 2023/1805, dal 1/1/2025)
- **Limite di intensità GHG:** sul ciclo completo, dalla produzione del carburante al motore, rispetto a 91,16 gCO2e/MJ:

  | Dal | 2025 | 2030 | 2035 | 2040 | 2045 | 2050 |
  |---|---|---|---|---|---|---|
  | Riduzione | −2% | −6% | −14,5% | −31% | −62% | −80% |

- **Penale:** 2.400 € per tonnellata di VLSFO equivalente di deficit (41.000 MJ), maggiorata del 10% per ogni anno consecutivo.
- **Flessibilità:** si possono mettere in comune le prestazioni di più navi (pooling), accantonare un surplus (banking) o anticipare un surplus dall'anno dopo (borrowing).
- **Carburanti sintetici (RFNBO):** moltiplicatore 2 fino al 2033; sotto-obiettivo del 2% dal 2034 se nel 2031 la quota resta sotto l'1%.
- **Allaccio elettrico in banchina (OPS):** dal 1/1/2030 portacontainer e navi passeggeri ormeggiate per più di 2 ore nei porti AFIR devono collegarsi. Penale: 1,5 € per kW per ora. Dal 2035 l'obbligo vale in ogni porto UE con OPS disponibile.

**IMO**
- **Net-Zero Framework:** riferimento 93,3 gCO2e/MJ.
  - Obiettivi: −4%/−17% nel 2028, −8%/−21% nel 2030, −30%/−43% nel 2035.
  - Prezzi delle unità correttive: 100 USD/t (Tier 1) e 380 USD/t (Tier 2) nel 2028–2030.
  - Entrata in vigore 16 mesi dopo l'adozione, che richiede due terzi dei votanti.
  - Questi parametri sono riportati da una fonte secondaria ([AIFILTECH, 30/10/2026](https://www.aifiltech.com/en/imo-net-zero-framework-vote-december-2026/)) e possono cambiare.
- **CII (indicatore annuale di intensità di carbonio):** riduzione richiesta rispetto al 2019:

  | Anno | 2023 | 2024 | 2025 | 2026 | 2027 | 2030 |
  |---|---|---|---|---|---|---|
  | Riduzione | 5% | 7% | 9% | 11% | 13,625% | 21,5% |

  Fonte: [DNV su MEPC 83](https://www.dnv.com/news/2025/imo-mepc-83-ghg-requirements-approved-taking-effect-from-2028/).
- **ECA del Nord-Est Atlantico** (zona a basse emissioni): adottata a MEPC 84, in vigore dal 1/9/2027 ed efficace 12 mesi dopo.

---

## 4. Cosa cambia per un porto del Nord Europa

**1. La concorrenza sul bunker si gioca sulle regole nazionali.** RED III olandese, assente in Belgio, ha spostato volumi: Rotterdam −23,9% nei primi nove mesi. Ship & Bunker attribuisce il calo soprattutto a RED III e aggiunge che il vantaggio di Anversa potrebbe durare un anno intero.
*Valutazione.* Si vedrà se il calo si rovescia quando il Belgio recepirà RED III.

**2. Nascono nuovi prodotti e cresce la domanda di biocarburanti.** FuelEU e l'ETS favoriscono bio-miscele, bio-GNL e bio-metanolo. A Rotterdam, nel 3° trimestre 2026, il bio-GNL è salito a 23.613 m³ (970 un anno prima) e il bio-metanolo a 4.166 t ([PDF del porto](https://www.portofrotterdam.com/sites/default/files/2026-10/bunker-sales-2024-2026.pdf)).
*Valutazione.* Con il GNL fossile a prezzi di crisi, le navi dual-fuel cercano bio-GNL o tornano all'olio. Il GNL venduto a Rotterdam nel 3° trimestre è sceso del 35% su un anno.

**3. L'elettricità in banchina diventa infrastruttura obbligatoria.**
- Rotterdam: 35 punti per portacontainer (8 km di banchina), prestito BEI di 90 milioni, piena operatività prevista a inizio 2029. Il collo di bottiglia è la rete elettrica congestionata.
- Amburgo è il più avanti tra i grandi porti.
- Anversa deve costruire quasi tutto: 26 dei 28 punti richiesti al 2030.
- Esbjerg ha l'OPS dal 2021: 1.740 MWh forniti nel 2025, circa 386 tCO2e evitate ([Port Esbjerg](https://portesbjerg.dk/en/our-focus/onshore-power-supply-and-electricity)).
- In Italia:
  - Trieste ha i punti di connessione pronti, in collaudo, e prepara la gara per il gestore ([Il Nord Est](https://www.ilnordest.it/economia/infrastrutture/cold-ironing-trieste-accende-i-moli-gara-per-il-gestore-entro-fine-anno-uhlmlcdj)).
  - A Genova le banchine crociere sono ancora in costruzione e i traghetti non prima del 2028 ([Shipping Italy](https://www.shippingitaly.it/2026/06/19/salvi-i-fondi-per-il-cold-ironing-dei-traghetti-nel-porto-di-genova/)).
  - Per Venezia lo stato del 2026 non è verificato.
  - MSC avverte che oggi, all'ormeggio, l'elettricità costa più del GNL ([Shipping Italy, 23/7/2026](https://www.shippingitaly.it/2026/07/23/msc-preoccupata-dal-costo-del-cold-ironing-nei-porti-italiani/)).

**4. Il trasbordo rischia di spostarsi fuori dall'UE.** Un hub fuori lista vicino all'UE taglia la parte di viaggio coperta. Nell'esempio con 500 t sull'ultima tratta (ipotesi), il costo ETS+FuelEU scende da 0,67 a 0,08 milioni di euro: un risparmio di circa 0,59 milioni per scalo. Per questo la Commissione vuole abbassare la soglia al 50% e introdurre il criterio delle 150 miglia nautiche. La WSC obietta che così si colpisce la concorrenza, non le emissioni.
*Valutazione.* Per i porti di trasbordo europei (Algeciras, Gioia Tauro, Valencia, Pireo) la lista conta più del prezzo del bunker.

---

## 5. Indicatori da seguire

| Indicatore | Dove | Frequenza | Perché |
|---|---|---|---|
| EUA (asta EEX) | `eua.asta_ultima`, `eua.aste_serie` | giornaliera | 1 € di EUA = circa 3,16 € per tonnellata di VLSFO nei viaggi intra UE |
| VLSFO, HSFO, MGO, GNL nei grandi hub | `elementi[tipo=hub_bunker].prezzi` | giornaliera | costo diretto; differenza Rotterdam–Anversa (RED III) |
| Premio VLSFO su Brent; Fujairah meno Singapore | `confronti` | giornaliera | tensione sui prodotti raffinati e rischio nel Golfo |
| Vendite di Singapore (MPA) | `volumi.singapore` | mensile, verso il 20 del mese | dove si sposta la domanda tolta a Fujairah |
| Vendite di Fujairah (FOIZ) | `volumi.fujairah` (a mano) | mensile | termometro di Hormuz per lo shipping |
| Vendite di Rotterdam | `volumi.rotterdam` (lo script avvisa se esce un nuovo PDF) | trimestrale | effetto di RED III e della concorrenza di Anversa |
| Sovrapprezzo ETS+FuelEU di Maersk | `sovrapprezzo_vettori` (a mano) | trimestrale; il 1° trimestre 2027 esce verso il 1/12 | quanto costo viene passato ai caricatori |
| Voto IMO sul Net-Zero Framework | `regole.imo` | 4/12/2026 | se passa, si apre il tema del doppio pagamento ETS+IMO |
| Revisione ETS (soglia 50% e 150 miglia) | `regole.eu_ets_marittimo.revisione_2026` | negoziato in Parlamento e Consiglio | lista dei porti di trasbordo e competitività dei porti UE |
| Allaccio elettrico (OPS) nei porti | `elementi[tipo=porto_ops]` | ad ogni annuncio | scadenza del 1/1/2030 |

---

## 6. Fonti provate

| Fonte | Esito | Licenza e note |
|---|---|---|
| Ship & Bunker, pagine prezzi per porto | **funziona** senza chiave (serie in `PORT_CHART`) per Rotterdam, Anversa, Gibilterra, Pireo, Istanbul, Fujairah, Singapore e l'indice EUA. **Solo per abbonati:** Genova, Algeciras, Amburgo, Skagen, Göteborg, Danzica, Malta, Port Said | © Ship & Bunker; si salva solo una serie settimanale di 13 mesi, con citazione |
| EEX, aste primarie EUA (xlsx annuale) | **funziona** | dati pubblici EEX |
| data.gov.sg, MPA Bunker Sales | **funziona** senza chiave; chiave facoltativa `DATAGOVSG_API_KEY` | Singapore Open Data Licence. L'unità dichiarata è «tonnes», ma i valori sono in migliaia |
| Port of Rotterdam, PDF trimestrale | **leggibile ma non automatizzato**: serve `pdftotext`, quindi è trascritto in `volumi.json`; lo script controlla se esce un PDF nuovo | uso con citazione |
| FOIZ (Fujairah) | **nessun file pubblico**; dati da S&P Global, Ship & Bunker, Engine | trascrizione a mano |
| EUR-Lex, Commissione europea, IMO | **funzionano** | testi ufficiali |
| Bunker Index | prove su URL non andate a buon fine (404) | — |
| WebFetch su vari siti | non risolve i domini; con curl invece funzionano | — |

---

## 7. Collegamenti con gli altri livelli della mappa

- **Stretti** (`stretti.json`, `portwatch.json`). Hormuz è a −95% di transiti, e questo spiega Fujairah. Suez si riprende: più navi sulla rotta Asia–Mediterraneo, che conta per ETS e FuelEU solo dall'ultimo porto extra UE.
- **Prezzi** (`prezzi.json`).
  - Brent 92,62 $/bbl, cioè 697 $/t: il VLSFO di Rotterdam ha un premio di 42 $/t, quello di Singapore di 157 $/t.
  - Il TTF a 82,33 €/MWh spiega il prezzo del GNL come carburante.
  - Il cambio EUR/USD serve per gli esempi di costo.
- **Noli** (`noli.json`). Il sovrapprezzo ETS+FuelEU vale circa il 4,7% del WCI Shanghai–Rotterdam.
- **Italia** (`italia.json`, `portwatch.json`). Genova, Trieste e Venezia hanno lo stato dell'OPS. I prezzi di Genova non sono pubblici.

## 8. Proposta per la mappa

- **Hub del bunker:** cerchi con il VLSFO in $/t nell'etichetta, colorati per variazione dal 27/2. Popup con VLSFO, HSFO, MGO e GNL, la serie settimanale e i volumi dove esistono (Singapore, Rotterdam, Fujairah). Gli hub riservati agli abbonati vanno in grigio.
- **Porti OPS:** icona a spina, colore per stato: operativo (verde), parziale (giallo), in costruzione (arancio), in progetto (rosso).
- **Porti di trasbordo extra UE** (Tanger Med, East Port Said): triangolo con un cerchio di 300 miglia nautiche, la distanza della regola attuale. Un secondo cerchio tratteggiato a 150 miglia per la proposta 2026.
- **Riquadro «costo del viaggio»:** EUA del giorno, costo per tonnellata nei viaggi intra ed extra UE, sovrapprezzo Maersk.

## 9. Limiti

- **Esempi di costo.** I consumi sono **ipotesi dichiarate** (4.000 t e 500 t), non dati di navi reali. La penale FuelEU è un tetto massimo: il prezzo di mercato del pooling non è pubblico. Il VLSFO è trattato come HFO (classe RMG), come d'uso. Con la classe LFO l'intensità scende a 91,39 gCO2e/MJ e la penale cala di circa il 15%.
- **Ship & Bunker.** Sono medie di più fonti, non transazioni. Una parte dei porti, tra cui **Genova**, è a pagamento. Il formato `PORT_CHART` può cambiare.
- **Volumi.** Fujairah e Rotterdam vanno aggiornati a mano. Fujairah mescola m³ (FOIZ) e tonnellate (Engine). Per Gibilterra, Algeciras e i porti italiani non ci sono serie pubbliche dei volumi di bunker.
- **Revisione ETS e parametri IMO.** Vengono da stampa di settore e fonti secondarie: affidabilità media.
- **OPS.** I conteggi BREEZE sono di settembre 2025 e comprendono i punti «impegnati».
