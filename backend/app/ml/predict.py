"""
BusFlow Inference Engine
Loads the serialized champion Scikit-Learn regression pipeline and serves real-time predictions:
- Predicted arrival delay (minutes)
- Predicted remaining travel time to SECE campus (minutes)
- Statistical 80% estimated prediction interval (validation residual method)
- Delay severity classification (ON_TIME, MINOR_DELAY, MODERATE_DELAY, SEVERE_DELAY)
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Union, Optional, Tuple
import pandas as pd
import numpy as np
import joblib

from app.ml.model_utils import extract_features_and_targets, FEATURE_COLUMNS

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "trained_models"
CHAMPION_MODEL_PATH = MODELS_DIR / "champion_model.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"

_cached_bundle: Optional[Dict[str, Any]] = None
_cached_metadata: Optional[Dict[str, Any]] = None

def load_champion_model(force_reload: bool = False) -> Dict[str, Any]:
    """Loads and caches the champion pipeline and metadata manifest."""
    global _cached_bundle, _cached_metadata

    if _cached_bundle is not None and not force_reload:
        return _cached_bundle

    if not CHAMPION_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No trained champion model found at {CHAMPION_MODEL_PATH}. "
            "Please run train_model.py first."
        )

    bundle = joblib.load(CHAMPION_MODEL_PATH)
    _cached_bundle = bundle

    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r") as f:
            _cached_metadata = json.load(f)
    else:
        _cached_metadata = {"version": bundle.get("version", "v1.0.0")}

    return _cached_bundle

def classify_delay_severity(delay_minutes: float) -> Tuple[str, str]:
    """Returns classification tag and user-facing status label."""
    if delay_minutes <= 2.0:
        return "ON_TIME", "On Time / Nominal"
    elif delay_minutes <= 7.0:
        return "MINOR_DELAY", "Minor Delay (3-7 mins)"
    elif delay_minutes <= 15.0:
        return "MODERATE_DELAY", "Moderate Delay (8-15 mins)"
    else:
        return "SEVERE_DELAY", "Significant Delay (>15 mins)"

def predict_arrival_delay(input_data: Union[Dict[str, Any], pd.DataFrame]) -> Dict[str, Any]:
    """
    Primary prediction function for student and driver queries.
    Returns point estimates, estimated prediction intervals, and delay status.
    """
    bundle = load_champion_model()
    pipeline = bundle["pipeline"]
    interval_estimator = bundle.get("interval_estimator")
    version = bundle.get("version", "v1.0.0")
    model_name = bundle.get("model_name", "HistGradientBoosting")

    if isinstance(input_data, dict):
        df_in = pd.DataFrame([input_data])
    else:
        df_in = input_data.copy()

    # Feature extraction (ensures departure_hour and minute are derived)
    X, _ = extract_features_and_targets(df_in)

    # Execute ML regression pipeline
    raw_preds = pipeline.predict(X)
    preds = np.array(raw_preds)
    if preds.ndim == 1:
        preds = preds.reshape(1, -1)

    predicted_delay = float(np.round(preds[0, 0], 1))
    predicted_remaining = float(np.round(np.maximum(0.0, preds[0, 1]), 1))

    # Prediction Intervals (Validation residual method)
    intervals_data = {}
    margin_delay = 2.5
    margin_remaining = 3.5

    if interval_estimator is not None:
        interval_res = interval_estimator.get_intervals(preds)
        delay_int = interval_res["delay_interval"]
        rem_int = interval_res["remaining_time_interval"]
        margin_delay = delay_int["margin_minutes"]
        margin_remaining = rem_int["margin_minutes"]

        intervals_data = {
            "delay": {
                "lower_bound_mins": float(delay_int["lower_bound"][0]),
                "upper_bound_mins": float(delay_int["upper_bound"][0]),
                "uncertainty_margin_mins": margin_delay,
                "label": "80% Estimated Prediction Interval (Validation Residual Quantile Method)"
            },
            "remaining_travel": {
                "lower_bound_mins": float(rem_int["lower_bound"][0]),
                "upper_bound_mins": float(rem_int["upper_bound"][0]),
                "uncertainty_margin_mins": margin_remaining,
                "label": "80% Estimated Prediction Interval (Validation Residual Quantile Method)"
            }
        }
    else:
        intervals_data = {
            "delay": {
                "lower_bound_mins": round(predicted_delay - 2.5, 1),
                "upper_bound_mins": round(predicted_delay + 2.5, 1),
                "uncertainty_margin_mins": 2.5,
                "label": "Estimated Prediction Interval (±2.5 mins)"
            }
        }

    status_tag, status_label = classify_delay_severity(predicted_delay)

    # Calculate estimated arrival timestamp if scheduled_arrival_time was provided
    estimated_arrival_clock = None
    if "scheduled_arrival_time" in df_in.columns and pd.notnull(df_in["scheduled_arrival_time"].iloc[0]):
        try:
            sched_str = str(df_in["scheduled_arrival_time"].iloc[0])
            today = datetime.now().date()
            h, m, s = map(int, sched_str.split(":"))
            sched_dt = datetime.combine(today, datetime.min.time()).replace(hour=h, minute=m, second=s)
            est_dt = sched_dt + timedelta(minutes=predicted_delay)
            estimated_arrival_clock = est_dt.strftime("%H:%M:%S")
        except Exception:
            estimated_arrival_clock = None

    return {
        "status": "success",
        "route_id": str(df_in["route_id"].iloc[0]) if "route_id" in df_in.columns else "UNKNOWN",
        "stop_id": str(df_in["stop_id"].iloc[0]) if "stop_id" in df_in.columns else "UNKNOWN",
        "predicted_delay_minutes": predicted_delay,
        "predicted_remaining_travel_minutes": predicted_remaining,
        "estimated_arrival_time": estimated_arrival_clock,
        "severity_status": status_tag,
        "severity_label": status_label,
        "prediction_interval": intervals_data,
        "model_version": version,
        "model_algorithm": model_name,
        "data_authenticity_notice": "Simulated-Data Performance (Synthetic Training Seeds)"
    }
