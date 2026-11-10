# Stato del progetto e passaggio di consegne

> File da leggere per primo in ogni nuova chat o sessione. Si aggiorna a ogni passo importante.
> Ultimo aggiornamento: 2026-11-09, sera (fine della prima sessione di lavoro).
> Per riprendere: "leggi STATO.md nel repository gabrielegiuliani04/monitor-geoeconomico e riprendi dal punto 1 di *Da fare*".

## In una riga
Osservatorio OSINT di rischio geoeconomico: mappa interattiva (eventi militari, stretti, energia, logistica, mercati) che deve diventare un "terminale" aggiornato ogni giorno da script automatici e da agenti AI programmati. Idea guida: evento → stretto/infrastruttura → flussi → noli → prezzi → chi è esposto (Italia in evidenza). Progetto personale per il CV di Gabriele (gabrielegiuliani04).

## Dove sta cosa
- Repository: https://github.com/gabrielegiuliani04/monitor-geoeconomico (pubblico)
- Sito: https://gabrielegiuliani04.github.io/monitor-geoeconomico/ (GitHub Pages attivo, si aggiorna a ogni push su main; verificato su desktop e telefono il 2026-11-09)
- Vecchia pagina su claude.ai: https://claude.ai/artifact/V7PncTJkuaCaEtjJtX8XmV — copiata nel repository il 2026-11-09 (versione 1794248917-373a). **Da ora il repository è l'unica fonte**: consigliato a Gabriele di non aggiornare più la vecchia pagina.
- `docs/` sito e dati · `raccolta/<dominio>/raccogli.py` script · `raccolta/AGENTI.md` regole comuni degli agenti · `report/agenti/<dominio>.md` rapporti · `METODO.md` metodo e fonti

## Aggiornamento automatico (GitHub Actions)
- `aggiorna-mercati.yml`: prezzi (`docs/data/prezzi.json`, 27 serie) alle 21:30 UTC lun–ven.
- `aggiorna-dati.yml`: ogni giorno alle 05:15 UTC, e a mano da Actions → Run workflow. Lancia flussi, scorte, navi, calendario, energia, stretti (ogni passo indipendente).
- Segreti inseriti da Gabriele il 2026-11-09: `AISSTREAM_API_KEY`, `GFW_API_KEY`, `AGSI_API_KEY`. **La chiave AGSI è finita per errore in un file pubblico (poi ripulito, ma resta nella cronologia git): va rigenerata.** Ora `raccolta/comune/nascondi_chiavi.py` gira prima di ogni salvataggio. Primo giro (2026-11-09 19:16): tutto verde; aisstream ha dato 19 petroliere negli Stretti danesi, nessun dato per Hormuz/Bab el-Mandeb/Suez/Bosforo (copertura AIS terrestre assente lì); AGSI ha risposto con errore. Facoltativo: `BLS_API_KEY` (data.bls.gov/registrationEngine).
- Non ancora nel workflow (dati statici o lenti): ferrovie, cavi (settimanale da aggiungere), paesi, commercio, elettricità, Ucraina storico.

## Fatto e pubblicato (aggiornato 2026-11-09 sera)
Sito: mappa con apertura su Europa e Medio Oriente (livelli militari spenti), menu Vista, riquadro "Come si usa", barra Report / Notizie / Simulatore / Terminale.
- **Livelli** (blocco "Strati aggiunti" in docs/index.html, funzioni xLoad/xDrawPoints/xBuildLines/renderExtra): ferrovie, cavi, rete elettrica + interconnessioni, nucleare, GNL, gas Italia, navi AIS, attacchi ucraini in Russia, AI nel mondo, investimenti (archi), incidenti cyber, webcam, rischio, basi nel mondo, porti Nord, eolico offshore, sicurezza Baltico, bunker, idrogeno, attacchi russi (in attesa dati). Selettore del periodo per gli eventi datati (XDATED, XR).
- **Terminale** (renderTerminal): Rischio (matrice), Nord Europa, Prezzi e tassi (33 serie + curva), Agenda, Stretti, Noli e rischio, Scorte, Paesi, Notizie, Ucraina (lanci, ondate, fronte in km²), Analisti.
- **Pagine**: docs/report/ (Hormuz e Mar Rosso; Supply chain), docs/notizie.html (57 testate per argomento), docs/simulatore.html, docs/crediti.html.
- **Dati** in docs/data/ con rapporto per ciascuno in report/agenti/*.md.
- **Licenze**: fronte senza poligoni di terzi (solo link ISW/DeepState/Majakovsk73; copie private in raccolta/fronte/privato/, escluse da git); Yahoo solo 3 mesi; Baltic Dry non più automatico. Modulo docs/isw-fronte.js pronto ma NON attivo: serve il consenso scritto dell'ISW.

## Agenti in corso o da riprendere (se la sessione si ferma, rilanciarli con lo stesso compito, dicendo di partire dai file già scritti)
| Agente | Output atteso | Stato |
|---|---|---|
| Revisore report Hormuz | report/revisioni/hormuz-mar-rosso-2026-11.md, report/STANDARD.md, riquadro Revisione nel report | in corso |
| Revisore report supply chain | report/revisioni/supply-chain-2026-11.md | in corso |
| Supply chain AI | docs/data/supply-chain-ai.json, docs/report/supply-chain-ai-2026-11.html | in corso (poi: aggiungere a docs/report/index.html) |
| Italia: impatti (carburanti, scioperi TIR, comportamenti) | docs/data/italia-impatti.json → poi sezione "Cosa succede in Italia" nel simulatore | in corso |
| Attacchi russi in Ucraina geolocalizzati | docs/data/attacchi-russi.json (livello xru già pronto in mappa) | in corso |
| Revisione livelli originali (fissi, italia, iran, difesa, mobili, eventi, ibrido) | report/agenti/originali.md, raccolta/originali/controlla.py | in corso |
| Commercio e minerali | docs/data/commercio.json, minerali.json | in corso da molto: verificare |
| Filiera eolico offshore | docs/data/eolico-filiera.json | FATTO, da mettere in mappa (porti base) |
| Assicurazioni war risk | docs/data/assicurazioni.json (27 aree JWC) | FATTO, da mettere in mappa (aree come poligoni) |

## Da fare (in ordine)
1. Verificare gli agenti mancanti (sopra) e il primo giro di `aggiorna-dati.yml` (Actions).
2. **FATTO in parte (2026-11-09): livelli Ferrovie, Cavi, Rete elettrica, Nucleare, Terminali GNL, Gas Italia, Navi nel pannello "Infrastrutture e flussi"; pannello "Terminale" (Prezzi e tassi con curva, Agenda, Stretti); schede degli stretti con PortWatch e stretti-dettaglio. Codice nel blocco "Strati aggiunti" di index.html. Restano:** scorte, schede paese, commercio, Ucraina storico, interconnessioni, noli/GPR nel Terminale. Prima era: Mostrare i nuovi livelli sulla mappa (`docs/index.html`, ~1.900 righe, canvas + d3; vedi come sono caricati `linee`/`condotte` in `start()` e il manifest `docs/data/manifest.json`): ferrovie, cavi, terminali GNL, gas Italia, rete elettrica, nucleare, navi (petroliere sanzionate in rosso, AIS falsi esclusi), schede stretti con PortWatch e prezzi collegati, pannello Mercati con le serie di `prezzi.json`, calendario, schede paese. Sul telefono ridurre il riquadro scala/fonti in basso a sinistra.
3. Primo report: "Hormuz e Mar Rosso: energia, logistica e mercati" in `report/` (base: report/agenti/stretti.md, flussi.md, energia.md, scorte.md).
4. Proporre a Gabriele e, dopo il suo ok, attivare la regia automatica con sessioni programmate di Claude Code: coordinatore quotidiano + agente "Miglioramento" a giorni alterni (militare, OSINT, mercati, finanza) + agenti tematici 1–2 volte a settimana, all'inizio su un ramo da rivedere. Attenzione al consumo dell'abbonamento.
5. (Tolto su richiesta di Gabriele il 2026-11-10: niente più sezione sugli analisti economici YouTube.)
6. Fonti OSINT preferite da Gabriele per Ucraina e militare: Clément Molin, AMK Mapping, "Davide Montingelli" (nome da verificare).
7. Serbatoi da satellite: decidere se farne un progetto separato in base alla conclusione dello studio.


## Lavori in parallelo (più sessioni di Claude Code sullo stesso repository)
Regole, valide per ogni sessione:
1. **Solo la sessione "Regia" modifica `docs/index.html`, `docs/data/manifest.json`, i workflow in `.github/` e questo file.** Le altre chiedono alla Regia (scrivendo in `STATO.md` → "Richieste per la Regia" con un commit) o lavorano nelle proprie cartelle.
2. Ogni sessione tocca **solo le sue cartelle** (vedi tabella) e fa `git pull --rebase origin main` prima di ogni `git push`.
3. Prima di iniziare: leggere `STATO.md` e `raccolta/AGENTI.md`. Mai numeri inventati, ogni dato con fonte e data.
4. Mai chiavi nei file: si leggono da variabili d'ambiente / segreti GitHub.

| Sessione | Compito | Cartelle sue |
|---|---|---|
| **Regia** (questa) | mappa, terminale, workflow, coordinamento, verifica degli agenti | `docs/index.html`, `docs/data/manifest.json`, `.github/`, `STATO.md` |
| **Report** | report settimanale geoeconomico + approfondimenti, pagina dei report | `report/` (esclusa `report/agenti/`), `docs/report/` |
| **Raccolta** | nuovi domini di dati e manutenzione degli script (es. minerali, sanzioni UE dettagliate, satelliti) | `raccolta/<dominio>/`, `docs/data/<file nuovi>.json`, `report/agenti/<dominio>.md` |
| **Vetrina CV** | README, pagina "Chi sono / Metodo" sul sito, post LinkedIn, sezione CV, presentazione del progetto | `README.md`, `METODO.md`, `docs/progetto/`, `vetrina/` |

## Richieste per la Regia
(le altre sessioni aggiungono qui una riga: data, sessione, richiesta)
- 2026-11-09, Vetrina e licenze: aggiungere nella mappa (riquadro fonti in basso a sinistra o menu) un link "Crediti e licenze" a `crediti.html` (pagina nuova in `docs/`). Rischi di licenza da decidere: `fronte.json` (@Majakovsk73) e `fronte-storico.json` (DeepState) senza permesso; serie Yahoo complete in `prezzi.json`; Baltic Dry da Trading Economics. Dettagli e azioni in `report/licenze.md`.

## Decisioni prese
- Lingua: italiano. Ogni dato con fonte, data, affidabilità. Mai numeri inventati.
- Repository pubblico; taglio di analisi, non tracciamento operativo; nessun consiglio di investimento.
- Prezzi: Tesoro USA per i tassi, Yahoo Finance per il resto (FRED e Stooq rifiutano il server cloud).
- Licenze non commerciali presenti (TeleGeography CC BY-NC-SA, OpenSanctions e GFW CC BY-NC): ok perché il progetto è personale.
- L'email di Gabriele non va usata negli User-Agent senza il suo permesso.

## Note per chi riprende
- Creare repository e attivare Pages sono stati bloccati dai controlli di sicurezza: li fa Gabriele a mano.
- Dalla sessione cloud: Overpass (OpenStreetMap), EIA, IEA, UNCTAD, OPEC e alcuni siti di stampa sono bloccati; da GitHub Actions possono funzionare.
- Il push da questa sessione funziona (app Claude installata sul repository).
