"""
BusFlow ML Model Utilities
Defines feature constants, column transformers, empirical baseline regressors,
metric computation, and statistical prediction interval estimators.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Canonical input feature set (Strictly no target leakage)
CATEGORICAL_FEATURES = [
    "route_id",
    "stop_id",
    "day_of_week",
    "traffic_level",
    "weather_condition"
]

NUMERICAL_FEATURES = [
    "departure_hour",
    "departure_minute",
    "segment_distance_km",
    "remaining_distance_km",
    "number_of_remaining_stops",
    "temperature",
    "rainfall",
    "humidity",
    "previous_trip_delay"
]

FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERICAL_FEATURES

TARGET_COLUMNS = [
    "actual_delay_minutes",
    "actual_remaining_travel_minutes"
]

def extract_features_and_targets(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extracts features and target variables while guaranteeing zero target leakage.
    Derives departure_hour and departure_minute if only scheduled_departure_time exists.
    """
    data = df.copy()

    # Derive departure_hour and departure_minute if missing
    if "departure_hour" not in data.columns or "departure_minute" not in data.columns:
        if "scheduled_departure_time" in data.columns:
            time_series = pd.to_datetime(
                data["scheduled_departure_time"], format="%H:%M:%S", errors="coerce"
            ).dt.time
            data["departure_hour"] = time_series.apply(lambda t: t.hour if pd.notnull(t) else 7)
            data["departure_minute"] = time_series.apply(lambda t: t.minute if pd.notnull(t) else 0)
        else:
            data["departure_hour"] = 7
            data["departure_minute"] = 0

    # Ensure all required features are present
    for col in NUMERICAL_FEATURES:
        if col not in data.columns:
            data[col] = 0.0
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0.0)

    for col in CATEGORICAL_FEATURES:
        if col not in data.columns:
            data[col] = "UNKNOWN"
        data[col] = data[col].astype(str).fillna("UNKNOWN")

    X = data[FEATURE_COLUMNS].copy()

    # Extract targets if present
    Y = None
    if all(col in data.columns for col in TARGET_COLUMNS):
        Y = data[TARGET_COLUMNS].copy()
        for col in TARGET_COLUMNS:
            Y[col] = pd.to_numeric(Y[col], errors="coerce").fillna(0.0)

    return X, Y

def build_feature_preprocessor() -> ColumnTransformer:
    """
    Builds a Scikit-Learn ColumnTransformer:
    - Numerical: Median imputation + Standard Scaling
    - Categorical: Most frequent imputation + OneHotEncoder(handle_unknown='ignore')
    """
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, NUMERICAL_FEATURES),
            ("cat", cat_pipeline, CATEGORICAL_FEATURES)
        ],
        remainder="drop"
    )
    return preprocessor

class HistoricalAverageBaseline:
    """
    Empirical baseline model:
    Predicts arrival delay and remaining travel time using historical stop-level averages.
    Falls back to route-level mean, then global mean if a stop has never been observed.
    """
    def __init__(self):
        self.stop_averages_: Dict[Tuple[str, str], Dict[str, float]] = {}
        self.route_averages_: Dict[str, Dict[str, float]] = {}
        self.global_averages_: Dict[str, float] = {}

    def fit(self, X: pd.DataFrame, Y: pd.DataFrame):
        combined = X.copy()
        for col in TARGET_COLUMNS:
            combined[col] = Y[col].values

        # Global means
        self.global_averages_ = {
            col: float(combined[col].mean()) for col in TARGET_COLUMNS
        }

        # Route-level means
        route_grp = combined.groupby("route_id")[TARGET_COLUMNS].mean()
        self.route_averages_ = route_grp.to_dict(orient="index")

        # Stop-level means: (route_id, stop_id) -> {targets}
        stop_grp = combined.groupby(["route_id", "stop_id"])[TARGET_COLUMNS].mean()
        self.stop_averages_ = stop_grp.to_dict(orient="index")
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        preds = []
        for _, row in X.iterrows():
            key = (row["route_id"], row["stop_id"])
            if key in self.stop_averages_:
                vals = [self.stop_averages_[key][col] for col in TARGET_COLUMNS]
            elif row["route_id"] in self.route_averages_:
                vals = [self.route_averages_[row["route_id"]][col] for col in TARGET_COLUMNS]
            else:
                vals = [self.global_averages_[col] for col in TARGET_COLUMNS]
            preds.append(vals)
        return np.array(preds)

def compute_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """Calculates MAE, RMSE, and R2 for individual targets and aggregate."""
    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)

    if y_true_arr.ndim == 1:
        y_true_arr = y_true_arr.reshape(-1, 1)
    if y_pred_arr.ndim == 1:
        y_pred_arr = y_pred_arr.reshape(-1, 1)

    metrics = {}
    target_names = ["delay", "remaining_time"] if y_true_arr.shape[1] == 2 else [f"target_{i}" for i in range(y_true_arr.shape[1])]

    total_mae = 0.0
    total_rmse = 0.0
    total_r2 = 0.0

    for i, name in enumerate(target_names):
        col_true = y_true_arr[:, i]
        col_pred = y_pred_arr[:, i]

        mae = float(mean_absolute_error(col_true, col_pred))
        rmse = float(np.sqrt(mean_squared_error(col_true, col_pred)))
        r2 = float(r2_score(col_true, col_pred))

        metrics[f"{name}_mae"] = round(mae, 3)
        metrics[f"{name}_rmse"] = round(rmse, 3)
        metrics[f"{name}_r2"] = round(r2, 3)

        total_mae += mae
        total_rmse += rmse
        total_r2 += r2

    n_targets = len(target_names)
    metrics["overall_mae"] = round(total_mae / n_targets, 3)
    metrics["overall_rmse"] = round(total_rmse / n_targets, 3)
    metrics["overall_r2"] = round(total_r2 / n_targets, 3)
    return metrics

class PredictionIntervalEstimator:
    """
    Computes empirical prediction intervals based on validation residuals.
    Provides statistically grounded bounds:
    Lower bound = pred + Q(alpha/2)
    Upper bound = pred + Q(1 - alpha/2)
    Clearly flagged as 'Estimated Prediction Interval' (not a guaranteed confidence score).
    """
    def __init__(self, confidence_level: float = 0.80):
        self.confidence_level = confidence_level
        self.alpha = 1.0 - confidence_level
        # Residual quantiles per target
        self.lower_quantile_offset_: Dict[str, float] = {}
        self.upper_quantile_offset_: Dict[str, float] = {}
        self.residual_std_: Dict[str, float] = {}

    def fit(self, y_val_true: np.ndarray, y_val_pred: np.ndarray):
        residuals = np.array(y_val_true) - np.array(y_val_pred)
        target_names = ["delay", "remaining_time"]

        for i, name in enumerate(target_names):
            res_col = residuals[:, i]
            q_low = float(np.percentile(res_col, (self.alpha / 2.0) * 100))
            q_high = float(np.percentile(res_col, (1.0 - self.alpha / 2.0) * 100))
            std = float(np.std(res_col))

            self.lower_quantile_offset_[name] = round(q_low, 2)
            self.upper_quantile_offset_[name] = round(q_high, 2)
            self.residual_std_[name] = round(std, 2)
        return self

    def get_intervals(self, y_pred: np.ndarray) -> Dict[str, Any]:
        """Calculates prediction interval bounds for given predictions."""
        preds = np.array(y_pred)
        if preds.ndim == 1:
            preds = preds.reshape(1, -1)

        result = {}
        target_names = ["delay", "remaining_time"]

        for i, name in enumerate(target_names):
            pred_col = preds[:, i]
            q_low = self.lower_quantile_offset_.get(name, -3.0)
            q_high = self.upper_quantile_offset_.get(name, 3.0)

            lower_bound = np.maximum(0.0 if name == "remaining_time" else -5.0, pred_col + q_low)
            upper_bound = pred_col + q_high

            result[f"{name}_interval"] = {
                "point_estimate": np.round(pred_col, 1).tolist(),
                "lower_bound": np.round(lower_bound, 1).tolist(),
                "upper_bound": np.round(upper_bound, 1).tolist(),
                "margin_minutes": round((q_high - q_low) / 2.0, 1),
                "confidence_level_label": f"{int(self.confidence_level * 100)}% Estimated Prediction Interval (Validation Residual Method)"
            }
        return result
