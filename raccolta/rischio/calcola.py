#!/usr/bin/env python3
"""Cruscotto del rischio: indicatori, stati e punteggi per 12 passaggi e 6 corridoi.

Legge solo i JSON già prodotti dagli altri script in docs/data/ (nessuna rete),
applica le regole descritte in report/metodo-rischio.md e scrive docs/data/rischio.json.
Salva lo storico dei punteggi in raccolta/rischio/storico.json per la tendenza a 7 giorni.

Solo libreria standard. Se un file o un campo manca, l'indicatore diventa "n.d." e lo
script prosegue: non deve mai fallire nel workflow giornaliero.

Uso:  python3 raccolta/rischio/calcola.py            (oggi = data UTC corrente)
      python3 raccolta/rischio/calcola.py 2026-11-09 (data di riferimento esplicita)
"""
import datetime as dt
import json
import math
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.normpath(os.path.join(QUI, "..", ".."))
DATI = os.environ.get("RISCHIO_DATI") or os.path.join(RADICE, "docs", "data")      # sostituibili per le prove
USCITA = os.path.join(DATI, "rischio.json")
STORICO = os.environ.get("RISCHIO_STORICO") or os.path.join(QUI, "storico.json")
SCENARI = os.path.join(QUI, "scenari.json")
METODO_LINK = "report/metodo-rischio.md"

# ---------------------------------------------------------------- regole generali
PUNTI = {"verde": 1, "giallo": 3, "rosso": 5}
# pesi delle quattro domande per asse (si rinormalizzano se una domanda è n.d.)
PESI_PROB = {"flussi": 0.35, "minaccia": 0.30, "clima": 0.15, "mercato": 0.20}
PESI_IMP = {"peso": 0.35, "alternative": 0.20, "scorte": 0.25, "costo": 0.20}
NOMI_GRUPPI = {
    "flussi": "I flussi calano?", "minaccia": "Ci sono attacchi o incidenti vicino?",
    "clima": "Il clima geopolitico peggiora?", "mercato": "Il mercato lo prezza?",
    "peso": "Quanto pesa ciò che passa?", "alternative": "Ci sono alternative?",
    "scorte": "Quanto cuscinetto c'è?", "costo": "Quanto costa già?",
}
SOGLIA_DISRUPTION = -50.0      # transiti ≤ −50% del riferimento: disruption in corso, P = 5
RAGGIO_KM = 150
FINESTRA_EVENTI = 30
FINESTRA_CAVI = 365
LIVELLI = [(20, "critico"), (12, "alto"), (6, "medio"), (0, "basso")]
SOGLIA_TENDENZA = 1.0          # variazione del punteggio (scala 1–25) per dire "in aumento/in calo"

NOMI_GPR = {"GPRC_SAU": "Arabia Saudita", "GPRC_EGY": "Egitto", "GPRC_TUR": "Turchia", "GPRC_UKR": "Ucraina",
            "GPRC_RUS": "Russia", "GPRC_TWN": "Taiwan", "GPRC_CHN": "Cina", "GPRC_ISR": "Israele", "GPRC_ITA": "Italia",
            "GPRC_USA": "Stati Uniti"}
ESITI_GIUDIZIARI = ("condann", "arrest", "processo", "sentenza")
CATEGORIE_EVENTO_ESCLUSE = {"esercitazione", "rischieramento", "avanzamento", "falso-allarme", "spionaggio"}
CATEGORIE_INTERRUZIONE = {"blackout", "chiusura-passaggio"}

# ---------------------------------------------------------------- utilità
ERRORI = []
_CACHE = {}


def carica(nome):
    """Legge docs/data/<nome>; None (con errore annotato) se manca o è illeggibile."""
    if nome in _CACHE:
        return _CACHE[nome]
    percorso = os.path.join(DATI, nome)
    try:
        with open(percorso, encoding="utf-8") as f:
            dati = json.load(f)
    except FileNotFoundError:
        ERRORI.append(f"{nome}: file mancante, indicatori collegati n.d.")
        dati = None
    except Exception as e:  # file corrotto o a metà scrittura
        ERRORI.append(f"{nome}: illeggibile ({e.__class__.__name__}), indicatori collegati n.d.")
        dati = None
    _CACHE[nome] = dati
    return dati


def data_file(nome):
    d = carica(nome)
    return (d or {}).get("aggiornato", "") if isinstance(d, dict) else ""


def giorno(s):
    return dt.date.fromisoformat(str(s)[:10])


def km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def taglia(serie, ritardo):
    """La serie com'era 'ritardo' giorni fa: toglie gli ultimi 'ritardo' giorni di dati."""
    serie = [p for p in (serie or []) if p and p[1] is not None]
    if not serie or ritardo <= 0:
        return serie
    if len(serie) >= 3:
        passi = sorted((giorno(serie[i][0]) - giorno(serie[i - 1][0])).days for i in range(len(serie) - 3, len(serie)))
        if passi[1] >= 25 and ritardo < 25:
            return serie  # serie mensile o annuale: una settimana fa il dato più recente era lo stesso
    limite = giorno(serie[-1][0]) - dt.timedelta(days=ritardo)
    return [p for p in serie if giorno(p[0]) <= limite]


def media_finestra(serie, fine, giorni):
    inizio = fine - dt.timedelta(days=giorni - 1)
    vals = [v for d, v in serie if inizio <= giorno(d) <= fine]
    return (sum(vals) / len(vals), len(vals)) if vals else (None, 0)


def media_periodo(serie, da, a):
    vals = [v for d, v in serie if giorno(da) <= giorno(d) <= giorno(a)]
    return (sum(vals) / len(vals), len(vals)) if vals else (None, 0)


def fmt(x, dec=1):
    if x is None:
        return "n.d."
    s = f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def corto(t, n):
    t = str(t or "")
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0].rstrip(",;:(") + "…"


def plur(n, uno, molti):
    return f"{n} {uno if n == 1 else molti}"


def pct(x):
    return "n.d." if x is None else (("+" if x > 0 else "") + fmt(x) + "%")


def classifica(valore, giallo, rosso, verso):
    """verso='basso_male': più basso è peggio; 'alto_male': più alto è peggio."""
    if valore is None:
        return "n.d."
    if verso == "basso_male":
        return "rosso" if valore <= rosso else "giallo" if valore <= giallo else "verde"
    return "rosso" if valore >= rosso else "giallo" if valore >= giallo else "verde"


def nd(nome, gruppo, motivo, fonte="", file=""):
    return {"nome": nome, "gruppo": gruppo, "valore": None, "testo": "n.d.", "stato": "n.d.",
            "soglie": {}, "fonte": fonte, "file": file, "data": "", "nota": motivo}


def ind(nome, gruppo, valore, testo, stato, soglie, fonte, link, file, data, nota="", unita="", tipo="dato"):
    return {"nome": nome, "gruppo": gruppo, "valore": None if valore is None else round(valore, 2),
            "unita": unita, "testo": testo, "stato": stato, "soglie": soglie, "fonte": fonte,
            "link": link, "file": file, "data": data, "tipo": tipo, "nota": nota}


# ---------------------------------------------------------------- indicatori: probabilità
def i_transiti(nome_pw, rif, ritardo, campo="n_total", etichetta=None):
    """Transiti PortWatch: media 7 giorni contro un riferimento.
    rif = 'anno' (stessi 7 giorni 52 settimane prima) oppure (da, a, descrizione) periodo fisso pre-crisi."""
    nome = etichetta or f"Transiti {nome_pw} (media 7 gg)"
    soglie = {"verde": "≥ −10% sul riferimento", "giallo": "tra −10% e −30%", "rosso": "< −30%",
              "disruption": "≤ −50%: disruption in corso, probabilità = 5"}
    pw = carica("portwatch.json")
    if not pw:
        return nd(nome, "flussi", "portwatch.json mancante", "IMF PortWatch", "portwatch.json")
    el = next((e for e in pw.get("elementi", []) if e.get("nome") == nome_pw), None)
    serie = taglia(((el or {}).get("serie") or {}).get(campo), ritardo)
    if not serie:
        return nd(nome, "flussi", f"nessuna serie {campo} per {nome_pw}", "IMF PortWatch", "portwatch.json")
    fine = giorno(serie[-1][0])
    m7, n = media_finestra(serie, fine, 7)
    if isinstance(rif, tuple):
        base, nb = media_periodo(serie, rif[0], rif[1])
        desc = rif[2]
    else:
        base, nb = media_finestra(serie, fine - dt.timedelta(days=364), 7)
        desc = "stessi 7 giorni di un anno prima"
    if m7 is None or not base:
        return nd(nome, "flussi", "riferimento non calcolabile", "IMF PortWatch", "portwatch.json")
    var = (m7 / base - 1) * 100
    stato = classifica(var, -10, -30, "basso_male")
    testo = f"{fmt(m7)} navi/g contro {fmt(base)} ({desc}): {pct(var)}"
    out = ind(nome, "flussi", var, testo, stato, soglie, "IMF PortWatch (FMI e Università di Oxford), dati AIS",
              "https://portwatch.imf.org/", "portwatch.json", fine.isoformat(),
              "Conta solo le navi con l'AIS acceso; dati con circa una settimana di ritardo.", "% sul riferimento")
    out["disruption"] = var <= SOGLIA_DISRUPTION
    out["media7"] = round(m7, 1)
    out["riferimento"] = round(base, 1)
    return out


def i_transiti_precalcolati(nome_pw, tipo_nave, confronto):
    """Usa le variazioni già calcolate da PortWatch per tipi di nave senza serie (es. container)."""
    nome = f"Portacontainer, {nome_pw} (media 7 gg)"
    soglie = {"verde": "≥ −10%", "giallo": "tra −10% e −30%", "rosso": "< −30%", "disruption": "≤ −50%"}
    pw = carica("portwatch.json")
    el = next((e for e in (pw or {}).get("elementi", []) if e.get("nome") == nome_pw), None)
    var = ((el or {}).get(f"var7_{confronto}_pct") or {}).get(tipo_nave)
    if var is None:
        return nd(nome, "flussi", "variazione non disponibile", "IMF PortWatch", "portwatch.json")
    m7 = (el.get("media7") or {}).get(tipo_nave)
    base = (el.get(f"media7_{'tre_anni_prima' if confronto == 'tre_anni' else 'anno_prima'}") or {}).get(tipo_nave)
    desc = "stessa settimana del 2023, prima degli attacchi houthi" if confronto == "tre_anni" else "un anno prima"
    out = ind(nome, "flussi", var, f"{fmt(m7)} portacontainer/g contro {fmt(base)} ({desc}): {pct(var)}",
              classifica(var, -10, -30, "basso_male"), soglie, "IMF PortWatch", "https://portwatch.imf.org/",
              "portwatch.json", el.get("ultima_data", ""), "Valore già calcolato nel file (nessuna serie per tipo): nello storico ricostruito resta uguale.",
              "% sul riferimento")
    out["disruption"] = var <= SOGLIA_DISRUPTION
    return out


def i_gas_flusso(punti, ritardo, nome):
    """Flusso ENTSOG (somma dei punti): media 7 giorni contro la media dei 365 giorni."""
    soglie = {"verde": "≥ −10% sulla media annua", "giallo": "tra −10% e −30%", "rosso": "< −30%",
              "disruption": "≤ −50%"}
    g = carica("gas-italia.json")
    if not g:
        return nd(nome, "flussi", "gas-italia.json mancante", "ENTSOG", "gas-italia.json")
    somma = {}
    for el in g.get("elementi", []):
        if el.get("id") in punti:
            for d, v in taglia((((el.get("flussi") or {}).get("entry") or {}).get("serie")), ritardo):
                somma[d] = somma.get(d, 0) + (v or 0)
    serie = sorted(somma.items())
    if len(serie) < 60:
        return nd(nome, "flussi", "serie troppo corta", "ENTSOG", "gas-italia.json")
    fine = giorno(serie[-1][0])
    m7, _ = media_finestra(serie, fine, 7)
    m365, _ = media_finestra(serie, fine, 365)
    var = (m7 / m365 - 1) * 100
    out = ind(nome, "flussi", var, f"{fmt(m7)} GWh/g contro una media annua di {fmt(m365)}: {pct(var)}",
              classifica(var, -10, -30, "basso_male"), soglie,
              "ENTSOG Transparency Platform (dati Snam Rete Gas)", "https://transparency.entsog.eu/",
              "gas-italia.json", fine.isoformat(), "A settembre 2026 il TransMed scese a circa −37% senza causa documentata.",
              "% sulla media annua")
    out["disruption"] = var <= SOGLIA_DISRUPTION
    out["media7"] = round(m7, 1)
    return out


def raccogli_eventi(oggi):
    """Tutti gli eventi datati con coordinate: eventi, ibrido, incidenti ai cavi, attacchi in Russia."""
    out = []
    for nome, chiave, fonte in (("eventi.json", "punti", "eventi"), ("ibrido.json", "punti", "ibrido")):
        for p in (carica(nome) or {}).get(chiave, []):
            out.append({**p, "_file": nome, "_tipo": fonte})
    for p in (carica("cavi-incidenti.json") or {}).get("elementi", []):
        out.append({**p, "_file": "cavi-incidenti.json", "_tipo": "cavi"})
    for p in (carica("ucraina-storico.json") or {}).get("elementi", []):
        out.append({**p, "_file": "ucraina-storico.json", "_tipo": "russia"})
    puliti = []
    for p in out:
        try:
            lat, lon = float(p.get("lat")), float(p.get("lon"))
            d = giorno(p.get("data_evento") or p.get("data"))
        except Exception:
            continue
        if d > oggi:
            continue
        puliti.append({**p, "_lat": lat, "_lon": lon, "_d": d})
    return puliti


def vicini(eventi, centri, oggi, giorni, raggio=RAGGIO_KM, tipi=None, filtro=None):
    da = oggi - dt.timedelta(days=giorni)
    sel = []
    for e in eventi:
        if e["_d"] < da or (tipi and e["_tipo"] not in tipi):
            continue
        if e.get("affidabilita") == "bassa" or e.get("categoria") in CATEGORIE_EVENTO_ESCLUSE:
            continue
        try:
            if e["_tipo"] != "cavi" and float(e.get("precisione_km") or 0) > raggio:
                continue  # coordinate troppo vaghe (centro di un paese o di un mare)
        except ValueError:
            pass
        if e["_tipo"] != "cavi" and any(k in str(e.get("nome", "")).lower() for k in ESITI_GIUDIZIARI):
            continue  # esito giudiziario di un fatto passato, non un evento sul terreno
        if filtro and not filtro(e):
            continue
        if any(km(e["_lat"], e["_lon"], la, lo) <= raggio for la, lo in centri):
            sel.append(e)
    return sel


def i_eventi(eventi, centri, oggi, ritardo, nome="Eventi entro 150 km (ultimi 30 gg)", filtro=None, soglie_n=(1, 3)):
    oggi_r = oggi - dt.timedelta(days=ritardo)
    sel = vicini(eventi, centri, oggi_r, FINESTRA_EVENTI, tipi={"eventi", "ibrido", "russia"}, filtro=filtro)
    if not any(carica(n) for n in ("eventi.json", "ibrido.json")):
        return nd(nome, "minaccia", "eventi.json e ibrido.json mancanti", "", "eventi.json")
    n = len(sel)
    stato = classifica(n, soglie_n[0], soglie_n[1], "alto_male")
    esempi = sorted(sel, key=lambda e: e["_d"], reverse=True)[:3]
    testo = plur(n, "evento", "eventi") + (": " + "; ".join(f"{e['_d'].isoformat()} {corto(e.get('breve') or e.get('nome', ''), 60)}" for e in esempi) if esempi else "")
    out = ind(nome, "minaccia", n, testo, stato,
              {"verde": f"meno di {soglie_n[0]}", "giallo": f"{soglie_n[0]}–{soglie_n[1] - 1}", "rosso": f"{soglie_n[1]} o più"},
              "UKMTO, CENTCOM, agenzie, OSINT (affidabilità alta o media)", "", "eventi.json, ibrido.json, ucraina-storico.json",
              oggi_r.isoformat(),
              "Esclusi eventi ad affidabilità bassa, esercitazioni, falsi allarmi. I file degli eventi coprono finestre recenti: "
              "un conteggio basso può voler dire poca raccolta.", "eventi")
    out["interruzioni_7g"] = [e.get("nome") for e in sel if e.get("categoria") in CATEGORIE_INTERRUZIONE
                              and e["_d"] >= oggi_r - dt.timedelta(days=7)]
    out["ids"] = [e.get("id") for e in esempi]
    return out


def i_cavi(eventi, centri, oggi, ritardo, raggio=300):
    nome = "Incidenti a cavi e condotte sottomarine (ultimi 12 mesi)"
    if not carica("cavi-incidenti.json"):
        return nd(nome, "minaccia", "cavi-incidenti.json mancante", "", "cavi-incidenti.json")
    oggi_r = oggi - dt.timedelta(days=ritardo)
    sel = vicini(eventi, centri, oggi_r, FINESTRA_CAVI, raggio=raggio, tipi={"cavi"})
    n = len(sel)
    testo = plur(n, "incidente", "incidenti") + (": " + "; ".join(f"{e['_d'].isoformat()} {corto(e.get('nome', ''), 70)} (causa: {corto(e.get('causa', ''), 70)})" for e in sel) if sel else "")
    return ind(nome, "minaccia", n, testo, classifica(n, 1, 2, "alto_male"),
               {"verde": "nessuno", "giallo": "1", "rosso": "2 o più"},
               "Stampa e operatori, curati dall'agente CAVI", "", "cavi-incidenti.json", oggi_r.isoformat(),
               f"Raggio {raggio} km. La causa è spesso solo un'ipotesi: un guasto naturale conta come un sabotaggio.", "incidenti")


def i_flotta_ombra():
    nome = "Petroliere sanzionate o della flotta ombra viste ora nel Baltico (AIS)"
    nv = carica("navi.json")
    if not nv:
        return nd(nome, "minaccia", "navi.json mancante", "", "navi.json")
    sel = [e for e in nv.get("elementi", []) if e.get("flotta_ombra_probabile") and
           any(k in (e.get("area") or "") for k in ("Baltico", "Finlandia", "danesi"))]
    n = len(sel)
    return ind(nome, "minaccia", n, plur(n, "nave", "navi") + " nella fotografia AIS di oggi", classifica(n, 10, 30, "alto_male"),
               {"verde": "meno di 10", "giallo": "10–29", "rosso": "30 o più"},
               "Digitraffic (Fintraffic), aisstream.io; incrocio con liste sanzioni", "https://www.digitraffic.fi/",
               "navi.json", (nv.get("aggiornato") or "")[:10],
               "Fotografia di un momento, non una media; copertura buona solo nel Golfo di Finlandia. Le soglie sono una "
               "valutazione da ricalibrare con lo storico. Rischio: ancore trascinate su cavi e condotte.", "navi")


def i_lanci_ucraina(ritardo):
    nome = "Missili e droni russi lanciati (7 gg contro la media dell'anno precedente)"
    u = carica("ucraina-storico.json")
    serie = taglia((((u or {}).get("serie") or {}).get("totale") or {}).get("lanciati"), ritardo)
    if not serie:
        return nd(nome, "minaccia", "ucraina-storico.json mancante o senza serie", "", "ucraina-storico.json")
    # la serie salta i giorni senza lanci: si somma per calendario
    fine = giorno(serie[-1][0])
    s7 = sum(v for d, v in serie if fine - dt.timedelta(days=6) <= giorno(d) <= fine) / 7
    s365 = sum(v for d, v in serie if fine - dt.timedelta(days=371) <= giorno(d) <= fine - dt.timedelta(days=7)) / 365
    r = s7 / s365 if s365 else None
    return ind(nome, "minaccia", r, f"{fmt(s7, 0)} al giorno contro {fmt(s365, 0)} di media nei 12 mesi precedenti (×{fmt(r, 2)})",
               classifica(r, 1.0, 1.5, "alto_male"), {"verde": "sotto la media (×<1)", "giallo": "×1–1,5", "rosso": "×1,5 o più"},
               "Aeronautica ucraina, dataset di Petro Ivaniuk (CC BY-NC-SA)",
               "https://www.kaggle.com/datasets/piterfm/massive-missile-attacks-on-ukraine", "ucraina-storico.json",
               fine.isoformat(), "Dichiarazioni di una parte; dal 13/8/2026 alcune cifre sui balistici non sono pubblicate.", "rapporto")


def i_ondate_rete(oggi, ritardo):
    nome = "Ondate di attacchi di massa contro la rete (ultimi 30 gg)"
    u = carica("ucraina-storico.json")
    if not u:
        return nd(nome, "minaccia", "ucraina-storico.json mancante", "", "ucraina-storico.json")
    oggi_r = oggi - dt.timedelta(days=ritardo)
    sel = [o for o in u.get("ondate_rete_ucraina", []) if oggi_r - dt.timedelta(days=30) <= giorno(o["data"]) <= oggi_r]
    n = len(sel)
    return ind(nome, "minaccia", n, plur(n, "ondata", "ondate") + (": " + "; ".join(f"{o['data']} {o['nome'][:60]}" for o in sel) if sel else ""),
               classifica(n, 1, 2, "alto_male"), {"verde": "nessuna", "giallo": "1", "rosso": "2 o più"},
               "Ondate curate dall'agente UCRAINA (DiXi Group, Ukrenergo, stampa)", "", "ucraina-storico.json",
               oggi_r.isoformat(), "Elenco curato a mano: dipende dall'aggiornamento dell'agente.", "ondate")


def i_eventi_rete_ua(eventi, oggi, ritardo):
    nome = "Attacchi e blackout sulla rete elettrica ucraina (ultimi 30 gg)"
    oggi_r = oggi - dt.timedelta(days=ritardo)
    if not carica("eventi.json"):
        return nd(nome, "minaccia", "eventi.json mancante", "", "eventi.json")
    sel = [e for e in eventi if e["_tipo"] == "eventi" and e.get("paese") == "UA"
           and (str(e.get("bersaglio", "")).startswith("energia") or e.get("categoria") == "blackout")
           and e.get("affidabilita") != "bassa" and oggi_r - dt.timedelta(days=30) <= e["_d"] <= oggi_r]
    n = len(sel)
    out = ind(nome, "minaccia", n, plur(n, "evento", "eventi") + f", di cui {sum(1 for e in sel if e.get('categoria') == 'blackout')} blackout",
              classifica(n, 1, 5, "alto_male"), {"verde": "nessuno", "giallo": "1–4", "rosso": "5 o più"},
              "Agenzie, DTEK, Ukrenergo, OSINT", "", "eventi.json", oggi_r.isoformat(),
              "Il file degli eventi copre una finestra recente: il conteggio è un minimo.", "eventi")
    out["interruzioni_7g"] = [e.get("nome") for e in sel if e.get("categoria") == "blackout"
                              and e["_d"] >= oggi_r - dt.timedelta(days=7)]
    return out


def i_gpr(codici, ritardo):
    """GPR per paese (mensile) contro la propria media degli ultimi 5 anni; se il paese manca, GPR globale (media 30 gg)."""
    g = carica("gpr.json")
    if not g:
        return [nd("Rischio geopolitico (GPR)", "clima", "gpr.json mancante", "Caldara e Iacoviello", "gpr.json")]
    soglie = {"verde": "sotto la propria media 5 anni (×<1)", "giallo": "×1–1,5", "rosso": "×1,5 o più"}
    fonte, link = "Caldara e Iacoviello, Geopolitical Risk Index", "https://www.matteoiacoviello.com/gpr.htm"
    out = []
    for c in codici:
        el = next((e for e in g.get("elementi", []) if e.get("id") == c), None)
        serie = taglia((el or {}).get("serie"), ritardo)
        if not serie:
            out.append(nd(f"GPR {c}", "clima", "serie assente", fonte, "gpr.json"))
            continue
        if c == "GPRD":
            fine = giorno(serie[-1][0])
            m30, _ = media_finestra(serie, fine, 30)
            media = sum(v for _, v in serie) / len(serie)
            r = m30 / media
            testo = f"media 30 gg {fmt(m30)} contro {fmt(media)} di media 5 anni (×{fmt(r, 2)})"
            nome, data = "Rischio geopolitico globale (GPR giornaliero, media 30 gg)", fine.isoformat()
        else:
            ultimo = serie[-1][1]
            media = sum(v for _, v in serie) / len(serie)
            r = ultimo / media if media else None
            testo = f"{fmt(ultimo, 2)} contro {fmt(media, 2)} di media 5 anni (×{fmt(r, 2)})"
            nome, data = f"Rischio geopolitico: {NOMI_GPR.get(c, c)}", serie[-1][0]
        out.append(ind(nome, "clima", r, testo, classifica(r, 1.0, 1.5, "alto_male"), soglie, fonte, link, "gpr.json", data,
                       "Conta gli articoli di 10 giornali su tensioni e guerre: misura l'attenzione, non il danno.", "rapporto"))
    return out


def serie_prezzo(pid, ritardo):
    p = carica("prezzi.json")
    el = next((s for s in (p or {}).get("serie", []) if s.get("id") == pid), None)
    return el, taglia((el or {}).get("serie"), ritardo)


def i_prezzo_90(pid, ritardo):
    el, serie = serie_prezzo(pid, ritardo)
    nome = f"{(el or {}).get('nome', pid)} contro la media 90 gg"
    if not serie:
        return nd(nome, "mercato", "prezzi.json mancante o serie assente", "Yahoo Finance", "prezzi.json")
    fine = giorno(serie[-1][0])
    m90, _ = media_finestra(serie, fine, 90)
    ultimo = serie[-1][1]
    dev = (ultimo / m90 - 1) * 100
    return ind(nome, "mercato", dev, f"{fmt(ultimo, 2)} {el.get('unita', '')} contro {fmt(m90, 2)} di media 90 gg: {pct(dev)}",
               classifica(dev, 5, 15, "alto_male"), {"verde": "meno di +5%", "giallo": "+5% / +15%", "rosso": "oltre +15%"},
               el.get("fonte", "Yahoo Finance"), el.get("link", ""), "prezzi.json", fine.isoformat(),
               "Segnale anticipatore: il mercato prezza un rischio nuovo. Future più vicino, non prezzo ufficiale.", "% sulla media 90 gg")


def i_prezzo_anno(pid, ritardo):
    el, serie = serie_prezzo(pid, ritardo)
    nome = f"{(el or {}).get('nome', pid)} contro un anno prima"
    if not serie:
        return nd(nome, "costo", "prezzi.json mancante o serie assente", "Yahoo Finance", "prezzi.json")
    fine = giorno(serie[-1][0])
    rif = [v for d, v in serie if giorno(d) <= fine - dt.timedelta(days=365)]
    ultimo = serie[-1][1]
    nota = "Il costo che famiglie e imprese pagano già."
    if rif:
        var = (ultimo / rif[-1] - 1) * 100
        testo = f"{fmt(ultimo, 2)} {el.get('unita', '')} contro {fmt(rif[-1], 2)} un anno prima: {pct(var)}"
    else:
        # prezzi.json pubblica solo ~3 mesi di serie: si usa la variazione a 1 anno calcolata dallo script dei mercati
        var = (el.get("var") or {}).get("1a")
        if var is None:
            return nd(nome, "costo", "manca il valore di un anno prima", "Yahoo Finance", "prezzi.json")
        testo = f"{fmt(el.get('ultimo'), 2)} {el.get('unita', '')}, {pct(var)} su un anno (variazione pubblicata in prezzi.json)"
        nota += " Variazione a 1 anno letta dal campo 'var.1a' (la serie pubblicata copre solo circa 3 mesi): nello storico ricostruito resta uguale."
        fine = giorno(el.get("data") or fine.isoformat())
    out = ind(nome, "costo", var, testo,
              classifica(var, 10, 40, "alto_male"), {"verde": "meno di +10%", "giallo": "+10% / +40%", "rosso": "oltre +40%"},
              el.get("fonte", "Yahoo Finance"), el.get("link", ""), "prezzi.json", fine.isoformat(), nota, "% su un anno")
    out["fisso"] = not rif
    return out


def _nolo(idx):
    n = carica("noli.json")
    return next((e for e in (n or {}).get("elementi", []) if e.get("id") == idx), None)


def i_premio_med():
    nome = "Premio del nolo Shanghai–Genova su Shanghai–Rotterdam (Drewry WCI)"
    el = _nolo("wci")
    rotte = (el or {}).get("rotte") or {}
    g, r = rotte.get("Shanghai-Genoa"), rotte.get("Shanghai-Rotterdam")
    if not g or not r:
        return nd(nome, "mercato", "rotte WCI non disponibili", "Drewry", "noli.json")
    prem = (g / r - 1) * 100
    return ind(nome, "mercato", prem, f"Genova {fmt(g, 0)} $ contro Rotterdam {fmt(r, 0)} $ per FEU: {pct(prem)}",
               classifica(prem, 5, 20, "alto_male"), {"verde": "meno di +5%", "giallo": "+5% / +20%", "rosso": "oltre +20%"},
               "Drewry World Container Index", el.get("link", ""), "noli.json", el.get("data", ""),
               "Il Mediterraneo dipende da Suez più del Nord Europa: un premio alto indica rischio sul Mar Rosso. "
               "Soglie: valutazione dell'osservatorio, da ricalibrare quando lo storico sarà lungo.", "% di premio")


def i_nolo_var(idx, rotta, etichetta):
    nome = f"Nolo {etichetta}: variazione settimanale"
    el = _nolo(idx)
    if not el:
        return nd(nome, "mercato", "noli.json mancante o indice assente", "", "noli.json")
    r = (el.get("rotte") or {}).get(rotta) or {}
    var = r.get("var_pct")
    if var is None and isinstance(r.get("var"), str):
        try:
            var = float(r["var"].replace("%", "").replace("+", ""))
        except ValueError:
            var = None
    if var is None:
        return nd(nome, "mercato", "variazione non pubblicata", el.get("fonte", ""), "noli.json")
    return ind(nome, "mercato", var, f"{fmt(r.get('valore'), 0)} ({el.get('unita', '')}), {pct(var)} sulla settimana",
               classifica(var, 3, 10, "alto_male"), {"verde": "meno di +3%", "giallo": "+3% / +10%", "rosso": "oltre +10%"},
               el.get("fonte", ""), el.get("link", ""), "noli.json", el.get("data", ""),
               "Una sola settimana: segnale rapido ma rumoroso.", "% sulla settimana")


def i_nolo_storico(idx, etichetta):
    nome = f"{etichetta} contro la media delle ultime settimane"
    el = _nolo(idx)
    st = (el or {}).get("storico") or []
    if len(st) < 4:
        return nd(nome, "mercato", "storico ancora troppo corto (meno di 4 settimane)", "", "noli.json")
    fine = giorno(st[-1][0])
    vals = [v for d, v in st if giorno(d) >= fine - dt.timedelta(days=90)]
    m = sum(vals) / len(vals)
    dev = (st[-1][1] / m - 1) * 100
    return ind(nome, "mercato", dev, f"{fmt(st[-1][1], 0)} $ contro {fmt(m, 0)} $ di media ({len(vals)} settimane): {pct(dev)}",
               classifica(dev, 5, 15, "alto_male"), {"verde": "meno di +5%", "giallo": "+5% / +15%", "rosso": "oltre +15%"},
               el.get("fonte", ""), el.get("link", ""), "noli.json", st[-1][0], "", "% sulla media")


# ---------------------------------------------------------------- indicatori: impatto
def i_strutturale(gruppo, punteggio, testo, fonte, link):
    stato = "rosso" if punteggio >= 4 else "giallo" if punteggio == 3 else "verde"
    nome = "Peso di ciò che passa" if gruppo == "peso" else "Mancanza di alternative"
    out = ind(nome, gruppo, punteggio, f"{punteggio}/5: {testo}", stato,
              {"verde": "1–2", "giallo": "3", "rosso": "4–5"}, fonte, link, "", "", "Giudizio strutturale dell'osservatorio sulle fonti citate: cambia di rado.",
              "punti 1–5", "valutazione")
    out["punti"] = punteggio
    return out


def i_quota_gas_italia(pid):
    nome = "Quota del gas entrato in Italia (12 mesi)"
    g = carica("gas-italia.json")
    q = next((x for x in (g or {}).get("quote_12_mesi", []) if x.get("id") == pid), None)
    if not q:
        return nd(nome, "peso", "gas-italia.json mancante", "ENTSOG", "gas-italia.json")
    v = q.get("quota_ingressi_pct")
    return ind(nome, "peso", v, f"{fmt(v)}% degli ingressi da gasdotti e GNL ({fmt(q.get('twh_12m'))} TWh)",
               classifica(v, 10, 25, "alto_male"), {"verde": "meno del 10%", "giallo": "10–25%", "rosso": "oltre il 25%"},
               "ENTSOG Transparency Platform (dati Snam)", "https://transparency.entsog.eu/", "gas-italia.json",
               (g.get("aggiornato") or "")[:10], "", "%")


def i_quota_paese(paese, chiave, nome):
    p = carica("paesi.json")
    el = next((e for e in (p or {}).get("elementi", []) if e.get("paese") == paese), None)
    x = ((el or {}).get("indicatori") or {}).get(chiave)
    if not x or not isinstance(x.get("valore"), dict):
        return nd(nome, "peso", "dato assente in paesi.json", "UN Comtrade", "paesi.json")
    v = x["valore"].get("max_pct")
    return ind(nome, "peso", v, f"{fmt(v)}% in valore ({x.get('anno')})", classifica(v, 10, 25, "alto_male"),
               {"verde": "meno del 10%", "giallo": "10–25%", "rosso": "oltre il 25%"}, x.get("fonte", ""), x.get("link", ""),
               "paesi.json", str(x.get("anno", "")), "Quota in valore dichiarata dall'importatore: approssima l'esposizione.", "%")


def _scarto_proprio(serie):
    """Scarto % dell'ultimo valore dalla media dello stesso giorno (±4) negli anni precedenti (almeno 2)."""
    if not serie:
        return None
    fine = giorno(serie[-1][0])
    vals = []
    for k in range(1, 6):
        try:
            rif = fine.replace(year=fine.year - k)
        except ValueError:
            rif = fine.replace(year=fine.year - k, day=28)
        vicino = sorted(((abs((giorno(d) - rif).days), v) for d, v in serie if abs((giorno(d) - rif).days) <= 4))
        if vicino:
            vals.append(vicino[0][1])
    if len(vals) < 2:
        return None
    m = sum(vals) / len(vals)
    return (serie[-1][1] / m - 1) * 100 if m else None


def i_scorte(sid, ritardo):
    """Scarto dalla media 5 anni calcolato da scorte.json (che usa lo storico completo).
    Nello storico ricostruito si applica allo scarto pubblicato la variazione calcolata sulla serie disponibile."""
    s = carica("scorte.json")
    el = next((e for e in (s or {}).get("elementi", []) if e.get("id") == sid), None)
    nome = (el or {}).get("nome", sid) + " contro la media 5 anni"
    if not el:
        return nd(nome, "scorte", "scorte.json mancante o voce assente", "", "scorte.json")
    piena = [p for p in (el.get("serie") or []) if p and p[1] is not None]
    serie = taglia(piena, ritardo)
    if not serie:
        return nd(nome, "scorte", "serie vuota", el.get("fonte", ""), "scorte.json")
    ult = el.get("ultimo") or {}
    pubblicato = (ult.get("media_5_anni") or {}).get("scarto_pct")
    media = (ult.get("media_5_anni") or {}).get("valore")
    if pubblicato is not None and serie[-1][0] == ult.get("data"):
        sc = pubblicato
    elif pubblicato is not None:
        a, b = _scarto_proprio(serie), _scarto_proprio(piena)
        sc = pubblicato + (a - b) if a is not None and b is not None else None
        media = None
    else:
        sc, media = _scarto_proprio(serie), None
    if sc is None:
        return nd(nome, "scorte", "media 5 anni non calcolabile", el.get("fonte", ""), "scorte.json")
    fine, ultimo = serie[-1][0], serie[-1][1]
    testo = f"{fmt(ultimo)} {el.get('unita', '')} il {fine}" + (f" contro {fmt(media)} di media 5 anni" if media else "") + f": {pct(sc)}"
    return ind(nome, "scorte", sc, testo, classifica(sc, -5, -15, "basso_male"),
               {"verde": "≥ −5% sulla media 5 anni", "giallo": "tra −5% e −15%", "rosso": "< −15%"},
               el.get("fonte", ""), el.get("link", ""), "scorte.json", fine, el.get("note", "") or "", "% sulla media 5 anni")


# ---------------------------------------------------------------- unità valutate
# Giudizi strutturali (peso, alternative): valutazioni dell'osservatorio su fonti citate.
SD = "docs/data/stretti-dettaglio.json"
U = [
    # --- 12 passaggi strategici
    dict(id="hormuz", nome="Stretto di Hormuz", tipo="passaggio", stretto="hormuz",
         flussi=[("pw", "Stretto di Hormuz", ("2025-01-01", "2025-12-31", "media del 2025, prima della guerra"), "n_total")],
         centri=[(26.6, 56.45), (25.12, 56.33)], gpr=["GPRC_SAU"], prezzi90=["brent", "ttf"],
         noli=[("var", "ccfi", "PERSIAN GULF/RED SEA", "CCFI Golfo Persico/Mar Rosso")],
         peso=(5, "circa 20 mb/g di petrolio (un quarto del petrolio via mare) e il 20% del GNL mondiale nel 2025", "IEA, Strait of Hormuz Factsheet (feb. 2026)", SD),
         alternative=(4, "gli oleodotti di aggiramento portano al massimo 5,5–7 mb/g; il GNL non ha alternative", "Report Hormuz e Mar Rosso, §3 (IEA, Baker Institute)", "report/hormuz-mar-rosso-2026-11.md"),
         quote=[("IT", "quota_gnl_golfo_persico", "GNL importato dall'Italia dal Golfo Persico")],
         scorte=["petrolio_emergenza_giorni_it", "petrolio_usa_spr"], costo=["brent", "ttf"],
         esposti=["Cina, India, Giappone, Corea del Sud (petrolio e GNL)", "Italia: GNL dal Qatar e prezzo di gas e gasolio",
                  "UE: prezzo TTF, stoccaggi bassi", "Settori: raffinazione, chimica e fertilizzanti (urea), trasporto aereo, industrie energivore"],
         livelli=["portwatch.json", "eventi.json", "prezzi.json", "noli.json", "scorte.json", "stretti-dettaglio.json"],
         calendario=["OPEC", "EIA", "IEA", "Iran", "Hormuz"]),
    dict(id="bab-el-mandeb", nome="Bab el-Mandeb", tipo="passaggio", stretto="bab-el-mandeb",
         flussi=[("pw", "Bab el-Mandeb", ("2023-01-01", "2023-10-31", "media gen.–ott. 2023, prima degli attacchi houthi"), "n_total")],
         centri=[(12.6, 43.4), (14.8, 42.9)], gpr=["GPRC_SAU"], prezzi90=["brent"], noli=[("premio",)],
         peso=(4, "8,1 mb/g nel 2° trimestre 2026 per il greggio saudita deviato a Yanbu; con Suez circa il 12% del petrolio via mare", "EIA (via Rigzone); EIA Today in Energy", SD),
         alternative=(3, "rotta del Capo: circa 7.000 km e 14–24 giorni in più; SUMED fino a 2,5 mb/g", "stretti-dettaglio.json (alternative)", SD),
         scorte=["petrolio_emergenza_giorni_it"], costo=["brent"],
         esposti=["Arabia Saudita (export da Yanbu)", "Italia ed Europa mediterranea: container Asia–Europa e cavi dati", "Egitto (ricavi del Canale)",
                  "Settori: armatori e porti di trasbordo, manifattura che importa componenti dall'Asia"],
         livelli=["portwatch.json", "eventi.json", "noli.json", "cavi.json", "stretti-dettaglio.json"], calendario=["Houthi", "Mar Rosso", "Suez"]),
    dict(id="suez", nome="Canale di Suez", tipo="passaggio", stretto="suez",
         flussi=[("pw", "Canale di Suez", ("2023-01-01", "2023-10-31", "media gen.–ott. 2023, prima degli attacchi houthi"), "n_total")],
         centri=[(30.05, 32.53), (31.26, 32.3), (29.95, 32.55)], gpr=["GPRC_EGY"], prezzi90=["brent"], noli=[("premio",)],
         peso=(4, "dal 12 al 15% del commercio mondiale; principale via Asia–Mediterraneo per i porti italiani", "UNCTAD; SRM (Intesa Sanpaolo)", SD),
         alternative=(3, "rotta del Capo: circa 7.000 km e 14–24 giorni in più", "stretti-dettaglio.json (alternative)", SD),
         scorte=["petrolio_emergenza_giorni_it"], costo=["brent"],
         esposti=["Italia: Genova, Trieste, Gioia Tauro, La Spezia", "Egitto", "Nord Europa (tempi di consegna)", "Settori: logistica container, auto, moda e meccanica che importano dall'Asia"],
         livelli=["portwatch.json", "noli.json", "stretti-dettaglio.json"], calendario=["Suez", "Mar Rosso"]),
    dict(id="panama", nome="Canale di Panama", tipo="passaggio", stretto="panama",
         flussi=[("pw", "Canale di Panama", "anno", "n_total")], centri=[(9.15, -79.75)], gpr=["GPRD"], prezzi90=["hh"],
         noli=[("var", "fbx", "FBX03", "Cina–Costa Est USA (FBX03)")],
         peso=(2, "circa il 5% del commercio mondiale; esposizione diretta dell'Italia bassa", "EPRS (Parlamento europeo)", SD),
         alternative=(2, "Suez o Capo per GNL e GPL USA–Asia; land bridge ferroviario negli USA", "stretti-dettaglio.json (alternative)", SD),
         scorte=["grano_scorte_finali_us"], costo=["hh"],
         esposti=["Stati Uniti (container, soia e mais)", "Asia orientale (GNL e GPL USA)", "Italia: indiretta, via noli e prezzi agricoli"],
         livelli=["portwatch.json", "noli.json"], calendario=[]),
    dict(id="malacca", nome="Stretto di Malacca", tipo="passaggio", stretto="malacca",
         flussi=[("pw", "Stretto di Malacca", "anno", "n_total")], centri=[(2.6, 101.2), (1.25, 103.8), (4.5, 99.0)], gpr=["GPRD"],
         prezzi90=["brent"], noli=[("storico", "fbx", "FBX globale")],
         peso=(4, "23,2 mb/g di petrolio (29% del petrolio via mare); con lo Stretto di Taiwan quasi metà del commercio via mare", "Anadolu/IEA-EIA; IUMI", SD),
         alternative=(2, "Lombok e Sonda: circa 5 giorni in più per una VLCC", "stretti-dettaglio.json (alternative)", SD),
         scorte=["petrolio_emergenza_giorni_it"], costo=["brent"],
         esposti=["Cina, Giappone, Corea (petrolio)", "Italia e UE: merci Asia–Europa", "Settori: elettronica, tessile, beni di consumo"],
         livelli=["portwatch.json", "noli.json"], calendario=[]),
    dict(id="stretti-turchi", nome="Stretti turchi (Bosforo e Dardanelli)", tipo="passaggio", stretto="stretti-turchi",
         flussi=[("pw", "Bosforo", "anno", "n_total")],
         centri=[(41.1, 29.06), (40.2, 26.4), (46.5, 30.75), (44.7, 37.8)], gpr=["GPRC_TUR", "GPRC_UKR"], prezzi90=["brent"], noli=[],
         peso=(3, "3,7 mb/g di petrolio; Russia e Ucraina il 27% dell'export di grano; greggio kazako CPC, terzo fornitore dell'Italia", "Anadolu/IEA-EIA; S&P Global; UN Comtrade (paesi.json)", SD),
         alternative=(4, "per il greggio CPC non c'è un'alternativa vera", "stretti-dettaglio.json (alternative)", SD),
         scorte=["petrolio_emergenza_giorni_it", "grano_scorte_finali_wd"], costo=["brent"],
         esposti=["Italia: raffinerie (greggio CPC kazako, 12,5% del greggio importato nel 2025)", "Importatori di grano di Nord Africa e Medio Oriente",
                  "Ucraina e Russia (export)", "Settori: raffinazione, molitoria"],
         livelli=["portwatch.json", "eventi.json", "ucraina-storico.json", "paesi.json"], calendario=["Russia", "Ucraina"]),
    dict(id="gibilterra", nome="Stretto di Gibilterra", tipo="passaggio", stretto="gibilterra",
         flussi=[("pw", "Stretto di Gibilterra", "anno", "n_total")], centri=[(35.97, -5.55)], gpr=["GPRD"], prezzi90=["ttf"],
         noli=[("var", "fbx", "FBX13", "Cina–Mediterraneo (FBX13)")],
         peso=(4, "132–135 transiti al giorno; porta del GNL statunitense che ha sostituito quello qatarino in Italia", "El Estrecho Digital; stretti-dettaglio.json", SD),
         alternative=(5, "nessuna alternativa marittima per il Mediterraneo occidentale", "stretti-dettaglio.json (alternative)", SD),
         scorte=["gas_stoccaggio_pct_it"], costo=["ttf"],
         esposti=["Italia e Spagna: GNL atlantico e container", "Marocco (Tanger Med)", "Settori: porti di trasbordo"],
         livelli=["portwatch.json", "gas-italia.json"], calendario=[]),
    dict(id="stretti-danesi", nome="Stretti danesi", tipo="passaggio", stretto="stretti-danesi",
         flussi=[("pw", "Stretti danesi", "anno", "n_total")], centri=[(55.5, 11.3), (57.7, 10.6), (55.6, 12.7)],
         gpr=["GPRC_RUS"], prezzi90=["brent"], noli=[], minaccia_extra=["flotta_ombra"],
         peso=(3, "4,9 mb/g di petrolio, circa un terzo dell'export russo via mare; per l'UE rischio soprattutto ambientale e di sicurezza", "Anadolu/IEA-EIA; gCaptain", SD),
         alternative=(4, "il petrolio russo del Baltico non ha alternative marittime", "stretti-dettaglio.json (alternative)", SD),
         scorte=["petrolio_usa_spr", "petrolio_emergenza_giorni_nl"], costo=["brent"],
         esposti=["Danimarca (controlli e rischio ambientale)", "Paesi Bassi e Germania: porti del Mare del Nord", "Russia (export)",
                  "Settori: assicurazioni marittime, pesca e turismo costiero"],
         livelli=["portwatch.json", "navi.json", "sanzioni-navi.json"], calendario=["sanzion", "NATO", "Russia"]),
    dict(id="taiwan", nome="Stretto di Taiwan", tipo="passaggio", stretto="taiwan",
         flussi=[("pw", "Stretto di Taiwan", "anno", "n_total")], centri=[(24.4, 119.6), (25.6, 120.2), (23.2, 119.4)],
         gpr=["GPRC_TWN", "GPRC_CHN"], prezzi90=[], noli=[("storico", "fbx", "FBX globale")], cavi=True,
         peso=(5, "oltre un quinto del commercio marittimo mondiale; quasi metà delle portacontainer è passata dallo stretto", "CSIS ChinaPower; Bloomberg", SD),
         alternative=(2, "rotta a est di Taiwan: circa tre giorni di ritardo", "stretti-dettaglio.json (alternative)", SD),
         scorte=[], costo=[],
         esposti=["Cina, Giappone, Corea, Taiwan", "UE e Italia: elettronica, auto, macchinari", "Settori: elettronica, automotive"],
         livelli=["portwatch.json", "cavi-incidenti.json", "gpr.json"], calendario=["Taiwan", "APEC"]),
    dict(id="capo", nome="Capo di Buona Speranza", tipo="passaggio", stretto="capo",
         flussi=[("pw", "Capo di Buona Speranza", "anno", "n_total")], centri=[(-34.36, 18.47)], gpr=["GPRD"], prezzi90=["brent"],
         noli=[("var", "fbx", "FBX11", "Cina–Nord Europa (FBX11)")],
         peso=(3, "9,1 mb/g di petrolio e la rotta di riserva di Suez e Hormuz", "Anadolu/IEA-EIA", SD),
         alternative=(2, "è essa stessa l'alternativa: dipende dalla riapertura di Suez", "stretti-dettaglio.json", SD),
         scorte=["petrolio_emergenza_giorni_it"], costo=["brent"],
         esposti=["Nord Europa (Rotterdam) e porti atlantici", "Sudafrica", "Settori: armatori (giorni di navigazione in più)"],
         livelli=["portwatch.json", "noli.json"], calendario=[]),
    dict(id="canale-di-sicilia", nome="Canale di Sicilia", tipo="passaggio", stretto="canale-di-sicilia",
         flussi=[("gas", ["mazara", "gela"], "Gas da Mazara e Gela (media 7 gg)")], centri=[(37.3, 11.7), (37.67, 12.54), (37.05, 14.26)],
         gpr=["GPRD"], prezzi90=["ttf"], noli=[], cavi=True,
         peso=(4, "un terzo del gas italiano (TransMed), 29 cavi dati, il futuro ELMED", "gas-italia.json; cavi.md", SD),
         alternative=(4, "il gas algerino non ha un'altra via verso l'Italia: l'alternativa è altro GNL", "stretti-dettaglio.json (alternative)", SD),
         scorte=["gas_stoccaggio_pct_it"], costo=["ttf"],
         esposti=["Italia: gas, cavi dati (Mazara, Palermo, Catania)", "Malta, Tunisia", "Settori: termoelettrico, industria del gas, telecomunicazioni"],
         livelli=["gas-italia.json", "cavi.json", "cavi-incidenti.json", "interconnessioni.json"], calendario=["gas", "Algeria"]),
    dict(id="kerch", nome="Stretto di Kerch", tipo="passaggio", stretto="kerch",
         flussi=[("pw", "Stretto di Kerch", "anno", "n_total")], centri=[(45.3, 36.6)], gpr=["GPRC_RUS", "GPRC_UKR"], prezzi90=[], noli=[],
         peso=(2, "circa il 28% del grano esportato dalla Russia, circa il 6% del grano mondiale", "S&P Global su dati USDA", SD),
         alternative=(3, "porti russi di acque profonde e del Baltico, anch'essi colpiti", "stretti-dettaglio.json (alternative)", SD),
         scorte=["grano_scorte_finali_wd"], costo=[],
         esposti=["Russia (export di grano)", "Importatori di grano del Medio Oriente e dell'Africa", "Italia: indiretta, sul prezzo del grano"],
         livelli=["portwatch.json", "eventi.json"], calendario=["Russia"]),
    # --- 6 corridoi e infrastrutture
    dict(id="transmed", nome="TransMed Algeria–Tunisia–Italia", tipo="corridoio", stretto="canale-di-sicilia", lat=37.67, lon=12.54,
         flussi=[("gas", ["mazara"], "Gas TransMed a Mazara del Vallo (media 7 gg)")],
         centri=[(37.67, 12.54), (37.3, 11.7), (36.95, 11.0), (36.4, 9.0), (36.5, 8.0)], gpr=["GPRD"], prezzi90=["ttf"], noli=[], cavi=True,
         peso_dinamico=("mazara",),
         peso=(5, "un solo tubo sottomarino porta un terzo del gas italiano", "gas-italia.json (ENTSOG)", "docs/data/gas-italia.json"),
         alternative=(4, "solo più GNL, limitato dalla capacità dei rigassificatori (21,8 Mt/a)", "energia.md (GEM)", "report/agenti/energia.md"),
         scorte=["gas_stoccaggio_pct_it"], costo=["ttf"],
         esposti=["Italia: famiglie e industria (PSV legato al TTF)", "Algeria (Sonatrach, entrate)", "Tunisia (diritti di transito)",
                  "Settori: termoelettrico, ceramica, carta, vetro, chimica"],
         livelli=["gas-italia.json", "condotte.json", "scorte.json", "prezzi.json"], calendario=["gas", "Algeria", "Consiglio europeo"]),
    dict(id="baltico", nome="Baltico: cavi, condotte ed elettrodotti", tipo="corridoio", stretto="stretti-danesi", lat=58.0, lon=20.5,
         flussi=[("pw", "Stretti danesi", "anno", "n_total")],
         centri=[(59.8, 24.5), (59.9, 27.5), (57.4, 19.8), (56.5, 18.8), (55.2, 15.0), (54.5, 12.5), (55.5, 11.3)],
         gpr=["GPRC_RUS"], prezzi90=["ttf"], noli=[], cavi=True, minaccia_extra=["flotta_ombra"],
         peso=(3, "Estlink, Balticconnector, Baltic Pipe, NordBalt e 34 cavi dati: sicurezza energetica regionale (Finlandia, Baltici, Polonia, Danimarca)", "cavi.md (TeleGeography); interconnessioni.json", "report/agenti/cavi.md"),
         alternative=(3, "ridondanza parziale: Estlink 2 è rimasto fermo circa 6 mesi dopo il danno del 2024 (almeno 60 milioni di euro)", "cavi.md; elettricita.md", "report/agenti/cavi.md"),
         scorte=["gas_stoccaggio_pct_de", "gas_stoccaggio_pct_nl"], costo=["ttf"],
         esposti=["Finlandia, Estonia, Lettonia, Lituania (elettricità e dati)", "Polonia e Danimarca (Baltic Pipe)", "Germania e Paesi Bassi (stoccaggi bassi, prezzo del gas)",
                  "Settori: telecomunicazioni, data center nordici, assicurazioni marittime"],
         livelli=["cavi.json", "cavi-incidenti.json", "condotte.json", "interconnessioni.json", "navi.json", "ibrido.json"], calendario=["NATO", "sanzion", "Russia"]),
    dict(id="mar-rosso-container", nome="Mar Rosso: rotta container Asia–Europa", tipo="corridoio", stretto="bab-el-mandeb", lat=20.0, lon=38.5,
         flussi=[("pwc", "Bab el-Mandeb", "n_container", "tre_anni"), ("pwc", "Canale di Suez", "n_container", "tre_anni")],
         centri=[(12.6, 43.4), (14.8, 42.9), (16.5, 41.5), (21.4, 38.9), (27.5, 34.0)], gpr=["GPRC_SAU", "GPRC_EGY"], prezzi90=[],
         noli=[("premio",), ("var", "ccfi", "MEDITERRANEAN", "CCFI Mediterraneo")], cavi=True,
         peso=(4, "12–15% del commercio mondiale; tutti i 6 cavi attivi Italia–Asia passano dal Mar Rosso", "UNCTAD; cavi.md (TeleGeography)", SD),
         alternative=(3, "Capo di Buona Speranza: 14–24 giorni e circa 0,7 milioni di dollari in più a viaggio", "stretti-dettaglio.json (alternative)", SD),
         scorte=[], costo=[],
         esposti=["Italia: Gioia Tauro, Genova, Trieste, La Spezia", "Grecia e Spagna (Pireo, Valencia)", "Egitto",
                  "Settori: manifattura che importa componenti, grande distribuzione, auto (car carrier)"],
         livelli=["portwatch.json", "noli.json", "cavi.json", "eventi.json"], calendario=["Houthi", "Suez", "Mar Rosso"]),
    dict(id="gnl-qatar", nome="GNL del Qatar (Ras Laffan → Hormuz)", tipo="corridoio", stretto="hormuz", lat=25.91, lon=51.55,
         flussi=[("pw", "Stretto di Hormuz", ("2025-01-01", "2025-12-31", "media del 2025, prima della guerra"), "n_tanker")],
         centri=[(25.91, 51.55), (26.6, 56.45)], gpr=["GPRC_SAU"], prezzi90=["ttf"], noli=[],
         peso=(5, "77 Mt/a di liquefazione, quasi il 20% del GNL mondiale, senza uscita alternativa; forza maggiore dal 4 marzo 2026", "energia.md (GEM); IEA", "report/agenti/energia.md"),
         alternative=(5, "nessuna: solo il gasdotto Dolphin verso Emirati e Oman, con poca capacità libera", "IEA (report Hormuz §3)", "report/hormuz-mar-rosso-2026-11.md"),
         quote=[("IT", "quota_gnl_golfo_persico", "GNL importato dall'Italia dal Golfo Persico")],
         scorte=["gas_stoccaggio_pct_it", "gas_stoccaggio_pct_de", "gas_stoccaggio_pct_nl"], costo=["ttf"],
         esposti=["Italia (Adriatic LNG), Belgio, Polonia", "India, Pakistan, Bangladesh, Cina", "Germania e Paesi Bassi: stoccaggi più bassi",
                  "Settori: termoelettrico, fertilizzanti, chimica, industrie energivore"],
         livelli=["terminali-gnl.json", "portwatch.json", "scorte.json", "prezzi.json", "paesi.json"], calendario=["GNL", "LNG", "Qatar", "Consiglio europeo"]),
    dict(id="rete-ucraina", nome="Rete elettrica ucraina", tipo="corridoio", stretto=None, lat=49.0, lon=31.5,
         flussi=[], centri=[], ucraina=True, gpr=["GPRC_UKR", "GPRC_RUS"], prezzi90=[], noli=[],
         peso=(3, "per l'UE: interconnessione sincrona con ENTSO-E (import fino a 2,45 GW) e stabilità regionale; per l'Ucraina il danno è critico", "elettricita.md (DiXi Group, ENTSO-E)", "report/agenti/elettricita.md"),
         alternative=(4, "poche: generazione distribuita e import dall'UE, limitati dalla capacità di rete", "elettricita.md", "report/agenti/elettricita.md"),
         scorte=[], costo=[],
         esposti=["Ucraina (civili, industria)", "Moldova (rete collegata)", "Polonia, Slovacchia, Ungheria, Romania (export di elettricità)",
                  "Settori: utility europee, assicurazioni, ricostruzione"],
         livelli=["rete-elettrica.json", "ucraina-storico.json", "eventi.json", "nucleare.json", "fronte.json"], calendario=["Ucraina", "Russia", "sanzion"]),
    dict(id="chip-taiwan", nome="Catena dei chip di Taiwan", tipo="corridoio", stretto="taiwan", lat=24.78, lon=120.99,
         flussi=[("pw", "Stretto di Taiwan", "anno", "n_total")], centri=[(24.78, 120.99), (22.6, 120.3), (24.4, 119.6), (25.6, 120.2)],
         gpr=["GPRC_TWN", "GPRC_CHN"], prezzi90=[], noli=[("storico", "fbx", "FBX globale")], cavi=True,
         peso=(5, "in un blocco le aziende che dipendono dai chip di Taiwan perderebbero fino a 1.600 miliardi di dollari di ricavi l'anno", "Rhodium Group (2022), in stretti-dettaglio.json", SD),
         alternative=(5, "la produzione avanzata fuori da Taiwan è in avvio e ancora piccola (TSMC Arizona: N3 a volume nel 2027)", "dossier AI Stati Uniti (dossier.json)", "docs/data/dossier.json"),
         scorte=[], costo=[],
         esposti=["Stati Uniti (Nvidia, Apple, hyperscaler)", "UE e Italia: automotive, macchinari, elettronica", "Paesi Bassi (ASML: export verso Taiwan)", "Settori: AI e data center, auto, difesa"],
         livelli=["dossier.json", "prezzi.json", "cavi-incidenti.json", "portwatch.json"], calendario=["Taiwan", "APEC", "Nvidia"]),
]


# ---------------------------------------------------------------- calcolo
def media_pesata(indicatori, pesi):
    """Media dei punti per gruppo, poi media pesata dei gruppi disponibili. Restituisce (valore, pesi usati)."""
    per_gruppo = {}
    for x in indicatori:
        if x["stato"] == "n.d.":
            continue
        punti = x.get("punti", PUNTI[x["stato"]])
        per_gruppo.setdefault(x["gruppo"], []).append(punti)
    disp = {g: w for g, w in pesi.items() if g in per_gruppo}
    if not disp:
        return None, {}
    if pesi is PESI_PROB and not ({"flussi", "minaccia"} & set(disp)):
        return None, {}  # senza flussi né minacce la probabilità non si calcola dal solo clima o dal solo mercato
    tot = sum(disp.values())
    val = sum(w / tot * (sum(per_gruppo[g]) / len(per_gruppo[g])) for g, w in disp.items())
    for x in indicatori:  # peso effettivo di ciascun indicatore, per trasparenza
        if x["stato"] != "n.d." and x["gruppo"] in disp:
            x["peso"] = round(disp[x["gruppo"]] / tot / len(per_gruppo[x["gruppo"]]), 3)
            x["punti"] = x.get("punti", PUNTI[x["stato"]])
        elif x["stato"] == "n.d.":
            x["peso"] = 0
            x["punti"] = None
    return val, {g: round(w / tot, 3) for g, w in disp.items()}


def livello(p):
    return next(n for s, n in LIVELLI if p >= s)


def fisso(x):
    """Indicatore che non si può ricostruire nel passato (file con sola finestra recente o senza serie):
    nello storico ricostruito resta uguale al valore di oggi."""
    x["fisso"] = True
    return x


def valuta(u, oggi, eventi, ritardo=0, correnti=None):
    prob, imp = [], []
    for f in u.get("flussi", []):
        try:
            if f[0] == "pw":
                prob.append(i_transiti(f[1], f[2], ritardo, f[3],
                                       etichetta=("Petroliere e metaniere, " if f[3] == "n_tanker" else "Transiti, ") + f[1] + " (media 7 gg)"))
            elif f[0] == "pwc":
                prob.append(fisso(i_transiti_precalcolati(f[1], f[2], f[3])))
            elif f[0] == "gas":
                prob.append(i_gas_flusso(f[1], ritardo, f[2]))
        except Exception as e:
            prob.append(nd(str(f[1]), "flussi", f"errore di calcolo: {e}"))
    try:
        if u.get("ucraina"):
            prob += [i_lanci_ucraina(ritardo), i_ondate_rete(oggi, ritardo), fisso(i_eventi_rete_ua(eventi, oggi, ritardo))]
        else:
            prob.append(fisso(i_eventi(eventi, u["centri"], oggi, ritardo)))
            if u.get("cavi"):
                prob.append(i_cavi(eventi, u["centri"], oggi, ritardo))
            if "flotta_ombra" in u.get("minaccia_extra", []):
                prob.append(fisso(i_flotta_ombra()))
    except Exception as e:
        prob.append(nd("Eventi", "minaccia", f"errore di calcolo: {e}"))
    try:
        prob += i_gpr(u["gpr"], ritardo)
    except Exception as e:
        prob.append(nd("GPR", "clima", f"errore di calcolo: {e}"))
    for pid in u.get("prezzi90", []):
        try:
            prob.append(i_prezzo_90(pid, ritardo))
        except Exception as e:
            prob.append(nd(pid, "mercato", f"errore di calcolo: {e}"))
    for n in u.get("noli", []):
        try:
            prob.append(fisso(i_premio_med() if n[0] == "premio" else i_nolo_var(n[1], n[2], n[3]) if n[0] == "var" else i_nolo_storico(n[1], n[2])))
        except Exception as e:
            prob.append(nd("Noli", "mercato", f"errore di calcolo: {e}"))

    imp.append(i_strutturale("peso", *u["peso"]))
    if u.get("peso_dinamico"):
        imp.append(i_quota_gas_italia(u["peso_dinamico"][0]))
    for paese, chiave, nome in u.get("quote", []):
        imp.append(i_quota_paese(paese, chiave, nome))
    imp.append(i_strutturale("alternative", *u["alternative"]))
    for sid in u.get("scorte", []):
        try:
            imp.append(i_scorte(sid, ritardo))
        except Exception as e:
            imp.append(nd(sid, "scorte", f"errore di calcolo: {e}"))
    for pid in u.get("costo", []):
        try:
            imp.append(i_prezzo_anno(pid, ritardo))
        except Exception as e:
            imp.append(nd(pid, "costo", f"errore di calcolo: {e}"))

    if ritardo and correnti:  # storico ricostruito: gli indicatori non ricostruibili restano quelli di oggi
        oggi_per_nome = {x["nome"]: x for x in correnti["prob"] + correnti["imp"]}
        prob = [dict(oggi_per_nome[x["nome"]]) if x.get("fisso") and x["nome"] in oggi_per_nome else x for x in prob]
        imp = [dict(oggi_per_nome[x["nome"]]) if x.get("fisso") and x["nome"] in oggi_per_nome else x for x in imp]
        for x in prob + imp:
            x.pop("peso", None)
            if x.get("tipo") != "valutazione":
                x.pop("punti", None)

    p, pesi_p = media_pesata(prob, PESI_PROB)
    i, pesi_i = media_pesata(imp, PESI_IMP)
    disruption = [x for x in prob if x.get("disruption")]
    interruzioni = [n for x in prob for n in x.get("interruzioni_7g", [])]
    regola = None
    if disruption:
        regola = f"{disruption[0]['nome']}: {disruption[0]['testo']}"
    elif interruzioni:
        regola = f"interruzione confermata negli ultimi 7 giorni: {interruzioni[0]}"
    if p is not None and regola:
        p = 5.0
    p = round(p, 1) if p is not None else None
    i = round(i, 1) if i is not None else None
    s = round(p * i, 1) if p is not None and i is not None else None
    cop_p = sum(w for g, w in PESI_PROB.items() if any(x["gruppo"] == g and x["stato"] != "n.d." for x in prob)) if p is not None else 0
    cop_i = sum(w for g, w in PESI_IMP.items() if any(x["gruppo"] == g and x["stato"] != "n.d." for x in imp)) if i is not None else 0
    return dict(prob=prob, imp=imp, p=p, i=i, s=s, pesi_p=pesi_p, pesi_i=pesi_i, regola=regola,
                copertura=round((cop_p + cop_i) / 2, 2))


def perche(u, r, tend):
    frasi = []
    if r["p"] is None or r["i"] is None:
        return "Punteggio non calcolabile oggi: mancano i dati su flussi e minacce (vedi errori)."
    attivi = sorted([x for x in r["prob"] if x["stato"] in ("rosso", "giallo")],
                    key=lambda x: -(x.get("punti") or 0) * (x.get("peso") or 0))
    if r["regola"]:
        frasi.append(f"La disruption è già in corso ({r['regola']}): per regola la probabilità è 5.")
    elif attivi:
        a = attivi[:2]
        frasi.append(f"La probabilità ({fmt(r['p'])}/5) è spinta da " + " e da ".join(f"«{x['nome']}» ({x['testo']})" for x in a) + ".")
    else:
        frasi.append(f"Nessun indicatore anticipatore è in allerta: probabilità {fmt(r['p'])}/5.")
    alti = sorted([x for x in r["imp"] if x["stato"] in ("rosso",)], key=lambda x: -(x.get("peso") or 0))
    if alti:
        frasi.append(f"L'impatto ({fmt(r['i'])}/5) è alto per " + "; ".join(f"«{x['nome']}» ({corto(x['testo'], 140)})" for x in alti[:2]) + ".")
    else:
        frasi.append(f"L'impatto è contenuto ({fmt(r['i'])}/5): nessuna voce di impatto è in rosso.")
    n_nd = sum(1 for x in r["prob"] + r["imp"] if x["stato"] == "n.d.")
    if tend.get("prima") is not None:
        frasi.append(f"Rispetto a 7 giorni fa il punteggio è {tend['tendenza']} ({fmt(tend['prima'])} → {fmt(r['s'])})"
                     + (f"; {n_nd} indicatori sono n.d." if n_nd else "") + ".")
    elif n_nd:
        frasi.append(f"{n_nd} indicatori non sono disponibili oggi: il punteggio poggia su meno dati.")
    if r.get("copertura", 1) < 0.7:
        frasi.append(f"Attenzione: le domande con dati coprono solo il {round(r['copertura'] * 100)}% dei pesi.")
    return " ".join(frasi)


def cosa_osservare(u, r, oggi, scen):
    out = []
    for x in r["prob"]:
        if x["gruppo"] == "flussi" and x["stato"] != "n.d.":
            if x.get("disruption"):
                rif = x.get("riferimento")
                soglia = f" (circa {fmt(rif * 0.7)} navi/g)" if rif else ""
                out.append(f"Fine della disruption: «{x['nome']}» sopra −30% del riferimento{soglia} per due settimane di fila.")
            elif x["stato"] != "verde":
                out.append(f"{x['nome']}: oggi {pct(x['valore'])}; sotto −50% scatta la regola della disruption in corso.")
    for x in r["prob"]:
        if x["gruppo"] != "flussi" and x["stato"] == "giallo":
            out.append(f"{x['nome']}: oggi {corto(x['testo'], 90)}; diventa rosso con {x['soglie'].get('rosso', '')}.")
    for x in r["imp"]:
        if x["gruppo"] == "scorte" and x["stato"] in ("giallo", "rosso"):
            out.append(f"{x['nome']}: {corto(x['testo'], 110)}.")
    cal = carica("calendario.json")
    if cal and u.get("calendario"):
        import re
        kw = re.compile("|".join(u["calendario"]), re.I)
        prossimi = [e for e in cal.get("elementi", []) if oggi.isoformat() <= e.get("data", "") <= (oggi + dt.timedelta(days=30)).isoformat()
                    and kw.search(e.get("titolo", "") + " " + (e.get("note") or ""))]
        vis = set()
        for e in prossimi:
            chiave = e["titolo"].split(":")[0]
            if chiave in vis:
                continue
            vis.add(chiave)
            out.append(f"In agenda il {e['data']}: {e['titolo']} (calendario.json).")
            if len(vis) >= 3:
                break
    if scen:
        out.append(f"Scenari a 3 mesi: oggi i segnali sono più coerenti con lo scenario «{scen['prevalente']}» (raccolta/rischio/scenari.json).")
    return out[:8]


# ---------------------------------------------------------------- scenari: lettura automatica dei segnali
def metriche_scenari(oggi, eventi):
    m = {}

    def pw(nome):
        x = i_transiti(nome, "anno", 0)
        return x.get("media7"), x.get("valore")

    for chiave, nome in (("hormuz", "Stretto di Hormuz"), ("bab", "Bab el-Mandeb"), ("suez", "Canale di Suez"),
                         ("capo", "Capo di Buona Speranza"), ("danesi", "Stretti danesi")):
        try:
            m[f"transiti.{chiave}.media7"], m[f"transiti.{chiave}.var_anno"] = pw(nome)
        except Exception:
            pass
    for pid in ("brent", "ttf"):
        _, s = serie_prezzo(pid, 0)
        if s:
            m[f"prezzo.{pid}"] = s[-1][1]
    w = _nolo("wci")
    if w:
        m["noli.wci"] = w.get("valore")
        m["noli.wci.genova"] = (w.get("rotte") or {}).get("Shanghai-Genoa")
        prem = i_premio_med()
        m["noli.premio_genova_pct"] = prem.get("valore")
    gf = i_gas_flusso(["mazara"], 0, "TransMed")
    m["gas.mazara.media7"] = gf.get("media7")
    for sid in ("gas_stoccaggio_pct_it", "gas_stoccaggio_pct_de"):
        x = i_scorte(sid, 0)
        m[f"scorte.{sid}.scarto5"] = x.get("valore")
    unita = {x["id"]: x for x in U}
    m["eventi.mar_rosso.attacchi_navi_30g"] = len(vicini(eventi, unita["mar-rosso-container"]["centri"], oggi, 30,
                                                         tipi={"eventi"}, filtro=lambda e: str(e.get("bersaglio", "")).startswith("nave")))
    m["eventi.hormuz.30g"] = len(vicini(eventi, unita["hormuz"]["centri"], oggi, 30, tipi={"eventi", "ibrido"}))
    m["eventi.baltico.30g"] = len(vicini(eventi, unita["baltico"]["centri"], oggi, 30, tipi={"eventi", "ibrido", "russia"}))
    m["eventi.sicilia.30g"] = len(vicini(eventi, unita["transmed"]["centri"], oggi, 30, tipi={"eventi", "ibrido"}))
    m["cavi.baltico.12m"] = len(vicini(eventi, unita["baltico"]["centri"], oggi, 365, raggio=300, tipi={"cavi"}))
    m["cavi.baltico.30g"] = len(vicini(eventi, unita["baltico"]["centri"], oggi, 30, raggio=300, tipi={"cavi"}))
    m["cavi.sicilia.12m"] = len(vicini(eventi, unita["transmed"]["centri"], oggi, 365, raggio=300, tipi={"cavi"}))
    m["navi.flotta_ombra_baltico"] = i_flotta_ombra().get("valore")
    return m


def verifica(valore, op, soglia):
    if valore is None:
        return None
    if op == ">":
        return valore > soglia
    if op == ">=":
        return valore >= soglia
    if op == "<":
        return valore < soglia
    if op == "<=":
        return valore <= soglia
    if op == "tra":
        return soglia[0] <= valore <= soglia[1]
    return None


def leggi_scenari(oggi, eventi):
    try:
        with open(SCENARI, encoding="utf-8") as f:
            sc = json.load(f)
    except Exception as e:
        ERRORI.append(f"scenari.json non letto ({e.__class__.__name__}): niente lettura dei segnali")
        return {}, []
    m = metriche_scenari(oggi, eventi)
    letture = {}
    sintesi = []
    for blocco in sc.get("unita", []):
        righe = []
        for s in blocco.get("scenari", []):
            segnali = []
            for x in s.get("segnali", []):
                v = m.get(x["metrica"])
                ok = verifica(v, x["operatore"], x["soglia"])
                segnali.append({"descrizione": x["descrizione"], "metrica": x["metrica"], "valore": v,
                                "condizione": f"{x['operatore']} {x['soglia']}", "attivo": ok})
            valutabili = [g for g in segnali if g["attivo"] is not None]
            attivi = sum(1 for g in valutabili if g["attivo"])
            righe.append({"id": s["id"], "nome": s["nome"], "tipo": s["tipo"], "segnali_attivi": attivi,
                          "segnali_valutabili": len(valutabili),
                          "quota": round(attivi / len(valutabili), 2) if valutabili else None, "segnali": segnali})
        con_quota = [r for r in righe if r["quota"] is not None]
        prevalente = max(con_quota, key=lambda r: (r["quota"], r["tipo"] == "base")) if con_quota else None
        lettura = {"unita": blocco["unita"], "scenari": righe,
                   "prevalente": prevalente["nome"] if prevalente else "n.d.",
                   "nota": "Lettura automatica: quota di segnali di ciascuno scenario che oggi risultano veri. Non è una probabilità."}
        letture[blocco["unita"]] = lettura
        sintesi.append(lettura)
    return letture, sintesi


# ---------------------------------------------------------------- storico e tendenza
def leggi_storico():
    try:
        with open(STORICO, encoding="utf-8") as f:
            st = json.load(f)
        if isinstance(st.get("giorni"), list):
            return st
    except Exception:
        pass
    return {"nota": "Punteggi giornalieri del cruscotto del rischio. 'ricostruito': true = calcolato a posteriori "
                    "togliendo gli ultimi 7 giorni da ogni serie (valori senza serie tenuti uguali).", "giorni": []}


def salva_giorno(st, data, punteggi, ricostruito=False):
    st["giorni"] = [g for g in st["giorni"] if g.get("data") != data]
    st["giorni"].append({"data": data, "ricostruito": ricostruito, "unita": punteggi})
    st["giorni"].sort(key=lambda g: g["data"])
    st["giorni"] = st["giorni"][-400:]


def riferimento_7g(st, oggi):
    """Il giorno salvato più vicino a 7 giorni fa (tra 5 e 10 giorni prima)."""
    cand = [g for g in st["giorni"] if 5 <= (oggi - giorno(g["data"])).days <= 10]
    return min(cand, key=lambda g: abs((oggi - giorno(g["data"])).days - 7)) if cand else None


# ---------------------------------------------------------------- principale
def coord(u):
    if u.get("lat") is not None:
        return u["lat"], u["lon"]
    sd = carica("stretti-dettaglio.json")
    el = next((e for e in (sd or {}).get("elementi", []) if e.get("id") == u.get("stretto")), None)
    if el:
        return el.get("lat"), el.get("lon")
    return (u["centri"][0] if u.get("centri") else (None, None))


def prezzi_collegati(u):
    ids = []
    for k in ("prezzi90", "costo"):
        for p in u.get(k, []):
            if p not in ids:
                ids.append(p)
    return ids


def principale():
    oggi = giorno(sys.argv[1]) if len(sys.argv) > 1 else dt.datetime.now(dt.timezone.utc).date()
    eventi = raccogli_eventi(oggi)
    st = leggi_storico()

    risultati = {}
    for u in U:
        try:
            risultati[u["id"]] = valuta(u, oggi, eventi)
        except Exception as e:  # una sola unità rotta non deve fermare le altre
            ERRORI.append(f"{u['id']}: calcolo non riuscito ({e.__class__.__name__}: {e})")

    # storico: se manca un giorno intorno a 7 giorni fa, lo ricostruisce togliendo 7 giorni da ogni serie
    if not riferimento_7g(st, oggi):
        rif = {}
        for u in U:
            if u["id"] not in risultati:
                continue
            try:
                r7 = valuta(u, oggi, eventi, ritardo=7, correnti=risultati[u["id"]])
                rif[u["id"]] = {"p": r7["p"], "i": r7["i"], "s": r7["s"], "livello": livello(r7["s"]) if r7["s"] is not None else "n.d."}
            except Exception as e:
                ERRORI.append(f"{u['id']}: ricostruzione a 7 giorni non riuscita ({e})")
        salva_giorno(st, (oggi - dt.timedelta(days=7)).isoformat(), rif, ricostruito=True)
    base7 = riferimento_7g(st, oggi)

    letture, sintesi_scenari = leggi_scenari(oggi, eventi)
    unita, punteggi = [], {}
    for u in U:
        r = risultati.get(u["id"])
        if not r:
            continue
        prima = ((base7 or {}).get("unita") or {}).get(u["id"], {}).get("s")
        if r["s"] is None or prima is None:
            tend = {"tendenza": "n.d.", "prima": None}
        else:
            d = r["s"] - prima
            tend = {"tendenza": "in aumento" if d >= SOGLIA_TENDENZA else "in calo" if d <= -SOGLIA_TENDENZA else "stabile", "prima": prima}
        lat, lon = coord(u)
        punteggi[u["id"]] = {"p": r["p"], "i": r["i"], "s": r["s"], "livello": livello(r["s"]) if r["s"] is not None else "n.d."}
        indicatori = []
        for asse, lista in (("probabilita", r["prob"]), ("impatto", r["imp"])):
            for x in lista:
                x = {k: v for k, v in x.items() if k not in ("interruzioni_7g", "fisso")}
                x["asse"] = asse
                x["domanda"] = NOMI_GRUPPI.get(x["gruppo"], x["gruppo"])
                indicatori.append(x)
        unita.append({
            "id": u["id"], "nome": u["nome"], "tipo": u["tipo"], "lat": lat, "lon": lon,
            "probabilita": r["p"], "impatto": r["i"], "punteggio": r["s"],
            "livello": livello(r["s"]) if r["s"] is not None else "n.d.",
            "tendenza": tend["tendenza"], "punteggio_7g_fa": tend["prima"],
            "data_7g_fa": base7["data"] if base7 and tend["prima"] is not None else None,
            "storico_ricostruito": bool(base7 and base7.get("ricostruito")),
            "regola_disruption": r["regola"],
            "copertura": r["copertura"],
            "pesi_usati": {"probabilita": r["pesi_p"], "impatto": r["pesi_i"]},
            "indicatori": indicatori,
            "perche": perche(u, r, tend),
            "cosa_osservare": cosa_osservare(u, r, oggi, letture.get(u["id"])),
            "esposti": u["esposti"],
            "collegamenti": {"stretto": u.get("stretto"), "prezzi": prezzi_collegati(u), "livelli": u.get("livelli", [])},
            "scenari": letture.get(u["id"], {}).get("prevalente") if u["id"] in letture else None,
        })
    salva_giorno(st, oggi.isoformat(), punteggi)
    st["aggiornato"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

    fonti_file = sorted({f for x in unita for i in x["indicatori"] for f in str(i.get("file", "")).split(", ") if f.endswith(".json")})
    out = {
        "aggiornato": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "data_riferimento": oggi.isoformat(),
        "metodo": METODO_LINK,
        "nota": "Cruscotto del rischio: probabilità di disruption (1–5) × impatto (1–5) = punteggio 1–25. "
                "Ogni indicatore ha valore, soglie, stato, fonte e data. È una valutazione con regole esplicite, "
                "non una previsione: vedi il metodo per cosa il punteggio NON dice.",
        "regole": {
            "copertura": "quota dei pesi (media dei due assi) coperta da domande con almeno un indicatore disponibile; sotto 0,7 il punteggio è fragile",
            "punti_stato": PUNTI, "pesi_probabilita": PESI_PROB, "pesi_impatto": PESI_IMP,
            "regola_disruption": f"transiti o flussi ≤ {SOGLIA_DISRUPTION:.0f}% del riferimento, oppure blackout/chiusura confermati negli ultimi 7 giorni: probabilità = 5",
            "livelli": {"basso": "< 6", "medio": "6–11,9", "alto": "12–19,9", "critico": "≥ 20"},
            "tendenza": f"differenza del punteggio con il giorno salvato più vicino a 7 giorni fa: ±{SOGLIA_TENDENZA}",
            "raggio_eventi_km": RAGGIO_KM, "finestra_eventi_giorni": FINESTRA_EVENTI,
        },
        "fonti": [{"file": f, "aggiornato": data_file(f)} for f in fonti_file],
        "unita": unita,
        "scenari": sintesi_scenari,
        "errori": ERRORI,
    }
    tmp = USCITA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    os.replace(tmp, USCITA)
    tmp = STORICO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STORICO)

    print(f"rischio.json: {len(unita)} unità, {len(ERRORI)} avvisi")
    for x in sorted(unita, key=lambda x: -(x["punteggio"] or 0)):
        print(f"  {x['nome'][:42]:42} P {fmt(x['probabilita'])}  I {fmt(x['impatto'])}  = {fmt(x['punteggio']):>5}  {x['livello']:8} {x['tendenza']}")
    for e in ERRORI:
        print("  avviso:", e)


if __name__ == "__main__":
    try:
        principale()
    except Exception as e:  # ultima rete di sicurezza: il workflow non deve fallire
        print(f"cruscotto del rischio non calcolato: {e.__class__.__name__}: {e}", file=sys.stderr)
        sys.exit(0)
