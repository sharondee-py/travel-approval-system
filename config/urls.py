from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from travel.api import TravelRequestViewSet

router = DefaultRouter()
router.register("travel-requests", TravelRequestViewSet, basename="travel")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
]
