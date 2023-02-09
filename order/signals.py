from django.db.models import signals
from django.dispatch import receiver
from .models import Order, OrderItem
from users.models import Customer
from .email import send_confirmation_email
from django.conf import settings


@receiver(signals.pre_save, sender=Order)
def mark_order_complete(sender, instance, **kwargs):
    """Send email to customer and admin to notify that order is complete"""
    if instance.complete:
        email = instance.email
        trn_id = str(instance.transaction_id)[:6]
        items = OrderItem.objects.filter(order=instance)

        customer_qs = Customer.objects.filter(order=instance)
        if customer_qs.exists():
            customer = customer_qs[0]
            if customer.user:
                if customer.user.first_name or customer.user.last_name:
                    customer_name = (
                        customer.user.first_name + " " + customer.user.last_name
                    )
                else:
                    customer_name = customer.user.username
            else:
                customer_name = "guest"
        context = {
            "customer_name": customer_name,
            "order": instance,
            "order_items": items,
            "trn_id": trn_id,
        }
        # send email only if host data is provided:
        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            send_confirmation_email(email, context)
        else:
            print("Order has been completed (no SMTP credentials provided)")
