# BusFlow – ML-Based College Bus Arrival Delay Prediction
*Designed specifically for Sri Eshwar College of Engineering (SECE), Coimbatore, Tamil Nadu, India*

> **Tagline:** Smart Arrival. Less Waiting.  
> **Brand Identity:** Deep Navy (`#071B3A`), Royal Blue (`#2563EB`), Sky Blue (`#38BDF8`), Cyan (`#06B6D4`), Emerald Green (`#10B981`), Light Canvas (`#F4F9FF`).

BusFlow is a full-stack, machine-learning-driven transport prediction and fleet management web application. It predicts college bus arrival times, expected delays, and remaining travel times across Coimbatore and Pollachi routes to Sri Eshwar College of Engineering (SECE).

---

## 🏛️ Authentic Sri Eshwar (SECE) Transit Corridors

All routes and stop sequences strictly correspond to authentic transport corridors published by **Sri Eshwar College of Engineering**:
- **Campus Location**: Kondampatti Post, Vadasithur (via), Kinathukadavu, Coimbatore – 641 202, Tamil Nadu, India
- **Reference**: [SECE Official Transport Page](https://sece.ac.in/transport/)

| Route ID | Route Name | Origin & Via Points | Stops | Distance |
|----------|------------|---------------------|-------|----------|
| `R01` | Bharathiar University Route | Bharathiar Univ → Vadavalli → Gandhi Park → Ukkadam → Eachanari → SECE | 9 | 48.6 km |
| `R02` | Kottampatti–Pollachi Route | Kottampatti → Mahalingapuram → Pollachi Bus Stand → Achipatti → SECE | 7 | 24.8 km |
| `R03` | Saravanampatti Route | Saravanampatti → Ganapathy → Gandhipuram → Podanur → Eachanari → SECE | 10 | 42.1 km |
| `R04` | Kovaipudur Route | Kovaipudur → Kuniyamuthur → Athupalam → Sundarapuram → Kinathukadavu → SECE | 9 | 26.4 km |
| `R05` | Vadakkipalayam Route | Vadakkipalayam → Sulakkal Temple → Thamaraikulam → Kinathukadavu → SECE | 8 | 25.1 km |
| `R06` | Sulur Route | Sulur → Ondipudur → Singanallur → Podanur → Vadasithur → SECE | 10 | 36.2 km |
| `R07` | Pollachi Central Route | Pollachi Bus Stand → MCET Gate → Achipatti → Kinathukadavu → SECE | 8 | 21.3 km |
| `R08` | Periyanaickenpalayam Route | Periyanaickenpalayam → Thudiyalur → Saibaba Colony → Ukkadam → SECE | 10 | 50.8 km |
| `R09` | Palladam Route | Palladam → Karanampettai → Sulthanpet → Vadasithur → SECE | 9 | 34.6 km |
| `R10` | Udumalpet Route | Udumalpet → Bodipatti → Negamam → Devanampalayam → SECE | 8 | 44.5 km |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python**: 3.10+ (with `pip` and virtual environment support)
- **Node.js**: v18+ (with `npm`)

### 2. Backend Startup (Terminal 1)
```bash
cd backend
pip install -r requirements.txt
python run_backend.py
```
- **Backend API URL**: `http://127.0.0.1:8001`
- **Interactive Swagger Docs**: `http://127.0.0.1:8001/api/docs`
- **Health Check**: `http://127.0.0.1:8001/api/health`

*(Note: Port 8001 is used by default as standard port 8000 is occupied on select Windows configurations).*

### 3. Frontend Startup (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```
- **Web Application**: `http://localhost:5173`
- The Vite development server automatically proxies `/api/*` requests to `http://127.0.0.1:8001`.

---

## 🔑 Pre-Seeded Demo Credentials

The database initializes with 3 pre-seeded demonstration accounts:

| Portal / Role | Email | Password | Primary Capabilities |
|---------------|-------|----------|----------------------|
| **Student** | `student@sece.ac.in` | `student123` | Route selection, boarding stop lookup, ML ETA & delay predictions, 80% confidence interval, interactive map |
| **Driver** | `driver@sece.ac.in` | `driver123` | Start/complete college trips, intermediate stop check-in, real-time traffic reporting (Low/Med/High/Severe), weather snapshot |
| **Admin** | `admin@sece.ac.in` | `admin123` | Fleet & route management, dataset ingestion, trigger ML retraining, champion metrics, training history, traffic logs |

---

## 🤖 Supervised Machine Learning Engine

BusFlow implements genuine Scikit-Learn regression pipelines — **no simulated or mocked predictions**:

### Current Production Champion Model: `v1.2.0`
- **Algorithm**: `HistGradientBoosting Regressor` (`MultiOutputRegressor`)
- **Dual Targets**:
  1. `actual_delay_minutes` (arrival delay relative to official timetable)
  2. `actual_remaining_travel_minutes` (estimated travel duration to SECE campus)
- **Features (14)**:
  - `route_id`, `stop_id`, `day_of_week`, `departure_hour`, `departure_minute`
  - `segment_distance_km`, `remaining_distance_km`, `number_of_remaining_stops`
  - `traffic_level`, `weather_condition`, `temperature`, `rainfall`, `humidity`, `previous_trip_delay`
- **Leakage Prevention**: Strictly excludes future information (actual arrival time, future delay, downstream traffic).

### Evaluation Metrics (Simulated-Data Benchmark)
- **Validation Delay MAE**: **1.477 minutes**
- **Test Delay MAE**: **1.644 minutes**
- **Test Delay RMSE**: **2.972 minutes**
- **Test Overall $R^2$**: **0.955**
- **Historical Baseline Val MAE**: 6.050 minutes (**75.6% improvement over baseline**)
- **Overfitting Gap**: 11.3% (Well within standard 40% generalization threshold)
- **Estimated Prediction Interval**: Statistical 80% uncertainty bounds derived from validation residual quantiles (e.g., $\pm 2.3$ mins).

### Top Predictive Features (Permutation Importance)
1. `remaining_distance_km` (+14.86 min score)
2. `previous_trip_delay` (+4.22 min score)
3. `segment_distance_km` (+1.68 min score)
4. `rainfall` (+1.38 min score)
5. `number_of_remaining_stops` (+1.10 min score)
6. `day_of_week` (+0.65 min score)
7. `traffic_level` (+0.24 min score)

---

## 💻 Tech Stack & Architecture

```
BusFlow/
├── frontend/                     # React 18 + Vite SPA
│   ├── src/
│   │   ├── components/           # Navbar, BubbleBackground, MetricCard, Maps, Modals
│   │   ├── pages/                # 8 Application Pages (Landing, Auth, Dashboards, ML)
│   │   ├── context/              # AuthContext, ToastContext
│   │   ├── hooks/                # useRoutes, usePrediction, useTripStatus, useBackendStatus
│   │   └── services/             # studentService, driverService, adminService, api
│   ├── tailwind.config.js
│   └── package.json
├── backend/                      # Python FastAPI Service
│   ├── app/
│   │   ├── api/                  # auth, student, driver, admin, health endpoints
│   │   ├── models/               # SQLAlchemy ORM (11 tables)
│   │   ├── schemas/              # Pydantic validation schemas
│   │   ├── services/             # weather_service (Open-Meteo), trip_service
│   │   ├── ml/                   # train_model, predict, evaluate, preprocessing
│   │   └── database/             # SQLite session & engine
│   ├── datasets/                 # college_routes.csv, bus_trip_history.csv (7,920 rows)
│   ├── trained_models/           # champion_model.joblib, model_metadata.json, ML_AUDIT_REPORT.md
│   ├── tests/                    # 32 pytest unit and integration tests
│   └── phase6_integration_tests.py # 23-point system verification suite
└── README.md
```

- **Frontend**: React 18, Vite 5, Tailwind CSS, Framer Motion, Recharts, Leaflet / React-Leaflet, Lucide React
- **Backend**: FastAPI, SQLAlchemy 2.0, Pydantic v2, SQLite
- **ML / Data**: Scikit-Learn 1.3+, NumPy, Pandas, Joblib
- **Weather API**: Open-Meteo CC BY 4.0 (`10.85° N, 76.98° E` – Coimbatore Area Grid)

---

## 📡 REST API Directory

### Authentication (`/api/auth`)
- `POST /api/auth/register` – Register new Student, Driver, or Admin
- `POST /api/auth/login` – Salted PBKDF2 verification & JWT token generation
- `GET /api/auth/me` – Current authenticated user session

### Student Portal (`/api/student`)
- `GET /api/student/routes` – All 10 active SECE routes with ordered stops & GPS coordinates
- `GET /api/student/schedules` – Timetable departures
- `GET /api/student/prediction?route_id={id}&stop_id={id}` – Live ML arrival prediction, delay, remaining travel time, and 80% prediction interval
- `GET /api/student/trip-status?route_id={id}` – Real-time route progress, current stop, next stop, and delay status

### Driver Cockpit (`/api/driver`)
- `GET /api/driver/assigned-bus` – Bus, route, and active trip assigned to driver
- `POST /api/driver/trip/start` – Start morning/evening college bus run
- `POST /api/driver/trip/update` – Check in at intermediate stop (actual arrival/departure)
- `POST /api/driver/traffic` – Broadcast road traffic conditions (`LOW`, `MEDIUM`, `HIGH`, `SEVERE`)
- `POST /api/driver/weather` – Snapshot weather observations
- `POST /api/driver/trip/complete` – Complete trip at SECE Campus

### Admin Portal (`/api/admin`)
- `GET /api/admin/dashboard` – Fleet KPIs, active trips, delays, traffic alerts
- `POST /api/admin/routes` – Create new college route with stop sequence
- `PUT /api/admin/routes/{id}` – Update route metadata
- `DELETE /api/admin/routes/{id}` – Deactivate route
- `POST /api/admin/datasets/upload` – Ingest trip log CSV
- `POST /api/admin/model/train` – Trigger retraining with validation gating
- `GET /api/admin/model/metrics` – Champion model metrics (Validation & Test MAE, RMSE, $R^2$)
- `GET /api/admin/model/history` – Complete training history log from SQLite

---

## 🧪 Testing & Verification

BusFlow includes comprehensive test suites spanning unit, integration, and ML audit tests:

### 1. Pytest Unit & Integration Suite
```bash
cd backend
python -m pytest tests/ -v
```
- **32 / 32 Passed**: Covers authentication, RBAC, route management, ML pipelines, inference engine, weather service, and trip lifecycles.

### 2. Phase 6 End-to-End System Verification
```bash
cd backend
python phase6_integration_tests.py
```
- **23 / 23 Passed**:
  - Auth: Password hashing, demo account integrity, RBAC tokens
  - Routes: 10 authentic SECE routes, 88 sequential stops, foreign keys
  - Machine Learning: Model loading, feature response, zero target leakage, metrics validation, robustness on unseen data
  - Driver: Assigned bus query, complete trip lifecycle (start → traffic report → complete)
  - Student: Profile loading, real-time prediction and schedule fallback
  - Admin: Statistics calculation, metadata synchronization
  - Weather: Open-Meteo fallback handling, Coimbatore GPS bounds
  - Frontend Build: 1,025KB JS bundle, all 8 pages, all 12 core components verified

### 3. Senior ML Audit & Hyperparameter Grid Search
```bash
cd backend
python ml_audit.py
```
- Audited feature importances, peak-hour bias, route-wise residuals, and promoted tuned model `v1.2.0` with `ML_AUDIT_REPORT.md`.

### 4. Frontend Production Build Check
```bash
cd frontend
npm run build
```
- **Zero build errors**: 2,572 modules transformed in 5.98s.

---

## ⚠️ Limitations & Real-World Notice

1. **Synthetic Training Seeds**: The historical dataset (7,920 records) was synthetically generated using authentic SECE timetable schedules and realistic Coimbatore weather/traffic patterns. All simulated rows are tagged `is_synthetic = True`.
2. **Real-World Calibration**: While the model achieves a 1.64-minute test MAE on simulated distributions, real-world deployment requires capturing physical GPS telematics from college buses to retrain and calibrate the champion model.
3. **Weather Attribution**: Weather forecasts and condition estimates are powered by [Open-Meteo](https://open-meteo.com/) under the CC BY 4.0 license for the SECE campus coordinates (`10.85° N, 76.98° E`).
4. **Estimated Prediction Interval**: Uncertainty ranges are calculated using the 80% validation residual quantile method and are explicitly presented as *Estimated Prediction Intervals* rather than absolute guarantees.
