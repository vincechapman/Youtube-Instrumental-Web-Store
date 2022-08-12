import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

if os.getenv('USE_LOCAL_REDIS') == 'True':
    redis_url = 'redis://localhost:6379'
else:
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
