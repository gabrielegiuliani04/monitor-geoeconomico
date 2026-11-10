#!/usr/bin/env python3
"""World events layer of the map (docs/data/eventi.json). Python 3 standard library only.

Merges, in this order of priority:
  1. raccolta/eventi/curati.json        the 126 events curated before Nov 2026 (copied unchanged; Italian text)
  2. raccolta/eventi/curati_nuovi.json  events curated from web research, each with source, link and date
  3. automatic keyless feeds:
       - USGS earthquakes (M6.0+, or M5.5+ with a PAGER alert yellow/orange/red)   public domain
       - GDACS orange/red alerts (EQ, TC, FL, VO, WF; droughts skipped)            GDACS terms, citation
       - NASA EONET v3 severe storms (hurricane force, >= 64 kt) and volcanoes     public domain
       - ReCAAP ISC list of Asian piracy/robbery incidents (PDF; parsed only when the
         `pdftotext` program is installed, otherwise skipped with a warning)
Then de-duplicates (id, and same category within a day and a few km), keeps a rolling window
(FINESTRA days; older items survive only if flagged "strategico": true) and writes the file in the
schema of the existing points (id, classe, categoria, nome, ..., fonti, breve), keeping the keys
"raccolte" and "fuori" of the curated file.

If a feed fails, the items that feed produced in the previous docs/data/eventi.json are kept, so a
temporary outage never empties the layer. Never invents coordinates: automatic points use the
coordinates published by the source (origine_coord "fonte").

Usage:  python3 raccolta/eventi/raccogli.py [--oggi AAAA-MM-GG] [--offline]
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(os.path.dirname(QUI))
DATI = os.path.join(RADICE, 'docs', 'data')
USCITA = os.path.join(DATI, 'eventi.json')
CURATI = os.path.join(QUI, 'curati.json')
NUOVI = os.path.join(QUI, 'curati_nuovi.json')
UA = 'monitor-geoeconomico/1.0 (OSINT geo-economic risk map; python-urllib)'
FINESTRA = 120          # days kept on the layer
TIMEOUT = 45

URL_USGS = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
URL_GDACS = 'https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH'
URL_EONET = 'https://eonet.gsfc.nasa.gov/api/v3/events'
URL_RECAAP = 'https://www.recaap.org/resources/ck/files/Number%20of%20Incidents/{y}/List%20of%20Incidents%20for%20{y}.pdf'

CAMPI = ['id', 'classe', 'categoria', 'nome', 'identificativo', 'appartenenza', 'stato', 'data_evento', 'ora_utc',
         'lat', 'lon', 'origine_coord', 'precisione_km', 'teatro', 'paese', 'regione', 'attore', 'bersaglio', 'mezzo',
         'esito', 'fonte', 'link', 'data_fonte', 'affidabilita', 'note', 'fonti', 'breve']

# ------------------------------------------------------------------ geography helpers
MO = {'IR', 'IQ', 'SA', 'AE', 'QA', 'KW', 'BH', 'OM', 'YE', 'IL', 'LB', 'SY', 'JO', 'EG', 'PS'}
RUUA = {'RU', 'UA', 'BY'}
EUROPA = {'GB', 'FR', 'NO', 'DE', 'ES', 'NL', 'BE', 'DK', 'PL', 'GR', 'PT', 'RO', 'BG', 'SE', 'FI', 'EE', 'LV', 'LT',
          'CZ', 'SK', 'HU', 'HR', 'AT', 'CH', 'TR', 'IS', 'IE', 'SI', 'AL', 'ME', 'MK', 'RS', 'BA', 'CY', 'MT', 'LU', 'MD'}
NOMI_PAESI = {
    'japan': 'JP', 'indonesia': 'ID', 'philippines': 'PH', 'papua new guinea': 'PG', 'solomon islands': 'SB',
    'vanuatu': 'VU', 'fiji': 'FJ', 'tonga': 'TO', 'new zealand': 'NZ', 'chile': 'CL', 'peru': 'PE', 'mexico': 'MX',
    'guatemala': 'GT', 'el salvador': 'SV', 'nicaragua': 'NI', 'costa rica': 'CR', 'panama': 'PA', 'colombia': 'CO',
    'ecuador': 'EC', 'argentina': 'AR', 'bolivia': 'BO', 'russia': 'RU', 'china': 'CN', 'taiwan': 'TW', 'iran': 'IR',
    'turkey': 'TR', 'türkiye': 'TR', 'turkiye': 'TR', 'greece': 'GR', 'italy': 'IT', 'afghanistan': 'AF',
    'pakistan': 'PK', 'india': 'IN', 'nepal': 'NP', 'myanmar': 'MM', 'alaska': 'US', 'hawaii': 'US', 'ca': 'US',
    'california': 'US', 'nevada': 'US', 'oregon': 'US', 'washington': 'US', 'venezuela': 'VE', 'haiti': 'HT',
    'dominican republic': 'DO', 'puerto rico': 'PR', 'northern mariana islands': 'MP', 'guam': 'GU',
    'micronesia': 'FM', 'samoa': 'WS', 'american samoa': 'AS', 'kyrgyzstan': 'KG', 'tajikistan': 'TJ',
    'kazakhstan': 'KZ', 'algeria': 'DZ', 'morocco': 'MA', 'ethiopia': 'ET', 'djibouti': 'DJ', 'yemen': 'YE',
    'mongolia': 'MN', 'australia': 'AU', 'iceland': 'IS', 'portugal': 'PT', 'spain': 'ES', 'canada': 'CA',
    'vietnam': 'VN', 'thailand': 'TH', 'malaysia': 'MY', 'timor leste': 'TL', 'east timor': 'TL', 'cuba': 'CU',
    'jamaica': 'JM', 'honduras': 'HN', 'iraq': 'IQ', 'saudi arabia': 'SA', 'egypt': 'EG', 'albania': 'AL',
    'romania': 'RO', 'kermadec islands': 'NZ', 'south sandwich islands': 'GS', 'south georgia and the south sandwich islands': 'GS',
    'new caledonia': 'NC', 'wallis and futuna': 'WF', 'french polynesia': 'PF', 'kuril islands': 'RU',
    'bangladesh': 'BD', 'sri lanka': 'LK', 'uzbekistan': 'UZ', 'turkmenistan': 'TM', 'azerbaijan': 'AZ',
    'armenia': 'AM', 'georgia': 'GE', 'syria': 'SY', 'lebanon': 'LB', 'israel': 'IL', 'jordan': 'JO', 'oman': 'OM',
    'tanzania': 'TZ', 'kenya': 'KE', 'mozambique': 'MZ', 'madagascar': 'MG', 'south africa': 'ZA', 'brunei': 'BN',
}


def km(a, b, c, d):
    p = math.radians
    x = math.sin(p(c - a) / 2) ** 2 + math.cos(p(a)) * math.cos(p(c)) * math.sin(p(d - b) / 2) ** 2
    return 2 * 6371 * math.asin(min(1, math.sqrt(x)))


def teatro_per(lat, lon, paese):
    if paese == 'IT':
        return 'IT'
    if paese in RUUA:
        return 'RU-UA'
    if paese in MO:
        return 'MO'
    if paese in EUROPA:
        return 'NATO'
    if not paese:
        if 40.5 <= lat <= 47.5 and 27.5 <= lon <= 42:      # Black Sea
            return 'RU-UA'
        if 11 <= lat <= 31.5 and 32 <= lon <= 62:          # Red Sea, Gulf of Aden, Gulf, Gulf of Oman
            return 'MO'
        if 30 <= lat <= 46 and -6 <= lon <= 36:            # Mediterranean
            return 'NATO'
        if 50 <= lat <= 72 and -12 <= lon <= 31:           # North Sea, Baltic, Norwegian Sea
            return 'NATO'
    return 'ALTRO'


def riferimenti():
    """Monitored ports and chokepoints from other layers (read-only), to say how close a hazard is."""
    out = []
    try:
        for p in json.load(open(os.path.join(DATI, 'port-risk.json'), encoding='utf-8')).get('ports', []):
            if isinstance(p.get('lat'), (int, float)):
                out.append((p['name'], p['lat'], p['lon'], 'port'))
    except Exception:
        pass
    try:
        for p in json.load(open(os.path.join(DATI, 'portwatch.json'), encoding='utf-8')).get('elementi', []):
            if p.get('tipo') == 'chokepoint' and isinstance(p.get('lat'), (int, float)):
                out.append((p.get('nome_portwatch') or p.get('nome'), p['lat'], p['lon'], 'chokepoint'))
    except Exception:
        pass
    return out


RIF = []


def vicino(lat, lon, raggio=500):
    best = None
    for n, a, b, t in RIF:
        d = km(lat, lon, a, b)
        if d <= raggio and (best is None or d < best[0]):
            best = (d, n, t)
    return ' Nearest monitored %s: %s (%d km).' % (best[2], best[1], round(best[0])) if best else ''


# ------------------------------------------------------------------ network
def scarica(url, binario=False):
    ultimo = None
    for _ in range(2):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                b = r.read()
            return b if binario else b.decode('utf-8-sig')
        except Exception as e:      # noqa: BLE001 - every feed is optional
            ultimo = e
    raise ultimo


def punto(**k):
    p = {c: '' for c in CAMPI}
    p.update(classe='evento', appartenenza='', stato='', origine_coord='fonte', affidabilita='alta')
    p.update(k)
    p['lat'] = round(float(p['lat']), 4)
    p['lon'] = round(float(p['lon']), 4)
    if not p.get('fonti'):
        p['fonti'] = [{'fonte': p['fonte'], 'link': p['link'], 'data_fonte': p['data_fonte']}]
    if not p.get('teatro'):
        p['teatro'] = teatro_per(p['lat'], p['lon'], p.get('paese', ''))
    return p


def iso_ms(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)


# ------------------------------------------------------------------ USGS
def usgs(oggi):
    q = {'format': 'geojson', 'starttime': (oggi - dt.timedelta(days=FINESTRA)).isoformat(),
         'endtime': (oggi + dt.timedelta(days=1)).isoformat(), 'minmagnitude': '5.5', 'orderby': 'time', 'limit': '2000'}
    d = json.loads(scarica(URL_USGS + '?' + urllib.parse.urlencode(q)))
    out = []
    for f in d.get('features', []):
        pr, g = f.get('properties') or {}, (f.get('geometry') or {}).get('coordinates') or []
        m, al = pr.get('mag'), (pr.get('alert') or '')
        if m is None or len(g) < 2 or pr.get('type') != 'earthquake':
            continue
        if not (m >= 6.0 or al in ('yellow', 'orange', 'red')):
            continue
        t = iso_ms(pr['time'])
        luogo = pr.get('place') or ''
        coda = re.sub(r'\s+region$', '', luogo.split(', ')[-1].strip(), flags=re.I).lower()
        paese = NOMI_PAESI.get(coda, '')
        prof = round(g[2]) if len(g) > 2 and g[2] is not None else None
        esito = []
        if al:
            esito.append('PAGER alert ' + al)
        if pr.get('tsunami'):
            esito.append('tsunami flag set')
        if pr.get('felt'):
            esito.append('%d felt reports' % pr['felt'])
        out.append(punto(
            id='USGS-' + f['id'], categoria='terremoto', nome='M%.1f earthquake, %s' % (m, luogo),
            identificativo=f['id'], data_evento=t.date().isoformat(), ora_utc=t.strftime('%H:%M'),
            lat=g[1], lon=g[0], precisione_km=10, paese=paese, regione=luogo, mezzo='',
            esito='; '.join(esito) or 'no PAGER alert', fonte='USGS Earthquake Hazards Program',
            link=pr.get('url') or 'https://earthquake.usgs.gov/', bersaglio='',
            data_fonte=iso_ms(pr.get('updated') or pr['time']).date().isoformat(),
            note=('Magnitude %s %s, depth %s km, status %s.' % (m, pr.get('magType', ''), prof, pr.get('status', ''))) + vicino(g[1], g[0]),
            breve='M%.1f %s' % (m, (luogo.split(' of ')[-1])[:30]), affidabilita='alta'))
    return out


# ------------------------------------------------------------------ GDACS
G_CAT = {'EQ': 'terremoto', 'TC': 'tempesta', 'FL': 'alluvione', 'VO': 'vulcano', 'WF': 'incendio-boschivo'}
G_PREC = {'EQ': 15, 'TC': 100, 'FL': 150, 'VO': 5, 'WF': 30}   # FL: centroid of a flooded area -> report only
G_NOME = {'EQ': 'Earthquake', 'TC': 'Tropical cyclone', 'FL': 'Flood', 'VO': 'Volcanic eruption', 'WF': 'Forest fire'}


def gdacs(oggi):
    q = {'fromDate': (oggi - dt.timedelta(days=FINESTRA)).isoformat(), 'toDate': oggi.isoformat(),
         'alertlevel': 'Orange;Red', 'eventlist': 'EQ;TC;FL;VO;WF'}
    d = json.loads(scarica(URL_GDACS + '?' + urllib.parse.urlencode(q, safe=';')))
    out = []
    for f in d.get('features', []):
        pr = f.get('properties') or {}
        tipo = pr.get('eventtype')
        g = (f.get('geometry') or {}).get('coordinates') or []
        if tipo not in G_CAT or len(g) < 2:
            continue
        pa = [c.get('iso2', '') for c in pr.get('affectedcountries') or [] if c.get('iso2')]
        paese = pa[0] if len(pa) == 1 else ''
        da = (pr.get('fromdate') or '')[:10]
        a = (pr.get('todate') or '')[:10]
        rep = (pr.get('url') or {}).get('report') or 'https://www.gdacs.org/'
        lvl = pr.get('alertlevel', '')
        sev = (pr.get('severitydata') or {}).get('severitytext', '')
        out.append(punto(
            id='GDACS-%s-%s' % (tipo, pr.get('eventid')), categoria=G_CAT[tipo],
            nome=re.sub(r'\s+', ' ', '%s (GDACS %s alert): %s' % (G_NOME[tipo], lvl.lower(), pr.get('name') or pr.get('eventname') or '')),
            identificativo=str(pr.get('glide') or pr.get('eventid') or ''), data_evento=da, ora_utc='',
            lat=g[1], lon=g[0], precisione_km=G_PREC[tipo], paese=paese,
            regione=(pr.get('country') or '')[:120], esito=re.sub(r';? ?Magnitude 0$', '', ('%s alert; %s' % (lvl, sev)).strip('; '))[:200],
            fonte='GDACS (Global Disaster Alert and Coordination System, EC JRC / UN OCHA)', link=rep,
            data_fonte=(pr.get('datemodified') or da)[:10], affidabilita='alta',
            note=('Episode from %s to %s. Alert levels are model estimates of humanitarian impact.' % (da, a)
                  + (' Point is the centroid of the affected area.' if tipo == 'FL' else '')
                  + (' Point is the GDACS reference position of the storm.' if tipo == 'TC' else '')) + vicino(g[1], g[0]),
            breve=('%s %s' % (G_NOME[tipo], pr.get('eventname') or ''))[:40]))
    return out


# ------------------------------------------------------------------ NASA EONET
def eonet(oggi):
    q = {'status': 'all', 'days': str(FINESTRA), 'category': 'severeStorms,volcanoes'}
    d = json.loads(scarica(URL_EONET + '?' + urllib.parse.urlencode(q)))
    out = []
    for e in d.get('events', []):
        cat = (e.get('categories') or [{}])[0].get('id')
        geos = [g for g in e.get('geometry') or [] if g.get('type') == 'Point' and g.get('coordinates')]
        if not geos:
            continue
        fonti_e = [s.get('id') for s in e.get('sources') or []]
        if cat == 'severeStorms':
            vmax = max((g.get('magnitudeValue') or 0) for g in geos)
            if vmax < 64:                      # hurricane / typhoon force only
                continue
            g = max(geos, key=lambda x: x.get('magnitudeValue') or 0)
            categoria, prec = 'tempesta', 50
            esito = 'peak %s %s; %d track fixes' % (g.get('magnitudeValue'), g.get('magnitudeUnit') or '', len(geos))
            nota = 'Point = position at peak intensity (%s). Track: %s to %s.' % (
                g['date'][:16].replace('T', ' '), geos[0]['date'][:10], geos[-1]['date'][:10])
        elif cat == 'volcanoes':
            g = geos[-1]
            categoria, prec, esito, nota = 'vulcano', 5, 'eruption reported', 'Latest position reported by EONET.'
        else:
            continue
        lon, lat = g['coordinates'][0], g['coordinates'][1]
        t = g['date']
        out.append(punto(
            id='EONET-' + e['id'], categoria=categoria, nome=e.get('title', ''), identificativo=e['id'],
            data_evento=t[:10], ora_utc=t[11:16], lat=lat, lon=lon, precisione_km=prec, paese='',
            regione='', esito=esito, fonte='NASA EONET v3 (sources: %s)' % ', '.join(filter(None, fonti_e)),
            link=e.get('link') or URL_EONET, data_fonte=geos[-1]['date'][:10], affidabilita='alta',
            note=nota + vicino(lat, lon), breve=e.get('title', '')[:40]))
    return out


# ------------------------------------------------------------------ ReCAAP (optional, needs pdftotext)
def _deg(s):
    m = re.match(r"\s*(\d+)\s*°\s*([\d.]+)?'?\s*([NSEW])", s)
    if not m:
        return None
    v = int(m.group(1)) + float(m.group(2) or 0) / 60
    return -v if m.group(3) in 'SW' else v


RC_PAESE = {'Vietnam': 'VN', 'Philippines': 'PH', 'Indonesia': 'ID', 'Bangladesh': 'BD', 'Malaysia': 'MY',
            'India': 'IN', 'Sri Lanka': 'LK', 'Thailand': 'TH', 'China': 'CN'}


def recaap_testo(testo, oggi, url):
    """Parse the `pdftotext -layout` text of ReCAAP's incident list into points."""
    righe = testo.split('\n')
    rx = re.compile(r"^\s*(\d+)\.\s+(.+?)\s{2,}(Robbery/|Piracy|Attempted|Robbery)\S*\s+(\d{1,2} \w{3})\s+(\d{4})\s+(.+?)\s{2,}(.+?)\s{2,}"
                    r"(\d+°\s*[\d.]*'?\s*[NS])\s+(\d+°\s*[\d.]*'?\s*[EW])\s+(.+?)\s{2,}")
    inizi = [i for i, l in enumerate(righe) if rx.match(l)]
    cols = None
    out = []
    for k, i in enumerate(inizi):
        for j in range(i, -1, -1):                        # nearest header above: column offsets
            if righe[j].startswith('S/N'):
                h = righe[j]
                cols = (h.find('Area description'), h.find('Ship ', h.find('Area description')), h.find('Attack method'), h.rfind('CAT'))
                break
        fine = inizi[k + 1] if k + 1 < len(inizi) else len(righe)
        blocco = [l for l in righe[i:fine] if not l.startswith('S/N') and 'Type     incident' not in l]
        m = rx.match(righe[i])
        anno = re.search(r'(20\d\d)', righe[i + 1] if i + 1 < len(righe) else '')
        try:
            data = dt.datetime.strptime('%s %s' % (m.group(4), anno.group(1) if anno else oggi.year), '%d %b %Y').date()
        except ValueError:
            continue
        if (oggi - data).days > FINESTRA:
            continue
        lat, lon = _deg(m.group(8)), _deg(m.group(9))
        if lat is None or lon is None:
            continue
        def col(a, b):
            return re.sub(r'\s+', ' ', ' '.join(l[a:b] for l in blocco if len(l) > a)).strip()
        area = col(cols[0], cols[1]) if cols and cols[0] > 0 else ''
        nome_nave = (m.group(2) + ' ' + ' '.join(l[:22].strip() for l in blocco[1:3] if l[:22].strip() and not re.search(r'\d{4}', l[:22]))).strip()
        nome_nave = re.sub(r'\s+', ' ', nome_nave)
        tipo_nave = re.sub(r'\s+', ' ', (m.group(7) + ' ' + ' '.join(l[cols[0] - 70:cols[0] - 55].strip() for l in blocco[1:2] if cols))).strip() if cols else m.group(7)
        cat = re.search(r'\s(\d)\s*$', righe[i])
        luogo = m.group(10).strip()
        paese = next((v for n, v in RC_PAESE.items() if n in luogo or ('(%s)' % n) in area), '')
        tutto = ' '.join(blocco)
        prime = ' '.join(blocco[:3])
        attivita = ('underway' if re.search(r'Sailing|While underway|Steaming', prime) else 'at berth' if re.search(r'Berth|At Port|Pier|at berth', prime)
                    else 'at anchor' if re.search(r'Anchor', prime) else 'activity not stated')
        rubato = 'nothing stolen' if re.search(r'[Nn]othing was stolen|[Nn]othing stolen', tutto) else ('items stolen' if 'stole' in tutto else 'theft not stated')
        feriti = 'crew injured' if re.search(r'injur', tutto) and not re.search(r'no injur|not injured|without injur|no (?:crew )?injur', tutto, re.I) else 'no injuries reported'
        luoghi = re.findall(r'(\d+(?:\.\d+)?\s*nm)', area)
        posto = re.search(r'(Pulau(?:\s+[A-Z])?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?|Vung Tau|Batangas|Jakarta|Belawan|Chittagong|Lubuk Gaung|Bintan|Nongsa|Manila|Sandakan)', area)
        dove = luogo + ((' - about %s off %s' % (luoghi[0], re.sub(r'^Pulau\s+[A-Z]\s+', 'Pulau ', posto.group(1)))) if (luoghi and posto) else (' - ' + posto.group(1) if posto else ''))
        sl = re.sub(r'[^a-z0-9]+', '-', nome_nave.lower()).strip('-')[:24]
        out.append(punto(
            id='EV-RECAAP-%s-%s' % (data.isoformat(), sl), categoria='pirateria',
            nome='%s: %s %s boarded (%s)' % ('Piracy' if 'Piracy' in m.group(3) else 'Sea robbery', tipo_nave.title(), nome_nave, luogo),
            identificativo='ReCAAP %s' % data.year, data_evento=data.isoformat(),
            ora_utc='', lat=lat, lon=lon, precisione_km=2, paese=paese, teatro='ALTRO',
            regione=dove[:160], bersaglio='nave-mercantile' if 'TANKER' not in tipo_nave.upper() else 'nave-petroliera',
            mezzo='boarding', esito='boarded %s; %s; %s' % (attivita, rubato, feriti),
            fonte='ReCAAP ISC, list of incidents %d' % data.year, link=url, data_fonte=oggi.isoformat(),
            affidabilita='alta', note=('Local time %s. ReCAAP category %s (1 most severe, 4 least). Coordinates from ReCAAP.' % (m.group(5), cat.group(1) if cat else '?')),
            breve=('Robbery: %s' % nome_nave)[:40]))
    return out


def recaap(oggi):
    if not shutil.which('pdftotext'):
        raise RuntimeError('pdftotext not installed (poppler-utils): ReCAAP skipped, curated ReCAAP items kept')
    url = URL_RECAAP.format(y=oggi.year)
    pdf = scarica(url, binario=True)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, 'r.pdf')
        open(p, 'wb').write(pdf)
        testo = subprocess.run(['pdftotext', '-layout', p, '-'], capture_output=True, timeout=120).stdout.decode('utf-8', 'replace')
    return recaap_testo(testo, oggi, url)


# ------------------------------------------------------------------ merge
GRUPPO = {'attacco': 'a', 'intercettazione': 'a', 'lancio': 'a'}


def doppione(p, q, raggio=None):
    if GRUPPO.get(p['categoria'], p['categoria']) != GRUPPO.get(q['categoria'], q['categoria']):
        return False
    try:
        dd = abs((dt.date.fromisoformat(p['data_evento']) - dt.date.fromisoformat(q['data_evento'])).days)
    except ValueError:
        return False
    if dd > 1:
        return False
    r = raggio if raggio is not None else max(5, min(30, (p.get('precisione_km') or 10), (q.get('precisione_km') or 10)))
    return km(p['lat'], p['lon'], q['lat'], q['lon']) <= r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--oggi', help='reference date AAAA-MM-GG (default: today UTC)')
    ap.add_argument('--offline', action='store_true', help='do not call the feeds; keep previous automatic items')
    a = ap.parse_args()
    adesso = dt.datetime.now(dt.timezone.utc)
    oggi = dt.date.fromisoformat(a.oggi) if a.oggi else adesso.date()
    RIF.extend(riferimenti())
    errori, fonti = [], []

    base = json.load(open(CURATI, encoding='utf-8'))
    nuovi = json.load(open(NUOVI, encoding='utf-8'))
    try:
        prima = json.load(open(USCITA, encoding='utf-8')).get('punti', [])
    except Exception:
        prima = []

    feed = [('USGS', 'USGS-', usgs, 'USGS Earthquake Hazards Program, FDSN event web service', URL_USGS, 'public domain (U.S. Government)'),
            ('GDACS', 'GDACS-', gdacs, 'GDACS (EC JRC / UN OCHA), event list API', URL_GDACS, 'free use with citation of GDACS'),
            ('EONET', 'EONET-', eonet, 'NASA EONET v3 (severe storms, volcanoes)', URL_EONET, 'public domain (NASA)'),
            ('ReCAAP', 'EV-RECAAP-', recaap, 'ReCAAP ISC, list of incidents (PDF)', URL_RECAAP.format(y=oggi.year), 'public information, cite ReCAAP ISC')]
    auto, conta_feed = [], {}
    for nome, pref, fn, desc, url, lic in feed:
        try:
            if a.offline:
                raise RuntimeError('offline run')
            r = fn(oggi)
            conta_feed[nome] = len(r)
            auto.extend(r)
            fonti.append({'nome': desc, 'link': url, 'licenza': lic, 'data_dato': adesso.strftime('%Y-%m-%dT%H:%MZ'), 'elementi': len(r)})
        except Exception as e:  # noqa: BLE001
            vecchi = [p for p in prima if p.get('id', '').startswith(pref)]
            if pref == 'EV-RECAAP-':
                vecchi = []          # curated ReCAAP items in curati_nuovi.json stand in
            auto.extend(vecchi)
            conta_feed[nome] = 'kept %d from previous run' % len(vecchi)
            errori.append('%s: %s' % (nome, str(e)[:200]))
            print('WARN', nome, e, file=sys.stderr)

    # priority: existing curated > new curated > automatic. A ReCAAP item from the feed replaces the
    # curated copy with the same id (it is the same record, refreshed).
    ids_auto = {p['id'] for p in auto}
    curati = list(base.get('punti', []))
    nuovi_p = [p for p in nuovi.get('punti', []) if p['id'] not in ids_auto]
    tutti, visti = [], set()
    scartati = 0
    for gruppo in (curati, nuovi_p, auto):
        prima_del_gruppo = list(tutti)          # a point is checked only against higher-priority groups
        for p in gruppo:
            if p['id'] in visti:
                scartati += 1
                continue
            if gruppo is not curati and any(doppione(p, q) for q in prima_del_gruppo):
                scartati += 1
                continue
            visti.add(p['id'])
            tutti.append(p)

    # GDACS earthquake = USGS earthquake: keep USGS, add the GDACS alert to its note and sources
    usgs_p = [p for p in tutti if p['id'].startswith('USGS-')]
    tenere = []
    for p in tutti:
        if p['id'].startswith('GDACS-EQ-'):
            mg = re.search(r'Magnitude ([\d.]+)', p['esito'])
            cand = [q for q in usgs_p if doppione(p, q, raggio=100)]
            def scarto(q):
                mq = re.match(r'M([\d.]+)', q['nome'])
                dm = abs(float(mg.group(1)) - float(mq.group(1))) if (mg and mq) else 9
                return (round(dm, 1), km(p['lat'], p['lon'], q['lat'], q['lon']))
            gemello = min(cand, key=scarto) if cand else None
            if gemello:
                gemello['note'] += ' GDACS: %s.' % p['esito']
                gemello['fonti'].append({'fonte': p['fonte'], 'link': p['link'], 'data_fonte': p['data_fonte']})
                scartati += 1
                continue
        tenere.append(p)
    # GDACS cyclone = EONET storm with the same name: keep EONET (it has the track), add the alert
    eon = [p for p in tenere if p['id'].startswith('EONET-')]
    finale = []
    for p in tenere:
        if p['id'].startswith('GDACS-TC-'):
            nome = re.sub(r'-\d+$', '', (p['breve'].split()[-1] if p['breve'] else '')).lower()
            gemello = next((q for q in eon if nome and nome in q['nome'].lower()), None)
            if gemello:
                gemello['note'] += ' GDACS: %s.' % p['esito']
                gemello['fonti'].append({'fonte': p['fonte'], 'link': p['link'], 'data_fonte': p['data_fonte']})
                scartati += 1
                continue
        finale.append(p)

    limite = oggi - dt.timedelta(days=FINESTRA)
    finestra = [p for p in finale if p.get('strategico') or (p.get('data_evento') or '9999') >= limite.isoformat()]
    fuori_finestra = len(finale) - len(finestra)
    finestra.sort(key=lambda p: (p.get('data_evento') or '', p.get('ora_utc') or ''), reverse=True)

    conteggi = {'totale': len(finestra), 'curati_esistenti': sum(1 for p in finestra if p in curati),
                'curati_nuovi': sum(1 for p in finestra if p in nuovi_p), 'automatici': conta_feed,
                'scartati_doppioni': scartati, 'fuori_finestra': fuori_finestra, 'per_categoria': {}}
    for p in finestra:
        conteggi['per_categoria'][p['categoria']] = conteggi['per_categoria'].get(p['categoria'], 0) + 1

    fonti = [{'nome': 'Curated events before Nov 2026 (raccolta/eventi/curati.json; per-item sources)', 'link': 'raccolta/eventi/curati.json',
              'licenza': 'facts with per-item source and link', 'data_dato': base.get('aggiornato', '')},
             {'nome': 'Curated events from web research (raccolta/eventi/curati_nuovi.json; per-item sources)', 'link': 'raccolta/eventi/curati_nuovi.json',
              'licenza': 'facts with per-item source and link; Wikipedia Current events used as an index (CC BY-SA)', 'data_dato': nuovi.get('aggiornato', '')}] + fonti
    out = {'aggiornato': adesso.strftime('%Y-%m-%dT%H:%MZ'), 'raccolte': base.get('raccolte', []), 'fuori': base.get('fuori', {}),
           'fonti': fonti,
           'nota': ('World events that move geo-economic risk: maritime security, attacks on energy/shipping/ports, chokepoints, '
                    'airspace closures, blackouts, industrial accidents, port strikes, natural hazards hitting logistics. '
                    'Rolling window of %d days. Curated points: coordinates of the place named by the source '
                    '(origine_coord "stimata", radius precisione_km); automatic points: coordinates published by the source. '
                    'Ukraine front-line and city strikes live in attacchi-analisti.json / attacchi-russi.json, hybrid incidents in ibrido.json, '
                    'cable incidents in cavi-incidenti.json.') % FINESTRA,
           'conteggi': conteggi, 'errori': errori, 'punti': finestra}
    tmp = USCITA + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    json.load(open(tmp, encoding='utf-8'))
    os.replace(tmp, USCITA)
    print('eventi.json: %d points (%s), %d KB, errors: %d' % (len(finestra), json.dumps(conta_feed), os.path.getsize(USCITA) // 1024, len(errori)))


if __name__ == '__main__':
    main()
