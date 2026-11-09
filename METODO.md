# Metodo

## Principi
1. **Ogni dato ha una fonte, una data e un link.** I punti sulla mappa conservano tutte le fonti lette (`fonti[]`).
2. **Affidabilità dichiarata** su tre livelli:
   - **alta**: confermato da fonte ufficiale o da più fonti indipendenti;
   - **media**: segnalato da fonte credibile, non ancora confermato;
   - **bassa**: non verificato, o rivendicazione di una parte in conflitto.
3. **Coordinate con origine e precisione:** `origine_coord` (fonte o stimata) e `precisione_km`.
4. **Fatti separati dalle valutazioni:** le valutazioni sono marcate come tali.
5. **Il tempo conta:** gli eventi cambiano colore con l'età; i prezzi di metà seduta sono segnati come provvisori.

## Schema dei dati
Schema comune con 25 campi (id, classe, categoria, nome, appartenenza, stato, data_evento, lat, lon, origine_coord, precisione_km, teatro, paese, attore, bersaglio, esito, fonte, link, data_fonte, affidabilità, note…) più campi di mappa. Dettagli in `docs/data/manifest.json`.

## Fonti principali e licenze
Il codice è sotto licenza MIT (`LICENSE`). I dati restano sotto le licenze delle fonti: elenco file per file in `DATA_LICENSES.md`, audit con rischi e azioni in `report/licenze.md`.

| Fonte | Uso | Licenza |
|---|---|---|
| Natural Earth | Base cartografica, ferrovie | Pubblico dominio |
| Global Energy Monitor | Oleodotti, gasdotti, GNL, nucleare | CC BY 4.0 |
| World Port Index (NGA), OurAirports, Wikidata | Porti, coordinate di basi e luoghi | Pubblico dominio / CC0 |
| Benden (2022) | Rotte marittime | Dichiarata in modo diverso dall'autore; si applica la più restrittiva, CC BY-NC 4.0 |
| TeleGeography | Cavi sottomarini | CC BY-NC-SA 3.0 (non commerciale, stessa licenza per i derivati) |
| OpenStreetMap / OpenInfraMap, PyPSA-Eur | Rete elettrica, interconnessioni | ODbL 1.0 (stessa licenza per la banca dati derivata) |
| IMF PortWatch | Transiti negli stretti, porti italiani | Dati pubblici FMI, con citazione |
| Digitraffic (Fintraffic) | Navi AIS nel Baltico | CC BY 4.0 |
| Global Fishing Watch, OpenSanctions | Interruzioni AIS; navi sanzionate dall'UE | CC BY-NC 4.0 (non commerciale) |
| OFAC, UK Sanctions List | Navi sanzionate | Pubblico dominio; Open Government Licence v3.0 |
| Eurostat, Banca Mondiale, EIA, ENTSOG, GIE AGSI+, FMI | Energia, scorte, schede paese | CC BY 4.0, pubblico dominio o riuso con citazione |
| U.S. Department of the Treasury | Rendimenti dei titoli di Stato | Pubblico dominio |
| Yahoo Finance | Indici, azioni, materie prime, valute | Nessuna licenza: solo uso personale, valori indicativi |
| @Majakovsk73, DeepStateMap | Fronte ucraino e storico | Nessuna licenza aperta: permesso degli autori da ottenere |
| Petro Ivaniuk (Kaggle) | Missili e droni sull'Ucraina | CC BY-NC-SA 4.0 |
| Stampa e centri di analisi | Eventi, notizie di mercato, dossier | Fatti citati con link |

## Limiti
- Le fonti aperte arrivano in ritardo e possono essere sbagliate o di parte.
- Le posizioni stimate sono indicative.
- I dati di Yahoo Finance non sono ufficiali e possono cambiare formato.
- Nessun dato è in tempo reale.
