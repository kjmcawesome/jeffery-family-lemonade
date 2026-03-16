from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
OUTPUT.mkdir(parents=True, exist_ok=True)

PDF_PATH = OUTPUT / "jeffery-family-lemonade-community-one-pager.pdf"
QR_PATH = ROOT / "qr-code.png"
MAP_PATH = ROOT / "google-maps-area.png"

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.4 * inch
CONTENT_W = PAGE_WIDTH - (2 * MARGIN)

PALETTE = {
    "paper": colors.HexColor("#fff9ec"),
    "ink": colors.HexColor("#23170b"),
    "muted": colors.HexColor("#604b25"),
    "cream": colors.HexColor("#fffdf6"),
    "yellow": colors.HexColor("#ffd84b"),
    "yellow_deep": colors.HexColor("#efb91d"),
    "line": colors.HexColor("#c89e3d"),
    "black": colors.HexColor("#17120c"),
    "market": colors.HexColor("#ee6c4d"),
}


def pstyle(font="Helvetica", size=12, leading=None, color=None, alignment=0):
    return ParagraphStyle(
        name=f"{font}-{size}-{alignment}",
        fontName=font,
        fontSize=size,
        leading=leading or size * 1.2,
        textColor=color or PALETTE["muted"],
        alignment=alignment,
    )


def draw_paragraph(c, text, x, y_top, width, style):
    para = Paragraph(text, style)
    _, height = para.wrap(width, 1000)
    para.drawOn(c, x, y_top - height)
    return height


def build_pdf():
    c = canvas.Canvas(str(PDF_PATH), pagesize=letter)
    c.setTitle("Jeffery Family Lemonade Community One-Pager")

    c.setFillColor(PALETTE["paper"])
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    c.setFillColor(PALETTE["black"])
    c.setStrokeColor(PALETTE["black"])
    c.setLineWidth(4)
    c.rect(MARGIN, MARGIN, CONTENT_W, PAGE_HEIGHT - 2 * MARGIN, fill=0, stroke=1)

    top_band_h = 26
    top_y = PAGE_HEIGHT - MARGIN - top_band_h
    c.setFillColor(PALETTE["black"])
    c.rect(MARGIN, top_y, CONTENT_W, top_band_h, fill=1, stroke=0)
    top_style = pstyle(font="Helvetica-Bold", size=11, color=colors.HexColor("#fff6dd"), alignment=1)
    draw_paragraph(c, "ONE AFTERNOON ONLY   •   SATURDAY, MARCH 21, 2026   •   MENLO PARK", MARGIN, top_y + 18, CONTENT_W, top_style)

    hero_y = top_y - 182
    hero_h = 168
    hero_w = CONTENT_W - 180
    qr_w = 166

    c.setFillColor(PALETTE["yellow"])
    c.rect(MARGIN, hero_y, hero_w, hero_h, fill=1, stroke=1)
    c.setFillColor(PALETTE["cream"])
    c.rect(MARGIN + hero_w - 2, hero_y + 20, qr_w, hero_h - 8, fill=1, stroke=1)

    kicker = pstyle(font="Helvetica-Bold", size=11, color=PALETTE["muted"])
    title = pstyle(font="Helvetica-Bold", size=36, leading=33, color=PALETTE["ink"])
    body = pstyle(font="Helvetica", size=13.5, leading=16.5, color=colors.HexColor("#3f3015"))
    qr_body = pstyle(font="Helvetica-Bold", size=11, leading=14, color=PALETTE["muted"], alignment=1)

    hero_top = hero_y + hero_h - 16
    hero_top -= draw_paragraph(c, "JEFFERY FAMILY LEMONADE", MARGIN + 16, hero_top, hero_w - 32, kicker) + 6
    hero_top -= draw_paragraph(c, "LEMONADE<br/>THIS SATURDAY", MARGIN + 16, hero_top, hero_w - 36, title) + 10
    draw_paragraph(
        c,
        "Come by between <b>noon and 3pm</b> for a bright neighborhood stop with kid-built lemonade, cheerful signs, and sunny energy.",
        MARGIN + 16,
        hero_top,
        hero_w - 36,
        body,
    )

    pill_y = hero_y - 56
    pill_w = (CONTENT_W - 20) / 3
    pill_style = pstyle(font="Helvetica-Bold", size=13, color=PALETTE["ink"])
    pill_sub = pstyle(font="Helvetica-Bold", size=14, leading=16, color=PALETTE["muted"])
    pills = [
        ("WHEN", "Saturday, March 21, 2026"),
        ("TIME", "Noon to 3pm"),
        ("WHERE", "Blackburn + Marmona, Menlo Park"),
    ]
    for idx, (label, value) in enumerate(pills):
        px = MARGIN + idx * (pill_w + 10)
        c.setFillColor(PALETTE["cream"])
        c.rect(px, pill_y, pill_w, 46, fill=1, stroke=1)
        draw_paragraph(c, label, px + 10, pill_y + 34, pill_w - 20, pill_style)
        draw_paragraph(c, value, px + 10, pill_y + 18, pill_w - 20, pill_sub)

    c.drawImage(str(QR_PATH), MARGIN + hero_w + 20, hero_y + 74, width=126, height=126, mask="auto")
    qr_top = hero_y + 52
    qr_top -= draw_paragraph(c, "Scan for site", MARGIN + hero_w + 10, qr_top, 146, pstyle(font="Helvetica-Bold", size=16, leading=18, color=PALETTE["ink"], alignment=1)) + 10
    draw_paragraph(c, "Map and menu.", MARGIN + hero_w + 16, qr_top, 134, qr_body)

    map_x = MARGIN
    map_y = MARGIN + 156
    map_w = 4.45 * inch
    map_h = 3.35 * inch

    c.setFillColor(PALETTE["cream"])
    c.rect(map_x, map_y, map_w, map_h, fill=1, stroke=1)
    draw_paragraph(c, "FIND THE STAND", map_x + 16, map_y + map_h - 16, map_w - 32, kicker)
    draw_paragraph(c, "Look for us just past Willows Market", map_x + 16, map_y + map_h - 34, map_w - 32, pstyle(font="Helvetica-Bold", size=22, leading=24, color=PALETTE["ink"]))
    c.setFillColor(PALETTE["cream"])
    c.rect(map_x + 16, map_y + 28, map_w - 32, 180, fill=1, stroke=1)
    c.drawImage(str(MAP_PATH), map_x + 16, map_y + 28, width=map_w - 32, height=180, mask="auto")
    draw_paragraph(c, "Google Maps area view with the stand marked near Blackburn + Marmona and Willows Market included as a landmark.", map_x + 16, map_y + 24, map_w - 32, pstyle(font="Helvetica", size=11.5, leading=14, color=PALETTE["muted"]))

    info_x = map_x + map_w + 14
    info_w = CONTENT_W - map_w - 14
    bot_info_h = 106
    info_gap = 12
    top_info_y = map_y + bot_info_h + info_gap
    top_info_h = map_h - bot_info_h - info_gap

    c.setFillColor(colors.HexColor("#fff4bf"))
    c.rect(info_x, top_info_y, info_w, top_info_h, fill=1, stroke=1)
    info_top = top_info_y + top_info_h - 16
    info_top -= draw_paragraph(c, "WHY COME BY", info_x + 14, info_top, info_w - 28, kicker) + 4
    info_top -= draw_paragraph(c, "A sweet little neighborhood stop", info_x + 14, info_top, info_w - 28, pstyle(font="Helvetica-Bold", size=18, leading=20, color=PALETTE["ink"])) + 8
    bullet = pstyle(font="Helvetica", size=12.5, leading=16, color=PALETTE["muted"])
    info_top -= draw_paragraph(c, "• Fresh lemonade made together as a kid-and-parent project.", info_x + 14, info_top, info_w - 28, bullet) + 4
    draw_paragraph(c, "• Easy stop for families, classmates, teachers, and neighbors.", info_x + 14, info_top, info_w - 28, bullet)

    c.setFillColor(PALETTE["black"])
    c.rect(info_x, map_y, info_w, bot_info_h, fill=1, stroke=1)
    light_kicker = pstyle(font="Helvetica-Bold", size=11, color=colors.HexColor("#f6e5b1"))
    light_body = pstyle(font="Helvetica", size=12.5, leading=16, color=colors.HexColor("#f6e5b1"))
    menu_top = map_y + bot_info_h - 14
    menu_top -= draw_paragraph(c, "ON THE STAND", info_x + 14, menu_top, info_w - 28, light_kicker) + 4
    menu_top -= draw_paragraph(c, "Classic Sunshine, Berry Blush, and Frozen Lemondade.", info_x + 14, menu_top, info_w - 28, pstyle(font="Helvetica-Bold", size=16, leading=18, color=colors.HexColor("#fff4cf"))) + 8
    draw_paragraph(c, "Use the QR code for the full flyer, menu, and directions.", info_x + 14, menu_top, info_w - 28, pstyle(font="Helvetica", size=11.5, leading=14, color=colors.HexColor("#f6e5b1")))

    footer_h = 96
    c.setFillColor(PALETTE["black"])
    c.rect(MARGIN, MARGIN + 12, CONTENT_W, footer_h, fill=1, stroke=0)
    footer_top = MARGIN + footer_h - 4
    footer_top -= draw_paragraph(c, "COME THROUGH", MARGIN + 16, footer_top, 160, light_kicker) + 4
    footer_top -= draw_paragraph(c, "NOON TO 3PM AT BLACKBURN + MARMONA", MARGIN + 16, footer_top, 430, pstyle(font="Helvetica-Bold", size=20, leading=21, color=colors.HexColor("#fff4cf"))) + 8

    c.showPage()
    c.save()


if __name__ == "__main__":
    build_pdf()
    print(PDF_PATH)
