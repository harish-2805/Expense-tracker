"""
Management command to load sample data for demo purposes.
Usage: python manage.py load_sample_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random

from accounts.models import CustomUser
from expenses.models import Expense
from budgets.models import Budget
from shared_expenses.models import SharedExpense, Participant


class Command(BaseCommand):
    help = 'Load sample data for demonstration'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample users...')

        # Create user 1
        user1, created = CustomUser.objects.get_or_create(
            email='alice@example.com',
            defaults={
                'username': 'alice@example.com',
                'full_name': 'Alice Johnson',
                'preferred_currency': 'INR',
                'is_active': True,
            }
        )
        if created:
            user1.set_password('demo1234')
            user1.save()
            self.stdout.write(f'  Created: alice@example.com (password: demo1234)')

        # Create user 2
        user2, created = CustomUser.objects.get_or_create(
            email='bob@example.com',
            defaults={
                'username': 'bob@example.com',
                'full_name': 'Bob Smith',
                'preferred_currency': 'INR',
                'is_active': True,
            }
        )
        if created:
            user2.set_password('demo1234')
            user2.save()
            self.stdout.write(f'  Created: bob@example.com (password: demo1234)')

        today = date.today()
        month = today.month
        year = today.year

        self.stdout.write('Creating sample expenses for Alice...')
        sample_expenses = [
            ('Lunch at Subway', 350, 'Food', 'UPI'),
            ('Monthly Groceries', 2800, 'Food', 'Card'),
            ('Uber to Office', 180, 'Travel', 'UPI'),
            ('New Jeans', 1499, 'Shopping', 'Card'),
            ('Netflix Subscription', 649, 'Entertainment', 'Card'),
            ('Doctor Visit', 500, 'Health', 'Cash'),
            ('Electricity Bill', 1200, 'Utilities', 'Net Banking'),
            ('Online Course', 2999, 'Education', 'Card'),
            ('Movie Tickets', 600, 'Entertainment', 'UPI'),
            ('Pharmacy', 350, 'Health', 'Cash'),
            ('Coffee Shop', 220, 'Food', 'UPI'),
            ('Swiggy Order', 450, 'Food', 'UPI'),
        ]
        for i, (title, amount, category, payment) in enumerate(sample_expenses):
            expense_date = today - timedelta(days=random.randint(0, 25))
            Expense.objects.get_or_create(
                user=user1, title=title,
                defaults={
                    'amount': Decimal(str(amount)),
                    'category': category,
                    'payment_method': payment,
                    'date': expense_date,
                    'notes': f'Sample expense for {title}',
                }
            )

        self.stdout.write('Creating sample budgets for Alice...')
        budgets_data = [
            ('Food', 5000),
            ('Travel', 2000),
            ('Shopping', 3000),
            ('Entertainment', 1500),
            ('Health', 2000),
            ('Utilities', 2000),
        ]
        for category, amount in budgets_data:
            Budget.objects.get_or_create(
                user=user1, category=category, month=month, year=year,
                defaults={'amount': Decimal(str(amount))}
            )

        self.stdout.write('Creating sample shared expense...')
        se, created = SharedExpense.objects.get_or_create(
            title='Team Dinner at Restaurant',
            created_by=user1,
            defaults={
                'total_amount': Decimal('3000'),
                'split_type': 'equal',
                'date': today - timedelta(days=3),
                'notes': 'Team dinner after project completion',
            }
        )
        if created:
            share = Decimal('1500')
            Participant.objects.create(
                shared_expense=se, user=user1,
                share_amount=share, is_payer=True,
                amount_paid=share, is_settled=True
            )
            Participant.objects.create(
                shared_expense=se, user=user2,
                share_amount=share, is_payer=False,
                amount_paid=Decimal('0'), is_settled=False
            )

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data loaded successfully!'))
        self.stdout.write(self.style.SUCCESS('   Login with: alice@example.com / demo1234'))
        self.stdout.write(self.style.SUCCESS('   Or:         bob@example.com  / demo1234'))
