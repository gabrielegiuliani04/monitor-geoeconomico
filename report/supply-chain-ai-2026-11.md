# La catena dell'AI, dalla miniera al data center — novembre 2026

*Dove sta ogni anello della catena dell'AI, chi lo controlla, dove si rompe.*

Gabriele Giuliani · Monitor geoeconomico · dati al 10 novembre 2026. Ogni numero ha fonte e data; le parti marcate *Valutazione* sono ragionamenti dell'osservatorio.

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
- [11. Europa e Italia: dove tocca la catena](#europa)
- [12. Scenari di rottura](#scenari)
- [13. Metodo, fonti e limiti](#metodo)
- [14. Appendice: tutti gli indicatori e i collegamenti](#appendice)
- [15. Revisione](#revisione)

<a id="in-breve"></a>

## 1. In breve

- **Pechino annuncia la proroga sulle terre rare, senza testo ufficiale.** Il 9 novembre la Cina ha prorogato al 10 gennaio 2027 la sospensione delle misure di ottobre 2025 (Reuters); il testo non è ancora sul sito del MOFCOM. Il divieto di gallio e germanio verso gli USA è sospeso fino al 27 novembre 2026. La Cina fa il 99% del gallio primario e il 69,2% delle terre rare ([USGS](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf), 2025).
- **Tre punti unici di rottura reggono la catena.** Gli scanner EUV escono solo da Veldhoven (Paesi Bassi); TSMC ha il 72,5% dei ricavi mondiali di fonderia (2° trimestre 2026, [TrendForce](https://www.trendforce.com/presscenter/news/20260909-13225.html)) e fa il 2 nm solo a Taiwan; il packaging CoWoS delle GPU è quasi tutto a Tainan e Chiayi. Arizona, Kumamoto e Dresda non cambiano il quadro prima del 2028.
- **Hormuz è quasi chiuso, lo Stretto di Taiwan no.** A Hormuz sono passate 4,4 navi al giorno nella settimana al 1 novembre 2026, −95% sulla stessa settimana del 2025 ([IMF PortWatch](https://portwatch.imf.org/)); il Qatar, 33,2% dell'elio mondiale, ha fermato la produzione il 2 marzo (AP). Nello Stretto di Taiwan 247 navi al giorno, +7,1% sulla stessa settimana del 2025.
- **La memoria è il collo di bottiglia che stringe.** L'HBM è divisa tra SK Hynix 50%, Samsung 33% e Micron 18% (Counterpoint, 2° trimestre 2026); TrendForce prevede prezzi contrattuali DRAM +20% sul trimestre nel 4° trimestre ([TrendForce](https://www.trendforce.com/news/2026/10/20/news-dram-prices-seen-rising-20-qoq-in-4q26-despite-slower-gains-ai-demand)). Per la Cina l'HBM è il limite della produzione Huawei.
- **In borsa salgono memoria e macchine, Nvidia resta sotto l'inizio d'anno.** Da inizio anno SK Hynix +87% (seduta del 10 novembre 2026, provvisorio), ASML +41%, indice SOX +42%, AMD +137%; Nvidia −4,2% (chiusure del 9 novembre 2026, prezzi.json). Nell'ultimo mese i semiconduttori correggono: SOX −20%.

> *Valutazione.* La catena dell'AI è lunga ma stretta in pochi punti, e quasi tutti sono in Asia orientale o dipendono da una sola società. Per l'Europa del Nord il legame più forte è anche il più solido: le macchine EUV di Veldhoven. I punti deboli sono a monte (terre rare, magneti, gallio, elio) e a valle (energia e trasformatori), più che nei chip.

> **Scadenze cinesi: stato al 10 novembre 2026**
>
> - **Divieto di export verso gli USA di gallio, germanio e antimonio (dicembre 2024)** — sospeso fino al 27 novembre 2026 (tra 17 giorni)
> - **Misure di ottobre 2025 (altre cinque terre rare, regola dello 0,1%, impianti e tecnologie)** — sospeso fino al 10 gennaio 2027 (tra 61 giorni); **proroga annunciata, testo primario non reperito** (scadenza precedente: 10 novembre 2026)
> - Le licenze cinesi su gallio e germanio (2023), sulle sette terre rare medie e pesanti (aprile 2025) e il divieto di export di elio (luglio 2026) sono in vigore in ogni caso.

<a id="catena"></a>

## 2. La catena in un colpo d'occhio

Otto anelli, dalla miniera al data center. Ogni riquadro mostra i paesi chiave (valutazione dell'osservatorio), quanti nodi e titoli quotati sono collegati e lo stato del collo di bottiglia peggiore. Le soglie degli indicatori sono una valutazione dell'osservatorio (sezione «Appendice»).

![La catena del valore dell'AI in otto anelli](grafici/sca-2026-11-catena.svg)

<small>La catena del valore dell'AI in otto anelli. Diagramma generato da docs/data/supply-chain-ai.json (70 nodi, 34 collegamenti, 13 colli di bottiglia; dati al 10 novembre 2026). Passare sopra un riquadro per l'elenco dei colli.</small>

<details><summary>Versione in tabella del diagramma</summary>

| Anello | Dove sta | Collo peggiore |
|---|---|---|
| 1. Materie prime | Cina (gallio, terre rare, fluorite, silicio), Cile e Congo (rame), Congo e Ruanda (tantalio), USA e Qatar (elio), North Carolina (quarzo), Ucraina (neon, fino al 2022). | ■ critico |
| 2. Macchine per fare chip | Paesi Bassi (Veldhoven), Germania (Oberkochen, Ditzingen), California (San Diego, Santa Clara, Fremont, Milpitas), Giappone (Tokyo). | ■ critico |
| 3. Wafer e fabbricazione | Taiwan (Hsinchu, Kaohsiung, Taichung), Arizona, Giappone (Kumamoto, Hokkaido), Corea (Pyeongtaek), Cina (Shanghai), Germania (Dresda), Irlanda. | ■ critico |
| 4. Packaging avanzato e memoria HBM | Taiwan (Tainan, Chiayi) per il CoWoS; Corea (Icheon, Cheongju, Onyang) per l'HBM; Giappone, Singapore e Indiana per la memoria in arrivo; Hefei per l'HBM cinese. | ■ critico |
| 5. Progetto dei chip e acceleratori | California (Santa Clara, Palo Alto, Mountain View), Shenzhen. | ■ critico |
| 6. Server, rete e assemblaggio | Taiwan (Nuova Taipei, Taoyuan), Messico (Jalisco), Texas (Houston, Dallas), Cina (Suzhou, Chengdu) per l'ottica, USA (Pennsylvania) per i laser. | ■ critico |
| 7. Logistica | Aeroporti di Taoyuan, Incheon, Schiphol, Anchorage, Pudong; Stretto di Taiwan, Mar Cinese Meridionale, Malacca, Hormuz. | ■ critico |
| 8. Energia e data center | Stati Uniti (Texas, Tennessee, Indiana, Georgia), Golfo, Malesia (Johor), Europa (Francia, Paesi del Nord, Italia); Taiwan per l'energia delle fab. | ■ critico |

</details>

<a id="anello-materie"></a>

## 3. Materie prime

**Dove sta.** Cina (gallio, terre rare, fluorite, silicio), Cile e Congo (rame), Congo e Ruanda (tantalio), USA e Qatar (elio), North Carolina (quarzo), Ucraina (neon, fino al 2022).

**Chi lo controlla.** Lo Stato cinese, con licenze all'export; poche società per il quarzo (Sibelco, The Quartz Corp); QatarEnergy per l'elio; gruppi armati nel Kivu per una parte del coltan.

Il rischio di questa settimana sono i controlli cinesi. Le licenze su gallio e germanio (agosto 2023) e sulle sette terre rare medie e pesanti (aprile 2025) sono in vigore e non sono mai state sospese. Il divieto di export di gallio, germanio e antimonio verso gli USA (dicembre 2024) è sospeso fino al 27 novembre 2026: una proroga non è stata trovata. Le misure di ottobre 2025, compresa la regola dello 0,1% di contenuto cinese nei prodotti esteri, erano sospese fino al 10 novembre 2026. Il 9 novembre il ministero del Commercio cinese (MOFCOM) ha annunciato una proroga di due mesi, fino al 10 gennaio 2027 ([Reuters, via The Star](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/11/09/china-extends-suspension-of-rare-earth-export-controls-until-january)); [Shanghai Metals Market](https://news.metal.com/newscontent/CNTOCBN4QTSC2L3BEOVBYILPAZVOOIHVV6INVPY-china-extends-suspension-of-rare-earth-export-controls-until-january-2027) ne riporta il testo come annuncio n. 58 del 2026. **Stato: proroga annunciata, non verificata sulla fonte primaria**: al 10 novembre l'annuncio non compare nell'[elenco ufficiale del MOFCOM](https://www.mofcom.gov.cn/zcfb/blgg/gg/2026/index.html), fermo al n. 52 del 26 ottobre. [Tech Times](https://www.techtimes.com/articles/330288/20261109/china-rare-earth-export-controls-pause-ends-tuesday-law-beijing-has-published-no-extension.htm), uscito il 9 novembre prima dell'annuncio, scriveva che nessun testo spostava la data.

<details><summary>Approfondimento (3 paragrafi)</summary>

Un chip per l'AI contiene poche decine di grammi di materiali, ma senza alcuni di essi la fabbrica si ferma. Il gallio serve ai semiconduttori di potenza e all'ottica, il germanio alla fibra, l'elio al raffreddamento dei wafer, il neon ai laser della litografia, la fluorite ai gas di incisione, il quarzo di Spruce Pine ai crogioli in cui si fonde il silicio. Rame e terre rare servono a valle: cavi, trasformatori, motori delle ventole e dei sistemi di raffreddamento, dischi rigidi.

La concentrazione è estrema e misurabile con l'ultima edizione del [USGS Mineral Commodity Summaries 2026](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026.pdf) (5 febbraio 2026, dati 2025): la tabella sotto calcola le quote dai dati di produzione per paese.

L'elio è il caso di scuola di un rischio logistico che diventa industriale. Il Qatar fa un terzo dell'elio mondiale (33,2% nel 2025, USGS) a Ras Laffan; QatarGas ha fermato la produzione il 2 marzo 2026 e dichiarato forza maggiore due giorni dopo, per la guerra con l'Iran ([WTOP/AP](https://wtop.com/news/2026/03/iran-war-halts-qatar-helium-output-threatening-global-tech-supply-chains/), marzo 2026). Lo stato attuale della produzione non è verificato da fonte primaria; Hormuz resta chiuso di fatto (portwatch.json). A giugno [Morningstar/Dow Jones](https://www.morningstar.com/news/dow-jones/202606253275/why-the-middle-east-helium-supply-shock-didnt-hit-chip-makers) spiegava perché lo shock non aveva colpito i produttori di chip: contratti di lungo periodo, fornitori diversi, caverne di stoccaggio e scorte negli impianti. Dal 10 luglio 2026 anche la Cina vieta temporaneamente l'export di elio ([annuncio MOFCOM n. 29](https://www.mofcom.gov.cn/zcfb/blgg/gg/2026/art/2026/art_e715aef77348447fb40cea835cdd8015.html)), ma ne produce poco (1,6% del mondo).

</details>

> *Valutazione.* Per l'Europa del Nord l'anello debole sono le terre rare. Il Baltico ha l'unico tratto europeo di filiera completa fuori dalla Cina, a Sillamäe e Narva in Estonia, a pochi chilometri dal confine russo; la Groenlandia (Danimarca) ha 1,5 milioni di tonnellate di riserve ma nessuna produzione.

![Quota del primo paese produttore, in % della produzione mondiale 2025 (stime), materie con primo produttore almeno al 30%](grafici/sca-2026-11-concentrazione.svg)

<small>Quota del primo paese produttore, in % della produzione mondiale 2025 (stime), materie con primo produttore almeno al 30%. Fonte: [USGS Mineral Commodity Summaries 2026](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026.pdf), 5 febbraio 2026; quote calcolate in docs/data/supply-chain-ai.json e uguali a quelle di minerali.json.</small>

Altre materie sotto licenza cinese toccano la catena. Quota della Cina nella produzione mondiale 2025: magnesio metallico 86,4%, tungsteno 78,7%, grafite naturale 77,8%, antimonio 36,1% ([minerali.json](https://www.usgs.gov/data/mineral-commodity-summaries-2026-data-release), USGS).

<details><summary>Produttori e quote per materia (USGS, dati 2025)</summary>

| Materia | A cosa serve | Primi produttori (quota della produzione mondiale) | Fonte USGS |
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
| Neon | miscele dei laser ad eccimeri della litografia DUV (sorgenti Cymer e Gigaphoton) | USGS pubblica solo Stati Uniti: 13,8% del totale mondiale; il resto non è ripartito per paese. Stima storica: Ucraina circa il 50% del neon mondiale nel 2022 (Cryoin a Odesa, Ingas a Mariupol); quasi tutto il neon ultrapuro importato dagli USA veniva dall'Ucraina | [Helium and rare gases](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-helium.pdf) |

<small>Quote calcolate da raccogli.py come produzione del paese / totale mondiale USGS (stime 2025); per il gallio la quota è quella dichiarata da USGS. Rame: estrazione; la Cina raffina il 48,3% del rame mondiale.</small>

</details>

<details><summary>Controlli cinesi all'export, 2023–2026</summary>

| Annuncio | Misura | Stato al 10 novembre 2026 | Fonte |
|---|---|---|---|
| 3 luglio 2023 | Licenza obbligatoria per esportare gallio e germanio e loro composti. | in vigore | [USGS, Mineral Commodity Summaries 2026: Gallium](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-gallium.pdf) |
| 3 dicembre 2024 | Divieto di export verso gli USA di gallio, germanio, antimonio e materiali superduri. | sospeso fino al 27 novembre 2026 (tra 17 giorni) | [Fastmarkets, «China suspends export prohibition on gallium, germanium, antimony, superhard materials to US»](https://www.fastmarkets.com/insights/china-suspends-export-prohibition-on-superhard-materials-us/) |
| 4 aprile 2025 | Licenze su sette terre rare medie e pesanti: samario, gadolinio, terbio, disprosio, lutezio, scandio, ittrio (e relativi magneti). | in vigore | [USGS, Mineral Commodity Summaries 2026: Rare Earths](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf) |
| 9 ottobre 2025 | Altre cinque terre rare (olmio, erbio, tulio, europio, itterbio); regola extraterritoriale dello 0,1% di contenuto cinese nei prodotti esteri; tecnologie ed impianti per estrazione, separazione e magneti; batterie e materiali superduri. | sospeso fino al 10 gennaio 2027 (tra 61 giorni); **proroga annunciata, testo primario non reperito** (scadenza precedente: 10 novembre 2026) | [Reuters, ripreso da The Star, «China extends suspension of rare earth export controls until January»](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/11/09/china-extends-suspension-of-rare-earth-export-controls-until-january) |
| 10 luglio 2026 | Divieto temporaneo di export di elio (codice doganale 2804290010), in vigore dalla pubblicazione; modifiche «con annuncio successivo». | in vigore | [MOFCOM, annuncio MOFCOM-Dogane n. 29 del 2026 (testo cinese)](https://www.mofcom.gov.cn/zcfb/blgg/gg/2026/art/2026/art_e715aef77348447fb40cea835cdd8015.html) |

<small>Per le misure di ottobre 2025 le fonti sono in disaccordo: vedi il testo sopra e il riquadro delle scadenze.</small>

</details>

**Collo di bottiglia: Controlli cinesi su terre rare, gallio e germanio.** La Cina fa il 99% del gallio primario e il 69% delle terre rare estratte; le licenze di aprile 2025 restano, le misure di ottobre 2025 e il divieto verso gli USA sono solo sospesi.

**Collo di bottiglia: Elio del Qatar bloccato a Hormuz.** Il Qatar fa un terzo dell'elio mondiale da Ras Laffan; dal 2 marzo 2026 Hormuz è chiuso di fatto. Le fab hanno scorte, ma l'elio non ha sostituti nel raffreddamento dei wafer.

**Collo di bottiglia: Quarzo ad alta purezza di Spruce Pine.** Due impianti in una sola valle della North Carolina forniscono la maggior parte del quarzo per i crogioli; l'uragano Helene li ha fermati nel 2024.

**Collo di bottiglia: Tantalio dal Kivu e dal Ruanda.** Congo e Ruanda fanno la maggior parte del tantalio estratto; la miniera di Rubaya è in mano al gruppo M23 da aprile 2024.

<details><summary>Dettagli dell'anello: 7 indicatori, 9 nodi, 3 titoli, cosa seguire</summary>

### Indicatori e soglie

| Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte, data del dato |
|---|---|---|---|---|
| Giorni alla fine della sospensione delle misure di ottobre 2025 (terre rare, regola dello 0,1%) | 61 giorni (proroga annunciata, testo primario non reperito) | 60 / 14 giorni | ● normale | [Reuters, ripreso da The Star, «China extends suspension of rare earth export controls until January»](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/11/09/china-extends-suspension-of-rare-earth-export-controls-until-january), 2026-11-09 |
| Giorni alla fine della sospensione del divieto di export di gallio e germanio verso gli USA | 17 giorni | 60 / 14 giorni | ▲ attenzione | [Fastmarkets, «China suspends export prohibition on gallium, germanium, antimony, superhard materials to US»](https://www.fastmarkets.com/insights/china-suspends-export-prohibition-on-superhard-materials-us/), 2025-11-09 |
| Quota cinese dell'estrazione di terre rare | 69,2 % | 40 / 60 % | ■ critico | [USGS, Mineral Commodity Summaries 2026: Rare Earths](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf), 2026-02-05 |
| Transiti a Hormuz, media 7 giorni rispetto a un anno prima | -95,1 % | -20 / -50 % | ■ critico | [IMF PortWatch (portwatch.json)](https://portwatch.imf.org/), 2026-11-01 |
| Quota del Qatar nella produzione mondiale di elio | 33,2 % | 20 / 30 % | ■ critico | [USGS, Mineral Commodity Summaries 2026: Helium and rare gases](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-helium.pdf), 2026-02-05 |
| Quota stimata di Spruce Pine nell'offerta di quarzo ad alta purezza (stima BloombergNEF: oltre l'80%) | 80 % | 50 / 75 % | ■ critico | [BNN Bloomberg (BloombergNEF)](https://bnnbloomberg.ca/investing/commodities/2024/10/02/hurricane-helene-halts-quartz-mines-vital-for-chipmaking-and-solar), 2024-10-02 |
| Quota di Congo e Ruanda nell'estrazione di tantalio | 68,0 % | 40 / 60 % | ■ critico | [USGS, Mineral Commodity Summaries 2026: Tantalum](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-tantalum.pdf), 2026-02-05 |

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| Spruce Pine (North Carolina): quarzo ad alta purezza | Stati Uniti | quarzo per i crogioli dei lingotti di silicio | 70–90% del quarzo commerciale ad alta purezza (stima Everstream); oltre 80% (BloombergNEF) | [BNN Bloomberg, «Hurricane Helene halts quartz mines vital for chipmaking and solar»](https://bnnbloomberg.ca/investing/commodities/2024/10/02/hurricane-helene-halts-quartz-mines-vital-for-chipmaking-and-solar), 2024-10-02 (media) |
| Bayan Obo (Mongolia Interna): terre rare | Cina | prima miniera di terre rare della Cina | Cina 69,2% di terre rare nel 2025 (calcolata da USGS, Mineral Commodity Summaries 2026) | [USGS, Mineral Commodity Summaries 2026: Rare Earths](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf), 2026-02-05 (media) |
| Mountain Pass (California): terre rare | Stati Uniti | unica miniera di terre rare degli USA | Stati Uniti 13,1% di terre rare nel 2025 (calcolata da USGS, Mineral Commodity Summaries 2026) | [USGS, Mineral Commodity Summaries 2026: Rare Earths](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-rare-earths.pdf), 2026-02-05 (media) |
| Rubaya (Nord Kivu, Congo): coltan | Congo (RD) | tantalio per condensatori e bersagli di deposizione | circa il 15% dell'offerta mondiale di tantalio (Global Witness, giugno 2026); frana con oltre 200 morti a fine gennaio 2026 (Argus) | [Argus Media, «Rubaya mine collapse and the tantalum supply chain»](https://www.argusmedia.com/en/news-and-insights/market-opinion-and-analysis-blog/rubaya-mine-collapse-tantalum-supply-chain), 2026-02-12 (media) |
| Ras Laffan (Qatar): elio dal gas naturale | Qatar | secondo produttore mondiale di elio | Qatar 33,2% di elio nel 2025 (calcolata da USGS, Mineral Commodity Summaries 2026) | [WTOP (AP), «Iran war halts Qatar helium output, threatening global tech supply chains»](https://wtop.com/news/2026/03/iran-war-halts-qatar-helium-output-threatening-global-tech-supply-chains/), 2026-03 (alta) |
| Odesa (Ucraina): purificazione del neon | Ucraina | neon per i laser della litografia DUV | Ucraina circa 50% del neon mondiale nel 2022 (USITC) | [USITC, Executive Briefing on Trade «Ukraine, neon, and semiconductors»](https://www.usitc.gov/publications/332/executive_briefings/ebot_decarlo_goodman_ukraine_neon_and_semiconductors.pdf), 2022 (media) |
| Mariupol (Ucraina occupata): neon | Ucraina | ex fornitore di neon per chip | — | [USITC, Executive Briefing on Trade «Ukraine, neon, and semiconductors»](https://www.usitc.gov/publications/332/executive_briefings/ebot_decarlo_goodman_ukraine_neon_and_semiconductors.pdf), 2022 (media) |
| Sillamäe (Estonia): separazione di terre rare | Estonia | separazione di terre rare leggere e, dal 2026, pesanti (terbio, disprosio) | — | [Shanghai Metals Market, «Neo Performance Materials Commissions Rare Earth Extraction Line in Estonia»](https://news.metal.com/newscontent/103853488-Neo-Performance-Materials-Commissions-Rare-Earth-Extraction-Line-in-Estonia-Strengthening-European-Supply-Chain), 2026-04 (media) |
| Narva (Estonia): magneti di terre rare | Estonia | fabbrica di magneti NdFeB, la prima di questa scala in Europa | 2.000 t/anno di capacità iniziale, poi 5.000 | [Shanghai Metals Market, «Neo Performance opens Europe's first rare earth magnet plant»](https://news.metal.com/newscontent/103541038/Neo-Performance-opens-Europe%E2%80%99s-first-rare-earth-magnet-plant), 2025-09 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Titoli collegati

Non ancora seguiti in prezzi.json: MP Materials (MP), terre rare USA (Mountain Pass); Lynas Rare Earths (LYC.AX), terre rare fuori dalla Cina (Australia, Malesia); Freeport-McMoRan (FCX), rame.

**Indicatori da seguire:** Testo ufficiale MOFCOM della proroga al 10 gennaio 2027 e decisione sul divieto verso gli USA che scade il 27 novembre 2026; Tassi di approvazione delle licenze cinesi e dati doganali di export di terre rare, gallio, germanio; Transiti a Hormuz (PortWatch) e stato di Ras Laffan; Stagione degli uragani in North Carolina (giugno–novembre); Notizie su Rubaya e sul Kivu (M23).

</details>

<a id="anello-attrezzature"></a>

## 4. Macchine per fare chip

**Dove sta.** Paesi Bassi (Veldhoven), Germania (Oberkochen, Ditzingen), California (San Diego, Santa Clara, Fremont, Milpitas), Giappone (Tokyo).

**Chi lo controlla.** ASML per la litografia (unico fornitore EUV), Applied Materials, Lam Research, KLA e Tokyo Electron per il resto; i governi di USA, Paesi Bassi e Giappone con le licenze.

È l'anello in cui l'Europa conta di più, e il legame più diretto con l'area di lavoro di questo osservatorio: **ogni scanner EUV del mondo esce da Veldhoven**, vicino a Eindhoven. Dentro ci sono le ottiche di Carl Zeiss SMT (Oberkochen, di cui ASML possiede circa un quarto), il laser CO2 di Trumpf (Ditzingen) e la sorgente di luce di Cymer, società di ASML a San Diego ([The Value Edge](https://thevalueedge.substack.com/p/asmls-supply-chain-bill-of-materials), analisi generata con un assistente AI: affidabilità bassa). La catena delle EUV attraversa quindi Paesi Bassi, Germania e Stati Uniti prima di arrivare a Taiwan, Corea, Giappone e Arizona.

<details><summary>Approfondimento (2 paragrafi)</summary>

Nel 3° trimestre 2026 ASML ha venduto 113 sistemi litografici nuovi (86 nel 2°) per 11,7 miliardi di euro di ricavi; per tutto il 2026 prevede 44–45 miliardi ([comunicato ASML del 14 ottobre 2026, depositato alla SEC](https://www.sec.gov/Archives/edgar/data/0000937966/000162828026065813/pressreleasefinancialresul.htm)). La Cina compra solo DUV e peserebbe circa il 20% delle vendite 2026 secondo la direzione (ai-mondo.json, trascrizione della conferenza di luglio): il comunicato di ottobre non dà la quota.

I controlli si sono stratificati: USA ottobre 2022 e ottobre 2023; Paesi Bassi dal 1° settembre 2023 e dal 7 settembre 2024 per le DUV a immersione 1970i e 1980i; Giappone dal 23 luglio 2023 per 23 tipi di macchine (licenza verso tutti i paesi, procedura semplificata per 42); USA 2 dicembre 2024 per 24 tipi di macchine, 3 software, l'HBM e 140 entità ([BIS](https://www.bis.gov/press-release/commerce-strengthens-export-controls-restrict-chinas-capability-produce-advanced-semiconductors-military)). Nel 2026 il fronte aperto è l'assistenza alle macchine già installate in Cina, che l'Aia ancora permette, e la proposta americana (MATCH Act) di vietare l'export in Cina di tutte le DUV a immersione e di spingere gli alleati ad allinearsi ([Bits&Chips](https://bits-chips.com/article/dutch-minister-pushes-back-on-us-bid-to-tighten-china-chip-controls/)).

</details>

> *Valutazione.* Un blocco dell'EUV è il colpo più grave per la catena, ma è anche il più improbabile perché tocca Paesi alleati. Il rischio concreto per Veldhoven è politico e commerciale (regole sulle DUV e sui servizi in Cina), non fisico.

<details><summary>Regole sull'export di macchine e chip (USA, Paesi Bassi, Giappone)</summary>

| Paese | Dal | Misura | Stato | Fonte |
|---|---|---|---|---|
| Stati Uniti | 7 ottobre 2022 | Prime regole su chip avanzati per l'AI e macchine per produrre chip avanzati in Cina; aggiornate nell'ottobre 2023. | in vigore | [CSIS, «Understanding the Biden Administration's Updated Export Controls»](https://www.csis.org/analysis/understanding-biden-administrations-updated-export-controls) |
| Giappone | 23 luglio 2023 | Licenza obbligatoria per 23 tipi di macchine per chip avanzati (pulizia, deposizione, trattamento termico, esposizione, incisione, ispezione, comprese parti EUV) verso tutti i paesi; procedura semplificata per 42 paesi e territori «amici». | in vigore | [Hogan Lovells (HLC), «Japan's new chip equipment export rules take effect»](https://www.hlc.com/en/publications/japans-new-chip-equipment-export-rules-take-effect) |
| Paesi Bassi | 1 settembre 2023 | Licenza nazionale per esportare fuori dall'UE le macchine litografiche DUV a immersione più avanzate. | in vigore | [Hogan Lovells (HLC), «Japan's new chip equipment export rules take effect» (cita le misure olandesi del 30 giugno 2023)](https://www.hlc.com/en/publications/japans-new-chip-equipment-export-rules-take-effect) |
| Paesi Bassi | 7 settembre 2024 | Licenza olandese anche per i sistemi DUV a immersione NXT:1970i e 1980i (prima sotto regole USA). | in vigore | [Export Compliance Daily](https://exportcompliancedaily.com/article/2024/09/10/netherlands-expands-chip-equipment-controls-asml-expects-no-impact-2409090024) |
| Stati Uniti | 2 dicembre 2024 | Controlli su 24 tipi di macchine per chip e 3 software, su tutta la memoria HBM in produzione; 140 entità aggiunte alla Entity List. | in vigore | [BIS, comunicato «Commerce Strengthens Export Controls to Restrict China's Capability to Produce Advanced Semiconductors for Military Applications»](https://www.bis.gov/press-release/commerce-strengthens-export-controls-restrict-chinas-capability-produce-advanced-semiconductors-military) |
| Stati Uniti | 29 settembre 2025 | «Affiliates Rule»: le società possedute al 50% o più da entità in lista subiscono gli stessi limiti. | sospeso fino al 10 gennaio 2027 (tra 61 giorni) | [Tech Times (regola BIS pubblicata nel Federal Register il 9 novembre 2026, FR Doc. 2026-22793)](https://www.techtimes.com/articles/330288/20261109/china-rare-earth-export-controls-pause-ends-tuesday-law-beijing-has-published-no-extension.htm) |
| Stati Uniti | 2026 | Vieterebbe l'export in Cina di tutte le DUV a immersione, limiterebbe ancora l'assistenza e creerebbe meccanismi per spingere gli alleati ad allinearsi: toccherebbe vendite e assistenza delle DUV ASML in Cina. | proposto | [Bits&Chips, «Dutch minister pushes back on US bid to tighten China chip controls»](https://bits-chips.com/article/dutch-minister-pushes-back-on-us-bid-to-tighten-china-chip-controls/) |
| Stati Uniti | 2026-01 | Licenze per vendere Nvidia H200 alla Cina con condizioni: verifica di laboratorio negli USA, dazio del 25%, tetti per cliente; Blackwell e Rubin esclusi. | in vigore | [TechRepublic, «US Approves Nvidia H200 Sales to China, But Shipments Remain Stalled»](https://www.techrepublic.com/article/news-nvidia-h200-ai-chip-sales-china-stalled/) |

</details>

**Collo di bottiglia: Litografia EUV: un solo fornitore, in Olanda.** Ogni chip AI avanzato passa da scanner EUV costruiti solo a Veldhoven, con ottiche da Oberkochen e laser da Ditzingen. Gli USA spingono per estendere i limiti alle DUV e all'assistenza in Cina.

<details><summary>Dettagli dell'anello: 3 indicatori, 8 nodi, 6 titoli, cosa seguire</summary>

### Indicatori e soglie

| Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte, data del dato |
|---|---|---|---|---|
| Fornitori di scanner EUV al mondo | 1 fornitori | 2 / 1 fornitori | ■ critico | [ai-mondo.json (ASML, fornitore unico al mondo di scanner EUV)](https://statementdog.com/analysis/ASML/earnings_calls/316926), 2026-07 |
| Quota della Cina nelle vendite ASML 2026 (guida) | 20 % | 25 / 40 % | ● normale | [XenoSpectrum / Seeking Alpha sui risultati ASML del 3° trimestre 2026 (guida del direttore finanziario Roger Dassen)](https://xenospectrum.com/en/asml-china-sales-q3-2026/), 2026-10-14 |
| ASML in borsa, variazione a 1 mese | -15,0 % | -10 / -25 % | ▲ attenzione | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/ASML), 2026-11-09 |

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| ASML, Veldhoven (Paesi Bassi): scanner EUV | Paesi Bassi | unico produttore al mondo di macchine litografiche EUV; assemblaggio finale | 100% delle EUV; Cina circa 20% delle vendite ASML 2026 (guida del direttore finanziario, solo DUV) | [ASML, risultati del 3° trimestre 2026 (comunicato)](https://seekingalpha.com/pr/20684919), 2026-10-14 (alta) |
| Carl Zeiss SMT, Oberkochen (Germania): ottiche EUV | Germania | specchi multistrato dell'ottica EUV | fornitore unico delle ottiche EUV di ASML | [The Value Edge, «ASML's Supply Chain, Bill of Materials...» (analisi generata con un assistente AI e citata dall'autore)](https://thevalueedge.substack.com/p/asmls-supply-chain-bill-of-materials), 2025 (bassa) |
| Trumpf, Ditzingen (Germania): laser CO2 per EUV | Germania | laser di potenza che vaporizza le gocce di stagno della sorgente EUV | fornitore unico del laser della sorgente EUV | [The Value Edge, «ASML's Supply Chain, Bill of Materials...» (analisi generata con un assistente AI e citata dall'autore)](https://thevalueedge.substack.com/p/asmls-supply-chain-bill-of-materials), 2025 (bassa) |
| Cymer, San Diego (California): sorgenti di luce | Stati Uniti | modulo sorgente EUV e laser ad eccimeri DUV (usano neon) | — | [The Value Edge, «ASML's Supply Chain, Bill of Materials...» (analisi generata con un assistente AI e citata dall'autore)](https://thevalueedge.substack.com/p/asmls-supply-chain-bill-of-materials), 2025 (bassa) |
| Applied Materials, Santa Clara (California) | Stati Uniti | deposizione, incisione, impianto ionico, ispezione | Cina circa il 35% delle vendite nel trimestre maggio–luglio 2025 | [TipRanks, «Applied Materials stock slides after warning of $600M revenue hit from new U.S. export rules»](https://www.tipranks.com/news/applied-materials-stock-amat-slides-after-warning-of-600m-revenue-hit-from-new-u-s-export-rules), 2025-10-02 (media) |
| Lam Research, Fremont (California) | Stati Uniti | incisione e deposizione (chiave per HBM e memoria 3D) | — | [TipRanks (reazione dei titoli alla Affiliates Rule)](https://www.tipranks.com/news/applied-materials-stock-amat-slides-after-warning-of-600m-revenue-hit-from-new-u-s-export-rules), 2025-10-02 (media) |
| KLA, Milpitas (California) | Stati Uniti | ispezione e metrologia dei wafer | — | [TipRanks (reazione dei titoli alla Affiliates Rule)](https://www.tipranks.com/news/applied-materials-stock-amat-slides-after-warning-of-600m-revenue-hit-from-new-u-s-export-rules), 2025-10-02 (media) |
| Tokyo Electron, Tokyo (Giappone) | Giappone | deposizione, rivestimento e sviluppo del resist (coater/developer), incisione | — | [Hogan Lovells (HLC), regole giapponesi del 2023](https://www.hlc.com/en/publications/japans-new-chip-equipment-export-rules-take-effect), 2023-07 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| ASML (ASML) | litografia EUV e DUV (Veldhoven) | 1.513,20 USD | −15% | +41% | +49% |
| Indice dei semiconduttori (PHLX SOX) (SOX) | termometro dell'intera filiera dei chip | 10.034 USD | −20% | +42% | +44% |

<small>Prezzi da prezzi.json (Yahoo Finance): chiusure del 9 novembre 2026 salvo dove indicato; * = valore provvisorio (seduta in corso). Variazioni rispetto alla chiusura di un mese prima, del 31 dicembre 2025 e di un anno prima.</small>

Non ancora seguiti in prezzi.json: Applied Materials (AMAT), deposizione, incisione; Lam Research (LRCX), incisione e deposizione; KLA (KLAC), ispezione e metrologia; Tokyo Electron (8035.T), deposizione, coater/developer, incisione.

**Indicatori da seguire:** Ordini e quota Cina nei conti trimestrali ASML (prossimi a gennaio 2027); Testo e iter del MATCH Act; decisioni del governo olandese sulle licenze di assistenza; Elenco BIS delle entità e regola sulle affiliate (sospesa fino al 10 gennaio 2027).

</details>

<a id="anello-fabbricazione"></a>

## 5. Wafer e fabbricazione

**Dove sta.** Taiwan (Hsinchu, Kaohsiung, Taichung), Arizona, Giappone (Kumamoto, Hokkaido), Corea (Pyeongtaek), Cina (Shanghai), Germania (Dresda), Irlanda.

**Chi lo controlla.** TSMC, con distacco; poi Samsung, SMIC e Intel; Rapidus come progetto statale giapponese.

TSMC ha avuto il 72,5% dei ricavi mondiali di fonderia nel 2° trimestre 2026, Samsung il 5,9%, SMIC il 5,4% ([TrendForce, 9 settembre 2026](https://www.trendforce.com/presscenter/news/20260909-13225.html)). Sui nodi avanzati la concentrazione è più forte: il 2 nm è in volume solo a Hsinchu e Kaohsiung dalla fine del 2025, e i chip AI di Nvidia, AMD, Broadcom e Google escono da linee TSMC a 3–4 nm. Quote per nodo da fonte verificata: non trovate.

<details><summary>Approfondimento (2 paragrafi)</summary>

La diversificazione è reale ma lenta. In Arizona TSMC produce a 4 nm, il 3 nm arriverà nel 2° semestre 2027 e il piano è salito a 265 miliardi di dollari ([BetaNews](https://betanews.com/article/tsmc-100-billion-arizona-chip-expansion/)); però i wafer americani tornano a Taiwan per il packaging. In Europa ESMC a Dresda farà chip da 28–12 nm per l'auto, non per l'AI, e i macchinari arriveranno solo nel 2° semestre 2027.

SMIC produce a 7 nm senza EUV i chip Huawei; i suoi ricavi sono cresciuti del 20% nel trimestre. Nexperia (Nijmegen) mostra l'altro lato del rischio europeo: un intervento statale olandese a settembre 2025 ha diviso la società in due, con la parte cinese a Dongguan.

</details>

**Collo di bottiglia: Fonderia avanzata concentrata a Taiwan.** TSMC ha il 72,5% dei ricavi di fonderia e il 2 nm è in volume solo a Hsinchu e Kaohsiung; lo Stretto di Taiwan è il punto unico di rottura.

<details><summary>Dettagli dell'anello: 4 indicatori, 13 nodi, 5 titoli, cosa seguire</summary>

### Indicatori e soglie

| Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte, data del dato |
|---|---|---|---|---|
| Quota TSMC dei ricavi mondiali di fonderia (2° trimestre 2026) | 72,5 % | 50 / 70 % | ■ critico | [TrendForce, classifica fonderie 2° trimestre 2026](https://www.trendforce.com/presscenter/news/20260909-13225.html), 2026-09-09 |
| Transiti nello Stretto di Taiwan, media 7 giorni rispetto a un anno prima | 7,1 % | -15 / -40 % | ● normale | [IMF PortWatch (portwatch.json)](https://portwatch.imf.org/), 2026-11-01 |
| Danni a cavi sottomarini intorno a Taiwan negli ultimi 365 giorni | 1 eventi | 1 / 3 eventi | ▲ attenzione | [cavi-incidenti.json (osservatorio)](https://www.submarinecablemap.com/), 2026-11-10 |
| TSMC (ADR) in borsa, variazione a 1 mese | -14,3 % | -10 / -25 % | ▲ attenzione | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/TSM), 2026-11-09 |

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

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| TSMC (ADR) (TSM) | fonderia avanzata e CoWoS | 388,62 USD | −14% | +28% | +36% |
| Indice dei semiconduttori (PHLX SOX) (SOX) | termometro dell'intera filiera dei chip | 10.034 USD | −20% | +42% | +44% |

<small>Prezzi da prezzi.json (Yahoo Finance): chiusure del 9 novembre 2026 salvo dove indicato; * = valore provvisorio (seduta in corso). Variazioni rispetto alla chiusura di un mese prima, del 31 dicembre 2025 e di un anno prima.</small>

Non ancora seguiti in prezzi.json: Samsung Electronics (005930.KS), fonderia, DRAM, HBM; Intel (INTC), fonderia 18A negli USA; SMIC (0981.HK), fonderia cinese (chip Huawei).

**Indicatori da seguire:** Quote di fonderia trimestrali (TrendForce, prossima a dicembre 2026); Ricavi mensili di TSMC (pubblicati intorno al 10 di ogni mese); Avanzamento di Arizona Fab 2 e del packaging AP1.

</details>

<a id="anello-packaging-memoria"></a>

## 6. Packaging avanzato e memoria HBM

**Dove sta.** Taiwan (Tainan, Chiayi) per il CoWoS; Corea (Icheon, Cheongju, Onyang) per l'HBM; Giappone, Singapore e Indiana per la memoria in arrivo; Hefei per l'HBM cinese.

**Chi lo controlla.** TSMC per il CoWoS; SK Hynix, Samsung e Micron per l'HBM; CXMT in Cina.

Una GPU per l'AI non è un chip ma un pacchetto: il die logico di TSMC viene montato accanto a più pile di memoria HBM su un interposer (CoWoS). Questo passaggio avviene quasi tutto a Taiwan. La capacità CoWoS di TSMC passa da 65.000–75.000 wafer al mese nel 2025 a un obiettivo di 120.000–130.000 nel 2026; Nvidia ha circa il 60% delle assegnazioni 2026, Broadcom circa il 15%, AMD circa l'11% ([Tom's Hardware](https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia), maggio 2026). Per fine 2027 [KGI](https://www.kgi.com.hk/en/-/media/files/kgishk/research-reports/tw-reports/tsmc_2330-tt_09032026e.pdf) stima 170.000 wafer al mese.

Nel 2° trimestre 2026 l'HBM era divisa tra SK Hynix 50%, Samsung 33% e Micron 18% ([Counterpoint](https://counterpointresearch.com/insights/global-dram-and-hbm-market-share)): Samsung ha recuperato dodici punti in un trimestre. L'AI toglie capacità alla DRAM normale: TrendForce prevede prezzi contrattuali DRAM +20% sul trimestre nel 4° trimestre 2026 ([TrendForce, 20 ottobre 2026](https://www.trendforce.com/news/2026/10/20/news-dram-prices-seen-rising-20-qoq-in-4q26-despite-slower-gains-ai-demand)).

<details><summary>Approfondimento (1 paragrafi)</summary>

Per la Cina l'HBM è il vincolo vero: i controlli USA di dicembre 2024 hanno tolto la memoria coreana, e secondo [Epoch AI](https://epoch.ai/publications/huaweis-roadmap-to-2031) Huawei produrrà nel 2026 meno del 4% del calcolo AI di Nvidia.

</details>

**Collo di bottiglia: Packaging CoWoS.** Ogni GPU di fascia alta passa dal CoWoS di TSMC a Taiwan; Nvidia ha prenotato circa il 60% della capacità 2026. Il packaging in Arizona arriverà dal 2028.

**Collo di bottiglia: Memoria HBM e DRAM.** Tre produttori (SK Hynix, Samsung, Micron) fanno tutta l'HBM occidentale; l'AI toglie capacità alla DRAM normale e i prezzi salgono. SK Hynix vede carenza fino al 2030.

<details><summary>Dettagli dell'anello: 3 indicatori, 9 nodi, 6 titoli, cosa seguire</summary>

### Indicatori e soglie

| Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte, data del dato |
|---|---|---|---|---|
| Divario tra domanda e offerta CoWoS a fine 2026 | 10 % | 5 / 15 % | ▲ attenzione | [TrendForce (ripreso in ai-mondo.json): dal 20% al 10% a fine 2026](https://www.trendforce.com/news/2026/01/21/news-tsmc-advanced-packaging-capex-projected-to-grow-24-cagr-in-2025-27-chiayi-ap7-targets-wmcm-and-copos/), 2026-06-15 |
| Prezzi contrattuali DRAM nel 4° trimestre 2026, variazione sul trimestre (previsione) | 20 % | 10 / 30 % | ▲ attenzione | [TrendForce, «DRAM prices seen rising 20% QoQ in 4Q26»](https://www.trendforce.com/news/2026/10/20/news-dram-prices-seen-rising-20-qoq-in-4q26-despite-slower-gains-ai-demand), 2026-10-20 |
| SK Hynix in borsa, variazione a 1 mese | -27,7 % | -10 / -25 % | ■ critico | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/000660.KS), 2026-11-10 |

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| TSMC AP8, Tainan: CoWoS | Taiwan | impacchettamento CoWoS delle GPU con l'HBM | capacità CoWoS di TSMC: obiettivo 120.000–130.000 wafer al mese nel 2026 (da 65.000–75.000 nel 2025); Nvidia circa il 60% delle assegnazioni 2026, Broadcom circa il 15%, AMD circa l'11%; KGI stima 170.000 wafer al mese a fine 2027 | [Tom's Hardware, «The custom AI ASIC state of play (May 2026)»; KGI Securities, nota su TSMC (9 marzo 2026)](https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia), 2026-05 (media) |
| TSMC AP7, Chiayi: SoIC e WMCM | Taiwan | impacchettamento avanzato 3D (SoIC) | — | [TrendForce](https://www.trendforce.com/news/2026/01/21/news-tsmc-advanced-packaging-capex-projected-to-grow-24-cagr-in-2025-27-chiayi-ap7-targets-wmcm-and-copos/), 2026-01-21 (alta) |
| SK Hynix, Icheon (Corea): sede e DRAM | Corea del Sud | primo produttore di HBM | SK Hynix 50% dei ricavi HBM nel 2° trimestre 2026 (58% nel 1°) | [Counterpoint Research, quote HBM 2° trimestre 2026 (ripreso da SamMobile e Daum)](https://counterpointresearch.com/insights/global-dram-and-hbm-market-share), 2026-09-03 (alta) |
| SK Hynix M15X, Cheongju: DRAM per HBM | Corea del Sud | nuova fabbrica di DRAM per HBM | — | [The Star (Reuters)](https://www.thestar.com.my/tech/tech-news/2026/01/15/exclusive-sk-hynix-speeds-up-new-chip-fab-opening-to-meet-memory-demand-executive-says), 2026-01-15 (media) |
| SK Hynix, West Lafayette (Indiana): HBM | Stati Uniti | packaging HBM negli USA dal 2029 | — | [Korea Times (Reuters)](https://www.koreatimes.co.kr/world/20260828/sk-hynix-to-start-ai-chip-volume-production-in-indiana-in-2029), 2026-08-28 (alta) |
| Samsung, Onyang (Asan): packaging HBM | Corea del Sud | assemblaggio e test HBM | Samsung 33% dei ricavi HBM nel 2° trimestre 2026 (21% nel 1°) | [Counterpoint Research, quote HBM 2° trimestre 2026](https://counterpointresearch.com/insights/global-dram-and-hbm-market-share), 2026-09-03 (alta) |
| Micron, Hiroshima (Giappone): DRAM con EUV e HBM | Giappone | DRAM avanzata per HBM | Micron 18% dei ricavi HBM nel 2° trimestre 2026 (21% nel 1°) | [Counterpoint Research, quote HBM 2° trimestre 2026](https://counterpointresearch.com/insights/global-dram-and-hbm-market-share), 2026-09-03 (alta) |
| Micron, Singapore: packaging HBM | Singapore | assemblaggio HBM | — | [Micron via Researchpool](https://app.researchpool.com/company/mu-us5951121038-micron-technology-inc-HzQHxJMipr/press/micron-technology-inc-mu-micron-breaks-ground-on-new-hbm-advanced-packaging-facility-in-singapo-D8fDEA5799), 2025-01 (media) |
| CXMT, Hefei (Cina): DRAM e HBM cinese | Cina | memoria per i chip AI cinesi | CXMT 10% del mercato DRAM+HBM nel 2° trimestre 2026 | [Counterpoint Research (ripreso da Huawei Central)](https://www.huaweicentral.com/cxmt-records-strong-growth-in-q2-2026-global-dram-and-hbm-market/), 2026-08 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| TSMC (ADR) (TSM) | fonderia avanzata e CoWoS | 388,62 USD | −14% | +28% | +36% |
| SK Hynix (000660.KS) | primo produttore di HBM | 1.215.000 KRW * (seduta del 10 novembre 2026) | −28% | +87% | +100% |
| Western Digital (WDC) | dischi rigidi per i data center (magneti di terre rare) | 289,78 USD | −27% | +68% | +78% |
| Indice dei semiconduttori (PHLX SOX) (SOX) | termometro dell'intera filiera dei chip | 10.034 USD | −20% | +42% | +44% |

<small>Prezzi da prezzi.json (Yahoo Finance): chiusure del 9 novembre 2026 salvo dove indicato; * = valore provvisorio (seduta in corso). Variazioni rispetto alla chiusura di un mese prima, del 31 dicembre 2025 e di un anno prima.</small>

Non ancora seguiti in prezzi.json: Samsung Electronics (005930.KS), fonderia, DRAM, HBM; Micron Technology (MU), HBM e DRAM.

**Indicatori da seguire:** Prezzi contrattuali DRAM e HBM (TrendForce, mensili); Quote HBM trimestrali (Counterpoint); Capacità CoWoS e nuove sedi (AP7, AP8, Arizona AP1); Qualifiche HBM4 presso Nvidia.

</details>

<a id="anello-progettazione"></a>

## 7. Progetto dei chip e acceleratori

**Dove sta.** California (Santa Clara, Palo Alto, Mountain View), Shenzhen.

**Chi lo controlla.** Nvidia, con larga maggioranza; AMD; Broadcom e Marvell come co-progettisti dei chip dei grandi cloud (TPU di Google, Trainium di Amazon, MTIA di Meta); Huawei in Cina.

Il progetto è l'anello più ricco e il meno fisico: nessuno di questi gruppi possiede una fabbrica di chip avanzati. Le stime della quota di Nvidia nei ricavi degli acceleratori AI 2026 vanno dal 70% all'86% a seconda che si contino i chip su misura dei cloud: 81% per IDC, 75% per Silicon Analysts; AMD il 5–7% ([commandlinux](https://commandlinux.com/ai/ai-chip-market-share/), sintesi di stime di terzi, affidabilità bassa). Broadcom e Marvell fanno circa il 95% della co-progettazione di ASIC; Broadcom è il secondo cliente CoWoS di TSMC ([Tom's Hardware](https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia)).

<details><summary>Approfondimento (1 paragrafi)</summary>

Le regole americane decidono dove vanno i chip: da gennaio 2026 gli USA permettono di vendere l'H200 in Cina con dazio del 25% e verifiche, ma a maggio nessun chip risultava spedito perché Pechino non aveva dato il via libera ([TechRepublic](https://www.techrepublic.com/article/news-nvidia-h200-ai-chip-sales-china-stalled/)).

</details>

> *Valutazione.* Il potere di mercato di questo anello dipende da anelli che non controlla (CoWoS, HBM, EUV). In borsa si vede in parte: da inizio anno Nvidia e Broadcom sono in calo mentre memoria e macchine salgono; l'eccezione è AMD, più che raddoppiata (tabella dei titoli).

**Collo di bottiglia: Un solo progettista dominante e regole USA sui chip.** Nvidia ha la grande maggioranza dei chip AI per data center; dove vanno i chip lo decidono le licenze USA (H200 per la Cina con dazio del 25%) e la risposta di Pechino.

<details><summary>Dettagli dell'anello: 2 indicatori, 5 nodi, 5 titoli, cosa seguire</summary>

### Indicatori e soglie

| Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte, data del dato |
|---|---|---|---|---|
| Quota di Nvidia nei chip AI per data center 2026 (stima IDC riportata da terzi; forchetta delle stime 70–86%) | 81 % | 50 / 70 % | ■ critico | [commandlinux.com (sintesi di stime IDC)](https://commandlinux.com/ai/ai-chip-market-share/), 2026 |
| Nvidia in borsa, variazione a 1 mese | -22,1 % | -10 / -25 % | ▲ attenzione | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/NVDA), 2026-11-09 |

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| Nvidia, Santa Clara (California) | Stati Uniti | GPU per data center (Blackwell, Rubin), reti NVLink e InfiniBand | circa 81% dei ricavi degli acceleratori AI nel 2026 secondo IDC, 75% secondo Silicon Analysts; forchetta delle stime 70–86% a seconda che si contino i chip su misura dei cloud (riprese da commandlinux.com); circa 70% secondo Tom's Hardware | [Tom's Hardware, «The custom AI ASIC state of play (May 2026)» e sintesi di stime IDC](https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia), 2026-05 (media) |
| AMD, Santa Clara (California) | Stati Uniti | acceleratori Instinct | 5–7% dei ricavi degli acceleratori AI nel 2026 (stime Silicon Analysts e IDC riportate da terzi) | [sintesi di stime IDC (commandlinux.com)](https://commandlinux.com/ai/ai-chip-market-share/), 2026 (bassa) |
| Broadcom, Palo Alto (California): ASIC su misura | Stati Uniti | co-progetta i TPU di Google e i chip di Meta; switch Ethernet | Broadcom e Marvell insieme circa il 95% della co-progettazione di ASIC per l'AI; Broadcom secondo cliente CoWoS di TSMC, circa il 15% delle assegnazioni 2026 (circa 150.000 wafer) | [Tom's Hardware, «The custom AI ASIC state of play (May 2026)»](https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia), 2026-05 (media) |
| Google, Mountain View (California): TPU | Stati Uniti | acceleratori propri (TPU) per uso interno e cloud | — | [Tom's Hardware, «The custom AI ASIC state of play (May 2026)»](https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia), 2026-05 (media) |
| Huawei, Shenzhen: Ascend | Cina | acceleratori Ascend (910C, 950) prodotti da SMIC | meno del 4% del calcolo AI prodotto da Nvidia nel 2026 secondo Epoch AI | [Epoch AI, «Huawei's roadmap to 2031»](https://epoch.ai/publications/huaweis-roadmap-to-2031), 2026 (alta) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| Nvidia (NVDA) | GPU per data center | 178,67 USD | −22% | −4,2% | −5,0% |
| AMD (AMD) | acceleratori Instinct | 508,58 USD | −16% | +137% | +118% |
| Broadcom (AVGO) | ASIC su misura (TPU) e switch | 319,48 USD | −12% | −7,7% | −8,6% |
| Alphabet (GOOGL) | TPU e data center | 288,15 USD | −18% | −7,9% | +3,3% |
| Indice dei semiconduttori (PHLX SOX) (SOX) | termometro dell'intera filiera dei chip | 10.034 USD | −20% | +42% | +44% |

<small>Prezzi da prezzi.json (Yahoo Finance): chiusure del 9 novembre 2026 salvo dove indicato; * = valore provvisorio (seduta in corso). Variazioni rispetto alla chiusura di un mese prima, del 31 dicembre 2025 e di un anno prima.</small>

**Indicatori da seguire:** Conti trimestrali di Nvidia (prossimi a fine novembre 2026); Licenze USA per la Cina e risposta di Pechino; Quota degli ASIC nei server AI (TrendForce).

</details>

<a id="anello-server-rete"></a>

## 8. Server, rete e assemblaggio

**Dove sta.** Taiwan (Nuova Taipei, Taoyuan), Messico (Jalisco), Texas (Houston, Dallas), Cina (Suzhou, Chengdu) per l'ottica, USA (Pennsylvania) per i laser.

**Chi lo controlla.** Foxconn, Quanta e Wistron per i rack; InnoLight, Coherent ed Eoptolink per l'ottica; Coherent e Lumentum per i laser EML.

Le GPU impacchettate diventano schede, vassoi e rack completi (GB300, VR200) negli impianti dei grandi assemblatori taiwanesi. Foxconn è il primo, con oltre il 44% dei rack AI spediti (circa 3.700; [TechNews](https://finance.technews.tw/2026/05/12/foxconn-leads-quanta-and-wistron-in-ai-server-shipments/), maggio 2026). L'assemblaggio si sta spostando verso il mercato finale: Messico (Jalisco), Texas (Foxconn a Houston, Wistron a Dallas), Thailandia. Il risultato si vede nell'export di Taiwan: le macchine per l'elaborazione dati (server e schede grafiche) sono diventate la prima voce, 192,6 miliardi di dollari in gennaio–agosto 2026, +87,5% sugli stessi mesi del 2025 e il 62,8% verso gli USA ([STAT Times](https://www.stattimes.com/latest-news/is-taiwans-ai-engine-on-fire-1360979)).

<details><summary>Approfondimento (2 paragrafi)</summary>

La rete ottica dei cluster dipende dalla Cina per i moduli (InnoLight intorno al 27% dei ricavi) e da due società americane per i chip laser EML: per [Yole](https://www.yolegroup.com/strategy-insights/opinion-optical-transceivers-at-the-chokepoint-of-ai-growth-and-supply-chain-constraints/) è il vincolo dell'1,6T nel 2026.

Fuori dal rack, il collo di bottiglia è elettrico: i tempi di consegna dei trasformatori elevatori hanno superato le 160 settimane nel 1° trimestre 2026 ([Reuters via Kitco](https://www.kitco.com/news/off-the-wire/2026-07-09/us-power-companies-scramble-secure-equipment-surging-data-center)).

</details>

**Collo di bottiglia: Ottica: chip laser EML per l'1,6T.** I chip EML da 200G per corsia vengono da pochi fornitori (Coherent, Lumentum e un terzo); per Yole sono il vincolo dell'1,6T nel 2026. I moduli sono assemblati soprattutto in Cina.

<details><summary>Dettagli dell'anello: 1 indicatori, 7 nodi, 8 titoli, cosa seguire</summary>

### Indicatori e soglie

| Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte, data del dato |
|---|---|---|---|---|
| Carenza di chip EML da 200G per corsia (stima) | 60 % | 10 / 30 % | ■ critico | [cnyes, blog di analisi (北風窗, in cinese): divario oltre il 60%](https://hao.cnyes.com/post/271963), 2026-10-12 |

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| Foxconn (Hon Hai), Tucheng (Nuova Taipei) | Taiwan | primo assemblatore di server AI e rack completi | oltre il 44% dei rack AI spediti (circa 3.700 rack; Quanta circa 2.100, Wistron 1.300–1.400), secondo stampa taiwanese | [TechNews, «AI 伺服器出貨鴻海領先廣達、緯創»](https://finance.technews.tw/2026/05/12/foxconn-leads-quanta-and-wistron-in-ai-server-shipments/), 2026-05-12 (media) |
| Quanta Computer, Guishan (Taoyuan) | Taiwan | secondo assemblatore di server AI | — | [TrendForce, Server Market Bulletin (gennaio 2026)](https://www.trendforce.com/research/download/RP260122RF3), 2026-01-22 (media) |
| Foxconn, Guadalajara (Jalisco, Messico): server GB200 | Messico | assemblaggio di server Nvidia per i data center USA (Stargate) | — | [Expansión, «Foxconn ya hace data centers de Nvidia en México»](https://expansion.mx/tecnologia/2025/04/07/foxconn-ya-hace-data-centers-de-nvidia-en-mexico), 2025-04-07 (media) |
| Foxconn, Houston (Texas): supercomputer Nvidia | Stati Uniti | assemblaggio negli USA | — | [Nvidia, «NVIDIA to Manufacture American-Made AI Supercomputers in US for First Time»](https://blogs.nvidia.com/blog/nvidia-manufacture-american-made-ai-supercomputers-us/), 2025-04-14 (alta) |
| InnoLight (Zhongji Innolight), Suzhou: moduli ottici | Cina | primo produttore di transceiver ottici 800G e 1,6T | circa 27% dei ricavi mondiali dei transceiver per data center (Counterpoint); 50–60% dell'1,6T nel 2026 (Yole) | [Yole Group, «Optical transceivers at the chokepoint of AI growth»](https://www.yolegroup.com/strategy-insights/opinion-optical-transceivers-at-the-chokepoint-of-ai-growth-and-supply-chain-constraints/), 2026 (media) |
| Eoptolink, Chengdu: moduli ottici | Cina | terzo produttore di transceiver per data center | — | [Counterpoint Research, «FCC China ban: AI component»](https://counterpointresearch.com/en/insights/fcc-china-ban-ai-component), 2026 (media) |
| Coherent, Saxonburg (Pennsylvania): laser e moduli ottici | Stati Uniti | secondo produttore di transceiver; chip laser EML insieme a Lumentum | circa 17% dei ricavi dei transceiver per data center (Counterpoint) | [Counterpoint Research, «FCC China ban: AI component»](https://counterpointresearch.com/en/insights/fcc-china-ban-ai-component), 2026 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| Western Digital (WDC) | dischi rigidi per i data center (magneti di terre rare) | 289,78 USD | −27% | +68% | +78% |
| Broadcom (AVGO) | ASIC su misura (TPU) e switch | 319,48 USD | −12% | −7,7% | −8,6% |

<small>Prezzi da prezzi.json (Yahoo Finance): chiusure del 9 novembre 2026 salvo dove indicato; * = valore provvisorio (seduta in corso). Variazioni rispetto alla chiusura di un mese prima, del 31 dicembre 2025 e di un anno prima.</small>

Non ancora seguiti in prezzi.json: Hon Hai (Foxconn) (2317.TW), assemblaggio server AI; Quanta Computer (2382.TW), assemblaggio server AI; Wistron (3231.TW), assemblaggio server AI; Coherent (COHR), laser EML e transceiver; Zhongji Innolight (300308.SZ), transceiver 800G/1,6T; Eoptolink (300502.SZ), transceiver.

**Indicatori da seguire:** Export mensile di Taiwan per categoria (Ministero delle Finanze); Ricavi mensili di Foxconn, Quanta, Wistron; Tempi di consegna di trasformatori e quadri (Wood Mackenzie); Prezzi e disponibilità dei transceiver 1,6T.

</details>

<a id="anello-logistica"></a>

## 9. Logistica

**Dove sta.** Aeroporti di Taoyuan, Incheon, Schiphol, Anchorage, Pudong; Stretto di Taiwan, Mar Cinese Meridionale, Malacca, Hormuz.

**Chi lo controlla.** Vettori cargo (China Airlines, EVA Air, integratori), aeroporti e, in caso di crisi, le marine militari.

Lo Stretto di Taiwan è il punto unico di rottura. Il 48% delle 5.400 portacontainer in servizio nel mondo vi è passato almeno una volta tra gennaio e luglio 2022 (Bloomberg, ripreso in stretti-dettaglio.json). Nello scenario estremo di Bloomberg Economics, una guerra tra USA e Cina per Taiwan costerebbe all'economia mondiale circa 10.600 miliardi di dollari (9,6% del PIL mondiale) nel primo anno ([Insurance Journal](https://www.insurancejournal.com/news/international/2026/02/12/857770.htm), febbraio 2026). In un blocco, le aziende che dipendono dai chip di Taiwan perderebbero fino a 1.600 miliardi di dollari di ricavi l'anno secondo [Rhodium](https://rhg.com/research/taiwan-economic-disruptions/) (stima del 2022). I cavi sottomarini intorno all'isola sono già stati danneggiati più volte (cavi-incidenti.json).

<details><summary>Approfondimento (2 paragrafi)</summary>

I chip e i server viaggiano in aereo: valgono molto e pesano poco. Le macchine viaggiano smontate: una EUV richiede circa 40 container, 20 camion e 3 Boeing 747 cargo ([Asia Times](https://asiatimes.com/2021/09/the-150mn-machine-that-is-changing-the-world/); [DHL](https://www.dhl.com/global-en/delivered/innovation/focus-on-the-details.html)); una High-NA è andata in Oregon in 43 container. Le materie (elio, quarzo, GNL per le centrali di Taiwan) viaggiano per nave.

Il cargo aereo di Taiwan è trainato dall'AI: per EVA Air il carico legato all'AI vale il 40–50% del cargo, il Nord America circa il 70% dei ricavi cargo (stampa taiwanese). Le rotte transpacifiche fanno scalo ad Anchorage.

</details>

> *Valutazione.* In un blocco navale gli aerei potrebbero continuare a portare chip per qualche tempo, ma il GNL no: Taiwan si fermerebbe per mancanza di energia prima che per mancanza di trasporti. Terremoti (aprile 2024: TSMC ha recuperato oltre il 70% delle macchine in 10 ore, [Tom's Hardware](https://www.tomshardware.com/tech-industry/tsmc-resumes-chip-production-following-biggest-earthquake-in-25-years-incurred-no-damage-to-its-critical-tools)), siccità e blackout sono i rischi ricorrenti.

<details><summary>Dettagli dell'anello: 10 nodi, 2 titoli, cosa seguire</summary>

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
| Stretto di Taiwan | Taiwan | passaggio obbligato di quasi ogni carico da e per le fab di Taiwan | — | [Bloomberg, ripreso da SupplyChainBrain (stretti-dettaglio.json)](https://www.supplychainbrain.com/articles/35419-taiwan-tensions-raise-risks-in-one-of-busiest-shipping-lanes), 2022-08-02 (media) |
| Stretto di Hormuz | Oman | uscita del GNL e dell'elio del Qatar | — | [IEA, Strait of Hormuz Factsheet (febbraio 2026), su dati Kpler](https://iea.blob.core.windows.net/assets/c8248eba-8689-46d9-ae4b-b858b59c0f1c/StraitofHormuz2026-Factsheet.pdf), 2026-02 (alta) |
| Stretto di Malacca | Malesia | rotta marittima Europa/Golfo–Asia orientale; accanto ai data center di Johor | — | [Anadolu Agency, su dati IEA ed EIA (ripreso da stretti.json)](https://www.aa.com.tr/en/energy/general/around-70-of-global-oil-demand-transported-through-strategic-maritime-chokepoints/55347), 2026-03-10 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Titoli collegati

Non ancora seguiti in prezzi.json: EVA Airways (2618.TW), cargo aereo AI da Taoyuan; China Airlines (2610.TW), cargo aereo AI da Taoyuan.

**Indicatori da seguire:** Transiti nello Stretto di Taiwan, di Luzon e di Malacca (PortWatch, settimanali); Incidenti ai cavi intorno a Taiwan; Esercitazioni cinesi intorno a Taiwan; Tariffe cargo aereo Asia–Nord America.

</details>

<a id="anello-energia-dc"></a>

## 10. Energia e data center

**Dove sta.** Stati Uniti (Texas, Tennessee, Indiana, Georgia), Golfo, Malesia (Johor), Europa (Francia, Paesi del Nord, Italia); Taiwan per l'energia delle fab.

**Chi lo controlla.** I grandi cloud (Microsoft, Amazon, Google, Meta, Oracle), i laboratori (OpenAI, xAI, Anthropic come cliente), i gestori di rete e i produttori di energia.

L'energia entra nella catena due volte. A monte, Taiwan produce metà dell'elettricità col gas e tiene scorte di GNL per 12–14 giorni ([Focus Taiwan](https://focustaiwan.tw/business/202603210010)); ha spento le centrali nucleari e ora valuta il riavvio di Maanshan ([FDD](https://www.fdd.org/analysis/in-major-reversal-taiwan-seeks-to-rewire-its-energy-strategy-by-restarting-its-nuclear-plants/)). A valle, i campus americani si scontrano con i tempi dei trasformatori e degli allacci, quelli europei con il prezzo: i progetti a gas come Ferrera Erbognone legano l'AI italiana al TTF, la Francia sfrutta il nucleare (il campus di Fouju, 1,4 GW, è a circa 55 km dalla centrale di Nogent-sur-Seine).

<details><summary>Approfondimento (2 paragrafi)</summary>

Secondo l'IEA i data center hanno consumato circa 485 TWh nel 2025 (+17%) e arriveranno a circa 950 TWh nel 2030, intorno al 3% dell'elettricità mondiale; i consumi dei siti dedicati all'AI sono cresciuti del 50% nel 2025 ([IEA, Key questions on energy and AI](https://www.iea.org/reports/key-questions-on-energy-and-ai/executive-summary): pagina non raggiungibile da qui, cifre riprese dal sommario IEA citato dalla stampa).

Il denaro non manca: per il 2026 Amazon indica circa 220 miliardi di dollari di spese in conto capitale, Alphabet 195–205, Microsoft 170–190, Meta 135–145 (guide aziendali di fine ottobre, fonti secondarie discordi; investimenti.json). La maggior parte va negli USA.

</details>

> *Valutazione.* Per l'Europa del Nord il vantaggio è l'elettricità pulita e il clima freddo (Paesi nordici, Finlandia), il limite è la capacità di rete; il legame con la mappa è nei livelli rete-elettrica e interconnessioni.

**Collo di bottiglia: Trasformatori e allacci alla rete.** Il denaro c'è, i trasformatori no: i tempi di consegna dei trasformatori elevatori superano i tre anni e le utility comprano con cinque anni di anticipo.

**Collo di bottiglia: Energia di Taiwan per le fab.** Taiwan importa quasi tutta l'energia, produce metà dell'elettricità col gas e tiene scorte di GNL per meno di due settimane: un blocco navale colpirebbe le fab anche senza toccarle.

**Collo di bottiglia: Costo dell'energia per i data center.** In Europa i progetti a gas (come Ferrera Erbognone) legano l'AI al TTF e quindi a Hormuz; negli USA conta il prezzo dell'Henry Hub e la capacità di rete.

<details><summary>Dettagli dell'anello: 4 indicatori, 9 nodi, 8 titoli, cosa seguire</summary>

### Indicatori e soglie

| Indicatore | Valore | Soglie (attenzione / critico) | Stato | Fonte, data del dato |
|---|---|---|---|---|
| Tempi di consegna dei trasformatori elevatori (GSU), 1° trimestre 2026 | 160 settimane | 52 / 104 settimane | ■ critico | [Reuters, ripreso da Kitco: «US power companies scramble to secure equipment»](https://www.kitco.com/news/off-the-wire/2026-07-09/us-power-companies-scramble-secure-equipment-surging-data-center), 2026-07-09 |
| Scorte di GNL di Taiwan (estremo basso della forchetta 12–14 giorni) | 12 giorni | 14 / 11 giorni | ▲ attenzione | [Focus Taiwan (dichiarazione del presidente Lai)](https://focustaiwan.tw/business/202603210010), 2026-03-21 |
| Gas TTF (Europa) | 82,3 EUR/MWh | 40 / 70 EUR/MWh | ■ critico | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/TTF%3DF), 2026-11-09 |
| Gas Henry Hub (USA) | 3,2 USD/MMBtu | 4 / 6 USD/MMBtu | ● normale | [Yahoo Finance (prezzi.json)](https://finance.yahoo.com/quote/NG%3DF), 2026-11-09 |

### Dove sono i nodi

| Nodo | Paese | Ruolo | Quota o peso | Fonte (affidabilità) |
|---|---|---|---|---|
| Centrale nucleare di Maanshan (Taiwan) | Taiwan | nucleare spento nel 2025, riavvio in esame | gas al 50,5% della generazione di Taiwan a luglio 2026; scorte di GNL 12–14 giorni (minimo legale 11) | [Focus Taiwan (scorte di GNL dette dal presidente Lai)](https://focustaiwan.tw/business/202603210010), 2026-03-21 (media) |
| Stargate Abilene (Texas) | Stati Uniti | campus OpenAI-Oracle-Crusoe | — | [Epoch AI](https://epoch.ai/blog/openai-stargate-where-the-us-sites-stand), 2026-04-17 (alta) |
| xAI Colossus 2, Memphis | Stati Uniti | secondo campus AI per potenza nei dati Epoch (946 MW), dopo New Carlisle | — | [Epoch AI (via techjacksolutions)](https://techjacksolutions.com/?p=83881), 2026-09-22 (media) |
| Amazon-Anthropic New Carlisle (Indiana) | Stati Uniti | campus Amazon usato da Anthropic (Project Rainier); il più grande per potenza nei dati Epoch (1.037 MW) | — | [Epoch AI (via techjacksolutions)](https://techjacksolutions.com/?p=83881), 2026-09-22 (media) |
| Microsoft Fairwater Atlanta | Stati Uniti | campus AI di Microsoft | — | [Epoch AI (via techjacksolutions)](https://techjacksolutions.com/?p=83881), 2026-09-22 (media) |
| DayOne Nusajaya, Johor (Malesia) | Malesia | primo polo AI fuori dagli USA nei dati Epoch | — | [Epoch AI, AI data centers](https://epoch.ai/data/ai-data-centers), 2026-10-02 (alta) |
| Stargate UAE, Abu Dhabi | Emirati | campus da 5 GW (1.000 MW IT previsti nel 2028) | — | [Epoch AI, AI data centers](https://epoch.ai/data/ai-data-centers), 2025-11-16 (media) |
| Campus IA di Fouju (Francia) | Francia | sottostazione da 1,4 GW di potenza finale; la centrale nucleare di Nogent-sur-Seine è a circa 55 km in linea d'aria | — | [Eiffage, comunicato](https://www.privacy.eiffage.com/files/live/sites/metal/files/publications/PR_Eiffage_Campus%2520AI%2520enters%2520the%2520implementation%2520phase_20260602.pdf), 2026-06-02 (media) |
| Campus AI Eni-Khazna, Ferrera Erbognone | Italia | progetto italiano a gas con cattura della CO2 | — | [DatacenterDynamics](https://www.datacenterdynamics.com/es/noticias/las-empresas-italianas-eni-y-khazna-se-asocian-para-construir-un-centro-de-datos-de-500-mw-en-las-afueras-de-mil%C3%A1n/), 2025-07 (media) |

<small>Coordinate nel file di dati (precisione indicata per ogni punto).</small>

### Titoli collegati

| Titolo | Ruolo nella catena | Ultimo | 1 mese | Da inizio anno | 1 anno |
|---|---|---|---|---|---|
| Alphabet (GOOGL) | TPU e data center | 288,15 USD | −18% | −7,9% | +3,3% |
| Microsoft (MSFT) | data center (Fairwater) | 545,18 USD | +1,9% | +13% | +9,7% |
| Amazon (AMZN) | data center (New Carlisle), chip Trainium | 266,93 USD | +1,7% | +16% | +9,2% |
| Meta (META) | data center | 641,37 USD | −11% | −2,8% | +3,2% |
| Oracle (ORCL) | data center Stargate (Abilene) | 119,79 USD | −15% | −39% | −50% |
| Gas TTF (Europa) (TTF) | costo dell'energia dei data center europei a gas | 82,33 EUR * | +1,1% | +192% | +164% |
| Gas Henry Hub (USA) (HH) | costo del gas per le centrali dei data center USA | 3,20 USD * | −0,5% | −13% | −26% |

<small>Prezzi da prezzi.json (Yahoo Finance): chiusure del 9 novembre 2026 salvo dove indicato; * = valore provvisorio (seduta in corso). Variazioni rispetto alla chiusura di un mese prima, del 31 dicembre 2025 e di un anno prima.</small>

Non ancora seguiti in prezzi.json: Freeport-McMoRan (FCX), rame.

**Indicatori da seguire:** Prezzi del gas TTF e Henry Hub (prezzi.json); Aste di capacità PJM e code di allaccio; Iter del riavvio di Maanshan; Aggiornamenti IEA sui consumi dei data center.

</details>

<a id="europa"></a>

## 11. Europa e Italia: dove tocca la catena

- **Magneti di terre rare: la dipendenza più netta.** Nel 2025 l'UE ha comprato dalla Cina l'88,3% dei magneti permanenti (NdFeB) importati da fuori l'Unione, 1.061 milioni di dollari su 1.201; l'Italia l'80,1% dei suoi (91,9 milioni di dollari). Sono i magneti di motori, ventole, pompe e dischi rigidi dei data center (commercio.json, UN Comtrade).
- **Terre rare a monte dei magneti.** La Cina pesa il 78,4% dei metalli delle terre rare importati dall'UE nel 2025; per gli ossidi e composti separati il 39,2%, seguita da Norvegia e Malesia. Gli acquisti italiani sono piccoli e passano da altri paesi UE (Francia, Austria, Paesi Bassi, Estonia), che il dato doganale registra come paesi di spedizione, non di origine.
- **Silicio ad altissima purezza: dipendenza americana, non cinese.** L'UE importa il 73,3% del silicio sopra il 99,99% dagli USA; l'Italia lo compra per il 58,3% dalla Danimarca (paese di spedizione).
- **Veldhoven (ASML)** è il nodo più critico della catena che si trovi in Europa: unico produttore di EUV, a 10,8 km da una linea da 380 kV (rete-elettrica.json). Le macchine partono smontate verso Taiwan, Corea, Giappone e USA; per via aerea l'uscita naturale è Schiphol (valutazione: ASML non pubblica gli aeroporti).
- **Nexperia (Nijmegen)** mostra il rischio opposto: la presa di controllo dello Stato olandese (settembre 2025) e la risposta cinese hanno spezzato una catena Europa–Cina. Non tocca i chip AI, ma è il precedente da tenere a mente per ASML.
- **Danimarca e Groenlandia.** La Groenlandia ha 1.500.000 tonnellate di riserve di terre rare (USGS) e nessuna produzione: è un'opzione di lungo periodo, non un'offerta. Gli Stretti danesi non sono una rotta della catena dei chip.
- **Baltico.** In Estonia, a Sillamäe (a 37,6 km da una linea da 450 kV HVDC Estlink 2) e Narva (a 63,7 km da una linea da 450 kV HVDC Estlink 2), Neo Performance Materials separa terre rare (anche terbio e disprosio dal 2026) e produce magneti (2.000 t l'anno all'avvio, 5.000 in prospettiva): il tratto di filiera europea più completo fuori dalla Cina, a pochi chilometri dal confine russo. Da seguire: sicurezza della zona di confine e dei cavi del Baltico (cavi-incidenti.json).
- **Italia.** Il campus Eni-Khazna di Ferrera Erbognone (500 MW nella prima fase, a gas con cattura della CO2) lega l'AI italiana al prezzo del gas TTF e quindi a Hormuz (valutazione).

<details><summary>Import di UE e Italia per voce doganale (2025, primi tre fornitori)</summary>

| Voce | Uso nella catena | Importatore | Import, milioni di USD | Primi fornitori (quota) | Cina |
|---|---|---|---|---|---|
| Silicio (>=99,99%) (HS 280461) | silicio ad altissima purezza per polisilicio e wafer | UE-27, da fuori UE | 141 | Stati Uniti 73,3%; Cina 13,9%; Singapore 3,3% | 13,9% |
| Silicio (>=99,99%) (HS 280461) | silicio ad altissima purezza per polisilicio e wafer | Italia | 40,3 | Danimarca 58,3%; Germania 22,5%; Corea del Sud 9,3% | — |
| Metalli delle terre rare, scandio e ittrio (HS 280530) | metalli delle terre rare (leghe per magneti) | UE-27, da fuori UE | 12,7 | Cina 78,4%; Vietnam 8,3%; Stati Uniti 3,7% | 78,4% |
| Metalli delle terre rare, scandio e ittrio (HS 280530) | metalli delle terre rare (leghe per magneti) | Italia | 1,3 (trascurabile) | Francia 77,6%; Stati Uniti 8,0%; Cina 4,8% | 4,8% |
| Composti delle terre rare (escluso cerio) (HS 284690) | composti delle terre rare (ossidi separati) | UE-27, da fuori UE | 98,8 | Cina 39,2%; Norvegia 21,6%; Malesia 12,4% | 39,2% |
| Composti delle terre rare (escluso cerio) (HS 284690) | composti delle terre rare (ossidi separati) | Italia | 5,5 | Austria 29,3%; Paesi Bassi 21,2%; Estonia 18,2% | — |
| Grafite artificiale (HS 380110) | grafite artificiale (elettrodi, anodi) | UE-27, da fuori UE | 426 | Cina 66,1%; Giappone 9,7%; Stati Uniti 7,0% | 66,1% |
| Grafite artificiale (HS 380110) | grafite artificiale (elettrodi, anodi) | Italia | 39,4 | Germania 23,2%; Cina 15,5%; Stati Uniti 14,6% | 15,5% |
| Catodi di rame raffinato (HS 740311) | rame raffinato per cavi, sbarre e trasformatori | UE-27, da fuori UE | 8.238 | Congo (RD) 40,2%; Cile 25,2%; Perù 5,9% | — |
| Catodi di rame raffinato (HS 740311) | rame raffinato per cavi, sbarre e trasformatori | Italia | 4.693 | Congo (RD) 20,5%; Bulgaria 18,1%; Spagna 12,2% | — |
| Gallio, germanio, indio, niobio, vanadio grezzi (voce mista) (HS 811292) | gallio e germanio (voce doganale mista con indio, niobio, vanadio) | UE-27, da fuori UE | 126 | Brasile 45,5%; Cina 28,5%; Stati Uniti 14,9% | 28,5% |
| Gallio, germanio, indio, niobio, vanadio grezzi (voce mista) (HS 811292) | gallio e germanio (voce doganale mista con indio, niobio, vanadio) | Italia | 14,5 | Paesi Bassi 51,9%; Germania 29,7%; Francia 9,2% | — |
| Magneti permanenti metallici (NdFeB) (HS 850511) | magneti NdFeB per motori, ventole, pompe e dischi rigidi | UE-27, da fuori UE | 1.201 | Cina 88,3%; Stati Uniti 2,8%; Svizzera 2,7% | 88,3% |
| Magneti permanenti metallici (NdFeB) (HS 850511) | magneti NdFeB per motori, ventole, pompe e dischi rigidi | Italia | 91,9 | Cina 80,1%; Germania 7,2%; Francia 6,1% | 80,1% |

<small>Fonte: commercio.json (UN Comtrade, anno 2025). Per l'Italia gli acquisti dentro l'UE sono attribuiti al paese di spedizione, non di origine; «trascurabile» = valore molto piccolo, segnalato così nel file.</small>

</details>

<a id="scenari"></a>

## 12. Scenari di rottura

Ragionamenti dell'osservatorio, non previsioni: nessuna probabilità numerica. Per ogni scenario, che cosa si ferma per primo e quale indicatore lo segnala.

| Scenario | Cosa si ferma per primo | Segnale da guardare |
|---|---|---|
| Blocco navale di Taiwan | Il GNL (scorte dichiarate di 12–14 giorni, dato non verificato da qui) e quindi l'elettricità delle fab; poi l'uscita di wafer, CoWoS e server. Gli aerei cargo potrebbero continuare per un po'. | Transiti PortWatch nello Stretto di Taiwan e di Luzon; esercitazioni; cavi tagliati |
| Conflitto aperto su Taiwan | Tutta la fonderia avanzata e il packaging: nessun sostituto per anni (Arizona fa 4 nm, packaging in Arizona dal 2028). | Come sopra; TSM e SOX in borsa |
| Hormuz chiuso a lungo (in corso) | L'elio del Qatar (un terzo del mondo) e il GNL che alimenta Taiwan, Corea e Giappone; prezzi dell'energia europei. | Transiti a Hormuz; TTF; notizie su Ras Laffan |
| Ritorno dei controlli cinesi di ottobre 2025 | Magneti e componenti con terre rare cinesi oltre lo 0,1% del valore: motori, ventole, dischi rigidi; impianti di separazione fuori dalla Cina. L'UE compra dalla Cina l'88% dei magneti importati. | Testo MOFCOM della proroga al 10 gennaio 2027; licenze e dati doganali |
| Stretta USA sulle DUV e sull'assistenza in Cina | Ricavi ASML dalla Cina (circa un quinto nel 2026); risposta cinese con terre rare e gallio. | MATCH Act; decisioni dell'Aia; conti ASML |
| Uragano a Spruce Pine | Quarzo per i crogioli: scorte di alcuni mesi, poi meno wafer. | Stagione degli uragani; forza maggiore Sibelco o The Quartz Corp |

<a id="metodo"></a>

## 13. Metodo, fonti e limiti

- **Dati.** Il file docs/data/supply-chain-ai.json è costruito da raccolta/supply-chain-ai/raccogli.py a partire da voci curate a mano (raccolta/supply-chain-ai/*.json), ciascuna con fonte, link, data e affidabilità, e da altri file dell'osservatorio (ai.json, ai-mondo.json, stretti-dettaglio.json, portwatch.json, prezzi.json, cavi-incidenti.json, rete-elettrica.json, cavi.json, minerali.json, commercio.json, investimenti.json). Le quote dei paesi sono calcolate dalle tabelle USGS e confrontate con minerali.json; i giorni alle scadenze e lo stato degli indicatori sono calcolati dallo script al 10 novembre 2026.
- **Date.** PortWatch: settimana al 1 novembre 2026. Prezzi: chiusure del 9 novembre 2026, salvo dove indicato. Quote USGS: produzione 2025 (stime), pubblicate il 5 febbraio 2026. Commercio: anno 2025 (UN Comtrade).
- **Coordinate.** I nodi nuovi sono geocodificati con OpenStreetMap Nominatim a livello di comune, sede o sito (precisione nel file); quelli già presenti nella mappa riusano le coordinate di ai.json e ai-mondo.json. Il punto di una sede non è la posizione di un impianto.
- **Limiti.** Mancano da fonte verificata: quote per nodo tecnologico (3 nm, 2 nm), quote di mercato dei singoli fornitori di macchine, quota attuale del neon ucraino, volumi di cargo AI per aeroporto, quota mondiale del germanio e del polisilicio, stato attuale della produzione di elio a Ras Laffan, testo ufficiale della proroga cinese del 9 novembre. Le quote dei chip AI (Nvidia, ASIC) e dei moduli ottici variano molto tra le fonti. Le fonti di stampa secondaria e le analisi generate con assistenti AI hanno affidabilità bassa e sono marcate.
- **Soglie.** Le soglie degli indicatori sono una valutazione dell'osservatorio: gli indicatori strutturali (concentrazione) restano spesso «critici» e dicono dove si romperebbe la catena, non che si stia rompendo.
- **Non è un consiglio di investimento.** I titoli sono collegati agli anelli per leggere la catena attraverso i mercati.
- **Uso di un assistente AI e trasparenza.** Raccolta delle voci, script, stesura e revisione sono stati fatti con l'aiuto di un assistente AI (Claude, un modello di Anthropic), sotto la cura e la responsabilità di Gabriele Giuliani, che risponde delle scelte e delle valutazioni. Anthropic è un cliente di questa catena: usa chip, server e data center descritti qui (per esempio il campus Amazon di New Carlisle). I dati che la riguardano vengono solo da fonti pubbliche e sono trattati come gli altri.

<a id="appendice"></a>

## 14. Appendice: tutti gli indicatori e i collegamenti

Su 13 colli di bottiglia, guardando solo gli indicatori congiunturali (che si muovono in settimane), 4 sono critici, 6 in attenzione, 3 normali o non misurati. Le soglie sono una **valutazione dell'osservatorio**, non valori ufficiali.

<details><summary>Tutti gli indicatori (24)</summary>

| Collo | Indicatore | Tipo | Valore | Stato |
|---|---|---|---|---|
| Controlli cinesi su terre rare, gallio e germanio | Giorni alla fine della sospensione delle misure di ottobre 2025 (terre rare, regola dello 0,1%) | congiunturale | 61 giorni | ● normale |
| Controlli cinesi su terre rare, gallio e germanio | Giorni alla fine della sospensione del divieto di export di gallio e germanio verso gli USA | congiunturale | 17 giorni | ▲ attenzione |
| Controlli cinesi su terre rare, gallio e germanio | Quota cinese dell'estrazione di terre rare | strutturale | 69,2 % | ■ critico |
| Elio del Qatar bloccato a Hormuz | Transiti a Hormuz, media 7 giorni rispetto a un anno prima | congiunturale | -95,1 % | ■ critico |
| Elio del Qatar bloccato a Hormuz | Quota del Qatar nella produzione mondiale di elio | strutturale | 33,2 % | ■ critico |
| Quarzo ad alta purezza di Spruce Pine | Quota stimata di Spruce Pine nell'offerta di quarzo ad alta purezza (stima BloombergNEF: oltre l'80%) | strutturale | 80 % | ■ critico |
| Tantalio dal Kivu e dal Ruanda | Quota di Congo e Ruanda nell'estrazione di tantalio | strutturale | 68,0 % | ■ critico |
| Litografia EUV: un solo fornitore, in Olanda | Fornitori di scanner EUV al mondo | strutturale | 1 fornitori | ■ critico |
| Litografia EUV: un solo fornitore, in Olanda | Quota della Cina nelle vendite ASML 2026 (guida) | congiunturale | 20 % | ● normale |
| Litografia EUV: un solo fornitore, in Olanda | ASML in borsa, variazione a 1 mese | congiunturale | -15,0 % | ▲ attenzione |
| Fonderia avanzata concentrata a Taiwan | Quota TSMC dei ricavi mondiali di fonderia (2° trimestre 2026) | strutturale | 72,5 % | ■ critico |
| Fonderia avanzata concentrata a Taiwan | Transiti nello Stretto di Taiwan, media 7 giorni rispetto a un anno prima | congiunturale | 7,1 % | ● normale |
| Fonderia avanzata concentrata a Taiwan | Danni a cavi sottomarini intorno a Taiwan negli ultimi 365 giorni | congiunturale | 1 eventi | ▲ attenzione |
| Fonderia avanzata concentrata a Taiwan | TSMC (ADR) in borsa, variazione a 1 mese | congiunturale | -14,3 % | ▲ attenzione |
| Packaging CoWoS | Divario tra domanda e offerta CoWoS a fine 2026 | congiunturale | 10 % | ▲ attenzione |
| Memoria HBM e DRAM | Prezzi contrattuali DRAM nel 4° trimestre 2026, variazione sul trimestre (previsione) | congiunturale | 20 % | ▲ attenzione |
| Memoria HBM e DRAM | SK Hynix in borsa, variazione a 1 mese | congiunturale | -27,7 % | ■ critico |
| Ottica: chip laser EML per l'1,6T | Carenza di chip EML da 200G per corsia (stima) | congiunturale | 60 % | ■ critico |
| Trasformatori e allacci alla rete | Tempi di consegna dei trasformatori elevatori (GSU), 1° trimestre 2026 | strutturale | 160 settimane | ■ critico |
| Energia di Taiwan per le fab | Scorte di GNL di Taiwan (estremo basso della forchetta 12–14 giorni) | congiunturale | 12 giorni | ▲ attenzione |
| Costo dell'energia per i data center | Gas TTF (Europa) | congiunturale | 82,3 EUR/MWh | ■ critico |
| Costo dell'energia per i data center | Gas Henry Hub (USA) | congiunturale | 3,2 USD/MMBtu | ● normale |
| Un solo progettista dominante e regole USA sui chip | Quota di Nvidia nei chip AI per data center 2026 (stima IDC riportata da terzi; forchetta delle stime 70–86%) | strutturale | 81 % | ■ critico |
| Un solo progettista dominante e regole USA sui chip | Nvidia in borsa, variazione a 1 mese | congiunturale | -22,1 % | ▲ attenzione |

</details>

<details><summary>Come si spostano le cose: i 34 collegamenti</summary>

Ogni riga è un arco «da → a» del file di dati. Le righe di tipo *valutazione* sono percorsi tipici ricostruiti dall'osservatorio (per esempio l'aeroporto usato), non tracciati reali: le società non pubblicano le rotte.

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

</details>

<a id="revisione"></a>

## 15. Revisione

> **Revisione del 10 novembre 2026**
>
> - Revisione indipendente del 9–10 novembre 2026 (fact-checking ed editing, svolta con un assistente AI): 110 affermazioni verificate contro i file di dati e le fonti, 62 confermate, 32 corrette, 16 non verificabili da qui.
> - Correzioni principali: stato della scadenza cinese del 10 novembre (proroga annunciata il 9 novembre, non ancora nel testo ufficiale); quote di AMD (5–7%, non 10%) e di Broadcom nel CoWoS (circa 15%, non «oltre 240.000 wafer»); Foxconn «oltre il 44% dei rack» (non «40% dei server»); costo di Bloomberg Economics riferito a una guerra, non a un blocco; «metà delle portacontainer» ricondotto al 48% del 2022 con la sua fonte; Colossus 2 non è il campus più grande nei dati Epoch; capacità CoWoS riattribuita a Tom's Hardware (la nota KGI dà solo il dato 2027).
> - Corretti anche nello script: gli stati degli indicatori apparivano come codice («{stato:critico}») nel Markdown; la data delle scadenze indicava il giorno del calcolo invece della fonte; il neon mostrava gli USA come «primo produttore» pur essendo l'unico paese pubblicato da USGS; le tabelle dei titoli non segnalavano le sedute di data diversa.
> - Non verificabili da qui: pagine bloccate o a pagamento (Counterpoint, TechRepublic, TipRanks, DIGITIMES, USITC, Focus Taiwan), le scorte di GNL di Taiwan (12–14 giorni), la quota del quarzo di Spruce Pine (stime Everstream e BloombergNEF), la carenza di chip EML (blog di analisi, affidabilità bassa).
> - Aggiunti: dipendenze di UE e Italia (commercio.json), altre materie sotto licenza cinese (minerali.json), spese in conto capitale 2026 dei grandi cloud (investimenti.json), divieto cinese di export di elio (annuncio MOFCOM n. 29 del 2026). Resoconto completo in [report/revisioni/supply-chain-ai-2026-11.md](https://github.com/gabrielegiuliani04/monitor-geoeconomico/blob/main/report/revisioni/supply-chain-ai-2026-11.md).

---

Gabriele Giuliani · Monitor geoeconomico. Scritto con l'aiuto di un assistente AI (Claude, modello di Anthropic; Anthropic è un cliente della catena descritta).
