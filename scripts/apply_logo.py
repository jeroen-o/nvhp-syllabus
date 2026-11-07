#!/usr/bin/env python3
"""
Vervangt de tekstuele merknaam in header en footer door het officiële NVHP-
logo (witte/transparante variant, opgehaald van hypothecairplanner.nl) plus
tekst. Idempotent (herkent "brand-logo").

Run: python3 scripts/apply_logo.py
"""
REPO = "/home/user/nvhp-syllabus"
PAGES = ["index.html", "boek1.html", "boek2.html", "boek3.html", "boek4.html",
         "bijlagen.html", "wijzigingen.html", "404.html"]

OLD = '<a class="brand" href="index.html">NVHP · Leergang Hypothecaire Planning</a>'
NEW = ('<a class="brand" href="index.html">'
       '<img class="brand-logo" src="logo-white.png" alt="NVHP" width="152" height="96">'
       '<span class="brand-text">NVHP · Leergang Hypothecaire Planning</span></a>')

for fname in PAGES:
    path = f"{REPO}/{fname}"
    try:
        with open(path, encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print(f"niet gevonden, overgeslagen: {fname}")
        continue

    if "brand-logo" in html:
        print(f"skip (al toegepast): {fname}")
        continue
    if OLD not in html:
        print(f"WAARSCHUWING: merknaam-patroon niet gevonden in {fname}")
        continue

    html = html.replace(OLD, NEW)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"toegepast: {fname}")
