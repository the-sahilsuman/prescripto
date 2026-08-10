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
from middlewares.auth import auth_user

router = APIRouter(prefix="/api/user")


# ── Request bodies (JSON) ─────────────────────────────────────────────────────

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
async def route_get_profile(user_id: str = Depends(auth_user)):
    return await get_profile(user_id)


@router.post("/update-profile")
async def route_update_profile(
    name: str = Form(...),
    phone: str = Form(...),
    dob: str = Form(...),
    address: str = Form(...),
    gender: str = Form(...),
    image: Optional[UploadFile] = File(None),
    user_id: str = Depends(auth_user),
):
    # update-profile uses multipart because it may include an image file
    return await update_profile(user_id, name, phone, dob, address, gender, image)


@router.post("/book-appointment")
async def route_book_appointment(
    body: BookAppointmentBody,
    user_id: str = Depends(auth_user),
):
    return await book_appointment(user_id, body.docId, body.slotDate, body.slotTime)


@router.get("/appointments")
async def route_list_appointments(user_id: str = Depends(auth_user)):
    return await list_appointments(user_id)


@router.post("/cancel-appointment")
async def route_cancel_appointment(
    body: CancelAppointmentBody,
    user_id: str = Depends(auth_user),
):
    return await cancel_appointment(user_id, body.appointmentId)
