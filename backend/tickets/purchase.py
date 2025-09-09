from django.db import transaction
from .models import Seat, Booking
from .redis_utils import get_hold, release_hold

def try_purchase(trip_id:int, seat_ids:list, hold_token:str, buyer_email:str=None):
    """
    Atomically:
    - validate holds
    - lock seat rows
    - ensure not sold
    - mark sold + create Booking
    - release holds
    """
    with transaction.atomic():
        # Lock seat rows
        seats = list(Seat.objects.select_for_update().filter(id__in=seat_ids, trip_id=trip_id))
        if len(seats) != len(seat_ids):
            raise Exception("Some seats not found")

        # Validate hold for each seat
        for seat in seats:
            hold = get_hold(trip_id, seat.id)
            if not hold or hold.get("hold_token") != hold_token:
                raise Exception(f"Invalid or missing hold for seat {seat.seat_label}")

        # Ensure not sold
        for seat in seats:
            if seat.is_sold:
                raise Exception(f"Seat {seat.seat_label} already sold")

        # Mark seats sold
        for seat in seats:
            seat.is_sold = True
            seat.save()

        # Create booking
        total = sum([seat.price for seat in seats])
        booking = Booking.objects.create(
            trip_id=trip_id,
            total_amount=total,
        )
        booking.seats.set(seats)
        booking.save()

        # Release holds
        for seat in seats:
            release_hold(trip_id, seat.id)

        return booking
