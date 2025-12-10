from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class Event(models.Model):
    """
    Event model with invited M2M to control access to private events.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(User, related_name='organized_events', on_delete=models.CASCADE)
    location = models.CharField(max_length=255, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_public = models.BooleanField(default=True)
    invited = models.ManyToManyField(User, related_name='invited_events', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time', 'title']

    def __str__(self):
        return f"{self.title} ({self.start_time:%Y-%m-%d %H:%M})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_time <= self.start_time:
            raise ValidationError("end_time must be after start_time")

class RSVP(models.Model):
    """
    RSVP model representing a user's RSVP status for an event.
    Unique constraint prevents multiple RSVPs by same user for same event.
    """
    STATUS_GOING = 'Going'
    STATUS_MAYBE = 'Maybe'
    STATUS_NOT_GOING = 'Not Going'

    STATUS_CHOICES = [
        (STATUS_GOING, 'Going'),
        (STATUS_MAYBE, 'Maybe'),
        (STATUS_NOT_GOING, 'Not Going'),
    ]

    event = models.ForeignKey(Event, related_name='rsvps', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='rsvps', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-updated_at']

    def __str__(self):
        return f"RSVP: {self.user} -> {self.event} ({self.status})"

class Review(models.Model):
    event = models.ForeignKey(Event, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review: {self.user} -> {self.event} ({self.rating})"
