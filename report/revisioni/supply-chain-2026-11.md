# Revisione: «Supply chain e logistica — novembre 2026»

Revisore indipendente (assistente AI, Claude) · 9 novembre 2026 · per Gabriele Giuliani

Oggetto: `report/supply-chain-2026-11.md` e `docs/report/supply-chain-2026-11.html`, generati da `report/costruisci_supply_chain.py`.
Criteri: i criteri del mandato e, appena è comparso durante la revisione, `report/STANDARD.md` (in particolare: «In breve» di al massimo 5 punti sotto le 60 parole circa, nessun numero nell'«In breve» che non sia nel corpo, termini tecnici spiegati, didascalie con file e data del dato, riquadro «Revisione» finale).

Le correzioni sono tutte nello script (testo, `FATTI_ESTERNI`, soglie, rendering); il report è stato rigenerato. Non ho toccato `docs/index.html`, `docs/report/index.html` né i file di `docs/data/`. Lo script ha riscritto, come fa a ogni esecuzione, la propria cache `report/dati/porti-europei.json`. Nessun commit.

## 1. Esito in breve

- **59 affermazioni controllate** (59 righe della sezione 2, oltre 100 numeri): 43 contro i JSON, 16 anche contro la fonte esterna (10 confermate, 6 non verificabili). Errori di calcolo nei dati: nessuno. Errori o imprecisioni del testo: 9, corretti (sezione 3).
- **Due dati non più validi**: il Baltic Dry (tolto da `noli.json`) e le soglie dei transiti (incoerenti con il metodo del cruscotto del rischio).
- **Un titolo fuorviante** in «In breve» («Il Mar Rosso si riapre»), in contrasto con il report Hormuz e con il cruscotto.
- **Aggiunta** la sezione 8 «Cosa significa per il Nord Europa» e il riquadro «Revisione» in fondo al report.

## 2. Verifica dei numeri

Esito: **ok** = coincide; **corretto** = cambiato nel report; **non verificabile** = fonte non raggiungibile o unica.

### Stretti e Mar Rosso

| Affermazione | Nel report (prima) | Verificato | Fonte | Esito |
|---|---|---|---|---|
| Suez, navi/giorno (7 gg al 1/11) | 43,0 | 43,0 | portwatch.json | ok |
| Suez su un anno | +10% | +10,3% | portwatch.json | ok |
| Suez «57% di fine 2023» | 57% | 56,6% della stessa settimana 2023; 58,4% della media gen–ott 2023 (riferimento del cruscotto, 73,6) | portwatch.json, rischio.json | corretto (58%, media gen–ott 2023) |
| Bab el-Mandeb, navi/giorno | 27,3 | 27,3 | portwatch.json | ok |
| Bab el-Mandeb su un anno | −22% | −22,0% | portwatch.json | ok |
| Bab el-Mandeb «34% di fine 2023» (cruscotto) | 34% | 34,3% stessa settimana; 36,6% della media gen–ott 2023 (74,6) | portwatch.json, rischio.json | corretto (37%) |
| Hormuz, navi/giorno | 4,4 | 4,4 (−94,8% sulla media 2025, 85,5) | portwatch.json, rischio.json | ok |
| Hormuz, LLI | assente | 116 transiti non legati all'Iran, 19–25 ottobre | LLI Strait of Hormuz Brief 5/11 (aperta) | aggiunto |
| Capo, navi/giorno e 189% di fine 2023 | 92,0; 189% | 92,0; 189% (stessa sett.), 187% sulla media gen–ott 2023 | portwatch.json | corretto (media gen–ott 2023) |
| Tabella transiti (9 passaggi) | valori | coincidono riga per riga | portwatch.json | ok |
| Colonna «su 3 anni (fine 2023)» | etichetta | è la stessa settimana di ottobre 2023 | portwatch.json (`media7_tre_anni_prima`) | corretto (etichetta) |
| Pre-crisi Suez 74, Capo 49 | 74; 49 | media mensile gen–ott 2023 | portwatch.json (serie) | ok |
| BIMCO: 753.000 TEU/sett. contro 1.457.000 | idem | idem, «per la prima volta sopra il 50%» | BIMCO 14/10/2026 (aperta) | ok |
| LLI: 1.195 transiti, 111 Mt tpl, 28/9–25/10; −36% | idem | 1.195 e 111m dwt confermati; il −36% si riferisce alla settimana 19–25 ottobre | LLI Red Sea Brief 29/10 (aperta) | ok, con precisazione (dato in stretti-dettaglio.json, non modificato) |
| LLI Bab el-Mandeb 295 transiti 12–18/10, −8%, −46% | idem | idem | LLI 29/10 (aperta) | ok |
| UNCTAD/Riviera: deviazione via Capo | idem | pagine non aperte (Riviera 429) | stretti-dettaglio.json | non verificabile |

### Noli

| Affermazione | Prima | Verificato | Fonte | Esito |
|---|---|---|---|---|
| WCI composito 5/11 | 4.389 $ | non aperto (Drewry irraggiungibile); 4.429 $ il 29/10 e «−1% sulla settimana» nel report Hormuz: coerente | noli.json; ricerca web | non verificabile (coerente) |
| WCI Shanghai–Genova / –Rotterdam | 4.166 / 3.615 | 4.166 / 3.615 | noli.json; The Loadstar (risultato di ricerca) | ok |
| WCI un anno prima (composito, Genova, Rotterdam) | 1.959 / 2.111 / 1.962 | idem | Cyprus Shipping News 12/11/2025 (aperta) | ok |
| Variazioni su un anno +124% / +97% / +84% | idem | +124,0% / +97,3% / +84,3% | calcolo | ok |
| FBX globale 3.452, −6% dal 14/8, +3% su 4 settimane | idem | 3.451,8; −6,5%; +3,2% (dal 9/10) | noli.json | ok |
| FBX13 4.324 (−1,17%), FBX11 3.422 (−4,8%) | idem | idem in noli.json; il comunicato settimanale del Baltic Exchange (6/11) dà 4.315 e 3.384, indice 3.497 | noli.json; Baltic Exchange via The Edge (aperta) | ok (scarto 1–1,3% tra istantanee: dichiarato) |
| SCFI 3.633,45 (−1,5%), CCFI 1.924,69 (+2,3%), CCFI Med +6,8% | idem | idem | noli.json | ok |
| Baltic Dry 2.854, +37% su un anno (9/11) | idem | non più in noli.json (raccolta sospesa per i termini di Trading Economics) | noli.json (nota) | corretto: 2.805 punti il 6/11, citato a mano, senza variazione annua |

### Porti

| Affermazione | Prima | Verificato | Fonte | Esito |
|---|---|---|---|---|
| Tabella 9 porti italiani (7 e 30 gg) | valori | coincidono | portwatch.json | ok |
| Genova 30 gg | −4% | −4,5% | portwatch.json | corretto (−5%, arrotondamento commerciale) |
| Ravenna import stimato −24% | idem | −23,9% (media 30 gg) | portwatch.json | ok |
| Genova import 7 gg +31% | idem | +31,2% | portwatch.json | ok |
| Porti europei (9) | valori | coincidono con nuovo download PortWatch | report/dati/porti-europei.json | ok |
| Porti italiani 12,8 mln TEU 2025, +1% H1 2026; −4,6% T1 2026 | idem | pagine non aperte | Intesa SRM, 9colonne | non verificabile |
| «I porti container beneficiano del ritorno a Suez» | valutazione | Genova −4,5% e Gioia Tauro −5,7% sui 30 gg, Livorno container −31% | portwatch.json | corretto (ridimensionato) |
| Cali adriatici «coerenti con meno greggio dal Golfo» | valutazione | dal Golfo arriva solo il 5,6–10,2% del greggio italiano | paesi.json | corretto |

### Energia, materie, rischi

| Affermazione | Prima | Verificato | Fonte | Esito |
|---|---|---|---|---|
| Brent 92,62, −12% 1m, +46% 1a | idem | 92,62; −11,55%; +45,56% (ultimo valore provvisorio) | prezzi.json (campo var) | ok; aggiunta nota «provvisorio» |
| TTF 82,33, +1% 1m, +164% 1a | idem | 82,33; +1,11%; +163,88% | prezzi.json | ok |
| Henry Hub 3,21, 0%, −26% | idem | 3,214; −0,19%; −25,52% | prezzi.json | ok |
| SOX 10.046, −20% 1m, +42% ytd; TSMC −14% | idem | 10.046,2; −20,09%; +41,83%; −13,75% | prezzi.json | ok |
| Gasolio self 2,224 €/l (7/11) | idem | 2,224 (Mimit) | Affaritaliani (aperta) | ok |
| Accise: +4,9 cent dall'8/11 | idem | Motor1 risponde 403 | — | non verificabile |
| Gasolio un anno prima 1,627 | idem | pagina non aperta | QuiFinanza | non verificabile (già «affidabilità bassa») |
| Ingressi gas: Mazara 34,0%, Melendugno 16,5%, Adriatic LNG 14,1%, Passo Gries 13,0% | idem | idem | gas-italia.json | ok |
| Stoccaggi IT 88,93%, −4,7 p. su un anno, −1,07 p. dal 90% | idem | 88,93; −4,72; −1,07 | scorte.json | ok |
| Germania 58,9%, «−29,7 punti sotto la media» | doppia negazione | 58,94; scarto −29,674 | scorte.json | corretto (testo) |
| GNL: 14,5% della liquefazione dietro Hormuz (82,9/570); IT 21,8 Mt rigass. | idem | ricalcolato dallo script | terminali-gnl.json | ok |
| GNL italiano 45,3% USA, 32,6% Qatar | idem | idem | paesi.json | ok |
| Distillati USA 99,3 mb, −13,3% sulla media 5 anni | idem | 99,259; −13,3% | scorte.json | ok |
| Scorte d'emergenza IT 77,2 giorni contro 90,5 | idem | idem | scorte.json | ok |
| Terre rare: sospensione n. 70/2025 scade il 10/11/2026 | idem | confermato | Mining Technology (aperta) | ok |
| CRM UE: 100% terre rare pesanti dalla Cina, 98% borato, 71% platino | idem | testo noto del comunicato IP/23/1661 | Commissione UE | ok |
| Grano: mondo 276,0 Mt (−2,0%), UE 11,7 (−38%), 10% del consumo, Russia 19,1 | idem | 276,04; −2,0; 11,72; −38,2; 10,1; 19,09 | scorte.json | ok |
| Italia 95,2% gas, 89,8% petrolio importati; Cina 2° fornitore 10,2% | idem | Germania 14,4%, Cina 10,2% | paesi.json | ok |
| Cavi: IT 37 cavi e 55 approdi; 6 cavi verso l'Asia; Mar Rosso 24, Baltico 34 | idem | idem | cavi.json | ok |
| 14 incidenti dal 2023, 3 nel 2026 | idem | 14; 2026: 29/4, 14/6, 8/8 | cavi-incidenti.json | ok |
| Starlink «attribuiti alla Russia dai governi» | generico | LT (premier, collega i tre) e PL (governo); BG nessuna attribuzione propria | ibrido.json | corretto |
| Flotta ombra: 2.022 sanzionate (950 RU, 679 IR), 1.163 probabili | idem | idem | sanzioni-navi.json | ok |
| Golfo di Finlandia 38 su 96 petroliere sanzionate | idem | idem | navi.json | ok |
| 4 navi con posizioni impossibili | idem | 4 | navi.json | ok |
| Ferrovie: 20.022 treni 2025; 2,05 mln TEU; 5.460 treni T1 2026 | idem | idem | ferrovie.json | ok |
| Ferrovie: etichette delle fonti Middle Corridor e INSTC | «Organizzazione degli Stati turchi», «Ferrovie russe» | i link puntano a BESA Center e Gulf Research Center | ferrovie.json | corretto (nome completo della fonte) |
| 2,05 mln TEU = 2,7 settimane di Suez | idem | 2.050.000 / 753.000 = 2,72 | calcolo | ok |

## 3. Correzioni fatte (nello script)

1. **Baltic Dry.** Tolto dal flusso automatico; nuovo `FATTI_ESTERNI["bdi"]` (2.805 punti, 6/11/2026, Baltic Exchange ripreso da Trading Economics, affidabilità media), senza variazione su un anno. Tolto dalla tabella delle soglie e dal cruscotto; testo «le rinfuse vanno in senso opposto» eliminato (non dimostrabile senza serie).
2. **«In breve».** «Il Mar Rosso si riapre, Hormuz no» → «Suez si riprende, Bab el-Mandeb resta a poco più di un terzo, Hormuz è chiuso di fatto», con i livelli del cruscotto del rischio e il conteggio LLI (fonte aperta) per i transiti con AIS spento. Nuovo punto sul Nord Europa.
3. **Soglie dei transiti allineate al metodo.** `SOGLIE` per Hormuz/Suez/Bab el-Mandeb (60/20 navi, 80/50%, 60/25%) sostituite dalle soglie del metodo (−10%/−30% sul riferimento, stesso riferimento di `rischio.json`). Con le vecchie soglie Suez (57%) e Bab el-Mandeb (34%) erano «attenzione»; per il metodo sono rossi (e Bab el-Mandeb è sotto la soglia di disruption del −50%).
4. **Vocabolario degli stati.** «normale/attenzione/critico» → «verde/giallo/rosso», come il metodo: «critico» nel cruscotto è un livello di P×I (≥ 20), non lo stato di un indicatore.
5. **Prezzi: differenza spiegata, non nascosta.** Il report misura il *livello* (costo per chi importa), il cruscotto le *variazioni* (90 giorni, un anno). Nuova colonna «Cruscotto del rischio» con la lettura del metodo (es. TTF: verde sulla media 90 gg, rosso su un anno). Le soglie Brent 85, TTF 70 e WCI Genova 5.000 coincidono con quelle degli scenari del report Hormuz: ora è scritto.
6. **Riferimento pre-crisi.** I rapporti di Suez, Bab el-Mandeb e Capo usano la media gennaio–ottobre 2023, come il cruscotto; la colonna della tabella dice «stessa settimana del 2023».
7. **Valutazione sui porti** corretta (vedi tabella) e «In breve» sui porti con i numeri.
8. **Fonti ferroviarie, Starlink, doppia negazione, arrotondamenti** (metà per eccesso, così −20,5 è −21% come nel cruscotto); formato delle variazioni FBX uniformato (−1,2% invece di «-1,17%»).
9. **Nord Europa.** Nuova sezione 8 da `porti-nord.json` (12 porti, chiamate a 30 giorni e traffico 2025 con fonte), `esposizione-nord.json` (GNL per origine, IEEFA; Danimarca esportatrice netta), `scorte.json`, `navi.json`, `cavi-incidenti.json`, `noli.json`, `rischio.json`. Stretti danesi nella tabella dei transiti e nel cruscotto, con l'avvertenza che PortWatch misura solo l'Øresund. Valutazione marcata.
10. **Grafici.** Il grafico dei porti ha un terzo gruppo (Nord Europa) e la data nel sottotitolo; sottotitoli dei grafici noli e porti accorciati sul mobile (a 390 px uscivano dal riquadro).
11. **Metodo e limiti.** Aggiunti: prezzi Yahoo con 3 mesi di serie e variazioni dal campo `var`; ultimo valore provvisorio; Baltic Dry citato a mano; soglie di livello contro soglie del metodo; file nuovi non ancora letti (`commercio.json`, `minerali.json`).
12. **Adeguamento a STANDARD.md.** «In breve» ridotto da 6 a 5 punti, ciascuno di 41–61 parole; il conteggio LLI e i livelli numerici del cruscotto spostati nel corpo (sezione 2), così ogni numero dell'«In breve» è anche nel corpo. Aggiunto un glossario (AIS, FEU/TEU, indici dei noli, Baltic Dry, GNL, TTF, Brent, flotta ombra, GNSS, chiamata). Didascalie dei grafici con file e data del dato e con gli eventi segnati.
13. **Riquadro «Revisione»** in fondo al report (dati in `REVISIONE` nello script, da riscrivere a ogni edizione).

## 4. Logica e coerenza

- **Con il report Hormuz.** Ora coerenti: Bab el-Mandeb come «secondo Hormuz» anche nel titolo; LLI citato nello stesso modo (116 transiti, 19–25 ottobre). Differenze rimaste e spiegabili: il report Hormuz cita Brent 92,58 (lettura delle 19:38), questo report 92,62 (prezzi.json delle 19:47), entrambi provvisori. **Da correggere nel report Hormuz (fuori dal mio mandato):** cita ancora «Baltic Dry a 2.854 punti, +37% su un anno (Trading Economics)», dato non più raccolto.
- **Con `rischio.json`.** Hormuz critico 22,5; Bab el-Mandeb alto 19,0; Suez medio 9,9; Stretti danesi medio 8,3; Baltico medio 9,0. Il report ora li riporta, e gli stati dei transiti coincidono con quelli degli indicatori di flusso del cruscotto.
- **Incoerenza nei dati, segnalata a chi li cura:** in `esposizione-nord.json` la scheda della Lituania data a «gennaio 2026» un danno ai cavi che `cavi-incidenti.json` registra il 26 gennaio 2025 (Ventspils–Gotland); il report usa `cavi-incidenti.json`. In `noli.json` le `fonti` elencano ancora Trading Economics anche se il Baltic Dry è stato tolto.

## 5. Chiarezza per un selezionatore del Nord Europa

Prima della revisione il report era tutto italiano: nessun porto oltre Rotterdam, Anversa e Amburgo, niente Stretti danesi, niente GNL del Nord. La sezione 8 risponde a tre domande di un porto o di un operatore energetico nei Paesi Bassi, in Danimarca o nel Baltico: come vanno i miei porti (tabella e testo), quanto mi costa la crisi (noli Nord Europa −21% rispetto al Mediterraneo; stoccaggi NL 63,5% e DE 58,9%), dove sono esposto (GNL USA, Polonia sul Qatar, flotta ombra nel Golfo di Finlandia, cavi). Limite: per la Danimarca `paesi.json` non ha indicatori; uso `esposizione-nord.json`.

## 6. Cosa resta non verificabile

- WCI composito 4.389 $ (Drewry non raggiungibile; coerente con 4.429 $ del 29/10 e −1%).
- Baltic Dry 2.805: unica fonte secondaria (Trading Economics, dominio non raggiungibile da questa sessione).
- Accise sul gasolio (Motor1, 403), GNSS nel Golfo (Windward), deviazioni via Capo (Riviera, 429), TEU Cina–Europa (Railmarket, 403), gasolio 2025 (QuiFinanza), traffico container italiano (Intesa SRM, 9colonne).
- Le schede curate (`stretti-dettaglio.json`, `ferrovie.json`, `ibrido.json`, `esposizione-nord.json`, traffico annuo di `porti-nord.json`) controllate solo a campione.
- Frasi lunghe: molte frasi del corpo superano le 30 parole indicate da STANDARD.md (soprattutto le schede generate dai JSON curati); non le ho riscritte tutte.
- I numeri di `offshore-nord.json` non sono usati: EMODnet ha stati in ritardo e duplicati dichiarati nel file stesso.

## 7. Verifica visiva

Playwright (Chromium) su `docs/report/supply-chain-2026-11.html` a 1440×900 e 390×844: nessuno scorrimento orizzontale della pagina (scrollWidth = clientWidth in entrambi i casi), nessun errore in console, quattro grafici visibili nella versione giusta (710 px e 340 px), nessun testo SVG fuori dal riquadro dopo la correzione, sezioni `#nord` e `#revisione` presenti. Le tabelle larghe scorrono dentro il proprio riquadro sul mobile, come previsto dal CSS.
