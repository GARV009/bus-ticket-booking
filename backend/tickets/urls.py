from django.urls import path
from .views import TripListView, HoldSeatsView

urlpatterns = [
    path('trips/', TripListView.as_view(), name='trip-list'),
    path('hold/', HoldSeatsView.as_view(), name='hold-seats'),
]
