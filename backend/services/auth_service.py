import os
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            password.encode("utf-8"), password_hash.encode("utf-8")
        )

    @staticmethod
    def create_access_token(user_id: int, email: str) -> str:
        """Create a JWT access token."""
        payload = {
            "sub": user_id,
            "email": email,
            "type": "access",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Create a JWT refresh token."""
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": datetime.now(timezone.utc)
            + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_access_token(token: str) -> Optional[dict]:
        """Verify and decode an access token."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "access":
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[dict]:
        """Verify and decode a refresh token."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "refresh":
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
