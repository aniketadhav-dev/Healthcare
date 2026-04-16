# routers/auth.py - Authentication endpoints

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.Token)
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    """Register a new user (patient by default)."""
    # Check if email already exists
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=auth.hash_password(user_data.password),
        role=user_data.role,
        phone=user_data.phone,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    token = auth.create_access_token({"sub": str(new_user.id), "role": new_user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": new_user.role,
        "user_id": new_user.id,
        "full_name": new_user.full_name,
    }


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login and receive a JWT token."""
    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = auth.create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "full_name": user.full_name,
    }


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    """Get current logged-in user's info."""
    return current_user
