import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import logging
import re
import time

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

TECH_TITLE_KEYWORDS = {
    "python", "javascript", "typescript", "react", "node", "nodejs",
    "backend", "frontend", "full stack", "fullstack", "full-stack",
    "software", "engineer", "developer", "devops", "sre", "platform",
    "machine learning", "data science", "data engineer", "data analyst",
    "fastapi", "django", "flask", "rails", "java", "golang", "rust",
    "kotlin", "swift", "c++", "c#", "php", "ruby", "scala", "elixir",
    "sql", "postgres", "mongodb", "redis", "kubernetes", "docker",
    "aws", "gcp", "azure", "microservices", "llm", "nlp", "ai engineer",
    "android", "ios", "flutter", "vue", "angular", "svelte", "next.js",
    "embedded", "firmware", "blockchain", "web3", "solidity",
    "cybersecurity", "infosec", "security engineer", "qa engineer",
    "automation engineer", "infrastructure", "cloud engineer",
    "product engineer", "research engineer", "ml engineer", "tech lead",
    "product manager", "scrum master", "solutions architect", "system architect",
}

NON_TECH_BLOCKLIST = {
    "sales", "store", "retail", "baker", "laborer", "courier",
    "cleaner", "trimmer", "accountant", "physician", "nurse",
    "removalist", "technician", "estimator", "surveyor",
    "merchandiser", "practitioner", "fitter", "guard", "officer",
    "assistant manager", "store manager", "post office", "lego",
}


def _clean_html(raw_html: str) -> str:
    """Helper to convert HTML description to clean plain text."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def _is_tech_job(title: str, description: str = "") -> bool:
    """Check if title or description matches tech criteria."""
    t = title.lower()
    d = description.lower()
    has_tech = any(kw in t or kw in d for kw in TECH_TITLE_KEYWORDS)
    has_noise = any(kw in t for kw in NON_TECH_BLOCKLIST)
    return has_tech and not has_noise


def _add_job_safely(db: Session, title: str, company: str, location: str, description: str, requirements: str, link: str) -> bool:
    """Safely adds a job with duplicate check and IntegrityError handling."""
    title = title.strip()
    company = company.strip()
    if not title or not company:
        return False

    exists = db.query(models.Job).filter_by(title=title, company=company).first()
    if exists:
        return False

    job = models.Job(
        title=title,
        company=company,
        location=location or "Remote",
        description=description,
        requirements=requirements,
        link=link,
        embedding_status="pending",
    )
    db.add(job)
    try:
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"[scraper] Error adding job {title} @ {company}: {e}")
        return False


def scrape_linkedin(db: Session, limit_per_keyword: int = 15) -> int:
    """Scrape real live jobs directly from LinkedIn's public job search API."""
    keywords = [
        "software engineer", "fullstack developer", "python engineer",
        "frontend developer", "backend engineer", "data engineer",
        "ai engineer", "devops engineer", "mobile developer"
    ]
    added = 0

    for kw in keywords:
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={requests.utils.quote(kw)}&location=Worldwide"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select("li")

            for item in items[:limit_per_keyword]:
                title_el = item.select_one("h3.base-search-card__title")
                company_el = item.select_one("h4.base-search-card__subtitle")
                location_el = item.select_one("span.job-search-card__location")
                link_el = item.select_one("a.base-card__full-link")

                if not title_el or not company_el:
                    continue

                title = title_el.get_text(strip=True)
                company = company_el.get_text(strip=True)
                location = location_el.get_text(strip=True) if location_el else "Remote / Global"
                link = link_el.get("href", "") if link_el else ""

                if not _is_tech_job(title):
                    continue

                success = _add_job_safely(
                    db=db,
                    title=title,
                    company=company,
                    location=location,
                    description=f"LinkedIn Real Listed Position: {title} at {company} ({location}). View full requirements and apply directly on LinkedIn via original link.",
                    requirements="Software Engineering, LinkedIn Real Posting, " + kw,
                    link=link or f"https://www.linkedin.com/jobs/search/?keywords={title.replace(' ', '%20')}",
                )
                if success:
                    added += 1

            time.sleep(0.2)
        except Exception as e:
            logger.error(f"[scraper] LinkedIn scrape error for '{kw}': {e}")

    return added


def scrape_arbeitnow(db: Session, limit: int = 100) -> int:
    """Scrape real global jobs from Arbeitnow Job Board API."""
    try:
        resp = requests.get("https://www.arbeitnow.com/api/job-board-api", headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json().get("data", [])
    except Exception as e:
        logger.error(f"[scraper] Arbeitnow fetch failed: {e}")
        return 0

    added = 0
    for j in data[:limit]:
        title = (j.get("title") or "").strip()
        company = (j.get("company_name") or "").strip()
        if not title or not company:
            continue

        raw_desc = j.get("description") or f"Role: {title} at {company}"
        description = _clean_html(raw_desc)[:1500]
        tags = j.get("tags") or []
        requirements = ", ".join(tags) if isinstance(tags, list) else str(tags)
        link = j.get("url") or f"https://www.arbeitnow.com/jobs"

        if not _is_tech_job(title, description):
            continue

        success = _add_job_safely(
            db=db,
            title=title,
            company=company,
            location=j.get("location") or "Global / Remote",
            description=description,
            requirements=requirements or "Software Engineering, Global Job",
            link=link,
        )
        if success:
            added += 1

    return added


def scrape_remotive(db: Session, limit: int = 60) -> int:
    """Scrape real software engineering jobs from Remotive API."""
    try:
        resp = requests.get(
            "https://remotive.com/api/remote-jobs?category=software-dev",
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        jobs_data = data.get("jobs", [])
    except Exception as e:
        logger.error(f"[scraper] Remotive fetch failed: {e}")
        return 0

    added = 0
    for j in jobs_data[:limit]:
        title = (j.get("title") or "").strip()
        company = (j.get("company_name") or "").strip()
        if not title or not company:
            continue

        tags = j.get("tags") or []
        requirements = ", ".join(tags) if isinstance(tags, list) else str(tags)
        raw_desc = j.get("description") or f"Remote role: {title} at {company}"
        description = _clean_html(raw_desc)[:1500]
        link = j.get("url") or f"https://remotive.com/remote-jobs/{company.lower()}-{title.lower()}"

        if not _is_tech_job(title, description):
            continue

        success = _add_job_safely(
            db=db,
            title=title,
            company=company,
            location=j.get("candidate_required_location") or "Worldwide Remote",
            description=description,
            requirements=requirements or "Software Development, Remote",
            link=link,
        )
        if success:
            added += 1

    return added


def scrape_weworkremotely(db: Session, limit: int = 80) -> int:
    """Scrape real programming/tech jobs from WeWorkRemotely RSS feed."""
    try:
        resp = requests.get(
            "https://weworkremotely.com/remote-jobs.rss",
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "xml")
    except Exception as e:
        logger.error(f"[scraper] WWR RSS fetch failed: {e}")
        return 0

    added = 0
    items = soup.find_all("item")
    for item in items[:limit]:
        title_tag = item.find("title")
        link_tag = item.find("link")
        desc_tag = item.find("description")

        if not title_tag:
            continue

        raw_title = title_tag.get_text(strip=True)
        parts = raw_title.split(":", 1)
        company = parts[0].strip() if len(parts) == 2 else "Unknown"
        title = parts[1].strip() if len(parts) == 2 else raw_title

        link = link_tag.get_text(strip=True) if link_tag else ""
        description = ""
        if desc_tag:
            description = _clean_html(desc_tag.get_text())[:1500]

        if not _is_tech_job(title, description):
            continue

        if not title or not company or company == "Unknown":
            continue

        success = _add_job_safely(
            db=db,
            title=title,
            company=company,
            location="Remote",
            description=description or f"Remote software development role: {title} at {company}",
            requirements="Software Development, Remote",
            link=link,
        )
        if success:
            added += 1

    return added


def scrape_remoteok(db: Session, limit: int = 50) -> int:
    """Scrape tech jobs from RemoteOK JSON API."""
    try:
        resp = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        jobs_data = [item for item in data if isinstance(item, dict) and item.get("position")]
    except Exception as e:
        logger.error(f"[scraper] RemoteOK fetch failed: {e}")
        return 0

    added = 0
    for j in jobs_data[:limit]:
        title = (j.get("position") or "").strip()
        company = (j.get("company") or "").strip()
        if not title or not company:
            continue

        tags = j.get("tags") or []
        requirements = ", ".join(tags) if isinstance(tags, list) else str(tags)
        raw_desc = j.get("description") or f"Remote tech position: {title} at {company}"
        description = _clean_html(raw_desc)[:1500]

        if not _is_tech_job(title, description):
            continue

        success = _add_job_safely(
            db=db,
            title=title,
            company=company,
            location=j.get("location", "Remote") or "Remote",
            description=description,
            requirements=requirements,
            link=j.get("url", "") or f"https://remoteok.com/remote-jobs/{title.lower().replace(' ', '-')}",
        )
        if success:
            added += 1

    return added


def run_all_scrapers(db: Session) -> dict:
    """Run all scrapers across 5 major job portals: LinkedIn, Arbeitnow, Remotive, WeWorkRemotely, RemoteOK."""
    linkedin_count = scrape_linkedin(db)
    arbeitnow_count = scrape_arbeitnow(db)
    remotive_count = scrape_remotive(db)
    wwr_count = scrape_weworkremotely(db)
    remoteok_count = scrape_remoteok(db)
    
    total = linkedin_count + arbeitnow_count + remotive_count + wwr_count + remoteok_count
    return {
        "linkedin": linkedin_count,
        "arbeitnow": arbeitnow_count,
        "remotive": remotive_count,
        "weworkremotely": wwr_count,
        "remoteok": remoteok_count,
        "total": total,
    }
