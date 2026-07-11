import os
from dotenv import load_dotenv
load_dotenv()

# Supabase
SUPABASE_URL              = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ANON_KEY         = os.environ.get("SUPABASE_ANON_KEY")

# LLM
LLM_API_KEY               = os.environ.get("LLM_API_KEY")
LLM_MODEL                 = "groq/llama-3.3-70b-versatile"
LLM_REQUEST_DELAY_SECONDS = 8

# Gmail
GMAIL_ADDRESS      = os.environ.get("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
FALLBACK_EMAIL     = os.environ.get("FALLBACK_EMAIL", os.environ.get("GMAIL_ADDRESS"))

# Table names
JOBS_TABLE            = "jobs"
APPLICATIONS_TABLE    = "applications"
USER_RESUMES_TABLE    = "user_resumes"
USER_PROFILES_TABLE   = "user_profiles"

# Storage buckets
USER_RESUMES_BUCKET   = "user-resumes"
GENERATED_PDFS_BUCKET = "generated-pdfs"

# Scraper defaults
LINKEDIN_SEARCH_QUERIES   = ["Python Developer", "Software Engineer"]
LINKEDIN_LOCATION         = "India"
LINKEDIN_GEO_ID           = 102713980
LINKEDIN_JOB_TYPE         = "F"
LINKEDIN_JOB_POSTING_DATE = "r604800"
LINKEDIN_F_WT             = 1
LINKEDIN_MAX_START        = 1
MAX_JOBS_PER_SEARCH       = 5
REQUEST_TIMEOUT           = 30
MAX_RETRIES               = 3
RETRY_DELAY_SECONDS       = 15
