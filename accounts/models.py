from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended user model with currency preference."""

    CURRENCY_CHOICES = [
        ('INR', '₹ Indian Rupee (INR)'),
        ('USD', '$ US Dollar (USD)'),
        ('EUR', '€ Euro (EUR)'),
        ('GBP', '£ British Pound (GBP)'),
        ('JPY', '¥ Japanese Yen (JPY)'),
        ('AUD', 'A$ Australian Dollar (AUD)'),
    ]

    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    preferred_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='INR'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_currency_symbol(self):
        symbols = {
            'INR': '₹', 'USD': '$', 'EUR': '€',
            'GBP': '£', 'JPY': '¥', 'AUD': 'A$'
        }
        return symbols.get(self.preferred_currency, '₹')
