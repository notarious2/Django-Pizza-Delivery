from django.db import models
import uuid
# Create your models here.


class Pizza(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    desc = models.TextField(max_length=500)
    image = models.ImageField(blank=True, upload_to='images')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.name
