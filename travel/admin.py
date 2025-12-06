from django.contrib import admin
from .models import TravelRequest

@admin.register(TravelRequest)
class TravelRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee",
        "destination_city",
        "destination_country",
        "status",
        "estimated_cost",
        "currency",
        "created_at",
    )
    list_filter = ("status", "destination_country", "currency")
    search_fields = ("employee__username", "destination_city", "reason")
