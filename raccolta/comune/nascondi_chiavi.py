#!/usr/bin/env python3
"""Ultimo controllo prima del salvataggio: nessuna chiave API deve finire nei file pubblici.

Sostituisce in docs/data/*.json i valori delle variabili d'ambiente *_API_KEY / *_KEY / *_TOKEN
e qualunque "api key: <stringa lunga>" con "[chiave nascosta]". Esce con codice 0 e stampa cosa ha ripulito.
"""
import glob, os, re

segreti = [v for k, v in os.environ.items() if re.search(r"(_API_KEY|_KEY|_TOKEN)$", k) and len(v) >= 8]
schema = re.compile(r"(?i)(api[ _-]?key\W*)[A-Za-z0-9._-]{16,}")
for f in glob.glob("docs/data/*.json") + glob.glob("docs/**/*.html", recursive=True):
    s = open(f, encoding="utf-8").read()
    n = s
    for v in segreti:
        n = n.replace(v, "[chiave nascosta]")
    n = schema.sub(r"\1[chiave nascosta]", n)
    if n != s:
        open(f, "w", encoding="utf-8").write(n)
        print("chiave nascosta in", f)
print("controllo chiavi: fatto")
