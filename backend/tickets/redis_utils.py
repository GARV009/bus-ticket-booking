import json
import time
import os
from redis import Redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

HOLD_KEY = "hold:{trip_id}:{seat_id}"  # e.g. hold:1:12

def make_hold_key(trip_id, seat_id):
    return HOLD_KEY.format(trip_id=trip_id, seat_id=seat_id)

def set_hold(trip_id:int, seat_id:int, hold_token:str, client_id:str, ttl_seconds:int):
    key = make_hold_key(trip_id, seat_id)
    payload = {
        "client_id": client_id,
        "hold_token": hold_token,
        "expires_at": int(time.time()) + ttl_seconds
    }
    # NX ensures only set if key not already present
    return redis_client.set(name=key, value=json.dumps(payload), nx=True, ex=ttl_seconds)

def get_hold(trip_id:int, seat_id:int):
    key = make_hold_key(trip_id, seat_id)
    v = redis_client.get(key)
    return json.loads(v) if v else None

def release_hold(trip_id:int, seat_id:int):
    key = make_hold_key(trip_id, seat_id)
    redis_client.delete(key)
