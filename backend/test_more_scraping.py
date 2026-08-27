import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    "Referer": "https://www.google.com/",
}

print("=== TESTING WUZZUF WITH ENHANCED HEADERS ===")
try:
    r = requests.get("https://wuzzuf.net/api/job/", headers=HEADERS, timeout=10)
    print("Wuzzuf API Status:", r.status_code)
except Exception as e:
    print("Wuzzuf API error:", e)

print("\n=== TESTING ARBEITNOW REAL JOBS API ===")
try:
    r = requests.get("https://www.arbeitnow.com/api/job-board-api", headers=HEADERS, timeout=10)
    print("Arbeitnow Status:", r.status_code)
    if r.status_code == 200:
        data = r.json().get("data", [])
        print(f"Arbeitnow Jobs: {len(data)}")
        for j in data[:3]:
            print(f" - {j.get('title')} @ {j.get('company_name')} | Link: {j.get('url')}")
except Exception as e:
    print("Arbeitnow Error:", e)

print("\n=== TESTING LINKEDIN MULTI-KEYWORD SEARCH ===")
keywords = ["software engineer", "python developer", "fullstack engineer", "frontend developer", "data engineer"]
for kw in keywords:
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={requests.utils.quote(kw)}&location=Worldwide"
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        jobs = soup.select("li")
        print(f"  LinkedIn keyword '{kw}': {len(jobs)} jobs found")
