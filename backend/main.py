from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, resume, jobs, apply, scraper,preferences
  
app = FastAPI(
    title="JobMinion API",
    description="AI-powered job application agent",
    version="1.0.0"
)

# ── CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://jobminion.vercel.app",  # update after deploy
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(jobs.router)
app.include_router(apply.router)
app.include_router(scraper.router)
app.include_router(preferences.router)


# ── Health check ──────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "JobMinion API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",    # ← add this
        "http://localhost:3000",
        "https://jobminion.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
