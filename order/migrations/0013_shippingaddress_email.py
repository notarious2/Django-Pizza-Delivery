# Generated by Django 4.1.3 on 2022-12-22 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0012_shippingaddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='email',
            field=models.EmailField(default='vasya@gmail.com', max_length=254),
            preserve_default=False,
        ),
    ]
