import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from config import JWT_SECRET, JWT_ALGORITHM


def hash_password(password: str) -> str:
    """Hash password using standard bcrypt library with max 72 byte truncation."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    pwd_bytes = password.encode("utf-8")[:72]
    return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))


def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except JWTError:
        return None
