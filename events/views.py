# events/views.py
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsEventPublicOrInvited

# Pagination class (can be reused for events and reviews)
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# -------------------------
# Event views
# -------------------------
class EventCreateView(generics.CreateAPIView):
    """
    POST /events/  -> create event (authenticated users only)
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

class EventListView(generics.ListAPIView):
    """
    GET /events/  -> list public events (paginated)
    Optional search via ?search=term (title, description, location)
    """
    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location', 'organizer__username']
    ordering_fields = ['start_time', 'created_at']

    def get_queryset(self):
        # Return only public events in list view
        qs = Event.objects.filter(is_public=True).order_by('-start_time')
        return qs

class EventDetailView(generics.RetrieveAPIView):
    """
    GET /events/{id}/ -> event detail
    Private events restricted to invited users (object permission)
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsEventPublicOrInvited]

    # object-level permission will be checked automatically by DRF

class EventUpdateView(generics.UpdateAPIView):
    """
    PUT /events/{id}/ -> update (only organizer)
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]

    def perform_update(self, serializer):
        # ensure organizer doesn't change on update
        serializer.save(organizer=self.get_object().organizer)

class EventDeleteView(generics.DestroyAPIView):
    """
    DELETE /events/{id}/ -> delete (only organizer)
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]

# -------------------------
# RSVP views
# -------------------------
class CreateRSVPView(APIView):
    """
    POST /events/{event_id}/rsvp/  -> create an RSVP for current user
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)

        data = {
            "event": event.id,
            # RSVPSerializer uses HiddenField(CurrentUserDefault()) for user,
            # but since we're not using a view tied to a serializer with context automatically,
            # pass the user in data as well or pass context below.
            "status": request.data.get("status")
        }

        serializer = RSVPSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            # save with user set by HiddenField (CurrentUserDefault) inside serializer
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateRSVPView(APIView):
    """
    PATCH /events/{event_id}/rsvp/{user_id}/ -> update RSVP (owner or organizer)
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, event_id, user_id):
        rsvp = get_object_or_404(RSVP, event_id=event_id, user_id=user_id)
        # The RSVPSerializer will validate ownership in validate(), but ensure request context
        serializer = RSVPSerializer(rsvp, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------------
# Review views
# -------------------------
class CreateReviewView(APIView):
    """
    POST /events/{event_id}/reviews/ -> create a review (authenticated)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)

        data = {
            "event": event.id,
            "rating": request.data.get("rating"),
            "comment": request.data.get("comment", "")
        }

        serializer = ReviewSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListReviewView(generics.ListAPIView):
    """
    GET /events/{event_id}/reviews/ -> list reviews for an event (paginated)
    """
    serializer_class = ReviewSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        event_id = self.kwargs.get("event_id")
        return Review.objects.filter(event_id=event_id).order_by('-created_at')
