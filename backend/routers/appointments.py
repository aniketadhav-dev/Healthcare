# routers/appointments.py - Appointment management endpoints

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.get("/", response_model=List[schemas.AppointmentOut])
def list_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get appointments:
    - Admin: all appointments
    - Doctor: their assigned appointments
    - Patient: their own appointments
    """
    if current_user.role == "admin":
        return db.query(models.Appointment).all()

    elif current_user.role == "doctor":
        doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.id).first()
        if not doctor:
            return []
        return db.query(models.Appointment).filter(
            models.Appointment.doctor_id == doctor.id
        ).all()

    else:  # patient
        return db.query(models.Appointment).filter(
            models.Appointment.patient_id == current_user.id
        ).all()


@router.post("/", response_model=schemas.AppointmentOut)
def book_appointment(
    data: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role("patient"))
):
    """Patient: Book an appointment with a doctor."""
    # Check doctor exists
    doctor = db.query(models.Doctor).filter(
        models.Doctor.id == data.doctor_id,
        models.Doctor.is_active == True
    ).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Check no conflict on same date+time for this doctor
    conflict = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == data.doctor_id,
        models.Appointment.appointment_date == data.appointment_date,
        models.Appointment.appointment_time == data.appointment_time,
        models.Appointment.status.in_(["pending", "confirmed"])
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="This time slot is already booked")

    appointment = models.Appointment(
        patient_id=current_user.id,
        doctor_id=data.doctor_id,
        appointment_date=data.appointment_date,
        appointment_time=data.appointment_time,
        reason=data.reason,
        status="pending",
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/{appointment_id}", response_model=schemas.AppointmentOut)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get a specific appointment (only if you own it or are admin)."""
    appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Access control
    if current_user.role == "admin":
        return appt
    if current_user.role == "patient" and appt.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.role == "doctor":
        doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.id).first()
        if not doctor or appt.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    return appt


@router.put("/{appointment_id}/status", response_model=schemas.AppointmentOut)
def update_appointment_status(
    appointment_id: int,
    data: schemas.AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Doctor/Admin: Update appointment status."""
    appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if current_user.role == "doctor":
        doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.id).first()
        if not doctor or appt.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    appt.status = data.status
    if data.notes:
        appt.notes = data.notes
    db.commit()
    db.refresh(appt)
    return appt


@router.delete("/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Patient/Admin: Cancel an appointment."""
    appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Patients can only cancel their own
    if current_user.role == "patient" and appt.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if appt.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel a completed appointment")

    appt.status = "cancelled"
    db.commit()
    return {"message": "Appointment cancelled successfully"}
