from django.contrib import admin
from .models import Event, RSVP, Review

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "organizer", "start_time", "end_time", "is_public")
    list_filter = ("is_public", "start_time")
    search_fields = ("title", "description", "location", "organizer__username")

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("event__title", "user__username")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "rating", "created_at")
    search_fields = ("event__title", "user__username", "comment")
