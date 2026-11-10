# Data licenses

The code in this repository is MIT-licensed (see `LICENSE`). **The data is not.** Every file in `docs/data/` stays under the license of the sources it comes from, and several of those licenses are non-commercial (NC) or share-alike (SA). If you reuse a file, the conditions in the table below apply to you too.

Each JSON file also lists its sources in its own `fonti[]` field (name, link, license, data date). That field is the reference for each file. This table summarises it as of 9 November 2026.

*This is not legal advice. It is a summary of the licenses as the sources state them. A full review in Italian is in `report/licenze.md`.*

## Rules that apply to the whole folder

- **Non-commercial files** (marked NC below): personal, educational and research use only. Using them inside a company, including a port or logistics operator, needs the rights holder's permission or a replacement source.
- **Share-alike files** (marked SA, and ODbL): if you publish a modified version, it must carry the same license.
- **No open license** (marked "permission not yet obtained" or "terms of service"): the file is published as part of a personal, non-commercial analysis project, with attribution. Do not reuse it without asking the original author. The project will remove it if the rights holder asks.
- Facts taken from press articles (events, dates, figures) are cited with a link and a short excerpt at most. The articles themselves belong to their publishers.

## File by file

| File | Main sources | License of the data | Conditions |
|---|---|---|---|
| `world.json`, `medio-oriente.json`, `labels.json` | Natural Earth | Public domain | None |
| `ferrovie.json` | Natural Earth railroads; corridors and incidents curated from cited sources | Public domain (network); facts with citation | None |
| `linee.json`, `condotte.json` | Global Energy Monitor, Global Oil and Gas Infrastructure Trackers | CC BY 4.0 | Attribute Global Energy Monitor |
| `terminali-gnl.json` | Global Energy Monitor, Global Gas Infrastructure Tracker / LNG Terminals | CC BY 4.0 | Attribute Global Energy Monitor |
| `nucleare.json` | Global Energy Monitor, Global Nuclear Power Tracker; IAEA facts via press | CC BY 4.0 | Attribute Global Energy Monitor |
| `gas-italia.json` | ENTSOG Transparency Platform; GEM coordinates | ENTSOG terms (free reuse with citation); CC BY 4.0 | Attribute ENTSOG and GEM |
| `rotte.json` | Benden (2022), Global Shipping Lanes v1.3.1, doi:10.5281/zenodo.6361763 | **CC BY-NC 4.0** (the most restrictive of the three licenses the author declares) | NC, attribution with DOI |
| `fissi.json`, `italia.json`, `iran.json`, `difesa.json` | World Port Index (NGA), OurAirports, Wikidata; dated press and analysis sources | Public domain / CC0; facts with citation | None for coordinates |
| `cavi.json` | TeleGeography Submarine Cable Map | **CC BY-NC-SA 3.0** | NC, attribution "TeleGeography", same license for derivatives |
| `cavi-incidenti.json` | Curated from press, one source per incident; cable ids from TeleGeography | Facts with citation; ids CC BY-NC-SA 3.0 | NC for the TeleGeography part |
| `rete-elettrica.json` | OpenStreetMap via OpenInfraMap vector tiles | **ODbL 1.0** | "© OpenStreetMap contributors", share-alike for the database |
| `interconnessioni.json` | Curated (Terna, ENTSO-E, press); PyPSA-Eur network; OSM | **ODbL 1.0** (geometry); facts with citation | Attribution OSM and PyPSA-Eur, share-alike |
| `navi.json` | Digitraffic / Fintraffic (CC BY 4.0); aisstream.io (terms of service); Global Fishing Watch (**CC BY-NC 4.0**); USNI News (facts) | Mixed | NC for the GFW part; attribution "Source: Fintraffic / digitraffic.fi, CC BY 4.0" |
| `portwatch.json` | IMF PortWatch (IMF and University of Oxford) | IMF terms: reuse with citation | Attribute "IMF PortWatch" |
| `noli.json` | Drewry WCI, Freightos FBX, Shanghai Shipping Exchange, Baltic Exchange (via Trading Economics) | **Proprietary indices**: values quoted with source and date | Do not reuse the series; cite the publishers |
| `gpr.json` | Caldara and Iacoviello, Geopolitical Risk Index | Free for research with citation | Cite Caldara and Iacoviello (2022), *American Economic Review* |
| `sanzioni-navi.json` | OFAC SDN (public domain); UK Sanctions List (OGL v3.0); EU vessels via OpenSanctions (**CC BY-NC 4.0**) | Mixed | NC for the EU part; "Contains public sector information licensed under the Open Government Licence v3.0" |
| `scorte.json` | GIE AGSI+, Eurostat (CC BY 4.0), EIA and USDA (public domain), IMF IRFCL | Mixed, all reusable with citation | Cite each source; IMF data non-commercial without permission |
| `paesi.json` | IMF WEO, World Bank (CC BY 4.0), SIPRI (non-commercial), OWID/Energy Institute (CC BY 4.0), Eurostat (CC BY 4.0), UN Comtrade | Mixed | NC for SIPRI values; cite each source |
| `calendario.json` | Fed, BLS, BEA, EIA, OFAC (public domain); ECB, BoE, BoJ, Eurostat; IFES ElectionGuide; Wikipedia | Facts (dates, official rates) with citation | None beyond citation |
| `stretti.json`, `stretti-dettaglio.json` | IEA (CC BY 4.0), EIA, Lloyd's List, Howden Re, press (around 100 cited sources) | Facts with citation | Text is the project's own; figures belong to the cited sources |
| `prezzi.json` | U.S. Treasury (public domain) for rates; **Yahoo Finance** for indices, stocks, futures, FX and crypto | Treasury: public domain. Yahoo: **no license, personal use only** | Do not reuse the Yahoo series. Indicative values for context, not official prices |
| `mercati.json` | Press and market sites, quoted values with links | Facts with citation | None beyond citation |
| `fronte.json` | Map "Ucraina (2025)" by **@Majakovsk73** on Google My Maps | **No license declared: permission not yet obtained** | Do not reuse. Will be removed if the author asks |
| `fronte-storico.json` | **DeepStateMap** history API; ISW and AEI Critical Threats; Natural Earth | **DeepState license: no redistribution of API data without permission; permission not yet obtained.** ISW/CTP: copyright, cited | Do not reuse. Cite DeepStateMap with a link |
| `ucraina-storico.json` | *Massive Missile Attacks on Ukraine* by Petro Ivaniuk (Kaggle), via the Narretz/sbs-stats copy; curated strike points (Kyiv Independent, Wikipedia, press; coordinates from OSM Nominatim) | **CC BY-NC-SA 4.0** (series); facts with citation; ODbL coordinates | NC, attribution "Petro Ivaniuk, Kaggle", same license for derivatives |
| `eventi.json`, `mobili.json`, `ibrido.json`, `report.json`, `dossier.json` | Press, official statements and OSINT accounts, each point with its own `fonti[]` | Facts with citation | Text is the project's own |
| `ai.json` | Epoch AI (CC BY 4.0), company statements | CC BY 4.0; facts with citation | Attribute Epoch AI |
| `notizie.json` | Google News RSS and official feeds (UKMTO, JMIC, MARAD and others) | Headlines and links; articles belong to their publishers | Headline, date and link only |
| `manifest.json` | Project file | MIT (part of the code) | None |

## Contact

If you hold rights in any of this data and want it credited differently or removed, open an issue in this repository.

| `docs/data/attacchi-russi.json` | Russian strikes in Ukraine: curated events (Kyiv Independent, Reuters, AP and others, cited per event) + per-oblast counts from P. Ivaniuk's dataset | CC BY-NC-SA 4.0 (inherited from the Ivaniuk dataset); events cited with link |

| `docs/data/italia.json` (10 command locations) | Coordinates from OpenStreetMap | ODbL 1.0 — © OpenStreetMap contributors |

### Added on 10 November 2026 (from each file's declared sources)

| File | Sources | Licence / terms |
|---|---|---|
| `docs/data/ai-mondo.json` | Epoch AI, AI data centers; Epoch AI, Data on AI chip imports; TOP500 | CC BY 4.0; ODbL 1.0 (© OpenStreetMap contributors); fatti con citazione |
| `docs/data/assicurazioni.json` | Joint War Committee (LMA/IUA), circolari JWLA e pagina pubbl; IUA, Joint War Committee Risk List (elenco delle circolari c; Reuters (via Insurance Journal, BusinessLive, MarineLink, Cl | citazione con link; citazione con link; testo non ripubblicato; dati dell'osservatorio |
| `docs/data/attacchi-analisti.json` | Clément Molin, canale Telegram pubblico @clement_molin; AMK Mapping, canale Telegram pubblico @AMK_Mapping; GeoNames (gazetteer: città e regioni di UA e RU) | CC BY 4.0; dati NASA, uso libero con citazione; diritti dell'autore: solo fatti, estratto <=160 caratteri e link al post |
| `docs/data/baltico-sicurezza.json` | Eventi curati con fonte per voce (raccolta/nord/sicurezza.js; docs/data/cavi-incidenti.json e ibrido.json (richiami per id; GPSJam (John Wiseman), dati ADS-B Exchange, celle H3 risoluz | citazione; nessuna licenza dichiarata: uso personale con citazione; vedi navi.json |
| `docs/data/basi-mondo.json` | OurAirports; Wikidata (coordinate P625); Wikipedia in inglese (descrizioni) | CC BY-SA 4.0; CC0; citazione con link; testi non copiati |
| `docs/data/bunker-emissioni.json` | Ship & Bunker, prezzi bunker per porto (serie della pagina p; MPA Singapore via data.gov.sg; Port of Rotterdam, bunker sales 2024-2026 | Singapore Open Data Licence; dati pubblici EEX, citare la fonte; documento pubblico Interreg Europe |
| `docs/data/commercio.json` | UN Comtrade, API pubblica preview (senza chiave); USGS Mineral Commodity Summaries 2026 (data release); EIA International Energy Data, bulk INTL | copyright WNA, uso informativo con citazione; pubblico dominio; pubblico dominio (USGS) |
| `docs/data/cyber-energia.json` | Voci curate a mano dall'agente CYBER-ENERGIA (una fonte per ; WindEurope, Wind energy in Europe - 2025 Statistics and the ; CERT Polska, CISA, SektorCERT, FE-DDIS, ESET, Mandiant, Sent | dati citati con fonte (report pubblico WindEurope); fatti con citazione; fatti con citazione delle fonti |
| `docs/data/eolico-filiera.json` | WindEurope, Wind energy in Europe - 2025 Statistics and the ; Port Esbjerg, 'Port Esbjerg expands by 570,000 square metres; offshoreWIND.biz, 'Dutch Terminal Equipped to Handle Two Off | (c) Navingo/offshoreWIND.biz: solo citazione di fatti con link; (c) WindEurope: rapporto pubblico, citazione con fonte; (c) editore/azienda: solo citazione di fatti con link |
| `docs/data/esposizione-nord.json` | Eurostat, Energy imports dependency (nrg_ind_id); IEEFA European LNG Tracker, maggio 2026 (quote del GNL per o; Global Energy Monitor via docs/data/terminali-gnl.json; inte | CC BY 4.0 (riuso Eurostat); citazione; dati pubblici con registrazione |
| `docs/data/health.json` | generated by raccolta/qualita/controlla_tutto.py | MIT (project output) |
| `docs/data/idrogeno.json` | Voci curate (comunicati, porti, stampa specializzata): fonte; IEA, Northwest European Hydrogen Monitor 2025; IEA, Global Hydrogen Review 2025 | CC BY 4.0; fatti citati con fonte; fonti pubbliche |
| `docs/data/investimenti.json` | Voci curate a mano da comunicati societari e governativi, Re | fatti con citazione |
| `docs/data/italia-impatti.json` | MASE, DGSAIE: prezzi medi settimanali dei carburanti (tutti ; Yahoo Finance, future Brent (BZ=F), TTF (TTF=F), cambio EUR/; GME, esiti del mercato elettrico (PUN Index GME) e del merca | CC BY 3.0 IT; CC BY 4.0; dati pubblici |
| `docs/data/minerali.json` | USGS Mineral Commodity Summaries 2026 (data release); EIA International Energy Data, bulk INTL; World Nuclear Association, World Uranium Mining Production | copyright WNA, uso informativo con citazione; pubblico dominio; pubblico dominio (USGS) |
| `docs/data/notizie-testate.json` | NBC News (Top); NBC News (World); ABC News (International) | articoli dell'editore: solo titolo, sommario del feed e link |
| `docs/data/offshore-nord.json` | EMODnet Human Activities: wind farms (poligoni e punti), pla; Wikipedia, List of offshore wind farms (proprietari e stato ; Tracciati da docs/data/rete-elettrica.json (OpenStreetMap, O | CC BY 4.0 (EMODnet); CC BY-SA 4.0; ODbL; GEM CC BY-NC-SA (uso personale non commerciale) |
| `docs/data/port-risk.json` | see file | see the fonti/sources field in the file; cite each source |
| `docs/data/porti-nord.json` | IMF PortWatch (FMI e Università di Oxford), Daily Ports Data; Autorità portuali e statistiche nazionali (traffico annuo, v | citazione di dati pubblicati; dati pubblici FMI; citare «IMF PortWatch» |
| `docs/data/rischio.json` | see file | see the fonti/sources field in the file; cite each source |
| `docs/data/simulatore.json` | Schede degli stretti dell'osservatorio; Prezzi di oggi di Brent e TTF (Yahoo Finance); Chiusure dei future Brent (BZ=F) e TTF (TTF=F), dicembre 202 | Yahoo Finance, uso informativo, non ufficiale: nel file si pubblicano solo medie |
| `docs/data/supply-chain-ai.json` | USGS, Mineral Commodity Summaries 2026; Voci curate a mano (stampa, società, governi, analisti); OpenStreetMap Nominatim (geocodifica una tantum) | ODbL 1.0; fatti citati con fonte e link per ogni voce; pubblico dominio (governo USA) |
| `docs/data/transit-times.json` | Benden, P. (2022) Global Shipping Lanes v1.3.1 (via docs/dat; Passage status (docs/data/stretti-dettaglio.json); IMF PortWatch chokepoint transits (docs/data/portwatch.json) | CC BY 4.0 / CC BY-SA / CC BY-NC 4.0 (declared differently in three places); pers; IMF public data, cite IMF PortWatch |
| `docs/data/webcam.json` | Elenco curato a mano (raccolta/webcam/webcam.json); Port of Rotterdam, mappa webcam (ArcGIS Webcams_v2); YouTube oEmbed (verifica canale e disponibilità) | endpoint pubblico; link pubblici del porto; solo link: le immagini restano dei rispettivi proprietari |
| `docs/data/wind-calendar.json` | RWE Thor project site; gCaptain (Reuters); offshoreWIND.biz (RWE purchase article recalling the stop) | (c) Navingo/offshoreWIND.biz: headlines and links only; (c) publisher: facts quoted with link; Open Government Licence v3.0 |
| `docs/data/aerei.json` | adsb.lol `/v2/mil` (© adsb.lol contributors, ODbL 1.0); adsb.fi open data (Data: adsb.fi, https://adsb.fi — personal non-commercial use); curated deployments from public press and flight-tracking blogs; airport coordinates from OurAirports (public domain) | ODbL 1.0 share-alike: this file is released under ODbL; adsb.fi non-commercial with attribution |
| `docs/data/mobili.json` | USNI News Fleet and Marine Tracker (facts with link); EUNAVFOR, navy press releases, Naval News and other outlets (facts with link) | facts quoted with link; positions are area-level estimates |
