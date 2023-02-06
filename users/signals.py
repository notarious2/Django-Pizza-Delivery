from django.db.models import signals
from django.dispatch import receiver
from .models import Customer


@receiver(signals.post_save, sender=Customer)
def create_customer(sender, instance, created, **kwargs):
    if created:
        print(f"Customer {instance} is created")
