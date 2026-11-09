# Filiera dell'eolico offshore: Mare del Nord e Baltico

Aggiornato al 9 novembre 2026. File prodotto: `docs/data/eolico-filiera.json` (script `raccolta/eolico/raccogli.py`, voci curate in `raccolta/eolico/*.json`).

**In una frase:** gli obiettivi 2030 del Mare del Nord non verranno raggiunti. Il freno principale non sono più navi e fondazioni, che oggi sono in eccesso. Frenano tre cose: le aste che non trovano offerenti, la rete HVDC (cavi e piattaforme di conversione) e la redditività dei costruttori di turbine.

---

## 1. I 10 fatti chiave (con numero, data e fonte)

1. **Europa a 38,6 GW offshore a fine 2025, ma solo 2 GW connessi nel 2025**, il minimo dal 2016. Hanno connesso nuova capacità solo Regno Unito (1.049 MW), Germania (503 MW) e Francia (408 MW). WindEurope prevede 73 GW nel 2030, con ritardi di 1-2 anni sui piani (WindEurope, *2025 Statistics*, febbraio 2026).
2. **Gli obiettivi non saranno raggiunti.** I 4 paesi di Esbjerg (DK, DE, NL, BE) hanno 19,3 GW. Al 2030 se ne prevedono 31,1, cioè il 48% dei 65 GW promessi (calcolo sui dati WindEurope). Per paese: Germania 16,5 GW previsti contro un obiettivo di 30; Paesi Bassi 8,4 contro circa 21; Regno Unito 32 contro 50.
3. **Nel 2024-2025 sono fallite aste "a offerta negativa" per 6,5 GW**: Danimarca 3 GW (dicembre 2024, nessuna offerta), Germania 2,5 GW (N-10.1/N-10.2, agosto 2025, nessuna offerta, la prima volta) e Paesi Bassi 1 GW (Nederwiek I-A, 30 ottobre 2025, nessuna offerta). In queste aste lo sviluppatore paga lo Stato per il diritto di costruire (WindEurope; offshoreWIND.biz).
4. **Con i CfD a due vie le aste tornano a funzionare.** Il CfD è un contratto per differenza: lo Stato garantisce un prezzo fisso, paga la differenza quando il mercato scende e la incassa quando sale. In Danimarca, ad agosto 2026, Vattenfall ha vinto 1,8 GW con prezzi di 504 e 542 DKK/MWh (circa 68-73 €/MWh, 20 anni); 5 offerte per Hesselø e 2 per North Sea I Mid. I contratti sono stati firmati il 6 novembre 2026. Nel Regno Unito l'asta AR7 ha assegnato 8,4 GW, un record, a 91,20 £/MWh (prezzi 2024; GOV.UK, 14 gennaio 2026). La Polonia ha assegnato 3,4 GW a circa 113-117 €/MWh (17 dicembre 2025).
5. **La Germania ha rinviato al 2027 le aste offshore del 2026.** La riforma della legge sull'eolico in mare (WindSeeG), presentata il 10 agosto 2026, prevede gare da 2 a 4,8 GW l'anno. Il CfD però resta solo una seconda fase di riserva, e l'industria chiede che diventi la regola (offshoreWIND.biz, 12 agosto 2026).
6. **Cavi HVDC: i portafogli ordini coprono anni di produzione.** Prysmian ha ordini per circa **16,5 miliardi €** al 29 ottobre 2026, più circa 2 miliardi aggiudicati e non ancora contati (comunicato Q3 2026). NKT ne ha **13,0 miliardi** a fine giugno 2026 ed era arrivata a un record di oltre 4,2 miliardi di ordini nel solo primo trimestre; la nuova fabbrica di Karlskrona entra in funzione nel 2027. LS Cable (Corea) vince lotti TenneT per connessioni da 2 GW.
7. **Le piattaforme di conversione HVDC sono il collo di bottiglia con l'effetto più grande.** La connessione BalWin1 (Amprion, 2 GW) slitta dal 16 settembre 2030 al **15 settembre 2031**, e con lei BalWin2. Le cause sono il lavoro aggiuntivo sulla piattaforma offshore e i terreni difficili a terra (HVDC World, 8 luglio 2026). Un anno di ritardo blocca 2 GW di turbine già contrattate.
8. **Le fondazioni sono passate dalla scarsità al surplus.** Secondo Rystad (18 settembre 2026) la capacità europea di monopile XXL salirà da 1,2 a 2,7 milioni di tonnellate l'anno dal 2027, con le fabbriche usate al 32% nel 2026 e al 19% nel 2028. Produrre in Cina costa circa il 41% in meno. Sif, che ha il 31% del mercato, chiude una delle tre linee di Rotterdam nel quarto trimestre 2026 e ha dichiarato dubbi sulla propria continuità aziendale (Windtech, novembre 2026).
9. **La scarsità di navi si è attenuata.** Le navi d'installazione occidentali capaci di montare turbine da 15 MW e oltre passano da zero nel 2020 a più di 25 nel 2028. Secondo Intelatus l'Europa tornerà in tensione solo dal 2032 (Offshore Engineer, 1 maggio 2026). Cadeler, l'armatore leader con 11 navi, ha usato la flotta al 66% nel primo semestre 2026 e ha ordini per 2,5 miliardi € (relazione semestrale, agosto 2026). Le tariffe giornaliere 2026 non sono pubbliche.
10. **Il Baltico è il mercato che cresce, e i porti si attrezzano.** Il terminal T5 di Danzica (21 ha, 253 milioni €) serve Baltica 2 dal quarto trimestre 2026. Swinoujscie, aperto a giugno 2025 con banchine da 50 t/m², prevede di ampliarsi. Klaipėda investe 201 milioni €, di cui 100 prestati dalla BEI (settembre 2026). L'obiettivo di Marienborg, però, è lontano: nel Baltico operano circa 2,7 GW (dati EMODnet raccolti dall'agente Nord) contro i 19,6 GW promessi per il 2030.

---

## 2. Dove sono i colli di bottiglia (valutazione)

| Anello | Tensione | Perché |
|---|---|---|
| **Aste e ricavi (tassi, CfD)** | alta | Senza CfD i progetti non si finanziano: il costo del capitale decide. |
| **Rete HVDC: cavi** | alta | Ordini per 13-17 miliardi € per produttore; nuove fabbriche solo dal 2027. |
| **Rete HVDC: piattaforme e convertitori** | alta | Pochi fornitori (Hitachi Energy, Siemens Energy) e pochi cantieri; un ritardo blocca 2 GW. |
| Turbine | media | Il problema è la redditività: Siemens Gamesa è ancora in perdita, GE Vernova ha sospeso i nuovi ordini offshore. In Europa restano due fornitori occidentali, e i costruttori cinesi premono. |
| Navi | media | Le navi WTIV bastano fino al 2030. Restano tese le navi per fondazioni e, dal 2030, le posacavi per i cavi inter-array. |
| Porti | media, locale | Pressione a Eemshaven ed Esbjerg. Nel Mare del Nord tedesco le nuove banchine arrivano tardi: Cuxhaven verso il 2028, e il terminal di Bremerhaven non è mai stato costruito. |
| Manodopera | media, locale | La domanda di tecnici ha picchi legati ai cantieri. Mancano dati affidabili per singolo porto. |
| **Fondazioni** | **eccesso di capacità** | Fabbriche poco usate, concorrenza cinese, rischio che chiudano. |

## 3. Cosa significa per un porto o un operatore logistico

- **Le aste decidono la domanda.** I porti olandesi e tedeschi hanno lavoro garantito fino al 2027-2028 (Ecowende, Nordseecluster, OranjeWind, Thor). Dopo dipende dall'esito delle gare 2026-2027: Paesi Bassi a dicembre 2026, Germania nel 2027.
- **Contano i contratti a progetto.** Il modello che funziona è l'affitto pluriennale legato a un parco, come Danzica T5 per Baltica 2 (dal quarto trimestre 2026 a fine 2028) o Swinoujscie per Ocean Winds. Serve anche la capacità di seguire due progetti insieme, come Eemshaven dopo l'upgrade di aprile 2026.
- **Le specifiche tecniche salgono.** Servono banchine da 40-50 t/m², fondali profondi e aree da decine di ettari per turbine da 15 MW con rotori oltre 230 m.
- **Gli spazi sono contesi.** Esbjerg usa le nuove aree anche per la cattura e lo stoccaggio di CO₂ (CCS) e per le merci modulari. A Mukran convivono l'eolico e il terminal GNL (da verificare nei dettagli).
- **La catena è sempre meno europea.** Dajin (Cina) apre un hub a Cuxhaven, Mitsui e MOL (Giappone) hanno comprato Nigg, LS Cable (Corea) fornisce TenneT, e le grandi navi sono costruite in Cina e Corea. Per chi lavora in logistica è un'opportunità, per i governi un tema di sicurezza.
- **Le basi di manutenzione (O&M) danno lavoro per 25-30 anni**, mentre l'installazione dura 1-2 stagioni. Esempi: Eemshaven per Nordlicht, Mukran per Iberdrola, Grimsby per Ørsted. Per un porto piccolo (Hvide Sande, Grenaa, Rønne) la manutenzione è il business realistico.

## 4. Indicatori da seguire

1. Esiti delle aste: Paesi Bassi IJmuiden Ver Gamma-A/B (domande fino al 10 dicembre 2026), riforma tedesca WindSeeG (iter in Parlamento), Danimarca North Sea South (offerte nella primavera 2028), Belgio Princess Elisabeth Zone, prossima asta polacca (2027).
2. Ordini e consegne di Prysmian, NKT e Nexans (trimestrali) e avvio della fabbrica di Karlskrona (2027).
3. Date di esercizio delle connessioni TenneT e Amprion da 2 GW (BalWin, LanWin): ogni slittamento sposta interi parchi.
4. Utilizzo della flotta e ordini di Cadeler (trimestrali), più eventuali tariffe pubbliche delle navi.
5. Situazione di Sif (assemblea del 22 dicembre 2026, aumento di capitale) e quota dei monopile cinesi.
6. Margini di Siemens Gamesa (risultati dell'esercizio 2026 a novembre) e ritorno di GE Vernova nell'offshore.
7. Decisioni finali d'investimento offshore in Europa: 5,4 GW nel 2025 per 22,5 miliardi € (WindEurope).
8. Notizie recenti su porti e navi: il campo `notizie_recenti` del JSON si aggiorna ogni giorno dai titoli di offshoreWIND.biz.

## 5. Collegamenti con tassi, acciaio, rame e TTF (da `docs/data/prezzi.json`)

- **Tassi.** Il titolo di Stato USA a 10 anni è al **4,86%** (6 novembre 2026), +68 punti base da inizio anno e +75 su un anno. Un parco offshore è quasi tutto spesa iniziale (capex), quindi il costo del capitale pesa molto sul prezzo minimo che lo sviluppatore deve incassare. Tassi alti spiegano perché le aste senza CfD falliscono e perché lo Stato deve dare garanzie. I tassi della BCE non sono nel file: oggi usiamo quelli USA come approssimazione del costo del capitale globale.
- **TTF (gas europeo).** **82,33 €/MWh** il 9 novembre 2026, +192% da inizio anno. Con il gas caro sale il prezzo dell'elettricità, quindi l'eolico guadagna di più sul mercato e un CfD a 68-73 €/MWh (Danimarca) costa poco allo Stato, o addirittura gli fa incassare. È un argomento forte per accelerare. Ma è anche un rischio: se il gas scende, il costo dei CfD per lo Stato sale.
- **EUR/USD** 1,1222 e **Brent** 92,62 $: navi e componenti si comprano spesso in dollari, e con il petrolio a questi livelli l'offshore oil & gas compete con l'eolico per navi e cantieri.
- **Rame e acciaio mancano in `prezzi.json`.** Sono segnalati nel campo `prezzi_collegati.mancanti`. Il rame pesa sul valore dei contratti dei cavi (NKT riporta il portafoglio anche "a prezzi standard dei metalli": 11,6 contro 13,0 miliardi). L'acciaio decide il confronto con la Cina sui monopile: secondo Rystad produrre in Europa costa 3,46 milioni $/kt contro 2,03 in Cina. **Proposta:** aggiungere allo script dei mercati il rame (COMEX HG=F) e una serie sull'acciaio (HRC).

## 6. Cosa contiene il file JSON

- `elementi`: **19 porti** come punti (lat/lon da OpenStreetMap), con ruolo, aree in ettari, banchine, portata in t/m², progetti serviti, investimenti, colli di bottiglia, fonte, data e affidabilità. Il campo `id_porti_nord` collega ogni porto a `porti-nord.json`.
- `navi` (20 unità con armatore, gru, stato e impiego), `flotta` (indicatori aggregati) e `jones_act`.
- `colli_bottiglia`: 8 schede con indicatori, valutazione e "cosa significa per un porto".
- `aste`: 12 aste o riforme del 2024-2026, con esito, meccanismo, prezzo e motivo.
- `obiettivi`: le dichiarazioni (Esbjerg, Ostenda, Amburgo, Marienborg) con quote calcolate, i dati per paese (installato a fine 2025, previsione al 2030, obiettivo e scarto) e un riscontro sul solo Baltico da EMODnet.
- `prezzi_collegati`, `collegamenti` (file dell'agente Nord e altri livelli), `notizie_recenti`, `errori`.

## 7. Fonti provate

| Fonte | Esito | Licenza / nota |
|---|---|---|
| WindEurope, *2025 Statistics* (PDF ospitato da rinnovabili.it) | funziona (scaricato e letto) | © WindEurope, citazione |
| offshoreWIND.biz (articoli e home page) | funziona con curl; la ricerca interna no (la pagina è generata in JavaScript) | © editore, solo fatti citati con link |
| Prysmian, comunicato Q3 2026 (PDF) | funziona | © Prysmian |
| Cadeler, relazione semestrale H1 2026 (SEC EDGAR) | funziona | pubblico |
| Rystad Energy (sintesi pubblica) | funziona | © Rystad |
| GOV.UK, risultati AR7 | funziona | Open Government Licence |
| HVDC World, Windtech, Daily Mare, OE Digital | funzionano | © editori |
| Nominatim / OpenStreetMap (coordinate) | funziona | ODbL |
| Bloomberg, Windpower Monthly, offshoreindustry.co.uk | **non raggiungibili** dalla rete della sessione | — |
| TGS 4C Offshore, TenneT | **403** (bloccano i bot) | 4C è a pagamento |
| WindEurope.org (sito) | 503 al momento della prova | — |
| Tariffe giornaliere delle navi (Clarksons e simili) | **non pubbliche** | a pagamento |

Il controllo dei link (`CONTROLLA_LINK=1`) ha trovato e corretto 2 link rotti. Restano lenti, senza essere rotti, Business Wire e nawindpower.

## 8. Proposta per la mappa

- **Livello "Porti dell'eolico":** icona diversa per installazione, fabbricazione e manutenzione. Dimensione del simbolo in base agli ettari, quando noti. Colore secondo lo stato: operativo, in ampliamento, bloccato (Bremerhaven). Nel popup: progetti serviti, investimenti e colli di bottiglia.
- **Pannello "Obiettivi e realtà":** barre per paese con installato a fine 2025, previsione al 2030 e obiettivo, più le quattro dichiarazioni. Si sovrappone ai parchi di `offshore-nord.json`.
- **Scheda "Filiera":** le 8 schede dei colli di bottiglia con un semaforo per la tensione, la cronologia delle aste e la tabella delle navi.
- **Collegamenti tra livelli:** cavi e incidenti nel Baltico (`cavi-incidenti.json`, `baltico-sicurezza.json`), rete HVDC (`rete-elettrica.json`), TTF e tassi (`prezzi.json`).

## 9. Limiti

- Le voci sono curate a mano: lo script valida e ricalcola, ma non scopre nuovi fatti da solo. Fanno eccezione i titoli recenti, che servono solo come segnale.
- Mancano molte metrature (ettari, metri di banchina, t/m²) per Vlissingen, Bremerhaven, Grenaa, Hvide Sande, Hull, Grimsby, Able Seaton e Ostenda: sono lasciate a `null`, non stimate.
- Le gru di alcune navi (Orion, Seaway Ventus, la classe M di Cadeler) non sono state verificate e sono lasciate a `null`. Le tariffe giornaliere non sono disponibili.
- I dati di installato sono nazionali (WindEurope): Germania e Danimarca mescolano Mare del Nord e Baltico. Per il Baltico usiamo il riscontro EMODnet dell'agente Nord, che può differire da WindEurope.
- Alcuni numeri vengono da sintesi secondarie e sono marcati `affidabilita: media`: Nexans al 30 settembre, i tetti di prezzo tedeschi e olandesi, la manodopera secondo GWO.
- Esbjerg: la data esatta del comunicato sui 570.000 m² non è indicata (collocato nel 2025).
