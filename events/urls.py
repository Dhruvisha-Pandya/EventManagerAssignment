from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, CreateRSVPView, UpdateRSVPView, CreateReviewView, ListReviewView

router = DefaultRouter()
router.register(r'', EventViewSet, basename='event')

app_name = "events"

urlpatterns = [
    path('', include(router.urls)),
    
    # RSVP
    path('<int:event_id>/rsvp/', CreateRSVPView.as_view(), name='rsvp-create'),                 
    path('<int:event_id>/rsvp/<int:user_id>/', UpdateRSVPView.as_view(), name='rsvp-update'),   
    
      # Reviews
    path('<int:event_id>/reviews/', CreateReviewView.as_view(), name='review-create'),          
    path('<int:event_id>/reviews/', ListReviewView.as_view(), name='review-list'),            
]