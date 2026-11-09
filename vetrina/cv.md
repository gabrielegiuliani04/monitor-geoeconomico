# Righe per il CV

Numeri presi dai file in `docs/data/` e dai workflow al 9/11/2026. Prima di inviare il CV, ricontrollare quelli che cambiano ogni giorno (transiti, sanzioni, navi).

Fonti dei numeri: 24 livelli = caselle della mappa con dati; 42 file JSON in `docs/data/`; 15 script `raccolta/*/raccogli.py`; oltre 50 fonti dati distinte (elenco in `DATA_LICENSES.md`, senza contare i ~100 articoli citati nelle schede degli stretti); Hormuz e porti da `portwatch.json`; 2.022 navi da `sanzioni-navi.json`; 713 cavi da `cavi.json`; 840 terminali da `terminali-gnl.json`.

## English

**Geo-economic Risk Monitor**, personal project, 2026 · [gabrielegiuliani04.github.io/monitor-geoeconomico](https://gabrielegiuliani04.github.io/monitor-geoeconomico/) · [GitHub](https://github.com/gabrielegiuliani04/monitor-geoeconomico)

- Designed an open-source OSINT map that links disruptions at sea to their economic effects (event → chokepoint → flows → freight → prices → exposed countries and ports): 24 map layers built from 50+ public data sources.
- Defined the data schema and reliability rules (source, date, link and high/medium/low reliability on every data point; stated coordinate precision); 15 Python collectors refresh 42 data files daily via GitHub Actions.
- Tracked 13 maritime chokepoints and 9 Italian ports with IMF PortWatch data: showed Hormuz transits down 95% year on year (4.4 vs 90.3 ships/day) and compared it with Lloyd's List Intelligence, which also counts ships with AIS switched off.
- Wrote a case study on Hormuz and the Red Sea, connecting rerouting, freight rates, Brent/TTF and exposure of Italian gas routes and ports. Built with an AI coding assistant (Claude); I set the design, sources and checks and reviewed the output.

Short version (one line):
- *Geo-economic Risk Monitor (personal project): OSINT map linking shipping chokepoints, energy flows, freight and prices; 24 layers, 50+ open sources, daily automated collection with GitHub Actions; case study on Hormuz (−95% transits).*

## Italiano

**Monitor geoeconomico**, progetto personale, 2026 · [gabrielegiuliani04.github.io/monitor-geoeconomico](https://gabrielegiuliani04.github.io/monitor-geoeconomico/) · [GitHub](https://github.com/gabrielegiuliani04/monitor-geoeconomico)

- Ho progettato una mappa OSINT open source che collega le crisi in mare ai loro effetti economici (evento → passaggio strategico → flussi → noli → prezzi → paesi e porti esposti): 24 livelli costruiti da oltre 50 fonti pubbliche.
- Ho definito lo schema dei dati e le regole di affidabilità (fonte, data, link e affidabilità alta/media/bassa per ogni dato, precisione delle coordinate dichiarata); 15 script Python aggiornano ogni giorno 42 file di dati con GitHub Actions.
- Ho monitorato 13 passaggi strategici e 9 porti italiani con i dati IMF PortWatch: transiti a Hormuz −95% su un anno (4,4 contro 90,3 navi al giorno), confrontati con Lloyd's List Intelligence, che conta anche le navi con l'AIS spento.
- Ho scritto un caso di studio su Hormuz e Mar Rosso che collega deviazioni delle rotte, noli, Brent e TTF ed esposizione dei gasdotti e dei porti italiani. Realizzato con un assistente AI (Claude): io ho curato progettazione, fonti e verifiche e ho rivisto i risultati.

Versione breve (una riga):
- *Monitor geoeconomico (progetto personale): mappa OSINT di stretti, flussi energetici, noli e prezzi; 24 livelli, oltre 50 fonti aperte, raccolta automatica quotidiana con GitHub Actions; caso di studio su Hormuz (−95% dei transiti).*

## Parole chiave per i filtri ATS
OSINT · maritime risk · chokepoints · AIS · port calls · supply chain · energy security · LNG · freight rates · sanctions screening · data pipeline · Python · GitHub Actions · data visualization · d3 · open data

## Da adattare alla candidatura
- **Porti (Rotterdam, Aarhus, Gdańsk...)**: mettere prima la riga su PortWatch e porti, citare il caso dei porti italiani (Trieste −13%, Ravenna −40% di chiamate su un anno).
- **Energia offshore (Danimarca, Mare del Nord)**: citare cavi sottomarini, rete HVDC, interconnessioni e incidenti alle infrastrutture del Baltico.
- **Logistica**: citare noli (WCI, FBX, SCFI) e il confronto Shanghai–Genova contro Shanghai–Rotterdam.
