from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from bson.objectid import ObjectId
import re

app = FastAPI(
    title="Dental Clinic API",
    description="RESTful API web application for dental clinic patients with MongoDB",
    version="1.0.0"
)
templates = Jinja2Templates(directory="templates")

client = MongoClient("mongodb://localhost:27017/")
db = client.dental_clinic
patients_collection = db.patients
doctors_collection = db.doctors
appointments_collection = db.appointments

def validate_patient_data(name: str, phone: str):
    if any(char.isdigit() for char in name):
        return "PIB ne mozhe mistyty tsyfry."
    if not re.match(r"^\+\d{10,15}$", phone):
        return "Telefon maie pochynatysia z '+' i mistyty vid 10 do 15 tsyfr."
    return None

def get_patients():
    patients = []
    for patient in patients_collection.find():
        patient["id"] = str(patient["_id"])
        patients.append(patient)
    return patients

@app.get('/', response_class=HTMLResponse, summary="Read patients page")
def read_root(request: Request, role: str = 'user'):
    patients = get_patients()
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={'patients': patients, 'role': role}
    )

@app.get('/patient/{id}', summary="Read patient")
def read_patient(id: str):
    try:
        patient = patients_collection.find_one({"_id": ObjectId(id)})
    except:
        patient = None

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {"id": str(patient["_id"]), "name": patient["name"], "phone": patient["phone"]}

@app.post('/patient/add', summary="Create patient")
def add_patient(request: Request, name: str = Form(...), phone: str = Form(...)):
    error_msg = validate_patient_data(name, phone)

    if error_msg:
        patients = get_patients()
        return templates.TemplateResponse(
            request=request,
            name='index.html',
            context={'patients': patients, 'role': 'admin', 'error': error_msg}
        )

    patients_collection.insert_one({"name": name, "phone": phone})
    return RedirectResponse(url='/?role=admin', status_code=303)

@app.post('/patient/update/{id}', summary="Update patient")
def update_patient(id: str, request: Request, name: str = Form(...), phone: str = Form(...)):
    error_msg = validate_patient_data(name, phone)

    if error_msg:
        patients = get_patients()
        return templates.TemplateResponse(
            request=request,
            name='index.html',
            context={'patients': patients, 'role': 'admin', 'error': error_msg}
        )

    try:
        result = patients_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": name, "phone": phone}}
        )
    except:
        result = None

    if not result or result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    return RedirectResponse(url='/?role=admin', status_code=303)

@app.post('/patient/delete/{id}', summary="Delete patient")
def delete_patient(id: str):
    try:
        patients_collection.delete_one({"_id": ObjectId(id)})
    except:
        pass
    return RedirectResponse(url='/?role=admin', status_code=303)
