from django.contrib import admin
from django.urls import path, include  # 👈 include is needed

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),  # 👈 this connects your users app
]
