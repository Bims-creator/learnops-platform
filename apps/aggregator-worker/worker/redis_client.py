import os

import redis

EVENTS_QUEUE_KEY = "learning-events"

_redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
client = redis.from_url(_redis_url, decode_responses=True)
