#!/usr/bin/env python3
"""Scarica i prezzi del pannello Mercati e scrive mercati.json.

Fonti:
  - Rendimenti dei titoli di Stato USA: U.S. Department of the Treasury,
    Daily Treasury Par Yield Curve Rates (fonte ufficiale).
  - Indici, azioni, materie prime, valute: Yahoo Finance (endpoint chart, non ufficiale).

Uso:  python3 raccolta/scarica_mercati.py docs/data/prezzi.json
Solo libreria standard, nessuna dipendenza.
"""
import csv, io, json, sys, time, urllib.request
from datetime import date, datetime, timedelta, timezone

UA = {"User-Agent": "Mozilla/5.0 (monitor-osint mercati)"}

# id, nome, gruppo, simbolo Yahoo
TITOLI = [
    ("spx", "S&P 500", "Indici", "^GSPC"),
    ("ndx", "Nasdaq 100", "Indici", "^NDX"),
    ("ixic", "Nasdaq Composite", "Indici", "^IXIC"),
    ("sox", "Semiconduttori (SOX)", "Indici", "^SOX"),
    ("vix", "VIX (volatilità S&P 500)", "Indici", "^VIX"),
    ("ftsemib", "FTSE MIB", "Indici", "FTSEMIB.MI"),
    ("sx5e", "Euro Stoxx 50", "Indici", "^STOXX50E"),
    ("dax", "DAX", "Indici", "^GDAXI"),
    ("nvda", "Nvidia", "AI", "NVDA"),
    ("msft", "Microsoft", "AI", "MSFT"),
    ("googl", "Alphabet", "AI", "GOOGL"),
    ("amzn", "Amazon", "AI", "AMZN"),
    ("meta", "Meta", "AI", "META"),
    ("avgo", "Broadcom", "AI", "AVGO"),
    ("tsm", "TSMC", "AI", "TSM"),
    ("amd", "AMD", "AI", "AMD"),
    ("asml", "ASML", "AI", "ASML"),
    ("orcl", "Oracle", "AI", "ORCL"),
    ("hynix", "SK Hynix", "AI", "000660.KS"),
    ("wdc", "Western Digital", "AI", "WDC"),
    ("gold", "Oro", "Materie prime", "GC=F"),
    ("silver", "Argento", "Materie prime", "SI=F"),
    ("brent", "Petrolio Brent", "Materie prime", "BZ=F"),
    ("wti", "Petrolio WTI", "Materie prime", "CL=F"),
    ("ttf", "Gas TTF (Europa)", "Materie prime", "TTF=F"),
    ("hh", "Gas Henry Hub (USA)", "Materie prime", "NG=F"),
    ("eurusd", "EUR/USD", "Valute", "EURUSD=X"),
    ("btc", "Bitcoin", "Cripto", "BTC-USD"),
    ("eth", "Ethereum", "Cripto", "ETH-USD"),
]
UNITA = {"gold": "USD/oncia", "silver": "USD/oncia", "brent": "USD/barile", "wti": "USD/barile",
         "ttf": "EUR/MWh", "hh": "USD/MMBtu", "eurusd": "USD per 1 EUR", "btc": "USD", "eth": "USD"}
SCADENZE = ["1 Mo", "3 Mo", "6 Mo", "1 Yr", "2 Yr", "3 Yr", "5 Yr", "7 Yr", "10 Yr", "20 Yr", "30 Yr"]


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep((15 if "429" in str(e) else 3) * (i + 1))


def variazioni(serie, in_punti_base=False):
    """serie: lista di [data_iso, valore] ordinata. Variazioni a 1 giorno, 1 mese, da inizio anno, 1 anno."""
    if len(serie) < 2:
        return {}
    d_last = date.fromisoformat(serie[-1][0]); v_last = serie[-1][1]

    def prima_di(d):          # ultimo valore con data <= d
        best = None
        for s, v in serie:
            if date.fromisoformat(s) <= d:
                best = v
            else:
                break
        return best

    rif = {"1g": serie[-2][1],
           "1m": prima_di(d_last - timedelta(days=30)),
           "ytd": prima_di(date(d_last.year - 1, 12, 31)),
           "1a": prima_di(d_last - timedelta(days=365))}
    out = {}
    for k, v0 in rif.items():
        if v0 is None or v0 == 0:
            continue
        out[k] = round((v_last - v0) * 100) if in_punti_base else round((v_last / v0 - 1) * 100, 2)
    return out


def yahoo(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(sym)}?range=13mo&interval=1d"
    r = json.loads(get(url))["chart"]["result"][0]
    meta, ts = r["meta"], r.get("timestamp", [])
    closes = r["indicators"]["quote"][0]["close"]
    off = meta.get("gmtoffset", 0)
    serie, seen = [], set()
    for t, c in zip(ts, closes):
        if c is None:
            continue
        d = datetime.fromtimestamp(t + off, tz=timezone.utc).date().isoformat()
        if d in seen:
            serie[-1] = [d, c]
        else:
            seen.add(d); serie.append([d, c])
    # se la seduta di oggi non e' ancora chiusa, l'ultimo valore e' provvisorio
    fine = (meta.get("currentTradingPeriod") or {}).get("regular", {}).get("end")
    meta["_provvisorio"] = bool(fine and time.time() < fine and serie and
                                serie[-1][0] == datetime.fromtimestamp(fine + off, tz=timezone.utc).date().isoformat())
    return meta, serie


def treasury():
    """Curva dei rendimenti per l'anno in corso e il precedente."""
    righe = []
    anno = date.today().year
    for y in (anno - 1, anno):
        url = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
               f"daily-treasury-rates.csv/{y}/all?type=daily_treasury_yield_curve&field_tdr_date_value={y}")
        righe += list(csv.DictReader(io.StringIO(get(url))))
    curva = {}
    for r in righe:
        d = datetime.strptime(r["Date"], "%m/%d/%Y").date().isoformat()
        curva[d] = {k: float(r[k]) for k in SCADENZE if r.get(k) not in (None, "", "N/A")}
    return dict(sorted(curva.items()))


def arrot(v, ref):
    a = abs(ref)
    return round(v, 4 if a < 10 else 2 if a < 1000 else 1)


def main(out_path):
    serie_out, errori = [], []
    for id_, nome, gruppo, sym in TITOLI:
        try:
            meta, s = yahoo(sym)
            if not s:
                raise ValueError("serie vuota")
            ref = s[-1][1]
            s = [[d, arrot(v, ref)] for d, v in s]
            serie_out.append({
                "id": id_, "nome": nome, "gruppo": gruppo, "simbolo": sym,
                "valuta": meta.get("currency"), "unita": UNITA.get(id_, meta.get("currency")),
                "borsa": meta.get("fullExchangeName"), "ultimo": s[-1][1], "data": s[-1][0],
                "var": variazioni(s), "serie": s,
                "fonte": "Yahoo Finance", "link": f"https://finance.yahoo.com/quote/{urllib.request.quote(sym)}",
                **({"provvisorio": True} if meta["_provvisorio"] else {}),
                **({"nota": "Contratto future con scadenza più vicina"} if sym.endswith("=F") else {}),
            })
            print(f"ok  {nome:24} {s[-1][0]}  {s[-1][1]}{'  (seduta in corso)' if meta['_provvisorio'] else ''}")
        except Exception as e:
            errori.append(f"{nome} ({sym}): {e}"); print(f"ERR {nome}: {e}")
        time.sleep(1.5)

    tassi, curva_out = [], None
    try:
        curva = treasury()
        date_c = list(curva)
        for nome, k, id_ in (("Titolo di Stato USA 2 anni", "2 Yr", "us2y"),
                             ("Titolo di Stato USA 10 anni", "10 Yr", "us10y"),
                             ("Titolo di Stato USA 30 anni", "30 Yr", "us30y")):
            s = [[d, curva[d][k]] for d in date_c if k in curva[d]]
            tassi.append({"id": id_, "nome": nome, "gruppo": "Tassi USA", "unita": "% rendimento",
                          "ultimo": s[-1][1], "data": s[-1][0], "var": variazioni(s, True), "var_unita": "punti base",
                          "serie": s[-260:]})
        s = [[d, round(curva[d]["10 Yr"] - curva[d]["2 Yr"], 2)] for d in date_c if "10 Yr" in curva[d] and "2 Yr" in curva[d]]
        tassi.append({"id": "us10y2y", "nome": "Differenza 10 anni − 2 anni", "gruppo": "Tassi USA", "unita": "punti percentuali",
                      "ultimo": s[-1][1], "data": s[-1][0], "var": variazioni(s, True), "var_unita": "punti base",
                      "serie": s[-260:], "nota": "Sotto zero la curva è invertita"})
        d_last = date.fromisoformat(date_c[-1])
        d_1m = max(d for d in date_c if date.fromisoformat(d) <= d_last - timedelta(days=30))
        d_1a = max(d for d in date_c if date.fromisoformat(d) <= d_last - timedelta(days=365))
        curva_out = {"scadenze": SCADENZE, "oggi": {"data": date_c[-1], "v": curva[date_c[-1]]},
                     "un_mese_fa": {"data": d_1m, "v": curva[d_1m]}, "un_anno_fa": {"data": d_1a, "v": curva[d_1a]}}
        for t in tassi:
            t.update(fonte="U.S. Department of the Treasury",
                     link="https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve")
        print(f"ok  Tassi USA {date_c[-1]}  2a {curva[date_c[-1]]['2 Yr']}  10a {curva[date_c[-1]]['10 Yr']}  30a {curva[date_c[-1]]['30 Yr']}")
    except Exception as e:
        errori.append(f"Tesoro USA: {e}"); print(f"ERR Tesoro USA: {e}")

    ordine = ["Indici", "AI", "Tassi USA", "Materie prime", "Valute", "Cripto"]
    tutte = serie_out + tassi
    tutte.sort(key=lambda x: ordine.index(x["gruppo"]))
    out = {"aggiornato": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
           "nota": "Prezzi di chiusura giornalieri. Variazioni in %, per i tassi in punti base. Non è una quotazione in tempo reale.",
           "gruppi": ordine, "serie": tutte, "curva": curva_out, "errori": errori}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"\nScritto {out_path}: {len(tutte)} serie, {len(errori)} errori")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/data/prezzi.json")
