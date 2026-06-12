from functools import wraps

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..forms import AppointmentForm, DoctorForm, PatientForm, UserForm
from ..main.routes import fill_appointment_choices
from ..models import Appointment, Doctor, Patient, Service, User


admin_bp = Blueprint("admin", __name__)


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for("main.index"))
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route("/")
@admin_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        users=User.query.all(),
        patients=Patient.query.all(),
        doctors=Doctor.query.all(),
        services=Service.query.all(),
        appointments=Appointment.query.order_by(Appointment.time.desc()).all(),
    )


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/form.html", title="Редагувати акаунт", form=form)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/patients/create", methods=["GET", "POST"])
@admin_required
def create_patient():
    form = PatientForm()
    if form.validate_on_submit():
        db.session.add(Patient(name=form.name.data, phone=form.phone.data))
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/form.html", title="Додати пацієнта", form=form)


@admin_bp.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        patient.name = form.name.data
        patient.phone = form.phone.data
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/form.html", title="Редагувати пацієнта", form=form)


@admin_bp.route("/patients/<int:patient_id>/delete", methods=["POST"])
@admin_required
def delete_patient(patient_id):
    db.session.delete(Patient.query.get_or_404(patient_id))
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/doctors/create", methods=["GET", "POST"])
@admin_required
def create_doctor():
    form = DoctorForm()
    if form.validate_on_submit():
        db.session.add(Doctor(name=form.name.data, specialty=form.specialty.data))
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/form.html", title="Додати лікаря", form=form)


@admin_bp.route("/doctors/<int:doctor_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    form = DoctorForm(obj=doctor)
    if form.validate_on_submit():
        doctor.name = form.name.data
        doctor.specialty = form.specialty.data
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/form.html", title="Редагувати лікаря", form=form)


@admin_bp.route("/doctors/<int:doctor_id>/delete", methods=["POST"])
@admin_required
def delete_doctor(doctor_id):
    db.session.delete(Doctor.query.get_or_404(doctor_id))
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/appointments/create", methods=["GET", "POST"])
@admin_required
def create_appointment():
    form = AppointmentForm()
    fill_appointment_choices(form)
    if form.validate_on_submit():
        db.session.add(Appointment(doctor_id=form.doctor_id.data, patient_id=form.patient_id.data, time=form.time.data))
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/form.html", title="Призначити візит", form=form)


@admin_bp.route("/appointments/<int:appointment_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    form = AppointmentForm(obj=appointment)
    form.appointment_id = appointment.id
    fill_appointment_choices(form)
    if form.validate_on_submit():
        appointment.doctor_id = form.doctor_id.data
        appointment.patient_id = form.patient_id.data
        appointment.time = form.time.data
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/form.html", title="Редагувати візит", form=form)


@admin_bp.route("/appointments/<int:appointment_id>/delete", methods=["POST"])
@admin_required
def delete_appointment(appointment_id):
    db.session.delete(Appointment.query.get_or_404(appointment_id))
    db.session.commit()
    return redirect(url_for("admin.dashboard"))
