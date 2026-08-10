from fastapi import APIRouter, Depends, Form, UploadFile, File
from pydantic import BaseModel
from typing import Optional

from controllers.admin_controller import (
    add_doctor,
    login_admin,
    all_doctors,
    appointments_admin,
    appointment_cancel,
    admin_dashboard,
)
from controllers.doctor_controller import change_availability
from middlewares.auth import auth_admin

router = APIRouter(prefix="/api/admin")


# ── Request bodies (JSON) ─────────────────────────────────────────────────────

class LoginBody(BaseModel):
    email: str
    password: str

class DocIdBody(BaseModel):
    docId: str

class AppointmentIdBody(BaseModel):
    appointmentId: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/add-doctor")
async def route_add_doctor(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    speciality: str = Form(...),
    degree: str = Form(...),
    experience: str = Form(...),
    about: str = Form(...),
    fees: str = Form(...),
    address: str = Form(...),
    image: UploadFile = File(...),
    _: None = Depends(auth_admin),
):
    # add-doctor uses multipart because it has a file upload — Form is correct here
    return await add_doctor(name, email, password, speciality, degree, experience, about, fees, address, image)


@router.post("/login")
async def route_login_admin(body: LoginBody):
    return await login_admin(body.email, body.password)


@router.post("/all-doctors")
async def route_all_doctors(_: None = Depends(auth_admin)):
    return await all_doctors()


@router.post("/change-availability")
async def route_change_availability(
    body: DocIdBody,
    _: None = Depends(auth_admin),
):
    return await change_availability(body.docId)


@router.get("/appointments")
async def route_appointments_admin(_: None = Depends(auth_admin)):
    return await appointments_admin()


@router.post("/cancel-appointment")
async def route_cancel_appointment(
    body: AppointmentIdBody,
    _: None = Depends(auth_admin),
):
    return await appointment_cancel(body.appointmentId)


@router.get("/dashboard")
async def route_admin_dashboard(_: None = Depends(auth_admin)):
    return await admin_dashboard()
