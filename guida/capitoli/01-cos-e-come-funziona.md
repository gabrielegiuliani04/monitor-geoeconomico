# Capitolo 1 — Cos'è e come funziona

> **Per chi è questa guida.** È per te, Gabriele. Serve a tre cose: capire come funziona il tuo sito, usarlo con sicurezza e presentarlo in un CV o a un colloquio (porti, logistica, energia offshore; Paesi Bassi, Danimarca, Baltico). I numeri vengono dai file del repository letti il **10 novembre 2026**; quelli che cambiano ogni giorno sono indicati «al 10 novembre 2026» con la data del dato. Prima di un colloquio ricontrollali nel file indicato. I termini tecnici sono spiegati nel glossario in appendice.

## 1.1 L'idea in una frase

Il Geo-economic Risk Monitor è una mappa aperta che segue uno shock dal punto in cui nasce fino a chi lo paga: *evento → passaggio strategico o infrastruttura → flussi → noli → prezzi → chi è esposto*. Ogni numero ha una fonte, una data e un livello di affidabilità.

> **Cosa dire al colloquio.** *"Geo-economic Risk Monitor is an open-source OSINT map that follows a shock from the event to the people who pay for it: event, chokepoint, flows, freight, prices, exposure. Every number carries a source, a date and a reliability level, and the data refresh automatically every day."*

### La catena, anello per anello

| Anello | Domanda | Dove lo trovi nel sito | File principali |
|---|---|---|---|
| 1. Evento | Che cosa è successo, dove, chi lo dice? | Punti sulla mappa (eventi, attacchi ibridi, Baltico) | `eventi.json`, `ibrido.json`, `baltico-sicurezza.json` |
| 2. Passaggio o infrastruttura | Che cosa è colpito o minacciato? | Rombi magenta degli stretti, condotte, cavi, terminali GNL, porti | `stretti-dettaglio.json`, `linee.json`, `cavi.json` |
| 3. Flussi | Passano ancora navi, gas, petrolio? | Scheda dello stretto; Terminal → *Chokepoints* | `portwatch.json`, `gas-italia.json`, `navi.json` |
| 4. Noli e costi | Quanto costa spostare la merce? | Terminal → *Freight and risk*, *Transit times* | `noli.json`, `assicurazioni.json`, `bunker-emissioni.json`, `transit-times.json` |
| 5. Prezzi | Come reagiscono petrolio, gas, tassi? | Terminal → *Prices and rates* | `prezzi.json` |
| 6. Chi è esposto | Quali Paesi, porti, settori pagano? | Terminal → *Risk*, *Ports*, *Northern Europe*, *Stocks*, *Countries* | `rischio.json`, `port-risk.json`, `esposizione-nord.json`, `scorte.json`, `italia-impatti.json` |

### Un esempio vero: Hormuz 2026

Nel 2025 dallo Stretto di Hormuz uscivano 19,9 milioni di barili di petrolio al giorno (IEA, febbraio 2026, citata nel report Hormuz). La guerra di Stati Uniti e Israele contro l'Iran inizia il 28 febbraio 2026; lo stretto è chiuso di fatto dal 2 marzo (report Hormuz, su dati PortWatch).

**Evento.** Esempi da `eventi.json`: il 7 novembre una petroliera in fiamme 8 miglia a nord-ovest di Khasab (avviso UKMTO 199-26, affidabilità **alta**, coordinate stimate con precisione 3 km); l'8 novembre «tre petroliere colpite su una rotta non autorizzata» (Al Jazeera che cita i Pasdaran: affidabilità **media**, perché è la rivendicazione di una parte in guerra).

**Flussi** (IMF PortWatch, `portwatch.json`, media 26 ottobre – 1° novembre 2026):

| Passaggio | Navi al giorno | Confronto | Variazione |
|---|---|---|---|
| Hormuz | 4,4 (1,4 petroliere) | 90,3 nella stessa settimana del 2025 | −95,1% |
| Bab el-Mandeb | 27,3 | 35,0 nella stessa settimana del 2025 | −22,0% |
| Canale di Suez | 43,0 | 39,0 (2025); 76,0 (2023) | +10,3% su un anno; −43,4% su tre |
| Capo di Buona Speranza | 92,0 | 48,6 nella stessa settimana del 2023 | +89,3% su tre anni |

Il traffico non è sparito: si è spostato. PortWatch però conta solo le navi con l'AIS acceso: nella settimana 19–25 ottobre conta 23 transiti a Hormuz, Lloyd's List Intelligence 116, perché ricostruisce anche le navi «al buio». Il sito mostra entrambe le cifre e spiega la differenza.

**Noli e costi.** Premio *war risk* per le petroliere a Hormuz: 6–10% del valore della nave per viaggio (FT via Insurance Business, 14 ottobre 2026), contro lo 0,2–0,25% di prima della guerra (`assicurazioni.json`): per una superpetroliera da 100 milioni di dollari, 6–10 milioni a transito. VLSFO a Rotterdam: 739,5 $/t il 6 novembre, +51,1% dal 27 febbraio (`bunker-emissioni.json`). Drewry WCI: 4.389 $/FEU il 5 novembre (`noli.json`).

**Prezzi** (`prezzi.json`, chiusure del 9 novembre lette il 10 alle 03:40 UTC; il file le segna ancora come provvisorie): Brent 91,70 $/barile (+44,1% su un anno), TTF 82,33 €/MWh (+163,9% su un anno).

**Chi è esposto.** Italia: il 32,6% del GNL importato arriva dal Qatar (UN Comtrade 2025, in valore), in forza maggiore dal 4 marzo; il TransMed dall'Algeria porta il 34,0% del gas entrato negli ultimi 12 mesi (`gas-italia.json`, ENTSOG); stoccaggi all'88,93% l'8 novembre contro una media quinquennale del 94,31%. Nord Europa: stoccaggi molto più bassi (Germania 58,94%, Paesi Bassi 63,51% l'8 novembre, `scorte.json`), ma il GNL olandese è per il 77% statunitense (IEEFA, 1° trimestre 2026): il Nord è esposto a Hormuz **soprattutto attraverso il prezzo** (il TTF è l'hub olandese).

> **Cosa dire al colloquio.** «Quando Hormuz si è chiuso, le navi visibili sono scese del 95%. Il traffico si è spostato sul Capo, l'assicurazione di guerra è passata da circa lo 0,2% al 6–10% del valore della nave, il carburante navale a Rotterdam è salito della metà e il gas europeo costa due volte e mezzo un anno fa. Per i porti del Nord il colpo arriva dai prezzi dell'energia, non dalle navi che mancano.»

*Lezione utile.* Alcuni testi del 9 novembre scrivono «Brent 92,62 $»: era una lettura in seduta delle 19:47 UTC, non la chiusura. Per questo lo standard dei report obbliga a marcare i prezzi in seduta come provvisori (`report/STANDARD.md`, punto 1).

## 1.2 Come è fatto (spiegato a chi non programma)

### Un sito «statico»

Il sito non ha un server che calcola qualcosa quando lo apri: è fatto di pagine HTML già pronte e di file di dati JSON, e il browser disegna la mappa da solo.

- **Dove sta:** su **GitHub Pages**, che pubblica la cartella `docs/` del repository all'indirizzo https://gabrielegiuliani04.github.io/monitor-geoeconomico/.
- **Quando cambia:** a ogni *commit* sul ramo `main` GitHub ripubblica il sito in pochi minuti.
- **Perché così:** costa zero, si rompe raramente, chiunque può controllare codice e dati, e la cronologia di git fa da archivio di ogni aggiornamento.

### Le parti del sito

| Parte | Cosa fa | Nome nell'interfaccia (inglese) |
|---|---|---|
| Mappa (`docs/index.html`) | Livelli da accendere e spegnere | Pannello *Layers* (cap. 2) |
| Viste | Sette inquadrature pronte | Menu *View…*: Europe and Middle East, North Sea and Baltic, Middle East, Russia–Ukraine, Europe, Italy, World |
| Terminale | 14 schede di dati | *Terminal*: Risk, Ports, Transit times, Wind calendar, Northern Europe, Prices and rates, Calendar, Chokepoints, Freight and risk, Stocks, Countries, Critical minerals, News, Ukraine (cap. 3) |
| Report | Analisi lunghe rivedute | *Reports* (`docs/report/`, inglese in `docs/report/en/`) |
| Notizie | Testate per argomento | *News feed* (`docs/notizie.html`) |
| Simulatore | «E se uno stretto si chiude?» | *"What if…" simulator* (`docs/simulatore.html`) |
| Guida rapida, crediti | Come si usa; fonti e licenze | *How to use it*; *Credits and licences* |

Il sito è tutto in inglese britannico dal 10 novembre 2026; molti testi generati dagli script (il «perché» del rischio, le sintesi degli stretti, il calendario) sono ancora in italiano, e il riquadro iniziale lo dichiara (*"Some source descriptions are in Italian"*).

### I dati: `docs/data/`

Al 10 novembre 2026 la cartella contiene **67 file JSON**: 66 di dati più `health.json`, il risultato del controllo di qualità (§4.6). Quasi tutti hanno la stessa forma (`raccolta/AGENTI.md`): `aggiornato` (quando lo script l'ha scritto), `fonti` (nome, link, licenza, data del dato), `nota` (che cosa il dato è e **non** è), `elementi` (i dati) ed `errori` (cosa non ha funzionato). I punti sulla mappa seguono uno schema comune di 25 campi (nome, data, coordinate, origine e precisione delle coordinate, fonte, link, data della fonte, affidabilità…). La tabella completa dei file è nel §4.1.

### Gli script di raccolta: `raccolta/`

Uno **script** è un piccolo programma Python che va su una fonte pubblica, scarica i dati, li controlla e scrive un file JSON. Al 10 novembre ci sono **37 script Python** in `raccolta/`: 33 raccolgono o calcolano dati (25 si chiamano `raccogli.py`, uno per dominio) e 4 fanno controlli (chiavi, qualità, simulatore, livelli originali). Quasi tutti usano solo la libreria standard di Python (eccezione: le navi, che usano `websockets`). Molti domini sono **curati**: le voci si scrivono a mano con fonte e data e lo script le **valida** (campi obbligatori, date, coordinate, link, voci da rivedere dopo 90 giorni). Ogni dominio ha un rapporto in `report/agenti/<dominio>.md` (33 rapporti): fonti provate, licenze, fatti, limiti.

### L'aggiornamento automatico: tre workflow

**GitHub Actions** accende un computer temporaneo a orari fissi, esegue i comandi di un file di istruzioni (*workflow*, in `.github/workflows/`) e si spegne. Ogni passo ha `continue-on-error: true`: se una fonte cade, le altre vanno avanti.

| Workflow | Quando | Che cosa fa |
|---|---|---|
| `aggiorna-dati.yml` | ogni giorno alle 05:15 UTC (06:15 in Italia con l'ora solare); anche a mano: *Actions → Aggiorna dati → Run workflow* | 17 passi di dati: flussi, noli, GPR e sanzioni; scorte; navi AIS; calendario; energia (GNL, gas Italia); Ucraina (lanci) e attacchi russi; notizie OSINT e testate; Nord Europa; bunker ed ETS; Italia (carburanti, PUN, inflazione, scioperi); stretti; calendario eolico; tempi di viaggio; per ultimi il cruscotto del rischio e il Port Risk Index, che leggono i file appena scritti. Poi mascheramento delle chiavi, test con il browser (*smoke test*), controllo di qualità e salvataggio con un commit. Tempo massimo 40 minuti |
| `aggiorna-mercati.yml` | lun–ven alle 21:30 UTC, dopo la chiusura di Wall Street | Prezzi di chiusura (Tesoro USA per i tassi, Yahoo Finance per il resto) → `prezzi.json` |
| `aggiorna-settimanale.yml` | ogni domenica alle 03:40 UTC | 11 passi: cavi, schede paese, rete elettrica e nucleare, ferrovie, AI e catena dell'AI, webcam, idrogeno, filiera eolica, aree war risk, basi; la prima domenica del mese anche commercio e minerali (circa 40 minuti) |

Restano fuori dai workflow, da lanciare a mano: incidenti cyber, storico del fronte (`fronte/`) e attacchi segnalati su Telegram da Clément Molin e AMK Mapping.

### Chiavi API, in breve

Alcune fonti chiedono una **chiave API** (una password personale). Il workflow ne passa quattro: `AISSTREAM_API_KEY`, `GFW_API_KEY`, `AGSI_API_KEY`, `BLS_API_KEY` (facoltativa). Le chiavi stanno cifrate nei *Secrets* di GitHub, mai nei file; se manca, lo script salta la fonte con un avviso; e `raccolta/comune/nascondi_chiavi.py` ripulisce i file pubblici prima di ogni salvataggio. Il caso della chiave AGSI finita in un file il 9 novembre e che cosa resta da fare sono nel §4.5.

### I report: script più revisione

I report più recenti sono prodotti da uno script Python (per esempio `report/build_northern_europe.py`) che legge i JSON e scrive Markdown e HTML con i grafici: i numeri del testo vengono dagli stessi file della mappa. Poi un revisore controlla ogni cifra; le correzioni si fanno nello script e il report si rigenera. Il processo e i report pubblicati sono nel §3.5.

### Gli agenti AI, detto onestamente

Il progetto è stato costruito con un assistente AI per la programmazione (Claude, tramite Claude Code). «Agente» vuol dire: una sessione dell'assistente con un compito preciso, regole scritte e cartelle sue.

- **Regia** (coordinatore): l'unica sessione che può modificare la mappa, il `manifest.json`, i workflow e `STATO.md`.
- **Agenti tematici**: uno per dominio, ciascuno con il suo script, il suo file e il suo rapporto, secondo `raccolta/AGENTI.md` (mai numeri inventati, fonte e data per ogni dato, niente chiavi nel codice).
- **Revisori**: sessioni AI separate che controllano un report contro `report/STANDARD.md`.
- **Coordinamento**: un file di stato condiviso, `STATO.md`, che ogni sessione legge per primo.

L'aggiornamento quotidiano lo fanno **script normali**, non l'AI: fanno ogni giorno la stessa cosa. Una «regia automatica» con sessioni AI programmate è **solo una proposta**, da attivare dopo il tuo via libera (`STATO.md`, *Da fare*, punto 4).

**Chi ha fatto cosa** (`README.md`, *My role*): tu hai definito la domanda e la catena, lo schema dei dati, le regole di affidabilità, le fonti e i compromessi sulle licenze, il flusso di lavoro e i controlli, e decidi cosa entra e cosa resta fuori. L'assistente ha scritto quasi tutto il codice, ha eseguito gli script, ha esplorato le fonti e ha scritto le bozze. Come dirlo a un colloquio è nel §5.4, domanda 15.

## 1.3 Il metodo

### Tre livelli di affidabilità

| Livello | Quando | Esempio da `eventi.json` |
|---|---|---|
| **Alta** | Fonte ufficiale, o almeno due fonti indipendenti | Petroliera in fiamme vicino a Khasab, 7 novembre: avviso UKMTO 199-26 |
| **Media** | Una fonte credibile, non ancora confermata | Tre petroliere colpite l'8 novembre: rivendicazione dei Pasdaran via Al Jazeera |
| **Bassa** | Non verificato, o rivendicazione senza conferme | Drone abbattuto su Qeshm, 6 novembre: prima segnalazione di un account su X |

Una rivendicazione di una parte in guerra non diventa mai un fatto: si scrive «i Pasdaran rivendicano». La regola delle due fonti applicata alle notizie è nel §3.4.

### Fatti e valutazioni

Un **fatto** è qualcosa che una fonte riporta, con fonte e data; una **valutazione** è un ragionamento dell'osservatorio (cause, scenari, «è un rischio»), marcata *Valutazione:* nei report e con un campo apposito nei JSON (per esempio `"valutazione": true` in `italia-impatti.json`). Esempio: 2.022 navi sono sanzionate da USA, Regno Unito o UE (**fatto**, liste ufficiali); 1.163 sono marcate `flotta_ombra_probabile` (**valutazione** della mappa) (`sanzioni-navi.json`, 9 novembre).

### Coordinate e tempo

Ogni punto dice se le coordinate vengono dalla **fonte** o sono **stimate** (`origine_coord`) e con quale raggio d'incertezza (`precisione_km`): la petroliera dell'avviso UKMTO ha 3 km, la Velos Sapphire «a nord del Qatar» 100 km. Gli eventi cambiano colore con l'età; le zone senza AIS lo dicono: «nessuna fonte per quest'area» non vuol dire «zero navi».

### Lo standard dei report e la revisione

`report/STANDARD.md` ha dieci regole: fonte, data e unità per ogni numero, e ogni variazione con il suo termine di confronto («−95% sulla stessa settimana del 2025»); fatti separati dalle valutazioni; incertezza dichiarata; tono senza allarmismi e nessun consiglio di investimento; un «In breve» di massimo 5 punti; limiti espliciti; grafici generati da script; italiano chiaro; trasparenza sull'AI; revisione indipendente di ogni numero.

| Report (pubblicati) | Affermazioni controllate | Corrette | File |
|---|---|---|---|
| Hormuz e Mar Rosso (9 nov) | 183 | 38 (10 non verificabili) | `report/revisioni/hormuz-mar-rosso-2026-11.md` |
| Supply chain e logistica (9 nov) | 59 | 9 | `report/revisioni/supply-chain-2026-11.md` |
| La catena dell'AI (10 nov) | 110 | 32 (16 non verificabili) | `report/revisioni/supply-chain-ai-2026-11.md` |
| Northern Europe: Ports and Energy (10 nov) | 64 | 12 | `report/revisioni/northern-europe-2026-11.md` |
| **Totale** | **416** | **91** | |

**La scoperta più utile.** Rivedendo il report Hormuz, il revisore ha trovato un errore nei **dati**: lo script dei prezzi convertiva l'ora di Yahoo Finance con il fuso di New York dell'ora solare anche nei mesi di ora legale, così tra l'8 marzo e il 1° novembre 2026 ogni seduta risultava un giorno prima. Lo script ora usa il fuso corretto per ogni data (`raccolta/scarica_mercati.py`). È la storia da raccontare (§5.4, domanda 17).

### Rischio = probabilità × impatto

Il cruscotto degli stretti e il Port Risk Index danno a ogni unità un punteggio da 1 a 25: probabilità di disruption (1–5) per impatto (1–5), come nei registri dei rischi aziendali (ISO 31000), ma con regole fisse su dati pubblici. Metodo, pesi, soglie e risultati del giorno sono nel §3.2.

## 1.4 Il flusso dei dati in un disegno

<figure class="schema">
<svg viewBox="0 0 900 430" xmlns="http://www.w3.org/2000/svg" font-family="IBM Plex Sans, sans-serif" font-size="12">
<defs><marker id="fr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#52606A"/></marker></defs>
<text x="10" y="18" font-weight="600" fill="#1D272D">FONTI PUBBLICHE</text>
<text x="250" y="18" font-weight="600" fill="#1D272D">SCRIPT (raccolta/)</text>
<text x="520" y="18" font-weight="600" fill="#1D272D">DATI (docs/data/)</text>
<text x="720" y="18" font-weight="600" fill="#1D272D">COSA VEDI</text>
<g fill="#ECEFEE" stroke="#86929A">
<rect x="10" y="30" width="200" height="34" rx="4"/><rect x="10" y="70" width="200" height="34" rx="4"/><rect x="10" y="110" width="200" height="34" rx="4"/><rect x="10" y="150" width="200" height="34" rx="4"/><rect x="10" y="190" width="200" height="34" rx="4"/><rect x="10" y="230" width="200" height="34" rx="4"/><rect x="10" y="270" width="200" height="34" rx="4"/><rect x="10" y="310" width="200" height="34" rx="4"/></g>
<g fill="#1D272D"><text x="20" y="52">IMF PortWatch (navi, porti)</text><text x="20" y="92">GIE AGSI+, Eurostat, ENTSOG</text><text x="20" y="132">AIS: Digitraffic, aisstream</text><text x="20" y="172">Sanzioni: OFAC, UK, UE</text><text x="20" y="212">Ship &amp; Bunker, Drewry, EEX</text><text x="20" y="252">UKMTO, stampa, OSINT</text><text x="20" y="292">Voci curate (JWC, eolico…)</text><text x="20" y="332">Tesoro USA, Yahoo Finance</text></g>
<rect x="250" y="40" width="220" height="150" rx="6" fill="#DCE8F5" stroke="#2F6DB5"/>
<text x="262" y="62" font-weight="600" fill="#1D3F6B">aggiorna-dati.yml</text><text x="262" y="80" fill="#1D3F6B">ogni giorno 05:15 UTC</text><text x="262" y="102" fill="#1D3F6B">17 passi indipendenti:</text><text x="262" y="120" fill="#1D3F6B">flussi, scorte, navi, energia,</text><text x="262" y="138" fill="#1D3F6B">Nord Europa, bunker, stretti…</text>
<rect x="262" y="150" width="196" height="32" rx="4" fill="#FBE3CC" stroke="#C26A12"/><text x="270" y="170" fill="#7A3E05">rischio + Port Risk (per ultimi)</text>
<rect x="250" y="205" width="220" height="44" rx="6" fill="#DCE8F5" stroke="#2F6DB5"/><text x="262" y="224" font-weight="600" fill="#1D3F6B">aggiorna-settimanale.yml</text><text x="262" y="241" fill="#1D3F6B">domenica 03:40 UTC, 11 passi</text>
<rect x="250" y="300" width="220" height="44" rx="6" fill="#DCE8F5" stroke="#2F6DB5"/><text x="262" y="319" font-weight="600" fill="#1D3F6B">aggiorna-mercati.yml</text><text x="262" y="336" fill="#1D3F6B">lun–ven 21:30 UTC → prezzi</text>
<path d="M520,60 a70,14 0 0,1 140,0 v230 a70,14 0 0,1 -140,0 z" fill="#DDEFE3" stroke="#2E8B57"/><ellipse cx="590" cy="60" rx="70" ry="14" fill="#C9E6D3" stroke="#2E8B57"/>
<g fill="#1B5E3A"><text x="532" y="110" font-weight="600">67 file JSON</text><text x="532" y="130">66 di dati +</text><text x="532" y="148">health.json</text><text x="532" y="176">aggiornato · fonti</text><text x="532" y="194">nota · elementi</text><text x="532" y="212">errori</text></g>
<rect x="250" y="372" width="410" height="40" rx="5" fill="#F3E6EC" stroke="#A61E6B"/><text x="262" y="390" fill="#6B0F43" font-weight="600">Prima di salvare: nascondi_chiavi.py → smoke test → controllo qualità</text><text x="262" y="405" fill="#6B0F43">→ commit su main → GitHub Pages ripubblica</text>
<g fill="#EEE3F3" stroke="#6E3D8F"><rect x="710" y="40" width="180" height="50" rx="5"/><rect x="710" y="105" width="180" height="50" rx="5"/><rect x="710" y="170" width="180" height="50" rx="5"/><rect x="710" y="235" width="180" height="50" rx="5"/></g>
<g fill="#3E1F55"><text x="722" y="62" font-weight="600">Mappa</text><text x="722" y="80">42 livelli tematici</text><text x="722" y="127" font-weight="600">Terminal</text><text x="722" y="145">14 schede</text><text x="722" y="192" font-weight="600">Reports</text><text x="722" y="210">script + revisione (416)</text><text x="722" y="257" font-weight="600">Simulatore, News feed</text><text x="722" y="275">health.json, report/qualita</text></g>
<g stroke="#52606A" stroke-width="1.4" fill="none" marker-end="url(#fr)"><path d="M212,120 H246"/><path d="M212,228 H246"/><path d="M212,326 H246"/><path d="M472,115 H516"/><path d="M472,227 H516"/><path d="M472,322 H516"/><path d="M662,65 H706"/><path d="M662,130 H706"/><path d="M662,195 H706"/><path d="M662,260 H706"/></g>
</svg>
<figcaption>Il flusso dei dati: fonti pubbliche → script nei tre workflow → file JSON → mappa, Terminal, report e simulatore. Ogni passo è indipendente: se una fonte cade, le altre continuano. Situazione dei workflow al 10 novembre 2026.</figcaption>
</figure>

### In sintesi (da rileggere prima di un colloquio)

1. **Che cos'è:** una mappa OSINT che segue la catena evento → stretto → flussi → noli → prezzi → esposizione, con fonte, data e affidabilità su ogni numero.
2. **Come funziona:** sito statico su GitHub Pages; 67 file JSON; 37 script Python; tre workflow GitHub Actions (ogni giorno, nei giorni feriali per i mercati, ogni domenica); chiavi nei Secrets e mascheramento automatico.
3. **Perché fidarsi:** tre livelli di affidabilità, fatti separati dalle valutazioni, precisione delle coordinate dichiarata, 416 affermazioni dei report controllate una per una, un controllo di qualità ogni mattina.
4. **Il valore per un porto o un'azienda energetica del Nord:** un punteggio di rischio trasparente per 18 stretti e corridoi e per 39 porti, che chiunque può rifare a mano.
5. **Il ruolo dell'AI:** l'assistente ha scritto il codice e le bozze; tu hai deciso domanda, metodo, fonti e controlli. L'aggiornamento quotidiano lo fanno script normali.
