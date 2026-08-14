from fastapi import APIRouter, Depends, Form, UploadFile, File
from pydantic import BaseModel
from typing import Optional

from controllers.user_controller import (
    register_user,
    login_user,
    get_profile,
    update_profile,
    book_appointment,
    list_appointments,
    cancel_appointment,
)
from middlewares.auth import CurrentUser, require_roles

router = APIRouter(prefix="/api/user", tags=["Users"])

_user = require_roles(["user"])


# ── Request bodies ────────────────────────────────────────────────────────────

class RegisterBody(BaseModel):
    name: str
    email: str
    password: str

class LoginBody(BaseModel):
    email: str
    password: str

class BookAppointmentBody(BaseModel):
    docId: str
    slotDate: str
    slotTime: str

class CancelAppointmentBody(BaseModel):
    appointmentId: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register")
async def route_register(body: RegisterBody):
    return await register_user(body.name, body.email, body.password)


@router.post("/login")
async def route_login(body: LoginBody):
    return await login_user(body.email, body.password)


@router.get("/get-profile")
async def route_get_profile(current_user: CurrentUser = Depends(_user)):
    return await get_profile(current_user.sub)


@router.post("/update-profile")
async def route_update_profile(
    name: str = Form(...),
    phone: str = Form(...),
    dob: str = Form(...),
    address: str = Form(...),
    gender: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: CurrentUser = Depends(_user),
):
    return await update_profile(current_user.sub, name, phone, dob, address, gender, image)


@router.post("/book-appointment")
async def route_book_appointment(
    body: BookAppointmentBody,
    current_user: CurrentUser = Depends(_user),
):
    return await book_appointment(current_user.sub, body.docId, body.slotDate, body.slotTime)


@router.get("/appointments")
async def route_list_appointments(current_user: CurrentUser = Depends(_user)):
    return await list_appointments(current_user.sub)


@router.post("/cancel-appointment")
async def route_cancel_appointment(
    body: CancelAppointmentBody,
    current_user: CurrentUser = Depends(_user),
):
    return await cancel_appointment(current_user.sub, body.appointmentId)
