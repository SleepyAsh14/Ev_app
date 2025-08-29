from django.db import models
from django.contrib.auth.models import User

class ChargingStation(models.Model):
    STATION_STATUS = [
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
        ('offline', 'Offline'),
        ('defective', 'Defective'),
    ]
    
    CHARGER_TYPES = [
        ('type1', 'Type 1 (J1772)'),
        ('type2', 'Type 2 (Mennekes)'),
        ('ccs', 'CCS (Combined Charging System)'),
        ('chademo', 'CHAdeMO'),
        ('tesla', 'Tesla Supercharger'),
    ]

    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    status = models.CharField(max_length=20, choices=STATION_STATUS, default='active')
    charger_type = models.CharField(max_length=20, choices=CHARGER_TYPES)
    power_rating = models.IntegerField(help_text="Power in kW")
    price_per_kwh = models.DecimalField(max_digits=6, decimal_places=3)
    total_ports = models.IntegerField(default=1)
    available_ports = models.IntegerField(default=1)
    amenities = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'charging_stations'
        
    def __str__(self):
        return f"{self.name} - {self.address}"

class StationReview(models.Model):
    station = models.ForeignKey(ChargingStation, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('station', 'user')