# JobMinion - AI Job Application Agent

JobMinion is a full-stack AI-powered web application that automates the entire job application process. Users upload their resume, browse scraped job listings, select jobs they want to apply to, and the system automatically tailors their resume, generates a professional cover letter, and sends the application via email — all without manual intervention.

Built as part of an internship project at NIELIT Tezpur


---


## What It Does

1. User registers and logs in (Google or Email)
2. User uploads their resume PDF
3. System parses the resume using Groq Llama 3.3 70B
4. Admin scrapes fresh job listings from LinkedIn
5. User browses jobs and selects up to 10
6. For each selected job, the system:
   - Tailors the resume to match the job description (never fabricates)
   - Generates a professional, human-sounding cover letter
   - Converts both to styled PDF files
   - Finds the HR/recruiter email from the job posting
   - Sends a professional application email with both PDFs attached
7. User tracks all applications on the Applications page


---


## Tech Stack

    Frontend        React, Tailwind CSS, Vite
    Backend         FastAPI (Python)
    Auth            Supabase Auth (Google + Email/Password)
    Database        Supabase (PostgreSQL)
    Storage         Supabase Storage
    LLM             Groq Llama 3.3 70B (via LiteLLM) - free tier
    PDF Generation  ReportLab
    Web Scraping    BeautifulSoup4, Requests
    Email           Gmail SMTP (smtplib)
    Deployment      Vercel (frontend), Railway (backend)


---


## Folder Structure

    JobMinion/
    |
    |-- backend/
    |   |
    |   |-- routers/
    |   |   |-- __init__.py
    |   |   |-- auth.py              GET /auth/me
    |   |   |-- jobs.py              GET /jobs/  GET /jobs/{id}
    |   |   |-- resume.py            POST /resume/upload  GET /resume/me
    |   |   |-- apply.py             POST /apply/  GET /apply/history
    |   |   |-- scraper.py           POST /scraper/run  GET /scraper/status
    |   |
    |   |-- services/
    |   |   |-- __init__.py
    |   |   |-- resume_service.py    Parse, tailor resume, generate cover letter
    |   |   |-- email_service.py     Find HR email, send SMTP email
    |   |   |-- pdf_service.py       Generate resume and cover letter PDFs
    |   |   |-- scraper_service.py   Scrape LinkedIn job listings
    |   |
    |   |-- main.py                  FastAPI app entry point
    |   |-- config.py                Environment variables and settings
    |   |-- database.py              Supabase client
    |   |-- requirements.txt         Python dependencies
    |   |-- .env                     Backend secrets (never commit this)
    |
    |-- frontend/
    |   |
    |   |-- src/
    |   |   |-- context/
    |   |   |   |-- AuthContext.jsx  Global auth state management
    |   |   |
    |   |   |-- lib/
    |   |   |   |-- supabase.js      Supabase client
    |   |   |   |-- api.js           Axios instance with JWT interceptor
    |   |   |
    |   |   |-- components/
    |   |   |   |-- Navbar.jsx       Top navigation bar
    |   |   |
    |   |   |-- pages/
    |   |   |   |-- Login.jsx        Sign in page
    |   |   |   |-- Register.jsx     Sign up page
    |   |   |   |-- Dashboard.jsx    Home after login
    |   |   |   |-- Jobs.jsx         Browse and select jobs
    |   |   |   |-- Applications.jsx Application history
    |   |   |
    |   |   |-- App.jsx              Routes and auth guard
    |   |   |-- main.jsx             React entry point
    |   |   |-- index.css            Tailwind imports
    |   |
    |   |-- vite.config.js           Vite and Tailwind config
    |   |-- package.json             Node dependencies
    |   |-- .env                     Frontend public keys only
    |
    |-- .gitignore
    |-- README.md


---


## Prerequisites

Before setting up, make sure you have the following installed:

    Python 3.11 or higher       python.org
    Node.js 18 or higher        nodejs.org
    Git                         git-scm.com

You will also need free accounts on:

    Supabase        supabase.com        (database and auth)
    Groq            console.groq.com    (LLM API)
    Google Cloud    console.cloud.google.com  (OAuth for Google login)
    Gmail           gmail.com           (sending emails)


---


## Setup Instructions


### 1. Clone the Repository

    git clone https://github.com/yourusername/JobMinion.git
    cd JobMinion


### 2. Supabase Setup

1. Go to supabase.com and create a free project
2. Go to SQL Editor and run the full schema from supabase_schema.sql
3. Go to Authentication - Providers and enable Email and Google
4. For Google provider, you need OAuth credentials from Google Cloud Console:
   - Create a project at console.cloud.google.com
   - Go to APIs and Services - Credentials - Create OAuth 2.0 Client ID
   - Add your Supabase callback URL as an authorized redirect URI:
     https://your-project-id.supabase.co/auth/v1/callback
   - Copy the Client ID and Secret into Supabase Google provider settings
5. Go to Project Settings - API and copy your Project URL, anon key, and service_role key


### 3. Groq API Key

1. Go to console.groq.com and sign up for free
2. Go to API Keys - Create API Key
3. Copy the key (starts with gsk_)


### 4. Gmail App Password

1. Enable 2-Step Verification on your Google account
2. Go to myaccount.google.com/apppasswords
3. Create a new app password named JobMinion
4. Copy the 16-character password


### 5. Backend Setup

    cd backend
    python -m venv .venv

    # Windows
    .\.venv\Scripts\activate

    # macOS/Linux
    source .venv/bin/activate

    pip install -r requirements.txt

Create backend/.env with the following:

    SUPABASE_URL=https://your-project-id.supabase.co
    SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
    SUPABASE_ANON_KEY=your_anon_key

    LLM_API_KEY=your_groq_api_key

    GMAIL_ADDRESS=your_gmail@gmail.com
    GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
    FALLBACK_EMAIL=your_gmail@gmail.com

Start the backend:

    uvicorn main:app --reload --port 8000

The API will be available at http://localhost:8000
API documentation will be at http://localhost:8000/docs


### 6. Frontend Setup

    cd frontend
    npm install

Create frontend/.env with the following:

    VITE_SUPABASE_URL=https://your-project-id.supabase.co
    VITE_SUPABASE_ANON_KEY=your_anon_key
    VITE_API_URL=http://localhost:8000

Start the frontend:

    npm run dev

The app will be available at http://localhost:5173


---


## How to Use the Web App

### Step 1: Register or Sign In

Go to http://localhost:5173 and either:
- Click Continue with Google to sign in with your Google account
- Or fill in your name, email, and password to create an account


### Step 2: Upload Your Resume

On the Dashboard, click the resume upload area and select your resume PDF.
The system will automatically parse your resume using AI and extract your
name, email, skills, experience, education, and projects.


### Step 3: Scrape Fresh Jobs

On the Dashboard, click Scrape New Jobs. This triggers a LinkedIn scraper
that runs in the background and populates the job database with fresh listings.
Wait about 1-2 minutes, then go to the Jobs page.


### Step 4: Browse and Select Jobs

Go to Browse Jobs. You will see all available job listings. Click on any
job card to select it (a blue checkmark appears). You can select up to 10 jobs
at a time. Use the search bar to filter by job title or company.


### Step 5: Apply

Once you have selected your jobs, click Apply Now at the bottom of the screen.
For each job, the system will:

    1. Tailor your resume to match the job description
    2. Write a professional cover letter
    3. Generate both as PDF files
    4. Find the HR email from the job posting
    5. Send a professional email with both PDFs attached

This takes about 30-60 seconds per job.


### Step 6: Track Applications

Go to My Applications to see all your submitted applications, their status,
and which email address the application was sent to.


---


## API Endpoints

    GET  /health                  Health check
    GET  /auth/me                 Get current user profile
    POST /resume/upload           Upload and parse resume PDF
    GET  /resume/me               Get current user resume
    GET  /jobs/                   Get job listings (search, filter, paginate)
    GET  /jobs/{job_id}           Get single job details
    POST /apply/                  Apply to selected jobs
    GET  /apply/history           Get user application history
    POST /scraper/run             Trigger LinkedIn scraper
    GET  /scraper/status          Get scraper status and last result

Full interactive documentation is available at http://localhost:8000/docs


---


## Email Intelligence

The system uses a 3-tier strategy to find the right HR email for each job:

    Tier 1: Regex scan of the job description (finds emails like hr@company.com)
    Tier 2: AI extraction using Groq (finds hidden or formatted contact emails)
    Tier 3: Company name pattern guessing (tries careers@companyname.com)
    Fallback: Delivers to your own inbox for manual review if nothing found


---


## Environment Variables Reference

Backend (.env):

    SUPABASE_URL               Your Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY  Supabase service role secret key (full DB access)
    SUPABASE_ANON_KEY          Supabase public anon key
    LLM_API_KEY                Groq API key
    GMAIL_ADDRESS              Gmail address to send from
    GMAIL_APP_PASSWORD         Gmail App Password (16 characters with spaces)
    FALLBACK_EMAIL             Your email — receives applications when no HR email found

Frontend (.env):

    VITE_SUPABASE_URL          Same Supabase URL (safe for browser)
    VITE_SUPABASE_ANON_KEY     Supabase anon key (safe for browser)
    VITE_API_URL               Backend URL (http://localhost:8000 for local dev)


---


## Important Notes

- Never commit .env files — they contain sensitive credentials
- The system never fabricates resume content — it only reorders and emphasises existing experience
- LinkedIn may rate-limit scraping — the scraper has built-in delays and retries
- Groq free tier has rate limits — LLM_REQUEST_DELAY_SECONDS handles this
- Gmail SMTP ports may be blocked on institutional networks — use a mobile hotspot if needed
- Resume tailoring is ATS-friendly: plain text structure, standard section headers, no tables


---


## Acknowledgements

- Full-stack web app, multi-user auth, resume tailoring, PDF generation, and email automation
- Built during internship at NIELIT Tezpur (Feb 2026 - Aug 2026)
- Developed by Krishnamoni Das, MCA student, Tezpur University


---


## License

MIT License

Copyright (c) 2026 Krishnamoni Das

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
