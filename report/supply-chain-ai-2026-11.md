# La catena dell'AI, dalla miniera al data center — novembre 2026

*Dove sta ogni anello della catena dell'AI, chi lo controlla, dove si rompe.*

Gabriele Giuliani · Monitor geoeconomico · dati al 9 novembre 2026. Ogni numero ha fonte e data; le parti marcate *Valutazione* sono ragionamenti dell'osservatorio.

## Indice
- [1. In breve](#in-breve)
- [2. La catena in un colpo d'occhio](#catena)
- [3. Materie prime](#anello-materie)
- [4. Macchine per fare chip](#anello-attrezzature)
- [5. Wafer e fabbricazione](#anello-fabbricazione)
- [6. Packaging avanzato e memoria HBM](#anello-packaging-memoria)
- [7. Progetto dei chip e acceleratori](#anello-progettazione)
- [8. Server, rete e assemblaggio](#anello-server-rete)
- [9. Logistica](#anello-logistica)
- [10. Energia e data center](#anello-energia-dc)
- [11. Come si spostano le cose: i collegamenti](#collegamenti)
- [12. Paesi Bassi, Danimarca e Baltico](#nord-europa)
- [13. Scenari di rottura](#scenari)
- [14. Tutti gli indicatori e le soglie](#indicatori)
- [15. Metodo, limiti e trasparenza](#metodo)

<a id="in-breve"></a>

## 1. In breve

- **Il rischio di questa settimana è cinese.** La sospensione delle misure di ottobre 2025 su terre rare e regola dello 0,1% scade domani (10 novembre 2026) e le fonti non concordano su una proroga; il divieto di export di gallio e germanio verso gli USA torna tra 18 giorni (27 novembre 2026). La Cina fa il 99% del gallio primario e il 69,2% delle terre rare estratte ([USGS MCS 2026](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf)).
- **Tre punti unici di rottura.** Gli scanner EUV escono solo da Veldhoven (Paesi Bassi); TSMC ha il 72,5% della fonderia mondiale e fa il 2 nm solo a Taiwan; il packaging CoWoS delle GPU è quasi tutto a Tainan e Chiayi. Diversificazione in corso (Arizona, Kumamoto, Dresda) ma i wafer americani tornano a Taiwan per il packaging ([TrendForce](https://www.trendforce.com/presscenter/news/20260909-13225.html)).
- **La logistica pesa già.** A Hormuz passano 4,4 navi al giorno (−95% su un anno, [IMF PortWatch](https://portwatch.imf.org/)): l'elio del Qatar, un terzo del mondo, è in gran parte fermo da marzo. Lo Stretto di Taiwan invece è normale (247 navi al giorno, +7,1% su un anno).
- **La memoria è il nuovo collo di bottiglia.** HBM divisa tra SK Hynix 50%, Samsung 33% e Micron 18% (Counterpoint, 2° trimestre 2026); prezzi DRAM previsti +20% nel 4° trimestre ([TrendForce](https://www.trendforce.com/news/2026/10/20/news-dram-prices-seen-rising-20-qoq-in-4q26-despite-slower-gains-ai-demand)). Per la Cina l'HBM è il limite vero della produzione Huawei.
- **In borsa vincono i colli di bottiglia fisici.** Da inizio anno SK Hynix +74%, ASML +42%, indice SOX +42%; Nvidia −4,9%. Nell'ultimo mese correzione su tutto il comparto (SOX −20%; prezzi.json, 9 novembre 2026).

> *Valutazione.* La catena dell'AI è lunga ma stretta in pochi punti, e quasi tutti sono in Asia orientale o dipendono da una sola società. Per l'Europa del Nord il legame più forte è anche il più solido: le macchine EUV di Veldhoven. I punti deboli sono a monte (terre rare, gallio, elio) e a valle (energia e trasformatori), più che nei chip.

<a id="catena"></a>

## 2. La catena in un colpo d'occhio

Otto anelli, dalla miniera al data center. Ogni riquadro mostra i paesi chiave dell'anello (valutazione dell'osservatorio), quanti nodi e titoli quotati sono collegati e lo stato del collo di bottiglia peggiore. Il riquadro ha il bordo colorato quando un indicatore supera una soglia: le soglie sono una valutazione dell'osservatorio, spiegata nella sezione degli indicatori.

![Diagramma generato da docs/data/supply-chain-ai](grafici/sca-2026-11-catena.svg)

<small>Diagramma generato da docs/data/supply-chain-ai.json (70 nodi, 34 collegamenti, 13 colli di bottiglia). Passare sopra un riquadro per l'elenco dei colli.</small>

| Anello | Dove sta | Collo peggiore |
|---|---|---|
| 1. Materie prime | Cina (gallio, terre rare, fluorite, silicio), Cile e Congo (rame), Congo e Ruanda (tantalio), USA e Qatar (elio), North Carolina (quarzo), Ucraina (neon, fino al 2022). | {stato:critico} |
| 2. Macchine per fare chip | Paesi Bassi (Veldhoven), Germania (Oberkochen, Ditzingen), California (San Diego, Santa Clara, Fremont, Milpitas), Giappone (Tokyo). | {stato:critico} |
| 3. Wafer e fabbricazione | Taiwan (Hsinchu, Kaohsiung, Taichung), Arizona, Giappone (Kumamoto, Hokkaido), Corea (Pyeongtaek), Cina (Shanghai), Germania (Dresda), Irlanda. | {stato:critico} |
| 4. Packaging avanzato e memoria HBM | Taiwan (Tainan, Chiayi) per il CoWoS; Corea (Icheon, Cheongju, Onyang) per l'HBM; Giappone, Singapore e Indiana per la memoria in arrivo; Hefei per l'HBM cinese. | {stato:critico} |
| 5. Progetto dei chip e acceleratori | California (Santa Clara, Palo Alto, Mountain View), Shenzhen. | {stato:critico} |
| 6. Server, rete e assemblaggio | Taiwan (Nuova Taipei, Taoyuan), Messico (Jalisco), Texas (Houston, Dallas), Cina (Suzhou, Chengdu) per l'ottica, USA (Pennsylvania) per i laser. | {stato:critico} |
| 7. Logistica | Aeroporti di Taoyuan, Incheon, Schiphol, Anchorage, Pudong; Stretto di Taiwan, Mar Cinese Meridionale, Malacca, Hormuz. | {stato:critico} |
| 8. Energia e data center | Stati Uniti (Texas, Tennessee, Indiana, Georgia), Golfo, Malesia (Johor), Europa (Francia, Paesi del Nord, Italia); Taiwan per l'energia delle fab. | {stato:critico} |

<small>Versione in tabella del diagramma.</small>

<a id="anello-materie"></a>

## 3. Materie prime

**Dove sta.** Cina (gallio, terre rare, fluorite, silicio), Cile e Congo (rame), Congo e Ruanda (tantalio), USA e Qatar (elio), North Carolina (quarzo), Ucraina (neon, fino al 2022).

**Chi lo controlla.** Lo Stato cinese, con licenze all'export; poche società per il quarzo (Sibelco, The Quartz Corp); QatarEnergy per l'elio; gruppi armati nel Kivu per una parte del coltan.

Un chip per l'AI contiene poche decine di grammi di materiali, ma senza alcuni di essi la fabbrica si ferma. Il gallio serve ai semiconduttori di potenza e all'ottica, il germanio alla fibra, l'elio al raffreddamento dei wafer, il neon ai laser della litografia, la fluorite ai gas di incisione, il quarzo di Spruce Pine ai crogioli in cui si fonde il silicio. Rame e terre rare servono a valle: cavi, trasformatori, motori delle ventole e dei sistemi di raffreddamento, dischi rigidi.

La concentrazione è estrema e misurabile con l'ultima edizione del [USGS Mineral Commodity Summaries 2026](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026.pdf) (5 febbraio 2026, dati 2025): la tabella sotto calcola le quote dai dati di produzione per paese.

Il rischio di questa settimana sono i controlli cinesi. Le licenze su gallio e germanio (agosto 2023) e sulle sette terre rare medie e pesanti (aprile 2025) sono in vigore. Il divieto di export di gallio e germanio verso gli USA (dicembre 2024) è sospeso fino al 27 novembre 2026; le misure di ottobre 2025, compresa la regola dello 0,1% di contenuto cinese nei prodotti esteri, erano sospese fino al 10 novembre 2026. Il 9 novembre le fonti non concordano: [Tech Times](https://www.techtimes.com/articles/330288/20261109/china-rare-earth-export-controls-pause-ends-tuesday-law-beijing-has-published-no-extension.htm) scrive che nessun testo cinese sposta la data, [Shanghai Metals Market](https://news.metal.com/newscontent/CNTOCBN4QTSC2L3BEOVBYILPAZVOOIHVV6INVPY-china-extends-suspension-of-rare-earth-export-controls-until-january-2027) riporta una proroga al 10 gennaio 2027.

L'elio è il caso di scuola di un rischio logistico che diventa industriale: il Qatar fa un terzo dell'elio mondiale a Ras Laffan e da marzo 2026 la produzione è in gran parte ferma per la guerra con l'Iran e la chiusura di fatto di Hormuz ([WTOP/AP](https://wtop.com/news/2026/03/iran-war-halts-qatar-helium-output-threatening-global-tech-supply-chains/)). A giugno però [Morningstar/Dow Jones](https://www.morningstar.com/news/dow-jones/202606253275/why-the-middle-east-helium-supply-shock-didnt-hit-chip-makers) spiegava perché lo shock non aveva colpito i produttori di chip: scorte, carichi già in viaggio, elio americano.

> *Valutazione.* Per l'Europa del Nord l'anello debole sono le terre rare. Il Baltico ha l'unico tratto europeo di filiera completa fuori dalla Cina, a Sillamäe e Narva in Estonia, a pochi chilometri dal confine russo; la Groenlandia (Danimarca) ha 1,5 milioni di tonnellate di riserve ma nessuna produzione.

### Produttori e quote (USGS, dati 2025)

| Materia | A cosa serve | Primi produttori (quota) | Fonte USGS |
|---|---|---|---|
| Gallio (primario a bassa purezza) | semiconduttori composti (GaN, GaAs): elettronica di potenza degli alimentatori dei server, radiofrequenza, laser e fotodiodi per l'ottica | Cina 99,0%; Russia 0,7%; Giappone 0,3% | [Gallium](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-gallium.pdf) |
| Germanio (raffinato) | fibra ottica (tetracloruro di germanio) per le reti dei data center, ottiche infrarosse, substrati | dato mancante (USGS non pubblica una tabella mondiale: «global production data were limited») | [Germanium](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-germanium.pdf) |
| Silicio metallico (grado metallurgico, base del polisilicio) | materia di partenza del polisilicio e dei wafer di silicio | Cina 87,0%; Brasile 3,9%; Norvegia 2,8% | [Silicon](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-silicon.pdf) |
| Quarzo ad alta purezza (Spruce Pine) | crogioli in cui si fonde il silicio per tirare i lingotti dei wafer | stima: 70–90% dell'offerta mondiale di quarzo commerciale ad alta purezza da Spruce Pine (Everstream); oltre l'80% secondo BloombergNEF | [Quartz (high-purity)](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-quartz.pdf) |
| Terre rare (estrazione, ossidi equivalenti) | magneti permanenti di motori, ventole, pompe di raffreddamento e dischi rigidi; macchine di fabbrica; lucidatura (cerio) | Cina 69,2%; Stati Uniti 13,1%; Australia 7,4% | [Rare Earths](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf) |
| Rame (miniera e raffinazione) | cavi di alimentazione, sbarre, trasformatori, interconnessioni in rame dentro i rack | Cile 23,0%; Congo (RD) 13,9%; Perù 11,7% | [Copper](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-copper.pdf) |
| Tantalio (coltan) | condensatori al tantalio delle schede madri e degli alimentatori; bersagli di deposizione (sputtering) nei chip | Congo (RD) 52,0%; Ruanda 16,0%; Nigeria 15,6% | [Tantalum](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-tantalum.pdf) |
| Fluorite | acido fluoridrico e gas fluorurati per l'incisione e la pulizia dei wafer | Cina 60,0%; Messico 15,0%; Mongolia 15,0% | [Fluorspar](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-fluorspar.pdf) |
| Elio | raffreddamento dei wafer e atmosfera inerte in litografia, deposizione e incisione; nessun sostituto pratico nei processi attuali | Stati Uniti 42,6%; Qatar 33,2%; Russia 9,5% | [Helium and rare gases](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-helium.pdf) |
| Neon | miscele dei laser ad eccimeri della litografia DUV (sorgenti Cymer e Gigaphoton) | Stati Uniti 13,8% | [Helium and rare gases](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-helium.pdf) |

<small>Quote calcolate da raccogli.py come produzione del paese / totale mondiale USGS (stime 2025); per il gallio la quota è quella dichiarata da USGS. Rame: estrazione; la Cina raffina il 48,3% del rame mondiale.</small>

![Quota del primo paese produttore](grafici/sca-2026-11-concentrazione.svg)

<small>Quota del primo paese produttore. Fonte: [USGS Mineral Commodity Summaries 2026](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026.pdf), 5 febbraio 2026.</small>

### Controlli cinesi all'export, 2023–2026

| Annuncio | Misura | Stato al 9 novembre 2026 | Fonte |
|---|---|---|---|
| 3 luglio 2023 | Licenza obbligatoria per esportare gallio e germanio e loro composti. | in-vigore | [USGS, Mineral Commodity Summaries 2026: Gallium](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-gallium.pdf) |
| 3 dicembre 2024 | Divieto di export verso gli USA di gallio, germanio, antimonio e materiali superduri. | sospeso fino al 27 novembre 2026 (tra 18 giorni) | [Fastmarkets, «China suspends export prohibition on gallium, germanium, antimony, superhard materials to US»](https://www.fastmarkets.com/insights/china-suspends-export-prohibition-on-superhard-materials-us/) |
| 4 aprile 2025 | Licenze su sette terre rare medie e pesanti: samario, gadolinio, terbio, disprosio, lutezio, scandio, ittrio (e relativi magneti). | in-vigore | [USGS, Mineral Commodity Summaries 2026: Rare Earths](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf) |
| 9 ottobre 2025 | Altre cinque terre rare (olmio, erbio, tulio, europio, itterbio); regola extraterritoriale dello 0,1% di contenuto cinese nei prodotti esteri; tecnologie ed impianti per estrazione, separazione e magneti; batterie e materiali superduri. | incerto fino al 10 novembre 2026 (tra 1 giorno) | [Tech Times, «China Rare Earth Export Controls Pause Ends Tuesday in Law; Beijing Has Published No Extension»](https://www.techtimes.com/articles/330288/20261109/china-rare-earth-export-controls-pause-ends-tuesday-law-beijing-has-published-no-extension.htm) |

<small>Per le misure di ottobre 2025 le fonti del 9 novembre 2026 sono in disaccordo: vedi il testo sopra.</small>

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| Spruce Pine (North Carolina): quarzo ad alta purezza | Stati Uniti | quarzo per i crogioli dei lingotti di silicio | 70–90% del quarzo commerciale ad alta purezza (stima Everstream); oltre 80% (BloombergNEF) | [BNN Bloomberg, «Hurricane Helene halts quartz mines vital for chipmaking and solar»](https://bnnbloomberg.ca/investing/commodities/2024/10/02/hurricane-helene-halts-quartz-mines-vital-for-chipmaking-and-solar), 2024-10-02 (media) |
| Bayan Obo (Mongolia Interna): terre rare | Cina | prima miniera di terre rare della Cina | Cina 69,2% di terre rare nel 2025 (calcolata da USGS, Mineral Commodity Summaries 2026) | [USGS, Mineral Commodity Summaries 2026: Rare Earths](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf), 2026-02-05 (media) |
| Mountain Pass (California): terre rare | Stati Uniti | unica miniera di terre rare degli USA | Stati Uniti 13,1% di terre rare nel 2025 (calcolata da USGS, Mineral Commodity Summaries 2026) | [USGS, Mineral Commodity Summaries 2026: Rare Earths](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf), 2026-02-05 (media) |
| Rubaya (Nord Kivu, Congo): coltan | Congo (RD) | tantalio per condensatori e bersagli di deposizione | circa 15% della produzione mondiale di coltan (stampa di settore) | [Argus Media, «Rubaya mine collapse and the tantalum supply chain»](https://www.argusmedia.com/en/news-and-insights/market-opinion-and-analysis-blog/rubaya-mine-collapse-tantalum-supply-chain), 2026-02-12 (media) |
| Ras Laffan (Qatar): elio dal gas naturale | Qatar | secondo produttore mondiale di elio | Qatar 33,2% di elio nel 2025 (calcolata da USGS, Mineral Commodity Summaries 2026) | [WTOP (AP), «Iran war halts Qatar helium output, threatening global tech supply chains»](https://wtop.com/news/2026/03/iran-war-halts-qatar-helium-output-threatening-global-tech-supply-chains/), 2026-03 (alta) |
| Odesa (Ucraina): purificazione del neon | Ucraina | neon per i laser della litografia DUV | Ucraina circa 50% del neon mondiale nel 2022 (USITC) | [USITC, Executive Briefing on Trade «Ukraine, neon, and semiconductors»](https://www.usitc.gov/publications/332/executive_briefings/ebot_decarlo_goodman_ukraine_neon_and_semiconductors.pdf), 2022 (media) |
| Mariupol (Ucraina occupata): neon | Ucraina | ex fornitore di neon per chip | — | [USITC, Executive Briefing on Trade «Ukraine, neon, and semiconductors»](https://www.usitc.gov/publications/332/executive_briefings/ebot_decarlo_goodman_ukraine_neon_and_semiconductors.pdf), 2022 (media) |
| Sillamäe (Estonia): separazione di terre rare | Estonia | separazione di terre rare leggere e, dal 2026, pesanti (terbio, disprosio) | — | [Shanghai Metals Market, «Neo Performance Materials Commissions Rare Earth Extraction Line in Estonia»](https://news.metal.com/newscontent/103853488-Neo-Performance-Materials-Commissions-Rare-Earth-Extraction-Line-in-Estonia-Strengthening-European-Supply-Chain), 2026-04 (media) |
| Narva (Estonia): magneti di terre rare | Estonia | fabbrica di magneti NdFeB, la prima di questa scala in Europa | 2.000 t/anno di capacità iniziale, poi 5.000 | [Shanghai Metals Market, «Neo Performance opens Europe's first rare earth magnet plant»](https://news.metal.com/newscontent/103541038/Neo-Performance-opens-Europe%E2%80%99s-first-rare-earth-magnet-plant), 2025-09 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Colli di bottiglia e indicatori

| Collo | Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte |
|---|---|---|---|---|---|
| Controlli cinesi su terre rare, gallio e germanio | Giorni alla fine della sospensione delle misure di ottobre 2025 (terre rare, regola dello 0,1%) | 1 giorni | 60 / 14 giorni | {stato:critico} | [Tech Times, «China Rare Earth Export Controls Pause Ends Tuesday in Law; Beijing Has Published No Extension»](https://www.techtimes.com/articles/330288/20261109/china-rare-earth-export-controls-pause-ends-tuesday-law-beijing-has-published-no-extension.htm), 2026-11-09 |
| Controlli cinesi su terre rare, gallio e germanio | Giorni alla fine della sospensione del divieto di export di gallio e germanio verso gli USA | 18 giorni | 60 / 14 giorni | {stato:attenzione} | [Fastmarkets, «China suspends export prohibition on gallium, germanium, antimony, superhard materials to US»](https://www.fastmarkets.com/insights/china-suspends-export-prohibition-on-superhard-materials-us/), 2026-11-09 |
| Controlli cinesi su terre rare, gallio e germanio | Quota cinese dell'estrazione di terre rare | 69,2 % | 40 / 60 % | {stato:critico} | [USGS, Mineral Commodity Summaries 2026: Rare Earths](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf), 2026-02-05 |
| Elio del Qatar bloccato a Hormuz | Transiti a Hormuz, media 7 giorni rispetto a un anno prima | -95,1 % | -20 / -50 % | {stato:critico} | [IMF PortWatch (portwatch.json)](https://portwatch.imf.org/), 2026-11-01 |
| Elio del Qatar bloccato a Hormuz | Quota del Qatar nella produzione mondiale di elio | 33,2 % | 20 / 30 % | {stato:critico} | [USGS, Mineral Commodity Summaries 2026: Helium and rare gases](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-helium.pdf), 2026-02-05 |
| Quarzo ad alta purezza di Spruce Pine | Quota stimata di Spruce Pine nell'offerta di quarzo ad alta purezza (stima BloombergNEF: oltre l'80%) | 80 % | 50 / 75 % | {stato:critico} | [BNN Bloomberg (BloombergNEF)](https://bnnbloomberg.ca/investing/commodities/2024/10/02/hurricane-helene-halts-quartz-mines-vital-for-chipmaking-and-solar), 2024-10-02 |
| Tantalio dal Kivu e dal Ruanda | Quota di Congo e Ruanda nell'estrazione di tantalio | 68,0 % | 40 / 60 % | {stato:critico} | [USGS, Mineral Commodity Summaries 2026: Tantalum](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-tantalum.pdf), 2026-02-05 |

**Controlli cinesi su terre rare, gallio e germanio.** La Cina fa il 99% del gallio primario e il 69% delle terre rare estratte; le licenze di aprile 2025 restano, le misure di ottobre 2025 e il divieto verso gli USA sono solo sospesi.

**Elio del Qatar bloccato a Hormuz.** Il Qatar fa un terzo dell'elio mondiale da Ras Laffan; dal 2 marzo 2026 Hormuz è chiuso di fatto. Le fab hanno scorte, ma l'elio non ha sostituti nel raffreddamento dei wafer.

**Quarzo ad alta purezza di Spruce Pine.** Due impianti in una sola valle della North Carolina forniscono la maggior parte del quarzo per i crogioli; l'uragano Helene li ha fermati nel 2024.

**Tantalio dal Kivu e dal Ruanda.** Congo e Ruanda fanno la maggior parte del tantalio estratto; la miniera di Rubaya è in mano al gruppo M23 da aprile 2024.

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| MP Materials (MP) | terre rare USA (Mountain Pass) | non seguito | — | — | — |
| Lynas Rare Earths (LYC.AX) | terre rare fuori dalla Cina (Australia, Malesia) | non seguito | — | — | — |
| Freeport-McMoRan (FCX) | rame | non seguito | — | — | — |

<small>Prezzi da prezzi.json (Yahoo Finance, chiusure al 9 novembre 2026; * = serie provvisoria). «non seguito»: titolo non ancora in prezzi.json.</small>

**Indicatori da seguire:** Annunci MOFCOM sulle sospensioni (10 novembre e 27 novembre 2026); Tassi di approvazione delle licenze cinesi e dati doganali di export di terre rare, gallio, germanio; Transiti a Hormuz (PortWatch) e stato di Ras Laffan; Stagione degli uragani in North Carolina (giugno–novembre); Notizie su Rubaya e sul Kivu (M23).

<a id="anello-attrezzature"></a>

## 4. Macchine per fare chip

**Dove sta.** Paesi Bassi (Veldhoven), Germania (Oberkochen, Ditzingen), California (San Diego, Santa Clara, Fremont, Milpitas), Giappone (Tokyo).

**Chi lo controlla.** ASML per la litografia (unico fornitore EUV), Applied Materials, Lam Research, KLA e Tokyo Electron per il resto; i governi di USA, Paesi Bassi e Giappone con le licenze.

È l'anello in cui l'Europa conta di più, e il legame più diretto con l'area di lavoro di questo osservatorio: **ogni scanner EUV del mondo esce da Veldhoven**, vicino a Eindhoven. Dentro ci sono le ottiche di Carl Zeiss SMT (Oberkochen, ASML ne possiede il 24,9%), il laser CO2 di Trumpf (Ditzingen) e la sorgente di luce di Cymer, società di ASML a San Diego ([The Value Edge](https://thevalueedge.substack.com/p/asmls-supply-chain-bill-of-materials)). La catena delle EUV attraversa quindi Paesi Bassi, Germania e Stati Uniti prima di arrivare a Taiwan, Corea, Giappone e Arizona.

Nel 3° trimestre 2026 ASML ha venduto 113 sistemi nuovi e 11,7 miliardi di euro, con una guida 2026 di 44–45 miliardi ([comunicato ASML, 14 ottobre 2026](https://seekingalpha.com/pr/20684919)). La Cina compra solo DUV e pesa circa il 20% delle vendite dell'anno secondo la guida del direttore finanziario.

I controlli si sono stratificati: USA ottobre 2022 e ottobre 2023; Paesi Bassi dal 1° settembre 2023 e dal 7 settembre 2024 per le DUV a immersione 1970i e 1980i; Giappone dal 23 luglio 2023 per 23 tipi di macchine; USA 2 dicembre 2024 per 24 tipi di macchine, l'HBM e 140 entità ([BIS](https://www.bis.gov/press-release/commerce-strengthens-export-controls-restrict-chinas-capability-produce-advanced-semiconductors-military)). Nel 2026 il fronte aperto è l'assistenza alle macchine già installate in Cina, che l'Aia ancora permette, e la proposta americana (MATCH Act) di obbligare gli alleati ad allinearsi ([Bits&Chips](https://bits-chips.com/article/dutch-minister-pushes-back-on-us-bid-to-tighten-china-chip-controls/)).

> *Valutazione.* Un blocco dell'EUV è il colpo più grave per la catena, ma è anche il più improbabile perché tocca Paesi alleati. Il rischio concreto per Veldhoven è politico e commerciale (regole sulle DUV e sui servizi in Cina), non fisico.

### Regole sull'export di macchine e chip (USA, Paesi Bassi, Giappone)

| Paese | Dal | Misura | Stato | Fonte |
|---|---|---|---|---|
| Stati Uniti | 7 ottobre 2022 | Prime regole su chip avanzati per l'AI e macchine per produrre chip avanzati in Cina; aggiornate nell'ottobre 2023. | in-vigore | [CSIS, «Understanding the Biden Administration's Updated Export Controls»](https://www.csis.org/analysis/understanding-biden-administrations-updated-export-controls) |
| Giappone | 23 luglio 2023 | 23 tipi di macchine per chip (pulizia, deposizione, trattamento termico, esposizione, incisione, ispezione, comprese parti EUV) sotto licenza fuori dai 42 paesi «amici». | in-vigore | [Hogan Lovells (HLC), «Japan's new chip equipment export rules take effect»](https://www.hlc.com/en/publications/japans-new-chip-equipment-export-rules-take-effect) |
| Paesi Bassi | 1 settembre 2023 | Licenza nazionale per esportare fuori dall'UE le macchine litografiche DUV a immersione più avanzate. | in-vigore | [Hogan Lovells (HLC), «Japan's new chip equipment export rules take effect» (cita le misure olandesi del 30 giugno 2023)](https://www.hlc.com/en/publications/japans-new-chip-equipment-export-rules-take-effect) |
| Paesi Bassi | 7 settembre 2024 | Licenza olandese anche per i sistemi DUV a immersione NXT:1970i e 1980i (prima sotto regole USA). | in-vigore | [Export Compliance Daily](https://exportcompliancedaily.com/article/2024/09/10/netherlands-expands-chip-equipment-controls-asml-expects-no-impact-2409090024) |
| Stati Uniti | 2 dicembre 2024 | Controlli su 24 tipi di macchine per chip e 3 software, su tutta la memoria HBM in produzione; 140 entità aggiunte alla Entity List. | in-vigore | [BIS, comunicato «Commerce Strengthens Export Controls to Restrict China's Capability to Produce Advanced Semiconductors for Military Applications»](https://www.bis.gov/press-release/commerce-strengthens-export-controls-restrict-chinas-capability-produce-advanced-semiconductors-military) |
| Stati Uniti | 29 settembre 2025 | «Affiliates Rule»: le società possedute al 50% o più da entità in lista subiscono gli stessi limiti. | sospeso fino al 10 gennaio 2027 | [Tech Times (regola BIS pubblicata nel Federal Register il 9 novembre 2026, FR Doc. 2026-22793)](https://www.techtimes.com/articles/330288/20261109/china-rare-earth-export-controls-pause-ends-tuesday-law-beijing-has-published-no-extension.htm) |
| Stati Uniti | 2026 | Obbligherebbe gli alleati ad allineare i controlli a quelli USA entro 150 giorni: potrebbe toccare vendite e assistenza delle DUV ASML già in Cina. | proposto | [Bits&Chips, «Dutch minister pushes back on US bid to tighten China chip controls»](https://bits-chips.com/article/dutch-minister-pushes-back-on-us-bid-to-tighten-china-chip-controls/) |
| Stati Uniti | 2026-01 | Licenze per vendere Nvidia H200 alla Cina con condizioni: verifica di laboratorio negli USA, dazio del 25%, tetti per cliente; Blackwell e Rubin esclusi. | in-vigore | [TechRepublic, «US Approves Nvidia H200 Sales to China, But Shipments Remain Stalled»](https://www.techrepublic.com/article/news-nvidia-h200-ai-chip-sales-china-stalled/) |

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| ASML, Veldhoven (Paesi Bassi): scanner EUV | Paesi Bassi | unico produttore al mondo di macchine litografiche EUV; assemblaggio finale | 100% delle EUV; Cina circa 20% delle vendite ASML 2026 (guida del direttore finanziario, solo DUV) | [ASML, risultati del 3° trimestre 2026 (comunicato)](https://seekingalpha.com/pr/20684919), 2026-10-14 (alta) |
| Carl Zeiss SMT, Oberkochen (Germania): ottiche EUV | Germania | specchi multistrato dell'ottica EUV | fornitore unico delle ottiche EUV di ASML | [The Value Edge, «ASML's Supply Chain, Bill of Materials...»](https://thevalueedge.substack.com/p/asmls-supply-chain-bill-of-materials), 2025 (media) |
| Trumpf, Ditzingen (Germania): laser CO2 per EUV | Germania | laser di potenza che vaporizza le gocce di stagno della sorgente EUV | fornitore unico del laser della sorgente EUV | [The Value Edge, «ASML's Supply Chain, Bill of Materials...»](https://thevalueedge.substack.com/p/asmls-supply-chain-bill-of-materials), 2025 (media) |
| Cymer, San Diego (California): sorgenti di luce | Stati Uniti | modulo sorgente EUV e laser ad eccimeri DUV (usano neon) | — | [The Value Edge, «ASML's Supply Chain, Bill of Materials...»](https://thevalueedge.substack.com/p/asmls-supply-chain-bill-of-materials), 2025 (media) |
| Applied Materials, Santa Clara (California) | Stati Uniti | deposizione, incisione, impianto ionico, ispezione | Cina circa il 35% delle vendite nel trimestre maggio–luglio 2025 | [TipRanks, «Applied Materials stock slides after warning of $600M revenue hit from new U.S. export rules»](https://www.tipranks.com/news/applied-materials-stock-amat-slides-after-warning-of-600m-revenue-hit-from-new-u-s-export-rules), 2025-10-02 (media) |
| Lam Research, Fremont (California) | Stati Uniti | incisione e deposizione (chiave per HBM e memoria 3D) | — | [TipRanks (reazione dei titoli alla Affiliates Rule)](https://www.tipranks.com/news/applied-materials-stock-amat-slides-after-warning-of-600m-revenue-hit-from-new-u-s-export-rules), 2025-10-02 (media) |
| KLA, Milpitas (California) | Stati Uniti | ispezione e metrologia dei wafer | — | [TipRanks (reazione dei titoli alla Affiliates Rule)](https://www.tipranks.com/news/applied-materials-stock-amat-slides-after-warning-of-600m-revenue-hit-from-new-u-s-export-rules), 2025-10-02 (media) |
| Tokyo Electron, Tokyo (Giappone) | Giappone | deposizione, rivestimento e sviluppo del resist (coater/developer), incisione | — | [Hogan Lovells (HLC), regole giapponesi del 2023](https://www.hlc.com/en/publications/japans-new-chip-equipment-export-rules-take-effect), 2023-07 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Colli di bottiglia e indicatori

| Collo | Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte |
|---|---|---|---|---|---|
| Litografia EUV: un solo fornitore, in Olanda | Fornitori di scanner EUV al mondo | 1 fornitori | 2 / 1 fornitori | {stato:critico} | [ai-mondo.json (ASML, fornitore unico al mondo di scanner EUV)](https://statementdog.com/analysis/ASML/earnings_calls/316926), 2026-07 |
| Litografia EUV: un solo fornitore, in Olanda | Quota della Cina nelle vendite ASML 2026 (guida) | 20 % | 25 / 40 % | {stato:normale} | [XenoSpectrum / Seeking Alpha sui risultati ASML del 3° trimestre 2026 (guida del direttore finanziario Roger Dassen)](https://xenospectrum.com/en/asml-china-sales-q3-2026/), 2026-10-14 |
| Litografia EUV: un solo fornitore, in Olanda | ASML in borsa, variazione a 1 mese | -14,7 % | -10 / -25 % | {stato:attenzione} | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/ASML), 2026-11-09 |

**Litografia EUV: un solo fornitore, in Olanda.** Ogni chip AI avanzato passa da scanner EUV costruiti solo a Veldhoven, con ottiche da Oberkochen e laser da Ditzingen. Gli USA spingono per estendere i limiti alle DUV e all'assistenza in Cina.

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| ASML (ASML) | litografia EUV e DUV (Veldhoven) | 1.518,30 USD * | −15% | +42% | +49% |
| Applied Materials (AMAT) | deposizione, incisione | non seguito | — | — | — |
| Lam Research (LRCX) | incisione e deposizione | non seguito | — | — | — |
| KLA (KLAC) | ispezione e metrologia | non seguito | — | — | — |
| Tokyo Electron (8035.T) | deposizione, coater/developer, incisione | non seguito | — | — | — |
| Indice dei semiconduttori (PHLX SOX) (SOX) | termometro dell'intera filiera dei chip | 10.046 USD * | −20% | +42% | +45% |

<small>Prezzi da prezzi.json (Yahoo Finance, chiusure al 9 novembre 2026; * = serie provvisoria). «non seguito»: titolo non ancora in prezzi.json.</small>

**Indicatori da seguire:** Ordini e quota Cina nei conti trimestrali ASML (prossimi a gennaio 2027); Testo e iter del MATCH Act; decisioni del governo olandese sulle licenze di assistenza; Elenco BIS delle entità e regola sulle affiliate (sospesa fino al 10 gennaio 2027).

<a id="anello-fabbricazione"></a>

## 5. Wafer e fabbricazione

**Dove sta.** Taiwan (Hsinchu, Kaohsiung, Taichung), Arizona, Giappone (Kumamoto, Hokkaido), Corea (Pyeongtaek), Cina (Shanghai), Germania (Dresda), Irlanda.

**Chi lo controlla.** TSMC, con distacco; poi Samsung, SMIC e Intel; Rapidus come progetto statale giapponese.

TSMC ha avuto il 72,5% dei ricavi mondiali di fonderia nel 2° trimestre 2026, Samsung il 5,9%, SMIC il 5,4% ([TrendForce, 9 settembre 2026](https://www.trendforce.com/presscenter/news/20260909-13225.html)). Sui nodi avanzati la concentrazione è più forte: il 2 nm è in volume solo a Hsinchu e Kaohsiung dalla fine del 2025, e i chip AI di Nvidia, AMD, Broadcom e Google escono da linee TSMC a 3–4 nm. Quote per nodo da fonte verificata: non trovate.

La diversificazione è reale ma lenta. In Arizona TSMC produce a 4 nm, il 3 nm arriverà nel 2° semestre 2027 e il piano è salito a 265 miliardi di dollari ([BetaNews](https://betanews.com/article/tsmc-100-billion-arizona-chip-expansion/)); però i wafer americani tornano a Taiwan per il packaging. In Europa ESMC a Dresda farà chip da 28–12 nm per l'auto, non per l'AI, e i macchinari arriveranno solo nel 2° semestre 2027.

SMIC produce a 7 nm senza EUV i chip Huawei; i suoi ricavi sono cresciuti del 20% nel trimestre. Nexperia (Nijmegen) mostra l'altro lato del rischio europeo: un intervento statale olandese a settembre 2025 ha diviso la società in due, con la parte cinese a Dongguan.

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| TSMC Fab 20, Hsinchu (Baoshan): 2 nm | Taiwan | nodo più avanzato in volume al mondo | TSMC 72,5% dei ricavi mondiali di fonderia nel 2° trimestre 2026 | [TrendForce, classifica fonderie 2° trimestre 2026](https://www.trendforce.com/presscenter/news/20260909-13225.html), 2026-09-09 (alta) |
| TSMC Fab 22, Kaohsiung: 2 nm | Taiwan | seconda sede del 2 nm | — | [TrendForce](https://www.trendforce.com/news/2026/02/23/news-tsmc-speeds-up-expansion-in-taiwan-up-to-10-fabs-reportedly-under-construction-or-starting-in-2026/), 2026-02-23 (alta) |
| TSMC Arizona Fab 21, Phoenix | Stati Uniti | 4 nm in produzione; 3 nm dal 2° semestre 2027 | — | [BetaNews, «TSMC adds $100 billion to Arizona plan»](https://betanews.com/article/tsmc-100-billion-arizona-chip-expansion/), 2026-07 (alta) |
| TSMC-JASM, Kumamoto (Giappone) | Giappone | 12–28 nm, poi 3 nm | — | [Remio](https://www.remio.ai/post/tsmc-kumamoto-3nm-fab-approved-but-japan-is-trading-volume-for-advanced-chips), 2026 (media) |
| ESMC (TSMC), Dresda (Germania) | Germania | 28–12 nm per auto e industria, non per GPU | — | [Focus Taiwan](https://focustaiwan.tw/business/202609150007), 2026-09-15 (alta) |
| Samsung, Pyeongtaek (Corea) | Corea del Sud | fonderia 2 nm e DRAM per HBM | Samsung 5,9% della fonderia mondiale nel 2° trimestre 2026 | [TrendForce, classifica fonderie 2° trimestre 2026](https://www.trendforce.com/presscenter/news/20260909-13225.html), 2026-09-09 (alta) |
| Samsung, Taylor (Texas) | Stati Uniti | fonderia avanzata negli USA | — | [TrendForce News](https://www.trendforce.com/news/?p=42788), 2025-07-28 (bassa) |
| Intel Fab 52, Ocotillo (Arizona): 18A | Stati Uniti | nodo avanzato di Intel | — | [Telepolis (cita CNBC)](https://www.telepolis.pl/tech/intel-tsmc-usa-produkcja-ukladow-polprzewodnikowych), 2026-11-09 (media) |
| Intel Fab 34, Leixlip (Irlanda) | Irlanda | unica fabbrica EUV di Intel in Europa | — | [Tom's Hardware](https://www.tomshardware.com/tech-industry/intel-commits-5-7-billion-to-ireland-one-year-after-cancelling-its-german-and-polish-fab-projects), 2026 (alta) |
| SMIC, Shanghai: 7 nm senza EUV | Cina | produce i chip Huawei Ascend | SMIC 5,4% della fonderia mondiale nel 2° trimestre 2026 (+20% di ricavi sul trimestre) | [TrendForce, classifica fonderie 2° trimestre 2026](https://www.trendforce.com/presscenter/news/20260909-13225.html), 2026-09-09 (alta) |
| Rapidus IIM-1, Chitose (Hokkaido) | Giappone | 2 nm giapponese, volume dal 2027 | — | [Tom's Hardware](https://www.tomshardware.com/tech-industry/semiconductors/rapidus-fab-roadmap-examined), 2026 (media) |
| Nexperia, Nijmegen (Paesi Bassi) | Paesi Bassi | chip discreti e di potenza (fronte-end in Europa, back-end a Dongguan) | — | [WTOP (AP), «Dutch court orders investigation into chipmaker Nexperia»](https://wtop.com/world/2026/02/dutch-court-orders-investigation-into-semiconductor-chipmaker-nexperia/), 2026-02 (alta) |
| Nexperia, Dongguan (Cina): assemblaggio e test | Cina | back-end: oltre 50 miliardi di pezzi l'anno, circa metà della produzione pre-crisi | — | [Model Diplomat, «Nexperia's Split Signals Chip Decoupling»](https://modeldiplomat.com/story/nexperias-split-signals-chip-decoupling), 2026 (bassa) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Colli di bottiglia e indicatori

| Collo | Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte |
|---|---|---|---|---|---|
| Fonderia avanzata concentrata a Taiwan | Quota TSMC dei ricavi mondiali di fonderia (2° trimestre 2026) | 72,5 % | 50 / 70 % | {stato:critico} | [TrendForce, classifica fonderie 2° trimestre 2026](https://www.trendforce.com/presscenter/news/20260909-13225.html), 2026-09-09 |
| Fonderia avanzata concentrata a Taiwan | Transiti nello Stretto di Taiwan, media 7 giorni rispetto a un anno prima | 7,1 % | -15 / -40 % | {stato:normale} | [IMF PortWatch (portwatch.json)](https://portwatch.imf.org/), 2026-11-01 |
| Fonderia avanzata concentrata a Taiwan | Danni a cavi sottomarini intorno a Taiwan negli ultimi 365 giorni | 1 eventi | 1 / 3 eventi | {stato:attenzione} | [cavi-incidenti.json (osservatorio)](https://www.submarinecablemap.com/), 2026-11-09 |
| Fonderia avanzata concentrata a Taiwan | TSMC (ADR) in borsa, variazione a 1 mese | -13,8 % | -10 / -25 % | {stato:attenzione} | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/TSM), 2026-11-09 |

**Fonderia avanzata concentrata a Taiwan.** TSMC ha il 72,5% dei ricavi di fonderia e il 2 nm è in volume solo a Hsinchu e Kaohsiung; lo Stretto di Taiwan è il punto unico di rottura.

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| TSMC (ADR) (TSM) | fonderia avanzata e CoWoS | 390,98 USD * | −14% | +29% | +36% |
| Samsung Electronics (005930.KS) | fonderia, DRAM, HBM | non seguito | — | — | — |
| Intel (INTC) | fonderia 18A negli USA | non seguito | — | — | — |
| SMIC (0981.HK) | fonderia cinese (chip Huawei) | non seguito | — | — | — |
| Indice dei semiconduttori (PHLX SOX) (SOX) | termometro dell'intera filiera dei chip | 10.046 USD * | −20% | +42% | +45% |

<small>Prezzi da prezzi.json (Yahoo Finance, chiusure al 9 novembre 2026; * = serie provvisoria). «non seguito»: titolo non ancora in prezzi.json.</small>

**Indicatori da seguire:** Quote di fonderia trimestrali (TrendForce, prossima a dicembre 2026); Ricavi mensili di TSMC (pubblicati intorno al 10 di ogni mese); Avanzamento di Arizona Fab 2 e del packaging AP1.

<a id="anello-packaging-memoria"></a>

## 6. Packaging avanzato e memoria HBM

**Dove sta.** Taiwan (Tainan, Chiayi) per il CoWoS; Corea (Icheon, Cheongju, Onyang) per l'HBM; Giappone, Singapore e Indiana per la memoria in arrivo; Hefei per l'HBM cinese.

**Chi lo controlla.** TSMC per il CoWoS; SK Hynix, Samsung e Micron per l'HBM; CXMT in Cina.

Una GPU per l'AI non è un chip ma un pacchetto: il die logico di TSMC viene montato accanto a più pile di memoria HBM su un interposer (CoWoS). Questo passaggio avviene quasi tutto a Taiwan. La capacità CoWoS di TSMC a fine 2026 è stimata in 125.000–130.000 wafer al mese, con 170.000 a fine 2027 secondo [KGI](https://www.kgi.com.hk/en/-/media/files/kgishk/research-reports/tw-reports/tsmc_2330-tt_09032026e.pdf); Nvidia ne avrebbe prenotato circa il 60% (stime di analisti riportate dalla stampa).

Nel 2° trimestre 2026 l'HBM era divisa tra SK Hynix 50%, Samsung 33% e Micron 18% ([Counterpoint](https://counterpointresearch.com/insights/global-dram-and-hbm-market-share)): Samsung ha recuperato dodici punti in un trimestre. L'AI toglie capacità alla DRAM normale: TrendForce prevede prezzi contrattuali DRAM +20% sul trimestre nel 4° trimestre 2026 ([TrendForce, 20 ottobre 2026](https://www.trendforce.com/news/2026/10/20/news-dram-prices-seen-rising-20-qoq-in-4q26-despite-slower-gains-ai-demand)).

Per la Cina l'HBM è il vincolo vero: i controlli USA di dicembre 2024 hanno tolto la memoria coreana, e secondo [Epoch AI](https://epoch.ai/publications/huaweis-roadmap-to-2031) Huawei produrrà nel 2026 meno del 4% del calcolo AI di Nvidia.

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| TSMC AP8, Tainan: CoWoS | Taiwan | impacchettamento CoWoS delle GPU con l'HBM | capacità CoWoS di TSMC a fine 2026 stimata 125.000–130.000 wafer al mese; Nvidia circa il 60% della capacità 2026 | [KGI Securities, nota su TSMC (marzo 2026) e stime di settore](https://www.kgi.com.hk/en/-/media/files/kgishk/research-reports/tw-reports/tsmc_2330-tt_09032026e.pdf), 2026-03-09 (media) |
| TSMC AP7, Chiayi: SoIC e WMCM | Taiwan | impacchettamento avanzato 3D (SoIC) | — | [TrendForce](https://www.trendforce.com/news/2026/01/21/news-tsmc-advanced-packaging-capex-projected-to-grow-24-cagr-in-2025-27-chiayi-ap7-targets-wmcm-and-copos/), 2026-01-21 (alta) |
| SK Hynix, Icheon (Corea): sede e DRAM | Corea del Sud | primo produttore di HBM | SK Hynix 50% dei ricavi HBM nel 2° trimestre 2026 (58% nel 1°) | [Counterpoint Research, quote HBM 2° trimestre 2026 (ripreso da SamMobile e Daum)](https://counterpointresearch.com/insights/global-dram-and-hbm-market-share), 2026-09-03 (alta) |
| SK Hynix M15X, Cheongju: DRAM per HBM | Corea del Sud | nuova fabbrica di DRAM per HBM | — | [The Star (Reuters)](https://www.thestar.com.my/tech/tech-news/2026/01/15/exclusive-sk-hynix-speeds-up-new-chip-fab-opening-to-meet-memory-demand-executive-says), 2026-01-15 (media) |
| SK Hynix, West Lafayette (Indiana): HBM | Stati Uniti | packaging HBM negli USA dal 2029 | — | [Korea Times (Reuters)](https://www.koreatimes.co.kr/world/20260828/sk-hynix-to-start-ai-chip-volume-production-in-indiana-in-2029), 2026-08-28 (alta) |
| Samsung, Onyang (Asan): packaging HBM | Corea del Sud | assemblaggio e test HBM | Samsung 33% dei ricavi HBM nel 2° trimestre 2026 (21% nel 1°) | [Counterpoint Research, quote HBM 2° trimestre 2026](https://counterpointresearch.com/insights/global-dram-and-hbm-market-share), 2026-09-03 (alta) |
| Micron, Hiroshima (Giappone): DRAM con EUV e HBM | Giappone | DRAM avanzata per HBM | Micron 18% dei ricavi HBM nel 2° trimestre 2026 (21% nel 1°) | [Counterpoint Research, quote HBM 2° trimestre 2026](https://counterpointresearch.com/insights/global-dram-and-hbm-market-share), 2026-09-03 (alta) |
| Micron, Singapore: packaging HBM | Singapore | assemblaggio HBM | — | [Micron via Researchpool](https://app.researchpool.com/company/mu-us5951121038-micron-technology-inc-HzQHxJMipr/press/micron-technology-inc-mu-micron-breaks-ground-on-new-hbm-advanced-packaging-facility-in-singapo-D8fDEA5799), 2025-01 (media) |
| CXMT, Hefei (Cina): DRAM e HBM cinese | Cina | memoria per i chip AI cinesi | CXMT 10% del mercato DRAM+HBM nel 2° trimestre 2026 | [Counterpoint Research (ripreso da Huawei Central)](https://www.huaweicentral.com/cxmt-records-strong-growth-in-q2-2026-global-dram-and-hbm-market/), 2026-08 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Colli di bottiglia e indicatori

| Collo | Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte |
|---|---|---|---|---|---|
| Packaging CoWoS | Divario tra domanda e offerta CoWoS a fine 2026 | 10 % | 5 / 15 % | {stato:attenzione} | [TrendForce (ripreso in ai-mondo.json): dal 20% al 10% a fine 2026](https://www.trendforce.com/news/2026/01/21/news-tsmc-advanced-packaging-capex-projected-to-grow-24-cagr-in-2025-27-chiayi-ap7-targets-wmcm-and-copos/), 2026-06-15 |
| Memoria HBM e DRAM | Prezzi contrattuali DRAM nel 4° trimestre 2026, variazione sul trimestre (previsione) | 20 % | 10 / 30 % | {stato:attenzione} | [TrendForce, «DRAM prices seen rising 20% QoQ in 4Q26»](https://www.trendforce.com/news/2026/10/20/news-dram-prices-seen-rising-20-qoq-in-4q26-despite-slower-gains-ai-demand), 2026-10-20 |
| Memoria HBM e DRAM | SK Hynix in borsa, variazione a 1 mese | -34,3 % | -10 / -25 % | {stato:critico} | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/000660.KS), 2026-11-06 |

**Packaging CoWoS.** Ogni GPU di fascia alta passa dal CoWoS di TSMC a Taiwan; Nvidia ha prenotato circa il 60% della capacità 2026. Il packaging in Arizona arriverà dal 2028.

**Memoria HBM e DRAM.** Tre produttori (SK Hynix, Samsung, Micron) fanno tutta l'HBM occidentale; l'AI toglie capacità alla DRAM normale e i prezzi salgono. SK Hynix vede carenza fino al 2030.

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| TSMC (ADR) (TSM) | fonderia avanzata e CoWoS | 390,98 USD * | −14% | +29% | +36% |
| Samsung Electronics (005930.KS) | fonderia, DRAM, HBM | non seguito | — | — | — |
| SK Hynix (000660.KS) | primo produttore di HBM | 1.132.000 KRW | −34% | +74% | +91% |
| Micron Technology (MU) | HBM e DRAM | non seguito | — | — | — |
| Western Digital (WDC) | dischi rigidi per i data center (magneti di terre rare) | 289,95 USD * | −27% | +68% | +78% |
| Indice dei semiconduttori (PHLX SOX) (SOX) | termometro dell'intera filiera dei chip | 10.046 USD * | −20% | +42% | +45% |

<small>Prezzi da prezzi.json (Yahoo Finance, chiusure al 9 novembre 2026; * = serie provvisoria). «non seguito»: titolo non ancora in prezzi.json.</small>

**Indicatori da seguire:** Prezzi contrattuali DRAM e HBM (TrendForce, mensili); Quote HBM trimestrali (Counterpoint); Capacità CoWoS e nuove sedi (AP7, AP8, Arizona AP1); Qualifiche HBM4 presso Nvidia.

<a id="anello-progettazione"></a>

## 7. Progetto dei chip e acceleratori

**Dove sta.** California (Santa Clara, Palo Alto, Mountain View), Shenzhen.

**Chi lo controlla.** Nvidia, con larga maggioranza; AMD; Broadcom e Marvell come co-progettisti dei chip dei grandi cloud (TPU di Google, Trainium di Amazon, MTIA di Meta); Huawei in Cina.

Il progetto è l'anello più ricco e il meno fisico: nessuno di questi gruppi possiede una fabbrica di chip avanzati. Le stime della quota di Nvidia nel 2026 vanno dal 75% all'86% a seconda della definizione, con IDC intorno all'81% (stime riportate da terzi; [Tom's Hardware](https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia) sugli ASIC su misura). Broadcom è il secondo cliente CoWoS di TSMC.

Le regole americane decidono dove vanno i chip: da gennaio 2026 gli USA permettono di vendere l'H200 in Cina con dazio del 25% e verifiche, ma a maggio nessun chip risultava spedito perché Pechino non aveva dato il via libera ([TechRepublic](https://www.techrepublic.com/article/news-nvidia-h200-ai-chip-sales-china-stalled/)). Huawei prevede circa 12 miliardi di dollari di ricavi da chip AI nel 2026.

> *Valutazione.* Il potere di mercato di questo anello dipende da anelli che non controlla (CoWoS, HBM, EUV). In borsa si vede: da inizio anno Nvidia e Broadcom sono in calo mentre memoria e macchine salgono (tabella dei titoli).

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| Nvidia, Santa Clara (California) | Stati Uniti | GPU per data center (Blackwell, Rubin), reti NVLink e InfiniBand | circa 81% del mercato dei chip AI per data center nel 2026 (stima IDC riportata da terzi; altre stime 75–86%) | [Tom's Hardware, «The custom AI ASIC state of play (May 2026)» e sintesi di stime IDC](https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia), 2026-05 (media) |
| AMD, Santa Clara (California) | Stati Uniti | acceleratori Instinct | circa 10% (stima IDC riportata da terzi) | [sintesi di stime IDC (commandlinux.com)](https://commandlinux.com/ai/ai-chip-market-share/), 2026 (bassa) |
| Broadcom, Palo Alto (California): ASIC su misura | Stati Uniti | co-progetta i TPU di Google e i chip di Meta; switch Ethernet | 60–80% del mercato degli ASIC su misura (stime discordi); secondo cliente CoWoS di TSMC (oltre 240.000 wafer nel 2026) | [Tom's Hardware, «The custom AI ASIC state of play (May 2026)»](https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia), 2026-05 (media) |
| Google, Mountain View (California): TPU | Stati Uniti | acceleratori propri (TPU) per uso interno e cloud | — | [Tom's Hardware, «The custom AI ASIC state of play (May 2026)»](https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia), 2026-05 (media) |
| Huawei, Shenzhen: Ascend | Cina | acceleratori Ascend (910C, 950) prodotti da SMIC | ricavi attesi dai chip AI circa 12 mld USD nel 2026 (7,5 nel 2025); meno del 4% del calcolo AI prodotto da Nvidia nel 2026 secondo Epoch AI | [Epoch AI, «Huawei's roadmap to 2031»](https://epoch.ai/publications/huaweis-roadmap-to-2031), 2026 (alta) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Colli di bottiglia e indicatori

| Collo | Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte |
|---|---|---|---|---|---|
| Un solo progettista dominante e regole USA sui chip | Quota di Nvidia nei chip AI per data center 2026 (stima IDC riportata da terzi; forchetta delle stime 75–86%) | 81 % | 50 / 70 % | {stato:critico} | [commandlinux.com (sintesi di stime IDC)](https://commandlinux.com/ai/ai-chip-market-share/), 2026 |
| Un solo progettista dominante e regole USA sui chip | Nvidia in borsa, variazione a 1 mese | -22,6 % | -10 / -25 % | {stato:attenzione} | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/NVDA), 2026-11-09 |

**Un solo progettista dominante e regole USA sui chip.** Nvidia ha la grande maggioranza dei chip AI per data center; dove vanno i chip lo decidono le licenze USA (H200 per la Cina con dazio del 25%) e la risposta di Pechino.

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| Nvidia (NVDA) | GPU per data center | 177,40 USD * | −23% | −4,9% | −5,7% |
| AMD (AMD) | acceleratori Instinct | 509,71 USD * | −16% | +138% | +118% |
| Broadcom (AVGO) | ASIC su misura (TPU) e switch | 320,77 USD * | −11% | −7,3% | −8,2% |
| Alphabet (GOOGL) | TPU e data center | 290,16 USD * | −17% | −7,3% | +4,1% |
| Indice dei semiconduttori (PHLX SOX) (SOX) | termometro dell'intera filiera dei chip | 10.046 USD * | −20% | +42% | +45% |

<small>Prezzi da prezzi.json (Yahoo Finance, chiusure al 9 novembre 2026; * = serie provvisoria). «non seguito»: titolo non ancora in prezzi.json.</small>

**Indicatori da seguire:** Conti trimestrali di Nvidia (prossimi a fine novembre 2026); Licenze USA per la Cina e risposta di Pechino; Quota degli ASIC nei server AI (TrendForce).

<a id="anello-server-rete"></a>

## 8. Server, rete e assemblaggio

**Dove sta.** Taiwan (Nuova Taipei, Taoyuan), Messico (Jalisco), Texas (Houston, Dallas), Cina (Suzhou, Chengdu) per l'ottica, USA (Pennsylvania) per i laser.

**Chi lo controlla.** Foxconn, Quanta e Wistron per i rack; InnoLight, Coherent ed Eoptolink per l'ottica; Coherent e Lumentum per i laser EML.

Le GPU impacchettate diventano schede, vassoi e rack completi (GB300, VR200) negli impianti dei grandi assemblatori taiwanesi. Foxconn è il primo con circa il 40% dei server AI ([TechNews](https://finance.technews.tw/2026/05/12/foxconn-leads-quanta-and-wistron-in-ai-server-shipments/)). L'assemblaggio si sta spostando verso il mercato finale: Messico (Jalisco), Texas (Foxconn a Houston, Wistron a Dallas), Thailandia. Il risultato si vede nell'export di Taiwan: server e computer sono diventati la prima voce, 192,6 miliardi di dollari in gennaio–agosto 2026, +87,5% ([STAT Times](https://www.stattimes.com/latest-news/is-taiwans-ai-engine-on-fire-1360979)).

La rete ottica dei cluster dipende dalla Cina per i moduli (InnoLight intorno al 27% dei ricavi) e da due società americane per i chip laser EML: per [Yole](https://www.yolegroup.com/strategy-insights/opinion-optical-transceivers-at-the-chokepoint-of-ai-growth-and-supply-chain-constraints/) è il vincolo dell'1,6T nel 2026.

Fuori dal rack, il collo di bottiglia è elettrico: i tempi di consegna dei trasformatori elevatori hanno superato le 160 settimane nel 1° trimestre 2026 ([Reuters via Kitco](https://www.kitco.com/news/off-the-wire/2026-07-09/us-power-companies-scramble-secure-equipment-surging-data-center)).

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| Foxconn (Hon Hai), Tucheng (Nuova Taipei) | Taiwan | primo assemblatore di server AI e rack completi | circa 40% dei server AI mondiali, oltre 44% dei rack secondo stampa taiwanese | [TechNews, «AI 伺服器出貨鴻海領先廣達、緯創»](https://finance.technews.tw/2026/05/12/foxconn-leads-quanta-and-wistron-in-ai-server-shipments/), 2026-05-12 (media) |
| Quanta Computer, Guishan (Taoyuan) | Taiwan | secondo assemblatore di server AI | — | [TrendForce, Server Market Bulletin (gennaio 2026)](https://www.trendforce.com/research/download/RP260122RF3), 2026-01-22 (media) |
| Foxconn, Guadalajara (Jalisco, Messico): server GB200 | Messico | assemblaggio di server Nvidia per i data center USA (Stargate) | — | [Expansión, «Foxconn ya hace data centers de Nvidia en México»](https://expansion.mx/tecnologia/2025/04/07/foxconn-ya-hace-data-centers-de-nvidia-en-mexico), 2025-04-07 (media) |
| Foxconn, Houston (Texas): supercomputer Nvidia | Stati Uniti | assemblaggio negli USA | — | [Nvidia, «NVIDIA to Manufacture American-Made AI Supercomputers in US for First Time»](https://blogs.nvidia.com/blog/nvidia-manufacture-american-made-ai-supercomputers-us/), 2025-04-14 (alta) |
| InnoLight (Zhongji Innolight), Suzhou: moduli ottici | Cina | primo produttore di transceiver ottici 800G e 1,6T | circa 27% dei ricavi mondiali dei transceiver per data center (Counterpoint); 50–60% dell'1,6T nel 2026 (Yole) | [Yole Group, «Optical transceivers at the chokepoint of AI growth»](https://www.yolegroup.com/strategy-insights/opinion-optical-transceivers-at-the-chokepoint-of-ai-growth-and-supply-chain-constraints/), 2026 (media) |
| Eoptolink, Chengdu: moduli ottici | Cina | terzo produttore di transceiver per data center | — | [Counterpoint Research, «FCC China ban: AI component»](https://counterpointresearch.com/en/insights/fcc-china-ban-ai-component), 2026 (media) |
| Coherent, Saxonburg (Pennsylvania): laser e moduli ottici | Stati Uniti | secondo produttore di transceiver; chip laser EML insieme a Lumentum | circa 17% dei ricavi dei transceiver per data center (Counterpoint) | [Counterpoint Research, «FCC China ban: AI component»](https://counterpointresearch.com/en/insights/fcc-china-ban-ai-component), 2026 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Colli di bottiglia e indicatori

| Collo | Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte |
|---|---|---|---|---|---|
| Ottica: chip laser EML per l'1,6T | Carenza di chip EML da 200G per corsia (stima) | 60 % | 10 / 30 % | {stato:critico} | [cnyes (analisi di settore in cinese): divario oltre il 60%](https://hao.cnyes.com/post/271963), 2026 |

**Ottica: chip laser EML per l'1,6T.** I chip EML da 200G per corsia vengono da pochi fornitori (Coherent, Lumentum e un terzo); per Yole sono il vincolo dell'1,6T nel 2026. I moduli sono assemblati soprattutto in Cina.

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| Western Digital (WDC) | dischi rigidi per i data center (magneti di terre rare) | 289,95 USD * | −27% | +68% | +78% |
| Broadcom (AVGO) | ASIC su misura (TPU) e switch | 320,77 USD * | −11% | −7,3% | −8,2% |
| Hon Hai (Foxconn) (2317.TW) | assemblaggio server AI | non seguito | — | — | — |
| Quanta Computer (2382.TW) | assemblaggio server AI | non seguito | — | — | — |
| Wistron (3231.TW) | assemblaggio server AI | non seguito | — | — | — |
| Coherent (COHR) | laser EML e transceiver | non seguito | — | — | — |
| Zhongji Innolight (300308.SZ) | transceiver 800G/1,6T | non seguito | — | — | — |
| Eoptolink (300502.SZ) | transceiver | non seguito | — | — | — |

<small>Prezzi da prezzi.json (Yahoo Finance, chiusure al 9 novembre 2026; * = serie provvisoria). «non seguito»: titolo non ancora in prezzi.json.</small>

**Indicatori da seguire:** Export mensile di Taiwan per categoria (Ministero delle Finanze); Ricavi mensili di Foxconn, Quanta, Wistron; Tempi di consegna di trasformatori e quadri (Wood Mackenzie); Prezzi e disponibilità dei transceiver 1,6T.

<a id="anello-logistica"></a>

## 9. Logistica

**Dove sta.** Aeroporti di Taoyuan, Incheon, Schiphol, Anchorage, Pudong; Stretto di Taiwan, Mar Cinese Meridionale, Malacca, Hormuz.

**Chi lo controlla.** Vettori cargo (China Airlines, EVA Air, integratori), aeroporti e, in caso di crisi, le marine militari.

I chip e i server viaggiano in aereo: valgono molto e pesano poco. Le macchine viaggiano smontate: una EUV richiede circa 40 container, 20 camion e 3 Boeing 747 cargo ([Asia Times](https://asiatimes.com/2021/09/the-150mn-machine-that-is-changing-the-world/); [DHL](https://www.dhl.com/global-en/delivered/innovation/focus-on-the-details.html)); una High-NA è andata in Oregon in 43 container. Le materie (elio, quarzo, GNL per le centrali di Taiwan) viaggiano per nave.

Il cargo aereo di Taiwan è trainato dall'AI: per EVA Air il carico legato all'AI vale il 40–50% del cargo, il Nord America circa il 70% dei ricavi cargo (stampa taiwanese). Le rotte transpacifiche fanno scalo ad Anchorage.

Lo Stretto di Taiwan è il punto unico di rottura. Ci passa metà delle portacontainer del mondo; un blocco o un conflitto costerebbero all'economia mondiale circa 10.600 miliardi di dollari (9,6% del PIL mondiale) nel primo anno nello scenario estremo di Bloomberg Economics ([Insurance Journal](https://www.insurancejournal.com/news/international/2026/02/12/857770.htm)), e le aziende dipendenti dai chip di Taiwan perderebbero fino a 1.600 miliardi di ricavi l'anno secondo [Rhodium](https://rhg.com/research/taiwan-economic-disruptions/). I cavi sottomarini intorno all'isola sono già stati danneggiati più volte (cavi-incidenti.json).

> *Valutazione.* In un blocco navale gli aerei potrebbero continuare a portare chip per qualche tempo, ma il GNL no: Taiwan si fermerebbe per mancanza di energia prima che per mancanza di trasporti. Terremoti (aprile 2024: TSMC ha recuperato oltre il 70% delle macchine in 10 ore, [Tom's Hardware](https://www.tomshardware.com/tech-industry/tsmc-resumes-chip-production-following-biggest-earthquake-in-25-years-incurred-no-damage-to-its-critical-tools)), siccità e blackout sono i rischi ricorrenti.

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| Aeroporto di Taipei Taoyuan (TPE) | Taiwan | uscita aerea di server e chip di Taiwan | carico AI tra il 40 e il 50% del cargo di EVA Air; Nord America circa il 70% dei ricavi cargo | [DIGITIMES / Taiwan News (sintesi di stampa)](https://www.digitimes.com/news/a20260527PD246.html), 2026-05-27 (media) |
| Aeroporto di Anchorage (ANC) | Stati Uniti | scalo tecnico dei cargo transpacifici Asia–USA | — | [The Loadstar, «Air cargo cashes in on AI boom – but who has the edge?»](https://theloadstar.com/?p=327930), 2026 (media) |
| Aeroporto di Amsterdam Schiphol (AMS) | Paesi Bassi | partenza per via aerea delle macchine ASML | una EUV: circa 40 container, 20 camion e 3 Boeing 747 cargo | [Asia Times, «The $150mn machine that is changing the world»](https://asiatimes.com/2021/09/the-150mn-machine-that-is-changing-the-world/), 2021-09 (media) |
| Aeroporto di Incheon (ICN) | Corea del Sud | uscita aerea di HBM e memorie coreane | — | [AJOT (Reuters), «AI race redraws Asian air cargo»](https://www.ajot.com/news/ai-race-redraws-asian-air-cargo-replacing-e-commerce-as-growth-engine), 2026-07-29 (media) |
| Aeroporto di Shanghai Pudong (PVG) | Cina | uscita aerea dei moduli ottici cinesi | — | [China Daily, «Air cargo service injects impetus into AI chains»](https://www.chinaservicesinfo.com/s/202603/18/WS69bd1371498e23165e06e3ea/air-cargo-service-injects-impetus-into-ai-chains.html), 2026-03-18 (media) |
| Aeroporto di Dallas/Fort Worth (DFW) | Stati Uniti | arrivo dei server verso i campus del Texas | — | [DIGITIMES, export di Taiwan verso gli USA (+83% nei primi due mesi 2026)](https://www.digitimes.com/news/a20260316PD217.html), 2026-03-16 (bassa) |
| Porto di Kaohsiung | Taiwan | primo porto di Taiwan: GNL, materie, componenti pesanti | — | [stretti-dettaglio.json (Stretto di Taiwan) e PortWatch](https://portwatch.imf.org/), 2026-11-01 (media) |
| Stretto di Taiwan | Taiwan | passaggio di metà delle portacontainer del mondo; attraversato da ogni carico da e per le fab di Taiwan | — | [CSIS ChinaPower (ripreso da stretti.json)](https://features.csis.org/chinapower/china-taiwan-strait-trade/), 2024-08-22 (alta) |
| Stretto di Hormuz | Oman | uscita del GNL e dell'elio del Qatar | — | [IEA, Strait of Hormuz Factsheet (febbraio 2026), su dati Kpler](https://iea.blob.core.windows.net/assets/c8248eba-8689-46d9-ae4b-b858b59c0f1c/StraitofHormuz2026-Factsheet.pdf), 2026-02 (alta) |
| Stretto di Malacca | Malesia | rotta marittima Europa/Golfo–Asia orientale; accanto ai data center di Johor | — | [Anadolu Agency, su dati IEA ed EIA (ripreso da stretti.json)](https://www.aa.com.tr/en/energy/general/around-70-of-global-oil-demand-transported-through-strategic-maritime-chokepoints/55347), 2026-03-10 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| EVA Airways (2618.TW) | cargo aereo AI da Taoyuan | non seguito | — | — | — |
| China Airlines (2610.TW) | cargo aereo AI da Taoyuan | non seguito | — | — | — |

<small>Prezzi da prezzi.json (Yahoo Finance, chiusure al 9 novembre 2026; * = serie provvisoria). «non seguito»: titolo non ancora in prezzi.json.</small>

**Indicatori da seguire:** Transiti nello Stretto di Taiwan, di Luzon e di Malacca (PortWatch, settimanali); Incidenti ai cavi intorno a Taiwan; Esercitazioni cinesi intorno a Taiwan; Tariffe cargo aereo Asia–Nord America.

<a id="anello-energia-dc"></a>

## 10. Energia e data center

**Dove sta.** Stati Uniti (Texas, Tennessee, Indiana, Georgia), Golfo, Malesia (Johor), Europa (Francia, Paesi del Nord, Italia); Taiwan per l'energia delle fab.

**Chi lo controlla.** I grandi cloud (Microsoft, Amazon, Google, Meta, Oracle), i laboratori (OpenAI, xAI, Anthropic come cliente), i gestori di rete e i produttori di energia.

Secondo l'IEA i data center hanno consumato circa 485 TWh nel 2025 e arriveranno a circa 950 TWh nel 2030, intorno al 3% dell'elettricità mondiale; i siti dedicati all'AI crescono molto più in fretta ([IEA, Key questions on energy and AI](https://www.iea.org/reports/key-questions-on-energy-and-ai/executive-summary)).

L'energia entra nella catena due volte. A monte, Taiwan produce metà dell'elettricità col gas e tiene scorte di GNL per 12–14 giorni ([Focus Taiwan](https://focustaiwan.tw/business/202603210010)); ha spento le centrali nucleari e ora valuta il riavvio di Maanshan ([FDD](https://www.fdd.org/analysis/in-major-reversal-taiwan-seeks-to-rewire-its-energy-strategy-by-restarting-its-nuclear-plants/)). A valle, i campus americani si scontrano con i tempi dei trasformatori e degli allacci, quelli europei con il prezzo: i progetti a gas come Ferrera Erbognone legano l'AI italiana al TTF, la Francia sfrutta il nucleare (Fouju è vicino a Nogent).

> *Valutazione.* Per l'Europa del Nord il vantaggio è l'elettricità pulita e il clima freddo (Paesi nordici, Finlandia), il limite è la capacità di rete; il legame con la mappa è nei livelli rete-elettrica e interconnessioni.

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| Centrale nucleare di Maanshan (Taiwan) | Taiwan | nucleare spento nel 2025, riavvio in esame | gas al 50,5% della generazione di Taiwan a luglio 2026; scorte di GNL 12–14 giorni (minimo legale 11) | [Focus Taiwan (scorte di GNL dette dal presidente Lai)](https://focustaiwan.tw/business/202603210010), 2026-03-21 (media) |
| Stargate Abilene (Texas) | Stati Uniti | campus OpenAI-Oracle-Crusoe | — | [Epoch AI](https://epoch.ai/blog/openai-stargate-where-the-us-sites-stand), 2026-04-17 (alta) |
| xAI Colossus 2, Memphis | Stati Uniti | il più grande campus AI operativo (Epoch) | — | [Epoch AI (via techjacksolutions)](https://techjacksolutions.com/?p=83881), 2026-09-22 (media) |
| Amazon-Anthropic New Carlisle (Indiana) | Stati Uniti | campus Amazon usato da Anthropic (Project Rainier) | — | [Epoch AI (via techjacksolutions)](https://techjacksolutions.com/?p=83881), 2026-09-22 (media) |
| Microsoft Fairwater Atlanta | Stati Uniti | campus AI di Microsoft | — | [Epoch AI (via techjacksolutions)](https://techjacksolutions.com/?p=83881), 2026-09-22 (media) |
| DayOne Nusajaya, Johor (Malesia) | Malesia | primo polo AI fuori dagli USA nei dati Epoch | — | [Epoch AI, AI data centers](https://epoch.ai/data/ai-data-centers), 2026-10-02 (alta) |
| Stargate UAE, Abu Dhabi | Emirati | campus da 5 GW (1.000 MW IT previsti nel 2028) | — | [Epoch AI, AI data centers](https://epoch.ai/data/ai-data-centers), 2025-11-16 (media) |
| Campus IA di Fouju (Francia) | Francia | 1,4 GW vicino al nucleare di Nogent | — | [Eiffage, comunicato](https://www.privacy.eiffage.com/files/live/sites/metal/files/publications/PR_Eiffage_Campus%2520AI%2520enters%2520the%2520implementation%2520phase_20260602.pdf), 2026-06-02 (media) |
| Campus AI Eni-Khazna, Ferrera Erbognone | Italia | progetto italiano a gas con cattura della CO2 | — | [DatacenterDynamics](https://www.datacenterdynamics.com/es/noticias/las-empresas-italianas-eni-y-khazna-se-asocian-para-construir-un-centro-de-datos-de-500-mw-en-las-afueras-de-mil%C3%A1n/), 2025-07 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Colli di bottiglia e indicatori

| Collo | Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte |
|---|---|---|---|---|---|
| Trasformatori e allacci alla rete | Tempi di consegna dei trasformatori elevatori (GSU), 1° trimestre 2026 | 160 settimane | 52 / 104 settimane | {stato:critico} | [Reuters, ripreso da Kitco: «US power companies scramble to secure equipment»](https://www.kitco.com/news/off-the-wire/2026-07-09/us-power-companies-scramble-secure-equipment-surging-data-center), 2026-07-09 |
| Energia di Taiwan per le fab | Scorte di GNL di Taiwan (estremo basso della forchetta 12–14 giorni) | 12 giorni | 14 / 11 giorni | {stato:attenzione} | [Focus Taiwan (dichiarazione del presidente Lai)](https://focustaiwan.tw/business/202603210010), 2026-03-21 |
| Costo dell'energia per i data center | Gas TTF (Europa) | 82,3 EUR/MWh | 40 / 70 EUR/MWh | {stato:critico} | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/TTF%3DF), 2026-11-09 |
| Costo dell'energia per i data center | Gas Henry Hub (USA) | 3,2 USD/MMBtu | 4 / 6 USD/MMBtu | {stato:normale} | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/NG%3DF), 2026-11-09 |

**Trasformatori e allacci alla rete.** Il denaro c'è, i trasformatori no: i tempi di consegna dei trasformatori elevatori superano i tre anni e le utility comprano con cinque anni di anticipo.

**Energia di Taiwan per le fab.** Taiwan importa quasi tutta l'energia, produce metà dell'elettricità col gas e tiene scorte di GNL per meno di due settimane: un blocco navale colpirebbe le fab anche senza toccarle.

**Costo dell'energia per i data center.** In Europa i progetti a gas (come Ferrera Erbognone) legano l'AI al TTF e quindi a Hormuz; negli USA conta il prezzo dell'Henry Hub e la capacità di rete.

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| Freeport-McMoRan (FCX) | rame | non seguito | — | — | — |
| Alphabet (GOOGL) | TPU e data center | 290,16 USD * | −17% | −7,3% | +4,1% |
| Microsoft (MSFT) | data center (Fairwater) | 547,67 USD * | +2,4% | +13% | +10% |
| Amazon (AMZN) | data center (New Carlisle), chip Trainium | 268,97 USD * | +2,5% | +17% | +10% |
| Meta (META) | data center | 645,10 USD * | −10% | −2,3% | +3,8% |
| Oracle (ORCL) | data center Stargate (Abilene) | 119,30 USD * | −16% | −39% | −50% |
| Gas TTF (Europa) (TTF) | costo dell'energia dei data center europei a gas | 82,33 EUR * | +1,1% | +192% | +164% |
| Gas Henry Hub (USA) (HH) | costo del gas per le centrali dei data center USA | 3,21 USD * | −0,2% | −13% | −26% |

<small>Prezzi da prezzi.json (Yahoo Finance, chiusure al 9 novembre 2026; * = serie provvisoria). «non seguito»: titolo non ancora in prezzi.json.</small>

**Indicatori da seguire:** Prezzi del gas TTF e Henry Hub (prezzi.json); Aste di capacità PJM e code di allaccio; Iter del riavvio di Maanshan; Aggiornamenti IEA sui consumi dei data center.

<a id="collegamenti"></a>

## 11. Come si spostano le cose: i collegamenti

Ogni riga è un arco «da → a» del file di dati. Le righe marcate *valutazione* sono percorsi tipici ricostruiti dall'osservatorio (per esempio l'aeroporto usato), non tracciati reali: le società non pubblicano le rotte.

| Da → a | Cosa | Modo | Stato | Tipo | km in linea d'aria |
|---|---|---|---|---|---|
| Spruce Pine (North Carolina): quarzo ad alta purezza → TSMC Fab 20, Hsinchu (Baoshan): 2 nm | quarzo per crogioli → lingotti e wafer di silicio (passando per i produttori di wafer, non mostrati) | nave | attivo | valutazione | 12.847 |
| Ras Laffan (Qatar): elio dal gas naturale → TSMC Fab 20, Hsinchu (Baoshan): 2 nm | elio liquido in contenitori criogenici per le fab asiatiche via Stretto di Hormuz, Stretto di Malacca | nave | ridotto | fatto | 6.893 |
| Odesa (Ucraina): purificazione del neon → Cymer, San Diego (California): sorgenti di luce | neon per le miscele dei laser ad eccimeri | misto | storico | fatto | 10.638 |
| Rubaya (Nord Kivu, Congo): coltan → Foxconn (Hon Hai), Tucheng (Nuova Taipei) | tantalio (coltan) → condensatori dei server, via Ruanda e raffinatori in Asia | misto | attivo | valutazione | 10.339 |
| Carl Zeiss SMT, Oberkochen (Germania): ottiche EUV → ASML, Veldhoven (Paesi Bassi): scanner EUV | ottiche EUV | camion | attivo | fatto | 445 |
| Trumpf, Ditzingen (Germania): laser CO2 per EUV → Cymer, San Diego (California): sorgenti di luce | laser CO2 di potenza → modulo sorgente EUV | aereo | attivo | fatto | 9.498 |
| Cymer, San Diego (California): sorgenti di luce → ASML, Veldhoven (Paesi Bassi): scanner EUV | modulo sorgente EUV per l'assemblaggio finale | aereo | attivo | fatto | 9.113 |
| ASML, Veldhoven (Paesi Bassi): scanner EUV → Aeroporto di Amsterdam Schiphol (AMS) | scanner EUV smontato in moduli (circa 40 container, 20 camion) | camion | attivo | valutazione | 112 |
| Aeroporto di Amsterdam Schiphol (AMS) → Aeroporto di Taipei Taoyuan (TPE) | scanner EUV: 3 aerei cargo per macchina | aereo | attivo | valutazione | 9.443 |
| Aeroporto di Taipei Taoyuan (TPE) → TSMC Fab 20, Hsinchu (Baoshan): 2 nm | macchine EUV → montaggio e calibrazione in fab | camion | attivo | valutazione | 43 |
| ASML, Veldhoven (Paesi Bassi): scanner EUV → TSMC Arizona Fab 21, Phoenix | scanner EUV per le fab americane | aereo | attivo | valutazione | 8.758 |
| ASML, Veldhoven (Paesi Bassi): scanner EUV → Samsung, Pyeongtaek (Corea) | scanner EUV per DRAM e fonderia | aereo | attivo | valutazione | 8.661 |
| Applied Materials, Santa Clara (California) → TSMC Fab 20, Hsinchu (Baoshan): 2 nm | macchine di deposizione e incisione (anche Lam, KLA) | aereo | attivo | valutazione | 10.481 |
| TSMC Fab 20, Hsinchu (Baoshan): 2 nm → TSMC AP8, Tainan: CoWoS | wafer di GPU a 3–4 nm → CoWoS | camion | attivo | fatto | 198 |
| TSMC Arizona Fab 21, Phoenix → TSMC AP8, Tainan: CoWoS | wafer fatti in Arizona rimandati a Taiwan per il packaging avanzato | aereo | attivo | fatto | 11.605 |
| SK Hynix, Icheon (Corea): sede e DRAM → Aeroporto di Incheon (ICN) | pile HBM | camion | attivo | valutazione | 91 |
| Aeroporto di Incheon (ICN) → Aeroporto di Taipei Taoyuan (TPE) | HBM verso il CoWoS di TSMC | aereo | attivo | valutazione | 1.463 |
| Aeroporto di Taipei Taoyuan (TPE) → TSMC AP8, Tainan: CoWoS | HBM → integrazione accanto alla GPU | camion | attivo | valutazione | 240 |
| TSMC AP8, Tainan: CoWoS → Foxconn (Hon Hai), Tucheng (Nuova Taipei) | GPU impacchettate (moduli) → schede e rack | camion | attivo | valutazione | 239 |
| TSMC AP8, Tainan: CoWoS → Quanta Computer, Guishan (Taoyuan) | GPU impacchettate → rack | camion | attivo | valutazione | 236 |
| Foxconn (Hon Hai), Tucheng (Nuova Taipei) → Aeroporto di Taipei Taoyuan (TPE) | rack e server AI completi | camion | attivo | valutazione | 24 |
| Aeroporto di Taipei Taoyuan (TPE) → Aeroporto di Anchorage (ANC) | server AI verso gli USA (scalo tecnico) | aereo | attivo | valutazione | 7.519 |
| Aeroporto di Anchorage (ANC) → Aeroporto di Dallas/Fort Worth (DFW) | server AI | aereo | attivo | valutazione | 4.889 |
| Aeroporto di Dallas/Fort Worth (DFW) → Stargate Abilene (Texas) | server AI → campus | camion | attivo | valutazione | 256 |
| Foxconn, Guadalajara (Jalisco, Messico): server GB200 → Stargate Abilene (Texas) | server GB200 NVL72 «soprattutto per Stargate» | camion | attivo | fatto | 1.357 |
| Aeroporto di Taipei Taoyuan (TPE) → Foxconn, Guadalajara (Jalisco, Messico): server GB200 | GPU e schede da Taiwan all'assemblaggio messicano | aereo | attivo | valutazione | 13.010 |
| Foxconn, Houston (Texas): supercomputer Nvidia → Stargate Abilene (Texas) | supercomputer assemblati in Texas | camion | attivo | valutazione | 512 |
| InnoLight (Zhongji Innolight), Suzhou: moduli ottici → Aeroporto di Shanghai Pudong (PVG) | transceiver ottici 800G/1,6T | camion | attivo | valutazione | 114 |
| Aeroporto di Shanghai Pudong (PVG) → xAI Colossus 2, Memphis | transceiver per le reti dei cluster | aereo | attivo | valutazione | 11.927 |
| Nexperia, Nijmegen (Paesi Bassi) → Nexperia, Dongguan (Cina): assemblaggio e test | wafer europei → assemblaggio e test in Cina | aereo | interrotto | fatto | 9.158 |
| Sillamäe (Estonia): separazione di terre rare → Narva (Estonia): magneti di terre rare | ossidi di terre rare separati → leghe e magneti | camion | attivo | fatto | 26 |
| SMIC, Shanghai: 7 nm senza EUV → Huawei, Shenzhen: Ascend | die Ascend a 7 nm | camion | attivo | fatto | 1.211 |
| CXMT, Hefei (Cina): DRAM e HBM cinese → Huawei, Shenzhen: Ascend | DRAM e HBM cinese per gli Ascend | camion | attivo | fatto | 1.075 |
| Centrale nucleare di Maanshan (Taiwan) → TSMC Fab 22, Kaohsiung: 2 nm | elettricità (oggi sostituita dal gas: riavvio in esame) | rete | interrotto | valutazione | 97 |

<a id="nord-europa"></a>

## 12. Paesi Bassi, Danimarca e Baltico

- **Veldhoven (ASML)** è il nodo più critico della catena che si trovi in Europa: unico produttore di EUV, a 10,8 km da una linea da 380 kV (rete-elettrica.json). Le macchine partono smontate verso Taiwan, Corea, Giappone e USA; per via aerea l'uscita naturale è Schiphol (valutazione: ASML non pubblica gli aeroporti).
- **Schiphol** è quindi un punto logistico della catena dell'AI oltre che dei fiori e della farmaceutica: un ritardo lì rallenta le nuove fab nel mondo, non la produzione corrente.
- **Nexperia (Nijmegen)** mostra il rischio opposto: un intervento dello Stato olandese (settembre 2025) e la risposta cinese hanno spezzato una catena Europa–Cina. Non tocca i chip AI, ma è il precedente da tenere a mente per ASML.
- **Regole olandesi.** Le licenze su DUV dal 2023 e 2024 sono olandesi; la proposta americana MATCH Act e le pressioni su assistenza e ricambi in Cina sono il prossimo fronte.
- **Danimarca e Groenlandia.** La Groenlandia ha 1.500.000 tonnellate di riserve di terre rare (USGS) e nessuna produzione: è un'opzione di lungo periodo, non un'offerta. Gli Stretti danesi non sono una rotta della catena dei chip.
- **Baltico.** In Estonia, a Sillamäe (a 37,6 km da una linea da 450 kV HVDC Estlink 2) e Narva (a 63,7 km da una linea da 450 kV HVDC Estlink 2), Neo Performance Materials separa terre rare (anche terbio e disprosio dal 2026) e produce magneti: il tratto di filiera europea più completo fuori dalla Cina, a pochi chilometri dal confine russo. Rischio da seguire: sicurezza della zona di confine e dei cavi del Baltico (livello cavi-incidenti).

<a id="scenari"></a>

## 13. Scenari di rottura

Ragionamenti dell'osservatorio, non previsioni. Per ogni scenario: cosa si ferma per primo e quale indicatore lo segnala.

| Scenario | Cosa si ferma per primo | Segnale da guardare |
|---|---|---|
| Blocco navale di Taiwan | Il GNL (scorte 12–14 giorni) e quindi l'elettricità delle fab; poi l'uscita di wafer, CoWoS e server. Gli aerei cargo potrebbero continuare per un po'. | Transiti PortWatch nello Stretto di Taiwan e di Luzon; esercitazioni; cavi tagliati |
| Conflitto aperto su Taiwan | Tutta la fonderia avanzata e il packaging: nessun sostituto per anni (Arizona fa 4 nm, packaging AP1 dal 2028). | Come sopra; TSM e SOX in borsa |
| Hormuz chiuso a lungo (in corso) | L'elio del Qatar (un terzo del mondo) e il GNL che alimenta Taiwan, Corea e Giappone; prezzi dell'energia europei. | Transiti a Hormuz; TTF; notizie su Ras Laffan |
| Ritorno dei controlli cinesi di ottobre 2025 | Magneti e componenti con terre rare cinesi oltre lo 0,1% del valore: motori, ventole, dischi rigidi; impianti di separazione fuori dalla Cina. | Testo MOFCOM dopo il 10 novembre; licenze e dati doganali |
| Stretta USA sulle DUV e sull'assistenza in Cina | Ricavi ASML dalla Cina (circa un quinto); risposta cinese con terre rare e gallio. | MATCH Act; decisioni dell'Aia; conti ASML |
| Uragano a Spruce Pine | Quarzo per i crogioli: scorte di alcuni mesi, poi meno wafer. | Stagione degli uragani; forza maggiore Sibelco o The Quartz Corp |

<a id="indicatori"></a>

## 14. Tutti gli indicatori e le soglie

Le soglie sono una **valutazione dell'osservatorio**, scelte per distinguere una situazione normale da una da seguire; non sono valori ufficiali. Indicatori *strutturali* (concentrazione) cambiano in anni e restano spesso «critici»: dicono dove si romperebbe la catena, non che si stia rompendo. Gli indicatori *congiunturali* si muovono in settimane.

| Collo | Indicatore | Tipo | Valore | Stato |
|---|---|---|---|---|
| Controlli cinesi su terre rare, gallio e germanio | Giorni alla fine della sospensione delle misure di ottobre 2025 (terre rare, regola dello 0,1%) | congiunturale | 1 giorni | {stato:critico} |
| Controlli cinesi su terre rare, gallio e germanio | Giorni alla fine della sospensione del divieto di export di gallio e germanio verso gli USA | congiunturale | 18 giorni | {stato:attenzione} |
| Controlli cinesi su terre rare, gallio e germanio | Quota cinese dell'estrazione di terre rare | strutturale | 69,2 % | {stato:critico} |
| Elio del Qatar bloccato a Hormuz | Transiti a Hormuz, media 7 giorni rispetto a un anno prima | congiunturale | -95,1 % | {stato:critico} |
| Elio del Qatar bloccato a Hormuz | Quota del Qatar nella produzione mondiale di elio | strutturale | 33,2 % | {stato:critico} |
| Quarzo ad alta purezza di Spruce Pine | Quota stimata di Spruce Pine nell'offerta di quarzo ad alta purezza (stima BloombergNEF: oltre l'80%) | strutturale | 80 % | {stato:critico} |
| Tantalio dal Kivu e dal Ruanda | Quota di Congo e Ruanda nell'estrazione di tantalio | strutturale | 68,0 % | {stato:critico} |
| Litografia EUV: un solo fornitore, in Olanda | Fornitori di scanner EUV al mondo | strutturale | 1 fornitori | {stato:critico} |
| Litografia EUV: un solo fornitore, in Olanda | Quota della Cina nelle vendite ASML 2026 (guida) | congiunturale | 20 % | {stato:normale} |
| Litografia EUV: un solo fornitore, in Olanda | ASML in borsa, variazione a 1 mese | congiunturale | -14,7 % | {stato:attenzione} |
| Fonderia avanzata concentrata a Taiwan | Quota TSMC dei ricavi mondiali di fonderia (2° trimestre 2026) | strutturale | 72,5 % | {stato:critico} |
| Fonderia avanzata concentrata a Taiwan | Transiti nello Stretto di Taiwan, media 7 giorni rispetto a un anno prima | congiunturale | 7,1 % | {stato:normale} |
| Fonderia avanzata concentrata a Taiwan | Danni a cavi sottomarini intorno a Taiwan negli ultimi 365 giorni | congiunturale | 1 eventi | {stato:attenzione} |
| Fonderia avanzata concentrata a Taiwan | TSMC (ADR) in borsa, variazione a 1 mese | congiunturale | -13,8 % | {stato:attenzione} |
| Packaging CoWoS | Divario tra domanda e offerta CoWoS a fine 2026 | congiunturale | 10 % | {stato:attenzione} |
| Memoria HBM e DRAM | Prezzi contrattuali DRAM nel 4° trimestre 2026, variazione sul trimestre (previsione) | congiunturale | 20 % | {stato:attenzione} |
| Memoria HBM e DRAM | SK Hynix in borsa, variazione a 1 mese | congiunturale | -34,3 % | {stato:critico} |
| Ottica: chip laser EML per l'1,6T | Carenza di chip EML da 200G per corsia (stima) | congiunturale | 60 % | {stato:critico} |
| Trasformatori e allacci alla rete | Tempi di consegna dei trasformatori elevatori (GSU), 1° trimestre 2026 | strutturale | 160 settimane | {stato:critico} |
| Energia di Taiwan per le fab | Scorte di GNL di Taiwan (estremo basso della forchetta 12–14 giorni) | congiunturale | 12 giorni | {stato:attenzione} |
| Costo dell'energia per i data center | Gas TTF (Europa) | congiunturale | 82,3 EUR/MWh | {stato:critico} |
| Costo dell'energia per i data center | Gas Henry Hub (USA) | congiunturale | 3,2 USD/MMBtu | {stato:normale} |
| Un solo progettista dominante e regole USA sui chip | Quota di Nvidia nei chip AI per data center 2026 (stima IDC riportata da terzi; forchetta delle stime 75–86%) | strutturale | 81 % | {stato:critico} |
| Un solo progettista dominante e regole USA sui chip | Nvidia in borsa, variazione a 1 mese | congiunturale | -22,6 % | {stato:attenzione} |

Riepilogo: su 13 colli di bottiglia, guardando solo gli indicatori congiunturali, 5 sono critici, 5 in attenzione, 3 normali o non misurati.

<a id="metodo"></a>

## 15. Metodo, limiti e trasparenza

- **Dati.** Il file docs/data/supply-chain-ai.json è costruito da raccolta/supply-chain-ai/raccogli.py a partire da voci curate a mano (raccolta/supply-chain-ai/*.json), ciascuna con fonte, link, data e affidabilità, e da altri file dell'osservatorio (ai.json, ai-mondo.json, stretti-dettaglio.json, portwatch.json, prezzi.json, cavi-incidenti.json, rete-elettrica.json, cavi.json). Le quote dei paesi sono calcolate dalle tabelle USGS; i giorni alle scadenze e lo stato degli indicatori sono calcolati dallo script.
- **Coordinate.** I nodi nuovi sono geocodificati con OpenStreetMap Nominatim a livello di comune, sede o sito (precisione nel file); quelli già presenti nella mappa riusano le coordinate di ai.json e ai-mondo.json. Il punto di una sede non è la posizione di un impianto.
- **Limiti.** Mancano da fonte verificata: quote per nodo tecnologico (3 nm, 2 nm), quote di mercato dei singoli fornitori di macchine, quota attuale del neon ucraino, volumi di cargo AI per aeroporto, quota mondiale del germanio e del polisilicio. Le quote dei chip AI (Nvidia, ASIC) e dei moduli ottici variano molto tra le fonti. Alcune fonti di stampa secondaria hanno affidabilità bassa e sono marcate.
- **Non è un consiglio di investimento.** I titoli sono collegati agli anelli per leggere la catena attraverso i mercati.
- **Uso di un assistente AI e trasparenza.** Questo report è stato scritto con l'aiuto di un assistente AI: chi scrive è Claude, un modello di Anthropic, sotto la cura e la responsabilità di Gabriele Giuliani. Anthropic è un cliente di questa catena: usa chip, server e data center descritti qui (per esempio il campus Amazon di New Carlisle). I dati che la riguardano vengono solo da fonti pubbliche e sono trattati come gli altri; nessuna valutazione è stata orientata a suo favore.

---

Gabriele Giuliani · Monitor geoeconomico. Scritto con l'aiuto di un assistente AI (Claude, modello di Anthropic; Anthropic è un cliente della catena descritta).
