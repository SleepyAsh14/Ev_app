from rest_framework import viewsets, permissions, serializers, status
from rest_framework.response import Response
from .models import Reservation
from stations.models import ChargingStation

class ReservationSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='station.name', read_only=True)
    station_address = serializers.CharField(source='station.address', read_only=True)
    
    class Meta:
        model = Reservation
        fields = ['id', 'station', 'station_name', 'station_address', 
                 'start_time', 'end_time', 'status', 'estimated_cost', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        station = data.get('station')
        if station and station.available_ports <= 0:
            raise serializers.ValidationError("No available ports at this station")
        return data

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        reservation = serializer.save(user=self.request.user)
        # Reduce available ports when reservation is created
        station = reservation.station
        if station.available_ports > 0:
            station.available_ports -= 1
            station.save()