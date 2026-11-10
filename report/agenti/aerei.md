# Aircraft layer (aerei.json): report

Updated 10 November 2026. Files: `raccolta/aerei/raccogli.py`, `raccolta/aerei/curati.json`, `docs/data/aerei.json`.

## What the file contains

`docs/data/aerei.json` keeps the items under `punti`, in the same schema as the aircraft items in `docs/data/mobili.json`. That means `classe: "mobile"`, the same fields (`id`, `categoria`, `nome`, `identificativo`, `appartenenza`, `stato`, `data_evento`, `ora_utc`, `lat`, `lon`, `origine_coord`, `precisione_km`, `teatro`, `paese`, `regione`, `fonte`, `link`, `data_fonte`, `affidabilita`, `note`, `fonti[]`, `breve`, `dettaglio`) and the same empty `attore`, `bersaglio`, `mezzo` and `esito`. There are two extra fields: `istantanea: 1` marks a snapshot item and `n_aerei` gives the number of aircraft in an item. The file also has `aggiornato`, `fonti`, `nota`, `conteggi`, `errori` and `avvisi`. It is about 95 KB.

The categories are `aereo-cisterna`, `aereo-ricognizione`, `aereo-trasporto` and `aereo-bombardiere`, as in mobili.json, plus `aereo-caccia`. The map already handles `aereo-caccia`: it is in `AIR_GLYPH` and `CAT_IT` in docs/index.html. For the 'air' layer the map takes any `classe: mobile` item whose category starts with `aereo`. It picks the colour from `appartenenza` (`NATO` counts as an ally) and fades items by age: over 14 days they are faded, over 60 days they are not drawn. For a `precisione_km` above 3 it draws a circle.

Counts from the 10 Nov 2026 runs (around 11:52 UTC; the snapshot changes on every run):

| Part | Items | Notes |
|---|---|---|
| ADS-B snapshot | 20 (20 aircraft) | 230 military aircraft received. 93 had no position, 110 were types not kept, and 7 were dropped as VIP or government. An earlier run the same morning kept 22. |
| Curated deployments | 43 | 10 Sep – 10 Nov 2026. One item (Turkish F-16s at Ämari, last report 1 Sep) is older than 60 days and will not be drawn. |
| By category | tanker 23, ISR/AWACS 21, transport 10, fighter 8, bomber 1 | |

### (a) Automatic snapshot
- **Sources:** `api.adsb.lol/v2/mil` first, then 8 `/v2/type/<ICAO>` queries (K35R, R135, E3TF, P8, Q4, B52, C17, C5M), then `opendata.adsb.fi/api/v2/mil`. adsb.fi adds missing aircraft and fills in the description and operator fields for the others.
- **What is kept:** only a whitelist of types. Tankers: KC-135, KC-46, A330 MRTT, KC-767 and Il-78. ISR and AWACS: RC-135, E-3, E-7, E-767, P-8, RQ-4/MQ-4C, U-2, E-6, A-50, Il-20 and P-1. Strategic airlifters: C-17, C-5, A400M, Il-76 and An-124. Bombers: B-52, B-1, B-2, Tu-160, Tu-95, Tu-22M and H-6. Airframes that also exist as VIP aircraft (A330, 767, 737, Global Express) are kept only if the description or registration shows a tanker or ISR variant.
- **What is excluded:** aircraft not flagged military; aircraft whose owners asked for privacy (database flags PIA or LADD); VIP callsigns (SAM, EXEC, SPAR, VENUS, AF1, AF2); operators described as VIP, government or royal flight; positions older than 10 minutes. No business jets, helicopters or private aircraft get through.
- **Grouping:** aircraft parked at the same base are merged into one item. Aircraft in flight within 30 km of each other, with the same category and owner, are also merged, which covers formations.
- **Timestamps:** each item has a UTC time (`ora_utc`). The note says the position is a snapshot taken at collection time and is not live.
- **Owner (`appartenenza`):** taken from the ICAO 24-bit address block (ICAO Annex 10). NATO is set from the registration: LX-N for the E-3A, T-05x/T-06x for the MRTT fleet, MM-AV-SA for the RQ-4D.

### (b) Curated deployments (43)
- **Each item:** placed at the base the source names. Base coordinates come from OurAirports and are recorded in `rif_coord`, with `origine_coord: stimata` and a precision of 2–5 km.
- **Orbits with no base:** these are Black Sea ISR, the Baltic, Poland, the Tyrrhenian during Steadfast Noon, and off Tobruk. They use an estimated centre and a wide radius of 80–350 km.
- **Departures:** a withdrawal is marked `stato: lasciata`. Examples are the B-1Bs leaving Fairford, the KC-135s leaving Mildenhall and the F-16s leaving Spangdahlem. The card then reads "Vacated", and the point is the base that was left.
- **Coverage:**
  - The US air bridge to CENTCOM through Ramstein, Spangdahlem, Sigonella and Tel Aviv.
  - The 9 November relocation of tankers from Mildenhall to Spangdahlem, Ramstein, Morón and Prestwick.
  - Fighter moves through Spangdahlem and Aviano, with KC-135s from Bucharest.
  - ISR at Souda Bay: RC-135V/W, the RAF RC-135W, the EA-37B and an Italian P-72A.
  - Black Sea ISR: the Italian CAEW, the RAF RC-135W, ARTEMIS II, and the US Navy P-8A from Varna.
  - NATO AWACS at Geilenkirchen and the NATO MRTT at Cologne.
  - Air policing at Šiauliai, Ämari, Mihail Kogălniceanu, Borcea and Rzeszów.
  - The Italian Task Force Air at Taif.

### (c) Airspace closures / NOTAM
Skipped. I found no clean, keyless public source with a licence that allows reuse. FAA NOTAM API needs registration and the ICAO API needs a key. EUROCONTROL publishes no open NOTAM feed, and the aggregator sites have unclear terms.

## Sources and licences

| Source | Status | Licence / terms | Attribution text to show |
|---|---|---|---|
| adsb.lol API `/v2/mil`, `/v2/type/*` | works, no key | **ODbL 1.0**. Share-alike: aerei.json is a derived database and has to stay under ODbL or a compatible licence. | "Aircraft data © adsb.lol contributors, ODbL 1.0 (https://www.adsb.lol)" |
| adsb.fi open data `/api/v2/mil` | works, no key, 1 request/s | **Personal, non-commercial use only**. You must cite adsb.fi with a link. No resale or relicensing. Fine for this personal project, but it is not an open licence. | "Data: adsb.fi (https://adsb.fi)" |
| airplanes.live `/v2/mil` | **does not work**: HTTP 403 | Asks the project to email them first | (not used) |
| OurAirports airports.csv | works | public domain | "Base coordinates: OurAirports" |
| ItaMilRadar, Misbar, CNN, UK Defence Journal, Task & Purpose, AeroTime, Euronews, Breitbart (citing BBC/CBS), MigFlug, Grosswald, LRT | facts quoted with link and date | publishers' copyright: only short facts are quoted, with a link | the source is named on every item |

Two more notes. The adsb.lol `/v2/type` queries sometimes return HTTP 429 (rate limited). The script then logs a warning and carries on, because these queries are only an extra. The domains thenationalnews.com and airandspaceforces.com cannot be reached from this environment, so I did not use them as sources.

## 8 facts (date, source)
1. **4 Oct 2026:** US European Command confirmed that all US bombers deployed to RAF Fairford had gone home. The New York Times put it at 12 B-1Bs. ([UKDJ](https://ukdefencejournal.org.uk/american-bomber-fleet-departs-britain/))
2. **9 Nov 2026:** 10 KC-135s were moved out of RAF Mildenhall after a threat linked to Iran: 4 to Spangdahlem, 1 to Ramstein, 4 to Morón and 1 to Prestwick. Mildenhall and Lakenheath went to FPCON Charlie. ([CNN](https://www.cnn.com/2026/11/10/world/us-moves-aircraft-british-military-base-intl))
3. **7 Nov 2026:** four C-17s left Ramstein and Spangdahlem for the eastern Mediterranean. Two KC-135Rs were flying to Tel Aviv, and a KC-135T reached Sigonella. ([Misbar](https://www.misbar.com/en/editorial/2026/11/08/flight-tracking-data-shows-seven-us-military-aircraft-arriving-europe-and-middle-east))
4. **22 and 29 Sep 2026:** 12 F-16Cs of the 138th FW left Spangdahlem, and 6 F-16Cs of the 482nd FW left Aviano, both toward CENTCOM with KC-135Rs flying from Bucharest. ([ItaMilRadar](https://www.itamilradar.com/2026/09/22/three-kc-135s-join-12-us-f-16s-in-germany-for-a-flight-toward-the-gulf/), [ItaMilRadar](https://www.itamilradar.com/2026/09/29/more-f-16s-leave-aviano-for-the-gulf/))
5. **8 Oct 2026:** an EA-37B Compass Call (19-1587) moved from Ramstein to Souda Bay, hours after reports that Iran strike options were being prepared. ([ItaMilRadar](https://www.itamilradar.com/2026/10/08/usaf-ea-37b-moves-from-ramstein-to-souda-bay-as-washington-weighs-new-iran-strike-options/))
6. **15 Sep 2026:** Italian Eurofighters flying Baltic air policing from Šiauliai shot down a drone that entered Lithuania from the direction of Belarus. ([ItaMilRadar](https://www.itamilradar.com/2026/09/15/italian-eurofighters-shoot-down-drone-over-lithuania-putting-natos-eastern-air-defence-to-the-test/))
7. **17 Oct 2026:** two Romanian F-16s from Borcea shot down two Geran jet drones near Sulina, according to the Romanian MoD. ([ItaMilRadar](https://www.itamilradar.com/2026/10/18/romanian-f-16s-shoot-down-two-geran-drones-as-black-sea-attacks-push-closer-to-nato-territory/))
8. **9 Nov 2026:** USAF RQ-4B 11-2046 (RICO28) was back at Sigonella, its first appearance in ItaMilRadar's records since 2 February. NATO's RQ-4D resumed flights from Sigonella on 3 November. ([ItaMilRadar](https://www.itamilradar.com/2026/11/09/us-air-force-rq-4b-global-hawk-returns-to-sigonella-restoring-a-key-mediterranean-surveillance-asset/))

## Links with other layers
- **Strategic passages (stretti) and Middle East:** the air bridge and tanker flow toward CENTCOM (Ramstein, Sigonella, Souda Bay, Ben Gurion) matches the Hormuz and Red Sea risk.
- **Italy:** this layer shows Sigonella, Aviano, Pratica di Mare, Pantelleria, Steadfast Noon over the Tyrrhenian, and the Italian detachments in Lithuania and at Taif.
- **Black Sea / Ukraine:** NATO ISR and P-8 patrols over the Bulgarian EEZ come at the same time as drone attacks on merchant ships near Sulina. They connect to the cargo, port and insurance layers.
- **Bases (basi-mondo.json, fissi.json):** curated items sit on the same airfields, so the "Nearby bases" chips will link them.

## Suggested display
Merge `aerei.json` `punti` into the 'air' layer. A small "snapshot HH:MM UTC" badge on items with `istantanea=1` would make clear they are not live. If the coordinator merges it into mobili.json, keep the `AE-S-`/`AE-C-` ids so later runs can replace the snapshot each day.

## Limits
- **The snapshot is one moment, once a day.** Most military aircraft fly with transponders off or without a broadcast position. 93 of 230 had no position. Absence means nothing, and a daily run misses most activity.
- **Owner is inferred.** It comes from the ICAO address block, so a foreign-registered airframe can be misattributed. The MLAT and TIS-B positions are less precise and are rated `media` reliability.
- **Base points are not sightings.** Curated items placed at a base show the departure or destination the source named. Many come from a single flight-tracking blog (ItaMilRadar) or from Misbar, and are rated `media` reliability.
- **Withdrawals are drawn as aircraft.** `stato: lasciata` items still appear with an aircraft symbol at the base that was left. The coordinator may prefer to hide them.
- **Ämari will not show.** The Turkish F-16 rotation at Ämari runs until 30 Nov, but its last dated report (1 Sep) is over 60 days old, so the map will not draw it. I found no newer dated report.
- **Duplicate skipped.** The RC-135U at Mildenhall (Misbar, 5 Nov) is not in my file because mobili.json already has it as X-20261105-07. Al Udeid tankers and Incirlik/Nevatim airlift are also only in mobili.json.
- **Not found in the window:** no new Bomber Task Force deployment (Guam, Diego Garcia, Morón) dated within the last 60 days. The latest I found was B-52s at RAAF Tindal on 1 Sep 2026 for BTF 26-3, which is just outside the window, so I left it out. I also found no autumn Iceland rotation.
- **No NOTAM or airspace-closure items** (see (c)).

## Workflow step (daily, `.github/workflows/aggiorna-dati.yml`, next to the other collectors)
```yaml
      - name: Aerei militari (ADS-B snapshot + curati)
        continue-on-error: true
        run: python3 raccolta/aerei/raccogli.py
```
