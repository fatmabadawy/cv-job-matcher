import os
import time
import httpx
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=key, timeout=30.0, http_client=httpx.Client(timeout=30.0))

MODEL_NAME = "qwen/qwen3.8-27b"
print(f"Testing Groq API with model: {MODEL_NAME}...")

start = time.time()
res = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": "You are a CV parser. Return ONLY valid JSON matching: {\"skills\": [], \"years_experience\": 0, \"seniority\": \"\"}"},
        {"role": "user", "content": "John Smith, Senior Python Engineer with 7 years of FastAPI and React experience."}
    ],
    response_format={"type": "json_object"}
)
elapsed = time.time() - start

print(f"GROQ {MODEL_NAME} RESPONSE SUCCESSFUL IN {elapsed:.2f}s:")
print(res.choices[0].message.content)
