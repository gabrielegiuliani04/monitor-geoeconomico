#!/usr/bin/env python3
"""Raccoglitore quotidiano di notizie OSINT (materia prima per il coordinatore).

Legge raccolta/notizie/fonti.json (feed RSS/Atom, ricerche Google News RSS per le
fonti bloccate, anteprime pubbliche di canali Telegram, Thread Reader, pagina
comunicati della Banca d'Italia), normalizza ogni notizia (titolo, data UTC, link,
fonte, famiglia, sommario breve <= 400 caratteri), deduplica, raggruppa le notizie
sulla stessa storia, tiene gli ultimi 7 giorni (unendo il file precedente), classifica
per tema con parole chiave e per luogo (toponimi di docs/data/labels.json, con
coordinate approssimate e precisione dichiarata) e segnala i possibili eventi nuovi.

Produce: docs/data/notizie.json
Uso:     python3 raccolta/notizie/raccogli.py   (dalla radice del repository)
Solo libreria standard. Nessuna chiave richiesta.

Non copia gli articoli: tiene solo titolo, un sommario breve e il link.
Tutte le notizie sono "da verificare" finche' il coordinatore non le incrocia.
"""
import concurrent.futures as cf
import hashlib
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.abspath(os.path.join(QUI, "..", ".."))
FONTI = os.path.join(QUI, "fonti.json")
LABELS = os.path.join(RADICE, "docs", "data", "labels.json")
PAESI = os.path.join(RADICE, "docs", "data", "paesi.json")
OUT = os.path.join(RADICE, "docs", "data", "notizie.json")

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124 Safari/537.36 monitor-geoeconomico-OSINT",
      "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, text/html;q=0.9, */*;q=0.8"}
GIORNI = 7               # finestra tenuta nel file
MAX_PER_FONTE = 60       # notizie massime per fonte a ogni giro
MAX_SOMMARIO = 400
SOGLIA_GRUPPO = 0.4      # Jaccard tra titoli per dire "stessa storia"
ORA = datetime.now(timezone.utc)

# ---------------------------------------------------------------- temi
# Parole in minuscolo: confronto senza maiuscole. Parole tutte in MAIUSCOLO: confronto esatto (sigle).
TEMI = {
 "hormuz": ["hormuz", "ormuz", "strait of hormuz", "kharg", "bandar abbas", "qeshm", "gulf of oman",
            "golfo di oman", "fujairah", "khorfakkan", "persian gulf", "arabian gulf", "golfo persico",
            "larak", "jask", "abu musa", "ras tanura"],
 "mar_rosso_houthi": ["red sea", "mar rosso", "houthi", "houthis", "huthi", "ansar allah", "bab el-mandeb",
                      "bab al-mandab", "bab-el-mandeb", "hodeidah", "hodeida", "gulf of aden", "golfo di aden",
                      "yemen", "yemeni", "eilat"],
 "ucraina_fronte": ["frontline", "front line", "front-line", "russian offensive", "summer offensive",
                    "winter offensive", "counteroffensive", "pokrovsk",
                    "kostiantynivka", "kostyantynivka", "myrnohrad", "huliaipole", "hulyaipole", "kupiansk",
                    "kupyansk", "siversk", "lyman", "zaporizhzhia oblast", "donetsk oblast", "kharkiv oblast",
                    "sumy oblast", "dnipropetrovsk oblast", "luhansk oblast", "kherson oblast", "advanced near",
                    "advance near", "general staff",
                    "russian offensive campaign assessment", "battlefield", "фронт", "просунувся", "наступ",
                    "мапу оновлено", "front ukrainien", "ligne de front"],
 "guerra_iran": ["iran", "iranian", "irgc", "tehran", "teheran", "israel", "israeli", "idf", "hezbollah",
                 "isfahan", "natanz", "fordow", "iran update", "ceasefire with iran"],
 "attacchi_energia": ["refinery", "refineries", "raffineria", "raffinerie", "oil depot", "fuel depot",
                      "oil terminal", "pumping station", "power plant", "substation", "thermal power",
                      "energy infrastructure", "gas facility", "нпз", "raffinerie", "sous-station",
                      "infrastructure énergétique", "енергетик"],
 "droni_missili": ["drone", "drones", "uav", "uavs", "shahed", "geran", "missile", "missiles", "ballistic",
                   "cruise missile", "air defense", "air defence", "patriot", "дрон", "дрони", "бпла",
                   "ракет", "droni", "missili", "missiles"],
 "cavi_sottomarini": ["undersea cable", "subsea cable", "submarine cable", "cable cut", "cable damage",
                      "data cable", "cavo sottomarino", "cavi sottomarini", "anchor drag", "dragged anchor",
                      "seabed infrastructure"],
 "sabotaggi_ibrido": ["sabotage", "saboteur", "saboteurs", "sabotaggio", "arson", "hybrid attack",
                      "hybrid warfare", "hybrid threat", "gps jamming", "jamming", "spoofing", "gnss",
                      "airspace violation", "drone sighting", "drone sightings", "cyberattack",
                      "cyber attack", "hackers", "hacker", "espionage", "spy", "spies"],
 "flotta_ombra_sanzioni": ["shadow fleet", "dark fleet", "flotta ombra", "sanction", "sanctions",
                           "sanctioned", "sanzioni", "OFAC", "price cap", "blacklist", "designated vessels"],
 "gnl_gas": ["lng", "gnl", "liquefied natural gas", "natural gas", "gas prices", "ttf", "regasification",
             "gas storage", "gas pipeline", "pipeline gas", "gasdotto", "henry hub"],
 "petrolio": ["oil", "crude", "brent", "wti", "opec", "opec+", "barrel", "barrels", "petrolio", "greggio",
              "tanker", "tankers", "vlcc", "bpd", "oil output", "oil exports"],
 "banche_centrali": ["Fed", "federal reserve", "FOMC", "ECB", "BCE", "bank of england", "monetary policy",
                     "interest rate", "interest rates", "rate cut", "rate hike", "bank rate", "lagarde",
                     "powell", "banca d'italia", "politica monetaria", "tassi", "inflation", "inflazione"],
 "sicurezza_marittima": ["UKMTO", "JMIC", "MARAD", "piracy", "pirates", "pirate", "hijack", "hijacked",
                         "boarded", "vessel attacked", "merchant vessel", "bulk carrier", "maritime security",
                         "maritime incident", "seafarer", "seafarers", "crew", "pirateria"],
 "nucleare": ["nuclear", "iaea", "uranium", "enrichment", "zaporizhzhia nuclear", "znpp", "nucleare",
              "chernobyl", "kursk npp", "aeo"],
 "logistica_noli": ["freight", "freight rates", "container", "containers", "shipping rates", "port",
                    "ports", "suez canal", "rerouting", "cape of good hope", "noli", "box rates",
                    "supply chain", "logistics", "dry bulk", "charter rates"],
 "elettricita_blackout": ["blackout", "blackouts", "power outage", "power outages", "outage",
                          "power grid", "electricity", "без світла", "відключення", "знеструм"],
 "diplomazia_negoziati": ["talks", "ceasefire", "negotiation", "negotiations", "peace deal", "truce",
                          "peace plan", "summit", "negoziati", "tregua", "witkoff", "kushner"],
}
TEMI_FORTI = {"hormuz", "mar_rosso_houthi", "attacchi_energia", "cavi_sottomarini", "sabotaggi_ibrido",
              "flotta_ombra_sanzioni", "sicurezza_marittima", "ucraina_fronte", "guerra_iran"}

# ---------------------------------------------------------------- possibili eventi
EVENTO = [  # (regex, categoria proposta per eventi.json / ibrido.json)
 (r"\battack(?:s|ed|ing)?\b|\bstrik(?:e|es|ing)\b|\bstruck\b|\bhit\b|\bhits\b|\bshell(?:ed|ing)\b|"
  r"\bbomb(?:ed|ing|ings)?\b|\bбомб\w*|\battacc\w*|\bcolpit\w*|\bfrapp\w*|\battaqu\w*|\bудар\w*|\bатак\w*|\bобстріл\w*",
  "attacco"),
 (r"\bseiz(?:e|ed|es|ure|ing)\b|\bhijack\w*|\bboarded\b|\bdetain(?:ed|s)?\b|\bsequestr\w*", "sequestro"),
 (r"\bexplosion\w*|\bexplod\w*|\bblast\w*|\bfire\b|\bfires\b|\bablaze\b|\bblaze\b|\besplosion\w*|"
  r"\bincendi\w*|\bвибух\w*|\bпожеж\w*", "esplosione-incendio"),
 (r"\bsabotag\w*|\barson\b", "sabotaggio"),
 (r"\bclos(?:e|ed|es|ure|ing)\b|\bshut(?:s|down)?\b|\bsuspend(?:s|ed)?\b|\bhalt(?:s|ed)?\b|\bchius\w*|"
  r"\bevacuation order\b", "chiusura"),
 (r"\bblackout\w*|\bpower outage\w*|\bpower cut\w*|\bзнеструм\w*|\bвідключ\w*", "blackout"),
 (r"\bshot down\b|\bdowned\b|\bintercept(?:ed|s|ion)\b|\bзбит\w*", "intercettazione"),
 (r"\badvanc(?:ed|es)\b|\bcaptur(?:ed|es)\b|\btook control\b|\bпросунув\w*|\bзахопи\w*|\bпросуван\w*",
  "avanzamento"),
 (r"\bsank\b|\bsunk\b|\bsinking\b|\bcollision\b|\bcollided\b|\bgrounded\b|\bincident\b", "incidente"),
 (r"\bjamming\b|\bspoofing\b|\bcyberattack\w*|\bcyber attack\w*|\bdrone sighting\w*", "ibrido"),
]
EVENTO = [(re.compile(p, re.I), c) for p, c in EVENTO]
# espressioni con verbi da evento che non sono eventi ("strikes a deal", "hit a record")
NON_EVENTO = re.compile(r"\bstrik(?:e|es|ing)\s+(?:\S+\s+){0,2}(?:deal|deals|agreement|accord|pact|balance|tone|chord)\b|"
                        r"\bhits?\s+(?:a\s+)?(?:record|high|low|peak|target|milestone)\w*|\bclose[sd]?\s+(?:higher|lower|up|down|at)\b|"
                        r"\bfire(?:s|d)?\s+(?:back|up)\b|\bceasefire\b", re.I)
# titoli che sembrano analisi, previsioni o rubriche: non eventi
SPECULATIVO = re.compile(
    r"\?|\b(could|may|might|would|warns?|risks?|explained|explainer|analysis|opinion|podcast|interview|"
    r"week in|daily view|outlook|forecast|assessment|update,|tracker|what|why|how|if|lessons|history|"
    r"review|editorial|comment|webinar|chart)\b", re.I)

# titoli di mercato ("prices hit", "markets closed"): non eventi
MERCATO = re.compile(r"\b(prices?|markets?|stocks?|shares|futures|rally|rallies|record high|bourse|equities|"
                     r"yields?|earnings|profit|revenue)\b", re.I)

# ---------------------------------------------------------------- luoghi
# Nomi inglesi (e qualche nome ucraino o francese) -> nome usato in labels.json.
ALIAS_PAESI = {
 "Stati Uniti": ["United States", "U.S.", "USA", "America"], "Regno Unito": ["United Kingdom", "UK", "Britain", "British"],
 "Sudafrica": ["South Africa"], "Arabia Saudita": ["Saudi Arabia", "Saudi"], "Russia": ["Russia", "Россия", "росія", "Russie"],
 "Giappone": ["Japan"], "India": ["India"], "Germania": ["Germany"], "Francia": ["France"], "Egitto": ["Egypt"],
 "Cina": ["China", "Chine"], "Canada": ["Canada"], "Brasile": ["Brazil"], "Australia": ["Australia"],
 "Groenlandia": ["Greenland"], "Vietnam": ["Vietnam"], "Turchia": ["Turkey", "Türkiye", "Turkiye"],
 "Spagna": ["Spain"], "Messico": ["Mexico"], "Italia": ["Italy", "Italie"], "Etiopia": ["Ethiopia"],
 "Argentina": ["Argentina"], "Svezia": ["Sweden"], "Islanda": ["Iceland"], "Corea del Sud": ["South Korea"],
 "Filippine": ["Philippines"], "Iran": ["Iran", "Іран"], "Venezuela": ["Venezuela"], "Sudan": ["Sudan"],
 "Polonia": ["Poland", "Польща"], "Algeria": ["Algeria"], "Pakistan": ["Pakistan"], "Ucraina": ["Ukraine", "Україна", "Україні"],
 "Grecia": ["Greece"], "Yemen": ["Yemen"], "Siria": ["Syria"], "Romania": ["Romania"], "Norvegia": ["Norway"],
 "Corea del Nord": ["North Korea"], "Libia": ["Libya"], "Irlanda": ["Ireland"], "Iraq": ["Iraq"],
 "Finlandia": ["Finland"], "Myanmar": ["Myanmar"], "Afghanistan": ["Afghanistan"], "Israele": ["Israel", "Israël"],
 "Danimarca": ["Denmark"], "Bielorussia": ["Belarus"], "Austria": ["Austria"], "Estonia": ["Estonia"],
 "Belgio": ["Belgium"], "Emirati Arabi Uniti": ["United Arab Emirates", "UAE", "Emirates"], "Svizzera": ["Switzerland"],
 "Panama": ["Panama"], "Oman": ["Oman"], "Giordania": ["Jordan"], "Eritrea": ["Eritrea"], "Bulgaria": ["Bulgaria"],
 "Bahrein": ["Bahrain"], "Serbia": ["Serbia"], "Qatar": ["Qatar"], "Paesi Bassi": ["Netherlands", "Dutch"],
 "Malta": ["Malta"], "Lituania": ["Lithuania"], "Libano": ["Lebanon"], "Lettonia": ["Latvia", "Латвія"],
 "Ungheria": ["Hungary"], "Georgia": ["Georgia"], "Gibuti": ["Djibouti"], "Cechia": ["Czech Republic", "Czechia"],
 "Azerbaigian": ["Azerbaijan"], "Somalia": ["Somalia"], "Slovacchia": ["Slovakia"], "Singapore": ["Singapore"],
 "Croazia": ["Croatia"], "Taiwan": ["Taiwan"], "Cipro": ["Cyprus"], "Moldavia": ["Moldova"], "Kuwait": ["Kuwait"],
 "Armenia": ["Armenia"], "Albania": ["Albania"], "Kazakistan": ["Kazakhstan"], "Portogallo": ["Portugal"],
 "Nigeria": ["Nigeria"], "Indonesia": ["Indonesia"], "Malaysia": ["Malaysia"], "Bangladesh": ["Bangladesh"],
 "Sri Lanka": ["Sri Lanka"], "Thailandia": ["Thailand"], "Cuba": ["Cuba"], "Colombia": ["Colombia"],
 "Tunisia": ["Tunisia"], "Marocco": ["Morocco"], "Kenya": ["Kenya"], "Mozambico": ["Mozambique"],
 "Nuova Zelanda": ["New Zealand"], "Cile": ["Chile"], "Perù": ["Peru"], "Ecuador": ["Ecuador"],
 "Sudan del Sud": ["South Sudan"], "Uzbekistan": ["Uzbekistan"], "Turkmenistan": ["Turkmenistan"],
 "Mongolia": ["Mongolia"], "Mali": ["Mali"], "Niger": ["Niger"], "Ciad": ["Chad"], "Burkina Faso": ["Burkina Faso"],
 "Slovenia": ["Slovenia"], "Montenegro": ["Montenegro"], "Bosnia-Erzegovina": ["Bosnia"], "Kosovo": ["Kosovo"],
 "Macedonia del Nord": ["North Macedonia"], "Lussemburgo": ["Luxembourg"], "Tagikistan": ["Tajikistan"],
 "Kirghizistan": ["Kyrgyzstan"], "Nepal": ["Nepal"], "Cambogia": ["Cambodia"], "Laos": ["Laos"],
 "RD Congo": ["DR Congo", "Democratic Republic of Congo", "DRC"], "Angola": ["Angola"], "Ghana": ["Ghana"],
 "Senegal": ["Senegal"], "Mauritania": ["Mauritania"], "Guinea Equatoriale": ["Equatorial Guinea"],
 "Papua Nuova Guinea": ["Papua New Guinea"], "Guyana": ["Guyana"], "Suriname": ["Suriname"],
}
ALIAS_CITTA = {
 "Kiev": ["Kyiv", "Kiev", "Київ", "Києві", "Києва"], "Leopoli": ["Lviv", "Львів"], "Odessa": ["Odesa", "Odessa", "Одеса", "Одесі"],
 "Kharkiv": ["Kharkiv", "Kharkov", "Харків"], "Dnipro": ["Dnipro", "Дніпро"], "Donetsk": ["Donetsk", "Донецьк"],
 "Sebastopoli": ["Sevastopol", "Севастополь"], "Rostov sul Don": ["Rostov-on-Don", "Rostov"],
 "Staryj Oskol": ["Stary Oskol"], "Lipeck": ["Lipetsk"], "Brjansk": ["Bryansk"], "Krasnojarsk": ["Krasnoyarsk"],
 "Ekaterinburg": ["Yekaterinburg"], "Kazan’": ["Kazan"], "Arcangelo": ["Arkhangelsk"], "Mosca": ["Moscow", "Москва", "Moscou"],
 "San Pietroburgo": ["St Petersburg", "St. Petersburg", "Saint Petersburg", "Saint-Pétersbourg"],
 "Novorossiysk": ["Novorossiysk", "Novorossiisk"], "Volgograd": ["Volgograd"], "Saratov": ["Saratov"],
 "Samara": ["Samara"], "Voronezh": ["Voronezh"], "Krasnodar": ["Krasnodar"], "Sochi": ["Sochi"],
 "Smolensk": ["Smolensk"], "Pskov": ["Pskov"], "Yaroslavl": ["Yaroslavl"], "Astrakhan": ["Astrakhan"],
 "Orenburg": ["Orenburg"], "Penza": ["Penza"], "Kaliningrad": ["Kaliningrad"], "Murmansk": ["Murmansk"],
 "Nizhny Novgorod": ["Nizhny Novgorod"], "Ufa": ["Ufa"], "Perm": ["Perm"], "Chelyabinsk": ["Chelyabinsk"],
 "Grozny": ["Grozny"], "Chisinau": ["Chisinau", "Chișinău"], "Bucarest": ["Bucharest"], "Varsavia": ["Warsaw"],
 "Teheran": ["Tehran"], "Riad": ["Riyadh"], "La Mecca": ["Mecca"], "Gerusalemme": ["Jerusalem"], "Gedda": ["Jeddah"],
 "Sana'a": ["Sanaa", "Sana'a", "Sana’a"], "Damasco": ["Damascus"], "Mascate": ["Muscat"], "Bassora": ["Basra"],
 "Hodeida": ["Hodeidah", "Hodeida", "Hudaydah"], "Sidone": ["Sidon"], "Nassiriya": ["Nasiriyah"],
 "Sulaymaniyya": ["Sulaymaniyah"], "Massaua": ["Massawa"], "Ta'izz": ["Taiz"], "Sa'da": ["Saada", "Sadah"],
 "Nazaret": ["Nazareth"], "Il Cairo": ["Cairo"], "Porto Said": ["Port Said"], "Alessandria": ["Alexandria"],
 "Mogadiscio": ["Mogadishu"], "Chisimaio": ["Kismayo"], "Khartum": ["Khartoum"], "Al-Fashir": ["El Fasher", "al-Fashir"],
 "Bengasi": ["Benghazi"], "Misurata": ["Misrata"], "Tunisi": ["Tunis"], "Algeri": ["Algiers"],
 "Pechino": ["Beijing"], "Seul": ["Seoul"], "Nuova Delhi": ["New Delhi"], "Canton": ["Guangzhou"],
 "Tientsin": ["Tianjin"], "Tsingtao": ["Qingdao"], "Nanchino": ["Nanjing"], "Londra": ["London"],
 "Parigi": ["Paris"], "Berlino": ["Berlin"], "Roma": ["Rome"], "Milano": ["Milan"], "Napoli": ["Naples"],
 "Torino": ["Turin"], "Genova": ["Genoa"], "Venezia": ["Venice"], "Firenze": ["Florence"], "Siracusa": ["Syracuse"],
 "Lisbona": ["Lisbon"], "Barcellona": ["Barcelona"], "Siviglia": ["Seville"], "Bruxelles": ["Brussels"],
 "Copenaghen": ["Copenhagen"], "Stoccolma": ["Stockholm"], "Dublino": ["Dublin"], "Praga": ["Prague"],
 "Belgrado": ["Belgrade"], "Zagabria": ["Zagreb"], "Atene": ["Athens"], "Pireo": ["Piraeus"], "Salonicco": ["Thessaloniki"],
 "Alessandropoli": ["Alexandroupoli", "Alexandroupolis"], "Danzica": ["Gdansk", "Gdańsk"], "Cracovia": ["Krakow", "Kraków"],
 "Amburgo": ["Hamburg"], "Francoforte": ["Frankfurt"], "Monaco di Baviera": ["Munich"], "Colonia": ["Cologne"],
 "Dresda": ["Dresden"], "Ginevra": ["Geneva"], "Zurigo": ["Zurich"], "Lione": ["Lyon"], "Marsiglia": ["Marseille"],
 "Edimburgo": ["Edinburgh"], "Smirne": ["Izmir"], "Famagosta": ["Famagusta"], "Erevan": ["Yerevan"],
 "Città del Capo": ["Cape Town"], "Città del Messico": ["Mexico City"], "L'Avana": ["Havana"],
 "La Valletta": ["Valletta"], "Gibuti": ["Djibouti City"], "Giacarta": ["Jakarta"], "Dacca": ["Dhaka"],
 "Katmandu": ["Kathmandu"], "Addis Abeba": ["Addis Ababa"], "Filadelfia": ["Philadelphia"],
 "Kaliningrad (Russia)": [],
}
ALIAS_STRETTI = {
 "Stretto di Hormuz": ["Strait of Hormuz", "Hormuz Strait", "Hormuz", "Ormuz", "Stretto di Hormuz"],
 "Bab el-Mandeb": ["Bab el-Mandeb", "Bab al-Mandab", "Bab-el-Mandeb", "Bab el Mandeb"],
 "Canale di Suez": ["Suez Canal", "Canale di Suez"], "Bosforo": ["Bosphorus", "Bosporus", "Bosforo"],
 "Dardanelli": ["Dardanelles"], "Stretto di Tiran": ["Strait of Tiran", "Tiran Strait"],
 "Stretto di Gibilterra": ["Strait of Gibraltar"], "Stretto di Malacca": ["Strait of Malacca", "Malacca Strait"],
 "Canale di Panama": ["Panama Canal"], "Stretto di Taiwan": ["Taiwan Strait"],
 "Stretti danesi": ["Danish straits", "Great Belt", "Oresund", "Øresund", "Skagerrak", "Kattegat"],
 "Capo di Buona Speranza": ["Cape of Good Hope"], "Canale di Sicilia": ["Strait of Sicily", "Sicily Channel"],
 "Stretto di Luzon": ["Luzon Strait", "Bashi Channel"], "Stretto di Bering": ["Bering Strait"],
 "Stretto di Kerch": ["Kerch Strait", "Strait of Kerch", "Kerch", "Crimean Bridge", "Керч"],
}
ALIAS_REGIONI = {
 "Sinai": ["Sinai"], "Cisgiordania": ["West Bank"], "Striscia di Gaza": ["Gaza Strip", "Gaza"],
 "Alture del Golan": ["Golan Heights", "Golan"], "Somaliland": ["Somaliland"], "Crimea": ["Crimea", "Крим", "Криму", "Crimée"],
 "Kashmir": ["Kashmir"], "Kurdistan iracheno": ["Iraqi Kurdistan", "Kurdistan Region"], "Darfur": ["Darfur"],
 "Donbass": ["Donbas", "Donbass", "Донбас"], "Sahara Occidentale": ["Western Sahara"],
 "Balucistan": ["Balochistan", "Baluchistan"], "Kaliningrad (Russia)": [], "Abcasia": ["Abkhazia"],
 "Ossezia del Sud": ["South Ossetia"], "Transnistria": ["Transnistria"], "Diego Garcia": ["Diego Garcia"],
 "Socotra": ["Socotra"], "Creta": ["Crete"], "Sicilia": ["Sicily"], "Sardegna": ["Sardinia"],
 "Qeshm": ["Qeshm"], "Kharg": ["Kharg Island", "Kharg"], "Abu Musa": ["Abu Musa"], "Masirah": ["Masirah"],
}
ALIAS_MARI = {
 "Mar Rosso": ["Red Sea"], "Mar Nero": ["Black Sea"], "Mar Baltico": ["Baltic Sea", "Baltic"],
 "Golfo Persico": ["Persian Gulf", "Arabian Gulf"], "Golfo di Oman": ["Gulf of Oman"], "Golfo di Aden": ["Gulf of Aden"],
 "Mar Arabico": ["Arabian Sea"], "Mar Cinese Meridionale": ["South China Sea"], "Mar Cinese Orientale": ["East China Sea"],
 "Mar Mediterraneo": ["Mediterranean"], "Mare del Nord": ["North Sea"], "Mar Caspio": ["Caspian Sea", "Caspian"],
 "Mar d'Azov": ["Sea of Azov", "Azov Sea"], "Mar Egeo": ["Aegean"], "Mar Adriatico": ["Adriatic"],
 "Mar Ionio": ["Ionian Sea"], "Mar Tirreno": ["Tyrrhenian"], "Mare di Barents": ["Barents Sea"],
 "Mare di Norvegia": ["Norwegian Sea"], "Mar dei Caraibi": ["Caribbean"], "Golfo del Messico": ["Gulf of Mexico", "Gulf of America"],
 "Golfo di Guinea": ["Gulf of Guinea"], "Golfo del Bengala": ["Bay of Bengal"], "Mar del Giappone": ["Sea of Japan"],
 "Mar Giallo": ["Yellow Sea"], "Mare delle Filippine": ["Philippine Sea"], "Canale della Manica": ["English Channel"],
 "Golfo di Suez": ["Gulf of Suez"], "Golfo di Aqaba": ["Gulf of Aqaba"], "Golfo della Sirte": ["Gulf of Sidra", "Gulf of Sirte"],
 "Mar Glaciale Artico": ["Arctic Ocean"], "Canale di Mozambico": ["Mozambique Channel"], "Mare delle Andamane": ["Andaman Sea"],
 "Mar di Marmara": ["Sea of Marmara"], "Mar di Levante": ["Eastern Mediterranean"], "Mare di Okhotsk": ["Sea of Okhotsk"],
}
# Citta' di labels.json che sono anche parole comuni o nomi di persona: non usate da sole.
CITTA_ESCLUSE = {"Mary", "Victoria", "Van", "Eil", "Hon", "Gat", "Brach", "Sur", "Bam", "Duma", "Hail", "Male", "Kaka",
                 "Mus", "Agri", "Saki", "Oguz", "Hilf", "Jackson", "Columbus", "Charlotte", "Phoenix", "Buffalo",
                 "Salvador", "Santa Fe", "Hamilton", "Richmond", "Charleston", "Wilmington", "Albany", "Portland",
                 "Georgetown", "Regina", "Helena", "Pierre", "Eureka", "Nain", "Churchill", "Stanley", "Darwin",
                 "Kingston", "Orlando", "Austin", "Fargo", "Nancy", "Porto", "Nome", "Como", "Ica", "Obo", "Resolute",
                 "Valdez", "Prince George", "Monaco", "Concepción", "Lugh", "Merca", "Garoe", "Alula", "Zillah",
                 "Kerma", "Gao", "Hilo", "Houma", "Sparta", "Kos", "Chio", "Saint Louis", "Birmingham", "Newcastle",
                 "Durban", "Medina", "Tripoli", "Valencia", "Hyderabad", "San Jose", "San José", "Mendoza",
                 "Córdoba", "Santa Cruz de la Sierra", "Nizza", "Batman", "Panama", "Gibuti", "Suez",
                 "Gaza", "Kaliningrad", "Gibilterra", "Bursa", "Sale", "Siena", "Ordu", "Asti", "Bari", "Cali",
                 "Lima", "Washington", "Mardin", "Paphos", "Ma'an", "Qalat", "El Qasr", "Dirj", "Gardo", "Hordio", "Ferfer"}
CITTA_RICHIESTE = set()  # alias che restano citta' anche se coincidono con un alias di paese
PRECISIONE = {"citta": 15, "stretto": 50, "regione": 100, "mare": 300, "paese": 500}
ORDINE = {"citta": 0, "stretto": 1, "regione": 2, "mare": 3, "paese": 4}


def carica_luoghi():
    """Costruisce la tabella alias -> luogo (nome, tipo, lat, lon, paese ISO2)."""
    lab = json.load(open(LABELS, encoding="utf-8"))
    iso3_2 = {}
    try:
        for p in json.load(open(PAESI, encoding="utf-8")).get("elementi", []):
            if p.get("iso3") and p.get("paese"):
                iso3_2[p["iso3"]] = p["paese"]
    except Exception:
        pass
    luoghi = {}  # alias -> dict
    avvisi = []

    def aggiungi(alias, nome, tipo, x, y, iso2=""):
        alias = alias.strip()
        if len(alias) < 3 and alias not in ("UK",):
            return
        prec = luoghi.get(alias)
        if prec and ORDINE[prec["tipo"]] <= ORDINE[tipo]:
            return
        luoghi[alias] = {"nome": nome, "tipo": tipo, "lat": round(y, 3), "lon": round(x, 3), "paese": iso2}

    def primo(lista, nome):
        for e in lista:
            if e["n"] == nome:
                return e
        return None

    for c in lab["countries"]:
        iso2 = iso3_2.get(c.get("id", ""), "")
        for a in ALIAS_PAESI.get(c["n"], []) + [c["n"]]:
            aggiungi(a, c["n"], "paese", c["x"], c["y"], iso2)
    for nome, alias in ALIAS_MARI.items():
        e = primo(lab["seas"], nome)
        if not e:
            avvisi.append(f"mare non in labels.json: {nome}")
            continue
        for a in alias + [nome]:
            aggiungi(a, nome, "mare", e["x"], e["y"])
    for e in lab["regions"]:
        for a in ALIAS_REGIONI.get(e["n"], []) + [e["n"]]:
            aggiungi(a, e["n"], "regione", e["x"], e["y"])
    for e in lab["straits"]:
        for a in ALIAS_STRETTI.get(e["n"], []) + [e["n"]]:
            aggiungi(a, e["n"], "stretto", e["x"], e["y"])
    visti = set()
    for e in lab["cities"]:
        if e["n"] in visti:          # nomi doppi (es. Tripoli): si tiene il primo, piu' popoloso
            continue
        visti.add(e["n"])
        alias = list(ALIAS_CITTA.get(e["n"], []))
        if e["n"] not in CITTA_ESCLUSE:
            alias.append(e["n"])
        for a in alias:
            if a in luoghi and luoghi[a]["tipo"] == "paese" and a not in CITTA_RICHIESTE:
                continue
            aggiungi(a, e["n"], "citta", e["x"], e["y"])
    for nome in ALIAS_CITTA:
        if nome not in visti and nome not in ("Kaliningrad (Russia)",):
            avvisi.append(f"citta' non in labels.json: {nome}")
    # una sola espressione regolare, alias piu' lunghi prima
    chiavi = sorted(luoghi, key=len, reverse=True)
    rx = re.compile(r"(?<![\w’'])(" + "|".join(re.escape(k) for k in chiavi) + r")(?![\w])")
    return luoghi, rx, avvisi


# ---------------------------------------------------------------- utilita
def scarica(url, timeout=25, tentativi=2):
    ultimo = None
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            ultimo = e
            if e.code in (403, 404, 410):
                break
        except Exception as e:  # rete, timeout
            ultimo = e
        time.sleep(2 + 3 * i)
    raise ultimo


def senza_simboli(t):
    """Toglie emoji, bandiere e simboli grafici (frequenti su Telegram)."""
    return "".join(c for c in t if unicodedata.category(c) not in ("So", "Cs", "Co")
                   and c not in "\ufe0f\ufe0e\u200d\u20e3")


def pulisci(testo):
    if not testo:
        return ""
    t = html.unescape(testo)
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</p>|</div>|</li>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = senza_simboli(html.unescape(t))
    return re.sub(r"\s+", " ", t).strip()


def taglia(t, n=MAX_SOMMARIO):
    t = t.strip()
    if len(t) <= n:
        return t
    t = t[: n - 1]
    if " " in t[n // 2:]:
        t = t[: t.rfind(" ")]
    return t.rstrip(" ,;:.-") + "…"


def data_utc(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        d = None
    if d is None:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def fmt(d):
    return d.strftime("%Y-%m-%dT%H:%MZ")


def dominio(url):
    try:
        h = urllib.parse.urlparse(url).hostname or ""
    except Exception:
        return ""
    return h[4:] if h.startswith("www.") else h


def link_canonico(url):
    try:
        p = urllib.parse.urlparse(url.strip())
        q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not k.lower().startswith(("utm_", "oc"))]
        return urllib.parse.urlunparse((p.scheme.lower(), (p.hostname or "").lower(), p.path.rstrip("/"),
                                        "", urllib.parse.urlencode(q), ""))
    except Exception:
        return url.strip()


def senza_ns(tag):
    return tag.rsplit("}", 1)[-1].lower()


def figlio(el, *nomi):
    for c in el:
        if senza_ns(c.tag) in nomi:
            return c
    return None


def lingua_di(testo, predefinita):
    if re.search(r"[іїєґ]", testo, re.I):
        return "uk"
    if re.search(r"[а-яё]", testo, re.I):
        return "ru"
    p = " " + testo.lower() + " "
    fr = sum(p.count(w) for w in (" le ", " la ", " les ", " des ", " et ", " est ", " une "))
    en = sum(p.count(w) for w in (" the ", " and ", " of ", " is ", " to ", " in "))
    if fr > en and fr >= 3:
        return "fr"
    if en > fr and en >= 3:
        return "en"
    return predefinita


# ---------------------------------------------------------------- lettori per tipo
def leggi_rss(fonte, dati):
    try:
        radice = ET.fromstring(dati)
    except ET.ParseError:
        # alcuni feed hanno caratteri non validi: ripulisce e riprova
        testo = dati.decode("utf-8", "replace")
        testo = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", testo)
        testo = re.sub(r"&(?!(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);)", "&amp;", testo)
        radice = ET.fromstring(testo.encode("utf-8"))
    voci = [e for e in radice.iter() if senza_ns(e.tag) in ("item", "entry")]
    out = []
    for v in voci[:MAX_PER_FONTE]:
        tit = figlio(v, "title")
        titolo = pulisci("".join(tit.itertext()) if tit is not None else "")
        link = ""
        for c in v:
            if senza_ns(c.tag) == "link":
                if c.get("href") and c.get("rel", "alternate") == "alternate":
                    link = c.get("href")
                    break
                if (c.text or "").strip():
                    link = c.text.strip()
                    break
        if not link:
            g = figlio(v, "guid", "id")
            if g is not None and (g.text or "").startswith("http"):
                link = g.text.strip()
        d = None
        for nome in ("pubdate", "published", "updated", "date", "issued"):
            c = figlio(v, nome)
            if c is not None and c.text:
                d = data_utc(c.text)
                if d:
                    break
        som = figlio(v, "description", "summary", "content", "encoded")
        sommario = pulisci("".join(som.itertext()) if som is not None else "")
        editore = ""
        src = figlio(v, "source")
        if src is not None and src.get("url"):
            editore = dominio(src.get("url"))
            nome_ed = (src.text or "").strip()
        else:
            nome_ed = ""
        out.append({"titolo": titolo, "link": link, "data": d, "sommario": sommario,
                    "editore": editore, "nome_editore": nome_ed})
    return out


def leggi_gnews(fonte, dati):
    out = leggi_rss(fonte, dati)
    for n in out:
        # Google News aggiunge " - Editore" al titolo e mette solo link nel sommario
        if n["nome_editore"] and n["titolo"].endswith(" - " + n["nome_editore"]):
            n["titolo"] = n["titolo"][: -len(" - " + n["nome_editore"])].strip()
        n["sommario"] = ""
    return out


def leggi_telegram(fonte, dati):
    t = dati.decode("utf-8", "replace")
    canale = fonte["url"].rstrip("/").rsplit("/", 1)[-1]
    out = []
    pezzi = t.split('class="tgme_widget_message_wrap')[1:]
    for p in pezzi[-MAX_PER_FONTE:]:
        post = re.search(r'data-post="([^"]+)"', p)
        tm = re.search(r'<time[^>]*datetime="([^"]+)"', p)
        tx = re.search(r'<div class="tgme_widget_message_text js-message_text"[^>]*>(.*?)</div>', p, re.S)
        if not (post and tm and tx):
            continue
        testo = pulisci(re.sub(r"<br\s*/?>", "\n", tx.group(1)))
        if len(testo) < 25:
            continue
        frase = re.split(r"(?<=[.!?])\s|\n", testo, maxsplit=1)[0]
        out.append({"titolo": taglia(frase, 160), "link": "https://t.me/" + post.group(1),
                    "data": data_utc(tm.group(1)), "sommario": testo, "editore": "t.me/" + canale,
                    "nome_editore": ""})
    return out


def leggi_threadreader(fonte, dati):
    t = dati.decode("utf-8", "replace")
    out, visti = [], set()
    for m in re.finditer(r'data-link-href="/thread/(\d+)\.html".*?data-time="(\d+)".*?'
                         r'<div class="card-tweetsv2"[^>]*>(.*?)</div>\s*</div>', t, re.S):
        tid, ts, corpo = m.group(1), int(m.group(2)), m.group(3)
        if tid in visti:
            continue
        visti.add(tid)
        corpo = re.sub(r'<div class="thumb-div">.*?</div>', " ", corpo, flags=re.S)
        testo = pulisci(re.sub(r'<span class="entity-image">.*?</span>', " ", corpo, flags=re.S))
        frase = re.split(r"(?<=[.!?])\s", testo, maxsplit=1)[0]
        out.append({"titolo": taglia(frase, 160),
                    "link": f"https://threadreaderapp.com/thread/{tid}.html",
                    "link_x": f"https://x.com/{fonte.get('utente', '')}/status/{tid}",
                    "data": datetime.fromtimestamp(ts, timezone.utc), "sommario": testo,
                    "editore": "x.com/" + fonte.get("utente", ""), "nome_editore": ""})
    return out[:MAX_PER_FONTE]


MESI = {m: i + 1 for i, m in enumerate(["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
                                        "agosto", "settembre", "ottobre", "novembre", "dicembre"])}


def leggi_bdi(fonte, dati):
    t = dati.decode("utf-8", "replace")
    out = []
    for m in re.finditer(r'<div class="bdi-result-date">.*?</div>\s*(\d{1,2}) (\w+) (\d{4}).*?'
                         r'<a class="bdi-result-title" href="([^"]+)"\s*>(.*?)</a>', t, re.S):
        g, mese, a, href, tit = m.groups()
        if mese.lower() not in MESI:
            continue
        d = datetime(int(a), MESI[mese.lower()], int(g), 12, 0, tzinfo=timezone.utc)
        out.append({"titolo": pulisci(tit), "link": urllib.parse.urljoin(fonte["url"], href.strip()),
                    "data": d, "sommario": "", "editore": "bancaditalia.it", "nome_editore": "",
                    "solo_data": True})
    return out[:MAX_PER_FONTE]


LETTORI = {"rss": leggi_rss, "gnews": leggi_gnews, "telegram": leggi_telegram,
           "threadreader": leggi_threadreader, "bdi_html": leggi_bdi}


def url_fonte(f):
    if f["tipo"] == "gnews":
        return "https://news.google.com/rss/search?" + urllib.parse.urlencode(
            {"q": f["url"], "hl": "en-US", "gl": "US", "ceid": "US:en"})
    return f["url"]


def raccogli_fonte(f):
    t0 = time.time()
    try:
        dati = scarica(url_fonte(f), tentativi=3 if f["tipo"] == "gnews" else 2)
        voci = LETTORI[f["tipo"]](f, dati)
        return f, voci, None, round(time.time() - t0, 1)
    except Exception as e:
        return f, [], f"{type(e).__name__}: {str(e)[:150]}", round(time.time() - t0, 1)


# ---------------------------------------------------------------- classificazione
def compila_temi():
    out = {}
    for tema, parole in TEMI.items():
        ci = [re.escape(p) for p in parole if not (p.isupper() and len(p) > 1)]
        cs = [re.escape(p) for p in parole if p.isupper() and len(p) > 1]
        rx_ci = re.compile(r"(?<!\w)(" + "|".join(ci) + r")(?!\w)", re.I) if ci else None
        rx_cs = re.compile(r"(?<!\w)(" + "|".join(cs) + r")(?!\w)") if cs else None
        out[tema] = (rx_ci, rx_cs)
    return out


def temi_di(testo, rx_temi):
    trovati = []
    for tema, (a, b) in rx_temi.items():
        if (a and a.search(testo)) or (b and b.search(testo)):
            trovati.append(tema)
    return trovati


def luoghi_di(titolo, sommario, luoghi, rx):
    trovati, visti = [], set()
    for parte, peso in ((titolo, 0), (sommario[:1200], 1)):
        for m in rx.finditer(parte):
            l = luoghi[m.group(1)]
            if l["nome"] in visti:
                continue
            visti.add(l["nome"])
            trovati.append((peso, ORDINE[l["tipo"]], m.start(), l))
    # il punto principale: prima il titolo, poi il luogo piu' preciso, poi il primo citato
    trovati.sort(key=lambda x: (x[0], x[1], x[2]))
    return [dict(l, precisione_km=PRECISIONE[l["tipo"]]) for _, _, _, l in trovati][:6]


def evento_di(titolo, sommario, famiglia, temi):
    # il verbo da evento deve stare nel titolo (per Telegram e Thread Reader il titolo e' la prima frase)
    testo = NON_EVENTO.sub(" ", titolo)
    motivi, cats = [], []
    for rx, cat in EVENTO:
        m = rx.search(testo)
        if m:
            motivi.append(m.group(0).lower())
            if cat not in cats:
                cats.append(cat)
    if not motivi or famiglia == "macro":
        return False, motivi, ""
    if SPECULATIVO.search(titolo) or MERCATO.search(titolo):
        return False, motivi, ""
    # serve almeno un tema "operativo", altrimenti e' rumore (es. "fire" in cronaca locale)
    if not set(temi) & (TEMI_FORTI | {"droni_missili", "nucleare", "elettricita_blackout"}):
        return False, motivi, ""
    if "ibrido" in cats:
        cat = "ibrido"
    elif "sabotaggio" in cats:
        cat = "sabotaggio"
    else:
        cat = cats[0]
    return True, motivi[:5], cat


def teatro_di(temi, luoghi):
    paesi = {l["paese"] for l in luoghi if l["paese"]}
    nomi = {l["nome"] for l in luoghi}
    if "ucraina_fronte" in temi or paesi & {"UA", "RU", "BY", "MD"} or nomi & {"Crimea", "Donbass", "Mar Nero", "Mar d'Azov"}:
        return "RU-UA"
    if set(temi) & {"hormuz", "mar_rosso_houthi", "guerra_iran"} or paesi & {
            "IR", "IL", "LB", "SY", "IQ", "YE", "SA", "AE", "QA", "OM", "KW", "BH", "JO", "EG"}:
        return "MO"
    if set(temi) & {"sabotaggi_ibrido", "cavi_sottomarini"}:
        return "NATO"
    return ""


def classifica(el, sommario, luoghi, rx_luoghi, rx_temi):
    """Temi, luoghi (con coordinate approssimate) e possibile evento di una notizia."""
    titolo = el["titolo"]
    temi = temi_di(titolo + " " + sommario, rx_temi)
    lu = luoghi_di(titolo, sommario, luoghi, rx_luoghi)
    ev, motivi, cat = evento_di(titolo, sommario, el["famiglia"], temi)
    el.update({
        "temi": temi,
        "luoghi": lu,
        "lat": lu[0]["lat"] if lu else None,
        "lon": lu[0]["lon"] if lu else None,
        "precisione_km": lu[0]["precisione_km"] if lu else None,
        "origine_coord": ("stimata dal toponimo '" + lu[0]["nome"] + "' (" + lu[0]["tipo"] + ", labels.json)") if lu else "",
        "paese": next((l["paese"] for l in lu if l["tipo"] == "paese" and l["paese"]), ""),
        "teatro": teatro_di(temi, lu),
        "possibile_evento": ev,
        "categoria_proposta": cat,
        "motivi_evento": motivi if ev else [],
    })


STOP = set("""a an the of to in on for and or at by with from as is are was were be been after before over into
amid says say said new news its it this that than more about up out not no but will has have had his her their
il lo la i gli le di da del della dei delle in con su per tra fra e o un una che non al alla""".split())


def parole_titolo(t):
    t = re.sub(r"[^\w\s]", " ", t.lower())
    return {w for w in t.split() if len(w) > 2 and w not in STOP}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ---------------------------------------------------------------- principale
def main():
    conf = json.load(open(FONTI, encoding="utf-8"))
    fonti = [f for f in conf["fonti"] if f.get("attiva", True)]
    editori = {}
    for livello, domini in conf.get("editori", {}).items():
        for d in domini:
            editori[d] = livello
    luoghi, rx_luoghi, avvisi_luoghi = carica_luoghi()
    rx_temi = compila_temi()
    errori = list(avvisi_luoghi)

    # 1. scarico: fonti dirette in parallelo, Google News una alla volta (limita le richieste: 503)
    risultati = []
    dirette = [f for f in fonti if f["tipo"] != "gnews"]
    with cf.ThreadPoolExecutor(8) as ex:
        risultati.extend(ex.map(raccogli_fonte, dirette))
    for f in [f for f in fonti if f["tipo"] == "gnews"]:
        r = raccogli_fonte(f)
        if r[2] and "503" in r[2]:
            time.sleep(30)
            r = raccogli_fonte(f)
        risultati.append(r)
        time.sleep(4)

    stato_fonti, grezze = [], []
    for f, voci, err, secondi in risultati:
        stato_fonti.append({"id": f["id"], "nome": f["nome"], "tipo": f["tipo"], "famiglia": f["famiglia"],
                            "esito": "funziona" if not err else "errore", "notizie_lette": len(voci),
                            "errore": err or "", "secondi": secondi})
        if err:
            errori.append(f"{f['id']}: {err}")
        for v in voci:
            v["_fonte"] = f
            grezze.append(v)
        print(f"{f['id']:20s} {'OK ' if not err else 'ERR'} {len(voci):3d} {err or ''}", file=sys.stderr)

    # 2. normalizzo
    limite = ORA - timedelta(days=GIORNI)
    nuove = []
    for v in grezze:
        f = v["_fonte"]
        if not v["titolo"] or not v["link"]:
            continue
        d = v["data"]
        data_stimata = False
        if d is None:
            d, data_stimata = ORA, True
        if d > ORA + timedelta(hours=2):
            d, data_stimata = ORA, True
        if d < limite:
            continue
        testo = v["titolo"] + " " + v["sommario"]
        if f.get("filtro") and not any(p.lower() in testo.lower() for p in f["filtro"]):
            continue
        temi = temi_di(testo, rx_temi)
        if f.get("solo_con_tema") and not temi:
            continue
        ed = v.get("editore") or dominio(v["link"])
        aff = editori.get(ed, f["affidabilita"]) if f["tipo"] == "gnews" else f["affidabilita"]
        if f["tipo"] == "gnews" and ed not in editori:
            aff = "bassa" if f["affidabilita"] != "alta" else "media"
        lingua = lingua_di(testo, f.get("lingua", "en")) if f["tipo"] in ("telegram", "threadreader") else f.get("lingua", "en")
        el = {
            "id": "N-" + hashlib.sha1(link_canonico(v["link"]).encode()).hexdigest()[:12],
            "titolo": v["titolo"][:300],
            "data_utc": fmt(d),
            "data_fonte": d.strftime("%Y-%m-%d"),
            "link": v["link"],
            "fonte": v.get("nome_editore") or f["nome"],
            "via": f["nome"] if f["tipo"] == "gnews" else "",
            "editore": ed,
            "fonte_id": f["id"],
            "famiglia": f["famiglia"],
            "lingua": lingua,
            "affidabilita": aff,
            "sommario": taglia(v["sommario"]) if v["sommario"] else "",
            "stato": "da verificare",
            "visto_il": fmt(ORA),
        }
        if v.get("link_x"):
            el["link_x"] = v["link_x"]
        if data_stimata:
            el["data_stimata"] = True
        if v.get("solo_data"):
            el["solo_data"] = True
        classifica(el, v["sommario"], luoghi, rx_luoghi, rx_temi)
        nuove.append(el)

    # 3. unisco con il file precedente (finestra di 7 giorni) e deduplico
    precedenti = []
    if os.path.exists(OUT):
        try:
            precedenti = json.load(open(OUT, encoding="utf-8")).get("elementi", [])
        except Exception as e:
            errori.append(f"file precedente illeggibile: {e}")
    per_id = {}
    for el in precedenti:
        d = data_utc(el.get("data_utc", "").replace("Z", ":00Z")) if el.get("data_utc") else None
        if d and d >= limite:
            classifica(el, el.get("sommario", ""), luoghi, rx_luoghi, rx_temi)  # regole sempre aggiornate
            per_id[el["id"]] = el
    for el in nuove:
        if el["id"] in per_id:
            el["visto_il"] = per_id[el["id"]].get("visto_il", el["visto_il"])
            if el.get("data_stimata") and not per_id[el["id"]].get("data_stimata"):
                el["data_utc"] = per_id[el["id"]]["data_utc"]
        per_id[el["id"]] = el
    tutte = list(per_id.values())
    # stesso titolo normalizzato = stessa notizia ripubblicata: tengo la piu' affidabile, poi la piu' vecchia
    rango = {"alta": 0, "media": 1, "bassa": 2}
    tutte.sort(key=lambda e: (rango.get(e["affidabilita"], 3), e["data_utc"]))
    per_titolo, doppioni = {}, 0
    for el in tutte:
        k = " ".join(sorted(parole_titolo(el["titolo"])))
        if not k:
            continue
        if k in per_titolo:
            tenuta = per_titolo[k]
            if el["editore"] and el["editore"] != tenuta["editore"]:
                tenuta.setdefault("anche_su", [])
                if el["editore"] not in tenuta["anche_su"]:
                    tenuta["anche_su"].append(el["editore"])
            doppioni += 1
            continue
        per_titolo[k] = el
    tutte = list(per_titolo.values())

    # 4. gruppi: titoli simili da editori diversi = stessa storia (base per la regola delle due fonti)
    tutte.sort(key=lambda e: e["data_utc"])
    parole = [parole_titolo(e["titolo"]) for e in tutte]
    padre = list(range(len(tutte)))

    def radice(i):
        while padre[i] != i:
            padre[i] = padre[padre[i]]
            i = padre[i]
        return i
    for i in range(len(tutte)):
        di = tutte[i]["data_utc"]
        for j in range(i + 1, len(tutte)):
            if tutte[j]["data_utc"][:10] > (data_utc(di.replace("Z", ":00Z")) + timedelta(days=2)).strftime("%Y-%m-%d"):
                break
            pi, pj = parole[i], parole[j]
            if len(pi & pj) >= 3 and jaccard(pi, pj) >= SOGLIA_GRUPPO:
                padre[radice(j)] = radice(i)
    gruppi = {}
    for i, e in enumerate(tutte):
        gruppi.setdefault(radice(i), []).append(e)
    for membri in gruppi.values():
        gid = "G-" + membri[0]["id"][2:10]
        ed = set()
        for m in membri:
            ed.add(m["editore"] or m["fonte_id"])
            ed.update(m.get("anche_su", []))
        for m in membri:
            m["gruppo"] = gid
            m["n_editori_gruppo"] = len(ed)

    # 5. punteggio di rilevanza (solo per ordinare: non e' una verifica)
    for e in tutte:
        d = data_utc(e["data_utc"].replace("Z", ":00Z"))
        ore = (ORA - d).total_seconds() / 3600
        p = 0
        p += 3 if e["possibile_evento"] else 0
        p += 2 * len(set(e["temi"]) & TEMI_FORTI) + len(set(e["temi"]) - TEMI_FORTI) * 0.5
        p += {"alta": 2, "media": 1}.get(e["affidabilita"], 0)
        p += min(e.get("n_editori_gruppo", 1) - 1, 4)
        p += 2 if ore <= 24 else 1 if ore <= 48 else 0
        p += 1 if e["lat"] is not None and e["precisione_km"] and e["precisione_km"] <= 100 else 0
        e["punteggio"] = round(p, 1)

    tutte.sort(key=lambda e: e["data_utc"], reverse=True)

    # 6. in evidenza: le storie piu' rilevanti delle ultime 48 ore, una per gruppo
    lim48 = fmt(ORA - timedelta(hours=48))
    evid, gruppi_visti = [], set()
    for e in sorted(tutte, key=lambda e: (-e["punteggio"], e["data_utc"])):
        if e["data_utc"] < lim48 or e["gruppo"] in gruppi_visti or e["famiglia"] == "macro":
            continue
        gruppi_visti.add(e["gruppo"])
        evid.append(e["id"])
        if len(evid) >= 25:
            break

    # 7. riepilogo
    oggi = ORA.strftime("%Y-%m-%d")
    riep = {"totale": len(tutte), "doppioni_tolti": doppioni, "gruppi": len({e["gruppo"] for e in tutte}),
            "per_famiglia": {}, "oggi_per_famiglia": {}, "ultime_24h_per_famiglia": {}, "per_tema": {},
            "possibili_eventi": sum(1 for e in tutte if e["possibile_evento"]),
            "con_coordinate": sum(1 for e in tutte if e["lat"] is not None)}
    lim24 = fmt(ORA - timedelta(hours=24))
    for e in tutte:
        riep["per_famiglia"][e["famiglia"]] = riep["per_famiglia"].get(e["famiglia"], 0) + 1
        if e["data_utc"].startswith(oggi):
            riep["oggi_per_famiglia"][e["famiglia"]] = riep["oggi_per_famiglia"].get(e["famiglia"], 0) + 1
        if e["data_utc"] >= lim24:
            riep["ultime_24h_per_famiglia"][e["famiglia"]] = riep["ultime_24h_per_famiglia"].get(e["famiglia"], 0) + 1
        for t in e["temi"]:
            riep["per_tema"][t] = riep["per_tema"].get(t, 0) + 1
    riep["per_tema"] = dict(sorted(riep["per_tema"].items(), key=lambda x: -x[1]))

    uscita = {
        "aggiornato": fmt(ORA),
        "fonti": [{"nome": f["nome"], "link": f["url"] if f["tipo"] != "gnews" else url_fonte(f),
                   "licenza": "solo titolo, sommario breve e link verso l'editore (diritti dell'editore)",
                   "data_dato": fmt(ORA), "famiglia": f["famiglia"], "tipo": f["tipo"],
                   "affidabilita_predefinita": f["affidabilita"], "lingua": f.get("lingua", "")}
                  for f in fonti],
        "nota": ("Notizie grezze degli ultimi 7 giorni per l'agente coordinatore: TUTTE 'da verificare'. "
                 "Temi e luoghi sono assegnati con parole chiave; lat/lon sono il centro del toponimo citato "
                 "(labels.json) con precisione_km dichiarata, non il punto esatto del fatto. 'possibile_evento' "
                 "segnala titoli con verbi da evento (attacco, sequestro, esplosione, sabotaggio, chiusura, "
                 "blackout...). 'gruppo' unisce titoli simili; 'n_editori_gruppo' conta gli editori diversi "
                 "(attenzione: le riprese di Reuters/AP non sono fonti indipendenti). Le voci 'via Google News' "
                 "puntano a news.google.com, che rimanda all'articolo dell'editore."),
        "riepilogo": riep,
        "stato_fonti": stato_fonti,
        "in_evidenza": evid,
        "elementi": tutte,
        "errori": errori,
    }
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(uscita, fh, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, OUT)
    print(f"scritto {OUT}: {len(tutte)} notizie, {riep['possibili_eventi']} possibili eventi, "
          f"{len(errori)} errori", file=sys.stderr)


if __name__ == "__main__":
    main()
