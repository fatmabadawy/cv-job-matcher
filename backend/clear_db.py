from database import engine, SessionLocal
from models import CV, Match, Application

def clear_old_records():
    db = SessionLocal()
    try:
        cv_count = db.query(CV).delete()
        match_count = db.query(Match).delete()
        app_count = db.query(Application).delete()
        db.commit()
        print(f"Cleared DB records: deleted {cv_count} CVs, {match_count} Matches, {app_count} Applications.")
    finally:
        db.close()

if __name__ == "__main__":
    clear_old_records()
