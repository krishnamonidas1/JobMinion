import os, re, smtplib, logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
load_dotenv()
import litellm
import supabase_utils
from config import LLM_MODEL, LLM_API_KEY, SUPABASE_TABLE_NAME

# PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GMAIL_ADDRESS      = os.environ.get("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
FALLBACK_EMAIL     = "krishnamonidas44@gmail.com"
litellm.api_key    = LLM_API_KEY

# ----------------------------------------------------------------
# PDF Generator
# ----------------------------------------------------------------
def generate_pdf(title: str, content: str, subtitle: str = "") -> bytes:
    """Generates a styled PDF from text content and returns bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#4a4a6a'),
        spaceAfter=2,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10.5,
        leading=16,
        textColor=colors.HexColor('#2c2c2c'),
        spaceAfter=8,
        fontName='Helvetica'
    )

    story = []

    # Title
    story.append(Paragraph(title, title_style))
    if subtitle:
        story.append(Paragraph(subtitle, subtitle_style))
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=1.5,
                             color=colors.HexColor('#1a1a2e')))
    story.append(Spacer(1, 6*mm))

    # Body — split by newlines, handle each paragraph
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('---'):
            story.append(HRFlowable(width="100%", thickness=0.5,
                                     color=colors.HexColor('#cccccc')))
            story.append(Spacer(1, 3*mm))
        elif line.startswith('##'):
            heading = line.replace('##', '').strip()
            story.append(Spacer(1, 3*mm))
            story.append(Paragraph(f"<b>{heading}</b>", body_style))
        elif line.startswith('#'):
            heading = line.replace('#', '').strip()
            story.append(Spacer(1, 2*mm))
            story.append(Paragraph(f"<b><u>{heading}</u></b>", body_style))
        elif line.startswith('-') or line.startswith('•'):
            bullet_text = line.lstrip('-•').strip()
            story.append(Paragraph(f"• {bullet_text}", body_style))
        elif line == '':
            story.append(Spacer(1, 3*mm))
        else:
            # Escape special XML characters for ReportLab
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(line, body_style))

    doc.build(story)
    return buffer.getvalue()

# ----------------------------------------------------------------
# Email Detection
# ----------------------------------------------------------------
def extract_email_from_description(description: str):
    if not description:
        return None
    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, description)
    valid = [m for m in matches if not m.lower().endswith(('.png','.jpg','.gif','.svg'))]
    return valid[0] if valid else None

def guess_company_email(company: str):
    if not company:
        return None
    clean = company.lower()
    for suffix in [' ltd',' limited',' pvt',' private',' inc',
                   ' corp',' corporation',' solutions',' technologies',
                   ' services',' india',' global']:
        clean = clean.replace(suffix, '')
    clean = re.sub(r'[^a-z0-9]', '', clean).strip()
    return f"careers@{clean}.com" if clean else None

def extract_email_with_ai(description: str, company: str):
    if not description:
        return None
    try:
        prompt = f"""Read this job posting carefully.
If it contains a contact email address or application email, return ONLY that email address.
If there is no email address anywhere in the text, return ONLY the word: NONE

Company: {company}
Job posting:
{description[:3000]}"""
        response = litellm.completion(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            api_key=LLM_API_KEY,
            max_tokens=50
        )
        result = response.choices[0].message.content.strip()
        if result.upper() == "NONE" or "@" not in result:
            return None
        if re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', result):
            return result
    except Exception as e:
        logging.warning(f"AI email extraction failed: {e}")
    return None

def find_recipient_email(job: dict):
    description = job.get("description", "")
    company     = job.get("company", "")

    email = extract_email_from_description(description)
    if email:
        return email, "extracted from description"

    email = extract_email_with_ai(description, company)
    if email:
        return email, "extracted by AI"

    email = guess_company_email(company)
    if email:
        return email, f"guessed from company name ({company})"

    return FALLBACK_EMAIL, "fallback (no company email found)"

# ----------------------------------------------------------------
# Email Sender
# ----------------------------------------------------------------
def send_application_email(job: dict, cover_letter: str,
                           tailored_resume: str, applicant_name: str,
                           applicant_email: str):
    recipient, source = find_recipient_email(job)
    job_title = job.get('job_title', 'Position')
    company   = job.get('company', 'Company')
    score     = job.get('resume_score', 'N/A')

    logging.info(f"    📧 Recipient: {recipient} [{source}]")

    # -- Generate PDFs --
    logging.info("    Generating cover letter PDF...")
    cover_pdf = generate_pdf(
        title    = "Cover Letter",
        subtitle = f"{applicant_name}  |  {applicant_email}",
        content  = cover_letter
    )

    logging.info("    Generating tailored resume PDF...")
    resume_pdf = generate_pdf(
        title    = "Resume",
        subtitle = f"{applicant_name}  |  {applicant_email}",
        content  = tailored_resume
    )

    # -- Build email --
    msg = MIMEMultipart("mixed")
    msg["Subject"] = f"Application for {job_title} – {applicant_name}"
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = FALLBACK_EMAIL  # delivering to your inbox

    # Personalised email body
    body_html = f"""
<html><body style="font-family: Arial, sans-serif; color: #2c2c2c; max-width: 600px;">

<p>Dear Hiring Team at <b>{company}</b>,</p>

<p>I am writing to express my strong interest in the <b>{job_title}</b> position at {company}. 
Having carefully reviewed the job requirements, I am confident that my skills and experience 
make me an excellent fit for this role.</p>

<p>Please find attached:</p>
<ul>
  <li>📄 <b>Cover Letter</b> — tailored specifically for this position</li>
  <li>📋 <b>Resume</b> — highlighting relevant experience and skills</li>
</ul>

<p>I would welcome the opportunity to discuss how my background aligns with your team's needs. 
Please feel free to reach out at <a href="mailto:{applicant_email}">{applicant_email}</a>.</p>

<p>Thank you for your time and consideration.</p>

<p>Best regards,<br>
<b>{applicant_name}</b><br>
{applicant_email}</p>

<hr style="border: 1px solid #eee; margin-top: 20px;">
<p style="font-size: 11px; color: #888;">
  Match Score: {score}/100 &nbsp;|&nbsp; 
  Applied via: AI Job Application Agent &nbsp;|&nbsp;
  Recipient source: {source}
</p>

</body></html>
"""

    body_plain = f"""Dear Hiring Team at {company},

I am writing to express my strong interest in the {job_title} position at {company}.
Having carefully reviewed the job requirements, I am confident that my skills and experience
make me an excellent fit for this role.

Please find attached my Cover Letter and Resume, tailored specifically for this position.

I would welcome the opportunity to discuss how my background aligns with your team's needs.
Please feel free to reach out at {applicant_email}.

Thank you for your time and consideration.

Best regards,
{applicant_name}
{applicant_email}

---
Match Score: {score}/100
Intended recipient: {recipient} ({source})
"""

    # Attach plain + HTML body
    body_part = MIMEMultipart("alternative")
    body_part.attach(MIMEText(body_plain, "plain"))
    body_part.attach(MIMEText(body_html, "html"))
    msg.attach(body_part)

    # Attach Cover Letter PDF
    cover_attachment = MIMEApplication(cover_pdf, _subtype="pdf")
    cover_attachment.add_header(
        "Content-Disposition", "attachment",
        filename=f"Cover_Letter_{applicant_name.replace(' ','_')}_{company.replace(' ','_')}.pdf"
    )
    msg.attach(cover_attachment)

    # Attach Resume PDF
    resume_attachment = MIMEApplication(resume_pdf, _subtype="pdf")
    resume_attachment.add_header(
        "Content-Disposition", "attachment",
        filename=f"Resume_{applicant_name.replace(' ','_')}_{company.replace(' ','_')}.pdf"
    )
    msg.attach(resume_attachment)

    # Send
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, FALLBACK_EMAIL, msg.as_string())

    return recipient, source

# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
def main():
    print(f"Gmail Address  : {GMAIL_ADDRESS}")
    print(f"Delivering to  : {FALLBACK_EMAIL}")

    base_resume    = supabase_utils.get_base_resume()
    applicant_name = base_resume.get("name", "Applicant") if base_resume else "Applicant"
    applicant_email = base_resume.get("email", GMAIL_ADDRESS) if base_resume else GMAIL_ADDRESS

    jobs_result = supabase_utils.supabase.table(SUPABASE_TABLE_NAME)\
        .select("job_id, job_title, company, description, resume_score, tailored_resume, cover_letter")\
        .not_.is_("cover_letter", "null")\
        .not_.is_("tailored_resume", "null")\
        .is_("emailed", "null")\
        .eq("is_active", True)\
        .order("resume_score", desc=True)\
        .limit(5)\
        .execute()

    jobs = jobs_result.data
    if not jobs:
        print("No jobs ready to email. Run cover_letter.py first.")
        return

    print(f"\nSending {len(jobs)} application emails with PDF attachments...")
    for job in jobs:
        print(f"\n  → {job.get('job_title')} at {job.get('company')}")
        try:
            recipient, source = send_application_email(
                job,
                job.get("cover_letter", ""),
                job.get("tailored_resume", ""),
                applicant_name,
                applicant_email
            )
            supabase_utils.supabase.table(SUPABASE_TABLE_NAME)\
                .update({"emailed": True, "recipient_email": recipient})\
                .eq("job_id", job["job_id"])\
                .execute()
            print(f"    ✓ Sent with PDFs to {FALLBACK_EMAIL} (intended for {recipient})")
        except Exception as e:
            logging.error(f"    ✗ Failed: {e}")

    print("\nEmail sending complete.")

if __name__ == "__main__":
    main()