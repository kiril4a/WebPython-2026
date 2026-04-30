from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Doctor, Patient, Appointment
from .forms import PatientForm, AppointmentForm

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'clinic/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('index')

def index(request):
    if request.method == 'POST':
        if 'patient_submit' in request.POST:
            p_form = PatientForm(request.POST)
            a_form = AppointmentForm()
            if p_form.is_valid():
                p_form.save()
                return redirect('index')
        elif 'appointment_submit' in request.POST:
            p_form = PatientForm()
            a_form = AppointmentForm(request.POST)
            if a_form.is_valid():
                a_form.save()
                return redirect('index')
    else:
        p_form = PatientForm()
        a_form = AppointmentForm()
        
    appointments = Appointment.objects.all().order_by('-time')
    patients = Patient.objects.all().order_by('-id')
    
    is_doctor = hasattr(request.user, 'doctor') if request.user.is_authenticated else False
    
    return render(request, 'clinic/index.html', {
        'appointments': appointments,
        'patients': patients,
        'form': p_form,
        'a_form': a_form,
        'is_doctor': is_doctor
    })

def confirm_appointment(request, pk):
    if request.user.is_authenticated:
        try:
            appt = Appointment.objects.get(pk=pk)
            if hasattr(request.user, 'doctor'):
                appt.doctor = request.user.doctor
                appt.status = 'confirmed'
                appt.save()
            elif request.user.is_superuser:
                appt.status = 'confirmed'
                appt.save()
        except Appointment.DoesNotExist:
            pass
    return redirect('index')
