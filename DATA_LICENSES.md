# Data licenses

The code in this repository is MIT-licensed (see `LICENSE`). **The data is not.** Every file in `docs/data/` stays under the license of the sources it comes from, and several of those licenses are non-commercial (NC) or share-alike (SA). If you reuse a file, the conditions in the table below apply to you too.

Each JSON file also lists its sources in its own `fonti[]` field (name, link, license, data date). That field is the reference for each file. This table summarises it as of 9 November 2026.

*This is not legal advice. It is a summary of the licenses as the sources state them. A full review in Italian is in `report/licenze.md`.*

## Rules that apply to the whole folder

- **Non-commercial files** (marked NC below): personal, educational and research use only. Using them inside a company, including a port or logistics operator, needs the rights holder's permission or a replacement source.
- **Share-alike files** (marked SA, and ODbL): if you publish a modified version, it must carry the same license.
- **No open license** (marked "permission pending" or "terms of service"): the file is published as part of a personal, non-commercial analysis project, with attribution. Do not reuse it without asking the original author. The project will remove it if the rights holder asks.
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
| `fronte.json` | Map "Ucraina (2025)" by **@Majakovsk73** on Google My Maps | **No license declared: permission pending** | Do not reuse. Will be removed if the author asks |
| `fronte-storico.json` | **DeepStateMap** history API; ISW and AEI Critical Threats; Natural Earth | **DeepState license: no redistribution of API data without permission; permission pending.** ISW/CTP: copyright, cited | Do not reuse. Cite DeepStateMap with a link |
| `ucraina-storico.json` | *Massive Missile Attacks on Ukraine* by Petro Ivaniuk (Kaggle), via the Narretz/sbs-stats copy; curated strike points (Kyiv Independent, Wikipedia, press; coordinates from OSM Nominatim) | **CC BY-NC-SA 4.0** (series); facts with citation; ODbL coordinates | NC, attribution "Petro Ivaniuk, Kaggle", same license for derivatives |
| `eventi.json`, `mobili.json`, `ibrido.json`, `report.json`, `dossier.json` | Press, official statements and OSINT accounts, each point with its own `fonti[]` | Facts with citation | Text is the project's own |
| `ai.json` | Epoch AI (CC BY 4.0), company statements | CC BY 4.0; facts with citation | Attribute Epoch AI |
| `notizie.json` | Google News RSS and official feeds (UKMTO, JMIC, MARAD and others) | Headlines and links; articles belong to their publishers | Headline, date and link only |
| `analisti.json` | YouTube RSS feeds of 5 channels | Content belongs to the authors (all rights reserved) | Title, short description and link only |
| `manifest.json` | Project file | MIT (part of the code) | None |

## Contact

If you hold rights in any of this data and want it credited differently or removed, open an issue in this repository.
