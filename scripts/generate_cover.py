#!/usr/bin/env python3
"""
Genereert een omslagmockup van de gedrukte NVHP-syllabus (zoals de
Wolters Kluwer Wettenbundel-foto die als voorbeeld is aangeleverd):
een rechtopstaand boek met een lichte 3D-schaduw, in NVHP-huisstijl,
met het echte NVHP-logo.

Vereist: logo-white.png (gegenereerd/opgehaald eerder in deze repo).
Run: python3 scripts/generate_cover.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = "/home/user/nvhp-syllabus"
NAVY = (35, 71, 101)
NAVY_DARK = (24, 45, 64)
NAVY_DEEP = (16, 30, 44)
RED = (231, 68, 59)
WHITE = (255, 255, 255)

FONT_BLACK = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def draw_cover(w, h):
    """Platte voorkant van het boek, portret-formaat."""
    img = Image.new("RGB", (w, h), NAVY)
    d = ImageDraw.Draw(img)

    # diagonale gradient navy -> donkerder navy
    for y in range(h):
        t = y / h
        c = tuple(int(NAVY[i] + (NAVY_DEEP[i] - NAVY[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)

    # rode accentbalk onderaan (als bij de Wettenbundel-stijl) + bovenaan dun randje
    d.rectangle([0, 0, w, int(h * 0.012)], fill=RED)
    d.rectangle([0, h - int(h * 0.09), w, h], fill=RED)
    d.rectangle([0, h - int(h * 0.09) - 4, w, h - int(h * 0.09)], fill=NAVY_DARK)

    # logo (wit, transparant) bovenin
    logo = Image.open(f"{REPO}/logo-white.png").convert("RGBA")
    logo_w = int(w * 0.52)
    logo_h = int(logo.size[1] * logo_w / logo.size[0])
    logo_r = logo.resize((logo_w, logo_h), Image.LANCZOS)
    img.paste(logo_r, ((w - logo_w) // 2, int(h * 0.07)), logo_r)

    top_text_y = int(h * 0.07) + logo_h + int(h * 0.05)

    # dunne scheidingslijn
    d.line([(int(w * 0.14), top_text_y), (w - int(w * 0.14), top_text_y)], fill=(255, 255, 255, 120), width=2)

    # "SYLLABUS" kicker
    kicker_font = ImageFont.truetype(FONT_BLACK, int(w * 0.052))
    kicker = "SYLLABUS"
    bbox = d.textbbox((0, 0), kicker, font=kicker_font)
    d.text(((w - (bbox[2] - bbox[0])) / 2, top_text_y + int(h * 0.025)), kicker, font=kicker_font, fill=RED)

    # titel
    title_font = ImageFont.truetype(FONT_BLACK, int(w * 0.088))
    lines = ["Leergang", "Hypothecaire", "Planning"]
    ty = top_text_y + int(h * 0.09)
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=title_font)
        d.text(((w - (bbox[2] - bbox[0])) / 2, ty), line, font=title_font, fill=WHITE)
        ty += int(h * 0.092)

    # subtitel / editie
    sub_font = ImageFont.truetype(FONT_REG, int(w * 0.036))
    sub = "Opleiding tot Erkend Hypothecair Planner"
    bbox = d.textbbox((0, 0), sub, font=sub_font)
    d.text(((w - (bbox[2] - bbox[0])) / 2, ty + int(h * 0.02)), sub, font=sub_font, fill=(199, 203, 214))

    # editie-badge onderin (boven de rode balk)
    badge_font = ImageFont.truetype(FONT_BLACK, int(w * 0.04))
    badge = "EDITIE 2025"
    bbox = d.textbbox((0, 0), badge, font=badge_font)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = int(w * 0.025)
    bx0 = (w - bw) / 2 - pad
    by0 = h - int(h * 0.09) - int(h * 0.075)
    d.rounded_rectangle([bx0, by0, bx0 + bw + pad * 2, by0 + bh + pad * 1.6], radius=int(pad * 0.9),
                         outline=WHITE, width=2)
    d.text(((w - bw) / 2, by0 + pad * 0.3), badge, font=badge_font, fill=WHITE)

    return img


def composite_shelf_image(cover, out_w=900, out_h=900):
    """Plaatst de platte cover vrijstaand met een zachte schaduw, zoals de
    productfoto van de Wettenbundel (vrijstaand boek op neutrale achtergrond)."""
    canvas = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))

    book_h = int(out_h * 0.86)
    book_w = int(book_h * (cover.size[0] / cover.size[1]))
    book = cover.resize((book_w, book_h), Image.LANCZOS).convert("RGBA")

    # lichte 'dikte' van het boek rechts (rug/edge) voor een subtiel 3D-effect
    spine_w = max(6, int(book_w * 0.035))
    spine = Image.new("RGBA", (spine_w, book_h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spine)
    for x in range(spine_w):
        t = x / spine_w
        shade = tuple(int(255 * (0.55 + 0.35 * t)) for _ in range(3))
        sd.line([(x, 0), (x, book_h)], fill=shade + (255,))
    # pagina-randje (lichte strepen) voor een "boek dat openligt om te bladeren"-gevoel
    pages = Image.new("RGBA", (spine_w, book_h), (255, 255, 255, 255))

    bx = (out_w - book_w - spine_w) // 2
    by = (out_h - book_h) // 2 - int(out_h * 0.02)

    # schaduw
    shadow = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse(
        [bx - 10, by + book_h - int(book_h * 0.03), bx + book_w + spine_w + 10, by + book_h + int(out_h * 0.09)],
        fill=(10, 16, 26, 130),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(out_h * 0.025))
    canvas = Image.alpha_composite(canvas, shadow)

    canvas.paste(pages, (bx + book_w, by), pages)
    canvas.paste(spine, (bx + book_w, by), spine)
    canvas.paste(book, (bx, by), book)

    return canvas


if __name__ == "__main__":
    cover = draw_cover(900, 1260)
    cover.save(f"{REPO}/syllabus-omslag-flat.png", optimize=True)

    shelf = composite_shelf_image(cover, 900, 900)
    shelf.save(f"{REPO}/syllabus-omslag.png", optimize=True)
    print("omslag opgeslagen: syllabus-omslag.png, syllabus-omslag-flat.png")
