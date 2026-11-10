#!/usr/bin/env python3
"""SHIPPING TRANSIT TIMES agent: days and extra cost to bring goods to European ports, today vs pre-crisis.

Produces: docs/data/transit-times.json

Method (standard library only, no network needed):
  1. Builds a graph from the Benden shipping lanes in docs/data/rotte.json (vertices shared between
     lanes are junctions; dangling lane ends are snapped to the nearest vertex within 250 km).
     Each port is joined to the network through a short approach (hand-set sea waypoint + the
     nearest lane vertices). Edge weight = great-circle length in km.
  2. Dijkstra shortest path in three scenarios: "all open" (2023 baseline, via Suez/Bab el-Mandeb,
     Hormuz open), "no Red Sea" (edges passing near Suez or Bab el-Mandeb removed: Cape of Good
     Hope) and, for Gulf origins, "no Hormuz".
  3. Picks today's route from the state of the passages in docs/data/stretti-dettaglio.json
     (Hormuz "chiuso" -> Gulf origins are re-routed to their bypass port, Suez/Bab "chiuso" -> Cape)
     and from the container share on Red Sea services (CONFIG below, sourced fact).
  4. Converts nm to days at the service speeds in CONFIG (sourced), fuel at declared hypothetical
     daily consumptions, cost at today's Ship & Bunker VLSFO price (docs/data/bunker-emissioni.json),
     EU ETS at today's EUA (50% of an extra-EU voyage, 2026 phase-in 100%), war-risk premium for
     Joint War Committee listed areas crossed (polygons and premiums from docs/data/assicurazioni.json),
     freight index on the lane from docs/data/noli.json.
  5. Validates the computed distances against published port-to-port distances (VALIDATION).

Usage: python3 raccolta/rotte/tempi.py   (from the repository root). Writes only its own JSON file.
"""
import datetime as dt
import heapq
import json
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
DATA = os.path.join(RADICE, "docs", "data")
OUT = os.path.join(DATA, "transit-times.json")

R_KM = 6371.0088
KM_PER_NM = 1.852

# ---------------------------------------------------------------- ports
# lon, lat of the berth area; "via" = sea waypoints between the berth and the lane network
# (river/estuary approaches, so that the connector does not cut across land).
ORIGINS = {
    "shanghai": {"name": "Shanghai (Yangshan)", "country": "CN", "pos": [122.07, 30.62], "via": [[122.6, 30.6]], "cargo": "container", "region": "east_asia"},
    "singapore": {"name": "Singapore", "country": "SG", "pos": [103.84, 1.26], "via": [[104.0, 1.2]], "cargo": "container", "region": "se_asia"},
    "busan": {"name": "Busan", "country": "KR", "pos": [129.05, 35.08], "via": [[129.2, 34.9]], "cargo": "container", "region": "east_asia"},
    "ras_laffan": {"name": "Ras Laffan", "country": "QA", "pos": [51.6, 25.93], "via": [[51.9, 26.2]], "cargo": "lng", "region": "gulf", "inside_hormuz": True,
                   "bypass": None, "bypass_note": "No bypass: Qatar has no LNG export terminal outside the Gulf."},
    "ras_tanura": {"name": "Ras Tanura / Juaymah", "country": "SA", "pos": [50.17, 26.64], "via": [[50.6, 26.9]], "cargo": "crude", "region": "gulf", "inside_hormuz": True,
                   "bypass": "yanbu", "bypass_note": "Crude is piped west on the East-West (Petroline) pipeline, Abqaiq-Yanbu, and loaded at Yanbu."},
    "yanbu": {"name": "Yanbu", "country": "SA", "pos": [38.06, 24.08], "via": [[37.7, 24.0]], "cargo": "crude", "region": "red_sea", "saudi": True},
    "jebel_ali": {"name": "Jebel Ali", "country": "AE", "pos": [55.03, 25.01], "via": [[55.0, 25.3]], "cargo": "container", "region": "gulf", "inside_hormuz": True,
                  "bypass": "khor_fakkan", "bypass_note": "Boxes are trucked to Khor Fakkan or Fujairah on the Gulf of Oman (land bridge) and loaded there."},
    "nhava_sheva": {"name": "Mumbai / Nhava Sheva (JNPA)", "country": "IN", "pos": [72.95, 18.95], "via": [[72.6, 18.8]], "cargo": "container", "region": "south_asia"},
    "sabine_pass": {"name": "Houston / Sabine Pass", "country": "US", "pos": [-93.87, 29.73], "via": [[-93.8, 29.4]], "cargo": "lng", "region": "us_gulf",
                    "note": "Sabine Pass LNG terminal; Houston (Galveston Bay entrance) is about 70 nm further west, i.e. +0.2 days."},
    "new_york": {"name": "New York / New Jersey", "country": "US", "pos": [-74.04, 40.66], "via": [[-73.83, 40.45]], "cargo": "container", "region": "us_east"},
    "santos": {"name": "Santos", "country": "BR", "pos": [-46.3, -23.98], "via": [[-46.3, -24.2]], "cargo": "container", "region": "south_america"},
}
BYPASS_PORTS = {
    "khor_fakkan": {"name": "Khor Fakkan (land bridge from Jebel Ali)", "country": "AE", "pos": [56.36, 25.35], "via": [[56.6, 25.35]]},
}
DESTINATIONS = {
    "rotterdam": {"name": "Rotterdam", "country": "NL", "pos": [4.05, 51.97], "via": [[3.7, 52.0]], "range": "north"},
    "antwerp": {"name": "Antwerp", "country": "BE", "pos": [4.3, 51.3], "via": [[3.6, 51.42], [3.1, 51.5]], "range": "north"},
    "hamburg": {"name": "Hamburg", "country": "DE", "pos": [9.95, 53.54], "via": [[9.1, 53.88], [8.4, 53.98], [7.8, 54.05]], "range": "north"},
    "gdansk": {"name": "Gdańsk", "country": "PL", "pos": [18.67, 54.4], "via": [[18.8, 54.6]], "range": "baltic"},
    "klaipeda": {"name": "Klaipėda", "country": "LT", "pos": [21.13, 55.71], "via": [[21.0, 55.72]], "range": "baltic"},
    "esbjerg": {"name": "Esbjerg", "country": "DK", "pos": [8.44, 55.46], "via": [[8.2, 55.45]], "range": "north"},
    "genoa": {"name": "Genoa", "country": "IT", "pos": [8.9, 44.4], "via": [[8.9, 44.3]], "range": "med"},
    "trieste": {"name": "Trieste", "country": "IT", "pos": [13.76, 45.65], "via": [[13.6, 45.6]], "range": "med"},
    "piraeus": {"name": "Piraeus", "country": "GR", "pos": [23.62, 37.94], "via": [[23.55, 37.9]], "range": "med"},
}

# ---------------------------------------------------------------- passages (gates)
# A path "uses" a passage when it comes within radius_km of the gate point; blocking a passage
# removes every edge that comes within radius_km. Names in Italian match stretti-dettaglio ids.
GATES = {
    "suez": {"name": "Suez Canal", "pos": [32.45, 30.4], "radius_km": 120, "stretti_id": "suez"},
    "bab_el_mandeb": {"name": "Bab el-Mandeb", "pos": [43.35, 12.6], "radius_km": 120, "stretti_id": "bab-el-mandeb"},
    "hormuz": {"name": "Strait of Hormuz", "pos": [56.45, 26.45], "radius_km": 110, "stretti_id": "hormuz"},
    "cape": {"name": "Cape of Good Hope", "pos": [19.5, -35.5], "radius_km": 450, "stretti_id": "capo"},
    "gibraltar": {"name": "Strait of Gibraltar", "pos": [-5.6, 35.95], "radius_km": 80, "stretti_id": "gibilterra"},
    "malacca": {"name": "Strait of Malacca / Singapore Strait", "pos": [101.0, 2.6], "radius_km": 250, "stretti_id": "malacca"},
    "taiwan": {"name": "Taiwan Strait", "pos": [119.8, 24.4], "radius_km": 120, "stretti_id": "taiwan"},
    "dover": {"name": "Dover Strait", "pos": [1.45, 51.0], "radius_km": 60, "stretti_id": None},
    "danish": {"name": "Danish straits (Skagerrak-Kattegat-Great Belt/Oresund)", "pos": [11.3, 56.4], "radius_km": 160, "stretti_id": "stretti-danesi"},
    "panama": {"name": "Panama Canal", "pos": [-79.7, 9.1], "radius_km": 80, "stretti_id": "panama"},
}

# ---------------------------------------------------------------- vessels (sourced speeds, declared consumptions)
CONFIG = {
    "vessels": {
        "container": {
            "label": "container ship ~15,000 TEU",
            "speed_kn": 15.0, "speed_range_kn": [14.0, 16.0],
            "speed_source": "Alphaliner via Lloyd's List/press (mid-April 2026): global container fleet average 15.22 kn, Far East-Europe faster because of Cape routings; BIMCO: 13.8 kn in Q1 2023 (slow steaming). Range 14-16 kn as in UNCTAD RMT 2024 sensitivity (14->16 kn = +31% fuel per mile).",
            "speed_links": ["https://www.hellenicshippingnews.com/?p=1033254", "https://www.weforum.org/stories/2024/03/slow-steaming-emissions-red-sea-trade/", "https://unctad.org/system/files/official-document/rmt2024ch2_en.pdf"],
            "fuel_t_day": 150.0, "fuel_note": "HYPOTHESIS: about 150 t/day VLSFO for a 15,000 TEU ship at 15 kn (order of magnitude, cubic speed law); consistent with the 4,000 t Asia-Rotterdam last leg used in bunker-emissioni.json",
            "hull_value_musd": 150.0, "hull_note": "HYPOTHESIS: a 2026 newbuild of 15,500 TEU is priced about 222 M$ (India Seatrade News, Aug 2026, in assicurazioni.json); an in-service ship is worth less, 150 M$ used",
            "unit": "FEU", "units_per_voyage": 6375.0, "unit_note": "15,000 TEU x 85% utilisation / 2 = 6,375 FEU (HYPOTHESIS)",
        },
        "crude": {
            "label": "Suezmax crude tanker (~1 million bbl; a laden VLCC cannot transit Suez)",
            "speed_kn": 12.5, "speed_range_kn": [12.0, 13.0],
            "speed_source": "S&P Global Commodity Insights / CAS: average VLCC laden speed about 12.4 kn in week 38 and 12.1 kn in week 43 of 2025; Clarksons: tanker fleet speeds at record lows in 2025",
            "speed_links": ["https://www.spglobal.com/energy/en/news-research/latest-news/shipping/103025-asian-vlcc-rates-rise-due-to-congestion-robust-demand", "https://tradewindsnews.com/tankers/ship-speeds-at-all-time-lows-as-industry-slow-steams-towards-green-goals-clarksons-data-shows/2-1-1790206"],
            "fuel_t_day": 45.0, "fuel_note": "HYPOTHESIS: about 45 t/day VLSFO laden at 12.5 kn for a Suezmax",
            "hull_value_musd": 100.0, "hull_note": "Reuters (Insurance Journal, 25 Sep 2026): average price of older tankers above 100 M$ (assicurazioni.json)",
            "unit": "bbl", "units_per_voyage": 1000000.0, "unit_note": "1 million barrels per Suezmax cargo",
        },
        "lng": {
            "label": "LNG carrier ~174,000 m3 (two-stroke)",
            "speed_kn": 17.0, "speed_range_kn": [16.0, 18.0],
            "speed_source": "Derived from S&P Global: a Qatar-NW Europe spot voyage takes about 16 days via Suez and about 27 days via the Cape (implies 16-17 kn on our distances); modern LNG carriers are designed for 19-19.5 kn but trade slower in an oversupplied market (Vortexa, Argus 2025)",
            "speed_links": ["https://www.spglobal.com/energy/en/news-research/latest-news/natural-gas/032421-lng-spot-shipping-market-not-feeling-impact-from-suez-canal-incident", "https://www.vortexa.com/insights/lng/falling-average-speeds-and-utilisation-rates-underscore-lng-vessel-oversupply-bringing-freight-prices-to-atypical-lows"],
            "fuel_t_day": 110.0, "fuel_note": "HYPOTHESIS: about 110 t/day VLSFO-equivalent (mostly boil-off gas) at 17 kn; emissions computed as if VLSFO",
            "hull_value_musd": 200.0, "hull_note": "Howden Re (March 2026): 200-300 M$ for tankers and LNG carriers in general (assicurazioni.json); low end used",
            "unit": "MMBtu", "units_per_voyage": 3600000.0, "unit_note": "about 3.6 million MMBtu delivered per 174,000 m3 cargo (HYPOTHESIS: 21 MMBtu per m3, minus boil-off)",
        },
    },
    # Fact used to choose today's container route Asia-Europe while Suez is open but not fully back.
    "container_red_sea_share": {
        "value_pct": 63, "date": "2026-10",
        "text": "Alphaliner: 63% of Far East-Europe capacity is on services via the Red Sea; Linerlytica expects a full return by Q1 2027",
        "source": "docs/data/stretti-dettaglio.json (suez, stato_attuale)",
    },
    # Pre-crisis war-risk premium (% of hull value per transit) where a listed area is crossed.
    "base_premium_pct": {
        "mar-rosso": {"value": 0.075, "date": "2023-11-30", "text": "0.05-0.1% before the Houthi attacks (Moody's, in assicurazioni.json)"},
        "golfo-hormuz": {"value": 0.2, "date": "2026-02-27", "text": "0.15-0.25% for a Hormuz transit before the 28 Feb 2026 war (Marsh, in assicurazioni.json)"},
        "mar-rosso-saudita": {"value": 0.0, "date": "2023", "text": "Yanbu was outside the listed area until JWLA-034 moved the Red Sea limit from 18N to 25.5N"},
    },
    "ets": {"share_extra_eu": 0.5, "phase_in_2026": 1.0, "tco2e_per_t_vlsfo": 3.1631,
            "source": "Directive (EU) 2023/959; factor 3.114 tCO2 + CH4/N2O from 2026, as in bunker-emissioni.json"},
}

# Published port-to-port distances used to validate the network (nautical miles unless days).
VALIDATION = [
    {"pair": "Shanghai-Rotterdam via Suez", "from": "shanghai", "to": "rotterdam", "scenario": "base", "published_nm": 10600,
     "source": "Rodrigue, Port Economics, Management and Policy: Routing options between Shanghai, Rotterdam and New York", "link": "https://porteconomicsmanagement.org/routing-options-shanghai-rotterdam/"},
    {"pair": "Shanghai-Rotterdam via Cape of Good Hope", "from": "shanghai", "to": "rotterdam", "scenario": "cape", "published_nm": 13800,
     "source": "Rodrigue, Port Economics, Management and Policy (same page)", "link": "https://porteconomicsmanagement.org/routing-options-shanghai-rotterdam/"},
    {"pair": "Singapore-Rotterdam via Suez", "from": "singapore", "to": "rotterdam", "scenario": "base", "published_nm": 8440,
     "source": "Rodrigue, The Geography of Transport Systems, map 'Panama and Suez shortcuts' (other tables: 8,288 nm)", "link": "https://transportgeography.org/media/maps/map_panama-suez-shortcuts"},
    {"pair": "Singapore-Rotterdam via Cape of Good Hope", "from": "singapore", "to": "rotterdam", "scenario": "cape", "published_nm": 11940,
     "source": "Rodrigue, The Geography of Transport Systems (other tables: 11,755 nm)", "link": "https://transportgeography.org/media/maps/map_panama-suez-shortcuts"},
    {"pair": "Middle East Gulf-Rotterdam: extra distance Cape vs Suez", "from": "ras_tanura", "to": "rotterdam", "scenario": "cape_minus_base", "published_nm": 4900,
     "source": "Lloyd's List: diverting via the Cape adds some 4,900 nm and 14-16 days one way MEG-Rotterdam", "link": "https://www.lloydslist.com/LL1148053/More-suezmax-tankers-take-the-long-way-to-Europe-and-the-Med"},
    {"pair": "New York-Rotterdam", "from": "new_york", "to": "rotterdam", "scenario": "base", "published_nm": 3350,
     "source": "Commonly published 3,200-3,450 nm (calculator sites, low reliability); midpoint used", "link": "https://everycalculators.com/sea-route-calculator.html"},
    {"pair": "Ras Laffan-NW Europe via Suez (days)", "from": "ras_laffan", "to": "rotterdam", "scenario": "base", "published_days": 16, "cargo": "lng",
     "source": "S&P Global: a spot voyage Qatar-NW Europe takes around 16 days via Suez", "link": "https://www.spglobal.com/energy/en/news-research/latest-news/natural-gas/032421-lng-spot-shipping-market-not-feeling-impact-from-suez-canal-incident"},
    {"pair": "Ras Laffan-NW Europe via Cape (days)", "from": "ras_laffan", "to": "rotterdam", "scenario": "cape", "published_days": 27, "cargo": "lng",
     "source": "S&P Global: around 27 days around the Cape of Good Hope", "link": "https://www.spglobal.com/energy/en/news-research/latest-news/natural-gas/032421-lng-spot-shipping-market-not-feeling-impact-from-suez-canal-incident"},
]

# Fuel price hub per origin region (Ship & Bunker VLSFO, bunker-emissioni.json ids).
FUEL_HUB = {"east_asia": "hub-singapore", "se_asia": "hub-singapore", "south_asia": "hub-fujairah", "gulf": "hub-fujairah",
            "red_sea": "hub-fujairah", "us_gulf": "hub-rotterdam", "us_east": "hub-rotterdam", "south_america": "hub-rotterdam"}


# ---------------------------------------------------------------- geometry
def hav(a, b):
    lo1, la1, lo2, la2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R_KM * math.asin(min(1.0, math.sqrt(h)))


def gc_points(a, b, step_km=25.0):
    """Points along the great circle a->b (inclusive), roughly every step_km."""
    d = hav(a, b)
    n = max(1, int(d / step_km))
    lo1, la1, lo2, la2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    dd = d / R_KM
    out = []
    for i in range(n + 1):
        f = i / n
        if dd == 0:
            out.append(tuple(a))
            continue
        A = math.sin((1 - f) * dd) / math.sin(dd)
        B = math.sin(f * dd) / math.sin(dd)
        x = A * math.cos(la1) * math.cos(lo1) + B * math.cos(la2) * math.cos(lo2)
        y = A * math.cos(la1) * math.sin(lo1) + B * math.cos(la2) * math.sin(lo2)
        z = A * math.sin(la1) + B * math.sin(la2)
        out.append((math.degrees(math.atan2(y, x)), math.degrees(math.atan2(z, math.hypot(x, y)))))
    return out


def point_in_poly(p, poly):
    x, y = p
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xin:
                inside = not inside
    return inside


def key(p):
    lo, la = p
    if lo <= -180:
        lo = 180.0
    return (round(lo, 2), round(la, 2))


# ---------------------------------------------------------------- graph
def build_graph(lanes):
    adj = {}

    def add(a, b, w):
        if a == b:
            return
        adj.setdefault(a, {})
        adj.setdefault(b, {})
        if b not in adj[a] or adj[a][b] > w:
            adj[a][b] = w
            adj[b][a] = w

    for r in lanes:
        g = [key(p) for p in r["g"]]
        for i in range(len(g) - 1):
            add(g[i], g[i + 1], hav(g[i], g[i + 1]))
    nodes = list(adj)
    for n in nodes:  # snap dangling ends
        if len(adj[n]) == 1 and abs(abs(n[0]) - 180) > 0.01:
            best = min(((hav(n, m), m) for m in nodes if m != n and m not in adj[n]), default=None)
            if best and best[0] < 250:
                add(n, best[1], best[0])
    # antimeridian: join +180 and -180 copies (key() already maps -180 to 180)
    return adj


def attach(adj, pid, port, k=3, max_km=900):
    """Joins a port to the network through its approach waypoints and the k nearest lane vertices."""
    chain = [tuple(port["pos"])] + [tuple(v) for v in port.get("via", [])]
    names = [("P", pid, i) for i in range(len(chain))]
    for i, nm in enumerate(names):
        adj.setdefault(nm, {})
    for i in range(len(chain) - 1):
        w = hav(chain[i], chain[i + 1])
        adj[names[i]][names[i + 1]] = w
        adj[names[i + 1]][names[i]] = w
    last = chain[-1]
    cand = sorted((hav(last, n), n) for n in adj if not (isinstance(n[0], str)))
    for d, n in cand[:k]:
        if d <= max_km:
            adj[names[-1]][n] = d
            adj[n][names[-1]] = d
    return names[0], {nm: chain[i] for i, nm in enumerate(names)}


def coord(n, extra):
    return extra[n] if n in extra else n


def dijkstra(adj, src, dst, banned):
    dist = {src: 0.0}
    prev = {}
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst:
            break
        if d > dist.get(u, 1e18):
            continue
        for v, w in adj[u].items():
            if (u, v) in banned:
                continue
            nd = d + w
            if nd < dist.get(v, 1e18):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if dst not in dist:
        return None, None
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    return dist[dst], path[::-1]


def banned_edges(adj, extra, gate_ids):
    out = set()
    for u in adj:
        for v in adj[u]:
            a, b = coord(u, extra), coord(v, extra)
            for gid in gate_ids:
                g = GATES[gid]
                if hav(a, g["pos"]) > hav(a, b) + g["radius_km"] + 50:
                    continue
                if any(hav(p, g["pos"]) <= g["radius_km"] for p in gc_points(a, b, 20)):
                    out.add((u, v))
                    break
    return out


def path_coords(path, extra):
    return [coord(n, extra) for n in path]


def gates_on(coords):
    pts = []
    for i in range(len(coords) - 1):
        pts.extend(gc_points(coords[i], coords[i + 1], 25))
    found = []
    for gid, g in GATES.items():
        hits = [i for i, p in enumerate(pts) if hav(p, g["pos"]) <= g["radius_km"]]
        if hits:
            found.append((hits[0], gid))
    return [gid for _, gid in sorted(found)], pts


def areas_on(pts, areas):
    out = []
    for a in areas:
        for poly in a["g"]:
            if any(point_in_poly(p, poly) for p in pts[::2]):
                out.append(a["id"])
                break
    return out


def simplify(coords, tol_km=40.0):
    """Douglas-Peucker on lon/lat with km tolerance (approximate), splits at the antimeridian."""
    def dp(pts):
        if len(pts) < 3:
            return pts
        a, b = pts[0], pts[-1]
        best, idx = -1, 0
        for i in range(1, len(pts) - 1):
            p = pts[i]
            d = min(hav(p, a), hav(p, b)) if hav(a, b) < 1 else cross_track(p, a, b)
            if d > best:
                best, idx = d, i
        if best > tol_km:
            return dp(pts[: idx + 1])[:-1] + dp(pts[idx:])
        return [a, b]
    dense = []
    for i in range(len(coords) - 1):
        seg = gc_points(coords[i], coords[i + 1], 150)
        dense.extend(seg if i == 0 else seg[1:])
    parts, cur = [], [dense[0]]
    for p in dense[1:]:
        if abs(p[0] - cur[-1][0]) > 180:
            parts.append(cur)
            cur = [p]
        else:
            cur.append(p)
    parts.append(cur)
    return [[[round(x, 3), round(y, 3)] for x, y in dp(part)] for part in parts if len(part) >= 2]


def cross_track(p, a, b):
    d13 = hav(a, p) / R_KM
    t13 = bearing(a, p)
    t12 = bearing(a, b)
    return abs(math.asin(max(-1, min(1, math.sin(d13) * math.sin(t13 - t12))))) * R_KM


def bearing(a, b):
    lo1, la1, lo2, la2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    y = math.sin(lo2 - lo1) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(lo2 - lo1)
    return math.atan2(y, x)


# ---------------------------------------------------------------- inputs
def load(name, errors):
    try:
        with open(os.path.join(DATA, name), encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        errors.append(f"{name}: not readable ({e})")
        return None


def passage_state(stretti, errors):
    out = {}
    if not stretti:
        return out
    for e in stretti.get("elementi", []):
        sa = e.get("stato_attuale") or {}
        out[e["id"]] = {"level": sa.get("livello") or e.get("stato") or "", "date": sa.get("data"),
                        "facts": [{"text": f.get("testo"), "date": f.get("data"), "source": f.get("fonte"), "link": f.get("link")} for f in (sa.get("fatti") or [])[:3]]}
    return out


def is_closed(level):
    level = (level or "").lower()
    return "chiuso" in level and "riaperto" not in level


def portwatch_summary(pw):
    out = {}
    if not pw:
        return out
    for e in pw.get("elementi", []):
        if e.get("tipo") != "chokepoint":
            continue
        out[e["nome"]] = {"date": e.get("ultima_data"), "transits_7d_avg": (e.get("media7") or {}).get("n_total"),
                          "transits_7d_avg_1y_ago": (e.get("media7_anno_prima") or {}).get("n_total"),
                          "transits_7d_avg_3y_ago": (e.get("media7_tre_anni_prima") or {}).get("n_total"),
                          "var_vs_3y_pct": (e.get("var7_tre_anni_pct") or {}).get("n_total"),
                          "var_vs_1y_pct": (e.get("var7_anno_pct") or {}).get("n_total")}
    return out


def bunker_prices(bk):
    out = {}
    if not bk:
        return out
    for e in bk.get("elementi", []):
        v = (e.get("prezzi") or {}).get("VLSFO")
        if v and v.get("ultimo"):
            out[e["id"]] = {"now": v["ultimo"], "date": v.get("data"), "prewar": v.get("valore_prima_guerra"), "prewar_date": v.get("data_prima_guerra"), "hub": e["nome"]}
    return out


def premiums(ass):
    """Latest public premium (% hull per transit, midpoint) per premium area."""
    out = {}
    if not ass:
        return out
    for k, v in (ass.get("ultimo_premio") or {}).items():
        if v and v.get("min") is not None:
            out[k] = {"pct": round((v["min"] + v["max"]) / 2, 3), "min": v["min"], "max": v["max"], "date": v.get("data"),
                      "segment": v.get("segmento"), "source": v.get("fonte"), "link": v.get("link")}
    return out


def freight_for(origin_id, dest, noli):
    if not noli:
        return None
    idx = {e["id"]: e for e in noli.get("elementi", [])}
    o = ORIGINS.get(origin_id, {})
    if o.get("cargo") != "container" or o.get("region") not in ("east_asia", "se_asia"):
        return None
    med = dest["range"] == "med"
    out = []
    wci = idx.get("wci")
    if wci and origin_id == "shanghai":
        lane = "Shanghai-Genoa" if med else "Shanghai-Rotterdam"
        v = (wci.get("rotte") or {}).get(lane)
        if v:
            out.append({"index": f"Drewry WCI {lane}", "value": v, "unit": "USD/FEU", "date": wci.get("data"), "link": wci.get("link")})
    fbx = idx.get("fbx")
    if fbx:
        code = "FBX13" if med else "FBX11"
        v = (fbx.get("rotte") or {}).get(code)
        if v:
            out.append({"index": f"Freightos {code} " + ("China-Mediterranean" if med else "China-North Europe"), "value": v.get("valore"), "unit": "USD/FEU",
                        "weekly_change": v.get("var"), "date": fbx.get("data"), "link": fbx.get("link")})
    ccfi = idx.get("ccfi")
    if ccfi:
        lane = "MEDITERRANEAN" if med else "EUROPE"
        v = (ccfi.get("rotte") or {}).get(lane)
        if v:
            out.append({"index": f"CCFI {lane.title()}", "value": v.get("valore"), "unit": "index points", "weekly_change_pct": v.get("var_pct"), "date": ccfi.get("data"), "link": ccfi.get("link")})
    return out or None


# ---------------------------------------------------------------- main
def main():
    errors = []
    rotte = load("rotte.json", errors)
    if not rotte:
        print("rotte.json missing: nothing to do", file=sys.stderr)
        return 1
    stretti = load("stretti-dettaglio.json", errors)
    pw = load("portwatch.json", errors)
    noli = load("noli.json", errors)
    bk = load("bunker-emissioni.json", errors)
    ass = load("assicurazioni.json", errors)

    adj = build_graph(rotte["rotte"])
    extra = {}
    entry = {}
    for pid, p in list(ORIGINS.items()) + list(BYPASS_PORTS.items()) + list(DESTINATIONS.items()):
        n, ex = attach(adj, pid, p)
        entry[pid] = n
        extra.update(ex)

    ban_red = banned_edges(adj, extra, ["suez", "bab_el_mandeb"])
    ban_hormuz = banned_edges(adj, extra, ["hormuz"])
    ban_suez_only = banned_edges(adj, extra, ["suez"])

    state = passage_state(stretti, errors)
    pws = portwatch_summary(pw)
    prices = bunker_prices(bk)
    prem = premiums(ass)
    areas = [a for a in (ass or {}).get("elementi", []) if a.get("tipo") == "acque" and a.get("g")]
    eua = ((bk or {}).get("eua") or {}).get("asta_ultima", {}).get("prezzo_eur")
    eua_date = ((bk or {}).get("eua") or {}).get("asta_ultima", {}).get("data")
    eurusd = ((bk or {}).get("mercati") or {}).get("eurusd", {}).get("ultimo")
    if not eua or not eurusd:
        errors.append("EUA price or EUR/USD missing in bunker-emissioni.json: ETS cost not computed")

    hormuz_closed = is_closed(state.get("hormuz", {}).get("level"))
    red_closed = is_closed(state.get("bab-el-mandeb", {}).get("level")) or is_closed(state.get("suez", {}).get("level"))

    cache = {}

    def route(o, d, banned):
        k = (o, d, id(banned))
        if k not in cache:
            km, path = dijkstra(adj, entry[o], entry[d], banned)
            cache[k] = (km, path)
        return cache[k]

    def describe(km, path):
        if km is None:
            return None
        coords = path_coords(path, extra)
        gl, pts = gates_on(coords)
        return {"nm": round(km / KM_PER_NM), "gates": gl, "areas": areas_on(pts, areas), "coords": coords}

    empty = set()
    ets = CONFIG["ets"]
    routes_out = []
    for oid, o in ORIGINS.items():
        cargo = o["cargo"]
        ves = CONFIG["vessels"][cargo]
        sp = ves["speed_kn"]
        hub = prices.get(FUEL_HUB[o["region"]]) or prices.get("hub-rotterdam")
        for did, dst in DESTINATIONS.items():
            base = describe(*route(oid, did, empty))
            if base is None:
                errors.append(f"{oid}->{did}: no path on the lane network")
                continue
            cape = describe(*route(oid, did, ban_red | (empty if not o.get("inside_hormuz") else empty)))
            notes = []
            status = "normal"
            today_from = oid
            if o.get("inside_hormuz") and hormuz_closed:
                if o.get("bypass"):
                    today_from = o["bypass"]
                    status = "re-routed (Hormuz de facto closed)"
                    notes.append(o["bypass_note"])
                else:
                    status = "blocked (Hormuz de facto closed)"
                    notes.append(o["bypass_note"] + " Only sporadic, often AIS-dark transits; the route shown is the one a ship would take if it got through, at Gulf war-risk rates.")
            today_banned = ban_red if red_closed else empty
            today = describe(*route(today_from, did, today_banned)) if today_from in ORIGINS or today_from in BYPASS_PORTS else None
            if today is None:
                errors.append(f"{oid}->{did}: no path today")
                continue
            # containers Asia-Europe: Suez open but only part of the capacity is back
            share = None
            if cargo == "container" and "suez" in today["gates"] and not red_closed:
                share = CONFIG["container_red_sea_share"]
                notes.append(f"{share['value_pct']}% of Far East-Europe container capacity is back on Red Sea/Suez services ({share['date']}); the rest still sails via the Cape (alternative given in 'cape').")
            if oid == "yanbu" and o.get("saudi"):
                notes.append("Northbound to Suez: does not cross Bab el-Mandeb; Yanbu is inside the JWC listed area since JWLA-034 (Red Sea limit moved from 18N to 25.5N).")
            if o.get("note"):
                notes.append(o["note"])

            def days(nm, s=sp):
                return round(nm / (s * 24.0), 1)

            dt_today, dt_base = days(today["nm"]), days(base["nm"])
            fuel_today = dt_today * ves["fuel_t_day"]
            fuel_base = dt_base * ves["fuel_t_day"]
            extra_fuel = round(fuel_today - fuel_base)
            price_now = hub["now"] if hub else None
            price_pre = hub["prewar"] if hub else None
            fuel_usd_extra = extra_fuel * price_now if price_now else None
            price_effect = fuel_base * (price_now - price_pre) if price_now and price_pre else None
            ets_usd = None
            if eua and eurusd:
                ets_usd = extra_fuel * ets["tco2e_per_t_vlsfo"] * ets["share_extra_eu"] * ets["phase_in_2026"] * eua * eurusd
            # war risk
            def wr(desc, today_flag, from_id):
                total, items = 0.0, []
                hull = ves["hull_value_musd"] * 1e6
                ar = set(desc["areas"])
                if "golfo-oceano-indiano-mar-rosso" in ar:
                    if "hormuz" in desc["gates"] or ORIGINS.get(from_id, {}).get("inside_hormuz"):
                        pk = "golfo-hormuz"
                    elif from_id == "yanbu":
                        pk = "mar-rosso-saudita"
                    elif "bab_el_mandeb" in desc["gates"]:
                        pk = "mar-rosso"
                    else:
                        pk = None
                    if pk:
                        if today_flag and pk in prem:
                            pct = prem[pk]["pct"]
                            src = f"{prem[pk]['source']} ({prem[pk]['date']}), {prem[pk]['min']}-{prem[pk]['max']}%"
                        else:
                            b = CONFIG["base_premium_pct"][pk]
                            pct, src = b["value"], b["text"]
                        items.append({"area": pk, "pct_hull": pct, "usd": round(hull * pct / 100), "source": src})
                        total += hull * pct / 100
                        if from_id == "yanbu" and "bab_el_mandeb" in desc["gates"] and today_flag and "mar-rosso" in prem:
                            pct2 = prem["mar-rosso"]["pct"]
                            items.append({"area": "mar-rosso", "pct_hull": pct2, "usd": round(hull * pct2 / 100), "source": prem["mar-rosso"]["source"]})
                            total += hull * pct2 / 100
                for other in ar - {"golfo-oceano-indiano-mar-rosso"}:
                    items.append({"area": other, "pct_hull": None, "usd": None, "source": "listed area crossed; no public premium in assicurazioni.json"})
                return total, items
            wr_today, wr_items = wr(today, True, today_from)
            wr_base, wr_base_items = wr(base, False, oid)
            wr_diff = wr_today - wr_base
            parts = [x for x in (fuel_usd_extra, ets_usd, wr_diff) if x is not None]
            extra_cost = round(sum(parts)) if parts else None
            per_unit = None
            if extra_cost is not None:
                per_unit = round((extra_cost + (price_effect or 0)) / ves["units_per_voyage"], 2)
            route_label = " - ".join(GATES[g]["name"] for g in today["gates"]) or "direct"
            if today_from != oid:
                route_label = f"from {BYPASS_PORTS.get(today_from, ORIGINS.get(today_from, {})).get('name')}: " + route_label
            rec = {
                "from": oid, "from_name": o["name"], "to": did, "to_name": dst["name"], "cargo": cargo, "vessel": ves["label"],
                "status": status, "loads_today_at": today_from,
                "route_today": route_label, "nm_today": today["nm"], "days_today": dt_today,
                "days_today_range": [days(today["nm"], ves["speed_range_kn"][1]), days(today["nm"], ves["speed_range_kn"][0])],
                "route_base": " - ".join(GATES[g]["name"] for g in base["gates"]) or "direct",
                "nm_base": base["nm"], "days_base": dt_base,
                "extra_days": round(dt_today - dt_base, 1),
                "extra_fuel_t": extra_fuel,
                "extra_cost_usd": extra_cost,
                "cost_breakdown_usd": {
                    "extra_fuel": round(fuel_usd_extra) if fuel_usd_extra is not None else None,
                    "ets_extra": round(ets_usd) if ets_usd is not None else None,
                    "war_risk_today": round(wr_today), "war_risk_base": round(wr_base), "war_risk_extra": round(wr_diff),
                    "fuel_price_effect_whole_voyage": round(price_effect) if price_effect is not None else None,
                },
                "extra_cost_per_unit_incl_price_effect": per_unit, "unit": ves["unit"],
                "fuel_price": {"hub": hub["hub"] if hub else None, "vlsfo_usd_t": price_now, "date": hub["date"] if hub else None,
                               "prewar_usd_t": price_pre, "prewar_date": hub["prewar_date"] if hub else None},
                "chokepoints": [GATES[g]["name"] for g in today["gates"]],
                "chokepoints_base": [GATES[g]["name"] for g in base["gates"]],
                "listed_areas_today": today["areas"], "war_risk_items": wr_items,
                "cape": {"nm": cape["nm"], "days": days(cape["nm"]), "extra_days_vs_base": round(days(cape["nm"]) - dt_base, 1),
                         "chokepoints": [GATES[g]["name"] for g in cape["gates"]]} if cape else None,
                "freight": freight_for(oid, dst, noli),
                "notes": notes,
                "g": simplify(today["coords"]),
            }
            if share:
                rec["red_sea_share_pct"] = share["value_pct"]
                c = rec["cape"]
                if c:
                    w = share["value_pct"] / 100
                    rec["days_today_weighted"] = round(w * dt_today + (1 - w) * c["days"], 1)
            routes_out.append(rec)

    # validation
    val = []
    for v in VALIDATION:
        cargo = v.get("cargo", ORIGINS[v["from"]]["cargo"])
        sp = CONFIG["vessels"][cargo]["speed_kn"]
        kb, _ = route(v["from"], v["to"], empty)
        kc, _ = route(v["from"], v["to"], ban_red)
        nb = kb / KM_PER_NM if kb else None
        nc = kc / KM_PER_NM if kc else None
        calc = {"base": nb, "cape": nc, "cape_minus_base": (nc - nb) if nb and nc else None}[v["scenario"].replace("_days", "")]
        row = {k: v[k] for k in ("pair", "source", "link")}
        if "published_nm" in v:
            row.update({"published_nm": v["published_nm"], "computed_nm": round(calc), "error_pct": round(100 * (calc - v["published_nm"]) / v["published_nm"], 1)})
        else:
            dd = calc / (sp * 24)
            row.update({"published_days": v["published_days"], "computed_days": round(dd, 1), "speed_kn": sp, "error_pct": round(100 * (dd - v["published_days"]) / v["published_days"], 1)})
        val.append(row)
    nm_err = [abs(r["error_pct"]) for r in val if "published_nm" in r]

    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    out = {
        "updated": now,
        "sources": [
            {"name": "Benden, P. (2022) Global Shipping Lanes v1.3.1 (via docs/data/rotte.json)", "link": "https://github.com/newzealandpaul/Shipping-Lanes", "license": "CC BY 4.0 / CC BY-SA / CC BY-NC 4.0 (declared differently in three places); personal use with citation", "date": rotte.get("aggiornato")},
            {"name": "Passage status (docs/data/stretti-dettaglio.json)", "link": "docs/data/stretti-dettaglio.json", "date": (stretti or {}).get("aggiornato")},
            {"name": "IMF PortWatch chokepoint transits (docs/data/portwatch.json)", "link": "https://portwatch.imf.org/", "license": "IMF public data, cite IMF PortWatch", "date": (pw or {}).get("aggiornato")},
            {"name": "Ship & Bunker VLSFO prices, EEX EUA auctions (docs/data/bunker-emissioni.json)", "link": "https://shipandbunker.com/prices/", "date": (bk or {}).get("aggiornato")},
            {"name": "Joint War Committee listed areas and press war-risk quotes (docs/data/assicurazioni.json)", "link": "https://lmalloyds.com/committee/joint-war-committee/", "date": (ass or {}).get("aggiornato")},
            {"name": "Drewry WCI, Freightos FBX, SSE CCFI (docs/data/noli.json)", "link": "docs/data/noli.json", "date": (noli or {}).get("aggiornato")},
        ] + [{"name": "Speed: " + c["label"], "text": c["speed_source"], "links": c["speed_links"]} for c in CONFIG["vessels"].values()],
        "method": {
            "graph": f"{sum(1 for n in adj if not isinstance(n[0], str))} lane vertices from {len(rotte['rotte'])} Benden lanes; shared vertices are junctions, dangling ends snapped to the nearest vertex within 250 km; ports attached via approach waypoints to the 3 nearest vertices; Dijkstra on great-circle edge lengths.",
            "scenarios": "base = all passages open (2023, via Suez and Bab el-Mandeb, Hormuz open); cape = edges within 120 km of Suez or Bab el-Mandeb removed; today = chosen from stretti-dettaglio.json levels (Hormuz 'chiuso' -> Gulf origins load at their bypass port or are flagged blocked; Suez/Bab 'chiuso' -> Cape).",
            "days": "nm / (speed_kn x 24), sea time only: no canal waiting, port time or bunkering stops. days_today_range = at the high and low end of the speed range.",
            "fuel": "days x hypothetical daily consumption per vessel type (see vessels); extra_fuel_t = fuel today - fuel base at the same speed. Cost at today's Ship & Bunker VLSFO at the bunkering hub of the origin region.",
            "extra_cost_usd": "extra fuel at today's price + EU ETS on the extra emissions (3.1631 tCO2e/t x 50% extra-EU voyage x 100% 2026 phase-in x today's EUA x EUR/USD) + (war-risk premium today - pre-crisis premium) x hull value. Not included: Suez Canal tolls saved on the Cape route (~0.5-1 M$ per transit), charter hire of the extra days, cargo inventory cost. fuel_price_effect_whole_voyage = base-route fuel x (today's price - 27 Feb 2026 price), shown separately.",
            "war_risk": "JWC listed area polygons (assicurazioni.json) tested on the route; premium = midpoint of the latest public quote for that area, % of hull per transit. Pre-crisis: Red Sea 0.075% (Nov 2023), Gulf 0.2% (Feb 2026), Yanbu 0% (outside the area until JWLA-034).",
            "vessels": CONFIG["vessels"],
            "container_red_sea_share": CONFIG["container_red_sea_share"],
            "speed_assumption": "same speed today and in the base case, to isolate the distance effect; on the Cape many container lines sail faster to keep weekly schedules, which raises fuel per mile",
        },
        "passages_today": {k: {"level": v["level"], "date": v["date"], "facts": v["facts"]} for k, v in state.items() if k in ("hormuz", "bab-el-mandeb", "suez", "capo", "gibilterra", "stretti-danesi")},
        "portwatch": {k: v for k, v in pws.items() if k in ("Stretto di Hormuz", "Bab el-Mandeb", "Canale di Suez", "Capo di Buona Speranza", "Stretto di Gibilterra", "Stretti danesi")},
        "prices_used": {"vlsfo": prices, "eua_eur": eua, "eua_date": eua_date, "eurusd": eurusd, "war_risk_latest": prem},
        "origins": {k: {"name": v["name"], "country": v["country"], "lon": v["pos"][0], "lat": v["pos"][1], "cargo": v["cargo"]} for k, v in ORIGINS.items()},
        "bypass_ports": {k: {"name": v["name"], "country": v["country"], "lon": v["pos"][0], "lat": v["pos"][1]} for k, v in BYPASS_PORTS.items()},
        "destinations": {k: {"name": v["name"], "country": v["country"], "lon": v["pos"][0], "lat": v["pos"][1]} for k, v in DESTINATIONS.items()},
        "validation": {"rows": val, "mean_abs_error_nm_pct": round(sum(nm_err) / len(nm_err), 1) if nm_err else None, "max_abs_error_nm_pct": max(nm_err) if nm_err else None},
        "routes": routes_out,
        "errors": errors,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {OUT}: {len(routes_out)} routes, {os.path.getsize(OUT)//1024} KB, validation mean |error| {out['validation']['mean_abs_error_nm_pct']}%")
    for r in val:
        print("  ", r["pair"], r.get("published_nm") or r.get("published_days"), "->", r.get("computed_nm") or r.get("computed_days"), f"{r['error_pct']}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
