from django import forms
from .models import Expense, Category, PaymentMethod


class ExpenseForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lunch at restaurant'}))
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01', 'min': '0.01'}))
    category = forms.ChoiceField(
        choices=Category.choices,
        widget=forms.Select(attrs={'class': 'form-select'}))
    payment_method = forms.ChoiceField(
        choices=PaymentMethod.choices,
        widget=forms.Select(attrs={'class': 'form-select'}))
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    notes = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes...'}))

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'payment_method', 'date', 'notes']
