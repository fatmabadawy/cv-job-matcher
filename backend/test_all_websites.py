import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
}

print("=== TESTING ARBEITNOW API ===")
try:
    r = requests.get("https://www.arbeitnow.com/api/job-board-api", headers=HEADERS, timeout=15)
    print("Arbeitnow status:", r.status_code)
    data = r.json().get("data", [])
    print("Arbeitnow count:", len(data))
    for j in data[:3]:
        print(f"  * {j.get('title')} @ {j.get('company_name')} | {j.get('url')}")
except Exception as e:
    print("Arbeitnow error:", e)

print("\n=== TESTING WUZZUF HTML SCRAPER ===")
try:
    url = "https://wuzzuf.net/search/jobs/?q=software&a=hpb"
    r = requests.get(url, headers=HEADERS, timeout=15)
    print("Wuzzuf HTML status:", r.status_code)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        titles = soup.select("h2 a")
        companies = soup.select("div.css-d7j1xi a")
        print(f"Wuzzuf titles found: {len(titles)}")
        for t in titles[:5]:
            href = t.get("href", "")
            if href and not href.startswith("http"):
                href = "https://wuzzuf.net" + href
            print(f"  * {t.get_text(strip=True)} | Link: {href}")
except Exception as e:
    print("Wuzzuf error:", e)
