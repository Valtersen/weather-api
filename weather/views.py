import json
import requests
from django.forms.models import model_to_dict
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from the_weather.settings import OPENWEATHERMAP_URL, OPENWEATHERMAP_PARAMS, BASE_DIR
from weather.models import *
from .serializers import *
from datetime import datetime
from rest_framework.views import APIView
from rest_framework import generics, status


class RegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'message': 'User created successfully. Go to api/token/ to get your token.',
        })


class WeatherView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscribed_cities = Subscription.objects.filter(
            user=request.user).all()
        weather_list = []
        if not subscribed_cities:
            return Response('No subscribed cities.')
        for city in subscribed_cities:
            OPENWEATHERMAP_PARAMS['id'] = city.city.id
            city_weather = requests.get(
                OPENWEATHERMAP_URL,
                params=OPENWEATHERMAP_PARAMS)
            if not city_weather.status_code == 200:
                return Response(city_weather)
            weather_list.append(get_weather_dict(city_weather))
        serialize = WeatherSerializer(data=weather_list, many=True)
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data)
        else:
            return Response(serialize.errors)


class SubscriptionView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user).values(
            'user__username', 'city__name', 'city__id', 'period', 'active')
        if not subscriptions:
            return Response('No subscribed cities.')
        return Response(subscriptions)

    def post(self, request):
        period_data = request.data.get('period', 60)
        active = request.data.get('active', True)

        def create_or_update_sub(city, user, period, active):
            sub, created = Subscription.objects.update_or_create(user=user, city=city,
                                                                 defaults={
                                                                     'period': period,
                                                                     'active': active})
            return sub

        # if user provides city id
        if request.data.get('id', None):
            city = City.objects.get(id=request.data['id'])
            subscription = create_or_update_sub(city, request.user, period_data, active)
            subscription.save()
            return Response(model_to_dict(subscription), status=status.HTTP_201_CREATED)

        # if user provides city name and country
        if request.data.get('city', None) and request.data.get('country', None):
            city = City.objects.filter(
                name=request.data['city'],
                country=request.data['country'])
            if city.count() != 1:
                city_dict = {c.name: model_to_dict(c) for c in city}
                return Response(city_dict)
            else:
                city_obj = city.first()
                subscription = create_or_update_sub(city_obj, request.user, period_data, active)
                subscription.save()
                return Response(model_to_dict(subscription), status=status.HTTP_201_CREATED)

        # if user provides only city name
        if request.data.get('city', None):
            city = City.objects.filter(name=request.data['city'])
            if city.count() != 1:
                return Response(
                    city.values(
                        'id',
                        'name',
                        'state',
                        'country',
                        'lon',
                        'lat').all())
            else:
                city_obj = city.first()
                subscription = create_or_update_sub(city_obj, request.user, period_data, active)
                subscription.save()
                return Response(model_to_dict(subscription), status=status.HTTP_201_CREATED)
        return Response('City not found', status=status.HTTP_404_NOT_FOUND)


class CityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.query_params.get('id', None):
            city = City.objects.filter(
                id=request.query_params['id']).values(
                'id', 'name', 'state', 'country', 'lon', 'lat')
            return Response(city)
        elif request.query_params.get('country', None) and request.query_params.get('city', None):
            city = City.objects.filter(
                name=request.query_params['city'],
                country=request.query_params['country']).values(
                'id',
                'name',
                'state',
                'country',
                'lon',
                'lat').all()
            return Response(city)
        elif request.query_params.get('city', None):
            city = City.objects.filter(
                name=request.query_params['city']).values(
                'id', 'name', 'state', 'country', 'lon', 'lat').all()
            return Response(city)
        elif request.query_params.get('country', None):
            city = City.objects.filter(
                country=request.query_params['country']).values(
                'id', 'name', 'state', 'country', 'lon', 'lat').all()
            return Response(city)
        else:
            city = City.objects.values(
                'id', 'name', 'state', 'country', 'lon', 'lat').all()
            return Response(city)


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