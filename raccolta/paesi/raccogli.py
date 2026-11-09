#!/usr/bin/env python3
"""Schede paese: indicatori economici, energetici, commerciali e militari.

Produce docs/data/paesi.json. Solo libreria standard di Python 3.

Fonti (tutte senza chiave, salvo EIA facoltativa):
  - IMF DataMapper API (WEO): crescita, inflazione, debito, partite correnti, PIL/popolazione di riserva
  - World Bank API (WDI): PIL in USD, popolazione, dipendenza energetica (paesi extra Eurostat)
  - SIPRI Military Expenditure Database (xlsx): spesa militare in USD correnti e in % del PIL
  - Our World in Data, energy-data (su dati Energy Institute Statistical Review): produzione di petrolio e gas
  - Eurostat nrg_ind_id: dipendenza energetica dalle importazioni (UE, NO, UK, TR, UA)
  - UN Comtrade public preview API: partner commerciali, import/export di greggio e gas, fornitori di greggio e GNL
  - EIA international (solo se c'e' EIA_API_KEY): produzione ed export di greggio in migliaia di barili al giorno

Uso: python3 raccolta/paesi/raccogli.py
"""
import csv
import datetime as dt
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

RADICE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
USCITA = os.path.join(RADICE, "docs", "data", "paesi.json")
UA = "monitor-geoeconomico/1.0 (osservatorio OSINT personale, non commerciale)"
OGGI = dt.datetime.now(dt.timezone.utc)
ANNO = OGGI.year

# ISO2 -> (nome italiano, ISO3, codice M49 usato da UN Comtrade, nome SIPRI)
PAESI = {
    "US": ("Stati Uniti", "USA", 842, "United States of America"),
    "CN": ("Cina", "CHN", 156, "China"),
    "RU": ("Russia", "RUS", 643, "Russia"),
    "UA": ("Ucraina", "UKR", 804, "Ukraine"),
    "IR": ("Iran", "IRN", 364, "Iran"),
    "IL": ("Israele", "ISR", 376, "Israel"),
    "SA": ("Arabia Saudita", "SAU", 682, "Saudi Arabia"),
    "AE": ("Emirati Arabi Uniti", "ARE", 784, "United Arab Emirates"),
    "QA": ("Qatar", "QAT", 634, "Qatar"),
    "IQ": ("Iraq", "IRQ", 368, "Iraq"),
    "KW": ("Kuwait", "KWT", 414, "Kuwait"),
    "OM": ("Oman", "OMN", 512, "Oman"),
    "YE": ("Yemen", "YEM", 887, "Yemen"),
    "EG": ("Egitto", "EGY", 818, "Egypt"),
    "TR": ("Turchia", "TUR", 792, "Türkiye"),
    "IN": ("India", "IND", 699, "India"),
    "JP": ("Giappone", "JPN", 392, "Japan"),
    "KR": ("Corea del Sud", "KOR", 410, "Korea, South"),
    "TW": ("Taiwan", "TWN", 490, "Taiwan"),
    "DE": ("Germania", "DEU", 276, "Germany"),
    "FR": ("Francia", "FRA", 251, "France"),
    "IT": ("Italia", "ITA", 380, "Italy"),
    "GB": ("Regno Unito", "GBR", 826, "United Kingdom"),
    "ES": ("Spagna", "ESP", 724, "Spain"),
    "NL": ("Paesi Bassi", "NLD", 528, "Netherlands"),
    "PL": ("Polonia", "POL", 616, "Poland"),
    "NO": ("Norvegia", "NOR", 579, "Norway"),
    "AZ": ("Azerbaigian", "AZE", 31, "Azerbaijan"),
    "KZ": ("Kazakistan", "KAZ", 398, "Kazakhstan"),
    "DZ": ("Algeria", "DZA", 12, "Algeria"),
    "LY": ("Libia", "LBY", 434, "Libya"),
    "BR": ("Brasile", "BRA", 76, "Brazil"),
    "NG": ("Nigeria", "NGA", 566, "Nigeria"),
}

# Nomi italiani dei partner commerciali piu' frequenti (ISO2). Gli altri restano in inglese.
NOMI_IT = {p: v[0] for p, v in PAESI.items()}
NOMI_IT.update({
    "CH": "Svizzera", "BE": "Belgio", "AT": "Austria", "CZ": "Cechia", "HU": "Ungheria", "RO": "Romania",
    "SE": "Svezia", "DK": "Danimarca", "FI": "Finlandia", "IE": "Irlanda", "PT": "Portogallo", "GR": "Grecia",
    "SK": "Slovacchia", "SI": "Slovenia", "HR": "Croazia", "BG": "Bulgaria", "LU": "Lussemburgo",
    "CA": "Canada", "MX": "Messico", "AR": "Argentina", "CL": "Cile", "CO": "Colombia", "PE": "Perù",
    "VN": "Vietnam", "SG": "Singapore", "MY": "Malaysia", "TH": "Thailandia", "ID": "Indonesia",
    "PH": "Filippine", "AU": "Australia", "NZ": "Nuova Zelanda", "HK": "Hong Kong", "BD": "Bangladesh",
    "PK": "Pakistan", "LK": "Sri Lanka", "BH": "Bahrein", "JO": "Giordania", "LB": "Libano", "SY": "Siria",
    "TN": "Tunisia", "MA": "Marocco", "ZA": "Sudafrica", "AO": "Angola", "GH": "Ghana", "CI": "Costa d'Avorio",
    "BY": "Bielorussia", "GE": "Georgia", "AM": "Armenia", "UZ": "Uzbekistan", "TM": "Turkmenistan",
    "KG": "Kirghizistan", "TJ": "Tagikistan", "MN": "Mongolia", "KP": "Corea del Nord", "MD": "Moldavia",
    "RS": "Serbia", "LT": "Lituania", "LV": "Lettonia", "EE": "Estonia", "CY": "Cipro", "MT": "Malta",
    "SD": "Sudan", "ET": "Etiopia", "KE": "Kenya", "SN": "Senegal", "CM": "Camerun", "TG": "Togo",
    "BJ": "Benin", "GA": "Gabon", "CG": "Congo", "GQ": "Guinea Equatoriale", "VE": "Venezuela",
    "GY": "Guyana", "EC": "Ecuador", "TT": "Trinidad e Tobago", "PA": "Panama", "MZ": "Mozambico",
    "PG": "Papua Nuova Guinea", "BN": "Brunei", "AF": "Afghanistan", "KH": "Cambogia", "MM": "Myanmar",
    "IS": "Islanda", "DJ": "Gibuti", "SO": "Somalia", "ER": "Eritrea", "MR": "Mauritania", "UY": "Uruguay",
    "PY": "Paraguay", "BO": "Bolivia", "CU": "Cuba", "DO": "Repubblica Dominicana", "SV": "El Salvador",
    "GT": "Guatemala", "CR": "Costa Rica", "MO": "Macao", "NE": "Niger", "ML": "Mali", "TD": "Ciad",
    "CD": "Congo (RD)", "TZ": "Tanzania", "UG": "Uganda", "ZM": "Zambia", "ZW": "Zimbabwe", "NA": "Namibia",
    "BW": "Botswana", "MG": "Madagascar", "LR": "Liberia", "SL": "Sierra Leone", "GN": "Guinea",
})

# Produttori del Golfo Persico: per il proxy di esposizione a Hormuz.
GOLFO_SOLO_HORMUZ = {"IQ": 368, "KW": 414, "QA": 634, "BH": 48, "IR": 364}  # nessuna via d'uscita alternativa rilevante
GOLFO_CON_BYPASS = {"SA": 682, "AE": 784}  # Yanbu (Mar Rosso) e Fujairah (golfo di Oman) permettono di aggirare in parte lo stretto

errori = []
fonti_usate = {}


def avviso(msg):
    print("AVVISO:", msg, file=sys.stderr)
    errori.append(msg)


def scarica(url, tentativi=3, pausa=3, timeout=90, binario=False):
    ultimo = None
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                dati = r.read()
            return dati if binario else dati.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            ultimo = e
            if e.code == 404:
                break
            time.sleep(pausa * (i + 1) + (5 if e.code == 429 else 0))
        except Exception as e:  # rete, timeout
            ultimo = e
            time.sleep(pausa * (i + 1))
    raise RuntimeError(f"{url}: {ultimo}")


def scarica_json(url, **kw):
    return json.loads(scarica(url, **kw))


def voce(valore, anno, fonte, link, unita=None, nota=None):
    if valore is None:
        return None
    d = {"valore": valore, "anno": anno, "fonte": fonte, "link": link}
    if unita:
        d["unita"] = unita
    if nota:
        d["nota"] = nota
    return d


def tondo(x, n=2):
    return None if x is None else round(float(x), n)


# ---------------------------------------------------------------- IMF WEO
IMF_BASE = "https://www.imf.org/external/datamapper/api/v1"


def raccogli_imf():
    ind = ["NGDPD", "NGDP_RPCH", "PCPIPCH", "GGXWDG_NGDP", "BCA_NGDPD", "LP"]
    out, meta = {}, {}
    try:
        m = scarica_json(IMF_BASE + "/indicators")["indicators"]
        meta = {k: m.get(k, {}) for k in ind}
    except Exception as e:
        avviso(f"IMF metadati non letti: {e}")
    for k in ind:
        try:
            d = scarica_json(f"{IMF_BASE}/{k}", timeout=120)
            out[k] = d["values"][k]
        except Exception as e:
            avviso(f"IMF {k} non scaricato: {e}")
            out[k] = {}
    src = (meta.get("NGDP_RPCH") or {}).get("source", "World Economic Outlook")
    fonti_usate["imf"] = {"nome": f"FMI, DataMapper API ({src})", "link": IMF_BASE,
                          "licenza": "Termini d'uso FMI: riuso consentito con citazione della fonte",
                          "data_dato": (meta.get("NGDP_RPCH") or {}).get("last-modified", "")[:10]}
    return out, src


# ---------------------------------------------------------------- World Bank
WB_BASE = "https://api.worldbank.org/v2"


def raccogli_wb(codici):
    ind = {"NY.GDP.MKTP.CD": "pil", "SP.POP.TOTL": "pop", "EG.IMP.CONS.ZS": "dip_en",
           "MS.MIL.XPND.GD.ZS": "mil_pil", "MS.MIL.XPND.CD": "mil_usd"}
    out = {}
    for code in ind:
        url = f"{WB_BASE}/country/{';'.join(codici)}/indicator/{code}?format=json&per_page=2000&date={ANNO-16}:{ANNO}"
        try:
            d = scarica_json(url)
            for r in d[1] or []:
                iso2 = r["country"]["id"]
                if r["value"] is None:
                    continue
                out.setdefault(iso2, {}).setdefault(code, {})[int(r["date"])] = r["value"]
        except Exception as e:
            avviso(f"World Bank {code} non scaricato: {e}")
    fonti_usate["wb"] = {"nome": "Banca Mondiale, World Development Indicators (API v2)", "link": WB_BASE,
                         "licenza": "CC BY 4.0", "data_dato": OGGI.strftime("%Y-%m-%d")}
    return out


def ultimo(serie):
    if not serie:
        return None, None
    a = max(serie)
    return serie[a], a


# ---------------------------------------------------------------- SIPRI
def leggi_xlsx(dati):
    """Legge un xlsx: restituisce {nome_foglio: [righe come liste]}. Solo valori."""
    z = zipfile.ZipFile(io.BytesIO(dati))
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    condivise = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns):
            condivise.append("".join(t.text or "" for t in si.iter("{%s}t" % ns["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    mappa = {r.get("Id"): r.get("Target") for r in rels}
    fogli = {}
    for s in wb.find("m:sheets", ns):
        rid = s.get("{%s}id" % ns["r"])
        tgt = mappa[rid].lstrip("/")
        tgt = tgt if tgt.startswith("xl/") else "xl/" + tgt
        righe = []
        for row in ET.fromstring(z.read(tgt)).iter("{%s}row" % ns["m"]):
            celle = {}
            for c in row.findall("m:c", ns):
                ref = re.match(r"([A-Z]+)", c.get("r")).group(1)
                col = 0
                for ch in ref:
                    col = col * 26 + ord(ch) - 64
                v = c.find("m:v", ns)
                if v is None:
                    t = c.find(".//m:t", ns)
                    val = t.text if t is not None else None
                elif c.get("t") == "s":
                    val = condivise[int(v.text)]
                else:
                    val = v.text
                celle[col - 1] = val
            if celle:
                righe.append([celle.get(i) for i in range(max(celle) + 1)])
        fogli[s.get("name")] = righe
    return fogli


def raccogli_sipri():
    url_ok, dati = None, None
    for y in (ANNO, ANNO - 1, ANNO - 2):
        for suff in ("", "_2", "_1", "_0"):
            url = f"https://www.sipri.org/sites/default/files/SIPRI-Milex-data-1949-{y}{suff}.xlsx"
            try:
                dati = scarica(url, tentativi=1, binario=True)
                if dati[:2] == b"PK":
                    url_ok = url
                    break
            except Exception:
                continue
        if url_ok:
            break
    if not url_ok:
        avviso("SIPRI: file xlsx non trovato; uso la copia SIPRI nella World Bank")
        return {}, None
    fogli = leggi_xlsx(dati)
    out = {}
    for nome_f, chiave in (("Current US$", "usd"), ("Share of GDP", "pil")):
        righe = fogli.get(nome_f)
        if not righe:
            avviso(f"SIPRI: foglio {nome_f} assente")
            continue
        intest = None
        for r in righe:
            if r and r[0] == "Country":
                intest = r
                continue
            if intest and r and r[0]:
                serie = {}
                for i, v in enumerate(r):
                    if i >= len(intest) or intest[i] is None:
                        continue
                    try:
                        anno = int(float(intest[i]))
                        serie[anno] = float(v)
                    except (TypeError, ValueError):
                        continue
                if serie:
                    out.setdefault(r[0].strip(), {})[chiave] = serie
    fonti_usate["sipri"] = {"nome": "SIPRI Military Expenditure Database", "link": url_ok,
                            "licenza": "Dati SIPRI: uso libero non commerciale con citazione (non CC)",
                            "data_dato": re.search(r"1949-(\d{4})", url_ok).group(1)}
    return out, url_ok


# ---------------------------------------------------------------- OWID / Energy Institute
OWID_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"


def raccogli_owid(iso3s):
    try:
        testo = scarica(OWID_URL, timeout=180)
    except Exception as e:
        avviso(f"OWID energy-data non scaricato: {e}")
        return {}
    out = {}
    for r in csv.DictReader(io.StringIO(testo)):
        if r["iso_code"] not in iso3s:
            continue
        for col in ("oil_production", "gas_production", "oil_consumption", "gas_consumption"):
            if r.get(col):
                out.setdefault(r["iso_code"], {}).setdefault(col, {})[int(r["year"])] = float(r[col])
    fonti_usate["owid"] = {"nome": "Our World in Data, energy-data (dati Energy Institute, Statistical Review of World Energy)",
                           "link": "https://github.com/owid/energy-data",
                           "licenza": "CC BY 4.0 (OWID); dati di base Energy Institute, citare la fonte",
                           "data_dato": OGGI.strftime("%Y-%m-%d")}
    return out


# ---------------------------------------------------------------- Eurostat
def raccogli_eurostat():
    url = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_ind_id?format=JSON&lang=EN"
           "&unit=PC&siec=TOTAL&siec=G3000&siec=O4000XBIO&siec=C0000X0350-0370&sinceTimePeriod=" + str(ANNO - 6))
    try:
        d = scarica_json(url, timeout=120)
    except Exception as e:
        avviso(f"Eurostat nrg_ind_id non scaricato: {e}")
        return {}
    dims = d["id"]
    size = d["size"]
    idx = {k: d["dimension"][k]["category"]["index"] for k in dims}
    inv = {k: {v: c for c, v in idx[k].items()} for k in dims}
    out = {}
    for pos, val in d["value"].items():
        pos = int(pos)
        coord = {}
        for k, s in zip(reversed(dims), reversed(size)):
            coord[k] = inv[k][pos % s]
            pos //= s
        geo = {"EL": "GR", "UK": "GB"}.get(coord["geo"], coord["geo"])
        out.setdefault(geo, {}).setdefault(coord["siec"], {})[int(coord["time"])] = val
    fonti_usate["eurostat"] = {"nome": "Eurostat, Energy imports dependency (nrg_ind_id)",
                               "link": "https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_id/default/table",
                               "licenza": "CC BY 4.0 (riuso Commissione europea)", "data_dato": d.get("updated", "")[:10]}
    return out


# ---------------------------------------------------------------- UN Comtrade
CT_BASE = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
_ct_ultima = [0.0]


def comtrade(**params):
    attesa = 1.3 - (time.time() - _ct_ultima[0])
    if attesa > 0:
        time.sleep(attesa)
    url = CT_BASE + "?" + urllib.parse.urlencode(params)
    for i in range(5):
        _ct_ultima[0] = time.time()
        try:
            testo = scarica(url, tentativi=1, timeout=90)
        except Exception as e:
            if i == 4:
                raise
            time.sleep(4 + 3 * i)
            continue
        d = json.loads(testo)
        if d.get("statusCode") == 429 or ("data" not in d and not d.get("error")):
            time.sleep(4 + 3 * i)
            continue
        if d.get("error"):
            raise RuntimeError(d["error"])
        return d["data"]
    raise RuntimeError("Comtrade: troppi tentativi (limite di frequenza)")


def partner_ref():
    try:
        d = scarica_json("https://comtradeapi.un.org/files/v1/app/reference/partnerAreas.json")
        ref = {}
        for r in d["results"]:
            ref[r["PartnerCode"]] = (r.get("PartnerCodeIsoAlpha2") or "", r["PartnerDesc"], r.get("isGroup"))
        ref[490] = ("TW", "Taiwan", False)
        return ref
    except Exception as e:
        avviso(f"Comtrade: elenco partner non letto: {e}")
        return {}


def nome_partner(ref, code):
    iso, nome, _ = ref.get(code, ("", str(code), False))
    return iso, NOMI_IT.get(iso, nome)


def partner_validi(righe, ref):
    tot = None
    parti = []
    for x in righe:
        c = x["partnerCode"]
        if x.get("partner2Code", 0) != 0 or x.get("motCode", 0) != 0 or x.get("customsCode", "C00") != "C00":
            continue
        if c == 0:
            tot = x["primaryValue"]
            continue
        iso, nome, grp = ref.get(c, ("", "", False))
        if grp or (("nes" in nome.lower() or "bunkers" in nome.lower() or "free zones" in nome.lower()) and c != 490):
            continue
        parti.append(x)
    return tot, parti


def top(ref, parti, tot, n=5):
    parti = sorted(parti, key=lambda x: -x["primaryValue"])[:n]
    res = []
    for x in parti:
        iso, nome = nome_partner(ref, x["partnerCode"])
        res.append({"paese": iso or None, "nome": nome, "valore_usd": round(x["primaryValue"]),
                    "quota_pct": tondo(100 * x["primaryValue"] / tot, 1) if tot else None})
    return res


def raccogli_comtrade(iso2, m49, ref):
    """Restituisce un dict di indicatori commerciali; None se il paese non riporta a Comtrade."""
    anno, righe_x = None, None
    for y in (ANNO - 1, ANNO - 2, ANNO - 3):
        try:
            r = comtrade(reporterCode=m49, period=y, flowCode="X", cmdCode="TOTAL")
        except Exception as e:
            avviso(f"Comtrade {iso2} {y} export totale: {e}")
            continue
        if r:
            anno, righe_x = y, r
            break
    if not anno:
        return None
    link = f"https://comtradeplus.un.org/TradeFlow?Frequency=A&Flows=X&CommodityCodes=TOTAL&Partners=0&Reporters={m49}&period={anno}&AggregateBy=none&BreakdownMode=plus"
    fonte = f"UN Comtrade (dati dichiarati da {PAESI[iso2][0]}, HS)"
    out = {"anno": anno, "link": link, "fonte": fonte}
    tot_x, px = partner_validi(righe_x, ref)
    out["export_totale_usd"] = tot_x
    out["partner_export"] = top(ref, px, tot_x)
    try:
        tot_m, pm = partner_validi(comtrade(reporterCode=m49, period=anno, flowCode="M", cmdCode="TOTAL"), ref)
        out["import_totale_usd"] = tot_m
        out["partner_import"] = top(ref, pm, tot_m)
    except Exception as e:
        avviso(f"Comtrade {iso2} import totale: {e}")
    # Energia: greggio 2709, GNL 271111, gas via gasdotto 271121
    try:
        en = {}
        for x in comtrade(reporterCode=m49, period=anno, flowCode="X,M", cmdCode="2709,271111,271121", partnerCode=0):
            if x.get("motCode", 0) != 0 or x.get("customsCode", "C00") != "C00" or x.get("partner2Code", 0) != 0:
                continue
            en[(x["flowCode"], x["cmdCode"])] = (x["primaryValue"], x.get("netWgt") or None)
        out["energia"] = en
    except Exception as e:
        avviso(f"Comtrade {iso2} scambi di energia: {e}")
    # Fornitori di greggio e GNL (per esposizione a Hormuz)
    try:
        forn = {"2709": [], "271111": []}
        tot = {}
        for x in comtrade(reporterCode=m49, period=anno, flowCode="M", cmdCode="2709,271111"):
            if x.get("motCode", 0) != 0 or x.get("customsCode", "C00") != "C00" or x.get("partner2Code", 0) != 0:
                continue
            if x["partnerCode"] == 0:
                tot[x["cmdCode"]] = x["primaryValue"]
            else:
                forn[x["cmdCode"]].append(x)
        out["fornitori"] = (forn, tot)
    except Exception as e:
        avviso(f"Comtrade {iso2} fornitori di greggio/GNL: {e}")
    return out


# ---------------------------------------------------------------- EIA (facoltativa)
def raccogli_eia(iso3s):
    key = os.environ.get("EIA_API_KEY")
    if not key:
        print("AVVISO: EIA_API_KEY assente, salto EIA international (produzione/export in barili)", file=sys.stderr)
        return {}
    out = {}
    # productId 57 = greggio incl. condensato; activityId 1 = produzione, 4 = export; unita' TBPD
    for act, chiave in ((1, "prod"), (4, "exp")):
        q = {"api_key": key, "frequency": "annual", "data[0]": "value", "facets[productId][]": "57",
             "facets[activityId][]": str(act), "facets[unit][]": "TBPD", "start": str(ANNO - 6), "length": "5000"}
        url = "https://api.eia.gov/v2/international/data/?" + urllib.parse.urlencode(q)
        for i3 in iso3s:
            url += "&facets%5BcountryRegionId%5D%5B%5D=" + i3
        try:
            for r in scarica_json(url)["response"]["data"]:
                try:
                    v = float(r["value"])
                except (TypeError, ValueError):
                    continue
                out.setdefault(r["countryRegionId"], {}).setdefault(chiave, {})[int(r["period"])] = v
        except Exception as e:
            avviso(f"EIA {chiave}: {e}")
    if out:
        fonti_usate["eia"] = {"nome": "U.S. EIA, International Energy Data (API v2)", "link": "https://www.eia.gov/international/data/world",
                              "licenza": "Pubblico dominio (governo USA)", "data_dato": OGGI.strftime("%Y-%m-%d")}
    return out


# ---------------------------------------------------------------- composizione
def serie_ann(d, da, a):
    return [[f"{y}-12-31", tondo(d[y], 3)] for y in range(da, a + 1) if y in d and d[y] is not None]


def main():
    iso2s = list(PAESI)
    iso3s = {v[1] for v in PAESI.values()}
    imf, imf_src = raccogli_imf()
    wb = raccogli_wb(iso2s)
    sipri, sipri_url = raccogli_sipri()
    owid = raccogli_owid(iso3s)
    euro = raccogli_eurostat()
    eia = raccogli_eia(iso3s)
    ref = partner_ref()
    if ref:
        fonti_usate["comtrade"] = {"nome": "UN Comtrade, API pubblica (preview, senza chiave)", "link": "https://comtradeplus.un.org/",
                                   "licenza": "Termini d'uso UN Comtrade: consultazione libera, riuso con citazione; verificare per usi commerciali",
                                   "data_dato": OGGI.strftime("%Y-%m-%d")}
    anno_rif = ANNO - 1  # ultimo anno concluso: nel WEO e' stima/consuntivo
    anno_prev = ANNO     # anno in corso: previsione WEO
    imf_link = "https://www.imf.org/external/datamapper/{}/{}"
    elementi = []
    for iso2, (nome, iso3, m49, sipri_nome) in PAESI.items():
        print(f"... {iso2} {nome}", file=sys.stderr)
        ind, serie, buchi = {}, {}, []
        fonte_imf = f"FMI, {imf_src}"

        def imf_val(k, y):
            return (imf.get(k, {}).get(iso3) or {}).get(str(y))

        # PIL in USD: World Bank, altrimenti FMI
        w = wb.get(iso2, {})
        v, a = ultimo(w.get("NY.GDP.MKTP.CD"))
        if v is not None:
            ind["pil_usd"] = voce(round(v), a, "Banca Mondiale, WDI (NY.GDP.MKTP.CD)",
                                  f"https://data.worldbank.org/indicator/NY.GDP.MKTP.CD?locations={iso2}", "USD correnti")
            serie["pil_usd"] = serie_ann({y: x / 1e9 for y, x in w["NY.GDP.MKTP.CD"].items()}, anno_rif - 9, anno_rif)
            serie["pil_usd_fonte"] = "Banca Mondiale, WDI; miliardi di USD correnti"
        elif imf_val("NGDPD", anno_rif) is not None:
            ind["pil_usd"] = voce(round(imf_val("NGDPD", anno_rif) * 1e9), anno_rif, fonte_imf + " (NGDPD)",
                                  imf_link.format("NGDPD", iso3), "USD correnti",
                                  "Assente in World Bank: dato FMI (stima WEO)")
            d = {y: imf_val("NGDPD", y) for y in range(anno_rif - 9, anno_rif + 1)}
            serie["pil_usd"] = serie_ann({k: x for k, x in d.items() if x is not None}, anno_rif - 9, anno_rif)
            serie["pil_usd_fonte"] = "FMI WEO (NGDPD); miliardi di USD correnti"
        else:
            buchi.append("PIL in USD")
        if imf_val("NGDPD", anno_prev) is not None:
            ind["pil_usd_previsione"] = voce(round(imf_val("NGDPD", anno_prev) * 1e9), anno_prev, fonte_imf + " (NGDPD)",
                                             imf_link.format("NGDPD", iso3), "USD correnti", "Previsione WEO")
        for k, chiave, unita, nm in (("NGDP_RPCH", "crescita_pil", "% annua, PIL reale", "crescita"),
                                     ("PCPIPCH", "inflazione", "% annua, prezzi al consumo medi", "inflazione"),
                                     ("GGXWDG_NGDP", "debito_pubblico_pil", "% del PIL, debito lordo delle amministrazioni pubbliche", None),
                                     ("BCA_NGDPD", "partite_correnti_pil", "% del PIL", None)):
            x = imf_val(k, anno_rif)
            if x is not None:
                ind[chiave] = voce(x, anno_rif, f"{fonte_imf} ({k})", imf_link.format(k, iso3), unita,
                                   "Stima/consuntivo WEO per l'ultimo anno concluso")
            else:
                buchi.append(f"{chiave} (FMI {k} assente per {anno_rif})")
            xp = imf_val(k, anno_prev)
            if xp is not None:
                ind[chiave + "_previsione"] = voce(xp, anno_prev, f"{fonte_imf} ({k})", imf_link.format(k, iso3), unita, "Previsione WEO")
            if nm:
                d = {y: imf_val(k, y) for y in range(anno_rif - 9, anno_rif + 1)}
                serie[nm] = serie_ann({y: x for y, x in d.items() if x is not None}, anno_rif - 9, anno_rif)
                serie[nm + "_fonte"] = f"{fonte_imf} ({k}); %"
        # Popolazione
        v, a = ultimo(w.get("SP.POP.TOTL"))
        if v is not None:
            ind["popolazione"] = voce(round(v), a, "Banca Mondiale, WDI (SP.POP.TOTL)",
                                      f"https://data.worldbank.org/indicator/SP.POP.TOTL?locations={iso2}", "persone")
        elif imf_val("LP", anno_rif) is not None:
            ind["popolazione"] = voce(round(imf_val("LP", anno_rif) * 1e6), anno_rif, fonte_imf + " (LP)",
                                      imf_link.format("LP", iso3), "persone", "Assente in World Bank: dato FMI")
        else:
            buchi.append("popolazione")
        # Spesa militare: SIPRI, altrimenti copia SIPRI nella World Bank
        s = sipri.get(sipri_nome, {})
        su, sp = s.get("usd", {}), s.get("pil", {})
        if su:
            a = max(su)
            ind["spesa_militare_usd"] = voce(round(su[a] * 1e6), a, "SIPRI Military Expenditure Database", sipri_url, "USD correnti")
            serie["spesa_militare_usd"] = serie_ann({y: x / 1e3 for y, x in su.items()}, a - 9, a)
            serie["spesa_militare_usd_fonte"] = "SIPRI; miliardi di USD correnti"
        elif w.get("MS.MIL.XPND.CD"):
            v, a = ultimo(w["MS.MIL.XPND.CD"])
            ind["spesa_militare_usd"] = voce(round(v), a, "Banca Mondiale (da SIPRI), MS.MIL.XPND.CD",
                                             f"https://data.worldbank.org/indicator/MS.MIL.XPND.CD?locations={iso2}", "USD correnti")
        else:
            buchi.append("spesa militare in USD (SIPRI non riporta stime recenti)")
        if sp:
            a = max(sp)
            ind["spesa_militare_pil"] = voce(tondo(sp[a] * 100, 2), a, "SIPRI Military Expenditure Database", sipri_url, "% del PIL")
        elif w.get("MS.MIL.XPND.GD.ZS"):
            v, a = ultimo(w["MS.MIL.XPND.GD.ZS"])
            ind["spesa_militare_pil"] = voce(tondo(v, 2), a, "Banca Mondiale (da SIPRI), MS.MIL.XPND.GD.ZS",
                                             f"https://data.worldbank.org/indicator/MS.MIL.XPND.GD.ZS?locations={iso2}", "% del PIL")
        else:
            buchi.append("spesa militare in % del PIL")
        # Energia: produzione (OWID/EI)
        o = owid.get(iso3, {})
        for col, chiave, lab in (("oil_production", "petrolio_produzione", "petrolio"),
                                 ("gas_production", "gas_produzione", "gas naturale"),
                                 ("oil_consumption", "petrolio_consumo", "petrolio"),
                                 ("gas_consumption", "gas_consumo", "gas naturale")):
            if o.get(col):
                v, a = ultimo(o[col])
                ind[chiave] = voce(tondo(v, 1), a, "Energy Institute, Statistical Review of World Energy (via Our World in Data)",
                                   "https://github.com/owid/energy-data", "TWh (energia primaria)")
            elif col.endswith("production"):
                buchi.append(f"produzione di {lab} (assente in OWID/EI)")
        e = eia.get(iso3, {})
        if e.get("prod"):
            v, a = ultimo(e["prod"])
            ind["greggio_produzione_kbd"] = voce(tondo(v, 1), a, "EIA international", "https://www.eia.gov/international/data/world", "migliaia di barili/giorno")
        if e.get("exp"):
            v, a = ultimo(e["exp"])
            ind["greggio_export_kbd"] = voce(tondo(v, 1), a, "EIA international", "https://www.eia.gov/international/data/world", "migliaia di barili/giorno")
        # Dipendenza energetica
        eu = euro.get(iso2)
        if eu and eu.get("TOTAL"):
            v, a = ultimo(eu["TOTAL"])
            lk = "https://ec.europa.eu/eurostat/databrowser/view/nrg_ind_id/default/table"
            ind["dipendenza_energetica"] = voce(tondo(v, 1), a, "Eurostat (nrg_ind_id)", lk, "% importazioni nette sul fabbisogno lordo",
                                               "Valori negativi = esportatore netto")
            for sc, ch in (("G3000", "dipendenza_gas"), ("O4000XBIO", "dipendenza_petrolio"), ("C0000X0350-0370", "dipendenza_carbone")):
                if eu.get(sc):
                    v, a = ultimo(eu[sc])
                    ind[ch] = voce(tondo(v, 1), a, "Eurostat (nrg_ind_id)", lk, "% importazioni nette sul fabbisogno lordo",
                                   "Oltre 100% = scorte accumulate o riesportazioni; negativo = esportatore netto")
        elif w.get("EG.IMP.CONS.ZS"):
            v, a = ultimo(w["EG.IMP.CONS.ZS"])
            ind["dipendenza_energetica"] = voce(tondo(v, 1), a, "Banca Mondiale, WDI (EG.IMP.CONS.ZS, dati IEA)",
                                               f"https://data.worldbank.org/indicator/EG.IMP.CONS.ZS?locations={iso2}",
                                               "% importazioni nette sull'uso di energia", "Valori negativi = esportatore netto")
        else:
            buchi.append("dipendenza energetica")
        # Commercio (Comtrade)
        commercio = None
        if ref:
            try:
                commercio = raccogli_comtrade(iso2, m49, ref)
            except Exception as ex:
                avviso(f"Comtrade {iso2}: {ex}")
        if commercio:
            a, lk, fc = commercio["anno"], commercio["link"], commercio["fonte"]
            nota_tw = "Taiwan in Comtrade e' 'Other Asia, nes' (codice 490)" if iso2 == "TW" else None
            if commercio.get("export_totale_usd"):
                ind["export_merci_usd"] = voce(round(commercio["export_totale_usd"]), a, fc, lk, "USD", nota_tw)
            if commercio.get("import_totale_usd"):
                ind["import_merci_usd"] = voce(round(commercio["import_totale_usd"]), a, fc, lk, "USD", nota_tw)
            if commercio.get("partner_export"):
                ind["partner_export"] = voce(commercio["partner_export"], a, fc, lk, "primi 5 mercati di sbocco, USD e % dell'export")
            if commercio.get("partner_import"):
                ind["partner_import"] = voce(commercio["partner_import"], a, fc, lk, "primi 5 fornitori, USD e % dell'import")
            en = commercio.get("energia", {})
            for (fl, cmd), ch in ((("X", "2709"), "export_greggio"), (("M", "2709"), "import_greggio"),
                                  (("X", "271111"), "export_gnl"), (("M", "271111"), "import_gnl"),
                                  (("X", "271121"), "export_gas_gasdotto"), (("M", "271121"), "import_gas_gasdotto")):
                if (fl, cmd) in en and en[(fl, cmd)][0]:
                    val, peso = en[(fl, cmd)]
                    d = voce({"usd": round(val), "tonnellate": round(peso / 1000) if peso else None}, a, fc, lk,
                             f"HS {cmd}: valore in USD e peso netto in tonnellate")
                    ind[ch] = d
            if commercio.get("fornitori"):
                forn, tot = commercio["fornitori"]
                for cmd, ch in (("2709", "greggio"), ("271111", "gnl")):
                    if not tot.get(cmd) or tot[cmd] < 1e8:  # sotto 100 milioni di USD non e' significativo
                        continue
                    ind[f"fornitori_{ch}"] = voce(top(ref, forn[cmd], tot[cmd]), a, fc, lk, "primi 5 fornitori, USD e % del totale importato")
                    somma_h = sum(x["primaryValue"] for x in forn[cmd] if x["partnerCode"] in GOLFO_SOLO_HORMUZ.values())
                    somma_b = sum(x["primaryValue"] for x in forn[cmd] if x["partnerCode"] in GOLFO_CON_BYPASS.values())
                    ind[f"quota_{ch}_golfo_persico"] = voce(
                        {"min_pct": tondo(100 * somma_h / tot[cmd], 1), "max_pct": tondo(100 * (somma_h + somma_b) / tot[cmd], 1)},
                        a, fc, lk, "% del valore importato",
                        "Proxy dell'esposizione a Hormuz. min = Iraq, Kuwait, Qatar, Bahrein, Iran (nessuna uscita alternativa); "
                        "max = anche Arabia Saudita ed Emirati (che possono esportare in parte da Yanbu e Fujairah). "
                        "Oman escluso (porti fuori dallo stretto). Basato sulle dichiarazioni dell'importatore: "
                        "l'origine puo' essere mascherata (es. greggio iraniano dichiarato come malese).")
        else:
            buchi.append("commercio e partner (il paese non riporta a UN Comtrade negli ultimi 3 anni)")
        ind["rating_sovrano"] = None
        buchi.append("rating sovrano: nessuna fonte aperta e riutilizzabile (S&P, Moody's, Fitch sono proprietari)")
        if iso2 == "TW":
            buchi.append("Taiwan non e' nella World Bank: PIL, popolazione e dipendenza energetica da FMI o assenti")
        elementi.append({"paese": iso2, "iso3": iso3, "nome": nome,
                         "indicatori": {k: v for k, v in ind.items() if v is not None or k == "rating_sovrano"},
                         "serie": serie, "buchi": buchi})
    doc = {
        "aggiornato": OGGI.strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": list(fonti_usate.values()),
        "nota": ("Schede paese. Ogni indicatore e' {valore, anno, fonte, link, unita, nota}. "
                 f"Per FMI: anno {anno_rif} = ultimo anno concluso (stima/consuntivo WEO), {anno_prev} = previsione. "
                 "Serie annuali con data convenzionale AAAA-12-31. Energia in TWh di energia primaria (Energy Institute). "
                 "Comtrade: valori dichiarati dal paese, ultimo anno disponibile; quota Golfo Persico = proxy di esposizione a Hormuz."),
        "elementi": elementi,
        "errori": errori,
    }
    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    with open(USCITA, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Scritto {USCITA}: {len(elementi)} paesi, {len(errori)} avvisi", file=sys.stderr)


if __name__ == "__main__":
    main()
