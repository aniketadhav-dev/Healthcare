# 🏥 MediBook – Healthcare Appointment System

A full-stack healthcare appointment booking system built with **FastAPI + SQLite + Vanilla HTML/CSS/JS**.

---

## 📁 Project Structure

```
healthcare/
├── backend/
│   ├── main.py              # FastAPI app entry point + seed data
│   ├── database.py          # SQLAlchemy DB setup
│   ├── models.py            # ORM models (User, Doctor, Appointment)
│   ├── schemas.py           # Pydantic validation schemas
│   ├── auth.py              # JWT auth + password hashing
│   ├── requirements.txt     # Python dependencies
│   └── routers/
│       ├── auth.py          # /auth endpoints
│       ├── doctors.py       # /doctors endpoints
│       ├── appointments.py  # /appointments endpoints
│       └── users.py         # /users endpoints
│
└── frontend/
    ├── server.py            # Simple Python HTTP server
    ├── templates/
    │   ├── login.html
    │   ├── register.html
    │   ├── dashboard.html
    │   ├── doctor_list.html
    │   ├── appointments.html
    │   └── admin.html
    └── static/
        ├── css/style.css    # Full stylesheet
        └── js/app.js        # API client + utilities
```

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.9+
- pip

### Step 1 – Install Backend Dependencies

```bash
cd healthcare/backend
pip install -r requirements.txt
```

### Step 2 – Start the Backend API

```bash
cd healthcare/backend
python main.py
# OR
uvicorn main:app --reload --port 8000
```

The API starts at **http://localhost:8000**
Interactive API docs: **http://localhost:8000/docs**

### Step 3 – Start the Frontend Server

Open a new terminal:

```bash
cd healthcare/frontend
python server.py
```

The frontend starts at **http://localhost:3000**

### Step 4 – Open the App

Visit: **http://localhost:3000/login.html**

---

## 🔑 Demo Accounts (auto-seeded on first run)

| Role    | Email                            | Password    |
|---------|----------------------------------|-------------|
| Patient | rahul@example.com                | patient123  |
| Doctor  | priya.sharma@healthcare.com      | doctor123   |
| Admin   | admin@healthcare.com             | admin123    |

> All seeded doctor passwords are: **doctor123**

---

## 📋 Feature Summary

### Patient
- Register & login
- Browse all doctors, search/filter by specialization
- Book appointment (select date + time slot)
- View upcoming and past appointments with status
- Cancel pending/confirmed appointments

### Doctor
- Login with seeded credentials
- View all assigned appointments
- Update appointment status (pending → confirmed → completed)
- Add clinical notes to appointments

### Admin
- View all users and deactivate accounts
- View and manage all doctors
- Add new doctors (register user + create profile in one flow)
- View all system appointments across all doctors

---

## 🔌 API Endpoints

### Auth
```
POST /auth/register     Register new user
POST /auth/login        Login, returns JWT
GET  /auth/me           Current user info
```

### Doctors
```
GET    /doctors/                   List all doctors (filter: ?specialization=X)
GET    /doctors/specializations    List unique specializations
GET    /doctors/{id}               Get doctor by ID
POST   /doctors/                   Create doctor profile (admin only)
PUT    /doctors/{id}               Update doctor profile (doctor/admin)
DELETE /doctors/{id}               Deactivate doctor (admin only)
```

### Appointments
```
GET    /appointments/              List appointments (filtered by role)
POST   /appointments/              Book appointment (patient only)
GET    /appointments/{id}          Get specific appointment
PUT    /appointments/{id}/status   Update status (doctor/admin)
DELETE /appointments/{id}          Cancel appointment (patient/admin)
```

### Users
```
GET    /users/          List all users (admin only)
GET    /users/{id}      Get specific user
DELETE /users/{id}      Deactivate user (admin only)
```

---

## 🧪 Example API Requests (curl)

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"John Doe","email":"john@test.com","password":"test123","role":"patient"}'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"rahul@example.com","password":"patient123"}'
```

### Book Appointment (with token)
```bash
curl -X POST http://localhost:8000/appointments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"doctor_id":1,"appointment_date":"2025-01-20","appointment_time":"10:00","reason":"Chest pain"}'
```

### List Doctors (public)
```bash
curl http://localhost:8000/doctors/
curl "http://localhost:8000/doctors/?specialization=Cardiologist"
```

---

## 🛠 Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3.9+, FastAPI              |
| Database  | SQLite via SQLAlchemy ORM         |
| Auth      | JWT (python-jose) + bcrypt        |
| Frontend  | HTML5, CSS3, Vanilla JavaScript   |
| Server    | Uvicorn (backend), Python HTTP (frontend) |

---

## 📝 Notes

- The SQLite database file (`healthcare.db`) is created automatically in the `backend/` folder on first run.
- JWT tokens expire after **24 hours**.
- To reset data: delete `healthcare.db` and restart the backend.
- For production use: replace SQLite with PostgreSQL, use environment variables for secrets, and serve frontend via Nginx.
