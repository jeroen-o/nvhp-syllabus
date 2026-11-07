#!/usr/bin/env python3
"""
Haalt de actuele catalogus van NVHP-masterclasses op van
https://mc.hypothecairplanner.nl/ (het NVHP-opleidingsportaal) en
schrijft een compacte JSON-lijst met titel, url, korte omschrijving,
prijs en PE-puntencode weg naar scripts/masterclasses_data.json.

Alle gebruikte content is publiek (geen login vereist).

Bedoeld om herhaaldelijk (bijv. wekelijks) gedraaid te worden zodat de
masterclass-content op de site actueel blijft — zie scripts/check_masterclasses.py
voor de wekelijkse controle die dit script aanroept en een rapport maakt.

Run: python3 scripts/fetch_masterclasses.py
"""
import html as html_lib
import json
import re
import subprocess
import sys
import time
from datetime import date, datetime, timezone

REPO = "/home/user/nvhp-syllabus"
BASE = "https://mc.hypothecairplanner.nl"
CATALOG_KEY = '"1AC6ED44F7B0484DA39F894C0371BEA5"'
OUT_PATH = f"{REPO}/scripts/masterclasses_data.json"

SKIP_SLUGS = {"3-daagse-leergang-financieel-relatie-adviseur"}  # meerdaagse opleiding, geen masterclass

# Voor een enkele cursuspagina staat er geen bruikbare omschrijving in het
# standaard contentblok (bv. alleen een docentbio). Handmatige, beknopte
# aanvulling i.p.v. een lege/onbruikbare omschrijving op de site.
MANUAL_DESCRIPTIONS = {
    "senioren-en-overwaarde": (
        "Adviseren over overwaarde en wonen voor de oudere klant: "
        "financiële mogelijkheden en aandachtspunten bij senioren in beeld."
    ),
}


def fetch(url, timeout=25):
    try:
        out = subprocess.run(
            ["curl", "-sS", "--max-time", str(timeout), url],
            capture_output=True, timeout=timeout + 5,
        )
        if out.returncode != 0:
            return None
        return out.stdout.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  fout bij ophalen {url}: {e}", file=sys.stderr)
        return None


def fetch_catalog():
    html = fetch(f"{BASE}/")
    if not html:
        raise RuntimeError("kon homepage niet ophalen")
    idx = html.find(CATALOG_KEY)
    if idx == -1:
        raise RuntimeError("catalogus-blok niet gevonden op homepage (pagina-structuur gewijzigd?)")
    start = html.find("[", idx)
    raw = html[start:]
    # de embedded JS-JSON gebruikt soms \' wat geen geldige JSON-escape is
    raw_fixed = raw.replace("\\'", "'")
    dec = json.JSONDecoder()
    data, _end = dec.raw_decode(raw_fixed)
    rows = []
    for row in data:
        c = row.get("columns", {})
        title = (c.get("KnWCITitl", {}).get("value") or "").strip()
        link = row.get("link") or ""
        price = c.get("U002", {}).get("value") or ""
        points = c.get("U003", {}).get("value") or ""
        if not title or not link:
            continue
        rows.append({"titel": title, "link": link, "prijs": price, "punten": points})
    return rows


def normalize_price(price):
    # "€ 162.50" -> "€ 162,50"; laat "€ 1.500,00" (duizendtal) met rust
    m = re.match(r"^€\s*([\d.,]+)$", price.strip())
    if not m:
        return price.strip()
    num = m.group(1)
    if re.match(r"^\d+\.\d{2}$", num):  # bv 162.50 -> decimaalpunt, geen duizendtal
        num = num.replace(".", ",")
    return f"€ {num}"


def strip_html(fragment):
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = html_lib.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


JUNK_PATTERNS = re.compile(
    r"javascript|laptop of tablet meenemen|is verbonden als docent|docent op het gebied"
    r"|het bestuur van de nvhp|professional op het gebied|ervaren financieel adviseur"
    r"|stap gemaakt om bij|in \d{4} heb ik|cookie|inloggen|wachtwoord",
    re.I,
)


def extract_description(page_html, title):
    # strip head (title/meta leveren geen bruikbare contenttekst), script/style
    cleaned = re.sub(r"<head.*?</head>", " ", page_html, flags=re.S)
    cleaned = re.sub(r"<script.*?</script>", " ", cleaned, flags=re.S)
    cleaned = re.sub(r"<style.*?</style>", " ", cleaned, flags=re.S)

    # de hoofdomschrijving van een cursus staat steevast in het eerste
    # content-blok van het type "content freehtml" (zowel met als zonder
    # een "Doel:"-kopje) — dat is een veel betrouwbaarder anker dan zoeken
    # naar het woord "Doel:" zelf, en voorkomt dat we in latere,
    # niet-gerelateerde pagina-secties (docentbio, footer) belanden.
    block_idx = cleaned.find('class="content freehtml"')
    if block_idx != -1:
        search_region = cleaned[block_idx : block_idx + 3500]
    else:
        doel_idx = cleaned.find("Doel:")
        search_region = cleaned[doel_idx : doel_idx + 3500] if doel_idx != -1 else cleaned

    # pak de paragraaf-achtige tekstblokken (tussen tags) in dat gebied
    chunks = re.split(r"<(?:p|div|li)[^>]*>", search_region)
    title_norm = re.sub(r"\s+", " ", title).strip().lower()
    candidates = []
    for chunk in chunks:
        text = strip_html(chunk.split("</")[0] if "</" in chunk else chunk)
        if len(text) <= 40:
            continue
        if "doel:" in text.lower():
            continue
        if JUNK_PATTERNS.search(text):
            continue
        # sla over als de tekst (vrijwel) letterlijk de titel herhaalt
        tl = text.lower().rstrip(".!? ")
        if tl == title_norm or tl.startswith(title_norm) and len(tl) < len(title_norm) + 15:
            continue
        candidates.append(text)
        if len(candidates) >= 3:
            break

    if not candidates:
        return None

    desc = candidates[0]
    # inkorten tot ~160 tekens op een woordgrens, eindigend op een punt waar mogelijk
    if len(desc) > 160:
        cutoff = desc.rfind(". ", 0, 160)
        if cutoff > 60:
            desc = desc[: cutoff + 1]
        else:
            cutoff = desc.rfind(" ", 0, 157)
            desc = desc[: cutoff if cutoff > 0 else 157].rstrip(",;: ") + "…"
    return desc.strip()


def slug_from_link(link):
    return link.rstrip("/").split("/")[-1]


def main():
    print("Catalogus ophalen van mc.hypothecairplanner.nl...")
    rows = fetch_catalog()
    print(f"{len(rows)} cursussen gevonden in catalogus.")

    results = []
    for i, row in enumerate(rows, 1):
        slug = slug_from_link(row["link"])
        url = BASE + row["link"]
        item_type = "opleiding" if slug in SKIP_SLUGS else "masterclass"

        print(f"[{i}/{len(rows)}] {row['titel']} ({slug})...")
        page_html = fetch(url)
        omschrijving = None
        if page_html:
            omschrijving = extract_description(page_html, row["titel"])
        if not omschrijving:
            if slug in MANUAL_DESCRIPTIONS:
                omschrijving = MANUAL_DESCRIPTIONS[slug]
                print(f"  (handmatige omschrijving gebruikt voor {slug})")
            else:
                print(f"  WAARSCHUWING: geen omschrijving gevonden voor {slug}", file=sys.stderr)
                omschrijving = ""

        titel = re.sub(r"\s+", " ", row["titel"]).strip()
        results.append({
            "titel": titel,
            "slug": slug,
            "url": url,
            "omschrijving": omschrijving,
            "prijs": normalize_price(row["prijs"]),
            "punten": row["punten"].strip(),
            "type": item_type,
        })
        time.sleep(0.4)

    payload = {
        "updated_on": date.today().isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": f"{BASE}/",
        "items": results,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    n_ok = sum(1 for r in results if r["omschrijving"])
    n_missing = len(results) - n_ok
    print(f"\nKlaar: {len(results)} items weggeschreven naar {OUT_PATH}")
    print(f"  {n_ok} met omschrijving, {n_missing} zonder (zie waarschuwingen hierboven).")
    return payload


if __name__ == "__main__":
    main()
