from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base

class Trip(Base):
    """An execution instance of an SECE bus operating along a designated route."""
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id", ondelete="CASCADE"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True)
    trip_date = Column(Date, nullable=False, default=date.today, index=True)
    trip_type = Column(String(50), nullable=False, default="MORNING_INBOUND") # MORNING_INBOUND, EVENING_OUTBOUND
    scheduled_departure = Column(DateTime, nullable=False)
    actual_departure = Column(DateTime, nullable=True)
    scheduled_arrival = Column(DateTime, nullable=False)
    actual_arrival = Column(DateTime, nullable=True)
    status = Column(String(50), default="SCHEDULED", index=True) # SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    total_delay_minutes = Column(Float, default=0.0)
    weather_condition = Column(String(100), nullable=True)
    temperature_c = Column(Float, nullable=True)
    precipitation_mm = Column(Float, default=0.0)
    is_synthetic = Column(Boolean, default=False, index=True) # Transparency flag for ML seeds
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bus = relationship("Bus", back_populates="trips")
    route = relationship("Route", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    segments = relationship("TripSegment", back_populates="trip", order_by="TripSegment.stop_sequence", cascade="all, delete-orphan")
    traffic_reports = relationship("TrafficReport", back_populates="trip", cascade="all, delete-orphan")


class TripSegment(Base):
    """Stop-level arrival & departure record within a specific trip for ML delay regression."""
    __tablename__ = "trip_segments"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    stop_id = Column(Integer, ForeignKey("stops.id", ondelete="CASCADE"), nullable=False, index=True)
    stop_sequence = Column(Integer, nullable=False)
    scheduled_arrival_time = Column(DateTime, nullable=False)
    actual_arrival_time = Column(DateTime, nullable=True)
    scheduled_departure_time = Column(DateTime, nullable=True)
    actual_departure_time = Column(DateTime, nullable=True)
    delay_minutes = Column(Float, default=0.0) # Target regression variable
    dwell_time_seconds = Column(Integer, default=30)
    distance_from_prev_km = Column(Float, default=0.0)
    segment_traffic_level = Column(String(50), default="LOW") # LOW, MEDIUM, HIGH, SEVERE
    weather_temp_c = Column(Float, nullable=True)
    weather_rain_mm = Column(Float, default=0.0)
    is_synthetic = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    trip = relationship("Trip", back_populates="segments")
    stop = relationship("Stop", back_populates="trip_segments")


class TrafficReport(Base):
    """Real-time traffic or road condition updates submitted by drivers."""
    __tablename__ = "traffic_reports"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    stop_id = Column(Integer, ForeignKey("stops.id", ondelete="SET NULL"), nullable=True)
    traffic_level = Column(String(50), nullable=False) # LOW, MEDIUM, HIGH, SEVERE
    condition_type = Column(String(50), default="NORMAL") # NORMAL, HEAVY_CONGESTION, ACCIDENT, ROAD_WORK, WATERLOGGING, BREAKDOWN
    notes = Column(Text, nullable=True)
    estimated_delay_impact_mins = Column(Integer, default=0)
    reported_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    trip = relationship("Trip", back_populates="traffic_reports")
    driver = relationship("Driver", back_populates="traffic_reports")
    route = relationship("Route", back_populates="traffic_reports")
    stop = relationship("Stop")
