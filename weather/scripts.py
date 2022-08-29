from .serializers import *
from datetime import datetime
from the_weather.settings import BASE_DIR


def get_weather_dict(weather_resp):
    now = datetime.now()
    weather = weather_resp.json()
    return {'city_id': weather['id'],
            'country': weather['sys']['country'],
            'city_name': weather['name'],
            'date_time': now.strftime("%d/%m/%Y %H:%M:%S"),
            'main': weather["weather"][0]["main"],
            'description': weather["weather"][0]["description"],
            'temp': weather['main']['temp'],
            'feels_like': weather['main']['feels_like'],
            'temp_min': weather['main']['temp_min'],
            'temp_max': weather['main']['temp_max'],
            'pressure': weather['main']['pressure'],
            'humidity': weather['main']['humidity'],
            'wind_speed': weather['wind']['speed']
            }


def populate_db():
    file_path = BASE_DIR / 'city_list.json'
    file = open(file_path, encoding="utf8")
    cities = json.loads(file.read())
    index = 0
    for city in cities:
        print(index, city['name'], city['coord']['lon'], city['coord']['lat'])
        city_obj = City(
            id=city['id'],
            name=city['name'],
            state=city['state'],
            country=city['country'],
            lon=city['coord']['lon'],
            lat=city['coord']['lat'])
        city_obj.save()
        index += 1