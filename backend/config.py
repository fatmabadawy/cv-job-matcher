import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/jobsdb")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
JWT_SECRET = os.getenv("JWT_SECRET", "changeme-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
MATCH_ALERT_THRESHOLD = float(os.getenv("MATCH_ALERT_THRESHOLD", "70"))
