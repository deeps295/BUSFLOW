# BusFlow Dataset Summary & Quality Audit Report
*Exclusively Localized to Sri Eshwar College of Engineering (SECE), Coimbatore, Tamil Nadu, India*

---

## 1. Dataset Overview & Inventory

| Dataset File | File Format | Record Count | Scope / Purpose | Authenticity Status |
| :--- | :--- | :--- | :--- | :--- |
| **`college_routes.csv`** | CSV | **88 stops across 10 routes** | Official SECE bus routes, stop sequences, distances, coordinates, and landmarks. | **Authentic official SECE transit records** |
| **`bus_trip_history.csv`** | CSV | **7,920 trip-segment records** | Multi-month simulated operational trip logs across 900 trips for ML regression training. | **100% Synthetic (Simulated physics model)** |

---

## 2. Authentic SECE Route Specifications (`college_routes.csv`)

All 10 operational corridors terminate at the **Sri Eshwar College of Engineering Campus Gate, Kondampatti, Kinathukadavu** (`10.8284° N, 77.0146° E`):

| Route ID | Route Number | Origin | Key Intermediate Stops & Bottlenecks | Stops Count | Distance (km) | Morning Dep. |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| `R01_BHARATHIAR` | Bus 1 | Bharathiar University | Vadavalli, Gandhi Park, Ukkadam, Sundarapuram, Eachanari | 10 | 48.6 km | 07:00 AM |
| `R02_KOTTAMPATTI_POLLACHI` | Bus 2 | Kottampatti Junction | Pollachi New Bus Stand, Achipatti, Kovilpalayam, Thamaraikulam | 9 | 24.8 km | 07:15 AM |
| `R03_SARAVANAMPATTI` | Bus 3 | Saravanampatti | Ganapathy, Gandhipuram, Lakshmi Mills, Ramanathapuram, Podanur | 10 | 42.1 km | 06:55 AM |
| `R04_KOVAIPUDUR` | Bus 4 | Kovaipudur | Kuniyamuthur, Athupalam, Sundarapuram, SIDCO, Eachanari | 9 | 26.4 km | 07:10 AM |
| `R05_VADAKKIPALAYAM` | Bus 5 | Vadakkipalayam Village | Ponnapuram, Sulakkal Temple, Vadakkipalayam Pirivu, Thamaraikulam | 7 | 25.1 km | 07:20 AM |
| `R06_SULUR` | Bus 6 | Sulur Bus Stand | Ondipudur, Singanallur, Podanur, Chettipalayam, Vadasithur | 9 | 36.2 km | 07:00 AM |
| `R07_POLLACHI_CENTRAL` | Bus 7 | Pollachi Central | Mahalingam College (MCET), Achipatti, Kovilpalayam, Kinathukadavu | 8 | 21.3 km | 07:25 AM |
| `R08_PERIYANAICKENPALAYAM` | Bus 8 | Periyanaickenpalayam | Thudiyalur, Saibaba Colony, Gandhipuram, Ukkadam, Eachanari | 10 | 50.8 km | 06:45 AM |
| `R09_PALLADAM` | Bus 9 | Palladam Bus Stand | Lakshmi Mills Palladam, Karanampettai, Panapatti, Sulthanpet, Vadasithur | 8 | 34.6 km | 07:05 AM |
| `R10_UDUMALPET` | Bus 10 | Udumalpet Central | Bodipatti, Pukkulam, Pethappampatti, Negamam, Devanampalayam | 8 | 44.5 km | 06:50 AM |
| **Total Network** | **10 Buses** | — | — | **88 Stops** | **354.4 km** | — |

---

## 3. Simulated Trip History Specifications (`bus_trip_history.csv`)

### 3.1 Feature Inventory & Types
| Feature Name | Data Type | Non-Null Count | Definition & Range |
| :--- | :--- | :--- | :--- |
| `trip_id` | String | 7,920 (100%) | Unique trip identifier (`TRIP_YYYYMMDD_ROUTE_ID_NNNN`) |
| `bus_id` | String | 7,920 (100%) | Assigned bus registration (`TN-38-BZ-XXXX`) |
| `route_id` | String | 7,920 (100%) | SECE route identifier (`R01` to `R10`) |
| `stop_id` | String | 7,920 (100%) | Stop identifier (`Rxx_Sxx`) |
| `stop_name` | String | 7,920 (100%) | Official published stop name |
| `stop_sequence` | Integer | 7,920 (100%) | Chronological stop index along route (1 to 10) |
| `trip_date` | Date (YYYY-MM-DD) | 7,920 (100%) | Date of trip execution (90 college calendar days) |
| `day_of_week` | String | 7,920 (100%) | Monday through Saturday |
| `scheduled_departure_time` | Time (HH:MM:SS) | 7,920 (100%) | Timetable departure from stop |
| `actual_departure_time` | Time (HH:MM:SS) | 7,920 (100%) | Simulated actual departure from stop |
| `scheduled_arrival_time` | Time (HH:MM:SS) | 7,920 (100%) | Timetable arrival at stop |
| `actual_arrival_time` | Time (HH:MM:SS) | 7,920 (100%) | Simulated actual arrival at stop |
| `segment_distance_km` | Float | 7,920 (100%) | Distance from previous stop ($0.0 - 11.2\text{ km}$) |
| `remaining_distance_km` | Float | 7,920 (100%) | Distance left to SECE Campus ($0.0 - 50.8\text{ km}$) |
| `number_of_remaining_stops` | Integer | 7,920 (100%) | Remaining stops until destination ($0 - 9$) |
| `traffic_level` | Categorical | 7,920 (100%) | `LOW`, `MEDIUM`, `HIGH`, `SEVERE` |
| `weather_condition` | Categorical | 7,920 (100%) | `CLEAR`, `CLOUDY`, `LIGHT_RAIN`, `MODERATE_RAIN`, `HEAVY_RAIN` |
| `temperature` | Float | 7,920 (100%) | Ambient temperature ($21.0 - 37.0^\circ\text{C}$) |
| `rainfall` | Float | 7,920 (100%) | Precipitation in mm ($0.0 - 24.8\text{ mm}$) |
| `humidity` | Float | 7,920 (100%) | Relative humidity ($45.0 - 95.0\%$) |
| `previous_trip_delay` | Float | 7,920 (100%) | Delay carried forward from upstream stop (mins) |
| `actual_delay_minutes` | Float | 7,920 (100%) | **Target 1**: Stop arrival delay ($Actual - Scheduled$) |
| `actual_remaining_travel_minutes`| Float | 7,920 (100%) | **Target 2**: Total remaining time to reach SECE Campus |
| `is_synthetic` | Boolean | 7,920 (100%) | **`True`** (Strict transparency audit flag) |

---

## 4. Quality Audit & Validation Results

| Quality Check | Criteria | Audit Result | Status |
| :--- | :--- | :--- | :--- |
| **Localization Boundary** | All stops within Coimbatore transit bounds (`10.45° - 11.25° N`, `76.75° - 77.35° E`) | Min Lat: `10.5850°`, Max Lat: `11.1440°`<br>Min Lon: `76.8837°`, Max Lon: `77.2880°` | **PASSED (100%)** |
| **Destination Consistency** | All routes terminate at SECE Campus | All 10 routes terminate at SECE Gate, Kondampatti | **PASSED (100%)** |
| **Missing Values** | Zero missing values across all columns | 0 missing values detected in all 7,920 rows | **PASSED (0.00%)** |
| **Duplicate Check** | Unique `(trip_id, stop_id)` combinations | 0 duplicate records detected | **PASSED** |
| **Synthetic Transparency**| All simulated records flagged as synthetic | `is_synthetic == True` across 7,920 of 7,920 rows | **PASSED (100%)** |
| **Target Distribution** | Delay distribution statistics | Mean: **7.62 mins**, Std: **14.01 mins**, Min: **-2.0 mins**, Max: **118.4 mins** | **PASSED (Realistic)** |
| **Traffic Breakdown** | Realistic Coimbatore traffic distribution | **MEDIUM**: 3,595 (45.4%)<br>**LOW**: 2,348 (29.6%)<br>**HIGH**: 1,452 (18.3%)<br>**SEVERE**: 525 (6.6%) | **PASSED** |
| **Outlier Profile (IQR)**| Expected breakdown / severe weather spikes | 502 records (6.34%) exceeding $Q_3 + 1.5 \times \text{IQR}$ (15.5 mins), representing peak junction gridlocks & rain disruptions | **PASSED** |

---

## 5. Preprocessing & Feature Engineering Matrix

The preprocessing pipeline in `app/ml/preprocessing.py` equips the dataset for Phase 3 regression modeling:
- **Temporal Encodings**: `scheduled_hour`, `scheduled_minute`, `scheduled_time_minutes`, `is_morning_peak` (07:30–08:45 AM), `is_evening_peak` (16:30–17:45 PM), `day_of_week_num`, `is_monday`, `is_saturday`.
- **Ordinal Encodings**: `traffic_level_ordinal` (0 to 3), `weather_ordinal` (0 to 4).
- **Domain Interation Features**: `weather_friction_index`, `stop_sequence_norm`, `distance_progress_ratio`.
- **Chronological Split**:
  - **Training Set**: 62 days (5,456 records, 68.9%)
  - **Validation Set**: 14 days (1,232 records, 15.6%)
  - **Test Set**: 14 days (1,232 records, 15.6%)
  - **Look-Ahead Leakage**: Zero (Strict chronological partition with no overlap).
