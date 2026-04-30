import os

base_dir = r'C:\Users\kril4a\Desktop\WebPython 2026\lab4'

# Cleanup stray files
for f in ['models.py', 'views.py']:
    try: os.remove(os.path.join(base_dir, f))
    except: pass

# 1. Update settings.py
settings_path = os.path.join(base_dir, 'config', 'settings.py')
with open(settings_path, 'r', encoding='utf-8') as f:
    settings = f.read()

if "'clinic'," not in settings and '"clinic",' not in settings:
    settings = settings.replace('INSTALLED_APPS = [', "INSTALLED_APPS = [\n    'clinic',")

with open(settings_path, 'w', encoding='utf-8') as f:
    f.write(settings)


models_code = """from django.db import models

class Doctor(models.Model):
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
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, verbose_name="Лікар")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Пацієнт")
    time = models.DateTimeField(verbose_name="Час прийому")

    def __str__(self):
        return f"{self.doctor} - {self.patient} - {self.time}"
"""
with open(os.path.join(base_dir, 'clinic', 'models.py'), 'w', encoding='utf-8') as f:
    f.write(models_code)

admin_code = """from django.contrib import admin
from .models import Doctor, Patient, Appointment

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
"""
with open(os.path.join(base_dir, 'clinic', 'admin.py'), 'w', encoding='utf-8') as f:
    f.write(admin_code)

config_urls = """from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clinic.urls')),
]
"""
with open(os.path.join(base_dir, 'config', 'urls.py'), 'w', encoding='utf-8') as f:
    f.write(config_urls)

clinic_urls = """from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
"""
with open(os.path.join(base_dir, 'clinic', 'urls.py'), 'w', encoding='utf-8') as f:
    f.write(clinic_urls)

views_code = """from django.shortcuts import render
from .models import Doctor, Patient, Appointment

def index(request):
    appointments = Appointment.objects.all().order_by('-time')
    return render(request, 'clinic/index.html', {'appointments': appointments})
"""
with open(os.path.join(base_dir, 'clinic', 'views.py'), 'w', encoding='utf-8') as f:
    f.write(views_code)


templates_dir = os.path.join(base_dir, 'clinic', 'templates', 'clinic')
os.makedirs(templates_dir, exist_ok=True)

html_code = """<!DOCTYPE html>
<html>
<head>
    <title>Стоматологічний кабінет (Lab 4)</title>
    <meta charset="utf-8">
</head>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h1>Стоматологічний кабінет (ЛБ 4 — Django Base)</h1>
    
    <div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
        {% if user.is_authenticated %}
            {% if user.is_superuser %}
                <p>Роль: <b>Адміністратор</b> ({{ user.username }})</p>
                <a href="/admin/clinic/" style="padding: 10px; background: blue; color: white; text-decoration: none; border-radius: 3px;">➤ Перейти в Адмін-панель для Додавання/Видалення/Зміни</a>
            {% else %}
                <p>Роль: Користувач системи ({{ user.username }})</p>
            {% endif %}
            <br><p><a href="/admin/logout/?next=/">Вийти</a></p>
        {% else %}
            <p>Роль: <b>Гість (Користувач)</b>. Ви можете тільки переглядати наявний розклад.</p>
            <a href="/admin/" style="padding: 10px; background: green; color: white; text-decoration: none; border-radius: 3px;">Увійти як Адміністратор</a>
        {% endif %}
    </div>

    <h2>Розклад прийомів:</h2>
    <ul>
    {% for appt in appointments %}
        <li>
            <b>{{ appt.time|date:"d.m.Y H:i" }}</b>: 
            Лікар <i>{{ appt.doctor.name }}</i> приймає пацієнта <i>{{ appt.patient.name }}</i>.
        </li>
    {% empty %}
        <li>Записів ще немає.</li>
    {% endfor %}
    </ul>
</body>
</html>
"""
with open(os.path.join(templates_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html_code)

print('Lab 4 files generated.')