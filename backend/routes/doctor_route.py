import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any

from controllers.doctor_controller import (
    doctor_list,
    login_doctor,
    appointments_doctor,
    appointment_cancel,
    appointment_completed,
    doctor_dashboard,
    doctor_profile,
    update_doctor_profile,
)
from middlewares.auth import auth_doctor

router = APIRouter(prefix="/api/doctor")


# ── Request bodies (JSON) ─────────────────────────────────────────────────────

class LoginBody(BaseModel):
    email: str
    password: str

class AppointmentIdBody(BaseModel):
    appointmentId: str

class UpdateProfileBody(BaseModel):
    fees: float
    address: Any
    available: bool


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/list")
async def route_doctor_list():
    return await doctor_list()


@router.post("/login")
async def route_login_doctor(body: LoginBody):
    return await login_doctor(body.email, body.password)


@router.get("/appointments")
async def route_appointments_doctor(doc_id: str = Depends(auth_doctor)):
    return await appointments_doctor(doc_id)


@router.post("/cancel-appointment")
async def route_cancel_appointment(
    body: AppointmentIdBody,
    doc_id: str = Depends(auth_doctor),
):
    return await appointment_cancel(doc_id, body.appointmentId)


@router.post("/complete-appointment")
async def route_complete_appointment(
    body: AppointmentIdBody,
    doc_id: str = Depends(auth_doctor),
):
    return await appointment_completed(doc_id, body.appointmentId)


@router.get("/dashboard")
async def route_doctor_dashboard(doc_id: str = Depends(auth_doctor)):
    return await doctor_dashboard(doc_id)


@router.get("/profile")
async def route_doctor_profile(doc_id: str = Depends(auth_doctor)):
    return await doctor_profile(doc_id)


@router.post("/update-profile")
async def route_update_doctor_profile(
    body: UpdateProfileBody,
    doc_id: str = Depends(auth_doctor),
):
    # address may come as a string or dict
    address = body.address if isinstance(body.address, dict) else json.loads(body.address)
    return await update_doctor_profile(doc_id, body.fees, address, body.available)
