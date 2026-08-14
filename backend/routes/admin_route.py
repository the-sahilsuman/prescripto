from fastapi import APIRouter, Depends, Form, UploadFile, File
from pydantic import BaseModel

from controllers.admin_controller import (
    add_doctor,
    login_admin,
    all_doctors,
    appointments_admin,
    appointment_cancel,
    admin_dashboard,
)
from controllers.doctor_controller import change_availability
from middlewares.auth import CurrentUser, require_roles

router = APIRouter(prefix="/api/admin", tags=["Admin"])

_admin = require_roles(["admin"])


# ── Request bodies ────────────────────────────────────────────────────────────

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
    _: CurrentUser = Depends(_admin),
):
    return await add_doctor(name, email, password, speciality, degree, experience, about, fees, address, image)


@router.post("/login")
async def route_login_admin(body: LoginBody):
    return await login_admin(body.email, body.password)


@router.post("/all-doctors")
async def route_all_doctors(_: CurrentUser = Depends(_admin)):
    return await all_doctors()


@router.post("/change-availability")
async def route_change_availability(
    body: DocIdBody,
    _: CurrentUser = Depends(_admin),
):
    return await change_availability(body.docId)


@router.get("/appointments")
async def route_appointments_admin(_: CurrentUser = Depends(_admin)):
    return await appointments_admin()


@router.post("/cancel-appointment")
async def route_cancel_appointment(
    body: AppointmentIdBody,
    _: CurrentUser = Depends(_admin),
):
    return await appointment_cancel(body.appointmentId)


@router.get("/dashboard")
async def route_admin_dashboard(_: CurrentUser = Depends(_admin)):
    return await admin_dashboard()
