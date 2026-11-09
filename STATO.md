# Stato del progetto e passaggio di consegne

> File da leggere per primo in ogni nuova chat o sessione. Si aggiorna a ogni passo importante.
> Ultimo aggiornamento: 2026-11-09, sera.

## In una riga
Osservatorio OSINT di rischio geoeconomico: mappa interattiva (eventi militari, stretti, energia, logistica, mercati) che deve diventare un "terminale" aggiornato ogni giorno da script automatici e da agenti AI programmati. Progetto personale per il CV di Gabriele (gabrielegiuliani04).

## Dove sta cosa
- Repository: https://github.com/gabrielegiuliani04/monitor-geoeconomico (pubblico)
- Sito: https://gabrielegiuliani04.github.io/monitor-geoeconomico/ (GitHub Pages attivo dal 2026-11-09, si aggiorna a ogni push su main)
- Vecchia pagina su claude.ai: https://claude.ai/artifact/V7PncTJkuaCaEtjJtX8XmV (aggiornata da un'altra chat; copiata nel repository il 2026-11-09, versione 1794248917-373a). Da ora il repository è l'unica fonte.
- `docs/` sito e dati · `raccolta/` script e regole degli agenti (`raccolta/AGENTI.md`) · `report/agenti/` rapporti degli agenti · `METODO.md` metodo e fonti

## Fatto
- Mappa copiata nel repository (21 file di dati), README, METODO.
- `raccolta/scarica_mercati.py` → `docs/data/prezzi.json`: 27 serie (indici, titoli AI compresi SK Hynix, Western Digital, Oracle; tassi USA 2/10/30 anni dal Tesoro USA; oro, argento, Brent, WTI, TTF, Henry Hub; EUR/USD). Aggiornamento automatico GitHub Actions alle 21:30 UTC nei giorni feriali (`.github/workflows/aggiorna-mercati.yml`), non ancora visto girare.
- Agente ferrovie: completato e verificato (`docs/data/ferrovie.json`, `report/agenti/ferrovie.md`).

## In corso (agenti lanciati il 2026-11-09)
| Agente | File attesi | Stato |
|---|---|---|
| Energia (GNL, gas Italia) | terminali-gnl.json, gas-italia.json | in corso |
| Cavi sottomarini | cavi.json, cavi-incidenti.json | in corso |
| Scorte nazionali | scorte.json | in corso |
| Dati paesi | paesi.json | in corso |
| Calendario mondiale | calendario.json | in corso |
| Risorse e commercio | commercio.json, minerali.json | in corso |
| Reti elettriche | rete-elettrica.json, interconnessioni.json, nucleare.json | in corso |
| Storico Ucraina | ucraina-storico.json | in corso |
| Flussi, noli, sanzioni | portwatch.json, noli.json, gpr.json, sanzioni-navi.json | in corso |
| Stretti approfonditi | stretti-dettaglio.json | in corso |
| Serbatoi da satellite (fattibilità) | report/agenti/serbatoi.md | in corso |
| Tracciamento navi | navi.json | in corso |

Ogni agente scrive anche `raccolta/<dominio>/raccogli.py` e `report/agenti/<dominio>.md`. Alcuni salvataggi intermedi sono stati caricati come "da verificare".

## Da fare (in ordine)
1. Verificare ogni agente (eseguire lo script, controllare numeri a campione) e caricare.
2. Aggiungere gli script verificati al workflow quotidiano.
3. Aggiungere i nuovi livelli alla mappa (`docs/index.html`): ferrovie, cavi, GNL, rete elettrica, nucleare, scorte, calendario, schede paese, navi, pannello Mercati con le serie di `prezzi.json` (oltre a `mercati.json` delle notizie).
4. Primo report: "Hormuz e Mar Rosso: energia, logistica e mercati" in `report/`.
5. Proporre e, dopo l'ok di Gabriele, attivare la regia automatica: coordinatore quotidiano + agente "Miglioramento" a giorni alterni (militare, OSINT, mercati, finanza) + agenti tematici 1–2 volte a settimana, inizialmente su un ramo da rivedere.
6. Agente analisti: canali in `raccolta/analisti/canali.json` (Bottaioli, Lops, Aldo Qefalia, Marco Lippiello, BNP Paribas). Feed RSS funzionanti (titoli, date, descrizioni). Trascrizioni bloccate da YouTube per gli IP cloud: valutare Remote Control sul computer di Gabriele o i sottotitoli caricati a mano.
6b. Fonti OSINT preferite da Gabriele per Ucraina e militare: Clément Molin, AMK Mapping, "Davide Montingelli" (nome da verificare). Da usare e seguire nella raccolta quotidiana (attacchi, logistica, fronte).
7. Chiavi API gratuite da chiedere quando servono: AISSTREAM_API_KEY, GFW_API_KEY, eventualmente AGSI_API_KEY, EIA_API_KEY.

## Decisioni prese
- Lingua: italiano. Ogni dato con fonte, data, affidabilità. Mai numeri inventati.
- Repository pubblico; taglio di analisi, non tracciamento operativo; nessun consiglio di investimento.
- Prezzi: Tesoro USA per i tassi, Yahoo Finance per il resto (FRED e Stooq rifiutano questo server).

## Note per chi riprende
- Creare repository e attivare Pages sono stati bloccati dai controlli di sicurezza: li fa Gabriele a mano.
- La rete della sessione cloud è aperta; Overpass (OpenStreetMap) risulta bloccato.
