# reservations/tasks.py - Automatic reservation management
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from reservations.models import Reservation
from stations.models import ChargingStation

class Command(BaseCommand):
    help = 'Manage expired reservations and update station availability'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find expired reservations
        expired_reservations = Reservation.objects.filter(
            status__in=['pending', 'confirmed'],
            start_time__lt=now - timedelta(minutes=15)  # 15 min grace period
        )
        
        expired_count = 0
        for reservation in expired_reservations:
            # Mark as expired
            reservation.status = 'expired'
            reservation.save()
            
            # Free up the station port
            station = reservation.station
            station.available_ports = min(station.available_ports + 1, station.total_ports)
            station.save()
            
            expired_count += 1
            self.stdout.write(f'Expired reservation {reservation.id} at {station.name}')
        
        # Auto-complete active reservations that have ended
        completed_reservations = Reservation.objects.filter(
            status='active',
            end_time__lt=now
        )
        
        completed_count = 0
        for reservation in completed_reservations:
            reservation.status = 'completed'
            reservation.save()
            
            # Free up the station port
            station = reservation.station
            station.available_ports = min(station.available_ports + 1, station.total_ports)
            station.save()
            
            completed_count += 1
            self.stdout.write(f'Completed reservation {reservation.id} at {station.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Processed {expired_count} expired and {completed_count} completed reservations'
            )
        )

# reservations/views.py - Enhanced with automatic management
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from .models import Reservation
from stations.models import ChargingStation

class ReservationSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='station.name', read_only=True)
    station_address = serializers.CharField(source='station.address', read_only=True)
    can_cancel = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = ['id', 'station', 'station_name', 'station_address', 
                 'start_time', 'end_time', 'status', 'estimated_cost', 
                 'created_at', 'can_cancel']
        read_only_fields = ['id', 'created_at']

    def get_can_cancel(self, obj):
        now = timezone.now()
        time_until_start = (obj.start_time - now).total_seconds() / 3600
        return obj.status in ['pending', 'confirmed'] and time_until_start > 1

    def validate(self, data):
        station = data.get('station')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        # Check station availability
        if station and station.available_ports <= 0:
            raise serializers.ValidationError("No available ports at this station")

        # Check timing
        now = timezone.now()
        if start_time <= now:
            raise serializers.ValidationError("Start time must be in the future")

        if end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time")

        # Check for overlapping reservations at the same station
        overlapping = Reservation.objects.filter(
            station=station,
            status__in=['pending', 'confirmed', 'active'],
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(user=self.context['request'].user)

        if overlapping.count() >= station.total_ports:
            raise serializers.ValidationError("Station is fully booked for this time period")

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
            
        self.stdout.write(f'Reservation created: {reservation.id}')
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        
        if reservation.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Cannot cancel this reservation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        now = timezone.now()
        time_until_start = (reservation.start_time - now).total_seconds() / 3600
        
        if time_until_start <= 1:
            return Response(
                {'error': 'Cannot cancel reservations less than 1 hour before start time'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel the reservation
        reservation.status = 'cancelled'
        reservation.save()
        
        # Free up the station port
        station = reservation.station
        station.available_ports = min(station.available_ports + 1, station.total_ports)
        station.save()
        
        return Response({'message': 'Reservation cancelled successfully'})
    
    @action(detail=True, methods=['post'])
    def start_charging(self, request, pk=None):
        reservation = self.get_object()
        
        if reservation.status != 'confirmed':
            return Response(
                {'error': 'Only confirmed reservations can be started'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        now = timezone.now()
        if now < reservation.start_time - timedelta(minutes=15):
            return Response(
                {'error': 'Cannot start charging more than 15 minutes early'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'active'
        reservation.save()
        
        return Response({'message': 'Charging session started'})
    
    @action(detail=True, methods=['post'])
    def complete_charging(self, request, pk=None):
        reservation = self.get_object()
        
        if reservation.status != 'active':
            return Response(
                {'error': 'Only active reservations can be completed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'completed'
        reservation.save()
        
        # Free up the station port
        station = reservation.station
        station.available_ports = min(station.available_ports + 1, station.total_ports)
        station.save()
        
        return Response({'message': 'Charging session completed'})