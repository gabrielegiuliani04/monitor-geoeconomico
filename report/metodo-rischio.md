# Metodo del cruscotto del rischio

Versione 1 · 9 novembre 2026 · script [`raccolta/rischio/calcola.py`](../raccolta/rischio/calcola.py) · risultato [`docs/data/rischio.json`](../docs/data/rischio.json) · scenari [`raccolta/rischio/scenari.json`](../raccolta/rischio/scenari.json)

## 1. L'idea in una riga

**Rischio = probabilità di disruption (1–5) × impatto (1–5)**, calcolati con regole fisse su dati pubblici già raccolti dall'osservatorio. È la classica **matrice probabilità × impatto** (ISO 31000, registri dei rischi aziendali) con tre aggiunte:
- gli **indicatori anticipatori** (*early warning*): prima del danno si muovono i flussi, gli incidenti, l'attenzione dei media e i prezzi;
- gli **scenari** a 3 mesi con segnali che dicono quale si sta avverando;
- la **catena** dell'osservatorio: *evento → passaggio o infrastruttura → flussi → noli → prezzi → chi è esposto*.

Ogni numero porta valore, soglie, stato (verde/giallo/rosso o n.d.), fonte e data. Chi legge può rifare il conto a mano.

## 2. Che cosa valutiamo (18 unità)

| Tipo | Unità |
|---|---|
| 12 passaggi strategici | Hormuz, Bab el-Mandeb, Suez, Panama, Malacca, Stretti turchi, Gibilterra, Stretti danesi, Taiwan, Capo di Buona Speranza, Canale di Sicilia, Kerch |
| 6 corridoi e infrastrutture | TransMed Algeria–Tunisia–Italia; Baltico (cavi, condotte, elettrodotti); Mar Rosso (rotta container Asia–Europa); GNL del Qatar (Ras Laffan → Hormuz); rete elettrica ucraina; catena dei chip di Taiwan |

Il punto di vista è **europeo e italiano**: l'impatto misura quanto la disruption pesa su UE e Italia (prezzi, approvvigionamento, porti), non sul paese colpito.

## 3. Otto domande, una per gruppo di indicatori

**Probabilità** (che il passaggio sia o resti disturbato nei prossimi 3 mesi)

| Domanda | Peso | Indicatori (dal repository) | Verde | Giallo | Rosso |
|---|---|---|---|---|---|
| **I flussi calano?** | 35% | Transiti PortWatch, media 7 gg, contro un riferimento (stessa settimana di un anno prima; per Hormuz la media 2025, per il Mar Rosso gen.–ott. 2023, cioè **prima della crisi**); per il gas, flusso ENTSOG 7 gg contro la media annua | ≥ −10% | −10 / −30% | < −30% |
| **Ci sono attacchi o incidenti vicino?** | 30% | Eventi negli ultimi 30 gg entro 150 km (eventi, ibrido, attacchi in Russia); incidenti a cavi e condotte in 12 mesi (300 km); flotta ombra nel Baltico; per l'Ucraina: lanci russi, ondate contro la rete, blackout | 0 eventi | 1–2 | ≥ 3 |
| **Il clima geopolitico peggiora?** | 15% | GPR di Caldara e Iacoviello del paese chiave contro la sua media 5 anni (globale se il paese manca) | ×< 1 | ×1–1,5 | ×≥ 1,5 |
| **Il mercato lo prezza?** | 20% | Prezzo collegato contro la media 90 gg (Brent, TTF, Henry Hub); premio del nolo Shanghai–Genova su Rotterdam; variazione settimanale dei noli di rotta | < +5% | +5 / +15% | > +15% |

**Impatto** (quanto fa male se succede)

| Domanda | Peso | Indicatori | Verde | Giallo | Rosso |
|---|---|---|---|---|---|
| **Quanto pesa ciò che passa?** | 35% | Giudizio 1–5 con fonte (es. Hormuz: 20 mb/g e 20% del GNL, IEA); quote misurate quando ci sono (TransMed = 34% del gas italiano, ENTSOG; GNL italiano dal Golfo = 32,6%, Comtrade) | 1–2 / < 10% | 3 / 10–25% | 4–5 / > 25% |
| **Ci sono alternative?** | 20% | Giudizio 1–5 con fonte (capacità di aggiramento, giorni in più) | 1–2 | 3 | 4–5 |
| **Quanto cuscinetto c'è?** | 25% | Scorte contro la media 5 anni: stoccaggi gas IT/DE/NL (AGSI+), scorte petrolifere di emergenza, SPR USA, grano | ≥ −5% | −5 / −15% | < −15% |
| **Quanto costa già?** | 20% | Prezzo collegato contro un anno prima | < +10% | +10 / +40% | > +40% |

**Perché queste soglie.** Verificato sulla serie PortWatch, settimane da gennaio 2024 a febbraio 2026 contro l'anno prima: nei passaggi "normali" (Malacca, Gibilterra, Taiwan, Stretti danesi, Capo) un calo oltre −10% capita nell'1–24% delle settimane (il giallo è un primo avviso, a volte rumore), un calo oltre −30% **mai**; è successo solo dove c'era una disruption vera: Panama con la siccità (12% delle settimane) e Suez con gli Houthi (46%). Quindi −30% separa il rumore dalla crisi. +5/+15% sulla media 90 giorni separa la volatilità ordinaria del greggio da uno shock. −5/−15% sulle scorte riprende il modo in cui GIE ed EIA leggono lo scarto dalla media stagionale. Le soglie dei noli e della flotta ombra sono **valutazioni** da ricalibrare quando lo storico sarà più lungo.

## 4. Come si combinano

1. Ogni indicatore vale **1 (verde), 3 (giallo), 5 (rosso)**; i giudizi strutturali valgono il loro punteggio 1–5.
2. Dentro una domanda si fa la **media**; tra le domande la **media pesata** con i pesi sopra.
3. Se un dato manca (n.d.) la sua domanda esce e i pesi si **rinormalizzano**; il campo `copertura` dice quanta parte dei pesi è coperta (sotto 0,7 il punteggio è fragile). Senza flussi né minacce la probabilità non si calcola.
4. **Regola della disruption in corso:** se i transiti o i flussi sono ≤ −50% del riferimento, o c'è un blackout o una chiusura confermati negli ultimi 7 giorni, la probabilità è 5. Non si stima la probabilità di un fatto già avvenuto.
5. **Punteggio = P × I** (1–25). Livelli: **basso** < 6 · **medio** 6–11,9 · **alto** 12–19,9 · **critico** ≥ 20 (servono entrambi gli assi almeno a 4).
6. **Tendenza:** confronto con il giorno salvato più vicino a 7 giorni fa (`raccolta/rischio/storico.json`); ±1 punto = in aumento / in calo. Il primo giorno lo storico è **ricostruito** togliendo l'ultima settimana da ogni serie; gli indicatori senza serie (eventi, noli, flotta ombra) restano uguali e sono segnati.
7. Il testo **«perché»** è generato da regole: cita gli indicatori che spingono di più e la regola applicata, non opinioni.

## 5. Come leggerlo

- **Quadrante in alto a destra (P alta, I alto):** Hormuz e GNL del Qatar. È la crisi in corso, non un rischio.
- **P alta, I medio:** Bab el-Mandeb, Mar Rosso, Stretti turchi, rete ucraina. Disruption in corso con alternative parziali.
- **P bassa, I alto:** TransMed, Canale di Sicilia, Gibilterra, chip di Taiwan. Sono i **rischi da sorvegliare**: oggi tranquilli, ma un evento li porterebbe subito a "critico". Per l'Italia il TransMed conta più di Hormuz sui volumi.
- **P media, I medio:** Baltico e Stretti danesi. Pressione ibrida costante: guardare incidenti a cavi e flotta ombra.
- La colonna **cosa osservare** dice quale soglia cambierebbe il colore domani.

## 6. Cosa il punteggio NON dice

- **Non è una probabilità statistica.** "5" significa "disruption in corso o tutti i segnali in allerta", non "100%". Le soglie sono scelte, non stimate su serie storiche.
- **Non vede ciò che non è nei dati.** PortWatch conta solo le navi con l'AIS acceso (a Hormuz Lloyd's List conta circa cinque volte più transiti); i file degli eventi coprono finestre recenti; Kerch a zero può essere un effetto dell'AIS spento nelle acque russe.
- **I giudizi strutturali sono valutazioni** dell'osservatorio con fonte, cambiano di rado e pesano molto sull'impatto.
- **Le unità non sono indipendenti:** Hormuz e GNL del Qatar condividono gli stessi transiti; Brent e TTF compaiono in molte unità. Non si sommano i punteggi.
- **Non dice quando né quanto** in euro: per questo ci sono gli scenari, che restano valutazioni.
- **Prezzi non ufficiali** (future da Yahoo Finance, 3 mesi di serie pubblicata); GPR misura l'attenzione dei giornali, non il danno.

## 7. Scenari a 3 mesi

Per Hormuz, Mar Rosso, Baltico e TransMed tre scenari (base, peggiorativo, migliorativo) con innesco, effetti lungo la catena e **segnali misurabili** (es. "Hormuz sopra 20 navi al giorno", "Mazara sotto 420 GWh/g"). Lo script li legge ogni giorno e scrive in `rischio.json` quanti segnali di ciascuno scenario sono veri: è una **lettura**, non una previsione. File: [`raccolta/rischio/scenari.json`](../raccolta/rischio/scenari.json).

## 8. Fonti

IMF PortWatch; ENTSOG (Snam); GIE AGSI+, EIA, Eurostat, USDA (scorte); Caldara e Iacoviello (GPR); Yahoo Finance (prezzi); Drewry, Freightos, SSE (noli); UKMTO, agenzie e OSINT (eventi); TeleGeography e stampa (cavi); Aeronautica ucraina (lanci); UN Comtrade (quote). Giudizi strutturali da IEA, EIA, UNCTAD, Rhodium Group e dalle schede di `stretti-dettaglio.json`. Pratiche di riferimento: ISO 31000 (matrice probabilità × impatto), sistemi di *early warning* per le catene di fornitura, pianificazione per scenari.
