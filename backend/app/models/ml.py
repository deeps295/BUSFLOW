from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base

class ModelTrainingHistory(Base):
    """Registry and audit history for all trained ML regression models."""
    __tablename__ = "model_training_history"

    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String(50), nullable=False, unique=True, index=True) # e.g., "v1.0.0"
    model_name = Column(String(100), nullable=False) # e.g., "HistGradientBoostingRegressor"
    algorithm_type = Column(String(100), nullable=False) # HistGradientBoosting, RandomForest, LinearRegression
    hyperparameters_json = Column(Text, nullable=True)
    
    # Dataset audit metadata
    train_records_count = Column(Integer, nullable=False, default=0)
    synthetic_records_count = Column(Integer, default=0)
    synthetic_ratio = Column(Float, default=0.0) # Explicit ratio of synthetic data
    
    # Validation & Test regression metrics
    train_mae = Column(Float, nullable=True)
    train_rmse = Column(Float, nullable=True)
    train_r2 = Column(Float, nullable=True)
    
    val_mae = Column(Float, nullable=True)
    val_rmse = Column(Float, nullable=True)
    val_r2 = Column(Float, nullable=True)
    
    test_mae = Column(Float, nullable=True)
    test_rmse = Column(Float, nullable=True)
    test_r2 = Column(Float, nullable=True)
    
    # Baseline comparison metrics
    baseline_mae = Column(Float, nullable=True)
    baseline_rmse = Column(Float, nullable=True)
    
    # Deployment status
    artifact_filepath = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=False, index=True) # Champion model flag
    trained_at = Column(DateTime, default=datetime.utcnow)
    trained_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    trained_by_user = relationship("User")
