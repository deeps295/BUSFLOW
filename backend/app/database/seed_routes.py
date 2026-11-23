"""
Seeds the authentic SECE routes, stops, buses, and demo accounts from college_routes.csv
into the SQLite database.
"""

from datetime import time
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session

from app.database.session import SessionLocal, engine, Base
from app.models.user import User, Driver, Student
from app.models.transport import Route, Stop, Bus
from app.core.security import hash_password

DATASETS_DIR = Path(__file__).resolve().parent.parent.parent / "datasets"

def seed_database_from_routes(db: Session):
    """Seed routes, stops, buses and demo users into the SQLite database."""
    routes_csv = DATASETS_DIR / "college_routes.csv"
    if not routes_csv.exists():
        print(f"[Error] {routes_csv} not found. Generate datasets first.")
        return

    df_routes = pd.read_csv(routes_csv)
    
    # Check if already seeded
    existing_routes_count = db.query(Route).count()
    if existing_routes_count > 0:
        print(f"[Seed] Database already contains {existing_routes_count} routes. Skipping duplicate seed.")
        return

    print("[Seed] Populating SQLite database from college_routes.csv...")

    # 1. Seed demo accounts
    admin_user = User(
        email="admin@sece.ac.in",
        username="admin",
        hashed_password=hash_password("admin123"),
        role="ADMIN",
        full_name="SECE Transport Administrator",
        phone="+91 94422 10001"
    )
    db.add(admin_user)
    db.flush()

    # Driver user
    driver_user = User(
        email="driver@sece.ac.in",
        username="driver_selvam",
        hashed_password=hash_password("driver123"),
        role="DRIVER",
        full_name="Selvam K. (Senior Driver)",
        phone="+91 98421 20002"
    )
    db.add(driver_user)
    db.flush()

    # Student user
    student_user = User(
        email="student@sece.ac.in",
        username="student_karthik",
        hashed_password=hash_password("student123"),
        role="STUDENT",
        full_name="Karthik R. (CSE Dept)",
        phone="+91 97890 30003"
    )
    db.add(student_user)
    db.flush()

    # 2. Seed Routes & Stops
    unique_routes = df_routes.groupby("route_id").first().reset_index()

    route_obj_map = {}
    first_stop_id = None

    for _, r_data in unique_routes.iterrows():
        dep_parts = [int(p) for p in str(r_data["scheduled_morning_departure"]).split(":")]
        morning_time = time(dep_parts[0], dep_parts[1], dep_parts[2] if len(dep_parts) > 2 else 0)

        route_obj = Route(
            route_number=r_data["route_number"],
            route_name=r_data["route_name"],
            origin_name=r_data["origin_name"],
            destination_name=r_data["destination_name"],
            total_distance_km=float(r_data["total_route_distance_km"]),
            estimated_duration_minutes=int(r_data["scheduled_offset_minutes"]) if "scheduled_offset_minutes" in r_data else 75,
            morning_start_time=morning_time,
            evening_start_time=time(16, 45, 0),
            is_active=True
        )
        db.add(route_obj)
        db.flush()
        route_obj_map[r_data["route_id"]] = route_obj

        # Seed Bus for this route
        bus_reg = f"TN-38-BZ-{4500 + int(r_data['route_number'].replace('Bus ', ''))}"
        bus_obj = Bus(
            bus_number=r_data["route_number"],
            registration_number=bus_reg,
            seating_capacity=55,
            model_info="Ashok Leyland Viking (SECE Fleet)",
            assigned_route_id=route_obj.id,
            is_active=True
        )
        db.add(bus_obj)
        db.flush()

        # Assign driver to Route 1 Bus
        if r_data["route_id"] == "R01_BHARATHIAR":
            driver_profile = Driver(
                user_id=driver_user.id,
                license_number="TN38-2015-0045892",
                experience_years=12,
                assigned_bus_id=bus_obj.id,
                contact_emergency="+91 94433 99999",
                is_available=True
            )
            db.add(driver_profile)

        # Seed Stops for this route
        route_stops = df_routes[df_routes["route_id"] == r_data["route_id"]].sort_values("stop_sequence")
        for _, s_data in route_stops.iterrows():
            stop_obj = Stop(
                route_id=route_obj.id,
                stop_name=s_data["stop_name"],
                stop_sequence=int(s_data["stop_sequence"]),
                latitude=float(s_data["latitude"]),
                longitude=float(s_data["longitude"]),
                distance_from_origin_km=float(s_data["distance_from_origin_km"]),
                scheduled_offset_minutes=int(s_data["scheduled_offset_minutes"]),
                landmark=str(s_data["landmark"]) if pd.notnull(s_data["landmark"]) else None
            )
            db.add(stop_obj)
            db.flush()
            if first_stop_id is None:
                first_stop_id = stop_obj.id

    # Seed student profile
    student_profile = Student(
        user_id=student_user.id,
        roll_number="718121104042",
        department="Computer Science & Engineering",
        year_of_study=3,
        default_route_id=route_obj_map["R01_BHARATHIAR"].id,
        default_stop_id=first_stop_id
    )
    db.add(student_profile)

    db.commit()
    print("[Seed] Successfully seeded 10 SECE routes, 88 stops, 10 buses, and demo user profiles!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database_from_routes(db)
    finally:
        db.close()
