from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY
from utils import resource_path
import pandas as pd 
import pymupdf
from reportlab.lib.pagesizes import A4
PAGE_WIDTH, PAGE_HEIGHT = A4
from ai_narratives import generate_narratives
from xml.sax.saxutils import escape

ORANGE = HexColor("#F58220")

class DynamicTOCTable(Flowable):
    def __init__(self, toc_pages=None):
        Flowable.__init__(self)
        self.toc_pages = toc_pages or {}
        self.table = None

    def wrap(self, availWidth, availHeight):
        self.availWidth = availWidth
        self.availHeight = availHeight

        data = [
            [
                Paragraph("<b>Sl. No.</b>", toc_header),
                Paragraph("<b>Contents</b>", toc_header),
                Paragraph("<b>Page No.</b>", toc_header)
            ],
            ["1", "Introduction to the Report",
             self.toc_pages.get("Introduction to the Report", "")],
            ["2", "Leadership Competencies",
             self.toc_pages.get("Leadership Competencies", "")],
            ["3", "Key Areas of Strength",
             self.toc_pages.get("Key Areas of Strength", "")],
            ["4", "Key Areas of Improvement",
             self.toc_pages.get("Key Areas of Improvement", "")],
            ["5", "Blind Spots",
             self.toc_pages.get("Blind Spots", "")],
            ["6", "Leadership Competency-wise Analysis",
             self.toc_pages.get("Leadership Competency-wise Analysis", "")],
            ["7", "Self-scores vs Average Scores from all respondents",
             self.toc_pages.get(
                 "Self-scores vs Average Scores from all respondents", ""
             )],
            ["8", "Module and Question-wise Analysis",
             self.toc_pages.get("Module and Question-wise Analysis", "")],
            ["9", "Recommended Next Steps",
             self.toc_pages.get("Recommended Next Steps", "")],
        ]

        self.table = Table(
            data,
            colWidths=[0.9 * inch, 4.9 * inch, 1.1 * inch],
            rowHeights=[0.55 * inch] + [0.52 * inch] * 9
        )

        self.table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F28C28")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (1, 0), (1, -1), "LEFT"),
            ("ALIGN", (2, 0), (2, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        return self.table.wrap(availWidth, availHeight)

    def draw(self):
        table_width = self.table._width
        x = (self.availWidth - table_width) / 2
        self.table.drawOn(self.canv, x, 0)


def add_contents(elements,toc_pages):

    elements.append(Paragraph("Table of Contents", orange_heading))
    elements.append(Spacer(1,0.35*inch))

    elements.append(DynamicTOCTable(toc_pages))

    elements.append(PageBreak())


def cover_page(canvas, doc):
    cover_pdf = resource_path("assets/cover.pdf")

    pdf = pymupdf.open(cover_pdf)
    page = pdf[0]

    # -------------------------------------------------
    # FUNCTION TO GET THE EXACT BACKGROUND COLOR
    # -------------------------------------------------
    def get_background_color(box):
        # Render page temporarily at high resolution
        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(3, 3),
            alpha=False
        )

        # Convert PDF coordinates to pixel coordinates
        x = int(((box.x0 + box.x1) / 2) * 3)

        # Sample just above the text
        y = int((box.y0 - 5) * 3)

        # Keep coordinates inside image
        x = max(0, min(x, pix.width - 1))
        y = max(0, min(y, pix.height - 1))

        # Get RGB pixel
        pixel = pix.samples[
            (y * pix.width + x) * 3 :
            (y * pix.width + x) * 3 + 3
        ]

        r, g, b = pixel

        return (
            r / 255,
            g / 255,
            b / 255
        )

    # -------------------------------------------------
    # 1. REPLACE PROGRAM NAME + YEAR
    # -------------------------------------------------
    program_text = f"{doc.program_name} - {doc.program_year}"

    program_boxes = page.search_for(
        "SHIKHAR MDP - 2026"
    )

    if program_boxes:
        box = program_boxes[0]

        # Get EXACT orange background color
        background_color = get_background_color(box)

        # Remove original text
        page.add_redact_annot(
            box,
            fill=background_color
        )

        page.apply_redactions()

        # Font
        fontsize = 18
        font = pymupdf.Font("hebo")

        # Calculate width
        text_width = font.text_length(
            program_text,
            fontsize
        )

        # Center horizontally
        x = box.x0 + (
            box.width - text_width
        ) / 2

        # Same vertical position
        y = box.y1 - 2

        # Insert new dynamic text
        page.insert_text(
            (x, y),
            program_text,
            fontname="hebo",
            fontsize=fontsize,
            color=(0, 0, 0)
        )

    # -------------------------------------------------
    # 2. REPLACE SAMPLE WITH PARTICIPANT NAME
    # -------------------------------------------------
    sample_boxes = page.search_for("Sample")

    if sample_boxes:
        box = sample_boxes[0]

        # Get EXACT orange background color
        background_color = get_background_color(box)

        # Remove original Sample
        page.add_redact_annot(
            box,
            fill=background_color
        )

        page.apply_redactions()

        participant_name = doc.participant_name

        # Font
        fontsize = 24
        font = pymupdf.Font("hebo")

        # Calculate width
        text_width = font.text_length(
            participant_name,
            fontsize
        )

        # Center participant name
        x = box.x0 + (
            box.width - text_width
        ) / 2

        # Same vertical position
        y = box.y1 - 2

        # Insert participant name
        page.insert_text(
            (x, y),
            participant_name,
            fontname="hebo",
            fontsize=fontsize,
            color=(0, 0, 0)
        )

    # -------------------------------------------------
    # 3. RENDER FINAL COVER
    # -------------------------------------------------
    pix = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2),
        alpha=False
    )

    temp_cover = resource_path(
        "assets/_generated_cover.png"
    )

    pix.save(temp_cover)

    pdf.close()

    # -------------------------------------------------
    # 4. PLACE COVER ON REPORT
    # -------------------------------------------------
    canvas.drawImage(
        temp_cover,
        0,
        0,
        width=PAGE_WIDTH,
        height=PAGE_HEIGHT,
        preserveAspectRatio=False,
        mask="auto"
    )



def add_page_template(canv, doc):

    width, height = doc.pagesize

    canv.setStrokeColor(ORANGE)
    canv.setLineWidth(2)

    canv.rect(
        0.45*inch,
        0.45*inch,
        width-0.9*inch,
        height-0.9*inch
    )

    logo_path =  resource_path("assets/unext_logo.png")

    if os.path.exists(logo_path):
        canv.drawImage(
            logo_path,
            width-1.55*inch,
            height-0.95*inch,
            width=1.0*inch,
            height=0.45*inch,
            preserveAspectRatio=True,
            mask='auto'
        )

    canv.setFont("Helvetica",9)
    #-----FOOTER-----
    canv.drawString(
        0.55*inch,
        0.58*inch,
        "© 2026 UNEXT LEARNING PVT.LTD."
    )

    page_no = "" if doc.page == 1 else str(doc.page-1)

    canv.drawCentredString(
        width/2,
        0.58*inch,
        page_no
    )

styles = getSampleStyleSheet()

orange_heading = ParagraphStyle(
    "OrangeHeading",
    parent=styles["Heading1"],
    textColor=colors.HexColor("#F58220"),
    fontName="Helvetica-Bold",
    fontSize=20,
    spaceAfter=12,
    alignment=0,
)

black_heading = ParagraphStyle(
    "BlackHeading",
    parent=styles["Heading2"],
    textColor=colors.black,
    fontName="Helvetica-Bold",
    fontSize=16,
    spaceAfter=10,
    alignment=0,
)

toc_header = ParagraphStyle(
    "TOCHeader",
    parent=styles["Heading2"],
    alignment=1,
    textColor=colors.white,
    fontName="Helvetica-Bold",
    fontSize=12,
)

MODULE_NAMES = []

competency_definitions = {}


strength_points = {}


improvement_points = {}

def heading(elements,text):
    elements.append(Paragraph(f"<b>{text}</b>", styles["Title"]))
    elements.append(Spacer(1,0.15*inch))

    
def make_table(data):

    t = Table(data)

    num_cols = len(data[0])

    style = [

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),

        ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

        ("BOTTOMPADDING", (0,0), (-1,0), 8),

        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),

        ("ROWBACKGROUNDS", (0,1), (-1,-1),
            [colors.white, colors.HexColor("#F8F8F8")])
    ]

    # Page 6 table (6 columns)
    if num_cols == 6:

        style.extend([

            ("BACKGROUND",(0,0),(0,0),colors.HexColor("#D9EAD3")),
            ("BACKGROUND",(1,0),(1,0),colors.HexColor("#4F81BD")),
            ("BACKGROUND",(2,0),(2,0),colors.HexColor("#F79646")),
            ("BACKGROUND",(3,0),(3,0),colors.HexColor("#A5A5A5")),
            ("BACKGROUND",(4,0),(4,0),colors.HexColor("#FFC000")),
            ("BACKGROUND",(5,0),(5,0),colors.HexColor("#9DC3E6")),

        ])

    # Page 7 table (3 columns)
    else:

        style.extend([

            ("BACKGROUND",(0,0),(0,0),colors.HexColor("#D9EAD3")),
            ("BACKGROUND",(1,0),(1,0),colors.HexColor("#4F81BD")),
            ("BACKGROUND",(2,0),(2,0),colors.HexColor("#9DC3E6")),

        ])

    t.setStyle(TableStyle(style))

    return t


def draw_cover(canvas, doc):
    canvas.saveState()

    canvas.drawImage(
        resource_path("assets/cover_banner.jpeg"),
        0,
        0,
        width=doc.pagesize[0],
        height=doc.pagesize[1],
        preserveAspectRatio=False
    )

    canvas.restoreState()


def add_introduction(elements, program_name, reviewer_types):

    elements.append(
        Paragraph("Introduction to the report", orange_heading)
    )
    elements.append(Spacer(1, 0.15 * inch))

    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=12,
        leading=20,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
    )

    # -------------------------------------------------
    # DYNAMIC PROGRAM NAME
    # -------------------------------------------------
    p1 = f"""
    The {program_name} has been designed by UNext with the primary objective
    of providing a developmental pathway that helps you adapt to the world
    of information technology and business that is consistently getting
    disrupted.
    """

    # -------------------------------------------------
    # DYNAMIC REVIEWER DESCRIPTION
    # -------------------------------------------------
    reviewer_text = []

    reviewer_map = {
        "self": "you",
        "manager": "your manager",
        "peer": "your peers",
        "peers": "your peers",
        "direct reportee": "your direct-reportees",
        "direct reportees": "your direct-reportees",
        "direct_reportee": "your direct-reportees",
        "direct_reportees": "your direct-reportees"
    }

    for reviewer in reviewer_types:
        key = str(reviewer).strip().lower()

        if key in reviewer_map:
            reviewer_text.append(reviewer_map[key])
        else:
            reviewer_text.append(str(reviewer))

    # Remove duplicates while preserving order
    reviewer_text = list(dict.fromkeys(reviewer_text))

    if len(reviewer_text) == 1:
        reviewers = reviewer_text[0]

    elif len(reviewer_text) == 2:
        reviewers = f"{reviewer_text[0]} and {reviewer_text[1]}"

    else:
        reviewers = (
            ", ".join(reviewer_text[:-1])
            + ", and "
            + reviewer_text[-1]
        )

    p2 = f"""
    As a foundation step for this program, we recently invited you to
    participate in a 360-degree survey. The responses to this survey
    received from {reviewers} form the basis of this report. The report
    has been crafted to provide you with a holistic perspective of your
    perceived strengths and improvement areas.
    """

    p3 = """
    We understand your organization emphasizes aligning professional
    development plans with the organization's goals. As such, we recommend
    that you reflect on the insights shared in this report and have a growth
    conversation with your manager about shaping your development plan.
    We wish you all success!
    """

    p4 = """
    This report provides visual summary, insights, and observations at the
    following levels:
    """

    elements.append(Paragraph(p1, body))
    elements.append(Paragraph(p2, body))
    elements.append(Paragraph(p3, body))
    elements.append(Paragraph(p4, body))

    bullet_style = ParagraphStyle(
        "BulletTimes",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=12,
        leading=20,
    )

    bullets = [
        "Feedback",
        "Module-wise and Question-wise results for identification of blind spots"
    ]

    for b in bullets:
        elements.append(
            Paragraph(f"• {b}", bullet_style)
        )

    elements.append(Spacer(1, 0.50 * inch))

    image_path = resource_path(
        "assets/introduction_image.png"
    )

    if os.path.exists(image_path):
        elements.append(
            Image(
                image_path,
                width=6.5 * inch,
                height=3.0 * inch
            )
        )

    elements.append(PageBreak())



def add_leadership_competencies(elements, competencies):

    body_style = ParagraphStyle(
        "LeadershipBodyStyle",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )

    bullet_style = ParagraphStyle(
        "LeadershipBulletStyle",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        leftIndent=25,
        bulletIndent=10,
        spaceAfter=4,
    )

    elements.append(
        Paragraph(
            "Leadership Competencies",
            orange_heading
        )
    )

    elements.append(
        Spacer(1, 0.15 * inch)
    )

    intro = """
    This report captures the feedback received and presents insights for the set of
    competencies that your organization has identified for the role of future leaders.
    """

    elements.append(
        Paragraph(
            intro,
            body_style
        )
    )

    elements.append(
        Spacer(1, 0.25 * inch)
    )

    icon_path = resource_path("assets/leadership_icon.png")

    if os.path.exists(icon_path):

        img = Image(
            icon_path,
            width=1.75 * inch,
            height=1.90 * inch
        )

        img.hAlign = "CENTER"

        elements.append(img)

    elements.append(
        Spacer(1, 0.25 * inch)
    )

    desc = """
    It reflects the specific skills, behaviours, and attributes that effective
    leaders possess. The following competencies enable you to guide, inspire,
    and influence others to achieve individual, team, and organizational goals:
    """

    elements.append(
        Paragraph(
            desc,
            body_style
        )
    )

    elements.append(
        Spacer(1, 0.12 * inch)
    )

    for comp in competencies:

        elements.append(
            Paragraph(
                f"• {comp}",
                bullet_style
            )
        )

    elements.append(PageBreak())



def add_strengths_improvements(
    elements,
    strengths,
    improvements,
    competency_definitions,
    strength_points,
    improvement_points,
    ai_narratives=None,
):

    body = ParagraphStyle(
        "StrengthBody",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )

    elements.append(
        Paragraph(
            "Key Areas of Strength",
            orange_heading
        )
    )

    elements.append(
        Spacer(1, 0.15 * inch)
    )

    
    
    for i, comp in enumerate(strengths, start=1):

        elements.append(
            Paragraph(
                f"<b>{i}. {comp}</b>",
                black_heading
            )
        )

        description = (ai_narratives or {}).get("strengths", {}).get(
            comp,
            "The feedback indicates that this competency is an area of relative strength."
        )

        elements.append(
            Paragraph(
                escape(description),
                body
            )
        )

        elements.append(
            Spacer(1, 0.15 * inch)
        )


    elements.append(
        Paragraph(
            "Key Areas of Improvement",
            orange_heading
        )
    )

    elements.append(
        Spacer(1, 0.15 * inch)
    )

    
        
    for i, comp in enumerate(improvements, start=1):

        elements.append(
            Paragraph(
                f"<b>{i}. {comp}</b>",
                black_heading
            )
        )

        description = (ai_narratives or {}).get("improvements", {}).get(
            comp,
            "The feedback indicates an opportunity to further strengthen this competency."
        )

        elements.append(
            Paragraph(
                escape(description),
                body
            )
        )

        elements.append(
            Spacer(1, 0.15 * inch)
        )




def add_improvement_blindspots(
        elements,
        improvements,
        competency_definitions,
        improvement_points,
        negative_blindspots,
        positive_blindspots,
        blindspots):

    body = ParagraphStyle(
        "BlindspotBody",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
    )

    bullet = ParagraphStyle(
        "BlindspotBullet",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        leftIndent=20,
        leading=18,
        fontSize=12,
        spaceAfter=4,
    )

    # ----------------------------------
    # BLIND SPOTS
    # ----------------------------------

    elements.append(
        Paragraph(
            "Blind Spots",
            orange_heading
        )
    )

    elements.append(
        Spacer(1, 0.10 * inch)
    )

    # ----------------------------------
    # NEGATIVE BLIND SPOTS
    # Self > Others
    # ----------------------------------

    if negative_blindspots:

        elements.append(
            Paragraph(
                "These are the competencies where you rated yourself higher than the ratings received from other respondents (Negative Blind Spot).",
                body
            )
        )

        elements.append(
            Spacer(1, 0.05 * inch)
        )

        for comp in negative_blindspots:

            elements.append(
                Paragraph(
                    f"• <b>{comp}</b>",
                    bullet
                )
            )

        elements.append(
            Spacer(1, 0.15 * inch)
        )

    # ----------------------------------
    # POSITIVE BLIND SPOTS
    # Others > Self
    # ----------------------------------

    if positive_blindspots:

        elements.append(
            Paragraph(
                "These are the competencies where other respondents rated you higher than your self-rating (Positive Blind Spot).",
                body
            )
        )

        elements.append(
            Spacer(1, 0.05 * inch)
        )

        for comp in positive_blindspots:

            elements.append(
                Paragraph(
                    f"• <b>{comp}</b>",
                    bullet
                )
            )



class TOCDocTemplate(SimpleDocTemplate):

    def __init__(self, *args, **kwargs):
        self.toc_pages = {}
        super().__init__(*args, **kwargs)

    def afterFlowable(self, flowable):

        if isinstance(flowable, Paragraph):

                text = flowable.getPlainText().strip()

                toc_sections = {
                    "Introduction to the report": "Introduction to the Report",
                    "Leadership Competencies": "Leadership Competencies",
                    "Key Areas of Strength": "Key Areas of Strength",
                    "Key Areas of Improvement": "Key Areas of Improvement",
                    "Blind Spots": "Blind Spots",
                    "1. Leadership Competency-wise Analysis": "Leadership Competency-wise Analysis",
                    "2. Self-scores vs Average Scores from all respondents":
                        "Self-scores vs Average Scores from all respondents",
                    "Module and Question-wise Analysis": "Module and Question-wise Analysis",
                    "Recommended Next Steps:": "Recommended Next Steps",
                }

                if text in toc_sections:
                    self.toc_pages[toc_sections[text]] = self.page



def fill_toc_page_numbers(pdf_path, toc_pages):

    pdf = pymupdf.open(pdf_path)

    # TOC is page 2 of the PDF
    page = pdf[1]

    # Find the Page No. header to determine the exact
    # center of the Page No. column.
    header = page.search_for("Page No.")

    if not header:
        pdf.close()
        return

    header_box = header[0]
    page_no_x = (header_box.x0 + header_box.x1) / 2

    toc_rows = [
        ("Introduction to the Report",
         toc_pages.get("Introduction to the Report")),

        ("Leadership Competencies",
         toc_pages.get("Leadership Competencies")),

        ("Key Areas of Strength",
         toc_pages.get("Key Areas of Strength")),

        ("Key Areas of Improvement",
         toc_pages.get("Key Areas of Improvement")),

        ("Blind Spots",
         toc_pages.get("Blind Spots")),

        ("Leadership Competency-wise Analysis",
         toc_pages.get("Leadership Competency-wise Analysis")),

        ("Self-scores vs Average Scores from all respondents",
         toc_pages.get("Self-scores vs Average Scores from all respondents")),

        ("Module and Question-wise Analysis",
         toc_pages.get("Module and Question-wise Analysis")),

        ("Recommended Next Steps",
         toc_pages.get("Recommended Next Steps")),
    ]

    for title, page_number in toc_rows:

        if page_number is None:
            continue

        matches = page.search_for(title)

        if not matches:
            continue

        title_box = matches[0]

        # Center vertically with the existing row text
        y = title_box.y1 - 1

        # Footer numbering excludes the cover page
        display_page = page_number - 1

        page.insert_text(
        (page_no_x - 3, y),
        str(display_page),
        fontname="helv",
        fontsize=10,
        color=(0, 0, 0)
    )

    temp_pdf = pdf_path.replace(".pdf", "_final.pdf")

    pdf.save(temp_pdf)
    pdf.close()

    os.replace(temp_pdf, pdf_path)



def create_report(participant_name, participant_scores, manager_scores, peer_scores,
                  reportee_scores, cohort_scores, average_scores,blindspots,form_link,program_name,program_year,competency_question_texts=None,submission_date=""):

    print("REPORT LOADED")

    doc=TOCDocTemplate(
        f"output/{participant_name}_360°_Feedback Report.pdf"
    )
    elements=[]  

    elements.append(Spacer(1, 0.1 * inch))
    elements.append(PageBreak())

    add_contents(elements,doc.toc_pages)

    reviewer_types = []

    if manager_scores:
        reviewer_types.append("manager")

    if peer_scores:
        reviewer_types.append("peers")

    if reportee_scores:
        reviewer_types.append("direct reportees")

    reviewer_types.insert(0, "self")

    add_introduction(
        elements,
        program_name,
        reviewer_types
    )

    add_leadership_competencies(elements,list(participant_scores.keys()))

    
    # Keep only competencies with valid scores
    valid_scores = {
        comp: score
        for comp, score in participant_scores.items()
        if score is not None and not pd.isna(score)
    }

    # Find top 2 strengths
    strengths = sorted(
        valid_scores,
        key=valid_scores.get,
        reverse=True
    )[:2]

    # Find bottom 2 improvements
    remaining_scores = {
        comp: score
        for comp, score in valid_scores.items()
        if comp not in strengths
    }

    improvements = sorted(
        remaining_scores,
        key=remaining_scores.get
    )[:2]


    # GENERATE AI NARRATIVES
    competency_question_texts = competency_question_texts or {}

    ai_strengths = [
        {
            "competency": comp,
            "score": valid_scores[comp]
        }
        for comp in strengths
    ]

    ai_improvements = [
        {
            "competency": comp,
            "score": valid_scores[comp]
        }
        for comp in improvements
    ]

    ai_narratives = generate_narratives(
        ai_strengths,
        ai_improvements,
        competency_question_texts
    )


    # Competencies already used
    used = set(strengths + improvements)


    positive_blindspots = []
    negative_blindspots = []

    # -------------------------------------------------
    # BLIND SPOT SELECTION
    # -------------------------------------------------
    # Positive delta = Self > Others
    # Negative delta = Others > Self
    #
    # First preference:
    # Use blind spots that are not already used
    # as Strengths or Improvements.
    #
    # Fallback:
    # If no unused blind spots are available,
    # allow genuine blind spots to repeat.
    # -------------------------------------------------

    BLINDSPOT_THRESHOLD = 0.25

    # First, find meaningful blind spots that are
    # not already used in Strengths / Improvements.
    unused_blindspots = []

    for comp, delta in blindspots.items():

        delta = float(delta)

        if abs(delta) >= BLINDSPOT_THRESHOLD and comp not in used:
            unused_blindspots.append((comp, delta))


    # -------------------------------------------------
    # FIRST: use unused blind spots
    # -------------------------------------------------

    for comp, delta in unused_blindspots:

        if delta > 0:
            negative_blindspots.append(comp)

        elif delta < 0:
            positive_blindspots.append(comp)


    # -------------------------------------------------
    # FALLBACK:
    # If no unused blind spots are available,
    # allow genuine blind spots to repeat.
    # -------------------------------------------------

    if not negative_blindspots and not positive_blindspots:

        for comp, delta in blindspots.items():

            delta = float(delta)

            if abs(delta) >= BLINDSPOT_THRESHOLD:

                if delta > 0:
                    negative_blindspots.append(comp)

                elif delta < 0:
                    positive_blindspots.append(comp)



    add_strengths_improvements(
        elements,
        strengths,
        improvements,
        competency_definitions,
        strength_points,
        improvement_points,
        ai_narratives
    )

    add_improvement_blindspots(
        elements,
        improvements,
        competency_definitions,
        improvement_points,
        negative_blindspots,
        positive_blindspots,
        blindspots,
    )

    elements.append(PageBreak())
    elements.append(Spacer(1,0.10*inch))
    elements.append(Paragraph("Feedback survey results:", orange_heading))
    elements.append(Spacer(1, 0.08*inch))

    elements.append(Paragraph("1. Leadership Competency-wise Analysis", black_heading))
    elements.append(Spacer(1, 0.10*inch))

    if os.path.exists("output/radar_chart.png"):
        elements.append(Image("output/radar_chart.png",width=5.5*inch,height=5.5*inch))
    data=[["Competency","Self","Manager","Peer","Reportee","Cohort Avg"]]
    for c in participant_scores:
        data.append([c,participant_scores[c],manager_scores.get(c,0),peer_scores.get(c,0),reportee_scores.get(c,0),cohort_scores.get(c,0)])
    elements.append(make_table(data))
    elements.append(PageBreak())

    # PAGE 7
    elements.append(Paragraph("2. Self-scores vs Average Scores from all respondents", black_heading))
    elements.append(Spacer(1, 0.10*inch))
    if os.path.exists("output/self_vs_average_radar.png"):
        elements.append(Image("output/self_vs_average_radar.png",width=5.5*inch,height=5.5*inch))
    data=[["Competency","Self","Average"]]
    for c in participant_scores:
        data.append([c,participant_scores[c],average_scores.get(c,0)])
    elements.append(make_table(data))
    elements.append(PageBreak())

    folder = "output/module_charts"

    # Use the dynamically detected competencies
    charts = [
        f"{name.replace(' ', '_')}.png"
        for name in participant_scores.keys()
    ]

    MODULE_NAMES = list(participant_scores.keys())

    first = True
    mod = 1

    for i in range(0, len(charts), 2):

        if first:
            elements.append(Paragraph("Module and Question-wise Analysis", orange_heading))
            elements.append(Spacer(1, 0.10*inch))
            first = False

        for ch in charts[i:i+2]:

            image_path = os.path.join(folder, ch)

            # Move the heading down
            elements.append(Spacer(1, 0.05*inch))

            elements.append(
                Paragraph(
                    f"{mod}. {MODULE_NAMES[mod-1]}",
                    black_heading
                )
            )

            elements.append(Spacer(1, 0.03*inch))

            if os.path.exists(image_path):

                img = Image(
                    image_path,
                    width=6.4*inch,
                    height=3.2*inch
                )
                
                elements.append(img)

            elements.append(Spacer(1, 0.15*inch))

            mod += 1

        if mod <= len(MODULE_NAMES):
            elements.append(PageBreak())

    # Recommended Next Steps
    elements.append(Spacer(1, 0.10*inch))

    elements.append(Paragraph("Recommended Next Steps:", orange_heading))
    elements.append(Spacer(1, 0.15*inch))

    elements.append(Paragraph(
        "• We recommend you discuss the report with your manager to validate the areas you have shortlisted.",
        styles["BodyText"]
    ))

    elements.append(Paragraph(
        '• Once identified, please update your areas of strength and improvement using the following link: '
        f'<link href="{form_link}">'
        '<font color="blue"><u>Identifying Areas of Strength and Improvements Form</u></font>'
        '</link>',
        styles["BodyText"]
    ))

    elements.append(Paragraph(
        "• Please report the identified areas to the program coordinator following a sign-off from your manager. "
        "This will help them in providing you the required support for your development.",
        styles["BodyText"]
    ))

    elements.append(Spacer(1,0.10*inch))

    next_steps = resource_path("assets/next_steps.png")

    if os.path.exists(next_steps):
        img = Image(next_steps, width=4.3*inch, height=2.2*inch)
        img.hAlign = "CENTER"
        elements.append(img)

    doc.participant_name = participant_name
    doc.program_name = program_name
    doc.program_year = program_year

    doc.multiBuild(
        elements,
        onFirstPage=cover_page,
        onLaterPages=add_page_template
    )


    fill_toc_page_numbers(
        f"output/{participant_name}_360°_Feedback Report.pdf",
        doc.toc_pages
    )
