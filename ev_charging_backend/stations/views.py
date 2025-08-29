from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import ChargingStation, StationReview
from .serializers import ChargingStationSerializer, StationReviewSerializer

class ChargingStationViewSet(viewsets.ModelViewSet):
    queryset = ChargingStation.objects.all()
    serializer_class = ChargingStationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'charger_type']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get nearby stations based on lat/lng"""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 10))  # Default 10km
        
        if not lat or not lng:
            return Response({'error': 'lat and lng parameters required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Simple distance calculation (for production use PostGIS)
        stations = ChargingStation.objects.filter(
            latitude__range=(float(lat) - radius/111, float(lat) + radius/111),
            longitude__range=(float(lng) - radius/111, float(lng) + radius/111),
            status='active'
        )
        
        serializer = self.get_serializer(stations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def report_defective(self, request, pk=None):
        """Report a station as defective"""
        station = self.get_object()
        station.status = 'defective'
        station.save()
        return Response({'message': 'Station reported as defective'})