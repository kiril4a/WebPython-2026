from datetime import datetime
import re

from flask import Flask, redirect, render_template, request, session, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Regexp, ValidationError


app = Flask(__name__)
app.config["SECRET_KEY"] = "lab6-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clinic_flask.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


doctor_services = db.Table(
    "doctor_services",
    db.Column("doctor_id", db.Integer, db.ForeignKey("doctor.id"), primary_key=True),
    db.Column("service_id", db.Integer, db.ForeignKey("service.id"), primary_key=True),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    patient = db.relationship("Patient", back_populates="user", uselist=False)


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(120), nullable=False)
    appointments = db.relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
    services = db.relationship("Service", secondary=doctor_services, back_populates="doctors")


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    user = db.relationship("User", back_populates="patient")
    appointments = db.relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    doctors = db.relationship("Doctor", secondary=doctor_services, back_populates="services")


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="confirmed")
    doctor = db.relationship("Doctor", back_populates="appointments")
    patient = db.relationship("Patient", back_populates="appointments")


class PatientForm(FlaskForm):
    name = StringField("ПІБ пацієнта", validators=[DataRequired()])
    phone = StringField(
        "Телефон",
        validators=[
            DataRequired(),
            Regexp(r"^\+\d{10,15}$", message="Телефон має починатися з '+' і містити від 10 до 15 цифр."),
        ],
    )
    submit = SubmitField("Зберегти пацієнта")

    def validate_name(self, field):
        if any(char.isdigit() for char in field.data):
            raise ValidationError("ПІБ не може містити цифри.")


class DoctorForm(FlaskForm):
    name = StringField("ПІБ лікаря", validators=[DataRequired()])
    specialty = StringField("Спеціальність", validators=[DataRequired()])
    submit = SubmitField("Зберегти лікаря")


class ServiceForm(FlaskForm):
    name = StringField("Назва послуги", validators=[DataRequired()])
    price = StringField("Ціна", validators=[DataRequired(), Regexp(r"^\d+$", message="Ціна має бути числом.")])
    submit = SubmitField("Зберегти послугу")


class AppointmentForm(FlaskForm):
    doctor_id = SelectField("Лікар", coerce=int, validators=[DataRequired()])
    patient_id = SelectField("Пацієнт", coerce=int, validators=[DataRequired()])
    time = DateTimeLocalField("Час прийому", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    submit = SubmitField("Зберегти візит")

    def validate_time(self, field):
        appointment_id = request.view_args.get("appointment_id") if request.view_args else None
        query = Appointment.query.filter_by(doctor_id=self.doctor_id.data, time=field.data)
        if appointment_id:
            query = query.filter(Appointment.id != appointment_id)
        if query.first():
            raise ValidationError("Обраний лікар уже зайнятий у цей час.")


def current_user():
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None


def is_admin():
    user = current_user()
    return user is not None and user.role == "admin"


def fill_appointment_choices(form, only_current_patient=False):
    form.doctor_id.choices = [(doctor.id, f"{doctor.name} ({doctor.specialty})") for doctor in Doctor.query.all()]
    if only_current_patient:
        user = current_user()
        form.patient_id.choices = [(user.patient.id, user.patient.name)] if user and user.patient else []
    else:
        form.patient_id.choices = [(patient.id, patient.name) for patient in Patient.query.all()]


def create_demo_data():
    if User.query.first():
        return

    admin = User(username="admin", role="admin")
    petrenko_user = User(username="petrenko", role="user")
    shevchenko_user = User(username="shevchenko", role="user")

    doctor1 = Doctor(name="Іваненко Іван", specialty="Терапевт")
    doctor2 = Doctor(name="Коваленко Марія", specialty="Ортодонт")
    doctor3 = Doctor(name="Бондар Сергій", specialty="Хірург")

    service1 = Service(name="Консультація", price=400)
    service2 = Service(name="Лікування карієсу", price=1200)
    service3 = Service(name="Ортодонтичний огляд", price=700)

    doctor1.services.extend([service1, service2])
    doctor2.services.extend([service1, service3])
    doctor3.services.append(service1)

    patient1 = Patient(name="Петренко Олена", phone="+380671234567", user=petrenko_user)
    patient2 = Patient(name="Шевченко Андрій", phone="+380681234567", user=shevchenko_user)

    db.session.add_all([admin, petrenko_user, shevchenko_user, doctor1, doctor2, doctor3, patient1, patient2])
    db.session.commit()

    db.session.add_all(
        [
            Appointment(doctor=doctor1, patient=patient1, time=datetime(2026, 6, 10, 9, 0)),
            Appointment(doctor=doctor2, patient=patient2, time=datetime(2026, 6, 10, 11, 30)),
        ]
    )
    db.session.commit()


@app.before_request
def prepare_database():
    db.create_all()
    create_demo_data()


@app.route("/")
def index():
    user = current_user()
    appointment_form = AppointmentForm()
    fill_appointment_choices(appointment_form, only_current_patient=user is not None and user.role == "user")

    if is_admin():
        patients = Patient.query.all()
        doctors = Doctor.query.all()
        services = Service.query.all()
        appointments = Appointment.query.order_by(Appointment.time.desc()).all()
    elif user and user.patient:
        patients = [user.patient]
        doctors = Doctor.query.all()
        services = Service.query.all()
        appointments = Appointment.query.filter_by(patient_id=user.patient.id).order_by(Appointment.time.desc()).all()
    else:
        patients = []
        doctors = Doctor.query.all()
        services = Service.query.all()
        appointments = []

    return render_template(
        "index.html",
        user=user,
        is_admin=is_admin(),
        patients=patients,
        doctors=doctors,
        services=services,
        appointments=appointments,
        appointment_form=appointment_form,
    )


@app.route("/login/<username>")
def login(username):
    user = User.query.filter_by(username=username).first()
    if user:
        session["user_id"] = user.id
        session["last_login_role"] = user.role
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/patients/create", methods=["GET", "POST"])
def create_patient():
    if not is_admin():
        return redirect(url_for("index"))
    form = PatientForm()
    if form.validate_on_submit():
        db.session.add(Patient(name=form.name.data, phone=form.phone.data))
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("form.html", title="Додати пацієнта", form=form)


@app.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
def edit_patient(patient_id):
    if not is_admin():
        return redirect(url_for("index"))
    patient = Patient.query.get_or_404(patient_id)
    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        patient.name = form.name.data
        patient.phone = form.phone.data
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("form.html", title="Редагувати пацієнта", form=form)


@app.route("/patients/<int:patient_id>/delete", methods=["POST"])
def delete_patient(patient_id):
    if is_admin():
        patient = Patient.query.get_or_404(patient_id)
        db.session.delete(patient)
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/doctors/create", methods=["GET", "POST"])
def create_doctor():
    if not is_admin():
        return redirect(url_for("index"))
    form = DoctorForm()
    if form.validate_on_submit():
        db.session.add(Doctor(name=form.name.data, specialty=form.specialty.data))
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("form.html", title="Додати лікаря", form=form)


@app.route("/doctors/<int:doctor_id>/edit", methods=["GET", "POST"])
def edit_doctor(doctor_id):
    if not is_admin():
        return redirect(url_for("index"))
    doctor = Doctor.query.get_or_404(doctor_id)
    form = DoctorForm(obj=doctor)
    if form.validate_on_submit():
        doctor.name = form.name.data
        doctor.specialty = form.specialty.data
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("form.html", title="Редагувати лікаря", form=form)


@app.route("/doctors/<int:doctor_id>/delete", methods=["POST"])
def delete_doctor(doctor_id):
    if is_admin():
        doctor = Doctor.query.get_or_404(doctor_id)
        db.session.delete(doctor)
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/services/create", methods=["GET", "POST"])
def create_service():
    if not is_admin():
        return redirect(url_for("index"))
    form = ServiceForm()
    if form.validate_on_submit():
        db.session.add(Service(name=form.name.data, price=int(form.price.data)))
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("form.html", title="Додати послугу", form=form)


@app.route("/services/<int:service_id>/edit", methods=["GET", "POST"])
def edit_service(service_id):
    if not is_admin():
        return redirect(url_for("index"))
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)
    if form.validate_on_submit():
        service.name = form.name.data
        service.price = int(form.price.data)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("form.html", title="Редагувати послугу", form=form)


@app.route("/services/<int:service_id>/delete", methods=["POST"])
def delete_service(service_id):
    if is_admin():
        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/appointments/create", methods=["GET", "POST"])
def create_appointment():
    user = current_user()
    if not user:
        return redirect(url_for("index"))
    form = AppointmentForm()
    fill_appointment_choices(form, only_current_patient=user.role == "user")
    if form.validate_on_submit():
        patient_id = form.patient_id.data
        if user.role == "user":
            patient_id = user.patient.id
        db.session.add(
            Appointment(
                doctor_id=form.doctor_id.data,
                patient_id=patient_id,
                time=form.time.data,
                status="confirmed",
            )
        )
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("form.html", title="Записатися на візит", form=form)


@app.route("/appointments/<int:appointment_id>/edit", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    if not is_admin():
        return redirect(url_for("index"))
    appointment = Appointment.query.get_or_404(appointment_id)
    form = AppointmentForm(obj=appointment)
    fill_appointment_choices(form)
    if form.validate_on_submit():
        appointment.doctor_id = form.doctor_id.data
        appointment.patient_id = form.patient_id.data
        appointment.time = form.time.data
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("form.html", title="Редагувати візит", form=form)


@app.route("/appointments/<int:appointment_id>/delete", methods=["POST"])
def delete_appointment(appointment_id):
    if is_admin():
        appointment = Appointment.query.get_or_404(appointment_id)
        db.session.delete(appointment)
        db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
