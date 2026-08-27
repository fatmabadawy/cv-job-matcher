from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from routers.auth import get_current_user_id
import models

router = APIRouter(prefix="/applications", tags=["applications"])

VALID_STATUSES = {"applied", "screening", "interview", "offer", "rejected", "withdrawn"}


class ApplicationCreate(BaseModel):
    job_id: int
    status: Optional[str] = "applied"
    notes: Optional[str] = ""


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


@router.get("")
def list_applications(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    apps = (
        db.query(models.Application, models.Job)
        .join(models.Job, models.Application.job_id == models.Job.id)
        .filter(models.Application.user_id == user_id)
        .all()
    )
    return [
        {
            "id": a.id,
            "job_id": a.job_id,
            "status": a.status,
            "notes": a.notes,
            "updated_at": a.updated_at,
            "job": {
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "link": j.link,
            },
        }
        for a, j in apps
    ]


@router.post("")
def create_application(
    data: ApplicationCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if data.status and data.status not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status. Valid: {VALID_STATUSES}")
    existing = db.query(models.Application).filter_by(user_id=user_id, job_id=data.job_id).first()
    if existing:
        raise HTTPException(409, "Application already exists for this job")
    app = models.Application(
        user_id=user_id,
        job_id=data.job_id,
        status=data.status or "applied",
        notes=data.notes or "",
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return {"id": app.id, "job_id": app.job_id, "status": app.status, "notes": app.notes}


@router.patch("/{app_id}")
def update_application(
    app_id: int,
    data: ApplicationUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    app = db.query(models.Application).filter_by(id=app_id, user_id=user_id).first()
    if not app:
        raise HTTPException(404, "Application not found")
    if data.status:
        if data.status not in VALID_STATUSES:
            raise HTTPException(400, f"Invalid status. Valid: {VALID_STATUSES}")
        app.status = data.status
    if data.notes is not None:
        app.notes = data.notes
    db.commit()
    return {"id": app.id, "status": app.status, "notes": app.notes}


@router.delete("/{app_id}")
def delete_application(
    app_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    app = db.query(models.Application).filter_by(id=app_id, user_id=user_id).first()
    if not app:
        raise HTTPException(404, "Application not found")
    db.delete(app)
    db.commit()
    return {"deleted": True}
