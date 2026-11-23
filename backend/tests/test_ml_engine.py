import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ml.predict import predict_arrival_delay, load_champion_model, classify_delay_severity
from app.ml.model_utils import (
    FEATURE_COLUMNS,
    TARGET_COLUMNS,
    HistoricalAverageBaseline,
    compute_regression_metrics,
    PredictionIntervalEstimator
)
from app.database.session import SessionLocal
from app.models.ml import ModelTrainingHistory

def test_feature_target_non_leakage():
    """Ensure no actual target or arrival timestamp features leak into training inputs."""
    forbidden = ["actual_delay_minutes", "actual_remaining_travel_minutes", "actual_arrival_time", "actual_departure_time"]
    for col in forbidden:
        assert col not in FEATURE_COLUMNS, f"Data leakage detected! '{col}' is present in FEATURE_COLUMNS."

def test_champion_model_loading():
    """Verify serialized champion pipeline bundle and metadata exist and load cleanly."""
    bundle = load_champion_model(force_reload=True)
    assert bundle is not None
    assert "pipeline" in bundle
    assert "version" in bundle
    assert "interval_estimator" in bundle
    assert bundle["data_authenticity"] == "Simulated-Data Performance (Synthetic Training Seeds)"

def test_predict_arrival_delay_on_sample_query():
    """Test inference on a realistic SECE route query."""
    query = {
        "route_id": "R01_BHARATHIAR",
        "stop_id": "R01_S05", # Ukkadam
        "day_of_week": "Monday",
        "departure_hour": 7,
        "departure_minute": 0,
        "scheduled_departure_time": "07:00:00",
        "scheduled_arrival_time": "07:37:00",
        "segment_distance_km": 4.8,
        "remaining_distance_km": 23.6,
        "number_of_remaining_stops": 5,
        "traffic_level": "HIGH",
        "weather_condition": "LIGHT_RAIN",
        "temperature": 26.5,
        "rainfall": 2.5,
        "humidity": 80.0,
        "previous_trip_delay": 2.0
    }
    result = predict_arrival_delay(query)
    
    assert result["status"] == "success"
    assert isinstance(result["predicted_delay_minutes"], float)
    assert isinstance(result["predicted_remaining_travel_minutes"], float)
    assert result["predicted_remaining_travel_minutes"] >= 0.0
    assert result["severity_status"] in ["ON_TIME", "MINOR_DELAY", "MODERATE_DELAY", "SEVERE_DELAY"]
    
    # Check prediction interval
    interval = result["prediction_interval"]
    assert "delay" in interval
    assert interval["delay"]["lower_bound_mins"] <= interval["delay"]["upper_bound_mins"]
    assert "Estimated Prediction Interval" in interval["delay"]["label"]

def test_predict_robustness_on_unseen_and_missing_inputs():
    """Inference must gracefully handle missing fields or unseen categorical values without crashing."""
    sparse_query = {
        "route_id": "UNKNOWN_NEW_ROUTE",
        "stop_id": "UNKNOWN_STOP",
        "traffic_level": "SEVERE"
        # Remaining numeric and categorical columns omitted intentionally
    }
    result = predict_arrival_delay(sparse_query)
    assert result["status"] == "success"
    assert isinstance(result["predicted_delay_minutes"], float)
    assert isinstance(result["predicted_remaining_travel_minutes"], float)

def test_historical_average_baseline():
    """Verify historical baseline regressor logic."""
    baseline = HistoricalAverageBaseline()
    X_toy = pd.DataFrame([
        {"route_id": "R1", "stop_id": "S1"},
        {"route_id": "R1", "stop_id": "S2"},
        {"route_id": "R2", "stop_id": "S1"},
    ])
    Y_toy = pd.DataFrame([
        {"actual_delay_minutes": 5.0, "actual_remaining_travel_minutes": 40.0},
        {"actual_delay_minutes": 10.0, "actual_remaining_travel_minutes": 30.0},
        {"actual_delay_minutes": 2.0, "actual_remaining_travel_minutes": 20.0},
    ])
    baseline.fit(X_toy, Y_toy)
    preds = baseline.predict(X_toy)
    assert preds.shape == (3, 2)
    assert preds[0, 0] == 5.0

def test_delay_severity_classifier():
    assert classify_delay_severity(0.5)[0] == "ON_TIME"
    assert classify_delay_severity(4.0)[0] == "MINOR_DELAY"
    assert classify_delay_severity(10.0)[0] == "MODERATE_DELAY"
    assert classify_delay_severity(22.0)[0] == "SEVERE_DELAY"

def test_model_training_history_in_database():
    """Verify that model training runs are audited in SQLite."""
    db = SessionLocal()
    try:
        active_model = db.query(ModelTrainingHistory).filter(ModelTrainingHistory.is_active == True).first()
        assert active_model is not None, "Expected an active model record in database"
        assert active_model.val_mae is not None
        assert active_model.test_mae is not None
        assert active_model.baseline_mae is not None
        assert active_model.synthetic_ratio == 1.0
    finally:
        db.close()
