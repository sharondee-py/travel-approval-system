from django.conf import settings
from django.db import models
from travel.models import TravelRequest
from policies.engine import evaluate_expense


class Expense(models.Model):
    class Category(models.TextChoices):
        FLIGHT = "FLIGHT", "Flight"
        HOTEL = "HOTEL", "Hotel"
        MEAL = "MEAL", "Meal"
        TRANSPORT = "TRANSPORT", "Transport"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        FLAGGED = "FLAGGED", "Flagged"

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )

    travel_request = models.ForeignKey(
        TravelRequest,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="expenses",
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )

    merchant = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)

    receipt = models.FileField(
        upload_to="receipts/",
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.amount} {self.currency}"

    def run_policy_checks(self):
        violations = evaluate_expense(self)

        # Auto-flag if needed
        if any(v.get("auto_flag") for v in violations):
            self.status = self.Status.FLAGGED
            self.save()

        return violations

