import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, SessionLocal
from routers import auth as auth_router
from routers import cv as cv_router
from routers import matching as matching_router
from routers import features as features_router
from routers import applications as applications_router
from routers import admin as admin_router
from jobs.job_alerts import start_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _bootstrap_jobs():
    """Scrape + index in a background thread so /health is available immediately."""
    from services.scraper import run_all_scrapers
    from services.embeddings import build_index

    db = SessionLocal()
    try:
        counts = run_all_scrapers(db)
        indexed = build_index(db)
        logger.info("[bootstrap] scraped=%s indexed=%s", counts, indexed)
    except Exception as e:
        logger.error("[bootstrap] failed: %s", e)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified.")
    start_scheduler()
    threading.Thread(target=_bootstrap_jobs, daemon=True, name="bootstrap-jobs").start()
    yield


app = FastAPI(
    title="AI CV → Job Matcher",
    description="Upload your CV, scrape jobs, match with FAISS + LLM reranking.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(cv_router.router)
app.include_router(matching_router.router)
app.include_router(features_router.router)
app.include_router(applications_router.router)
app.include_router(admin_router.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "cv-job-matcher"}


@app.get("/")
def root():
    return {"message": "CV Job Matcher API. See /docs for Swagger UI."}
