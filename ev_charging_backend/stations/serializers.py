from rest_framework import serializers
from .models import ChargingStation, StationReview

class ChargingStationSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
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

class StationReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = StationReview
        fields = ['id', 'station', 'user', 'user_name', 'rating', 'comment', 'created_at']