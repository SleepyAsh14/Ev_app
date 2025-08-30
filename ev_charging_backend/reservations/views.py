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

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)