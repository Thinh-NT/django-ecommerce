# Generated by Django 3.2.4 on 2021-06-16 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_payment_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='being_delivered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='received',
            field=models.BooleanField(default=False),
        ),
    ]
