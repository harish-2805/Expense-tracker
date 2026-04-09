from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('Food', 'Food & Dining'), ('Travel', 'Travel & Transport'), ('Shopping', 'Shopping'), ('Entertainment', 'Entertainment'), ('Health', 'Health & Medical'), ('Utilities', 'Utilities & Bills'), ('Education', 'Education'), ('Others', 'Others')], max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['category'],
                'unique_together': {('user', 'category', 'month', 'year')},
            },
        ),
    ]
