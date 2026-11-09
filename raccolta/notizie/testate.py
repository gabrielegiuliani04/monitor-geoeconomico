#!/usr/bin/env python3
"""Raccoglitore delle TESTATE (generaliste, economiche, di settore, centri studi) per argomento.

Affianca raccolta/notizie/raccogli.py (fonti OSINT specialistiche, file notizie.json) senza
toccarlo. Legge:
  raccolta/notizie/testate.json    elenco dei feed (RSS/Atom/RDF o ricerca Google News 'site:')
  raccolta/notizie/argomenti.json  12 argomenti con parole chiave (en, it, da/no, nl)
Per ogni articolo tiene SOLO titolo, data UTC, link, testata, sommario del feed (<= 300
caratteri) e immagine se il feed la da'. Mai il testo dell'articolo.
Poi: deduplica (stesso link o stesso titolo), classifica per argomento (piu' argomenti per
articolo), raggruppa le storie simili tra testate diverse, calcola un punteggio di
rilevanza per argomento, tiene gli ultimi 3 giorni (unendo il file precedente).

Produce: docs/data/notizie-testate.json
Uso:     python3 raccolta/notizie/testate.py   (dalla radice del repository)
Solo libreria standard. Nessuna chiave richiesta.
"""
import concurrent.futures as cf
import hashlib
import html
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
TESTATE = os.path.join(QUI, "testate.json")
ARGOMENTI = os.path.join(QUI, "argomenti.json")
OUT = os.path.join(RADICE, "docs", "data", "notizie-testate.json")

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124 Safari/537.36 monitor-geoeconomico",
      "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8"}
ORE = 72                  # finestra tenuta: 3 giorni
MAX_PER_FEED = 100
MAX_SOMMARIO = 300
SOGLIA_SIM = 0.30         # somiglianza pesata (idf) tra titoli per dire "stessa storia" (provata: 0.28-0.42)
FINESTRA_GRUPPO_H = 48    # due articoli della stessa storia entro 48 ore
ORA = datetime.now(timezone.utc)
PESO_AFFID = {"alta": 3.0, "media": 2.0, "bassa": 1.0}


# ---------------------------------------------------------------- utilita'
def scarica(url, timeout=25, tentativi=2):
    ultimo = None
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            ultimo = e
            if e.code in (401, 403, 404, 410):
                break
        except Exception as e:  # rete, timeout, lettura incompleta
            ultimo = e
        time.sleep(2 + 3 * i)
    raise ultimo


def pulisci(testo):
    if not testo:
        return ""
    t = html.unescape(testo)
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = "".join(c for c in t if unicodedata.category(c) not in ("So", "Cs", "Co", "Cc") or c in "\n\t")
    return re.sub(r"\s+", " ", t).strip()


CODE_SOMMARIO = re.compile(
    r"(The post .{3,200}? appeared first on .{2,80}?\.?$|Continue reading\.*$|Read more\.*$|"
    r"\[\s*(?:…|\.\.\.)\s*\]$|Leggi (?:tutto|l'articolo).*$|Lees verder.*$|Læs mere.*$)", re.I)


def sommario_breve(t, titolo):
    t = CODE_SOMMARIO.sub("", t).strip()
    if not t or t.lower() == titolo.lower() or t.lower().startswith(titolo.lower()) and len(t) < len(titolo) + 15:
        return ""
    if len(t) <= MAX_SOMMARIO:
        return t
    t = t[: MAX_SOMMARIO - 1]
    if " " in t[MAX_SOMMARIO // 2:]:
        t = t[: t.rfind(" ")]
    return t.rstrip(" ,;:.-") + "…"


def data_utc(s):
    if not s:
        return None
    s = s.strip()
    d = None
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        pass
    if d is None:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            m = re.match(r"(\d{1,2}) (\w+) (\d{4}) - (\d{1,2}):(\d{2})", s)  # "9 November 2026 - 19:40" (NL Times)
            if not m:
                return None
            try:
                d = datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)} {m.group(4)}:{m.group(5)}",
                                      "%d %B %Y %H:%M").replace(tzinfo=timezone(timedelta(hours=1)))
            except ValueError:
                return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def fmt(d):
    return d.strftime("%Y-%m-%dT%H:%MZ")


def link_canonico(url):
    try:
        p = urllib.parse.urlparse(url.strip())
        q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query)
             if not k.lower().startswith(("utm_", "at_", "ocid", "cmp", "ref", "taid", "src"))]
        host = (p.hostname or "").lower()
        host = host[4:] if host.startswith("www.") else host
        return urllib.parse.urlunparse(("https", host, p.path.rstrip("/"), "", urllib.parse.urlencode(q), ""))
    except Exception:
        return url.strip()


def senza_ns(tag):
    return tag.rsplit("}", 1)[-1].lower()


def figli(el, *nomi):
    return [c for c in el if senza_ns(c.tag) in nomi]


def figlio(el, *nomi):
    f = figli(el, *nomi)
    return f[0] if f else None


def url_immagine(v, html_grezzo):
    """Immagine dichiarata nel feed: media:content / media:thumbnail / enclosure / prima <img>."""
    cand = []
    for c in v.iter():
        n = senza_ns(c.tag)
        u = c.get("url") or c.get("href") or ""
        if n in ("content", "thumbnail") and u and c.tag.startswith("{http://search.yahoo.com/mrss"):
            tipo = (c.get("type") or c.get("medium") or "image").lower()
            if "image" in tipo or re.search(r"\.(jpe?g|png|webp)(\?|$)", u, re.I):
                try:
                    w = int(c.get("width") or 0)
                except ValueError:
                    w = 0
                cand.append((w, u))
        elif n == "enclosure" and u and "image" in (c.get("type") or ""):
            cand.append((0, u))
        elif n == "image" and u:
            cand.append((0, u))
    if cand:
        # la piu' larga, ma non oltre ~1200 px (risparmia banda); altrimenti la prima
        cand.sort(key=lambda x: (x[0] <= 1200, x[0]), reverse=True)
        u = cand[0][1]
    else:
        m = re.search(r"<img[^>]+src=[\"']([^\"']+)[\"']", html_grezzo or "", re.I)
        u = html.unescape(m.group(1)) if m else ""
    if u.startswith("//"):
        u = "https:" + u
    return u if u.startswith("https://") and len(u) < 600 else ""


# ---------------------------------------------------------------- lettura feed
def leggi_feed(t, dati):
    try:
        radice = ET.fromstring(dati)
    except ET.ParseError:
        testo = dati.decode("utf-8", "replace")
        testo = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", testo)
        testo = re.sub(r"&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)", "&amp;", testo)
        radice = ET.fromstring(testo.encode("utf-8"))
    voci = [e for e in radice.iter() if senza_ns(e.tag) in ("item", "entry")]
    out = []
    for v in voci[:MAX_PER_FEED]:
        tit = figlio(v, "title")
        titolo = pulisci("".join(tit.itertext()) if tit is not None else "")
        link = ""
        for c in figli(v, "link"):
            if c.get("href") and c.get("rel", "alternate") == "alternate":
                link = c.get("href")
                break
            if (c.text or "").strip():
                link = c.text.strip()
                break
        if not link:
            g = figlio(v, "guid", "id")
            if g is not None and (g.text or "").startswith("http"):
                link = g.text.strip()
        d = None
        for nome in ("pubdate", "published", "date", "updated", "issued"):
            c = figlio(v, nome)
            if c is not None and c.text:
                d = data_utc(c.text)
                if d:
                    break
        som = figlio(v, "description", "summary")
        if som is None or not "".join(som.itertext()).strip():
            som = figlio(v, "encoded", "content")
        grezzo = "".join(som.itertext()) if som is not None else ""
        enc = figlio(v, "encoded")
        img = url_immagine(v, grezzo + ("".join(enc.itertext()) if enc is not None else ""))
        nome_ed, dom_ed = "", ""
        src = figlio(v, "source")
        if src is not None:
            nome_ed = (src.text or "").strip()
            dom_ed = src.get("url") or ""
        if t["tipo_feed"] == "gnews":
            if nome_ed and titolo.endswith(" - " + nome_ed):
                titolo = titolo[: -len(" - " + nome_ed)].strip()
            grezzo, img = "", ""
        if t.get("solo_titolo"):
            grezzo = ""
        if titolo and link:
            out.append({"titolo": titolo, "link": link, "data": d, "sommario": sommario_breve(pulisci(grezzo), titolo),
                        "immagine": img, "editore": nome_ed, "dominio_editore": dom_ed})
    return out


def url_di(t):
    if t["tipo_feed"] == "gnews":
        return "https://news.google.com/rss/search?" + urllib.parse.urlencode(
            {"q": t["url"], "hl": "en-US", "gl": "US", "ceid": "US:en"})
    return t["url"]


def raccogli(t):
    t0 = time.time()
    try:
        dati = scarica(url_di(t), tentativi=3 if t["tipo_feed"] == "gnews" else 2)
        return t, leggi_feed(t, dati), None, round(time.time() - t0, 1)
    except Exception as e:
        return t, [], f"{type(e).__name__}: {str(e)[:150]}", round(time.time() - t0, 1)


# ---------------------------------------------------------------- argomenti
def compila_argomenti(argomenti):
    """Per ogni argomento due regex: parole senza maiuscole (confronto libero) e con maiuscole (esatto)."""
    out = {}
    for a in argomenti:
        libere, esatte = [], []
        for w in a["parole"]:
            pref = w.endswith("*")
            w0 = w.rstrip("*")
            p = re.escape(w0).replace(r"\ ", r"\s+") + (r"\w*" if pref else "")
            (esatte if any(c.isupper() for c in w0) else libere).append(p)
        rx = []
        if libere:
            rx.append(re.compile(r"(?<!\w)(?:" + "|".join(sorted(libere, key=len, reverse=True)) + r")(?!\w)", re.I))
        if esatte:
            rx.append(re.compile(r"(?<!\w)(?:" + "|".join(sorted(esatte, key=len, reverse=True)) + r")(?!\w)"))
        out[a["id"]] = rx
    return out


def colpi(testo, rxs):
    return sum(len(r.findall(testo)) for r in rxs)


# ---------------------------------------------------------------- raggruppamento
VUOTE = set("""a an the of to in on at for and or but with from by as is are was were be been has have had
it its this that these those after before over under into about amid against says said say new news live
latest update updates report reports more than up down out off how why what who when where will would could
can may might not no yes his her their our your they we you he she them us all any some one two three first
last year years week day days today tonight yesterday per via vs just also still now amid says' video watch
il lo la i gli le un uno una di da del della dei degli delle dal dalla nel nella nei con su sul sulla per tra
fra e ed o ma che chi non piu più come anche dopo prima oggi ieri sono stato stata ha hanno al alla ai agli
og i på en et af til med for den det de der som er var har ikke fra om efter ved over under nye
het een van en in op te met voor door bij naar niet wel ook dat die deze dit zijn wordt worden na om uit
""".split())


def gettoni(titolo):
    t = unicodedata.normalize("NFKD", titolo.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    out = set()
    for w in re.findall(r"[a-z0-9æøå]+", t):
        if w in VUOTE or (len(w) < 3 and not w.isdigit()):
            continue
        if len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.add(w)
    return out


def raggruppa(articoli):
    """Assegna un 'gruppo' agli articoli che raccontano la stessa storia (titoli simili, pesati per idf)."""
    n = len(articoli)
    df = {}
    for a in articoli:
        a["_g"] = gettoni(a["titolo"])
        for w in a["_g"]:
            df[w] = df.get(w, 0) + 1
    idf = {w: math.log(1 + n / c) for w, c in df.items()}
    padre = list(range(n))

    def radice(i):
        while padre[i] != i:
            padre[i] = padre[padre[i]]
            i = padre[i]
        return i

    indice = {}
    ordine = sorted(range(n), key=lambda i: articoli[i]["data_utc"])
    for i in ordine:
        a = articoli[i]
        da = datetime.strptime(a["data_utc"], "%Y-%m-%dT%H:%MZ")
        cand = {}
        for w in a["_g"]:
            for j in indice.get(w, ()):
                cand[j] = cand.get(j, 0) + 1
        for j, comuni in cand.items():
            if comuni < 2:
                continue
            b = articoli[j]
            if a["lingua"] != b["lingua"]:
                continue
            db = datetime.strptime(b["data_utc"], "%Y-%m-%dT%H:%MZ")
            if abs((da - db).total_seconds()) > FINESTRA_GRUPPO_H * 3600:
                continue
            inter = a["_g"] & b["_g"]
            uni = a["_g"] | b["_g"]
            if sum(idf[w] for w in inter) / max(1e-9, sum(idf[w] for w in uni)) >= SOGLIA_SIM:
                padre[radice(i)] = radice(j)
        for w in a["_g"]:
            indice.setdefault(w, []).append(i)
    per_radice = {}
    for i in ordine:
        per_radice.setdefault(radice(i), []).append(i)
    gruppi = list(per_radice.values())
    for a in articoli:
        a.pop("_g", None)
    return gruppi


# ---------------------------------------------------------------- principale
def main():
    conf = json.load(open(TESTATE, encoding="utf-8"))
    testate = conf["testate"]
    argdoc = json.load(open(ARGOMENTI, encoding="utf-8"))
    argomenti = argdoc["argomenti"]
    rx = compila_argomenti(argomenti)
    limite = ORA - timedelta(hours=ORE)

    print(f"Scarico {len(testate)} feed…", file=sys.stderr)
    risultati = []
    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        for r in ex.map(raccogli, testate):
            risultati.append(r)
            t, voci, err, sec = r
            print(f"  {t['id']:20s} {'ERRORE ' + err if err else str(len(voci)) + ' voci'} ({sec}s)", file=sys.stderr)

    per_link, per_titolo = {}, {}
    stato, errori = [], []
    for t, voci, err, sec in risultati:
        tenuti = 0
        for v in voci:
            d = v["data"]
            stimata = d is None
            if d is None:
                d = ORA
            if d > ORA + timedelta(minutes=30):
                d = ORA
            if d < limite:
                continue
            testo_t = v["titolo"]
            testo_s = v["sommario"]
            args = {}
            for a in argomenti:
                ct = colpi(testo_t, rx[a["id"]])
                cs = colpi(testo_s, rx[a["id"]])
                if ct or cs >= 2:   # nel solo sommario servono almeno due parole chiave
                    args[a["id"]] = (ct, cs)
            if not args and t.get("predefinito"):
                args[t["predefinito"]] = (0, 0)
            if not args:
                continue
            canon = link_canonico(v["link"])
            chiave_t = (t["testata"], re.sub(r"\W+", " ", testo_t.lower()).strip())
            prec = per_link.get(canon) or per_titolo.get(chiave_t)
            if prec:  # stesso articolo in due sezioni della stessa testata (o ripetuto)
                for k, val in args.items():
                    if k not in prec["_colpi"] or sum(val) > sum(prec["_colpi"][k]):
                        prec["_colpi"][k] = val
                if t["sezione"] not in prec["sezioni"]:
                    prec["sezioni"].append(t["sezione"])
                if not prec["immagine"] and v["immagine"]:
                    prec["immagine"] = v["immagine"]
                if not prec["sommario"] and v["sommario"]:
                    prec["sommario"] = v["sommario"]
                continue
            el = {
                "id": "T-" + hashlib.sha1(canon.encode()).hexdigest()[:12],
                "titolo": testo_t,
                "data_utc": fmt(d),
                "link": v["link"],
                "testata": t["testata"],
                "fonte_id": t["id"],
                "sezioni": [t["sezione"]],
                "lingua": t["lingua"],
                "paese": t["paese"],
                "tipo": t["tipo"],
                "paywall": t["paywall"],
                "affidabilita": t["affidabilita"],
                "via": "Google News" if t["tipo_feed"] == "gnews" else "",
                "sommario": testo_s,
                "immagine": v["immagine"],
            }
            if stimata:
                el["data_stimata"] = True
            el["_colpi"] = args
            per_link[canon] = el
            per_titolo[chiave_t] = el
            tenuti += 1
        stato.append({"id": t["id"], "testata": t["testata"], "sezione": t["sezione"],
                      "esito": "errore" if err else "ok", "letti": len(voci), "tenuti": tenuti,
                      "secondi": sec, "errore": err or ""})
        if err:
            errori.append(f"{t['id']} ({t['testata']}): {err}")

    nuovi = list(per_link.values())
    for el in nuovi:
        el["argomenti"] = sorted(el["_colpi"], key=lambda k: -(2 * el["_colpi"][k][0] + el["_colpi"][k][1]))

    # unione con il file precedente (articoli usciti dal feed ma ancora nei 3 giorni)
    visti = {e["id"] for e in nuovi}
    tit_visti = {(e["testata"], e["titolo"].lower()) for e in nuovi}
    recuperati = 0
    if os.path.exists(OUT):
        try:
            vecchio = json.load(open(OUT, encoding="utf-8"))
            for e in vecchio.get("elementi", []):
                if e["id"] in visti or (e["testata"], e["titolo"].lower()) in tit_visti:
                    continue
                if datetime.strptime(e["data_utc"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc) < limite:
                    continue
                e = {k: v for k, v in e.items() if k not in ("gruppo", "n_testate", "testate_gruppo", "rilevanza", "punteggio")}
                e["_colpi"] = {k: tuple(v) for k, v in e.pop("colpi", {}).items()} or {k: (0, 0) for k in e["argomenti"]}
                nuovi.append(e)
                visti.add(e["id"])
                recuperati += 1
        except Exception as ex:
            errori.append(f"file precedente non leggibile: {ex}")

    articoli = sorted(nuovi, key=lambda e: e["data_utc"], reverse=True)

    # raggruppa storie simili tra testate
    gruppi = raggruppa(articoli)
    storie = []
    for membri in gruppi:
        els = [articoli[i] for i in membri]
        testate_g = sorted({e["testata"] for e in els})
        gid = "S-" + hashlib.sha1(min(e["id"] for e in els).encode()).hexdigest()[:10]
        for e in els:
            e["gruppo"] = gid
            e["n_testate"] = len(testate_g)
        if len(testate_g) >= 2:
            storie.append((gid, els, testate_g))

    # rilevanza per argomento: fonte + testate che riportano la storia + parole nel titolo + freschezza
    for e in articoli:
        d = datetime.strptime(e["data_utc"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
        ore = (ORA - d).total_seconds() / 3600
        base = PESO_AFFID.get(e["affidabilita"], 2.0)
        base += 2.0 * min(6, e["n_testate"] - 1)
        base += 2.0 if ore < 12 else (1.0 if ore < 24 else 0.0)
        if e["tipo"] in ("settore", "analisi"):
            base += 0.5
        ril = {}
        for k in e["argomenti"]:
            ct, cs = e["_colpi"].get(k, (0, 0))
            ril[k] = round(base + 1.5 * min(3, ct) + 0.5 * min(2, cs), 1)
        e["rilevanza"] = ril
        e["punteggio"] = max(ril.values())
        e["colpi"] = {k: list(v) for k, v in e.pop("_colpi").items()}

    out_storie = []
    for gid, els, testate_g in storie:
        args = {}
        for e in els:
            for k, v in e["rilevanza"].items():
                args[k] = max(args.get(k, 0), v)
        # titolo rappresentativo: testata piu' affidabile, con sommario, poi la piu' recente
        rap = sorted(els, key=lambda e: (PESO_AFFID.get(e["affidabilita"], 2), bool(e["sommario"]),
                                         e["tipo"] == "generalista", e["data_utc"]), reverse=True)[0]
        img = next((e["immagine"] for e in els if e["immagine"]), "")
        out_storie.append({
            "id": gid, "titolo": rap["titolo"], "sommario": rap["sommario"], "link": rap["link"],
            "testata_principale": rap["testata"], "testate": testate_g, "n_testate": len(testate_g),
            "argomenti": sorted(args, key=lambda k: -args[k]), "rilevanza": {k: round(v, 1) for k, v in args.items()},
            "prima": min(e["data_utc"] for e in els), "ultima": max(e["data_utc"] for e in els),
            "lingua": rap["lingua"], "immagine": img, "articoli": [e["id"] for e in els],
        })
    out_storie.sort(key=lambda s: (s["n_testate"], max(s["rilevanza"].values())), reverse=True)

    # riepilogo
    un_giorno = fmt(ORA - timedelta(hours=24))
    riep = {"articoli": len(articoli), "storie_multi_testata": len(out_storie), "recuperati_dal_giro_prima": recuperati,
            "feed_ok": sum(1 for s in stato if s["esito"] == "ok"), "feed_errore": sum(1 for s in stato if s["esito"] != "ok"),
            "per_argomento": {}, "per_lingua": {}}
    for a in argomenti:
        k = a["id"]
        tutti = [e for e in articoli if k in e["argomenti"]]
        riep["per_argomento"][k] = {"3_giorni": len(tutti), "24_ore": sum(1 for e in tutti if e["data_utc"] >= un_giorno),
                                    "storie_multi_testata": sum(1 for s in out_storie if k in s["argomenti"])}
    for e in articoli:
        riep["per_lingua"][e["lingua"]] = riep["per_lingua"].get(e["lingua"], 0) + 1

    fonti = []
    for t in testate:
        fonti.append({"id": t["id"], "nome": f"{t['testata']} ({t['sezione']})", "testata": t["testata"],
                      "sezione": t["sezione"], "link": t["url"] if t["tipo_feed"] == "rss" else url_di(t),
                      "tipo_feed": t["tipo_feed"], "lingua": t["lingua"], "paese": t["paese"], "tipo": t["tipo"],
                      "paywall": t["paywall"], "affidabilita": t["affidabilita"],
                      "licenza": "articoli dell'editore: solo titolo, sommario del feed e link",
                      "data_dato": fmt(ORA)})

    doc = {
        "aggiornato": fmt(ORA),
        "fonti": fonti,
        "nota": ("Notizie delle testate generaliste e di settore, per argomento. Solo titolo, sommario breve del feed "
                 "(<= 300 caratteri), immagine se il feed la da' e link all'articolo originale: il testo resta "
                 "dell'editore. Ultimi 3 giorni. 'gruppo' unisce gli articoli sulla stessa storia (titoli simili, "
                 "stessa lingua, entro 48 ore); 'rilevanza' per argomento = affidabilita' della testata + 2 punti per "
                 "ogni altra testata sulla stessa storia + parole chiave nel titolo e nel sommario + freschezza. "
                 "Classificazione automatica a parole chiave (raccolta/notizie/argomenti.json): puo' sbagliare."),
        "argomenti": argomenti,
        "riepilogo": riep,
        "stato_fonti": stato,
        "storie": out_storie,
        "elementi": articoli,
        "errori": errori,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, OUT)
    print(f"Scritto {OUT}: {len(articoli)} articoli, {len(out_storie)} storie con piu' testate, "
          f"{riep['feed_ok']}/{len(testate)} feed ok, {os.path.getsize(OUT) // 1024} KB", file=sys.stderr)
    for k, v in riep["per_argomento"].items():
        print(f"  {k:16s} 24h {v['24_ore']:4d}  3g {v['3_giorni']:4d}  storie {v['storie_multi_testata']}", file=sys.stderr)


if __name__ == "__main__":
    main()
