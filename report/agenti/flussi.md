# Agente FLUSSI, NOLI E SANZIONI — rapporto del 9 novembre 2026

Script: `raccolta/flussi/raccogli.py` (solo libreria standard, nessuna chiave; `solo=portwatch,noli,gpr,sanzioni` per eseguire una parte). Eseguito il 9/11/2026 alle 19 UTC circa, nessun errore.
File prodotti: `docs/data/portwatch.json` (900 KB), `docs/data/noli.json` (6 KB), `docs/data/gpr.json` (213 KB), `docs/data/sanzioni-navi.json` (1 MB).

## Fonti provate

| Fonte | Esito | Licenza | Ultimo dato |
|---|---|---|---|
| IMF PortWatch, ArcGIS `Daily_Chokepoints_Data`, `Daily_Ports_Data`, `PortWatch_*_database` (services9.arcgis.com) | funziona, senza chiave | dati pubblici FMI, citare «IMF PortWatch» | 1/11/2026 (stretti), 30/10/2026 (porti) |
| Drewry World Container Index (pagina pubblica settimanale) | funziona, letto dal testo (una volta ha risposto 429: lo script riprova) | © Drewry, si cita il valore | 5/11/2026 |
| Freightos FBX (pagina «Terminal», dati incorporati) | funziona: circa 3 mesi di serie settimanale e 13 rotte | © Freightos | 6/11/2026 |
| SCFI, Shanghai Shipping Exchange (endpoint JSON `currentIndex`) | solo il composito; le rotte richiedono registrazione | © SSE | 6/11/2026 |
| CCFI, Shanghai Shipping Exchange (stesso endpoint) | funziona, con 12 rotte (Europa e Mediterraneo comprese) | © SSE | 6/11/2026 |
| Baltic Dry Index | nessuna fonte ufficiale gratuita; ultimo valore da Trading Economics (CFD) | © Baltic Exchange / TE: solo l'ultimo valore | 9/11/2026 |
| GPR di Caldara e Iacoviello, file Stata `.dta` giornaliero e mensile (gli `.xls` sono BIFF, illeggibili senza librerie) | funziona, lettore `.dta` scritto in Python puro | dati liberi per la ricerca, citare | 2/11/2026 (giornaliero), ottobre 2026 (mensile) |
| OFAC SDN XML (sanctionslistservice.ofac.treas.gov) | funziona | pubblico dominio | 6/11/2026 |
| UK Sanctions List FCDO, CSV (sostituisce la lista OFSI) | funziona, con data di designazione e bandiera | Open Government Licence v3 | 3/11/2026 |
| UE: navi dagli atti in Gazzetta ufficiale (allegato XLII reg. 833/2014 ecc.), trascritte da OpenSanctions `eu_journal_sanctions` | funziona; la lista consolidata FSF dell'UE non contiene le navi | **CC BY-NC 4.0**: solo uso non commerciale (va bene per questo progetto, da citare) | 28/10/2026 |

Nessuna fonte richiede chiavi. Lo storico dei noli si costruisce a ogni esecuzione: lo script unisce i valori nuovi con quelli già nel file.

## Cosa contengono i file
- **portwatch.json**: 13 passaggi con le chiavi di `stretti.json` (PortWatch non misura i Dardanelli, il Canale di Sicilia e Tiran; per gli «Stretti danesi» misura solo l'Øresund) e 9 porti italiani (Venezia divisa in Lido e Malamocco). Per ognuno: media 7 giorni all'ultima data, stessa settimana di 1, 2 e 3 anni prima (52/104/156 settimane, stessi giorni della settimana), variazioni %, media 30 giorni, divisione per tipo di nave (petroliere, container, rinfuse, merci varie, ro-ro), portata lorda stimata, per i porti import/export in tonnellate stimate; serie giornaliere dal 1/1/2023 (totale e petroliere per gli stretti, chiamate totali per i porti), coordinate.
- **noli.json**: WCI (composito e 4 rotte, Shanghai–Genova compresa), FBX (serie e rotte), SCFI, CCFI, Baltic Dry; valore, data, variazione, storico.
- **gpr.json**: GPR giornaliero (totale, atti, minacce, medie a 7 e 30 giorni) e mensile (totale, atti, minacce, e per Italia, Russia, Ucraina, Israele, Arabia Saudita, Cina, Taiwan, USA, Egitto, Turchia), ultimi 5 anni.
- **sanzioni-navi.json**: 2.022 navi, unite per numero IMO: nome, altri nomi, bandiera (testo e ISO), tipo, chi sanziona con programma e data, società collegate (solo enti già nella lista OFAC), ambito (Russia, Iran, Corea del Nord…), una valutazione «flotta_ombra_probabile», più i conteggi.

## Fatti attuali (numeri dai file, fonte tra parentesi)
1. **Hormuz quasi chiuso**: 4,4 navi al giorno in media nella settimana 26/10–1/11/2026, contro 90,3 nella stessa settimana del 2025 (−95%); petroliere 1,4 contro 50,1 (−97%). Il crollo comincia a inizio marzo 2026: media mensile 78,3 a febbraio, 3,2 a marzo e mai sopra 13 da allora (IMF PortWatch).
2. **Bab el-Mandeb** 27,3 navi al giorno (−22% su un anno, −66% sul 2023 prima degli attacchi houthi, quando erano 79,6). Il calo riparte ad agosto 2026: media mensile da 36,6 a giugno a 27,4 ad agosto (PortWatch).
3. **Suez** 43,0 navi al giorno (+10% su un anno, petroliere +22%), ma ancora −43% sul 2023 (76,0). Valutazione: la crescita delle petroliere a Suez mentre Bab el-Mandeb cala fa pensare a traffico verso i porti sauditi del Mar Rosso (Yanbu), da verificare (PortWatch).
4. **Bosforo** 44,4 navi al giorno, −55% su un anno (98,4); petroliere −49%. Il calo è continuo da luglio (72,1 di media) a ottobre (49,4), insieme alla guerra sulle infrastrutture del Mar Nero. **Kerch**: 0 passaggi registrati da agosto (24,4 un anno fa). Possibile anche spegnimento dell'AIS: il dato dice che non ci sono segnali, non per forza che non ci siano navi (PortWatch).
5. **Rotte alternative**: Capo di Buona Speranza 92,0 al giorno (+5% su un anno, +89% sul 2023); Stretto di Luzon 112,9 (+72%); Malacca 202,7 (−15%), Gibilterra 131,6 (−5%), Øresund 38,7 (−21%), Panama 27,3 (−12%) (PortWatch).
6. **Porti italiani**, settimana 24–30/10/2026 contro un anno prima: Ravenna 5,6 chiamate al giorno (−40%, petroliere −50%), Venezia Lido 4,6 (−38%) e Malamocco 1,1 (−62%), Trieste 5,3 (−13%, petroliere −24%), Genova 8,9 (−4%), Livorno 6,4 (−3%), Gioia Tauro 5,0 (+2%), Augusta 4,7 (+15%, petroliere +33%), La Spezia 2,4 (+71%). Su 7 giorni i numeri sono piccoli: guardare anche la media a 30 giorni nel file (PortWatch).
7. **Noli container**: Drewry WCI 4.389 dollari per 40 piedi il 5/11/2026 (−1% sulla settimana), Shanghai–Genova 4.166 stabile, Shanghai–Rotterdam 3.615 (−2%); Drewry cita la ripresa dei transiti da Suez che accorcia i viaggi (Drewry). FBX globale 3.452 dollari il 6/11 (3.690 a metà agosto), Cina–Mediterraneo (FBX13) 4.324, Cina–Nord Europa (FBX11) 3.422 (Freightos). SCFI 3.633 punti il 6/11 (−1,5%); CCFI 1.925 (+2,3%), rotta Europa +1,5% (SSE).
8. **Rinfuse**: Baltic Dry 2.854 punti il 9/11/2026, +37% su un anno (Trading Economics, affidabilità media).
9. **GPR**: picco mensile del periodo a marzo 2026 con 330 (media 1985–2019 = 100), poi 253 ad aprile, 126 ad agosto, 151 a ottobre. Giornaliero: media 30 giorni 184,7 al 2/11/2026 contro 143,3 un anno prima. Quota di articoli sull'Italia: 0,59% a marzo 2026, 0,19% a ottobre (Caldara e Iacoviello).
10. **Sanzioni**: 2.022 navi sanzionate da almeno uno tra USA (1.570), Regno Unito (683) e UE (734); 275 da tutti e tre. 950 legate alla Russia, 679 all'Iran; bandiere più frequenti Panama (374), Russia (290), Iran (192), Cina (159), Barbados (101). Ultime designazioni datate: UE 24/7/2026, Regno Unito 8/10/2026; OFAC non pubblica la data (OFAC, FCDO, OpenSanctions).

## Collegamenti con gli altri livelli
- **Brent e TTF** (`prezzi.json`): il Brent passa da 66 dollari a inizio febbraio a 109 il 1° aprile e 114 il 3 maggio, mentre Hormuz va da 78 a 3 navi al giorno; il 9/11 è a 93,65 (+47% su un anno). Il TTF è a 82,33 euro/MWh (+164% su un anno): Hormuz porta circa il 20% del GNL mondiale (`stretti.json`, EIA). Il GPR mensile segue lo stesso profilo (330 a marzo). Sono andamenti paralleli, non una prova di causa.
- **Eventi della mappa** (`eventi.json`), 7–9 novembre: petroliera in fiamme presso Khasab (X-20261108-03), due petroliere su mine a est di Hormuz (GI-20261108-04), Velos Sapphire colpita (GI-20261108-05), tre petroliere colpite su una rotta «non autorizzata» (X-20261109-09), blocco USA dei porti iraniani (X-20261108-05). **PortWatch arriva solo al 1/11: questi eventi non sono ancora nei numeri**; il prossimo aggiornamento dirà se Hormuz scende sotto le 4 navi al giorno. Nel Mar Nero: nave colpita a sud-est di Odesa (GI-20261107-09), coerente con il calo del Bosforo. Nel Mar Rosso: missili houthi su Riad e Abqaiq (X-20261109-03/05), rischio per il traffico saudita di Yanbu e quindi per Suez.
- **Italia esposta**: Trieste (porto del petrolio per l'oleodotto TAL verso Germania e Austria) e Ravenna/Venezia (energia e rinfuse) mostrano i cali più forti; Augusta (raffinerie siciliane) cresce. Genova e Gioia Tauro (container) tengono. Il nolo Shanghai–Genova (WCI 4.166 dollari) è più alto del Shanghai–Rotterdam (3.615).
- **Flotta ombra**: le navi sanzionate con IMO si possono incrociare con le navi coinvolte negli eventi (nome/IMO negli eventi) e con i porti.

## Proposta per la mappa
- Sugli stretti di `stretti.json`: un'etichetta «navi al giorno, ultima settimana» con la variazione su un anno colorata (rosso sotto −20%, verde sopra +20%) e una piccola serie (totale e petroliere) nel riquadro dello stretto; per Suez e Bab el-Mandeb anche il confronto con il 2023.
- Porti italiani come punti con chiamate al giorno e variazione.
- Pannello «Noli» accanto ai Mercati: WCI, FBX, SCFI, CCFI, Baltic Dry con data e freccia.
- GPR come linea nel pannello Mercati, sovrapponibile a Brent e TTF.
- Sanzioni: tabella cercabile per IMO/nome; contatori per chi sanziona e per bandiera.

## Limiti
- PortWatch conta le navi con AIS acceso, con circa una settimana di ritardo; le navi della flotta ombra e quelle in zone di guerra spesso lo spengono: i cali di Hormuz, Kerch e Bosforo possono essere in parte sottostimati o sovrastimati. Tra gli stretti mancano Dardanelli, Canale di Sicilia e Tiran; per i danesi solo l'Øresund.
- Noli: nessuna serie storica gratuita; WCI e Baltic Dry sono letti dal testo delle pagine e possono rompersi se il testo cambia; il Baltic Dry viene da un CFD (affidabilità media). Le rotte FBX non hanno una data propria.
- GPR: è un indice di articoli di giornale, non di eventi; l'ultimo valore giornaliero è del 2/11.
- Sanzioni: OFAC senza date di designazione; i dati UE passano da OpenSanctions (CC BY-NC); bandiere spesso false o cambiate; «flotta_ombra_probabile» è una valutazione della mappa, non un'etichetta delle fonti.
