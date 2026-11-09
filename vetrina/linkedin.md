# Post di lancio per LinkedIn

Consigli: pubblicare di martedì o mercoledì mattina (ora di Amsterdam/Copenaghen). Immagine: `docs/img/north-sea-baltic.jpg` o `docs/img/terminal-chokepoints.jpg`. Il link va nel post, non solo nel primo commento. Prima di pubblicare, aggiornare i numeri che cambiano (transiti, prezzi) e la data.

## English

Traffic through the Strait of Hormuz went from a monthly average of 78 ships a day in February 2026 to 3 in March. In the last week of October it averaged 4.4, against 90.3 a year earlier: −95% (IMF PortWatch).

A number like that only means something if you can follow what happens next. So I have been building a **Geo-economic Risk Monitor**: an open-source map that follows a disruption along the whole chain:

event → chokepoint → flows → freight rates → prices → who is exposed

What is on it:
🔹 13 chokepoints with daily transits, plus port calls in 9 Italian ports
🔹 pipelines, LNG terminals, submarine cables and the high-voltage grid, including the North Sea and the Baltic
🔹 AIS positions in the Gulf of Finland and 2,022 sanctioned vessels (US, UK, EU)
🔹 freight indices, Brent, TTF, US rates and a geopolitical risk index
🔹 a daily refresh from 50+ public sources, run by GitHub Actions

The rule I care about most: **no number without a source, a date and a reliability level**. When the coverage is missing, the map says so. A sea with no AIS coverage is not an empty sea.

I designed the questions, the data schema, the reliability rules and the checks. I wrote the code with an AI coding assistant (Claude), and I say so on the project page, because how you check AI output matters as much as the output.

The first case study is on Hormuz and the Red Sea: where the tankers went, what happened to freight and gas prices, and which ports and gas routes are most exposed.

🗺️ Map: https://gabrielegiuliani04.github.io/monitor-geoeconomico/
📄 Case study: https://gabrielegiuliani04.github.io/monitor-geoeconomico/report/hormuz-mar-rosso-2026-11.html
💻 Code: https://github.com/gabrielegiuliani04/monitor-geoeconomico

I am looking for roles in ports, logistics and offshore energy in the Netherlands, Denmark and the Baltic region. If you work on maritime or energy risk, I would really value your feedback, especially on what you would check first.

#OSINT #Shipping #Ports #Logistics #EnergySecurity #SupplyChain #OffshoreEnergy #DataVisualization

## Italiano

Il traffico nello Stretto di Hormuz è passato da una media di 78 navi al giorno a febbraio 2026 a 3 a marzo. Nell'ultima settimana di ottobre la media era 4,4, contro 90,3 un anno prima: −95% (IMF PortWatch).

Un numero così ha senso solo se si riesce a seguire cosa succede dopo. Per questo ho costruito un **Monitor geoeconomico**: una mappa open source che segue una crisi lungo tutta la catena:

evento → passaggio strategico → flussi → noli → prezzi → chi è esposto

Cosa contiene:
🔹 13 passaggi strategici con i transiti giornalieri e le navi in arrivo in 9 porti italiani
🔹 oleodotti, gasdotti, terminali GNL, cavi sottomarini e rete elettrica, anche nel Mare del Nord e nel Baltico
🔹 posizioni AIS nel Golfo di Finlandia e 2.022 navi sanzionate (USA, Regno Unito, UE)
🔹 noli, Brent, TTF, tassi USA e un indice di rischio geopolitico
🔹 aggiornamento quotidiano da oltre 50 fonti pubbliche, con GitHub Actions

La regola a cui tengo di più: **nessun numero senza fonte, data e livello di affidabilità**. Se una zona non è coperta, la mappa lo dice. Un mare senza copertura AIS non è un mare vuoto.

Ho progettato le domande, lo schema dei dati, le regole di affidabilità e le verifiche. Il codice l'ho scritto con un assistente AI (Claude), e lo dico nella pagina del progetto: come si controlla il lavoro di un'AI conta quanto il lavoro stesso.

Il primo caso di studio è su Hormuz e Mar Rosso: dove sono andate le petroliere, cosa è successo ai noli e al prezzo del gas, quali porti e gasdotti italiani sono più esposti.

🗺️ Mappa: https://gabrielegiuliani04.github.io/monitor-geoeconomico/
📄 Report: https://gabrielegiuliani04.github.io/monitor-geoeconomico/report/hormuz-mar-rosso-2026-11.html
💻 Codice: https://github.com/gabrielegiuliani04/monitor-geoeconomico

Cerco ruoli nei porti, nella logistica e nell'energia offshore nei Paesi Bassi, in Danimarca e nel Baltico. Se lavori sul rischio marittimo o energetico, un tuo parere mi sarebbe utile, soprattutto su cosa controlleresti per primo.

#OSINT #Shipping #Porti #Logistica #SicurezzaEnergetica #SupplyChain #EnergiaOffshore
