#!/usr/bin/env python3
"""
Verrijkt de bestaande masterclass-links in de mc-list-blokken per boek
(boek1-4.html) met een korte omschrijving + prijs/PE-punten, op basis van
scripts/masterclasses_data.json (door scripts/fetch_masterclasses.py
wekelijks bijgewerkt). Matcht op slug (laatste deel van de cursus-URL).

Idempotent: als een <li> al een .mc-list-desc bevat, wordt die eerst
verwijderd en opnieuw opgebouwd (zodat een woordelijke update van de
masterclass-omschrijving ook hier doorkomt bij een her-run).

Run: python3 scripts/apply_mc_descriptions.py
"""
import json
import re

REPO = "/home/user/nvhp-syllabus"
PAGES = ["boek1.html", "boek2.html", "boek3.html", "boek4.html"]

with open(f"{REPO}/scripts/masterclasses_data.json", encoding="utf-8") as f:
    DATA = json.load(f)

BY_SLUG = {item["slug"]: item for item in DATA["items"]}

LI_RE = re.compile(
    r'<li><a href="https://mc\.hypothecairplanner\.nl/cursus-nvhp/([a-z0-9-]+)"'
    r'([^>]*)>([^<]*)</a>'
    r'(?:<span class="mc-list-meta">.*?</span>)?'
    r'(?:<span class="mc-list-desc">.*?</span>)?</li>',
    re.DOTALL,
)


def build_li(slug, attrs, title):
    item = BY_SLUG.get(slug)
    url = f"https://mc.hypothecairplanner.nl/cursus-nvhp/{slug}"
    if not item:
        return f'<li><a href="{url}"{attrs}>{title}</a></li>'
    desc = item.get("omschrijving", "")
    meta = []
    if item.get("prijs"):
        meta.append(item["prijs"])
    if item.get("punten"):
        meta.append(f"PE {item['punten']}")
    meta_html = f'<span class="mc-list-meta">{" · ".join(meta)}</span>' if meta else ""
    return (
        f'<li><a href="{url}"{attrs}>{title}</a>{meta_html}'
        f'<span class="mc-list-desc">{desc}</span></li>'
    )


def apply_to(fname):
    path = f"{REPO}/{fname}"
    with open(path, encoding="utf-8") as f:
        html = f.read()

    matches = list(LI_RE.finditer(html))
    if not matches:
        print(f"WAARSCHUWING: geen mc-list items gevonden in {fname}")
        return

    def repl(m):
        slug, attrs, title = m.group(1), m.group(2), m.group(3)
        return build_li(slug, attrs, title)

    new_html = LI_RE.sub(repl, html)
    if new_html == html:
        print(f"skip (geen wijziging): {fname}")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"toegepast: {fname} ({len(matches)} items)")


if __name__ == "__main__":
    for p in PAGES:
        apply_to(p)
