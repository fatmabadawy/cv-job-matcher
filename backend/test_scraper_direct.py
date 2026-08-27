import requests
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
}

print("=== TESTING REMOTEOK API FETCH (timeout=30s) ===")
start = time.time()
try:
    r = requests.get("https://remoteok.com/api", headers=headers, timeout=30)
    print(f"RemoteOK Status Code: {r.status_code} in {time.time()-start:.2f}s")
    if r.status_code == 200:
        data = r.json()
        print(f"RemoteOK Jobs Found: {len(data)-1 if isinstance(data, list) else 0}")
        if isinstance(data, list) and len(data) > 1:
            print("First Real Job:", data[1].get("position"), "@", data[1].get("company"))
except Exception as e:
    print(f"RemoteOK Fetch Failed: {e}")

print("\n=== TESTING WE WORK REMOTELY FETCH (timeout=30s) ===")
start = time.time()
try:
    r = requests.get("https://weworkremotely.com/categories/remote-programming-jobs", headers=headers, timeout=30)
    print(f"WWR Status Code: {r.status_code} in {time.time()-start:.2f}s")
    if r.status_code == 200:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, "html.parser")
        items = soup.select("section.jobs ul li")
        print(f"WWR Jobs Found: {len(items)}")
        if items:
            title_el = items[0].select_one(".title")
            comp_el = items[0].select_one(".company")
            if title_el and comp_el:
                print("First Real Job:", title_el.get_text(strip=True), "@", comp_el.get_text(strip=True))
except Exception as e:
    print(f"WWR Fetch Failed: {e}")
