import os
import json
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import pandas as pd

from app.database.session import get_db
from app.models.transport import Route, Stop, Bus
from app.models.user import User, Driver, Student
from app.models.trip import Trip, TrafficReport
from app.models.ml import ModelTrainingHistory
from app.schemas.transport import RouteCreate, RouteUpdate, RouteResponse, StopResponse
from app.schemas.admin import (
    AdminDashboardResponse,
    ModelMetricsResponse,
    ModelHistoryResponse,
    DatasetUploadResponse,
    DriverResponse,
    DriverCreate,
    DriverUpdate,
    StudentResponse,
    StudentCreate,
    StudentUpdate
)
from app.core.security import hash_password
from app.api.deps import get_current_admin
from app.ml.train_model import train_and_compare_models, retrain_pipeline, METADATA_PATH, DATASETS_DIR
from app.utils.data_validator import validate_datasets

router = APIRouter(prefix="/admin", tags=["Admin Portal"])

@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_admin_dashboard(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Overview dashboard KPIs for SECE Transport Administration."""
    total_routes = db.query(Route).filter(Route.is_active == True).count()
    active_buses = db.query(Bus).filter(Bus.is_active == True).count()
    reg_drivers = db.query(Driver).count()
    reg_students = db.query(Student).count()
    total_trips = db.query(Trip).count()
    active_trips_today = db.query(Trip).filter(Trip.trip_date == date.today()).count()
    synthetic_count = db.query(Trip).filter(Trip.is_synthetic == True).count()
    synth_ratio = (synthetic_count / total_trips * 100.0) if total_trips > 0 else 0.0

    # Get active champion model info
    active_model = db.query(ModelTrainingHistory).filter(ModelTrainingHistory.is_active == True).first()
    model_version = active_model.model_version if active_model else "v1.1.0"
    model_algo = active_model.model_name if active_model else "HistGradientBoosting Regressor"
    val_mae = active_model.val_mae if active_model and active_model.val_mae else 1.49

    # Recent severe / high traffic reports count
    recent_alerts = db.query(TrafficReport).filter(TrafficReport.traffic_level.in_(["HIGH", "SEVERE"])).count()

    return {
        "total_routes": total_routes,
        "active_buses": active_buses,
        "registered_drivers": reg_drivers,
        "registered_students": reg_students,
        "total_trips_recorded": total_trips,
        "active_trips_today": active_trips_today,
        "synthetic_records_count": synthetic_count,
        "synthetic_ratio_percentage": round(synth_ratio, 1),
        "champion_model_version": model_version,
        "champion_algorithm": model_algo,
        "champion_val_mae_minutes": val_mae,
        "recent_traffic_alerts_count": recent_alerts
    }

@router.post("/routes", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
def create_route(route_in: RouteCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Adds a new authentic SECE bus route with stops."""
    # Check if route number already exists
    if db.query(Route).filter(Route.route_number == route_in.route_number).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Route with number '{route_in.route_number}' already exists."
        )

    # Parse morning start time
    parts = [int(p) for p in route_in.morning_start_time.split(":")]
    from datetime import time
    morning_time = time(parts[0], parts[1], parts[2] if len(parts) > 2 else 0)

    route_obj = Route(
        route_number=route_in.route_number,
        route_name=route_in.route_name,
        origin_name=route_in.origin_name,
        destination_name=route_in.destination_name,
        total_distance_km=route_in.total_distance_km,
        estimated_duration_minutes=route_in.estimated_duration_minutes,
        morning_start_time=morning_time,
        evening_start_time=time(16, 45, 0),
        is_active=True
    )
    db.add(route_obj)
    db.flush()

    # Add stops if provided
    if route_in.stops:
        for s in route_in.stops:
            stop_obj = Stop(
                route_id=route_obj.id,
                stop_name=s.stop_name,
                stop_sequence=s.stop_sequence,
                latitude=s.latitude,
                longitude=s.longitude,
                distance_from_origin_km=s.distance_from_origin_km,
                scheduled_offset_minutes=s.scheduled_offset_minutes,
                landmark=s.landmark
            )
            db.add(stop_obj)

    db.commit()
    db.refresh(route_obj)
    return route_obj

@router.put("/routes/{route_id}", response_model=RouteResponse)
def update_route(
    route_id: int,
    route_in: RouteUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Updates an existing SECE bus route."""
    route_obj = db.query(Route).filter(Route.id == route_id).first()
    if not route_obj:
        raise HTTPException(status_code=404, detail=f"Route ID {route_id} not found.")

    if route_in.route_name is not None:
        route_obj.route_name = route_in.route_name
    if route_in.origin_name is not None:
        route_obj.origin_name = route_in.origin_name
    if route_in.total_distance_km is not None:
        route_obj.total_distance_km = route_in.total_distance_km
    if route_in.estimated_duration_minutes is not None:
        route_obj.estimated_duration_minutes = route_in.estimated_duration_minutes
    if route_in.is_active is not None:
        route_obj.is_active = route_in.is_active

    db.commit()
    db.refresh(route_obj)
    return route_obj

@router.delete("/routes/{route_id}", status_code=status.HTTP_200_OK)
def delete_route(route_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Deactivates an SECE bus route."""
    route_obj = db.query(Route).filter(Route.id == route_id).first()
    if not route_obj:
        raise HTTPException(status_code=404, detail=f"Route ID {route_id} not found.")

    route_obj.is_active = False
    db.commit()
    return {"message": f"Route '{route_obj.route_name}' ({route_obj.route_number}) has been deactivated."}

@router.post("/datasets/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Uploads and ingests a historical CSV dataset of trip records."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files (.csv) are supported.")

    try:
        contents = await file.read()
        import io
        uploaded_df = pd.read_csv(io.BytesIO(contents))

        # Check required columns
        req_cols = ["trip_id", "route_id", "stop_id", "actual_delay_minutes", "actual_remaining_travel_minutes"]
        missing = [c for c in req_cols if c not in uploaded_df.columns]
        if missing:
            raise HTTPException(status_code=400, detail=f"Uploaded CSV is missing required columns: {missing}")

        # Mark uploaded records
        if "is_synthetic" not in uploaded_df.columns:
            uploaded_df["is_synthetic"] = False

        # Append to existing trip history file
        target_csv = DATASETS_DIR / "bus_trip_history.csv"
        existing_df = pd.read_csv(target_csv)
        combined_df = pd.concat([existing_df, uploaded_df], ignore_index=True).drop_duplicates(subset=["trip_id", "stop_id"])
        combined_df.to_csv(target_csv, index=False)

        records_added = len(combined_df) - len(existing_df)
        return {
            "status": "success",
            "filename": file.filename,
            "records_added": max(0, records_added),
            "total_records": len(combined_df),
            "message": f"Successfully ingested {records_added} new records into {target_csv.name}."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process CSV dataset: {str(e)}")

@router.post("/model/train")
def trigger_model_training(admin: User = Depends(get_current_admin)):
    """Triggers ML model training and candidate benchmarking with promotion gating."""
    try:
        res = retrain_pipeline()
        return {
            "status": "success",
            "message": f"Retraining executed successfully. Action: {res.get('deployment_action', 'COMPLETED')}",
            "version": res.get("version"),
            "model_name": res.get("model_name"),
            "validation_delay_mae": res.get("champion_validation_metrics", {}).get("delay_mae"),
            "test_delay_mae": res.get("champion_test_metrics", {}).get("delay_mae"),
            "test_overall_r2": res.get("champion_test_metrics", {}).get("overall_r2")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model retraining failed: {str(e)}")

@router.get("/model/metrics", response_model=ModelMetricsResponse)
def get_model_metrics(admin: User = Depends(get_current_admin)):
    """Returns evaluation metrics, feature list, and metadata of the active champion model."""
    if not METADATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Model metadata manifest not found.")

    with open(METADATA_PATH, "r") as f:
        meta = json.load(f)

    return {
        "version": meta.get("version", "v1.1.0"),
        "model_name": meta.get("model_name", "HistGradientBoosting Regressor"),
        "algorithm_type": meta.get("algorithm_type", "gradient_boosting"),
        "trained_at": meta.get("trained_at", datetime.utcnow().isoformat()),
        "training_records_count": meta.get("training_records_count", 5456),
        "validation_metrics": meta.get("champion_validation_metrics", {}),
        "test_metrics": meta.get("champion_test_metrics", {}),
        "baseline_metrics": meta.get("baseline_validation_metrics", {}),
        "features_count": meta.get("features", {}).get("total_count", 14),
        "data_authenticity_notice": meta.get("data_authenticity_notice", "Simulated-Data Performance")
    }

@router.get("/model/history", response_model=List[ModelHistoryResponse])
def get_model_history(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Returns historical model training and retraining runs from SQLite."""
    history = db.query(ModelTrainingHistory).order_by(ModelTrainingHistory.trained_at.desc()).all()
    return history


# ─────────────────────────────────────────────────────────────────────────────
# DRIVER MANAGEMENT CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/drivers", response_model=List[DriverResponse])
def get_drivers(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Lists all registered college bus drivers."""
    drivers = db.query(Driver).all()
    results = []
    for d in drivers:
        u = d.user
        bus = d.assigned_bus
        results.append({
            "id": d.id,
            "user_id": d.user_id,
            "full_name": u.full_name if u else "Unknown",
            "email": u.email if u else "",
            "phone": u.phone if u else None,
            "license_number": d.license_number,
            "experience_years": d.experience_years,
            "assigned_bus_id": d.assigned_bus_id,
            "assigned_bus_number": bus.bus_number if bus else None,
            "contact_emergency": d.contact_emergency,
            "is_available": d.is_available
        })
    return results

@router.post("/drivers", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(data: DriverCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Creates a new driver account and profile."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail=f"User with email '{data.email}' already exists.")
    if db.query(Driver).filter(Driver.license_number == data.license_number).first():
        raise HTTPException(status_code=400, detail=f"Driver with license '{data.license_number}' already exists.")

    username = data.email.split("@")[0] + f"_{os.urandom(2).hex()}"
    user = User(
        email=data.email,
        username=username,
        hashed_password=hash_password(data.password),
        role="DRIVER",
        full_name=data.full_name,
        phone=data.phone,
        is_active=True
    )
    db.add(user)
    db.flush()

    driver = Driver(
        user_id=user.id,
        license_number=data.license_number,
        experience_years=data.experience_years,
        assigned_bus_id=data.assigned_bus_id,
        contact_emergency=data.contact_emergency,
        is_available=True
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    bus = driver.assigned_bus
    return {
        "id": driver.id,
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "license_number": driver.license_number,
        "experience_years": driver.experience_years,
        "assigned_bus_id": driver.assigned_bus_id,
        "assigned_bus_number": bus.bus_number if bus else None,
        "contact_emergency": driver.contact_emergency,
        "is_available": driver.is_available
    }

@router.put("/drivers/{driver_id}", response_model=DriverResponse)
def update_driver(driver_id: int, data: DriverUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Updates driver details and bus assignment."""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found.")
    user = driver.user

    if data.full_name is not None and user:
        user.full_name = data.full_name
    if data.phone is not None and user:
        user.phone = data.phone
    if data.license_number is not None:
        driver.license_number = data.license_number
    if data.experience_years is not None:
        driver.experience_years = data.experience_years
    if data.assigned_bus_id is not None:
        driver.assigned_bus_id = data.assigned_bus_id
    if data.contact_emergency is not None:
        driver.contact_emergency = data.contact_emergency
    if data.is_available is not None:
        driver.is_available = data.is_available

    db.commit()
    db.refresh(driver)
    bus = driver.assigned_bus
    return {
        "id": driver.id,
        "user_id": user.id if user else 0,
        "full_name": user.full_name if user else "",
        "email": user.email if user else "",
        "phone": user.phone if user else None,
        "license_number": driver.license_number,
        "experience_years": driver.experience_years,
        "assigned_bus_id": driver.assigned_bus_id,
        "assigned_bus_number": bus.bus_number if bus else None,
        "contact_emergency": driver.contact_emergency,
        "is_available": driver.is_available
    }

@router.delete("/drivers/{driver_id}")
def delete_driver(driver_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Deletes a driver profile and user account."""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found.")
    user = driver.user
    db.delete(driver)
    if user:
        db.delete(user)
    db.commit()
    return {"message": "Driver deleted successfully."}


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT MANAGEMENT CRUD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/students", response_model=List[StudentResponse])
def get_students(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Lists all registered students."""
    students = db.query(Student).all()
    results = []
    for s in students:
        u = s.user
        route = s.default_route
        stop = s.default_stop
        results.append({
            "id": s.id,
            "user_id": s.user_id,
            "full_name": u.full_name if u else "Unknown",
            "email": u.email if u else "",
            "phone": u.phone if u else None,
            "roll_number": s.roll_number,
            "department": s.department,
            "year_of_study": s.year_of_study,
            "default_route_id": s.default_route_id,
            "default_route_number": route.route_number if route else None,
            "default_stop_id": s.default_stop_id,
            "default_stop_name": stop.stop_name if stop else None
        })
    return results

@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(data: StudentCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Creates a new student account and transport profile."""
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail=f"User with email '{data.email}' already exists.")
    if db.query(Student).filter(Student.roll_number == data.roll_number).first():
        raise HTTPException(status_code=400, detail=f"Student with roll number '{data.roll_number}' already exists.")

    username = data.email.split("@")[0] + f"_{os.urandom(2).hex()}"
    user = User(
        email=data.email,
        username=username,
        hashed_password=hash_password(data.password),
        role="STUDENT",
        full_name=data.full_name,
        phone=data.phone,
        is_active=True
    )
    db.add(user)
    db.flush()

    student = Student(
        user_id=user.id,
        roll_number=data.roll_number,
        department=data.department,
        year_of_study=data.year_of_study,
        default_route_id=data.default_route_id,
        default_stop_id=data.default_stop_id
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    route = student.default_route
    stop = student.default_stop
    return {
        "id": student.id,
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "roll_number": student.roll_number,
        "department": student.department,
        "year_of_study": student.year_of_study,
        "default_route_id": student.default_route_id,
        "default_route_number": route.route_number if route else None,
        "default_stop_id": student.default_stop_id,
        "default_stop_name": stop.stop_name if stop else None
    }

@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Updates student profile information."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    user = student.user

    if data.full_name is not None and user:
        user.full_name = data.full_name
    if data.phone is not None and user:
        user.phone = data.phone
    if data.roll_number is not None:
        student.roll_number = data.roll_number
    if data.department is not None:
        student.department = data.department
    if data.year_of_study is not None:
        student.year_of_study = data.year_of_study
    if data.default_route_id is not None:
        student.default_route_id = data.default_route_id
    if data.default_stop_id is not None:
        student.default_stop_id = data.default_stop_id

    db.commit()
    db.refresh(student)
    route = student.default_route
    stop = student.default_stop
    return {
        "id": student.id,
        "user_id": user.id if user else 0,
        "full_name": user.full_name if user else "",
        "email": user.email if user else "",
        "phone": user.phone if user else None,
        "roll_number": student.roll_number,
        "department": student.department,
        "year_of_study": student.year_of_study,
        "default_route_id": student.default_route_id,
        "default_route_number": route.route_number if route else None,
        "default_stop_id": student.default_stop_id,
        "default_stop_name": stop.stop_name if stop else None
    }

@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Deletes a student profile and user account."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    user = student.user
    db.delete(student)
    if user:
        db.delete(user)
    db.commit()
    return {"message": "Student deleted successfully."}
