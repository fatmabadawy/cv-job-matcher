import os
import time
import httpx
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=key, timeout=15.0, http_client=httpx.Client(timeout=15.0))

models_to_test = ["openai/gpt-oss-20b", "qwen/qwen3.6-27b", "allam-2-7b"]

for m in models_to_test:
    try:
        print(f"Testing {m}...")
        start = time.time()
        res = client.chat.completions.create(
            model=m,
            messages=[
                {"role": "system", "content": "You are a CV parser. Return ONLY valid JSON: {\"skills\": [], \"years_experience\": 0}"},
                {"role": "user", "content": "John Smith, Senior Python Engineer with 7 years experience."}
            ],
            response_format={"type": "json_object"}
        )
        print(f"SUCCESS {m} in {time.time()-start:.2f}s: {res.choices[0].message.content}")
        break
    except Exception as e:
        print(f"FAIL {m}: {e}")
