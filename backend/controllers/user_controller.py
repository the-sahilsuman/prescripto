import os
import json
import tempfile
import time

import cloudinary.uploader
from bson import ObjectId
from email_validator import validate_email, EmailNotValidError
from fastapi import UploadFile
from passlib.context import CryptContext
from middlewares.auth import create_access_token, create_refresh_token

from config.mongodb import get_db
from utils import serialize

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Register User ─────────────────────────────────────────────────────────────

async def register_user(name: str, email: str, password: str):
    db = get_db()

    if not all([name, email, password]):
        return {"success": False, "message": "Missing Details"}

    try:
        validate_email(email)
    except EmailNotValidError:
        return {"success": False, "message": "Please Enter a Correct Email"}

    if len(password) < 8:
        return {"success": False, "message": "Please Enter a Strong Password"}

    hashed = pwd_context.hash(password)
    result = await db.users.insert_one({"name": name, "email": email, "password": hashed})
    user_id = str(result.inserted_id)

    access_token  = create_access_token(sub=user_id, role="user")
    refresh_token = create_refresh_token(sub=user_id, role="user")
    await db.refresh_tokens.insert_one({"token": refresh_token, "role": "user", "sub": user_id})

    return {"success": True, "token": access_token, "refreshToken": refresh_token}


# ── Login User ────────────────────────────────────────────────────────────────

async def login_user(email: str, password: str):
    db = get_db()

    user = await db.users.find_one({"email": email})
    if not user:
        return {"success": False, "message": "User doesn't Exist!"}

    if pwd_context.verify(password, user["password"]):
        user_id       = str(user["_id"])
        access_token  = create_access_token(sub=user_id, role="user")
        refresh_token = create_refresh_token(sub=user_id, role="user")
        await db.refresh_tokens.insert_one({"token": refresh_token, "role": "user", "sub": user_id})
        return {"success": True, "token": access_token, "refreshToken": refresh_token}

    return {"success": False, "message": "Invalid Credentials"}


# ── Get Profile ───────────────────────────────────────────────────────────────

async def get_profile(user_id: str):
    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if not user:
        return {"success": False, "message": "User not found"}
    return {"success": True, "userData": serialize(user)}


# ── Update Profile ────────────────────────────────────────────────────────────

async def update_profile(user_id, name, phone, dob, address, gender, img_file=None):
    db = get_db()

    if not all([name, phone, dob, gender]):
        return {"success": False, "message": "Data Missing"}

    update_fields = {
        "name": name,
        "phone": phone,
        "address": json.loads(address) if isinstance(address, str) else address,
        "dob": dob,
        "gender": gender,
    }

    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})

    if img_file:
        contents = await img_file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=img_file.filename) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        upload_result = cloudinary.uploader.upload(tmp_path, resource_type="image")
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"image": upload_result["secure_url"]}},
        )

    return {"success": True, "message": "Profile Updated Successfully"}


# ── Book Appointment ──────────────────────────────────────────────────────────

async def book_appointment(user_id: str, doc_id: str, slot_date: str, slot_time: str):
    db = get_db()

    doctor = await db.doctors.find_one({"_id": ObjectId(doc_id)}, {"password": 0})
    if not doctor:
        return {"success": False, "message": "Doctor not found"}

    if not doctor.get("available"):
        return {"success": False, "message": "Doctor Not Available"}

    slots_booked = doctor.get("slots_booked", {})
    if slot_date in slots_booked:
        if slot_time in slots_booked[slot_date]:
            return {"success": False, "message": "Slot Not Available"}
        slots_booked[slot_date].append(slot_time)
    else:
        slots_booked[slot_date] = [slot_time]

    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})

    # Serialize snapshots before storing — removes ObjectIds
    doc_snapshot = serialize({k: v for k, v in doctor.items() if k != "slots_booked"})
    user_snapshot = serialize(user)

    appointment_data = {
        "userId": user_id,
        "docId": doc_id,
        "userData": user_snapshot,
        "docData": doc_snapshot,
        "slotDate": slot_date,
        "slotTime": slot_time,
        "amount": doctor.get("fees", 0),
        "date": int(time.time() * 1000),
        "cancelled": False,
        "payment": False,
        "isCompleted": False,
    }

    await db.appointments.insert_one(appointment_data)
    await db.doctors.update_one(
        {"_id": ObjectId(doc_id)}, {"$set": {"slots_booked": slots_booked}}
    )

    return {"success": True, "message": "Appointment Booked Successfully"}


# ── List Appointments ─────────────────────────────────────────────────────────

async def list_appointments(user_id: str):
    db = get_db()
    appointments = []
    async for appt in db.appointments.find({"userId": user_id}):
        appointments.append(serialize(appt))
    return {"success": True, "appointments": appointments}


# ── Cancel Appointment ────────────────────────────────────────────────────────

async def cancel_appointment(user_id: str, appointment_id: str):
    db = get_db()

    appt = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
    if not appt:
        return {"success": False, "message": "Appointment not found"}

    if appt.get("userId") != user_id:
        return {"success": False, "message": "Unauthorized action"}

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
