from datetime import datetime, date
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User, Driver
from app.models.transport import Route, Stop, Bus
from app.models.trip import Trip, TripSegment, TrafficReport
from app.schemas.trip import (
    TripStartRequest,
    TripUpdateRequest,
    TrafficReportRequest,
    WeatherSnapshotRequest,
    TripCompleteRequest,
    TripResponse
)
from app.api.deps import get_current_driver
from app.services.weather_service import get_current_sece_weather

router = APIRouter(prefix="/driver", tags=["Driver Cockpit"])

@router.get("/assigned-bus")
def get_driver_assigned_bus(
    db: Session = Depends(get_db),
    driver_user: User = Depends(get_current_driver)
):
    """Fetches assigned bus, route details, and live active trip for the logged-in driver."""
    driver_profile = db.query(Driver).filter(Driver.user_id == driver_user.id).first()
    if not driver_profile or not driver_profile.assigned_bus_id:
        # Fallback to Bus 1 if demo user
        bus = db.query(Bus).filter(Bus.is_active == True).first()
    else:
        bus = db.query(Bus).filter(Bus.id == driver_profile.assigned_bus_id).first()

    if not bus:
        raise HTTPException(status_code=404, detail="No active bus assigned to this driver.")

    route = db.query(Route).filter(Route.id == bus.assigned_route_id).first()
    stops = (
        db.query(Stop)
        .filter(Stop.route_id == (route.id if route else bus.assigned_route_id))
        .order_by(Stop.stop_sequence)
        .all()
    )

    # Check if there is an active trip right now
    today = date.today()
    active_trip = (
        db.query(Trip)
        .filter(Trip.bus_id == bus.id, Trip.trip_date == today, Trip.status.in_(["IN_PROGRESS", "SCHEDULED"]))
        .first()
    )

    return {
        "driver_id": driver_profile.id if driver_profile else 1,
        "driver_name": driver_user.full_name,
        "bus_id": bus.id,
        "bus_number": bus.bus_number,
        "registration_number": bus.registration_number,
        "route_id": route.id if route else None,
        "route_number": route.route_number if route else None,
        "route_name": route.route_name if route else None,
        "total_stops": len(stops),
        "stops": [
            {
                "id": s.id,
                "name": s.stop_name,
                "sequence": s.stop_sequence,
                "scheduled_offset_minutes": s.scheduled_offset_minutes,
                "distance_km": s.distance_from_origin_km
            }
            for s in stops
        ],
        "active_trip": {
            "id": active_trip.id,
            "status": active_trip.status,
            "trip_type": active_trip.trip_type,
            "actual_departure": active_trip.actual_departure
        } if active_trip else None
    }

@router.post("/trip/start", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def start_trip(
    trip_in: TripStartRequest,
    db: Session = Depends(get_db),
    driver_user: User = Depends(get_current_driver)
):
    """Driver marks commencement of morning or evening college bus run."""
    driver_profile = db.query(Driver).filter(Driver.user_id == driver_user.id).first()
    driver_id = driver_profile.id if driver_profile else None

    # Get bus
    bus = None
    if trip_in.bus_id:
        bus = db.query(Bus).filter(Bus.id == trip_in.bus_id).first()
    elif driver_profile and driver_profile.assigned_bus_id:
        bus = db.query(Bus).filter(Bus.id == driver_profile.assigned_bus_id).first()

    if not bus:
        bus = db.query(Bus).filter(Bus.assigned_route_id == trip_in.route_id).first()
        if not bus:
            raise HTTPException(status_code=404, detail="No bus assigned to this route.")

    route = db.query(Route).filter(Route.id == trip_in.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found.")

    now = datetime.now()
    weather = get_current_sece_weather()

    # Scheduled arrival is departure + estimated duration
    sched_arrival = now + datetime.resolution * 0 # initialized
    from datetime import timedelta
    sched_arrival = now + timedelta(minutes=route.estimated_duration_minutes)

    new_trip = Trip(
        bus_id=bus.id,
        route_id=route.id,
        driver_id=driver_id,
        trip_date=now.date(),
        trip_type=trip_in.trip_type,
        scheduled_departure=now,
        actual_departure=now,
        scheduled_arrival=sched_arrival,
        status="IN_PROGRESS",
        total_delay_minutes=0.0,
        weather_condition=weather.get("condition", "CLEAR"),
        temperature_c=weather.get("temperature_c", 28.0),
        precipitation_mm=weather.get("precipitation_mm", 0.0),
        is_synthetic=False # Live driver action is actual observation!
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return new_trip

@router.post("/trip/update")
def update_trip_stop(
    update_in: TripUpdateRequest,
    db: Session = Depends(get_db),
    driver_user: User = Depends(get_current_driver)
):
    """Driver logs arrival / departure at an intermediate stop along the route."""
    trip = db.query(Trip).filter(Trip.id == update_in.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")

    stop = db.query(Stop).filter(Stop.id == update_in.stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found.")

    now = datetime.now()
    arr_time = update_in.actual_arrival_time or now
    dep_time = update_in.actual_departure_time or (arr_time + datetime.resolution * 0)

    # Calculate delay in minutes compared to scheduled offset
    from datetime import timedelta
    sched_arr_time = trip.scheduled_departure + timedelta(minutes=stop.scheduled_offset_minutes)
    delay_mins = round((arr_time - sched_arr_time).total_seconds() / 60.0, 1)

    # Weather
    weather = get_current_sece_weather()

    # Log TripSegment
    segment = TripSegment(
        trip_id=trip.id,
        stop_id=stop.id,
        stop_sequence=stop.stop_sequence,
        scheduled_arrival_time=sched_arr_time,
        actual_arrival_time=arr_time,
        scheduled_departure_time=sched_arr_time + timedelta(seconds=30),
        actual_departure_time=dep_time,
        delay_minutes=delay_mins,
        dwell_time_seconds=update_in.dwell_time_seconds or 30,
        distance_from_prev_km=stop.distance_from_origin_km,
        segment_traffic_level=update_in.traffic_level or "LOW",
        weather_temp_c=weather.get("temperature_c", 28.0),
        weather_rain_mm=weather.get("precipitation_mm", 0.0),
        is_synthetic=False
    )
    db.add(segment)

    # Update cumulative delay on Trip
    trip.total_delay_minutes = delay_mins
    db.commit()

    return {
        "status": "success",
        "trip_id": trip.id,
        "stop_name": stop.stop_name,
        "sequence": stop.stop_sequence,
        "delay_minutes": delay_mins,
        "logged_at": now.isoformat()
    }

@router.post("/traffic")
def report_traffic_condition(
    traffic_in: TrafficReportRequest,
    db: Session = Depends(get_db),
    driver_user: User = Depends(get_current_driver)
):
    """Driver reports real-time traffic levels: LOW, MEDIUM, HIGH, SEVERE."""
    driver_profile = db.query(Driver).filter(Driver.user_id == driver_user.id).first()
    driver_id = driver_profile.id if driver_profile else 1

    report = TrafficReport(
        trip_id=traffic_in.trip_id,
        driver_id=driver_id,
        route_id=traffic_in.route_id,
        stop_id=traffic_in.stop_id,
        traffic_level=traffic_in.traffic_level,
        condition_type=traffic_in.condition_type,
        notes=traffic_in.notes,
        estimated_delay_impact_mins=traffic_in.estimated_delay_impact_mins or 0,
        reported_at=datetime.utcnow()
    )
    db.add(report)

    # If associated with an active trip, update trip
    if traffic_in.trip_id:
        trip = db.query(Trip).filter(Trip.id == traffic_in.trip_id).first()
        if trip and traffic_in.estimated_delay_impact_mins:
            trip.total_delay_minutes = (trip.total_delay_minutes or 0.0) + traffic_in.estimated_delay_impact_mins

    db.commit()
    db.refresh(report)

    return {
        "status": "success",
        "message": f"Traffic level '{traffic_in.traffic_level}' recorded successfully.",
        "report_id": report.id,
        "timestamp": report.reported_at.isoformat()
    }

@router.post("/weather")
def snapshot_weather_condition(
    weather_in: WeatherSnapshotRequest,
    db: Session = Depends(get_db),
    driver_user: User = Depends(get_current_driver)
):
    """Logs weather observations for an active trip."""
    trip = db.query(Trip).filter(Trip.id == weather_in.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")

    trip.weather_condition = weather_in.weather_condition
    trip.temperature_c = weather_in.temperature_c
    trip.precipitation_mm = weather_in.precipitation_mm
    db.commit()

    return {
        "status": "success",
        "trip_id": trip.id,
        "weather_condition": trip.weather_condition,
        "temperature_c": trip.temperature_c,
        "precipitation_mm": trip.precipitation_mm
    }

@router.post("/trip/complete")
def complete_trip(
    complete_in: TripCompleteRequest,
    db: Session = Depends(get_db),
    driver_user: User = Depends(get_current_driver)
):
    """Driver marks the trip as completed upon arrival at SECE Campus."""
    trip = db.query(Trip).filter(Trip.id == complete_in.trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")

    now = datetime.now()
    trip.status = "COMPLETED"
    trip.actual_arrival = now
    db.commit()

    return {
        "status": "success",
        "message": "Trip marked as COMPLETED. Bus has arrived safely at SECE Campus.",
        "trip_id": trip.id,
        "actual_arrival": now.isoformat(),
        "total_delay_minutes": trip.total_delay_minutes
    }
