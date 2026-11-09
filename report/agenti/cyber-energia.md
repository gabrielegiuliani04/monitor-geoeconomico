# Rischio cyber per energia ed eolico: il caso dei "frigoriferi" e cosa insegna

*Agente CYBER-ENERGIA, 9 novembre 2026. Taglio difensivo: nessun dettaglio tecnico sfruttabile, nessun indirizzo di dispositivi, nessuna ricerca di sistemi esposti.*

## Risposta breve a Gabriele

**Che cosa hai letto.** Quasi certamente l'attacco ai **frigoriferi e congelatori dei supermercati francesi**. Nella notte tra l'**11 e il 12 ottobre 2026** qualcuno è entrato da remoto nei controller della refrigerazione di centinaia di negozi (Intermarché, Carrefour, Leclerc, Coopérative U, Monoprix, Netto) e ha portato le temperature fino a 50 °C, oppure ha fatto partire sbrinamenti lunghissimi. Merce buttata, alcuni principi d'incendio. Le stime iniziali parlavano di 500-700 negozi; Al Jazeera oggi scrive oltre 1.000. **Oggi, 9 novembre 2026, la Francia ha attribuito l'attacco alle Guardie della Rivoluzione iraniane (IRGC)**: il ministro degli Esteri Barrot chiede sanzioni UE (Reuters, AP, BBC, Al Jazeera, 9-11-2026). Una seconda ondata ha colpito l'1-2 novembre oltre 115 negozi in Belgio, **Paesi Bassi** (almeno 17 attività secondo Danfoss), Lussemburgo, Svezia, Irlanda ed **Estonia**. Ci sono anche casi sospetti in Sicilia, con causa non confermata. Il legame tra l'IRGC e l'ondata di novembre non è dimostrato nelle fonti che ho letto. Prima di oggi alcuni gruppi filorussi avevano rivendicato gli attacchi.

**Non c'entrano i frigoriferi di casa né una "botnet di elettrodomestici".** Sono stati colpiti **controller industriali connessi** (Danfoss, danese, poi Copeland e Dixell), spesso **modelli vecchi non più aggiornati** e raggiungibili da Internet per la manutenzione remota.

**Può succedere all'eolico?** Il meccanismo sì. L'effetto sarebbe diverso e oggi è più contenuto.
- **Sì, perché la logica è la stessa e i precedenti ci sono già.** Anche l'eolico e il solare dipendono da molti dispositivi connessi, gestiti da remoto da produttori e manutentori. Nel 2022 un attacco al satellite KA-SAT ha tolto il controllo remoto a **circa 5.800 turbine Enercon**. Il 29 dicembre 2025 un attacco distruttivo ha colpito **oltre 30 parchi eolici e solari in Polonia**: ha tolto la comunicazione con la rete, ma non la produzione.
- **Il punto più debole non sono le grandi turbine offshore.** Sono i **milioni di piccoli inverter solari** e altri dispositivi domestici comandati dal cloud del produttore, molti cinesi: oltre il 70% in Germania secondo il BSI. Lì un comando sbagliato, ostile o anche solo commerciale (caso Deye, 2024) può spegnere tanta potenza insieme.
- **Dove sta la capacità esposta.** In Mare del Nord e Baltico la capacità è concentrata in pochi grandi parchi: Hornsea, Dogger Bank, Borssele, Hollandse Kust, Gemini, Horns Rev, Kriegers Flak, Baltic Power, Arcadis Ost. Questa è solo una mappa di dove sta la capacità, non un giudizio sulla loro sicurezza. Questi parchi sono gestiti da operatori grandi, soggetti a NIS2, con protezioni elettriche locali. Al 9-11-2026 **non è noto alcun attacco cyber riuscito a un parco offshore europeo**.

## 1. Il caso: candidati e meccanismo

| Candidato | Data | Fonte | Probabilità che sia "quello" |
|---|---|---|---|
| Controller della refrigerazione di supermercati (FR, poi BE/NL/LU/SE/IE/EE, forse IT); **attribuito dalla Francia all'IRGC** | 11-12 ott 2026; 1-2 nov 2026; attribuzione 9 nov 2026 | [Reuters via Al-Monitor](https://www.al-monitor.com/originals/2026/11/french-officials-blame-iran-refrigerator-hacks-vow-retaliation), [Al Jazeera 13-10](https://aljazeera.com/news/2026/10/13/unprecedented-cyberattack-hits-french-supermarkets-causing-food-losses), [SecurityWeek](https://securityweek.com/over-100-european-stores-hit-as-supermarket-fridge-attacks-resume), [Open (Sicilia)](https://www.open.online/2026/11/02/supermercati-frigoriferi-hacker-italia-sicilia/) | **molto alta** |
| Botnet IoT Aisuru/Kimwolf (router, telecamere, DVR): attacchi DDoS record da 29,7 e poi 31,4 Tbps, smantellata a marzo 2026 | ott 2025 - mar 2026 | [Help Net Security](https://www.helpnetsecurity.com/2026/03/20/us-disrupts-iot-botnets-ddos-attacks-aisuru-kimwolf/) | bassa (niente frigoriferi) |
| "Frigorifero che manda spam" (Proofpoint), poi smentito da Symantec | gen 2014 | [Computerworld](https://www.computerworld.com/article/1491026/blame-infected-windows-pcs-not-smart-fridge-for-spam-spewing-botnet-attack.html) | bassa |

**Il meccanismo, spiegato a livello di concetti:**
1. **Dispositivi connessi per comodità.** Il manutentore vuole vedere e regolare l'impianto da remoto, quindi il controller resta raggiungibile da Internet.
2. **Protezioni deboli e prodotti a fine vita.** Password predefinite o deboli, nessun aggiornamento (Danfoss: molti modelli colpiti non erano più supportati), nessuna rete separata.
3. **Scala.** Gli aggressori trovano tanti dispositivi uguali e li colpiscono in serie, di notte, quando nessuno guarda. Forescout conta oltre 20 attacchi rivendicati a sistemi di refrigerazione dal gennaio 2026.
4. **Effetto fisico.** Non si rubano dati: si cambia un parametro (temperatura, sbrinamento) e il danno è materiale.
5. **Botnet IoT.** È un concetto diverso: dispositivi infettati e usati insieme per un altro scopo, per esempio inondare un sito di traffico. Il caso dei frigoriferi è **manomissione diretta**, non botnet.
6. **Dipendenza dal fornitore.** Chi controlla il cloud o l'accesso remoto del produttore controlla la flotta. Per l'energia questo è il punto chiave.

Precedente dello stesso attore: nel novembre 2023 i **CyberAv3ngers**, legati all'IRGC, hanno manomesso controller industriali esposti in impianti idrici USA e di altri Paesi ([CISA AA23-335A](https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-335a)). Lo schema è lo stesso: si sceglie una marca di dispositivo, non una vittima.

## 2. Precedenti reali nell'energia

| Data | Caso | Effetto | Fonte |
|---|---|---|---|
| 23-12-2015 | Ucraina, 3 distributori | ~225.000 clienti al buio per ore | [CISA](https://www.cisa.gov/news-events/ics-alerts/ir-alert-h-16-056-01) |
| 17-12-2016 | Kyiv, sottostazione Pivnichna (Industroyer) | ~1 ora di blackout | [ESET](https://www.welivesecurity.com/2017/06/12/industroyer-biggest-threat-industrial-control-systems-since-stuxnet/) |
| 19-11-2021 | Vestas (DK), sistemi IT | IT spento; nessun impatto dichiarato sulle turbine; attribuzione non confermata | [ITPro](https://www.itpro.com/security/cyber-attacks/367498/russian-affiliates-believed-to-be-behind-cyber-attacks-on-wind) |
| 24-02-2022 | **Viasat KA-SAT**, effetto collaterale su **Enercon** | ~5.800 turbine (oltre 10-11 GW) senza telecontrollo; produzione continua; >95% riconnesse entro il 19-04 | [SentinelOne](https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/) |
| 31-03-2022 | **Nordex**, ransomware rivendicato da Conti | accesso remoto alle turbine spento per precauzione | [SecurityWeek](https://www.securityweek.com/conti-ransomware-gang-claims-cyberattack-wind-turbine-giant-nordex) |
| 11-04-2022 | **Deutsche Windtechnik** | telecontrollo di ~2.000 turbine spento per ~1 giorno | [The Record](https://therecord.media/german-wind-farm-operator-confirms-cybersecurity-incident-after-ransomware-group) |
| 08-04-2022 | Ucraina, **Industroyer2** | sventato | [ESET](https://www.welivesecurity.com/2022/04/12/industroyer2-industroyer-reloaded/) |
| 10-10-2022 | Ucraina, blackout da attacco OT insieme ai missili | interruzione locale | [Mandiant](https://cloud.google.com/blog/topics/threat-intelligence/sandworm-disrupts-power-ukraine-operational-technology) |
| 11-05-2023 | **Danimarca**, 22 aziende energetiche violate tramite firewall | isolamento delle reti, nessun cliente colpito | [SecurityWeek su SektorCERT](https://www.securityweek.com/22-energy-firms-hacked-in-largest-coordinated-attack-on-denmarks-critical-infrastructure/) |
| 15-11-2024 | **Deye**: inverter disattivati da remoto (USA, UK, Pakistan); per il produttore non è un attacco | dispositivi bloccati | [Born City](https://borncity.com/win/2024/11/28/deye-deactivates-solar-inverters-in-usa-uk-and-pakistan/) (fonte di qualità media) |
| 12-2024 | **Danimarca**, acquedotto sabotato da Z-Pentest (legato allo Stato russo secondo FE-DDIS) | tubi rotti, case senz'acqua | [FE-DDIS](https://www.fe-ddis.dk/globalassets/fe/dokumenter/2025/-russia-responsible-for-cyber-attacks-.pdf) |
| 07-04-2025 | **Norvegia**, diga di Bremanger | valvola aperta per 4 ore | [Security Affairs](https://securityaffairs.com/181143/hacktivism/norway-confirms-dam-intrusion-by-pro-russian-hackers.html) |
| 14-05-2025 | **Reuters**: radio non documentate in inverter e batterie cinesi | nessun effetto noto; fonti anonime | [Reuters (copia)](https://www.insurancejournal.com/news/international/2025/05/16/824006.htm) |
| 29-12-2025 | **Polonia**: oltre 30 parchi eolici e solari e una centrale di cogenerazione | comunicazione e telecontrollo persi, wiper; produzione non interrotta | [CERT Polska](https://cert.pl/en/posts/2026/01/incident-report-energy-sector-2025/) |

**Allarmi delle agenzie** (dettagli in `allarmi_agenzie` nel JSON):
- **CISA/FBI/NSA e partner** (9-12-2025): avviso sui gruppi filorussi che manomettono OT esposta.
- **Danimarca**: minaccia di attacchi distruttivi alzata a MEDIA (giugno 2024); preparazione del settore energetico ad arancione (settembre 2025).
- **RDI olandese**: nove inverter testati nel 2023, nessuno pienamente conforme; maggiore vigilanza annunciata a luglio 2025.
- **BSI tedesco**: preferisce il comando locale tramite smart meter al cloud del produttore.
- **ENISA**: Threat Landscape 2025.
- **Forescout**: SUN:DOWN, 46 vulnerabilità in inverter e portali (marzo 2025).

Nel Mare del Nord e nel Baltico **non risultano attacchi cyber riusciti a parchi offshore**. Il rischio documentato lì è soprattutto fisico: cavi e sorvoli di droni.

## 3. Esposizione

**Per paese** (WindEurope, fine 2025; solare da fonti nazionali):

| Paese | Eolico totale | di cui offshore | Quota eolico nel mix | Solare | Inverter cinesi |
|---|---|---|---|---|---|
| Danimarca | 7,5 GW | 2,7 GW | **50%** | ~6,3 GW | dato mancante |
| Paesi Bassi | 11,8 GW | 4,7 GW | 29% | ~29,4 GWp | dato mancante |
| Germania | 77,7 GW | 9,6 GW | 28% | ~117 GW | **>70%** (BSI) |
| Regno Unito | 32,9 GW | 17,0 GW | 31% | dato mancante | dato mancante |
| Polonia | 11,2 GW | 0 | 14% | ~24,8 GW | dato mancante |
| Lituania | 2,5 GW | 0 | 33% | ~3,0 GW | divieto di accesso remoto >100 kW |
| Belgio | 5,9 GW | 2,3 GW | 15% | dato mancante | dato mancante |
| Svezia, Finlandia, Estonia, Lettonia, Norvegia | vedi JSON | | | | |

In Europa: 304 GW di eolico, di cui 38,6 GW offshore. Nell'UE: 407 GW di solare (SolarPower Europe).

**Per produttore:**
- **Turbine.** Nel 2025 i fornitori europei hanno coperto circa il 94,5% delle nuove installazioni in Europa (GWEC): Vestas, Nordex (primo in Europa), Siemens Gamesa, Enercon, GE Vernova. I produttori cinesi hanno installato solo 446 MW in Europa. Il rischio "fornitore ostile" nell'eolico oggi è basso. Il rischio "fornitore attaccato" (Vestas, Nordex, Deutsche Windtechnik) è reale.
- **Inverter.** Huawei e Sungrow hanno circa il 55% del mercato mondiale nel 2024 (Wood Mackenzie). Le aziende con sede nell'UE avevano il 21% del mercato europeo nel 2023 (SolarPower Europe). Qui si concentra il rischio di dipendenza.

**Per tecnologia** (valutazione dell'agente; voce completa nel JSON):
- **Esposizione alta:** inverter e batterie domestiche; cloud dei fornitori; accesso remoto e SCADA di flotta dei produttori e manutentori; controller di impianti tecnici (refrigerazione di porti e magazzini).
- **Esposizione media:** turbine onshore e offshore, che hanno sistemi di sicurezza locali; collegamenti satellitari e 4G; aggregatori di flessibilità.
- **Sottostazioni offshore e HVDC:** impatto alto ma probabilità bassa.

**"Load altering attacks"**, cioè migliaia di dispositivi accesi e spenti insieme. Il tema è studiato da oltre dieci anni:
- Mohsenian-Rad e Leon-Garcia, IEEE TSG 2011;
- Dabrowski, Ullrich e Weippl, *Grid Shock*, ACSAC 2017;
- Amini, Pasqualetti e Mohsenian-Rad, IEEE TSG 2018;
- Soltan, Mittal e Poor, *BlackIoT*, USENIX Security 2018. In simulazione, botnet di condizionatori o scaldabagni possono causare blackout.

Huang, Cárdenas e Baldick (USENIX Security 2019) mostrano che le protezioni reali della rete riducono molto l'effetto. L'RDI olandese avverte che un attacco alle **piattaforme** di produttori e aggregatori può muovere abbastanza potenza da toccare il sistema. **Nessun caso reale finora.**

## 4. Scenari plausibili (VALUTAZIONI, non fatti)

1. **Probabile:** ransomware sull'IT di un produttore, manutentore o operatore. Il telecontrollo di una flotta viene staccato per giorni, ma la produzione continua. È già successo tre volte nel 2021-2022.
2. **Plausibile:** gruppi hacktivisti o legati a uno Stato (filorussi, IRGC) manomettono pannelli esposti di piccoli impianti: solare commerciale, biogas, teleriscaldamento, impianti tecnici portuali. Danno locale, molta visibilità mediatica. È lo schema di frigoriferi, dighe e acquedotti.
3. **Plausibile, con impatto maggiore:** compromissione di un cloud di inverter o di un aggregatore. Variazione simultanea di molti MW distribuiti, gestibile dai margini di riserva ma con rischio crescente man mano che aumenta la quota di solare sui tetti (NL, DE).
4. **Poco probabile, ma con impatto alto:** attacco mirato e preparato a lungo (stile Polonia o Ucraina) contro sottostazioni di connessione o sistemi di un grande parco offshore, magari insieme a sabotaggi fisici di cavi nel Baltico.
5. **Rischio di dipendenza, non di attacco:** un produttore extra-UE spegne o blocca i dispositivi da remoto per motivi commerciali o politici (precedente Deye).

## 5. Difese e regole: cosa deve sapere chi lavora in un porto o con un operatore offshore

- **NIS2** (Direttiva 2022/2555): gestione del rischio, notifica degli incidenti entro 24/72 ore, responsabilità dei vertici, sicurezza dei fornitori. Copre energia e porti. Nei Paesi Bassi la **Cyberbeveiligingswet** è in vigore dal **15-08-2026**, insieme alla legge sulle entità critiche (CER). In Danimarca la legge NIS2 è in vigore dal luglio 2025 (data da verificare).
- **Cyber Resilience Act** (Reg. 2024/2847): in vigore da dicembre 2024. Dall'11-09-2026 obbliga i produttori a segnalare le vulnerabilità sfruttate; piena applicazione dall'11-12-2027. Vieta in pratica i prodotti con password deboli predefinite e senza aggiornamenti. Riguarda proprio controller e inverter.
- **Network Code on Cybersecurity** per l'elettricità (Reg. delegato 2024/1366, in vigore dal 13-06-2024): valutazioni del rischio coordinate da ENTSO-E, EU DSO Entity e ACER per i flussi transfrontalieri, e controlli minimi per le entità ad alto impatto.
- **Fornitori ad alto rischio:**
  - **Lituania** (12-11-2024): niente accesso remoto da Paesi a rischio per impianti oltre 100 kW (più di 1.000 impianti interessati). Dal 2026 sono previsti audit e il gestore di rete può disconnettere gli impianti non conformi.
  - **Commissione UE**: niente fondi UE per progetti con inverter di fornitori ad alto rischio (aprile 2026). Proposta di revisione del Cybersecurity Act (gennaio 2026).
  - **Direttiva apparecchiature radio**: requisiti di sicurezza obbligatori dal 1-08-2025.
- **Lato mare:** IMO MSC.428(98) e regole IACS E26/E27 per le navi di servizio che si collegano ai parchi.

**Buone pratiche da citare a un colloquio:**
- togliere i pannelli di controllo da Internet;
- accesso remoto dei fornitori solo da punti controllati, con autenticazione forte, a tempo e registrato;
- segmentare IT, OT e reti dei fornitori (IEC 62443);
- monitorare la rete OT per notare comandi anomali, per esempio molti dispositivi cambiati di notte;
- tenere l'inventario degli apparati a fine vita;
- mettere clausole contrattuali sulla sicurezza dei fornitori;
- esercitarsi a gestire l'impianto in manuale;
- partecipare ai CERT settoriali (SektorCERT, Z-CERT/NCSC, CERT Polska).

**In un porto** c'è un'attenzione in più: refrigerazione dei container reefer, gru, varchi e impianti tecnici sono la stessa famiglia di dispositivi colpiti nei supermercati.

## 6. Indicatori da seguire

- Le sanzioni UE all'Iran per i frigoriferi. Il collegamento, o il mancato collegamento, tra l'IRGC e l'ondata di novembre in BE/NL/EE.
- Nuovi rapporti di CERT Polska e ANSSI e avvisi congiunti CISA/NCSC.
- L'elenco UE dei fornitori ad alto rischio (revisione del Cybersecurity Act) e le esenzioni per gli inverter già installati.
- La prima applicazione della Cyberbeveiligingswet e le ispezioni dell'RDI sugli inverter.
- Gli incidenti presso produttori e manutentori di turbine.
- Eventi di frequenza anomali segnalati da ENTSO-E.
- I livelli di minaccia danesi.

## Note per il coordinatore

- **Fonti provate:**
  - ricerche web per tutte le voci;
  - PDF delle statistiche WindEurope 2025 (copia su rinnovabili.it): **funziona**, tabella 1 usata;
  - WebFetch diretto su cybersecurity360.it, businesstoday.in, aljazeera.com e bbc.co.uk: **non funziona** (host non consentiti nella sessione);
  - windeurope.org: risponde 503.
  
  L'attribuzione all'IRGC (9-11-2026) è stata verificata solo sui titoli e sommari in `docs/data/notizie.json` (Reuters via Al-Monitor, AP, BBC, Al Jazeera): il budget di ricerche web era esaurito.
- **Licenze:** solo fatti con citazione. Nessun dato soggetto a licenze restrittive.
- **File prodotti:**
  - `docs/data/cyber-energia.json` contiene: 20 incidenti come punti (lat/lon stimati, con `precisione_km`); 10 concentrazioni offshore (`tipo: concentrazione_offshore`); `candidati_frigoriferi`; `allarmi_agenzie`; `esposizione` (paesi, produttori, tecnologie, studi); `regole`; `buone_pratiche`.
  - `raccolta/cyber/raccogli.py` valida le voci di `raccolta/cyber/incidenti.json`: campi, date, ISO, coordinate, categorie, link. Rifiuta indirizzi IP, credenziali, CVE e riferimenti a motori di scansione. Se trova `docs/data/offshore-nord.json` (oggi assente) ne riassume i MW per paese senza modificarlo.
- **Collegamenti con la mappa:** cavi e incidenti nel Baltico (`cavi-incidenti.json`), rete elettrica e interconnessioni, Iran e Hormuz (lo stesso IRGC attacca petroliere), Ucraina (attacchi alla rete), notizie.
- **Proposta di visualizzazione:** punti colorati per categoria, con cerchio di raggio `precisione_km`. Le concentrazioni offshore come cerchi grigi proporzionali ai MW, senza etichetta di rischio. Pannello laterale con le tabelle per paese e la timeline 2015-2026.
- **Limiti:**
  - alcune date esatte (BSI, acquedotto danese, entrata in vigore NIS2 in Danimarca) sono da verificare;
  - le capacità offshore sono arrotondate;
  - la quota di inverter cinesi esiste solo per la Germania;
  - il solare manca per BE, GB e i Paesi nordici;
  - l'attribuzione all'IRGC è una dichiarazione governativa senza prove tecniche pubbliche nelle fonti lette.
