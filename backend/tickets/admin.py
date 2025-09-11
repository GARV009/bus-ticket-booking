from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Trip, Seat, Booking, User

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

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role Info", {"fields": ("role",)}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Role Info", {"fields": ("role",)}),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "trip", "buyer_email", "total_amount", "created_at")
    list_filter = ("trip", "created_at")
    search_fields = ("buyer_email",)
    filter_horizontal = ("seats",)  
