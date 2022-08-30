import json

import coreschema
import requests
# from django.conf.global_settings import DEFAULT_FROM_EMAIL
from django.forms.models import model_to_dict
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema

from the_weather.settings import OPENWEATHERMAP_URL, OPENWEATHERMAP_PARAMS, DEFAULT_FROM_EMAIL
from weather.models import *
from rest_framework.views import APIView
from rest_framework import generics, status
from django.core.mail import send_mail
from .scripts import *


class RegistrationView(generics.GenericAPIView):
    """
    Register new user
    """
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({
                'user': UserSerializer(user, context=self.get_serializer_context()).data,
                'message': 'User created successfully. Go to api/token/ to get your token.',
            })
        else:
            return Response(serializer.errors)


class WeatherView(APIView):
    """
    View all subscribed city weather
    """
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
    """
    post:Subscribe or change your subscription. Parameters:
    period - 3, 6, 12, 24 - how often you receive mail with weather; active - True or False;
    city - can be specified with 'city' - city name, 'id' - city id, 'city'&'country' city and country names.
    If multiple cities fit the specification they will be returned.
    get:View all subscriptions.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def create_or_update_sub(self, city, user, period_data, active, period_options=(3, 6, 12, 24)):
        period = min(period_options, key=lambda x:abs(x-period_data))
        sub, created = Subscription.objects.update_or_create(user=user, city=city,
                                                             defaults={
                                                                 'period': period,
                                                                 'active': active})
        if user.email:
            send_mail(
                'Weather',
                (f'{user.username}, you have subscribed to {city.name} weather:',
                 json.dumps(model_to_dict(sub), indent=4)),
                DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        return sub

    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user).values(
            'user__username', 'city__name', 'city__id', 'period', 'active')
        if not subscriptions:
            return Response('No subscribed cities.')
        return Response(subscriptions)

    def post(self, request):
        period_data = request.data.get('period', 60)
        active = request.data.get('active', True)

        # if user provides city id
        if request.data.get('id', None):
            city = City.objects.get(id=request.data['id'])
            subscription = self.create_or_update_sub(city, request.user, period_data, active)
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
                subscription = self.create_or_update_sub(city_obj, request.user, period_data, active)
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
                subscription = self.create_or_update_sub(city_obj, request.user, period_data, active)
                subscription.save()
                return Response(model_to_dict(subscription), status=status.HTTP_201_CREATED)
        return Response('City not found', status=status.HTTP_404_NOT_FOUND)


class CityView(APIView):
    """
    View all cities, with filters: 'id' - city id; 'city' - city name; 'country' - country name; 'city'&'country'
    """
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
