from fastapi import APIRouter, HTTPException, Header
from database import supabase

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_from_token(authorization: str):
    token = authorization.replace("Bearer ", "").strip()
    user  = supabase.auth.get_user(token)
    if not user or not user.user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user.user


@router.get("/me")
async def get_current_user(authorization: str = Header(...)):
    """Get current logged in user profile."""
    user = get_user_from_token(authorization)

    profile = supabase.table("user_profiles")\
        .select("*")\
        .eq("id", user.id)\
        .execute()

    profile_data = profile.data[0] if profile.data else {}

    return {
        "id":         user.id,
        "email":      user.email,
        "full_name":  profile_data.get("full_name", ""),
        "avatar_url": profile_data.get("avatar_url", ""),
    }
