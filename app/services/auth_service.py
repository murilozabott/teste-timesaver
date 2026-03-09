from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from app.ext.database import db
from app.models.user import User, UserRole


class AuthService:
    @staticmethod
    def register(username: str, password: str, role: str = "employee") -> User:
        user_role = UserRole(role)
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=user_role,
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def login(username: str, password: str) -> str:
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            raise InvalidCredentialsError()

        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "exp": datetime.now(timezone.utc)
            + timedelta(hours=current_app.config.get("JWT_EXPIRATION_HOURS", 24)),
        }
        token = jwt.encode(
            payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256"
        )
        return token

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(
                token.strip(),
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            raise TokenError("Token expired")
        except jwt.InvalidTokenError:
            raise TokenError("Invalid token")


class InvalidCredentialsError(Exception):
    def __init__(self):
        self.message = "Invalid username or password"
        super().__init__(self.message)


class TokenError(Exception):
    def __init__(self, message: str = "Invalid token"):
        self.message = message
        super().__init__(self.message)
