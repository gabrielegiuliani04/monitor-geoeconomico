#!/usr/bin/env python3
"""Attacchi russi in Ucraina (dal 24/2/2022): dove, con che cosa, contro che cosa.

Produce docs/data/attacchi-russi.json con:
  - elementi: eventi puntuali curati a mano (raccolta/ucraina/attacchi_russi_curati.json),
    validati qui (campi, date, coordinate dentro l'Ucraina, vocabolari);
  - per_oblast: per ogni oblast il centroide e due serie mensili
      * giorni_citati: giorni del mese in cui il dataset di Petro Ivaniuk (comunicati
        dell'Aeronautica e dei comandi regionali) cita l'oblast come bersaglio/direzione
        dell'attacco (campi target, target_main, "affected region");
      * eventi_curati: numero di eventi curati nel mese;
  - riepilogo: conteggi per anno, categoria e oblast.

Solo libreria standard. Fonti automatiche:
  - copia SQLite pubblica del dataset Ivaniuk (Narretz/sbs-stats su Cloudflare R2), oppure
    Kaggle se ci sono KAGGLE_USERNAME e KAGGLE_KEY. Licenza dati: CC BY-NC-SA 4.0.
  - opzionale, VIINA (Zhukov, ODbL) se la variabile d'ambiente VIINA=1: eventi geocodificati
    da notizie, filtrati su azioni russe con aerei/droni/artiglieria. Non provato da qui (il
    file e' su Git LFS e da questo ambiente non era scaricabile): se fallisce viene saltato.
ACLED non e' usato: i termini vietano di ripubblicare i dati grezzi.

Uso:  python3 raccolta/ucraina/attacchi_russi.py [--solo-valida]
"""
import ast
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
import base64

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, '..', '..'))
CURATI = os.path.join(QUI, 'attacchi_russi_curati.json')
USCITA = os.path.join(RADICE, 'docs', 'data', 'attacchi-russi.json')

R2_URL = 'https://pub-de9836bbd1a14affa2ecd7e998df13a2.r2.dev/ru-air-attacks-gsua.db'
R2_PAGINA = 'https://github.com/Narretz/sbs-stats/blob/main/scripts/missile_attacks/README.md'
KAGGLE_URL = 'https://www.kaggle.com/api/v1/datasets/download/piterfm/massive-missile-attacks-on-ukraine'
KAGGLE_PAGINA = 'https://www.kaggle.com/datasets/piterfm/massive-missile-attacks-on-ukraine'
VIINA_URL = 'https://github.com/zhukovyuri/VIINA/raw/master/Data/event_1pd_latest_{anno}.zip'
VIINA_PAGINA = 'https://github.com/zhukovyuri/VIINA'
UA = 'monitor-geoeconomico/1.0 (osservatorio OSINT personale, non commerciale)'

INIZIO = '2022-02-24'
CATEGORIE = {'energia', 'porto', 'ferrovia', 'industria', 'militare', 'civile/residenziale',
             'grano/logistica', 'altro'}
AFFIDABILITA = {'alta', 'media', 'bassa'}
CAMPI = ['id', 'data', 'lat', 'lon', 'precisione_km', 'citta', 'oblast', 'categoria', 'mezzi',
         'quanti', 'effetto', 'fonte', 'link', 'data_fonte', 'affidabilita']

# Centroidi delle oblast: punto rappresentativo restituito da OpenStreetMap Nominatim
# (interrogato il 9/11/2026; dati ODbL). Kyiv (citta') e' separata dall'oblast di Kyiv.
CENTROIDI = {
    'Cherkasy': (49.146, 31.227), 'Chernihiv': (51.273, 31.742), 'Chernivtsi': (48.381, 26.108),
    'Dnipropetrovsk': (48.663, 34.950), 'Donetsk': (47.921, 37.781), 'Ivano-Frankivsk': (48.748, 24.521),
    'Kharkiv': (49.830, 36.379), 'Kherson': (46.542, 33.408), 'Khmelnytskyi': (49.269, 27.064),
    'Kirovohrad': (48.192, 31.690), 'Kyiv': (50.179, 30.492), 'Kyiv (città)': (50.450, 30.524),
    'Luhansk': (49.272, 38.915), 'Lviv': (49.684, 23.897), 'Mykolaiv': (47.389, 31.944),
    'Odesa': (46.115, 29.957), 'Poltava': (49.861, 33.750), 'Rivne': (51.207, 26.521),
    'Sumy': (50.770, 34.329), 'Ternopil': (49.663, 25.617), 'Vinnytsia': (48.899, 28.516),
    'Volyn': (51.545, 24.663), 'Zakarpattia': (48.295, 23.447), 'Zaporizhzhia': (47.417, 35.923),
    'Zhytomyr': (50.908, 28.387),
}
# Nomi che compaiono nel dataset Ivaniuk (minuscolo) -> oblast
ALIAS = {
    'kyiv': 'Kyiv (città)', 'dnipro': 'Dnipropetrovsk', 'kryvyi rih': 'Dnipropetrovsk',
    'dnipropetrovsk oblas': 'Dnipropetrovsk', 'odesa': 'Odesa', 'snake island': 'Odesa',
    'kharkiv': 'Kharkiv', 'zaporizhzhia': 'Zaporizhzhia', 'kherson': 'Kherson', 'sumy': 'Sumy',
    'kramatorsk': 'Donetsk', 'ochakiv': 'Mykolaiv', 'starokostiantyniv': 'Khmelnytskyi',
    'kremenchuk': 'Poltava', 'kolomyia': 'Ivano-Frankivsk', 'lutsk': 'Volyn', 'lutsk oblast': 'Volyn',
    'vinnytsia': 'Vinnytsia', 'kyiv oblast (south)': 'Kyiv', 'lviv': 'Lviv', 'mykolaiv': 'Mykolaiv',
    'poltava': 'Poltava', 'chernihiv': 'Chernihiv',
}
# lettere cirilliche finite per errore nei nomi latini del dataset (es. 'оblast', 'obкlast')
OMOGLIFI = str.maketrans({'о': 'o', 'а': 'a', 'е': 'e', 'і': 'i', 'с': 'c', 'р': 'p', 'к': ''})
IGNORA = {'ukraine', 'south', 'north', 'east', 'west', 'center', 'centre', 'front line',
          'north-east', 'south-east', 'black sea', 'kursk oblast', ''}


def scarica(url, headers=None, timeout=180):
    h = {'User-Agent': UA}
    h.update(headers or {})
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
        return r.read()


# ---------------------------------------------------------------- parte curata
def valida(curati, oggi):
    validi, errori, visti = [], [], set()
    for i, e in enumerate(curati.get('eventi', [])):
        problemi = [c for c in CAMPI if c not in e]
        try:
            d = dt.date.fromisoformat(e.get('data', ''))
            if not (INIZIO <= d.isoformat() <= oggi):
                problemi.append('data fuori intervallo')
        except ValueError:
            problemi.append('data non valida')
        try:
            dt.date.fromisoformat(e.get('data_fonte', ''))
        except ValueError:
            problemi.append('data_fonte non valida')
        lat, lon = e.get('lat'), e.get('lon')
        if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float))
                and 44.0 <= lat <= 52.5 and 22.0 <= lon <= 40.5):
            problemi.append('coordinate fuori dall\'Ucraina')
        if e.get('categoria') not in CATEGORIE:
            problemi.append('categoria sconosciuta')
        if e.get('affidabilita') not in AFFIDABILITA:
            problemi.append('affidabilita sconosciuta')
        if e.get('oblast') not in CENTROIDI:
            problemi.append('oblast sconosciuta')
        if not str(e.get('link', '')).startswith('http'):
            problemi.append('link mancante')
        if not isinstance(e.get('precisione_km'), (int, float)):
            problemi.append('precisione_km mancante')
        if e.get('quanti') is not None and not isinstance(e.get('quanti'), int):
            problemi.append('quanti non intero')
        if e.get('id') in visti:
            problemi.append('id duplicato')
        visti.add(e.get('id'))
        if problemi:
            errori.append(f"evento {i} ({e.get('id')}): {', '.join(problemi)}")
        else:
            validi.append(e)
    return validi, errori


# ------------------------------------------------------------ dataset Ivaniuk
def righe_ivaniuk():
    """Righe (attack_date, target, target_main, affected) dalla copia R2 o da Kaggle."""
    tmp = tempfile.mkdtemp()
    utente, chiave = os.environ.get('KAGGLE_USERNAME'), os.environ.get('KAGGLE_KEY')
    if utente and chiave:
        try:
            auth = base64.b64encode(f'{utente}:{chiave}'.encode()).decode()
            z = zipfile.ZipFile(io.BytesIO(scarica(KAGGLE_URL, {'Authorization': 'Basic ' + auth})))
            nome = [n for n in z.namelist() if n.endswith('missile_attacks_daily.csv')][0]
            testo = z.read(nome).decode('utf-8', 'replace')
            out = [(r.get('time_start', '')[:10], r.get('target', ''), r.get('target_main', ''),
                    r.get('affected region', '')) for r in csv.DictReader(io.StringIO(testo))]
            return out, {'nome': 'Kaggle (originale)', 'link': KAGGLE_PAGINA}
        except Exception as ex:  # noqa: BLE001
            print('Kaggle non disponibile, uso la copia R2:', ex, file=sys.stderr)
    p = os.path.join(tmp, 'ivaniuk.db')
    with open(p, 'wb') as f:
        f.write(scarica(R2_URL))
    con = sqlite3.connect(p)
    out = list(con.execute('SELECT attack_date, target, target_main, "affected region" '
                           'FROM missile_attacks_latest'))
    copia = con.execute('SELECT MAX(scraped_at) FROM missile_attacks').fetchone()[0]
    con.close()
    return out, {'nome': 'copia SQLite Narretz/sbs-stats (Cloudflare R2)', 'link': R2_PAGINA,
                 'copia_aggiornata': copia}


def oblast_da_testo(testo, sconosciuti):
    """'Odesa oblast and Mykolaiv oblast' / "['Kharkiv oblast', ...]" -> {oblast}"""
    testo = (testo or '').strip()
    if not testo:
        return set()
    parti = []
    if testo.startswith('['):
        try:
            parti = [str(x) for x in ast.literal_eval(testo)]
        except (ValueError, SyntaxError):
            parti = [testo]
    else:
        for p in testo.replace(' and ', '|').split('|'):
            parti.append(p)
    trovati = set()
    for p in parti:
        p = p.split(',')[0].strip().lower().translate(OMOGLIFI)
        if p in IGNORA:
            continue
        if p in ALIAS:
            trovati.add(ALIAS[p])
            continue
        if p.endswith(' oblast'):
            nome = p[:-7].strip()
            cand = [o for o in CENTROIDI if o.lower() == nome]
            if cand:
                trovati.add(cand[0])
                continue
        sconosciuti[p] = sconosciuti.get(p, 0) + 1
    return trovati


def giorni_per_oblast(righe):
    giorni, sconosciuti = {}, {}
    for data, *campi in righe:
        if not data or data < INIZIO:
            continue
        for c in campi:
            for o in oblast_da_testo(c, sconosciuti):
                giorni.setdefault(o, set()).add(data[:10])
    return giorni, sconosciuti


# ------------------------------------------------------------- VIINA (opzionale)
def viina_per_oblast(oggi):
    """Eventi VIINA 'one-per-day' iniziati da forze russe con aerei, droni o artiglieria."""
    conteggi = {}
    nomi = {o.lower(): o for o in CENTROIDI}
    nomi.update({'kiev': 'Kyiv', 'kyiv city': 'Kyiv (città)', 'kiev city': 'Kyiv (città)',
                 'odessa': 'Odesa', 'zaporizhia': 'Zaporizhzhia', 'zaporizhzhya': 'Zaporizhzhia',
                 'dnipropetrovs\'k': 'Dnipropetrovsk', 'kharkiv': 'Kharkiv'})
    for anno in range(2022, int(oggi[:4]) + 1):
        z = zipfile.ZipFile(io.BytesIO(scarica(VIINA_URL.format(anno=anno))))
        testo = z.read(z.namelist()[0]).decode('utf-8', 'replace')
        for r in csv.DictReader(io.StringIO(testo)):
            if r.get('a_rus_init') != '1':
                continue
            if not any(r.get(k) == '1' for k in ('t_airstrike', 't_uav', 't_artillery')):
                continue
            nome = (r.get('ADM1_NAME') or '').lower().replace(' oblast', '').strip()
            o = nomi.get(nome)
            d = r.get('date', '')
            if not o or len(d) != 8:
                continue
            mese = f'{d[:4]}-{d[4:6]}-01'
            conteggi.setdefault(o, {}).setdefault(mese, 0)
            conteggi[o][mese] += 1
    return conteggi


# ------------------------------------------------------------------- uscita
def mesi(da, a):
    y, m = int(da[:4]), int(da[5:7])
    while f'{y:04d}-{m:02d}' <= a[:7]:
        yield f'{y:04d}-{m:02d}-01'
        m += 1
        if m == 13:
            y, m = y + 1, 1


def main():
    oggi = dt.date.today().isoformat()
    errori = []
    with open(CURATI, encoding='utf-8') as f:
        curati = json.load(f)
    eventi, err = valida(curati, oggi)
    errori += err
    print(f'Curati: {len(eventi)} validi, {len(err)} scartati', file=sys.stderr)
    if '--solo-valida' in sys.argv:
        for e in err:
            print('  ', e, file=sys.stderr)
        sys.exit(1 if err else 0)

    fonti = [{
        'nome': 'Eventi curati a mano (raccolta/ucraina/attacchi_russi_curati.json): Kyiv Independent; '
                'Reuters, AP, Ukrainska Pravda, France 24, ABC, United24 tramite Wikipedia «Odesa strikes (2022–present)»',
        'link': 'https://kyivindependent.com/',
        'licenza': 'fatti con link alla fonte e testi propri brevi; coordinate © OpenStreetMap contributors (ODbL)',
        'data_dato': max(e['data'] for e in eventi) if eventi else ''}]

    giorni, sconosciuti, info = {}, {}, None
    try:
        righe, info = righe_ivaniuk()
        giorni, sconosciuti = giorni_per_oblast(righe)
        tutte = sorted({d for s in giorni.values() for d in s})
        fonti.append({
            'nome': 'Massive Missile Attacks on Ukraine (Petro Ivaniuk) - campi target, target_main, '
                    'affected region; letto da: ' + info['nome'],
            'link': KAGGLE_PAGINA, 'copia_usata': info['link'],
            'licenza': 'CC BY-NC-SA 4.0 (citare Petro Ivaniuk; uso non commerciale; derivati con la stessa licenza)',
            'data_dato': f'{tutte[0]} / {tutte[-1]}' if tutte else '',
            **({'copia_aggiornata': info['copia_aggiornata']} if info.get('copia_aggiornata') else {})})
    except Exception as ex:  # noqa: BLE001
        errori.append(f'dataset Ivaniuk non disponibile: {ex}')

    viina = {}
    if os.environ.get('VIINA') == '1':
        try:
            viina = viina_per_oblast(oggi)
            fonti.append({'nome': 'VIINA 2.0 (Zhukov e Ayers), eventi one-per-day',
                          'link': VIINA_PAGINA, 'licenza': 'ODbL 1.0 (attribuzione, share-alike)',
                          'data_dato': oggi})
        except Exception as ex:  # noqa: BLE001
            errori.append(f'VIINA non disponibile: {ex}')

    # serie mensili per oblast
    per_mese_ev = {}
    for e in eventi:
        per_mese_ev.setdefault(e['oblast'], {}).setdefault(e['data'][:7] + '-01', 0)
        per_mese_ev[e['oblast']][e['data'][:7] + '-01'] += 1
    per_oblast = []
    for o, (lat, lon) in sorted(CENTROIDI.items()):
        cont = {}
        for d in giorni.get(o, ()):
            cont[d[:7] + '-01'] = cont.get(d[:7] + '-01', 0) + 1
        voce = {'oblast': o, 'lat': lat, 'lon': lon,
                'origine_coord': 'OpenStreetMap Nominatim (punto rappresentativo dell\'oblast)',
                'giorni_citati': [[m, cont[m]] for m in mesi(INIZIO, oggi) if m in cont],
                'eventi_curati': sorted([m, n] for m, n in per_mese_ev.get(o, {}).items()),
                'totale_giorni_citati': sum(cont.values()),
                'totale_eventi_curati': sum(per_mese_ev.get(o, {}).values())}
        if viina:
            voce['eventi_viina'] = sorted([m, n] for m, n in viina.get(o, {}).items())
        per_oblast.append(voce)

    # riepilogo
    anni = sorted({e['data'][:4] for e in eventi})
    riepilogo = {'eventi_per_anno_categoria': {}, 'eventi_per_anno_oblast': {}, 'giorni_citati_per_anno_oblast': {}}
    for a in anni:
        sel = [e for e in eventi if e['data'][:4] == a]
        cat, obl = {}, {}
        for e in sel:
            cat[e['categoria']] = cat.get(e['categoria'], 0) + 1
            obl[e['oblast']] = obl.get(e['oblast'], 0) + 1
        riepilogo['eventi_per_anno_categoria'][a] = dict(sorted(cat.items(), key=lambda x: -x[1]))
        riepilogo['eventi_per_anno_oblast'][a] = dict(sorted(obl.items(), key=lambda x: -x[1]))
    for o, s in giorni.items():
        for d in s:
            riepilogo['giorni_citati_per_anno_oblast'].setdefault(d[:4], {}).setdefault(o, 0)
            riepilogo['giorni_citati_per_anno_oblast'][d[:4]][o] += 1
    for a in riepilogo['giorni_citati_per_anno_oblast']:
        riepilogo['giorni_citati_per_anno_oblast'][a] = dict(sorted(
            riepilogo['giorni_citati_per_anno_oblast'][a].items(), key=lambda x: -x[1]))
    riepilogo['giorni_citati_per_anno_oblast'] = dict(sorted(riepilogo['giorni_citati_per_anno_oblast'].items()))
    if sconosciuti:
        riepilogo['nomi_non_attribuiti_ivaniuk'] = dict(sorted(sconosciuti.items(), key=lambda x: -x[1])[:15])

    out = {
        'aggiornato': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
        'fonti': fonti,
        'nota': ("elementi = attacchi russi curati a mano (date, luoghi, mezzi ed effetti come riportati dalla fonte; "
                 "coordinate del centro abitato o dell'oblast, non del punto d'impatto: vedi precisione_km). "
                 "Non sono tutti gli attacchi: sono eventi chiave scelti con priorita' a energia, porti, ferrovie e logistica. "
                 "per_oblast.giorni_citati = giorni del mese in cui i comunicati dell'Aeronautica ucraina e dei comandi "
                 "regionali (dataset Ivaniuk) indicano l'oblast come bersaglio o direzione dell'attacco: e' un indicatore "
                 "di pressione, non di colpi andati a segno; il campo e' compilato solo in una parte delle righe "
                 "(soprattutto comando Sud, 2023-2024) e il dataset parte dal 28/9/2022. "
                 "per_oblast.eventi_curati = eventi del file per mese. Serie mensili [AAAA-MM-01, valore]. "
                 "Le ondate nazionali contro la rete sono in ucraina-storico.json (ondate_rete_ucraina). "
                 "Licenza: la parte derivata dal dataset Ivaniuk e' CC BY-NC-SA 4.0; coordinate ODbL."),
        'categorie': sorted(CATEGORIE),
        'elementi': sorted(eventi, key=lambda e: (e['data'], e['id'])),
        'per_oblast': per_oblast,
        'riepilogo': riepilogo,
        'errori': errori,
    }
    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    with open(USCITA, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print(f'Scritto {USCITA}: {len(eventi)} eventi, {len(per_oblast)} oblast, '
          f'{os.path.getsize(USCITA) / 1e6:.2f} MB, errori: {len(errori)}', file=sys.stderr)


if __name__ == '__main__':
    main()
