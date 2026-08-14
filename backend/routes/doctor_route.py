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
from middlewares.auth import CurrentUser, require_roles

router = APIRouter(prefix="/api/doctor", tags=["Doctors"])

_doctor = require_roles(["doctor"])


# ── Request bodies ────────────────────────────────────────────────────────────

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
async def route_appointments_doctor(current_user: CurrentUser = Depends(_doctor)):
    return await appointments_doctor(current_user.sub)


@router.post("/cancel-appointment")
async def route_cancel_appointment(
    body: AppointmentIdBody,
    current_user: CurrentUser = Depends(_doctor),
):
    return await appointment_cancel(current_user.sub, body.appointmentId)


@router.post("/complete-appointment")
async def route_complete_appointment(
    body: AppointmentIdBody,
    current_user: CurrentUser = Depends(_doctor),
):
    return await appointment_completed(current_user.sub, body.appointmentId)


@router.get("/dashboard")
async def route_doctor_dashboard(current_user: CurrentUser = Depends(_doctor)):
    return await doctor_dashboard(current_user.sub)


@router.get("/profile")
async def route_doctor_profile(current_user: CurrentUser = Depends(_doctor)):
    return await doctor_profile(current_user.sub)


@router.post("/update-profile")
async def route_update_doctor_profile(
    body: UpdateProfileBody,
    current_user: CurrentUser = Depends(_doctor),
):
    address = body.address if isinstance(body.address, dict) else json.loads(body.address)
    return await update_doctor_profile(current_user.sub, body.fees, address, body.available)
