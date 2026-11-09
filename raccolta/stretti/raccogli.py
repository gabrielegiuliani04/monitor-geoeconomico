#!/usr/bin/env python3
"""Stretti e passaggi strategici -> docs/data/stretti-dettaglio.json

Dominio CURATO: le schede (flussi, origini, destinazioni, alternative, impatti di mercato,
episodi, stato attuale) si scrivono a mano nel file JSON. Questo script, solo libreria
standard, ogni giorno:

  1. VALIDA il file: campi obbligatori, ogni voce con valore, anno, fonte, link e data_fonte,
     date nel formato giusto, link http(s) o percorso locale esistente, chiavi coerenti con
     docs/data/stretti.json e labels.json, stato attuale non troppo vecchio.
  2. AGGIORNA solo le parti automatizzabili, leggendo i file degli altri agenti (non li rifà):
       - prezzi.json        -> 'prezzi_collegati_valori' (Brent, WTI, TTF, Henry Hub: ultimo e variazioni)
       - mercati.json       -> 'mercati_collegati_valori' (Baltic Dry, TTF, Brent della raccolta del giorno)
       - gas-italia.json    -> flussi del TransMed e del Greenstream per il Canale di Sicilia
       - eventi.json        -> eventi degli ultimi 30 giorni entro un raggio dal passaggio
       - portwatch.json, noli.json, gpr.json, sanzioni-navi.json -> se esistono, ultimo dato
         che nomina il passaggio (collegamento, non copia)
  3. Riscrive il file con 'aggiornato', 'errori' (problemi di validazione e fonti mancanti)
     e 'avvisi' (dati vecchi da ricontrollare a mano).

Uso:
  python3 raccolta/stretti/raccogli.py                # valida e aggiorna
  python3 raccolta/stretti/raccogli.py --controlla    # valida soltanto, non scrive
  python3 raccolta/stretti/raccogli.py --verifica-link  # come sopra + prova i link http (lento)
Esce con codice 0 anche se ci sono errori di validazione (finiscono nel file);
codice 1 solo se il file curato manca o non è JSON valido.
"""
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.request

RADICE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATI = os.path.join(RADICE, "docs", "data")
FILE = os.path.join(DATI, "stretti-dettaglio.json")
OGGI = dt.datetime.now(dt.timezone.utc).date()

SEZIONI = ["flussi", "origini", "destinazioni", "esposizione_italia_ue", "alternative", "impatti_mercato", "episodi"]
OBBLIGATORI_ELEMENTO = ["id", "nome", "chiavi_stretti", "lat", "lon", "paese", "categoria", "stato", "affidabilita", "sintesi", "stato_attuale"]
OBBLIGATORI_VOCE = ["voce", "valore", "anno", "fonte", "link", "data_fonte", "tipo", "affidabilita"]
TIPI = {"fatto", "stima", "valutazione", "automatico"}
AFFIDABILITA = {"alta", "media", "bassa"}
RE_DATA = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
# raggio (km) entro cui un evento di eventi.json si collega al passaggio
RAGGI_KM = {"hormuz": 250, "bab-el-mandeb": 350, "suez": 200, "stretti-turchi": 250, "kerch": 200,
            "malacca": 400, "taiwan": 250, "stretti-danesi": 200, "canale-di-sicilia": 200}
GIORNI_EVENTI = 30
GIORNI_STATO_VECCHIO = 14
GIORNI_FATTO_VECCHIO = 90
ALTRI_AGENTI = ["portwatch.json", "noli.json", "gpr.json", "sanzioni-navi.json"]

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
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        errore(f"{nome}: non leggibile ({e})")
        return None


def data_da_testo(s):
    """Prima data AAAA-MM-GG (o AAAA-MM) trovata nel testo, come date (giorno 1 se manca)."""
    if not isinstance(s, str):
        return None
    m = re.search(r"(\d{4})-(\d{2})(?:-(\d{2}))?", s)
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3) or 1))
    except ValueError:
        return None


def km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ------------------------------------------------------------------ validazione
def link_ok(link):
    if not isinstance(link, str) or not link.strip():
        return False
    if link.startswith("http://") or link.startswith("https://"):
        return True
    return os.path.exists(os.path.join(RADICE, link))


def valida_voce(v, dove):
    for c in OBBLIGATORI_VOCE:
        if c not in v or v[c] in (None, ""):
            errore(f"{dove}: manca '{c}'")
    if v.get("tipo") and v["tipo"] not in TIPI:
        errore(f"{dove}: tipo '{v['tipo']}' non ammesso")
    if v.get("affidabilita") and v["affidabilita"] not in AFFIDABILITA:
        errore(f"{dove}: affidabilita '{v['affidabilita']}' non ammessa")
    df = v.get("data_fonte", "")
    if df and not (RE_DATA.match(str(df)) or str(df).startswith(("anno non indicato", "consultata"))):
        errore(f"{dove}: data_fonte '{df}' non nel formato AAAA, AAAA-MM o AAAA-MM-GG")
    if "link" in v and not link_ok(v["link"]):
        errore(f"{dove}: link non valido o file locale inesistente ({v.get('link')})")
    if v.get("tipo") == "valutazione" and "base" not in v:
        errore(f"{dove}: una valutazione deve dire su quali fonti poggia ('base')")


def valida(doc, chiavi_note):
    for c in ["aggiornato", "fonti", "nota", "elementi", "errori"]:
        if c not in doc:
            errore(f"radice: manca '{c}'")
    ids = set()
    for i, e in enumerate(doc.get("elementi", [])):
        nome = e.get("id", f"elemento {i}")
        for c in OBBLIGATORI_ELEMENTO:
            if c not in e:
                errore(f"{nome}: manca '{c}'")
        if nome in ids:
            errore(f"{nome}: id duplicato")
        ids.add(nome)
        if not isinstance(e.get("lat"), (int, float)) or not isinstance(e.get("lon"), (int, float)):
            errore(f"{nome}: lat/lon devono essere numeri")
        for k in e.get("chiavi_stretti", []):
            if k not in chiavi_note and not e.get("chiavi_nuove"):
                errore(f"{nome}: la chiave '{k}' non è in stretti.json né in labels.json")
        for s in SEZIONI:
            voci = e.get(s)
            if not isinstance(voci, list) or not voci:
                errore(f"{nome}: sezione '{s}' vuota o mancante")
                continue
            for j, v in enumerate(voci):
                valida_voce(v, f"{nome}.{s}[{j}]")
        sa = e.get("stato_attuale", {})
        d = data_da_testo(sa.get("data", ""))
        if not d:
            errore(f"{nome}: stato_attuale senza data")
        elif (OGGI - d).days > GIORNI_STATO_VECCHIO:
            avviso(f"{nome}: stato attuale fermo al {d} ({(OGGI - d).days} giorni): da ricontrollare a mano")
        fatti = sa.get("fatti", [])
        if not fatti:
            errore(f"{nome}: stato_attuale senza fatti")
        for j, f in enumerate(fatti):
            for c in ["testo", "data", "fonte", "link", "data_fonte"]:
                if not f.get(c):
                    errore(f"{nome}.stato_attuale.fatti[{j}]: manca '{c}'")
            if f.get("link") and not link_ok(f["link"]):
                errore(f"{nome}.stato_attuale.fatti[{j}]: link non valido ({f['link']})")
            df = data_da_testo(f.get("data", ""))
            if df and (OGGI - df).days > GIORNI_FATTO_VECCHIO:
                avviso(f"{nome}: fatto del {df} nello stato attuale ha più di {GIORNI_FATTO_VECCHIO} giorni")


def verifica_link(doc):
    visti = {}
    for e in doc.get("elementi", []):
        for s in SEZIONI:
            for v in e.get(s, []):
                l = v.get("link", "")
                if l.startswith("http") and l not in visti:
                    try:
                        req = urllib.request.Request(l, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (monitor-osint stretti)"})
                        with urllib.request.urlopen(req, timeout=20) as r:
                            visti[l] = r.status
                    except Exception as ex:  # noqa: BLE001
                        visti[l] = str(ex)[:80]
    for l, st in visti.items():
        if st != 200:
            avviso(f"link da ricontrollare ({st}): {l}")


# ------------------------------------------------------------------ aggiornamenti automatici
def aggiorna_prezzi(e, prezzi):
    if not prezzi:
        return None
    per_id = {s["id"]: s for s in prezzi.get("serie", [])}
    out = []
    for pid in e.get("prezzi_collegati", []):
        s = per_id.get(pid)
        if not s:
            errore(f"{e['id']}: serie '{pid}' assente in prezzi.json")
            continue
        out.append({"id": pid, "nome": s.get("nome"), "ultimo": s.get("ultimo"), "unita": s.get("unita") or s.get("valuta"),
                    "data": s.get("data"), "var_pct": s.get("var"), "fonte": "docs/data/prezzi.json", "link": "docs/data/prezzi.json"})
    return out


def aggiorna_mercati(e, mercati):
    if not mercati or not e.get("mercati_collegati"):
        return None
    giorni = mercati.get("giorni", [])
    if not giorni:
        return None
    g = giorni[0]
    out = []
    for ind in e["mercati_collegati"]:
        for r in g.get("righe", []):
            if r.get("indicatore", "").lower() == ind.lower():
                out.append({"indicatore": r["indicatore"], "valore": r.get("valore"), "unita": r.get("unita"),
                            "var_giorno_pct": r.get("var_giorno"), "data": r.get("data"), "ora_utc": r.get("ora_utc"),
                            "fonte": r.get("fonte"), "link": r.get("link")})
    return out


def aggiorna_gas(e, gas):
    if not gas or not e.get("gas_italia_ids"):
        return None
    quote = {q["id"]: q for q in gas.get("quote_12_mesi", [])}
    el = {x["id"]: x for x in gas.get("elementi", [])}
    out = []
    for gid in e["gas_italia_ids"]:
        q, x = quote.get(gid, {}), el.get(gid, {})
        note = x.get("note", "")
        m_last = re.search(r"Ingresso ultimo giorno gas \((\d{4}-\d{2}-\d{2})\): ([\d.]+) GWh", note)
        m_30 = re.search(r"media 30 giorni ([\d.]+) GWh", note)
        out.append({"id": gid, "nome": q.get("nome") or x.get("nome"), "twh_12m": q.get("twh_12m"),
                    "quota_ingressi_pct": q.get("quota_ingressi_pct"),
                    "ultimo_giorno": m_last.group(1) if m_last else None,
                    "ultimo_gwh": float(m_last.group(2)) if m_last else None,
                    "media_30g_gwh": float(m_30.group(1)) if m_30 else None,
                    "stato": x.get("stato"), "fonte": "docs/data/gas-italia.json (ENTSOG)", "link": "docs/data/gas-italia.json",
                    "data_fonte": gas.get("aggiornato")})
    return out


def aggiorna_eventi(e, eventi):
    if not eventi:
        return None
    raggio = RAGGI_KM.get(e["id"], 200)
    punti = list(eventi.get("punti", []))
    centri = [(e["lat"], e["lon"])] + [(c["lat"], c["lon"]) for c in e.get("coordinate_extra", [])]
    trovati = []
    for p in punti:
        if not isinstance(p.get("lat"), (int, float)) or not isinstance(p.get("lon"), (int, float)):
            continue
        d = data_da_testo(p.get("data_evento", ""))
        if not d or (OGGI - d).days > GIORNI_EVENTI or d > OGGI + dt.timedelta(days=1):
            continue
        dist = min(km(p["lat"], p["lon"], la, lo) for la, lo in centri)
        if dist <= raggio:
            trovati.append((d, p, dist))
    trovati.sort(key=lambda t: t[0], reverse=True)
    per_cat = {}
    for _, p, _ in trovati:
        per_cat[p.get("categoria", "?")] = per_cat.get(p.get("categoria", "?"), 0) + 1
    return {"raggio_km": raggio, "giorni": GIORNI_EVENTI, "totale": len(trovati), "per_categoria": per_cat,
            "ultimi": [{"id": p.get("id"), "data": str(d), "categoria": p.get("categoria"), "nome": p.get("nome"),
                        "affidabilita": p.get("affidabilita"), "distanza_km": round(dist)} for d, p, dist in trovati[:8]],
            "fonte": "docs/data/eventi.json", "link": "docs/data/eventi.json"}


def _cerca(obj, nomi, profondita=0):
    """Cerca ricorsivamente il primo dizionario che nomina il passaggio in un campo testuale breve."""
    if profondita > 6:
        return None
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and len(v) < 120 and k.lower() in {"nome", "name", "portname", "stretto", "chokepoint", "passaggio", "id", "breve"}:
                vl = v.lower()
                if any(n.lower() == vl or (len(n) > 5 and n.lower() in vl) for n in nomi):
                    return obj
        for v in obj.values():
            r = _cerca(v, nomi, profondita + 1)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _cerca(v, nomi, profondita + 1)
            if r is not None:
                return r
    return None


def _riassumi(o):
    out = {}
    for k, v in o.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            if not (isinstance(v, str) and len(v) > 300):
                out[k] = v
        elif isinstance(v, list) and v and isinstance(v[-1], list) and len(v[-1]) == 2 and isinstance(v[-1][0], str):
            out[k + "_ultimo"] = v[-1]          # serie storica [["AAAA-MM-GG", valore], ...]
            out[k + "_punti"] = len(v)
    return out


def collega_altri_agenti(e, altri):
    nomi = list(e.get("portwatch_nomi", [])) + [e["nome"]] + list(e.get("chiavi_stretti", []))
    out = {}
    for nome_file, doc in altri.items():
        if doc is None:
            out[nome_file] = {"presente": False, "nota": "file non ancora prodotto dall'altro agente"}
            continue
        trovato = _cerca(doc.get("elementi", doc), nomi)
        out[nome_file] = {"presente": True, "link": f"docs/data/{nome_file}", "aggiornato": doc.get("aggiornato")}
        if trovato:
            out[nome_file]["dato"] = _riassumi(trovato)
        else:
            out[nome_file]["nota"] = "nessuna voce che nomini questo passaggio"
    return out


# ------------------------------------------------------------------ main
def main():
    solo_controllo = "--controlla" in sys.argv or "--verifica-link" in sys.argv
    try:
        with open(FILE, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as ex:  # noqa: BLE001
        print(f"ERRORE: {FILE} mancante o non valido: {ex}", file=sys.stderr)
        return 1

    stretti = carica("stretti.json") or {}
    labels = carica("labels.json") or {}
    chiavi_note = set(stretti.get("stretti", {}).keys()) | {x.get("n") for x in labels.get("straits", [])}
    if not stretti:
        errore("stretti.json non trovato: non posso controllare le chiavi")

    valida(doc, chiavi_note)
    if "--verifica-link" in sys.argv:
        verifica_link(doc)

    if solo_controllo:
        print(f"Controllo: {len(errori)} errori, {len(avvisi)} avvisi")
        return 0

    prezzi, mercati, gas, eventi = carica("prezzi.json"), carica("mercati.json"), carica("gas-italia.json"), carica("eventi.json")
    for nome, d in [("prezzi.json", prezzi), ("mercati.json", mercati), ("gas-italia.json", gas), ("eventi.json", eventi)]:
        if d is None:
            errore(f"{nome} assente: parte automatica saltata")
    altri = {n: carica(n) for n in ALTRI_AGENTI}

    for e in doc.get("elementi", []):
        auto = {"aggiornato": OGGI.isoformat()}
        v = aggiorna_prezzi(e, prezzi)
        if v is not None:
            e["prezzi_collegati_valori"] = v
        v = aggiorna_mercati(e, mercati)
        if v is not None:
            e["mercati_collegati_valori"] = v
        v = aggiorna_gas(e, gas)
        if v is not None:
            auto["gas_italia"] = v
        v = aggiorna_eventi(e, eventi)
        if v is not None:
            auto["eventi_vicini"] = v
        auto["altri_agenti"] = collega_altri_agenti(e, altri)
        e.setdefault("stato_attuale", {})["automatico"] = auto

    doc["aggiornato"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    doc["errori"] = errori
    doc["avvisi"] = avvisi
    tmp = FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(tmp, FILE)
    print(f"Scritto {FILE}: {len(doc.get('elementi', []))} passaggi, {len(errori)} errori, {len(avvisi)} avvisi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
