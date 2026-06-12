from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AdminAppointmentForm, PatientForm, UserAppointmentForm
from .models import Appointment, Doctor, Patient


def ensure_demo_data():
    admin, _ = User.objects.get_or_create(username="admin", defaults={"is_staff": True, "is_superuser": True})
    if not admin.is_staff or not admin.is_superuser:
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

    doctor_user, _ = User.objects.get_or_create(username="doctor")
    doctor, _ = Doctor.objects.get_or_create(
        user=doctor_user,
        defaults={"name": "Іваненко Іван", "specialty": "Терапевт"}
    )

    second_doctor_user, _ = User.objects.get_or_create(username="ortodont")
    Doctor.objects.get_or_create(
        user=second_doctor_user,
        defaults={"name": "Коваленко Марія", "specialty": "Ортодонт"}
    )

    patient_user, _ = User.objects.get_or_create(username="patient")
    patient, _ = Patient.objects.get_or_create(
        user=patient_user,
        defaults={"name": "Петренко Олена", "phone": "+380671234567"}
    )

    second_patient_user, _ = User.objects.get_or_create(username="patient2")
    Patient.objects.get_or_create(
        user=second_patient_user,
        defaults={"name": "Шевченко Андрій", "phone": "+380681234567"}
    )

    return {
        "admin": admin,
        "doctor": doctor_user,
        "patient": patient_user,
        "patient2": second_patient_user,
    }


def demo_login(request, username):
    users = ensure_demo_data()
    user = users.get(username)
    if user:
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return redirect("index")


def custom_login(request):
    ensure_demo_data()
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
    else:
        form = AuthenticationForm()
    return render(request, "clinic/login.html", {"form": form})


def custom_logout(request):
    logout(request)
    return redirect("index")


def get_current_patient(user):
    if user.is_authenticated:
        try:
            return user.patient
        except Patient.DoesNotExist:
            return None
    return None


def index(request):
    ensure_demo_data()
    current_patient = get_current_patient(request.user)
    is_doctor = hasattr(request.user, "doctor") if request.user.is_authenticated else False
    is_admin = request.user.is_authenticated and request.user.is_superuser

    patient_form = PatientForm()
    user_appointment_form = UserAppointmentForm()
    admin_appointment_form = AdminAppointmentForm()

    if request.method == "POST":
        if "patient_submit" in request.POST and is_admin:
            patient_form = PatientForm(request.POST)
            if patient_form.is_valid():
                patient_form.save()
                return redirect("index")

        elif "user_appointment_submit" in request.POST and current_patient:
            user_appointment_form = UserAppointmentForm(request.POST)
            if user_appointment_form.is_valid():
                appointment = user_appointment_form.save(commit=False)
                appointment.patient = current_patient
                appointment.status = "confirmed"
                appointment.save()
                return redirect("index")

        elif "admin_appointment_submit" in request.POST and is_admin:
            admin_appointment_form = AdminAppointmentForm(request.POST)
            if admin_appointment_form.is_valid():
                appointment = admin_appointment_form.save(commit=False)
                appointment.status = "confirmed"
                appointment.save()
                return redirect("index")

    if is_admin or is_doctor:
        appointments = Appointment.objects.all().order_by("-time")
        patients = Patient.objects.all().order_by("-id")
    elif current_patient:
        appointments = Appointment.objects.filter(patient=current_patient).order_by("-time")
        patients = Patient.objects.filter(pk=current_patient.pk)
    else:
        appointments = Appointment.objects.none()
        patients = Patient.objects.none()

    return render(request, "clinic/index.html", {
        "appointments": appointments,
        "patients": patients,
        "patient_form": patient_form,
        "user_appointment_form": user_appointment_form,
        "admin_appointment_form": admin_appointment_form,
        "current_patient": current_patient,
        "is_doctor": is_doctor,
        "is_admin": is_admin,
    })


def confirm_appointment(request, pk):
    if request.user.is_authenticated:
        appointment = get_object_or_404(Appointment, pk=pk)
        if hasattr(request.user, "doctor"):
            if not Appointment.objects.filter(doctor=request.user.doctor, time=appointment.time).exclude(pk=appointment.pk).exists():
                appointment.doctor = request.user.doctor
                appointment.status = "confirmed"
                appointment.save()
        elif request.user.is_superuser:
            appointment.status = "confirmed"
            appointment.save()
    return redirect("index")
