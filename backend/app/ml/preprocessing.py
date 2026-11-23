"""
BusFlow Data Preprocessing and Feature Engineering Pipeline
Handles:
1. Missing-value imputation (Median / Mode)
2. Duplicate detection & deduplication
3. Outlier inspection & robust capping
4. Categorical feature encoding (Ordinal & One-Hot)
5. Temporal & spatial feature engineering
6. Chronological Train / Validation / Test splitting
"""

from typing import Tuple, List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

# Ordinal mappings
TRAFFIC_ORDINAL_MAP = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "SEVERE": 3
}

WEATHER_ORDINAL_MAP = {
    "CLEAR": 0,
    "CLOUDY": 1,
    "LIGHT_RAIN": 2,
    "MODERATE_RAIN": 3,
    "HEAVY_RAIN": 4
}

DAY_OF_WEEK_MAP = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

class BusFlowPreprocessor:
    """Production data preprocessing and feature engineering transformer."""

    def __init__(self, clip_outliers: bool = True, max_delay_cap: float = 120.0):
        self.clip_outliers = clip_outliers
        self.max_delay_cap = max_delay_cap
        self.median_imputations: Dict[str, float] = {}
        self.mode_imputations: Dict[str, Any] = {}
        self.is_fitted = False

    def clean_and_handle_missing(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """Handles missing values, deduplication, and data type coercion."""
        data = df.copy()

        # 1. Deduplication on trip_id and stop_id
        if "trip_id" in data.columns and "stop_id" in data.columns:
            init_len = len(data)
            data = data.drop_duplicates(subset=["trip_id", "stop_id"])
            dropped = init_len - len(data)
            if dropped > 0:
                print(f"[Preprocessor] Removed {dropped} duplicate trip-stop rows.")

        # Numeric columns to impute
        numeric_cols = [
            "segment_distance_km", "remaining_distance_km", "number_of_remaining_stops",
            "temperature", "rainfall", "humidity", "previous_trip_delay"
        ]
        
        # Categorical columns to impute
        cat_cols = ["traffic_level", "weather_condition", "day_of_week"]

        for col in numeric_cols:
            if col in data.columns:
                if is_training:
                    median_val = float(data[col].median())
                    self.median_imputations[col] = median_val
                fill_val = self.median_imputations.get(col, 0.0)
                data[col] = data[col].fillna(fill_val)

        for col in cat_cols:
            if col in data.columns:
                if is_training:
                    mode_val = data[col].mode()[0] if not data[col].mode().empty else "LOW"
                    self.mode_imputations[col] = mode_val
                fill_val = self.mode_imputations.get(col, "LOW")
                data[col] = data[col].fillna(fill_val)

        return data

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies spatial, temporal, and traffic feature engineering."""
        data = df.copy()

        # 1. Temporal decomposition
        if "scheduled_arrival_time" in data.columns:
            # Parse time string HH:MM:SS
            sched_time = pd.to_datetime(data["scheduled_arrival_time"], format="%H:%M:%S", errors="coerce").dt.time
            data["scheduled_hour"] = sched_time.apply(lambda t: t.hour if pd.notnull(t) else 8)
            data["scheduled_minute"] = sched_time.apply(lambda t: t.minute if pd.notnull(t) else 0)
            data["scheduled_time_minutes"] = data["scheduled_hour"] * 60 + data["scheduled_minute"]
            
            # Peak hour flags
            time_float = data["scheduled_hour"] + data["scheduled_minute"] / 60.0
            data["is_morning_peak"] = ((time_float >= 7.5) & (time_float <= 8.75)).astype(int)
            data["is_evening_peak"] = ((time_float >= 16.5) & (time_float <= 17.75)).astype(int)
        else:
            data["scheduled_hour"] = 8
            data["scheduled_minute"] = 0
            data["scheduled_time_minutes"] = 480
            data["is_morning_peak"] = 1
            data["is_evening_peak"] = 0

        # 2. Day of week numeric
        if "day_of_week" in data.columns:
            data["day_of_week_num"] = data["day_of_week"].map(DAY_OF_WEEK_MAP).fillna(0).astype(int)
            data["is_saturday"] = (data["day_of_week"] == "Saturday").astype(int)
            data["is_monday"] = (data["day_of_week"] == "Monday").astype(int)
        else:
            data["day_of_week_num"] = 0
            data["is_saturday"] = 0
            data["is_monday"] = 0

        # 3. Ordinal encodings
        if "traffic_level" in data.columns:
            data["traffic_level_ordinal"] = data["traffic_level"].map(TRAFFIC_ORDINAL_MAP).fillna(1).astype(int)
        else:
            data["traffic_level_ordinal"] = 1

        if "weather_condition" in data.columns:
            data["weather_ordinal"] = data["weather_condition"].map(WEATHER_ORDINAL_MAP).fillna(0).astype(int)
        else:
            data["weather_ordinal"] = 0

        # 4. Weather friction interaction feature
        if "rainfall" in data.columns and "temperature" in data.columns:
            # High rain + moderate cold indicates severe monsoon congestion
            data["weather_friction_index"] = (
                data["rainfall"] * 0.15 + (data["weather_ordinal"] * 0.5)
            ).round(3)
        else:
            data["weather_friction_index"] = 0.0

        # 5. Spatial & stop progress features
        if "stop_sequence" in data.columns:
            # Normalize stop sequence (typical max route length ~ 10)
            data["stop_sequence_norm"] = (data["stop_sequence"] / 10.0).round(3)
        else:
            data["stop_sequence_norm"] = 0.5

        if "remaining_distance_km" in data.columns and "segment_distance_km" in data.columns:
            total_dist_approx = data["remaining_distance_km"] + data["segment_distance_km"]
            data["distance_progress_ratio"] = np.where(
                total_dist_approx > 0,
                (data["segment_distance_km"] / total_dist_approx).round(3),
                0.0
            )
        else:
            data["distance_progress_ratio"] = 0.5

        # 6. Outlier clipping on target variable
        if self.clip_outliers and "actual_delay_minutes" in data.columns:
            data["actual_delay_minutes"] = data["actual_delay_minutes"].clip(
                lower=-5.0, upper=self.max_delay_cap
            )

        return data

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit imputation statistics and transform dataset."""
        cleaned = self.clean_and_handle_missing(df, is_training=True)
        transformed = self.engineer_features(cleaned)
        self.is_fitted = True
        return transformed

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform test or live inference inputs using fitted parameters."""
        cleaned = self.clean_and_handle_missing(df, is_training=False)
        return self.engineer_features(cleaned)

def create_chronological_splits(
    df: pd.DataFrame,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Partitions the dataset strictly by chronological trip_date to eliminate
    look-ahead data leakage in time-series bus delay forecasting.
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5, "Ratios must sum to 1.0"

    # Sort strictly chronologically by date and scheduled departure
    sorted_df = df.sort_values(
        by=["trip_date", "scheduled_departure_time", "trip_id", "stop_sequence"]
    ).reset_index(drop=True)

    # Unique chronological trip dates
    unique_dates = sorted(sorted_df["trip_date"].unique())
    n_dates = len(unique_dates)

    train_end_idx = int(n_dates * train_ratio)
    val_end_idx = int(n_dates * (train_ratio + val_ratio))

    train_dates = set(unique_dates[:train_end_idx])
    val_dates = set(unique_dates[train_end_idx:val_end_idx])
    test_dates = set(unique_dates[val_end_idx:])

    train_df = sorted_df[sorted_df["trip_date"].isin(train_dates)].copy()
    val_df = sorted_df[sorted_df["trip_date"].isin(val_dates)].copy()
    test_df = sorted_df[sorted_df["trip_date"].isin(test_dates)].copy()

    print(f"[Chronological Split] Train dates: {len(train_dates)} ({len(train_df)} rows) | "
          f"Val dates: {len(val_dates)} ({len(val_df)} rows) | "
          f"Test dates: {len(test_dates)} ({len(test_df)} rows)")

    return train_df, val_df, test_df

if __name__ == "__main__":
    from app.utils.data_validator import DATASETS_DIR
    trips_file = DATASETS_DIR / "bus_trip_history.csv"
    if trips_file.exists():
        raw_df = pd.read_csv(trips_file)
        preprocessor = BusFlowPreprocessor()
        processed_df = preprocessor.fit_transform(raw_df)
        print(f"[Preprocessor] Transformed {len(processed_df)} rows with {len(processed_df.columns)} columns.")
        train, val, test = create_chronological_splits(processed_df)
        print("Feature columns:", [c for c in processed_df.columns if c not in ["trip_id", "bus_id", "is_synthetic"]])
