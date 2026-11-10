#!/usr/bin/env python3
"""Impatti in Italia: carburanti, accise, bollette, inflazione, autotrasporto, scenari.

Scrive docs/data/italia-impatti.json. Solo libreria standard di Python 3.

Cosa si aggiorna da solo (fonti pubbliche, nessuna chiave):
  - prezzi settimanali di benzina e gasolio con accise, IVA e prezzo netto (MASE, DGSAIE)
  - prezzi medi giornalieri self (open data Mimit, prezzo_alle_8.csv): media calcolata qui
  - PUN e prezzo del gas MGP del GME (API della home page del sito GME)
  - inflazione NIC (Istat SDMX) e HICP per voce (Eurostat), pesi HICP
  - fiducia dei consumatori (Istat SDMX)
  - Brent, TTF ed euro/dollaro (Yahoo Finance) per stimare i coefficienti di trasmissione
  - scioperi nei trasporti dal calendario del MIT (se raggiungibile)
Cosa è curato a mano e qui solo validato: raccolta/italia/*.json
  (precedenti, autotrasporto, misure, scioperi di riserva, ARERA, letteratura, scenari, vendite mensili MASE).

Uso:  python3 raccolta/italia/raccogli.py            (scarica e scrive)
      python3 raccolta/italia/raccogli.py --valida   (controlla solo i file curati)
"""
import csv
import datetime as dt
import http.cookiejar
import io
import json
import os
import re
import statistics as st
import sys
import time
import urllib.parse
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
USCITA = os.path.join(RADICE, "docs", "data", "italia-impatti.json")
SIMULATORE = os.path.join(RADICE, "docs", "data", "simulatore.json")
PREZZI = os.path.join(RADICE, "docs", "data", "prezzi.json")
UA = {"User-Agent": "Mozilla/5.0 (monitor-osint italia)"}
OGGI = dt.date.today()
INIZIO_SERIE = "2022-01-01"
IVA = 0.22
LITRI_BARILE = 158.987
KWH_SMC = 10.57275  # stesso potere calorifico di gas-italia.json / simulatore.json

errori = []
avvisi = []
fonti = []


# ---------------------------------------------------------------- utilità
def scarica(url, intestazioni=None, tentativi=3, timeout=90, opener=None):
    h = dict(UA)
    h.update(intestazioni or {})
    ultimo = None
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers=h)
            f = (opener.open if opener else urllib.request.urlopen)(req, timeout=timeout)
            return f.read()
        except Exception as e:  # rete, HTTP, TLS
            ultimo = e
            time.sleep(2 + 3 * i)
    raise RuntimeError("%s: %s" % (url, ultimo))


def num_it(s):
    """'1.234,56' -> 1234.56 ; '' -> None."""
    s = (s or "").strip()
    if not s:
        return None
    return float(s.replace(".", "").replace(",", "."))


def r(x, n=3):
    return None if x is None else round(x, n)


def ols(x, y):
    mx, my = st.mean(x), st.mean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sxx
    a = my - b * mx
    sst = sum((c - my) ** 2 for c in y)
    r2 = 1 - sum((c - a - b * q) ** 2 for q, c in zip(x, y)) / sst if sst else None
    return a, b, r2


def fonte(nome, link, licenza, data_dato, nota=None):
    d = {"nome": nome, "link": link, "licenza": licenza, "data_dato": data_dato}
    if nota:
        d["nota"] = nota
    fonti.append(d)


def leggi_json(p, predefinito=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return predefinito


# ---------------------------------------------------------------- MASE settimanale
def mase_settimanale():
    url = "https://sisen.mase.gov.it/dgsaie/api/v1/weekly-prices/report/export?type=ALL&format=CSV&lang=it"
    testo = scarica(url).decode("latin-1")
    righe = list(csv.DictReader(io.StringIO(testo)))
    W = {}
    for x in righe:
        d = x["DATA_RILEVAZIONE"]
        W.setdefault(d, {})[x["CODICE_PRODOTTO"]] = {
            "prezzo": num_it(x["PREZZO"]), "accisa": num_it(x["ACCISA"]),
            "iva": num_it(x["IVA"]), "netto": num_it(x["NETTO"])}
    date = sorted(W)
    fonte("MASE, DGSAIE: prezzi medi settimanali dei carburanti (tutti i dati: prezzo, accisa, IVA, netto)",
          "https://sisen.mase.gov.it/dgsaie/prezzi-settimanali-carburanti",
          "dati pubblici MASE, riuso citando la fonte", date[-1],
          "€/1000 litri nel file originale, qui €/litro. Media nazionale settimanale (base del Weekly Oil Bulletin UE); il file non distingue self e servito.")
    return W, date


# ---------------------------------------------------------------- Mimit giornaliero
def mimit_giornaliero():
    url = "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
    testo = scarica(url, timeout=120).decode("utf-8", "replace")
    righe = testo.splitlines()
    m = re.search(r"(\d{4}-\d{2}-\d{2})", righe[0])
    data = m.group(1) if m else OGGI.isoformat()
    sep = "|" if righe[1].count("|") > righe[1].count(";") else ";"
    testa = [c.strip() for c in righe[1].split(sep)]
    i_c, i_p, i_s, i_d = (testa.index(k) for k in ("descCarburante", "prezzo", "isSelf", "dtComu"))
    valori = {"Benzina": [], "Gasolio": []}
    limite = dt.datetime.strptime(data, "%Y-%m-%d") - dt.timedelta(days=7)
    for riga in righe[2:]:
        c = riga.split(sep)
        if len(c) <= max(i_c, i_p, i_s, i_d):
            continue
        carb = c[i_c].strip()
        if carb not in valori or c[i_s].strip() != "1":
            continue
        try:
            p = float(c[i_p].replace(",", "."))
            quando = dt.datetime.strptime(c[i_d].strip()[:10], "%d/%m/%Y")
        except ValueError:
            continue
        if 0.8 < p < 4.0 and quando >= limite:
            valori[carb].append(p)
    out = {}
    for carb, v in valori.items():
        if len(v) < 1000:
            raise RuntimeError("Mimit: troppo pochi prezzi self per %s (%d)" % (carb, len(v)))
        v.sort()
        k = len(v) // 20  # media troncata al 5% per parte
        out[carb.lower()] = {"media_troncata": round(st.mean(v[k:len(v) - k]), 3),
                             "mediana": round(st.median(v), 3), "n_impianti": len(v)}
    fonte("Mimit, open data prezzi dei carburanti (prezzo_alle_8.csv)",
          "https://www.mimit.gov.it/it/open-data/elenco-dataset/carburanti-prezzi-praticati-e-anagrafica-degli-impianti",
          "IODL 2.0", data,
          "Media calcolata dall'osservatorio: prezzi self di Benzina e Gasolio comunicati negli ultimi 7 giorni, media troncata al 5%. Non è la media ufficiale pubblicata dal Mimit.")
    return data, out


# ---------------------------------------------------------------- Yahoo
def yahoo(simbolo, da="2021-01-01"):
    p1 = int(dt.datetime.strptime(da, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp())
    p2 = int(time.time()) + 86400
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?period1=%d&period2=%d&interval=1d" % (
        urllib.parse.quote(simbolo), p1, p2)
    d = json.loads(scarica(url))["chart"]["result"][0]
    out = {}
    for t, c in zip(d["timestamp"], d["indicators"]["quote"][0]["close"]):
        if c is not None:
            out[dt.datetime.fromtimestamp(t, dt.timezone.utc).date()] = c
    return out


def media_settimana_prima(serie, giorno, giorni=7):
    v = [serie[giorno - dt.timedelta(k)] for k in range(1, giorni + 1) if giorno - dt.timedelta(k) in serie]
    return st.mean(v) if v else None


# ---------------------------------------------------------------- GME
def gme():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    pagina = scarica("https://www.mercatoelettrico.org/it-it/", opener=op).decode("utf-8", "replace")
    tok = re.search(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"', pagina)
    mid = re.search(r'ModuleId":(\d+)', pagina)
    tid = re.search(r'TabId":(\d+)', pagina)
    if not (tok and mid and tid):
        raise RuntimeError("GME: token o ModuleId non trovati nella pagina")
    h = {"ModuleId": mid.group(1), "TabId": tid.group(1), "RequestVerificationToken": tok.group(1)}
    base = "https://www.mercatoelettrico.org/DesktopModules/GmeCardTabellaGrafico/API/item/"
    mgp = json.loads(scarica(base + "GetMGPGraficoHP", h, opener=op))
    gas = json.loads(scarica(base + "GetMGASGraficoHP", h, opener=op))
    annuale, mensile, giornaliero = [], [], []
    for x in mgp:
        g, d = x.get("granularita"), str(x.get("data"))
        if g == "T":
            annuale.append([d, r(x["pun"], 2)])
        elif g == "A" and len(d) == 6:
            mensile.append([d[:4] + "-" + d[4:], r(x["pun"], 2)])
        elif g == "M" and len(d) == 8:
            giornaliero.append(["%s-%s-%s" % (d[:4], d[4:6], d[6:]), r(x["pun"], 2)])
    gas_g = [["%s-%s-%s" % (str(x["dataFlusso"])[:4], str(x["dataFlusso"])[4:6], str(x["dataFlusso"])[6:]),
              r(x.get("prezzoMedioContinuo"), 2)] for x in gas.get("mgp", []) if x.get("dataFlusso")]
    fonte("GME, esiti del mercato elettrico (PUN Index GME) e del mercato del gas MGP-GAS",
          "https://www.mercatoelettrico.org/it-it/", "dati pubblici GME, uso informativo",
          giornaliero[-1][0] if giornaliero else None,
          "Letti dall'API della home page del GME: medie annue dal 2004, medie mensili degli ultimi 13 mesi (il mese in corso è parziale), medie giornaliere degli ultimi 30 giorni. €/MWh.")
    return {"annuale": sorted(annuale), "mensile": sorted(mensile), "giornaliero": sorted(giornaliero),
            "gas_mgp_giornaliero": sorted(gas_g)}


# ---------------------------------------------------------------- Istat SDMX
def istat(flusso, chiave, da):
    url = "https://esploradati.istat.it/SDMXWS/rest/data/IT1,%s,1.0/%s?startPeriod=%s" % (flusso, chiave, da)
    t = scarica(url, timeout=180).decode("utf-8", "replace")
    out = {}
    for s in re.findall(r"<generic:Series>(.*?)</generic:Series>", t, re.S):
        k = dict(re.findall(r'id="([^"]+)" value="([^"]+)"', re.search(r"<generic:SeriesKey>(.*?)</generic:SeriesKey>", s, re.S).group(1)))
        obs = re.findall(r'TIME_PERIOD" value="([^"]+)" /><generic:ObsValue value="([^"]+)"', s)
        out[k.get("ECOICOP_2") or k.get("E_COICOP_REV_ISTAT") or k.get("DATA_TYPE")] = [[a, float(b)] for a, b in obs]
    return out


NIC_VOCI = {"00": "generale", "ENRGY": "energetici", "APENRGY": "energetici_regolamentati",
            "ENRGYXAPE": "energetici_non_regolamentati", "FOODXT": "alimentari",
            "FOODHPC": "carrello_spesa", "0451": "elettricita", "0452": "gas", "0722": "carburanti",
            "00XEFOODUNP": "componente_di_fondo"}


def inflazione_istat():
    nuovo = istat("167_745_DF_DCSP_NIC1B2025_6", "M.IT.85.7." + "+".join(NIC_VOCI), "2026-01")
    vecchio = istat("167_744_DF_DCSP_NIC1B2015_1", "M.IT.39.7.00", INIZIO_SERIE[:7])
    out = {}
    for cod, nome in NIC_VOCI.items():
        serie = list(nuovo.get(cod, []))
        if cod == "00":
            visti = {a for a, _ in serie}
            serie = [x for x in vecchio.get("00", []) if x[0] not in visti] + serie
        out[nome] = sorted(serie)
    ult = out["generale"][-1][0] if out["generale"] else None
    fonte("Istat, prezzi al consumo NIC: variazioni tendenziali (dataflow 167_745 dal 2026, 167_744 per l'indice generale 2022-2025)",
          "https://esploradati.istat.it/databrowser/", "CC BY 3.0 IT", ult,
          "Dal 2026 base 2025 ed ECOICOP 2; l'ultimo mese può essere la stima preliminare (OBS_STATUS p). Le voci di dettaglio sono disponibili da gennaio 2026: per 2022-2025 vedi le serie HICP Eurostat.")
    return out


def fiducia_istat():
    s = istat("30_264", "M.IT.COF_21_WE+COF_ECO_21_WE+COF_FUT_21_WE..TOTAL.9.99.99", INIZIO_SERIE[:7])
    out = {"clima": s.get("COF_21_WE", []), "clima_economico": s.get("COF_ECO_21_WE", []),
           "clima_futuro": s.get("COF_FUT_21_WE", [])}
    fonte("Istat, fiducia dei consumatori (dataflow 30_264, base 2021=100)", "https://esploradati.istat.it/databrowser/",
          "CC BY 3.0 IT", out["clima"][-1][0] if out["clima"] else None,
          "Serie con ADJUSTMENT=N come pubblicata nel dataflow; il comunicato Istat usa i dati destagionalizzati, che possono differire.")
    return out


# ---------------------------------------------------------------- Eurostat
def eurostat(dataset, parametri):
    q = "&".join("%s=%s" % (k, v) for k, vs in parametri.items() for v in (vs if isinstance(vs, list) else [vs]))
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/%s?%s&format=JSON&lang=EN" % (dataset, q)
    d = json.loads(scarica(url, timeout=180))
    ids, size = d["id"], d["size"]
    cat = {k: d["dimension"][k]["category"]["index"] for k in ids}
    out = {}
    for pos, val in d["value"].items():
        pos = int(pos)
        coord = {}
        for k, n in zip(reversed(ids), reversed(size)):
            coord[k] = pos % n
            pos //= n
        inv = {k: {v: kk for kk, v in cat[k].items()} for k in ids}
        c = {k: inv[k][coord[k]] for k in ids}
        out.setdefault(c["coicop18"], []).append([c["time"], val])
    return {k: sorted(v) for k, v in out.items()}, d.get("updated")


HICP_VOCI = {"TOTAL": "generale", "NRG": "energia", "FOOD": "alimentari_alcol_tabacco", "CP011": "alimentari",
             "ELC_GAS": "elettricita_gas", "CP0451": "elettricita", "CP0452": "gas", "CP0722": "carburanti",
             "SERV": "servizi", "CP074": "trasporto_merci"}


def hicp():
    tassi, agg = eurostat("prc_hicp_minr", {"geo": "IT", "unit": "RCH_A", "coicop18": list(HICP_VOCI), "sinceTimePeriod": INIZIO_SERIE[:7]})
    pesi, _ = eurostat("prc_hicp_iw", {"geo": "IT", "coicop18": ["NRG", "FUEL", "CP0451", "CP0452", "ELC_GAS", "FOOD", "CP011"], "sinceTimePeriod": "2022"})
    fonte("Eurostat, HICP ECOICOP 2 (prc_hicp_minr, variazioni annue; prc_hicp_iw, pesi)",
          "https://ec.europa.eu/eurostat/databrowser/view/prc_hicp_minr/default/table", "CC BY 4.0",
          (agg or "")[:10], "Indice armonizzato per l'Italia (calcolato da Istat). Pesi in millesimi.")
    return {HICP_VOCI[k]: v for k, v in tassi.items() if k in HICP_VOCI}, {k: dict(v) for k, v in pesi.items()}


# ---------------------------------------------------------------- MIT scioperi
def scioperi_mit():
    """Prova il calendario ufficiale del MIT. Restituisce una lista o solleva un errore."""
    trovati = []
    for url in ("https://scioperi.mit.gov.it/mit2/public/scioperi/rss",
                "https://scioperi.mit.gov.it/mit2/public/scioperi"):
        try:
            t = scarica(url, tentativi=2, timeout=60).decode("utf-8", "replace")
        except Exception as e:
            ultimo = e
            continue
        blocchi = re.findall(r"<item>(.*?)</item>", t, re.S) or re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S)
        for b in blocchi:
            testo = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", b)).strip()
            date = re.findall(r"(\d{2})/(\d{2})/(\d{4})", testo)
            if not date:
                continue
            d0 = dt.date(int(date[0][2]), int(date[0][1]), int(date[0][0]))
            d1 = dt.date(int(date[-1][2]), int(date[-1][1]), int(date[-1][0])) if len(date) > 1 else d0
            if d1 < OGGI or d0 > OGGI + dt.timedelta(days=30):
                continue
            trovati.append({"data_inizio": d0.isoformat(), "data_fine": max(d0, d1).isoformat(), "testo": testo[:400],
                            "autotrasporto": bool(re.search(r"autotrasport|merci su strada|conto terzi", testo, re.I))})
        if trovati:
            fonte("Ministero delle Infrastrutture e dei Trasporti, calendario degli scioperi", url,
                  "dati pubblici", OGGI.isoformat())
            return trovati
        ultimo = "nessuna riga con date nei prossimi 30 giorni"
    raise RuntimeError("calendario MIT non disponibile: %s" % ultimo)


# ---------------------------------------------------------------- MASE vendite: controllo novità
def controlla_vendite(curati):
    try:
        url = "https://sisen.mase.gov.it/dgsaie/api/v1/cmis/documents?folder=" + urllib.parse.quote(
            "/sg_dgsaie/consumi_petroliferi/preconsuntivi/%d/" % OGGI.year)
        lista = json.loads(scarica(url, tentativi=2))
        nomi = sorted(x["fileName"] for x in lista)
        ultimo = re.search(r"(\d{4})_(\d{2})", nomi[-1]) if nomi else None
        if ultimo:
            mese = "%s-%s" % ultimo.groups()
            noti = {e["mese"] for e in curati.get("elementi", [])}
            if mese not in noti:
                avvisi.append("MASE ha pubblicato le vendite di %s (%s): aggiornare a mano raccolta/italia/consumi_carburanti.json (file Excel, non leggibile con la libreria standard)." % (mese, nomi[-1]))
    except Exception as e:
        avvisi.append("controllo nuove vendite MASE non riuscito: %s" % e)


# ---------------------------------------------------------------- validazione dei file curati
CURATI = ["precedenti.json", "autotrasporto.json", "misure.json", "scioperi.json", "arera.json",
          "letteratura.json", "scenari.json", "consumi_carburanti.json"]
DATA_RE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")


def valida():
    dati, problemi = {}, []
    for nome in CURATI:
        p = os.path.join(QUI, nome)
        d = leggi_json(p)
        if d is None:
            problemi.append("%s: manca o non è JSON valido" % nome)
            continue
        dati[nome[:-5]] = d
        voci = d.get("elementi", [])
        if nome == "autotrasporto.json":
            voci = d.get("regole_scioperi", []) + d.get("dichiarazioni_2026", []) + d.get("peso_gasolio_sui_costi", [])
        for i, v in enumerate(voci):
            if nome == "scioperi.json":
                continue  # fonte unica a livello di file
            if nome == "consumi_carburanti.json":
                if not v.get("link"):
                    problemi.append("%s[%d]: manca il link al file MASE" % (nome, i))
                continue
            if nome == "scenari.json":
                continue
            if not (v.get("link") and (v.get("fonte") or nome == "autotrasporto.json")):
                problemi.append("%s[%d] %s: manca fonte o link" % (nome, i, v.get("id", "")))
            for campo in ("data_fonte", "data", "data_inizio", "mese"):
                if v.get(campo) and not DATA_RE.match(str(v[campo])):
                    problemi.append("%s[%d]: data non valida in %s: %s" % (nome, i, campo, v[campo]))
    sc = dati.get("scioperi", {})
    if sc:
        if not (sc.get("link_elenco") and sc.get("data_fonte")):
            problemi.append("scioperi.json: manca fonte dell'elenco")
        elif (OGGI - dt.date.fromisoformat(sc["data_fonte"])).days > 20:
            avvisi.append("scioperi.json ha più di 20 giorni: aggiornare l'elenco di riserva.")
    ar = dati.get("arera", {})
    if ar.get("elementi"):
        ult = max(e["mese"] for e in ar["elementi"])
        y, m = map(int, ult.split("-"))
        attesa = (OGGI.replace(day=1) - dt.timedelta(days=1))
        if (attesa.year, attesa.month) > (y, m) and OGGI.day > 4:
            avvisi.append("arera.json: ultimo mese %s; ARERA dovrebbe aver pubblicato %04d-%02d." % (ult, attesa.year, attesa.month))
    return dati, problemi


# ---------------------------------------------------------------- calcoli
def serie_carburanti(W, date):
    s = {k: [] for k in ("benzina", "gasolio", "benzina_netto", "gasolio_netto", "benzina_accisa", "gasolio_accisa")}
    for d in date:
        if d < INIZIO_SERIE:
            continue
        for cod, nome in (("1", "benzina"), ("2", "gasolio")):
            x = W[d].get(cod)
            if not x or x["prezzo"] is None:
                continue
            s[nome].append([d, r(x["prezzo"] / 1000, 4)])
            s[nome + "_netto"].append([d, r(x["netto"] / 1000, 4)])
            s[nome + "_accisa"].append([d, r(x["accisa"] / 1000, 4)])
    return s


def cambi_accise(W, date):
    out, prec = [], {}
    for d in date:
        if d < "2021-12-01":
            continue
        for cod, nome in (("1", "benzina"), ("2", "gasolio")):
            x = W[d].get(cod)
            if not x or x["accisa"] is None:
                continue
            if nome in prec and prec[nome] != x["accisa"]:
                out.append({"data_rilevazione": d, "prodotto": nome, "da_eur_l": r(prec[nome] / 1000, 4),
                            "a_eur_l": r(x["accisa"] / 1000, 4),
                            "variazione_cent_con_iva": r((x["accisa"] - prec[nome]) / 10 * (1 + IVA), 1)})
            prec[nome] = x["accisa"]
    return out


def prezzo_a(W, date, giorno, cod="2"):
    ok = [d for d in date if d <= giorno and cod in W[d] and W[d][cod]["prezzo"]]
    if not ok:
        return None, None
    d = ok[-1]
    return d, W[d][cod]["prezzo"] / 1000


def coefficienti(W, date, B, E, T, pun_mensile, pun_annuale):
    """Stima la trasmissione Brent -> prezzo netto alla pompa e TTF -> PUN."""
    dati = []
    for d in date:
        if d < "2021-01-11":
            continue
        g = dt.date.fromisoformat(d)
        b, e = media_settimana_prima(B, g), media_settimana_prima(E, g)
        if b is None or e is None or "1" not in W[d] or "2" not in W[d]:
            continue
        dati.append((d, b / e / LITRI_BARILE, W[d]["2"]["netto"] / 1000, W[d]["1"]["netto"] / 1000, b, e))
    res = {"periodo": [dati[0][0], dati[-1][0]], "n_settimane": len(dati)}
    for nome, i in (("gasolio", 2), ("benzina", 3)):
        x = [q[1] for q in dati]
        y = [q[i] for q in dati]
        a, b, r2 = ols(x, y)
        res[nome] = {"livello": {"b": r(b), "r2": r(r2, 2)}}
        for h in (1, 4, 8, 13):
            xs = [dati[k][1] - dati[k - h][1] for k in range(h, len(dati))]
            ys = [dati[k][i] - dati[k - h][i] for k in range(h, len(dati))]
            a, b, r2 = ols(xs, ys)
            res[nome]["diff_%d_sett" % h] = {"b": r(b), "r2": r(r2, 2)}
    # TTF -> PUN, medie mensili e annuali
    Tm = {}
    for g, c in T.items():
        Tm.setdefault(g.strftime("%Y-%m"), []).append(c)
    punti = [(m, p, st.mean(Tm[m])) for m, p in pun_mensile if m in Tm and len(Tm[m]) >= 15]
    for a_, p in pun_annuale:
        if int(a_) >= 2021:
            v = [c for m, cs in Tm.items() if m.startswith(a_) for c in cs]
            if v:
                punti.append((a_, p, st.mean(v)))
    if len(punti) >= 6:
        a, b, r2 = ols([q[2] for q in punti], [q[1] for q in punti])
        res["pun_ttf"] = {"a": r(a, 1), "b": r(b, 2), "r2": r(r2, 2), "n": len(punti),
                          "punti": [[q[0], r(q[1], 1), r(q[2], 1)] for q in punti]}
    return res, dati


def finestra_osservata(W, date, base_entro, inizio, giorni, cod):
    db, pb = prezzo_a(W, date, base_entro, cod)
    fine = (dt.date.fromisoformat(inizio) + dt.timedelta(days=giorni)).isoformat()
    sett = [d for d in date if inizio < d <= fine and cod in W[d]]
    if not sett or pb is None:
        return None
    p = [W[d][cod]["prezzo"] / 1000 for d in sett]
    netti = [W[d][cod]["netto"] / 1000 for d in sett]
    acc = [W[d][cod]["accisa"] / 1000 for d in sett]
    acc0 = W[db][cod]["accisa"] / 1000
    n0 = W[db][cod]["netto"] / 1000
    # prezzo che si sarebbe avuto senza tagli di accise: netto osservato + accisa della base, con IVA
    senza = [(n + acc0) * (1 + IVA) for n in netti]
    return {"base": {"data": db, "eur_l": r(pb), "netto": r(n0)}, "fino_a": fine, "n_settimane": len(sett),
            "media_eur_l": r(st.mean(p)), "max_eur_l": r(max(p)), "data_max": sett[p.index(max(p))],
            "media_senza_tagli_accise": r(st.mean(senza)), "max_senza_tagli_accise": r(max(senza)),
            "accisa_min_eur_l": r(min(acc), 4), "accisa_base_eur_l": r(acc0, 4)}


def rischio(prezzo_max, aumento_pct, soglie):
    s1, s2 = soglie["soglie_eur_l"]
    a1, a2 = soglie["soglie_aumento_pct"]
    if prezzo_max >= s2 or aumento_pct > a2:
        return "alto"
    if prezzo_max >= s1 or aumento_pct >= a1:
        return "medio"
    return "basso"


def applica(base, brent, ttf, k_g, k_b, b_pun, pesi, rapp_elettrico, soglie, spiegazione):
    """Traduce variazioni % di Brent e TTF in prezzi italiani a partire da una base."""
    d_brent_eur_l = [base["brent"] * x / 100 / base["eurusd"] / LITRI_BARILE for x in brent]
    d_g = [d_brent_eur_l[0] * k_g[0] * (1 + IVA), d_brent_eur_l[1] * k_g[1] * (1 + IVA)]
    d_b = [d_brent_eur_l[0] * k_b[0] * (1 + IVA), d_brent_eur_l[1] * k_b[1] * (1 + IVA)]
    g = [base["gasolio"] + x for x in d_g]
    bz = [base["benzina"] + x for x in d_b]
    d_ttf = [base["ttf"] * x / 100 for x in ttf]
    d_pun = [x * b_pun for x in d_ttf] if (b_pun and base.get("pun")) else [None, None]
    d_smc = [x * KWH_SMC / 1000 * 1.10 for x in d_ttf]  # €/Smc con IVA al 10%
    gas_pct = [x / base["gas_rif_eur_smc"] * 100 for x in d_smc] if base.get("gas_rif_eur_smc") else [None, None]
    w_fuel = pesi.get("FUEL", {}).get("2026") or 0
    w_gas = pesi.get("CP0452", {}).get("2026") or 0
    w_el = pesi.get("CP0451", {}).get("2026") or 0
    pct_fuel = [(d_g[i] / base["gasolio"] + d_b[i] / base["benzina"]) / 2 * 100 for i in (0, 1)]
    pct_el = [d_pun[i] / base["pun"] * 100 * rapp_elettrico if (d_pun[i] is not None and rapp_elettrico) else 0 for i in (0, 1)]
    pp = [(w_fuel * pct_fuel[i] + w_gas * (gas_pct[i] or 0) + w_el * pct_el[i]) / 1000 for i in (0, 1)]
    aumento = d_g[1] / base["gasolio"] * 100
    liv = rischio(g[1], aumento, soglie)
    return {
        "spiegazione": spiegazione,
        "base": {k: base.get(k) for k in ("data_carburanti", "gasolio", "benzina", "brent", "eurusd", "ttf", "pun", "mese_pun")},
        "gasolio_eur_l": [r(x, 2) for x in g], "benzina_eur_l": [r(x, 2) for x in bz],
        "gasolio_aumento_cent": [r(x * 100, 1) for x in d_g], "benzina_aumento_cent": [r(x * 100, 1) for x in d_b],
        "pun_eur_mwh": [r(base["pun"] + x, 0) if x is not None else None for x in d_pun],
        "gas_vulnerabili_aumento_cent_smc": [r(x * 100, 1) for x in d_smc],
        "gas_vulnerabili_spesa_pct": [r(x, 1) for x in gas_pct],
        "inflazione_effetto_diretto_punti": [r(x, 2) for x in pp],
        "rischio_fermo_tir": liv,
        "rischio_motivo": "gasolio fino a %.2f €/l (+%.0f%% sulla base); soglie: alto se %s" % (g[1], aumento, soglie["alto"]),
    }


def scenari_italia(curati, sim, coeff, base, base_normale, pesi, rapp_elettrico, W, date, osservati):
    sc_def = curati["scenari"]
    soglie = sc_def["soglie_fermo"]
    ep = sim.get("episodi", {})
    passaggi = {p["id"]: p for p in sim.get("passaggi", [])}
    out = []
    for s in sc_def["scenari"]:
        fin = s["finestra"]
        e = ep.get(s["episodio"], {}).get("calcolato", {})
        brent = [0.0, 0.0]
        ttf = [0.0, 0.0]
        origine = ""
        if s["passaggio"] == "hormuz" or s["episodio"] == "mar_rosso_2023":
            w = e.get("brent", {}).get("finestre", {}).get(fin, {})
            brent = [w.get("media_pct", 0.0), w.get("max_pct", 0.0)]
            if s["passaggio"] == "hormuz":
                wt = e.get("ttf", {}).get("finestre", {}).get(fin, {})
                ttf = [wt.get("media_pct", 0.0), wt.get("max_pct", 0.0)]
                origine = "variazioni di Brent e TTF nell'episodio di Hormuz 2026 (simulatore.json, finestra %s giorni: media e picco)" % fin
            else:
                origine = "variazione del Brent nella crisi del Mar Rosso 2023-24 (simulatore.json, finestra %s giorni); TTF a zero come nel simulatore" % fin
        elif s["passaggio"] == "canale-di-sicilia":
            p = passaggi.get("canale-di-sicilia", {})
            flusso = p.get("gnl", {}).get("flusso_bcm", 0)
            libera = sim.get("calcolato", {}).get("gnl_italia", {}).get("libera_bcm", 0)
            c = ep.get("hormuz_2026", {}).get("calcolato", {}).get("coeff_ttf_per_bcm", {}).get(fin, {})
            ttf = [max(flusso - libera, 0) * c.get("min", 0), flusso * c.get("max", 0)]
            origine = "regola ttf_perdita del simulatore: %.2f bcm/anno del TransMed, meno %.1f bcm di capacità libera dei rigassificatori (minimo) o senza bypass (massimo), per il coefficiente di Hormuz 2026 a %s giorni" % (flusso, libera, fin)
        sett = s["orizzonte_settimane"]
        kg = coeff["gasolio"]
        kb = coeff["benzina"]
        if sett <= 4:
            k_g = [kg["diff_4_sett"]["b"], kg["diff_8_sett"]["b"]]
            k_b = [kb["diff_4_sett"]["b"], kb["diff_8_sett"]["b"]]
        else:
            k_g = [kg["diff_8_sett"]["b"], max(kg["diff_13_sett"]["b"], kg["livello"]["b"])]
            k_b = [kb["diff_8_sett"]["b"], max(kb["diff_13_sett"]["b"], kb["livello"]["b"])]
        b_pun = coeff.get("pun_ttf", {}).get("b")
        res = {
            "id": s["id"], "nome": s["nome"], "passaggio": s["passaggio"], "durata_giorni": s["durata_giorni"],
            "valutazione": True,
            "ingresso": {"brent_pct": [r(x, 1) for x in brent], "ttf_pct": [r(x, 1) for x in ttf], "origine": origine},
            "coefficienti_usati": {"gasolio": k_g, "benzina": k_b, "pun_per_ttf": b_pun, "rapporto_elettricita_dettaglio_pun": rapp_elettrico},
            "da_oggi": applica(base, brent, ttf, k_g, k_b, b_pun, pesi, rapp_elettrico, soglie,
                               "se uno shock della stessa forma partisse dai prezzi di oggi (che includono già la crisi di Hormuz)"),
        }
        if base_normale:
            res["da_condizioni_normali"] = applica(base_normale, brent, ttf, k_g, k_b, b_pun, pesi, rapp_elettrico, soglie,
                                                   "partendo dai prezzi dell'ultima settimana prima della guerra (fine febbraio 2026), con le accise ordinarie e senza tagli")
        res["catene"] = s["catene"]
        res["misure_probabili"] = s["misure_probabili"]
        res["indicatori"] = s["indicatori"]
        if s.get("nota"):
            res["nota"] = s["nota"]
        if s["id"] in osservati:
            res["osservato"] = osservati[s["id"]]
        out.append(res)
    return out


# ---------------------------------------------------------------- principale
def principale():
    curati, problemi = valida()
    if "--valida" in sys.argv:
        print("\n".join(problemi + avvisi) or "file curati: tutto in ordine")
        return 1 if problemi else 0
    errori.extend("validazione: " + p for p in problemi)
    precedente = leggi_json(USCITA, {}) or {}
    sim = leggi_json(SIMULATORE, {}) or {}
    prezzi = leggi_json(PREZZI, {}) or {}

    W, date = mase_settimanale()
    carb = serie_carburanti(W, date)
    ultima = date[-1]

    # Mimit giornaliero: si accumula nel file
    giorn = (precedente.get("serie", {}) or {}).get("carburanti_giornalieri_self", {"benzina": [], "gasolio": []})
    mimit = None
    try:
        dm, mimit = mimit_giornaliero()
        for k in ("benzina", "gasolio"):
            giorn[k] = [x for x in giorn.get(k, []) if x[0] != dm] + [[dm, mimit[k]["media_troncata"]]]
            giorn[k].sort()
    except Exception as e:
        errori.append("Mimit giornaliero non scaricato (resta la serie settimanale MASE): %s" % e)

    B = E = T = {}
    try:
        B, E, T = yahoo("BZ=F"), yahoo("EURUSD=X"), yahoo("TTF=F")
        fonte("Yahoo Finance, future Brent (BZ=F), TTF (TTF=F), cambio EUR/USD", "https://finance.yahoo.com/",
              "uso informativo, non ufficiale: si pubblicano solo i coefficienti stimati, non le serie", max(B).isoformat())
    except Exception as e:
        errori.append("Yahoo non scaricato: coefficienti di trasmissione non ricalcolati (%s)" % e)

    g = {}
    try:
        g = gme()
    except Exception as e:
        errori.append("GME non scaricato: %s" % e)
        g = (precedente.get("serie", {}) or {}).get("gme", {}) or {}

    nic = fid = {}
    try:
        nic = inflazione_istat()
    except Exception as e:
        errori.append("Istat NIC non scaricato: %s" % e)
        nic = (precedente.get("serie", {}) or {}).get("inflazione_nic", {})
    try:
        fid = fiducia_istat()
    except Exception as e:
        errori.append("Istat fiducia non scaricata: %s" % e)
        fid = (precedente.get("serie", {}) or {}).get("fiducia_consumatori", {})
    hi, pesi = {}, {}
    try:
        hi, pesi = hicp()
    except Exception as e:
        errori.append("Eurostat HICP non scaricato: %s" % e)
        hi = (precedente.get("serie", {}) or {}).get("hicp", {})
        pesi = precedente.get("pesi_hicp_millesimi", {})

    try:
        scioperi = {"origine": "calendario MIT", "elementi": scioperi_mit()}
    except Exception as e:
        errori.append("scioperi: %s; uso l'elenco curato raccolta/italia/scioperi.json" % e)
        sc = curati.get("scioperi", {})
        prossimi = [x for x in sc.get("elementi", []) if x["data_fine"] >= OGGI.isoformat()
                    and x["data_inizio"] <= (OGGI + dt.timedelta(days=30)).isoformat()]
        scioperi = {"origine": "elenco curato: " + sc.get("fonte_elenco", ""), "link": sc.get("link_elenco"),
                    "data_fonte": sc.get("data_fonte"), "elementi": prossimi, "revocati": sc.get("revocati", []),
                    "autotrasporto": sc.get("autotrasporto")}
    controlla_vendite(curati.get("consumi_carburanti", {}))

    # coefficienti
    coeff = (precedente.get("regole_trasmissione", {}) or {}).get("stimate")
    if B and E:
        coeff, _ = coefficienti(W, date, B, E, T, g.get("mensile", []), g.get("annuale", []))
    if not coeff:
        raise SystemExit("impossibile stimare i coefficienti: nessun dato di mercato")

    # rapporto tra variazione dei prezzi elettrici al consumo e del PUN (2022 su 2021)
    rapp_el = None
    try:
        el22 = [v for m, v in hi.get("elettricita", []) if m.startswith("2022")]
        pa = dict(g.get("annuale", []))
        if el22 and pa.get("2022") and pa.get("2021"):
            rapp_el = r(st.mean(el22) / ((pa["2022"] / pa["2021"] - 1) * 100), 2)
    except Exception:
        pass

    # base di oggi
    gb = W[ultima]["2"]
    bb = W[ultima]["1"]
    acc_ord = max(W[d]["2"]["accisa"] for d in date if d >= (dt.date.fromisoformat(ultima) - dt.timedelta(days=365)).isoformat())
    gasolio_oggi = gb["prezzo"] / 1000
    if gb["accisa"] < acc_ord and OGGI >= dt.date(2026, 11, 8):
        gasolio_oggi = (gb["netto"] + acc_ord) / 1000 * (1 + IVA)
    serie_prezzi = {x.get("id"): x for x in prezzi.get("serie", [])}
    brent_oggi = (serie_prezzi.get("brent") or {}).get("ultimo") or (B[max(B)] if B else None)
    eur_oggi = (serie_prezzi.get("eurusd") or {}).get("ultimo") or (E[max(E)] if E else None)
    ttf_oggi = (serie_prezzi.get("ttf") or {}).get("ultimo") or (T[max(T)] if T else None)
    mesi_pun = [x for x in g.get("mensile", []) if x[0] < OGGI.strftime("%Y-%m")]
    arera = curati.get("arera", {}).get("elementi", [])
    rif = [e for e in arera if e.get("prezzo_riferimento_cliente_tipo_cent_smc")]
    base = {"data_carburanti": ultima, "gasolio": r(gasolio_oggi), "benzina": r(bb["prezzo"] / 1000),
            "brent": brent_oggi, "eurusd": eur_oggi, "ttf": ttf_oggi,
            "pun": mesi_pun[-1][1] if mesi_pun else None, "mese_pun": mesi_pun[-1][0] if mesi_pun else None,
            "gas_rif_eur_smc": rif[-1]["prezzo_riferimento_cliente_tipo_cent_smc"] / 100 if rif else None}

    # episodi osservati in Italia
    osservati = {}
    for sid, b0, i0, gg in (("hormuz_1m", "2026-02-27", "2026-03-02", 30), ("hormuz_3m", "2026-02-27", "2026-03-02", 91),
                            ("mar_rosso_1m", "2023-12-15", "2023-12-18", 30)):
        o = {"gasolio": finestra_osservata(W, date, b0, i0, gg, "2"), "benzina": finestra_osservata(W, date, b0, i0, gg, "1")}
        fine = (dt.date.fromisoformat(i0) + dt.timedelta(days=gg)).strftime("%Y-%m")
        nic_g = dict(nic.get("generale", []))
        nic_e = dict(hi.get("energia", []))
        mesi = [m for m in sorted(nic_g) if i0[:7] <= m <= fine]
        o["inflazione"] = {"mesi": mesi, "nic_generale": [nic_g.get(m) for m in mesi],
                           "hicp_energia": [nic_e.get(m) for m in mesi],
                           "prima": {"mese": (dt.date.fromisoformat(i0) - dt.timedelta(days=20)).strftime("%Y-%m")}}
        o["inflazione"]["prima"]["nic_generale"] = nic_g.get(o["inflazione"]["prima"]["mese"])
        o["pun_mensile"] = [x for x in g.get("mensile", []) if i0[:7] <= x[0] <= fine]
        vend = curati.get("consumi_carburanti", {}).get("elementi", [])
        o["vendite_gasolio_motori_var_pct"] = [[v["mese"], v["gasolio_motori"]["var_pct"]] for v in vend if i0[:7] <= v["mese"] <= fine]
        o["nota"] = "Fatti dai dati: prezzi medi settimanali MASE (con i tagli di accise effettivi e, a parte, senza tagli: netto osservato più accisa della settimana base, con IVA), inflazione Istat/Eurostat, PUN GME, vendite MASE."
        osservati[sid] = o

    # base 'condizioni normali': ultima settimana prima della guerra (stessa base del simulatore)
    base_normale = None
    try:
        hb = sim["episodi"]["hormuz_2026"]["calcolato"]
        bd = sim["episodi"]["hormuz_2026"]["base"]
        e_feb = [v for k, v in E.items() if bd["da"] <= k.isoformat() <= bd["a"]]
        d0, g0 = prezzo_a(W, date, bd["a"], "2")
        _, b0 = prezzo_a(W, date, bd["a"], "1")
        pun_feb = dict(g.get("mensile", [])).get(bd["a"][:7]) or ((precedente.get("regole_trasmissione") or {}).get("per_il_simulatore", {}).get("base_condizioni_normali") or {}).get("pun")
        base_normale = {"data_carburanti": d0, "gasolio": r(g0), "benzina": r(b0), "brent": hb["brent"]["base"],
                        "eurusd": r(st.mean(e_feb), 4) if e_feb else None, "ttf": hb["ttf"]["base"],
                        "pun": pun_feb, "mese_pun": bd["a"][:7], "gas_rif_eur_smc": None}
        if not base_normale["eurusd"]:
            base_normale = None
    except Exception as e:
        avvisi.append("base 'condizioni normali' non calcolata: %s" % e)
    scen = scenari_italia(curati, sim, coeff, base, base_normale, pesi, rapp_el, W, date, osservati)
    # verifica: la regola applicata alla base di febbraio 2026 contro quello che è successo davvero
    for s in scen:
        o, n = s.get("osservato", {}).get("gasolio"), s.get("da_condizioni_normali")
        if o and n:
            s["verifica"] = ("Regola su base febbraio 2026: gasolio %.2f–%.2f €/l. Osservato (MASE): media %.2f, massimo %.2f €/l con i tagli di accise; "
                             "%.2f e %.2f senza i tagli." % (n["gasolio_eur_l"][0], n["gasolio_eur_l"][1], o["media_eur_l"], o["max_eur_l"],
                                                              o["media_senza_tagli_accise"], o["max_senza_tagli_accise"]))

    # precedenti: prezzo del gasolio alla data e variazione su un anno
    prec = []
    for e in curati.get("precedenti", {}).get("elementi", []):
        e = dict(e)
        if e.get("data_prezzo"):
            d0, p0 = prezzo_a(W, date, e["data_prezzo"])
            d1, p1 = prezzo_a(W, date, (dt.date.fromisoformat(e["data_prezzo"]) - dt.timedelta(days=365)).isoformat())
            e["gasolio_alla_data"] = {"settimana": d0, "eur_l": r(p0), "un_anno_prima": r(p1),
                                      "var_pct_un_anno": r((p0 / p1 - 1) * 100, 1) if p0 and p1 else None,
                                      "fonte": "MASE, prezzi medi settimanali"}
        prec.append(e)

    # quadro di oggi
    def ultimo(serie):
        return serie[-1] if serie else None
    oggi = {
        "gasolio_settimanale": {"data": ultima, "eur_l": r(gb["prezzo"] / 1000), "netto": r(gb["netto"] / 1000),
                                "accisa": r(gb["accisa"] / 1000, 4), "iva": r(gb["iva"] / 1000, 4),
                                "stima_dopo_fine_taglio_accise": r(gasolio_oggi) if gasolio_oggi != gb["prezzo"] / 1000 else None},
        "benzina_settimanale": {"data": ultima, "eur_l": r(bb["prezzo"] / 1000), "netto": r(bb["netto"] / 1000),
                                "accisa": r(bb["accisa"] / 1000, 4), "iva": r(bb["iva"] / 1000, 4)},
        "self_giornaliero": {"data": ultimo(giorn.get("gasolio", []))[0] if giorn.get("gasolio") else None, "valori": mimit},
        "pun_ultimo_mese_completo": mesi_pun[-1] if mesi_pun else None,
        "pun_mese_in_corso_parziale": ultimo([x for x in g.get("mensile", []) if x[0] == OGGI.strftime("%Y-%m")]),
        "pun_ultimo_giorno": ultimo(g.get("giornaliero", [])),
        "gas_mgp_ultimo_giorno": ultimo(g.get("gas_mgp_giornaliero", [])),
        "arera_cmem_ultimo": arera[-1] if arera else None,
        "nic_generale": ultimo(nic.get("generale", [])), "nic_energetici": ultimo(nic.get("energetici", [])),
        "nic_alimentari": ultimo(nic.get("alimentari", [])), "fiducia_consumatori": ultimo(fid.get("clima", [])),
        "brent": brent_oggi, "ttf": ttf_oggi, "eurusd": eur_oggi,
    }

    kg, kb = coeff["gasolio"], coeff["benzina"]
    k10 = 10 / (eur_oggi or 1.12) / LITRI_BARILE
    regole = {
        "stimate": coeff,
        "regole": [
            {"id": "brent_pompa_teorico", "testo": "Se i margini di raffinazione non cambiano, 10 $/barile di Brent valgono %.1f centesimi al litro di prezzo netto, %.1f con l'IVA (EUR/USD %.4f). Le accise sono fisse al litro e non si muovono con il petrolio." % (k10 * 100, k10 * 122, eur_oggi or 0),
             "cent_l_per_10_usd_bbl": r(k10 * 122, 1), "fonte": "calcolo: 10 / EURUSD / 158,987 litri × 1,22", "affidabilita": "alta"},
            {"id": "brent_gasolio", "testo": "Gasolio: stimato sui dati italiani %s–%s, il prezzo netto si muove di %.2f volte la variazione del Brent in €/litro dopo 4 settimane, %.2f dopo 8 e %.2f dopo 13 (a regime: %.2f). Con l'IVA, 10 $/barile in più ≈ +%.0f/+%.0f centesimi dopo 4/8 settimane. Il gasolio amplifica il greggio perché nelle crisi sale anche il margine del diesel." % (
                coeff["periodo"][0], coeff["periodo"][1], kg["diff_4_sett"]["b"], kg["diff_8_sett"]["b"], kg["diff_13_sett"]["b"], kg["livello"]["b"],
                k10 * 122 * kg["diff_4_sett"]["b"], k10 * 122 * kg["diff_8_sett"]["b"]),
             "coeff": {"4_sett": kg["diff_4_sett"]["b"], "8_sett": kg["diff_8_sett"]["b"], "13_sett": kg["diff_13_sett"]["b"], "livello": kg["livello"]["b"]},
             "r2": {"4_sett": kg["diff_4_sett"]["r2"], "8_sett": kg["diff_8_sett"]["r2"]},
             "fonte": "stima dell'osservatorio: regressione sulle medie settimanali MASE (prezzo netto) e sulla media della settimana precedente del Brent in € (Yahoo)", "affidabilita": "media"},
            {"id": "brent_benzina", "testo": "Benzina: %.2f volte dopo 4 settimane, %.2f dopo 8 (a regime %.2f). 10 $/barile ≈ +%.0f/+%.0f centesimi con IVA dopo 4/8 settimane." % (
                kb["diff_4_sett"]["b"], kb["diff_8_sett"]["b"], kb["livello"]["b"], k10 * 122 * kb["diff_4_sett"]["b"], k10 * 122 * kb["diff_8_sett"]["b"]),
             "coeff": {"4_sett": kb["diff_4_sett"]["b"], "8_sett": kb["diff_8_sett"]["b"], "13_sett": kb["diff_13_sett"]["b"], "livello": kb["livello"]["b"]},
             "fonte": "stima dell'osservatorio, come sopra", "affidabilita": "media"},
            {"id": "ritardo", "testo": "Ritardo: dopo una settimana passa circa il %.0f%% dell'effetto di lungo periodo sul gasolio, dopo 4 settimane il %.0f%%, dopo 8 il %.0f%%. Il taglio delle accise invece arriva in pochi giorni ma non ovunque (marzo 2026: 60%% dei distributori nei primi tre giorni)." % (
                kg["diff_1_sett"]["b"] / kg["livello"]["b"] * 100, kg["diff_4_sett"]["b"] / kg["livello"]["b"] * 100, kg["diff_8_sett"]["b"] / kg["livello"]["b"] * 100),
             "fonte": "stima dell'osservatorio; Today.it 27/3/2026 per le accise", "affidabilita": "media"},
            {"id": "ttf_pun", "testo": ("PUN ≈ %.0f + %.2f × TTF (€/MWh), su %d medie mensili e annuali GME/Yahoo (R² %.2f): +10 €/MWh di TTF ≈ +%.0f €/MWh di PUN. Il gas fa il prezzo dell'elettricità nella maggior parte delle ore." % (
                coeff["pun_ttf"]["a"], coeff["pun_ttf"]["b"], coeff["pun_ttf"]["n"], coeff["pun_ttf"]["r2"], coeff["pun_ttf"]["b"] * 10)) if coeff.get("pun_ttf") else "dato mancante",
             "coeff": coeff.get("pun_ttf"), "fonte": "stima dell'osservatorio su dati GME e Yahoo", "affidabilita": "media"},
            {"id": "ttf_gas_vulnerabili", "testo": "Gas vulnerabili: la materia prima (CMEM) è la media mensile del PSV, quindi +10 €/MWh all'ingrosso = +%.1f centesimi per Smc più IVA, in bolletta il mese dopo. Sul prezzo di riferimento di ottobre 2026 (%.2f c€/Smc) è circa +%.0f%%." % (
                10 * KWH_SMC / 10, (base["gas_rif_eur_smc"] or 0) * 100, 10 * KWH_SMC / 1000 * 1.10 / (base["gas_rif_eur_smc"] or 1) * 100),
             "fonte": "ARERA, comunicato 3/11/2026; potere calorifico come gas-italia.json; IVA 10% sui primi 480 Smc annui (22% oltre)", "affidabilita": "alta"},
            {"id": "energia_inflazione", "testo": "Inflazione: l'energia pesa %.1f%% nel paniere HICP italiano 2026 (carburanti %.1f%%, elettricità %.1f%%, gas %.1f%%). Effetto diretto: +10%% sui prezzi dell'energia al consumo ≈ +%.1f punti di inflazione, con 1-3 mesi di ritardo (carburanti subito, bollette dopo). Gli effetti indiretti (trasporti, alimentari) vengono dopo e non sono stimati qui." % (
                (pesi.get("NRG", {}).get("2026") or 0) / 10, (pesi.get("FUEL", {}).get("2026") or 0) / 10, (pesi.get("CP0451", {}).get("2026") or 0) / 10, (pesi.get("CP0452", {}).get("2026") or 0) / 10, (pesi.get("NRG", {}).get("2026") or 0) / 100),
             "fonte": "Eurostat prc_hicp_iw (pesi 2026)", "affidabilita": "alta"},
            {"id": "pun_bollette", "testo": ("Bollette elettriche: nel 2022 i prezzi al consumo dell'elettricità (HICP) sono saliti in media del %.0f%% a fronte di un PUN più alto del %.0f%%: rapporto %.2f, usato come approssimazione. Contratti a prezzo fisso e tutele rallentano il passaggio." % (
                st.mean([v for m, v in hi.get("elettricita", []) if m.startswith("2022")]), (dict(g.get("annuale", []))["2022"] / dict(g.get("annuale", []))["2021"] - 1) * 100, rapp_el)) if rapp_el else "dato mancante",
             "fonte": "Eurostat, GME; stima dell'osservatorio su un solo anno", "affidabilita": "bassa"},
        ],
        "letteratura": curati.get("letteratura", {}).get("elementi", []),
        "per_il_simulatore": {
            "testo": "Come usare le regole nella sezione 'Cosa succede in Italia': dato Δ%Brent e Δ%TTF calcolati dal simulatore, ΔBrent €/l = Brent_oggi × Δ%/100 / EURUSD / 158,987. Gasolio = gasolio_oggi + ΔBrent€/l × coeff × 1,22 (coeff 4 settimane per 2 settimane–1 mese, 8–13 settimane per 3 mesi). PUN = PUN_ultimo_mese + b × ΔTTF€/MWh. Gas vulnerabili: +ΔTTF × 0,01057 €/Smc più IVA. Inflazione diretta = Σ peso × Δ% (pesi in millesimi). Rischio fermo dalle soglie in 'soglie_fermo'. Gli scenari già calcolati sono in 'scenari'.",
            "base_oggi": base,
            "base_condizioni_normali": base_normale,
            "pesi_hicp_millesimi_2026": {k: v.get("2026") for k, v in pesi.items()},
        },
    }

    vend = curati.get("consumi_carburanti", {})
    uscita = {
        "aggiornato": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "versione": "1.0",
        "fonti": fonti + [
            {"nome": vend.get("fonte"), "link": vend.get("link"), "licenza": vend.get("licenza"),
             "data_dato": (vend.get("elementi") or [{}])[-1].get("mese"), "nota": "voci curate in raccolta/italia/consumi_carburanti.json"},
            {"nome": "ARERA, comunicati vulnerabili gas", "link": "https://www.arera.it/comunicati-stampa", "licenza": "dati pubblici",
             "data_dato": arera[-1]["mese"] if arera else None, "nota": "voci curate in raccolta/italia/arera.json"},
            {"nome": "Voci curate (precedenti, autotrasporto, misure, scioperi, letteratura, scenari)", "link": "raccolta/italia/",
             "licenza": "testi dell'osservatorio con link alle fonti", "data_dato": OGGI.isoformat()},
        ],
        "nota": "Cosa succede in Italia quando uno shock energetico o logistico si trasmette: carburanti, accise, bollette, inflazione, autotrasporto e scioperi, comportamenti, regole di trasmissione e scenari per il simulatore. I fatti hanno fonte e data; le parti con 'valutazione': true sono stime dell'osservatorio. Generato da raccolta/italia/raccogli.py.",
        "oggi": oggi,
        "serie": {
            "carburanti_settimanali": carb,
            "carburanti_giornalieri_self": giorn,
            "gme": g,
            "inflazione_nic": nic,
            "hicp": hi,
            "fiducia_consumatori": fid,
            "vendite_carburanti_kt": [{"mese": v["mese"], **{k: v[k] for k in ("benzina", "gasolio_motori", "gasolio_extrarete", "gasolio_agricolo") if k in v}} for v in vend.get("elementi", [])],
            "arera_cmem": [[e["mese"], e["cmem_eur_mwh"]] for e in arera],
        },
        "pesi_hicp_millesimi": pesi,
        "accise": {"oggi_gasolio_eur_l": r(gb["accisa"] / 1000, 4), "ordinaria_gasolio_eur_l": r(acc_ord / 1000, 4),
                   "oggi_benzina_eur_l": r(bb["accisa"] / 1000, 4), "cambi": cambi_accise(W, date),
                   "fonte": "MASE, serie settimanale (campo ACCISA)",
                   "nota": "Il taglio del gasolio di 4 centesimi (4,9 con IVA) è scaduto l'8 novembre 2026 (Rai News, 8/11/2026): la rilevazione MASE del 2/11 lo include ancora."},
        "regole_trasmissione": regole,
        "autotrasporto": curati.get("autotrasporto", {}),
        "precedenti": prec,
        "scioperi_proclamati": scioperi,
        "misure_governo": curati.get("misure", {}).get("elementi", []),
        "soglie_fermo": curati.get("scenari", {}).get("soglie_fermo"),
        "scenari": scen,
        "errori": errori,
        "avvisi": avvisi,
    }
    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    with open(USCITA, "w", encoding="utf-8") as f:
        json.dump(uscita, f, ensure_ascii=False, separators=(",", ":"))
    print("scritto %s (%d kB); errori: %d; avvisi: %d" % (USCITA, os.path.getsize(USCITA) // 1024, len(errori), len(avvisi)))
    for x in errori + avvisi:
        print(" -", x)
    return 0


if __name__ == "__main__":
    sys.exit(principale())
