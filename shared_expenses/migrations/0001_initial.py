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
            name='SharedExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('split_type', models.CharField(choices=[('equal', 'Equal Split'), ('manual', 'Manual Split')], default='equal', max_length=10)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_shared_expenses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('share_amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('is_payer', models.BooleanField(default=False)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('is_settled', models.BooleanField(default=False)),
                ('shared_expense', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='shared_expenses.sharedexpense')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('shared_expense', 'user')},
            },
        ),
        migrations.CreateModel(
            name='Settlement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('paid_at', models.DateTimeField(auto_now_add=True)),
                ('note', models.CharField(blank=True, max_length=200)),
                ('via_upi', models.BooleanField(default=False)),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settlements', to='shared_expenses.participant')),
            ],
            options={
                'ordering': ['-paid_at'],
            },
        ),
    ]
