import os
import shutil
import json
import requests
from database import SessionLocal, engine, Base
import models
from services.scraper import run_all_scrapers
from services.embeddings import build_index

def purge_and_rescrape():
    print("=" * 60)
    print("1. PURGING ALL DB TABLES AND FAISS INDEX...")
    print("=" * 60)
    
    # Delete FAISS index files
    if os.path.exists("faiss_index"):
        shutil.rmtree("faiss_index")
        print("  - Deleted faiss_index/ directory")

    db = SessionLocal()
    try:
        # Clear DB tables
        m_del = db.query(models.Match).delete()
        a_del = db.query(models.Application).delete()
        c_del = db.query(models.CV).delete()
        j_del = db.query(models.Job).delete()
        db.commit()
        print(f"  - Deleted {m_del} matches, {a_del} applications, {c_del} CVs, {j_del} jobs")

        print("\n" + "=" * 60)
        print("2. SCRAPING REAL LIVE JOBS FROM ALL 5 MAJOR WEBSITES...")
        print("   (LinkedIn, Arbeitnow, Remotive, WeWorkRemotely, RemoteOK)")
        print("=" * 60)
        res = run_all_scrapers(db)
        print(f"  - Scraped REAL Jobs: LinkedIn={res.get('linkedin', 0)}, Arbeitnow={res.get('arbeitnow', 0)}, Remotive={res.get('remotive', 0)}, WWR={res.get('weworkremotely', 0)}, RemoteOK={res.get('remoteok', 0)}")
        print(f"  - TOTAL REAL JOBS SCRAPED: {res.get('total', 0)}")

        # Print top 12 real jobs scraped
        real_jobs = db.query(models.Job).all()
        print("\n  Top Scraped Real Jobs:")
        for j in real_jobs[:12]:
            print(f"    * ID #{j.id}: {j.title} @ {j.company} ({j.link})")

        print("\n" + "=" * 60)
        print("3. BUILDING FAISS VECTOR INDEX FOR REAL JOBS...")
        print("=" * 60)
        indexed_count = build_index(db)
        print(f"  - FAISS Index Built: {indexed_count} real jobs embedded into IndexFlatIP (cosine similarity)")

    finally:
        db.close()

if __name__ == "__main__":
    purge_and_rescrape()
