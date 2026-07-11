import io
import json
import logging
import pdfplumber
import litellm
from config import LLM_MODEL, LLM_API_KEY

logging.basicConfig(level=logging.INFO)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from PDF bytes."""
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def parse_resume_with_ai(resume_text: str) -> dict:
    """Use Groq to parse resume text into structured JSON."""
    prompt = f"""
Parse this resume into a structured JSON object.
Return ONLY valid JSON, no markdown, no explanation, no code blocks.

Required JSON structure:
{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "+91-XXXXXXXXXX",
  "linkedin": "linkedin URL or username",
  "github": "github URL or username",
  "summary": "profile summary paragraph",
  "education": [
    {{"degree": "...", "institution": "...", "year": "..."}}
  ],
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "duration": "Start - End",
      "bullets": ["responsibility 1", "responsibility 2"]
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "tech": "technologies used",
      "duration": "period",
      "bullets": ["point 1", "point 2"]
    }}
  ],
  "skills": {{
    "category name": "comma separated skills"
  }},
  "certifications": [
    {{"name": "cert name", "issuer": "issuer"}}
  ],
  "extracurricular": {{
    "soft_skills": ["skill1", "skill2"],
    "activities": ["activity 1", "activity 2"]
  }}
}}

Resume text:
{resume_text[:4000]}
"""
    response = litellm.completion(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        api_key=LLM_API_KEY,
        max_tokens=2000
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def tailor_resume_for_job(parsed_resume: dict, job: dict) -> str:
    """Tailor resume content for a specific job. Never fabricates."""
    prompt = f"""
You are an expert ATS resume writer. Tailor this resume for the job below.

STRICT RULES:
- NEVER add skills, experience, or achievements not in the original resume
- ONLY reorder, rephrase, and emphasise existing content
- Inject relevant keywords from the job description naturally where they already apply
- Keep all sections: Summary, Education, Experience, Projects, Skills, Certifications
- Use standard section headers — no tables, no columns
- Return the tailored resume as plain structured text only

JOB TITLE: {job.get('job_title', '')}
COMPANY: {job.get('company', '')}
JOB DESCRIPTION:
{job.get('description', '')[:2500]}

ORIGINAL RESUME:
{json.dumps(parsed_resume, indent=2)[:2500]}
"""
    response = litellm.completion(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        api_key=LLM_API_KEY,
        max_tokens=2000
    )
    return response.choices[0].message.content.strip()


def generate_cover_letter(parsed_resume: dict, job: dict) -> str:
    """Generate a professional, human-sounding cover letter."""
    prompt = f"""
Write a professional cover letter for this job application.

STRICT RULES:
- Sound like a real human wrote it, NOT like AI
- Do NOT use phrases like: "I am excited to", "I am passionate about",
  "leverage my skills", "dynamic team", "fast-paced environment",
  "I am writing to apply", "synergy", "results-driven"
- Be specific: reference the company name and exact role
- Match 2-3 real achievements from the resume to the job requirements
- Structure:
    Paragraph 1: Why this specific company and role (2 sentences)
    Paragraph 2: Most relevant experience with specific examples (3-4 sentences)
    Paragraph 3: What you bring to the team (2-3 sentences)
    Closing: Simple confident sign-off (1-2 sentences)
- Total length: 250-300 words
- No bullet points
- End with: Best regards, [Name]

APPLICANT: {parsed_resume.get('name', '')}
JOB TITLE: {job.get('job_title', '')}
COMPANY: {job.get('company', '')}
JOB DESCRIPTION:
{job.get('description', '')[:2000]}

RESUME HIGHLIGHTS:
{json.dumps(parsed_resume, indent=2)[:2000]}
"""
    response = litellm.completion(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        api_key=LLM_API_KEY,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()
