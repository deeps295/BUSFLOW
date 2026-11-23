"""
BusFlow Prediction Service
Orchestrates database state, live driver traffic reports, Open-Meteo weather synthesis,
and champion ML regression inference.
"""

from datetime import datetime, date, time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.transport import Route, Stop, Bus
from app.models.trip import Trip, TripSegment, TrafficReport
from app.services.weather_service import get_current_sece_weather
from app.ml.predict import predict_arrival_delay

def get_live_student_prediction(
    route_id: int,
    stop_id: int,
    db: Session,
    override_traffic: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes real-time arrival prediction for a student at a specific stop on an SECE route.
    Guarantees that completed trips are not presented as still approaching.
    """
    # 1. Validate route and stop
    route = db.query(Route).filter(Route.id == route_id, Route.is_active == True).first()
    if not route:
        raise HTTPException(status_code=404, detail=f"Active route ID {route_id} not found.")

    stop = db.query(Stop).filter(Stop.id == stop_id, Stop.route_id == route_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail=f"Stop ID {stop_id} does not belong to route {route_id}.")

    # 2. Query today's latest trip for this route
    today = date.today()
    latest_trip = (
        db.query(Trip)
        .filter(Trip.route_id == route_id, Trip.trip_date == today)
        .order_by(Trip.id.desc())
        .first()
    )

    # If no trip found for today, check most recent trip
    if not latest_trip:
        latest_trip = (
            db.query(Trip)
            .filter(Trip.route_id == route_id)
            .order_by(Trip.id.desc())
            .first()
        )

    # 3. Determine Active / Scheduled Trip parameters
    trip_id = latest_trip.id if latest_trip else None
    trip_status = latest_trip.status if latest_trip else "SCHEDULED"
    is_completed = (latest_trip.status == "COMPLETED") if latest_trip else False

    # Latest driver traffic report
    traffic_level = override_traffic if isinstance(override_traffic, str) else None
    if not traffic_level:
        if latest_trip and latest_trip.status == "IN_PROGRESS":
            latest_traffic = (
                db.query(TrafficReport)
                .filter(TrafficReport.trip_id == latest_trip.id)
                .order_by(TrafficReport.reported_at.desc())
                .first()
            )
            traffic_level = latest_traffic.traffic_level if latest_traffic else "LOW"
        else:
            traffic_level = "LOW"

    # Upstream delay accumulation
    previous_delay = 0.0
    if latest_trip and latest_trip.status == "IN_PROGRESS":
        latest_segment = (
            db.query(TripSegment)
            .filter(TripSegment.trip_id == latest_trip.id)
            .order_by(TripSegment.stop_sequence.desc())
            .first()
        )
        if latest_segment and latest_segment.delay_minutes:
            previous_delay = float(latest_segment.delay_minutes)

    # Total and remaining route geometry
    total_stops = db.query(Stop).filter(Stop.route_id == route_id).count()
    remaining_stops = max(0, total_stops - stop.stop_sequence)
    remaining_dist_km = max(0.0, route.total_distance_km - stop.distance_from_origin_km)

    # Weather snapshot
    weather = get_current_sece_weather()

    # Scheduled departure and arrival times with stop sequence offset
    now = datetime.now()
    sched_dep_time = route.morning_start_time or time(7, 0, 0)
    stop_offset_mins = stop.scheduled_offset_minutes if stop.scheduled_offset_minutes > 0 else (stop.stop_sequence * 5)
    
    today = date.today()
    sched_dep_dt = datetime.combine(today, sched_dep_time)
    from datetime import timedelta
    sched_stop_dt = sched_dep_dt + timedelta(minutes=stop_offset_mins)
    sched_arrival_time = sched_stop_dt.time()

    # Map database route_number to dataset route_id
    clean_route_num = route.route_number.replace("Bus ", "").strip()
    dataset_route_id = f"R{int(clean_route_num):02d}" if clean_route_num.isdigit() else "R01"

    ml_input = {
        "route_id": dataset_route_id,
        "stop_id": f"{dataset_route_id}_S{stop.stop_sequence:02d}",
        "day_of_week": now.strftime("%A"),
        "departure_hour": sched_dep_time.hour,
        "departure_minute": sched_dep_time.minute,
        "scheduled_departure_time": sched_dep_time.strftime("%H:%M:%S"),
        "scheduled_arrival_time": sched_arrival_time.strftime("%H:%M:%S"),
        "segment_distance_km": round(stop.distance_from_origin_km / max(1, stop.stop_sequence), 1),
        "remaining_distance_km": round(remaining_dist_km, 1),
        "number_of_remaining_stops": remaining_stops,
        "traffic_level": traffic_level,
        "weather_condition": weather["condition"],
        "temperature": weather["temperature_c"],
        "rainfall": weather["precipitation_mm"],
        "humidity": weather["humidity_percent"],
        "previous_trip_delay": previous_delay
    }

    # 5. Run ML Regression
    ml_result = predict_arrival_delay(ml_input)

    if is_completed:
        predicted_arrival_str = "Trip Completed"
        predicted_remaining = 0.0
    else:
        predicted_arrival_str = ml_result.get("estimated_arrival_time") or sched_arrival_time.strftime("%H:%M:%S")
        predicted_remaining = ml_result["predicted_remaining_travel_minutes"]

    return {
        "route_id": route.id,
        "route_number": route.route_number,
        "route_name": route.route_name,
        "stop_id": stop.id,
        "stop_name": stop.stop_name,
        "trip_id": trip_id,
        "trip_status": trip_status,
        "is_trip_completed": is_completed,
        "scheduled_arrival": sched_arrival_time.strftime("%H:%M:%S"),
        "predicted_arrival_time": predicted_arrival_str,
        "predicted_remaining_travel_minutes": predicted_remaining,
        "expected_delay_minutes": ml_result["predicted_delay_minutes"],
        "predicted_delay_minutes": ml_result["predicted_delay_minutes"],
        "remaining_stops": remaining_stops,
        "severity_status": ml_result["severity_status"],
        "severity_label": ml_result["severity_label"],
        "traffic_level": traffic_level,
        "weather": weather,
        "estimated_prediction_interval": ml_result["prediction_interval"],
        "prediction_interval": ml_result["prediction_interval"],
        "model_version": ml_result["model_version"],
        "model_algorithm": ml_result["model_algorithm"],
        "last_updated_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "data_authenticity_notice": "Simulated-Data Performance (Synthetic Training Seeds)"
    }
