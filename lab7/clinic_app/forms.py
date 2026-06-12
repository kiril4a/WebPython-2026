from wtforms import DateTimeLocalField, EmailField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError
from flask_wtf import FlaskForm

from .models import Appointment, User


class LoginForm(FlaskForm):
    username = StringField("Логін", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Увійти")


class RegisterForm(FlaskForm):
    username = StringField("Логін", validators=[DataRequired(), Length(min=3, max=50)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=4)])
    name = StringField("ПІБ пацієнта", validators=[DataRequired()])
    phone = StringField("Телефон", validators=[DataRequired(), Regexp(r"^\+\d{10,15}$")])
    submit = SubmitField("Зареєструватися")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Такий логін уже зайнятий.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Такий email уже використовується.")


class UserForm(FlaskForm):
    username = StringField("Логін", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    role = SelectField("Роль", choices=[("user", "Користувач"), ("admin", "Адміністратор")])
    password = PasswordField("Новий пароль")
    submit = SubmitField("Зберегти акаунт")


class PatientForm(FlaskForm):
    name = StringField("ПІБ пацієнта", validators=[DataRequired()])
    phone = StringField("Телефон", validators=[DataRequired(), Regexp(r"^\+\d{10,15}$")])
    submit = SubmitField("Зберегти пацієнта")


class DoctorForm(FlaskForm):
    name = StringField("ПІБ лікаря", validators=[DataRequired()])
    specialty = StringField("Спеціальність", validators=[DataRequired()])
    submit = SubmitField("Зберегти лікаря")


class AppointmentForm(FlaskForm):
    doctor_id = SelectField("Лікар", coerce=int, validators=[DataRequired()])
    patient_id = SelectField("Пацієнт", coerce=int, validators=[DataRequired()])
    time = DateTimeLocalField("Час прийому", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    submit = SubmitField("Зберегти візит")

    def validate_time(self, field):
        appointment_id = getattr(self, "appointment_id", None)
        query = Appointment.query.filter_by(doctor_id=self.doctor_id.data, time=field.data)
        if appointment_id:
            query = query.filter(Appointment.id != appointment_id)
        if query.first():
            raise ValidationError("Обраний лікар уже зайнятий у цей час.")


class MailForm(FlaskForm):
    recipient = EmailField("Одержувач", validators=[DataRequired(), Email()])
    subject = StringField("Тема", validators=[DataRequired()])
    body = StringField("Текст листа", validators=[DataRequired()])
    submit = SubmitField("Надіслати")
