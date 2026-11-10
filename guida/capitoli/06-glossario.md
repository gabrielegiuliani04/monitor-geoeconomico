# Appendice — Glossario

Definizioni brevi, da poter ripetere a voce. Tra parentesi, dove trovi il termine nel sito o nei file.

| Termine | Che cos'è |
|---|---|
| **AIS** (Automatic Identification System) | Il transponder di bordo che trasmette posizione, rotta e identità della nave. Se è spento, la nave sparisce dai sistemi pubblici (`navi.json`) |
| **Navi «dark»** | Navi che viaggiano con l'AIS spento: per questo PortWatch conta meno transiti di Lloyd's List Intelligence a Hormuz |
| **Baltic Dry** | Indice dei noli delle navi per rinfuse secche; nel sito non è più raccolto in automatico per i termini d'uso della fonte |
| **Brent / WTI** | Prezzi di riferimento del greggio (mondiale / statunitense), in dollari al barile (*Prices and rates*) |
| **Bunker, VLSFO, HSFO, MGO** | *Bunker* è il carburante delle navi; VLSFO: olio a bassissimo zolfo, il più usato; HSFO: ad alto zolfo (con *scrubber*); MGO: gasolio marino (`bunker-emissioni.json`) |
| **CfD** (Contract for Difference) | Contratto con lo Stato che garantisce un prezzo fisso a un parco eolico: se il mercato paga meno lo Stato integra, se paga di più il produttore restituisce. È lo strumento delle aste in Regno Unito, Danimarca, Polonia |
| **Chokepoint** (passaggio strategico) | Stretto o canale con molto traffico e poche alternative: Hormuz, Bab el-Mandeb, Suez, Stretti danesi, Bosforo (*Chokepoints*) |
| **Chiave API / Secrets** | Password personale per scaricare dati da un servizio; su GitHub si conserva cifrata nei *Secrets* |
| **Disruption** | Interruzione o forte riduzione di un flusso (navi, gas, petrolio) |
| **Early warning** | Indicatori che si muovono prima del danno: flussi in calo, incidenti, prezzi, attenzione dei media |
| **EU ETS marittimo** | Il sistema europeo delle quote di CO₂ esteso alle navi: gli armatori comprano quote per le emissioni dei viaggi verso, da e dentro l'UE |
| **EUA** (EU Allowance) | Una quota di emissione (1 t di CO₂ equivalente): 86,91 € all'asta EEX del 9 novembre 2026; 87,71 € sul mercato secondario (Ship & Bunker, 6 novembre) |
| **FEU / TEU** | Container da 40 / da 20 piedi; un FEU vale due TEU |
| **FID** (Final Investment Decision) | La decisione finale di investimento: il momento in cui un progetto passa dalla carta ai contratti |
| **Flotta ombra** (*shadow fleet*) | Petroliere vecchie, spesso con bandiere di comodo e assicurazioni opache, usate per il petrolio russo o iraniano sotto sanzioni. Nel sito «flotta ombra probabile» è una **valutazione**, non un'etichetta ufficiale |
| **Forza maggiore** | Clausola che sospende un contratto per cause esterne (guerra, disastro): il Qatar la usa per il GNL dal 4 marzo 2026 |
| **FSRU** | Terminale galleggiante di rigassificazione del GNL |
| **FuelEU Maritime** | Regolamento UE 2023/1805: obbliga le navi a ridurre anno dopo anno l'intensità di gas serra dell'energia a bordo, con penali |
| **GitHub Actions / workflow** | Il servizio che esegue gli script a orari fissi; il *workflow* è il file con le istruzioni |
| **GitHub Pages / sito statico** | Sito fatto di file già pronti, pubblicato gratis da GitHub dalla cartella `docs/` |
| **GNL** (gas naturale liquefatto, LNG) | Gas raffreddato a −162 °C e trasportato con navi metaniere fino a un terminale di rigassificazione |
| **GNSS jamming / spoofing** | Disturbo dei segnali satellitari di posizione: il segnale viene coperto (*jamming*) o falsificato (*spoofing*). Il sito usa le mappe di GPSJam (`baltico-sicurezza.json`) |
| **GPR** (Geopolitical Risk Index) | Indice di Caldara e Iacoviello che conta gli articoli su guerre e tensioni (media 1985–2019 = 100): misura l'attenzione dei media, non il danno |
| **Henry Hub** | Prezzo di riferimento del gas negli Stati Uniti, in dollari per milione di BTU |
| **HVDC** | Cavi ad alta tensione in corrente continua, per lunghe distanze e sotto il mare (interconnessioni, parchi eolici offshore) |
| **IMF PortWatch** | Piattaforma del Fondo monetario internazionale e dell'Università di Oxford che stima dai segnali AIS le navi al giorno negli stretti e nei porti, con circa una settimana di ritardo |
| **IMO** | Organizzazione marittima internazionale (ONU): fa le regole globali delle navi |
| **JSON** | Formato di testo per i dati, leggibile da persone e programmi |
| **JWC Listed Areas** | Zone a rischio guerra del Joint War Committee (assicuratori di Londra): entrandovi si può pagare un premio aggiuntivo. 27 aree nella circolare JWLA-035 del 16 settembre 2026 |
| **Lloyd's List Intelligence (LLI)** | Società di dati marittimi a pagamento che ricostruisce anche i transiti delle navi «dark»; il sito ne cita i bollettini pubblici |
| **mb/g** | Milioni di barili al giorno, l'unità dei flussi di petrolio |
| **Nolo** (*freight rate*) | Il prezzo del trasporto via mare; per i container in dollari per FEU |
| **OSINT** | Analisi fatta solo con fonti aperte: stampa, dati pubblici, immagini satellitari gratuite, social, AIS |
| **Porto base** (*base port*) | Il porto da cui partono pale, torri e fondazioni per costruire un parco eolico offshore (Esbjerg, Eemshaven) |
| **Port Risk Index** | L'indice di rischio di 39 porti del progetto: probabilità × impatto, ogni giorno (§3.2) |
| **Probabilità × impatto** | Il modo standard di dare un punteggio a un rischio: quanto è probabile, per quanto fa male (*Risk*) |
| **PUN** | Prezzo unico nazionale dell'elettricità all'ingrosso in Italia (GME) |
| **TTF** (Title Transfer Facility) | Il mercato del gas olandese; il suo prezzo in €/MWh è il riferimento per tutta l'Europa |
| **UKMTO** | Centro della Marina britannica che pubblica gli avvisi di sicurezza per le navi (Golfo, Mar Rosso) |
| **War risk** | Assicurazione separata per guerra, mine, sequestro; si paga per viaggio in percentuale del valore della nave (a Hormuz 6–10% a ottobre 2026) |
| **WCI, FBX, SCFI, CCFI** | Indici dei noli container: Drewry World Container Index, Freightos Baltic Index, Shanghai e China Containerized Freight Index |
