from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..forms import AppointmentForm
from ..models import Appointment, Doctor, Patient, Service


main_bp = Blueprint("main", __name__)


def fill_appointment_choices(form, only_current_patient=False):
    form.doctor_id.choices = [(doctor.id, f"{doctor.name} ({doctor.specialty})") for doctor in Doctor.query.all()]
    if only_current_patient and current_user.patient:
        form.patient_id.choices = [(current_user.patient.id, current_user.patient.name)]
    else:
        form.patient_id.choices = [(patient.id, patient.name) for patient in Patient.query.all()]


@main_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = AppointmentForm()
    fill_appointment_choices(form, only_current_patient=not current_user.is_admin)

    if form.validate_on_submit():
        patient_id = form.patient_id.data
        if not current_user.is_admin:
            patient_id = current_user.patient.id
        appointment = Appointment(
            doctor_id=form.doctor_id.data,
            patient_id=patient_id,
            time=form.time.data,
            status="confirmed",
        )
        db.session.add(appointment)
        db.session.commit()
        return redirect(url_for("main.index"))

    if current_user.is_admin:
        appointments = Appointment.query.order_by(Appointment.time.desc()).all()
        patients = Patient.query.all()
    else:
        appointments = Appointment.query.filter_by(patient_id=current_user.patient.id).order_by(Appointment.time.desc()).all()
        patients = [current_user.patient]

    return render_template(
        "main/index.html",
        form=form,
        appointments=appointments,
        patients=patients,
        doctors=Doctor.query.all(),
        services=Service.query.all(),
    )
