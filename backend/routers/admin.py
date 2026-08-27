from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import get_current_user_id
from services.scraper import run_all_scrapers
from services.embeddings import build_index

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/scrape")
def trigger_scrape(
    db: Session = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    """Manually trigger the scraper (authenticated)."""
    counts = run_all_scrapers(db)
    return {"scraped": counts}


@router.post("/build-index")
def trigger_index(
    db: Session = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    """Manually trigger embedding index build for pending jobs."""
    count = build_index(db)
    return {"indexed": count}
