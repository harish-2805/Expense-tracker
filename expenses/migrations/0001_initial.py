from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('category', models.CharField(choices=[('Food', 'Food & Dining'), ('Travel', 'Travel & Transport'), ('Shopping', 'Shopping'), ('Entertainment', 'Entertainment'), ('Health', 'Health & Medical'), ('Utilities', 'Utilities & Bills'), ('Education', 'Education'), ('Others', 'Others')], default='Others', max_length=50)),
                ('payment_method', models.CharField(choices=[('Cash', 'Cash'), ('UPI', 'UPI'), ('Card', 'Card (Debit/Credit)'), ('Net Banking', 'Net Banking'), ('Wallet', 'Digital Wallet')], default='Cash', max_length=20)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('notes', models.TextField(blank=True, null=True)),
                ('is_shared', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date', '-created_at'],
            },
        ),
    ]
