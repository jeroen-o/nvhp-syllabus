#!/usr/bin/env python3
"""
Zet een eenvoudig wachtwoordslot op de "Print dit boek"-knop (wachtwoord:
Agaat). Let op: dit is uitsluitend een laagdrempelige drempel, geen
echte beveiliging — de check staat in client-side JavaScript en is dus
zichtbaar/omzeilbaar via de paginabron voor iedereen die dat zou willen.
Geschikt om per ongeluk printen te voorkomen, niet om de syllabus
daadwerkelijk af te schermen.

Idempotent. Run: python3 scripts/apply_print_password.py
"""
import re

REPO = "/home/user/nvhp-syllabus"
PAGES = ["boek1.html", "boek2.html", "boek3.html", "boek4.html"]

MARKER = "printWithPassword"

SCRIPT_BLOCK = """<script>
function printWithPassword(slug) {
  var pw = window.prompt("Voer het wachtwoord in om te printen.\n\nWilt u de volledige syllabus (alle boeken) printen? Vraag dit aan via info@hypothecairplanner.nl.");
  if (pw === null) return;
  if (pw === "Agaat") {
    window.open(slug + ".html", "_blank").print();
  } else {
    window.alert("Onjuist wachtwoord.");
  }
}
</script>
"""

BTN_RE = re.compile(
    r'onclick="window\.open\(\'([a-z0-9]+)\.html\',\'_blank\'\)\.print\(\)"'
)


def apply_to(fname):
    path = f"{REPO}/{fname}"
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if MARKER in html:
        print(f"skip (al toegepast): {fname}")
        return

    if not BTN_RE.search(html):
        print(f"WAARSCHUWING: print-knop niet gevonden in {fname}")
        return

    html = BTN_RE.sub(lambda m: f'onclick="printWithPassword(\'{m.group(1)}\')"', html)

    if "</head>" not in html:
        print(f"WAARSCHUWING: </head> niet gevonden in {fname}")
        return
    html = html.replace("</head>", SCRIPT_BLOCK + "</head>", 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"toegepast: {fname}")


if __name__ == "__main__":
    for p in PAGES:
        apply_to(p)
