# Assicurazioni marittime e rischio guerra: rapporto dell'agente (9 novembre 2026)

**Tema per il colloquio: come il rischio diventa costo.**

File prodotto: `docs/data/assicurazioni.json` (103 KB). Contiene:
- 27 aree elencate dal Joint War Committee (JWC);
- 49 punti di premio, di cui 5 «non pubblico»;
- 6 esempi di costo calcolati dallo script;
- 25 eventi assicurativi;
- 11 circolari;
- 10 schede «come funziona».

Lo script è `raccolta/assicurazioni/raccogli.py` (solo libreria standard). Le voci curate stanno in `raccolta/assicurazioni/*.json`. Ultimo giro: 0 errori, 0 avvisi. Il controllo JWC online ha dato «nessun cambiamento».

**Fatto** = dato con fonte e data. **Valutazione** = ragionamento dell'osservatorio.

---

## 1. Come funziona, in breve

- **Corpo e macchine (H&M).** Assicura la nave stessa. La polizza ordinaria **esclude la guerra**: mine, missili, terrorismo, sequestro e confisca.
- **P&I.** Copre le responsabilità verso terzi: equipaggio, carico, inquinamento, relitto, collisioni.
  - I **12 club dell'International Group** sono mutue e coprono circa l'**87%** della stazza oceanica mondiale.
  - Ogni club tiene i sinistri fino a **10 milioni di $**; oltre quella soglia li dividono in un pool comune riassicurato ([IG P&I](https://www.igpandi.org/about/)).
  - Porti e convenzioni chiedono un certificato P&I valido.
- **Rischio guerra (war risk).** È una copertura separata: scafo-guerra e P&I-guerra. Si compra soprattutto a Londra, presso i sindacati dei Lloyd's e le compagnie IUA.
  - La polizza annuale vale ovunque **tranne le aree elencate**.
  - Ha una clausola di disdetta con preavviso breve: 72 ore per le coperture dei club.
  - Il 1° marzo 2026 Gard ha notificato la disdetta per l'Iran e il Golfo, in vigore dal 5 marzo, con ripristino a nuove condizioni ([Gard 01/2026](https://gard.no/en/circulars/notice-of-cancellation-for-war-risks/)).
  - Entro il 5 marzo, 7 club su 12 avevano mandato avvisi simili.
  - La disdetta toccava le coperture non mutualistiche. La copertura mutualistica P&I e l'Excess War Risks restavano.
- **Joint War Committee e Listed Areas.** Il JWC riunisce sottoscrittori dei Lloyd's e delle compagnie IUA.
  - Con il consulente Herminius pubblica le circolari JWLA-0xx, cioè l'elenco delle aree «a rischio accresciuto».
  - **Il JWC non fissa i prezzi**: chi entra in un'area elencata deve avvisare l'assicuratore e paga un premio negoziato ([LMA, Listed areas](https://lmalloyds.com/specialist-areas/underwriting/listed-areas/)).
- **Premio aggiuntivo (AP).** È una percentuale del valore dello scafo per una copertura di 7 giorni o per un transito. Il mercato lo rivede ogni 24–48 ore.
  - **Costo = valore della nave × tasso.**
  - Le navi legate a USA, Regno Unito, Israele e, dal luglio 2026, all'Arabia Saudita pagano di più.
- **Violazione della garanzia (breach of warranty).** Se la nave entra in un'area elencata senza avvisare, la copertura di guerra può non rispondere (clausola JW2005/001A).
  - Per Iran, Siria, Russia e Venezuela serve un accordo preventivo ([Swedish Club, 13 agosto 2026](https://www.swedishclub.com/uploads/2026/07/Listed-Areas-as-per-13-August-2026.pdf)).
- **K&R e perdita di nolo.** Il K&R (sequestro e riscatto) serve per la pirateria: Golfo di Guinea, Somalia.
  - Contro una detenzione da parte di uno Stato o di una milizia serve la copertura di guerra per «detenzione e blocco». Esempio: la Galaxy Leader, equipaggio trattenuto dagli Houthi da novembre 2023 a gennaio 2025.
  - Howden Re stima l'esposizione per perdita di nolo nel Golfo a circa **200 milioni di $ al giorno**: 1.000 navi × 200.000 $.
- **Sanzioni e tetto al prezzo.** Assicuratori e club occidentali possono coprire greggio russo solo se venduto sotto il tetto, che si dimostra con attestazioni lungo la catena commerciale.
  - Il tetto è di **44,10 $/barile** dal 1° febbraio 2026 ([Commissione UE](https://finance.ec.europa.eu/news/new-dynamic-mechanism-lower-price-cap-russian-crude-oil-4410-barrel-2026-01-15_en)).
  - Il 23 luglio 2026 l'UE lo ha congelato per 12 mesi ([Moscow Times](https://www.themoscowtimes.com/2026/07/23/eu-agrees-21st-sanctions-package-against-russia-a93317)).
  - Per Hormuz l'OFAC vieta i «pedaggi» all'Iran (FAQ 1249). Il 27 maggio ha sanzionato la Persian Gulf Strait Authority ([pagina JWC dell'LMA](https://lmalloyds.com/committee/joint-war-committee/)).
- **Flotta ombra.** Petroliere vecchie, proprietà opache, assicuratori russi o sconosciuti fuori dall'International Group. Il rischio ricade sugli **Stati costieri**: chi paga un versamento di petrolio o la rimozione di un relitto?
  - Nel marzo 2024 l'Andromeda Star, dopo una collisione al largo della Danimarca, mostrò una polizza Gard non valida ([gCaptain/Bloomberg](https://gcaptain.com/shadow-fleet-oil-tanker-that-crashed-had-void-western-insurance)).
  - Dal febbraio 2025 la Danimarca ispeziona le petroliere ancorate a Skagen ([Insurance Journal](https://www.insurancejournal.com/news/international/2025/02/06/810919.htm)). Non può però fermare il transito, protetto dal trattato del 1857.
  - Circa una nave su tre del traffico russo negli stretti danesi ha un'assicurazione sconosciuta (gCaptain, in `stretti-dettaglio.json`).

## 2. Le aree elencate oggi (JWLA-035, 16 settembre 2026)

Letta dal PDF pubblico. La pagina LMA dice: «the committee last reviewed the areas in September 2026».

- **Acque definite:**
  - Golfo, Golfo di Oman, Oceano Indiano, Golfo di Aden e **Mar Rosso a sud di 25,5°N**, escluse le acque egiziane;
  - **tutto il Mar Nero** (escluse le acque territoriali di Turchia, Bulgaria, Romania e Georgia), più l'Azov e le acque interne di Ucraina, Russia e Bielorussia;
  - Golfo di Guinea;
  - Cabo Delgado.
- **Paesi:** Benin, Gibuti, Eritrea, Libia, Nigeria, Somalia, Sudan, Togo; Bahrein, Iran, Iraq, Israele, Kuwait, Libano, Oman, Qatar, Arabia Saudita, Siria, Emirati, Yemen; **Russia** (tutti i porti, anche quelli del Baltico); Guyana (solo offshore); Venezuela.
- **Le ultime tre circolari:**

| Circolare | Data | Cosa cambia |
|---|---|---|
| JWLA-033 | 3 marzo 2026 | Aggiunge Bahrein, Gibuti, Kuwait, Oman e Qatar, «i paesi con basi USA» |
| JWLA-034 | 29 luglio 2026 | Mette in lista tutta l'Arabia Saudita e sposta il limite nel Mar Rosso da 18°N a 25,5°N. **Yanbu, lo sbocco dell'oleodotto che aggira Hormuz, entra in area.** Toglie il Pakistan |
| JWLA-035 | 16 settembre 2026 | Mette in lista tutto il Mar Nero: una nave per Odessa entra in area appena uscita dal Bosforo |

## 3. Numeri con fonte e data

Sono **quotazioni di mercato riportate dalla stampa**, non un indice. I premi effettivi sono privati.

| Area | Prima | Picco | Ultimo dato pubblico |
|---|---|---|---|
| **Hormuz/Golfo** | 0,15–0,25% (Marsh) | ~5% il 19/3 (CEO dei Lloyd's); 7,5–10% il 22/7 (Marsh su S&P) | **6–10%** inizio ottobre (broker al FT, [Insurance Business 14/10](https://www.insurancebusinessmag.com/ca/news/marine/hormuz-sinking-hands-marine-war-underwriters-another-total-loss-as-attacks-surge-593542.aspx)); 6–9% il 24/9 ([Reuters/IJ](https://www.insurancejournal.com/news/international/2026/09/25/886769.htm)) |
| **Mar Rosso/Bab el-Mandeb** | meno dello 0,1% (Moody's, fine 2023) | 1% il 16/1/2024; 2% a settembre 2024; oltre l'1% il 23/7/2026 | **0,2–0,3%** per le navi senza legami sauditi (24/9/2026) |
| **Yanbu e porti sauditi del Mar Rosso** | 0,1% (luglio 2026) | 7% a sud di Yanbu | **3%** per le petroliere saudite a Yanbu (24/9/2026) |
| **Mar Nero** | «quasi zero» (inizio 2022) | fino al 10% (aprile 2022); **20%** per alcune navi al terminale CPC (novembre 2026, picco) | circa 1% (23/9/2026, Beinsure); 0,8–1% per i porti ucraini (Platts, dicembre 2025) |
| **Israele** | 0,2% (giugno 2025) | oltre il 2% (novembre 2023) | 0,7–1% (17/6/2025). **Nessuna percentuale pubblica per il 2026** |

Altri fatti sul Mar Nero e sull'Ucraina:
- I tassi sul carico a Odessa sono scesi dal 4–5% del 2022 allo 0,35–0,4% (aprile 2025, [GMK Center](https://gmk.center/en/opinion/insurance-rates-in-the-ports-of-greater-odessa-decreased-to-0-35-0-4/)).
- Lo schema ucraino **Unity** (Marsh, Lloyd's, governo ucraino) è nato a novembre 2023, con 50 milioni di $ per viaggio, ed è stato esteso a tutte le merci il 1° marzo 2024.

**Dove il dato non è pubblico.** Dopo metà ottobre non ho trovato quotazioni pubbliche per Hormuz, dopo il 24 settembre nessuna per il Mar Rosso, e nessuna per Israele nel 2026. Nel file sono voci «non_pubblico» con la spiegazione.

## 4. Esempio passo passo: Hormuz (VLCC, ottobre 2026)

Calcolato dallo script dagli ingressi con fonte (esempio `hormuz-vlcc-ottobre-2026`).

1. **Valore della nave:** 100 milioni di $. Reuters (settembre 2026): il prezzo medio delle petroliere vecchie è salito sopra i 100 milioni.
2. **Tasso:** 6–10% del valore per transito (broker al FT, ottobre). Prima della guerra era lo 0,25% (Marsh).
3. **Premio:**
   - 100 × 6% = **6 milioni di $**;
   - 100 × 10% = **10 milioni di $**;
   - prima della guerra 0,25 milioni, cioè **×40**;
   - su una nave da 150 milioni, al 10%: **15 milioni**.
4. **Per barile:** la nave porta circa 2 milioni di barili, quindi **3–5 $/barile**. Al Brent di oggi (92,62 $, `prezzi.json`) il premio massimo vale il **5,4%** del prezzo del carico.
5. **Il nolo pesa di più:**
   - il 22 luglio il nolo Golfo–Cina era di 77,96 $/t × 270.000 t = **21,05 milioni** (circa 10,5 $/barile);
   - la media di cinque anni è 18,91 $/t, cioè 5,11 milioni (S&P Global via [Al Jazeera](https://www.aljazeera.com/economy/2026/7/23/how-shipping-insurance-rates-are-rising-as-hormuz-bab-al-mandeb-shut-down)).
   - Assicurazione e nolo **insieme** aggiungono oltre 20 milioni di $ a viaggio rispetto al prebellico. Il nolo è di luglio: non ho trovato un dato pubblico più recente.
6. **L'alternativa** non è un'altra rotta ma l'oleodotto saudita verso Yanbu. Nel settembre 2026 una petroliera saudita a Yanbu pagava il **3% = 3 milioni**, contro 6–9 milioni a Hormuz: si risparmiano **3–6 milioni a viaggio**.
   - Il premio di Yanbu vale comunque **6 giorni di nolo** (a 0,5 milioni di $ al giorno).
   - Una petroliera senza legami sauditi nello stesso mare paga lo 0,25%, circa 0,25 milioni.
   - *Valutazione:* conta chi sei, non solo dove sei.

## 5. Esempio passo passo: Mar Rosso (grande portacontainer) contro il Capo

Esempio `mar-rosso-portacontainer-contro-capo`.

1. **Valore della nave:** 221,7 milioni di $, il prezzo indicativo di una 15.500 TEU nuova ordinata da CMA CGM ad agosto 2026. È un massimo: una nave in esercizio vale meno.
2. **Gennaio 2024, tasso dell'1%:**
   - premio **2,22 milioni** a transito;
   - a settembre 2024, al 2%: **4,43 milioni**.
3. **Costo del giro dal Capo (UNCTAD 2024):** circa **0,7 milioni di $ in più** a viaggio (1,0 via Suez contro 1,7 via Capo) e **14–24 giorni** in più. È riferito a una nave di taglia media: per una nave grande il costo in più è maggiore (LSEG: +35%).
4. **Soglia di convenienza** = costo del Capo / valore della nave:
   - 0,7 / 221,7 = **0,32%** per la nave nuova;
   - **0,7%** per una nave da 100 milioni.
   - Sopra la soglia il Capo conviene, contando solo i costi diretti.
5. **Gennaio 2024:** con l'1% si era sopra la soglia, e il Capo conveniva.
   - Per posto container: 2,22 milioni / 15.500 = **143 $/TEU**, circa **il 7% del nolo Shanghai–Genova di oggi** (WCI 4.166 $/FEU, `noli.json`).
6. **Settembre 2026, tasso dello 0,2–0,3%:**
   - premio 0,44–0,67 milioni, cioè **29–43 $/TEU**;
   - è sotto o vicino alla soglia. *Valutazione:* è coerente con il ritorno delle linee a Suez (63% della capacità Asia–Europa secondo Alphaliner, in `stretti.md`).

*Valutazione:* il premio non spiega da solo la fuga del 2024. Contano anche la sicurezza degli equipaggi, il rifiuto dei marittimi e la regolarità del servizio. Però **fissa il prezzo del rientro**.

## 6. Cosa guardare: indicatori anticipatori

1. **Le circolari JWC.** Lo script controlla ogni giorno la pagina LMA e l'elenco IUA. Una nuova JWLA o un'estensione del perimetro precede di giorni i premi e i noli. JWLA-034 su Yanbu è arrivata 9 giorni dopo l'embargo houthi.
2. **Le disdette dei club** (preavviso di 72 ore) e i comunicati di Gard, Skuld, NorthStandard e UK P&I: segnalano che i riassicuratori ritirano capacità.
3. **Il premio di Hormuz o del Mar Rosso nella stampa di mercato** (Reuters/The Insurer, Insurance Journal, Lloyd's List, Insurance Business). Conta la **direzione nell'arco di 48 ore**.
4. **Gli attacchi UKMTO e gli eventi a navi** (`eventi.json`): 13 attacchi a navi entro 300 km da Hormuz negli ultimi 30 giorni, 1 entro 350 km da Bab el-Mandeb, 4 nel Mar Nero.
5. **I sovrapprezzi di guerra dei vettori:** Hapag-Lloyd 1.500 $/TEU sul Golfo (Howden Re, marzo); ZIM 100 $/TEU su Israele dal 12 marzo 2026 (estratto, affidabilità bassa).
6. **Gli schemi pubblici:**
   - DFC-Chubb da 20 miliardi di $ (11 marzo 2026), poi 40;
   - pool indiano (maggio 2026);
   - pool saudita (15 settembre 2026).
   - Un nuovo schema dice che il mercato da solo non regge.
7. **Le perdite totali.** La GFS Pride, affondata il 13 ottobre a Hormuz, è un sinistro da pagare. Howden Re stima 2–3 miliardi di sinistri contro 1,5–2 miliardi di premi annui del ramo: è segno di un **rincaro strutturale** al rinnovo.

## 7. Effetti su porti e catene

- **Scali evitati.** Con la lista estesa a Kuwait, Qatar, Bahrein e Oman (JWLA-033) ogni scalo nel Golfo paga il premio, oltre al transito di Hormuz. A marzo erano ferme nel Golfo circa **1.000 navi**, per 25 miliardi di $ di scafi (LMA, [gCaptain](https://gcaptain.com/insurers-say-war-cover-still-available-for-gulf-voyages-as-shipping-crisis-deepens/)).
- **Spostamento dei carichi.** Dal Golfo il greggio passa a Yanbu e Fujairah, che sono a loro volta in lista. Il Mar Rosso saudita è diventato un'area cara.
- **Transhipment e Mediterraneo.** *Valutazione:* nel 2024 il giro dal Capo ha favorito i porti atlantici e Tanger Med rispetto a Gioia Tauro, Genova e Trieste (`stretti.md`). Il rientro a Suez, reso possibile da premi allo 0,2–0,3%, inverte la spinta.
  - PortWatch (`flussi.md`, ultima settimana di ottobre): Gioia Tauro +2%, Genova −4% sull'anno; Trieste −13% e Ravenna −40%, porti energetici esposti a Hormuz.
- **Mar Nero.** Con JWLA-035 il costo in più arriva anche alle rotte per Costanza e Varna. Per Odessa sono circa **150.000 $ a viaggio**, cioè 2–3 $/t di carico ([Beinsure](https://beinsure.com/black-sea-war-risk-expansion-raises-shipping-insurance-costs/)). Il Bosforo è a **−55%** sull'anno (PortWatch).
- **Flotta ombra e Stati costieri.** Le petroliere senza copertura dell'International Group non pagano premi di guerra occidentali, ma scaricano il rischio di versamento sugli Stati costieri: Danimarca, Baltico, Turchia.

## 8. Rischio percepito e misurato: premi contro transiti PortWatch

| Area | Ultimo premio pubblico | Transiti (PortWatch, 7 giorni al 1/11) | Attacchi a navi in 30 giorni |
|---|---|---|---|
| Hormuz | 6–10% (inizio ottobre) | 4,4 navi al giorno, **−95%** sull'anno | 13 |
| Bab el-Mandeb | 0,2–0,3% (24/9) | 27,3 navi al giorno, −22% sull'anno, **−66%** sul 2023 | 1 |
| Mar Nero (Bosforo) | circa 1% (23/9); picchi del 20% | 44,4 navi al giorno, **−55%** | 4 |

Cosa si legge (*valutazione*):
- **I premi misurano la paura del mercato** a Londra. **I transiti misurano chi passa davvero**, ma solo con l'AIS acceso.
- **Hormuz.** Dopo il memorandum di giugno il premio è sceso a circa il 2% e i transiti sono saliti a 12,9 al giorno di media. A luglio il premio è risalito al 7,5–10% e i transiti sono tornati a 4,7 ad agosto.
  - Qui premio e traffico vanno insieme. In più, a marzo oltre metà delle navi in transito erano navi ombra, alcune «dark» (LMA/Lloyd's List via [Enterprise](https://enterpriseam.com/logistics/2026/03/17/war-risk-premiums-up-tenfold-for-vessels-transiting-hormuz/)), e non comprano copertura a Londra.
  - Windward stima che **circa una nave su 50** in transito sia stata colpita nel 3° trimestre. Un premio del 6–10% prezza quindi più della frequenza osservata: incertezza, mine, poche navi su cui spalmare il rischio, capacità scarsa.
- **Bab el-Mandeb.** Il premio è basso (0,2–0,3%) ma il traffico è ancora −66% rispetto al 2023. Il rischio misurato in premi è sceso prima della fiducia degli armatori.
  - Inoltre il premio medio nasconde la segmentazione: 3–7% per le navi saudite. Dopo l'embargo di luglio i transiti sono passati da 36,6 al giorno a giugno a 27,4 ad agosto.
- **Mar Nero.** Il premio di massa è intorno all'1%, ma il Bosforo perde più della metà del traffico. Qui conta il rischio fisico (droni navali, porti colpiti) più del prezzo.
  - Il picco del 20% è un premio che equivale a un rifiuto di quotare.

## 9. Fonti provate

| Fonte | Esito | Licenza / note |
|---|---|---|
| LMA, pagine «Listed areas» e «Joint War Committee», PDF delle circolari JWLA-033, 034, 035 | funziona (curl/urllib) | documenti pubblici; citazione |
| IUA, Joint War Committee Risk List | funziona; dà l'elenco con date | pagina pubblica |
| Swedish Club, liste al 13 marzo e al 13 agosto 2026 (PDF) | funziona | documenti pubblici |
| Howden Re, rapporto del 27 marzo 2026 (PDF) | funziona | citazione |
| Insurance Journal (testi Reuters), Insurance Business, Al Jazeera, gCaptain, Maritime Executive, Hellenic/Cyprus Shipping News, Beinsure, Reinsurance News, Gard, IG P&I, Commissione UE | funzionano | citazione con link; testi non ripubblicati |
| S&P Global, Lloyd's List, FT, Bloomberg, Reuters, Splash247, Seatrade, Business Insurance, ZIM | **403/401 o DNS** da questo ambiente | ripresi tramite altre testate; Lloyd's List e FT sono a pagamento |
| Pagina «Herminius Quarterly Briefings» | solo per membri LMA | non usata |

Nessuna fonte richiede chiavi.

## 10. Fatti attuali (sintesi)

1. È in vigore **JWLA-035** del 16 settembre 2026: tutto il Mar Nero in lista. L'ultima revisione è di settembre 2026 (LMA, controllo del 9 novembre: nessun cambiamento).
2. **Hormuz:** premi al 6–10% del valore dello scafo all'inizio di ottobre, contro lo 0,25% prebellico. Per una VLCC da 100 milioni sono 6–10 milioni di $ a transito.
3. **Yanbu:** 3% per le petroliere saudite (24 settembre), contro meno dell'1% a inizio luglio. A sud di Yanbu fino al 7%.
4. **Mar Rosso** senza legami sauditi: 0,2–0,3% (24 settembre); oltre l'1% il 23 luglio dopo l'embargo houthi.
5. **Mar Nero:** circa 1% a settembre; picchi del 20% per alcune navi al terminale CPC (9 novembre).
6. **GFS Pride** affondata il 13 ottobre a Hormuz: seconda nave affondata dall'inizio della guerra. IMO: 106 incidenti e 24 marittimi morti.
7. **Howden Re:** sinistri da guerra stimati in 2–3 miliardi di $, contro 1,5–2 miliardi di premi annui mondiali del ramo.
8. **Tetto UE** al greggio russo a 44,10 $, congelato per 12 mesi dal 23 luglio 2026.
9. **Pool saudita** per i rischi di guerra approvato il 15 settembre 2026. DFC-Chubb da 20 miliardi di $ dall'11 marzo.

## 11. Collegamenti e proposta per la mappa

- **Collegamenti:**
  - ogni area elencata porta i **transiti PortWatch** (serie mensile di 24 mesi) e gli **attacchi a navi** degli ultimi 30 giorni;
  - gli esempi leggono **Brent** (`prezzi.json`) e **WCI Shanghai–Genova** (`noli.json`);
  - le chiavi dei passaggi sono quelle di `portwatch.json`.
- **Livello «Aree di rischio guerra (JWC)»:**
  - poligoni semitrasparenti per le acque definite, colorati per data dell'ultima modifica (2026 in rosso);
  - punti per i paesi;
  - nel riquadro: circolare, data di inserimento, ultimo premio con forchetta e data.
- **Pannello «Il rischio diventa costo»:**
  - grafico a gradini delle serie dei premi (Hormuz, Mar Rosso, Mar Nero, Israele) sovrapposto ai transiti PortWatch mensili;
  - sotto, l'esempio di calcolo con i passi in chiaro.
- **Banner:** un avviso se `controllo_jwc.stato` = «cambiamenti da verificare».

## 12. Limiti

- I premi sono **quotazioni riportate dalla stampa**, spesso di seconda mano (Reuters via Insurance Journal, FT via Insurance Business). Non sono un indice; i premi effettivi sono privati e scontati.
- La serie usa il **valore centrale** della forchetta, che nasconde la dispersione: per Hormuz a marzo si andava dall'1% al 10%.
- Mancano dati pubblici recenti: Hormuz dopo metà ottobre, Mar Rosso dopo il 24 settembre, Israele per il 2026.
- **Poligoni indicativi:** vertici al largo dalla circolare, coste semplificate a mano. Per il Mar Nero non sono ritagliate le acque territoriali escluse.
- Le date di inserimento delle aree precedenti a JWLA-032 non sono verificate sul testo.
- **Esempi di costo:**
  - il valore della nave è scelto (100 milioni, oppure il prezzo a nuovo per la portacontainer);
  - il costo del Capo viene da UNCTAD 2024 ed è riferito a una nave di taglia media;
  - il nolo TD3C è di luglio.
  - Sono ordini di grandezza, non preventivi.
- PortWatch vede solo l'AIS. Le navi ombra e «dark», numerose a Hormuz, non entrano né nei transiti né nel mercato assicurativo di Londra.
