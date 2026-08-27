from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import get_current_user_id
from services.embeddings import embed_text, search_similar, build_index
from services.llm import rerank_jobs
import models

router = APIRouter(prefix="/match", tags=["matching"])


@router.post("/run")
def run_match(
    user_id: int = Depends(get_current_user_id),
    top_k: int = Query(20, ge=5, le=50),
    db: Session = Depends(get_db),
):
    cv = db.query(models.CV).filter_by(user_id=user_id).order_by(models.CV.id.desc()).first()
    if not cv:
        raise HTTPException(404, "No CV uploaded yet. Upload a CV first.")

    # Ensure index is up to date
    build_index(db)

    vec = embed_text(cv.raw_text)
    candidate_ids = search_similar(vec, top_k=top_k)

    if not candidate_ids:
        raise HTTPException(404, "No jobs in the index yet. Run the scraper first.")

    jobs = db.query(models.Job).filter(models.Job.id.in_(candidate_ids)).all()

    try:
        results = rerank_jobs(cv.structured_data or {}, jobs)
    except Exception as e:
        raise HTTPException(502, f"LLM reranking failed: {e}")

    # Upsert matches
    for r in results:
        existing = db.query(models.Match).filter_by(user_id=user_id, job_id=r["job_id"]).first()
        if existing:
            existing.score = r["score"]
            existing.reason = ", ".join(r.get("reasons", []))
        else:
            db.add(
                models.Match(
                    user_id=user_id,
                    job_id=r["job_id"],
                    score=r["score"],
                    reason=", ".join(r.get("reasons", [])),
                )
            )
    db.commit()

    # Return enriched results with full job details including description and link
    job_map = {j.id: j for j in jobs}
    enriched = []
    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        job = job_map.get(r["job_id"])
        if job:
            enriched.append(
                {
                    "job_id": r["job_id"],
                    "score": r["score"],
                    "reasons": r.get("reasons", []),
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "description": job.description or "",
                    "link": job.link or "",
                    "requirements": job.requirements or "",
                }
            )
    return enriched


@router.get("/results")
def get_match_results(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Return previously computed matches with full job details."""
    matches = (
        db.query(models.Match, models.Job)
        .join(models.Job, models.Match.job_id == models.Job.id)
        .filter(models.Match.user_id == user_id)
        .order_by(models.Match.score.desc())
        .all()
    )
    return [
        {
            "job_id": m.job_id,
            "score": m.score,
            "reason": m.reason,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "description": j.description or "",
            "link": j.link or "",
            "requirements": j.requirements or "",
        }
        for m, j in matches
    ]
