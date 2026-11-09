# Agente NOTIZIE PER ARGOMENTO (testate): rapporto

Data: 2026-11-09. Script: `raccolta/notizie/testate.py` (solo libreria standard, nessuna chiave, circa 10 secondi). Elenco feed: `raccolta/notizie/testate.json` (93 feed, 57 testate). Argomenti e parole chiave: `raccolta/notizie/argomenti.json`. Produce `docs/data/notizie-testate.json` (circa 950 KB). Pagina: `docs/notizie.html`. Eseguito davvero due volte il 2026-11-09 (ultimo giro intorno alle 20:05 UTC): **93 feed su 93 ok, 1.049 articoli negli ultimi 3 giorni, 40 storie riprese da più testate, 0 errori**.

Il raccoglitore OSINT (`raccogli.py`, `fonti.json`, `notizie.json`) non è stato toccato: la pagina legge `notizie.json` solo per il riquadro «Fonti specialistiche OSINT».

## 1. Cosa fa
- **Raccolta.** Legge 93 feed RSS, Atom o RDF. Per 15 testate che bloccano i feed o non ne hanno usa una ricerca Google News RSS `site:dominio`: il titolo arriva lo stesso, e il link passa da news.google.com prima di portare all'articolo originale.
- **Normalizzazione.** Per ogni articolo tiene titolo, data UTC, link, testata e sezione, lingua, paese, tipo, paywall e affidabilità, più l'immagine se il feed la dà (480 articoli su 1.049 ce l'hanno). Il sommario viene dal feed ed è lungo al massimo 300 caratteri. **Non copia mai il testo degli articoli.** Per Financial Times e Bloomberg tiene solo il titolo, e lo stesso vale per le testate lette da Google News.
- **Deduplica.** Due voci sono lo stesso articolo se hanno lo stesso link canonico (senza `utm_` e parametri simili) o lo stesso titolo nella stessa testata. Così un articolo che compare in due sezioni, per esempio NYT World e NYT Business, si conta una volta sola.
- **Argomenti.** 12 argomenti, con circa 850 parole chiave in inglese, italiano, danese/norvegese e olandese. Una parola con almeno una maiuscola, come una sigla, si confronta in modo esatto; una parola che finisce con `*` vale come prefisso. Un argomento si assegna se c'è almeno una parola nel titolo, o almeno due nel sommario. Un articolo può avere più argomenti. Le testate di settore e le sezioni dedicate hanno un argomento predefinito, usato solo quando nessuna parola chiave classifica l'articolo (per esempio offshoreWIND.biz → eolico, ANSA Politica → Italia).
- **Storie.** Raggruppa i titoli simili. La somiglianza tra due titoli si misura sulle parole in comune, pesate per rarità (idf), con soglia 0,30 e almeno 2 parole in comune. I due titoli devono essere nella stessa lingua e usciti entro 48 ore. La soglia è stata provata tra 0,28 e 0,42: a 0,30 i gruppi restano puliti e si frammentano meno.
- **Rilevanza per argomento.** È la somma di quattro parti:
  - affidabilità della testata (alta 3, media 2);
  - 2 punti per ogni altra testata che riporta la stessa storia (al massimo 12);
  - parole chiave: 1,5 punti per ognuna nel titolo (al massimo 3 parole) e 0,5 per ognuna nel sommario (al massimo 2);
  - freschezza: 2 punti sotto le 12 ore, 1 sotto le 24.
  Le testate di settore e di analisi hanno 0,5 punti in più.
- **Finestra di 3 giorni.** A ogni giro lo script unisce il file precedente: gli articoli usciti dal feed restano finché hanno meno di 72 ore. Al secondo giro ne ha recuperati 10.

## 2. Fonti provate
Legenda: «letti / tenuti» = voci lette dal feed / articoli tenuti, cioè degli ultimi 3 giorni e con almeno un argomento. Paywall: **no**, **parziale** (alcuni articoli o un limite al mese), **sì**.

| Testata | Sezione | Lingua · paese | Tipo | Accesso | Paywall | Letti / tenuti |
|---|---|---|---|---|---|---|
| NBC News | Top | en · US | generalista | RSS diretto | no | 25 / 2 |
| NBC News | World | en · US | generalista | RSS diretto | no | 25 / 1 |
| ABC News | International | en · US | generalista | RSS diretto | no | 25 / 6 |
| CBS News | World | en · US | generalista | RSS diretto | no | 30 / 9 |
| CBS News | MoneyWatch | en · US | economia | RSS diretto | no | 30 / 5 |
| CNN | via Google News | en · US | generalista | Google News `site:` | no | 100 / 24 |
| NPR | via Google News | en · US | generalista | Google News `site:` | no | 100 / 11 |
| AP News | via Google News | en · US | generalista | Google News `site:` | no | 100 / 28 |
| New York Times | World | en · US | generalista | RSS diretto | sì | 54 / 13 |
| New York Times | Business | en · US | economia | RSS diretto | sì | 48 / 15 |
| New York Times | Technology | en · US | economia | RSS diretto | sì | 25 / 4 |
| New York Times | Climate | en · US | generalista | RSS diretto | sì | 34 / 0 |
| Washington Post | World | en · US | generalista | RSS diretto | sì | 14 / 8 |
| Washington Post | Business | en · US | economia | RSS diretto | sì | 13 / 6 |
| Politico | Defense | en · US | generalista | RSS diretto | parziale | 30 / 0 |
| Politico | Energy | en · US | generalista | RSS diretto | parziale | 30 / 1 |
| Axios | Tutte | en · US | generalista | RSS diretto | no | 100 / 11 |
| BBC News | World | en · GB | generalista | RSS diretto | no | 24 / 8 |
| BBC News | Business | en · GB | economia | RSS diretto | no | 53 / 4 |
| BBC News | Technology | en · GB | generalista | RSS diretto | no | 21 / 0 |
| The Guardian | World | en · GB | generalista | RSS diretto | no | 45 / 12 |
| The Guardian | Business | en · GB | economia | RSS diretto | no | 20 / 2 |
| The Guardian | Energy | en · GB | generalista | RSS diretto | no | 20 / 10 |
| The Guardian | Shipping | en · GB | economia | RSS diretto | no | 20 / 0 |
| Financial Times | World | en · GB | economia | RSS diretto | sì | 25 / 16 |
| Financial Times | Energy | en · GB | economia | RSS diretto | sì | 25 / 4 |
| Financial Times | Home | en · GB | economia | RSS diretto | sì | 12 / 0 |
| Reuters | via Google News | en · GB | generalista | Google News `site:` | parziale | 100 / 60 |
| Euronews | News | en · EU | generalista | RSS diretto | no | 50 / 21 |
| Politico Europe | Tutte | en · EU | generalista | RSS diretto | parziale | 10 / 6 |
| Deutsche Welle | Tutte | en · DE | generalista | RSS diretto | no | 100 / 13 |
| Deutsche Welle | Business | en · DE | economia | RSS diretto | no | 20 / 0 |
| France 24 | Tutte | en · FR | generalista | RSS diretto | no | 24 / 10 |
| France 24 | Business/Tech | en · FR | economia | RSS diretto | no | 30 / 1 |
| Le Monde (in English) | International | en · FR | generalista | RSS diretto | parziale | 20 / 10 |
| Le Monde (in English) | Prima pagina | en · FR | generalista | RSS diretto | parziale | 14 / 0 |
| DR | Alle nyheder | da · DK | generalista | RSS diretto | no | 20 / 5 |
| DR | Udland | da · DK | generalista | RSS diretto | no | 20 / 7 |
| DR | Penge | da · DK | economia | RSS diretto | no | 20 / 2 |
| NOS | Algemeen | nl · NL | generalista | RSS diretto | no | 20 / 6 |
| NOS | Economie | nl · NL | economia | RSS diretto | no | 20 / 4 |
| NOS | Buitenland | nl · NL | generalista | RSS diretto | no | 20 / 0 |
| NL Times | News | en · NL | generalista | RSS diretto | no | 10 / 3 |
| NRK | Toppsaker | no · NO | generalista | RSS diretto | no | 99 / 5 |
| Yle News | News (in English) | en · FI | generalista | RSS diretto | no | 20 / 1 |
| ERR News | News (in English) | en · EE | generalista | RSS diretto | no | 50 / 9 |
| LSM | News (in English) | en · LV | generalista | RSS diretto | no | 50 / 1 |
| LRT | News in English | en · LT | generalista | RSS diretto | no | 100 / 3 |
| ANSA | Prima pagina | it · IT | generalista | RSS diretto | no | 28 / 8 |
| ANSA | Economia | it · IT | economia | RSS diretto | no | 56 / 55 |
| ANSA | Mondo | it · IT | generalista | RSS diretto | no | 45 / 23 |
| ANSA | Politica | it · IT | generalista | RSS diretto | no | 15 / 14 |
| ANSA English | News | en · IT | generalista | RSS diretto | no | 100 / 38 |
| Il Sole 24 Ore | Economia | it · IT | economia | RSS diretto | parziale | 12 / 12 |
| Il Sole 24 Ore | Mondo | it · IT | economia | RSS diretto | parziale | 10 / 4 |
| Il Sole 24 Ore | Italia | it · IT | economia | RSS diretto | parziale | 12 / 12 |
| Il Sole 24 Ore | Finanza | it · IT | economia | RSS diretto | parziale | 9 / 5 |
| Corriere della Sera | Esteri | it · IT | generalista | RSS diretto | parziale | 100 / 34 |
| Corriere della Sera | Economia | it · IT | economia | RSS diretto | parziale | 100 / 83 |
| la Repubblica | Prima pagina | it · IT | generalista | RSS diretto | parziale | 30 / 11 |
| la Repubblica | Esteri | it · IT | generalista | RSS diretto | parziale | 25 / 4 |
| la Repubblica | Economia | it · IT | economia | RSS diretto | parziale | 25 / 22 |
| Rai News | Tutte | it · IT | generalista | RSS diretto | no | 40 / 14 |
| Rai News | Esteri | it · IT | generalista | RSS diretto | no | 41 / 10 |
| Rai News | Economia e finanza | it · IT | economia | RSS diretto | no | 41 / 10 |
| gCaptain | Tutte | en · US | settore | RSS diretto | no | 12 / 12 |
| Splash247 | Tutte | en · SG | settore | RSS diretto | no | 10 / 10 |
| Lloyd's List | via Google News (solo titoli) | en · GB | settore | Google News `site:` | sì | 18 / 16 |
| TradeWinds | via Google News (solo titoli) | en · NO | settore | Google News `site:` | sì | 34 / 34 |
| offshoreWIND.biz | Tutte | en · NL | settore | RSS diretto | no | 50 / 4 |
| Offshore Energy | Tutte | en · NL | settore | RSS diretto | no | 50 / 6 |
| Recharge | via Google News (solo titoli) | en · NO | settore | Google News `site:` | sì | 7 / 7 |
| Hydrogen Insight | via Google News (solo titoli) | en · NO | settore | Google News `site:` | sì | 6 / 5 |
| LNG Prime | Tutte | en · HR | settore | RSS diretto | no | 10 / 8 |
| The Maritime Executive | Articles | en · US | settore | RSS diretto | no | 63 / 32 |
| Port Technology International | via Google News | en · GB | settore | Google News `site:` | no | 20 / 7 |
| JOC (Journal of Commerce) | Tutte | en · US | settore | RSS diretto | sì | 40 / 1 |
| The Loadstar | Tutte | en · GB | settore | RSS diretto | parziale | 10 / 10 |
| Seatrade Maritime News | Tutte | en · GB | settore | RSS diretto | no | 50 / 7 |
| Hellenic Shipping News | Tutte | en · GR | settore | RSS diretto | no | 20 / 20 |
| Breaking Defense | Tutte | en · US | settore | RSS diretto | parziale | 15 / 0 |
| Defense News | Tutte | en · US | settore | RSS diretto | no | 10 / 2 |
| The War Zone | Tutte | en · US | settore | RSS diretto | parziale | 30 / 2 |
| Naval News | Tutte | en · FR | settore | RSS diretto | no | 10 / 10 |
| RUSI | Commentary | en · GB | analisi | RSS diretto | no | 20 / 1 |
| IISS | via Google News | en · GB | analisi | Google News `site:` | parziale | 8 / 1 |
| ECFR | via Google News | en · EU | analisi | Google News `site:` | no | 10 / 0 |
| Bruegel | via Google News | en · EU | analisi | Google News `site:` | no | 54 / 1 |
| CNBC | via Google News | en · US | economia | Google News `site:` | parziale | 100 / 61 |
| MarketWatch | Top stories | en · US | economia | RSS diretto | parziale | 10 / 10 |
| Bloomberg | Markets (solo titoli) | en · US | economia | RSS diretto | sì | 20 / 20 |
| Bloomberg | Politics (solo titoli) | en · US | economia | RSS diretto | sì | 20 / 11 |
| Bloomberg | Technology (solo titoli) | en · US | economia | RSS diretto | sì | 20 / 15 |

**Non funzionano direttamente da qui (provati il 2026-11-09), con il ripiego usato:**
- **Bloccati (403):**
  - NPR (`feeds.npr.org`), AP (`apnews.com/hub/*.rss` e rsshub), CNBC (`/id/.../device/rss`): → Google News.
  - Lloyd's List (`/rss`), Port Technology (`/feed/`, Cloudflare), IISS (`/rss`), ECFR (`/feed/`): → Google News.
- **Nessun feed pubblico (404):** TradeWinds, Recharge e Hydrogen Insight (gruppo NHST); RUSI `/rss.xml`. Le prime tre passano da Google News. Per RUSI funziona invece `/rss/latest-commentary.xml`.
- **Non raggiungibili:** CNN (`rss.cnn.com` non si risolve o chiude la connessione) → Google News. Reuters (feed ufficiali chiusi, 401) → Google News.
- **Fermi:**
  - Bruegel `rss.xml`: ultimo post di agosto 2026 → Google News.
  - Corriere `xml2.corriereobjects.it`: fermo al 2024 → si usa `corriere.it/dynamic-feed/rss/section/…`.
- **Indirizzo cambiato:** Rai News `rss/economia` (404) → `rss/economiaefinanza`.
- **Errore occasionale:** Il Sole 24 Ore Finanza ha dato una volta una lettura incompleta; lo script riprova.
- **Lingua:** DR, NOS e NRK non hanno un servizio in inglese, quindi si leggono in danese, olandese e norvegese. Yle (`yle.fi/rss/news`), ERR, LSM e LRT sono i servizi in inglese.

**Affidabilità.** È «alta» per tutte le testate riconosciute. È «media» per NL Times (sito di notizie in inglese, non un servizio pubblico) e per Hellenic Shipping News, che ripubblica testi di terzi.

**Licenze.** Gli articoli appartengono agli editori. Il progetto li usa come segnalazione, con titolo, sommario breve del feed e link, per un uso personale e non commerciale. Le immagini sono quelle dichiarate nei feed: la pagina le carica dal sito dell'editore e non le copia. Il passaggio da Google News è un uso non ufficiale e non garantito.

## 3. Quanti articoli per argomento oggi (giro delle 20:05 UTC del 2026-11-09)
| Argomento | Ultime 24 ore | Ultimi 3 giorni | Storie con 2+ testate |
|---|---|---|---|
| Porti e logistica | 25 | 27 | 0 |
| Shipping e noli | 91 | 113 | 1 |
| Energia offshore ed eolico | 18 | 23 | 2 |
| Gas, GNL e petrolio | 88 | 105 | 6 |
| Idrogeno e transizione nei porti | 25 | 37 | 2 |
| Stretti e sicurezza marittima | 37 | 48 | 5 |
| Russia-Ucraina | 85 | 115 | 8 |
| Medio Oriente e Iran | 119 | 189 | 12 |
| Infrastrutture critiche e cyber | 43 | 47 | 3 |
| Mercati e banche centrali | 135 | 171 | 7 |
| AI e chip | 181 | 206 | 5 |
| Italia | 163 | 212 | 8 |

**Per lingua:** en 697, it 323, da 14, nl 10, no 5. **Per paywall:** no 526, parziale 348, sì 175.

I conteggi dei «3 giorni» sono quasi uguali a quelli delle 24 ore perché questo è il primo giorno: molti feed tengono solo le ultime 10–50 voci. Con i giri quotidiani successivi la finestra si riempie. È lunedì, e le testate di settore hanno pubblicato poco nel fine settimana: offshoreWIND.biz ha solo 4 articoli negli ultimi 3 giorni su 50 voci nel feed.

**Storie più riprese oggi** (fatti come li riportano le testate, da verificare):
1. L'indagine di Nvidia sul CEO Jensen Huang e una presunta spia cinese: **17 testate**, tra cui AP, BBC, Bloomberg, FT, NYT e Reuters. Argomenti AI e chip, Mercati.
2. La Francia attribuisce all'Iran (Guardie rivoluzionarie) gli attacchi informatici ai frigoriferi dei supermercati: **12 testate**. Argomenti Medio Oriente e Iran, Infrastrutture e cyber.
3. Israele: Gadi Eisenkot incaricato di formare il governo: **9 testate**.
4. Ecofin: via libera alla flessibilità per energia e difesa per l'Italia: **5 testate italiane**.
5. Missili sull'Arabia Saudita, danneggiato un edificio Aramco a Riad: **4 testate**. Argomenti Medio Oriente, Gas e petrolio, Stretti.

## 4. La pagina `docs/notizie.html`
- **Bottoni degli argomenti** con il numero di articoli delle ultime 24 ore. L'argomento scelto finisce nell'URL (`notizie.html#porti`, `#shipping`, `#offshore`, `#gas_petrolio`, `#idrogeno`, `#stretti`, `#russia_ucraina`, `#medio_oriente`, `#infrastrutture`, `#mercati`, `#ai_chip`, `#italia`). C'è anche un bottone «Copia link».
- **«Le 5 storie del giorno»** (ultime 36 ore): prima i gruppi con più testate, con il nome di ogni testata e il link al suo articolo. Se non bastano, la lista si completa con i singoli articoli più rilevanti, segnati «una testata». Oggi «Porti e logistica» non ha storie con più testate.
- **Elenco degli articoli** per giorno e ora. Ogni articolo mostra testata, sezione, lingua, paywall, «via GN», sommario di 2 righe, miniatura e «anche su altre N testate». Si vedono 60 articoli alla volta, con «Mostra altri».
- **Filtri:** lingua (tutte, it, en, da, nl, no) e «Solo senza paywall». Si applicano anche alle 5 storie.
- **Riquadro «Fonti specialistiche OSINT»:** le notizie di `notizie.json` degli ultimi 3 giorni che toccano lo stesso argomento, trovate con le stesse parole chiave più i temi OSINT equivalenti (`temi_osint` in argomenti.json). Mostra le 12 più rilevanti, una per gruppo.
- **Comportamento:** tutti i link si aprono in una nuova scheda (`rel="noopener noreferrer"`). In alto ci sono i link «Torna alla mappa» (index.html) e «Report» (report/).
- **Stile:** IBM Plex, accento #A61E6B, inchiostro #1D272D, carta #F6F5F0, tema scuro automatico.
- **Su telefono** i bottoni degli argomenti stanno in una striscia di 3 righe che scorre in orizzontale.
- **Verifica con Playwright (chromium):**
  - a 1440×900 e a 390×844, in tema chiaro e scuro, nessun errore JS;
  - nessuno scroll orizzontale (`scrollWidth` = 390);
  - sempre 5 storie per argomento;
  - funzionano link diretto con `#`, cambio di argomento, filtro lingua e filtro paywall.
- `docs/index.html` mostra già il link «Notizie» quando `notizie.html` esiste, e non è stato modificato.

## 5. Limiti
- **Classificazione a parole chiave:**
  - può sbagliare, per esempio un incidente ferroviario in Egitto finisce in «Medio Oriente» e un taglio climatico in «Idrogeno e transizione»;
  - non legge il contesto;
  - le parole in danese e olandese sono quelle essenziali.
- **Raggruppamento solo nella stessa lingua:** la stessa storia su ANSA e su Reuters resta in due gruppi.
- **Google News:**
  - i link passano da news.google.com;
  - le ricerche `site:` restituiscono al massimo 100 titoli, mescolati tra sezioni;
  - per le testate generaliste lette così (CNN, NPR, AP, Reuters, CNBC) contano solo i titoli che toccano un argomento.
- **Paywall:** è un valore per testata, non per singolo articolo. Il Guardian, per esempio, è «no», anche se chiede una donazione.
- **Orari:** la pagina mostra l'ora locale del browser.
- **Quando gira lo script:** va aggiunto al lavoro quotidiano di GitHub Actions accanto a `raccogli.py`, con `python3 raccolta/notizie/testate.py`. Questo spetta al coordinatore.
