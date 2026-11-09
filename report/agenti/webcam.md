# Webcam pubbliche su stretti, canali, porti e ponti

Agente: WEBCAM PUBBLICHE · controllo del 9 novembre 2026 · file: `docs/data/webcam.json` (45 voci)

## Cosa contiene
45 webcam su punti di interesse geoeconomico, da mostrare sulla mappa come link "guarda dal vivo". Il 9-11-2026 **42 rispondevano** (HTTP 200, pagina giusta) e **3 non erano raggiungibili** da qui: İBB Istanbul e le due voci del Canale di Panama.

- Per categoria: 30 porti, 6 stretti, 5 canali, 3 ponti, 1 energia (Augusta). Per paese: NL 7, DE 7, IT 8, FI 3, LV 3, LT 2, HK 3, MT 2, GR 2, GB 2, DK/SE 2, TR 2, PA 2.
- Campi di ogni voce: `nome`, `inquadra`, `lat`/`lon` del **punto inquadrato** (stimati a mano, ±0,5–2 km), `paese`, `categoria` (stretto/canale/porto/energia/ponte), `proprietario`/`fonte`, `link`, `pagina` (la pagina indice ufficiale, quando il link punta a un singolo stream), `tipo` (immagine aggiornata / video live / YouTube live), `lingua`, `verificato_il`, `stato`, `esito_controllo`, `controlli_falliti`, `affidabilita`, `note`.
- Elenco curato: `raccolta/webcam/webcam.json` (si modifica a mano). Lo script `raccolta/webcam/raccogli.py` lo ricontrolla e scrive `docs/data/webcam.json`.

## Come lavora lo script (da far girare una volta alla settimana)
- Usa solo la libreria standard e un User-Agent onesto (`monitor-geoeconomico/1.0`), senza fingersi un browser.
- **Pagine web:** richiede HTTP 200 e un frammento atteso nel `<title>`. Serve perché alcuni siti, per esempio le pagine `/en/` delle telecamere del porto di Riga, rispondono "Page not found" con codice 200 o 404. Su SkylineWebcams controlla anche la scritta `OFFLINE`.
- **YouTube:** usa l'endpoint pubblico oEmbed, senza chiave. Conferma che il video esiste e che il **canale** è quello atteso, per esempio "Port of Rotterdam". La pagina youtube.com normale risponde 429 ai client automatici.
- Stati possibili: `attiva`, `offline`, `rotta`, `non_raggiungibile` (403/429/connessione chiusa: da verificare a mano da un browser). Lo script tiene `verificato_il` (ultima verifica riuscita) e `controlli_falliti` (fallimenti di seguito). Non fallisce mai per un link rotto.
- Workflow suggerito al coordinatore: un cron settimanale, per esempio il lunedì.

## Fonti provate
| Fonte | Esito | Note |
|---|---|---|
| Port of Rotterdam – mappa webcam (layer ArcGIS `Webcams_v2`) | funziona | 12 punti, ognuno con il suo link; 2 stream YouTube del porto stesso. Le altre webcam sono di siti locali linkati dal porto. |
| Port of Helsinki (6 pagine webcam) | funziona | Per vedere il video bisogna accettare i cookie di marketing. |
| Freeport of Riga (8 telecamere HLS) | funziona | Le pagine singole funzionano solo in lettone; l'indice in inglese è `rop.lv/en/port-webcams`. |
| Hafen Hamburg (Neuhof, Teufelsbrück) | funziona | Immagini aggiornate. |
| Città di Wedel (Willkomm-Höft, Altona, Schulauer Hafen) | funziona | Feed earthTV incorporato dalla città. |
| Port of Kiel (2 webcam) | funziona | Feed livespotting e feratel. |
| UCA Kiel Canal (chiuse di Holtenau e Brunsbüttel) | funziona | Agenzia marittima del canale. Il gestore pubblico WSV non pubblica webcam proprie. |
| Øresundsbron (2 telecamere sui piloni) | funziona | |
| Hong Kong Observatory | funziona | 34 punti foto, ne ho scelti 3 sul porto. |
| SkylineWebcams | funziona | Usato solo per le telecamere proprie (stream `livee.m3u8`), per gli stretti e i porti italiani. |
| Baltic Live Cam (Klaipėda) | funziona | Telecamere proprie installate su hotel e moli. |
| Autoridad del Canal de Panamá | **non raggiungibile da qui** | pancanal.com risponde 200 e il link "Web Cameras" porta a `multimedia.panama-canal.com`, che chiude la connessione. |
| İBB "İstanbul'u Seyret" (Bosforo) | **non raggiungibile da qui** | Connessione chiusa, forse per un filtro geografico. Fonte ufficiale: va tenuta e verificata da browser. |
| Port of Gdańsk – pagina "Cameras" | **sospesa** | Telecamere spente per il livello di allerta BRAVO. Anche le webcam Skyline di Gdańsk e Gdynia risultano OFFLINE, quindi le ho escluse. |
| Klaipėdos uostas (autorità portuale) | 403 | Rifiuta i client automatici. |
| webcamtaxi.com | 403 | Rifiuta i client automatici, quindi non verificabile senza fingersi un browser: escluso. |
| rotterdam.info | 200, ma contenuto caricato via JavaScript | Elenco non leggibile; le stesse webcam arrivano dalla mappa del porto. |
| Port of Antwerp-Bruges, Port of Dover, AdSP italiane (Genova, La Spezia, Civitavecchia, Ancona, Taranto, Gioia Tauro), MPA Singapore, Gibraltar Port | nessuna webcam pubblica trovata sui siti | I siti di Trieste, Venezia, Napoli e Sicilia orientale non erano raggiungibili da qui. |
| Suez Canal Authority | non raggiungibile; nessuna webcam ufficiale nota | Escluso. |

Il budget di ricerche web dell'ambiente è finito a metà lavoro. Le ultime verifiche le ho fatte leggendo direttamente i siti ufficiali.

**Licenze.** Il file contiene solo link. Immagini e video restano dei proprietari e **non vanno incorporati né copiati**. I link a SkylineWebcams e Baltic Live Cam portano a siti commerciali con pubblicità, che si possono linkare ma non ripubblicare.

## Fatti attuali (verificati il 9-11-2026)
1. **Port of Gdańsk** ha spento le dirette delle sue telecamere. Motivo: l'estensione del secondo livello di allerta (BRAVO, BRAVO-CRP) in tutta la Polonia, per decisione del Primo ministro (portgdansk.pl, pagina "Cameras"). Le webcam Skyline sul porto di Gdańsk e su Gdynia risultano OFFLINE lo stesso giorno. È un segnale di sicurezza ibrida nel Baltico (fatto); che sia collegato a minacce alle infrastrutture è una valutazione.
2. **Port of Rotterdam** pubblica una mappa di 12 webcam (layer ArcGIS `Webcams_v2`). Due sono stream YouTube del canale ufficiale "Port of Rotterdam": Nieuwe Waterweg e Amazonehaven west sulla Maasvlakte.
3. **Freeport of Riga** elenca 8 telecamere sulla pagina "Port Webcams" (foce della Daugava, faro di Daugavgrīva, Krievu sala, Kundziņsala, torre VTS).
4. **Port of Helsinki** ha 6 pagine webcam: South Harbour, West Harbour, LT1, LT2, area P e Vuosaari, il porto merci principale.
5. **Amburgo, webcam Neuhof:** sta a circa 62 m sul silo ADM e cambia posizione ogni 20 secondi. Inquadra i terminal container, la stazione piloti e Finkenwerder (hafen-hamburg.de).
6. **Canale di Kiel:** l'agenzia UCA trasmette in diretta le chiuse di Kiel-Holtenau e di Brunsbüttel (kiel-canal.de/webcam).
7. **Hong Kong Observatory:** 34 punti foto pubblici; 3 inquadrano Victoria Harbour (Museo marittimo, Central Pier, ICC).
8. **Canale di Panama:** l'ACP linka ancora dalla home "Web Cameras" → multimedia.panama-canal.com, ma il server non era raggiungibile da questo ambiente.
9. **Nessuna webcam pubblica ufficiale trovata** per Canale di Suez, Stretto di Gibilterra, porto di Anversa, Singapore e per le autorità portuali italiane. In Italia la copertura passa da SkylineWebcams: Genova, Stretto di Messina, Palermo, Augusta, Venezia, Trieste.
10. **Ponte di Crimea:** escluso. Non esiste una fonte pubblica affidabile che lo trasmetta; le dirette che si trovano sono russe o non verificabili.

## Collegamenti con gli altri livelli della mappa
- **Stretti** (`stretti.json`): Bosforo (İBB), Øresund/Stretti danesi (ponte e Flintrännan), Passo di Calais (Deal, Dover), Stretto di Messina, Canali di Kiel e di Panama. Il popup di uno stretto può mostrare "guarda dal vivo".
- **Porti, GNL ed energia** (`terminali-gnl.json`, `condotte.json`): Augusta–Priolo (raffinerie), Trieste (golfo dove ancorano le petroliere per l'oleodotto TAL), Klaipėda (GNL), Brunsbüttel (FSRU), Rotterdam (Botlek e Pernis, da Maassluis e Vlaardingen). In nessuno di questi casi il terminale energetico è inquadrato direttamente: è scritto nelle note.
- **Eventi e rischio ibrido** (`ibrido.json`, `cavi-incidenti.json`): lo spegnimento delle webcam di Gdańsk è esso stesso un dato. Lo script lo coglie come `offline` o `rotta` se una webcam sparisce, e può servire da indicatore.
- **Navi** (`navi.json`, `portwatch.json`): la webcam conferma visivamente quello che l'AIS mostra, per esempio code al Nieuwe Waterweg o navi in chiusa a Kiel.

## Proposta per la mappa
- Livello "Webcam", spento di default, con una piccola icona a forma di telecamera. Colore per `stato`: verde attiva, grigio `non_raggiungibile`, rosso `rotta`/`offline`.
- Popup: nome, cosa inquadra, proprietario, tipo e lingua, data di `verificato_il`, pulsante **"Guarda dal vivo ↗"** che apre `link` in una nuova scheda (`rel="noopener"`). **Nessun iframe.**
- Nascondere o grigiare le voci con `controlli_falliti >= 2`.

## Limiti
- Le coordinate sono stime del punto inquadrato, non la posizione della telecamera.
- "Risponde 200" non garantisce che il video stia andando in quel momento. Vale soprattutto per i player esterni (Helsinki, Riga, Kiel, Wedel). Per Skyline lo script legge il flag OFFLINE; per YouTube oEmbed conferma che il video esiste, non che la diretta sia in onda.
- Copertura debole su Bosforo, Dardanelli, Gibilterra, Suez, Singapore e Anversa, e porti italiani solo tramite una rete commerciale.
- Due voci (Panama) e una (İBB) vanno confermate da un browser normale.
- Regole rispettate: nessuna telecamera esposta per errore (Insecam/Shodan), nessun IP diretto, nessun login aggirato, nessun video incorporato.
