
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import datetime
import re

engine = create_engine('sqlite:///./clinic.db', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    specialty = Column(String)

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    patient_id = Column(Integer, ForeignKey('patients.id'))
    time = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory='templates')

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.get('/', response_class=HTMLResponse)
def read_root(request: Request, role: str = 'user', db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return templates.TemplateResponse(
        request=request, 
        name='index.html', 
        context={'patients': patients, 'role': role}
    )

@app.post('/patient/add')
def add_patient(request: Request, name: str = Form(...), phone: str = Form(...), db: Session = Depends(get_db)):
    error_msg = None
    if any(char.isdigit() for char in name):
        error_msg = "ПІБ не може містити цифри."
    elif not re.match(r"^\+\d{10,15}$", phone):
        error_msg = "Телефон має містити код країни (починатися з '+') і загалом від 10 до 15 цифр."

    if error_msg:
        patients = db.query(Patient).all()
        return templates.TemplateResponse(
            request=request, 
            name='index.html', 
            context={'patients': patients, 'role': 'admin', 'error': error_msg}
        )

    db.add(Patient(name=name, phone=phone))
    db.commit()
    return RedirectResponse(url='/?role=admin', status_code=303)

@app.post('/patient/delete/{id}')
def delete_patient(id: int, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.id == id).first()
    if p: db.delete(p); db.commit()
    return RedirectResponse(url='/?role=admin', status_code=303)
