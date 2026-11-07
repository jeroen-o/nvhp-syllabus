#!/usr/bin/env python3
"""
Voegt de "Opleiding"-link toe aan de header-navigatie en de footer
("Informatie"-kolom) op alle bestaande pagina's (niet opleiding.html
zelf, die heeft 'm al). Idempotent.

Run: python3 scripts/apply_opleiding_nav.py
"""
REPO = "/home/user/nvhp-syllabus"
PAGES = ["index.html", "boek1.html", "boek2.html", "boek3.html", "boek4.html",
         "bijlagen.html", "wijzigingen.html", "masterclasses.html"]

NAV_OLD = '      <a href="bijlagen.html">Bijlagen</a>\n      <a href="masterclasses.html">Masterclasses</a>\n'
NAV_NEW = ('      <a href="bijlagen.html">Bijlagen</a>\n'
           '      <a href="opleiding.html">Opleiding</a>\n'
           '      <a href="masterclasses.html">Masterclasses</a>\n')

FOOTER_OLD = '        <li><a href="bijlagen.html">Bijlagen</a></li>\n        <li><a href="masterclasses.html">Masterclasses</a></li>\n'
FOOTER_NEW = ('        <li><a href="bijlagen.html">Bijlagen</a></li>\n'
              '        <li><a href="opleiding.html">Opleiding Hypothecair Planner</a></li>\n'
              '        <li><a href="masterclasses.html">Masterclasses</a></li>\n')

for fname in PAGES:
    path = f"{REPO}/{fname}"
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if 'href="opleiding.html">Opleiding</a>' in html:
        print(f"skip (al toegepast): {fname}")
        continue

    changed = False
    if NAV_OLD in html:
        html = html.replace(NAV_OLD, NAV_NEW, 1)
        changed = True
    else:
        print(f"WAARSCHUWING: nav-anker niet gevonden in {fname}")

    if FOOTER_OLD in html:
        html = html.replace(FOOTER_OLD, FOOTER_NEW, 1)
        changed = True
    else:
        print(f"WAARSCHUWING: footer-anker niet gevonden in {fname}")

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"toegepast: {fname}")
