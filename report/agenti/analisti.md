# Analisti su YouTube: rapporto dell'agente (9 novembre 2026)

File prodotto: `docs/data/analisti.json` (75 video, 5 canali, circa 200 kB).
Script: `raccolta/analisti/raccogli.py` (solo libreria standard, `xml.etree`). Dizionario dei temi e degli asset: `raccolta/analisti/temi.json` (20 temi, 49 titoli o asset con i loro alias).
Lo script l'ho eseguito davvero il 9/11/2026 alle 19:35 UTC. Non ha dato errori.

In questo testo **fatto** vuol dire un dato con fonte e data: un titolo pubblicato, un prezzo. **Valutazione** vuol dire una lettura dell'osservatorio. I video sono **opinioni dei loro autori**. Per questo ogni video ha `affidabilita: "bassa"`.

---

## 1. Fonti provate

| Fonte | Esito | Note |
|---|---|---|
| Feed RSS di YouTube `https://www.youtube.com/feeds/videos.xml?channel_id=<id>` | **funziona**, senza chiave | Dà gli ultimi 15 video del canale: titolo, data di pubblicazione, link, miniatura, descrizione completa, visualizzazioni (`media:statistics`) e voti (`media:starRating`). |
| Durata del video | **non c'è nel feed** | Ne ricavo un limite inferiore dall'ultimo capitolo scritto nella descrizione (`durata_almeno_s`): c'è in 9 video. Gli *short* (link `/shorts/`) durano al massimo 3 minuti. La pagina del video non si può leggere senza superare il consenso dei cookie, quindi l'ho lasciata stare. |
| Trascrizioni (youtube-transcript-api, timedtext) | **bloccate** per gli indirizzi cloud | Non ho insistito. La proposta per aggirare il blocco è al §6. |

**Licenze.** I contenuti appartengono agli autori (tutti i diritti riservati). Il file salva solo questi dati:
- titolo;
- descrizione ripulita e tagliata a 600 caratteri;
- titoli dei capitoli;
- link e miniatura (è l'URL di `i.ytimg.com`: l'immagine non viene copiata).

Ogni video riporta canale e link. Il parlato non viene riprodotto.

## 2. Cosa fa lo script

1. **Legge i 5 canali** di `canali.json`: Stefano Bottaioli, Vito Lops, Aldo Qefalia, Marco Lippiello e Investimenti BNP Paribas. Per ogni canale prende 15 video.
2. **Pulisce le descrizioni.** Toglie le righe che tornano in almeno 3 video dello stesso canale: firme, link promozionali, liste di libri, hashtag fissi. Toglie anche le avvertenze legali, le affiliazioni, i social e gli URL. Così, per esempio, l'hashtag fisso `#Oro #Argento` di BNP non fa contare l'oro in ogni puntata.
3. **Riconosce temi e asset** con parole chiave in italiano e in inglese, a parola intera. Regole del dizionario:
   - `=AI` cerca maiuscole e minuscole esatte, così non prende la preposizione «ai»;
   - `semicondutt*` è un prefisso;
   - `escludi` toglie frasi fuorvianti, come «oro nero» o «Wall Street Italia».

   Per ogni video salva il tema, dove l'ha trovato (titolo o descrizione) e la parola che l'ha fatto scattare, così si può controllare.
4. **Conta per settimana**, con finestre mobili di 7 giorni in ora di Roma: questa settimana va dal 3 al 9/11, la precedente dal 27/10 al 2/11. Il conto si fa in totale e per canale, con la **quota**: la parte dei video con almeno un tema riconosciuto.
5. **Trova i temi in crescita o in calo** confrontando solo i canali che coprono tutte e due le settimane (vedi i limiti).
6. **Collega i temi ai prezzi.** Per ogni tema elenca le serie di `docs/data/prezzi.json` collegate, con la variazione a 1 settimana e a 1 mese calcolata dalla serie (in punti base per i tassi). Aggiunge anche una riga pronta per il terminale, per esempio:
   `Bolla AI / titoli AI: 6 video in 7 giorni (2 nei 7 prima) · Nvidia −12,7% in 1 settimana, −23,1% in 1 mese; Semiconduttori (SOX) −3,3% in 1 settimana, −20,5% in 1 mese; Nasdaq 100 −0,5% in 1 settimana, −9,8% in 1 mese`
7. **Tiene un archivio.** Rilegge l'uscita precedente e conserva i video degli ultimi 70 giorni. Così, girando ogni giorno, il confronto tra settimane non dipende più dal limite dei 15 video del feed.
8. **Prevede le trascrizioni.** Se esiste `raccolta/analisti/trascrizioni/<video_id>.json`, ne usa il testo per riconoscere i temi e pubblica solo il campo `riassunto` (vedi il §6).

## 3. Cosa contiene `analisti.json`

- **Le chiavi comuni:** `aggiornato`, `fonti` (un feed per canale, più prezzi.json), `nota` ed `errori`.
- **`elementi`:** un elemento per video. Ogni video ha questi campi:
  - `canale`, `titolo`, `data`, `pubblicato`, `link`, `tipo` (video o short), `miniatura`;
  - `descrizione` (al massimo 600 caratteri) e `capitoli`;
  - `durata_s` (sempre null), `durata_almeno_s` e `durata_nota`;
  - `visualizzazioni` (con l'ora della lettura) e `voti`;
  - `programmato`: con 0 visualizzazioni è di solito una diretta annunciata;
  - `temi[]` e `asset[]`, ognuno con `dove` e `parola`;
  - `fonte`, `data_fonte`, `affidabilita` e `note`.
- **`canali`:** quanti video ha dato il feed, da che data a che data, e se il canale copre anche la settimana precedente.
- **`temi_settimana`:**
  - le due finestre;
  - `totale` (video, video con il tema nel titolo, video nella settimana prima, canali, quota, e fino a 3 esempi con titolo, canale e link);
  - `in_crescita`, `in_calo`, `per_canale`;
  - `asset`: i titoli citati, con la variazione del prezzo quando la serie esiste.
- **`collegamenti_prezzi`:** per ognuno dei 20 temi, le serie collegate (ultimo valore, data, `var_1s`, `var_1m`, date di base, fonte), le `serie_mancanti` e la `riga` di testo.

## 4. I temi di questa settimana (3–9 novembre 2026)

Questa settimana ci sono 24 video. In 13 il dizionario riconosce almeno un tema. Gli altri 11 sono quasi tutti promozioni o dirette annunciate di BNP, e le «Quick Note» di Bottaioli, che non hanno testo (vedi i limiti). I fatti sono i titoli dei video. I numeri dei prezzi vengono da `prezzi.json`, letto il 9/11.

1. **Elezioni USA (midterm): 8 video da 4 canali**, contro 1 la settimana prima. È l'unico tema «in crescita» nel confronto omogeneo: 5 video contro 1, quota dal 17% al 71%.
   - «Midterm Usa: la vittoria Dem e i riflessi su Piazza Affari», Investimenti BNP Paribas, 9/11 ([link](https://www.youtube.com/watch?v=tdar-pQ_Ikg))
   - «MIDTERM USA: ARRIVA L'ONDA BLU SUI MERCATI? IL PORTAFOGLIO DA STALLO», Vito Lops, 4/11 ([link](https://www.youtube.com/watch?v=7oh-xKWs9Bw))
   - «BITCOIN e Elezioni USA: ora arriva il vero RALLY?», Aldo Qefalia, 4/11 ([link](https://www.youtube.com/watch?v=oY7TfGkdMQA))

   Prezzi: S&P 500 +0,1% in 1 settimana e −3,4% in 1 mese; Treasury a 10 anni −8 pb in 1 settimana.
2. **Bolla AI e titoli AI: 6 video da 3 canali** (2 la settimana prima). Nvidia è l'asset più citato (4 video).
   - «Bolla AI, come capire se sta per scoppiare? Ecco il mio indicatore AI 40», Vito Lops, 9/11 ([link](https://www.youtube.com/watch?v=mpqhe2DyHk0))
   - «CROLLO NASDAQ: È FINITA LA FESTA DELL'AI? Il Caso Anthropic», Marco Lippiello, 8/11 ([link](https://www.youtube.com/watch?v=D6BErqgZxDA))
   - «L'Affair Jensen, le tensioni in Medio-Oriente, recupero a V o Inizio correzione?», Investimenti BNP Paribas, 9/11 ([link](https://www.youtube.com/watch?v=mRmHkmsFqsY))

   Prezzi: Nvidia −12,7% in 1 settimana e −23,1% in 1 mese; SOX −20,5% in 1 mese; SK Hynix −20,2% in 1 settimana.
3. **Crollo, correzione e volatilità: 6 video da 4 canali.**
   - «CROLLO DEI MERCATI.... (Wall Street è in panico.....)», Aldo Qefalia, 6/11 ([link](https://www.youtube.com/watch?v=JG0jeEoH9PM))
   - «Peggior selloff tech dal Covid, liquidazione posizioni in leva?», Investimenti BNP Paribas, 6/11 ([link](https://www.youtube.com/watch?v=h751EGFdKDw))
4. **Wall Street, Nasdaq e S&P 500: 5 video da 4 canali.**
   - «LA SETTIMANA PIÙ FOLLE DI WALL STREET: CHI HA PAGATO IL CONTO?», Vito Lops, 7/11 ([link](https://www.youtube.com/watch?v=-EEcbrdJG-E)): 33.317 visualizzazioni, il video più visto della settimana tra quelli letti.
5. **Oro e argento: 4 video**, contro 0 la settimana prima.
   - «BORSE, BOND, ORO, BITCOIN: SVOLTA DOPO IL MIDTERM? COSA DICE LA TEORIA DEI CICLI», Vito Lops, 5/11 ([link](https://www.youtube.com/watch?v=lMCQpT_vQug))

   Prezzi: oro +3,7% in 1 settimana, argento +4,1%.
6. **Bitcoin e crypto: 3 video**, stabile (3 anche la settimana prima). Il tema è quasi tutto di Aldo Qefalia, che ne parla in 12 dei suoi 15 video. Nessuna serie di Bitcoin è in `prezzi.json`.
7. **Petrolio e Medio Oriente:** solo 2 menzioni, entrambe di BNP: il titolo del 9/11 e un capitolo «Petrolio». Eppure il Brent ha perso il 10,6% in 1 settimana. **Valutazione:** sul petrolio gli analisti seguiti parlano poco rispetto a quanto si muove il prezzo. Il terminale può mostrare proprio questo scarto.

**In calo** nel confronto omogeneo: debito e Treasury (1 video contro 3), Fed e tassi (0 contro 2) e crypto (2 contro 3). La settimana prima c'erano la Fed di Warsh e le aste dei Treasury, per esempio «Warsh ferma i tassi, i Treasury salgono: chi comanda davvero?» di Vito Lops, 29/10 ([link](https://www.youtube.com/watch?v=3cgTSxtbjj4)).

**Profilo dei canali** (fatto, dai feed):
- **Vito Lops:** macro, debito, AI e cicli; 4 video questa settimana.
- **Marco Lippiello:** un video a settimana di analisi dei conti delle Big Tech e dell'AI.
- **Aldo Qefalia:** Bitcoin e trading.
- **Investimenti BNP Paribas:** fino a 4 video al giorno. Dirette, «Morning Trading Show» con i capitoli, promozioni di certificati.
- **Stefano Bottaioli:** «QUICK NOTE» con titolo generico e descrizione fatta solo di avvertenze. Senza trascrizione, da questo canale non esce nessun tema.

## 5. Limiti

- **Niente parlato.** I temi vengono solo da titolo, descrizione e capitoli. Un video può parlare d'altro rispetto al titolo. Bottaioli resta del tutto «muto», e lo sono anche diversi video di Qefalia: il suo testo è solo promozionale, quindi conta solo il titolo.
- **15 video per feed.** BNP pubblica tanto: i suoi 15 video coprono solo dal 4 al 9/11. Per questo BNP è fuori dal confronto «in crescita/calo» (è in `copertura_incompleta`). L'archivio risolve il problema dopo qualche giorno di esecuzioni.
- **Peso diseguale dei canali.** Le puntate BNP con molti capitoli fanno scattare molti temi insieme, fino a 15 in un video. I conteggi sono per video, non per minuti di discorso.
- **Parole chiave:**
  - possono sbagliare. Per esempio, «energia per i data center» conta per il tema «Gas ed energia», e `=AI` in un titolo tutto maiuscolo può prendere una preposizione;
  - ogni tema registra la parola che l'ha fatto scattare, così si possono controllare;
  - il dizionario va curato nel tempo.
- **Serie mancanti in `prezzi.json`** per temi molto citati: Bitcoin, FTSE MIB, banche italiane, BTP e spread, VIX. Sono elencate in `serie_mancanti` di ogni tema.
- **Variazioni a 1 mese.** Prendo lo stesso giorno del mese prima rispetto all'ultima data della serie. Per i tassi, aggiornati al 6/11, il valore può differire di 1–3 pb dal campo `var.1m` di `prezzi.json`.
- **Dati che cambiano.** Visualizzazioni e voti valgono al momento della lettura. I video «programmati» (0 visualizzazioni) sono annunci di dirette.

## 6. Proposta: trascrizioni dal computer di Gabriele

YouTube blocca le trascrizioni dagli indirizzi cloud, quindi anche da GitHub Actions. Da una connessione di casa invece funzionano. La proposta è uno **script locale**, da lanciare a mano o con un'attività pianificata (cron o Utilità di pianificazione). Usa `pip install youtube-transcript-api` e non serve sul server.

```python
# raccolta/analisti/trascrivi_locale.py  (da girare sul computer di casa, non su GitHub Actions)
import json, os, re, sys
from youtube_transcript_api import YouTubeTranscriptApi   # pip install youtube-transcript-api
QUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(QUI, "trascrizioni"); os.makedirs(OUT, exist_ok=True)
dati = json.load(open(os.path.join(QUI, "..", "..", "docs", "data", "analisti.json"), encoding="utf-8"))
temi = json.load(open(os.path.join(QUI, "temi.json"), encoding="utf-8"))["temi"]
api = YouTubeTranscriptApi()
for v in dati["elementi"][:40]:                       # i più recenti
    f = os.path.join(OUT, v["video_id"] + ".json")
    if os.path.exists(f) or v["tipo"] == "short":
        continue
    try:
        t = api.fetch(v["video_id"], languages=["it", "en"])
    except Exception as e:
        print("salto", v["video_id"], e); continue
    testo = " ".join(s.text for s in t)
    frasi = re.split(r"(?<=[.?!])\s+", testo)
    # riassunto estrattivo: le 4 frasi con più parole chiave del dizionario
    def punti(fr): return sum(fr.lower().count(p.strip("=*").lower()) for tm in temi for p in tm["parole"])
    migliori = sorted(frasi, key=punti, reverse=True)[:4]
    riassunto = " ".join(fr for fr in frasi if fr in migliori)[:500]
    json.dump({"video_id": v["video_id"], "canale": v["canale"], "titolo": v["titolo"], "link": v["link"],
               "lingua": t.language_code, "generata": t.is_generated,
               "testo": testo, "riassunto": riassunto}, open(f, "w", encoding="utf-8"), ensure_ascii=False)
    print("ok", v["canale"], v["titolo"][:60])
```

**Come si collega.** `raccogli.py` legge già `trascrizioni/<video_id>.json`:
- usa il `testo` per riconoscere i temi;
- pubblica solo il `riassunto` (al massimo 600 caratteri) e `trascrizione: true`;
- il testo integrale **non** finisce in `docs/`.

**Diritti.** Per non ripubblicare il parlato, consiglio due cose:
1. tenere i testi integrali fuori dal repository pubblico, con una riga in `.gitignore` che li escluda, oppure con il campo `testo` salvato in un file separato e ignorato;
2. caricare solo i riassunti.

**Due miglioramenti possibili:**
- **riassunto migliore:** sostituire il riassunto estrattivo con uno prodotto da un modello linguistico, lanciato in locale (per esempio Claude da riga di comando sul file JSON), sempre con canale e link;
- **sottotitoli automatici:** quelli generati da YouTube (`generata: true`) hanno errori sui nomi dei titoli. Il dizionario degli alias aiuta, ma conviene segnalarlo.

## 7. Come mostrarlo sul terminale e sulla mappa

- **Pannello «Di cosa parlano gli analisti»:** le prime 5–6 righe di `collegamenti_prezzi[].riga`, con una freccia per i temi `in_crescita` e un riquadro di 2–3 titoli d'esempio, ognuno cliccabile con il nome del canale.
- **Accanto a ogni serie del pannello prezzi:** un badge con quante volte il tema o l'asset è citato nella settimana, da `temi_settimana.asset`. Per esempio: «Nvidia: citata in 4 video, −12,7% in 1 settimana».
- **Scarto da mettere in evidenza:** i temi con prezzi che si muovono molto ma pochi video (questa settimana petrolio e gas), e viceversa.
- **Sulla mappa:** questi dati non hanno coordinate. Il collegamento passa per i temi. Petrolio, Iran e Hormuz rimandano agli stretti, a `iran.json` e a `brent`; Cina e Taiwan ai semiconduttori; gas ed energia a `gas-italia.json` e `ttf`.
