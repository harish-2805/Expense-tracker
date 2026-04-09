from django import forms
from .models import Budget
from expenses.models import Category
from datetime import date


class BudgetForm(forms.ModelForm):
    category = forms.ChoiceField(
        choices=Category.choices,
        widget=forms.Select(attrs={'class': 'form-select'}))
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0.01'}))
    month = forms.ChoiceField(
        choices=[(i, date(2000, i, 1).strftime('%B')) for i in range(1, 13)],
        widget=forms.Select(attrs={'class': 'form-select'}))
    year = forms.ChoiceField(
        choices=[(y, y) for y in range(date.today().year - 2, date.today().year + 3)],
        widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year']
