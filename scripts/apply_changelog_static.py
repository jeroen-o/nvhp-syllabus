#!/usr/bin/env python3
"""
Bakt het wijzigingenlog (scripts/changelog_data.json) statisch in
wijzigingen.html, om dezelfde GEO-reden als scripts/apply_mc_static.py:
crawlers zonder JavaScript (GPTBot, ClaudeBot, PerplexityBot e.d.) zagen
tot nu toe alleen lege <div>'s i.p.v. de bijgewerkte en bewust niet-
bijgewerkte kerncijfers.

De client-side fetch in wijzigingen.html blijft bestaan en ververst
dezelfde inhoud zodra de pagina laadt (progressive enhancement, geen
functieverlies).

Idempotent: vervangt telkens de volledige inhoud van #updates-list en
#not-updated-list, en de teller in #count-updated.

Run: python3 scripts/apply_changelog_static.py
"""
import json
import re

REPO = "/home/user/nvhp-syllabus"

with open(f"{REPO}/scripts/changelog_data.json", encoding="utf-8") as f:
    DATA = json.load(f)


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def upd_card(u):
    src = (f'<a href="{esc(u["source_url"])}" target="_blank" rel="noopener">{esc(u["source"])}</a>'
           if u.get("source_url") else esc(u.get("source", "")))
    note = f'\n        <p class="upd-note">{esc(u["note"])}</p>' if u.get("note") else ""
    return f'''      <div class="upd-card">
        <p class="upd-topic">{esc(u["topic"])}<span class="upd-book">{esc(u["book"])}</span></p>
        <div class="upd-diff">
          <span class="upd-old">{esc(u["oud_fragment"])}</span>
          <span class="upd-new">{esc(u["nieuw_fragment"])}</span>
        </div>
        <p class="upd-src">Bron: {src}</p>{note}
      </div>'''


def nu_card(n):
    return f'''      <div class="nu-card">
        <p class="nu-topic">{esc(n["topic"])}</p>
        <p class="nu-books">{esc(n["books"])}</p>
        <p>{esc(n["reason"])}</p>
      </div>'''


def apply():
    path = f"{REPO}/wijzigingen.html"
    with open(path, encoding="utf-8") as f:
        html = f.read()

    updates_html = "\n".join(upd_card(u) for u in DATA["updates"])
    not_updated_html = "\n".join(nu_card(n) for n in DATA["not_updated"])
    stamp = f'Laatst bijgewerkt: {esc(DATA["applied_on"])}'

    new_html = html

    new_html, n1 = re.subn(
        r'<span id="count-updated">[^<]*</span>',
        f'<span id="count-updated">{len(DATA["updates"])}</span>',
        new_html, count=1,
    )
    new_html, n2 = re.subn(
        r'<div id="updates-list">.*?</div>\s*(?=</section>)',
        f'<div id="updates-list">\n{updates_html}\n    </div>\n    ',
        new_html, count=1, flags=re.DOTALL,
    )
    new_html, n3 = re.subn(
        r'<div id="not-updated-list">.*?</div>\s*(?=</section>)',
        f'<div id="not-updated-list">\n{not_updated_html}\n    </div>\n    ',
        new_html, count=1, flags=re.DOTALL,
    )
    new_html, n4 = re.subn(
        r'<p id="changelog-stamp"[^>]*>[^<]*</p>',
        f'<p id="changelog-stamp" style="color:var(--nvhp-muted);font-size:.8rem;text-align:center;margin-top:32px;">{stamp}</p>',
        new_html, count=1,
    )
    if n4 == 0:
        # eerste keer: voeg de stamp-paragraaf toe ná de niet-bijgewerkt-sectie (vóór </main>)
        new_html, n4b = re.subn(
            r'(</section>)(\s*)(</main>)',
            f'\\1\\2<p id="changelog-stamp" style="color:var(--nvhp-muted);font-size:.8rem;text-align:center;margin-top:32px;">{stamp}</p>\n  \\3',
            new_html, count=1,
        )
        if n4b == 0:
            print("WAARSCHUWING: kon stamp-paragraaf niet plaatsen")

    if not (n1 and n2 and n3):
        print(f"WAARSCHUWING: niet alle ankers gevonden (count={n1}, updates={n2}, not_updated={n3})")
        return

    if new_html == html:
        print("geen wijziging (al actueel)")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"wijzigingen.html bijgewerkt: {len(DATA['updates'])} updates, {len(DATA['not_updated'])} niet-bijgewerkt")


if __name__ == "__main__":
    apply()
