from django.contrib import admin
from .models import PolicyRule


@admin.register(PolicyRule)
class PolicyRuleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "scope",
        "require_finance_approval",
        "auto_flag",
        "active",
    )
    list_filter = ("scope", "active", "require_finance_approval")
    search_fields = ("name", "description")
