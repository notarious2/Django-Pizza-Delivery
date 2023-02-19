from django.db import models
from django.contrib.auth.models import AbstractUser


class Customer(models.Model):
    user = models.OneToOneField("User", null=True, blank=True, on_delete=models.CASCADE)
    device = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username if self.user else self.device


class User(AbstractUser):
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = [
        "email",
    ]
