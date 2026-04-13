from pathlib import Path
import re
import shutil

from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "pdf"
TMP_DIR = ROOT / "tmp" / "pdfs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

FLYER_PDF = OUTPUT_DIR / "jeffery-family-lemonade-community-one-pager.pdf"
MENU_PDF = OUTPUT_DIR / "jeffery-family-lemonade-stand-menu.pdf"
FLYER_DOWNLOAD = Path("/Users/kj/Downloads/jeffery-family-lemonade-community-one-pager.pdf")
MENU_DOWNLOAD = Path("/Users/kj/Downloads/jeffery-family-lemonade-stand-menu.pdf")

PAGE_W, PAGE_H = letter

INK = colors.HexColor("#2d2412")
MUTED = colors.HexColor("#5d4a28")
LINE = colors.HexColor("#d6bf7a")
PAPER = colors.HexColor("#fffef7")
CARD = colors.HexColor("#fff9e2")
YELLOW = colors.HexColor("#f5c93a")
YELLOW_SOFT = colors.HexColor("#fff2b8")
GREEN = colors.HexColor("#35a926")
GREEN_DARK = colors.HexColor("#27831c")
WOOD = colors.HexColor("#c78126")
WOOD_DARK = colors.HexColor("#935b18")
RED = colors.HexColor("#df3b30")


def draw_round(c, x, y, w, h, r=14, fill=CARD, stroke=LINE, sw=1.6):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(sw)
    c.roundRect(x, y, w, h, r, stroke=1, fill=1)


def text(c, value, x, y, size=12, font="Helvetica", color=INK, leading=None):
    c.setFillColor(color)
    c.setFont(font, size)
    if leading is None:
        c.drawString(x, y, value)
        return
    box = c.beginText(x, y)
    box.setFont(font, size)
    box.setFillColor(color)
    box.setLeading(leading)
    for line in value.splitlines():
        box.textLine(line)
    c.drawText(box)


def centered(c, value, x, y, w, size=12, font="Helvetica-Bold", color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(x + (w / 2), y, value)


def wrap_lines(c, value, max_width, font, size):
    words = value.split()
    lines = []
    current = ""
    c.setFont(font, size)
    for word in words:
        candidate = f"{current} {word}".strip()
        if c.stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paragraph(c, value, x, y, max_width, size=11, leading=15, font="Helvetica", color=MUTED):
    for line in wrap_lines(c, value, max_width, font, size):
        text(c, line, x, y, size=size, font=font, color=color)
        y -= leading
    return y


def svg_qr_to_png(svg_path, png_path, fill="#111111", quiet=16):
    svg = Path(svg_path).read_text()
    width = int(re.search(r'width="(\d+)"', svg).group(1))
    height = int(re.search(r'height="(\d+)"', svg).group(1))
    scale = int(re.search(r'transform="scale\((\d+)\)"', svg).group(1))
    path = re.search(r'd="([^"]+)"', svg).group(1)
    tokens = re.findall(r"[MmHh]|-?\d+(?:\.\d+)?", path)

    img = Image.new("RGB", (width + quiet * 2, height + quiet * 2), "white")
    draw = ImageDraw.Draw(img)
    x = y = 0.0
    idx = 0
    while idx < len(tokens):
        token = tokens[idx]
        idx += 1
        if token == "M":
            x = float(tokens[idx])
            y = float(tokens[idx + 1])
            idx += 2
        elif token == "m":
            x += float(tokens[idx])
            y += float(tokens[idx + 1])
            idx += 2
        elif token in ("h", "H"):
            length = float(tokens[idx])
            idx += 1
            start_x = x if token == "h" else 0
            end_x = x + length if token == "h" else length
            x0 = min(start_x, end_x) * scale + quiet
            x1 = max(start_x, end_x) * scale + quiet
            y0 = (y - 0.5) * scale + quiet
            y1 = (y + 0.5) * scale + quiet
            draw.rectangle([x0, y0, x1, y1], fill=fill)
            x = end_x
    img.save(png_path)
    return png_path


def qr_png(name):
    source = ROOT / f"{name}.svg"
    output = TMP_DIR / f"{name}.png"
    color = "#2d2412" if name != "venmo-qr" else "#111111"
    return svg_qr_to_png(source, output, fill=color)


def draw_brand_badge(c, x, y, size=42):
    draw_round(c, x, y, size, size, r=10, fill=colors.HexColor("#ffe58a"), stroke=YELLOW, sw=1.4)
    c.setFillColor(colors.HexColor("#ffd83d"))
    c.circle(x + size * 0.48, y + size * 0.54, size * 0.28, stroke=0, fill=1)
    c.setStrokeColor(colors.HexColor("#ff8f7a"))
    c.setLineWidth(6)
    c.line(x + size * 0.48, y + size * 0.24, x + size * 0.64, y + size * 0.78)


def draw_lemonade_stand(c, x, y, w, h):
    draw_round(c, x, y, w, h, r=14, fill=colors.HexColor("#fff0a8"), stroke=LINE)
    c.setFillColor(colors.HexColor("#ffd13f"))
    c.circle(x + w - 58, y + h - 56, 34, stroke=0, fill=1)

    stand_w = w * 0.58
    stand_x = x + (w - stand_w) / 2
    stand_y = y + 34
    c.setFillColor(GREEN_DARK)
    c.roundRect(stand_x, stand_y + 118, stand_w, 44, 14, stroke=0, fill=1)
    stripe_w = stand_w / 6
    for i in range(6):
        c.setFillColor(GREEN if i % 2 == 0 else colors.HexColor("#ffe84a"))
        c.rect(stand_x + i * stripe_w + 3, stand_y + 121, stripe_w - 4, 38, stroke=0, fill=1)
    c.setFillColor(WOOD_DARK)
    c.rect(stand_x + 30, stand_y + 68, 7, 52, stroke=0, fill=1)
    c.rect(stand_x + stand_w - 37, stand_y + 68, 7, 52, stroke=0, fill=1)
    c.setFillColor(WOOD)
    c.roundRect(stand_x + 20, stand_y + 52, stand_w - 40, 78, 8, stroke=0, fill=1)
    c.setFillColor(WOOD_DARK)
    c.roundRect(stand_x + 12, stand_y + 118, stand_w - 24, 14, 7, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#ffe84a"))
    c.setStrokeColor(WOOD_DARK)
    c.setLineWidth(3)
    c.rect(stand_x + 46, stand_y + 22, stand_w - 92, 42, stroke=1, fill=1)
    centered(c, "Lemonade", stand_x + 46, stand_y + 34, stand_w - 92, size=18, font="Helvetica-Bold", color=GREEN_DARK)
    c.setStrokeColor(colors.white)
    c.setLineWidth(6)
    c.roundRect(stand_x + 62, stand_y + 78, 34, 56, 10, stroke=1, fill=0)
    c.roundRect(stand_x + 92, stand_y + 94, 22, 30, 10, stroke=1, fill=0)
    for cup_x, cup_h in [(stand_x + stand_w - 86, 28), (stand_x + stand_w - 58, 38), (stand_x + stand_w - 30, 48)]:
        c.roundRect(cup_x, stand_y + 82, 18, cup_h, 5, stroke=1, fill=0)


def draw_map_panel(c, x, y, w, h):
    draw_round(c, x, y, w, h, r=13, fill=CARD, stroke=LINE)
    text(c, "FIND US NEAR WILLOWS MARKET", x + 14, y + h - 25, size=9.5, font="Helvetica-Bold", color=MUTED)
    text(c, "Blackburn + Marmona", x + 14, y + h - 50, size=18, font="Helvetica-Bold", color=INK)
    map_path = ROOT / "google-maps-poster-area.png"
    if map_path.exists():
        c.drawImage(ImageReader(str(map_path)), x + 14, y + 34, w - 28, h - 96, preserveAspectRatio=True, anchor="c")
    c.setFillColor(RED)
    pin_x, pin_y = x + (w * 0.33), y + 74
    c.circle(pin_x, pin_y, 7, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.circle(pin_x, pin_y, 3, stroke=0, fill=1)
    text(c, "Pin marks the corner. Scan for directions.", x + 14, y + 16, size=9.5, font="Helvetica", color=MUTED)


def build_flyer():
    c = canvas.Canvas(str(FLYER_PDF), pagesize=letter)
    c.setTitle("Jeffery Family Lemonade Community Flyer")
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_round(c, 14, 14, PAGE_W - 28, PAGE_H - 28, r=20, fill=PAPER, stroke=LINE, sw=2)

    draw_round(c, 28, 660, PAGE_W - 56, 102, r=16, fill=colors.HexColor("#fff8da"), stroke=LINE, sw=1.5)
    draw_brand_badge(c, 42, 696, size=40)
    text(c, "FAMILY-RUN NEIGHBORHOOD POP-UP", 90, 736, size=9, font="Helvetica-Bold", color=MUTED)
    text(c, "Jeffery", 90, 714, size=27, font="Helvetica-Bold", color=INK)
    text(c, "Family", 90, 690, size=27, font="Helvetica-Bold", color=INK)
    text(c, "Lemonade", 90, 666, size=27, font="Helvetica-Bold", color=INK)
    qr = qr_png("map-qr")
    draw_round(c, 410, 688, 160, 50, r=12, fill=PAPER, stroke=LINE, sw=1.2)
    c.drawImage(ImageReader(str(qr)), 418, 690, 46, 46)
    text(c, "Scan for directions", 472, 720, size=11, font="Helvetica-Bold", color=INK)
    text(c, "Open Google Maps", 472, 704, size=9, font="Helvetica", color=MUTED)

    draw_round(c, 28, 548, PAGE_W - 56, 92, r=16, fill=YELLOW_SOFT, stroke=LINE, sw=1.5)
    centered(c, "SATURDAY, MAY 2, 2026", 28, 606, PAGE_W - 56, size=11, font="Helvetica-Bold", color=MUTED)
    centered(c, "Noon to 3pm", 28, 576, PAGE_W - 56, size=34, font="Helvetica-Bold", color=INK)
    centered(c, "Blackburn + Marmona near Willows Market.", 28, 558, PAGE_W - 56, size=11, font="Helvetica", color=MUTED)

    draw_round(c, 28, 300, PAGE_W - 56, 230, r=16, fill=CARD, stroke=LINE, sw=1.5)
    text(c, "FRESH SQUEEZED AND FAMILY APPROVED", 44, 505, size=10, font="Helvetica-Bold", color=MUTED)
    text(c, "Fresh cups", 44, 466, size=31, font="Helvetica-Bold", color=INK)
    text(c, "for a sunny", 44, 433, size=31, font="Helvetica-Bold", color=INK)
    text(c, "afternoon.", 44, 400, size=31, font="Helvetica-Bold", color=INK)
    paragraph(
        c,
        "Classic lemonade and slushy lemonade, served by the Jeffery family.",
        44,
        380,
        195,
        size=10.5,
        leading=14,
    )
    draw_round(c, 44, 312, 104, 32, r=16, fill=PAPER, stroke=LINE, sw=1)
    centered(c, "Classic + slushy", 44, 325, 104, size=10, font="Helvetica-Bold", color=INK)
    draw_round(c, 158, 312, 116, 32, r=16, fill=PAPER, stroke=LINE, sw=1)
    centered(c, "Willows Market", 158, 325, 116, size=10, font="Helvetica-Bold", color=INK)
    draw_lemonade_stand(c, 290, 318, 278, 188)

    draw_map_panel(c, 28, 38, 235, 242)
    draw_round(c, 278, 38, 306, 242, r=13, fill=CARD, stroke=LINE)
    text(c, "MENU BOARD", 294, 254, size=9.5, font="Helvetica-Bold", color=MUTED)
    text(c, "Two stand favorites", 294, 230, size=20, font="Helvetica-Bold", color=INK)
    for idx, (name, desc, price) in enumerate(
        [
            ("Lemonade", "Fresh classic lemonade.", "$2"),
            ("Slushy Lemonade", "Slushy and extra cold.", "$5"),
        ]
    ):
        yy = 154 - idx * 78
        draw_round(c, 294, yy, 274, 56, r=12, fill=PAPER, stroke=LINE, sw=1)
        text(c, name, 310, yy + 34, size=13, font="Helvetica-Bold", color=INK)
        text(c, desc, 310, yy + 16, size=9.5, font="Helvetica", color=MUTED)
        text(c, price, 536, yy + 30, size=15, font="Helvetica-Bold", color=WOOD_DARK)

    c.showPage()
    c.save()


def draw_item(c, x, y, w, h, name, desc, price, slushy=False):
    draw_round(c, x, y, w, h, r=15, fill=PAPER if not slushy else YELLOW_SOFT, stroke=LINE, sw=1.4)
    art_x = x + 18
    art_y = y + 16
    draw_round(c, art_x, art_y, 78, 78, r=12, fill=colors.HexColor("#ffe58a"), stroke=LINE, sw=1)
    if slushy:
        c.setFillColor(colors.HexColor("#fff6bf"))
        c.roundRect(art_x + 22, art_y + 16, 34, 46, 10, stroke=0, fill=1)
        c.setStrokeColor(colors.white)
        c.setLineWidth(4)
        c.roundRect(art_x + 24, art_y + 16, 30, 46, 8, stroke=1, fill=0)
        c.setStrokeColor(GREEN)
        c.setLineWidth(5)
        c.line(art_x + 48, art_y + 26, art_x + 58, art_y + 66)
        c.setFillColor(colors.HexColor("#ffd83d"))
        c.circle(art_x + 46, art_y + 40, 8, stroke=0, fill=1)
    else:
        c.setFillColor(colors.HexColor("#ffd83d"))
        c.circle(art_x + 39, art_y + 42, 28, stroke=0, fill=1)
        c.setFillColor(INK)
        c.circle(art_x + 31, art_y + 49, 2.2, stroke=0, fill=1)
        c.circle(art_x + 47, art_y + 49, 2.2, stroke=0, fill=1)
        c.setStrokeColor(INK)
        c.setLineWidth(2)
        c.arc(art_x + 27, art_y + 32, art_x + 51, art_y + 48, 205, 130)
    text(c, name, x + 116, y + h - 42, size=24, font="Helvetica-Bold", color=INK)
    text(c, desc, x + 116, y + h - 62, size=12, font="Helvetica", color=MUTED)
    c.setFillColor(YELLOW)
    c.setStrokeColor(colors.HexColor("#d79f16"))
    c.setLineWidth(2)
    c.circle(x + w - 58, y + h / 2, 34, stroke=1, fill=1)
    centered(c, price, x + w - 92, y + h / 2 - 8, 68, size=24, font="Helvetica-Bold", color=WOOD_DARK)


def build_menu():
    c = canvas.Canvas(str(MENU_PDF), pagesize=letter)
    c.setTitle("Jeffery Family Lemonade Stand Menu")
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_round(c, 14, 14, PAGE_W - 28, PAGE_H - 28, r=20, fill=PAPER, stroke=LINE, sw=2)

    draw_round(c, 28, 658, PAGE_W - 56, 106, r=16, fill=colors.HexColor("#fff8da"), stroke=LINE, sw=1.5)
    draw_brand_badge(c, 44, 696, size=42)
    text(c, "FRESH SQUEEZED AND FAMILY APPROVED", 98, 736, size=9, font="Helvetica-Bold", color=MUTED)
    text(c, "Jeffery", 98, 714, size=25, font="Helvetica-Bold", color=INK)
    text(c, "Family", 98, 690, size=25, font="Helvetica-Bold", color=INK)
    text(c, "Lemonade", 98, 666, size=25, font="Helvetica-Bold", color=INK)
    draw_round(c, 438, 700, 130, 38, r=19, fill=YELLOW, stroke=colors.HexColor("#d79f16"), sw=1.4)
    centered(c, "Saturday, May 2", 438, 713, 130, size=12, font="Helvetica-Bold", color=INK)

    draw_round(c, 28, 554, PAGE_W - 56, 84, r=16, fill=YELLOW_SOFT, stroke=LINE, sw=1.5)
    centered(c, "SATURDAY, MAY 2, 2026", 28, 610, PAGE_W - 56, size=10, font="Helvetica-Bold", color=MUTED)
    centered(c, "Easy drinks. Easy prices.", 28, 582, PAGE_W - 56, size=31, font="Helvetica-Bold", color=INK)
    centered(c, "Pick your cup, scan to pay, and show us your payment between noon and 3pm.", 28, 562, PAGE_W - 56, size=10.5, font="Helvetica", color=MUTED)

    draw_round(c, 28, 316, PAGE_W - 56, 218, r=16, fill=CARD, stroke=LINE, sw=1.5)
    draw_item(c, 44, 428, PAGE_W - 88, 88, "Lemonade", "Fresh-squeezed classic", "$2")
    draw_item(c, 44, 330, PAGE_W - 88, 88, "Slushy Lemonade", "Icy, extra cold, and sunny", "$5", slushy=True)

    draw_round(c, 28, 38, PAGE_W - 56, 256, r=16, fill=CARD, stroke=LINE, sw=1.5)
    text(c, "PAY HERE", 48, 260, size=9, font="Helvetica-Bold", color=MUTED)
    text(c, "Scan to pay with Venmo", 48, 232, size=23, font="Helvetica-Bold", color=INK)
    text(c, "@Kevin-Jeffery-1", 48, 210, size=16, font="Helvetica-Bold", color=GREEN_DARK)
    paragraph(
        c,
        "Scan the code, send payment, and show us the confirmation at the stand.",
        48,
        190,
        230,
        size=11,
        leading=15,
    )
    draw_round(c, 374, 70, 170, 178, r=14, fill=PAPER, stroke=LINE, sw=1.3)
    venmo_qr = qr_png("venmo-qr")
    c.drawImage(ImageReader(str(venmo_qr)), 396, 104, 126, 126)
    centered(c, "venmo", 374, 86, 170, size=22, font="Helvetica-Bold", color=colors.black)

    c.showPage()
    c.save()


def validate(path):
    reader = PdfReader(str(path))
    if len(reader.pages) != 1:
        raise RuntimeError(f"{path} has {len(reader.pages)} pages")
    page = reader.pages[0]
    if (float(page.mediabox.width), float(page.mediabox.height)) != (612.0, 792.0):
        raise RuntimeError(f"{path} is not Letter size")


def build():
    build_flyer()
    build_menu()
    validate(FLYER_PDF)
    validate(MENU_PDF)
    shutil.copy2(FLYER_PDF, FLYER_DOWNLOAD)
    shutil.copy2(MENU_PDF, MENU_DOWNLOAD)
    print(FLYER_PDF)
    print(MENU_PDF)


if __name__ == "__main__":
    build()
