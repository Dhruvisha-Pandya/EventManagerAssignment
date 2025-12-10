# accounts/signals.py
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile when a new User is created.
    Also save the profile when user is saved (ensures profile exists).
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # ensure profile exists
        UserProfile.objects.get_or_create(user=instance)
