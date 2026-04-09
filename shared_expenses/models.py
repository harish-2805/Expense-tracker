from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class SharedExpense(models.Model):
    """A shared expense among multiple users."""

    SPLIT_CHOICES = [
        ('equal', 'Equal Split'),
        ('manual', 'Manual Split'),
    ]

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='created_shared_expenses')
    title = models.CharField(max_length=200)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    split_type = models.CharField(max_length=10, choices=SPLIT_CHOICES, default='equal')
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.total_amount}"

    def get_participants_count(self):
        return self.participants.count()

    def is_fully_settled(self):
        return all(p.is_settled for p in self.participants.all())


class Participant(models.Model):
    """A participant in a shared expense."""

    shared_expense = models.ForeignKey(SharedExpense, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participations')
    share_amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_payer = models.BooleanField(default=False)  # True if this person paid the bill
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    is_settled = models.BooleanField(default=False)

    class Meta:
        unique_together = ['shared_expense', 'user']

    def __str__(self):
        return f"{self.user.email} owes {self.share_amount} for {self.shared_expense.title}"

    def amount_due(self):
        """Amount still owed (0 if payer or settled)."""
        if self.is_payer:
            return Decimal('0')
        return max(self.share_amount - self.amount_paid, Decimal('0'))

    def save(self, *args, **kwargs):
        # Auto-settle payer or when fully paid
        if self.is_payer or self.amount_paid >= self.share_amount:
            self.is_settled = True
        super().save(*args, **kwargs)


class Settlement(models.Model):
    """A repayment record for a shared expense participant."""

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='settlements')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=200, blank=True)
    via_upi = models.BooleanField(default=False)  # Mock UPI payment flag

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return f"{self.participant.user.email} paid {self.amount}"
