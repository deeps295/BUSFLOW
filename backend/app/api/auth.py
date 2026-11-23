from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.user import User, Driver, Student
from app.schemas.auth import UserRegister, UserLogin, Token, UserResponse, PasswordReset
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Registers a new user (Student, Driver, or Admin) with salted password hashing, or updates if overwrite_if_exists=True."""
    norm_email = user_in.email.strip().lower()
    norm_username = user_in.username.strip().lower()

    existing_by_email = db.query(User).filter(func.lower(User.email) == norm_email).first()
    existing_by_username = db.query(User).filter(func.lower(User.username) == norm_username).first()

    existing_user = existing_by_email or existing_by_username

    if existing_user:
        if user_in.overwrite_if_exists:
            # Overwrite credentials and details
            existing_user.hashed_password = hash_password(user_in.password)
            existing_user.full_name = user_in.full_name.strip()
            existing_user.role = user_in.role
            existing_user.is_active = True
            if user_in.phone:
                existing_user.phone = user_in.phone

            if user_in.role == "STUDENT":
                student_profile = db.query(Student).filter(Student.user_id == existing_user.id).first()
                roll_num = user_in.roll_number.strip().upper() if user_in.roll_number else f"7181{existing_user.id:08d}"
                # Ensure roll number uniqueness
                dup_roll = db.query(Student).filter(Student.roll_number == roll_num, Student.user_id != existing_user.id).first()
                if dup_roll:
                    roll_num = f"{roll_num}_{existing_user.id}"

                if student_profile:
                    student_profile.roll_number = roll_num
                    student_profile.department = user_in.department or student_profile.department
                else:
                    db.add(Student(
                        user_id=existing_user.id,
                        roll_number=roll_num,
                        department=user_in.department or "Engineering",
                        year_of_study=1
                    ))
            elif user_in.role == "DRIVER":
                driver_profile = db.query(Driver).filter(Driver.user_id == existing_user.id).first()
                lic_num = user_in.license_number.strip().upper() if user_in.license_number else f"TN38-DL-{existing_user.id:06d}"
                dup_lic = db.query(Driver).filter(Driver.license_number == lic_num, Driver.user_id != existing_user.id).first()
                if dup_lic:
                    lic_num = f"{lic_num}_{existing_user.id}"

                if driver_profile:
                    driver_profile.license_number = lic_num
                else:
                    db.add(Driver(
                        user_id=existing_user.id,
                        license_number=lic_num,
                        experience_years=3,
                        is_available=True
                    ))
            db.commit()
            db.refresh(existing_user)
            return existing_user
        else:
            conflict_field = "email" if existing_by_email else "username"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account with this {conflict_field} already exists. You can sign in directly or select 'Update Existing Account'."
            )

    # Check roll number uniqueness if student
    if user_in.role == "STUDENT" and user_in.roll_number:
        clean_roll = user_in.roll_number.strip().upper()
        dup_roll = db.query(Student).filter(Student.roll_number == clean_roll).first()
        if dup_roll and (not existing_user or dup_roll.user_id != existing_user.id):
            if user_in.overwrite_if_exists:
                dup_roll.roll_number = f"{clean_roll}_{dup_roll.id}"
                db.flush()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Roll number '{clean_roll}' is already assigned to an existing student profile."
                )

    # Check driver license uniqueness if driver
    if user_in.role == "DRIVER" and user_in.license_number:
        clean_lic = user_in.license_number.strip().upper()
        dup_lic = db.query(Driver).filter(Driver.license_number == clean_lic).first()
        if dup_lic and (not existing_user or dup_lic.user_id != existing_user.id):
            if user_in.overwrite_if_exists:
                dup_lic.license_number = f"{clean_lic}_{dup_lic.id}"
                db.flush()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Driver license number '{clean_lic}' is already registered."
                )

    # Create User
    new_user = User(
        email=user_in.email.strip().lower(),
        username=user_in.username.strip(),
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
        full_name=user_in.full_name.strip(),
        phone=user_in.phone,
        is_active=True
    )
    db.add(new_user)
    db.flush()

    # Create associated profile based on role
    if user_in.role == "STUDENT":
        roll_num = user_in.roll_number.strip().upper() if user_in.roll_number else f"7181{new_user.id:08d}"
        dept = user_in.department or "Engineering"
        student_profile = Student(
            user_id=new_user.id,
            roll_number=roll_num,
            department=dept,
            year_of_study=1
        )
        db.add(student_profile)
    elif user_in.role == "DRIVER":
        lic_num = user_in.license_number.strip().upper() if user_in.license_number else f"TN38-DL-{new_user.id:06d}"
        driver_profile = Driver(
            user_id=new_user.id,
            license_number=lic_num,
            experience_years=3,
            is_available=True
        )
        db.add(driver_profile)

    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user credentials and returns signed JWT access token with 365-day validity."""
    clean_identifier = login_data.username_or_email.strip().lower()

    user = (
        db.query(User)
        .filter(
            (func.lower(User.username) == clean_identifier) | 
            (func.lower(User.email) == clean_identifier)
        )
        .first()
    )

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact SECE transport administration."
        )

    # Create access token with long-lived validity (525600 minutes / 1 year)
    token_payload = {
        "user_id": user.id,
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role
    }
    access_token = create_access_token(token_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/reset-password")
def reset_password(data: PasswordReset, db: Session = Depends(get_db)):
    """Instantly resets the password for a given username or email."""
    clean_id = data.username_or_email.strip().lower()
    user = (
        db.query(User)
        .filter(
            (func.lower(User.username) == clean_id) | 
            (func.lower(User.email) == clean_id)
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No account found matching '{data.username_or_email}'."
        )

    user.hashed_password = hash_password(data.new_password)
    user.is_active = True
    db.commit()

    return {
        "message": f"Password for {user.username} ({user.email}) has been reset successfully.",
        "username": user.username,
        "email": user.email
    }

@router.get("/demo-tokens")
def get_demo_tokens(db: Session = Depends(get_db)):
    """Returns multiple ready-to-use long-lived JWT tokens for seamless project demonstration to external reviewers."""
    demo_accounts = [
        {"role": "STUDENT", "label": "Deepika T. (Student - AI&DS)", "email": "deepika@sece.ac.in", "username": "deepika", "password": "deepika123"},
        {"role": "STUDENT", "label": "Karthik R. (Student - CSE)", "email": "student@sece.ac.in", "username": "student_karthik", "password": "student123"},
        {"role": "DRIVER", "label": "Selvam K. (Senior Bus Driver)", "email": "driver@sece.ac.in", "username": "driver_selvam", "password": "driver123"},
        {"role": "ADMIN", "label": "SECE Transport Admin", "email": "admin@sece.ac.in", "username": "admin", "password": "admin123"},
        {"role": "ADMIN", "label": "External Reviewer / Examiner", "email": "reviewer@sece.ac.in", "username": "reviewer_external", "password": "reviewer123"},
    ]

    tokens_out = []
    for acc in demo_accounts:
        user = db.query(User).filter(func.lower(User.email) == acc["email"].lower()).first()
        if user:
            payload = {
                "user_id": user.id,
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
            jwt_token = create_access_token(payload)
            tokens_out.append({
                **acc,
                "user_id": user.id,
                "token": jwt_token,
                "validity": "365 Days"
            })

    return {
        "status": "success",
        "description": "Ready-to-use review tokens with 1-year validity for external evaluation.",
        "tokens": tokens_out
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's profile and assigned role."""
    return current_user
