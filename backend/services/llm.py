import json
import os
import sys
import logging
import httpx
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Fastest ultra-reliable free LLM model on Groq (0.7s response time)
MODEL_NAME = "openai/gpt-oss-20b"
_client = None


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROQ_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing from environment or .env file.")
        http_client = httpx.Client(timeout=30.0)
        _client = Groq(api_key=api_key, timeout=30.0, http_client=http_client)
    return _client


EXTRACTION_SYSTEM = """You are a CV parser. Extract structured information from the CV text.
Return ONLY valid JSON matching this schema:
{
  "skills": [string],
  "years_experience": number,
  "education": string,
  "job_titles": [string],
  "seniority": string,
  "summary": string
}
If a field cannot be determined, use null for numbers and "" for strings and [] for arrays."""

RERANK_SYSTEM = """You are a job-candidate matching expert.
You will receive a candidate profile and a list of candidate jobs (each with job_id, title, company, top_requirements).
Evaluate how well the candidate matches each job based on skills, experience, and role type.
Return ONLY valid JSON matching:
{
  "matches": [
    {
      "job_id": number,
      "score": number (0-100),
      "reasons": [string, string]
    }
  ]
}
Be realistic and specific: if a job is unrelated to the candidate's skills, give a low score (0-30) and state why in reasons. Keep each reason short (max 8 words)."""

GAP_ANALYSIS_SYSTEM = """You are a career coach doing gap analysis.
Given a candidate profile and a job description, identify skill gaps.
Return ONLY valid JSON matching:
{
  "missing_skills": [string],
  "partial_skills": [{"skill": string, "gap": string}],
  "recommendations": [string]
}"""

COVER_LETTER_SYSTEM = """You are a professional cover letter writer.
Given a candidate profile and job details, write a compelling cover letter.
Return ONLY valid JSON matching:
{
  "cover_letter": string,
  "key_points": [string]
}
The cover letter should be 3-4 paragraphs, professional, and tailored."""

ATS_SYSTEM = """You are an Applicant Tracking System (ATS) expert.
Analyze the candidate's CV text against the job title, requirements, and description.
Extract ONLY meaningful technical skills, qualifications, tools, domain expertise, and professional terms (e.g., Python, React, SQL, Machine Learning, Agile).
Do NOT include generic web metadata, URLs, stop words, or filler words (e.g. link, view, real, linkedin, http, com, page, site).

Return ONLY valid JSON matching:
{
  "ats_score": number (0-100),
  "matched_keywords": [string] (real technical/professional skills found in both CV and job),
  "missing_keywords": [string] (important job requirements missing from candidate CV),
  "formatting_issues": [string],
  "recommendations": [string]
}"""

INTERVIEW_SYSTEM = """You are an interview coach.
Given a candidate profile and job details, generate interview preparation materials.
Return ONLY valid JSON matching:
{
  "likely_questions": [{"question": string, "tips": string}],
  "key_talking_points": [string],
  "company_research_tips": [string]
}"""

TAILOR_CV_SYSTEM = """You are an expert resume writer and career strategist.
Given a candidate's structured CV data and a target job description, rewrite and optimize the CV for maximum relevance to that specific job.
Return ONLY valid JSON matching:
{
  "tailored_summary": string (tightened 2-3 sentence summary matching the job's seniority and target title),
  "tailored_skills": [string] (reordered and highlighted skills prioritizing what the job asks for),
  "tailored_experience_bullets": [string] (rewritten/rephrased experience bullet points emphasizing relevant accomplishments for this job),
  "key_adjustments_made": [string] (3-4 bullet points summarizing the strategic changes made)
}"""


def _safe_print(label: str, text: str):
    """Print helper that safely encodes non-ascii characters for Windows console."""
    safe_text = text.encode("ascii", errors="replace").decode("ascii")
    print(f"\n{label}")
    print(safe_text)


def _call_groq_json(system_prompt: str, user_content: str, max_tokens: int = 2500):
    """Helper for single Groq chat completion call returning parsed JSON. No swallowing exceptions."""
    client = get_client()
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
        max_tokens=max_tokens,
        temperature=0.2,
    )
    text = resp.choices[0].message.content.strip()
    return text


def extract_cv_data(raw_text: str) -> dict:
    """Single Groq call to extract structured CV data."""
    raw_json_str = _call_groq_json(EXTRACTION_SYSTEM, raw_text[:5000], max_tokens=1000)
    _safe_print("=================== [GROQ CV EXTRACTION RAW RESPONSE] ===================", raw_json_str)
    return json.loads(raw_json_str)


def rerank_jobs(structured_cv: dict, jobs: list) -> list:
    """Single batched Groq call to score and explain candidate job matches. No silent fallbacks."""
    job_summaries = [
        {
            "job_id": j.id,
            "title": j.title,
            "company": j.company,
            "top_requirements": (j.requirements or "")[:150],
        }
        for j in jobs[:15]
    ]
    payload = {"candidate": structured_cv, "jobs": job_summaries}
    user_payload_str = json.dumps(payload, indent=2)

    _safe_print("=================== [GROQ RERANK REQUEST PAYLOAD] ===================", user_payload_str)

    raw_response_str = _call_groq_json(RERANK_SYSTEM, user_payload_str, max_tokens=2500)

    _safe_print("=================== [GROQ RERANK RAW RESPONSE] ===================", raw_response_str)

    res = json.loads(raw_response_str)
    if isinstance(res, dict):
        if "matches" in res:
            return res["matches"]
        if "results" in res:
            return res["results"]
        if "jobs" in res:
            return res["jobs"]
    if isinstance(res, list):
        return res
    raise ValueError(f"Unexpected Groq rerank response format: {res}")


def analyze_gap(structured_cv: dict, job: dict) -> dict:
    """Single Groq call for CV-Job gap analysis."""
    payload = {"candidate": structured_cv, "job": job}
    raw_str = _call_groq_json(GAP_ANALYSIS_SYSTEM, json.dumps(payload), max_tokens=1000)
    return json.loads(raw_str)


def generate_cover_letter(structured_cv: dict, job: dict) -> dict:
    """Single Groq call to generate a tailored cover letter."""
    payload = {"candidate": structured_cv, "job": job}
    raw_str = _call_groq_json(COVER_LETTER_SYSTEM, json.dumps(payload), max_tokens=1500)
    return json.loads(raw_str)


def check_ats(raw_cv_text: str, job: dict) -> dict:
    """ATS compatibility check via Groq LLM — filters out web boilerplate and extracts real technical skills."""
    return analyze_ats_llm(raw_cv_text, job)


def analyze_ats_llm(raw_cv_text: str, job: dict) -> dict:
    payload = {
        "cv_text": raw_cv_text[:3000],
        "job": {
            "title": job.get("title"),
            "company": job.get("company"),
            "requirements": job.get("requirements"),
            "description": (job.get("description") or "")[:1500],
        },
    }
    raw_str = _call_groq_json(ATS_SYSTEM, json.dumps(payload), max_tokens=1200)
    return json.loads(raw_str)


def generate_interview_prep(structured_cv: dict, job: dict) -> dict:
    """Single Groq call to generate interview prep materials."""
    payload = {"candidate": structured_cv, "job": job}
    raw_str = _call_groq_json(INTERVIEW_SYSTEM, json.dumps(payload), max_tokens=1500)
    return json.loads(raw_str)


def tailor_cv(structured_cv: dict, job: dict) -> dict:
    """Single Groq call to generate job-tailored CV content."""
    payload = {"candidate": structured_cv, "job": job}
    raw_str = _call_groq_json(TAILOR_CV_SYSTEM, json.dumps(payload), max_tokens=2000)
    return json.loads(raw_str)
