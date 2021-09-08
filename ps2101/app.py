"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

#jonathon@maxiem.com
#Farmbot2021

#https://gitops.westernsydney.edu.au/professional-experience/spring-2021/PS2101

from flask import Flask, request, render_template, redirect, session, make_response, url_for, g
from waitress import serve
from apscheduler.schedulers.background import BackgroundScheduler

from database_interface import Database
from farmbot_interface import Farmbot
from plantcv_interface import plantcv_interface
from weatherstack_interface import Weatherstack

import requests
import json
import time
import atexit


PORT = 5000

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

# Grabs keys out of config file
config = open('config.json',)
api_keys = json.load(config)
config.close()

database = Database(app)
farmbot = Farmbot()
weatherstack = Weatherstack(api_keys['weatherstack'])


@app.route('/', methods = ['POST', 'GET'])
def login():

    # Checks if cookie exists
    if(request.cookies.get('token') is not None):
        if(database.user_check_token_exists('token', time.time()) == True):
            return redirect(url_for('dashboard'))

    # Checks if not POST request
    if(request.method != 'POST'):
        return render_template('login.html', data = str(PORT))

    login = request.form

    # Handles if a user post requests with no data
    if('email' not in login or 'password' not in login):
        return "POST: Data Error"

    # JSON for POST request
    site_data = {'user': {'email': login['email'], 'password': login['password']}}

    # Sends POST request
    r = requests.post('https://my.farm.bot/api/tokens', json = site_data)

    # Loads JSON into object
    farmbot_data = json.loads(r.content)

    if(r.status_code != 200 or ('token' not in farmbot_data)):
        return "error"

    # Grabs the Farmbot API key
    user_token = farmbot_data['token']['encoded']

    headers = {'Authorization': 'Bearer ' + user_token}

    user_id = farmbot.user_info(headers)

    user_exists = database.exists_user(user_id, user_token)
    
    response = make_response(redirect(url_for('dashboard')))
    response.set_cookie('token', user_token, max_age=(86400 * 30))

    return response

@app.route('/dashboard', methods = ['GET'])
def dashboard():
    api_key = request.cookies.get('token')
    
    # Handles if no cookie is available
    if(api_key is None):
        return redirect(url_for('login'))
    
    # Generates Authorization Token
    headers = {'Authorization': 'Bearer ' + api_key}
    
    # Requests Farmbot plant's
    data = farmbot.plants(headers)

    if data == "error":
        return "error"

    pin = farmbot.sensor_pin(headers)

    last_reading = farmbot.latest_sensor_reading(headers, pin)

    weather = weatherstack.current()
    
    #return render_template('dashboard.html', data=output)
    return render_template('dashboard.html', **locals())

# DEBUG: Cookie delete endpoint
@app.route('/cookie')
def cookie():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('token')
    return response

# DEBUG: Runs the daily function
@app.route('/update_database')
def update_database():
    daily_run()

# Function that will be called daily
def daily_run():

    users = database.get_all('users')

    for user in users:

        # Generates Authorization Token
        headers = {'Authorization': 'Bearer ' + user[1]}

        plants = farmbot.plants(headers)

        # Check if plants exist in database, if not, add them
        database.remove_active(plants, user[0])

        image_name_list = farmbot.plant_images(headers)

        for plant in plants:
            database.add_plant(plant, user[0])

        for image in image_name_list:
            plantcv_interface.prepare_image(str(image))

        for image in image_name_list:
            plantcv_interface.info_image(str(image))

    print('daily_run\n')

    if users is False:
        return

    # Grab photos from farmbot

    # Run each photo through PlantCV updating database


    return 0

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')

    # Sets up daily scheduler, will run exactly 24 hours after first run
    
    # CODE IS COMMENTED OUT DUE TO THE FACT IF THE PROGRAM CRASHES, THE BACKGROUND TASK
    # MAY NOT CORRECTLY CLOSE, EFFECTIVELY PINGING THE SERVER CONSTANTLY UNTIL PC SHUT DOWN
    # DO NOT DELETE, AS IT WILL BE UTILISED 
    
    #scheduler = BackgroundScheduler()
    #scheduler.add_job(func=daily_run, trigger="interval", seconds=5)
    #scheduler.start()

    # Makes sure the schedular closes when Website closes
    #atexit.register(lambda: scheduler.shutdown())

    serve(app, port=5000)
