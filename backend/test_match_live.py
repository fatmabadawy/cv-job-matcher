import os
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_live_matching_real_data():
    print("=" * 60)
    print("MATCHING CS STUDENT CV AGAINST 50 REAL SCRAPED JOBS...")
    print("=" * 60)

    # 1. Health
    requests.get(f"{BASE_URL}/health")

    # 2. Auth
    email = f"real_job_user_{int(time.time())}@example.com"
    r = requests.post(f"{BASE_URL}/auth/signup", json={"email": email, "password": "password123"})
    assert r.status_code == 200, f"Signup failed: {r.text}"
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Upload CS Student CV
    student_cv = """
    Alex Rivera
    Computer Science & Artificial Intelligence Student | alex.rivera@university.edu
    
    EDUCATION
    BS in Computer Science (AI Track) — Expected Graduation 2026
    Coursework: Data Structures, Algorithms, Machine Learning, Web Development, Database Systems
    
    PROJECTS
    AI Resume Analyzer (2024): Built FastAPI backend with Python, SentenceTransformers, and React frontend.
    Full-Stack E-Commerce (2023): React, Node.js, PostgreSQL application with JWT authentication.
    
    SKILLS
    Languages: Python, JavaScript, SQL, HTML/CSS
    Frameworks: FastAPI, React, PyTorch, Node.js
    Databases & Tools: PostgreSQL, Git, Docker, VS Code
    """

    r = requests.post(
        f"{BASE_URL}/cv/upload",
        headers=headers,
        files={"file": ("alex_rivera_cv.txt", student_cv.encode("utf-8"), "text/plain")},
    )
    assert r.status_code == 200, f"Upload failed: {r.text}"
    print("\n[GROQ CV EXTRACTION RESULT]:")
    print(json.dumps(r.json().get("structured_data"), indent=2))

    # 4. Run Match against 50 real scraped jobs
    print("\n[RUNNING FAISS COSINE VECTOR SEARCH + GROQ RERANKING]...")
    r = requests.post(f"{BASE_URL}/match/run?top_k=10", headers=headers)
    print("MATCH RUN STATUS CODE:", r.status_code)
    assert r.status_code == 200, f"Match run failed: {r.text}"

    matches = r.json()
    print(f"\nREAL SCRAPED JOB MATCH RESULTS ({len(matches)} jobs returned):")
    for idx, m in enumerate(matches, 1):
        print(f"\n--- Rank #{idx} ---")
        print(f"Job ID: {m['job_id']}")
        print(f"Title: {m['title']} @ {m['company']}")
        print(f"Score: {m['score']}%")
        print(f"Reasons: {m.get('reasons')}")
        print(f"Link: {m.get('link')}")

if __name__ == "__main__":
    test_live_matching_real_data()
