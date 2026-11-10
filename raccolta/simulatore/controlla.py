#!/usr/bin/env python3
"""Controlla il modello del simulatore «E se…» (docs/data/simulatore.json).

Uso:
    python3 raccolta/simulatore/controlla.py            # verifica e basta (nessuna rete)
    python3 raccolta/simulatore/controlla.py --scrivi   # ricalcola coefficienti e GNL dai valori nel file e li scrive
    python3 raccolta/simulatore/controlla.py --scarica  # riscarica da Yahoo Finance le chiusure degli episodi,
                                                        # ricalcola medie e massimi e scrive tutto
    python3 raccolta/simulatore/controlla.py --verifica-online  # riscarica e confronta, senza scrivere

Perché le serie non sono nel file: prezzi.json pubblica solo gli ultimi 3 mesi di Yahoo Finance.
Il modello conserva solo le statistiche degli episodi (base, media e massimo per finestra).

Cosa verifica:
  1. ogni riferimento 'rif' punta a una voce esistente di stretti-dettaglio.json
     e il testo 'cerca' compare davvero in quella voce;
  2. i numeri dei flussi (mb/g, bcm) compaiono nella voce citata o nel file di dati collegato;
  3. i nomi usati per PortWatch, cavi, rotte, paesi, terminali GNL e punti gas esistono nei file;
  4. gli episodi di prezzo: che le variazioni % siano coerenti con base, media e massimo scritti;
     che i coefficienti delle regole siano coerenti con le variazioni e con il volume scoperto
     di Hormuz calcolato dai flussi e dai bypass; se prezzi.json copre una finestra la ricalcola;
     con --verifica-online o --scarica ricalcola tutto dalle chiusure di Yahoo Finance;
  5. coerenza interna: intensità tra 0 e 1, bypass min <= max, ipotesi e limiti presenti;
  6. sezione «Cosa succede in Italia» di docs/simulatore.html: ogni percorso dell'elenco IT_PERCORSI
     esiste in italia-impatti.json (coefficienti, soglie, basi, pesi numerici), le soglie sono ordinate,
     le costanti IT_K compaiono nella regola scritta, i coefficienti degli scenari sono quelli stimati,
     la formula della pagina rifà gli scenari già calcolati e i numeri dei testi delle misure compaiono
     nella voce citata.

Solo libreria standard. Esce con codice 1 se trova errori.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

RADICE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATI = os.path.join(RADICE, "docs", "data")
MODELLO = os.path.join(DATI, "simulatore.json")
PAGINA = os.path.join(RADICE, "docs", "simulatore.html")
TOLL = 0.05  # tolleranza in punti percentuali o unità sui valori calcolati

errori, avvisi = [], []


def carica(nome):
    with open(os.path.join(DATI, nome), encoding="utf-8") as f:
        return json.load(f)


def num_it(x):
    """19.87 -> '19,87'; 112.0 -> '112'."""
    if x is None:
        return None
    s = ("%.2f" % x).rstrip("0").rstrip(".")
    return s.replace(".", ",")


def giorno(s):
    return date.fromisoformat(s[:10])


# ------------------------------------------------------------------ calcoli degli episodi
def statistiche(serie, inizio, base_da, base_a, finestre=(14, 30, 91)):
    """Media della base, e per ogni finestra media e massimo in % sulla base."""
    base = [v for d, v in serie if base_da <= d <= base_a and v is not None]
    if not base:
        raise ValueError("nessun dato nella base %s–%s" % (base_da, base_a))
    b = round(sum(base) / len(base), 2)
    out = {"base": b, "n_base": len(base), "finestre": {}}
    t0 = giorno(inizio)
    ultimo = max(d for d, _ in serie)
    for w in finestre:
        fine = (t0 + timedelta(days=w - 1)).isoformat()
        vals = [(d, v) for d, v in serie if inizio <= d <= fine and v is not None]
        if not vals:
            raise ValueError("nessun dato nella finestra di %d giorni" % w)
        media = round(sum(v for _, v in vals) / len(vals), 2)
        dmax, vmax = max(vals, key=lambda x: x[1])
        out["finestre"][str(w)] = {
            "fino_a": fine,
            "n": len(vals),
            "media": round(media, 2),
            "media_pct": round((media / b - 1) * 100, 1),
            "max": round(vmax, 2),
            "data_max": dmax,
            "max_pct": round((vmax / b - 1) * 100, 1),
            "completa": fine <= ultimo,
        }
    return out


def scoperto(passaggio, chiave, quota):
    """Volume scoperto (min, max) dato un flusso e i bypass."""
    blocco = passaggio.get(chiave) or {}
    flusso = blocco.get("flusso") if chiave == "petrolio" else blocco.get("flusso_bcm")
    if flusso is None:
        return None
    bmin = sum(b["min"] for b in blocco.get("bypass", []))
    bmax = sum(b["max"] for b in blocco.get("bypass", []))
    colpito = flusso * quota
    return max(0.0, colpito - bmax), max(0.0, colpito - bmin)


def scarica_yahoo(simbolo, da, a):
    """Chiusure giornaliere [[AAAA-MM-GG, valore], ...] tra due date (API chart di Yahoo Finance)."""
    p1 = int(datetime.fromisoformat(da).replace(tzinfo=timezone.utc).timestamp())
    p2 = int(datetime.fromisoformat(a).replace(tzinfo=timezone.utc).timestamp()) + 86400
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?period1=%d&period2=%d&interval=1d" % (
        urllib.parse.quote(simbolo), p1, p2)
    ultimo_errore = None
    for tentativo in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)["chart"]["result"][0]
            chiusure = d["indicators"]["quote"][0]["close"]
            return [[datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d"), round(v, 2)]
                    for t, v in zip(d["timestamp"], chiusure) if v is not None]
        except Exception as e:  # rete, formato
            ultimo_errore = e
            time.sleep(2 * (tentativo + 1))
    raise RuntimeError("Yahoo Finance %s: %s" % (simbolo, ultimo_errore))


def finestre_da_serie(serie, ep):
    return statistiche(serie, ep["inizio"], ep["base"]["da"], ep["base"]["a"])


def periodo_episodio(ep):
    fine = (giorno(ep["inizio"]) + timedelta(days=95)).isoformat()
    return ep["base"]["da"], fine


def ricalcola_pct(stat):
    """Ricalcola le % dai valori assoluti (base, media, max) scritti nel file."""
    b = stat["base"]
    out = {"base": b, "finestre": {}}
    for w, f in stat["finestre"].items():
        out["finestre"][w] = {"media_pct": round((f["media"] / b - 1) * 100, 1),
                              "max_pct": round((f["max"] / b - 1) * 100, 1)}
    return out


def calcola_derivati(modello):
    """Coefficienti delle regole e grandezze che dipendono dai passaggi (nessuna rete)."""
    ep = modello["episodi"]
    pas = {p["id"]: p for p in modello["passaggi"]}
    h = ep["hormuz_2026"]
    hp = pas[h["riferimento"]]
    smin, smax = scoperto(hp, "petrolio", 1.0)
    rif_mbg = round((smin + smax) / 2, 2)
    rif_bcm = hp["gnl"]["flusso_bcm"]
    c = h.get("calcolato") or {}
    der = {"scoperto_petrolio_mbg": {"min": round(smin, 2), "max": round(smax, 2), "centrale": rif_mbg},
           "gnl_fermo_bcm": rif_bcm}
    if "brent" in c and "ttf" in c:
        der["coeff_brent_per_mbg"] = {
            w: {"min": round(f["media_pct"] / rif_mbg, 3), "max": round(f["max_pct"] / rif_mbg, 3)}
            for w, f in c["brent"]["finestre"].items()}
        der["coeff_ttf_per_bcm"] = {
            w: {"min": round(f["media_pct"] / rif_bcm, 4), "max": round(f["max_pct"] / rif_bcm, 4)}
            for w, f in c["ttf"]["finestre"].items()}
    m = ep["mar_rosso_2023"]
    w = m["wci"]
    der_m = {"wci_salto_usd_feu": w["a"] - w["da"],
             "wci_salto_pct": round((w["a"] / w["da"] - 1) * 100, 1),
             "wci_giorni": (giorno(w["data_a"]) - giorno(w["data_da"])).days}
    return der, der_m


def confronta(atteso, scritto, percorso=""):
    """Confronta ricorsivamente due strutture; numeri con tolleranza."""
    if isinstance(atteso, dict):
        if not isinstance(scritto, dict):
            errori.append("%s: manca o non è un oggetto (eseguire --scrivi)" % percorso)
            return
        for k, v in atteso.items():
            confronta(v, scritto.get(k), "%s.%s" % (percorso, k))
    elif isinstance(atteso, (int, float)) and not isinstance(atteso, bool):
        if not isinstance(scritto, (int, float)) or abs(atteso - scritto) > TOLL:
            errori.append("%s: nel file %r, ricalcolato %r (eseguire --scrivi)" % (percorso, scritto, atteso))
    elif atteso != scritto:
        errori.append("%s: nel file %r, ricalcolato %r" % (percorso, scritto, atteso))


# ------------------------------------------------------------------ riferimenti e nomi
def controlla_rif(rif, schede, dove):
    if rif is None:
        return None
    s = schede.get(rif.get("s"))
    if s is None:
        errori.append("%s: scheda '%s' assente in stretti-dettaglio.json" % (dove, rif.get("s")))
        return None
    sez = s.get(rif.get("sez"))
    if not isinstance(sez, list) or not (0 <= rif.get("i", -1) < len(sez)):
        errori.append("%s: voce %s/%s[%s] assente" % (dove, rif.get("s"), rif.get("sez"), rif.get("i")))
        return None
    voce = sez[rif["i"]]
    testo = " ".join(str(voce.get(k, "")) for k in ("voce", "valore", "quota", "nota"))
    if rif.get("cerca") and rif["cerca"] not in testo:
        errori.append("%s: '%s' non compare in %s/%s[%d] («%s»)" % (
            dove, rif["cerca"], rif["s"], rif["sez"], rif["i"], voce.get("valore", "")[:80]))
    for k in ("fonte", "anno", "link"):
        if not voce.get(k):
            avvisi.append("%s: la voce citata non ha '%s'" % (dove, k))
    return voce


def tutti_i_rif(oggetto, percorso=""):
    """Trova tutti i dizionari 'rif'/'rif2'/'*_rif' e le liste di rif."""
    if isinstance(oggetto, dict):
        for k, v in oggetto.items():
            p = "%s.%s" % (percorso, k)
            if (k == "rif" or k.startswith("rif") or k.endswith("_rif")) and isinstance(v, dict) and "s" in v:
                yield p, v
            elif k in ("noli_episodi", "prezzi_episodi") and isinstance(v, list):
                for i, r in enumerate(v):
                    yield "%s[%d]" % (p, i), r
            else:
                yield from tutti_i_rif(v, p)
    elif isinstance(oggetto, list):
        for i, v in enumerate(oggetto):
            yield from tutti_i_rif(v, "%s[%d]" % (percorso, i))

# ------------------------------------------------------------------ Italia (docs/simulatore.html)
def it_percorso(o, percorso):
    """Stessa sintassi di itPath() nella pagina: a.b[k=v,k2=v2].c, [k~=testo] per 'contiene'."""
    for tok in percorso.split("."):
        m = re.match(r"^([^\[]+)(?:\[(.+)\])?$", tok)
        if o is None or not m:
            return None, False
        if isinstance(o, dict):
            if m.group(1) not in o:
                return None, False
            o = o[m.group(1)]
        else:
            return None, False
        if m.group(2):
            if not isinstance(o, list):
                return None, False
            cond = [re.match(r"^([^~=]+)(~?=)(.*)$", c).groups() for c in m.group(2).split(",")]
            def ok(e):
                return all((v in str(e.get(k) or "")) if op == "~=" else (str(e.get(k)) == v) for k, op, v in cond)
            o = next((e for e in o if isinstance(e, dict) and ok(e)), None)
            if o is None:
                return None, False
    return o, True


def controlla_italia(modello):
    """Controlla che i coefficienti, le soglie e i valori usati dalla pagina esistano in italia-impatti.json."""
    try:
        html = open(PAGINA, encoding="utf-8").read()
    except OSError as e:
        errori.append("Italia: %s non leggibile (%s)" % (PAGINA, e))
        return 0
    m = re.search(r"/\*IT_PERCORSI\*/(\[.*?\])/\*FINE_IT_PERCORSI\*/", html, re.S)
    if not m:
        errori.append("Italia: elenco IT_PERCORSI non trovato in simulatore.html")
        return 0
    percorsi = json.loads(m.group(1))
    it = carica("italia-impatti.json")
    # percorsi usati nel codice ma non dichiarati
    for usato in set(re.findall(r'itv\("([^"]+)"\)', html)):
        if usato not in percorsi:
            errori.append("Italia: itv(\"%s\") usato nella pagina ma assente da IT_PERCORSI" % usato)
    valori = {}
    for pc in percorsi:
        v, trovato = it_percorso(it, pc)
        if not trovato:
            errori.append("Italia: %s assente in italia-impatti.json" % pc)
            continue
        valori[pc] = v
        foglia = pc.split(".")[-1]
        numerico = (foglia in ("b", "a", "r2", "n", "gasolio", "benzina", "brent", "eurusd", "ttf", "pun", "FUEL", "CP0451", "CP0452",
                              "eur_l", "variazione_cent_con_iva", "rapporto_elettricita_dettaglio_pun", "n_settimane")
                    or foglia.endswith("_eur_l") or foglia.endswith("senza_tagli_accise"))
        if numerico and not (isinstance(v, (int, float)) or (isinstance(v, list) and v and all(isinstance(x, (int, float)) for x in v))):
            errori.append("Italia: %s non è un numero (%r)" % (pc, v))
        elif v is None and not pc.endswith("base_condizioni_normali.gas_rif_eur_smc"):
            errori.append("Italia: %s è vuoto" % pc)
    S = "regole_trasmissione.stimate."
    # coefficienti: positivi; carburanti tra 0,3 e 3 volte il Brent
    for prod in ("gasolio", "benzina"):
        for k in ("diff_4_sett", "diff_8_sett", "diff_13_sett", "livello"):
            v = valori.get("%s%s.%s.b" % (S, prod, k))
            if isinstance(v, (int, float)) and not 0.3 <= v <= 3:
                errori.append("Italia: coefficiente %s %s = %s fuori da 0,3–3" % (prod, k, v))
    # soglie: due numeri crescenti, e coerenti con i testi
    sf = it.get("soglie_fermo") or {}
    for k in ("soglie_eur_l", "soglie_aumento_pct"):
        v = sf.get(k)
        if not (isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v) and v[0] < v[1]):
            errori.append("Italia: soglie_fermo.%s deve essere [basso, alto] crescente, trovato %r" % (k, v))
    if isinstance(sf.get("soglie_eur_l"), list) and len(sf["soglie_eur_l"]) == 2:
        for liv, x in (("medio", sf["soglie_eur_l"][0]), ("alto", sf["soglie_eur_l"][1])):
            if num_it(x) not in (sf.get(liv) or "") and ("%.2f" % x).replace(".", ",") not in (sf.get(liv) or ""):
                avvisi.append("Italia: la soglia %s €/l non compare nel testo soglie_fermo.%s" % (num_it(x), liv))
    # costanti IT_K della pagina presenti nelle regole scritte
    mk = re.search(r"const IT_K = \{ iva_carburanti: ([\d.]+), litri_barile: ([\d.]+), iva_gas: ([\d.]+) \}", html)
    testo = (it.get("regole_trasmissione") or {}).get("per_il_simulatore", {}).get("testo", "")
    if not mk:
        errori.append("Italia: costanti IT_K non trovate nella pagina")
        iva = litri = iva_gas = None
    else:
        iva, litri, iva_gas = (float(x) for x in mk.groups())
        if ("%.2f" % (1 + iva)).replace(".", ",") not in testo:
            errori.append("Italia: IVA carburanti %s non compare in per_il_simulatore.testo" % iva)
        if ("%.3f" % litri).replace(".", ",") not in testo:
            errori.append("Italia: litri per barile %s non compaiono in per_il_simulatore.testo" % litri)
        reg_gas = next((r for r in it["regole_trasmissione"].get("regole", []) if r.get("id") == "ttf_gas_vulnerabili"), {})
        if "IVA %d%%" % round(iva_gas * 100) not in reg_gas.get("fonte", ""):
            errori.append("Italia: IVA gas %s non compare nella regola ttf_gas_vulnerabili" % iva_gas)
    kwh = modello["costanti"]["kwh_per_smc"]["valore"]
    # gli scenari già calcolati usano gli stessi coefficienti stimati che legge la pagina
    st = it["regole_trasmissione"]["stimate"]
    for sc in it.get("scenari", []):
        lungo = sc["durata_giorni"] > 45
        attesi = {}
        for prod in ("gasolio", "benzina"):
            c = st[prod]
            attesi[prod] = ([c["diff_8_sett"]["b"], max(c["diff_13_sett"]["b"], c["livello"]["b"])] if lungo
                            else [c["diff_4_sett"]["b"], c["diff_8_sett"]["b"]])
            if sc["coefficienti_usati"][prod] != attesi[prod]:
                errori.append("Italia: scenario %s usa coefficienti %s %s, la pagina %s" % (sc["id"], prod, sc["coefficienti_usati"][prod], attesi[prod]))
        if sc["coefficienti_usati"].get("pun_per_ttf") != st["pun_ttf"]["b"]:
            errori.append("Italia: scenario %s, pun_per_ttf diverso da stimate.pun_ttf.b" % sc["id"])
        if iva is None:
            continue
        # la formula della pagina (calcolaItalia) applicata agli ingressi dello scenario
        pesi = it["regole_trasmissione"]["per_il_simulatore"]["pesi_hicp_millesimi_2026"]
        rapp = sc["coefficienti_usati"]["rapporto_elettricita_dettaglio_pun"]
        for chiave in ("da_oggi", "da_condizioni_normali"):
            ref = sc.get(chiave)
            if not ref:
                continue
            b = it["regole_trasmissione"]["per_il_simulatore"]["base_oggi" if chiave == "da_oggi" else "base_condizioni_normali"]
            br, tt = sc["ingresso"]["brent_pct"], sc["ingresso"]["ttf_pct"]
            dbl = [b["brent"] * x / 100 / b["eurusd"] / litri for x in br]
            dg = [dbl[i] * attesi["gasolio"][i] * (1 + iva) for i in (0, 1)]
            db = [dbl[i] * attesi["benzina"][i] * (1 + iva) for i in (0, 1)]
            dt = [b["ttf"] * x / 100 for x in tt]
            dp = [x * st["pun_ttf"]["b"] for x in dt]
            dsmc = [x * kwh / 1000 * (1 + iva_gas) for x in dt]
            gp = [x / b["gas_rif_eur_smc"] * 100 for x in dsmc] if b.get("gas_rif_eur_smc") else [0, 0]
            pf = [(dg[i] / b["gasolio"] + db[i] / b["benzina"]) / 2 * 100 for i in (0, 1)]
            pe = [dp[i] / b["pun"] * 100 * rapp for i in (0, 1)]
            pp = [(pesi["FUEL"] * pf[i] + pesi["CP0452"] * gp[i] + pesi["CP0451"] * pe[i]) / 1000 for i in (0, 1)]
            confronti = (("gasolio_eur_l", [b["gasolio"] + x for x in dg], 0.006), ("benzina_eur_l", [b["benzina"] + x for x in db], 0.006),
                         ("pun_eur_mwh", [b["pun"] + x for x in dp], 0.6), ("gas_vulnerabili_aumento_cent_smc", [x * 100 for x in dsmc], 0.1),
                         ("inflazione_effetto_diretto_punti", pp, 0.01))
            for campo, calc, tol in confronti:
                for i in (0, 1):
                    if ref.get(campo) and abs(calc[i] - ref[campo][i]) > tol:
                        errori.append("Italia: scenario %s %s %s[%d]: pagina %.3f, file %s" % (sc["id"], chiave, campo, i, calc[i], ref[campo][i]))
    # numeri nei testi inglesi delle misure: devono comparire nella voce citata (anni esclusi)
    misure = {e["id"]: e for e in it.get("misure_governo", [])}
    testi_misure = re.findall(r'm\("([\w-]+)", `(.*?)`\);', html)
    if not testi_misure:
        errori.append("Italia: nessun testo di misura trovato nella pagina (forma m(\"id\", `testo`))")
    for mid, testo_en in testi_misure:
        voce = misure.get(mid)
        if not voce:
            errori.append("Italia: misura '%s' assente in misure_governo" % mid)
            continue
        txt = voce.get("testo", "").replace("−", "-")
        for num in re.findall(r"\d[\d,.]*", re.sub(r"<[^>]+>", "", testo_en)):
            num = num.rstrip(".,")
            if re.fullmatch(r"(19|20)\d\d", num):
                continue
            it_num = num.replace(",", "§").replace(".", ",").replace("§", ".")
            mila = re.sub(r"\.000$", " mila", it_num)
            if not any(x in txt for x in (num, it_num, mila)):
                errori.append("Italia: misura %s, il numero %s del testo inglese non compare nella voce («%s»)" % (mid, num, txt[:70]))
    return len(percorsi)


def main():
    scrivi = "--scrivi" in sys.argv
    modello = json.load(open(MODELLO, encoding="utf-8"))
    stretti = carica("stretti-dettaglio.json")
    schede = {e["id"]: e for e in stretti["elementi"]}
    prezzi = carica("prezzi.json")
    portwatch = carica("portwatch.json")
    paesi = carica("paesi.json")
    cavi = carica("cavi.json")
    rotte = carica("rotte.json")
    gasit = carica("gas-italia.json")
    gnl = carica("terminali-gnl.json")
    scorte = carica("scorte.json")
    noli = carica("noli.json")

    # 1. riferimenti
    n_rif = 0
    for p, r in tutti_i_rif(modello):
        controlla_rif(r, schede, p)
        n_rif += 1

    # 2–3. passaggi
    pw = {e["nome"]: e for e in portwatch["elementi"]}
    nomi_cavi = set(cavi["riepilogo"]["cavi_per_passaggio"])
    nomi_rotte = {s for r in rotte["rotte"] for s in r["s"]}
    ind_paesi = {i for p in paesi["elementi"] for i in p["indicatori"]}
    gas_ids = {e["id"] for e in gasit["elementi"]}
    approdi = {a["nome"] for a in cavi["approdi"]}
    gnl_nomi = {e["nome"] for e in gnl["elementi"]}
    for p in modello["passaggi"]:
        d = "passaggio %s" % p["id"]
        if p["stretto"] not in schede:
            errori.append("%s: scheda '%s' assente" % (d, p["stretto"]))
        if p.get("portwatch") and p["portwatch"] not in pw:
            errori.append("%s: '%s' assente in portwatch.json" % (d, p["portwatch"]))
        if p.get("cavi") and p["cavi"] not in nomi_cavi:
            errori.append("%s: '%s' assente in cavi.json (riepilogo)" % (d, p["cavi"]))
        if p.get("rotte") and p["rotte"] not in nomi_rotte:
            avvisi.append("%s: nessuna rotta di rotte.json passa da '%s'" % (d, p["rotte"]))
        for f in p.get("flussi", []):
            if f.get("valore") is None:
                continue
            if f.get("gas_italia"):
                g = next(e for e in gasit["elementi"] if e["id"] == f["gas_italia"])
                v = g["flussi"]["entry"]["riassunto"]["totale_periodo_mld_smc"]
                if abs(v - f["valore"]) > 0.3:
                    errori.append("%s: flusso %s = %s, gas-italia.json dice %s bcm" % (d, f["etichetta"], f["valore"], v))
                elif abs(v - f["valore"]) > TOLL:
                    avvisi.append("%s: flusso %s = %s, gas-italia.json ora dice %s bcm (aggiornare)" % (d, f["etichetta"], f["valore"], v))
                continue
            voce = controlla_rif(f.get("rif"), schede, d + " flusso")
            if voce and num_it(f["valore"]) not in voce.get("valore", "") + voce.get("voce", ""):
                errori.append("%s: il numero %s non compare nella voce citata («%s»)" % (d, num_it(f["valore"]), voce["valore"][:80]))
        for chiave in ("petrolio", "gnl"):
            blocco = p.get(chiave)
            if not blocco:
                continue
            if blocco.get("meccanismo") not in ("perdita", "deviazione"):
                errori.append("%s: %s.meccanismo deve essere 'perdita' o 'deviazione'" % (d, chiave))
            fl = blocco.get("flusso") if chiave == "petrolio" else blocco.get("flusso_bcm")
            nums = [f["valore"] for f in p["flussi"] if f.get("valore") is not None]
            if fl is not None and fl not in nums:
                errori.append("%s: il flusso %s %s non è tra i flussi elencati" % (d, chiave, fl))
            for b in blocco.get("bypass", []):
                if b["min"] > b["max"]:
                    errori.append("%s: bypass '%s' con min > max" % (d, b["nome"]))
                voce = controlla_rif(b.get("rif"), schede, d + " bypass")
                if voce and b["max"] > 0 and b["max"] != fl:
                    txt = voce.get("valore", "")
                    if num_it(b["max"]) not in txt:
                        avvisi.append("%s: bypass '%s' max %s non compare alla lettera nella voce («%s»)" % (d, b["nome"], num_it(b["max"]), txt[:70]))
        r = p.get("rotta")
        if r and r.get("giorni") and r["giorni"][0] > r["giorni"][1]:
            errori.append("%s: rotta con giorni min > max" % d)
        for e in p.get("esposizione", []):
            if e["ind"] not in ind_paesi:
                errori.append("%s: indicatore '%s' assente in paesi.json" % (d, e["ind"]))
        if p.get("esposizione_gas_italia") and p["esposizione_gas_italia"] not in gas_ids:
            errori.append("%s: punto gas '%s' assente" % (d, p["esposizione_gas_italia"]))
        for po in p.get("porti", []):
            if po.get("portwatch") and po["portwatch"] not in pw:
                errori.append("%s: porto '%s' assente in portwatch.json" % (d, po["portwatch"]))
            if po.get("gnl") and po["gnl"] not in gnl_nomi:
                errori.append("%s: terminale '%s' assente in terminali-gnl.json" % (d, po["gnl"]))
            if po.get("gas_italia") and po["gas_italia"] not in gas_ids:
                errori.append("%s: punto '%s' assente in gas-italia.json" % (d, po["gas_italia"]))
            if po.get("cavi_approdo") and po["cavi_approdo"] not in approdi and po["cavi_approdo"] not in cavi["riepilogo"]["italia"]["per_approdo"]:
                errori.append("%s: approdo '%s' assente in cavi.json" % (d, po["cavi_approdo"]))

    # terminali GNL italiani (bypass del TransMed)
    cap = uso = 0.0
    k_bcm = modello["costanti"]["gnl_mt_in_bcm"]["valore"]
    kwh = modello["costanti"]["kwh_per_smc"]["valore"]
    for t in modello["terminali_gnl_italia"]:
        g = next((e for e in gnl["elementi"] if e["nome"] == t["gem"] and e["paese"] == "IT"), None)
        q = next((e for e in gasit["quote_12_mesi"] if e["id"] == t["gas_italia"]), None)
        if g is None or q is None:
            errori.append("terminale GNL %s / %s non trovato" % (t["gem"], t["gas_italia"]))
            continue
        cap += (g["capacita_operativa_mtpa"] or 0) * k_bcm
        uso += q["twh_12m"] / kwh  # TWh / (kWh/Smc) = miliardi di Smc
    libera = max(0.0, cap - uso)
    gnl_it = {"capacita_bcm": round(cap, 2), "uso_12m_bcm": round(uso, 2), "libera_bcm": round(libera, 2)}

    # 4. episodi
    scarica = "--scarica" in sys.argv
    online = scarica or "--verifica-online" in sys.argv
    if scarica:
        scrivi = True
    serie_prezzi = {s["id"]: s["serie"] for s in prezzi["serie"]}
    for nome, ep in modello["episodi"].items():
        c = ep.get("calcolato") or {}
        if online:
            da, a = periodo_episodio(ep)
            for k, sym in ep["simboli"].items():
                stat = finestre_da_serie(scarica_yahoo(sym, da, a), ep)
                if scarica:
                    c[k] = stat
                else:
                    confronta(stat, c.get(k), "episodi.%s.calcolato.%s (Yahoo)" % (nome, k))
            ep["calcolato"] = c
        for k in ep["simboli"]:
            if k not in c:
                errori.append("episodi.%s: mancano le statistiche di %s (eseguire --scarica)" % (nome, k))
                continue
            confronta(ricalcola_pct(c[k]), c[k], "episodi.%s.calcolato.%s" % (nome, k))
            for w, f in c[k]["finestre"].items():
                if not f.get("completa", True):
                    avvisi.append("episodio %s, %s: la finestra di %s giorni non è completa nei dati" % (nome, k, w))
            # se prezzi.json copre l'episodio (serie recente), ricalcola anche da lì
            sp = serie_prezzi.get(k, [])
            if sp and sp[0][0] <= ep["base"]["da"]:
                confronta(finestre_da_serie(sp, ep), c[k], "episodi.%s.calcolato.%s (prezzi.json)" % (nome, k))
    der_h, der_m = calcola_derivati(modello)
    if scrivi:
        modello["episodi"]["hormuz_2026"]["calcolato"].update(der_h)
        modello["episodi"]["mar_rosso_2023"]["calcolato"].update(der_m)
        modello["calcolato"] = {"gnl_italia": gnl_it}
    else:
        confronta(der_h, modello["episodi"]["hormuz_2026"]["calcolato"], "episodi.hormuz_2026.calcolato")
        confronta(der_m, modello["episodi"]["mar_rosso_2023"]["calcolato"], "episodi.mar_rosso_2023.calcolato")
        confronta(gnl_it, (modello.get("calcolato") or {}).get("gnl_italia"), "calcolato.gnl_italia")

    # 5. coerenza interna
    for o in modello["opzioni"]["intensita"]:
        if not 0 < o["quota"] <= 1:
            errori.append("intensità %s fuori da (0, 1]" % o["id"])
    if len(modello.get("ipotesi", [])) < 3 or len(modello.get("limiti", [])) < 3:
        errori.append("ipotesi o limiti mancanti")
    for paese in modello["focus_paesi"]:
        if paese not in {p["paese"] for p in paesi["elementi"]}:
            avvisi.append("paese in evidenza %s assente in paesi.json: il simulatore lo descrive solo a parole" % paese)
    if not any(e["id"] == "wci" for e in noli["elementi"]):
        errori.append("noli.json senza WCI")
    ids_scorte = {e["id"] for e in scorte["elementi"]}
    for p in ("it", "de", "nl"):
        for pref in ("gas_stoccaggio_pct_", "petrolio_emergenza_giorni_"):
            if pref + p not in ids_scorte:
                avvisi.append("scorte.json senza %s%s" % (pref, p))
    agg = prezzi.get("aggiornato", "")[:10]
    if agg and (date.today() - giorno(agg)).days > 7:
        avvisi.append("prezzi.json aggiornato il %s: più di 7 giorni fa" % agg)

    # 6. Italia
    n_it = controlla_italia(modello)

    if scrivi:
        with open(MODELLO, "w", encoding="utf-8") as f:
            txt = json.dumps(modello, ensure_ascii=False, indent=1)
            # coppie [data, valore] su una riga
            txt = re.sub(r'\[\n\s+"(\d{4}-\d\d-\d\d)",\n\s+(-?[\d.]+)\n\s+\]', r'["\1", \2]', txt)
            f.write(txt + "\n")
        print("Scritte le parti calcolate in", os.path.relpath(MODELLO, RADICE))

    h = modello["episodi"]["hormuz_2026"]["calcolato"]
    m = modello["episodi"]["mar_rosso_2023"]["calcolato"]
    if "brent" not in h or "brent" not in m:
        for e in errori:
            print("ERRORE:", e)
        return 1
    print("Riferimenti controllati: %d; passaggi: %d" % (n_rif, len(modello["passaggi"])))
    print("Hormuz 2026: Brent base %.2f, 30 giorni media %+.1f%% picco %+.1f%%; TTF base %.2f, 30 giorni media %+.1f%% picco %+.1f%%; scoperto %.2f–%.2f mb/g" % (
        h["brent"]["base"], h["brent"]["finestre"]["30"]["media_pct"], h["brent"]["finestre"]["30"]["max_pct"],
        h["ttf"]["base"], h["ttf"]["finestre"]["30"]["media_pct"], h["ttf"]["finestre"]["30"]["max_pct"],
        der_h["scoperto_petrolio_mbg"]["min"], der_h["scoperto_petrolio_mbg"]["max"]))
    print("Mar Rosso 2023–24: Brent 30 giorni media %+.1f%% picco %+.1f%%; TTF 30 giorni media %+.1f%%; WCI +%d $/FEU in %d giorni" % (
        m["brent"]["finestre"]["30"]["media_pct"], m["brent"]["finestre"]["30"]["max_pct"],
        m["ttf"]["finestre"]["30"]["media_pct"], der_m["wci_salto_usd_feu"], der_m["wci_giorni"]))
    print("GNL Italia: capacità %.1f bcm/anno, uso 12 mesi %.1f, libera %.1f" % (cap, uso, libera))
    print("Italia (simulatore.html): %d valori di italia-impatti.json controllati" % n_it)
    for a in avvisi:
        print("AVVISO:", a)
    for e in errori:
        print("ERRORE:", e)
    print("Esito: %d errori, %d avvisi" % (len(errori), len(avvisi)))
    return 1 if errori else 0


if __name__ == "__main__":
    sys.exit(main())
