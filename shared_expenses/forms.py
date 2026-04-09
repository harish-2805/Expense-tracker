from django import forms
from .models import SharedExpense, Settlement
from accounts.models import CustomUser, Friendship
from datetime import date
from django.db.models import Q


class SharedExpenseForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Dinner at restaurant'}))
    total_amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0.01'}))
    split_type = forms.ChoiceField(
        choices=SharedExpense.SPLIT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_split_type'}))
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    notes = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes...'}))
    participants = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'participant-checkbox'}),
        required=True,
        help_text="Only your friends appear here. Add friends first if someone is missing.")  # ← new

    class Meta:
        model = SharedExpense
        fields = ['title', 'total_amount', 'split_type', 'date', 'notes', 'participants']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # ↓ ONLY CHANGE: show only accepted friends instead of all users
            friends = user.get_friends()
            self.fields['participants'].queryset = friends


class SettlementForm(forms.ModelForm):
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0.01'}),
        label='Payment Amount')
    note = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional note...'}))

    class Meta:
        model = Settlement
        fields = ['amount', 'note']