from django import forms
from .models import TicketBooking
from datetime import date
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Import User model
from django.contrib.auth.forms import AuthenticationForm

class TicketBookingForm(forms.ModelForm):
    class Meta:
        model = TicketBooking
        fields = ['name', 'email', 'date', 'tickets']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': date.today().isoformat(), 'max': date.today().isoformat()}),  
            'tickets': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
        }
    
    def clean_date(self):
        selected_date = self.cleaned_data['date']
        if selected_date != date.today():
            raise forms.ValidationError("You can only book tickets for today.")
        return selected_date
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        }

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter Password"})
    )