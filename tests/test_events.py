from datetime import timedelta

import pytest
from django.urls import reverse
from rest_framework import status

from events.models import Event
from tests.factories import AttendeeFactory, EventFactory


@pytest.mark.django_db
class TestEventViewSet:

    def test_list_events(self, api_client, user):
        EventFactory.create_batch(5, creator=user)
        url = reverse("events-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_retrieve_event(self, api_client, event):
        url = reverse("events-detail", args=[event.pk])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == event.pk

    def test_create_event(self, api_client, user):
        url = reverse("events-list")
        data = {
            "name": "New Event",
            "description": "Event Description",
            "start_date": "2024-08-30T10:00:00Z",
            "end_date": "2024-08-30T12:00:00Z",
            "capacity": 40,
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert Event.objects.filter(name="New Event").exists()
        assert Event.objects.get(name="New Event").creator == user

    def test_update_event(self, api_client, event):
        url = reverse("events-detail", args=[event.pk])
        data = {"name": "Updated Event Name"}
        response = api_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert Event.objects.get(pk=event.pk).name == "Updated Event Name"

    def test_delete_event(self, api_client, event):
        url = reverse("events-detail", args=[event.pk])
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Event.objects.filter(pk=event.pk).exists()

    def test_filter_mine_events(self, api_client, user, another_user):
        my_events = EventFactory.create_batch(3, creator=user)
        other_events = EventFactory.create_batch(2, creator=another_user)
        api_client.force_authenticate(user=user)

        url = reverse("events-list") + "?mine=true"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        event_ids = [event["id"] for event in response.data]
        assert all(event.id in event_ids for event in my_events)
        assert all(event.id not in event_ids for event in other_events)

    def test_register_event_success(self, api_client, user, event):
        url = reverse("events-register")
        data = {"event_id": event.pk, "action": "register"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"

    def test_unregister_event_success(self, api_client, user, event):
        url = reverse("events-register")
        data = {"event_id": event.pk, "action": "register"}
        api_client.post(url, data, format="json")

        data["action"] = "unregister"
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "success"

    def test_register_event_invalid_action(self, api_client, user, event):
        url = reverse("events-register")
        data = {"event_id": event.pk, "action": "invalid_action"}
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "action" in response.data
        assert '"invalid_action" is not a valid choice.' in response.data["action"][0]

    def test_register_event_failure(self, api_client, user):
        url = reverse("events-register")
        data = {"event_id": 9999, "action": "register"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "event_id" in response.data
        assert "does not exist" in response.data["event_id"][0]

    def test_register_event_full_capacity(self, api_client, user, event):
        AttendeeFactory.create_batch(event.capacity, event=event)

        url = reverse("events-register")
        data = {"event_id": event.pk, "action": "register"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["error"]
            == "Error occurred while registering for the event. Event is already at full capacity."
        )

    def test_update_event_reduce_capacity_below_attendees(
        self, api_client, user, event
    ):
        # Assume event capacity is 10 and 8 attendees are already registered
        event.capacity = 10
        event.save()

        AttendeeFactory.create_batch(8, event=event)

        url = reverse("events-detail", kwargs={"pk": event.pk})
        data = {
            "name": event.name,
            "description": event.description,
            "start_date": event.start_date.isoformat(),
            "end_date": (
                event.start_date + timedelta(days=1)
            ).isoformat(),  # Ensure end_date is after start_date
            "capacity": 5,  # Attempt to reduce capacity to less than 8
        }

        api_client.force_authenticate(user=user)
        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert (
            response.data["non_field_errors"][0]
            == f"Cannot reduce capacity below the current number of registered attendees (8)."
        )
