#!/usr/bin/env python3
"""Prova di fattibilita': livello dei serbatoi a Cushing (OK) da Sentinel-2 a 10 m.

Studio dimostrativo, NON fa parte della raccolta giornaliera (usa librerie esterne).
    pip install numpy scipy rasterio pystac-client pillow pandas xlrd matplotlib
    python3 report/agenti/serbatoi/prova.py

Cosa fa:
 1. cerca su Element84 Earth Search (STAC, nessuna chiave) le scene Sentinel-2 L2A
    (collezione sentinel-2-c1-l2a, tile MGRS 14SPE) con nuvole < 5 % tra DATA_DA e DATA_A;
 2. legge solo un ritaglio di 4 x 4 km attorno al centro dei parchi serbatoi
    (lettura a finestra dai COG su AWS, pochi MB per scena), scarta le scene con
    nuvole/ombre di nuvole nel ritaglio (banda SCL);
 3. individua i serbatoi una volta sola, sulla mediana di tutte le date: oggetti
    tondi e chiari di 30-150 pixel (= 60-140 m di diametro);
 4. per ogni serbatoio e data misura il contrasto Nord-Sud dentro il tetto:
    con il sole a sud (azimut ~165 gradi), la parete sud proietta l'ombra sulla
    meta' sud del tetto galleggiante; piu' il tetto e' basso (serbatoio vuoto),
    piu' l'ombra e' larga. Indice = (N - S) / (N + S), poi moltiplicato per
    tan(elevazione solare) per togliere l'effetto dell'angolo del sole
    (lunghezza ombra = altezza libera / tan(elevazione));
 5. scarica la serie EIA settimanale W_EPC0_SAX_YCUOK_MBBL (scorte di greggio a
    Cushing, migliaia di barili), la interpola alla data di ogni scena e calcola
    le correlazioni (Pearson e Spearman), anche dopo aver tolto la dipendenza
    lineare dall'elevazione solare;
 6. salva ritagli PNG, un grafico e un CSV in questa cartella.
"""
import csv
import io
import math
import os
import sys
import urllib.request

import numpy as np
import pandas as pd
import rasterio
from PIL import Image, ImageDraw
from pystac_client import Client
from rasterio.warp import transform
from rasterio.windows import from_bounds
from scipy import ndimage, stats

OUT = os.path.dirname(os.path.abspath(__file__))
STAC = "https://earth-search.aws.element84.com/v1"
COLL = "sentinel-2-c1-l2a"
TILE = "MGRS-14SPE"
DATA_DA, DATA_A = "2025-06-01", "2026-11-09"
CENTRO = (-96.7497, 35.9423)    # lon, lat: centro del ritaglio (parchi a sud di Cushing)
MEZZO_LATO = 2000               # metri -> ritaglio 4 x 4 km
EIA_XLS = "https://www.eia.gov/dnav/pet/hist_xls/W_EPC0_SAX_YCUOK_MBBLw.xls"
SCL_CATTIVI = {0, 1, 3, 8, 9, 10, 11}  # nodata, saturato, ombra nuvola, nuvole, cirri, neve


def leggi(href, bounds, scala=None, offset=None, shape=None):
    with rasterio.open(href) as src:
        w = from_bounds(*bounds, src.transform)
        kw = {"out_shape": shape, "resampling": rasterio.enums.Resampling.nearest} if shape else {}
        a = src.read(1, window=w, boundless=True, fill_value=0, **kw).astype("float32")
    if scala is not None:
        a = np.where(a == 0, np.nan, a * scala + offset)
    return a


def scene():
    cl = Client.open(STAC)
    s = cl.search(collections=[COLL], intersects={"type": "Point", "coordinates": list(CENTRO)},
                  datetime=f"{DATA_DA}/{DATA_A}", query={"eo:cloud_cover": {"lt": 5}}, max_items=500)
    its = [i for i in s.items() if i.properties.get("grid:code") == TILE]
    # una sola scena per giorno
    visti, out = set(), []
    for i in sorted(its, key=lambda i: i.datetime):
        d = i.datetime.date()
        if d not in visti:
            visti.add(d)
            out.append(i)
    return out


def bande(item, bounds):
    r = {}
    for k in ("blue", "green", "red", "nir"):
        a = item.assets[k]
        rb = a.extra_fields["raster:bands"][0]
        r[k] = leggi(a.href, bounds, rb.get("scale", 1e-4), rb.get("offset", 0.0))
    shp = r["red"].shape
    r["scl"] = leggi(item.assets["scl"].href, bounds, shape=shp)
    return r


def trova_serbatoi(lumin):
    """Serbatoi = dischi chiari sulla mediana multi-data.

    I serbatoi a Cushing sono spesso a contatto fra loro, quindi una semplice
    etichettatura li fonde: si usa la trasformata di distanza della maschera
    chiara e se ne prendono i massimi locali (centro del disco, raggio = distanza).
    """
    soglia = np.nanpercentile(lumin, 90)
    m = ndimage.binary_fill_holes(lumin > soglia)
    dist = ndimage.distance_transform_edt(m)
    picchi = (dist == ndimage.maximum_filter(dist, size=7)) & (dist >= 3.0) & (dist <= 7.5)
    tanks = []
    for cy, cx in zip(*np.nonzero(picchi)):
        r = float(dist[cy, cx])
        # scarta doppioni troppo vicini (plateau della distanza)
        if any(math.hypot(cy - t["cy"], cx - t["cx"]) < 0.8 * (r + t["r"]) for t in tanks):
            continue
        # il disco deve essere quasi tutto chiaro (forma tonda, non un tetto rettangolare)
        yy, xx = np.ogrid[-int(r):int(r) + 1, -int(r):int(r) + 1]
        disco = (yy ** 2 + xx ** 2) <= r ** 2
        y0, x0 = cy - int(r), cx - int(r)
        sub = m[max(0, y0):y0 + disco.shape[0], max(0, x0):x0 + disco.shape[1]]
        if sub.shape != disco.shape or sub[disco].mean() < 0.95:
            continue
        tanks.append({"cy": float(cy), "cx": float(cx), "r": r + 0.5, "area": int(disco.sum())})
    return tanks


def indice_ns(img, t, H, W):
    """Contrasto Nord-Sud dentro il disco interno (raggio ridotto di 1 px)."""
    yy, xx = np.mgrid[0:H, 0:W]
    rin = max(1.5, t["r"] - 1.0)
    d = np.hypot(yy - t["cy"], xx - t["cx"])
    dentro = d <= rin
    nord = dentro & (yy < t["cy"] - 0.5)
    sud = dentro & (yy > t["cy"] + 0.5)
    n, s = np.nanmean(img[nord]), np.nanmean(img[sud])
    return (n - s) / (n + s), np.nanmean(img[dentro])


def serie_eia():
    req = urllib.request.Request(EIA_XLS, headers={"User-Agent": "Mozilla/5.0 (studio OSINT)"})
    raw = urllib.request.urlopen(req, timeout=60).read()
    df = pd.read_excel(io.BytesIO(raw), sheet_name="Data 1", skiprows=2)
    df.columns = ["data", "kbbl"]
    df["data"] = pd.to_datetime(df["data"])
    return df.dropna()


def png_rgb(r, path, scala=3, tanks=None, box=None):
    rgb = np.dstack([r["red"], r["green"], r["blue"]])
    rgb = np.clip(rgb / 0.30, 0, 1) ** (1 / 1.3)
    if box:
        y0, y1, x0, x1 = box
        rgb = rgb[y0:y1, x0:x1]
    im = Image.fromarray((np.nan_to_num(rgb) * 255).astype("uint8"))
    im = im.resize((im.width * scala, im.height * scala), Image.NEAREST)
    if tanks:
        dr = ImageDraw.Draw(im)
        for t in tanks:
            cx, cy, rr = (t["cx"] + .5) * scala, (t["cy"] + .5) * scala, t["r"] * scala
            dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(255, 60, 60))
    im.save(path, optimize=True)
    return os.path.getsize(path)


def main():
    items = scene()
    print(f"scene trovate (tile {TILE}, nuvole<5%): {len(items)}")
    cl = Client.open(STAC)
    tmp = cl.get_collection(COLL).get_item(items[0].id)
    with rasterio.open(tmp.assets["red"].href) as src:
        xs, ys = transform("EPSG:4326", src.crs, [CENTRO[0]], [CENTRO[1]])
    x, y = xs[0], ys[0]
    bounds = (x - MEZZO_LATO, y - MEZZO_LATO, x + MEZZO_LATO, y + MEZZO_LATO)

    dati = []
    for it in items:
        try:
            r = bande(it, bounds)
        except Exception as e:  # rete o asset mancante
            print("  salto", it.id, e)
            continue
        cattivi = np.isin(r["scl"], list(SCL_CATTIVI)).mean()
        if cattivi > 0.01:
            print(f"  {it.datetime.date()} scartata: {cattivi:.1%} pixel nuvola/ombra nel ritaglio")
            continue
        dati.append((it, r))
        print(f"  {it.datetime.date()} ok  elev. sole {it.properties['view:sun_elevation']:.1f}")

    lum = np.nanmedian(np.stack([(r["red"] + r["green"] + r["blue"]) / 3 for _, r in dati]), axis=0)
    H, W = lum.shape
    tanks = trova_serbatoi(lum)
    print(f"serbatoi individuati: {len(tanks)} (diametro mediano "
          f"{np.median([2 * t['r'] for t in tanks]) * 10:.0f} m)")

    eia = serie_eia()
    t_eia = eia["data"].to_numpy().astype("datetime64[D]").astype("int64")
    righe = []
    for it, r in dati:
        img = r["red"] + r["green"] + r["blue"]
        ns, lm = zip(*[indice_ns(img, t, H, W) for t in tanks])
        el = it.properties["view:sun_elevation"]
        d = pd.Timestamp(it.datetime.date())
        giorno = np.datetime64(d.date(), "D").astype("int64")
        stock = float(np.interp(giorno, t_eia, eia["kbbl"].to_numpy().astype(float)))
        righe.append({"data": d.date().isoformat(), "elev_sole": round(el, 2),
                      "ns_mediano": float(np.nanmedian(ns)),
                      "ns_x_tan": float(np.nanmedian(ns) * math.tan(math.radians(el))),
                      "lum_media": float(np.nanmedian(lm)), "eia_kbbl": round(stock)})

    with open(os.path.join(OUT, "risultati.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(righe[0]))
        w.writeheader()
        w.writerows(righe)

    df = pd.DataFrame(righe)
    print("\ncorrelazioni con le scorte EIA (n=%d):" % len(df))
    res = {}
    for col in ("ns_mediano", "ns_x_tan", "lum_media", "elev_sole"):
        p = stats.pearsonr(df[col], df["eia_kbbl"])
        s = stats.spearmanr(df[col], df["eia_kbbl"])
        res[col] = (p.statistic, p.pvalue, s.statistic)
        print(f"  {col:11s} Pearson r={p.statistic:+.2f} (p={p.pvalue:.3f})  Spearman={s.statistic:+.2f}")
    # residuo dopo aver tolto l'effetto lineare dell'elevazione solare
    b = np.polyfit(df["elev_sole"], df["ns_mediano"], 1)
    resid = df["ns_mediano"] - np.polyval(b, df["elev_sole"])
    p = stats.pearsonr(resid, df["eia_kbbl"])
    print(f"  ns_mediano al netto dell'elevazione solare: r={p.statistic:+.2f} (p={p.pvalue:.3f})")
    # inverno soltanto (sole basso: ombra piu' lunga, piu' misurabile)
    inv = df[df["elev_sole"] < 45]
    if len(inv) >= 4:
        p = stats.pearsonr(inv["ns_x_tan"], inv["eia_kbbl"])
        print(f"  solo scene con sole < 45 gradi (n={len(inv)}): r={p.statistic:+.2f} (p={p.pvalue:.3f})")

    # ---- immagini ----
    per_data = {it.datetime.date().isoformat(): r for it, r in dati}
    # zoom 1,2 x 1,2 km su un gruppo di serbatoi grandi (zona centro-est)
    zoom = (int(H * .38), int(H * .38) + 120, int(W * .50), int(W * .50) + 120)
    scelte = [df.loc[df["elev_sole"].idxmin(), "data"], df.loc[df["elev_sole"].idxmax(), "data"]]
    scelte += [df.loc[df["eia_kbbl"].idxmin(), "data"], df.loc[df["eia_kbbl"].idxmax(), "data"]]
    print()
    print("ritaglio_4km_maschera.png", png_rgb(per_data[df["data"].iloc[-1]],
          os.path.join(OUT, "ritaglio_4km_maschera.png"), scala=1, tanks=tanks), "byte")
    for d in dict.fromkeys(scelte):
        fn = f"zoom_{d}.png"
        print(fn, png_rgb(per_data[d], os.path.join(OUT, fn), scala=4, box=zoom), "byte")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4), dpi=90)
    e = eia[eia["data"] >= DATA_DA]
    ax[0].plot(e["data"], e["kbbl"] / 1000, color="#444", lw=1.5, label="EIA scorte Cushing (Mbbl)")
    ax[0].set_ylabel("milioni di barili")
    a2 = ax[0].twinx()
    a2.plot(pd.to_datetime(df["data"]), df["ns_x_tan"], "o-", color="#c0392b", ms=4, lw=.8,
            label="indice ombra x tan(elev)")
    a2.set_ylabel("indice ombra (piu' alto = piu' vuoto)", color="#c0392b")
    ax[0].set_title("Serie nel tempo")
    ax[0].tick_params(axis="x", rotation=30)
    sc = ax[1].scatter(df["ns_x_tan"], df["eia_kbbl"] / 1000, c=df["elev_sole"], cmap="viridis")
    fig.colorbar(sc, ax=ax[1], label="elevazione sole (gradi)")
    ax[1].set_xlabel("indice ombra x tan(elev)")
    ax[1].set_ylabel("EIA Cushing (Mbbl)")
    ax[1].set_title(f"Dispersione (Pearson r={res['ns_x_tan'][0]:+.2f}, n={len(df)})")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "confronto_eia.png"))
    print("confronto_eia.png", os.path.getsize(os.path.join(OUT, "confronto_eia.png")), "byte")


if __name__ == "__main__":
    sys.exit(main())
