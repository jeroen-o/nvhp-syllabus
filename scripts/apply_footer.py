#!/usr/bin/env python3
"""
Vervangt de simpele footer op alle pagina's door een uitgebreide, kolommen-
footer (merk + beschrijving, boeken, informatie, contact) met een losse
onderbalk voor copyright/juridische tekst.

Idempotent: herkent of de rich footer (MARKER) al aanwezig is per bestand
en slaat die dan over. Her-runnen na scripts/build.py is dus veilig.

Run: python3 scripts/apply_footer.py
"""
import re

REPO = "/home/user/nvhp-syllabus"
MARKER = "footer-main"

PAGES = ["index.html", "boek1.html", "boek2.html", "boek3.html", "boek4.html", "bijlagen.html", "wijzigingen.html"]

LEGAL = (
    "© Nederlandse Vereniging van Hypothecair Planners (NVHP), april 2025. Artikelnummers "
    "NVHP-SYLL202503/1 t/m /4. Niets uit deze syllabus mag zonder voorafgaande schriftelijke "
    "toestemming van de NVHP worden verveelvoudigd of openbaar gemaakt door middel van druk, "
    "fotokopie, microfilm of op welke andere wijze dan ook; deze digitale uitgave wordt "
    "verspreid met toestemming van de NVHP, uitsluitend voor eigen studiegebruik binnen de "
    "Leergang Hypothecaire Planning. Een afgebakende set veelgebruikte kerncijfers is na "
    "publicatie, buiten de NVHP om, bijgewerkt naar 2026 — zie het "
    '<a href="wijzigingen.html">wijzigingenlog</a> voor wat wel en niet is aangepast, met bronnen.'
)


def footer_html():
    return f'''<footer class="site-footer-rich no-print">
  <div class="footer-main">
    <div class="footer-brand-col">
      <a class="brand" href="index.html">NVHP · Leergang Hypothecaire Planning</a>
      <p>Digitale, doorzoekbare uitgave van de vier NVHP-leerboeken (editie 2025) voor de opleiding tot Erkend Hypothecair Planner, met transparant wijzigingenlog en alle officiële bijlagen.</p>
      <div class="footer-social">
        <a href="https://www.hypothecairplanner.nl" target="_blank" rel="noopener" aria-label="NVHP website" title="hypothecairplanner.nl">W</a>
        <a href="https://mc.hypothecairplanner.nl/" target="_blank" rel="noopener" aria-label="NVHP Masterclasses" title="Masterclasses">M</a>
        <a href="mailto:info@hypothecairplanner.nl" aria-label="E-mail NVHP" title="E-mail">@</a>
      </div>
    </div>
    <div class="footer-col">
      <h3>Boeken</h3>
      <ul>
        <li><a href="boek1.html">Boek 1 — Recht en fiscaliteit</a></li>
        <li><a href="boek2.html">Boek 2 — Planning</a></li>
        <li><a href="boek3.html">Boek 3 — Financieren</a></li>
        <li><a href="boek4.html">Boek 4 — De klant in beeld</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h3>Informatie</h3>
      <ul>
        <li><a href="index.html">Alle boeken</a></li>
        <li><a href="bijlagen.html">Bijlagen</a></li>
        <li><a href="wijzigingen.html">Wijzigingenlog</a></li>
        <li><a href="index.html#faq">Veelgestelde vragen</a></li>
        <li><a href="https://www.hypothecairplanner.nl/adviseur/lidmaatschap/lid-worden" target="_blank" rel="noopener">Word lid van de NVHP</a></li>
      </ul>
    </div>
    <div class="footer-col footer-contact-col">
      <h3>Contact</h3>
      <address>
        Nederlandse Vereniging van Hypothecair Planners<br>
        De Wel 14-16<br>
        3871 MV Hoevelaken<br>
        033 - 254 20 12<br>
        <a href="mailto:info@hypothecairplanner.nl">info@hypothecairplanner.nl</a><br>
        <a href="https://www.hypothecairplanner.nl" target="_blank" rel="noopener">hypothecairplanner.nl</a>
      </address>
    </div>
  </div>
  <p class="footer-legal">{LEGAL}</p>
  <div class="footer-bottom">
    <div class="footer-bottom-inner">
      <span>&copy; NVHP 2025 &middot; Leergang Hypothecaire Planning</span>
      <span><a href="https://www.hypothecairplanner.nl" target="_blank" rel="noopener">hypothecairplanner.nl</a> &middot; <a href="mailto:info@hypothecairplanner.nl">info@hypothecairplanner.nl</a></span>
    </div>
  </div>
</footer>'''


FOOTER_RE = re.compile(
    r'<footer class="(?:index-footer|site-footer)[^"]*">.*?</footer>',
    re.DOTALL,
)
COPYRIGHT_P_RE = re.compile(
    r'\n?<p class="index-copyright"[^>]*>.*?</p>\n?',
    re.DOTALL,
)


def apply_to(fname):
    path = f"{REPO}/{fname}"
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if MARKER in html:
        print(f"skip (al toegepast): {fname}")
        return

    if not FOOTER_RE.search(html):
        print(f"WAARSCHUWING: geen <footer> gevonden in {fname}, overgeslagen")
        return

    html = FOOTER_RE.sub(footer_html().replace("\\", "\\\\"), html, count=1)

    # index.html: de losse copyright-paragrafen zijn nu verwerkt in footer-legal
    if fname == "index.html":
        html = COPYRIGHT_P_RE.sub("", html)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"toegepast: {fname}")


if __name__ == "__main__":
    for p in PAGES:
        apply_to(p)
