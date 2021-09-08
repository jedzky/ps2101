import requests
import json

class Weatherstack:
    def __init__(self, weatherstack_key):
        self.key = weatherstack_key

    def current(self):
        request_string = 'http://api.weatherstack.com/current?access_key=' + self.key + '&query=Curl Curl'

        r = requests.get(request_string)

        if(r.status_code != 200):
            return "error"

        json_data = json.loads(r.content)

        location_data = json_data['location']
        weather_data = json_data['current']

        weather_output = weatherstack_output(
            name = location_data['name'],
            country = location_data['country'],
            region = location_data['region'],
            code = weather_data['weather_code'],
            temp = weather_data['temperature'],
            humidity = weather_data['humidity'],
            cloudcover = weather_data['cloudcover']
            )

        return weather_output

class weatherstack_output:
    name = ''
    country = ''
    region = ''
    code = 0
    temp = 0
    humidity = 0
    cloudcover = 0

    def __init__(self, name, country, region, code, temp, humidity, cloudcover):
        self.name = name
        self.country = country
        self.region = region
        self.code = code
        self.temp = temp
        self.humidity = humidity
        self.cloudcover - cloudcover