# Stretti e passaggi strategici: rapporto dell'agente (9 novembre 2026)

File prodotto: `docs/data/stretti-dettaglio.json` (13 schede, 222 voci con fonte, 100 fonti).
Script: `raccolta/stretti/raccogli.py` (solo libreria standard). Non modifica `stretti.json`: ne riusa le chiavi in `chiavi_stretti`.

In questo testo **fatto** vuol dire un dato con fonte e data. **Valutazione** vuol dire un ragionamento dell'osservatorio sulle fonti citate. Anni diversi non si confrontano.

---

## 1. Il quadro in una pagina

Nel 2026 due passaggi si sono chiusi o ristretti insieme, e il secondo dipende dal primo.

- **Hormuz è chiuso di fatto dal 2 marzo 2026.** IMF PortWatch conta 1 transito il 1° novembre, contro una media prebellica di 85 al giorno ([Straits su PortWatch](https://straits.live/briefs/2026-11-09)). Prima della guerra ci passavano 19,9 mb/g di petrolio, circa il 25% del petrolio via mare, e il 20% del GNL mondiale ([IEA, febbraio 2026](https://iea.blob.core.windows.net/assets/c8248eba-8689-46d9-ae4b-b858b59c0f1c/StraitofHormuz2026-Factsheet.pdf)).
- **Bab el-Mandeb è diventato il «secondo Hormuz».** L'Arabia Saudita porta il greggio a Yanbu, sul Mar Rosso, con l'oleodotto Est-Ovest. Da lì il greggio per l'Asia deve uscire da Bab el-Mandeb: 8,1 mb/g nel 2° trimestre 2026, contro 5,4 alla fine del 2025 ([EIA STEO, agosto 2026](https://www.rigzone.com/news/how_much_oil_transited_through_worlds_chokepoints_in_2q-12-aug-2026-184358-article/)). A luglio gli Houthi hanno dichiarato chiuso lo stretto alle navi legate all'Arabia Saudita ([AP](https://wtop.com/world/2026/07/a-new-threat-by-yemens-houthis-could-widen-the-iran-war-and-put-another-trade-chokepoint-at-risk/)). Valutazione: un attacco riuscito qui chiuderebbe l'ultima uscita di massa del greggio del Golfo.
- **Suez, al contrario, si riapre.** A ottobre 2026 sono passate 1.490 navi, il mese più trafficato dall'ottobre 2023 ([EgyptToday, dati SCA](https://www.egypttoday.com/Article/1/150437/Suez-Canal-records-highest-monthly-vessel-traffic-since-Red-Sea)). La capacità container è tornata sopra il 50% del livello pre-crisi ([BIMCO](https://www.bimco.org/news-insights/market-analysis/shipping-number-of-the-week/2026/1014-snow/)). UKMTO non segnala attacchi nel Mar Rosso dal 24 agosto ([Lloyd's List Intelligence](https://www.lloydslistintelligence.com/resources/blog/red-sea-brief---29-october-2026)).

Per l'Italia l'esposizione diretta sul greggio di Hormuz è bassa: il primo fornitore che passa da Hormuz, l'Iraq, è all'8° posto ([Auto.it](https://www.auto.it/news/attualita/caro-benzina-costi-carburante/2026/04/13-8732583/quanto_petrolio_italiano_passa_da_hormuz_)). L'esposizione è alta su tre fronti:
- **il gas:** il Qatar dava il 45% del GNL italiano nel 2024 ([BISI](https://bisi.org.uk/reports/how-do-disruptions-in-the-hormuz-strait-affect-europe-a-spotlight-on-italy));
- **i prezzi:** Brent e TTF si formano sul mercato mondiale;
- **le rotte container di Suez.**

Il passaggio più critico per l'Italia resta quello di casa, il **Canale di Sicilia**. Dal TransMed algerino entra il 34% del gas italiano degli ultimi 12 mesi (`gas-italia.json`, dati ENTSOG).

---

## 2. Tabella riassuntiva

| Passaggio | Cosa passa | Chi è esposto | Quali prezzi si muovono |
|---|---|---|---|
| **Hormuz** | 19,9 mb/g di petrolio (2025), 112 bcm di GNL (≈20% del mondo), 25–43% dell'urea, GPL per l'India | Cina, India, Giappone, Corea (69% del greggio nel 2024); Bangladesh, India, Pakistan per il GNL; Italia sul GNL qatarino e sui prezzi | Brent, TTF, JKM, noli VLCC (TD3C), war risk, urea, ammoniaca, zolfo |
| **Bab el-Mandeb** | 8,1 mb/g nel 2° trim. 2026 (greggio saudita da Yanbu), container Asia–Europa, auto cinesi | Raffinatori asiatici; Italia e porti mediterranei per i container | Brent, noli tanker, Drewry WCI |
| **Suez** | 4,9–5,8 mb/g; 12–15% del commercio mondiale (2023); GNL in calo (140 metaniere nel 2025) | Italia e Mediterraneo; Nord Europa | noli Shanghai–Genova/Rotterdam, Brent |
| **Panama** | 5% del commercio, 40% dei container USA, 29% della soia USA, GNL e GPL USA–Asia | USA, Asia orientale | noli VLGC e portarinfuse, soia e mais USA, Henry Hub–JKM |
| **Malacca** | 23,2 mb/g nel 1° sem. 2025, 16,6 nel 2° trim. 2026; 17% delle metaniere; con Taiwan metà del commercio via mare | Cina, Giappone, Corea | noli VLCC, Dubai/Brent |
| **Stretti turchi** | 3,7–4,1 mb/g (CPC kazako, Urals); Russia+Ucraina = 27% dell'export di grano | Italia (greggio CPC); Nord Africa e Medio Oriente (grano) | grano, differenziale CPC, noli Suezmax/Aframax |
| **Gibilterra** | circa 130 navi al giorno (stima); ingresso della rotta del Capo | Italia (GNL USA, container) | noli container Mediterraneo |
| **Stretti danesi** | 4,5–4,9 mb/g, circa un terzo del petrolio russo via mare | India, Turchia, Cina (acquirenti); UE (rischio ambientale) | Brent, sconto Urals, diesel |
| **Taiwan** | oltre 1/5 del commercio marittimo; 48% delle portacontainer (2022); chip | tutto il mondo, Europa via chip | semiconduttori, noli Asia, GNL spot |
| **Capo di Buona Speranza** | 9,4 mb/g nel 2° trim. 2026; minerale di ferro brasiliano (≈24% del mondo) | Asia ed Europa (rotte più lunghe) | noli tanker e container (tonnellate-miglio) |
| **Canale di Sicilia** | TransMed: 34% del gas che entra in Italia; Greenstream: 0,8% | Italia | PSV, TTF |
| **Kerch** | fino al 25% del grano e olio di girasole russi | Nord Africa e Medio Oriente | grano |
| **Lombok e Sonda** | VLCC troppo pesanti per Malacca; greggio iraniano verso la Cina | Cina | noli VLCC (marginale) |

---

## 3. Hormuz: cosa passa, chi perde, quanto costa

**Cosa passa (2025, IEA su Kpler).** Il totale è 14,95 mb/g di greggio, quasi il 34% del greggio commerciato nel mondo, più 4,93 mb/g di prodotti. Per origine:
- Arabia Saudita 6,23 mb/g;
- Iraq 3,63;
- Emirati 3,24;
- Iran 2,41;
- Kuwait 2,37;
- Qatar 1,43.

Il GNL vale poco più di 112 bcm, quasi il 20% del commercio mondiale. Passano dallo stretto il 93% del GNL del Qatar e il 96% di quello degli Emirati.

Sui fertilizzanti le stime non concordano:
- un quarto dell'export mondiale di urea per la [Banca Mondiale](https://blogs.worldbank.org/en/opendata/fertilizer-prices-surge-as-strait-of-hormuz-disruptions-tighten-);
- il 43% dell'export via mare per la North Dakota State University;
- il 50% per Howden Re.

**Per dove.**
- Circa l'80% del petrolio va in Asia.
- Cina e India ricevono il 44% del greggio (IEA, 2025). Con Giappone e Corea arrivano al 69% (EIA, 2024).
- In Europa va solo il 4% del greggio, circa 600.000 b/g.
- Il GNL va per il 90% in Asia e per poco più del 10% in Europa. Per l'Asia è il 27% del GNL importato, per l'Europa circa il 7%.
- Bangladesh, India e Pakistan ricevevano da Hormuz quasi due terzi del loro GNL.

**Alternative e loro limite.** Le capacità degli oleodotti, secondo IEA e Baker Institute:

| Oleodotto | Capacità | Note |
|---|---|---|
| Est-Ovest saudita | 5 mb/g di progetto, 7 dichiarati da Aramco | A fine marzo 2026 era al massimo ([Fortune](https://fortune.com/2026/03/28/saudi-arabia-east-west-oil-pipeline-strait-hormuz-bypass-7-million-barrels-yanbu-red-sea/)). Il limite vero è il porto di Yanbu: circa 5 mb/g di greggio esportabile ([Baker Institute](https://www.bakerinstitute.org/sites/default/files/2026-04/20260408-Krane%20Alexander-Losing%20Hormuz-Working%20Paper.pdf)) |
| ADCOP Habshan–Fujairah | 1,5–1,8 mb/g | Circa 0,7 liberi prima della guerra. Fujairah è stata colpita più volte |
| Goreh–Jask iraniano | 1 mb/g | Di fatto fermo |
| Kirkuk–Ceyhan | — | Riaperto il 17 marzo 2026, ma circa 130.000 b/g ad agosto ([Shafaq](https://shafaq.com/en/Economy/Kirkuk-Ceyhan-oil-exports-fall-to-around-130-000-bpd)) |

Il GNL non ha alternative. *Valutazione:* in tutto si aggirano 5,5–7 mb/g su quasi 20. Il resto, cioè Iraq del sud, Kuwait, Qatar e quasi tutti i prodotti, resta senza uscita.

**Prezzi (Howden Re, 27 marzo 2026).**
- Brent: picco a 119 $ il 19 marzo, da 71 prima della guerra.
- War risk: da 0,25% a fino al 3% del valore della nave (×12). Il CEO dei Lloyd's ha parlato di circa il 5% il 19 marzo.
- Costo assicurativo in dollari: per una nave da 100 milioni il transito è passato da 250.000 a 375.000 $.
- Noli: TD3C (Golfo–Cina) quasi triplicato; una VLCC a circa WS225, circa 12 milioni di $ a viaggio.
- Container: Hapag-Lloyd applica un sovrapprezzo di guerra di 1.500 $/TEU.
- Urea: da 475 a 680 $/t, poi oltre 850 $/t ad aprile secondo la stampa sui dati della Banca Mondiale.
- Riserve: l'IEA ha rilasciato 400 milioni di barili, pari a 20 giorni di flusso di Hormuz.
- GNL: Ras Laffan è in forza maggiore dal 4 marzo. I treni 4 e 6 sono danneggiati (12,8 Mt/anno) e la forza maggiore è prorogata almeno a fine dicembre ([Global LNG Hub](https://globallnghub.com/qatar-lng-capacity-hit-as-ras-laffan-attacks-damage-key-trains/)).
- Banche centrali: la BCE ha alzato i tassi a giugno (2,25%) e a settembre (2,5%). Ad agosto l'inflazione era al 3,3%, con l'energia al +14,3% ([Euronews](https://www.euronews.com/2026/09/10/ecb-hikes-rates-to-25-as-energy-shock-pushes-eurozone-inflation-higher)).

**Chi guadagna e chi perde** *(valutazione, senza dati di borsa per titolo)*.
- **Ne beneficiano:**
  - gli armatori di petroliere e metaniere che possono operare;
  - i produttori fuori dal Golfo (USA, Brasile, Norvegia, Guyana);
  - i raffinatori con greggio atlantico.
- **Ne soffrono:**
  - le compagnie aeree;
  - la chimica e i fertilizzanti europei, per il gas caro;
  - le raffinerie asiatiche costruite per il greggio acido del Golfo;
  - gli importatori di GNL spot del Sud Asia.
- **Gli assicuratori** incassano premi più alti ma pagano sinistri.

**Episodi storici.**
- Guerra delle petroliere: 451 navi colpite tra il 1984 e il 1988 ([USIP](https://iranprimer.usip.org/node/6146)).
- Operazione Earnest Will: 259 navi scortate in 127 convogli.
- Prima settimana del 2026: solo 16 attraversamenti visibili all'AIS nei sette giorni al 22 marzo.
- Aprile 2026: riapertura il 17 e nuova chiusura il 18, per il blocco USA dei porti iraniani.

**Stato al 9 novembre 2026.** Le fonti non concordano sui transiti:
- PortWatch conta 1 transito il 1° novembre, ma vede solo le navi con l'AIS acceso;
- Lloyd's List Intelligence conta 116 transiti di navi non legate all'Iran nella settimana 19–25 ottobre, di cui 95 petroliere e gasiere, con molti transiti «dark» ([LLI, 5 novembre](https://www.lloydslistintelligence.com/resources/blog/strait-of-hormuz-brief-5-november-2026)).

*Valutazione:* lo stretto non è chiuso a tutti. È aperto a chi accetta il rischio e spegne il transponder.

Gli altri fatti:
- UKMTO conta 144 eventi dall'inizio del conflitto; nel 75% dei casi le navi hanno proseguito.
- Il CENTCOM dice di aver dirottato 144 navi con il blocco.
- `eventi.json` registra 27 eventi entro 250 km negli ultimi 30 giorni, di cui 13 attacchi.
- Brent a 93,65 $ e TTF a 82,33 €/MWh il 9 novembre, in calo sulla mediazione del Qatar.

## 4. Mar Rosso: Bab el-Mandeb e Suez

**Cosa passava prima della crisi.**
- Suez, SUMED e Bab el-Mandeb portavano insieme il 12% del petrolio via mare e l'8% del GNL (EIA, 1° semestre 2023).
- Suez valeva il 12–15% del commercio mondiale (UNCTAD).

**La crisi 2023–2025, in numeri.**
- Il Drewry WCI è passato da 1.521 a 3.777 $/FEU tra metà dicembre 2023 e il 18 gennaio 2024.
- A metà ottobre 2024 Suez faceva 33 transiti al giorno (−55% in un anno, UNCTAD).
- I ricavi del canale sono scesi dal record di 10,2 miliardi di $ nel 2023 a circa 4,1 miliardi nel 2025.
- Il passaggio dal Capo costa circa 7.000 km e 14–24 giorni in più (UNCTAD). Su Singapore–Rotterdam andata e ritorno le emissioni salgono di oltre il 70%.
- Una portacontainer media spende 1 milione di $ via Suez e 1,7 milioni via Capo, circa 160 $/FEU in più. Un'Aframax Asia–Nord Europa spende circa 933.000 $ in più e il viaggio passa da 16 a 32 giorni (LSEG).

**Per l'Italia.**
- Confartigianato stima 8,8 miliardi di € di commercio estero persi dal novembre 2023 (stima, affidabilità bassa).
- SRM (Intesa Sanpaolo) ha dedicato il rapporto 2026 agli stretti.

*Valutazione:* la rotta del Capo fa entrare le navi da Gibilterra. Così favorisce Tanger Med (11,1 milioni di TEU nel 2025), Algeciras e il Nord Europa a scapito di Gioia Tauro, Genova e Trieste.

**Ora.** Le portacontainer tornano: Alphaliner stima che il 63% della capacità Estremo Oriente–Europa usi il Mar Rosso, e Linerlytica prevede il ritorno completo entro il 1° trimestre 2027. Il WCI era a 4.429 $/FEU il 29 ottobre (Shanghai–Genova 4.151).

*Valutazione:* il ritorno libera navi ed è ribassista per i noli nel 2027. Il rischio opposto è un attacco houthi a una petroliera saudita, che riaprirebbe la fuga dal Mar Rosso e toglierebbe l'uscita del greggio di Yanbu. Gli Houthi rivendicano attacchi ad Abqaiq e Riyadh l'8 novembre (`eventi.json`). Bab el-Mandeb ha 7 eventi entro 350 km negli ultimi 30 giorni.

## 5. Gli altri passaggi in breve

- **Panama.** Nell'anno fiscale 2026 ha registrato 13.951 transiti e un record di 521 milioni di t PC/UMS. Con la siccità 2023–24 gli slot scesero a 18 al giorno (febbraio 2024). Le metaniere sono passate da 251 nel 2021 a 32 nel 2025. Ora si attende un El Niño.
- **Malacca.** Il petrolio è sceso da 23,2 a 16,6 mb/g. Le importazioni cinesi via mare sono scese a 6,7 mb/g a maggio 2026, il minimo da dieci anni (Kpler).
- **Stretti turchi.** Il passaggio è aperto, ma i porti del Mar Nero sono sotto attacco. A ottobre un drone navale ha fermato il terminale CPC, che carica l'80% dell'export di greggio kazako. Da luglio l'export ucraino di grano è calato del 90% (Kpler).
- **Kerch.** Chiuso il 10 luglio 2026 e riaperto alle navi del grano dal 26–28 ottobre, con permessi fino al 15 novembre.
- **Stretti danesi.** Ci passano 4,5 mb/g, circa un terzo del petrolio russo via mare. La Danimarca ispeziona la flotta ombra ma non ferma le navi.
- **Taiwan.** Bloomberg Economics stima che un anno di blocco costerebbe il 5% del PIL mondiale. Il 31 ottobre Taipei ha accusato la guardia costiera cinese di molestare le navi al largo della costa est.
- **Capo di Buona Speranza.** Nel 2° trimestre 2026 ci passavano 9,4 mb/g. La settimana del 13 aprile ha segnato il record di 24 milioni di tpl di petroliere.
- **Lombok e Sonda.** Da Lombok passano le VLCC troppo cariche per Malacca e le petroliere iraniane che evitano i controlli.
- **Gibilterra e Canale di Sicilia.** Sono sicuri. Il rischio per l'Italia è sui gasdotti, cioè sul TransMed.

---

## 6. Fonti provate

| Fonte | Esito | Licenza / note |
|---|---|---|
| IEA, Strait of Hormuz Factsheet (feb. 2026), PDF su iea.blob.core.windows.net | funziona (scaricato e letto) | CC BY 4.0 |
| Howden Re, rapporto del 27 marzo 2026 (PDF) | funziona | citazione |
| Lloyd's List Intelligence, brief Hormuz e Mar Rosso (blog pubblico) | funziona | citazione; i dati completi sono a pagamento |
| straits.live (brief giornalieri su IMF PortWatch) | funziona | progetto OSINT indipendente, testi assistiti da AI: affidabilità media |
| eia.gov, rigzone.com, iea.org, unctad.org, spglobal.com, seatrade-maritime.com, lloydslist.com, ahram.org.eg, bakerinstitute.org | **non raggiungibili da questo ambiente** (DNS o 403 del proxy) | dati presi da ricerche web e da stretti.json |
| IMF PortWatch | raggiungibile, ma è il dominio dell'agente PortWatch: **non rifatto** | collegato da `portwatch.json` quando esisterà |
| File interni (prezzi, mercati, gas-italia, eventi) | funzionano | dato dell'osservatorio |

Le cifre di stampa riprese da aggregatori (pulse.bot, StartMag) hanno affidabilità «bassa» nel file.

## 7. Cosa fa lo script

`raccogli.py` non inventa né scarica dati curati. Fa due cose.

**Valida il file:**
- campi obbligatori;
- valore, anno, fonte, link e data_fonte per ogni voce;
- formato delle date;
- link http o file locale esistente;
- base dichiarata per ogni valutazione;
- chiavi coerenti con `stretti.json` e `labels.json`;
- avviso se lo stato attuale ha più di 14 giorni o un fatto ha più di 90 giorni.

**Aggiorna le parti automatiche:**
- prezzi collegati da `prezzi.json` (Brent, WTI, TTF, Henry Hub);
- Baltic Dry, Brent e TTF della raccolta del giorno da `mercati.json`;
- flussi TransMed e Greenstream da `gas-italia.json`;
- eventi degli ultimi 30 giorni entro un raggio, da `eventi.json`;
- l'ultimo dato che nomina il passaggio in `portwatch.json`, `noli.json`, `gpr.json` e `sanzioni-navi.json`, quando esisteranno: oggi sono segnati «file non ancora prodotto».

Con `--controlla` valida soltanto; con `--verifica-link` prova anche i link. Ultimo giro: 0 errori e 4 avvisi (fatti datati per Panama, Malacca, Gibilterra, Lombok).

## 8. Collegamenti con gli altri livelli

| Livello | Collegamento |
|---|---|
| **Eventi** | gli attacchi UKMTO a Hormuz e le rivendicazioni houthi entrano nello `stato_attuale.automatico.eventi_vicini` di ogni scheda |
| **Oleodotti** (`linee.json`, `condotte.json`) | Est-Ovest, ADCOP, Goreh–Jask, SUMED, Kirkuk–Ceyhan, CPC, TransMed e Greenstream sono le alternative citate. Si possono evidenziare quando si apre la scheda |
| **Mercati** | Brent, TTF e Baltic Dry già legati. I noli (`noli.json`) e il GPR (`gpr.json`) si agganciano da soli quando l'altro agente li pubblica |
| **Scorte** | SPR USA, stoccaggi UE e GNL qatarino perso (`report/agenti/scorte.md`) |
| **Sanzioni** | flotta ombra (stretti danesi, Lombok, Hormuz «dark») ↔ `sanzioni-navi.json` |

**Proposta per la mappa.** Il colore del simbolo di ogni passaggio segue `stato`: rosso «chiuso di fatto», arancio «minaccia alta», giallo «aperto con limiti», verde «aperto». Al clic si apre una scheda a schede:

- cosa passa;
- chi è esposto (con l'Italia in evidenza);
- alternative, con la linea dell'oleodotto o della rotta accesa sulla mappa;
- prezzi (valori automatici con freccia);
- storia;
- stato attuale (con gli eventi vicini).

La tabella riassuntiva (`riepilogo`) può fare da pannello «Stretti» accanto al pannello Mercati.

## 9. Limiti

- Le cifre sui transiti di Hormuz divergono di due ordini di grandezza a seconda del metodo: AIS visibile o transiti «dark» ricostruiti. Nel file ci sono entrambe.
- Mancano numeri verificati per:
  - GPL mondiale via Hormuz;
  - quote mondiali di Gibilterra, Sicilia, Lombok e Sonda;
  - capacità degli oleodotti cinesi;
  - quota italiana del greggio kazako nel 2025.
- I dati EIA e IEA più recenti sono letti tramite stampa: eia.gov non era raggiungibile.
- Gli episodi della Guerra delle petroliere non hanno premi war risk storici da fonte verificata.
- Lo stato attuale è curato a mano: lo script segnala quando invecchia, ma non lo riscrive.
