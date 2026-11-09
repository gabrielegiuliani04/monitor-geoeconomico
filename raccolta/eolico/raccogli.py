#!/usr/bin/env python3
"""Filiera dell'eolico offshore nel Mare del Nord e nel Baltico.

Solo libreria standard. Le voci sono curate a mano in questa cartella:
  porti.json      porti base (punti con lat/lon)
  navi.json       navi di installazione, posacavi, CSOV + indicatori di flotta
  colli.json      colli di bottiglia (schede con indicatori) + aste 2024-2026
  obiettivi.json  dichiarazioni (Esbjerg, Ostenda, Amburgo, Marienborg) e paesi

Lo script:
  1. valida ogni voce (campi obbligatori, coordinate, paesi ISO, date, link,
     affidabilita'); le voci non valide finiscono in "errori" e, se mancano
     le coordinate, vengono scartate dalla mappa;
  2. calcola gli scarti obiettivi/realta' (somme per dichiarazione);
  3. collega i prezzi gia' raccolti in docs/data/prezzi.json (TTF, tassi USA,
     EUR/USD, Brent) e segnala quelli mancanti (rame, acciaio);
  4. se esistono, legge i file dell'agente "Nord" (porti-nord.json,
     offshore-nord.json, baltico-sicurezza.json, esposizione-nord.json) e
     annota le corrispondenze per nome di porto;
  5. prova a leggere i titoli recenti di offshoreWIND.biz e tiene quelli che
     citano porti o navi dell'elenco (fonte facoltativa: se fallisce, avviso).

Variabili d'ambiente facoltative:
  CONTROLLA_LINK=1   prova ad aprire ogni link (lento; errori solo come avviso)
  SENZA_RETE=1       non fa richieste HTTP (solo validazione e calcoli)

Opzione: --rigoroso  esce con codice 1 se ci sono errori di validazione
(per un controllo in CI); senza, esce sempre con 0.

Uscita: docs/data/eolico-filiera.json
"""
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
DATI = os.path.join(RADICE, "docs", "data")
USCITA = os.path.join(DATI, "eolico-filiera.json")
UA = "monitor-geoeconomico/1.0 (ricerca OSINT non commerciale)"

ADESSO = dt.datetime.now(dt.timezone.utc)
ERRORI = []

PAESI_OK = {"DK", "NL", "DE", "BE", "GB", "NO", "PL", "LT", "LV", "EE", "FI",
            "SE", "FR", "IE", "LU", "US"}
AFFIDABILITA = {"alta", "media", "bassa"}
# riquadro Mare del Nord + Baltico (con margine)
LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = 49.0, 66.0, -8.0, 31.0
RE_DATA = re.compile(r"^(n\.d\.|\d{4}(-\d{4})?(-\d{2}(-\d{2})?)?)$")

FILE_NORD = ["porti-nord.json", "offshore-nord.json",
             "baltico-sicurezza.json", "esposizione-nord.json"]

LICENZE = [
    ("rinnovabili.it", "(c) WindEurope: rapporto pubblico, citazione con fonte"),
    ("windeurope.org", "(c) WindEurope: citazione con fonte"),
    ("offshorewind.biz", "(c) Navingo/offshoreWIND.biz: solo citazione di fatti con link"),
    ("sec.gov", "documento depositato presso la SEC: pubblico"),
    ("gov.uk", "Open Government Licence v3.0"),
    ("wikipedia.org", "CC BY-SA 4.0"),
    ("openstreetmap.org", "ODbL"),
]


def avviso(dove, msg):
    ERRORI.append({"fonte": dove, "errore": msg})
    print(f"[avviso] {dove}: {msg}", file=sys.stderr)


def carica(nome):
    with open(os.path.join(QUI, nome), encoding="utf-8") as f:
        return json.load(f)


def licenza(link):
    for dominio, lic in LICENZE:
        if link and dominio in link:
            return lic
    return "(c) editore/azienda: solo citazione di fatti con link"


def scarica(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


# ------------------------------------------------------------ validazione
def controlla_comuni(voce, dove, campi):
    ok = True
    for c in campi:
        if voce.get(c) in (None, ""):
            avviso(dove, f"campo obbligatorio mancante: {c}")
            ok = False
    link = voce.get("link")
    if link and not str(link).startswith("https://"):
        avviso(dove, f"link non https: {link}")
    if link and re.search(r"\s", str(link)):
        avviso(dove, f"link con spazi (codificarli come %20): {link}")
    data = voce.get("data_fonte")
    if data is not None and not RE_DATA.match(str(data)):
        avviso(dove, f"data_fonte non nel formato AAAA[-MM[-GG]] o n.d.: {data}")
    aff = voce.get("affidabilita")
    if aff is not None and aff not in AFFIDABILITA:
        avviso(dove, f"affidabilita' non valida: {aff}")
    paese = voce.get("paese")
    if paese is not None and paese not in PAESI_OK:
        avviso(dove, f"codice paese inatteso: {paese}")
    return ok


def valida_porti(porti):
    buoni = []
    obbl = ["id", "nome", "paese", "lat", "lon", "categoria", "stato",
            "fonte", "link", "data_fonte", "affidabilita"]
    visti = set()
    for p in porti:
        dove = f"porti.json/{p.get('id', '?')}"
        ok = controlla_comuni(p, dove, obbl)
        if p.get("id") in visti:
            avviso(dove, "id duplicato")
        visti.add(p.get("id"))
        lat, lon = p.get("lat"), p.get("lon")
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            avviso(dove, "lat/lon non numerici: voce esclusa dalla mappa")
            continue
        if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
            avviso(dove, f"coordinate fuori dal riquadro Nord/Baltico: {lat},{lon}")
            ok = False
        for ind in p.get("indicatori") or []:
            v = ind.get("valore")
            if v is not None and not isinstance(v, (int, float)):
                avviso(dove, f"indicatore non numerico: {ind.get('nome')}")
        for fx in p.get("fonti_extra") or []:
            if not str(fx.get("link", "")).startswith("https://"):
                avviso(dove, f"fonte extra senza link https: {fx.get('nome')}")
        if ok or (lat is not None and lon is not None):
            buoni.append(p)
    return buoni


def valida_navi(navi):
    for n in navi.get("navi", []):
        controlla_comuni(n, f"navi.json/{n.get('nome', '?')}",
                         ["nome", "armatore", "tipo", "stato", "fonte", "link",
                          "data_fonte", "affidabilita"])
        g = n.get("gru_t")
        if g is not None and not isinstance(g, (int, float)):
            avviso(f"navi.json/{n.get('nome')}", "gru_t non numerico")
    for f in navi.get("flotta", []):
        controlla_comuni(f, f"navi.json/flotta/{f.get('indicatore', '?')[:40]}",
                         ["indicatore", "fonte", "link", "data_fonte", "affidabilita"])


def valida_colli(colli):
    for s in colli.get("schede", []):
        dove = f"colli.json/{s.get('id', '?')}"
        controlla_comuni(s, dove, ["id", "titolo", "tensione", "sintesi"])
        for ind in s.get("indicatori", []):
            controlla_comuni(ind, f"{dove}/{ind.get('nome', '?')[:40]}",
                             ["nome", "fonte", "link", "affidabilita"])
    for a in colli.get("aste", []):
        controlla_comuni(a, f"colli.json/aste/{a.get('paese')}/{a.get('nome', '?')[:30]}",
                         ["paese", "data", "nome", "esito", "fonte", "link",
                          "data_fonte", "affidabilita"])


def valida_obiettivi(ob):
    for d in ob.get("dichiarazioni", []):
        controlla_comuni(d, f"obiettivi.json/{d.get('id')}",
                         ["id", "nome", "data", "paesi", "fonte", "link", "affidabilita"])
        for p in d.get("paesi", []):
            if p not in PAESI_OK:
                avviso(f"obiettivi.json/{d.get('id')}", f"paese inatteso {p}")
    for p in ob.get("paesi", []):
        controlla_comuni(p, f"obiettivi.json/paesi/{p.get('paese')}",
                         ["paese", "nome", "installato_fine2025_mw", "previsione_2030_mw"])


# ------------------------------------------------------------ calcoli
def calcola_obiettivi(ob):
    per_paese = {p["paese"]: p for p in ob.get("paesi", [])}
    for p in per_paese.values():
        target = p.get("obiettivo_2030_gw")
        inst = p.get("installato_fine2025_mw")
        prev = p.get("previsione_2030_mw")
        if target:
            p["quota_obiettivo_oggi_pct"] = round(100 * inst / (target * 1000), 1)
            p["quota_obiettivo_2030_previsto_pct"] = round(100 * prev / (target * 1000), 1)
            p["scarto_2030_previsto_gw"] = round(target - prev / 1000, 2)
        p["aggiunta_2026_2030_prevista_mw"] = prev - inst if prev is not None and inst is not None else None
    for d in ob.get("dichiarazioni", []):
        # paesi_calcolo: sottoinsieme da sommare quando i totali nazionali includerebbero
        # un altro mare (es. Marienborg: Germania e Danimarca hanno soprattutto Mare del Nord)
        paesi = d.get("paesi_calcolo") or d["paesi"]
        mancanti = [c for c in paesi if c not in per_paese]
        inst = sum(per_paese[c]["installato_fine2025_mw"] for c in paesi if c in per_paese)
        prev = sum(per_paese[c]["previsione_2030_mw"] for c in paesi if c in per_paese)
        d["calcolo"] = {
            "paesi_sommati": paesi,
            "installato_fine2025_gw_paesi": round(inst / 1000, 2),
            "previsione_2030_gw_paesi": round(prev / 1000, 2),
            "paesi_senza_dato": mancanti,
            "avvertenza": d.get("nota_calcolo") or (
                "Somma dei dati nazionali WindEurope: include capacita' fuori dal mare della "
                "dichiarazione (Baltico tedesco e danese, Mare d'Irlanda, Atlantico e Manica "
                "francesi), quindi sovrastima la realta' del solo Mare del Nord."),
        }
        if d.get("obiettivo_2030_gw"):
            d["calcolo"]["quota_obiettivo_2030_oggi_pct"] = round(100 * inst / (d["obiettivo_2030_gw"] * 1000), 1)
            d["calcolo"]["quota_obiettivo_2030_previsto_pct"] = round(100 * prev / (d["obiettivo_2030_gw"] * 1000), 1)
        if d.get("obiettivo_2050_gw"):
            d["calcolo"]["quota_obiettivo_2050_oggi_pct"] = round(100 * inst / (d["obiettivo_2050_gw"] * 1000), 1)
    return ob


def aggiungi_baltico_emodnet(ob):
    """Capacita' solo-Baltico dai parchi EMODnet gia' raccolti dall'agente Nord (se presenti)."""
    percorso = os.path.join(DATI, "offshore-nord.json")
    if not os.path.exists(percorso):
        return
    try:
        with open(percorso, encoding="utf-8") as f:
            riep = json.load(f).get("riepilogo_mw") or []
    except (OSError, ValueError) as e:
        avviso("offshore-nord.json", f"non leggibile: {e}")
        return
    per_stato, per_paese = {}, {}
    for r in riep:
        if r.get("mare") != "Baltico" or not isinstance(r.get("mw"), (int, float)):
            continue
        per_stato[r["stato"]] = per_stato.get(r["stato"], 0) + r["mw"]
        if r["stato"] == "operativo":
            per_paese[r["paese"]] = per_paese.get(r["paese"], 0) + r["mw"]
    for d in ob.get("dichiarazioni", []):
        if d.get("id") == "marienborg" and per_stato:
            op = per_stato.get("operativo", 0)
            d["calcolo"]["baltico_emodnet"] = {
                "mw_per_stato": per_stato,
                "operativo_mw_per_paese": per_paese,
                "quota_obiettivo_2030_operativo_pct": round(100 * op / (d["obiettivo_2030_gw"] * 1000), 1),
                "quota_obiettivo_2030_con_cantieri_pct": round(
                    100 * (op + per_stato.get("in costruzione", 0)) / (d["obiettivo_2030_gw"] * 1000), 1),
                "fonte": "docs/data/offshore-nord.json (EMODnet Human Activities, riepilogo_mw)",
                "avvertenza": "Lo stato EMODnet puo' non coincidere con WindEurope (aggiornamenti diversi).",
            }


def collega_prezzi():
    """Legge i prezzi gia' raccolti; non scarica nulla."""
    out = {"fonte": "docs/data/prezzi.json", "serie": [], "mancanti": []}
    try:
        with open(os.path.join(DATI, "prezzi.json"), encoding="utf-8") as f:
            pr = json.load(f)
    except (OSError, ValueError) as e:
        avviso("prezzi.json", f"non leggibile: {e}")
        return out
    perche = {
        "ttf": "Prezzo del gas europeo: fissa spesso il prezzo marginale dell'elettricita' e quindi i ricavi attesi (e il costo dei CfD per lo Stato).",
        "us10y": "Tasso a lungo termine (proxy del costo del capitale globale): un parco offshore e' quasi tutto capex, ogni punto di tasso pesa sul prezzo necessario.",
        "us2y": "Tasso a breve: aspettative di politica monetaria, condizioni del debito di costruzione.",
        "eurusd": "Navi e componenti si pagano spesso in USD; ricavi in EUR/GBP/DKK.",
        "brent": "Petrolio: concorrenza per navi e cantieri con l'offshore oil & gas.",
    }
    for s in pr.get("serie", []):
        if s.get("id") in perche:
            out["serie"].append({
                "id": s["id"], "nome": s.get("nome"), "ultimo": s.get("ultimo"),
                "unita": s.get("unita"), "data": s.get("data"), "var": s.get("var"),
                "perche_conta": perche[s["id"]],
            })
    ids = {s.get("id") for s in pr.get("serie", [])}
    for chiave, nome, perche_m in [
        ("rame", "Rame (LME/COMEX)", "Cavi HVDC e inter-array: il valore dei portafogli NKT/Prysmian dipende dal metallo."),
        ("acciaio", "Acciaio (lamiere pesanti / HRC Europa)", "Monopile e torri: costo europeo per kt e confronto con la Cina."),
    ]:
        if chiave not in ids:
            out["mancanti"].append({"id": chiave, "nome": nome, "perche_conta": perche_m,
                                    "nota": "serie non presente in prezzi.json: da aggiungere allo script dei mercati"})
    out["aggiornato_prezzi"] = pr.get("aggiornato")
    return out


def collega_nord(porti):
    """Collega i porti ai file dell'agente Nord: per id (porti-nord.json) e per alias nel testo."""
    out = {"file": [], "corrispondenze": []}
    for nome in FILE_NORD:
        percorso = os.path.join(DATI, nome)
        if not os.path.exists(percorso):
            out["file"].append({"file": nome, "presente": False})
            continue
        try:
            with open(percorso, encoding="utf-8") as f:
                testo = f.read()
            dati = json.loads(testo)
        except (OSError, ValueError) as e:
            avviso(nome, f"non leggibile: {e}")
            continue
        out["file"].append({"file": nome, "presente": True, "aggiornato": dati.get("aggiornato")})
        ids_nord = {e.get("id") for e in dati.get("elementi", []) if isinstance(e, dict)}
        for p in porti:
            if nome == "porti-nord.json" and p.get("id_porti_nord"):
                if p["id_porti_nord"] in ids_nord:
                    out["corrispondenze"].append({"porto": p["id"], "file": nome, "id": p["id_porti_nord"], "tipo": "id"})
                else:
                    avviso(nome, f"id {p['id_porti_nord']} (porto {p['id']}) non trovato")
                continue
            for a in p.get("alias") or []:
                if re.search(r"\b" + re.escape(a) + r"\b", testo):
                    out["corrispondenze"].append({"porto": p["id"], "file": nome, "alias": a, "tipo": "citazione"})
                    break
    return out


def notizie_recenti(porti, navi):
    """Titoli recenti offshoreWIND.biz che citano porti o navi dell'elenco."""
    if os.environ.get("SENZA_RETE"):
        return []
    url = "https://www.offshorewind.biz/"
    try:
        h = scarica(url)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        avviso(url, f"titoli non scaricati: {e}")
        return []
    chiavi = set()
    for p in porti:
        chiavi.add(p["nome"].split(" ")[0].split("-")[0].lower())
    for n in navi.get("navi", []):
        if not n["nome"][0].isdigit():
            chiavi.add(n["nome"].lower())
    chiavi |= {"port", "vessel", "wtiv", "csov", "sov", "cable", "monopile", "tender", "auction"}
    trovati, visti = [], set()
    for m in re.finditer(r'href="(/20\d\d/\d\d/\d\d/[^"]+)"', h):
        perc = m.group(1)
        if perc in visti:
            continue
        visti.add(perc)
        slug = perc.rsplit("/", 1)[-1].replace("-", " ")
        hit = sorted(k for k in chiavi if re.search(r"\b" + re.escape(k) + r"\b", slug))
        data = "-".join(perc.split("/")[1:4])
        try:
            vecchia = (ADESSO.date() - dt.date.fromisoformat(data)).days > 60
        except ValueError:
            vecchia = True
        if hit and not vecchia:
            trovati.append({"titolo": html.unescape(slug).capitalize(), "data": data,
                            "link": "https://www.offshorewind.biz" + perc, "parole": hit})
    return trovati[:30]


def controlla_link(tutti):
    if not os.environ.get("CONTROLLA_LINK") or os.environ.get("SENZA_RETE"):
        return
    for link in sorted(tutti):
        try:
            req = urllib.request.Request(link, headers={"User-Agent": UA}, method="GET")
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status >= 400:
                    avviso(link, f"HTTP {r.status}")
        except urllib.error.HTTPError as e:
            if e.code not in (401, 403, 405, 429):  # anti-bot: non e' un link rotto
                avviso(link, f"HTTP {e.code}")
        except Exception as e:  # noqa: BLE001 - un link non deve mai fermare la raccolta
            avviso(link, f"non raggiungibile: {e}")


def raccogli_link(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("link", "link_obiettivo") and isinstance(v, str) and v.startswith("http"):
                acc.add(v)
            else:
                raccogli_link(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            raccogli_link(v, acc)


# ------------------------------------------------------------ principale
def main():
    rigoroso = "--rigoroso" in sys.argv
    porti = carica("porti.json")["porti"]
    navi = carica("navi.json")
    colli = carica("colli.json")
    ob = carica("obiettivi.json")

    porti_ok = valida_porti(porti)
    valida_navi(navi)
    valida_colli(colli)
    valida_obiettivi(ob)
    n_errori_validazione = len(ERRORI)

    ob = calcola_obiettivi(ob)
    aggiungi_baltico_emodnet(ob)
    prezzi = collega_prezzi()
    nord = collega_nord(porti_ok)
    notizie = notizie_recenti(porti_ok, navi)

    elementi = []
    for p in porti_ok:
        e = {k: p.get(k) for k in ("id", "nome", "paese", "mare", "lat", "lon",
                                   "categoria", "stato", "fonte", "link", "data_fonte",
                                   "affidabilita", "note")}
        e["lat"], e["lon"] = round(p["lat"], 4), round(p["lon"], 4)
        for k in ("id_porti_nord", "coord_nota", "ruoli", "area_nuova_ha", "area_nota", "banchine",
                  "portata_t_m2", "progetti_serviti", "indicatori", "investimenti",
                  "colli_bottiglia", "fonti_extra"):
            e[k] = p.get(k)
        elementi.append(e)

    tutti_link = set()
    for blocco in (porti_ok, navi, colli, ob):
        raccogli_link(blocco, tutti_link)
    controlla_link(tutti_link)

    # fonti principali (una per dominio+pagina), con licenza indicativa
    fonti, visti = [], set()
    def aggiungi(nome, link, data):
        if link and link not in visti:
            visti.add(link)
            fonti.append({"nome": nome, "link": link, "licenza": licenza(link), "data_dato": data})
    aggiungi(ob["fonte_installato"]["nome"], ob["fonte_installato"]["link"], ob["fonte_installato"]["data_fonte"])
    for p in porti_ok:
        aggiungi(p["fonte"], p["link"], p["data_fonte"])
    for f in navi.get("flotta", []):
        aggiungi(f["fonte"], f["link"], f["data_fonte"])
    for s in colli.get("schede", []):
        for i in s.get("indicatori", []):
            aggiungi(i["fonte"], i["link"], i.get("data"))
    for a in colli.get("aste", []):
        aggiungi(a["fonte"], a["link"], a["data_fonte"])
    for d in ob.get("dichiarazioni", []):
        aggiungi(d["fonte"], d["link"], d["data_fonte"])
    aggiungi("OpenStreetMap / Nominatim (coordinate dei porti)", "https://nominatim.openstreetmap.org/", "2026-11-09")

    uscita = {
        "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": fonti,
        "nota": ("Filiera dell'eolico offshore nel Mare del Nord e nel Baltico: porti base "
                 "(elementi, punti), navi, colli di bottiglia, aste 2024-2026, obiettivi vs realta'. "
                 "Voci curate a mano con fonte e data; numeri mancanti = null. "
                 "Le 'valutazioni' nelle schede sono interpretazioni, non fatti. "
                 "Parchi eolici e porti generali sono nei file dell'agente Nord (vedi 'collegamenti')."),
        "elementi": elementi,
        "navi": navi.get("navi", []),
        "flotta": navi.get("flotta", []),
        "jones_act": navi.get("jones_act"),
        "colli_bottiglia": colli.get("schede", []),
        "aste": sorted(colli.get("aste", []), key=lambda a: str(a.get("data"))),
        "obiettivi": {
            "fonte_installato": ob.get("fonte_installato"),
            "dichiarazioni": ob.get("dichiarazioni", []),
            "paesi": ob.get("paesi", []),
            "europa": ob.get("europa"),
        },
        "prezzi_collegati": prezzi,
        "collegamenti": {
            "file_nord": nord,
            "altri_livelli": [
                "prezzi.json: TTF, tassi USA, EUR/USD, Brent",
                "cavi.json / cavi-incidenti.json: cavi sottomarini e incidenti nel Baltico",
                "rete-elettrica.json / interconnessioni.json: linee HVDC e interconnessioni",
                "terminali-gnl.json: Mukran e altri terminali GNL condividono porti con l'eolico",
            ],
        },
        "notizie_recenti": notizie,
        "errori": ERRORI,
    }
    os.makedirs(DATI, exist_ok=True)
    with open(USCITA, "w", encoding="utf-8") as f:
        json.dump(uscita, f, ensure_ascii=False, indent=1)
    kb = os.path.getsize(USCITA) / 1024
    print(f"Scritto {USCITA} ({kb:.0f} KB): {len(elementi)} porti, {len(uscita['navi'])} navi, "
          f"{len(uscita['colli_bottiglia'])} schede, {len(uscita['aste'])} aste, "
          f"{len(notizie)} notizie, {len(ERRORI)} avvisi ({n_errori_validazione} di validazione)")
    if rigoroso and n_errori_validazione:
        sys.exit(1)


if __name__ == "__main__":
    main()
