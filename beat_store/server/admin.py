from flask import Blueprint, render_template, request

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/fetchvideos', methods=['GET', 'POST'])
def update_database():

    if request.method == 'POST':

        import os
        import redis
        from rq import Queue

        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        conn = redis.from_url(redis_url)
        q = Queue(connection=conn)

        from .. google_api.youtube import get_videos, get_audio_links
        from .. google_api.drive import get_folder_ids

        jobs = q.enqueue_many(
        [
            Queue.prepare_data(get_videos, job_id='GET VIDEOS'),
            Queue.prepare_data(get_audio_links, job_id='GET AUDIO LINKS'),
            Queue.prepare_data(get_folder_ids, job_id='GET FOLDER IDS'),
            # Queue.prepare_data(copy_to_Videos, job_id='copy_to_Videos')
        ]
        )


    from .. db import get_db

    db = get_db()

    cursor = db.cursor()

    data = cursor.execute('SELECT id, title, beat_name, tags, mixdown_folder, stems_folder, link_to_video_audio, thumbnail FROM video').fetchall()

    class video():
        def __init__(self, id, title, beat_name, tags, link_to_mixdowns, link_to_stems, link_to_video_audio, thumbnail):
            self.id = id
            self.title = title
            self.beat_name = beat_name
            self.tags = tags
            self.link_to_mixdowns = link_to_mixdowns
            self.link_to_stems = link_to_stems
            self.link_to_video_audio = link_to_video_audio
            self.thumbnail = thumbnail

    videos = []

    for row in data:
        id, title, beat_name, tags, link_to_mixdowns, link_to_stems, link_to_video_audio, thumbnail = row
        new_video = video(id, title, beat_name, tags, link_to_mixdowns, link_to_stems, link_to_video_audio, thumbnail)
        videos.append(new_video)
    
    return render_template('update_database.html', videos=videos)
