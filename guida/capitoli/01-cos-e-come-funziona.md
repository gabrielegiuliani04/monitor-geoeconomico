# Capitolo 1 — Cos'è e come funziona

> **Per chi è questa guida.** È per te, Gabriele. Serve a tre cose: capire bene come funziona il tuo sito, saperlo usare con sicurezza e saperlo spiegare in un CV o a un colloquio (porti, logistica, energia offshore; Paesi Bassi, Danimarca, Baltico).
>
> **Regola del capitolo.** Ogni numero ha accanto il file da cui viene e la data del dato. I file sono quelli di `docs/data/` nel repository, letti il 10 novembre 2026. Se riapri i file in un altro giorno, i numeri saranno diversi: è normale, i dati si aggiornano ogni mattina.
>
> **Nota sulla lingua dell'interfaccia.** Mentre scrivo, un altro agente sta traducendo il sito in inglese. Uso i nomi inglesi quando sono già nel codice del sito (`docs/index.html`) e quelli italiani negli altri casi. Dove non sono sicuro scrivo **[da controllare dopo la traduzione]**.

---

## 1.1 L'idea in una frase

**In italiano.** Il Monitor geoeconomico è una mappa aperta che segue uno shock dal punto in cui nasce fino a chi lo paga: *evento → passaggio strategico o infrastruttura → flussi → noli → prezzi → chi è esposto*. Ogni numero ha una fonte, una data e un livello di affidabilità.

**In inglese, da dire a un colloquio.** *"Geo-economic Risk Monitor is an open-source OSINT map that follows a shock from the event to the people who pay for it: event, chokepoint, flows, freight, prices, exposure. Every number carries a source, a date and a reliability level, and the data refresh automatically every day."*

### La catena delle conseguenze, anello per anello

Un problema in mare raramente resta in mare. La catena dice in che ordine guardare le cose:

| Anello | Domanda | Dove lo trovi nel sito | File principali |
|---|---|---|---|
| **1. Evento** | Che cosa è successo, dove, quando, chi lo dice? | Punti sulla mappa (eventi, attacchi ibridi, fronte) | `eventi.json`, `ibrido.json`, `baltico-sicurezza.json` |
| **2. Passaggio strategico o infrastruttura** | Che cosa è stato colpito o minacciato? | Rombi magenta degli stretti, condotte, cavi, terminali GNL, porti | `stretti.json`, `stretti-dettaglio.json`, `linee.json`, `cavi.json`, `terminali-gnl.json` |
| **3. Flussi** | Passano ancora le navi, il gas, il petrolio? | Scheda dello stretto; Terminal → *Chokepoints* | `portwatch.json`, `gas-italia.json`, `navi.json` |
| **4. Noli e costi del trasporto** | Quanto costa spostare la merce? | Terminal → *Freight and risk* | `noli.json`, `assicurazioni.json`, `bunker-emissioni.json`, `transit-times.json` |
| **5. Prezzi** | Come reagiscono petrolio, gas, tassi? | Terminal → *Prices and rates* | `prezzi.json` |
| **6. Chi è esposto** | Quali Paesi, porti e settori pagano di più? | Terminal → *Countries*, *Stocks*, *Northern Europe*, *Risk* | `scorte.json`, `esposizione-nord.json`, `italia-impatti.json`, `rischio.json`, `port-risk.json` |

### Un esempio vero: Hormuz 2026

Lo Stretto di Hormuz collega il Golfo Persico all'oceano. Nel 2025 da lì uscivano 19,9 milioni di barili di petrolio al giorno (IEA, *Strait of Hormuz Factsheet*, febbraio 2026, citata in `report/hormuz-mar-rosso-2026-11.md`). Ecco la catena con i dati del sito.

**Anello 1 — Evento.** La guerra di Stati Uniti e Israele contro l'Iran inizia il 28 febbraio 2026 (report Hormuz, che cita `report.json` e Al Jazeera). Nella prima settimana di novembre gli attacchi alle navi continuano. Esempi da `eventi.json`:

- 7 novembre: petroliera in fiamme 8 miglia a nord-ovest di Khasab. Fonte: UKMTO, avviso 199-26 (data della fonte 8 novembre). Affidabilità **alta**. Coordinate **stimate**, precisione 3 km.
- 8 novembre: «tre petroliere colpite su una rotta non autorizzata». Fonte: Al Jazeera, che cita i Pasdaran. Affidabilità **media**, perché è la rivendicazione di una parte in conflitto. Precisione 40 km.

**Anello 2 — Passaggio strategico.** Hormuz è chiuso di fatto dal 2 marzo 2026 (report Hormuz, su dati PortWatch). Non esiste una vera alternativa via mare. Gli oleodotti che lo aggirano arrivano a Yanbu (Mar Rosso) e a Fujairah, entrambi in zone di guerra per gli assicuratori (`assicurazioni.json`, scheda di esempio «hormuz-vlcc-ottobre-2026»).

**Anello 3 — Flussi.** I numeri di IMF PortWatch (`portwatch.json`, ultimo dato 1° novembre 2026):

| Passaggio | Navi al giorno, media 26 ott – 1 nov 2026 | Confronto | Variazione |
|---|---|---|---|
| Hormuz | 4,4 (di cui 1,4 petroliere) | 90,3 nella stessa settimana del 2025 (50,1 petroliere) | −95,1% |
| Bab el-Mandeb | 27,3 | 35,0 nella stessa settimana del 2025 | −22,0% |
| Canale di Suez | 43,0 | 39,0 nella stessa settimana del 2025; 76,0 in quella del 2023 | +10,3% su un anno; −43,4% su tre anni |
| Capo di Buona Speranza | 92,0 | 48,6 nella stessa settimana del 2023 | +89,3% su tre anni |

Il traffico non è sparito: si è spostato. Attenzione però a un limite importante. PortWatch conta solo le navi con il transponder AIS acceso. Nella settimana 19–25 ottobre PortWatch conta 23 transiti a Hormuz; Lloyd's List Intelligence ne conta 116, perché ricostruisce anche le navi «al buio» (report Hormuz, LLI del 5 novembre 2026). Il sito mostra entrambe le cifre e spiega perché sono diverse.

**Anello 4 — Noli e costi.**

- **Assicurazione di guerra.** A Hormuz il premio *war risk* per le petroliere è tra il 6% e il 10% del valore della nave per viaggio (Financial Times, ripreso da Insurance Business il 14 ottobre 2026; dato riferito al 7 ottobre; `assicurazioni.json`). Il 27 febbraio 2026, prima della guerra, la serie del file segna 0,2%. Per una superpetroliera da 100 milioni di dollari vuol dire 6–10 milioni per un transito: circa 40 volte il premio prebellico e 3–5 dollari per barile trasportato (calcolo passo per passo in `assicurazioni.json`, `esempi_costo`).
- **Carburante delle navi.** Il VLSFO (il carburante navale più usato) a Rotterdam costa 739,5 $/t il 6 novembre 2026, +51,1% dal 27 febbraio (489,5 $/t). A Singapore 854 $/t, +63,8% (`bunker-emissioni.json`, Ship & Bunker).
- **Noli container.** Il Drewry World Container Index è a 4.389 $ per container da 40 piedi (FEU) il 5 novembre 2026. Shanghai–Genova costa 4.166 $, Shanghai–Rotterdam 3.615 $ (`noli.json`).

**Anello 5 — Prezzi.** Da `prezzi.json` (file aggiornato il 10 novembre alle 03:40 UTC, chiusure del 9 novembre):

- **Brent**: 91,70 $/barile, −6,7% in giornata, +44,1% su un anno.
- **TTF** (gas in Europa): 82,33 €/MWh, −3,8% in giornata, +163,9% su un anno.

*Lezione utile.* I report del 9 novembre scrivono «Brent 92,62 $». Non è un errore: era la lettura provvisoria delle 19:47 UTC, durante la seduta. La chiusura definitiva, arrivata di notte, è 91,70. Per questo lo standard dei report obbliga a segnare i prezzi in seduta come «provvisori» (`report/STANDARD.md`, punto 1; `report/revisioni/supply-chain-ai-2026-11.md`).

**Anello 6 — Chi è esposto.**

*Italia.*
- Il 32,6% del GNL importato arriva dal Qatar, che passa da Hormuz (UN Comtrade 2025, quote in valore; report Hormuz). Il Qatar è in forza maggiore dal 4 marzo 2026.
- La dipendenza più grande però è vicina: il gasdotto TransMed dall'Algeria (ingresso a Mazara del Vallo) porta il 34,0% del gas entrato da gasdotti e GNL negli ultimi 12 mesi (`gas-italia.json`, dati ENTSOG al 8 novembre 2026).
- Stoccaggi di gas: 88,93% l'8 novembre, contro una media di 5 anni del 94,31% (`scorte.json`, GIE AGSI+).
- Scorte petrolifere di emergenza: 77,2 giorni ad agosto 2026, contro 89,26 di media in 5 anni (`scorte.json`, Eurostat).
- Porti: nella settimana al 30 ottobre, rispetto alla stessa settimana del 2025, le navi in arrivo calano a Ravenna (−39,8%), Venezia Lido (−37,8%) e Trieste (−13,1%); crescono ad Augusta (+14,6%) (`portwatch.json`).
- Pompa: gasolio a 2,238 €/litro nella settimana del 2 novembre 2026 (`italia-impatti.json`, dati MASE).

*Nord Europa.*
- Gli stoccaggi di gas sono molto più bassi che in Italia: Germania 58,94% e Paesi Bassi 63,51% l'8 novembre, contro medie di 5 anni dell'88,61% e dell'82,40% (`scorte.json`).
- Il GNL dei Paesi Bassi arriva per il 77% dagli Stati Uniti; quello della Polonia per il 21% dal Qatar (IEEFA, 1° trimestre 2026; `esposizione-nord.json`). Quindi il Nord Europa è esposto a Hormuz **soprattutto attraverso il prezzo** (il TTF è l'hub olandese), meno attraverso i volumi.
- Il cruscotto del rischio dà a Hormuz 22,5 su 25 (**critico**) e al GNL del Qatar 24,0 (**critico**). Il TransMed è a 5,6 (**basso**, ma con impatto alto: 4,3 su 5) (`rischio.json`, 9 novembre 2026).
- Il Port Risk Index dà a Rotterdam 7,5 (*medium*): probabilità bassa (1,5) ma impatto massimo (5,0) (`port-risk.json`, 10 novembre 2026).

> **Come raccontarlo in 30 secondi.** «Quando Hormuz si è chiuso, le navi visibili sono scese del 95%. Il traffico si è spostato sul Capo di Buona Speranza, l'assicurazione di guerra è passata da circa lo 0,2% a 6–10% del valore della nave, il carburante navale a Rotterdam è salito della metà e il gas europeo costa oltre due volte e mezzo un anno fa. Per i porti del Nord il colpo arriva dal prezzo del gas e del carburante, non dalle navi che mancano.»

---

## 1.2 Come è fatto (spiegato a chi non programma)

### Il principio: un sito «statico»

Il sito non ha un server che calcola qualcosa quando lo apri. È fatto di pagine già pronte (HTML) e di file di dati (JSON). Il tuo browser scarica le pagine e i dati e disegna la mappa da solo.

- **Dove sta:** su **GitHub Pages**, il servizio gratuito di GitHub che pubblica una cartella del repository come sito. La cartella è `docs/`. Indirizzo: https://gabrielegiuliani04.github.io/monitor-geoeconomico/
- **Quando cambia:** a ogni modifica salvata sul ramo `main` del repository (un *commit*), GitHub ripubblica il sito in pochi minuti (`STATO.md`).
- **Perché così:** costa zero, non si rompe quasi mai, chiunque può controllare il codice e i dati. In più la cronologia di git fa da archivio: ogni aggiornamento giornaliero dei dati resta salvato come commit (`README.md`).

### Le parti del sito

| Parte | Cosa fa | Nome nell'interfaccia |
|---|---|---|
| Mappa (`docs/index.html`) | Mappa interattiva: si accendono e spengono i livelli | Pannello *Layers*, con le sezioni *Theatres*, *Categories*, *Fixed layers*, *Infrastructure and flows* |
| Menu delle viste | Salta a un'area: Europa e Medio Oriente, Mare del Nord e Baltico, Medio Oriente, Russia-Ucraina, Europa, Italia, Mondo | Menu *View…* (i nomi delle viste vengono da `manifest.json` e sono ancora in italiano nel file) **[da controllare dopo la traduzione]** |
| Terminale | Pannello con le schede di dati | *Terminal*, con le schede *Risk*, *Northern Europe*, *Prices and rates*, *Calendar*, *Chokepoints*, *Freight and risk*, *Stocks*, *Countries*, *News*, *Ukraine*, *Dossier*, *Critical minerals*, *Markets* **[ordine e presenza delle schede da controllare dopo la traduzione]** |
| Report | Analisi lunghe, in italiano e in inglese | *Reports* (`docs/report/`, versioni inglesi in `docs/report/en/`) |
| Notizie | 57 testate raccolte per argomento (`STATO.md`) | *News feed* (`docs/notizie.html`) |
| Simulatore | «Che cosa succede se…» uno stretto si chiude per un certo periodo | *"What if…" simulator* (`docs/simulatore.html`) |
| Guida rapida e crediti | Spiega come si usa; elenca fonti e licenze | *How to use it*; *Credits and licences* (`docs/crediti.html`) |
| Vai a coordinate | Centra la mappa su un punto | *Go to coordinates* |

Il riquadro *How to use it* riassume l'uso in tre passi: leggi la mappa; tocca uno stretto (rombo magenta) per vedere navi al giorno, cosa passa, chi è esposto e i prezzi collegati; apri il *Terminal* e i *Reports* (`docs/index.html`, righe 296–302).

### I dati: `docs/data/` (66 file JSON)

Ogni file JSON è una «scatola» di dati con la stessa forma (`raccolta/AGENTI.md`):

- `aggiornato`: quando lo script l'ha scritto;
- `fonti`: nome, link, licenza e data del dato di ogni fonte;
- `nota`: che cosa il dato è e che cosa **non** è;
- `elementi`: i dati veri e propri (punti, linee o serie storiche);
- `errori`: cosa non ha funzionato nell'ultima raccolta.

I punti sulla mappa seguono uno schema comune di 25 campi (nome, data dell'evento, latitudine, longitudine, origine delle coordinate, precisione in km, fonte, link, data della fonte, affidabilità, note…). L'elenco dei livelli e delle viste sta in `docs/data/manifest.json`.

*Nota:* il README dice ancora «15 collectors» e «42 data files». Al 10 novembre i file JSON in `docs/data/` sono 66 e gli script Python in `raccolta/` sono 36. Conviene aggiornare il README (lo fa la sessione «Vetrina»).

### Gli script di raccolta: `raccolta/`

Uno **script** è un piccolo programma in Python che va su una fonte pubblica, scarica i dati, li controlla e scrive un file JSON. C'è una cartella per ogni dominio. Quasi tutti usano solo la libreria standard di Python, così girano ovunque senza installare niente (eccezione: lo script delle navi usa `websockets`, `raccolta/navi/requirements.txt`).

Molti domini sono **curati**: le voci si scrivono a mano con fonte e data, e lo script le **valida** (campi obbligatori, date, coordinate, link, voci più vecchie di 90 giorni da rivedere).

**Quotidiani** (workflow `aggiorna-dati.yml`, ogni giorno alle 05:15 UTC, nell'ordine in cui girano):

| Script | Cosa fa | File prodotti |
|---|---|---|
| `flussi/raccogli.py` | Transiti negli stretti e navi nei porti italiani (IMF PortWatch); noli; indice di rischio geopolitico; navi sanzionate (OFAC, Regno Unito, UE) | `portwatch.json`, `noli.json`, `gpr.json`, `sanzioni-navi.json` |
| `scorte/raccogli.py` | Stoccaggi gas UE (GIE AGSI+, con chiave), Eurostat, petrolio USA, grano, oro | `scorte.json` |
| `navi/raccogli.py` | Posizioni AIS di navi da fonti aperte (Digitraffic, aisstream.io, Global Fishing Watch, USNI) | `navi.json` |
| `calendario/raccogli.py` | Agenda: banche centrali, dati macro, OPEC+, elezioni, sanzioni | `calendario.json` |
| `energia/raccogli.py` | Terminali GNL del mondo; ingressi del gas in Italia con flussi giornalieri | `terminali-gnl.json`, `gas-italia.json` |
| `ucraina/raccogli.py` | Missili e droni lanciati e abbattuti; attacchi a lungo raggio | `ucraina-storico.json` |
| `notizie/raccogli.py` | Notizie OSINT degli ultimi 7 giorni (feed, Telegram pubblici) | `notizie.json` |
| `notizie/testate.py` | Testate per argomento, per la pagina *News feed* | `notizie-testate.json` |
| `nord/raccogli.py` | Porti di Mare del Nord e Baltico, eolico offshore, sicurezza baltica, schede di esposizione di 10 Paesi | `porti-nord.json`, `offshore-nord.json`, `baltico-sicurezza.json`, `esposizione-nord.json` |
| `bunker/raccogli.py` | Prezzi del carburante navale, EU ETS marittimo, FuelEU, IMO | `bunker-emissioni.json` |
| `italia/raccogli.py` | Carburanti, accise, PUN, inflazione, scioperi dell'autotrasporto | `italia-impatti.json` |
| `stretti/raccogli.py` | Valida le schede degli stretti e aggiorna le parti automatiche | `stretti-dettaglio.json` |
| `eolico/calendario.py` | Calendario delle tappe dell'eolico offshore (aste, FID, primo kWh…): validazione e voci scadute | `wind-calendar.json` |
| `rotte/tempi.py` | Giorni e costo extra per portare merci in 9 porti europei, oggi contro prima della crisi | `transit-times.json` |
| `rischio/calcola.py` | Cruscotto del rischio di 12 stretti e 6 corridoi (legge gli altri JSON, senza rete) | `rischio.json` |
| `porti/rischio_porti.py` | Port Risk Index di 39 porti (legge gli altri JSON, senza rete) | `port-risk.json` |
| `comune/nascondi_chiavi.py` | Ultimo controllo: toglie eventuali chiavi API dai file pubblici | — |

**Nei giorni feriali** (workflow `aggiorna-mercati.yml`, lun–ven alle 21:30 UTC, dopo la chiusura di Wall Street):

| Script | Cosa fa | File |
|---|---|---|
| `scarica_mercati.py` | Prezzi di chiusura (Tesoro USA per i tassi, Yahoo Finance per il resto) | `prezzi.json` |

**A mano, quando serve** (dati lenti o curati; non sono nei workflow):

| Script | Cosa fa | File |
|---|---|---|
| `ai/raccogli.py` | Data center AI, fabbriche di chip, flussi di investimento | `ai-mondo.json`, `investimenti.json` |
| `assicurazioni/raccogli.py` | Aree a rischio guerra del Joint War Committee (27 aree, circolare JWLA-035 del 16 settembre 2026), premi | `assicurazioni.json` |
| `basi/raccogli.py` | Basi militari nel mondo (curate e validate) | `basi-mondo.json` |
| `cavi/raccogli.py` | Cavi sottomarini (TeleGeography) e incidenti | `cavi.json`, `cavi-incidenti.json` |
| `commercio/raccogli.py` | Commercio per Paese, dipendenze, minerali critici | `commercio.json`, `minerali.json` |
| `cyber/raccogli.py` | Incidenti cyber contro energia ed eolico (taglio difensivo) | `cyber-energia.json` |
| `elettricita/raccogli.py` | Rete ad alta tensione, interconnessioni, centrali nucleari | `rete-elettrica.json`, `interconnessioni.json`, `nucleare.json` |
| `eolico/raccogli.py` | Filiera dell'eolico offshore: porti base, navi, colli di bottiglia, aste | `eolico-filiera.json` |
| `ferrovie/raccogli.py` | Rete ferroviaria, corridoi Europa–Asia, incidenti | `ferrovie.json` |
| `fronte/raccogli.py` | Storico del fronte ucraino (copia privata, vedi licenze) | `fronte-storico.json` |
| `idrogeno/raccogli.py` | Idrogeno e ammoniaca nei porti | `idrogeno.json` |
| `paesi/raccogli.py` | Schede paese (FMI, Banca Mondiale, SIPRI…) | `paesi.json` |
| `supply-chain-ai/raccogli.py` | Catena del valore dell'AI | `supply-chain-ai.json` |
| `ucraina/attacchi_russi.py`, `ucraina/telegram_analisti.py` | Attacchi russi geolocalizzati; attacchi segnalati da Clément Molin e AMK Mapping | `attacchi-russi.json`, `attacchi-analisti.json` |
| `webcam/raccogli.py` | Controlla che i link delle webcam funzionino | `webcam.json` |
| `originali/controlla.py`, `simulatore/controlla.py` | Controlli dei livelli originali e del modello del simulatore | — |

In costruzione al 10 novembre: `raccolta/qualita/controlla_tutto.py`, un controllo generale giornaliero (freschezza dei dati, schema, link rotti, coerenza tra file, chiavi, licenze). **[da controllare: non è ancora nel workflow]**

Ogni script ha un **rapporto** in `report/agenti/<dominio>.md` (33 rapporti al 10 novembre): fonti provate (funziona / non funziona / serve chiave), licenze, cosa c'è nel file, 5–10 fatti attuali con numero, data e fonte, limiti.

### L'aggiornamento automatico: GitHub Actions

**GitHub Actions** è un servizio di GitHub che accende un computer temporaneo a orari fissi, esegue i comandi scritti in un file di istruzioni (un *workflow*) e poi si spegne. Nel tuo progetto ci sono due workflow in `.github/workflows/`.

**`aggiorna-dati.yml` — ogni giorno alle 05:15 UTC** (06:15 in Italia con l'ora solare, 07:15 con l'ora legale). Si può lanciare anche a mano: su GitHub, scheda *Actions* → *Aggiorna dati* → *Run workflow*.

1. Prepara Python 3.12 e installa l'unica dipendenza (per le navi).
2. Esegue i 16 script della tabella sopra, uno dopo l'altro.
3. **Ogni passo è indipendente** (`continue-on-error: true`): se una fonte cade, le altre vanno avanti.
4. Il cruscotto del rischio e il Port Risk Index girano **per ultimi**, perché leggono i file appena scritti dagli altri.
5. Esegue `nascondi_chiavi.py`.
6. Salva i file cambiati con un commit «Dati: aggiornamento automatico del …», poi li pubblica.
7. Ha un tempo massimo di 40 minuti, e due esecuzioni non possono sovrapporsi.

**`aggiorna-mercati.yml` — dal lunedì al venerdì alle 21:30 UTC.** Scarica i prezzi e salva `prezzi.json`.

### Chiavi API e come sono protette

Alcune fonti gratuite chiedono una **chiave API**: una specie di password personale che identifica chi scarica i dati. Il progetto ne usa quattro nel workflow: `AISSTREAM_API_KEY` (navi AIS), `GFW_API_KEY` (Global Fishing Watch), `AGSI_API_KEY` (stoccaggi gas), `BLS_API_KEY` (dati USA, facoltativa). Il README cita anche `EIA_API_KEY`, facoltativa.

Le protezioni sono tre:

1. **Mai chiavi nei file.** Le chiavi stanno nei *Secrets* di GitHub (Settings → Secrets and variables → Actions). GitHub le conserva cifrate e le passa agli script solo durante l'esecuzione, come variabili d'ambiente. GitHub nasconde anche i loro valori nei log.
2. **Se una chiave manca, lo script non si blocca:** salta quella fonte e scrive un avviso (`raccolta/AGENTI.md`).
3. **Il controllo finale `raccolta/comune/nascondi_chiavi.py`.** Prima di ogni salvataggio legge tutti i file `docs/data/*.json` e le pagine HTML in `docs/`. Sostituisce con «[chiave nascosta]» due cose: il valore di ogni variabile d'ambiente che finisce in `_API_KEY`, `_KEY` o `_TOKEN`; e qualunque testo del tipo «api key: <stringa lunga>».

**Perché c'è il controllo.** Il 9 novembre 2026 la chiave AGSI è finita per errore in un file pubblico. Il file è stato ripulito, ma la chiave resta nella cronologia di git: **va rigenerata** sul sito di GIE e reinserita nei Secrets (`STATO.md`). È una buona storia da colloquio: hai trovato un errore, l'hai corretto e hai messo un controllo automatico perché non si ripeta.

### I report: generati da script e rivisti

I report non sono scritti a mano numero per numero. Per i più recenti uno script Python (per esempio `report/build_northern_europe.py`, `report/costruisci_supply_chain.py`) legge i JSON e produce sia il Markdown sia la pagina HTML con i grafici. Così i numeri del testo vengono dagli stessi file della mappa. Poi un revisore indipendente controlla ogni cifra (vedi 1.3). Le correzioni si fanno nello script, non a mano nella pagina, e il report si rigenera.

### Gli agenti AI: che cosa sono, detto onestamente

Il progetto è stato costruito con un assistente AI per la programmazione (Claude, tramite Claude Code). «Agente» qui vuol dire: una sessione dell'assistente con un compito preciso, regole scritte e cartelle sue.

- **Il coordinatore («Regia»).** È l'unica sessione che può modificare la mappa (`docs/index.html`), il `manifest.json`, i workflow e `STATO.md`. Distribuisce i compiti e controlla i risultati.
- **Agenti tematici.** Uno per dominio (flussi, energia, Nord Europa, assicurazioni, eolico…). Ognuno scrive solo il suo script, il suo file JSON e il suo rapporto. Seguono le regole comuni di `raccolta/AGENTI.md`: mai numeri inventati, ogni dato con fonte e data, niente chiavi nel codice, niente commit (li fa il coordinatore).
- **Revisori.** Sessioni separate che controllano un report contro `report/STANDARD.md` e scrivono il resoconto in `report/revisioni/`.
- **Altre sessioni parallele:** «Report», «Raccolta», «Vetrina CV», e dal 10 novembre la traduzione in inglese (`STATO.md`, sezione «Lavori in parallelo»).
- **Il coordinamento** passa da un file di stato condiviso, `STATO.md`, che ogni sessione legge per prima.

**Che cosa NON fanno gli agenti oggi.** L'aggiornamento quotidiano è fatto da **script normali**, non dall'AI: gli script sono deterministici, cioè fanno ogni giorno la stessa cosa. Una «regia automatica» con sessioni AI programmate (coordinatore quotidiano, agenti tematici settimanali) è **solo una proposta**, da attivare dopo il tuo via libera (`STATO.md`, *Da fare*, punto 4).

**Chi ha fatto cosa** (dal `README.md`, sezione *My role*): tu hai definito la domanda e la catena, lo schema dei dati, le regole di affidabilità, le fonti e i compromessi, il flusso di lavoro e i controlli; hai rivisto i risultati e deciso cosa entra e cosa resta fuori. L'assistente ha scritto quasi tutto il codice, ha eseguito gli script, ha esplorato le fonti e ha scritto le bozze. Dillo così ai colloqui: è credibile e mostra che sai governare uno strumento.

---

## 1.3 Il metodo

### Regole di affidabilità

Ogni dato porta uno di tre livelli (`METODO.md`):

| Livello | Quando | Esempio da `eventi.json` |
|---|---|---|
| **Alta** | Fonte ufficiale, o più fonti indipendenti | Petroliera in fiamme vicino a Khasab, 7 nov 2026: avviso UKMTO 199-26 |
| **Media** | Fonte credibile, non ancora confermata | Tre petroliere colpite l'8 nov 2026: rivendicazione dei Pasdaran riportata da Al Jazeera |
| **Bassa** | Non verificato, o rivendicazione di una parte in conflitto senza conferme | Drone MQM-170 abbattuto su Qeshm, 6 nov 2026: segnalazione iniziale di un account su X |

**La regola delle due fonti.** «Alta» richiede una fonte ufficiale oppure **almeno due fonti indipendenti**. Una sola fonte credibile, anche se di un grande giornale, vale «media». Una rivendicazione di una parte in guerra non diventa mai un fatto: si scrive «i Pasdaran rivendicano» (`report/STANDARD.md`, punto 2).

### Fatti e valutazioni

- **Fatto:** qualcosa che una fonte riporta, con fonte e data.
- **Valutazione:** un ragionamento dell'osservatorio sui fatti (cause, scenari, «è un rischio»). Nei report è marcata *Valutazione:*; nei file JSON con un campo apposito (per esempio `"valutazione": true` in `italia-impatti.json`).
- Una frase «X perché Y» senza una fonte che la sostenga è una valutazione.

Esempio pratico: nel file delle sanzioni, 2.022 navi sono sanzionate da USA, Regno Unito o UE (**fatto**, dalle liste ufficiali). Di queste, 1.163 sono marcate `flotta_ombra_probabile` (**valutazione** della mappa: petroliere sanzionate per Russia o Iran) (`sanzioni-navi.json`, 9 novembre 2026).

### Coordinate: origine e precisione

Ogni punto dice da dove vengono le sue coordinate e quanto sono precise:

- `origine_coord`: **fonte** (la fonte dà le coordinate) oppure **stimata** (le abbiamo ricavate noi da una descrizione, per esempio «8 miglia a nord-ovest di Khasab»);
- `precisione_km`: il raggio di incertezza.

Esempi da `eventi.json`: la petroliera dell'avviso UKMTO 199 ha precisione 3 km; la Velos Sapphire, descritta solo come «a nord del Qatar», ha precisione 100 km. Un evento riportato solo «vicino a Hormuz» non viene disegnato come un punto esatto (`README.md`).

**Il tempo conta.** Gli eventi cambiano colore con l'età. I prezzi presi durante la seduta sono marcati come provvisori. Le zone senza dati AIS lo dicono: «nessuna fonte per quest'area» non vuol dire «zero navi». Esempio: il 9 novembre `navi.json` scrive per Hormuz «nessuna fonte gratuita attiva per quest'area in questa esecuzione».

### Lo standard editoriale dei report

`report/STANDARD.md` ha dieci regole. Le più importanti:

1. **Numeri:** sempre fonte, data e unità; ogni variazione con il termine di confronto («−95% sulla stessa settimana del 2025», non «−95%»).
2. **Fatti e valutazioni** separati.
3. **Incertezza dichiarata:** se due fonti divergono si mostrano entrambe; ciò che manca si scrive.
4. **Tono:** niente allarmismi («scende del 22%», non «crolla»); nessun consiglio di investimento.
5. **«In breve»:** al massimo 5 punti, leggibili in 60 secondi da chi lavora in un porto o in una società energetica.
6. **Limiti espliciti** in fondo a ogni report.
7. **Grafici** generati da script, con titolo, unità, periodo e fonte.
8. **Italiano chiaro:** frasi brevi, sigle spiegate.
9. **Trasparenza sull'AI:** cosa è stato fatto con l'assistente.
10. **Revisione indipendente** di ogni numero, con tabella e riquadro «Revisione» finale.

### La revisione indipendente: i numeri

| Report | Affermazioni controllate | Esito | File |
|---|---|---|---|
| Hormuz e Mar Rosso (9 nov 2026) | 183 | 135 confermate, 38 corrette, 10 non verificabili | `report/revisioni/hormuz-mar-rosso-2026-11.md` |
| Supply chain e logistica (9 nov 2026) | 59 | 9 errori o imprecisioni corretti; 43 controlli sui JSON e 16 anche sulla fonte esterna (10 confermati, 6 non verificabili) | `report/revisioni/supply-chain-2026-11.md` |
| La catena dell'AI (9–10 nov 2026) | 110 | 62 confermate, 32 corrette, 16 non verificabili | `report/revisioni/supply-chain-ai-2026-11.md` |
| Northern Europe: Ports and Energy (10 nov 2026) | 64 | 12 errori o debolezze corretti; 4 incoerenze tra file dichiarate nel report | `report/revisioni/northern-europe-2026-11.md` |
| **Totale** | **416** | | |

**La scoperta più utile.** Rivedendo il report Hormuz, il revisore ha trovato un errore nei **dati**, non nel testo: lo script dei prezzi convertiva l'ora di Yahoo Finance con il fuso di New York dell'ora solare anche nei mesi di ora legale. Risultato: tra l'8 marzo e il 1° novembre 2026 ogni seduta risultava un giorno prima. Ora lo script usa il fuso corretto per ogni data (`raccolta/scarica_mercati.py`, righe 97–100). È un ottimo esempio da raccontare: la revisione serve davvero.

### Il metodo del rischio: probabilità × impatto

Lo spiega `report/metodo-rischio.md`. È la classica matrice dei registri dei rischi aziendali (norma ISO 31000).

**Rischio = probabilità di disruption (1–5) × impatto (1–5)**, quindi un punteggio da 1 a 25. Si valutano 18 unità: 12 passaggi strategici e 6 corridoi o infrastrutture (TransMed, Baltico, Mar Rosso, GNL del Qatar, rete elettrica ucraina, chip di Taiwan). Il punto di vista è **europeo e italiano**.

**Probabilità** — quattro domande (che lo stretto sia o resti disturbato nei prossimi 3 mesi):

| Domanda | Peso | Rosso se… |
|---|---|---|
| I flussi calano? | 35% | transiti sotto −30% rispetto al riferimento |
| Ci sono attacchi o incidenti vicino? | 30% | 3 o più eventi in 30 giorni entro 150 km |
| Il clima geopolitico peggiora? | 15% | indice GPR almeno 1,5 volte la sua media di 5 anni |
| Il mercato lo prezza? | 20% | prezzo collegato oltre +15% sulla media di 90 giorni |

**Impatto** — quattro domande (quanto fa male se succede):

| Domanda | Peso | Rosso se… |
|---|---|---|
| Quanto pesa ciò che passa? | 35% | quota oltre il 25% o giudizio 4–5 |
| Ci sono alternative? | 20% | giudizio 4–5 (poche alternative) |
| Quanto cuscinetto c'è? | 25% | scorte sotto −15% rispetto alla media di 5 anni |
| Quanto costa già? | 20% | prezzo oltre +40% su un anno |

**Come si calcola.** Ogni indicatore vale 1 (verde), 3 (giallo) o 5 (rosso). Si fa la media dentro ogni domanda e la media pesata tra le domande. Se un dato manca, la domanda esce e i pesi si ridistribuiscono; il campo `copertura` dice quanto è solido il punteggio. **Regola della disruption in corso:** se i transiti sono a −50% o peggio, la probabilità è 5 (non si stima la probabilità di un fatto già avvenuto). Livelli: basso sotto 6, medio 6–11,9, alto 12–19,9, critico da 20 in su.

**Perché −30%.** Sulla serie PortWatch dal gennaio 2024 al febbraio 2026, nei passaggi «normali» un calo oltre −30% non capita **mai**. È successo solo dove c'era una crisi vera: Panama con la siccità e Suez con gli Houthi (`report/metodo-rischio.md`, sezione 3).

**Cosa il punteggio NON dice.** Non è una probabilità statistica: «5» vuol dire «disruption in corso», non «100%». Non vede le navi con l'AIS spento. Le unità non sono indipendenti (Hormuz e GNL del Qatar condividono gli stessi transiti), quindi i punteggi non si sommano.

**Port Risk Index (39 porti).** Stessa logica, applicata ai porti: 30 del Mare del Nord e del Baltico e 9 italiani (`report/port-risk-method.md`). Probabilità: traffico (30%), sicurezza nelle vicinanze, incluso il disturbo GNSS (30%), dipendenza da stretti a rischio (25%), aree elencate dagli assicuratori (15%). Impatto: ruolo strategico (45%: terminale GNL, hub petrolifero, porta container, porto base per l'eolico…), merce movimentata (30%), costo dell'energia (25%). Esempi del 10 novembre (`port-risk.json`): Rotterdam 7,5 *medium*; Gdańsk 7,0 *medium*; Esbjerg 3,2 *low*; Aarhus 2,0 *low*.

---

## 1.4 Il flusso dei dati in un disegno

### Versione in testo

```
 FONTI PUBBLICHE                      SCRIPT (raccolta/)                 DATI (docs/data/)         COSA VEDI
 ─────────────────                    ───────────────────                ─────────────────         ─────────
 IMF PortWatch ─────────┐
 GIE AGSI+, Eurostat ───┤
 ENTSOG, Snam ──────────┤   GitHub Actions 05:15 UTC ogni giorno
 AIS (Digitraffic,      │   ┌───────────────────────────────┐
  aisstream, GFW) ──────┼──▶│ 14 script di raccolta         │──▶ portwatch.json, scorte.json,  ─┐
 OFAC, UK, UE ──────────┤   │ (flussi, scorte, navi, ...)   │    navi.json, gas-italia.json…    │
 Ship & Bunker, Drewry ─┤   └───────────────┬───────────────┘                                   │
 UKMTO, stampa, OSINT ──┤                   ▼                                                    ├─▶ MAPPA (docs/index.html)
 Joint War Committee ───┤   ┌───────────────────────────────┐                                   │    livelli, schede stretti
 (voci curate a mano) ──┘   │ rischio/calcola.py            │──▶ rischio.json, port-risk.json ──┤
                            │ porti/rischio_porti.py        │    (leggono i JSON, senza rete)   ├─▶ TERMINAL
                            └───────────────┬───────────────┘                                   │    Risk, Prices and rates…
 Tesoro USA, Yahoo ──▶ scarica_mercati.py (lun–ven 21:30 UTC) ──▶ prezzi.json ──────────────────┤
                                            ▼                                                    ├─▶ REPORTS
                            nascondi_chiavi.py ──▶ commit su main ──▶ GitHub Pages ripubblica    │    script → Markdown + HTML
                                                                                                 │    → revisione indipendente
                                                                                                 └─▶ SIMULATORE, NEWS FEED
```

### Descrizione per un'immagine SVG (da far disegnare al revisore)

Formato orizzontale, cinque colonne da sinistra a destra, frecce piene tra le colonne.

1. **Colonna «Fonti»** (rettangoli grigi impilati): IMF PortWatch; GIE AGSI+ / Eurostat; ENTSOG; AIS (Digitraffic, aisstream.io, Global Fishing Watch); liste sanzioni (OFAC, UK, UE); Ship & Bunker / Drewry / Freightos; Tesoro USA / Yahoo Finance; UKMTO, stampa, analisti OSINT; voci curate a mano (Joint War Committee, eolico, basi).
2. **Colonna «Script»** (rettangoli blu): un riquadro grande «14 script di raccolta» con dentro l'etichetta «GitHub Actions, ogni giorno 05:15 UTC»; sotto, un riquadro più piccolo «scarica_mercati.py, lun–ven 21:30 UTC». Sotto ancora, un riquadro arancione «calcola rischio e Port Risk Index (leggono i JSON)», collegato con una freccia che torna dalla colonna 3 alla colonna 2, per mostrare che leggono i file appena scritti.
3. **Colonna «Dati»** (cilindro verde): «docs/data/ — 66 file JSON, formato comune: aggiornato, fonti, nota, elementi, errori».
4. **Barriera** (sottile barra rossa tra colonna 3 e 4): «nascondi_chiavi.py → commit su main → GitHub Pages».
5. **Colonna «Uscite»** (quattro rettangoli viola): Mappa; Terminal; Reports (con una piccola freccia a un riquadro «Revisione: 416 affermazioni controllate»); Simulatore e News feed.

Legenda in basso: «Ogni passo è indipendente: se una fonte cade, le altre continuano». Colori distinguibili anche per chi è daltonico (blu, arancione, viola, grigio; il rosso solo per la barriera delle chiavi).

---

## 1.5 Glossario per i colloqui

Le definizioni sono brevi, così le puoi ripetere a voce. Tra parentesi, dove trovi il termine nel sito.

| Termine | Che cos'è, in parole semplici |
|---|---|
| **Chokepoint** (passaggio strategico) | Uno stretto o un canale dove passa molto traffico e non ci sono vie alternative comode: Hormuz, Bab el-Mandeb, Suez, Stretti danesi, Bosforo. Se si chiude, le navi devono fare giri lunghi o fermarsi. (*Chokepoints*) |
| **AIS** (Automatic Identification System) | Il transponder di bordo che trasmette posizione, rotta e identità della nave. Se viene spento, la nave sparisce dai sistemi pubblici. (`navi.json`) |
| **Navi «dark»** | Navi che viaggiano con l'AIS spento. Per questo PortWatch conta meno transiti di Lloyd's List Intelligence a Hormuz. |
| **IMF PortWatch** | Piattaforma del Fondo Monetario Internazionale e dell'Università di Oxford che stima, dai segnali AIS, le navi al giorno negli stretti e nei porti. Dati con circa una settimana di ritardo. (`portwatch.json`) |
| **Lloyd's List Intelligence (LLI)** | Società di dati marittimi a pagamento; ricostruisce anche i transiti delle navi «dark». Il sito ne cita i bollettini pubblici. |
| **Brent** | Il prezzo di riferimento del greggio nel mondo, in dollari al barile. (*Prices and rates*) |
| **WTI** | Il prezzo di riferimento del greggio americano. |
| **TTF** (Title Transfer Facility) | Il mercato del gas all'ingrosso nei Paesi Bassi; il suo prezzo, in euro per MWh, è il riferimento per tutta l'Europa. |
| **Henry Hub** | Il prezzo di riferimento del gas negli Stati Uniti, in dollari per milione di BTU. |
| **GNL** (gas naturale liquefatto, in inglese LNG) | Gas raffreddato a −162 °C e trasportato con navi metaniere. Arriva a un terminale di rigassificazione (anche galleggiante: FSRU). |
| **mb/g** | Milioni di barili al giorno: l'unità dei flussi di petrolio. |
| **Forza maggiore** | Clausola che sospende un contratto di fornitura per cause esterne (guerra, disastro). Il Qatar la usa per il GNL dal 4 marzo 2026. |
| **Nolo** (*freight rate*) | Il prezzo del trasporto via mare. Per i container si misura in dollari per FEU. |
| **FEU / TEU** | Container da 40 piedi / da 20 piedi. Un FEU vale due TEU. |
| **WCI, FBX, SCFI** | Indici dei noli container: Drewry World Container Index, Freightos Baltic Index, Shanghai Containerized Freight Index. |
| **Baltic Dry** | Indice dei noli delle navi per rinfuse secche (carbone, grano, minerali). Nel sito non è più raccolto in automatico per i termini d'uso della fonte. |
| **Bunker, VLSFO, MGO** | *Bunker* è il carburante delle navi. VLSFO: olio combustibile a bassissimo zolfo, il più usato. MGO: gasolio marino. (`bunker-emissioni.json`) |
| **War risk** (assicurazione di guerra) | Copertura separata per guerra, mine, sequestro. Si paga per viaggio, in percentuale del valore della nave. A Hormuz 6–10% a ottobre 2026. |
| **JWC Listed Areas** | Elenco delle zone a rischio guerra del Joint War Committee (assicuratori del mercato di Londra). Se una nave entra in una zona elencata, l'assicuratore può chiedere un premio aggiuntivo. 27 aree nella circolare JWLA-035 del 16 settembre 2026. (`assicurazioni.json`) |
| **EU ETS marittimo** | Il sistema europeo di scambio delle quote di CO₂, esteso alle navi. Gli armatori devono comprare quote per le emissioni dei viaggi verso, da e dentro l'UE. |
| **EUA** (EU Allowance) | Una quota di emissione: dà diritto a emettere 1 tonnellata di CO₂ equivalente. 87,71 € il 6 novembre 2026 (`bunker-emissioni.json`, Ship & Bunker). |
| **FuelEU Maritime** | Regolamento UE (2023/1805) che obbliga le navi a ridurre, anno dopo anno, l'intensità di gas serra dell'energia usata a bordo. Chi non rispetta i limiti paga una penale. |
| **IMO** | Organizzazione marittima internazionale (ONU): fa le regole globali delle navi. |
| **Flotta ombra** (*shadow fleet*) | Petroliere vecchie, spesso con bandiere di comodo e assicurazioni poco trasparenti, usate per trasportare petrolio russo o iraniano aggirando le sanzioni. Nel sito «flotta ombra probabile» è una **valutazione**, non un'etichetta ufficiale. |
| **GNSS jamming / spoofing** | Disturbo dei segnali satellitari di posizione (GPS, Galileo). *Jamming*: il segnale viene coperto. *Spoofing*: viene falsificato. Nel Baltico colpisce aerei e navi. Il sito usa le mappe di GPSJam (`baltico-sicurezza.json`). |
| **HVDC** (High Voltage Direct Current) | Cavi elettrici ad alta tensione in corrente continua: servono per le lunghe distanze e sotto il mare (interconnessioni tra Paesi, collegamento dei parchi eolici offshore). (`interconnessioni.json`) |
| **CfD** (Contract for Difference) | Contratto con lo Stato che garantisce a un parco eolico un prezzo fisso: se il mercato paga meno, lo Stato integra; se paga di più, il produttore restituisce la differenza. È lo strumento delle aste eoliche in Regno Unito, Danimarca, Polonia. |
| **FID** (Final Investment Decision) | La decisione finale di investimento: il momento in cui un progetto (per esempio un parco eolico) passa dalla carta ai contratti veri. Il calendario eolico ne conta 4 tra le sue 114 tappe (`wind-calendar.json`). |
| **Porto base** (*base port*) | Il porto da cui partono le navi con le pale, le torri e le fondazioni per costruire un parco eolico offshore (es. Esbjerg, Eemshaven). (`eolico-filiera.json`) |
| **OSINT** (Open Source Intelligence) | Analisi fatta solo con fonti aperte: stampa, dati pubblici, immagini satellitari gratuite, social, AIS. È il metodo di tutto il progetto. |
| **GPR** (Geopolitical Risk Index) | Indice di Caldara e Iacoviello che conta gli articoli di 10 giornali su guerre e tensioni. Media 1985–2019 = 100. Misura l'attenzione dei media, non il danno. (`gpr.json`) |
| **UKMTO** | United Kingdom Maritime Trade Operations: centro della Marina britannica che pubblica gli avvisi di sicurezza per le navi (Golfo, Mar Rosso). |
| **Disruption** | Interruzione o forte riduzione di un flusso (navi, gas, petrolio). |
| **Probabilità × impatto** | Il modo standard di dare un punteggio a un rischio: quanto è probabile che succeda, moltiplicato per quanto fa male. (*Risk*) |
| **Early warning** (indicatori anticipatori) | Segnali che si muovono prima del danno: flussi in calo, incidenti, prezzi, attenzione dei media. |
| **Sito statico / GitHub Pages** | Sito fatto di file già pronti, pubblicato gratis da GitHub. |
| **GitHub Actions / workflow** | Il servizio che esegue gli script a orari fissi; il *workflow* è il file con le istruzioni. |
| **JSON** | Formato di testo per i dati, leggibile sia dalle persone sia dai programmi. |
| **Chiave API / Secrets** | Password personale per scaricare dati da un servizio; su GitHub si conserva cifrata nei *Secrets*. |

---

### In sintesi (da rileggere prima di un colloquio)

1. **Che cos'è:** una mappa OSINT che segue la catena evento → stretto → flussi → noli → prezzi → esposizione, con fonte, data e affidabilità su ogni numero.
2. **Come funziona:** sito statico su GitHub Pages; 66 file JSON in `docs/data/`; 36 script Python in `raccolta/`; aggiornamento automatico ogni mattina alle 05:15 UTC e ogni sera feriale alle 21:30 UTC con GitHub Actions; chiavi nei Secrets e controllo finale che le nasconde.
3. **Perché fidarsi:** tre livelli di affidabilità, regola delle due fonti, fatti separati dalle valutazioni, coordinate con precisione dichiarata, 416 affermazioni dei report controllate una per una.
4. **Il valore per un porto o un'azienda energetica del Nord:** un punteggio di rischio trasparente per 18 stretti e corridoi e per 39 porti, che chiunque può rifare a mano.
5. **Il ruolo dell'AI:** l'assistente ha scritto il codice; tu hai deciso domanda, metodo, fonti e controlli. L'aggiornamento quotidiano lo fanno script normali, non l'AI.
