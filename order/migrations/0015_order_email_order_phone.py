# Generated by Django 4.1.3 on 2023-01-18 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0014_remove_order_email_remove_order_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.EmailField(blank=True, max_length=70, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]