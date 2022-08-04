from flask import Blueprint, render_template, request

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/fetchvideos', methods=['GET', 'POST'])
def update_database():

    if request.method == 'POST':
        # from . youtube import add_uploads_to_database
        from . import youtube
        # youtube.get_videos()
        # youtube.get_audio_url('1OQxbuPRiWA')
        youtube.get_all_audio_urls()
        # add_uploads_to_database()
  
    from . db import get_db

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
    
    return render_template('update_database.html', videos=videos)