import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

db_url = DATABASE_URL

# Check engine type
if "sqlite" in db_url:
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            pass
    except Exception as e:
        print(f"[database] Could not connect to Postgres ({e}). Falling back to SQLite.")
        db_url = "sqlite:///./jobsdb.db"
        engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
