# Generated by Django 3.2.3 on 2021-06-13 03:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0007_auto_20210612_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ordered_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.client'),
        ),
    ]
