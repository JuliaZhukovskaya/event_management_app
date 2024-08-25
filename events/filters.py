from datetime import datetime

from django_filters import rest_framework as filters

from events.models import Event


class EventFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name="start_date", lookup_expr="exact")
    end_date = filters.DateFilter(field_name="end_date", lookup_expr="exact")
    type = filters.CharFilter(field_name="type", lookup_expr="icontains")
    is_future = filters.BooleanFilter(method="filter_future_events")
    mine = filters.BooleanFilter(method="filter_my_events")

    class Meta:
        model = Event
        fields = ["start_date", "end_date", "type"]

    def filter_future_events(self, queryset, name, value):
        if value:
            return queryset.filter(start_date__gt=datetime.now())
        return queryset.filter(start_date__lte=datetime.now())

    def filter_my_events(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(creator=user)
        return queryset
