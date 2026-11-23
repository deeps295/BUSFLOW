from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict

class TripStartRequest(BaseModel):
    route_id: int
    bus_id: Optional[int] = None
    trip_type: str = Field("MORNING_INBOUND", pattern="^(MORNING_INBOUND|EVENING_OUTBOUND)$")

class TripUpdateRequest(BaseModel):
    trip_id: int
    stop_id: int
    actual_arrival_time: Optional[datetime] = None
    actual_departure_time: Optional[datetime] = None
    traffic_level: Optional[str] = Field("LOW", pattern="^(LOW|MEDIUM|HIGH|SEVERE)$")
    delay_minutes: Optional[float] = None
    dwell_time_seconds: Optional[int] = 30

class TrafficReportRequest(BaseModel):
    trip_id: Optional[int] = None
    route_id: int
    stop_id: Optional[int] = None
    traffic_level: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|SEVERE)$")
    condition_type: str = Field("NORMAL", pattern="^(NORMAL|HEAVY_CONGESTION|ACCIDENT|ROAD_WORK|WATERLOGGING|BREAKDOWN)$")
    notes: Optional[str] = None
    estimated_delay_impact_mins: Optional[int] = 0

class WeatherSnapshotRequest(BaseModel):
    trip_id: int
    weather_condition: str
    temperature_c: float
    precipitation_mm: float = 0.0

class TripCompleteRequest(BaseModel):
    trip_id: int
    notes: Optional[str] = None

class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bus_id: int
    route_id: int
    driver_id: Optional[int] = None
    trip_date: date
    trip_type: str
    scheduled_departure: datetime
    actual_departure: Optional[datetime] = None
    scheduled_arrival: datetime
    actual_arrival: Optional[datetime] = None
    status: str
    total_delay_minutes: float
    weather_condition: Optional[str] = None
    temperature_c: Optional[float] = None
    precipitation_mm: Optional[float] = None
    is_synthetic: bool
