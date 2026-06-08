# JobMinion - AI Job Application Agent

An intelligent, fully automated job application pipeline that scrapes job listings, scores them against your resume, tailors your resume per job, generates personalised cover letters, and sends applications via email - all without manual intervention.

Built as part of an internship project at NIELIT Tezpur, under Tezpur University MCA program.


## Features

- Job Scraping: Scrapes live job listings from LinkedIn using BeautifulSoup and Requests
- AI Resume Scoring: Scores each job against your resume using Groq Llama 3.3 70B (0-100)
- Resume Tailoring: Rewrites your resume to match each job description - never fabricates
- Cover Letter Generation: Writes a personalised cover letter per job using LLM
- Automated Email: Sends application emails with PDF attachments via Gmail SMTP
- PDF Generation: Generates styled one-page resume and cover letter PDFs using ReportLab
- Supabase Backend: Stores all jobs, scores, and application status in Supabase (PostgreSQL)
- Full Pipeline: Single command runs the entire workflow end to end


## Tech Stack

- Language: Python 3.11+
- LLM: Groq Llama 3.3 70B (via LiteLLM) - free tier
- Web Scraping: BeautifulSoup4, Requests
- Database: Supabase (PostgreSQL) - free tier
- PDF Generation: ReportLab
- Email: Gmail SMTP (smtplib)
- Environment: python-dotenv
- Resume Parsing: pdfplumber


## Project Structure

    JobMinion/
    |
    |-- scraper.py                  # Scrapes LinkedIn job listings
    |-- score_jobs.py               # Scores jobs against resume using AI
    |-- resume_parser.py            # Parses uploaded resume PDF with AI
    |-- resume_tailor.py            # Tailors resume per job using Groq
    |-- cover_letter.py             # Generates cover letters using Groq
    |-- email_sender.py             # Sends application emails with PDF attachments
    |-- resume_pdf_generator.py     # Generates styled one-page resume PDF
    |-- run_pipeline.py             # Runs the full pipeline in sequence
    |
    |-- supabase_utils.py           # Supabase client and helper functions
    |-- llm_client.py               # LiteLLM wrapper for Groq
    |-- config.py                   # Configuration (search queries, model, limits)
    |-- models.py                   # Pydantic data models
    |-- user_agents.py              # Rotating user agents for scraping
    |
    |-- requirements.txt            # Python dependencies
    |-- .env                        # Environment variables (not committed)
    |-- README.md                   # This file


## Setup and Installation

### 1. Clone the Repository

    git clone https://github.com/krishnamonidas1/JobMinion.git
    cd JobMinion

### 2. Create Virtual Environment

    python -m venv .venv

    # Windows
    .\.venv\Scripts\activate

    # macOS/Linux
    source .venv/bin/activate

### 3. Install Dependencies

    pip install -r requirements.txt
    playwright install chromium

### 4. Set Up Supabase

1. Create a free project at supabase.com
2. Go to SQL Editor and run the full schema from supabase_schema.sql
3. Go to Storage, open the resumes bucket, and upload your resume.pdf
4. Copy your Project URL and service_role key from Project Settings - API

### 5. Get API Keys

- Groq API Key (free): console.groq.com
- Gmail App Password (free): myaccount.google.com/apppasswords

### 6. Configure .env

Create a .env file in the project root:

    SUPABASE_URL=https://your-project-id.supabase.co
    SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

    LLM_API_KEY=your_groq_api_key

    GMAIL_ADDRESS=your_gmail@gmail.com
    GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
    FALLBACK_EMAIL=your_gmail@gmail.com

### 7. Configure Job Search in config.py

    LLM_MODEL = "groq/llama-3.3-70b-versatile"

    LINKEDIN_SEARCH_QUERIES = ["Python Developer", "Software Engineer"]
    LINKEDIN_LOCATION = "India"
    LINKEDIN_JOB_TYPE = "I"   # I = Internship, F = Full-time


## Running the Pipeline

Run the full pipeline with a single command:

    python run_pipeline.py

Or run each step individually:

    python resume_parser.py      # Step 1: Parse your resume
    python scraper.py            # Step 2: Scrape LinkedIn jobs
    python score_jobs.py         # Step 3: Score jobs vs resume
    python resume_tailor.py      # Step 4: Tailor resume per job
    python cover_letter.py       # Step 5: Generate cover letters
    python email_sender.py       # Step 6: Send application emails


## Verification

After running the pipeline, check results in Supabase SQL Editor:

    SELECT
        job_title,
        company,
        resume_score,
        CASE WHEN tailored_resume IS NOT NULL THEN 'done' ELSE 'pending' END AS tailored,
        CASE WHEN cover_letter    IS NOT NULL THEN 'done' ELSE 'pending' END AS cover_letter,
        CASE WHEN emailed = TRUE              THEN 'sent' ELSE 'pending' END AS emailed,
        COALESCE(recipient_email, 'not sent') AS sent_to
    FROM public.jobs
    ORDER BY resume_score DESC;


## Email Intelligence

The agent uses a 3-tier strategy to find the right recipient email:

1. Regex scan of job description - finds emails like hr@company.com
2. AI extraction using Groq - finds hidden or formatted contact emails
3. Company name pattern guessing - tries careers@companyname.com
4. Fallback - delivers to your own inbox for manual review


## Environment Variables

    SUPABASE_URL               Your Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY  Supabase service role secret key
    LLM_API_KEY                Groq API key
    GMAIL_ADDRESS              Gmail address to send from
    GMAIL_APP_PASSWORD         Gmail App Password (16 characters)
    FALLBACK_EMAIL             Email to deliver to if no company email found


## Important Notes

- Never commit .env - it contains sensitive credentials
- LinkedIn may rate-limit scraping - MAX_JOBS_PER_SEARCH = 2 is safe to start
- Groq free tier has rate limits - LLM_REQUEST_DELAY_SECONDS = 8 handles this
- Gmail SMTP ports may be blocked on institutional networks - use mobile hotspot if needed
- The agent never fabricates resume content - it only reorganises and highlights existing experience


## Acknowledgements
- Extended with resume tailoring, cover letter generation, PDF export, and email automation
- Built during internship at NIELIT Tezpur (Feb 2026 - Aug 2026)
- Developed by Krishnamoni Das


## License

MIT License - free to use, modify, and distribute with attribution.