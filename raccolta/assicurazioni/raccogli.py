#!/usr/bin/env python3
"""Assicurazioni marittime e rischio guerra -> docs/data/assicurazioni.json

Dominio CURATO: i dati si scrivono a mano in raccolta/assicurazioni/*.json
  aree.json       aree elencate dal Joint War Committee (circolare in vigore), con poligono o punto
  circolari.json  storia delle circolari JWLA e ultimo controllo manuale delle pagine pubbliche
  premi.json      punti di premio war risk (data, forchetta %, fonte, affidabilità)
  costi.json      esempi di costo per viaggio: ingressi con fonte + formule (i risultati li calcola lo script)
  eventi.json     eventi assicurativi chiave
  concetti.json   schede «come funziona»

Ogni giorno lo script, solo libreria standard:
  1. VALIDA i file curati (campi obbligatori, date, affidabilità, link, forchette coerenti, geometrie).
  2. CALCOLA gli esempi di costo dalle formule (valore nave × premio, per barile, per TEU, soglia del Capo),
     leggendo gli ingressi automatici da prezzi.json (Brent) e noli.json (WCI).
  3. COSTRUISCE le serie storiche dei premi per area ([data, valore centrale]).
  4. COLLEGA ogni area elencata ai transiti di portwatch.json e agli attacchi a navi di eventi.json
     (ultimi 30 giorni), per confrontare rischio percepito (premi) e misurato (transiti, attacchi).
  5. CONTROLLA (se c'è rete) la pagina pubblica delle Listed Areas dell'LMA e l'elenco IUA delle
     circolari: segnala circolari nuove, una circolare in vigore diversa da quella curata, una frase
     di revisione cambiata o un PDF modificato. NON cambia i file curati: li aggiorna una persona.
  6. Scrive docs/data/assicurazioni.json con 'errori' e 'avvisi'.

Uso:
  python3 raccolta/assicurazioni/raccogli.py              # valida, calcola, controlla il JWC, scrive
  python3 raccolta/assicurazioni/raccogli.py --controlla  # valida e calcola soltanto, non scrive
  python3 raccolta/assicurazioni/raccogli.py --offline    # non va in rete (niente controllo JWC)
Esce con 0 anche con errori di validazione (finiscono nel file); 1 solo se un file curato manca o non è JSON.
"""
import ast
import datetime as dt
import html
import json
import math
import operator
import os
import re
import sys
import urllib.error
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
DATI = os.path.join(RADICE, "docs", "data")
USCITA = os.path.join(DATI, "assicurazioni.json")
ADESSO = dt.datetime.now(dt.timezone.utc)
OGGI = ADESSO.date()
UA = "Mozilla/5.0 (compatible; monitor-geoeconomico/1.0; osservatorio OSINT personale)"
GIORNI_EVENTI = 30
GIORNI_PREMIO_VECCHIO = 45
AFFIDABILITA = {"alta", "media", "bassa"}
RE_DATA = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
MESI_EN = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july",
                                         "august", "september", "october", "november", "december"], 1)}

errori, avvisi = [], []


def errore(msg):
    errori.append(msg)
    print("ERRORE:", msg, file=sys.stderr)


def avviso(msg):
    avvisi.append(msg)
    print("AVVISO:", msg, file=sys.stderr)


def carica(nome, obbligatorio=True, cartella=QUI):
    p = os.path.join(cartella, nome)
    if not os.path.exists(p):
        if obbligatorio:
            print(f"File mancante: {p}", file=sys.stderr)
            sys.exit(1)
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        if obbligatorio:
            print(f"JSON non valido in {p}: {e}", file=sys.stderr)
            sys.exit(1)
        avviso(f"{nome}: JSON non valido ({e}), ignorato")
        return None


def data_ok(s):
    if not isinstance(s, str) or not RE_DATA.match(s):
        return False
    try:
        parti = [int(x) for x in s.split("-")]
        dt.date(parti[0], parti[1] if len(parti) > 1 else 1, parti[2] if len(parti) > 2 else 1)
        return True
    except ValueError:
        return False


def a_data(s):
    parti = [int(x) for x in s.split("-")]
    return dt.date(parti[0], parti[1] if len(parti) > 1 else 1, parti[2] if len(parti) > 2 else 1)


def link_ok(l):
    return isinstance(l, str) and (l.startswith("https://") or l.startswith("http://")
                                   or os.path.exists(os.path.join(RADICE, l)))


def controlla_fonte(dove, v, campo_data="data_fonte"):
    for k in ("fonte", "link", campo_data, "affidabilita"):
        if not v.get(k) and v.get(k) != 0:
            errore(f"{dove}: manca '{k}'")
    if v.get(campo_data) and not data_ok(v[campo_data]) and v[campo_data] != "2024":
        errore(f"{dove}: data '{v.get(campo_data)}' non nel formato AAAA[-MM[-GG]]")
    if v.get("link") and not link_ok(v["link"]):
        errore(f"{dove}: link non valido '{v['link']}'")
    if v.get("affidabilita") and v["affidabilita"] not in AFFIDABILITA:
        errore(f"{dove}: affidabilità '{v['affidabilita']}' non ammessa")


# ---------------------------------------------------------------- validazione

def valida_aree(aree):
    ids = set()
    if not data_ok(aree.get("data_circolare", "")):
        errore("aree.json: data_circolare mancante o non valida")
    for a in aree.get("aree", []):
        dove = f"aree/{a.get('id')}"
        for k in ("id", "nome", "gruppo", "tipo", "lat", "lon", "data_inserimento"):
            if k not in a:
                errore(f"{dove}: manca '{k}'")
        if a.get("id") in ids:
            errore(f"{dove}: id duplicato")
        ids.add(a.get("id"))
        lat, lon = a.get("lat"), a.get("lon")
        if not (isinstance(lat, (int, float)) and -90 <= lat <= 90 and isinstance(lon, (int, float)) and -180 <= lon <= 180):
            errore(f"{dove}: coordinate non valide")
        if a.get("tipo") == "paese" and not re.match(r"^[A-Z]{2}$", a.get("paese", "")):
            errore(f"{dove}: codice paese ISO a 2 lettere mancante")
        if a.get("tipo") == "acque":
            g = a.get("g")
            if not g:
                errore(f"{dove}: area di acque senza poligono 'g'")
                continue
            for parte in g:
                if len(parte) < 4 or parte[0] != parte[-1]:
                    errore(f"{dove}: anello del poligono non chiuso o troppo corto")
                for p in parte:
                    if not (len(p) == 2 and -180 <= p[0] <= 180 and -90 <= p[1] <= 90):
                        errore(f"{dove}: vertice non valido {p}")
                    elif any(len(str(x).split(".")[-1]) > 4 for x in p if isinstance(x, float)):
                        avviso(f"{dove}: vertice con più di 4 decimali {p}")
    return ids


def valida_circolari(circ):
    ids = []
    for c in circ.get("circolari", []):
        dove = f"circolari/{c.get('id')}"
        for k in ("id", "data", "titolo", "link"):
            if not c.get(k):
                errore(f"{dove}: manca '{k}'")
        if c.get("data") and not data_ok(c["data"]):
            errore(f"{dove}: data non valida")
        ids.append(c.get("id"))
    if len(ids) != len(set(ids)):
        errore("circolari.json: id duplicati")
    return ids


def valida_premi(premi):
    aree = premi.get("aree", {})
    for i, p in enumerate(premi.get("punti", [])):
        dove = f"premi[{i}] {p.get('area')} {p.get('data')}"
        if p.get("area") not in aree:
            errore(f"{dove}: area non dichiarata in 'aree'")
        if not data_ok(p.get("data", "")):
            errore(f"{dove}: data non valida")
        controlla_fonte(dove, p)
        if p.get("non_pubblico"):
            if not p.get("note"):
                errore(f"{dove}: voce 'non_pubblico' senza nota che spieghi")
            continue
        mn, mx = p.get("min"), p.get("max")
        if not isinstance(mn, (int, float)) or not isinstance(mx, (int, float)):
            errore(f"{dove}: 'min' e 'max' devono essere numeri")
            continue
        if mn > mx:
            errore(f"{dove}: min > max")
        if not (0 <= mn <= 100 and 0 <= mx <= 100):
            errore(f"{dove}: percentuale fuori scala")
        if p.get("base") not in ("scafo", "carico"):
            errore(f"{dove}: 'base' deve essere 'scafo' o 'carico'")
        if p.get("in_serie") and p.get("base") != "scafo":
            errore(f"{dove}: in serie solo punti sul valore dello scafo")
        if data_ok(p.get("data", "")) and data_ok(p.get("data_fonte", "")) and a_data(p["data"]) > a_data(p["data_fonte"]):
            errore(f"{dove}: il punto è successivo alla data della fonte")


def valida_eventi(ev):
    for i, e in enumerate(ev.get("eventi", [])):
        dove = f"eventi[{i}] {e.get('data')} {e.get('titolo', '')[:40]}"
        for k in ("data", "tipo", "titolo", "dettaglio"):
            if not e.get(k):
                errore(f"{dove}: manca '{k}'")
        if e.get("data") and not data_ok(e["data"]):
            errore(f"{dove}: data non valida")
        controlla_fonte(dove, e)


def valida_concetti(co):
    for c in co.get("concetti", []):
        dove = f"concetti/{c.get('id')}"
        for k in ("id", "nome", "testo", "tipo"):
            if not c.get(k):
                errore(f"{dove}: manca '{k}'")
        if c.get("tipo") == "fatto":
            for k in ("fonte", "link", "data_fonte"):
                if not c.get(k):
                    errore(f"{dove}: manca '{k}'")
            if c.get("link") and not link_ok(c["link"]):
                errore(f"{dove}: link non valido")


# ---------------------------------------------------------------- calcoli

OPERATORI = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def valuta(espr, nomi):
    """Valuta un'espressione aritmetica semplice (+ - * / e parentesi) sui nomi dati. Niente eval."""
    def _v(n):
        if isinstance(n, ast.Expression):
            return _v(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Name):
            if n.id not in nomi or nomi[n.id] is None:
                raise KeyError(n.id)
            return nomi[n.id]
        if isinstance(n, ast.BinOp) and type(n.op) in OPERATORI:
            return OPERATORI[type(n.op)](_v(n.left), _v(n.right))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -_v(n.operand)
        raise ValueError(f"elemento non ammesso: {ast.dump(n)[:40]}")
    return _v(ast.parse(espr, mode="eval"))


def ingresso_auto(spec, prezzi, noli):
    """'prezzi.json:brent' oppure 'noli.json:wci:Shanghai-Genoa'. Restituisce (valore, data, fonte)."""
    parti = spec.split(":")
    if parti[0] == "prezzi.json" and prezzi:
        for s in prezzi.get("serie", []):
            if s.get("id") == parti[1]:
                return s.get("ultimo"), s.get("data"), f"docs/data/prezzi.json ({s.get('nome')}, {s.get('fonte')})"
    if parti[0] == "noli.json" and noli:
        for e in noli.get("elementi", []):
            if e.get("id") == parti[1]:
                v = e.get("rotte", {}).get(parti[2]) if len(parti) > 2 else e.get("valore")
                if isinstance(v, dict):
                    v = v.get("valore")
                return v, e.get("data"), f"docs/data/noli.json ({e.get('nome')})"
    return None, None, None


def calcola_costi(costi, prezzi, noli):
    out = []
    for ex in costi.get("esempi", []):
        dove = f"costi/{ex.get('id')}"
        nomi, ingressi = {}, {}
        for k, v in ex.get("ingressi", {}).items():
            if "auto" in v:
                val, data, fonte = ingresso_auto(v["auto"], prezzi, noli)
                if val is None:
                    avviso(f"{dove}: ingresso automatico '{v['auto']}' non disponibile")
                ingressi[k] = {**v, "valore": val, "data": data, "fonte": fonte, "link": v["auto"].split(":")[0] and "docs/data/" + v["auto"].split(":")[0], "affidabilita": "alta" if val is not None else "bassa", "tipo": "automatico"}
                nomi[k] = val
                continue
            if not isinstance(v.get("valore"), (int, float)):
                errore(f"{dove}: ingresso '{k}' senza valore numerico")
                continue
            if not v.get("ipotesi"):
                for c in ("fonte", "link", "data", "affidabilita"):
                    if not v.get(c):
                        errore(f"{dove}: ingresso '{k}' senza '{c}'")
                if v.get("link") and not link_ok(v["link"]):
                    errore(f"{dove}: ingresso '{k}' con link non valido")
            ingressi[k] = {**v, "tipo": "ipotesi" if v.get("ipotesi") else "fatto"}
            nomi[k] = v["valore"]
        risultati, passi = [], []
        for f in ex.get("formule", []):
            try:
                val = valuta(f["espr"], nomi)
            except KeyError as e:
                avviso(f"{dove}: formula '{f['nome']}' non calcolata, manca {e}")
                val = None
            except (ValueError, SyntaxError, ZeroDivisionError) as e:
                errore(f"{dove}: formula '{f['nome']}' non valida ({e})")
                val = None
            nomi[f["nome"]] = val
            if val is not None:
                val = round(val, 4 if abs(val) < 1 else 2)
            testo = f["espr"]
            for n in sorted(nomi, key=len, reverse=True):
                if nomi[n] is not None and re.search(rf"\b{re.escape(n)}\b", testo):
                    testo = re.sub(rf"\b{re.escape(n)}\b", fmt(nomi[n]), testo)
            risultati.append({"nome": f["nome"], "valore": val, "unita": f.get("unita"), "descrizione": f.get("descrizione")})
            passi.append(f"{f.get('descrizione', f['nome'])}: {testo} = {fmt(val)} {f.get('unita', '')}".strip())
        out.append({"id": ex["id"], "titolo": ex.get("titolo"), "area": ex.get("area"), "data_riferimento": ex.get("data_riferimento"),
                    "ingressi": ingressi, "risultati": risultati, "passi": passi, "lettura": ex.get("lettura")})
    return out


def fmt(x):
    if x is None:
        return "n.d."
    if isinstance(x, float) and not x.is_integer():
        return f"{x:,.4f}".rstrip("0").rstrip(".") if abs(x) < 1 else f"{x:,.2f}".rstrip("0").rstrip(".")
    return f"{int(x):,}" if isinstance(x, (int, float)) else str(x)


def serie_premi(premi):
    per_area = {}
    for p in premi.get("punti", []):
        if not p.get("in_serie") or p.get("non_pubblico"):
            continue
        centro = round((p["min"] + p["max"]) / 2, 4)
        per_area.setdefault(p["area"], []).append([p["data"], centro])
    for a in per_area:
        per_area[a].sort()
    ultimi = {}
    for a, nome in premi.get("aree", {}).items():
        punti = [p for p in premi.get("punti", []) if p["area"] == a and not p.get("non_pubblico") and p.get("base") == "scafo"]
        if not punti:
            continue
        u = max(punti, key=lambda p: p["data"])
        eta = (OGGI - a_data(u["data"])).days
        np_ = [p for p in premi.get("punti", []) if p["area"] == a and p.get("non_pubblico")]
        ultimi[a] = {"area": a, "nome": nome, "data": u["data"], "min": u["min"], "max": u["max"], "segmento": u.get("segmento"),
                     "fonte": u["fonte"], "link": u["link"], "giorni": eta,
                     "aggiornato_pubblico": eta <= GIORNI_PREMIO_VECCHIO,
                     "nota_non_pubblico": np_[-1]["note"] if np_ else None}
        documentato = any((OGGI - a_data(x["data_fonte"])).days <= 14 for x in np_ if data_ok(x.get("data_fonte", "")))
        if eta > GIORNI_PREMIO_VECCHIO and not documentato:
            avviso(f"premi/{a}: ultima quotazione pubblica del {u['data']} ({eta} giorni): cercarne una più recente")
    return per_area, ultimi


# ---------------------------------------------------------------- collegamenti

def km(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = p2 - p1, math.radians(lo2 - lo1)
    return 2 * 6371 * math.asin(math.sqrt(math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))


def collega_portwatch(area, pw):
    out = []
    if not pw:
        return out
    for nome in area.get("chokepoint_portwatch", []):
        el = next((e for e in pw.get("elementi", []) if e.get("nome") == nome), None)
        if not el:
            avviso(f"aree/{area['id']}: '{nome}' non trovato in portwatch.json")
            continue
        mensile = {}
        for d, v in el.get("serie", {}).get("n_total", []):
            mensile.setdefault(d[:7], []).append(v)
        mesi = sorted(mensile)[-24:]
        out.append({"nome": nome, "ultima_data": el.get("ultima_data"),
                    "navi_giorno_7g": el.get("media7", {}).get("n_total"),
                    "petroliere_giorno_7g": el.get("media7", {}).get("n_tanker"),
                    "var_anno_pct": el.get("var7_anno_pct", {}).get("n_total"),
                    "var_tre_anni_pct": el.get("var7_tre_anni_pct", {}).get("n_total"),
                    "serie_mensile": [[m + "-15", round(sum(mensile[m]) / len(mensile[m]), 1)] for m in mesi],
                    "fonte": "IMF PortWatch via docs/data/portwatch.json", "link": "docs/data/portwatch.json"})
    return out


def collega_eventi(area, ev):
    if not ev or not area.get("centro_eventi") or not area.get("raggio_eventi_km"):
        return None
    la, lo = area["centro_eventi"]
    r = area["raggio_eventi_km"]
    sel = []
    for p in ev.get("punti", []):
        d = p.get("data_evento") or ""
        if not (isinstance(p.get("lat"), (int, float)) and isinstance(p.get("lon"), (int, float)) and data_ok(d[:10])):
            continue
        if (OGGI - a_data(d[:10])).days > GIORNI_EVENTI:
            continue
        if not str(p.get("bersaglio", "")).startswith("nave") and p.get("categoria") != "chiusura-passaggio":
            continue
        if km(la, lo, p["lat"], p["lon"]) <= r:
            sel.append({"id": p.get("id"), "data": d[:10], "nome": p.get("nome"), "categoria": p.get("categoria"), "bersaglio": p.get("bersaglio")})
    sel.sort(key=lambda x: x["data"], reverse=True)
    return {"giorni": GIORNI_EVENTI, "raggio_km": r, "eventi_navi": len(sel), "ultimi": sel[:8], "fonte": "docs/data/eventi.json"}


# ---------------------------------------------------------------- controllo JWC online

def scarica(url, metodo="GET", timeout=40):
    req = urllib.request.Request(url, method=metodo, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        corpo = r.read() if metodo == "GET" else b""
        return corpo.decode("utf-8", "replace"), dict(r.headers)


def testo_html(h):
    h = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h)))


def id_circolare(s):
    m = re.search(r"(?:JWLA|JLWA)[-\s]?0*(\d{1,3})", s)
    if m:
        return f"JWLA-{int(m.group(1)):03d}"
    m = re.search(r"JW(\d{4})-(\d{3})", s)
    return f"JW{m.group(1)}-{m.group(2)}" if m else None


def controlla_jwc(circ):
    pag = circ.get("pagine_controllo", {})
    manuale = circ.get("ultimo_controllo_manuale", {})
    noti = {c["id"] for c in circ.get("circolari", [])}
    esito = {"data": ADESSO.strftime("%Y-%m-%dT%H:%MZ"), "lma": None, "iua": None, "cambiamenti": []}

    # 1) pagina pubblica LMA delle Listed Areas
    try:
        h, _ = scarica(pag["lma_listed_areas"])
        t = testo_html(h)
        m = re.search(r"last reviewed the areas in ([A-Za-z]+ \d{4})", t)
        pdf = sorted(set(re.findall(r"https://lmalloyds\.com/wp-content/uploads/[^\"' ]*JWLA[^\"' ]*\.pdf", h, re.I)))
        correnti = sorted({id_circolare(x) for x in pdf if id_circolare(x)})
        lma = {"url": pag["lma_listed_areas"], "frase_revisione": m.group(0) if m else None, "pdf": pdf, "circolari_linkate": correnti}
        if m and manuale.get("frase_revisione") and m.group(0) not in manuale["frase_revisione"]:
            esito["cambiamenti"].append(f"LMA: la frase di revisione è cambiata: «{m.group(0)}» (prima: «{manuale['frase_revisione']}»)")
        if not m:
            avviso("controllo JWC: frase «last reviewed the areas in…» non trovata sulla pagina LMA (struttura cambiata?)")
        if correnti and manuale.get("circolare_corrente_lma") not in correnti:
            esito["cambiamenti"].append(f"LMA: la pagina linka {', '.join(correnti)} invece di {manuale.get('circolare_corrente_lma')}")
        for c in correnti:
            if c not in noti:
                esito["cambiamenti"].append(f"LMA: circolare {c} non presente in circolari.json")
        for u in pdf:
            try:
                _, hd = scarica(u, metodo="HEAD")
                lm, cl = hd.get("Last-Modified") or hd.get("last-modified"), hd.get("Content-Length") or hd.get("content-length")
                lma.setdefault("pdf_intestazioni", []).append({"url": u, "last_modified": lm, "byte": int(cl) if cl and cl.isdigit() else None})
                if u == manuale.get("pdf_corrente"):
                    if lm and manuale.get("pdf_last_modified") and lm != manuale["pdf_last_modified"]:
                        esito["cambiamenti"].append(f"LMA: il PDF {u.rsplit('/', 1)[-1]} è stato modificato ({lm})")
                    if cl and manuale.get("pdf_byte") and int(cl) != manuale["pdf_byte"]:
                        esito["cambiamenti"].append(f"LMA: il PDF {u.rsplit('/', 1)[-1]} ha cambiato dimensione ({cl} byte)")
            except (urllib.error.URLError, OSError, ValueError) as e:
                avviso(f"controllo JWC: HEAD del PDF non riuscito ({u}): {e}")
        esito["lma"] = lma
    except (urllib.error.URLError, OSError, KeyError) as e:
        avviso(f"controllo JWC: pagina LMA non raggiungibile ({e})")

    # 2) elenco IUA delle circolari, con date
    try:
        h, _ = scarica(pag["iua_risk_list"])
        t = testo_html(h)
        trovate = []
        for m in re.finditer(r"((?:JWLA|JLWA|JW\d{4})[-\s]?\d{3}[^()]{0,120}?)\(\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*\)", t):
            cid = id_circolare(m.group(1))
            if not cid:
                continue
            try:
                d = dt.date(int(m.group(4)), int(m.group(2)), int(m.group(3))).isoformat()
            except ValueError:
                continue
            trovate.append({"id": cid, "titolo": m.group(1).strip(), "data": d})
        esito["iua"] = {"url": pag["iua_risk_list"], "circolari": trovate[:12], "totale": len(trovate)}
        if not trovate:
            avviso("controllo JWC: nessuna circolare letta dalla pagina IUA (struttura cambiata?)")
        date_note = {c["id"]: c.get("data_iua") for c in circ.get("circolari", [])}
        for c in trovate:
            if c["id"] not in noti and c["data"] >= "2021-01-01":
                esito["cambiamenti"].append(f"IUA: nuova circolare {c['id']} del {c['data']} («{c['titolo']}»)")
            elif c["id"] in date_note and date_note[c["id"]] and date_note[c["id"]] != c["data"]:
                esito["cambiamenti"].append(f"IUA: data di {c['id']} diversa ({c['data']} contro {date_note[c['id']]})")
    except (urllib.error.URLError, OSError, KeyError) as e:
        avviso(f"controllo JWC: pagina IUA non raggiungibile ({e})")

    for c in esito["cambiamenti"]:
        avviso("JWC CAMBIATO: " + c + " -> aggiornare a mano aree.json e circolari.json")
    esito["stato"] = ("cambiamenti da verificare" if esito["cambiamenti"] else
                      "nessun cambiamento" if (esito["lma"] or esito["iua"]) else "non controllato (rete)")
    return esito


# ---------------------------------------------------------------- confronto percepito / misurato

def confronti(ultimi, aree_out):
    """Accosta l'ultimo premio pubblico ai transiti PortWatch e agli attacchi recenti. Solo numeri dai file."""
    mappa = {"golfo-hormuz": ("golfo-oceano-indiano-mar-rosso", "Stretto di Hormuz"),
             "mar-rosso": ("golfo-oceano-indiano-mar-rosso", "Bab el-Mandeb"),
             "mar-nero": ("mar-nero-azov", "Bosforo")}
    out = []
    for premio_area, (area_id, cp) in mappa.items():
        u = ultimi.get(premio_area)
        a = next((x for x in aree_out if x["id"] == area_id), None)
        if not u or not a:
            continue
        t = next((x for x in a.get("transiti_portwatch", []) if x["nome"] == cp), None)
        out.append({"area": premio_area, "premio_ultimo_pct": [u["min"], u["max"]], "premio_data": u["data"],
                    "premio_pubblico_recente": u["aggiornato_pubblico"],
                    "transiti_passaggio": cp,
                    "navi_giorno_7g": t and t["navi_giorno_7g"], "var_anno_pct": t and t["var_anno_pct"],
                    "var_tre_anni_pct": t and t["var_tre_anni_pct"], "transiti_data": t and t["ultima_data"],
                    "attacchi_navi_30g": (a.get("eventi_recenti") or {}).get("eventi_navi")})
    return out


# ---------------------------------------------------------------- main

def main():
    solo_controllo = "--controlla" in sys.argv
    offline = "--offline" in sys.argv or solo_controllo

    aree = carica("aree.json")
    circ = carica("circolari.json")
    premi = carica("premi.json")
    costi = carica("costi.json")
    ev_ass = carica("eventi.json")
    concetti = carica("concetti.json")
    prezzi = carica("prezzi.json", False, DATI)
    noli = carica("noli.json", False, DATI)
    pw = carica("portwatch.json", False, DATI)
    eventi = carica("eventi.json", False, DATI)
    for nome, f in (("prezzi.json", prezzi), ("noli.json", noli), ("portwatch.json", pw), ("eventi.json", eventi)):
        if f is None:
            avviso(f"{nome} non disponibile: collegamento saltato")

    valida_aree(aree)
    ids_circ = valida_circolari(circ)
    valida_premi(premi)
    valida_eventi(ev_ass)
    valida_concetti(concetti)
    if aree.get("circolare_in_vigore") not in ids_circ:
        errore("aree.json: circolare_in_vigore assente da circolari.json")
    ultima_circ = max(circ.get("circolari", []), key=lambda c: c["data"]) if circ.get("circolari") else None
    if ultima_circ and ultima_circ["id"].startswith("JWLA") and ultima_circ["id"] != aree.get("circolare_in_vigore"):
        errore(f"aree.json descrive {aree.get('circolare_in_vigore')} ma l'ultima JWLA è {ultima_circ['id']}")

    esempi = calcola_costi(costi, prezzi, noli)
    serie, ultimi = serie_premi(premi)

    aree_out = []
    for a in aree.get("aree", []):
        x = {k: v for k, v in a.items() if k not in ("centro_eventi", "raggio_eventi_km", "chokepoint_portwatch")}
        x.update({"categoria": "area-elencata-jwc", "stato": "in lista", "fonte": aree.get("fonte"), "link": aree.get("link"),
                  "data_fonte": aree.get("data_circolare"), "affidabilita": "alta" if a.get("tipo") == "acque" or "precedente" not in str(a.get("data_inserimento")) else "media"})
        if a.get("tipo") == "acque":
            x["g"] = [[[round(c[0], 4), round(c[1], 4)] for c in parte] for parte in a["g"]]
            x["geometria"] = "poligono indicativo: vertici al largo dalla circolare, coste semplificate a mano"
        tp = collega_portwatch(a, pw)
        if tp:
            x["transiti_portwatch"] = tp
        er = collega_eventi(a, eventi)
        if er:
            x["eventi_recenti"] = er
        aree_out.append(x)

    controllo = None if offline else controlla_jwc(circ)

    fonti = [
        {"nome": "Joint War Committee (LMA/IUA), circolari JWLA e pagina pubblica «Listed areas»", "link": "https://lmalloyds.com/specialist-areas/underwriting/listed-areas/", "licenza": "documenti pubblici; citazione con link", "data_dato": aree.get("data_circolare")},
        {"nome": "IUA, Joint War Committee Risk List (elenco delle circolari con date)", "link": circ["pagine_controllo"]["iua_risk_list"], "licenza": "pagina pubblica; citazione con link", "data_dato": OGGI.isoformat()},
        {"nome": "Reuters (via Insurance Journal, BusinessLive, MarineLink, Claims Journal)", "link": "https://www.insurancejournal.com/news/international/2026/09/25/886769.htm", "licenza": "citazione con link; testo non ripubblicato", "data_dato": "2026-09-25"},
        {"nome": "S&P Global Platts / Marsh (via Al Jazeera, Hellenic Shipping News, Cyprus Shipping News)", "link": "https://www.aljazeera.com/economy/2026/7/23/how-shipping-insurance-rates-are-rising-as-hormuz-bab-al-mandeb-shut-down", "licenza": "citazione con link", "data_dato": "2026-07-23"},
        {"nome": "Howden Re, «Strait of Hormuz: (Re)insurance impact»", "link": "https://www.howdenre.com/sites/howdenre.howdenprod.com/files/2026-03/HowdenRe_Strait_of_Hormuz_report_March272026.pdf", "licenza": "rapporto pubblico; citazione", "data_dato": "2026-03-27"},
        {"nome": "Insurance Business (riprende FT, Marsh, LMA)", "link": "https://www.insurancebusinessmag.com/ca/news/marine/hormuz-sinking-hands-marine-war-underwriters-another-total-loss-as-attacks-surge-593542.aspx", "licenza": "citazione con link", "data_dato": "2026-10-14"},
        {"nome": "Bloomberg (via Insurance Journal, gCaptain, The Maritime Executive)", "link": "https://www.insurancejournal.com/news/international/2022/04/11/662371.htm", "licenza": "citazione con link", "data_dato": "2022-04-11"},
        {"nome": "Gard, circolare 01/2026; International Group of P&I Clubs", "link": "https://gard.no/en/circulars/notice-of-cancellation-for-war-risks/", "licenza": "documenti pubblici", "data_dato": "2026-03-01"},
        {"nome": "File dell'osservatorio: portwatch.json, eventi.json, prezzi.json, noli.json", "link": "docs/data/portwatch.json", "licenza": "dati dell'osservatorio", "data_dato": (pw or {}).get("aggiornato", "")[:10]},
    ]

    risultato = {
        "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": fonti,
        "nota": ("Come il rischio geopolitico diventa costo per la logistica marittima. Premi war risk in % del valore dello scafo per viaggio "
                 "(di solito 7 giorni): sono quotazioni di mercato riportate dalla stampa, non un indice ufficiale; i premi effettivi sono privati. "
                 "Aree: Listed Areas del Joint War Committee in vigore (circolare " + str(aree.get("circolare_in_vigore")) + "), poligoni indicativi. "
                 "Esempi di costo calcolati dallo script dagli ingressi con fonte. Dove un dato recente non è pubblico è scritto."),
        "schema": {
            "elementi[]": "aree elencate: id, nome, gruppo, tipo (acque/paese), lat, lon, paese, g (poligono [lon,lat], solo acque), data_inserimento, ultima_modifica, transiti_portwatch[], eventi_recenti",
            "serie_premi": "area -> [[AAAA-MM-GG, % centrale della forchetta]] solo segmento generico, base scafo",
            "premi_punti[]": "tutti i punti curati con min, max, segmento, fonte, link, data_fonte, affidabilita (anche quelli fuori serie e i 'non_pubblico')",
            "ultimo_premio": "per area: ultima quotazione pubblica e da quanti giorni",
            "esempi_costo[]": "ingressi (con fonte o ipotesi dichiarata), risultati calcolati, passi del calcolo in chiaro",
            "eventi_assicurativi[]": "ritiri di copertura, circolari JWC, schemi pubblici, sinistri, sanzioni",
            "circolari[]": "storia delle circolari JWLA",
            "controllo_jwc": "esito del controllo automatico delle pagine LMA e IUA",
            "percepito_misurato[]": "ultimo premio accanto a transiti PortWatch e attacchi recenti",
            "come_funziona[]": "schede brevi"},
        "circolare_in_vigore": {"id": aree.get("circolare_in_vigore"), "data": aree.get("data_circolare"), "link": aree.get("link")},
        "elementi": aree_out,
        "rimosse_di_recente": aree.get("rimosse_di_recente", []),
        "serie_premi": serie,
        "premi_unita": premi.get("unita"),
        "premi_aree": premi.get("aree"),
        "ultimo_premio": ultimi,
        "premi_punti": premi.get("punti", []),
        "esempi_costo": esempi,
        "eventi_assicurativi": sorted(ev_ass.get("eventi", []), key=lambda e: e["data"], reverse=True),
        "circolari": circ.get("circolari", []),
        "controllo_jwc": controllo or {"stato": "non eseguito (--offline o --controlla)"},
        "percepito_misurato": confronti(ultimi, aree_out),
        "come_funziona": concetti.get("concetti", []),
        "errori": errori,
        "avvisi": avvisi,
    }

    print(f"aree: {len(aree_out)}, punti di premio: {len(premi.get('punti', []))}, esempi: {len(esempi)}, "
          f"eventi assicurativi: {len(ev_ass.get('eventi', []))}, errori: {len(errori)}, avvisi: {len(avvisi)}")
    for e in esempi:
        for p in e["passi"]:
            print(f"  [{e['id']}] {p}")
    if solo_controllo:
        return
    with open(USCITA, "w", encoding="utf-8") as f:
        json.dump(risultato, f, ensure_ascii=False, separators=(",", ":"))
    print(f"scritto {USCITA} ({os.path.getsize(USCITA) // 1024} KB)")


if __name__ == "__main__":
    main()
