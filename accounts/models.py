from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        VENDOR = 'vendor', 'Vendor'
        DROPSHIPPER = 'dropshipper', 'Dropshipper'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"