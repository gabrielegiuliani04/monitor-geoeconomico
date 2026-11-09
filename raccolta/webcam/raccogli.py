#!/usr/bin/env python3
"""Webcam pubbliche su punti di interesse geoeconomico: controllo dei link.

Legge l'elenco curato a mano in raccolta/webcam/webcam.json e, per ogni voce,
controlla che il link risponda davvero e che la pagina sia quella giusta:

  - pagine web: HTTP 200 e un frammento atteso nel <title> (le pagine
    "non trovato" servite con codice 200 vengono segnate come rotte);
    per SkylineWebcams si controlla anche la scritta OFFLINE;
  - YouTube: endpoint pubblico oEmbed (niente chiave); il canale deve
    corrispondere a quello atteso (verifica dell'editore).

Produce docs/data/webcam.json (formato AGENTI.md) con, per ogni webcam,
stato = attiva | offline | rotta | non_raggiungibile, la data dell'ultimo
controllo riuscito e il numero di controlli falliti di seguito.
Pensato per girare una volta alla settimana; non fallisce mai per un link rotto.

Regole etiche (vedi report/agenti/webcam.md): solo webcam pubblicate
intenzionalmente dal proprietario; nessun IP diretto, nessun elenco tipo
Insecam/Shodan, nessun incorporamento del video: solo link alla pagina.

Uso:  python3 raccolta/webcam/raccogli.py   (dalla radice del repository)
Solo libreria standard.
"""
import concurrent.futures as cf
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
IN_CURATE = os.path.join(QUI, "webcam.json")
OUT = os.path.join(RADICE, "docs", "data", "webcam.json")

# User-Agent onesto: niente finti browser. I siti che rifiutano i client
# automatici restano "non_raggiungibile" e vanno controllati a mano.
UA = "monitor-geoeconomico/1.0 (osservatorio OSINT non commerciale; controllo settimanale dei link)"
TIMEOUT = 30
MAX_BYTE = 600_000
SOFT404 = re.compile(r"page not found|pagina non trovata|seite nicht gefunden|404 not found|\b404\b",
                     re.I)


def ora():
    return datetime.now(timezone.utc)


def scarica(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en,it;q=0.8"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.status, r.geturl(), r.read(MAX_BYTE).decode("utf-8", "ignore")


def id_youtube(url):
    p = urllib.parse.urlparse(url)
    if p.netloc.endswith("youtu.be"):
        return p.path.strip("/") or None
    if "youtube.com" in p.netloc:
        q = urllib.parse.parse_qs(p.query).get("v")
        if q:
            return q[0]
        m = re.search(r"/(?:embed|live)/([A-Za-z0-9_-]{11})", p.path)
        if m:
            return m.group(1)
    return None


def controlla(voce):
    """Ritorna (stato, http, dettaglio)."""
    url = voce["link"]
    atteso = (voce.get("atteso") or "").lower()
    vid = id_youtube(url)
    try:
        if vid:
            o = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(
                "https://www.youtube.com/watch?v=" + vid, safe="")
            code, _, testo = scarica(o)
            d = json.loads(testo)
            canale = d.get("author_name", "")
            if atteso and atteso not in (canale + " " + d.get("title", "")).lower():
                return "rotta", code, f"canale inatteso: {canale}"
            return "attiva", code, f"YouTube: {d.get('title','')[:80]} | canale {canale}"
        code, finale, testo = scarica(url)
        m = re.search(r"<title[^>]*>(.*?)</title>", testo, re.S | re.I)
        titolo = html.unescape(m.group(1)).strip() if m else ""
        if code != 200:
            return "rotta", code, f"HTTP {code}"
        if titolo and SOFT404.search(titolo):
            return "rotta", code, f"pagina 'non trovata' servita con 200: {titolo[:80]}"
        if atteso and atteso not in titolo.lower():
            return "rotta", code, f"titolo inatteso: {titolo[:80]}"
        if "skylinewebcams.com" in url and re.search(r">\s*OFFLINE\s*<|['\"]OFFLINE['\"]", testo):
            return "offline", code, "SkylineWebcams segnala la webcam OFFLINE"
        return "attiva", code, titolo[:100]
    except urllib.error.HTTPError as e:
        stato = "non_raggiungibile" if e.code in (401, 403, 429, 503) else "rotta"
        return stato, e.code, f"HTTP {e.code}"
    except Exception as e:  # rete, TLS, timeout, connessione chiusa
        return "non_raggiungibile", None, f"{type(e).__name__}: {str(e)[:100]}"


def carica_precedente():
    try:
        with open(OUT, encoding="utf-8") as f:
            return {e.get("id"): e for e in json.load(f).get("elementi", [])}
    except Exception:
        return {}


def main():
    with open(IN_CURATE, encoding="utf-8") as f:
        curate = json.load(f)
    voci = [v for v in curate["elementi"] if v.get("attivo", True)]
    prima = carica_precedente()
    adesso = ora()
    oggi = adesso.strftime("%Y-%m-%d")

    with cf.ThreadPoolExecutor(6) as ex:
        esiti = list(ex.map(controlla, voci))

    elementi, errori = [], []
    for v, (stato, code, dett) in zip(voci, esiti):
        old = prima.get(v["id"], {})
        ok = stato == "attiva"
        falliti = 0 if ok else int(old.get("controlli_falliti", 0)) + 1
        e = {
            "id": v["id"],
            "nome": v["nome"],
            "lat": round(float(v["lat"]), 4),
            "lon": round(float(v["lon"]), 4),
            "paese": v["paese"],
            "categoria": v["categoria"],
            "stato": stato,
            "inquadra": v["inquadra"],
            "proprietario": v["proprietario"],
            "fonte": v["proprietario"],
            "link": v["link"],
            "pagina": v.get("pagina", v["link"]),
            "tipo": v["tipo"],
            "lingua": v["lingua"],
            "verificato_il": oggi if ok else old.get("verificato_il"),
            "ultimo_controllo": oggi,
            "esito_controllo": dett,
            "http": code,
            "controlli_falliti": falliti,
            "data_fonte": oggi,
            "affidabilita": v.get("affidabilita", "media"),
            "note": v.get("note", ""),
        }
        elementi.append(e)
        if not ok:
            errori.append(f"{v['id']}: {stato} ({dett})")

    conta = {}
    for e in elementi:
        conta[e["stato"]] = conta.get(e["stato"], 0) + 1
    out = {
        "aggiornato": adesso.strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": [
            {"nome": "Elenco curato a mano (raccolta/webcam/webcam.json)", "link": "",
             "licenza": "solo link: le immagini restano dei rispettivi proprietari", "data_dato": oggi},
            {"nome": "Port of Rotterdam, mappa webcam (ArcGIS Webcams_v2)",
             "link": "https://www.portofrotterdam.com/en/experience-online/webcams",
             "licenza": "link pubblici del porto", "data_dato": oggi},
            {"nome": "YouTube oEmbed (verifica canale e disponibilità)", "link": "https://www.youtube.com/oembed",
             "licenza": "endpoint pubblico", "data_dato": oggi},
        ],
        "nota": ("Webcam pubbliche e ufficiali (o di reti che ritrasmettono feed autorizzati) su stretti, canali, "
                 "porti, ponti ed energia. Solo link alla pagina del proprietario, nessun video incorporato. "
                 "lat/lon = punto inquadrato, stimato. stato: attiva | offline | rotta | non_raggiungibile "
                 "(il sito rifiuta o chiude la connessione dall'ambiente di raccolta: verificare da browser). "
                 f"Conteggio: {json.dumps(conta, ensure_ascii=False)}."),
        "elementi": elementi,
        "errori": errori,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"webcam: {len(elementi)} voci, {conta}", file=sys.stderr)
    for r in errori:
        print("  ! " + r, file=sys.stderr)


if __name__ == "__main__":
    main()
