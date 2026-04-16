# models.py - SQLAlchemy ORM Models

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(str, enum.Enum):
    patient = "patient"
    doctor = "doctor"
    admin = "admin"


class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


class User(Base):
    """User model - stores all users (patients, doctors, admins)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.patient, nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship: one user can be one doctor profile
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    # Relationship: one patient can have many appointments
    appointments = relationship("Appointment", back_populates="patient", foreign_keys="Appointment.patient_id")


class Doctor(Base):
    """Doctor profile - extended info for users with doctor role."""
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialization = Column(String(100), nullable=False)
    qualification = Column(String(200), nullable=True)
    experience_years = Column(Integer, default=0)
    bio = Column(Text, nullable=True)
    consultation_fee = Column(Integer, default=0)  # in INR
    available_days = Column(String(200), default="Monday,Tuesday,Wednesday,Thursday,Friday")
    available_start_time = Column(String(10), default="09:00")
    available_end_time = Column(String(10), default="17:00")
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    appointments = relationship("Appointment", back_populates="doctor")


class Appointment(Base):
    """Appointment model - stores all appointment bookings."""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(String(20), nullable=False)  # YYYY-MM-DD
    appointment_time = Column(String(10), nullable=False)  # HH:MM
    status = Column(String(20), default=AppointmentStatus.pending, nullable=False)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)  # Doctor's notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("User", back_populates="appointments", foreign_keys=[patient_id])
    doctor = relationship("Doctor", back_populates="appointments")
