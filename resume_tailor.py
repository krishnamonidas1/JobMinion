import os, json, logging
from dotenv import load_dotenv
load_dotenv()
import litellm
import supabase_utils
from config import LLM_MODEL, LLM_API_KEY, SUPABASE_TABLE_NAME

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
litellm.api_key = LLM_API_KEY

def tailor_resume(base_resume: dict, job: dict) -> str:
    prompt = f"""
You are an expert resume writer. Tailor the resume below to match the job description.
Rules:
- NEVER fabricate or add information not in the original resume
- Reorder bullet points to highlight most relevant experience first
- Inject job-specific keywords naturally where they already apply
- Strengthen action verbs
- Return only the tailored resume as plain text, ready to send

JOB TITLE: {job.get('job_title', '')}
COMPANY: {job.get('company', '')}
JOB DESCRIPTION:
{job.get('description', '')[:3000]}

ORIGINAL RESUME:
{json.dumps(base_resume, indent=2)[:3000]}
"""
    response = litellm.completion(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        api_key=LLM_API_KEY
    )
    return response.choices[0].message.content.strip()

def main():
    # Get base resume using existing utility
    base_resume = supabase_utils.get_base_resume()
    if not base_resume:
        print("ERROR: No base resume found. Run resume_parser.py first.")
        return

    # Get top scored jobs that haven't been tailored yet
    jobs_result = supabase_utils.supabase.table(SUPABASE_TABLE_NAME)\
        .select("job_id, job_title, company, description, resume_score")\
        .gte("resume_score", 40)\
        .is_("tailored_resume", "null")\
        .eq("is_active", True)\
        .order("resume_score", desc=True)\
        .limit(5)\
        .execute()

    jobs = jobs_result.data
    if not jobs:
        print("No jobs to tailor. Either no jobs scored above 40, or all already tailored.")
        return

    print(f"Tailoring resume for {len(jobs)} jobs...")
    for job in jobs:
        print(f"  → {job.get('job_title')} at {job.get('company')}")
        tailored = tailor_resume(base_resume, job)
        supabase_utils.supabase.table(SUPABASE_TABLE_NAME)\
            .update({"tailored_resume": tailored})\
            .eq("job_id", job["job_id"])\
            .execute()
        print(f"    ✓ Done")

    print("Resume tailoring complete.")

if __name__ == "__main__":
    main()