# Calendario ed eventi di rilevanza mondiale: rapporto dell'agente

Data di riferimento: lunedì 9 novembre 2026. Script: `raccolta/calendario/raccogli.py` (eseguito alle 19:04 UTC circa). Dati: `docs/data/calendario.json` (215 elementi, 141 KB). Voci curate a mano: `raccolta/calendario/voci_manuali.json`.

## 1. Cosa contiene il file

Ogni elemento ha `data` (AAAA-MM-GG; `AAAA` o `AAAA-MM` quando il giorno non è fissato), `data_fine` (per vertici di più giorni), `ora_utc`, `paese` (ISO a 2 lettere; `EU` per BCE ed Eurostat), `categoria` (banca-centrale, dato-macro, energia, elezioni, vertice, sanzioni), `titolo`, `importanza` (alta/media/bassa), `valore_precedente`, `valore_atteso` (solo con fonte citata), `valore_uscito`, `fonte`, `link`, `data_fonte`, `affidabilita`, `note`, `origine` (auto / manuale / manuale (riserva)), `stato` (passato/oggi/futuro) e `id`.
Finestra: dal 10/10/2026 (30 giorni indietro, per avere i risultati appena usciti) al 10/11/2027.

| Categoria | Elementi |
|---|---|
| dato-macro | 81 (BLS, BEA, Eurostat, più la trimestrale Nvidia) |
| banca-centrale | 37 (Fed, BCE, BoJ, BoE, verbali Fed) |
| elezioni | 37 (ElectionGuide + Wikipedia) |
| sanzioni | 31 (scadenze dei regimi UE + azioni OFAC delle ultime 2 settimane) |
| energia | 25 (OPEC+, IEA, OPEC, EIA STEO e settimanale) |
| vertice | 4 (COP31, APEC, G20, Consiglio europeo) |

## 2. Fonti provate

| Fonte | Esito | Cosa dà | Licenza |
|---|---|---|---|
| Fed, `fomccalendars.htm` + RSS `press_monetary.xml` + comunicato | Funziona | Riunioni 2026-2027, ultima decisione, voto e dissensi | Pubblico dominio |
| BCE, calendario del Consiglio direttivo + RSS + comunicato | Funziona | Riunioni fino al 2028, ultima decisione | Riuso con citazione |
| BCE Data Portal API (`FM.B.U2.EUR.4F.KR.*`) | Funziona, ma un 504 al primo giro (aggiunti 3 tentativi) | Tassi su depositi, MRO, marginale | Riuso con citazione |
| Bank of Japan, calendario MPM (HTML) | Funziona | Riunioni 2026-2027 | Termini BoJ (citazione) |
| Bank of Japan, comunicato | Solo PDF: tasso messo a mano | Tasso, voto | Termini BoJ |
| Bank of England, date MPC e pagina Bank Rate | Funziona | Date 2026-2027, tasso, ultima decisione | Termini BoE / OGL |
| BLS, calendario ICS + testo dei comunicati CPI e occupazione | Funziona (bls.gov può rifiutare richieste senza contatto nello User-Agent: impostare `CONTATTO_EMAIL`; ci sono voci di riserva) | Date fino a dicembre 2026, ultimi valori | Pubblico dominio |
| BLS API v1 (senza chiave) | **Non funziona oggi**: limite giornaliero esaurito sull'IP condiviso. Con `BLS_API_KEY` si usa la v2 | Serie CPI, disoccupazione, occupati | Pubblico dominio |
| BEA, calendario ICS + pagine PIL e redditi personali | Funziona (l'API BEA richiede una chiave, non usata) | Date fino a fine 2027, PIL e PCE | Pubblico dominio |
| Eurostat, iCal delle uscite + API `teicp000` | Funziona. Nota: `prc_hicp_manr` per l'area euro è fermo a dicembre 2025 (passaggio a ECOICOP 2) | Date, HICP flash | CC BY 4.0 |
| EIA STEO, calendario e tabella 1 del WPSR (`ir.eia.gov/wpsr/table1.csv`) | Funziona, senza chiave | Date, scorte settimanali | Pubblico dominio |
| OPEC (opec.org) | **Non funziona**: 403 agli script. Voci a mano da riprese di stampa | Riunioni OPEC+ | — |
| IEA (iea.org) | **Non funziona**: 403. Data dell'OMR messa a mano | Data dell'OMR | — |
| IFES ElectionGuide, `elections/type/upcoming/` | Funziona | 27 elezioni nazionali fino a luglio 2027 | Termini IFES: uso non commerciale con citazione (da verificare) |
| Wikipedia, calendari elettorali nazionali 2026-2027 | Funziona (l'API dà 429, la pagina HTML no). Usata a mano | Elezioni che ElectionGuide non elenca ancora (Italia, Polonia, Grecia, Messico, Argentina...) | CC BY-SA 4.0 |
| EU Sanctions Map API (`sanctionsmap.eu/api/v1/regime`) | Funziona | Data di scadenza di ogni regime UE | Riuso con citazione (Commissione) |
| OFAC, Recent Actions | Funziona (il feed XML dà 403) | Azioni sanzionatorie USA recenti | Pubblico dominio |
| Consilium (Consiglio UE), g20.org | 403. Date ricavate da ricerca web | Vertici | — |

## 3. Fatti attuali (con numero, data e fonte)

1. **Fed**, 28/10/2026: fed funds invariati a **3,75-4,00%**, voto 10-2. Lisa Cook e Beth Hammack volevano un **rialzo** di 0,25 punti. Prossima riunione l'8-9 dicembre, con proiezioni economiche. (federalreserve.gov, comunicato FOMC)
2. **BCE**, 29/10/2026: tassi invariati. Depositi al **2,50%**, MRO al 2,65%, marginale al 2,90%, in vigore dal 16/9/2026 (prima i depositi erano al 2,25%). Il comunicato parla di uno shock energetico che spinge in alto l'inflazione e frena la crescita. Prossima riunione il 16-17 dicembre. (BCE, comunicato e Data Portal)
3. **Bank of England**, 5/11/2026: Bank Rate **alzato al 4,00%** (+0,25). L'inflazione è al 3,5% e la BoE la vede a circa il 5% a metà 2027 per il caro energia dovuto al conflitto in Medio Oriente. Prossima decisione il 17/12. (bankofengland.co.uk)
4. **Bank of Japan**, 30/10/2026: call rate invariato a circa **1,25%** (voto 8-1). Le vendite di ETF salgono a circa 860 miliardi di yen l'anno da gennaio 2027. Prossima riunione il 17-18 dicembre. (BoJ, Statement on Monetary Policy)
5. **Inflazione USA**, CPI di settembre (uscito il 14/10): **+0,6% m/m, +3,7% a/a**. La benzina, +9,1% nel mese, spiega oltre metà dell'aumento. Il CPI di ottobre esce **domani, 10/11, alle 13:30 UTC**. Per TD Securities sarà +0,30% m/m (core +0,21%): è la previsione di una sola banca, non un consensus. (BLS; FXStreet)
6. **Occupazione USA** di ottobre (uscita il 6/11): **+165.000** posti non agricoli, disoccupazione al **4,1%**. (BLS, USDL-26-1632)
7. **PIL USA** nel terzo trimestre, stima preliminare del 29/10: **+3,4%** annualizzato (+2,2% nel secondo). Deflatore PCE di settembre: **+3,6% a/a, core +3,1%**. (BEA)
8. **Eurozona**, stima flash dell'HICP di ottobre (4/11): **4,0% a/a**, dal 3,8% di settembre. (Eurostat, teicp000)
9. **Scorte commerciali di greggio USA** al 30/10: **409,8 milioni di barili**, -0,9 Mb sulla settimana. Il dato è uscito il 4/11; il prossimo esce giovedì 12/11 alle 17:00 UTC, spostato per il Veterans Day. (EIA WPSR)
10. **OPEC+**, 1/11/2026: i sette paesi del gruppo lasciano invariati gli obiettivi di dicembre, ai livelli di settembre. Secondo Reuters le esportazioni del Golfo viaggiano al 60-80% del normale per la guerra con l'Iran. Il **29/11** si tengono la riunione ministeriale e il JMMC sulle quote 2027. (OPEC via stampa; Reuters via Engineering News)

## 4. Cosa è successo nell'ultima settimana (2-9 novembre)

- **Elezioni di metà mandato USA (3/11)**: i democratici conquistano **entrambe le camere**. Camera: 254 D contro 162 R, con il 95,6% dei seggi assegnati (Wikipedia, 6/11). Senato: 54-44 secondo AP e NBC, con Alaska e Mississippi ancora da assegnare (4/11); Wikipedia indica una forbice di 52-54 seggi per i democratici. Dal 3 gennaio 2027 il governo sarà diviso: Trump resta presidente, Jeffries è atteso come speaker. Sono risultati provvisori: fonti Wikipedia (supporto), NPR/KUT e AP via WDBO.
  *Valutazione*: un Congresso democratico rende più difficili nuovi tagli fiscali e più probabili lo stallo sul bilancio e le inchieste parlamentari. Su dazi e sanzioni il presidente conserva ampi poteri esecutivi, quindi l'effetto diretto sul petrolio è limitato. Per i titoli AI conta di più il rischio regolatorio (antitrust, export di chip) che la politica fiscale.
- **BoE alza i tassi (5/11)**: è la prima grande banca centrale a rialzare in risposta allo shock energetico. Fed (dissensi per un rialzo) e BCE (che ha già alzato a settembre) restano in attesa.
- **Inflazione dell'eurozona al 4,0% (4/11)**: rafforza l'ipotesi di una BCE ancora restrittiva a dicembre.
- **Occupazione USA solida (6/11)**: +165.000 posti e disoccupazione al 4,1%. Non c'è un rallentamento che spinga la Fed a tagliare.
- **OFAC**: designazioni legate all'Iran il 4/11 e il 6/11, una licenza generale Iran modificata il 29/10, designazioni su Cuba il 5/11.
- **Altri voti**: Nuova Zelanda (7/11) e Grenada (5/11), secondo ElectionGuide.
- **Contesto mercati**, da `docs/data/mercati.json` (altro livello della mappa): oggi a metà seduta il Brent scende a circa 93 $/bbl (-5%). Pesano le speranze di colloqui con l'Iran.

## 5. Cosa arriva nelle prossime due settimane (10-23 novembre) e perché conta

| Data (UTC) | Evento | Petrolio | Gas | Tassi | Titoli AI |
|---|---|---|---|---|---|
| 9-20/11 | COP31 ad Antalya (vertice dei leader l'11-12/11 secondo una fonte di stampa, non confermato) | Bassa | Bassa | — | Bassa (domanda elettrica dei data center) |
| **10/11 13:30** | **CPI USA di ottobre** | — | — | **Alta**: con due dissensi per un rialzo, un core sopra lo 0,3% riapre il rialzo a dicembre | Alta: i titoli growth soffrono rendimenti più alti |
| 10/11 17:00 | EIA STEO (previsioni su prezzi e produzione) | Media | Media (Henry Hub) | — | — |
| 12/11 17:00 | EIA, settimanale sul petrolio (giovedì per il festivo) | Media | — | — | — |
| 13/11 09:00 | IEA Oil Market Report | Alta: stima delle perdite di offerta del Golfo | Bassa | — | — |
| 13/11 10:00 | Eurostat, stima flash di PIL e occupazione | — | — | Media (BCE) | — |
| 13/11 13:30 | PPI USA | — | — | Media | — |
| metà novembre | OPEC MOMR (data non confermata) e revisione della capacità dei membri OPEC+ (attesa a metà mese) | Alta: è la base delle quote 2027 | — | — | — |
| 15/11 | Capo Verde, presidenziali | Bassa | — | — | — |
| **17/11 22:00** | **Nvidia, trimestrale (terzo trimestre fiscale 2027)** | — | — | — | **Molto alta**: misura la spesa per l'AI e trascina tutto il comparto |
| 18/11 10:00 | Eurostat, HICP definitivo di ottobre | — | Media (componente energia) | Media | — |
| 18/11 15:30 | EIA, settimanale sul petrolio | Media | — | — | — |
| 18/11 (stima) | Verbali FOMC del 27-28/10 | — | — | Media: quanto è ampio il fronte pro-rialzo | Media |
| **18-19/11** | **APEC, vertice dei leader a Shenzhen** | Media (domanda cinese) | Media (GNL) | — | **Alta**: possibili incontri USA-Cina su chip, export control e terre rare |

**Subito dopo (24-30/11)**: il 25/11 escono la seconda stima del PIL e il PCE di ottobre (BEA). Il 29/11 si tengono la **riunione ministeriale OPEC+** sulle quote 2027 e le **elezioni politiche anticipate in Spagna**. Il 30/11 scade il regime UE di sanzioni sulle trivellazioni turche nel Mediterraneo orientale. Più avanti: Fed l'8-9/12, G20 a Miami il 14-15/12, BCE e BoE il 17/12, Consiglio europeo il 17-18/12, BoJ il 17-18/12.

## 6. Collegamenti con gli altri livelli della mappa

- **Stretti** (`stretti.json`): OPEC+, IEA e OPEC MOMR riguardano Hormuz. Gli export del Golfo al 60-80% sono il motivo per cui le quote restano "teoriche".
- **Mercati** (`mercati.json`): le date del calendario spiegano i movimenti di Brent, Treasury, Bund e Nasdaq. Si possono collegare con `evento`/`id` (es. CPI → rendimento del decennale USA; Nvidia → indice dei semiconduttori).
- **Eventi** (`eventi.json`): le azioni OFAC sull'Iran e le scadenze delle sanzioni UE (Russia il 31/7/2027, Bielorussia il 28/2/2027, Iran il 13/4 e il 9/10/2027) vanno accostate agli eventi strategici.
- **Italia**: le elezioni politiche (data non fissata, 2027), la BCE (tassi sui mutui, spread BTP) e l'HICP dell'eurozona (bollette) sono le voci di maggiore esposizione.

## 7. Proposta per la mappa

- Un pannello laterale "Calendario" con una linea del tempo: 7 giorni passati in grigio con il valore uscito, 14 giorni futuri evidenziati, e filtri per categoria e importanza.
- Le voci con `paese` possono accendere il paese sulla mappa con un'icona per categoria (banca, urna, barile, stretta di mano, lucchetto). Banche centrali ed Eurostat vanno sulle sedi (Washington, Francoforte, Tokyo, Londra, Lussemburgo).
- Un badge "oggi/domani" per gli eventi ad alta importanza, con il conto alla rovescia in UTC.

## 8. Limiti

- **Le voci manuali vanno aggiornate a mano**: tasso BoJ, OPEC+, IEA, vertici, risultati delle elezioni USA ed elezioni senza data. OPEC, IEA, Consilium e G20 bloccano gli script (403).
- Il **calendario ICS della BLS** arriva solo a dicembre 2026: le date del 2027 compariranno quando la BLS le pubblicherà. L'**API BLS v1** è satura: conviene una `BLS_API_KEY` gratuita come secret di GitHub Actions, più `CONTATTO_EMAIL` per lo User-Agent.
- I **valori usciti** sono letti con espressioni regolari dal testo dei comunicati: se cambia la formulazione, il campo resta vuoto (non viene inventato). Solo l'ultima uscita di ogni serie ha `valore_uscito`.
- Le date **STEO dopo novembre** sono calcolate con la regola pubblicata dall'EIA (primo martedì dopo il primo giovedì del mese) e segnate con affidabilità "media". Il settimanale EIA è mostrato solo per 6 settimane.
- La **data dei verbali Fed** (18/11) è stimata (prassi delle tre settimane). La **data del MOMR OPEC** non è stata trovata ed è indicata solo come "2026-11".
- **Sanctions Map**: alcune scadenze UE possono essere già state rinnovate senza aggiornare il sito. Le azioni OFAC sono solo i titoli dei comunicati.
- Le **elezioni USA** sono provvisorie (dati del 4-6/11). L'infobox di Wikipedia è una fonte di supporto, da sostituire con i risultati certificati.
- Mancano ancora le aste del Tesoro USA, le riunioni di altre banche centrali (PBoC, SNB, RBI) e le trimestrali di altri titoli AI (Microsoft, Alphabet, TSMC). Si possono aggiungere come voci manuali o con nuove fonti.
- Lo schema non ha una categoria "societaria": la trimestrale Nvidia è finita in `dato-macro`, con una nota che lo spiega.
