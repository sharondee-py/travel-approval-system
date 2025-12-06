from django.db import models


class PolicyRule(models.Model):
    """
    Example policies:
    - Trips > 1500 USD require finance approval
    - Any single expense > 500 USD is flagged
    """

    class Scope(models.TextChoices):
        TRAVEL = "TRAVEL", "Travel"
        EXPENSE = "EXPENSE", "Expense"

    name = models.CharField(max_length=100)

    scope = models.CharField(
        max_length=20,
        choices=Scope.choices,
        default=Scope.TRAVEL,
    )

    description = models.TextField()

    min_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum threshold for rule to apply",
    )

    max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum threshold (if any)",
    )

    require_finance_approval = models.BooleanField(default=False)
    auto_flag = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
