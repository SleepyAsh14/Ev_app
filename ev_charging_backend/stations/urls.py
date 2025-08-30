from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChargingStationViewSet

router = DefaultRouter()
router.register(r'', ChargingStationViewSet, basename='chargingstation')

urlpatterns = [
    path('', include(router.urls)),
]