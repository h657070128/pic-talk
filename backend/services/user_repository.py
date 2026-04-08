from typing import Optional
from db.database import SessionLocal
from db.user import User


class UserRepository:

    def create_user(self, email: str, password_hash: str, nickname: Optional[str] = None) -> User:
        """Create a new user and return the User object."""
        db = SessionLocal()
        try:
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
        """Find a user by email address."""
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

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields (nickname, avatar_url, etc.)."""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()
