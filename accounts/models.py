from django.db import models

# accounts/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        # helpful for admin list display
        return f"{self.user.username} - {self.full_name or 'No name'}"
