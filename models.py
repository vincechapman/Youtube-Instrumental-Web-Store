from config import app, db
from flask_sqlalchemy import SQLAlchemy

class Videos(db.Model):
    video_id = db.Column(db.String(20), primary_key=True)
    video_title = db.Column(db.String(101), nullable=False)
    video_publishedAt = db.Column(db.String(50), nullable=False)
    video_thumbnail = db.Column(db.Text, nullable=False)
    video_description = db.Column(db.Text)
    video_beat_name = db.Column(db.String(100))
    video_tags = db.Column(db.Text)
    beat_mixdowns = db.Column(db.Text)
    beat_stems = db.Column(db.Text)
    audio_url = db.Column(db.Text)

    def __repr__(self):
        return f"\nvideo_id = {self.video_id}\nvideo_title = {self.video_title}\nvideo_publishedAt = {self.video_publishedAt}\nvideo_thumbnail = {self.video_thumbnail}\nvideo_description = {self.video_description}"

class Updated_videos(db.Model):
    video_id = db.Column(db.String(20), primary_key=True)
    video_title = db.Column(db.String(101), nullable=False)
    video_publishedAt = db.Column(db.String(50), nullable=False)
    video_thumbnail = db.Column(db.Text, nullable=False)
    video_description = db.Column(db.Text)
    video_beat_name = db.Column(db.String(100))
    video_tags = db.Column(db.Text)
    beat_mixdowns = db.Column(db.Text)
    beat_stems = db.Column(db.Text)
    audio_url = db.Column(db.Text)

    def __repr__(self):
        return f"\nvideo_id = {self.video_id}\nvideo_title = {self.video_title}\nvideo_publishedAt = {self.video_publishedAt}\nvideo_thumbnail = {self.video_thumbnail}\nvideo_description = {self.video_description}"

def clear_database(table_name):

    try:
        num_rows_deleted = db.session.query(table_name).delete()
        db.session.commit()
        print('Table cleared')
    except:
        db.session.rollback()
        print('It did not work')

if __name__ == '__main__':
    db.create_all() # Adds any new models attributes to the database
