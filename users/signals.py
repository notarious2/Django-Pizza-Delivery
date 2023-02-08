from django.db.models import signals
from django.dispatch import receiver
from .models import Customer, User


@receiver(signals.post_save, sender=Customer)
def create_customer(sender, instance, created, **kwargs):
    if created:
        if instance.user != None:
            print(f"Customer {instance} is created")
