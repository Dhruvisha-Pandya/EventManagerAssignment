# accounts/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import UserProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = ("id", "username", "email")  # treat as read-only where used

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile. We accept profile_picture uploads (ImageField).
    If you want to allow editing user's email/username here, you can add nested updates.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ("user", "full_name", "bio", "location", "profile_picture")
