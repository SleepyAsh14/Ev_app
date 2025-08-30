# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    vehicle_model = serializers.CharField(required=False, allow_blank=True)
    preferred_charger_type = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number', 'vehicle_model', 'preferred_charger_type']

    def create(self, validated_data):
        # Extract profile data
        phone_number = validated_data.pop('phone_number', '')
        vehicle_model = validated_data.pop('vehicle_model', '')
        preferred_charger_type = validated_data.pop('preferred_charger_type', '')
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            phone_number=phone_number,
            vehicle_model=vehicle_model,
            preferred_charger_type=preferred_charger_type
        )
        
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'vehicle_model', 'preferred_charger_type']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        
        # Update user fields
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance