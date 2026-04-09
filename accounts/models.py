from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
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
        max_length=3, choices=CURRENCY_CHOICES, default='INR'
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

    def get_friends(self):
        """Return accepted friends of this user."""
        sent = Friendship.objects.filter(from_user=self, status='accepted').values_list('to_user', flat=True)
        received = Friendship.objects.filter(to_user=self, status='accepted').values_list('from_user', flat=True)
        ids = list(sent) + list(received)
        return CustomUser.objects.filter(pk__in=ids)

    def get_pending_requests(self):
        """Friend requests received and not yet responded to."""
        return Friendship.objects.filter(to_user=self, status='pending')


class Friendship(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    from_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='sent_requests'
    )
    to_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='received_requests'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['from_user', 'to_user']

    def __str__(self):
        return f"{self.from_user.email} → {self.to_user.email} ({self.status})"