#!/usr/bin/env python3
"""Catena del valore dell'AI, dalla miniera al data center: costruisce docs/data/supply-chain-ai.json.

Solo libreria standard di Python 3, nessuna rete. Uso, dalla radice del repository:

    python3 raccolta/supply-chain-ai/raccogli.py              # valida e scrive il file
    python3 raccolta/supply-chain-ai/raccogli.py --valida     # valida soltanto, non scrive
    python3 raccolta/supply-chain-ai/raccogli.py --oggi 2026-11-09

Le voci sono curate a mano in raccolta/supply-chain-ai/*.json (anelli, nodi, archi, colli,
controlli, materie, titoli), ciascuna con fonte, link, data e affidabilità. Lo script:
1. controlla schema, codici paese, coordinate, date, link, riferimenti incrociati;
2. prende coordinate e dati da altri livelli dell'osservatorio (ai.json, ai-mondo.json,
   stretti-dettaglio.json) invece di riscriverli;
3. CALCOLA le quote dei paesi dalle tabelle USGS (materie.json), i giorni alle scadenze dei
   controlli all'export, i valori degli indicatori che vengono da altri file (prezzi.json,
   portwatch.json, cavi-incidenti.json) e lo stato dei colli di bottiglia rispetto alle soglie;
4. aggiunge legami con la rete elettrica (linee >= 380 kV in rete-elettrica.json) e con i cavi
   sottomarini (cavi.json).
Ogni problema finisce in "errori" (bloccante per --valida) o in "avvisi" (dati vecchi, mancanti).
"""

import argparse
import datetime as dt
import json
import math
import os
import re
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(os.path.dirname(QUI))
DATI = os.path.join(RADICE, "docs", "data")
USCITA = os.path.join(DATI, "supply-chain-ai.json")

ANELLI_ID = ["materie", "attrezzature", "fabbricazione", "packaging-memoria",
             "progettazione", "server-rete", "logistica", "energia-dc"]
AFFIDABILITA = {"alta", "media", "bassa"}
STATI_CONTROLLO = {"in-vigore", "sospeso", "incerto", "proposto", "interrotto"}
STATI_ARCO = {"attivo", "ridotto", "interrotto", "storico"}
MODI = {"aereo", "nave", "camion", "misto", "rete"}
TIPI_ARCO = {"fatto", "valutazione"}
# Paesi ammessi (ISO 3166-1 alfa-2) usati in questo livello; l'elenco evita refusi.
PAESI = {"US", "CN", "TW", "KR", "JP", "NL", "DE", "IE", "IL", "IN", "SG", "MY", "AE", "QA", "UA", "RU",
         "CD", "RW", "NG", "BR", "AU", "MM", "TH", "MG", "CL", "PE", "ZM", "MX", "MN", "ZA", "VN", "ES",
         "DZ", "CA", "PL", "NO", "FR", "EE", "GL", "OM", "ET", "BE", "IT", "GB", "FI", "SE"}
NOMI_PAESE = {"CN": "Cina", "US": "Stati Uniti", "AU": "Australia", "MM": "Myanmar", "TH": "Thailandia",
              "IN": "India", "MG": "Madagascar", "RU": "Russia", "BR": "Brasile", "NG": "Nigeria",
              "CL": "Cile", "CD": "Congo (RD)", "PE": "Perù", "ZM": "Zambia", "RW": "Ruanda",
              "ET": "Etiopia", "MX": "Messico", "MN": "Mongolia", "ZA": "Sudafrica", "VN": "Vietnam",
              "ES": "Spagna", "QA": "Qatar", "DZ": "Algeria", "CA": "Canada", "PL": "Polonia",
              "NO": "Norvegia", "FR": "Francia", "JP": "Giappone", "GL": "Groenlandia", "KR": "Corea del Sud",
              "TW": "Taiwan", "NL": "Paesi Bassi", "DE": "Germania"}
GIORNI_VECCHIO = 120  # un valore manuale congiunturale più vecchio di così va ricontrollato

ERRORI, AVVISI = [], []


def errore(msg):
    ERRORI.append(msg)


def avviso(msg):
    AVVISI.append(msg)


def leggi(percorso, obbligatorio=True):
    try:
        with open(percorso, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        (errore if obbligatorio else avviso)("file mancante: %s" % os.path.relpath(percorso, RADICE))
    except json.JSONDecodeError as e:
        errore("JSON non valido in %s: %s" % (os.path.relpath(percorso, RADICE), e))
    return None


def data_valida(s):
    """Accetta AAAA, AAAA-MM, AAAA-MM-GG. Restituisce la data (primo giorno) o None."""
    if not isinstance(s, str):
        return None
    for fmt, n in (("%Y-%m-%d", 10), ("%Y-%m", 7), ("%Y", 4)):
        if len(s) == n:
            try:
                return dt.datetime.strptime(s, fmt).date()
            except ValueError:
                return None
    return None


def controlla_fonte(voce, dove, obbligatoria=True):
    for campo in ("fonte", "link", "data_fonte", "affidabilita"):
        if not voce.get(campo):
            if obbligatoria:
                errore("%s: manca '%s'" % (dove, campo))
            return
    if not re.match(r"^https?://", voce["link"]):
        errore("%s: link non valido %r" % (dove, voce["link"]))
    if voce["affidabilita"] not in AFFIDABILITA:
        errore("%s: affidabilità %r non ammessa" % (dove, voce["affidabilita"]))
    if data_valida(voce["data_fonte"]) is None:
        errore("%s: data_fonte %r non nel formato AAAA[-MM[-GG]]" % (dove, voce["data_fonte"]))


def prendi(d, percorso):
    """prendi({'a': {'b': 1}}, 'a.b') -> 1"""
    for k in percorso.split("."):
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def dist_segmento_km(lat, lon, a, b):
    """Distanza approssimata (proiezione equirettangolare locale) da un punto a un segmento [lon,lat]."""
    k = math.cos(math.radians(lat))
    px, py = lon * k, lat
    ax, ay, bx, by = a[0] * k, a[1], b[0] * k, b[1]
    dx, dy = bx - ax, by - ay
    t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    qx, qy = ax + t * dx, ay + t * dy
    return math.hypot(px - qx, py - qy) * 111.2


def fmt_num(x, dec=1):
    s = ("{:,.%df}" % dec).format(x)
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


# --------------------------------------------------------------------------------------
def carica_curati():
    nomi = ["anelli", "nodi", "archi", "colli", "controlli", "materie", "titoli"]
    out = {}
    for n in nomi:
        d = leggi(os.path.join(QUI, n + ".json"))
        out[n] = (d or {}).get("elementi", [])
        out[n + "_nota"] = (d or {}).get("nota", "")
    return out


def carica_osservatorio():
    nomi = ["ai", "ai-mondo", "stretti-dettaglio", "portwatch", "prezzi", "cavi-incidenti", "rete-elettrica", "cavi",
            "minerali", "commercio", "investimenti"]
    return {n: leggi(os.path.join(DATI, n + ".json"), obbligatorio=False) for n in nomi}


def indice_rif(oss):
    idx = {}
    for p in (oss.get("ai") or {}).get("punti", []):
        idx[("ai.json", p.get("nome"))] = p
    for p in (oss.get("ai-mondo") or {}).get("elementi", []):
        idx[("ai-mondo.json", p.get("nome"))] = p
    for p in (oss.get("stretti-dettaglio") or {}).get("elementi", []):
        idx[("stretti-dettaglio.json", p.get("id"))] = p
    return idx


# --------------------------------------------------------------------------------------
def valida_anelli(anelli):
    ids = [a.get("id") for a in anelli]
    if sorted(ids) != sorted(ANELLI_ID):
        errore("anelli.json: attesi %s, trovati %s" % (ANELLI_ID, ids))
    for a in anelli:
        for c in ("nome", "dove", "chi_controlla", "testo", "indicatori", "ordine"):
            if not a.get(c):
                errore("anello %s: manca '%s'" % (a.get("id"), c))
    return sorted(anelli, key=lambda a: a.get("ordine", 99))


def calcola_materie(materie):
    out = []
    for m in materie:
        dove = "materia %s" % m.get("id")
        controlla_fonte(m, dove)
        for c in ("id", "nome", "uso_ai", "unita", "anno"):
            if not m.get(c):
                errore("%s: manca '%s'" % (dove, c))
        r = dict(m)
        prod, mondo = m.get("produzione") or {}, m.get("mondo")
        for p in prod:
            if p not in PAESI:
                errore("%s: codice paese sconosciuto %r" % (dove, p))
        quote = []
        if m.get("quota_dichiarata"):
            for p, q in m["quota_dichiarata"].items():
                quote.append({"paese": p, "nome_paese": NOMI_PAESE.get(p, p), "quota_pct": float(q), "metodo": "dichiarata dalla fonte"})
        if prod and mondo:
            if sum(prod.values()) > mondo * 1.02 and not m.get("quota_dichiarata"):
                avviso("%s: la somma dei paesi supera il totale mondiale" % dove)
            gia = {q["paese"] for q in quote}
            for p, v in sorted(prod.items(), key=lambda kv: -kv[1]):
                if p in gia:
                    continue
                quote.append({"paese": p, "nome_paese": NOMI_PAESE.get(p, p), "valore": v,
                              "quota_pct": round(100.0 * v / mondo, 1), "metodo": "calcolata: paese / totale mondiale"})
        r["quote"] = sorted(quote, key=lambda q: -q["quota_pct"])
        if m.get("produzione_raffinazione") and m.get("mondo_raffinazione"):
            r["quote_raffinazione"] = [
                {"paese": p, "nome_paese": NOMI_PAESE.get(p, p), "valore": v,
                 "quota_pct": round(100.0 * v / m["mondo_raffinazione"], 1)}
                for p, v in sorted(m["produzione_raffinazione"].items(), key=lambda kv: -kv[1])]
        if quote:
            top = r["quote"][0]
            r["primo_produttore"] = {"paese": top["paese"], "nome_paese": top["nome_paese"], "quota_pct": top["quota_pct"]}
            copertura = sum(q["quota_pct"] for q in r["quote"])
            # indice di concentrazione Herfindahl-Hirschman (0-10.000), solo se i paesi elencati coprono quasi tutto
            r["hhi"] = round(sum(q["quota_pct"] ** 2 for q in r["quote"])) if copertura >= 80 and not m.get("quota_dichiarata") else None
            r["copertura_pct"] = round(copertura, 1)
        else:
            r["primo_produttore"] = None
            if not m.get("quota_stima"):
                avviso("%s: nessuna quota per paese (dato mancante dichiarato)" % dove)
        if m.get("quota_stima"):
            controlla_fonte(m["quota_stima"], dove + " quota_stima")
        out.append(r)
    return out


def quota_materia(materie, mid, paesi):
    m = next((x for x in materie if x["id"] == mid), None)
    if not m:
        errore("materia %r non trovata" % mid)
        return None, None
    tot = 0.0
    for p in paesi:
        q = next((x for x in m["quote"] if x["paese"] == p), None)
        if q is None:
            errore("materia %s: paese %s senza quota" % (mid, p))
            return None, m
        tot += q["quota_pct"]
    return round(tot, 1), m


def risolvi_nodi(nodi, idx, materie):
    out, visti = [], set()
    for n in nodi:
        nid = n.get("id")
        dove = "nodo %s" % nid
        if not nid or nid in visti:
            errore("%s: id mancante o duplicato" % dove)
        visti.add(nid)
        r = dict(n)
        if n.get("anello") not in ANELLI_ID:
            errore("%s: anello %r non valido" % (dove, n.get("anello")))
        if n.get("paese") not in PAESI:
            errore("%s: paese %r non valido" % (dove, n.get("paese")))
        if n.get("rif"):
            rif = n["rif"]
            chiave = (rif.get("file"), rif.get("nome") or rif.get("id"))
            src = idx.get(chiave)
            if not src:
                errore("%s: riferimento non trovato %s" % (dove, chiave))
                continue
            r["lat"], r["lon"] = src.get("lat"), src.get("lon")
            r["origine_coord"] = "da %s (%s)" % (rif["file"], src.get("origine_coord") or src.get("origine_dato") or "coordinate del livello")
            if src.get("precisione_km") is not None:
                r["precisione_km"] = src.get("precisione_km")
            base = src
            if not src.get("fonte") and src.get("flussi"):
                base = dict(src["flussi"][0])  # stretti-dettaglio: la fonte sta nel primo flusso
                base["affidabilita"] = base.get("affidabilita") or src.get("affidabilita")
            for c in ("fonte", "link", "data_fonte", "affidabilita"):
                if not r.get(c) and base.get(c):
                    r[c] = base[c]
            if not r.get("stato") and src.get("stato"):
                r["stato"] = src["stato"]
            if not r.get("note") and (src.get("note") or src.get("sintesi")):
                r["note"] = src.get("note") or src.get("sintesi")
            for c in ("mw", "mw_previsto", "nodo", "proprietario"):
                if src.get(c) is not None and c not in r:
                    r[c] = src[c]
        lat, lon = r.get("lat"), r.get("lon")
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            errore("%s: coordinate mancanti o fuori scala (%r, %r)" % (dove, lat, lon))
        if n.get("quota_da"):
            q, m = quota_materia(materie, n["quota_da"]["materia"], [n["quota_da"]["paese"]])
            if q is not None:
                r["quota"] = "%s %s%% di %s nel %s (calcolata da %s)" % (
                    NOMI_PAESE.get(n["quota_da"]["paese"], n["quota_da"]["paese"]), fmt_num(q),
                    m["nome"].split(" (")[0].lower(), m["anno"].split(" ")[0], m["fonte"].split(":")[0])
                r["quota_pct"] = q
        controlla_fonte(r, dove)
        r["categoria"] = "supply-chain-ai"
        out.append(r)
    return out


def calcola_controlli(controlli, materie_ids, oggi):
    out = []
    for c in controlli:
        dove = "controllo %s" % c.get("id")
        controlla_fonte(c, dove)
        r = dict(c)
        if c.get("paese") not in PAESI:
            errore("%s: paese non valido" % dove)
        if c.get("stato") not in STATI_CONTROLLO:
            errore("%s: stato %r non ammesso" % (dove, c.get("stato")))
        for m in c.get("materie", []):
            if m not in materie_ids:
                errore("%s: materia %r sconosciuta" % (dove, m))
        for a in c.get("anelli", []):
            if a not in ANELLI_ID:
                errore("%s: anello %r sconosciuto" % (dove, a))
        for campo in ("data_annuncio", "data_effetto", "scadenza"):
            if c.get(campo) and data_valida(c[campo]) is None:
                errore("%s: %s non valida" % (dove, campo))
        if c.get("scadenza"):
            g = (data_valida(c["scadenza"]) - oggi).days
            r["giorni_alla_scadenza"] = g
            if g < 0 and c.get("stato") == "sospeso":
                avviso("%s: la sospensione è scaduta da %d giorni: aggiornare lo stato" % (dove, -g))
        out.append(r)
    return sorted(out, key=lambda x: x.get("data_annuncio") or "")


def valuta_soglia(v, ind):
    a, c = ind.get("soglia_attenzione"), ind.get("soglia_critica")
    if v is None or a is None or c is None:
        return "non misurato" if v is None else "informativo"
    if ind.get("direzione") == "alto-male":
        return "critico" if v >= c else "attenzione" if v >= a else "normale"
    return "critico" if v <= c else "attenzione" if v <= a else "normale"


def calcola_colli(colli, oss, materie, controlli, nodi_ids, oggi):
    prezzi = {p["id"]: p for p in (oss.get("prezzi") or {}).get("serie", [])}
    pw = {p["id"]: p for p in (oss.get("portwatch") or {}).get("elementi", [])}
    inc = (oss.get("cavi-incidenti") or {}).get("elementi", [])
    ctrl = {c["id"]: c for c in controlli}
    ordine = {"normale": 0, "informativo": 0, "non misurato": 0, "attenzione": 1, "critico": 2}
    out = []
    for cb in colli:
        dove = "collo %s" % cb.get("id")
        r = dict(cb)
        if cb.get("anello") not in ANELLI_ID:
            errore("%s: anello non valido" % dove)
        for n in cb.get("nodi", []):
            if n not in nodi_ids:
                errore("%s: nodo %r inesistente" % (dove, n))
        inds = []
        for ind in cb.get("indicatori", []):
            s = ind.get("sorgente", {})
            t = s.get("tipo")
            ri = {k: v for k, v in ind.items() if k != "sorgente"}
            v = None
            if t == "manuale":
                controlla_fonte(s, dove + " indicatore manuale")
                v = s.get("valore")
                ri.update({"fonte": s.get("fonte"), "link": s.get("link"), "data": s.get("data_fonte"), "affidabilita": s.get("affidabilita")})
                d = data_valida(s.get("data_fonte") or "")
                if d and ind.get("tipo") == "congiunturale" and (oggi - d).days > GIORNI_VECCHIO:
                    avviso("%s: valore manuale «%s» del %s, da ricontrollare" % (dove, ind.get("nome"), s.get("data_fonte")))
            elif t == "prezzi":
                p = prezzi.get(s.get("id"))
                if p is None:
                    avviso("%s: serie %r assente in prezzi.json" % (dove, s.get("id")))
                else:
                    v = prendi(p, s.get("campo", "ultimo"))
                    ri.update({"fonte": "%s (prezzi.json)" % p.get("fonte"), "link": p.get("link"), "data": p.get("data"), "affidabilita": "media" if p.get("provvisorio") else "alta"})
                    if p.get("provvisorio"):
                        ri["nota"] = "serie marcata provvisoria in prezzi.json"
            elif t == "portwatch":
                p = pw.get(s.get("id"))
                if p is None:
                    avviso("%s: passaggio %r assente in portwatch.json" % (dove, s.get("id")))
                else:
                    v = prendi(p, s.get("campo"))
                    ri.update({"fonte": "IMF PortWatch (portwatch.json)", "link": "https://portwatch.imf.org/",
                               "data": p.get("ultima_data"), "affidabilita": "alta",
                               "nota": "media 7 giorni %s – %s; navi con AIS acceso" % tuple(p.get("periodo_media7", ["?", "?"]))})
                    if s.get("campo", "").startswith("var7") and p.get("media7"):
                        ri["dettaglio"] = {"navi_giorno": prendi(p, "media7.n_total"), "anno_prima": prendi(p, "media7_anno_prima.n_total")}
            elif t == "scadenza":
                c = ctrl.get(s.get("controllo"))
                if c is None:
                    errore("%s: controllo %r inesistente" % (dove, s.get("controllo")))
                else:
                    v = c.get("giorni_alla_scadenza")
                    # data = data della fonte sulla scadenza (non la data del calcolo: i giorni sono contati a oggi)
                    ri.update({"fonte": c.get("fonte"), "link": c.get("link"), "data": c.get("data_fonte") or oggi.isoformat(), "affidabilita": c.get("affidabilita"),
                               "nota": "scadenza %s; stato del controllo: %s; giorni contati al %s%s" % (
                                   c.get("scadenza"), c.get("stato"), oggi.isoformat(), ("; " + c["verifica"]) if c.get("verifica") else "")})
                    if c.get("verifica"):
                        ri["verifica"] = c["verifica"]
            elif t == "cavi-incidenti":
                lim = oggi - dt.timedelta(days=s.get("giorni", 365))
                ev = [e for e in inc if e.get("paese") == s.get("paese") and data_valida(e.get("data_evento") or "") and lim <= data_valida(e["data_evento"]) <= oggi]
                v = len(ev)
                ri.update({"fonte": "cavi-incidenti.json (osservatorio)", "link": "https://www.submarinecablemap.com/", "data": oggi.isoformat(),
                           "affidabilita": "media", "eventi": [e.get("nome") for e in ev]})
            elif t == "materie":
                q, m = quota_materia(materie, s.get("materia"), s.get("paesi", []))
                v = q
                if m:
                    ri.update({"fonte": m["fonte"], "link": m["link"], "data": m["data_fonte"], "affidabilita": m["affidabilita"],
                               "nota": "calcolata dalla produzione %s per paese" % m["anno"]})
            else:
                errore("%s: sorgente %r sconosciuta" % (dove, t))
            if isinstance(v, float):
                v = round(v, 1)
            ri["valore"] = v
            ri["stato"] = valuta_soglia(v, ind)
            if v is None:
                avviso("%s: indicatore «%s» senza valore" % (dove, ind.get("nome")))
            inds.append(ri)
        r["indicatori"] = inds
        r["stato"] = max((i["stato"] for i in inds), key=lambda s: ordine.get(s, 0)) if inds else "non misurato"
        r["stato_congiunturale"] = max((i["stato"] for i in inds if i.get("tipo") == "congiunturale"), key=lambda s: ordine.get(s, 0), default="non misurato")
        out.append(r)
    return out


def calcola_titoli(titoli, oss):
    prezzi = {p["id"]: p for p in (oss.get("prezzi") or {}).get("serie", [])}
    out = []
    for t in titoli:
        r = dict(t)
        for a in t.get("anelli", []):
            if a not in ANELLI_ID:
                errore("titolo %s: anello %r sconosciuto" % (t.get("simbolo"), a))
        pid = t.get("prezzi_id")
        if pid:
            p = prezzi.get(pid)
            if p is None:
                errore("titolo %s: prezzi_id %r non trovato in prezzi.json" % (t.get("simbolo"), pid))
            else:
                r["prezzo"] = {"ultimo": p.get("ultimo"), "valuta": p.get("valuta") or p.get("unita"), "data": p.get("data"),
                               "var": p.get("var"), "fonte": p.get("fonte"), "link": p.get("link"), "provvisorio": bool(p.get("provvisorio"))}
        r["in_prezzi"] = bool(pid)
        out.append(r)
    return out


def calcola_archi(archi, nodi):
    pos = {n["id"]: n for n in nodi}
    out, visti = [], set()
    for a in archi:
        dove = "arco %s" % a.get("id")
        if a.get("id") in visti:
            errore("%s: id duplicato" % dove)
        visti.add(a.get("id"))
        controlla_fonte(a, dove)
        for campo, ammessi in (("modo", MODI), ("stato", STATI_ARCO), ("tipo", TIPI_ARCO)):
            if a.get(campo) not in ammessi:
                errore("%s: %s %r non ammesso" % (dove, campo, a.get(campo)))
        da, aa = pos.get(a.get("da")), pos.get(a.get("a"))
        if not da or not aa:
            errore("%s: nodo di partenza o arrivo inesistente (%s → %s)" % (dove, a.get("da"), a.get("a")))
            continue
        for v in a.get("via", []):
            if v not in pos:
                errore("%s: passaggio %r inesistente" % (dove, v))
        r = dict(a)
        r.update({"anello_da": da["anello"], "anello_a": aa["anello"], "da_nome": da["nome"], "a_nome": aa["nome"],
                  "da_lat": da["lat"], "da_lon": da["lon"], "a_lat": aa["lat"], "a_lon": aa["lon"],
                  "km": round(km(da["lat"], da["lon"], aa["lat"], aa["lon"]))})
        punti = [(da["lat"], da["lon"])] + [(pos[v]["lat"], pos[v]["lon"]) for v in a.get("via", []) if v in pos] + [(aa["lat"], aa["lon"])]
        r["g"] = [[[round(lo, 4), round(la, 4)] for la, lo in punti]]
        out.append(r)
    return out


def legami(nodi, oss):
    """Legami con altri livelli: distanza dalla linea >= 380 kV più vicina (solo nel riquadro di
    rete-elettrica.json) e numero di cavi sottomarini attivi che approdano nel paese del nodo."""
    linee = (oss.get("rete-elettrica") or {}).get("elementi", [])
    cavi = (oss.get("cavi") or {}).get("elementi", [])
    cavi_paese = {}
    for c in cavi:
        if c.get("stato") == "attivo":
            for p in c.get("paesi", []):
                cavi_paese[p] = cavi_paese.get(p, 0) + 1
    out = {"rete_380kv": [], "cavi_attivi_per_paese": {}}
    for n in nodi:
        lat, lon = n.get("lat"), n.get("lon")
        if lat is None or not (-25 <= lon <= 65 and 12 <= lat <= 72) or not linee:
            continue
        if (n.get("rif") or {}).get("file") == "stretti-dettaglio.json":
            continue  # uno stretto non ha bisogno di un allaccio
        best, nome_best = None, None
        for l in linee:
            if (l.get("tensione_kv") or 0) < 380:
                continue
            for parte in l.get("g", []):
                for a, b in zip(parte, parte[1:]):
                    if abs(a[1] - lat) > 3 or abs(a[0] - lon) > 4:
                        continue
                    d = dist_segmento_km(lat, lon, a, b)
                    if best is None or d < best:
                        best, nome_best = d, "%s kV%s" % (l.get("tensione_kv"), (" " + l["nome"]) if l.get("nome") else "")
        if best is not None:
            out["rete_380kv"].append({"nodo": n["id"], "nome": n["nome"], "km": round(best, 1), "linea": nome_best})
    for p in sorted({n["paese"] for n in nodi}):
        if p in cavi_paese:
            out["cavi_attivi_per_paese"][p] = cavi_paese[p]
    out["nota"] = ("Distanza in linea d'aria dalla linea >= 380 kV più vicina in rete-elettrica.json (OpenStreetMap via "
                   "openinframap, riquadro Europa-Medio Oriente); conteggio dei cavi sottomarini attivi con almeno un "
                   "approdo nel paese (cavi.json, TeleGeography CC BY-NC-SA).")
    return out


def riepilogo(anelli, nodi, archi, colli, controlli):
    r = {"nodi_per_anello": {}, "archi_per_modo": {}, "colli_per_stato": {}, "controlli_per_stato": {},
         "archi_tra_anelli": {}}
    for a in anelli:
        r["nodi_per_anello"][a["id"]] = sum(1 for n in nodi if n["anello"] == a["id"])
    for x in archi:
        r["archi_per_modo"][x["modo"]] = r["archi_per_modo"].get(x["modo"], 0) + 1
        if x["anello_da"] != x["anello_a"]:
            k = "%s → %s" % (x["anello_da"], x["anello_a"])
            r["archi_tra_anelli"][k] = r["archi_tra_anelli"].get(k, 0) + 1
    for c in colli:
        r["colli_per_stato"][c["stato"]] = r["colli_per_stato"].get(c["stato"], 0) + 1
    for c in controlli:
        r["controlli_per_stato"][c["stato"]] = r["controlli_per_stato"].get(c["stato"], 0) + 1
    r["nodi_per_paese"] = {}
    for n in nodi:
        r["nodi_per_paese"][n["paese"]] = r["nodi_per_paese"].get(n["paese"], 0) + 1
    return r


# Voci di commercio.json (dipendenze di Italia e UE) che toccano la catena dell'AI, con l'anello
HS_CATENA = {"850511": "magneti NdFeB per motori, ventole, pompe e dischi rigidi",
             "280530": "metalli delle terre rare (leghe per magneti)",
             "284690": "composti delle terre rare (ossidi separati)",
             "811292": "gallio e germanio (voce doganale mista con indio, niobio, vanadio)",
             "280461": "silicio ad altissima purezza per polisilicio e wafer",
             "740311": "rame raffinato per cavi, sbarre e trasformatori",
             "380110": "grafite artificiale (elettrodi, anodi)"}
# materie sotto licenza cinese censite in minerali.json ma non nella tabella USGS di questo livello
ALTRE_CONTROLLATE = {"antimonio": "semiconduttori e ritardanti di fiamma; nel divieto verso gli USA di dicembre 2024",
                     "tungsteno": "bersagli di deposizione e contatti nei chip",
                     "grafite": "anodi delle batterie dei sistemi di continuità dei data center",
                     "magnesio": "leghe leggere per chassis e componenti"}


def confronti(materie, oss):
    """Coerenza con minerali.json (stesse quote USGS) e legami con commercio.json e investimenti.json."""
    out = {"minerali_confronto": [], "dipendenze_ue_italia": [], "altre_materie_controllate": [], "capex_2026": None}
    mi = {m.get("id"): m for m in (oss.get("minerali") or {}).get("elementi", [])}
    for m in materie:
        pp = m.get("primo_produttore")
        x = mi.get(m["id"])
        if not pp or not x or not x.get("produttori"):
            continue
        q = next((p for p in x["produttori"] if p.get("iso2") == pp["paese"]), None)
        qv = q.get("quota") if q else None
        ok = qv is not None and abs(qv - pp["quota_pct"]) <= 0.15
        out["minerali_confronto"].append({"materia": m["id"], "paese": pp["paese"], "quota_qui": pp["quota_pct"],
                                          "quota_minerali_json": qv, "coerente": ok})
        if not ok:
            avviso("materia %s: quota %s diversa da minerali.json (%s contro %s)" % (m["id"], pp["paese"], pp["quota_pct"], qv))
    for dp in (oss.get("commercio") or {}).get("dipendenze", []):
        if dp.get("hs") in HS_CATENA:
            out["dipendenze_ue_italia"].append({
                "importatore": dp.get("importatore"), "iso2": dp.get("iso2"), "hs": dp["hs"], "prodotto": dp.get("prodotto"),
                "uso_ai": HS_CATENA[dp["hs"]], "anno": dp.get("anno"), "import_totale_usd": dp.get("import_totale_usd"),
                "fornitori": (dp.get("fornitori") or [])[:3], "quota_cina": next((f.get("quota") for f in dp.get("fornitori", []) if f.get("iso2") == "CN"), None),
                "valore_trascurabile": bool(dp.get("valore_trascurabile")), "dipendenza_oltre_50": bool(dp.get("dipendenza_oltre_50"))})
    for mid, uso in ALTRE_CONTROLLATE.items():
        x = mi.get(mid)
        if x and x.get("produttori"):
            p0 = x["produttori"][0]
            cn = next((p for p in x["produttori"] if p.get("iso2") == "CN"), {})
            out["altre_materie_controllate"].append({"materia": mid, "nome": x.get("minerale"), "uso_ai": uso, "anno": x.get("anno"),
                                                     "primo": p0.get("iso2"), "quota_primo": p0.get("quota"), "quota_cina": cn.get("quota"),
                                                     "fonte": x.get("fonte"), "link": x.get("link")})
    inv = oss.get("investimenti") or {}
    if inv.get("capex_2026"):
        out["capex_2026"] = inv["capex_2026"]
    out["nota"] = ("minerali_confronto: quota del primo produttore qui e in minerali.json (stessa fonte USGS 2026); "
                   "dipendenze_ue_italia: import 2025 di Italia e UE-27 (extra-UE) per voce doganale da commercio.json (UN Comtrade), "
                   "con i primi tre fornitori; per l'Italia gli acquisti intra-UE sono attribuiti al paese di spedizione, non di origine.")
    return out


def costruisci(oggi):
    cur = carica_curati()
    oss = carica_osservatorio()
    anelli = valida_anelli(cur["anelli"])
    materie = calcola_materie(cur["materie"])
    nodi = risolvi_nodi(cur["nodi"], indice_rif(oss), materie)
    controlli = calcola_controlli(cur["controlli"], {m["id"] for m in materie}, oggi)
    colli = calcola_colli(cur["colli"], oss, materie, controlli, {n["id"] for n in nodi}, oggi)
    titoli = calcola_titoli(cur["titoli"], oss)
    archi = calcola_archi(cur["archi"], nodi)
    simboli = {t["simbolo"] for t in titoli}
    for n in nodi:
        for s in n.get("titoli", []):
            if s not in simboli:
                errore("nodo %s: titolo %r non in titoli.json" % (n["id"], s))
    for c in colli:
        for s in c.get("titoli", []):
            if s not in simboli:
                errore("collo %s: titolo %r non in titoli.json" % (c["id"], s))
    for a in anelli:
        a["titoli"] = [t["simbolo"] for t in titoli if a["id"] in t["anelli"]]
        a["colli"] = [c["id"] for c in colli if c["anello"] == a["id"]]
    fonti_osservatorio = []
    for nome, f in (("prezzi.json", "prezzi"), ("portwatch.json", "portwatch"), ("ai.json", "ai"), ("ai-mondo.json", "ai-mondo"),
                    ("stretti-dettaglio.json", "stretti-dettaglio"), ("cavi-incidenti.json", "cavi-incidenti"),
                    ("rete-elettrica.json", "rete-elettrica"), ("cavi.json", "cavi"), ("minerali.json", "minerali"),
                    ("commercio.json", "commercio"), ("investimenti.json", "investimenti")):
        if oss.get(f):
            fonti_osservatorio.append({"nome": nome, "aggiornato": oss[f].get("aggiornato")})
    return {
        "aggiornato": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "data_riferimento": oggi.isoformat(),
        "fonti": [
            {"nome": "USGS, Mineral Commodity Summaries 2026", "link": "https://pubs.usgs.gov/periodicals/mcs2026/mcs2026.pdf", "licenza": "pubblico dominio (governo USA)", "data_dato": "2026-02-05"},
            {"nome": "Voci curate a mano (stampa, società, governi, analisti)", "link": None, "file": "raccolta/supply-chain-ai/*.json", "licenza": "fatti citati con fonte e link per ogni voce", "data_dato": oggi.isoformat()},
            {"nome": "OpenStreetMap Nominatim (geocodifica una tantum)", "link": "https://nominatim.openstreetmap.org/", "licenza": "ODbL 1.0", "data_dato": "2026-11-09"},
        ],
        "fonti_osservatorio": fonti_osservatorio,
        "nota": ("Catena del valore dell'AI dalla miniera al data center, in 8 anelli. elementi = nodi (punti con lat/lon); "
                 "archi = collegamenti da → a (g = [[lon, lat], ...]); colli = colli di bottiglia con indicatori, valori e "
                 "stato rispetto a soglie che sono una VALUTAZIONE dell'osservatorio; controlli = controlli all'export 2022-2026; "
                 "materie = produzione per paese (USGS) con quote calcolate; titoli = titoli quotati collegati, con prezzo da "
                 "prezzi.json quando seguito. Gli archi di tipo 'valutazione' sono percorsi tipici, non tracciati reali. "
                 "Non è una raccomandazione di investimento."),
        "anelli": anelli,
        "elementi": nodi,
        "archi": archi,
        "colli": colli,
        "controlli": controlli,
        "materie": materie,
        "titoli": titoli,
        "legami": legami(nodi, oss),
        "confronti": confronti(materie, oss),
        "riepilogo": riepilogo(anelli, nodi, archi, colli, controlli),
        "avvisi": AVVISI,
        "errori": ERRORI,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--valida", action="store_true", help="valida soltanto, non scrive il file")
    ap.add_argument("--oggi", help="data di riferimento AAAA-MM-GG (predefinita: oggi UTC)")
    ap.add_argument("--uscita", default=USCITA)
    a = ap.parse_args()
    oggi = data_valida(a.oggi) if a.oggi else dt.datetime.now(dt.timezone.utc).date()
    if oggi is None:
        sys.exit("data --oggi non valida")
    out = costruisci(oggi)
    for m in AVVISI:
        print("AVVISO:", m, file=sys.stderr)
    for m in ERRORI:
        print("ERRORE:", m, file=sys.stderr)
    if a.valida:
        print("validazione: %d errori, %d avvisi" % (len(ERRORI), len(AVVISI)))
        sys.exit(1 if ERRORI else 0)
    with open(a.uscita, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    r = out["riepilogo"]
    print("scritto %s: %d nodi, %d archi, %d colli, %d controlli, %d materie, %d titoli; %d errori, %d avvisi" % (
        os.path.relpath(a.uscita, RADICE), len(out["elementi"]), len(out["archi"]), len(out["colli"]),
        len(out["controlli"]), len(out["materie"]), len(out["titoli"]), len(ERRORI), len(AVVISI)))
    print("colli per stato:", r["colli_per_stato"])


if __name__ == "__main__":
    main()
