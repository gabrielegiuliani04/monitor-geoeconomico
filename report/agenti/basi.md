# Basi militari nel mondo: rapporto dell'agente (9 novembre 2026)

File prodotto: `docs/data/basi-mondo.json`, con 181 basi, 0 errori e 4 avvisi.
Voci curate: `raccolta/basi/basi.json`.
Script: `raccolta/basi/raccogli.py`. Usa solo la libreria standard: valida le voci, cerca i duplicati, collega le basi agli altri livelli e confronta le coordinate.

Il file completa `fissi.json` (basi USA, NATO e Israele in Medio Oriente), `italia.json`, `iran.json` e `difesa.json`, e non li modifica. Per questo mancano di proposito alcune basi chieste dal compito che sono già lì:
- Aviano, Sigonella, Vicenza, Napoli, Gaeta e Niscemi (in `italia.json`);
- Camp Lemonnier, le forze francesi e la base italiana a Gibuti, Diego Garcia, Akrotiri, Dhekelia, Duqm, Incirlik, Kürecik, la base francese di Abu Dhabi e il comando turco in Qatar (in `fissi.json`).

Questo è un lavoro di analisi su fonti aperte, non operativo. Le forze presenti compaiono solo come ordini di grandezza già pubblicati; non ci sono dettagli su armi, reparti o difese oltre quanto riportato dalle fonti citate.

In questo testo **fatto** vuol dire un dato con fonte e data. **Valutazione** vuol dire un ragionamento dell'osservatorio sulle fonti citate.

---

## 1. Fonti provate

| Fonte | Esito | Licenza | Uso |
|---|---|---|---|
| OurAirports, `airports.csv` | funziona, senza chiave | pubblico dominio | coordinate di 83 basi aeree (codice ICAO o identificativo in `rif_coord`) |
| Wikidata, servizio SPARQL | funziona, senza chiave | CC0 | coordinate di 97 basi (Q-id in `rif_coord`) |
| Wikipedia, API e riassunti REST | funziona a tratti: risponde spesso con errore 429 (troppe richieste) | CC BY-SA 4.0 | descrizioni; circa 50 riassunti letti oggi, gli altri citati come link |
| Congressional Research Service, IF12389 (aprile 2026) | funziona con il download diretto; lo strumento di lettura web non risolve il dominio | pubblico dominio | Russia in Africa |
| Stampa e centri studi (Stars and Stripes, Meduza, Euromaidan Press, Africa Defense Forum/NGA Tearline, Al Jazeera, ITV, Euronews, Newsweek, Critical Threats, USNI News, The Star/AP) | funzionano | citazione con link | stato al 2026 |
| Associated Press (abcnews.com) | il testo non si legge con lo script | citazione con link | sostituita da Meduza ed Euromaidan per la Siria |

Nessuna fonte richiede una chiave. Lo script non scarica nulla nel giro normale. Con `--verifica-coordinate` scarica OurAirports (circa 12 MB) e interroga Wikidata. Se una delle due non risponde, lo salta con un avviso.

---

## 2. Cosa contiene il file

**Ogni punto ha:**
- nome, paese ospite (`paese`) e chi la usa (`appartenenza` e `utenti`);
- tipo: aerea, navale, terrestre, comando, radar o mista;
- stato: operativa, in costruzione, ridotta, lasciata o pianificata;
- anno, lat/lon, origine e precisione delle coordinate;
- forze, se pubblicate;
- `perche_conta`, e `vicino_a` con i nomi di `labels.json`;
- fonte, link, data, affidabilità, note e l'elenco completo delle fonti.

Per la mappa il campo `categoria` riprende le categorie esistenti (`base-aerea`, `base-navale`, `base-terrestre`, `comando`). Ne aggiunge due nuove: `radar` (radar, stazioni spaziali e di ascolto) e `base-mista`.

**Collegamenti calcolati dallo script dagli altri file:**
- `stretto_vicino`: il passaggio più vicino di `labels.json`, se entro 1.000 km;
- `rotta_vicina`: la rotta più vicina di `rotte.json`, entro 500 km, con distanza, tipo e passaggi che attraversa;
- `approdi_cavi_100km` e `approdi_cavi_esempi`: approdi di cavi sottomarini da `cavi.json`.

**Numeri del file:**
- Per utilizzatore principale: USA 44, Russia 35, Regno Unito 10, Cina 10, Francia 7, Turchia 4, India 3, Giappone 3, NATO 3. Il resto sono basi del paese ospite usate da alleati, per esempio i siti EDCA filippini o le basi baltiche.
- Per stato: 151 operative, 11 in costruzione, 9 lasciate, 7 ridotte, 3 pianificate.
- 85 basi sono all'estero rispetto a chi le usa.

**Coordinate:**
- 83 vengono da OurAirports e 97 da Wikidata. Il controllo del 9 novembre non ha trovato scarti oltre 1 km.
- 1 sola è stimata: Batanes, con un cerchio di 25 km.
- Dove Wikidata dà solo il centro di una città, la precisione dichiarata è di 3–10 km e la nota lo dice: Vladivostok, Zhanjiang, Dušanbe, Krychaŭ, Stettino e altre.

**Verifica:**
- 87 basi su 181 hanno almeno una fonte letta oggi (`verificata: true`).
- Le altre citano fatti consolidati (apertura, ruolo) con il link alla fonte, ma lo stato al 2026 non è stato riletto. Hanno affidabilità media o bassa, e la nota lo dice.

**Duplicati con gli altri livelli:**
- Nessun duplicato entro 5 km con lo stesso utilizzatore.
- 4 avvisi:
  - la base giapponese a Gibuti ha le stesse coordinate (quelle dell'aeroporto) di Camp Lemonnier e delle forze francesi in `fissi.json`; è tenuta, perché l'utilizzatore è diverso;
  - Camp de Gaulle e Abd al-Kuri hanno lo stato basato su fonti di oltre un anno fa, da ricontrollare.

---

## 3. La geografia delle basi per potenza

**Stati Uniti: una rete globale, con un nuovo baricentro.**

Fatti:
- In Europa la rete poggia sui comandi in Germania: EUCOM e AFRICOM a Stoccarda, l'Esercito a Wiesbaden, l'aviazione a Ramstein. A maggio 2026 in Germania c'erano circa 34.000 militari USA ([Stars and Stripes, 1° maggio 2026](https://www.stripes.com/theaters/europe/2026-05-01/trump-withdraw-5000-troops-germany-21550153.html)).
- La rete prosegue verso sud con Rota e Morón su Gibilterra e Souda Bay sul Mediterraneo orientale.
- Verso est ci sono gli scudi antimissile di Deveselu (2016) e Redzikowo (inaugurata dalla NATO il 13 novembre 2024).
- Nell'Indo-Pacifico la catena va da Corea e Giappone (Camp Humphreys, Kadena, Yokosuka) a Guam e all'Australia (Darwin, Tindal, Pine Gap). In mezzo ci sono i nove siti EDCA nelle Filippine: cinque dal 2016 e quattro dal 2023, tre dei quali rivolti a Taiwan ([PTV, aprile 2023](https://ptvnews.ph/ph-us-announce-4-new-edca-sites/)).
- In Africa la presenza si è ristretta al Corno (Gibuti, Kenya, Somalia).
- Nell'Artico conta Pituffik.

**Russia: due flotte chiuse e un'Africa al posto della Siria.**
- In patria le basi decisive sono le due uscite oceaniche: la Flotta del Nord (Severomorsk, Gadžievo, Olen'ja) e quella del Pacifico (Viljučinsk, Vladivostok). Le flotte del Baltico (Baltijsk, nell'exclave di Kaliningrad) e del Mar Nero (Sebastopoli, Novorossijsk) dipendono da stretti controllati da altri.
- All'estero ci sono:
  - un anello post-sovietico: Gyumri, la 201ª base in Tagikistan, Kant, Abcasia, Ossezia del Sud, Transnistria, Bielorussia;
  - la proiezione africana dell'Africa Corps: Libia, Mali, Niger, Burkina Faso, Repubblica Centrafricana.

**Cina: poche basi all'estero, molto vicine alle rotte.**
- Ha una sola base dichiarata all'estero, Gibuti (2017).
- Usa Ream, in Cambogia, dove le corvette cinesi stazionano dalla fine del 2023.
- Ha costruito tre isole artificiali con piste nelle Spratly (Fiery Cross, Subi, Mischief) e controlla Woody Island nelle Paracel.
- Valutazione: tutte guardano le rotte tra Malacca, il Mar Cinese Meridionale e il Mar Rosso. Altri punti (Coco in Myanmar, Bejucal a Cuba, l'antenna di Neuquén in Argentina) hanno legami cinesi documentati in modo diverso, e qui sono a bassa affidabilità.

**Regno Unito e Francia: basi residue di imperi, ma su passaggi chiave.**
- Il Regno Unito tiene:
  - Gibilterra;
  - le Falkland, con 1.000–2.000 militari ([Wikipedia](https://en.wikipedia.org/wiki/RAF_Mount_Pleasant));
  - Ascensione, Brunei, Kenya e Belize;
  - Cipro e Diego Garcia, che sono in `fissi.json`.
- La Francia, dopo il 2022, ha in Africa solo Gibuti (in `fissi.json`) e un campo condiviso in Gabon. Le resta la rete dei territori d'oltremare: La Riunione, Mayotte, Nuova Caledonia, Polinesia, Guyana.

**Potenze medie: Turchia, India, Giappone, Emirati.**
- La Turchia ha la rete estera più dinamica: Qatar (in `fissi.json`), Somalia, Libia occidentale, Cipro Nord, nord dell'Iraq.
- L'India si muove sull'Oceano Indiano: Agaléga dal 2024, Andamane e Nicobare all'imbocco di Malacca. Ha lasciato Ayni, in Tagikistan, nel 2022 (secondo la stampa indiana, 2025).
- Il Giappone ha la sua unica base estera a Gibuti e fortifica le isole sud-occidentali (Yonaguni, Mageshima).
- Gli Emirati hanno smontato Assab (2021) e convertito Berbera (2019). Restano piste attribuite a loro ma non rivendicate, su Mayun (Perim) e Abd al-Kuri, sul Bab el-Mandeb e il Golfo di Aden.

**NATO sul fianco est: da presenza simbolica a presidio.**

Gruppi tattici in tutti i paesi dal Baltico al Mar Nero:
- Lituania (Germania);
- Lettonia (Canada, ora brigata);
- Estonia (Regno Unito);
- Polonia (USA);
- Romania (Francia);
- Bulgaria (Italia);
- Slovacchia.

A questi si aggiungono il nuovo polo di Mihail Kogălniceanu sul Mar Nero e la polizia aerea del Baltico (Šiauliai, Ämari).

---

## 4. Cosa è cambiato dal 2022: 10 fatti

1. **La Russia in Siria è ridotta a centri di addestramento.** Il 9 agosto 2026 Mosca e Damasco hanno firmato un memorandum: la Siria riprende l'aeroporto di Hmeimim e il quarto molo commerciale di Tartus, e le basi russe diventano centri di addestramento congiunti entro tre mesi ([Meduza su SANA, 10 agosto 2026](https://meduza.io/en/news/2026/08/10/russia-and-syria-agree-to-turn-russian-military-bases-into-joint-training-centers); [Euromaidan Press, 11 agosto](https://euromaidanpress.com/2026/08/11/russias-syrian-foothold-shrinks-to-a-training-center-as-damascus-takes-back-the-airport-and-a-berth/)). Mosca non ha commentato. Nel file entrambe le basi sono «ridotte».
2. **La logistica russa si è spostata in Libia.** Secondo i dati NGA Tearline ripresi dall'[Africa Defense Forum (11 agosto 2026)](https://adf-magazine.com/2026/08/africa-corps-work-at-libyan-air-bases-raises-concerns/), la Russia lavora su sei basi aeree libiche. Maaten al-Sarra, abbandonata dal 2011, è stata riattivata da dicembre 2024 verso Sudan, Ciad e Sahel. Al-Khadim ha tre nuovi hangar nel 2025 e probabili caserme nel 2026.
3. **Il modello Africa Corps ha un limite.** All'inizio del 2026 c'erano fino a 2.500 russi in Mali e circa 1.500 nella Repubblica Centrafricana ([CRS, 8 aprile 2026](https://www.everycrsreport.com/files/2026-04-08_IF12389_eafb70071b5b5ecad891e918583c30947bf78996.html)). Il 27 aprile 2026 l'Africa Corps ha confermato il ritiro da Kidal ([NV su CNN](https://english.nv.ua/nation/cnn-reports-russian-setback-in-mali-exposed-wider-africa-role-50606846.html)). La base navale di Port Sudan, prevista dall'accordo del 2020, è sospesa secondo l'ambasciatore russo (fine 2025, CRS).
4. **La Francia ha chiuso le basi permanenti in Africa occidentale e centrale:**
   - Mali, agosto 2022;
   - Burkina Faso, 2023;
   - Niger, dicembre 2023;
   - Ciad, gennaio 2025;
   - Costa d'Avorio, 20 febbraio 2025;
   - Senegal, 17 luglio 2025, con circa 350 militari ([Le Temps](https://www.letemps.ch/articles/l-armee-francaise-quitte-le-senegal-et-signe-la-fin-de-sa-presence-permanente-en-afrique-de-l-ouest-et-centrale); [Le Soleil](https://lesoleil.sn/international/infos-afrique/bases-militaires-francaises-en-afrique-de-la-fermeture-a-la-dechirure/)).

   Restano Gibuti e un campo condiviso in Gabon.
5. **Gli USA hanno lasciato il Niger.** Più di 1.000 militari sono partiti nel 2024 e i russi sono arrivati nello stesso anno (CRS). La base dei droni di Agadez è passata al Niger.
6. **La Cina si è stabilita in Cambogia.** Le corvette cinesi stazionano a Ream dalla fine del 2023. A gennaio 2026 l'USS Cincinnati ha fatto la prima visita USA, ormeggiata a 150 metri da due navi cinesi ([The Star/AP, 24 gennaio 2026](https://www.thestar.com.my/aseanplus/aseanplus-news/2026/01/24/us-warship-makes-first-call-at-cambodia039s-chinese-renovated-naval-base)). Il 15 agosto 2026 Elbridge Colby ha incontrato a Phnom Penh il ministro della Difesa cambogiano ([China Global South, 23 agosto 2026](https://chinaglobalsouth.com/2026/08/23/cambodia-us-defense-ties-china-ream-naval-base/)).
7. **Il fianco est si è consolidato, ma gli USA si ritirano in parte.** La Germania stanzia la 45ª Brigata in Lituania: circa 4.800 militari a Rūdninkai entro il 2027 ([Stars and Stripes, 2024](https://stripes.com/theaters/europe/2024-08-20/new-nato-base-lithuania-14922162.html); [Euronews, febbraio 2026](https://euronews.com/2026/02/02/why-germany-is-stationing-a-bundeswehr-brigade-in-lithuania)). Gli USA, invece:
   - il 1° maggio 2026 hanno annunciato il ritiro di fino a 5.000 militari dalla Germania;
   - a maggio hanno cancellato la rotazione di una brigata corazzata in Polonia;
   - sono così tornati a tre brigate in Europa, il livello del 2021 ([Stars and Stripes, 20 maggio 2026](https://www.stripes.com/theaters/europe/2026-05-20/pentagon-europe-force-posture-changes-21727163.html)).
8. **L'Artico si è aperto agli USA.** L'accordo USA-Danimarca-Groenlandia del 22 settembre 2026 consente di ampliare Pituffik e di aprire aree di difesa a Narsarsuaq e Mestersvig ([ITV](https://www.itv.com/news/2026-09-22/us-to-build-two-new-military-bases-in-greenland-under-deal-with-denmark); [Euronews](https://www.euronews.com/2026/09/22/trump-signs-greenland-security-deal-allowing-us-to-expand-military-presence)).
9. **Diego Garcia è in sospeso.** Il trattato del 22 maggio 2025 dà la sovranità sulle Chagos a Mauritius e lascia la base al Regno Unito per 99 anni. Non è in vigore: la legge di ratifica è decaduta con la fine della sessione del Parlamento britannico, il 29 aprile 2026 ([Al Jazeera, 2 ottobre 2026](https://www.aljazeera.com/news/2026/10/2/uk-mauritius-chagos-sovereignty-deal-stalls-amid-fears-of-further-delays)). La base è in `fissi.json`; la nota è qui per il rapporto.
10. **I Caraibi sono tornati un teatro.** Roosevelt Roads, a Porto Rico, è stata riattivata nel 2025 per l'ammassamento contro il Venezuela, culminato nell'operazione del 3 gennaio 2026 ([CBS](https://www.cbsnews.com/news/u-s-reopens-shuttered-puerto-rico-naval-base-caribbean-military-buildup-continues)). Nel frattempo:
    - la Turchia ha portato F-16 a Mogadiscio (gennaio 2026) e ha prorogato la missione in Somalia fino al 2028 ([Critical Threats](https://www.criticalthreats.org/analysis/turkey-somalia-niger-africa-file-april-16-2026));
    - i lavori russi a Ochamchire, in Abcasia, si sono fermati all'inizio del 2026 ([Newsweek](https://www.newsweek.com/photos-show-work-grind-to-halt-at-secret-russian-base-12286620)).

---

## 5. Collegamenti con stretti, cavi e rotte

**Stretti.** Basi entro 300 km da un passaggio di `labels.json`, calcolate dallo script:

| Passaggio | Basi di questo file | Basi già in altri file |
|---|---|---|
| Bab el-Mandeb | Cina (118 km), Giappone (120), Chabelley USA (126), Mayun/Perim (7), Assab (97), Berbera (298) | in `fissi.json`: Camp Lemonnier, francesi e italiani a Gibuti |
| Stretto di Gibilterra | Gibilterra (27 km), Rota (101), Morón (134) | |
| Stretto di Luzon | Batanes (72), Camilo Osias (249), Lal-lo (273) | |
| Stretto di Kerch | Novorossijsk (112), Sebastopoli (254) | |
| Dardanelli e Bosforo | Alessandropoli (82 km dai Dardanelli), Novo Selo (272 dal Bosforo) | |

Valutazione: il Bab el-Mandeb è il punto del mondo con più potenze militari in 150 km (USA, Francia, Italia, Cina, Giappone, più le piste attribuite agli Emirati). È anche lo stretto che il rapporto `stretti.md` indica come il «secondo Hormuz» del 2026.

Altri passaggi sono presidiati da più lontano:
- su Malacca guardano Sembawang (Singapore), il comando delle Andamane, INS Baaz e le isole Coco;
- su Taiwan guardano Yonaguni (342 km) e Kadena;
- sugli Stretti danesi guardano Baltijsk e Gotland.

**Cavi.**
- 97 basi su 181 hanno almeno un approdo di cavo sottomarino entro 100 km.
- Le più dense sono Faslane (31 approdi), Singapore-Sembawang (19), Roosevelt Roads (14), Mactan (12), Gibilterra, Pearl Harbor e Kitsap (11), Kadena e Yokosuka (10).
- Valutazione: le basi navali stanno quasi sempre negli stessi porti dove arrivano i cavi. Un incidente su un cavo vicino a una base (`cavi-incidenti.json`) va letto anche come possibile atto ostile. Vale soprattutto nel Baltico (Baltijsk, Gotland) e a Taiwan.

**Rotte.**
- 19 basi stanno entro 50 km da una rotta di `rotte.json`.
- Tra le più vicine: Gibilterra (7 km dalla rotta principale Gibilterra-Sicilia), Mayun (6 km dalla rotta Bab el-Mandeb-Suez), Yokosuka (6 km), Mageshima (10 km), INS Kadamba (4 km) e Sembawang (42 km dalla rotta di Malacca).

**Oleodotti ed energia.** Non è un calcolo dello script, ma i collegamenti sono questi:
- Novorossijsk è insieme base della Flotta del Mar Nero e terminale del CPC kazako, che porta greggio anche in Italia;
- le basi russe in Libia stanno nel paese da cui parte il Greenstream;
- Hmeimim e Tartus sono vicine al terminale di Baniyas (in `fissi.json`).

---

## 6. Proposta per la mappa

- **Un livello «Basi nel mondo»**, spento di default, con un filtro per appartenenza (USA, Russia, Cina, Regno Unito, Francia, Turchia, NATO e alleati, altri). Ogni potenza ha il suo colore, e la forma del simbolo indica il tipo, come in `fissi.json`.
- **Stato in evidenza:**
  - le basi lasciate hanno il simbolo vuoto e grigio, con l'anno di chiusura: rendono visibile il ritiro francese e americano dal Sahel;
  - quelle in costruzione o pianificate hanno il bordo tratteggiato;
  - quelle ridotte sono semitrasparenti.
- **Cerchio di precisione** quando `precisione_km` è maggiore o uguale a 5, come per i punti stimati di `fissi.json`.
- **Scheda della base:**
  - nome, chi la usa, `perche_conta`, forze;
  - stretto più vicino con la distanza, approdi di cavi, rotta vicina;
  - le fonti, con il segno «da rileggere» se `verificata` è falsa.
- **Vista «Corno d'Africa»** con `fissi.json` e questo file insieme: è il caso più eloquente.

---

## 7. Limiti

- 94 voci su 181 non sono state rilette oggi su una fonte datata. Il blocco di Wikipedia (errore 429) ha impedito di leggere tutte le schede. Lo stato di queste voci viene da fatti consolidati fino al 2025 e va ricontrollato. Le prime da rileggere:
  - Camp de Gaulle in Gabon;
  - Rzeszów;
  - Mihail Kogălniceanu e la rotazione USA in Romania (le fonti non concordano sull'ottobre 2025);
  - Tindal;
  - Abd al-Kuri;
  - le basi russe nell'Artico.
- Le forze presenti sono indicate solo dove una fonte le pubblica, e sono ordini di grandezza. Fonti diverse danno numeri diversi (per esempio Pituffik: 150 o 200).
- Alcune coordinate sono quelle della città o dell'aeroporto vicino, non della base: la precisione è dichiarata in ogni punto. Krychau-6 (l'Oreshnik in Bielorussia) ha le coordinate della città. Le fonti non concordano nemmeno sul ruolo del sito: base permanente o tecnica.
- Mancano di proposito i punti senza coordinate affidabili: l'avamposto cinese in Tagikistan, il futuro spazioporto turco in Somalia, i siti USA a Panama.
- Le isole contese (Spratly, Paracel, Curili) e i territori occupati (Crimea, Abcasia, Ossezia del Sud, Transnistria, Cipro Nord) hanno come paese chi le controlla di fatto o lo stato riconosciuto, e la nota lo spiega. Non è una presa di posizione.
- Licenze: OurAirports e Wikidata sono liberi. Le descrizioni prese da Wikipedia sono riassunte, non copiate (CC BY-SA). Gli articoli di stampa sono citati con link. Nessuna fonte CC BY-NC.
