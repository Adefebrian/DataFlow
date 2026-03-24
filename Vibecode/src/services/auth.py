from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
from pydantic import BaseModel
from src.config import get_settings


class User(BaseModel):
    id: str
    username: str
    email: str
    hashed_password: str
    api_key: str
    created_at: datetime
    is_active: bool = True


class TokenData(BaseModel):
    user_id: str
    exp: datetime


class AuthService:
    def __init__(self):
        self.settings = get_settings()
        self._users: dict[str, User] = {}
        self._api_keys: dict[str, str] = {}

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.hash_password(plain_password) == hashed_password

    def generate_api_key(self) -> str:
        return f"df_{secrets.token_urlsafe(32)}"

    def create_user(self, username: str, email: str, password: str) -> User:
        user_id = secrets.token_urlsafe(16)
        hashed = self.hash_password(password)
        api_key = self.generate_api_key()

        user = User(
            id=user_id,
            username=username,
            email=email,
            hashed_password=hashed,
            api_key=api_key,
            created_at=datetime.utcnow(),
        )
        self._users[user_id] = user
        self._api_keys[api_key] = user_id
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        for user in self._users.values():
            if user.username == username and self.verify_password(
                password, user.hashed_password
            ):
                return user
        return None

    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        user_id = self._api_keys.get(api_key)
        if user_id:
            return self._users.get(user_id)
        return None

    def create_default_admin(self):
        if not self._users:
            self.create_user(
                username="admin", email="admin@dataflow.local", password="admin123"
            )

    def get_all_users(self) -> list[User]:
        return list(self._users.values())


auth_service = AuthService()
auth_service.create_default_admin()


def get_auth() -> AuthService:
    return auth_service
