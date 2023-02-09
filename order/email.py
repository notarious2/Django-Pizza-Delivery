from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


def send_confirmation_email(email, context):
    email_subject = "Thank you for your order"
    email_body = render_to_string("order/order_confirmation_email.txt", context)

    email = EmailMessage(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )

    return email.send(fail_silently=False)
