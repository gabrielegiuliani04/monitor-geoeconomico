#!/usr/bin/env python3
"""Storico degli attacchi aerei a lungo raggio in Ucraina e in Russia.

Produce docs/data/ucraina-storico.json con:
  1. serie giornaliere dei missili e droni russi lanciati e abbattuti, per tipo
     (dataset "Massive Missile Attacks on Ukraine" di Petro Ivaniuk, basato sui
     comunicati dell'Aeronautica ucraina);
  2. punti degli attacchi ucraini a energia e basi aeree in Russia
     (curati a mano in raccolta/ucraina/attacchi_energia_russia.json);
  3. grandi ondate di attacchi russi alla rete energetica ucraina
     (curate a mano in raccolta/ucraina/ondate_rete_ucraina.json), con i numeri
     del dataset per ciascuna data.

Solo libreria standard. Fonti del dataset, nell'ordine:
  a) Kaggle API (serve KAGGLE_USERNAME e KAGGLE_KEY nell'ambiente; se mancano si salta);
  b) copia SQLite pubblica del progetto Narretz/sbs-stats (aggiornata ogni giorno
     dalla stessa API Kaggle, nessun login);
  c) copia CSV in un repository GitHub pubblico (meno aggiornata).
"""
import base64
import collections
import csv
import datetime as dt
import io
import json
import os
import sqlite3
import sys
import tempfile
import urllib.request
import zipfile

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, '..', '..'))
USCITA = os.path.join(RADICE, 'docs', 'data', 'ucraina-storico.json')
PUNTI = os.path.join(QUI, 'attacchi_energia_russia.json')
ONDATE = os.path.join(QUI, 'ondate_rete_ucraina.json')

KAGGLE_URL = 'https://www.kaggle.com/api/v1/datasets/download/piterfm/massive-missile-attacks-on-ukraine'
KAGGLE_PAGINA = 'https://www.kaggle.com/datasets/piterfm/massive-missile-attacks-on-ukraine'
R2_URL = 'https://pub-de9836bbd1a14affa2ecd7e998df13a2.r2.dev/ru-air-attacks-gsua.db'
R2_PAGINA = 'https://github.com/Narretz/sbs-stats/blob/main/scripts/missile_attacks/README.md'
GH_URL = 'https://raw.githubusercontent.com/ShadenAlrshoud/air-attacks-eda-dashboard/main/missile_attacks_daily.csv'
LICENZA = 'CC BY-NC-SA 4.0 (dataset di Petro Ivaniuk / piterfm su Kaggle; uso non commerciale, citare la fonte)'
UA = {'User-Agent': 'monitor-geoeconomico/1.0 (osservatorio OSINT personale)'}

errori = []


def scarica(url, headers=None, timeout=120):
    h = dict(UA)
    h.update(headers or {})
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
        return r.read()


# ---------------------------------------------------------------- lettura dati
def da_kaggle():
    user, key = os.environ.get('KAGGLE_USERNAME'), os.environ.get('KAGGLE_KEY')
    if not (user and key):
        raise RuntimeError('KAGGLE_USERNAME/KAGGLE_KEY non impostate: fonte saltata')
    tok = base64.b64encode(f'{user}:{key}'.encode()).decode()
    z = zipfile.ZipFile(io.BytesIO(scarica(KAGGLE_URL, {'Authorization': 'Basic ' + tok})))
    nome = [n for n in z.namelist() if n.endswith('missile_attacks_daily.csv')][0]
    return list(csv.DictReader(io.StringIO(z.read(nome).decode('utf-8'))))


def da_r2():
    dati = scarica(R2_URL, timeout=180)
    if not dati.startswith(b'SQLite format 3'):
        raise RuntimeError('il file scaricato non è un database SQLite')
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'm.db')
        with open(p, 'wb') as f:
            f.write(dati)
        con = sqlite3.connect(p)
        con.row_factory = sqlite3.Row
        righe = [dict(r) for r in con.execute('SELECT * FROM missile_attacks_latest')]
        ultimo = con.execute('SELECT MAX(scraped_at) FROM missile_attacks').fetchone()[0]
        con.close()
    for r in righe:
        r['_scaricato_da_mirror'] = ultimo
    return righe


def da_github():
    return list(csv.DictReader(io.StringIO(scarica(GH_URL).decode('utf-8'))))


# ---------------------------------------------------------------- classificazione
GRUPPI = {
    'shahed': 'Shahed/Geran (droni d\'attacco)',
    'droni_altri': 'altri droni (esche, ricognizione, Lancet, sconosciuti)',
    'kh101': 'Kh-101/Kh-555 (crociera, da bombardiere)',
    'kalibr': 'Kalibr (crociera, navale)',
    'iskander_k': 'Iskander-K (crociera, da terra)',
    'iskander_m': 'Iskander-M / KN-23 (balistici)',
    'kinzhal': 'Kh-47 Kinzhal (aerobalistico)',
    'kh22_kh32': 'Kh-22 / Kh-32 (crociera, supersonici)',
    'kh59_kh69': 'Kh-59 / Kh-69 (crociera, da aereo tattico)',
    's300_s400': 'S-300 / S-400 usati contro terra',
    'zircon_oniks': 'Zircon / Oniks',
    'kh31_kh35': 'Kh-31 / Kh-35',
    'banderol': 'S8000 Banderol',
    'missili_misti': 'missili di tipi diversi riportati insieme',
    'altro': 'altro',
}
TOKEN = [  # (sottostringa minuscola, gruppo, categoria)
    ('shahed', 'shahed', 'drone'), ('geran', 'shahed', 'drone'),
    ('kinzhal', 'kinzhal', 'balistico'), ('x-47', 'kinzhal', 'balistico'),
    ('iskander-k', 'iskander_k', 'crociera'), ('iskander-m', 'iskander_m', 'balistico'),
    ('kn-23', 'iskander_m', 'balistico'), ('ballistic', 'iskander_m', 'balistico'),
    ('x-101', 'kh101', 'crociera'), ('x-555', 'kh101', 'crociera'), ('kalibr', 'kalibr', 'crociera'),
    ('x-22', 'kh22_kh32', 'crociera'), ('x-32', 'kh22_kh32', 'crociera'),
    ('x-59', 'kh59_kh69', 'crociera'), ('x-69', 'kh59_kh69', 'crociera'),
    ('c-300', 's300_s400', 'balistico'), ('c-400', 's300_s400', 'balistico'),
    ('zircon', 'zircon_oniks', 'crociera'), ('oniks', 'zircon_oniks', 'crociera'),
    ('x-31', 'kh31_kh35', 'crociera'), ('x-35', 'kh31_kh35', 'crociera'),
    ('banderol', 'banderol', 'crociera'), ('dan-t', 'banderol', 'crociera'),
    ('missile', 'altro', 'crociera'), ('gbu', 'altro', 'altro'), ('bomb', 'altro', 'altro'),
]
PRIORITA = {'balistico': 3, 'crociera': 2, 'drone': 1, 'altro': 0}


def classifica(modello):
    gruppi, cats = [], []
    for t in [x.strip().lower() for x in (modello or '').split(' and ') if x.strip()]:
        g = c = None
        for s, gg, cc in TOKEN:
            if s in t:
                g, c = gg, cc
                break
        if g is None:  # nessun missile riconosciuto: è un drone (UAV, Lancet, Orlan, ZALA, Molnija...)
            g, c = 'droni_altri', 'drone'
        gruppi.append(g)
        cats.append(c)
    if not gruppi:
        return 'altro', 'altro'
    cat = max(cats, key=lambda c: PRIORITA[c])
    if len(set(gruppi)) == 1:
        return gruppi[0], cat
    if cat == 'drone':
        return ('shahed' if set(gruppi) == {'shahed'} else 'droni_altri'), cat
    return 'missili_misti', cat


def num(v):
    try:
        if v is None or str(v).strip() in ('', 'nan', 'None'):
            return None
        return int(float(v))
    except ValueError:
        return None


def nazionale(r):
    s = r.get('source') or ''
    return s.startswith('kpszsu/') or s.startswith('GeneralStaff.ua/')


def solo_geran(modello):
    toks = {t.strip() for t in (modello or '').split(' and ')}
    return bool(toks) and toks <= {'Geran-2', 'Geran-4', 'Geran-5', 'Shahed-136/131'}


def normalizza(righe):
    """Toglie i doppi conteggi e applica le regole su dati non divulgati.

    - Le righe dei comandi regionali con soli Shahed/Geran che cadono dentro la
      finestra di un comunicato nazionale sono già comprese nel totale nazionale
      (stessa regola della vista missile_attacks_counted di Narretz/sbs-stats).
    - Da agosto 2026 l'Aeronautica non pubblica alcune cifre: righe con
      status_data = 'hidden' e valore 0 sono 'non divulgato', non zero.
    """
    finestre = [(r['time_start'], r['time_end']) for r in righe
                if nazionale(r) and classifica(r.get('model'))[1] == 'drone'
                and len(r.get('time_start') or '') > 10 and len(r.get('time_end') or '') > 10]
    out, scartate = [], 0
    for r in righe:
        ts, te = r.get('time_start') or '', r.get('time_end') or ''
        if (not nazionale(r) and solo_geran(r.get('model')) and len(ts) > 10 and len(te) > 10
                and any(a < te and ts < b for a, b in finestre)):
            scartate += 1
            continue
        nascosto = (r.get('status_data') or '') == 'hidden'
        lan, abb = num(r.get('launched')), num(r.get('destroyed'))
        if nascosto and lan == 0:
            lan = None
        if nascosto and abb == 0:
            abb = None
        g, c = classifica(r.get('model'))
        out.append({'data': ts[:10], 'modello': r.get('model'), 'gruppo': g, 'cat': c,
                    'lanciati': lan, 'abbattuti': abb, 'nascosto': nascosto})
    return out, scartate


# ---------------------------------------------------------------- aggregazioni
def aggrega(righe):
    giorno = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    nascosti = set()
    for r in righe:
        d = r['data']
        if len(d) != 10:
            continue
        if r['nascosto'] and (r['lanciati'] is None or r['abbattuti'] is None):
            nascosti.add(d)
        for chiave in ('totale', 'cat_' + r['cat'], r['gruppo']):
            if r['lanciati'] is not None:
                giorno[d][chiave][0] += r['lanciati']
            if r['abbattuti'] is not None:
                giorno[d][chiave][1] += r['abbattuti']
    return giorno, sorted(nascosti)


def serie(giorno):
    chiavi = ['totale', 'cat_drone', 'cat_crociera', 'cat_balistico', 'cat_altro'] + list(GRUPPI)
    s = {}
    for k in chiavi:
        lan = [[d, giorno[d][k][0]] for d in sorted(giorno) if k in giorno[d]]
        abb = [[d, giorno[d][k][1]] for d in sorted(giorno) if k in giorno[d]]
        if lan:
            s[k] = {'lanciati': lan, 'abbattuti': abb}
    return s


def mensile(giorno):
    m = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for d, gs in giorno.items():
        for k, (a, b) in gs.items():
            m[k][d[:7]][0] += a
            m[k][d[:7]][1] += b
    out = {}
    for k, mesi in m.items():
        out[k] = [[mm, a, b, round(100 * b / a, 1) if a else None] for mm, (a, b) in sorted(mesi.items())]
    return out


# ---------------------------------------------------------------- curati a mano
CAMPI_PUNTO = ['lat', 'lon', 'nome', 'paese', 'categoria', 'stato', 'fonte', 'link', 'data_fonte', 'affidabilita', 'note']


def carica_punti():
    with open(PUNTI, encoding='utf-8') as f:
        doc = json.load(f)
    buoni = []
    for p in doc['punti']:
        manca = [c for c in CAMPI_PUNTO if c not in p]
        if manca or not isinstance(p['lat'], (int, float)) or not isinstance(p['lon'], (int, float)):
            errori.append(f"punto {p.get('id')} scartato: campi mancanti o non validi {manca}")
            continue
        p['lat'], p['lon'] = round(p['lat'], 4), round(p['lon'], 4)
        buoni.append(p)
    return buoni


def carica_ondate(giorno):
    with open(ONDATE, encoding='utf-8') as f:
        doc = json.load(f)
    out = []
    for o in doc['ondate']:
        d = dt.date.fromisoformat(o['data'])
        # la notte dell'attacco è registrata alla data d'inizio: guardo il giorno e quello prima
        cand = [x.isoformat() for x in (d - dt.timedelta(days=1), d)]
        best = max(cand, key=lambda x: giorno.get(x, {}).get('totale', [0, 0])[0])
        t = giorno.get(best, {})
        o = dict(o)
        o['dataset'] = {
            'data_registrata': best if best in giorno else None,
            'lanciati': t.get('totale', [None])[0], 'abbattuti': t.get('totale', [None, None])[1],
            'missili_lanciati': (t.get('cat_crociera', [0, 0])[0] + t.get('cat_balistico', [0, 0])[0]) if t else None,
            'droni_lanciati': t.get('cat_drone', [None])[0],
        }
        out.append(o)
    return out


# ---------------------------------------------------------------- principale
def main():
    fonti = []
    righe, usata = None, None
    for nome, fn, link in [('Kaggle API', da_kaggle, KAGGLE_PAGINA),
                           ('copia SQLite Narretz/sbs-stats (Cloudflare R2)', da_r2, R2_PAGINA),
                           ('copia CSV su GitHub (ShadenAlrshoud/air-attacks-eda-dashboard)', da_github, GH_URL)]:
        try:
            righe = fn()
            usata = (nome, link)
            print(f'fonte usata: {nome} ({len(righe)} righe)')
            break
        except Exception as e:  # noqa: BLE001 - si prova la fonte successiva
            msg = f'{nome}: {e}'
            print('avviso:', msg, file=sys.stderr)
            if 'saltata' not in str(e):
                errori.append(msg)
    if righe is None:
        errori.append('nessuna fonte del dataset raggiungibile: serie vuote')
        righe = []

    norm, scartate = normalizza(righe)
    giorno, nascosti = aggrega(norm)
    s = serie(giorno)
    mens = mensile(giorno)
    date = sorted(giorno)
    picchi = sorted(((d, gs['totale'][0], gs['totale'][1]) for d, gs in giorno.items()), key=lambda x: -x[1])[:20]
    tot_l = sum(gs['totale'][0] for gs in giorno.values())
    tot_a = sum(gs['totale'][1] for gs in giorno.values())
    aggiornamento_mirror = next((r.get('_scaricato_da_mirror') for r in righe if r.get('_scaricato_da_mirror')), None)

    punti = carica_punti()
    ondate = carica_ondate(giorno)

    fonti.append({'nome': 'Massive Missile Attacks on Ukraine (Petro Ivaniuk, da comunicati Aeronautica ucraina) - letto da: ' + (usata[0] if usata else 'nessuna'),
                  'link': KAGGLE_PAGINA, 'licenza': LICENZA,
                  'data_dato': f"{date[0]} / {date[-1]}" if date else 'nessuno',
                  'copia_usata': usata[1] if usata else None,
                  'copia_aggiornata': aggiornamento_mirror})
    fonti.append({'nome': 'Attacchi ucraini a energia e basi aeree in Russia (curati: Kyiv Independent, Wikipedia, Reuters/AP/Moscow Times/Meduza, Clément Molin, AMK Mapping)',
                  'link': 'raccolta/ucraina/attacchi_energia_russia.json', 'licenza': 'testi propri; coordinate OpenStreetMap Nominatim (ODbL); Wikipedia CC BY-SA',
                  'data_dato': max(p['data_evento'] for p in punti) if punti else ''})
    fonti.append({'nome': 'Ondate di attacchi russi alla rete energetica ucraina (curate)',
                  'link': 'raccolta/ucraina/ondate_rete_ucraina.json', 'licenza': 'testi propri con link alle fonti',
                  'data_dato': max(o['data'] for o in ondate) if ondate else ''})

    doc = {
        'aggiornato': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
        'fonti': fonti,
        'nota': ('Serie giornaliere dei missili e droni russi lanciati e abbattuti secondo l\'Aeronautica ucraina, dal 2022-09-28 '
                 '(prima del settembre 2022 il dataset non ha dati: il buco 24/2-27/9/2022 resta scoperto). Data = giorno di inizio '
                 'dell\'attacco (notte). Le cifre sono dichiarazioni di una delle parti. Dal 13/8/2026 l\'Aeronautica non pubblica '
                 'alcune cifre sui balistici: quei giorni sono in giorni_non_divulgati e i lanciati vanno letti come minimo. '
                 'Le righe regionali di soli Shahed/Geran già comprese nel comunicato nazionale sono tolte (' + str(scartate) + ' righe). '
                 'elementi = attacchi ucraini a raffinerie, depositi, porti, stazioni di pompaggio e basi aeree in Russia (punti).'),
        'gruppi': GRUPPI,
        'serie': s,
        'mensile': mens,
        'riepilogo': {
            'primo_giorno': date[0] if date else None, 'ultimo_giorno': date[-1] if date else None,
            'giorni_con_dati': len(date), 'lanciati_totali': tot_l, 'abbattuti_totali': tot_a,
            'tasso_abbattimento_pct': round(100 * tot_a / tot_l, 1) if tot_l else None,
            'picchi': [{'data': d, 'lanciati': a, 'abbattuti': b} for d, a, b in picchi],
            'giorni_non_divulgati': nascosti,
            'righe_lette': len(righe), 'righe_doppie_tolte': scartate,
        },
        'ondate_rete_ucraina': ondate,
        'elementi': punti,
        'errori': errori,
    }
    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    with open(USCITA, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, separators=(',', ':'))
    print(f'scritto {USCITA}: {os.path.getsize(USCITA) / 1e6:.2f} MB, {len(date)} giorni, {len(punti)} punti, {len(ondate)} ondate, errori: {len(errori)}')


if __name__ == '__main__':
    main()
