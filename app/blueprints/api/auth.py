from functools import wraps

from flask import request
from flask_restful import Resource

from app.blueprints.api.schemas import UserLogin, UserRegister
from app.models.user import UserRole
from app.services.auth_service import AuthService, TokenError


def require_role(minimum_role: UserRole):
    """
    Decorator that requires a minimum role level.
    Role hierarchy: EMPLOYEE < ADMIN
    """
    role_hierarchy = {
        UserRole.EMPLOYEE: 1,
        UserRole.ADMIN: 2,
    }

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return {"message": "Missing or invalid authorization header"}, 401

            token = auth_header.split(" ", 1)[1]
            try:
                payload = AuthService.decode_token(token)
            except TokenError as e:
                return {"message": e.message}, 401

            user_role = UserRole(payload["role"])
            if role_hierarchy[user_role] < role_hierarchy[minimum_role]:
                return {"message": "Insufficient permissions"}, 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator


class RegisterResource(Resource):
    def post(self):
        data = UserRegister.model_validate(request.get_json())
        user = AuthService.register(
            username=data.username,
            password=data.password,
            role=data.role,
        )
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role.value,
        }, 201


class LoginResource(Resource):
    def post(self):
        data = UserLogin.model_validate(request.get_json())
        token = AuthService.login(
            username=data.username,
            password=data.password,
        )
        return {"access_token": token}, 200
