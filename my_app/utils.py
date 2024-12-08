# utils.py

from django.core.mail import send_mail
from django.conf import settings

def send_bulk_emails(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # You need to define this in your settings
        recipient_list,
        fail_silently=False,
    )
