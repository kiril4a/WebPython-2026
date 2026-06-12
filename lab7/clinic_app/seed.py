from datetime import datetime

from .extensions import db
from .models import Appointment, Doctor, Patient, Service, User


def create_user(username, email, password, role="user"):
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    return user


def create_demo_data():
    if User.query.first():
        return

    admin = create_user("admin", "admin@example.com", "admin", "admin")
    petrenko_user = create_user("petrenko", "petrenko@example.com", "1234")
    shevchenko_user = create_user("shevchenko", "shevchenko@example.com", "1234")

    doctor1 = Doctor(name="Іваненко Іван", specialty="Терапевт")
    doctor2 = Doctor(name="Коваленко Марія", specialty="Ортодонт")
    service1 = Service(name="Консультація", price=400)
    service2 = Service(name="Лікування карієсу", price=1200)
    service3 = Service(name="Ортодонтичний огляд", price=700)
    doctor1.services.extend([service1, service2])
    doctor2.services.extend([service1, service3])

    patient1 = Patient(name="Петренко Олена", phone="+380671234567", user=petrenko_user)
    patient2 = Patient(name="Шевченко Андрій", phone="+380681234567", user=shevchenko_user)

    db.session.add_all([admin, petrenko_user, shevchenko_user, doctor1, doctor2, patient1, patient2])
    db.session.commit()

    db.session.add_all(
        [
            Appointment(doctor=doctor1, patient=patient1, time=datetime(2026, 6, 10, 9, 0)),
            Appointment(doctor=doctor2, patient=patient2, time=datetime(2026, 6, 10, 11, 30)),
        ]
    )
    db.session.commit()
