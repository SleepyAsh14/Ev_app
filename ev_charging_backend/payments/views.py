from rest_framework import viewsets, permissions
from .models import Payment

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')
        
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class PaymentSerializer(serializers.ModelSerializer):
            class Meta:
                model = Payment
                fields = '__all__'
                
        return PaymentSerializer