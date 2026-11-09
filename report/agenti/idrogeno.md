# Idrogeno e ammoniaca verde nei porti — rapporto dell'agente

Aggiornato al 9 novembre 2026. File: `docs/data/idrogeno.json` (41 progetti come punti, 7 gasdotti H2 come linee schematiche, sezione `realta`, sezione `collegamenti`). Script: `raccolta/idrogeno/raccogli.py`. Voci curate: `raccolta/idrogeno/progetti.json`, `pipeline.json`, `realta.json`.

## In 30 secondi (per un colloquio)

1. **Cosa esiste davvero.** In Europa nel luglio 2025 erano operativi **571 MW** di elettrolisi (Hydrogen Europe, Clean Hydrogen Monitor 2025). I primi impianti grandi nei porti stanno partendo solo ora: **Holland Hydrogen 1** (Shell, 200 MW, Rotterdam) è quasi finito e l'avvio è atteso per fine 2026. **ELYgator** (Air Liquide, 200 MW) ha preso la FID a luglio 2025, con avvio a fine 2027. **Hyoffwind** (25 MW, Zeebrugge) ha gli elettrolizzatori installati da aprile 2026. **Amburgo-Moorburg** (100 MW) è in cantiere dal dicembre 2025. Il primo flusso reale produzione → rete → industria in Germania (Lingen → Marl) è partito nel 2026.
2. **Cosa è stato cancellato e perché.** Tra il 2024 e il 2026 si sono ritirati Ørsted (FlagshipONE), Shell ed Equinor (Norvegia), ArcelorMittal (acciaio DRI a Brema ed Eisenhüttenstadt), Air Products (Immingham), Fortescue (Gladstone e Arizona), BP (H2Teesside e AREH) ed Equinor (Eemshaven). I motivi ricorrenti sono quattro: **nessun cliente disposto a pagare il premio**, regole UE (RFNBO e addizionalità) ancora da recepire, costi di elettrolizzatori e capitale aumentati, priorità diverse (petrolio e gas, data center).
3. **Il divario con gli obiettivi.** REPowerEU punta a 10 + 10 Mt al 2030, che richiederebbero 90–100 GW di elettrolisi secondo la Commissione. Oggi l'Europa ha meno di 1 GW operativo e circa 3 GW su 31 pianificati hanno la FID (EIC). Nel mondo l'IEA ha ridotto la produzione potenziale al 2030 da 49 Mt (GHR 2024) a 37 Mt (GHR 2025) e poi a **27 Mt** (GHR 2026). Quella "sicura", da progetti operativi o in FID, è di circa **4,3 Mt**.
4. **Cosa significa per i porti del Nord.** Prima del 2030 i porti saranno **produttori locali per le raffinerie** (HH1 coprirà il 5–10% dell'idrogeno di Pernis) e **terminali di ammoniaca in sviluppo** (Uniper Wilhelmshaven, ACE e VTTI a Rotterdam, Fluxys-Advario ad Anversa), non ancora hub di import. Il collo di bottiglia sono i tubi verso l'entroterra: il Delta Rhine Corridor arriverà nel 2031–2032 e la dorsale danese nel 2030, solo con prenotazioni sufficienti.

## Fonti provate

| Fonte | Esito | Licenza |
|---|---|---|
| IEA Hydrogen Production and Infrastructure Projects Database (pagina prodotto) | **Non funziona in automatico**: HTTP 403 ai client automatici, il download passa dal sito. Lo script lo legge se si salva l'xlsx in `raccolta/idrogeno/iea/` o si imposta `IEA_H2_DB_URL`. Il parser xlsx (solo libreria standard) è stato testato su un file di prova. | CC BY 4.0 |
| IEA Northwest European Hydrogen Monitor 2025 (PDF su iea.blob.core.windows.net) | Funziona | CC BY 4.0 |
| IEA Global Hydrogen Review 2025 (PDF) | Funziona | CC BY 4.0 |
| IEA Global Hydrogen Review 2026 (18/06/2026) | Le pagine iea.org rispondono 403: letto **tramite sintesi** (GH2, stampa). Affidabilità media. | CC BY 4.0 |
| Port of Rotterdam, Ammonia Energy Association, Fluxys, BESIX, Città di Amburgo, RWE, FNB Gas (via pv magazine), Pipeline & Gas Journal, Pipeline Journal | Funzionano | Fatti citati |
| S&P Global, Argus, Gasworld, H2 View, Air Liquide, Mining Weekly, Seatrade, Marine Log | 403 ai client automatici: i fatti vengono da estratti di ricerca o da ripubblicazioni, indicati come tali | Fatti citati |
| Hydrogen Insight, Reuters (diretto) | Non usati direttamente. Reuters è citato tramite la ripubblicazione del factbox su P&GJ (luglio 2025). | — |

Nessuna fonte richiede una chiave API. Lo script non scarica nulla dalla rete, tranne l'eventuale `IEA_H2_DB_URL`. Legge solo file locali, quindi gira ogni giorno su GitHub Actions senza fallire.

## Cosa contiene `docs/data/idrogeno.json`

- **`elementi`** (punti). Per ogni progetto: `lat`, `lon`, `nome`, `paese`, `porto`, `categoria` (elettrolizzatore, terminale-import, bunkeraggio, e-fuel, export, rete-h2-locale, idrogeno-blu, domanda-industriale), `stato` (operativo, in costruzione, FID, sviluppo [pre-FID], annunciato, sospeso, cancellato), `mw`, `capacita` (t/anno o t/giorno come da fonte), `anno`, `operatore`, `fonte`, `link`, `data_fonte`, `affidabilita`, `note`. Ci sono anche:
  - `precisione_coord`: sito, area o regione. Molti punti sono collocati solo a livello di area portuale. **Non sono coordinate di impianto.**
  - `focus`: nord-europa, italia o esportatori-e-altri.
  - `rete_vicina`: la linea ≥380 kV o HVDC più vicina, calcolata da `rete-elettrica.json`.
  - `hvdc_entro_60km`: i collegamenti HVDC entro 60 km.
- **`pipeline`** (linee, `g` = [[lon, lat]...]). Hynetwork Rotterdam, Delta Rhine Corridor, Kernnetz Lubmin–Bobbau e Lingen–Marl, Danish Hydrogen Backbone 1, H2Med–BarMar, SoutH2 Corridor. Il tracciato è **schematico**: i vertici sono solo le città o i nodi di partenza e arrivo.
- **`realta`**:
  - `obiettivi`, `capacita_reale`, `costi`;
  - `aste_ehb` (con l'"esito reale" dopo le rinunce), `h2global`, `cancellazioni`, `rinvii`;
  - `marittimo` (FuelEU, IMO, flotta), `contesto_2026`;
  - `sintesi_progetti` (conteggi e MW per stato).
- **`collegamenti`**:
  - rete elettrica: metadati della lettura;
  - eolico offshore: `offshore-nord.json` **non esisteva** all'esecuzione, quindi il collegamento è stato saltato. Lo script lo aggancia da solo quando il file comparirà;
  - gas: TTF da `prezzi.json` e stima del costo dell'H2 grigio.

## Fatti attuali (numero, data, fonte)

1. **Holland Hydrogen 1**: 200 MW, 60 t/giorno, avvio "later in 2026". Coprirà il 5–10% del fabbisogno di H2 di Pernis ed è alimentato dal parco offshore HKN da 759 MW. *S&P Global, 30/04/2026.* Era annunciato per il 2025.
2. **Kernnetz**: approvato il 22/10/2024 per 9.040 km. Oltre 500 km sono pronti, di cui 507 convertiti dal gas, con altri 900 km previsti nel 2026–27. Sono stati prenotati **quasi 6 GW** di capacità. *FNB Gas, 22/10/2026.*
3. **Delta Rhine Corridor** (H2 Rotterdam → Germania): previsto per il **2031–2032**, quattro anni di ritardo rispetto al 2028. Fino ad allora l'idrogeno viaggerà su chiatta. *Port of Rotterdam, 2025.*
4. **Danish Hydrogen Backbone 1** (Esbjerg → Frøslev): 2,7 GW in vendita, esercizio a fine 2030. Si costruisce solo se si prenotano **almeno 0,5 GW entro il 1/12/2026**. Sostegno statale di 16,5 miliardi di DKK. *Pipeline Journal, 05/02 e 01/10/2026.*
5. **European Hydrogen Bank**:
   - pilota (2024): 7 progetti, circa 720 milioni di euro, premi di 0,37–0,48 €/kg;
   - seconda asta (2025): 15 progetti, 992 milioni di euro, premi di 0,20–1,88 €/kg. Poi 7 su 15 si sono ritirati (oltre il 75% della capacità) e a gennaio 2026 risultavano firmati **solo 6 accordi per 271 milioni di euro** (S&P, via ricerca);
   - terza asta (07/05/2026): 9 progetti, 1,09 miliardi di euro, 1,1 GW, premi di 0,44–3,49 €/kg, domanda oltre 6 volte il budget. *pv magazine / Commissione europea.*
6. **Costi**:
   - H2 grigio nel Nord-Ovest europeo: 2,9 €/kg nel 2024, con TTF a 10 €/MBtu; 4,8 €/kg nel 2022, con TTF a 39 €/MBtu;
   - H2 da eolico: **5,3–7 €/kg** nel 2024;
   - indice HYDRIX (2024): 240 €/MWh, quasi 2,5 volte il grigio. *IEA NWE Hydrogen Monitor 2025.*
7. **Gas oggi**: TTF a **82,3 €/MWh** il 09/11/2026 (`prezzi.json`), con una media di 90 €/MWh nelle ultime 22 sedute. Interpolando i due punti IEA, l'H2 grigio costerebbe circa **3,8 €/kg**. È una *stima dell'osservatorio*: ignora il prezzo della CO2. Con il gas caro il divario con l'H2 eolico si riduce a circa 1,5–3 €/kg, ma non si chiude.
8. **H2Global**: Fertiglobe (Egitto) fornirà ammoniaca a Rotterdam: 19.500 t nel 2027, fino a 397.000 t entro il 2033, a **1.000 €/t consegnato**, per un massimo di 397 milioni di euro (BMWK, 11/07/2024). La FID dell'impianto egiziano a inizio 2026 era ancora "attesa".
9. **Wilhelmshaven (Uniper)**: open season chiusa con successo a settembre 2026. Fino a 2,6 Mt/anno di NH3 e un cracker. Contratto vincolante per **500.000 t/anno** di ammoniaca da AM Green (India) "già dal 2028". *Ammonia Energy Association, 13/09/2026.*
10. **Bunkeraggio**:
    - Rotterdam: pilota di ammoniaca nave-nave da 800 m³ (aprile 2025);
    - Zhoushan: primo bunkeraggio **commerciale** nave-nave di ammoniaca verde, 1.000 t (13/10/2026);
    - Port Hedland: prova sulla prima portarinfuse ad ammoniaca, la *Mineral Europa* (02/11/2026);
    - metanolo: Singapore ne ha bunkerate 1.600 t nel 2024. Kassø (DK) produce fino a 42.000 t/anno di e-metanolo.

## Cosa è stato cancellato e perché (selezione; elenco completo in `realta.cancellazioni`)

| Data | Chi | Cosa | Perché |
|---|---|---|---|
| 08/2024 | Ørsted | FlagshipONE, e-metanolo 55 kt/anno (SE) | Mercato degli e-fuel lento, nessun contratto di acquisto |
| 09/2024 | Shell, Equinor | Idrogeno blu in Norvegia, gasdotto H2 Norvegia–Germania | Mancanza di domanda |
| 06/2025 | ArcelorMittal | DRI a H2 a Brema ed Eisenhüttenstadt (2,5 mld €) | Economia del progetto nonostante 1,3 mld € di sussidi |
| 06/2025 | Air Products | Terminale e impianto di Immingham (UK) | L'ammoniaca importata è esclusa dai sostegni britannici |
| 07/2025 | Fortescue | PEM50 Gladstone (50 MW) e Arizona (80 MW), entrambi già in FID | Politica USA; cambio di tecnologia |
| 08–09/2025 | Vincitori EHB-2 | 7 grant su 15 restituiti (Zeevonk NL, Lubmin DE…) | Garanzie di completamento, avvio obbligatorio entro 5 anni |
| 12/2025 | BP | H2Teesside (blu, UK) | Il terreno è andato a un data center IA; domanda locale in calo |
| 03/2026 | Equinor | H2M Eemshaven (blu, NL) | Incertezza normativa, fondi, nessuna rete H2 locale |

**Valutazione.** Si cancella soprattutto dove manca il cliente. I progetti che vanno avanti (HH1, ELYgator, Hyoffwind, Moorburg, Lingen) hanno tutti un **acquirente vicino e già esistente**: raffinerie, chimica, rete locale. Gli obblighi RED III nell'industria e nei trasporti e FuelEU sono l'unica vera leva di domanda. La loro trasposizione nazionale è in ritardo, come segnala l'IEA.

## Italia a confronto

- **Operativo**: Sapio a Porto Marghera, 5 MW, inaugurato il 16/07/2026 (ANSA).
- **In costruzione**: Trieste (North Adriatic Hydrogen Valley), 2,5 MW, con prima produzione prevista a fine 2026.
- **Annunciati e fermi**: la Puglia Green Hydrogen Valley (Brindisi 60 MW su 220 MW con Taranto e Cerignola) è del 2021 e non risultano FID né cantieri.
- **Nessun terminale** di import di ammoniaca o H2 trovato a Trieste, Taranto, Brindisi o Genova. A Genova esiste solo un'idea di elettrolizzatore dell'AdSP, senza stato verificabile, ed è esclusa dalla mappa.
- **SoutH2 Corridor**: progetto PCI da 3.300 km. Il piano Snam 2026–2030 riduce la spesa sul backbone italiano a circa 200 milioni di euro (erano 380) e sposta la **FID "entro l'inizio del 2030"**. Un tubo funzionante prima della metà degli anni 2030 è quindi improbabile (*valutazione*).
- Ordine di grandezza: tutta l'elettrolisi portuale italiana operativa è circa 1/40 di un solo impianto di Rotterdam.

## Collegamenti con gli altri livelli

- **Rete elettrica** (`rete-elettrica.json`). Lo script calcola per ogni punto la linea ≥380 kV o HVDC più vicina:
  - i siti di **Eemshaven** sono a meno di 2 km dalla linea Noord-West 380 kV e entro 60 km dagli approdi COBRA (DK) e NorNed (NO). È il porto meglio "cablato";
  - **Maasvlakte** si trova lungo i corridoi dei cavi IJmuiden Ver e BritNed;
  - **Brunsbüttel e Amburgo** stanno sull'avvio di SuedLink e vicino a NordLink.

  L'H2 nei porti è prima di tutto una **questione di connessione alla rete e di congestione**: il Porto di Rotterdam la cita come freno ai terminali (marzo 2026).
- **Eolico offshore**. HH1 si alimenta da Hollandse Kust Noord, ELYgator da OranjeWind e HKZ, RWE Eemshaven da OranjeWind. Quando ci sarà `offshore-nord.json`, lo script aggiungerà i parchi entro 150 km.
- **Gas** (`prezzi.json`). Il gas pesa circa il 70% del costo dell'H2 grigio (IEA). Ogni +10 €/MWh di TTF alza l'H2 grigio di circa 0,19 €/kg (*stima* dalla pendenza IEA). Il conflitto in Medio Oriente del 2026 ha raddoppiato l'urea tra gennaio e maggio (IEA GHR 2026), ma l'IEA scrive che l'H2 rinnovabile "non può dare una risposta immediata".
- **Stretti e rotte**. NEOM (Mar Rosso), Ain Sokhna (Suez), Duqm (Mar Arabico) e Kakinada esportano verso Rotterdam e Wilhelmshaven passando da **Bab el-Mandeb e Suez**: l'ammoniaca verde "di importazione" ha lo stesso rischio di rotta del GNL qatariota.
- **FuelEU Maritime** (in vigore dal 2025: −2% di intensità GHG nel 2025, −6% nel 2030, moltiplicatore ×2 per gli RFNBO fino al 2033). Spinge metanolo e ammoniaca nei porti UE. L'**IMO Net-Zero Framework** è stato aggiornato a ottobre 2025 (57–49) e la ripresa è prevista per il **4 dicembre 2026**.

## Indicatori da seguire

1. **Prima produzione di HH1**, attesa per fine 2026: è la prova che un impianto da 200 MW gira davvero in un porto UE.
2. **Prenotazioni del Danish Hydrogen Backbone 1** entro il 1/12/2026: se non si arriva a 0,5 GW il tubo Esbjerg–Germania non si fa.
3. **Grant firmati dalla terza asta EHB**, cioè quanti dei 9 progetti firmano davvero. L'apertura di IF26, indicata per dicembre 2026 con 500 milioni di euro, va confermata.
4. **FID di Uniper Maasvlakte**, attesa nel secondo semestre 2026, e **FID dei terminali di ammoniaca** (ACE, VTTI, Fluxys-Advario, Uniper Wilhelmshaven).
5. **Voto IMO** del 4/12/2026 e prime navi ad ammoniaca che fanno scalo nel Nord Europa.
6. **Prima ammoniaca di NEOM** (metà 2027), **FID di Egypt Green Hydrogen** (H2Global → Rotterdam 2027) e **FID di Hyphen** (fine 2027).
7. **TTF contro H2 rinnovabile** (HYDRIX): se il TTF resta sopra 80 €/MWh, il divario di costo si riduce sensibilmente.
8. **Trasposizione di RED III** nei paesi, cioè le quote RFNBO nell'industria al 2030: è il vero motore della domanda.

## Proposta per la mappa

- Livello **"Idrogeno nei porti"**:
  - simbolo per categoria: cerchio per l'elettrolizzatore, quadrato per il terminale di import, ancora per il bunkeraggio, triangolo per l'export;
  - colore per stato: verde operativo, blu in costruzione/FID, grigio sviluppo/annunciato, rosso barrato cancellato o sospeso;
  - dimensione proporzionale ai MW, dove noti.
- **Linee tratteggiate** per i gasdotti H2, con l'etichetta "schematico" e l'anno di esercizio. I tratti operativi (Lubmin–Bobbau, Lingen–Marl) vanno a tratto pieno.
- Filtro **"cosa esiste davvero"**, che mostra solo gli impianti operativi e in costruzione: rende visibile il divario.
- Pannello `realta` con due barre: **obiettivo REPowerEU 20 Mt** contro **circa 1 Mt mondiale prodotto nel 2025**, e la curva dei potenziali IEA 49 → 37 → 27 Mt.
- Usare `precisione_coord` per sfocare i punti "regione" (alone invece di un punto preciso).

## Limiti

- I progetti sono **curati a mano** (41) e non sono un censimento. Il database IEA, che conta migliaia di righe, non è scaricabile in automatico. Le somme di MW in `sintesi_progetti` valgono solo per il campione.
- Molte coordinate sono a livello di area o regione. I tracciati dei gasdotti sono schematici.
- Alcuni dati vengono da **sintesi di ricerca** di articoli a pagamento o bloccati (S&P, Argus, GHR 2026) e sono marcati con affidabilità media o bassa. Tra questi: lo stato di BP H2-Fifty, di BP Wilhelmshaven e del terminale RWE di Brunsbüttel, l'identità di "NJK" con Njordkraft e IF26.
- Per il **Marocco** nessun dato verificato è stato trovato: è escluso. Su Taranto, Brindisi e Genova non c'è nulla oltre agli annunci.
- La stima dell'H2 grigio con il TTF di oggi è un'interpolazione lineare su due punti IEA, senza CO2: va usata solo come ordine di grandezza.
- Licenze: i dati IEA sono CC BY 4.0 (da citare). Le altre fonti sono fatti citati con link. Nessun dato è CC BY-NC.
