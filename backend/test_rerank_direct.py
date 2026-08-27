import os
import json
import httpx
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=key, timeout=30.0, http_client=httpx.Client(timeout=30.0))

candidate = {
    "skills": ["Python", "FastAPI", "React", "PostgreSQL"],
    "years_experience": 0,
    "seniority": "Entry/Student",
    "summary": "CS student with experience in Python FastAPI and React web development."
}

jobs = [
    {"job_id": 1, "title": "Junior Python Developer", "company": "TechCorp", "top_requirements": "Python, FastAPI, SQL"},
    {"job_id": 2, "title": "Post Office Manager", "company": "PostCorp", "top_requirements": "Logistics, Staff Management"},
    {"job_id": 3, "title": "Beauty Merchandiser", "company": "GlamCo", "top_requirements": "Cosmetics, Retail Sales"},
]

RERANK_SYSTEM = """You are a job-candidate matching expert.
You will receive a candidate profile and a list of candidate jobs.
Evaluate how well the candidate matches each job based on skills, experience, and role type.
Return ONLY valid JSON matching:
{
  "matches": [
    {
      "job_id": 1,
      "score": 90,
      "reasons": ["Matches Python and FastAPI skills", "Good entry-level fit"]
    }
  ]
}
Be realistic: if a job is totally unrelated (e.g. Postal Manager for a CS student), give a low score (0-20) and state why in reasons."""

payload = {"candidate": candidate, "jobs": jobs}

print("Testing Groq reranking call directly...")
resp = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": RERANK_SYSTEM},
        {"role": "user", "content": json.dumps(payload)},
    ],
    response_format={"type": "json_object"},
    max_tokens=1000,
    temperature=0.2,
)

print("RAW GROQ RESPONSE:")
print(resp.choices[0].message.content)
