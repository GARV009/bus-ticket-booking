import time
import json
from django.core.management.base import BaseCommand
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from tickets.redis_utils import redis_client, release_hold  # adjust import if needed

HOLD_KEY_PATTERN = "hold:*"

class Command(BaseCommand):
    help = "Watch Redis holds and broadcast release events when TTLs expire (run separately)"

    def handle(self, *args, **options):
        self.stdout.write("Expire-watcher started. Scanning hold keys...")
        channel_layer = get_channel_layer()
        try:
            while True:
                keys = redis_client.keys(HOLD_KEY_PATTERN)
                now = int(time.time())
                for k in keys:
                    try:
                        v = redis_client.get(k)
                        if not v:
                            continue
                        payload = json.loads(v)
                        expires_at = int(payload.get("expires_at", 0))
                        if expires_at and expires_at < now:
                            # Parse trip_id and seat_id from key: hold:{trip}:{seat}
                            parts = k.split(":")
                            if len(parts) >= 3:
                                trip_id = int(parts[1])
                                seat_id = int(parts[2])

                                # Remove expired hold
                                release_hold(trip_id, seat_id)

                                # ✅ Broadcast "released" in the same format as Hold/Purchase
                                async_to_sync(channel_layer.group_send)(
                                    f"trip_{trip_id}",
                                    {
                                        "type": "seat_event",
                                        "status": "released",
                                        "seat_ids": [seat_id],
                                    }
                                )
                                self.stdout.write(
                                    self.style.SUCCESS(f"Released seat {seat_id} on trip {trip_id}")
                                )
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Error handling key {k}: {e}"))
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("Expire-watcher stopped by user.")
