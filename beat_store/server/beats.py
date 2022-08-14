from flask import Blueprint, render_template

bp = Blueprint('beats', __name__, url_prefix='/beats')

from beat_store.db import get_db

@bp.route('/')
def beat_library():

    db = get_db()
    cursor = db.cursor()

    data = cursor.execute('SELECT id, title, beat_name, tags, link_to_mixdowns, link_to_stems, link_to_video_audio, thumbnail FROM video').fetchall()

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

    return render_template('beat-library.html', videos=videos)



@bp.route('/<video_id>')
def beat(video_id):

    from .. db import get_db
    db = get_db()
    cursor = db.cursor()

    data = cursor.execute('SELECT * FROM video WHERE id = ?;', (video_id,)).fetchone()

    class video():
        def __init__(self, id, title, published_at, thumbnail, description, beat_name, tags, link_to_mixdowns, link_to_stems, link_to_video_audio):
            self.id = id
            self.title = title
            self.published_at = published_at
            self.thumbnail = thumbnail
            self.description = description
            self.beat_name = beat_name
            self.tags = tags
            self.link_to_mixdowns = link_to_mixdowns
            self.link_to_stems = link_to_stems
            self.link_to_video_audio = link_to_video_audio

    id, title, published_at, thumbnail, description, beat_name, tags, link_to_mixdowns, link_to_stems, link_to_video_audio = data

    return render_template('beat.html', video=video(id, title, published_at, thumbnail, description, beat_name, tags, link_to_mixdowns, link_to_stems, link_to_video_audio))
