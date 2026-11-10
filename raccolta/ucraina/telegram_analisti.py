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
                elif fclass == "P" and pop >= soglia[paese] and fcode not in ("PPLH", "PPLQ", "PPLW"):
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
                   "nota": "UA: luoghi abitati >=1.000 abitanti; RU: >=15.000; ADM1 = oblast/regioni "
                   "(coordinate del punto GeoNames della regione)",
                   "voci": voci}, h, ensure_ascii=False, separators=(",", ":"))
    print("  gazetteer: %d voci" % len(voci))


# Nomi alternativi/inglesi/francesi delle regioni come li scrivono gli analisti -> nome GeoNames ADM1
OBLAST_ALIAS = {
    # Ucraina
    "kyiv oblast": "Kyiv", "kiev oblast": "Kyiv", "kharkiv oblast": "Kharkiv", "odesa oblast": "Odessa",
    "odessa oblast": "Odessa", "dnipropetrovsk": "Dnipropetrovsk", "dnipro oblast": "Dnipropetrovsk",
    "zaporizhzhia oblast": "Zaporizhia", "zaporijia": "Zaporizhia", "zaporizhia oblast": "Zaporizhia",
    "kherson oblast": "Kherson", "mykolaiv oblast": "Mykolaiv", "sumy oblast": "Sumy",
    "chernihiv oblast": "Chernihiv", "poltava oblast": "Poltava", "donetsk oblast": "Donetsk",
    "luhansk oblast": "Luhansk", "lviv oblast": "Lviv", "volyn": "Volyn", "rivne oblast": "Rivne",
    "khmelnytskyi oblast": "Khmelnytskyi", "vinnytsia oblast": "Vinnyts'ka", "zhytomyr oblast": "Zhytomyr",
    "cherkasy oblast": "Cherkasy", "kirovohrad": "Kirovohrad", "ivano-frankivsk oblast": "Ivano-Frankivsk",
    "ternopil oblast": "Ternopil", "chernivtsi oblast": "Chernivtsi", "zakarpattia": "Zakarpattia",
    "crimea": "Crimea", "crimée": "Crimea",
    # Russia
    "belgorod oblast": "Belgorod", "kursk oblast": "Kursk", "bryansk oblast": "Bryansk",
    "voronezh oblast": "Voronezh", "rostov oblast": "Rostov", "krasnodar krai": "Krasnodar",
    "krasnodar": "Krasnodar", "kuban": "Krasnodar", "oryol oblast": "Orel", "orel oblast": "Orel",
    "tula oblast": "Tula", "ryazan oblast": "Ryazan", "moscow oblast": "Moscow Oblast",
    "leningrad oblast": "Leningrad", "samara oblast": "Samara", "saratov oblast": "Saratov",
    "volgograd oblast": "Volgograd", "tambov oblast": "Tambov", "lipetsk oblast": "Lipetsk",
    "kaluga oblast": "Kaluga", "smolensk oblast": "Smolensk", "tver oblast": "Tver",
    "yaroslavl oblast": "Jaroslavl", "nizhny novgorod oblast": "Nizhny Novgorod",
    "bashkortostan": "Bashkortostan", "tatarstan": "Tatarstan", "chuvashia": "Chuvashia",
    "penza oblast": "Penza", "astrakhan oblast": "Astrakhan", "stavropol krai": "Stavropol Kray",
    "dagestan": "Dagestan", "chechnya": "Chechnya", "novgorod oblast": "Novgorod",
    "pskov oblast": "Pskov", "kaliningrad oblast": "Kaliningrad", "mordovia": "Mordoviya",
    "ulyanovsk oblast": "Ulyanovsk", "orenburg oblast": "Orenburg", "perm krai": "Perm",
    "udmurtia": "Udmurtiya", "vladimir oblast": "Vladimir", "ivanovo oblast": "Ivanovo",
    "kostroma oblast": "Kostroma", "vologda oblast": "Vologda", "murmansk oblast": "Murmansk",
    "adygea": "Adygeya", "kalmykia": "Kalmykiya",
}

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
    "ust-luga": "Ust-Luga", "primorsk": "Primorsk", "volgograd": "Volgograd", "saratov": "Saratov",
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
    "march", "may", "august", "trump", "putin", "ukraina", "nato", "europe", "american", "france",
}


def carica_gazetteer():
    with open(GAZ, encoding="utf-8") as h:
        g = json.load(h)
    idx = {}  # nome minuscolo -> voce (la più popolosa)
    obl = {}  # nome oblast -> voce ADM1
    for v in g["voci"]:
        if v["tipo"] == "oblast":
            obl[v["oblast"].lower()] = v
            obl[v["n"].lower()] = v
        nomi = [v["n"]] + v.get("alt", [])
        for n in nomi:
            k = n.lower().strip()
            if len(k) < 4 or k in STOP_LUOGHI:
                continue
            if v["tipo"] == "oblast" and n not in (v["n"],):
                continue
            prec = idx.get(k)
            if prec is None or (v["tipo"] == "citta" and (prec["tipo"] == "oblast" or v["pop"] > prec["pop"])):
                idx[k] = v
    # città dichiarate negli alias
    perno = {}
    for v in g["voci"]:
        if v["tipo"] == "citta":
            k = v["n"].lower()
            if k not in perno or v["pop"] > perno[k]["pop"]:
                perno[k] = v
    for a, n in CITTA_ALIAS.items():
        if n and n.lower() in perno:
            idx[a] = perno[n.lower()]
        elif n is None:
            idx.pop(a, None)
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
    ("artiglieria/MLRS", r"artillery|artillerie|himars|\bmlrs\b|grad\b|tornado-s|uragan"),
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
                 r"radar|air defen[cs]e|s-400|s-300|pantsir|buk\b|tor-m|warehouse|barracks|military|militaire|"
                 r"positions?\b|brigade|regiment|logistic|tank\b|tanks\b|armou?red|launcher|lanceur"),
    ("industria", r"plant\b|factory|usine|industrial|industriel|enterprise|chemical|chimique|"
                  r"metallurg|steel|aciérie|azot|fertili[sz]er|defen[cs]e industry|electronics|"
                  r"shipyard|chantier naval"),
    ("civile", r"civilian|civil|residential|apartment|building|immeuble|hospital|hôpital|school|école|"
               r"\bkilled\b|\binjured\b|\btués?\b|\bblessés?\b|\bmorts?\b|house|maison|market|shopping"),
]
ATTACCO = re.compile(
    r"\bstrikes?\b|\bstruck\b|\bhit\b|\bhits\b|\battack(?:s|ed)?\b|\bdrones?\b|\bmissiles?\b|shahed|geran|"
    r"iskander|kh-?101|kalibr|\bkabs?\b|refiner|oil depot|substation|explosion|\bfires?\b|\bblaze\b|burning|"
    r"\bfrappes?\b|\bfrappé|\bbombard|raffinerie|d[ée]p[ôo]t|incendie|touch[ée]|\bvisé|"
    r"\bdestroyed\b|\bdétrui", re.I)
# temi che non sono attacchi a lungo raggio (guerra di terra, mappe del fronte, politica)
NON_ATTACCO = re.compile(
    r"\badvance[sd]?\b|\bprogression\b|\bavanc[ée]|captured|\bcapture\b|liberat|libér|front ?line|"
    r"ligne de front|assault|assaut|counteroffensive|contre-offensive|\bgains?\b|frontline map|"
    r"geolocated (?:footage|video) (?:shows|of) (?:russian|ukrainian) (?:troops|soldiers|forces)|"
    r"\bentered\b|seized|took control|pris le contrôle", re.I)
VERBI_FORTI = re.compile(
    r"\bstrikes?\b|\bstruck\b|\bhit\b|\bhits\b|\battack(?:s|ed)?\b|\bfrapp|\bbombard|\btarget(?:s|ed)?\b|"
    r"\bvis[ée]|\btouch[ée]|explosions?|\bfires?\b|\bincendie|\bburning\b|\bdestroyed\b|\bdétrui|\bdamaged?\b|"
    r"\bendommag|\bshot down|\binterc|\blaunch(?:ed)?\b", re.I)
DIR_UA = re.compile(
    r"ukrainian (?:long[- ]range |kamikaze |attack )?(?:drones?|forces|strikes?|missiles?|uavs?|sbu|gur|navy)|"
    r"\bsbu\b|\bgur\b|\bhur\b|ukraine (?:struck|strikes|hit|attacked|targeted)|drones? ukrainiens?|"
    r"frappes? ukrainiennes?|missiles? ukrainiens?|l'ukraine a (?:frappé|touché|visé)|"
    r"flamingo|neptune|lyuty|liutyi|storm shadow|scalp|atacms|himars|\bfp-1\b|\bfp-5\b|"
    r"in russia\b|en russie\b|deep strike|frappe en profondeur", re.I)
DIR_RU = re.compile(
    r"russian (?:forces |army |)(?:strikes?|missiles?|drones?|attack|shaheds?|bombs?|kabs?|geran)|"
    r"russia (?:struck|strikes|hit|attacked|launched|targeted)|shahed|geran|iskander|kh-?101|kalibr|"
    r"kinzhal|\bkabs?\b|glide bomb|frappes? russes?|drones? russes|missiles? russes|la russie a (?:frappé|lancé|visé)|"
    r"in ukraine\b|en ukraine\b|ukrenergo|naftogaz|dtek|ukrzaliznytsia", re.I)
COORD = re.compile(r"(?<![\d.])([45]\d\.\d{3,6})\s*[,;/ ]\s*([2-9]\d\.\d{3,6}|1[0-4]\d\.\d{3,6})(?![\d.])")
PAROLA = re.compile(r"[A-Za-zÀ-ÿ'\-]+(?:[ \-][A-Za-zÀ-ÿ'\-]+){0,2}")


def trova_luoghi(testo, idx, obl):
    """Ritorna lista di (voce, tipo, posizione) trovati nel testo."""
    t = testo
    tl = t.lower()
    trovati = []
    # oblast esplicite ("X Oblast", "X oblast", "oblast de X", "X Krai", "region of X")
    for alias, nome in OBLAST_ALIAS.items():
        for m in re.finditer(r"(?<![a-zà-ÿ])" + re.escape(alias) + r"(?![a-zà-ÿ])", tl):
            v = obl.get(nome.lower())
            if v:
                trovati.append((v, "oblast", m.start()))
    for m in re.finditer(r"\b([A-Z][a-zà-ÿ'\-]+(?:[ \-][A-Z][a-zà-ÿ'\-]+)?) (?:oblast|Oblast|region|Region|Krai|krai)\b", t):
        v = obl.get(m.group(1).lower())
        if v:
            trovati.append((v, "oblast", m.start()))
    for m in re.finditer(r"(?:oblast|région|region) (?:de |d'|of )([A-Z][a-zà-ÿ'\-]+)", t):
        v = obl.get(m.group(1).lower())
        if v:
            trovati.append((v, "oblast", m.start()))
    # città: parole con iniziale maiuscola (1–3 parole), lunghezza >= 4
    for m in re.finditer(r"\b[A-ZÀ-Ý][A-Za-zÀ-ÿ'\-]+(?:[ \-](?:na|on|de|nad|Don|[A-ZÀ-Ý][A-Za-zÀ-ÿ'\-]+)){0,2}", t):
        frase = m.group(0)
        parti = frase.split(" ")
        # prova la sequenza più lunga poi le più corte
        for n in range(len(parti), 0, -1):
            k = " ".join(parti[:n]).lower().strip("'-")
            if k.endswith("'s"):
                k = k[:-2]
            v = idx.get(k)
            if v and v["tipo"] == "citta":
                seg = tl[m.end(): m.end() + 8]
                if " oblast" in seg or " region" in seg or " krai" in seg:
                    break  # è l'oblast, già presa sopra
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
    ordine = [c for _, c in CATEGORIE]
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


def estrai_attacco(post, idx, obl):
    t = post["testo"]
    if not t or len(t) < 25:
        return None, "testo vuoto o troppo corto"
    if not ATTACCO.search(t):
        return None, "nessuna parola chiave d'attacco"
    if not VERBI_FORTI.search(t):
        return None, "nessun verbo d'attacco"
    nf = len(NON_ATTACCO.findall(t))
    na = len(ATTACCO.findall(t))
    if nf and nf >= na:
        return None, "post sul fronte terrestre"
    luoghi = trova_luoghi(t, idx, obl)
    coord = None
    m = COORD.search(t)
    if m:
        la, lo = float(m.group(1)), float(m.group(2))
        if 43 <= la <= 70 and 20 <= lo <= 140:
            coord = (la, lo)
    if not luoghi and not coord:
        return None, "nessun luogo riconosciuto"
    # scelta del luogo: prima città menzionata vicino al primo verbo d'attacco; altrimenti prima oblast
    vpos = VERBI_FORTI.search(t).start()
    citta = [x for x in luoghi if x[1] == "citta" and x[0].get("paese") in ("UA", "RU", "")]
    oblasti = [x for x in luoghi if x[1] == "oblast"]
    scelto = None
    if citta:
        scelto = min(citta, key=lambda x: abs(x[2] - vpos))
    elif oblasti:
        scelto = min(oblasti, key=lambda x: abs(x[2] - vpos))
    if scelto:
        v, tipo, _ = scelto
        paese = v.get("paese") or ""
        if not paese:  # città di labels.json: paese dalla città GeoNames omonima se c'è
            w = idx.get(v["n"].lower())
            paese = w.get("paese", "") if w else ""
    else:
        v, tipo, paese = None, None, ""
    if coord:
        lat, lon, prec, orig = coord[0], coord[1], 1, "coordinate scritte nel post"
        if not paese:
            paese = "RU" if lon > 40.3 or lat > 52.4 else ""
    elif v:
        lat, lon = v["lat"], v["lon"]
        prec = 10 if tipo == "citta" else 80
        orig = "GeoNames: %s (%s)" % (v["n"], "centro abitato" if tipo == "citta" else "regione")
    if paese not in ("UA", "RU"):
        if not paese and lat and lon:
            paese = "RU" if lon > 40.3 or lat > 52.4 else "UA"
        else:
            return None, "luogo fuori da Ucraina/Russia"
    occupato = paese == "UA" and v is not None and oblast_ua_occupato(v)
    d = direzione(t, paese, occupato)
    if d is None:
        return None, "direzione non determinata"
    cat = classifica(t)
    return {
        "post": post,
        "lat": round(lat, 4), "lon": round(lon, 4), "precisione_km": prec, "origine_coord": orig,
        "luogo": v["n"] if v else "coordinate del post",
        "oblast": (v.get("oblast") if v else "") or "",
        "paese": paese, "occupato": occupato,
        "direzione": d, "categoria": cat, "mezzi": mezzi(t),
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
    for p in posts:
        a, mot = estrai_attacco(p, idx, obl)
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
            "categoria": a["categoria"], "mezzi": a["mezzi"],
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
