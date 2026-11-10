# Hormuz e Mar Rosso: energia, logistica e mercati

**Report n. 1 · novembre 2026** · Gabriele Giuliani · Monitor geoeconomico
Dati aggiornati al 9 novembre 2026. Versione impaginata con i grafici: [docs/report/hormuz-mar-rosso-2026-11.html](../docs/report/hormuz-mar-rosso-2026-11.html).

> **Come leggere questo report.** Ogni numero ha una fonte e una data. Le frasi marcate *Valutazione* sono ragionamenti dell'osservatorio sulle fonti citate, non fatti. Dove un dato manca, è scritto. Il report non dà consigli di investimento.

> **Parole utili.** *AIS*: il transponder che trasmette posizione e identità della nave; spegnerlo rende la nave invisibile ai sistemi pubblici. *mb/g*: milioni di barili al giorno. *GNL*: gas naturale liquefatto, viaggia su metaniere. *TTF*: il prezzo di riferimento del gas all'ingrosso in Europa (hub olandese), in euro per MWh. *Brent*: il prezzo di riferimento del greggio. *War risk*: l'assicurazione di guerra per nave e carico, pagata per ogni viaggio in zona di rischio. *Forza maggiore*: la clausola che sospende un contratto di fornitura per cause esterne. *Bab el-Mandeb*: lo stretto tra Yemen e Gibuti all'ingresso sud del Mar Rosso. *UKMTO*: il centro britannico che raccoglie gli avvisi di sicurezza delle navi.

---

## 1. In breve

1. **Hormuz è chiuso di fatto dal 2 marzo 2026, ma non per tutti.** Le navi visibili con l'AIS (il transponder di bordo) sono 4,4 al giorno nella settimana al 1° novembre, contro 90,3 un anno prima (−95%; IMF PortWatch, [`portwatch.json`](../docs/data/portwatch.json)). Molte però passano con il transponder spento: nella settimana 19–25 ottobre PortWatch conta 23 transiti, Lloyd's List Intelligence 116, contando solo le navi non legate all'Iran ([LLI, 5 novembre](https://www.lloydslistintelligence.com/resources/blog/strait-of-hormuz-brief-5-november-2026)).
2. **Il rischio si sposta sul Mar Rosso.** L'Arabia Saudita aggira Hormuz con l'oleodotto Est-Ovest fino a Yanbu, sul Mar Rosso. Da lì il greggio per l'Asia passa da Bab el-Mandeb: 8,1 milioni di barili al giorno (mb/g) nel 2° trimestre 2026, da 5,4 a fine 2025 ([EIA via Rigzone](https://www.rigzone.com/news/how_much_oil_transited_through_worlds_chokepoints_in_2q-12-aug-2026-184358-article/)). Dal 20 luglio gli Houthi dichiarano lo stretto chiuso alle navi legate all'Arabia Saudita. Suez invece si riprende: 1.490 navi a ottobre, il mese più trafficato dall'inizio della crisi del Mar Rosso ([EgyptToday, dati dell'Autorità del Canale](https://www.egypttoday.com/Article/1/150437/Suez-Canal-records-highest-monthly-vessel-traffic-since-Red-Sea)).
3. **Il gas pesa più del petrolio.** Il 9 novembre il Brent è a 92,62 dollari al barile (quotazione provvisoria: −5,8% in giornata, +45,6% su un anno); il TTF, il prezzo di riferimento del gas in Europa, è a 82,33 €/MWh, +164% su un anno ([`prezzi.json`](../docs/data/prezzi.json)). Il gas naturale liquefatto (GNL) del Qatar non ha vie alternative: è in forza maggiore dal 4 marzo, prorogata almeno a fine dicembre ([gasworld](https://www.gasworld.com/story/qatarenergy-extends-lng-force-majeure-on-edison-cargoes-to-end-december/2262726.article/)). Gli stoccaggi di gas sono al 58,9% in Germania e al 63,5% nei Paesi Bassi (8 novembre, [`scorte.json`](../docs/data/scorte.json)).
4. **Lo shock energetico è arrivato all'inflazione e ai tassi.** Nell'area euro l'inflazione è al 4,0% a ottobre (stima flash Eurostat). La BCE ha alzato il tasso sui depositi a giugno e a settembre, al 2,50%; la Bank of England al 4,00% il 5 novembre. La Fed è ferma al 3,75–4,00%, con due voti per un rialzo ([`calendario.json`](../docs/data/calendario.json)).
5. **L'Italia è esposta più sul gas e sui prezzi che sul greggio.** Dal Golfo arriva tra il 5,6% e il 10,2% del greggio importato, ma il 32,6% del GNL, dal Qatar (UN Comtrade 2025, quote in valore). La dipendenza maggiore è vicina: il gasdotto TransMed dall'Algeria porta il 34,0% del gas importato via tubo e GNL negli ultimi 12 mesi ([`gas-italia.json`](../docs/data/gas-italia.json)). Le scorte petrolifere di emergenza sono a 77,2 giorni (agosto), sotto i circa 90 chiesti dalla normativa UE ([`scorte.json`](../docs/data/scorte.json)).

---

## 2. Cosa è successo nel 2026

Cronologia essenziale. I dati di mercato sono chiusure di [`prezzi.json`](../docs/data/prezzi.json) (Yahoo Finance), con le date delle sedute corrette (vedi Limiti); i transiti sono di IMF PortWatch.

| Data | Fatto | Fonte |
|---|---|---|
| 28 febbraio | Inizia la guerra di Stati Uniti e Israele contro l'Iran. | Report dell'osservatorio ([`report.json`](../docs/data/report.json)), su [Al Jazeera](https://www.aljazeera.com/news/2026/11/9/qatar-pm-to-meet-trump-whats-the-latest-on-us-iran-negotiations) |
| 1–2 marzo | I transiti a Hormuz passano da 57 (28/2) a 20 (1/3) e 4 (2/3). Il TTF sale da 31,96 a 44,51 €/MWh (+39%) in una seduta; il Brent da 72,48 a 77,74 $. | [`portwatch.json`](../docs/data/portwatch.json), [`prezzi.json`](../docs/data/prezzi.json) |
| 4 marzo | QatarEnergy dichiara forza maggiore dopo gli attacchi a Ras Laffan; danneggiati i treni 4 e 6 (12,8 Mt/anno). | [Global LNG Hub](https://globallnghub.com/qatar-lng-capacity-hit-as-ras-laffan-attacks-damage-key-trains/) |
| 14 marzo | Droni su Fujairah, terminale dell'oleodotto emiratino che aggira Hormuz: carichi sospesi (dato senza link alla fonte primaria, non verificato). Nuovo attacco a Fujairah il 4 maggio. | [`energia.md`](agenti/energia.md); per il 4 maggio [Al Jazeera](https://www.aljazeera.com/news/2026/5/5/whats-the-significance-of-uaes-fujairah-hit-on-monday) |
| 17–18 marzo | Riprende l'export iracheno da Kirkuk a Ceyhan dopo l'accordo Baghdad–Erbil. | [The National](https://www.thenationalnews.com/business/energy/2026/03/18/iraq-to-resume-oil-exports-via-turkeys-ceyhan-port-amid-regional-tensions/) |
| 19 marzo | Brent a 119 $ in seduta secondo Howden Re (chiusura 108,65 $); la chiusura più alta dell'anno è 118,35 $ il 31 marzo (Yahoo Finance; in `prezzi.json` risulta al 30 per un errore di fuso orario, vedi Limiti). Premio war risk fino al 3% del valore della nave, da 0,25%. | [Howden Re, 27 marzo](https://www.howdenre.com/sites/howdenre.howdenprod.com/files/2026-03/HowdenRe_Strait_of_Hormuz_report_March272026.pdf) |
| 28 marzo | Secondo una fonte anonima citata da Fortune, l'oleodotto saudita Est-Ovest pompa a pieno regime, 7 mb/g (la capacità annunciata da Aramco nel 2025), di cui 2 per le raffinerie saudite. | [Fortune](https://fortune.com/2026/03/28/saudi-arabia-east-west-oil-pipeline-strait-hormuz-bypass-7-million-barrels-yanbu-red-sea/) |
| 8 aprile | Tregua tra Iran e Stati Uniti. | [`report.json`](../docs/data/report.json) |
| 13 aprile | Gli Stati Uniti impongono il blocco navale dei porti iraniani. | [The New Arab](https://www.newarab.com/news/hormuz-conflict-continues-iran-closes-strait-over-us-blockade) |
| 17–18 aprile | L'Iran annuncia la riapertura di Hormuz e il giorno dopo la revoca, per il blocco. PortWatch: 20 transiti il 18, 2 il 19. | [The New Arab](https://www.newarab.com/news/hormuz-conflict-continues-iran-closes-strait-over-us-blockade), [`portwatch.json`](../docs/data/portwatch.json) |
| giugno | La BCE alza il tasso sui depositi al 2,25%. Memorandum di Islamabad tra Iran e USA (poi saltato). Il 18 giugno il blocco USA viene sospeso: a Hormuz i transiti risalgono fino a 51 il 24 giugno; il Brent scende a 71,99 $ il 26 giugno e tocca il minimo della guerra, 71,57 $, il 1° luglio. | [Euronews](https://www.euronews.com/2026/09/10/ecb-hikes-rates-to-25-as-energy-shock-pushes-eurozone-inflation-higher); [`report.json`](../docs/data/report.json) (RFE/RL); [`portwatch.json`](../docs/data/portwatch.json); [`prezzi.json`](../docs/data/prezzi.json) |
| 14 luglio | Il CENTCOM riprende il blocco dei porti iraniani. Secondo l'UKMTO le ostilità in mare riprendono a inizio luglio. | [`report.json`](../docs/data/report.json), su [RFE/RL](https://www.rferl.org/a/iran-live-blog-trump-middle-east/33803414.html) |
| 20 luglio | Gli Houthi dichiarano il blocco delle navi legate all'Arabia Saudita a Bab el-Mandeb. | [`energia.md`](agenti/energia.md); [AP via WTOP](https://wtop.com/world/2026/07/a-new-threat-by-yemens-houthis-could-widen-the-iran-war-and-put-another-trade-chokepoint-at-risk/) |
| 31 luglio | Seconda metaniera con GNL qatarino colpita in un mese: la GasLog Shanghai, vicino a Limah (Oman), all'uscita di Hormuz. Nel Mar Rosso, tra il 20 luglio e il 2 agosto, gli Houthi colpiscono quattro petroliere saudite. | [Cyprus Shipping News, 6 agosto](https://cyprusshippingnews.com/2026/08/06/a-second-qatari-lng-carrier-struck-as-22-chinese-vessels-cross-the-red-sea-unharmed/) |
| 24 agosto | Ultimo attacco a navi nel Mar Rosso segnalato dall'UKMTO (al 29 ottobre). | [LLI, Red Sea Brief 29 ottobre](https://www.lloydslistintelligence.com/resources/blog/red-sea-brief---29-october-2026) |
| 10 settembre | La BCE porta il tasso sui depositi al 2,50%; inflazione di agosto al 3,3%, energia +14,3%. | [Euronews](https://www.euronews.com/2026/09/10/ecb-hikes-rates-to-25-as-energy-shock-pushes-eurozone-inflation-higher) |
| 11–13 settembre | L'oleodotto Est-Ovest viene fermato da droni partiti dall'Iraq; riparte a basso regime intorno al 22. Il Brent era già salito a 107,63 $ il 10 settembre. | [Al-Monitor](https://al-monitor.com/originals/2026/09/saudi-running-out-oil-export-options-iran-allies-choke-routes); [The National](https://thenationalnews.com/business/energy/2026/09/22/saudi-arabia-restarts-east-west-pipeline-for-crude-exports/) |
| 28 settembre | QatarEnergy proroga ancora la forza maggiore, alla vigilia dell'inverno. A fine ottobre la proroga per le consegne a Edison (terminale Adriatic LNG) arriva a fine dicembre. | [gasworld](https://www.gasworld.com/story/qatarenergy-extends-lng-force-majeure-on-edison-cargoes-to-end-december/2262726.article/); [The National](https://www.thenationalnews.com/business/energy/2026/09/28/qatar-extends-lng-force-majeure-as-hormuz-disruption-threatens-winter-supply) |
| ottobre | Suez: 1.490 navi nel mese. Il 30 ottobre il TTF chiude a 103,94 €/MWh, il massimo dell'anno, e il Brent a 117,64 $. Fed (28/10) e BCE (29/10) lasciano i tassi invariati. | [EgyptToday](https://www.egypttoday.com/Article/1/150437/Suez-Canal-records-highest-monthly-vessel-traffic-since-Red-Sea); [`prezzi.json`](../docs/data/prezzi.json); [`calendario.json`](../docs/data/calendario.json) |
| 1–8 novembre | A Hormuz l'UKMTO pubblica gli avvisi da 191 a 200 su navi colpite o coinvolte; il 4–5 una petroliera colpita a nord del Qatar, probabilmente la Velos Sapphire, con un marittimo morto. Il 2 e il 6 attacchi USA su Qeshm. L'8 i Pasdaran rivendicano tre petroliere su una rotta «non autorizzata»; gli Houthi rivendicano attacchi ad Abqaiq e Riyadh. | [`eventi.json`](../docs/data/eventi.json): [UKMTO 196](https://x.com/UK_MTO/status/2118256876966039679), [AP via NBC](https://www.nbcnews.com/news/us-news/us-military-carries-new-targeted-strikes-iran-rcna607969), [Al Jazeera](https://www.aljazeera.com/news/2026/11/9/who-are-the-seafarers-caught-in-the-us-israeli-war-on-iran) |
| 5 novembre | La Bank of England alza il Bank Rate al 4,00%. | [`calendario.json`](../docs/data/calendario.json) |
| 9 novembre | Il premier del Qatar porta a Washington un piano iraniano di riapertura in due giorni. Brent −5,8% a 92,62 $ (provvisorio), TTF −3,8% a 82,33 €. | [Al Jazeera](https://www.aljazeera.com/news/2026/11/9/qatar-pm-to-meet-trump-whats-the-latest-on-us-iran-negotiations); [`prezzi.json`](../docs/data/prezzi.json) |

L'indice di rischio geopolitico di Caldara e Iacoviello segue lo stesso profilo: 330 a marzo 2026 (media 1985–2019 = 100), 126 ad agosto, 151 a ottobre ([`gpr.json`](../docs/data/gpr.json)).

---

## 3. Hormuz

### Cosa passa

Prima della guerra, nel 2025, da Hormuz uscivano **19,9 milioni di barili al giorno di petrolio**: 14,95 di greggio (quasi il 34% del greggio commerciato nel mondo) e 4,93 di prodotti ([IEA, Strait of Hormuz Factsheet, febbraio 2026](https://iea.blob.core.windows.net/assets/c8248eba-8689-46d9-ae4b-b858b59c0f1c/StraitofHormuz2026-Factsheet.pdf)). Per origine: Arabia Saudita 6,23 mb/g, Iraq 3,63, Emirati 3,24, Iran 2,41, Kuwait 2,37, Qatar 1,43.

- **GNL:** poco più di 112 miliardi di m³, quasi il 20% del commercio mondiale; passano dallo stretto il 93% del GNL qatarino e il 96% di quello emiratino (IEA).
- **Fertilizzanti:** un quarto dell'export mondiale di urea per la [Banca Mondiale](https://blogs.worldbank.org/en/opendata/fertilizer-prices-surge-as-strait-of-hormuz-disruptions-tighten-); il 43% dell'urea via mare per la North Dakota State University ([Fertilizer Daily](https://www.fertilizerdaily.com/20260807-un-itc-hormuz-disruption-urea-exports-83-percent-drop/)). Le stime non concordano perché misurano cose diverse.
- **Destinazioni:** circa l'80% del petrolio va in Asia; Cina, India, Giappone e Corea del Sud ricevevano insieme il 69% del greggio nel 2024 ([EIA](https://www.eia.gov/todayinenergy/detail.php?id=65504)). All'Europa andava solo il 4% del greggio, circa 600.000 b/g, e poco più del 10% del GNL che passava dallo stretto (IEA).

### I transiti misurati

![Transiti giornalieri](grafici/transiti.svg)
*Navi al giorno, media mobile a 7 giorni, da ottobre 2023 (per mostrare il livello prima degli attacchi houthi) al 1° novembre 2026. Fonte: IMF PortWatch, [`portwatch.json`](../docs/data/portwatch.json). Eventi: 1 = Hormuz chiuso di fatto (2 marzo); 2 = blocco USA sospeso (18 giugno); 3 = blocco houthi delle navi saudite (20 luglio).*

**Fatti (PortWatch).**
- Nel 2025 la media era di 85,5 navi al giorno; a febbraio 2026 78,3. Da marzo la media mensile non ha mai superato 13 navi al giorno (12,9 a giugno, durante la sospensione del blocco).
- Settimana 26 ottobre – 1° novembre: 4,4 navi al giorno (1,4 petroliere, 1,9 rinfuse); −95% sulla stessa settimana del 2025. Il 1° novembre: 1 transito.

**La discrepanza con Lloyd's List Intelligence.** Per la stessa settimana del 19–25 ottobre:

| Fonte | Transiti | Di cui petroliere e gasiere | Cosa conta |
|---|---|---|---|
| IMF PortWatch | 23 | 6 | navi che attraversano lo stretto con l'AIS acceso, stimate da segnali AIS |
| Lloyd's List Intelligence | 116 (solo navi non legate all'Iran, da carico, sopra 10.000 t di portata lorda) | 95 | AIS e altre fonti; include i transiti «dark» (transponder spento) |

Fonti: [`portwatch.json`](../docs/data/portwatch.json) (somma dei sette giorni); [LLI, Strait of Hormuz Brief del 5 novembre](https://www.lloydslistintelligence.com/resources/blog/strait-of-hormuz-brief-5-november-2026). LLI dà anche una media di 121 transiti a settimana tra il 5 e il 25 ottobre. Già ad agosto Kpler stimava che circa due terzi dei transiti fossero «dark» o non identificati ([Gulf News, dati Kpler](https://gulfnews.com/amp/story/world%2Fmena%2Fsix-months-into-the-iran-war-hormuz-is-still-a-chokepoint-under-siege-and-uncertainty-grips-energy-markets-1.500651257)).

Perché le cifre divergono:
1. **Metodo.** PortWatch è costruito sui segnali AIS e quindi vede solo chi trasmette. In zona di guerra molte navi spengono il transponder per non farsi localizzare, e le navi della flotta ombra lo fanno di regola. LLI unisce l'AIS ad altre fonti di intelligence marittima (il brief non dice quali) e conta anche i transiti al buio: per questo considera «completa» solo la settimana precedente.
2. **Perimetro.** LLI conta solo le navi da carico sopra 10.000 tonnellate non legate all'Iran; PortWatch conta tutte le navi che vede.
3. **Ritardo.** PortWatch pubblica con circa una settimana di ritardo: gli attacchi del 4–8 novembre non sono ancora nei suoi numeri.

*Valutazione:* nessuna delle due cifre è «quella vera». PortWatch misura bene il traffico normale e trasparente, che è quasi scomparso; LLI misura meglio quanto passa davvero. Entrambe dicono la stessa cosa: **lo stretto non è chiuso a tutti, è aperto a chi accetta il rischio e spegne il transponder**. Anche il dato LLI resta però sotto i livelli prebellici: circa 17 navi al giorno contro le 85 di PortWatch nel 2025, che a loro volta sono un minimo.

Altri fatti sullo stato attuale: l'UKMTO conta 144 eventi segnalati dall'inizio del conflitto a fine ottobre, e nel 75% dei casi le navi hanno proseguito; il CENTCOM dice di aver dirottato 144 mercantili con il blocco dei porti iraniani (LLI, 5 novembre; 147 l'8 novembre secondo Al Jazeera, in [`report.json`](../docs/data/report.json)). [`eventi.json`](../docs/data/eventi.json) registra 27 eventi entro 250 km dallo stretto tra il 29 ottobre e il 9 novembre (il file parte dal 29 ottobre), di cui 13 attacchi.

### Le alternative e i loro limiti

| Via | Capacità | Stato nel 2026 | Fonte |
|---|---|---|---|
| Oleodotto Est-Ovest, Abqaiq–Yanbu (Arabia Saudita) | 5 mb/g di progetto, 7 dichiarati da Aramco (2025) | a pieno regime a fine marzo (fonte anonima); fermato da droni l'11–13 settembre, riavviato a basso regime intorno al 22 | [IEA](https://iea.blob.core.windows.net/assets/c8248eba-8689-46d9-ae4b-b858b59c0f1c/StraitofHormuz2026-Factsheet.pdf), [Fortune](https://fortune.com/2026/03/28/saudi-arabia-east-west-oil-pipeline-strait-hormuz-bypass-7-million-barrels-yanbu-red-sea/), [Al-Monitor](https://al-monitor.com/originals/2026/09/saudi-running-out-oil-export-options-iran-allies-choke-routes) |
| Porti di Yanbu | circa 5 mb/g di export di greggio | è il vero collo di bottiglia, non l'oleodotto | [Baker Institute](https://www.bakerinstitute.org/sites/default/files/2026-04/20260408-Krane%20Alexander-Losing%20Hormuz-Working%20Paper.pdf) |
| ADCOP, Habshan–Fujairah (Emirati) | 1,5–1,8 mb/g, circa 0,7 liberi prima della guerra | Fujairah e Habshan colpite a marzo, aprile e maggio; volumi attuali non pubblici | IEA; [`energia.md`](agenti/energia.md) |
| Goreh–Jask (Iran) | 1 mb/g dichiarato | di fatto fermo a inizio 2026; usato di più ad agosto contro il blocco USA | IEA; [S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/crude-oil/080526-iran-turns-to-crude-exports-via-jask-terminal-amid-hormuz-disruptions) |
| Kirkuk–Ceyhan (Iraq–Turchia) | obiettivo 0,5–0,6 mb/g | circa 130.000 b/g ad agosto, circa 500.000 a fine ottobre (fonti anonime) | [Shafaq](https://shafaq.com/en/Economy/Kirkuk-Ceyhan-oil-exports-fall-to-around-130-000-bpd), [Iraqi News](https://iraqinews.com/iraq/iraq-to-raise-oil-exports-via-turkey-to-600000-barrels-per-day) |
| GNL di Qatar ed Emirati | nessuna alternativa | solo il gasdotto Dolphin verso Emirati e Oman, con poca capacità libera | IEA |

Il risultato si vede nei dati EIA: nel 2° trimestre 2026 da Hormuz sono passati 4,9 mb/g, contro 21,6 nel 4° trimestre 2025 (−77%) ([EIA via Rigzone](https://www.rigzone.com/news/how_much_oil_transited_through_worlds_chokepoints_in_2q-12-aug-2026-184358-article/)). A inizio novembre, secondo Reuters, le esportazioni del Golfo viaggiano al 60–80% del normale ([`calendario.json`](../docs/data/calendario.json)). *Valutazione:* se confermato, il dato è compatibile con i transiti al buio contati da LLI, non con i numeri di PortWatch.

*Valutazione:* le vie di aggiramento possono portare fuori in tutto circa 6,5–7 mb/g di greggio (Yanbu circa 5, Fujairah fino a 1,8, Ceyhan circa 0,5), di cui solo 3,5–5,5 in più rispetto a prima della guerra secondo l'IEA, contro quasi 20 mb/g di petrolio che passavano dallo stretto. Iraq del sud, Kuwait, Qatar, Bahrein, quasi tutti i prodotti raffinati e tutto il GNL restano senza uscita. E ogni alternativa è stata colpita almeno una volta nel 2026: aggirare Hormuz non vuol dire uscire dalla guerra.

Il cuscinetto delle scorte si è assottigliato. L'IEA ha coordinato un rilascio record di 400 milioni di barili, pari a 20 giorni di flusso normale di Hormuz (Howden Re). La riserva strategica USA è scesa a 282,2 milioni di barili al 30 ottobre, il minimo dall'ottobre 1982 (−31% su un anno, EIA, [`scorte.json`](../docs/data/scorte.json)).

---

## 4. Mar Rosso, Bab el-Mandeb e Suez

**Prima della crisi.** Suez, l'oleodotto SUMED e Bab el-Mandeb portavano insieme circa il 12% del petrolio via mare e l'8% del GNL (EIA, 1° semestre 2023). Da Suez passava il 12–15% del commercio mondiale ([UNCTAD](https://unctad.org/news/suez-and-panama-canal-disruptions-threaten-global-trade-and-development)).

**Bab el-Mandeb oggi: il «secondo Hormuz».**
- PortWatch: 27,3 navi al giorno nella settimana al 1° novembre, −22% su un anno e −66% sulla stessa settimana del 2023 (79,6), prima degli attacchi houthi. Il calo è ripreso a luglio, con il blocco houthi: media mensile 36,6 a giugno, 33,7 a luglio, 27,4 ad agosto, 27,9 a ottobre.
- Petrolio: 8,1 mb/g nel 2° trimestre 2026, più che prima della guerra, per il greggio saudita caricato a Yanbu (EIA).
- Lloyd's List: 295 transiti nella settimana 12–18 ottobre; in tonnellaggio −46% rispetto a prima della crisi houthi. Nessun attacco UKMTO nel Mar Rosso dal 24 agosto, ma più contatti radio con sedicenti «autorità yemenite» ([LLI, 29 ottobre](https://www.lloydslistintelligence.com/resources/blog/red-sea-brief---29-october-2026)).
- Secondo S&P Global (citato in [`energia.md`](agenti/energia.md)) a ottobre i transiti legati all'Arabia Saudita sono scesi a 21, da 52 a settembre.
- L'8 novembre gli Houthi rivendicano attacchi ad Abqaiq e all'aeroporto di Riyadh; un edificio Aramco a Riyadh risulta danneggiato (CNN, video geolocalizzati). Una sola fonte OSINT (Davide Montingelli) dice lo stretto chiuso alle navi legate all'Arabia Saudita dal 3 novembre, senza avviso ufficiale: affidabilità media ([`eventi.json`](../docs/data/eventi.json)).

**Suez: la ripresa.**
- PortWatch: 43,0 navi al giorno, +10% su un anno (petroliere +22%), ma ancora −43% sulla stessa settimana del 2023 (76,0).
- Autorità del Canale: 1.490 navi a ottobre, +32% su un anno ([EgyptToday](https://www.egypttoday.com/Article/1/150437/Suez-Canal-records-highest-monthly-vessel-traffic-since-Red-Sea)).
- Container: 753.000 TEU a settimana nelle prime due settimane di ottobre, sopra il 50% del 2023 per la prima volta ([BIMCO](https://www.bimco.org/news-insights/market-analysis/shipping-number-of-the-week/2026/1014-snow/)). Alphaliner stima che il 63% della capacità Estremo Oriente–Europa usi di nuovo il Mar Rosso; Linerlytica prevede il ritorno completo entro il 1° trimestre 2027 ([Seatrade Maritime](https://www.seatrade-maritime.com/containers/full-suez-return-for-container-carriers-expected-by-q1-2027)).
- Ricavi: 4,67 miliardi di dollari nell'anno fiscale luglio 2025–giugno 2026 (+23%), lontani dal record di 10,2 miliardi dell'anno solare 2023 ([Ahram Online](https://english.ahram.org.eg/News/571808.aspx); [gCaptain](https://gcaptain.com/suez-canal-revival-gathers-pace-as-hormuz-crisis-reroutes-ships/)).

*Valutazione:* il Mar Rosso oggi ha due direzioni opposte. Le portacontainer tornano a Suez perché da agosto non ci sono attacchi; il greggio saudita, invece, dipende da uno stretto che gli Houthi dichiarano chiuso proprio a quelle navi. La crescita delle petroliere a Suez mentre Bab el-Mandeb cala è coerente con traffico verso e da Yanbu e il SUMED (fino a 2,5 mb/g verso il Mediterraneo senza passare da Bab el-Mandeb, [AP](https://wtop.com/world/2026/07/a-new-threat-by-yemens-houthis-could-widen-the-iran-war-and-put-another-trade-chokepoint-at-risk/)), ma va verificata con dati per singola nave.

---

## 5. La catena delle conseguenze

### Noli e assicurazioni

- **War risk.** Da 0,25% del valore della nave prima della guerra a fino al 3% per le navi legate a USA, Regno Unito o Israele; per una nave da 100 milioni di dollari un transito nel Golfo costava circa 250.000 dollari prima della guerra e da 375.000 a 3 milioni a marzo, secondo il profilo di rischio della nave ([Howden Re, marzo](https://www.howdenre.com/sites/howdenre.howdenprod.com/files/2026-03/HowdenRe_Strait_of_Hormuz_report_March272026.pdf)). Una stima di ottobre (32 volte il livello prebellico, [straits.live](https://straits.live/)) ha affidabilità bassa: un premio aggiornato da fonte primaria **manca**.
- **Petroliere.** Il nolo Golfo–Cina (TD3C) è quasi triplicato a marzo, circa 12 milioni di dollari a viaggio per una VLCC (Howden Re). Una serie aggiornata dei noli tanker **manca** nell'osservatorio.
- **Container.** Drewry WCI a 4.389 dollari per container da 40 piedi il 5 novembre (−1% sulla settimana, +124% su un anno secondo il [report sulla supply chain](supply-chain-2026-11.md)); Shanghai–Genova 4.166, Shanghai–Rotterdam 3.615. Freightos FBX globale 3.452 dollari il 6 novembre, da 3.690 a metà agosto; Cina–Mediterraneo 4.324 ([`noli.json`](../docs/data/noli.json)). Hapag-Lloyd applica dal marzo un sovrapprezzo di guerra di 1.500 dollari per TEU (Howden Re).
- **Rinfuse.** Baltic Dry a 2.805 punti il 6 novembre (Baltic Exchange, ripreso da Trading Economics; variazione annua non verificata). Il valore di 2.854 del 9 novembre citato in [`nord.md`](agenti/nord.md) viene da un contratto derivato (CFD) che replica l'indice, non dall'indice: non è più raccolto in `noli.json` (affidabilità media).

*Valutazione:* i noli container scendono piano perché il ritorno a Suez accorcia i viaggi e libera navi; è un fattore ribassista per il 2027. Che il nolo verso Genova resti sopra quello verso Rotterdam è coerente con la maggiore esposizione del Mediterraneo al Mar Rosso.

### Prezzi: Brent, TTF, urea

![Brent e TTF](grafici/prezzi.svg)
*Chiusure giornaliere dall'8 ottobre 2025 al 9 novembre 2026. Fonte: Yahoo Finance, [`prezzi.json`](../docs/data/prezzi.json). Eventi: 1 = Hormuz chiuso (2 marzo); 2 = tregua (8 aprile); 3 = blocco USA sospeso (18 giugno); 4 = Est-Ovest fermato (11 settembre); 5 = massimi d'autunno (30 ottobre); 6 = mediazione del Qatar (9 novembre). Grafico prodotto con la versione di `prezzi.json` delle 19:38 UTC del 9 novembre; nelle etichette dei punti le date tra l'8 marzo e il 1° novembre risultano anticipate di un giorno (errore di fuso orario, vedi Limiti).*

**Brent.** Da una media di 69,4 dollari al barile a febbraio a 99,6 a marzo; massima chiusura 118,35 il 31 marzo, poi 118,03 il 29 aprile; minimo della guerra 71,57 il 1° luglio, con il blocco USA sospeso; risalita a 117,64 il 30 ottobre; 92,62 il 9 novembre, quotazione provvisoria (+45,6% su un anno, +52% da inizio anno). Il WTI è a 86,95. Date delle sedute verificate su Yahoo Finance il 9 novembre.

**TTF.** Da 31,96 euro/MWh il 27 febbraio a 44,51 il 2 marzo; poi una salita quasi continua da luglio, fino al massimo dell'anno, 103,94, il 30 ottobre; 82,33 il 9 novembre (+164% su un anno, +192% da inizio anno). L'Henry Hub americano è a 3,21 dollari/MMBtu, −13% da inizio anno.

*Valutazione:* il petrolio ha reagito soprattutto alle notizie militari (marzo, aprile, settembre) e si è sgonfiato con le tregue; il gas ha avuto un primo salto a marzo e poi è salito con l'avvicinarsi dell'inverno. Il motivo è nelle scorte: gli stoccaggi UE erano a 729 TWh a fine agosto, −24% sulla media di cinque anni (Eurostat, [`scorte.json`](../docs/data/scorte.json)), e l'IEA scrive che entrano nell'inverno al livello più basso dal 2013 e nel caso peggiore (inverno freddo e Hormuz ancora chiuso) potrebbero scendere sotto il 10% a fine marzo ([IEA, 3 novembre](https://www.iea.org/news/low-storage-buffers-in-europe-could-prolong-global-gas-market-tightness-well-into-2027)). Lo scarto tra TTF e Henry Hub misura il premio europeo per il GNL che manca.

**Urea.** Da 475 a 680 dollari per tonnellata nelle prime settimane di guerra (Howden Re), oltre 850 dollari ad aprile ([Banca Mondiale](https://blogs.worldbank.org/en/opendata/fertilizer-prices-surge-as-strait-of-hormuz-disruptions-tighten-)). A fine ottobre l'export di fertilizzanti del Medio Oriente risultava in calo del 70–75% secondo Kpler ([The National](https://www.thenationalnews.com/business/energy/2026/10/31/middle-east-fertiliser-exports-decline-by-70-as-iran-war-disrupts-supplies/)). **Manca** un prezzo dell'urea aggiornato a novembre: l'osservatorio non ha ancora una serie dei fertilizzanti.

### Inflazione e banche centrali

| | Ultimo dato | Fonte |
|---|---|---|
| Area euro, inflazione HICP | 4,0% a ottobre (stima flash del 4/11), dal 3,8% di settembre | Eurostat via [`calendario.json`](../docs/data/calendario.json) |
| BCE | deposito 2,50% dal 16/9; invariato il 29/10; il comunicato parla di uno shock energetico che spinge l'inflazione e frena la crescita | [BCE, comunicato del 29/10](https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp261029~9a493adf17.en.html) |
| USA, CPI | +3,7% a settembre; la benzina (+9,1% nel mese) spiega oltre metà dell'aumento | BLS |
| Fed | 3,75–4,00%, invariato il 28/10 con due voti (Cook, Hammack) per un rialzo | Federal Reserve |
| Bank of England | Bank Rate alzato al 4,00% il 5/11; inflazione al 3,5%, vista a circa il 5% a metà 2027 | Bank of England |
| Treasury USA 10 anni | 4,86% il 6/11 (4,11% un anno prima); BTP 10 anni 4,29% e spread BTP-Bund 103,7 pb il 9/11 | U.S. Treasury via [`prezzi.json`](../docs/data/prezzi.json); ANSA via [`mercati.json`](../docs/data/mercati.json) |

**Manca** l'inflazione italiana (Istat) nei dati dell'osservatorio.

*Valutazione:* è uno shock d'offerta classico, ma le banche centrali reagiscono in modo diverso. La BCE e la BoE hanno scelto di alzare per evitare che l'inflazione energetica entri nei salari; la Fed, con un'economia forte (PIL del 3° trimestre +3,4% annualizzato), è ferma ma divisa. Un ritorno del Brent sopra i 110 dollari renderebbe più probabile un altro rialzo europeo nel 2027; una riapertura di Hormuz lo renderebbe meno probabile.

---

## 6. Chi è esposto

![Esposizione al Golfo Persico](grafici/esposizione.svg)
*Quota delle importazioni di greggio e di GNL (in valore) che arriva dai paesi del Golfo Persico. Il punto di sinistra conta solo i fornitori senza uscita alternativa (Iraq, Kuwait, Qatar, Bahrein, Iran); quello di destra aggiunge Arabia Saudita ed Emirati, che possono aggirare in parte lo stretto da Yanbu e Fujairah. Oman escluso. Fonte: UN Comtrade 2025 (Taiwan 2024), [`paesi.json`](../docs/data/paesi.json). È un'approssimazione dell'esposizione, non una misura dei transiti.*

### Asia

- **Giappone:** dal Golfo arriva tra il 10,3% e il 93,0% del greggio; Emirati 43,3%, Arabia Saudita 39,5%. Dipendenza energetica 87,3% (World Bank 2024).
- **Corea del Sud:** tra il 23,0% e il 68,8% del greggio; primo fornitore l'Arabia Saudita (34,2%).
- **India:** tra il 22,6% e il 47,9% del greggio e tra il 47,3% e il 60,8% del GNL (Qatar 47,3%). L'India importa circa il 60% del GPL che consuma, e circa il 90% di queste importazioni passava da Hormuz ([ORF](https://www.orfonline.org/expert-speak/one-narrow-strait-millions-of-cylinders-india-s-lpg-crisis)).
- **Cina:** tra il 16,0% e il 37,8% del greggio dichiarato e circa il 28% del GNL; il greggio iraniano è probabilmente nascosto sotto la voce Malesia (10,5% dell'import cinese). Le importazioni cinesi dal Medio Oriente sono scese a 1,42 mb/g a giugno, il minimo dal 2013 ([Kpler](https://www.kpler.com/pt/blog/will-china-help-reopen-hormuz)).
- **Bangladesh, India, Pakistan** ricevevano da Hormuz quasi due terzi del loro GNL (IEA).

Fonte, salvo dove indicato: [`paesi.json`](../docs/data/paesi.json) (UN Comtrade 2025).

### Unione europea

- Esposizione diretta bassa sul greggio (Germania 4,0–5,8%, Francia 6,5–8,7%, Paesi Bassi 8,1–9,4%, Spagna 4,3–10,3%), ma piena sul prezzo.
- Gas: circa il 7% del GNL arrivato in Europa passava da Hormuz (IEA). I carichi da Qatar ed Emirati sono calati di oltre 60 miliardi di m³ tra marzo e ottobre ([IEA](https://www.iea.org/reports/global-gas-security-review-2026/executive-summary)).
- Stoccaggi all'8 novembre (GIE AGSI+, [`scorte.json`](../docs/data/scorte.json)): Germania al 58,9% (74,9% un anno prima, 88,6% la media di cinque anni), Paesi Bassi 63,5%, Austria 64,3%, Francia 80,8%. Il dato aggregato dell'UE non è stato scaricato dallo script; secondo dati AGSI ripresi da [oenergetice.cz](https://oenergetice.cz/en/natural-gas/eu-gas-storage-is-less-than-three-quarters-full-how-much-will-be-left-after-winter) l'UE era al 74,6% il 1° novembre, lontana dall'obiettivo del 90%.
- Gasolio: le scorte di distillati USA sono a −13% sulla media di cinque anni (EIA); i distillati del Golfo passano da Hormuz. *Valutazione:* è un rischio per il gasolio europeo in inverno.

### Italia

**Greggio: esposizione diretta bassa.** Dal Golfo arriva tra il 5,6% e il 10,2% del greggio importato (UN Comtrade 2025). I primi fornitori sono Libia (24,5%), Azerbaigian (15,9%, via Ceyhan) e Kazakistan (12,5%, terminale CPC sul Mar Nero e Bosforo) ([`paesi.json`](../docs/data/paesi.json)). *Valutazione:* per il greggio italiano contano più Libia, Mar Nero e Turchia che Hormuz; il terminale CPC è stato colpito da droni più volte nel 2026 ([`energia.md`](agenti/energia.md)).

**Scorte petrolifere: sotto soglia.** 77,2 giorni ad agosto 2026, contro 90,5 un anno prima; sotto i circa 90 giorni della direttiva 2009/119/CE, verosimilmente per i rilasci coordinati (Eurostat, [`scorte.json`](../docs/data/scorte.json)).

**Gas: la dipendenza maggiore.**

![Ingressi di gas in Italia](grafici/gas.svg)
*Quota di ogni punto di ingresso sul gas entrato da gasdotti e GNL, 8 novembre 2025 – 8 novembre 2026. Fonte: ENTSOG, dati Snam, [`gas-italia.json`](../docs/data/gas-italia.json).*

- Il **TransMed** da Mazara del Vallo (Algeria via Tunisia) porta il 34,0% degli ingressi, 220,5 TWh in 12 mesi. Attraversa il Canale di Sicilia in un solo corridoio di condotte parallele, senza alternativa per quel gas. A settembre il flusso è sceso a 11,3 TWh nel mese, contro 16,9 ad agosto e 20,2 a ottobre; la causa non è documentata nel dato.
- Il **TAP** (Azerbaigian) porta il 16,5% e a ottobre 2026 ha toccato il massimo mensile del periodo.
- Il **GNL** pesa in tutto per circa un terzo (Adriatic LNG 14,1%, Piombino 6,9%, OLT Livorno 6,7%, Ravenna 3,5%, Panigaglia 1,5%). Nel 2025 il GNL italiano veniva per il 45,3% dagli Stati Uniti e per il 32,6% dal Qatar (UN Comtrade, quote in valore); nel 2024 il Qatar era al 45% ([BISI](https://bisi.org.uk/reports/how-do-disruptions-in-the-hormuz-strait-affect-europe-a-spotlight-on-italy)). Adriatic LNG è il terminale dove arrivava il GNL qatarino di Edison, oggi in forza maggiore ([gasworld](https://www.gasworld.com/story/qatarenergy-extends-lng-force-majeure-on-edison-cargoes-to-end-december/2262726.article/)): l'origine dei carichi arrivati nel 2026 **manca** (servirebbero dati Kpler o GIIGNL).
- **Stoccaggi:** l'Italia ha superato il 90% il 20 ottobre, ha toccato il 91,1% il 31 ottobre e l'8 novembre, con l'erogazione invernale già cominciata, è all'88,9% (180,9 TWh), contro il 93,7% di un anno prima (GIE AGSI+, [`scorte.json`](../docs/data/scorte.json)). È molto meglio della Germania (58,9%).

*Valutazione:* l'Italia è più protetta di altri paesi europei sui volumi, grazie ad Algeria, TAP e cinque rigassificatori, ma paga il gas al prezzo europeo (TTF e PSV). Il peggior scenario di approvvigionamento non è Hormuz ma un danno al TransMed: è il caso di impatto più alto, non il più probabile (nel cruscotto del rischio il TransMed è a livello «basso», 5,6 su 25, [`rischio.json`](../docs/data/rischio.json)).

**Porti.** Settimana 24–30 ottobre contro un anno prima (PortWatch): Ravenna −40% di chiamate (petroliere −50%), Venezia Lido −38%, Trieste −13% (petroliere −24%), Genova −4%, Livorno −3%, Gioia Tauro +2%, Augusta +15% (petroliere +33%) ([`portwatch.json`](../docs/data/portwatch.json)). Su sette giorni i numeri sono piccoli. *Valutazione:* i cali più forti sono nei porti dell'energia dell'Adriatico (Trieste serve l'oleodotto TAL verso Austria e Germania); i porti container tengono. Il ritorno a Suez è una buona notizia per Gioia Tauro, Genova e Trieste, che con la rotta del Capo perdevano terreno rispetto a Tanger Med e al Nord Europa. A gennaio 2024 Confartigianato stimava 8,8 miliardi di euro di commercio estero perso nei primi tre mesi della crisi del Mar Rosso, novembre 2023–gennaio 2024 ([LaPresse](https://www.lapresse.it/economia/2024/01/25/mar-rosso-88-miliardi-di-danni-per-commercio-italiano-in-3-mesi/); stima, affidabilità bassa).

**Cavi.** Tutti i 6 cavi attivi che collegano direttamente l'Italia all'Asia passano dal Mar Rosso e dall'Egitto: 2Africa (Genova), AAE-1 (Bari), SeaMeWe-4 (Palermo), SeaMeWe-5 e IMEWE (Catania), MENA/GBI (Mazara). Tre (AAE-1, SeaMeWe-4, IMEWE) sono stati danneggiati negli incidenti del 2024–2025. A Hormuz nessun taglio confermato nel 2026, ma tutti i progetti di cavi nel Golfo sono rinviati (TeleGeography, [`cavi.md`](agenti/cavi.md)). *Valutazione:* il rischio per l'Italia è di capacità e latenza verso Asia e Golfo, non di isolamento.

---

## 7. Scenari per i prossimi tre mesi (novembre 2026 – febbraio 2027)

> **Questa sezione è una valutazione dell'osservatorio**, non una previsione con probabilità calcolate. Gli scenari servono a sapere che cosa guardare. Le soglie sono ancorate ai dati di questo report e sono le stesse del cruscotto del rischio ([`rischio.json`](../docs/data/rischio.json)), dove al 9 novembre sono attivi tutti i segnali dello scenario B e nessuno dello scenario A.

| | A. Riapertura negoziata | B. Stallo armato | C. Il Mar Rosso si chiude |
|---|---|---|---|
| **Cosa succede** | Il piano portato dal Qatar porta a una riapertura graduale e a una sospensione del blocco USA, come a giugno. | Continuano attacchi sporadici e blocco; passa solo chi naviga al buio. | Un attacco riuscito a una petroliera saudita a Bab el-Mandeb o a Yanbu, o un nuovo stop dell'Est-Ovest. |
| **Hormuz (PortWatch, media 7 g)** | sopra 20 navi al giorno per due settimane di fila (a giugno si arrivò a 51 in un giorno) | sotto 10 | sotto 5 |
| **Hormuz (LLI, a settimana)** | sopra 150 | 100–130 | in calo sotto 100 |
| **Bab el-Mandeb e Suez (PortWatch)** | stabili o in crescita | Bab el-Mandeb 25–30, Suez oltre 40 | Bab el-Mandeb sotto 20; Suez sotto 35; primo avviso UKMTO nel Mar Rosso dal 24 agosto |
| **Brent** | sotto 85 $ (minimo della guerra 71,57 il 1° luglio) | 90–115 $ | sopra 118,35 $, la massima chiusura del 2026 |
| **TTF** | sotto 70 €/MWh, ma frenato dalle scorte basse | 75–105 €/MWh, con picchi se fa freddo | sopra 103,94 €/MWh, il massimo dell'anno |
| **Noli container** | in calo (WCI sotto 4.000 $) | stabili intorno a 4.400 $ | nuovo rialzo; Shanghai–Genova sopra 5.000 $ |
| **GNL del Qatar** | annuncio di fine della forza maggiore | forza maggiore prorogata oltre dicembre | navi qatariote colpite di nuovo |
| **Banche centrali** | BCE ferma, poi dibattito sui tagli | BCE ferma con tono restrittivo | nuovo rialzo BCE e BoE nel 1° trimestre 2027 |
| **Italia** | bollette in calo con ritardo; stoccaggi meno sotto pressione | inverno costoso ma coperto sui volumi | rischio sul gasolio e sui container; Mazara e TAP decisivi |

*Valutazione sull'equilibrio tra gli scenari:* lo scenario B è il punto di partenza, perché descrive gli ultimi quattro mesi. Lo scenario A ha ora una strada concreta, il piano mediato dal Qatar, ma la tregua di aprile e il memorandum di giugno sono già falliti: un annuncio non basta, conta il dato di PortWatch per due settimane. Lo scenario C è il meno probabile ma il più costoso, perché toglierebbe l'unica uscita di massa rimasta al greggio del Golfo. Anche nello scenario A il gas europeo resterebbe caro per tutto l'inverno: le scorte sono basse e due treni di Ras Laffan restano fuori servizio.

**Indicatori da controllare ogni settimana:** PortWatch (Hormuz, Bab el-Mandeb, Suez), brief di Lloyd's List Intelligence, avvisi UKMTO, Brent e TTF in chiusura, stoccaggi UE (AGSI), WCI di Drewry, comunicati di QatarEnergy e del CENTCOM.

---

## 8. Cosa guardare in agenda

Da [`calendario.json`](../docs/data/calendario.json). Orari in UTC.

| Data | Evento | Perché conta qui |
|---|---|---|
| 10 nov, 13:30 | CPI USA di ottobre | quanto la benzina spinge ancora l'inflazione; con due voti per un rialzo, un dato alto riapre il rialzo Fed a dicembre |
| 10 nov, 17:00 | EIA, Short-Term Energy Outlook | stime su Brent e flussi dagli stretti |
| 12 nov, 17:00 | EIA, scorte settimanali di petrolio (spostate per il Veterans Day) | SPR e distillati |
| 13 nov, 09:00 | IEA, Oil Market Report | stima delle perdite di offerta del Golfo |
| metà novembre | OPEC, rapporto mensile (data non confermata) | base delle quote 2027 |
| 18–19 nov | Vertice APEC a Shenzhen | domanda cinese di petrolio e GNL; incontri USA-Cina |
| 25 nov, 13:30 | PIL USA (seconda stima) e deflatore PCE di ottobre | inflazione misurata dalla Fed |
| 29 nov | OPEC+: riunione ministeriale e JMMC sulle quote 2027 | quote «teoriche» con l'export del Golfo al 60–80% |
| 1 dic, 10:00 | Inflazione dell'area euro, stima flash di novembre | prima della BCE |
| 8–9 dic | Fed, con proiezioni economiche | rialzo o attesa |
| 14–15 dic | Vertice G20 a Miami | Iran, energia |
| 17 dic | BCE e Bank of England | tassi e tono sull'energia |
| 17–18 dic | Consiglio europeo | gas, stoccaggi, sanzioni |
| fine dicembre | scadenza della proroga della forza maggiore a Ras Laffan («almeno a fine dicembre») | GNL qatarino nel 1° trimestre 2027 |
| 27 gen 2027 | Fed | |
| 4 feb 2027 | BCE e Bank of England | |

Ogni settimana: aggiornamento di IMF PortWatch (con circa una settimana di ritardo) e indici dei noli (WCI il giovedì, SCFI e CCFI il venerdì).

---

## 9. Metodo, fonti e limiti

**Metodo.** Il report usa quasi solo i dati già raccolti dagli script dell'osservatorio in [`docs/data/`](../docs/data/) e i rapporti degli agenti in [`report/agenti/`](agenti/). I fatti hanno fonte, data e link; le valutazioni sono marcate. I grafici sono generati da [`report/costruisci_grafici.py`](costruisci_grafici.py) a partire dai file JSON, senza numeri scritti a mano: per rifarli si usa `python3 report/costruisci_grafici.py`. Regole complete in [`METODO.md`](../METODO.md).

**Fonti principali.**

| Dato | Fonte | File | Data del dato |
|---|---|---|---|
| Transiti negli stretti e nei porti | IMF PortWatch (FMI e Università di Oxford), dati AIS | `portwatch.json` | 1/11/2026 |
| Prezzi di Brent, WTI, TTF, Henry Hub, oro; tassi USA | Yahoo Finance; U.S. Department of the Treasury | `prezzi.json` | 9/11/2026, 19:47 UTC (tassi 6/11; grafico: lettura delle 19:38) |
| Noli | Drewry, Freightos, Shanghai Shipping Exchange (Baltic Dry: Baltic Exchange via Trading Economics, citato a mano, non raccolto in automatico) | `noli.json` | 5–9/11/2026 |
| Rischio geopolitico | Caldara e Iacoviello, GPR | `gpr.json` | 2/11/2026 |
| Gas in Italia | ENTSOG, dati Snam Rete Gas | `gas-italia.json` | 8/11/2026 |
| Scorte | GIE AGSI+, EIA, Eurostat, USDA, FMI | `scorte.json` | agosto–8 novembre 2026 |
| Esposizione per paese | UN Comtrade, Eurostat, World Bank, FMI | `paesi.json` | 2024–2025 |
| Schede degli stretti | IEA, EIA, Howden Re, Lloyd's List Intelligence, Baker Institute, stampa | `stretti-dettaglio.json` | febbraio–novembre 2026 |
| Eventi | UKMTO, CENTCOM, agenzie, account OSINT (file dal 29/10) | `eventi.json` | 1–9/11/2026 |
| Agenda | Fed, BCE, BoE, BoJ, BLS, BEA, Eurostat, EIA, OPEC (via stampa) | `calendario.json` | 9/11/2026 |

**Limiti.**
- **I transiti sono un minimo.** PortWatch vede solo le navi con l'AIS acceso e arriva con una settimana di ritardo; Lloyd's List pubblica solo sintesi, i dati completi sono a pagamento.
- **Prezzi non ufficiali.** Le serie di Yahoo Finance sono quotazioni dei future, non prezzi ufficiali; lo script di raccolta converte le date con il fuso di New York senza ora legale, così tra l'8 marzo e il 1° novembre 2026 ogni seduta dei future (Brent, WTI, TTF, Henry Hub) risulta anticipata di un giorno, e alcune cadono di domenica. Nel testo le date sono corrette sulle sedute di Yahoo Finance; nel file e nelle etichette del grafico no. L'ultimo valore del 9 novembre è provvisorio: il Brent era a 93,65 alle 18:43 UTC, 92,58 alle 19:38 (lettura usata per il grafico) e 92,62 alle 19:47 (lettura usata nel testo). Dalle 19:56 `prezzi.json` contiene solo le sedute dal 6 agosto: rilanciare oggi lo script dei grafici produrrebbe un grafico dei prezzi più corto. I massimi in seduta (per esempio i 119 dollari di Howden Re) differiscono dalle chiusure.
- **Esposizione per paese approssimata.** Le quote Comtrade sono in valore, non in volume, e si basano sulle dichiarazioni dell'importatore: l'origine può essere mascherata.
- **Dati che mancano:** prezzo dell'urea e degli altri fertilizzanti dopo maggio 2026; premi war risk aggiornati da fonte primaria; noli delle petroliere (TD3C) recenti; inflazione italiana; aggregato UE degli stoccaggi AGSI (lo script scarica solo i singoli paesi); origine dei carichi di GNL arrivati in Italia nel 2026; volumi attuali dell'oleodotto ADCOP e dell'Est-Ovest dopo settembre; posizioni delle navi a Hormuz e nel Mar Rosso (le fonti gratuite richiedono chiavi).
- **Fonti in conflitto.** Su molti eventi di novembre (petroliere colpite, Riyadh, Bab el-Mandeb chiuso) le versioni divergono: l'affidabilità di ogni evento è indicata in `eventi.json`.

**Uso di un assistente AI.** Raccolta dei dati, scrittura degli script e prima stesura di questo testo sono state fatte con l'aiuto di un assistente AI (Claude, di Anthropic). Le fonti sono riportate punto per punto; l'impostazione, le scelte e la revisione sono dell'autore. Anche la revisione indipendente del 9 novembre (sotto) è stata fatta con un assistente AI, controllando i numeri sui file di dati e sulle fonti.

---

## Revisione

> **Data:** 9 novembre 2026, revisione indipendente contro lo [standard editoriale](STANDARD.md); aggiornata il 10 novembre (Baltic Dry, su segnalazione di un secondo revisore).
>
> **Affermazioni verificate:** 183 tra numeri e fatti datati: 135 confermate, 38 corrette, 10 non verificabili da qui (fonte a pagamento, sito non raggiungibile o dato solo nei rapporti degli agenti).
>
> **Correzioni principali:** date delle sedute di Brent e TTF (massimi il 31 marzo e il 30 ottobre, non il 30 e il 29: errore di fuso orario nello script dei prezzi); minimo della guerra del Brent 71,57 $ il 1° luglio, non 71,99 il 25 giugno; Treasury a 10 anni un anno prima 4,11%, non 4,02%; premio war risk per una nave da 100 milioni da 375.000 a 3 milioni di dollari, non solo 375.000; seconda metaniera qatarina colpita il 31 luglio vicino a Hormuz, non nel Mar Rosso; stima Confartigianato riferita ai soli primi tre mesi della crisi; avvisi UKMTO 191–200, non 194–200; finestra degli eventi di `eventi.json` (dal 29 ottobre, non 30 giorni); TransMed fatto di più condotte, non «un solo tubo»; capacità delle vie alternative riallineata all'IEA; ultimi prezzi aggiornati alla lettura delle 19:47 UTC.
>
> **Chiarezza:** «In breve» riscritto con frasi più corte e sigle spiegate; aggiunto un glossario; segnalata la coerenza con il cruscotto del rischio (TransMed: impatto alto, probabilità bassa).
>
> **Resta non verificabile:** origine dei carichi di GNL in Italia; volumi di ADCOP ed Est-Ovest dopo settembre; Kirkuk–Ceyhan a 500.000 b/g (fonti anonime); importazioni cinesi dal Medio Oriente (Kpler); calo di 60 miliardi di m³ di GNL (pagina IEA non raggiungibile); attacco a Fujairah del 14 marzo; variazione annua del Baltic Dry (il dato di 2.854 punti e +37% veniva da un CFD di Trading Economics e non da fonte primaria: sostituito il 10 novembre con 2.805 punti al 6 novembre); premio war risk attuale. Il grafico dei prezzi conserva le date anticipate di un giorno finché lo script di raccolta non è corretto. Resoconto completo in [`revisioni/hormuz-mar-rosso-2026-11.md`](revisioni/hormuz-mar-rosso-2026-11.md).

---

*Gabriele Giuliani · Monitor geoeconomico · 9 novembre 2026* · [Torna alla mappa](https://gabrielegiuliani04.github.io/monitor-geoeconomico/)
