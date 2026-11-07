#!/usr/bin/env python3
"""
Maakt de zoekbalk in de header pagina-breed en voegt een zichtbare
"Zoeken"-knop toe naast het invoerveld. Idempotent.

Run: python3 scripts/apply_search_button.py
"""
REPO = "/home/user/nvhp-syllabus"
PAGES = ["index.html", "boek1.html", "boek2.html", "boek3.html", "boek4.html",
         "bijlagen.html", "wijzigingen.html", "masterclasses.html", "404.html"]

OLD = (
    '    <div class="header-search">\n'
    '      <input type="search" id="site-search" placeholder="Zoek in alle boeken…" autocomplete="off" aria-label="Zoek in alle boeken">\n'
    '      <div id="search-results" class="search-results" hidden></div>\n'
    '    </div>'
)
NEW = (
    '    <div class="header-search">\n'
    '      <form class="header-search-form" id="site-search-form" role="search">\n'
    '        <input type="search" id="site-search" placeholder="Zoek in alle boeken…" autocomplete="off" aria-label="Zoek in alle boeken">\n'
    '        <button type="submit" class="header-search-btn">Zoeken</button>\n'
    '      </form>\n'
    '      <div id="search-results" class="search-results" hidden></div>\n'
    '    </div>'
)

for fname in PAGES:
    path = f"{REPO}/{fname}"
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if 'header-search-btn' in html:
        print(f"skip (al toegepast): {fname}")
        continue
    if OLD not in html:
        print(f"WAARSCHUWING: anker niet gevonden in {fname}")
        continue

    html = html.replace(OLD, NEW, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"toegepast: {fname}")
