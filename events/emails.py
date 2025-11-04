from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_registration_confirmation_email(user, event):
    subject = f'Registration Confirmed: {event.title}'

    event_date = event.date.strftime('%B %d, %Y at %I:%M %p')

    html_message = render_to_string('emails/registration_confirmation.html', {
        'user': user,
        'event': event,
        'event_date': event_date,
    })

    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_unregistration_email(user, event):
    subject = f'Unregistered from: {event.title}'

    event_date = event.date.strftime('%B %d, %Y at %I:%M %p')

    html_message = render_to_string('emails/unregistration_confirmation.html', {
        'user': user,
        'event': event,
        'event_date': event_date,
    })

    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
