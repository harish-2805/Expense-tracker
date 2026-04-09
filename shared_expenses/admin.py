from django.contrib import admin
from .models import SharedExpense, Participant, Settlement

@admin.register(SharedExpense)
class SharedExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'total_amount', 'split_type', 'date']

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'shared_expense', 'share_amount', 'amount_paid', 'is_payer', 'is_settled']

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ['participant', 'amount', 'paid_at', 'via_upi']
