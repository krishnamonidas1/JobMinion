from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
from database import supabase

router = APIRouter(prefix="/preferences", tags=["preferences"])


class PreferencesUpdate(BaseModel):
    job_titles:  Optional[List[str]] = None
    locations:   Optional[List[str]] = None
    job_types:   Optional[List[str]] = None
    experience:  Optional[str]       = None
    salary_min:  Optional[int]       = None
    salary_max:  Optional[int]       = None
    skills:      Optional[List[str]] = None


def get_user_id(authorization: str) -> str:
    token = authorization.replace("Bearer ", "").strip()
    user  = supabase.auth.get_user(token)
    if not user or not user.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user.user.id


@router.get("/")
async def get_preferences(authorization: str = Header(...)):
    """Get current user's job preferences."""
    user_id = get_user_id(authorization)
    result  = supabase.table("user_profiles")\
        .select("job_titles, locations, job_types, experience, salary_min, salary_max, skills, onboarded")\
        .eq("id", user_id)\
        .execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result.data[0]


@router.put("/")
async def update_preferences(
    prefs:         PreferencesUpdate,
    authorization: str = Header(...)
):
    """Save user's job preferences."""
    user_id    = get_user_id(authorization)
    update_data = {k: v for k, v in prefs.dict().items() if v is not None}
    update_data["onboarded"] = True

    result = supabase.table("user_profiles")\
        .update(update_data)\
        .eq("id", user_id)\
        .execute()

    return {"message": "Preferences saved", "data": result.data[0] if result.data else {}}