#!/usr/bin/env python3
"""Offshore wind milestone calendar: North Sea and Baltic, 2023-2027 (plus later anchors).

Standard library only. Curated items live in raccolta/eolico/calendario_voci.json.

What the script does:
  1. validates every item (required fields, unique id, date format and precision,
     country code, type, status, reliability, https link, source date);
  2. derives the period covered by each date (day, month, quarter, half, year or an
     explicit window with date_end) and flags STALE items: a 'scheduled' or
     'at risk' item whose period has ended without confirmation becomes
     status_effective = "unconfirmed" (curated 'status' is left untouched);
     scheduled items whose source is older than 180 days get 'needs_recheck';
  3. builds a summary: next 90 days, last 90 days, items by status/type, and
     supported capacity awarded by country and year vs national targets
     (installed end-2025 taken from docs/data/eolico-filiera.json if present);
  4. reads the offshoreWIND.biz RSS feed and lists CANDIDATE new items
     (milestone keywords + in-scope country/project names, links not already
     in the calendar). Candidates are suggestions only: never added to 'elementi'.

Optional environment variables:
  SENZA_RETE=1       no HTTP requests (validation and summary only)
  CONTROLLA_LINK=1   try to open every link (slow; failures only as warnings)
  OGGI=YYYY-MM-DD    reference date (default: today, UTC), useful for tests

Option: --rigoroso  exit code 1 if there are validation errors (for CI).

Output: docs/data/wind-calendar.json
"""
import calendar
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
DATI = os.path.join(RADICE, "docs", "data")
VOCI = os.path.join(QUI, "calendario_voci.json")
FILIERA = os.path.join(DATI, "eolico-filiera.json")
USCITA = os.path.join(DATI, "wind-calendar.json")
RSS = "https://www.offshorewind.biz/feed"
UA = "monitor-geoeconomico/1.0 (non-commercial OSINT research)"

ADESSO = dt.datetime.now(dt.timezone.utc)
OGGI = dt.date.fromisoformat(os.environ["OGGI"]) if os.environ.get("OGGI") else ADESSO.date()
ERRORI = []

COUNTRIES = {"GB", "NL", "BE", "DE", "DK", "NO", "SE", "FI", "PL", "LT", "LV", "EE", "FR", "EU"}
TYPES = {"auction", "FID", "construction", "first power", "commissioning", "delay",
         "cancellation", "grid", "policy"}
STATUSES = {"done", "scheduled", "at risk"}
RELIABILITY = {"high", "medium", "low"}
REQUIRED = ["id", "date", "country", "type", "project", "status", "summary",
            "source", "link", "source_date", "reliability"]
RE_DATE = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2}))?|-Q([1-4])|-H([12]))?$")
RE_SOURCE_DATE = re.compile(r"^(n\.d\.|\d{4}(-\d{2}(-\d{2})?)?)$")
WINDOW_DAYS = 90
RECHECK_DAYS = 180


def avviso(dove, msg):
    ERRORI.append({"fonte": dove, "errore": msg})
    print(f"[warning] {dove}: {msg}", file=sys.stderr)


def scarica(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ------------------------------------------------------------ dates
def periodo(testo):
    """'2026-11-26' / '2026-11' / '2026-Q4' / '2026-H2' / '2026' -> (start, end, precision)."""
    m = RE_DATE.match(str(testo or ""))
    if not m:
        raise ValueError(f"bad date: {testo!r}")
    y, mo, d, q, h = m.groups()
    y = int(y)
    if d:
        g = dt.date(y, int(mo), int(d))
        return g, g, "day"
    if mo:
        mo = int(mo)
        if not 1 <= mo <= 12:
            raise ValueError(f"bad month: {testo!r}")
        return dt.date(y, mo, 1), dt.date(y, mo, calendar.monthrange(y, mo)[1]), "month"
    if q:
        q = int(q)
        m1, m3 = 3 * q - 2, 3 * q
        return dt.date(y, m1, 1), dt.date(y, m3, calendar.monthrange(y, m3)[1]), "quarter"
    if h:
        return (dt.date(y, 1, 1), dt.date(y, 6, 30), "half") if h == "1" else \
               (dt.date(y, 7, 1), dt.date(y, 12, 31), "half")
    return dt.date(y, 1, 1), dt.date(y, 12, 31), "year"


def data_fonte(testo):
    """Latest plausible day of a source date (for age checks); None if n.d."""
    if not testo or testo == "n.d.":
        return None
    try:
        return periodo(testo)[1]
    except ValueError:
        return None


# ------------------------------------------------------------ validation
def valida(items):
    buoni, visti = [], set()
    for i, it in enumerate(items):
        dove = f"item {it.get('id', '#' + str(i))}"
        ok = True
        for c in REQUIRED:
            if it.get(c) in (None, ""):
                avviso(dove, f"missing required field: {c}")
                ok = False
        if not ok:
            continue
        if it["id"] in visti:
            avviso(dove, "duplicate id")
            continue
        visti.add(it["id"])
        try:
            inizio, fine, prec = periodo(it["date"])
            if it.get("date_end"):
                _, fine, _ = periodo(it["date_end"])
                prec = "window"
                if fine < inizio:
                    raise ValueError("date_end before date")
        except ValueError as e:
            avviso(dove, str(e))
            continue
        if it["country"] not in COUNTRIES:
            avviso(dove, f"unexpected country code: {it['country']}")
        if it["type"] not in TYPES:
            avviso(dove, f"unknown type: {it['type']}")
        if it["status"] not in STATUSES:
            avviso(dove, f"unknown status: {it['status']}")
        if it["reliability"] not in RELIABILITY:
            avviso(dove, f"unknown reliability: {it['reliability']}")
        if not str(it["link"]).startswith("https://") or re.search(r"\s", it["link"]):
            avviso(dove, f"link must be https without spaces: {it['link']}")
        if not RE_SOURCE_DATE.match(str(it["source_date"])):
            avviso(dove, f"source_date not YYYY[-MM[-DD]] or n.d.: {it['source_date']}")
        if it["status"] == "done" and inizio > OGGI:
            avviso(dove, f"status 'done' but date {it['date']} is in the future")
        for k in ("capacity_mw", "awarded_mw"):
            v = it.get(k)
            if v is not None and (not isinstance(v, (int, float)) or v < 0):
                avviso(dove, f"{k} must be a non-negative number or null")
        if it.get("awarded_mw") is not None and it["type"] != "auction":
            avviso(dove, "awarded_mw only allowed on auction items")
        it["_inizio"], it["_fine"], it["_prec"] = inizio, fine, prec
        buoni.append(it)
    return buoni


# ------------------------------------------------------------ status and staleness
def arricchisci(it):
    out = {k: v for k, v in it.items() if not k.startswith("_")}
    inizio, fine = it["_inizio"], it["_fine"]
    out["precision"] = it["_prec"]
    out["period_start"] = inizio.isoformat()
    out["period_end"] = fine.isoformat()
    flags = []
    eff = it["status"]
    if it["status"] in ("scheduled", "at risk") and fine < OGGI:
        eff = "unconfirmed"
        flags.append("stale")
        out["days_overdue"] = (OGGI - fine).days
    if it["status"] in ("scheduled", "at risk"):
        fd = data_fonte(it["source_date"])
        if fd is None or (OGGI - fd).days > RECHECK_DAYS:
            flags.append("needs_recheck")
    out["status_effective"] = eff
    out["flags"] = flags
    if fine < OGGI:
        out["timing"] = "past"
    elif inizio > OGGI:
        out["timing"] = "future"
    else:
        out["timing"] = "current"
    return out


def nella_finestra(e, da, a):
    return dt.date.fromisoformat(e["period_start"]) <= a and dt.date.fromisoformat(e["period_end"]) >= da


def breve(e):
    return {"id": e["id"], "date": e["date"], "date_end": e.get("date_end"),
            "country": e["country"], "type": e["type"], "project": e["project"],
            "capacity_mw": e.get("capacity_mw"), "status_effective": e["status_effective"]}


# ------------------------------------------------------------ awarded vs targets
def installato_filiera():
    try:
        with open(FILIERA, encoding="utf-8") as f:
            d = json.load(f)
        return {p["paese"]: p.get("installato_fine2025_mw") for p in d["obiettivi"]["paesi"]}
    except (OSError, KeyError, ValueError) as e:
        avviso(FILIERA, f"installed capacity not read: {e}")
        return {}


def assegnato(elementi, targets):
    per = {}
    for e in elementi:
        if e["type"] != "auction" or e.get("awarded_mw") is None or e["status_effective"] != "done":
            continue
        anno = e["period_start"][:4]
        per.setdefault(e["country"], {}).setdefault(anno, 0.0)
        per[e["country"]][anno] += e["awarded_mw"]
    inst = installato_filiera()
    righe = []
    for c in sorted(set(per) | {t["country"] for t in targets}):
        anni = {a: round(v, 1) for a, v in sorted(per.get(c, {}).items())}
        tot = round(sum(v for a, v in anni.items() if "2023" <= a <= "2026"), 1)
        t = next((t for t in targets if t["country"] == c), None)
        r = {"country": c, "awarded_mw_by_year": anni, "awarded_mw_2023_2026": tot,
             "installed_end2025_mw": inst.get(c)}
        if t:
            r.update({"target_gw": t["target_gw"], "target_low_gw": t.get("target_low_gw"),
                      "target_year": t["target_year"], "target_note": t.get("target_note"),
                      "target_source": t["source"], "target_link": t["link"]})
            if r["installed_end2025_mw"] is not None:
                gap = t["target_gw"] * 1000 - r["installed_end2025_mw"]
                r["gap_to_target_mw"] = round(gap)
                r["awarded_2023_2026_pct_of_gap"] = round(100 * tot / gap, 1) if gap > 0 else None
        righe.append(r)
    return righe


# ------------------------------------------------------------ RSS candidates
SCOPE = ["north sea", "baltic", "uk", "british", "britain", "scotland", "scottish", "england",
         "english", "welsh", "dutch", "netherlands", "german", "germany", "danish", "denmark",
         "belgian", "belgium", "norway", "norwegian", "sweden", "swedish", "finland", "finnish",
         "poland", "polish", "lithuania", "lithuanian", "latvia", "latvian", "estonia",
         "estonian", "france", "french", "dunkirk", "dunkerque", "tennet", "amprion", "50hertz",
         "energinet", "elia", "statnett", "rvo", "bnetza", "bsh", "desnz", "ofgem", "crown estate",
         "dogger", "hornsea", "norfolk", "east anglia", "sofia", "berwick", "inch cape", "thor",
         "baltica", "baltyk", "baltic power", "ijmuiden", "nederwiek", "borkum", "he dreiht",
         "nordlicht", "nordseecluster", "bornholm", "princess elisabeth", "utsira",
         "balwin", "lanwin", "dolwin", "borwin", "ecowende", "oranjewind", "zeevonk"]
OUT_OF_SCOPE = ["us ", "u.s.", "united states", "american", "maryland", "virginia", "new york",
                "massachusetts", "rhode island", "korea", "korean", "japan", "japanese",
                "taiwan", "australia", "new zealand", "india", "china", "chinese", "philippines",
                "vietnam", "brazil", "türkiye", "turkish", "greece", "greek", "mediterranean"]
MILESTONES = [
    ("auction", ["tender", "auction", "allocation round", "bid", "bids", "cfd", "awarded the right",
                 "seabed lease", "winner"]),
    ("FID", ["final investment decision", "fid", "financial close"]),
    ("first power", ["first power", "first electricity", "first turbine", "first energy"]),
    ("commissioning", ["fully commissioned", "commissioned", "commercial operation",
                       "fully operational", "inaugurat"]),
    ("delay", ["delay", "postpone", "slip", "pushed back", "deferred", "extension of the deadline"]),
    ("cancellation", ["cancel", "discontinu", "halt", "scrap", "withdraw", "exit", "terminate"]),
    ("grid", ["grid connection", "hvdc", "converter", "substation", "export cable", "energy island",
              "interconnector", "platform"]),
    ("policy", ["target", "offshore wind act", "windseeg", "government", "ministry", "minister",
                "parliament", "regulation", "port", "terminal", "budget"]),
    ("construction", ["installation", "installed", "monopile", "construction", "keel", "foundation"]),
]


def contiene(testo, parola):
    return re.search(r"(?<![a-z0-9])" + re.escape(parola.strip()) + r"(?![a-z0-9])", testo) is not None


def candidati_rss(elementi):
    if os.environ.get("SENZA_RETE"):
        return {"stato": "skipped (SENZA_RETE)", "candidati": []}
    try:
        radice = ET.fromstring(scarica(RSS))
    except (urllib.error.URLError, TimeoutError, OSError, ET.ParseError) as e:
        avviso(RSS, f"RSS not read: {e}")
        return {"stato": f"error: {e}", "candidati": []}
    noti = {e["link"].rstrip("/").lower() for e in elementi}
    progetti = {e["project"].split("(")[0].strip().lower() for e in elementi}
    out, letti = [], 0
    for item in radice.iter("item"):
        letti += 1
        titolo = html.unescape(item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = html.unescape(re.sub(r"<[^>]+>", " ", item.findtext("description") or ""))
        pub = item.findtext("pubDate") or ""
        try:
            data = dt.datetime.strptime(pub[:16], "%a, %d %b %Y").date().isoformat()
        except ValueError:
            data = None
        testo = f" {titolo} {desc} ".lower()
        if link.rstrip("/").lower() in noti:
            continue
        scope = [k for k in SCOPE if contiene(testo, k)]
        fuori = [k for k in OUT_OF_SCOPE if contiene(testo, k)]
        if not scope or (fuori and len(fuori) >= len(scope)):
            continue
        tipi = [t for t, parole in MILESTONES if any(contiene(testo, p) for p in parole)]
        if not tipi:
            continue
        legati = sorted(p for p in progetti if len(p) > 4 and p in testo)
        out.append({"title": titolo, "date": data, "link": link,
                    "suggested_type": tipi[0], "matched_types": tipi,
                    "scope_terms": scope[:6], "related_calendar_projects": legati[:5],
                    "excerpt": re.sub(r"\s+", " ", desc).strip()[:240],
                    "action": "review manually; add to calendario_voci.json only with a primary source"})
    return {"stato": f"ok: {letti} RSS items read, {len(out)} candidates", "candidati": out}


# ------------------------------------------------------------ link check
def controlla_link(elementi):
    if not os.environ.get("CONTROLLA_LINK") or os.environ.get("SENZA_RETE"):
        return
    for link in sorted({e["link"] for e in elementi}):
        try:
            req = urllib.request.Request(link, headers={"User-Agent": "Mozilla/5.0 " + UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                if r.status >= 400:
                    avviso(link, f"HTTP {r.status}")
        except urllib.error.HTTPError as e:
            if e.code not in (401, 403, 405, 429):  # anti-bot answers are not broken links
                avviso(link, f"HTTP {e.code}")
        except Exception as e:  # noqa: BLE001 - one link must never stop the run
            avviso(link, f"unreachable: {e}")


# ------------------------------------------------------------ main
def main():
    rigoroso = "--rigoroso" in sys.argv
    with open(VOCI, encoding="utf-8") as f:
        voci = json.load(f)
    items = valida(voci["items"])
    n_val = len(ERRORI)
    elementi = sorted((arricchisci(i) for i in items), key=lambda e: (e["period_start"], e["id"]))
    controlla_link(elementi)

    da, a = OGGI - dt.timedelta(days=WINDOW_DAYS), OGGI + dt.timedelta(days=WINDOW_DAYS)
    prossimi = [breve(e) for e in elementi if e["timing"] != "past" and nella_finestra(e, OGGI, a)]
    passati = [breve(e) for e in elementi if nella_finestra(e, da, OGGI)
               and dt.date.fromisoformat(e["period_start"]) <= OGGI]
    stale = [dict(breve(e), days_overdue=e.get("days_overdue")) for e in elementi if "stale" in e["flags"]]
    recheck = [e["id"] for e in elementi if "needs_recheck" in e["flags"]]
    conta = lambda campo: {k: sum(1 for e in elementi if e[campo] == k)
                           for k in sorted({e[campo] for e in elementi})}
    rss = candidati_rss(elementi)

    fonti, visti = [], set()
    for e in elementi:
        dom = re.sub(r"^https://(www\.)?", "", e["link"]).split("/")[0]
        if dom not in visti:
            visti.add(dom)
            fonti.append({"nome": e["source"].split(";")[0], "link": e["link"],
                          "licenza": "Open Government Licence v3.0" if dom.endswith("gov.uk")
                          else "(c) publisher: facts quoted with link",
                          "data_dato": e["source_date"]})
    fonti.append({"nome": "offshoreWIND.biz RSS (candidate items only)", "link": RSS,
                  "licenza": "(c) Navingo/offshoreWIND.biz: headlines and links only",
                  "data_dato": OGGI.isoformat()})

    uscita = {
        "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "riferimento": OGGI.isoformat(),
        "fonti": fonti,
        "nota": ("Offshore wind milestone calendar for the North Sea and the Baltic (GB, NL, BE, DE, DK, NO, "
                 "SE, FI, PL, LT, LV, EE, FR, EU), 2023-2027 with later anchors. Curated items with source, link "
                 "and source date; null = not found, never estimated. 'status' is curated (done/scheduled/at risk); "
                 "'status_effective' adds 'unconfirmed' when a scheduled date has passed without confirmation. "
                 "Reliability high/medium/low = alta/media/bassa. 'precision' tells how exact the date is. "
                 "'candidati_rss' are suggestions from the offshoreWIND.biz feed, NOT verified items."),
        "riepilogo": {
            "items": len(elementi),
            "by_status_effective": conta("status_effective"),
            "by_type": conta("type"),
            "by_country": conta("country"),
            "next_90_days": {"from": OGGI.isoformat(), "to": a.isoformat(), "items": prossimi},
            "last_90_days": {"from": da.isoformat(), "to": OGGI.isoformat(), "items": passati},
            "unconfirmed_stale": stale,
            "needs_recheck": recheck,
            "awarded_vs_targets": {
                "nota": ("Supported or zero-subsidy capacity awarded in auctions/tenders (status done), by year of award. "
                         "Site-right auctions without revenue support (e.g. Estonia Saare 1) are not counted. "
                         "Gap = target minus installed end-2025 (WindEurope national totals via eolico-filiera.json; "
                         "include seas outside North Sea/Baltic for GB, FR, DE, DK). Awarded capacity mostly "
                         "comes online after 2030: the share is an upper bound for target delivery."),
                "per_country": assegnato(elementi, voci.get("targets", [])),
            },
        },
        "elementi": elementi,
        "candidati_rss": rss,
        "errori": ERRORI,
    }
    os.makedirs(DATI, exist_ok=True)
    with open(USCITA, "w", encoding="utf-8") as f:
        json.dump(uscita, f, ensure_ascii=False, indent=1)
    print(f"Written {USCITA} ({os.path.getsize(USCITA) / 1024:.0f} KB): {len(elementi)} items, "
          f"{len(prossimi)} next 90 days, {len(passati)} last 90 days, {len(stale)} unconfirmed, "
          f"{len(rss['candidati'])} RSS candidates, {len(ERRORI)} warnings ({n_val} validation)")
    if rigoroso and n_val:
        sys.exit(1)


if __name__ == "__main__":
    main()
