# Tracciamento navi — rapporto dell'agente (9 novembre 2026)

Script: `raccolta/navi/raccogli.py` (libreria standard; solo aisstream.io usa il pacchetto `websockets`, in `raccolta/navi/requirements.txt`, ed è facoltativo).
Dato: `docs/data/navi.json` (eseguito davvero il 9/11/2026 alle 19:01 UTC). Tempo di esecuzione senza chiavi: circa 5 secondi; con la DMA attiva serve scaricare un file da centinaia di MB (da GitHub Actions va bene).

## Fonti provate

| Fonte | Esito da qui | Chiave | Licenza | Copertura utile |
|---|---|---|---|---|
| **Digitraffic marittimo (Fintraffic, Finlandia)** `meri.digitraffic.fi/api/ais/v1/locations` + `/vessels` | **Funziona** (1.099 posizioni, 991 schede nave) | nessuna (solo l'intestazione `Digitraffic-User`) | CC BY 4.0 | Golfo di Finlandia fino a San Pietroburgo, Primorsk e Ust-Luga, Baltico a nord di 57°N. Solo l'ultima posizione per nave: niente storico via API |
| **Danish Maritime Authority, AIS storici** (file giornalieri `aisdk-AAAA-MM-GG.zip`) | **Non raggiungibile da questo ambiente**: `aisdata.ais.dk` risponde solo in HTTP semplice (il proxy dell'ambiente lascia passare solo HTTPS), `web.ais.dk` ha un certificato TLS non valido (scaduto o con nome sbagliato). Codice scritto e provato su un CSV di prova con lo stesso formato | nessuna | uso libero citando la DMA | Stretti danesi (Skagerrak, Kattegat, Grande Belt, Øresund). Su GitHub Actions dovrebbe funzionare (HTTP diretto) |
| **aisstream.io** (WebSocket) | Host raggiungibile; con una chiave non valida chiude la connessione. Non provato con una chiave vera | **gratuita** (`AISSTREAM_API_KEY`) | termini del servizio | Mondiale, ma da ricevitori volontari a terra: buona nel Bosforo e a Suez, scarsa nel mezzo di Hormuz e di Bab el-Mandeb |
| **Global Fishing Watch API v3** | Host raggiungibile (401 senza chiave). Codice pronto, non provato | **gratuita**, uso non commerciale (`GFW_API_KEY`) | CC BY-NC 4.0 (da segnalare: va bene solo perché il progetto non è commerciale) | Eventi "AIS gap" (transponder spento) e incontri in mare, da satellite, ultimi 30 giorni |
| **USNI News Fleet and Marine Tracker** (API WordPress del sito) | **Funziona**. L'ultimo tracker pubblicato alle 19:00 UTC del 9/11 è quello del **2 novembre** (quello del 9 non è ancora in linea) | nessuna | articolo con copyright: si estraggono solo fatti (nave, area) | Aree dichiarate di portaerei, gruppi anfibi e cacciatorpediniere USA. Nessuna coordinata |
| AISHub | non provato | serve contribuire con una propria stazione AIS | — | — |
| MarineTraffic, VesselFinder, Spire, Kpler | non provati | **a pagamento** | — | soltanto da segnalare |
| BarentsWatch (Norvegia) | non provato | registrazione gratuita (client OAuth) | NLOD | acque norvegesi e Mare di Barents: alternativa possibile |

## Cosa contiene `navi.json`

- `elementi`: una voce per nave con `mmsi, imo, nome, tipo, bandiera, lat, lon, velocita_nodi, rotta_gradi, ora_utc, area, sanzionata, fonte`, più `destinazione`, `pescaggio_m` e `scia` (lista `[lon, lat, ora_utc]`, fino a 12 punti negli ultimi 7 giorni, accumulati rileggendo il file precedente a ogni esecuzione). Si tengono le petroliere e gasiere (AIS 80–89) e le navi militari (AIS 35) dentro i riquadri degli stretti, più ogni nave sanzionata ovunque nella copertura.
- `riepilogo_aree`: per ognuno dei 6 stretti, petroliere viste, quante sanzionate, transiti stimati (solo Stretti danesi) e le fonti. Un'area senza fonte attiva riporta 0 con la nota "nessuna fonte gratuita attiva": **non vuol dire zero navi**.
- `militari_usni`: 35 navi USA dal tracker del 2/11, con l'area dichiarata e come coordinata il **centro dell'area** (`origine_coord`, `precisione_km` da 250 a 2.000 km).
- `avvisi_ais`: eventi GFW (vuoto finché manca la chiave).
- `bandiera`: è quella dichiarata dalle prime 3 cifre dell'MMSI (tabella parziale nello script), non quella del registro.
- `sanzionata`: oggi vale sempre **"non verificato"**, perché `docs/data/sanzioni-navi.json` non esisteva ancora quando lo script è girato. Appena l'altro agente lo produce, lo script incrocia IMO e MMSI senza bisogno di modifiche (lo schema viene letto in modo tollerante: `elementi`/`navi`, `imo`, `mmsi`, `sanzionata_da`/`programmi`/`liste`).
- Nessun dato personale: solo identificativi della nave.

## Fatti dal dato di oggi

Fatti (Digitraffic, istantanea del 9/11/2026, 19:00 UTC, salvo dove indicato):
1. Nel riquadro del Golfo di Finlandia ci sono **90 petroliere e gasiere** con AIS acceso; 85 hanno trasmesso nelle ultime 6 ore e 18 navigano a più di 3 nodi.
2. **50 delle 90** sono a est di 27,8°E, cioè nelle acque dei porti russi (Primorsk, Ust-Luga, San Pietroburgo). Le destinazioni dichiarate più frequenti: Ust-Luga (varie grafie, almeno 16), "RU LED"/San Pietroburgo, Primorsk, e "BALTIC/GOF FOR ORDERS" (carico senza destinazione dichiarata).
3. 16 di queste 50 dichiarano un **pescaggio di almeno 11 m**, cioè sono cariche o in carico.
4. Bandiere da MMSI delle 90: Russia 23, Isole Marshall 9, Liberia 9, **Sierra Leone 9**, Barbados 5, Panama 4, **Guinea Equatoriale 4**, Estonia 4, Malta 4, Camerun 3, Oman 2, Gambia 1, Palau 1 e altre.
5. Nel Golfo di Finlandia sono visibili anche **7 unità militari con AIS acceso** (tipo 35): marina finlandese (FNS Louhi, FNS Pori), estone e unità che trasmettono il nome generico "NATO WARSHIP".
6. USNI, tracker del **2 novembre 2026**: due portaerei nel Mar Arabico, **George Washington (CVN-73)** e **George H. W. Bush (CVN-77)**, con 12 tra cacciatorpediniere e incrociatori nella stessa sezione; due cacciatorpediniere nel Mar Rosso (Jason Dunham, Gonzalez); il gruppo anfibio **Boxer** (LHD-4, con Comstock e Portland) nell'Oceano Indiano; Theodore Roosevelt (CVN-71) nel Mar Cinese Meridionale; Eisenhower (CVN-69) e Nimitz (CVN-68) nell'Atlantico occidentale; Ronald Reagan (CVN-76) nel Pacifico orientale.
7. Hormuz, Bab el-Mandeb, Suez e Bosforo: **oggi nessun dato di posizione**, perché le uniche fonti gratuite per quelle aree (aisstream.io e GFW) richiedono una chiave.

Valutazioni (non fatti):
- Bandiere come Sierra Leone, Guinea Equatoriale, Camerun, Barbados, Gambia e Palau, insieme a "for orders" come destinazione, sono tipiche della flotta ombra russa. **Ma senza l'incrocio con le liste di sanzioni non si può dire quante delle 90 siano sanzionate**: è il primo controllo da fare appena c'è `sanzioni-navi.json`.
- Le navi che spengono l'AIS non compaiono: il conteggio è un minimo.

**Flotta ombra negli Stretti danesi in un giorno: oggi non è ricavabile**, perché il file DMA non è scaricabile da questo ambiente. Lo script lo calcola già (`riepilogo_aree["Stretti danesi"]`): petroliere viste nel giorno, quante sanzionate, e "transiti stimati", cioè navi viste nello stesso giorno sia a sud di 55,7°N sia a nord di 56,5°N. Va eseguito su GitHub Actions o in locale.

## Chiavi gratuite da chiedere all'utente

1. **`AISSTREAM_API_KEY`** (aisstream.io, accesso con GitHub): è l'unica fonte gratuita di posizioni in tempo reale per Hormuz, Bab el-Mandeb, Suez e Bosforo. Lo script ascolta per `AISSTREAM_MINUTI` (10 minuti di default) i riquadri dei 6 stretti. Con `AISSTREAM_SOLO_SANZIONATE=1` filtra fino a 50 MMSI sanzionati. Su GitHub Actions serve `pip install -r raccolta/navi/requirements.txt`.
2. **`GFW_API_KEY`** (globalfishingwatch.org, uso non commerciale): segnala i "gap" AIS (navi che spengono il transponder) e gli incontri in mare, quindi i trasbordi da nave a nave, negli ultimi 30 giorni dentro i riquadri. È l'unico modo gratuito per l'avviso di AIS spento basato su un dato vero.
3. Facoltativa: una registrazione BarentsWatch, per il Mare del Nord e il Barents (rotta da Murmansk).

Variabili utili: `NAVI_DMA=0` salta la DMA (download pesante); `NAVI_DMA_GIORNO=AAAA-MM-GG` sceglie il giorno.

## Collegamenti con gli altri livelli della mappa

- **Stretti** (`stretti.json`, `portwatch.json`): le petroliere viste qui sono il dettaglio nave per nave dietro i transiti aggregati di PortWatch, che va usato per i volumi.
- **Sanzioni** (`sanzioni-navi.json`): fornisce il campo `sanzionata`.
- **Oleodotti, terminali e cavi**: Primorsk e Ust-Luga sono i terminali del greggio russo nel Baltico. Le petroliere ferme sopra i cavi del Golfo di Finlandia sono un segnale da incrociare con `cavi-incidenti.json` (precedente: Eagle S, dicembre 2024).
- **Mezzi militari** (`mobili.json`, non modificato): `militari_usni` è una fonte di conferma settimanale delle aree, da affiancare ai punti stimati già in mappa.

## Proposta per la mappa

- **Petroliere**: piccoli triangoli orientati secondo la rotta. Grigi se `sanzionata` è "no" o "non verificato"; **rossi con alone** se è "sì", con la lista sanzionatrice nel popup.
- **Scia**: polilinea sottile delle ultime 12 posizioni (`scia`), visibile solo per le navi sanzionate o al passaggio del mouse.
- **AIS spento**: icona con punto esclamativo sull'ultima posizione nota quando c'è `avviso_ais` (nave sanzionata ferma da più di 6 ore) o un evento GFW "AIS spento". Quando la nave ricompare, un tratteggio tra l'ultimo punto prima del buio e il primo dopo.
- **Incontri in mare** (GFW): due cerchi sovrapposti, a indicare un possibile trasbordo.
- **Riquadro degli stretti**: un'etichetta "N petroliere, M sanzionate (fonte, ora)" e la scritta "nessuna fonte" se l'area non è coperta.
- **Navi militari USNI**: cerchio semitrasparente grande quanto `precisione_km`, mai un punto preciso, con la data del tracker.

## Limiti

- L'AIS si spegne o si falsifica (spoofing, frequente nel Golfo e nel Baltico). Le navi della flotta ombra spesso trasmettono a intermittenza.
- Digitraffic copre solo il Baltico settentrionale e dà solo l'ultima posizione: le scie si costruiscono esecuzione dopo esecuzione.
- Le coordinate USNI sono il centro dell'area dichiarata, non posizioni.
- Il codice per DMA, aisstream e GFW è scritto ma non è stato provato su dati reali da qui: la DMA è bloccata dalla rete, per gli altri due mancano le chiavi. Il lettore DMA è stato provato su un CSV di prova con lo stesso formato.
- La bandiera è quella dichiarata nell'MMSI; navi che cambiano bandiera spesso (flotta ombra) possono avere un MMSI non aggiornato.
