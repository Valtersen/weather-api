from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    indexes = [
        models.Index(fields=['country', 'name']),
    ]
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    state = models.CharField(max_length=256, blank=True)
    country = models.CharField(max_length=256)
    lon = models.FloatField()
    lat = models.FloatField()

    def __str__(self):
        return f"id: {self.id}, city: {self.name}, state: {self.state}, country: {self.country}"

    class Meta:
        app_label = 'weather'


class Subscription(models.Model):
    indexes = [models.Index(fields=['user'])]

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='subscribed')
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='user_subscribed')
    period = models.IntegerField(blank=False, verbose_name='period, hours')
    active = models.BooleanField()

    def __str__(self):
        return f"city: {self.city.name}, country: {self.city.country}, user: {self.user.username}"

    class Meta:
        app_label = 'weather'


class Weather(models.Model):
    indexes = [models.Index(fields=['city_id'])]

    city_id = models.ForeignKey(City, on_delete=models.PROTECT, to_field='id', unique=False, db_column='city_id', related_name='city')
    city_name = models.CharField(max_length=256)
    country = models.CharField(max_length=256)
    date_time = models.DateTimeField(auto_now_add=True)
    main = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    temp = models.FloatField()
    feels_like = models.FloatField()
    temp_min = models.FloatField()
    temp_max = models.FloatField()
    pressure = models.FloatField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()

    def __str__(self):
        return f"country: {self.country}, city: {self.city_name}, time: {self.date_time}"

    class Meta:
        app_label = 'weather'

