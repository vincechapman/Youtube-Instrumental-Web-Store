web: gunicorn application:application

celery_worker: celery -A beat_store worker --loglevel=INFO
