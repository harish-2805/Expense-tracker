from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
import re   # ✅ ADDED


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=255, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Full Name', 'class': 'form-control'}))
    
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-control'}))
    
    preferred_currency = forms.ChoiceField(choices=CustomUser.CURRENCY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}))
    
    password1 = forms.CharField(label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))
    
    password2 = forms.CharField(label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('full_name', 'email', 'preferred_currency', 'password1', 'password2')

    # ✅ ADDED PASSWORD VALIDATION
    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")

        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            raise forms.ValidationError("Password must contain at least one special character.")

        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Use email as username
        user.preferred_currency = self.cleaned_data['preferred_currency']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-control', 'autofocus': True}))
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))