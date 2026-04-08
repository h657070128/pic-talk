from typing import Optional
from db.database import SessionLocal
from db.user import User
from services.auth_service import AuthService


class UserService:
    def create_user(self, email: str, password: str, nickname: Optional[str] = None) -> User:
        """Register a new user."""
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                raise ValueError("Email already registered")

            password_hash = AuthService.hash_password(password)
            user = User(
                email=email,
                password_hash=password_hash,
                nickname=nickname,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Find a user by email."""
        db = SessionLocal()
        try:
            return db.query(User).filter(User.email == email).first()
        finally:
            db.close()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Find a user by ID."""
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()

    def update_profile(
        self,
        user_id: int,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Optional[User]:
        """Update user profile fields."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            if nickname is not None:
                user.nickname = nickname
            if avatar_url is not None:
                user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()
