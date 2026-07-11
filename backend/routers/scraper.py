import logging
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from services.scraper_service import run_scraper

logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/scraper", tags=["scraper"])

# In-memory status tracker
scraper_status = {"running": False, "last_result": None}


class ScrapeRequest(BaseModel):
    queries:  Optional[List[str]] = None
    location: Optional[str]       = None
    limit:    Optional[int]       = 5


def get_user_id(authorization: str):
    from database import supabase
    token = authorization.replace("Bearer ", "").strip()
    user  = supabase.auth.get_user(token)
    if not user or not user.user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user.user.id


def _run_in_background(queries, location, limit):
    scraper_status["running"] = True
    try:
        result = run_scraper(queries, location, limit)
        scraper_status["last_result"] = result
        logging.info(f"Scraper finished: {result['total_saved']} jobs saved")
    except Exception as e:
        scraper_status["last_result"] = {"error": str(e)}
        logging.error(f"Scraper error: {e}")
    finally:
        scraper_status["running"] = False


@router.post("/run")
async def trigger_scraper(
    request:          ScrapeRequest,
    background_tasks: BackgroundTasks,
    authorization:    str = Header(...)
):
    """Trigger LinkedIn job scraping in the background."""
    get_user_id(authorization)

    if scraper_status["running"]:
        raise HTTPException(
            status_code=409,
            detail="Scraper is already running. Please wait for it to finish."
        )

    background_tasks.add_task(
        _run_in_background,
        request.queries,
        request.location,
        request.limit
    )

    return {
        "message": "Scraper started in background",
        "status":  "running"
    }


@router.get("/status")
async def get_scraper_status(authorization: str = Header(...)):
    """Check if scraper is running and get last result."""
    get_user_id(authorization)

    return {
        "running":     scraper_status["running"],
        "last_result": scraper_status["last_result"]
    }
