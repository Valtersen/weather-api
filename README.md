# Weather API
API to get weather information via mail.

## Setup
```$ docker-compose up -d --build```

## Endpoints
apidocs/ - documentation

api/register/ - POST username, password and email to register new user

api/token/ - get JWT token for registered user

api/city/ - get list of available cities, filterable

api/subscription/ - GET list of all subscriptions, POST to create new subscription, parameters:
* period - 3, 6, 12, 24 - how often you receive mail with weather, hours; 
* active - True or False;
* city - can be specified with 'city' - city name, 'id' - city id, 'city'&'country' city and country names

api/weather/ - get weather in subscribed cities


