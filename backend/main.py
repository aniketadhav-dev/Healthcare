# main.py - FastAPI Application Entry Point

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import engine, Base, SessionLocal
import models
import auth

# Import all routers
from routers import auth as auth_router
from routers import doctors, appointments, users

# ─── Create DB tables ─────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Healthcare Appointment System",
    description="A full-stack healthcare appointment booking API",
    version="1.0.0",
)

# Allow frontend to call the API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routers ─────────────────────────────────────────────────────────
app.include_router(auth_router.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(users.router)


# ─── Seed Sample Data ─────────────────────────────────────────────────────────
def seed_data():
    """Create sample doctors and admin on first run."""
    db = SessionLocal()
    try:
        # Skip if data already exists
        if db.query(models.User).count() > 0:
            return

        print("🌱 Seeding sample data...")

        # Create admin
        admin = models.User(
            full_name="Admin User",
            email="admin@healthcare.com",
            hashed_password=auth.hash_password("admin123"),
            role="admin",
            phone="9999999999",
        )
        db.add(admin)
        db.flush()

        # Sample doctors data
        doctors_data = [
            {
                "full_name": "Dr. Priya Sharma",
                "email": "priya.sharma@healthcare.com",
                "phone": "9876543210",
                "specialization": "Cardiologist",
                "qualification": "MBBS, MD (Cardiology), DM",
                "experience_years": 12,
                "bio": "Senior cardiologist with expertise in interventional cardiology and heart failure management.",
                "consultation_fee": 800,
            },
            {
                "full_name": "Dr. Arjun Mehta",
                "email": "arjun.mehta@healthcare.com",
                "phone": "9876543211",
                "specialization": "Dermatologist",
                "qualification": "MBBS, MD (Dermatology)",
                "experience_years": 8,
                "bio": "Specialist in skin disorders, cosmetic dermatology and hair loss treatment.",
                "consultation_fee": 600,
            },
            {
                "full_name": "Dr. Sunita Rao",
                "email": "sunita.rao@healthcare.com",
                "phone": "9876543212",
                "specialization": "Pediatrician",
                "qualification": "MBBS, DCH, MD (Pediatrics)",
                "experience_years": 15,
                "bio": "Caring pediatrician specializing in child development, vaccinations, and neonatal care.",
                "consultation_fee": 500,
            },
            {
                "full_name": "Dr. Vikram Joshi",
                "email": "vikram.joshi@healthcare.com",
                "phone": "9876543213",
                "specialization": "Orthopedic Surgeon",
                "qualification": "MBBS, MS (Orthopedics), DNB",
                "experience_years": 10,
                "bio": "Expert in joint replacement, sports injuries and spine surgery.",
                "consultation_fee": 900,
            },
            {
                "full_name": "Dr. Kavitha Nair",
                "email": "kavitha.nair@healthcare.com",
                "phone": "9876543214",
                "specialization": "Neurologist",
                "qualification": "MBBS, MD (Neurology), DM",
                "experience_years": 9,
                "bio": "Specialist in epilepsy, stroke, migraine and neurodegenerative disorders.",
                "consultation_fee": 1000,
            },
            {
                "full_name": "Dr. Ravi Gupta",
                "email": "ravi.gupta@healthcare.com",
                "phone": "9876543215",
                "specialization": "General Physician",
                "qualification": "MBBS, MD (General Medicine)",
                "experience_years": 6,
                "bio": "General physician providing comprehensive primary care and preventive medicine.",
                "consultation_fee": 400,
            },
        ]

        for d in doctors_data:
            # Create user with doctor role
            user = models.User(
                full_name=d["full_name"],
                email=d["email"],
                hashed_password=auth.hash_password("doctor123"),
                role="doctor",
                phone=d["phone"],
            )
            db.add(user)
            db.flush()

            # Create doctor profile
            doctor = models.Doctor(
                user_id=user.id,
                specialization=d["specialization"],
                qualification=d["qualification"],
                experience_years=d["experience_years"],
                bio=d["bio"],
                consultation_fee=d["consultation_fee"],
                available_days="Monday,Tuesday,Wednesday,Thursday,Friday",
                available_start_time="09:00",
                available_end_time="17:00",
            )
            db.add(doctor)

        # Create a sample patient
        patient = models.User(
            full_name="Rahul Verma",
            email="rahul@example.com",
            hashed_password=auth.hash_password("patient123"),
            role="patient",
            phone="9123456789",
        )
        db.add(patient)

        db.commit()
        print("✅ Sample data seeded successfully!")
        print("\n📋 Test Accounts:")
        print("  Admin:   admin@healthcare.com / admin123")
        print("  Patient: rahul@example.com / patient123")
        print("  Doctor:  priya.sharma@healthcare.com / doctor123")

    except Exception as e:
        print(f"⚠️  Seed error: {e}")
        db.rollback()
    finally:
        db.close()


# Seed on startup
@app.on_event("startup")
def startup_event():
    seed_data()


# ─── Root endpoint ────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "Healthcare Appointment System API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# ─── Run directly ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
