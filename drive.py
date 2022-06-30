import os.path
import io
import google.auth
import json

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from flask import send_file
from zipfile import ZipFile

from credentials import creds

start_folder_id = '1EPZPIV36JUNKf-azQxcBKSOcM2LB56R-' # Got this directly from the URL of my overall beat folder on GDrive

# Creating a service
drive_service = build('drive', 'v3', credentials=creds)

def return_directory(folder, mode=None):

    if mode == 'folders-only':
        query = f"mimeType = 'application/vnd.google-apps.folder' and parents in '{folder}'"
    elif mode == 'files-only':
        query = f"mimeType != 'application/vnd.google-apps.folder' and parents in '{folder}'"
    else:
        query = f"parents in '{folder}'"

    current_dir = {}

    page_token = None
    while True:

        response = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=page_token
        ).execute()

        for file in response.get('files', []):
            current_dir[file.get('name')] = file.get('id')

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    return current_dir

def fetch_beat_files(beat_name):

    stems, mixdowns = None, None

    try:
        beat_folder_id = return_directory(start_folder_id)[beat_name]
        beat_folder_dir = return_directory(beat_folder_id)

        stems_folder_id = beat_folder_dir['Stems']
        stems = return_directory(stems_folder_id, mode='files-only')
 
        mixdown_folder_id = beat_folder_dir['Mixdown']
        mixdowns = return_directory(mixdown_folder_id, mode='files-only')
    except KeyError:
        print(f"Either there's no folder called '{beat_name}', or there IS a folder called '{beat_name}' but 'Stems' or 'Mixdown' are missing from that folder.")

    return stems, mixdowns

def download_file(file_id, file_path):

    try:

        request = drive_service.files().get_media(fileId=file_id) # The API call details
        file = io.BytesIO() # Don't fully understand what this does
        downloader = MediaIoBaseDownload(file, request) # I believe this is where the API request is executed.

        # Seems the download is carried out in chunks. The following loops goes through each chunk until the entire file has been downloaded.
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Downloading '{file_path}' - {int(status.progress() * 100)}%")

        file.seek(0)
        return send_file(file, as_attachment=True, download_name=file_path)

        # with io.BytesIO() as file: THIS MIGHT BE A BETTER WAY TO CLOSE OPEN AND CLOSE THE BUFFER IF I CAN GET IT WORKING.
        #     downloader = MediaIoBaseDownload(file, request) # I believe this is where the API request is executed.

        #     # Seems the download is carried out in chunks. The following loops goes through each chunk until the entire file has been downloaded.
        #     done = False
        #     while done is False:
        #         status, done = downloader.next_chunk()
        #         print(f"Downloading '{file_path}' - {int(status.progress() * 100)}%")

        #     file.seek(0)
        #     return send_file(file, as_attachment=True, download_name=file_path)

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
        return False # Error

def download_all_files(beat_name, download_order, label):

    zip_stream = io.BytesIO()
    with ZipFile(zip_stream, 'w') as archive:
        for file_name in dict.keys(download_order):
            with archive.open(file_name, 'w') as f:
                try:
                    request = drive_service.files().get_media(fileId=download_order[file_name])  # The API call details
                    file_stream = io.BytesIO()
                    downloader = MediaIoBaseDownload(file_stream, request)

                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print(f"Downloading '{file_name}' - {int(status.progress() * 100)}%")

                    f.write(file_stream.getvalue())

                    file_stream.close()

                except HttpError as error:
                    print(F'An error occurred: {error}')
                    file = None
                    return False # Error

    print('Finished Downloading')
    zip_stream.seek(0)
    return send_file(zip_stream, as_attachment=True, download_name=f"{label} - '{beat_name}'.zip")

if __name__ == '__main__':
    fetch_beat_files('The Abyss')