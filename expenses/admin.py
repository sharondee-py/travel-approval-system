from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "employee",
        "amount",
        "currency",
        "category",
        "status",
        "created_at",
    )
    list_filter = ("status", "currency", "category")
    search_fields = ("employee__username", "merchant", "description")
