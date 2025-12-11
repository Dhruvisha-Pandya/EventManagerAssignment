from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import Event, RSVP, Review
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsEventPublicOrInvited

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location', 'organizer__username']
    ordering_fields = ['start_time', 'created_at']
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]
        else: 
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        
        if self.action == 'list':
            qs = Event.objects.filter(is_public=True)
        else:
            qs = Event.objects.all()
        
        return qs.order_by('-start_time')
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if not instance.is_public:
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication credentials were not provided."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if request.user != instance.organizer and not instance.invited.filter(id=request.user.id).exists():
                return Response(
                    {"detail": "You do not have permission to access this event."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CreateRSVPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        
        if not event.is_public:
            if request.user != event.organizer and not event.invited.filter(id=request.user.id).exists():
                return Response(
                    {"detail": "You are not invited to this private event."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        data = request.data.copy()
        data['event'] = event.id
        
        serializer = RSVPSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateRSVPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, event_id, user_id):
        rsvp = get_object_or_404(RSVP, event_id=event_id, user_id=user_id)
        
        # Check permission: only RSVP owner or event organizer can update
        if request.user != rsvp.user and request.user != rsvp.event.organizer:
            return Response(
                {"detail": "You do not have permission to update this RSVP."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = RSVPSerializer(rsvp, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        
        data = request.data.copy()
        data['event'] = event.id
        
        serializer = ReviewSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListReviewView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        event_id = self.kwargs.get("event_id")
        return Review.objects.filter(event_id=event_id).order_by('-created_at')