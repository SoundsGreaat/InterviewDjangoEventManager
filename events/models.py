from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Event(models.Model):
    title = models.CharField(max_length=200, help_text="Event title")
    description = models.TextField(help_text="Detailed description of the event")
    date = models.DateTimeField(help_text="Date and time of the event")
    location = models.CharField(max_length=300, help_text="Physical or virtual location")
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        help_text="User who created this event"
    )
    max_attendees = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of attendees (optional)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['organizer']),
        ]

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        if self.date and self.date < timezone.now():
            raise ValidationError("Event date cannot be in the past")

    @property
    def is_full(self):
        if self.max_attendees is None:
            return False
        return self.registrations.filter(status='confirmed').count() >= self.max_attendees

    @property
    def attendees_count(self):
        return self.registrations.filter(status='confirmed').count()


class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('waitlist', 'Waitlist'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_registrations',
        help_text="User registering for the event"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
        help_text="Event being registered for"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed',
        help_text="Registration status"
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'event']
        ordering = ['-registered_at']
        indexes = [
            models.Index(fields=['user', 'event']),
            models.Index(fields=['event', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"

    def clean(self):
        if self.user == self.event.organizer:
            raise ValidationError("Organizer cannot register for their own event")

        if self.event.date < timezone.now():
            raise ValidationError("Cannot register for past events")
