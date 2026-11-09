# Agente CRUSCOTTO DEL RISCHIO: rapporto

Data: 2026-11-09. Script: `raccolta/rischio/calcola.py` (solo libreria standard, nessuna rete: legge i JSON di `docs/data/`). Eseguito davvero il 9 novembre 2026, circa 0,3 secondi, nessun errore. Metodo: [`report/metodo-rischio.md`](../metodo-rischio.md).

## File prodotti

| File | Contenuto |
|---|---|
| `docs/data/rischio.json` (≈185 kB) | 18 unità con `probabilita`, `impatto`, `punteggio`, `livello`, `tendenza`, `copertura`, `regola_disruption`, `indicatori[]` (valore, testo, soglie, stato, punti, peso, fonte, link, file, data, nota), `perche`, `cosa_osservare[]`, `esposti[]`, `collegamenti{stretto, prezzi, livelli}`; in testa `regole` (pesi e soglie), `fonti` (file letti con la loro data), `scenari` (lettura dei segnali), `errori` |
| `raccolta/rischio/storico.json` | punteggi giornalieri per la tendenza a 7 giorni; il 2 novembre è **ricostruito** (`ricostruito: true`) |
| `raccolta/rischio/scenari.json` | 4 unità × 3 scenari (base, peggiorativo, migliorativo): innesco, effetti sulla catena, segnali misurabili, fonti dei numeri. Marcati come **valutazioni** |
| `report/metodo-rischio.md` | il metodo, una pagina e mezza |

Workflow: aggiunto un passo in `.github/workflows/aggiorna-dati.yml` dopo "Stretti" (`continue-on-error`) e `raccolta/rischio/storico.json` nel `git add`, altrimenti lo storico non si conserverebbe tra le esecuzioni. **Da approvare dal coordinatore**: è l'unico file fuori dal mio dominio che ho toccato.

## Risultati di oggi (9 novembre 2026)

| # | Unità | P | I | P×I | Livello | Tendenza (7 gg fa) | Che cosa spinge |
|---|---|---|---|---|---|---|---|
| 1 | GNL del Qatar (Ras Laffan → Hormuz) | 5,0 | 4,8 | **24,0** | critico | stabile (23,5) | petroliere e metaniere a Hormuz 1,4/g contro 48,2 nel 2025 (−97%); 25 eventi in 30 gg; nessuna alternativa |
| 2 | Stretto di Hormuz | 5,0 | 4,5 | **22,5** | critico | stabile (22,5) | 4,4 navi/g contro 85,5 nel 2025 (−95%); 23 eventi in 30 gg; GPR Arabia Saudita ×2,3 |
| 3 | Bab el-Mandeb | 5,0 | 3,8 | 19,0 | alto | stabile | 27,3 navi/g contro 74,6 nel 2023 (−63%); premio Genova/Rotterdam +15% |
| 4 | Mar Rosso: container Asia–Europa | 5,0 | 3,6 | 18,0 | alto | stabile | portacontainer −75% a Bab el-Mandeb e −41% a Suez sul 2023; CCFI Mediterraneo +6,8% in una settimana |
| 5 | Rete elettrica ucraina | 5,0 | 3,4 | 17,0 | alto | stabile | blackout a Kyiv negli ultimi 7 gg; lanci russi ×1,7 sulla media annua; 2 ondate contro la rete (copertura 0,5) |
| 6 | Stretti turchi | 5,0 | 3,3 | 16,5 | alto | **in aumento** (11,9) | Bosforo −55% su un anno; 10 eventi (Odesa, Mar Nero, Novorossiysk) |
| 7 | Canale di Suez | 2,6 | 3,8 | 9,9 | medio | stabile | −42% sul 2023 ma in ripresa (+10% su un anno); nessun evento |
| 8 | Stretto di Kerch | 5,0 | 1,9 | 9,5 | medio | stabile | 0 transiti AIS (forse effetto AIS spento); impatto basso |
| 9 | Baltico: cavi, condotte, elettrodotti | 2,3 | 3,9 | 9,0 | medio | stabile (9,4) | Stretti danesi −20,5%; 45 petroliere ombra/sanzionate in AIS; 1 incidente ai cavi in 12 mesi; stoccaggi DE −33,5% e NL −22,9% sulla media 5 anni |
| 10 | Stretti danesi | 2,3 | 3,6 | 8,3 | medio | **in aumento** (5,8) | transiti da −2% a −20,5% su un anno in una settimana |
| 11 | Stretto di Malacca | 2,0 | 3,5 | 7,0 | medio | **in aumento** (4,5) | transiti da −4% a −15% su un anno |
| 12 | Catena dei chip di Taiwan | 1,3 | 5,0 | 6,5 | medio | stabile | tutto verde tranne un cavo a Matsu (causa naturale); impatto massimo |
| 13 | TransMed Algeria–Italia | 1,3 | 4,3 | 5,6 | basso | **in calo** (8,0) | flusso +3% sulla media annua; il TTF è sceso sotto la soglia della media 90 gg; 34% del gas italiano |
| 14 | Stretto di Gibilterra | 1,3 | 4,2 | 5,5 | basso | stabile | nessun segnale; nessuna alternativa |
| 15 | Canale di Sicilia | 1,3 | 4,0 | 5,2 | basso | in calo (7,4) | come TransMed |
| 16 | Stretto di Taiwan | 1,3 | 3,9 | 5,1 | basso | stabile | transiti +7% |
| 17 | Capo di Buona Speranza | 1,3 | 3,2 | 4,2 | basso | stabile | traffico +5% (rotta alternativa) |
| 18 | Canale di Panama | 2,2 | 1,6 | 3,5 | basso | stabile | transiti −11,6%; Henry Hub +9% sulla media 90 gg |

P = probabilità 1–5, I = impatto 1–5. Fonti dei valori nei singoli indicatori di `rischio.json`.

**Scenari (lettura automatica dei segnali, non probabilità):** Hormuz → *Stallo armato* (4 segnali su 4 veri; peggiorativo 1 su 6, migliorativo 0 su 4). Mar Rosso → *Ritorno graduale sotto minaccia* (4/4). Baltico → *Pressione ibrida senza danni gravi* (3/3; 1 segnale peggiorativo: 3 eventi ibridi in 30 gg). TransMed → *Flussi regolari, inverno caro* (3/3).

## Controlli di senso

- **Hormuz critico con i transiti a −95%:** sì (22,5); scatta la regola della disruption in corso.
- **Il Brent è verde sulla media 90 gg** (−8,8%, il mercato si è sgonfiato con il piano del Qatar), ma è **rosso sul costo** (+45,6% su un anno): il metodo separa il segnale anticipatore dal costo già pagato.
- **Le tendenze** vengono da dati veri: Stretti turchi in aumento perché il Bosforo è sceso sotto −50%; TransMed e Sicilia in calo perché il TTF è passato da 94,9 a 82,3 €/MWh (+24% → +5% sulla media 90 gg).
- **Soglie dei flussi verificate** sulla serie PortWatch 2024–febbraio 2026: oltre −30% su un anno non succede mai nei passaggi normali; solo a Panama (siccità) e Suez (Houthi).
- **Robustezza:** provato con cartella vuota, file mancanti e un `prezzi.json` corrotto (variabili `RISCHIO_DATI` e `RISCHIO_STORICO`): lo script esce sempre con codice 0, gli indicatori diventano n.d., la probabilità non viene calcolata se mancano sia flussi sia minacce, e `copertura` scende.
- Durante il lavoro `prezzi.json` è stato ridotto a circa 3 mesi di serie da un altro agente: il confronto a un anno usa il campo `var.1a` pubblicato, quello a 90 giorni la serie.

## Come presentarlo in 2 minuti a un colloquio

1. **Il problema (15 s).** "Una mappa mostra dove sono i problemi, non quanto pesano. Volevo un numero che si spiega da solo e che chiunque può ricontrollare."
2. **Il metodo (40 s).** "Uso la matrice probabilità × impatto, come nei registri dei rischi aziendali (ISO 31000), con indicatori anticipatori. Per la probabilità faccio quattro domande: i flussi calano? (PortWatch), ci sono attacchi vicino? (eventi entro 150 km), il clima peggiora? (indice GPR), il mercato lo prezza? (prezzi e noli). Per l'impatto altre quattro: quanto pesa ciò che passa, se ci sono alternative, quanto cuscinetto di scorte c'è, quanto costa già. Ogni indicatore è verde, giallo o rosso con soglie scritte; pesi espliciti; se i transiti sono sotto −50% la disruption è un fatto e la probabilità è 5."
3. **Il risultato (35 s).** "Oggi Hormuz e il GNL del Qatar sono critici: 4 navi al giorno contro 85. Ma il dato più interessante per l'Italia è in basso a destra della matrice: il TransMed ha probabilità bassa e impatto 4,3, perché un solo tubo porta il 34% del nostro gas. È il rischio da sorvegliare, non quello da titolo di giornale. Nel Baltico il punteggio è medio ma con due segnali che salgono: Stretti danesi −20% e 45 petroliere della flotta ombra visibili; e Germania e Paesi Bassi hanno stoccaggi a −34% e −23% sulla media."
4. **I limiti (20 s).** "Non è una probabilità statistica: le soglie sono scelte e le ho verificate sulla serie storica. PortWatch non vede le navi con l'AIS spento. E il punteggio non dice quando: per questo ho tre scenari a tre mesi con segnali misurabili, che lo script controlla ogni giorno."
5. **Chiusura (10 s).** "Tutto gira da solo ogni mattina su GitHub Actions, solo librerie standard, e ogni numero ha fonte e data."

Domande probabili: *perché questi pesi?* (i flussi sono la misura più diretta della disruption; le scorte decidono se un blocco diventa un razionamento) · *perché moltiplicare?* (un rischio con probabilità bassa e impatto massimo resta sotto osservazione, ma non va confuso con una crisi in corso) · *come lo validi?* (soglie sui dati 2024–26; nel tempo con lo storico: quante volte un "alto" è diventato una disruption).

## Collegamenti con gli altri livelli

- Ogni unità ha `collegamenti.stretto` (id di `stretti-dettaglio.json`), `collegamenti.prezzi` (id di `prezzi.json`) e `collegamenti.livelli` (file da accendere sulla mappa).
- Proposta per la mappa (non ho toccato `docs/index.html`): cerchio sull'unità colorato per `livello` (verde basso, giallo medio, arancio alto, rosso critico), freccia per `tendenza`; al clic la scheda con `perche`, la tabella degli indicatori raggruppati per `domanda`, `cosa_osservare` e lo scenario prevalente. Una vista "matrice" 5×5 con le 18 unità renderebbe subito leggibili i quadranti.

## Limiti

- I giudizi strutturali (peso, alternative) sono valutazioni con fonte e pesano il 55% dell'impatto.
- `eventi.json` e `ibrido.json` coprono solo finestre recenti: nello storico ricostruito gli indicatori sugli eventi restano uguali a oggi.
- La flotta ombra è una fotografia AIS, non una media; le soglie dei noli e della flotta ombra vanno ricalibrate con lo storico.
- Mancano: noli delle petroliere (TD3C), premi war risk aggiornati, prezzo del grano e dei fertilizzanti, scorte di chip, flussi elettrici ucraini (la rete ucraina ha copertura 0,5).
- Hormuz e GNL del Qatar condividono i transiti; Brent e TTF compaiono in molte unità: non sommare i punteggi.
