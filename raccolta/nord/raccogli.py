#!/usr/bin/env python3
"""Agente TEATRO BALTICO E MARE DEL NORD: porti, energia offshore, sicurezza, esposizione.

Produce (in docs/data/):
  porti-nord.json         porti del Mare del Nord e del Baltico: traffico annuo (curato) e chiamate
                          giornaliere IMF PortWatch (media 7 giorni, confronto a 1 e 2 anni)
  offshore-nord.json      parchi eolici offshore (EMODnet, poligoni semplificati), piattaforme oil&gas,
                          hub e isole energetiche, elettrodotti e condotte strategiche
  baltico-sicurezza.json  eventi di sicurezza (curati + richiami a cavi-incidenti.json e ibrido.json),
                          disturbo GNSS (GPSJam), petroliere sanzionate viste nell'AIS (navi.json)
  esposizione-nord.json   schede di esposizione di 10 Paesi (curate + Eurostat + file della mappa)

Uso:  python3 raccolta/nord/raccogli.py [solo=porti,offshore,sicurezza,esposizione]
Solo libreria standard di Python 3. Nessuna chiave obbligatoria: se c'è GIE_API_KEY aggiunge il
riempimento degli stoccaggi di gas (GIE AGSI+), altrimenti lo salta con un avviso.
Le voci curate a mano stanno in raccolta/nord/*.json. Gli altri file di docs/data sono solo LETTI.
Ogni fonte che fallisce finisce in "errori" senza bloccare le altre.
"""
import csv, gzip, io, json, math, os, sys, time, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(os.path.dirname(QUI))
DATI = os.path.join(RADICE, "docs", "data")
UA = {"User-Agent": "monitor-geoeconomico/1.0 (osservatorio OSINT personale, non commerciale)"}
ORA = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
OGGI = datetime.now(timezone.utc).date()
# riquadro del teatro: Mare del Nord, Skagerrak/Kattegat, Baltico, Golfo di Finlandia e di Botnia
BBOX = (-5.0, 50.0, 33.0, 67.0)  # lon_min, lat_min, lon_max, lat_max
PAESI_TEATRO = ["NL", "DK", "DE", "PL", "LT", "LV", "EE", "FI", "SE", "NO"]


def avviso(msg):
    print("[nord] " + msg, file=sys.stderr)


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
        except Exception as e:
            ultimo = e
            time.sleep(3 * (i + 1))
    raise RuntimeError("%s: %s" % (url.split("?")[0], ultimo))


def leggi(percorso):
    with open(percorso, encoding="utf-8") as f:
        return json.load(f)


def leggi_dato(nome):
    """Legge un file di docs/data (sola lettura). None se manca."""
    try:
        return leggi(os.path.join(DATI, nome))
    except Exception as e:
        avviso("non leggo %s: %s" % (nome, e))
        return None


def curato(nome):
    return leggi(os.path.join(QUI, nome))


def scrivi(nome, dati):
    percorso = os.path.join(DATI, nome)
    with open(percorso, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, separators=(",", ":"))
    avviso("scritto %s (%d KB)" % (percorso, os.path.getsize(percorso) // 1024))


def nel_teatro(lat, lon):
    return lat is not None and lon is not None and BBOX[1] <= lat <= BBOX[3] and BBOX[0] <= lon <= BBOX[2]


def media(v):
    v = [x for x in v if x is not None]
    return round(sum(v) / len(v), 1) if v else None


def var_pct(a, b):
    if a is None or b in (None, 0):
        return None
    return round((a - b) / b * 100, 1)


# ------------------------------------------------------------------ PortWatch
# Stesso metodo di raccolta/flussi/raccogli.py: servizi ArcGIS pubblici di IMF PortWatch, senza chiave.
PW = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services"
PW_LINK = "https://portwatch.imf.org/"
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


def confronti(per_data, campi):
    """Media 7 giorni all'ultima data, stessi 7 giorni di 52 e 104 settimane prima, media 30 giorni."""
    if not per_data:
        return None
    ultima = max(per_data)
    u = date.fromisoformat(ultima)

    def finestra(fine, giorni):
        return {c: media([per_data.get((fine - timedelta(days=k)).isoformat(), {}).get(c) for k in range(giorni)])
                for c in campi}
    m7 = finestra(u, 7)
    m7_1a = finestra(u - timedelta(days=364), 7)
    m7_2a = finestra(u - timedelta(days=728), 7)
    m30 = finestra(u, 30)
    m30_1a = finestra(u - timedelta(days=364), 30)
    c0 = campi[0]
    return {
        "ultima_data": ultima,
        "ultimo_giorno": {c: per_data[ultima].get(c) for c in campi},
        "media7": m7, "media7_anno_prima": m7_1a, "media7_due_anni_prima": m7_2a,
        "var7_anno_pct": {c: var_pct(m7[c], m7_1a[c]) for c in campi},
        "var7_due_anni_pct": {c: var_pct(m7[c], m7_2a[c]) for c in campi},
        "media30": m30, "media30_anno_prima": m30_1a, "var30_anno_pct": var_pct(m30[c0], m30_1a[c0]),
        "periodo_media7": [(u - timedelta(days=6)).isoformat(), ultima],
        "periodo_media7_anno_prima": [(u - timedelta(days=370)).isoformat(), (u - timedelta(days=364)).isoformat()],
    }


def raccogli_porti(errori):
    cur = curato("porti.json")
    tutti_id = [i for p in cur["porti"] for i in p["portwatch"]]
    try:
        lista = ",".join("'%s'" % i for i in tutti_id)
        coord = {x["portid"]: x for x in pw_query("PortWatch_ports_database", "portid IN (%s)" % lista,
                                                   ["portid", "portname", "lat", "lon", "ISO3"], "portid")}
    except Exception as e:
        errori.append("PortWatch coordinate porti: %s" % e)
        coord = {}
    inizio = date(OGGI.year - 3, 1, 1).isoformat()
    inizio_serie = date(OGGI.year - 1, 1, 1).isoformat()
    elementi, date_dato = [], []
    for p in cur["porti"]:
        somma, presenti = {}, []
        for pid in p["portwatch"]:
            try:
                r = pw_query("Daily_Ports_Data", "portid='%s' AND date>=DATE '%s'" % (pid, inizio), ["date"] + TIPI_PORTO)
            except Exception as e:
                errori.append("PortWatch %s (%s): %s" % (p["nome"], pid, e))
                continue
            if r:
                presenti.append(pid)
            for x in r:
                d = x.get("date")
                if not d:
                    continue
                s = somma.setdefault(d, {c: None for c in TIPI_PORTO})
                for c in TIPI_PORTO:
                    if x.get(c) is not None:
                        s[c] = (s[c] or 0) + x[c]
        cf = confronti(somma, TIPI_PORTO)
        c0 = coord.get(p["portwatch"][0], {})
        el = {
            "id": p["id"], "nome": p["nome"], "paese": p["paese"], "categoria": "porto",
            "lat": round(c0["lat"], 4) if c0.get("lat") is not None else None,
            "lon": round(c0["lon"], 4) if c0.get("lon") is not None else None,
            "portwatch_id": p["portwatch"], "portwatch_nomi": [coord.get(i, {}).get("portname") for i in p["portwatch"]],
            "specializzazione": p.get("specializzazione", []), "traffico_annuo": p.get("traffico", []),
            "peso_economico": p.get("peso_economico"), "ruolo": p.get("ruolo", ""), "note": p.get("nota", ""),
            "fonte": "IMF PortWatch (Daily Ports Data) per le chiamate; fonti annuali in traffico_annuo",
            "link": PW_LINK, "affidabilita": "alta",
        }
        if cf:
            date_dato.append(cf["ultima_data"])
            el.update({"data_fonte": cf["ultima_data"], **cf,
                       "unita": "chiamate di navi al giorno (portcalls*), tonnellate stimate (import/export)",
                       "serie": {"portcalls": [[d, somma[d]["portcalls"]] for d in sorted(somma)
                                               if d >= inizio_serie and somma[d]["portcalls"] is not None]}})
        else:
            errori.append("PortWatch %s: nessun dato giornaliero" % p["nome"])
            el["data_fonte"] = None
        elementi.append(el)
    # passaggio degli Stretti danesi già raccolto dall'agente FLUSSI (sola lettura)
    stretti = []
    pw = leggi_dato("portwatch.json")
    for e in (pw or {}).get("elementi", []):
        if e.get("id") in ("chokepoint10",):
            stretti.append({k: e.get(k) for k in ("id", "nome", "nome_portwatch", "lat", "lon", "ultima_data", "media7",
                                                   "media7_anno_prima", "var7_anno_pct", "var7_due_anni_pct", "note")})
    riepilogo = []
    for e in elementi:
        if e.get("media7"):
            riepilogo.append([e["nome"], e["paese"], e["media7"]["portcalls"], e["var7_anno_pct"]["portcalls"],
                              e["media7"]["portcalls_tanker"], e["var7_anno_pct"]["portcalls_tanker"]])
    scrivi("porti-nord.json", {
        "aggiornato": ORA,
        "fonti": [
            {"nome": "IMF PortWatch (FMI e Università di Oxford), Daily Ports Data", "link": PW_LINK,
             "licenza": "dati pubblici FMI; citare «IMF PortWatch»", "data_dato": max(date_dato) if date_dato else None},
            {"nome": "Autorità portuali e statistiche nazionali (traffico annuo, vedi traffico_annuo di ogni porto)",
             "link": "", "licenza": "citazione di dati pubblicati", "data_dato": "2025-2026"}],
        "nota": ("Chiamate giornaliere di navi stimate da PortWatch con i segnali AIS; più id PortWatch sommati quando "
                 "un porto è diviso (es. Anversa + Zeebrugge + Bruges). Media a 7 giorni all'ultima data disponibile "
                 "confrontata con gli stessi giorni di 52 e 104 settimane prima. I dati arrivano con circa una settimana "
                 "di ritardo. Le navi che spengono l'AIS non sono contate: per i porti russi il dato sottostima. "
                 "traffico_annuo è curato a mano in raccolta/nord/porti.json con fonte per ogni numero."),
        "riepilogo_colonne": ["porto", "paese", "chiamate_media7", "var_anno_pct", "petroliere_media7", "var_petroliere_anno_pct"],
        "riepilogo": riepilogo,
        "stretti": stretti,
        "elementi": elementi,
        "errori": [e for e in errori if e.startswith("PortWatch")],
    })
    return elementi


# ------------------------------------------------------------------ Offshore (EMODnet)
EMOD = "https://ows.emodnet-humanactivities.eu/wfs"
EMOD_LINK = "https://emodnet.ec.europa.eu/en/human-activities"
STATI_WF = {"Production": "operativo", "Construction": "in costruzione", "Approved": "autorizzato",
            "Planned": "pianificato", "Dismantled": "smantellato", "Test site": "sito di prova"}
PAESE_ISO = {"Belgium": "BE", "Denmark": "DK", "Germany": "DE", "Netherlands": "NL", "United Kingdom": "GB",
             "Sweden": "SE", "Finland": "FI", "Poland": "PL", "Lithuania": "LT", "Latvia": "LV", "Estonia": "EE",
             "Norway": "NO", "France": "FR", "Russia": "RU", "Ireland": "IE"}


def wfs(tipo):
    q = urllib.parse.urlencode({"service": "WFS", "version": "2.0.0", "request": "GetFeature",
                                "typeNames": tipo, "outputFormat": "application/json"})
    return json.loads(scarica(EMOD + "?" + q, timeout=240))


def dp(punti, tol):
    """Douglas-Peucker iterativo su una lista di [lon, lat]."""
    if len(punti) < 3:
        return punti
    tieni = [False] * len(punti)
    tieni[0] = tieni[-1] = True
    pila = [(0, len(punti) - 1)]
    while pila:
        a, b = pila.pop()
        (x1, y1), (x2, y2) = punti[a], punti[b]
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy) or 1e-12
        dmax, imax = -1, None
        for i in range(a + 1, b):
            x0, y0 = punti[i]
            d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / n
            if d > dmax:
                dmax, imax = d, i
        if imax is not None and dmax > tol:
            tieni[imax] = True
            pila += [(a, imax), (imax, b)]
    return [p for p, t in zip(punti, tieni) if t]


def semplifica_poligono(geom, tol=0.004):
    """MultiPolygon/Polygon GeoJSON -> lista di anelli esterni semplificati [[lon,lat],...] a 4 decimali."""
    if not geom:
        return []
    polis = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    out = []
    for poli in polis:
        anello = poli[0]
        s = dp([[x, y] for x, y in (pt[:2] for pt in anello)], tol)
        if len(s) < 4:  # poligono troppo piccolo: tieni il riquadro
            xs = [pt[0] for pt in anello]
            ys = [pt[1] for pt in anello]
            s = [[min(xs), min(ys)], [max(xs), min(ys)], [max(xs), max(ys)], [min(xs), max(ys)], [min(xs), min(ys)]]
        out.append([[round(x, 4), round(y, 4)] for x, y in s])
    return out


def centroide(anelli):
    xs = [p[0] for a in anelli for p in a[:-1]] or [0]
    ys = [p[1] for a in anelli for p in a[:-1]] or [0]
    return round(sum(ys) / len(ys), 4), round(sum(xs) / len(xs), 4)


def mw_plausibile(q):
    """EMODnet ha qualche potenza sbagliata (es. Bockstigen 2.750 MW invece di 2,75): oltre 20 MW per turbina è un errore."""
    mw, n = q.get("power_mw"), q.get("n_turbines")
    if mw and n and mw / n > 20:
        return None, "potenza EMODnet %s MW scartata: %s MW per turbina non plausibili" % (mw, round(mw / n))
    return mw, ""


def mare_di(lat, lon):
    """Zona approssimata (valutazione geometrica grossolana, non un confine ufficiale)."""
    if lon >= 12.6 or (lon >= 10.0 and lat < 56.0):
        return "Baltico"
    if lon >= 9.5 and lat >= 56.0:
        return "Kattegat/Skagerrak"
    return "Mare del Nord"


def in_mare_teatro(lat, lon, paese):
    if not nel_teatro(lat, lon) or lat < 50.9:
        return False
    if paese == "GB":  # solo la costa est britannica (Mare del Nord), non Mare d'Irlanda o Manica
        return lon > -3.6 and (lat > 55.8 or lon > -1.0)
    return True


def raccogli_offshore(errori):
    cur = curato("offshore.json")
    parchi, piattaforme, linee, hub, giacimenti = [], [], [], [], []
    poligoni_per_nome, punti_per_nome = {}, {}
    try:
        fc = wfs("emodnet:windfarmspoly")
        visti = []
        for f in fc.get("features", []):
            q = f["properties"]
            paese = PAESE_ISO.get(q.get("country"), q.get("country"))
            anelli = semplifica_poligono(f.get("geometry"))
            if not anelli:
                continue
            lat, lon = centroide(anelli)
            poligoni_per_nome.setdefault(q.get("name"), []).append((lat, lon, anelli, q))
            if not in_mare_teatro(lat, lon, paese) or q.get("status") not in ("Production", "Construction", "Approved"):
                continue
            # duplicati EMODnet (stesso parco in più versioni): stesso Paese, centro entro 3 km
            dup = next((v for v in visti if v[0] == paese and abs(v[1] - lat) < 0.03 and abs(v[2] - lon) < 0.045), None)
            if dup:
                continue
            visti.append((paese, lat, lon))
            mw, avv = mw_plausibile(q)
            parchi.append({
                "id": "WF-%s" % f.get("id", "").split(".")[-1], "nome": q.get("name"), "paese": paese,
                "categoria": "eolico-offshore", "stato": STATI_WF.get(q.get("status"), q.get("status")),
                "mw": mw, "avviso_mw": avv, "turbine": q.get("n_turbines"), "anno": q.get("year"),
                "area_km2": round(q["area_sqkm"], 1) if q.get("area_sqkm") else None,
                "distanza_costa_km": round(q["dist_coast"] / 1000, 1) if q.get("dist_coast") else None,
                "mare": mare_di(lat, lon), "lat": lat, "lon": lon, "poligono": anelli,
                "fonte": "EMODnet Human Activities (windfarmspoly)", "link": EMOD_LINK,
                "data_fonte": q.get("updateyear"), "affidabilita": "media", "operatore": None,
                "note": "stato e anno come registrati da EMODnet (aggiornamento %s): possono essere in ritardo sulla realtà" % q.get("updateyear"),
            })
        # punti EMODnet per parchi che non hanno poligono (es. Polonia, Finlandia)
        pt = wfs("emodnet:windfarms")
        nomi_poli = set(poligoni_per_nome)
        for f in pt.get("features", []):
            q = f["properties"]
            paese = PAESE_ISO.get(q.get("country"), q.get("country"))
            lon, lat = f["geometry"]["coordinates"][:2]
            punti_per_nome.setdefault(q.get("name"), (round(lat, 4), round(lon, 4), q))
            if q.get("name") in nomi_poli or not in_mare_teatro(lat, lon, paese):
                continue
            if q.get("status") not in ("Production", "Construction", "Approved"):
                continue
            if any(v[0] == paese and abs(v[1] - lat) < 0.03 and abs(v[2] - lon) < 0.045 for v in visti):
                continue
            visti.append((paese, lat, lon))
            mw, avv = mw_plausibile(q)
            parchi.append({
                "id": "WFP-%s" % f.get("id", "").split(".")[-1], "nome": q.get("name"), "paese": paese,
                "categoria": "eolico-offshore", "stato": STATI_WF.get(q.get("status"), q.get("status")),
                "mw": mw, "avviso_mw": avv, "turbine": q.get("n_turbines"), "anno": q.get("year"),
                "mare": mare_di(lat, lon), "lat": round(lat, 4), "lon": round(lon, 4), "poligono": None,
                "fonte": "EMODnet Human Activities (windfarms, punti)", "link": EMOD_LINK,
                "data_fonte": q.get("updateyear"), "affidabilita": "media", "operatore": None, "note": "solo punto",
            })
        # parchi pianificati: solo il totale per Paese (sono centinaia)
        pianificati = {}
        for nome, lista in poligoni_per_nome.items():
            for lat, lon, an, q in lista:
                paese = PAESE_ISO.get(q.get("country"), q.get("country"))
                if q.get("status") == "Planned" and in_mare_teatro(lat, lon, paese):
                    pianificati.setdefault(paese, [0, 0.0])
                    pianificati[paese][0] += 1
                    pianificati[paese][1] += mw_plausibile(q)[0] or 0
    except Exception as e:
        errori.append("EMODnet parchi eolici: %s" % e)
        pianificati = {}
    # proprietari dei grandi parchi in costruzione (Wikipedia) agganciati per nome EMODnet
    for v in cur["parchi_chiave"]["voci"]:
        trovato = None
        for p in parchi:
            if p["nome"] == v["emodnet"]:
                trovato = p
                break
        if trovato is None and v["emodnet"] in poligoni_per_nome:
            lat, lon, an, q = poligoni_per_nome[v["emodnet"]][0]
            trovato = {"id": "WFK-" + v["nome"].replace(" ", "-"), "nome": q.get("name"), "paese": v["paese"],
                       "categoria": "eolico-offshore", "mare": mare_di(lat, lon), "lat": lat, "lon": lon,
                       "poligono": an, "fonte": "EMODnet Human Activities (windfarmspoly)", "link": EMOD_LINK,
                       "data_fonte": q.get("updateyear"), "affidabilita": "media", "turbine": q.get("n_turbines")}
            parchi.append(trovato)
        if trovato is None and v["emodnet"] in punti_per_nome:
            lat, lon, q = punti_per_nome[v["emodnet"]]
            trovato = {"id": "WFK-" + v["nome"].replace(" ", "-"), "nome": q.get("name"), "paese": v["paese"],
                       "categoria": "eolico-offshore", "mare": mare_di(lat, lon), "lat": lat, "lon": lon,
                       "poligono": None, "fonte": "EMODnet Human Activities (windfarms, punti)", "link": EMOD_LINK,
                       "data_fonte": q.get("updateyear"), "affidabilita": "media", "turbine": q.get("n_turbines")}
            parchi.append(trovato)
        if trovato is None:
            errori.append("offshore: %s non trovato in EMODnet (nome %s)" % (v["nome"], v["emodnet"]))
            continue
        trovato.update({"nome_progetto": v["nome"], "operatore": v["proprietari"], "mw": v["mw"],
                        "stato": "in costruzione", "anno": v["completamento"],
                        "fonte": trovato["fonte"] + "; MW, stato, anno e proprietari da Wikipedia (List of offshore wind farms)",
                        "link_proprietari": cur["parchi_chiave"]["link"]})
    # piattaforme oil & gas: un punto per giacimento chiave, coordinate EMODnet
    try:
        pl = wfs("emodnet:platforms")
        tutte = pl.get("features", [])
        for g in cur["giacimenti"]:
            sel = [f for f in tutte if any((f["properties"].get("name") or "").upper().startswith(pref)
                                           for pref in g.get("emodnet_prefissi", []))
                   and f["properties"].get("current_status") in ("Operational", "Under construction")]
            sel = [f for f in sel if "STATPIPE" not in (f["properties"].get("name") or "").upper()]  # valvole a costa
            if sel:
                lon = round(sorted(f["geometry"]["coordinates"][0] for f in sel)[len(sel) // 2], 4)
                lat = round(sorted(f["geometry"]["coordinates"][1] for f in sel)[len(sel) // 2], 4)
                orig = "mediana delle %d strutture EMODnet attive" % len(sel)
            else:
                lat, lon, orig = g.get("lat"), g.get("lon"), g.get("origine_coord", "")
            giacimenti.append({k: v for k, v in g.items() if k not in ("emodnet_prefissi",)} |
                              {"categoria": "giacimento-oil-gas", "lat": lat, "lon": lon, "origine_coord": orig,
                               "strutture": sorted({f["properties"].get("name") for f in sel})[:20]})
        # tutte le piattaforme attive del teatro come strato leggero
        for f in tutte:
            q = f["properties"]
            lon, lat = f["geometry"]["coordinates"][:2]
            paese = PAESE_ISO.get(q.get("country"), q.get("country"))
            if q.get("current_status") != "Operational" or not in_mare_teatro(lat, lon, paese):
                continue
            if q.get("function") not in ("Above water production", None) and "production" not in (q.get("function") or "").lower():
                continue
            piattaforme.append([round(lon, 3), round(lat, 3), q.get("name"), paese, q.get("operator"), q.get("primary_production")])
    except Exception as e:
        errori.append("EMODnet piattaforme: %s" % e)
    # hub ed isole energetiche
    for h in cur["hub"]:
        el = dict(h)
        el["categoria"] = "hub-energetico"
        poli = []
        for n in h.get("emodnet_poligoni", []):
            for lat, lon, an, q in poligoni_per_nome.get(n, []):
                poli += an
        el.pop("emodnet_poligoni", None)
        if poli:
            el["poligono"] = poli
            if el.get("lat") is None:
                el["lat"], el["lon"] = centroide(poli)
                el["origine_coord"] = "centro dei poligoni EMODnet della zona"
        parchi_hub = el
        hub.append(parchi_hub)
    # elettrodotti e condotte: tracciato preso dai file della mappa (sola lettura)
    rete = (leggi_dato("rete-elettrica.json") or {}).get("elementi", [])
    condotte = (leggi_dato("condotte.json") or {}).get("linee", [])
    for c in cur["collegamenti"]:
        src = c["geometria_da"]
        lista = rete if src["file"] == "rete-elettrica.json" else condotte
        valori = src["valore"] if isinstance(src["valore"], list) else [src["valore"]]
        g = []
        for x in lista:
            if x.get(src["chiave"]) in valori and x.get("g"):
                g += x["g"]
        el = {k: v for k, v in c.items() if k != "geometria_da"}
        el["categoria"] = "collegamento-" + ("gas" if c["tipo"] == "gasdotto" else "elettrico")
        el["tracciato"] = ("da %s (%s)" % (src["file"], "OSM" if src["file"] == "rete-elettrica.json" else "Global Energy Monitor")) if g else "non trovato"
        el["g"] = [[[round(p[0], 4), round(p[1], 4)] for p in parte] for parte in g]
        if not g:
            errori.append("offshore: tracciato di %s non trovato in %s" % (c["nome"], src["file"]))
        linee.append(el)
    # riepilogo MW
    riep = {}
    for p in parchi:
        k = (p["paese"], p.get("mare", ""), p.get("stato"))
        riep.setdefault(k, [0, 0.0])
        riep[k][0] += 1
        riep[k][1] += p.get("mw") or 0
    riepilogo = [{"paese": k[0], "mare": k[1], "stato": k[2], "parchi": v[0], "mw": round(v[1])} for k, v in sorted(riep.items())]
    scrivi("offshore-nord.json", {
        "aggiornato": ORA,
        "fonti": [
            {"nome": "EMODnet Human Activities: wind farms (poligoni e punti), platforms", "link": EMOD_LINK,
             "licenza": "CC BY 4.0 (EMODnet)", "data_dato": "aggiornamento EMODnet indicato in data_fonte"},
            {"nome": "Wikipedia, List of offshore wind farms (proprietari e stato dei grandi parchi in costruzione)",
             "link": cur["parchi_chiave"]["link"], "licenza": "CC BY-SA 4.0", "data_dato": "2026-07"},
            {"nome": "Tracciati da docs/data/rete-elettrica.json (OpenStreetMap, ODbL) e condotte.json (Global Energy Monitor)",
             "link": "", "licenza": "ODbL; GEM CC BY-NC-SA (uso personale non commerciale)", "data_dato": ""},
            {"nome": "Voci curate (hub, giacimenti, collegamenti): raccolta/nord/offshore.json, fonte per voce", "link": "", "licenza": "", "data_dato": "2026-11-09"}],
        "nota": ("Parchi eolici offshore operativi, in costruzione e autorizzati del Mare del Nord (solo costa est britannica) e "
                 "del Baltico secondo EMODnet, con poligoni semplificati (Douglas-Peucker 0,004 gradi, 4 decimali). EMODnet "
                 "ha versioni duplicate di alcuni parchi (tolte se il centro è entro 3 km) e stati talvolta in ritardo: i "
                 "13 grandi parchi in costruzione hanno MW, stato e proprietari presi da Wikipedia (campo operatore). "
                 "operatore=null significa che EMODnet non lo riporta. I parchi solo pianificati sono contati in "
                 "pianificati_per_paese. 'piattaforme' = strutture di produzione attive [lon, lat, nome, paese, operatore, prodotto]."),
        "riepilogo_mw": riepilogo,
        "pianificati_per_paese": {k: {"zone": v[0], "mw_dichiarati": round(v[1])} for k, v in sorted(pianificati.items())},
        "parchi": parchi, "giacimenti": giacimenti, "hub": hub, "collegamenti": linee,
        "piattaforme_colonne": ["lon", "lat", "nome", "paese", "operatore", "prodotto"], "piattaforme": piattaforme,
        "errori": [e for e in errori if e.startswith(("EMODnet", "offshore"))],
    })
    return parchi


# ------------------------------------------------------------------ Sicurezza
GPSJAM = "https://gpsjam.org/data"


def raccogli_gnss(errori, giorni=7):
    """Celle H3 con disturbo GNSS dai file giornalieri di GPSJam (dati ADS-B), nel riquadro del teatro."""
    celle = curato("h3_celle.json")["celle"]
    man = scarica(GPSJAM + "/manifest.csv", timeout=60)
    try:
        man = gzip.decompress(man)
    except OSError:
        pass
    righe = list(csv.reader(io.StringIO(man.decode("utf-8"))))
    date_ok = sorted(r[0] for r in righe if r and r[0][:2] == "20")[-giorni:]
    per_cella, serie = {}, []
    for d in date_ok:
        b = scarica("%s/%s-h3_4.csv" % (GPSJAM, d), timeout=90)
        try:
            b = gzip.decompress(b)
        except OSError:
            pass
        alte = buoni = cattivi = 0
        for r in csv.DictReader(io.StringIO(b.decode("utf-8"))):
            h = r.get("hex")
            if h not in celle:
                continue
            g, c = int(r["count_good_aircraft"]), int(r["count_bad_aircraft"])
            buoni += g
            cattivi += c
            x = per_cella.setdefault(h, [0, 0, 0])
            x[0] += g
            x[1] += c
            if g + c > 0 and c / (g + c) > 0.10:
                x[2] += 1
                alte += 1
        serie.append([d, alte, round(100 * cattivi / (buoni + cattivi), 2) if buoni + cattivi else None])
    out = []
    for h, (g, c, n_alte) in per_cella.items():
        tot = g + c
        if tot < 10:
            continue
        pct = 100 * c / tot
        if pct <= 2:
            continue
        la, lo = celle[h]
        out.append({"h3": h, "lat": la, "lon": lo, "pct_aerei_disturbati": round(pct, 1), "aerei": tot,
                    "giorni_alti": n_alte, "livello": "alto" if pct > 10 else "medio"})
    out.sort(key=lambda x: -x["pct_aerei_disturbati"])
    return {"periodo": [date_ok[0], date_ok[-1]] if date_ok else None, "celle": out,
            "serie_giornaliera_colonne": ["data", "celle_alte_nel_riquadro", "pct_aerei_disturbati_nel_riquadro"],
            "serie_giornaliera": serie}


def raccogli_sicurezza(errori):
    cur = curato("sicurezza.json")
    eventi = []
    for e in cur["eventi"]:
        eventi.append(dict(e, origine="curato (raccolta/nord/sicurezza.json)"))
    # richiami a cavi-incidenti.json (nessuna copia dei testi: solo id, data, punto e titolo)
    ci = leggi_dato("cavi-incidenti.json") or {}
    rif = set(cur.get("rif_cavi_incidenti", []))
    for x in ci.get("elementi", []):
        if x.get("id") in rif or nel_teatro(x.get("lat"), x.get("lon")):
            eventi.append({"id": x["id"], "rif": x["id"], "origine": "cavi-incidenti.json", "data": x.get("data_evento"),
                           "categoria": "danno-cavo", "nome": x.get("nome"), "paese": x.get("paese"),
                           "lat": x.get("lat"), "lon": x.get("lon"), "precisione_km": x.get("precisione_km"),
                           "fonte": x.get("fonte"), "link": x.get("link"), "data_fonte": x.get("data_fonte"),
                           "affidabilita": x.get("affidabilita"), "note": "dettagli in cavi-incidenti.json"})
    # richiami a ibrido.json: eventi nel riquadro del teatro o nei Paesi del teatro
    ib = leggi_dato("ibrido.json") or {}
    for x in ib.get("punti", []):
        if not (nel_teatro(x.get("lat"), x.get("lon")) and (x.get("paese") in PAESI_TEATRO or not x.get("paese"))):
            continue
        if x.get("categoria") in ("falso-allarme", "attacco-informatico"):  # fuori dal tema porti/energia/mare
            continue
        eventi.append({"id": x.get("id"), "rif": x.get("id"), "origine": "ibrido.json", "data": x.get("data_evento"),
                       "categoria": x.get("categoria"), "nome": x.get("nome"), "paese": x.get("paese"),
                       "lat": x.get("lat"), "lon": x.get("lon"), "precisione_km": x.get("precisione_km"),
                       "fonte": x.get("fonte"), "link": x.get("link"), "data_fonte": x.get("data_fonte"),
                       "affidabilita": x.get("affidabilita"), "note": "dettagli in ibrido.json"})
    # petroliere sanzionate viste nell'AIS (navi.json incrociato con sanzioni-navi.json dall'agente NAVI)
    navi = leggi_dato("navi.json") or {}
    sanz = {s.get("imo"): s for s in (leggi_dato("sanzioni-navi.json") or {}).get("elementi", [])}
    flotta, per_area = [], {}
    for n in navi.get("elementi", []):
        if not nel_teatro(n.get("lat"), n.get("lon")):
            continue
        a = per_area.setdefault(n.get("area", ""), {"navi": 0, "sanzionate": 0, "flotta_ombra_probabile": 0})
        a["navi"] += 1
        s_ok = str(n.get("sanzionata", "")).startswith("sì")
        if s_ok:
            a["sanzionate"] += 1
        if n.get("flotta_ombra_probabile"):
            a["flotta_ombra_probabile"] += 1
        if s_ok:
            s = sanz.get(n.get("imo")) or {}
            flotta.append({"id": "AIS-%s" % (n.get("imo") or n.get("mmsi")), "categoria": "nave-sanzionata-vista",
                           "nome": n.get("nome"), "imo": n.get("imo"), "tipo": n.get("tipo"), "bandiera": n.get("bandiera"),
                           "lat": n.get("lat"), "lon": n.get("lon"), "data": (n.get("ora_utc") or "")[:10],
                           "ora_utc": n.get("ora_utc"), "area": n.get("area"), "destinazione": n.get("destinazione"),
                           "sanzionata": n.get("sanzionata"), "flotta_ombra_probabile": n.get("flotta_ombra_probabile"),
                           "regimi": sorted({z.get("chi") for z in s.get("sanzioni", []) if z.get("chi")}),
                           "fonte": n.get("fonte"), "link": "", "affidabilita": "media",
                           "note": "posizione AIS dichiarata dalla nave; incrocio IMO con sanzioni-navi.json"})
    # disturbo GNSS
    try:
        gnss = raccogli_gnss(errori)
    except Exception as e:
        errori.append("GPSJam: %s" % e)
        gnss = None
    vecchio = leggi_dato("baltico-sicurezza.json") or {}
    if gnss:  # storico giornaliero accumulato a ogni esecuzione
        st = {r[0]: r for r in (vecchio.get("gnss") or {}).get("serie_giornaliera", [])}
        for r in gnss["serie_giornaliera"]:
            st[r[0]] = r
        gnss["serie_giornaliera"] = [st[k] for k in sorted(st)][-400:]
    elif vecchio.get("gnss"):
        gnss = vecchio["gnss"]
        gnss["nota_vecchio"] = "dati della corsa precedente: GPSJam non raggiungibile"
    eventi.sort(key=lambda x: str(x.get("data") or ""), reverse=True)
    conteggi = {}
    for e in eventi:
        conteggi[e.get("categoria")] = conteggi.get(e.get("categoria"), 0) + 1
    scrivi("baltico-sicurezza.json", {
        "aggiornato": ORA,
        "fonti": [
            {"nome": "Eventi curati con fonte per voce (raccolta/nord/sicurezza.json)", "link": "", "licenza": "citazione", "data_dato": "2026-11-09"},
            {"nome": "docs/data/cavi-incidenti.json e ibrido.json (richiami per id)", "link": "", "licenza": "", "data_dato": ci.get("aggiornato")},
            {"nome": "GPSJam (John Wiseman), dati ADS-B Exchange, celle H3 risoluzione 4", "link": "https://gpsjam.org/",
             "licenza": "nessuna licenza dichiarata: uso personale con citazione", "data_dato": (gnss or {}).get("periodo", [None, None])[-1] if gnss and gnss.get("periodo") else None},
            {"nome": "docs/data/navi.json (AIS: Digitraffic, aisstream.io) incrociato con sanzioni-navi.json", "link": "", "licenza": "vedi navi.json", "data_dato": navi.get("aggiornato")}],
        "nota": ("Punti con data, categoria, fonte e affidabilità. Coordinate stimate (precisione_km). Gli incidenti a cavi e "
                 "condotte e gli eventi ibridi già raccolti da altri agenti sono richiamati per id (campo rif), non ricopiati. "
                 "gnss.celle = celle H3 con aerei che segnalano navigazione degradata negli ultimi 7 giorni (medio 2-10%, "
                 "alto oltre 10%, minimo 10 aerei): misura l'effetto sugli aerei, non la posizione dei disturbatori. "
                 "flotta_vista = navi sanzionate nelle ultime posizioni AIS raccolte da navi.json: le navi con AIS spento non ci sono."),
        "conteggi": conteggi,
        "eventi": eventi,
        "flotta_vista": flotta, "flotta_per_area": per_area,
        "gnss": gnss,
        "errori": [e for e in errori if e.startswith(("GPSJam", "sicurezza"))],
    })
    return eventi, gnss, flotta


# ------------------------------------------------------------------ Esposizione
EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
SIEC = {"TOTAL": "totale", "G3000": "gas", "O4100_TOT": "greggio", "C0000X0350-0370": "carbone"}


def eurostat_dipendenza(errori):
    out = {}
    try:
        q = [("format", "JSON"), ("lang", "EN"), ("unit", "PC"), ("sinceTimePeriod", str(OGGI.year - 4))]
        q += [("geo", g) for g in PAESI_TEATRO] + [("siec", s) for s in SIEC]
        d = json.loads(scarica(EUROSTAT + "/nrg_ind_id?" + urllib.parse.urlencode(q), timeout=120))
        dims, size = d["id"], d["size"]
        idx = {k: d["dimension"][k]["category"]["index"] for k in dims}
        inv = {k: {v: c for c, v in idx[k].items()} for k in dims}
        for k, v in d.get("value", {}).items():
            k = int(k)
            pos = {}
            for dim, n in zip(reversed(dims), reversed(size)):
                pos[dim] = inv[dim][k % n]
                k //= n
            o = out.setdefault(pos["geo"], {})
            anno = pos["time"]
            prec = o.get(SIEC[pos["siec"]])
            if prec is None or anno > prec["anno"]:
                o[SIEC[pos["siec"]]] = {"anno": anno, "pct": round(v, 1)}
    except Exception as e:
        errori.append("Eurostat nrg_ind_id: %s" % e)
    return out


def gie_stoccaggi(errori):
    chiave = os.environ.get("GIE_API_KEY")
    if not chiave:
        avviso("GIE_API_KEY assente: salto gli stoccaggi di gas (AGSI+)")
        return {}
    out = {}
    for p in PAESI_TEATRO:
        try:
            d = json.loads(scarica("https://agsi.gie.eu/api?country=%s&size=1" % p, intestazioni={"x-key": chiave}))
            r = (d.get("data") or [{}])[0]
            if r:
                out[p] = {"data": r.get("gasDayStart"), "pieno_pct": float(r["full"]) if r.get("full") not in (None, "-") else None,
                          "twh": float(r["gasInStorage"]) if r.get("gasInStorage") not in (None, "-") else None}
        except Exception as e:
            errori.append("GIE AGSI %s: %s" % (p, e))
    return out


def raccogli_esposizione(errori, porti=None, eventi=None):
    cur = curato("esposizione.json")
    dip = eurostat_dipendenza(errori)
    stocc = gie_stoccaggi(errori)
    gnl = {}
    for t in (leggi_dato("terminali-gnl.json") or {}).get("elementi", []):
        if t.get("tipo") == "import" and t.get("paese") in PAESI_TEATRO:
            g = gnl.setdefault(t["paese"], {"operativi": 0, "mtpa_operativa": 0.0, "terminali": []})
            cap = (t.get("capacita_per_stato") or {}).get("operativo") or 0
            if cap:
                g["operativi"] += 1
                g["mtpa_operativa"] += cap
                g["terminali"].append(t.get("nome"))
    inter = {}
    for x in (leggi_dato("interconnessioni.json") or {}).get("elementi", []):
        for p in x.get("paesi", []):
            if p in PAESI_TEATRO:
                inter.setdefault(p, []).append("%s (%s MW, %s)" % (x.get("nome"), x.get("mw"), x.get("stato")))
    approdi = {}
    cv = leggi_dato("cavi.json") or {}
    for a in cv.get("approdi", []):
        p = a.get("paese")
        if p in PAESI_TEATRO:
            approdi[p] = approdi.get(p, 0) + 1
    cavi_paese = {}
    for c in cv.get("elementi", []):
        for p in c.get("paesi", []):
            if p in PAESI_TEATRO:
                cavi_paese[p] = cavi_paese.get(p, 0) + 1
    porti = porti or (leggi_dato("porti-nord.json") or {}).get("elementi", [])
    eventi = eventi or (leggi_dato("baltico-sicurezza.json") or {}).get("eventi", [])
    oggi_meno_2a = (OGGI - timedelta(days=730)).isoformat()
    schede = []
    for s in cur["paesi"]:
        p = s["paese"]
        miei_porti = [{"nome": x["nome"], "chiamate_media7": (x.get("media7") or {}).get("portcalls"),
                       "var_anno_pct": (x.get("var7_anno_pct") or {}).get("portcalls")} for x in porti if x.get("paese") == p]
        ev = [e for e in eventi if e.get("paese") == p and str(e.get("data") or "") >= oggi_meno_2a]
        g = gnl.get(p)
        schede.append(dict(s, **{
            "categoria": "scheda-paese",
            "dipendenza_importazioni_pct": dip.get(p, {}),
            "gnl_rigassificazione_operativa": {"terminali": g["operativi"], "mtpa": round(g["mtpa_operativa"], 1),
                                               "mld_m3_anno": round(g["mtpa_operativa"] * 1.36, 1), "nomi": g["terminali"]} if g else None,
            "stoccaggi_gas": stocc.get(p),
            "interconnessioni_mappa": inter.get(p, []),
            "cavi_sottomarini": {"cavi": cavi_paese.get(p, 0), "approdi": approdi.get(p, 0)},
            "porti_portwatch": miei_porti,
            "eventi_sicurezza_24_mesi": len(ev),
        }))
    scrivi("esposizione-nord.json", {
        "aggiornato": ORA,
        "fonti": [
            {"nome": "Eurostat, Energy imports dependency (nrg_ind_id)", "link": "https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_id/default/table",
             "licenza": "CC BY 4.0 (riuso Eurostat)", "data_dato": max((v.get("totale", {}).get("anno", "") for v in dip.values()), default=None)},
            {"nome": "IEEFA European LNG Tracker, maggio 2026 (quote del GNL per origine)", "link": "https://ieefa.org/european-lng-tracker",
             "licenza": "citazione", "data_dato": "2026-05"},
            {"nome": "Global Energy Monitor via docs/data/terminali-gnl.json; interconnessioni.json; cavi.json (TeleGeography, CC BY-NC-SA)",
             "link": "", "licenza": "vedi i file", "data_dato": ""},
            {"nome": "GIE AGSI+ (solo con GIE_API_KEY)", "link": "https://agsi.gie.eu/", "licenza": "dati pubblici con registrazione", "data_dato": None}],
        "nota": ("Una scheda per Paese. dipendenza_importazioni_pct = importazioni nette / energia disponibile (Eurostat): "
                 "oltre 100% vuol dire che il Paese accumula scorte o riesporta, valori negativi = esportatore netto (Norvegia, "
                 "Danimarca per il gas). gnl_rigassificazione_operativa: capacità dei terminali d'importazione operativi "
                 "(1 Mt di GNL ≈ 1,36 miliardi di m³). rischi e livello sono valutazioni dell'agente."),
        "elementi": schede,
        "errori": [e for e in errori if e.startswith(("Eurostat", "GIE"))],
    })


def main():
    solo = None
    for a in sys.argv[1:]:
        if a.startswith("solo="):
            solo = set(a[5:].split(","))
    errori = []
    porti = eventi = None

    def fa(nome):
        return solo is None or nome in solo
    if fa("porti"):
        try:
            porti = raccogli_porti(errori)
        except Exception as e:
            errori.append("porti: %s" % e)
    if fa("offshore"):
        try:
            raccogli_offshore(errori)
        except Exception as e:
            errori.append("offshore: %s" % e)
    if fa("sicurezza"):
        try:
            eventi, _, _ = raccogli_sicurezza(errori)
        except Exception as e:
            errori.append("sicurezza: %s" % e)
    if fa("esposizione"):
        try:
            raccogli_esposizione(errori, porti, eventi)
        except Exception as e:
            errori.append("esposizione: %s" % e)
    for e in errori:
        avviso("ERRORE " + e)


if __name__ == "__main__":
    main()
