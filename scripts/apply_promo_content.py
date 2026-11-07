#!/usr/bin/env python3
"""
Voegt NVHP-promotiecontent toe: een "Word Erkend Hypothecair Planner"-sectie
op index.html, per boek een korte lijst met passende Masterclasses
(mc.hypothecairplanner.nl), en een lichte verwijzing op wijzigingen.html en
bijlagen.html. Idempotent: bevat guards zodat herhaald draaien niet
dupliceert. Bedoeld om na een rebuild van de boeken (scripts/build.py)
opnieuw te draaien, net als de apply_2026_updates(_part2).py-scripts.

Run: python3 scripts/apply_promo_content.py
"""
import os

REPO = "/home/user/nvhp-syllabus"

PROMOS = {
    1: {
        "intro": "Dit boek behandelt vermogensrecht, huwelijksvermogensrecht, erfrecht en fiscaliteit — stof die in de praktijk continu verandert. Verdiep deze kennis met een Masterclass:",
        "items": [
            ("Alles wat je moet weten over de Wettelijke Verdeling", "https://mc.hypothecairplanner.nl/cursus-nvhp/masterclass-alles-wat-je-moet-weten-over-de-wettelijke-verdeling"),
            ("Draagplichtovereenkomst", "https://mc.hypothecairplanner.nl/cursus-nvhp/masterclass-draagplichtovereenkomst"),
            ("Samengestelde gezinnen en de juridisch-fiscale-financiële spaghetti", "https://mc.hypothecairplanner.nl/cursus-nvhp/masterclass-samengestelde-gezinnen-en-de-juridisch-fiscale-financiele-spaghetti"),
            ("Kan de klant na overlijden in de woning blijven?", "https://mc.hypothecairplanner.nl/cursus-nvhp/masterclass-testamentaire-clausules-en-hun-impact-op-hypothecair-advies"),
        ],
    },
    2: {
        "intro": "Estate planning en toekomstvoorzieningen vragen om actuele kennis van pensioen, schenken en erven. Deze Masterclasses sluiten direct aan op dit boek:",
        "items": [
            ("Estate Planning in Box 3", "https://mc.hypothecairplanner.nl/cursus-nvhp/masterclass-estate-planning-in-box-3"),
            ("De Nieuwe pensioenwet", "https://mc.hypothecairplanner.nl/cursus-nvhp/de-nieuwe-pensioenwet"),
            ("Hoe zeker is de langstlevende van een financieel bestaan?", "https://mc.hypothecairplanner.nl/cursus-nvhp/masterclass-hoe-zeker-is-de-langstlevende-van-een-financieel-bestaan-2026"),
            ("Overwaarde slim benutten", "https://mc.hypothecairplanner.nl/cursus-nvhp/vierluik-estate-planning"),
        ],
    },
    3: {
        "intro": "Financieren, beleggen en de positie van de IB-ondernemer en DGA: onderwerpen die je scherp houdt met gerichte verdieping. Aanbevolen bij dit boek:",
        "items": [
            ("Beleggen voor de Hypothecair Planner", "https://mc.hypothecairplanner.nl/cursus-nvhp/opfrissing-theorie-op-efpa-niveau-5"),
            ("Hypotheken en Vermogen: alles over Box 3", "https://mc.hypothecairplanner.nl/cursus-nvhp/masterclass-hypotheken-en-vermogen-alles-over-box-3"),
            ("Hypotheekmaster 2026", "https://mc.hypothecairplanner.nl/cursus-nvhp/hypotheekmaster-2026"),
            ("Inkomensbepaling zelfstandige ondernemers", "https://mc.hypothecairplanner.nl/cursus-nvhp/inkomensbepaling-zelfstandige-ondernemers-zakelijk-inkomen"),
        ],
    },
    4: {
        "intro": "Dit boek draait om de klant: gesprek, advies en de bijzondere situaties waarin mensen verkeren. Deze Masterclasses verdiepen precies dat:",
        "items": [
            ("Adviseren op basis van NBI/CBI 2026", "https://mc.hypothecairplanner.nl/cursus-nvhp/adviseren-op-basis-van-nbi-cbi-2026"),
            ("De Kracht van Aandacht", "https://mc.hypothecairplanner.nl/cursus-nvhp/de-kracht-van-aandacht"),
            ("Schrijf een adviesrapport dat klanten wél lezen", "https://mc.hypothecairplanner.nl/cursus-nvhp/masterclass-klantadviesrapport-schrijven"),
            ("Senioren en Overwaarde", "https://mc.hypothecairplanner.nl/cursus-nvhp/senioren-en-overwaarde"),
        ],
    },
}

MARKER = 'class="mc-promo no-print"'


def promo_block(p):
    items_html = "\n".join(
        f'        <li><a href="{url}" target="_blank" rel="noopener">{title}</a></li>'
        for title, url in p["items"]
    )
    return (
        '<div class="mc-promo no-print">\n'
        '      <div class="mc-promo-header"><span class="mc-badge">PE / masterclasses</span>'
        '<span class="mc-promo-title">Verdiep je kennis</span></div>\n'
        '      <div class="mc-promo-body">\n'
        f'      <p class="mc-promo-intro">{p["intro"]}</p>\n'
        '      <ul class="mc-list">\n'
        f"{items_html}\n"
        "      </ul>\n"
        '      <p class="mc-promo-foot">Als lid van de NVHP volg je deze bij permanente educatie als Erkend '
        'Hypothecair Planner. <a href="https://mc.hypothecairplanner.nl/" target="_blank" rel="noopener">Bekijk '
        'het volledige aanbod</a> of <a href="https://www.hypothecairplanner.nl/adviseur/lidmaatschap/lid-worden" '
        'target="_blank" rel="noopener">word lid</a>. Liever een gedrukt exemplaar van deze syllabus? Ook dat is, '
        'net als de Wettenbundel, te bestellen bij de NVHP via het '
        '<a href="https://www.hypothecairplanner.nl/portal/syllabi" target="_blank" rel="noopener">opleidingsportaal</a>.</p>\n'
        "      </div>\n"
        "    </div>"
    )


def apply_book_promos():
    for num, p in PROMOS.items():
        path = f"{REPO}/boek{num}.html"
        with open(path, encoding="utf-8") as f:
            c = f.read()
        if MARKER in c:
            print(f"boek{num}.html: al aanwezig, overgeslagen")
            continue
        anchor = (
            '<p class="copyright-note">© Nederlandse Vereniging van Hypothecair '
            "Planners (NVHP), april 2025. Uitsluitend voor eigen studiegebruik "
            "binnen de Leergang Hypothecaire Planning.</p>"
        )
        assert anchor in c, f"boek{num}.html: anker niet gevonden"
        c = c.replace(anchor, anchor + "\n  " + promo_block(p), 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"boek{num}.html: promo toegevoegd")


def apply_index_promo():
    path = f"{REPO}/index.html"
    with open(path, encoding="utf-8") as f:
        c = f.read()
    if 'class="ehp-promo"' in c:
        print("index.html: al aanwezig, overgeslagen")
        return
    anchor = '<p class="index-copyright">© Nederlandse Vereniging van Hypothecair Planners (NVHP), april 2025.'
    assert anchor in c, "index.html: anker niet gevonden"
    block = (
        '<div class="ehp-promo" style="max-width:1100px; margin:0 auto 32px; margin-top:0;">\n'
        "  <h2>Word Erkend Hypothecair Planner</h2>\n"
        "  <p>Deze syllabus is de basis — maar de titel Erkend Hypothecair Planner maak je waar met "
        "permanente educatie. Als lid van de NVHP volg je jaarlijks <strong>Masterclasses</strong> over "
        "actuele thema's, zodat je niet alleen het bovenwettelijke kader bijhoudt, maar ook leert hoe je "
        "dat vertaalt naar advies dat uw klant écht rust en overzicht geeft. Zo claim je je plek in de "
        "eredivisie van hypotheekadviseurs.</p>\n"
        "  <p>Voorwaarde om de titel in 2027 te mogen blijven voeren: in 2026 minimaal drie verschillende "
        "Masterclasses volgen.</p>\n"
        '  <div class="ehp-actions">\n'
        '    <a class="ehp-btn" href="https://www.hypothecairplanner.nl/adviseur/lidmaatschap/lid-worden" '
        'target="_blank" rel="noopener">Word lid van de NVHP</a>\n'
        '    <a class="ehp-btn secondary" href="https://mc.hypothecairplanner.nl/" target="_blank" '
        'rel="noopener">Bekijk alle Masterclasses</a>\n'
        "  </div>\n"
        "</div>\n\n"
    )
    c = c.replace(anchor, block + anchor, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("index.html: promo toegevoegd")


def apply_inline_notes():
    notes = {
        "wijzigingen.html": (
            "      zonder de genoemde bronnen zelf te controleren.\n    </p>",
            '\n\n    <p class="mc-inline-note no-print">Blijf zelf op het laatste niveau: de NVHP biedt '
            'jaarlijks <a href="https://mc.hypothecairplanner.nl/" target="_blank" rel="noopener">Masterclasses'
            "</a> over actuele thema's zoals deze.</p>",
        ),
        "bijlagen.html": (
            '      Gedownload op <span id="fetch-date"></span>.\n    </p>',
            '\n\n    <p class="mc-inline-note no-print">Veel van deze bijlagen (zoals NHG-normen en '
            'leennormen) komen jaarlijks terug in de <a href="https://mc.hypothecairplanner.nl/" '
            'target="_blank" rel="noopener">Masterclasses</a> van de NVHP. De syllabus zelf is, net als de '
            '<a href="https://www.hypothecairplanner.nl/adviseur/materialen/wettenbundel" target="_blank" '
            'rel="noopener">Wettenbundel</a>, ook als gedrukt boek te bestellen bij de NVHP via het '
            '<a href="https://www.hypothecairplanner.nl/portal/syllabi" target="_blank" rel="noopener">'
            "opleidingsportaal</a>.</p>",
        ),
    }
    # (bewust in één <p> samengevoegd: twee opeenvolgende .mc-inline-note-alinea's bleken elkaar
    # te overlappen bij het renderen — een hardnekkige layoutfout die alleen verdween door ze
    # samen te voegen tot één blok.)
    for fname, (anchor, addition) in notes.items():
        path = f"{REPO}/{fname}"
        with open(path, encoding="utf-8") as f:
            c = f.read()
        if "mc-inline-note" in c:
            print(f"{fname}: al aanwezig, overgeslagen")
            continue
        assert anchor in c, f"{fname}: anker niet gevonden"
        c = c.replace(anchor, anchor + addition, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"{fname}: notitie toegevoegd")


def apply_printed_edition_notes():
    # 1) per-boek: zin toevoegen aan het bestaande mc-promo-foot
    book_old_tail = (
        '<a href="https://mc.hypothecairplanner.nl/" target="_blank" rel="noopener">Bekijk '
        'het volledige aanbod</a> of <a href="https://www.hypothecairplanner.nl/adviseur/lidmaatschap/lid-worden" '
        'target="_blank" rel="noopener">word lid</a>.</p>'
    )
    book_addition = (
        ' Liever een gedrukt exemplaar van deze syllabus? Ook dat is, net als de Wettenbundel, te bestellen '
        'bij de NVHP via het <a href="https://www.hypothecairplanner.nl/portal/syllabi" target="_blank" '
        'rel="noopener">opleidingsportaal</a>.</p>'
    )
    for num in PROMOS:
        path = f"{REPO}/boek{num}.html"
        with open(path, encoding="utf-8") as f:
            c = f.read()
        if "portal/syllabi" in c:
            print(f"boek{num}.html: bestel-notitie al aanwezig, overgeslagen")
            continue
        assert book_old_tail in c, f"boek{num}.html: anker (mc-promo-foot) niet gevonden"
        c = c.replace(book_old_tail, book_old_tail[:-4] + book_addition, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        print(f"boek{num}.html: bestel-notitie toegevoegd")

    # 2) index.html: eigen mc-promo-blok vóór de copyrighttekst
    path = f"{REPO}/index.html"
    with open(path, encoding="utf-8") as f:
        c = f.read()
    if "portal/syllabi" in c:
        print("index.html: bestel-notitie al aanwezig, overgeslagen")
    else:
        anchor = '<p class="index-copyright">© Nederlandse Vereniging van Hypothecair Planners (NVHP), april 2025.'
        assert anchor in c, "index.html: anker niet gevonden"
        block = (
            '<div class="mc-promo" style="max-width:1100px; margin:0 auto 32px;">\n'
            '  <div class="mc-promo-header"><span class="mc-badge">Gedrukte editie</span>'
            '<span class="mc-promo-title">Liever een fysiek boek?</span></div>\n'
            '  <div class="mc-promo-body has-cover">\n'
            '    <div class="mc-promo-cover"><img src="syllabus-omslag.png" alt="Omslag van de gedrukte NVHP-syllabus '
            'Leergang Hypothecaire Planning" width="300" height="300" loading="lazy"></div>\n'
            '    <div class="mc-promo-text">\n'
            '    <p class="mc-promo-intro">Net als de <a href="https://www.hypothecairplanner.nl/adviseur/materialen/wettenbundel" '
            'target="_blank" rel="noopener">Wettenbundel Financiële Dienstverlening</a> is ook deze syllabus los '
            "te bestellen bij de NVHP als gedrukt boek.</p>\n"
            '    <p class="mc-promo-foot">Bestellen kan via het <a href="https://www.hypothecairplanner.nl/portal/syllabi" '
            'target="_blank" rel="noopener">NVHP-opleidingsportaal (Syllabi)</a> — inlog met uw NVHP-account vereist — '
            'of via de <a href="https://www.hypothecairplanner.nl/adviseur/materialen" target="_blank" rel="noopener">materialenpagina</a>. '
            'Vragen? Mail <a href="mailto:info@hypothecairplanner.nl">info@hypothecairplanner.nl</a>.</p>\n'
            "    </div>\n"
            "  </div>\n"
            "</div>\n\n"
        )
        c = c.replace(anchor, block + anchor, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(c)
        print("index.html: bestel-notitie toegevoegd")

    # 3) bijlagen.html: de bestel-zin zit al in de .mc-inline-note tekst die
    # apply_inline_notes() genereert (bewust in hetzelfde <p> i.p.v. een
    # tweede, losse alinea — zie de toelichting daar). Niets te doen hier.
    path = f"{REPO}/bijlagen.html"
    with open(path, encoding="utf-8") as f:
        c = f.read()
    if "portal/syllabi" in c:
        print("bijlagen.html: bestel-notitie al aanwezig, overgeslagen")
    else:
        print("bijlagen.html: wordt mee opgenomen door apply_inline_notes()")


if __name__ == "__main__":
    apply_book_promos()
    apply_index_promo()
    apply_inline_notes()
    apply_printed_edition_notes()
