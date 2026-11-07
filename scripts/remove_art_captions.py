#!/usr/bin/env python3
"""
Verwijdert losse kunstwerk-bijschriften die als tekst zijn overgebleven
uit de PDF-extractie (de bijbehorende decoratieve afbeeldingen aan het
begin van elke module zijn nooit meegenomen, alleen het onderschrift
erbij bleef achter als een losse alinea vlak voor de hoofdstuktitel).

Patroon: <p>Titel, Kunstenaarsnaam, JJJJ - JJJJ</p>

Idempotent (patroon simpelweg niet meer aanwezig na eerste run).
Run: python3 scripts/remove_art_captions.py
"""
import re

REPO = "/home/user/nvhp-syllabus"
PAGES = ["boek1.html", "boek2.html", "boek3.html", "boek4.html"]

PATTERN = re.compile(
    r'<p>[^<]*, [A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+, [0-9]{4} ?[-–] ?[0-9]{4}</p>\n?'
)

for fname in PAGES:
    path = f"{REPO}/{fname}"
    with open(path, encoding="utf-8") as f:
        html = f.read()

    new_html, n = PATTERN.subn("", html)
    if n == 0:
        print(f"skip (geen bijschriften gevonden): {fname}")
        continue

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"{fname}: {n} bijschrift(en) verwijderd")
