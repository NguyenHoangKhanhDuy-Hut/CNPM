import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from core.auth import create_access_token, generate_user_id, hash_password, verify_password
from core.config import settings
from core.database import db_manager
from models.auth import User
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        result = self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        result = self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    def register_user(self, email: str, password: str, name: Optional[str] = None) -> User:
        existing = self.get_user_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        user = User(
            id=generate_user_id(),
            email=email,
            name=name,
            password_hash=hash_password(password),
            role="user",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user or not user.password_hash:
            return None
        if not verify_password(password, user.password_hash):
            return None
        user.last_login = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user

    def issue_app_token(
        self,
        user: User,
    ) -> Tuple[str, datetime, Dict[str, Any]]:
        try:
            expires_minutes = int(getattr(settings, "jwt_expire_minutes", 60))
        except (TypeError, ValueError):
            logger.warning("Invalid JWT_EXPIRE_MINUTES value; fallback to 60 minutes")
            expires_minutes = 60
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

        claims: Dict[str, Any] = {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
        }

        if user.name:
            claims["name"] = user.name
        if user.last_login:
            claims["last_login"] = user.last_login.isoformat()
        token = create_access_token(claims, expires_minutes=expires_minutes)

        return token, expires_at, claims


async def initialize_admin_user():
    if "MGX_IGNORE_INIT_ADMIN" in os.environ:
        logger.info("Ignore initialize admin")
        return

    from services.database import initialize_database

    await initialize_database()

    admin_user_id = getattr(settings, "admin_user_id", "")
    admin_user_email = getattr(settings, "admin_user_email", "")

    if not admin_user_id or not admin_user_email:
        logger.warning("Admin user ID or email not configured, skipping admin initialization")
        return

    with db_manager.session_maker() as db:
        result = db.execute(select(User).where(User.id == admin_user_id))
        user = result.scalar_one_or_none()

        if user:
            if user.role != "admin":
                user.role = "admin"
                user.email = admin_user_email
                db.commit()
                logger.debug(f"Updated user {admin_user_id} to admin role")
        else:
            admin_user = User(
                id=admin_user_id,
                email=admin_user_email,
                role="admin",
                password_hash=hash_password("admin123"),
            )
            db.add(admin_user)
            db.commit()
            logger.debug(f"Created admin user: {admin_user_id} with email: {admin_user_email}")
