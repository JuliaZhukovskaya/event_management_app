import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import authentication, exceptions

from services.auth_service import AuthService


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()

        if not auth_header or auth_header[0].lower() != b"bearer":
            return None  # No token provided or invalid scheme

        if len(auth_header) == 1:
            raise exceptions.AuthenticationFailed(
                "Invalid token header. No credentials provided."
            )
        elif len(auth_header) > 2:
            raise exceptions.AuthenticationFailed(
                "Invalid token header. Token string should not contain spaces."
            )

        token = auth_header[1].decode("utf-8")
        auth_service = AuthService()

        try:
            payload = auth_service.decode_token(token)
            user_id = payload["user_id"]
            user = get_user_model().objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found")
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        return (user, token)
