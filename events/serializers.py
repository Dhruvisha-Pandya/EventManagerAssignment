from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Event, RSVP, Review
from accounts.serializers import UserSerializer

User = get_user_model()

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    invited = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Event
        fields = (
            "id", "title", "description", "organizer", "location",
            "start_time", "end_time", "is_public", "invited",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "organizer")

    def validate(self, attrs):
        start = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start and end and end <= start:
            raise serializers.ValidationError({"end_time": "end_time must be after start_time."})
        return attrs

    def create(self, validated_data):
        invited = validated_data.pop("invited", [])
        request = self.context.get("request", None)
        if request and request.user and not request.user.is_anonymous:
            validated_data["organizer"] = request.user
        event = super().create(validated_data)
        if invited:
            event.invited.set(invited)
        return event

    def update(self, instance, validated_data):
        invited = validated_data.pop("invited", None)
        instance = super().update(instance, validated_data)
        if invited is not None:
            instance.invited.set(invited)
        return instance

class RSVPSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = RSVP
        fields = ("id", "event", "user", "status", "updated_at")
        read_only_fields = ("id", "updated_at")
    
    def validate(self, attrs):
        request = self.context.get("request")
        user = attrs.get("user") or (request.user if request else None)
        event = attrs.get("event") or getattr(self.instance, "event", None)

        if event is None:
            raise serializers.ValidationError({"event": "Event must be provided."})

        if not event.is_public:
            if user != event.organizer and user not in event.invited.all():
                raise serializers.ValidationError({"detail": "You are not invited to this private event."})

        if self.instance is None:
            if RSVP.objects.filter(event=event, user=user).exists():
                raise serializers.ValidationError({"detail": "You already have an RSVP for this event."})
        else:
         
            if self.instance.user != user and request.user != event.organizer:
                raise serializers.ValidationError({"detail": "You cannot modify someone else's RSVP."})

        
        status = attrs.get("status", getattr(self.instance, "status", None))
        if status not in dict(RSVP.STATUS_CHOICES):
            raise serializers.ValidationError({"status": "Invalid RSVP status."})

        return attrs

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ("id", "event", "user", "rating", "comment", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("rating must be between 1 and 5.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        user = attrs.get("user") or (request.user if request else None)
        event = attrs.get("event") or getattr(self.instance, "event", None)

        if event is None:
            raise serializers.ValidationError({"event": "Event must be provided."})

        if self.instance is None:
            if Review.objects.filter(event=event, user=user).exists():
                raise serializers.ValidationError({"detail": "You have already reviewed this event."})
        else:
            
            #  only review owner or event organizer can update
            if self.instance.user != user and request.user != event.organizer:
                raise serializers.ValidationError({"detail": "You cannot modify someone else's review."})
        return attrs
