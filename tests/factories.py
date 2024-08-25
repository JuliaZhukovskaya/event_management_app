import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory

from events.models import Attendee, Event


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "defaultpassword")


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    name = factory.Faker("word")
    description = factory.Faker("text")
    start_date = factory.Faker("future_date")
    end_date = factory.Faker("future_date")
    creator = factory.SubFactory(UserFactory)
    capacity = factory.Faker("random_int", min=1, max=20)


class AttendeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attendee

    event = factory.SubFactory(EventFactory)  # Assuming you have an EventFactory
    user = factory.SubFactory(UserFactory)
