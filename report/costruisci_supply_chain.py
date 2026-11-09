#!/usr/bin/env python3
"""Costruisce il report mensile «Supply chain e logistica» dai dati dell'osservatorio.

Solo libreria standard di Python 3. Uso, dalla radice del repository:

    python3 report/costruisci_supply_chain.py                 # edizione del mese corrente
    python3 report/costruisci_supply_chain.py --mese 2026-12  # un'altra edizione
    python3 report/costruisci_supply_chain.py --senza-rete    # non scarica i porti europei

Cosa fa, ogni volta che lo si rilancia:
1. legge i JSON di docs/data/ (portwatch, noli, stretti-dettaglio, ferrovie, cavi,
   cavi-incidenti, ibrido, scorte, gas-italia, terminali-gnl, calendario, prezzi,
   sanzioni-navi, navi, paesi; commercio e minerali se esistono);
2. aggiorna report/dati/porti-europei.json da IMF PortWatch (stessa API e stesso metodo
   di raccolta/flussi/raccogli.py); se la rete manca usa la copia già salvata;
3. ricalcola tutti i numeri del testo e disegna quattro grafici SVG (due larghezze);
4. scrive report/supply-chain-AAAA-MM.md, docs/report/supply-chain-AAAA-MM.html e gli
   SVG in report/grafici/sc-AAAA-MM-*.svg.

Regole: nessun numero dei dati è scritto a mano nel testo o nei grafici. Le sole cose
scritte qui sono:
- FATTI_ESTERNI: fatti letti sul web per le parti che i JSON non coprono (gasolio,
  terre rare, chip, GNSS, noli di un anno fa...). Ognuno ha fonte, link, data e
  affidabilità; lo script avvisa quando un fatto ha più di 60 giorni, perché va
  ricontrollato prima di pubblicare la nuova edizione;
- SOGLIE: le soglie degli indicatori, che sono una valutazione dell'osservatorio e
  sono dichiarate come tali nel report;
- il testo di raccordo e le valutazioni, marcate come tali.
"""

import argparse
import calendar
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(RADICE, "docs", "data")
CARTELLA_SVG = os.path.join(RADICE, "report", "grafici")
CARTELLA_CACHE = os.path.join(RADICE, "report", "dati")
CARTELLA_HTML = os.path.join(RADICE, "docs", "report")

MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]
MESI_BREVI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]

AVVISI = []


def avviso(msg):
    AVVISI.append(msg)
    print("AVVISO:", msg, file=sys.stderr)


# =====================================================================================
# Fatti esterni (letti sul web: i JSON dell'osservatorio non li contengono)
# Ogni voce: data del dato, fonte, link, affidabilità e come è stata letta.
# Da ricontrollare a ogni edizione: lo script avvisa se una voce ha più di 60 giorni.
# =====================================================================================
FATTI_ESTERNI = {
    "wci_anno_prima": {
        "data": "2025-11-06",
        "valori": {"composito": 1959, "Shanghai-Rotterdam": 1962, "Shanghai-Genoa": 2111,
                   "Shanghai-Los Angeles": 2647, "Shanghai-New York": 3837},
        "fonte": "Drewry WCI del 6 novembre 2025, ripreso da Cyprus Shipping News e Alchempro/Fibre2Fashion",
        "link": "https://cyprusshippingnews.com/2025/11/12/drewrys-world-container-index-increased-8-to-1959-per-40ft-container-this-week/",
        "affidabilita": "media",
        "letto": "pagina aperta in revisione il 9 novembre 2026: composito 1.959, Shanghai–Rotterdam 1.962, Shanghai–Genova 2.111 confermati",
    },
    # Il Baltic Dry non è più raccolto in automatico (termini d'uso di Trading Economics) ed è uscito da noli.json:
    # si cita a mano l'ultimo valore pubblicato dal Baltic Exchange, ripreso dalla stampa. Niente serie, niente
    # variazione su un anno (non verificata).
    "bdi": {
        "attuale": True,
        "data": "2026-11-06", "valore": 2805, "var_giorno_pct": 2.4, "bci": 4344,
        "testo": "massimo dal 12 ottobre, terza seduta in rialzo; indice capesize (BCI) a 4.344",
        "fonte": "Baltic Exchange, valore ripreso dalla nota di mercato di Trading Economics",
        "link": "https://tradingeconomics.com/commodity/baltic/news/599210",
        "affidabilita": "media",
        "letto": "ricerca web (pagina non aperta: dominio non raggiungibile dalla sessione); nessuna seconda fonte trovata",
    },
    "lli_hormuz": {
        "attuale": True,
        "data": "2026-11-05", "transiti_settimana": 116,
        "testo": "116 transiti di navi non legate all'Iran nella settimana 19–25 ottobre 2026, circa 17 al giorno",
        "fonte": "Lloyd's List Intelligence, Strait of Hormuz Brief del 5 novembre 2026",
        "link": "https://www.lloydslistintelligence.com/resources/blog/strait-of-hormuz-brief-5-november-2026",
        "affidabilita": "alta", "letto": "pagina aperta in revisione il 9 novembre 2026",
    },
    "gasolio": {
        "attuale": True,
        "data": "2026-11-07", "self": 2.224, "autostrada": 2.277, "self_1nov": 2.241,
        "fonte": "Mimit, Osservatorio prezzi carburanti (media nazionale self), ripreso da Affaritaliani",
        "link": "https://www.affaritaliani.it/economia/carburanti-benzina-a-un-soffio-dai-2-euro-il-self-scende-ancora-ma-il-gasolio-resta-alto.html",
        "link_1nov": "https://www.ladige.it/attualita/mimit-carburanti-in-calo-prezzo-medio-self-benzina-a-2-010-euro-gasolio-a-2-241-tywv0crm",
        "affidabilita": "media", "letto": "pagina aperta in revisione il 9 novembre 2026: 2,224 €/litro self confermato (Mimit, 7 novembre)",
    },
    "accise_gasolio": {
        "attuale": True,
        "data": "2026-11-08", "centesimi": 4.9,
        "testo": "il taglio delle accise sul gasolio deciso il 28 ottobre non è stato rinnovato: dall'8 novembre circa 4,9 centesimi al litro in più tra accise e IVA",
        "fonte": "Motor1 Italia", "link": "https://it.motor1.com/news/814756/stop-taglio-accise-diesel-novembre-2026/",
        "affidabilita": "media", "letto": "ricerca web",
    },
    "gasolio_anno_prima": {
        "data": "2025-10", "self": 1.627,
        "fonte": "QuiFinanza, osservatorio prezzi di ottobre 2025 (data esatta non indicata nell'estratto)",
        "link": "https://quifinanza.it/osservatorio-prezzi/prezzi-carburanti-benzina-diesel-ottobre-2025/933821/",
        "affidabilita": "bassa", "letto": "ricerca web",
    },
    "terre_rare": {
        "attuale": True,
        "data": "2026-11-09", "scadenza": "2026-11-10",
        "testo": ("la sospensione dei controlli cinesi all'export di terre rare decisi a ottobre 2025 "
                  "(annuncio MOFCOM-GAC n. 70 del 2025, compresa la regola dello 0,1% di contenuto cinese "
                  "nei prodotti esteri) scade il 10 novembre 2026; restano in vigore le licenze di aprile 2025 "
                  "su sette terre rare medie e pesanti (tra cui disprosio e ittrio). Alla data del report non "
                  "risultano annunci di proroga"),
        "fonte": "CIRS Group (testo dell'annuncio n. 70/2025) e Mining Technology",
        "link": "https://www.mining-technology.com/news/china-rare-earth-export-pause-nears-expiry-amid-persistent-supply-concentration/",
        "link2": "https://cirs-group.com/en/chemicals/china-temporarily-suspends-export-controls-on-key-raw-materials-including-rare-earths-lithium-batteries-and-diamond",
        "affidabilita": "media", "letto": "ricerca web (pagine non aperte: domini bloccati dalla rete della sessione)",
    },
    "crm_ue": {
        "data": "2023-03-16",
        "testo": "la Cina fornisce il 100% delle terre rare pesanti usate nell'UE, la Turchia il 98% del borato, il Sudafrica il 71% del platino",
        "fonte": "Commissione europea, comunicato sul Critical Raw Materials Act (IP/23/1661)",
        "link": "https://ec.europa.eu/commission/presscorner/detail/en/ip_23_1661",
        "affidabilita": "alta", "letto": "fonte ufficiale (dato del 2023)",
    },
    "dram": {
        "data": "2026-06",
        "testo": ("S&P Global Mobility prevede prezzi DRAM +70–100% nel 2026 sui nuovi contratti, perché i produttori "
                  "spostano capacità verso i chip per i data center AI; Micron (giugno 2026) dice che l'offerta di "
                  "memorie resterà scarsa oltre il 2027"),
        "fonte": "S&P Global Mobility (dicembre 2025); Counterpoint Research su Micron (giugno 2026)",
        "link": "https://www.spglobal.com/automotive-insights/en/blogs/2025/12/dram-makers-ai-data-centers-semiconductor-shortage",
        "link2": "https://counterpointresearch.com/jp/reports/memory-crisis-automotive-industry-suppliers-automakers-response",
        "affidabilita": "media", "letto": "ricerca web",
    },
    "gnss_golfo": {
        "data": "2026-04",
        "testo": ("nel 1° trimestre 2026 Hormuz, Golfo Persico e Golfo di Oman hanno concentrato il 98% degli eventi "
                  "di disturbo GNSS (jamming) registrati nel mondo, con oltre 1.100 navi colpite; posizioni AIS "
                  "spostate su aeroporti e nell'entroterra"),
        "fonte": "Windward, «What is GPS jamming and why are we seeing so much of it?»",
        "link": "https://windward.ai/blog/what-is-gps-jamming-and-why-are-we-seeing-so-much-of-it/",
        "affidabilita": "media", "letto": "ricerca web (pagina non aperta)",
    },
    "urea_sp": {
        "data": "2026-10-20",
        "testo": "per S&P Global la chiusura di Hormuz toglie il 29% del commercio mondiale di urea",
        "fonte": "Fertilizer Daily, su S&P Global",
        "link": "https://www.fertilizerdaily.com/20261020-global-food-crisis-hormuz-sp-global-el-nino/",
        "affidabilita": "media", "letto": "ricerca web",
    },
    "porti_it_2026": {
        "data": "2026-07",
        "testo": ("i porti italiani hanno movimentato 12,8 milioni di TEU nel 2025 (11,9 nel 2024); nel 1° semestre "
                  "2026 il traffico container italiano è cresciuto dell'1%, contro l'11% dei porti del Nord Africa "
                  "(Tanger Med)"),
        "fonte": "Intesa Sanpaolo, SRM (studi sul traffico container nel Mediterraneo, 2026)",
        "link": "https://group.intesasanpaolo.com/it/research/area-media/macro-italia/2026/mediterraneo-traffico-container-porti-italia",
        "affidabilita": "media", "letto": "ricerca web",
    },
    "porti_it_t1": {
        "data": "2026-05",
        "testo": "il traffico container nei porti italiani è sceso del 4,6% nel 1° trimestre 2026 sul 1° trimestre 2025",
        "fonte": "9colonne, «Hormuz crisis weighs on container traffic at Italian ports»",
        "link": "https://www.9colonne.it/614809/hormuz-crisis-weighs-on-container-traffic-at-italian-ports",
        "affidabilita": "media", "letto": "ricerca web",
    },
}

# Eventi da segnare sul grafico dei transiti (con fonte)
EVENTI_TRANSITI = [
    ("2023-12-01", "dic 2023: attacchi houthi, iniziano le deviazioni",
     "Drewry WCI da 1.521 a 3.777 $/FEU tra metà dicembre 2023 e il 18 gennaio 2024 (FreightWaves, in stretti-dettaglio.json)"),
    ("2026-03-02", "2 mar 2026: Hormuz chiuso di fatto",
     "stretti-dettaglio.json, scheda Hormuz"),
]

# Scadenze esterne da aggiungere al calendario (con fonte)
SCADENZE_EXTRA = [
    ("2026-11-10", "Cina: scade la sospensione dei controlli all'export di terre rare (annuncio n. 70/2025)",
     "CIRS Group / Mining Technology", "https://www.mining-technology.com/news/china-rare-earth-export-pause-nears-expiry-amid-persistent-supply-concentration/"),
    ("2026-11-15", "Kerch: scadono i permessi russi di passaggio per le navi del grano dell'Azov",
     "Baird Maritime (Reuters), in stretti-dettaglio.json", "https://www.bairdmaritime.com/shipping/dry-cargo/bulkers/sea-of-azov-reopens-to-grain-export-ships-after-months-long-shutdown-russian-naval-escorts-involved"),
    ("2026-12-01", "UE: fine della finestra per l'obiettivo di riempimento degli stoccaggi gas (90%, con deroghe)",
     "scorte.json (nota dell'indicatore)", "https://agsi.gie.eu/"),
    ("2026-12-31", "Qatar: forza maggiore sul GNL di Ras Laffan estesa almeno a fine dicembre",
     "Global LNG Hub, in stretti-dettaglio.json", "https://globallnghub.com/qatar-lng-capacity-hit-as-ras-laffan-attacks-damage-key-trains/"),
]

# Porti europei e mediterranei da confrontare con quelli italiani (id IMF PortWatch)
PORTI_UE = [
    ("port1114", "Rotterdam", "NL"), ("port57", "Anversa", "BE"), ("port446", "Amburgo", "DE"),
    ("port1348", "Valencia", "ES"), ("port31", "Algeciras", "ES"), ("port1265", "Tanger Med", "MA"),
    ("port908", "Pireo", "GR"), ("port712", "Marsiglia", "FR"), ("port592", "Capodistria (Koper)", "SI"),
    # Nord Europa e Baltico (aggiunti in revisione; id dal PortWatch_ports_database)
    ("port45", "Amsterdam", "NL"), ("port168", "Bremerhaven", "DE"), ("port1396", "Wilhelmshaven", "DE"),
    ("port408", "Göteborg", "SE"), ("port67", "Aarhus", "DK"), ("port328", "Esbjerg", "DK"),
    ("port380", "Danzica (Gdańsk)", "PL"), ("port579", "Klaipėda", "LT"),
]
PAESI_NORD = {"NL", "BE", "DE", "SE", "DK", "PL", "LT", "FI", "NO", "EE", "LV"}
PW = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services"

# =====================================================================================
# Soglie degli indicatori (VALUTAZIONE dell'osservatorio, dichiarata nel report)
# stato: "verde" / "giallo" / "rosso"; 'alto_male' = valori alti sono peggiori
# =====================================================================================
# Stati con lo stesso vocabolario del cruscotto del rischio (report/metodo-rischio.md): verde / giallo / rosso.
# I FLUSSI (transiti negli stretti) non hanno soglie proprie: si usano quelle del metodo (−10% / −30% sul
# riferimento, stesso riferimento di rischio.json). Le soglie qui sotto riguardano invece il LIVELLO di prezzi e
# noli, cioè il costo per chi importa o trasporta: il cruscotto del rischio misura le VARIAZIONI (su 90 giorni e su
# un anno), quindi le due letture possono dare colori diversi, e il report le mostra affiancate.
SOGLIE = {
    "fbx": {"giallo": 2500, "rosso": 4000, "alto_male": True,
            "perche": "dollari per FEU, indice globale"},
    "wci_genova": {"giallo": 3000, "rosso": 5000, "alto_male": True,
                   "perche": "dollari per FEU sulla rotta che serve l'Italia; 5.000 è anche la soglia dello scenario C del report Hormuz"},
    "ttf": {"giallo": 40, "rosso": 70, "alto_male": True,
            "perche": "€/MWh; gas e quindi elettricità e fertilizzanti; 70 è la soglia dello scenario A del report Hormuz"},
    "brent": {"giallo": 85, "rosso": 110, "alto_male": True,
              "perche": "$/barile; carburanti e bunker; 85 è la soglia dello scenario A del report Hormuz"},
    "stoccaggi_it": {"giallo": 90, "rosso": 80, "alto_male": False,
                     "perche": "% di riempimento; obiettivo UE 90%"},
    "gasolio": {"giallo": 1.9, "rosso": 2.2, "alto_male": True,
                "perche": "€/litro self; costo dell'autotrasporto"},
}
# soglie del metodo per i flussi (report/metodo-rischio.md, domanda «I flussi calano?»)
SOGLIE_FLUSSI = {"giallo": -10, "rosso": -30, "disruption": -50}


def stato(chiave, valore):
    s = SOGLIE[chiave]
    if valore is None:
        return "n.d."
    if s["alto_male"]:
        return "rosso" if valore >= s["rosso"] else "giallo" if valore >= s["giallo"] else "verde"
    return "rosso" if valore <= s["rosso"] else "giallo" if valore <= s["giallo"] else "verde"


def stato_flussi(var_pct):
    """Stato di un flusso con le soglie del metodo del cruscotto: ≥ −10% verde, −10/−30% giallo, < −30% rosso."""
    if var_pct is None:
        return "n.d."
    return "verde" if var_pct >= SOGLIE_FLUSSI["giallo"] else "giallo" if var_pct >= SOGLIE_FLUSSI["rosso"] else "rosso"


STATO_IT = {"verde": "verde", "giallo": "giallo", "rosso": "rosso", "n.d.": "n.d."}


def unita_rischio(v, uid):
    return v.get("rischio", {}).get(uid)


def flusso_rischio(v, uid):
    """Primo indicatore di flusso di un'unità del cruscotto del rischio: (valore %, riferimento, stato, nome)."""
    u = unita_rischio(v, uid)
    if not u:
        return None
    for i in u.get("indicatori", []):
        if i.get("gruppo") == "flussi":
            return {"valore": i.get("valore"), "riferimento": i.get("riferimento"), "stato": i.get("stato"),
                    "nome": i.get("nome"), "data": i.get("data")}
    return None


def livello_txt(v, uid):
    """«alto, 19,0 su 25» dal cruscotto del rischio."""
    u = unita_rischio(v, uid)
    if not u:
        return "n.d."
    return f"{u['livello']}, {num(u['punteggio'], 1)} su 25"


# =====================================================================================
# Utilità
# =====================================================================================

def leggi(nome, obbligatorio=True):
    p = os.path.join(DATI, nome)
    if not os.path.exists(p):
        if obbligatorio:
            raise SystemExit("manca docs/data/%s" % nome)
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def d(s):
    return dt.date.fromisoformat(str(s)[:10])


def num(v, dec=1, segno=False):
    """Numero all'italiana: virgola decimale, punto per le migliaia."""
    if v is None:
        return "n.d."
    s = f"{v:+,.{dec}f}" if segno else f"{v:,.{dec}f}"
    s = s.replace(",", "§").replace(".", ",").replace("§", ".")
    return s.replace("-", "−")


def pct(v, dec=0, segno=True):
    if v is None:
        return "n.d."
    if round(v, dec) == 0:
        return "0%"
    return num(v, dec, segno) + "%"


def data_it(x, anno=True):
    x = d(x) if not isinstance(x, dt.date) else x
    return f"{x.day} {MESI[x.month - 1]}" + (f" {x.year}" if anno else "")


def mese_it(chiave, breve=False):
    a, m = chiave.split("-")[:2]
    return (MESI_BREVI if breve else MESI)[int(m) - 1] + " " + a


def var(a, b):
    if a is None or b in (None, 0):
        return None
    return (a - b) / b * 100


def media(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def esc(s):
    return html.escape(str(s), quote=True)


def medie_mensili(serie):
    """Media mensile delle serie giornaliere, solo per i mesi completi (al massimo 2 giorni mancanti)."""
    gruppi = {}
    for g, v in serie:
        if v is None:
            continue
        gruppi.setdefault(g[:7], []).append(v)
    out = []
    for k in sorted(gruppi):
        a, m = map(int, k.split("-"))
        if len(gruppi[k]) >= calendar.monthrange(a, m)[1] - 2:
            out.append((k, sum(gruppi[k]) / len(gruppi[k])))
    return out


def maiuscola(t):
    """Prima lettera maiuscola senza toccare il resto (str.capitalize abbassa sigle e nomi)."""
    return t[:1].upper() + t[1:] if t else t


def apostrofo(numtesto):
    """True se il numero letto in italiano comincia per vocale (8, 11, 18, 80–89, 800...)."""
    n = numtesto.lstrip("+−-")
    return n.startswith("8") or re.match(r"^1[18](\D|$)", n) is not None


def il(numtesto):
    return ("l'" if apostrofo(numtesto) else "il ") + numtesto


def al(numtesto):
    return ("all'" if apostrofo(numtesto) else "al ") + numtesto


def da(numtesto):
    return ("dall'" if apostrofo(numtesto) else "dal ") + numtesto


def data_tab(x):
    """Data compatta per le tabelle: 9 nov 2026."""
    x = d(x) if not isinstance(x, dt.date) else x
    return f"{x.day} {MESI_BREVI[x.month - 1]} {x.year}"


def fonte_breve(s):
    """Nome corto della fonte per il testo del link: taglia a ' (', ',' o ':' fuori dalle parentesi."""
    out, liv = "", 0
    for i, ch in enumerate(s):
        if ch == "(":
            if liv == 0 and i > 0 and s[i - 1] == " ":
                break
            liv += 1
        elif ch == ")":
            liv -= 1
        elif ch in ",:;" and liv == 0:
            break
        out += ch
    return out.strip()


def num_auto(x):
    """Numero con i decimali che servono (al massimo 3), senza zeri finali."""
    if float(x) == int(x):
        return num(x, 0)
    for dec in (1, 2, 3):
        if abs(round(x, dec) - x) < 1e-9:
            return num(x, dec)
    return num(x, 3)


def nome_porto(n):
    return n.replace(" (", " ").replace(")", "")


def link(testo, url):
    return f"[{testo}]({url})"


def fonte_est(chiave):
    f = FATTI_ESTERNI[chiave]
    return f"{link(f['fonte'], f['link'])}, {data_breve(f['data'])}"


def data_breve(s):
    s = str(s)
    if len(s) == 7:
        return mese_it(s)
    return data_it(s)


def scarica(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": "monitor-geoeconomico (report supply chain)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# =====================================================================================
# Porti europei da IMF PortWatch (cache in report/dati/porti-europei.json)
# =====================================================================================

def pw_query(servizio, where, campi):
    righe, offset = [], 0
    while True:
        q = urllib.parse.urlencode({
            "where": where, "outFields": ",".join(campi), "orderByFields": "date",
            "returnGeometry": "false", "resultOffset": offset, "resultRecordCount": 1000, "f": "json"})
        r = json.loads(scarica("%s/%s/FeatureServer/0/query?%s" % (PW, servizio, q)))
        if "error" in r:
            raise RuntimeError(str(r["error"]))
        f = [x["attributes"] for x in r.get("features", [])]
        righe += f
        if not r.get("exceededTransferLimit") and len(f) < 1000:
            break
        offset += len(f)
    return righe


def confronto_porto(righe, campi):
    """Stesso metodo di raccolta/flussi/raccogli.py: media 7 e 30 giorni all'ultima data,
    stessi giorni di 52 settimane prima."""
    per_data = {r["date"]: r for r in righe if r.get("date")}
    if not per_data:
        return None
    ultima = max(per_data)
    u = d(ultima)

    def finestra(fine, giorni):
        return {c: media([per_data.get((fine - dt.timedelta(days=k)).isoformat(), {}).get(c)
                          for k in range(giorni)]) for c in campi}
    m7, m7a = finestra(u, 7), finestra(u - dt.timedelta(days=364), 7)
    m30, m30a = finestra(u, 30), finestra(u - dt.timedelta(days=364), 30)
    r1 = lambda x: None if x is None else round(x, 1)
    return {
        "ultima_data": ultima,
        "media7": {c: r1(v) for c, v in m7.items()}, "media7_anno_prima": {c: r1(v) for c, v in m7a.items()},
        "media30": {c: r1(v) for c, v in m30.items()}, "media30_anno_prima": {c: r1(v) for c, v in m30a.items()},
        "var7_anno_pct": {c: r1(var(m7[c], m7a[c])) for c in campi},
        "var30_anno_pct": {c: r1(var(m30[c], m30a[c])) for c in campi},
        "periodo_media30": [(u - dt.timedelta(days=29)).isoformat(), ultima],
    }


def porti_europei(oggi, senza_rete):
    cache = os.path.join(CARTELLA_CACHE, "porti-europei.json")
    vecchio = None
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            vecchio = json.load(f)
    if vecchio:
        for e in vecchio.get("elementi", []):
            e.setdefault("gruppo", "nord" if e.get("paese") in PAESI_NORD else "mediterraneo")
    if senza_rete:
        if vecchio is None:
            avviso("porti europei: nessuna copia salvata e rete disattivata")
        return vecchio
    campi = ["portcalls", "portcalls_container", "portcalls_tanker", "portcalls_dry_bulk", "import", "export"]
    inizio = (oggi - dt.timedelta(days=430)).isoformat()
    elementi, errori = [], []
    for pid, nome, paese in PORTI_UE:
        try:
            r = pw_query("Daily_Ports_Data", "portid='%s' AND date>=DATE '%s'" % (pid, inizio), ["date"] + campi)
            cf = confronto_porto(r, campi)
            if not cf:
                raise RuntimeError("nessun dato")
            elementi.append({"id": pid, "nome": nome, "paese": paese,
                             "gruppo": "nord" if paese in PAESI_NORD else "mediterraneo",
                             "fonte": "IMF PortWatch (Daily Ports Data)",
                             "link": "https://portwatch.imf.org/", "data_fonte": cf["ultima_data"],
                             "affidabilita": "alta", **cf})
        except Exception as e:  # la rete o l'API possono mancare: si tiene la copia vecchia
            errori.append("%s: %s" % (nome, e))
    if not elementi:
        avviso("porti europei: PortWatch non raggiungibile (%s); uso la copia salvata" % "; ".join(errori[:2]))
        return vecchio
    out = {"aggiornato": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
           "fonti": [{"nome": "IMF PortWatch (FMI e Università di Oxford), Daily Ports Data",
                      "link": "https://portwatch.imf.org/", "licenza": "dati pubblici FMI; citare «IMF PortWatch»",
                      "data_dato": max(e["ultima_data"] for e in elementi)}],
           "nota": ("Chiamate di navi al giorno stimate da AIS. Medie a 7 e 30 giorni all'ultima data, confrontate "
                    "con gli stessi giorni di 52 settimane prima (metodo di raccolta/flussi/raccogli.py). "
                    "File di supporto del report supply chain, scritto da report/costruisci_supply_chain.py."),
           "elementi": elementi, "errori": errori}
    os.makedirs(CARTELLA_CACHE, exist_ok=True)
    with open(cache, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return out


# =====================================================================================
# Calcoli
# =====================================================================================

def calcola(oggi, senza_rete):
    v = {"mancanti": [], "oggi": oggi}
    pw = leggi("portwatch.json")
    noli = leggi("noli.json")
    sd = leggi("stretti-dettaglio.json")
    fer = leggi("ferrovie.json")
    cavi = leggi("cavi.json")
    ci = leggi("cavi-incidenti.json")
    ib = leggi("ibrido.json", False)
    scorte = leggi("scorte.json")
    gas = leggi("gas-italia.json")
    gnl = leggi("terminali-gnl.json")
    cal = leggi("calendario.json")
    prezzi = leggi("prezzi.json")
    sanz = leggi("sanzioni-navi.json")
    navi = leggi("navi.json")
    paesi = leggi("paesi.json")
    rischio = leggi("rischio.json", False)
    for nome in ("commercio.json", "minerali.json"):
        if leggi(nome, False) is None:
            v["mancanti"].append(nome)
    v["file_letti"] = [("portwatch.json", pw), ("noli.json", noli), ("stretti-dettaglio.json", sd),
                       ("ferrovie.json", fer), ("cavi.json", cavi), ("cavi-incidenti.json", ci),
                       ("ibrido.json", ib), ("scorte.json", scorte), ("gas-italia.json", gas),
                       ("terminali-gnl.json", gnl), ("calendario.json", cal), ("prezzi.json", prezzi),
                       ("sanzioni-navi.json", sanz), ("navi.json", navi), ("paesi.json", paesi),
                       ("rischio.json", rischio)]
    # cruscotto del rischio: livelli per unità e indicatore di flusso (stesso riferimento del metodo)
    v["rischio"] = {u["id"]: u for u in (rischio or {}).get("unita", [])}
    v["rischio_data"] = (rischio or {}).get("data_riferimento")
    if rischio is None:
        avviso("manca docs/data/rischio.json: il report non può confrontarsi con il cruscotto del rischio")

    # ---------------- stretti
    cp = {e["nome"]: e for e in pw["elementi"] if e["tipo"] == "chokepoint"}
    v["cp"] = cp
    v["pw_data"] = max(e["ultima_data"] for e in cp.values())
    v["pw_periodo"] = cp["Canale di Suez"]["periodo_media7"]
    v["mensili"] = {k: medie_mensili(cp[k]["serie"]["n_total"])
                    for k in ("Canale di Suez", "Bab el-Mandeb", "Capo di Buona Speranza", "Stretto di Hormuz")}
    for k, s in v["mensili"].items():
        s23 = [x for x in s if x[0] <= "2023-10"]
        v.setdefault("pre_crisi", {})[k] = media([x[1] for x in s23 if x[0] >= "2023-01"])
    v["ultimo_mese"] = v["mensili"]["Canale di Suez"][-1][0]

    def rapporto(nome):
        e = cp[nome]
        return 100 * e["media7"]["n_total"] / e["media7_tre_anni_prima"]["n_total"]
    v["suez_ratio"] = rapporto("Canale di Suez")
    v["bab_ratio"] = rapporto("Bab el-Mandeb")
    v["capo_ratio"] = rapporto("Capo di Buona Speranza")
    # rapporto con la media gennaio–ottobre 2023, il riferimento del metodo del cruscotto per il Mar Rosso
    v["pre_ratio"] = {k: 100 * cp[k]["media7"]["n_total"] / v["pre_crisi"][k]
                      for k in ("Canale di Suez", "Bab el-Mandeb", "Capo di Buona Speranza") if v["pre_crisi"].get(k)}
    # minimo mensile di Suez dal 2024 e quando
    s24 = [x for x in v["mensili"]["Canale di Suez"] if x[0] >= "2024-01"]
    v["suez_min"] = min(s24, key=lambda x: x[1])
    v["capo_max"] = max(v["mensili"]["Capo di Buona Speranza"], key=lambda x: x[1])

    # schede curate
    schede = {e["id"]: e for e in sd["elementi"]}
    v["schede"] = schede

    def voce(id_, sez, inizio):
        for x in schede.get(id_, {}).get(sez, []):
            if x["voce"].startswith(inizio):
                return x
        return None
    v["voce"] = voce

    # ---------------- noli
    nl = {e["id"]: e for e in noli["elementi"]}
    v["noli"] = nl
    wci = nl.get("wci")
    est = FATTI_ESTERNI["wci_anno_prima"]
    if wci:
        v["wci_yoy"] = var(wci["valore"], est["valori"]["composito"])
        v["wci_rotte_yoy"] = {r: var(x, est["valori"].get(r)) for r, x in wci.get("rotte", {}).items()}
        if abs((d(wci["data"]) - d(est["data"])).days - 365) > 20:
            avviso("il riferimento WCI di un anno prima (%s) non è più a un anno dal dato (%s): aggiornare FATTI_ESTERNI"
                   % (est["data"], wci["data"]))
    fbx = nl.get("fbx")
    if fbx and len(fbx["storico"]) >= 2:
        st = fbx["storico"]
        v["fbx_inizio"] = st[0]
        v["fbx_max"] = max(st, key=lambda x: x[1])
        quattro = [x for x in st if d(x[0]) <= d(st[-1][0]) - dt.timedelta(days=28)]
        v["fbx_4s"] = quattro[-1] if quattro else st[0]
        v["fbx_var4s"] = var(st[-1][1], v["fbx_4s"][1])
        v["fbx_var_inizio"] = var(st[-1][1], st[0][1])

    # ---------------- porti
    v["porti_it"] = [e for e in pw["elementi"] if e["tipo"] == "porto"]
    v["porti_it_data"] = max(e["ultima_data"] for e in v["porti_it"])
    v["porti_ue"] = porti_europei(oggi, senza_rete)

    # ---------------- ferrovie
    cor = {e["id"]: e for e in fer["elementi"] if e["categoria"] == "corridoio-strategico"}
    v["corridoi"] = cor
    v["incidenti_ferrovie"] = [e for e in fer["elementi"] if e["categoria"] == "evento"]
    suez_teu = voce("suez", "flussi", "Container")
    v["suez_teu"] = suez_teu
    m = re.search(r"([\d.]+) TEU a settimana", suez_teu["valore"]) if suez_teu else None
    v["suez_teu_sett"] = int(m.group(1).replace(".", "")) if m else None
    teu_ce = next((x for x in cor.get("FR-COR-01", {}).get("volumi", []) if x["unita"] == "TEU"), None)
    v["teu_ce"] = teu_ce
    v["settimane_suez"] = teu_ce["valore"] / v["suez_teu_sett"] if teu_ce and v["suez_teu_sett"] else None

    # ---------------- prezzi
    pz = {s["id"]: s for s in prezzi["serie"]}
    v["pz"] = pz

    # ---------------- scorte e gas
    sc = {r["id"]: r for r in scorte["riepilogo"]}
    v["sc"] = sc
    v["quote_gas"] = gas["quote_12_mesi"]
    ing = medie_mensili(gas["ingressi_totali"]["serie"])
    v["ingressi_mese"] = ing[-1] if ing else None
    v["gas_data"] = gas["fonti"][0]["data_dato"]
    golfo = {"QA", "IR", "KW", "BH", "IQ"}
    exp_op = [e for e in gnl["elementi"] if e["tipo"] == "export" and e["stato"] == "operativo"]
    tot = sum(e.get("capacita_operativa_mtpa") or 0 for e in exp_op)
    dentro = sum(e.get("capacita_operativa_mtpa") or 0 for e in exp_op
                 if e["paese"] in golfo or (e["paese"] == "AE" and e["lon"] < 56.3))
    v["gnl_liq_tot"], v["gnl_liq_golfo"] = tot, dentro
    v["gnl_it_regas"] = sum(e.get("capacita_operativa_mtpa") or 0 for e in gnl["elementi"]
                            if e["paese"] == "IT" and e["tipo"] == "import" and e["stato"] == "operativo")
    v["gnl_data"] = gnl["fonti"][0]["data_dato"]

    # ---------------- paesi
    pe = {e["paese"]: e for e in paesi["elementi"]}
    v["paesi"] = pe

    # ---------------- cavi
    rc = cavi["riepilogo"]
    v["cavi_riep"] = rc
    v["cavi_it_asia"] = sorted({e["nome"] for e in cavi["elementi"] if e.get("approdi_it")
                                and "Bab el-Mandeb" in (e.get("s") or []) and e["stato"] == "attivo"})
    v["cavi_data"] = cavi["fonti"][0]["data_dato"]
    v["incidenti_cavi"] = ci["elementi"]

    # ---------------- ibrido
    v["ibrido"] = (ib or {}).get("punti", [])

    # ---------------- sanzioni e navi
    v["sanz"] = sanz["conteggi"]
    v["sanz_data"] = max(f["data_dato"] for f in sanz["fonti"] if f.get("data_dato"))
    v["navi_aree"] = navi["riepilogo_aree"]
    v["navi_spoof"] = [e for e in navi["elementi"] if e.get("avviso_posizione")]
    v["navi_agg"] = navi["aggiornato"]

    # ---------------- calendario
    fine = oggi + dt.timedelta(days=42)
    # solo ciò che muove energia, noli e commercio: energia (un'uscita per tipo), vertici e banche centrali
    # di importanza alta per UE/USA/Cina, sanzioni su Russia e Iran
    ev, visti = [], set()
    for e in cal["elementi"]:
        if not (oggi.isoformat() <= e["data"] <= fine.isoformat()):
            continue
        c, imp, paese = e["categoria"], e.get("importanza"), e.get("paese")
        tipo = re.sub(r"\s*[-–].*$", "", e["titolo"]).split(":")[0] + ":" + e["titolo"].split(":")[1][:25] if ":" in e["titolo"] else e["titolo"]
        ok = ((c == "energia" and imp in ("alta", "media")) or
              (c in ("vertice", "banca-centrale") and imp == "alta" and paese in ("EU", "US", "CN", "BE")) or
              (c == "sanzioni" and re.search(r"Russia|Iran", e["titolo"])))
        if ok and tipo not in visti:
            visti.add(tipo)
            ev.append((e["data"], e["titolo"], e["fonte"], e.get("link")))
    ev += [x for x in SCADENZE_EXTRA if oggi.isoformat() <= x[0] <= fine.isoformat()]
    v["agenda"] = sorted(ev)

    # ---------------- controllo età dei fatti esterni
    for k, f in FATTI_ESTERNI.items():
        s = str(f["data"])
        x = d(s + "-28") if len(s) == 7 else d(s)
        # i fatti «attuali» (prezzi, scadenze) vanno riletti a ogni edizione; gli altri sono riferimenti datati
        if f.get("attuale") and (oggi - x).days > 21:
            avviso("fatto esterno «%s» del %s ha più di 3 settimane: rileggere la fonte prima di pubblicare" % (k, s))
        elif (oggi - x).days > 240 and k not in ("crm_ue", "wci_anno_prima", "gasolio_anno_prima"):
            avviso("fatto esterno «%s» del %s ha più di 8 mesi: cercare un dato più recente" % (k, s))
    return v


# =====================================================================================
# Grafici SVG
# =====================================================================================
STILE = """
.viz{--v-s1:#A61E6B;--v-s2:#eb6834;--v-s3:#2a78d6;--v-ok:#0ca30c;--v-warn:#fab219;--v-crit:#d03b3b;
--v-ink:#1D272D;--v-soft:#52606A;--v-faint:#86929A;--v-grid:#DCDFDD;--v-bg:#F6F5F0;--v-card:#FFFFFF;--v-band:#ECE9E0;
font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
@media (prefers-color-scheme:dark){.viz{--v-s1:#d14f9a;--v-s2:#d95926;--v-s3:#3987e5;
--v-ink:#DAE0E2;--v-soft:#A0ABB1;--v-faint:#6C787F;--v-grid:#2B373E;--v-bg:#10181D;--v-card:#172127;--v-band:#1A252C}}
.viz text{fill:var(--v-soft);font-size:var(--fs,12px)}
.viz .t-ink{fill:var(--v-ink)}.viz .t-b{font-weight:600}.viz .t-faint{fill:var(--v-faint)}
.viz .num{font-variant-numeric:tabular-nums}
.viz .grid{stroke:var(--v-grid);stroke-width:1}.viz .base{stroke:var(--v-faint);stroke-width:1}
.viz .ev{stroke:var(--v-faint);stroke-width:1;stroke-dasharray:3 3}
.viz .l{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.viz .c-s1{stroke:var(--v-s1)}.viz .c-s2{stroke:var(--v-s2)}.viz .c-s3{stroke:var(--v-s3)}
.viz .f-s1{fill:var(--v-s1)}.viz .f-s2{fill:var(--v-s2)}.viz .f-s3{fill:var(--v-s3)}
.viz .f-ok{fill:var(--v-ok)}.viz .f-warn{fill:var(--v-warn)}.viz .f-crit{fill:var(--v-crit)}
.viz .card{fill:var(--v-card);stroke:var(--v-grid);stroke-width:1}
.viz .ring{stroke:var(--v-bg);stroke-width:2}
.viz .hit{fill:transparent}.viz .hit:hover{fill:var(--v-ink);fill-opacity:.06}
.viz .tick{stroke:var(--v-ink);stroke-width:2}
"""


class Scala:
    def __init__(self, d0, d1, r0, r1):
        self.d0, self.d1, self.r0, self.r1 = d0, d1, r0, r1

    def __call__(self, x):
        return self.r0 + (x - self.d0) / (self.d1 - self.d0) * (self.r1 - self.r0)


def tacche(maxv, n=5):
    for p in [1, 2, 2.5, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000]:
        if maxv / p <= n:
            return [i * p for i in range(int(maxv // p) + 2) if i * p <= maxv + 1e-9]
    return [0, maxv]


def svg_apri(w, h, titolo, descr, id_, fs):
    return [f'<svg class="viz" id="{id_}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" '
            f'role="img" aria-labelledby="{id_}-t {id_}-d" style="--fs:{fs}px;max-width:{w}px;height:auto;display:block">',
            f'<title id="{id_}-t">{esc(titolo)}</title><desc id="{id_}-d">{esc(descr)}</desc>',
            f"<style>{STILE}</style>"]


def mese_idx(k):
    a, m = map(int, k.split("-"))
    return a * 12 + m - 1


def grafico_transiti(v, largo=True):
    w, h, fs = (720, 380, 12) if largo else (360, 330, 11)
    ml, mr, mt, mb = (40, 118, 46, 34) if largo else (30, 92, 52, 30)
    serie = [("Capo di Buona Speranza", "Capo", "s2"), ("Canale di Suez", "Suez", "s3"),
             ("Bab el-Mandeb", "Bab el-Mandeb", "s1")]
    tutti = [x for k, _, _ in serie for x in v["mensili"][k]]
    mesi = sorted({x[0] for x in tutti})
    i0, i1 = mese_idx(mesi[0]), mese_idx(mesi[-1])
    ymax = max(x[1] for x in tutti)
    tk = tacche(ymax * 1.05, 5)
    X = Scala(i0, i1, ml, w - mr)
    Y = Scala(0, tk[-1], h - mb, mt)
    idg = "g-transiti" + ("" if largo else "-m")
    out = svg_apri(w, h, "Transiti giornalieri a Suez, Bab el-Mandeb e Capo di Buona Speranza, 2023–%s" % v["ultimo_mese"][:4],
                   "Media mensile delle navi al giorno (IMF PortWatch). Suez e Bab el-Mandeb crollano da dicembre 2023, "
                   "mentre il Capo di Buona Speranza raddoppia.", idg, fs)
    out.append(f'<text x="{ml}" y="{mt - 26}" class="t-ink t-b">Navi al giorno, media mensile</text>')
    out.append(f'<text x="{ml}" y="{mt - 10}" class="t-faint">IMF PortWatch (AIS) · mesi completi fino a {mese_it(v["ultimo_mese"])}</text>')
    for t in tk:
        y = Y(t)
        out.append(f'<line x1="{ml}" x2="{w - mr}" y1="{y:.1f}" y2="{y:.1f}" class="{"base" if t == 0 else "grid"}"/>')
        out.append(f'<text x="{ml - 6}" y="{y + 4:.1f}" text-anchor="end" class="num">{num(t, 0)}</text>')
    for a in range(int(mesi[0][:4]), int(mesi[-1][:4]) + 1):
        i = a * 12
        if i0 <= i <= i1:
            out.append(f'<text x="{X(i):.1f}" y="{h - mb + 16}" text-anchor="middle" class="num">{a}</text>')
            out.append(f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{h - mb}" y2="{h - mb + 4}" class="base"/>')
    # eventi
    for k, (data_ev, testo, _) in enumerate(EVENTI_TRANSITI):
        dd = d(data_ev)
        i = dd.year * 12 + dd.month - 1 + (dd.day - 1) / 31
        if i0 <= i <= i1:
            x = X(i)
            out.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{mt}" y2="{h - mb}" class="ev"/>')
            # etichette nella fascia bassa del grafico, dove non passano linee (valori sotto 20)
            etichetta = testo if largo else testo.split(":")[0]
            ancora = "start" if x < w * 0.6 else "end"
            dx = 4 if ancora == "start" else -4
            yl = Y(tk[-1] * (0.16 if k == 0 else 0.08))
            out.append(f'<text x="{x + dx:.1f}" y="{yl:.1f}" text-anchor="{ancora}" class="t-faint">{esc(etichetta)}</text>')
    # linee
    finali = []
    for k, etich, col in serie:
        pts = [(X(mese_idx(m)), Y(val)) for m, val in v["mensili"][k]]
        out.append(f'<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" class="l c-{col}"/>')
        finali.append([pts[-1][1], etich if largo or len(etich) < 9 else etich.split()[0], col, v["mensili"][k][-1][1], pts[-1][0]])
    # etichette dirette a fine linea, distanziate
    finali.sort()
    for j in range(1, len(finali)):
        if finali[j][0] - finali[j - 1][0] < fs + 4:
            finali[j][0] = finali[j - 1][0] + fs + 4
    for y, etich, col, val, x in finali:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" class="f-{col} ring"/>')
        out.append(f'<text x="{x + 8:.1f}" y="{y + 4:.1f}" class="t-ink"><tspan class="t-b num">{num(val, 0)}</tspan> {esc(etich)}</text>')
    # legenda in basso a sinistra (identità non affidata solo al colore)
    lx, ly = ml, h - 4
    for k, etich, col in serie:
        out.append(f'<line x1="{lx}" x2="{lx + 14}" y1="{ly - 4}" y2="{ly - 4}" class="l c-{col}" style="stroke-width:3"/>')
        out.append(f'<text x="{lx + 18}" y="{ly}" class="t-ink">{esc(etich)}</text>')
        lx += 18 + len(etich) * fs * 0.58 + 14
    # zone di passaggio (tooltip nativo)
    passo = (X(i0 + 1) - X(i0))
    per_mese = {}
    for k, etich, _ in serie:
        for m, val in v["mensili"][k]:
            per_mese.setdefault(m, []).append(f"{etich} {num(val, 1)}")
    for m, testi in sorted(per_mese.items()):
        x = X(mese_idx(m)) - passo / 2
        out.append(f'<rect x="{x:.1f}" y="{mt}" width="{passo:.1f}" height="{h - mb - mt}" class="hit">'
                   f'<title>{esc(mese_it(m))}: {esc(" · ".join(testi))} navi al giorno</title></rect>')
    out.append("</svg>")
    return "\n".join(out)


def grafico_noli(v, largo=True):
    """Due pannelli con la stessa unità ($ per FEU): andamento FBX e ultimo valore per rotta."""
    w = 720 if largo else 360
    fs = 12 if largo else 11
    nl = v["noli"]
    fbx, wci = nl.get("fbx"), nl.get("wci")
    est = FATTI_ESTERNI["wci_anno_prima"]
    idg = "g-noli" + ("" if largo else "-m")
    # pannello rotte
    rotte = []
    if wci:
        rotte.append(("WCI composito", wci["valore"], est["valori"].get("composito")))
        nomi = {"Shanghai-Genoa": "Shanghai–Genova", "Shanghai-Rotterdam": "Shanghai–Rotterdam",
                "Shanghai-Los Angeles": "Shanghai–Los Angeles", "Shanghai-New York": "Shanghai–New York"}
        for k in ("Shanghai-Genoa", "Shanghai-Rotterdam", "Shanghai-Los Angeles", "Shanghai-New York"):
            if k in wci.get("rotte", {}):
                rotte.append((nomi[k], wci["rotte"][k], est["valori"].get(k)))
    altezza_rotte = 34 + len(rotte) * 30 + 30
    h_trend = 220 if largo else 200
    h = h_trend + altezza_rotte + 20
    out = svg_apri(w, h, "Noli container: andamento FBX e ultimo valore WCI per rotta",
                   "Freightos FBX globale settimanale e Drewry WCI per rotta, in dollari per container da 40 piedi, "
                   "con il valore di un anno prima dove disponibile.", idg, fs)
    ml, mr = (44, 70) if largo else (40, 52)
    # --- trend FBX
    mt, mb = 44, 28
    if fbx and len(fbx["storico"]) >= 2:
        st = [(d(a), b) for a, b in fbx["storico"]]
        lo = min(b for _, b in st)
        hi = max(b for _, b in st)
        y0 = max(0, (lo // 500) * 500 - 500)
        y1 = (hi // 500 + 1) * 500
        X = Scala(st[0][0].toordinal(), st[-1][0].toordinal(), ml, w - mr)
        Y = Scala(y0, y1, h_trend - mb, mt)
        out.append(f'<text x="{ml}" y="18" class="t-ink t-b">Freightos FBX globale, $ per FEU</text>')
        out.append(f'<text x="{ml}" y="34" class="t-faint">{"serie settimanale disponibile gratis: " if largo else "settimanale, "}{esc(data_it(st[0][0], anno=largo))} – {esc(data_it(st[-1][0]))}</text>')
        passo = 500 if (y1 - y0) <= 2500 else 1000
        t = y0
        while t <= y1:
            y = Y(t)
            out.append(f'<line x1="{ml}" x2="{w - mr}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>')
            out.append(f'<text x="{ml - 6}" y="{y + 4:.1f}" text-anchor="end" class="num">{num(t, 0)}</text>')
            t += passo
        pts = [(X(a.toordinal()), Y(b)) for a, b in st]
        out.append('<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '" class="l c-s3"/>')
        for (a, b), (x, y) in zip(st, pts):
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="f-s3 ring"/>')
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" class="hit"><title>{esc(data_it(a))}: {num(b, 0)} $/FEU</title></circle>')
        for (a, b), (x, y) in [(st[0], pts[0]), (st[-1], pts[-1])]:
            anc = "start" if (a, b) == st[0] else "end"
            out.append(f'<text x="{x + (0 if anc == "start" else 0):.1f}" y="{y - 10:.1f}" text-anchor="{anc}" class="t-ink num t-b">{num(b, 0)}</text>')
        for a, _ in [st[0], st[len(st) // 2], st[-1]]:
            anc = "start" if a == st[0][0] else "end" if a == st[-1][0] else "middle"
            out.append(f'<text x="{X(a.toordinal()):.1f}" y="{h_trend - mb + 16}" text-anchor="{anc}">{esc(data_it(a, anno=False))}</text>')
    # --- rotte
    top = h_trend + 20
    out.append(f'<text x="{ml if largo else 8}" y="{top}" class="t-ink t-b">Drewry WCI per rotta, $ per FEU</text>')
    if wci:
        out.append(f'<text x="{ml if largo else 8}" y="{top + 16}" class="t-faint">barra: {esc(data_it(wci["data"]))} · tacca: {esc(data_it(est["data"]))} (fonte secondaria)</text>')
    lab = 150 if largo else 118
    x0 = (ml if largo else 8) + lab
    xmax = max([r[1] for r in rotte] + [r[2] or 0 for r in rotte] + [1])
    Xr = Scala(0, xmax * 1.12, x0, w - (mr if largo else 46))
    y = top + 34
    for nome, val, prima in rotte:
        bh = 16
        out.append(f'<text x="{x0 - 8}" y="{y + bh - 4}" text-anchor="end" class="t-ink">{esc(nome)}</text>')
        out.append(f'<rect x="{x0}" y="{y}" width="{Xr(val) - x0:.1f}" height="{bh}" rx="3" class="f-s1"/>')
        out.append(f'<text x="{Xr(val) + 6:.1f}" y="{y + bh - 4}" class="t-ink num t-b">{num(val, 0)}</text>')
        if prima:
            xp = Xr(prima)
            out.append(f'<line x1="{xp:.1f}" x2="{xp:.1f}" y1="{y - 3}" y2="{y + bh + 3}" class="tick"/>')
        tt = f"{nome}: {num(val, 0)} $/FEU" + (f"; un anno prima {num(prima, 0)} ({pct(var(val, prima))})" if prima else "")
        out.append(f'<rect x="{x0 - lab}" y="{y - 6}" width="{w - x0 + lab}" height="{bh + 12}" class="hit"><title>{esc(tt)}</title></rect>')
        y += 30
    out.append("</svg>")
    return "\n".join(out)


def righe_porti(v, gruppo="mediterraneo"):
    it = [(e["nome"], e["var30_anno_pct"], e["media30"]["portcalls"], e["media30_anno_prima"]["portcalls"]) for e in v["porti_it"]]
    ue = []
    if v["porti_ue"]:
        ue = [(e["nome"], e["var30_anno_pct"]["portcalls"], e["media30"]["portcalls"], e["media30_anno_prima"]["portcalls"])
              for e in v["porti_ue"]["elementi"] if e.get("gruppo") == gruppo]
    it.sort(key=lambda x: (x[1] is None, -(x[1] or 0)))
    ue.sort(key=lambda x: (x[1] is None, -(x[1] or 0)))
    return it, ue


def grafico_porti(v, largo=True):
    it, ue = righe_porti(v)
    _, nord = righe_porti(v, "nord")
    w = 720 if largo else 360
    fs = 12 if largo else 11
    rh = 24 if largo else 22
    gruppi = ([("Porti italiani", it)] + ([("Mediterraneo e Atlantico", ue)] if ue else [])
              + ([("Nord Europa e Baltico", nord)] if nord else []))
    h = 60 + sum(26 + len(r) * rh for _, r in gruppi) + 10
    idg = "g-porti" + ("" if largo else "-m")
    out = svg_apri(w, h, "Porti: chiamate di navi, variazione anno su anno (media 30 giorni)",
                   "Variazione percentuale delle chiamate di navi al giorno negli ultimi 30 giorni rispetto agli stessi giorni "
                   "di un anno prima, IMF PortWatch.", idg, fs)
    lab = 150 if largo else 112
    destra = 70 if largo else 50
    out.append(f'<text x="8" y="18" class="t-ink t-b">Chiamate di navi al giorno: ultimi 30 giorni contro un anno prima</text>' if largo else
               f'<text x="8" y="18" class="t-ink t-b">Chiamate di navi, 30 giorni, anno su anno</text>')
    out.append(f'<text x="8" y="34" class="t-faint">IMF PortWatch, dati fino al {esc(data_it(v["porti_it_data"]))} · blu = aumento, magenta = calo</text>')
    tutti = [r[1] for _, g in gruppi for r in g if r[1] is not None]
    lim = max(20, min(80, max(abs(x) for x in tutti) * 1.1)) if tutti else 50
    X = Scala(-lim, lim, 8 + lab, w - destra)
    y = 56
    for titolo, righe in gruppi:
        out.append(f'<text x="8" y="{y + 12}" class="t-ink t-b">{esc(titolo)}</text>')
        y0 = y + 20
        out.append(f'<line x1="{X(0):.1f}" x2="{X(0):.1f}" y1="{y0 - 2}" y2="{y0 + len(righe) * rh}" class="base"/>')
        y = y0
        for nome, vv, m30, m30a in righe:
            bh = 14
            out.append(f'<text x="{8 + lab - 8}" y="{y + bh - 3}" text-anchor="end" class="t-ink">{esc(nome)}</text>')
            if vv is not None:
                vc = max(-lim, min(lim, vv))
                xa, xb = sorted([X(0), X(vc)])
                cls = "f-s3" if vv >= 0 else "f-s1"
                out.append(f'<rect x="{xa:.1f}" y="{y}" width="{max(1, xb - xa):.1f}" height="{bh}" rx="3" class="{cls}"/>')
                tx = X(vc) + (6 if vv >= 0 else -6)
                out.append(f'<text x="{tx:.1f}" y="{y + bh - 3}" text-anchor="{"start" if vv >= 0 else "end"}" class="t-ink num">{pct(vv)}</text>')
            tt = f"{nome}: {num(m30, 1)} chiamate al giorno negli ultimi 30 giorni, {num(m30a, 1)} un anno prima ({pct(vv)})"
            out.append(f'<rect x="0" y="{y - 4}" width="{w}" height="{rh}" class="hit"><title>{esc(tt)}</title></rect>')
            y += rh
        y += 6
    out.append("</svg>")
    return "\n".join(out)


def indicatori_cruscotto(v):
    cp, nl, pz, sc = v["cp"], v["noli"], v["pz"], v["sc"]
    out = []
    # transiti: stato con le soglie del metodo del cruscotto del rischio (stesso riferimento di rischio.json)
    for uid, nome_s, titolo in (("hormuz", "Stretto di Hormuz", "Hormuz, transiti"), ("bab-el-mandeb", "Bab el-Mandeb", "Bab el-Mandeb, transiti"),
                                ("stretti-danesi", "Stretti danesi", "Stretti danesi, transiti")):
        e, fr = cp.get(nome_s), flusso_rischio(v, uid)
        if not (e and fr):
            continue
        out.append({"nome": titolo, "valore": num(e["media7"]["n_total"], 1), "unita": "navi/giorno (7 gg)",
                    "delta": fr["valore"], "delta_txt": "sul riferimento",
                    "stato": stato_flussi(fr["valore"]), "data": e["ultima_data"], "fonte": "IMF PortWatch"})
    if nl.get("fbx"):
        f = nl["fbx"]
        out.append({"nome": "Noli container FBX", "valore": num(f["valore"], 0), "unita": "$ per FEU",
                    "delta": v.get("fbx_var4s"), "delta_txt": "su 4 settimane",
                    "stato": stato("fbx", f["valore"]), "data": f["data"], "fonte": "Freightos"})
    t = pz.get("ttf")
    if t:
        out.append({"nome": "Gas TTF", "valore": num(t["ultimo"], 1), "unita": "€/MWh",
                    "delta": t["var"].get("1a"), "delta_txt": "su un anno",
                    "stato": stato("ttf", t["ultimo"]), "data": t["data"], "fonte": "Yahoo Fin."})
    g = v["sc"].get("gas_stoccaggio_pct_it")
    if g:
        out.append({"nome": "Stoccaggi gas Italia", "valore": num(g["valore"], 1), "unita": "% pieno",
                    "delta_pp": g["anno_scorso"]["variazione"], "delta_txt": "p.p. su un anno",
                    "stato": stato("stoccaggi_it", g["valore"]), "data": g["data"], "fonte": "GIE AGSI+"})
    return out[:6]


def grafico_cruscotto(v, largo=True):
    ind = indicatori_cruscotto(v)
    cols = 3 if largo else 2
    w = 720 if largo else 360
    fs = 12 if largo else 11
    gap = 10
    cw = (w - gap * (cols - 1)) / cols
    ch = 150 if largo else 156
    righe = (len(ind) + cols - 1) // cols
    h = righe * ch + (righe - 1) * gap + 2
    idg = "g-cruscotto" + ("" if largo else "-m")
    out = svg_apri(w, h, "Cruscotto: sei indicatori della supply chain",
                   "Valore, direzione recente e stato (valutazione con soglie dichiarate) di sei indicatori.", idg, fs)
    icone = {"verde": ("f-ok", "●", "verde"), "giallo": ("f-warn", "▲", "giallo"),
             "rosso": ("f-crit", "■", "rosso"), "n.d.": ("t-faint", "○", "n.d.")}
    for i, x in enumerate(ind):
        r, c = divmod(i, cols)
        X0, Y0 = c * (cw + gap) + 1, r * (ch + gap) + 1
        out.append(f'<rect x="{X0:.1f}" y="{Y0:.1f}" width="{cw - 2:.1f}" height="{ch - 2}" rx="8" class="card"/>')
        out.append(f'<text x="{X0 + 12:.1f}" y="{Y0 + 22:.1f}" class="t-ink t-b">{esc(x["nome"])}</text>')
        out.append(f'<text x="{X0 + 12:.1f}" y="{Y0 + 58:.1f}" class="t-ink num t-b" style="font-size:{fs * 2.2:.0f}px">{esc(x["valore"])}</text>')
        out.append(f'<text x="{X0 + 12:.1f}" y="{Y0 + 76:.1f}">{esc(x["unita"])}</text>')
        if "delta_pp" in x:
            dv = x["delta_pp"]
            dtesto = f'{num(dv, 1, True)} {x["delta_txt"]}'
        else:
            dv = x.get("delta")
            dtesto = f'{pct(dv)} {x["delta_txt"]}'
        freccia = "→" if dv is None or abs(dv) < 1 else ("↑" if dv > 0 else "↓")
        out.append(f'<text x="{X0 + 12:.1f}" y="{Y0 + 96:.1f}" class="t-ink"><tspan class="t-b">{freccia}</tspan> <tspan class="num">{esc(dtesto)}</tspan></text>')
        cls, ic, lab = icone[x["stato"]]
        out.append(f'<text x="{X0 + 12:.1f}" y="{Y0 + 118:.1f}"><tspan class="{cls}">{ic}</tspan> <tspan class="t-ink t-b">{lab}</tspan></text>')
        out.append(f'<text x="{X0 + 12:.1f}" y="{Y0 + 138:.1f}" class="t-faint">{esc(data_it(x["data"], anno=False))} · {esc(x["fonte"])}</text>')
        out.append(f'<rect x="{X0:.1f}" y="{Y0:.1f}" width="{cw:.1f}" height="{ch}" class="hit"><title>{esc(x["nome"])}: {esc(x["valore"])} {esc(x["unita"])}; {esc(dtesto)}; stato {lab}</title></rect>')
    out.append("</svg>")
    return "\n".join(out), ind


# =====================================================================================
# Testo del report: blocchi comuni a Markdown e HTML
# blocchi: ("h2", id, titolo) ("p", testo) ("ul", [voci]) ("val", testo) ("tab", intest, righe, nota)
#          ("fig", nome, didascalia)
# testo: **grassetto**, *corsivo*, [testo](link)
# =====================================================================================

def costruisci_blocchi(v, oggi, edizione):
    B = []
    cp, nl, pz, sc, pe = v["cp"], v["noli"], v["pz"], v["sc"], v["paesi"]
    suez, bab, capo, hor = cp["Canale di Suez"], cp["Bab el-Mandeb"], cp["Capo di Buona Speranza"], cp["Stretto di Hormuz"]
    pw_link = "https://portwatch.imf.org/"
    per = v["pw_periodo"]
    fpw = f"{link('IMF PortWatch', pw_link)}, media 7 giorni {data_it(per[0], False)}–{data_it(per[1])}"
    wci, fbx, bdi, scfi, ccfi = nl.get("wci"), nl.get("fbx"), nl.get("bdi"), nl.get("scfi"), nl.get("ccfi")
    brent, ttf, hh = pz.get("brent"), pz.get("ttf"), pz.get("hh")
    git = sc.get("gas_stoccaggio_pct_it")
    gde = sc.get("gas_stoccaggio_pct_de")
    est_wci = FATTI_ESTERNI["wci_anno_prima"]
    gaso = FATTI_ESTERNI["gasolio"]
    it_ports = {e["nome"]: e for e in v["porti_it"]}
    it_rows, ue_rows = righe_porti(v)
    cali_it = [r for r in it_rows if r[1] is not None and r[1] < 0]
    su_it = [r for r in it_rows if r[1] is not None and r[1] > 0]

    # ------------------------------------------------------------- 1. In breve
    B.append(("h2", "in-breve", "1. In breve"))
    voci = []
    pr = v["pre_ratio"]
    voci.append(f"**Suez si riprende, Bab el-Mandeb resta a un terzo, Hormuz è chiuso di fatto.** A Suez passano "
                f"{num(suez['media7']['n_total'], 1)} navi al giorno ({pct(suez['var7_anno_pct']['n_total'])} su un anno), "
                f"{il(num(pr['Canale di Suez'], 0))}% della media gennaio–ottobre 2023; Bab el-Mandeb è a {num(bab['media7']['n_total'], 1)} "
                f"({num(pr['Bab el-Mandeb'], 0)}% di quella media). Hormuz resta a {num(hor['media7']['n_total'], 1)} navi al giorno con AIS acceso "
                f"({fpw}); Lloyd's List Intelligence, che ricostruisce anche i transiti con il transponder spento, conta "
                f"{FATTI_ESTERNI['lli_hormuz']['testo']} ({fonte_est('lli_hormuz')}). "
                f"Nel cruscotto del rischio dell'osservatorio Hormuz è {livello_txt(v, 'hormuz')}, Bab el-Mandeb {livello_txt(v, 'bab-el-mandeb')}, "
                f"Suez {livello_txt(v, 'suez')} (docs/data/rischio.json, {data_it(v['rischio_data'])}; metodo in report/metodo-rischio.md).")
    if wci:
        voci.append(f"**I noli container sono più del doppio di un anno fa.** Il Drewry WCI è a {num(wci['valore'], 0)} dollari per FEU "
                    f"({data_it(wci['data'])}), {pct(v['wci_yoy'])} sul {data_it(est_wci['data'])}; Shanghai–Genova "
                    f"{num(wci['rotte'].get('Shanghai-Genoa'), 0)} dollari ({pct(v['wci_rotte_yoy'].get('Shanghai-Genoa'))}). "
                    + (f"Il trend recente è piatto: FBX globale {pct(v['fbx_var_inizio'])} {da(data_it(v['fbx_inizio'][0], anno=False))}, "
                       f"{pct(v['fbx_var4s'])} nelle ultime 4 settimane." if v.get("fbx_var4s") is not None else ""))
    if cali_it:
        peggiori = sorted(cali_it, key=lambda r: r[1])[:2]
        voci.append(f"**Porti italiani a due velocità.** Negli ultimi 30 giorni calano soprattutto "
                    + " e ".join(f"{nome_porto(r[0])} ({pct(r[1])})" for r in peggiori)
                    + ", porti dell'energia e delle rinfuse; calano poco i porti container ("
                    + ", ".join(f"{nome_porto(n_)} {pct(it_ports[n_]['var30_anno_pct'])}" for n_ in ("Genova", "Gioia Tauro") if n_ in it_ports) + ")"
                    + (f" e cresce {nome_porto(su_it[0][0])} ({pct(su_it[0][1])}, ma su numeri piccoli)" if su_it else "")
                    + f" (chiamate di navi, 30 giorni su un anno, {link('IMF PortWatch', pw_link)}, dati fino al {data_it(v['porti_it_data'])}).")
    if ttf and git:
        voci.append(f"**L'energia resta il costo più pesante.** Gas TTF a {num(ttf['ultimo'], 2)} €/MWh ({pct(ttf['var']['1a'])} su un anno), "
                    f"gasolio self a {num(gaso['self'], 3)} €/litro ({fonte_est('gasolio')}) e taglio delle accise scaduto l'8 novembre; "
                    f"stoccaggi gas italiani {al(num(git['valore'], 1))}% contro {il(num(gde['valore'], 1)) if gde else 'n.d.'}% della Germania (GIE AGSI+, {data_it(git['data'])}).")
    sdn = cp.get("Stretti danesi")
    gnl_ = sc.get("gas_stoccaggio_pct_nl")
    f11 = (fbx or {}).get("rotte", {}).get("FBX11")
    f13 = (fbx or {}).get("rotte", {}).get("FBX13")
    if sdn and gnl_ and gde and f11 and f13:
        voci.append(f"**Nord Europa: meno esposto sui noli, più esposto sul gas.** La rotta Cina–Nord Europa costa "
                    f"{num(f11['valore'], 0)} dollari per FEU contro {num(f13['valore'], 0)} verso il Mediterraneo (Freightos FBX, {data_it(fbx['data'])}); "
                    f"gli stoccaggi di gas sono {al(num(gnl_['valore'], 1))}% nei Paesi Bassi e {al(num(gde['valore'], 1))}% in Germania, "
                    f"{num(-gnl_['media_5_anni']['scarto'], 1)} e {num(-gde['media_5_anni']['scarto'], 1)} punti sotto la media di 5 anni (GIE AGSI+, {data_it(gde['data'])}); "
                    f"agli Stretti danesi passano {num(sdn['media7']['n_total'], 1)} navi al giorno, {pct(sdn['var7_anno_pct']['n_total'])} su un anno "
                    f"({link('IMF PortWatch', pw_link)}). Dettagli nella sezione 8.")
    voci.append(f"**Il rischio di questa settimana è sulle materie critiche:** {FATTI_ESTERNI['terre_rare']['testo']} ({fonte_est('terre_rare')}).")
    B.append(("ul", voci))
    B.append(("val", "La supply chain europea di novembre 2026 ha due velocità. I container tornano verso Suez e i noli spot "
              "non salgono più ma restano circa il doppio di un anno fa, mentre energia, fertilizzanti e materie critiche restano legati a Hormuz e alla Cina. "
              "Per l'Italia il rischio più concreto nei prossimi due mesi non è logistico ma di costo: gas, gasolio ed "
              "elettricità in inverno con stoccaggi europei bassi."))

    # ------------------------------------------------------------- 2. Rotte marittime
    B.append(("h2", "rotte", "2. Rotte marittime: stretti e noli"))
    B.append(("h3", "Transiti negli stretti"))
    righe = []
    for nome in ("Canale di Suez", "Bab el-Mandeb", "Capo di Buona Speranza", "Stretto di Hormuz", "Stretto di Gibilterra",
                 "Bosforo", "Stretti danesi", "Stretto di Malacca", "Canale di Panama", "Stretto di Kerch"):
        e = cp.get(nome)
        if not e:
            continue
        righe.append([nome, num(e["media7"]["n_total"], 1), num(e["media7"]["n_tanker"], 1), num(e["media7"]["n_container"], 1),
                      pct(e["var7_anno_pct"]["n_total"]), pct(e["var7_tre_anni_pct"]["n_total"])])
    B.append(("tab", ["Passaggio", "Navi/giorno", "di cui petroliere", "di cui portacontainer", "su 1 anno", "sulla stessa settimana del 2023"],
              righe, f"Fonte: {fpw}. Navi con AIS acceso: chi lo spegne non è contato. La stessa settimana del 2023 (fine ottobre) "
                     f"è prima degli attacchi houthi. Il cruscotto del rischio usa per Suez e Bab el-Mandeb la media gennaio–ottobre 2023 "
                     f"e per Hormuz la media del 2025: le percentuali possono differire di qualche punto."))
    B.append(("fig", "transiti", f"Navi al giorno, media mensile dei mesi completi. Fonte: {link('IMF PortWatch', pw_link)}, "
              f"dati fino al {data_it(v['pw_data'])}. Linee tratteggiate: eventi con fonte nel testo."))
    sm = v["suez_min"]
    cm = v["capo_max"]
    B.append(("p", f"**Fatti.** Prima della crisi del Mar Rosso (media gennaio–ottobre 2023) Suez faceva {num(v['pre_crisi']['Canale di Suez'], 0)} navi al giorno "
              f"e il Capo {num(v['pre_crisi']['Capo di Buona Speranza'], 0)}. Da dicembre 2023 il rapporto si è rovesciato: il minimo mensile di Suez dal 2024 "
              f"è {num(sm[1], 1)} ({mese_it(sm[0])}), il massimo del Capo {num(cm[1], 1)} ({mese_it(cm[0])}). "
              f"Nell'ultima settimana misurata il Capo è a {num(capo['media7']['n_total'], 1)} navi al giorno, {il(num(v['pre_ratio']['Capo di Buona Speranza'], 0))}% della media gennaio–ottobre 2023 "
              f"({fpw})."))
    bt = v["voce"]("suez", "flussi", "Container")
    nt = v["voce"]("suez", "flussi", "Navi in totale")
    extra = []
    if bt:
        extra.append(f"capacità container: {bt['valore']} ({link(bt['fonte'], bt['link'])})")
    if nt:
        extra.append(f"transiti: {nt['valore']} ({link(nt['fonte'], nt['link'])})")
    if extra:
        B.append(("p", "Altre fonti confermano il ritorno a Suez delle portacontainer: " + "; ".join(extra) + "."))
    cap = v["voce"]("suez", "alternative", "Capo di Buona Speranza")
    afr = v["voce"]("bab-el-mandeb", "impatti_mercato", "Costo per viaggio")
    if cap or afr:
        t = "**Tempi e costi della deviazione via Capo.** "
        if cap:
            t += f"Rispetto a Suez: {cap['valore']} ({link(cap['fonte'], cap['link'])}). "
        if afr:
            t += f"Per una petroliera: {afr['valore']} ({link(afr['fonte'], afr['link'])})."
        B.append(("p", t))
    sb = v["schede"].get("bab-el-mandeb", {}).get("stato_attuale", {})
    fatti_bab = [f for f in sb.get("fatti", [])][:2]
    if fatti_bab:
        B.append(("p", "**Stato di Bab el-Mandeb.** " + " ".join(f"{f['testo']} ({link(fonte_breve(f['fonte']), f['link'])}, {data_it(f['data'])})." for f in fatti_bab)))
    B.append(("val", "Il ritorno a Suez è reale ma parziale e fragile. Le portacontainer rientrano, mentre il greggio saudita "
              "che esce da Yanbu rende Bab el-Mandeb un «secondo Hormuz»: un attacco riuscito a una petroliera "
              "riporterebbe le navi sul Capo in pochi giorni. Il dato da guardare è Bab el-Mandeb, non Suez."))

    B.append(("h3", "Noli container e rinfuse"))
    rn = []
    if wci:
        rn.append(["Drewry WCI composito", f"{num(wci['valore'], 0)} $/FEU", data_tab(wci["data"]),
                   f"{pct(v['wci_yoy'])} su un anno (a)", link("Drewry", wci["link"])])
        for k, nome in (("Shanghai-Genoa", "WCI Shanghai–Genova"), ("Shanghai-Rotterdam", "WCI Shanghai–Rotterdam")):
            if k in wci["rotte"]:
                rn.append([nome, f"{num(wci['rotte'][k], 0)} $/FEU", data_tab(wci["data"]),
                           f"{pct(v['wci_rotte_yoy'].get(k))} su un anno (a)", link("Drewry", wci["link"])])
    if fbx:
        rn.append(["Freightos FBX globale", f"{num(fbx['valore'], 0)} $/FEU", data_tab(fbx["data"]),
                   f"{pct(v.get('fbx_var4s'))} su 4 settimane", link("Freightos", fbx["link"])])
        for k, nome in (("FBX13", "FBX Cina–Mediterraneo"), ("FBX11", "FBX Cina–Nord Europa")):
            r = fbx.get("rotte", {}).get(k)
            if r:
                rn.append([nome, f"{num(r['valore'], 0)} $/FEU", data_tab(fbx["data"]), f"{r['var'].replace('.', ',')} sulla settimana",
                           link("Freightos", fbx["link"])])
    if scfi:
        rn.append(["SCFI (Shanghai, composito)", f"{num(scfi['valore'], 2)} punti", data_tab(scfi["data"]),
                   f"{pct(scfi.get('var_pct'), 1)} sulla settimana", link("SSE", scfi["link"])])
    if ccfi:
        med = ccfi.get("rotte", {}).get("MEDITERRANEAN")
        rn.append(["CCFI (Cina, composito)", f"{num(ccfi['valore'], 2)} punti", data_tab(ccfi["data"]),
                   f"{pct(ccfi.get('var_pct'), 1)} sulla settimana", link("SSE", ccfi["link"])])
        if med:
            rn.append(["CCFI rotta Mediterraneo", f"{num(med['valore'], 2)} punti", data_tab(ccfi["data"]),
                       f"{pct(med['var_pct'], 1)} sulla settimana", link("SSE", ccfi["link"])])
    eb = FATTI_ESTERNI["bdi"]
    if bdi:  # se un giorno il Baltic Dry torna in noli.json
        rn.append(["Baltic Dry Index (rinfuse)", f"{num(bdi['valore'], 0)} punti", data_tab(bdi["data"]),
                   f"{pct(bdi.get('var_anno_pct'))} su un anno", link("fonte", bdi["link"])])
    else:
        rn.append(["Baltic Dry Index (rinfuse) (b)", f"{num(eb['valore'], 0)} punti", data_tab(eb["data"]),
                   f"{pct(eb['var_giorno_pct'], 1)} sul giorno", link("Baltic Exchange via Trading Economics", eb["link"])])
    B.append(("tab", ["Indice", "Valore", "Data", "Variazione", "Fonte"], rn,
              f"Container: valori da docs/data/noli.json. (a) Variazione su un anno calcolata sul WCI del {data_it(est_wci['data'])} "
              f"({fonte_est('wci_anno_prima')}, affidabilità media). (b) Il Baltic Dry non è più raccolto in automatico dall'osservatorio "
              f"(termini d'uso di Trading Economics): è citato a mano, un solo valore, senza serie e senza variazione su un anno verificata "
              f"({fonte_est('bdi')}, affidabilità media)."))
    B.append(("fig", "noli", f"Sopra: Freightos FBX globale, serie settimanale disponibile gratis ({link('Freightos', fbx['link']) if fbx else 'n.d.'}). "
              f"Sotto: Drewry WCI per rotta al {data_it(wci['data']) if wci else 'n.d.'}; la tacca verticale è il valore di un anno prima "
              f"({fonte_est('wci_anno_prima')})."))
    if fbx and v.get("fbx_max"):
        B.append(("p", f"**Trend.** L'FBX globale è a {num(fbx['valore'], 0)} dollari: {pct(v['fbx_var_inizio'])} {da(data_it(v['fbx_inizio'][0]))} "
                  f"({num(v['fbx_inizio'][1], 0)}), massimo della serie {num(v['fbx_max'][1], 0)} il {data_it(v['fbx_max'][0])}. "
                  + (f"La rotta Cina–Mediterraneo (FBX13, {num(fbx['rotte']['FBX13']['valore'], 0)}) costa più della Cina–Nord Europa "
                     f"(FBX11, {num(fbx['rotte']['FBX11']['valore'], 0)}), come nel WCI Shanghai–Genova contro Shanghai–Rotterdam. "
                     if "FBX13" in fbx.get("rotte", {}) and "FBX11" in fbx.get("rotte", {}) else "")
                  + (f"Lo SCFI scende ({pct(scfi['var_pct'], 1)}) mentre il CCFI, che pesa i contratti, sale ({pct(ccfi['var_pct'], 1)}), "
                     f"con la rotta Mediterraneo a {pct(ccfi['rotte']['MEDITERRANEAN']['var_pct'], 1)} (SSE, {data_it(ccfi['data'])})."
                     if scfi and ccfi and "MEDITERRANEAN" in ccfi.get("rotte", {}) else "")))
    B.append(("p", f"**Rinfuse secche.** Il Baltic Dry è a {num(eb['valore'], 0)} punti il {data_it(eb['data'])}, "
              f"{eb['testo']} ({fonte_est('bdi')}, citato a mano, affidabilità media). Senza una serie non si può dire "
              f"se le rinfuse vadano nella stessa direzione dei container."))
    B.append(("val", "Due forze opposte sui noli container: il ritorno a Suez libera navi (ribassista, ed è quello che si vede "
              "nell'FBX) mentre il premio di guerra legato a Hormuz e al Golfo tiene alti i noli verso il Mediterraneo e il "
              "Medio Oriente. Per un importatore italiano lo scenario base è un calo lento, non un ritorno ai livelli di fine 2025."))

    # ------------------------------------------------------------- 3. Porti
    B.append(("h2", "porti", "3. Porti italiani ed europei"))
    rp = []
    for e in v["porti_it"]:
        rp.append([e["nome"], num(e["media7"]["portcalls"], 1), pct(e["var7_anno_pct"]["portcalls"]),
                   num(e["media30"]["portcalls"], 1), pct(e["var30_anno_pct"]),
                   pct(e["var7_anno_pct"].get("portcalls_container")), pct(e["var7_anno_pct"].get("portcalls_tanker"))])
    B.append(("tab", ["Porto", "Chiamate/giorno (7 gg)", "su 1 anno", "Chiamate/giorno (30 gg)", "su 1 anno", "portacontainer 7 gg", "petroliere 7 gg"],
              rp, f"Fonte: {link('IMF PortWatch', pw_link)}, dati fino al {data_it(v['porti_it_data'])}. Sui 7 giorni i numeri sono piccoli: "
              f"la media a 30 giorni è più stabile."))
    if v["porti_ue"]:
        re_ = []
        for e in v["porti_ue"]["elementi"]:
            if e.get("gruppo") != "mediterraneo":
                continue
            re_.append([e["nome"], num(e["media30"]["portcalls"], 1), pct(e["var30_anno_pct"]["portcalls"]),
                        pct(e["var30_anno_pct"].get("portcalls_container")), pct(e["var30_anno_pct"].get("portcalls_tanker"))])
        dfu = v["porti_ue"]["fonti"][0]["data_dato"]
        B.append(("tab", ["Porto (Mediterraneo e Atlantico)", "Chiamate/giorno (30 gg)", "su 1 anno", "portacontainer", "petroliere"], re_,
                  f"Fonte: {link('IMF PortWatch', pw_link)}, dati fino al {data_it(dfu)}, scaricati dallo script del report "
                  f"(report/dati/porti-europei.json) con lo stesso metodo di portwatch.json. I porti del Nord Europa sono nella sezione 8."))
    B.append(("fig", "porti", f"Variazione delle chiamate di navi al giorno, ultimi 30 giorni contro gli stessi giorni di un anno prima. "
              f"Fonte: {link('IMF PortWatch', pw_link)}."))
    gen, gt, tri, rav = it_ports.get("Genova"), it_ports.get("Gioia Tauro"), it_ports.get("Trieste"), it_ports.get("Ravenna")
    t = "**Fatti.** "
    if rav:
        t += (f"Ravenna fa {num(rav['media30']['portcalls'], 1)} chiamate al giorno in 30 giorni ({pct(rav['var30_anno_pct'])}), con import stimato "
              f"{pct(var(rav['media30']['import'], rav['media30_anno_prima']['import']))}. ")
    if tri:
        t += (f"Trieste, porto del greggio per l'oleodotto TAL verso Austria e Germania, è a {pct(tri['var30_anno_pct'])}, "
              f"petroliere {pct(tri['var7_anno_pct']['portcalls_tanker'])} sui 7 giorni. ")
    if gen and gt:
        t += (f"I porti container tengono: Genova {pct(gen['var30_anno_pct'])} sulle chiamate ma portacontainer {pct(gen['var7_anno_pct']['portcalls_container'])} "
              f"e import stimato {pct(gen['var7_anno_pct']['import'])} sui 7 giorni; Gioia Tauro, primo porto di trasbordo, portacontainer "
              f"{pct(gt['var7_anno_pct']['portcalls_container'])}. ")
    B.append(("p", t + f"({link('IMF PortWatch', pw_link)})."))
    B.append(("p", f"Su base annua: {FATTI_ESTERNI['porti_it_2026']['testo']} ({fonte_est('porti_it_2026')}); "
              f"{FATTI_ESTERNI['porti_it_t1']['testo']} ({fonte_est('porti_it_t1')})."))
    if ue_rows:
        su = [r for r in ue_rows if r[1] is not None and r[1] > 0]
        giu = [r for r in ue_rows if r[1] is not None and r[1] < 0]
        t = "Nel resto del Mediterraneo e sull'Atlantico"
        if su:
            t += " crescono " + ", ".join(f"{r[0]} ({pct(r[1])})" for r in su[:3])
        if giu:
            t += ("; calano " if su else " calano ") + ", ".join(f"{r[0]} ({pct(r[1])})" for r in sorted(giu, key=lambda r: r[1])[:3])
        B.append(("p", t + f" (chiamate al giorno, 30 giorni su un anno, {link('IMF PortWatch', pw_link)})."))
    gq = pe["IT"]["indicatori"]["quota_greggio_golfo_persico"]["valore"]
    B.append(("val", "I cali più forti sono nei porti italiani legati all'energia e alle rinfuse dell'Adriatico (Ravenna, "
              "Venezia, Trieste). Hormuz da solo li spiega poco: dal Golfo Persico arriva solo "
              f"{il(num(gq['min_pct'], 1))}–{num(gq['max_pct'], 1)}% del greggio importato dall'Italia (UN Comtrade 2025); più probabili "
              "la domanda industriale debole e l'energia cara, ma i dati PortWatch non permettono di dirlo. Genova e Gioia Tauro "
              "vedono più portacontainer sui 7 giorni, coerente con il ritorno a Suez, ma sui 30 giorni le chiamate totali restano "
              "sotto l'anno scorso. Le chiamate contano le navi, non le tonnellate né i TEU: per i volumi servono i dati delle "
              "Autorità di sistema portuale, che escono con mesi di ritardo."))

    # ------------------------------------------------------------- 4. Ferrovie
    B.append(("h2", "ferrovie", "4. Ferrovie e corridoi terrestri"))
    rf = []
    for cid in ("FR-COR-01", "FR-COR-02", "FR-COR-03", "FR-COR-04"):
        c = v["corridoi"].get(cid)
        if not c:
            continue
        vol = c.get("volumi") or []
        if vol:
            x = vol[0]
            rf.append([c["nome"].split("(")[0].strip(), f"{num_auto(x['valore'])} {x['unita']} ({x['anno']})",
                       x.get("trend", ""), c["stato"].split(";")[0], link(x["fonte"], x["link"])])
        else:
            rf.append([c["nome"].split("(")[0].strip(), "dato mancante", "", c["stato"].split(";")[0], "ferrovie.json"])
    B.append(("tab", ["Corridoio", "Volume", "Andamento", "Stato", "Fonte"], rf, "Fonte: docs/data/ferrovie.json (schede curate con fonte per ogni voce)."))
    ce = v["corridoi"].get("FR-COR-01", {})
    t1 = next((x for x in ce.get("volumi", []) if "2026" in x["anno"]), None)
    if t1:
        periodo = re.sub(r"^(\d{4}) T(\d)$", r"\2° trimestre \1", t1["anno"])
        B.append(("p", f"**Fatti.** Ferrovia Cina–Europa: {num(t1['valore'], 0)} treni nel {periodo}, {t1['trend']} ({link(t1['fonte'], t1['link'])}). "
                  f"Il ramo occidentale dell'INSTC aspetta ancora il tratto Rasht–Astara: "
                  + next((f"avvio lavori previsto nel {x['valore']} ({link(x['fonte'], x['link'])})" for x in v["corridoi"].get("FR-COR-03", {}).get("volumi", [])
                          if x["voce"].startswith("avvio")), "data non disponibile") + "."))
    if v.get("settimane_suez"):
        B.append(("p", f"**Ordine di grandezza.** Tutto il traffico Cina–Europa su ferrovia del {v['teu_ce']['anno']} "
                  f"({num(v['teu_ce']['valore'] / 1e6, 2)} milioni di TEU, {link(v['teu_ce']['fonte'], v['teu_ce']['link'])}) equivale a "
                  f"circa {num(v['settimane_suez'], 1)} settimane di container via Suez al ritmo di ottobre 2026 "
                  f"({num(v['suez_teu_sett'], 0)} TEU a settimana, {link(v['suez_teu']['fonte'], v['suez_teu']['link'])}). Calcolo dell'osservatorio."))
    inc = sorted(v["incidenti_ferrovie"], key=lambda e: e.get("data_evento") or "", reverse=True)[:3]
    if inc:
        B.append(("p", "**Rischi sulla rete.** " + " ".join(
            f"{data_it(e['data_evento']) if e.get('data_evento') and len(e['data_evento']) == 10 else e.get('data_evento', '')}: {e['nome']} ({link(fonte_breve(e['fonte']), e['link'])})."
            for e in inc)))
    B.append(("val", "La ferrovia non è un'alternativa al mare per volumi: è un'assicurazione per merci di valore alto e urgenti. "
              "La rotta nord passa da Russia e Bielorussia (rischio sanzioni e confine polacco); il Middle Corridor "
              "cresce ma resta sotto i 5 milioni di tonnellate l'anno con il trasbordo sul Caspio; l'INSTC non sarà "
              "completo prima della fine del decennio. Per l'Italia il peso diretto di questi corridoi è un dato mancante."))

    # ------------------------------------------------------------- 5. Energia
    B.append(("h2", "energia", "5. Energia come input della supply chain"))
    re2 = []
    for k, nome in (("brent", "Brent"), ("ttf", "Gas TTF"), ("hh", "Gas Henry Hub")):
        s = pz.get(k)
        if s:
            re2.append([nome, f"{num(s['ultimo'], 2)} {s['unita']}", data_tab(s["data"]), pct(s["var"].get("1m")), pct(s["var"].get("1a")),
                        "Yahoo Finance (prezzi.json)"])
    re2.append(["Gasolio self, media Italia", f"{num(gaso['self'], 3)} €/litro", data_tab(gaso["data"]), "—",
                f"circa {pct(var(gaso['self'], FATTI_ESTERNI['gasolio_anno_prima']['self']))} (b)", link("Mimit via Affaritaliani", gaso["link"])])
    re2.append(["Elettricità, PUN Italia", "dato mancante", "ottobre 2026", "", "", "le fonti secondarie divergono (vedi sotto)"])
    B.append(("tab", ["Voce", "Ultimo", "Data", "1 mese", "1 anno", "Fonte"], re2,
              f"(b) Gasolio un anno prima: {num(FATTI_ESTERNI['gasolio_anno_prima']['self'], 3)} €/litro, {fonte_est('gasolio_anno_prima')}, affidabilità bassa."))
    q = v["quote_gas"]
    B.append(("p", f"**Gas in Italia.** Negli ultimi 12 mesi i primi ingressi sono " +
              ", ".join(f"{x['nome'].split(' (')[0]} {num(x['quota_ingressi_pct'], 1)}%" for x in q[:4]) +
              f" ({link('ENTSOG', 'https://transparency.entsog.eu/')}, dati Snam fino {al(data_it(v['gas_data']))}). "
              + (f"Ingressi medi a {mese_it(v['ingressi_mese'][0])}: {num(v['ingressi_mese'][1], 0)} GWh al giorno. " if v.get("ingressi_mese") else "")
              + (f"Stoccaggi italiani {al(num(git['valore'], 2))}% {('l' + chr(39)) if apostrofo(data_it(git['data'])) else 'il '}{data_it(git['data'])}, {num(git['anno_scorso']['variazione'], 1, True)} punti su un anno e "
                 f"{num(git['distanza_obiettivo_pp'], 2, True)} punti dall'obiettivo UE del 90% (GIE AGSI+). " if git else "")
              + (f"La Germania è {al(num(gde['valore'], 1))}%, {num(-gde['media_5_anni']['scarto'], 1)} punti sotto la media di 5 anni." if gde else "")))
    B.append(("p", f"**GNL.** Dietro Hormuz c'è {il(num(100 * v['gnl_liq_golfo'] / v['gnl_liq_tot'], 1))}% della capacità mondiale di liquefazione operativa "
              f"({num(v['gnl_liq_golfo'], 1)} su {num(v['gnl_liq_tot'], 0)} Mt/anno); l'Italia ha {num(v['gnl_it_regas'], 1)} Mt/anno di rigassificazione operativa "
              f"({link('Global Energy Monitor', 'https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/')}, file di {data_breve(v['gnl_data'][:7])}). "
              + (lambda f: f"Nel 2025 il GNL italiano veniva per {il(num(f[0]['quota_pct'], 1))}% dagli Stati Uniti e per {il(num(f[1]['quota_pct'], 1))}% dal Qatar "
                 f"({link('UN Comtrade', pe['IT']['indicatori']['fornitori_gnl']['link'])}, quote sul valore)." )(pe["IT"]["indicatori"]["fornitori_gnl"]["valore"])))
    dist = sc.get("petrolio_usa_distillati")
    emer = sc.get("petrolio_emergenza_giorni_it")
    t = "**Gasolio e scorte.** "
    t += f"{maiuscola(FATTI_ESTERNI['accise_gasolio']['testo'])} ({fonte_est('accise_gasolio')}). "
    if dist:
        t += (f"Le scorte di distillati USA, riferimento per il mercato atlantico del gasolio, sono a {num(dist['valore'], 1)} milioni di barili, "
              f"{pct(dist['media_5_anni']['scarto_pct'], 1)} sulla media di 5 anni (EIA, {data_it(dist['data'])}). ")
    if emer:
        t += (f"Le scorte petrolifere di emergenza italiane sono a {num(emer['valore'], 1)} giorni ({mese_it(emer['data'][:7])}), contro {num(emer['anno_scorso']['valore'], 1)} "
              f"un anno prima (Eurostat).")
    B.append(("p", t))
    B.append(("p", "**Elettricità: dato mancante.** Nessun file dell'osservatorio contiene il PUN e le fonti secondarie trovate per "
              "ottobre 2026 non sono coerenti tra loro (una media parziale di Selectra intorno a 389 €/MWh e un dato di Comparasemplice di "
              "216 €/MWh, con definizioni diverse). Il dato va preso dal GME: "
              + link("mercatoelettrico.org", "https://www.mercatoelettrico.org/") + "."))
    B.append(("val", "Il gas è l'input che lega tutto: fa il prezzo dell'elettricità, dei fertilizzanti azotati e di parte della "
              "chimica. Con il TTF sopra 80 €/MWh e gli stoccaggi del nord Europa molto sotto la norma, il rischio di prezzo "
              "per l'industria italiana resta alto fino a marzo 2027, anche se i volumi italiani sono coperti da Algeria, TAP e GNL americano."))

    # ------------------------------------------------------------- 6. Materie critiche
    B.append(("h2", "materie", "6. Materie critiche e colli di bottiglia"))
    B.append(("p", f"**Terre rare.** {maiuscola(FATTI_ESTERNI['terre_rare']['testo'])} ({fonte_est('terre_rare')}). "
              f"Per l'UE la dipendenza è quasi totale: {FATTI_ESTERNI['crm_ue']['testo']} ({fonte_est('crm_ue')})."))
    sox, tsm = pz.get("sox"), pz.get("tsm")
    B.append(("p", f"**Chip e AI.** {maiuscola(FATTI_ESTERNI['dram']['testo'])} ({fonte_est('dram')}). "
              + (f"In borsa l'indice dei semiconduttori SOX è a {num(sox['ultimo'], 0)} punti, {pct(sox['var']['1m'])} in un mese ma {pct(sox['var']['ytd'])} da inizio anno; "
                 f"TSMC {pct(tsm['var']['1m'])} in un mese (Yahoo Finance, {data_it(sox['data'])}). " if sox and tsm else "")
              + (lambda x: f"Lo Stretto di Taiwan: {x['valore']} ({link(x['fonte'], x['link'])})." if x else "")(v["voce"]("taiwan", "flussi", "Semiconduttori"))))
    u1 = v["voce"]("hormuz", "flussi", "Urea")
    u2 = v["voce"]("hormuz", "impatti_mercato", "Fertilizzanti")
    u3 = v["voce"]("hormuz", "impatti_mercato", "Export di fertilizzanti")
    t = "**Fertilizzanti.** "
    if u1:
        t += f"Da Hormuz passava {u1['valore']} ({link(fonte_breve(u1['fonte']), u1['link'])}); {FATTI_ESTERNI['urea_sp']['testo']} ({fonte_est('urea_sp')}). "
    if u2:
        t += f"Prezzi: {u2['valore']} ({link(fonte_breve(u2['fonte']), u2['link'])}). "
    if u3:
        t += f"Export di fertilizzanti del Medio Oriente: {u3['valore']} ({link(fonte_breve(u3['fonte']), u3['link'])}, {u3['anno']})."
    B.append(("p", t))
    gw, geu, gru = sc.get("grano_scorte_finali_wd"), sc.get("grano_scorte_finali_eu"), sc.get("grano_scorte_finali_ru")
    gk = v["voce"]("stretti-turchi", "impatti_mercato", "Grano ucraino")
    t = "**Grano.** "
    if gw and geu:
        t += (f"USDA stima scorte finali mondiali 2026/27 a {num(gw['valore'], 1)} milioni di tonnellate ({pct(gw['anno_scorso']['variazione_pct'], 1)}), "
              f"ma l'UE scende a {num(geu['valore'], 1)} ({pct(geu['anno_scorso']['variazione_pct'], 0)}), con scorte pari {al(num(geu['rapporto_scorte_consumo_pct'], 0))}% del consumo; "
              f"la Russia sale a {num(gru['valore'], 1)} (USDA PSD). " if gru else "")
    if gk:
        t += f"Ucraina: {gk['valore']} ({link(fonte_breve(gk['fonte']), gk['link'])}). "
    kerch = v["schede"].get("kerch", {}).get("stato_attuale", {}).get("fatti", [])
    if kerch:
        t += f"Kerch, ultimo aggiornamento: {kerch[-1]['testo'][:1].lower() + kerch[-1]['testo'][1:]} ({link(fonte_breve(kerch[-1]['fonte']), kerch[-1]['link'])})."
    B.append(("p", t))
    it = pe["IT"]["indicatori"]
    cn = next((x for x in it["partner_import"]["valore"] if x["paese"] == "CN"), None)
    B.append(("p", f"**Dipendenze dell'Italia.** L'Italia importa {il(num(it['dipendenza_gas']['valore'], 1))}% del gas e {il(num(it['dipendenza_petrolio']['valore'], 1))}% "
              f"del petrolio che consuma ({link('Eurostat', it['dipendenza_gas']['link'])}, {it['dipendenza_gas']['anno']}). "
              + (f"La Cina è il secondo fornitore di merci con {il(num(cn['quota_pct'], 1))}% delle importazioni ({link('UN Comtrade', it['partner_import']['link'])}, {it['partner_import']['anno']}). " if cn else "")
              + f"Il greggio arriva soprattutto da " + ", ".join(f"{x['nome']} ({num(x['quota_pct'], 1)}%)" for x in it["fornitori_greggio"]["valore"][:3])
              + f"; dal Golfo Persico solo {il(num(it['quota_greggio_golfo_persico']['valore']['min_pct'], 1))}–{num(it['quota_greggio_golfo_persico']['valore']['max_pct'], 1)}% "
              f"(UN Comtrade {it['fornitori_greggio']['anno']}). Mancano i dati per minerali e componenti: "
              + ("i file commercio.json e minerali.json non esistono ancora." if v["mancanti"] else "vedi commercio.json e minerali.json.")))
    B.append(("val", "I colli di bottiglia di fine 2026 non sono tutti in mare. Le terre rare (decisione cinese attesa il 10 "
              "novembre) e le memorie per l'auto (capacità assorbita dall'AI) possono fermare linee produttive europee più di "
              "un nolo alto. Per i fertilizzanti il problema è il gas caro in Europa più che la logistica. Sul grano l'UE ha "
              "il cuscinetto più sottile da anni."))

    # ------------------------------------------------------------- 7. Rischi
    B.append(("h2", "rischi", "7. Rischi digitali e fisici"))
    rc = v["cavi_riep"]
    inc = v["incidenti_cavi"]
    n26 = sum(1 for e in inc if e["data_evento"].startswith(str(oggi.year)))
    B.append(("p", f"**Cavi sottomarini.** L'Italia ha {rc['italia']['cavi']} cavi e {rc['italia']['approdi']} approdi; i cavi attivi che la collegano all'Asia passando da "
              f"Bab el-Mandeb sono {len(v['cavi_it_asia'])} ({', '.join(v['cavi_it_asia'])}). Nel Mar Rosso passano {rc['cavi_per_passaggio'].get('Mar Rosso')} cavi, "
              f"nel Baltico {rc['cavi_per_passaggio'].get('Mar Baltico')} ({link('TeleGeography', 'https://www.submarinecablemap.com/')}, CC BY-NC-SA, {data_it(v['cavi_data'])}). "
              f"L'osservatorio registra {len(inc)} incidenti dal {min(e['data_evento'] for e in inc)[:4]}, {n26} nel {oggi.year}; l'ultimo: "
              + (lambda e: f"{e['nome']} ({data_it(e['data_evento'])}, {link(fonte_breve(e['fonte']), e['link'])}).")(max(inc, key=lambda e: e['data_evento']))))
    ib = v["ibrido"]
    fr = [e for e in ib if e["categoria"] == "attacco-informatico" and "frigorifer" in e["nome"].lower()]
    gn = [e for e in ib if e["categoria"] == "disturbo-gnss"]
    sab = [e for e in ib if e["categoria"] == "sabotaggio" and "starlink" in e["nome"].lower()]
    t = "**Sabotaggi e attacchi informatici alla logistica.** "
    if fr:
        t += "La catena del freddo è il bersaglio nuovo: " + "; ".join(f"{e['nome'][:1].lower() + e['nome'][1:]} ({data_it(e['data_evento'])}, {link(fonte_breve(e['fonte']), e['link'])})" for e in fr) + ". "
    if sab:
        t += (f"Tre attacchi a stazioni Starlink in Europa centro-orientale tra settembre e ottobre ({', '.join(e['paese'] for e in sab)}): "
              f"il premier lituano li collega e li attribuisce alla Russia, come il governo polacco per l'impianto in Polonia "
              f"(attribuzioni politiche, senza sentenze; ibrido.json). ")
    noname = next((e for e in ib if e["id"] == "IB-20261107-12"), None)
    if noname:
        t += (f"In Italia NoName057(16) ha rivendicato DDoS anche contro Terminal Container Ravenna e Interporto Padova a metà ottobre, senza conferma delle vittime "
              f"({link('QN', noname['link'])}).")
    B.append(("p", t))
    t = "**GNSS jamming.** "
    if gn:
        e = gn[0]
        t += f"{e['nome']} ({data_it(e['data_evento'])}, {link(fonte_breve(e['fonte']), e['link'])}, affidabilità {e['affidabilita']}). "
    t += f"Nel Golfo: {FATTI_ESTERNI['gnss_golfo']['testo']} ({fonte_est('gnss_golfo')}). "
    if v["navi_spoof"]:
        t += (f"Nei dati AIS dell'osservatorio {len(v['navi_spoof'])} navi risultano con posizioni impossibili (oltre 40 nodi o nell'entroterra), "
              f"segno di spoofing o disturbo (navi.json, {data_it(v['navi_agg'])}).")
    B.append(("p", t))
    s = v["sanz"]
    gf = v["navi_aree"].get("Golfo di Finlandia", {})
    B.append(("p", f"**Flotta ombra.** {num(s['navi_totali'], 0)} navi sono sanzionate da USA, Regno Unito o UE ({s['ambito_russia']} legate alla Russia, "
              f"{s['ambito_iran']} all'Iran); {num(s['flotta_ombra_probabile'], 0)} sono valutate «flotta ombra probabile» dall'osservatorio "
              f"(OFAC, FCDO, OpenSanctions, liste al {data_it(v['sanz_data'])}). "
              + (f"Nel Golfo di Finlandia {gf.get('sanzionate')} delle {gf.get('petroliere_viste')} petroliere viste con AIS sono sanzionate "
                 f"(Digitraffic e aisstream, {data_it(v['navi_agg'])})." if gf else "")))
    B.append(("val", "Il rischio fisico più probabile per l'Italia non è un taglio dei cavi nel Mediterraneo ma un incidente nel "
              "Mar Rosso (ancore di navi colpite, come nel 2024) che degrada la capacità verso Asia e Golfo, con riparazioni "
              "lente in zona di guerra. Il rischio nuovo per la logistica europea sono gli attacchi informatici ai sistemi "
              "di controllo (refrigerazione, terminal) e il disturbo GNSS nel Baltico e nel Golfo, che rende meno affidabili "
              "i dati AIS su cui si basano anche questi numeri."))

    # ------------------------------------------------------------- 8. Nord Europa
    B += blocchi_nord(v, pw_link)

    # ------------------------------------------------------------- 9. Indicatori
    B.append(("h2", "indicatori", "9. Indicatori da seguire nelle prossime settimane"))
    B.append(("p", "Due letture affiancate. **Flussi negli stretti:** stessi riferimenti e stesse soglie del cruscotto del rischio "
              "(report/metodo-rischio.md): verde se il calo sul riferimento è entro il 10%, giallo tra −10% e −30%, rosso oltre −30%; "
              "sotto −50% il metodo considera la disruption in corso. **Prezzi, noli, gasolio e stoccaggi:** il report usa soglie di "
              "*livello*, cioè quanto costa oggi a chi importa o trasporta; il cruscotto del rischio misura invece le *variazioni* "
              "(contro la media di 90 giorni e contro un anno prima). Per questo un prezzo può essere rosso qui e verde nel cruscotto: "
              "alto, ma non in salita. La colonna «Cruscotto del rischio» riporta la lettura del metodo dove esiste."))
    B.append(("val", "Le soglie di livello sono una **valutazione dell'osservatorio**, non soglie ufficiali: servono a dire quando "
              "un dato cambia il quadro. Brent 85 $, TTF 70 € e WCI Shanghai–Genova 5.000 $ coincidono con le soglie degli scenari "
              "del report «Hormuz e Mar Rosso». Lo stato è ricalcolato dallo script a ogni edizione."))
    B.append(("fig", "cruscotto", "Cruscotto: valore, direzione recente e stato. Transiti con le soglie del metodo del cruscotto del rischio, "
              "prezzi e stoccaggi con le soglie di livello della tabella qui sotto. ● verde, ▲ giallo, ■ rosso. Fonti e date nei singoli riquadri."))
    ri = []

    def ind_rischio(uid, prefisso):
        u = unita_rischio(v, uid)
        for i in (u or {}).get("indicatori", []):
            if i.get("nome", "").startswith(prefisso):
                return i
        return None

    def lettura(i, testo):
        return f"{i['stato']}: {pct(i['valore'], 1)} {testo}" if i else "n.d."

    for uid, nome_s, nome_r in (("hormuz", "Stretto di Hormuz", "Hormuz"), ("bab-el-mandeb", "Bab el-Mandeb", "Bab el-Mandeb"),
                                ("suez", "Canale di Suez", "Suez"), ("stretti-danesi", "Stretti danesi", "Stretti danesi")):
        fr = flusso_rischio(v, uid)
        e = cp.get(nome_s)
        if not (fr and e):
            continue
        ri.append([f"{nome_r}, navi/giorno (7 gg)", f"{num(e['media7']['n_total'], 1)} ({pct(fr['valore'])} sul riferimento {num(fr['riferimento'], 1)})",
                   data_tab(e["ultima_data"]), "metodo: −10% / −30% sul riferimento", stato_flussi(fr["valore"]),
                   f"{unita_rischio(v, uid)['livello']} ({num(unita_rischio(v, uid)['punteggio'], 1)}/25)", "PortWatch"])

    def riga(nome, val_txt, data_s, chiave, valore_stato, soglia_txt, crusc, fonte):
        ri.append([nome, val_txt, data_s, soglia_txt, stato(chiave, valore_stato), crusc, fonte])
    if fbx:
        riga("FBX globale, $/FEU", num(fbx["valore"], 0), data_tab(fbx["data"]), "fbx", fbx["valore"], "giallo sopra 2.500, rosso sopra 4.000",
             "—", "Freightos")
    if wci and "Shanghai-Genoa" in wci["rotte"]:
        riga("WCI Shanghai–Genova, $/FEU", num(wci["rotte"]["Shanghai-Genoa"], 0), data_tab(wci["data"]), "wci_genova", wci["rotte"]["Shanghai-Genoa"],
             "giallo sopra 3.000, rosso sopra 5.000", "—", "Drewry")
    if brent:
        riga("Brent, $/barile", num(brent["ultimo"], 2), data_tab(brent["data"]), "brent", brent["ultimo"], "giallo sopra 85, rosso sopra 110",
             lettura(ind_rischio("hormuz", "Petrolio Brent contro la media 90"), "sulla media 90 gg") + "; "
             + lettura(ind_rischio("hormuz", "Petrolio Brent contro un anno"), "su un anno"), "Yahoo Finance")
    if ttf:
        riga("TTF, €/MWh", num(ttf["ultimo"], 2), data_tab(ttf["data"]), "ttf", ttf["ultimo"], "giallo sopra 40, rosso sopra 70",
             lettura(ind_rischio("hormuz", "Gas TTF (Europa) contro la media 90"), "sulla media 90 gg") + "; "
             + lettura(ind_rischio("hormuz", "Gas TTF (Europa) contro un anno"), "su un anno"), "Yahoo Finance")
    if git:
        riga("Stoccaggi gas Italia, %", num(git["valore"], 2), data_tab(git["data"]), "stoccaggi_it", git["valore"], "giallo sotto 90%, rosso sotto 80%",
             lettura(ind_rischio("transmed", "Stoccaggi gas Italia"), "sulla media 5 anni"), "GIE AGSI+")
    riga("Gasolio self Italia, €/litro", num(gaso["self"], 3), data_tab(gaso["data"]), "gasolio", gaso["self"], "giallo sopra 1,90, rosso sopra 2,20",
         "—", "Mimit")
    B.append(("tab", ["Indicatore", "Ultimo", "Data", "Soglie", "Stato", "Cruscotto del rischio", "Fonte"], ri,
              f"Stato calcolato dallo script. Per i transiti la colonna «Cruscotto del rischio» dà il livello dell'unità (probabilità × impatto, "
              f"su 25); per i prezzi lo stato dei singoli indicatori del metodo (docs/data/rischio.json, {data_it(v['rischio_data'])}). "
              f"Riferimenti dei transiti: Hormuz media 2025; Suez e Bab el-Mandeb media gennaio–ottobre 2023; Stretti danesi stessa settimana "
              f"di un anno prima. Prezzi di Yahoo Finance: l'ultimo valore del 9 novembre è provvisorio. Il Baltic Dry è uscito dalla tabella: "
              f"non è più raccolto in automatico. Fonti e link nelle sezioni precedenti."))
    B.append(("p", "**Eventi da seguire** (dal calendario dell'osservatorio e dalle schede degli stretti):"))
    ag = []
    for data_s, titolo, fonte, url in v["agenda"]:
        ag.append(f"{data_it(data_s)}: {titolo} ({link(fonte_breve(fonte), url) if url else fonte})")
    B.append(("ul", ag))
    B.append(("val", "Tre segnali cambierebbero il quadro prima della prossima edizione: (1) la Cina non proroga la sospensione "
              "sulle terre rare; (2) un attacco riuscito a una petroliera a Bab el-Mandeb, che si vedrebbe nei transiti del Capo in "
              "risalita e nell'FBX Cina–Mediterraneo; (3) un'intesa su Hormuz con riapertura verificata dai transiti PortWatch "
              "sopra le 20 navi al giorno, che farebbe scendere TTF e premi di guerra."))

    # ------------------------------------------------------------- 9. Metodo
    B.append(("h2", "metodo", "10. Metodo e limiti"))
    B.append(("p", "**Come è fatto.** Testo, tabelle e grafici sono generati da `report/costruisci_supply_chain.py`, che legge i file "
              "di `docs/data/` del giorno e si può rilanciare ogni mese. I numeri dei dati non sono scritti a mano. I fatti che i file "
              "non contengono (gasolio, terre rare, memorie, GNSS nel Golfo, noli di un anno fa, Baltic Dry, traffico annuo dei porti) sono in una "
              "tabella dello script con fonte, link, data e affidabilità, e lo script avvisa quando invecchiano. Le parti marcate "
              "*Valutazione* sono ragionamenti dell'osservatorio sulle fonti citate, non fatti."))
    rf = []
    for nome, dd in v["file_letti"]:
        if dd is None:
            continue
        agg = dd.get("aggiornato", "")
        rf.append([nome, str(agg)[:16].replace("T", " ")])
    if v["porti_ue"]:
        rf.append(["report/dati/porti-europei.json", v["porti_ue"]["aggiornato"][:16].replace("T", " ")])
    B.append(("tab", ["File letto", "Aggiornato (UTC)"], rf, ""))
    lim = [
        "PortWatch conta solo le navi con AIS acceso, con circa una settimana di ritardo: a Hormuz e nel Mar Nero i transiti «dark» sfuggono (Lloyd's List Intelligence conta molti più transiti a Hormuz).",
        "Le chiamate nei porti contano le navi, non le tonnellate né i TEU; sui 7 giorni i numeri sono piccoli e oscillano.",
        "I noli non hanno serie storiche gratuite: il confronto su un anno del WCI usa un valore ripreso da una fonte secondaria. Il Baltic Dry non è più raccolto in automatico (termini d'uso di Trading Economics): è citato a mano, un solo valore, senza variazione su un anno.",
        "Prezzi (Brent, TTF, Henry Hub, borsa): future da Yahoo Finance, non prezzi ufficiali; l'osservatorio pubblica solo circa 3 mesi di serie, quindi le variazioni a un anno e da inizio anno vengono dal campo «var» calcolato in raccolta e non si possono ricalcolare dal file. L'ultimo valore del giorno di lettura è provvisorio.",
        "Le soglie di livello dei prezzi sono valutazioni; i transiti usano le soglie del metodo del cruscotto del rischio. Hormuz e il GNL del Qatar condividono gli stessi transiti e Brent e TTF compaiono in più unità del cruscotto: i livelli non si sommano.",
        "Le ferrovie sono schede curate a mano: i volumi sono annuali o trimestrali e alcune fonti sono di parte.",
        "Mancano: prezzo dell'elettricità (PUN), volumi Cina–Europa diretti all'Italia, dipendenze italiane per minerale e componente (" + (", ".join(v["mancanti"]) + " non esistono" if v["mancanti"] else "file presenti") + "), prezzi attuali di urea e grano da fonte primaria.",
        "Alcune fonti esterne non sono state aperte (Trading Economics, Motor1, Windward, Riviera, Railmarket): quei fatti sono letti dai risultati di ricerca e marcati con affidabilità media o bassa. Le fonti aperte in revisione sono elencate nel riquadro finale.",
        "La sezione sul Nord Europa usa porti scaricati da PortWatch dallo script del report e i file paesi.json, scorte.json, navi.json e cavi-incidenti.json: per la Danimarca mancano gli indicatori paese (non è in paesi.json).",
    ]
    B.append(("ul", lim))
    return B


def blocchi_nord(v, pw_link):
    """Sezione «Cosa significa per il Nord Europa»: porti del Mare del Nord e del Baltico, Stretti danesi,
    noli verso il Nord Europa, gas, flotta ombra e cavi. Solo numeri dai JSON (porti da report/dati)."""
    B = [("h2", "nord", "8. Cosa significa per il Nord Europa")]
    cp, nl, sc, pe = v["cp"], v["noli"], v["sc"], v["paesi"]
    B.append(("p", "Questa sezione legge gli stessi dati dal punto di vista di chi lavora in un porto o in un'azienda energetica "
              "dei Paesi Bassi, della Danimarca o del Baltico. Il resto del report guarda soprattutto all'Italia."))
    righe = []
    if v["porti_ue"]:
        nord = [e for e in v["porti_ue"]["elementi"] if e.get("gruppo") == "nord"]
        nord.sort(key=lambda e: -(e["media30"]["portcalls"] or 0))
        for e in nord:
            righe.append([f"{e['nome']} ({e['paese']})", num(e["media30"]["portcalls"], 1), pct(e["var30_anno_pct"]["portcalls"]),
                          pct(e["var30_anno_pct"].get("portcalls_container")), pct(e["var30_anno_pct"].get("portcalls_tanker")),
                          pct(e["var30_anno_pct"].get("portcalls_dry_bulk"))])
        if righe:
            B.append(("tab", ["Porto", "Chiamate/giorno (30 gg)", "su 1 anno", "portacontainer", "petroliere", "rinfuse secche"], righe,
                      f"Fonte: {link('IMF PortWatch', pw_link)}, media 30 giorni al {data_it(v['porti_ue']['fonti'][0]['data_dato'])} contro gli "
                      f"stessi giorni di un anno prima (report/dati/porti-europei.json). Chiamate di navi stimate da AIS, non tonnellate né TEU; "
                      f"nei porti piccoli poche navi spostano molto la percentuale."))
            su = [e for e in nord if (e["var30_anno_pct"]["portcalls"] or 0) > 0]
            giu = sorted([e for e in nord if (e["var30_anno_pct"]["portcalls"] or 0) < 0], key=lambda e: e["var30_anno_pct"]["portcalls"])
            t = "**Porti.** "
            if su:
                t += "Crescono " + ", ".join(f"{e['nome']} ({pct(e['var30_anno_pct']['portcalls'])})" for e in su[:4]) + "; "
            if giu:
                t += "calano " + ", ".join(f"{e['nome']} ({pct(e['var30_anno_pct']['portcalls'])})" for e in giu[:3]) + " "
            B.append(("p", t.rstrip("; ") + f" (chiamate al giorno, 30 giorni su un anno, {link('IMF PortWatch', pw_link)})."))
    sdn = cp.get("Stretti danesi")
    t = "**Stretti danesi e Baltico.** "
    if sdn:
        t += (f"Agli Stretti danesi passano {num(sdn['media7']['n_total'], 1)} navi al giorno (di cui {num(sdn['media7']['n_tanker'], 1)} petroliere), "
              f"{pct(sdn['var7_anno_pct']['n_total'])} sulla stessa settimana di un anno prima ({link('IMF PortWatch', pw_link)}, settimana al {data_it(sdn['ultima_data'])}). ")
    if unita_rischio(v, "stretti-danesi") and unita_rischio(v, "baltico"):
        t += (f"Nel cruscotto del rischio gli Stretti danesi sono {livello_txt(v, 'stretti-danesi')} e il Baltico (cavi, condotte, elettrodotti) "
              f"{livello_txt(v, 'baltico')}: flussi in giallo, scorte di gas in rosso (rischio.json). ")
    rc = v["cavi_riep"]
    inc_b = [e for e in v["incidenti_cavi"] if "altic" in json.dumps(e, ensure_ascii=False)]
    if inc_b:
        ult = max(inc_b, key=lambda e: e["data_evento"])
        n_anno = sum(1 for e in inc_b if e["data_evento"].startswith(str(v["oggi"].year)))
        t += (f"Nel Baltico passano {rc['cavi_per_passaggio'].get('Mar Baltico')} cavi (TeleGeography); l'archivio dell'osservatorio conta "
              f"{len(inc_b)} incidenti a cavi e condotte nel Baltico dal {min(e['data_evento'] for e in inc_b)[:4]}, l'ultimo il {data_it(ult['data_evento'])}, "
              f"{'nessuno' if n_anno == 0 else n_anno} nel {v['oggi'].year} (cavi-incidenti.json). ")
    gf = v["navi_aree"].get("Golfo di Finlandia", {})
    sd = v["navi_aree"].get("Stretti danesi", {})
    if gf:
        t += (f"Nel Golfo di Finlandia {gf.get('sanzionate')} delle {gf.get('petroliere_viste')} petroliere viste con AIS sono sanzionate; "
              f"agli Stretti danesi {sd.get('sanzionate', 'n.d.')} su {sd.get('petroliere_viste', 'n.d.')}, ma con una sola fonte AIS gratuita "
              f"(navi.json, {data_it(v['navi_agg'])}).")
    B.append(("p", t))
    fbx, wci = nl.get("fbx"), nl.get("wci")
    t = "**Noli.** "
    if fbx and "FBX11" in fbx.get("rotte", {}) and "FBX13" in fbx.get("rotte", {}):
        f11, f13 = fbx["rotte"]["FBX11"]["valore"], fbx["rotte"]["FBX13"]["valore"]
        t += (f"La rotta Cina–Nord Europa costa {num(f11, 0)} dollari per FEU, {pct(var(f11, f13))} rispetto alla Cina–Mediterraneo "
              f"(Freightos FBX, {data_it(fbx['data'])}). ")
    if wci and "Shanghai-Rotterdam" in wci.get("rotte", {}):
        t += (f"Il WCI Shanghai–Rotterdam è a {num(wci['rotte']['Shanghai-Rotterdam'], 0)} dollari, "
              f"{pct(v['wci_rotte_yoy'].get('Shanghai-Rotterdam'))} su un anno (Drewry, {data_it(wci['data'])}; anno prima da {fonte_est('wci_anno_prima')}).")
    B.append(("p", t))
    gnl_, gde = sc.get("gas_stoccaggio_pct_nl"), sc.get("gas_stoccaggio_pct_de")
    nlp = pe.get("NL", {}).get("indicatori", {})
    t = "**Gas.** "
    if gnl_ and gde:
        t += (f"L'8 novembre gli stoccaggi sono {al(num(gnl_['valore'], 1))}% nei Paesi Bassi ({num(-gnl_['media_5_anni']['scarto'], 1)} punti sotto la media di 5 anni) "
              f"e {al(num(gde['valore'], 1))}% in Germania ({num(-gde['media_5_anni']['scarto'], 1)} punti sotto), contro "
              f"{il(num(sc['gas_stoccaggio_pct_it']['valore'], 1))}% dell'Italia (GIE AGSI+). ")
    if nlp.get("dipendenza_gas") and nlp.get("fornitori_gnl"):
        fg = nlp["fornitori_gnl"]["valore"]
        qg = nlp.get("quota_gnl_golfo_persico", {}).get("valore", {})
        t += (f"I Paesi Bassi importano {il(num(nlp['dipendenza_gas']['valore'], 1))}% del gas che consumano (Eurostat, {nlp['dipendenza_gas']['anno']}); "
              f"il loro GNL nel 2025 veniva per {il(num(fg[0]['quota_pct'], 1))}% da {fg[0]['nome']} e per {il(num(fg[1]['quota_pct'], 1))}% da {fg[1]['nome']}, "
              f"{'per nulla' if qg.get('max_pct') == 0 else 'per ' + num(qg.get('max_pct'), 1) + '%'} dal Golfo Persico "
              f"({link('UN Comtrade', nlp['fornitori_gnl']['link'])}, quote sul valore). ")
    if nlp.get("quota_greggio_golfo_persico"):
        q = nlp["quota_greggio_golfo_persico"]["valore"]
        t += f"Dal Golfo arriva {il(num(q['min_pct'], 1))}–{num(q['max_pct'], 1)}% del greggio importato dai Paesi Bassi (UN Comtrade 2025)."
    B.append(("p", t))
    B.append(("val", "Per un porto del Mare del Nord la crisi di Hormuz arriva più dal prezzo che dai volumi. I noli verso il Nord "
              "Europa costano meno di quelli verso il Mediterraneo e il ritorno a Suez aggiunge capacità sulla rotta Asia–Europa; "
              "il GNL olandese viene quasi tutto dall'Atlantico, non dal Golfo. Il punto debole è il gas: con stoccaggi olandesi e "
              "tedeschi molto sotto la media, il TTF (che si forma proprio in Olanda) resta sensibile a ogni notizia su Qatar e Hormuz "
              "e a un inverno freddo. Per chi opera nel Baltico e negli Stretti danesi il rischio è ibrido: cavi, flotta ombra e "
              "disturbo GNSS, che pesa anche sulle navi che installano e servono i parchi eolici offshore. I dati non dicono "
              "perché calano i transiti agli Stretti danesi: possono pesare il calo dell'export russo, le sanzioni o le navi con AIS spento."))
    return B


# =====================================================================================
# Rendering
# =====================================================================================

def inline_md(t):
    return t


def inline_html(t):
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|[^)\s]+)\)",
               lambda m: f'<a href="{m.group(2)}"' + (' rel="noopener"' if m.group(2).startswith("http") else "") + f'>{m.group(1)}</a>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def render_md(B, meta, figure):
    o = [f"# {meta['titolo']}", "", f"*{meta['sottotitolo']}*", "",
         f"Dati letti il {meta['data_lettura']}. Ogni numero ha fonte e data; le parti marcate *Valutazione* sono ragionamenti dell'osservatorio.", ""]
    o.append("## Indice")
    for b in B:
        if b[0] == "h2":
            o.append(f"- [{b[2]}](#{b[1]})")
    o.append("")
    for b in B:
        k = b[0]
        if k == "h2":
            o += [f'<a id="{b[1]}"></a>', "", f"## {b[2]}", ""]
        elif k == "h3":
            o += [f"### {b[1]}", ""]
        elif k == "p":
            o += [inline_md(b[1]), ""]
        elif k == "val":
            o += [f"> *Valutazione.* {inline_md(b[1])}", ""]
        elif k == "ul":
            o += [f"- {inline_md(x)}" for x in b[1]] + [""]
        elif k == "tab":
            intest, righe, nota = b[1], b[2], b[3]
            o.append("| " + " | ".join(intest) + " |")
            o.append("|" + "|".join("---" for _ in intest) + "|")
            for r in righe:
                o.append("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |")
            o.append("")
            if nota:
                o += [f"<small>{nota}</small>", ""]
        elif k == "fig":
            o += [f"![{b[1]}]({figure[b[1]]})", "", f"<small>{b[2]}</small>", ""]
    o += ["---", "", f"Gabriele Giuliani · Monitor geoeconomico · {meta['edizione_lunga']}", "",
          meta["nota_ai"], ""]
    return "\n".join(o)


CSS = """
:root{--paper:#F6F5F0;--card:#FFFFFF;--ink:#1D272D;--soft:#52606A;--faint:#86929A;--rule:#DCDFDD;--accent:#A61E6B;--band:#ECE9E0;
--ok:#0ca30c;--warn:#fab219;--crit:#d03b3b;color-scheme:light dark}
@media (prefers-color-scheme:dark){:root{--paper:#10181D;--card:#172127;--ink:#DAE0E2;--soft:#A0ABB1;--faint:#6C787F;--rule:#2B373E;--accent:#d14f9a;--band:#1A252C}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 "IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
.pagina{max-width:72ch;margin:0 auto;padding:24px 16px 64px}
.larga{max-width:760px}
a{color:var(--accent);text-underline-offset:2px}
a:hover{text-decoration-thickness:2px}
.torna{display:inline-block;font-size:14px;margin-bottom:24px;text-decoration:none}
.torna:hover{text-decoration:underline}
.occhiello{font:600 13px/1.4 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:0 0 8px}
h1{font:600 clamp(28px,5vw,40px)/1.15 "IBM Plex Serif",Georgia,serif;margin:0 0 12px;letter-spacing:-.01em}
.sottotitolo{font-size:18px;color:var(--soft);margin:0 0 16px}
.meta{font-size:14px;color:var(--soft);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:10px 0;margin:0 0 28px}
h2{font:600 24px/1.25 "IBM Plex Serif",Georgia,serif;margin:48px 0 12px;padding-top:8px;scroll-margin-top:16px}
h3{font:600 18px/1.3 "IBM Plex Sans",sans-serif;margin:28px 0 8px}
p,ul{margin:0 0 16px}
ul{padding-left:1.2em}
li{margin:0 0 8px}
strong{font-weight:600}
code{font:14px "IBM Plex Mono",ui-monospace,monospace;background:var(--band);padding:1px 4px;border-radius:3px}
nav.indice{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:14px 18px;margin:0 0 8px}
nav.indice h2{font:600 13px/1.4 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;margin:0 0 6px;padding:0;color:var(--soft)}
nav.indice ol{margin:0;padding-left:1.4em;columns:2;column-gap:28px;font-size:15px}
nav.indice li{margin:0 0 4px;break-inside:avoid}
@media (max-width:560px){nav.indice ol{columns:1}}
.valutazione{border-left:3px solid var(--accent);background:var(--band);padding:10px 14px;margin:0 0 18px;border-radius:0 6px 6px 0;font-size:16px}
.valutazione .etichetta{font:600 12px/1 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);display:block;margin-bottom:6px}
.tabella{overflow-x:auto;margin:0 0 16px;-webkit-overflow-scrolling:touch;border:1px solid var(--rule);border-radius:6px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
th,td{padding:7px 10px;text-align:left;vertical-align:top;border-bottom:1px solid var(--rule)}
th{font-weight:600;color:var(--soft);background:var(--band);white-space:nowrap}
tr:last-child td{border-bottom:0}
td:first-child{font-weight:500}
.nota{font-size:13px;color:var(--soft);margin:-8px 0 20px}
figure{margin:20px 0 22px}
figure .grafico{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:14px}
figcaption{font-size:13px;color:var(--soft);margin-top:8px}
.stretto{display:none}
@media (max-width:600px){.largo{display:none}.stretto{display:block}figure .grafico{padding:8px}}
details{margin-top:6px;font-size:13px}
summary{cursor:pointer;color:var(--soft)}
.s-verde::before{content:"● ";color:var(--ok)}
.s-giallo::before{content:"▲ ";color:var(--warn)}
.s-rosso::before{content:"■ ";color:var(--crit)}
footer{margin-top:56px;padding-top:16px;border-top:1px solid var(--rule);font-size:14px;color:var(--soft)}
footer .firma{font-weight:600;color:var(--ink)}
"""


def render_html(B, meta, svg):
    o = ["<!doctype html>", '<html lang="it">', "<head>", '<meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         f"<title>{esc(meta['titolo_breve'])}</title>",
         f'<meta name="description" content="{esc(meta["sottotitolo"])}">',
         '<link rel="preconnect" href="https://fonts.googleapis.com">',
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@600&display=swap" rel="stylesheet">',
         f"<style>{CSS}</style>", "</head>", "<body>", '<main class="pagina">',
         '<a class="torna" href="../index.html">← Torna alla mappa</a>',
         f'<p class="occhiello">Report supply chain e logistica · {esc(meta["edizione_lunga"])}</p>',
         f"<h1>{esc(meta['titolo'])}</h1>",
         f'<p class="sottotitolo">{esc(meta["sottotitolo"])}</p>',
         f'<p class="meta">Gabriele Giuliani · Monitor geoeconomico · dati letti il {esc(meta["data_lettura"])}. '
         f"Ogni numero ha fonte e data; i riquadri <em>Valutazione</em> sono ragionamenti dell'osservatorio, non fatti.</p>",
         '<nav class="indice" aria-label="Indice"><h2>Indice</h2><ol>']
    for b in B:
        if b[0] == "h2":
            o.append(f'<li><a href="#{b[1]}">{esc(re.sub(r"^\d+\. ", "", b[2]))}</a></li>')
    o.append("</ol></nav>")
    for b in B:
        k = b[0]
        if k == "h2":
            o.append(f'<h2 id="{b[1]}">{esc(b[2])}</h2>')
        elif k == "h3":
            o.append(f"<h3>{esc(b[1])}</h3>")
        elif k == "p":
            o.append(f"<p>{inline_html(b[1])}</p>")
        elif k == "val":
            o.append(f'<aside class="valutazione"><span class="etichetta">Valutazione</span>{inline_html(b[1])}</aside>')
        elif k == "ul":
            o.append("<ul>" + "".join(f"<li>{inline_html(x)}</li>" for x in b[1]) + "</ul>")
        elif k == "tab":
            intest, righe, nota = b[1], b[2], b[3]
            col_stato = intest.index("Stato") if "Stato" in intest else -1
            t = ['<div class="tabella"><table><thead><tr>' + "".join(f"<th scope=\"col\">{esc(x)}</th>" for x in intest) + "</tr></thead><tbody>"]
            for r in righe:
                celle = []
                for j, x in enumerate(r):
                    if j == col_stato:
                        celle.append(f'<td class="s-{esc(x)}">{esc(x)}</td>')
                    else:
                        celle.append(f"<td>{inline_html(str(x))}</td>")
                t.append("<tr>" + "".join(celle) + "</tr>")
            t.append("</tbody></table></div>")
            o.append("".join(t))
            if nota:
                o.append(f'<p class="nota">{inline_html(nota)}</p>')
        elif k == "fig":
            g = svg[b[1]]
            o.append('<figure><div class="grafico">'
                     f'<div class="largo">{g["largo"]}</div><div class="stretto">{g["stretto"]}</div></div>'
                     f'<figcaption>{inline_html(b[2])}</figcaption>'
                     + (f'<details><summary>Dati del grafico in tabella</summary>{g["tabella"]}</details>' if g.get("tabella") else "")
                     + "</figure>")
    o.append(f'<footer><p class="firma">Gabriele Giuliani · Monitor geoeconomico</p><p>{esc(meta["edizione_lunga"])}. '
             f'{inline_html(meta["nota_ai"])}</p><p><a href="../index.html">← Torna alla mappa</a></p></footer>')
    o += ["</main>", "</body>", "</html>"]
    return "\n".join(o)


def tabella_html(intest, righe):
    return ('<div class="tabella"><table><thead><tr>' + "".join(f"<th>{esc(x)}</th>" for x in intest) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in righe) + "</tbody></table></div>")


# =====================================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mese", help="edizione AAAA-MM (predefinito: mese di oggi)")
    ap.add_argument("--oggi", help="data di riferimento AAAA-MM-GG (predefinito: oggi)")
    ap.add_argument("--senza-rete", action="store_true", help="non scarica i porti europei, usa la copia salvata")
    a = ap.parse_args()
    oggi = d(a.oggi) if a.oggi else dt.date.today()
    mese = a.mese or oggi.strftime("%Y-%m")
    edizione_lunga = mese_it(mese).capitalize()

    v = calcola(oggi, a.senza_rete)
    B = costruisci_blocchi(v, oggi, mese)

    os.makedirs(CARTELLA_SVG, exist_ok=True)
    os.makedirs(CARTELLA_HTML, exist_ok=True)
    svg = {}
    cru_l, ind = grafico_cruscotto(v, True)
    cru_s, _ = grafico_cruscotto(v, False)
    tab_tr = tabella_html(["Mese", "Suez", "Bab el-Mandeb", "Capo"],
                          [[mese_it(m), num(dict(v["mensili"]["Canale di Suez"]).get(m), 1),
                            num(dict(v["mensili"]["Bab el-Mandeb"]).get(m), 1),
                            num(dict(v["mensili"]["Capo di Buona Speranza"]).get(m), 1)]
                           for m, _ in v["mensili"]["Canale di Suez"]])
    fbx = v["noli"].get("fbx")
    tab_noli = tabella_html(["Settimana", "FBX globale ($/FEU)"], [[data_it(x), num(y, 0)] for x, y in fbx["storico"]]) if fbx else ""
    it_rows, ue_rows = righe_porti(v)
    _, nord_rows = righe_porti(v, "nord")
    tab_porti = tabella_html(["Porto", "Chiamate/giorno 30 gg", "Un anno prima", "Variazione"],
                             [[n, num(a1, 1), num(b1, 1), pct(c1)] for n, c1, a1, b1 in it_rows + ue_rows + nord_rows])
    tab_cru = tabella_html(["Indicatore", "Valore", "Unità", "Stato", "Data", "Fonte"],
                           [[x["nome"], x["valore"], x["unita"], x["stato"], data_it(x["data"]), x["fonte"]] for x in ind])
    svg["transiti"] = {"largo": grafico_transiti(v, True), "stretto": grafico_transiti(v, False), "tabella": tab_tr}
    svg["noli"] = {"largo": grafico_noli(v, True), "stretto": grafico_noli(v, False), "tabella": tab_noli}
    svg["porti"] = {"largo": grafico_porti(v, True), "stretto": grafico_porti(v, False), "tabella": tab_porti}
    svg["cruscotto"] = {"largo": cru_l, "stretto": cru_s, "tabella": tab_cru}
    figure = {}
    for k, g in svg.items():
        nome = f"sc-{mese}-{k}.svg"
        with open(os.path.join(CARTELLA_SVG, nome), "w", encoding="utf-8") as f:
            f.write(g["largo"])
        figure[k] = f"grafici/{nome}"

    meta = {
        "titolo": "Supply chain e logistica — " + mese_it(mese),
        "titolo_breve": "Supply chain " + mese_it(mese),
        "sottotitolo": ("Stretti, noli, porti, ferrovie, energia, materie critiche e rischi per la logistica, "
                        "con l'Italia in evidenza."),
        "edizione_lunga": edizione_lunga,
        "data_lettura": data_it(oggi),
        "nota_ai": ("Nota sull'uso dell'AI: questo report è stato preparato con l'aiuto di un assistente AI (Claude, "
                    "Anthropic), che ha scritto lo script di costruzione, i calcoli e la bozza del testo a partire dai dati "
                    "dell'osservatorio e dalle fonti citate. I numeri vengono dai file di dati e dalle fonti linkate; le "
                    "valutazioni sono marcate come tali. La responsabilità della pubblicazione è dell'autore."),
    }
    md = render_md(B, meta, figure)
    with open(os.path.join(RADICE, "report", f"supply-chain-{mese}.md"), "w", encoding="utf-8") as f:
        f.write(md)
    pagina = render_html(B, meta, svg)
    with open(os.path.join(CARTELLA_HTML, f"supply-chain-{mese}.html"), "w", encoding="utf-8") as f:
        f.write(pagina)
    # controllo: nessun «None» o «n.d.» finito nel testo per errore
    for parola in ("None", "nan"):
        if re.search(r"\b%s\b" % parola, re.sub(r"<[^>]+>", " ", pagina)):
            avviso("la pagina contiene «%s»: controllare i dati" % parola)
    print("scritti: report/supply-chain-%s.md, docs/report/supply-chain-%s.html, report/grafici/sc-%s-*.svg" % (mese, mese, mese))
    print("avvisi:", len(AVVISI))


if __name__ == "__main__":
    main()
