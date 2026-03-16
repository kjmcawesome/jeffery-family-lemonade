from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
OUTPUT.mkdir(parents=True, exist_ok=True)

PDF_PATH = OUTPUT / "jeffery-family-lemonade-community-one-pager.pdf"
QR_PATH = ROOT / "qr-code.png"


def build_pdf() -> None:
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=0.42 * inch,
        rightMargin=0.42 * inch,
        topMargin=0.42 * inch,
        bottomMargin=0.42 * inch,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="FlyerKicker",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#5d4a28"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="HeroTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=30,
            leading=31,
            textColor=colors.HexColor("#2d2412"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=20,
            textColor=colors.HexColor("#2d2412"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCopy",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#5d4a28"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallLabel",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#5d4a28"),
            spaceAfter=3,
        )
    )

    story = []

    story.append(Paragraph("SCHOOL + COMMUNITY FLYER", styles["FlyerKicker"]))

    hero_text = [
        Paragraph("JEFFERY FAMILY LEMONADE", styles["FlyerKicker"]),
        Paragraph("Lemonade stand this Saturday.", styles["HeroTitle"]),
        Paragraph(
            "Come by on <b>Saturday, March 21, 2026</b> between <b>noon and 3pm</b> for a cheerful "
            "neighborhood stop with kid-built lemonade, bright signs, and sunny energy.",
            styles["BodyCopy"],
        ),
        Spacer(1, 0.14 * inch),
    ]

    event_row = Table(
        [
            [
                Paragraph("<b>WHEN</b><br/>Saturday, March 21, 2026", styles["BodyCopy"]),
                Paragraph("<b>TIME</b><br/>Noon to 3pm", styles["BodyCopy"]),
                Paragraph("<b>WHERE</b><br/>Blackburn + Marmona, Menlo Park", styles["BodyCopy"]),
            ]
        ],
        colWidths=[2.0 * inch, 1.45 * inch, 2.35 * inch],
    )
    event_row.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffef7")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#d6bf7a")),
                ("INNERGRID", (0, 0), (-1, -1), 1, colors.HexColor("#d6bf7a")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    hero_text.append(event_row)

    qr_card = Table(
        [
            [Image(str(QR_PATH), width=1.78 * inch, height=1.78 * inch)],
            [Paragraph("Scan for the full site", styles["SectionTitle"])],
            [Paragraph("Directions, menu, and the online flyer are all in one place.", styles["BodyCopy"])],
        ],
        colWidths=[2.18 * inch],
    )
    qr_card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffef7")),
                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#d6bf7a")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ]
        )
    )

    hero = Table([[hero_text, qr_card]], colWidths=[4.95 * inch, 2.32 * inch])
    hero.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffe588")),
                ("BOX", (0, 0), (-1, -1), 1.8, colors.HexColor("#d6bf7a")),
                ("ROUNDEDCORNERS", (0, 0), (-1, -1), 16),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("TOPPADDING", (0, 0), (-1, -1), 16),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(hero)
    story.append(Spacer(1, 0.16 * inch))

    bullets = ListFlowable(
        [
            ListItem(Paragraph("Fresh lemonade made as a family project.", styles["BodyCopy"])),
            ListItem(Paragraph("Easy drop-in timing for a weekend walk or bike ride.", styles["BodyCopy"])),
            ListItem(
                Paragraph(
                    "Friendly stop for parents, classmates, neighbors, and local supporters.",
                    styles["BodyCopy"],
                )
            ),
        ],
        bulletType="bullet",
        start="circle",
        leftIndent=14,
    )

    why_card = [
        Paragraph("WHY STOP BY", styles["FlyerKicker"]),
        Paragraph("A simple neighborhood event for kids and families", styles["SectionTitle"]),
        bullets,
    ]

    expect_card = [
        Paragraph("WHAT TO EXPECT", styles["FlyerKicker"]),
        Paragraph("Classic favorites will be ready", styles["SectionTitle"]),
        Paragraph("Classic Sunshine, Berry Blush, and Frozen Lemondade.", styles["BodyCopy"]),
        Spacer(1, 0.09 * inch),
        Paragraph("For full menu details and directions, use the QR code above.", styles["BodyCopy"]),
    ]

    lower_cards = Table([[why_card, expect_card]], colWidths=[4.25 * inch, 3.02 * inch])
    lower_cards.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#fff9e5")),
                ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#fff4c2")),
                ("BOX", (0, 0), (-1, -1), 1.4, colors.HexColor("#d6bf7a")),
                ("INNERGRID", (0, 0), (-1, -1), 1.4, colors.HexColor("#d6bf7a")),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(lower_cards)
    story.append(Spacer(1, 0.16 * inch))

    footer_left = [
        Paragraph("FIND US", styles["FlyerKicker"]),
        Paragraph("Corner of Blackburn and Marmona in Menlo Park", styles["SectionTitle"]),
        Paragraph(
            "This handout keeps the location privacy-safe with cross streets only. Use the QR code if you want "
            "the live flyer and map link.",
            styles["BodyCopy"],
        ),
    ]

    footer_right = [
        Paragraph("Come between noon and 3pm", styles["SectionTitle"]),
        Paragraph("One afternoon only. Bring a smile and stop by for a cup.", styles["BodyCopy"]),
    ]

    footer = Table([[footer_left, footer_right]], colWidths=[4.95 * inch, 2.32 * inch])
    footer.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff7d4")),
                ("BOX", (0, 0), (-1, -1), 1.6, colors.HexColor("#d6bf7a")),
                ("INNERGRID", (0, 0), (-1, -1), 1.2, colors.HexColor("#d6bf7a")),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(footer)

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
    print(PDF_PATH)
