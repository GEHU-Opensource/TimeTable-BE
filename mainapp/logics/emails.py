import os

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import threading
import requests
from django.conf import settings
from premailer import transform

SLACK_WEBHOOK_URL = settings.SLACK_WEBHOOK_URL


def send_slack_notification(message):
    """
    Sends a notification to Slack via webhook.
    """
    try:
        payload = {"text": message}
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code != 200:
            print(f"Failed to send Slack notification: {response.text}")
    except Exception as e:
        print(f"Slack notification error: {e}")


def send_email_async(subject, template_name, context, recipient_email):
    """
    Sends an email asynchronously using a separate thread.
    """

    def send():
        try:
            html_content = render_to_string(template_name, context)
            html_content = transform(html_content)  # Convert styles to inline CSS
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

        except Exception as e:
            error_message = f"Email sending failed for {recipient_email}. Error: {e}"
            print(error_message)  # Log the error
            send_slack_notification(error_message)  # Notify via Slack

    thread = threading.Thread(target=send)
    thread.start()
