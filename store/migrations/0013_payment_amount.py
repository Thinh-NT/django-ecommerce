# Generated by Django 3.2.4 on 2021-06-16 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_auto_20210616_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='amount',
            field=models.FloatField(default=12),
            preserve_default=False,
        ),
    ]