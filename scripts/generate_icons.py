#!/usr/bin/env python3
"""
Genereert favicon (svg + png's), apple-touch-icon en og-image.png voor
SEO/GEO (Open Graph / Twitter Card previews, browsertab-icon).

Run: python3 scripts/generate_icons.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

REPO = "/home/user/nvhp-syllabus"
NAVY = (35, 71, 101)
NAVY_DARK = (28, 57, 81)
RED = (231, 68, 59)
WHITE = (255, 255, 255)

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def draw_mark(size, radius_ratio=0.22):
    """Navy rounded square with a white open-book glyph and a red accent bar."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = int(size * radius_ratio)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=NAVY)

    # simple open-book glyph made of two trapezoid-ish pages
    cx, cy = size / 2, size * 0.54
    w = size * 0.56
    h = size * 0.34
    spine_top = (cx, cy - h * 0.32)
    spine_bot = (cx, cy + h * 0.5)
    left_pts = [spine_top, (cx - w / 2, cy - h * 0.18), (cx - w / 2, cy + h * 0.62), spine_bot]
    right_pts = [spine_top, (cx + w / 2, cy - h * 0.18), (cx + w / 2, cy + h * 0.62), spine_bot]
    d.polygon(left_pts, fill=WHITE)
    d.polygon(right_pts, fill=WHITE)
    # spine line
    d.line([spine_top, spine_bot], fill=NAVY, width=max(1, size // 40))

    # red accent dot (top-right), evokes the brand's red accent
    rr = size * 0.13
    d.ellipse([size - rr * 2.1, rr * 0.5, size - rr * 0.1, rr * 2.5], fill=RED)
    return img


def save_favicons():
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="rgb{NAVY}"/>
  <polygon points="32,24 10,30 10,50 32,44" fill="#fff"/>
  <polygon points="32,24 54,30 54,50 32,44" fill="#fff"/>
  <line x1="32" y1="24" x2="32" y2="44" stroke="rgb{NAVY}" stroke-width="2"/>
  <circle cx="50" cy="12" r="7" fill="rgb{RED}"/>
</svg>'''
    with open(f"{REPO}/favicon.svg", "w", encoding="utf-8") as f:
        f.write(svg)

    for size, name in [(16, "favicon-16.png"), (32, "favicon-32.png"), (48, "favicon-48.png")]:
        draw_mark(size * 4).resize((size, size), Image.LANCZOS).save(f"{REPO}/{name}")

    draw_mark(720).resize((180, 180), Image.LANCZOS).save(f"{REPO}/apple-touch-icon.png")

    # multi-size .ico
    icon_sizes = [16, 32, 48]
    imgs = [draw_mark(s * 4).resize((s, s), Image.LANCZOS) for s in icon_sizes]
    imgs[0].save(f"{REPO}/favicon.ico", format="ICO", sizes=[(s, s) for s in icon_sizes])
    print("favicons opgeslagen")


def save_og_image(filename, title_lines, subtitle, brand="NVHP · Nederlandse Vereniging van Hypothecair Planners"):
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # subtle diagonal gradient feel: darker band at bottom
    for y in range(H):
        t = y / H
        c = tuple(int(NAVY[i] + (NAVY_DARK[i] - NAVY[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)

    # red accent bar
    d.rectangle([0, 0, 10, H], fill=RED)

    mark = draw_mark(220)
    img.paste(mark, (80, 90), mark)

    title_font = ImageFont.truetype(FONT_BOLD, 58)
    sub_font = ImageFont.truetype(FONT_REG, 30)
    brand_font = ImageFont.truetype(FONT_BOLD, 26)

    y = 350
    for line in title_lines:
        d.text((80, y), line, font=title_font, fill=WHITE)
        y += 68
    d.text((80, y + 7), subtitle, font=sub_font, fill=(199, 203, 214))
    d.text((80, y + 57), brand, font=brand_font, fill=RED)

    img.save(f"{REPO}/{filename}", optimize=True)
    print(f"{filename} opgeslagen")


if __name__ == "__main__":
    save_favicons()
    save_og_image("og-image.png", ["Syllabus Leergang", "Hypothecaire Planning"],
                  "4 boeken · doorzoekbaar · altijd actueel")
    save_og_image("og-image-masterclasses.png", ["Masterclasses"],
                  "Permanente educatie voor de Erkend Hypothecair Planner")
    save_og_image("og-image-opleiding.png", ["Opleiding", "Hypothecair Planner"],
                  "Wat het u en uw klant oplevert")
