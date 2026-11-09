# Regole comuni per gli agenti di raccolta

Progetto: osservatorio OSINT di rischio geoeconomico. Mappa in `docs/index.html`, dati in `docs/data/`.
Idea guida: evento → passaggio strategico/infrastruttura → flussi → prezzi → chi è esposto (Italia in evidenza).

## Cosa produce ogni agente
1. `raccolta/<dominio>/raccogli.py`: script ripetibile, **solo libreria standard di Python 3** (urllib, json, csv, zipfile…). Deve girare da solo ogni giorno su GitHub Actions senza intervento umano. Se una fonte richiede una chiave API gratuita, leggerla da una variabile d'ambiente (es. `EIA_API_KEY`) e saltare quella fonte con un avviso se manca, senza fallire.
2. `docs/data/<file>.json`: il dato prodotto dallo script (eseguito davvero, non inventato). Formato:
   ```json
   {"aggiornato": "AAAA-MM-GGTHH:MMZ", "fonti": [{"nome": "...", "link": "...", "licenza": "...", "data_dato": "..."}],
    "nota": "...", "elementi": [ ... ], "errori": []}
   ```
   - Punti: `lat`, `lon` (numeri), `nome`, `paese` (ISO a 2 lettere), `categoria`, `stato`, `fonte`, `link`, `data_fonte`, `affidabilita` (alta/media/bassa), `note`.
   - Linee: come `docs/data/linee.json`: `g` = lista di parti, ogni parte lista di `[lon, lat]` con al massimo 4 decimali; semplificare le geometrie (il file finale deve stare sotto ~1,5 MB).
   - Serie storiche: `[["AAAA-MM-GG", valore], ...]`.
3. `report/agenti/<dominio>.md`: rapporto in italiano, chiaro e breve, con: fonti provate (funziona / non funziona / serve chiave), licenze, cosa contiene il file, **5–10 fatti attuali rilevanti con numero, data e fonte**, collegamenti con gli altri livelli della mappa (stretti, oleodotti, eventi, mercati), proposta di come mostrarlo sulla mappa, limiti.

## Regole
- Mai inventare numeri o coordinate. Se un dato manca, scrivi che manca.
- Ogni dato con fonte, link e data. Distinguere fatti e valutazioni.
- Licenze: preferire pubblico dominio, CC0, CC BY. Se CC BY-NC o simili, segnalarlo nel rapporto (il progetto è personale e non commerciale).
- Niente dati personali, niente chiavi nel codice.
- Toccare SOLO i propri file (`raccolta/<dominio>/`, `docs/data/<file>.json`, `report/agenti/<dominio>.md`). Non modificare `docs/index.html` né altri file di dati. Niente git commit o push: li fa il coordinatore.
- Lo schema completo dei dati esistenti è descritto in `docs/data/manifest.json` (campo `notes.layers`).
