from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'full_name', 'preferred_currency', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('full_name', 'preferred_currency')}),
    )
