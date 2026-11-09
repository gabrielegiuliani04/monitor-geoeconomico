#!/usr/bin/env python3
"""Agente FERROVIE: rete ferroviaria principale + corridoi strategici + incidenti.

Solo libreria standard. Scrive docs/data/ferrovie.json.

Fonti:
- Natural Earth 10m railroads (pubblico dominio), via GitHub nvkelso/natural-earth-vector
  (fallback: jsDelivr). Si tengono le linee principali (category=1) nell'area
  Europa - Russia - Medio Oriente - Asia centrale - Cina, si uniscono i tratti
  contigui e si semplificano con Douglas-Peucker.
- Corridoi strategici e incidenti: schede curate a mano in questo file, ognuna con
  fonte, link e data (aggiornarle a mano quando escono dati nuovi).
- Collegamenti con docs/data/ibrido.json: punti del livello "attacchi ibridi" che
  stanno entro DIST_KM da una linea ferroviaria o che citano la ferrovia nel testo.
"""
import json
import math
import os
import sys
import urllib.request
from datetime import datetime, timezone

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
USCITA = os.path.join(RADICE, "docs", "data", "ferrovie.json")
IBRIDO = os.path.join(RADICE, "docs", "data", "ibrido.json")

NE_URLS = [
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_railroads.geojson",
    "https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@master/geojson/ne_10m_railroads.geojson",
]
BBOX = (-11.0, 12.0, 135.0, 72.0)   # lon_min, lat_min, lon_max, lat_max
CATEGORIE = {1, 2}                    # Natural Earth: 1 e 2 = linee principali e secondarie importanti (3 = minori)
TOLL = 0.012                          # tolleranza Douglas-Peucker in gradi
MIN_LUNG_KM = 15                      # scarta pezzi isolati piu' corti
DIST_KM = 2.0                         # soglia per collegare un punto ibrido a una ferrovia
CAT_VICINANZA = {"sabotaggio"}        # solo questi eventi ibridi si collegano per sola vicinanza
LIMITE_BYTE = 1_450_000

errori = []


def scarica(urls, timeout=120):
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "monitor-geoeconomico/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return u, r.read()
        except Exception as e:  # noqa: BLE001
            errori.append(f"download fallito {u}: {e}")
    return None, None


def km(a, b):
    lon1, lat1 = map(math.radians, a)
    lon2, lat2 = map(math.radians, b)
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * math.asin(min(1, math.sqrt(h)))


def dp(pts, tol):
    """Douglas-Peucker iterativo."""
    if len(pts) < 3:
        return pts
    tieni = [False] * len(pts)
    tieni[0] = tieni[-1] = True
    pila = [(0, len(pts) - 1)]
    while pila:
        i, j = pila.pop()
        ax, ay = pts[i]
        bx, by = pts[j]
        dx, dy = bx - ax, by - ay
        n = dx * dx + dy * dy
        dmax, imax = -1.0, -1
        for k in range(i + 1, j):
            px, py = pts[k]
            if n == 0:
                d = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / n))
                d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2
            if d > dmax:
                dmax, imax = d, k
        if dmax > tol * tol:
            tieni[imax] = True
            pila += [(i, imax), (imax, j)]
    return [p for p, t in zip(pts, tieni) if t]


def unisci(linee):
    """Unisce i tratti che si toccano in nodi di grado 2 (line merge semplice)."""
    chiave = lambda p: (round(p[0], 4), round(p[1], 4))  # noqa: E731
    grado = {}
    for l in linee:
        for p in (l[0], l[-1]):
            grado[chiave(p)] = grado.get(chiave(p), 0) + 1
    per_nodo = {}
    for i, l in enumerate(linee):
        for p in (l[0], l[-1]):
            per_nodo.setdefault(chiave(p), []).append(i)
    usata = [False] * len(linee)
    out = []
    for i in range(len(linee)):
        if usata[i]:
            continue
        usata[i] = True
        cur = list(linee[i])
        for verso in (0, 1):
            while True:
                fine = chiave(cur[-1])
                if grado.get(fine) != 2:
                    break
                cand = [j for j in per_nodo[fine] if not usata[j]]
                if not cand:
                    break
                j = cand[0]
                usata[j] = True
                l = linee[j]
                cur += (l[1:] if chiave(l[0]) == fine else l[::-1][1:])
            cur.reverse()
        out.append(cur)
    return out


def macroarea(lon, lat):
    """Etichetta indicativa per riquadri (non confini politici)."""
    if lon < 28 or (lon < 40 and lat > 41.5 and lat < 47.5 and lon < 33):
        return "Europa"
    if lat >= 50 and lon >= 28:
        return "Russia e Bielorussia/Ucraina settentrionale" if lon < 40 else "Russia"
    if lon < 40 and lat >= 44:
        return "Ucraina e Russia meridionale"
    if lat < 42 and lon < 63:
        return "Medio Oriente e Caucaso/Anatolia"
    if lon >= 73 and lat < 50 and not (lon < 80 and lat > 40):
        return "Cina e Asia orientale"
    if lat < 36 and lon < 73:
        return "Medio Oriente e Caucaso/Anatolia"
    return "Asia centrale e Caucaso" if lat < 50 else "Russia"


def dentro(p):
    return BBOX[0] <= p[0] <= BBOX[2] and BBOX[1] <= p[1] <= BBOX[3]


def costruisci_rete():
    url, raw = scarica(NE_URLS)
    if raw is None:
        return None, []
    d = json.loads(raw)
    tratti = []
    for f in d.get("features", []):
        pr = f.get("properties") or {}
        if pr.get("category") not in CATEGORIE:
            continue
        g = f.get("geometry") or {}
        parti = [g["coordinates"]] if g.get("type") == "LineString" else g.get("coordinates", [])
        for cs in parti:
            # taglio al bbox: si tengono le sequenze di punti interni
            seq = []
            for p in cs:
                if dentro(p):
                    seq.append((p[0], p[1]))
                else:
                    if len(seq) > 1:
                        tratti.append((seq, pr))
                    seq = []
            if len(seq) > 1:
                tratti.append((seq, pr))
    # gruppi per elettrificazione/doppio binario (attributi Natural Earth)
    gruppi = {}
    for seq, pr in tratti:
        k = (pr.get("mult_track", 0), pr.get("electric", 0))
        gruppi.setdefault(k, []).append(seq)
    elementi = {}
    for (mt, el), linee in gruppi.items():
        for l in unisci(linee):
            lung = sum(km(l[i], l[i + 1]) for i in range(len(l) - 1))
            if lung < MIN_LUNG_KM:
                continue
            s = dp(l, TOLL)
            s = [[round(x, 3), round(y, 3)] for x, y in s]
            s = [p for i, p in enumerate(s) if i == 0 or p != s[i - 1]]
            if len(s) < 2:
                continue
            mid = l[len(l) // 2]
            area = macroarea(*mid)
            k = (area, mt, el)
            e = elementi.setdefault(k, {"g": [], "km": 0.0})
            e["g"].append(s)
            e["km"] += lung
    desc_mt = {0: "binario non indicato", 1: "binario singolo", 2: "binario multiplo"}
    desc_el = {0: "elettrificazione non indicata", 1: "non elettrificata", 2: "elettrificata"}
    out = []
    for i, ((area, mt, el), e) in enumerate(sorted(elementi.items())):
        out.append({
            "id": f"FR-NE-{i + 1:03d}",
            "categoria": "ferrovia-principale",
            "nome": f"Linee principali - {area}",
            "macroarea": area,
            "binari": desc_mt.get(mt, str(mt)),
            "elettrificazione": desc_el.get(el, str(el)),
            "km": round(e["km"]),
            "fonte": "Natural Earth 10m railroads",
            "link": "https://www.naturalearthdata.com/downloads/10m-cultural-vectors/railroads/",
            "affidabilita": "media",
            "tracciato": "generalizzato 1:10m, semplificato (tolleranza ~1 km)",
            "g": e["g"],
        })
    return url, out


# ---------------------------------------------------------------------------
# Corridoi strategici (schede curate: ogni numero ha fonte, link e data)
# g = tracciato SCHEMATICO tra nodi principali (citta' collegate in linea retta),
# non e' il binario reale: serve solo a disegnare il corridoio sopra la rete.
# ---------------------------------------------------------------------------
CORRIDOI = [
    {
        "id": "FR-COR-01",
        "nome": "Ferrovia Cina-Europa (China-Europe Railway Express), rotta settentrionale",
        "paesi": ["CN", "KZ", "RU", "BY", "PL", "DE"],
        "stato": "operativo; il transito attraversa Russia e Bielorussia (rischio sanzioni e sicurezza al confine BY-PL)",
        "nodi": [["Xi'an", 108.94, 34.27], ["Urumqi", 87.62, 43.83], ["Dostyk/Alashankou", 82.5, 45.2],
                 ["Astana", 71.45, 51.17], ["Mosca", 37.62, 55.75], ["Minsk", 27.56, 53.9],
                 ["Brest/Małaszewicze", 23.6, 52.07], ["Varsavia", 21.01, 52.23], ["Duisburg", 6.76, 51.43]],
        "volumi": [
            {"voce": "treni nel 2025", "valore": 20022, "unita": "treni", "anno": "2025",
             "trend": "+3,2% sul 2024 (Railmarket); 1.702 nel 2016",
             "fonte": "CGTN su dati China State Railway Group",
             "link": "https://news.cgtn.com/news/2026-06-19/China-Europe-freight-train-trips-up-10-8-fold-in-a-decade-1O6lmqO1Ka4/p.html",
             "data_fonte": "2026-06-19", "affidabilita": "alta"},
            {"voce": "TEU trasportati nel 2025", "valore": 2050000, "unita": "TEU", "anno": "2025",
             "trend": "-1,3% sul 2024; 9.898 treni in andata e 10.124 di ritorno (i ritorni superano le andate)",
             "fonte": "Railmarket", "link": "https://railmarket.com/news/freight-rail/51534",
             "data_fonte": "2026", "affidabilita": "media",
             "nota": "valore 'oltre 2,05 milioni'; non confermato da una seconda fonte"},
            {"voce": "treni gennaio-marzo 2026", "valore": 5460, "unita": "treni", "anno": "2026 T1",
             "trend": "+29% treni e +22% TEU (546.000 TEU) sul T1 2025",
             "fonte": "Index1520 / China State Railway Group",
             "link": "https://index1520.com/en/news/obemy-perevozok-po-marshrutu-kitay-evropa-vyrosli-na-chetvert-za-pervye-dva-mesyatsa-2026-goda/",
             "data_fonte": "2026-04", "affidabilita": "media"},
        ],
    },
    {
        "id": "FR-COR-02",
        "nome": "Middle Corridor / Trans-Caspian International Transport Route (TITR)",
        "paesi": ["CN", "KZ", "AZ", "GE", "TR"],
        "stato": "operativo con trasbordo navale sul Caspio (Aktau/Kuryk - Baku/Alat); ferrovia Baku-Tbilisi-Kars attiva",
        "nodi": [["Xi'an", 108.94, 34.27], ["Khorgos", 80.4, 44.2], ["Almaty", 76.89, 43.24],
                 ["Aktau", 51.2, 43.65], ["Baku/Alat", 49.4, 39.95], ["Tbilisi", 44.79, 41.72],
                 ["Kars", 43.1, 40.6], ["Istanbul", 28.98, 41.01]],
        "volumi": [
            {"voce": "merci 2025", "valore": 4.7, "unita": "milioni di tonnellate", "anno": "2025",
             "trend": "4,484 Mt nel 2024 (ministero dei Trasporti del Kazakhstan); altre stime 2025 tra 4,5 e 5,2 Mt",
             "fonte": "Organizzazione degli Stati turchi (riportato da BESA Center)",
             "link": "https://besacenter.org/azerbaijan-uses-the-middle-corridor-to-consolidate/",
             "data_fonte": "2026", "affidabilita": "media",
             "nota": "le cifre misurano cose diverse (solo ferrovia, transito, flussi multipaese): non confrontabili"},
            {"voce": "merci su ferrovie azere lungo la rotta Est-Ovest, gen-set 2025", "valore": 2.651,
             "unita": "milioni di tonnellate", "anno": "2025 (9 mesi)", "trend": "+6% anno su anno",
             "fonte": "Report.az (Ferrovie dell'Azerbaigian)",
             "link": "https://report.az/en/infrastructure/cargo-shipment-via-azerbaijan-s-railways-along-middle-corridor-up-6",
             "data_fonte": "2025-10", "affidabilita": "media"},
            {"voce": "obiettivo 2030", "valore": 11.4, "unita": "milioni di tonnellate", "anno": "2030",
             "trend": "obiettivo, non dato", "fonte": "Railmarket / BCG",
             "link": "https://railmarket.com/news/freight-rail/42407-transit-volumes-on-the-middle-corridor-forecast-to-quadruple-by-end-of-decade",
             "data_fonte": "2025", "affidabilita": "bassa"},
        ],
    },
    {
        "id": "FR-COR-03",
        "nome": "INSTC ramo occidentale (Russia - Azerbaigian - Iran - India), anello mancante Rasht-Astara",
        "paesi": ["RU", "AZ", "IR", "IN"],
        "stato": "parziale: manca il tratto Rasht-Astara (162 km). Avvio lavori slittato al 2027, completamento in circa 3 anni (RZD, ottobre 2026); prestito russo di 1,6 miliardi (valuta indicata in modo diverso dalle fonti)",
        "nodi": [["Mosca", 37.62, 55.75], ["Astrakhan", 48.03, 46.35], ["Makhachkala", 47.5, 42.98],
                 ["Baku", 49.87, 40.41], ["Astara", 48.87, 38.43], ["Rasht", 49.58, 37.28],
                 ["Qazvin", 50.0, 36.27], ["Teheran", 51.39, 35.69], ["Bandar Abbas", 56.27, 27.18]],
        "volumi": [
            {"voce": "traffico ferroviario lungo l'INSTC 2024", "valore": 12.9, "unita": "milioni di tonnellate",
             "anno": "2024", "trend": "dato 2025 completo non trovato",
             "fonte": "Ferrovie russe (RZD), riportato da Gulf Research Center",
             "link": "https://www.grc.net/single-commentary/302", "data_fonte": "2025", "affidabilita": "media"},
            {"voce": "obiettivo transito Russia-Azerbaigian-Iran", "valore": 15, "unita": "milioni di tonnellate/anno",
             "anno": "obiettivo", "trend": "roadmap firmata a ottobre 2025",
             "fonte": "Caspian Post", "link": "https://caspianpost.com/iran/iran-azerbaijan-russia-finalize-plan-to-increase-transit-to-15-million-tons",
             "data_fonte": "2025-10", "affidabilita": "media"},
            {"voce": "avvio lavori Rasht-Astara", "valore": 2027, "unita": "anno previsto", "anno": "2026",
             "trend": "slittato dal 1 aprile 2026 annunciato a febbraio", "fonte": "Interfax (vice AD di RZD)",
             "link": "https://interfax.com/newsroom/top-stories/119557/", "data_fonte": "2026-10-15", "affidabilita": "alta"},
        ],
    },
    {
        "id": "FR-COR-04",
        "nome": "INSTC ramo orientale (Russia - Kazakhstan - Turkmenistan - Iran)",
        "paesi": ["RU", "KZ", "TM", "IR"],
        "stato": "operativo (linea Uzen-Bereket-Gorgan aperta nel 2014)",
        "nodi": [["Astrakhan", 48.03, 46.35], ["Atyrau", 51.92, 47.1], ["Uzen/Zhanaozen", 52.85, 43.34],
                 ["Bereket", 55.0, 39.25], ["Gorgan", 54.43, 36.84], ["Teheran", 51.39, 35.69]],
        "volumi": [],
        "nota": "nessun volume annuo con fonte verificabile trovato: dato mancante",
    },
    {
        "id": "FR-COR-05",
        "nome": "Corridoio ferroviario Ucraina - Polonia/UE (Kyiv - Kovel/Yahodyn - Lublino - Varsavia; Leopoli - Przemyśl)",
        "paesi": ["UA", "PL"],
        "stato": "operativo sotto attacco: principale via di uscita di passeggeri e merci ucraini verso l'UE e di ingresso di aiuti",
        "nodi": [["Kyiv", 30.52, 50.45], ["Kovel", 24.71, 51.21], ["Yahodyn/Dorohusk", 23.82, 51.19],
                 ["Lublino", 22.57, 51.25], ["Varsavia", 21.01, 52.23]],
        "volumi": [
            {"voce": "attacchi russi alla rete ferroviaria ucraina nel 2026 (al 24 agosto)", "valore": 1534,
             "unita": "attacchi", "anno": "2026", "trend": "gia' oltre i 1.200 di tutto il 2025",
             "fonte": "ministro ucraino delle Infrastrutture, riportato da Euromaidan Press",
             "link": "https://euromaidanpress.com/2026/08/28/russia-hunts-ukraine-locomotives-odesa-port-strikes/",
             "data_fonte": "2026-08-28", "affidabilita": "media"},
            {"voce": "locomotive colpite dall'inizio del 2026", "valore": 200, "unita": "locomotive (oltre)",
             "anno": "2026 (al 4 luglio)", "trend": "oltre 500 dall'invasione del 2022",
             "fonte": "Euromaidan Press (cita Ukrzaliznytsia)",
             "link": "https://euromaidanpress.com/2026/07/04/russia-has-hit-over-200-ukrainian-locomotives-this-year-its-targeting-logistics-that-keep-country-supplied/",
             "data_fonte": "2026-07-04", "affidabilita": "media"},
        ],
    },
    {
        "id": "FR-COR-06",
        "nome": "Rete RZD (Russia): logistica civile e militare verso il fronte e verso l'Asia",
        "paesi": ["RU"],
        "stato": "operativa; carichi in calo per il quinto anno; tratti vicino al fronte e a ovest colpiti da droni e sabotaggi",
        "nodi": [],
        "volumi": [
            {"voce": "carico sulla rete RZD 2025", "valore": 1120, "unita": "milioni di tonnellate (circa)", "anno": "2025",
             "trend": "attesa 2026: -1% (quinto calo annuo consecutivo); -5,6% nel 2025 secondo l'intelligence estera ucraina",
             "fonte": "www1.ru (dati RZD)",
             "link": "https://www1.ru/en/news/2026/07/24/424886-pogruzka-na-seti-rzd-padaet-piatyi-god-podriad-minus-1-v-2026-m.html",
             "data_fonte": "2026-07-24", "affidabilita": "media"},
        ],
    },
    {
        "id": "FR-COR-07",
        "nome": "Etihad Rail (EAU) e Hafeet Rail (EAU - Oman, verso Sohar)",
        "paesi": ["AE", "OM"],
        "stato": "merci operative dal 2023; passeggeri programmati dal 30 giugno 2026 (Abu Dhabi-Fujairah) e rete dal 30 settembre 2026 (avvio effettivo non verificato); Hafeet Rail al 30% (gennaio 2026)",
        "nodi": [["Ruwais", 52.73, 24.11], ["Abu Dhabi", 54.37, 24.45], ["Dubai", 55.27, 25.2],
                 ["Fujairah", 56.33, 25.12], ["Al Ain", 55.76, 24.21], ["Sohar", 56.75, 24.36]],
        "volumi": [
            {"voce": "avanzamento Hafeet Rail", "valore": 30, "unita": "%", "anno": "2026-01",
             "trend": "in costruzione", "fonte": "Etihad Rail (riunione del consiglio)",
             "link": "https://corporate.etihadrail.ae/en/newsroom/press/etihad-rail-board-of-directors-reviews-developments-of-the-national-rail-network-and-passenger-train-project",
             "data_fonte": "2026-01", "affidabilita": "media"},
        ],
    },
    {
        "id": "FR-COR-08",
        "nome": "Ferrovia dell'Hejaz (storica, Damasco - Medina)",
        "paesi": ["SY", "JO", "SA"],
        "stato": "in gran parte dismessa dal 1918; solo tratti brevi in Giordania e Siria. Rilevanza oggi simbolica (progetti di rilancio senza numeri verificati)",
        "nodi": [["Damasco", 36.29, 33.51], ["Amman", 35.93, 31.95], ["Ma'an", 35.73, 30.19],
                 ["Tabuk", 36.57, 28.38], ["Medina", 39.61, 24.47]],
        "volumi": [],
        "nota": "nessun traffico merci rilevante: dato mancante",
    },
    {
        "id": "FR-COR-09",
        "nome": "Corridoi europei TEN-T (regolamento UE 2024/1679, 9 corridoi europei di trasporto)",
        "paesi": ["UE"],
        "stato": "quadro normativo; rete centrale da completare entro il 2030. Quattro corridoi attraversano l'Italia (Scandinavo-Mediterraneo, Baltico-Adriatico, Mediterraneo, Mare del Nord-Reno-Mediterraneo); il nuovo Mar Baltico-Mar Nero-Mar Egeo e l'estensione verso Ucraina e Moldova servono anche la mobilita' militare",
        "nodi": [],
        "volumi": [],
        "link": "https://transport.ec.europa.eu/transport-themes/infrastructure-and-investment/trans-european-transport-network-ten-t_en",
        "nota": "tracciati ufficiali non scaricati in questa versione (servono i file GIS della DG MOVE)",
    },
]


# ---------------------------------------------------------------------------
# Incidenti, sabotaggi e attacchi alla ferrovia (fatti con fonte e data).
# Coordinate: stimate dal luogo indicato dalla fonte (precisione_km).
# ---------------------------------------------------------------------------
INCIDENTI = [
    {"id": "FR-INC-01", "nome": "Esplosione sulla linea Varsavia-Lublino presso Mika: sabotaggio", "data_evento": "2025-11-16",
     "lat": 51.79, "lon": 21.79, "precisione_km": 10, "paese": "PL", "categoria": "sabotaggio",
     "attore": "secondo il governo polacco due cittadini ucraini al servizio dei servizi russi, entrati e usciti dalla Bielorussia",
     "esito": "binario distrutto; secondo danno sulla stessa linea vicino a Lublino; allerta alzata sulle linee ferroviarie",
     "fonte": "Associated Press / Notes from Poland", "link": "https://notesfrompoland.com/2025/11/17/poland-confirms-act-of-sabotage-behind-explosion-that-damaged-rail-line/",
     "data_fonte": "2025-11-17", "affidabilita": "alta"},
    {"id": "FR-INC-02", "nome": "Drone russo colpisce la locomotiva del treno Kyiv-Varsavia a circa 2 km dalla Polonia (Yahodyn)", "data_evento": "2026-09",
     "lat": 51.19, "lon": 23.82, "precisione_km": 5, "paese": "UA", "categoria": "attacco-militare",
     "attore": "Russia", "esito": "nessun passeggero ferito; giorni dopo colpita un'altra locomotiva in Volinia",
     "fonte": "Boston Globe (AP) / Kyiv Independent", "link": "https://www.bostonglobe.com/2026/09/14/world/russian-strike-train-station-near-poland-seen-warning-ukraines-allies/",
     "data_fonte": "2026-09-14", "affidabilita": "alta"},
    {"id": "FR-INC-03", "nome": "Attacco al deposito locomotive di Kovel e a vagoni a Konotop", "data_evento": "2026-01-01",
     "lat": 51.21, "lon": 24.71, "precisione_km": 5, "paese": "UA", "categoria": "attacco-militare",
     "attore": "Russia", "esito": "danni a deposito e materiale rotabile", "fonte": "Censor.net",
     "link": "https://censor.net/en/photonews/3593402/russia-attacked-ukraine-s-railway-on-the-first-day-of-2026",
     "data_fonte": "2026-01-01", "affidabilita": "media"},
    {"id": "FR-INC-04", "nome": "Droni russi su un treno passeggeri in Ucraina: 5 morti", "data_evento": "2026-01-27",
     "lat": None, "lon": None, "precisione_km": None, "paese": "UA", "categoria": "attacco-militare",
     "attore": "Russia", "esito": "5 morti secondo Euronews (localita' non riportata qui: coordinate mancanti)",
     "fonte": "Euronews", "link": "https://www.euronews.com/2026/01/28/russia-strikes-passenger-train-in-ukraine-killing-five",
     "data_fonte": "2026-01-28", "affidabilita": "media"},
    {"id": "FR-INC-05", "nome": "Droni ucraini contro treni merci e cisterne di carburante nell'oblast di Luhansk occupato", "data_evento": "2026-03/04",
     "lat": 48.57, "lon": 39.31, "precisione_km": 80, "paese": "UA", "categoria": "attacco-militare",
     "attore": "Ucraina", "esito": "almeno 10 treni merci e cisterne colpiti o danneggiati (video geolocalizzati)",
     "fonte": "Institute for the Study of War", "link": "https://x.com/TheStudyofWar/status/2059332424065044704",
     "data_fonte": "2026-05", "affidabilita": "media"},
    {"id": "FR-INC-06", "nome": "Deragliamento di un treno merci vicino a Ekaterinburg: 39 carri, 7 cisterne in fiamme", "data_evento": "2026-10-26",
     "lat": 56.84, "lon": 60.6, "precisione_km": 50, "paese": "RU", "categoria": "incidente-causa-ignota",
     "attore": "", "esito": "causa non comunicata: NON attribuito ad attacco",
     "fonte": "RBC-Ukraine", "link": "https://newsukraine.rbc.ua/news/freight-train-derails-in-russia-s-urals-fuel-1793015713.html",
     "data_fonte": "2026-10-26", "affidabilita": "media"},
    {"id": "FR-INC-07", "nome": "Incendio di cavidotti sulla linea Colonia-Düsseldorf presso Leverkusen, rivendicato da 'Kommando Angry Birds'", "data_evento": "2026 (estate; data esatta da verificare)",
     "lat": 51.03, "lon": 6.98, "precisione_km": 10, "paese": "DE", "categoria": "sabotaggio",
     "attore": "rivendicazione di estrema sinistra (autenticita' in verifica)", "esito": "linea chiusa circa 36 ore; indaga la sicurezza di Stato",
     "fonte": "Railmarket / blue News", "link": "https://www.bluewin.ch/en/news/letter-claiming-responsibility-after-fire-suspected-sabotage-on-railroad-line-li.3525182",
     "data_fonte": "2026", "affidabilita": "media"},
    {"id": "FR-INC-08", "nome": "Germania: circa 2.200 atti di sabotaggio (furti, incendi, vandalismo) contro la rete DB nel primo semestre 2026", "data_evento": "2026-01/06",
     "lat": None, "lon": None, "precisione_km": None, "paese": "DE", "categoria": "statistica",
     "attore": "vari", "esito": "+7% sul primo semestre 2025 (rapporto interno trapelato, Bild)",
     "fonte": "Bild via Ground News", "link": "https://ground.news/article/german-rail-network-hit-by-2-200-criminal-acts-this-year-bild-reports",
     "data_fonte": "2026", "affidabilita": "media"},
    {"id": "FR-INC-09", "nome": "Germania: arrestati due bielorussi che preparavano incendi vicino a ferrovia e linea elettrica (Norimberga)", "data_evento": "2026-10-07",
     "lat": 49.452, "lon": 11.077, "precisione_km": 20, "paese": "DE", "categoria": "sabotaggio",
     "attore": "per conto della Russia secondo la procura", "esito": "gia' nel livello ibrido (IB-20261107-11)",
     "fonte": "Anadolu / Reuters", "link": "https://www.aa.com.tr/en/europe/2-belarusians-arrested-in-germany-over-alleged-sabotage-for-russia/4104268",
     "data_fonte": "2026-10-28", "affidabilita": "alta"},
]


def dist_punto_segmento_km(p, a, b):
    # approssimazione equirettangolare locale
    lat0 = math.radians(p[1])
    kx, ky = 111.32 * math.cos(lat0), 110.57
    px, py = p[0] * kx, p[1] * ky
    ax, ay, bx, by = a[0] * kx, a[1] * ky, b[0] * kx, b[1] * ky
    dx, dy = bx - ax, by - ay
    n = dx * dx + dy * dy
    t = 0 if n == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / n))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def collega_ibrido(rete):
    try:
        with open(IBRIDO, encoding="utf-8") as f:
            ib = json.load(f)
    except Exception as e:  # noqa: BLE001
        errori.append(f"ibrido.json non leggibile: {e}")
        return []
    segmenti = []
    for el in rete:
        for parte in el["g"]:
            for i in range(len(parte) - 1):
                segmenti.append((parte[i], parte[i + 1]))
    parole = ("ferrov", "rail", "train", "treno", "binari", "locomot")
    out = []
    for p in ib.get("punti", []):
        lat, lon = p.get("lat"), p.get("lon")
        testo = json.dumps(p, ensure_ascii=False).lower()
        cita = any(w in testo for w in parole)
        dmin = None
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            for a, b in segmenti:
                if abs(a[1] - lat) > 0.5 and abs(b[1] - lat) > 0.5:
                    continue
                d = dist_punto_segmento_km((lon, lat), a, b)
                if dmin is None or d < dmin:
                    dmin = d
        if cita or (p.get("categoria") in CAT_VICINANZA and dmin is not None and dmin <= DIST_KM):
            out.append({"id": p.get("id"), "nome": p.get("nome"), "categoria": p.get("categoria"),
                        "data_evento": p.get("data_evento"),
                        "dist_ferrovia_km": None if dmin is None else round(dmin, 1),
                        "cita_ferrovia": cita,
                        "nota": "solo vicinanza geometrica (<= 2 km) alla rete Natural Earth semplificata: da verificare, non implica che il bersaglio fosse la ferrovia" if not cita else "il testo cita esplicitamente la ferrovia"})
    return out


def linea_schematica(nodi):
    return [[[n[1], n[2]] for n in nodi]] if len(nodi) > 1 else []


def main():
    ora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    url_ne, rete = costruisci_rete()
    if url_ne is None:
        # niente rete: se esiste un file precedente, si conservano le sue linee
        try:
            with open(USCITA, encoding="utf-8") as f:
                vecchio = json.load(f)
            rete = [e for e in vecchio.get("elementi", []) if e.get("categoria") == "ferrovia-principale"]
            errori.append("Natural Earth non raggiungibile: conservate le linee del file precedente")
        except Exception:  # noqa: BLE001
            rete = []
    corridoi = []
    for c in CORRIDOI:
        c = dict(c)
        c["categoria"] = "corridoio-strategico"
        c["tracciato"] = "schematico: nodi principali collegati in linea retta, non e' il binario reale"
        c["g"] = linea_schematica(c.get("nodi", []))
        corridoi.append(c)
    incidenti = [dict(i, classe="evento") for i in INCIDENTI]
    collegamenti = collega_ibrido(rete)

    dati = {
        "aggiornato": ora,
        "fonti": [
            {"nome": "Natural Earth 10m railroads (v5.x)", "link": url_ne or NE_URLS[0],
             "licenza": "pubblico dominio", "data_dato": "rilascio Natural Earth corrente (dato statico, ~2012-2017)"},
            {"nome": "Schede corridoi e incidenti curate dall'agente (fonti di stampa e ufficiali, una per voce)",
             "link": "report/agenti/ferrovie.md", "licenza": "fatti citati con link alla fonte", "data_dato": "2025-11 / 2026-11"},
        ],
        "nota": ("Rete: linee principali Natural Earth (category=1) nel riquadro lon -11..135, lat 12..72, tratti uniti e "
                 "semplificati; 'macroarea' e' un'etichetta indicativa per riquadri, non per confini. Natural Earth e' "
                 "generalizzata e non aggiornata: mancano linee recenti (es. Baku-Tbilisi-Kars, Etihad Rail). "
                 "Corridoi: tracciato schematico tra nodi. Incidenti: coordinate stimate (vedi precisione_km); "
                 "lat/lon nulli dove la fonte non indica il luogo."),
        "elementi": rete + corridoi + incidenti,
        "collegamenti_ibrido": collegamenti,
        "errori": errori,
    }
    testo = json.dumps(dati, ensure_ascii=False, separators=(",", ":"))
    if len(testo.encode("utf-8")) > LIMITE_BYTE:
        errori.append(f"file oltre {LIMITE_BYTE} byte: aumentare TOLL o MIN_LUNG_KM")
        testo = json.dumps(dati, ensure_ascii=False, separators=(",", ":"))
    os.makedirs(os.path.dirname(USCITA), exist_ok=True)
    with open(USCITA, "w", encoding="utf-8") as f:
        f.write(testo)
    n_parti = sum(len(e["g"]) for e in rete)
    n_punti = sum(len(p) for e in rete for p in e["g"])
    print(f"scritto {USCITA}: {len(testo.encode('utf-8'))} byte; rete {len(rete)} gruppi, {n_parti} parti, "
          f"{n_punti} vertici, {round(sum(e['km'] for e in rete))} km; corridoi {len(corridoi)}; "
          f"incidenti {len(incidenti)}; collegamenti ibrido {len(collegamenti)}; errori {len(errori)}")
    for e in errori:
        print("ERRORE:", e, file=sys.stderr)


if __name__ == "__main__":
    main()
