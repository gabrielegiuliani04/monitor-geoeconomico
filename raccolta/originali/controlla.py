#!/usr/bin/env python3
"""Controllo dei livelli originali della mappa (solo libreria standard).

Valida docs/data/{fissi,italia,iran,difesa,mobili,eventi,ibrido}.json (punti) e
docs/data/{linee,condotte}.json (linee): campi obbligatori dello schema, coordinate,
date, link, affidabilita, stato. Segnala come «da rivedere» i punti con data_fonte
piu vecchia di 90 giorni e, per mobili.json, le posizioni piu vecchie di 14 giorni
non marcate come datate (campo dubbia).

Uso:
  python3 raccolta/originali/controlla.py              # controllo, rapporto a schermo
  python3 raccolta/originali/controlla.py --oggi 2026-11-10 --json raccolta/originali/controllo.json
  python3 raccolta/originali/controlla.py --rete       # prova anche a raggiungere i link (uno per dominio)

Uscita 0 se non ci sono errori, 1 se ce ne sono (gli avvisi non bloccano).
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request

RADICE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATI = os.path.join(RADICE, 'docs', 'data')
PUNTI = ['fissi', 'italia', 'iran', 'difesa', 'mobili', 'eventi', 'ibrido']
LINEE = ['linee', 'condotte']

# Le 25 colonne di regole/02_schema-dati.md, piu fonti[] (extra di mappa comune a tutti i livelli).
CAMPI = ['id', 'classe', 'categoria', 'nome', 'identificativo', 'appartenenza', 'stato', 'data_evento', 'ora_utc',
         'lat', 'lon', 'origine_coord', 'precisione_km', 'teatro', 'paese', 'regione', 'attore', 'bersaglio', 'mezzo',
         'esito', 'fonte', 'link', 'data_fonte', 'affidabilita', 'note', 'fonti']
NON_VUOTI = ['id', 'classe', 'categoria', 'nome', 'data_evento', 'fonte', 'link', 'data_fonte', 'affidabilita']
STATI = {'', 'operativo', 'in-costruzione', 'in-manutenzione', 'danneggiato', 'in-riparazione', 'fuori-servizio', 'lasciata'}
AFFIDABILITA = {'alta', 'media', 'bassa'}
CLASSI = {'fisso', 'mobile', 'evento'}
ORIGINI = {'fonte', 'stimata'}
TEATRI = {'MO', 'IT', 'NATO', 'RU-UA', 'ALTRO', 'EU'}
DATA = re.compile(r'^\d{4}-\d{2}-\d{2}$')
ORA = re.compile(r'^([01]\d|2[0-3]):[0-5]\d$')
LINK_TERZI = ('github.com/Yusnelkis',)          # copie di terzi del World Port Index
GIORNI_RIVEDERE = 90
GIORNI_MOBILI = 14


def data_ok(s):
    if not isinstance(s, str) or not DATA.match(s):
        return None
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        return None


def link_ok(s):
    if not isinstance(s, str) or not s:
        return False
    u = urllib.parse.urlparse(s)
    return u.scheme in ('http', 'https') and '.' in u.netloc and ' ' not in s


def dominio(s):
    n = urllib.parse.urlparse(s or '').netloc.lower()
    return n[4:] if n.startswith('www.') else n


def distanza(a, b, c, d):
    p = math.radians
    x = math.sin(p(c - a) / 2) ** 2 + math.cos(p(a)) * math.cos(p(c)) * math.sin(p(d - b) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(x))


class Rapporto:
    def __init__(self):
        self.r = {}

    def file(self, n):
        return self.r.setdefault(n, {'punti': 0, 'errori': [], 'avvisi': [], 'da_rivedere': []})

    def add(self, n, tipo, i, msg):
        self.file(n)[tipo].append(f'{i}: {msg}')


def controlla_punto(R, n, e, oggi, ids, basi_mondo):
    i = e.get('id', '?')
    for c in CAMPI:
        if c not in e:
            R.add(n, 'errori', i, f'manca il campo obbligatorio «{c}»')
    for c in NON_VUOTI:
        if c in e and (e[c] is None or e[c] == ''):
            R.add(n, 'errori', i, f'campo «{c}» vuoto')
    if i in ids:
        R.add(n, 'errori', i, 'id duplicato')
    ids.add(i)
    lat, lon = e.get('lat'), e.get('lon')
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)) or isinstance(lat, bool):
        R.add(n, 'errori', i, 'lat/lon non numerici')
    else:
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            R.add(n, 'errori', i, f'coordinate fuori range ({lat}, {lon})')
        if lat == 0 and lon == 0:
            R.add(n, 'errori', i, 'coordinate 0,0')
    if e.get('classe') not in CLASSI:
        R.add(n, 'errori', i, f'classe non valida «{e.get("classe")}»')
    if e.get('stato') not in STATI:
        R.add(n, 'errori', i, f'stato non riconosciuto dalla mappa «{e.get("stato")}»')
    if e.get('affidabilita') not in AFFIDABILITA:
        R.add(n, 'errori', i, f'affidabilita non valida «{e.get("affidabilita")}»')
    if e.get('origine_coord') not in ORIGINI:
        R.add(n, 'avvisi', i, f'origine_coord insolita «{e.get("origine_coord")}»')
    if e.get('teatro') not in TEATRI:
        R.add(n, 'avvisi', i, f'teatro insolito «{e.get("teatro")}»')
    p = e.get('paese', '')
    if p and not re.match(r'^[A-Z]{2}$', p):
        R.add(n, 'errori', i, f'paese non ISO a 2 lettere «{p}»')
    pk = e.get('precisione_km')
    if not isinstance(pk, (int, float)) or pk < 0:
        R.add(n, 'errori', i, 'precisione_km non valida')
    if e.get('ora_utc') and not ORA.match(e['ora_utc']):
        R.add(n, 'errori', i, f'ora_utc non valida «{e["ora_utc"]}»')
    domani = oggi + dt.timedelta(days=1)
    de = data_ok(e.get('data_evento'))
    if e.get('data_evento') and not de:
        R.add(n, 'errori', i, f'data_evento non valida «{e.get("data_evento")}»')
    elif de and de > domani:
        R.add(n, 'errori', i, f'data_evento nel futuro ({de})')
    df = data_ok(e.get('data_fonte'))
    if e.get('data_fonte') and not df:
        R.add(n, 'errori', i, f'data_fonte non valida «{e.get("data_fonte")}»')
    elif df and df > domani:
        R.add(n, 'errori', i, f'data_fonte nel futuro ({df})')
    if not link_ok(e.get('link')):
        R.add(n, 'errori', i, f'link principale non valido «{e.get("link")}»')
    if any(t in (e.get('link') or '') for t in LINK_TERZI):
        R.add(n, 'errori', i, 'link a una copia di terzi del World Port Index: usare msi.nga.mil')
    fonti = e.get('fonti')
    if not isinstance(fonti, list) or not fonti:
        R.add(n, 'errori', i, 'fonti[] vuoto o mancante')
        fonti = []
    date_fonti = []
    for k, f in enumerate(fonti):
        if not isinstance(f, dict) or not f.get('fonte'):
            R.add(n, 'errori', i, f'fonti[{k}] senza nome della fonte')
            continue
        if f.get('link') and not link_ok(f['link']):
            R.add(n, 'errori', i, f'fonti[{k}] link non valido «{f["link"]}»')
        if not f.get('link') and 'regia' not in f['fonte'].lower():
            R.add(n, 'avvisi', i, f'fonti[{k}] senza link ({f["fonte"][:50]})')
        if any(t in (f.get('link') or '') for t in LINK_TERZI):
            R.add(n, 'errori', i, f'fonti[{k}] punta a una copia di terzi del World Port Index')
        fd = data_ok(f.get('data_fonte'))
        if f.get('data_fonte') and not fd:
            R.add(n, 'errori', i, f'fonti[{k}] data_fonte non valida «{f.get("data_fonte")}»')
        elif not f.get('data_fonte'):
            R.add(n, 'avvisi', i, f'fonti[{k}] senza data ({f["fonte"][:50]})')
        elif fd > domani:
            R.add(n, 'errori', i, f'fonti[{k}] data nel futuro ({fd})')
        else:
            date_fonti.append(fd)
    if e.get('link') and fonti and not any(f.get('link') == e['link'] for f in fonti if isinstance(f, dict)):
        R.add(n, 'avvisi', i, 'il link principale non compare in fonti[]')
    # regola: alta solo con due fonti indipendenti o una fonte primaria (qui si controllano i domini)
    if e.get('affidabilita') == 'alta':
        dom = {dominio(f.get('link')) for f in fonti if isinstance(f, dict) and f.get('link')}
        dom.discard('ourairports.com'); dom.discard('wikidata.org'); dom.discard('openstreetmap.org')
        if len(dom) < 2:
            R.add(n, 'avvisi', i, 'affidabilita alta con una sola fonte (dominio) oltre agli archivi di coordinate: '
                                  'va bene solo se la fonte e primaria')
    # da rivedere: data_fonte oltre 90 giorni
    rif = df or (max(date_fonti) if date_fonti else None)
    if rif and (oggi - rif).days > GIORNI_RIVEDERE:
        R.add(n, 'da_rivedere', i, f'data_fonte {rif} ({(oggi - rif).days} giorni) - {e.get("nome", "")[:60]}')
    # navi e aerei: posizione oltre 14 giorni non marcata come datata
    if n == 'mobili' and de and (oggi - de).days > GIORNI_MOBILI and not e.get('dubbia'):
        R.add(n, 'errori', i, f'posizione del {de} ({(oggi - de).days} giorni) non marcata come datata (dubbia)')
    # duplicati con basi-mondo.json
    if n in ('fissi', 'italia', 'iran', 'difesa') and e.get('categoria') != 'porto' and isinstance(lat, (int, float)):
        for b in basi_mondo:
            if distanza(lat, lon, b['lat'], b['lon']) < 2:
                stesso = b.get('appartenenza') == e.get('appartenenza')
                R.add(n, 'errori' if stesso else 'avvisi', i,
                      f'entro 2 km da {b.get("id")} «{b.get("nome", "")[:40]}» di basi-mondo.json'
                      + (' con lo stesso utilizzatore: duplicato' if stesso else f' (utilizzatore diverso: {b.get("appartenenza")})'))


def controlla_linee(R, n, d, oggi):
    for c in ('aggiornato', 'fonte', 'versione', 'link', 'licenza', 'linee'):
        if c not in d:
            R.add(n, 'errori', 'file', f'manca «{c}»')
    lic = d.get('licenza', '')
    if 'CC BY 4.0' not in lic:
        R.add(n, 'errori', 'file', 'licenza: Global Energy Monitor pubblica i dati dei tracker in CC BY 4.0')
    if 'NC-SA' in lic and 'non sono riprodotti' not in lic:
        R.add(n, 'errori', 'file', 'licenza: cita gem.wiki CC BY-NC-SA come licenza dei dati')
    if not link_ok(d.get('link')):
        R.add(n, 'errori', 'file', 'link della fonte non valido')
    ids = set()
    for l in d.get('linee', []):
        i = l.get('id', '?')
        R.file(n)['punti'] += 1
        for c in ('id', 'categoria', 'nome', 'stato', 'g', 'link', 'data_fonte'):
            if c not in l:
                R.add(n, 'errori', i, f'manca «{c}»')
        if i in ids:
            R.add(n, 'errori', i, 'id duplicato')
        ids.add(i)
        if l.get('stato') not in STATI:
            R.add(n, 'errori', i, f'stato non riconosciuto «{l.get("stato")}»')
        if l.get('link') and not link_ok(l['link']):
            R.add(n, 'errori', i, 'link non valido')
        df = data_ok(l.get('data_fonte'))
        if l.get('data_fonte') and not df:
            R.add(n, 'errori', i, f'data_fonte non valida «{l.get("data_fonte")}»')
        elif df and df > oggi + dt.timedelta(days=1):
            R.add(n, 'errori', i, 'data_fonte nel futuro')
        g = l.get('g') or []
        if not g:
            R.add(n, 'errori', i, 'geometria vuota')
        cattive, decimali = 0, 0
        for parte in g:
            for pt in parte:
                if (not isinstance(pt, list) or len(pt) != 2 or not all(isinstance(v, (int, float)) for v in pt)
                        or not (-180 <= pt[0] <= 180) or not (-90 <= pt[1] <= 90)):
                    cattive += 1
                elif any(len(repr(float(v)).split('.')[1]) > 4 for v in pt):
                    decimali += 1
        if cattive:
            R.add(n, 'errori', i, f'{cattive} vertici non validi o fuori range [lon, lat]')
        if decimali:
            R.add(n, 'avvisi', i, f'{decimali} vertici con piu di 4 decimali')


def prova_link(R, file_link):
    """Una richiesta per dominio, solo con --rete."""
    visti = {}
    for n, i, u in file_link:
        dmn = dominio(u)
        if dmn in visti:
            continue
        try:
            req = urllib.request.Request(u, method='HEAD', headers={'User-Agent': 'monitor-geoeconomico/1.0 (controllo link)'})
            with urllib.request.urlopen(req, timeout=15) as r:
                visti[dmn] = r.status
        except Exception as ex:  # noqa: BLE001 - il controllo non deve mai fermarsi
            visti[dmn] = str(getattr(ex, 'code', ex))[:40]
            R.add(n, 'avvisi', i, f'link non raggiungibile oggi ({visti[dmn]}): {dmn}')
    return visti


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--oggi', help='data di riferimento AAAA-MM-GG (predefinita: oggi)')
    ap.add_argument('--json', help='scrive il rapporto completo in questo file JSON')
    ap.add_argument('--rete', action='store_true', help='prova a raggiungere i link (uno per dominio)')
    ap.add_argument('--max', type=int, default=8, help='righe per elenco nel rapporto a schermo')
    a = ap.parse_args()
    oggi = dt.date.fromisoformat(a.oggi) if a.oggi else dt.date.today()
    R = Rapporto()
    try:
        basi_mondo = json.load(open(os.path.join(DATI, 'basi-mondo.json'), encoding='utf-8')).get('elementi', [])
    except (OSError, ValueError):
        basi_mondo = []
        print('avviso: basi-mondo.json non letto, niente controllo dei duplicati')
    tutti_link = []
    for n in PUNTI:
        try:
            d = json.load(open(os.path.join(DATI, n + '.json'), encoding='utf-8'))
        except (OSError, ValueError) as ex:
            R.add(n, 'errori', 'file', f'non leggibile: {ex}')
            continue
        punti = d.get('punti')
        if not isinstance(punti, list):
            R.add(n, 'errori', 'file', 'manca la lista «punti»')
            continue
        if not data_ok(str(d.get('aggiornato', ''))[:10]):
            R.add(n, 'avvisi', 'file', 'campo «aggiornato» assente o non datato')
        ids = set()
        for e in punti:
            R.file(n)['punti'] += 1
            controlla_punto(R, n, e, oggi, ids, basi_mondo)
            tutti_link += [(n, e.get('id'), f.get('link')) for f in e.get('fonti', []) if isinstance(f, dict) and f.get('link')]
    for n in LINEE:
        try:
            controlla_linee(R, n, json.load(open(os.path.join(DATI, n + '.json'), encoding='utf-8')), oggi)
        except (OSError, ValueError) as ex:
            R.add(n, 'errori', 'file', f'non leggibile: {ex}')
    if a.rete:
        prova_link(R, tutti_link)

    tot_err = 0
    print(f'Controllo dei livelli originali al {oggi}')
    for n, v in R.r.items():
        tot_err += len(v['errori'])
        print(f'\n== {n}.json: {v["punti"]} elementi, {len(v["errori"])} errori, {len(v["avvisi"])} avvisi, '
              f'{len(v["da_rivedere"])} da rivedere (data_fonte oltre {GIORNI_RIVEDERE} giorni)')
        for tipo in ('errori', 'avvisi', 'da_rivedere'):
            for riga in v[tipo][:a.max]:
                print(f'  [{tipo}] {riga}')
            if len(v[tipo]) > a.max:
                print(f'  [{tipo}] ... altri {len(v[tipo]) - a.max}')
    if a.json:
        json.dump({'controllato': oggi.isoformat(), 'file': R.r}, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'\nRapporto completo: {a.json}')
    print(f'\nTotale errori: {tot_err}')
    return 1 if tot_err else 0


if __name__ == '__main__':
    sys.exit(main())
