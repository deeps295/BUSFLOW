# BusFlow ML Training Report (v1.6.0)
*Sri Eshwar College of Engineering, Coimbatore, Tamil Nadu*
*Training Timestamp: 2026-11-18T08:08:24.626155*

> **Notice**: All evaluations in this report represent **Simulated-Data Performance** derived from physics-grounded synthetic training records.

---

## 1. Executive Champion Summary
- **Champion Architecture**: `HistGradientBoosting Regressor`
- **Algorithm Type**: `gradient_boosting`
- **Target Variables**:
  1. `actual_delay_minutes` (Stop-level arrival delay in minutes)
  2. `actual_remaining_travel_minutes` (Total transit time remaining to SECE Campus)
- **Validation Delay MAE**: **2.647 minutes** (Baseline: 5.764 mins)
- **Untouched Test Delay MAE**: **2.59 minutes**
- **Test Overall R² Score**: **0.902**

---

## 2. Candidate Model Benchmark Comparison

| Model Algorithm | Val Delay MAE (min) | Val Delay RMSE | Val Remaining MAE (min) | Val Overall R² | Overfitting Gap (Train-Val MAE) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Historical Average)** | 5.76 | 7.19 | 4.75 | 0.491 | 0.14 |
| **Linear Regression (Ridge)** | 3.06 | 3.86 | 2.09 | 0.854 | 0.11 |
| **Random Forest Regressor** | 3.13 | 3.95 | 1.80 | 0.848 | 1.13 |
| **HistGradientBoosting Regressor** | 2.65 | 3.35 | 1.36 | 0.891 | 0.46 |

---

## 3. Untouched Test Set Evaluation
The champion model was benchmarked on the chronologically split test partition (15% latest dates, unseen during training/tuning):

| Metric | Target 1: Arrival Delay (mins) | Target 2: Remaining Travel Time (mins) |
| :--- | :---: | :---: |
| **MAE (Mean Absolute Error)** | **2.59 mins** | **1.373 mins** |
| **RMSE (Root Mean Squared Error)** | **3.228** | **2.061** |
| **Combined R² Score** | **0.902** | — |

---

## 4. Error Analysis Stratified by Urban Traffic & Route

### 4.1 Traffic State Impact on Arrival Delay MAE
| Traffic Level | Test Delay MAE (mins) | Test Remaining Travel MAE (mins) | Sample Count |
| :--- | :---: | :---: | :---: |
| **HIGH** | 2.55 mins | 1.29 mins | 533 |
| **LOW** | 2.65 mins | 1.44 mins | 313 |
| **MEDIUM** | 2.6 mins | 1.34 mins | 749 |
| **SEVERE** | 2.59 mins | 1.62 mins | 189 |

### 4.2 Route-Wise Test Performance
| Route ID | Delay MAE (mins) | Remaining Travel MAE (mins) | Test Samples |
| :--- | :---: | :---: | :---: |
| **R01_BHARATHIAR** | 2.53 mins | 0.97 mins | 172 |
| **R02_KOTTAMPATTI_POLLACHI** | 2.48 mins | 1.41 mins | 178 |
| **R03_SARAVANAMPATTI** | 2.42 mins | 1.09 mins | 190 |
| **R04_KOVAIPUDUR** | 2.51 mins | 1.28 mins | 155 |
| **R05_VADAKKIPALAYAM** | 2.75 mins | 1.06 mins | 165 |
| **R06_SULUR** | 2.58 mins | 1.34 mins | 194 |
| **R07_POLLACHI_CENTRAL** | 2.66 mins | 1.19 mins | 211 |
| **R08_PERIYANAICKENPALAYAM** | 2.61 mins | 1.46 mins | 170 |
| **R09_PALLADAM** | 2.71 mins | 1.96 mins | 183 |
| **R10_UDUMALPET** | 2.65 mins | 2.03 mins | 166 |

---

## 5. Statistical Prediction Interval Specification
- **Methodology**: Empirical Validation Residual Quantile Analysis ($80\%$ interval)
- **Estimated Interval**: $[\hat{y} + \Delta_{10\%}, \hat{y} + \Delta_{90\%}]$
- **Average Delay Uncertainty Margin**: $\pm$-4.08 minutes
- **Label**: `80% Estimated Prediction Interval (Validation Residual Quantile Method)`

*The interval reflects expected variance under non-linear Coimbatore traffic surges and monsoon rain conditions.*
