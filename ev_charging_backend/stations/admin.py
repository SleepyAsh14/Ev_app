from django.contrib import admin
from .models import ChargingStation, StationReview

@admin.register(ChargingStation)
class ChargingStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'charger_type', 'available_ports', 'total_ports', 'price_per_kwh']
    list_filter = ['status', 'charger_type']
    list_editable = ['status', 'available_ports', 'price_per_kwh']
    search_fields = ['name', 'address']

@admin.register(StationReview)  
class StationReviewAdmin(admin.ModelAdmin):
    list_display = ['station', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']