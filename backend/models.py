from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    ForeignKey, TIMESTAMP, JSON, UniqueConstraint
)
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("title", "company", name="uq_job_title_company"),)
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    description = Column(Text)
    requirements = Column(Text)
    link = Column(String(500))
    embedding_status = Column(String(20), default="pending", index=True)
    scraped_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class CV(Base):
    __tablename__ = "cvs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    raw_text = Column(Text)
    structured_data = Column(JSON)
    uploaded_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_match_user_job"),)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    score = Column(Float)
    reason = Column(Text)
    alerted = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_app_user_job"),)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    status = Column(String(50), default="applied")
    notes = Column(Text, default="")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
