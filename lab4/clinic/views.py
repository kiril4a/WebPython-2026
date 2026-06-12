from django.shortcuts import render


APPOINTMENTS = [
    {
        "time": "10.06.2026 09:00",
        "doctor": "Ivanenko Ivan",
        "specialty": "Terapevt",
        "patient": "Petrenko Olena",
    },
    {
        "time": "10.06.2026 11:30",
        "doctor": "Kovalenko Mariia",
        "specialty": "Ortodont",
        "patient": "Shevchenko Andrii",
    },
    {
        "time": "11.06.2026 14:00",
        "doctor": "Bondar Serhii",
        "specialty": "Khirurh",
        "patient": "Melnyk Nataliia",
    },
]

PATIENTS = [
    "Petrenko Olena",
    "Shevchenko Andrii",
    "Melnyk Nataliia",
]


def index(request):
    role = request.GET.get("role", "user")
    current_patient = request.GET.get("patient", PATIENTS[0])
    if current_patient not in PATIENTS:
        current_patient = PATIENTS[0]

    if role == "admin":
        visible_appointments = APPOINTMENTS
    else:
        visible_appointments = [
            appointment for appointment in APPOINTMENTS
            if appointment["patient"] == current_patient
        ]

    return render(
        request,
        "clinic/index.html",
        {
            "appointments": APPOINTMENTS,
            "visible_appointments": visible_appointments,
            "patients": PATIENTS,
            "current_patient": current_patient,
            "role": role,
        }
    )
