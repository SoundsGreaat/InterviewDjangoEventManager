from django.contrib import admin
from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'organizer', 'attendees_count', 'created_at']
    list_filter = ['date', 'created_at', 'organizer']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at', 'attendees_count']
    date_hierarchy = 'date'

    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'date', 'location')
        }),
        ('Organizer', {
            'fields': ('organizer',)
        }),
        ('Capacity', {
            'fields': ('max_attendees', 'attendees_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'registered_at']
    list_filter = ['status', 'registered_at', 'event']
    search_fields = ['user__username', 'user__email', 'event__title']
    readonly_fields = ['registered_at', 'updated_at']
    date_hierarchy = 'registered_at'

    fieldsets = (
        ('Registration Details', {
            'fields': ('user', 'event', 'status')
        }),
        ('Timestamps', {
            'fields': ('registered_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
