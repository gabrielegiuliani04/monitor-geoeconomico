#!/usr/bin/env python3
"""Scorte e depositi strategici -> docs/data/scorte.json

Solo libreria standard. Uso:  python3 raccolta/scorte/raccogli.py [percorso_output]

Fonti:
  1. GIE AGSI+ (stoccaggi gas UE, giornaliero)  -> serve AGSI_API_KEY (gratuita, header x-key). Se manca: avviso, si salta.
  2. Eurostat nrg_stk_gasm (stock gas mensile, senza chiave, ritardo ~3 mesi) -> ripiego senza chiave per il gas.
  3. EIA (petrolio USA, settimanale): pagine pubbliche LeafHandler (senza chiave); ripiego API v2 con EIA_API_KEY.
  4. Eurostat nrg_stk_oem (scorte petrolifere di emergenza UE, giorni equivalenti, mensile).
  5. USDA FAS PSD (grano: scorte finali per anno commerciale, file zip pubblico).
  6. FMI IRFCL (oro delle banche centrali, once troy -> tonnellate, mensile).
Ogni fonte e' indipendente: se fallisce finisce in "errori" e le altre proseguono.
"""
import csv
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

UA = {"User-Agent": "Mozilla/5.0 (monitor-osint scorte)"}
OGGI = dt.date.today()
INIZIO_SERIE = OGGI.replace(year=OGGI.year - 3, month=1, day=1)      # serie pubblicate: ~3 anni
INIZIO_STORICO = OGGI.replace(year=OGGI.year - 6, month=1, day=1)    # storico per media 5 anni
OBIETTIVO_UE_GAS = 90.0   # % reg. (UE) 2022/1032 modificato nel 2025: 90% fra 1/10 e 1/12, deroghe fino a -10 pp (+5 pp)
OZ_PER_TONNELLATA = 32150.7466

errori = []
fonti = []


def avviso(msg):
    print("AVVISO:", msg, file=sys.stderr)
    errori.append(msg)


def get(url, headers=None, tries=4, timeout=90, binary=False):
    h = dict(UA)
    if headers:
        h.update(headers)
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
                data = r.read()
                return data if binary else data.decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 + 3 * i)
    raise RuntimeError(f"{url.split('?')[0]}: {last}")


def r2(v, n=2):
    return None if v is None else round(v, n)


def valore_vicino(serie, data, tolleranza=4):
    """Valore della serie (lista ordinata di [data_iso, v]) piu' vicino a `data` entro +-tolleranza giorni."""
    best = None
    for d, v in serie:
        diff = abs((dt.date.fromisoformat(d) - data).days)
        if diff <= tolleranza and (best is None or diff < best[0]):
            best = (diff, v)
    return None if best is None else best[1]


def meno_anni(d, k):
    try:
        return d.replace(year=d.year - k)
    except ValueError:  # 29 febbraio
        return d.replace(year=d.year - k, day=28)


def confronti(serie, tolleranza=4, anni_media=5):
    """Ultimo valore, variazione su periodo precedente, anno scorso, media 5 anni (stessa data)."""
    if not serie:
        return {}
    d_ult, v_ult = serie[-1]
    d0 = dt.date.fromisoformat(d_ult)
    out = {"data": d_ult, "valore": v_ult}
    if len(serie) > 1:
        out["precedente"] = {"data": serie[-2][0], "valore": serie[-2][1], "variazione": r2(v_ult - serie[-2][1], 3)}
    a1 = valore_vicino(serie, meno_anni(d0, 1), tolleranza)
    if a1 is not None:
        out["anno_scorso"] = {"valore": a1, "variazione": r2(v_ult - a1, 3),
                              "variazione_pct": r2((v_ult - a1) / a1 * 100, 1) if a1 else None}
    vals = [valore_vicino(serie, meno_anni(d0, k), tolleranza) for k in range(1, anni_media + 1)]
    vals = [v for v in vals if v is not None]
    if len(vals) == anni_media:
        m = sum(vals) / len(vals)
        out["media_5_anni"] = {"valore": r2(m, 3), "scarto": r2(v_ult - m, 3),
                               "scarto_pct": r2((v_ult - m) / m * 100, 1) if m else None}
    return out


def taglia(serie, inizio=INIZIO_SERIE):
    s = inizio.isoformat()
    return [p for p in serie if p[0] >= s]


def elemento(**kw):
    serie = kw.pop("serie_completa")
    kw.setdefault("tolleranza", 4)
    tol = kw.pop("tolleranza")
    kw["ultimo"] = confronti(serie, tol)
    kw["data_fonte"] = serie[-1][0] if serie else None
    kw["serie"] = taglia(serie, kw.pop("inizio", INIZIO_SERIE))
    return kw


# ---------------------------------------------------------------- 1. GIE AGSI+
AGSI_PAESI = [("IT", "Italia"), ("DE", "Germania"), ("FR", "Francia"), ("NL", "Paesi Bassi"), ("AT", "Austria"), ("EU", "Unione europea")]


def agsi():
    key = os.environ.get("AGSI_API_KEY", "").strip()
    if not key:
        avviso("AGSI+: AGSI_API_KEY non impostata, stoccaggi gas giornalieri saltati "
               "(chiave gratuita: registrazione su https://agsi.gie.eu/account). Uso il ripiego mensile Eurostat.")
        return []
    out = []
    for cod, nome in AGSI_PAESI:
        try:
            righe, page, last = [], 1, 1
            while page <= last and page <= 40:
                q = {"from": INIZIO_STORICO.isoformat(), "to": OGGI.isoformat(), "size": 300, "page": page}
                if cod == "EU":
                    q["type"] = "eu"
                else:
                    q["country"] = cod
                j = json.loads(get("https://agsi.gie.eu/api?" + urllib.parse.urlencode(q), {"x-key": key}))
                if j.get("error"):
                    raise RuntimeError(j.get("message") or j.get("error"))
                last = int(j.get("last_page") or 1)
                righe += j.get("data") or []
                page += 1
            pct, twh, cap = [], [], None
            for r in righe:
                d = r.get("gasDayStart")
                try:
                    if r.get("full") not in (None, "", "-"):
                        pct.append([d, round(float(r["full"]), 2)])
                    if r.get("gasInStorage") not in (None, "", "-"):
                        twh.append([d, round(float(r["gasInStorage"]), 2)])
                except (TypeError, ValueError):
                    continue
            if not cap and righe:
                try:
                    cap = float(sorted(righe, key=lambda x: x.get("gasDayStart", ""))[-1].get("workingGasVolume"))
                except (TypeError, ValueError):
                    cap = None
            pct.sort()
            twh.sort()
            if not pct:
                raise RuntimeError("nessun dato")
            paese = "EU" if cod == "EU" else cod
            e1 = elemento(id=f"gas_stoccaggio_pct_{cod.lower()}", nome=f"Stoccaggi gas {nome} – riempimento", gruppo="Gas UE",
                          paese=paese, unita="%", frequenza="giornaliera", fonte="GIE AGSI+", link="https://agsi.gie.eu/",
                          affidabilita="alta", serie_completa=pct, tolleranza=2,
                          note=f"Obiettivo UE {OBIETTIVO_UE_GAS:.0f}% fra 1 ottobre e 1 dicembre (con deroghe).")
            e1["ultimo"]["obiettivo_ue"] = OBIETTIVO_UE_GAS
            e1["ultimo"]["distanza_obiettivo_pp"] = r2(e1["ultimo"]["valore"] - OBIETTIVO_UE_GAS, 2)
            out.append(e1)
            e2 = elemento(id=f"gas_stoccaggio_twh_{cod.lower()}", nome=f"Stoccaggi gas {nome} – gas in stoccaggio", gruppo="Gas UE",
                          paese=paese, unita="TWh", frequenza="giornaliera", fonte="GIE AGSI+", link="https://agsi.gie.eu/",
                          affidabilita="alta", serie_completa=twh, tolleranza=2,
                          note="Capacita' di working gas (TWh): %s" % (r2(cap, 1) if cap else "n.d."))
            out.append(e2)
        except Exception as ex:  # noqa: BLE001
            avviso(f"AGSI+ {cod}: {ex}")
    if out:
        fonti.append({"nome": "GIE AGSI+ (Aggregated Gas Storage Inventory)", "link": "https://agsi.gie.eu/",
                      "licenza": "uso libero con citazione della fonte GIE AGSI+ (condizioni del sito)",
                      "data_dato": max(e["data_fonte"] for e in out)})
    return out


# ---------------------------------------------------------------- 2/4. Eurostat
def eurostat(dataset, filtri, since):
    q = dict(filtri)
    q.update({"sinceTimePeriod": since, "lang": "en"})
    url = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}?" + urllib.parse.urlencode(q, doseq=True)
    d = json.loads(get(url))
    ids, size = d["id"], d["size"]
    idx = {k: {v: c for c, v in d["dimension"][k]["category"]["index"].items()} for k in ids}
    serie = {}
    for k, v in d["value"].items():
        k = int(k)
        coords = {}
        for dim, n in zip(reversed(ids), reversed(size)):
            coords[dim] = idx[dim][k % n]
            k //= n
        serie.setdefault(coords["geo"], []).append([coords["time"] + "-01", v])
    for s in serie.values():
        s.sort()
    return serie, d.get("updated", "")


NOMI = {"IT": "Italia", "DE": "Germania", "FR": "Francia", "NL": "Paesi Bassi", "AT": "Austria", "EU27_2020": "UE-27"}


def eurostat_gas():
    out = []
    geos = ["IT", "DE", "FR", "NL", "AT", "EU27_2020"]
    serie, agg = eurostat("nrg_stk_gasm", {"stk_flow": "STKCL_NAT", "unit": "TJ_GCV", "geo": geos}, INIZIO_STORICO.strftime("%Y-%m"))
    for g in geos:
        s = [[d, round(v / 3600.0, 2)] for d, v in serie.get(g, [])]   # TJ -> TWh (PCS)
        if not s:
            avviso(f"Eurostat nrg_stk_gasm: nessun dato per {g}")
            continue
        out.append(elemento(id=f"gas_stock_mensile_twh_{g.lower()[:2]}", nome=f"Gas in stoccaggio {NOMI[g]} – fine mese (Eurostat)",
                            gruppo="Gas UE (mensile)", paese="EU" if g.startswith("EU") else g, unita="TWh (PCS)",
                            frequenza="mensile", fonte="Eurostat nrg_stk_gasm (STKCL_NAT)",
                            link="https://ec.europa.eu/eurostat/databrowser/view/nrg_stk_gasm/default/table",
                            affidabilita="alta", serie_completa=s, tolleranza=3,
                            note="Scorta di chiusura sul territorio nazionale, TJ PCS / 3600. Il mese e' indicato col primo giorno; "
                                 "ritardo di pubblicazione ~3 mesi. Non da' la % di riempimento (manca la capacita')."))
    fonti.append({"nome": "Eurostat – Gas products stock levels, monthly (nrg_stk_gasm)",
                  "link": "https://ec.europa.eu/eurostat/databrowser/view/nrg_stk_gasm/default/table",
                  "licenza": "CC BY 4.0 (Eurostat)", "data_dato": max(e["data_fonte"] for e in out) if out else agg})
    return out


def eurostat_petrolio():
    out = []
    geos = ["IT", "DE", "FR", "NL", "AT"]
    serie, agg = eurostat("nrg_stk_oem", {"stk_flow": "STK_EUE_DIR", "unit": "NR", "geo": geos}, INIZIO_STORICO.strftime("%Y-%m"))
    for g in geos:
        s = [[d, round(v, 1)] for d, v in serie.get(g, [])]
        if not s:
            avviso(f"Eurostat nrg_stk_oem: nessun dato per {g}")
            continue
        out.append(elemento(id=f"petrolio_emergenza_giorni_{g.lower()}", nome=f"Scorte petrolifere di emergenza {NOMI[g]} – giorni",
                            gruppo="Petrolio UE", paese=g, unita="giorni equivalenti", frequenza="mensile",
                            fonte="Eurostat nrg_stk_oem (STK_EUE_DIR)",
                            link="https://ec.europa.eu/eurostat/databrowser/view/nrg_stk_oem/default/table",
                            affidabilita="alta", serie_completa=s, tolleranza=3,
                            note="Scorte di emergenza detenute secondo la direttiva 2009/119/CE, in giorni equivalenti "
                                 "(minimo: 90 giorni di importazioni nette o 61 di consumo, il maggiore)."))
    fonti.append({"nome": "Eurostat – Emergency oil stocks in days equivalent, monthly (nrg_stk_oem)",
                  "link": "https://ec.europa.eu/eurostat/databrowser/view/nrg_stk_oem/default/table",
                  "licenza": "CC BY 4.0 (Eurostat)", "data_dato": max(e["data_fonte"] for e in out) if out else agg})
    return out


# ---------------------------------------------------------------- 3. EIA
EIA_SERIE = [
    ("WCSSTUS1", "petrolio_usa_spr", "Strategic Petroleum Reserve (SPR) USA", "Petrolio USA",
     "Greggio nella riserva strategica federale."),
    ("WCESTUS1", "petrolio_usa_greggio_commerciale", "Scorte commerciali di greggio USA (esclusa SPR)", "Petrolio USA", ""),
    ("WGTSTUS1", "petrolio_usa_benzina", "Scorte di benzina USA", "Petrolio USA", ""),
    ("WDISTUS1", "petrolio_usa_distillati", "Scorte di distillati USA (gasolio)", "Petrolio USA", ""),
    ("W_EPC0_SAX_YCUOK_MBBL", "petrolio_usa_cushing", "Scorte di greggio a Cushing, Oklahoma", "Petrolio USA",
     "Hub di consegna del future WTI."),
]
MESI = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def eia_leaf(serie_id):
    html = get(f"https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s={serie_id}&f=W")
    out = []
    for riga in re.findall(r"<tr>(.*?)</tr>", html, re.S):
        m = re.search(r"class='B6'>[^0-9]*(\d{4})-([A-Za-z]{3})", riga)
        if not m:
            continue
        anno, mese = int(m.group(1)), MESI[m.group(2)]
        celle = re.findall(r"class='B5'>([^<]*)</td>\s*<td class='B3'>([^<]*)</td>", riga)
        for data, val in celle:
            data = data.replace("&nbsp;", "").strip()
            val = val.replace("&nbsp;", "").replace(",", "").strip()
            if not data or not re.match(r"^-?\d+(\.\d+)?$", val):
                continue
            mm, gg = map(int, data.split("/"))
            a = anno - 1 if (mese == 1 and mm == 12) else anno
            out.append([dt.date(a, mm, gg).isoformat(), round(float(val) / 1000.0, 3)])  # migliaia -> milioni di barili
    out.sort()
    rel = re.search(r"Release Date:\s*([0-9/]+)", html)
    return out, rel.group(1) if rel else ""


def eia_api(serie_id, key):
    q = [("api_key", key), ("frequency", "weekly"), ("data[0]", "value"), ("facets[series][]", serie_id),
         ("start", INIZIO_STORICO.isoformat()), ("sort[0][column]", "period"), ("sort[0][direction]", "asc"), ("length", 5000)]
    j = json.loads(get("https://api.eia.gov/v2/petroleum/stoc/wstk/data/?" + urllib.parse.urlencode(q)))
    return sorted([[r["period"], round(float(r["value"]) / 1000.0, 3)] for r in j["response"]["data"] if r.get("value") is not None]), ""


def eia():
    out, rilascio = [], ""
    key = os.environ.get("EIA_API_KEY", "").strip()
    for sid, ident, nome, gruppo, nota in EIA_SERIE:
        s = None
        try:
            s, rel = eia_leaf(sid)
            rilascio = rel or rilascio
            if not s:
                raise RuntimeError("tabella vuota")
        except Exception as ex:  # noqa: BLE001
            if key:
                try:
                    s, _ = eia_api(sid, key)
                except Exception as ex2:  # noqa: BLE001
                    avviso(f"EIA {sid}: pagina pubblica ({ex}) e API v2 ({ex2}) non riuscite")
            else:
                avviso(f"EIA {sid}: pagina pubblica non riuscita ({ex}); EIA_API_KEY non impostata per il ripiego API v2")
        if not s:
            continue
        s = [p for p in s if p[0] >= INIZIO_STORICO.isoformat()]
        out.append(elemento(id=ident, nome=nome, gruppo=gruppo, paese="US", unita="milioni di barili", frequenza="settimanale",
                            fonte=f"U.S. EIA, Weekly Petroleum Status Report (serie {sid})",
                            link=f"https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s={sid}&f=W",
                            affidabilita="alta", serie_completa=s, tolleranza=4,
                            note=(nota + " Dato al venerdi' di fine settimana.").strip()))
    if out:
        fonti.append({"nome": "U.S. Energy Information Administration – Weekly Petroleum Status Report",
                      "link": "https://www.eia.gov/petroleum/supply/weekly/", "licenza": "pubblico dominio (governo USA)",
                      "data_dato": max(e["data_fonte"] for e in out) + (f" (rilascio {rilascio})" if rilascio else "")})
    return out


# ---------------------------------------------------------------- 5. USDA PSD grano
PSD_PAESI = [(None, "Mondo (somma paesi PSD)", "WD"), ("CH", "Cina", "CN"), ("US", "Stati Uniti", "US"),
             ("E4", "Unione europea", "EU"), ("RS", "Russia", "RU"), ("IN", "India", "IN")]


def psd_grano():
    z = zipfile.ZipFile(io.BytesIO(get("https://apps.fas.usda.gov/psdonline/downloads/psd_grains_pulses_csv.zip",
                                       binary=True, timeout=240)))
    f = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8-sig")
    stock, cons, mese = {}, {}, {}
    for r in csv.DictReader(f):
        if r["Commodity_Description"] != "Wheat":
            continue
        a = r["Attribute_Description"]
        if a not in ("Ending Stocks", "Domestic Consumption"):
            continue
        y = int(r["Market_Year"])
        if y < OGGI.year - 15:
            continue
        v = float(r["Value"])
        dst = stock if a == "Ending Stocks" else cons
        for c in (None, r["Country_Code"]):
            dst[(c, y)] = dst.get((c, y), 0.0) + v
        if a == "Ending Stocks":
            mese[y] = max(mese.get(y, ""), f"{r['Calendar_Year']}-{r['Month']}")
    out = []
    for cod, nome, iso in PSD_PAESI:
        anni = sorted(y for (c, y) in stock if c == cod)
        if not anni:
            continue
        s = [[f"{y}-01-01", round(stock[(cod, y)] / 1000.0, 2)] for y in anni]   # 1000 t -> milioni di t
        e = elemento(id=f"grano_scorte_finali_{iso.lower()}", nome=f"Grano – scorte finali {nome}", gruppo="Grano",
                     paese=iso if iso != "WD" else "", unita="milioni di tonnellate", frequenza="annuale (anno commerciale)",
                     fonte="USDA FAS PSD (WASDE)", link="https://apps.fas.usda.gov/psdonline/app/index.html#/app/downloads",
                     affidabilita="alta", serie_completa=s, tolleranza=3, inizio=dt.date(OGGI.year - 15, 1, 1),
                     note="Data = anno commerciale (es. 2026-01-01 = campagna 2026/27); l'ultimo anno e' una stima/proiezione USDA "
                          f"(ultimo aggiornamento PSD: {mese.get(anni[-1], 'n.d.')}).")
        c = cons.get((cod, anni[-1]))
        if c:
            e["ultimo"]["rapporto_scorte_consumo_pct"] = r2(stock[(cod, anni[-1])] / c * 100, 1)
            c1 = cons.get((cod, anni[-1] - 1))
            if c1:
                e["ultimo"]["rapporto_scorte_consumo_pct_anno_prec"] = r2(stock[(cod, anni[-1] - 1)] / c1 * 100, 1)
        out.append(e)
    fonti.append({"nome": "USDA Foreign Agricultural Service – Production, Supply and Distribution (PSD)",
                  "link": "https://apps.fas.usda.gov/psdonline/downloads/psd_grains_pulses_csv.zip",
                  "licenza": "pubblico dominio (governo USA)", "data_dato": max(mese.values()) if mese else ""})
    return out


# ---------------------------------------------------------------- 6. FMI IRFCL oro
ORO_PAESI = [("ITA", "Italia", "IT"), ("DEU", "Germania", "DE"), ("FRA", "Francia", "FR"), ("NLD", "Paesi Bassi", "NL"),
             ("USA", "Stati Uniti", "US"), ("CHN", "Cina", "CN"), ("RUS", "Russia", "RU"), ("IND", "India", "IN"),
             ("TUR", "Turchia", "TR"), ("POL", "Polonia", "PL"), ("JPN", "Giappone", "JP"), ("CHE", "Svizzera", "CH")]


def fmi_oro():
    paesi = "+".join(p[0] for p in ORO_PAESI)
    url = (f"https://api.imf.org/external/sdmx/2.1/data/IMF.STA,IRFCL/{paesi}.IRFCLDT1_IRFCL56V_FTO.S1XS1311.M"
           f"?startPeriod={INIZIO_SERIE.strftime('%Y-%m')}")
    xml = get(url, timeout=120)
    dati = {}
    for m in re.finditer(r"<Series ([^>]*)>(.*?)</Series>", xml, re.S):
        attr = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        obs = re.findall(r'TIME_PERIOD="(\d{4})-M(\d{2})"\s+OBS_VALUE="([^"]+)"', m.group(2))
        dati[attr.get("COUNTRY")] = sorted([f"{a}-{mm}-01", round(float(v) / OZ_PER_TONNELLATA, 1)] for a, mm, v in obs)
    out = []
    for cod, nome, iso in ORO_PAESI:
        s = dati.get(cod)
        if not s:
            avviso(f"FMI IRFCL oro: nessun dato per {cod}")
            continue
        out.append(elemento(id=f"oro_riserve_{iso.lower()}", nome=f"Riserve d'oro {nome}", gruppo="Oro", paese=iso,
                            unita="tonnellate", frequenza="mensile", fonte="FMI IRFCL (IRFCLDT1_IRFCL56V_FTO)",
                            link="https://data.imf.org/en/datasets/IMF.STA:IRFCL", affidabilita="alta",
                            serie_completa=s, tolleranza=3,
                            note="Oro monetario (incl. depositi e swap) in once troy convertite in tonnellate (/32.150,7). "
                                 "Autorita' monetarie + governo centrale (S1XS1311)."))
    fonti.append({"nome": "FMI – International Reserves and Foreign Currency Liquidity (IRFCL)",
                  "link": "https://data.imf.org/en/datasets/IMF.STA:IRFCL",
                  "licenza": "© FMI, tutti i diritti riservati; riuso consentito con citazione per uso non commerciale (termini FMI)",
                  "data_dato": max(e["data_fonte"] for e in out) if out else ""})
    return out


# ---------------------------------------------------------------- main
def main(out_path):
    elementi = []
    for nome, fn in [("AGSI+", agsi), ("Eurostat gas", eurostat_gas), ("EIA", eia), ("Eurostat petrolio", eurostat_petrolio),
                     ("USDA PSD", psd_grano), ("FMI oro", fmi_oro)]:
        try:
            r = fn()
            elementi += r
            print(f"{nome}: {len(r)} serie", file=sys.stderr)
        except Exception as ex:  # noqa: BLE001
            avviso(f"{nome}: {ex}")
    riepilogo = []
    for e in elementi:
        u = e.get("ultimo", {})
        x = {"id": e["id"], "nome": e["nome"], "unita": e["unita"], "data": u.get("data"), "valore": u.get("valore")}
        for k in ("precedente", "anno_scorso", "media_5_anni"):
            if k in u:
                x[k] = u[k]
        for k in ("obiettivo_ue", "distanza_obiettivo_pp", "rapporto_scorte_consumo_pct"):
            if k in u:
                x[k] = u[k]
        riepilogo.append(x)
    doc = {
        "aggiornato": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": fonti,
        "nota": ("Scorte strategiche: gas UE (AGSI+ giornaliero se c'e' AGSI_API_KEY, altrimenti Eurostat mensile), petrolio USA "
                 "(EIA settimanale, milioni di barili), scorte petrolifere di emergenza UE (giorni), grano (USDA PSD, scorte finali), "
                 "oro delle banche centrali (FMI, tonnellate). Ogni elemento ha 'serie' [[data, valore]] e 'ultimo' con confronti "
                 "rispetto al dato precedente, all'anno scorso e alla media dei 5 anni precedenti alla stessa data (se disponibile). "
                 "Serie mensili/annuali datate al primo giorno del periodo."),
        "obiettivo_ue_gas_pct": OBIETTIVO_UE_GAS,
        "riepilogo": riepilogo,
        "elementi": elementi,
        "errori": errori,
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"scritto {out_path}: {len(elementi)} serie, {len(errori)} avvisi, {os.path.getsize(out_path)//1024} KB", file=sys.stderr)


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(base, "docs", "data", "scorte.json"))
