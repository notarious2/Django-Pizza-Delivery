# Generated by Django 4.1.3 on 2022-12-13 07:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_order_coupon_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='coupon_value',
        ),
    ]