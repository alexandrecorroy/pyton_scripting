from logging.handlers import RotatingFileHandler
from db import connection_to_database

import requests
import os
import logging
from datetime import datetime
import dotenv
import json

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

def mask_token(token):
    return token[:2] + '*' * (len(token) - 4) + token[-2:]

def mask_credentials(credential):
    return '*' * len(credential)

def get_token():
    logging.info(f'Get token with credentials : {mask_credentials(api_login)} / {mask_credentials(api_password)}')

    try:
        response = requests.post(
            f'{url}/login',
            headers={
                'login': api_login,
                'password': api_password
            },
            timeout=TIMEOUT_IN_SECONDS
        )

        logging.info(f'Status code: {response.status_code}')

        response.raise_for_status()

        if response.status_code == 200:
            return response.json()['token']
            logging.info(f'Response token : {mask_token(response.json()["token"])}')

        if response.status_code == 401:
            logging.error(f'Unauthorized, invalid or missing credentials : {api_login} / {api_password}')

    except requests.exceptions.RequestException as e:
        logging.error(f'Error: {e}')

    except Exception as e:
        logging.error(f'Error: {e}')

def insert_data_in_database(data_json):
    try:
        connection = connection_to_database()
    except Exception as e:
        logging.error(f'Error: {e}')

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO app_status (timestamp, app_name, status, response_time) VALUES (%s, %s, %s, %s)", (datetime.fromtimestamp(data_json['timestamp']), data_json['app'], data_json['status'], data_json['response_time']))
        connection.commit()
        cursor.close()
        connection.close()

    except Exception as e:
        logging.error(f'Error: {e}')

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

    logging.info(f'Data saved in {file_name}')

def main():
    logging.info('===============================================')
    token = get_token()

    for app in apps:
        logging.info(f'Checking {app}')

        try:
            response = requests.get(
                f'{url}/status?app={app}',
                headers={
                    'Authorization': f'Bearer {token}'
                },
                timeout=TIMEOUT_IN_SECONDS
            )

            logging.info(f'Status code: {response.status_code}')
            logging.info(f'Token: {mask_token(token)}')

            response.raise_for_status()

            if response.status_code == 200:
                insert_data_in_json_file(response.json(), app)
                insert_data_in_database(response.json())

                logging.info(f'Response: {response.json()}')

            if response.status_code == 401:
                logging.error(f'Unauthorized, invalid or missing token : {token}')

        except requests.exceptions.RequestException as e:
            logging.error(f'Error: {e}')

        except Exception as e:
            logging.error(f'Error: {e}')


if __name__ == '__main__':
    main()
