from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Акаунт лікаря")
    name = models.CharField(max_length=200, verbose_name="ПІБ лікаря")
    specialty = models.CharField(max_length=100, verbose_name="Спеціальність")

    def __str__(self):
        return f"{self.name} ({self.specialty})"

class Patient(models.Model):
    name = models.CharField(max_length=200, verbose_name="ПІБ пацієнта")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    def __str__(self):
        return f"{self.name}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує'),
        ('confirmed', 'Підтверджено'),
    ]
    doctor = models.ForeignKey(Doctor, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Лікар")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Пацієнт")
    time = models.DateTimeField(null=True, verbose_name="Час прийому")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")

    def __str__(self):
        return f"{self.doctor} - {self.patient} - {self.time}"
