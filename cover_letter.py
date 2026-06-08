import os, json, logging
from dotenv import load_dotenv
load_dotenv()
import litellm
import supabase_utils
from config import LLM_MODEL, LLM_API_KEY, SUPABASE_TABLE_NAME

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
litellm.api_key = LLM_API_KEY

def generate_cover_letter(base_resume: dict, job: dict) -> str:
    prompt = f"""
Write a professional, personalized cover letter for this job application.
Guidelines:
- Sound human, confident, and specific — not generic
- Reference the company name and role directly
- Match 2-3 achievements from the resume to the job requirements
- Keep it to 3 short paragraphs
- Do NOT start with "I am writing to apply..."
- Return only the cover letter text, no subject line

APPLICANT NAME: {base_resume.get('name', 'Applicant')}
JOB TITLE: {job.get('job_title', '')}
COMPANY: {job.get('company', '')}
JOB DESCRIPTION:
{job.get('description', '')[:2000]}

RESUME SUMMARY:
{json.dumps(base_resume, indent=2)[:2000]}
"""
    response = litellm.completion(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        api_key=LLM_API_KEY
    )
    return response.choices[0].message.content.strip()

def main():
    base_resume = supabase_utils.get_base_resume()
    if not base_resume:
        print("ERROR: No base resume found. Run resume_parser.py first.")
        return

    # Get jobs that have tailored resumes but no cover letter yet
    jobs_result = supabase_utils.supabase.table(SUPABASE_TABLE_NAME)\
        .select("job_id, job_title, company, description, resume_score")\
        .not_.is_("tailored_resume", "null")\
        .is_("cover_letter", "null")\
        .eq("is_active", True)\
        .order("resume_score", desc=True)\
        .limit(5)\
        .execute()

    jobs = jobs_result.data
    if not jobs:
        print("No jobs need cover letters. Run resume_tailor.py first.")
        return

    print(f"Generating cover letters for {len(jobs)} jobs...")
    for job in jobs:
        print(f"  → {job.get('job_title')} at {job.get('company')}")
        letter = generate_cover_letter(base_resume, job)
        supabase_utils.supabase.table(SUPABASE_TABLE_NAME)\
            .update({"cover_letter": letter})\
            .eq("job_id", job["job_id"])\
            .execute()
        print(f"    ✓ Done")

    print("Cover letter generation complete.")

if __name__ == "__main__":
    main()