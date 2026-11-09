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
| Fonte | Uso | Licenza |
|---|---|---|
| Natural Earth | Base cartografica | Pubblico dominio |
| Global Energy Monitor | Oleodotti e gasdotti | CC BY 4.0 |
| World Port Index (NGA) | Porti | Pubblico dominio |
| Benden (2022) | Rotte marittime | Dati di ricerca, citati |
| OurAirports, Wikidata | Coordinate di basi e luoghi | Pubblico dominio / CC0 |
| U.S. Department of the Treasury | Rendimenti dei titoli di Stato | Pubblico dominio |
| Yahoo Finance | Prezzi di indici, azioni, materie prime, valute | Uso informativo, non ufficiale |
| Stampa e centri di analisi | Eventi, notizie di mercato, dossier | Citati con link |

## Limiti
- Le fonti aperte arrivano in ritardo e possono essere sbagliate o di parte.
- Le posizioni stimate sono indicative.
- I dati di Yahoo Finance non sono ufficiali e possono cambiare formato.
- Nessun dato è in tempo reale.
