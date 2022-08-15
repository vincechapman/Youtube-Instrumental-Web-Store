import json

import os
from dotenv import load_dotenv
load_dotenv()

from requests import HTTPError

from googleapiclient.discovery import build
youtube = build('youtube', 'v3', developerKey=os.environ['YOUTUBE_API_KEY'])

channel_id = os.environ['YOUTUBE_CHANNEL_ID']
uploads_id = channel_id[0] + 'U' + channel_id[2:]


import sqlite3

db = sqlite3.connect(
    'instance/flaskr.sqlite',
    detect_types=sqlite3.PARSE_DECLTYPES)


def get_video_ids():
    
    # Produces a list of IDs for each video the channel has uploaded
    keep_looping = True
    page_token = None
    video_id_list = []

    while keep_looping:

        request = youtube.playlistItems().list(
            part="contentDetails",
            maxResults=50, # This is the maximum value
            pageToken=page_token,
            playlistId=uploads_id
            )

        try:
            response = request.execute()
        except HTTPError as e:
            print('Error response status code : {0}, reason : {1}'.format(e.status_code, e.error_details))

        for item in response['items']:
            video_id_list.append(item['contentDetails']['videoId'])

        try:
            page_token = response['nextPageToken']
        except KeyError:
            print('No more pages!')
            keep_looping = False
    
    return video_id_list


def process_description(video_description, search_key):
    
    delimiter = '|'
    temp = None

    for i in video_description.splitlines():
        if search_key + ':' in i:
            temp = i[len(search_key) + 1:].strip()
            temp = [i.strip() for i in temp.split(delimiter)] 
            if search_key == ('Beat name'):
                temp = temp[0]
               
    return str(temp)


def get_videos():

    video_id_list = get_video_ids()

    keep_looping = True
    while keep_looping:

        if len(video_id_list) < 50:
            request = youtube.videos().list(
                    part="snippet,contentDetails",
                    id=video_id_list[0:len(video_id_list)]
                )
            keep_looping = False

        else:
            request = youtube.videos().list(
                    part="snippet,contentDetails",
                    id=video_id_list[0:50]
                )
            video_id_list = video_id_list[50:]

        try:
            response = request.execute()

        except HTTPError as e:
            print('Error response status code : {0}, reason : {1}'.format(e.status_code, e.error_details))

        # This takes those details and adds them to our database.

        for video in response['items']:

            video_id = video['id']
            title = video['snippet']['title']
            published_at = video['snippet']['publishedAt']
            thumbnail = video['snippet']['thumbnails']['medium']['url']
            description = video['snippet']['description']
            beat_name = process_description(video['snippet']['description'], 'Beat name')
            tags = process_description(video['snippet']['description'], 'Tags')

            cursor = db.cursor()

            cursor.execute('DELETE FROM video WHERE id = ?;', (video_id,))

            cursor.execute("""
                INSERT INTO video (id, title, published_at, thumbnail, description, beat_name, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?);""", (video_id, title, published_at, thumbnail, description, beat_name, tags))

            db.commit()


def get_audio_url(video_id):

    from . import pafy_modified
    import requests

    print(f'\nFetching audio for {video_id}...')

    verfied = False

    while not verfied: # Seems like Pafy sometimes produces dead links, this while loop ensures that a valid link is always returned.

        video_object = pafy_modified.new(video_id)
        audio_url = video_object.getbestaudio().url_https
        response = requests.head(audio_url)

        if response.status_code == 200:
            print(f'Status code: {response.status_code} (Link works)')
            verfied = True
        elif response.status_code == 403:
            print(f'Status code: {response.status_code} (Dead link, generate a new one.)')
        else:
            print(f'Status code: {response.status_code} (Other http error.)')
        
    return audio_url


def get_audio_links():

    cursor = db.cursor()

    data = cursor.execute('SELECT id FROM video').fetchall()

    # Formatting the data returned by SQLite
    video_id_list = []
    for row in data:
        video_id_list.append(row[0])

    # Adding/updating link_to_video_audio cells in table
    for id in video_id_list:
        cursor.execute("""
            UPDATE video
            SET link_to_video_audio = ?
            WHERE id = ?;""", (get_audio_url(id), id))
    
    db.commit()
