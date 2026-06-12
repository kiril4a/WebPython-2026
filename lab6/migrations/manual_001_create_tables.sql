CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    role VARCHAR(20) NOT NULL DEFAULT 'user'
);

CREATE TABLE doctor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    specialty VARCHAR(120) NOT NULL
);

CREATE TABLE patient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    user_id INTEGER UNIQUE,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE TABLE service (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    price INTEGER NOT NULL
);

CREATE TABLE appointment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    time DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed',
    FOREIGN KEY(doctor_id) REFERENCES doctor(id),
    FOREIGN KEY(patient_id) REFERENCES patient(id)
);

CREATE TABLE doctor_services (
    doctor_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    PRIMARY KEY (doctor_id, service_id),
    FOREIGN KEY(doctor_id) REFERENCES doctor(id),
    FOREIGN KEY(service_id) REFERENCES service(id)
);
