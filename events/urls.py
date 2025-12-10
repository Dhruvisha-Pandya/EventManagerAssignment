# events/urls.py
from django.urls import path
from .views import (
    EventCreateView, EventListView, EventDetailView,
    EventUpdateView, EventDeleteView,
    CreateRSVPView, UpdateRSVPView,
    CreateReviewView, ListReviewView
)

app_name = "events"

urlpatterns = [
    # Events
    path('', EventListView.as_view(), name='event-list'),              # GET /events/
    path('create/', EventCreateView.as_view(), name='event-create'),   # POST /events/create/
    path('<int:pk>/', EventDetailView.as_view(), name='event-detail'), # GET /events/{id}/
    path('<int:pk>/update/', EventUpdateView.as_view(), name='event-update'), # PUT/PATCH
    path('<int:pk>/delete/', EventDeleteView.as_view(), name='event-delete'), # DELETE

    # RSVP
    path('<int:event_id>/rsvp/', CreateRSVPView.as_view(), name='rsvp-create'),                 # POST
    path('<int:event_id>/rsvp/<int:user_id>/', UpdateRSVPView.as_view(), name='rsvp-update'),   # PATCH

    # Reviews
    path('<int:event_id>/reviews/', ListReviewView.as_view(), name='review-list'),              # GET
    path('<int:event_id>/reviews/create/', CreateReviewView.as_view(), name='review-create'),   # POST
]
