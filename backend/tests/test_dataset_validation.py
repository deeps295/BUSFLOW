import sys
from pathlib import Path
import pandas as pd
import pytest

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.utils.data_validator import validate_datasets, COIMBATORE_BBOX, DATASETS_DIR
from app.ml.preprocessing import BusFlowPreprocessor, create_chronological_splits
from app.database.session import SessionLocal
from app.models.transport import Route, Stop

@pytest.fixture(scope="module")
def validation_report():
    return validate_datasets()

@pytest.fixture(scope="module")
def routes_df():
    return pd.read_csv(DATASETS_DIR / "college_routes.csv")

@pytest.fixture(scope="module")
def trips_df():
    return pd.read_csv(DATASETS_DIR / "bus_trip_history.csv")

def test_datasets_exist():
    assert (DATASETS_DIR / "college_routes.csv").exists(), "college_routes.csv must exist"
    assert (DATASETS_DIR / "bus_trip_history.csv").exists(), "bus_trip_history.csv must exist"

def test_validation_report_status(validation_report):
    assert validation_report["status"] == "PASSED", f"Validation errors: {validation_report['errors']}"
    assert validation_report["localization_verified"] is True
    assert len(validation_report["errors"]) == 0

def test_route_dataset_localization(routes_df):
    """Assert all stops strictly fall within Coimbatore transit bounds and terminate at SECE."""
    lats = routes_df["latitude"]
    lons = routes_df["longitude"]
    assert (lats >= COIMBATORE_BBOX["min_lat"]).all(), "Latitude below Coimbatore bbox"
    assert (lats <= COIMBATORE_BBOX["max_lat"]).all(), "Latitude above Coimbatore bbox"
    assert (lons >= COIMBATORE_BBOX["min_lon"]).all(), "Longitude below Coimbatore bbox"
    assert (lons <= COIMBATORE_BBOX["max_lon"]).all(), "Longitude above Coimbatore bbox"
    
    # Destination check
    assert routes_df["destination_name"].str.contains("SECE", case=False).all(), "All routes must terminate at SECE"

def test_trip_record_count(trips_df):
    """Assert trip record count is within the required 5,000 - 25,000 range."""
    count = len(trips_df)
    assert 5000 <= count <= 25000, f"Expected 5,000-25,000 records, got {count}"

def test_trip_routes_are_local_sece_only(trips_df, routes_df):
    """Ensure trips only reference local SECE college routes."""
    valid_routes = set(routes_df["route_id"].unique())
    trip_routes = set(trips_df["route_id"].unique())
    assert trip_routes.issubset(valid_routes), f"Foreign routes detected: {trip_routes - valid_routes}"

def test_no_duplicate_trip_segments(trips_df):
    duplicates = trips_df.duplicated(subset=["trip_id", "stop_id"]).sum()
    assert duplicates == 0, f"Found {duplicates} duplicate trip segments"

def test_synthetic_data_transparency_flag(trips_df):
    """Every generated trip history record must be explicitly tagged as synthetic."""
    assert (trips_df["is_synthetic"] == True).all(), "Synthetic records must be labeled is_synthetic=True"

def test_data_preprocessing_pipeline(trips_df):
    """Verify feature engineering and chronological train/val/test splitting."""
    preprocessor = BusFlowPreprocessor(clip_outliers=True)
    processed = preprocessor.fit_transform(trips_df)
    
    # Check engineered columns
    expected_new_cols = [
        "scheduled_hour", "scheduled_minute", "scheduled_time_minutes",
        "is_morning_peak", "is_evening_peak", "day_of_week_num",
        "traffic_level_ordinal", "weather_ordinal", "weather_friction_index"
    ]
    for col in expected_new_cols:
        assert col in processed.columns, f"Engineered column missing: {col}"
        
    # Check no missing values after preprocessing
    assert processed[expected_new_cols].isnull().sum().sum() == 0, "Engineered features have nulls"
    
    # Check chronological split
    train, val, test = create_chronological_splits(processed, 0.70, 0.15, 0.15)
    assert len(train) > 0 and len(val) > 0 and len(test) > 0
    
    # Assert strict date order across splits
    assert train["trip_date"].max() < val["trip_date"].min(), "Train/Val date overlap detected (data leakage!)"
    assert val["trip_date"].max() < test["trip_date"].min(), "Val/Test date overlap detected (data leakage!)"

def test_database_seeded_routes():
    """Verify that the SQLite database has been seeded with SECE routes & stops."""
    db = SessionLocal()
    try:
        route_count = db.query(Route).count()
        stop_count = db.query(Stop).count()
        assert route_count == 10, f"Expected 10 routes in DB, got {route_count}"
        assert stop_count == 88, f"Expected 88 stops in DB, got {stop_count}"
    finally:
        db.close()
