from django.contrib import admin
from .models import ChargingStation

@admin.register(ChargingStation)
class ChargingStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'status', 'charger_type', 'available_ports', 'total_ports']
    list_filter = ['status', 'charger_type']
    search_fields = ['name', 'address']