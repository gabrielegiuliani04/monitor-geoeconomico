#!/usr/bin/env python3
"""Daily health check of the whole monitor: data, links, consistency, secrets, licences, validators.

Standard library only. It must never crash and should finish in about 5 minutes: every check runs
inside its own try/except, the link sample has a time budget and each validator a timeout.
It never modifies other agents' files: it only reads docs/data, report/ and raccolta/.

Checks (area -> what):
  a) freshness    'aggiornato'/'updated' and the newest data date of every docs/data/*.json against
                  the expected cadence (table CADENZA below); daily series inside a file that lag behind
  b) schema       every file parses; points have numeric lat/lon in range; source fields present
                  (fonte/link/data_fonte/affidabilita, or the English equivalents); element counts vs
                  yesterday (raccolta/qualita/storico.json, fallback: git history) -> drops > 20%
  c) errors       the 'errori'/'errors' arrays of every file (and 'avvisi'/'warnings' as notes)
  d) links        rotating sample of ~150 source links a day (HEAD, then GET), rolling record in
                  raccolta/qualita/link_storico.json; a link is 'broken' after 2 failed checks in a row
  e) consistency  the same fact in different files: chokepoint transits (portwatch / rischio /
                  stretti-dettaglio / transit-times), chokepoint scores (rischio / port-risk), port calls
                  (porti-nord / esposizione-nord / port-risk), Brent and TTF (prezzi vs every other file),
                  gas storage (scorte / esposizione-nord), key report figures (fatti_chiave.json)
  f) secrets      anything in docs/ that looks like an API key or token -> overall red and exit code 2
  g) licences     every docs/data file has a row in DATA_LICENSES.md
  h) validators   the repository's own validators, with exit status (none of them writes files here)
  +  smoke        result of the Playwright smoke test (raccolta/qualita/smoke.json) if present

Output: docs/data/health.json and report/qualita/<date>.md (English). In the Markdown report,
anything written below the line '<!-- manual notes: kept on rewrite -->' is preserved.

Usage:
  python3 raccolta/qualita/controlla_tutto.py               # full run
  python3 raccolta/qualita/controlla_tutto.py --senza-rete  # no link check (offline)
  python3 raccolta/qualita/controlla_tutto.py --oggi 2026-11-10 --link 150
Environment: SENZA_RETE=1 same as --senza-rete. Exit code: 0, or 2 if a secret was found.
"""
import concurrent.futures as cf
import datetime as dt
import glob
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
DATI = os.path.join(RADICE, "docs", "data")
DOCS = os.path.join(RADICE, "docs")
STORICO = os.path.join(QUI, "storico.json")
LINK_STORICO = os.path.join(QUI, "link_storico.json")
FATTI = os.path.join(QUI, "fatti_chiave.json")
SMOKE = os.path.join(QUI, "smoke.json")
USCITA = os.path.join(DATI, "health.json")
UA = "monitor-geoeconomico-linkcheck/1.0 (personal non-commercial OSINT project; source link check)"
INIZIO = time.time()
ADESSO = dt.datetime.now(dt.timezone.utc)


def argomento(nome, predefinito=None):
    if nome in sys.argv:
        i = sys.argv.index(nome)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return predefinito


OGGI = dt.date.fromisoformat(argomento("--oggi") or os.environ.get("OGGI") or ADESSO.date().isoformat())
SENZA_RETE = "--senza-rete" in sys.argv or os.environ.get("SENZA_RETE") == "1"
N_LINK = int(argomento("--link", "150"))
BUDGET_LINK_S = 200          # seconds for the whole link sample
TIMEOUT_LINK = 10
TIMEOUT_VALIDATORE = 60

# ----------------------------------------------------------------------------- cadence table
# file -> (cadence label, max age of 'aggiornato' in days, max age of the newest data date in days or None,
#          keys that hold the data date (None = any YYYY-MM-DD value in the file, future dates ignored))
# Age limits include one day of slack for a missed run. 'static' files are not dated on purpose.
D, W, M, S = "daily", "weekly", "monthly (curated)", "static"
CADENZA = {
    "prezzi.json":            ("daily, weekdays (Treasury + Yahoo)", 4, 4, ["data"]),
    "portwatch.json":         ("daily run, weekly source with ~7-day lag (IMF PortWatch)", 2, 14, ["ultima_data"]),
    "porti-nord.json":        ("daily run, PortWatch ports with ~7-11-day lag", 2, 16, ["ultima_data"]),
    "noli.json":              ("daily run, weekly freight indices", 2, 10, ["data", "data_dato", "data_fonte"]),
    "gpr.json":               ("daily run, GPR index (daily/monthly)", 2, 40, None),
    "sanzioni-navi.json":     ("daily run (OFAC, UK, EU lists)", 2, None, None),
    "scorte.json":            ("daily (AGSI+ D-2), monthly Eurostat/USDA", 2, 5, ["data_fonte"]),
    "navi.json":              ("daily AIS snapshot", 2, 3, None),
    "calendario.json":        ("daily", 2, None, None),
    "terminali-gnl.json":     ("daily run (GEM tracker)", 2, None, None),
    "gas-italia.json":        ("daily (ENTSOG flows)", 2, 6, None),
    "ucraina-storico.json":   ("daily", 2, 10, None),
    "attacchi-russi.json":    ("daily", 2, 10, None),
    "attacchi-analisti.json": ("daily (Telegram channels)", 2, 5, None),
    "notizie.json":           ("daily (RSS, last 7 days)", 2, 2, None),
    "notizie-testate.json":   ("daily (RSS of the outlets)", 2, 2, None),
    "baltico-sicurezza.json": ("daily", 2, 7, None),
    "esposizione-nord.json":  ("daily", 2, None, None),
    "offshore-nord.json":     ("daily run, slow-changing source", 2, None, None),
    "bunker-emissioni.json":  ("daily, weekly bunker prices", 2, 10, None),
    "italia-impatti.json":    ("daily", 2, 10, None),
    "stretti-dettaglio.json": ("daily (curated + automatic parts)", 2, 7, None),
    "wind-calendar.json":     ("daily validation", 2, None, None),
    "transit-times.json":     ("daily", 2, 14, None),
    "rischio.json":           ("daily (risk dashboard)", 2, 14, None),
    "port-risk.json":         ("daily (port risk index)", 2, 14, None),
    "mercati.json":           ("manual market collections, about weekly", 8, 8, ["data"]),
    "health.json":            ("daily (this check)", 2, None, None),
}
MENSILE = ["eventi.json", "mobili.json", "ibrido.json", "iran.json", "italia.json", "difesa.json", "fissi.json",
           "dossier.json", "report.json", "basi-mondo.json", "assicurazioni.json", "cyber-energia.json",
           "ai-mondo.json", "investimenti.json", "ai.json", "minerali.json", "commercio.json", "paesi.json",
           "idrogeno.json", "eolico-filiera.json", "supply-chain-ai.json", "simulatore.json", "webcam.json",
           "fronte.json", "fronte-storico.json", "ferrovie.json", "nucleare.json", "cavi.json",
           "cavi-incidenti.json", "interconnessioni.json", "rete-elettrica.json"]
for _f in MENSILE:
    CADENZA.setdefault(_f, (M, 35, None, None))
STATICI = ["world.json", "medio-oriente.json", "labels.json", "linee.json", "condotte.json", "rotte.json",
           "stretti.json", "manifest.json"]
for _f in STATICI:
    CADENZA.setdefault(_f, (S, None, None, None))
# Mobile military positions get old fast even if the file is curated: one more limit.
LIMITI_EXTRA = {"mobili.json": ("positions of mobile units", 14)}

# Severity order (worst first) and the weight used for the overall status.
GRAVITA = ["critical", "high", "medium", "low", "info"]
FIX = {
    "parse": "Re-run the collector that writes this file; if it was edited by hand, restore it from git (git checkout <file>) and fix the JSON.",
    "missing": "Run the collector once (see raccolta/<domain>/) or remove the file from the map if it is retired.",
    "stale": "Check the GitHub Actions log of the step that writes this file; run the collector by hand; if the source moved, update the URL in the collector.",
    "stale-curated": "Curated layer: schedule the monthly review of this file (agent or by hand) and refresh dates and sources.",
    "stale-series": "The collector ran but this series did not move: check the source endpoint and the API key for this series.",
    "drop": "A collector probably broke silently (empty answer, changed format, missing key). Compare with yesterday's file in git and look at the step log.",
    "coords": "Fix the coordinates at the source (curated file in raccolta/<domain>/) and re-run the collector; never guess coordinates.",
    "fields": "Add fonte/link/data_fonte/affidabilita to the points in the curated input of this collector (raccolta/AGENTI.md, Punti).",
    "errors": "Read the error text: missing key -> add the secret to the workflow env; HTTP error -> check the source URL; then re-run.",
    "link": "Replace the URL with the current page of the same source (or an archived copy at web.archive.org) in the curated file, then re-run the collector.",
    "mismatch-data": "Files disagree on the same fact: re-run the collector that copies the value (it read an older version) and make it read the value at run time, not from a cached copy.",
    "mismatch-report": "Correct the figure in the report (Markdown and HTML) or add a dated note that the report used an earlier reading.",
    "secret": "Remove the value, rotate the key at the provider at once (it stays in git history), and check raccolta/comune/nascondi_chiavi.py covers the pattern.",
    "licence": "Add a row for the file to DATA_LICENSES.md (sources, licence, conditions), taken from its fonti[] field.",
    "validator": "Run the validator by hand, read its output and fix the curated input it names.",
    "smoke": "Open the page in a browser with the console open; fix the JS error or the missing data file (only the Regia session edits docs/index.html).",
}


# ----------------------------------------------------------------------------- small helpers
def leggi(percorso, predefinito=None):
    try:
        with open(percorso, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return predefinito


def scrivi(percorso, dato, indent=1):
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    tmp = percorso + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dato, f, ensure_ascii=False, indent=indent)
        f.write("\n")
    os.replace(tmp, percorso)


def data_da(testo):
    """First YYYY-MM-DD in a string, as a date, or None."""
    if not isinstance(testo, str):
        return None
    m = re.match(r"\s*(\d{4})-(\d{2})-(\d{2})", testo)
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def cammina(o, percorso="", profondita=0):
    """Yields (path, key, value, parent) for every value in a JSON tree."""
    if profondita > 40:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            p = f"{percorso}.{k}" if percorso else k
            yield p, k, v, o
            yield from cammina(v, p, profondita + 1)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            p = f"{percorso}[{i}]"
            yield p, None, v, o
            yield from cammina(v, p, profondita + 1)


def prendi(o, percorso):
    """Dot path with key[field=value] and key[3] selectors. Returns None if missing."""
    for parte in re.findall(r"[^.\[\]]+(?:\[[^\]]*\])*", percorso):
        m = re.match(r"([^\[]+)((?:\[[^\]]*\])*)$", parte)
        if not m:
            return None
        chiave, selettori = m.group(1), re.findall(r"\[([^\]]*)\]", m.group(2))
        if not isinstance(o, dict) or chiave not in o:
            return None
        o = o[chiave]
        for s in selettori:
            if not isinstance(o, list):
                return None
            if re.fullmatch(r"-?\d+", s):
                i = int(s)
                o = o[i] if -len(o) <= i < len(o) else None
            elif "=" in s:
                c, v = s.split("=", 1)
                o = next((x for x in o if isinstance(x, dict) and str(x.get(c)) == v), None)
            if o is None:
                return None
    return o


def valore_in_serie(serie, giorno):
    if not isinstance(serie, list):
        return None
    for x in serie:
        if isinstance(x, (list, tuple)) and len(x) >= 2 and str(x[0])[:10] == giorno:
            return x[1]
    return None


def numero(testo, lingua):
    t = testo.replace("−", "-").replace(" ", "").replace(" ", "")
    if lingua == "it":
        t = t.replace(".", "").replace(",", ".")
    else:
        t = t.replace(",", "")
    return float(t)


def decimali(testo):
    t = testo.replace("−", "-")
    sep = "," if "," in t and not re.search(r"\.\d{3}\b", t) and "." not in t else "."
    if sep in t:
        return len(t.split(sep)[-1])
    return 0


def fmt(x):
    if isinstance(x, float):
        return f"{x:.4g}" if abs(x) < 1e6 else f"{x:.0f}"
    return str(x)


# ----------------------------------------------------------------------------- result collector
class Esito:
    def __init__(self):
        self.checks = []          # {area, name, status, detail}
        self.problemi = []        # {severity, area, file, problem, fix}
        self.stale, self.broken, self.mismatches = [], [], []
        self.counts = {}
        self.segreti = []

    def check(self, area, nome, stato, dettaglio):
        self.checks.append({"area": area, "name": nome, "status": stato, "detail": dettaglio})

    def problema(self, gravita, area, file, testo, fix):
        self.problemi.append({"severity": gravita, "area": area, "file": file, "problem": testo, "fix": FIX.get(fix, fix)})


def protetto(R, area, nome):
    """Decorator: a check that crashes becomes a red check, never a crash of the script."""
    def deco(fn):
        def run(*a, **k):
            try:
                return fn(*a, **k)
            except Exception as e:  # noqa: BLE001
                R.check(area, nome, "red", f"check crashed: {type(e).__name__}: {e}")
                R.problema("medium", area, "raccolta/qualita/controlla_tutto.py", f"the check '{nome}' crashed: {e}",
                           "Fix the health check: " + traceback.format_exc(limit=1).strip().splitlines()[-1])
                return None
        return run
    return deco


# ----------------------------------------------------------------------------- load all files
def carica_tutti(R):
    dati, rotti = {}, {}
    for p in sorted(glob.glob(os.path.join(DATI, "*.json"))):
        nome = os.path.basename(p)
        if nome == "health.json":
            continue
        try:
            with open(p, encoding="utf-8") as f:
                dati[nome] = json.load(f)
        except Exception as e:  # noqa: BLE001
            rotti[nome] = str(e)
    if rotti:
        for n, e in rotti.items():
            R.problema("critical", "schema", f"docs/data/{n}", f"does not parse as JSON: {e}", "parse")
        R.check("schema", "JSON parses", "red", f"{len(rotti)} of {len(dati) + len(rotti)} files do not parse: {', '.join(rotti)}")
    else:
        R.check("schema", "JSON parses", "green", f"all {len(dati)} files in docs/data parse")
    return dati


# ----------------------------------------------------------------------------- a) freshness
def campo_aggiornato(d):
    if not isinstance(d, dict):
        return None, None
    for k in ("aggiornato", "updated", "generato", "generated", "compilato"):
        if k in d:
            return k, d[k]
    return None, None


def data_piu_recente(d, chiavi):
    best = None
    for _p, k, v, _par in cammina(d):
        if chiavi is not None and k not in chiavi:
            # series values [["YYYY-MM-DD", n], ...] count as data dates only with chiavi None
            continue
        if k in ("aggiornato", "updated", "riferimento", "data_riferimento", "reference_date", "generato"):
            continue
        cand = None
        if isinstance(v, str):
            cand = data_da(v)
        if cand and cand <= OGGI and (best is None or cand > best):
            best = cand
    if chiavi is None:
        return best
    return best


def freschezza(R, dati):
    n_ok = n_stale = n_missing = 0
    for nome in sorted(set(CADENZA) | set(dati)):
        if nome == "health.json":
            continue
        cad = CADENZA.get(nome)
        if nome not in dati:
            if os.path.exists(os.path.join(DATI, nome)):
                continue  # parse failure, already reported
            if cad and cad[0] != S:
                n_missing += 1
                R.stale.append({"file": nome, "status": "missing", "cadence": cad[0]})
                R.problema("high", "freshness", f"docs/data/{nome}", "expected by the cadence table but missing", "missing")
            continue
        if cad is None:
            cad = (M, 35, None, None)
            R.problema("low", "freshness", f"docs/data/{nome}", "no cadence defined in CADENZA (treated as monthly curated)",
                       "Add the file to the CADENZA table of raccolta/qualita/controlla_tutto.py.")
        etichetta, max_agg, max_dato, chiavi = cad
        d = dati[nome]
        k, v = campo_aggiornato(d)
        agg = data_da(v) if v else None
        recente = data_piu_recente(d, chiavi) if (max_dato is not None or etichetta != S) else None
        voce = {"file": nome, "cadence": etichetta, "updated": v, "newest_data_date": recente.isoformat() if recente else None}
        stato, motivi = "ok", []
        if etichetta == S:
            voce["status"] = "ok (static)"
            n_ok += 1
            continue
        if agg is None:
            stato = "missing"
            motivi.append("no 'aggiornato'/'updated' field")
        else:
            eta = (OGGI - agg).days
            voce["updated_age_days"] = eta
            if max_agg is not None and eta > max_agg:
                stato = "stale"
                motivi.append(f"updated {eta} days ago (limit {max_agg})")
        if max_dato is not None:
            if recente is None:
                stato = "stale" if stato == "ok" else stato
                motivi.append("no data date found inside")
            else:
                eta_d = (OGGI - recente).days
                voce["data_age_days"] = eta_d
                if eta_d > max_dato:
                    stato = "stale"
                    motivi.append(f"newest data {recente} is {eta_d} days old (limit {max_dato})")
        if nome in LIMITI_EXTRA and isinstance(d, dict):
            descr, lim = LIMITI_EXTRA[nome]
            vecchi = 0
            for p in d.get("punti", []) or []:
                g = data_da(p.get("data_fonte") or p.get("data_evento") or "")
                if g and (OGGI - g).days > lim and not p.get("dubbia"):
                    vecchi += 1
            if vecchi:
                R.problema("medium", "freshness", f"docs/data/{nome}", f"{vecchi} {descr} older than {lim} days and not marked as dated ('dubbia')", "stale-curated")
        voce["status"] = stato
        if motivi:
            voce["why"] = "; ".join(motivi)
        if stato == "ok":
            n_ok += 1
        else:
            if stato == "stale":
                n_stale += 1
            else:
                n_missing += 1
            R.stale.append(voce)
            curato = etichetta == M
            R.problema("medium" if curato else "high", "freshness", f"docs/data/{nome}",
                       f"{stato}: {'; '.join(motivi)} (cadence: {etichetta})", "stale-curated" if curato else "stale")
    # series inside files: elements that declare a daily/weekly frequency and lag behind
    lag = {"giornaliera": 6, "daily": 6, "settimanale": 16, "weekly": 16, "mensile": 135, "monthly": 135}   # Eurostat/IMF monthly data arrive 2-4 months late
    indietro = []
    for nome, d in dati.items():
        if not isinstance(d, dict):
            continue
        for e in d.get("elementi", []) if isinstance(d.get("elementi"), list) else []:
            if not isinstance(e, dict):
                continue
            fr = str(e.get("frequenza") or e.get("frequency") or "").lower()
            if fr not in lag:
                continue
            ult = e.get("ultimo") if isinstance(e.get("ultimo"), dict) else {}
            g = data_da(str(e.get("data_fonte") or ult.get("data") or ""))
            if g and (OGGI - g).days > lag[fr]:
                indietro.append(f"{nome}:{e.get('id')} ({fr}, last {g})")
    for x in indietro:
        f = x.split(":")[0]
        R.problema("medium", "freshness", f"docs/data/{f}", f"series lagging behind its frequency: {x.split(':', 1)[1]}", "stale-series")
    assenti = sum(1 for x in R.stale if x.get("status") == "missing" and x["file"] not in dati)
    stato = "red" if assenti or n_stale > 5 else ("amber" if n_stale or n_missing or indietro else "green")
    # market series must not fall on weekends (date convention of the price collector)
    for s_ in (dati.get("prezzi.json") or {}).get("serie", []):
        if s_.get("gruppo") in ("Cripto", "Crypto") or s_.get("id") in ("btc", "eth"):
            continue
        fs = [x[0] for x in s_.get("serie", []) if isinstance(x, list) and data_da(str(x[0])) and data_da(str(x[0])).weekday() >= 5]
        if fs:
            R.problema("medium", "freshness", "docs/data/prezzi.json", f"series {s_.get('id')}: {len(fs)} values dated on a weekend "
                       f"(e.g. {', '.join(fs[:3])}): session dates are shifted", "Check the time-zone conversion in raccolta/scarica_mercati.py.")
    R.check("freshness", "files against cadence", stato,
            f"{n_ok} ok, {n_stale} stale, {n_missing} missing; {len(indietro)} lagging series inside files")


# ----------------------------------------------------------------------------- b) schema
LISTE_PRINCIPALI = ["elementi", "punti", "ports", "routes", "linee", "rotte", "serie", "unita", "dossier",
                    "reports", "parchi", "storie", "istantanee", "countries", "giorni", "anelli", "passaggi"]
ALTERNATIVE = {
    "fonte": ["fonte", "source", "fonti", "sources"],
    "link": ["link", "links", "url", "fonti", "sources", "source_links"],
    "data_fonte": ["data_fonte", "source_date", "data", "date", "data_evento", "ora_utc", "fonti"],
    "affidabilita": ["affidabilita", "reliability", "affidabilità"],
}
# Files whose elements are cards (country or chokepoint sheets with sources inside each fact), not map points.
SCHEDE = {"stretti-dettaglio.json", "esposizione-nord.json", "paesi.json", "commercio.json", "minerali.json"}
AFF_OK = {"alta", "media", "bassa", "high", "medium", "low"}


def conta(d):
    if isinstance(d, list):
        return len(d)
    if not isinstance(d, dict):
        return 0
    for k in LISTE_PRINCIPALI:
        v = d.get(k)
        if isinstance(v, list) and v:
            return len(v)
    if d.get("type") == "Topology":
        return len(d.get("arcs", []))
    tot = sum(len(v) for v in d.values() if isinstance(v, list))
    tot += sum(len(v) for k, v in d.items() if isinstance(v, dict) and k not in ("schema", "notes", "regole", "rules"))
    return tot


def pieno(v):
    return v not in (None, "", [], {})


def schema(R, dati):
    problemi_coord = 0
    for nome, d in sorted(dati.items()):
        R.counts[nome] = conta(d)
        if not isinstance(d, (dict, list)):
            continue
        cattive, esempi, totale = 0, [], 0
        for p, k, v, par in cammina(d):
            if isinstance(v, dict) and ("lat" in v or "lon" in v):
                totale += 1
                lat, lon = v.get("lat"), v.get("lon")
                motivo = None
                if v.get("lat") is None and v.get("lon") is None:
                    continue  # explicitly unlocated (null): allowed
                if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)) or isinstance(lat, bool):
                    motivo = f"non-numeric lat/lon ({lat!r}, {lon!r})"
                elif not (-90 <= lat <= 90 and -180 <= lon <= 180) or math.isnan(lat) or math.isnan(lon):
                    motivo = f"out of range ({lat}, {lon})"
                elif lat == 0 and lon == 0:
                    motivo = "(0, 0): probably a missing coordinate"
                if motivo:
                    cattive += 1
                    if len(esempi) < 3:
                        esempi.append(f"{p}: {motivo}")
        # lines: g = parts of [lon, lat]
        fuori = 0
        if isinstance(d, dict):
            for lista in (d.get("elementi"), d.get("linee"), d.get("rotte")):
                for e in lista or []:
                    if isinstance(e, dict) and isinstance(e.get("g"), list):
                        parti = [e["g"]] if e["g"] and isinstance(e["g"][0], list) and e["g"][0] and isinstance(e["g"][0][0], (int, float)) else e["g"]
                        for parte in parti:
                            for c in parte if isinstance(parte, list) else []:
                                if not (isinstance(c, list) and len(c) >= 2 and isinstance(c[0], (int, float))
                                        and isinstance(c[1], (int, float)) and -180 <= c[0] <= 180 and -90 <= c[1] <= 90):
                                    fuori += 1
        if cattive or fuori:
            problemi_coord += 1
            R.problema("high" if cattive > 10 else "medium", "schema", f"docs/data/{nome}",
                       f"{cattive} of {totale} points with bad coordinates{'; ' + str(fuori) + ' bad line vertices' if fuori else ''}"
                       f"{(': ' + '; '.join(esempi)) if esempi else ''}", "coords")
        # required fields on the main point list
        if isinstance(d, dict):
            for k in ("elementi", "punti"):
                lista = d.get(k)
                if not isinstance(lista, list):
                    continue
                punti = [x for x in lista if isinstance(x, dict) and isinstance(x.get("lat"), (int, float))]
                if len(punti) < 3:
                    continue
                mancano = {}
                aff_strane = 0
                for x in punti:
                    for campo, alt in ALTERNATIVE.items():
                        if not any(pieno(x.get(a)) for a in alt):
                            mancano[campo] = mancano.get(campo, 0) + 1
                    a = x.get("affidabilita", x.get("reliability"))
                    if pieno(a) and str(a).lower() not in AFF_OK:
                        aff_strane += 1
                if mancano:
                    quota = max(mancano.values()) / len(punti) if nome not in SCHEDE else 0
                    det = ", ".join(f"{c} missing in {n}/{len(punti)}" for c, n in mancano.items())
                    R.problema("medium" if quota > 0.05 else "low", "schema", f"docs/data/{nome}", f"source fields on '{k}': {det}", "fields")
                if aff_strane:
                    R.problema("low", "schema", f"docs/data/{nome}", f"{aff_strane} points with reliability outside alta/media/bassa", "fields")
    R.check("schema", "coordinates", "amber" if problemi_coord else "green",
            f"{problemi_coord} files with bad coordinates" if problemi_coord else "all lat/lon numeric and in range")
    n_campi = sum(1 for p in R.problemi if p["area"] == "schema" and "source fields" in p["problem"])
    R.check("schema", "source fields on points", "amber" if any(p["severity"] == "medium" and "source fields" in p["problem"] for p in R.problemi) else "green",
            f"{n_campi} files with points lacking fonte/link/data_fonte/affidabilita")


def conteggi_ieri_da_git():
    """Counts of yesterday's committed files, when the storico has no previous day (first run)."""
    try:
        ieri = (OGGI - dt.timedelta(days=1)).isoformat()
        sha = subprocess.run(["git", "-C", RADICE, "log", "-1", f"--until={ieri}T23:59:59Z", "--format=%H"],
                             capture_output=True, text=True, timeout=20).stdout.strip()
        if not sha:
            return None, None
        out = {}
        files = subprocess.run(["git", "-C", RADICE, "ls-tree", "--name-only", sha, "docs/data/"],
                               capture_output=True, text=True, timeout=20).stdout.split()
        for f in files:
            if not f.endswith(".json"):
                continue
            r = subprocess.run(["git", "-C", RADICE, "show", f"{sha}:{f}"], capture_output=True, timeout=20)
            try:
                out[os.path.basename(f)] = conta(json.loads(r.stdout.decode("utf-8")))
            except Exception:  # noqa: BLE001
                pass
        return out, f"git {sha[:7]} (last commit of {ieri})"
    except Exception:  # noqa: BLE001
        return None, None


def confronta_conteggi(R):
    storico = leggi(STORICO, {}) or {}
    giorni = storico.get("giorni", {})
    precedenti = sorted(g for g in giorni if g < OGGI.isoformat())
    if precedenti:
        prima, origine = giorni[precedenti[-1]], f"storico.json {precedenti[-1]}"
    else:
        prima, origine = conteggi_ieri_da_git()
    cali = []
    if prima:
        for f, n in R.counts.items():
            p = prima.get(f)
            if p and p >= 5 and n < p * 0.8:
                cali.append((f, p, n))
                R.problema("high", "schema", f"docs/data/{f}", f"element count fell {p} -> {n} ({(n - p) / p * 100:+.0f}%) vs {origine}", "drop")
        spariti = [f for f in prima if f not in R.counts and f != "health.json"]
        for f in spariti:
            R.problema("medium", "schema", f"docs/data/{f}", f"file present in {origine} is gone (if retired on purpose, also remove "
                       "it from DATA_LICENSES.md, manifest.json and the pages that load it)", "missing")
        R.check("schema", "counts vs yesterday", "red" if cali or spariti else "green",
                f"compared with {origine}: {len(cali)} drops > 20%" + (f", {len(spariti)} files gone" if spariti else ""))
    else:
        R.check("schema", "counts vs yesterday", "amber", "no previous counts (first run, no git history): baseline saved")
    giorni[OGGI.isoformat()] = R.counts
    for g in sorted(giorni)[:-60]:
        giorni.pop(g, None)
    scrivi(STORICO, {"nota": "Element count per docs/data file per day, written by controlla_tutto.py (last 60 days).", "giorni": giorni})


# ----------------------------------------------------------------------------- c) errors
def errori(R, dati):
    tot, file_con = 0, 0
    for nome, d in sorted(dati.items()):
        if not isinstance(d, dict):
            continue
        for k in ("errori", "errors"):
            v = d.get(k)
            if isinstance(v, list) and v:
                file_con += 1
                tot += len(v)
                giornaliero = CADENZA.get(nome, (M,))[0] not in (M, S)
                for e in v[:8]:
                    testo = e if isinstance(e, str) else json.dumps(e, ensure_ascii=False)
                    R.problema("medium" if giornaliero else "low", "errors", f"docs/data/{nome}", f"collector error: {testo[:300]}", "errors")
                if len(v) > 8:
                    R.problema("low", "errors", f"docs/data/{nome}", f"... and {len(v) - 8} more errors", "errors")
        for k in ("avvisi", "warnings"):
            v = d.get(k)
            if isinstance(v, list) and v:
                R.problema("info", "errors", f"docs/data/{nome}", f"{len(v)} warnings ('{k}'), first: {str(v[0])[:200]}", "errors")
    R.check("errors", "errori/errors arrays", "amber" if tot else "green", f"{tot} errors in {file_con} files")


# ----------------------------------------------------------------------------- d) links
def raccogli_link(dati):
    link = {}
    for nome, d in dati.items():
        for _p, k, v, _par in cammina(d):
            if k is None or not (("link" in k.lower()) or k.lower() in ("url", "href", "fonte_url")):
                continue
            valori = v if isinstance(v, list) else [v]
            for u in valori:
                if isinstance(u, dict):
                    u = u.get("link") or u.get("url")
                if isinstance(u, str) and re.match(r"https?://", u.strip()):
                    u = u.strip()
                    link.setdefault(u, set()).add(nome)
    return link


def prova_link(u):
    """Returns (result, code, detail). result: ok / broken / blocked / proxy / error."""
    parti = urllib.parse.urlsplit(u)
    try:
        host = parti.netloc.encode("idna").decode("ascii") if any(ord(c) > 127 for c in parti.netloc) else parti.netloc
    except Exception:  # noqa: BLE001
        host = parti.netloc
    u = urllib.parse.urlunsplit((parti.scheme, host, urllib.parse.quote(parti.path, safe="/%:@!$&'()*+,;=-._~"),
                                 urllib.parse.quote(parti.query, safe="=&%+/:,;@!$'()*-._~?"), ""))
    def apri(metodo):
        req = urllib.request.Request(u, method=metodo, headers={"User-Agent": UA, "Accept": "*/*"})
        if metodo == "GET":
            req.add_header("Range", "bytes=0-2047")
        with urllib.request.urlopen(req, timeout=TIMEOUT_LINK) as r:
            if metodo == "GET":
                r.read(2048)
            return r.status
    try:
        try:
            return "ok", apri("HEAD"), ""
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                # confirm with GET: some servers answer HEAD badly
                pass
            elif e.code not in (400, 403, 405, 406, 429, 500, 501, 502, 503):
                return ("broken" if e.code >= 400 else "ok"), e.code, ""
        try:
            return "ok", apri("GET"), ""
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 429, 451, 999):
                return "blocked", e.code, "anti-bot or login wall: not counted as broken"
            if e.code in (404, 410) or e.code >= 500 or e.code == 400:
                return "broken", e.code, ""
            return "error", e.code, ""
    except urllib.error.URLError as e:
        r = str(e.reason)
        if "Tunnel connection failed" in r or "407" in r:
            return "proxy", None, f"blocked by the local network proxy ({r[:80]}): not tested"
        if u.startswith("http://") and os.environ.get("HTTPS_PROXY") and not os.environ.get("HTTP_PROXY"):
            return "proxy", None, "plain-http link not testable behind an HTTPS-only proxy"
        if any(x in r for x in ("Name or service not known", "nodename nor servname", "getaddrinfo failed", "No address associated")):
            return "broken", None, f"DNS: {r[:100]}"
        if "CERTIFICATE_VERIFY_FAILED" in r:
            return "error", None, f"TLS: {r[:100]}"
        return "error", None, r[:120]
    except Exception as e:  # noqa: BLE001  (timeouts, resets)
        return "error", None, f"{type(e).__name__}: {str(e)[:100]}"


def link_check(R, dati):
    tutti = raccogli_link(dati)
    archivio = leggi(LINK_STORICO, {}) or {}
    rec = archivio.get("link", {})
    ordinati = sorted(tutti, key=lambda u: hashlib.sha1(u.encode()).hexdigest())
    n = len(ordinati)
    if SENZA_RETE or n == 0:
        R.check("links", "source links", "amber" if SENZA_RETE else "green",
                f"{n} distinct links found; not checked (offline run)" if SENZA_RETE else "no links found")
        campione = []
    else:
        giorno = OGGI.toordinal()
        inizio = (giorno * N_LINK) % n
        campione = (ordinati[inizio:] + ordinati[:inizio])[:min(N_LINK, n)]
        # links that failed last time go first, so a broken link is confirmed the next day
        da_rivedere = [u for u, r in rec.items() if r.get("fails_in_a_row", 0) >= 1 and u in tutti and u not in campione]
        campione = (da_rivedere[:40] + campione)[:N_LINK + 40]
    risultati = {}
    if campione:
        per_host = {}
        for u in campione:
            per_host.setdefault(urllib.parse.urlsplit(u).netloc, []).append(u)
        # one worker per host at a time; 8 hosts in parallel; short pause between requests to the same host
        def lavora(lista):
            out = {}
            for i, u in enumerate(lista):
                if time.time() - INIZIO > BUDGET_LINK_S + 60:
                    break
                out[u] = prova_link(u)
                time.sleep(0.5)
            return out
        with cf.ThreadPoolExecutor(max_workers=8) as ex:
            futuri = [ex.submit(lavora, l) for l in per_host.values()]
            fine = time.time() + BUDGET_LINK_S
            for fu in futuri:
                try:
                    risultati.update(fu.result(timeout=max(1, fine - time.time())))
                except Exception:  # noqa: BLE001
                    pass
    adesso = ADESSO.strftime("%Y-%m-%dT%H:%MZ")
    for u, (esito, codice, det) in risultati.items():
        r = rec.setdefault(u, {})
        r["files"] = sorted(tutti.get(u, []))[:5]
        r["last_checked"] = adesso
        r["last_result"] = esito
        r["last_code"] = codice
        if det:
            r["detail"] = det
        else:
            r.pop("detail", None)
        if esito == "broken":
            r["fails_in_a_row"] = r.get("fails_in_a_row", 0) + 1
            r.setdefault("first_failed", adesso)
        elif esito == "ok":
            r["fails_in_a_row"] = 0
            r.pop("first_failed", None)
        r["history"] = (r.get("history", []) + [f"{OGGI.isoformat()}:{esito}:{codice or ''}"])[-6:]
    # forget links no longer in the data
    for u in list(rec):
        if u not in tutti:
            rec.pop(u)
    rotti = []
    for u, r in rec.items():
        if r.get("last_result") == "broken":
            conf = r.get("fails_in_a_row", 0) >= 2
            rotti.append({"url": u, "files": r.get("files", []), "code": r.get("last_code"), "detail": r.get("detail", ""),
                          "fails_in_a_row": r.get("fails_in_a_row", 0), "first_failed": r.get("first_failed"),
                          "confirmed": conf})
    rotti.sort(key=lambda x: (-x["fails_in_a_row"], x["url"]))
    R.broken = rotti
    for b in rotti:
        R.problema("medium" if b["confirmed"] else "low", "links", ", ".join("docs/data/" + f for f in b["files"]),
                   f"{'broken' if b['confirmed'] else 'failed once (re-checked tomorrow)'}: {b['url']} "
                   f"({b['code'] or b['detail']})", "link")
    archivio = {"nota": "Rolling record of source-link checks (controlla_tutto.py). A link is 'broken' after 2 failed checks in a row; "
                        "401/403/429 answers are anti-bot walls, not broken links; 'proxy' = not reachable from the check environment.",
                "aggiornato": adesso, "link_totali": n, "link": rec}
    scrivi(LINK_STORICO, archivio)
    if campione:
        conta_e = {}
        for e, _c, _d in risultati.values():
            conta_e[e] = conta_e.get(e, 0) + 1
        conf = sum(1 for b in rotti if b["confirmed"])
        stato = "red" if conf > 20 else ("amber" if rotti else "green")
        R.check("links", "source links (rotating sample)", stato,
                f"{len(risultati)} of {n} distinct links checked today: " + ", ".join(f"{v} {k}" for k, v in sorted(conta_e.items()))
                + f"; {conf} confirmed broken, {len(rotti) - conf} failed once (rolling record)")


# ----------------------------------------------------------------------------- e) consistency
def mismatch(R, fatto, valori, gravita, fix, nota=""):
    R.mismatches.append({"fact": fatto, "values": valori, "severity": gravita, "note": nota})
    testo = "; ".join(f"{v['file']} {v.get('path', '')} = {fmt(v['value'])}" + (f" ({v['date']})" if v.get("date") else "") for v in valori)
    R.problema(gravita, "consistency", ", ".join(sorted({v["file"] for v in valori})), f"{fatto}: {testo}{('. ' + nota) if nota else ''}", fix)


def vicini(a, b, abs_=0.05, pct=0.0):
    if a is None or b is None:
        return True
    return abs(a - b) <= max(abs_, abs(b) * pct / 100)


def coerenza(R, dati):
    n_conf, n_mis = 0, 0
    pw = dati.get("portwatch.json", {})
    pw_nome = {e.get("nome"): e for e in pw.get("elementi", []) if e.get("tipo") == "chokepoint"}
    pw_en = {e.get("nome_portwatch"): e for e in pw.get("elementi", []) if e.get("tipo") == "chokepoint"}
    # 1. chokepoint 7-day transits: portwatch vs rischio vs transit-times vs stretti-dettaglio
    rk = dati.get("rischio.json", {})
    for u in rk.get("unita", []):
        for i in u.get("indicatori", []):
            if i.get("file") != "portwatch.json" or i.get("media7") is None:
                continue
            m = re.match(r"(?:Transiti|Petroliere e metaniere|Portacontainer), (.+?) \(media 7 gg\)", i.get("nome", ""))
            if not m or m.group(1) not in pw_nome:
                continue
            e = pw_nome[m.group(1)]
            campo = "n_tanker" if i["nome"].startswith("Petroliere") else ("n_container" if i["nome"].startswith("Portacontainer") else "n_total")
            v_pw = (e.get("media7") or {}).get(campo)
            n_conf += 1
            if not vicini(i["media7"], v_pw, 0.051) or (i.get("data") and i.get("data") != e.get("ultima_data")):
                n_mis += 1
                mismatch(R, f"{m.group(1)} 7-day transits ({campo})", [
                    {"file": "portwatch.json", "path": f"elementi[id={e.get('id')}].media7.{campo}", "value": v_pw, "date": e.get("ultima_data")},
                    {"file": "rischio.json", "path": f"unita[id={u['id']}].indicatori[{i['nome']}].media7", "value": i["media7"], "date": i.get("data")}],
                    "high", "mismatch-data", "rischio.json should be recomputed after portwatch.json (workflow order)")
    tt = dati.get("transit-times.json", {})
    alias = {"Bab el-Mandeb": "Bab el-Mandeb Strait", "Strait of Gibraltar": "Gibraltar Strait", "Danish straits (Oresund)": "Oresund Strait"}
    for k, v in (tt.get("portwatch_transits_per_day") or {}).items():
        e = pw_en.get(alias.get(k, k))
        if not e or not isinstance(v, dict):
            continue
        n_conf += 1
        a, b = v.get("transits_7d_avg"), (e.get("media7") or {}).get("n_total")
        if not vicini(a, b, 0.051) or v.get("date") != e.get("ultima_data"):
            n_mis += 1
            mismatch(R, f"{k} 7-day transits", [
                {"file": "portwatch.json", "path": f"elementi[id={e.get('id')}].media7.n_total", "value": b, "date": e.get("ultima_data")},
                {"file": "transit-times.json", "path": f"portwatch_transits_per_day.{k}.transits_7d_avg", "value": a, "date": v.get("date")}],
                "high", "mismatch-data")
    sd = dati.get("stretti-dettaglio.json", {})
    for e in sd.get("elementi", []):
        aa = prendi(e, "stato_attuale.automatico.altri_agenti") or {}
        copia = (aa.get("portwatch.json") or {}).get("dato")
        if isinstance(copia, dict) and copia.get("id"):
            orig = next((x for x in pw.get("elementi", []) if x.get("id") == copia["id"]), None)
            if orig:
                n_conf += 1
                a, b = (copia.get("media7") or {}).get("n_total"), (orig.get("media7") or {}).get("n_total")
                if not vicini(a, b, 0.051) or copia.get("ultima_data") != orig.get("ultima_data"):
                    n_mis += 1
                    mismatch(R, f"{orig.get('nome')} 7-day transits (copy in stretti-dettaglio)", [
                        {"file": "portwatch.json", "path": f"elementi[id={orig['id']}].media7.n_total", "value": b, "date": orig.get("ultima_data")},
                        {"file": "stretti-dettaglio.json", "path": f"elementi[id={e.get('id')}].stato_attuale.automatico.altri_agenti", "value": a, "date": copia.get("ultima_data")}],
                        "medium", "mismatch-data")
    # 2. chokepoint scores: rischio vs port-risk (English names in port-risk texts)
    nomi_pr = {"Strait of Hormuz": "hormuz", "Qatar LNG (Ras Laffan → Hormuz)": "gnl-qatar",
               "Red Sea (Asia–Europe container route)": "mar-rosso-container", "Baltic (cables, pipelines, power links)": "baltico",
               "Danish straits": "stretti-danesi", "Bab el-Mandeb": "bab-el-mandeb", "Suez Canal": "suez",
               "Turkish Straits (Bosphorus and Dardanelles)": "stretti-turchi", "Strait of Gibraltar": "gibilterra",
               "Sicily Channel": "canale-di-sicilia", "TransMed Algeria–Tunisia–Italy": "transmed", "Kerch Strait": "kerch"}
    punteggi = {u.get("id"): u.get("punteggio") for u in rk.get("unita", [])}
    visti = set()
    for p in (dati.get("port-risk.json") or {}).get("ports", []):
        for i in p.get("indicators", []):
            if i.get("group") != "chokepoints":
                continue
            for m in re.finditer(r"([A-Z][^;]*?)\s+(\d+(?:\.\d+)?)/25", i.get("text", "")):
                nome, val = m.group(1).strip(), float(m.group(2))
                rid = nomi_pr.get(nome)
                if not rid or (rid, val) in visti:
                    continue
                visti.add((rid, val))
                n_conf += 1
                if punteggi.get(rid) is not None and abs(float(punteggi[rid]) - val) > 0.051:
                    n_mis += 1
                    mismatch(R, f"chokepoint score {nome}", [
                        {"file": "rischio.json", "path": f"unita[id={rid}].punteggio", "value": punteggi[rid], "date": rk.get("data_riferimento")},
                        {"file": "port-risk.json", "path": f"ports[id={p.get('id')}].indicators[chokepoints]", "value": val, "date": i.get("date")}],
                        "high", "mismatch-data", "port-risk must run after rischio (workflow order)")
    # 3. port calls: porti-nord / portwatch ports vs esposizione-nord vs port-risk
    pn = dati.get("porti-nord.json", {})
    calls = {}
    for e in pn.get("elementi", []):
        calls[e.get("id")] = ((e.get("media7") or {}).get("portcalls"), e.get("ultima_data"), e.get("nome"))
    for e in pw.get("elementi", []):
        if e.get("tipo") != "chokepoint":
            m7 = e.get("media7") or {}
            calls[e.get("id")] = (m7.get("portcalls", m7.get("n_total")), e.get("ultima_data"), e.get("nome"))
    per_nome = {v[2]: (k, v) for k, v in calls.items()}
    for p in (dati.get("esposizione-nord.json") or {}).get("elementi", []):
        for x in p.get("porti_portwatch") or []:
            k_v = per_nome.get(x.get("nome"))
            if not k_v:
                continue
            n_conf += 1
            if not vicini(x.get("chiamate_media7"), k_v[1][0], 0.051):
                n_mis += 1
                mismatch(R, f"{x.get('nome')} port calls, 7-day mean", [
                    {"file": "porti-nord.json", "path": f"elementi[id={k_v[0]}].media7.portcalls", "value": k_v[1][0], "date": k_v[1][1]},
                    {"file": "esposizione-nord.json", "path": f"elementi[paese={p.get('paese')}].porti_portwatch", "value": x.get("chiamate_media7")}],
                    "medium", "mismatch-data")
    for p in (dati.get("port-risk.json") or {}).get("ports", []):
        src = calls.get(p.get("source_id"))
        if not src:
            continue
        for i in p.get("indicators", []):
            if i.get("name", "").startswith("Port calls, 7-day mean"):
                m = re.match(r"([\d.]+) calls/day", i.get("text", ""))
                if m:
                    n_conf += 1
                    if not vicini(float(m.group(1)), src[0], 0.051) or (i.get("date") and src[1] and i["date"] != src[1]):
                        n_mis += 1
                        mismatch(R, f"{p.get('name')} port calls, 7-day mean", [
                            {"file": "porti-nord.json" if not str(p.get("source_id")).startswith("port") else "portwatch.json",
                             "path": f"elementi[id={p.get('source_id')}].media7", "value": src[0], "date": src[1]},
                            {"file": "port-risk.json", "path": f"ports[id={p.get('id')}].indicators[Port calls]", "value": float(m.group(1)), "date": i.get("date")}],
                            "medium", "mismatch-data")
    # 4. Brent / TTF / WTI anywhere vs prezzi.json at the same date
    prezzi = dati.get("prezzi.json", {})
    serie = {s.get("id"): s for s in prezzi.get("serie", [])}
    chiavi = {"brent": "brent", "petrolio brent": "brent", "brent crude": "brent", "ttf": "ttf", "gas ttf (europa)": "ttf",
              "ttf gas": "ttf", "wti": "wti", "petrolio wti": "wti"}
    trovati = {}
    for nome, d in dati.items():
        if nome == "prezzi.json":
            continue
        for path, _k, v, _par in cammina(d):
            if not isinstance(v, dict):
                continue
            etich = None
            for c in ("id", "indicatore", "nome", "name"):
                if isinstance(v.get(c), str) and v[c].strip().lower() in chiavi:
                    etich = chiavi[v[c].strip().lower()]
                    break
            if not etich or etich not in serie:
                continue
            val = next((v[c] for c in ("ultimo", "valore", "value", "last", "now", "prezzo") if isinstance(v.get(c), (int, float))), None)
            giorno = next((str(v[c])[:10] for c in ("data", "date") if isinstance(v.get(c), str)), None)
            if val is None:
                continue
            rif = valore_in_serie(serie[etich].get("serie"), giorno) if giorno else None
            if rif is None:
                continue
            fonte = str(v.get("fonte") or v.get("source") or v.get("link") or "")
            copia = "prezzi.json" in fonte
            n_conf += 1
            tol = 0.5 if copia else 2.5
            if not vicini(val, rif, 0.0, tol):
                n_mis += 1
                chiave = (etich, nome, round(val, 2), giorno)
                if chiave in trovati:
                    continue
                trovati[chiave] = 1
                mismatch(R, f"{etich.upper()} on {giorno}", [
                    {"file": "prezzi.json", "path": f"serie[id={etich}].serie[{giorno}]", "value": rif, "date": giorno},
                    {"file": nome, "path": path, "value": val, "date": giorno, "source": fonte[:80]}],
                    "medium" if copia else "low", "mismatch-data",
                    f"{abs(val - rif) / rif * 100:.1f}% apart; " + ("the file says it copies prezzi.json: it holds an earlier provisional reading"
                                                                    if copia else "different source or intraday reading (tolerance 2.5%)"))
    # 5. gas storage: scorte vs esposizione-nord
    sc = {e.get("id"): e for e in (dati.get("scorte.json") or {}).get("elementi", [])}
    vuoti = []
    for p in (dati.get("esposizione-nord.json") or {}).get("elementi", []):
        cc = str(p.get("paese", "")).lower()
        s = sc.get(f"gas_stoccaggio_pct_{cc}")
        if not s:
            continue
        st = p.get("stoccaggi_gas")
        n_conf += 1
        if not st:
            vuoti.append(p.get("paese"))
            continue
        giorno = str(st.get("data") or "")[:10]
        rif = valore_in_serie(s.get("serie"), giorno)
        if rif is not None and not vicini(st.get("pieno_pct"), rif, 0.051):
            n_mis += 1
            mismatch(R, f"gas storage fill {p.get('paese')} on {giorno}", [
                {"file": "scorte.json", "path": f"elementi[id={s['id']}].serie", "value": rif, "date": giorno},
                {"file": "esposizione-nord.json", "path": f"elementi[paese={p.get('paese')}].stoccaggi_gas.pieno_pct", "value": st.get("pieno_pct"), "date": giorno}],
                "medium", "mismatch-data")
    if vuoti:
        n_mis += 1
        R.mismatches.append({"fact": "gas storage by country", "severity": "high",
                             "values": [{"file": "scorte.json", "value": "present", "countries": vuoti},
                                        {"file": "esposizione-nord.json", "value": None, "countries": vuoti}],
                             "note": "esposizione-nord.json has stoccaggi_gas = null"})
        R.problema("high", "consistency", "docs/data/esposizione-nord.json",
                   f"gas storage missing (stoccaggi_gas = null) for {', '.join(vuoti)} although scorte.json has AGSI+ data for them; "
                   "the collector skips AGSI+ silently (warning only, errori[] stays empty)",
                   "raccolta/nord/raccogli.py reads GIE_API_KEY but the workflow provides AGSI_API_KEY: read AGSI_API_KEY (or reuse the "
                   "values already in docs/data/scorte.json) and add the skip to errori[] so it is visible.")
    # 6. key report figures
    rep_ok, rep_mis, rep_nf = report_figures(R, dati)
    stato = "red" if n_mis > 10 else ("amber" if n_mis or rep_mis or rep_nf else "green")
    n_dati = sum(1 for m in R.mismatches if not m["fact"].startswith("report figure"))
    R.check("consistency", "same fact across data files", stato, f"{n_conf} comparisons, {n_mis} disagree ({n_dati} distinct mismatches listed)")
    R.check("consistency", "key report figures vs data", "amber" if rep_mis or rep_nf else "green",
            f"{rep_ok} match, {rep_mis} differ, {rep_nf} not found in the report (fatti_chiave.json)")


def report_figures(R, dati):
    fatti = (leggi(FATTI, {}) or {}).get("fatti", [])
    ok = mis = nf = 0
    testi = {}
    for f in fatti:
        try:
            rp = os.path.join(RADICE, f["report"])
            if rp not in testi:
                testi[rp] = open(rp, encoding="utf-8").read() if os.path.exists(rp) else None
            t = testi[rp]
            if t is None:
                nf += 1
                R.problema("low", "consistency", f["report"], f"report missing for key figure '{f['id']}'", "Update fatti_chiave.json.")
                continue
            m = re.search(f["regex"], t)
            if not m:
                nf += 1
                R.problema("low", "consistency", f["report"], f"key figure '{f['id']}' ({f['testo']}) not found: the text changed",
                           "Update the regex in raccolta/qualita/fatti_chiave.json to the new wording.")
                continue
            grezzo = m.group(1)
            val = numero(grezzo, f.get("lingua", "it"))
            dd = leggi(os.path.join(DATI, f["dato"]["file"])) if f["dato"]["file"] not in dati else dati[f["dato"]["file"]]
            rif = prendi(dd, f["dato"]["path"]) if dd is not None else None
            if f["dato"].get("data"):
                rif = valore_in_serie(rif, f["dato"]["data"])
            if not isinstance(rif, (int, float)):
                nf += 1
                R.problema("medium", "consistency", f"docs/data/{f['dato']['file']}",
                           f"key figure '{f['id']}': no value at {f['dato']['path']}{(' on ' + f['dato']['data']) if f['dato'].get('data') else ''}",
                           "The data file changed structure or lost the date: update fatti_chiave.json or the collector.")
                continue
            rif = rif * f.get("scala", 1)
            tol = f.get("tolleranza", {})
            ammesso = max(tol.get("abs", 0), abs(rif) * tol.get("pct", 0) / 100, 0.5 * 10 ** (-decimali(grezzo)) + 1e-9)
            if abs(val - rif) <= ammesso:
                ok += 1
            else:
                mis += 1
                mismatch(R, f"report figure: {f['testo']}", [
                    {"file": f["report"], "path": f"regex '{f['regex'][:40]}'", "value": val},
                    {"file": f["dato"]["file"], "path": f["dato"]["path"], "value": rif, "date": f["dato"].get("data")}],
                    "medium", "mismatch-report", f"difference {val - rif:+.4g}")
        except Exception as e:  # noqa: BLE001
            nf += 1
            R.problema("low", "consistency", "raccolta/qualita/fatti_chiave.json", f"key figure '{f.get('id')}' could not be checked: {e}",
                       "Fix the entry in fatti_chiave.json.")
    return ok, mis, nf


# ----------------------------------------------------------------------------- f) secrets
SCHEMI_SEGRETI = [
    ("api key assignment", re.compile(r"(?i)(api[ _-]?key\W{0,3})([A-Za-z0-9._\-]{16,})")),
    ("key/token in URL", re.compile(r"(?i)[?&](?:api_?key|apikey|access_token|token|auth|key|secret)=([A-Za-z0-9._\-]{16,})")),
    ("credential assignment", re.compile(r"(?i)[\"']?(?:secret|password|passwd|token|access[_-]?key|client[_-]?secret|x-key)[\"']?\s*[:=]\s*[\"']([A-Za-z0-9._\-/+]{16,})[\"']")),
    ("GitHub token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b")),
    ("AWS access key", re.compile(r"\b(AKIA[0-9A-Z]{16})\b")),
    ("Google API key", re.compile(r"\b(AIza[0-9A-Za-z_\-]{35})\b")),
    ("OpenAI/Anthropic-style key", re.compile(r"\b(sk-(?:ant-)?[A-Za-z0-9_\-]{24,})\b")),
    ("Slack token", re.compile(r"\b(xox[abprs]-[A-Za-z0-9-]{10,})\b")),
    ("Bearer token", re.compile(r"(?i)\bBearer\s+([A-Za-z0-9._\-]{24,})")),
    ("private key", re.compile(r"(-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")),
]
def sembra_chiave(s):
    """A key looks random: letters and digits mixed, many distinct characters, not words joined by hyphens (URL slugs)."""
    if not (re.search(r"\d", s) and re.search(r"[A-Za-z]", s)) or len(set(s)) < 10:
        return False
    parti = re.split(r"[-_.]", s)
    if len(parti) >= 3 and sum(1 for x in parti if re.fullmatch(r"[a-z]+|\d{1,4}", x)) >= len(parti) - 1:
        return False   # e.g. sk-hynix-to-build-a-fab-2026
    if s.count("/") > 1:
        return False
    return True


FALSI = re.compile(r"(?i)nascost|hidden|redacted|example|esempio|your[_-]?key|xxxx|placeholder|\$\{|<[a-z_]+>")


def segreti(R):
    valori_env = [v for k, v in os.environ.items() if re.search(r"(_API_KEY|_KEY|_TOKEN|_SECRET)$", k) and len(v) >= 8]
    trovati = []
    for p in glob.glob(os.path.join(DOCS, "**", "*"), recursive=True):
        if os.path.isdir(p) or not re.search(r"\.(json|html?|js|mjs|css|md|txt|svg|xml|csv|geojson|webmanifest)$", p, re.I):
            continue
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except Exception:  # noqa: BLE001
            continue
        rel = os.path.relpath(p, RADICE)
        for v in valori_env:
            if v in t:
                trovati.append((rel, "value of a secret environment variable", v[:4] + "…"))
        for nome, rx in SCHEMI_SEGRETI:
            for m in rx.finditer(t):
                s = m.group(m.lastindex or 0)
                ctx = t[max(0, m.start() - 30): m.end() + 10]
                if FALSI.search(s) or FALSI.search(ctx):
                    continue
                if nome != "private key" and not sembra_chiave(s):
                    continue
                trovati.append((rel, nome, s[:4] + "…" + str(len(s)) + " chars"))
                if len(trovati) > 50:
                    break
    R.segreti = trovati
    if trovati:
        for f, nome, ind in trovati[:30]:
            R.problema("critical", "secrets", f, f"looks like a secret ({nome}): {ind}", "secret")
        R.check("secrets", "API keys and tokens in docs/", "red", f"{len(trovati)} possible secrets found: FAIL")
        print("\n" + "!" * 72 + "\n!!! POSSIBLE SECRETS IN docs/ (published on GitHub Pages):", file=sys.stderr)
        for f, nome, ind in trovati[:30]:
            print(f"!!!   {f}: {nome} {ind}", file=sys.stderr)
        print("!" * 72 + "\n", file=sys.stderr)
    else:
        R.check("secrets", "API keys and tokens in docs/", "green", "nothing that looks like a key or token")


# ----------------------------------------------------------------------------- g) licences
def licenze(R, dati):
    p = os.path.join(RADICE, "DATA_LICENSES.md")
    if not os.path.exists(p):
        R.check("licences", "DATA_LICENSES.md", "red", "file missing")
        R.problema("high", "licences", "DATA_LICENSES.md", "file missing", "licence")
        return
    t = open(p, encoding="utf-8").read()
    citati = {os.path.basename(x) for x in re.findall(r"`([^`]+?\.json)`", t)}
    tutti = sorted({os.path.basename(x) for x in glob.glob(os.path.join(DATI, "*.json"))})
    mancano = [f for f in tutti if f not in citati]
    for f in mancano:
        R.problema("medium" if f != "health.json" else "low", "licences", f"docs/data/{f}", "no row in DATA_LICENSES.md", "licence")
    orfani = sorted(f for f in citati if f not in tutti and not f.startswith("manuali"))
    for f in orfani:
        R.problema("low", "licences", "DATA_LICENSES.md", f"row for {f}, which is not in docs/data (retired?)",
                   "Remove the row or mark the file as retired in DATA_LICENSES.md.")
    R.check("licences", "every data file has a licence row", "amber" if mancano else "green",
            f"{len(tutti) - len(mancano)} of {len(tutti)} files listed; missing: {', '.join(mancano) if mancano else 'none'}"
            + (f"; rows without a file: {', '.join(orfani)}" if orfani else ""))


# ----------------------------------------------------------------------------- h) validators
def esegui_wind(tmp):
    """raccolta/eolico/calendario.py writes docs/data/wind-calendar.json: run it with the output redirected."""
    codice = (
        "import importlib.util, sys, os\n"
        "spec = importlib.util.spec_from_file_location('cal', os.path.join(%r, 'raccolta', 'eolico', 'calendario.py'))\n"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "m.USCITA = %r\n"
        "sys.argv = ['calendario.py', '--rigoroso']\n"
        "m.main()\n" % (RADICE, tmp))
    return [sys.executable, "-c", codice]


def validatori(R):
    tmp = os.path.join(QUI, ".tmp-wind-calendar.json")
    env = dict(os.environ, SENZA_RETE="1", OGGI=OGGI.isoformat(), PYTHONDONTWRITEBYTECODE="1")
    lista = [
        ("originali (fissi, italia, iran, difesa, mobili, eventi, ibrido, linee, condotte)", "raccolta/originali/controlla.py",
         [sys.executable, "raccolta/originali/controlla.py", "--oggi", OGGI.isoformat()]),
        ("simulatore", "raccolta/simulatore/controlla.py", [sys.executable, "raccolta/simulatore/controlla.py"]),
        ("wind calendar --rigoroso (output redirected)", "raccolta/eolico/calendario.py", esegui_wind(tmp)),
        ("stretti-dettaglio --controlla", "raccolta/stretti/raccogli.py", [sys.executable, "raccolta/stretti/raccogli.py", "--controlla"]),
        ("basi-mondo --controlla", "raccolta/basi/raccogli.py", [sys.executable, "raccolta/basi/raccogli.py", "--controlla"]),
        ("assicurazioni --controlla", "raccolta/assicurazioni/raccogli.py", [sys.executable, "raccolta/assicurazioni/raccogli.py", "--controlla"]),
        ("ai-mondo / investimenti --valida", "raccolta/ai/raccogli.py", [sys.executable, "raccolta/ai/raccogli.py", "--valida"]),
        ("italia-impatti --valida", "raccolta/italia/raccogli.py", [sys.executable, "raccolta/italia/raccogli.py", "--valida"]),
        ("supply-chain-ai --valida", "raccolta/supply-chain-ai/raccogli.py", [sys.executable, "raccolta/supply-chain-ai/raccogli.py", "--valida"]),
        ("attacchi-russi --solo-valida", "raccolta/ucraina/attacchi_russi.py", [sys.executable, "raccolta/ucraina/attacchi_russi.py", "--solo-valida"]),
    ]
    falliti = 0
    eseguiti = []
    for nome, script, cmd in lista:
        if not os.path.exists(os.path.join(RADICE, script)):
            continue
        t0 = time.time()
        try:
            r = subprocess.run(cmd, cwd=RADICE, capture_output=True, text=True, timeout=TIMEOUT_VALIDATORE, env=env)
            codice, out = r.returncode, (r.stdout + "\n" + r.stderr).strip()
        except subprocess.TimeoutExpired:
            codice, out = "timeout", f"no answer within {TIMEOUT_VALIDATORE} s"
        except Exception as e:  # noqa: BLE001
            codice, out = "error", str(e)
        righe = [x for x in out.splitlines() if x.strip()]
        sintesi = " | ".join(righe[-3:])[:400]
        # stretti --controlla returns 0 even with errors: read its summary line
        m = re.search(r"Controllo: (\d+) errori", out)
        if codice == 0 and m and int(m.group(1)) > 0:
            codice = "0 (with errors)"
        eseguiti.append({"validator": nome, "script": script, "exit": codice, "seconds": round(time.time() - t0, 1), "tail": sintesi})
        if codice != 0:
            falliti += 1
            err_righe = [x for x in righe if re.search(r"(?i)errore|error|✗|fail|scartat", x)][:6]
            R.problema("high" if codice in ("timeout", "error") or "originali" in nome or "simulatore" in nome else "medium",
                       "validators", script, f"validator '{nome}' exit {codice}: " + (" | ".join(err_righe) or sintesi)[:600], "validator")
    try:
        os.remove(tmp)
    except OSError:
        pass
    R.check("validators", "repository validators", "amber" if falliti else "green",
            f"{len(eseguiti)} run, {falliti} with a non-zero exit: " + "; ".join(f"{v['script'].split('/')[1]} {v['exit']}" for v in eseguiti))
    return eseguiti


# ----------------------------------------------------------------------------- smoke test result
def smoke(R):
    s = leggi(SMOKE)
    if not s:
        R.check("smoke", "browser smoke test", "amber", "raccolta/qualita/smoke.json not found: run node raccolta/qualita/smoke.js")
        return None
    quando = data_da(str(s.get("updated", "")))
    vecchio = quando is None or (OGGI - quando).days > 2
    nf = s.get("failed", [])
    stato = "red" if s.get("overall") == "red" else ("amber" if nf or vecchio else "green")
    R.check("smoke", "browser smoke test", stato,
            f"run {s.get('updated')}: {s.get('passed', 0)} passed, {len(nf)} failed" + ("; result older than 2 days" if vecchio else ""))
    for f in nf[:20]:
        R.problema("high" if "index" in str(f.get("page", "")) else "medium", "smoke", f"docs/{f.get('page', '')}",
                   f"smoke test '{f.get('test')}': {str(f.get('detail', ''))[:300]}", "smoke")
    return s


# ----------------------------------------------------------------------------- outputs
def complessivo(R):
    g = [p["severity"] for p in R.problemi]
    if R.segreti or "critical" in g or g.count("high") >= 3:
        return "red"
    if "high" in g or "medium" in g:
        return "amber"
    return "green"


def scrivi_report(R, overall, eseguiti, durata):
    giorno = OGGI.isoformat()
    percorso = os.path.join(RADICE, "report", "qualita", f"{giorno}.md")
    segno = "<!-- manual notes: kept on rewrite -->"
    manuale = ""
    if os.path.exists(percorso):
        vecchio = open(percorso, encoding="utf-8").read()
        if segno in vecchio:
            manuale = vecchio.split(segno, 1)[1]
    ordine = {k: i for i, k in enumerate(GRAVITA)}
    problemi = sorted(R.problemi, key=lambda p: (ordine.get(p["severity"], 9), p["area"], p["file"]))
    conta_g = {k: sum(1 for p in problemi if p["severity"] == k) for k in GRAVITA}
    L = [f"# Health check, {giorno}", "",
         f"Automatic daily check of the monitor (`raccolta/qualita/controlla_tutto.py`), run {ADESSO.strftime('%Y-%m-%d %H:%M')} UTC in {durata:.0f} s. "
         f"Machine-readable result: [`docs/data/health.json`](../../docs/data/health.json).", "",
         f"**Overall: {overall.upper()}.** Problems: " + ", ".join(f"{conta_g[k]} {k}" for k in GRAVITA) + ".", "",
         "Rule: red if a secret is found, a file does not parse or is missing, or 3+ high-severity problems; amber if any high or medium problem; green otherwise.", "",
         "## Checks", "", "| Area | Check | Status | Detail |", "|---|---|---|---|"]
    for c in R.checks:
        L.append(f"| {c['area']} | {c['name']} | {c['status']} | {c['detail'].replace('|', '/')} |")
    L += ["", "## Problems, most serious first", "",
          "Severity: **critical** = published secret, broken file or missing file; **high** = a collector probably broke or two files disagree on a headline fact; "
          "**medium** = stale curated layer, missing source fields, report figure out of date, confirmed broken link; **low/info** = notes.", ""]
    n = 0
    for k in GRAVITA:
        sel = [p for p in problemi if p["severity"] == k]
        if not sel:
            continue
        L += [f"### {k.capitalize()} ({len(sel)})", ""]
        if k == "info" and len(sel) > 15:
            sel = sel[:15]
        for p in sel:
            n += 1
            L.append(f"{n}. **[{p['area']}] {p['file']}**: {p['problem']}  \n   *Fix:* {p['fix']}")
        L.append("")
    if R.mismatches:
        L += ["## Mismatches (same fact, different values)", "", "| Fact | Values | Note |", "|---|---|---|"]
        for m in R.mismatches:
            vals = "; ".join(f"`{v['file']}` {fmt(v.get('value'))}" + (f" ({v['date']})" if v.get("date") else "") for v in m["values"])
            L.append(f"| {m['fact']} | {vals} | {m.get('note', '')} |")
        L.append("")
    if R.stale:
        L += ["## Stale or missing files", "", "| File | Cadence | Updated | Newest data | Why |", "|---|---|---|---|---|"]
        for s in R.stale:
            L.append(f"| {s['file']} | {s.get('cadence', '')} | {s.get('updated', '')} | {s.get('newest_data_date', '')} | {s.get('why', s.get('status', ''))} |")
        L.append("")
    if R.broken:
        L += ["## Broken links (rolling record)", "", "| URL | Files | Result | Fails in a row |", "|---|---|---|---|"]
        for b in R.broken[:60]:
            L.append(f"| {b['url']} | {', '.join(b['files'])} | {b['code'] or b['detail']} | {b['fails_in_a_row']} |")
        L.append("")
    if eseguiti:
        L += ["## Validators", "", "| Validator | Exit | Seconds | Last lines |", "|---|---|---|---|"]
        for v in eseguiti:
            L.append(f"| `{v['script']}` {v['validator']} | {v['exit']} | {v['seconds']} | {v['tail'].replace('|', '/')[:300]} |")
        L.append("")
    L += ["## Element counts", "", "| File | Elements |", "|---|---|"]
    for f, c in sorted(R.counts.items()):
        L.append(f"| {f} | {c} |")
    L += ["", segno]
    testo = "\n".join(L) + (manuale if manuale else "\n")
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, "w", encoding="utf-8") as f:
        f.write(testo)
    return percorso


def main():
    R = Esito()
    dati = {}
    eseguiti = []
    passi = [
        ("schema", "load", lambda: dati.update(carica_tutti(R) or {})),
        ("freshness", "cadence", lambda: freschezza(R, dati)),
        ("schema", "structure", lambda: schema(R, dati)),
        ("schema", "counts", lambda: confronta_conteggi(R)),
        ("errors", "arrays", lambda: errori(R, dati)),
        ("consistency", "cross-file", lambda: coerenza(R, dati)),
        ("secrets", "scan", lambda: segreti(R)),
        ("licences", "rows", lambda: licenze(R, dati)),
    ]
    for area, nome, fn in passi:
        protetto(R, area, nome)(fn)()
    # links in a background thread while the validators run
    with cf.ThreadPoolExecutor(max_workers=1) as ex:
        fl = ex.submit(protetto(R, "links", "sample")(link_check), R, dati)
        eseguiti = protetto(R, "validators", "run")(validatori)(R) or []
        try:
            fl.result(timeout=BUDGET_LINK_S + 120)
        except Exception as e:  # noqa: BLE001
            R.check("links", "source links", "amber", f"link check did not finish: {e}")
    protetto(R, "smoke", "read")(smoke)(R)
    overall = complessivo(R)
    durata = time.time() - INIZIO
    ordine = {k: i for i, k in enumerate(GRAVITA)}
    salute = {
        "updated": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "date": OGGI.isoformat(),
        "overall": overall,
        "rule": "red: secret found, file unparsable/missing, or 3+ high problems; amber: any high or medium problem; green otherwise",
        "seconds": round(durata, 1),
        "summary": {k: sum(1 for p in R.problemi if p["severity"] == k) for k in GRAVITA},
        "checks": R.checks,
        "problems": sorted(R.problemi, key=lambda p: (ordine.get(p["severity"], 9), p["area"], p["file"])),
        "stale": R.stale,
        "broken_links": R.broken,
        "mismatches": R.mismatches,
        "validators": eseguiti,
        "counts": R.counts,
        "report": f"report/qualita/{OGGI.isoformat()}.md",
        "errors": [],
    }
    try:
        scrivi(USCITA, salute)
    except Exception as e:  # noqa: BLE001
        print("could not write health.json:", e, file=sys.stderr)
    try:
        percorso = scrivi_report(R, overall, eseguiti, durata)
    except Exception as e:  # noqa: BLE001
        percorso = None
        print("could not write the report:", e, file=sys.stderr)
    print(f"Health check {OGGI}: {overall.upper()} in {durata:.0f} s; " + ", ".join(f"{v} {k}" for k, v in salute["summary"].items())
          + f"; report {os.path.relpath(percorso, RADICE) if percorso else '-'}")
    for c in R.checks:
        print(f"  [{c['status']:>5}] {c['area']}: {c['name']}: {c['detail'][:160]}")
    return 2 if R.segreti else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:  # noqa: BLE001 - never crash the workflow
        print("health check failed unexpectedly:", e, file=sys.stderr)
        traceback.print_exc()
        sys.exit(0)
