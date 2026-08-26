# JobMinion — AI-Powered Job Application Agent

JobMinion is an AI-powered job application automation system that helps reduce the repetitive work involved in applying for jobs.

It automates the workflow from **resume parsing and job matching to resume tailoring, cover-letter generation, PDF creation, and email application**.

---

## Features

### 1. Resume Upload & AI Parsing

- Upload a resume in PDF format.
- Extract text using `pdfplumber`.
- Parse the resume into structured JSON using an LLM.
- Extract:
  - Name
  - Email
  - Phone
  - LinkedIn
  - GitHub
  - Summary
  - Education
  - Experience
  - Projects
  - Skills
  - Certifications
  - Extracurricular activities

### 2. LinkedIn Job Scraping

JobMinion collects job listings from LinkedIn, including:

- Job title
- Company
- Location
- Job description
- Job URL

The scraper can be configured with different search queries, locations and job limits.

### 3. AI Resume-to-Job Matching

The AI analyzes the relationship between the candidate's resume and a job description.

Each job can be scored based on how well the candidate's existing qualifications match the requirements.

### 4. Job-Specific Resume Tailoring

JobMinion generates a tailored version of the resume for each job.

The system follows a strict **no-fabrication policy**:

- It can reorder existing information.
- It can rephrase existing content.
- It can emphasize relevant skills and projects.
- It can align existing experience with the job description.

It does **not** invent:

- Skills
- Degrees
- Companies
- Employment history
- Projects
- Achievements
- Qualifications

### 5. Personalized Cover Letters

The system generates a separate cover letter for each job.

Cover letters are based on:

- Candidate information
- Job title
- Company
- Job description
- Existing resume experience

The system is instructed to avoid generic AI-style phrases and keep the content specific to the application.

### 6. PDF Generation

Tailored resumes and cover letters can be converted into professional PDF documents using ReportLab.

### 7. Automated Email Applications

JobMinion can:

- Identify application/contact email addresses.
- Generate the application email.
- Attach the generated resume and cover letter.
- Send the application through Gmail SMTP.

### 8. Supabase Tracking

Supabase is used to store and track application-related information such as:

- Jobs
- Applications
- Resume information
- User profiles
- Generated documents
- Application/email status

---

## System Workflow

```text
                 ┌─────────────────┐
                 │  Resume Upload  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ PDF Text        │
                 │ Extraction      │
                 │   pdfplumber    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ AI Resume       │
                 │ Parsing         │
                 │   Groq LLM      │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ LinkedIn Job    │
                 │ Scraping        │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ AI Job Matching │
                 │ & Scoring       │
                 └────────┬────────┘
                          │
                          ▼
                ┌──────────────────┐
                │ Resume Tailoring │
                └────────┬─────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
     ┌─────────────────┐   ┌──────────────────┐
     │ Tailored Resume │   │ Cover Letter     │
     └────────┬────────┘   └────────┬─────────┘
              │                     │
              └──────────┬──────────┘
                         ▼
                ┌──────────────────┐
                │ PDF Generation   │
                │    ReportLab     │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Gmail SMTP       │
                │ Application Send │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Supabase         │
                │ Tracking         │
                └──────────────────┘
```

---

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Backend API | FastAPI |
| ASGI Server | Uvicorn |
| LLM | Groq |
| Current LLM Model | `openai/gpt-oss-120b` |
| LLM Integration | LiteLLM |
| PDF Text Extraction | pdfplumber |
| Web Scraping | BeautifulSoup + Requests |
| PDF Generation | ReportLab |
| Database | Supabase |
| Email | Gmail SMTP |
| Configuration | python-dotenv |
| Validation | Pydantic |

---

## Project Structure

```text
JobMinion/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── .env
│   │
│   ├── routers/
│   │   ├── resume.py
│   │   ├── jobs.py
│   │   └── ...
│   │
│   ├── services/
│   │   ├── resume_service.py
│   │   ├── job_service.py
│   │   ├── email_service.py
│   │   ├── pdf_service.py
│   │   └── ...
│   │
│   └── ...
│
├── frontend/
│   ├── .env
│   └── ...
│
├── outputs/
│   └── ...
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

> The exact structure may change as the project evolves.

---

## Backend API

The backend is built using FastAPI.

### Start the Backend

From the project root:

```powershell
uvicorn backend.main:app --reload --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Resume Upload

The resume endpoint accepts a PDF resume and performs:

```text
PDF Upload
    ↓
Text Extraction
    ↓
AI Resume Parsing
    ↓
Structured Resume Data
    ↓
Supabase Storage/Database
```

Example endpoint:

```text
POST /resume/upload
```

---

## Environment Variables

The backend uses a separate `.env` file.

### `backend/.env`

```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Groq
LLM_API_KEY=your_groq_api_key

# Gmail
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
FALLBACK_EMAIL=fallback@example.com
```

### Important

Never commit real credentials to GitHub.

The following should remain private:

```text
.env
API keys
Supabase service-role keys
Gmail app passwords
Access tokens
```

Use `.env.example` to document the required variables without exposing secrets.

---

## LLM Configuration

The LLM configuration is defined in:

```text
backend/config.py
```

Current configuration:

```python
LLM_MODEL = "groq/openai/gpt-oss-120b"
```

LiteLLM is used as the interface between the application and Groq.

Example:

```python
response = litellm.completion(
    model=LLM_MODEL,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    api_key=LLM_API_KEY,
    max_tokens=4000
)
```

---

## Resume Processing

The main resume-processing service is:

```text
backend/services/resume_service.py
```

It currently provides:

```python
extract_text_from_pdf()
parse_resume_with_ai()
tailor_resume_for_job()
generate_cover_letter()
```

### Resume Parsing

The PDF is processed using:

```text
pdfplumber
```

The extracted text is then passed to the LLM and converted into structured JSON.

### Resume Tailoring

The system is explicitly instructed not to fabricate information.

### Cover Letter Generation

Cover letters are generated from the actual resume information and job description.

---

## Ethical Design

JobMinion is designed as an application productivity tool, not a tool for misrepresenting candidates.

### What JobMinion Does

- Highlights relevant existing skills.
- Reorders relevant experience.
- Rephrases existing content.
- Matches existing qualifications to job requirements.
- Generates personalized application documents.

### What JobMinion Never Does

- Invent skills.
- Invent degrees.
- Invent work experience.
- Invent projects.
- Invent achievements.
- Create fake employment history.
- Exaggerate qualifications.

The candidate's original information remains the source of truth.

---

## Database

Supabase is used for persistent application data.

Configured tables include:

```text
jobs
applications
user_resumes
user_profiles
```

Storage buckets include:

```text
user-resumes
generated-pdfs
```

---

## Email Automation

JobMinion uses Gmail SMTP for application emails.

The workflow is:

```text
Job
 ↓
Find Recipient Email
 ↓
Generate Email
 ↓
Attach Resume PDF
 ↓
Attach Cover Letter PDF
 ↓
Send Email
 ↓
Store Status in Supabase
```

A fallback email can be configured using:

```env
FALLBACK_EMAIL=your@email.com
```

---

## Current Development Status

### Completed

- [x] FastAPI backend
- [x] Resume PDF text extraction
- [x] AI resume parsing
- [x] Groq/LiteLLM integration
- [x] LinkedIn job scraping
- [x] AI job matching/scoring
- [x] Job-specific resume tailoring
- [x] Personalized cover-letter generation
- [x] PDF generation
- [x] Gmail email automation
- [x] Supabase integration
- [x] Application tracking
- [x] Environment-based configuration
- [x] Backend resume upload API

### In Progress / Improvements

- [ ] Improve structured JSON reliability for resume parsing
- [ ] Add robust LLM response validation
- [ ] Improve error handling for malformed AI responses
- [ ] Improve frontend/backend integration
- [ ] Add comprehensive automated tests
- [ ] Improve LinkedIn scraping reliability
- [ ] Add better application history and status UI

---

## Running the Project

### 1. Clone the repository

```bash
git clone <repository-url>
cd JobMinion
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure environment variables

Create:

```text
backend/.env
```

and add the required Supabase, Groq and Gmail credentials.

### 6. Start the backend

```powershell
uvicorn backend.main:app --reload --port 8000
```

### 7. Open API documentation

```text
http://127.0.0.1:8000/docs
```

---

## Troubleshooting

### `Could not import module "main"`

If `main.py` is located at:

```text
JobMinion/backend/main.py
```

start Uvicorn from the project root using:

```powershell
uvicorn backend.main:app --reload --port 8000
```

Do not use:

```powershell
uvicorn main:app --reload --port 8000
```

from the project root.

---

### LLM API Key Not Found

Check:

```powershell
python -c "from backend.config import LLM_API_KEY; print(bool(LLM_API_KEY))"
```

Expected:

```text
True
```

The backend loads:

```text
backend/.env
```

---

### Groq Model Error

Check the configured model in:

```text
backend/config.py
```

Current model:

```python
LLM_MODEL = "groq/openai/gpt-oss-120b"
```

Make sure the selected model is available to the Groq API key being used.

---

### Invalid JSON From LLM

Resume parsing depends on structured JSON output from the LLM.

If the LLM returns incomplete JSON, parsing may fail with:

```text
json.decoder.JSONDecodeError
```

For long resumes, use an appropriate completion limit:

```python
max_tokens=4000
```

The application should also validate malformed responses before storing the parsed resume.

---

## Security

Never commit credentials.

Make sure `.gitignore` contains:

```gitignore
.env
backend/.env
frontend/.env
.venv/
venv/
__pycache__/
*.pyc
outputs/
```

Use:

```text
.env.example
```

for sharing the required environment-variable structure.

---

## Design Principles

JobMinion follows four main principles:

### Automation

Reduce repetitive manual work involved in job applications.

### Personalization

Each application should be adapted to the specific job.

### Accuracy

Generated content must be grounded in the candidate's actual information.

### Transparency

Application status, documents and job information should be traceable through Supabase.

---

## Future Improvements

Potential future enhancements include:

- Browser-based job search
- More job platforms
- Advanced semantic job matching
- Resume version management
- Application dashboard
- Application analytics
- Email reply tracking
- Better duplicate-job detection
- Improved AI structured-output validation
- Background job processing
- User authentication
- Deployment with Docker
- Production cloud deployment

---

## How to run start jobminion
- (.venv) PS C:\Users\KRISHNAMONI\JobMinion> 
cd backend
uvicorn main:app --reload --port 8000

- Another terminal
- (.venv) PS C:\Users\KRISHNAMONI\JobMinion>
cd frontend
npm run dev

