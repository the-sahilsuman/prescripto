import os
import json
import time
import tempfile

import cloudinary.uploader
from bson import ObjectId
from email_validator import validate_email, EmailNotValidError
from fastapi import UploadFile
from passlib.context import CryptContext
from middlewares.auth import create_access_token, create_refresh_token

from config.mongodb import get_db
from utils import serialize

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Add Doctor ────────────────────────────────────────────────────────────────

async def add_doctor(
    name, email, password, speciality, degree, experience, about, fees, address, image: UploadFile
):
    db = get_db()

    if not all([name, email, password, speciality, degree, experience, about, fees, address]):
        return {"success": False, "message": "Missing Details"}

    try:
        validate_email(email)
    except EmailNotValidError:
        return {"success": False, "message": "Please enter a valid Email"}

    if len(password) < 8:
        return {"success": False, "message": "Please enter a strong password"}

    hashed_password = pwd_context.hash(password)

    contents = await image.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=image.filename) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    upload_result = cloudinary.uploader.upload(tmp_path, resource_type="image")
    img_url = upload_result["secure_url"]

    doctor_data = {
        "name": name,
        "email": email,
        "image": img_url,
        "password": hashed_password,
        "speciality": speciality,
        "degree": degree,
        "experience": experience,
        "fees": float(fees),
        "about": about,
        "address": json.loads(address),
        "available": True,
        "slots_booked": {},
        "date": int(time.time() * 1000),
    }

    await db.doctors.insert_one(doctor_data)
    return {"success": True, "message": "Doctor Added"}


# ── Admin Login ───────────────────────────────────────────────────────────────

async def login_admin(email: str, password: str):
    admin_email    = os.getenv("ADMIN_EMAIL", "")
    admin_password = os.getenv("ADMIN_PASSWORD", "")

    if email == admin_email and password == admin_password:
        sentinel = email + password          # existing sentinel value kept as sub
        access_token  = create_access_token(sub=sentinel,  role="admin")
        refresh_token = create_refresh_token(sub=sentinel, role="admin")

        # Persist refresh token so it can be validated and rotated
        db = get_db()
        await db.refresh_tokens.insert_one({"token": refresh_token, "role": "admin", "sub": sentinel})

        return {"success": True, "token": access_token, "refreshToken": refresh_token}

    return {"success": False, "message": "Invalid Credentials"}


# ── All Doctors ───────────────────────────────────────────────────────────────

async def all_doctors():
    db = get_db()
    doctors = []
    async for doc in db.doctors.find({}, {"password": 0}):
        doctors.append(serialize(doc))
    return {"success": True, "doctors": doctors}


# ── Appointments (Admin) ──────────────────────────────────────────────────────

async def appointments_admin():
    db = get_db()
    appointments = []
    async for appt in db.appointments.find({}):
        appointments.append(serialize(appt))
    return {"success": True, "appointments": appointments}


# ── Cancel Appointment (Admin) ────────────────────────────────────────────────

async def appointment_cancel(appointment_id: str):
    db = get_db()

    appt = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
    if not appt:
        return {"success": False, "message": "Appointment not found"}

    await db.appointments.update_one(
        {"_id": ObjectId(appointment_id)}, {"$set": {"cancelled": True}}
    )

    doc_id = appt["docId"]
    slot_date = appt["slotDate"]
    slot_time = appt["slotTime"]

    doctor = await db.doctors.find_one({"_id": ObjectId(doc_id)})
    slots_booked = doctor.get("slots_booked", {})
    if slot_date in slots_booked:
        slots_booked[slot_date] = [s for s in slots_booked[slot_date] if s != slot_time]

    await db.doctors.update_one(
        {"_id": ObjectId(doc_id)}, {"$set": {"slots_booked": slots_booked}}
    )

    return {"success": True, "message": "Appointment Cancelled"}


# ── Admin Dashboard ───────────────────────────────────────────────────────────

async def admin_dashboard():
    db = get_db()

    doctors = await db.doctors.count_documents({})
    users = await db.users.count_documents({})
    all_appts = []
    async for appt in db.appointments.find({}):
        all_appts.append(serialize(appt))

    latest = list(reversed(all_appts))[:5]

    dash_data = {
        "doctors": doctors,
        "appointments": len(all_appts),
        "patients": users,
        "latestAppointments": latest,
    }

    return {"success": True, "dashData": dash_data}
