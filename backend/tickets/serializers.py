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
