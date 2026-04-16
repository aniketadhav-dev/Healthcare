# routers/doctors.py - Doctor management endpoints

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/", response_model=List[schemas.DoctorOut])
def list_doctors(
    specialization: Optional[str] = Query(None, description="Filter by specialization"),
    db: Session = Depends(get_db)
):
    """List all active doctors, optionally filtered by specialization."""
    query = db.query(models.Doctor).filter(models.Doctor.is_active == True)
    if specialization:
        query = query.filter(
            models.Doctor.specialization.ilike(f"%{specialization}%")
        )
    doctors = query.all()
    return doctors


@router.get("/specializations")
def list_specializations(db: Session = Depends(get_db)):
    """Get list of all unique specializations."""
    results = db.query(models.Doctor.specialization).distinct().all()
    return [r[0] for r in results]


@router.get("/{doctor_id}", response_model=schemas.DoctorOut)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Get a specific doctor's details."""
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.post("/", response_model=schemas.DoctorOut)
def create_doctor_profile(
    data: schemas.DoctorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role("admin"))
):
    """Admin: Create a doctor profile for an existing user."""
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if doctor profile already exists
    existing = db.query(models.Doctor).filter(models.Doctor.user_id == data.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Doctor profile already exists for this user")

    # Update user role to doctor
    user.role = "doctor"
    db.commit()

    doctor = models.Doctor(**data.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.put("/{doctor_id}", response_model=schemas.DoctorOut)
def update_doctor(
    doctor_id: int,
    data: schemas.DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Doctor or admin can update a doctor's profile."""
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Only the doctor themselves or admin can update
    if current_user.role != "admin" and doctor.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(doctor, field, value)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role("admin"))
):
    """Admin: Deactivate a doctor."""
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.is_active = False
    db.commit()
    return {"message": "Doctor deactivated successfully"}
