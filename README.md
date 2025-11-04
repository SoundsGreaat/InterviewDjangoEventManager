# Event Manager API

Django REST API for managing events with user registration and authentication.

## Features

- Event CRUD operations with capacity management
- Token-based authentication
- Event registration system
- Permission control (organizers only edit their events)
- Interactive API documentation (Swagger/ReDoc)
- Automated email confirmations for event registration/unregistration

## Tech Stack

- Django 5.2.7 + DRF
- PostgreSQL 17
- Docker + Docker Compose
- Token Authentication
- drf-spectacular (OpenAPI)

## Quick Start

### Environment Variables

Create `.env` from `.env.example`

Remove `env_file` section in `docker-compose.yml` so it will use `.env` file.

For a test run, you can leave the contents of the `.env.example` file unchanged, but in this case, email delivery will not work.

### Docker

```bash
git clone https://github.com/SoundsGreaat/InterviewDjangoEventManager
cd InterviewDjangoEventManager
docker-compose up --build
```

- API: http://localhost:8000/api/
- Swagger: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

## API Endpoints

### Authentication

- `POST /api/users/register/` - Register user
- `POST /api/users/login/` - Login and get token
- `GET /api/users/list/` - List all users
- `GET /api/users/list/{id}/` - Get user details

### Events

- `GET /api/events/` - List events (public)
- `POST /api/events/` - Create event (auth)
- `GET /api/events/{id}/` - Get event details
- `PATCH /api/events/{id}/` - Update event (organizer only)
- `DELETE /api/events/{id}/` - Delete event (organizer only)
- `POST /api/events/{id}/register/` - Register for event (auth)
- `POST /api/events/{id}/unregister/` - Unregister from event (auth)
- `GET /api/events/{id}/attendees/` - List attendees

### Registrations

- `GET /api/registrations/` - List user's registrations (auth)
- `GET /api/registrations/{id}/` - Get registration details (auth)

## Project Structure

```
├── events/                                     # Events application
│   ├── migrations/                             # Database migrations for events
│   ├── admin.py                                # Django admin configuration
│   ├── apps.py                                 # App configuration
│   ├── authentication.py                       # Custom authentication schemes for drf-spectacular
│   ├── emails.py                               # Email sending utilities
│   ├── models.py                               # Event and EventRegistration models
│   ├── permissions.py                          # Custom permissions (IsOrganizerOrReadOnly)
│   ├── serializers.py                          # DRF serializers for events
│   ├── urls.py                                 # Event API routes
│   └── views.py                                # Event ViewSets and endpoints
├── InterviewDjangoEventManager/                # Main project configuration
│   ├── settings.py                             # Django settings (DB, REST Framework, drf-spectacular)
│   ├── urls.py                                 # Main URL configuration
│   ├── wsgi.py                                 # WSGI configuration for production
│   └── asgi.py                                 # ASGI configuration
├── templates/                                  # HTML templates
│   └── emails/                                 # Email templates
│       ├── registration_confirmation.html      # Registration email template
│       └── unregistration_confirmation.html    # Unregistration email template
├── users/                                      # Users application
│   ├── serializers.py                          # User serializers (registration, login, detail)
│   ├── urls.py                                 # User API routes
│   └── views.py                                # User views (register, login, UserViewSet)
├── docker-compose.yml                          # Docker Compose configuration (db + web)
├── Dockerfile                                  # Docker image definition
├── entrypoint.sh                               # Container startup script (wait for DB, migrations, collectstatic)
├── manage.py                                   # Django management script
├── requirements.txt                            # Python dependencies
├── .env.example                                # Environment variables template
└── README.md                                   # This file
```
