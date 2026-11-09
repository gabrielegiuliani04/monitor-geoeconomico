#!/usr/bin/env python3
"""Agente RISORSE E COMMERCIO.

Produce:
  docs/data/commercio.json  per paese: anno, totali, primi capitoli HS esportati e importati,
                            primi partner, voci strategiche (HS4), risorse energetiche e minerarie;
                            piu' "dipendenze": prodotti per cui Italia e UE dipendono per oltre il 50%
                            da un solo fornitore.
  docs/data/minerali.json   per minerale: produttori, quote mondiali, riserve, anno.

Fonti (nessuna chiave richiesta):
  - UN Comtrade, endpoint pubblico "public/v1/preview" (max 500 righe e 1 anno per chiamata).
  - USGS Mineral Commodity Summaries 2026, data release (ScienceBase, pubblico dominio).
  - EIA International Energy Data, bulk INTL.zip (pubblico dominio).
  - CIA World Factbook (mirror JSON github factbook/factbook.json, pubblico dominio): riserve petrolio e gas.
  - World Nuclear Association, tabella produzione mineraria di uranio (uso informativo, citare la fonte).

Uso:  python3 raccolta/commercio/raccogli.py [cartella_docs_data]
Solo libreria standard. Se una fonte non risponde, la salta e lo scrive in "errori".
"""
import csv, hashlib, io, json, os, re, sys, time, urllib.parse, urllib.request, zipfile
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (monitor-osint commercio)"}
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "..", "docs", "data")
ERR = []
ADESSO = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

PAESI = "US CN RU UA IR IL SA AE QA IQ KW OM YE EG TR IN JP KR TW DE FR IT GB ES NL PL NO AZ KZ DZ LY BR NG AU CL CD ID ZA".split()
# Paesi per cui il dato dichiarato a Comtrade manca o e' incompleto: si usano i dati dei partner (specchio).
SPECCHIO = {"RU": "nessun dato dichiarato dal 2022", "LY": "nessun dato dichiarato recente",
            "YE": "dato dichiarato 2024 incompleto (import 3 mld USD)"}
ANNI = [2025, 2024, 2023, 2022]
ANNO_SPECCHIO = 2024

CT = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
CT_REF = "https://comtradeapi.un.org/files/v1/app/reference/"
USGS_ITEM = "https://www.sciencebase.gov/catalog/item/696a75d5d4be0228872d3bf8"
USGS_PAGINA = "https://www.usgs.gov/data/mineral-commodity-summaries-2026-data-release"
EIA_BULK = "https://www.eia.gov/opendata/bulk/INTL.zip"
FACTBOOK = "https://raw.githubusercontent.com/factbook/factbook.json/master/"
WNA = "https://world-nuclear.org/information-library/nuclear-fuel-cycle/mining-of-uranium/world-uranium-mining-production"

# ---------------------------------------------------------------- utilita'

def get(url, tries=5, binary=False, timeout=90):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                b = r.read()
                return b if binary else b.decode("utf-8", errors="replace")
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep((20 if "429" in str(e) else 4) * (i + 1))


_ultima = [0.0]


def comtrade(**q):
    """Una chiamata all'endpoint preview. Ritorna la lista 'data' (righe gia' filtrate sui totali)."""
    url = CT + "?" + urllib.parse.urlencode({k: v for k, v in q.items() if v is not None})
    cache = os.environ.get("COMMERCIO_CACHE")  # facoltativo: cartella per riusare le risposte (solo sviluppo)
    fcache = os.path.join(cache, hashlib.sha1(url.encode()).hexdigest() + ".json") if cache else None
    for i in range(6):
        if fcache and os.path.exists(fcache):
            with open(fcache, encoding="utf-8") as f:
                d = json.load(f)
        else:
            attesa = 1.2 - (time.time() - _ultima[0])
            if attesa > 0:
                time.sleep(attesa)
            _ultima[0] = time.time()
            try:
                d = json.loads(get(url, tries=2, timeout=60))
            except Exception as e:
                d = {"error": str(e)}
            if fcache and isinstance(d, dict) and isinstance(d.get("data"), list):
                os.makedirs(cache, exist_ok=True)
                with open(fcache, "w", encoding="utf-8") as f:
                    json.dump(d, f)
        if isinstance(d, dict) and isinstance(d.get("data"), list):
            righe = [x for x in d["data"] if x.get("partner2Code") in (0, None) and x.get("motCode") in (0, None)
                     and x.get("customsCode") in ("C00", None)]
            if d.get("count", 0) >= 500:
                ERR.append(f"Comtrade: risposta troncata a 500 righe per {q}")
            return righe
        print(f"  comtrade riprovo ({i + 1}): {str(d)[:120]}", file=sys.stderr)
        time.sleep(5 * (i + 1))
    ERR.append(f"Comtrade: nessuna risposta valida per {q}: {str(d)[:200]}")
    return None


def num(s):
    if s is None:
        return None
    s = str(s).strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def r1(x, n=1):
    return None if x is None else round(x, n)


# ------------------------------------------------------- tabelle Comtrade

def riferimenti():
    rep = json.loads(get(CT_REF + "Reporters.json"))["results"]
    par = json.loads(get(CT_REF + "partnerAreas.json"))["results"]
    hs = json.loads(get(CT_REF + "HS.json"))["results"]
    iso2_rep = {}
    for x in rep:
        c = x.get("reporterCodeIsoAlpha2")
        if c and not x.get("entryExpiredDate"):
            iso2_rep[c] = x["reporterCode"]
    iso2_rep["TW"] = 490  # Comtrade pubblica Taiwan come "Other Asia, nes" (codice 490)
    partner = {}
    for x in par:
        partner[x["PartnerCode"]] = {"nome": x["PartnerDesc"], "iso2": x.get("PartnerCodeIsoAlpha2"),
                                     "iso3": x.get("PartnerCodeIsoAlpha3"), "gruppo": x.get("isGroup")}
    partner[490] = {"nome": "Taiwan (Comtrade: Other Asia, nes)", "iso2": "TW", "iso3": "TWN", "gruppo": False}
    hsdesc = {x["id"]: re.sub(r"^\S+ - ", "", x["text"]) for x in hs}
    return iso2_rep, partner, hsdesc


# Nomi brevi italiani dei capitoli HS (traduzione redazionale delle intestazioni ufficiali).
HS2_IT = {
    "01": "Animali vivi", "02": "Carni", "03": "Pesci e crostacei", "04": "Latte, uova, miele", "05": "Altri prodotti animali",
    "06": "Piante e fiori", "07": "Ortaggi", "08": "Frutta", "09": "Caffè, tè, spezie", "10": "Cereali",
    "11": "Farine e malto", "12": "Semi oleosi (soia ecc.)", "13": "Gomme e resine vegetali", "14": "Altri vegetali",
    "15": "Grassi e oli", "16": "Preparazioni di carne e pesce", "17": "Zuccheri", "18": "Cacao", "19": "Preparazioni di cereali",
    "20": "Preparazioni di ortaggi e frutta", "21": "Preparazioni alimentari varie", "22": "Bevande", "23": "Mangimi e residui",
    "24": "Tabacco", "25": "Sale, zolfo, pietre, cemento", "26": "Minerali metallici", "27": "Combustibili minerali (petrolio, gas, carbone)",
    "28": "Chimica inorganica, terre rare", "29": "Chimica organica", "30": "Farmaci", "31": "Fertilizzanti",
    "32": "Coloranti e vernici", "33": "Oli essenziali e cosmetici", "34": "Saponi e detergenti", "35": "Colle ed enzimi",
    "36": "Esplosivi", "37": "Prodotti fotografici", "38": "Prodotti chimici vari", "39": "Plastica", "40": "Gomma",
    "41": "Pelli grezze", "42": "Articoli in pelle", "43": "Pellicce", "44": "Legno", "45": "Sughero", "46": "Lavori di intreccio",
    "47": "Paste di legno", "48": "Carta", "49": "Libri e stampa", "50": "Seta", "51": "Lana", "52": "Cotone",
    "53": "Altre fibre vegetali", "54": "Filamenti sintetici", "55": "Fibre sintetiche", "56": "Ovatte e feltri", "57": "Tappeti",
    "58": "Tessuti speciali", "59": "Tessuti tecnici", "60": "Tessuti a maglia", "61": "Abbigliamento a maglia",
    "62": "Abbigliamento non a maglia", "63": "Altri articoli tessili", "64": "Calzature", "65": "Cappelli", "66": "Ombrelli",
    "67": "Piume e fiori artificiali", "68": "Lavori in pietra", "69": "Ceramica", "70": "Vetro",
    "71": "Oro, pietre e metalli preziosi", "72": "Ferro e acciaio", "73": "Lavori in ferro o acciaio", "74": "Rame",
    "75": "Nichel", "76": "Alluminio", "78": "Piombo", "79": "Zinco", "80": "Stagno", "81": "Altri metalli comuni (cobalto, tungsteno, gallio…)",
    "82": "Utensili", "83": "Lavori di metalli vari", "84": "Macchinari e reattori nucleari", "85": "Macchine ed elettronica",
    "86": "Ferrovie", "87": "Autoveicoli", "88": "Aeromobili e veicoli spaziali", "89": "Navi", "90": "Ottica e strumenti di precisione",
    "91": "Orologi", "92": "Strumenti musicali", "93": "Armi e munizioni", "94": "Mobili", "95": "Giocattoli e sport",
    "96": "Lavori diversi", "97": "Opere d'arte", "99": "Merci non specificate",
}

# Voci strategiche a 4 cifre seguite per ogni paese (export e import).
HS4 = {
    "2709": "Petrolio greggio", "2710": "Prodotti petroliferi raffinati", "2711": "Gas naturale e GPL (incl. GNL)",
    "2701": "Carbone", "2601": "Minerale di ferro", "2603": "Minerale di rame", "2604": "Minerale di nichel",
    "2605": "Minerale di cobalto", "2612": "Minerali di uranio e torio", "2844": "Uranio e materiali radioattivi",
    "2805": "Metalli delle terre rare", "2846": "Composti delle terre rare", "7403": "Rame raffinato",
    "7601": "Alluminio grezzo", "7108": "Oro", "7102": "Diamanti", "8542": "Circuiti integrati (chip)",
    "8541": "Semiconduttori e celle solari", "8471": "Computer", "8517": "Telefoni e apparati di rete",
    "8703": "Automobili", "8507": "Accumulatori (batterie)", "8802": "Aerei ed elicotteri",
    "9306": "Munizioni e missili", "1001": "Frumento", "1005": "Mais", "1201": "Soia",
    "3102": "Fertilizzanti azotati", "3104": "Fertilizzanti potassici", "3004": "Medicinali",
}

# Prodotti per l'analisi delle dipendenze di Italia e UE (codici HS 2022 a 6 cifre).
DIP = [
    ("280530", "Metalli delle terre rare, scandio e ittrio"),
    ("284690", "Composti delle terre rare (escluso cerio)"),
    ("850511", "Magneti permanenti metallici (NdFeB)"),
    ("811292", "Gallio, germanio, indio, niobio, vanadio grezzi (voce mista)"),
    ("250410", "Grafite naturale in polvere o scaglie"),
    ("380110", "Grafite artificiale"),
    ("282520", "Ossido e idrossido di litio"),
    ("283691", "Carbonato di litio"),
    ("810520", "Cobalto grezzo e metalline"),
    ("750210", "Nichel grezzo non legato"),
    ("740311", "Catodi di rame raffinato"),
    ("811010", "Antimonio grezzo"),
    ("810411", "Magnesio grezzo (>=99,8%)"),
    ("280461", "Silicio (>=99,99%)"),
    ("711011", "Platino grezzo"),
    ("711021", "Palladio grezzo"),
    ("284410", "Uranio naturale e composti"),
    ("284420", "Uranio arricchito in U-235"),
    ("271111", "Gas naturale liquefatto (GNL)"),
    ("271121", "Gas naturale allo stato gassoso (gasdotto)"),
    ("270900", "Petrolio greggio"),
    ("270112", "Carbone bituminoso"),
    ("760110", "Alluminio grezzo non legato"),
    ("850760", "Batterie al litio"),
    ("854143", "Moduli fotovoltaici"),
    ("294110", "Penicilline (antibiotici)"),
    ("293627", "Vitamina C"),
    ("100199", "Frumento tenero e altro"),
    ("120190", "Soia"),
]


def anni_disponibili(codici):
    """Per ogni anno: insieme dei reporter con totale export e import dichiarati."""
    out = {}
    for y in ANNI:
        righe = comtrade(reporterCode=",".join(str(c) for c in codici), period=y, partnerCode=0,
                         flowCode="X,M", cmdCode="TOTAL") or []
        tot = {}
        for x in righe:
            tot.setdefault(x["reporterCode"], {})[x["flowCode"]] = x["primaryValue"]
        out[y] = tot
    return out


def top_partner(righe, partner, n=5):
    tot = next((x["primaryValue"] for x in righe if x["partnerCode"] == 0), None)
    lst = []
    for x in righe:
        p = partner.get(x["partnerCode"], {})
        if x["partnerCode"] == 0 or (p.get("gruppo") and x["partnerCode"] != 490):
            continue
        lst.append((x["primaryValue"], x["partnerCode"]))
    lst.sort(reverse=True)
    if tot is None:
        tot = sum(v for v, _ in lst)
    return tot, [{"partner": partner.get(c, {}).get("nome", str(c)), "iso2": partner.get(c, {}).get("iso2"),
                  "valore_usd": round(v), "quota": r1(100 * v / tot) if tot else None} for v, c in lst[:n]]


def top_hs2(valori, tot, n=10):
    lst = sorted(valori.items(), key=lambda kv: -kv[1])
    return [{"hs": k, "nome": HS2_IT.get(k, k), "valore_usd": round(v), "quota": r1(100 * v / tot) if tot else None}
            for k, v in lst[:n]]


def paese_dichiarato(iso, code, anno, partner):
    d = {"metodo": "dichiarato", "anno": anno}
    righe = comtrade(reporterCode=code, period=anno, partnerCode=0, flowCode="X,M", cmdCode="AG2")
    if righe is None:
        return None
    for fl, k in (("X", "export"), ("M", "import")):
        val = {x["cmdCode"]: x["primaryValue"] for x in righe if x["flowCode"] == fl}
        tot_p = None
        pr = comtrade(reporterCode=code, period=anno, flowCode=fl, cmdCode="TOTAL")
        if pr:
            tot_p, tp = top_partner(pr, partner)
            d[k + "_partner"] = tp
        tot = tot_p or sum(val.values())
        d[k + "_totale_usd"] = round(tot)
        d[k + "_prodotti"] = top_hs2(val, tot)
    s = comtrade(reporterCode=code, period=anno, partnerCode=0, flowCode="X,M", cmdCode=",".join(HS4))
    if s:
        d["voci_strategiche"] = voci(s, d)
    return d


def voci(righe, d):
    out = []
    for c, nome in HS4.items():
        x = sum(r["primaryValue"] for r in righe if r["cmdCode"] == c and r["flowCode"] == "X")
        m = sum(r["primaryValue"] for r in righe if r["cmdCode"] == c and r["flowCode"] == "M")
        if x or m:
            out.append({"hs": c, "nome": nome, "export_usd": round(x), "import_usd": round(m),
                        "quota_export": r1(100 * x / d["export_totale_usd"]) if d.get("export_totale_usd") else None,
                        "quota_import": r1(100 * m / d["import_totale_usd"]) if d.get("import_totale_usd") else None})
    return sorted(out, key=lambda v: -(v["export_usd"] + v["import_usd"]))


def paese_specchio(iso, code, partner):
    """Commercio ricostruito dai dati dei partner: le loro importazioni dal paese = sue esportazioni."""
    anno = ANNO_SPECCHIO
    d = {"metodo": "specchio", "anno": anno,
         "nota_metodo": "Ricostruito dalle dichiarazioni dei paesi partner (import dei partner = export del paese, valori CIF; "
                        "export dei partner = import del paese, valori FOB). Mancano i partner che non dichiarano a Comtrade."}
    for fl_p, k in (("M", "export"), ("X", "import")):
        pr = comtrade(period=anno, partnerCode=code, flowCode=fl_p, cmdCode="TOTAL")
        if not pr:
            continue
        per_rep = {}
        for x in pr:
            p = partner.get(x["reporterCode"], {})
            if p.get("gruppo") and x["reporterCode"] != 490:
                continue
            per_rep[x["reporterCode"]] = per_rep.get(x["reporterCode"], 0) + x["primaryValue"]
        tot = sum(per_rep.values())
        top = sorted(per_rep.items(), key=lambda kv: -kv[1])
        d[k + "_totale_usd"] = round(tot)
        d[k + "_partner"] = [{"partner": partner.get(c, {}).get("nome", str(c)), "iso2": partner.get(c, {}).get("iso2"),
                              "valore_usd": round(v), "quota": r1(100 * v / tot) if tot else None} for c, v in top[:5]]
        # prodotti: capitoli HS dai primi 15 partner (5 per chiamata, <=500 righe)
        val, coperto = {}, 0
        primi = [c for c, _ in top[:15]]
        for i in range(0, len(primi), 5):
            g = primi[i:i + 5]
            rr = comtrade(reporterCode=",".join(str(c) for c in g), period=anno, partnerCode=code, flowCode=fl_p, cmdCode="AG2")
            if not rr:
                continue
            coperto += sum(per_rep[c] for c in g)
            for x in rr:
                val[x["cmdCode"]] = val.get(x["cmdCode"], 0) + x["primaryValue"]
        d[k + "_prodotti"] = top_hs2(val, sum(val.values()))
        d[k + "_copertura_prodotti"] = r1(100 * coperto / tot) if tot else None
    return d


def dipendenze(partner):
    out = []
    for rep_code, rep_nome, rep_iso in ((380, "Italia", "IT"), (97, "UE-27 (import extra-UE)", "EU")):
        anno = None
        for y in (2025, 2024):
            t = comtrade(reporterCode=rep_code, period=y, partnerCode=0, flowCode="M", cmdCode="TOTAL")
            if t:
                anno = y
                break
        if not anno:
            ERR.append(f"Dipendenze: nessun anno disponibile per {rep_nome}")
            continue
        for hs, nome in DIP:
            rr = comtrade(reporterCode=rep_code, period=anno, flowCode="M", cmdCode=hs)
            if not rr:
                continue
            tot, tp = top_partner(rr, partner, n=3)
            if not tot or not tp:
                continue
            out.append({"importatore": rep_nome, "iso2": rep_iso, "hs": hs, "prodotto": nome, "anno": anno,
                        "import_totale_usd": round(tot), "fornitori": tp,
                        "dipendenza_oltre_50": bool(tp[0]["quota"] and tp[0]["quota"] > 50)})
    return out


# ------------------------------------------------------------------ USGS

USGS_NOMI = {"Congo (Kinshasa)": "CD", "Korea, Republic of": "KR", "Korea, North": "KP", "Turkey": "TR", "Burma": "MM",
             "Russia": "RU", "Iran": "IR", "United States": "US", "Laos": "LA", "Vietnam": "VN", "Bolivia": "BO",
             "Côte d’Ivoire": "CI", "Syria": "SY", "Tanzania": "TZ", "Czechia": "CZ", "Venezuela": "VE",
             "United Kingdom": "GB", "New Caledonia": "NC", "Greenland": "GL", "Kyrgyzstan": "KG", "Moldova": "MD",
             "Netherlands": "NL", "United Arab Emirates": "AE", "Saudi Arabia": "SA", "Trinidad and Tobago": "TT"}

MINERALI = [  # id, nome, commodity USGS, dettaglio produzione, dettaglio riserve, critico per il progetto
    ("litio", "Litio", "Lithium", "Mine production", "Reserves"),
    ("cobalto", "Cobalto", "Cobalt", "Mine production", "Reserves"),
    ("rame", "Rame (miniera)", "Copper", "Mine production", "Reserves"),
    ("rame-raffinato", "Rame raffinato", "Copper", "Refinery production", None),
    ("nichel", "Nichel", "Nickel", "Mine production", "Reserves"),
    ("terre-rare", "Terre rare (ossidi)", "Rare Earths", "Mine production", "Reserves"),
    ("gallio", "Gallio (produzione primaria)", "Gallium", "Primary production", None),
    ("grafite", "Grafite naturale", "Graphite (Natural)", "Mine production", "Reserves"),
    ("antimonio", "Antimonio", "Antimony", "Mine production", "Reserves"),
    ("tungsteno", "Tungsteno", "Tungsten", "Mine production", "Reserves"),
    ("manganese", "Manganese (contenuto)", "Manganese", "Mine production", "Reserves"),
    ("stagno", "Stagno", "Tin", "Mine production", "Reserves"),
    ("vanadio", "Vanadio", "Vanadium", "Mine production", "Reserves"),
    ("bauxite", "Bauxite", "Bauxite", "Bauxite, mine production", "Bauxite reserves"),
    ("ferro", "Minerale di ferro (utilizzabile)", "Iron Ore", "Mine production: Usable ore", "Reserves (million metric tons): Crude ore"),
    ("platino", "Platino", "Platinum", "Mine production: Platinum", None),
    ("palladio", "Palladio", "Palladium", "Mine production: Palladium", None),
    ("silicio", "Silicio metallico", "Silicon", "Silicon metal", None),
    ("magnesio", "Magnesio metallico", "Magnesium Metal", "Smelter production", None),
    ("titanio", "Spugna di titanio", "Titanium Sponge Metal", "Titanium sponge metal production", None),
]

UNITA_IT = {"metric tons": "t", "thousand metric tons": "migliaia di t", "kilograms": "kg",
            "thousand metric dry tons": "migliaia di t secche", "million metric tons": "milioni di t"}


def usgs(nome_iso2):
    meta = json.loads(get(USGS_ITEM + "?format=json"))
    f = next(x for x in meta["files"] if x["name"].endswith("_Commodities_Data.csv"))
    raw = get(f["url"], binary=True, timeout=180)
    try:
        testo = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        testo = raw.decode("cp1252", errors="replace")
    righe = [x for x in csv.DictReader(io.StringIO(testo)) if "World" in (x.get("Section") or "")]
    ctrl = next((x for x in meta["files"] if "Export_Control" in x["name"]), None)
    controlli = []
    if ctrl:
        try:
            rb = get(ctrl["url"], binary=True)
            try:
                t = rb.decode("utf-8-sig")
            except UnicodeDecodeError:
                t = rb.decode("cp1252", errors="replace")
            for x in csv.DictReader(io.StringIO(t)):
                controlli.append({"paese": x["Country"], "iso2": iso_usgs(x["Country"], nome_iso2),
                                  "tipo": x["Control_Type"].strip(), "materie": x["Commodity_Year"], "fonte_primaria": x["Data_source"]})
        except Exception as e:
            ERR.append(f"USGS controlli export: {e}")
    elementi = []
    for mid, nome, comm, dprod, dris in MINERALI:
        rr = [x for x in righe if x["Commodity"] == comm]
        if not rr:
            ERR.append(f"USGS: {comm} assente")
            continue
        prod = [x for x in rr if x["Statistics_detail"] == dprod]
        if not prod:
            ERR.append(f"USGS: {comm} senza '{dprod}'")
            continue
        anno = max(int(x["Year"]) for x in prod)
        e = {"id": mid, "minerale": nome, "commodity_usgs": comm, "anno": anno,
             "unita": UNITA_IT.get(prod[0]["Unit"], prod[0]["Unit"]),
             "critico_usgs_2025": (prod[0].get("Is critical mineral 2025") or "").strip().lower() == "yes"}
        e.update(tabella(rr, dprod, anno, nome_iso2, "produzione"))
        if dris:
            ris = [x for x in rr if x["Statistics_detail"] == dris]
            if ris:
                anno_r = max(int(x["Year"]) for x in ris)
                e["anno_riserve"] = anno_r
                e["unita_riserve"] = UNITA_IT.get(ris[0]["Unit"], ris[0]["Unit"])
                e.update(tabella(rr, dris, anno_r, nome_iso2, "riserve"))
        e["fonte"] = "USGS Mineral Commodity Summaries 2026"
        e["link"] = USGS_PAGINA
        elementi.append(e)
    elementi.append({"id": "germanio", "minerale": "Germanio", "anno": 2025, "produttori": [], "mondo_produzione": None,
                     "fonte": "USGS Mineral Commodity Summaries 2026, scheda germanio",
                     "link": "https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-germanium.pdf",
                     "note": "USGS non pubblica una tabella mondiale: 'la maggior parte dei produttori non dichiara la produzione'. "
                             "La Cina e' il primo produttore ed esportatore; licenze all'export dal 2023 e divieto verso gli USA dal dicembre 2024."})
    return elementi, controlli


def iso_usgs(nome, nome_iso2):
    return USGS_NOMI.get(nome) or nome_iso2.get(norm(nome))


def norm(s):
    return re.sub(r"[^a-z]", "", (s or "").lower())


def tabella(rr, det, anno, nome_iso2, chiave):
    paesi, mondo, mondo_txt = [], None, None
    for x in rr:
        if int(x["Year"]) != anno:
            continue
        if x["Country"] == "World total" and x["Statistics_detail"] in (det, det + ": rounded", det + ", rounded"):
            mondo, mondo_txt = num(x["Value"].lstrip("<>")), x["Value"]
        elif x["Statistics_detail"] == det and x["Country"] not in ("World total",):
            v = num(x["Value"])
            paesi.append({"paese": x["Country"], "iso2": None if x["Country"] == "Other countries" else iso_usgs(x["Country"], nome_iso2),
                          "valore": v, "valore_testo": None if v is not None else x["Value"]})
    somma = sum(p["valore"] for p in paesi if p["valore"])
    den = max(mondo or 0, somma)  # il totale USGS e' arrotondato: se la somma lo supera, si usa la somma
    for p in paesi:
        p["quota"] = r1(100 * p["valore"] / den) if (p["valore"] is not None and den) else None
    paesi.sort(key=lambda p: -(p["valore"] or -1) if p["paese"] != "Other countries" else 1)
    return {("produttori" if chiave == "produzione" else "riserve"): paesi,
            "mondo_" + chiave: mondo, "mondo_" + chiave + "_testo": mondo_txt}


# ------------------------------------------------------------------- EIA

EIA_SERIE = {"petrolio": ("57-1", "TBPD", "Petrolio greggio e condensati, produzione", "migliaia di barili/giorno"),
             "gas": ("26-1", "BCM", "Gas naturale secco, produzione", "miliardi di m3"),
             "carbone": ("7-1", "MT", "Carbone, produzione", "migliaia di t"),
             "carbone-riserve": ("7-6", "MST", "Carbone, riserve", "milioni di short ton")}


def eia(iso3_iso2):
    raw = get(EIA_BULK, binary=True, timeout=300)
    z = zipfile.ZipFile(io.BytesIO(raw))
    voluti = {f"INTL.{c}-": k for k, (c, u, _, _) in EIA_SERIE.items()}
    dati = {k: {} for k in EIA_SERIE}
    with z.open(z.namelist()[0]) as fh:
        for line in io.TextIOWrapper(fh, encoding="utf-8"):
            if not line.startswith('{"series_id":"INTL.'):
                continue
            sid = line[14:line.find('"', 14)]
            if not sid.endswith(".A"):
                continue
            for pref, k in voluti.items():
                if sid.startswith(pref) and sid.endswith("-" + EIA_SERIE[k][1] + ".A"):
                    geo = sid[len(pref):-len(EIA_SERIE[k][1]) - 3]
                    d = json.loads(line)
                    serie = {a: v for a, v in d.get("data", []) if isinstance(v, (int, float))}
                    if serie:
                        dati[k][geo] = serie
    out = {}
    for k, (c, u, nome, unita) in EIA_SERIE.items():
        mondo = dati[k].get("WORL", {})
        anno = max((a for a in mondo), default=None)
        if not anno:
            ERR.append(f"EIA: serie mondiale {k} assente")
            continue
        paesi = []
        for geo, s in dati[k].items():
            iso2 = iso3_iso2.get(geo)
            if not iso2 or anno not in s:
                continue
            paesi.append({"iso2": iso2, "valore": r1(s[anno]), "quota": r1(100 * s[anno] / mondo[anno])})
        paesi.sort(key=lambda p: -p["valore"])
        out[k] = {"id": k, "minerale": nome, "anno": int(anno), "unita": unita, "mondo_produzione": r1(mondo[anno]),
                  "produttori": [p for p in paesi if p["valore"] > 0],
                  "fonte": "EIA International Energy Data (bulk INTL)", "link": "https://www.eia.gov/international/data/world"}
    return out


# -------------------------------------------------------------- Factbook

FB = {"US": "north-america/us", "CN": "east-n-southeast-asia/ch", "RU": "central-asia/rs", "UA": "europe/up",
      "IR": "middle-east/ir", "IL": "middle-east/is", "SA": "middle-east/sa", "AE": "middle-east/ae", "QA": "middle-east/qa",
      "IQ": "middle-east/iz", "KW": "middle-east/ku", "OM": "middle-east/mu", "YE": "middle-east/ym", "EG": "africa/eg",
      "TR": "middle-east/tu", "IN": "south-asia/in", "JP": "east-n-southeast-asia/ja", "KR": "east-n-southeast-asia/ks",
      "TW": "east-n-southeast-asia/tw", "DE": "europe/gm", "FR": "europe/fr", "IT": "europe/it", "GB": "europe/uk",
      "ES": "europe/sp", "NL": "europe/nl", "PL": "europe/pl", "NO": "europe/no", "AZ": "middle-east/aj",
      "KZ": "central-asia/kz", "DZ": "africa/ag", "LY": "africa/ly", "BR": "south-america/br", "NG": "africa/ni",
      "AU": "australia-oceania/as", "CL": "south-america/ci", "CD": "africa/cg", "ID": "east-n-southeast-asia/id",
      "ZA": "africa/sf", "WORLD": "world/xx"}


def factbook():
    out = {}
    for iso, path in FB.items():
        try:
            d = json.loads(get(FACTBOOK + path + ".json", tries=3))
        except Exception as e:
            ERR.append(f"Factbook {iso}: {e}")
            continue
        en = d.get("Energy", {})
        oil = ((en.get("Petroleum") or {}).get("crude oil estimated reserves") or {}).get("text")
        gas = ((en.get("Natural gas") or {}).get("proven reserves") or {}).get("text")
        out[iso] = {"petrolio": parse_fb(oil, {"trillion barrels": 1e3, "billion barrels": 1, "million barrels": 1e-3, "barrels": 1e-9}),
                    "gas": parse_fb(gas, {"trillion cubic meters": 1, "billion cubic meters": 1e-3, "million cubic meters": 1e-6, "cubic meters": 1e-12})}
    return out


def parse_fb(t, unita):
    if not t:
        return None
    m = re.match(r"\s*([\d.,]+)\s+([a-z ]+?)\s*\((\d{4})", t)
    if not m:
        return {"testo": t}
    v = num(m.group(1))
    for u, f in unita.items():
        if m.group(2).strip() == u:
            return {"valore": r1(v * f, 3), "anno": int(m.group(3)), "testo": t}
    return {"testo": t}


# ------------------------------------------------------------------- WNA

def uranio(nome_iso2):
    h = get(WNA)
    t = re.search(r"<table.*?</table>", h, re.S)
    if not t:
        raise ValueError("tabella non trovata")
    righe = []
    for tr in re.findall(r"<tr.*?</tr>", t.group(0), re.S):
        celle = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
        if celle:
            righe.append(celle)
    intest = righe[0]
    anno = intest[-1]
    paesi, mondo = [], None
    for r in righe[1:]:
        nome = r[0].replace("(est.)", "").strip()
        v = num(r[-1])
        if v is None:
            continue
        if nome.lower().startswith("total") or nome.lower() == "world":
            mondo = v
        elif nome.lower() == "others":
            paesi.append({"paese": "Altri", "iso2": None, "valore": v})
        else:
            paesi.append({"paese": nome, "iso2": USGS_NOMI.get(nome) or {"USA": "US"}.get(nome) or nome_iso2.get(norm(nome)), "valore": v})
    if mondo is None:
        mondo = sum(p["valore"] for p in paesi)
    for p in paesi:
        p["quota"] = r1(100 * p["valore"] / mondo)
    return {"id": "uranio", "minerale": "Uranio (produzione mineraria)", "anno": int(anno), "unita": "t U",
            "mondo_produzione": mondo, "produttori": paesi, "fonte": "World Nuclear Association", "link": WNA,
            "note": "Dati WNA; i valori 'est.' sono stime WNA. Uso informativo con citazione della fonte."}


# ------------------------------------------------------------------- main

def main():
    iso2_rep, partner, hsdesc = riferimenti()
    nome_iso2 = {norm(v["nome"]): v["iso2"] for v in partner.values() if v.get("iso2")}
    iso3_iso2 = {v["iso3"]: v["iso2"] for v in partner.values() if v.get("iso2") and v.get("iso3")}
    iso3_iso2["TWN"] = "TW"
    fonti = []

    # --- risorse
    minerali, controlli = [], []
    try:
        minerali, controlli = usgs(nome_iso2)
        fonti.append({"nome": "USGS Mineral Commodity Summaries 2026 (data release)", "link": USGS_PAGINA,
                      "licenza": "pubblico dominio (USGS)", "data_dato": "2025 (stime) e 2024"})
    except Exception as e:
        ERR.append(f"USGS: {e}")
    energia = {}
    try:
        energia = eia(iso3_iso2)
        fonti.append({"nome": "EIA International Energy Data, bulk INTL", "link": EIA_BULK,
                      "licenza": "pubblico dominio (governo USA)", "data_dato": ", ".join(f"{k} {v['anno']}" for k, v in energia.items())})
    except Exception as e:
        ERR.append(f"EIA: {e}")
    try:
        u = uranio(nome_iso2)
        energia["uranio"] = u
        fonti.append({"nome": "World Nuclear Association, World Uranium Mining Production", "link": WNA,
                      "licenza": "copyright WNA, uso informativo con citazione", "data_dato": str(u["anno"])})
    except Exception as e:
        ERR.append(f"WNA uranio: {e}")
    fb = {}
    try:
        fb = factbook()
        fonti.append({"nome": "CIA World Factbook (mirror factbook/factbook.json)", "link": "https://github.com/factbook/factbook.json",
                      "licenza": "pubblico dominio", "data_dato": "riserve stimate 2021 (fonte primaria EIA)"})
    except Exception as e:
        ERR.append(f"Factbook: {e}")

    # --- commercio
    codici = [iso2_rep[p] for p in PAESI if p in iso2_rep]
    disp = anni_disponibili(codici)
    elementi = []
    for iso in PAESI:
        code = iso2_rep.get(iso)
        print("commercio", iso, code, file=sys.stderr)
        rec = None
        if iso in SPECCHIO:
            rec = paese_specchio(iso, code, partner)
            rec["motivo_specchio"] = SPECCHIO[iso]
        else:
            anno = next((y for y in ANNI if set(disp.get(y, {}).get(code, {})) >= {"X", "M"}), None)
            if anno:
                rec = paese_dichiarato(iso, code, anno, partner)
            else:
                rec = paese_specchio(iso, code, partner)
                rec["motivo_specchio"] = "nessun anno dichiarato tra " + ", ".join(map(str, ANNI))
        rec = rec or {"metodo": "mancante"}
        el = {"iso2": iso, "nome": partner.get(code, {}).get("nome") if iso != "TW" else "Taiwan"}
        el.update(rec)
        if iso == "TW" and rec.get("metodo") == "dichiarato":
            el["nota_metodo"] = "Comtrade pubblica i dati di Taiwan come reporter 'Other Asia, nes' (codice 490)."
        if iso == "IR" and rec.get("anno", 9999) < 2024:
            el["nota_metodo"] = "Ultimo anno dichiarato dall'Iran a Comtrade; export petrolifero verso la Cina in gran parte non registrato."
        el["fonte"] = "UN Comtrade (public/v1/preview)"
        el["link"] = "https://comtradeplus.un.org/"
        el["affidabilita"] = "alta" if rec.get("metodo") == "dichiarato" else "media"
        el["risorse"] = risorse_paese(iso, minerali, energia, fb)
        elementi.append(el)
    fonti.insert(0, {"nome": "UN Comtrade, API pubblica preview (senza chiave)", "link": "https://comtradeapi.un.org/public/v1/preview/",
                     "licenza": "uso libero con citazione (termini UN Comtrade); vietata la redistribuzione massiva del database",
                     "data_dato": "anni " + ", ".join(sorted({str(e.get('anno')) for e in elementi}))})
    dip = dipendenze(partner)

    commercio = {"aggiornato": ADESSO, "fonti": fonti,
                 "nota": "Per paese: primi 10 capitoli HS esportati e importati, primi 5 partner, voci strategiche HS4 (valori USD correnti, "
                         "quota sul totale), anno = ultimo dichiarato a Comtrade con export e import. metodo='specchio' = ricostruito dai partner. "
                         "risorse = produzione e riserve con quota mondiale (USGS 2026, EIA, WNA, Factbook). dipendenze = import di Italia e UE "
                         "(extra-UE) per prodotto con i primi 3 fornitori: dipendenza_oltre_50 se un solo paese supera il 50%. "
                         "Le importazioni italiane intra-UE sono attribuite al paese di spedizione, non di origine.",
                 "elementi": elementi, "dipendenze": dip, "errori": ERR}
    mins = {"aggiornato": ADESSO, "fonti": fonti[1:],
            "nota": "Per minerale: produttori con valore e quota mondiale (%), riserve dove disponibili, anno. Valori USGS: 'W' = dato riservato, "
                    "'NA' = non disponibile, '—' = zero o trascurabile. Energia: EIA (petrolio, gas, carbone), WNA (uranio). "
                    "controlli_export = restrizioni all'export di minerali censite da USGS (dati al 21/11/2025).",
            "elementi": list(energia.values()) + minerali, "controlli_export": controlli, "errori": ERR}
    os.makedirs(OUT, exist_ok=True)
    for nome, obj in (("commercio.json", commercio), ("minerali.json", mins)):
        with open(os.path.join(OUT, nome), "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    print(f"ok: {len(elementi)} paesi, {len(dip)} dipendenze, {len(mins['elementi'])} minerali, {len(ERR)} errori", file=sys.stderr)


def risorse_paese(iso, minerali, energia, fb):
    out = []
    for e in list(energia.values()) + minerali:
        for i, p in enumerate(e.get("produttori", [])):
            if p.get("iso2") == iso and (p.get("valore") or 0) > 0:
                out.append({"risorsa": e["minerale"], "produzione": p["valore"], "unita": e["unita"], "anno": e["anno"],
                            "quota_mondiale": p.get("quota"), "rango": i + 1, "fonte": e["fonte"]})
        for p in e.get("riserve", []):
            if p.get("iso2") == iso and (p.get("valore") or 0) > 0:
                out.append({"risorsa": e["minerale"] + " - riserve", "riserve": p["valore"], "unita": e.get("unita_riserve"),
                            "anno": e.get("anno_riserve"), "quota_mondiale": p.get("quota"), "fonte": e["fonte"]})
    f, w = fb.get(iso) or {}, fb.get("WORLD") or {}
    for k, nome, u in (("petrolio", "Petrolio greggio - riserve provate", "miliardi di barili"),
                       ("gas", "Gas naturale - riserve provate", "migliaia di miliardi di m3")):
        v = f.get(k)
        if v and v.get("valore"):
            mondo = (w.get(k) or {}).get("valore")
            out.append({"risorsa": nome, "riserve": v["valore"], "unita": u, "anno": v.get("anno"),
                        "quota_mondiale": r1(100 * v["valore"] / mondo) if mondo else None,
                        "fonte": "CIA World Factbook"})
    return out


if __name__ == "__main__":
    main()
