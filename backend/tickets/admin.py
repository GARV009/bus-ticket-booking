from django.contrib import admin
from .models import Trip, Seat

class SeatInline(admin.TabularInline):
    model = Seat
    extra = 1  # allows adding extra seats directly when creating a Trip

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("title", "origin", "destination", "depart_at", "arrive_at")
    inlines = [SeatInline]

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("trip", "seat_label", "price", "is_sold")
