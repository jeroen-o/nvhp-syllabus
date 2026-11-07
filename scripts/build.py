#!/usr/bin/env python3
"""Convert NVHP syllabus PDF-text dumps into structured HTML per boek."""
import re, html, sys, os

SRC_DIR = "/tmp/claude-0/-home-user-nvhp-syllabus/abbf8499-7977-5575-a19e-1f6a27d335a3/scratchpad/dl/SYLLABUS NVHP 2025"
OUT_DIR = "/home/user/nvhp-syllabus"

BOOKS = [
    {"num": 1, "file": "NVHP-SYLL202503_1 - Recht en fiscaliteit BW Druk.txt",
     "title": "Recht en fiscaliteit", "slug": "boek1",
     "subtitle": "Recht · Fiscaliteit · Fiscaliteit eigen woning"},
    {"num": 2, "file": "NVHP-SYLL202503_2 - Planning BW Druk.txt",
     "title": "Planning", "slug": "boek2",
     "subtitle": "Estate planning · Toekomstvoorzieningen"},
    {"num": 3, "file": "NVHP-SYLL202503_3 - Financieren BW Druk.txt",
     "title": "Financieren", "slug": "boek3",
     "subtitle": "Financieren en beleggen · IB-ondernemer en DGA"},
    {"num": 4, "file": "NVHP-SYLL202503_4 - De klant in beeld BW Druk.txt",
     "title": "De klant in beeld", "slug": "boek4",
     "subtitle": "Omgaan met cliënten · Consumptief besteedbaar inkomen · Gezin · Vermogen ontvangen en overdragen · Financieringsaanvraag van de ondernemer · Wonen"},
]

FOOTER_RE = re.compile(r"^\s*Boek \d+\.indb \d+.*\d{2}-\d{2}-\d{4}.*$")
LONE_NUM_RE = re.compile(r"^\s*[IVXLCDM]+\s*$|^\s*\d{1,4}\s*$")
DEEL_BODY_RE = re.compile(r"^\s*DEEL\s+(\d+)\s*(?:[–-]\s*(.+))?\s*$", re.IGNORECASE)
CHAPTER_RE = re.compile(r"^\s*(\d{1,2})\s{2,}([A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝ0-9:,\.\-\'’/ ]{3,})\s*$")
LETTERS_RE = re.compile(r"[A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝ]{3,}")
MOJIBAKE_RE = re.compile(r"([éëóáïöèüàúíêÉËÓÁÏÖÈÜÀÚÍÊea])�\s?")
BULLET_UFFFD_RE = re.compile(r"(?<=\s)�(?=\s)")
HYPHEN_END_RE = re.compile(r"(\w)-$")
SECTION_RE = re.compile(r"^\s*(\d{1,2}\.\d{1,2})\s{2,}(\S.{1,110})\s*$")
SUBSECTION_RE = re.compile(r"^\s*(\d{1,2}\.\d{1,2}\.\d{1,2})\s{1,}(\S.{1,110})\s*$")
TRAILING_PAGENUM_RE = re.compile(r"\d+\s*$")
BIG_GAP_RE = re.compile(r"\s{3,}\d+\s*$")  # TOC style: "....title....   84"
TOC_NUM_RE = re.compile(r"^\s*(\d{1,2}(?:\.\d{1,2}){0,2})\s+(.+?)\s{2,}\d+\s*(?:[IVXLCDM]+)?\s*$")
TOC_DEEL_RE = re.compile(r"^\s*DEEL\s+(\d+)\s+(.+?)\s{2,}\d+\s*(?:[IVXLCDM]+)?\s*$", re.IGNORECASE)
TOC_NUM_NOGAP_RE = re.compile(r"^\s*(\d{1,2}(?:\.\d{1,2}){0,2})\t(\D+?)\d{1,4}\s*$")
TOC_NUM_NOPAGE_RE = re.compile(r"^\s*(\d{1,2}(?:\.\d{1,2}){0,2})\s+(\S.*\S|\S)\s*$")
TOC_CONT_PAGE_RE = re.compile(r"^\s*(.*?)\s{2,}\d+\s*(?:[IVXLCDM]+)?\s*$")


def parse_toc_titles(lines, body_start):
    """Authoritative titles: the table of contents is (mostly) single-line and
    free of the dropped-capital artifacts that hit the printed body headings.
    A handful of long titles wrap onto a continuation line before the page
    number, so track a pending entry across lines for those."""
    titles = {}
    pending = None  # (key, [word, word, ...])
    for ln in lines[:body_start]:
        if not ln.strip():
            continue
        m = TOC_DEEL_RE.match(ln)
        if m:
            titles.setdefault("deel" + m.group(1), re.sub(r"\s+", " ", m.group(2)).strip())
            pending = None
            continue
        m = TOC_NUM_RE.match(ln)
        if m:
            titles.setdefault(m.group(1), re.sub(r"\s+", " ", m.group(2)).strip())
            pending = None
            continue
        m = TOC_NUM_NOGAP_RE.match(ln)
        if m:
            titles.setdefault(m.group(1), re.sub(r"\s+", " ", m.group(2)).strip())
            pending = None
            continue
        m = TOC_NUM_NOPAGE_RE.match(ln)
        if m:
            pending = (m.group(1), [m.group(2).strip()])
            continue
        if pending:
            key, words = pending
            m2 = TOC_CONT_PAGE_RE.match(ln)
            if m2:
                words.append(m2.group(1).strip())
                titles.setdefault(key, re.sub(r"\s+", " ", " ".join(w for w in words if w)).strip())
                pending = None
            else:
                words.append(ln.strip())
    return titles

def is_toc_line(line):
    """TOC entries end in a page number preceded by a wide gap."""
    return bool(BIG_GAP_RE.search(line))

def is_heading_line(ln):
    return bool(DEEL_BODY_RE.match(ln) or CHAPTER_RE.match(ln) or SECTION_RE.match(ln) or SUBSECTION_RE.match(ln))

def absorb_continuation(lines, i, n):
    """Titles (DEEL/hoofdstuk/paragraaf) are set in full caps and sometimes wrap
    across 1-2 extra physical lines in the PDF layout. Consume those immediate
    follow-up lines and return (extra_words, new_index)."""
    extra = []
    j = i
    while j < n:
        raw = lines[j]
        s = raw.strip()
        if not s:
            break
        if is_toc_line(raw) or is_heading_line(raw) or LONE_NUM_RE.match(s):
            break
        letters = re.sub(r"[^A-Za-zÀ-ÿ]", "", s)
        if not letters or letters != letters.upper() or len(s) > 90:
            break
        extra.append(s)
        j += 1
    return extra, j

def strip_footers(text):
    text = MOJIBAKE_RE.sub(r"\1", text)
    text = BULLET_UFFFD_RE.sub("•", text)
    text = text.replace("�", "")
    # \x07 / \x08: pdftotext noise around dropped/garbled glyphs (confirmed harmless
    # in the TOC; in the body they sometimes coincide with a lost capital letter in
    # footnote references — rare and not worth chasing further here).
    text = text.replace("\x07", "").replace("\x08", "")
    lines = text.split("\n")
    out = []
    for ln in lines:
        if FOOTER_RE.match(ln):
            continue
        out.append(ln)
    return "\n".join(out)

def esc(s):
    return html.escape(s, quote=False)

def find_body_start(lines):
    """Skip the TOC: find second occurrence of 'DEEL <n>' pattern (body heading, no page-number gap)."""
    deel_hits = 0
    for i, ln in enumerate(lines):
        if DEEL_BODY_RE.match(ln) and not is_toc_line(ln):
            deel_hits += 1
            if deel_hits == 1:
                return i
    return 0

def build_book_html(book):
    path = os.path.join(SRC_DIR, book["file"])
    raw = open(path, encoding="utf-8").read()
    raw = raw.replace("\x0c", "\n")
    raw = strip_footers(raw)
    lines = raw.split("\n")

    body_start = find_body_start(lines)
    toc_titles = parse_toc_titles(lines, body_start)
    lines = lines[body_start:]

    html_parts = []
    toc_parts = []
    paragraph_buf = []
    current_part_title = None
    seen_chap_nums = set()
    first_heading_done = False

    # Authoritative, ordered deel-list from the TOC. The book's own running
    # headers for a "DEEL N – Titel" are unreliable (confirmed print error:
    # boek 1 prints "DEEL 3" as the running header for both deel 2 and deel 3),
    # so only the bare, dash-less "DEEL N" divider triggers a new part, and we
    # take the next untouched (number, title) pair from the TOC in order
    # instead of trusting the printed number.
    deel_queue = sorted(
        ((int(k[4:]), v) for k, v in toc_titles.items() if k.startswith("deel")),
        key=lambda kv: kv[0],
    )
    deel_idx = 0

    def flush_paragraph():
        if paragraph_buf:
            text = ""
            for x in paragraph_buf:
                x = x.strip()
                if not x:
                    continue
                m_hyph = HYPHEN_END_RE.search(text)
                if m_hyph and text and not text.endswith(" -"):
                    text = text[:-1] + x  # drop hyphen, glue directly
                elif text:
                    text = text + " " + x
                else:
                    text = x
            if text:
                html_parts.append(f"<p>{esc(text)}</p>")
            paragraph_buf.clear()

    i = 0
    n = len(lines)
    while i < n:
        raw_ln = lines[i]
        ln = raw_ln.rstrip()
        stripped = ln.strip()

        if not stripped or LONE_NUM_RE.match(stripped):
            flush_paragraph()
            i += 1
            continue

        m_deel = DEEL_BODY_RE.match(ln)
        if m_deel and not is_toc_line(ln):
            if m_deel.group(2):
                # "DEEL N – Titel" running header repeated on every page of
                # this part — its N is not reliable in print, so ignore it.
                i += 1
                continue
            flush_paragraph()
            # bare "DEEL N" divider: title sits on the next non-empty line
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            body_title = lines[j].strip() if j < n else ""
            i = j
            extra, j2 = absorb_continuation(lines, i + 1, n)
            if extra:
                body_title = (body_title + " " + " ".join(extra)).strip()
                i = j2 - 1
            if deel_idx < len(deel_queue):
                deel_num, title = deel_queue[deel_idx]
                deel_idx += 1
            else:
                deel_num, title = m_deel.group(1), body_title
            title = title.upper()
            current_part_title = title
            anchor = f"deel-{deel_num}"
            html_parts.append(f'<h2 id="{anchor}" class="deel">DEEL {deel_num} — {esc(title)}</h2>')
            toc_parts.append(("deel", anchor, f"DEEL {deel_num} — {title}"))
            i += 1
            continue

        if not is_toc_line(ln):
            m_sub = SUBSECTION_RE.match(ln)
            m_sec = SECTION_RE.match(ln) if not m_sub else None
            m_chap = CHAPTER_RE.match(ln) if not m_sub and not m_sec else None
            if m_chap and not LETTERS_RE.search(m_chap.group(2)):
                m_chap = None  # reject page-edge index-tab artifacts (e.g. "13 A")
            if m_chap and m_chap.group(1) in seen_chap_nums:
                m_chap = None  # reject repeated running-header artifacts

            if m_sub:
                flush_paragraph()
                num, title = m_sub.group(1), m_sub.group(2).strip()
                title = toc_titles.get(num, title)
                anchor = num.replace(".", "-")
                html_parts.append(f'<h4 id="h{anchor}">{esc(num)} {esc(title)}</h4>')
                toc_parts.append(("sub", f"h{anchor}", f"{num} {title}"))
                i += 1
                continue
            if m_sec:
                flush_paragraph()
                num, title = m_sec.group(1), m_sec.group(2).strip()
                extra, j2 = absorb_continuation(lines, i + 1, n)
                if extra:
                    title = (title + " " + " ".join(extra)).strip()
                    i = j2 - 1
                title = toc_titles.get(num, title).upper()
                anchor = num.replace(".", "-")
                html_parts.append(f'<h3 id="h{anchor}">{esc(num)} {esc(title)}</h3>')
                toc_parts.append(("sec", f"h{anchor}", f"{num} {title}"))
                i += 1
                continue
            if m_chap:
                flush_paragraph()
                num, title = m_chap.group(1), m_chap.group(2).strip()
                extra, j2 = absorb_continuation(lines, i + 1, n)
                if extra:
                    title = (title + " " + " ".join(extra)).strip()
                    i = j2 - 1
                title = toc_titles.get(num, title).upper()
                seen_chap_nums.add(num)
                anchor = f"h{num}"
                html_parts.append(f'<h3 class="chapter" id="{anchor}">{esc(num)}. {esc(title)}</h3>')
                toc_parts.append(("chap", anchor, f"{num}. {title}"))
                i += 1
                continue

        paragraph_buf.append(stripped)
        i += 1

    flush_paragraph()
    return "\n".join(html_parts), toc_parts

def render_toc(toc_parts):
    out = ['<nav class="toc" aria-label="Inhoudsopgave"><ul>']
    for kind, anchor, title in toc_parts:
        cls = {"deel": "toc-deel", "chap": "toc-chap", "sec": "toc-sec", "sub": "toc-sub"}[kind]
        out.append(f'<li class="{cls}"><a href="#{anchor}">{esc(title)}</a></li>')
    out.append("</ul></nav>")
    return "\n".join(out)

PAGE_TMPL = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — NVHP Syllabus Hypothecair Planner</title>
<meta name="description" content="Boek {num}: {title} — Syllabus Leergang Hypothecair Planner, NVHP 2025.">
<link rel="stylesheet" href="style.css">
<script>
function printWithPassword(slug) {{
  var pw = window.prompt("Voer het wachtwoord in om te printen.\n\nWilt u de volledige syllabus (alle boeken) printen? Vraag dit aan via info@hypothecairplanner.nl.");
  if (pw === null) return;
  if (pw === "Agaat") {{
    window.open(slug + ".html", "_blank").print();
  }} else {{
    window.alert("Onjuist wachtwoord.");
  }}
}}
</script>
</head>
<body>
<header class="site-header no-print">
  <div class="header-inner">
    <a class="brand" href="index.html">NVHP · Leergang Hypothecaire Planning</a>
    <nav class="header-nav" aria-label="Boeken en pagina's">
      <a href="boek1.html">Boek 1</a>
      <a href="boek2.html">Boek 2</a>
      <a href="boek3.html">Boek 3</a>
      <a href="boek4.html">Boek 4</a>
      <a href="bijlagen.html">Bijlagen</a>
      <a href="wijzigingen.html">Wijzigingen</a>
    </nav>
    <div class="header-search">
      <input type="search" id="site-search" placeholder="Zoek in alle boeken…" autocomplete="off" aria-label="Zoek in alle boeken">
      <div id="search-results" class="search-results" hidden></div>
    </div>
    <button class="print-btn" onclick="printWithPassword('{slug}')">Print dit boek</button>
  </div>
</header>
<section class="book-intro">
  <h1 class="book-title">Boek {num} — {title}</h1>
  <p class="book-subtitle">{subtitle}</p>
  <p class="copyright-note">© Nederlandse Vereniging van Hypothecair Planners (NVHP), april 2025. Uitsluitend voor eigen studiegebruik binnen de Leergang Hypothecaire Planning.</p>
</section>
<div class="layout">
  <aside class="sidebar">
    <a class="back-link" href="index.html">&larr; Alle boeken</a>
    <h1 class="book-label">Boek {num}<br>{title}</h1>
    {toc}
  </aside>
  <main class="content">
    {body}
  </main>
</div>
<footer class="site-footer no-print">
  <p>© NVHP 2025 — Leergang Hypothecaire Planning · Artikelnummer NVHP-SYLL202503/{num} · <a href="wijzigingen.html">Wijzigingenlog</a></p>
  <p class="footer-contact">Nederlandse Vereniging van Hypothecair Planners · De Wel 14-16, 3871 MV Hoevelaken · 033 - 254 20 12 · <a href="mailto:info@hypothecairplanner.nl">info@hypothecairplanner.nl</a> · <a href="https://www.hypothecairplanner.nl" target="_blank" rel="noopener">hypothecairplanner.nl</a></p>
  <p style="font-size:.75rem;opacity:.7;margin-top:4px;">Let op: dit bestand wordt gegenereerd uit de brontekst. Na een rebuild moeten scripts/apply_2026_updates(_part2).py en scripts/build_search_index.py opnieuw worden gedraaid — zie wijzigingen.html.</p>
</footer>
<script src="search.js" defer></script>
</body>
</html>
"""

def main():
    index_cards = []
    for book in BOOKS:
        print(f"Verwerken: {book['title']}...", file=sys.stderr)
        body, toc_parts = build_book_html(book)
        toc_html = render_toc(toc_parts)
        page = PAGE_TMPL.format(
            title=esc(book["title"]), num=book["num"], slug=book["slug"],
            subtitle=esc(book["subtitle"]), toc=toc_html, body=body,
        )
        outpath = os.path.join(OUT_DIR, f"{book['slug']}.html")
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"  -> {outpath} ({len(body)} bytes body, {len(toc_parts)} headings)", file=sys.stderr)
        index_cards.append(book)
    return index_cards

if __name__ == "__main__":
    main()
