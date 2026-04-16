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

# ─── Register API Routers ─────────────────────────────────────────────────────
app.include_router(auth_router.router, prefix="/api") # Added /api prefix to avoid conflicts
app.include_router(doctors.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(users.router, prefix="/api")

# ─── Seed Sample Data ─────────────────────────────────────────────────────────
def seed_data():
    db = SessionLocal()
    try:
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

        doctors_data = [
            {
                "full_name": "Dr. Priya Sharma",
                "email": "priya.sharma@healthcare.com",
                "phone": "9876543210",
                "specialization": "Cardiologist",
                "qualification": "MBBS, MD (Cardiology), DM",
                "experience_years": 12,
                "bio": "Senior cardiologist with expertise in interventional cardiology.",
                "consultation_fee": 800,
            },
            # ... baaki doctors ka data wahi rahega jo aapne diya tha ...
        ]

        for d in doctors_data:
            user = models.User(
                full_name=d["full_name"],
                email=d["email"],
                hashed_password=auth.hash_password("doctor123"),
                role="doctor",
                phone=d["phone"],
            )
            db.add(user)
            db.flush()

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

        db.commit()
        print("✅ Seed success!")
    except Exception as e:
        print(f"⚠️ Seed error: {e}")
        db.rollback()
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    seed_data()

# ─── Frontend Serving Logic ───────────────────────────────────────────────────

# 1. Mount Static Files (CSS/JS)
# Path ko handle karne ke liye absolute path use kar rahe hain
current_dir = os.path.dirname(os.path.realpath(__file__))
frontend_static_path = os.path.join(current_dir, "..", "frontend", "static")
frontend_templates_path = os.path.join(current_dir, "..", "frontend", "templates")

if os.path.exists(frontend_static_path):
    app.mount("/static", StaticFiles(directory=frontend_static_path), name="static")

# 2. Serve HTML Pages
@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_templates_path, "login.html"))

@app.get("/{page_name}.html")
async def get_html_page(page_name: str):
    file_path = os.path.join(frontend_templates_path, f"{page_name}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Page not found"}

# API Health Check
@app.get("/api/status")
def root():
    return {"status": "online", "version": "1.0.0"}

# ─── Run Configuration for Render ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    # Render assigns a port via environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
