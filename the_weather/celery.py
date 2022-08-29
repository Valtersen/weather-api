import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "the_weather.settings")

app = Celery("the_weather")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
