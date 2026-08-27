import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
}

# Check RemoteOK tag-filtered endpoints
print("=== REMOTEOK - /remote-dev-jobs (tag filter) ===")
r = requests.get("https://remoteok.com/api?tag=dev", headers=HEADERS, timeout=30)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    jobs = [item for item in data if isinstance(item, dict) and item.get("position")]
    print(f"Jobs returned: {len(jobs)}")
    for j in jobs[:5]:
        print(f"  {j.get('position')} @ {j.get('company')} | tags: {j.get('tags')}")

print()
print("=== REMOTEOK - /api?tag=python ===")
r = requests.get("https://remoteok.com/api?tag=python", headers=HEADERS, timeout=30)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    jobs = [item for item in data if isinstance(item, dict) and item.get("position")]
    print(f"Jobs returned: {len(jobs)}")
    for j in jobs[:5]:
        print(f"  {j.get('position')} @ {j.get('company')} | tags: {j.get('tags')}")

print()
print("=== REMOTEOK - /api?tag=software-dev ===")
r = requests.get("https://remoteok.com/api?tag=software-dev", headers=HEADERS, timeout=30)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    jobs = [item for item in data if isinstance(item, dict) and item.get("position")]
    print(f"Jobs returned: {len(jobs)}")
    for j in jobs[:5]:
        print(f"  {j.get('position')} @ {j.get('company')} | tags: {j.get('tags')}")

print()
print("=== WWR - Programming jobs RSS ===")
r = requests.get("https://weworkremotely.com/remote-jobs.rss", headers=HEADERS, timeout=30)
print(f"WWR RSS Status: {r.status_code} | Length: {len(r.text)}")
from bs4 import BeautifulSoup
soup = BeautifulSoup(r.text, "xml")
items = soup.find_all("item")[:5]
for item in items:
    print(f"  {item.find('title').get_text()[:80] if item.find('title') else '?'}")

print()
print("=== WWR - Programming category page ===")
r = requests.get("https://weworkremotely.com/categories/remote-programming-jobs", headers=HEADERS, timeout=30)
print(f"Status: {r.status_code}")
soup = BeautifulSoup(r.text, "html.parser")
titles = soup.select("li.feature a .title")
companies = soup.select("li.feature a .company")
print(f"Jobs: {len(titles)}")
for t, c in zip(titles[:5], companies[:5]):
    print(f"  {t.get_text(strip=True)} @ {c.get_text(strip=True)}")
