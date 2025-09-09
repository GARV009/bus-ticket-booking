from django.urls import path
from .views import TripListView, HoldSeatsView
from .views import TripListView, HoldSeatsView, PurchaseView

urlpatterns = [
    path('trips/', TripListView.as_view(), name='trip-list'),
    path('hold/', HoldSeatsView.as_view(), name='hold-seats'),
    path('purchase/', PurchaseView.as_view(), name='purchase'),
]
