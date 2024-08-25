from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Event(models.Model):
    name = models.CharField(max_length=80)
    description = models.TextField(max_length=500)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    type = models.CharField(max_length=80, default="concert")
    capacity = models.IntegerField(default=0)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["updated_at", "created_at"]

    def is_future_event(self):
        return self.start_date > timezone.now()


class Attendee(models.Model):
    event = models.ForeignKey(Event, related_name="attendees", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="events", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("event", "user")
