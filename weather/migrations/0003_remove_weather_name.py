# Generated by Django 4.1 on 2022-08-15 14:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0002_weather_subscription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='weather',
            name='name',
        ),
    ]
