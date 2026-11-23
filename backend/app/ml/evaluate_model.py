"""
BusFlow Model Evaluation Module
Calculates MAE, RMSE, R² across Train, Validation, and Test partitions.
Performs stratified residual analysis across routes, traffic states, and weather conditions.
All synthetic evaluations are explicitly marked as "Simulated-Data Performance".
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from app.ml.model_utils import compute_regression_metrics, TARGET_COLUMNS

def evaluate_model_pipeline(
    model: Any,
    X: pd.DataFrame,
    Y: pd.DataFrame,
    dataset_name: str = "Validation"
) -> Dict[str, Any]:
    """Evaluates a trained model pipeline on input features and ground truth."""
    y_pred = model.predict(X)
    metrics = compute_regression_metrics(Y.values, y_pred)
    metrics["partition"] = dataset_name
    metrics["num_samples"] = len(X)
    metrics["data_authenticity"] = "Simulated-Data Performance (Synthetic Training Seeds)"
    return metrics

def run_stratified_error_analysis(
    model: Any,
    X_test: pd.DataFrame,
    Y_test: pd.DataFrame
) -> Dict[str, Any]:
    """
    Detailed residual analysis stratified by route, traffic level, and weather.
    Helps identify urban bottleneck impact and non-linear congestion spikes.
    """
    y_pred = model.predict(X_test)
    y_true = Y_test.values

    analysis_df = X_test.copy()
    analysis_df["true_delay"] = y_true[:, 0]
    analysis_df["pred_delay"] = y_pred[:, 0]
    analysis_df["delay_residual"] = analysis_df["true_delay"] - analysis_df["pred_delay"]
    analysis_df["abs_delay_error"] = analysis_df["delay_residual"].abs()

    analysis_df["true_remaining"] = y_true[:, 1]
    analysis_df["pred_remaining"] = y_pred[:, 1]
    analysis_df["abs_remaining_error"] = (analysis_df["true_remaining"] - analysis_df["pred_remaining"]).abs()

    # 1. Error by Route
    route_perf = analysis_df.groupby("route_id").agg(
        delay_mae=("abs_delay_error", "mean"),
        remaining_mae=("abs_remaining_error", "mean"),
        count=("true_delay", "count")
    ).round(2).to_dict(orient="index")

    # 2. Error by Traffic Level
    traffic_perf = analysis_df.groupby("traffic_level").agg(
        delay_mae=("abs_delay_error", "mean"),
        remaining_mae=("abs_remaining_error", "mean"),
        count=("true_delay", "count")
    ).round(2).to_dict(orient="index")

    # 3. Error by Weather Condition
    weather_perf = analysis_df.groupby("weather_condition").agg(
        delay_mae=("abs_delay_error", "mean"),
        remaining_mae=("abs_remaining_error", "mean"),
        count=("true_delay", "count")
    ).round(2).to_dict(orient="index")

    return {
        "by_route": route_perf,
        "by_traffic_level": traffic_perf,
        "by_weather_condition": weather_perf
    }

def format_markdown_comparison_table(model_results: List[Dict[str, Any]]) -> str:
    """Formats comparison results into a Markdown table for reports."""
    header = (
        "| Model Algorithm | Val Delay MAE (min) | Val Delay RMSE | Val Remaining MAE (min) | Val Overall R² | Overfitting Gap (Train-Val MAE) |\n"
        "| :--- | :---: | :---: | :---: | :---: | :---: |"
    )
    rows = []
    for res in model_results:
        name = res.get("model_name", "Unknown")
        v_d_mae = res.get("val_delay_mae", 0.0)
        v_d_rmse = res.get("val_delay_rmse", 0.0)
        v_r_mae = res.get("val_remaining_time_mae", 0.0)
        v_r2 = res.get("val_overall_r2", 0.0)
        t_d_mae = res.get("train_delay_mae", 0.0)
        gap = round(abs(v_d_mae - t_d_mae), 2)

        rows.append(f"| **{name}** | {v_d_mae:.2f} | {v_d_rmse:.2f} | {v_r_mae:.2f} | {v_r2:.3f} | {gap:.2f} |")

    return "\n".join([header] + rows)
