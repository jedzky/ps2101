import requests
import json
import random
import os
import uuid

class Farmbot:

    def plants(self, headers):
    
        # Requests Farmbot plant's
        r = requests.get('https://my.farm.bot/api/points', headers=headers)

        # Handles if request has failed
        if(r.status_code != 200):
            return "error"

        # Loads Json into objects
        json_data = json.loads(r.content)

        # Creates a list
        col_values = []

        # Fills list with only plants
        for points in json_data:
            if points['pointer_type'] == 'Plant':
                col_values.append({'id': points['id'], 'name': points['name'], 'x': points['x'],'y': points['y'], 'z': points['z']})

        return col_values

    # Unfinished Function
    def plant_images(self, headers):

        r = requests.get('https://my.farm.bot/api/images', headers=headers)

        if(r.status_code != 200):
            return "error"

        json_data = json.loads(r.content)

        i = 0

        list = []

        for image in json_data:
            if(i < 20):
                url = image['attachment_url']

                response = requests.get(url)

                img_name = os.getcwd() + '\\images\\' + str(uuid.uuid4()) + '.jpg'

                list.append(img_name)

                open(str(img_name), 'wb').write(response.content)

            i += 1
        return list

    def sensor_pin(self, headers):
    
        r = requests.get('https://my.farm.bot/api/sensors', headers=headers)

        if(r.status_code != 200):
            return "error"

        json_data = json.loads(r.content)

        for tools in json_data:
            if tools['label'] == 'Soil Sensor':
                return tools['pin']

        return -1

    # Only grabs the latest
    def latest_sensor_reading(self, headers, pin):
    
        r = requests.get('https://my.farm.bot/api/sensor_readings', headers=headers)

        if(r.status_code != 200):
            return "error"

        json_data = json.loads(r.content)

        for readings in json_data:
            if readings['pin'] == pin:
                return (readings['value'])

        return -1

    def user_info(self, headers):
        r = requests.get('https://my.farm.bot/api/users', headers=headers)

        if(r.status_code != 200):
            return "error"

        json_data = json.loads(r.content)

        return json_data[0]['id']