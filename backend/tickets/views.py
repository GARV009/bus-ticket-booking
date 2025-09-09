from rest_framework import generics
from .models import Trip
from .serializers import TripSerializer

class TripListView(generics.ListCreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .serializers import HoldRequestSerializer
from .redis_utils import set_hold

HOLD_TTL = int(os.environ.get("HOLD_TTL_SECONDS", 120))  # 2 min default

class HoldSeatsView(APIView):
    def post(self, request):
        serializer = HoldRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trip_id = serializer.validated_data["trip_id"]
        seat_ids = serializer.validated_data["seat_ids"]
        client_id = serializer.validated_data["client_id"]

        hold_token = str(uuid.uuid4())
        success, failed = [], []

        for sid in seat_ids:
            was_set = set_hold(trip_id, sid, hold_token, client_id, HOLD_TTL)
            if was_set:
                success.append(sid)
            else:
                failed.append(sid)

        # Notify via WebSocket
        channel_layer = get_channel_layer()
        if success:
            async_to_sync(channel_layer.group_send)(
                f"trip_{trip_id}",
                {"type":"seat_event", "event":"seat_held", "seat_ids": success}
            )

        return Response({
            "hold_token": hold_token,
            "held": success,
            "failed": failed,
            "ttl": HOLD_TTL
        }, status=status.HTTP_200_OK)
