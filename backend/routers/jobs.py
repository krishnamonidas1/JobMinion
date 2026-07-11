from fastapi import APIRouter, HTTPException, Header, Query
from database import supabase
from config import JOBS_TABLE

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_user_id(authorization: str) -> str:
    token = authorization.replace("Bearer ", "").strip()
    user  = supabase.auth.get_user(token)
    if not user or not user.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user.user.id


@router.get("/")
async def get_jobs(
    search:        str = Query(None),
    location:      str = Query(None),
    limit:         int = Query(20),
    offset:        int = Query(0),
    authorization: str = Header(...)
):
    """Get paginated job listings with optional search filter."""
    get_user_id(authorization)

    query = supabase.table(JOBS_TABLE)\
        .select("job_id, job_title, company, location, level, description, provider, scraped_at")\
        .eq("is_active", True)\
        .order("scraped_at", desc=True)\
        .range(offset, offset + limit - 1)

    if search:
        query = query.or_(
            f"job_title.ilike.%{search}%,"
            f"company.ilike.%{search}%,"
            f"description.ilike.%{search}%"
        )

    if location:
        query = query.ilike("location", f"%{location}%")

    result = query.execute()

    return {
        "jobs":  result.data,
        "count": len(result.data)
    }


@router.get("/{job_id}")
async def get_job(
    job_id:        str,
    authorization: str = Header(...)
):
    """Get a single job by job_id."""
    get_user_id(authorization)

    result = supabase.table(JOBS_TABLE)\
        .select("*")\
        .eq("job_id", job_id)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")

    return result.data[0]
