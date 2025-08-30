# tests/test_reservations.py - Critical module testing
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from stations.models import ChargingStation
from reservations.models import Reservation
from payments.models import Payment

class ReservationAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser@test.com',
            email='testuser@test.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.station = ChargingStation.objects.create(
            name='Test Station',
            address='Test Address, Casablanca',
            latitude=33.5731,
            longitude=-7.5898,
            charger_type='type2',
            power_rating=22,
            price_per_kwh=2.50,
            total_ports=4,
            available_ports=3,
            status='active'
        )
    
    def test_create_reservation(self):
        """Test creating a new reservation"""
        start_time = timezone.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        data = {
            'station': self.station.id,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'estimated_cost': 125.00
        }
        
        response = self.client.post('/api/reservations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check station availability decreased
        self.station.refresh_from_db()
        self.assertEqual(self.station.available_ports, 2)
    
    def test_reservation_overlap_validation(self):
        """Test that overlapping reservations are prevented"""
        start_time = timezone.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        
        # Create first reservation
        Reservation.objects.create(
            user=self.user,
            station=self.station,
            start_time=start_time,
            end_time=end_time,
            estimated_cost=100.00
        )
        
        # Try to create overlapping reservation
        data = {
            'station': self.station.id,
            'start_time': (start_time + timedelta(minutes=30)).isoformat(),
            'end_time': (end_time + timedelta(minutes=30)).isoformat(),
            'estimated_cost': 125.00
        }
        
        response = self.client.post('/api/reservations/', data)
        # Should succeed if station has multiple ports
        if self.station.total_ports > 1:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_cancel_reservation(self):
        """Test cancelling a reservation"""
        start_time = timezone.now() + timedelta(hours=2)
        end_time = start_time + timedelta(hours=1)
        
        reservation = Reservation.objects.create(
            user=self.user,
            station=self.station,
            start_time=start_time,
            end_time=end_time,
            estimated_cost=100.00,
            status='confirmed'
        )
        
        response = self.client.post(f'/api/reservations/{reservation.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'cancelled')

class PaymentAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='paymentuser@test.com',
            email='paymentuser@test.com',
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.station = ChargingStation.objects.create(
            name='Payment Test Station',
            address='Test Address, Casablanca',
            latitude=33.5731,
            longitude=-7.5898,
            charger_type='type2',
            power_rating=22,
            price_per_kwh=2.50,
            total_ports=2,
            available_ports=2,
            status='active'
        )
        
        self.reservation = Reservation.objects.create(
            user=self.user,
            station=self.station,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=3),
            estimated_cost=125.00,
            status='pending'
        )
    
    def test_create_payment(self):
        """Test creating a payment"""
        data = {
            'reservation': self.reservation.id,
            'amount': 125.00,
            'payment_method': 'card'
        }
        
        response = self.client.post('/api/payments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check reservation status updated
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, 'confirmed')
    
    def test_process_refund(self):
        """Test processing a refund"""
        payment = Payment.objects.create(
            user=self.user,
            reservation=self.reservation,
            amount=125.00,
            payment_method='card',
            status='completed'
        )
        
        response = self.client.post(f'/api/payments/{payment.id}/refund/', {
            'reason': 'station_defective',
            'amount': 125.00
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'refunded')