import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from database import supabase
from services.resume_service import extract_text_from_pdf, parse_resume_with_ai
from config import USER_RESUMES_BUCKET, USER_RESUMES_TABLE

router = APIRouter(prefix="/resume", tags=["resume"])


def get_user_id(authorization: str) -> str:
    token = authorization.replace("Bearer ", "").strip()
    user  = supabase.auth.get_user(token)
    if not user or not user.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user.user.id


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    authorization: str = Header(...)
):
    """Upload resume PDF, parse it with AI, save to Supabase."""
    user_id = get_user_id(authorization)

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    pdf_bytes = await file.read()

    if len(pdf_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB")

    # Upload to Supabase Storage
    storage_path = f"{user_id}/{uuid.uuid4()}_{file.filename}"
    supabase.storage.from_(USER_RESUMES_BUCKET).upload(
        storage_path, pdf_bytes,
        file_options={"content-type": "application/pdf", "upsert": "true"}
    )

    # Parse with AI
    text        = extract_text_from_pdf(pdf_bytes)
    parsed_data = parse_resume_with_ai(text)

    # Deactivate previous resumes
    supabase.table(USER_RESUMES_TABLE)\
        .update({"is_active": False})\
        .eq("user_id", user_id)\
        .execute()

    # Save new resume record
    result = supabase.table(USER_RESUMES_TABLE).insert({
        "user_id":      user_id,
        "file_name":    file.filename,
        "storage_path": storage_path,
        "parsed_data":  parsed_data,
        "is_active":    True
    }).execute()

    return {
        "message":     "Resume uploaded and parsed successfully",
        "resume_id":   result.data[0]["id"],
        "parsed_data": parsed_data
    }


@router.get("/me")
async def get_my_resume(authorization: str = Header(...)):
    """Get the current user's active resume."""
    user_id = get_user_id(authorization)

    result = supabase.table(USER_RESUMES_TABLE)\
        .select("*")\
        .eq("user_id", user_id)\
        .eq("is_active", True)\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="No resume found. Please upload your resume first."
        )

    return result.data[0]
