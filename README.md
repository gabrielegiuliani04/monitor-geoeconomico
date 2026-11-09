# Monitor geoeconomico

Osservatorio OSINT di rischio geoeconomico: una mappa interattiva che collega **eventi militari e geopolitici**, **passaggi strategici**, **flussi di energia e merci** e **mercati finanziari**.

L'idea guida è la *catena delle conseguenze*:

> evento → passaggio strategico → flussi (navi, energia, merci) → noli → prezzi → chi è esposto

**Sito:** https://gabrielegiuliani04.github.io/monitor-geoeconomico/

## Cosa contiene

| Livello | Contenuto | Fonte principale |
|---|---|---|
| Eventi | Attacchi, lanci, intercettazioni, sequestri, blackout, con data e affidabilità | Stampa e analisi da fonti aperte, ogni punto con le sue fonti |
| Russia-Ucraina | Aree controllate e contese, avanzate, colpi lungo il fronte | Mappe da fonti aperte |
| Europa, attacchi ibridi | Sabotaggi, droni, disturbo GNSS, attacchi informatici, spionaggio | Stampa e fonti ufficiali |
| Basi e difesa aerea | Basi USA, NATO, Israele, Italia; siti iraniani; radar e batterie | Fonti datate, OurAirports, Wikidata |
| Energia | Oleodotti, gasdotti, condotte sottomarine | Global Energy Monitor (CC BY 4.0) |
| Logistica | Porti, rotte marittime, passaggi strategici con le quote mondiali di petrolio, gas, grano e merci | World Port Index, Benden (2022), EIA, UNCTAD e altre |
| AI | Data center e dossier per paese | Epoch AI, IEA, comunicati societari |
| Mercati | Indici, titoli AI, tassi USA, materie prime, valute; notizie che spiegano i movimenti | U.S. Treasury, Yahoo Finance, stampa finanziaria |

## Struttura

```
docs/            il sito (GitHub Pages): index.html e i dati in docs/data/
raccolta/        script di raccolta automatica
.github/workflows/  aggiornamento automatico quotidiano
METODO.md        fonti, affidabilità, verifiche, limiti
```

## Aggiornamento

- **Automatico:** ogni giorno feriale dopo la chiusura di Wall Street, GitHub Actions lancia `raccolta/scarica_mercati.py` e salva `docs/data/prezzi.json`. La cronologia dei commit è anche l'archivio storico.
- **Curato a mano:** eventi, report giornalieri e dossier richiedono verifica e giudizio, e si aggiornano con una revisione delle fonti.

Per lanciare la raccolta in locale (solo libreria standard di Python 3):

```bash
python3 raccolta/scarica_mercati.py docs/data/prezzi.json
```

## Avvertenze

Tutti i dati vengono da fonti aperte e già pubbliche. Il progetto è di analisi: non è uno strumento di tracciamento operativo e non dà consigli di investimento. Parte della raccolta e della scrittura è stata fatta con l'aiuto di un assistente AI (Claude); fonti e verifiche sono riportate punto per punto.
