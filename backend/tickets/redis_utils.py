# tickets/redis_utils.py
import json
import time
import os
from redis import Redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

HOLD_KEY = "hold:{trip_id}:{seat_id}"  # value: json {client_id, hold_token, expires_at}

def make_hold_key(trip_id, seat_id):
    return HOLD_KEY.format(trip_id=trip_id, seat_id=seat_id)

def set_hold(trip_id: int, seat_id: int, hold_token: str, client_id: str, ttl_seconds: int):
    key = make_hold_key(trip_id, seat_id)
    payload = {
        "client_id": client_id,
        "hold_token": hold_token,
        "expires_at": int(time.time()) + ttl_seconds
    }
    return redis_client.set(name=key, value=json.dumps(payload), nx=True, ex=ttl_seconds)

def get_hold(trip_id: int, seat_id: int):
    key = make_hold_key(trip_id, seat_id)
    v = redis_client.get(key)
    return json.loads(v) if v else None

def release_hold(trip_id: int, seat_id: int, hold_token: str) -> bool:
    """
    Safely release a hold only if the hold_token matches.
    Returns True if released, False otherwise.
    """
    key = make_hold_key(trip_id, seat_id)
    val = redis_client.get(key)
    if not val:
        return False
    
    try:
        payload = json.loads(val)
    except Exception:
        return False
    
    if payload.get("hold_token") == hold_token:
        redis_client.delete(key)
        return True
    
    return False

def holds_for_trip(trip_id: int):
    pattern = make_hold_key(trip_id, "*")
    keys = redis_client.keys(pattern)
    out = {}
    for k in keys:
        v = redis_client.get(k)
        if v:
            try:
                out[k] = json.loads(v)
            except Exception:
                continue
    return out
