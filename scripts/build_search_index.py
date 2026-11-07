#!/usr/bin/env python3
"""
Bouwt search-index.json: een doorzoekbare index over alle 4 boeken, met
per heading-sectie (deel/hoofdstuk/paragraaf/subparagraaf) de bijbehorende
tekst, zodat de header-zoeker ermee kan zoeken zonder server of build-step.

Run: python3 scripts/build_search_index.py
"""
import html
import json
import re

REPO = "/home/user/nvhp-syllabus"

BOOKS = [
    {"file": "boek1.html", "num": 1, "title": "Recht en fiscaliteit"},
    {"file": "boek2.html", "num": 2, "title": "Planning"},
    {"file": "boek3.html", "num": 3, "title": "Financieren"},
    {"file": "boek4.html", "num": 4, "title": "De klant in beeld"},
]

HEADING_RE = re.compile(
    r'<h2 id="([^"]+)" class="deel">(.*?)</h2>'
    r'|<h3 class="chapter" id="([^"]+)">(.*?)</h3>'
    r'|<h3 id="([^"]+)">(.*?)</h3>'
    r'|<h4 id="([^"]+)">(.*?)</h4>'
)
PARA_RE = re.compile(r"<p>(.*?)</p>")
TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(s):
    return html.unescape(TAG_RE.sub("", s)).strip()


def build_index():
    entries = []
    for book in BOOKS:
        path = f"{REPO}/{book['file']}"
        with open(path, encoding="utf-8") as f:
            content = f.read()
        i = content.find('<main class="content">')
        j = content.find("</main>", i)
        body = content[i:j]

        matches = list(HEADING_RE.finditer(body))
        for idx, m in enumerate(matches):
            if m.group(1):
                anchor, raw_title, level = m.group(1), m.group(2), "deel"
            elif m.group(3):
                anchor, raw_title, level = m.group(3), m.group(4), "chap"
            elif m.group(5):
                anchor, raw_title, level = m.group(5), m.group(6), "sec"
            else:
                anchor, raw_title, level = m.group(7), m.group(8), "sub"
            title = strip_tags(raw_title)

            start = m.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
            section_html = body[start:end]
            paras = [strip_tags(p) for p in PARA_RE.findall(section_html)]
            text = " ".join(p for p in paras if p)

            entries.append({
                "b": book["num"],
                "bt": book["title"],
                "a": anchor,
                "lv": level,
                "t": title,
                "x": text[:600],  # cap per-section text to keep the index light
            })

    out_path = f"{REPO}/search-index.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Index geschreven: {len(entries)} secties -> {out_path}")


if __name__ == "__main__":
    build_index()
