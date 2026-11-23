from datetime import datetime, time
from sqlalchemy import Column, Integer, String, Boolean, Float, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base

class Bus(Base):
    """SECE fleet bus entity."""
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    bus_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "Bus 45", "Bus 40"
    registration_number = Column(String(50), unique=True, nullable=False)   # e.g., "TN 38 BZ 4501"
    seating_capacity = Column(Integer, default=55)
    model_info = Column(String(100), default="Ashok Leyland Viking")
    assigned_route_id = Column(Integer, ForeignKey("routes.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assigned_route = relationship("Route", back_populates="buses")
    assigned_driver = relationship("Driver", uselist=False, back_populates="assigned_bus")
    schedules = relationship("Schedule", back_populates="bus")
    trips = relationship("Trip", back_populates="bus")


class Route(Base):
    """SECE official college bus routes across Coimbatore & Pollachi."""
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    route_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "Route 45"
    route_name = Column(String(150), nullable=False)  # e.g., "Kanuvai to SECE Campus via Ukkadam"
    origin_name = Column(String(100), nullable=False)  # e.g., "Kanuvai"
    destination_name = Column(String(100), default="Sri Eshwar College of Engineering, Kinathukadavu")
    total_distance_km = Column(Float, nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=False)
    morning_start_time = Column(Time, default=time(7, 0, 0))   # 07:00 AM
    evening_start_time = Column(Time, default=time(16, 45, 0)) # 04:45 PM
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    stops = relationship("Stop", back_populates="route", order_by="Stop.stop_sequence", cascade="all, delete-orphan")
    buses = relationship("Bus", back_populates="assigned_route")
    schedules = relationship("Schedule", back_populates="route", cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="route")
    traffic_reports = relationship("TrafficReport", back_populates="route")


class Stop(Base):
    """Designated boarding/drop-off stop along an SECE route."""
    __tablename__ = "stops"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    stop_name = Column(String(150), nullable=False, index=True)  # e.g., "Ukkadam Bus Stand"
    stop_sequence = Column(Integer, nullable=False)               # 1, 2, 3, ...
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    distance_from_origin_km = Column(Float, default=0.0)
    scheduled_offset_minutes = Column(Integer, default=0)         # Minutes after route departure
    landmark = Column(String(200), nullable=True)

    # Relationships
    route = relationship("Route", back_populates="stops")
    trip_segments = relationship("TripSegment", back_populates="stop")


class Schedule(Base):
    """Operational timetable for a route & bus."""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id", ondelete="SET NULL"), nullable=True)
    trip_type = Column(String(50), nullable=False, default="MORNING_INBOUND")  # MORNING_INBOUND, EVENING_OUTBOUND
    day_of_week = Column(String(20), nullable=False, default="MONDAY")          # MONDAY to SATURDAY
    departure_time = Column(Time, nullable=False)
    expected_arrival_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    route = relationship("Route", back_populates="schedules")
    bus = relationship("Bus", back_populates="schedules")
