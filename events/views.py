from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from .models import Event, EventRegistration
from .permissions import IsOrganizerOrReadOnly
from .serializers import (
    EventSerializer,
    EventCreateUpdateSerializer,
    EventDetailSerializer,
    EventRegistrationSerializer,
    AttendeeSerializer
)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().select_related('organizer').prefetch_related('registrations')
    permission_classes = [IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['date', 'created_at', 'title']
    ordering = ['-date']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventSerializer

    @extend_schema(
        summary="List all events",
        description="Get a paginated list of all events. Supports search and ordering.",
        parameters=[
            OpenApiParameter(name='search', description='Search in title, description, location', type=str),
            OpenApiParameter(name='ordering', description='Order by: date, created_at, title', type=str),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new event",
        description="Create a new event. The authenticated user becomes the organizer.",
        request=EventCreateUpdateSerializer,
        responses={
            201: EventSerializer,
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save(organizer=request.user)
        return Response(
            EventSerializer(event).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Get event details",
        description="Retrieve detailed information about a specific event including attendees.",
        responses={
            200: EventDetailSerializer,
            404: OpenApiResponse(description="Event not found"),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update an event",
        description="Update an event. Only the organizer can update.",
        request=EventCreateUpdateSerializer,
        responses={
            200: EventSerializer,
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only organizer can update"),
            404: OpenApiResponse(description="Event not found"),
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update an event",
        description="Partially update an event. Only the organizer can update.",
        request=EventCreateUpdateSerializer,
        responses={
            200: EventSerializer,
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only organizer can update"),
            404: OpenApiResponse(description="Event not found"),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete an event",
        description="Delete an event. Only the organizer can delete.",
        responses={
            204: OpenApiResponse(description="Event deleted successfully"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Only organizer can delete"),
            404: OpenApiResponse(description="Event not found"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Register for an event",
        description="Register the authenticated user for this event",
        request=None,
        responses={
            201: EventRegistrationSerializer,
            400: OpenApiResponse(description="Cannot register (full, already registered, etc.)"),
            401: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Event not found"),
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        event = self.get_object()
        user = request.user

        if event.organizer == user:
            return Response(
                {'error': 'Organizer cannot register for their own event'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if EventRegistration.objects.filter(user=user, event=event).exists():
            return Response(
                {'error': 'You are already registered for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if event.is_full:
            return Response(
                {'error': 'This event has reached maximum capacity'},
                status=status.HTTP_400_BAD_REQUEST
            )

        registration = EventRegistration.objects.create(
            user=user,
            event=event,
            status='confirmed'
        )

        return Response(
            EventRegistrationSerializer(registration).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Unregister from an event",
        description="Unregister the authenticated user from this event",
        request=None,
        responses={
            200: OpenApiResponse(description="Successfully unregistered"),
            400: OpenApiResponse(description="Not registered for this event"),
            401: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Event not found"),
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unregister(self, request, pk=None):
        event = self.get_object()
        user = request.user

        try:
            registration = EventRegistration.objects.get(user=user, event=event)
            registration.delete()
            return Response(
                {'message': 'Successfully unregistered from event'},
                status=status.HTTP_200_OK
            )
        except EventRegistration.DoesNotExist:
            return Response(
                {'error': 'You are not registered for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Get event attendees",
        description="Get list of all confirmed attendees for this event",
        responses={
            200: AttendeeSerializer(many=True),
            404: OpenApiResponse(description="Event not found"),
        }
    )
    @action(detail=True, methods=['get'])
    def attendees(self, request, pk=None):
        event = self.get_object()
        registrations = event.registrations.filter(status='confirmed').select_related('user')
        attendees = [reg.user for reg in registrations]
        serializer = AttendeeSerializer(attendees, many=True)
        return Response(serializer.data)


class EventRegistrationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]
    queryset = EventRegistration.objects.all()

    def get_queryset(self):
        return EventRegistration.objects.filter(
            user=self.request.user
        ).select_related('event', 'user').order_by('-registered_at')

    @extend_schema(
        summary="List user's registrations",
        description="Get all event registrations for the authenticated user",
        responses={
            200: EventRegistrationSerializer(many=True),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get registration details",
        description="Get details of a specific registration",
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Registration ID')
        ],
        responses={
            200: EventRegistrationSerializer,
            401: OpenApiResponse(description="Authentication required"),
            404: OpenApiResponse(description="Registration not found"),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
