from logging.handlers import RotatingFileHandler
from db import connection_to_database

import requests
import os
import logging
from datetime import datetime
import dotenv
import json

from mongodb_logger import MongoDbLogger

dotenv.load_dotenv()

# Configuration
TIMEOUT_IN_SECONDS = 5

# Environnement
url = os.environ.get("API_URL")
apps = os.environ.get("APPS").split(',')
api_login = os.environ.get("API_LOGIN")
api_password = os.environ.get("API_PASSWORD")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("logs/script_"+datetime.now().strftime("%Y-%m-%d")+".log", 'a', encoding='utf-8', maxBytes=1000000, backupCount=5)
    ],
)

def create_logs_and_reports_dir():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    if not os.path.exists("reports"):
        os.makedirs("reports")

def log(level, message):
    if(level == 'info'):
        logging.info(message)
        MongoDbLogger().log(level, message)
    else:
        logging.error(message)
        MongoDbLogger().log(level, message)

def mask_token(token):
    return token[:2] + '*' * (len(token) - 4) + token[-2:]

def mask_credentials(credential):
    return '*' * len(credential)

def get_token():
    log('info', f'Get token with credentials : {mask_credentials(api_login)} / {mask_credentials(api_password)}')

    try:
        response = requests.post(
            f'{url}/login',
            headers={
                'login': api_login,
                'password': api_password
            },
            timeout=TIMEOUT_IN_SECONDS
        )

        log('info', f'Token: {mask_token(response.json()["token"])}')

        if response.status_code == 200:
            return response.json()['token']
            log('info', f'Response token: {mask_token(response.json()["token"])}')

        if response.status_code == 401:
            log('error', f'Unauthorized, invalid or missing credentials : {api_login} / {api_password}')
            return

    except requests.exceptions.RequestException as e:
        log('error', f'Error: {e}')

    except Exception as e:
        log('error', f'Error: {e}')

def insert_data_in_database(data_json):
    try:
        connection = connection_to_database()
    except Exception as e:
        log('error', f'Error: {e}')

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO app_status (timestamp, app_name, status, response_time) VALUES (%s, %s, %s, %s)", (datetime.fromtimestamp(data_json['timestamp']), data_json['app'], data_json['status'], data_json['response_time']))
        connection.commit()
        cursor.close()
        connection.close()

        log('info', f'Data saved in database')

    except Exception as e:
        log('error', f'Error: {e}')

def insert_data_in_json_file(data_json, app):
    file_name = "reports/"+datetime.now().strftime("%Y-%m-%d")+"-"+app+".json"


    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(data_json)

    with open(file_name, "w") as f:
        json.dump(data, f, indent=2)

    log('info', f'Data saved in {file_name}')

def main():
    create_logs_and_reports_dir()
    log('info', '===============================================')
    token = get_token()

    if not token:
        log('error', 'Error: Token not found')
        return

    for app in apps:
        log('info', f'Checking {app}')

        try:
            response = requests.get(
                f'{url}/status?app={app}',
                headers={
                    'Authorization': f'Bearer {token}'
                },
                timeout=TIMEOUT_IN_SECONDS
            )
            log('info', f'Response: {response.json()}')
            log('info', f'Token: {mask_token(token)}')

            response.raise_for_status()

            if response.status_code == 200:
                insert_data_in_json_file(response.json(), app)
                insert_data_in_database(response.json())

                log('info', f'Response: {response.json()}')

            if response.status_code == 401:
                log('error', f'Unauthorized, invalid or missing token : {token}')

        except requests.exceptions.RequestException as e:
            log('error', f'Error: {e}')

        except Exception as e:
            log('error', f'Error: {e}')


if __name__ == '__main__':
    main()
