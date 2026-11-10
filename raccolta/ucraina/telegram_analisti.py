#!/usr/bin/env python3
"""Attacchi segnalati dagli analisti OSINT Clément Molin e AMK Mapping (canali Telegram pubblici).

Solo libreria standard di Python 3.

Passi (tutti di default, oppure uno alla volta):
  python3 raccolta/ucraina/telegram_analisti.py scarica     # cronologia pubblica t.me/s/<canale> (?before=)
  python3 raccolta/ucraina/telegram_analisti.py gazetteer   # costruisce gazetteer.json (GeoNames, CC BY 4.0)
  python3 raccolta/ucraina/telegram_analisti.py estrai      # regole -> attacchi, incroci, FIRMS, scrive il JSON
  python3 raccolta/ucraina/telegram_analisti.py campione    # 40 casi a caso per il controllo manuale

Cache locale (esclusa da git): raccolta/ucraina/cache_telegram/
  <canale>.json      tutti i post letti {id: post}; "completo" = arrivati al primo post
  firms/...          archivi FIRMS scaricati
Variabili d'ambiente: FIRMS_MAP_KEY (facoltativa: API area di NASA FIRMS),
  TG_MAX_PAGINE (limite pagine per canale a ogni esecuzione, default nessuno),
  TG_PAUSA (secondi tra pagine, default 1.5).

Diritti: il JSON contiene fatti (data, luogo, bersaglio, mezzi) con citazione e link
al post; del testo si tiene solo un estratto di massimo 160 caratteri.
"""
import csv
import datetime as dt
import gzip
import html
import io
import json
import math
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
import zipfile
from html.parser import HTMLParser

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
CACHE = os.path.join(QUI, "cache_telegram")
GAZ = os.path.join(QUI, "gazetteer.json")
DATI = os.path.join(RADICE, "docs", "data")
USCITA = os.path.join(DATI, "attacchi-analisti.json")
CANALI = [
    {"canale": "clement_molin", "autore": "Clément Molin", "lingua": "fr/en"},
    {"canale": "AMK_Mapping", "autore": "AMK Mapping", "lingua": "en"},
]
UA = "Mozilla/5.0 (X11; Linux x86_64) monitor-geoeconomico/1.0 (osservatorio personale)"
ADESSO = dt.datetime.now(dt.timezone.utc)
ERRORI = []


def avviso(msg):
    print("AVVISO:", msg, file=sys.stderr)
    ERRORI.append(msg)


def scarica_url(url, timeout=60, tentativi=4, binario=False):
    ultimo = None
    for k in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                dati = r.read()
            return dati if binario else dati.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            ultimo = e
            if e.code in (404, 403, 401):
                break
            time.sleep(5 * (k + 1) if e.code == 429 else 2 * (k + 1))
        except Exception as e:  # rete
            ultimo = e
            time.sleep(2 * (k + 1))
    raise RuntimeError("download fallito: %s (%s)" % (url, ultimo))


# ---------------------------------------------------------------- 1. Telegram

class PaginaTelegram(HTMLParser):
    """Legge una pagina t.me/s/<canale>: un post per div con data-post."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.posts = []
        self.cur = None
        self.prof = 0          # profondità dei div dentro il post corrente
        self.testo_prof = None  # profondità del div del testo
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if tag == "div" and a.get("data-post") and "tgme_widget_message " in cls + " ":
            canale, _, pid = a["data-post"].partition("/")
            self.cur = {"canale": canale, "id": int(pid), "data": None, "testo": "",
                        "immagini": False, "video": False}
            self.prof = 1
            return
        if self.cur is None:
            return
        if tag == "div":
            self.prof += 1
            if "js-message_text" in cls and self.testo_prof is None and not self.cur["testo"]:
                self.testo_prof = self.prof
                self.buf = []
        if "tgme_widget_message_photo" in cls:
            self.cur["immagini"] = True
        if "tgme_widget_message_video" in cls or "message_roundvideo" in cls or tag == "video":
            self.cur["video"] = True
        if tag == "time" and a.get("datetime") and self.cur["data"] is None:
            self.cur["data"] = a["datetime"]
        if self.testo_prof is not None and tag == "br":
            self.buf.append("\n")

    def handle_endtag(self, tag):
        if self.cur is None or tag != "div":
            return
        if self.testo_prof is not None and self.prof == self.testo_prof:
            self.cur["testo"] = "".join(self.buf).strip()
            self.testo_prof = None
        self.prof -= 1
        if self.prof == 0:
            self.posts.append(self.cur)
            self.cur = None

    def handle_data(self, d):
        if self.testo_prof is not None:
            self.buf.append(d)


def leggi_pagina(canale, before=None):
    url = "https://t.me/s/%s" % canale + ("?before=%d" % before if before else "")
    p = PaginaTelegram()
    p.feed(scarica_url(url, timeout=40))
    out = []
    for x in p.posts:
        if x["canale"].lower() != canale.lower() or not x["data"]:
            continue
        d = dt.datetime.fromisoformat(x["data"]).astimezone(dt.timezone.utc)
        x["data"] = d.strftime("%Y-%m-%dT%H:%M:%SZ")
        x["canale"] = canale
        x["link"] = "https://t.me/%s/%d" % (canale, x["id"])
        out.append(x)
    return out


def carica_cache(canale):
    f = os.path.join(CACHE, canale + ".json")
    if os.path.exists(f):
        with open(f, encoding="utf-8") as h:
            d = json.load(h)
        d["posts"] = {int(k): v for k, v in d["posts"].items()}
        return d
    return {"canale": canale, "completo": False, "posts": {}}


def salva_cache(st):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, st["canale"] + ".json")
    tmp = f + ".tmp"
    with open(tmp, "w", encoding="utf-8") as h:
        json.dump({"canale": st["canale"], "completo": st["completo"],
                   "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
                   "posts": {str(k): v for k, v in sorted(st["posts"].items())}},
                  h, ensure_ascii=False)
    os.replace(tmp, f)


def scarica_canale(canale):
    pausa = float(os.environ.get("TG_PAUSA", "1.5"))
    max_pag = int(os.environ.get("TG_MAX_PAGINE", "0") or 0)
    st = carica_cache(canale)
    noti = set(st["posts"])
    pagine, nuovi = 0, 0
    # a) dalla testa all'indietro fino ai post già in cache
    before = None
    fasi = ["testa"] if st["completo"] or not noti else ["testa", "coda"]
    for fase in fasi:
        if fase == "coda":
            before = min(st["posts"])  # riprende dove si era fermato
        while True:
            if max_pag and pagine >= max_pag:
                salva_cache(st)
                print("  %s: limite di %d pagine raggiunto" % (canale, max_pag))
                return st
            try:
                posts = leggi_pagina(canale, before)
            except Exception as e:
                avviso("%s: pagina before=%s non letta (%s)" % (canale, before, e))
                break
            pagine += 1
            ids = [p["id"] for p in posts if before is None or p["id"] < before]
            gia = any(i in noti for i in ids)
            for p in posts:
                if p["id"] not in st["posts"]:
                    nuovi += 1
                st["posts"][p["id"]] = p
            if pagine % 25 == 0:
                salva_cache(st)
                print("  %s: %d pagine, %d post, arrivato a id %s (%s)" % (
                    canale, pagine, len(st["posts"]), min(ids) if ids else "-",
                    st["posts"][min(ids)]["data"][:10] if ids else "-"), flush=True)
            if not ids:
                if fase == "coda" or not noti:
                    st["completo"] = True
                break
            if fase == "testa" and gia and noti:
                break
            before = min(ids)
            if before <= 1:
                st["completo"] = True
                break
            time.sleep(pausa + random.random() * 0.5)
        if fase == "testa" and not noti:
            break
    salva_cache(st)
    print("  %s: %d pagine lette, %d post nuovi, %d in cache, completo=%s" % (
        canale, pagine, nuovi, len(st["posts"]), st["completo"]))
    return st


# ---------------------------------------------------------------- 2. gazetteer

GEONAMES = "https://download.geonames.org/export/dump/"


# piccoli centri russi sede di impianti spesso colpiti (porti, raffinerie, stazioni di pompaggio)
RU_PICCOLI = {"Ust'-Luga", "Andreapol'", "Taman'", "Vysotsk", "Novoshakhtinsk", "Nikolo-Berezovka",
              "Zelenyy Gorod", "Kavkaz", "Peresyp'", "Chaltyr'", "Tinguta", "Krasnyy Bor"}


def costruisci_gazetteer():
    """GeoNames (CC BY 4.0): città UA (>=1.000 abitanti dal file UA.zip) e RU (>=15.000),
    oblast (ADM1) con le loro coordinate, più le città di docs/data/labels.json."""
    os.makedirs(os.path.join(CACHE, "geonames"), exist_ok=True)
    voci = []

    def zipfile_cache(nome):
        f = os.path.join(CACHE, "geonames", nome)
        if not os.path.exists(f):
            print("  scarico", GEONAMES + nome)
            with open(f, "wb") as h:
                h.write(scarica_url(GEONAMES + nome, timeout=300, binario=True))
        return zipfile.ZipFile(f)

    # nomi delle oblast (admin1) per paese
    adm1 = {}
    for riga in scarica_url(GEONAMES + "admin1CodesASCII.txt", timeout=120).splitlines():
        c = riga.split("\t")
        if len(c) >= 3 and c[0][:2] in ("UA", "RU"):
            adm1[c[0]] = c[2]
    soglia = {"UA": 1000, "RU": 15000}
    for paese in ("UA", "RU"):
        z = zipfile_cache(paese + ".zip")
        with z.open(paese + ".txt") as h:
            for riga in io.TextIOWrapper(h, encoding="utf-8"):
                c = riga.rstrip("\n").split("\t")
                if len(c) < 15:
                    continue
                fclass, fcode = c[6], c[7]
                pop = int(c[14] or 0)
                alt = [a for a in c[3].split(",") if a and re.fullmatch(r"[A-Za-zÀ-ÿ' \-]+", a)]
                if fcode == "ADM1":
                    voci.append({"n": c[2], "alt": sorted(set(alt))[:30], "lat": round(float(c[4]), 4),
                                 "lon": round(float(c[5]), 4), "paese": paese, "tipo": "oblast",
                                 "oblast": adm1.get(paese + "." + c[10], c[2]), "pop": pop,
                                 "geonameid": int(c[0])})
                elif fclass == "P" and fcode not in ("PPLH", "PPLQ", "PPLW") and (
                        pop >= soglia[paese] or (paese == "RU" and pop >= 3000 and float(c[5]) < 61)
                        or (paese == "RU" and c[2] in RU_PICCOLI)):
                    voci.append({"n": c[2], "alt": sorted(set(alt))[:30], "lat": round(float(c[4]), 4),
                                 "lon": round(float(c[5]), 4), "paese": paese, "tipo": "citta",
                                 "oblast": adm1.get(paese + "." + c[10], ""), "pop": pop,
                                 "geonameid": int(c[0])})
    # città della mappa (labels.json) nella zona del conflitto
    try:
        with open(os.path.join(DATI, "labels.json"), encoding="utf-8") as h:
            lab = json.load(h)
        for c in lab.get("cities", []):
            if 22 <= c["x"] <= 60 and 43 <= c["y"] <= 60:
                voci.append({"n": c["n"], "alt": [], "lat": c["y"], "lon": c["x"], "paese": "",
                             "tipo": "citta", "oblast": "", "pop": c.get("p", 0) * 1000,
                             "fonte": "labels.json"})
    except Exception as e:
        avviso("labels.json non letto: %s" % e)
    with open(GAZ, "w", encoding="utf-8") as h:
        json.dump({"fonte": "GeoNames (https://www.geonames.org/, CC BY 4.0): UA.zip, RU.zip, "
                   "admin1CodesASCII.txt; più docs/data/labels.json",
                   "creato": ADESSO.strftime("%Y-%m-%d"),
                   "nota": "UA: luoghi abitati >=1.000 abitanti; RU: >=15.000 (>=3.000 a ovest degli Urali, lon<61); ADM1 = oblast/regioni "
                   "(coordinate del punto GeoNames della regione)",
                   "voci": voci}, h, ensure_ascii=False, separators=(",", ":"))
    print("  gazetteer: %d voci" % len(voci))


def norm_obl(n):
    n = n.lower().replace("'", "").replace("’", "")
    n = re.sub(r"\b(oblast|oblasti|krai|kray|republic|respublika|city|autonomous|okrug|region|province)\b", "", n)
    n = re.sub(r"\(.*?\)", "", n)
    return re.sub(r"\s+", " ", n).strip(" -")


# Come gli analisti scrivono le regioni (base del nome, senza "Oblast"/"Krai") -> chiave norm_obl GeoNames
OBLAST_ALIAS = {
    "kiev": "kyiv", "odessa": "odesa", "zaporizhia": "zaporizhzhia", "zaporozhye": "zaporizhzhia",
    "zaporijia": "zaporizhzhia", "dnipro": "dnipropetrovsk", "dnepropetrovsk": "dnipropetrovsk",
    "vinnytsya": "vinnytsia", "vinnitsa": "vinnytsia", "kirovograd": "kirovohrad", "mykolayiv": "mykolaiv",
    "nikolaev": "mykolaiv", "volhynia": "volyn", "volyn": "volyn", "transcarpathia": "zakarpattia",
    "zakarpattia": "zakarpattia", "khmelnytskyi": "khmelnytskyi", "khmelnytsky": "khmelnytskyi",
    "lugansk": "luhansk", "crimée": "crimea", "crimea": "crimea", "kharkov": "kharkiv",
    "chernigov": "chernihiv", "cherkassy": "cherkasy",
    "orel": "oryol", "leningrad": "leningradskaya", "saint petersburg": "st. petersburg",
    "udmurtia": "udmurtiya", "chuvashia": "chuvash", "mordovia": "mordoviya", "adygea": "adygeya",
    "kalmykia": "kalmykiya", "tatarstan": "tatarstan", "bashkortostan": "bashkortostan",
    "bashkiria": "bashkortostan", "ingushetia": "ingushetiya", "kabardino-balkaria": "kabardino-balkariya",
    "karachay-cherkessia": "karachayevo-cherkesiya", "north ossetia": "north ossetia-alania",
    "krasnodar": "krasnodar", "kuban": "krasnodar", "stavropol": "stavropol", "perm": "perm",
    "arkhangelsk": "arkhangelskaya", "nizhny novgorod": "nizhny novgorod", "nizhniy novgorod": "nizhny novgorod",
    "khanty-mansi": "khanty-mansia", "yamalo-nenets": "yamalo-nenets", "mari el": "mariy-el",
    "kemerovo": "kuzbass", "dagestan": "dagestan", "chechnya": "chechnya",
}
# regioni che gli analisti nominano anche senza "Oblast" (nomi non ambigui con città)
OBLAST_NUDE = {"crimea", "crimée", "tatarstan", "bashkortostan", "bashkiria", "dagestan", "chechnya",
               "udmurtia", "chuvashia", "mordovia", "kuban", "adygea", "kalmykia", "zakarpattia",
               "transcarpathia", "volhynia", "ingushetia", "karelia", "krasnodar krai", "stavropol krai",
               "perm krai", "kuzbass"}

# Nomi d'uso degli analisti (traslitterazioni inglesi/francesi) -> nome nel gazetteer
CITTA_ALIAS = {
    "kyiv": "Kyiv", "kiev": "Kyiv", "kharkov": "Kharkiv", "odesa": "Odesa", "odessa": "Odesa",
    "zaporizhzhia": "Zaporizhzhya", "zaporizhia": "Zaporizhzhya", "zaporojie": "Zaporizhzhya",
    "dnipro": "Dnipro", "kryvyi rih": "Kryvyi Rih", "krivoï rog": "Kryvyi Rih",
    "kramatorsk": "Kramatorsk", "sloviansk": "Slovyansk", "kostiantynivka": "Kostiantynivka",
    "pokrovsk": "Pokrovsk", "myrnohrad": "Myrnohrad", "kupiansk": "Kupiansk", "kupyansk": "Kupiansk",
    "huliaipole": "Hulyaypole", "lviv": "Lviv", "lvov": "Lviv", "lutsk": "Lutsk",
    "ivano-frankivsk": "Ivano-Frankivsk", "khmelnytskyi": "Khmelnytskyi", "vinnytsia": "Vinnytsya",
    "chernihiv": "Chernihiv", "tchernihiv": "Chernihiv", "mykolaiv": "Mykolayiv", "kherson": "Kherson",
    "izmail": "Izmayil", "reni": "Reni", "chornomorsk": "Chornomorsk", "pivdennyi": "Yuzhne",
    "burshtyn": "Burshtyn", "ladyzhyn": "Ladyzhyn", "shostka": "Shostka", "konotop": "Konotop",
    "sumy": "Sumy", "poltava": "Poltava", "kremenchuk": "Kremenchuk", "kropyvnytskyi": "Kropyvnytskyy",
    "nikopol": "Nikopol", "pavlohrad": "Pavlohrad", "kamianske": "Kamianske", "bila tserkva": "Bila Tserkva",
    "brovary": "Brovary", "fastiv": "Fastiv", "uzhhorod": "Uzhhorod", "rivne": "Rivne", "ternopil": "Ternopil",
    "zhytomyr": "Zhytomyr", "cherkasy": "Cherkasy", "chernivtsi": "Chernivtsi", "sevastopol": "Sevastopol",
    "simferopol": "Simferopol", "feodosia": "Feodosiya", "kerch": "Kerch", "dzhankoi": "Dzhankoy",
    "yevpatoria": "Yevpatoriya", "saky": "Saky", "donetsk": "Donetsk", "luhansk": "Luhansk",
    "mariupol": "Mariupol", "berdiansk": "Berdyans'k", "melitopol": "Melitopol", "makiivka": "Makiyivka",
    "horlivka": "Horlivka", "enerhodar": "Enerhodar", "nova kakhovka": "Nova Kakhovka",
    # Russia
    "moscow": "Moscow", "moscou": "Moscow", "saint petersburg": "Saint Petersburg",
    "st. petersburg": "Saint Petersburg", "saint-pétersbourg": "Saint Petersburg",
    "belgorod": "Belgorod", "kursk": "Kursk", "bryansk": "Bryansk", "voronezh": "Voronezh",
    "rostov-on-don": "Rostov-na-Donu", "rostov": "Rostov-na-Donu", "taganrog": "Taganrog",
    "novorossiysk": "Novorossiysk", "novorossiisk": "Novorossiysk", "tuapse": "Tuapse",
    "krasnodar": "Krasnodar", "sochi": "Sochi", "ryazan": "Ryazan", "riazan": "Ryazan",
    "yaroslavl": "Yaroslavl", "iaroslavl": "Yaroslavl", "kstovo": "Kstovo", "kirishi": "Kirishi",
    "ust-luga": "RU:Ust'-Luga", "primorsk": "RU:Primorsk", "prymorsk": "UA:Prymorsk", "volgograd": "Volgograd", "saratov": "Saratov",
    "engels": "Engels", "samara": "Samara", "syzran": "Syzran", "novokuibyshevsk": "Novokuybyshevsk",
    "novokuybyshevsk": "Novokuybyshevsk", "ufa": "Ufa", "salavat": "Salavat", "orsk": "Orsk",
    "kazan": "Kazan", "nizhnekamsk": "Nizhnekamsk", "almetyevsk": "Al'met'yevsk",
    "cheboksary": "Cheboksary", "tambov": "Tambov", "lipetsk": "Lipetsk", "oryol": "Orel",
    "orel": "Orel", "tula": "Tula", "kaluga": "Kaluga", "smolensk": "Smolensk", "tver": "Tver",
    "penza": "Penza", "astrakhan": "Astrakhan", "makhachkala": "Makhachkala", "grozny": "Groznyy",
    "armavir": "Armavir", "slavyansk-na-kubani": "Slavyansk-na-Kubani", "yeysk": "Yeysk",
    "millerovo": "Millerovo", "morozovsk": "Morozovsk", "kamensk-shakhtinsky": "Kamensk-Shakhtinskiy",
    "novoshakhtinsk": "Novoshakhtinsk", "shakhty": "Shakhty", "bataysk": "Bataysk",
    "kotovo": "Kotovo", "michurinsk": "Michurinsk", "zheleznogorsk": "Zheleznogorsk",
    "kurchatov": "Kurchatov", "novocherkassk": "Novocherkassk", "perm": "Perm",
    "nizhny novgorod": "Nizhniy Novgorod", "dzerzhinsk": "Dzerzhinsk", "cherepovets": "Cherepovets",
    "murmansk": "Murmansk", "olenya": "Olenegorsk", "olenegorsk": "Olenegorsk",
    "novoshakhtinsky": "Novoshakhtinsk", "afipsky": "Afipskiy", "afipskiy": "Afipskiy",
    "ilsky": "Il'skiy", "ilskiy": "Il'skiy", "volzhsky": "Volzhskiy", "atyrau": None,
    "chelyabinsk": "Chelyabinsk", "yekaterinburg": "Yekaterinburg", "omsk": "Omsk",
    "tyumen": "Tyumen", "orenburg": "Orenburg", "togliatti": "Tol'yatti", "tolyatti": "Tol'yatti",
    "sterlitamak": "Sterlitamak", "izhevsk": "Izhevsk", "yelabuga": "Yelabuga", "alabuga": "Yelabuga",
    "kaliningrad": "Kaliningrad", "pskov": "Pskov", "veliky novgorod": "Velikiy Novgorod",
    "anapa": "Anapa", "gelendzhik": "Gelendzhik", "temryuk": "Temryuk", "kavkaz": None,
}

# parole troppo comuni o ambigue da non usare come nomi di luogo
STOP_LUOGHI = {
    "mir", "pobeda", "sovetskiy", "sovetsky", "oktyabrskiy", "lenina", "zarya", "progress",
    "front", "port", "mayak", "ukraine", "russia", "nova", "novyi", "stantsiya", "drone",
    "druzhba", "energetik", "promin", "pervomaisk", "pervomaysk", "zelenyi gai", "russkiy",
    "ugol", "parkovy", "lyman", "liman", "ray", "oleksandrivka", "mykolaivka", "andriivka",
    "ivanivka", "novoselivka", "petrivka", "vasylivka", "bilohorivka", "kamianka",
    "march", "may", "august", "azov", "serhii", "serhiyi", "skala", "artem", "nove", "shevchenko", "ukrainka", "trump", "putin", "ukraina", "nato", "europe", "american", "france",
}


ALIAS_MANCANTI = []


def carica_gazetteer():
    with open(GAZ, encoding="utf-8") as h:
        g = json.load(h)
    idx = {}  # nome minuscolo -> voce (nome principale prima dei nomi alternativi, poi la più popolosa)
    rango = {}
    obl = {}  # nome della regione normalizzato -> voce ADM1
    for v in g["voci"]:
        if v["tipo"] == "oblast":
            obl[norm_obl(v["oblast"])] = v
            obl.setdefault(norm_obl(v["n"]), v)
            continue
        da_labels = bool(v.get("fonte"))
        for j, n in enumerate([v["n"]] + v.get("alt", [])):
            k = n.lower().strip()
            if len(k) < 4 or k in STOP_LUOGHI:
                continue
            r = (0 if da_labels else 1, 1 if j == 0 else 0, v["pop"])
            if k not in idx or r > rango[k]:
                idx[k] = v
                rango[k] = r
    # città dichiarate negli alias
    perno = {}
    for v in g["voci"]:
        if v["tipo"] == "citta" and not v.get("fonte"):
            for k in (v["n"].lower(), v["paese"] + ":" + v["n"].lower()):
                if k not in perno or v["pop"] > perno[k]["pop"]:
                    perno[k] = v
    ALIAS_MANCANTI.clear()
    for a, n in CITTA_ALIAS.items():
        if n is None:
            idx.pop(a, None)
        elif n.lower() in perno:
            idx[a] = perno[n.lower()]
        elif n.lower() in idx and idx[n.lower()]["tipo"] == "citta":
            idx[a] = idx[n.lower()]
        elif a not in idx:
            ALIAS_MANCANTI.append(a)
    for a, k in OBLAST_ALIAS.items():
        if k in obl:
            obl.setdefault(a, obl[k])
    return idx, obl


# ---------------------------------------------------------------- 2. regole

MEZZI = [
    ("Shahed/Geran", r"\bshahed|\bgeran|\bgerbera"),
    ("Iskander", r"iskander|kn-23"),
    ("Kh-101/Kh-555", r"kh-?101|kh-?555|x-101"),
    ("Kalibr", r"\bkalibr"),
    ("Kinzhal", r"kinzhal|kinjal"),
    ("Kh-22/Kh-32", r"kh-?22\b|kh-?32\b"),
    ("Kh-59/Kh-69", r"kh-?59|kh-?69"),
    ("S-300/S-400", r"\bs-?300|\bs-?400"),
    ("KAB/bombe plananti", r"\bkab\b|\bkabs\b|glide bomb|guided aerial bomb|bombe planante|fab-?\d{3,4}"),
    ("missili", r"missile|cruise|ballistic|balistique|\bmissiles?\b"),
    ("droni", r"\bdrones?\b|\buavs?\b|\buas\b|lyuty|liutyi|fp-1\b|fp-5|flamingo|neptune|\bfpv\b|lancet"),
    ("artiglieria/MLRS", r"\bartillery\b|\bartillerie\b|himars|\bmlrs\b|\bgrad\b|tornado-s|uragan|\bsmerch"),
    ("Storm Shadow/SCALP/ATACMS", r"storm shadow|scalp|atacms"),
]
CATEGORIE = [
    ("raffineria/deposito", r"refiner|raffinerie|oil depot|fuel depot|petroleum depot|oil terminal|oil storage|"
                            r"tank farm|d[ée]p[ôo]t p[ée]trolier|d[ée]p[ôo]t de carburant|pumping station|"
                            r"station de pompage|\boil\b|\bpétrol|fuel|carburant|transneft|rosneft|lukoil|gazprom neft"),
    ("energia", r"substation|sous-station|power plant|power station|centrale|\btpp\b|\bchp\b|thermal plant|"
                r"hydroelectric|\bhpp\b|\bnpp\b|nuclear|electric|électri|energy|énergie|énergétique|power grid|"
                r"\bgrid\b|transformer|gas (?:production|facility|field|plant|compressor)|naftogaz|ukrenergo|dtek|"
                r"blackout|power outage|coupure"),
    ("porto", r"\bport\b|\bports\b|seaport|harbou?r|\bpier\b|terminal|vessel|tanker|cargo ship|\bnavire|"
              r"\bship\b|\bships\b|pétrolier"),
    ("ferrovia", r"railway|railroad|\btrain\b|\btrains\b|locomotive|rail\b|rail |ferroviaire|gare\b|"
                 r"train station|ukrzaliznytsia"),
    ("aeroporto", r"airfield|air base|airbase|airport|aérodrome|aéroport|base aérienne"),
    ("militare", r"\bammunition|ammo depot|arsenal|munitions|\bbase\b|command post|headquarters|\bhq\b|"
                 r"radar|air defen[cs]e|s-400|s-300|pantsir|buk\b|tor-m|barracks|military|militaire|"
                 r"positions?\b|brigade|regiment|logistic|tank\b|tanks\b|armou?red|launcher|lanceur"),
    ("industria", r"plant\b|factory|usine|industrial|industriel|enterprise|chemical|chimique|"
                  r"metallurg|steel|aciérie|azot|fertili[sz]er|defen[cs]e industry|electronics|"
                  r"shipyard|chantier naval|warehouse|entrepôt|data cent(?:re|er)|logistics (?:centre|terminal)|nova poshta"),
    ("civile", r"civilian|civil|residential|apartment|building|immeuble|hospital|hôpital|school|école|"
               r"\bkilled\b|\binjured\b|\btués?\b|\bblessés?\b|\bmorts?\b|house|maison|market|shopping|district|"
               r"petrol station|gas station|station-service|\bbus\b|trolleybus|church|église|university"),
]
ATTACCO = re.compile(
    r"\bstrikes?\b|\bstruck\b|\bhit\b|\bhits\b|\battack(?:s|ed)?\b|\bdrones?\b|\bmissiles?\b|shahed|geran|"
    r"iskander|kh-?101|kalibr|\bkabs?\b|refiner|oil depot|substation|explosion|\bfires?\b|\bblaze\b|burning|"
    r"\bfrappes?\b|\bfrappé|\bbombard|raffinerie|d[ée]p[ôo]t|incendie|touch[ée]|\bvisé|"
    r"\bdestroyed\b|\bdétrui", re.I)
# impatto avvenuto (non solo allerta o lancio)
IMPATTO = re.compile(
    r"\bstruck\b|\bwas hit\b|\bwere hit\b|\bbeen hit\b|\bhit (?:a|an|the|two|three|several|multiple|its|their)\b|"
    r"\bhits? on\b|\bimpact(?:ed|s)?\b|\bdamag(?:ed|ing)\b|\bdestroy(?:ed|ing)\b|"
    r"\bfires? (?:broke out|br[eo]ke|is burning|are burning|burning|raging|continu)|\blarge fire|\bmassive fire|"
    r"\bon fire\b|\bblaze\b|\bexplosions? (?:were|was|have been|has been|are being)? ?(?:heard|reported|seen|recorded)|"
    r"\bexplosions? (?:in|at|near|over)\b|\baftermath\b|\btargeted\b|\battacked\b|\battacks? on\b|"
    r"\battacks? against\b|\bstrikes? (?:on|against|at|targeting|hit)\b|\bstrike (?:hit|on)\b|"
    r"\bcame under (?:attack|fire)\b|\bpower outages?\b|\bblackouts?\b|\bkilled\b|\binjured\b|"
    r"\bfrapp[ée]e?s?\b|\bont frapp|\ba frapp|\btouch[ée]e?s?\b|\bvis[ée]e?s?\b|\bincendies?\b|"
    r"\bexplosions?\b.{0,40}\b(?:signal|rapport|entendu)|\bd[ée]g[aâ]ts\b|\bd[ée]truit|\bendommag", re.I)
# allerte e tracciamento di lanci senza impatto confermato
ALLERTA = re.compile(
    r"\bthreat\b|\bflying (?:to|towards|past|over|in)\b|\bheading (?:to|towards|for)\b|\ben route\b|"
    r"\bmoving towards\b|\btook off\b|\btaking off\b|\bairborne\b|\bare (?:redeploying|conducting|preparing)\b|"
    r"\bexpected to\b|\bmay (?:launch|strike)\b|\bcould (?:launch|strike|be)\b|\bwarning\b|\balert\b|"
    r"\bmenace\b|\ben direction de\b", re.I)
# guerra di terra, analisi del fronte
FRONTE = re.compile(
    r"\badvanc|\bcaptur|\bassault|\binfiltrat|\btreelines?\b|counter-?attack|counter-?offensive|\bpositions?\b|"
    r"\bbrigades?\b|\bbattalions?\b|\bregiments?\b|\bcorps\b|mechani[sz]ed|\binfantry\b|\bsoldiers\b|grey zone|"
    r"km²|\bsalient\b|encircl|front ?line|\bfpv\b|\bclearing\b|\bbridgehead\b|\bpocket\b|\bprogress|"
    r"\bavanc|\bprogression|\bassaut|\bfantassins|\bsoldats|\bligne de front|\bencercl|\bcapturé|\bpris le contr|"
    r"\bstalemate\b|\bfighting\b|\bbattle\b|\bcombats?\b|\bgains?\b|\bdirection\b", re.I)
INFRA = re.compile(
    r"refiner|oil depot|fuel depot|substation|power plant|power station|thermal|\bchp\b|\btpp\b|\bhpp\b|"
    r"pumping station|oil terminal|\bport\b|railway|locomotive|airbase|air base|airfield|ammunition depot|"
    r"arsenal|plant\b|factory|raffinerie|d[ée]p[ôo]t|sous-station|centrale|usine|a[ée]roport|a[ée]rodrome", re.I)
MESI = re.compile(r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december|"
                  r"janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b", re.I)
VERBI_FORTI = IMPATTO
DIR_UA = re.compile(
    r"ukrainian (?:long[- ]range |kamikaze |attack |naval |unmanned |sea |)(?:drones?|forces|strikes?|missiles?|uavs?|"
    r"sbu|gur|hur|navy|usv|attack)|\bsbu\b|\bgur\b|\bhur\b|\busf\b|ukraine (?:struck|strikes|hit|attacked|targeted)|"
    r"drones? ukrainiens?|frappes? ukrainiennes?|missiles? ukrainiens?|l'ukraine a (?:frappé|touché|visé)|"
    r"\bles ukrainiens\b|flamingo|neptune|lyuty|liutyi|storm shadow|scalp|atacms|himars|\bfp-1\b|\bfp-5\b|"
    r"russian-controlled|occupied|deep strike|frappe en profondeur|governor|gouverneur|russian mod claims", re.I)
DIR_RU = re.compile(
    r"russian (?:forces |army |)(?:strikes?|missiles?|drones?|attack|shaheds?|bombs?|kabs?|geran|glide)|"
    r"russia (?:struck|strikes|hit|attacked|launched|targeted)|shahed|geran|iskander|kh-?101|kalibr|"
    r"kinzhal|\bkabs?\b|glide[- ]bomb|banderol|frappes? russes?|drones? russes|missiles? russes|"
    r"la russie a (?:frappé|lancé|visé)|ukrenergo|naftogaz|dtek|ukrzaliznytsia|ukrainian air force|"
    r"air defen[cs]e of ukraine", re.I)
COORD = re.compile(r"(?<![\d.])([45]\d\.\d{3,6})\s*[,;/ ]\s*([2-9]\d\.\d{3,6}|1[0-4]\d\.\d{3,6})(?![\d.])")
# luoghi da non usare (persone, unità, nomi in codice) quando seguono/precedono certe parole
NON_LUOGO = re.compile(r"^(?:\s+(?:putin|zelensky|zelenskyy|solovyov|saldo)|['’]s (?:mayor|governor|administration)|"
                       r"\s+(?:says|said|claims|claimed|reports|government|regime|officials))", re.I)
PRIMA_LANCIO = re.compile(r"(?:from|from near|launched from|de|depuis|d'|over|by)\s+(?:the\s+)?(?:\w+\s+)?$", re.I)
PRIMA_LUOGO = re.compile(r"(?:\bin|\bon|\bat|\bnear|\bof|\bstruck|\bhit|\btargeted|\btargeting|\battacked|\bà|\bsur|"
                         r"\bdans|\bprès de|\bcity of|\btown of|\bvillage of)\s+(?:the\s+)?(?:city\s+of\s+|town\s+of\s+)?$",
                         re.I)


# Impianti con coordinate OSM già presenti in docs/data/ucraina-storico.json (precisione 2–10 km):
# regola sul testo -> parte del nome dell'impianto in quel file
IMPIANTI = [
    (r"kirishi", "Kirishi"), (r"kstovo|norsi", "Kstovo"), (r"yaroslavl\w*.{0,40}refiner|yanos|slavneft", "Jaroslavl"),
    (r"ryazan\w*.{0,40}refiner|riazan\w*.{0,40}raffinerie|raffinerie de riazan|refinery in ryazan", "Riazan"),
    (r"saratov\w*.{0,40}refiner|raffinerie de saratov|refinery in saratov", "Raffineria di Saratov"),
    (r"volgograd\w*.{0,40}refiner|raffinerie de volgograd|refinery in volgograd", "Raffineria di Volgograd"),
    (r"tuapse", "Tuapse"), (r"afips", "Afipskij"), (r"\bilsk", "Ilskij"), (r"novoshakhtinsk", "Novošachtinsk"),
    (r"syzran", "Syzran"), (r"novokuybyshevsk|novokuibyshevsk|novokouïbychevsk", "Novokujbyševsk"),
    (r"salavat", "Salavat"), (r"\bufa\b.{0,40}refiner|bashneft|raffinerie d'oufa|raffineries? d'ufa", "Ufa"),
    (r"\borsk\b", "Orsk"), (r"\bomsk\b.{0,40}refiner", "Omsk"), (r"\bperm\b.{0,40}refiner|permnefteorgsintez", "Perm"),
    (r"ukhta", "Uchta"), (r"taneco|nizhnekamsk", "TANECO"), (r"kapotnya|moscow (?:oil )?refinery", "Mosca"),
    (r"slavyansk-na-kubani|slaviansk-na-kubani|slavyansk eco", "Slavjansk"), (r"ust-luga|oust-louga", "Ust-Luga"),
    (r"\bprimorsk\b", "Primorsk"), (r"sheskharis", "Novorossijsk"), (r"tamanneftegaz|\btaman\b", "Taman"),
    (r"unecha", "Unecha"), (r"kavkazskaya", "Kavkazskaja"), (r"vtorovo", "Vtorovo"), (r"prosvet", "Prosvet"),
    (r"kuibyshev refinery|kuybyshev refinery|samara refinery", "Kujbyšev"), (r"antipinsk", "Antipinskij"),
    (r"belaya air|belaya airbase|belaïa", "Belaja"), (r"olenya|olenegorsk", "Olenja"), (r"engels", "Engels-2"),
    (r"marinovka", "Marinovka"), (r"morozovsk", "Morozovsk"), (r"millerovo", "Millerovo"),
    (r"borisoglebsk", "Borisoglebsk"), (r"akhtubinsk", "Achtubinsk"), (r"dyagilevo|diaghilevo|dyaghilevo", "Djagilevo"),
    (r"yeysk air|yeysk airbase|yeysk airfield", "Base aerea di Ejsk"), (r"khanskaya", "Chanskaja"),
    (r"savasleyka", "Savasleika"), (r"soltsy", "Sol'cy"), (r"shaykovka|shaikovka", "Šajkovka"),
    (r"lipetsk air", "Lipeck"), (r"khalino", "Kursk-Chalino"), (r"krymsk", "Krymsk"),
    (r"kushchevskaya", "Kuščëvskaja"), (r"chkalovsk", "Čkalovskij"), (r"ivanovo[- ]sever", "Ivanovo-Severnyj"),
    (r"\bkavkaz port|port kavkaz|port of kavkaz", "Porto Kavkaz"), (r"surgut", "Surgut"),
    (r"orenburg gas|orenburg gas processing|gazprom.{0,30}orenburg", "Orenburg"),
    (r"feodosi\w*.{0,40}(?:oil|terminal|depot)", "Feodosia"), (r"proletarsk", "Proletarsk"),
    (r"novospassk", "Novospasskoe"), (r"\bklintsy\b.{0,40}(?:oil|depot)", "Klincy"),
]


def carica_impianti():
    try:
        with open(os.path.join(DATI, "ucraina-storico.json"), encoding="utf-8") as h:
            el = json.load(h)["elementi"]
    except Exception:
        return []
    out = []
    for rx, pezzo in IMPIANTI:
        for e in el:
            if pezzo in e["nome"] and e.get("lat") is not None:
                out.append((re.compile(rx, re.I), e))
                break
    return out


def trova_luoghi(testo, idx, obl):
    """Ritorna lista di (voce, tipo, posizione) trovati nel testo."""
    t = testo
    tl = t.lower()
    trovati = []
    # oblast esplicite ("X Oblast", "X Krai", "X region", "oblast de X", "region of X") e regioni nominate da sole
    for m in re.finditer(r"([A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-]+(?:[ \-][A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-]+)?)[ \-](?:oblast|Oblast|region|Region|Krai|krai|Kray|Republic|republic)\b", t):
        nome = m.group(1)
        v = obl.get(norm_obl(nome)) or obl.get(nome.lower())
        if not v and " " in nome:  # "Northern Kharkiv" -> "Kharkiv"
            v = obl.get(norm_obl(nome.split(" ")[-1]))
        if v:
            trovati.append((v, "oblast", m.start()))
    for m in re.finditer(r"(?:[Oo]blast|[Rr]égion|[Rr]egion|[Kk]raï) (?:de |d'|du |of )(?:la |l')?([A-ZÀ-Ý][A-Za-zÀ-ÿ'\-]+)", t):
        v = obl.get(norm_obl(m.group(1))) or obl.get(m.group(1).lower())
        if v:
            trovati.append((v, "oblast", m.start()))
    for nome in OBLAST_NUDE:
        for m in re.finditer(r"(?<![A-Za-zà-ÿ])" + re.escape(nome) + r"(?![a-zà-ÿ])", tl):
            v = obl.get(norm_obl(nome)) or obl.get(nome)
            if v:
                trovati.append((v, "oblast", m.start()))
    # città: parole con iniziale maiuscola (1–3 parole), lunghezza >= 4
    for m in re.finditer(r"\b[A-ZÀ-Ý][A-Za-zÀ-ÿ'\-]+(?:[ \-](?:na|on|de|nad|Don|[A-ZÀ-Ý][A-Za-zÀ-ÿ'\-]+)){0,2}", t):
        frase = m.group(0)
        parti = frase.split(" ")
        # prova la sequenza più lunga poi le più corte
        for n in range(len(parti), 0, -1):
            sotto = " ".join(parti[:n])
            k = sotto.lower().strip("'-")
            if k.endswith("'s"):
                k = k[:-2]
            v = idx.get(k)
            if v and v["tipo"] == "citta":
                fine = m.start() + len(sotto)
                seg = tl[fine: fine + 9]
                if re.match(r"[ \-](?:oblast|region|krai|kray|republic)", seg):
                    break  # è la regione, già presa sopra
                if re.search(r"(?:oblast|région|region) (?:de |d'|of )$", tl[max(0, m.start() - 12): m.start()]):
                    break
                trovati.append((v, "citta", m.start()))
                break
    return trovati


def classifica(testo):
    tl = testo.lower()
    cats = []
    for nome, rx in CATEGORIE:
        m = re.search(rx, tl)
        if m:
            cats.append((m.start(), nome))
    # priorità: bersagli specifici prima di "civile"
    ordine = [n for n, _ in CATEGORIE]
    if not cats:
        return "altro"
    nomi = {c for _, c in cats}
    for c in ordine:
        if c in nomi:
            return c
    return "altro"


def mezzi(testo):
    tl = testo.lower()
    out = [n for n, rx in MEZZI if re.search(rx, tl)]
    if "missili" in out and len([x for x in out if x in ("Iskander", "Kh-101/Kh-555", "Kalibr", "Kinzhal",
                                                          "Kh-22/Kh-32", "Kh-59/Kh-69", "S-300/S-400",
                                                          "Storm Shadow/SCALP/ATACMS")]):
        out.remove("missili")
    if "droni" in out and "Shahed/Geran" in out:
        out.remove("droni")
    return out


def direzione(testo, luogo_paese, occupato):
    ua = len(DIR_UA.findall(testo))
    ru = len(DIR_RU.findall(testo))
    if luogo_paese == "RU" or occupato:
        if ru > ua + 1 and luogo_paese != "RU":
            return "russo su Ucraina"
        return "ucraino su Russia o territori occupati"
    if luogo_paese == "UA":
        if ua > ru and re.search(r"ukrainian (?:drones?|missiles?|strikes?)", testo, re.I):
            return "ucraino su Russia o territori occupati"
        return "russo su Ucraina"
    if ua > ru:
        return "ucraino su Russia o territori occupati"
    if ru > ua:
        return "russo su Ucraina"
    return None


# territori occupati (approssimazione: Crimea e oblast di Donetsk/Luhansk sono trattati
# come occupati per città; Zaporizhzhia/Kherson solo per le città note sotto controllo russo)
OCCUPATE_OBLAST = {"crimea", "sevastopol", "luhansk"}
OCCUPATE_CITTA = {"donetsk", "makiyivka", "horlivka", "mariupol", "melitopol", "berdyans'k", "enerhodar",
                  "nova kakhovka", "skadovsk", "henichesk", "tokmak", "yenakiieve", "yenakiyeve",
                  "khartsyzk", "debaltseve", "ilovaisk", "shakhtarsk", "torez", "chystiakove", "snizhne",
                  "dokuchaievsk", "volnovakha", "polohy", "vasylivka", "kakhovka", "oleshky",
                  "hola prystan", "dzhankoy", "kerch", "sevastopol", "simferopol", "feodosiya",
                  "yevpatoriya", "saky", "yalta", "alushta", "armyansk", "krasnoperekops'k",
                  "luhansk", "alchevsk", "sievierodonetsk", "lysychansk", "rubizhne", "stakhanov",
                  "rovenky", "sverdlovs'k", "krasnyi luch", "antratsyt", "brianka", "starobilsk"}


def oblast_ua_occupato(v):
    o = (v.get("oblast") or "").lower()
    if any(x in o for x in OCCUPATE_OBLAST):
        return True
    return v["tipo"] == "citta" and v["n"].lower() in OCCUPATE_CITTA


def estrai_attacco(post, idx, obl, impianti=()):
    t = post["testo"]
    if not t or len(t) < 25:
        return None, "testo vuoto o troppo corto"
    if not ATTACCO.search(t):
        return None, "nessuna parola chiave d'attacco"
    imp = IMPATTO.search(t)
    if not imp:
        return None, "nessun impatto (solo menzione)"
    infra = INFRA.search(t)
    if len(set(m.lower() for m in MESI.findall(t))) >= 3 or len(re.findall(r"\d+", t)) >= 25:
        return None, "post di sintesi o statistiche"
    nfr = len(FRONTE.findall(t))
    if (nfr >= 2 and not infra) or nfr >= 4 or (nfr >= 1 and not infra and len(t) > 500) \
            or re.match(r"\s*situation (?:on|in|near|around)", t, re.I):
        return None, "post sul fronte terrestre"
    if ALLERTA.search(t) and not re.search(r"\bstruck\b|\bimpact|\bdamag|\bfire|\bexplosions? (?:were|was) (?:heard|reported)"
                                           r"|\baftermath|\bfrapp|\btouch|\bincendie", t, re.I):
        return None, "allerta o lancio senza impatto"
    luoghi = []
    for v, tipo, pos in trova_luoghi(t, idx, obl):
        dopo = t[pos + len(v["n"]): pos + len(v["n"]) + 40] if tipo == "citta" else ""
        frase = re.match(r"[A-Za-zÀ-ÿ'’\-]+(?:[ \-][A-ZÀ-Ý][A-Za-zÀ-ÿ'’\-]+)*", t[pos:])
        if frase:
            dopo = t[pos + len(frase.group(0)): pos + len(frase.group(0)) + 40]
        if tipo == "citta" and (NON_LUOGO.match(dopo) or re.match(r"[A-Z]\w+\s+(?:Putin|Zelensk|Solovyov)", t[pos:])):
            continue
        prima = t[max(0, pos - 30): pos]
        lancio = bool(PRIMA_LANCIO.search(prima))
        prep = bool(PRIMA_LUOGO.search(prima))
        luoghi.append((v, tipo, pos, lancio, prep))
    coord = None
    m = COORD.search(t)
    if m:
        la, lo = float(m.group(1)), float(m.group(2))
        if 43 <= la <= 70 and 20 <= lo <= 140:
            coord = (la, lo)
    impianto = None
    for rx, e in impianti:
        mm = rx.search(t)
        if mm and not PRIMA_LANCIO.search(t[max(0, mm.start() - 30): mm.start()]):
            impianto = e
            break
    if not luoghi and not coord and not impianto:
        return None, "nessun luogo riconosciuto"
    vpos = imp.start()

    def punteggio(x):
        v, tipo, pos, lancio, prep = x
        return (lancio, 0 if tipo == "citta" else 1, 0 if prep else 1, abs(pos - vpos))
    cand = sorted([x for x in luoghi if x[0].get("paese") in ("UA", "RU", "")], key=punteggio)
    if cand and cand[0][3] and not impianto and not coord:
        return None, "solo luoghi di lancio"
    scelto = cand[0] if cand else None
    v, tipo = (scelto[0], scelto[1]) if scelto else (None, None)
    paese = (v.get("paese") or "") if v else ""
    if v and not paese:
        w = idx.get(v["n"].lower())
        paese = w.get("paese", "") if w else ""
    if impianto:
        lat, lon = impianto["lat"], impianto["lon"]
        prec = impianto.get("precisione_km") or 3
        orig = "impianto in ucraina-storico.json (%s; %s)" % (impianto["nome"], impianto.get("origine_coord", "OSM"))
        nome = impianto["nome"]
        paese = impianto.get("paese") or "RU"
        obl_n = impianto.get("regione") or ""
    elif coord:
        lat, lon, prec, orig = coord[0], coord[1], 1, "coordinate scritte nel post"
        nome = v["n"] if v else "coordinate del post"
        obl_n = (v.get("oblast") if v else "") or ""
        if v:
            if dist_km(lat, lon, v["lat"], v["lon"]) > 150:
                nome, obl_n, paese = "coordinate del post", "", ""
        if not paese:
            paese = "RU" if lon > 40.3 or lat > 52.4 else "UA"
    else:
        lat, lon = v["lat"], v["lon"]
        prec = 10 if tipo == "citta" else 80
        orig = "GeoNames: %s (%s)" % (v["n"], "centro abitato" if tipo == "citta" else "regione")
        nome, obl_n = v["n"], v.get("oblast") or ""
        if not paese:
            paese = "RU" if lon > 40.3 or lat > 52.4 else "UA"
    if paese not in ("UA", "RU"):
        return None, "luogo fuori da Ucraina/Russia"
    occupato = paese == "UA" and v is not None and not impianto and oblast_ua_occupato(v)
    if impianto and "Crimea" in impianto["nome"]:
        occupato = True
    d = direzione(t, paese, occupato)
    if d is None:
        return None, "direzione non determinata"
    return {
        "post": post,
        "lat": round(lat, 4), "lon": round(lon, 4), "precisione_km": prec, "origine_coord": orig,
        "luogo": nome, "oblast": obl_n, "paese": paese, "occupato": occupato,
        "direzione": d, "categoria": classifica(t), "mezzi": mezzi(t),
        "luoghi_citati": len({x[0]["n"] for x in luoghi}),
    }, "ok"


# ---------------------------------------------------------------- incroci

def dist_km(a, b, c, d):
    r = math.pi / 180
    x = (d - b) * r * math.cos((a + c) / 2 * r)
    y = (c - a) * r
    return 6371 * math.hypot(x, y)


def giorno(s):
    return dt.date.fromisoformat(s[:10])


def riferimenti():
    rif = []
    try:
        with open(os.path.join(DATI, "attacchi-russi.json"), encoding="utf-8") as h:
            for e in json.load(h)["elementi"]:
                rif.append(("attacchi-russi.json", e["id"], giorno(e["data"]), e["lat"], e["lon"], e.get("link")))
    except Exception as e:
        avviso("attacchi-russi.json non letto: %s" % e)
    try:
        with open(os.path.join(DATI, "ucraina-storico.json"), encoding="utf-8") as h:
            for e in json.load(h)["elementi"]:
                if e.get("data_evento") and e.get("lat") is not None:
                    rif.append(("ucraina-storico.json", e["id"], giorno(e["data_evento"]), e["lat"], e["lon"],
                                e.get("link")))
    except Exception as e:
        avviso("ucraina-storico.json non letto: %s" % e)
    return rif


class Griglia:
    """Indice spazio-temporale: celle di 0,5° per giorno."""

    def __init__(self, punti, chiave_data, chiave_lat, chiave_lon):
        self.c = {}
        for p in punti:
            k = (chiave_data(p), int(math.floor(chiave_lat(p) * 2)), int(math.floor(chiave_lon(p) * 2)))
            self.c.setdefault(k, []).append(p)

    def vicini(self, d, lat, lon, giorni):
        out = []
        for dd in range(-giorni, giorni + 1):
            g = d + dt.timedelta(days=dd)
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    out.extend(self.c.get((g, int(math.floor(lat * 2)) + i, int(math.floor(lon * 2)) + j), []))
        return out


# ---------------------------------------------------------------- 3. FIRMS

FIRMS_ARCHIVI = [
    # file pubblici senza chiave: ultimi 7 giorni (globale) per VIIRS e MODIS
    ("VIIRS_SNPP_NRT", "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_7d.csv"),
    ("VIIRS_NOAA20_NRT", "https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_Global_7d.csv"),
    ("VIIRS_NOAA21_NRT", "https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-21-viirs-c2/csv/J2_VIIRS_C2_Global_7d.csv"),
    ("MODIS_NRT", "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_7d.csv"),
]
# riquadro Ucraina + Russia europea + Urali (dove avvengono quasi tutti gli attacchi all'energia)
BBOX = (22.0, 43.0, 62.0, 62.0)  # ovest, sud, est, nord


def leggi_csv_fuochi(testo, fuochi, fonte):
    n = 0
    for r in csv.DictReader(io.StringIO(testo)):
        try:
            la, lo = float(r["latitude"]), float(r["longitude"])
        except (KeyError, ValueError):
            continue
        if not (BBOX[1] <= la <= BBOX[3] and BBOX[0] <= lo <= BBOX[2]):
            continue
        d = r.get("acq_date")
        if not d:
            continue
        fuochi.append((dt.date.fromisoformat(d), la, lo, fonte))
        n += 1
    return n


def carica_firms(attacchi):
    """Ritorna (lista fuochi, info fonti). Usa: archivi CSV pubblici a 7 giorni (senza chiave);
    API area con FIRMS_MAP_KEY per le date degli attacchi (10 giorni per richiesta, archivio SP)."""
    fuochi, info = [], []
    cart = os.path.join(CACHE, "firms")
    os.makedirs(cart, exist_ok=True)
    for nome, url in FIRMS_ARCHIVI:
        try:
            t = scarica_url(url, timeout=180)
            n = leggi_csv_fuochi(t, fuochi, nome)
            info.append({"nome": "NASA FIRMS %s (CSV pubblico, ultimi 7 giorni)" % nome, "link": url,
                         "esito": "funziona", "focolai_nel_riquadro": n})
        except Exception as e:
            info.append({"nome": "NASA FIRMS %s (CSV pubblico)" % nome, "link": url, "esito": "errore: %s" % e})
            avviso("FIRMS %s: %s" % (nome, e))
    # archivi annuali per paese (pubblici, zip) - https://firms.modaps.eosdis.nasa.gov/country/
    for anno in range(2022, ADESSO.year + 1):
        for prod in ("viirs-snpp", "modis"):
            for paese in ("Ukraine", "Russian_Federation"):
                f = os.path.join(cart, "%s_%d_%s_riquadro.csv.gz" % (prod, anno, paese))
                url = "https://firms.modaps.eosdis.nasa.gov/data/country/%s/%d/%s_%d_%s.csv" % (
                    prod, anno, prod, anno, paese)
                nome = "NASA FIRMS archivio annuale per paese %s %d %s" % (prod, anno, paese)
                try:
                    if os.path.exists(f):
                        with gzip.open(f, "rt", encoding="utf-8") as h:
                            t = h.read()
                        nome += " (cache)"
                    else:
                        t = scarica_url(url, timeout=900, tentativi=2)
                        # tiene solo le colonne e le righe utili (riquadro), per una cache piccola
                        righe = ["latitude,longitude,acq_date"]
                        for r in csv.DictReader(io.StringIO(t)):
                            try:
                                la, lo = float(r["latitude"]), float(r["longitude"])
                            except (KeyError, ValueError):
                                continue
                            if BBOX[1] <= la <= BBOX[3] and BBOX[0] <= lo <= BBOX[2]:
                                righe.append("%s,%s,%s" % (r["latitude"], r["longitude"], r["acq_date"]))
                        t = "\n".join(righe) + "\n"
                        with gzip.open(f, "wt", encoding="utf-8") as h:
                            h.write(t)
                    n = leggi_csv_fuochi(t, fuochi, prod)
                    info.append({"nome": nome, "link": url, "esito": "funziona", "focolai_nel_riquadro": n})
                except Exception as e:
                    info.append({"nome": nome, "link": url, "esito": "non disponibile: %s" % str(e)[:120]})
    chiave = os.environ.get("FIRMS_MAP_KEY")
    if not chiave:
        avviso("FIRMS_MAP_KEY assente: salto l'API area di NASA FIRMS (uso solo gli archivi pubblici)")
        info.append({"nome": "NASA FIRMS API area", "link": "https://firms.modaps.eosdis.nasa.gov/api/area/",
                     "esito": "serve chiave (FIRMS_MAP_KEY, gratuita)"})
        return fuochi, info
    # API area: per ogni finestra di 10 giorni che contiene attacchi energetici
    date = sorted({a["data"] for a in attacchi})
    finestre = sorted({(dt.date.fromisoformat(d) - dt.timedelta(days=1)) for d in date})
    fatte = set()
    n_tot = 0
    for f0 in finestre:
        if any(0 <= (f0 - x).days < 8 for x in fatte):
            continue
        fatte.add(f0)
        for src in ("VIIRS_SNPP_SP", "VIIRS_SNPP_NRT", "MODIS_SP"):
            url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/%s/%s/%d,%d,%d,%d/10/%s" % (
                chiave, src, *BBOX, f0.isoformat())
            fc = os.path.join(cart, "api_%s_%s.csv.gz" % (src, f0.isoformat()))
            try:
                if os.path.exists(fc):
                    with gzip.open(fc, "rt", encoding="utf-8") as h:
                        t = h.read()
                else:
                    t = scarica_url(url, timeout=180, tentativi=2)
                    with gzip.open(fc, "wt", encoding="utf-8") as h:
                        h.write(t)
                    time.sleep(1)
                n_tot += leggi_csv_fuochi(t, fuochi, src)
            except Exception as e:
                avviso("FIRMS API %s %s: %s" % (src, f0, str(e).replace(chiave, "***")))
    info.append({"nome": "NASA FIRMS API area (VIIRS SNPP SP/NRT, MODIS SP)",
                 "link": "https://firms.modaps.eosdis.nasa.gov/api/area/", "esito": "funziona",
                 "focolai_nel_riquadro": n_tot})
    return fuochi, info


# ---------------------------------------------------------------- uscita

def estratto(t, n=160):
    t = re.sub(r"\s+", " ", t).strip()
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + "…"


def estrai_tutto(senza_firms=False):
    idx, obl = carica_gazetteer()
    posts, info_canali = [], []
    for c in CANALI:
        st = carica_cache(c["canale"])
        ps = sorted(st["posts"].values(), key=lambda p: p["id"])
        posts.extend(ps)
        info_canali.append({"canale": c["canale"], "autore": c["autore"], "post_letti": len(ps),
                            "con_testo": sum(1 for p in ps if p["testo"]),
                            "con_immagini": sum(1 for p in ps if p["immagini"]),
                            "con_video": sum(1 for p in ps if p["video"]),
                            "primo_post": ps[0]["data"] if ps else None,
                            "ultimo_post": ps[-1]["data"] if ps else None,
                            "cronologia_completa": st["completo"]})
    motivi = {}
    grezzi = []
    impianti = carica_impianti()
    for p in posts:
        a, mot = estrai_attacco(p, idx, obl, impianti)
        motivi[mot] = motivi.get(mot, 0) + 1
        if a:
            a["data"] = p["data"][:10]
            grezzi.append(a)
    # deduplica nello stesso canale: stesso luogo, stessa data, stessa categoria -> un attacco
    visti, attacchi = {}, []
    for a in grezzi:
        k = (a["post"]["canale"], a["data"], a["luogo"], a["categoria"], a["direzione"])
        if k in visti:
            visti[k]["altri_post"].append(a["post"]["link"])
            continue
        a["altri_post"] = []
        visti[k] = a
        attacchi.append(a)
    # incroci
    rif = riferimenti()
    g_rif = Griglia(rif, lambda r: r[2], lambda r: r[3], lambda r: r[4])
    g_att = Griglia(attacchi, lambda a: giorno(a["data"]), lambda a: a["lat"], lambda a: a["lon"])
    for a in attacchi:
        d = giorno(a["data"])
        corr = []
        for r in g_rif.vicini(d, a["lat"], a["lon"], 1):
            if dist_km(a["lat"], a["lon"], r[3], r[4]) <= 30:
                corr.append({"file": r[0], "id": r[1], "link": r[5]})
        altro = None
        for b in g_att.vicini(d, a["lat"], a["lon"], 1):
            if b["post"]["canale"] != a["post"]["canale"] and b["direzione"] == a["direzione"] \
                    and dist_km(a["lat"], a["lon"], b["lat"], b["lon"]) <= 30:
                altro = b["post"]["link"]
                break
        if altro:
            corr.append({"canale": "altro canale", "link": altro})
        a["corroborato_da"] = corr
    # FIRMS per l'energia (energia + raffineria/deposito) con coordinata di città o migliore
    energetici = [a for a in attacchi if a["categoria"] in ("energia", "raffineria/deposito")
                  and a["precisione_km"] <= 10]
    info_firms = []
    if not senza_firms:
        fuochi, info_firms = carica_firms(energetici)
        g_f = Griglia(fuochi, lambda f: f[0], lambda f: f[1], lambda f: f[2])
        date_f = sorted({f[0] for f in fuochi})
        copertura = set(date_f)
        for a in energetici:
            d = giorno(a["data"])
            # finestra 2 giorni: dal giorno dell'attacco ai 2 giorni dopo (e il giorno prima, per l'orario UTC)
            if not any((d + dt.timedelta(days=k)) in copertura for k in range(-1, 3)):
                a["firms"] = None  # nessun dato FIRMS per quelle date
                continue
            hit = None
            for f in g_f.vicini(d, a["lat"], a["lon"], 2):
                if -1 <= (f[0] - d).days <= 2 and dist_km(a["lat"], a["lon"], f[1], f[2]) <= 5:
                    hit = f
                    break
            a["firms"] = bool(hit)
            if hit:
                a["firms_focolaio"] = {"data": hit[0].isoformat(), "lat": round(hit[1], 4),
                                       "lon": round(hit[2], 4), "prodotto": hit[3]}
    # elementi finali
    elementi = []
    for i, a in enumerate(sorted(attacchi, key=lambda x: (x["data"], x["post"]["canale"], x["post"]["id"]))):
        p = a["post"]
        e = {
            "id": "an-%s-%s-%d" % (a["data"], "cm" if p["canale"] == "clement_molin" else "amk", p["id"]),
            "data": a["data"], "data_post_utc": p["data"],
            "direzione": a["direzione"],
            "lat": a["lat"], "lon": a["lon"], "precisione_km": a["precisione_km"],
            "origine_coord": a["origine_coord"],
            "nome": a["luogo"], "oblast": a["oblast"], "paese": a["paese"],
            "territorio_occupato": a["occupato"],
            "categoria": a["categoria"], "mezzi": a["mezzi"], "luoghi_citati": a["luoghi_citati"],
            "fonte": "%s (Telegram @%s)" % ("Clément Molin" if p["canale"] == "clement_molin" else "AMK Mapping",
                                             p["canale"]),
            "canale": p["canale"], "link": p["link"], "data_fonte": p["data"][:10],
            "estratto": estratto(p["testo"]),
            "immagini": p["immagini"], "video": p["video"],
            "affidabilita": "alta" if a["corroborato_da"] else "media",
            "stato": "segnalato da analista OSINT" + (" e corroborato" if a["corroborato_da"] else ", non corroborato"),
        }
        if a["corroborato_da"]:
            e["corroborato_da"] = a["corroborato_da"][:3]
        if a.get("altri_post"):
            e["altri_post"] = a["altri_post"][:5]
        if "firms" in a:
            e["firms"] = a["firms"]
            if a.get("firms_focolaio"):
                e["firms_focolaio"] = a["firms_focolaio"]
        elementi.append(e)
    # riepilogo
    rie = {"per_anno": {}, "per_direzione": {}, "per_categoria": {}, "per_anno_direzione_categoria": {},
           "per_canale": {}, "corroborati": 0, "firms_verificati": 0, "firms_positivi": 0,
           "motivi_scarto_post": dict(sorted(motivi.items(), key=lambda x: -x[1]))}
    for e in elementi:
        y = e["data"][:4]
        rie["per_anno"][y] = rie["per_anno"].get(y, 0) + 1
        rie["per_direzione"][e["direzione"]] = rie["per_direzione"].get(e["direzione"], 0) + 1
        rie["per_categoria"][e["categoria"]] = rie["per_categoria"].get(e["categoria"], 0) + 1
        rie["per_canale"][e["canale"]] = rie["per_canale"].get(e["canale"], 0) + 1
        x = rie["per_anno_direzione_categoria"].setdefault(y, {}).setdefault(e["direzione"], {})
        x[e["categoria"]] = x.get(e["categoria"], 0) + 1
        rie["corroborati"] += e["affidabilita"] == "alta"
        if e.get("firms") is not None and "firms" in e:
            rie["firms_verificati"] += 1
            rie["firms_positivi"] += bool(e["firms"])
    rie["per_anno"] = dict(sorted(rie["per_anno"].items()))
    rie["per_anno_direzione_categoria"] = dict(sorted(rie["per_anno_direzione_categoria"].items()))
    out = {
        "aggiornato": ADESSO.strftime("%Y-%m-%dT%H:%MZ"),
        "fonti": [
            {"nome": "Clément Molin, canale Telegram pubblico @clement_molin", "link": "https://t.me/s/clement_molin",
             "licenza": "diritti dell'autore: solo fatti, estratto <=160 caratteri e link al post",
             "data_dato": info_canali[0]["ultimo_post"]},
            {"nome": "AMK Mapping, canale Telegram pubblico @AMK_Mapping", "link": "https://t.me/s/AMK_Mapping",
             "licenza": "diritti dell'autore: solo fatti, estratto <=160 caratteri e link al post",
             "data_dato": info_canali[1]["ultimo_post"]},
            {"nome": "GeoNames (gazetteer: città e regioni di UA e RU)", "link": "https://www.geonames.org/",
             "licenza": "CC BY 4.0", "data_dato": ADESSO.strftime("%Y-%m-%d")},
            {"nome": "NASA FIRMS (focolai VIIRS/MODIS)", "link": "https://firms.modaps.eosdis.nasa.gov/",
             "licenza": "dati NASA, uso libero con citazione", "data_dato": ADESSO.strftime("%Y-%m-%d"),
             "dettaglio": info_firms},
        ],
        "nota": ("elementi = attacchi a lungo raggio estratti con regole a parole chiave dai post di due analisti "
                 "OSINT (Clément Molin, AMK Mapping). Un elemento = un post (o più post dello stesso canale sullo "
                 "stesso luogo e giorno). Coordinate del centro abitato (precisione_km 10), della regione (80) "
                 "o scritte nel post (1). affidabilita 'media' = segnalato da un analista e non corroborato; "
                 "'alta' = stesso evento (±1 giorno, entro 30 km) in attacchi-russi.json, ucraina-storico.json o "
                 "nell'altro canale. firms = focolaio NASA FIRMS entro 5 km e da -1 a +2 giorni (solo energia e "
                 "raffinerie/depositi; null = nessun dato FIRMS per quelle date). L'estrazione è automatica: "
                 "precisione stimata a mano nel rapporto report/agenti/attacchi-analisti.md. Il testo dei post non "
                 "è incluso: solo un estratto e il link."),
        "canali": info_canali,
        "categorie": sorted({c for c, _ in CATEGORIE} | {"altro"}),
        "elementi": elementi,
        "riepilogo": rie,
        "errori": ERRORI,
    }
    with open(USCITA, "w", encoding="utf-8") as h:
        json.dump(out, h, ensure_ascii=False, separators=(",", ":"))
    print("scritto %s: %d attacchi, %.2f MB" % (USCITA, len(elementi), os.path.getsize(USCITA) / 1e6))
    return out


def campione(n=40, seme=20261110):
    with open(USCITA, encoding="utf-8") as h:
        el = json.load(h)["elementi"]
    random.seed(seme)
    cache = {c["canale"]: carica_cache(c["canale"])["posts"] for c in CANALI}
    for e in random.sample(el, min(n, len(el))):
        p = cache[e["canale"]][int(e["link"].rsplit("/", 1)[1])]
        print("=" * 100)
        print(e["id"], "|", e["direzione"], "|", e["nome"], e["paese"], "|", e["categoria"], "|", e["mezzi"])
        print(re.sub(r"\s+", " ", p["testo"])[:700])


def main():
    passi = sys.argv[1:] or ["scarica", "gazetteer", "estrai"]
    if "scarica" in passi:
        for c in CANALI:
            print("Telegram @%s" % c["canale"])
            scarica_canale(c["canale"])
    if "gazetteer" in passi and (not os.path.exists(GAZ) or "gazetteer" in sys.argv[1:]):
        costruisci_gazetteer()
    if "estrai" in passi:
        estrai_tutto(senza_firms="--senza-firms" in passi)
    if "campione" in passi:
        campione()


if __name__ == "__main__":
    main()
