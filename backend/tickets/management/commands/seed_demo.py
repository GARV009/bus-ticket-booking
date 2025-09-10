from django.core.management.base import BaseCommand
from tickets.models import Trip, Seat
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Seed demo data: one trip with seats"

    def handle(self, *args, **kwargs):
        # Clear old demo trips
        Trip.objects.filter(title="Demo Trip").delete()

        # Create a demo trip
        trip = Trip.objects.create(
            title="Demo Trip",
            origin="City A",
            destination="City B",
            depart_at=timezone.now() + timedelta(days=1),
            arrive_at=timezone.now() + timedelta(days=1, hours=5),
        )

        # Create seats (4 rows × 4 seats each = 16 total)
        seat_labels = []
        for row in range(1, 5):
            for col in ["A", "B", "C", "D"]:
                seat_labels.append(f"{row}{col}")

        seats = [
            Seat(trip=trip, seat_label=label, row=int(label[0]), column=label[1], price=500)
            for label in seat_labels
        ]
        Seat.objects.bulk_create(seats)

        self.stdout.write(self.style.SUCCESS("✅ Demo Trip with 16 seats created"))
