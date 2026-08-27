from fastapi import APIRouter, UploadFile, Depends, HTTPException, File
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import get_current_user_id
import models
import shutil
import os
from services.parsing import extract_text
from services.llm import extract_cv_data

router = APIRouter(prefix="/cv", tags=["cv"])


@router.post("/upload")
def upload_cv(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    allowed = {".pdf", ".docx", ".txt"}
    ext = os.path.splitext(file.filename or "")[-1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Unsupported file type: {ext}. Use PDF, DOCX, or TXT.")

    os.makedirs("uploads", exist_ok=True)
    path = f"uploads/{user_id}_{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
        else:
            raw_text = extract_text(path)
    except Exception as e:
        raise HTTPException(422, f"Could not extract text: {e}")

    # Replace non-breaking hyphen and sanitize unicode for Windows system encoding
    raw_text = raw_text.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")

    if not raw_text.strip():
        raise HTTPException(422, "CV appears to be empty or unreadable")

    try:
        structured = extract_cv_data(raw_text)
    except Exception as e:
        raise HTTPException(502, f"LLM extraction failed: {e}")

    cv = models.CV(user_id=user_id, raw_text=raw_text, structured_data=structured)
    db.add(cv)
    db.commit()
    db.refresh(cv)

    return {"cv_id": cv.id, "structured_data": structured}


@router.get("/latest")
def get_latest_cv(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    cv = db.query(models.CV).filter_by(user_id=user_id).order_by(models.CV.id.desc()).first()
    if not cv:
        raise HTTPException(404, "No CV found")
    return {"cv_id": cv.id, "structured_data": cv.structured_data, "uploaded_at": cv.uploaded_at}
