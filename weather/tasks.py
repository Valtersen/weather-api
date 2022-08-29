import json
import os
from datetime import datetime
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import send_mail
import requests



logger = get_task_logger(__name__)


@shared_task
def weather_task():
    from weather.models import User, Subscription
    from weather.scripts import get_weather_dict
    from weather.serializers import WeatherSerializer
    from dotenv import load_dotenv

    load_dotenv()
    OPENWEATHERMAP_KEY = os.environ.get('OPENWEATHERMAP_KEY', '')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', '')
    OPENWEATHERMAP_URL = 'http://api.openweathermap.org/data/2.5/weather'
    OPENWEATHERMAP_PARAMS = {
        'id': None,
        'units': 'metric',
        'appid': OPENWEATHERMAP_KEY
    }

    for user in User.objects.all():

        if user.subscribed.all().count() and user.email:

            subscribed_cities = Subscription.objects.filter(user=user).all()
            for subscribed_city in subscribed_cities:

                if int(datetime.now().strftime("%H")) % subscribed_city.period == 0:

                    OPENWEATHERMAP_PARAMS['id'] = subscribed_city.city.id
                    city_weather = requests.get(OPENWEATHERMAP_URL, params=OPENWEATHERMAP_PARAMS)
                    weather_dict = get_weather_dict(city_weather)
                    serialize = WeatherSerializer(data=weather_dict)

                    if serialize.is_valid():
                        serialize.save()
                        send_mail(
                            'Weather',
                            (f'{user.username}, here is {subscribed_city.city.name} weather:',
                             json.dumps(serialize.data, indent=4)),
                            DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=False,
                        )

                        logger.info(f"sent {subscribed_city.city.name} city weather info to {user.username}, email: {user.email}")
