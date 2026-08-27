from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from routers.auth import get_current_user_id
from services.llm import (
    analyze_gap,
    generate_cover_letter,
    check_ats,
    generate_interview_prep,
    tailor_cv,
)
import models

router = APIRouter(prefix="/features", tags=["features"])


class FeatureRequest(BaseModel):
    job_id: int


def _get_cv_and_job(user_id: int, job_id: int, db: Session):
    cv = db.query(models.CV).filter_by(user_id=user_id).order_by(models.CV.id.desc()).first()
    if not cv:
        raise HTTPException(404, "No CV found. Upload a CV first.")
    job = db.query(models.Job).get(job_id)
    if not job:
        raise HTTPException(404, f"Job {job_id} not found.")
    job_dict = {
        "title": job.title,
        "company": job.company,
        "description": job.description or "",
        "requirements": job.requirements or "",
        "location": job.location or "",
        "link": job.link or "",
    }
    return cv, job_dict


@router.post("/gap-analysis")
def gap_analysis(
    req: FeatureRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    cv, job_dict = _get_cv_and_job(user_id, req.job_id, db)
    try:
        result = analyze_gap(cv.structured_data or {}, job_dict)
    except Exception as e:
        raise HTTPException(502, f"Gap analysis failed: {e}")
    return result


@router.post("/cover-letter")
def cover_letter(
    req: FeatureRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    cv, job_dict = _get_cv_and_job(user_id, req.job_id, db)
    try:
        result = generate_cover_letter(cv.structured_data or {}, job_dict)
    except Exception as e:
        raise HTTPException(502, f"Cover letter generation failed: {e}")
    return result


@router.post("/ats-check")
def ats_check(
    req: FeatureRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    cv, job_dict = _get_cv_and_job(user_id, req.job_id, db)
    try:
        result = check_ats(cv.raw_text or "", job_dict)
    except Exception as e:
        raise HTTPException(502, f"ATS check failed: {e}")
    return result


@router.post("/interview-prep")
def interview_prep(
    req: FeatureRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    cv, job_dict = _get_cv_and_job(user_id, req.job_id, db)
    try:
        result = generate_interview_prep(cv.structured_data or {}, job_dict)
    except Exception as e:
        raise HTTPException(502, f"Interview prep failed: {e}")
    return result


@router.post("/tailor-cv")
def tailor_cv_endpoint(
    req: FeatureRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """POST /features/tailor-cv: Tailors candidate CV for a target job."""
    cv, job_dict = _get_cv_and_job(user_id, req.job_id, db)
    try:
        result = tailor_cv(cv.structured_data or {}, job_dict)
    except Exception as e:
        raise HTTPException(502, f"CV tailoring failed: {e}")
    return result
