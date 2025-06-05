from logging.handlers import RotatingFileHandler

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
token = os.environ.get("API_TOKEN")
url = os.environ.get("API_URL")
apps = os.environ.get("APPS").split(',')

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
    for app in apps:

        logging.info('===============================================')
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
                logging.info(f'Response: {response.json()}')

            if response.status_code == 401:
                logging.error(f'Unauthorized, invalid or missing token : {token}')

        except requests.exceptions.RequestException as e:
            logging.error(f'Error: {e}')

        except Exception as e:
            logging.error(f'Error: {e}')


if __name__ == '__main__':
    main()
