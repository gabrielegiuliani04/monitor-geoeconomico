#!/usr/bin/env python3
"""Costruisce la guida personale del Geo-economic Risk Monitor.

Uso (dalla radice del repository):
    python3 guida/costruisci_guida.py            # guida.html + PDF
    python3 guida/costruisci_guida.py --solo-html

Legge guida/capitoli/0*.md (Markdown), incorpora le immagini di guida/img/
(ridimensionate, in base64) e scrive guida/guida.html, un solo file.
Poi genera il PDF con Playwright (Node) in due passate, per mettere
nell'indice i numeri di pagina veri, e aggiunge la copertina senza numero.
Dipendenze: pip install markdown pillow pypdf; node con il pacchetto playwright;
pdftotext (poppler-utils). La guida è personale: non va copiata in docs/.
"""
import base64, html, io, os, re, subprocess, sys, tempfile
import markdown
from PIL import Image
from pypdf import PdfReader, PdfWriter

QUI = os.path.dirname(os.path.abspath(__file__))
CAPITOLI = os.path.join(QUI, "capitoli")
IMG = os.path.join(QUI, "img")
HTML_OUT = os.path.join(QUI, "guida.html")
PDF_OUT = os.path.join(QUI, "Guida-Geo-economic-Risk-Monitor.pdf")
DATA = "10 novembre 2026"
LARGHEZZA_MAX = 1700  # px delle immagini incorporate
QUALITA = 80

CSS = r"""
@page { size: A4; margin: 19mm 19mm 20mm 19mm; }
:root { --ink:#1D272D; --soft:#52606A; --faint:#86929A; --acc:#A61E6B; --line:#D6D9D6;
  --card:#F7F6F2; --note:#ECEFEE; --ok:#E7F1EA; --okb:#2E7D4F; --warn:#FBEEDC; --warnb:#C26A12; }
html { background:#fff; }
body { margin:0; color:var(--ink); font:10pt/1.48 "IBM Plex Serif", Georgia, serif; background:#fff;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; hyphens:auto; }
h1,h2,h3,h4,th,.toc,figcaption,table,.cover,code,pre { font-family:"IBM Plex Sans", system-ui, sans-serif; }
h1 { font-size:22pt; line-height:1.15; color:var(--ink); margin:0 0 14pt; padding-bottom:8pt;
  border-bottom:2.5pt solid var(--acc); break-before:page; break-after:avoid; }
h2 { font-size:14pt; color:var(--acc); margin:18pt 0 6pt; break-after:avoid; }
h3 { font-size:11.5pt; margin:13pt 0 4pt; break-after:avoid; }
h1, h2, h3 { position:relative; }
p { margin:0 0 6.5pt; orphans:3; widows:3; }
p:has(+ blockquote), p:has(+ ul), p:has(+ table), p:has(+ figure) { break-after:avoid; }
ul, ol { margin:0 0 7pt; padding-left:16pt; } li { margin:0 0 2.5pt; }
a { color:var(--acc); text-decoration:none; }
code { font:8.6pt "IBM Plex Mono", ui-monospace, monospace; background:var(--note); padding:0 2.5pt; border-radius:2pt; overflow-wrap:anywhere; }
pre { background:var(--note); padding:7pt 9pt; border-radius:4pt; font-size:8.4pt; line-height:1.45; white-space:pre-wrap; break-inside:avoid; }
pre code { background:none; padding:0; }
table { clear:both; width:100%; border-collapse:collapse; font-size:8.3pt; line-height:1.38; margin:5pt 0 10pt; break-inside:auto; }
thead { display:table-header-group; }
tr { break-inside:avoid; }
th { text-align:left; background:#EFE7EB; color:#4A0F30; font-weight:600; border-bottom:1pt solid var(--acc); padding:3.5pt 5pt; vertical-align:bottom; }
td { padding:3pt 5pt; border-bottom:0.5pt solid var(--line); vertical-align:top; overflow-wrap:break-word; }
td code { overflow-wrap:normal; word-break:normal; hyphens:none; }
tbody tr:nth-child(even) td { background:#FAFAF8; }
table.piccola { break-inside:avoid; }
figure { margin:8pt 0 12pt; break-inside:avoid; text-align:center; }
figure img { max-width:100%; max-height:90mm; border:0.5pt solid var(--line); border-radius:3pt; }
figure.alta { clear:right; float:right; width:38%; margin:2pt 0 8pt 12pt; }
figure.alta img { max-height:none; width:100%; }
h1, h2 { clear:both; }
figcaption { font-size:8.3pt; color:var(--soft); margin-top:4pt; text-align:left; }
figure.schema svg { width:100%; height:auto; }
blockquote { margin:8pt 0 11pt; padding:7pt 11pt; border-radius:0 4pt 4pt 0; background:var(--note);
  border-left:3pt solid var(--faint); break-inside:avoid; font-size:9.6pt; }
blockquote p:last-child { margin-bottom:0; }
blockquote.colloquio { background:#F5E8EF; border-left-color:var(--acc); }
blockquote.colloquio::before { content:"Cosa dire al colloquio"; display:block; font:600 7.8pt "IBM Plex Sans",sans-serif;
  letter-spacing:.06em; text-transform:uppercase; color:var(--acc); margin-bottom:3pt; }
blockquote.attenzione { background:var(--warn); border-left-color:var(--warnb); }
blockquote.attenzione::before { content:"Attenzione"; display:block; font:600 7.8pt "IBM Plex Sans",sans-serif;
  letter-spacing:.06em; text-transform:uppercase; color:var(--warnb); margin-bottom:3pt; }
blockquote.discorso { background:#fff; border:0.5pt solid var(--line); border-left:3pt solid var(--acc); font-style:normal; }
.mk { position:absolute; left:0; top:0; font-size:1pt; color:#fff; line-height:1; }
/* indice */
.toc { break-after:page; }
.toc h1 { break-before:auto; }
.toc ol { list-style:none; padding:0; margin:0; }
.toc li.c { margin:9pt 0 2pt; font-weight:600; font-size:11pt; }
.toc li.s { margin:0 0 1.5pt 14pt; font-size:9.2pt; color:var(--soft); }
.toc a { color:inherit; display:flex; gap:6pt; }
.toc a .t { flex:0 1 auto; }
.toc a .dots { flex:1 1 auto; border-bottom:0.6pt dotted var(--faint); margin-bottom:3pt; }
.toc a .p { flex:0 0 auto; font-variant-numeric:tabular-nums; }
.prefazione { font-size:9.4pt; color:var(--soft); margin-top:16pt; border-top:0.5pt solid var(--line); padding-top:8pt; }
/* copertina */
.cover { height:257mm; display:flex; flex-direction:column; justify-content:space-between; }
.cover .top { border-top:6pt solid var(--acc); padding-top:30mm; }
.cover .eyebrow { font-size:9pt; letter-spacing:.14em; text-transform:uppercase; color:var(--acc); font-weight:600; }
.cover h1.titolo { border:0; break-before:auto; font-size:31pt; line-height:1.1; margin:10pt 0 12pt; padding:0; }
.cover .sub { font:italic 15pt/1.35 "IBM Plex Serif", serif; color:var(--soft); }
.cover .bottom { font-size:10.5pt; border-top:0.6pt solid var(--line); padding-top:10pt; }
.cover .bottom b { font-size:13pt; }
.cover .nota { color:var(--faint); font-size:8.5pt; margin-top:6pt; }
@media screen { body { max-width:180mm; margin:0 auto; padding:10mm; } .cover { height:auto; min-height:240mm; } }
"""

FONT = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400&family=IBM+Plex+Sans:wght@400;500;600&'
        'family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">')


def img_data_uri(nome):
    percorso = os.path.join(IMG, nome)
    im = Image.open(percorso).convert("RGB")
    if im.width > LARGHEZZA_MAX:
        im = im.resize((LARGHEZZA_MAX, round(im.height * LARGHEZZA_MAX / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=QUALITA, optimize=True, progressive=True)
    alta = im.height > im.width * 1.1
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), alta


def slug(testo):
    t = re.sub(r"<[^>]+>", "", testo).lower()
    t = re.sub(r"[^a-z0-9àèéìòù]+", "-", t).strip("-")
    return t[:50]


def converti_capitolo(n, testo, toc):
    corpo = markdown.markdown(testo, extensions=["tables", "fenced_code", "sane_lists"])
    # figure: paragrafo con sola immagine
    def fig(m):
        alt, src = html.unescape(m.group(1)), m.group(2)
        nome = os.path.basename(src)
        uri, alta = img_data_uri(nome)
        cls = ' class="alta"' if alta else ""
        return f'<figure{cls}><img src="{uri}" alt="{html.escape(alt)}"><figcaption>{html.escape(alt)}</figcaption></figure>'
    corpo = re.sub(r'<p><img alt="([^"]*)" src="([^"]+)" ?/?></p>', fig, corpo)
    # riquadri
    corpo = corpo.replace("<blockquote>\n<p><strong>Cosa dire al colloquio.</strong>", '<blockquote class="colloquio">\n<p>')
    corpo = corpo.replace("<blockquote>\n<p><strong>Attenzione.</strong>", '<blockquote class="attenzione">\n<p>')
    corpo = re.sub(r"<blockquote>\n<p><em>", '<blockquote class="discorso">\n<p><em>', corpo)
    # titoli con id e marcatori per i numeri di pagina
    conta = {"h": 0}
    def tit(m):
        liv, contenuto = m.group(1), m.group(2)
        conta["h"] += 1
        hid = f"c{n}-{conta['h']}-{slug(contenuto)}"
        mk = f"MK{n:02d}{conta['h']:03d}X"
        if liv in ("1", "2"):
            toc.append((liv, hid, re.sub(r"<[^>]+>", "", contenuto), mk))
        return f'<h{liv} id="{hid}"><span class="mk">{mk}</span>{contenuto}</h{liv}>'
    corpo = re.sub(r"<h([123])>(.*?)</h\1>", tit, corpo)
    # tabelle corte: non spezzarle
    def tab(m):
        righe = m.group(0).count("<tr>")
        return m.group(0).replace("<table>", '<table class="piccola">', 1) if righe <= 6 else m.group(0)
    corpo = re.sub(r"<table>.*?</table>", tab, corpo, flags=re.S)
    return f'<section class="capitolo" id="cap{n}">{corpo}</section>'


def costruisci_html(pagine=None, copertina=True, marcatori=True):
    files = sorted(f for f in os.listdir(CAPITOLI) if re.match(r"0\d-.*\.md$", f))
    toc, sezioni = [], []
    for i, f in enumerate(files, 1):
        testo = open(os.path.join(CAPITOLI, f), encoding="utf-8").read()
        sezioni.append(converti_capitolo(i, testo, toc))
    voci = []
    for liv, hid, t, mk in toc:
        p = (pagine or {}).get(mk, "00")
        cls = "c" if liv == "1" else "s"
        voci.append(f'<li class="{cls}"><a href="#{hid}"><span class="t">{html.escape(t)}</span><span class="dots"></span><span class="p">{p}</span></a></li>')
    indice = ('<nav class="toc"><h1 id="indice">Indice</h1><ol>' + "".join(voci) + "</ol>"
              '<p class="prefazione">Guida personale, non pubblicata sul sito. Numeri letti dai file del repository '
              f'il {DATA}: quelli che cambiano ogni giorno vanno ricontrollati prima di un colloquio. '
              'I riquadri rosa contengono «Cosa dire al colloquio», quelli arancio «Attenzione». '
              'Il glossario è in appendice. Resoconto della revisione: <code>guida/revisione-guida.md</code>.</p></nav>')
    cover = ('<section class="cover"><div class="top"><div class="eyebrow">Guida al progetto · uso personale</div>'
             '<h1 class="titolo">Geo-economic Risk Monitor — Guida al progetto</h1>'
             '<div class="sub">Come funziona, come usarlo, come presentarlo</div></div>'
             f'<div class="bottom"><b>Gabriele Giuliani</b><br>{DATA}<br>'
             'https://gabrielegiuliani04.github.io/monitor-geoeconomico/'
             '<div class="nota">Dati e conteggi al 10 novembre 2026. Testo preparato con un assistente AI e rivisto '
             'contro i file del repository (vedi revisione-guida.md).</div></div></section>')
    corpo = (cover if copertina else "") + indice + "".join(sezioni)
    if not marcatori:
        corpo = re.sub(r'<span class="mk">MK\d+X</span>', "", corpo)
    return ('<!doctype html><html lang="it"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Guida al Geo-economic Risk Monitor</title>' + FONT + f"<style>{CSS}</style></head><body>"
            + corpo + "</body></html>")


NODE = r"""
const { chromium } = require('playwright');
(async () => {
  const [src, out, footer] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + src, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const opt = { path: out, format: 'A4', printBackground: true, preferCSSPageSize: true };
  if (footer === '1') Object.assign(opt, { displayHeaderFooter: true, headerTemplate: '<div></div>',
    footerTemplate: '<div style="width:100%;font:7.5pt IBM Plex Sans,Arial,sans-serif;color:#86929A;padding:0 19mm;display:flex;justify-content:space-between"><span>Geo-economic Risk Monitor — Guida al progetto</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>' });
  await p.pdf(opt); await b.close();
})();
"""


def node_pdf(html_path, pdf_path, footer):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(NODE)
        js = f.name
    env = dict(os.environ)
    env.setdefault("NODE_PATH", subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    subprocess.run(["node", js, html_path, pdf_path, "1" if footer else "0"], check=True, env=env)
    os.unlink(js)


def pagine_dei_marcatori(pdf):
    n = len(PdfReader(pdf).pages)
    trovati = {}
    for i in range(1, n + 1):
        t = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), pdf, "-"], capture_output=True, text=True).stdout
        for mk in re.findall(r"MK\d{5}X", t):
            trovati.setdefault(mk, i)
    return trovati


def main():
    open(HTML_OUT, "w", encoding="utf-8").write(costruisci_html(marcatori=False))
    print("scritto", HTML_OUT)
    if "--solo-html" in sys.argv:
        return
    tmp = tempfile.mkdtemp()
    corpo_html = os.path.join(tmp, "corpo.html")
    corpo_pdf = os.path.join(tmp, "corpo.pdf")
    cover_html, cover_pdf = os.path.join(tmp, "cover.html"), os.path.join(tmp, "cover.pdf")
    # passata 1: posizioni dei titoli
    open(corpo_html, "w", encoding="utf-8").write(costruisci_html(copertina=False))
    node_pdf(corpo_html, corpo_pdf, True)
    pagine = pagine_dei_marcatori(corpo_pdf)
    # passata 2: indice con i numeri veri
    open(corpo_html, "w", encoding="utf-8").write(costruisci_html(pagine=pagine, copertina=False))
    node_pdf(corpo_html, corpo_pdf, True)
    pagine2 = pagine_dei_marcatori(corpo_pdf)
    if pagine2 != pagine:
        print("avviso: numeri di pagina cambiati tra le passate", len(set(pagine.items()) ^ set(pagine2.items())))
    # copertina senza numero di pagina
    doc = costruisci_html(copertina=True)
    doc = doc.split('<nav class="toc">')[0] + "</body></html>"
    open(cover_html, "w", encoding="utf-8").write(doc)
    node_pdf(cover_html, cover_pdf, False)
    w = PdfWriter()
    w.append(PdfReader(cover_pdf), pages=(0, 1))
    w.append(PdfReader(corpo_pdf))
    w.add_metadata({"/Title": "Geo-economic Risk Monitor — Guida al progetto", "/Author": "Gabriele Giuliani"})
    with open(PDF_OUT, "wb") as f:
        w.write(f)
    n = len(PdfReader(PDF_OUT).pages)
    print(f"scritto {PDF_OUT}: {n} pagine, {os.path.getsize(PDF_OUT)/1e6:.1f} MB")


if __name__ == "__main__":
    main()
