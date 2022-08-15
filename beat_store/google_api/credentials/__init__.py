from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/documents']

import os
from dotenv import load_dotenv
load_dotenv()

from cryptography.fernet import Fernet

key = os.environ['SERVICE_ACCOUNT_CREDENTIALS_DECRYPTION']

fernet = Fernet(key)
 
with open('service-encrypted.json', 'rb') as enc_file:
    encrypted = enc_file.read()

decrypted = fernet.decrypt(encrypted)
 
with open('service.json', 'wb') as dec_file:
    dec_file.write(decrypted)

SERVICE_ACCOUNT_FILE = 'service.json'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
