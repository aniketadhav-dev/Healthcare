# schemas.py - Pydantic schemas for request/response validation

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


# ─── Auth Schemas ────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: str = "patient"

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("role")
    @classmethod
    def valid_role(cls, v):
        if v not in ["patient", "doctor", "admin"]:
            raise ValueError("Role must be patient, doctor, or admin")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str


# ─── User Schemas ─────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    phone: Optional[str]
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ─── Doctor Schemas ───────────────────────────────────────────────────────────

class DoctorCreate(BaseModel):
    user_id: int
    specialization: str
    qualification: Optional[str] = None
    experience_years: int = 0
    bio: Optional[str] = None
    consultation_fee: int = 0
    available_days: str = "Monday,Tuesday,Wednesday,Thursday,Friday"
    available_start_time: str = "09:00"
    available_end_time: str = "17:00"


class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    consultation_fee: Optional[int] = None
    available_days: Optional[str] = None
    available_start_time: Optional[str] = None
    available_end_time: Optional[str] = None


class DoctorOut(BaseModel):
    id: int
    user_id: int
    specialization: str
    qualification: Optional[str]
    experience_years: int
    bio: Optional[str]
    consultation_fee: int
    available_days: str
    available_start_time: str
    available_end_time: str
    is_active: bool
    # Nested user info
    user: UserOut

    class Config:
        from_attributes = True


# ─── Appointment Schemas ──────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: str   # YYYY-MM-DD
    appointment_time: str   # HH:MM
    reason: Optional[str] = None

    @field_validator("appointment_date")
    @classmethod
    def valid_date_format(cls, v):
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class AppointmentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        if v not in ["pending", "confirmed", "completed", "cancelled"]:
            raise ValueError("Invalid status")
        return v


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: str
    appointment_time: str
    status: str
    reason: Optional[str]
    notes: Optional[str]
    created_at: Optional[datetime]
    # Nested info
    patient: UserOut
    doctor: DoctorOut

    class Config:
        from_attributes = True
