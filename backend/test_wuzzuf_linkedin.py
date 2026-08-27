import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

print("=== TESTING WUZZUF SCRAPER ===")
try:
    url = "https://wuzzuf.net/search/jobs/?q=software+engineer&a=hpb"
    r = requests.get(url, headers=HEADERS, timeout=15)
    print(f"Wuzzuf Status: {r.status_code}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        # Wuzzuf job cards
        cards = soup.select("div.css-1gxyz74, div.css-p2035e, div[class*='job-card']")
        if not cards:
            cards = soup.select("h2.css-m604qf a")
        print(f"Wuzzuf Jobs Found: {len(cards)}")
        for idx, card in enumerate(cards[:5], 1):
            title_el = card.select_one("h2.css-m604qf a, a.css-o171kl") or card
            company_el = card.select_one("a.css-17s97q8, div.css-d7j1xi a")
            link = title_el.get("href") if title_el else ""
            if link and not link.startswith("http"):
                link = "https://wuzzuf.net" + link
            print(f"  #{idx}: {title_el.get_text(strip=True)} | Link: {link}")
except Exception as e:
    print(f"Wuzzuf Scrape Error: {e}")

print("\n=== TESTING LINKEDIN PUBLIC JOBS SCRAPER ===")
try:
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=software%20engineer&location=Worldwide"
    r = requests.get(url, headers=HEADERS, timeout=15)
    print(f"LinkedIn Status: {r.status_code}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        jobs = soup.select("li")
        print(f"LinkedIn Jobs Found: {len(jobs)}")
        for idx, job in enumerate(jobs[:5], 1):
            title_el = job.select_one("h3.base-search-card__title")
            company_el = job.select_one("h4.base-search-card__subtitle")
            link_el = job.select_one("a.base-card__full-link")
            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else ""
            link = link_el.get("href") if link_el else ""
            print(f"  #{idx}: {title} @ {company} | Link: {link[:60]}...")
except Exception as e:
    print(f"LinkedIn Scrape Error: {e}")
