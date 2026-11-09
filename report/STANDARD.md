# Standard editoriale dei report

Regole che ogni report del Monitor geoeconomico deve rispettare prima di essere pubblicato. Valgono per il testo in Markdown (`report/*.md`) e per la pagina impaginata (`docs/report/*.html`), che devono dire le stesse cose. Completano i principi di [`METODO.md`](../METODO.md).

Ogni report passa una revisione indipendente contro questo standard; il resoconto va in [`report/revisioni/`](revisioni/) e un riquadro «Revisione» chiude il report.

## 1. Numeri: fonte, data, unità

- **Ogni numero ha una fonte e una data.** La fonte è un link alla fonte primaria o al file di dati dell'osservatorio (`docs/data/*.json`) che la riporta; la data è quella del dato, non della lettura.
- **Unità sempre esplicite** alla prima occorrenza in ogni sezione: mb/g (milioni di barili al giorno), $/barile, €/MWh, $/FEU (container da 40 piedi), navi al giorno, punti indice.
- **Variazioni con il termine di confronto**: «−95% sulla stessa settimana del 2025», non «−95%». Se il confronto è con una media, dire quale (mese, anno, cinque anni).
- **Arrotondamenti coerenti** con il file di dati: si arrotonda il valore del file, non si ricalcola a mano.
- **Stesso periodo, stessa fonte** quando si confrontano due cifre. Se i periodi o i perimetri sono diversi, va scritto.
- **Valori provvisori** (prezzi in seduta, stime flash, dati preliminari) sono marcati come tali, con l'ora di lettura se cambiano in giornata.
- **Date di mercato**: la data è quella della seduta. Se il file di dati ha una convenzione diversa (fusi orari, ora legale), si corregge nel testo e lo si dichiara.

## 2. Fatti e valutazioni

- **Fatto**: qualcosa che una fonte riporta, con fonte e data.
- **Valutazione**: un ragionamento dell'osservatorio sui fatti (cause, conseguenze, scenari, giudizi «è un rischio», «conviene guardare»). Va marcata con *Valutazione:* (nel Markdown in corsivo, nella pagina con il riquadro colorato).
- **Rivendicazioni** di una parte in conflitto si scrivono come tali («i Pasdaran rivendicano»), mai come fatti.
- Una frase causale («X perché Y») senza fonte che la sostenga è una valutazione.

## 3. Incertezza dichiarata

- Dire **quanto è affidabile** una fonte quando non è primaria o ufficiale (alta, media, bassa: scala di `METODO.md`).
- Quando due fonti divergono, **mostrare entrambe** e spiegare perché (metodo, perimetro, ritardo) invece di sceglierne una in silenzio.
- Gli scenari non hanno probabilità numeriche se non sono calcolate: si danno soglie osservabili per riconoscerli.
- Ciò che manca si scrive: «**Manca** il dato X».

## 4. Tono

- **Niente toni allarmistici**: niente superlativi non sostenuti dai dati («catastrofe», «collasso», «senza precedenti» solo se un dato lo dice, con la serie storica).
- Verbi neutri e precisi: «scende del 22%», non «crolla».
- Nessun consiglio di investimento.

## 5. Titoli e «In breve»

- Ogni punto dell'«In breve» **regge da solo**: un lettore che legge solo quello capisce che cosa è successo, quanto e da quando, con una cifra e la sua fonte.
- Il titolo di ogni punto è una frase con un verbo che dice il risultato, non un'etichetta.
- L'«In breve» si legge **in 60 secondi** (massimo 5 punti, ognuno sotto le 60 parole circa) da un lettore non specialista, per esempio chi lavora in un porto o in una società energetica del Nord Europa.
- Nessun numero nell'«In breve» che non sia anche nel corpo del report.

## 6. Limiti espliciti

- Una sezione «Metodo, fonti e limiti» chiude ogni report: fonti principali con data del dato, limiti dei dati (copertura, ritardo, perimetro), dati che mancano, fonti in conflitto.
- I limiti noti di uno script (per esempio un errore di date) si dichiarano finché non sono corretti.

## 7. Grafici

- Ogni grafico ha **titolo, unità, periodo, fonte con file e data del dato** nella didascalia.
- I grafici sono generati da script a partire dai file JSON (nessun numero scritto a mano), e il testo non contraddice il grafico.
- Eventi segnati sul grafico con numero e legenda nella didascalia.
- Leggibili a 390 px di larghezza (telefono) e in tema chiaro e scuro; colori distinguibili anche con daltonismo.
- Se un grafico non si può rigenerare con i dati attuali, va scritto con quale versione dei dati è stato prodotto.

## 8. Italiano chiaro

- Frasi brevi: di norma sotto le 30 parole; una frase, un'idea.
- **Termini tecnici spiegati** alla prima occorrenza o in un breve glossario (AIS, GNL, TTF, war risk, forza maggiore, mb/g…). Sigle sciolte la prima volta.
- Niente gergo inglese quando esiste una parola italiana comune; i nomi propri di indici e fonti restano in originale.
- Numeri all'italiana: virgola decimale, punto per le migliaia (4.389; 92,62).

## 9. Trasparenza sull'AI

- Ogni report dice **che cosa è stato fatto con un assistente AI** (raccolta dati, script, stesura, revisione) e che cosa resta responsabilità dell'autore.
- Le cifre prodotte o riassunte con l'AI si verificano contro i file di dati o le fonti prima della pubblicazione; la revisione ne tiene il conto.

## 10. Revisione

- Prima della pubblicazione: verifica di **ogni** numero contro i dati del repository o la fonte citata (tabella in `report/revisioni/<report>.md`: affermazione, valore nel report, valore verificato, fonte, esito: ok / corretto / non verificabile).
- Controllo di coerenza: tra sezioni, tra testo e grafici, con gli altri report e con `docs/data/rischio.json`.
- Riquadro «Revisione» in fondo al report (Markdown e pagina): data, numero di affermazioni verificate, correzioni, che cosa resta non verificabile.
