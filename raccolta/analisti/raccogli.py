#!/usr/bin/env python3
"""Di cosa parlano gli analisti: video recenti di alcuni canali YouTube italiani
di mercati, con i temi e i titoli/asset citati, messi accanto ai prezzi.

Solo libreria standard (urllib, xml.etree, json, re). Fonte: feed RSS pubblico
di YouTube (https://www.youtube.com/feeds/videos.xml?channel_id=<id>), che da'
gli ultimi 15 video per canale: titolo, data, descrizione, miniatura,
visualizzazioni e voti. Niente trascrizioni (YouTube le blocca dagli indirizzi
cloud): i temi si ricavano solo da titolo e descrizione.

File letti (stessa cartella):
  canali.json  canali da seguire (nome, handle, channel_id)
  temi.json    dizionario dei temi e degli asset, con le serie di prezzi collegate
Altri file letti:
  docs/data/prezzi.json    serie dei prezzi (per le variazioni a 1 settimana/1 mese)
  docs/data/analisti.json  uscita precedente: archivio dei video gia' visti, cosi'
                           il confronto con la settimana precedente non dipende
                           solo dagli ultimi 15 video del feed
Uscita: docs/data/analisti.json

Variabili d'ambiente facoltative:
  OGGI   data di riferimento AAAA-MM-GG (per test; default: oggi, ora di Roma)
"""
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
USCITA = os.path.join(RADICE, "docs", "data", "analisti.json")
PREZZI = os.path.join(RADICE, "docs", "data", "prezzi.json")
CANALI = os.path.join(QUI, "canali.json")
TEMI = os.path.join(QUI, "temi.json")
TRASCRIZIONI = os.path.join(QUI, "trascrizioni")  # facoltativo: <video_id>.json dal computer locale

FEED = "https://www.youtube.com/feeds/videos.xml?channel_id={}"
UA = "monitor-geoeconomico/1.0 (ricerca OSINT non commerciale)"
NS = {"a": "http://www.w3.org/2005/Atom",
      "m": "http://search.yahoo.com/mrss/",
      "yt": "http://www.youtube.com/xml/schemas/2015"}

MAX_VIDEO = 15          # il feed ne da' al massimo 15
MAX_DESCR = 600         # caratteri di descrizione salvati
GIORNI_ARCHIVIO = 70    # quanto tenere i video gia' visti
FINESTRA = 7            # giorni di una "settimana" (finestre mobili)

try:
    from zoneinfo import ZoneInfo
    ROMA = ZoneInfo("Europe/Rome")
except Exception:  # tzdata mancante: si usa UTC
    ROMA = dt.timezone.utc

ADESSO = dt.datetime.now(dt.timezone.utc)
OGGI = (dt.date.fromisoformat(os.environ["OGGI"]) if os.environ.get("OGGI")
        else ADESSO.astimezone(ROMA).date())

ERRORI = []


def avviso(msg):
    print("AVVISO:", msg, file=sys.stderr)
    ERRORI.append(msg)


# ---------------------------------------------------------------- download
def scarica(url, timeout=30, tentativi=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "it,en"})
    ultimo = None
    for k in range(tentativi):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            ultimo = e
            # 404 = canale inesistente: inutile riprovare
            if isinstance(e, urllib.error.HTTPError) and e.code == 404:
                break
            time.sleep(2 * (k + 1))
    raise RuntimeError("download fallito: %s (%s)" % (url, ultimo))


# ---------------------------------------------------------------- parole chiave
def compila(termine):
    """'=AI' maiuscole esatte, 'chip*' prefisso, altrimenti parola intera senza maiuscole."""
    esatto = termine.startswith("=")
    t = termine[1:] if esatto else termine
    prefisso = t.endswith("*")
    t = t.rstrip("*")
    corpo = re.escape(t).replace(r"\ ", r"[\s\-]+")  # 'data center' trova anche 'data-center'
    pat = r"(?<!\w)" + corpo + (r"\w*" if prefisso else "") + r"(?!\w)"
    return re.compile(pat, 0 if esatto else re.IGNORECASE)


def prepara_dizionario(diz):
    temi, asset = [], []
    for t in diz["temi"]:
        temi.append({**t, "_re": [compila(p) for p in t["parole"]],
                     "_escl": [compila(e) for e in t.get("escludi", [])]})
    for a in diz["asset"]:
        asset.append({**a, "_re": [compila(p) for p in a["alias"]],
                      "_escl": [compila(e) for e in a.get("escludi", [])]})
    return temi, asset


def trova(voce, testo):
    """Prima parola chiave trovata (o None)."""
    for e in voce["_escl"]:
        testo = e.sub(" ", testo)
    for r in voce["_re"]:
        m = r.search(testo)
        if m:
            return m.group(0)
    return None


def classifica(voci, titolo, descr):
    """[{id, dove: titolo|descrizione, parola}]"""
    out = []
    for v in voci:
        p = trova(v, titolo)
        if p:
            out.append({"id": v["id"], "dove": "titolo", "parola": p})
            continue
        p = trova(v, descr)
        if p:
            out.append({"id": v["id"], "dove": "descrizione", "parola": p})
    return out


# ---------------------------------------------------------------- descrizioni
URL_RE = re.compile(r"https?://\S+|www\.\S+")
CAPITOLO_RE = re.compile(r"^\s*((?:\d{1,2}:)?\d{1,2}:\d{2})\s+[-–—]?\s*(.+)$")
# righe di servizio: avvertenze legali, promozioni, social, affiliazioni
SERVIZIO_RE = re.compile(
    r"consulen[zt]|raccomandazion|sollecitazion|non costituisc|capitale investito|"
    r"emittente|garante|\bKID\b|prospetto|documentazione (legale|di offerta)|messaggio pubblicitari|"
    r"materiale pubblicitario|avvertenz|disclaimer|DYOR|affiliazion|#ADV|iscriviti|seguimi|"
    r"telegram|instagram|twitter|tiktok|linkedin|substack|patreon|sconto|bonus|registrati|"
    r"link (in|nella) descrizione|performance passate|rischio di perdita|perdere l'intero|"
    r"i nostri prodotti|vi aspettiamo|appuntamento a milano",
    re.IGNORECASE)


HASHTAG_RE = re.compile(r"#\w+")
SOLO_HASHTAG_RE = re.compile(r"^\s*(#\w+[\s,.;]*)+$")


def norm_riga(r):
    r = URL_RE.sub("", r).lower()
    r = re.sub(r"^\s*(\d{1,2}:)?\d{1,2}:\d{2}\s*", "", r)  # timestamp dei capitoli
    return re.sub(r"[\W_]+", " ", r).strip()


def righe_ricorrenti(descrizioni):
    """Righe che tornano in almeno 3 video dello stesso canale (firma, link, hashtag fissi)."""
    conta = {}
    for d in descrizioni:
        for r in set(norm_riga(x) for x in d.splitlines()):
            if len(r) >= 3:
                conta[r] = conta.get(r, 0) + 1
    soglia = max(3, int(0.2 * len(descrizioni)))
    return {r for r, n in conta.items() if n >= soglia}


def pulisci(descr, ricorrenti):
    """Toglie righe ricorrenti, righe di servizio e link. Restituisce (testo, capitoli)."""
    tenute, capitoli = [], []
    for riga in descr.splitlines():
        n = norm_riga(riga)
        if not n or n in ricorrenti or SERVIZIO_RE.search(riga) or SOLO_HASHTAG_RE.match(riga):
            continue
        m = CAPITOLO_RE.match(riga)
        if m:
            titolo = re.sub(r"\s+", " ", HASHTAG_RE.sub("", m.group(2))).strip()
            if titolo:
                capitoli.append([m.group(1), titolo[:120]])
            continue
        r = URL_RE.sub("", riga)
        r = re.sub(r"#(\w+)", r"\1", r)
        r = re.sub(r"[►▶👉👇🔎📣🌐📈✅💰⚠️]+", " ", r)
        r = re.sub(r"\s+", " ", r).strip(" -–—:|")
        if len(r) >= 3:
            tenute.append(r)
    return "\n".join(tenute).strip(), capitoli


def secondi(ts):
    s = 0
    for p in ts.split(":"):
        s = s * 60 + int(p)
    return s


def tronca(t, n):
    if len(t) <= n:
        return t
    return t[:n].rsplit(" ", 1)[0].rstrip(" ,.;:") + "…"


# ---------------------------------------------------------------- trascrizioni (facoltative)
def leggi_trascrizione(video_id):
    """(testo, riassunto) da raccolta/analisti/trascrizioni/<id>.json, prodotti dallo script locale
    trascrivi_locale.py. Il testo del parlato serve solo a riconoscere i temi: non va in uscita."""
    f = os.path.join(TRASCRIZIONI, video_id + ".json")
    if not os.path.exists(f):
        return "", ""
    try:
        d = json.load(open(f, encoding="utf-8"))
        return d.get("testo") or "", d.get("riassunto") or ""
    except Exception as e:
        avviso("trascrizione %s non leggibile: %s" % (video_id, e))
        return "", ""


# ---------------------------------------------------------------- feed
def leggi_feed(canale):
    xml = scarica(FEED.format(canale["channel_id"]))
    radice = ET.fromstring(xml)
    video = []
    for e in radice.findall("a:entry", NS)[:MAX_VIDEO]:
        vid = e.findtext("yt:videoId", "", NS)
        g = e.find("m:group", NS)
        link_el = e.find("a:link", NS)
        link = link_el.get("href") if link_el is not None else "https://www.youtube.com/watch?v=" + vid
        st = e.find("m:group/m:community/m:statistics", NS)
        voto = e.find("m:group/m:community/m:starRating", NS)
        mini = e.find("m:group/m:thumbnail", NS)
        video.append({
            "id": vid,
            "titolo": html.unescape(e.findtext("a:title", "", NS)).strip(),
            "pubblicato": e.findtext("a:published", "", NS),
            "aggiornato_feed": e.findtext("a:updated", "", NS),
            "link": link,
            "miniatura": mini.get("url") if mini is not None else None,
            "descr_raw": html.unescape(g.findtext("m:description", "", NS) if g is not None else ""),
            "visualizzazioni": int(st.get("views")) if st is not None and st.get("views", "").isdigit() else None,
            "voti": int(voto.get("count")) if voto is not None and voto.get("count", "").isdigit() else None,
        })
    return video


def data_roma(iso):
    try:
        return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(ROMA).date()
    except Exception:
        return None


# ---------------------------------------------------------------- prezzi
def indietro(serie, giorni=None, mesi=None):
    """Valore all'ultima data <= (ultima data - periodo)."""
    ultima = dt.date.fromisoformat(serie[-1][0])
    if mesi:
        a, m = ultima.year, ultima.month - mesi
        while m <= 0:
            a, m = a - 1, m + 12
        g = min(ultima.day, [31, 29 if a % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
        obiettivo = dt.date(a, m, g)
    else:
        obiettivo = ultima - dt.timedelta(days=giorni)
    prec = None
    for d, v in serie:
        if dt.date.fromisoformat(d) <= obiettivo:
            prec = (d, v)
        else:
            break
    return prec


def variazione(s, base):
    if base is None or base[1] in (None, 0):
        return None
    if s.get("var_unita") == "punti base":
        return round((s["serie"][-1][1] - base[1]) * 100)
    return round((s["serie"][-1][1] / base[1] - 1) * 100, 2)


def scheda_serie(s):
    if not s.get("serie"):
        return None
    b1s = indietro(s["serie"], giorni=7)
    b1m = indietro(s["serie"], mesi=1)
    return {
        "id": s["id"], "nome": s["nome"], "gruppo": s.get("gruppo"),
        "ultimo": s["serie"][-1][1], "data": s["serie"][-1][0], "unita": s.get("unita"),
        "var_1s": variazione(s, b1s), "var_1m": variazione(s, b1m),
        "unita_var": "punti base" if s.get("var_unita") == "punti base" else "%",
        "base_1s": b1s[0] if b1s else None, "base_1m": b1m[0] if b1m else None,
        "fonte": s.get("fonte"), "link": s.get("link"),
    }


def num_it(x, dec=1, segno=True):
    t = ("%+.*f" if segno else "%.*f") % (dec, x)
    return t.replace("-", "−").replace(".", ",")


def frase_serie(sc):
    if sc is None:
        return ""
    pezzi = []
    for k, et in (("var_1s", "1 settimana"), ("var_1m", "1 mese")):
        v = sc.get(k)
        if v is None:
            continue
        if sc["unita_var"] == "punti base":
            pezzi.append("%s pb in %s" % (num_it(v, 0), et))
        else:
            pezzi.append("%s%% in %s" % (num_it(v, 1), et))
    return "%s %s" % (sc["nome"], ", ".join(pezzi)) if pezzi else sc["nome"]


# ---------------------------------------------------------------- conteggi
def finestra(video, dal, al):
    return [v for v in video if v.get("data") and dal <= v["data"] <= al]


def conta_temi(video, chiave):
    """{id: {video, titolo, canali:set, esempi:[...]}}"""
    out = {}
    for v in video:
        for t in v.get(chiave, []):
            c = out.setdefault(t["id"], {"video": 0, "titolo": 0, "canali": set(), "esempi": []})
            c["video"] += 1
            c["titolo"] += t["dove"] == "titolo"
            c["canali"].add(v["canale"])
            c["esempi"].append(v)
    return out


def esempio(v):
    return {"titolo": v["titolo"], "canale": v["canale"], "data": v["data"], "link": v["link"]}


def scegli_esempi(lista, n=3):
    # prima i video con il tema nel titolo, poi i piu' recenti; al massimo uno per canale se possibile
    lista = sorted(lista, key=lambda v: v["data"] or "", reverse=True)
    scelti, canali = [], set()
    for v in lista:
        if v["canale"] not in canali:
            scelti.append(v)
            canali.add(v["canale"])
        if len(scelti) == n:
            break
    for v in lista:
        if len(scelti) == n:
            break
        if v not in scelti:
            scelti.append(v)
    return [esempio(v) for v in scelti]


# ---------------------------------------------------------------- principale
def main():
    canali = json.load(open(CANALI, encoding="utf-8"))["canali"]
    diz = json.load(open(TEMI, encoding="utf-8"))
    firma_diz = hashlib.sha1(json.dumps(diz, sort_keys=True).encode()).hexdigest()[:12]
    temi, asset = prepara_dizionario(diz)
    nomi_temi = {t["id"]: t["nome"] for t in temi}
    nomi_asset = {a["id"]: a["nome"] for a in asset}

    try:
        prezzi = json.load(open(PREZZI, encoding="utf-8"))
        serie_prezzi = {s["id"]: s for s in prezzi.get("serie", [])}
    except Exception as e:
        avviso("prezzi.json non leggibile: %s" % e)
        prezzi, serie_prezzi = {}, {}

    # archivio: video gia' visti nelle esecuzioni precedenti
    archivio = {}
    firma_vecchia = None
    if os.path.exists(USCITA):
        try:
            vecchio = json.load(open(USCITA, encoding="utf-8"))
            firma_vecchia = vecchio.get("firma_dizionario")
            for el in vecchio.get("elementi", []):
                archivio[el["id"]] = el
        except Exception as e:
            avviso("uscita precedente non leggibile, riparto da zero: %s" % e)

    fonti, stato_canali, nuovi = [], [], {}
    for c in canali:
        info = {"nome": c["nome"], "handle": c.get("handle"), "channel_id": c["channel_id"],
                "link": "https://www.youtube.com/channel/" + c["channel_id"]}
        try:
            video = leggi_feed(c)
        except Exception as e:
            avviso("%s: %s" % (c["nome"], e))
            info.update({"video_nel_feed": 0, "errore": str(e)})
            stato_canali.append(info)
            continue
        ricorrenti = righe_ricorrenti([v["descr_raw"] for v in video]) if len(video) >= 4 else set()
        for v in video:
            testo, capitoli = pulisci(v["descr_raw"], ricorrenti)
            parlato, riassunto = leggi_trascrizione(v["id"])
            cerca = testo + "\n" + " ".join(t for _, t in capitoli) + "\n" + riassunto + "\n" + parlato
            short = "/shorts/" in v["link"]
            durata_min = secondi(capitoli[-1][0]) if capitoli else None
            el = {
                "id": "yt:" + v["id"],
                "video_id": v["id"],
                "canale": c["nome"],
                "channel_id": c["channel_id"],
                "titolo": v["titolo"],
                "data": (data_roma(v["pubblicato"]) or OGGI).isoformat(),
                "pubblicato": v["pubblicato"],
                "link": v["link"],
                "tipo": "short" if short else "video",
                "miniatura": v["miniatura"],
                "descrizione": tronca(testo, MAX_DESCR),
                "capitoli": capitoli[:25],
                "durata_s": None,
                "durata_almeno_s": durata_min,
                "durata_nota": ("short: al massimo 3 minuti" if short else
                                "almeno fino all'ultimo capitolo indicato nella descrizione" if durata_min else
                                "non presente nel feed RSS"),
                "visualizzazioni": v["visualizzazioni"],
                "visualizzazioni_al": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
                "voti": v["voti"],
                "programmato": v["visualizzazioni"] == 0,
                "temi": classifica(temi, v["titolo"], cerca),
                "asset": classifica(asset, v["titolo"], cerca),
                "trascrizione": bool(parlato or riassunto),
                "riassunto": tronca(riassunto, MAX_DESCR) or None,
                "fonte": "YouTube, feed RSS del canale " + c["nome"],
                "data_fonte": v["aggiornato_feed"][:10],
                "affidabilita": "bassa",
                "note": "Opinione dell'autore del video, non un fatto. Temi ricavati da titolo e descrizione, non dal parlato.",
            }
            nuovi[el["id"]] = el
        date = sorted(v["pubblicato"][:10] for v in video)
        info.update({"video_nel_feed": len(video), "dal": date[0] if date else None,
                     "al": date[-1] if date else None})
        stato_canali.append(info)
        fonti.append({"nome": "YouTube – " + c["nome"] + " (feed RSS)", "link": FEED.format(c["channel_id"]),
                      "licenza": "Contenuti degli autori (tutti i diritti riservati): si salvano solo titolo, breve descrizione e link",
                      "data_dato": ADESSO.strftime("%Y-%m-%d")})

    # unione con l'archivio: i video del feed sostituiscono quelli salvati
    limite = (OGGI - dt.timedelta(days=GIORNI_ARCHIVIO)).isoformat()
    tutti = {}
    for k, el in archivio.items():
        if el.get("data", "") >= limite and k not in nuovi:
            if firma_vecchia != firma_diz:  # dizionario cambiato: ricalcolo su titolo + descrizione salvata
                cap = " ".join(t for _, t in el.get("capitoli", []))
                el["temi"] = classifica(temi, el["titolo"], el.get("descrizione", "") + "\n" + cap)
                el["asset"] = classifica(asset, el["titolo"], el.get("descrizione", "") + "\n" + cap)
            el["solo_archivio"] = True
            tutti[k] = el
    tutti.update(nuovi)
    elementi = sorted(tutti.values(), key=lambda e: (e.get("pubblicato", ""), e["id"]), reverse=True)

    # copertura per canale (archivio compreso)
    corr_al, corr_dal = OGGI, OGGI - dt.timedelta(days=FINESTRA - 1)
    prec_al, prec_dal = corr_dal - dt.timedelta(days=1), corr_dal - dt.timedelta(days=FINESTRA)
    for info in stato_canali:
        date = [e["data"] for e in elementi if e["channel_id"] == info["channel_id"]]
        info["archivio_dal"] = min(date) if date else None
        info["video_in_archivio"] = len(date)
        info["copre_settimana_precedente"] = bool(date) and min(date) <= prec_dal.isoformat()

    corr = finestra(elementi, corr_dal.isoformat(), corr_al.isoformat())
    prec = finestra(elementi, prec_dal.isoformat(), prec_al.isoformat())
    utili_c = [v for v in corr if v["temi"]]
    utili_p = [v for v in prec if v["temi"]]
    tc, tp = conta_temi(corr, "temi"), conta_temi(prec, "temi")
    ac, ap = conta_temi(corr, "asset"), conta_temi(prec, "asset")

    def quota(n, tot):
        return round(n / tot, 3) if tot else None

    totale = []
    for t in temi:
        c, p = tc.get(t["id"]), tp.get(t["id"])
        if not c and not p:
            continue
        nc, np_ = (c["video"] if c else 0), (p["video"] if p else 0)
        totale.append({
            "tema": t["id"], "nome": t["nome"],
            "video": nc, "nel_titolo": c["titolo"] if c else 0, "video_prec": np_,
            "canali": sorted(c["canali"]) if c else [],
            "quota": quota(nc, len(utili_c)), "quota_prec": quota(np_, len(utili_p)),
            "punteggio": (c["video"] + c["titolo"]) if c else 0,
            "esempi": scegli_esempi(c["esempi"]) if c else [],
        })
    totale.sort(key=lambda r: (-r["punteggio"], -len(r["canali"]), r["nome"]))

    # temi in crescita/calo: confronto omogeneo, solo canali che coprono entrambe le finestre
    # (il feed da' solo gli ultimi 15 video: un canale molto attivo non arriva alla settimana prima)
    confrontabili = {i["channel_id"] for i in stato_canali if i.get("copre_settimana_precedente")}
    cc_ = [v for v in corr if v["channel_id"] in confrontabili]
    pp_ = [v for v in prec if v["channel_id"] in confrontabili]
    uc_, up_ = sum(1 for v in cc_ if v["temi"]), sum(1 for v in pp_ if v["temi"])
    kc, kp = conta_temi(cc_, "temi"), conta_temi(pp_, "temi")
    in_crescita, in_calo = [], []
    for t in temi:
        nc = kc[t["id"]]["video"] if t["id"] in kc else 0
        np_ = kp[t["id"]]["video"] if t["id"] in kp else 0
        if not nc and not np_:
            continue
        q, qp = quota(nc, uc_), quota(np_, up_)
        dq = round((q or 0) - (qp or 0), 3)
        riga = {"tema": t["id"], "nome": t["nome"], "video": nc, "video_prec": np_,
                "canali": sorted(kc[t["id"]]["canali"]) if t["id"] in kc else [],
                "quota": q, "quota_prec": qp, "delta_quota": dq}
        if nc >= 2 and nc > np_ and dq >= 0.10:
            in_crescita.append(riga)
        elif np_ >= 2 and nc < np_ and dq <= -0.10:
            in_calo.append(riga)
    in_crescita.sort(key=lambda r: (-r["delta_quota"], -r["video"]))
    in_calo.sort(key=lambda r: (r["delta_quota"], -r["video_prec"]))
    for r in totale:
        r["delta_quota"] = round((r["quota"] or 0) - (r["quota_prec"] or 0), 3)

    per_canale = {}
    for info in stato_canali:
        vc = [v for v in corr if v["channel_id"] == info["channel_id"]]
        vp = [v for v in prec if v["channel_id"] == info["channel_id"]]
        cc, cp = conta_temi(vc, "temi"), conta_temi(vp, "temi")
        righe = [{"tema": k, "nome": nomi_temi[k], "video": cc[k]["video"] if k in cc else 0,
                  "video_prec": cp[k]["video"] if k in cp else 0}
                 for k in set(cc) | set(cp)]
        righe.sort(key=lambda r: (-r["video"], -r["video_prec"], r["nome"]))
        per_canale[info["nome"]] = {
            "video": len(vc), "video_prec": len(vp),
            "video_senza_temi": sum(1 for v in vc if not v["temi"]),
            "copre_settimana_precedente": info["copre_settimana_precedente"],
            "temi": righe[:8],
        }

    asset_sett = []
    for a in asset:
        c, p = ac.get(a["id"]), ap.get(a["id"])
        if not c and not p:
            continue
        sc = scheda_serie(serie_prezzi[a["serie"]]) if a.get("serie") in serie_prezzi else None
        asset_sett.append({
            "asset": a["id"], "nome": a["nome"],
            "video": c["video"] if c else 0, "video_prec": p["video"] if p else 0,
            "canali": sorted(c["canali"]) if c else [],
            "serie": a.get("serie") if sc else None,
            "var_1s": sc["var_1s"] if sc else None, "var_1m": sc["var_1m"] if sc else None,
            "unita_var": sc["unita_var"] if sc else None,
            "esempi": scegli_esempi(c["esempi"], 2) if c else [],
        })
    asset_sett.sort(key=lambda r: (-r["video"], -r["video_prec"], r["nome"]))

    # collegamenti tema -> serie di prezzi
    collegamenti = []
    righe_totale = {r["tema"]: r for r in totale}
    for t in temi:
        schede, mancanti_id = [], []
        for sid in t.get("serie", []):
            if sid in serie_prezzi:
                sc = scheda_serie(serie_prezzi[sid])
                if sc:
                    schede.append(sc)
            else:
                mancanti_id.append(sid)
        if mancanti_id:
            avviso("tema %s: serie non trovate in prezzi.json: %s" % (t["id"], ", ".join(mancanti_id)))
        r = righe_totale.get(t["id"], {})
        nv, npv = r.get("video", 0), r.get("video_prec", 0)
        prime = [frase_serie(s) for s in schede[:3]]
        riga = "%s: %d video in 7 giorni (%d nei 7 prima)" % (t["nome"], nv, npv)
        riga += (" · " + "; ".join(prime)) if prime else " · nessuna serie di prezzi collegata"
        collegamenti.append({
            "tema": t["id"], "nome": t["nome"], "video": nv, "video_prec": npv,
            "in_crescita": any(x["tema"] == t["id"] for x in in_crescita),
            "serie": schede, "serie_mancanti": t.get("serie_mancanti", []),
            "riga": riga,
        })
    collegamenti.sort(key=lambda c: (-c["video"], -c["video_prec"], c["nome"]))

    for el in elementi:  # nomi leggibili accanto agli id
        for t in el["temi"]:
            t["nome"] = nomi_temi.get(t["id"], t["id"])
        for a in el["asset"]:
            a["nome"] = nomi_asset.get(a["id"], a["id"])

    fonti.append({"nome": "Prezzi dell'osservatorio (docs/data/prezzi.json)", "link": "data/prezzi.json",
                  "licenza": "vedi prezzi.json (Yahoo Finance, U.S. Treasury)",
                  "data_dato": (prezzi.get("aggiornato") or "")[:10]})

    uscita = {
        "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": fonti,
        "nota": ("Di cosa parlano alcuni analisti italiani su YouTube, accanto a cosa fanno i prezzi. "
                 "Elementi = video (ultimi %d per canale dal feed RSS, piu' l'archivio delle esecuzioni precedenti, %d giorni). "
                 "Temi e asset ricavati con parole chiave (raccolta/analisti/temi.json) SOLO da titolo e descrizione: "
                 "il parlato non e' letto. Sono opinioni degli autori, non fatti. Settimane = finestre mobili di 7 giorni "
                 "(ora di Roma). 'quota' = parte dei video con almeno un tema riconosciuto. Variazioni dei prezzi calcolate "
                 "dalle serie di prezzi.json (1 settimana = ultimo valore contro l'ultimo valore di almeno 7 giorni prima; "
                 "1 mese = stesso giorno del mese prima); per i tassi in punti base. Si salvano solo titolo, breve "
                 "descrizione ripulita da link e avvertenze, e link al video." % (MAX_VIDEO, GIORNI_ARCHIVIO)),
        "firma_dizionario": firma_diz,
        "canali": stato_canali,
        "elementi": elementi,
        "temi_settimana": {
            "finestra_corrente": {"dal": corr_dal.isoformat(), "al": corr_al.isoformat(),
                                  "video": len(corr), "video_con_temi": len(utili_c)},
            "finestra_precedente": {"dal": prec_dal.isoformat(), "al": prec_al.isoformat(),
                                    "video": len(prec), "video_con_temi": len(utili_p)},
            "copertura_incompleta": [i["nome"] for i in stato_canali if not i.get("copre_settimana_precedente")],
            "totale": totale,
            "in_crescita": in_crescita,
            "in_calo": in_calo,
            "per_canale": per_canale,
            "asset": asset_sett,
        },
        "collegamenti_prezzi": collegamenti,
        "errori": ERRORI,
    }
    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    tmp = USCITA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(uscita, f, ensure_ascii=False, indent=1)
    os.replace(tmp, USCITA)

    print("Video: %d (nuovi dal feed %d). Finestra %s–%s: %d video, %d con temi." %
          (len(elementi), len(nuovi), corr_dal, corr_al, len(corr), len(utili_c)))
    for r in totale[:10]:
        print("  %-38s %2d (prima %2d) canali %d" % (r["nome"], r["video"], r["video_prec"], len(r["canali"])))
    print("In crescita:", ", ".join(r["nome"] for r in in_crescita) or "-")
    if ERRORI:
        print("Errori:", len(ERRORI))
    # fallisce solo se nessun canale ha risposto
    return 0 if nuovi else 1


if __name__ == "__main__":
    sys.exit(main())
