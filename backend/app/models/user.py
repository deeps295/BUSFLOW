from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base

class User(Base):
    """Base user account for Sri Eshwar College transportation portal."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="STUDENT")  # ADMIN, DRIVER, STUDENT
    full_name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    driver_profile = relationship("Driver", back_populates="user", uselist=False, cascade="all, delete-orphan")
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Driver(Base):
    """Driver profile for SECE college bus drivers."""
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    experience_years = Column(Integer, default=0)
    assigned_bus_id = Column(Integer, ForeignKey("buses.id", ondelete="SET NULL"), nullable=True)
    contact_emergency = Column(String(20), nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="driver_profile")
    assigned_bus = relationship("Bus", foreign_keys=[assigned_bus_id], back_populates="assigned_driver")
    trips = relationship("Trip", back_populates="driver")
    traffic_reports = relationship("TrafficReport", back_populates="driver")


class Student(Base):
    """Student profile for SECE transport day scholars."""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    roll_number = Column(String(50), unique=True, nullable=False)  # e.g., "718121104001"
    department = Column(String(100), nullable=False)  # e.g., "CSE", "ECE", "AI&DS", "IT"
    year_of_study = Column(Integer, nullable=False, default=1)
    default_route_id = Column(Integer, ForeignKey("routes.id", ondelete="SET NULL"), nullable=True)
    default_stop_id = Column(Integer, ForeignKey("stops.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    default_route = relationship("Route", foreign_keys=[default_route_id])
    default_stop = relationship("Stop", foreign_keys=[default_stop_id])
