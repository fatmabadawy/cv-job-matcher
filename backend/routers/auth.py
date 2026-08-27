from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
import models
import auth

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthIn(BaseModel):
    email: EmailStr
    password: str


def get_current_user_id(authorization: str = Header(None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    user_id = auth.decode_token(token)
    if not user_id:
        raise HTTPException(401, "Invalid or expired token")
    return user_id


@router.post("/signup")
def signup(data: AuthIn, db: Session = Depends(get_db)):
    if db.query(models.User).filter_by(email=data.email).first():
        raise HTTPException(400, "Email already registered")
    user = models.User(
        email=data.email,
        hashed_password=auth.hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": auth.create_token(user.id), "user_id": user.id}


@router.post("/login")
def login(data: AuthIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(email=data.email).first()
    if not user or not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return {"token": auth.create_token(user.id), "user_id": user.id}


@router.get("/me")
def me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return {"id": user.id, "email": user.email}
