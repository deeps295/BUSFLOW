from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    route_id: int
    stop_id: int
    current_time: Optional[str] = None
    traffic_level: Optional[str] = Field(None, pattern="^(LOW|MEDIUM|HIGH|SEVERE)$")
    weather_condition: Optional[str] = None
    temperature: Optional[float] = None
    rainfall: Optional[float] = None
    humidity: Optional[float] = None
    previous_trip_delay: Optional[float] = None

class PredictionInterval(BaseModel):
    lower_bound_mins: float
    upper_bound_mins: float
    uncertainty_margin_mins: float
    label: str

class PredictionIntervals(BaseModel):
    delay: PredictionInterval
    remaining_travel: Optional[PredictionInterval] = None

class WeatherAttribution(BaseModel):
    source: str = "Open-Meteo (open-meteo.com)"
    license: str = "CC BY 4.0"
    area_note: str = "Area-level weather estimate for Sri Eshwar College / Kinathukadavu (10.85° N, 76.98° E)"

class WeatherSnapshot(BaseModel):
    condition: str
    temperature_c: float
    precipitation_mm: float
    humidity_percent: float
    attribution: WeatherAttribution

class PredictionResponse(BaseModel):
    route_id: int
    route_number: str
    route_name: str
    stop_id: int
    stop_name: str
    trip_id: Optional[int] = None
    trip_status: str # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    is_trip_completed: bool = False
    scheduled_arrival: Optional[str] = None
    predicted_arrival_time: Optional[str] = None
    predicted_remaining_travel_minutes: float
    expected_delay_minutes: float
    predicted_delay_minutes: Optional[float] = None
    remaining_stops: Optional[int] = None
    severity_status: str # ON_TIME, MINOR_DELAY, MODERATE_DELAY, SEVERE_DELAY
    severity_label: str
    traffic_level: str
    weather: WeatherSnapshot
    estimated_prediction_interval: Optional[PredictionIntervals] = None
    prediction_interval: Optional[Dict[str, Any]] = None
    model_version: str
    model_algorithm: str
    last_updated_time: str
    data_authenticity_notice: str = "Simulated-Data Performance (Synthetic Training Seeds)"

class StudentTripStatusResponse(BaseModel):
    route_id: int
    route_name: str
    bus_number: Optional[str] = None
    trip_id: Optional[int] = None
    trip_status: str
    current_stop_name: Optional[str] = None
    next_stop_name: Optional[str] = None
    completed_stops_count: int
    total_stops_count: int
    progress_percentage: float
    current_delay_minutes: float
    traffic_level: str
    weather_summary: str
    last_reported_time: Optional[datetime] = None
