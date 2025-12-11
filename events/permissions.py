from rest_framework import permissions

class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only the organizer can perform write operations
        return obj.organizer == request.user

class IsEventPublicOrInvited(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # If not authenticated, only public events
        if not request.user.is_authenticated:
            return obj.is_public
        
        # If event is public, allow
        if obj.is_public:
            return True
        # Organizer can always see
        if request.user == obj.organizer:
            return True
        # Invited users can see private event
        return obj.invited.filter(id=request.user.id).exists()