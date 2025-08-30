# payments/serializers.py
from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'reservation', 'amount', 'currency', 'payment_method', 
                 'status', 'transaction_id', 'created_at']
        read_only_fields = ['id', 'user', 'transaction_id', 'created_at', 'status']