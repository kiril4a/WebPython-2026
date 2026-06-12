import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Appointment, Doctor, Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["name", "phone"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Іван Іванов", "class": "form-control"}),
            "phone": forms.TextInput(attrs={"placeholder": "+380671234567", "class": "form-control"}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "")
        if any(char.isdigit() for char in name):
            raise ValidationError("ПІБ не може містити цифри.")
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if not re.match(r"^\+\d{10,15}$", phone):
            raise ValidationError("Телефон має містити код країни, починатися з '+' і містити від 10 до 15 цифр.")
        return phone


class UserAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["doctor", "time"]
        widgets = {
            "time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        time = cleaned_data.get("time")
        if doctor and time and Appointment.objects.filter(doctor=doctor, time=time).exists():
            raise ValidationError("Обраний лікар уже зайнятий у цей час.")
        return cleaned_data


class AdminAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "time"]
        widgets = {
            "time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctor")
        time = cleaned_data.get("time")
        if doctor and time and Appointment.objects.filter(doctor=doctor, time=time).exists():
            raise ValidationError("Обраний лікар уже зайнятий у цей час.")
        return cleaned_data
