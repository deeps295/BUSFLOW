import sys
from pathlib import Path
from datetime import datetime, date
import pytest
from sqlalchemy.orm import Session

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import SessionLocal
from app.models.user import User
from app.models.transport import Route, Stop, Bus
from app.models.trip import Trip, TrafficReport
from app.api.auth import register, login, get_me
from app.api.admin import (
    get_admin_dashboard,
    create_route,
    update_route,
    delete_route,
    get_model_metrics,
    get_model_history
)
from app.api.driver import (
    get_driver_assigned_bus,
    start_trip,
    update_trip_stop,
    report_traffic_condition,
    complete_trip
)
from app.api.student import (
    get_student_routes,
    get_student_arrival_prediction,
    get_student_trip_status
)
from app.schemas.auth import UserRegister, UserLogin
from app.schemas.transport import RouteCreate, RouteUpdate, StopCreate
from app.schemas.trip import (
    TripStartRequest,
    TripUpdateRequest,
    TrafficReportRequest,
    TripCompleteRequest
)
from app.services.weather_service import get_current_sece_weather

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def admin_user(db_session):
    user = db_session.query(User).filter(User.role == "ADMIN").first()
    return user

@pytest.fixture(scope="module")
def driver_user(db_session):
    user = db_session.query(User).filter(User.role == "DRIVER").first()
    return user

@pytest.fixture(scope="module")
def student_user(db_session):
    user = db_session.query(User).filter(User.role == "STUDENT").first()
    return user

# 1. Authentication Tests
def test_login_demo_admin(db_session):
    login_in = UserLogin(username_or_email="admin@sece.ac.in", password="admin123")
    token = login(login_data=login_in, db=db_session)
    assert token["access_token"] is not None
    assert token["user"].role == "ADMIN"

def test_login_demo_driver(db_session):
    login_in = UserLogin(username_or_email="driver@sece.ac.in", password="driver123")
    token = login(login_data=login_in, db=db_session)
    assert token["access_token"] is not None
    assert token["user"].role == "DRIVER"

def test_register_new_student(db_session):
    import random
    rand_id = random.randint(10000, 99999)
    reg_in = UserRegister(
        email=f"test_student_{rand_id}@sece.ac.in",
        username=f"test_student_{rand_id}",
        password="password123",
        full_name="Priya M. (AI&DS)",
        role="STUDENT",
        roll_number=f"718122{rand_id}",
        department="Artificial Intelligence & Data Science"
    )
    new_user = register(user_in=reg_in, db=db_session)
    assert new_user.id is not None
    assert new_user.role == "STUDENT"

# 2. Weather Service Tests
def test_weather_service_sece_area():
    weather = get_current_sece_weather()
    assert weather is not None
    assert "temperature_c" in weather
    assert "condition" in weather
    assert "attribution" in weather
    assert "Open-Meteo" in weather["attribution"]["source"]
    assert "Kinathukadavu" in weather["attribution"]["area_note"]

# 3. Student Routes & Prediction Tests
def test_get_student_routes(db_session):
    routes = get_student_routes(db=db_session)
    assert len(routes) >= 10
    route_names = [r.route_name for r in routes]
    assert any("Bharathiar" in r for r in route_names)
    assert any("Pollachi" in r for r in route_names)

def test_student_arrival_prediction(db_session):
    route = db_session.query(Route).filter(Route.is_active == True).first()
    stop = db_session.query(Stop).filter(Stop.route_id == route.id).first()
    
    pred = get_student_arrival_prediction(
        route_id=route.id,
        stop_id=stop.id,
        traffic_override="HIGH",
        db=db_session
    )
    assert pred["route_id"] == route.id
    assert pred["stop_id"] == stop.id
    assert isinstance(pred["expected_delay_minutes"], float)
    assert isinstance(pred["predicted_remaining_travel_minutes"], float)
    assert pred["severity_status"] in ["ON_TIME", "MINOR_DELAY", "MODERATE_DELAY", "SEVERE_DELAY"]
    assert "delay" in pred["estimated_prediction_interval"]
    assert pred["traffic_level"] == "HIGH"
    assert pred["weather"] is not None

# 4. Driver Cockpit Tests
def test_driver_assigned_bus(db_session, driver_user):
    bus_info = get_driver_assigned_bus(db=db_session, driver_user=driver_user)
    assert bus_info["bus_number"] is not None
    assert len(bus_info["stops"]) > 0

def test_driver_trip_lifecycle(db_session, driver_user):
    route = db_session.query(Route).first()
    bus = db_session.query(Bus).filter(Bus.assigned_route_id == route.id).first()
    stop = db_session.query(Stop).filter(Stop.route_id == route.id).first()

    # 1. Start Trip
    start_req = TripStartRequest(route_id=route.id, bus_id=bus.id, trip_type="MORNING_INBOUND")
    new_trip = start_trip(trip_in=start_req, db=db_session, driver_user=driver_user)
    assert new_trip.id is not None
    assert new_trip.status == "IN_PROGRESS"
    assert new_trip.is_synthetic is False # Live observation!

    # 2. Report Traffic
    traffic_req = TrafficReportRequest(
        trip_id=new_trip.id,
        route_id=route.id,
        stop_id=stop.id,
        traffic_level="SEVERE",
        condition_type="HEAVY_CONGESTION",
        notes="Heavy bottle-neck at Eachanari junction due to temple crowd",
        estimated_delay_impact_mins=8
    )
    t_res = report_traffic_condition(traffic_in=traffic_req, db=db_session, driver_user=driver_user)
    assert t_res["status"] == "success"

    # 3. Update Stop Check-in
    update_req = TripUpdateRequest(
        trip_id=new_trip.id,
        stop_id=stop.id,
        traffic_level="SEVERE",
        dwell_time_seconds=45
    )
    u_res = update_trip_stop(update_in=update_req, db=db_session, driver_user=driver_user)
    assert u_res["status"] == "success"

    # 4. Verify Student Prediction uses latest active trip state
    active_pred = get_student_arrival_prediction(route_id=route.id, stop_id=stop.id, db=db_session)
    assert active_pred["trip_status"] == "IN_PROGRESS"
    assert active_pred["is_trip_completed"] is False

    # 5. Complete Trip
    complete_req = TripCompleteRequest(trip_id=new_trip.id)
    c_res = complete_trip(complete_in=complete_req, db=db_session, driver_user=driver_user)
    assert c_res["status"] == "success"

    # 6. Verify Student Prediction does NOT show approaching for completed trip
    completed_pred = get_student_arrival_prediction(route_id=route.id, stop_id=stop.id, db=db_session)
    assert completed_pred["is_trip_completed"] is True
    assert completed_pred["trip_status"] == "COMPLETED"
    assert completed_pred["predicted_remaining_travel_minutes"] == 0.0

# 5. Admin Dashboard & Model History Tests
def test_admin_dashboard(db_session, admin_user):
    dash = get_admin_dashboard(db=db_session, admin=admin_user)
    assert dash["total_routes"] >= 10
    assert dash["active_buses"] >= 10
    assert dash["champion_model_version"] is not None
    assert dash["champion_val_mae_minutes"] > 0.0

def test_admin_model_metrics(admin_user):
    metrics = get_model_metrics(admin=admin_user)
    assert "version" in metrics
    assert "validation_metrics" in metrics
    assert metrics["validation_metrics"]["delay_mae"] < 3.5

def test_admin_model_history(db_session, admin_user):
    history = get_model_history(db=db_session, admin=admin_user)
    assert len(history) >= 1
    active_entry = next((h for h in history if h.is_active), None)
    assert active_entry is not None
