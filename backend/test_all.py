import sys
import os
import time
import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def _safe_print(text: str):
    """Print helper that safely encodes non-ascii characters for Windows console."""
    safe_text = text.encode("ascii", errors="replace").decode("ascii")
    print(safe_text)


def run_tests():
    _safe_print("=" * 60)
    _safe_print("RUNNING COMPLETE SYSTEM END-TO-END VERIFICATION TEST SUITE")
    _safe_print("=" * 60)

    # 1. Health check
    _safe_print("\n[1/8] Testing /health...")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    _safe_print(f"  [SUCCESS] Health check passed: {r.json()}")

    # 2. Auth (signup + login)
    _safe_print("\n[2/8] Testing Auth (signup + login)...")
    test_email = f"system_test_user_{int(time.time())}@example.com"
    r = requests.post(
        f"{BASE_URL}/auth/signup",
        json={"email": test_email, "password": "password123"},
    )
    assert r.status_code == 200, f"Signup failed: {r.text}"
    token = r.json()["token"]
    user_id = r.json()["user_id"]
    headers = {"Authorization": f"Bearer {token}"}
    _safe_print(f"  [SUCCESS] Signup successful: user_id={user_id}")

    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": test_email, "password": "password123"},
    )
    assert r.status_code == 200, f"Login failed: {r.text}"
    _safe_print("  [SUCCESS] Login successful")

    # 3. Scrape Jobs across all 5 major websites
    _safe_print("\n[3/8] Testing Multi-Site Web Scraper (LinkedIn, Arbeitnow, Remotive, WWR, RemoteOK)...")
    r = requests.post(f"{BASE_URL}/admin/scrape", headers=headers)
    assert r.status_code == 200, f"Scrape failed: {r.text}"
    scraped = r.json().get("scraped", {})
    _safe_print(f"  [SUCCESS] Scrape result: Total Scraped={scraped.get('total')}")

    # 4. Build Embeddings & FAISS Index
    _safe_print("\n[4/8] Testing FAISS Cosine Vector Index Builder...")
    r = requests.post(f"{BASE_URL}/admin/build-index", headers=headers)
    assert r.status_code == 200, f"Build index failed: {r.text}"
    _safe_print(f"  [SUCCESS] FAISS Index result: Total Indexed={r.json().get('indexed')}")

    # 5. Upload CV & Groq Extraction
    _safe_print("\n[5/8] Testing CV Upload + Groq LLM Profile Extractor...")
    student_cv = """
    Alex Rivera
    Computer Science & Artificial Intelligence Student | alex.rivera@university.edu
    
    EDUCATION
    BS in Computer Science (AI Track) - Expected Graduation 2026
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
    assert r.status_code == 200, f"CV upload failed: {r.text}"
    cv_data = r.json().get("structured_data")
    _safe_print(f"  [SUCCESS] CV Upload successful: cv_id={r.json().get('cv_id')}")
    _safe_print(f"    - Extracted skills: {cv_data.get('skills')}")
    _safe_print(f"    - Extracted seniority: {cv_data.get('seniority')}")

    # 6. Matching Endpoint
    _safe_print("\n[6/8] Testing Matching Engine (FAISS Cosine Retrieval + Groq Reranker)...")
    r = requests.post(f"{BASE_URL}/match/run?top_k=5", headers=headers)
    assert r.status_code == 200, f"Match run failed: {r.text}"
    matches = r.json()
    _safe_print(f"  [SUCCESS] Matches evaluated: {len(matches)} jobs returned")
    for idx, m in enumerate(matches[:3], 1):
        _safe_print(f"    #{idx}: [{m['score']}%] {m['title']} @ {m['company']} (Link: {m.get('link')})")
        _safe_print(f"         Reasons: {m.get('reasons')}")

    # 7. AI Accelerator Suite Testing
    _safe_print("\n[7/8] Testing AI Acceleration Suite (Tailor CV, Gap Analysis, Cover Letter, ATS Check, Interview Prep)...")
    job_id = matches[0]["job_id"]

    r = requests.post(f"{BASE_URL}/features/tailor-cv", headers=headers, json={"job_id": job_id})
    assert r.status_code == 200, f"CV Tailoring failed: {r.text}"
    _safe_print(f"  [SUCCESS] CV Tailoring works! Adjustments: {r.json().get('key_adjustments_made')[:2]}")

    r = requests.post(f"{BASE_URL}/features/gap-analysis", headers=headers, json={"job_id": job_id})
    assert r.status_code == 200, f"Gap analysis failed: {r.text}"
    _safe_print("  [SUCCESS] Gap Analysis works!")

    r = requests.post(f"{BASE_URL}/features/ats-check", headers=headers, json={"job_id": job_id})
    assert r.status_code == 200, f"ATS check failed: {r.text}"
    _safe_print(f"  [SUCCESS] ATS Check works! Score: {r.json().get('ats_score')}%, Matched: {r.json().get('matched_keywords')[:4]}")

    r = requests.post(f"{BASE_URL}/features/cover-letter", headers=headers, json={"job_id": job_id})
    assert r.status_code == 200, f"Cover Letter failed: {r.text}"
    _safe_print("  [SUCCESS] Cover Letter generation works!")

    r = requests.post(f"{BASE_URL}/features/interview-prep", headers=headers, json={"job_id": job_id})
    assert r.status_code == 200, f"Interview prep failed: {r.text}"
    _safe_print("  [SUCCESS] Interview Prep works!")

    # 8. Applications Pipeline CRUD
    _safe_print("\n[8/8] Testing Application Pipeline Kanban CRUD...")
    r = requests.post(f"{BASE_URL}/applications", headers=headers, json={"job_id": job_id, "status": "applied"})
    assert r.status_code == 200, f"Create application failed: {r.text}"
    app_id = r.json()["id"]

    r = requests.patch(f"{BASE_URL}/applications/{app_id}", headers=headers, json={"status": "interview"})
    assert r.status_code == 200, f"Update application failed: {r.text}"

    r = requests.get(f"{BASE_URL}/applications", headers=headers)
    assert r.status_code == 200, f"List applications failed: {r.text}"
    _safe_print(f"  [SUCCESS] Pipeline Applications tracked: {len(r.json())}")

    _safe_print("\n" + "=" * 60)
    _safe_print("ALL 8 SYSTEM END-TO-END VERIFICATION TESTS PASSED 100% CLEANLY!")
    _safe_print("=" * 60)


if __name__ == "__main__":
    run_tests()
