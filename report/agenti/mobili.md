# Agente MOBILI (navi militari): schieramenti navali per il livello "Ships"

Rapporto del 10 novembre 2026. Script: `raccolta/mobili/raccogli.py`, solo libreria standard (`urllib`, `json`, `re`, `html`, `math`, `hashlib`). Dati curati: `raccolta/mobili/navi_curate.json`. L'ho eseguito davvero. Ha scritto `docs/data/mobili.json`: **134 elementi, di cui 124 navi** (prima 53 elementi, 43 navi), 210 KB. Il testo dei nuovi elementi è in inglese, come l'interfaccia della mappa; quelli esistenti restano com'erano (in italiano).

## Cosa fa lo script
1. Legge il `docs/data/mobili.json` attuale come base. Gli elementi che non sono navi (9 aerei, 1 batteria Patriot) sono **copiati identici** (verificato byte per byte).
2. Tiene le 43 navi esistenti. Se il tracker USNI è più recente della nave, aggiorna data, fonte e area. Se l'area cambia di oltre 150 km, la posizione vecchia va in `storico[]`. In fondo alle note aggiunge la frase USNI marcata `[USNI data]`, che sostituisce quella della corsa precedente.
3. **USNI Fleet and Marine Tracker automatico**: interroga l'API WordPress di news.usni.org e prende l'ultimo post `usni-news-fleet-and-marine-tracker-*`. Toglie le didascalie delle foto, che nominano navi di altre sezioni. Legge le sezioni `<h2>In the …>` e i numeri di scafo (`USS Nome (DDG-79)`). Area: un'area più specifica nella frase (es. Andaman Sea), altrimenti l'area della nave capofila citata prima, perché USNI disegna la nave capitale; altrimenti il titolo della sezione. Riconosce i porti ("in port in", "returned to", "arrived in"). Gli elenchi "deployed warships in the region include" diventano "sea not specified" con raggio di 1.000 km. Le navi nuove hanno id `NU-<scafo>`.
4. Aggiunge 67 elementi curati (id `NV-…`), ognuno con fonte, link e data. Salta un elemento curato se lo scafo esiste già nel file.
5. Sposta il simbolo (`sim`) solo per i propri elementi che condividono un centro: dentro il cerchio e in mare. Per la verifica del mare usa `docs/data/world.json`.
6. Valida: id unici, campi obbligatori, categorie e sagome note, teatro, date non future, coordinate, link, simbolo dentro il cerchio e in mare. I problemi sono solo avvisi: lo script non si ferma.
7. Scrive lo stesso schema di prima: `{"aggiornato", "schema", "punti"}`, indentazione 1. Ho controllato che sia idempotente: due corse danno lo stesso file.

Se USNI non risponde, lo script registra l'errore, tiene le navi esistenti e scrive comunque gli elementi curati. Con `--secco` fa una prova senza scrivere il file.

## Fonti provate
| Fonte | Esito | Uso |
|---|---|---|
| USNI News, API WordPress (`/wp-json/wp/v2/posts`) | funziona (le pagine HTML danno 403 a curl, l'API no) | tracker settimanale automatico; Western Pacific Pulse, Neptune Strike, Malabar, Royal Navy (articoli curati) |
| EUNAVFOR Atalanta (eunavfor.eu/news) | funziona | ammiraglia Atalanta, rotazione |
| Naval News (sito e feed RSS) | funziona | Primula/Bab el-Mandeb; ma a inizio novembre il feed è quasi solo Euronaval (industria) |
| Zone Militaire/opex360, Euronews, Militarnyi, United24, Global Times, Funeco (Stato maggiore congiunto giapponese), Jiji | funzionano | Aspides, Russia nel Baltico, Mar Nero, Cina, Giappone |
| NATO MARCOM (mc.nato.int) | 403 | composizione degli SNMG presa da USNI (21 ott.) |
| Royal Navy (royalnavy.mod.uk) | 403 | ripresa da USNI |
| operationaspides.eu | 502 dal proxy | nessuna fonte Aspides ufficiale diretta |
| Breaking Defense | 403 | citata solo tramite euperspectives |

Licenze: sono articoli di stampa e comunicati, tutti i diritti riservati. Uso solo fatti brevi (nave, area, data) con link. Nessun testo lungo è copiato, salvo una frase del tracker USNI nella nota di ogni elemento `NU-`. Progetto personale, non commerciale.

## Cosa contiene (navi)
- **Per marina (124 navi):** US 48, CN 19, GB 7, IT 7, RU 7, TR 5, FR 4, JP 4, ES 4, KR 3, DE 3, AU 2, CA 2, NO 1, IN 1, DK 1, PT 1, LT 1, PL 1, FI 1, GR 1, BE 1.
- **Per teatro:** Altri teatri (Indo-Pacifico, Americhe) 54, NATO ed Europa 36, Medio Oriente (Mar Rosso, Golfo di Aden, Mar Arabico, Oceano Indiano occidentale) 29, Italia 4, Russia–Ucraina 1.
- **Per categoria:** nave-scorta 75, nave-portaerei 16, nave-ausiliaria 16, nave-anfibia 14, sottomarino 3.
- **Origine:** 43 esistenti, 14 nuove dal tracker USNI del 9 novembre (Minneapolis-Saint Paul, Oscar Austin, Bulkeley, Paul Ignatius, Stout, Milius, Rafael Peralta, John Finn, Delbert D. Black, Mason, Princeton, Wayne E. Meyer, Miguel Keith, Mustin), 67 curate.
- **Gruppi** (`gruppo`, con `capo` = ammiraglia): SNMG1 (5), SNMG2 (5), SNMCMG1 (3), SNMCMG2 (5), gruppo portaerei italiano (Cavour + 2), gruppo Anadolu turco (3), Malabar 2026 (4), Atalanta (1), 49ª task force cinese di scorta (3), tre gruppi PLAN intorno al Giappone, crociera addestrativa sudcoreana (3).
- **Visibilità sulla mappa oggi** (regole di `index.html`: navi piene entro 7 giorni, sbiadite fino a 30, poi nascoste; portaerei mai nascoste): 57 piene, 64 sbiadite, 2 scadute (ITS Carlo Bergamini al 28 set. e JS Takanami al 2 ott.: non ho trovato fonti più recenti), 1 con affidabilità bassa (USNS Rappahannock, già così). 27 elementi hanno `dubbia: 1` (il punto interrogativo): sono le forze di cui si conosce solo l'area della missione.
- Precisione: porti 3–5 km; stretti e mari stretti 60–300 km; gruppi NATO e missioni 450–1.000 km; elenchi USNI "sea not specified" 1.000 km; Oceano Indiano 2.000 km.

## Fatti attuali (con data e fonte)
1. **Due portaerei USA nel Mar Arabico**: George Washington (CSG 5) e George H.W. Bush (CSG 10). Con loro altri 9 cacciatorpediniere e incrociatori e la base galleggiante Miguel Keith nella regione. La presenza a due portaerei dura da sei mesi a sostegno del blocco dei porti iraniani. Fonti: USNI Fleet Tracker, 9 nov. 2026; USNI, 22 ott. 2026.
2. **Theodore Roosevelt verso il Medio Oriente**: è ripartita da Singapore lunedì 9 novembre e opera nel Mare delle Andamane. Il Boxer ARG (11ª MEU) è nell'Oceano Indiano, vicino al Mar delle Laccadive. Fonte: USNI, 9 nov. 2026.
3. **Hormuz**: a ottobre gli attacchi a navi commerciali sono stati 27, il numero più alto da quando la guerra USA–Iran è iniziata a fine febbraio (dati IMO). La missione franco-britannica di sminamento è ferma senza cessate il fuoco. RFA Lyme Bay è l'unica nave britannica vicina allo stretto. Fonti: USNI, 22 e 12 ott. 2026.
4. **Bab el-Mandeb**: nella notte tra l'1 e il 2 ottobre la FREMM francese Languedoc ha abbattuto con il cannone un drone che si avvicinava alla portacontainer CMA CGM Champs-Élysées. A metà ottobre una nave francese ha intercettato un missile balistico, probabilmente degli Houthi, vicino al cacciamine belga Primula. Fonti: opex360, 16 ott.; Naval News, 27 ott. 2026.
5. **Aspides sottodimensionata**: per Kallas servono "almeno dieci navi". Hanno offerto una nave in più solo Paesi Bassi e Belgio, e la fregata belga Leopold I arriverà solo nel 2027. Italia e Grecia forniscono le tre navi principali. Fonte: Euronews, 12 ott. 2026.
6. **Atalanta**: dal 10 ottobre l'ammiraglia è la fregata spagnola Santa María, con un comandante portoghese (54ª rotazione). Il 3 novembre era ormeggiata a Gibuti. Dall'aprile 2026 la pirateria somala conta sette casi. Fonti: EUNAVFOR, 10 ott., 3 nov. 2026 e comunicato su MV Glamor.
7. **Scorte russe dal Baltico**: la corvetta Stoykiy (545) ha scortato due convogli russi di cargo verso l'Atlantico (1 e 7–8 novembre), seguita dalla danese HDMS Rota nel Kattegat. Il carico sospetto sono mezzi militari imbarcati a Baltiysk. Fonte: Militarnyi, 9 nov. 2026 (OSINT e Sentinel-1). Dal 1° al 14 ottobre HMS Dauntless e HMS Tyne hanno seguito la fregata Neustrashimy, che scortava cargo sanzionati nella Manica. Fonte: USNI, 3 nov. 2026.
8. **Cina**: la 48ª task force di scorta nel Golfo di Aden è rientrata a Qingdao il 23 ottobre dopo 378 giorni, un record, con 423 navi scortate. È subentrata la 49ª (Kunming, Yueyang, Luomahu). Intorno al Giappone si contano almeno cinque gruppi PLAN tra il 27 ottobre e il 4 novembre, di cui uno insieme a una nave della guardia costiera, per la prima volta annunciato da Tokyo. Fonti: Global Times, 25 ott.; USNI, 30 ott. e 6 nov. 2026.
9. Il Mar Nero non è più un bacino da cui partire: la Flotta del Mar Nero è ferma a Novorossiysk da cinque mesi, secondo la Marina ucraina (26 ott., affermazione non verificata). Tra luglio e inizio settembre nel Mediterraneo non c'era nessuna nave da guerra russa (funzionario NATO via euperspectives, 29 ott. 2026).

## Collegamenti con gli altri livelli
- **Stretti** (`stretti.json`, `stretti-dettaglio.json`): Bab el-Mandeb (Languedoc, Primula, Aspides), Hormuz e Golfo di Oman (gruppi USA, Lyme Bay), Golfo di Aden (Atalanta, Cina, Giappone), Malacca (Roosevelt, Charleston), stretti danesi (Stoykiy, Rota), Manica (Neustrashimy, Shabalin), Miyako, Osumi e La Pérouse (PLAN e Russia).
- **Navi mercantili AIS** (`navi.json`, `sanzioni-navi.json`): i convogli russi scortati e la flotta ombra. `navi.json` contiene anche `militari_usni` (36 navi USA) da un altro agente: è un doppione delle navi USA di questo file. Non l'ho toccato.
- **Eventi e assicurazioni**: attacchi a Hormuz e Bab el-Mandeb, aree elencate dal JWC.
- **Mercati e noli**: le scorte che mancano nel Mar Rosso tengono alti i premi e allungano le rotte via Capo di Buona Speranza.
- **Italia**: gruppo portaerei Cavour, FREMM Bergamini (Aspides), Martinengo (SNMG2), cacciamine Numana (SNMCMG2), cacciamine per Hormuz in rotazione.

## Proposta per la mappa
Le categorie e le sagome esistenti (`nave-portaerei`, `nave-scorta`, `nave-anfibia`, `nave-ausiliaria`, `sottomarino`) bastano. `gruppo` e `capo` legano già le navi alla loro ammiraglia. Un filtro per "missione" (SNMG, Aspides, Atalanta…) potrebbe usare il prefisso di `gruppo`. Le navi con `dubbia` mostrano già il "?". Non ho modificato `index.html`.

## Passo da aggiungere al workflow
Il tracker esce il lunedì. Il job settimanale gira la domenica alle 03:40 UTC: troverebbe il tracker di 6 giorni prima. Meglio il job quotidiano (`.github/workflows/aggiorna-dati.yml`), perché costa una sola richiesta HTTP:
```yaml
      - name: Naval deployments (USNI tracker + curated)
        continue-on-error: true
        run: python3 raccolta/mobili/raccogli.py
```
Il passo va messo **prima** di qualunque passo che legga `mobili.json`. Se resta settimanale, conviene un cron il martedì, per esempio `"40 5 * * 2"`. Gli elementi curati non si aggiornano da soli: vanno rivisti a mano in `navi_curate.json` (circa ogni settimana).

## Limiti
- **Nessuna posizione precisa** tranne i porti: i cerchi sono aree dichiarate dalle fonti, non rilevamenti. Le navi militari spengono l'AIS.
- **Aggiornamento automatico solo per gli USA** (USNI). Tutto il resto è curato a mano e invecchia: dopo 30 giorni le navi spariscono dalla mappa.
- **SNMG1, SNMG2, SNMCMG1, SNMCMG2**: composizione al 21 ottobre (Neptune Strike, finita il 5 novembre). MARCOM non è raggiungibile (403). La tabella di Wikipedia per SNMG1 (Van Amstel, Johan de Witt) non è verificata e non l'ho usata.
- **Mancano (nessuna fonte datata e localizzabile trovata)**: le navi indiane dell'operazione Sankalp a Hormuz e Bab el-Mandeb (ultimo dato: 3 navi, agosto); la fregata greca di Aspides; la fregata olandese Evertsen (partita il 27 settembre per il Medio Oriente, nessuna posizione); i cacciamine italiani che sostituiscono Crotone e Rimini; Prosperity Guardian e CTF-153 (il sito CMF indica il comando italiano, ma non c'è una data); navi russe nel Mediterraneo dopo settembre; navi saudite; navi dell'Iran.
- La 49ª task force cinese e JS Takanami sono messe sull'area della missione, con `dubbia`. JS Kirisame è nell'ultima posizione nota (Mar Cinese Meridionale, 23 ottobre), mentre è in viaggio verso Aden.
- Alcune navi esistenti (Comstock, Portland, Chosin, Decatur, Paul Hamilton, Anchorage, Murtha) hanno un `sim` a 650–1.000 km dal centro, fuori dal cerchio. Lo script lo segnala ma non lo cambia: non sono elementi miei.
- Doppioni possibili con `docs/data/aerei.json` (altro agente) se anche quello contiene gli stessi aerei: `index.html` carica entrambi i file. Come richiesto, qui gli aerei restano copiati identici.
- La classificazione per scafo dei nuovi elementi USNI (classe, sagoma) è automatica: le classi delle navi ausiliarie sono generiche.
