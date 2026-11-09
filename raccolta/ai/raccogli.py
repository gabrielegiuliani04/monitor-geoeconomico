#!/usr/bin/env python3
"""Infrastrutture AI nel mondo e direzione degli investimenti.

Produce:
  docs/data/ai-mondo.json       punti: data-center-ai, fab-chip, supercalcolo
                                + quote di calcolo AI per paese (Epoch AI)
  docs/data/investimenti.json   flussi di capitale "da -> a" + riepilogo + capex 2026

Fonti automatiche (scaricate a ogni esecuzione):
  - Epoch AI, "AI data centers" (CC BY 4.0): data_centers.zip
      https://epoch.ai/data/data_centers/data_centers.zip
    -> data center fuori dagli USA (gli USA sono già in docs/data/ai.json)
  - Epoch AI, "AI chip imports" (CC BY 4.0): ai_chip_trade.zip
      https://epoch.ai/data/ai_chip_trade/ai_chip_trade.zip
    -> quote di calcolo AI (equivalenti H100) per paese
  - TOP500 (lista più recente, pagina pubblica): primi 20 sistemi
      https://www.top500.org/lists/top500/list/AAAA/MM/

Voci curate a mano (stessa cartella):
  - punti_curati.json     data center fuori dal tracker Epoch e fabbriche di chip
  - epoch_coordinate.json coordinate dei siti Epoch (Epoch dà indirizzi, non coordinate)
  - top500_siti.json      coordinate dei siti TOP500, centroidi e codici ISO
  - flussi.json           flussi di investimento e capex 2026

Se una fonte automatica non risponde, lo script riusa le voci dell'esecuzione
precedente (lette dal file di uscita) e lo scrive in "errori", senza fallire.

Uso (dalla radice del repository):
  python3 raccolta/ai/raccogli.py             scarica, unisce, valida, scrive
  python3 raccolta/ai/raccogli.py --valida    valida solo i due file già scritti
Solo libreria standard di Python 3.
"""
import csv
import io
import json
import os
import re
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
DATI = os.path.join(RADICE, "docs", "data")
OUT_MONDO = os.path.join(DATI, "ai-mondo.json")
OUT_INV = os.path.join(DATI, "investimenti.json")
AI_USA = os.path.join(DATI, "ai.json")  # sola lettura: punti USA del dossier

URL_EPOCH_DC = "https://epoch.ai/data/data_centers/data_centers.zip"
URL_EPOCH_TRADE = "https://epoch.ai/data/ai_chip_trade/ai_chip_trade.zip"
URL_TOP500 = "https://www.top500.org/lists/top500/list/{a}/{m:02d}/"
PAGINA_EPOCH_DC = "https://epoch.ai/data/ai-data-centers"
PAGINA_EPOCH_TRADE = "https://epoch.ai/data/ai-chip-imports"
UA = {"User-Agent": "Mozilla/5.0 (monitor-geoeconomico OSINT, uso personale non commerciale)"}

# Cambi fissi indicativi (USD per 1 unità), usati solo se la fonte non dà l'equivalente in USD.
# Valori arrotondati sulla media 2025: NON sono il cambio del giorno dell'annuncio.
CAMBI = {"USD": 1.0, "EUR": 1.10, "GBP": 1.30, "JPY": 1 / 150, "KRW": 1 / 1400, "INR": 1 / 88,
         "BRL": 0.18, "SEK": 0.10, "CNY": 0.14}

CATEGORIE = {"data-center-ai", "fab-chip", "supercalcolo"}
STATI_PUNTI = {"operativo", "operativo-parziale", "in-costruzione", "annunciato", "sospeso", "cancellato"}
STATI_FLUSSI = {"annunciato", "in corso", "completato", "sospeso", "cancellato"}
SETTORI = {"data center", "chip", "energia per AI", "fondo"}
AFFIDABILITA = {"alta", "media", "bassa"}
RE_DATA = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
RE_PAESE = re.compile(r"^[A-Z]{2}(\+[A-Z]{2})*$")

ADESSO = datetime.now(timezone.utc)
OGGI = ADESSO.strftime("%Y-%m-%d")


# ----------------------------------------------------------------- utilità
def leggi_json(percorso, predefinito=None):
    try:
        with open(percorso, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return predefinito


def scrivi_json(percorso, dato):
    tmp = percorso + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dato, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(tmp, percorso)


def scarica(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def slug(testo):
    return re.sub(r"[^A-Z0-9]+", "-", testo.upper()).strip("-")


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def tondo(v, n=1):
    return None if v is None else round(v, n)


def pulisci_tag(testo):
    """Epoch aggiunge '#confident', '#likely', '#speculative' ai nomi: li sposto in una nota."""
    if not testo:
        return "", ""
    nomi, tag = [], []
    for parte in testo.split(","):
        parte = parte.strip()
        m = re.match(r"^(.*?)\s*#(\w+)$", parte)
        if m:
            nomi.append(m.group(1).strip())
            tag.append(f"{m.group(1).strip()}: {m.group(2)}")
        elif parte:
            nomi.append(parte)
    return ", ".join(nomi), "; ".join(tag)


def in_usd(importo, valuta, usd_fonte=None):
    """Restituisce (usd_mld, metodo)."""
    if usd_fonte is not None:
        return round(float(usd_fonte), 2), "equivalente dato dalla fonte"
    if importo is None or valuta is None:
        return None, "importo non dichiarato"
    if valuta not in CAMBI:
        return None, f"valuta {valuta} senza cambio"
    if valuta == "USD":
        return round(float(importo), 2), "USD dalla fonte"
    return round(float(importo) * CAMBI[valuta], 2), f"convertito con cambio fisso indicativo {valuta}={CAMBI[valuta]:.5g} USD"


# ----------------------------------------------------------------- Epoch: data center
def epoch_data_center(coord, iso, errori):
    """Data center fuori dagli USA dal tracker Epoch. Restituisce (punti, data_dato) o (None, None)."""
    try:
        z = zipfile.ZipFile(io.BytesIO(scarica(URL_EPOCH_DC)))
        dc = list(csv.DictReader(io.TextIOWrapper(z.open("data_centers.csv"), encoding="utf-8")))
        tl = list(csv.DictReader(io.TextIOWrapper(z.open("data_center_timelines.csv"), encoding="utf-8")))
    except Exception as e:  # rete, zip, csv
        errori.append(f"Epoch AI data center: download non riuscito ({e}); riuso le voci precedenti")
        return None, None
    tempi = {}
    for r in tl:
        tempi.setdefault(r.get("Data center", ""), []).append(r)
    punti, usa = [], 0
    for r in dc:
        nome = (r.get("Name") or "").strip()
        paese_nome = (r.get("Country") or "").strip()
        if not nome:
            continue
        if paese_nome == "United States":
            usa += 1
            continue
        c = coord.get(nome)
        if not c:
            errori.append(f"Epoch AI: sito nuovo senza coordinate, non in mappa: '{nome}' ({paese_nome}). "
                          "Aggiungerlo a raccolta/ai/epoch_coordinate.json")
            continue
        righe = sorted(tempi.get(nome, []), key=lambda t: t.get("Date", ""))
        passate = [t for t in righe if t.get("Date", "") <= OGGI]
        mw_att = num(r.get("Current power (MW)")) or 0.0
        mw_max, data_max = mw_att, None
        for t in righe:
            v = num(t.get("IT power (MW)")) or 0.0
            if v > mw_max + 0.01:
                mw_max, data_max = v, t.get("Date")
        primo = next((t.get("Date") for t in righe if (num(t.get("IT power (MW)")) or 0) > 0), None)
        if mw_att <= 0:
            stato = "in-costruzione" if righe else "annunciato"
        elif mw_max > mw_att + 0.5:
            stato = "operativo-parziale"
        else:
            stato = "operativo"
        ultimo = passate[-1] if passate else (righe[-1] if righe else {})
        proprietario, tag_p = pulisci_tag(r.get("Owner", ""))
        utenti, tag_u = pulisci_tag(r.get("Users", ""))
        progetto, _ = pulisci_tag(r.get("Project", ""))
        investitori, _ = pulisci_tag(r.get("Investors", ""))
        costo = num(r.get("Current total capital cost (2025 USD billions)"))
        h100 = num(r.get("Current H100 equivalents"))
        stato_testo = re.sub(r"\s+", " ", (ultimo.get("Construction status") or "")).strip()
        stato_testo = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stato_testo)  # toglie i link markdown
        if len(stato_testo) > 320:
            stato_testo = stato_testo[:317].rstrip() + "..."
        note = []
        if c.get("note"):
            note.append(c["note"])
        if stato_testo:
            note.append(f"Ultima osservazione Epoch ({ultimo.get('Date', '?')}, in inglese): {stato_testo}")
        if tag_p or tag_u:
            note.append("Certezza Epoch su proprietario/utilizzatori: " + "; ".join(x for x in (tag_p, tag_u) if x))
        anno = int(primo[:4]) if primo else (int(data_max[:4]) if data_max else None)
        punti.append({
            "id": "EP-" + slug(nome),
            "categoria": "data-center-ai",
            "nome": nome,
            "paese": iso.get(paese_nome, ""),
            "luogo": (r.get("Address") or "").strip() or None,
            "lat": c["lat"], "lon": c["lon"],
            "origine_coord": "stimata: " + c.get("origine", ""),
            "precisione_km": c.get("precisione_km"),
            "mw": tondo(mw_att, 0),
            "mw_tipo": "potenza IT attuale (stima Epoch)",
            "mw_previsto": tondo(mw_max, 0) if data_max else None,
            "data_mw_previsto": data_max,
            "h100e": int(h100) if h100 else None,
            "proprietario": proprietario or None,
            "utilizzatori": utenti or None,
            "progetto": progetto or None,
            "investitori": investitori or None,
            "stato": stato,
            "anno": anno,
            "importo": None, "valuta": None,
            "costo_capitale_stimato_usd_mld": tondo(costo, 1) if costo else None,
            "fonte": "Epoch AI, AI data centers",
            "link": PAGINA_EPOCH_DC,
            "data_fonte": (ultimo.get("Date") or OGGI)[:10],
            "affidabilita": "alta" if mw_att > 0 else "media",
            "note": " ".join(note),
            "origine_dato": "epoch",
        })
    data_dato = OGGI
    return punti, {"siti_usa_esclusi": usa, "data_dato": data_dato}


# ----------------------------------------------------------------- Epoch: quote per paese
def epoch_quote(errori):
    try:
        z = zipfile.ZipFile(io.BytesIO(scarica(URL_EPOCH_TRADE)))
        righe = list(csv.DictReader(io.TextIOWrapper(z.open("by_country.csv"), encoding="utf-8")))
    except Exception as e:
        errori.append(f"Epoch AI quote per paese: download non riuscito ({e}); riuso il dato precedente")
        return None
    def chiave(q):
        a, t = q.split()
        return int(a), int(t[1])
    trimestri = sorted({r["Quarter"] for r in righe if r.get("Quarter")}, key=chiave)
    definitivi = [q for q in trimestri if any(r["Quarter"] == q and r.get("Provisional") == "No" for r in righe)]
    if not definitivi:
        errori.append("Epoch AI quote: nessun trimestre definitivo")
        return None
    def quote(q):
        rr = [r for r in righe if r["Quarter"] == q]
        tot_c = sum(num(r.get("Cumulative compute capacity (H100e)")) or 0 for r in rr)
        tot_q = sum(num(r.get("Quarterly compute capacity (H100e)")) or 0 for r in rr)
        out = []
        for r in rr:
            c = num(r.get("Cumulative compute capacity (H100e)")) or 0
            qv = num(r.get("Quarterly compute capacity (H100e)")) or 0
            out.append({"paese": r["Country"], "iso": r.get("Country code") or ("EU" if r["Country"] == "European Union" else ""),
                        "h100e_cumulati": int(c), "quota_cumulata_pct": round(100 * c / tot_c, 2) if tot_c else None,
                        "h100e_trimestre": int(qv), "quota_trimestre_pct": round(100 * qv / tot_q, 2) if tot_q else None,
                        "gw_chip_cumulati": tondo(num(r.get("Cumulative chip power (GW)")), 2)})
        out.sort(key=lambda x: -x["h100e_cumulati"])
        return out, tot_c, tot_q
    q = definitivi[-1]
    paesi, tot_c, tot_q = quote(q)
    principali = paesi[:20]
    altri_c = sum(p["h100e_cumulati"] for p in paesi[20:])
    serie = {}
    for qq in trimestri[-12:]:
        pp, tc, _ = quote(qq)
        serie[qq] = {p["iso"] or p["paese"]: p["quota_cumulata_pct"] for p in pp[:6]}
    return {
        "trimestre": q,
        "provvisorio": False,
        "ultimo_trimestre_disponibile": trimestri[-1],
        "totale_h100e_cumulati": int(tot_c),
        "totale_h100e_trimestre": int(tot_q),
        "paesi": principali,
        "altri_paesi_h100e_cumulati": int(altri_c),
        "serie_quote_cumulate_pct": serie,
        "fonte": "Epoch AI, Data on AI chip imports (CC BY 4.0)",
        "link": PAGINA_EPOCH_TRADE,
        "nota": "Quote del calcolo AI (equivalenti H100) arrivato in ciascun paese dal 2022, stimate da Epoch "
                "dalle statistiche doganali. L'Unione europea è un unico aggregato. Taiwan non compare come destinazione "
                "perché esporta. È un'indicazione, non un censimento: Epoch stima di coprire una parte del totale.",
    }


# ----------------------------------------------------------------- TOP500
def top500(siti, errori, quanti=20):
    anno = ADESSO.year
    tentativi = []
    for a, m in ((anno, 11), (anno, 6), (anno - 1, 11), (anno - 1, 6)):
        if (a, m) <= (ADESSO.year, ADESSO.month):
            tentativi.append((a, m))
    html_txt, lista = None, None
    for a, m in tentativi:
        try:
            t = scarica(URL_TOP500.format(a=a, m=m)).decode("utf-8", "replace")
        except Exception:
            continue
        if t.count("/system/") >= quanti:
            html_txt, lista = t, (a, m)
            break
    if not html_txt:
        errori.append("TOP500: nessuna lista scaricabile; riuso le voci precedenti")
        return None, None
    import html as H
    usa_ai = {p.get("nome", "").split(" (")[0].lower() for p in (leggi_json(AI_USA, {}) or {}).get("punti", [])
              if p.get("categoria") == "supercomputer"}
    centroidi, iso = siti.get("centroidi_paese", {}), siti.get("iso", {})
    punti = []
    for riga in re.findall(r"<tr>(.*?)</tr>", html_txt, re.S)[1:]:
        td = re.findall(r"<td[^>]*>(.*?)</td>", riga, re.S)
        if len(td) < 6:
            continue
        try:
            rango = int(re.sub(r"\D", "", td[0]))
        except ValueError:
            continue
        if rango > quanti:
            break
        m_sys = re.search(r'href="(/system/\d+)">\s*<b>(.*?)</b>\s*-\s*(.*?)</a>\s*(.*?)<br', td[1], re.S)
        m_site = re.search(r'href="/site/(\d+)">(.*?)</a>\s*<br>\s*(.*?)\s*$', td[1].strip(), re.S)
        if not m_sys or not m_site:
            errori.append(f"TOP500: riga {rango} non interpretabile")
            continue
        nome = H.unescape(m_sys.group(2)).strip()
        sistema = re.sub(r"\s+", " ", H.unescape(m_sys.group(3))).strip().rstrip(",")
        costruttore = re.sub(r"\s+", " ", H.unescape(m_sys.group(4))).strip()
        sito_id, sito_nome = m_site.group(1), H.unescape(m_site.group(2)).strip()
        paese_nome = H.unescape(re.sub(r"<[^>]+>", "", m_site.group(3))).strip()
        valori = [re.sub(r"[^\d.]", "", re.sub(r"<[^>]+>", "", v)) for v in td[2:6]]
        core, rmax, rpeak, kw = (num(v) for v in valori)
        s = siti.get("siti", {}).get(sito_id)
        if s:
            lat, lon, prec, orig, luogo = s["lat"], s["lon"], s["precisione_km"], s["origine"], s["luogo"]
        else:
            cc = centroidi.get(paese_nome)
            if not cc:
                errori.append(f"TOP500: sito {sito_id} ({sito_nome}, {paese_nome}) senza coordinate né centroide; escluso")
                continue
            lat, lon, prec, orig, luogo = cc[0], cc[1], 1000, "centroide-paese: sito nuovo non ancora localizzato", sito_nome
            errori.append(f"TOP500: sito nuovo {sito_id} ({sito_nome}) messo sul centroide del paese; "
                          "aggiungerlo a raccolta/ai/top500_siti.json")
        punti.append({
            "id": f"T500-{lista[0]}{lista[1]:02d}-{rango:02d}",
            "categoria": "supercalcolo",
            "nome": nome,
            "paese": iso.get(paese_nome, ""),
            "luogo": luogo,
            "lat": lat, "lon": lon,
            "origine_coord": orig if orig.startswith(("stimata", "centroide", "coordinate")) else "stimata: " + orig,
            "precisione_km": prec,
            "rango_top500": rango,
            "rmax_pflops": rmax, "rpeak_pflops": rpeak,
            "potenza_kw": kw, "core": int(core) if core else None,
            "mw": round(kw / 1000, 1) if kw else None,
            "mw_tipo": "potenza misurata durante il test Linpack (TOP500)" if kw else "non dichiarata alla TOP500",
            "sistema": sistema,
            "proprietario": sito_nome,
            "costruttore": costruttore or None,
            "stato": "operativo",
            "anno": None,
            "importo": None, "valuta": None,
            "fonte": f"TOP500, lista {lista[0]}-{lista[1]:02d}",
            "link": "https://www.top500.org" + m_sys.group(1),
            "data_fonte": f"{lista[0]}-{lista[1]:02d}",
            "affidabilita": "alta",
            "duplicato_ai_json": nome.lower() in usa_ai,
            "note": (f"{rmax / 1000:.3f} exaflop (Rmax)" if rmax else "")
                    + (". Già in ai.json (dossier USA): non disegnarlo due volte" if nome.lower() in usa_ai else ""),
            "origine_dato": "top500",
        })
    return punti, f"{lista[0]}-{lista[1]:02d}"


# ----------------------------------------------------------------- validazione
def valida_punto(p):
    e = []
    for k in ("id", "nome", "paese", "categoria", "lat", "lon", "stato", "fonte", "link", "data_fonte", "affidabilita"):
        if p.get(k) in (None, ""):
            e.append(f"manca {k}")
    lat, lon = p.get("lat"), p.get("lon")
    if not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
        e.append("lat non valida")
    if not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
        e.append("lon non valida")
    if p.get("categoria") not in CATEGORIE:
        e.append(f"categoria '{p.get('categoria')}' non ammessa")
    if p.get("stato") not in STATI_PUNTI:
        e.append(f"stato '{p.get('stato')}' non ammesso")
    if p.get("affidabilita") not in AFFIDABILITA:
        e.append("affidabilita non ammessa")
    if p.get("paese") and not RE_PAESE.match(p["paese"]):
        e.append("paese non ISO a 2 lettere")
    d = p.get("data_fonte")
    if d and (not RE_DATA.match(str(d)) or str(d) > OGGI):
        e.append(f"data_fonte '{d}' non valida o futura")
    a = p.get("anno")
    if a is not None and not (isinstance(a, int) and 2000 <= a <= 2040):
        e.append("anno non valido")
    if p.get("link") and not str(p["link"]).startswith("https://"):
        e.append("link non https")
    if p.get("precisione_km") is None:
        e.append("manca precisione_km")
    for f in p.get("fonti") or []:
        if f.get("data_fonte") and (not RE_DATA.match(str(f["data_fonte"])) or str(f["data_fonte"]) > OGGI):
            e.append(f"data di una fonte secondaria non valida: {f.get('data_fonte')}")
    return e


def valida_flusso(f):
    e = []
    for k in ("id", "attore", "da_paese", "a_paese", "da_lat", "da_lon", "a_lat", "a_lon", "anno", "settore",
              "stato", "fonte", "link", "data_fonte", "affidabilita"):
        if f.get(k) in (None, ""):
            e.append(f"manca {k}")
    for k in ("da_lat", "a_lat"):
        if not isinstance(f.get(k), (int, float)) or not -90 <= f[k] <= 90:
            e.append(f"{k} non valida")
    for k in ("da_lon", "a_lon"):
        if not isinstance(f.get(k), (int, float)) or not -180 <= f[k] <= 180:
            e.append(f"{k} non valida")
    for k in ("da_paese", "a_paese"):
        if f.get(k) and not RE_PAESE.match(f[k]) and f[k] != "EU":
            e.append(f"{k} '{f[k]}' non ISO")
    if f.get("settore") not in SETTORI:
        e.append(f"settore '{f.get('settore')}' non ammesso")
    if f.get("stato") not in STATI_FLUSSI:
        e.append(f"stato '{f.get('stato')}' non ammesso")
    if f.get("affidabilita") not in AFFIDABILITA:
        e.append("affidabilita non ammessa")
    d = f.get("data_fonte")
    if d and (not RE_DATA.match(str(d)) or str(d) > OGGI):
        e.append(f"data_fonte '{d}' non valida o futura")
    if not isinstance(f.get("anno"), int) or not 2015 <= f["anno"] <= 2030:
        e.append("anno non valido")
    if f.get("importo") is not None and (not isinstance(f["importo"], (int, float)) or f["importo"] <= 0):
        e.append("importo non positivo")
    if f.get("importo") is not None and f.get("valuta") not in CAMBI:
        e.append(f"valuta '{f.get('valuta')}' senza cambio")
    if f.get("link") and not str(f["link"]).startswith("https://"):
        e.append("link non https")
    return e


def filtra(voci, funzione, errori, etichetta):
    buone = []
    for v in voci:
        e = funzione(v)
        if e:
            gravi = [x for x in e if x.startswith(("manca lat", "manca lon", "lat ", "lon ", "da_l", "a_l", "manca da_l", "manca a_l"))]
            errori.append(f"{etichetta} {v.get('id', '?')}: " + "; ".join(e) + (" -> escluso" if gravi else ""))
            if gravi:
                continue
        buone.append(v)
    return buone


# ----------------------------------------------------------------- investimenti
def costruisci_flussi(fl, indice_punti, errori):
    luoghi = fl.get("luoghi", {})
    out = []
    for f in fl.get("flussi", []):
        g = dict(f)
        da = luoghi.get(f.get("da_luogo"))
        if da:
            g["da_lat"], g["da_lon"] = da
        else:
            errori.append(f"flusso {f.get('id')}: luogo di partenza '{f.get('da_luogo')}' non in tabella")
        if f.get("a_rif"):
            p = indice_punti.get(f["a_rif"])
            if p:
                g["a_lat"], g["a_lon"] = p["lat"], p["lon"]
                g["a_luogo"] = p["nome"]
            else:
                errori.append(f"flusso {f.get('id')}: punto di arrivo '{f['a_rif']}' non trovato")
        else:
            a = luoghi.get(f.get("a_luogo"))
            if a:
                g["a_lat"], g["a_lon"] = a
            else:
                errori.append(f"flusso {f.get('id')}: luogo di arrivo '{f.get('a_luogo')}' non in tabella")
        g["importo_usd_mld"], g["metodo_usd"] = in_usd(f.get("importo"), f.get("valuta"), f.get("importo_usd_mld"))
        g["importo_originale"] = (f"{f['importo']:g} mld {f['valuta']}" if f.get("importo") is not None else None)
        g["quadro"] = bool(f.get("quadro"))
        out.append(g)
    return out


def riepilogo(flussi):
    def somma(gruppo, chiave):
        tab = {}
        for f in gruppo:
            k = f.get(chiave) or "?"
            t = tab.setdefault(k, {"usd_mld": 0.0, "voci": 0, "voci_senza_importo": 0})
            t["voci"] += 1
            if f.get("importo_usd_mld") is None:
                t["voci_senza_importo"] += 1
            else:
                t["usd_mld"] = round(t["usd_mld"] + f["importo_usd_mld"], 2)
        return dict(sorted(tab.items(), key=lambda kv: -kv[1]["usd_mld"]))
    progetti = [f for f in flussi if not f["quadro"] and f.get("stato") != "cancellato"]
    quadri = [f for f in flussi if f["quadro"]]
    esclusi = [f for f in flussi if f.get("stato") == "cancellato"]
    internazionali = [f for f in progetti if f["da_paese"] != f["a_paese"]]
    return {
        "avvertenza": ("Annunci e spese effettive non coincidono. Le somme mettono insieme impegni di natura diversa "
                       "(piani pluriennali, acquisizioni chiuse, contributi pubblici, lettere d'intenti) e cambi fissi "
                       "indicativi: servono a vedere la direzione e l'ordine di grandezza dei flussi, non quanto è stato speso. "
                       "Gli impegni-quadro dei governi (quadro=true) sono sommati a parte perché in parte contengono gli stessi "
                       "progetti. I progetti cancellati sono esclusi. Le voci senza importo sono contate ma non sommate. "
                       "Il campione è curato a mano: mancano molti flussi minori, quindi i totali sono parziali."),
        "progetti": {
            "totale_usd_mld": round(sum(f["importo_usd_mld"] or 0 for f in progetti), 1),
            "voci": len(progetti),
            "voci_senza_importo": sum(1 for f in progetti if f["importo_usd_mld"] is None),
            "per_paese_origine": somma(progetti, "da_paese"),
            "per_paese_destinazione": somma(progetti, "a_paese"),
            "per_settore": somma(progetti, "settore"),
            "per_stato": somma(progetti, "stato"),
            "solo_internazionali_usd_mld": round(sum(f["importo_usd_mld"] or 0 for f in internazionali), 1),
            "verso_italia": [{"id": f["id"], "attore": f["attore"], "usd_mld": f["importo_usd_mld"], "stato": f["stato"]}
                             for f in progetti if f["a_paese"] == "IT"],
        },
        "impegni_quadro": {
            "totale_usd_mld": round(sum(f["importo_usd_mld"] or 0 for f in quadri), 1),
            "voci": [{"id": f["id"], "da": f["da_paese"], "a": f["a_paese"], "usd_mld": f["importo_usd_mld"],
                      "stato": f["stato"], "attore": f["attore"]} for f in quadri],
        },
        "esclusi_cancellati": [{"id": f["id"], "attore": f["attore"], "usd_mld": f["importo_usd_mld"]} for f in esclusi],
        "cambi_usati": {k: round(v, 6) for k, v in CAMBI.items()},
    }


# ----------------------------------------------------------------- principale
def principale():
    errori_m, errori_i = [], []
    curati = leggi_json(os.path.join(QUI, "punti_curati.json"), {})
    coord = (leggi_json(os.path.join(QUI, "epoch_coordinate.json"), {}) or {}).get("siti", {})
    siti = leggi_json(os.path.join(QUI, "top500_siti.json"), {}) or {}
    fl = leggi_json(os.path.join(QUI, "flussi.json"), {}) or {}
    precedente = leggi_json(OUT_MONDO, {}) or {}
    prec_el = precedente.get("elementi", [])

    # Epoch data center
    ep, info_ep = epoch_data_center(coord, siti.get("iso", {}), errori_m)
    if ep is None:
        ep = [p for p in prec_el if p.get("origine_dato") == "epoch"]
        info_ep = (precedente.get("meta", {}) or {}).get("epoch", {})
    # TOP500
    t5, lista = top500(siti, errori_m)
    if t5 is None:
        t5 = [p for p in prec_el if p.get("origine_dato") == "top500"]
        lista = (precedente.get("meta", {}) or {}).get("top500_lista")
    # Quote Epoch
    quote = epoch_quote(errori_m) or precedente.get("quote_paesi")

    # Voci curate
    cur = []
    for p in curati.get("punti", []):
        q = dict(p)
        q["importo_usd_mld"], q["metodo_usd"] = in_usd(p.get("importo"), p.get("valuta"), p.get("importo_usd_mld"))
        q["origine_dato"] = "curato"
        cur.append(q)

    elementi = filtra(cur + ep + t5, valida_punto, errori_m, "punto")
    ids = [p["id"] for p in elementi]
    for d in {i for i in ids if ids.count(i) > 1}:
        errori_m.append(f"id duplicato: {d}")

    conta = {}
    for p in elementi:
        conta[p["categoria"]] = conta.get(p["categoria"], 0) + 1
    mondo = {
        "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": [
            {"nome": "Epoch AI, AI data centers", "link": PAGINA_EPOCH_DC, "licenza": "CC BY 4.0", "data_dato": (info_ep or {}).get("data_dato", OGGI)},
            {"nome": "Epoch AI, Data on AI chip imports", "link": PAGINA_EPOCH_TRADE, "licenza": "CC BY 4.0", "data_dato": (quote or {}).get("trimestre")},
            {"nome": "TOP500", "link": "https://www.top500.org/lists/top500/", "licenza": "uso con citazione (pagina pubblica, nessuna licenza aperta dichiarata)", "data_dato": lista},
            {"nome": "Voci curate a mano (comunicati societari, DCD, TrendForce, Reuters e altri: fonte e link per riga)", "link": "raccolta/ai/punti_curati.json", "licenza": "fatti con citazione", "data_dato": OGGI},
            {"nome": "Coordinate: geocodifica OpenStreetMap Nominatim", "link": "https://nominatim.openstreetmap.org/", "licenza": "ODbL 1.0 (© OpenStreetMap contributors)", "data_dato": "2026-11-09"},
        ],
        "nota": ("Infrastrutture AI fuori dagli USA (gli USA sono in ai.json): data center AI (Epoch AI in automatico + voci curate), "
                 "fabbriche di chip e impacchettamento (curate) e i primi 20 supercalcolatori della TOP500 (automatico; quelli già "
                 "in ai.json hanno duplicato_ai_json=true). Coordinate tutte stimate: vedi origine_coord e precisione_km "
                 "(i 'centroide-paese' non sono posizioni reali). mw = potenza come la dà la fonte: per Epoch è potenza IT stimata, "
                 "per la TOP500 il consumo durante il test, per le voci curate vedi mw_tipo. importo = investimento dichiarato, "
                 "in miliardi della valuta; importo_usd_mld convertito con cambi fissi indicativi. Lo stato dei progetti esteri "
                 "è spesso dedotto da annunci: controllare data_fonte."),
        "conteggi": conta,
        "meta": {"epoch": info_ep, "top500_lista": lista},
        "quote_paesi": quote,
        "elementi": elementi,
        "errori": errori_m,
    }
    scrivi_json(OUT_MONDO, mondo)

    # Investimenti
    indice = {p["id"]: p for p in elementi}
    for p in (leggi_json(AI_USA, {}) or {}).get("punti", []):
        indice.setdefault(p["id"], p)
    flussi = filtra(costruisci_flussi(fl, indice, errori_i), valida_flusso, errori_i, "flusso")
    inv = {
        "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": [{"nome": "Voci curate a mano da comunicati societari e governativi, Reuters/AFP, DCD, TrendForce e altri (fonte e link per riga)",
                   "link": "raccolta/ai/flussi.json", "licenza": "fatti con citazione", "data_dato": OGGI}],
        "nota": fl.get("nota", ""),
        "elementi": flussi,
        "riepilogo": riepilogo(flussi),
        "capex_2026": fl.get("capex_2026"),
        "errori": errori_i,
    }
    scrivi_json(OUT_INV, inv)
    print(f"ai-mondo.json: {len(elementi)} punti {conta}; quote Epoch {(quote or {}).get('trimestre')}; TOP500 {lista}")
    print(f"investimenti.json: {len(flussi)} flussi; totale progetti {inv['riepilogo']['progetti']['totale_usd_mld']} mld USD; "
          f"impegni-quadro {inv['riepilogo']['impegni_quadro']['totale_usd_mld']} mld USD")
    for e in errori_m + errori_i:
        print("AVVISO:", e)


def solo_valida():
    errori = []
    m = leggi_json(OUT_MONDO, {}) or {}
    i = leggi_json(OUT_INV, {}) or {}
    for p in m.get("elementi", []):
        errori += [f"punto {p.get('id')}: {x}" for x in valida_punto(p)]
    for f in i.get("elementi", []):
        errori += [f"flusso {f.get('id')}: {x}" for x in valida_flusso(f)]
    for e in errori:
        print("ERRORE:", e)
    print(f"Validati {len(m.get('elementi', []))} punti e {len(i.get('elementi', []))} flussi: {len(errori)} problemi")
    return 1 if errori else 0


if __name__ == "__main__":
    if "--valida" in sys.argv:
        sys.exit(solo_valida())
    principale()
