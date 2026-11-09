#!/usr/bin/env python3
"""Idrogeno e ammoniaca verde nei porti: progetti, gasdotti H2, bunkeraggio, 'realta' 2025-2026.

Fonti:
  - raccolta/idrogeno/progetti.json   progetti curati a mano (punti), ognuno con fonte, link, data
  - raccolta/idrogeno/pipeline.json   gasdotti H2 come linee SCHEMATICHE
  - raccolta/idrogeno/realta.json     obiettivi vs capacita' reale, costi, aste EHB, H2Global,
                                      cancellazioni, FuelEU/IMO
  - IEA Hydrogen Production and Infrastructure Projects Database (CC BY 4.0), FACOLTATIVO:
      la pagina IEA e' protetta (HTTP 403 ai client automatici) e il download richiede il sito.
      Lo script lo usa se trova un .xlsx in raccolta/idrogeno/iea/ oppure se la variabile
      d'ambiente IEA_H2_DB_URL punta a un file .xlsx scaricabile. Altrimenti salta con un avviso.
  - Collegamenti con gli altri livelli (solo lettura): docs/data/rete-elettrica.json (linee >=380 kV
    e HVDC), docs/data/offshore-nord.json (se esiste), docs/data/prezzi.json (TTF).

Produce: docs/data/idrogeno.json
Uso:     python3 raccolta/idrogeno/raccogli.py   (dalla radice del repository)
Solo libreria standard. Non fallisce se una fonte facoltativa manca: lo scrive in "errori".
"""
import glob
import io
import json
import math
import os
import re
import sys
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
DATI = os.path.join(RADICE, "docs", "data")
OUT = os.path.join(DATI, "idrogeno.json")
UA = {"User-Agent": "Mozilla/5.0 (monitor-geoeconomico OSINT, uso non commerciale)"}

STATI = {"operativo", "in costruzione", "FID", "sviluppo", "annunciato", "sospeso", "cancellato"}
CATEGORIE = {"elettrolizzatore", "terminale-import", "bunkeraggio", "e-fuel", "export",
             "rete-h2-locale", "idrogeno-blu", "domanda-industriale"}
AFFIDABILITA = {"alta", "media", "bassa"}
PRECISIONI = {"sito", "area", "regione"}
OBBLIGATORI_PUNTO = ["id", "nome", "paese", "lat", "lon", "categoria", "stato", "operatore",
                     "fonte", "link", "data_fonte", "affidabilita", "precisione_coord"]
OBBLIGATORI_LINEA = ["id", "nome", "stato", "fonte", "link", "data_fonte", "affidabilita", "g"]

FOCUS_NORD = {"NL", "DE", "BE", "DK", "PL", "SE", "GB", "NO"}
FOCUS_IT = {"IT"}
# Paesi seguiti nel database IEA (codici ISO3 come li usa l'IEA)
IEA_PAESI = {"NLD": "NL", "DEU": "DE", "BEL": "BE", "DNK": "DK", "POL": "PL", "ITA": "IT",
             "SAU": "SA", "EGY": "EG", "OMN": "OM", "MAR": "MA", "NAM": "NA", "CHL": "CL",
             "AUS": "AU", "IND": "IN", "ARE": "AE"}

errori = []


def avviso(msg):
    errori.append(msg)
    print("AVVISO:", msg, file=sys.stderr)


def carica(nome):
    with open(os.path.join(QUI, nome), encoding="utf-8") as f:
        return json.load(f)


def leggi_dati(nome):
    p = os.path.join(DATI, nome)
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        avviso(f"{nome}: lettura fallita ({e})")
        return None


# ---------------------------------------------------------------- validazione
def data_valida(s):
    return isinstance(s, str) and re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", s) is not None


def valida_punto(p):
    probl = [f"manca {k}" for k in OBBLIGATORI_PUNTO if p.get(k) in (None, "")]
    if not isinstance(p.get("lat"), (int, float)) or not -90 <= p["lat"] <= 90:
        probl.append("lat non valida")
    if not isinstance(p.get("lon"), (int, float)) or not -180 <= p["lon"] <= 180:
        probl.append("lon non valida")
    if p.get("stato") not in STATI:
        probl.append(f"stato '{p.get('stato')}' non ammesso")
    if p.get("categoria") not in CATEGORIE:
        probl.append(f"categoria '{p.get('categoria')}' non ammessa")
    if p.get("affidabilita") not in AFFIDABILITA:
        probl.append("affidabilita non ammessa")
    if p.get("precisione_coord") not in PRECISIONI:
        probl.append("precisione_coord non ammessa")
    if not data_valida(p.get("data_fonte")):
        probl.append("data_fonte non AAAA[-MM[-GG]]")
    if not str(p.get("link", "")).startswith("https://"):
        probl.append("link non https")
    if not re.fullmatch(r"[A-Z]{2}", str(p.get("paese", ""))):
        probl.append("paese non ISO2")
    if p.get("mw") is not None and not isinstance(p["mw"], (int, float)):
        probl.append("mw non numerico")
    return probl


def valida_linea(l):
    probl = [f"manca {k}" for k in OBBLIGATORI_LINEA if l.get(k) in (None, "")]
    if l.get("stato") not in STATI:
        probl.append(f"stato '{l.get('stato')}' non ammesso")
    if not data_valida(l.get("data_fonte")):
        probl.append("data_fonte non valida")
    for parte in l.get("g", []):
        if len(parte) < 2:
            probl.append("parte con meno di 2 vertici")
        for v in parte:
            if not (isinstance(v, list) and len(v) == 2 and -180 <= v[0] <= 180 and -90 <= v[1] <= 90):
                probl.append(f"vertice non valido {v}")
    return probl


# ---------------------------------------------------------------- geometria
def km_tra(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def km_punto_segmento(lat, lon, a, b):
    """Distanza approssimata (proiezione equirettangolare locale) punto - segmento [lon,lat]."""
    k = math.cos(math.radians(lat))
    px, py = lon * k, lat
    ax, ay, bx, by = a[0] * k, a[1], b[0] * k, b[1]
    dx, dy = bx - ax, by - ay
    t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    qx, qy = ax + t * dx, ay + t * dy
    return math.hypot(px - qx, py - qy) * 111.2


def km_linea(lat, lon, g):
    best = float("inf")
    for parte in g:
        for a, b in zip(parte, parte[1:]):
            best = min(best, km_punto_segmento(lat, lon, a, b))
        if len(parte) == 1:
            best = min(best, km_tra(lat, lon, parte[0][1], parte[0][0]))
    return best


# ---------------------------------------------------------------- collegamenti
def collega_rete(punti):
    rete = leggi_dati("rete-elettrica.json")
    if not rete:
        avviso("rete-elettrica.json assente: niente collegamento con la rete elettrica")
        return None
    linee = [l for l in rete.get("elementi", []) if l.get("g")]
    for p in punti:
        if not (34 <= p["lat"] <= 72 and -25 <= p["lon"] <= 65):
            continue  # fuori dal riquadro di rete-elettrica.json
        vicine = []
        for l in linee:
            d = km_linea(p["lat"], p["lon"], l["g"])
            if d <= 60:
                vicine.append((d, l))
        vicine.sort(key=lambda x: x[0])
        if vicine:
            d, l = vicine[0]
            p["rete_vicina"] = {"nome": l.get("nome") or "(senza nome in OSM)", "tensione_kv": l.get("tensione_kv"),
                                "hvdc": l.get("hvdc"), "stato": l.get("stato"), "km": round(d, 1)}
        hvdc = []
        for d, l in vicine:
            if l.get("hvdc") and l.get("nome") and l["nome"] not in [h["nome"] for h in hvdc]:
                hvdc.append({"nome": l["nome"], "stato": l.get("stato"), "km": round(d, 1)})
        if hvdc:
            p["hvdc_entro_60km"] = hvdc[:5]
    return {"file": "rete-elettrica.json", "aggiornato": rete.get("aggiornato"), "linee_lette": len(linee)}


def collega_offshore(punti):
    off = leggi_dati("offshore-nord.json")
    if not off:
        return {"file": "offshore-nord.json", "nota": "file non presente al momento dell'esecuzione: collegamento saltato"}
    parchi = [e for e in off.get("elementi", []) if isinstance(e.get("lat"), (int, float)) and isinstance(e.get("lon"), (int, float))]
    for p in punti:
        vicini = sorted(((km_tra(p["lat"], p["lon"], e["lat"], e["lon"]), e) for e in parchi), key=lambda x: x[0])
        vicini = [(d, e) for d, e in vicini if d <= 150][:3]
        if vicini:
            p["eolico_offshore_entro_150km"] = [{"nome": e.get("nome"), "stato": e.get("stato"),
                                                  "mw": e.get("mw") or e.get("capacita_mw"), "km": round(d, 1)} for d, e in vicini]
    return {"file": "offshore-nord.json", "aggiornato": off.get("aggiornato"), "parchi_letti": len(parchi)}


def ttf_e_grigio():
    """TTF da prezzi.json e stima del costo dell'H2 grigio per interpolazione lineare tra i due
    punti IEA (2024: 10 EUR/MBtu -> 2,9 EUR/kg; 2022: 39 EUR/MBtu -> 4,8 EUR/kg).
    E' una STIMA dell'osservatorio: ignora variazioni di prezzo della CO2 e dei costi fissi."""
    prezzi = leggi_dati("prezzi.json")
    if not prezzi:
        avviso("prezzi.json assente: niente TTF")
        return None
    ttf = next((s for s in prezzi.get("serie", []) if s.get("id") == "ttf"), None)
    if not ttf or not ttf.get("serie"):
        avviso("prezzi.json: serie TTF non trovata")
        return None
    ultimo_data, ultimo = ttf["serie"][-1]
    ultimi30 = [v for _, v in ttf["serie"][-22:]]
    media = sum(ultimi30) / len(ultimi30)
    MWH_PER_MBTU = 0.293071

    def grigio(eur_mwh):
        mbtu = eur_mwh * MWH_PER_MBTU
        return 2.9 + (mbtu - 10.0) * (4.8 - 2.9) / (39.0 - 10.0)

    return {
        "ttf_ultimo_eur_mwh": ultimo, "data": ultimo_data,
        "ttf_media_22_sedute_eur_mwh": round(media, 2),
        "ttf_ultimo_eur_mbtu": round(ultimo * MWH_PER_MBTU, 1),
        "h2_grigio_stima_eur_kg": round(grigio(ultimo), 1),
        "h2_eolico_2024_iea_eur_kg": "5,3-7",
        "tipo": "stima",
        "metodo": "Interpolazione lineare sul TTF tra due punti IEA (NW European Hydrogen Monitor 2025): "
                  "TTF 10 EUR/MBtu -> 2,9 EUR/kg (2024) e 39 EUR/MBtu -> 4,8 EUR/kg (2022). "
                  "Non tiene conto del prezzo CO2 attuale ne' dell'inflazione: ordine di grandezza, non quotazione.",
        "fonte_ttf": "docs/data/prezzi.json (serie 'ttf')",
    }


# ---------------------------------------------------------------- database IEA (facoltativo)
def _xlsx_righe(dati):
    """Legge il primo foglio 'utile' di un xlsx con la sola libreria standard. Restituisce {foglio: righe}."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    z = zipfile.ZipFile(io.BytesIO(dati))
    condivise = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", ns):
            condivise.append("".join(t.text or "" for t in si.iter("{%s}t" % ns["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    mappa = {r.get("Id"): r.get("Target") for r in rels}
    fogli = {}
    for s in wb.find("m:sheets", ns):
        rid = s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        target = mappa.get(rid, "")
        path = "xl/" + target.lstrip("/").replace("xl/", "") if not target.startswith("xl/") else target
        if path not in z.namelist():
            continue
        righe = []
        for row in ET.fromstring(z.read(path)).iter("{%s}row" % ns["m"]):
            r = {}
            for c in row.findall("m:c", ns):
                ref = re.match(r"([A-Z]+)", c.get("r", "A")).group(1)
                col = 0
                for ch in ref:
                    col = col * 26 + ord(ch) - 64
                v = c.find("m:v", ns)
                if c.get("t") == "s" and v is not None:
                    val = condivise[int(v.text)]
                elif c.get("t") == "inlineStr":
                    val = "".join(t.text or "" for t in c.iter("{%s}t" % ns["m"]))
                else:
                    val = v.text if v is not None else None
                r[col - 1] = val
            if r:
                righe.append([r.get(i) for i in range(max(r) + 1)])
        fogli[s.get("name")] = righe
    return fogli


def _num(x):
    try:
        return float(str(x).replace(",", ""))
    except (TypeError, ValueError):
        return None


def riassumi_iea(fogli):
    """Cerca un foglio con intestazioni Country/Status e conta i progetti per paese e stato.
    Le colonne vengono riconosciute per nome (l'IEA le cambia tra edizioni)."""
    for nome, righe in fogli.items():
        for i, riga in enumerate(righe[:40]):
            testo = [str(c or "").strip().lower() for c in riga]
            ic = next((j for j, t in enumerate(testo) if t in ("country", "country code", "iso code")), None)
            is_ = next((j for j, t in enumerate(testo) if t == "status"), None)
            if ic is None or is_ is None:
                continue
            itec = next((j for j, t in enumerate(testo) if t.startswith("technology")), None)
            imw = next((j for j, t in enumerate(testo) if "mwel" in t or t.startswith("capacity_mw")), None)
            conteggio = {}
            for r in righe[i + 1:]:
                if len(r) <= max(ic, is_):
                    continue
                paese = IEA_PAESI.get(str(r[ic] or "").strip().upper())
                if not paese:
                    continue
                stato = str(r[is_] or "n.d.").strip()
                c = conteggio.setdefault(paese, {})
                s = c.setdefault(stato, {"progetti": 0, "mw_el": 0.0})
                s["progetti"] += 1
                if imw is not None and len(r) > imw and _num(r[imw]):
                    s["mw_el"] += _num(r[imw])
            if conteggio:
                for c in conteggio.values():
                    for s in c.values():
                        s["mw_el"] = round(s["mw_el"], 1)
                return {"foglio": nome, "colonna_tecnologia": itec is not None,
                        "colonna_mw": imw is not None, "per_paese_e_stato": conteggio}
    return None


def database_iea():
    dati, origine = None, None
    locali = sorted(glob.glob(os.path.join(QUI, "iea", "*.xlsx")))
    if locali:
        origine = os.path.relpath(locali[-1], RADICE)
        with open(locali[-1], "rb") as f:
            dati = f.read()
    elif os.environ.get("IEA_H2_DB_URL"):
        url = os.environ["IEA_H2_DB_URL"]
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                dati = r.read()
            origine = url
        except Exception as e:  # noqa: BLE001
            avviso(f"IEA database: download da IEA_H2_DB_URL fallito ({e})")
            return None
    else:
        avviso("IEA Hydrogen Production and Infrastructure Projects Database non usato: la pagina IEA "
               "risponde 403 ai client automatici e il download passa dal sito. Per includerlo: salvare "
               "l'xlsx in raccolta/idrogeno/iea/ oppure impostare IEA_H2_DB_URL.")
        return None
    try:
        riassunto = riassumi_iea(_xlsx_righe(dati))
    except Exception as e:  # noqa: BLE001
        avviso(f"IEA database: lettura xlsx fallita ({e})")
        return None
    if not riassunto:
        avviso("IEA database: intestazioni Country/Status non trovate nel file")
        return None
    riassunto.update({"origine": origine, "licenza": "CC BY 4.0 (IEA)"})
    return riassunto


# ---------------------------------------------------------------- sintesi
def sintesi(punti):
    out = {"per_stato": {}, "per_categoria": {}, "mw_per_stato_nord_europa": {}, "mw_per_stato_italia": {}}
    for p in punti:
        out["per_stato"][p["stato"]] = out["per_stato"].get(p["stato"], 0) + 1
        out["per_categoria"][p["categoria"]] = out["per_categoria"].get(p["categoria"], 0) + 1
        if p["categoria"] == "elettrolizzatore" and isinstance(p.get("mw"), (int, float)):
            chiave = ("mw_per_stato_nord_europa" if p["paese"] in FOCUS_NORD else
                      "mw_per_stato_italia" if p["paese"] in FOCUS_IT else None)
            if chiave:
                out[chiave][p["stato"]] = round(out[chiave].get(p["stato"], 0) + p["mw"], 1)
    out["nota"] = ("Somme dei soli progetti curati in questo file (non e' un censimento): servono a "
                   "confrontare cio' che gira, cio' che si costruisce e cio' che resta sulla carta.")
    return out


def main():
    progetti = carica("progetti.json")["progetti"]
    linee = carica("pipeline.json")["pipeline"]
    realta = carica("realta.json")
    realta.pop("_nota", None)

    punti, ids = [], set()
    for p in progetti:
        probl = valida_punto(p)
        if p.get("id") in ids:
            probl.append("id duplicato")
        ids.add(p.get("id"))
        if probl:
            avviso(f"progetto {p.get('id')} scartato: {', '.join(probl)}")
            continue
        q = dict(p)
        q["lat"], q["lon"] = round(q["lat"], 4), round(q["lon"], 4)
        q["focus"] = ("nord-europa" if q["paese"] in FOCUS_NORD else "italia" if q["paese"] in FOCUS_IT
                      else "esportatori-e-altri")
        punti.append(q)

    pipeline = []
    for l in linee:
        probl = valida_linea(l)
        if probl:
            avviso(f"pipeline {l.get('id')} scartata: {', '.join(probl)}")
            continue
        q = dict(l)
        q["g"] = [[[round(x, 4), round(y, 4)] for x, y in parte] for parte in l["g"]]
        q["tracciato"] = "schematico"
        pipeline.append(q)

    collegamenti = {
        "rete_elettrica": collega_rete(punti),
        "eolico_offshore": collega_offshore(punti),
        "gas": ttf_e_grigio(),
        "fueleu": "vedi realta.marittimo.fueleu",
    }
    iea = database_iea()
    if iea:
        realta["iea_database"] = iea
    realta["sintesi_progetti"] = sintesi(punti)

    fonti = [
        {"nome": "Voci curate (comunicati, porti, stampa specializzata): fonte e link per ogni voce",
         "link": "raccolta/idrogeno/progetti.json", "licenza": "fatti citati con fonte", "data_dato": "2021-2026"},
        {"nome": "IEA, Northwest European Hydrogen Monitor 2025",
         "link": "https://iea.blob.core.windows.net/assets/e77d3543-065d-49d8-b74c-e6a0283281ee/NorthwestEuropeanHydrogenMonitor2025.pdf",
         "licenza": "CC BY 4.0", "data_dato": "2025"},
        {"nome": "IEA, Global Hydrogen Review 2025",
         "link": "https://iea.blob.core.windows.net/assets/a6c466dd-b6f0-44bd-a60a-6940eccfb1c3/GlobalHydrogenReview2025.pdf",
         "licenza": "CC BY 4.0", "data_dato": "2025-09"},
        {"nome": "IEA Hydrogen Production and Infrastructure Projects Database",
         "link": "https://www.iea.org/data-and-statistics/data-product/hydrogen-production-and-infrastructure-projects-database",
         "licenza": "CC BY 4.0", "data_dato": "usato" if iea else "non scaricabile in automatico"},
        {"nome": "FNB Gas (Kernnetz), Energinet (DHB1), Port of Rotterdam, Commissione europea (EHB, FuelEU)",
         "link": "https://eur-lex.europa.eu/eli/reg/2023/1805/oj", "licenza": "fonti pubbliche", "data_dato": "2025-2026"},
    ]
    out = {
        "aggiornato": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": fonti,
        "nota": ("Idrogeno e derivati (ammoniaca, metanolo) nei porti del Nord Europa, in Italia e nei grandi esportatori. "
                 "Punti = progetti con stato (operativo, in costruzione, FID, sviluppo pre-FID, annunciato, sospeso, cancellato); "
                 "'precisione_coord' indica se il punto e' il sito, l'area o solo la regione. 'pipeline' = gasdotti H2 con "
                 "tracciato SCHEMATICO. 'realta' = obiettivi UE vs capacita' reale, costi, aste, cancellazioni, FuelEU/IMO. "
                 "Ogni numero ha fonte e data; le stime sono marcate tipo='stima'."),
        "elementi": punti,
        "pipeline": pipeline,
        "realta": realta,
        "collegamenti": collegamenti,
        "errori": errori,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    kb = os.path.getsize(OUT) / 1024
    print(f"Scritto {os.path.relpath(OUT, RADICE)}: {len(punti)} progetti, {len(pipeline)} gasdotti, "
          f"{len(errori)} avvisi, {kb:.0f} KB")
    if kb > 1500:
        print("ATTENZIONE: file oltre 1,5 MB", file=sys.stderr)


if __name__ == "__main__":
    main()
