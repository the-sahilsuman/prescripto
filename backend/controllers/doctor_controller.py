import os

from bson import ObjectId
from passlib.context import CryptContext
from middlewares.auth import create_access_token, create_refresh_token

from config.mongodb import get_db
from utils import serialize

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Change Availability ───────────────────────────────────────────────────────

async def change_availability(doc_id: str):
    db = get_db()
    doctor = await db.doctors.find_one({"_id": ObjectId(doc_id)})
    if not doctor:
        return {"success": False, "message": "Doctor not found"}
    await db.doctors.update_one(
        {"_id": ObjectId(doc_id)},
        {"$set": {"available": not doctor.get("available", True)}},
    )
    return {"success": True, "message": "Availability Changed"}


# ── Doctor List (public) ──────────────────────────────────────────────────────

async def doctor_list():
    db = get_db()
    doctors = []
    async for doc in db.doctors.find({}, {"email": 0, "password": 0}):
        doctors.append(serialize(doc))
    return {"success": True, "doctors": doctors}


# ── Doctor Login ──────────────────────────────────────────────────────────────

async def login_doctor(email: str, password: str):
    db = get_db()

    doctor = await db.doctors.find_one({"email": email})
    if not doctor:
        return {"success": False, "message": "Invalid Credentials"}

    if pwd_context.verify(password, doctor["password"]):
        doc_id        = str(doctor["_id"])
        access_token  = create_access_token(sub=doc_id,  role="doctor")
        refresh_token = create_refresh_token(sub=doc_id, role="doctor")

        await db.refresh_tokens.insert_one({"token": refresh_token, "role": "doctor", "sub": doc_id})

        return {"success": True, "token": access_token, "refreshToken": refresh_token}

    return {"success": False, "message": "Invalid Credentials"}


# ── Appointments for Doctor ───────────────────────────────────────────────────

async def appointments_doctor(doc_id: str):
    db = get_db()
    appointments = []
    async for appt in db.appointments.find({"docId": doc_id}):
        appointments.append(serialize(appt))
    return {"success": True, "appointments": appointments}


# ── Complete Appointment ──────────────────────────────────────────────────────

async def appointment_completed(doc_id: str, appointment_id: str):
    db = get_db()
    appt = await db.appointments.find_one({"_id": ObjectId(appointment_id)})

    if appt and appt.get("docId") == doc_id:
        await db.appointments.update_one(
            {"_id": ObjectId(appointment_id)}, {"$set": {"isCompleted": True}}
        )
        return {"success": True, "message": "Appointment Completed"}

    return {"success": False, "message": "Mark Failed"}


# ── Cancel Appointment ────────────────────────────────────────────────────────

async def appointment_cancel(doc_id: str, appointment_id: str):
    db = get_db()
    appt = await db.appointments.find_one({"_id": ObjectId(appointment_id)})

    if appt and appt.get("docId") == doc_id:
        await db.appointments.update_one(
            {"_id": ObjectId(appointment_id)}, {"$set": {"cancelled": True}}
        )
        return {"success": True, "message": "Appointment Cancelled"}

    return {"success": False, "message": "Cancellation Failed"}


# ── Doctor Dashboard ──────────────────────────────────────────────────────────

async def doctor_dashboard(doc_id: str):
    db = get_db()
    all_appts = []
    async for appt in db.appointments.find({"docId": doc_id}):
        all_appts.append(serialize(appt))

    earnings = sum(
        a["amount"] for a in all_appts if a.get("isCompleted") or a.get("payment")
    )
    patients = list({a["userId"] for a in all_appts})

    dash_data = {
        "earnings": earnings,
        "appointments": len(all_appts),
        "patients": len(patients),
        "latestAppointments": list(reversed(all_appts))[:5],
    }
    return {"success": True, "dashData": dash_data}


# ── Doctor Profile ────────────────────────────────────────────────────────────

async def doctor_profile(doc_id: str):
    db = get_db()
    doctor = await db.doctors.find_one({"_id": ObjectId(doc_id)}, {"password": 0})
    if not doctor:
        return {"success": False, "message": "Doctor not found"}
    return {"success": True, "profileData": serialize(doctor)}


# ── Update Doctor Profile ─────────────────────────────────────────────────────

async def update_doctor_profile(doc_id: str, fees: float, address: dict, available: bool):
    db = get_db()
    await db.doctors.update_one(
        {"_id": ObjectId(doc_id)},
        {"$set": {"fees": fees, "address": address, "available": available}},
    )
    return {"success": True, "message": "Profile Updated"}
