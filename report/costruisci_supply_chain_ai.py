#!/usr/bin/env python3
"""Costruisce il report «La catena dell'AI, dalla miniera al data center» da docs/data/supply-chain-ai.json.

Solo libreria standard di Python 3. Uso, dalla radice del repository:

    python3 raccolta/supply-chain-ai/raccogli.py          # prima aggiorna i dati
    python3 report/costruisci_supply_chain_ai.py          # poi il report (mese corrente)
    python3 report/costruisci_supply_chain_ai.py --mese 2026-11

Scrive report/supply-chain-ai-AAAA-MM.md e docs/report/supply-chain-ai-AAAA-MM.html.
I numeri di tabelle, grafici e del riquadro «In breve» vengono dal file di dati (che a sua volta
li calcola da USGS, prezzi.json, portwatch.json...). Il testo per anello sta in
raccolta/supply-chain-ai/anelli.json con i link alle fonti. Il diagramma della catena e il grafico
delle concentrazioni sono SVG generati qui dai dati.
"""

import argparse
import datetime as dt
import html
import json
import os
import re

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(RADICE, "docs", "data", "supply-chain-ai.json")
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]
PAESI = {"US": "Stati Uniti", "CN": "Cina", "TW": "Taiwan", "KR": "Corea del Sud", "JP": "Giappone",
         "NL": "Paesi Bassi", "DE": "Germania", "IE": "Irlanda", "SG": "Singapore", "MY": "Malesia",
         "AE": "Emirati", "QA": "Qatar", "UA": "Ucraina", "CD": "Congo (RD)", "EE": "Estonia", "MX": "Messico",
         "FR": "Francia", "IT": "Italia", "OM": "Oman", "IL": "Israele", "IN": "India"}
STATO_ETICHETTA = {"critico": ("■", "critico", "s-critico"), "attenzione": ("▲", "attenzione", "s-attenzione"),
                   "normale": ("●", "normale", "s-normale"), "informativo": ("○", "informativo", ""),
                   "non misurato": ("○", "non misurato", "")}


def num(x, dec=1):
    if x is None:
        return "—"
    if isinstance(x, (int,)) or (isinstance(x, float) and x.is_integer() and dec == 0):
        s = "{:,}".format(int(x))
    else:
        s = ("{:,.%df}" % dec).format(x)
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x, segno=True):
    if x is None:
        return "—"
    s = num(abs(x), 1 if abs(x) < 10 else 0) + "%"
    if not segno:
        return s
    return ("+" if x > 0 else "−" if x < 0 else "") + s


def data_it(s):
    d = dt.date.fromisoformat(s[:10]) if s and len(s) >= 10 else None
    return "%d %s %d" % (d.day, MESI[d.month - 1], d.year) if d else (s or "—")


# ----------------------------------------------------------------------------------------
# Blocchi: ogni blocco si rende sia in Markdown sia in HTML
# ----------------------------------------------------------------------------------------
def inline_html(s):
    out, pos = [], 0
    for m in re.finditer(r"\[([^\]]+)\]\((https?://[^)\s]+)\)|\*\*(.+?)\*\*", s):
        out.append(html.escape(s[pos:m.start()], quote=False))
        if m.group(1):
            out.append('<a href="%s" rel="noopener">%s</a>' % (html.escape(m.group(2)), html.escape(m.group(1), quote=False)))
        else:
            out.append("<strong>%s</strong>" % html.escape(m.group(3), quote=False))
        pos = m.end()
    out.append(html.escape(s[pos:], quote=False))
    return "".join(out)


class Doc:
    def __init__(self):
        self.b = []

    def h2(self, ident, testo):
        self.b.append(("h2", ident, testo))

    def h3(self, testo):
        self.b.append(("h3", testo))

    def p(self, testo):
        self.b.append(("p", testo))

    def ul(self, voci):
        self.b.append(("ul", voci))

    def val(self, testo):
        self.b.append(("val", testo))

    def tab(self, intest, righe, nota=None):
        self.b.append(("tab", intest, righe, nota))

    def nota(self, testo):
        self.b.append(("nota", testo))

    def svg(self, largo, stretto, didascalia, nome_md):
        self.b.append(("svg", largo, stretto, didascalia, nome_md))

    def apri(self, sommario, aperto=False):
        """Inizio di un blocco comprimibile (<details>): su telefono la pagina resta corta."""
        self.b.append(("apri", sommario, aperto))

    def chiudi(self):
        self.b.append(("chiudi",))

    def box(self, classe, titolo, voci):
        """Riquadro con titolo ed elenco (stato delle scadenze, revisione)."""
        self.b.append(("box", classe, titolo, voci))

    def md(self):
        out = []
        for b in self.b:
            k = b[0]
            if k == "h2":
                out += ['<a id="%s"></a>' % b[1], "", "## " + b[2], ""]
            elif k == "h3":
                out += ["### " + b[1], ""]
            elif k == "p":
                out += [b[1], ""]
            elif k == "ul":
                out += ["- " + v for v in b[1]] + [""]
            elif k == "val":
                out += ["> *Valutazione.* " + b[1], ""]
            elif k == "tab":
                out.append("| " + " | ".join(b[1]) + " |")
                out.append("|" + "---|" * len(b[1]))
                for r in b[2]:
                    out.append("| " + " | ".join(cella_md(c) for c in r) + " |")
                out.append("")
                if b[3]:
                    out += ["<small>" + b[3] + "</small>", ""]
            elif k == "nota":
                out += ["<small>" + b[1] + "</small>", ""]
            elif k == "svg":
                out += ["![%s](grafici/%s)" % (re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", b[3]).split(".")[0], b[4]), "", "<small>" + b[3] + "</small>", ""]
            elif k == "apri":
                out += ["<details%s><summary>%s</summary>" % (" open" if b[2] else "", re.sub(r"\*\*(.+?)\*\*", r"\1", b[1])), ""]
            elif k == "chiudi":
                out += ["</details>", ""]
            elif k == "box":
                out += ["> **%s**" % b[2], ">"] + ["> - " + v for v in b[3]] + [""]
        return "\n".join(out)

    def html(self):
        out = []
        for b in self.b:
            k = b[0]
            if k == "h2":
                out.append('<h2 id="%s">%s</h2>' % (b[1], inline_html(b[2])))
            elif k == "h3":
                out.append("<h3>%s</h3>" % inline_html(b[1]))
            elif k == "p":
                out.append("<p>%s</p>" % inline_html(b[1]))
            elif k == "ul":
                out.append("<ul>" + "".join("<li>%s</li>" % inline_html(v) for v in b[1]) + "</ul>")
            elif k == "val":
                out.append('<aside class="valutazione"><span class="etichetta">Valutazione</span>%s</aside>' % inline_html(b[1]))
            elif k == "tab":
                t = ['<div class="tabella" role="region" tabindex="0" aria-label="Tabella"><table><thead><tr>']
                t += ['<th scope="col">%s</th>' % inline_html(h) for h in b[1]]
                t.append("</tr></thead><tbody>")
                for r in b[2]:
                    t.append("<tr>" + "".join("<td>%s</td>" % cella_html(c) for c in r) + "</tr>")
                t.append("</tbody></table></div>")
                out.append("".join(t))
                if b[3]:
                    out.append('<p class="nota">%s</p>' % inline_html(b[3]))
            elif k == "nota":
                out.append('<p class="nota">%s</p>' % inline_html(b[1]))
            elif k == "svg":
                out.append('<figure><div class="grafico"><div class="largo">%s</div><div class="stretto">%s</div></div>'
                           '<figcaption>%s</figcaption></figure>' % (b[1], b[2], inline_html(b[3])))
            elif k == "apri":
                out.append('<details class="dettagli"%s><summary>%s</summary>' % (" open" if b[2] else "", inline_html(b[1])))
            elif k == "chiudi":
                out.append("</details>")
            elif k == "box":
                out.append('<aside class="box %s"><p class="box-titolo">%s</p><ul>%s</ul></aside>' % (
                    b[1], inline_html(b[2]), "".join("<li>%s</li>" % inline_html(v) for v in b[3])))
        return "\n".join(out)


def cella_html(c):
    c = str(c)
    m = re.match(r"^\{stato:([a-z ]+)\}$", c)
    if m:
        sym, lab, cls = STATO_ETICHETTA.get(m.group(1), ("○", m.group(1), ""))
        return '<span class="stato %s">%s</span>' % (cls, html.escape(lab))
    return inline_html(c)


def cella_md(c):
    c = str(c).replace("|", "/")
    m = re.match(r"^\{stato:([a-z ]+)\}$", c)
    return stato_md(m.group(1)) if m else c


def stato_md(s):
    sym, lab, _ = STATO_ETICHETTA.get(s, ("○", s, ""))
    return "%s %s" % (sym, lab)


def cella_stato(s):
    return "{stato:%s}" % s


# ----------------------------------------------------------------------------------------
# SVG
# ----------------------------------------------------------------------------------------
STILE_SVG = """<style>
.viz{--v-ink:#1D272D;--v-soft:#52606A;--v-faint:#86929A;--v-grid:#DCDFDD;--v-card:#FFFFFF;--v-band:#ECE9E0;--v-acc:#A61E6B;
--v-ok:#0ca30c;--v-warn:#b47d00;--v-crit:#d03b3b;font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
@media (prefers-color-scheme:dark){.viz{--v-ink:#DAE0E2;--v-soft:#A0ABB1;--v-faint:#6C787F;--v-grid:#2B373E;--v-card:#172127;--v-band:#1A252C;--v-acc:#d14f9a;
--v-ok:#3fbf3f;--v-warn:#fab219;--v-crit:#e5605f}}
.viz text{fill:var(--v-soft);font-size:12px}.viz .ink{fill:var(--v-ink)}.viz .b{font-weight:600}.viz .faint{fill:var(--v-faint)}
.viz .box{fill:var(--v-card);stroke:var(--v-grid);stroke-width:1}.viz .box-crit{stroke:var(--v-crit);stroke-width:1.5}
.viz .box-warn{stroke:var(--v-warn);stroke-width:1.5}.viz .num{font-variant-numeric:tabular-nums}
.viz .arr{stroke:var(--v-faint);stroke-width:1.5;fill:none}.viz .head{fill:var(--v-faint)}
.viz .acc{fill:var(--v-acc)}.viz .f-ok{fill:var(--v-ok)}.viz .f-warn{fill:var(--v-warn)}.viz .f-crit{fill:var(--v-crit)}
.viz .bar{fill:var(--v-acc)}.viz .track{fill:var(--v-band)}.viz .grid{stroke:var(--v-grid);stroke-width:1}
.viz .hit{fill:transparent}.viz .hit:hover{fill:var(--v-ink);fill-opacity:.05}
</style>"""


def esc(s):
    return html.escape(str(s), quote=True)


def simbolo_stato(x, y, stato):
    cls = {"critico": "f-crit", "attenzione": "f-warn", "normale": "f-ok"}.get(stato, "faint")
    if stato == "critico":
        return '<rect x="%.1f" y="%.1f" width="9" height="9" class="%s"/>' % (x, y - 8, cls)
    if stato == "attenzione":
        return '<path d="M%.1f %.1f l5 -9 l5 9 z" class="%s"/>' % (x - 0.5, y + 1, cls)
    return '<circle cx="%.1f" cy="%.1f" r="4.5" class="%s"/>' % (x + 4.5, y - 3.5, cls)


def dati_anello(d, a):
    nodi = [n for n in d["elementi"] if n["anello"] == a["id"]]
    conta = {}
    for n in nodi:
        conta[n["paese"]] = conta.get(n["paese"], 0) + 1
    top = [PAESI.get(p, p) for p in a.get("paesi_chiave", [])] or [PAESI.get(p, p) for p, _ in sorted(conta.items(), key=lambda kv: (-kv[1], kv[0]))[:3]]
    ids = {n["id"] for n in nodi}
    # un collo conta per l'anello se è suo o se tocca uno dei suoi nodi (es. lo Stretto di Taiwan per la logistica)
    colli = [c for c in d["colli"] if c["anello"] == a["id"] or ids & set(c.get("nodi", []))]
    ordine = {"critico": 2, "attenzione": 1}
    peggio = max((c["stato"] for c in colli), key=lambda s: ordine.get(s, 0), default=None)
    return nodi, top, colli, peggio


def diagramma(d, largo=True):
    anelli = d["anelli"]
    if largo:
        W, cols, bw, bh, gx, gy, x0, y0 = 720, 4, 150, 128, 26, 58, 12, 44
    else:
        W, cols, bw, bh, gx, gy, x0, y0 = 340, 1, 300, 92, 0, 26, 20, 44
    rows = (len(anelli) + cols - 1) // cols
    H = y0 + rows * bh + (rows - 1) * gy + 56
    tid = "g-catena-%s" % ("l" if largo else "s")
    o = ['<svg class="viz" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" role="img" aria-labelledby="%s-t %s-d" style="max-width:%dpx;height:auto;display:block">' % (W, H, tid, tid, W),
         '<title id="%s-t">La catena del valore dell\'AI in otto anelli</title>' % tid,
         '<desc id="%s-d">Dalla miniera al data center: per ogni anello i paesi con più nodi, il numero di nodi e lo stato peggiore dei colli di bottiglia.</desc>' % tid,
         STILE_SVG,
         '<text x="%d" y="18" class="ink b">Dalla miniera al data center</text>' % x0,
         ('<text x="%d" y="34" class="faint">paesi chiave · nodi e titoli nel file di dati · simbolo = collo di bottiglia peggiore</text>' % x0) if largo else
         ('<text x="%d" y="34" class="faint">paesi chiave · simbolo = collo peggiore</text>' % x0)]
    pos = []
    for i, a in enumerate(anelli):
        r, c = divmod(i, cols)
        x = x0 + c * (bw + gx)
        y = y0 + r * (bh + gy)
        pos.append((x, y))
    # frecce
    for i in range(len(anelli) - 1):
        (x1, y1), (x2, y2) = pos[i], pos[i + 1]
        if largo and y1 == y2:
            o.append('<path d="M%.1f %.1f H%.1f" class="arr"/><path d="M%.1f %.1f l-7 -4 v8 z" class="head"/>' % (x1 + bw + 2, y1 + bh / 2, x2 - 4, x2 - 2, y1 + bh / 2))
        elif largo:
            ym = y1 + bh + gy / 2
            o.append('<path d="M%.1f %.1f V%.1f H%.1f V%.1f" class="arr"/><path d="M%.1f %.1f l-4 -7 h8 z" class="head"/>' % (
                x1 + bw / 2, y1 + bh + 2, ym, x2 + bw / 2, y2 - 4, x2 + bw / 2, y2 - 2))
        else:
            o.append('<path d="M%.1f %.1f V%.1f" class="arr"/><path d="M%.1f %.1f l-4 -7 h8 z" class="head"/>' % (
                x1 + bw / 2, y1 + bh + 2, y2 - 4, x1 + bw / 2, y2 - 2))
    for i, a in enumerate(anelli):
        x, y = pos[i]
        nodi, top, colli, peggio = dati_anello(d, a)
        cls = {"critico": " box-crit", "attenzione": " box-warn"}.get(peggio, "")
        tip = "%s: %d nodi; %s; colli di bottiglia: %s" % (a["nome"], len(nodi), ", ".join(top),
                                                           "; ".join("%s (%s)" % (c["nome"], c["stato"]) for c in colli) or "nessuno")
        o.append('<g><title>%s</title>' % esc(tip))
        o.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="6" class="box%s"/>' % (x, y, bw, bh, cls))
        o.append('<text x="%.1f" y="%.1f" class="acc b num" style="font-size:13px">%d</text>' % (x + 10, y + 20, a["ordine"]))
        o.append('<text x="%.1f" y="%.1f" class="ink b" style="font-size:13px">%s</text>' % (x + 26, y + 20, esc(a["breve"])))
        if largo:
            for j, p in enumerate(top):
                o.append('<text x="%.1f" y="%.1f">%s</text>' % (x + 10, y + 42 + j * 16, esc(p)))
            o.append('<text x="%.1f" y="%.1f" class="faint num">%d nodi · %d titoli</text>' % (x + 10, y + bh - 30, len(nodi), len(a.get("titoli", []))))
        else:
            o.append('<text x="%.1f" y="%.1f">%s</text>' % (x + 10, y + 42, esc(", ".join(top))))
            o.append('<text x="%.1f" y="%.1f" class="faint num">%d nodi · %d titoli</text>' % (x + 10, y + 60, len(nodi), len(a.get("titoli", []))))
        if peggio:
            o.append(simbolo_stato(x + 10, y + bh - 10, peggio))
            o.append('<text x="%.1f" y="%.1f" class="ink">%s</text>' % (x + 24, y + bh - 10, esc(STATO_ETICHETTA[peggio][1])))
        else:
            o.append('<text x="%.1f" y="%.1f" class="faint">nessun indicatore</text>' % (x + 10, y + bh - 10))
        o.append("</g>")
    yl = H - 16
    o.append(simbolo_stato(x0, yl, "critico") + '<text x="%d" y="%d">critico</text>' % (x0 + 14, yl))
    o.append(simbolo_stato(x0 + 80, yl, "attenzione") + '<text x="%d" y="%d">attenzione</text>' % (x0 + 94, yl))
    o.append(simbolo_stato(x0 + 180, yl, "normale") + '<text x="%d" y="%d">normale</text>' % (x0 + 194, yl))
    o.append("</svg>")
    return "\n".join(o)


def grafico_concentrazione(d, largo=True):
    righe = [m for m in d["materie"] if m.get("primo_produttore")]
    righe = [m for m in righe if m["primo_produttore"]["quota_pct"] >= 30]
    righe.sort(key=lambda m: -m["primo_produttore"]["quota_pct"])
    W = 720 if largo else 340
    lab = 230 if largo else 120
    x0, x1 = lab, W - 56
    rh, y0 = 30, 50
    H = y0 + len(righe) * rh + 30
    tid = "g-conc-%s" % ("l" if largo else "s")
    o = ['<svg class="viz" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" role="img" aria-labelledby="%s-t %s-d" style="max-width:%dpx;height:auto;display:block">' % (W, H, tid, tid, W),
         '<title id="%s-t">Quota del primo paese produttore per materia</title>' % tid,
         '<desc id="%s-d">USGS Mineral Commodity Summaries 2026, dati 2025. Quote calcolate dalla produzione per paese.</desc>' % tid,
         STILE_SVG,
         '<text x="8" y="18" class="ink b">Quota del primo produttore, %</text>',
         '<text x="8" y="34" class="faint">%s</text>' % ("USGS MCS 2026, dati 2025 · solo materie con primo produttore ≥ 30%" if largo else "USGS MCS 2026, dati 2025")]
    for k in (0, 50, 100):
        xx = x0 + (x1 - x0) * k / 100
        o.append('<line x1="%.1f" x2="%.1f" y1="%d" y2="%d" class="grid"/>' % (xx, xx, y0 - 6, H - 26))
        o.append('<text x="%.1f" y="%d" text-anchor="middle" class="faint num">%d</text>' % (xx, H - 10, k))
    for i, m in enumerate(righe):
        y = y0 + i * rh
        q = m["primo_produttore"]["quota_pct"]
        w = (x1 - x0) * q / 100
        nome = m["nome"].split(" (")[0]
        etich = "%s · %s" % (nome, m["primo_produttore"]["nome_paese"]) if largo else nome
        o.append('<g><title>%s</title>' % esc("%s: %s %s%% (%s)" % (m["nome"], m["primo_produttore"]["nome_paese"], num(q), m["fonte"])))
        o.append('<rect x="0" y="%d" width="%d" height="%d" class="hit"/>' % (y - 4, W, rh))
        o.append('<text x="%d" y="%d" text-anchor="end" class="ink">%s</text>' % (x0 - 8, y + 12, esc(etich)))
        o.append('<rect x="%.1f" y="%d" width="%.1f" height="14" rx="2" class="bar"/>' % (x0, y + 1, max(w, 2)))
        o.append('<text x="%.1f" y="%d" class="ink b num">%s</text>' % (x0 + w + 6, y + 12, num(q)))
        o.append("</g>")
    o.append("</svg>")
    return "\n".join(o)


# ----------------------------------------------------------------------------------------
def fonte_md(x):
    if not x.get("link"):
        return x.get("fonte") or "—"
    return "[%s](%s)" % (x.get("fonte", "fonte").replace("[", "(").replace("]", ")"), x["link"])


def prezzo_txt(t):
    p = t.get("prezzo")
    if not p:
        return "non seguito", "—", "—", "—"
    v = p.get("var") or {}
    ult = "%s %s" % (num(p["ultimo"], 2 if p["ultimo"] < 10000 else 0), p.get("valuta") or "")
    return ult.strip() + (" *" if p.get("provvisorio") else ""), pct(v.get("1m")), pct(v.get("ytd")), pct(v.get("1a"))


def costruisci(d, mese):
    anno, m = mese.split("-")
    titolo = "La catena dell'AI, dalla miniera al data center — %s %s" % (MESI[int(m) - 1], anno)
    rif = d["data_riferimento"]
    colli = {c["id"]: c for c in d["colli"]}
    ctrl = {c["id"]: c for c in d["controlli"]}
    mat = {x["id"]: x for x in d["materie"]}
    nodi = {n["id"]: n for n in d["elementi"]}
    tit = {t["simbolo"]: t for t in d["titoli"]}
    doc = Doc()

    # --- In breve
    ree, gage = ctrl["CN-2025-10-TR"], ctrl["CN-2024-USBAN"]
    ind = {(c["id"], i["nome"]): i for c in d["colli"] for i in c["indicatori"]}

    def ival(cid, inizio):
        for (c, n), i in ind.items():
            if c == cid and n.startswith(inizio):
                return i
        return {}
    hz = ival("C02", "Transiti a Hormuz")
    tw = ival("C06", "Transiti nello Stretto")
    sox, nvda, hyn, asml = (tit[s].get("prezzo") or {} for s in ("SOX", "NVDA", "000660.KS", "ASML"))
    breve = [
        "**Il rischio di questa settimana è cinese.** La sospensione delle misure di ottobre 2025 su terre rare e regola dello 0,1%% scade %s (%s) e le fonti non concordano su una proroga; il divieto di export di gallio e germanio verso gli USA torna tra %d giorni (%s). La Cina fa il %s%% del gallio primario e il %s%% delle terre rare estratte ([USGS MCS 2026](%s))." % (
            ("domani" if ree["giorni_alla_scadenza"] == 1 else "oggi" if ree["giorni_alla_scadenza"] == 0 else "tra %d giorni" % ree["giorni_alla_scadenza"]), data_it(ree["scadenza"]), gage["giorni_alla_scadenza"], data_it(gage["scadenza"]),
            num(mat["gallio"]["primo_produttore"]["quota_pct"], 0), num(mat["terre-rare"]["primo_produttore"]["quota_pct"]), mat["terre-rare"]["link"]),
        "**Tre punti unici di rottura.** Gli scanner EUV escono solo da Veldhoven (Paesi Bassi); TSMC ha il %s%% della fonderia mondiale e fa il 2 nm solo a Taiwan; il packaging CoWoS delle GPU è quasi tutto a Tainan e Chiayi. Diversificazione in corso (Arizona, Kumamoto, Dresda) ma i wafer americani tornano a Taiwan per il packaging ([TrendForce](%s))." % (num(ival("C06", "Quota TSMC").get("valore")), ival("C06", "Quota TSMC").get("link")),
        "**La logistica pesa già.** A Hormuz passano %s navi al giorno (%s su un anno, [IMF PortWatch](https://portwatch.imf.org/)): l'elio del Qatar, un terzo del mondo, è in gran parte fermo da marzo. Lo Stretto di Taiwan invece è normale (%s navi al giorno, %s su un anno)." % (
            num((hz.get("dettaglio") or {}).get("navi_giorno")), pct(hz.get("valore")), num((tw.get("dettaglio") or {}).get("navi_giorno"), 0), pct(tw.get("valore"))),
        "**La memoria è il nuovo collo di bottiglia.** HBM divisa tra SK Hynix 50%%, Samsung 33%% e Micron 18%% (Counterpoint, 2° trimestre 2026); prezzi DRAM previsti +%s%% nel 4° trimestre ([TrendForce](%s)). Per la Cina l'HBM è il limite vero della produzione Huawei." % (num(ival("C08", "Prezzi contrattuali").get("valore"), 0), ival("C08", "Prezzi contrattuali").get("link")),
        "**In borsa vincono i colli di bottiglia fisici.** Da inizio anno SK Hynix %s, ASML %s, indice SOX %s; Nvidia %s. Nell'ultimo mese correzione su tutto il comparto (SOX %s; prezzi.json, %s)." % (
            pct((hyn.get("var") or {}).get("ytd")), pct((asml.get("var") or {}).get("ytd")), pct((sox.get("var") or {}).get("ytd")),
            pct((nvda.get("var") or {}).get("ytd")), pct((sox.get("var") or {}).get("1m")), data_it(sox.get("data"))),
    ]
    doc.h2("in-breve", "1. In breve")
    doc.ul(breve)
    doc.val("La catena dell'AI è lunga ma stretta in pochi punti, e quasi tutti sono in Asia orientale o dipendono da una sola società. Per l'Europa del Nord il legame più forte è anche il più solido: le macchine EUV di Veldhoven. I punti deboli sono a monte (terre rare, gallio, elio) e a valle (energia e trasformatori), più che nei chip.")

    # --- Diagramma
    doc.h2("catena", "2. La catena in un colpo d'occhio")
    doc.p("Otto anelli, dalla miniera al data center. Ogni riquadro mostra i paesi chiave dell'anello (valutazione dell'osservatorio), quanti nodi e titoli quotati sono collegati e lo stato del collo di bottiglia peggiore. Il riquadro ha il bordo colorato quando un indicatore supera una soglia: le soglie sono una valutazione dell'osservatorio, spiegata nella sezione degli indicatori.")
    doc.svg(diagramma(d, True), diagramma(d, False),
            "Diagramma generato da docs/data/supply-chain-ai.json (%d nodi, %d collegamenti, %d colli di bottiglia). Passare sopra un riquadro per l'elenco dei colli." % (
                len(d["elementi"]), len(d["archi"]), len(d["colli"])), "sca-%s-catena.svg" % mese)
    righe = [["%d. %s" % (a["ordine"], a["nome"]), a["dove"], stato_md(dati_anello(d, a)[3] or "non misurato")] for a in d["anelli"]]
    doc.tab(["Anello", "Dove sta", "Collo peggiore"],
            [[r[0], r[1], cella_stato(dati_anello(d, a)[3] or "non misurato")] for r, a in zip(righe, d["anelli"])],
            "Versione in tabella del diagramma.")

    # --- Anelli
    n_sez = 3
    for a in d["anelli"]:
        ident = "anello-%s" % a["id"]
        doc.h2(ident, "%d. %s" % (n_sez, a["nome"]))
        n_sez += 1
        doc.p("**Dove sta.** " + a["dove"])
        doc.p("**Chi lo controlla.** " + a["chi_controlla"])
        for par in a["testo"]:
            if par.startswith("Valutazione: "):
                v = par[len("Valutazione: "):]
                doc.val(v[:1].upper() + v[1:])
            else:
                doc.p(par)
        if a["id"] == "materie":
            doc.h3("Produttori e quote (USGS, dati 2025)")
            rr = []
            for x in d["materie"]:
                if x.get("quote"):
                    q = x["quote"][:3]
                    quote = "; ".join("%s %s%%" % (y["nome_paese"], num(y["quota_pct"])) for y in q)
                elif x.get("quota_stima"):
                    quote = "stima: " + x["quota_stima"]["testo"]
                else:
                    quote = "dato mancante (" + (x.get("nota_quota") or "").split(".")[0] + ")"
                rr.append([x["nome"], x["uso_ai"], quote, "[%s](%s)" % (x["fonte"].split(": ")[-1], x["link"])])
            doc.tab(["Materia", "A cosa serve", "Primi produttori (quota)", "Fonte USGS"], rr,
                    "Quote calcolate da raccogli.py come produzione del paese / totale mondiale USGS (stime 2025); per il gallio la quota è quella dichiarata da USGS. Rame: estrazione; la Cina raffina il %s%% del rame mondiale." % num(mat["rame"]["quote_raffinazione"][0]["quota_pct"]))
            doc.svg(grafico_concentrazione(d, True), grafico_concentrazione(d, False),
                    "Quota del primo paese produttore. Fonte: [USGS Mineral Commodity Summaries 2026](https://pubs.usgs.gov/periodicals/mcs2026/mcs2026.pdf), 5 febbraio 2026.",
                    "sca-%s-concentrazione.svg" % mese)
            doc.h3("Controlli cinesi all'export, 2023–2026")
            rr = []
            for c in d["controlli"]:
                if c["paese"] != "CN":
                    continue
                stato = c["stato"] + (" fino al %s (%s)" % (data_it(c["scadenza"]), "tra 1 giorno" if c["giorni_alla_scadenza"] == 1 else "tra %d giorni" % c["giorni_alla_scadenza"]) if c.get("scadenza") else "")
                rr.append([data_it(c["data_annuncio"]), c["misura"], stato, fonte_md(c)])
            doc.tab(["Annuncio", "Misura", "Stato al %s" % data_it(rif), "Fonte"], rr,
                    "Per le misure di ottobre 2025 le fonti del 9 novembre 2026 sono in disaccordo: vedi il testo sopra.")
        if a["id"] == "attrezzature":
            doc.h3("Regole sull'export di macchine e chip (USA, Paesi Bassi, Giappone)")
            rr = []
            for c in d["controlli"]:
                if c["paese"] == "CN" or not ({"attrezzature", "progettazione", "packaging-memoria"} & set(c["anelli"])):
                    continue
                stato = c["stato"] + (" fino al %s" % data_it(c["scadenza"]) if c.get("scadenza") else "")
                rr.append([PAESI.get(c["paese"], c["paese"]), data_it(c["data_effetto"] or c["data_annuncio"]) if (c["data_effetto"] or c["data_annuncio"] or "").count("-") == 2 else (c["data_effetto"] or c["data_annuncio"]), c["misura"], stato, fonte_md(c)])
            doc.tab(["Paese", "Dal", "Misura", "Stato", "Fonte"], rr)
        # nodi
        nn = [n for n in d["elementi"] if n["anello"] == a["id"]]
        doc.h3("Dove sono i nodi")
        doc.tab(["Nodo", "Paese", "Ruolo", "Quota o peso", "Fonte (affidabilità)"],
                [[n["nome"], PAESI.get(n["paese"], n["paese"]), n.get("ruolo") or "—", n.get("quota") or "—",
                  "%s, %s (%s)" % (fonte_md(n), n.get("data_fonte", "—"), n.get("affidabilita", "—"))] for n in nn],
                "Coordinate nel file di dati (precisione indicata per ogni punto).")
        # colli
        cc = [c for c in d["colli"] if c["anello"] == a["id"]]
        if cc:
            doc.h3("Colli di bottiglia e indicatori")
            rr = []
            for c in cc:
                for i in c["indicatori"]:
                    soglia = "%s / %s %s" % (num(i.get("soglia_attenzione"), 0), num(i.get("soglia_critica"), 0), i.get("unita", ""))
                    val = "%s %s" % (num(i["valore"]) if isinstance(i["valore"], float) else num(i["valore"], 0), i.get("unita", ""))
                    rr.append([c["nome"], i["nome"], val.strip(), soglia, cella_stato(i["stato"]),
                               "%s, %s" % (fonte_md(i), i.get("data") or "—")])
            doc.tab(["Collo", "Indicatore", "Valore", "Soglie (attenzione / critico)", "Stato", "Fonte"], rr)
            for c in cc:
                doc.p("**%s.** %s" % (c["nome"], c["perche"]))
        # titoli
        tt = [t for t in d["titoli"] if a["id"] in t["anelli"]]
        if tt:
            doc.h3("Titoli collegati")
            rr = []
            for t in tt:
                ult, m1, ytd, a1 = prezzo_txt(t)
                rr.append(["%s (%s)" % (t["nome"], t["simbolo"]), t["ruolo"], ult, m1, ytd, a1])
            doc.tab(["Titolo", "Ruolo nella catena", "Ultimo", "1 mese", "Da inizio anno", "1 anno"], rr,
                    "Prezzi da prezzi.json (Yahoo Finance, chiusure al %s; * = serie provvisoria). «non seguito»: titolo non ancora in prezzi.json." % data_it(sox.get("data")))
        doc.p("**Indicatori da seguire:** " + "; ".join(a["indicatori"]) + ".")

    # --- Logistica: collegamenti
    doc.h2("collegamenti", "%d. Come si spostano le cose: i collegamenti" % n_sez)
    n_sez += 1
    doc.p("Ogni riga è un arco «da → a» del file di dati. Le righe marcate *valutazione* sono percorsi tipici ricostruiti dall'osservatorio (per esempio l'aeroporto usato), non tracciati reali: le società non pubblicano le rotte.")
    rr = []
    for x in d["archi"]:
        via = (" via " + ", ".join(nodi[v]["nome"] for v in x.get("via", []))) if x.get("via") else ""
        rr.append(["%s → %s" % (x["da_nome"], x["a_nome"]), x["cosa"] + via, x["modo"], x["stato"], x["tipo"], num(x["km"], 0)])
    doc.tab(["Da → a", "Cosa", "Modo", "Stato", "Tipo", "km in linea d'aria"], rr)

    # --- Paesi Bassi, Danimarca, Baltico
    doc.h2("nord-europa", "%d. Paesi Bassi, Danimarca e Baltico" % n_sez)
    n_sez += 1
    reti = {r["nodo"]: r for r in d["legami"]["rete_380kv"]}
    def rete(nid):
        r = reti.get(nid)
        return ("a %s km da una linea da %s" % (num(r["km"]), r["linea"])) if r else "distanza dalla rete non calcolata"
    gl = mat["terre-rare"].get("riserve", {}).get("GL")
    doc.ul([
        "**Veldhoven (ASML)** è il nodo più critico della catena che si trovi in Europa: unico produttore di EUV, %s (rete-elettrica.json). Le macchine partono smontate verso Taiwan, Corea, Giappone e USA; per via aerea l'uscita naturale è Schiphol (valutazione: ASML non pubblica gli aeroporti)." % rete("veldhoven"),
        "**Schiphol** è quindi un punto logistico della catena dell'AI oltre che dei fiori e della farmaceutica: un ritardo lì rallenta le nuove fab nel mondo, non la produzione corrente.",
        "**Nexperia (Nijmegen)** mostra il rischio opposto: un intervento dello Stato olandese (settembre 2025) e la risposta cinese hanno spezzato una catena Europa–Cina. Non tocca i chip AI, ma è il precedente da tenere a mente per ASML.",
        "**Regole olandesi.** Le licenze su DUV dal 2023 e 2024 sono olandesi; la proposta americana MATCH Act e le pressioni su assistenza e ricambi in Cina sono il prossimo fronte.",
        "**Danimarca e Groenlandia.** La Groenlandia ha %s tonnellate di riserve di terre rare (USGS) e nessuna produzione: è un'opzione di lungo periodo, non un'offerta. Gli Stretti danesi non sono una rotta della catena dei chip." % (num(gl, 0) if gl else "—"),
        "**Baltico.** In Estonia, a Sillamäe (%s) e Narva (%s), Neo Performance Materials separa terre rare (anche terbio e disprosio dal 2026) e produce magneti: il tratto di filiera europea più completo fuori dalla Cina, a pochi chilometri dal confine russo. Rischio da seguire: sicurezza della zona di confine e dei cavi del Baltico (livello cavi-incidenti)." % (rete("sillamae"), rete("narva")),
    ])

    # --- Scenari
    doc.h2("scenari", "%d. Scenari di rottura" % n_sez)
    n_sez += 1
    doc.p("Ragionamenti dell'osservatorio, non previsioni. Per ogni scenario: cosa si ferma per primo e quale indicatore lo segnala.")
    doc.tab(["Scenario", "Cosa si ferma per primo", "Segnale da guardare"], [
        ["Blocco navale di Taiwan", "Il GNL (scorte 12–14 giorni) e quindi l'elettricità delle fab; poi l'uscita di wafer, CoWoS e server. Gli aerei cargo potrebbero continuare per un po'.", "Transiti PortWatch nello Stretto di Taiwan e di Luzon; esercitazioni; cavi tagliati"],
        ["Conflitto aperto su Taiwan", "Tutta la fonderia avanzata e il packaging: nessun sostituto per anni (Arizona fa 4 nm, packaging AP1 dal 2028).", "Come sopra; TSM e SOX in borsa"],
        ["Hormuz chiuso a lungo (in corso)", "L'elio del Qatar (un terzo del mondo) e il GNL che alimenta Taiwan, Corea e Giappone; prezzi dell'energia europei.", "Transiti a Hormuz; TTF; notizie su Ras Laffan"],
        ["Ritorno dei controlli cinesi di ottobre 2025", "Magneti e componenti con terre rare cinesi oltre lo 0,1% del valore: motori, ventole, dischi rigidi; impianti di separazione fuori dalla Cina.", "Testo MOFCOM dopo il 10 novembre; licenze e dati doganali"],
        ["Stretta USA sulle DUV e sull'assistenza in Cina", "Ricavi ASML dalla Cina (circa un quinto); risposta cinese con terre rare e gallio.", "MATCH Act; decisioni dell'Aia; conti ASML"],
        ["Uragano a Spruce Pine", "Quarzo per i crogioli: scorte di alcuni mesi, poi meno wafer.", "Stagione degli uragani; forza maggiore Sibelco o The Quartz Corp"],
    ])

    # --- Indicatori complessivi
    doc.h2("indicatori", "%d. Tutti gli indicatori e le soglie" % n_sez)
    n_sez += 1
    doc.p("Le soglie sono una **valutazione dell'osservatorio**, scelte per distinguere una situazione normale da una da seguire; non sono valori ufficiali. Indicatori *strutturali* (concentrazione) cambiano in anni e restano spesso «critici»: dicono dove si romperebbe la catena, non che si stia rompendo. Gli indicatori *congiunturali* si muovono in settimane.")
    rr = []
    for c in d["colli"]:
        for i in c["indicatori"]:
            val = "%s %s" % (num(i["valore"]) if isinstance(i["valore"], float) else num(i["valore"], 0), i.get("unita", ""))
            rr.append([c["nome"], i["nome"], i.get("tipo", "—"), val.strip(), cella_stato(i["stato"])])
    doc.tab(["Collo", "Indicatore", "Tipo", "Valore", "Stato"], rr)
    cong = {}
    for c in d["colli"]:
        cong[c["stato_congiunturale"]] = cong.get(c["stato_congiunturale"], 0) + 1
    doc.p("Riepilogo: su %d colli di bottiglia, guardando solo gli indicatori congiunturali, %d sono critici, %d in attenzione, %d normali o non misurati." % (
        len(d["colli"]), cong.get("critico", 0), cong.get("attenzione", 0), len(d["colli"]) - cong.get("critico", 0) - cong.get("attenzione", 0)))

    # --- Metodo
    doc.h2("metodo", "%d. Metodo, limiti e trasparenza" % n_sez)
    doc.ul([
        "**Dati.** Il file docs/data/supply-chain-ai.json è costruito da raccolta/supply-chain-ai/raccogli.py a partire da voci curate a mano (raccolta/supply-chain-ai/*.json), ciascuna con fonte, link, data e affidabilità, e da altri file dell'osservatorio (ai.json, ai-mondo.json, stretti-dettaglio.json, portwatch.json, prezzi.json, cavi-incidenti.json, rete-elettrica.json, cavi.json). Le quote dei paesi sono calcolate dalle tabelle USGS; i giorni alle scadenze e lo stato degli indicatori sono calcolati dallo script.",
        "**Coordinate.** I nodi nuovi sono geocodificati con OpenStreetMap Nominatim a livello di comune, sede o sito (precisione nel file); quelli già presenti nella mappa riusano le coordinate di ai.json e ai-mondo.json. Il punto di una sede non è la posizione di un impianto.",
        "**Limiti.** Mancano da fonte verificata: quote per nodo tecnologico (3 nm, 2 nm), quote di mercato dei singoli fornitori di macchine, quota attuale del neon ucraino, volumi di cargo AI per aeroporto, quota mondiale del germanio e del polisilicio. Le quote dei chip AI (Nvidia, ASIC) e dei moduli ottici variano molto tra le fonti. Alcune fonti di stampa secondaria hanno affidabilità bassa e sono marcate.",
        "**Non è un consiglio di investimento.** I titoli sono collegati agli anelli per leggere la catena attraverso i mercati.",
        "**Uso di un assistente AI e trasparenza.** Questo report è stato scritto con l'aiuto di un assistente AI: chi scrive è Claude, un modello di Anthropic, sotto la cura e la responsabilità di Gabriele Giuliani. Anthropic è un cliente di questa catena: usa chip, server e data center descritti qui (per esempio il campus Amazon di New Carlisle). I dati che la riguardano vengono solo da fonti pubbliche e sono trattati come gli altri; nessuna valutazione è stata orientata a suo favore.",
    ])
    return titolo, doc


CSS = """:root{--paper:#F6F5F0;--card:#FFFFFF;--ink:#1D272D;--soft:#52606A;--faint:#86929A;--rule:#DCDFDD;--accent:#A61E6B;--band:#ECE9E0;
--ok:#0ca30c;--warn:#b47d00;--crit:#d03b3b;color-scheme:light dark}
@media (prefers-color-scheme:dark){:root{--paper:#10181D;--card:#172127;--ink:#DAE0E2;--soft:#A0ABB1;--faint:#6C787F;--rule:#2B373E;--accent:#d14f9a;--band:#1A252C;--ok:#3fbf3f;--warn:#fab219;--crit:#e5605f}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 "IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
.pagina{max-width:70ch;margin:0 auto;padding:24px 16px 64px}
a{color:var(--accent);text-underline-offset:2px;overflow-wrap:anywhere}
a:hover{text-decoration-thickness:2px}
.torna{display:inline-block;font-size:14px;margin-bottom:24px;text-decoration:none}
.torna:hover{text-decoration:underline}
.occhiello{font:600 13px/1.4 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:0 0 8px}
h1{font:600 clamp(28px,5vw,40px)/1.15 "IBM Plex Serif",Georgia,serif;margin:0 0 12px;letter-spacing:-.01em}
.sottotitolo{font-size:18px;color:var(--soft);margin:0 0 16px}
.meta{font-size:14px;color:var(--soft);border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);padding:10px 0;margin:0 0 28px}
h2{font:600 24px/1.25 "IBM Plex Serif",Georgia,serif;margin:48px 0 12px;padding-top:8px;scroll-margin-top:16px}
h3{font:600 18px/1.3 "IBM Plex Sans",sans-serif;margin:28px 0 8px}
p,ul{margin:0 0 16px}
ul{padding-left:1.2em}
li{margin:0 0 8px}
strong{font-weight:600}
nav.indice{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:14px 18px;margin:0 0 8px}
nav.indice h2{font:600 13px/1.4 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;margin:0 0 6px;padding:0;color:var(--soft)}
nav.indice ol{margin:0;padding-left:1.4em;columns:2;column-gap:28px;font-size:15px}
nav.indice li{margin:0 0 4px;break-inside:avoid}
@media (max-width:560px){nav.indice ol{columns:1}}
.valutazione{border-left:3px solid var(--accent);background:var(--band);padding:10px 14px;margin:0 0 18px;border-radius:0 6px 6px 0;font-size:16px}
.valutazione .etichetta{font:600 12px/1 "IBM Plex Mono",monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);display:block;margin-bottom:6px}
.tabella{overflow-x:auto;margin:0 0 16px;-webkit-overflow-scrolling:touch;border:1px solid var(--rule);border-radius:6px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
th,td{padding:7px 10px;text-align:left;vertical-align:top;border-bottom:1px solid var(--rule)}
th{font-weight:600;color:var(--soft);background:var(--band)}
td{min-width:7ch}
tr:last-child td{border-bottom:0}
td:first-child{font-weight:500}
.nota{font-size:13px;color:var(--soft);margin:-8px 0 20px}
figure{margin:20px 0 22px}
figure .grafico{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:14px}
figcaption{font-size:13px;color:var(--soft);margin-top:8px}
.stretto{display:none}
@media (max-width:600px){.largo{display:none}.stretto{display:block}figure .grafico{padding:8px}}
.stato{white-space:nowrap}
.s-normale::before{content:"● ";color:var(--ok)}
.s-attenzione::before{content:"▲ ";color:var(--warn)}
.s-critico::before{content:"■ ";color:var(--crit)}
footer{margin-top:56px;padding-top:16px;border-top:1px solid var(--rule);font-size:14px;color:var(--soft)}
footer .firma{font-weight:600;color:var(--ink)}"""


def pagina_html(titolo, doc, d, mese):
    sezioni = [(b[1], b[2]) for b in doc.b if b[0] == "h2"]
    indice = "".join('<li><a href="#%s">%s</a></li>' % (i, html.escape(re.sub(r"^\d+\. ", "", t))) for i, t in sezioni)
    anno, m = mese.split("-")
    return """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catena dell'AI — %(mese_it)s</title>
<meta name="description" content="La catena del valore dell'AI dalla miniera al data center: dove sta ogni anello, chi lo controlla, colli di bottiglia, rischi geopolitici e logistici, indicatori e titoli collegati.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@600&display=swap" rel="stylesheet">
<style>
%(css)s
</style>
</head>
<body>
<main class="pagina">
<a class="torna" href="../index.html">← Torna alla mappa</a>
<p class="occhiello">Report supply chain dell'AI · %(mese_it)s</p>
<h1>%(titolo)s</h1>
<p class="sottotitolo">Otto anelli, dalle miniere di gallio e terre rare alle macchine EUV di Veldhoven, alle fab di Taiwan, ai data center: dove sono, chi li controlla, dove si rompono.</p>
<p class="meta">Gabriele Giuliani · Monitor geoeconomico · dati al %(rif)s. Ogni numero ha fonte e data; i riquadri <em>Valutazione</em> sono ragionamenti dell'osservatorio, non fatti. Dati: <a href="../data/supply-chain-ai.json">supply-chain-ai.json</a>.</p>
<nav class="indice" aria-label="Indice"><h2>Indice</h2><ol>%(indice)s</ol></nav>
%(corpo)s
<footer><p class="firma">Gabriele Giuliani · Monitor geoeconomico</p>
<p>Scritto con l'aiuto di un assistente AI (Claude, modello di Anthropic; Anthropic è un cliente della catena descritta). Dati generati il %(agg)s da raccolta/supply-chain-ai/raccogli.py; report da report/costruisci_supply_chain_ai.py. <a href="../index.html">Torna alla mappa</a></p></footer>
</main>
</body>
</html>
""" % {"mese_it": "%s %s" % (MESI[int(m) - 1], anno), "css": CSS, "titolo": html.escape(titolo), "rif": data_it(d["data_riferimento"]),
       "indice": indice, "corpo": doc.html(), "agg": d["aggiornato"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mese", help="AAAA-MM (predefinito: mese della data di riferimento dei dati)")
    a = ap.parse_args()
    with open(DATI, encoding="utf-8") as f:
        d = json.load(f)
    if d.get("errori"):
        raise SystemExit("il file di dati ha errori di validazione: rilanciare raccogli.py")
    mese = a.mese or d["data_riferimento"][:7]
    titolo, doc = costruisci(d, mese)
    md = "# %s\n\n*Dove sta ogni anello della catena dell'AI, chi lo controlla, dove si rompe.*\n\nGabriele Giuliani · Monitor geoeconomico · dati al %s. Ogni numero ha fonte e data; le parti marcate *Valutazione* sono ragionamenti dell'osservatorio.\n\n## Indice\n%s\n\n%s\n---\n\nGabriele Giuliani · Monitor geoeconomico. Scritto con l'aiuto di un assistente AI (Claude, modello di Anthropic; Anthropic è un cliente della catena descritta).\n" % (
        titolo, data_it(d["data_riferimento"]),
        "\n".join("- [%s](#%s)" % (b[2], b[1]) for b in doc.b if b[0] == "h2"), doc.md())
    for b in doc.b:
        if b[0] == "svg":
            with open(os.path.join(RADICE, "report", "grafici", b[4]), "w", encoding="utf-8") as f:
                f.write(b[1].replace('<svg class="viz"', '<svg class="viz"', 1) + "\n")
    p_md = os.path.join(RADICE, "report", "supply-chain-ai-%s.md" % mese)
    p_html = os.path.join(RADICE, "docs", "report", "supply-chain-ai-%s.html" % mese)
    with open(p_md, "w", encoding="utf-8") as f:
        f.write(md)
    with open(p_html, "w", encoding="utf-8") as f:
        f.write(pagina_html(titolo, doc, d, mese))
    print("scritti %s e %s" % (os.path.relpath(p_md, RADICE), os.path.relpath(p_html, RADICE)))


if __name__ == "__main__":
    main()
