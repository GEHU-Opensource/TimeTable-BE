from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Room, Teacher, Subject, TeacherSubject, Student, SubjectPreference
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import threading

def send_email_async(subject, template_name, context, recipient_email):
    """
    Sends an email asynchronously using a separate thread.
    """

    def send():
        html_content = render_to_string(template_name, context)  # Render HTML template
        text_content = strip_tags(html_content)  # Remove HTML tags for plain-text email

        email = EmailMultiAlternatives(
            subject,
            text_content,
            None,  # Uses default email sender from settings
            [recipient_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    thread = threading.Thread(target=send)
    thread.start()
