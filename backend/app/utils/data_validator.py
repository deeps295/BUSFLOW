"""
BusFlow Dataset Validator
Performs comprehensive data quality audits on college_routes.csv and bus_trip_history.csv:
- Strict Coimbatore & SECE localization verification
- Schema & column integrity
- Missing value audit
- Duplicate record detection
- Coordinate and distance sanity checks
- Outlier inspection (IQR analysis for delay and travel times)
- Synthetic data transparency verification
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np

DATASETS_DIR = Path(__file__).resolve().parent.parent.parent / "datasets"

# Coimbatore & surrounding transit bounding box
COIMBATORE_BBOX = {
    "min_lat": 10.45,
    "max_lat": 11.25,
    "min_lon": 76.75,
    "max_lon": 77.35,
}

REQUIRED_ROUTE_COLUMNS = [
    "route_id", "route_number", "route_name", "origin_name", "destination_name",
    "stop_id", "stop_name", "stop_sequence", "latitude", "longitude",
    "segment_distance_km", "distance_from_origin_km", "scheduled_offset_minutes"
]

REQUIRED_TRIP_COLUMNS = [
    "trip_id", "bus_id", "route_id", "stop_id", "trip_date", "day_of_week",
    "scheduled_departure_time", "actual_departure_time", "scheduled_arrival_time",
    "actual_arrival_time", "segment_distance_km", "remaining_distance_km",
    "number_of_remaining_stops", "traffic_level", "weather_condition",
    "temperature", "rainfall", "humidity", "previous_trip_delay",
    "actual_delay_minutes", "actual_remaining_travel_minutes", "is_synthetic"
]

def validate_datasets(
    routes_path: Path = DATASETS_DIR / "college_routes.csv",
    trips_path: Path = DATASETS_DIR / "bus_trip_history.csv"
) -> Dict[str, Any]:
    """Run full validation suite on the datasets."""
    report = {
        "status": "PASSED",
        "errors": [],
        "warnings": [],
        "routes_summary": {},
        "trips_summary": {},
        "outliers": {},
        "localization_verified": False
    }

    # 1. File existence
    if not routes_path.exists():
        report["status"] = "FAILED"
        report["errors"].append(f"Missing routes dataset: {routes_path}")
        return report

    if not trips_path.exists():
        report["status"] = "FAILED"
        report["errors"].append(f"Missing trips dataset: {trips_path}")
        return report

    df_routes = pd.read_csv(routes_path)
    df_trips = pd.read_csv(trips_path)

    # 2. Schema check - Routes
    missing_route_cols = [c for c in REQUIRED_ROUTE_COLUMNS if c not in df_routes.columns]
    if missing_route_cols:
        report["status"] = "FAILED"
        report["errors"].append(f"Routes missing required columns: {missing_route_cols}")

    # 3. Schema check - Trips
    missing_trip_cols = [c for c in REQUIRED_TRIP_COLUMNS if c not in df_trips.columns]
    if missing_trip_cols:
        report["status"] = "FAILED"
        report["errors"].append(f"Trips missing required columns: {missing_trip_cols}")

    # 4. Localization check (Strict SECE & Coimbatore coordinates)
    invalid_coords = df_routes[
        (df_routes["latitude"] < COIMBATORE_BBOX["min_lat"]) |
        (df_routes["latitude"] > COIMBATORE_BBOX["max_lat"]) |
        (df_routes["longitude"] < COIMBATORE_BBOX["min_lon"]) |
        (df_routes["longitude"] > COIMBATORE_BBOX["max_lon"])
    ]
    if len(invalid_coords) > 0:
        report["status"] = "FAILED"
        report["errors"].append(
            f"Found {len(invalid_coords)} stop coordinates outside Coimbatore transit bounding box!"
        )
    else:
        report["localization_verified"] = True

    # Check destinations all terminate at SECE
    non_sece_dest = df_routes[~df_routes["destination_name"].str.contains("SECE", case=False, na=False)]
    if len(non_sece_dest) > 0:
        report["status"] = "FAILED"
        report["errors"].append(f"Found {len(non_sece_dest)} routes not terminating at SECE Campus!")

    # Check that trips only use routes present in college_routes.csv
    valid_routes = set(df_routes["route_id"].unique())
    trip_routes = set(df_trips["route_id"].unique())
    unknown_routes = trip_routes - valid_routes
    if unknown_routes:
        report["status"] = "FAILED"
        report["errors"].append(f"Trips reference unknown route IDs: {unknown_routes}")

    # 5. Missing Values Audit
    routes_missing = df_routes.isnull().sum().to_dict()
    trips_missing = df_trips.isnull().sum().to_dict()
    
    total_trips_missing = sum(trips_missing.values())
    if total_trips_missing > 0:
        report["warnings"].append(f"Trips dataset contains {total_trips_missing} missing values.")

    # 6. Duplicate Detection
    trip_duplicates = df_trips.duplicated(subset=["trip_id", "stop_id"]).sum()
    if trip_duplicates > 0:
        report["status"] = "FAILED"
        report["errors"].append(f"Found {trip_duplicates} duplicate trip-segment records!")

    # 7. Synthetic Data Transparency Audit
    non_synthetic_count = (df_trips["is_synthetic"] != True).sum()
    if non_synthetic_count > 0:
        report["warnings"].append(
            f"{non_synthetic_count} trip records are not flagged as is_synthetic=True."
        )

    # 8. Outlier Inspection using IQR
    for col in ["actual_delay_minutes", "actual_remaining_travel_minutes"]:
        q25 = df_trips[col].quantile(0.25)
        q75 = df_trips[col].quantile(0.75)
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr
        outliers = df_trips[(df_trips[col] < lower_bound) | (df_trips[col] > upper_bound)]
        report["outliers"][col] = {
            "q25": round(float(q25), 2),
            "q75": round(float(q75), 2),
            "iqr": round(float(iqr), 2),
            "lower_bound": round(float(lower_bound), 2),
            "upper_bound": round(float(upper_bound), 2),
            "outlier_count": int(len(outliers)),
            "outlier_percentage": round(float(len(outliers) / len(df_trips) * 100), 2)
        }

    # 9. Summary Statistics
    report["routes_summary"] = {
        "total_stops": int(len(df_routes)),
        "unique_routes": int(df_routes["route_id"].nunique()),
        "avg_stops_per_route": round(float(len(df_routes) / df_routes["route_id"].nunique()), 1),
        "total_network_distance_km": round(float(df_routes.groupby("route_id")["total_route_distance_km"].first().sum()), 2),
        "major_junctions_count": int(df_routes["is_major_junction"].sum()),
        "missing_values": routes_missing
    }

    report["trips_summary"] = {
        "total_records": int(len(df_trips)),
        "unique_trips": int(df_trips["trip_id"].nunique()),
        "date_range_start": str(df_trips["trip_date"].min()),
        "date_range_end": str(df_trips["trip_date"].max()),
        "delay_mean_mins": round(float(df_trips["actual_delay_minutes"].mean()), 2),
        "delay_std_mins": round(float(df_trips["actual_delay_minutes"].std()), 2),
        "delay_min_mins": round(float(df_trips["actual_delay_minutes"].min()), 2),
        "delay_max_mins": round(float(df_trips["actual_delay_minutes"].max()), 2),
        "traffic_distribution": df_trips["traffic_level"].value_counts().to_dict(),
        "weather_distribution": df_trips["weather_condition"].value_counts().to_dict(),
        "synthetic_records_ratio": round(float(df_trips["is_synthetic"].sum() / len(df_trips)), 4),
        "missing_values": trips_missing
    }

    return report

if __name__ == "__main__":
    report = validate_datasets()
    print("\n=== BusFlow Dataset Validation Report ===")
    print(f"Overall Status: {report['status']}")
    print(f"Localization Verified: {report['localization_verified']}")
    print(f"Total Routes: {report['routes_summary']['unique_routes']}, Total Stops: {report['routes_summary']['total_stops']}")
    print(f"Total Trip Segments: {report['trips_summary']['total_records']} across {report['trips_summary']['unique_trips']} trips")
    print(f"Delay (Mean ± Std): {report['trips_summary']['delay_mean_mins']} ± {report['trips_summary']['delay_std_mins']} mins")
    print(f"Traffic Distribution: {report['trips_summary']['traffic_distribution']}")
    print(f"Synthetic Ratio: {report['trips_summary']['synthetic_records_ratio'] * 100:.1f}%")
    print(f"Outliers (Delay): {report['outliers']['actual_delay_minutes']['outlier_count']} ({report['outliers']['actual_delay_minutes']['outlier_percentage']}%)")
    if report["errors"]:
        print(f"Errors: {report['errors']}")
        sys.exit(1)
    else:
        print("[SUCCESS] All dataset quality checks passed cleanly.")
