from django.db import models
from django.conf import settings
from expenses.models import Category
from django.utils import timezone


class Budget(models.Model):
    """Monthly budget per category for a user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=50, choices=Category.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'category', 'month', 'year']
        ordering = ['category']

    def __str__(self):
        return f"{self.user.email} - {self.category} - {self.month}/{self.year}: {self.amount}"
