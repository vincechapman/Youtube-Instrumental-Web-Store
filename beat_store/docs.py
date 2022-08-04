# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START docs_quickstart]
from __future__ import print_function

from datetime import datetime

import io

import google.auth
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

from flask import send_file


'''---------------------------
MY MODULES'''

from credentials import creds
from drive import drive_service, download_file
from config import lease_price


LEASE_TEMPLATE_ID = '1Eny9AaVXVbFvAljb2rD47pP6exeuzvPgoeW5gep-0BY'
LEASE_FOLDER_ID = '1iVlkZ_JQXaPvFpQLxYM0267_oym2UkEu'

docs_service = build('docs', 'v1', credentials=creds)

def copy_lease_template(beat_name, artist_name, order_id):
    
    copy_title = f'{artist_name} - {beat_name} - Licence (Non-Exclusive) - {order_id}'
    
    body = {
        'name': copy_title,
        'parents': [LEASE_FOLDER_ID]
    }
    
    drive_response = drive_service.files().copy(fileId=LEASE_TEMPLATE_ID, body=body).execute()
    
    document_copy_id = drive_response.get('id')
    
    return document_copy_id

def create_lease(producers_legal_name, producers_professional_name, artists_legal_name, artists_professional_name, beat_name, youtube_link, composer_legal_name, beat_price, order_id):
    document_id = copy_lease_template(beat_name, artists_professional_name, order_id)
    document = docs_service.documents().batchUpdate(
        documentId = document_id,
        body = {
            "requests": [
                {
                    "replaceAllText": {
                        "containsText": {
                            "matchCase": "False",
                            "text": "[[producers legal name]]" # Text to replace
                        },
                        "replaceText": producers_legal_name # Text to replace it with
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {
                            "matchCase": "False",
                            "text": "[[producers professional name]]" # Text to replace
                        },
                        "replaceText": producers_professional_name # Text to replace it with
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {
                            "matchCase": "False",
                            "text": "[[artists legal name]]" # Text to replace
                        },
                        "replaceText": artists_legal_name # Text to replace it with
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {
                            "matchCase": "False",
                            "text": "[[artists professional name]]" # Text to replace
                        },
                        "replaceText": artists_professional_name # Text to replace it with
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {
                            "matchCase": "False",
                            "text": "[[beat name]]" # Text to replace
                        },
                        "replaceText": beat_name # Text to replace it with
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {
                            "matchCase": "False",
                            "text": "[[youtube_link]]" # Text to replace
                        },
                        "replaceText": youtube_link # Text to replace it with
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {
                            "matchCase": "False",
                            "text": "[[composer legal name]]" # Text to replace
                        },
                        "replaceText": composer_legal_name # Text to replace it with
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {
                            "matchCase": "False",
                            "text": "[[lease price]]" # Text to replace
                        },
                        "replaceText": beat_price # Text to replace it with
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {
                            "matchCase": "False",
                            "text": "[[lease date]]" # Text to replace
                        },
                        "replaceText": str(datetime.now().astimezone().strftime("%d %B %Y, %H:%M (%Z)")) # Text to replace it with
                    }
                },
                {
                    "replaceAllText": {
                        "containsText": {
                            "matchCase": "False",
                            "text": "[[order ID]]" # Text to replace
                        },
                        "replaceText": order_id # Text to replace it with
                    }
                },
            ]
        }
        ).execute()
    return document_id

def export_lease(file_id, file_path):

    try:
        request = drive_service.files().export_media(fileId=file_id, mimeType='application/pdf')
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    file.seek(0)
    return send_file(file, as_attachment=True, download_name=file_path)




if __name__ == '__main__':
    print(export_lease(
        create_lease(
            producers_legal_name='Vincent Chapman-Andrews',
            producers_professional_name='Vince Maina',
            artists_legal_name='John Doe',
            artists_professional_name='Johnny 2 Trappy',
            beat_name='Maida Vale',
            youtube_link='https://www.youtube.com/watch?v=uBXpY1gE4xU&ab_channel=VinceMaina',
            composer_legal_name='Vincent Chapman-Andrews',
            beat_price='£' + lease_price
        )
    ))