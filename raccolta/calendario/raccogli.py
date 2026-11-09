#!/usr/bin/env python3
"""Calendario degli eventi che muovono mercati e geopolitica.

Solo libreria standard. Ogni fonte e' indipendente: se una fallisce, l'errore
finisce in "errori" e lo script prosegue. Le voci curate a mano stanno in
voci_manuali.json (stessa cartella).

Variabili d'ambiente facoltative:
  CONTATTO_EMAIL  indirizzo da mettere nello User-Agent (bls.gov rifiuta le
                  richieste automatiche senza un contatto)
  BLS_API_KEY     chiave gratuita BLS API v2 (senza: API v1, limite basso)
  OGGI            data di riferimento AAAA-MM-GG (per test)

Uscita: docs/data/calendario.json
"""
import csv
import datetime as dt
import html
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
USCITA = os.path.join(RADICE, "docs", "data", "calendario.json")
MANUALI = os.path.join(QUI, "voci_manuali.json")

CONTATTO = os.environ.get("CONTATTO_EMAIL", "").strip()
UA = "monitor-geoeconomico/1.0 (ricerca OSINT non commerciale" + ("; " + CONTATTO if CONTATTO else "") + ")"

ADESSO = dt.datetime.now(dt.timezone.utc)
OGGI = dt.date.fromisoformat(os.environ["OGGI"]) if os.environ.get("OGGI") else ADESSO.date()
INIZIO = OGGI - dt.timedelta(days=30)   # eventi passati recenti (con risultato)
FINE = OGGI + dt.timedelta(days=366)    # prossimi 12 mesi

ERRORI = []
FONTI = []
ELEMENTI = []
FONTI_FALLITE = set()

MESI_EN = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], 1)}
MESI_EN.update({k[:3]: v for k, v in list(MESI_EN.items())})
MESI_EN["sept"] = 9


# ---------------------------------------------------------------- utilita'
def scarica(url, timeout=40, binario=False, tentativi=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    for k in range(tentativi):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                dati = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code in (500, 502, 503, 504) and k < tentativi - 1:
                time.sleep(5 * (k + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if k < tentativi - 1:
                time.sleep(5 * (k + 1))
                continue
            raise
    return dati if binario else dati.decode("utf-8", errors="replace")


def testo(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S | re.I)
    h = html.unescape(re.sub(r"<[^>]+>", " ", h))
    return re.sub(r"\s+", " ", h).strip()


def errore(fonte, e):
    FONTI_FALLITE.add(fonte)
    ERRORI.append({"fonte": fonte, "errore": str(e)[:300], "quando": ADESSO.strftime("%Y-%m-%dT%H:%MZ")})
    print("ERRORE", fonte, e, file=sys.stderr)


def fonte(nome, link, licenza, data_dato=None):
    FONTI.append({"nome": nome, "link": link, "licenza": licenza,
                  "data_dato": data_dato or OGGI.isoformat()})


def ultima_domenica(anno, mese):
    d = dt.date(anno, mese + 1, 1) - dt.timedelta(days=1) if mese < 12 else dt.date(anno, 12, 31)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)


def nesima_domenica(anno, mese, n):
    d = dt.date(anno, mese, 1)
    d += dt.timedelta(days=(6 - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def utc_da_locale(giorno, ora, minuto, zona):
    """Converte un orario locale in UTC. zona: 'ET' (USA est), 'UK', 'CET'."""
    if zona == "ET":
        estate = nesima_domenica(giorno.year, 3, 2) <= giorno < nesima_domenica(giorno.year, 11, 1)
        off = -4 if estate else -5
    elif zona == "UK":
        estate = ultima_domenica(giorno.year, 3) <= giorno < ultima_domenica(giorno.year, 10)
        off = 1 if estate else 0
    elif zona == "CET":
        estate = ultima_domenica(giorno.year, 3) <= giorno < ultima_domenica(giorno.year, 10)
        off = 2 if estate else 1
    else:
        raise ValueError(zona)
    t = dt.datetime(giorno.year, giorno.month, giorno.day, ora, minuto) - dt.timedelta(hours=off)
    return t.date(), t.strftime("%H:%M")


def nella_finestra(giorno):
    return INIZIO <= giorno <= FINE


def aggiungi(data, categoria, paese, titolo, importanza, fonte_nome, link, ora_utc=None,
             valore_precedente=None, valore_atteso=None, valore_uscito=None, note="",
             affidabilita="alta", data_fonte=None, origine="auto", data_fine=None):
    d = data if isinstance(data, str) else data.isoformat()
    ELEMENTI.append({
        "data": d, "data_fine": data_fine, "ora_utc": ora_utc, "paese": paese, "categoria": categoria,
        "titolo": titolo, "importanza": importanza,
        "valore_precedente": valore_precedente, "valore_atteso": valore_atteso, "valore_uscito": valore_uscito,
        "fonte": fonte_nome, "link": link, "data_fonte": data_fonte or OGGI.isoformat(),
        "affidabilita": affidabilita, "note": note, "origine": origine,
    })


def leggi_ics(t):
    t = t.replace("\r\n", "\n").replace("\n ", "").replace("\n\t", "")
    eventi = []
    for blocco in t.split("BEGIN:VEVENT")[1:]:
        m = re.search(r"^DTSTART([^:\n]*):(\d{8})(T(\d{2})(\d{2})\d{0,2}(Z?))?", blocco, re.M)
        s = re.search(r"^SUMMARY[^:\n]*:(.*)$", blocco, re.M)
        if not m or not s:
            continue
        giorno = dt.datetime.strptime(m.group(2), "%Y%m%d").date()
        ora = (int(m.group(4)), int(m.group(5))) if m.group(3) else None
        eventi.append({"giorno": giorno, "ora": ora, "utc": bool(m.group(6)), "tz": m.group(1),
                       "titolo": s.group(1).replace("\\,", ",").replace("\\;", ";").strip()})
    return eventi


# ---------------------------------------------------------------- Fed
MESI_IT = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
           "settembre", "ottobre", "novembre", "dicembre"]


def mese_it(s):
    """'SEPTEMBER 2026' o 'August: ...' -> nomi dei mesi in italiano."""
    def sost(m):
        n = MESI_EN.get(m.group(0).lower())
        return MESI_IT[n - 1] if n else m.group(0)
    return re.sub(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b", sost, s, flags=re.I)


def frazione(s):
    s = s.strip()
    m = re.match(r"(\d+)(?:-(\d)/(\d))?$", s)
    if not m:
        return s
    v = int(m.group(1)) + (int(m.group(2)) / int(m.group(3)) if m.group(2) else 0)
    return ("%.2f" % v).replace(".", ",")


def fed():
    url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    try:
        t = testo(scarica(url))
        ultima = None
        try:
            rss = scarica("https://www.federalreserve.gov/feeds/press_monetary.xml")
            for it in re.findall(r"<item>(.*?)</item>", rss, re.S):
                tit = re.search(r"<title>(.*?)</title>", it, re.S).group(1)
                if "FOMC statement" in tit:
                    link = re.search(r"<link>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>", it, re.S).group(1).strip()
                    st = testo(scarica(link))
                    m = re.search(r"decided to (maintain|raise|lower) the target range for the federal funds rate (?:by [^ ]+ percentage point )?(?:to|at) ([\d\-/]+) to ([\d\-/]+) percent", st)
                    v = re.search(r"by a (\d+)\s*[–-]\s*(\d+) vote", st)
                    contro = re.search(r"Voting against the monetary policy action were (.*?)\.", st)
                    dm = re.search(r"monetary(\d{8})", link)
                    if m and dm:
                        azione = {"maintain": "invariato", "raise": "rialzo", "lower": "taglio"}[m.group(1)]
                        ultima = {"data": dt.datetime.strptime(dm.group(1), "%Y%m%d").date(),
                                  "testo": "Tassi fed funds %s: %s-%s%%%s%s" % (
                                      azione, frazione(m.group(2)), frazione(m.group(3)),
                                      " (voto %s-%s)" % v.groups() if v else "",
                                      "; contrari: " + contro.group(1) if contro else ""),
                                  "intervallo": "%s-%s%%" % (frazione(m.group(2)), frazione(m.group(3))),
                                  "link": link}
                    break
        except Exception as e:  # noqa
            errore("Fed RSS/comunicato", e)
        n = 0
        for anno_m in re.finditer(r"(\d{4}) FOMC Meetings", t):
            anno = int(anno_m.group(1))
            if anno < OGGI.year - 1:
                continue
            fine_sez = t.find("FOMC Meetings", anno_m.end())
            sez = t[anno_m.end(): fine_sez if fine_sez > 0 else len(t)]
            for m in re.finditer(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)(?:/(\w+))? (\d{1,2})-(\d{1,2})(\*?)", sez):
                mese = MESI_EN[(m.group(2) or m.group(1)).lower()]
                giorno = dt.date(anno, mese, int(m.group(4)))
                if not nella_finestra(giorno):
                    continue
                d_utc, ora = utc_da_locale(giorno, 14, 0, "ET")
                sep = " con proiezioni economiche (SEP)" if m.group(5) else ""
                tit = "Fed: decisione FOMC (riunione %s %s-%s)%s" % (m.group(1), m.group(3), m.group(4), sep)
                passato = giorno <= OGGI
                aggiungi(d_utc, "banca-centrale", "US", tit, "alta", "Federal Reserve, calendario FOMC", url,
                         ora_utc=ora,
                         valore_precedente=None if passato else (ultima and ultima["intervallo"]),
                         valore_uscito=ultima["testo"] if (ultima and ultima["data"] == giorno) else None,
                         note="Tasso attuale %s (ultima decisione %s)." % (ultima["intervallo"], ultima["data"].isoformat()) if ultima else "")
                n += 1
        if ultima and not nella_finestra(ultima["data"]):
            aggiungi(ultima["data"], "banca-centrale", "US", "Fed: ultima decisione FOMC", "alta",
                     "Federal Reserve, comunicato FOMC", ultima["link"], valore_uscito=ultima["testo"])
        fonte("Federal Reserve - FOMC calendar e comunicati", url, "Pubblico dominio (governo USA)")
        print("Fed:", n, "riunioni")
    except Exception as e:
        errore("Fed calendario FOMC", e)


# ---------------------------------------------------------------- BCE
def bce():
    url = "https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html"
    tassi = {}
    try:
        for cod, nome in (("DFR", "deposito"), ("MRR_FR", "rifinanziamento principale"), ("MLFR", "rifinanziamento marginale")):
            c = scarica("https://data-api.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.%s.LEV?lastNObservations=2&format=csvdata" % cod)
            righe = list(csv.DictReader(io.StringIO(c)))
            if righe:
                tassi[nome] = (righe[-1]["TIME_PERIOD"], righe[-1]["OBS_VALUE"],
                               righe[-2]["OBS_VALUE"] if len(righe) > 1 else None)
        fonte("BCE Data Portal - tassi ufficiali (FM.B.U2.EUR.4F.KR.*)", "https://data.ecb.europa.eu/", "Riuso libero con citazione della fonte (BCE)")
    except Exception as e:
        errore("BCE tassi (data-api)", e)
    ultima = None
    try:
        rss = scarica("https://www.ecb.europa.eu/rss/press.html")
        for it in re.findall(r"<item>(.*?)</item>", rss, re.S):
            tit = html.unescape(re.search(r"<title>(.*?)</title>", it, re.S).group(1)).strip()
            if tit.startswith("Monetary policy decisions"):
                link = re.search(r"<link>(.*?)</link>", it, re.S).group(1).strip().replace("europa.eu//", "europa.eu/")
                st = testo(scarica(link))
                m = re.search(r"decided to (keep|raise|lower|cut)[^.]*?(unchanged|by [\d.]+ percentage points?|by \d+ basis points)?", st)
                dm = re.search(r"\.mp(\d{6})", link)
                if m and dm:
                    giorno = dt.datetime.strptime(dm.group(1), "%y%m%d").date()
                    azione = {"keep": "tassi invariati", "raise": "rialzo", "lower": "taglio", "cut": "taglio"}[m.group(1)]
                    ultima = {"data": giorno, "azione": azione, "link": link}
                break
    except Exception as e:
        errore("BCE RSS/comunicato", e)
    dfr = tassi.get("deposito")
    stato_tassi = ("deposito %s%%, rifinanziamento principale %s%%, marginale %s%% (in vigore dal %s)" % (
        dfr[1], tassi.get("rifinanziamento principale", ("", "?"))[1], tassi.get("rifinanziamento marginale", ("", "?"))[1], dfr[0])
    ).replace(".", ",") if dfr else None
    try:
        t = testo(scarica(url))
        n = 0
        visti = set()
        for m in re.finditer(r"(\d{2})/(\d{2})/(\d{4}) Governing Council of the ECB: monetary policy meeting[^0-9]*?(\(Day 2\), followed by press conference|followed by press conference|\(Day 1\))?", t):
            if m.group(4) and "Day 1" in m.group(4):
                continue
            giorno = dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            if giorno in visti or not nella_finestra(giorno):
                continue
            visti.add(giorno)
            d_utc, ora = utc_da_locale(giorno, 14, 15, "CET")
            passato = giorno <= OGGI
            uscito = None
            if ultima and ultima["data"] == giorno:
                uscito = "%s; %s" % (ultima["azione"], stato_tassi or "")
            aggiungi(d_utc, "banca-centrale", "EU", "BCE: decisione di politica monetaria (con conferenza stampa)", "alta",
                     "BCE, calendario riunioni del Consiglio direttivo", url, ora_utc=ora,
                     valore_precedente=None if passato else stato_tassi, valore_uscito=uscito,
                     note="Comunicato alle 14:15 ora di Francoforte, conferenza alle 14:45.")
            n += 1
        if ultima and ultima["data"] not in visti:
            d_utc, ora = utc_da_locale(ultima["data"], 14, 15, "CET")
            aggiungi(d_utc, "banca-centrale", "EU", "BCE: decisione di politica monetaria (ultima)", "alta",
                     "BCE, comunicato", ultima["link"], ora_utc=ora,
                     valore_uscito="%s; %s" % (ultima["azione"], stato_tassi or "livelli dei tassi non letti"))
        fonte("BCE - calendario riunioni e comunicati", url, "Riuso libero con citazione della fonte (BCE)")
        print("BCE:", n, "riunioni")
    except Exception as e:
        errore("BCE calendario", e)


# ---------------------------------------------------------------- BoJ
def boj():
    url = "https://www.boj.or.jp/en/mopo/mpmsche_minu/index.htm"
    try:
        h = scarica(url)
        anni = [int(a) for a in re.findall(r"<caption[^>]*>\s*Table\s*:\s*(\d{4})", h)] or [OGGI.year, OGGI.year + 1]
        tabelle = re.findall(r"<table.*?</table>", h, re.S)
        n = 0
        for anno, tab in zip(anni, tabelle):
            for tr in re.findall(r"<tr.*?</tr>", tab, re.S):
                celle = [testo(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
                if not celle:
                    continue
                m = re.match(r"([A-Za-z]+)\.? (\d{1,2}) \(\w+\.?\), (?:([A-Za-z]+)\.? )?(\d{1,2})", celle[0])
                if not m:
                    continue
                mese = MESI_EN.get((m.group(3) or m.group(1)).lower().rstrip("."))
                if not mese:
                    continue
                giorno = dt.date(anno, mese, int(m.group(4)))
                if not nella_finestra(giorno):
                    continue
                outlook = len(celle) > 1 and celle[1] not in ("-", "")
                aggiungi(giorno, "banca-centrale", "JP",
                         "Bank of Japan: decisione di politica monetaria%s" % (" e Outlook Report" if outlook else ""),
                         "alta", "Bank of Japan, calendario riunioni (MPM)", url,
                         note="Orario non fisso (di solito a fine mattinata ora di Tokyo, notte in Europa). Il tasso attuale e' nelle voci manuali.")
                n += 1
        fonte("Bank of Japan - calendario MPM", url, "Riuso consentito con citazione (termini del sito BoJ)")
        print("BoJ:", n, "riunioni")
    except Exception as e:
        errore("BoJ calendario", e)


# ---------------------------------------------------------------- BoE
def boe():
    url = "https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates"
    url_tasso = "https://www.bankofengland.co.uk/monetary-policy/the-interest-rate-bank-rate"
    tasso = ultima = None
    try:
        t = testo(scarica(url_tasso))
        m = re.search(r"Current Bank Rate ([\d.]+)%", t)
        tasso = m.group(1).replace(".", ",") + "%" if m else None
        m2 = re.search(r"Our latest decision: (.*?) (?:Energy|Inflation|We|The)\b.*?Published on (\d{1,2} \w+ \d{4})", t)
        if m2:
            ultima = (dt.datetime.strptime(m2.group(2), "%d %B %Y").date(), m2.group(1))
        fonte("Bank of England - Bank Rate", url_tasso, "Open Government Licence / termini BoE (riuso con citazione)")
    except Exception as e:
        errore("BoE Bank Rate", e)
    try:
        h = scarica(url)
        anni = [int(a) for a in re.findall(r"(\d{4}) confirmed dates", testo(h))]
        tabelle = re.findall(r"<table.*?</table>", h, re.S)
        n = 0
        for anno, tab in zip(anni, tabelle):
            for m in re.finditer(r"(Monday|Tuesday|Wednesday|Thursday|Friday) (\d{1,2}) (\w+)", testo(tab)):
                mese = MESI_EN.get(m.group(3).lower())
                if not mese:
                    continue
                giorno = dt.date(anno, mese, int(m.group(2)))
                if not nella_finestra(giorno):
                    continue
                d_utc, ora = utc_da_locale(giorno, 12, 0, "UK")
                passato = giorno <= OGGI
                uscito = None
                if ultima and ultima[0] == giorno:
                    uscito = re.sub(r"Bank Rate (raised|cut|reduced|maintained|held) (?:to|at) ([\d.]+)%",
                                    lambda x: "Bank Rate %s al %s%%" % ({"raised": "alzato", "cut": "tagliato", "reduced": "tagliato"}.get(x.group(1), "invariato"), x.group(2).replace(".", ",")),
                                    ultima[1])
                aggiungi(d_utc, "banca-centrale", "GB", "Bank of England: decisione MPC sul Bank Rate", "alta",
                         "Bank of England, date MPC", url, ora_utc=ora,
                         valore_precedente=None if passato else ("Bank Rate " + tasso if tasso else None),
                         valore_uscito=uscito)
                n += 1
        fonte("Bank of England - date MPC", url, "Open Government Licence / termini BoE (riuso con citazione)")
        print("BoE:", n, "riunioni")
    except Exception as e:
        errore("BoE calendario", e)


# ---------------------------------------------------------------- BLS
BLS_SERIE = {
    "Consumer Price Index": ("USA: Consumer Price Index (CPI)", "alta", "cpi"),
    "Employment Situation": ("USA: Employment Situation (occupazione)", "alta", "empsit"),
    "Producer Price Index": ("USA: Producer Price Index (PPI)", "media", "ppi"),
    "Job Openings and Labor Turnover Survey": ("USA: JOLTS (posti vacanti)", "bassa", "jolts"),
    "Employment Cost Index": ("USA: Employment Cost Index", "media", "eci"),
}


def bls_ultimi():
    """Ultimi valori da comunicato BLS (testo). Ritorna {codice: (data_uscita, periodo, testo, precedente)}."""
    out = {}
    try:
        t = testo(scarica("https://www.bls.gov/news.release/cpi.nr0.htm"))
        d = re.search(r"embargoed until [\d:apm. ]*\(ET\) \w+, (\w+ \d{1,2}, \d{4})", t)
        p = re.search(r"CONSUMER PRICE INDEX - (\w+ \d{4})", t)
        m = re.search(r"CPI-U\) (increased|decreased|rose|fell|was unchanged)( [\d.]+ percent)? on a seasonally adjusted basis in \w+ after (rising|falling|increasing|decreasing|being unchanged)( [\d.]+ percent)? in (\w+)", t)
        a = re.search(r"Over the last 12 months, the all items index (increased|decreased|rose|fell) ([\d.]+) percent", t)
        c = re.search(r"all items less food and energy (rose|fell|increased|decreased|was unchanged)( [\d.]+ percent)?", t)
        if d and m:
            segno = "-" if m.group(1) in ("decreased", "fell") else "+"
            val = "%s%s%% m/m (dest.)" % (segno, (m.group(2) or " 0").strip().split()[0])
            if a:
                val += ", %s%s%% a/a" % ("-" if a.group(1) in ("decreased", "fell") else "+", a.group(2))
            if c:
                val += "; core %s%s%% m/m" % ("-" if c.group(1) in ("fell", "decreased") else "+", (c.group(2) or " 0").strip().split()[0])
            prec = "%s: %s%s%% m/m" % (m.group(5), "-" if m.group(3) in ("falling", "decreasing") else "+", (m.group(4) or " 0").strip().split()[0])
            out["cpi"] = (dt.datetime.strptime(d.group(1), "%B %d, %Y").date(), mese_it(p.group(1)) if p else "",
                          val.replace(".", ","), mese_it(prec).replace(".", ","))
    except Exception as e:
        errore("BLS comunicato CPI", e)
    try:
        t = testo(scarica("https://www.bls.gov/news.release/empsit.nr0.htm"))
        d = re.search(r"\(ET\) \w+, (\w+ \d{1,2}, \d{4})", t)
        p = re.search(r"THE EMPLOYMENT SITUATION - (\w+ \d{4})", t)
        m = re.search(r"Total nonfarm payroll employment (rose|increased|fell|declined|decreased|changed little)(?: by)? ?([\d,]+)?", t)
        u = re.search(r"unemployment rate (?:changed little|was unchanged|rose|fell|increased|decreased|edged \w+)(?: \w+)? (?:at|to) ([\d.]+) percent", t)
        if d and m:
            segno = "-" if m.group(1) in ("fell", "declined", "decreased") else "+"
            val = "Occupati non agricoli %s%s" % (segno, (m.group(2) or "n.d.").replace(",", "."))
            if u:
                val += "; disoccupazione %s%%" % u.group(1).replace(".", ",")
            out["empsit"] = (dt.datetime.strptime(d.group(1), "%B %d, %Y").date(), mese_it(p.group(1)) if p else "", val, None)
    except Exception as e:
        errore("BLS comunicato occupazione", e)
    return out


def bls_api_check():
    """Prova l'API BLS (v2 con chiave, altrimenti v1) solo per registrare se funziona."""
    chiave = os.environ.get("BLS_API_KEY")
    url = "https://api.bls.gov/publicAPI/%s/timeseries/data/" % ("v2" if chiave else "v1")
    corpo = {"seriesid": ["CUUR0000SA0", "LNS14000000", "CES0000000001"],
             "startyear": str(OGGI.year - 1), "endyear": str(OGGI.year)}
    if chiave:
        corpo["registrationkey"] = chiave
    try:
        req = urllib.request.Request(url, data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json", "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as r:
            j = json.loads(r.read().decode())
        if j.get("status") != "REQUEST_SUCCEEDED":
            raise RuntimeError("; ".join(j.get("message", []))[:200])
        res = {}
        for s in j["Results"]["series"]:
            if s["data"]:
                x = s["data"][0]
                res[s["seriesID"]] = (x["year"], x["periodName"], x["value"])
        return res
    except Exception as e:
        errore("BLS API " + ("v2" if chiave else "v1"), e)
        return {}


def bls():
    url = "https://www.bls.gov/schedule/news_release/bls.ics"
    try:
        ev = leggi_ics(scarica(url))
    except Exception as e:
        errore("bls", "calendario ICS non raggiungibile (%s). Serve CONTATTO_EMAIL nello User-Agent? Uso le voci di riserva." % e)
        return
    api = bls_api_check()
    ultimi = bls_ultimi()
    n = 0
    prossimo_visto = set()
    for e in sorted(ev, key=lambda x: x["giorno"]):
        info = BLS_SERIE.get(e["titolo"])
        if not info or not nella_finestra(e["giorno"]):
            continue
        tit, imp, cod = info
        d_utc, ora = (utc_da_locale(e["giorno"], e["ora"][0], e["ora"][1], "ET") if e["ora"] else (e["giorno"], None))
        uscito = prec = None
        if cod in ultimi and ultimi[cod][0] == e["giorno"]:
            uscito = ultimi[cod][2]
            prec = ultimi[cod][3]
            tit2 = "%s, %s" % (tit, ultimi[cod][1])
        else:
            tit2 = tit
            if e["giorno"] > OGGI and cod in ultimi and cod not in prossimo_visto:
                prec = "%s: %s" % (ultimi[cod][1], ultimi[cod][2])
                prossimo_visto.add(cod)
        aggiungi(d_utc, "dato-macro", "US", tit2, imp, "BLS, calendario comunicati", "https://www.bls.gov/schedule/news_release/%s.htm" % cod,
                 ora_utc=ora, valore_precedente=prec, valore_uscito=uscito)
        n += 1
    nota_api = (" API: " + ", ".join("%s %s %s=%s" % (k, v[1], v[0], v[2]) for k, v in api.items())) if api else ""
    fonte("BLS - calendario ICS e comunicati (CPI, occupazione)" + nota_api, url, "Pubblico dominio (governo USA)")
    print("BLS:", n, "uscite")


# ---------------------------------------------------------------- BEA
def bea_ultimi():
    out = {}
    try:
        t = testo(scarica("https://www.bea.gov/data/gdp/gross-domestic-product"))
        m = re.search(r"Current release: (\w+ \d{1,2}, \d{4})", t)
        g = re.search(r"(Real gross domestic product \(GDP\) (?:increased|decreased) at an annual rate of [\d.]+ percent in the (\w+) quarter of (\d{4}))", t)
        q = re.search(r"(?:increased|decreased) at an annual rate of ([\d.]+) percent", t)
        s = re.search(r"\((Advance|Second|Third) Estimate\)", t)
        if m and q:
            neg = "decreased at an annual rate" in (g.group(1) if g else "")
            out["gdp"] = (dt.datetime.strptime(m.group(1), "%B %d, %Y").date(),
                          "PIL reale %s%s%% annualizzato (%s, stima %s)" % ("-" if neg else "+", q.group(1).replace(".", ","),
                                                                           ("%s trimestre %s" % (g.group(2), g.group(3))) if g else "",
                                                                           s.group(1).lower() if s else ""))
    except Exception as e:
        errore("BEA PIL", e)
    try:
        h = scarica("https://www.bea.gov/data/income-saving/personal-income")
        lk = re.search(r'href="(/news/\d{4}/personal-income-and-outlays-[^"]+)"', h)
        t0 = testo(h)
        m = re.search(r"Current release: (\w+ \d{1,2}, \d{4})", t0)
        if lk and m:
            t = testo(scarica("https://www.bea.gov" + lk.group(1)))
            a = re.search(r"From the same month one year ago, the PCE price index for \w+ increased ([\d.]+) percent\s*\. Excluding food and energy, the PCE price index increased ([\d.]+) percent", t)
            b = re.search(r"From the preceding month, the PCE price index for \w+ increased ([\d.]+) percent\s*\. Excluding food and energy, the PCE price index increased ([\d.]+) percent", t)
            if a:
                v = "Deflatore PCE +%s%% a/a, core +%s%% a/a" % (a.group(1), a.group(2))
                if b:
                    v += " (m/m +%s%%, core +%s%%)" % (b.group(1), b.group(2))
                out["pio"] = (dt.datetime.strptime(m.group(1), "%B %d, %Y").date(), v.replace(".", ","))
    except Exception as e:
        errore("BEA PCE", e)
    return out


def bea():
    url = "https://www.bea.gov/news/schedule/ics/online-calendar-subscription.ics"
    try:
        ev = leggi_ics(scarica(url))
        ultimi = bea_ultimi()
        n = 0
        visti_prossimi = set()
        for e in sorted(ev, key=lambda x: x["giorno"]):
            tl = e["titolo"]
            if tl.startswith("GDP (") or tl.startswith("GDP,"):
                cod, imp, tit = "gdp", "alta", "USA: PIL - " + tl
            elif tl.startswith("Personal Income and Outlays"):
                cod, imp, tit = "pio", "alta", "USA: redditi e spese personali, deflatore PCE - " + tl.replace("Personal Income and Outlays, ", "")
            else:
                continue
            if not e["ora"]:
                giorno, ora = e["giorno"], None
            elif e["utc"]:
                giorno, ora = e["giorno"], "%02d:%02d" % e["ora"]
            else:
                giorno, ora = utc_da_locale(e["giorno"], e["ora"][0], e["ora"][1], "ET")
            if not nella_finestra(giorno):
                continue
            uscito = prec = None
            if cod in ultimi and ultimi[cod][0] == giorno:
                uscito = ultimi[cod][1]
            elif giorno > OGGI and cod in ultimi and cod not in visti_prossimi:
                prec = ultimi[cod][1]
                visti_prossimi.add(cod)
            aggiungi(giorno, "dato-macro", "US", tit, imp, "BEA, calendario comunicati", "https://www.bea.gov/news/schedule",
                     ora_utc=ora, valore_precedente=prec, valore_uscito=uscito)
            n += 1
        fonte("BEA - calendario ICS e pagine dati (PIL, PCE)", url, "Pubblico dominio (governo USA)")
        print("BEA:", n, "uscite")
    except Exception as e:
        errore("BEA calendario", e)


# ---------------------------------------------------------------- Eurostat
def eurostat():
    url = "https://ec.europa.eu/eurostat/o/calendars/eventsIcal?theme=0&category=0"
    ultimo = None
    try:
        j = json.loads(scarica("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/teicp000?geo=EA&unit=PCH_M12&lastTimePeriod=3"))
        idx = j["dimension"]["time"]["category"]["index"]
        per = sorted(idx, key=idx.get)
        vals = {p: j["value"].get(str(idx[p])) for p in per}
        flag = j.get("status", {})
        ult = per[-1]
        ultimo = {"periodo": ult, "valore": vals[ult], "stima": flag.get(str(idx[ult])) == "e",
                  "prec": (per[-2], vals[per[-2]]) if len(per) > 1 else None,
                  "agg": j.get("updated", "")[:10]}
        fonte("Eurostat - HICP area euro, tasso annuo (teicp000, EA)", "https://ec.europa.eu/eurostat/databrowser/view/teicp000/default/table", "CC BY 4.0 (Eurostat)", ultimo["agg"])
    except Exception as e:
        errore("Eurostat HICP", e)
    try:
        ev = leggi_ics(scarica(url, timeout=60))
        n = 0
        visto_prossimo = False
        for e in sorted(ev, key=lambda x: x["giorno"]):
            tl = e["titolo"]
            if tl == "Flash estimate inflation euro area":
                tit, imp = "Eurozona: inflazione HICP, stima flash", "alta"
            elif tl == "Inflation (HICP)":
                tit, imp = "Eurozona/UE: inflazione HICP, dato definitivo", "media"
            elif tl.startswith("Flash estimate GDP"):
                tit, imp = "Eurozona/UE: PIL e occupazione, stima flash", "media"
            elif tl == "Unemployment":
                tit, imp = "Eurozona/UE: disoccupazione", "bassa"
            else:
                continue
            if not nella_finestra(e["giorno"]):
                continue
            d_utc, ora = utc_da_locale(e["giorno"], 11, 0, "CET")
            uscito = prec = None
            if ultimo and "Flash estimate inflation" in tl:
                if ultimo["agg"] == e["giorno"].isoformat():
                    uscito = "%s: %s%% a/a%s" % (ultimo["periodo"], str(ultimo["valore"]).replace(".", ","), " (stima flash)" if ultimo["stima"] else "")
                    if ultimo["prec"]:
                        prec = "%s: %s%%" % (ultimo["prec"][0], str(ultimo["prec"][1]).replace(".", ","))
                elif e["giorno"] > OGGI and not visto_prossimo:
                    prec = "%s: %s%% a/a%s" % (ultimo["periodo"], str(ultimo["valore"]).replace(".", ","), " (stima flash)" if ultimo["stima"] else "")
                    visto_prossimo = True
            aggiungi(d_utc, "dato-macro", "EU", tit, imp, "Eurostat, calendario delle uscite",
                     "https://ec.europa.eu/eurostat/news/release-calendar", ora_utc=ora,
                     valore_precedente=prec, valore_uscito=uscito, note="Ora: di norma 11:00 di Lussemburgo.")
            n += 1
        fonte("Eurostat - calendario uscite (iCal)", url, "CC BY 4.0 (Eurostat)")
        print("Eurostat:", n, "uscite")
    except Exception as e:
        errore("Eurostat calendario", e)


# ---------------------------------------------------------------- EIA
def eia():
    # STEO: prossima uscita dalla pagina + regola (primo martedi' dopo il primo giovedi' del mese)
    url = "https://www.eia.gov/outlooks/steo/"
    try:
        t = testo(scarica(url))
        m = re.search(r"Release Date: (\w+ \d{1,2}, \d{4}).*?Next Release Date: (\w+ \d{1,2}, \d{4})", t)
        rilasciata = dt.datetime.strptime(m.group(1), "%B %d, %Y").date() if m else None
        prossima = dt.datetime.strptime(m.group(2), "%B %d, %Y").date() if m else None
        date = set()
        if prossima:
            date.add((prossima, "ufficiale"))
        if rilasciata and nella_finestra(rilasciata):
            date.add((rilasciata, "ufficiale"))
        for k in range(1, 13):
            a, me = (OGGI.year + (OGGI.month - 1 + k) // 12, (OGGI.month - 1 + k) % 12 + 1)
            g = dt.date(a, me, 1)
            g += dt.timedelta(days=(3 - g.weekday()) % 7)   # primo giovedi'
            g += dt.timedelta(days=5)                       # martedi' successivo
            if prossima and g.year == prossima.year and g.month == prossima.month:
                continue
            if nella_finestra(g) and (not prossima or g > prossima):
                date.add((g, "stimata con la regola EIA"))
        for g, tipo in sorted(date):
            d_utc, ora = utc_da_locale(g, 12, 0, "ET")
            aggiungi(d_utc, "energia", "US", "EIA: Short-Term Energy Outlook (STEO)", "media", "EIA, STEO", url, ora_utc=ora,
                     note="Data %s. Ora indicativa (mezzogiorno ET)." % tipo, affidabilita="alta" if tipo == "ufficiale" else "media")
        fonte("EIA - Short-Term Energy Outlook", url, "Pubblico dominio (governo USA)")
    except Exception as e:
        errore("EIA STEO", e)
    # Settimanale petrolio (WPSR): mercoledi' 10:30 ET, eccezioni per festivi dalla tabella ufficiale
    url_s = "https://www.eia.gov/petroleum/supply/weekly/schedule.php"
    try:
        eccezioni = {}
        t = testo(scarica(url_s))
        for m in re.finditer(r"(\w+ \d{1,2}, \d{4}) (\w+ \d{1,2}, \d{4}) (\w+day) (\d{1,2}:\d{2}) ([ap])\.m\.", t):
            try:
                normale = dt.datetime.strptime(m.group(1), "%B %d, %Y").date()
                nuova = dt.datetime.strptime(m.group(2), "%B %d, %Y").date()
            except ValueError:
                continue
            hh, mm = map(int, m.group(4).split(":"))
            if m.group(5) == "p" and hh != 12:
                hh += 12
            eccezioni[nuova] = (hh, mm)
        ultimo = None
        try:
            righe = list(csv.reader(io.StringIO(scarica("https://ir.eia.gov/wpsr/table1.csv"))))
            intest = righe[0]
            for r in righe[1:]:
                if r and r[0].startswith("Commercial (Excluding SPR)"):
                    sett = dt.datetime.strptime(intest[1], "%m/%d/%y").date()
                    ultimo = (sett, "Scorte commerciali greggio USA %s Mb (%s%s Mb sulla settimana) al %s" % (
                        r[1].replace(".", ","), "+" if not r[3].startswith("-") else "", r[3].replace(".", ","), sett.isoformat()))
            fonte("EIA - Weekly Petroleum Status Report, tabella 1", "https://ir.eia.gov/wpsr/table1.csv", "Pubblico dominio (governo USA)")
        except Exception as e:
            errore("EIA WPSR tabella 1", e)
        g = OGGI - dt.timedelta(days=(OGGI.weekday() - 2) % 7) - dt.timedelta(days=7)
        fine = OGGI + dt.timedelta(days=42)  # solo sei settimane: e' un evento ricorrente
        rilascio_ultimo = None
        if ultimo:
            # l'uscita e' il mercoledi' (o giorno di eccezione) dopo il venerdi' di riferimento
            rilascio_ultimo = ultimo[0] + dt.timedelta(days=5)
        prec_messo = False
        while g <= fine:
            giorno, hhmm = g, (10, 30)
            for nuova, oh in eccezioni.items():
                if 0 < (nuova - g).days <= 2:
                    giorno, hhmm = nuova, oh
            d_utc, ora = utc_da_locale(giorno, hhmm[0], hhmm[1], "ET")
            uscito = prec = None
            if ultimo and rilascio_ultimo and abs((giorno - rilascio_ultimo).days) <= 2:
                uscito = ultimo[1]
            elif ultimo and giorno > OGGI and not prec_messo:
                prec = ultimo[1]
                prec_messo = True
            aggiungi(d_utc, "energia", "US", "EIA: rapporto settimanale sul petrolio (WPSR), scorte USA", "media",
                     "EIA, calendario WPSR", url_s, ora_utc=ora, valore_precedente=prec, valore_uscito=uscito,
                     note="Spostato per festivita'." if giorno != g else "")
            g += dt.timedelta(days=7)
        fonte("EIA - calendario WPSR", url_s, "Pubblico dominio (governo USA)")
        print("EIA: ok")
    except Exception as e:
        errore("EIA WPSR calendario", e)


# ---------------------------------------------------------------- elezioni
PAESI = {
    "Cabo Verde": "CV", "Switzerland": "CH", "Spain": "ES", "Gambia, The": "GM", "Northern Cyprus": "CY",
    "Fiji": "FJ", "South Sudan": "SS", "Somalia": "SO", "Nigeria": "NG", "Kyrgyzstan": "KG", "El Salvador": "SV",
    "Micronesia, Federated States of": "FM", "Estonia": "EE", "France": "FR", "Finland": "FI", "Haiti": "HT",
    "United States of America": "US", "Germany": "DE", "Italy": "IT", "Japan": "JP", "United Kingdom": "GB",
    "Poland": "PL", "Greece": "GR", "Mexico": "MX", "Kenya": "KE", "Argentina": "AR", "Slovakia": "SK",
    "Brazil": "BR", "India": "IN", "Turkey": "TR", "Türkiye": "TR", "Israel": "IL", "Iran": "IR", "Iraq": "IQ",
    "Russia": "RU", "Ukraine": "UA", "Taiwan": "TW", "Korea, Republic of": "KR", "South Korea": "KR",
    "Netherlands": "NL", "Belgium": "BE", "Austria": "AT", "Czech Republic": "CZ", "Hungary": "HU",
    "Romania": "RO", "Bulgaria": "BG", "Serbia": "RS", "Norway": "NO", "Denmark": "DK", "Sweden": "SE",
    "Portugal": "PT", "Ireland": "IE", "Canada": "CA", "Australia": "AU", "Saudi Arabia": "SA", "Egypt": "EG",
    "Algeria": "DZ", "Libya": "LY", "Venezuela": "VE", "Colombia": "CO", "Chile": "CL", "Peru": "PE",
    "Philippines": "PH", "Indonesia": "ID", "Thailand": "TH", "Malaysia": "MY", "Vietnam": "VN",
    "Kazakhstan": "KZ", "Azerbaijan": "AZ", "Georgia": "GE", "Armenia": "AM", "Qatar": "QA", "Oman": "OM",
    "Kuwait": "KW", "United Arab Emirates": "AE", "Grenada": "GD", "New Zealand": "NZ", "Guatemala": "GT",
    "Mongolia": "MN", "Angola": "AO", "Burundi": "BI", "Andorra": "AD", "Slovenia": "SI", "Montenegro": "ME",
}
ALTA = {"US", "FR", "DE", "IT", "GB", "JP", "ES", "PL", "TW", "IL", "IR", "RU", "UA", "BR", "IN", "TR", "SA", "NG", "AR", "MX", "KR"}
MEDIA = {"NL", "BE", "AT", "GR", "PT", "HU", "RO", "CZ", "SK", "FI", "SE", "DK", "NO", "EE", "CH", "CA", "AU", "VE", "CO", "KZ", "AZ", "EG", "DZ", "LY", "IQ", "QA", "AE", "KW", "OM", "AO", "ID"}


def elezioni():
    url = "https://www.electionguide.org/elections/type/upcoming/"
    try:
        h = scarica(url)
        n = 0
        for tr in re.findall(r"<tr.*?</tr>", h, re.S):
            celle = [testo(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
            lk = re.search(r'(/elections/id/\d+/)', tr)
            if len(celle) < 5 or not lk:
                continue
            piene = [c for c in celle if c]
            m = None
            for c in piene[1:]:
                m = re.search(r"(\d{4}-\d{2}-\d{2})", c)
                if m:
                    break
            if not m:
                continue
            giorno = dt.date.fromisoformat(m.group(1))
            if not nella_finestra(giorno):
                continue
            nome_paese = piene[0]
            organo = re.sub(r"\s*\d{4}-\d{2}-\d{2}.*$", "", piene[1]).strip()
            stato = next((c for c in celle if c in ("Confirmed", "Date not confirmed")), "")
            snap = celle[-1] if celle[-1] in ("Yes", "No") else (celle[-2] if len(celle) > 6 else "")
            iso = PAESI.get(nome_paese)
            imp = "alta" if iso in ALTA else ("media" if iso in MEDIA else "bassa")
            note = "Data %s." % ("confermata" if stato == "Confirmed" else "non confermata (indicativa)")
            if "Yes" in celle[5:]:
                note += " Elezione anticipata."
            if not iso:
                note += " Paese: %s (codice ISO non mappato)." % nome_paese
            aggiungi(giorno, "elezioni", iso, "%s: %s" % (nome_paese, organo), imp, "IFES ElectionGuide",
                     "https://www.electionguide.org" + lk.group(1), note=note,
                     affidabilita="alta" if stato == "Confirmed" else "media")
            n += 1
        fonte("IFES ElectionGuide - elezioni in arrivo", url, "Termini d'uso IFES: uso non commerciale con citazione (verificare)")
        print("Elezioni:", n)
    except Exception as e:
        errore("ElectionGuide", e)


# ---------------------------------------------------------------- sanzioni
def sanzioni_ue():
    url = "https://www.sanctionsmap.eu/api/v1/regime"
    try:
        j = json.loads(scarica(url, timeout=60))
        n = 0
        for r in j.get("data", []):
            sc = r.get("expiration")
            if not sc:
                continue
            t = dt.datetime.fromtimestamp(int(sc), dt.timezone.utc)
            # le scadenze sono a mezzanotte di Bruxelles: conversione all'ora locale
            estate = ultima_domenica(t.year, 3) <= t.date() < ultima_domenica(t.year, 10)
            giorno = (t + dt.timedelta(hours=2 if estate else 1)).date()
            if not (OGGI - dt.timedelta(days=7) <= giorno <= FINE):
                continue
            paese = ((r.get("country") or {}).get("data") or {}).get("code")
            spec = re.sub(r"\s+", " ", r.get("specification", "")).strip()
            imp = "alta" if paese in ("RU", "UA", "IR", "BY") else ("media" if paese in ("SY", "VE", "TR", "LY", "MD") else "bassa")
            aggiungi(giorno, "sanzioni", paese or "EU", "UE: scadenza del regime di misure restrittive - " + spec[:140], imp,
                     "EU Sanctions Map (Commissione europea / Consiglio UE)", "https://www.sanctionsmap.eu/#/main/details/%s/" % r.get("id"),
                     note="Data di scadenza indicata da Sanctions Map; di norma il Consiglio rinnova prima. Se la data e' passata e non e' stata aggiornata, il rinnovo potrebbe non essere ancora registrato.",
                     affidabilita="media")
            n += 1
        fonte("EU Sanctions Map - regimi e scadenze", url, "Riuso consentito con citazione (Commissione europea, decisione 2011/833/UE)")
        print("Sanzioni UE:", n)
    except Exception as e:
        errore("EU Sanctions Map", e)


def ofac():
    url = "https://ofac.treasury.gov/recent-actions"
    try:
        h = scarica(url)
        n = 0
        azioni = [(a, b) for a, _, b in re.findall(r'<a href="(/recent-actions/(\d{8})[^"]*)"[^>]*>(.*?)</a>', h, re.S)]
        for lk, tit in azioni:
            giorno = dt.datetime.strptime(re.search(r"(\d{8})", lk).group(1), "%Y%m%d").date()
            if giorno < OGGI - dt.timedelta(days=14):
                continue
            tt = testo(tit)
            paese = None
            for chiave, iso in (("Iran", "IR"), ("Russia", "RU"), ("Venezuela", "VE"), ("North Korea", "KP"), ("Cuba", "CU"), ("Belarus", "BY"), ("Syria", "SY"), ("China", "CN")):
                if chiave in tt:
                    paese = iso
                    break
            imp = "alta" if paese in ("IR", "RU") else "media" if paese else "bassa"
            aggiungi(giorno, "sanzioni", paese or "US", "OFAC (Tesoro USA): " + tt[:200], imp, "OFAC, Recent Actions",
                     "https://ofac.treasury.gov" + lk, valore_uscito="Azione pubblicata", note="Azione gia' avvenuta (ultime due settimane).")
            n += 1
        fonte("OFAC - Recent Actions", url, "Pubblico dominio (governo USA)")
        print("OFAC:", n)
    except Exception as e:
        errore("OFAC", e)


# ---------------------------------------------------------------- manuali
def manuali():
    try:
        j = json.load(open(MANUALI, encoding="utf-8"))
    except Exception as e:
        errore("voci_manuali.json", e)
        return
    n = 0
    for v in j.get("voci", []):
        if v.get("solo_se_manca") and v.get("sostituisce") not in FONTI_FALLITE:
            continue
        d = v.get("data", "")
        if re.match(r"^\d{4}-\d{2}-\d{2}$", d):
            fine = v.get("data_fine") or d
            if dt.date.fromisoformat(fine) < INIZIO or dt.date.fromisoformat(d) > FINE:
                continue
        elif re.match(r"^\d{4}(-\d{2})?$", d):
            if d < INIZIO.isoformat()[:len(d)]:
                continue
        else:
            continue
        x = {k: v.get(k) for k in ("data", "data_fine", "ora_utc", "paese", "categoria", "titolo", "importanza",
                                   "valore_precedente", "valore_atteso", "valore_uscito", "fonte", "link",
                                   "data_fonte", "affidabilita", "note")}
        x["origine"] = "manuale" + (" (riserva)" if v.get("solo_se_manca") else "")
        ELEMENTI.append(x)
        n += 1
    fonte("Voci curate a mano (raccolta/calendario/voci_manuali.json)", "raccolta/calendario/voci_manuali.json",
          "Vedi fonte di ciascuna voce", j.get("aggiornato"))
    print("Manuali:", n)


# ---------------------------------------------------------------- main
def main():
    for f in (fed, bce, boj, boe, bls, bea, eurostat, eia, elezioni, sanzioni_ue, ofac, manuali):
        try:
            f()
        except Exception as e:  # rete di sicurezza: nessuna fonte deve fermare lo script
            errore(f.__name__, e)
    # una voce manuale (non di riserva) prevale sulla voce automatica dello stesso giorno, paese e categoria
    manuali_chiavi = {(e["data"], e["paese"], e["categoria"]) for e in ELEMENTI if e.get("origine") == "manuale"}
    visti, finali = set(), []
    for e in ELEMENTI:
        if e.get("origine") == "auto" and (e["data"], e["paese"], e["categoria"]) in manuali_chiavi \
                and e["categoria"] == "banca-centrale":
            continue
        chiave = (e["data"], e["titolo"].lower())
        if chiave in visti:
            continue
        visti.add(chiave)
        dd = e["data"]
        e["stato"] = ("passato" if (len(dd) == 10 and dd < OGGI.isoformat()) else
                      "oggi" if dd == OGGI.isoformat() else "futuro")
        finali.append(e)
    finali.sort(key=lambda e: (e["data"].ljust(10, "~"), e.get("ora_utc") or "99:99", e["titolo"]))
    for i, e in enumerate(finali, 1):
        e["id"] = "CAL-%s-%03d" % (e["data"].replace("-", "")[:8].ljust(8, "0"), i)
    uscita = {
        "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "finestra": {"da": INIZIO.isoformat(), "a": FINE.isoformat(), "riferimento": OGGI.isoformat()},
        "fonti": FONTI,
        "nota": ("Calendario di eventi che muovono mercati e geopolitica: banche centrali, dati macro USA ed eurozona, "
                 "energia, elezioni, vertici, sanzioni. Orari in UTC. Le voci 'auto' sono lette dalle fonti ufficiali a ogni esecuzione; "
                 "le voci 'manuale' sono curate in raccolta/calendario/voci_manuali.json. valore_uscito e' compilato solo dove la fonte "
                 "ufficiale lo pubblica; valore_atteso solo con fonte citata. Date 'AAAA' o 'AAAA-MM' = giorno non fissato."),
        "categorie": ["banca-centrale", "dato-macro", "energia", "elezioni", "vertice", "sanzioni"],
        "elementi": finali,
        "errori": ERRORI,
    }
    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    with open(USCITA, "w", encoding="utf-8") as f:
        json.dump(uscita, f, ensure_ascii=False, indent=1)
    print("Scritto %s: %d elementi, %d errori" % (USCITA, len(finali), len(ERRORI)))


if __name__ == "__main__":
    main()
