#!/usr/bin/env python3
"""Evoluzione del fronte ucraino: aree controllate dalla Russia in Ucraina, una istantanea al mese.

Scrive docs/data/fronte-storico.json.

Fonti
- DeepStateMap (deepstatemap.live), API pubblica dello storico: /api/history/public (elenco degli
  aggiornamenti) e /api/history/<id>/geojson (la mappa di quell'aggiornamento). Copre dal 3/4/2022.
- ISW e Critical Threats Project (AEI), servizio ArcGIS pubblico "UkraineCoTTimelapse_Full_Length_view":
  aree che ISW valuta sotto controllo russo, giorno per giorno dal 24/2/2022 al 31/12/2024. Serve per
  le istantanee del 24/2/2022 e del 1/3/2022 (prima dello storico DeepState) e per il confronto tra fonti.

Cosa fa a ogni esecuzione
- tiene le istantanee già salvate (non riscarica nulla se l'aggiornamento DeepState scelto è lo stesso);
- aggiunge l'istantanea del 1° di ogni mese che manca (l'ultimo aggiornamento DeepState pubblicato
  entro la fine di quel giorno) e sostituisce l'istantanea "ultima" con l'aggiornamento più recente;
- ricalcola km², variazioni, serie e riepiloghi.
Opzioni: --ricostruisci (rifà tutte le istantanee), --senza-confronto (salta il confronto con ISW).
Variabile FRONTE_CACHE: cartella dove tenere i file scaricati (utile in sviluppo).

Richiede shapely (vedi requirements.txt): unione, semplificazione e aree dei poligoni.
"""
import datetime as dt
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request

try:
    import numpy as np
    import shapely
    from shapely.geometry import MultiPolygon, Polygon, shape
    from shapely.ops import unary_union
except ImportError:  # pragma: no cover
    shapely = None

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(os.path.dirname(QUI))
OUT = os.path.join(RADICE, "docs", "data", "fronte-storico.json")
MOMENTI = os.path.join(QUI, "momenti.json")
CONFINE = os.path.join(QUI, "ucraina.json")
CACHE = os.environ.get("FRONTE_CACHE")

UA = "monitor-geoeconomico/1.0 (osservatorio OSINT personale, non commerciale)"
DS_INDICE = "https://deepstatemap.live/api/history/public"
DS_GEO = "https://deepstatemap.live/api/history/{id}/geojson"
DS_LINK = "https://deepstatemap.live/en"
ISW_BASE = "https://services5.arcgis.com/SaBe5HMtmnbqSWlu/ArcGIS/rest/services/"
ISW_STORICO = "UkraineCoTTimelapse_Full_Length_view"  # layer 0 controllo, 1 avanzate
# Confronto DeepState / ISW: (data, servizio ISW, layer del controllo valutato)
CONFRONTI = [
    ("2022-04-03", ISW_STORICO, 0),
    ("2022-09-01", ISW_STORICO, 0),
    ("2023-06-01", ISW_STORICO, 0),
    ("2024-12-01", ISW_STORICO, 0),
    ("2025-11-01", "Russo_Ukraine_War_November_2025_Timelapse", 33),
    ("2026-04-01", "Ukraine_Timelapse_April_2026_WFL1", 33),
]

SUP_UCRAINA = 603628  # km², superficie ufficiale dell'Ucraina con la Crimea
TOL_RU = 1.5          # km, tolleranza di semplificazione delle aree russe
TOL_GRIGIA = 1.0      # km, tolleranza della zona grigia
MIN_PARTE = 0.5       # km², parti più piccole scartate dopo la semplificazione
MIN_BUCO = 1.0        # km², buchi più piccoli scartati
INIZIO_DS = dt.date(2022, 4, 1)

errori = []


# ---------------------------------------------------------------- rete
def scarica(url, nome_cache=None, tentativi=3):
    if CACHE and nome_cache:
        p = os.path.join(CACHE, nome_cache)
        if os.path.exists(p):
            with open(p, "rb") as f:
                return f.read()
    ultimo = None
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                dati = r.read()
            if CACHE and nome_cache:
                os.makedirs(CACHE, exist_ok=True)
                with open(os.path.join(CACHE, nome_cache), "wb") as f:
                    f.write(dati)
            return dati
        except Exception as e:  # noqa: BLE001
            ultimo = e
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"{url}: {ultimo}")


# ---------------------------------------------------------------- proiezione equivalente (Lambert azimutale)
R = 6371.0072  # raggio autalico, km
LAT0, LON0 = math.radians(48.5), math.radians(32.0)


def _avanti(x, y, z=None):
    lon = np.radians(np.asarray(x, dtype=float))
    lat = np.radians(np.asarray(y, dtype=float))
    k = np.sqrt(2 / (1 + math.sin(LAT0) * np.sin(lat) + math.cos(LAT0) * np.cos(lat) * np.cos(lon - LON0)))
    return (R * k * np.cos(lat) * np.sin(lon - LON0),
            R * k * (math.cos(LAT0) * np.sin(lat) - math.sin(LAT0) * np.cos(lat) * np.cos(lon - LON0)))


def _indietro(x, y, z=None):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    rho = np.hypot(x, y)
    rho = np.where(rho == 0, 1e-12, rho)
    c = 2 * np.arcsin(np.clip(rho / (2 * R), -1, 1))
    lat = np.arcsin(np.cos(c) * math.sin(LAT0) + y * np.sin(c) * math.cos(LAT0) / rho)
    lon = LON0 + np.arctan2(x * np.sin(c), rho * math.cos(LAT0) * np.cos(c) - y * math.sin(LAT0) * np.sin(c))
    return np.degrees(lon), np.degrees(lat)


def in_km(g):
    return shapely.transform(g, lambda c: np.column_stack(_avanti(c[:, 0], c[:, 1])))


def km2(g):
    return in_km(g).area if g is not None and not g.is_empty else 0.0


# ---------------------------------------------------------------- geometrie
def poligoni(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    if g.geom_type in ("MultiPolygon", "GeometryCollection"):
        out = []
        for p in g.geoms:
            out.extend(poligoni(p))
        return out
    return []


def pulisci(g):
    g = shapely.force_2d(g)
    if not g.is_valid:
        g = shapely.make_valid(g)
    return unary_union(poligoni(g)) if g.geom_type != "Polygon" else g


_ucraina = None


def ucraina():
    global _ucraina
    if _ucraina is None:
        with open(CONFINE, encoding="utf-8") as f:
            d = json.load(f)
        _ucraina = unary_union([Polygon(r) for r in d["g"]]).buffer(0.05)
    return _ucraina


def solo_ucraina(g):
    """Tiene le parti il cui punto interno cade in Ucraina (scarta Transnistria, Russia, ecc.)."""
    u = ucraina()
    return unary_union([p for p in poligoni(g) if u.contains(p.representative_point())])


def codifica(g, tol, con_buchi=True):
    """Semplifica in km, torna a lon/lat con 3 decimali. Restituisce (parti esterne, buchi)."""
    if g is None or g.is_empty:
        return [], []
    s = in_km(g).simplify(tol, preserve_topology=True)
    esterni, buchi = [], []

    def anello(coords):
        xs, ys = zip(*coords)
        lon, lat = _indietro(xs, ys)
        out = []
        for a, b in zip(lon.tolist(), lat.tolist()):
            p = [round(a, 3), round(b, 3)]
            if not out or out[-1] != p:
                out.append(p)
        if out and out[0] != out[-1]:
            out.append(out[0])
        return out if len(out) >= 4 else None

    for p in poligoni(s):
        if p.area < MIN_PARTE:
            continue
        a = anello(p.exterior.coords)
        if a:
            esterni.append(a)
        if con_buchi:
            for h in p.interiors:
                if Polygon(h).area >= MIN_BUCO:
                    b = anello(h.coords)
                    if b:
                        buchi.append(b)
    esterni.sort(key=len, reverse=True)
    return esterni, buchi


# ---------------------------------------------------------------- DeepStateMap
def classe_ds(props):
    """'ru' (occupato, Crimea, ORDLO, Tuzla), 'grigia' (stato incerto / conteso) o None."""
    n = (props.get("name") or "").lower()
    fill = (props.get("fill") or "").lower()
    if "geojson.status.occupied" in n:
        return "ru"
    if "geojson.status.unknown" in n:
        return "grigia"
    if any(k in n for k in ("territories.crimea", "territories.ordlo", "territories.tuzla")):
        return "ru"
    if "geojson." in n:
        return None
    # aggiornamenti vecchi (2022-2023) senza chiave: nome ucraino e colore
    if "придністров" in n or fill == "#ff5252":
        return None
    if fill in ("#880e4f", "#000000"):
        return "ru" if any(k in n for k in ("крим", "ордло", "тузла")) else None
    if fill in ("#bcaaa4", "#bdbdbd"):
        return "grigia"
    if fill == "#a52714":
        return "grigia" if "невідомо" in n else "ru"
    return None


def solo_2014(props):
    n = (props.get("name") or "").lower()
    return any(k in n for k in ("territories.crimea", "territories.ordlo", "territories.tuzla",
                                "крим", "ордло", "тузла"))


def indice_ds():
    d = json.loads(scarica(DS_INDICE))
    d = [r for r in d if r.get("status", True) and r.get("createdAt")]
    d.sort(key=lambda r: r["createdAt"])
    return d


def scegli(indice, giorno):
    """Ultimo aggiornamento pubblicato entro la fine del giorno; se non c'è, il primo disponibile."""
    lim = f"{giorno.isoformat()}T23:59:59"
    prima = [r for r in indice if r["createdAt"][:19] <= lim]
    return prima[-1] if prima else indice[0]


def geojson_ds(id_):
    return json.loads(scarica(DS_GEO.format(id=id_), f"ds_{id_}.json"))


def aree_ds(gj, solo_pre=False):
    ru, gr = [], []
    for f in gj.get("features", []):
        geo = f.get("geometry") or {}
        if geo.get("type") not in ("Polygon", "MultiPolygon", "GeometryCollection"):
            continue
        p = f.get("properties") or {}
        if solo_pre:
            c = "ru" if solo_2014(p) else None
        else:
            c = classe_ds(p)
        if not c:
            continue
        try:
            g = pulisci(shape(geo))
        except Exception:  # noqa: BLE001
            continue
        (ru if c == "ru" else gr).append(g)
    ru_u = solo_ucraina(unary_union(ru)) if ru else Polygon()
    gr_u = solo_ucraina(unary_union(gr)).difference(ru_u) if gr else Polygon()
    return ru_u, gr_u


# ---------------------------------------------------------------- ISW / CTP
def aree_isw(giorno, servizio=ISW_STORICO, layer=0):
    d0 = dt.date.fromisoformat(giorno)
    d1 = d0 + dt.timedelta(days=1)
    where = f"datetime >= TIMESTAMP '{d0} 00:00:00' AND datetime < TIMESTAMP '{d1} 00:00:00'"
    q = urllib.parse.urlencode({"where": where, "outFields": "datetime", "outSR": 4326,
                                "f": "geojson", "returnGeometry": "true"})
    url = f"{ISW_BASE}{servizio}/FeatureServer/{layer}/query?{q}"
    gj = json.loads(scarica(url, f"isw_{servizio}_{layer}_{giorno}.json"))
    if "error" in gj:
        raise RuntimeError(f"ISW {servizio}/{layer} {giorno}: {gj['error']}")
    gs = [pulisci(shape(f["geometry"])) for f in gj.get("features", []) if f.get("geometry")]
    return unary_union(gs) if gs else Polygon()


# ---------------------------------------------------------------- istantanee
def istantanea(data, fonte, ru, gr, **extra):
    g, buchi = codifica(ru, TOL_RU)
    gg, _ = codifica(gr, TOL_GRIGIA, con_buchi=False)
    k = round(km2(ru))
    rec = {"data": data, **extra, "fonte": fonte, "km2": k, "km2_var": None,
           "pct_ucraina": round(100 * k / SUP_UCRAINA, 2), "km2_grigia": round(km2(gr)),
           "g": g}
    if buchi:
        rec["buchi"] = buchi
    if gg:
        rec["g_grigia"] = gg
    return rec


def mesi(da, a):
    d = da
    while d <= a:
        yield d
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)


def costruisci(vecchie, ricostruisci):
    oggi = dt.datetime.now(dt.timezone.utc).date()
    per_data = {} if ricostruisci else {s["data"]: s for s in vecchie if not s.get("ultima")}
    nuove = []

    try:
        indice = indice_ds()
    except Exception as e:  # noqa: BLE001
        errori.append(f"DeepStateMap: elenco degli aggiornamenti non letto ({e}); tengo le istantanee salvate")
        return vecchie

    # 1) prima dell'invasione: Crimea, ORDLO e Tuzla come le disegna DeepState (linee 2014-2022)
    primo = indice[0]
    s = per_data.get("2022-02-23")
    if not s or s.get("id_fonte") != primo["id"]:
        try:
            ru, gr = aree_ds(geojson_ds(primo["id"]), solo_pre=True)
            s = istantanea("2022-02-23", "DeepStateMap", ru, gr, id_fonte=primo["id"],
                           data_fonte=primo["createdAt"][:16] + "Z",
                           nota="Prima dell'invasione: Crimea, Sebastopoli e le aree di Donetsk e Luhansk "
                                "fuori dal controllo di Kyiv dal 2014-2015 (poligoni 'ORDLO' e 'Crimea' di DeepState).")
        except Exception as e:  # noqa: BLE001
            errori.append(f"istantanea 2022-02-23: {e}")
            s = None
    if s:
        nuove.append(s)

    # 2) 24/2 e 1/3/2022 da ISW/CTP (DeepState non ha storico prima del 3/4/2022)
    for giorno in ("2022-02-24", "2022-03-01"):
        s = per_data.get(giorno)
        if not s:
            try:
                ru = solo_ucraina(aree_isw(giorno, ISW_STORICO, 0))
                try:
                    av = solo_ucraina(aree_isw(giorno, ISW_STORICO, 1)).difference(ru)
                except Exception:  # noqa: BLE001
                    av = Polygon()
                s = istantanea(giorno, "ISW/CTP", ru, av, data_fonte=giorno,
                               nota="Controllo russo valutato da ISW/CTP a fine giornata; grigio = 'avanzate russe valutate' di ISW.")
            except Exception as e:  # noqa: BLE001
                errori.append(f"istantanea {giorno} (ISW): {e}")
                s = None
        if s:
            nuove.append(s)

    # 3) una istantanea DeepState al mese, dal 1/4/2022
    for giorno in mesi(INIZIO_DS, oggi):
        r = scegli(indice, giorno)
        s = per_data.get(giorno.isoformat())
        if not s or s.get("id_fonte") != r["id"]:
            try:
                ru, gr = aree_ds(geojson_ds(r["id"]))
                s = istantanea(giorno.isoformat(), "DeepStateMap", ru, gr, id_fonte=r["id"],
                               data_fonte=r["createdAt"][:16] + "Z")
                time.sleep(1)
            except Exception as e:  # noqa: BLE001
                errori.append(f"istantanea {giorno}: {e}")
                s = None
        if s:
            nuove.append(s)

    # 4) l'aggiornamento più recente, se è dopo l'ultima istantanea mensile
    r = indice[-1]
    if nuove and r["id"] != nuove[-1].get("id_fonte"):
        vecchia = next((s for s in vecchie if s.get("ultima")), None)
        if vecchia and vecchia.get("id_fonte") == r["id"] and not ricostruisci:
            nuove.append(vecchia)
        else:
            try:
                ru, gr = aree_ds(geojson_ds(r["id"]))
                nuove.append(istantanea(r["createdAt"][:10], "DeepStateMap", ru, gr, id_fonte=r["id"],
                                        data_fonte=r["createdAt"][:16] + "Z", ultima=True))
            except Exception as e:  # noqa: BLE001
                errori.append(f"istantanea più recente: {e}")
    return nuove


def variazioni(ist):
    prec = None
    for s in ist:
        s["km2_var"] = None if prec is None else s["km2"] - prec["km2"]
        if prec is not None and prec["fonte"] != s["fonte"] and prec["data"] != "2022-02-23":
            s["cambio_fonte"] = True
        prec = s


def riepilogo_anni(ist):
    """Per anno: km² al 1° gennaio (o alla prima istantanea), alla fine (1° gennaio successivo o oggi)."""
    mensili = [s for s in ist if s["data"] >= "2022-02-23"]
    anni = sorted({s["data"][:4] for s in mensili})
    out = []
    for a in anni:
        inizio = next(s for s in mensili if s["data"][:4] == a)
        fine = next((s for s in mensili if s["data"] == f"{int(a) + 1}-01-01"), mensili[-1])
        d0 = dt.date.fromisoformat(inizio["data"])
        d1 = dt.date.fromisoformat(fine["data"])
        giorni = (d1 - d0).days or 1
        var = [s["km2_var"] for s in mensili if s["data"][:4] == a and s["km2_var"] is not None
               and s["data"] > inizio["data"]]
        out.append({
            "anno": int(a), "da": inizio["data"], "a": fine["data"],
            "km2_inizio": inizio["km2"], "km2_fine": fine["km2"], "netto_km2": fine["km2"] - inizio["km2"],
            "km2_al_giorno": round((fine["km2"] - inizio["km2"]) / giorni, 1),
            "km2_al_mese": round((fine["km2"] - inizio["km2"]) / giorni * 30.44),
            "mesi_in_guadagno": sum(1 for v in var if v > 0), "mesi_in_perdita": sum(1 for v in var if v < 0),
        })
    return out


def arricchisci_momenti(momenti, ist):
    for m in momenti:
        d = m.get("data", "")[:10]
        prima = [s for s in ist if s["data"] <= d]
        dopo = [s for s in ist if s["data"] > d]
        if prima:
            m["km2_prima"] = [prima[-1]["data"], prima[-1]["km2"]]
        if dopo:
            m["km2_dopo"] = [dopo[0]["data"], dopo[0]["km2"]]
    return momenti


def confronti_isw(ist, vecchi):
    fatti = {c["data"]: c for c in (vecchi or [])}
    out = []
    indice = None
    for giorno, servizio, layer in CONFRONTI:
        if giorno in fatti:
            out.append(fatti[giorno])
            continue
        if giorno > dt.datetime.now(dt.timezone.utc).date().isoformat():
            continue
        try:
            if indice is None:
                indice = indice_ds()
            r = scegli(indice, dt.date.fromisoformat(giorno))
            ds, _ = aree_ds(geojson_ds(r["id"]))
            isw = solo_ucraina(aree_isw(giorno, servizio, layer))
            if isw.is_empty:
                raise RuntimeError("nessun poligono ISW per quel giorno")
            out.append({
                "data": giorno, "deepstate_aggiornamento": r["createdAt"][:16] + "Z",
                "isw_servizio": f"{servizio}/{layer}",
                "km2_deepstate": round(km2(ds)), "km2_isw": round(km2(isw)),
                "differenza_km2": round(km2(ds) - km2(isw)),
                "solo_deepstate_km2": round(km2(ds.difference(isw))),
                "solo_isw_km2": round(km2(isw.difference(ds))),
            })
        except Exception as e:  # noqa: BLE001
            errori.append(f"confronto ISW {giorno}: {e}")
    return out


def main():
    if shapely is None:
        print("serve shapely: pip install -r raccolta/fronte/requirements.txt", file=sys.stderr)
        sys.exit(1)
    ricostruisci = "--ricostruisci" in sys.argv
    vecchio = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            vecchio = json.load(f)
    ist = costruisci(vecchio.get("istantanee", []), ricostruisci)
    if not ist:
        errori.append("nessuna istantanea: file non aggiornato")
        print("\n".join(errori), file=sys.stderr)
        sys.exit(1)
    ist.sort(key=lambda s: s["data"])
    variazioni(ist)

    with open(MOMENTI, encoding="utf-8") as f:
        mom = json.load(f)
    confronti = vecchio.get("confronto_isw", [])
    if "--senza-confronto" not in sys.argv:
        confronti = confronti_isw(ist, confronti)

    mensili = [s for s in ist if not s.get("ultima")]
    massimo = max(ist, key=lambda s: s["km2"])
    ds = [s for s in ist if s["fonte"] == "DeepStateMap" and s["data"] >= "2022-04-01"]
    massimo_ds = max(ds, key=lambda s: s["km2"]) if ds else None
    out = {
        "aggiornato": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": [
            {"nome": "DeepStateMap.live (DEEPSTATEUATECH LLC), API dello storico",
             "link": DS_LINK, "api": DS_INDICE,
             "licenza": "diritti riservati; accordo di licenza https://deepstatemap.live/license-en.html: "
                        "API gratuita per attività di volontariato e per la difesa dell'Ucraina, uso commerciale "
                        "solo con permesso, vietato ridistribuire o fare da proxy all'API; materiali visivi e "
                        "testuali liberamente usabili citando DeepStateMap con link. Qui: poligoni derivati, "
                        "semplificati e citati, per un progetto personale non commerciale.",
             "data_dato": f"{ds[0]['data_fonte'][:10] if ds else '?'} / {ist[-1].get('data_fonte', '')[:10]}"},
            {"nome": "ISW e AEI Critical Threats Project, 'Assessed Russian-controlled Ukrainian Territory' (ArcGIS)",
             "link": ISW_BASE + ISW_STORICO + "/FeatureServer",
             "licenza": "© Institute for the Study of War e AEI Critical Threats Project; nessuna licenza aperta "
                        "dichiarata; servizio pubblico senza login; citare ISW/CTP",
             "data_dato": "2022-02-24 / 2022-03-01 (istantanee); confronti fino al 2026-04-01"},
            {"nome": "Natural Earth 1:10m, confini con il punto di vista ucraino (solo per filtrare)",
             "link": "https://www.naturalearthdata.com/", "licenza": "pubblico dominio", "data_dato": "v5.1"},
        ],
        "nota": ("Aree dell'Ucraina controllate od occupate dalla Russia (categorie unite: 'occupato', Crimea, "
                 "ORDLO, isola di Tuzla), un'istantanea al 1° di ogni mese: l'ultimo aggiornamento DeepState "
                 "pubblicato entro quel giorno. Dal 3/4/2022 la fonte è DeepStateMap; il 24/2 e l'1/3/2022 "
                 "vengono da ISW/CTP (DeepState non ha storico prima), il 23/2/2022 è la situazione prima "
                 "dell'invasione. 'grigia' = zona a stato incerto o contesa di DeepState (per ISW: avanzate "
                 "russe valutate), tenuta separata e non sommata ai km². km² calcolati sui poligoni originali "
                 "(proiezione equivalente di Lambert); le geometrie salvate sono semplificate "
                 f"({TOL_RU} km le aree russe, {TOL_GRIGIA} km la zona grigia; parti sotto {MIN_PARTE} km² "
                 "tolte) con coordinate a 3 decimali. g = parti esterne [[lon,lat],...], buchi = anelli interni "
                 "(riempimento pari-dispari). km2_var = differenza con l'istantanea precedente; dove "
                 "cambio_fonte=true la differenza mescola due mappe diverse. pct_ucraina su 603.628 km². "
                 "Mappe OSINT: valutazioni, non dati ufficiali."),
        "istantanee": ist,
        "serie_km2": [[s["data"], s["km2"]] for s in ist],
        "serie_var_km2": [[s["data"], s["km2_var"]] for s in mensili if s["km2_var"] is not None],
        "serie_grigia_km2": [[s["data"], s["km2_grigia"]] for s in ist],
        "per_anno": riepilogo_anni(mensili),
        "massimo": {"data": massimo["data"], "km2": massimo["km2"], "fonte": massimo["fonte"]},
        "massimo_deepstate": ({"data": massimo_ds["data"], "km2": massimo_ds["km2"]} if massimo_ds else None),
        "momenti_chiave": arricchisci_momenti(mom.get("momenti", []), ist),
        "confronto_isw": confronti,
        "errori": errori,
    }
    testo = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(testo)
    print(f"scritto {OUT}: {len(ist)} istantanee, {len(testo) / 1e6:.2f} MB, errori: {len(errori)}")
    for e in errori:
        print("  -", e)


if __name__ == "__main__":
    main()
