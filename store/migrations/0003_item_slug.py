# Generated by Django 3.2.3 on 2021-06-12 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_auto_20210612_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='slug',
            field=models.SlugField(default='product'),
            preserve_default=False,
        ),
    ]