from __future__ import print_function

from googleapiclient.discovery import build
from requests import HTTPError

from models import Updated_videos, Videos, clear_database
from config import YOUTUBE_API_KEY, db, q

from rq import Queue

import pafy_modified
import requests

from drive import return_directory, start_folder_id

youtube_api_key = YOUTUBE_API_KEY # Currently unrestricted - consider restricting. Don't keep this in this file. Look into using environment variables for secret keys.
youtube = build('youtube', 'v3', developerKey=youtube_api_key)

channel_id = 'UCn2iypP7ektcWULuNKGdcSQ'
uploads_id = channel_id[0] + 'U' + channel_id[2:]

def fetch_upload_ids():
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

    video_id_list = fetch_upload_ids()

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
            video_to_add = Updated_videos(
                video_id = video['id'],
                video_title = video['snippet']['title'],
                video_publishedAt = video['snippet']['publishedAt'],
                video_thumbnail = video['snippet']['thumbnails']['medium']['url'],
                video_description = video['snippet']['description'],
                video_beat_name = process_description(video['snippet']['description'], 'Beat name'),
                video_tags = process_description(video['snippet']['description'], 'Tags'),
                )
            db.session.add(video_to_add)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        
def get_audio_url(video_id):
    
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

def get_all_audio_urls():
    for video in Updated_videos.query.all():
        video.audio_url = get_audio_url(video.video_id)
    db.session.commit()


def get_files():

    beat_folder_id = return_directory(start_folder_id)

    for i in dict.keys(beat_folder_id):
        if 'Mixdown' in return_directory(beat_folder_id[i]):
            try:
                video = Updated_videos.query.filter_by(video_beat_name=i).first()
                video.beat_mixdowns = return_directory(beat_folder_id[i])['Mixdown']
                db.session.commit()
            except:
                db.session.rollback()
                print('Error 1: Video not in database. Or other error.')
        if 'Stems' in return_directory(beat_folder_id[i]):
            try:
                video = Updated_videos.query.filter_by(video_beat_name=i).first()
                video.beat_stems = return_directory(beat_folder_id[i])['Stems']
                db.session.commit()
            except:
                db.session.rollback()
                print('Error 2: Video not in database. Or other error.')

def copy_to_Videos():

    db.session.query(Videos).delete()

    for update_row in Updated_videos.query.all():
        live_row = Videos(
            video_id = update_row.video_id,
            video_title = update_row.video_title,
            video_publishedAt = update_row.video_publishedAt,
            video_thumbnail = update_row.video_thumbnail,
            video_description = update_row.video_description,
            video_beat_name = update_row.video_beat_name,
            video_tags = update_row.video_tags,
            beat_mixdowns = update_row.beat_mixdowns,
            beat_stems = update_row.beat_stems,
            audio_url = update_row.audio_url
            )
        db.session.add(live_row)

    db.session.query(Updated_videos).delete()

    db.session.commit()


def add_uploads_to_database():
    jobs = q.enqueue_many(
    [
        Queue.prepare_data(get_videos, job_id='get_videos'),
        Queue.prepare_data(get_all_audio_urls, job_id='get_all_audio_urls'),
        Queue.prepare_data(get_files, job_id='get_files'),
        Queue.prepare_data(copy_to_Videos, job_id='copy_to_Videos')
    ]
    )

if __name__ == '__main__':
    add_uploads_to_database()