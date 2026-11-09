#!/usr/bin/env python3
"""Costruisce i grafici SVG del report «Hormuz e Mar Rosso» dai dati in docs/data/.

Solo libreria standard di Python 3. Uso, dalla radice del repository:

    python3 report/costruisci_grafici.py

Cosa fa:
1. legge portwatch.json, prezzi.json, gas-italia.json e paesi.json;
2. disegna quattro grafici in SVG, ognuno in due larghezze (pagina larga e telefono);
3. salva gli SVG in report/grafici/ (per il testo Markdown);
4. inserisce gli SVG nella pagina docs/report/hormuz-mar-rosso-2026-11.html, tra i
   segnaposto <!-- grafico:NOME inizio --> e <!-- grafico:NOME fine -->.

Nessun numero è scritto a mano nei grafici: valori, date e quote vengono dai file JSON.
Le sole cose scritte qui sono le date degli eventi da segnare sui grafici, ognuna con
la sua fonte (vedi EVENTI_*), e le scelte di stile.
"""

import datetime as dt
import html
import json
import os
import re
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(RADICE, "docs", "data")
CARTELLA_SVG = os.path.join(RADICE, "report", "grafici")
PAGINA = os.path.join(RADICE, "docs", "report", "hormuz-mar-rosso-2026-11.html")

MESI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]

# Colori: categorici validati (dataviz, controllo CVD e contrasto) in chiaro e in scuro.
# s1 = accento del progetto (Hormuz), s2 = arancio, s3 = blu. Brent e TTF usano i colori
# di petrolio e gas della mappa. Tutto passa da variabili CSS, così il tema scuro funziona
# sia dentro la pagina sia aprendo l'SVG da solo.
STILE = """
.viz{--v-s1:#A61E6B;--v-s2:#eb6834;--v-s3:#2a78d6;--v-oil:#4B3B2B;--v-gas:#7A55B5;
--v-ink:#1D272D;--v-soft:#52606A;--v-faint:#86929A;--v-grid:#DCDFDD;--v-bg:#F6F5F0;--v-band:#ECE9E0;
font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif}
@media (prefers-color-scheme:dark){.viz{--v-s1:#d14f9a;--v-s2:#d95926;--v-s3:#3987e5;--v-oil:#C8B08E;--v-gas:#B9A0F0;
--v-ink:#DAE0E2;--v-soft:#A0ABB1;--v-faint:#6C787F;--v-grid:#2B373E;--v-bg:#10181D;--v-band:#1A252C}}
.viz text{fill:var(--v-soft);font-size:var(--fs,12px)}
.viz .t-ink{fill:var(--v-ink)}.viz .t-b{font-weight:600}.viz .t-faint{fill:var(--v-faint)}
.viz .num{font-variant-numeric:tabular-nums}
.viz .grid{stroke:var(--v-grid);stroke-width:1}
.viz .base{stroke:var(--v-faint);stroke-width:1}
.viz .ev{stroke:var(--v-faint);stroke-width:1;stroke-dasharray:3 3}
.viz .band{fill:var(--v-band)}
.viz .l{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.viz .c-s1{stroke:var(--v-s1)}.viz .c-s2{stroke:var(--v-s2)}.viz .c-s3{stroke:var(--v-s3)}
.viz .c-oil{stroke:var(--v-oil)}.viz .c-gas{stroke:var(--v-gas)}
.viz .f-s1{fill:var(--v-s1)}.viz .f-s2{fill:var(--v-s2)}.viz .f-s3{fill:var(--v-s3)}
.viz .f-oil{fill:var(--v-oil)}.viz .f-gas{fill:var(--v-gas)}
.viz .ring{stroke:var(--v-bg);stroke-width:2}
.viz .hit{fill:transparent}.viz .hit:hover{fill:var(--v-ink);fill-opacity:.06}
.viz .badge{fill:var(--v-bg);stroke:var(--v-faint);stroke-width:1}
"""


# ---------------------------------------------------------------- utilità

def leggi(nome):
    with open(os.path.join(DATI, nome), encoding="utf-8") as f:
        return json.load(f)


def data(s):
    return dt.date.fromisoformat(s[:10])


def num(v, dec=1):
    """Numero all'italiana: virgola decimale, punto per le migliaia."""
    s = f"{v:,.{dec}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def data_it(d, anno=True):
    return f"{d.day} {MESI[d.month - 1]}" + (f" {d.year}" if anno else "")


def esc(s):
    return html.escape(str(s), quote=True)


def media_mobile(serie, n=7):
    """Media mobile su n giorni di calendario, solo dove ci sono n valori."""
    valori = {data(d): v for d, v in serie}
    giorni = sorted(valori)
    out = []
    for g in giorni:
        fin = [valori.get(g - dt.timedelta(days=i)) for i in range(n)]
        if all(x is not None for x in fin):
            out.append((g, sum(fin) / n))
    return out


class Scala:
    def __init__(self, d0, d1, r0, r1):
        self.d0, self.d1, self.r0, self.r1 = d0, d1, r0, r1

    def __call__(self, v):
        if isinstance(v, dt.date):
            v = v.toordinal()
            a, b = self.d0.toordinal(), self.d1.toordinal()
        else:
            a, b = self.d0, self.d1
        return self.r0 + (v - a) / (b - a) * (self.r1 - self.r0)


def tacche(maxv, n=5):
    passi = [1, 2, 2.5, 5, 10, 20, 25, 50, 100, 200, 250, 500]
    for p in passi:
        if maxv / p <= n:
            return [i * p for i in range(int(maxv // p) + 2) if i * p <= maxv * 1.0001 + p * 0.0001]
    return [0, maxv]


def percorso(punti):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in punti)


def svg_apri(w, h, titolo, descr, id_):
    return [
        f'<svg class="viz" id="{id_}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="100%" role="img" aria-labelledby="{id_}-t {id_}-d" style="max-width:{w}px;height:auto;display:block">',
        f'<title id="{id_}-t">{esc(titolo)}</title><desc id="{id_}-d">{esc(descr)}</desc>',
        f"<style>{STILE}</style>",
    ]


def legenda(x, y, voci, fs):
    """voci: lista di (classe_colore, testo). Linea corta + testo, in riga."""
    out, cx = [], x
    for cls, testo in voci:
        out.append(f'<line x1="{cx}" y1="{y - fs * .35:.1f}" x2="{cx + 16}" y2="{y - fs * .35:.1f}" class="l {cls}" style="stroke-width:3"/>')
        out.append(f'<text x="{cx + 21}" y="{y}" class="t-ink">{esc(testo)}</text>')
        cx += 21 + len(testo) * fs * 0.56 + 18
    return out


def asse_mesi(sx, d0, d1, y, fs, ogni, anno_sempre=False):
    """Etichette di mese sull'asse x; l'anno compare a gennaio e sulla prima etichetta."""
    out = []
    g = dt.date(d0.year, d0.month, 1)
    if g < d0:
        g = dt.date(g.year + (g.month == 12), g.month % 12 + 1, 1)
    primo = True
    while g <= d1:
        if (g.month - 1) % ogni == 0:
            x = sx(g)
            out.append(f'<line x1="{x:.1f}" y1="{y - 4}" x2="{x:.1f}" y2="{y}" class="base"/>')
            lab = MESI[g.month - 1]
            gen_vicino = primo and g.month != 1 and (13 - g.month) <= 6 and dt.date(g.year + 1, 1, 1) <= d1
            if g.month == 1 or anno_sempre or (primo and not gen_vicino):
                lab += f" {g.year}"
            out.append(f'<text x="{x:.1f}" y="{y + fs + 2}" text-anchor="middle" class="num">{esc(lab)}</text>')
            primo = False
        g = dt.date(g.year + (g.month == 12), g.month % 12 + 1, 1)
    return out


def badge_eventi(xs, y_top, y_fondo, cy=None, verso=-1):
    """Linee tratteggiate e cerchietti numerati; se due cerchi si toccano, il secondo si sposta
    di una riga (verso l'alto con verso=-1, verso il basso con verso=+1)."""
    out, prec_x, livello = [], -99, 0
    cy = y_top - 8 if cy is None else cy
    for x, i in xs:
        livello = livello + 1 if x - prec_x < 17 else 0
        c = cy + verso * livello * 17
        out.append(f'<line x1="{x:.1f}" y1="{c + 8:.1f}" x2="{x:.1f}" y2="{y_fondo}" class="ev"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{c:.1f}" r="8" class="badge"/>'
                   f'<text x="{x:.1f}" y="{c + 4:.1f}" text-anchor="middle" class="t-ink t-b" style="font-size:11px">{i}</text>')
        prec_x = x
    return out


# ---------------------------------------------------------------- grafico 1: transiti

EVENTI_TRANSITI = [
    # (data, etichetta breve, fonte) – le fonti sono citate nel testo del report
    ("2026-03-02", "Hormuz chiuso di fatto", "stretti-dettaglio.json (IEA, Howden Re)"),
    ("2026-06-18", "blocco USA sospeso", "report.json (RFE/RL, CENTCOM)"),
    ("2026-07-20", "Houthi: blocco navi saudite", "energia.md (AP)"),
]


def grafico_transiti(pw, W):
    stretto = W < 500
    fs = 13 if stretto else 12
    H = 440 if stretto else 400
    ml, mr, mt, mb = (34, 14, 84, 34) if stretto else (40, 132, 78, 34)
    d0 = dt.date(2023, 10, 1)
    serie = {}
    nomi = {"chokepoint6": ("Hormuz", "c-s1", "f-s1"), "chokepoint4": ("Bab el-Mandeb", "c-s2", "f-s2"),
            "chokepoint1": ("Suez", "c-s3", "f-s3")}
    ultima = None
    for e in pw["elementi"]:
        if e["id"] in nomi:
            mm = [(g, v) for g, v in media_mobile(e["serie"]["n_total"]) if g >= d0]
            serie[e["id"]] = mm
            ultima = mm[-1][0]
    d1 = ultima
    maxv = max(v for s in serie.values() for _, v in s)
    yt = tacche(maxv * 1.05, 6)
    ymax = yt[-1] if yt[-1] >= maxv else yt[-1] + (yt[1] - yt[0])
    sx = Scala(d0, d1, ml, W - mr)
    sy = Scala(0, ymax, H - mb, mt)
    titolo = "Transiti giornalieri a Hormuz, Bab el-Mandeb e Suez (media 7 giorni)"
    descr = (f"Navi al giorno, media mobile a 7 giorni, da {data_it(d0)} a {data_it(d1)}. "
             + "; ".join(f"{nomi[k][0]}: {num(serie[k][-1][1])} all'ultima data" for k in nomi)
             + ". Fonte: IMF PortWatch.")
    o = svg_apri(W, H, titolo, descr, f"g-transiti-{W}")
    o.append(f'<g style="--fs:{fs}px">')
    # sfondo: periodo di chiusura di Hormuz
    xa = sx(data(EVENTI_TRANSITI[0][0]))
    o.append(f'<rect x="{xa:.1f}" y="{mt}" width="{W - mr - xa:.1f}" height="{H - mb - mt}" class="band"/>')
    for t in yt:
        y = sy(t)
        o.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{W - mr}" y2="{y:.1f}" class="{"base" if t == 0 else "grid"}"/>')
        o.append(f'<text x="{ml - 6}" y="{y + 4:.1f}" text-anchor="end" class="num">{num(t, 0)}</text>')
    o += asse_mesi(sx, d0, d1, H - mb + 4, fs, 6 if stretto else 3)
    # eventi
    o += badge_eventi([(sx(data(d)), i) for i, (d, _l, _f) in enumerate(EVENTI_TRANSITI, 1)], mt - 4, H - mb)
    # linee
    for k, (nome, c, f) in nomi.items():
        pts = [(sx(g), sy(v)) for g, v in serie[k]]
        o.append(f'<path d="{percorso(pts)}" class="l {c}"/>')
        x, y = pts[-1]
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" class="{f} ring"/>')
    # etichette a fine linea (solo pagina larga; sul telefono legenda sopra)
    if not stretto:
        fine = sorted(((sy(serie[k][-1][1]), k) for k in nomi))
        ys, prec = [], -99
        for y, k in fine:
            y = max(y, prec + fs + 4)
            ys.append((y, k)); prec = y
        for y, k in ys:
            v = serie[k][-1][1]
            o.append(f'<text x="{W - mr + 10}" y="{y + 4:.1f}" class="t-ink"><tspan class="t-b">{esc(nomi[k][0])}</tspan> '
                     f'<tspan class="num">{num(v)}</tspan></text>')
    o += legenda(ml if stretto else ml, 16, [(nomi[k][1], nomi[k][0]) for k in nomi], fs)
    o.append(f'<text x="{ml}" y="{16 + fs + 8}" class="t-faint">navi al giorno · in grigio: Hormuz chiuso di fatto</text>')
    # livello di contatto: un rettangolo per settimana con i tre valori
    sett = {}
    for k in nomi:
        for g, v in serie[k]:
            if g.weekday() == 6:
                sett.setdefault(g, {})[k] = v
    giorni = sorted(sett)
    for i, g in enumerate(giorni):
        x0 = sx(g - dt.timedelta(days=3.5)); x1 = sx(g + dt.timedelta(days=3.5))
        testo = f"settimana al {data_it(g)} — " + ", ".join(f"{nomi[k][0]} {num(sett[g].get(k, float('nan')))}" for k in nomi)
        o.append(f'<rect x="{max(x0, ml):.1f}" y="{mt}" width="{min(x1, W - mr) - max(x0, ml):.1f}" height="{H - mb - mt}" class="hit"><title>{esc(testo)}</title></rect>')
    o.append("</g></svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- grafico 2: Brent e TTF

EVENTI_PREZZI = [
    ("2026-03-02", "Hormuz chiuso di fatto; 4 mar forza maggiore a Ras Laffan"),
    ("2026-04-08", "tregua Iran-USA"),
    ("2026-06-18", "blocco USA dei porti iraniani sospeso (ripreso il 14 luglio)"),
    ("2026-09-11", "droni fermano l'oleodotto saudita Est-Ovest (11–13 set)"),
    ("2026-10-29", "massimi d'autunno di Brent e TTF"),
    ("2026-11-09", "mediazione del Qatar a Washington"),
]


def grafico_prezzi(pr, W):
    stretto = W < 500
    fs = 13 if stretto else 12
    serie = {s["id"]: s for s in pr["serie"]}
    br = [(data(d), v) for d, v in serie["brent"]["serie"]]
    tt = [(data(d), v) for d, v in serie["ttf"]["serie"]]
    d0 = min(br[0][0], tt[0][0]); d1 = max(br[-1][0], tt[-1][0])
    ml, mr = (34, 14) if stretto else (40, 20)
    top = 50 if stretto else 30
    ph = 150 if stretto else 135
    gap = 52
    H = top + 2 * ph + gap + 40
    sx = Scala(d0, d1, ml, W - mr)
    titolo = "Brent e TTF nell'ultimo anno, con gli eventi principali"
    descr = (f"Chiusure giornaliere da {data_it(d0)} a {data_it(d1)}. Brent ultimo {num(br[-1][1], 2)} dollari al barile, "
             f"TTF ultimo {num(tt[-1][1], 2)} euro al MWh. Fonte: Yahoo Finance tramite prezzi.json.")
    o = svg_apri(W, H, titolo, descr, f"g-prezzi-{W}")
    o.append(f'<g style="--fs:{fs}px">')
    pannelli = [("Brent", "dollari al barile", br, "c-oil", "f-oil", top + 16),
                ("TTF", "euro al MWh", tt, "c-gas", "f-gas", top + 16 + ph + gap)]
    for nome, unita, s, c, f, y0 in pannelli:
        maxv = max(v for _, v in s)
        yt = tacche(maxv, 4)
        if yt[-1] < maxv * 1.15:
            yt.append(yt[-1] + (yt[1] - yt[0]))
        sy = Scala(0, yt[-1], y0 + ph, y0)
        o.append(f'<text x="{ml}" y="{y0 - 10}" class="t-ink"><tspan class="t-b">{nome}</tspan> · {unita}</text>')
        for t in yt:
            y = sy(t)
            o.append(f'<line x1="{ml}" y1="{y:.1f}" x2="{W - mr}" y2="{y:.1f}" class="{"base" if t == 0 else "grid"}"/>')
            o.append(f'<text x="{ml - 6}" y="{y + 4:.1f}" text-anchor="end" class="num">{num(t, 0)}</text>')
        xs = [(sx(data(d)), i) for i, (d, _lab) in enumerate(EVENTI_PREZZI, 1)]
        if nome == "Brent":
            o += badge_eventi(xs, top, y0 + ph, 12 if stretto else top - 8, +1 if stretto else -1)
        else:
            o += [f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0 + ph}" class="ev"/>' for x, _i in xs]
        pts = [(sx(d), sy(v)) for d, v in s]
        o.append(f'<path d="{percorso(pts)}" class="l {c}"/>')
        # massimo e ultimo valore
        dm, vm = max(s, key=lambda p: p[1])
        xm, ym = sx(dm), sy(vm)
        o.append(f'<circle cx="{xm:.1f}" cy="{ym:.1f}" r="4" class="{f} ring"/>')
        anc = "end" if xm > W * 0.6 else "start"
        dxm = -2 if anc == "end" else -6
        testo_max = f"massimo {num(vm, 2)} ({data_it(dm, False)})" if not stretto else f"max {num(vm, 1)}"
        o.append(f'<text x="{xm + dxm:.1f}" y="{ym - 9:.1f}" text-anchor="{anc}" class="t-ink num">{testo_max}</text>')
        dl, vl = s[-1]
        xl, yl = sx(dl), sy(vl)
        o.append(f'<circle cx="{xl:.1f}" cy="{yl:.1f}" r="4" class="{f} ring"/>')
        o.append(f'<text x="{xl - 7:.1f}" y="{yl + fs + 8:.1f}" text-anchor="end" class="t-ink num t-b">{num(vl, 2)}</text>')
        # contatto: un rettangolo per settimana
        per_sett = {}
        for d, v in s:
            per_sett[d - dt.timedelta(days=d.weekday())] = (d, v)
        for lun, (d, v) in sorted(per_sett.items()):
            x0, x1 = sx(lun), sx(lun + dt.timedelta(days=7))
            x0, x1 = max(x0, ml), min(x1, W - mr)
            if x1 <= x0:
                continue
            o.append(f'<rect x="{x0:.1f}" y="{y0}" width="{x1 - x0:.1f}" height="{ph}" class="hit">'
                     f'<title>{esc(nome)} {num(v, 2)} il {data_it(d)}</title></rect>')
    o += asse_mesi(sx, d0, d1, H - 30, fs, 3 if stretto else 2)
    o.append("</g></svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- grafico 3: gas in Italia

def grafico_gas(gi, W):
    stretto = W < 500
    fs = 13 if stretto else 12
    tipo = {e["id"]: e["categoria"] for e in gi["elementi"]}
    prov = {e["id"]: e.get("provenienza", "") for e in gi["elementi"]}
    righe = sorted(gi["quote_12_mesi"], key=lambda r: -r["quota_ingressi_pct"])
    corto = {"mazara": "Mazara del Vallo (Algeria)", "melendugno": "Melendugno, TAP (Azerbaigian)",
             "adriatic": "Adriatic LNG, Rovigo (GNL)", "gries": "Passo Gries (Nord Europa)",
             "piombino": "Piombino (GNL)", "olt": "OLT Livorno (GNL)", "ravenna": "Ravenna (GNL)",
             "tarvisio": "Tarvisio (Austria)", "panigaglia": "Panigaglia (GNL)", "gela": "Gela, Greenstream (Libia)",
             "gorizia": "Gorizia (Slovenia)"}
    rh = 30 if stretto else 26
    lab_w = 0 if stretto else 210
    ml = 12 if stretto else lab_w + 12
    mr = 132 if stretto else 120
    top = 40
    H = top + len(righe) * (rh + (14 if stretto else 0)) + 14
    maxv = max(r["quota_ingressi_pct"] for r in righe)
    sx = Scala(0, maxv, ml, W - mr)
    d = gi["fonti"][0]["data_dato"]
    titolo = "Da dove entra il gas in Italia: quote degli ultimi 12 mesi"
    descr = ("Quota di ogni punto sugli ingressi da gasdotti e GNL, novembre 2025 – novembre 2026: "
             + "; ".join(f"{corto.get(r['id'], r['nome'])} {num(r['quota_ingressi_pct'])}%" for r in righe)
             + f". Fonte: ENTSOG, dati Snam, al {d}.")
    o = svg_apri(W, H, titolo, descr, f"g-gas-{W}")
    o.append(f'<g style="--fs:{fs}px">')
    o += legenda(12, 16, [("c-s3", "gasdotto"), ("c-s2", "GNL via nave")], fs)
    y = top
    for r in righe:
        f = "f-s3" if tipo.get(r["id"]) == "gas-ingresso-gasdotto" else "f-s2"
        nome = corto.get(r["id"], r["nome"])
        if stretto:
            o.append(f'<text x="{ml}" y="{y + fs - 2}" class="t-ink">{esc(nome)}</text>')
            y += 14
        else:
            o.append(f'<text x="{ml - 10}" y="{y + rh / 2 + 4:.1f}" text-anchor="end" class="t-ink">{esc(nome)}</text>')
        bw = max(sx(r["quota_ingressi_pct"]) - ml, 1.5)
        bh = min(rh - 10, 16)
        by = y + (rh - bh) / 2
        rr = min(4, bw / 2)
        # barra con estremità arrotondata e base squadrata
        o.append(f'<path d="M{ml},{by:.1f} h{bw - rr:.1f} a{rr},{rr} 0 0 1 {rr},{rr} v{bh - 2 * rr:.1f} '
                 f'a{rr},{rr} 0 0 1 -{rr},{rr} h-{bw - rr:.1f} z" class="{f}">'
                 f'<title>{esc(r["nome"])}: {num(r["quota_ingressi_pct"])}% degli ingressi, {num(r["twh_12m"])} TWh in 12 mesi ({esc(prov.get(r["id"], ""))})</title></path>')
        o.append(f'<text x="{ml + bw + 6:.1f}" y="{by + bh / 2 + 4:.1f}" class="t-ink num"><tspan class="t-b">{num(r["quota_ingressi_pct"])}%</tspan>'
                 f'<tspan class="t-faint"> · {num(r["twh_12m"])} TWh</tspan></text>')
        y += rh
    o.append(f'<line x1="{ml}" y1="{top - 2}" x2="{ml}" y2="{y}" class="base"/>')
    o.append("</g></svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- grafico 4: esposizione a Hormuz

def grafico_esposizione(pa, W):
    stretto = W < 500
    fs = 13 if stretto else 12
    righe = []
    for e in pa["elementi"]:
        i = e["indicatori"]
        g = (i.get("quota_greggio_golfo_persico") or {}).get("valore")
        n = (i.get("quota_gnl_golfo_persico") or {}).get("valore")
        if not g and not n:
            continue
        righe.append({"paese": e["paese"], "nome": e["nome"], "g": g, "n": n,
                      "ag": (i.get("quota_greggio_golfo_persico") or {}).get("anno"),
                      "an": (i.get("quota_gnl_golfo_persico") or {}).get("anno")})
    # ordine: per quota massima di greggio dal Golfo, poi GNL
    righe.sort(key=lambda r: -max((r["g"] or {}).get("max_pct", 0), (r["n"] or {}).get("max_pct", 0) * 0.999))
    lab_w = 92 if stretto else 130
    ml = lab_w
    gap = 18 if stretto else 30
    mr = 10
    colw = (W - ml - mr - gap) / 2
    top = 62
    rh = 24 if stretto else 22
    H = top + len(righe) * rh + 34
    cols = [("g", "Greggio" if stretto else "Greggio dal Golfo Persico", "f-s3", ml),
            ("n", "GNL" if stretto else "GNL dal Golfo Persico", "f-s2", ml + colw + gap)]
    titolo = "Quanto greggio e GNL arriva dal Golfo Persico, per paese importatore"
    descr = ("Quota delle importazioni (in valore) che arriva dai paesi del Golfo Persico. Barra: dal minimo (Iraq, Kuwait, Qatar, "
             "Bahrein, Iran: nessuna uscita alternativa) al massimo (con Arabia Saudita ed Emirati, che possono aggirare in parte "
             "Hormuz). " + "; ".join(
                 f"{r['nome']}: greggio " + (f"{num(r['g']['min_pct'])}–{num(r['g']['max_pct'])}%" if r["g"] else "n.d.")
                 + ", GNL " + (f"{num(r['n']['min_pct'])}–{num(r['n']['max_pct'])}%" if r["n"] else "n.d.") for r in righe)
             + ". Fonte: UN Comtrade tramite paesi.json, anno 2025 (Taiwan 2024).")
    o = svg_apri(W, H, titolo, descr, f"g-esposizione-{W}")
    o.append(f'<g style="--fs:{fs}px">')
    for k, tit, f, x0 in cols:
        sx = Scala(0, 100, x0, x0 + colw)
        o.append(f'<text x="{x0}" y="16" class="t-ink t-b">{esc(tit)}</text>')
        for t in (0, 50, 100):
            x = sx(t)
            o.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{top + len(righe) * rh}" class="{"base" if t == 0 else "grid"}"/>')
            o.append(f'<text x="{x:.1f}" y="{top - 14}" text-anchor="{"start" if t == 0 else ("end" if t == 100 else "middle")}" class="num t-faint">{t}%</text>')
    o.append(f'<text x="{ml}" y="34" class="t-faint">{"punti: minimo e massimo · % del valore" if stretto else "punti: stima minima e massima · % del valore importato, 2025"}</text>')
    y = top
    for r in righe:
        evid = r["paese"] == "IT"
        if evid:  # Italia in evidenza con una fascia
            o.append(f'<rect x="2" y="{y + 1}" width="{W - 4}" height="{rh - 2}" class="band" rx="3"/>')
        o.append(f'<text x="{ml - 8}" y="{y + rh / 2 + 4:.1f}" text-anchor="end" class="t-ink{" t-b" if evid else ""}">{esc(r["nome"])}</text>')
        for k, tit, f, x0 in cols:
            sx = Scala(0, 100, x0, x0 + colw)
            v = r[k]
            cy = y + rh / 2
            if not v:
                o.append(f'<text x="{x0 + 2}" y="{cy + 4:.1f}" class="t-faint" style="font-size:11px">n.d.</text>')
                continue
            a, b = sx(v["min_pct"]), sx(v["max_pct"])
            anno = r["ag"] if k == "g" else r["an"]
            tip = f'{r["nome"]}, {"greggio" if k == "g" else "GNL"} dal Golfo Persico: {num(v["min_pct"])}–{num(v["max_pct"])}% ({anno})'
            if b - a < 8:
                o.append(f'<circle cx="{(a + b) / 2:.1f}" cy="{cy:.1f}" r="4.5" class="{f} ring"><title>{esc(tip)}</title></circle>')
            else:
                o.append(f'<rect x="{a:.1f}" y="{cy - 4:.1f}" width="{b - a:.1f}" height="8" rx="4" class="{f}" style="fill-opacity:.35"><title>{esc(tip)}</title></rect>')
                o.append(f'<circle cx="{a:.1f}" cy="{cy:.1f}" r="4.5" class="{f} ring"><title>{esc(tip)}</title></circle>')
                o.append(f'<circle cx="{b:.1f}" cy="{cy:.1f}" r="4.5" class="{f} ring"><title>{esc(tip)}</title></circle>')
        y += rh
    nota = "n.d. = dato non calcolato" if stretto else "n.d. = dato non calcolato (paese produttore o voce assente in Comtrade)"
    o.append(f'<text x="{ml}" y="{y + 22}" class="t-faint" style="font-size:11px">{nota}</text>')
    o.append("</g></svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- uscita

def main():
    pw = leggi("portwatch.json")
    pr = leggi("prezzi.json")
    gi = leggi("gas-italia.json")
    pa = leggi("paesi.json")
    grafici = {
        "transiti": lambda W: grafico_transiti(pw, W),
        "prezzi": lambda W: grafico_prezzi(pr, W),
        "gas": lambda W: grafico_gas(gi, W),
        "esposizione": lambda W: grafico_esposizione(pa, W),
    }
    os.makedirs(CARTELLA_SVG, exist_ok=True)
    blocchi = {}
    for nome, f in grafici.items():
        largo, stretto = f(720), f(380)
        with open(os.path.join(CARTELLA_SVG, f"{nome}.svg"), "w", encoding="utf-8") as fh:
            fh.write(largo + "\n")
        blocchi[nome] = (f'<div class="graf graf-largo">\n{largo}\n</div>\n'
                         f'<div class="graf graf-stretto">\n{stretto}\n</div>')
        print(f"grafico {nome}: {len(largo) // 1024} KB + {len(stretto) // 1024} KB")
    if os.path.exists(PAGINA):
        with open(PAGINA, encoding="utf-8") as fh:
            testo = fh.read()
        for nome, blocco in blocchi.items():
            pat = re.compile(rf"(<!-- grafico:{nome} inizio -->)(.*?)(<!-- grafico:{nome} fine -->)", re.S)
            if not pat.search(testo):
                print(f"avviso: segnaposto per '{nome}' non trovato nella pagina", file=sys.stderr)
                continue
            testo = pat.sub(lambda m: m.group(1) + "\n" + blocco + "\n" + m.group(3), testo)
        with open(PAGINA, "w", encoding="utf-8") as fh:
            fh.write(testo)
        print(f"pagina aggiornata: {os.path.relpath(PAGINA, RADICE)}")
    else:
        print(f"avviso: {PAGINA} non esiste, salvati solo gli SVG", file=sys.stderr)


if __name__ == "__main__":
    main()
