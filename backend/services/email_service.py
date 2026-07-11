import re
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import litellm
from config import (
    GMAIL_ADDRESS, GMAIL_APP_PASSWORD,
    FALLBACK_EMAIL, LLM_MODEL, LLM_API_KEY
)

logging.basicConfig(level=logging.INFO)


def extract_email_from_description(description: str):
    if not description:
        return None
    pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, description)
    valid   = [m for m in matches if not m.lower().endswith(
        ('.png', '.jpg', '.gif', '.svg', '.webp'))]
    return valid[0] if valid else None


def guess_company_email(company: str):
    if not company:
        return None
    clean = company.lower()
    for suffix in [' ltd', ' limited', ' pvt', ' private', ' inc',
                   ' corp', ' corporation', ' solutions', ' technologies',
                   ' services', ' india', ' global']:
        clean = clean.replace(suffix, '')
    clean = re.sub(r'[^a-z0-9]', '', clean).strip()
    return f"careers@{clean}.com" if clean else None


def extract_email_with_ai(description: str, company: str):
    if not description:
        return None
    try:
        prompt = f"""Read this job posting.
If it contains a contact or application email address, return ONLY that email.
If no email exists, return ONLY the word: NONE

Company: {company}
Job posting: {description[:2000]}"""
        response = litellm.completion(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            api_key=LLM_API_KEY,
            max_tokens=30
        )
        result = response.choices[0].message.content.strip()
        if result.upper() == "NONE" or "@" not in result:
            return None
        if re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', result):
            return result
    except Exception as e:
        logging.warning(f"AI email extraction failed: {e}")
    return None


def find_recipient_email(job: dict) -> tuple[str, str]:
    description = job.get("description", "")
    company     = job.get("company", "")

    email = extract_email_from_description(description)
    if email:
        return email, "extracted from job description"

    email = extract_email_with_ai(description, company)
    if email:
        return email, "extracted by AI"

    email = guess_company_email(company)
    if email:
        return email, "guessed from company name"

    return FALLBACK_EMAIL, "fallback — no company email found"


def send_application_email(
    applicant_name:  str,
    applicant_email: str,
    job:             dict,
    cover_letter_pdf: bytes,
    resume_pdf:       bytes
) -> tuple[str, str]:
    """Send application email with resume and cover letter as PDF attachments."""

    recipient, source = find_recipient_email(job)
    job_title = job.get('job_title', 'Position')
    company   = job.get('company', 'Company')

    msg = MIMEMultipart("mixed")
    msg["Subject"]  = f"Application for {job_title} — {applicant_name}"
    msg["From"]     = f"{applicant_name} <{GMAIL_ADDRESS}>"
    msg["To"]       = FALLBACK_EMAIL
    msg["Reply-To"] = applicant_email

    # ── Email body ────────────────────────────────────────────────
    plain = f"""Dear Hiring Team at {company},

Please find attached my application for the {job_title} position,
including my tailored resume and cover letter.

I would welcome the opportunity to discuss how my background
aligns with your team's needs.

Best regards,
{applicant_name}
{applicant_email}

---
Intended recipient: {recipient} ({source})
"""

    html = f"""
<html>
<body style="font-family: Georgia, serif; color: #1a1a1a;
             max-width: 600px; margin: auto; padding: 24px;">

  <p>Dear Hiring Team at <strong>{company}</strong>,</p>

  <p>Please find attached my application for the
  <strong>{job_title}</strong> position — including my tailored
  resume and a cover letter outlining my relevant experience.</p>

  <p>I would welcome the opportunity to discuss how my background
  aligns with your team's needs. Please feel free to reach me at
  <a href="mailto:{applicant_email}">{applicant_email}</a>.</p>

  <p>Best regards,<br>
  <strong>{applicant_name}</strong><br>
  <a href="mailto:{applicant_email}">{applicant_email}</a>
  </p>

  <hr style="border:none; border-top:1px solid #e0e0e0; margin-top:32px;">
  <p style="font-size:11px; color:#aaa;">
    Intended recipient: {recipient} ({source})
  </p>

</body>
</html>
"""
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(plain, "plain"))
    alt.attach(MIMEText(html,  "html"))
    msg.attach(alt)

    # ── Attach Resume PDF ─────────────────────────────────────────
    res_att = MIMEApplication(resume_pdf, _subtype="pdf")
    res_att.add_header("Content-Disposition", "attachment",
        filename=f"Resume_{applicant_name.replace(' ', '_')}.pdf")
    msg.attach(res_att)

    # ── Attach Cover Letter PDF ───────────────────────────────────
    cl_att = MIMEApplication(cover_letter_pdf, _subtype="pdf")
    safe_company = company.replace(' ', '_').replace('/', '_')
    cl_att.add_header("Content-Disposition", "attachment",
        filename=f"Cover_Letter_{applicant_name.replace(' ', '_')}_{safe_company}.pdf")
    msg.attach(cl_att)

    # ── Send ──────────────────────────────────────────────────────
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.ehlo()
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, FALLBACK_EMAIL, msg.as_string())

    logging.info(f"Email sent: {job_title} at {company} → {FALLBACK_EMAIL}")
    return recipient, source
