import os
from datetime import datetime, timedelta

import jwt
from django.contrib.auth.models import User


class AuthService:
    def __init__(self):
        self.key = os.environ.get("JWT_SECRET")
        self.JWT_ACCESS_TTL = int(os.environ.get("JWT_ACCESS_TTL", 60))
        self.JWT_REFRESH_TTL = int(os.environ.get("JWT_REFRESH_TTL", 7))  # In days
        self.JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

    def create_access_token(self, user_id):
        payload = {
            "iss": "backend-api",
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(minutes=self.JWT_ACCESS_TTL),
            "type": "access",
        }
        return jwt.encode(payload, self.key, algorithm=self.JWT_ALGORITHM)

    def create_refresh_token(self, user_id):
        payload = {
            "iss": "backend-api",
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=self.JWT_REFRESH_TTL),
            "type": "refresh",
        }
        return jwt.encode(payload, self.key, algorithm=self.JWT_ALGORITHM)

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.key, algorithms=[self.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")

    def generate_access_and_refresh_tokens(self, user_id):
        access_token = self.create_access_token(user_id)
        refresh_token = self.create_refresh_token(user_id)
        return {"access_token": access_token, "refresh_token": refresh_token}

    def get_user_and_generate_tokens(self, email):
        user = User.objects.filter(email=email).first()
        if user:
            return self.generate_access_and_refresh_tokens(user.id)

    def validate_refresh_token(self, refresh_token):
        payload = self.decode_token(refresh_token)
        if payload["type"] != "refresh":
            raise jwt.InvalidTokenError("Invalid token type")
        return payload["user_id"]

    def refresh_tokens(self, refresh_token):
        user_id = self.validate_refresh_token(refresh_token)
        return self.generate_access_and_refresh_tokens(user_id)
