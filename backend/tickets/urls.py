from django.urls import path
from .views import TripListView, TripDetailView, HoldSeatsView, PurchaseView

urlpatterns = [
    path('trips/', TripListView.as_view(), name='trip-list'),
    path('trips/<int:trip_id>/', TripDetailView.as_view(), name='trip-detail'),
    path('hold/', HoldSeatsView.as_view(), name='hold-seats'),
    path('purchase/', PurchaseView.as_view(), name='purchase'),
]

