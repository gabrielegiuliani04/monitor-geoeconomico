# Impatti in Italia — rapporto dell'agente

*Cosa succede in Italia quando uno shock energetico o logistico (Hormuz, Mar Rosso, TransMed) arriva ai prezzi, all'autotrasporto e alle persone. Dati letti il 9-10 novembre 2026.*

Ogni numero ha fonte e data. Le parti marcate *Valutazione* sono ragionamenti dell'osservatorio, non fatti.

## In breve

- **Gasolio a 2,24 €/l, benzina a 2,00** (media settimanale MASE, 2 novembre 2026). Il taglio di 4,9 centesimi sul gasolio è scaduto l'8 novembre: senza il taglio il gasolio sarebbe intorno a 2,29 (calcolo: prezzo netto più accisa ordinaria, con IVA). Il 9 novembre il Mimit indica 2,232 per il gasolio self e 2,000 per la benzina ([ANSA](https://www.ansa.it/sito/notizie/economia/2026/11/09/mimit-prezzo-benzina-stabile-a-2000-euro-gasolio-in-leggero-aumento-a-2232_9d0752c9-8a30-4d1f-9149-b033ff112a55.html)), anche per effetto del tetto volontario di Eni e IP.
- **Elettricità ai massimi dal 2022.** PUN medio di ottobre 2026: 230,8 €/MWh; novembre (parziale) 277,3; media 2022: 304,0 (GME).
- **Gas per i vulnerabili** a 88,36 €/MWh di materia prima a ottobre 2026 (ARERA, 3/11/2026), contro 46-47 in aprile-maggio.
- **Inflazione NIC al 5,4% a ottobre 2026** (stima preliminare Istat), dal 1,5% di febbraio. Energetici +31,4%, alimentari +2,7%, componente di fondo +2,0%.
- **Fiducia dei consumatori a 90,3** (ottobre 2026, Istat, base 2021=100); il minimo del 2022 era 80,9 (ottobre 2022).
- **Si consuma meno gasolio.** Vendite di gasolio per motori −7,5% a settembre 2026 su un anno, −9,4% l'extrarete (flotte e autotrasporto); maggio era −10,8% (MASE). La benzina invece cresce (+4,9% a settembre).
- **Autotrasporto in tensione da marzo.** Fermo di Trasportounito ad aprile (sospeso dopo la morte di un camionista sull'A1), fermo Unatras 25-29 maggio sospeso con 300 milioni di crediti d'imposta, fermi regionali in Sicilia e Calabria 16-20 ottobre, nuovo fermo nazionale prospettato da Unatras a fine ottobre.

> *Valutazione.* Oggi il rischio di un fermo dei TIR è **alto** per le soglie di questo rapporto (gasolio sopra 2,10 €/l): è al livello che ha fatto partire i blocchi del marzo 2022 (2,15) e dell'aprile 2026 (2,11). Un fermo regolare richiede 25 giorni di preavviso: proclamato oggi, non potrebbe partire prima di inizio dicembre.

## 1. Dati italiani di oggi

| Indicatore | Valore | Data | Fonte |
|---|---|---|---|
| Gasolio, media nazionale settimanale | 2,238 €/l (netto 1,202; accisa 0,633; IVA 0,404) | 2/11/2026 | [MASE](https://sisen.mase.gov.it/dgsaie/prezzi-settimanali-carburanti) |
| Benzina, media nazionale settimanale | 2,001 €/l (accisa 0,673) | 2/11/2026 | MASE |
| Gasolio self (Mimit) | 2,232 €/l | 9/11/2026 | ANSA |
| PUN, media di ottobre | 230,8 €/MWh | ottobre 2026 | [GME](https://www.mercatoelettrico.org/it-it/) |
| PUN, giorno | 293,9 €/MWh | 10/11/2026 | GME |
| Gas MGP (GME), giorno | 87,1 €/MWh | 10/11/2026 | GME |
| Gas vulnerabili, materia prima | 88,36 €/MWh (+9,1% la spesa del cliente tipo su settembre) | ottobre 2026 | [ARERA](https://www.arera.it/comunicati-stampa/dettaglio/gas-valore-materia-prima-vulnerabilita-ottobre-2026) |
| NIC, indice generale | +5,4% a/a | ottobre 2026 (prov.) | [Istat](https://esploradati.istat.it/databrowser/) |
| NIC energetici / regolamentati | +31,4% / +59,5% | ottobre 2026 | Istat |
| HICP Italia | +5,6% a/a | ottobre 2026 | [Eurostat](https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_minr/default/table) |
| Fiducia consumatori | 90,3 | ottobre 2026 | Istat |

**Accise.** Dalla serie MASE si leggono tutti i cambi: nel 2022 −25 centesimi (30,5 con IVA) dal 22 marzo, poi −15 a dicembre, fine il 1° gennaio 2023. Nel 2026: accise di benzina e gasolio allineate a 0,6729 €/l da gennaio; −20 centesimi (24,4 con IVA) dal 23 marzo; poi una serie di proroghe e tagli più piccoli soprattutto sul gasolio (agosto −17,1 centesimi con IVA, poi risalite a settembre e ottobre); l'ultimo taglio di 4,9 centesimi è scaduto l'8 novembre ([Rai News](https://www.rainews.it/articoli/2026/11/carburanti-scade-lo-sconto-di-49-cent-sulle-accise-del-diesel-rischio-rincari-c2f0e782-44ba-426d-9017-19a5504f37b7.html)). L'elenco completo è in `accise.cambi`.

**Decreto Bollette (9/11/2026):** da gennaio circa −15 €/MWh, meno di 30 euro l'anno per famiglia ([ANSA](https://www.ansa.it/sito/notizie/economia/2026/11/09/dal-cdm-ok-al-decreto-bollette-15-euro-in-meno-al-megawattora_cbf74d76-2c12-4718-89af-73ab9c1e6fec.html), [Corriere](https://www.corriere.it/economia/energie/26_novembre_09/bollette-il-governo-ha-approvato-il-nuovo-decreto-9a245b11-fe65-4be6-93e8-4f024d742xlk.shtml)).

## 2. Autotrasporto e scioperi

**Regole.** La legge 146/1990 regola gli scioperi nei servizi essenziali; la Commissione di garanzia può chiedere la revoca e segnalare per la precettazione. Per i fermi dell'autotrasporto il codice di settore chiede **25 giorni di preavviso** e servizi minimi; vale la "rarefazione oggettiva" (niente fermi ravvicinati nello stesso settore). Nel marzo 2022 e nell'aprile 2026 la Commissione ha contestato fermi proclamati con meno di 25 giorni.

**Il meccanismo del 2026.** I camionisti recuperano una parte dell'accisa sul gasolio (26,5 centesimi al litro secondo Federtrasporti). Quando il governo taglia l'accisa per tutti, quel rimborso si riduce: Unatras ha parlato di "una decisione errata che scaricava sulle imprese di autotrasporto la riduzione di 20 centesimi" ([Shipping Italy, 23/5/2026](https://www.shippingitaly.it/2026/05/23/sospeso-il-fermo-dellautotrasporto-in-programma-dal-25-maggio/)). Il taglio delle accise quindi calma gli automobilisti ma può irritare i camionisti.

**Precedenti** (prezzo del gasolio della settimana, media MASE, e variazione su un anno):

| Quando | Cosa | Gasolio | Su un anno | Effetti documentati |
|---|---|---|---|---|
| 10-14 dic 2007 | Fermo nazionale TIR | 1,29 €/l | +15,8% | latte, medicinali e benzina garantiti solo dal 12 dicembre ([VareseNews](https://www.varesenews.it/2007/12/camion-ancora-fermi-ma-garantiti-latte-benzina-e-medicinali/225029/)) |
| 16-20 gen 2012 | Forconi, Sicilia | 1,68 | +27,6% | distributori a secco, acqua e latte esauriti ([Balarm](https://www.balarm.it/news/magazine/protesta-dei-forconi-esaurite-scorte-e-benzina-8548)) |
| 23-27 gen 2012 | Blocchi TIR in tutta Italia | 1,69 | +25,9% | circa 60 presidi ai caselli ([Il Post](https://www.ilpost.it/2012/01/23/sciopero-tir-autotrasportatori/)) |
| marzo 2022 | Protesta camionisti (gasolio oltre 2 €) | 2,15 | +51,6% | corsa a pasta, farina, olio; file alle pompe ([La Sicilia/ANSA](https://www.lasicilia.it/news/economia/1208929/il-garante-ferma-lo-sciopero-degli-autotrasportatori-ma-e-solo-una-tregua.html)) |
| gen-feb 2024 | Trattori (IRPEF agricola, PAC) | 1,79 | −6,6% | nessuna carenza; esenzione IRPEF sotto 10.000 euro ([Il Post](https://www.ilpost.it/2024/02/09/irpef-agricola-agricoltori-meloni-lollobrigida/)) |
| 20 apr 2026 | Fermo Trasportounito | 2,11 | +29,5% | sospeso dopo la morte di un camionista sull'A1 ([LaPresse](https://www.lapresse.it/cronaca/2026/04/20/sciopero-autotrasportatori-trasportounito-camionista-muore-investito-sospeso-il-fermo/)) |
| 25-29 mag 2026 | Fermo Unatras | 1,98 | +25,6% | sospeso il 22 maggio, revocato il 23 luglio ([trans.info](https://trans.info/it/unatras-revoca-definitivamente-il-fermo-nazionale-491492)) |
| 16-20 ott 2026 | Fermi regionali Sicilia e Calabria | 2,24 | +37,0% | incontro al MIT il 27/10 ([Logisticamente](https://www.logisticamente.it/articoli/60800/caro-gasolio-autotrasporto-in-agitazione-rischio-fermo-nazionale/)) |

> *Valutazione.* La soglia che conta non è un numero fisso ma il **nuovo massimo** con un aumento rapido (tra +16% e +52% su un anno in tutti i casi di blocco). Le proteste dei trattori del 2024 sono partite con il gasolio in calo: altro motore. Soglie usate: basso sotto 1,90 €/l, medio 1,90-2,10, alto da 2,10 o con +15% in 8 settimane.

**Associazioni e dichiarazioni 2026.** Unatras (Paolo Uggè): fino a 40 centesimi al litro di aggravio, circa 9.000 euro al mese di perdita per impresa (17/4/2026, [Il Fatto Quotidiano](https://www.ilfattoquotidiano.it/2026/04/17/fermo-autotrasporto-unatras-gasolio-logistica-notizie/8358442/)). CNA Fermo: circa 2.000 euro al mese in più per un solo mezzo pesante (ottobre 2026). Federtrasporti: fuel surcharge automatica sulle tariffe (10/9/2026). MIT: concessi 242,2 dei 480 milioni di credito d'imposta, da usare entro il 31/12/2026 ([TrasportoEuropa](https://www.trasportoeuropa.it/notizie/autotrasporto/semaforo-rosso-del-garante-al-fermo-dellautotrasporto/)).

**Peso del gasolio sui costi.** Non c'è un valore ufficiale italiano aggiornato (lo nota Federtrasporti a settembre 2026). Il riferimento più vicino è francese: il gasolio pesa il **20,9%** del costo di un autoarticolato a lunga distanza nel 2026 (22,1% nel 2025, 24,4% nel 2024; CNR, ponderazioni dell'indice). Il CNR stima che il rialzo di marzo 2026 abbia fatto salire il costo totale del 4,2%.

**Scioperi proclamati nei prossimi 30 giorni** (calendario MIT e Commissione non raggiungibili da questo ambiente; elenco da [Rai News, 8/11/2026](https://www.rainews.it/articoli/2026/11/scioperi-novembre-di-mobilitazioni-trasporti-scuola-e-settore-pubblico-le-proteste-88aa7da4-ad6b-4ec7-a964-d9829015bf04.html)): trasporto locale a Genova (9/11), Cosenza (10/11), Milano-Atm e Venezia (13/11), Bari (14/11), Napoli-Anm (16/11); **sciopero generale Cgil il 20 novembre**; ferrovie e merci su rotaia dalle 21 del 20 alle 20 del 21 novembre (Sgb, Cub, Assemblea Pdm/Pdbi); aerei Firenze-Pisa e Enav Varese il 22/11. Revocato lo sciopero Italo del 9/11. **Nessun fermo nazionale dell'autotrasporto proclamato** nelle fonti consultate.

## 3. Comportamenti

- **Code e "esaurito" in Italia nel 2026** nascono dai cambi di prezzo, non da carenze vere: dopo il taglio del 19 marzo solo il 60% dei distributori l'ha applicato tra il 23 e il 25 marzo e oltre l'11% ha alzato i prezzi; la gente è corsa ai distributori più economici, le cisterne da 15-30 mila litri si sono svuotate in poche ore ([Today.it, 27/3/2026](https://www.today.it/economia/benzina-esaurita-cartelli-distributori.html)). Lo stesso il 28 settembre con il tetto Eni/IP (1,99 e 2,19 €/l): code e distributori esauriti da Napoli a Roma ([La Prealpina](https://www.prealpina.it/news/economia/553287/corsa-al-pieno-scontato-alcuni-distributori-a-secco-code-e-lo-spettro-degli-scioperi.html)).
- **Accaparramento di cibo** documentato solo quando c'è un blocco dei TIR: marzo 2022 (pasta, zucchero, farina, olio, riso), Sicilia 2012 (acqua, latte).
- **Estero.** Regno Unito, settembre 2021: carenza di autisti, panic buying, due terzi dei 5.500 impianti indipendenti a secco nel fine settimana ([Al Jazeera/Reuters](https://www.aljazeera.com/news/2021/9/27/panic-buying-leaves-petrol-pumps-dry-in-major-british-cities)). Francia, ottobre 2022: scioperi in quattro raffinerie TotalEnergies, fino a circa il 30% delle stazioni in carenza. Ungheria, dicembre 2022: il tetto ai prezzi riduce le forniture, un quarto delle stazioni vuote, tetto abolito il 6 dicembre ([bne IntelliNews](https://www.intellinews.com/hungary-scraps-fuel-price-cap-after-panic-buying-leaves-pumps-dry-264485)). Slovenia, agosto 2022: corsa al pieno prima del cambio dei prezzi regolati, molte stazioni a secco (affidabilità bassa).
- **Consumi.** Elasticità della benzina: −0,09 nel breve, −0,31 nel lungo (meta-analisi [Havranek, Irsova, Janda 2012](https://econpapers.repec.org/RePEc:eee:eneeco:v:34:y:2012:i:1:p:201-207)). Nel 2026 il gasolio per motori cala fino al −10,8% (maggio) e l'extrarete fino al −14,3%, mentre la benzina cresce: *valutazione*, il gasolio costa 20-25 centesimi più della benzina e una parte del calo è attività economica più debole, non solo risparmio.
- **Trasporto pubblico:** nessun dato nazionale 2026 trovato.

## 4. Regole di trasmissione (per il simulatore)

Stimate da `raccogli.py` sui dati italiani 2021-2026 (MASE e Yahoo) e ricalcolate a ogni esecuzione:

| Regola | Valore | Fonte |
|---|---|---|
| 10 $/barile di Brent, a margini fermi | +6,8 c€/l con IVA (EUR/USD 1,12) | calcolo |
| Gasolio: prezzo netto per 1 €/l di Brent | 1,40 dopo 4 settimane, 1,66 dopo 8, 1,72 dopo 13, 1,88 a regime | stima osservatorio |
| quindi 10 $/barile | +10 c€/l dopo 4 settimane, +11 dopo 8 | stima |
| Benzina | 1,03 (4 sett.), 1,15 (8), 1,40 a regime: +7/+8 c€/l per 10 $ | stima |
| Ritardo | dopo 1 settimana passa il 35% dell'effetto, dopo 4 il 74%, dopo 8 l'88% | stima |
| TTF → PUN | PUN ≈ 48 + 1,96 × TTF (R² 0,95, 18 punti): +10 €/MWh di TTF ≈ +20 di PUN | GME, Yahoo |
| TTF → gas vulnerabili | materia prima = media mensile PSV: +10 €/MWh ≈ +10,6 c€/Smc più IVA, circa +7% della spesa | ARERA |
| Energia → inflazione | peso energia 10,9% del paniere HICP 2026 (carburanti 4,7%, elettricità 2,8%, gas 3,1%): +10% energia ≈ +1,1 punti, effetto diretto | Eurostat |
| PUN → bollette elettriche | 2022: prezzi al consumo +107% con PUN +142%, rapporto 0,75 (affidabilità bassa) | Eurostat, GME |
| Petrolio → PIL | +10% del petrolio per uno shock geopolitico: −0,2/−0,3 punti di crescita l'anno per tre anni | [BCE, Economic Bulletin 4/2026](https://www.ecb.europa.eu/press/economic-bulletin/focus/2026/html/ecb.ebbox202604_04~9b6a4036fc.en.html) |

**Prova sul 2026.** Applicata ai prezzi di fine febbraio 2026, la regola dà per Hormuz a 1 mese un gasolio a 1,96-2,21 €/l. Il dato vero (MASE) è stato 1,99 di media e 2,03 di massimo con i tagli delle accise, 2,11 e 2,28 senza i tagli. A 3 mesi la regola dà 2,03-2,28, il dato vero 2,22 di media e 2,40 di massimo senza i tagli: a 3 mesi la regola sottostima un po' il picco. Il PUN invece è sovrastimato (regola 156-174, dato vero di marzo 143): in primavera pesano le rinnovabili.

## 5. Scenari Italia (*valutazione*)

Le variazioni di Brent e TTF vengono dal simulatore (`simulatore.json`); i prezzi italiani dalle regole sopra. Due basi: **condizioni normali** (fine febbraio 2026: Brent 71,3 $, TTF 31,6 €/MWh, gasolio 1,70 €/l) e **oggi** (Brent 91,7 $, TTF 82,3, gasolio 2,29 senza il taglio scaduto). Accise ferme, nessuna misura del governo.

| Scenario | Base | Gasolio €/l | Benzina €/l | PUN €/MWh | Gas vulnerabili | Inflazione, effetto diretto | Rischio fermo TIR |
|---|---|---|---|---|---|---|---|
| Hormuz chiuso 1 mese | normale | 1,96–2,21 | 1,85–2,01 | 156–174 | +25/+35 c€/Smc | +1,4/+2,3 punti | alto |
| | oggi | 2,64–2,98 | 2,26–2,48 | 340–385 | +37/+52% | +2,8/+4,3 punti | alto |
| Hormuz chiuso 3 mesi | normale | 2,03–2,28 | 1,89–2,08 | 148–174 | +20/+35 c€/Smc | +1,4/+2,5 punti | alto |
| | oggi | 2,74–3,07 | 2,31–2,58 | 317–385 | +29/+52% | +2,5/+4,5 punti | alto |
| Mar Rosso, 1 mese (navi dal Capo) | normale | 1,73–1,76 | 1,67–1,70 | invariato | invariato | +0,1 punti | basso |
| | oggi | 2,32–2,37 | 2,03–2,06 | invariato | invariato | +0,1 punti | alto (già oggi) |
| TransMed chiuso 1 mese | normale | invariato | invariato | 119–125 | +3/+7 c€/Smc | +0,1/+0,2 punti | basso |
| | oggi | invariato | invariato | 243–260 | +4/+10% | +0,2/+0,6 punti | alto (già oggi) |

- **Scaffali e catene.** *Valutazione.* Le carenze nei negozi arrivano con i blocchi dei TIR, non con il prezzo (2012, 2022). I farmaci e il latte sono stati garantiti come servizi minimi anche nel 2007. Hormuz pesa sui fertilizzanti (urea del Golfo) e quindi sulla campagna agricola dopo; il Mar Rosso pesa su tempi e noli dei container (porti di transhipment come Gioia Tauro); il TransMed colpisce gas, elettricità e imprese energivore (carta, ceramica, vetro, acciaio), non i carburanti.
- **Misure probabili** (precedenti): taglio delle accise (2022: 30,5 c€/l; 2026: 24,4), crediti d'imposta all'autotrasporto (2026: 300 milioni) e alle imprese energivore (2022), bonus sociali con soglia ISEE alzata (2022: 12.000 euro), oneri di sistema azzerati e IVA sul gas al 5% (2021-2022), bonus da 200 e 150 euro (2022), tetti di prezzo volontari (Eni/IP 2026), decreti bollette (novembre 2026).
- **Indicatori da guardare:** gasolio self Mimit giornaliero; differenza gasolio-benzina; proclamazioni sul calendario MIT e della Commissione di garanzia; vendite di gasolio extrarete MASE; PUN giornaliero e gas MGP del GME; CMEM ARERA; stima preliminare NIC a fine mese; fiducia dei consumatori; flussi a Mazara del Vallo; stoccaggi gas.

## Fonti provate

| Fonte | Esito | Licenza |
|---|---|---|
| MASE DGSAIE, prezzi settimanali con accise e IVA (CSV, dal 2005) | funziona | dati pubblici MASE |
| MASE, vendite mensili di prodotti petroliferi (XLS) | funziona, ma file Excel: estratti a mano in `consumi_carburanti.json`, lo script segnala i mesi nuovi | dati pubblici MASE |
| Mimit, open data giornalieri (`prezzo_alle_8.csv`) | **non funziona da qui** (connessione chiusa); codice pronto, da provare su GitHub Actions | IODL 2.0 |
| GME, PUN e MGP-GAS (API della home page con token) | funziona | uso informativo |
| Istat SDMX, NIC e fiducia dei consumatori | funziona | CC BY 3.0 IT |
| Eurostat, HICP ECOICOP 2 e pesi | funziona | CC BY 4.0 |
| Yahoo Finance, Brent, TTF, EUR/USD | funziona (solo i coefficienti finiscono nel file) | non ufficiale |
| ARERA, comunicati vulnerabili | pagine leggibili, URL non regolari: valori curati in `arera.json` | dati pubblici |
| MIT scioperi.mit.gov.it, Commissione cgsse.it | **non raggiungibili da qui** (rete); il MIT si prova a ogni esecuzione, altrimenti elenco curato | — |
| CNR (Francia), PDF | non apribili da qui; valori dal riassunto di ricerca | — |

## Cosa contiene `docs/data/italia-impatti.json`

`oggi` (quadro attuale), `serie` (carburanti settimanali dal 2022 con netto e accisa; giornalieri self Mimit che si accumulano; GME annuale, mensile, giornaliero; NIC; HICP per voce; fiducia; vendite mensili MASE; CMEM ARERA), `accise` (tutti i cambi dal dicembre 2021), `regole_trasmissione` (coefficienti stimati, regole in parole, letteratura, sezione `per_il_simulatore` con le basi e i pesi), `autotrasporto`, `precedenti` (eventi datati con prezzo del gasolio alla data), `scioperi_proclamati`, `misure_governo`, `soglie_fermo`, `scenari` (due basi, osservato 2026 e verifica), `errori`, `avvisi`. Pesa circa 133 kB.

Le voci curate stanno in `raccolta/italia/*.json`. Si controllano con `python3 raccolta/italia/raccogli.py --valida`.

## Collegamenti con la mappa e proposta

- **Simulatore**: la sezione "Cosa succede in Italia" può leggere `scenari` già calcolati per Hormuz, Mar Rosso e TransMed, oppure applicare `regole_trasmissione.per_il_simulatore` alle variazioni di Brent e TTF che il simulatore calcola per qualsiasi passaggio e intensità. Conviene mostrare per prima la base "condizioni normali" per Hormuz, perché lo stretto è già chiuso e i prezzi di oggi incorporano lo shock.
- **Mappa**: Mazara del Vallo (TransMed) e rigassificatori da `gas-italia.json`; porti energetici in calo (Ravenna, Venezia) da PortWatch; un riquadro Italia con gasolio, PUN, NIC e un semaforo del rischio fermo.
- **Calendario**: NIC preliminare a fine mese, CMEM ARERA nei primi giorni del mese, scioperi proclamati.

## Limiti

- I coefficienti sono regressioni semplici su 2021-2026, un periodo con due grandi crisi: valgono per shock grandi, meno per oscillazioni piccole. Non distinguono salite e discese (di solito i prezzi alla pompa scendono più lentamente di come salgono).
- La serie MASE è settimanale e non separa self e servito; la media giornaliera Mimit non è stata scaricata da qui.
- L'inflazione è solo l'effetto diretto dell'energia, senza effetti indiretti né misure del governo. Il rapporto elettricità/PUN viene da un solo anno.
- Le soglie del rischio fermo sono un giudizio sui precedenti, non un modello.
- Mancano: dato ufficiale italiano sul peso del gasolio nei costi dell'autotrasporto, testo del codice di autoregolamentazione (durate e periodi di franchigia), calendario ufficiale degli scioperi, esito dell'incontro al MIT del 27 ottobre 2026, dati sul trasporto pubblico, CMEM di giugno e agosto 2026.
