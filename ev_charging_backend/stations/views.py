from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChargingStation

class ChargingStationViewSet(viewsets.ModelViewSet):
    queryset = ChargingStation.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class ChargingStationSerializer(serializers.ModelSerializer):
            class Meta:
                model = ChargingStation
                fields = '__all__'
        
        return ChargingStationSerializer
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 10))
        
        stations = ChargingStation.objects.filter(status='active')
        serializer = self.get_serializer(stations, many=True)
        return Response(serializer.data)