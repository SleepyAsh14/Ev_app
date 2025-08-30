# reservations/serializers.py
from rest_framework import serializers
from .models import Reservation
from stations.models import ChargingStation

class ReservationSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='station.name', read_only=True)
    station_address = serializers.CharField(source='station.address', read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'station', 'station_name', 'station_address', 
                 'start_time', 'end_time', 'status', 'estimated_cost', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate(self, data):
        station = data.get('station')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        # Check if station is available
        if station.available_ports <= 0:
            raise serializers.ValidationError("No available ports at this station")

        # Check if start time is in the future
        from django.utils import timezone
        if start_time <= timezone.now():
            raise serializers.ValidationError("Start time must be in the future")

        # Check if end time is after start time
        if end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time")

        return data