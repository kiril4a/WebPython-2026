from django import forms
from .models import Patient, Appointment
import re
from django.core.exceptions import ValidationError

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'time']
        widgets = {
            'time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Іван Іванов', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': '+380671234567', 'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if any(char.isdigit() for char in name):
            raise ValidationError("ПІБ не може містити цифри.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r"^\+\d{10,15}$", phone):
            raise ValidationError("Телефон має містити код країни (починатися з '+') і загалом від 10 до 15 цифр.")
        return phone
