from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from events.enums import RegisterEnum
from events.filters import EventFilter
from events.models import Event
from events.permissions import IsEventOwner
from events.serializers import EventRegistrationSerializer, EventSerializer
from services.register_service import EventRegistrationService


# Create your views here.
class EventViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_class = EventFilter
    permission_classes = [permissions.IsAuthenticated, IsEventOwner]

    def perform_create(self, serializer):
        # Set the creator to the current user
        serializer.save(creator=self.request.user)

    @action(detail=False, methods=["post"], url_path="registration")
    def register(self, request):
        serializer = EventRegistrationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        event = serializer.validated_data["event_id"]
        action = serializer.validated_data["action"]
        user = request.user

        service = EventRegistrationService(event, user)

        try:
            service.handle_registration(action)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "success"}, status=status.HTTP_200_OK)
