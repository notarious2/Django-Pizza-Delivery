from django.db import models
from django.contrib.auth.models import AbstractUser


class Customer(models.Model):
    user = models.OneToOneField(
        'User', null=True, blank=True, on_delete=models.CASCADE)
    username = models.CharField(
        max_length=200, null=True, blank=True, unique=True)
    device = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.username if self.username else self.device


class User(AbstractUser):
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ['email',]
