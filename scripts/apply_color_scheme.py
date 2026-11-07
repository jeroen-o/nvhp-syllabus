#!/usr/bin/env python3
"""
Voegt <meta name="color-scheme" content="light"> toe aan alle pagina's.

Zonder dit past Chrome/Edge bij een donkere systeem-/browservoorkeur
automatisch "dark mode"-heuristieken toe op de pagina, wat de navy
gradient-achtergronden (header, footer, promoblokken) laat verbleken
tot nauwelijks leesbaar — ook al is de CSS zelf correct (geverifieerd
met getComputedStyle). Dit is de standaardoplossing: de browser expliciet
vertellen dat de pagina een licht kleurenschema heeft, zodat hij niets
automatisch aanpast.

Idempotent. Run: python3 scripts/apply_color_scheme.py
"""
REPO = "/home/user/nvhp-syllabus"
PAGES = ["index.html", "boek1.html", "boek2.html", "boek3.html", "boek4.html",
         "bijlagen.html", "wijzigingen.html", "404.html"]

META = '<meta name="color-scheme" content="light">\n'

for fname in PAGES:
    path = f"{REPO}/{fname}"
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if 'name="color-scheme"' in html:
        print(f"skip (al toegepast): {fname}")
        continue

    marker = '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    if marker not in html:
        print(f"WAARSCHUWING: viewport-meta niet gevonden in {fname}")
        continue

    html = html.replace(marker, marker + META, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"toegepast: {fname}")
