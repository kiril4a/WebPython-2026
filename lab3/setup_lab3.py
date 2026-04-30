import os
import shutil

os.makedirs(r'C:\Users\kril4a\Desktop\WebPython 2026\lab3\templates', exist_ok=True)
shutil.copy(r'C:\Users\kril4a\Desktop\WebPython 2026\lab1\templates\index.html', r'C:\Users\kril4a\Desktop\WebPython 2026\lab3\templates\index.html')

code = """from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from bson.objectid import ObjectId
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Підключення до локальної MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.dental_clinic
patients_collection = db.patients
doctors_collection = db.doctors
appointments_collection = db.appointments

@app.get('/', response_class=HTMLResponse)
def read_root(request: Request, role: str = 'user'):
    patients = []
    # Конвертуємо _id з MongoDB в звичайний рядок для HTML
    for p in patients_collection.find():
        p["id"] = str(p["_id"])
        patients.append(p)
    return templates.TemplateResponse(request=request, name='index.html', context={'patients': patients, 'role': role})

@app.post('/patient/add')
def add_patient(request: Request, name: str = Form(...), phone: str = Form(...)):
    error_msg = None
    if any(char.isdigit() for char in name):
        error_msg = "ПІБ не може містити цифри."
    elif not re.match(r"^\+\d{10,15}$", phone):
        error_msg = "Телефон має містити код країни (починатися з '+') і загалом від 10 до 15 цифр."
    
    if error_msg:
        patients = []
        for p in patients_collection.find():
            p["id"] = str(p["_id"])
            patients.append(p)
        return templates.TemplateResponse(request=request, name='index.html', context={'patients': patients, 'role': 'admin', 'error': error_msg})
    
    patients_collection.insert_one({"name": name, "phone": phone})
    return RedirectResponse(url='/?role=admin', status_code=303)

@app.post('/patient/delete/{id}')
def delete_patient(id: str):
    try:
        patients_collection.delete_one({"_id": ObjectId(id)})
    except:
        pass
    return RedirectResponse(url='/?role=admin', status_code=303)
"""

with open(r'C:\Users\kril4a\Desktop\WebPython 2026\lab3\main.py', 'w', encoding='utf-8') as f:
    f.write(code)
