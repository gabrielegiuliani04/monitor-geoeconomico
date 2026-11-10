#!/usr/bin/env python3
"""Agente FLUSSI, NOLI E SANZIONI: un'unica entrata, una sotto-funzione per fonte.

Produce (in docs/data/):
  portwatch.json      passaggi giornalieri ai chokepoint e chiamate nei porti italiani (IMF PortWatch)
  noli.json           indici dei noli (Drewry WCI, Freightos FBX, SCFI, CCFI, Baltic Dry)
  gpr.json            indice di rischio geopolitico di Caldara e Iacoviello (giornaliero e mensile)
  sanzioni-navi.json  navi sanzionate (OFAC SDN, UK FCDO, UE Gazzetta ufficiale via OpenSanctions)

Uso:  python3 raccolta/flussi/raccogli.py [solo=portwatch,noli,gpr,sanzioni]
Solo libreria standard di Python 3. Nessuna chiave richiesta.
Ogni fonte che fallisce viene scritta in "errori" senza bloccare le altre.
"""
import csv, html, io, json, os, re, struct, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone

RADICE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATI = os.path.join(RADICE, "docs", "data")
UA = {"User-Agent": "monitor-geoeconomico/1.0 (osservatorio OSINT personale, non commerciale)"}
ORA = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
OGGI = datetime.now(timezone.utc).date()


def avviso(msg):
    print("[flussi] " + msg, file=sys.stderr)


def scarica(url, timeout=90, tentativi=3, intestazioni=None):
    h = dict(UA)
    if intestazioni:
        h.update(intestazioni)
    ultimo = None
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # rete, 429, 5xx
            ultimo = e
            time.sleep(3 * (i + 1))
    raise RuntimeError("%s: %s" % (url.split("?")[0], ultimo))


def scrivi(nome, dati):
    percorso = os.path.join(DATI, nome)
    with open(percorso, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, separators=(",", ":"))
    avviso("scritto %s (%d KB)" % (percorso, os.path.getsize(percorso) // 1024))


def leggi_vecchio(nome):
    try:
        with open(os.path.join(DATI, nome), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def media(v):
    v = [x for x in v if x is not None]
    return round(sum(v) / len(v), 1) if v else None


def var_pct(a, b):
    if a is None or b in (None, 0):
        return None
    return round((a - b) / b * 100, 1)


# ---------------------------------------------------------------- PortWatch
PW = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services"
PW_LINK = "https://portwatch.imf.org/"
# id PortWatch -> chiave di docs/data/stretti.json
CHOKEPOINT = [
    ("chokepoint6", "Stretto di Hormuz", None),
    ("chokepoint4", "Bab el-Mandeb", None),
    ("chokepoint1", "Canale di Suez", None),
    ("chokepoint2", "Canale di Panama", None),
    ("chokepoint3", "Bosforo", "PortWatch misura il Bosforo; i Dardanelli hanno in pratica lo stesso traffico."),
    ("chokepoint5", "Stretto di Malacca", None),
    ("chokepoint8", "Stretto di Gibilterra", None),
    ("chokepoint7", "Capo di Buona Speranza", None),
    ("chokepoint11", "Stretto di Taiwan", None),
    ("chokepoint10", "Stretti danesi", "PortWatch misura solo l'Øresund, non il Grande Belt (dove passano le petroliere più grandi)."),
    ("chokepoint14", "Stretto di Luzon", None),
    ("chokepoint28", "Stretto di Kerch", None),
    ("chokepoint26", "Stretto di Bering", None),
]
# porti italiani: id PortWatch, nome mostrato
PORTI_IT = [
    ("port387", "Genova"), ("port1318", "Trieste"), ("port395", "Gioia Tauro"),
    ("port622", "La Spezia"), ("port655", "Livorno"), ("port1005", "Venezia (Lido)"),
    ("port1006", "Venezia (Malamocco)"), ("port1004", "Ravenna"), ("port80", "Augusta"),
]
TIPI_CP = ["n_total", "n_tanker", "n_container", "n_dry_bulk", "n_general_cargo", "n_roro"]
TIPI_PORTO = ["portcalls", "portcalls_tanker", "portcalls_container", "portcalls_dry_bulk",
              "portcalls_general_cargo", "portcalls_roro", "import", "export"]


def pw_query(servizio, where, campi, ordine="date"):
    righe, offset = [], 0
    while True:
        q = urllib.parse.urlencode({
            "where": where, "outFields": ",".join(campi), "orderByFields": ordine,
            "returnGeometry": "false", "resultOffset": offset, "resultRecordCount": 1000, "f": "json"})
        d = json.loads(scarica("%s/%s/FeatureServer/0/query?%s" % (PW, servizio, q), timeout=120))
        if "error" in d:
            raise RuntimeError("%s: %s" % (servizio, d["error"]))
        f = [x["attributes"] for x in d.get("features", [])]
        righe += f
        if not d.get("exceededTransferLimit") and len(f) < 1000:
            break
        offset += len(f)
    return righe


def pw_coordinate(servizio, ids):
    lista = ",".join("'%s'" % i for i in ids)
    try:
        r = pw_query(servizio, "portid IN (%s)" % lista, ["portid", "portname", "lat", "lon", "country", "ISO3"], "portid")
        return {x["portid"]: x for x in r}
    except Exception as e:
        avviso("coordinate %s: %s" % (servizio, e))
        return {}


def confronti(righe, campi):
    """Media 7 giorni all'ultima data, stessa settimana di 1 e 2 anni prima, media 30 giorni."""
    per_data = {r["date"]: r for r in righe if r.get("date")}
    if not per_data:
        return None
    ultima = max(per_data)
    u = date.fromisoformat(ultima)

    def finestra(fine, giorni):
        out = {}
        for c in campi:
            out[c] = media([per_data.get((fine - timedelta(days=k)).isoformat(), {}).get(c) for k in range(giorni)])
        return out
    m7 = finestra(u, 7)
    m7_1a = finestra(u - timedelta(days=364), 7)  # 52 settimane: stessi giorni della settimana
    m7_2a = finestra(u - timedelta(days=728), 7)
    m7_3a = finestra(u - timedelta(days=1092), 7)  # per Suez e Bab el-Mandeb: prima della crisi del Mar Rosso
    m30 = finestra(u, 30)
    m30_1a = finestra(u - timedelta(days=364), 30)
    c0 = campi[0]
    return {
        "ultima_data": ultima,
        "ultimo_giorno": {c: per_data[ultima].get(c) for c in campi},
        "media7": m7, "media7_anno_prima": m7_1a, "media7_due_anni_prima": m7_2a,
        "media7_tre_anni_prima": m7_3a,
        "var7_anno_pct": {c: var_pct(m7[c], m7_1a[c]) for c in campi},
        "var7_due_anni_pct": {c: var_pct(m7[c], m7_2a[c]) for c in campi},
        "var7_tre_anni_pct": {c: var_pct(m7[c], m7_3a[c]) for c in campi},
        "media30": m30, "media30_anno_prima": m30_1a,
        "var30_anno_pct": var_pct(m30[c0], m30_1a[c0]),
        "periodo_media7": [(u - timedelta(days=6)).isoformat(), ultima],
        "periodo_media7_anno_prima": [(u - timedelta(days=370)).isoformat(), (u - timedelta(days=364)).isoformat()],
    }


def serie_di(righe, campo):
    return [[r["date"], r.get(campo)] for r in righe if r.get("date") and r.get(campo) is not None]


def precedenti_portwatch():
    """Elementi dell'esecuzione precedente, per id: se PortWatch non risponde si riusano invece di pubblicare un file vuoto."""
    try:
        with open(os.path.join(DATI, "portwatch.json"), encoding="utf-8") as h:
            return {e["id"]: e for e in json.load(h).get("elementi", []) if e.get("id")}
    except Exception:
        return {}


def riusa(prec, pid, elementi, fonti_date):
    e = prec.get(pid)
    if not e:
        return
    e = dict(e, riusato=True)
    elementi.append(e)
    if e.get("data_fonte"):
        fonti_date.append(e["data_fonte"])


def raccogli_portwatch(errori):
    inizio = date(OGGI.year - 3, 1, 1).isoformat()  # ultimi ~3 anni, per i confronti a 1 e 2 anni
    elementi, fonti_date = [], []
    prec = precedenti_portwatch()
    coord_cp = pw_coordinate("PortWatch_chokepoints_database", [c[0] for c in CHOKEPOINT])
    for pid, chiave, nota in CHOKEPOINT:
        try:
            r = pw_query("Daily_Chokepoints_Data", "portid='%s' AND date>=DATE '%s'" % (pid, inizio),
                         ["date"] + TIPI_CP + ["capacity", "capacity_tanker"])
        except Exception as e:
            errori.append("PortWatch %s (%s): %s (riuso il dato precedente)" % (chiave, pid, e))
            riusa(prec, pid, elementi, fonti_date)
            continue
        cf = confronti(r, TIPI_CP + ["capacity", "capacity_tanker"])
        if not cf:
            errori.append("PortWatch %s: nessun dato" % chiave)
            continue
        fonti_date.append(cf["ultima_data"])
        c = coord_cp.get(pid, {})
        elementi.append({
            "tipo": "chokepoint", "id": pid, "nome": chiave, "nome_portwatch": c.get("portname"),
            "lat": c.get("lat"), "lon": c.get("lon"),
            "categoria": "passaggio strategico", "fonte": "IMF PortWatch (Daily Chokepoints Data)",
            "link": PW_LINK, "data_fonte": cf["ultima_data"], "affidabilita": "alta",
            "unita": "navi al giorno (n_*), tonnellate di portata lorda stimate (capacity*)",
            **cf,
            # serie giornaliere dal 1° gennaio di 3 anni fa: totale e petroliere (il file deve restare leggero)
            "serie": {k: serie_di(r, k) for k in ("n_total", "n_tanker")},
            "note": nota or "",
        })
    coord_p = pw_coordinate("PortWatch_ports_database", [p[0] for p in PORTI_IT])
    for pid, nome in PORTI_IT:
        try:
            r = pw_query("Daily_Ports_Data", "portid='%s' AND date>=DATE '%s'" % (pid, inizio), ["date"] + TIPI_PORTO)
        except Exception as e:
            errori.append("PortWatch porto %s (%s): %s (riuso il dato precedente)" % (nome, pid, e))
            riusa(prec, pid, elementi, fonti_date)
            continue
        cf = confronti(r, TIPI_PORTO)
        if not cf:
            errori.append("PortWatch porto %s: nessun dato" % nome)
            continue
        c = coord_p.get(pid, {})
        elementi.append({
            "tipo": "porto", "id": pid, "nome": nome, "nome_portwatch": c.get("portname"), "paese": "IT",
            "lat": c.get("lat"), "lon": c.get("lon"), "categoria": "porto",
            "fonte": "IMF PortWatch (Daily Ports Data)", "link": PW_LINK, "data_fonte": cf["ultima_data"],
            "affidabilita": "alta",
            "unita": "chiamate di navi al giorno (portcalls*), tonnellate stimate (import/export)",
            **cf,
            "serie": {k: serie_di(r, k) for k in ("portcalls",)},
            "note": "Venezia è divisa da PortWatch in due porti: Lido e Malamocco (porto petroli e Marghera)." if "Venezia" in nome else "",
        })
    ultima = max(fonti_date) if fonti_date else None
    scrivi("portwatch.json", {
        "aggiornato": ORA,
        "fonti": [{"nome": "IMF PortWatch (FMI e Università di Oxford), dati AIS elaborati",
                   "link": PW_LINK, "licenza": "dati pubblici FMI; citare «IMF PortWatch»",
                   "data_dato": ultima}],
        "nota": ("Passaggi giornalieri di navi stimati da PortWatch con i segnali AIS. Media a 7 giorni all'ultima "
                 "data disponibile, confrontata con gli stessi 7 giorni di 52 e 104 settimane prima. "
                 "Per Suez e Bab el-Mandeb il confronto utile è a 3 anni (fine 2023, prima degli attacchi houthi). I dati arrivano con circa una settimana di ritardo e l'ultimo giorno può essere rivisto. "
                 "Le navi che spengono l'AIS (flotta ombra, zone di guerra) non sono contate."),
        "elementi": elementi, "errori": [e for e in errori if e.startswith("PortWatch")],
    })


# ---------------------------------------------------------------- Noli
def testo_pulito(b):
    t = b.decode("utf-8", "replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def numero(s):
    return float(s.replace(",", "").replace("$", ""))


MESI = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def noli_drewry():
    url = "https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry"
    t = testo_pulito(scarica(url))
    m = re.search(r"assessment for \w+, (\d{1,2}) (\w{3})\w* (\d{4})", t)
    if not m:
        raise RuntimeError("Drewry: data della valutazione non trovata")
    d = date(int(m.group(3)), MESI[m.group(2).lower()], int(m.group(1))).isoformat()
    m = re.search(r"World Container Index \(WCI\)[^.]*?(increased|decreased|rose|fell|was stable|remained stable|unchanged)[^$]*?\$([\d,]+) per 40ft", t)
    if not m:
        raise RuntimeError("Drewry: valore del WCI non trovato")
    rotte = {}
    for mm in re.finditer(r"Shanghai to ([A-Z][a-zA-Z ]+?) (?:increased|decreased|rose|fell|surged|dropped|declined|climbed|jumped|were unchanged|was unchanged|remained stable|remained unchanged|stayed)[^$]{0,40}\$([\d,]+) per 40ft", t):
        rotte["Shanghai-" + mm.group(1).strip()] = numero(mm.group(2))
    for mm in re.finditer(r"([A-Z][a-z]+) to Shanghai (?:increased|decreased|rose|fell|were unchanged|was unchanged|remained stable)[^$]{0,40}\$([\d,]+) per 40ft", t):
        rotte[mm.group(1) + "-Shanghai"] = numero(mm.group(2))
    return {"id": "wci", "nome": "Drewry World Container Index (composito)", "unita": "USD per container da 40 piedi",
            "valore": numero(m.group(2)), "data": d, "rotte": rotte, "frequenza": "settimanale (giovedì)",
            "fonte": "Drewry", "link": url, "licenza": "© Drewry; pagina pubblica, si riporta il valore con la fonte",
            "metodo": "letto dal testo della pagina pubblica settimanale"}


def noli_fbx():
    url = "https://www.freightos.com/enterprise/terminal/freightos-baltic-index-global-container-pricing-index/"
    b = scarica(url).decode("utf-8", "replace")
    serie = []
    for m in re.finditer(r"frProductIntroChartData\['[^']+'\] = (\[.*?\]);", b):
        try:
            for x in json.loads(m.group(1)):
                if x.get("ticker") == "FBX":
                    serie.append([x["indexDate"], x["value"]])
        except Exception:
            pass
    serie = sorted({d: v for d, v in serie}.items())
    rotte = {}
    m = re.search(r"frProductIntroTickerData\['[^']+'\] = (\[.*?\]);", b)
    if m:
        for x in json.loads(m.group(1)):
            try:
                rotte[x["label"]] = {"valore": numero(x["value"]), "var": x.get("change")}
            except Exception:
                pass
    if not serie:
        raise RuntimeError("FBX: serie non trovata nella pagina")
    return {"id": "fbx", "nome": "Freightos Baltic Index FBX (globale)", "unita": "USD per container da 40 piedi",
            "valore": serie[-1][1], "data": serie[-1][0], "serie": [list(x) for x in serie],
            "rotte": rotte, "frequenza": "settimanale nella pagina pubblica (l'indice è giornaliero)",
            "fonte": "Freightos / Baltic Exchange", "link": url,
            "licenza": "© Freightos; pagina pubblica, uso con citazione",
            "nota_rotte": "Valori delle rotte dalla barra della pagina, senza data esplicita: si assume la data dell'ultimo punto della serie. "
                          "FBX01 Cina-Costa Ovest USA, FBX03 Cina-Costa Est USA, FBX11 Cina-Nord Europa, FBX13 Cina-Mediterraneo.",
            "metodo": "letto dai dati incorporati nella pagina pubblica"}


def noli_sse(nome_indice):
    url = "https://en.sse.net.cn/currentIndex?indexName=" + nome_indice
    d = json.loads(scarica(url))["data"]
    righe = {}
    tot = None
    for x in d["lineDataList"]:
        n = x["properties"].get("lineName_EN") or x["dataItemTypeName"]
        if x.get("currentContent") is None:
            continue
        v = {"valore": round(x["currentContent"], 2), "precedente": round(x["lastContent"], 2) if x.get("lastContent") is not None else None,
             "var_pct": round(x["percentage"], 2) if x.get("percentage") is not None else None,
             "unita": x["properties"].get("unit_EN") or "punti indice"}
        if x["dataItemTypeName"].endswith("_T"):
            tot = v
        else:
            righe[n] = v
    if not tot:
        raise RuntimeError("%s: composito non trovato" % nome_indice)
    nomi = {"scfi": "Shanghai Containerized Freight Index SCFI (composito)",
            "ccfi": "China Containerized Freight Index CCFI (composito)"}
    return {"id": nome_indice, "nome": nomi[nome_indice], "unita": "punti indice",
            "valore": tot["valore"], "data": d["currentDate"], "precedente": tot["precedente"],
            "data_precedente": d["lastDate"], "var_pct": tot["var_pct"], "rotte": righe,
            "frequenza": "settimanale (venerdì)", "fonte": "Shanghai Shipping Exchange",
            "link": "https://en.sse.net.cn/indices/%snew.jsp" % nome_indice,
            "licenza": "© Shanghai Shipping Exchange; il dettaglio per rotta dello SCFI richiede registrazione",
            "metodo": "endpoint JSON pubblico della pagina (currentIndex)"}


def noli_bdi():
    url = "https://tradingeconomics.com/commodity/baltic"
    t = testo_pulito(scarica(url))
    m = re.search(r"Baltic Dry (rose|fell|was unchanged|increased|decreased|eased|climbed|declined)[a-z ]* to ([\d,\.]+) Index Points on (\w+ \d{1,2}, \d{4})(?:, (up|down) ([\d\.]+)% from the previous day)?", t)
    if not m:
        raise RuntimeError("Baltic Dry: valore non trovato")
    d = datetime.strptime(m.group(3), "%B %d, %Y").date().isoformat()
    a = re.search(r"(up|down) ([\d\.]+)% compared to the same time last year", t)
    var_a = (float(a.group(2)) * (1 if a.group(1) == "up" else -1)) if a else None
    var_g = (float(m.group(5)) * (1 if m.group(4) == "up" else -1)) if m.group(5) else None
    return {"id": "bdi", "nome": "Baltic Dry Index (rinfuse secche)", "unita": "punti indice",
            "valore": numero(m.group(2)), "data": d, "var_giorno_pct": var_g, "var_anno_pct": var_a,
            "frequenza": "giornaliero", "fonte": "Trading Economics (riprende l'indice del Baltic Exchange tramite un CFD)",
            "link": url, "licenza": "© Baltic Exchange / Trading Economics: solo l'ultimo valore, citato; niente serie storica",
            "metodo": "letto dal testo della pagina pubblica",
            "nota": "Il Baltic Exchange non pubblica l'indice gratis; Trading Economics lo ricava da un CFD: affidabilità media."}


def raccogli_noli(errori):
    vecchio = leggi_vecchio("noli.json") or {}
    vecchi = {e.get("id"): e for e in vecchio.get("elementi", [])}
    elementi = []
    for nome, f in [("Drewry WCI", noli_drewry), ("Freightos FBX", noli_fbx),
                    ("SCFI", lambda: noli_sse("scfi")), ("CCFI", lambda: noli_sse("ccfi")),
                    ]:  # Baltic Dry tolto: i termini di Trading Economics vietano la raccolta automatica
        try:
            e = f()
        except Exception as ex:
            errori.append("Noli %s: %s" % (nome, ex))
            if nome.split()[-1].lower() in vecchi:  # tieni l'ultimo valore buono
                pass
            continue
        # storico che cresce a ogni esecuzione: unisce i valori vecchi con quelli nuovi
        st = {d: v for d, v in vecchi.get(e["id"], {}).get("storico", [])}
        for d, v in e.get("serie", []):
            st[d] = v
        if e.get("data_precedente") and e.get("precedente") is not None:
            st.setdefault(e["data_precedente"], e["precedente"])
        st[e["data"]] = e["valore"]
        e["storico"] = sorted([list(x) for x in st.items()])
        e.pop("serie", None)
        # variazione anno su anno se lo storico la contiene (tolleranza 7 giorni)
        target = date.fromisoformat(e["data"]) - timedelta(days=364)
        vicino = [x for x in e["storico"] if abs((date.fromisoformat(x[0]) - target).days) <= 7]
        e["var_anno_pct_calcolata"] = var_pct(e["valore"], vicino[0][1]) if vicino else None
        elementi.append(e)
    ids_nuovi = {e["id"] for e in elementi}
    for i, e in vecchi.items():  # fonte caduta oggi: resta l'ultimo valore, segnato come vecchio
        if i not in ids_nuovi:
            e["nota_stato"] = "valore non aggiornato in questa esecuzione"
            elementi.append(e)
    scrivi("noli.json", {
        "aggiornato": ORA,
        "fonti": [{"nome": e["fonte"], "link": e["link"], "licenza": e["licenza"], "data_dato": e["data"]} for e in elementi],
        "nota": ("Indici dei noli marittimi. Container: WCI e FBX in USD per 40 piedi, SCFI e CCFI in punti. "
                 "Rinfuse secche: Baltic Dry. Nessuno di questi editori offre la serie storica gratis: lo storico "
                 "si costruisce a ogni esecuzione dello script (per FBX la pagina dà circa 3 mesi settimanali)."),
        "elementi": elementi, "errori": [x for x in errori if x.startswith("Noli")],
    })


# ---------------------------------------------------------------- GPR
GPR_LINK = "https://www.matteoiacoviello.com/gpr.htm"


def leggi_dta(b):
    """Lettore minimo dei file Stata 117/118 (formato con tag XML). Solo colonne numeriche."""
    if not b.startswith(b"<stata_dta>"):
        raise RuntimeError("non è un file Stata 117/118")
    rel = int(re.search(rb"<release>(\d+)</release>", b[:200]).group(1))
    p = b.index(b"<K>") + 3
    K = struct.unpack_from("<H", b, p)[0]
    p = b.index(b"<N>") + 3
    N = struct.unpack_from("<Q" if rel >= 118 else "<I", b, p)[0]
    p = b.index(b"<map>") + 5
    mappa = struct.unpack_from("<14Q", b, p)
    p = mappa[2] + len(b"<variable_types>")
    tipi = struct.unpack_from("<%dH" % K, b, p)
    lung = 129 if rel >= 118 else 33
    p = mappa[3] + len(b"<varnames>")
    nomi = [b[p + i * lung:p + (i + 1) * lung].split(b"\0")[0].decode("utf-8") for i in range(K)]
    flen = 57 if rel >= 118 else 49
    p = mappa[5] + len(b"<formats>")
    formati = [b[p + i * flen:p + (i + 1) * flen].split(b"\0")[0].decode() for i in range(K)]
    num = {65526: ("d", 8), 65527: ("f", 4), 65528: ("l", 4), 65529: ("h", 2), 65530: ("b", 1)}
    larg, fmt = [], "<"
    for t in tipi:
        if t in num:
            fmt += num[t][0]
            larg.append(num[t][1])
        elif t <= 2045:
            fmt += "%ds" % t
            larg.append(t)
        elif t == 32768:
            fmt += "8s"
            larg.append(8)
        else:
            raise RuntimeError("tipo Stata sconosciuto %d" % t)
    st = struct.Struct(fmt)
    p = mappa[9] + len(b"<data>")
    righe = []
    for i in range(N):
        v = list(st.unpack_from(b, p + i * st.size))
        for j, t in enumerate(tipi):
            x = v[j]
            if t == 65526 and (x > 8.988e307 or x != x):
                v[j] = None
            elif t == 65527 and (x > 1.7e38 or x != x):
                v[j] = None
            elif t == 65528 and x > 2147483620:
                v[j] = None
            elif t == 65529 and x > 32740:
                v[j] = None
            elif t == 65530 and x > 100:
                v[j] = None
            elif isinstance(x, bytes):
                v[j] = x.split(b"\0")[0].decode("utf-8", "replace") if t <= 2045 else None
        righe.append(dict(zip(nomi, v)))
    return nomi, formati, righe


def data_stata(x, formato):
    base = date(1960, 1, 1)
    if x is None:
        return None
    if formato.startswith("%td") or formato.startswith("%d"):
        return (base + timedelta(days=int(x))).isoformat()
    if formato.startswith("%tc"):
        return (datetime(1960, 1, 1) + timedelta(milliseconds=x)).date().isoformat()
    if formato.startswith("%tm"):
        a, m = divmod(int(x), 12)
        return date(1960 + a, m + 1, 1).isoformat()
    return None


def colonna_data(nomi, formati):
    for n, f in zip(nomi, formati):
        if f.startswith(("%td", "%tc", "%tm", "%d")):
            return n, f
    raise RuntimeError("colonna della data non trovata: %s" % list(zip(nomi, formati)))


def raccogli_gpr(errori):
    inizio = date(OGGI.year - 5, OGGI.month, 1).isoformat()
    elementi, fonti = [], []
    descr = {
        "GPRD": "GPR giornaliero (indice di rischio geopolitico)",
        "GPRD_ACT": "GPR giornaliero, atti (eventi avvenuti)",
        "GPRD_THREAT": "GPR giornaliero, minacce",
        "GPRD_MA7": "GPR giornaliero, media mobile 7 giorni",
        "GPRD_MA30": "GPR giornaliero, media mobile 30 giorni",
        "GPR": "GPR mensile (1985-oggi)",
        "GPRT": "GPR mensile, minacce",
        "GPRA": "GPR mensile, atti",
        "GPRC_ITA": "GPR mensile per l'Italia (quota % di articoli GPR che citano il paese)",
        "GPRC_RUS": "GPR mensile per la Russia",
        "GPRC_ISR": "GPR mensile per Israele",
        "GPRC_SAU": "GPR mensile per l'Arabia Saudita",
        "GPRC_CHN": "GPR mensile per la Cina",
        "GPRC_TWN": "GPR mensile per Taiwan",
        "GPRC_UKR": "GPR mensile per l'Ucraina",
        "GPRC_USA": "GPR mensile per gli Stati Uniti",
        "GPRC_EGY": "GPR mensile per l'Egitto",
        "GPRC_TUR": "GPR mensile per la Turchia",
    }
    for file, freq in [("data_gpr_daily_recent.dta", "giornaliera"), ("data_gpr_export.dta", "mensile")]:
        url = "https://www.matteoiacoviello.com/gpr_files/" + file
        try:
            nomi, formati, righe = leggi_dta(scarica(url, timeout=180))
            cd, fd = colonna_data(nomi, formati)
        except Exception as e:
            errori.append("GPR %s: %s" % (file, e))
            continue
        disponibili = {n.upper(): n for n in nomi}
        ultima = None
        for var, testo in descr.items():
            if var not in disponibili:
                continue
            n = disponibili[var]
            s = []
            for r in righe:
                d = data_stata(r.get(cd), fd)
                if d and d >= inizio and r.get(n) is not None:
                    s.append([d, round(float(r[n]), 2)])
            if not s:
                continue
            ultima = max(ultima or "", s[-1][0])
            valori = [x[1] for x in s]
            e = {"id": var, "nome": testo, "frequenza": freq, "ultimo": s[-1][1], "data": s[-1][0],
                 "media_periodo": media(valori), "massimo_periodo": max(s, key=lambda x: x[1]),
                 "serie": s}
            if freq == "giornaliera":
                e["media7"] = media(valori[-7:])
                e["media30"] = media(valori[-30:])
                a = date.fromisoformat(s[-1][0]) - timedelta(days=365)
                e["media30_anno_prima"] = media([v for d, v in s if a - timedelta(days=29) <= date.fromisoformat(d) <= a])
            else:
                e["anno_prima"] = next((v for d, v in s if d == date.fromisoformat(s[-1][0]).replace(year=date.fromisoformat(s[-1][0]).year - 1).isoformat()), None)
            elementi.append(e)
        fonti.append({"nome": "Caldara e Iacoviello, Geopolitical Risk Index, file %s" % file, "link": url,
                      "licenza": "dati liberi per la ricerca; citare Caldara e Iacoviello (2022), American Economic Review",
                      "data_dato": ultima})
    if not elementi:
        errori.append("GPR: nessuna serie letta")
    scrivi("gpr.json", {
        "aggiornato": ORA, "fonti": fonti,
        "nota": ("Indice di rischio geopolitico (GPR) di Dario Caldara e Matteo Iacoviello: conta gli articoli di 10 "
                 "giornali internazionali che parlano di tensioni, guerre e terrorismo. Media 1985-2019 = 100. "
                 "Ultimi 5 anni. Le serie per paese sono mensili."),
        "elementi": elementi, "errori": [x for x in errori if x.startswith("GPR")],
    })


# ---------------------------------------------------------------- Sanzioni
PAESI = {  # bandiera (testo) -> ISO 2 lettere, solo i casi frequenti
    "panama": "PA", "liberia": "LR", "marshall islands": "MH", "comoros": "KM", "cameroon": "CM", "gabon": "GA",
    "sierra leone": "SL", "cook islands": "CK", "palau": "PW", "togo": "TG", "barbados": "BB", "russia": "RU",
    "iran": "IR", "malta": "MT", "hong kong": "HK", "china": "CN", "india": "IN", "vietnam": "VN", "tanzania": "TZ",
    "eswatini": "SZ", "guinea-bissau": "GW", "benin": "BJ", "gambia": "GM", "djibouti": "DJ", "st kitts and nevis": "KN",
    "saint kitts and nevis": "KN", "belize": "BZ", "cuba": "CU", "venezuela": "VE", "north korea": "KP",
    "korea, north": "KP", "mongolia": "MN", "sao tome and principe": "ST", "vanuatu": "VU", "tuvalu": "TV",
    "united arab emirates": "AE", "turkey": "TR", "türkiye": "TR", "greece": "GR", "cyprus": "CY", "malaysia": "MY",
    "antigua and barbuda": "AG", "honduras": "HN", "bolivia": "BO", "mozambique": "MZ", "curacao": "CW",
    "equatorial guinea": "GQ", "zanzibar": "TZ", "moldova": "MD", "aruba": "AW", "guyana": "GY", "unknown": None,
    "false flag": None, "syria": "SY", "st vincent and the grenadines": "VC", "saint vincent and the grenadines": "VC",
    "kiribati": "KI", "madagascar": "MG", "nauru": "NR", "seychelles": "SC", "dominica": "DM", "fiji": "FJ",
    "bahamas": "BS", "singapore": "SG", "norway": "NO", "sri lanka": "LK", "eritrea": "ER", "burkina faso": "BF",
    "democratic people's republic of korea": "KP", "san marino": "SM", "ecuador": "EC", "st. kitts and nevis": "KN",
    "republic of palau": "PW", "antigua & barbuda": "AG", "cambodia": "KH", "cayman islands": "KY", "indonesia": "ID",
    "the gambia": "GM", "sao tome & principe": "ST", "guinea": "GN", "russian federation": "RU",
    "haiti": "HT", "belarus": "BY", "kazakhstan": "KZ", "libya": "LY", "iraq": "IQ", "egypt": "EG", "ukraine": "UA",
}


def iso_bandiera(t):
    if not t:
        return None
    return PAESI.get(t.strip().lower())


def ambito(programmi):
    t = " ".join(programmi).upper()
    out = []
    if "RUS" in t or "UKRAINE" in t or "PEESA" in t:
        out.append("Russia")
    if "IRAN" in t or "IFSR" in t:
        out.append("Iran")
    if "DPRK" in t or "PRK" in t or "KOREA" in t:
        out.append("Corea del Nord")
    if "VENEZUELA" in t:
        out.append("Venezuela")
    if "SDGT" in t or "TERROR" in t:
        out.append("terrorismo (es. Houthi, Hezbollah)")
    if "CUBA" in t:
        out.append("Cuba")
    if "LBY" in t or "LIBYA" in t:
        out.append("Libia")
    if "SYRIA" in t or "SYR" in t:
        out.append("Siria")
    return out or ["altro"]


def imo_norm(s):
    m = re.search(r"(\d{7})", s or "")
    return m.group(1) if m else None


def sanz_ofac():
    url = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.XML"
    root = ET.fromstring(scarica(url, timeout=240))
    ns = root.tag.split("}")[0] + "}" if root.tag.startswith("{") else ""
    pub = root.findtext("%spublshInformation/%sPublish_Date" % (ns, ns))
    try:
        pub = datetime.strptime(pub, "%m/%d/%Y").date().isoformat()
    except Exception:
        pass
    societa = {}
    navi = []
    for e in root.iter(ns + "sdnEntry"):
        tipo = e.findtext(ns + "sdnType")
        nome = " ".join(x for x in [e.findtext(ns + "firstName"), e.findtext(ns + "lastName")] if x)
        if tipo == "Entity":
            societa[nome.upper()] = True
        if tipo != "Vessel":
            continue
        imo = None
        for i in e.iter(ns + "id"):
            if (i.findtext(ns + "idType") or "").startswith("Vessel Registration") and "IMO" in (i.findtext(ns + "idNumber") or ""):
                imo = imo_norm(i.findtext(ns + "idNumber"))
        vi = e.find(ns + "vesselInfo")
        prog = [p.text for p in e.iter(ns + "program")]
        navi.append({"imo": imo, "nome": nome, "bandiera": vi.findtext(ns + "vesselFlag") if vi is not None else None,
                     "tipo_nave": vi.findtext(ns + "vesselType") if vi is not None else None,
                     "programmi": prog, "uid": e.findtext(ns + "uid"),
                     "collegata": re.findall(r"Linked To: ([^)]+)\)", e.findtext(ns + "remarks") or "")})
    for n in navi:  # solo società collegate presenti come Entity nella lista (niente persone)
        n["collegata"] = [c.strip() for c in n["collegata"] if c.strip().upper() in societa]
    return pub, navi


def sanz_uk():
    url = "https://sanctionslist.fcdo.gov.uk/docs/UK-Sanctions-List.csv"
    t = scarica(url, timeout=240).decode("utf-8-sig", "replace")
    prima, resto = t.split("\n", 1)
    m = re.search(r"(\d{2}-\w{3}-\d{4})", prima)
    data_lista = datetime.strptime(m.group(1), "%d-%b-%Y").date().isoformat() if m else None
    navi = {}
    for r in csv.DictReader(io.StringIO(resto)):
        if (r.get("Designation Type") or "").strip().lower() != "ship":
            continue
        uid = r["Unique ID"]
        n = navi.setdefault(uid, {"imo": imo_norm(r.get("IMO number")), "nome": None, "alias": [],
                                  "bandiera": (r.get("Current believed flag of ship") or "").strip() or None,
                                  "tipo_nave": (r.get("Type of ship") or "").strip() or None,
                                  "regime": (r.get("Regime Name") or "").strip(), "data": None, "uid": uid})
        nome = (r.get("Name 6") or "").strip()
        if (r.get("Name type") or "").lower().startswith("primary") and nome:
            n["nome"] = nome
        elif nome:
            n["alias"].append(nome)
        try:
            n["data"] = datetime.strptime(r["Date Designated"].strip(), "%d/%m/%Y").date().isoformat()
        except Exception:
            pass
    for n in navi.values():
        if not n["nome"] and n["alias"]:
            n["nome"] = n["alias"].pop(0)
    return data_lista, list(navi.values())


def sanz_ue():
    url = "https://data.opensanctions.org/datasets/latest/eu_journal_sanctions/targets.simple.csv"
    t = scarica(url, timeout=240).decode("utf-8", "replace")
    navi, ultima = [], None
    for r in csv.DictReader(io.StringIO(t)):
        if r.get("schema") != "Vessel":
            continue
        date_s = re.findall(r"(\d{4}-\d{2}-\d{2})", r.get("sanctions") or "")
        d = min(date_s) if date_s else None
        ultima = max(ultima or "", r.get("last_change", "")[:10])
        navi.append({"imo": imo_norm(r.get("identifiers")), "nome": r.get("name"), "programmi": [r.get("program_ids") or ""],
                     "data": d, "base_giuridica": (r.get("sanctions") or "")[:160],
                     "bandiera": None})
    return ultima, navi


def raccogli_sanzioni(errori):
    per_imo, senza_imo, fonti = {}, [], []

    def aggiungi(n, chi, data, programmi, extra=None):
        rec = {"chi": chi, "data": data, "programmi": programmi}
        if extra:
            rec.update(extra)
        k = n.get("imo")
        if not k:
            senza_imo.append({"imo": None, "nome": n.get("nome"), "bandiera": n.get("bandiera"),
                              "bandiera_iso": iso_bandiera(n.get("bandiera")), "sanzioni": [rec]})
            return
        e = per_imo.setdefault(k, {"imo": k, "nome": n.get("nome"), "altri_nomi": [], "bandiera": None,
                                   "bandiera_iso": None, "tipo_nave": None, "sanzioni": [], "societa_collegate": []})
        if n.get("nome") and n["nome"].upper() != (e["nome"] or "").upper() and n["nome"] not in e["altri_nomi"]:
            e["altri_nomi"].append(n["nome"])
        if n.get("bandiera") and not e["bandiera"]:
            e["bandiera"] = n["bandiera"]
            e["bandiera_iso"] = iso_bandiera(n["bandiera"])
        if n.get("tipo_nave") and not e["tipo_nave"]:
            e["tipo_nave"] = n["tipo_nave"]
        e["sanzioni"].append(rec)
        for c in n.get("collegata") or []:
            if c not in e["societa_collegate"]:
                e["societa_collegate"].append(c)

    try:
        pub, navi = sanz_ofac()
        for n in navi:
            aggiungi(n, "USA (OFAC SDN)", None, n["programmi"], {"data_lista": pub})
        fonti.append({"nome": "OFAC SDN List (XML)", "link": "https://sanctionslist.ofac.treas.gov/Home/SdnList",
                      "licenza": "pubblico dominio (governo USA)", "data_dato": pub})
    except Exception as e:
        errori.append("Sanzioni OFAC: %s" % e)
    try:
        d, navi = sanz_uk()
        for n in navi:
            aggiungi(n, "Regno Unito (FCDO/OFSI)", n["data"], [n["regime"]], {"data_lista": d})
        fonti.append({"nome": "UK Sanctions List (FCDO), CSV", "link": "https://www.gov.uk/government/publications/the-uk-sanctions-list",
                      "licenza": "Open Government Licence v3.0", "data_dato": d})
    except Exception as e:
        errori.append("Sanzioni UK: %s" % e)
    try:
        d, navi = sanz_ue()
        for n in navi:
            aggiungi(n, "Unione europea (Gazzetta ufficiale)", n["data"], n["programmi"], {"base_giuridica": n["base_giuridica"]})
        fonti.append({"nome": "UE, atti in Gazzetta ufficiale trascritti da OpenSanctions (eu_journal_sanctions)",
                      "link": "https://www.opensanctions.org/datasets/eu_journal_sanctions/",
                      "licenza": "CC BY-NC 4.0 (OpenSanctions): uso non commerciale, citare la fonte", "data_dato": d})
    except Exception as e:
        errori.append("Sanzioni UE: %s" % e)

    elementi = []
    for e in list(per_imo.values()) + senza_imo:
        progs = [p for s in e["sanzioni"] for p in s["programmi"]]
        e["ambito"] = ambito(progs)
        e["sanzionata_da"] = sorted({s["chi"].split(" (")[0] for s in e["sanzioni"]})
        date_d = [s["data"] for s in e["sanzioni"] if s.get("data")]
        e["prima_designazione"] = min(date_d) if date_d else None
        e["flotta_ombra_probabile"] = bool({"Russia", "Iran"} & set(e["ambito"])) and \
            (e.get("tipo_nave") is None or "tank" in (e.get("tipo_nave") or "").lower() or "oil" in (e.get("tipo_nave") or "").lower())
        elementi.append(e)
    elementi.sort(key=lambda e: (-(len(e["sanzionata_da"])), e.get("prima_designazione") or "9999", e.get("nome") or ""))
    conta = {
        "navi_totali": len(elementi),
        "per_chi": {k: sum(1 for e in elementi if k in e["sanzionata_da"]) for k in ["USA", "Regno Unito", "Unione europea"]},
        "da_tutti_e_tre": sum(1 for e in elementi if len(e["sanzionata_da"]) == 3),
        "ambito_russia": sum(1 for e in elementi if "Russia" in e["ambito"]),
        "ambito_iran": sum(1 for e in elementi if "Iran" in e["ambito"]),
        "flotta_ombra_probabile": sum(1 for e in elementi if e["flotta_ombra_probabile"]),
        "bandiere_principali": sorted(
            ((b, sum(1 for e in elementi if e.get("bandiera") == b)) for b in {e.get("bandiera") for e in elementi if e.get("bandiera")}),
            key=lambda x: -x[1])[:15],
        "designate_ultimi_90_giorni": sum(1 for e in elementi if e.get("prima_designazione") and
                                          e["prima_designazione"] >= (OGGI - timedelta(days=90)).isoformat()),
    }
    scrivi("sanzioni-navi.json", {
        "aggiornato": ORA, "fonti": fonti,
        "nota": ("Navi sanzionate da USA (OFAC SDN), Regno Unito (UK Sanctions List) e Unione europea (divieto di "
                 "accesso ai porti, allegato XLII del reg. 833/2014 e altri regimi). Unione per numero IMO. "
                 "Solo navi e società collegate già presenti come enti nella lista OFAC: nessuna persona fisica. "
                 "La lista OFAC non riporta la data di designazione (resta vuota). «flotta_ombra_probabile» è una "
                 "valutazione della mappa: petroliera (o tipo ignoto) sanzionata per Russia o Iran. La bandiera è "
                 "quella dichiarata dalla fonte e spesso è falsa o cambia."),
        "conteggi": conta, "elementi": elementi, "errori": [x for x in errori if x.startswith("Sanzioni")],
    })


# ---------------------------------------------------------------- main
def main():
    scelte = None
    for a in sys.argv[1:]:
        if a.startswith("solo="):
            scelte = set(a[5:].split(","))
    os.makedirs(DATI, exist_ok=True)
    errori = []
    for nome, f in [("portwatch", raccogli_portwatch), ("noli", raccogli_noli),
                    ("gpr", raccogli_gpr), ("sanzioni", raccogli_sanzioni)]:
        if scelte and nome not in scelte:
            continue
        try:
            f(errori)
        except Exception as e:  # una fonte rotta non ferma le altre
            errori.append("%s: errore inatteso %s" % (nome, e))
    for e in errori:
        avviso("ERRORE " + e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
