from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from typing import List, Dict, Any
from .models import Event, EventRegistration


class OrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields


class EventSerializer(serializers.ModelSerializer):
    organizer = OrganizerSerializer(read_only=True)
    attendees_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location',
            'organizer', 'max_attendees', 'attendees_count',
            'is_full', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at', 'attendees_count', 'is_full']

    def validate_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Event date cannot be in the past")
        return value

    def validate_max_attendees(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Maximum attendees must be greater than 0")
        return value


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'max_attendees']

    def validate_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Event date cannot be in the past")
        return value

    def validate_max_attendees(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Maximum attendees must be greater than 0")
        return value


class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class EventRegistrationSerializer(serializers.ModelSerializer):
    user = AttendeeSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = EventRegistration
        fields = ['id', 'user', 'event', 'status', 'registered_at', 'updated_at']
        read_only_fields = ['id', 'user', 'event', 'registered_at', 'updated_at']


class EventRegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = ['event']

    def validate_event(self, value):
        user = self.context['request'].user

        if value.date < timezone.now():
            raise serializers.ValidationError("Cannot register for past events")

        if value.organizer == user:
            raise serializers.ValidationError("Organizer cannot register for their own event")

        if EventRegistration.objects.filter(user=user, event=value).exists():
            raise serializers.ValidationError("You are already registered for this event")

        if value.is_full:
            raise serializers.ValidationError("This event has reached maximum capacity")

        return value


class EventDetailSerializer(serializers.ModelSerializer):
    organizer = OrganizerSerializer(read_only=True)
    attendees_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    attendees = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location',
            'organizer', 'max_attendees', 'attendees_count',
            'is_full', 'attendees', 'is_registered',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields

    @extend_schema_field(AttendeeSerializer(many=True))
    def get_attendees(self, obj: Event) -> List[Dict[str, Any]]:
        registrations = obj.registrations.filter(status='confirmed').select_related('user')
        return AttendeeSerializer([reg.user for reg in registrations], many=True).data

    @extend_schema_field(serializers.BooleanField)
    def get_is_registered(self, obj: Event) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.registrations.filter(user=request.user, status='confirmed').exists()
        return False
