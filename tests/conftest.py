import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tests.factories import EventFactory, UserFactory

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    return user


@pytest.fixture
def another_user(api_client):
    another_user = UserFactory()
    api_client.force_authenticate(user=another_user)
    return another_user


@pytest.fixture
def event(user):
    return EventFactory(creator=user)
