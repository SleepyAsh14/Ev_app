# payments/models.py - Complete Payment model
from django.db import models
from django.contrib.auth.models import User
from reservations.models import Reservation
import uuid

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('mobile', 'Mobile Payment'),
        ('cash', 'Cash at Station'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='MAD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_gateway_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount} {self.currency}"

class Refund(models.Model):
    REFUND_REASONS = [
        ('station_defective', 'Station Defective'),
        ('user_cancelled', 'User Cancelled'),
        ('technical_issue', 'Technical Issue'),
        ('service_unavailable', 'Service Unavailable'),
        ('other', 'Other'),
    ]
    
    REFUND_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    reason = models.CharField(max_length=30, choices=REFUND_REASONS)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=REFUND_STATUS, default='pending')
    admin_notes = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Refund {self.id} - {self.amount} MAD"

# payments/views.py - Complete payment processing
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Payment, Refund

class PaymentSerializer(serializers.ModelSerializer):
    reservation_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = ['id', 'reservation', 'reservation_details', 'amount', 'currency', 
                 'payment_method', 'status', 'transaction_id', 'created_at']
        read_only_fields = ['id', 'user', 'transaction_id', 'created_at']
    
    def get_reservation_details(self, obj):
        if obj.reservation:
            return {
                'station_name': obj.reservation.station.name,
                'start_time': obj.reservation.start_time,
                'end_time': obj.reservation.end_time,
            }
        return None

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Simulate payment processing
        payment = serializer.save(
            user=self.request.user,
            status='completed',  # In real app, this would be 'processing' initially
        )
        
        # Update reservation status to confirmed after payment
        if payment.reservation:
            payment.reservation.status = 'confirmed'
            payment.reservation.save()
    
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        
        if payment.status != 'completed':
            return Response(
                {'error': 'Can only refund completed payments'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', 'user_request')
        refund_amount = request.data.get('amount', payment.amount)
        
        refund = Refund.objects.create(
            payment=payment,
            reason=reason,
            amount=refund_amount,
            status='completed',  # Simulate instant refund
        )
        
        payment.status = 'refunded'
        payment.save()
        
        return Response({
            'message': 'Refund processed successfully',
            'refund_id': refund.id,
            'amount': refund_amount
        })

# Create management command: reservations/management/commands/cleanup_reservations.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from reservations.models import Reservation

class Command(BaseCommand):
    help = 'Clean up expired reservations and update station availability'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Process expired reservations
        expired_reservations = Reservation.objects.filter(
            status__in=['pending', 'confirmed'],
            start_time__lt=now - timedelta(minutes=15)
        )
        
        for reservation in expired_reservations:
            reservation.status = 'expired'
            reservation.save()
            
            # Free up station port
            station = reservation.station
            if station.available_ports < station.total_ports:
                station.available_ports += 1
                station.save()
        
        # Auto-complete ended sessions
        completed_sessions = Reservation.objects.filter(
            status='active',
            end_time__lt=now
        )
        
        for session in completed_sessions:
            session.status = 'completed'
            session.save()
            
            # Free up station port
            station = session.station
            if station.available_ports < station.total_ports:
                station.available_ports += 1
                station.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Processed {expired_reservations.count()} expired and {completed_sessions.count()} completed reservations'
            )
        )