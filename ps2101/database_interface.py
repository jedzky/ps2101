import sqlite3
import hashlib
import time

# Things to do:
# 1.  Figure out how to create connection & cursor without causing thread
# issues.
# Setting check_same_thread=FALSE can cause issues ALLEGEDLY
class Database:
    def __init__(self, app):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        # Generates the database if it doesn't exists
        with app.open_resource('schema.sql', mode = 'r') as f:
            cursor.executescript(f.read())

    def update_user(self, hash, token):
        connection = sqlite3.connect('database.db')
        cursor = self.connection.cursor()

        sql = "UPDATE users SET token = " + token + "WHERE user_hash = " + hash
        cursor.execute(sql)

        connection.close()

    def exists_user(self, user_id, user_token):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

        data = cursor.fetchone()

        if data is not None:
            cursor.execute('UPDATE users SET token = ? WHERE id = ?', (user_token, user_id,))
        else:
            cursor.execute('INSERT INTO users (id, token, token_timeout, administrator) VALUES (?, ?, ?, ?)', (user_id, user_token, time.time() + (86400 * 30), 1))

        connection.commit()

        connection.close()
        
        if data is not None:
            return True
        else:
            return False

    def user_check_token_exists(self, token, current_time):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE token = ?", (token,))

        data = cursor.fetchone()

        if data is not None and data['token_timeout'] < current_time:
            return True

        return False

    def add_user(self, hash, api_key):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        user = (hash, api_key, "empty", 1)

        sql = 'INSERT INTO users(user_hash, token, administrator) VALUES (?, ?, ?, ?)'

        cursor.execute(sql, user)

        connection.commit()

        connection.close()

    def get_all(self, table):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        sql = 'SELECT * FROM ' + table

        cursor.execute(sql)

        data = cursor.fetchall()

        connection.close()

        if data is not None:
            return data
        
        return False
    
    # Checks if plant exists, and places in if not
    # TODO: CHECK IF PLANTS HAVE CORRECT XYZ CO-ORDS
    # TODO: CHECK IF PLANTS ARE ACTIVE
    def add_plant(self, plant, hash):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        plant = (plant['id'], hash, plant['name'], plant['x'], plant['y'], plant['z'], '1')

        sql_search = 'SELECT * FROM unique_plants WHERE user_hash = \'' + hash + "\' AND farmbot_id = \'" + str(plant[0]) + '\''

        cursor.execute(sql_search)

        data = cursor.fetchone()

        if data is not None:
            connection.close()
            return

        sql_create = "INSERT INTO unique_plants (farmbot_id, user_hash, name, x, y, z, active) VALUES (?, ?, ?, ?, ?, ?, ?)"

        cursor.execute(sql_create, plant)

        connection.commit()

        connection.close()

        return

    def remove_active(self, plants, hash):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        sql = 'UPDATE unique_plants SET active = 0 WHERE user_hash = \'' + str(hash) + '\''

        for plant in plants:
            sql += ' AND farmbot_id != ' + str(plant['id'])

        cursor.execute(sql)

        connection.commit()

        connection.close()

        return

    # Generates a secure hash
    def generate_hash(self, input):
        byte_input = str.encode(input)
        return hashlib.sha224(byte_input).hexdigest()