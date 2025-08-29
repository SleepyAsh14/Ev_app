from django.db import models
from django.contrib.auth.models import User
from stations.models import ChargingStation
from datetime import timedelta
from django.utils import timezone

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(ChargingStation, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.end_time and self.start_time:
            self.end_time = self.start_time + timedelta(hours=2)  # Default 2-hour reservation
        super().save(*args, **kwargs)
    
    def is_expired(self):
        return timezone.now() > self.end_time and self.status in ['pending', 'confirmed']