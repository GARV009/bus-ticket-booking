from rest_framework import generics
from .models import Trip, Seat
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
from .serializers import HoldRequestSerializer, ReleaseRequestSerializer
from .redis_utils import set_hold

HOLD_TTL = int(os.environ.get("HOLD_TTL_SECONDS", 20))  # 2 min default

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
            # Check DB: seat must exist and not be sold
            try:
                seat = Seat.objects.get(id=sid, trip_id=trip_id)
                if seat.is_sold:
                    failed.append(sid)
                    continue
            except Seat.DoesNotExist:
                failed.append(sid)
                continue

            # Try to set hold in Redis
            was_set = set_hold(trip_id, sid, hold_token, client_id, HOLD_TTL)
            if was_set:
                success.append(sid)
            else:
                failed.append(sid)

        # ✅ Notify via WebSocket (use "status" instead of "event")
        if success:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"trip_{trip_id}",
                {"type": "seat_event", "event": "held", "seat_ids": success}
            )

        return Response({
            "hold_token": hold_token,
            "held": success,
            "failed": failed,
            "ttl": HOLD_TTL
        }, status=status.HTTP_200_OK)


from .serializers import PurchaseRequestSerializer
from .purchase import try_purchase

class PurchaseView(APIView):
    def post(self, request):
        serializer = PurchaseRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trip_id = serializer.validated_data["trip_id"]
        seat_ids = serializer.validated_data["seat_ids"]
        hold_token = serializer.validated_data["hold_token"]
        buyer_email = serializer.validated_data["buyer_email"]

        try:
            booking = try_purchase(trip_id, seat_ids, hold_token, buyer_email)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Notify via WebSocket (sold status)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"trip_{trip_id}",
            {"type": "seat_event", "event": "sold", "seat_ids": seat_ids}
        )

        return Response({
            "booking_id": booking.id,
            "status": "success"
        }, status=status.HTTP_200_OK)


class TripDetailView(APIView):
    def get(self, request, trip_id):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)

        seats = trip.seats.all().values(
            "id", "seat_label", "row", "column", "price", "is_sold"
        )
        return Response({
            "id": trip.id,
            "title": trip.title,
            "origin": trip.origin,
            "destination": trip.destination,
            "depart_at": trip.depart_at,
            "arrive_at": trip.arrive_at,
            "seats": list(seats),
        })


from rest_framework.permissions import IsAuthenticated
from .permissions import IsOrganizer
from .serializers import TripCreateSerializer

class TripCreateView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizer]

    def post(self, request):
        serializer = TripCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        trip = serializer.save()
        return Response({"id": trip.id, "title": trip.title}, status=status.HTTP_201_CREATED)

from .redis_utils import release_hold
class ReleaseSeatsView(APIView):
    def post(self, request):
        serializer = ReleaseRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        trip_id = serializer.validated_data["trip_id"]
        seat_ids = serializer.validated_data["seat_ids"]
        hold_token = serializer.validated_data["hold_token"]

        released = []
        for sid in seat_ids:
            if release_hold(trip_id, sid, hold_token):  # only release if token matches
                released.append(sid)

        if released:
            # notify all users via websocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"trip_{trip_id}",
                {"type": "seat_event", "event": "released", "seat_ids": released}
            )

        return Response({"released": released}, status=status.HTTP_200_OK)