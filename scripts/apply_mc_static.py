#!/usr/bin/env python3
"""
Bakt de masterclass-kaarten statisch in masterclasses.html (i.p.v. een
lege placeholder die pas via JavaScript wordt gevuld). Belangrijk voor
GEO: crawlers van AI-zoekmachines (GPTBot, ClaudeBot, PerplexityBot e.d.)
voeren doorgaans geen JavaScript uit en zouden anders alleen "Masterclasses
laden…" zien in plaats van de 29 echte kaarten.

De client-side fetch in masterclasses.html blijft bestaan: zodra de
pagina laadt, vervangt die dezelfde markup met de meest actuele data en
zorgt hij voor de live filterfunctie. Dit script levert alleen de
eerste, statische weergave (en daarmee de door crawlers geziene inhoud).

Idempotent: vervangt alles tussen de MARKER-commentaren.

Run: python3 scripts/apply_mc_static.py
(Hoort te draaien na scripts/fetch_masterclasses.py, dus ook onderdeel
van de wekelijkse update.)
"""
import json
import re

REPO = "/home/user/nvhp-syllabus"
START = "<!-- mc-static:start -->"
END = "<!-- mc-static:end -->"

with open(f"{REPO}/scripts/masterclasses_data.json", encoding="utf-8") as f:
    DATA = json.load(f)


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card_html(m):
    badge_cls = "opleiding" if m.get("type") == "opleiding" else ""
    badge_txt = "Opleiding" if m.get("type") == "opleiding" else "Masterclass"
    points = f'<span class="mc-card-points">PE {esc(m["punten"])}</span>' if m.get("punten") else ""
    return f'''      <div class="mc-card">
        <div class="mc-card-top">
          <span class="mc-card-badge {badge_cls}">{badge_txt}</span>
          {points}
        </div>
        <h3>{esc(m["titel"])}</h3>
        <p>{esc(m.get("omschrijving", ""))}</p>
        <div class="mc-card-foot">
          <span class="mc-card-price">{esc(m.get("prijs", ""))}</span>
          <a class="mc-card-link" href="{esc(m["url"])}" target="_blank" rel="noopener">Bekijk &amp; inschrijven →</a>
        </div>
      </div>'''


def build_grid():
    cards = "\n".join(card_html(m) for m in DATA["items"])
    return f'{START}\n{cards}\n      {END}'


def apply():
    path = f"{REPO}/masterclasses.html"
    with open(path, encoding="utf-8") as f:
        html = f.read()

    grid_re = re.compile(
        r'<div id="mc-grid" class="mc-grid">.*?</div>\s*\n\s*(?=<p id="mc-stamp")',
        re.DOTALL,
    )
    if START in html:
        block_re = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.DOTALL)
        new_inner = build_grid()
        new_html = block_re.sub(lambda m: new_inner, html)
    else:
        if not grid_re.search(html):
            print("WAARSCHUWING: #mc-grid anker niet gevonden")
            return
        replacement = f'<div id="mc-grid" class="mc-grid">\n{build_grid()}\n    </div>\n\n    '
        new_html = grid_re.sub(replacement, html, count=1)

    if new_html == html:
        print("geen wijziging (al actueel)")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"masterclasses.html bijgewerkt met {len(DATA['items'])} statische kaarten")


if __name__ == "__main__":
    apply()
