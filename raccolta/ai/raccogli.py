#!/usr/bin/env python3
"""AI infrastructure worldwide and the direction of AI investment.

Produces:
  docs/data/ai-mondo.json      points worldwide (US included): data-center-ai, hub-data-center, fab-chip,
                               packaging, attrezzature, supercalcolo + AI compute shares by country (Epoch AI)
  docs/data/ai.json            curated subset (~60 key sites) for the fixed layer 'AI infrastructure',
                               in the fixed-installation schema (classe 'fisso'), built from ai_selezione.json
  docs/data/investimenti.json  capital flows "from -> to" + summary + 2026 capex (logic unchanged)

Automatic sources (downloaded on every run):
  - Epoch AI, "AI data centers" (CC BY 4.0): data_centers.zip, all countries
      https://epoch.ai/data/data_centers/data_centers.zip
  - Epoch AI, "GPU clusters" (CC BY 4.0): gpu_clusters.csv (archive frozen in 2025, with coordinates)
      https://epoch.ai/data/gpu_clusters.csv
  - Epoch AI, "AI chip imports" (CC BY 4.0): ai_chip_trade.zip -> AI compute shares by country
  - TOP500 (latest list, public page): top 50 systems

Hand-curated files (same folder):
  - punti_curati.json     data centres beyond the Epoch tracker, data-centre hubs, fabs, packaging, equipment
  - epoch_coordinate.json coordinates of Epoch tracker sites (Epoch gives addresses, not coordinates)
  - top500_siti.json      coordinates of TOP500 sites ('posizione_sconosciuta' = not drawn)
  - ai_selezione.json     which points go into ai.json, with the legacy ids kept
  - flussi.json           investment flows and 2026 capex

If an automatic source fails, the script reuses the entries of the previous run (read from the output
file) and records it in "errori", without failing.

Usage (from the repository root):
  python3 raccolta/ai/raccogli.py             download, merge, validate, write
  python3 raccolta/ai/raccogli.py --valida    only validate the files already written
Python 3 standard library only.
"""
import csv
import html as H
import io
import json
import math
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
OUT_AI = os.path.join(DATI, "ai.json")

URL_EPOCH_DC = "https://epoch.ai/data/data_centers/data_centers.zip"
URL_EPOCH_GPU = "https://epoch.ai/data/gpu_clusters.csv"
URL_EPOCH_TRADE = "https://epoch.ai/data/ai_chip_trade/ai_chip_trade.zip"
URL_TOP500 = "https://www.top500.org/lists/top500/list/{a}/{m:02d}/"
PAGINA_EPOCH_DC = "https://epoch.ai/data/ai-data-centers"
PAGINA_EPOCH_GPU = "https://epoch.ai/data/gpu-clusters"
PAGINA_EPOCH_TRADE = "https://epoch.ai/data/ai-chip-imports"
UA = {"User-Agent": "osint-data-fetcher/1.0 (personal, non-commercial)"}
QUANTI_TOP500 = 50
SOGLIA_GPU_H100E = 500       # GPU clusters below this size (H100-equivalents) are not drawn
RAGGIO_DOPPIONE_KM = 8.0     # a GPU cluster this close to another drawn AI site is treated as the same site

# Fixed indicative exchange rates (USD per unit), used only when the source gives no USD equivalent.
CAMBI = {"USD": 1.0, "EUR": 1.10, "GBP": 1.30, "JPY": 1 / 150, "KRW": 1 / 1400, "INR": 1 / 88,
         "BRL": 0.18, "SEK": 0.10, "CNY": 0.14}

METODO_EN = {"equivalente dato dalla fonte": "USD equivalent given by the source", "importo non dichiarato": "amount not declared",
             "USD dalla fonte": "USD from the source"}
CATEGORIE = {"data-center-ai", "hub-data-center", "fab-chip", "packaging", "attrezzature", "supercalcolo"}
STATI_PUNTI = {"operativo", "operativo-parziale", "in-costruzione", "annunciato", "sospeso", "cancellato"}
STATI_FLUSSI = {"annunciato", "in corso", "completato", "sospeso", "cancellato"}
SETTORI = {"data center", "chip", "energia per AI", "fondo"}
AFFIDABILITA = {"alta", "media", "bassa"}
RE_DATA = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
RE_PAESE = re.compile(r"^[A-Z]{2}(\+[A-Z]{2})*$")
# ai.json (fixed layer): categories understood by docs/index.html (AI_CAT) and theatre of each country
CAT_AI_JSON = {"data-center-ai": "data-center", "hub-data-center": "data-center", "fab-chip": "fab-chip",
               "packaging": "fab-chip", "attrezzature": "fab-chip", "supercalcolo": "supercomputer"}
TEATRO_MO = {"SA", "AE", "QA", "BH", "KW", "OM", "IL", "JO", "EG", "IR", "IQ"}
TEATRO_NATO = {"US", "CA", "GB", "FR", "DE", "NL", "BE", "LU", "DK", "NO", "SE", "FI", "IS", "IE", "ES", "PT", "PL",
               "EE", "LV", "LT", "CZ", "SK", "HU", "AT", "CH", "GR", "TR", "RO", "BG", "SI", "HR"}

ADESSO = datetime.now(timezone.utc)
OGGI = ADESSO.strftime("%Y-%m-%d")


# ----------------------------------------------------------------- utilities
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


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a["lat"], a["lon"], b["lat"], b["lon"]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def pulisci_tag(testo):
    """Epoch appends '#confident', '#likely', '#speculative' to names: move them to a note."""
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
    """Returns (usd_bn, method). Method strings stay in Italian for investimenti.json compatibility."""
    if usd_fonte is not None:
        return round(float(usd_fonte), 2), "equivalente dato dalla fonte"
    if importo is None or valuta is None:
        return None, "importo non dichiarato"
    if valuta not in CAMBI:
        return None, f"valuta {valuta} senza cambio"
    if valuta == "USD":
        return round(float(importo), 2), "USD dalla fonte"
    return round(float(importo) * CAMBI[valuta], 2), f"convertito con cambio fisso indicativo {valuta}={CAMBI[valuta]:.5g} USD"


# ----------------------------------------------------------------- Epoch: data centres (all countries)
def epoch_data_center(coord, iso, errori):
    """All sites of the Epoch AI data-centre tracker. Returns (points, info) or (None, None)."""
    try:
        z = zipfile.ZipFile(io.BytesIO(scarica(URL_EPOCH_DC)))
        dc = list(csv.DictReader(io.TextIOWrapper(z.open("data_centers.csv"), encoding="utf-8")))
        tl = list(csv.DictReader(io.TextIOWrapper(z.open("data_center_timelines.csv"), encoding="utf-8")))
    except Exception as e:  # network, zip, csv
        errori.append(f"Epoch AI data centres: download failed ({e}); reusing previous entries")
        return None, None
    tempi = {}
    for r in tl:
        tempi.setdefault(r.get("Data center", ""), []).append(r)
    punti, per_paese = [], {}
    for r in dc:
        nome = (r.get("Name") or "").strip()
        paese_nome = (r.get("Country") or "").strip()
        if not nome:
            continue
        per_paese[paese_nome] = per_paese.get(paese_nome, 0) + 1
        c = coord.get(nome)
        if not c:
            errori.append(f"Epoch AI: new site without coordinates, not mapped: '{nome}' ({paese_nome}). "
                          "Add it to raccolta/ai/epoch_coordinate.json")
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
        energia, _ = pulisci_tag(r.get("Energy companies", ""))
        costo = num(r.get("Current total capital cost (2025 USD billions)"))
        h100 = num(r.get("Current H100 equivalents"))
        stato_testo = re.sub(r"\s+", " ", (ultimo.get("Construction status") or "")).strip()
        stato_testo = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stato_testo)  # strip markdown links
        if len(stato_testo) > 320:
            stato_testo = stato_testo[:317].rstrip() + "..."
        note = []
        if c.get("note"):
            note.append(c["note"])
        if data_max:
            note.append(f"Epoch projects {mw_max:.0f} MW IT by {data_max}.")
        if stato_testo:
            note.append(f"Latest Epoch observation ({ultimo.get('Date', '?')}): {stato_testo}")
        if tag_p or tag_u:
            note.append("Epoch certainty on owner/users: " + "; ".join(x for x in (tag_p, tag_u) if x))
        anno = int(primo[:4]) if primo else (int(data_max[:4]) if data_max else None)
        punti.append({
            "id": "EP-" + slug(nome),
            "categoria": "data-center-ai",
            "nome": nome,
            "paese": iso.get(paese_nome, ""),
            "luogo": re.sub(r"\s+", " ", (r.get("Address") or "")).strip() or None,
            "lat": c["lat"], "lon": c["lon"],
            "origine_coord": "estimated: " + c.get("origine", ""),
            "precisione_km": c.get("precisione_km"),
            "mw": tondo(mw_att, 0),
            "mw_tipo": "current IT power (Epoch estimate)",
            "mw_previsto": tondo(mw_max, 0) if data_max else None,
            "data_mw_previsto": data_max,
            "h100e": int(h100) if h100 else None,
            "proprietario": proprietario or None,
            "utilizzatori": utenti or None,
            "progetto": progetto or None,
            "investitori": investitori or None,
            "energia": energia or None,
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
    return punti, {"siti_per_paese": dict(sorted(per_paese.items(), key=lambda kv: -kv[1])), "data_dato": OGGI}


# ----------------------------------------------------------------- Epoch: GPU clusters (2025 archive)
def epoch_gpu_cluster(iso, gia, nomi_gia, errori):
    """Clusters from Epoch's GPU clusters archive that have real coordinates and are not already drawn."""
    try:
        righe = list(csv.DictReader(io.StringIO(scarica(URL_EPOCH_GPU).decode("utf-8"))))
    except Exception as e:
        errori.append(f"Epoch AI GPU clusters: download failed ({e}); reusing previous entries")
        return None, None
    conta_coord = {}
    for r in righe:
        la, lo = num(r.get("latitude")), num(r.get("longitude"))
        if la is not None and lo is not None:
            k = (round(la, 3), round(lo, 3))
            conta_coord[k] = conta_coord.get(k, 0) + 1
    cand, scartati = [], {"senza_coordinate": 0, "centroide_paese": 0, "sotto_soglia": 0, "superati_o_dismessi": 0}
    for r in righe:
        if (r.get("Superseded by") or "").strip() or (r.get("Decommissioned Date (if applicable)") or "").strip() \
                or (r.get("Exclude") or "").strip():
            scartati["superati_o_dismessi"] += 1
            continue
        la, lo = num(r.get("latitude")), num(r.get("longitude"))
        luogo = re.sub(r"\s+", " ", (r.get("Location") or "")).strip()
        paese_nome = (r.get("Country") or "").strip()
        if la is None or lo is None:
            scartati["senza_coordinate"] += 1
            continue
        if not luogo or luogo.lower() == paese_nome.lower() or conta_coord.get((round(la, 3), round(lo, 3)), 0) >= 10:
            scartati["centroide_paese"] += 1   # Epoch puts unknown sites on the country centroid: not a position
            continue
        h = num(r.get("H100 equivalents")) or 0
        if h < SOGLIA_GPU_H100E:
            scartati["sotto_soglia"] += 1
            continue
        cand.append((h, r, la, lo, luogo, paese_nome))
    cand.sort(key=lambda x: -x[0])
    punti, doppioni = [], 0
    for h, r, la, lo, luogo, paese_nome in cand:
        p = {"lat": round(la, 4), "lon": round(lo, 4)}
        nome_l = " " + re.sub(r"[^a-z0-9.]+", " ", (r.get("Name") or "").lower()) + " "
        if any(km(p, q) <= RAGGIO_DOPPIONE_KM for q in gia + punti) or any(f" {n} " in nome_l for n in nomi_gia):
            doppioni += 1
            continue
        nome = (r.get("Name") or "").strip()
        mw = num(r.get("Power Capacity (MW)"))
        data = (r.get("First Operational Date") or "")[:10]
        prop, _ = pulisci_tag(r.get("Owner", ""))
        utenti, _ = pulisci_tag(r.get("Users", ""))
        chip = (r.get("Chip type (primary)") or "").strip()
        nchip = num(r.get("Chip quantity (primary)"))
        fonte1 = (r.get("Source 1") or "").strip()
        p.update({
            "id": "GPU-" + slug(nome)[:60],
            "categoria": "data-center-ai",
            "tipo": "GPU cluster (Epoch archive, 2025)",
            "nome": nome,
            "paese": iso.get(paese_nome, iso.get(paese_nome.replace("United States of America", "United States"), "")),
            "luogo": luogo[:160],
            "origine_coord": "from the Epoch AI GPU clusters dataset (latitude/longitude columns)",
            "precisione_km": 3,
            "mw": tondo(mw, 0) if mw else None,
            "mw_tipo": "cluster power capacity (Epoch estimate)" if mw else None,
            "h100e": int(h),
            "proprietario": prop or None,
            "utilizzatori": utenti or None,
            "stato": "operativo",
            "anno": int(data[:4]) if data[:4].isdigit() else None,
            "importo": None, "valuta": None,
            "fonte": "Epoch AI, GPU clusters (archive)",
            "link": fonte1 if fonte1.startswith("https://") else PAGINA_EPOCH_GPU,
            "data_fonte": data if RE_DATA.match(data) and data <= OGGI else "2025",
            "affidabilita": "media" if (r.get("Certainty") or "") == "Likely" else "alta",
            "note": (f"{int(nchip):,} x {chip}. " if nchip and chip else "")
                    + f"First operational {data or 'n/a'}. Epoch archive frozen in 2025: status 'operativo' means 'existing when recorded'.",
            "origine_dato": "epoch-gpu",
        })
        if p["link"] != PAGINA_EPOCH_GPU:
            p["fonti"] = [{"fonte": "Epoch AI, GPU clusters", "link": PAGINA_EPOCH_GPU, "data_fonte": "2025"}]
        punti.append(p)
    scartati["doppioni_di_siti_gia_in_mappa"] = doppioni
    return punti, {"cluster_letti": len(righe), "cluster_in_mappa": len(punti), "scartati": scartati,
                   "soglia_h100e": SOGLIA_GPU_H100E}


# ----------------------------------------------------------------- Epoch: shares by country
def epoch_quote(errori):
    try:
        z = zipfile.ZipFile(io.BytesIO(scarica(URL_EPOCH_TRADE)))
        righe = list(csv.DictReader(io.TextIOWrapper(z.open("by_country.csv"), encoding="utf-8")))
    except Exception as e:
        errori.append(f"Epoch AI shares by country: download failed ({e}); reusing previous data")
        return None

    def chiave(q):
        a, t = q.split()
        return int(a), int(t[1])
    trimestri = sorted({r["Quarter"] for r in righe if r.get("Quarter")}, key=chiave)
    definitivi = [q for q in trimestri if any(r["Quarter"] == q and r.get("Provisional") == "No" for r in righe)]
    if not definitivi:
        errori.append("Epoch AI shares: no final quarter")
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
    serie = {}
    for qq in trimestri[-12:]:
        pp, _, _ = quote(qq)
        serie[qq] = {p["iso"] or p["paese"]: p["quota_cumulata_pct"] for p in pp[:6]}
    return {
        "trimestre": q,
        "provvisorio": False,
        "ultimo_trimestre_disponibile": trimestri[-1],
        "totale_h100e_cumulati": int(tot_c),
        "totale_h100e_trimestre": int(tot_q),
        "paesi": paesi[:20],
        "altri_paesi_h100e_cumulati": int(sum(p["h100e_cumulati"] for p in paesi[20:])),
        "serie_quote_cumulate_pct": serie,
        "fonte": "Epoch AI, Data on AI chip imports (CC BY 4.0)",
        "link": PAGINA_EPOCH_TRADE,
        "nota": "Shares of AI compute (H100 equivalents) delivered to each country since 2022, estimated by Epoch from "
                "customs statistics. The European Union is a single aggregate. Taiwan does not appear as a destination "
                "because it exports. An indication, not a census: Epoch estimates it covers part of the total.",
    }


# ----------------------------------------------------------------- TOP500
def top500(siti, errori, quanti=QUANTI_TOP500):
    """Returns (points, list, systems without a public position) or (None, None, None)."""
    anno = ADESSO.year
    tentativi = [(a, m) for a, m in ((anno, 11), (anno, 6), (anno - 1, 11), (anno - 1, 6))
                 if (a, m) <= (ADESSO.year, ADESSO.month)]
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
        errori.append("TOP500: no list could be downloaded; reusing previous entries")
        return None, None, None
    iso = siti.get("iso", {})
    punti, senza = [], []
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
        m_sys = re.search(r'href="(/system/\d+)">\s*(?:<b>(.*?)</b>\s*-\s*)?(.*?)</a>\s*(.*?)<br', td[1], re.S)
        m_site = re.search(r'href="/site/(\d+)">(.*?)</a>\s*<br>\s*(.*?)\s*$', td[1].strip(), re.S)
        if not m_sys or not m_site:
            errori.append(f"TOP500: row {rango} could not be parsed")
            continue
        sistema = re.sub(r"\s+", " ", H.unescape(m_sys.group(3))).strip().rstrip(",")
        sito_id, sito_nome = m_site.group(1), H.unescape(m_site.group(2)).strip()
        nome = H.unescape(m_sys.group(2) or "").strip() or f"Unnamed system ({sito_nome})"
        costruttore = re.sub(r"\s+", " ", H.unescape(m_sys.group(4))).strip()
        paese_nome = H.unescape(re.sub(r"<[^>]+>", "", m_site.group(3))).strip()
        valori = [re.sub(r"[^\d.]", "", re.sub(r"<[^>]+>", "", v)) for v in td[2:6]]
        core, rmax, rpeak, kw = (num(v) for v in valori)
        s = siti.get("siti", {}).get(sito_id)
        base = {"rango_top500": rango, "nome": nome, "proprietario": sito_nome, "paese": iso.get(paese_nome, ""),
                "rmax_pflops": rmax, "link": "https://www.top500.org" + m_sys.group(1)}
        if not s:
            errori.append(f"TOP500: new site {sito_id} ({sito_nome}, {paese_nome}) without coordinates: not mapped. "
                          "Add it to raccolta/ai/top500_siti.json")
            senza.append(dict(base, motivo="site not yet in top500_siti.json"))
            continue
        if s.get("posizione_sconosciuta"):
            senza.append(dict(base, motivo=s.get("luogo", "site not public")))
            continue
        punti.append({
            "id": f"T500-{lista[0]}{lista[1]:02d}-{rango:02d}",
            "categoria": "supercalcolo",
            "nome": nome,
            "paese": iso.get(paese_nome, ""),
            "luogo": s["luogo"],
            "lat": s["lat"], "lon": s["lon"],
            "origine_coord": s["origine"],
            "precisione_km": s["precisione_km"],
            "rango_top500": rango,
            "rmax_pflops": rmax, "rpeak_pflops": rpeak,
            "potenza_kw": kw, "core": int(core) if core else None,
            "mw": round(kw / 1000, 1) if kw else None,
            "mw_tipo": "power measured during the Linpack run (TOP500)" if kw else "not reported to TOP500",
            "sistema": sistema,
            "proprietario": sito_nome,
            "costruttore": costruttore or None,
            "stato": "operativo",
            "anno": None,
            "importo": None, "valuta": None,
            "fonte": f"TOP500, list {lista[0]}-{lista[1]:02d}",
            "link": "https://www.top500.org" + m_sys.group(1),
            "data_fonte": f"{lista[0]}-{lista[1]:02d}",
            "affidabilita": "alta",
            "note": f"Rank {rango} in the TOP500 of {lista[0]}-{lista[1]:02d}." + (f" {rmax / 1000:.3f} exaflop/s (Rmax)." if rmax else ""),
            "origine_dato": "top500",
        })
    return punti, f"{lista[0]}-{lista[1]:02d}", senza


# ----------------------------------------------------------------- validation
def valida_punto(p):
    e = []
    for k in ("id", "nome", "paese", "categoria", "lat", "lon", "stato", "fonte", "link", "data_fonte", "affidabilita"):
        if p.get(k) in (None, ""):
            e.append(f"missing {k}")
    lat, lon = p.get("lat"), p.get("lon")
    if not isinstance(lat, (int, float)) or not -90 <= lat <= 90:
        e.append("lat invalid")
    if not isinstance(lon, (int, float)) or not -180 <= lon <= 180:
        e.append("lon invalid")
    if p.get("categoria") not in CATEGORIE:
        e.append(f"category '{p.get('categoria')}' not allowed")
    if p.get("stato") not in STATI_PUNTI:
        e.append(f"status '{p.get('stato')}' not allowed")
    if p.get("affidabilita") not in AFFIDABILITA:
        e.append("affidabilita not allowed")
    if p.get("paese") and not RE_PAESE.match(p["paese"]):
        e.append("paese not a 2-letter ISO code")
    d = p.get("data_fonte")
    if d and (not RE_DATA.match(str(d)) or str(d) > OGGI):
        e.append(f"data_fonte '{d}' invalid or in the future")
    a = p.get("anno")
    if a is not None and not (isinstance(a, int) and 2000 <= a <= 2040):
        e.append("anno invalid")
    if p.get("link") and not str(p["link"]).startswith("https://"):
        e.append("link not https")
    if p.get("precisione_km") is None:
        e.append("missing precisione_km")
    if not p.get("origine_coord"):
        e.append("missing origine_coord")
    for f in p.get("fonti") or []:
        if f.get("data_fonte") and (not RE_DATA.match(str(f["data_fonte"])) or str(f["data_fonte"]) > OGGI):
            e.append(f"date of a secondary source invalid: {f.get('data_fonte')}")
    return e


def valida_flusso(f):
    e = []
    for k in ("id", "attore", "da_paese", "a_paese", "da_lat", "da_lon", "a_lat", "a_lon", "anno", "settore",
              "stato", "fonte", "link", "data_fonte", "affidabilita"):
        if f.get(k) in (None, ""):
            e.append(f"missing {k}")
    for k in ("da_lat", "a_lat"):
        if not isinstance(f.get(k), (int, float)) or not -90 <= f[k] <= 90:
            e.append(f"{k} invalid")
    for k in ("da_lon", "a_lon"):
        if not isinstance(f.get(k), (int, float)) or not -180 <= f[k] <= 180:
            e.append(f"{k} invalid")
    for k in ("da_paese", "a_paese"):
        if f.get(k) and not RE_PAESE.match(f[k]) and f[k] != "EU":
            e.append(f"{k} '{f[k]}' not ISO")
    if f.get("settore") not in SETTORI:
        e.append(f"settore '{f.get('settore')}' not allowed")
    if f.get("stato") not in STATI_FLUSSI:
        e.append(f"stato '{f.get('stato')}' not allowed")
    if f.get("affidabilita") not in AFFIDABILITA:
        e.append("affidabilita not allowed")
    d = f.get("data_fonte")
    if d and (not RE_DATA.match(str(d)) or str(d) > OGGI):
        e.append(f"data_fonte '{d}' invalid or in the future")
    if not isinstance(f.get("anno"), int) or not 2015 <= f["anno"] <= 2030:
        e.append("anno invalid")
    if f.get("importo") is not None and (not isinstance(f["importo"], (int, float)) or f["importo"] <= 0):
        e.append("importo not positive")
    if f.get("importo") is not None and f.get("valuta") not in CAMBI:
        e.append(f"valuta '{f.get('valuta')}' without exchange rate")
    if f.get("link") and not str(f["link"]).startswith("https://"):
        e.append("link not https")
    return e


def valida_ai(p):
    e = []
    for k in ("id", "classe", "categoria", "nome", "appartenenza", "stato", "lat", "lon", "teatro", "paese",
              "fonte", "link", "data_fonte", "affidabilita", "precisione_km", "origine_coord"):
        if p.get(k) in (None, ""):
            e.append(f"missing {k}")
    if p.get("categoria") not in set(CAT_AI_JSON.values()):
        e.append("category not understood by the map (AI_CAT)")
    if not isinstance(p.get("lat"), (int, float)) or not isinstance(p.get("lon"), (int, float)):
        e.append("coordinates invalid")
    return e


def filtra(voci, funzione, errori, etichetta):
    buone = []
    for v in voci:
        e = funzione(v)
        if e:
            gravi = [x for x in e if x.startswith(("missing lat", "missing lon", "lat ", "lon ", "da_l", "a_l",
                                                   "missing da_l", "missing a_l", "coordinates"))]
            errori.append(f"{etichetta} {v.get('id', '?')}: " + "; ".join(e) + (" -> excluded" if gravi else ""))
            if gravi:
                continue
        buone.append(v)
    return buone


# ----------------------------------------------------------------- ai.json (curated subset)
def teatro(paese):
    if paese == "IT":
        return "IT"
    if paese in TEATRO_MO:
        return "MO"
    if paese in TEATRO_NATO:
        return "NATO"
    return "ALTRO"


def costruisci_ai_json(elementi, selezione, errori):
    indice = {p["id"]: p for p in elementi}
    for p in elementi:   # TOP500 ids change with the rank: also index them by name
        if p["categoria"] == "supercalcolo":
            indice.setdefault("top500:" + p["nome"], p)
    punti = []
    for s in selezione.get("voci", []):
        p = indice.get(s["rif"])
        if not p:
            errori.append(f"ai.json: point '{s['rif']}' not found in ai-mondo.json; entry {s['id']} skipped")
            continue
        stato = p["stato"]
        note = s.get("note") or p.get("note") or ""
        if stato == "operativo-parziale":
            stato, note = "operativo", "Partly operational. " + note
        mw = p.get("mw")
        testa = []
        if mw:
            testa.append(f"{mw:g} MW ({p.get('mw_tipo') or 'power'})")
        if p.get("mw_previsto"):
            testa.append(f"{p['mw_previsto']:g} MW planned by {p.get('data_mw_previsto')}")
        if p.get("h100e"):
            testa.append(f"{p['h100e']:,} H100-equivalents")
        if p.get("rmax_pflops"):
            testa.append(f"{p['rmax_pflops']:g} PFlop/s Rmax, TOP500 rank {p.get('rango_top500')}")
        if p.get("nodo"):
            testa.append(p["nodo"])
        if p.get("proprietario"):
            testa.append("Owner: " + p["proprietario"])
        fonti = [{"fonte": p["fonte"], "link": p["link"], "data_fonte": p["data_fonte"]}] + list(p.get("fonti") or [])
        q = {
            "id": s["id"],
            "classe": "fisso",
            "categoria": CAT_AI_JSON[p["categoria"]],
            "nome": s.get("nome") or p.get("nome_en") or p["nome"],
            "appartenenza": p["paese"],
            "stato": stato,
            "data_evento": OGGI,
            "lat": p["lat"], "lon": p["lon"],
            "origine_coord": p.get("origine_coord"),
            "precisione_km": p.get("precisione_km"),
            "teatro": teatro(p["paese"]),
            "paese": p["paese"],
            "regione": p.get("luogo"),
            "fonte": p["fonte"],
            "link": p["link"],
            "data_fonte": p["data_fonte"],
            "affidabilita": p["affidabilita"],
            "note": (". ".join(testa) + ". " if testa else "") + note,
            "fonti": fonti,
            "rif_ai_mondo": p["id"],
            "dettaglio": "AI infrastructure, curated selection (from ai-mondo.json)",
        }
        if p["paese"] == "US":
            q["dossier"] = "stati-uniti"
        punti.append(q)
        p["duplicato_ai_json"] = True
    return punti


# ----------------------------------------------------------------- investment flows (logic unchanged)
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


# ----------------------------------------------------------------- main
def conteggi(elementi):
    cat, paese, orig, stato = {}, {}, {}, {}
    for p in elementi:
        cat[p["categoria"]] = cat.get(p["categoria"], 0) + 1
        paese[p["paese"]] = paese.get(p["paese"], 0) + 1
        orig[p["origine_dato"]] = orig.get(p["origine_dato"], 0) + 1
        stato[p["stato"]] = stato.get(p["stato"], 0) + 1
    ordina = lambda d: dict(sorted(d.items(), key=lambda kv: -kv[1]))
    return {"totale": len(elementi), "per_categoria": ordina(cat), "per_paese": ordina(paese),
            "per_origine": ordina(orig), "per_stato": ordina(stato)}


def principale():
    errori_m, errori_i = [], []
    curati = leggi_json(os.path.join(QUI, "punti_curati.json"), {})
    coord = (leggi_json(os.path.join(QUI, "epoch_coordinate.json"), {}) or {}).get("siti", {})
    siti = leggi_json(os.path.join(QUI, "top500_siti.json"), {}) or {}
    selezione = leggi_json(os.path.join(QUI, "ai_selezione.json"), {}) or {}
    fl = leggi_json(os.path.join(QUI, "flussi.json"), {}) or {}
    precedente = leggi_json(OUT_MONDO, {}) or {}
    prec_el = precedente.get("elementi", [])
    meta_prec = precedente.get("meta", {}) or {}
    iso = siti.get("iso", {})

    ep, info_ep = epoch_data_center(coord, iso, errori_m)
    if ep is None:
        ep = [p for p in prec_el if p.get("origine_dato") == "epoch"]
        info_ep = meta_prec.get("epoch", {})
    t5, lista, senza = top500(siti, errori_m)
    if t5 is None:
        t5 = [p for p in prec_el if p.get("origine_dato") == "top500"]
        lista, senza = meta_prec.get("top500_lista"), precedente.get("senza_posizione", [])
    quote = epoch_quote(errori_m) or precedente.get("quote_paesi")

    cur = []
    for p in curati.get("punti", []):
        q = dict(p)
        q["importo_usd_mld"], metodo = in_usd(p.get("importo"), p.get("valuta"), p.get("importo_usd_mld"))
        q["metodo_usd"] = METODO_EN.get(metodo, metodo.replace("convertito con cambio fisso indicativo", "converted at fixed indicative rate"))
        q["origine_dato"] = "curato"
        cur.append(q)

    gia = [{"lat": p["lat"], "lon": p["lon"]} for p in cur + ep + t5
           if p.get("categoria") in ("data-center-ai", "supercalcolo") and isinstance(p.get("lat"), (int, float))]
    nomi_t5 = {re.sub(r"[^a-z0-9.]+", " ", p["nome"].lower()).strip() for p in t5}
    nomi_t5 = {n.replace("supercomputer ", "") for n in nomi_t5 if len(n) >= 4}
    gpu, info_gpu = epoch_gpu_cluster(iso, gia, nomi_t5, errori_m)
    if gpu is None:
        gpu = [p for p in prec_el if p.get("origine_dato") == "epoch-gpu"]
        info_gpu = meta_prec.get("epoch_gpu", {})

    elementi = filtra(cur + ep + gpu + t5, valida_punto, errori_m, "point")
    ids = [p["id"] for p in elementi]
    for d in sorted({i for i in ids if ids.count(i) > 1}):
        errori_m.append(f"duplicate id: {d}")

    # ai.json first: it marks the points it uses (duplicato_ai_json)
    ai_punti = filtra(costruisci_ai_json(elementi, selezione, errori_m), valida_ai, errori_m, "ai.json")
    ai_doc = {
        "aggiornato": OGGI,
        "nota": ("Curated selection of the most important AI sites worldwide for the fixed layer 'AI infrastructure' "
                 "(fixed-installation schema). Every entry is a copy of a point in ai-mondo.json (field rif_ai_mondo), "
                 "chosen in raccolta/ai/ai_selezione.json; ids of the November 2026 US dossier are kept. "
                 "Categories mapped to the map's AI_CAT: data-center, fab-chip (fabs, packaging, equipment), supercomputer."),
        "punti": ai_punti,
    }
    scrivi_json(OUT_AI, ai_doc)

    for p in elementi:
        p.setdefault("duplicato_ai_json", False)
    mondo = {
        "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": [
            {"nome": "Epoch AI, AI data centers", "link": PAGINA_EPOCH_DC, "licenza": "CC BY 4.0", "data_dato": (info_ep or {}).get("data_dato", OGGI)},
            {"nome": "Epoch AI, GPU clusters (archive frozen in 2025)", "link": PAGINA_EPOCH_GPU, "licenza": "CC BY 4.0", "data_dato": "2025"},
            {"nome": "Epoch AI, Data on AI chip imports", "link": PAGINA_EPOCH_TRADE, "licenza": "CC BY 4.0", "data_dato": (quote or {}).get("trimestre")},
            {"nome": "TOP500", "link": "https://www.top500.org/lists/top500/", "licenza": "use with citation (public page, no open licence stated)", "data_dato": lista},
            {"nome": "Hand-curated points (company releases, DCD, TrendForce, Reuters and others: source and link per row)", "link": "raccolta/ai/punti_curati.json", "licenza": "facts with citation", "data_dato": OGGI},
            {"nome": "Wikipedia, List of semiconductor fabrication plants (baseline for some fabs)", "link": "https://en.wikipedia.org/wiki/List_of_semiconductor_fabrication_plants", "licenza": "CC BY-SA 4.0", "data_dato": "2026-11-10"},
            {"nome": "Coordinates: OpenStreetMap Nominatim geocoding", "link": "https://nominatim.openstreetmap.org/", "licenza": "ODbL 1.0 (© OpenStreetMap contributors)", "data_dato": "2026-11-10"},
        ],
        "nota": ("AI infrastructure worldwide, US included: AI data centres (Epoch AI tracker, automatic, all countries; Epoch GPU-cluster "
                 "archive, automatic, only clusters with real coordinates and at least 500 H100e not already mapped; hand-curated campuses), "
                 "data-centre hubs (metro clusters, not single sites), chip fabs and memory fabs, advanced packaging, equipment and "
                 "material chokepoints (curated) and the top 50 TOP500 supercomputers (automatic). All coordinates are estimates: see "
                 "origine_coord and precisione_km; systems or sites without a public position are not drawn and are listed in "
                 "senza_posizione. mw = power as given by the source: Epoch = estimated IT power; TOP500 = consumption during the "
                 "benchmark; hubs = metro market capacity; curated = see mw_tipo. importo = declared investment in billions of the "
                 "currency; importo_usd_mld converted at fixed indicative rates. duplicato_ai_json = the point is also in ai.json "
                 "(do not draw twice when both layers are on). Status of projects is often inferred from announcements: check data_fonte."),
        "conteggi": conteggi(elementi),
        "meta": {"epoch": info_ep, "epoch_gpu": info_gpu, "top500_lista": lista, "categorie": sorted(CATEGORIE)},
        "quote_paesi": quote,
        "senza_posizione": senza,
        "elementi": elementi,
        "errori": errori_m,
    }
    scrivi_json(OUT_MONDO, mondo)

    # Investment flows: destination points looked up in ai-mondo and ai.json
    indice = {p["id"]: p for p in elementi}
    for p in ai_punti:
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
    c = mondo["conteggi"]
    print(f"ai-mondo.json: {c['totale']} points {c['per_categoria']}; origin {c['per_origine']}; "
          f"Epoch shares {(quote or {}).get('trimestre')}; TOP500 {lista}; without position {len(senza or [])}")
    print(f"ai.json: {len(ai_punti)} points")
    print(f"investimenti.json: {len(flussi)} flows; projects total {inv['riepilogo']['progetti']['totale_usd_mld']} bn USD; "
          f"framework commitments {inv['riepilogo']['impegni_quadro']['totale_usd_mld']} bn USD")
    for e in errori_m + errori_i:
        print("WARNING:", e)


def solo_valida():
    errori = []
    m = leggi_json(OUT_MONDO, {}) or {}
    i = leggi_json(OUT_INV, {}) or {}
    a = leggi_json(OUT_AI, {}) or {}
    for p in m.get("elementi", []):
        errori += [f"point {p.get('id')}: {x}" for x in valida_punto(p)]
    ids = [p.get("id") for p in m.get("elementi", [])]
    errori += [f"duplicate id {d}" for d in sorted({x for x in ids if ids.count(x) > 1})]
    for p in a.get("punti", []):
        errori += [f"ai.json {p.get('id')}: {x}" for x in valida_ai(p)]
    for f in i.get("elementi", []):
        errori += [f"flusso {f.get('id')}: {x}" for x in valida_flusso(f)]
    for nome, perc in (("ai-mondo.json", OUT_MONDO), ("ai.json", OUT_AI), ("investimenti.json", OUT_INV)):
        if os.path.exists(perc) and os.path.getsize(perc) > 1_500_000:
            errori.append(f"{nome} larger than 1.5 MB")
    for e in errori:
        print("ERROR:", e)
    print(f"Validated {len(m.get('elementi', []))} points, {len(a.get('punti', []))} ai.json points and "
          f"{len(i.get('elementi', []))} flows: {len(errori)} problems")
    return 1 if errori else 0


if __name__ == "__main__":
    if "--valida" in sys.argv:
        sys.exit(solo_valida())
    principale()
