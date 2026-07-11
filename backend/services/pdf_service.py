import io
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# ── Page constants ─────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
ML = 15 * mm
MR = PAGE_W - 15 * mm
CONTENT_W = MR - ML

# ── Colours ────────────────────────────────────────────────────────
BLACK      = colors.HexColor('#1a1a1a')
DARK_BLUE  = colors.HexColor('#1a1a2e')
MID_GRAY   = colors.HexColor('#555555')
LIGHT_GRAY = colors.HexColor('#888888')

# ── Fonts ──────────────────────────────────────────────────────────
FONT_REG  = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'
FONT_ITAL = 'Helvetica-Oblique'


def _clean(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*',     r'\1', text)
    text = re.sub(r'__(.+?)__',     r'\1', text)
    text = re.sub(r'_(.+?)_',       r'\1', text)
    return text.strip()


def _wrap(c, text, font, size, max_w):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines or [""]


class ResumeBuilder:
    def __init__(self, buffer):
        self.c = canvas.Canvas(buffer, pagesize=A4)
        self.y = PAGE_H - 12 * mm

    def _move(self, dy):
        self.y -= dy

    def _line(self, x1, y, x2, color=DARK_BLUE, thickness=0.8):
        self.c.setStrokeColor(color)
        self.c.setLineWidth(thickness)
        self.c.line(x1, y, x2, y)

    def _text(self, x, y, text, font, size, color=BLACK):
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        self.c.drawString(x, y, _clean(str(text)))

    def _text_right(self, x, y, text, font, size, color=BLACK):
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        self.c.drawRightString(x, y, _clean(str(text)))

    def section(self, title, gap_before=4.5):
        self._move(gap_before * mm)
        self._text(ML, self.y, title.upper(), FONT_BOLD, 8.2, DARK_BLUE)
        self._move(2.5 * mm)
        self._line(ML, self.y, MR, thickness=0.9)
        self._move(2.8 * mm)

    def entry_header(self, left_bold, left_light, right):
        self.c.setFont(FONT_BOLD, 8.8)
        self.c.setFillColor(BLACK)
        bw = self.c.stringWidth(_clean(left_bold), FONT_BOLD, 8.8)
        self.c.drawString(ML, self.y, _clean(left_bold))
        if left_light:
            self.c.setFont(FONT_REG, 8.8)
            self.c.setFillColor(MID_GRAY)
            self.c.drawString(ML + bw + 2, self.y, _clean(left_light))
        if right:
            self._text_right(MR, self.y, right, FONT_ITAL, 8.2, LIGHT_GRAY)
        self._move(3.8 * mm)

    def bullet(self, text, indent=4.5):
        x     = ML + indent * mm
        avail = CONTENT_W - indent * mm
        lines = _wrap(self.c, _clean(str(text)), FONT_REG, 8.2, avail)
        for i, line in enumerate(lines):
            if i == 0:
                self.c.setFillColor(DARK_BLUE)
                self.c.circle(ML + 1.8 * mm, self.y + 1.4, 1.0, fill=1, stroke=0)
            self.c.setFont(FONT_REG, 8.2)
            self.c.setFillColor(BLACK)
            self.c.drawString(x, self.y, line)
            self._move(3.5 * mm)

    def para(self, text, font=FONT_REG, size=8.3, color=BLACK, indent=0):
        x     = ML + indent * mm
        avail = CONTENT_W - indent * mm
        lines = _wrap(self.c, _clean(str(text)), font, size, avail)
        for line in lines:
            self._text(x, self.y, line, font, size, color)
            self._move(3.6 * mm)

    def skills_row(self, category, items_str):
        cat = _clean(category) + ": "
        cw  = self.c.stringWidth(cat, FONT_BOLD, 8.2)
        self.c.setFont(FONT_BOLD, 8.2)
        self.c.setFillColor(BLACK)
        self.c.drawString(ML, self.y, cat)
        avail = CONTENT_W - cw
        lines = _wrap(self.c, items_str, FONT_REG, 8.2, avail)
        self.c.setFont(FONT_REG, 8.2)
        self.c.setFillColor(MID_GRAY)
        self.c.drawString(ML + cw, self.y, lines[0])
        self._move(3.5 * mm)
        for line in lines[1:]:
            self.c.setFont(FONT_REG, 8.2)
            self.c.setFillColor(MID_GRAY)
            self.c.drawString(ML + cw, self.y, line)
            self._move(3.5 * mm)

    def build(self):
        self.c.save()


def generate_resume_pdf(parsed_resume: dict, tailored_text: str = "") -> bytes:
    """Generate a one-page ATS-friendly resume PDF."""
    buffer = io.BytesIO()
    rb = ResumeBuilder(buffer)
    c  = rb.c

    name     = parsed_resume.get("name", "Applicant")
    phone    = parsed_resume.get("phone", "")
    email    = parsed_resume.get("email", "")
    linkedin = parsed_resume.get("linkedin", "")
    github   = parsed_resume.get("github", "")
    summary  = parsed_resume.get("summary", "")
    edu      = parsed_resume.get("education", [])
    exp      = parsed_resume.get("experience", [])
    projects = parsed_resume.get("projects", [])
    skills   = parsed_resume.get("skills", {})
    certs    = parsed_resume.get("certifications", [])
    extras   = parsed_resume.get("extracurricular", {})

    # ── HEADER ──────────────────────────────────────────────────
    c.setFont(FONT_BOLD, 18)
    c.setFillColor(DARK_BLUE)
    c.drawCentredString(PAGE_W / 2, rb.y, name.upper())
    rb._move(6 * mm)

    contact = "  •  ".join(p for p in [phone, email, linkedin, github] if p)
    c.setFont(FONT_REG, 7.8)
    c.setFillColor(MID_GRAY)
    c.drawCentredString(PAGE_W / 2, rb.y, contact)
    rb._move(3.5 * mm)
    rb._line(ML, rb.y, MR, thickness=1.2)
    rb._move(4 * mm)

    # ── PROFILE ─────────────────────────────────────────────────
    if summary:
        rb.section("Profile", gap_before=0)
        rb.para(summary, size=8.3)

    # ── EDUCATION ───────────────────────────────────────────────
    if edu:
        rb.section("Education")
        for e in edu:
            if isinstance(e, dict):
                rb.entry_header(
                    e.get("degree", ""),
                    f",  {e.get('institution','')}" if e.get("institution") else "",
                    e.get("year", "")
                )

    # ── EXPERIENCE ──────────────────────────────────────────────
    if exp:
        rb.section("Internship" if any(
            "intern" in str(e.get("title","")).lower() for e in exp if isinstance(e, dict)
        ) else "Experience")
        for e in exp:
            if isinstance(e, dict):
                company = e.get("company", "")
                rb.entry_header(
                    e.get("title", ""),
                    f"  —  {company}" if company else "",
                    e.get("duration", "")
                )
                for b in (e.get("bullets", []) or []):
                    if b:
                        rb.bullet(str(b))

    # ── PROJECTS ────────────────────────────────────────────────
    if projects:
        rb.section("Projects")
        for p in projects:
            if isinstance(p, dict):
                tech = p.get("tech", "")
                rb.entry_header(
                    p.get("name", ""),
                    f"  |  {tech}" if tech else "",
                    p.get("duration", "")
                )
                for b in (p.get("bullets", []) or []):
                    if b:
                        rb.bullet(str(b))

    # ── SKILLS ──────────────────────────────────────────────────
    if skills:
        rb.section("Technical Skills")
        if isinstance(skills, dict):
            for cat, items in skills.items():
                items_str = ", ".join(items) if isinstance(items, list) else str(items)
                rb.skills_row(cat, items_str)
        elif isinstance(skills, list):
            rb.para(", ".join(str(s) for s in skills), size=8.2, color=MID_GRAY)

    # ── CERTIFICATIONS ──────────────────────────────────────────
    if certs:
        rb.section("Certifications")
        for cert in certs:
            if isinstance(cert, dict):
                name_c  = cert.get("name", "")
                issuer  = cert.get("issuer", "")
                rb.bullet(f"{name_c} — {issuer}" if issuer else name_c)
            else:
                rb.bullet(str(cert))

    # ── EXTRACURRICULAR ─────────────────────────────────────────
    if extras:
        rb.section("Extracurricular & Soft Skills")
        if isinstance(extras, dict):
            soft = extras.get("soft_skills", [])
            acts = extras.get("activities", [])
            if soft:
                rb.para("Soft Skills: " + ", ".join(soft), size=8.2)
            for act in acts:
                rb.bullet(str(act))
        elif isinstance(extras, list):
            for item in extras:
                rb.bullet(str(item))

    rb.build()
    return buffer.getvalue()


def generate_cover_letter_pdf(
    cover_text: str,
    applicant_name: str,
    applicant_email: str,
    job: dict
) -> bytes:
    """Generate a professional cover letter PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=22*mm, leftMargin=22*mm,
        topMargin=22*mm, bottomMargin=22*mm
    )
    styles = getSampleStyleSheet()
    story  = []

    header_style = ParagraphStyle('H', parent=styles['Normal'],
        fontSize=14, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a1a2e'), spaceAfter=2)

    sub_style = ParagraphStyle('S', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#555555'), spaceAfter=2)

    ref_style = ParagraphStyle('R', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a1a2e'), spaceAfter=12)

    body_style = ParagraphStyle('B', parent=styles['Normal'],
        fontSize=10.5, leading=17, fontName='Helvetica',
        textColor=colors.HexColor('#1a1a1a'), spaceAfter=10)

    story.append(Paragraph(applicant_name, header_style))
    story.append(Paragraph(applicant_email, sub_style))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=1.2,
                             color=colors.HexColor('#1a1a2e')))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph(
        f"Re: Application for {job.get('job_title','Position')} — {job.get('company','')}",
        ref_style
    ))

    for para in cover_text.split('\n\n'):
        para = para.strip()
        if para:
            para = (para.replace('&', '&amp;')
                        .replace('<', '&lt;')
                        .replace('>', '&gt;'))
            story.append(Paragraph(para, body_style))

    doc.build(story)
    return buffer.getvalue()
