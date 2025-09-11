from rest_framework import serializers
from .models import Trip, Seat

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ('id','seat_label','price','is_sold')

class TripSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)
    class Meta:
        model = Trip
        fields = ('id','title','origin','destination','depart_at','arrive_at','seats')

class HoldRequestSerializer(serializers.Serializer):
    trip_id = serializers.IntegerField()
    seat_ids = serializers.ListField(child=serializers.IntegerField())
    client_id = serializers.CharField(required=False, allow_blank=True)
    hold_token = serializers.CharField(required=False, allow_blank=True)

class PurchaseRequestSerializer(serializers.Serializer):
    trip_id = serializers.IntegerField()
    seat_ids = serializers.ListField(child=serializers.IntegerField())
    hold_token = serializers.CharField()
    buyer_email = serializers.EmailField()

class ReleaseRequestSerializer(serializers.Serializer):
    trip_id = serializers.IntegerField()
    seat_ids = serializers.ListField(child=serializers.IntegerField())
    hold_token = serializers.CharField()


class TripCreateSerializer(serializers.ModelSerializer):
    rows = serializers.IntegerField(write_only=True)
    cols = serializers.IntegerField(write_only=True)
    seat_price = serializers.DecimalField(max_digits=9, decimal_places=2, write_only=True)

    class Meta:
        model = Trip
        fields = [
            "title",
            "origin",
            "destination",
            "depart_at",
            "arrive_at",
            "bus_type",
            "booking_opens_at",
            "booking_closes_at",
            "rows",
            "cols",
            "seat_price",
        ]

    def create(self, validated_data):
        rows = validated_data.pop("rows")
        cols = validated_data.pop("cols")
        seat_price = validated_data.pop("seat_price")
        organizer = self.context["request"].user

        # Create trip
        trip = Trip.objects.create(organizer=organizer, **validated_data)

        # Generate seats
        for r in range(1, rows + 1):
            for c in range(1, cols + 1):
                label = f"{r}{chr(64+c)}"  # e.g. 1A, 1B
                Seat.objects.create(
                    trip=trip,
                    seat_label=label,
                    row=r,
                    column=chr(64+c),
                    price=seat_price
                )

        return trip
