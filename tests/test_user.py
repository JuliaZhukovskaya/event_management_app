import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from services.auth_service import AuthService
from tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestAuthenticationViewSet:

    def test_register_success(self, api_client):
        url = reverse("auth-register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword",
            "password2": "testpassword",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        assert "user_id" in response.data

    def test_register_password_mismatch(self, api_client):
        url = reverse("auth-register")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword",
            "password2": "differentpassword",
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_login_success(self, api_client):
        user = UserFactory(email="test@example.com", password="testpassword")
        url = reverse("auth-login")
        data = {"email": user.email, "password": "testpassword"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data["data"]
        assert "refresh_token" in response.data["data"]

    def test_login_invalid_credentials(self, api_client):
        url = reverse("auth-login")
        data = {"email": "nonexistent@example.com", "password": "wrongpassword"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_refresh_success(self, api_client):
        user = UserFactory()
        tokens = AuthService().generate_access_and_refresh_tokens(user.id)
        url = reverse("auth-refresh")
        data = {"refresh_token": tokens["refresh_token"]}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data["data"]
        assert "refresh_token" in response.data["data"]

    def test_refresh_invalid_token(self, api_client):
        url = reverse("auth-refresh")
        data = {"refresh_token": "invalidtoken"}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["error"] == "Invalid refresh token."

    def test_logout_success(self, api_client):
        user = UserFactory()
        tokens = AuthService().generate_access_and_refresh_tokens(user.id)
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access_token"])
        url = reverse("auth-logout")
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"
        assert response.data["message"] == "User logged out successfully"
