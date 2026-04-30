from django.shortcuts import render
from .models import Doctor, Patient, Appointment

def index(request):
    appointments = Appointment.objects.all().order_by('-time')
    return render(request, 'clinic/index.html', {'appointments': appointments})
