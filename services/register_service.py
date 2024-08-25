from events.enums import RegisterEnum
from events.models import Attendee


class EventRegistrationService:
    def __init__(self, event, user):
        self.event = event
        self.user = user

    def handle_registration(self, action):
        if action == RegisterEnum.REGISTER:
            self._check_capacity()
            self.register()
        elif action == RegisterEnum.UNREGISTER:
            self.unregister()
        else:
            raise ValueError("Invalid action.")

    def _check_capacity(self):
        if self.event.attendees.count() >= self.event.capacity:
            raise ValueError(
                "Error occurred while registering for the event. Event is already at full capacity."
            )

    def register(self):
        if Attendee.objects.filter(event=self.event, user=self.user).exists():
            raise ValueError(
                "Error registrating for the event. You've already registered for this event"
            )
        Attendee.objects.create(event=self.event, user=self.user)

    def unregister(self):
        try:
            attendee = Attendee.objects.get(event=self.event, user=self.user)
            attendee.delete()
        except Attendee.DoesNotExist:
            raise ValueError(
                "You haven't registered for this event. You need to register first"
            )
