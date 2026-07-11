import logging
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List
from database import supabase
from services.resume_service import tailor_resume_for_job, generate_cover_letter
from services.email_service import send_application_email
from services.pdf_service import generate_resume_pdf, generate_cover_letter_pdf
from config import JOBS_TABLE, APPLICATIONS_TABLE, USER_RESUMES_TABLE

logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/apply", tags=["apply"])


class ApplyRequest(BaseModel):
    job_ids: List[str]


def get_user_id(authorization: str) -> str:
    token = authorization.replace("Bearer ", "").strip()
    user  = supabase.auth.get_user(token)
    if not user or not user.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user.user.id


@router.post("/")
async def apply_to_jobs(
    request:       ApplyRequest,
    authorization: str = Header(...)
):
    """Apply to selected jobs — runs full pipeline per job."""
    user_id = get_user_id(authorization)

    if len(request.job_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 jobs per batch"
        )

    # Get user's active resume
    resume_result = supabase.table(USER_RESUMES_TABLE)\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("is_active", True)\
        .limit(1)\
        .execute()

    if not resume_result.data:
        raise HTTPException(
            status_code=400,
            detail="No resume found. Please upload your resume first."
        )

    resume          = resume_result.data[0]
    parsed_data     = resume.get("parsed_data", {})
    applicant_name  = parsed_data.get("name",  "Applicant")
    applicant_email = parsed_data.get("email", "")

    results = []

    for job_id in request.job_ids:
        try:
            # Check if already applied
            existing = supabase.table(APPLICATIONS_TABLE)\
                .select("id, status")\
                .eq("user_id", user_id)\
                .eq("job_id",  job_id)\
                .execute()

            if existing.data:
                results.append({
                    "job_id":  job_id,
                    "status":  "skipped",
                    "message": "Already applied to this job"
                })
                continue

            # Get job details
            job_result = supabase.table(JOBS_TABLE)\
                .select("*")\
                .eq("job_id", job_id)\
                .execute()

            if not job_result.data:
                results.append({
                    "job_id":  job_id,
                    "status":  "failed",
                    "message": "Job not found"
                })
                continue

            job = job_result.data[0]

            # Create application record — status: processing
            app_result = supabase.table(APPLICATIONS_TABLE).insert({
                "user_id":   user_id,
                "job_id":    job_id,
                "resume_id": resume["id"],
                "status":    "processing"
            }).execute()
            app_id = app_result.data[0]["id"]

            # Step 1: Tailor resume
            logging.info(f"Tailoring resume for {job.get('job_title')} at {job.get('company')}")
            tailored_text = tailor_resume_for_job(parsed_data, job)

            # Step 2: Generate cover letter
            logging.info("Generating cover letter...")
            cover_text = generate_cover_letter(parsed_data, job)

            # Step 3: Generate PDFs
            logging.info("Generating PDFs...")
            resume_pdf = generate_resume_pdf(parsed_data, tailored_text)
            cover_pdf  = generate_cover_letter_pdf(
                cover_text, applicant_name, applicant_email, job
            )

            # Step 4: Send email
            logging.info("Sending email...")
            recipient, source = send_application_email(
                applicant_name,
                applicant_email,
                job,
                cover_pdf,
                resume_pdf
            )

            # Step 5: Update application record — status: applied
            supabase.table(APPLICATIONS_TABLE).update({
                "tailored_resume": tailored_text,
                "cover_letter":    cover_text,
                "emailed":         True,
                "recipient_email": recipient,
                "email_source":    source,
                "status":          "applied"
            }).eq("id", app_id).execute()

            results.append({
                "job_id":    job_id,
                "job_title": job.get("job_title"),
                "company":   job.get("company"),
                "status":    "applied",
                "sent_to":   recipient,
                "source":    source
            })

            logging.info(f"Applied to {job.get('job_title')} at {job.get('company')}")

        except Exception as e:
            logging.error(f"Failed for job {job_id}: {e}")
            # Mark as failed in DB if app record was created
            try:
                supabase.table(APPLICATIONS_TABLE).update({
                    "status": "failed"
                }).eq("user_id", user_id).eq("job_id", job_id).execute()
            except Exception:
                pass
            results.append({
                "job_id":  job_id,
                "status":  "failed",
                "message": str(e)
            })

    return {"results": results}


@router.get("/history")
async def get_application_history(authorization: str = Header(...)):
    """Get all applications for the current user."""
    user_id = get_user_id(authorization)

    result = supabase.table(APPLICATIONS_TABLE)\
        .select("*, jobs(job_title, company, location, level)")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .execute()

    return {"applications": result.data}
