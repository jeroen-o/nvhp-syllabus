#!/usr/bin/env python3
"""
Volledige SEO- en GEO-optimalisatie (Generative Engine Optimization: vindbaar
en correct citeerbaar in AI-antwoorden zoals ChatGPT/Perplexity/Google AI
Overviews) voor nvhp-syllabus.nl.

Voegt toe aan elke pagina: canonical URL, Open Graph + Twitter Card, favicons,
robots-meta, JSON-LD structured data (Organization, WebSite+SearchAction,
Book, BreadcrumbList, FAQPage). Plus nieuwe bestanden: robots.txt,
sitemap.xml, llms.txt, 404.html.

Idempotent (checkt op bestaande markers). Opnieuw draaien na een rebuild van
de boeken (scripts/build.py) of na wijziging van titels/beschrijvingen.

Run: python3 scripts/apply_seo_geo.py
"""
import json
import os

REPO = "/home/user/nvhp-syllabus"
DOMAIN = "https://nvhp-syllabus.nl"
ORG_NAME = "Nederlandse Vereniging van Hypothecair Planners (NVHP)"
SITE_NAME = "NVHP · Leergang Hypothecaire Planning"
TODAY = "2026-11-07"

PAGES = {
    "index.html": {
        "path": "/",
        "title": "Syllabus Leergang Hypothecaire Planning | NVHP",
        "description": "Digitale, doorzoekbare syllabus van de Leergang Hypothecaire Planning (NVHP, editie 2025) — alle 4 boeken, bijlagen en een transparant wijzigingenlog voor (aankomend) Erkend Hypothecair Planners.",
        "og_type": "website",
        "priority": "1.0",
        "changefreq": "weekly",
    },
    "boek1.html": {
        "path": "/boek1.html",
        "title": "Boek 1: Recht en fiscaliteit — NVHP Syllabus Hypothecair Planner",
        "description": "Recht, fiscaliteit en fiscaliteit eigen woning: vermogensrecht, goederenrecht, overeenkomstenrecht, personen- en familierecht, erfrecht, box 1/2/3, heffingskortingen en overdrachtsbelasting. Boek 1 van de NVHP-syllabus Leergang Hypothecaire Planning.",
        "og_type": "book",
        "priority": "0.9",
        "changefreq": "monthly",
    },
    "boek2.html": {
        "path": "/boek2.html",
        "title": "Boek 2: Planning — NVHP Syllabus Hypothecair Planner",
        "description": "Estate planning en toekomstvoorzieningen: huwelijksvermogensrecht, schenk- en erfbelasting, pensioen, AOW en arbeidsongeschiktheid. Boek 2 van de NVHP-syllabus Leergang Hypothecaire Planning.",
        "og_type": "book",
        "priority": "0.9",
        "changefreq": "monthly",
    },
    "boek3.html": {
        "path": "/boek3.html",
        "title": "Boek 3: Financieren — NVHP Syllabus Hypothecair Planner",
        "description": "Financieren en beleggen, vermogensallocatie, financiering van particulieren en ondernemers, de IB-ondernemer en de DGA. Boek 3 van de NVHP-syllabus Leergang Hypothecaire Planning.",
        "og_type": "book",
        "priority": "0.9",
        "changefreq": "monthly",
    },
    "boek4.html": {
        "path": "/boek4.html",
        "title": "Boek 4: De klant in beeld — NVHP Syllabus Hypothecair Planner",
        "description": "Wft, gedragscode en adviesvaardigheden, consumptief besteedbaar inkomen, gezin, vermogen ontvangen en overdragen, financieringsaanvraag van de ondernemer en wonen. Boek 4 van de NVHP-syllabus Leergang Hypothecaire Planning.",
        "og_type": "book",
        "priority": "0.9",
        "changefreq": "monthly",
    },
    "bijlagen.html": {
        "path": "/bijlagen.html",
        "title": "Bijlagen — NVHP Syllabus Hypothecaire Planning",
        "description": "Alle officiële NVHP-referentiedocumenten bij de syllabus: NHG-voorwaarden en -normen, leennormen, Nibud-advies, gedragscode, AVG-materiaal en SVn-productvoorwaarden.",
        "og_type": "website",
        "priority": "0.6",
        "changefreq": "yearly",
    },
    "wijzigingen.html": {
        "path": "/wijzigingen.html",
        "title": "Wijzigingenlog — NVHP Syllabus Hypothecaire Planning",
        "description": "Transparant overzicht van alle kerncijfers die in deze digitale syllabus zijn bijgewerkt naar 2026 t.o.v. de gedrukte editie 2025, met bron per wijziging.",
        "og_type": "website",
        "priority": "0.5",
        "changefreq": "monthly",
    },
    "masterclasses.html": {
        "path": "/masterclasses.html",
        "title": "Masterclasses — NVHP Syllabus Hypothecaire Planning",
        "description": "Overzicht van alle actuele NVHP-Masterclasses voor Erkend Hypothecair Planners: korte omschrijving, PE-punten en prijs per masterclass.",
        "og_type": "website",
        "priority": "0.6",
        "changefreq": "daily",
    },
    "opleiding.html": {
        "path": "/opleiding.html",
        "title": "Opleiding Hypothecair Planner — wat levert het op?",
        "description": "Wat de Leergang Hypothecaire Planning (opleiding tot Erkend Hypothecair Planner) u en uw klant oplevert: inhoud, instapeisen, examen en waar u de opleiding kunt volgen.",
        "og_type": "website",
        "priority": "0.7",
        "changefreq": "monthly",
    },
}

BOOK_META = {
    "boek1.html": {"num": 1, "name": "Recht en fiscaliteit", "pos": 2},
    "boek2.html": {"num": 2, "name": "Planning", "pos": 3},
    "boek3.html": {"num": 3, "name": "Financieren", "pos": 4},
    "boek4.html": {"num": 4, "name": "De klant in beeld", "pos": 5},
}

MARKER = "<!-- seo-geo -->"


def head_block(fname, meta):
    url = DOMAIN + meta["path"]
    lines = [MARKER]
    lines.append(f'<link rel="canonical" href="{url}">')
    lines.append('<meta name="robots" content="index, follow">')
    lines.append(f'<meta name="author" content="{ORG_NAME}">')
    lines.append(f'<meta property="og:type" content="{meta["og_type"]}">')
    lines.append(f'<meta property="og:site_name" content="{SITE_NAME}">')
    lines.append('<meta property="og:locale" content="nl_NL">')
    lines.append(f'<meta property="og:title" content="{meta["title"]}">')
    lines.append(f'<meta property="og:description" content="{meta["description"]}">')
    lines.append(f'<meta property="og:url" content="{url}">')
    lines.append(f'<meta property="og:image" content="{DOMAIN}/og-image.png">')
    lines.append('<meta property="og:image:width" content="1200">')
    lines.append('<meta property="og:image:height" content="630">')
    lines.append('<meta name="twitter:card" content="summary_large_image">')
    lines.append(f'<meta name="twitter:title" content="{meta["title"]}">')
    lines.append(f'<meta name="twitter:description" content="{meta["description"]}">')
    lines.append(f'<meta name="twitter:image" content="{DOMAIN}/og-image.png">')
    lines.append('<link rel="icon" href="/favicon.svg" type="image/svg+xml">')
    lines.append('<link rel="icon" href="/favicon.ico" sizes="any">')
    lines.append('<link rel="apple-touch-icon" href="/apple-touch-icon.png">')
    lines.append('<meta name="theme-color" content="#234765">')
    lines.append(f'<script type="application/ld+json">{json.dumps(jsonld(fname, meta), ensure_ascii=False)}</script>')
    return "\n".join(lines)


def breadcrumb(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": DOMAIN + path}
            for i, (name, path) in enumerate(items)
        ],
    }


def org_entity():
    return {
        "@type": "Organization",
        "name": ORG_NAME,
        "alternateName": "NVHP",
        "url": "https://www.hypothecairplanner.nl",
        "logo": f"{DOMAIN}/apple-touch-icon.png",
        "sameAs": ["https://www.hypothecairplanner.nl"],
    }


def jsonld(fname, meta):
    graph = []
    if fname == "index.html":
        graph.append({"@type": "WebSite", "@id": DOMAIN + "/#website", "name": SITE_NAME,
                       "url": DOMAIN + "/", "inLanguage": "nl-NL", "publisher": org_entity(),
                       "potentialAction": {"@type": "SearchAction",
                                           "target": {"@type": "EntryPoint", "urlTemplate": DOMAIN + "/?q={search_term_string}"},
                                           "query-input": "required name=search_term_string"}})
        graph.append({"@type": "ItemList", "name": "Boeken in de syllabus",
                       "itemListElement": [
                           {"@type": "ListItem", "position": b["pos"] - 1, "name": f"Boek {b['num']} — {b['name']}",
                            "url": DOMAIN + "/" + f}
                           for f, b in BOOK_META.items()
                       ]})
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in FAQ
            ],
        })
        graph.append(org_entity())
    elif fname in BOOK_META:
        b = BOOK_META[fname]
        graph.append({
            "@type": "Book", "@id": DOMAIN + "/" + fname + "#book",
            "name": f"Boek {b['num']} — {b['name']}",
            "author": org_entity(), "publisher": org_entity(),
            "inLanguage": "nl-NL", "datePublished": "2025-04",
            "isPartOf": {"@type": "CreativeWorkSeries", "name": "Syllabus Leergang Hypothecaire Planning", "url": DOMAIN + "/"},
            "url": DOMAIN + "/" + fname,
            "description": meta["description"],
            "educationalUse": "Opleidingsmateriaal", "audience": {"@type": "Audience", "audienceType": "Hypotheekadviseurs"},
        })
        graph.append(breadcrumb([("Alle boeken", "/"), (f"Boek {b['num']} — {b['name']}", "/" + fname)]))
    elif fname == "bijlagen.html":
        graph.append({"@type": "CollectionPage", "name": meta["title"], "url": DOMAIN + "/bijlagen.html",
                       "description": meta["description"], "isPartOf": {"@type": "WebSite", "url": DOMAIN + "/"}})
        graph.append(breadcrumb([("Alle boeken", "/"), ("Bijlagen", "/bijlagen.html")]))
    elif fname == "wijzigingen.html":
        graph.append({"@type": "WebPage", "name": meta["title"], "url": DOMAIN + "/wijzigingen.html",
                       "description": meta["description"]})
        graph.append(breadcrumb([("Alle boeken", "/"), ("Wijzigingenlog", "/wijzigingen.html")]))
    elif fname == "masterclasses.html":
        graph.append({"@type": "CollectionPage", "name": meta["title"], "url": DOMAIN + "/masterclasses.html",
                       "description": meta["description"], "isPartOf": {"@type": "WebSite", "url": DOMAIN + "/"}})
        graph.append(breadcrumb([("Alle boeken", "/"), ("Masterclasses", "/masterclasses.html")]))
    elif fname == "opleiding.html":
        graph.append({"@type": "Course", "name": "Leergang Hypothecaire Planning",
                       "description": "HBO-niveau verdiepingsopleiding tot Erkend Hypothecair Planner (EHP), voor hypotheekadviseurs met het Wft-diploma Hypothecair Krediet.",
                       "provider": org_entity(), "url": DOMAIN + "/opleiding.html",
                       "educationalCredentialAwarded": "Erkend Hypothecair Planner (EHP)"})
        graph.append(breadcrumb([("Alle boeken", "/"), ("Opleiding Hypothecair Planner", "/opleiding.html")]))
    return {"@context": "https://schema.org", "@graph": graph}


FAQ = [
    ("Wat is deze syllabus?",
     "Dit is een digitale, doorzoekbare uitgave van de vier officiële NVHP-leerboeken (editie 2025) voor de Leergang Hypothecaire Planning, de opleiding tot Erkend Hypothecair Planner. De syllabus is gepubliceerd met toestemming van de Nederlandse Vereniging van Hypothecair Planners (NVHP), uitsluitend voor eigen studiegebruik."),
    ("Wat is een Erkend Hypothecair Planner?",
     "Een Erkend Hypothecair Planner (EHP) is een hypotheekadviseur die, bovenop het Wft-diploma Hypothecair Krediet, de Leergang Hypothecaire Planning heeft afgerond en lid is van de NVHP. EHP's onderhouden hun kennis jaarlijks via Masterclasses en onderwerpen zich aan de Gedragscode Erkend Hypothecair Planners."),
    ("Hoe word ik Erkend Hypothecair Planner?",
     "Eerst volgt u de Leergang Hypothecaire Planning bij een erkend opleidingsinstituut (o.a. DFO, Impact Opleidingen of Lindenhaeghe). Na het behalen van het diploma schrijft u zich in als lid bij de NVHP, waarmee u de beschermde titel Erkend Hypothecair Planner mag voeren."),
    ("Is deze website de officiële, actuele examenstof?",
     "Nee. De syllabus zelf is bijgewerkt tot 1 maart 2025. Een afgebakende set veelgebruikte kerncijfers is nadien, buiten de NVHP om, bijgewerkt naar 2026 — zie het transparante wijzigingenlog voor precies wat wel en niet is aangepast, met bron. Raadpleeg voor de officiële, actuele examenstof altijd de NVHP zelf."),
    ("Is de gedrukte versie van deze syllabus ook te bestellen?",
     "Ja. Net als de Wettenbundel Financiële Dienstverlening is de syllabus los te bestellen bij de NVHP als gedrukt boek, via het NVHP-opleidingsportaal (Syllabi) of de materialenpagina op hypothecairplanner.nl."),
    ("Wat zijn de Masterclasses van de NVHP?",
     "Jaarlijkse verdiepingsbijeenkomsten over actuele thema's in de hypothecaire advisering. Erkend Hypothecair Planners moeten jaarlijks minimaal drie verschillende Masterclasses volgen om de titel te mogen blijven voeren."),
]


def apply_head_blocks():
    for fname, meta in PAGES.items():
        path = f"{REPO}/{fname}"
        with open(path, encoding="utf-8") as f:
            c = f.read()
        if MARKER in c:
            print(f"{fname}: seo/geo-blok al aanwezig, overgeslagen")
            continue
        anchor = '<link rel="stylesheet" href="style.css">'
        assert anchor in c, f"{fname}: anker niet gevonden"
        block = head_block(fname, meta)
        c = c.replace(anchor, anchor + "\n" + block, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"{fname}: seo/geo-blok toegevoegd")


def write_robots_txt():
    content = f"""User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
"""
    with open(f"{REPO}/robots.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("robots.txt geschreven")


def write_sitemap_xml():
    urls = []
    for fname, meta in PAGES.items():
        urls.append(
            "  <url>\n"
            f"    <loc>{DOMAIN}{meta['path']}</loc>\n"
            f"    <lastmod>{TODAY}</lastmod>\n"
            f"    <changefreq>{meta['changefreq']}</changefreq>\n"
            f"    <priority>{meta['priority']}</priority>\n"
            "  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n"
        "</urlset>\n"
    )
    with open(f"{REPO}/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    print("sitemap.xml geschreven")


def write_llms_txt():
    content = f"""# NVHP Syllabus — Leergang Hypothecaire Planning

> Digitale, doorzoekbare uitgave van de vier officiële NVHP-leerboeken (editie 2025) voor
> de opleiding tot Erkend Hypothecair Planner (EHP), uitgegeven door en gepubliceerd met
> toestemming van de Nederlandse Vereniging van Hypothecair Planners (NVHP).

## Boeken

- [Boek 1 — Recht en fiscaliteit]({DOMAIN}/boek1.html): vermogensrecht, goederenrecht,
  overeenkomstenrecht, koop en verkoop onroerende zaken, personen- en familierecht,
  erfrecht, ondernemingsvormen, inkomstenbelasting (box 1/2/3), heffingskortingen,
  overdrachtsbelasting, fiscaliteit eigen woning.
- [Boek 2 — Planning]({DOMAIN}/boek2.html): estate planning, huwelijksvermogensrecht,
  schenk- en erfbelasting, toekomstvoorzieningen (pensioen, AOW, arbeidsongeschiktheid).
- [Boek 3 — Financieren]({DOMAIN}/boek3.html): financieren en beleggen,
  vermogensallocatie, financiering van particulieren en ondernemers, de IB-ondernemer
  en de DGA.
- [Boek 4 — De klant in beeld]({DOMAIN}/boek4.html): Wft, gedragscode en
  adviesvaardigheden, consumptief besteedbaar inkomen, gezin, vermogen ontvangen en
  overdragen, financieringsaanvraag van de ondernemer, wonen.

## Overig

- [Bijlagen]({DOMAIN}/bijlagen.html): officiële NVHP-referentiedocumenten (NHG-normen,
  leennormen, Nibud-advies, gedragscode, AVG-materiaal, SVn-productvoorwaarden).
- [Opleiding Hypothecair Planner]({DOMAIN}/opleiding.html): wat de Leergang Hypothecaire
  Planning (de opleiding tot Erkend Hypothecair Planner) een adviseur en diens klant oplevert,
  instapeisen, examen, en een overzicht van de opleidingsinstituten (DFO, Lindenhaeghe, Impact)
  met prijs en inhoud; maandelijks automatisch gecontroleerd.
- [Masterclasses]({DOMAIN}/masterclasses.html): actueel overzicht van NVHP-Masterclasses
  (permanente educatie voor Erkend Hypothecair Planners), met omschrijving, PE-punten en
  prijs per masterclass; dagelijks automatisch gecontroleerd op mc.hypothecairplanner.nl.
- [Wijzigingenlog]({DOMAIN}/wijzigingen.html): transparant overzicht van kerncijfers die
  zijn bijgewerkt naar 2026 t.o.v. de gedrukte editie 2025, met bron per wijziging.

## Over deze uitgave

Uitgegeven door de Nederlandse Vereniging van Hypothecair Planners (NVHP),
https://www.hypothecairplanner.nl. Bedoeld voor eigen studiegebruik binnen de Leergang
Hypothecaire Planning. Dit is niet de live, door de NVHP gecontroleerde examenstof —
zie het wijzigingenlog voor wat na publicatie is bijgewerkt en wat niet.
"""
    with open(f"{REPO}/llms.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("llms.txt geschreven")


def write_404():
    if os.path.exists(f"{REPO}/404.html"):
        print("404.html al aanwezig, overgeslagen")
        return
    content = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pagina niet gevonden — NVHP Syllabus</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header no-print">
  <div class="header-inner">
    <a class="brand" href="/">NVHP · Leergang Hypothecaire Planning</a>
    <nav class="header-nav" aria-label="Boeken en pagina's">
      <a href="/boek1.html">Boek 1</a>
      <a href="/boek2.html">Boek 2</a>
      <a href="/boek3.html">Boek 3</a>
      <a href="/boek4.html">Boek 4</a>
      <a href="/bijlagen.html">Bijlagen</a>
      <a href="/wijzigingen.html">Wijzigingen</a>
    </nav>
  </div>
</header>
<section class="hero">
  <h1>Pagina niet gevonden</h1>
  <p>Deze pagina bestaat niet (meer). Ga terug naar de <a href="/" style="color:#fff;text-decoration:underline;">boekenoverzicht</a> of gebruik de zoekfunctie in de header.</p>
</section>
<footer class="index-footer no-print">
  <p class="footer-contact">Nederlandse Vereniging van Hypothecair Planners · De Wel 14-16, 3871 MV Hoevelaken · 033 - 254 20 12 · <a href="mailto:info@hypothecairplanner.nl">info@hypothecairplanner.nl</a></p>
</footer>
<script src="/search.js" defer></script>
</body>
</html>
"""
    with open(f"{REPO}/404.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("404.html geschreven")


if __name__ == "__main__":
    apply_head_blocks()
    write_robots_txt()
    write_sitemap_xml()
    write_llms_txt()
    write_404()
