# World events layer — agent report

10 November 2026 · script `raccolta/eventi/raccogli.py` (standard library only, no keys; run for real on 10 Nov 2026, about 15 s) · output `docs/data/eventi.json` (**385 points**, 402 KB, 0 errors) · inputs `raccolta/eventi/curati.json` (the 126 earlier events, copied unchanged) and `raccolta/eventi/curati_nuovi.json` (155 new curated events) · project validator `raccolta/originali/controlla.py`: 0 errors.

The layer went from 126 points (90 "attacco", almost all Middle East and Ukraine, 29 Oct – 9 Nov) to 385 points across the world, 13 Jul – 9 Nov 2026. It now covers maritime security, attacks on energy, shipping, ports and airports, chokepoint notices and closures, blackouts, industrial accidents, port strikes and blockades, and natural hazards that hit logistics. 117 of the points refresh by themselves every day: USGS 56, GDACS 20, EONET 28 and ReCAAP 13.

## 1. Sources tried

| Source | Result | Licence | Use |
|---|---|---|---|
| USGS FDSN event service (GeoJSON) | **works**, no key | public domain (US Government) | automatic: M6.0+, or M5.5+ with a PAGER alert yellow/orange/red, 120 days → 56 points |
| GDACS event-list API (`gdacsapi/.../geteventlist/SEARCH`) | **works**, no key (RSS also works, 850 KB) | free use with citation of GDACS (EC JRC / UN OCHA) | automatic: orange/red EQ, TC, FL, VO, WF → 41 read, 20 kept after merging (droughts skipped) |
| NASA EONET v3 | **works**, no key | public domain (NASA) | automatic: severe storms at hurricane force (≥ 64 kt), point at peak intensity → 28 points. The volcano category returned nothing for the window. |
| ReCAAP ISC list of incidents (PDF) | **works** (plain HTTPS) | public reports, cite ReCAAP ISC | automatic **only if `pdftotext` (poppler-utils) is installed**. Otherwise it is skipped with a warning and the 13 curated copies in `curati_nuovi.json` are kept. Coordinates come from ReCAAP. |
| UKMTO recent incidents | **fails**: 403 to scripted clients (bot protection) | — | not used directly; UKMTO warnings enter through the outlets that report them |
| MARAD MSCI advisories | **fails**: 403 "Access denied" | — | — |
| IMB PRC live piracy report | **fails**: 403 "Blocked" | — | IMB statistics cited through the press |
| NGA MSI ASAM API | **fails**: 503 | — | — |
| ReliefWeb API | v1 **gone** (410). v2 **needs an approved appname** (403). | — | possible later: a free appname in an env var |
| GDELT DOC/GEO API | **fails**: 429 (one call every 5 s), then connection resets. DOC returns articles without coordinates. | — | not used: points would need invented coordinates |
| IMO GISIS monthly piracy reports | **fails**: September 2026 PDF not found (404) | — | — |
| Wikipedia Portal:Current events (raw wikitext, 13 Jul – 10 Nov) and *List of shipwrecks in 2026* | **works**; 429 if called too fast | CC BY-SA | **index only** for curation: each item links the outlet Wikipedia cites (Reuters, AP, BBC, Al Jazeera…); no text copied |
| Web search (news) | works | facts with link | curation of `curati_nuovi.json` |

## 2. What the file contains

Same schema as before. Each point has id, classe `evento`, categoria, nome, identificativo, appartenenza, stato, data_evento, ora_utc, lat, lon, origine_coord, precisione_km, teatro, paese, regione, attore, bersaglio, mezzo, esito, fonte, link, data_fonte, affidabilita, note, fonti[] and breve. The keys `raccolte` and `fuori` are kept from the curated file. New top-level keys: `fonti`, `nota`, `conteggi` and `errori`.

- **Curated new points (142 + 13 ReCAAP)** are in English. The coordinates are those of the place the source names: a port, plant, airport or town, or a distance and bearing from it ("63 nm W of Yanbu"), computed with a great-circle formula. They carry `origine_coord: "stimata"` and an honest radius. 14 points have a radius over 100 km and are therefore report-only on the map: for example "off the UAE", the East-West pipeline, Cyclone Arnab's landfall and Ocean Winner "240 nm off Odisha".
- **Automatic points** use the coordinates the source publishes (`origine_coord: "fonte"`). Their notes add the nearest monitored port or chokepoint within 500 km (from `port-risk.json` and `portwatch.json`, read only).
- **Earlier 126 points**: unchanged, still in Italian.
- **Rolling window**: 120 days. Older items are kept only if flagged `"strategico": true`, a flag no item uses yet.
- **Merge rules**: priority goes earlier curated > new curated > automatic. An item is dropped as a duplicate if it has the same category group within ±1 day and a few km of a higher-priority item. A GDACS earthquake becomes a note on its USGS twin (matched by magnitude and distance). A GDACS cyclone becomes a note on the EONET storm with the same name. 19 duplicates were dropped.
- **If a feed fails**, the items it produced in yesterday's file are kept, so a temporary outage does not empty the layer. This was tested with `--offline` and without `pdftotext`.

### Counts by category (all 385 / new 259)

| Category | All | New | Display name to add |
|---|---|---|---|
| attacco | 156 | 66 | (exists) |
| terremoto | 57 | 57 | **new**: Earthquake |
| tempesta | 38 | 38 | **new**: Storm / tropical cyclone |
| incidente | 37 | 28 | (exists) |
| pirateria | 18 | 18 | **new**: Piracy / sea robbery |
| incendio-boschivo | 10 | 10 | **new**: Wildfire |
| blackout | 10 | 3 | (exists) |
| alluvione | 8 | 8 | **new**: Flood |
| vulcano | 7 | 7 | **new**: Volcanic eruption |
| chiusura-passaggio | 6 | 5 | (exists) |
| lancio | 6 | 0 | (exists) |
| sciopero | 5 | 5 | **new**: Strike or port blockade |
| avviso-marittimo | 5 | 5 | (exists) |
| chiusura-spazio-aereo | 5 | 4 | (exists) |
| intercettazione | 5 | 0 | (exists) |
| combattimento | 3 | 3 | (exists) |
| avanzamento | 3 | 0 | (exists) |
| sequestro | 2 | 2 | (exists) |
| allerta | 2 | 0 | (exists) |
| rischieramento / esercitazione | 1 / 1 | 0 | (exist) |

New `bersaglio` value: **`nave-gasiera`** (gas carrier). It is already in `CAT_IT` but missing from `BERS_IT`. `rotta-marittima` and `passaggio-strategico` already exist.

### Counts by region

| Theatre (`teatro`) | All | New |
|---|---|---|
| MO | 124 | 72 |
| RU-UA | 85 | 12 |
| NATO (Europe) | 26 | 25 |
| ALTRO (rest of world) | 150 | 150 |

The 259 new points by area: Gulf, Red Sea and Arabian Peninsula 71 (50 attacks), South and South-East Asia 56 (13 piracy/robbery, 12 storms, 12 earthquakes), Americas 48, Europe and Mediterranean 25, Pacific 17, East Asia 11, Black Sea 11, Africa 9, Russia and Central Asia 6, other 5.

Reliability of the new points: 173 `alta` (official agency or operator, or several outlets), 86 `media` (one outlet, or a party's claim such as the IRGC or the Houthis). None is `bassa`.

## 3. Eight notable facts

1. **Panama, 9 Oct 2026**: M7.7 earthquake 10 km WSW of Pitaloza Arriba, PAGER alert orange, 2,018 felt reports. It was followed by M6.6, M6.0 and M6.1 events through 12 Oct, about 200 km from the Canal. Separately, the Canal cut daily transits from 36 to 32 on 15 Sep because of the El Niño drought, after a record USD 5.3 m was paid for one slot on 27 Aug. (USGS; DW; France 24)
2. **Strait of Hormuz, 14 Oct**: container ship GFS Pride and bulk carrier Cape Dao sank off Musandam after attacks. The IRGC said they were on an "illegal route". ADNOC says 15 of its ships were attacked in Hormuz since 28 Feb. (The Guardian; Reuters, 7 Aug)
3. **Saudi Arabia, 10–11 Sep**: drones launched from Iraq damaged pumping stations 8 and 9 of the East-West crude pipeline, the Hormuz bypass to Yanbu. The line was shut on 11 Sep and fully restarted about 22 Sep. (Reuters via PGJ Online; CNBC; ARY News)
4. **Riyadh, 10 Oct**: a Houthi missile hit Terminal 3 of King Khalid International Airport, killing 12 (13 later) and injuring 309. The airport resumed limited operations only on 25 Oct. (WSJ; Reuters; ABS-CBN)
5. **Black Sea, 6 and 13 Oct**: drones of unknown origin hit two merchant ships off Bulgaria on each day and one sank each time. 12 Syrian sailors went missing in the first attack and 11 crew in the second; Bulgaria's prime minister blamed Russia. Also on 6 Oct, the shadow-fleet Aframax Rio burned for more than 24 h off Sochi. (Reuters; Al Jazeera; Maritime Executive)
6. **Somali piracy, 20 Aug – 29 Sep**: the sanctioned tanker Sibu 1 was hijacked 136 nm east of Al Mukalla. Puntland forces freed Honour 25 on 29 Sep after pirates had killed five crew, the first such deaths in over a decade. In Asia, ReCAAP counts 50 incidents in Jan–Sep 2026 (−58 %). (Al Jazeera; Reuters; Baird Maritime)
7. **China ports, 7–10 Aug and 26–28 Aug**: Typhoons Dolphin and Saudel shut terminals at Shanghai (Yangshan, Waigaoqiao) and Ningbo. Drewry: Bavi and Dolphin left more than 2.4 million TEU stranded. (C.H. Robinson; Kuehne+Nagel)
8. **Danube, 13 Aug**: Romania shut the second Cernavodă reactor because drought pushed the Danube below cooling level, leaving both reactors offline. Imports covered demand. (AP)

Also worth a look: Cuba's grid collapsed nationwide on 14 Jul, 2 Aug and 18 Sep. MRPL's Mangaluru refinery blast on 30 Sep led it to cancel export tenders. A drone hit the Damietta LNG storage ship on 29 Jul. Dockworkers at 113 ports struck on 30 Oct ("Dockworkers don't work for war"; Reuters).

## 4. Links with the other layers

- **Chokepoints** (`stretti.json` via `raccolta/stretti/raccogli.py`, risk dashboard via `raccolta/rischio/calcola.py`): both count events within 150–200 km of a passage over 30 days. With the new file, over the last 30 days Hormuz gains 7 points (attacks, notices, incidents), Malacca 2 (ReCAAP robberies) and the Taiwan Strait 1 (a factory fire in Hsinchu). **Suggestion for the coordinator**: add `terremoto, tempesta, vulcano, alluvione, incendio-boschivo, sciopero, avviso-marittimo` to `CATEGORIE_EVENTO_ESCLUSE` in `calcola.py`, or count them as "disruption" rather than "threat". I did not edit it.
- **Ports** (`port-risk.json`): the notes of automatic points name the nearest monitored port or chokepoint.
- **Not duplicated on purpose**: Ukraine front-line and city strikes (`attacchi-analisti.json`, `attacchi-russi.json`; here only six major energy and port items: Sheskharis, Ust-Luga, Moscow, Yaroslavl, Ufa and Nizhnekamsk refineries, Odesa port), hybrid drones and airport scares (`ibrido.json`, e.g. Vilnius, Berlin, Munich, Leipzig), Baltic shadow-fleet detentions (`baltico-sicurezza.json`) and cable cuts (`cavi-incidenti.json`).
- **Health check**: `controlla_tutto.py` lists `eventi.json` with a monthly cadence. It is now daily, so it could move to the daily list.

## 5. Suggested display

New categories fall back to the generic "altro" glyph, coloured by age, which works as is. Better options:

- add the seven display names above to `CAT_IT` and `nave-gasiera: 'gas carrier'` to `BERS_IT`;
- give natural hazards (terremoto, tempesta, vulcano, alluvione, incendio-boschivo) their own glyph, or their own switch "Natural hazards", because 57 earthquakes in 120 days would crowd the 90-day view;
- show `pirateria` with the attack glyph but hollow;
- keep `sciopero` and `avviso-marittimo` as small symbols.

The default 7-day view barely changes: 111 drawable points, of which only 8 are new. Most of the growth shows in the 30-day, 90-day and "All" views.

## 6. Limits

- Curated points do not update themselves. The daily run refreshes only USGS, GDACS, EONET and ReCAAP. The curated files need a periodic pass (agent or by hand); items drop out after 120 days.
- Many Gulf incidents are known only as "in the Strait of Hormuz" (radius 40–50 km) or from time-late UKMTO warnings. Some dates differ by a day between outlets. Iranian and Houthi claims are marked `media` and described as claims.
- Several curated positions are a named place standing for an area. For example, Cuba's national blackouts are shown on Havana, and Honour 25 on Bandarbeyla for "Bayla", with radius 60 km. Some plant locations (Nizhnekamsk, Ufa) are approximate within the stated radius.
- EONET storm points mark peak intensity, not landfall. GDACS flood points are area centroids (radius 150 km, report only). Many M6+ earthquakes are remote and deep, with no logistic impact; the "nearest monitored port" note helps, but that list has only 39 ports, mostly in Europe and the Middle East.
- ReCAAP needs `pdftotext` on the runner (one apt package). Without it the curated copies stand in until they age out.
- `controlla.py` flags 37 points as "to review" because their `data_fonte` is older than 90 days. That is expected with a 120-day window.
- One source link returned 404 on 10 Nov (CNA, Sikkim tunnel blast). The item's first source is now the Wikipedia Current events page for that day.
- Search results were dense for the Gulf and the Red Sea but thin for September–October in some topics: Libya, Gulf of Guinea, LNG outages and Baltic detentions.
