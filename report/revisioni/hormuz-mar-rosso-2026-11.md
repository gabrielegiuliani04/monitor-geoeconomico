# Revisione: «Hormuz e Mar Rosso: energia, logistica e mercati» (novembre 2026)

**Revisore:** revisione indipendente (fact-checking ed editing), svolta con un assistente AI · **Data:** 9 novembre 2026, sera
**Testo rivisto:** [`report/hormuz-mar-rosso-2026-11.md`](../hormuz-mar-rosso-2026-11.md) e [`docs/report/hormuz-mar-rosso-2026-11.html`](../../docs/report/hormuz-mar-rosso-2026-11.html)
**Standard di riferimento:** [`report/STANDARD.md`](../STANDARD.md)

## Sintesi

- Affermazioni verificate: 183 (ogni numero del testo e i fatti datati della cronologia): 135 confermate, 38 corrette, 10 non verificabili da qui.
- Errori trovati e corretti nel Markdown e nella pagina HTML; i grafici **non** sono stati rigenerati (motivo nella sezione 3).
- Il problema più serio non è nel testo ma nei dati: lo script dei prezzi (`raccolta/scarica_mercati.py`, riga 102) converte i timestamp di Yahoo con lo scarto UTC attuale di New York (−5 h, ora solare) anche nei mesi di ora legale. Risultato: tra l'8 marzo e il 1° novembre 2026 ogni seduta di Brent, WTI, TTF, Henry Hub, oro, argento ed euro/dollaro è registrata un giorno prima (11 valori cadono di domenica; nella serie del Brent c'è un solo venerdì). Il report riportava quindi date sbagliate di un giorno per i massimi di marzo e ottobre e per il picco di settembre.

Metodo: confronto con i file `docs/data/*.json` (lettura diretta con Python), con i rapporti degli agenti in `report/agenti/` e con le fonti citate, scaricate e lette il 9 novembre (44 link: 36 raggiungibili, 7 bloccati con 403, 1 con 404 per un indirizzo senza `www`). Per i prezzi storici, che `prezzi.json` non contiene più (vedi sotto), la serie del Brent è stata riscaricata da Yahoo Finance (2 anni, giornaliera). La serie del TTF non è stata riscaricabile: le sue date sono corrette applicando lo stesso scarto, documentato nel file.

## 1. Tabella di verifica

Esiti: **ok** = corrisponde; **corretto** = sbagliato o impreciso, corretto nel testo; **n.v.** = non verificabile da qui (fonte a pagamento, sito non raggiungibile, dato presente solo nei rapporti degli agenti senza fonte primaria).

### In breve e cifre in testa

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 1 | Hormuz, navi al giorno, settimana al 1/11 | 4,4 | 4,4 (26/10–1/11) | `portwatch.json`, `media7` | ok |
| 2 | Hormuz, stessa settimana 2025 | 90,3 | 90,3 | `portwatch.json` | ok |
| 3 | Variazione su un anno | −95% | −95,1% | `portwatch.json` | ok |
| 4 | Petroliere, ora / un anno prima | 1,4 / 50,1 | 1,4 / 50,1 | `portwatch.json` | ok |
| 5 | LLI, transiti 19–25 ottobre, navi non legate all'Iran | 116 | 116 (vs 124 la settimana prima) | LLI, Hormuz Brief 5/11 | ok |
| 6 | «circa cinque volte di più» | 5× | 116 / 23 = 5,0× per la stessa settimana; ma il testo accostava 4,4/giorno (settimana 26/10–1/11) a 116 (settimana 19–25/10) | `portwatch.json`, LLI | corretto (stessa settimana nei due numeri) |
| 7 | Bab el-Mandeb, petrolio 2° trim. 2026 / 4° trim. 2025 | 8,1 / 5,4 mb/g | 8,1 / 5,4 | EIA STEO via Rigzone | ok |
| 8 | Houthi: chiusura alle navi saudite «da luglio» | luglio | dichiarazione del 20 luglio | AP via WTOP; `energia.md` | ok (precisata la data) |
| 9 | Suez, navi a ottobre; «mese più trafficato dall'ottobre 2023» | 1.490 | 1.490, massimo dall'inizio della crisi del Mar Rosso (ott. 2023) | EgyptToday 5/11 (letto tramite ricerca: sito non raggiungibile direttamente) | ok |
| 10 | Brent 9/11 | 92,58 $ | 92,62 $ in `prezzi.json` (lettura delle 19:47 UTC, provvisoria); 90,75 $ su Yahoo alle 20:05 | `prezzi.json` | corretto (allineato al file; marcato provvisorio) |
| 11 | Brent, variazione giornaliera | −5,8% | −5,8% | `prezzi.json` | ok |
| 12 | Brent, su un anno | +45,5% | +45,56% → +45,6% | `prezzi.json` | corretto (arrotondamento) |
| 13 | Brent, massima chiusura | 118,35 il 30 marzo | 118,35 il **31 marzo** (seduta); il 30 in `prezzi.json` per l'errore di fuso | Yahoo Finance, timestamp 2026-03-31 04:00 UTC | corretto |
| 14 | Brent, «due massimi» 118,35 e 117,64 | due massimi | c'è anche 118,03 il 29 aprile, sopra 117,64 | Yahoo Finance | corretto (aggiunto 118,03 nel corpo; tolto dall'In breve) |
| 15 | Brent 117,64 | 29 ottobre | **30 ottobre** | Yahoo Finance | corretto |
| 16 | TTF 9/11 e su un anno | 82,33 €/MWh, +164% | 82,33; +163,9% | `prezzi.json` | ok |
| 17 | Ras Laffan in forza maggiore dal 4 marzo | 4 marzo | dichiarata il 4 marzo | The National 4/3; Global LNG Hub | ok |
| 18 | Forza maggiore «prorogata almeno a fine dicembre» | fine dicembre | prorogata a fine dicembre per Edison (e, secondo Reuters, per acquirenti in Pakistan e Bangladesh); `energia.md` diceva «fino a novembre» | gasworld; OilPrice | ok (aggiunta la fonte, che mancava) |
| 19 | Inflazione area euro ottobre (flash) | 4,0% | 4,0%, da 3,8% | `calendario.json` | ok |
| 20 | BCE deposito, rialzi di giugno e settembre | 2,50% | 2,25% l'11 giugno, 2,50% il 10 settembre (in vigore dal 16/9) | Euronews 10/9; `calendario.json` | ok |
| 21 | Bank of England 5/11 | 4,00% | 4% | `calendario.json`; `calendario.md` | ok |
| 22 | Fed, due voti per un rialzo | 3,75–4,00%, 2 voti | voto 10-2, Cook e Hammack per un rialzo | `calendario.json`; `calendario.md` | ok |
| 23 | Italia, greggio dal Golfo | 5,6–10,2% | 5,6–10,2% | `paesi.json` | ok |
| 24 | Italia, GNL dal Qatar 2025 | 32,6% | 32,6% (in valore) | `paesi.json` | ok |
| 25 | TransMed, quota 12 mesi | 34,0% «del gas entrato in Italia» | 34,0% degli ingressi da gasdotti e GNL, **senza** produzione nazionale e stoccaggi | `gas-italia.json` | corretto (perimetro precisato) |
| 26 | TransMed «il punto più critico» | — | nel cruscotto del rischio il TransMed è «basso» (5,6/25: impatto 4,3, probabilità 1,3) | `rischio.json` | corretto (ora «dipendenza maggiore», con il dato del cruscotto) |
| 27 | Scorte petrolifere di emergenza Italia | 77,2 giorni | 77,2 (agosto 2026) | `scorte.json` (Eurostat) | ok |

### Cronologia (sezione 2)

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 28 | Inizio della guerra | 28 febbraio, «tra Iran e Stati Uniti» | 28 febbraio; le fonti parlano di guerra di USA e Israele contro l'Iran | Al Jazeera 9/11; `report.json` | corretto (formulazione) |
| 29 | Transiti Hormuz 28/2, 1/3, 2/3 | 57, 20, 4 | 57, 20, 4 | `portwatch.json` | ok |
| 30 | TTF 27/2 → 2/3 | 31,96 → 44,51 (+39%) | 31,96 → 44,51 (+39,3%), date prima dell'ora legale: corrette | grafico (`prezzi.svg`, lettura 19:38) | ok |
| 31 | Brent 27/2 → 2/3 | 72,48 → 77,74 | 72,48 → 77,74 | Yahoo Finance | ok |
| 32 | Ras Laffan: treni 4 e 6, 12,8 Mt/anno | S4, S6, 12,8 | S4 e S6, 12,8 Mt/anno (circa 17% dell'export) | Global LNG Hub | ok |
| 33 | Fujairah, droni il 14 marzo, carichi sospesi | 14/3 | presente solo in `energia.md`, senza link; il link di Al Jazeera citato riguarda l'attacco del 4 maggio | `energia.md`; Al Jazeera 5/5 | n.v. (marcato nel testo; fonte riallineata) |
| 34 | Kirkuk–Ceyhan riprende il 17–18 marzo | 17–18/3 | ripresa annunciata il 18/3, circa 250.000 b/g | The National 18/3 | ok |
| 35 | Brent 119 $ il 19 marzo (in seduta) | 119 | 119 in seduta, chiusura 108,65 | Howden Re 27/3; Yahoo 108,65 | ok (aggiunta la chiusura) |
| 36 | War risk da 0,25% a fino al 3% | 0,25% → 3% | «from 0.25% … to as much as 3%» per navi legate a USA, Regno Unito, Israele | Howden Re | ok |
| 37 | Est-Ovest «pompa ai 7 mb/g dichiarati da Aramco» | 7 mb/g | a pieno regime, 7 mb/g, **secondo una persona informata** (anonima); 2 mb/g vanno alle raffinerie saudite; 7 mb/g è la capacità annunciata da Aramco nel 2025 (IEA) | Fortune 28/3; IEA | corretto (fonte anonima esplicitata) |
| 38 | Tregua 8 aprile | 8/4 | 8 aprile | `report.json` | ok |
| 39 | Blocco USA dei porti iraniani 13 aprile | 13/4 | «imposto il 13 aprile» | `report.json` (The New Arab: 403) | ok |
| 40 | Riapertura annunciata e revocata, 17–18 aprile; PortWatch 20 il 18, 2 il 19 | 20 / 2 | 20 il 18/4, 2 il 19/4 | `portwatch.json`; The New Arab non raggiungibile | ok (dati); n.v. (annuncio) |
| 41 | BCE al 2,25% a giugno | 2,25% | 11 giugno, prima mossa in tre anni | Euronews 10/9 | ok |
| 42 | Memorandum di Islamabad di giugno, poi saltato | — | «il memorandum di Islamabad di giugno è saltato» | `report.json` | ok |
| 43 | Blocco USA sospeso il 18 giugno | 18/6 | «sospeso il 18 giugno» | `report.json` | ok |
| 44 | Hormuz fino a 51 transiti il 24 giugno | 51 | 51 (massimo di giugno) | `portwatch.json` | ok |
| 45 | Brent «minimo della guerra 71,99 il 25 giugno» | 71,99 / 25/6 | 71,99 è la seduta del **26 giugno**; il minimo dopo il 2 marzo è **71,57 il 1° luglio** | Yahoo Finance | corretto |
| 46 | Blocco ripreso il 14 luglio; ostilità in mare da inizio luglio (UKMTO) | 14/7 | sì | `report.json` (RFE/RL) | ok |
| 47 | Houthi, blocco navi saudite 20 luglio | 20/7 | sì | AP via WTOP; `energia.md` | ok |
| 48 | «6 agosto: una seconda metaniera qatariota colpita nel Mar Rosso» | Mar Rosso, 6/8 | la GasLog Shanghai è stata colpita il **31 luglio** vicino a Limah (Oman), cioè all'uscita di Hormuz, non nel Mar Rosso; il 6 agosto è la data dell'articolo. Nel Mar Rosso, 20/7–2/8, gli Houthi colpiscono quattro petroliere saudite | Cyprus Shipping News 6/8 | corretto |
| 49 | Ultimo attacco UKMTO nel Mar Rosso 24 agosto | 24/8 | «no attacks since August 24» | LLI Red Sea Brief 29/10 | ok |
| 50 | BCE 2,50% il 10/9; inflazione agosto 3,3%, energia +14,3% | 3,3 / 14,3 | 3,3%; energia 14,3% | Euronews | ok |
| 51 | Est-Ovest fermato l'11–13 settembre da droni partiti dall'Iraq | 11–13/9 | chiuso dopo attacchi partiti dall'Iraq; The National data lo stop al 13/9 | Al-Monitor; The National 22/9 | ok |
| 52 | Riavvio a basso regime intorno al 22 | 22/9 | riavvio del 22/9 «at a low rate» | The National 22/9 | ok |
| 53 | Brent 107,63 il 9 settembre | 9/9 | 107,63 è la seduta del **10 settembre** | `prezzi.json` (data anticipata di un giorno) | corretto |
| 54 | QatarEnergy proroga la forza maggiore il 28 settembre | 28/9 | articolo esistente (il link senza `www` dava 404: corretto) | The National 28/9 (tramite ricerca) | ok (link corretto) |
| 55 | TTF 103,94 massimo dell'anno | 29 ottobre | massimo dell'anno, seduta del **30 ottobre** | `prezzi.json` (stessa convenzione delle date del Brent) | corretto |
| 56 | Fed 28/10 e BCE 29/10 invariate | — | sì | `calendario.json`; comunicato BCE | ok |
| 57 | Avvisi UKMTO 1–8 novembre «da 194 a 200» | 194–200 | nel periodo sono usciti gli avvisi 191–200 (191–193 riguardano il 1° novembre, pubblicati il 2) | `eventi.json` | corretto |
| 58 | Petroliera colpita a nord del Qatar «il 4», probabilmente la Velos Sapphire, un marittimo morto | 4/11 | UKMTO 196: sera del 4 secondo Reuters; l'armatore della Velos Sapphire parla di giovedì 5 | `eventi.json` | corretto («il 4–5») |
| 59 | Attacchi USA su Qeshm il 2 e il 6 | 2 e 6/11 | sì (AP; Trump conferma il 6) | `eventi.json` | ok |
| 60 | Pasdaran: tre petroliere su rotta «non autorizzata» l'8 | 3 | rivendicazione, affidabilità media | `eventi.json` | ok (è scritta come rivendicazione) |
| 61 | Houthi: Abqaiq e Riyadh l'8 | — | rivendicazioni; edificio Aramco a Riyadh danneggiato (CNN, video geolocalizzati) | `eventi.json` | ok |
| 62 | Bank of England 4,00% il 5/11 | 4,00% | sì | `calendario.json` | ok |
| 63 | Piano iraniano di riapertura «in due giorni» portato dal premier del Qatar | 2 giorni | «Tehran's two-day proposal developed with Qatari mediators» | Al Jazeera 9/11 | ok |
| 64 | TTF 9/11 −3,8% | −3,8% | −3,81% | `prezzi.json` | ok |
| 65 | GPR marzo / agosto / ottobre 2026 | 330 / 126 / 151 | 330,2 / 125,8 / 150,5 | `gpr.json` | ok |

### Hormuz (sezione 3)

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 66 | Petrolio da Hormuz 2025 | 19,9 mb/g | 19,87 | IEA Factsheet, tabella | ok |
| 67 | Greggio / prodotti | 14,95 / 4,93 | 14,95 / 4,93 | IEA | ok |
| 68 | Quota del greggio commerciato | quasi 34% | «nearly 34%» | IEA | ok |
| 69 | Per origine: SA 6,23; IQ 3,63; EAU 3,24; IR 2,41; KW 2,37; QA 1,43 | — | identici | IEA | ok |
| 70 | GNL via Hormuz | poco più di 112 mld m³, quasi 20% | «just over 112 bcm … almost 20%» | IEA | ok |
| 71 | 93% del GNL qatarino, 96% di quello emiratino | 93 / 96 | sì | IEA | ok |
| 72 | Urea: un quarto dell'export mondiale | 1/4 | «nearly one-quarter» | Banca Mondiale | ok |
| 73 | Urea: 43% dell'urea via mare | 43% | 43% (NDSU) | Fertilizer Daily | ok |
| 74 | 80% del petrolio verso l'Asia | 80% | «80% destined for Asia» (greggio) | IEA | ok |
| 75 | Cina, India, Giappone, Corea: 69% del greggio 2024 | 69% | 69% | EIA | ok |
| 76 | All'Europa 4% del greggio, circa 600.000 b/g | 4%, 600 kb/g | «around 600 kb/d, or just 4%» | IEA | ok |
| 77 | All'Europa «poco più del 10% del GNL» | 10% | 10% del GNL **che passa da Hormuz** (diverso dal 7% del GNL europeo che arriva da Hormuz) | IEA | corretto (perimetro esplicitato) |
| 78 | Media 2025 / febbraio 2026 | 85,5 / 78,3 | 85,53 / 78,29 | `portwatch.json` | ok |
| 79 | Media mensile da marzo mai sopra 13; 12,9 a giugno | 12,9 | 12,93 (marzo 3,2 … ottobre 3,8) | `portwatch.json` | ok |
| 80 | Settimana 26/10–1/11: 1,4 petroliere, 1,9 rinfuse; 1 transito il 1/11 | — | identici | `portwatch.json` | ok |
| 81 | PortWatch 19–25 ottobre: 23 transiti, 6 petroliere | 23 / 6 | 23 / 6 | `portwatch.json` (somma) | ok |
| 82 | LLI: 95 petroliere e gasiere | 95 | 95 | LLI 5/11 | ok |
| 83 | LLI «ricostruisce» i transiti dark con immagini satellitari e analisti | — | il brief non descrive il metodo; dice che la settimana è «completa» solo con ritardo per i transiti dark; perimetro: navi da carico > 10.000 tpl | LLI 5/11 e 29/10 | corretto (tolto il dettaglio non documentato; aggiunto il perimetro) |
| 84 | LLI media 121 a settimana 5–25 ottobre | 121 | 121 | LLI | ok |
| 85 | Kpler: circa due terzi dei transiti «dark» | 2/3 | «about two-thirds … since the July collapse of the ceasefire» | Gulf News (fine agosto) | ok |
| 86 | Circa 17 navi al giorno (LLI) | 17 | 116/7 = 16,6 | calcolo | ok |
| 87 | UKMTO: 144 eventi, 75% delle navi ha proseguito | 144 / 75% | sì | LLI 5/11 | ok |
| 88 | CENTCOM: 144 mercantili dirottati | 144 | 144 al 5/11; 147 l'8/11 (Al Jazeera) | LLI; `report.json` | ok (aggiunto il dato più recente) |
| 89 | 27 eventi entro 250 km «negli ultimi 30 giorni», 13 attacchi | 30 giorni | 27 e 13 corretti, ma `eventi.json` parte dal 29 ottobre: la finestra reale è di 12 giorni | `eventi.json` | corretto |
| 90 | Est-Ovest: 5 mb/g di progetto, 7 dichiarati | 5 / 7 | 5 di progetto; Aramco ha dichiarato 7 a marzo 2025 | IEA | ok |
| 91 | Yanbu, circa 5 mb/g di export di greggio | 5 | «unlikely to exceed 5 mbd» | Baker Institute | ok |
| 92 | ADCOP 1,5–1,8 mb/g, circa 0,7 liberi | — | 1,5 di progetto, circa 1,8 attuali, fino a 700 kb/d liberi | IEA | ok |
| 93 | Fujairah e Habshan colpite a marzo, aprile e maggio | — | 14/3 (senza fonte primaria), 18/3 e 7/4 Habshan, 4/5 Fujairah | `energia.md`; Al Jazeera 5/5 | ok (marzo parzialmente n.v.) |
| 94 | Goreh–Jask 1 mb/g, fermo a inizio 2026 | 1 | «reported capacity of 1 mb/d … effectively non-operational» | IEA | ok |
| 95 | Jask usato di più ad agosto | — | S&P Global 5/8 (403); ripreso in `energia.md` | `energia.md` | n.v. |
| 96 | Kirkuk–Ceyhan circa 130.000 b/g ad agosto | 130.000 | «near 130,000 bpd» (13/8) | Shafaq | ok |
| 97 | Kirkuk–Ceyhan circa 500.000 b/g a fine ottobre | 500.000 | fonti anonime (Iraqi News: 403) | `energia.md` | n.v. |
| 98 | Dolphin con poca capacità libera | — | «limited spare capacity» | IEA | ok |
| 99 | EIA: Hormuz 4,9 mb/g nel 2° trim. 2026 contro 21,6 nel 4° trim. 2025 (−77%) | 4,9 / 21,6 | identici; −77,3% | EIA via Rigzone | ok |
| 100 | Export del Golfo al 60–80% del normale (Reuters) | 60–80% | sì | `calendario.json` (nota OPEC+) | ok |
| 101 | Vie di aggiramento «al massimo 5,5–7 mb/g» | 5,5–7 | l'IEA stima 3,5–5,5 mb/g di capacità **libera**; in totale (Yanbu circa 5 + ADCOP fino a 1,8 + Ceyhan circa 0,5) circa 6,5–7 | IEA; Baker; Shafaq | corretto (riformulato con le due misure) |
| 102 | Rilascio IEA di 400 milioni di barili = 20 giorni di Hormuz | 400 / 20 | sì | Howden Re | ok |
| 103 | SPR USA 282,2 milioni di barili al 30/10 | 282,2 | 282,184 | `scorte.json` | ok |
| 104 | SPR, minimo dall'ottobre 1982 | 1982 | la serie del file parte dal 2023; il confronto storico è in `scorte.md` (EIA, serie dal 1982) | `scorte.md` | n.v. sul file (ok sul rapporto dell'agente) |
| 105 | SPR −31% su un anno | −31% | 409,6 → 282,2: −31,1% | `scorte.json` | ok |

### Mar Rosso e Suez (sezione 4)

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 106 | Suez + SUMED + Bab el-Mandeb: 12% del petrolio via mare, 8% del GNL (EIA, 1° sem. 2023) | 12 / 8 | dato EIA noto; pagina non riletta | EIA | n.v. |
| 107 | Suez 12–15% del commercio mondiale | 12–15% | UNCTAD: 403 | UNCTAD | n.v. |
| 108 | Bab el-Mandeb 27,3 navi/giorno, −22% su un anno | 27,3 / −22% | 27,3 / −22,0% | `portwatch.json` | ok |
| 109 | «−66% sul 2023 (79,6)» | 79,6 | 79,6 è la **stessa settimana del 2023**, non la media 2023 (74,0) | `portwatch.json`, `media7_tre_anni_prima` | corretto (precisato) |
| 110 | «Il calo è ripartito ad agosto»; medie 36,6 / 27,4 / 27,9 | agosto | medie corrette, ma il calo parte a **luglio** (33,7) | `portwatch.json` | corretto |
| 111 | Bab el-Mandeb 8,1 mb/g nel 2° trim. | 8,1 | sì | EIA | ok |
| 112 | LLI: 295 transiti 12–18 ottobre; tonnellaggio −46% | 295 / −46% | sì | LLI 29/10 | ok |
| 113 | Contatti con sedicenti «autorità yemenite» | — | sì | LLI 29/10 | ok |
| 114 | S&P: transiti legati all'Arabia Saudita 21 a ottobre, 52 a settembre | 21 / 52 | riportato in `energia.md`, fonte primaria non letta | `energia.md` | n.v. |
| 115 | Montingelli: stretto chiuso alle navi saudite dal 3/11, affidabilità media | — | sì | `eventi.json` | ok |
| 116 | Suez 43,0 navi/giorno, +10%, petroliere +22% | — | 43,0; +10,3%; +22,3% | `portwatch.json` | ok |
| 117 | Suez «−43% sul 2023 (76,0)» | 76,0 | stessa settimana del 2023 | `portwatch.json` | corretto (precisato) |
| 118 | Suez 1.490 navi a ottobre, +32% | +32% | 1.490 contro 1.128 a ottobre 2025 = +32% | EgyptToday (via ricerca) | ok |
| 119 | Container 753.000 TEU/settimana, oltre il 50% del 2023 | 753k | 753k contro 1.457k nel 2023 | BIMCO | ok |
| 120 | Alphaliner 63% della capacità Estremo Oriente–Europa | 63% | 5,50 su 8,70 milioni di TEU (15/9–15/10) | Ship & Bunker (Seatrade: 403) | ok |
| 121 | Linerlytica: ritorno completo entro il 1° trim. 2027 | — | sì | Seatrade (via ricerca) | ok |
| 122 | Ricavi FY 2025/26 4,67 mld $ (+23%) | 4,67 / +23% | sì | Ahram (403), Egyptian Streets, Arab News (via ricerca) | ok |
| 123 | Record di 10,2 mld $ «del 2023» | 10,2 | 10,2 nell'anno solare 2023; il record per anno fiscale è 9,4 (2022/23): non confrontabile direttamente con un anno fiscale | gCaptain | corretto (specificato «anno solare») |
| 124 | SUMED fino a 2,5 mb/g | 2,5 | «up to 2.5 million barrels a day» | AP via WTOP | ok |

### Conseguenze (sezione 5)

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 125 | War risk: «da 250.000 a 375.000 dollari» per una nave da 100 milioni | 375.000 | incoerente con il 3% citato nella stessa frase (3% di 100 milioni = 3 milioni). Howden dà «~$375,000–$3M/transit» | Howden Re, tabella | corretto |
| 126 | Straits.live: 32 volte il prebellico, affidabilità bassa | 32× | «priced at 32…»; fonte OSINT con testi AI | straits.live | ok |
| 127 | TD3C quasi triplicato, circa 12 milioni $ a viaggio | 3× / 12 M | sì | Howden Re | ok |
| 128 | WCI 4.389 $/FEU il 5/11 | 4.389 | 4.389 | `noli.json` | ok |
| 129 | WCI −1% sulla settimana | −1% | `noli.json` ha un solo punto; il −1% è in `flussi.md` (Drewry) | `flussi.md` | ok (sul rapporto agente) |
| 130 | Shanghai–Genova 4.166, Shanghai–Rotterdam 3.615 | — | identici | `noli.json` | ok |
| 131 | FBX 3.452 il 6/11, da 3.690 a metà agosto | — | 3.451,8; 3.689,8 il 14/8 | `noli.json` | ok |
| 132 | FBX13 Cina–Mediterraneo 4.324 | 4.324 | 4.324 | `noli.json` | ok |
| 133 | Hapag-Lloyd 1.500 $/TEU | 1.500 | sì | Howden Re | ok |
| 134 | Baltic Dry 2.854, +37% (Trading Economics) | 2.854 | non è in `noli.json` (non più raccolto); presente solo in `nord.md`. **Aggiornamento del 10 novembre:** Trading Economics ricava 2.854 (9/11) e +36,95% da un CFD che replica l'indice; l'ultimo valore dell'indice è 2.805 il 6 novembre | Trading Economics, pagina «Baltic Dry» letta il 10/11; segnalazione di un altro revisore | corretto (2.805 il 6/11; variazione annua tolta perché non verificata) |
| 135 | Brent: media febbraio 69,4, marzo 99,7 | 69,4 / 99,7 | 69,41 / **99,60** (sedute di marzo con date corrette) | Yahoo Finance | corretto |
| 136 | WTI | 86,91 | 86,95 (stessa lettura del Brent) | `prezzi.json` | corretto |
| 137 | Brent +52% da inizio anno | +52% | +52,2% | `prezzi.json` | ok |
| 138 | TTF +192% da inizio anno | +192% | +192,4% | `prezzi.json` | ok |
| 139 | Henry Hub | 3,22 $/MMBtu, −13% | 3,214 → 3,21; −12,8% | `prezzi.json` | corretto (arrotondamento) |
| 140 | Stoccaggi UE 729 TWh a fine agosto, −24% sulla media 5 anni | 729 / −24% | 729,19; −24,3% | `scorte.json` (Eurostat) | ok |
| 141 | IEA: inverno al livello più basso dal 2013; sotto il 10% a fine marzo | — | sì, ma «sotto il 10%» è lo scenario peggiore dell'IEA | IEA, Global Gas Security Review 3/11 (via ricerca: iea.org dà 403) | corretto («nel caso peggiore») |
| 142 | Urea da 475 a 680 $/t | 475 / 680 | sì | Howden Re | ok |
| 143 | Urea oltre 850 $ ad aprile «secondo la stampa» | 850 | lo dice direttamente la Banca Mondiale | Banca Mondiale | corretto (fonte primaria) |
| 144 | Export di fertilizzanti del Medio Oriente −70% | −70% | −70–75% (Kpler) | The National 31/10 | corretto (forbice) |
| 145 | Inflazione USA settembre +3,7%; benzina +9,1% nel mese, oltre metà dell'aumento | — | sì | `calendario.json`; `calendario.md` (BLS) | ok |
| 146 | BCE: comunicato su shock energetico, inflazione su, crescita giù | — | «likely to drive up inflation and lower growth» | comunicato BCE 29/10 | ok (aggiunto il link) |
| 147 | BoE: inflazione 3,5%, vista a circa 5% a metà 2027 | 3,5 / 5 | sì | `calendario.md` (bankofengland.co.uk) | ok |
| 148 | Treasury 10 anni: 4,86% il 6/11 | 4,86 | 4,86 | `prezzi.json`, `curva` | ok |
| 149 | Treasury 10 anni un anno prima | 4,02% | **4,11%** (6/11/2025; +75 pb). 4,02 è il rendimento a 1 mese | `prezzi.json`, `curva.un_anno_fa` | corretto |
| 150 | BTP 10 anni 4,29%; spread 103,7 pb | — | identici | `mercati.json` (ANSA) | ok |
| 151 | PIL USA 3° trim. +3,4% annualizzato | 3,4 | sì | `calendario.json` | ok |

### Chi è esposto (sezione 6)

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 152 | Giappone: greggio 10,3–93,0%; EAU 43,3%, SA 39,5%; dipendenza 87,3% | — | identici | `paesi.json` | ok |
| 153 | Corea: 23,0–68,8%; SA 34,2% | — | identici | `paesi.json` | ok |
| 154 | India: greggio 22,6–47,9%, GNL 47,3–60,8%, Qatar 47,3% | — | identici | `paesi.json` | ok |
| 155 | India: 60% del GPL importato, 90% via Hormuz | 60 / 90 | sì | ORF | ok |
| 156 | Cina: 16,0–37,8%; GNL circa 28%; Malesia 10,5% | — | identici | `paesi.json` | ok |
| 157 | Cina dal Medio Oriente 1,42 mb/g a giugno, minimo dal 2013 | 1,42 | pagina Kpler non leggibile (contenuto caricato da script) | Kpler | n.v. |
| 158 | Bangladesh, India, Pakistan: quasi due terzi del GNL via Hormuz | 2/3 | sì | IEA | ok |
| 159 | Germania 4,0–5,8%, Francia 6,5–8,7%, Paesi Bassi 8,1–9,4%, Spagna 4,3–10,3% | — | identici | `paesi.json` | ok |
| 160 | Circa il 7% del GNL europeo passava da Hormuz | 7% | «around 7% of Europe's total LNG inflows» | IEA | ok |
| 161 | Carichi da Qatar ed Emirati −60 mld m³ tra marzo e ottobre | 60 | pagina IEA: 403 | IEA | n.v. |
| 162 | Stoccaggi 8/11: DE 58,9% (74,9% un anno prima, 88,6% media 5 anni), NL 63,5%, AT 64,3%, FR 80,8% | — | 58,94 (74,88; 88,61), 63,51, 64,34, 80,81 | `scorte.json` | ok |
| 163 | UE 74,6% il 1° novembre | 74,6 | 74,56% | oenergetice.cz (dati AGSI) | ok |
| 164 | Distillati USA −13% sulla media 5 anni | −13% | −13,3% | `scorte.json` | ok |
| 165 | Italia: Libia 24,5%, Azerbaigian 15,9%, Kazakistan 12,5% | — | identici | `paesi.json` | ok |
| 166 | CPC colpito più volte nel 2026 | — | sì (aprile, luglio) | `energia.md` | ok |
| 167 | Scorte di emergenza 77,2 giorni contro 90,5 un anno prima | 90,5 | 90,5 (agosto 2025) | `scorte.json` | ok |
| 168 | TransMed 220,5 TWh in 12 mesi | 220,5 | 220,5 | `gas-italia.json` | ok |
| 169 | TransMed «un solo tubo» | — | il TransMed attraversa il Canale di Sicilia con più condotte parallele: è un solo corridoio, non un solo tubo | conoscenza di dominio (Snam/TMPC) | corretto |
| 170 | TransMed: settembre 11,3, agosto 16,9, ottobre 20,2 TWh | — | identici | `gas-italia.json` (somme mensili) | ok |
| 171 | TAP 16,5%, massimo mensile a ottobre | 16,5% | 16,5%; 9,77 TWh a ottobre, massimo del periodo | `gas-italia.json` | ok |
| 172 | GNL: Adriatic 14,1%, Piombino 6,9%, OLT 6,7%, Ravenna 3,5%, Panigaglia 1,5% (circa un terzo) | — | identici (32,7% in tutto) | `gas-italia.json` | ok |
| 173 | GNL italiano 2025: USA 45,3%, Qatar 32,6%; Qatar 45% nel 2024 | — | identici; BISI: «45% … from Qatar» nel 2024 | `paesi.json`; BISI | ok |
| 174 | Adriatic LNG «da marzo riceve carichi di altra origine» | — | affermazione senza fonte; verificato solo che le consegne qatarine a Edison sono in forza maggiore | gasworld | corretto (riformulato su ciò che è documentato) |
| 175 | Stoccaggi Italia: 90% il 20/10, 91,1% il 31/10, 88,9% (180,9 TWh) l'8/11, 93,7% un anno prima | — | 90,03; 91,14; 88,93 (180,9); 93,65 | `scorte.json` | ok |
| 176 | Porti, settimana 24–30 ottobre: Ravenna −40% (petroliere −50%), Venezia Lido −38%, Trieste −13% (petroliere −24%), Genova −4%, Livorno −3%, Gioia Tauro +2%, Augusta +15% (petroliere +33%) | — | −39,8 (−50,0), −37,8, −13,1 (−23,5), −4,3, −3,0, +2,0, +14,6 (+33,3) | `portwatch.json` | ok |
| 177 | Confartigianato: 8,8 mld € di commercio estero perso «dal novembre 2023» | dal nov. 2023 | la stima (gennaio 2024) copre solo **novembre 2023–gennaio 2024** | LaPresse 25/1/2024; `stretti-dettaglio.json` | corretto |
| 178 | 6 cavi attivi Italia–Asia via Mar Rosso; 3 danneggiati nel 2024–2025; progetti nel Golfo rinviati | 6 / 3 | sì | `cavi.md` (TeleGeography) | ok |

### Scenari, agenda, metodo (sezioni 7–9)

| # | Affermazione | Valore nel report | Valore verificato | Fonte | Esito |
|---|---|---|---|---|---|
| 179 | Soglie degli scenari (Hormuz 20/10/5; Brent 85, 90–115, 118,35; TTF 70, 75–105, 103,94; WCI 4.000; Genova 5.000; Bab el-Mandeb 20; Suez 35) | — | identiche a quelle di `rischio.json`; oggi attivi 4/4 segnali di B, 0/4 di A, 1/6 di C | `rischio.json` | ok |
| 180 | «a giugno toccò 71,99» (scenario A) | 71,99 | minimo 71,57 il 1° luglio | Yahoo Finance | corretto |
| 181 | Agenda: CPI 10/11 13:30; STEO 10/11 17:00; EIA 12/11 17:00 (Veterans Day); IEA OMR 13/11 09:00; APEC 18–19/11; PIL e PCE 25/11 13:30; OPEC+ 29/11; HICP flash 1/12 10:00; Fed 8–9/12; G20 14–15/12; BCE e BoE 17/12; Consiglio europeo 17–18/12; Fed 27/1; BCE e BoE 4/2 | — | tutte presenti in `calendario.json` con le stesse date e ore | `calendario.json` | ok |
| 182 | Data dei prezzi nella tabella delle fonti | 19:38 UTC | il file è stato riscritto alle 19:47 (dato) e alle 19:56 (file) | `prezzi.json` | corretto |
| 183 | Eventi: «1–9/11/2026» | 1–9/11 | il file copre 29/10–9/11 | `eventi.json` | corretto |

**Conteggio:** 183 affermazioni verificate (molte righe raggruppano più numeri della stessa fonte) · **ok:** 135 · **corretto:** 38 · **non verificabile:** 10. Verificate solo in parte: righe 40 e 93 (dati ok, un dettaglio senza fonte primaria) e 129 (ok sul rapporto di un agente, non sul file di dati).

## 2. Logica e coerenza

1. **Confronti fra periodi diversi.** L'«In breve» accostava PortWatch della settimana 26/10–1/11 (4,4 al giorno) e LLI della settimana 19–25/10 (116 a settimana) per dire «cinque volte di più». Il rapporto 5× è corretto solo sulla stessa settimana (23 contro 116): riscritto così.
2. **Perimetri diversi.** «Poco più del 10% del GNL» (quota del GNL di Hormuz che va in Europa) e «circa il 7% del GNL arrivato in Europa» (quota del GNL europeo che passa da Hormuz) sembravano in contraddizione: esplicitato il perimetro. Stesso problema per «−66% sul 2023»: è la stessa settimana del 2023, non la media annua.
3. **Contraddizione interna sul war risk.** «Fino al 3%» e «da 250.000 a 375.000 dollari per una nave da 100 milioni» non stanno insieme (il 3% fa 3 milioni). La fonte dà una forbice 375.000–3 milioni: corretto.
4. **Le esportazioni del Golfo al 60–80% del normale** convivono con PortWatch a −95% solo se gran parte del traffico è al buio: aggiunta una valutazione esplicita che lega i due dati.
5. **TransMed «punto più critico» contro il cruscotto del rischio.** In `rischio.json` il TransMed è a livello «basso» (5,6/25), con impatto alto ma probabilità bassa. Il report ora dice «dipendenza maggiore» e cita il cruscotto; la valutazione «peggior scenario di approvvigionamento» resta, chiarendo che è il caso di impatto più alto, non il più probabile.
6. **Scenari e cruscotto.** Le soglie del capitolo 7 coincidono con quelle di `rischio.json` (scenari Hormuz): aggiunto il rimando e lo stato dei segnali al 9 novembre (B 4/4, A 0/4).
7. **Coerenza con il report sulla supply chain.** Nessuna contraddizione sui numeri condivisi (PortWatch, WCI, FBX, TTF, porti, cavi). Il report supply chain usa già il Brent a 92,62: ora i due report coincidono. Aggiunto il +124% su un anno del WCI, che mancava e cambia la lettura («i noli scendono piano» ma restano più del doppio di un anno fa).
8. **`energia.md` contro il report sulla forza maggiore qatarina.** L'agente scriveva «prorogata fino a novembre»; il report «almeno a fine dicembre». Verificato: vale la proroga a fine dicembre (Edison, fine ottobre). Il report non aveva fonte per questa frase: aggiunta.
9. **Testo e grafici.** Il grafico dei prezzi e le sue etichette usano le date di `prezzi.json` (un giorno prima del vero da marzo a ottobre); il testo ora usa le date delle sedute. La didascalia lo dichiara. Il grafico dei transiti, del gas e dell'esposizione coincidono con il testo.
10. **Valutazioni non marcate.** Marcate come tali: il legame export del Golfo/transiti al buio; «Adriatic LNG riceve carichi di altra origine» è stato tolto perché non documentato. «Una riapertura di Hormuz renderebbe inutile un rialzo» ammorbidito in «meno probabile» (era una certezza su un fatto futuro).

## 3. Grafici: perché non sono stati rigenerati

- `docs/data/prezzi.json` è stato riscritto alle 19:56, dopo la costruzione dei grafici (19:43), e ora contiene solo 66 sedute (dal 6 agosto 2026). Rilanciare `python3 report/costruisci_grafici.py` produrrebbe un grafico dei prezzi senza marzo, cioè senza i massimi di cui parla il testo.
- I file usati dagli altri tre grafici (`portwatch.json`, `gas-italia.json`, `paesi.json`) non sono cambiati dopo le 19:32: i grafici attuali sono già aggiornati.
- Quindi i grafici restano quelli delle 19:43. La didascalia del grafico dei prezzi dice con quale lettura è stato fatto e che le date nelle etichette sono anticipate di un giorno.
- **Da fare (fuori dal perimetro di questa revisione, che non tocca dati e script di raccolta):** in `raccolta/scarica_mercati.py` convertire i timestamp con il fuso della borsa (`zoneinfo.ZoneInfo(meta["exchangeTimezoneName"])`) invece di `gmtoffset`; poi riscaricare un anno di prezzi e rigenerare i grafici.

## 4. Chiarezza

- «In breve» riscritto: frasi più corte, una cifra con fonte e data per punto, sigle spiegate alla prima occorrenza (AIS, mb/g, TTF, GNL). Aggiunto un dato rilevante per il Nord Europa (stoccaggi tedeschi e olandesi). Tolta dall'«In breve» la serie dei massimi del Brent (resta nel corpo).
- Aggiunto un glossario breve («Parole utili») sotto «Come leggere», anche nella pagina HTML, che prima non aveva neppure il riquadro «Come leggere».
- Verbi neutri mantenuti; nessun tono allarmistico trovato. «Il rischio si è spostato» → «si sposta» (presente, coerente con gli altri titoli).

## 5. Elenco delle correzioni (Markdown e HTML)

1. In breve: riscritto (punti 1–5), con 92,62 $, +45,6%, confronto PortWatch/LLI sulla stessa settimana, perimetro del TransMed, fonte della proroga della forza maggiore.
2. Cifre in testa (HTML): Brent 92,62 $ provvisorio, +45,6%; TransMed «del gas importato (gasdotti e GNL)».
3. Aggiunti «Come leggere» (HTML) e glossario (MD e HTML).
4. Cronologia: guerra «di Stati Uniti e Israele contro l'Iran»; Fujairah 14/3 marcato non verificato e link riallineato al 4 maggio; massimo del Brent 31 marzo, chiusura del 19 marzo 108,65; Est-Ovest a 7 mb/g da fonte anonima; minimo 71,57 il 1° luglio; metaniera del 31 luglio vicino a Hormuz (non Mar Rosso); Brent 107,63 il 10 settembre; link The National con `www`; proroga a fine dicembre con fonte; massimi del 30 ottobre; avvisi UKMTO 191–200; Velos Sapphire 4–5 novembre; Brent 92,62 provvisorio.
5. Hormuz: perimetro del GNL verso l'Europa; tabella LLI (perimetro >10.000 t, metodo non dettagliato); CENTCOM 147 all'8/11; finestra di `eventi.json`; Est-Ovest «a pieno regime (fonte anonima)»; valutazione sull'export al 60–80%; capacità delle vie alternative (6,5–7 in tutto, 3,5–5,5 libere secondo l'IEA).
6. Mar Rosso: «stessa settimana del 2023» per Bab el-Mandeb e Suez; calo da luglio con la media di luglio (33,7); record dei ricavi «anno solare 2023».
7. Conseguenze: war risk 375.000–3 milioni; WCI +124% su un anno; Baltic Dry con fonte reale; didascalia del grafico dei prezzi; paragrafo Brent (99,6; 31 marzo; 118,03 il 29 aprile; 71,57 il 1° luglio; 30 ottobre; 92,62; WTI 86,95); TTF 30 ottobre; Henry Hub 3,21; IEA «nel caso peggiore»; urea con la Banca Mondiale come fonte; fertilizzanti −70–75%; link al comunicato BCE; Treasury un anno prima 4,11%; «meno probabile» invece di «inutile».
8. Chi è esposto: «Gas: la dipendenza maggiore»; TransMed come corridoio di più condotte; Adriatic LNG riformulato; valutazione sul TransMed con il cruscotto; Confartigianato riferita a nov. 2023–gen. 2024.
9. Scenari: minimo 71,57; rimando a `rischio.json` con lo stato dei segnali.
10. Metodo e limiti: ora del dato dei prezzi (19:47; grafico 19:38); errore di fuso orario spiegato; avviso che `prezzi.json` ora parte dal 6 agosto; Baltic Dry; finestra degli eventi; nota AI sulla revisione.
11. Aggiunto il riquadro «Revisione» in fondo (MD e HTML) e la voce nell'indice della pagina.

## 6. Cosa resta aperto

- **Non verificabile da qui:** S&P Global (transiti sauditi a Bab el-Mandeb; Jask), Kpler (import cinese), IEA Gas Security Review (−60 mld m³; sito 403), UNCTAD (403), Iraqi News (403), Fujairah 14 marzo (nessuna fonte primaria), Baltic Dry (solo rapporto dell'agente), EIA 1° semestre 2023 (pagina non riletta), annuncio iraniano del 17 aprile (The New Arab: 403).
- **Dati:** errore di fuso in `scarica_mercati.py`; `prezzi.json` accorciato al 6 agosto; il TTF storico non è stato riscaricato (date corrette per analogia con il Brent, stesso exchange su Yahoo e stessa conversione).
- **Prezzi del 9 novembre ancora provvisori:** alle 20:05 UTC Yahoo dava il Brent a 90,75 $; il valore definitivo di chiusura va riletto il 10 novembre.
- **Grafici:** non rigenerati (sezione 3).
