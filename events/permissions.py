# events/permissions.py
from rest_framework import permissions

class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Allow safe methods for everyone, but only the organizer may edit/delete.
    """
    def has_object_permission(self, request, view, obj):
        # Safe methods are allowed for any request (object-level read allowed)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only the organizer can perform write operations
        return obj.organizer == request.user

class IsEventPublicOrInvited(permissions.BasePermission):
    """
    Object-level permission to allow access to an Event only if:
    - event.is_public is True OR
    - request.user is the organizer OR
    - request.user is in event.invited
    """
    def has_object_permission(self, request, view, obj):
        # If event is public, allow
        if obj.is_public:
            return True
        # Organizer can always see
        if request.user == obj.organizer:
            return True
        # Invited users can see private event
        # Use `.exists()` only if necessary, but simple membership check is fine
        return request.user in obj.invited.all()
