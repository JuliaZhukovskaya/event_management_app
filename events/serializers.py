from rest_framework import serializers

from events.enums import RegisterEnum
from events.models import Attendee, Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "type",
            "capacity",
            "description",
            "start_date",
            "end_date",
            "creator",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["creator", "created_at", "updated_at"]

    def validate(self, data):
        """
        Check that the end_date is later than the start_date.
        """
        if "start_date" in data and "end_date" in data:
            if data["end_date"] <= data["start_date"]:
                raise serializers.ValidationError(
                    "The end date must be later than the start date."
                )

        instance = self.instance
        if instance:
            current_attendees = instance.attendees.count()
            new_capacity = data.get("capacity", instance.capacity)

            if int(new_capacity) < current_attendees:
                raise serializers.ValidationError(
                    f"Cannot reduce capacity below the current number of registered attendees ({current_attendees})."
                )

        return data


class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = ["id", "event", "user"]
        read_only_fields = ["event", "user"]


class EventRegistrationSerializer(serializers.Serializer):
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), write_only=True
    )
    action = serializers.ChoiceField(choices=RegisterEnum)

    def validate(self, data):
        event = data["event_id"]
        if not event.is_future_event():
            raise serializers.ValidationError(
                "This event has already passed. Please, make sure you are registrating or unregistrating for future events"
            )
        return data
