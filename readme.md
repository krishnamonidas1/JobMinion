# JobMinion - AI Job Application Agent

JobMinion is a full-stack AI-powered web application that automates the entire job application
process. Users register, upload their resume, set job preferences, browse scraped LinkedIn
listings, select jobs they want to apply to, and the system automatically tailors their resume,
generates a professional cover letter, and sends the application via email with both documents
attached as PDFs.



---


## What It Does

1. User registers and logs in using Google or Email with full verification
2. User uploads their resume PDF
3. System parses the resume using Groq Llama 3.3 70B into structured data
4. User sets job preferences: roles, location, job type, experience, salary, skills
5. System scrapes fresh job listings from LinkedIn based on preferences
6. User browses jobs and selects up to 10 at a time
7. For each selected job, the system runs a full pipeline:
   - Tailors the resume to match the job description (never fabricates content)
   - Generates a professional, human-sounding cover letter
   - Converts both to ATS-friendly styled PDF files
   - Finds the HR or recruiter email from the job posting
   - Sends a professional application email with both PDFs attached
8. User tracks all applications and their status on the Applications page


---


## Features

Authentication and Security
- Google OAuth and Email and Password login
- Email verification required on signup
- Strong password rules with real-time strength meter
- Show and hide password toggle
- Rate limiting: account locks after 5 failed attempts for 5 minutes
- Remember me option
- Forgot password and reset password flow

Job Preferences
- Job titles and roles with autocomplete suggestions
- Preferred locations
- Job type selector: Full-time, Internship, Remote, Hybrid, Part-time, Contract
- Experience level: Fresher, Junior, Mid, Senior
- Expected salary range in LPA
- Skills and tech stack filter with autocomplete
- Preferences saved to profile and used automatically when scraping

Job Pipeline
- LinkedIn job scraper runs in background via API trigger
- Jobs filtered and displayed based on user preferences
- Resume tailored per job using Groq LLM (no fabrication, only reordering)
- Professional cover letter generated per job
- ATS-friendly one-page resume PDF generated using ReportLab
- 3-tier HR email detection: regex scan, AI extraction, company name pattern
- Professional HTML email with PDF attachments sent via Gmail SMTP

Dashboard
- Resume upload with instant AI parsing
- Application stats: total, successful, processing, failed
- One-click job scraping trigger with live status polling
- Recent applications summary


---


## Tech Stack

    Frontend        React 18, Tailwind CSS, Vite
    Backend         FastAPI (Python 3.11+)
    Auth            Supabase Auth (Google OAuth + Email/Password)
    Database        Supabase (PostgreSQL) with Row Level Security
    Storage         Supabase Storage (private buckets per user)
    LLM             Groq Llama 3.3 70B via LiteLLM (free tier)
    PDF Generation  ReportLab
    Web Scraping    BeautifulSoup4, Requests
    Email           Gmail SMTP via smtplib
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
    |   |   |-- preferences.py       GET /preferences/  PUT /preferences/
    |   |
    |   |-- services/
    |   |   |-- __init__.py
    |   |   |-- resume_service.py    Parse resume, tailor per job, generate cover letter
    |   |   |-- email_service.py     Find HR email, send SMTP email with attachments
    |   |   |-- pdf_service.py       Generate ATS resume PDF and cover letter PDF
    |   |   |-- scraper_service.py   Scrape LinkedIn job listings
    |   |
    |   |-- main.py                  FastAPI app entry point with CORS
    |   |-- config.py                All settings and environment variables
    |   |-- database.py              Supabase client initialisation
    |   |-- requirements.txt         Python dependencies
    |   |-- .env                     Backend secrets (never commit)
    |
    |-- frontend/
    |   |
    |   |-- src/
    |   |   |
    |   |   |-- context/
    |   |   |   |-- AuthContext.jsx      Global auth state, Google and email auth methods
    |   |   |
    |   |   |-- lib/
    |   |   |   |-- supabase.js          Supabase browser client
    |   |   |   |-- api.js               Axios instance with automatic JWT injection
    |   |   |
    |   |   |-- components/
    |   |   |   |-- Navbar.jsx           Top navigation with all page links
    |   |   |
    |   |   |-- pages/
    |   |   |   |-- Login.jsx            Secure sign in with rate limiting and remember me
    |   |   |   |-- Register.jsx         Sign up with password strength and validation
    |   |   |   |-- ForgotPassword.jsx   Send password reset email
    |   |   |   |-- ResetPassword.jsx    Set new password after reset
    |   |   |   |-- Dashboard.jsx        Home: stats, resume upload, scraper trigger
    |   |   |   |-- Jobs.jsx             Browse, search, select and apply to jobs
    |   |   |   |-- Applications.jsx     Full application history with status
    |   |   |   |-- Preferences.jsx      Job preferences: roles, location, type, skills
    |   |   |
    |   |   |-- App.jsx              All routes with auth guard
    |   |   |-- main.jsx             React entry point
    |   |   |-- index.css            Tailwind CSS import
    |   |
    |   |-- vite.config.js           Vite and Tailwind plugin config
    |   |-- package.json             Node dependencies
    |   |-- .env                     Frontend public Supabase keys only
    |
    |-- job-scraper/                 Original CLI pipeline (kept for reference)
    |   |-- scraper.py
    |   |-- score_jobs.py
    |   |-- resume_parser.py
    |   |-- resume_tailor.py
    |   |-- cover_letter.py
    |   |-- email_sender.py
    |   |-- resume_pdf_generator.py
    |   |-- run_pipeline.py
    |
    |-- .gitignore
    |-- README.md


---


## Prerequisites

Make sure you have these installed before starting:

    Python 3.11 or higher       python.org/downloads
    Node.js 18 or higher        nodejs.org
    Git                         git-scm.com

You also need free accounts on:

    Supabase            supabase.com
    Groq                console.groq.com
    Google Cloud        console.cloud.google.com
    Gmail               gmail.com


---


## Setup Instructions


### 1. Clone the Repository

    git clone https://github.com/yourusername/JobMinion.git
    cd JobMinion


### 2. Supabase Setup

1. Go to supabase.com and create a free project
2. Go to SQL Editor and run the full schema from supabase_schema.sql
   This creates: user_profiles, user_resumes, jobs, applications tables
   and storage buckets: user-resumes and generated-pdfs
3. Go to Authentication - Providers:
   - Enable Email provider (on by default)
   - Enable Google provider (requires OAuth credentials below)
4. Go to Authentication - Settings:
   - Enable Confirm email
   - Set Site URL to http://localhost:5174
   - Add http://localhost:5174/reset-password to Redirect URLs
5. Go to Project Settings - API and note down:
   - Project URL
   - anon public key
   - service_role secret key


### 3. Google OAuth Setup (for Google login)

1. Go to console.cloud.google.com and create a new project named JobMinion
2. Go to APIs and Services - OAuth consent screen
   - User Type: External
   - Fill in app name and email, then save
3. Go to Credentials - Create Credentials - OAuth 2.0 Client ID
   - Application type: Web application
   - Add this to Authorized redirect URIs:
     https://your-project-id.supabase.co/auth/v1/callback
4. Copy the Client ID and Client Secret
5. Paste both into Supabase - Authentication - Providers - Google - Save


### 4. Groq API Key

1. Go to console.groq.com and sign up for free
2. Go to API Keys and create a new key
3. Copy the key (it starts with gsk_)


### 5. Gmail App Password

1. Enable 2-Step Verification on your Google account
2. Go to myaccount.google.com/apppasswords
3. Create a new app password and name it JobMinion
4. Copy the 16-character password (keep the spaces)


### 6. Backend Setup

    cd backend

    python -m venv .venv

    # Windows
    .\.venv\Scripts\activate

    # macOS / Linux
    source .venv/bin/activate

    pip install -r requirements.txt

Create the file backend/.env with your actual values:

    SUPABASE_URL=https://your-project-id.supabase.co
    SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
    SUPABASE_ANON_KEY=your_anon_key

    LLM_API_KEY=your_groq_api_key

    GMAIL_ADDRESS=your_gmail@gmail.com
    GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
    FALLBACK_EMAIL=your_gmail@gmail.com

Start the backend server:

    uvicorn main:app --reload --port 8000

The API runs at http://localhost:8000
Interactive API docs are at http://localhost:8000/docs


### 7. Frontend Setup

    cd frontend
    npm install

Create the file frontend/.env with your actual values:

    VITE_SUPABASE_URL=https://your-project-id.supabase.co
    VITE_SUPABASE_ANON_KEY=your_anon_key
    VITE_API_URL=http://localhost:8000

Start the frontend:

    npm run dev

The app runs at http://localhost:5173 or http://localhost:5174


---


## How to Use the Web App


### Step 1: Register

Go to the app URL and click Create one to register.
Choose Continue with Google for instant access, or fill in your name,
email, and a strong password. If using email, check your inbox to verify
your account before signing in.


### Step 2: Upload Your Resume

On the Dashboard, click the resume upload area and select your PDF file.
The system parses it automatically using AI and extracts your name, email,
skills, experience, education, and projects. This takes about 10 seconds.


### Step 3: Set Your Preferences

Click Preferences in the navigation bar. Set:
- The job roles you are targeting (e.g. Python Developer, ML Engineer)
- Your preferred locations (e.g. Bangalore, Remote)
- Job types you want (Full-time, Internship, Remote)
- Your experience level
- Expected salary range
- Your key skills and tech stack

Save your preferences. These are used automatically when scraping jobs.


### Step 4: Scrape Fresh Jobs

On the Dashboard, click Scrape New Jobs. The system scrapes LinkedIn
in the background using your saved preferences. Wait 1 to 2 minutes.
When done it shows how many new jobs were added.


### Step 5: Browse and Select Jobs

Click Browse Jobs in the navigation. You will see all available listings.
Click any job card to select it (a blue checkmark appears). Select up to
10 jobs. Use the search bar to filter by title or company name.


### Step 6: Apply

Once jobs are selected, click Apply Now in the floating bar at the bottom.
For each job the system will:
- Tailor your resume keywords to match the job description
- Write a professional cover letter specific to that company and role
- Generate both as PDF files
- Find the HR or recruiter email from the listing
- Send a professional email with both PDFs attached

This takes 30 to 60 seconds per job.


### Step 7: Track Applications

Click My Applications to see all submitted applications with their status
(applied, processing, failed), the company name, and the email address
the application was sent to.


---


## API Reference

    GET  /health                  Health check
    GET  /auth/me                 Get current user profile
    POST /resume/upload           Upload and parse resume PDF
    GET  /resume/me               Get current user active resume
    GET  /jobs/                   Get job listings with search and filter
    GET  /jobs/{job_id}           Get single job details
    POST /apply/                  Apply to selected jobs (max 10)
    GET  /apply/history           Get all applications for current user
    POST /scraper/run             Trigger LinkedIn scraper in background
    GET  /scraper/status          Get scraper running status and last result
    GET  /preferences/            Get current user job preferences
    PUT  /preferences/            Update current user job preferences

Full interactive docs with request and response examples at:
http://localhost:8000/docs


---


## Database Schema

    user_profiles       Extends Supabase auth with name, avatar, job preferences
    user_resumes        Each user's uploaded resume file and parsed JSON data
    jobs                Shared job listings scraped from LinkedIn
    applications        Per-user application records with status and generated content


---


## Security

    All routes require a valid Supabase JWT token
    Row Level Security is enabled on all tables
    Users can only access their own resumes and applications
    Storage buckets are private and folder-scoped per user ID
    Service role key is only used server-side and never exposed to the browser
    Email verification is required before login
    Password reset uses a secure token sent to the registered email
    Login rate limiting prevents brute force attacks


---


## Email Intelligence

The system uses a 3-tier strategy to find the right recipient email per job:

    Tier 1   Regex scan of the job description text
             Finds direct emails like hr@company.com or apply@company.com
    Tier 2   AI extraction using Groq
             Finds emails mentioned in formatted or obfuscated text
    Tier 3   Company name pattern matching
             Tries careers@companyname.com based on the company name
    Fallback Delivers to your own inbox for manual review


---


## Environment Variables

Backend (backend/.env):

    SUPABASE_URL                Your Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY   Full database access key - keep this secret
    SUPABASE_ANON_KEY           Public key also used by frontend
    LLM_API_KEY                 Groq API key for LLM calls
    GMAIL_ADDRESS               Gmail address emails are sent from
    GMAIL_APP_PASSWORD          Gmail App Password, 16 characters with spaces
    FALLBACK_EMAIL              Your email for receiving fallback applications

Frontend (frontend/.env):

    VITE_SUPABASE_URL           Same Supabase URL, safe for browser
    VITE_SUPABASE_ANON_KEY      Public anon key, safe for browser
    VITE_API_URL                Backend URL (http://localhost:8000 locally)


---


## Important Notes

Never commit .env files. They are listed in .gitignore.

The resume tailoring system never fabricates content. It only reorders
bullet points, emphasises relevant existing experience, and injects keywords
from the job description where they naturally apply.

LinkedIn may rate-limit scraping. The scraper includes random delays between
requests and automatic retry logic with rotating user agents.

Gmail SMTP ports 465 and 587 may be blocked on institutional or college
networks. Use a mobile hotspot if emails are not sending.

Groq free tier has request rate limits. The LLM_REQUEST_DELAY_SECONDS
setting in config.py handles this automatically.


---


## Acknowledgements

Base scraper concept inspired by anandanair/job-scraper on GitHub.
Extended with multi-user authentication, job preferences, resume tailoring,
ATS-friendly PDF generation, intelligent email detection, and a full React
web application.

Developed by Krishna Moni Das


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