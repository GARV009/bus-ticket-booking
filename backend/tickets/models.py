from django.db import models

class Trip(models.Model):
    title = models.CharField(max_length=200)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    depart_at = models.DateTimeField(null=True, blank=True)
    arrive_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.origin} → {self.destination})"

class Seat(models.Model):
    trip = models.ForeignKey(Trip, related_name='seats', on_delete=models.CASCADE)
    seat_label = models.CharField(max_length=16)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    is_sold = models.BooleanField(default=False)
