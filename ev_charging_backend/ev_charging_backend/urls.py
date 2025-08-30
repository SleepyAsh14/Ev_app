from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # API endpoints
    path("api/stations/", include("stations.urls")),
    path("api/users/", include("users.urls")),
    path("api/reservations/", include("reservations.urls")),
    path("api/payments/", include("payments.urls")),  # Comment this out for now
    
    # Authentication endpoints
    path("api/auth/login/", TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name='token_refresh'),
]