from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "location")
    search_fields = ("user__username", "full_name", "location")
