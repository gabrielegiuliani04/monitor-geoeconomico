#!/usr/bin/env python3
"""Agente BUNKER, CARBURANTI NAVALI ED EMISSIONI (EU ETS marittimo, FuelEU Maritime, IMO).

Produce: docs/data/bunker-emissioni.json

Fonti automatiche (ogni esecuzione):
  - Ship & Bunker, pagine prezzi pubbliche per porto: la pagina contiene la serie giornaliera
    (oggetto PORT_CHART) di VLSFO, HSFO (IFO380), MGO/LSMGO, GNL, biocarburanti. Alcuni porti
    (Genova, Algeciras, Amburgo, Malta, Port Said) sono solo per abbonati: lo script lo segnala.
  - Ship & Bunker, pagina EUA: prezzo EUA in euro e costo EUA per tonnellata di carburante.
  - EEX, risultati delle aste primarie EUA (file xlsx pubblico, un file per anno).
  - MPA Singapore via data.gov.sg: vendite mensili di bunker (totale e per tipo). Chiave facoltativa
    in DATAGOVSG_API_KEY (senza chiave funziona, con limiti di frequenza).
  - Port of Rotterdam: controlla se sulla pagina bunkering c'e' un PDF delle vendite piu' recente di
    quello trascritto in raccolta/bunker/volumi.json (il PDF non si legge con la sola libreria standard).
  - docs/data/prezzi.json (gia' nel repository): Brent, EUR/USD, TTF per i confronti.

Voci curate a mano (raccolta/bunker/*.json): regole.json, volumi.json, ops.json, esempi.json, hub.json.

Uso:  python3 raccolta/bunker/raccogli.py      (dalla radice del repository). Solo libreria standard.
"""
import datetime as dt
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
OUT = os.path.join(RADICE, "docs", "data", "bunker-emissioni.json")
PREZZI = os.path.join(RADICE, "docs", "data", "prezzi.json")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) monitor-osint bunker; uso personale non commerciale"}
SB = "https://shipandbunker.com/prices/"
EEX = "https://public.eex-group.com/eex/eua-auction-report/emission-spot-primary-market-auction-report-{anno}-data.xlsx"
DGS = "https://data.gov.sg/api/action/datastore_search"
SG_TOT = "d_89d2874dad74a273270369334f1e7d28"
SG_TIPO = "d_4f5abbf4486bf8e52bbed3be56dde562"
ROTT_PAGINA = "https://www.portofrotterdam.com/en/sea-shipping/bunkering-in-rotterdam"
BBL_PER_T = 7.53  # conversione usata da Ship & Bunker per il Brent in USD/t

ADESSO = dt.datetime.now(dt.timezone.utc)
STAMP = ADESSO.strftime("%Y-%m-%dT%H:%MZ")
OGGI = ADESSO.date()
errori = []


def avviso(msg):
    print("AVVISO:", msg, file=sys.stderr)
    errori.append(msg)


def scarica(url, binario=False, intestazioni=None, tentativi=3):
    h = dict(UA)
    h.update(intestazioni or {})
    for i in range(tentativi):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r:
                dati = r.read()
                return dati if binario else dati.decode("utf-8", "replace")
        except Exception as e:  # rete, 4xx/5xx
            ultimo = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"{url}: {ultimo}")


def carica(nome):
    with open(os.path.join(QUI, nome), encoding="utf-8") as f:
        return json.load(f)


def giorno(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).date()


def r2(x, n=2):
    return None if x is None else round(x, n)


# ---------------------------------------------------------------- Ship & Bunker
GRADI = {"VLSFO": "VLSFO", "IFO380": "HSFO", "MGO": "MGO", "LSMGO": "LSMGO", "LNG": "GNL",
         "LNG-380e": "GNL_equiv_HSFO", "LNG-MGOe": "GNL_equiv_MGO", "BIO": "bio_blend",
         "SS": "scrubber_spread", "MEOH": "metanolo", "MEOHVLSF": "metanolo_equiv_VLSFO",
         "EUA": "EUA_eur", "EUA-USD": "EUA_usd", "EUAVLSFO": "EUA_per_t_VLSFO_usd",
         "EUAMGO": "EUA_per_t_MGO_usd", "EUAHFO": "EUA_per_t_HSFO_usd"}
SERIE_SALVATE = {"VLSFO", "HSFO", "MGO", "GNL", "EUA_eur", "EUA_per_t_VLSFO_usd"}


def valore_al(serie, data):
    """Ultimo valore con data <= data (serie [[date, v], ...] ordinata)."""
    out = None
    for d, v in serie:
        if d <= data:
            out = (d, v)
        else:
            break
    return out


def settimanale(serie, giorni=400):
    """Ultima osservazione di ogni settimana ISO negli ultimi `giorni` giorni."""
    lim = OGGI - dt.timedelta(days=giorni)
    sett = {}
    for d, v in serie:
        if d >= lim:
            sett[d.isocalendar()[:2]] = (d, v)
    return [[d.isoformat(), v] for d, v in sorted(sett.values())]


def sintesi(serie, prima_guerra):
    d, v = serie[-1]
    out = {"ultimo": v, "data": d.isoformat()}
    for chiave, rif in (("var_1s_pct", d - dt.timedelta(days=7)), ("var_1a_pct", d - dt.timedelta(days=365)),
                        ("var_da_prima_guerra_pct", prima_guerra)):
        p = valore_al(serie, rif)
        out[chiave] = r2((v / p[1] - 1) * 100, 1) if p and p[1] else None
        if chiave == "var_da_prima_guerra_pct" and p:
            out["valore_prima_guerra"] = p[1]
            out["data_prima_guerra"] = p[0].isoformat()
    anno = [x for x in serie if x[0].year == d.year]
    if anno:
        mx = max(anno, key=lambda x: x[1])
        out["massimo_anno"] = [mx[0].isoformat(), mx[1]]
    return out


def leggi_sb(percorso, prima_guerra):
    url = SB + percorso
    html = scarica(url)
    m = re.search(r"const PORT_CHART\s*=\s*(\{.*?\});", html, flags=re.S)
    if not m:
        if "Subscriber Content" in html:
            return {"stato_prezzi": "riservato agli abbonati Ship & Bunker", "link": url}
        raise RuntimeError(f"{url}: serie PORT_CHART non trovata (pagina cambiata?)")
    grezzo = json.loads(m.group(1))
    gradi, serie = {}, {}
    for k, v in grezzo.items():
        if k not in GRADI or not isinstance(v, list) or not v:
            continue
        s = sorted((giorno(p[0]), float(p[1])) for p in v if isinstance(p, list) and len(p) == 2 and p[1] is not None)
        if not s:
            continue
        nome = GRADI[k]
        gradi[nome] = sintesi(s, prima_guerra)
        if nome in SERIE_SALVATE:
            serie[nome] = settimanale(s)
    return {"stato_prezzi": "pubblico", "link": url, "gradi": gradi, "serie_settimanali": serie, "_grezze": grezzo}


# ---------------------------------------------------------------- EEX aste EUA
def leggi_xlsx(dati):
    z = zipfile.ZipFile(io.BytesIO(dati))
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode("utf-8"), flags=re.S):
            ss.append(re.sub(r"<[^>]+>", "", si))
    foglio = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
    righe = []
    for r in re.findall(r"<row[^>]*>(.*?)</row>", foglio, flags=re.S):
        celle = {}
        for c in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(.*?)</c>)', r, flags=re.S):
            col, attr, dentro = c.groups()
            v = re.search(r"<v>(.*?)</v>", dentro or "")
            v = v.group(1) if v else ""
            if 't="s"' in attr and v:
                v = ss[int(v)]
            celle[col] = v
        righe.append(celle)
    return righe


def aste_eex():
    out = []
    for anno in (OGGI.year - 1, OGGI.year):
        try:
            righe = leggi_xlsx(scarica(EEX.format(anno=anno), binario=True))
        except Exception as e:
            avviso(f"EEX aste {anno}: {e}")
            continue
        intest = next((r for r in righe if r.get("B") == "Date"), None)
        if not intest:
            avviso(f"EEX aste {anno}: intestazione non trovata")
            continue
        col = {v: k for k, v in intest.items()}
        cp, cv, cc, cn, cs, cz = (col.get("Auction Price €/tCO2"), col.get("Auction Volume tCO2"), col.get("Cover Ratio"),
                                  col.get("Auction Name"), col.get("Status"), col.get("Zone"))
        for r in righe:
            try:
                seriale = float(r.get("B", ""))
            except ValueError:
                continue
            if r.get(cs, "").lower() != "successful":
                continue
            try:
                prezzo = float(r[cp])
            except (KeyError, ValueError):
                continue
            d = dt.date(1899, 12, 30) + dt.timedelta(days=int(seriale))
            nome = r.get(cn, "")
            zona = r.get(cz, "") if cz else ""
            if not zona:  # nei file degli anni precedenti la colonna Zone puo' mancare: la ricavo dal nome
                zona = nome.split()[-1] if nome else ""
            out.append({"data": d.isoformat(), "asta": nome, "zona": zona, "prezzo_eur": prezzo,
                        "volume_t": r2(float(r[cv]), 0) if r.get(cv) else None,
                        "cover_ratio": r2(float(r[cc])) if r.get(cc) else None})
    out.sort(key=lambda x: x["data"])
    return out


# ---------------------------------------------------------------- Singapore (MPA)
def dgs(resource, **param):
    h = {}
    if os.environ.get("DATAGOVSG_API_KEY"):
        h["x-api-key"] = os.environ["DATAGOVSG_API_KEY"]
    q = {"resource_id": resource, "limit": 5000}
    q.update(param)
    j = json.loads(scarica(DGS + "?" + urllib.parse.urlencode(q), intestazioni=h))
    if not j.get("success"):
        raise RuntimeError(f"data.gov.sg {resource}: risposta non valida")
    return j["result"]["records"]


def singapore():
    rec = dgs(SG_TOT)
    mesi = sorted((r["month"], float(r["bunker_sales"])) for r in rec if r.get("bunker_sales") not in (None, "", "na"))
    ultimo_mese, ultimo_val = mesi[-1]
    anno_u = int(ultimo_mese[:4])
    n = int(ultimo_mese[5:7])
    annuali = {}
    for m, v in mesi:
        annuali.setdefault(int(m[:4]), []).append(v)
    annuali = {a: r2(sum(v), 1) for a, v in annuali.items() if len(v) == 12}
    ytd = sum(v for m, v in mesi if m.startswith(str(anno_u)) and int(m[5:7]) <= n)
    ytd_prec = sum(v for m, v in mesi if m.startswith(str(anno_u - 1)) and int(m[5:7]) <= n)
    stesso_mese_prec = dict(mesi).get(f"{anno_u - 1}-{n:02d}")
    tipo = []
    try:
        for r in dgs(SG_TIPO, filters=json.dumps({"month": ultimo_mese})):
            v = r.get("bunker_sales")
            if v not in (None, "", "na") and float(v) > 0:
                tipo.append({"tipo": r["bunker_type"], "migliaia_t": float(v)})
        tipo.sort(key=lambda x: -x["migliaia_t"])
    except Exception as e:
        avviso(f"Singapore, dettaglio per tipo: {e}")
    return {
        "porto": "Singapore", "unita": "migliaia di tonnellate (il dataset MPA dice 'tonnes' ma i valori sono in migliaia)",
        "ultimo_mese": ultimo_mese, "ultimo_valore": ultimo_val,
        "var_anno_pct": r2((ultimo_val / stesso_mese_prec - 1) * 100, 1) if stesso_mese_prec else None,
        "da_inizio_anno": r2(ytd, 1), "da_inizio_anno_anno_prima": r2(ytd_prec, 1),
        "var_da_inizio_anno_pct": r2((ytd / ytd_prec - 1) * 100, 1) if ytd_prec else None,
        "annuali": [[a, annuali[a]] for a in sorted(annuali) if a >= OGGI.year - 6],
        "mensile": [[m, v] for m, v in mesi if m >= f"{OGGI.year - 2}-01"],
        "per_tipo_ultimo_mese": tipo,
        "fonte": "Maritime and Port Authority of Singapore via data.gov.sg (Bunker Sales Total / Breakdown, Monthly)",
        "link": "https://data.gov.sg/collections/388/view", "licenza": "Singapore Open Data Licence",
        "nota": "l'ultimo mese e' una stima preliminare dell'MPA",
    }


# ---------------------------------------------------------------- Rotterdam: nuovo PDF?
def controlla_rotterdam(noto):
    html = scarica(ROTT_PAGINA)
    pdf = sorted(set(re.findall(r'/sites/default/files/(\d{4}-\d{2}/bunker-sales-20\d\d-20\d\d[^"]*\.pdf)', html)))
    if not pdf:
        return "link al PDF delle vendite non trovato sulla pagina (pagina cambiata?)"
    ultimo = pdf[-1]
    if ultimo != noto:
        return f"NUOVO PDF disponibile: https://www.portofrotterdam.com/sites/default/files/{ultimo} (trascrivere in raccolta/bunker/volumi.json)"
    return "nessun PDF piu' recente di quello trascritto"


# ---------------------------------------------------------------- calcoli
def fattori_carburante(f, reg):
    gw_e, gw_f = reg["gwp_ets_mrv"], reg["gwp_fueleu"]
    co2e_ets = f["cf_co2"] + f["cf_ch4"] * gw_e["ch4"] + f["cf_n2o"] * gw_e["n2o"]
    ttw = (f["cf_co2"] + f["cf_ch4"] * gw_f["ch4"] + f["cf_n2o"] * gw_f["n2o"]) / f["pci_MJ_per_g"]
    return co2e_ets, f["wtt_gCO2e_per_MJ"] + ttw


def limite_fueleu(anno, reg, fe):
    rid = 0
    for a, p in fe:
        if anno >= a:
            rid = p
    return reg["fueleu_riferimento_gCO2e_per_MJ"] * (1 + rid / 100)


def esempio(e, reg, fe_serie, prezzi_hub, eua, eurusd):
    f = reg["carburanti"][e["carburante"]]
    co2e_t, wtw = fattori_carburante(f, reg)
    p_usd = prezzi_hub.get(e["prezzo_hub"])
    if p_usd is None or eua is None or not eurusd:
        return {"id": e["id"], "nome": e["nome"], "errore": "manca un prezzo (bunker, EUA o cambio)"}
    p_eur = p_usd / eurusd
    t = e["consumo_t"]
    t_ets = e.get("consumo_ultima_tratta_t", t)
    anno = OGGI.year
    lim = limite_fueleu(anno, reg, fe_serie)
    passi, out = [], {"id": e["id"], "nome": e["nome"], "ipotesi": e["ipotesi_consumo"], "anno_regole": anno}
    costo_carb = t * p_eur
    passi.append(f"Carburante: {t} t x {p_usd:.1f} USD/t ({e['prezzo_hub']}) / {eurusd:.4f} USD per EUR = {costo_carb:,.0f} EUR")
    em = t_ets * co2e_t
    passi.append(f"Emissioni nella tratta coperta: {t_ets} t x {co2e_t:.4f} tCO2e/t (CO2 {f['cf_co2']} + CH4 e N2O dal 2026) = {em:,.0f} tCO2e")
    eua_n = em * e["quota_ets"] * e["fattore_phase_in"]
    costo_ets = eua_n * eua
    passi.append(f"ETS: {em:,.0f} x quota viaggio {e['quota_ets']:.0%} x phase-in {e['fattore_phase_in']:.0%} = {eua_n:,.0f} EUA x {eua:.2f} EUR = {costo_ets:,.0f} EUR")
    energia = t_ets * e["quota_fueleu"] * f["pci_MJ_per_g"] * 1e6
    deficit = (wtw - lim) * energia  # gCO2e (positivo = deficit)
    pen = max(deficit, 0) / (wtw * reg["fueleu_MJ_per_t_vlsfo_eq"]) * reg["fueleu_penale_eur_per_t_vlsfo_eq"]
    passi.append(f"FuelEU: intensita' WtW del carburante {wtw:.2f} gCO2e/MJ contro limite {anno} {lim:.2f}; energia in ambito {energia / 1e6:,.1f} TJ; "
                 f"deficit {deficit / 1e6:,.1f} tCO2e; penale = deficit / ({wtw:.2f} x 41.000 MJ) x 2.400 EUR = {pen:,.0f} EUR (tetto: pooling o carburanti bio possono costare meno)")
    tot = costo_carb + costo_ets + pen
    out.update({
        "prezzo_bunker_usd_t": p_usd, "eua_eur": eua, "eurusd": eurusd,
        "costo_carburante_eur": r2(costo_carb, 0), "costo_ets_eur": r2(costo_ets, 0), "costo_fueleu_max_eur": r2(pen, 0),
        "totale_eur": r2(tot, 0),
        "quota_ets_su_totale_pct": r2(costo_ets / tot * 100, 1), "quota_fueleu_su_totale_pct": r2(pen / tot * 100, 1),
        "ets_per_t_carburante_bruciato_eur": r2(costo_ets / t, 1), "fueleu_per_t_carburante_bruciato_eur": r2(pen / t, 1),
        "calcolo": passi,
    })
    return out


# ---------------------------------------------------------------- validazione
def valida(doc):
    probl = []
    for el in doc["elementi"]:
        for k in ("lat", "lon", "nome", "paese", "categoria", "stato", "fonte", "link", "data_fonte", "affidabilita"):
            if el.get(k) in (None, ""):
                probl.append(f"{el.get('id')}: campo {k} mancante")
        if not (-90 <= el.get("lat", 999) <= 90 and -180 <= el.get("lon", 999) <= 180):
            probl.append(f"{el.get('id')}: coordinate fuori intervallo")
        if el.get("affidabilita") not in ("alta", "media", "bassa"):
            probl.append(f"{el.get('id')}: affidabilita' non valida")
        for g, s in (el.get("prezzi") or {}).items():
            v = s.get("ultimo")
            lim = (50, 5000) if not g.startswith(("EUA", "scrubber")) else (-500, 5000)
            if v is not None and not (lim[0] <= v <= lim[1]):
                probl.append(f"{el['id']}: prezzo {g}={v} fuori dall'intervallo plausibile")
            if s.get("data") and (OGGI - dt.date.fromisoformat(s["data"])).days > 14:
                probl.append(f"{el['id']}: prezzo {g} vecchio ({s['data']})")
    eua = doc["eua"]
    for k in ("asta_ultima", "ship_and_bunker"):
        v = (eua.get(k) or {}).get("prezzo_eur")
        if v is not None and not (5 <= v <= 300):
            probl.append(f"EUA {k} = {v} fuori intervallo")
    if eua.get("asta_ultima") and eua.get("ship_and_bunker"):
        a, b = eua["asta_ultima"]["prezzo_eur"], eua["ship_and_bunker"]["prezzo_eur"]
        if abs(a / b - 1) > 0.15:
            probl.append(f"EUA: asta EEX {a} e Ship & Bunker {b} differiscono piu' del 15%")
    for e in doc["esempi_costo"]:
        if "errore" in e:
            probl.append(f"esempio {e['id']}: {e['errore']}")
    return probl


# ---------------------------------------------------------------- main
def main():
    hubcfg, reg, vol, ops, es = (carica(n) for n in ("hub.json", "regole.json", "volumi.json", "ops.json", "esempi.json"))
    prima_guerra = dt.date.fromisoformat(hubcfg["data_prima_guerra"])
    fonti = []

    # mercati gia' raccolti nel repository
    mercati = {}
    try:
        with open(PREZZI, encoding="utf-8") as f:
            for s in json.load(f)["serie"]:
                if s["id"] in ("brent", "wti", "ttf", "eurusd"):
                    mercati[s["id"]] = {"nome": s["nome"], "ultimo": s["ultimo"], "data": s["data"], "var": s.get("var")}
    except Exception as e:
        avviso(f"prezzi.json non leggibile: {e}")
    eurusd = (mercati.get("eurusd") or {}).get("ultimo")

    # prezzi bunker per hub
    elementi, prezzi_vlsfo, fonte_sb_data = [], {}, None
    for h in hubcfg["hub"]:
        try:
            r = leggi_sb(h["sb"], prima_guerra)
        except Exception as e:
            avviso(f"Ship & Bunker {h['nome']}: {e}")
            r = {"stato_prezzi": "errore di lettura", "link": SB + h["sb"]}
        r.pop("_grezze", None)
        g = r.get("gradi", {})
        if "VLSFO" in g:
            prezzi_vlsfo[h["id"]] = g["VLSFO"]["ultimo"]
            fonte_sb_data = max(fonte_sb_data or "", g["VLSFO"]["data"])
        note = []
        if "VLSFO" in g and "HSFO" in g:
            note.append(f"VLSFO {g['VLSFO']['ultimo']:.1f} e HSFO {g['HSFO']['ultimo']:.1f} USD/t al {g['VLSFO']['data']}")
        if g.get("VLSFO", {}).get("var_da_prima_guerra_pct") is not None:
            note.append(f"VLSFO {g['VLSFO']['var_da_prima_guerra_pct']:+.1f}% dal {g['VLSFO']['data_prima_guerra']} (prima della guerra)")
        if r["stato_prezzi"] != "pubblico":
            note.append("prezzi: " + r["stato_prezzi"])
        elementi.append({
            "id": "hub-" + h["id"], "tipo": "hub_bunker", "nome": h["nome"], "paese": h["paese"], "lat": h["lat"], "lon": h["lon"],
            "categoria": "hub del bunkeraggio", "stato": r["stato_prezzi"], "focus": h.get("focus", False),
            "fonte": "Ship & Bunker (pagina prezzi del porto)", "link": r["link"],
            "data_fonte": g.get("VLSFO", {}).get("data") or OGGI.isoformat(),
            "affidabilita": "media" if g else "bassa",
            "unita": "USD per tonnellata metrica (EUA in EUR/USD per quota)",
            "prezzi": g, "serie_settimanali": r.get("serie_settimanali", {}), "note": "; ".join(note)})
    fonti.append({"nome": "Ship & Bunker, prezzi bunker per porto (serie della pagina pubblica)", "link": SB,
                  "licenza": "© Ship & Bunker: pagine pubbliche, valori citati con la fonte; si salva solo una serie settimanale di 13 mesi",
                  "data_dato": fonte_sb_data})

    # volumi: Singapore automatico, Rotterdam e Fujairah curati
    volumi = {"singapore": None, "rotterdam": vol["rotterdam"], "fujairah": vol["fujairah"], "mancanti": vol["mancanti"]}
    try:
        volumi["singapore"] = singapore()
        fonti.append({"nome": "MPA Singapore via data.gov.sg", "link": "https://data.gov.sg/collections/388/view",
                      "licenza": "Singapore Open Data Licence", "data_dato": volumi["singapore"]["ultimo_mese"]})
    except Exception as e:
        avviso(f"Singapore data.gov.sg: {e}; uso il valore di riserva")
        volumi["singapore"] = vol["singapore_riserva"]
    try:
        volumi["rotterdam"]["controllo_nuovo_pdf"] = controlla_rotterdam(vol["rotterdam"]["file_pdf_noto"])
    except Exception as e:
        avviso(f"Rotterdam pagina bunkering: {e}")
    rt = {q["periodo"]: q for q in vol["rotterdam"]["trimestri"]}
    def tot(p):
        q = rt.get(p)
        return q["fossili_t"] + q["bio_t"] if q else None
    a9 = sum(tot(f"{OGGI.year}-T{i}") or 0 for i in (1, 2, 3))
    b9 = sum(tot(f"{OGGI.year - 1}-T{i}") or 0 for i in (1, 2, 3))
    volumi["rotterdam"]["calcolato"] = {
        "totale_2025_t": tot("2025"), "primi_9_mesi_t": {str(OGGI.year): a9, str(OGGI.year - 1): b9},
        "var_9_mesi_pct": r2((a9 / b9 - 1) * 100, 1) if a9 and b9 else None,
        "nota": "fossili + bio-miscele, GNL incluso con densita' 0,45 t/m3 come nella tabella del porto"}
    fonti.append({"nome": "Port of Rotterdam, bunker sales 2024-2026", "link": vol["rotterdam"]["link"],
                  "licenza": vol["rotterdam"]["licenza"], "data_dato": vol["rotterdam"]["data_fonte"]})
    fonti.append({"nome": "FOIZ / S&P Global (Fujairah) via Ship & Bunker ed Engine", "link": vol["fujairah"]["mensile"][-1]["link"],
                  "licenza": "valori citati da articoli di stampa", "data_dato": vol["fujairah"]["mensile"][-1]["data_fonte"]})
    sg = volumi["singapore"]
    for el in elementi:
        if el["id"] == "hub-singapore" and sg.get("ultimo_mese"):
            el["volume_ultimo_mese_kt"] = [sg["ultimo_mese"], sg["ultimo_valore"]]
            el["note"] += f"; venduti {sg['ultimo_valore']:,.0f} mila t a {sg['ultimo_mese']} (MPA)"
        if el["id"] == "hub-rotterdam":
            el["volume_9_mesi_t"] = [str(OGGI.year), a9]
            el["note"] += f"; venduti {a9 / 1e6:.2f} milioni di t nei primi 9 mesi del {OGGI.year} ({volumi['rotterdam']['calcolato']['var_9_mesi_pct']:+.1f}%)"
        if el["id"] == "hub-fujairah":
            u = vol["fujairah"]["mensile"][-1]
            el["volume_ultimo_mese"] = [u["mese"], u["valore"], u["unita"]]
            el["note"] += f"; venduti {u['valore']:,} {u['unita']} a {u['mese']} (FOIZ); gen-ago 2026 -57,3% sul 2025"

    # EUA
    eua = {"nota": "Prezzo della quota UE di emissione (1 EUA = 1 tCO2e)."}
    try:
        sbe = leggi_sb("port/EU-EUA", prima_guerra)
        sbe.pop("_grezze", None)
        g = sbe.get("gradi", {})
        if "EUA_eur" in g:
            eua["ship_and_bunker"] = {"prezzo_eur": g["EUA_eur"]["ultimo"], "data": g["EUA_eur"]["data"],
                                      "var_1a_pct": g["EUA_eur"].get("var_1a_pct"),
                                      "costo_EUA_per_t_VLSFO_usd": g.get("EUA_per_t_VLSFO_usd", {}).get("ultimo"),
                                      "costo_EUA_per_t_MGO_usd": g.get("EUA_per_t_MGO_usd", {}).get("ultimo"),
                                      "serie_settimanale": sbe["serie_settimanali"].get("EUA_eur"), "link": sbe["link"]}
    except Exception as e:
        avviso(f"Ship & Bunker EUA: {e}")
    try:
        aste = aste_eex()
        ue = [a for a in aste if a["zona"] == "EU"] or aste
        if ue:
            u = ue[-1]
            un_anno = valore_al([(dt.date.fromisoformat(a["data"]), a["prezzo_eur"]) for a in ue], dt.date.fromisoformat(u["data"]) - dt.timedelta(days=365))
            eua["asta_ultima"] = dict(u, var_1a_pct=r2((u["prezzo_eur"] / un_anno[1] - 1) * 100, 1) if un_anno else None)
            eua["aste_serie"] = [[a["data"], a["prezzo_eur"]] for a in ue if a["data"] >= (OGGI - dt.timedelta(days=400)).isoformat()]
            anno = [a["prezzo_eur"] for a in ue if a["data"].startswith(str(OGGI.year))]
            eua["media_aste_anno"] = r2(sum(anno) / len(anno)) if anno else None
            fonti.append({"nome": "EEX, risultati delle aste primarie EUA", "link": EEX.format(anno=OGGI.year),
                          "licenza": "dati pubblici EEX, citare la fonte", "data_dato": u["data"]})
    except Exception as e:
        avviso(f"EEX: {e}")
    eua_prezzo = (eua.get("asta_ultima") or {}).get("prezzo_eur") or (eua.get("ship_and_bunker") or {}).get("prezzo_eur")
    eua["usato_negli_esempi_eur"] = eua_prezzo

    # esempi di costo
    fe_serie = next(v["serie"] for v in reg["fueleu_maritime"]["voci"] if "serie" in v)
    esempi = [esempio(e, reg["fattori"], fe_serie, prezzi_vlsfo, eua_prezzo, eurusd) for e in es["esempi"]]
    for e in esempi:
        if e["id"] == "deviazione-tanger":
            base = next((x for x in esempi if x["id"] == "asia-rotterdam"), None)
            if base and "costo_ets_eur" in base and "costo_ets_eur" in e:
                e["risparmio_rispetto_al_primo_esempio_eur"] = r2(base["costo_ets_eur"] + base["costo_fueleu_max_eur"] - e["costo_ets_eur"] - e["costo_fueleu_max_eur"], 0)
    sovrapprezzo = {
        "nome": "Maersk Emissions Surcharge (EMS/ESS), ETS + FuelEU, 4o trimestre 2026",
        "valori_usd_per_feu": {"Estremo Oriente -> Nord Europa": 170, "Nord Europa -> Estremo Oriente": 114,
                               "Estremo Oriente -> Mediterraneo": 131, "Mediterraneo -> Nord Europa": 93, "Intra Nord Europa": 31},
        "eua_medio_usato_eur": 78.97, "periodo_eua": "16 maggio - 15 agosto 2026 (ICE EUA Daily Futures)",
        "link": "https://www.maersk.com/news/articles/2026/09/01/emissions-surcharge-ems-ess", "data_fonte": "2026-09-01",
        "nota": "e' cio' che il vettore fa pagare ai caricatori, non il suo costo: utile come indicatore del costo ETS+FuelEU per container"}
    wci = None
    try:
        with open(os.path.join(RADICE, "docs", "data", "noli.json"), encoding="utf-8") as f:
            for n in json.load(f)["elementi"]:
                if n["id"] == "wci":
                    wci = {"valore": n["rotte"].get("Shanghai-Rotterdam"), "data": n["data"]}
    except Exception as e:
        avviso(f"noli.json non leggibile: {e}")
    if wci and wci["valore"]:
        sovrapprezzo["confronto_nolo"] = {"wci_shanghai_rotterdam_usd_feu": wci["valore"], "data": wci["data"],
                                          "quota_pct": r2(170 / wci["valore"] * 100, 1)}

    # confronti di mercato
    confronti = {}
    br = (mercati.get("brent") or {}).get("ultimo")
    if br:
        confronti["brent_usd_t"] = r2(br * BBL_PER_T, 1)
        for hid in ("rotterdam", "singapore", "fujairah"):
            if hid in prezzi_vlsfo:
                confronti[f"premio_vlsfo_{hid}_su_brent_usd_t"] = r2(prezzi_vlsfo[hid] - br * BBL_PER_T, 1)
    if "fujairah" in prezzi_vlsfo and "singapore" in prezzi_vlsfo:
        confronti["fujairah_meno_singapore_vlsfo_usd_t"] = r2(prezzi_vlsfo["fujairah"] - prezzi_vlsfo["singapore"], 1)
    if "rotterdam" in prezzi_vlsfo and "anversa" in prezzi_vlsfo:
        confronti["rotterdam_meno_anversa_vlsfo_usd_t"] = r2(prezzi_vlsfo["rotterdam"] - prezzi_vlsfo["anversa"], 1)

    # punti OPS e porti di trasbordo
    for p in ops["porti"]:
        elementi.append({"id": p["id"], "tipo": "porto_ops", "nome": p["nome"], "paese": p["paese"], "lat": p["lat"], "lon": p["lon"],
                         "categoria": "elettrificazione banchine e carburanti alternativi", "stato": p["stato"],
                         "fonte": p["fonti"][0]["nome"], "link": p["fonti"][0]["link"], "fonti": p["fonti"],
                         "data_fonte": p["fonti"][0]["data_fonte"], "affidabilita": p["affidabilita"],
                         "note": p["ops"], "carburanti_alternativi": p["carburanti_alternativi"]})
    for p in ops["trasbordo_extra_ue"]:
        elementi.append({"id": p["id"], "tipo": "porto_trasbordo_extra_ue", "nome": p["nome"], "paese": p["paese"], "lat": p["lat"], "lon": p["lon"],
                         "categoria": "porto di trasbordo vicino (rischio di elusione ETS)", "stato": p["stato"],
                         "fonte": "Commissione europea, Regolamento di esecuzione (UE) 2023/2297", "link": p["link"],
                         "data_fonte": p["data_fonte"], "affidabilita": "alta",
                         "note": "Una sosta qui non interrompe il viaggio ai fini ETS/FuelEU: conta il porto extra UE precedente."})
    fonti += [
        {"nome": "EUR-Lex: Direttiva (UE) 2023/959, Regolamento (UE) 2023/1805, Reg. esec. 2023/2297 e 2025/1127", "link": "https://eur-lex.europa.eu/",
         "licenza": "© Unione europea, riuso consentito con citazione", "data_dato": "2025-06-06"},
        {"nome": "Commissione europea, FAQ ETS marittimo", "link": reg["eu_ets_marittimo"]["link"], "licenza": "© Unione europea", "data_dato": OGGI.isoformat()},
        {"nome": "IMO, resoconti MEPC 83, MEPC/ES.2, MEPC 84, ISWG-GHG 22, anteprima MEPC 85", "link": "https://www.imo.org/en/MediaCentre/MeetingSummaries/Pages/MEPC-default.aspx",
         "licenza": "© IMO, citazione", "data_dato": "2026-09-04"},
        {"nome": "Interreg BREEZE, analisi OPS (aprile 2026)", "link": "https://www.interregeurope.eu/sites/default/files/2026-04/OPS%20Analysis%20BREEZE.pdf",
         "licenza": "documento pubblico Interreg Europe", "data_dato": "2025-09"},
        {"nome": "Maersk, Emissions surcharge Q4 2026", "link": sovrapprezzo["link"], "licenza": "pagina pubblica", "data_dato": "2026-09-01"},
    ]

    doc = {
        "aggiornato": STAMP, "fonti": fonti,
        "nota": ("Bunker, carburanti navali ed emissioni. Prezzi in USD per tonnellata (Ship & Bunker, chiusura del giorno di borsa precedente); "
                 "EUA in euro (asta EEX piu' recente e Ship & Bunker). Volumi: Singapore automatico (MPA), Rotterdam e Fujairah trascritti dalle fonti. "
                 "Regole ETS/FuelEU/IMO e stato OPS curati a mano con link ai testi. Gli esempi di costo usano consumi IPOTETICI dichiarati "
                 "e i prezzi del giorno: sono un ordine di grandezza, non il costo di una nave reale."),
        "data_prima_guerra": hubcfg["data_prima_guerra"],
        "elementi": elementi,
        "eua": eua,
        "mercati": mercati,
        "confronti": confronti,
        "volumi": volumi,
        "regole": {k: reg[k] for k in ("eu_ets_marittimo", "fueleu_maritime", "afir_porti", "imo")},
        "fattori": reg["fattori"],
        "esempi_costo": esempi,
        "sovrapprezzo_vettori": sovrapprezzo,
        "candidati_porti_trasbordo": ops["candidati_citati_nella_revisione_2026"],
        "errori": errori,
    }
    doc["validazione"] = valida(doc)
    for p in doc["validazione"]:
        print("VALIDAZIONE:", p, file=sys.stderr)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    print(f"scritto {OUT}: {len(elementi)} punti, {os.path.getsize(OUT) / 1024:.0f} KB, {len(errori)} errori, {len(doc['validazione'])} avvisi di validazione")


if __name__ == "__main__":
    main()
