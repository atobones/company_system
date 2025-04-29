from django import forms
from .models import Driver, Car, License

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['full_name', 'phone', 'email', 'bank_account', 'home_address', 'company']


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['registration_number', 'insurance_expiry', 'driver']  # 👈 добавлено поле driver

        widgets = {
            'insurance_expiry': forms.DateInput(attrs={'type': 'date'})
        }


class LicenseForm(forms.ModelForm):
    class Meta:
        model = License
        fields = ['registration_number', 'car', 'file']
