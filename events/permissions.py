# events/permissions.py
from rest_framework import permissions


class IsEventOwner(permissions.BasePermission):
    """
    Permission to verify that the user is event owner(creator).
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user
