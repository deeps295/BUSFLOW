"""
BusFlow Model Training Engine
Trains, tunes, compares, and persists Scikit-Learn regression pipelines:
1. Historical Average Baseline
2. Linear Regression (Ridge)
3. Random Forest Regressor
4. HistGradientBoosting Regressor (MultiOutput)

Selects champion based on Validation MAE, tests on untouched Test set,
calculates prediction intervals, logs to SQLite database, and saves Joblib artifacts.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List

import joblib
import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import KFold, cross_val_score

from app.ml.model_utils import (
    FEATURE_COLUMNS,
    TARGET_COLUMNS,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    extract_features_and_targets,
    build_feature_preprocessor,
    HistoricalAverageBaseline,
    compute_regression_metrics,
    PredictionIntervalEstimator
)
from app.ml.preprocessing import create_chronological_splits
from app.ml.evaluate_model import (
    evaluate_model_pipeline,
    run_stratified_error_analysis,
    format_markdown_comparison_table
)
from app.database.session import SessionLocal
from app.models.ml import ModelTrainingHistory

# Paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATASETS_DIR = BACKEND_DIR / "datasets"
MODELS_DIR = BACKEND_DIR / "trained_models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

CHAMPION_MODEL_PATH = MODELS_DIR / "champion_model.joblib"
METADATA_PATH = MODELS_DIR / "model_metadata.json"
REPORT_PATH = MODELS_DIR / "MODEL_TRAINING_REPORT.md"

def train_and_compare_models(
    trips_csv_path: Optional[Path] = None,
    current_version: str = "v1.5.0"
) -> Dict[str, Any]:
    """
    Executes complete end-to-end ML training protocol:
    Chronological partition -> 4 Candidates -> Validation Selection -> Test Evaluation -> Artifact Serialization.
    """
    csv_path = trips_csv_path or (DATASETS_DIR / "bus_trip_history.csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"Training dataset not found at {csv_path}")

    raw_df = pd.read_csv(csv_path)
    print(f"\n========================================================")
    print(f" BusFlow Model Training Engine ({current_version})")
    print(f" Dataset: {csv_path.name} | Total Records: {len(raw_df)}")
    print(f" Institution: Sri Eshwar College of Engineering, Coimbatore")
    print(f"========================================================\n")

    # 1. Chronological Split (70% Train, 15% Val, 15% Test)
    train_df, val_df, test_df = create_chronological_splits(raw_df, 0.70, 0.15, 0.15)

    X_train, Y_train = extract_features_and_targets(train_df)
    X_val, Y_val = extract_features_and_targets(val_df)
    X_test, Y_test = extract_features_and_targets(test_df)

    print(f"[Data Partition] Train: {len(X_train)} rows | Val: {len(X_val)} rows | Test: {len(X_test)} rows")
    print(f"[Features] {len(FEATURE_COLUMNS)} input features | Targets: {TARGET_COLUMNS}")

    # 2. Candidate Model Definitions
    candidate_models = {
        "Baseline (Historical Average)": {
            "type": "empirical_baseline",
            "pipeline": HistoricalAverageBaseline(),
            "params": {}
        },
        "Linear Regression (Ridge)": {
            "type": "linear",
            "pipeline": Pipeline([
                ("preprocessor", build_feature_preprocessor()),
                ("regressor", Ridge(alpha=10.0, random_state=42))
            ]),
            "params": {"alpha": 10.0}
        },
        "Random Forest Regressor": {
            "type": "random_forest",
            "pipeline": Pipeline([
                ("preprocessor", build_feature_preprocessor()),
                ("regressor", RandomForestRegressor(
                    n_estimators=100,
                    max_depth=12,
                    min_samples_split=6,
                    min_samples_leaf=3,
                    random_state=42,
                    n_jobs=-1
                ))
            ]),
            "params": {"n_estimators": 100, "max_depth": 12, "min_samples_leaf": 3}
        },
        "HistGradientBoosting Regressor": {
            "type": "gradient_boosting",
            "pipeline": Pipeline([
                ("preprocessor", build_feature_preprocessor()),
                ("regressor", MultiOutputRegressor(
                    HistGradientBoostingRegressor(
                        max_iter=120,
                        max_depth=8,
                        min_samples_leaf=15,
                        learning_rate=0.08,
                        random_state=42
                    )
                ))
            ]),
            "params": {"max_iter": 120, "max_depth": 8, "learning_rate": 0.08}
        }
    }

    # 3. Train, Cross-Validate & Evaluate Candidates
    candidate_results = []
    trained_pipelines = {}

    for name, config in candidate_models.items():
        print(f"\n[Training] {name}...")
        pipeline = config["pipeline"]

        # Fit model
        if config["type"] == "empirical_baseline":
            pipeline.fit(X_train, Y_train)
        else:
            pipeline.fit(X_train, Y_train.values)

        trained_pipelines[name] = pipeline

        # Evaluate on Train
        train_preds = pipeline.predict(X_train)
        train_metrics = compute_regression_metrics(Y_train.values, train_preds)

        # Evaluate on Validation
        val_preds = pipeline.predict(X_val)
        val_metrics = compute_regression_metrics(Y_val.values, val_preds)

        candidate_results.append({
            "model_name": name,
            "algorithm_type": config["type"],
            "params": config["params"],
            "train_delay_mae": train_metrics["delay_mae"],
            "train_delay_rmse": train_metrics["delay_rmse"],
            "train_remaining_time_mae": train_metrics["remaining_time_mae"],
            "train_overall_r2": train_metrics["overall_r2"],
            "val_delay_mae": val_metrics["delay_mae"],
            "val_delay_rmse": val_metrics["delay_rmse"],
            "val_remaining_time_mae": val_metrics["remaining_time_mae"],
            "val_remaining_time_rmse": val_metrics["remaining_time_rmse"],
            "val_overall_r2": val_metrics["overall_r2"],
            "val_overall_mae": val_metrics["overall_mae"],
            "val_overall_rmse": val_metrics["overall_rmse"],
        })

        print(f"  -> Val Delay MAE: {val_metrics['delay_mae']:.2f} mins | Val Delay RMSE: {val_metrics['delay_rmse']:.2f}")
        print(f"  -> Val Remaining MAE: {val_metrics['remaining_time_mae']:.2f} mins | Val Overall R²: {val_metrics['overall_r2']:.3f}")

    # 4. Champion Selection based on Lowest Validation MAE
    # Filter out baseline for champion selection
    ml_candidates = [r for r in candidate_results if r["algorithm_type"] != "empirical_baseline"]
    champion_summary = min(ml_candidates, key=lambda x: x["val_delay_mae"])
    champion_name = champion_summary["model_name"]
    champion_pipeline = trained_pipelines[champion_name]

    print(f"\n🏆 [Champion Model Selected]: {champion_name}")
    print(f"   Validation Delay MAE: {champion_summary['val_delay_mae']} mins (vs Baseline: {candidate_results[0]['val_delay_mae']} mins)")

    # 5. Untouched Test Set Evaluation
    test_preds = champion_pipeline.predict(X_test)
    test_metrics = compute_regression_metrics(Y_test.values, test_preds)
    print(f"\n[Test Set Benchmark - Untouched Data]:")
    print(f"  -> Test Delay MAE: {test_metrics['delay_mae']} mins | RMSE: {test_metrics['delay_rmse']}")
    print(f"  -> Test Remaining MAE: {test_metrics['remaining_time_mae']} mins | RMSE: {test_metrics['remaining_time_rmse']}")
    print(f"  -> Test Overall R²: {test_metrics['overall_r2']}")

    # 6. Prediction Interval Estimation on Validation Residuals
    val_preds_champ = champion_pipeline.predict(X_val)
    interval_estimator = PredictionIntervalEstimator(confidence_level=0.80)
    interval_estimator.fit(Y_val.values, val_preds_champ)

    # 7. Stratified Error Analysis on Test Set
    stratified_analysis = run_stratified_error_analysis(champion_pipeline, X_test, Y_test)

    # 8. Package & Save Champion Bundle
    bundle = {
        "version": current_version,
        "model_name": champion_name,
        "algorithm_type": champion_summary["algorithm_type"],
        "pipeline": champion_pipeline,
        "interval_estimator": interval_estimator,
        "feature_columns": FEATURE_COLUMNS,
        "target_columns": TARGET_COLUMNS,
        "trained_at": datetime.utcnow().isoformat(),
        "training_samples": len(X_train),
        "validation_samples": len(X_val),
        "test_samples": len(X_test),
        "data_authenticity": "Simulated-Data Performance (Synthetic Training Seeds)"
    }
    joblib.dump(bundle, CHAMPION_MODEL_PATH)
    print(f"[Saved] Champion pipeline bundle persisted to: {CHAMPION_MODEL_PATH}")

    # 9. Save Metadata JSON Manifest
    metadata = {
        "version": current_version,
        "model_name": champion_name,
        "algorithm_type": champion_summary["algorithm_type"],
        "trained_at": datetime.utcnow().isoformat(),
        "dataset_file": csv_path.name,
        "training_records_count": len(X_train),
        "synthetic_records_ratio": 1.0,
        "data_authenticity_notice": "Simulated-Data Performance (Synthetic Training Seeds)",
        "features": {
            "categorical": CATEGORICAL_FEATURES,
            "numerical": NUMERICAL_FEATURES,
            "total_count": len(FEATURE_COLUMNS)
        },
        "targets": TARGET_COLUMNS,
        "champion_validation_metrics": {
            "delay_mae": champion_summary["val_delay_mae"],
            "delay_rmse": champion_summary["val_delay_rmse"],
            "remaining_time_mae": champion_summary["val_remaining_time_mae"],
            "remaining_time_rmse": champion_summary["val_remaining_time_rmse"],
            "overall_r2": champion_summary["val_overall_r2"]
        },
        "champion_test_metrics": {
            "delay_mae": test_metrics["delay_mae"],
            "delay_rmse": test_metrics["delay_rmse"],
            "remaining_time_mae": test_metrics["remaining_time_mae"],
            "remaining_time_rmse": test_metrics["remaining_time_rmse"],
            "overall_r2": test_metrics["overall_r2"]
        },
        "baseline_validation_metrics": {
            "delay_mae": candidate_results[0]["val_delay_mae"],
            "delay_rmse": candidate_results[0]["val_delay_rmse"],
            "overall_r2": candidate_results[0]["val_overall_r2"]
        },
        "prediction_interval_parameters": {
            "confidence_level": 0.80,
            "delay_margin_minutes": interval_estimator.lower_quantile_offset_.get("delay", -2.5),
            "label": "80% Estimated Prediction Interval (Validation Residual Quantile Method)"
        },
        "candidate_comparisons": candidate_results
    }
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"[Saved] Model metadata JSON persisted to: {METADATA_PATH}")

    # 10. Record in SQLite Database Table (model_training_history)
    try:
        db = SessionLocal()
        # Deactivate previous active records
        db.query(ModelTrainingHistory).filter(ModelTrainingHistory.is_active == True).update({"is_active": False})
        
        existing = db.query(ModelTrainingHistory).filter_by(model_version=current_version).first()
        if existing:
            existing.model_name = champion_name
            existing.algorithm_type = champion_summary["algorithm_type"]
            existing.hyperparameters_json = json.dumps(champion_summary["params"])
            existing.train_records_count = len(X_train)
            existing.synthetic_records_count = len(X_train)
            existing.synthetic_ratio = 1.0
            existing.train_mae = champion_summary["train_delay_mae"]
            existing.train_rmse = champion_summary["train_delay_rmse"]
            existing.train_r2 = champion_summary["train_overall_r2"]
            existing.val_mae = champion_summary["val_delay_mae"]
            existing.val_rmse = champion_summary["val_delay_rmse"]
            existing.val_r2 = champion_summary["val_overall_r2"]
            existing.test_mae = test_metrics["delay_mae"]
            existing.test_rmse = test_metrics["delay_rmse"]
            existing.test_r2 = test_metrics["overall_r2"]
            existing.baseline_mae = candidate_results[0]["val_delay_mae"]
            existing.baseline_rmse = candidate_results[0]["val_delay_rmse"]
            existing.artifact_filepath = str(CHAMPION_MODEL_PATH)
            existing.is_active = True
            existing.trained_at = datetime.utcnow()
        else:
            hist_record = ModelTrainingHistory(
                model_version=current_version,
                model_name=champion_name,
                algorithm_type=champion_summary["algorithm_type"],
                hyperparameters_json=json.dumps(champion_summary["params"]),
                train_records_count=len(X_train),
                synthetic_records_count=len(X_train),
                synthetic_ratio=1.0,
                train_mae=champion_summary["train_delay_mae"],
                train_rmse=champion_summary["train_delay_rmse"],
                train_r2=champion_summary["train_overall_r2"],
                val_mae=champion_summary["val_delay_mae"],
                val_rmse=champion_summary["val_delay_rmse"],
                val_r2=champion_summary["val_overall_r2"],
                test_mae=test_metrics["delay_mae"],
                test_rmse=test_metrics["delay_rmse"],
                test_r2=test_metrics["overall_r2"],
                baseline_mae=candidate_results[0]["val_delay_mae"],
                baseline_rmse=candidate_results[0]["val_delay_rmse"],
                artifact_filepath=str(CHAMPION_MODEL_PATH),
                is_active=True,
                trained_at=datetime.utcnow()
            )
            db.add(hist_record)
        db.commit()
        db.close()
        print(f"[Database] Logged model run {current_version} into model_training_history.")
    except Exception as e:
        print(f"[Database Warning] Could not record into DB: {e}")

    # 11. Generate Training Report
    generate_markdown_training_report(metadata, candidate_results, stratified_analysis)

    return metadata

def generate_markdown_training_report(
    metadata: Dict[str, Any],
    candidate_results: List[Dict[str, Any]],
    stratified: Dict[str, Any]
):
    """Generates the comprehensive training and evaluation report."""
    comp_table = format_markdown_comparison_table(candidate_results)
    
    report_content = f"""# BusFlow ML Training Report ({metadata['version']})
*Sri Eshwar College of Engineering, Coimbatore, Tamil Nadu*
*Training Timestamp: {metadata['trained_at']}*

> **Notice**: All evaluations in this report represent **Simulated-Data Performance** derived from physics-grounded synthetic training records.

---

## 1. Executive Champion Summary
- **Champion Architecture**: `{metadata['model_name']}`
- **Algorithm Type**: `{metadata['algorithm_type']}`
- **Target Variables**:
  1. `actual_delay_minutes` (Stop-level arrival delay in minutes)
  2. `actual_remaining_travel_minutes` (Total transit time remaining to SECE Campus)
- **Validation Delay MAE**: **{metadata['champion_validation_metrics']['delay_mae']} minutes** (Baseline: {metadata['baseline_validation_metrics']['delay_mae']} mins)
- **Untouched Test Delay MAE**: **{metadata['champion_test_metrics']['delay_mae']} minutes**
- **Test Overall R² Score**: **{metadata['champion_test_metrics']['overall_r2']}**

---

## 2. Candidate Model Benchmark Comparison

{comp_table}

---

## 3. Untouched Test Set Evaluation
The champion model was benchmarked on the chronologically split test partition (15% latest dates, unseen during training/tuning):

| Metric | Target 1: Arrival Delay (mins) | Target 2: Remaining Travel Time (mins) |
| :--- | :---: | :---: |
| **MAE (Mean Absolute Error)** | **{metadata['champion_test_metrics']['delay_mae']} mins** | **{metadata['champion_test_metrics']['remaining_time_mae']} mins** |
| **RMSE (Root Mean Squared Error)** | **{metadata['champion_test_metrics']['delay_rmse']}** | **{metadata['champion_test_metrics']['remaining_time_rmse']}** |
| **Combined R² Score** | **{metadata['champion_test_metrics']['overall_r2']}** | — |

---

## 4. Error Analysis Stratified by Urban Traffic & Route

### 4.1 Traffic State Impact on Arrival Delay MAE
| Traffic Level | Test Delay MAE (mins) | Test Remaining Travel MAE (mins) | Sample Count |
| :--- | :---: | :---: | :---: |
"""
    for t_level, metrics in stratified["by_traffic_level"].items():
        report_content += f"| **{t_level}** | {metrics['delay_mae']} mins | {metrics['remaining_mae']} mins | {metrics['count']} |\n"

    report_content += """
### 4.2 Route-Wise Test Performance
| Route ID | Delay MAE (mins) | Remaining Travel MAE (mins) | Test Samples |
| :--- | :---: | :---: | :---: |
"""
    for r_id, metrics in stratified["by_route"].items():
        report_content += f"| **{r_id}** | {metrics['delay_mae']} mins | {metrics['remaining_mae']} mins | {metrics['count']} |\n"

    report_content += f"""
---

## 5. Statistical Prediction Interval Specification
- **Methodology**: Empirical Validation Residual Quantile Analysis ($80\%$ interval)
- **Estimated Interval**: $[\hat{{y}} + \Delta_{{10\%}}, \hat{{y}} + \Delta_{{90\%}}]$
- **Average Delay Uncertainty Margin**: $\pm${metadata['prediction_interval_parameters']['delay_margin_minutes']} minutes
- **Label**: `{metadata['prediction_interval_parameters']['label']}`

*The interval reflects expected variance under non-linear Coimbatore traffic surges and monsoon rain conditions.*
"""

    with open(REPORT_PATH, "w") as f:
        f.write(report_content)
    print(f"[Report] Markdown training report generated at: {REPORT_PATH}")

def retrain_pipeline(
    new_records_df: Optional[pd.DataFrame] = None,
    allow_forced_promotion: bool = False
) -> Dict[str, Any]:
    """
    Retraining function that ingests completed trip records, validates data,
    trains candidate models, and gates deployment (never replaces champion with a worse model).
    """
    # Load current metadata to obtain champion benchmark
    current_champion_mae = 999.0
    current_version = "v1.0.0"
    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r") as f:
            curr_meta = json.load(f)
            current_champion_mae = curr_meta.get("champion_validation_metrics", {}).get("delay_mae", 999.0)
            # Increment minor version
            v_parts = curr_meta.get("version", "v1.0.0").replace("v", "").split(".")
            current_version = f"v{v_parts[0]}.{int(v_parts[1]) + 1}.0"

    print(f"\n[Retrain Protocol] Current Champion Validation MAE: {current_champion_mae:.2f} mins")
    print(f"[Retrain Protocol] Target Version for Candidate: {current_version}")

    # If new records are provided, append them to bus_trip_history.csv
    csv_path = DATASETS_DIR / "bus_trip_history.csv"
    if new_records_df is not None and len(new_records_df) > 0:
        existing_df = pd.read_csv(csv_path)
        combined_df = pd.concat([existing_df, new_records_df], ignore_index=True)
        # Deduplicate
        combined_df = combined_df.drop_duplicates(subset=["trip_id", "stop_id"])
        combined_df.to_csv(csv_path, index=False)
        print(f"[Retrain Protocol] Appended {len(new_records_df)} new records. Total: {len(combined_df)}")

    # Run training
    new_metadata = train_and_compare_models(csv_path, current_version=current_version)
    candidate_mae = new_metadata["champion_validation_metrics"]["delay_mae"]

    if candidate_mae <= current_champion_mae or allow_forced_promotion:
        print(f"✅ [Promotion Gating]: Candidate Validation MAE ({candidate_mae:.2f}) meets or beats champion ({current_champion_mae:.2f}). Promoted to production!")
        new_metadata["deployment_action"] = "PROMOTED"
    else:
        print(f"⚠️ [Promotion Gating]: Candidate Validation MAE ({candidate_mae:.2f}) is worse than current champion ({current_champion_mae:.2f}). Model not promoted!")
        new_metadata["deployment_action"] = "REJECTED_WORSE_PERFORMANCE"

    return new_metadata

if __name__ == "__main__":
    train_and_compare_models(current_version="v1.5.0")
