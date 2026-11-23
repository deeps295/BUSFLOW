from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AdminDashboardResponse(BaseModel):
    total_routes: int
    active_buses: int
    registered_drivers: int
    registered_students: int
    total_trips_recorded: int
    active_trips_today: int
    synthetic_records_count: int
    synthetic_ratio_percentage: float
    champion_model_version: str
    champion_algorithm: str
    champion_val_mae_minutes: float
    recent_traffic_alerts_count: int

class ModelMetricsResponse(BaseModel):
    version: str
    model_name: str
    algorithm_type: str
    trained_at: str
    training_records_count: int
    validation_metrics: Dict[str, float]
    test_metrics: Dict[str, float]
    baseline_metrics: Dict[str, float]
    features_count: int
    data_authenticity_notice: str

class ModelHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_version: str
    model_name: str
    algorithm_type: str
    train_records_count: int
    synthetic_ratio: float
    val_mae: Optional[float] = None
    val_rmse: Optional[float] = None
    val_r2: Optional[float] = None
    test_mae: Optional[float] = None
    is_active: bool
    trained_at: datetime

class DatasetUploadResponse(BaseModel):
    status: str
    filename: str
    records_added: int
    total_records: int
    message: str

class DriverResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    license_number: str
    experience_years: int
    assigned_bus_id: Optional[int] = None
    assigned_bus_number: Optional[str] = None
    contact_emergency: Optional[str] = None
    is_available: bool

class DriverCreate(BaseModel):
    full_name: str
    email: str
    password: str = "driver123"
    phone: Optional[str] = None
    license_number: str
    experience_years: int = 1
    assigned_bus_id: Optional[int] = None
    contact_emergency: Optional[str] = None

class DriverUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    experience_years: Optional[int] = None
    assigned_bus_id: Optional[int] = None
    contact_emergency: Optional[str] = None
    is_available: Optional[bool] = None

class StudentResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    roll_number: str
    department: str
    year_of_study: int
    default_route_id: Optional[int] = None
    default_route_number: Optional[str] = None
    default_stop_id: Optional[int] = None
    default_stop_name: Optional[str] = None

class StudentCreate(BaseModel):
    full_name: str
    email: str
    password: str = "student123"
    phone: Optional[str] = None
    roll_number: str
    department: str
    year_of_study: int = 1
    default_route_id: Optional[int] = None
    default_stop_id: Optional[int] = None

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    roll_number: Optional[str] = None
    department: Optional[str] = None
    year_of_study: Optional[int] = None
    default_route_id: Optional[int] = None
    default_stop_id: Optional[int] = None
