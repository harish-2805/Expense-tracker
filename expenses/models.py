from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.TextChoices):
    FOOD = 'Food', 'Food & Dining'
    TRAVEL = 'Travel', 'Travel & Transport'
    SHOPPING = 'Shopping', 'Shopping'
    ENTERTAINMENT = 'Entertainment', 'Entertainment'
    HEALTH = 'Health', 'Health & Medical'
    UTILITIES = 'Utilities', 'Utilities & Bills'
    EDUCATION = 'Education', 'Education'
    OTHERS = 'Others', 'Others'


class PaymentMethod(models.TextChoices):
    CASH = 'Cash', 'Cash'
    UPI = 'UPI', 'UPI'
    CARD = 'Card', 'Card (Debit/Credit)'
    NET_BANKING = 'Net Banking', 'Net Banking'
    WALLET = 'Wallet', 'Digital Wallet'


class Expense(models.Model):
    """Model representing a personal expense."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.OTHERS)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.amount}"

    def get_category_icon(self):
        icons = {
            'Food': 'bi-cup-hot',
            'Travel': 'bi-airplane',
            'Shopping': 'bi-bag',
            'Entertainment': 'bi-film',
            'Health': 'bi-heart-pulse',
            'Utilities': 'bi-lightning',
            'Education': 'bi-book',
            'Others': 'bi-three-dots',
        }
        return icons.get(self.category, 'bi-three-dots')

    def get_category_color(self):
        colors = {
            'Food': 'danger',
            'Travel': 'primary',
            'Shopping': 'warning',
            'Entertainment': 'info',
            'Health': 'success',
            'Utilities': 'secondary',
            'Education': 'dark',
            'Others': 'light',
        }
        return colors.get(self.category, 'secondary')
