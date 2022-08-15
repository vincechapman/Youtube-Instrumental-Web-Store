from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/fetchvideos', methods=['GET', 'POST'])
@login_required
def update_database():

    if current_user.username.lower() not in ('admin', 'eventbridge'):
        flash("You are not authorised to access that page.")
        return redirect(url_for('home'))

    if request.method == 'POST' or current_user.username.lower() == 'eventbridge':

        import os
        import redis
        from rq import Queue

        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        conn = redis.from_url(redis_url)
        q = Queue(connection=conn)

        from .. google_api.youtube import get_videos, get_audio_links, make_changes_live
        from .. google_api.drive import get_folder_ids

        jobs = q.enqueue_many(
        [
            Queue.prepare_data(get_videos, job_id='GET VIDEOS'),
            Queue.prepare_data(get_audio_links, job_id='GET AUDIO LINKS'),
            Queue.prepare_data(get_folder_ids, job_id='GET FOLDER IDS'),
            Queue.prepare_data(make_changes_live, job_id='MAKE CHANGES LIVE')
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
