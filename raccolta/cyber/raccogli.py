#!/usr/bin/env python3
"""Rischio cyber per energia ed eolico: incidenti, allarmi, esposizione, regole.

Taglio DIFENSIVO e di analisi del rischio. Le voci sono curate a mano in
raccolta/cyber/incidenti.json (una fonte per voce); questo script:
  1. valida il file (campi obbligatori, coordinate, date, categorie, affidabilita,
     link, assenza di dettagli sensibili come indirizzi IP o credenziali);
  2. se esiste docs/data/offshore-nord.json (prodotto da un altro agente, solo
     lettura) ne riassume la capacita offshore per paese nella sezione esposizione;
  3. scrive docs/data/cyber-energia.json nello schema comune del progetto.

Non scarica nulla da Internet e non interroga motori di ricerca di dispositivi.
Uso:  python3 raccolta/cyber/raccogli.py   (dalla radice o da qualsiasi cartella)
Esce con codice 1 se la validazione trova errori bloccanti.
Solo libreria standard.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
IN_VOCI = os.path.join(QUI, "incidenti.json")
IN_OFFSHORE = os.path.join(RADICE, "docs", "data", "offshore-nord.json")
OUT = os.path.join(RADICE, "docs", "data", "cyber-energia.json")

OBBLIGATORI = ["id", "nome", "data_evento", "paese", "lat", "lon", "precisione_km", "categoria",
               "settore", "vittima", "effetto", "attore", "attribuzione_stato", "fonte", "link",
               "data_fonte", "affidabilita"]
AFFIDABILITA = {"alta", "media", "bassa"}
RE_DATA = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
RE_ISO2 = re.compile(r"^[A-Z]{2}$")
# Contenuti da NON pubblicare (regola del dominio): indirizzi IP, credenziali, riferimenti a motori di scansione.
RE_SENSIBILE = [
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "indirizzo IP"),
    (re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]"), "credenziale"),
    (re.compile(r"(?i)\b(shodan|censys|zoomeye|fofa)\b"), "motore di scansione di dispositivi"),
    (re.compile(r"(?i)\bCVE-\d{4}-\d+"), "identificativo di vulnerabilita (tenere il livello alto)"),
]


def ora():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def controlla_testo(oggetto, dove, errori):
    testo = json.dumps(oggetto, ensure_ascii=False)
    for regex, cosa in RE_SENSIBILE:
        m = regex.search(testo)
        if m:
            errori.append(f"{dove}: contiene un possibile {cosa} ('{m.group(0)}')")


def valida_incidente(e, categorie, visti, errori, avvisi):
    dove = f"incidente {e.get('id', '?')}"
    for k in OBBLIGATORI:
        if k not in e or e[k] in (None, ""):
            errori.append(f"{dove}: manca il campo '{k}'")
    if e.get("id") in visti:
        errori.append(f"{dove}: id duplicato")
    visti.add(e.get("id"))
    lat, lon = e.get("lat"), e.get("lon")
    if not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
        errori.append(f"{dove}: lat non valida")
    if not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
        errori.append(f"{dove}: lon non valida")
    for k in ("data_evento", "data_fonte"):
        v = str(e.get(k, ""))
        if not RE_DATA.match(v):
            errori.append(f"{dove}: {k} non e' AAAA-MM-GG")
    if str(e.get("data_fonte", "")) < str(e.get("data_evento", ""))[:len(str(e.get("data_fonte", "")))]:
        avvisi.append(f"{dove}: data_fonte precedente a data_evento")
    if not RE_ISO2.match(str(e.get("paese", ""))):
        errori.append(f"{dove}: paese non e' ISO a 2 lettere")
    if e.get("categoria") not in categorie:
        errori.append(f"{dove}: categoria '{e.get('categoria')}' non definita")
    if e.get("affidabilita") not in AFFIDABILITA:
        errori.append(f"{dove}: affidabilita deve essere alta/media/bassa")
    if not str(e.get("link", "")).startswith("https://"):
        errori.append(f"{dove}: link non https")
    if (e.get("precisione_km") or 0) > 1000:
        avvisi.append(f"{dove}: punto solo simbolico (precisione {e.get('precisione_km')} km)")


def riassumi_offshore(avvisi):
    """Legge (senza modificarlo) il file dell'agente offshore, se c'e'."""
    if not os.path.exists(IN_OFFSHORE):
        avvisi.append("docs/data/offshore-nord.json non presente: uso le concentrazioni curate a mano")
        return None
    try:
        with open(IN_OFFSHORE, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError) as exc:
        avvisi.append(f"offshore-nord.json illeggibile: {exc}")
        return None
    per_paese = {}
    for el in d.get("elementi", []):
        if not isinstance(el, dict):
            continue
        mw = None
        for k in ("mw", "capacita_mw", "potenza_mw", "capacity_mw"):
            if isinstance(el.get(k), (int, float)):
                mw = float(el[k])
                break
        p = el.get("paese") or "??"
        stato = str(el.get("stato", "")).lower()
        r = per_paese.setdefault(p, {"parchi": 0, "mw_totali": 0.0, "mw_in_esercizio": 0.0})
        r["parchi"] += 1
        if mw:
            r["mw_totali"] += mw
            if any(s in stato for s in ("eserciz", "operat", "attivo", "online")):
                r["mw_in_esercizio"] += mw
    for r in per_paese.values():
        r["mw_totali"] = round(r["mw_totali"])
        r["mw_in_esercizio"] = round(r["mw_in_esercizio"])
    return {"fonte": "docs/data/offshore-nord.json", "aggiornato": d.get("aggiornato"),
            "per_paese": dict(sorted(per_paese.items()))}


def main():
    errori, avvisi = [], []
    with open(IN_VOCI, encoding="utf-8") as f:
        voci = json.load(f)
    categorie = voci.get("categorie", {})
    visti = set()
    incidenti = voci.get("incidenti", [])
    for e in incidenti:
        valida_incidente(e, categorie, visti, errori, avvisi)
    controlla_testo(voci, "incidenti.json", errori)

    esp = voci.get("esposizione", {})
    for p in esp.get("paesi", []):
        if not RE_ISO2.match(str(p.get("paese", ""))):
            errori.append(f"esposizione paese {p}: codice non valido")
        for k in ("eolico_mw", "eolico_offshore_mw", "solare_mw"):
            v = p.get(k)
            if v is not None and (not isinstance(v, (int, float)) or v < 0):
                errori.append(f"esposizione {p.get('paese')}: {k} non numerico")
    for c in esp.get("concentrazioni_offshore", []):
        if not (-90 <= c.get("lat", 999) <= 90 and -180 <= c.get("lon", 999) <= 180):
            errori.append(f"concentrazione {c.get('nome')}: coordinate non valide")
    for t in esp.get("tecnologie", []):
        for pid in t.get("precedenti", []):
            if pid not in visti:
                errori.append(f"tecnologia '{t.get('tecnologia')}': precedente {pid} inesistente")

    if errori:
        for e in errori:
            print("ERRORE:", e, file=sys.stderr)
        sys.exit(1)

    # Punti nello schema comune (campi base + extra del dominio).
    elementi = []
    for e in sorted(incidenti, key=lambda x: x["data_evento"], reverse=True):
        p = dict(e)
        p["stato"] = "avvenuto" if "sventato" not in e["effetto"] else "sventato"
        p["note"] = e.get("lezione", "")
        p["tipo"] = "incidente"
        elementi.append(p)
    for c in esp.get("concentrazioni_offshore", []):
        elementi.append({
            "id": "OFF-" + re.sub(r"[^A-Za-z0-9]+", "-", c["nome"]).strip("-").upper(),
            "tipo": "concentrazione_offshore", "nome": c["nome"], "paese": c["paese"],
            "lat": c["lat"], "lon": c["lon"], "categoria": "concentrazione-capacita",
            "stato": c.get("stato", ""), "mw": c.get("mw"),
            "fonte": "curato a mano (capacita arrotondate); prevale offshore-nord.json se presente",
            "link": "https://windeurope.org/", "data_fonte": voci.get("versione"),
            "affidabilita": "media",
            "note": (c.get("nota", "") + " Solo concentrazione di capacita: nessuna indicazione di vulnerabilita.").strip()})

    off = riassumi_offshore(avvisi)
    if off:
        esp = dict(esp)
        esp["offshore_da_agente"] = off

    conteggio = {}
    for e in incidenti:
        conteggio[e["categoria"]] = conteggio.get(e["categoria"], 0) + 1

    fonte_eol = esp.get("fonte_eolico", {})
    uscita = {
        "aggiornato": ora(),
        "fonti": [
            {"nome": "Voci curate a mano dall'agente CYBER-ENERGIA (una fonte per voce)",
             "link": "raccolta/cyber/incidenti.json", "licenza": "fatti con citazione delle fonti",
             "data_dato": voci.get("versione")},
            {"nome": fonte_eol.get("nome", "WindEurope"), "link": fonte_eol.get("link", ""),
             "licenza": "dati citati con fonte (report pubblico WindEurope)",
             "data_dato": fonte_eol.get("data_dato", "")},
            {"nome": "CERT Polska, CISA, SektorCERT, FE-DDIS, ESET, Mandiant, SentinelOne, Forescout (rapporti pubblici)",
             "link": "https://cert.pl/en/posts/2026/01/incident-report-energy-sector-2025/",
             "licenza": "fatti con citazione", "data_dato": "2016-2026"},
        ],
        "nota": voci.get("nota", "") + " Taglio difensivo: niente dettagli sfruttabili. Gli elementi di tipo "
                "'concentrazione_offshore' indicano solo dove si concentra la capacita.",
        "categorie": categorie,
        "conteggio_categorie": conteggio,
        "elementi": elementi,
        "candidati_frigoriferi": voci.get("candidati_frigoriferi", []),
        "allarmi_agenzie": voci.get("allarmi_agenzie", []),
        "esposizione": esp,
        "regole": voci.get("regole", []),
        "buone_pratiche": voci.get("buone_pratiche", []),
        "errori": [],
        "avvisi": avvisi,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(uscita, f, ensure_ascii=False, indent=1)
    print(f"Scritto {OUT}: {len(incidenti)} incidenti, "
          f"{len(esp.get('concentrazioni_offshore', []))} concentrazioni offshore, "
          f"{len(esp.get('paesi', []))} paesi; avvisi: {len(avvisi)}")
    for a in avvisi:
        print("avviso:", a)


if __name__ == "__main__":
    main()
