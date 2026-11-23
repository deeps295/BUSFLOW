from typing import Optional, List
from datetime import time, datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator

class StopCreate(BaseModel):
    stop_name: str
    stop_sequence: int
    latitude: float
    longitude: float
    distance_from_origin_km: float = 0.0
    scheduled_offset_minutes: int = 0
    landmark: Optional[str] = None

class StopResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stop_id: Optional[int] = None
    route_id: int
    stop_name: str
    stop_sequence: int
    latitude: float
    longitude: float
    distance_from_origin_km: float
    scheduled_offset_minutes: int
    landmark: Optional[str] = None

    @model_validator(mode="after")
    def populate_stop_id(self):
        if self.stop_id is None:
            self.stop_id = self.id
        return self

class RouteCreate(BaseModel):
    route_number: str
    route_name: str
    origin_name: str
    destination_name: str = "Sri Eshwar College of Engineering, Kinathukadavu"
    total_distance_km: float
    estimated_duration_minutes: int = 75
    morning_start_time: str = "07:00:00"
    evening_start_time: str = "16:45:00"
    stops: Optional[List[StopCreate]] = None

class RouteUpdate(BaseModel):
    route_name: Optional[str] = None
    origin_name: Optional[str] = None
    total_distance_km: Optional[float] = None
    estimated_duration_minutes: Optional[int] = None
    morning_start_time: Optional[str] = None
    evening_start_time: Optional[str] = None
    is_active: Optional[bool] = None

class RouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    route_id: Optional[int] = None
    route_number: str
    route_name: str
    origin_name: str
    destination_name: str
    total_distance_km: float
    estimated_duration_minutes: int
    morning_start_time: Optional[time] = None
    evening_start_time: Optional[time] = None
    is_active: bool
    stops: List[StopResponse] = []

    @model_validator(mode="after")
    def populate_route_id(self):
        if self.route_id is None:
            self.route_id = self.id
        return self

class BusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bus_number: str
    registration_number: str
    seating_capacity: int
    model_info: Optional[str] = None
    assigned_route_id: Optional[int] = None
    is_active: bool

class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    route_id: int
    bus_id: Optional[int] = None
    trip_type: str
    day_of_week: str
    departure_time: time
    expected_arrival_time: time
    is_active: bool
