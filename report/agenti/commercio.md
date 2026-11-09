# Agente RISORSE E COMMERCIO: chi esporta cosa, chi produce i minerali critici, dove dipendono Italia e UE

Rapporto del 9 novembre 2026. Script: `raccolta/commercio/raccogli.py`, solo libreria standard. L'ho eseguito davvero, ultima esecuzione completa senza errori il 9/11/2026: 38 paesi, 58 righe di dipendenze, 25 minerali e fonti energetiche.

**Tempo di esecuzione.** Ci vogliono circa 40 minuti. L'endpoint gratuito di Comtrade risponde "429 Too Many Requests" e "403 Quota Exceeded" dopo poche decine di chiamate, e lo script aspetta e riprova. Su GitHub Actions va bene: il limite è di 6 ore. La variabile facoltativa `COMMERCIO_CACHE` indica una cartella in cui riusare le risposte. Serve solo in sviluppo; in produzione non va impostata.

## File prodotti

| File | Dimensione | Contenuto |
|---|---|---|
| `docs/data/commercio.json` | ~320 KB | **`elementi`**: un record per paese (38). Ogni record contiene `anno`, `metodo` (`dichiarato` o `specchio`), i totali di export e import in USD e i primi 10 capitoli HS2 esportati e importati, con nome italiano, valore e quota. Contiene anche i primi 5 partner per export e import e le `voci_strategiche`: 30 voci HS4 (greggio 2709, gas 2711, chip 8542, terre rare 2805/2846, frumento, soia, armi 9306…) con valore e quota. In `risorse` ci sono produzione e riserve del paese, con quota mondiale e rango. Per i paesi del Golfo c'è in più `export_partner_specchio` (vedi sotto). **`dipendenze`**: 29 prodotti critici (HS6) importati dall'Italia e dalla UE-27 (solo import extra-UE), con i primi 3 fornitori, la quota e il flag `dipendenza_oltre_50`. |
| `docs/data/minerali.json` | ~70 KB | **`elementi`**: 25 voci. Ci sono petrolio, gas e carbone (EIA), uranio (WNA), poi litio, cobalto, rame (miniera e raffinato), nichel, terre rare, gallio, grafite, antimonio, tungsteno, manganese, stagno, vanadio, bauxite, ferro, platino, palladio, silicio metallico, magnesio, spugna di titanio (USGS) e il germanio, solo come nota. Per ogni voce: `produttori` con valore e quota mondiale, `riserve` dove esistono, anno, unità e fonte. **`controlli_export`**: 19 paesi con divieti, quote o licenze all'export di minerali, censiti da USGS con dati al 21/11/2025. |

Il formato è quello di AGENTI.md: `aggiornato`, `fonti`, `nota`, `elementi`, `errori`. Non sono dati puntuali: la chiave è `iso2`, da collegare ai poligoni dei paesi.

**Anno usato.** Per ogni paese è l'ultimo anno in cui ha dichiarato a Comtrade sia l'export sia l'import:
- 2025 per 28 paesi;
- 2024 per UA, QA, IQ, DZ e TW;
- 2023 per IR e AE, che non hanno dichiarato oltre.

**Dati "specchio".** Per RU (niente dati dal 2022), LY (niente dati recenti) e YE (dato 2024 incompleto) il commercio è ricostruito dalle dichiarazioni dei partner, anno 2024. I prodotti coprono i primi 15 partner: 83% del totale per la Russia, 94% per Libia e Yemen.

**Taiwan.** Comtrade la pubblica come reporter "Other Asia, nes" (codice 490): il dato è dichiarato e affidabile. Come *partner*, invece, il codice 490 resta senza ISO2. Arabia Saudita e Iran ci mettono destinazioni asiatiche non dichiarate: per esempio il 49,6% dell'export saudita risulta verso "Other Asia, nes".

## Fonti provate

| Fonte | Esito | Licenza | Note |
|---|---|---|---|
| UN Comtrade `public/v1/preview` | **Funziona**, senza chiave | Uso libero con citazione; vietata la redistribuzione massiva del database | Fino a 500 righe e 1 anno per chiamata. Ci vogliono limiti di frequenza (429/403) e pause. Gestisce più reporter in una chiamata e i codici HS a 2, 4 e 6 cifre. È la scelta più ripetibile: dati ufficiali, aggiornati al 2025. |
| Riferimenti Comtrade (`files/v1/app/reference/*.json`) | **Funziona** | come sopra | Codici dei paesi (ISO2/ISO3) e descrizioni HS. |
| OEC (`api.oec.world/tesseract`) | Risponde (HTTP 200), **non usata** | — | Si basa su BACI/Comtrade, quindi non aggiunge una fonte primaria. |
| WITS, Atlas di Harvard | **Non provate** | — | Comtrade basta. L'Atlas può servire in futuro per dati armonizzati e "puliti". |
| USGS MCS 2026, data release (ScienceBase, item `696a75d5d4be0228872d3bf8`) | **Funziona** | Pubblico dominio | `MCS2026_Commodities_Data.csv` (3,2 MB, codifica cp1252) e `T4_Country_Export_Control.csv`. Lo script trova i file dal JSON dell'item, quindi non dipende da un URL fisso. |
| EIA, bulk `INTL.zip` | **Funziona**, senza chiave | Pubblico dominio | 24 MB compressi, 129 MB di testo, aggiornato il 19/10/2026. Petrolio al 2025, gas e carbone al 2024, riserve di carbone al 2023. **Non contiene più le riserve di petrolio e di gas.** |
| CIA World Factbook (mirror `factbook/factbook.json`) | **Funziona** | Pubblico dominio | Lo uso solo per le riserve provate di petrolio e gas, stime 2021 con fonte EIA. Il dato è vecchio e va mostrato con l'anno. |
| World Nuclear Association, produzione mineraria di uranio | **Funziona** (tabella HTML) | © WNA, uso informativo con citazione | Dato 2024. |
| Energy Institute Statistical Review | **Non funziona** (403, protezione anti-bot) | — | Non è necessaria: EIA copre la stessa produzione in pubblico dominio. |

## Fatti chiave (dati nei file)

1. **La Cina controlla la raffinazione dei minerali "della transizione".** Quote mondiali stimate da USGS (MCS 2026) per il 2025:
   - terre rare: 69% dell'estrazione;
   - grafite naturale: 78%;
   - tungsteno: 79%;
   - silicio metallico: 87%;
   - magnesio: 86%;
   - gallio primario: circa 99% (900 t su circa 909 t; il totale mondiale USGS è arrotondato a 900 t);
   - rame raffinato: 48%.

   Su antimonio, gallio, germanio, grafite, magnesio, terre rare, tungsteno e materiali per batterie al litio Pechino applica licenze all'export (USGS, tabella T4, dati al 21/11/2025).
2. **Tre paesi dominano altrettanti metalli.** Sono stime USGS 2025:
   - la RD Congo estrae il 73% del cobalto mondiale (230.000 t su 310.000) e ha il 50% delle riserve; dal 2025 applica quote all'export;
   - l'Indonesia fa il 67% del nichel e ne vieta l'export di minerale grezzo dal 2020;
   - il Sudafrica fa il 71% del platino; la Russia fa il 44% del palladio.
3. **Il litio è più distribuito.** Nel 2025 Australia 32%, Cina 21% e Cile 19% della produzione mineraria (USGS). Le riserve maggiori sono in Cile: 9,2 milioni di t su 37.
4. **Uranio.** Nel 2024 il Kazakistan ha estratto il 38,6% dell'uranio mondiale (23.270 tU su 60.213), il Canada il 23,8% (WNA). Nel 2025 il primo fornitore extra-UE di uranio arricchito della UE è stato il Regno Unito, con il 56,7% (Comtrade, HS 284420).
5. **UE: dipendenze sopra il 50% da un solo paese.** Import extra-UE del 2025, Comtrade, reporter UE-27:

   | Prodotto | Primo fornitore | Quota | Valore |
   |---|---|---|---|
   | Moduli fotovoltaici | Cina | 98,6% | 9,0 mld USD |
   | Batterie al litio | Cina | 90,0% | 32,1 mld USD |
   | Magnesio grezzo | Cina | 89,3% | — |
   | Magneti permanenti | Cina | 88,3% | 1,2 mld USD |
   | Metalli delle terre rare | Cina | 78,4% | — |
   | Vitamina C | Cina | 74,9% | — |
   | Silicio iperpuro | USA | 73,3% | — |
   | Penicilline | Cina | 72,8% | — |
   | Carbonato di litio | Cile | 69,8% | — |
   | Grafite artificiale | Cina | 66,1% | — |
   | Antimonio | Tagikistan | 57,9% | — |
   | Platino | Sudafrica | 56,5% | — |
   | **GNL** | **USA** (Russia seconda con il 16,1%) | **52,6%** | 52,0 mld USD |

6. **Italia (Comtrade, 2025).** Dipendenze sopra il 50%:
   - magneti permanenti: 80,1% dalla Cina;
   - magnesio: 67,4% dalla Cina;
   - nichel grezzo: 65,3% dai Paesi Bassi (paese di spedizione, non di origine);
   - carbonato di litio: 60,0% dalla Germania (idem).

   Sull'energia nessun fornitore supera il 50%, ma ci vanno vicino:
   - gas via gasdotto (17,3 mld USD): Algeria 47,6%;
   - GNL (8,7 mld USD): USA 45,3%;
   - greggio (25,2 mld USD): Libia primo fornitore con il 24,5%.

   Il palladio grezzo (845 milioni di USD) arriva per il 41% dalla Russia.
7. **L'Italia è il primo cliente di diversi fornitori di energia.** Per l'Azerbaigian vale il 45,3% dell'export (2025), per la Libia il 25,0% (specchio 2024), per l'Algeria il 24,0% (2024) e per il Kazakistan il 19,7% (2025). L'esposizione è quindi reciproca.
8. **Il petrolio del Golfo va in Asia, ma i paesi del Golfo non lo dichiarano.** Iraq, Kuwait, Oman ed Emirati attribuiscono a "Areas, nes" rispettivamente il 96%, l'88%, il 62% e il 50% dell'export. I dati dei paesi acquirenti (specchio, 2024) mostrano:
   - Iraq: Cina 34,7%, India 27,1%;
   - Arabia Saudita: Cina 20,4%, Corea 11,1%, India 10,8%, Giappone 10,6%.

   Il greggio pesa per il 53% dell'export saudita (165 mld USD), il gas per il 60% di quello del Qatar (56,9 mld USD, 2024).
9. **Russia sotto sanzioni (specchio, 2024).** Partner dichiarati: export di 401 mld USD, per il 67% combustibili. I clienti sono Cina 32,4%, India 16,7% e Turchia 11,0%. Per gli import la Cina vale il 56,4%. L'Iran ha dichiarato l'ultima volta nel 2023: 68% combustibili. Secondo gli acquirenti, i primi clienti sono Cina 26,8% e Iraq 21,8%, ma il greggio iraniano verso la Cina passa in gran parte fuori dalle statistiche.
10. **Taiwan e i chip.** Nel 2024 i circuiti integrati (HS 8542) sono stati il 34,7% dell'export di Taiwan (164,9 mld USD); il capitolo 85 vale il 47,2%. I clienti sono USA 23,5% e Cina 20,4%. Nel 2025 la Corea ha esportato 142,8 mld USD di chip (20,1% dell'export). La Cina ne ha importati 425 mld USD (16,5% dell'import).

## Collegamenti con gli altri livelli della mappa

**Hormuz** (`stretti.json`: petrolio sceso a 4,9 milioni di barili/giorno nel 2° trimestre 2026, da 21,6).
- Ne dipende tutto l'export di Iraq, Kuwait, Qatar e la maggior parte di quello saudita ed emiratino. Le quote dei combustibili (HS 27) sull'export: Iraq 99%, Kuwait 88%, Qatar 84%, Arabia Saudita 69%, Emirati 50% (2023).
- I paesi più esposti sono gli importatori asiatici, per peso dei combustibili sull'import:
  - India: 27,8% dell'import, greggio da solo 18,4% (139 mld USD);
  - Corea: 22,2%;
  - Giappone: 19,6%;
  - Cina: 17,2%, greggio 295 mld USD.
- Per l'Italia il Qatar è il secondo fornitore di GNL (32,6% nel 2025) dopo gli USA (45,3%).

**Malacca.** Ci passa il greggio del Golfo diretto in Cina, Giappone e Corea. A Malacca e nel Mar Cinese Meridionale passano anche i flussi di Taiwan e della Corea (chip) e il nichel indonesiano (67% del mondo).

**Suez / Bab el-Mandeb.** È la rotta dei prodotti dalla Cina verso l'Italia:
- la Cina è il secondo fornitore dell'Italia, con il 10,2% dell'import;
- da qui passano magneti, batterie e pannelli solari, cioè le dipendenze del punto 5;
- passano anche il greggio del Golfo e il gas del Qatar destinati all'Europa.

**Bosforo e Kerch.** Nel 2024 il frumento è stato il 9,0% e il mais il 12,2% dell'export ucraino.

**Capo di Buona Speranza.** È la rotta del minerale di ferro brasiliano e dei metalli del Sudafrica (platino 71%, manganese 38%).

**Gasdotti** (`linee.json`, rapporto energia). TransMed e Greenstream portano il gas di Algeria e Libia, TAP quello dell'Azerbaigian: il punto 7 mostra quanto questi paesi dipendano dall'Italia come cliente.

**Sanzioni.**
- La Russia vende energia a Cina, India e Turchia.
- Il palladio russo (44% del mondo) arriva ancora in Italia: 41,1% dell'import di palladio grezzo nel 2025.
- La Russia ha un divieto all'export di uranio arricchito dal 2022 (USGS T4).

**Mercati** (`prezzi.json`).
- Brent, TTF e Henry Hub sono legati ai punti 6 e 8.
- La quota della Cina sulle terre rare e le licenze all'export si leggono sui titoli dei produttori di magneti e di auto.
- Le quote sul cobalto della RD Congo spingono il prezzo del cobalto.
- Il rame (Cile 23% della produzione da miniera, RD Congo 14%) è legato all'elettrificazione e ai data center AI.

## Proposta per la mappa

- **Paese cliccato → scheda "Commercio e risorse".** Due barre orizzontali con i primi 5 capitoli HS esportati e importati (quota %) e i primi 5 partner, con una freccia verso il paese partner. Per i paesi del Golfo si mostra `export_partner_specchio` al posto di "Areas, nes". Sotto, le risorse con quota mondiale ≥ 5%, come badge (es. "Cobalto 73% · 1°").
- **Filtro "minerale"** (da `minerali.json`). Colora i paesi per quota di produzione, con un tratteggio sui paesi che hanno controlli all'export (`controlli_export`).
- **Pannello "Italia/UE: dipendenze".** Elenco dei prodotti con `dipendenza_oltre_50 = true`, collegato agli stretti della rotta: Cina → Suez per magneti, batterie e pannelli; USA → Atlantico per il GNL.

## Limiti

- **I valori sono annuali, del 2024–2025, quindi precedenti alla crisi di Hormuz del 2026.** Mostrano la struttura degli scambi, non i flussi di oggi.
- **Paese di origine.** Le importazioni italiane da altri paesi UE sono attribuite al paese di spedizione, non di origine. Per esempio il nichel "dai Paesi Bassi" o il litio "dalla Germania" vengono in realtà da fuori UE. Per l'origine vera conviene guardare la riga UE-27, che riguarda solo l'extra-UE.
- **Dati specchio.** Sono valori CIF e mancano i partner che non dichiarano. Le voci HS4 strategiche non sono calcolate per RU, LY e YE.
- **Voci miste.** HS 811292 mescola gallio, germanio, indio, niobio e vanadio. Le quote sotto i 5 milioni di USD sono segnate `valore_trascurabile`, senza flag.
- **Riserve di petrolio e gas.** Sono stime 2021 del Factbook, perché EIA non le pubblica più nel bulk. **Il germanio** non ha una tabella mondiale USGS: i produttori non dichiarano.
- **Nomi.** I partner sono in inglese (nomi Comtrade) con ISO2. Le voci HS hanno nomi italiani redazionali.
