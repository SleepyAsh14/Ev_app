from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]