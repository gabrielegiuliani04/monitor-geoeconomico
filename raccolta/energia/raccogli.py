#!/usr/bin/env python3
"""Agente ENERGIA: terminali GNL del mondo e punti di ingresso del gas in Italia.

Produce:
  docs/data/terminali-gnl.json  terminali GNL (import/rigassificazione ed export/liquefazione)
  docs/data/gas-italia.json     punti di ingresso del gas in Italia + flussi fisici giornalieri (12 mesi)

Fonti:
  - Global Energy Monitor, Global Gas Infrastructure Tracker (GGIT) + LNG Terminals, file della mappa
    pubblica (bucket publicgemdata su DigitalOcean, cartella Current_maps/ggit-lng/). Lo script elenca il
    bucket e prende il file piu' recente: nessun nome di file fisso. Licenza CC BY 4.0.
  - ENTSOG Transparency Platform, API pubblica senza chiave (operationaldata, indicatore Physical Flow,
    dati inviati da Snam Rete Gas e dagli altri gestori).

Uso:  python3 raccolta/energia/raccogli.py            (dalla radice del repository)
Solo libreria standard.
"""
import json, os, re, sys, time, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone

RADICE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_GNL = os.path.join(RADICE, "docs", "data", "terminali-gnl.json")
OUT_IT = os.path.join(RADICE, "docs", "data", "gas-italia.json")
UA = {"User-Agent": "Mozilla/5.0 (monitor-osint energia; uso personale non commerciale)"}

BUCKET = "https://publicgemdata.nyc3.cdn.digitaloceanspaces.com/"
PREFISSO_GEM = "Current_maps/ggit-lng/"
ENTSOG = "https://transparency.entsog.eu/api/v1/operationaldata"
KWH_PER_SMC = 10.57275  # PCS convenzionale Snam (38,1 MJ/Smc): solo per la conversione indicativa in milioni di Smc

ADESSO = datetime.now(timezone.utc)
STAMP = ADESSO.strftime("%Y-%m-%dT%H:%MZ")
OGGI = ADESSO.date()

ISO = {  # nomi paese GEM -> ISO 3166-1 alpha-2
    "Albania": "AL", "Algeria": "DZ", "Angola": "AO", "Antigua and Barbuda": "AG", "Argentina": "AR",
    "Australia": "AU", "Azerbaijan": "AZ", "Bahamas": "BS", "Bahrain": "BH", "Bangladesh": "BD",
    "Barbados": "BB", "Belgium": "BE", "Belize": "BZ", "Benin": "BJ", "Bolivia": "BO", "Brazil": "BR",
    "Brunei": "BN", "Bulgaria": "BG", "Cameroon": "CM", "Canada": "CA", "Chile": "CL", "China": "CN",
    "Colombia": "CO", "Costa Rica": "CR", "Côte d'Ivoire": "CI", "Cote d'Ivoire": "CI", "Croatia": "HR",
    "Cuba": "CU", "Cyprus": "CY", "Djibouti": "DJ", "Dominican Republic": "DO", "Ecuador": "EC",
    "Egypt": "EG", "El Salvador": "SV", "Equatorial Guinea": "GQ", "Estonia": "EE", "Finland": "FI",
    "France": "FR", "Gabon": "GA", "Germany": "DE", "Ghana": "GH", "Greece": "GR", "Guatemala": "GT",
    "Guinea": "GN", "Guyana": "GY", "Haiti": "HT", "Honduras": "HN", "Hong Kong": "HK", "India": "IN",
    "Indonesia": "ID", "Iran": "IR", "Iraq": "IQ", "Ireland": "IE", "Israel": "IL", "Italy": "IT",
    "Jamaica": "JM", "Japan": "JP", "Jordan": "JO", "Kenya": "KE", "Kuwait": "KW", "Latvia": "LV",
    "Lebanon": "LB", "Liberia": "LR", "Libya": "LY", "Lithuania": "LT", "Malaysia": "MY", "Malta": "MT",
    "Mauritania": "MR", "Mauritius": "MU", "Mexico": "MX", "Montenegro": "ME", "Morocco": "MA",
    "Mozambique": "MZ", "Myanmar": "MM", "Namibia": "NA", "Netherlands": "NL", "New Zealand": "NZ",
    "Nicaragua": "NI", "Nigeria": "NG", "Norway": "NO", "Oman": "OM", "Pakistan": "PK", "Panama": "PA",
    "Papua New Guinea": "PG", "Peru": "PE", "Philippines": "PH", "Poland": "PL", "Portugal": "PT",
    "Puerto Rico": "PR", "Qatar": "QA", "Romania": "RO", "Russia": "RU", "Saudi Arabia": "SA",
    "Senegal": "SN", "Singapore": "SG", "Somalia": "SO", "South Africa": "ZA", "South Korea": "KR",
    "Spain": "ES", "Sri Lanka": "LK", "Sudan": "SD", "Suriname": "SR", "Sweden": "SE", "Syria": "SY",
    "Taiwan": "TW", "Tanzania": "TZ", "Thailand": "TH", "Trinidad and Tobago": "TT", "Tunisia": "TN",
    "Türkiye": "TR", "Turkey": "TR", "Ukraine": "UA", "United Arab Emirates": "AE", "United Kingdom": "GB",
    "United States": "US", "Uruguay": "UY", "Venezuela": "VE", "Vietnam": "VN", "Viet Nam": "VN",
    "Yemen": "YE", "Mauritania-Senegal": "MR", "Togo": "TG", "Sierra Leone": "SL", "Congo": "CG",
    "Republic of the Congo": "CG", "Democratic Republic of the Congo": "CD", "Eritrea": "ER",
    "Ethiopia": "ET", "Georgia": "GE", "Kazakhstan": "KZ", "Turkmenistan": "TM", "Uzbekistan": "UZ",
    "Denmark": "DK", "Iceland": "IS", "Fiji": "FJ", "Guam": "GU", "Martinique": "MQ", "Guadeloupe": "GP",
    "New Caledonia": "NC", "French Polynesia": "PF", "Saint Lucia": "LC", "Grenada": "GD",
    "Saint Kitts and Nevis": "KN", "Saint Vincent and the Grenadines": "VC", "Cayman Islands": "KY",
    "Bermuda": "BM", "Aruba": "AW", "Curaçao": "CW", "Curacao": "CW", "Virgin Islands (U.S.)": "VI",
    "Cambodia": "KH", "Mongolia": "MN", "Cape Verde": "CV", "Madagascar": "MG", "Comoros": "KM",
    "Zambia": "ZM", "Zimbabwe": "ZW", "Uganda": "UG", "Malawi": "MW", "Botswana": "BW", "Belarus": "BY",
    "Hungary": "HU", "Slovenia": "SI", "Slovakia": "SK", "Czech Republic": "CZ", "Czechia": "CZ",
    "Austria": "AT", "Switzerland": "CH", "Serbia": "RS", "Bosnia and Herzegovina": "BA",
    "North Macedonia": "MK", "Kosovo": "XK", "Moldova": "MD", "Armenia": "AM", "Kuwait-Saudi Arabia": "KW",
}

STATO = {  # stato GEM -> stato in italiano (come linee.json)
    "operating": "operativo", "construction": "in-costruzione", "proposed": "proposto",
    "shelved": "sospeso", "cancelled": "cancellato", "retired": "dismesso",
    "mothballed": "fermo", "idled": "inattivo",
}
PRIORITA = ["operating", "construction", "idled", "mothballed", "proposed", "shelved", "retired", "cancelled"]


def get(url, tries=4, timeout=120):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep((20 if "429" in str(e) else 4) * (i + 1))


def ripara(s):
    """GEM a volte ha testo UTF-8 letto come Latin-1 (es. 'TÃ¼rkiye')."""
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin-1").decode("utf-8")
    except Exception:
        return s


def num(v):
    try:
        return float(v)
    except Exception:
        return None


# ---------------------------------------------------------------------------- GEM
def ultimo_file_gem():
    xml = get(BUCKET + "?prefix=" + urllib.parse.quote(PREFISSO_GEM)).decode("utf-8")
    voci = re.findall(r"<Key>(.*?)</Key><LastModified>(.*?)</LastModified>", xml)
    voci = [v for v in voci if v[0].endswith(".geojson")]
    if not voci:
        raise RuntimeError("nessun .geojson in " + PREFISSO_GEM)
    voci.sort(key=lambda v: v[1])
    return voci[-1]


def scarica_gem(errori):
    try:
        chiave, modificato = ultimo_file_gem()
        url = BUCKET + urllib.parse.quote(chiave)
        print("GEM:", url, file=sys.stderr)
        dati = json.loads(get(url, timeout=600))
        return dati, url, chiave, modificato[:10]
    except Exception as e:
        errori.append("GEM GGIT/LNG non scaricato: %s" % e)
        return None, None, None, None


def terminali(gem, url, chiave, data_file):
    """Un punto per terminale (project-id): le unita' (fasi, ampliamenti) finiscono in 'unita'."""
    gruppi = {}
    for f in gem["features"]:
        p = f["properties"]
        if p.get("tracker-acro") != "LNG" and "LNG" not in str(p.get("tracker-display")):
            continue
        g = f.get("geometry") or {}
        if g.get("type") != "Point":
            continue
        lon, lat = g["coordinates"][:2]
        if lon is None or lat is None:
            continue
        pid = p.get("project-id") or p.get("url") or p.get("name")
        gruppi.setdefault(pid, []).append((p, lat, lon))

    out = []
    for pid, righe in gruppi.items():
        p0, lat, lon = righe[0]
        tipo = "export" if "export" in str(p0.get("tracker-display")).lower() else "import"
        unita, cap = [], {}
        for p, _, _ in righe:
            st = p.get("status") or ""
            c = num(p.get("capacity"))
            unita.append({"unita": ripara(p.get("unit-name") or "") or "principale", "stato": STATO.get(st, st),
                          "mtpa": c, "inizio": p.get("start-year") or None})
            if c is not None:
                cap[st] = round(cap.get(st, 0) + c, 2)
        stati = [p.get("status") for p, _, _ in righe]
        st = next((s for s in PRIORITA if s in stati), stati[0])
        paese_nome = ripara(p0.get("country-area1") or "")
        cap_op = cap.get("operating")
        note = "Capacità per stato (Mt/anno di GNL): " + ", ".join(
            "%s %s" % (STATO.get(k, k), v) for k, v in sorted(cap.items(), key=lambda kv: PRIORITA.index(kv[0]) if kv[0] in PRIORITA else 99)) if cap else "Capacità non indicata da GEM."
        out.append({
            "lat": round(lat, 4), "lon": round(lon, 4),
            "nome": ripara(p0.get("name")),
            "paese": ISO.get(paese_nome, ""),
            "paese_nome": paese_nome,
            "categoria": "gnl-rigassificazione" if tipo == "import" else "gnl-liquefazione",
            "tipo": tipo,
            "stato": STATO.get(st, st),
            "gem_stato": st,
            "capacita_operativa_mtpa": cap_op,
            "capacita_totale_mtpa": round(sum(cap.values()), 2) if cap else None,
            "capacita_per_stato": {STATO.get(k, k): v for k, v in cap.items()},
            "unita": unita,
            "proprietario": ripara(p0.get("owner") or ""),
            "area": ripara(p0.get("location-display") or ""),
            "fonte": "Global Energy Monitor, Global Gas Infrastructure Tracker / LNG Terminals",
            "link": p0.get("url") or "https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/",
            "data_fonte": data_file,
            "affidabilita": "alta" if st == "operating" else "media",
            "gem_id": pid,
            "note": note,
        })
    out.sort(key=lambda x: (-(x["capacita_operativa_mtpa"] or 0), x["nome"]))
    return out


# ------------------------------------------------- punti di ingresso in Italia
# Coordinate: estremo lato Italia del tracciato GEM indicato (nome condotta, unita', regola).
# Se la condotta non si trova nel file GEM si usa il valore di riserva (letto dallo stesso tracciato GEM
# di ottobre 2026) e lo si segnala nelle note.
PUNTI = [
    {"id": "mazara", "nome": "Mazara del Vallo (TransMed / Transmed)", "da": "Algeria via Tunisia", "paese_origine": "DZ",
     "entsog": [("IT-TSO-0001", "ITP-00093", "entry")],
     "gem": ("Trans-Mediterranean Gas Pipeline", "", "fine"), "riserva": (37.6675, 12.5408),
     "categoria": "gas-ingresso-gasdotto"},
    {"id": "gela", "nome": "Gela (Greenstream)", "da": "Libia", "paese_origine": "LY",
     "entsog": [("IT-TSO-0001", "ITP-00074", "entry")],
     "gem": ("Greenstream Gas Pipeline", "", "fine"), "riserva": (37.0493, 14.2643),
     "categoria": "gas-ingresso-gasdotto"},
    {"id": "melendugno", "nome": "Melendugno (TAP)", "da": "Azerbaigian via Turchia, Grecia, Albania", "paese_origine": "AZ",
     "entsog": [("IT-TSO-0001", "ITP-00008", "entry")],
     "gem": ("Trans-Adriatic Gas Pipeline", "", "ovest"), "riserva": (40.3410, 18.4370),
     "categoria": "gas-ingresso-gasdotto"},
    {"id": "gries", "nome": "Passo Gries (Transitgas)", "da": "Nord Europa via Svizzera", "paese_origine": "CH",
     "entsog": [("IT-TSO-0001", "ITP-00136", "entry"), ("IT-TSO-0001", "ITP-00136", "exit")],
     "gem": ("Passo Gries-Masera Gas Pipeline", "", "nord"), "riserva": (46.4460, 8.3838),
     "categoria": "gas-ingresso-gasdotto"},
    {"id": "tarvisio", "nome": "Tarvisio (TAG)", "da": "Austria (storicamente gas russo)", "paese_origine": "AT",
     "entsog": [("IT-TSO-0001", "ITP-00040", "entry"), ("IT-TSO-0001", "ITP-00040", "exit")],
     "gem": ("Tarvisio-Zimella Gas Pipeline", "", "nord"), "riserva": (46.4768, 13.6636),
     "categoria": "gas-ingresso-gasdotto"},
    {"id": "gorizia", "nome": "Gorizia (interconnessione con la Slovenia)", "da": "Slovenia", "paese_origine": "SI",
     "entsog": [("IT-TSO-0001", "ITP-00049", "entry"), ("IT-TSO-0001", "ITP-00049", "exit")],
     "gem": ("Villesse-Gorizia Gas Pipeline", "", "est"), "riserva": (45.8930, 13.5778),
     "categoria": "gas-ingresso-gasdotto"},
    {"id": "panigaglia", "nome": "Panigaglia (GNL Italia)", "da": "GNL via nave", "paese_origine": "",
     "entsog": [("IT-TSO-0001", "LNG-00019", "entry")], "gnl": "Panigaglia LNG Terminal",
     "categoria": "gas-ingresso-gnl"},
    {"id": "olt", "nome": "OLT Livorno (FSRU Toscana)", "da": "GNL via nave", "paese_origine": "",
     "entsog": [("IT-TSO-0001", "LNG-00004", "entry")], "gnl": "Toscana FSRU",
     "categoria": "gas-ingresso-gnl"},
    {"id": "adriatic", "nome": "Adriatic LNG (Porto Levante, Rovigo; ingresso a Cavarzere)", "da": "GNL via nave", "paese_origine": "",
     "entsog": [("IT-TSO-0001", "LNG-00015", "entry")], "gnl": "Adriatic LNG Terminal",
     "categoria": "gas-ingresso-gnl"},
    {"id": "piombino", "nome": "Piombino FSRU (Italis LNG)", "da": "GNL via nave", "paese_origine": "",
     "entsog": [("IT-TSO-0001", "LNG-00069", "entry")], "gnl": "Piombino FSRU",
     "categoria": "gas-ingresso-gnl"},
    {"id": "ravenna", "nome": "Ravenna FSRU (Italis LNG, BW Singapore)", "da": "GNL via nave", "paese_origine": "",
     "entsog": [("IT-TSO-0001", "LNG-00082", "entry")], "gnl": "Ravenna FSRU",
     "categoria": "gas-ingresso-gnl"},
]
# Serie nazionali senza un punto preciso sulla mappa
NAZIONALI = [
    {"id": "produzione", "nome": "Produzione nazionale (immissione in rete)", "entsog": [("IT-TSO-0001", "PRD-00154", "entry")]},
    {"id": "stoccaggi_stogit", "nome": "Stoccaggi Stogit: erogazione (entry) e iniezione (exit)",
     "entsog": [("IT-TSO-0001", "UGS-00008", "entry"), ("IT-TSO-0001", "UGS-00008", "exit")]},
]


def coordinate_gem(gem, nome, unita, regola):
    pts = []
    for f in gem["features"]:
        p = f["properties"]
        if p.get("tracker-display") != "Gas pipeline" or ripara(p.get("name")) != nome:
            continue
        if unita and ripara(p.get("unit-name")) != unita:
            continue
        if not unita and p.get("unit-name"):
            # preferisce il segmento senza nome di unita'; se non c'e' prende tutti
            continue
        g = f.get("geometry") or {}
        parti = g.get("coordinates") if g.get("type") == "MultiLineString" else [g.get("coordinates") or []]
        for parte in parti:
            if parte:
                pts.append((parte, p))
    if not pts:
        return None
    if regola == "fine":
        c = pts[0][0][-1]
    else:
        tutti = [c for parte, _ in pts for c in parte]
        c = {"ovest": min(tutti, key=lambda c: c[0]), "est": max(tutti, key=lambda c: c[0]),
             "nord": max(tutti, key=lambda c: c[1])}[regola]
    return round(c[1], 4), round(c[0], 4)


def entsog_serie(operatore, punto, direzione, da, a, errori):
    pd = (operatore + punto + direzione).lower()
    q = urllib.parse.urlencode({"pointDirection": pd, "indicator": "Physical Flow", "periodType": "day",
                                "from": da.isoformat(), "to": a.isoformat(), "timezone": "CET", "limit": -1})
    url = ENTSOG + "?" + q
    try:
        d = json.loads(get(url, timeout=180))
    except Exception as e:
        if "404" in str(e):
            return [], url, None  # nessun dato per quel punto/direzione
        errori.append("ENTSOG %s: %s" % (pd, e))
        return None, url, None
    righe = d.get("operationaldata") or []
    per_giorno = {}
    etichetta = None
    for r in righe:
        if r.get("unit") != "kWh/d" or r.get("value") is None:
            continue
        g = r["periodFrom"][:10]
        etichetta = r.get("pointLabel")
        per_giorno[g] = per_giorno.get(g, 0) + r["value"]  # piu' righe = piu' operatori adiacenti
    serie = [[g, round(v / 1e6, 2)] for g, v in sorted(per_giorno.items())]  # GWh/giorno
    return serie, url, etichetta


def riassunto(serie):
    if not serie:
        return {}
    ult = serie[-1]
    def media(n):
        v = [x[1] for x in serie[-n:]]
        return round(sum(v) / len(v), 1) if v else None
    tot = sum(x[1] for x in serie)
    return {"ultimo_giorno": ult[0], "ultimo_gwh": ult[1],
            "ultimo_mln_smc": round(ult[1] * 1e6 / KWH_PER_SMC / 1e6, 1),
            "media_7g_gwh": media(7), "media_30g_gwh": media(30), "media_365g_gwh": media(365),
            "totale_periodo_twh": round(tot / 1000, 1),
            "totale_periodo_mld_smc": round(tot * 1e6 / KWH_PER_SMC / 1e9, 2),
            "giorni": len(serie)}


def gas_italia(gem, gnl_punti, errori):
    a = OGGI
    da = a - timedelta(days=366)
    elementi, nazionali = [], []
    gnl_per_nome = {x["nome"]: x for x in gnl_punti if x["paese"] == "IT"}
    for P in PUNTI:
        lat = lon = None
        nota_coord = ""
        if "gnl" in P:
            t = gnl_per_nome.get(P["gnl"])
            if t:
                lat, lon = t["lat"], t["lon"]
                nota_coord = "Coordinate del terminale da GEM (%s)." % t["gem_id"]
        else:
            nome, unita, regola = P["gem"]
            c = coordinate_gem(gem, nome, unita, regola) if gem else None
            if c:
                lat, lon = c
                nota_coord = "Coordinate: estremo lato Italia del tracciato GEM «%s»." % nome
            else:
                lat, lon = P["riserva"]
                nota_coord = "Coordinate di riserva (estremo del tracciato GEM «%s», file di ottobre 2026): il file GEM di oggi non l'ha fornito." % nome
        flussi, links, etichette = {}, [], []
        for op, pk, dirz in P["entsog"]:
            s, url, et = entsog_serie(op, pk, dirz, da, a, errori)
            links.append(url)
            if et:
                etichette.append(et)
            if s:
                flussi[dirz] = {"unita": "GWh/giorno", "riassunto": riassunto(s), "serie": s}
        ingresso = flussi.get("entry", {}).get("riassunto", {})
        uscita = flussi.get("exit", {}).get("riassunto", {})
        ultimo = ingresso.get("ultimo_giorno") or uscita.get("ultimo_giorno")
        stato = "dato-mancante"
        if ingresso:
            m7 = ingresso.get("media_7g_gwh") or 0
            stato = "in-flusso" if m7 > 1 else "fermo-o-minimo"
        note = [nota_coord]
        if ingresso:
            note.append("Ingresso ultimo giorno gas (%s): %s GWh (circa %s milioni di Smc); media 30 giorni %s GWh/g; ultimi 12 mesi %s TWh (circa %s miliardi di Smc)." % (
                ingresso["ultimo_giorno"], ingresso["ultimo_gwh"], ingresso["ultimo_mln_smc"], ingresso["media_30g_gwh"],
                ingresso["totale_periodo_twh"], ingresso["totale_periodo_mld_smc"]))
        if uscita and uscita.get("totale_periodo_twh"):
            note.append("Uscita (export/controflusso) ultimi 12 mesi: %s TWh." % uscita["totale_periodo_twh"])
        elementi.append({
            "id": P["id"], "lat": lat, "lon": lon, "nome": P["nome"], "paese": "IT",
            "categoria": P["categoria"], "stato": stato, "provenienza": P["da"], "paese_origine": P["paese_origine"],
            "entsog_punto": ", ".join(sorted(set(etichette))) or None,
            "fonte": "ENTSOG Transparency Platform (dati Snam Rete Gas); coordinate Global Energy Monitor",
            "link": links[0], "data_fonte": ultimo,
            "affidabilita": "alta" if ingresso else "bassa",
            "note": " ".join(note), "flussi": flussi,
        })
    for N in NAZIONALI:
        flussi = {}
        for op, pk, dirz in N["entsog"]:
            s, url, _ = entsog_serie(op, pk, dirz, da, a, errori)
            if s:
                flussi[dirz] = {"unita": "GWh/giorno", "riassunto": riassunto(s), "serie": s, "link": url}
        nazionali.append({"id": N["id"], "nome": N["nome"], "flussi": flussi})
    # totale importazioni giornaliere (somma degli ingressi dei punti)
    tot = {}
    for e in elementi:
        for g, v in e["flussi"].get("entry", {}).get("serie", []):
            tot[g] = tot.get(g, 0) + v
    serie_tot = [[g, round(v, 1)] for g, v in sorted(tot.items())]
    quote = []
    t12 = sum(e["flussi"].get("entry", {}).get("riassunto", {}).get("totale_periodo_twh", 0) or 0 for e in elementi)
    for e in elementi:
        r = e["flussi"].get("entry", {}).get("riassunto", {})
        if r and t12:
            quote.append({"id": e["id"], "nome": e["nome"], "twh_12m": r["totale_periodo_twh"],
                          "quota_ingressi_pct": round(100 * r["totale_periodo_twh"] / t12, 1)})
    quote.sort(key=lambda x: -x["twh_12m"])
    return elementi, nazionali, serie_tot, quote


def scrivi(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)
    print("scritto", path, os.path.getsize(path), "byte", file=sys.stderr)


def main():
    err_gnl, err_it = [], []
    gem, url, chiave, data_file = scarica_gem(err_gnl)
    gnl = terminali(gem, url, chiave, data_file) if gem else []
    fonte_gem = {"nome": "Global Energy Monitor, Global Gas Infrastructure Tracker e LNG Terminals (file della mappa pubblica %s)" % (chiave or "non disponibile"),
                 "link": "https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/",
                 "file": url, "licenza": "CC BY 4.0 (citare Global Energy Monitor); le schede gem.wiki sono CC BY-NC-SA",
                 "data_dato": data_file}
    if gem and gnl:
        n_op = [x for x in gnl if x["stato"] == "operativo"]
        scrivi(OUT_GNL, {
            "aggiornato": STAMP, "fonti": [fonte_gem],
            "nota": ("Un punto per terminale GNL (project-id GEM); le fasi e gli ampliamenti sono in 'unita'. "
                     "tipo import = rigassificazione (anche FSRU), export = liquefazione. Capacità in milioni di tonnellate "
                     "di GNL all'anno (Mt/a; 1 Mt GNL ≈ 1,36 miliardi di m³ di gas). 'stato' è lo stato più avanzato tra le unità. "
                     "Terminali: %d, di cui operativi %d (import %d, export %d)." % (
                         len(gnl), len(n_op), sum(1 for x in n_op if x["tipo"] == "import"), sum(1 for x in n_op if x["tipo"] == "export"))),
            "elementi": gnl, "errori": err_gnl})
    else:
        print("terminali-gnl.json non riscritto: GEM non disponibile", file=sys.stderr)

    elementi, nazionali, tot, quote = gas_italia(gem, gnl, err_it)
    if not any(e["flussi"] for e in elementi) and os.path.exists(OUT_IT):
        print("gas-italia.json non riscritto: nessun flusso ENTSOG", file=sys.stderr)
        return
    scrivi(OUT_IT, {
        "aggiornato": STAMP,
        "fonti": [{"nome": "ENTSOG Transparency Platform, API operationaldata (Physical Flow, giornaliero, dati Snam Rete Gas)",
                   "link": "https://transparency.entsog.eu/", "licenza": "dati pubblici ENTSOG, riuso con citazione della fonte",
                   "data_dato": tot[-1][0] if tot else None},
                  dict(fonte_gem, nome="Global Energy Monitor (coordinate di condotte e terminali)")],
        "nota": ("Flussi fisici giornalieri in GWh/giorno (giorno gas dalle 6 alle 6, ora CET), ultimi 12 mesi. "
                 "La conversione in milioni di Smc usa 10,57275 kWh/Smc ed è indicativa. 'entry' = gas che entra nella rete "
                 "Snam, 'exit' = gas che esce (export o controflusso). Gli ultimi giorni possono essere ancora provvisori. "
                 "'serie_nazionali' (produzione, stoccaggi) non ha un punto sulla mappa."),
        "elementi": elementi,
        "serie_nazionali": nazionali,
        "ingressi_totali": {"unita": "GWh/giorno", "nota": "Somma degli ingressi dei punti in elenco (gasdotti + GNL), senza produzione e stoccaggi.", "serie": tot},
        "quote_12_mesi": quote,
        "errori": err_it})


if __name__ == "__main__":
    main()
