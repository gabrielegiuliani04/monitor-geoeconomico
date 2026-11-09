#!/usr/bin/env python3
"""Basi militari nel mondo -> docs/data/basi-mondo.json

Dominio CURATO: le schede delle basi (chi le usa, stato, perché contano, fonti) si scrivono a mano
in raccolta/basi/basi.json. Questo script, solo libreria standard, ogni volta:

  1. VALIDA le voci: campi obbligatori, valori ammessi (tipo, stato, affidabilità), codici paese,
     coordinate nei limiti, date nel formato AAAA-MM-GG e non future, link http(s), nomi dei
     passaggi strategici e dei mari coerenti con docs/data/labels.json.
  2. CERCA I DUPLICATI con i livelli già in mappa (fissi.json, italia.json, difesa.json, iran.json):
     un punto entro 5 km da una base dello stesso utilizzatore è un duplicato e non entra nel file;
     se l'utilizzatore è diverso (es. Giappone e USA sullo stesso aeroporto di Gibuti) resta, con un avviso.
     Controlla anche i doppioni interni (entro 1 km, stesso utilizzatore).
  3. COLLEGA ogni base agli altri livelli, leggendo i file degli altri agenti (non li rifà):
       - labels.json  -> passaggio strategico più vicino (entro 1.000 km) e distanza in km
       - rotte.json   -> rotta marittima più vicina (entro 500 km): distanza, tipo, passaggi che attraversa
       - cavi.json    -> approdi di cavi sottomarini entro 100 km
  4. Con --verifica-coordinate confronta le coordinate con la fonte indicata in 'rif_coord':
     OurAirports (airports.csv, pubblico dominio) e Wikidata (SPARQL, CC0). Scarti oltre 1 km
     finiscono negli avvisi. Se le fonti non rispondono, salta con un avviso e non fallisce.
  5. Scrive docs/data/basi-mondo.json nel formato comune (raccolta/AGENTI.md) con 'errori' e 'avvisi'.

Uso:
  python3 raccolta/basi/raccogli.py                         # valida, collega, scrive
  python3 raccolta/basi/raccogli.py --controlla             # valida soltanto, non scrive
  python3 raccolta/basi/raccogli.py --verifica-coordinate   # come il primo + confronto online delle coordinate
Esce con codice 0 anche se ci sono errori di validazione (finiscono nel file);
codice 1 solo se il file curato manca o non è JSON valido.
"""
import csv
import datetime as dt
import io
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
DATI = os.path.join(RADICE, "docs", "data")
CURATO = os.path.join(QUI, "basi.json")
USCITA = os.path.join(DATI, "basi-mondo.json")
ADESSO = dt.datetime.now(dt.timezone.utc)
OGGI = ADESSO.date()
UA = "monitor-geoeconomico/1.0 (osservatorio OSINT; github.com/gabrielegiuliani04/monitor-geoeconomico)"

URL_OURAIRPORTS = "https://davidmegginson.github.io/ourairports-data/airports.csv"
URL_WIKIDATA = "https://query.wikidata.org/sparql"

TIPI = {"aerea": "base-aerea", "navale": "base-navale", "terrestre": "base-terrestre",
        "comando": "comando", "radar": "radar", "mista": "base-mista"}
STATI = {"operativa", "in costruzione", "ridotta", "lasciata", "pianificata"}
AFFIDABILITA = {"alta", "media", "bassa"}
ORIGINI = {"ourairports", "wikidata", "fonte", "stimata"}
TEATRI = {"EU": "Europa", "AR": "Artico e Nord Atlantico", "IP": "Indo-Pacifico", "OI": "Oceano Indiano",
          "AF": "Africa", "MO": "Medio Oriente", "AC": "Caucaso e Asia centrale", "AM": "Americhe e Atlantico"}
UTENTI_SPECIALI = {"NATO", "EU"}
OBBLIGATORI = ["nome", "paese", "appartenenza", "utenti", "tipo", "stato", "lat", "lon", "origine_coord",
               "precisione_km", "teatro", "perche_conta", "fonti", "affidabilita"]
RE_ISO2 = re.compile(r"^[A-Z]{2}$")
RE_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_QID = re.compile(r"^Q\d+$")
KM_DUPLICATO = 5.0       # con i livelli esistenti
KM_DOPPIONE_INTERNO = 1.0
KM_CAVI = 100.0
KM_STRETTO = 1000.0       # oltre questa distanza il passaggio più vicino non si indica
KM_ROTTA = 500.0
TIPI_ROTTA = {"M": "principale", "m": "media", "n": "secondaria"}
KM_SCARTO_COORD = 1.0
GIORNI_STATO_VECCHIO = 365  # stati che cambiano (in costruzione, ridotta, pianificata)
ALTRI_LIVELLI = ["fissi.json", "italia.json", "difesa.json", "iran.json"]
NON_BASI = {"porto"}        # categorie dei livelli esistenti che non sono basi

errori, avvisi = [], []


def errore(msg):
    errori.append(msg)
    print("ERRORE:", msg, file=sys.stderr)


def avviso(msg):
    avvisi.append(msg)
    print("AVVISO:", msg, file=sys.stderr)


def carica(nome):
    p = os.path.join(DATI, nome)
    if not os.path.exists(p):
        avviso(f"{nome}: non trovato, collegamento saltato")
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        avviso(f"{nome}: non leggibile ({e})")
        return None


def km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def km_segmento(lat, lon, a, b):
    """distanza approssimata punto-segmento (proiezione equirettangolare locale); a, b = [lon, lat]"""
    kx = 111.32 * math.cos(math.radians(lat))
    ky = 110.57
    ax, ay = (a[0] - lon) * kx, (a[1] - lat) * ky
    bx, by = (b[0] - lon) * kx, (b[1] - lat) * ky
    if abs(a[0] - b[0]) > 180:  # segmento che attraversa l'antimeridiano: uso i vertici
        return min(math.hypot(ax, ay), math.hypot(bx, by))
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / l2))
    return math.hypot(ax + t * dx, ay + t * dy)


def scarica(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ------------------------------------------------------------------ validazione
def valida_data(s):
    if not isinstance(s, str) or not RE_DATA.match(s):
        return False
    try:
        return dt.date.fromisoformat(s) <= OGGI
    except ValueError:
        return False


def valida(v, i, nomi_luoghi):
    chi = f"voce {i + 1} ({v.get('nome', '?')})"
    ok = True
    for c in OBBLIGATORI:
        if v.get(c) in (None, "", []):
            errore(f"{chi}: manca '{c}'")
            ok = False
    if not ok:
        return False
    if v["tipo"] not in TIPI:
        errore(f"{chi}: tipo '{v['tipo']}' non ammesso ({', '.join(TIPI)})")
        ok = False
    if v["stato"] not in STATI:
        errore(f"{chi}: stato '{v['stato']}' non ammesso")
        ok = False
    if v["affidabilita"] not in AFFIDABILITA:
        errore(f"{chi}: affidabilità '{v['affidabilita']}' non ammessa")
        ok = False
    if v["teatro"] not in TEATRI:
        errore(f"{chi}: teatro '{v['teatro']}' non ammesso")
        ok = False
    if not RE_ISO2.match(v["paese"]):
        errore(f"{chi}: paese '{v['paese']}' non è un codice ISO a 2 lettere")
        ok = False
    for u in [v["appartenenza"]] + list(v["utenti"]):
        if not (RE_ISO2.match(u) or u in UTENTI_SPECIALI):
            errore(f"{chi}: utilizzatore '{u}' non valido")
            ok = False
    if v["appartenenza"] not in v["utenti"]:
        avviso(f"{chi}: l'appartenenza {v['appartenenza']} non è tra gli utenti")
    lat, lon = v["lat"], v["lon"]
    if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and -90 <= lat <= 90 and -180 <= lon <= 180):
        errore(f"{chi}: coordinate fuori limite ({lat}, {lon})")
        ok = False
    elif lat == 0 and lon == 0:
        errore(f"{chi}: coordinate (0, 0)")
        ok = False
    if v["origine_coord"] not in ORIGINI:
        errore(f"{chi}: origine_coord '{v['origine_coord']}' non ammessa")
        ok = False
    rif = v.get("rif_coord", "")
    if v["origine_coord"] == "ourairports" and not rif:
        errore(f"{chi}: coordinate da OurAirports senza codice in rif_coord")
        ok = False
    if v["origine_coord"] == "wikidata" and not RE_QID.match(rif or ""):
        errore(f"{chi}: coordinate da Wikidata senza Q-id in rif_coord")
        ok = False
    if not isinstance(v["precisione_km"], (int, float)) or v["precisione_km"] <= 0:
        errore(f"{chi}: precisione_km deve essere un numero positivo")
        ok = False
    if v["origine_coord"] == "stimata" and v["precisione_km"] < 5:
        avviso(f"{chi}: coordinate stimate con precisione dichiarata sotto 5 km")
    anno = v.get("anno")
    if anno is not None and not (isinstance(anno, int) and 1500 <= anno <= OGGI.year + 5):
        errore(f"{chi}: anno '{anno}' non valido")
        ok = False
    for f in v["fonti"]:
        if not f.get("fonte") or not f.get("link") or not f.get("data_fonte"):
            errore(f"{chi}: fonte incompleta ({f.get('fonte', '?')})")
            ok = False
            continue
        if not re.match(r"^https?://", f["link"]):
            errore(f"{chi}: link non http(s): {f['link']}")
            ok = False
        if not valida_data(f["data_fonte"]):
            errore(f"{chi}: data_fonte non valida o futura: {f['data_fonte']}")
            ok = False
    for n in v.get("vicino_a", []):
        if n not in nomi_luoghi:
            avviso(f"{chi}: '{n}' non è un nome di labels.json (stretti, mari, regioni)")
    if v["stato"] in ("in costruzione", "ridotta", "pianificata"):
        date = [f["data_fonte"] for f in v["fonti"] if valida_data(f.get("data_fonte", ""))
                and not f["fonte"].startswith(("OurAirports", "Wikidata"))]
        if date and (OGGI - dt.date.fromisoformat(max(date))).days > GIORNI_STATO_VECCHIO:
            avviso(f"{chi}: stato '{v['stato']}' con fonte più recente del {max(date)}: da ricontrollare")
    return ok


# ------------------------------------------------------------------ duplicati
def punti_esistenti():
    out = []
    for nome in ALTRI_LIVELLI:
        d = carica(nome)
        if not d:
            continue
        for p in d.get("punti", d.get("elementi", [])):
            if p.get("categoria") in NON_BASI:
                continue
            if not isinstance(p.get("lat"), (int, float)) or not isinstance(p.get("lon"), (int, float)):
                continue
            utenti = set(p.get("utenti") or []) | {p.get("appartenenza", "")}
            out.append({"file": nome, "nome": p.get("nome", ""), "lat": p["lat"], "lon": p["lon"],
                        "utenti": {u for u in utenti if u}, "app": p.get("appartenenza", "")})
    return out


def controlla_duplicati(voci, esistenti):
    scarta = set()
    for i, v in enumerate(voci):
        for p in esistenti:
            d = km(v["lat"], v["lon"], p["lat"], p["lon"])
            if d > KM_DUPLICATO:
                continue
            if v["appartenenza"] == p["app"] or (v["appartenenza"] in p["utenti"] and p["app"] in v["utenti"]):
                errore(f"'{v['nome']}' duplica '{p['nome']}' di {p['file']} ({d:.1f} km, stesso utilizzatore): esclusa")
                scarta.add(i)
            else:
                avviso(f"'{v['nome']}' ({v['appartenenza']}) è a {d:.1f} km da '{p['nome']}' ({p['app']}) di {p['file']}: tenuta, utilizzatore diverso")
    for i in range(len(voci)):
        for j in range(i + 1, len(voci)):
            a, b = voci[i], voci[j]
            d = km(a["lat"], a["lon"], b["lat"], b["lon"])
            if d <= KM_DOPPIONE_INTERNO and a["appartenenza"] == b["appartenenza"]:
                errore(f"doppione interno: '{a['nome']}' e '{b['nome']}' ({d:.1f} km): esclusa la seconda")
                scarta.add(j)
    return scarta


# ------------------------------------------------------------------ collegamenti
def collega(v, stretti, rotte, approdi):
    out = {}
    if stretti:
        n, d = min(((s["n"], km(v["lat"], v["lon"], s["y"], s["x"])) for s in stretti), key=lambda t: t[1])
        if d <= KM_STRETTO:
            out["stretto_vicino"] = {"nome": n, "km": round(d)}
    if rotte:
        best = None
        for r in rotte:
            g = r.get("g") or []
            # le rotte possono essere una lista di punti o una lista di parti
            parti = g if g and isinstance(g[0][0], list) else [g]
            for parte in parti:
                for a, b in zip(parte, parte[1:]):
                    d = km_segmento(v["lat"], v["lon"], a, b)
                    if best is None or d < best[0]:
                        best = (d, r.get("t", ""), r.get("s") or [])
        if best and best[0] <= KM_ROTTA:
            out["rotta_vicina"] = {"km": round(best[0]), "tipo": TIPI_ROTTA.get(best[1], best[1]), "passaggi": best[2]}
    if approdi is not None:
        vicini = sorted(((km(v["lat"], v["lon"], a["lat"], a["lon"]), a["nome"]) for a in approdi
                         if isinstance(a.get("lat"), (int, float))), key=lambda t: t[0])
        vicini = [t for t in vicini if t[0] <= KM_CAVI]
        out["approdi_cavi_100km"] = len(vicini)
        if vicini:
            out["approdi_cavi_esempi"] = [n for _, n in vicini[:3]]
    return out


# ------------------------------------------------------------------ verifica online
def verifica_coordinate(voci):
    oa = [v for v in voci if v["origine_coord"] == "ourairports"]
    wd = [v for v in voci if v["origine_coord"] == "wikidata"]
    if oa:
        try:
            testo = scarica(URL_OURAIRPORTS, timeout=120).decode("utf-8")
            tab = {}
            for r in csv.DictReader(io.StringIO(testo)):
                for k in ("gps_code", "icao_code", "ident"):
                    if r[k]:
                        tab[r[k]] = r
            for v in oa:
                r = tab.get(v["rif_coord"])
                if not r:
                    avviso(f"'{v['nome']}': codice {v['rif_coord']} non trovato in OurAirports")
                    continue
                d = km(v["lat"], v["lon"], float(r["latitude_deg"]), float(r["longitude_deg"]))
                if d > KM_SCARTO_COORD:
                    avviso(f"'{v['nome']}': coordinate a {d:.1f} km da OurAirports {v['rif_coord']}")
            print(f"OurAirports: controllate {len(oa)} coordinate", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            avviso(f"OurAirports non raggiungibile ({e}): verifica saltata")
    if wd:
        try:
            trovate = {}
            qids = sorted({v["rif_coord"] for v in wd})
            for k in range(0, len(qids), 60):
                valori = " ".join("wd:" + q for q in qids[k:k + 60])
                q = f"SELECT ?i ?c WHERE {{ VALUES ?i {{{valori}}} ?i wdt:P625 ?c }}"
                url = URL_WIKIDATA + "?format=json&query=" + urllib.parse.quote(q)
                d = json.loads(scarica(url, timeout=90))
                for b in d["results"]["bindings"]:
                    m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", b["c"]["value"])
                    if m:
                        trovate.setdefault(b["i"]["value"].rsplit("/", 1)[1], (float(m.group(2)), float(m.group(1))))
            for v in wd:
                c = trovate.get(v["rif_coord"])
                if not c:
                    avviso(f"'{v['nome']}': {v['rif_coord']} senza coordinate su Wikidata")
                    continue
                d = km(v["lat"], v["lon"], c[0], c[1])
                if d > KM_SCARTO_COORD:
                    avviso(f"'{v['nome']}': coordinate a {d:.1f} km da Wikidata {v['rif_coord']}")
            print(f"Wikidata: controllate {len(wd)} coordinate", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            avviso(f"Wikidata non raggiungibile ({e}): verifica saltata")


# ------------------------------------------------------------------ uscita
def elemento(v, n, collegamenti):
    fonti_testo = [f for f in v["fonti"] if not f["fonte"].startswith(("OurAirports", "Wikidata"))] or v["fonti"]
    principale = max(fonti_testo, key=lambda f: f["data_fonte"])
    ident = v.get("rif_coord", "") if v["origine_coord"] == "ourairports" and re.match(r"^[A-Z]{4}$", v.get("rif_coord", "")) else ""
    e = {
        "id": f"BM-{n:03d}", "classe": "fisso", "categoria": TIPI[v["tipo"]], "tipo": v["tipo"],
        "nome": v["nome"], "breve": v.get("breve", ""), "identificativo": ident,
        "appartenenza": v["appartenenza"], "utenti": v["utenti"], "paese": v["paese"],
        "regione": v.get("regione", ""), "teatro": v["teatro"], "stato": v["stato"], "anno": v.get("anno"),
        "lat": round(v["lat"], 4), "lon": round(v["lon"], 4), "origine_coord": v["origine_coord"],
        "rif_coord": v.get("rif_coord", ""), "precisione_km": v["precisione_km"],
        "forze": v.get("forze", ""), "perche_conta": v["perche_conta"], "vicino_a": v.get("vicino_a", []),
        "fonte": principale["fonte"], "link": principale["link"], "data_fonte": principale["data_fonte"],
        "affidabilita": v["affidabilita"], "verificata": bool(v.get("verificata_oggi")),
        "note": v.get("note", ""),
        "fonti": [{"fonte": f["fonte"], "link": f["link"], "data_fonte": f["data_fonte"], "riletta": bool(f.get("letta"))}
                  for f in v["fonti"]],
    }
    e.update(collegamenti)
    return e


def riepilogo(elementi):
    def conta(chiave):
        c = {}
        for e in elementi:
            c[e[chiave]] = c.get(e[chiave], 0) + 1
        return dict(sorted(c.items(), key=lambda t: -t[1]))
    return {"basi": len(elementi), "per_appartenenza": conta("appartenenza"), "per_stato": conta("stato"),
            "per_teatro": conta("teatro"), "per_tipo": conta("tipo"),
            "verificate_su_fonte_letta": sum(1 for e in elementi if e["verificata"]),
            "coordinate_stimate": sum(1 for e in elementi if e["origine_coord"] == "stimata"),
            "vicine_a_un_passaggio_entro_300km": sum(1 for e in elementi if e.get("stretto_vicino", {}).get("km", 1e9) <= 300),
            "con_approdi_di_cavi_entro_100km": sum(1 for e in elementi if e.get("approdi_cavi_100km", 0) > 0)}


FONTI_GENERALI = [
    {"nome": "OurAirports", "link": "https://ourairports.com/data/", "licenza": "pubblico dominio", "data_dato": ""},
    {"nome": "Wikidata (coordinate P625)", "link": "https://www.wikidata.org/", "licenza": "CC0", "data_dato": ""},
    {"nome": "Wikipedia in inglese (descrizioni)", "link": "https://en.wikipedia.org/", "licenza": "CC BY-SA 4.0", "data_dato": ""},
    {"nome": "Congressional Research Service, IF12389", "link": "https://www.everycrsreport.com/files/2026-04-08_IF12389_eafb70071b5b5ecad891e918583c30947bf78996.html", "licenza": "pubblico dominio (governo USA)", "data_dato": "2026-04-08"},
    {"nome": "Stampa e centri studi citati in ogni punto (Stars and Stripes, Meduza, Africa Defense Forum, Al Jazeera, ITV, Newsweek, Critical Threats, USNI News e altri)", "link": "", "licenza": "citazione con link; testi non copiati", "data_dato": ""},
]


def main():
    controlla = "--controlla" in sys.argv
    verifica = "--verifica-coordinate" in sys.argv
    if not os.path.exists(CURATO):
        print(f"manca {CURATO}", file=sys.stderr)
        return 1
    try:
        with open(CURATO, encoding="utf-8") as f:
            curato = json.load(f)
    except Exception as e:  # noqa: BLE001
        print(f"{CURATO} non è JSON valido: {e}", file=sys.stderr)
        return 1
    voci = curato.get("basi", [])

    labels = carica("labels.json") or {}
    stretti = labels.get("straits", [])
    nomi_luoghi = {x["n"] for k in ("straits", "seas", "regions") for x in labels.get(k, [])}
    valide = [v for i, v in enumerate(voci) if valida(v, i, nomi_luoghi)]
    scarta = controlla_duplicati(valide, punti_esistenti())
    valide = [v for i, v in enumerate(valide) if i not in scarta]
    if verifica:
        verifica_coordinate(valide)

    rotte_d = carica("rotte.json") or {}
    rotte = rotte_d.get("rotte", [])
    cavi = carica("cavi.json")
    approdi = cavi.get("approdi", []) if cavi else None

    ordine = sorted(valide, key=lambda v: (list(TEATRI).index(v["teatro"]), v["appartenenza"], v["nome"]))
    elementi = [elemento(v, n + 1, collega(v, stretti, rotte, approdi)) for n, v in enumerate(ordine)]
    rie = riepilogo(elementi)
    print(f"basi valide: {len(elementi)} su {len(voci)}; errori {len(errori)}, avvisi {len(avvisi)}", file=sys.stderr)
    if controlla:
        return 0
    out = {
        "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": FONTI_GENERALI,
        "nota": ("Principali installazioni militari nel mondo, soprattutto all'estero, con il loro significato strategico. "
                 "Completa fissi.json (Medio Oriente), italia.json, iran.json e difesa.json, senza duplicarli. "
                 "Solo fonti aperte; forze presenti come ordini di grandezza pubblicati. 'verificata' = almeno una fonte "
                 "letta alla data di compilazione; le altre voci citano fatti consolidati da rileggere. Paese = chi "
                 "controlla il territorio (per le isole contese è indicato nelle note). Teatri: "
                 + ", ".join(f"{k} = {n}" for k, n in TEATRI.items()) + "."),
        "compilato": curato.get("compilato", ""),
        "riepilogo": rie,
        "elementi": elementi,
        "errori": errori,
        "avvisi": avvisi,
    }
    with open(USCITA, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"scritto {USCITA} ({os.path.getsize(USCITA) // 1024} KB)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
