from rest_framework import serializers
from .models import TravelRequest


class TravelRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = TravelRequest
        fields = "__all__"
        read_only_fields = (
            "employee",
            "status",
            "policy_flags",
            "created_at",
            "updated_at",
            "manager",
            "finance_reviewer",
        )
