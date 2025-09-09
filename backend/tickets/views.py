from rest_framework import generics
from .models import Trip
from .serializers import TripSerializer

class TripListView(generics.ListCreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
