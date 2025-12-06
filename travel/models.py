from django.conf import settings
from django.db import models
from policies.engine import evaluate_travel_request


class TravelRequest(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING_MANAGER = "PENDING_MANAGER", "Pending Manager Approval"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        ESCALATED_FINANCE = "ESCALATED_FINANCE", "Escalated to Finance"

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="travel_requests",
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="managed_requests",
        help_text="Manager responsible for approval",
    )

    finance_reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="finance_reviews",
    )

    destination_city = models.CharField(max_length=100)
    destination_country = models.CharField(max_length=100)

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.TextField()

    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Estimated cost in local currency",
    )

    currency = models.CharField(max_length=10, default="USD")

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    policy_flags = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.username} → {self.destination_city} ({self.status})"

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1

    def run_policy_checks(self):
        violations = evaluate_travel_request(self)
        self.policy_flags = violations
        self.save()

        # Auto escalate if needed
        requires_finance = any(v.get("require_finance_approval") for v in violations)
        if requires_finance:
            self.status = self.Status.ESCALATED_FINANCE
            self.save()

        return violations

