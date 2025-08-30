# stations/serializers.py - Add this to your existing file
from rest_framework import serializers
from .models import ChargingStation, StationReview

class StationReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = StationReview
        fields = ['id', 'station', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class ChargingStationSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    recent_reviews = StationReviewSerializer(source='reviews', many=True, read_only=True)
    
    class Meta:
        model = ChargingStation
        fields = '__all__'
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum([r.rating for r in reviews]) / len(reviews), 1)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.count()

# stations/views.py - Update your existing ChargingStationViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import ChargingStation, StationReview
from .serializers import ChargingStationSerializer, StationReviewSerializer

class ChargingStationViewSet(viewsets.ModelViewSet):
    queryset = ChargingStation.objects.all()
    serializer_class = ChargingStationSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'nearby']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 10))
        
        if not lat or not lng:
            return Response({'error': 'lat and lng parameters required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        stations = ChargingStation.objects.filter(
            latitude__range=(float(lat) - radius/111, float(lat) + radius/111),
            longitude__range=(float(lng) - radius/111, float(lng) + radius/111),
            status='active'
        )
        
        serializer = self.get_serializer(stations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def report_defective(self, request, pk=None):
        station = self.get_object()
        station.status = 'defective'
        station.save()
        return Response({'message': 'Station reported as defective'})
    
    @action(detail=True, methods=['post'])
    def add_review(self, request, pk=None):
        station = self.get_object()
        
        # Check if user already reviewed this station
        existing_review = StationReview.objects.filter(
            station=station, 
            user=request.user
        ).first()
        
        if existing_review:
            return Response(
                {'error': 'You have already reviewed this station'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = StationReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, station=station)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        station = self.get_object()
        reviews = StationReview.objects.filter(station=station).order_by('-created_at')
        serializer = StationReviewSerializer(reviews, many=True)
        return Response(serializer.data)