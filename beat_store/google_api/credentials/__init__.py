from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/documents']

import os
from dotenv import load_dotenv
load_dotenv()

SERVICE_ACCOUNT_ENV_VAR = os.environ['SERVICE_ACCOUNT_ENV_VAR']

with open('service.json', 'w') as f:
    f.write(SERVICE_ACCOUNT_ENV_VAR)

SERVICE_ACCOUNT_FILE = 'service.json'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
