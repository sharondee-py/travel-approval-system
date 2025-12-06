from django.conf import settings
from django.db import models

class UserProfile(models.Model):
    class Role(models.TextChoices):
        EMPLOYEE = "EMPLOYEE", "Employee"
        MANAGER = "MANAGER", "Manager"
        FINANCE = "FINANCE", "Finance"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )

    department = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
