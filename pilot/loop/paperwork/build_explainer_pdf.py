"""Render the authored DRAFT explainer; no dataset or detector access.

The Markdown is authoritative content. This helper only lays out that text.
"""
from pathlib import Path
import re
from xml.sax.saxutils import escape, quoteattr

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "EXPLAINER-DRAFT.md"
OUTPUT = HERE / "EXPLAINER-DRAFT.pdf"
text = SOURCE.read_text()
links = dict(re.findall(r"^\[([^]]+)\]:\s+(.+)$", text, re.M))


def inline(value):
    value = escape(value)
    value = re.sub(r"\[([^]]+)\]\[([^]]+)\]",
                   lambda m: '<link href=' + quoteattr(links[m[2]])
                   + ' color="#24527A">' + m[1] + '</link>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", value)
    return value


body = ParagraphStyle("Body", fontName="Helvetica", fontSize=11.3, leading=15.1,
                      textColor=colors.HexColor("#243244"), spaceAfter=8,
                      alignment=TA_LEFT)
heading = ParagraphStyle("Heading", parent=body, fontName="Helvetica-Bold",
                         fontSize=12.0, leading=15, textColor=colors.HexColor("#24527A"),
                         spaceBefore=8, spaceAfter=4, keepWithNext=True)
title = ParagraphStyle("Title", parent=body, fontName="Helvetica-Bold", fontSize=19,
                       leading=23, textColor=colors.HexColor("#172A40"), spaceAfter=5)
status = ParagraphStyle("Status", parent=body, fontSize=10, leading=13,
                        textColor=colors.HexColor("#5F6C79"), spaceAfter=8)
source_style = ParagraphStyle("Sources", parent=status, fontSize=9.5, leading=12,
                              spaceBefore=5)

story = []
for block in text.strip().split("\n\n"):
    if block.startswith("["):
        continue
    if block.startswith("# "):
        story.append(Paragraph(inline(block[2:]), title))
    elif block.startswith("## "):
        story.append(Paragraph(inline(block[3:]), heading))
    elif block.startswith("*Draft"):
        story.append(Paragraph(inline(block), status))
    else:
        story.append(Paragraph(inline(block.replace("\n", " ")), body))
source_text = "Sources: " + ", ".join(
    '<link href=' + quoteattr(links[key]) + ' color="#24527A">' + label + '</link>'
    for key, label in (("results", "saved simulation results"), ("pilot", "pilot guide"),
                       ("scoring", "scoring draft"))) + "."
story.append(Paragraph(source_text, source_style))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D6DEE7"))
    canvas.line(36, 33, A4[0] - 36, 33)
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#5F6C79"))
    canvas.drawString(36, 20, "Draft discussion material - no real utility performance established")
    canvas.drawRightString(A4[0] - 36, 20, str(doc.page))
    canvas.restoreState()


document = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=36, leftMargin=36,
                             topMargin=34, bottomMargin=45,
                             title="Bubble Man: a first utility-data trial (DRAFT)",
                             author="Bubble Man project")
document.build(story, onFirstPage=footer, onLaterPages=footer)
reader = PdfReader(OUTPUT)
assert len(reader.pages) == 1, "The explainer must be one readable page; revise content/layout"
extracted = reader.pages[0].extract_text()
for phrase in ("1,000", "89%", "13.5", "47%", "50%", "Unverified", "unknown", "timing association"):
    assert phrase in extracted, phrase
assert len(reader.pages[0].get("/Annots", [])) >= 3, "Source links must remain in the PDF"
print("Draft explainer saved: one A4 page, key qualifications and source links retained.")
