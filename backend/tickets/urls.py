from django.urls import path
from .views import TripListView, TripDetailView, HoldSeatsView, PurchaseView, TripCreateView, ReleaseSeatsView

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('trips/', TripListView.as_view(), name='trip-list'),
    path('trips/<int:trip_id>/', TripDetailView.as_view(), name='trip-detail'),
    path("trips/create/", TripCreateView.as_view(), name="trip-create"),
    path('hold/', HoldSeatsView.as_view(), name='hold-seats'),
    path('purchase/', PurchaseView.as_view(), name='purchase'),
    path("release/", ReleaseSeatsView.as_view(), name="release-seats"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

