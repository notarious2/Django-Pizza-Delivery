from django.db.models import signals
from django.dispatch import receiver
from .models import Order


@receiver(signals.pre_save, sender=Order)
def mark_order_complete(sender, instance, **kwargs):
    """Send email to customer and admin to notify that order is complete"""
    if instance.complete:
        print(f"Order: {instance} has been completed!")
