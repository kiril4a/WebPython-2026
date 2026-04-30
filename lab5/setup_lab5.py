import os
import shutil

base_dir = r"C:\Users\kril4a\Desktop\WebPython 2026\lab5\clinic"

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
    doctor = models.ForeignKey(Doctor, null=True, on_delete=models.CASCADE, verbose_name="Лікар")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Пацієнт")
    time = models.DateTimeField(null=True, verbose_name="Час прийому")

    def __str__(self):
        return f"{self.doctor} - {self.patient} - {self.time}"
"""

forms_code = """from django import forms
from .models import Patient
import re
from django.core.exceptions import ValidationError

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
"""

views_code = """from django.shortcuts import render, redirect
from .models import Doctor, Patient, Appointment
from .forms import PatientForm

def index(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = PatientForm()
        
    appointments = Appointment.objects.all().order_by('-time')
    patients = Patient.objects.all().order_by('-id')
    
    return render(request, 'clinic/index.html', {
        'appointments': appointments,
        'patients': patients,
        'form': form
    })
"""

html_code = """<!DOCTYPE html>
<html>
<head>
    <title>Стоматологічний кабінет (Lab 5)</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .panel { background: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
        .errorlist { color: red; font-weight: bold; list-style-type: none; padding: 0; }
        .form-control { margin-bottom: 10px; padding: 5px; width: 250px; }
        button { padding: 8px 15px; background: green; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background: darkgreen; }
    </style>
</head>
<body>
    <h1>Стоматологічний кабінет (ЛБ 5 — Django Forms & Validation)</h1>
    
    <div class="panel">
        {% if user.is_authenticated %}
            {% if user.is_superuser %}
                <p>Роль: <b>Адміністратор</b> ({{ user.username }})</p>
                <a href="/admin/clinic/" style="padding: 10px; background: blue; color: white; text-decoration: none; border-radius: 3px;">➤ Перейти в Адмін-панель (Структура/Лікарі/Записи)</a>
            {% else %}
                <p>Роль: Користувач системи ({{ user.username }})</p>
            {% endif %}
            <br><p><a href="/admin/logout/?next=/">Вийти</a></p>
        {% else %}
            <p>Роль: <b>Гість</b>. Ви можете тільки переглядати розклад та реєструвати пацієнтів.</p>
            <a href="/admin/" style="padding: 10px; background: blue; color: white; text-decoration: none; border-radius: 3px;">Увійти як Адміністратор</a>
        {% endif %}
    </div>

    <div style="display: flex; gap: 40px;">
        <div>
            <h2>Додати нового пацієнта (Django Forms)</h2>
            <form method="POST" class="panel" style="background: #e8f4f8;">
                {% csrf_token %}
                {{ form.non_field_errors }}
                {% for field in form %}
                    <div>
                        {{ field.label_tag }}<br>
                        {{ field }}
                        {{ field.errors }}
                    </div>
                {% endfor %}
                <br>
                <button type="submit">Додати пацієнта</button>
            </form>

            <h3>Список пацієнтів бази:</h3>
            <ul>
            {% for p in patients %}
                <li>{{ p.name }} ({{ p.phone }})</li>
            {% empty %}
                <li>Пацієнтів немає.</li>
            {% endfor %}
            </ul>
        </div>

        <div>
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
        </div>
    </div>
</body>
</html>
"""

admin_code = """from django.contrib import admin
from .models import Doctor, Patient, Appointment

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
"""

with open(os.path.join(base_dir, 'models.py'), 'w', encoding='utf-8') as f:
    f.write(models_code)
with open(os.path.join(base_dir, 'forms.py'), 'w', encoding='utf-8') as f:
    f.write(forms_code)
with open(os.path.join(base_dir, 'views.py'), 'w', encoding='utf-8') as f:
    f.write(views_code)
with open(os.path.join(base_dir, 'admin.py'), 'w', encoding='utf-8') as f:
    f.write(admin_code)

os.makedirs(os.path.join(base_dir, 'templates', 'clinic'), exist_ok=True)
with open(os.path.join(base_dir, 'templates', 'clinic', 'index.html'), 'w', encoding='utf-8') as f:
    f.write(html_code)

# Drop old db to avoid migration conflicts due to changed models
db_path = r"C:\Users\kril4a\Desktop\WebPython 2026\lab5\db.sqlite3"
if os.path.exists(db_path):
    os.remove(db_path)
try:
    shutil.rmtree(r"C:\Users\kril4a\Desktop\WebPython 2026\lab5\clinic\migrations")
except: pass

print("Lab 5 updated!")
