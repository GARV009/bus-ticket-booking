# backend/tickets/consumers.py
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .redis_utils import holds_for_trip

class TripConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.trip_id = int(self.scope['url_route']['kwargs']['trip_id'])
        self.group_name = f"trip_{self.trip_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send initial held seats (so clients see existing holds immediately)
        holds = await sync_to_async(holds_for_trip)(self.trip_id)  # returns dict of keys -> payload
        held_ids = []
        for k in holds.keys():
            try:
                # key format: hold:{trip_id}:{seat_id}
                parts = k.split(":")
                seat_id = int(parts[-1])
                held_ids.append(seat_id)
            except Exception:
                continue

        await self.send_json({"type": "init", "held_seat_ids": held_ids})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        # no client -> server actions required for now
        pass

    async def seat_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "seat_event",
            "event": event["event"],
            "seat_ids": event["seat_ids"],
    }))

