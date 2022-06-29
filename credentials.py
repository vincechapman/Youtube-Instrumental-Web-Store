import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import BEAT_WEBSITE_OAUTH_CREDENTIALS

# If making changes to scope, delete 'token.json'
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/documents']

creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        with open('credentials.json', 'w') as f: # Creates a credentials.json file from the string in the environment variable, BEAT_WEBSITE_OAUTH_CREDENTIALS. This string was obtained from a json file downlaoded from the google developer console.
            f.write(BEAT_WEBSITE_OAUTH_CREDENTIALS)
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0) # IS THIS GOING TO WORK ON A LIVE SERVER?
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())