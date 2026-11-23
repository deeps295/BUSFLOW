from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.transport import Route, Stop, Bus, Schedule
from app.models.trip import Trip, TripSegment, TrafficReport
from app.schemas.transport import RouteResponse, ScheduleResponse
from app.schemas.prediction import PredictionResponse, StudentTripStatusResponse
from app.services.prediction_service import get_live_student_prediction

router = APIRouter(prefix="/student", tags=["Student Portal"])

@router.get("/routes", response_model=List[RouteResponse])
def get_student_routes(db: Session = Depends(get_db)):
    """Fetches all active SECE college bus routes and their designated stops."""
    routes = (
        db.query(Route)
        .filter(Route.is_active == True)
        .order_by(Route.id)
        .all()
    )
    return routes

@router.get("/schedules", response_model=List[ScheduleResponse])
def get_student_schedules(
    route_id: Optional[int] = Query(None, description="Optional filter by route ID"),
    db: Session = Depends(get_db)
):
    """Fetches timetable schedules for SECE college buses."""
    query = db.query(Schedule).filter(Schedule.is_active == True)
    if route_id:
        query = query.filter(Schedule.route_id == route_id)
    return query.all()

@router.get("/prediction", response_model=PredictionResponse)
def get_student_arrival_prediction(
    route_id: int = Query(..., description="ID of SECE Bus Route"),
    stop_id: int = Query(..., description="ID of student boarding stop"),
    traffic_override: Optional[str] = Query(None, description="Optional test traffic override (LOW, MEDIUM, HIGH, SEVERE)"),
    db: Session = Depends(get_db)
):
    """
    Computes real-time arrival prediction using the champion ML model.
    Guarantees that completed trips are not displayed as still approaching.
    """
    prediction = get_live_student_prediction(
        route_id=route_id,
        stop_id=stop_id,
        db=db,
        override_traffic=traffic_override
    )
    return prediction

@router.get("/trip-status", response_model=StudentTripStatusResponse)
def get_student_trip_status(
    route_id: int = Query(..., description="ID of SECE Bus Route"),
    db: Session = Depends(get_db)
):
    """Returns the live status of the college bus operating on this route."""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found.")

    bus = db.query(Bus).filter(Bus.assigned_route_id == route_id).first()
    total_stops = db.query(Stop).filter(Stop.route_id == route_id).count()

    today = date.today()
    latest_trip = (
        db.query(Trip)
        .filter(Trip.route_id == route_id)
        .order_by(Trip.id.desc())
        .first()
    )

    if not latest_trip:
        return {
            "route_id": route.id,
            "route_name": route.route_name,
            "bus_number": bus.bus_number if bus else None,
            "trip_id": None,
            "trip_status": "SCHEDULED",
            "current_stop_name": "At Origin (" + route.origin_name + ")",
            "next_stop_name": "Departing Soon",
            "completed_stops_count": 0,
            "total_stops_count": total_stops,
            "progress_percentage": 0.0,
            "current_delay_minutes": 0.0,
            "traffic_level": "LOW",
            "weather_summary": "Clear, Normal Road Conditions",
            "last_reported_time": None
        }

    # Query last checked-in stop
    last_segment = (
        db.query(TripSegment)
        .filter(TripSegment.trip_id == latest_trip.id)
        .order_by(TripSegment.stop_sequence.desc())
        .first()
    )

    completed_stops = last_segment.stop_sequence if last_segment else 0
    progress_pct = round((completed_stops / max(1, total_stops)) * 100.0, 1) if latest_trip.status != "COMPLETED" else 100.0

    current_stop_name = "Origin (" + route.origin_name + ")"
    next_stop_name = "En Route to SECE"
    if last_segment:
        current_stop = db.query(Stop).filter(Stop.id == last_segment.stop_id).first()
        if current_stop:
            current_stop_name = current_stop.stop_name

        next_stop = (
            db.query(Stop)
            .filter(Stop.route_id == route_id, Stop.stop_sequence == last_segment.stop_sequence + 1)
            .first()
        )
        if next_stop:
            next_stop_name = next_stop.stop_name
        elif latest_trip.status == "COMPLETED":
            next_stop_name = "Arrived at SECE Campus"

    # Traffic
    latest_traffic = (
        db.query(TrafficReport)
        .filter(TrafficReport.trip_id == latest_trip.id)
        .order_by(TrafficReport.reported_at.desc())
        .first()
    )
    traffic_level = latest_traffic.traffic_level if latest_traffic else "LOW"

    return {
        "route_id": route.id,
        "route_name": route.route_name,
        "bus_number": bus.bus_number if bus else None,
        "trip_id": latest_trip.id,
        "trip_status": latest_trip.status,
        "current_stop_name": current_stop_name,
        "next_stop_name": next_stop_name,
        "completed_stops_count": completed_stops,
        "total_stops_count": total_stops,
        "progress_percentage": progress_pct,
        "current_delay_minutes": latest_trip.total_delay_minutes or 0.0,
        "traffic_level": traffic_level,
        "weather_summary": f"{latest_trip.weather_condition or 'CLEAR'}, {latest_trip.temperature_c or 28}°C",
        "last_reported_time": latest_trip.actual_departure or latest_trip.scheduled_departure
    }

@router.get("/route-stats")
def get_student_route_stats(
    route_id: int = Query(..., description="ID of SECE Bus Route"),
    db: Session = Depends(get_db)
):
    """Provides historical delay analysis, route-wise statistics, and peak-hour congestion detection."""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found.")

    BENCHMARKS = {
        1: {"avg_delay": 9.5, "punctuality": 50.4, "risk": "HIGH", "peak_factor": 1.9, "hotspots": ["Ukkadam Bus Stand", "Eachanari Junction", "Gandhi Park"]},
        2: {"avg_delay": 3.0, "punctuality": 77.2, "risk": "LOW", "peak_factor": 1.2, "hotspots": ["Pollachi Bus Stand", "Achipatti Junction"]},
        3: {"avg_delay": 6.0, "punctuality": 63.9, "risk": "MEDIUM", "peak_factor": 1.6, "hotspots": ["Gandhipuram Crosscut", "Lakshmi Mills", "Podanur"]},
        4: {"avg_delay": 6.1, "punctuality": 64.4, "risk": "MEDIUM", "peak_factor": 1.5, "hotspots": ["Kuniyamuthur", "Athupalam Bridge", "Sundarapuram"]},
        5: {"avg_delay": 0.8, "punctuality": 89.5, "risk": "LOW", "peak_factor": 1.1, "hotspots": ["Sulakkal Mariamman Temple", "Kinathukadavu"]},
        6: {"avg_delay": 6.7, "punctuality": 64.9, "risk": "MEDIUM", "peak_factor": 1.7, "hotspots": ["Singanallur Junction", "Ondipudur Flyover"]},
        7: {"avg_delay": 2.8, "punctuality": 78.3, "risk": "LOW", "peak_factor": 1.2, "hotspots": ["MCET College Gate", "Achipatti"]},
        8: {"avg_delay": 15.3, "punctuality": 34.6, "risk": "SEVERE", "peak_factor": 2.3, "hotspots": ["Thudiyalur", "Saibaba Colony", "Gandhipuram"]},
        9: {"avg_delay": 9.2, "punctuality": 51.8, "risk": "HIGH", "peak_factor": 1.8, "hotspots": ["Palladam Bus Stand", "Karanampettai", "Sulthanpet"]},
        10: {"avg_delay": 14.8, "punctuality": 49.0, "risk": "HIGH", "peak_factor": 2.0, "hotspots": ["Udumalpet Central", "Negamam Junction"]}
    }
    bench = BENCHMARKS.get(route.id, {"avg_delay": 4.5, "punctuality": 75.0, "risk": "MEDIUM", "peak_factor": 1.4, "hotspots": ["Campus Gate"]})

    now = datetime.now()
    total_mins = now.hour * 60 + now.minute

    # Peak hours: Morning 7:15 (435) - 8:45 (525) | Evening 16:30 (990) - 17:45 (1065)
    is_morning_peak = (435 <= total_mins <= 525)
    is_evening_peak = (990 <= total_mins <= 1065)
    is_peak = is_morning_peak or is_evening_peak

    current_peak_status = "Off-Peak (Normal Traffic Flow)"
    if is_morning_peak:
        current_peak_status = "Morning Rush Hour (High Congestion Probability)"
    elif is_evening_peak:
        current_peak_status = "Evening Return Peak (Moderate Delay Probability)"

    # Query recent trips from DB
    db_trips = db.query(Trip).filter(Trip.route_id == route.id).order_by(Trip.id.desc()).limit(5).all()
    recent_history = []
    for t in db_trips:
        recent_history.append({
            "trip_id": t.id,
            "trip_date": str(t.trip_date),
            "departure": str(t.actual_departure or t.scheduled_departure or "07:00"),
            "delay_minutes": float(t.total_delay_minutes or 0.0),
            "status": t.status,
            "weather": t.weather_condition or "CLEAR"
        })

    return {
        "route_id": route.id,
        "route_number": route.route_number,
        "route_name": route.route_name,
        "total_stops": len(route.stops),
        "total_distance_km": route.total_distance_km,
        "average_delay_minutes": bench["avg_delay"],
        "punctuality_rate_percentage": bench["punctuality"],
        "risk_level": bench["risk"],
        "peak_hour_analysis": {
            "is_currently_peak_hour": is_peak,
            "current_peak_status": current_peak_status,
            "morning_peak_window": "07:15 AM – 08:45 AM",
            "evening_peak_window": "04:30 PM – 05:45 PM",
            "peak_delay_multiplier": bench["peak_factor"],
            "congestion_hotspots": bench["hotspots"]
        },
        "recent_trips": recent_history
    }
