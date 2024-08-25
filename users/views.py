import jwt
from django.contrib.auth import logout
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from services.auth_service import AuthService
from services.user_service import UserService
from users.serializers import (LoginSerializer, RefreshSerializer,
                               RegisterSerializer, TokenSerializer)


class AuthenticationViewSet(viewsets.GenericViewSet):
    """
    Authentication viewset that allows users to login, logout, register and refresh tokens.
    """

    serializer_classes = {
        "login": LoginSerializer,
        "refresh": RefreshSerializer,
        "register": RegisterSerializer,
    }

    def get_serializer_class(self):
        serializer_class = self.serializer_classes.get(self.action)
        if not serializer_class:
            raise NotImplementedError(
                f"Serializer for action '{self.action}' is not implemented."
            )
        return serializer_class

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user_service = UserService()
        user = user_service.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )
        return Response(
            {
                "status": "success",
                "message": "User registered successfully",
                "user_id": user.id,
            }
        )

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            user = UserService().validate_user_credentials(
                validated_data["email"], validated_data["password"]
            )
            # Generate tokens and return them
            tokens = AuthService().generate_access_and_refresh_tokens(user.id)
            return Response({"data": tokens}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def refresh(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        try:
            tokens_data = AuthService().refresh_tokens(validated_data["refresh_token"])
            return Response(
                {"status": "success", "data": TokenSerializer(tokens_data).data}
            )
        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Refresh token has expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except jwt.InvalidTokenError:
            return Response(
                {"error": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED
            )

    @action(
        detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def logout(self, request):
        logout(request)
        return Response(
            {"status": "success", "message": "User logged out successfully"}
        )
