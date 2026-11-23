"""
BusFlow Dataset Generator for Sri Eshwar College of Engineering (SECE), Coimbatore.
Generates:
1. college_routes.csv - Authentic SECE bus routes, stop sequences, and coordinates.
2. bus_trip_history.csv - High-fidelity simulated trip-segment records with realistic
   Coimbatore traffic, weather, peak-hour, and delay propagation dynamics.

All generated records are explicitly tagged with `is_synthetic = True`.
"""

import os
import math
import random
from pathlib import Path
from datetime import datetime, date, time, timedelta
import pandas as pd
import numpy as np

# Reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

DATASETS_DIR = Path(__file__).resolve().parent.parent.parent / "datasets"
DATASETS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Authentic SECE Route Definitions (Coimbatore District, Tamil Nadu)
# ---------------------------------------------------------------------------
SECE_ROUTES = [
    {
        "route_id": "R01_BHARATHIAR",
        "route_number": "Bus 1",
        "route_name": "Bharathiar University to SECE via Vadavalli & Ukkadam",
        "origin_name": "Bharathiar University",
        "destination_name": "SECE Campus, Kinathukadavu",
        "departure_time": "07:00:00",
        "stops": [
            {"stop_id": "R01_S01", "name": "Bharathiar University Main Gate", "lat": 11.0402, "lon": 76.8837, "offset": 0, "major": False, "landmark": "University Arch"},
            {"stop_id": "R01_S02", "name": "Vadavalli Bus Terminus", "lat": 11.0264, "lon": 76.9042, "offset": 9, "major": False, "landmark": "Marudhamalai Main Rd"},
            {"stop_id": "R01_S03", "name": "P.N Pudhur", "lat": 11.0180, "lon": 76.9210, "offset": 16, "major": False, "landmark": "Corporation Bank"},
            {"stop_id": "R01_S04", "name": "Gandhi Park / R.S. Puram", "lat": 11.0068, "lon": 76.9421, "offset": 25, "major": True, "landmark": "Gandhi Park Roundabout"},
            {"stop_id": "R01_S05", "name": "Ukkadam Bus Terminus", "lat": 10.9892, "lon": 76.9582, "offset": 37, "major": True, "landmark": "Ukkadam Flyover Junction"},
            {"stop_id": "R01_S06", "name": "Sundarapuram Junction", "lat": 10.9490, "lon": 76.9678, "offset": 49, "major": True, "landmark": "Pollachi Main Road"},
            {"stop_id": "R01_S07", "name": "Eachanari Temple Junction", "lat": 10.9275, "lon": 76.9740, "offset": 58, "major": True, "landmark": "Vinayagar Temple NH-83"},
            {"stop_id": "R01_S08", "name": "Malumichampatti Pirivu", "lat": 10.8980, "lon": 76.9880, "offset": 66, "major": False, "landmark": "L&T Bypass Pirivu"},
            {"stop_id": "R01_S09", "name": "Kinathukadavu Old Bus Stand", "lat": 10.8250, "lon": 77.0195, "offset": 78, "major": False, "landmark": "Kinathukadavu Police Station"},
            {"stop_id": "R01_S10", "name": "SECE Campus Gate, Kondampatti", "lat": 10.8284, "lon": 77.0146, "offset": 85, "major": False, "landmark": "Sri Eshwar Main Entrance"},
        ]
    },
    {
        "route_id": "R02_KOTTAMPATTI_POLLACHI",
        "route_number": "Bus 2",
        "route_name": "Kottampatti & Pollachi to SECE via Sulakkal",
        "origin_name": "Kottampatti Junction",
        "destination_name": "SECE Campus, Kinathukadavu",
        "departure_time": "07:15:00",
        "stops": [
            {"stop_id": "R02_S01", "name": "Kottampatti Junction", "lat": 10.6580, "lon": 77.0090, "offset": 0, "major": False, "landmark": "Kottampatti Pirivu"},
            {"stop_id": "R02_S02", "name": "Vijayapuram Bunk", "lat": 10.6550, "lon": 77.0140, "offset": 7, "major": False, "landmark": "Indian Oil Fuel Pump"},
            {"stop_id": "R02_S03", "name": "Rajeshwari Hall / Mahalingapuram", "lat": 10.6620, "lon": 77.0110, "offset": 14, "major": False, "landmark": "Mahalingapuram Roundana"},
            {"stop_id": "R02_S04", "name": "Pollachi New Bus Stand", "lat": 10.6655, "lon": 77.0080, "offset": 22, "major": True, "landmark": "Central Clock Tower"},
            {"stop_id": "R02_S05", "name": "Achipatti Junction", "lat": 10.6950, "lon": 77.0120, "offset": 30, "major": False, "landmark": "Coimbatore Rd Toll Pirivu"},
            {"stop_id": "R02_S06", "name": "Kovilpalayam Pirivu", "lat": 10.7350, "lon": 77.0150, "offset": 38, "major": False, "landmark": "Kovilpalayam Bus Stop"},
            {"stop_id": "R02_S07", "name": "Thamaraikulam", "lat": 10.7780, "lon": 77.0175, "offset": 46, "major": False, "landmark": "Thamaraikulam High School"},
            {"stop_id": "R02_S08", "name": "Kinathukadavu New Bus Stand", "lat": 10.8220, "lon": 77.0210, "offset": 55, "major": False, "landmark": "NH-83 Elevated Highway"},
            {"stop_id": "R02_S09", "name": "SECE Campus Gate, Kondampatti", "lat": 10.8284, "lon": 77.0146, "offset": 62, "major": False, "landmark": "Sri Eshwar Main Entrance"},
        ]
    },
    {
        "route_id": "R03_SARAVANAMPATTI",
        "route_number": "Bus 3",
        "route_name": "Saravanampatti to SECE via Gandhipuram & Podanur",
        "origin_name": "Saravanampatti",
        "destination_name": "SECE Campus, Kinathukadavu",
        "departure_time": "06:55:00",
        "stops": [
            {"stop_id": "R03_S01", "name": "Saravanampatti Checkpost", "lat": 11.0780, "lon": 76.9940, "offset": 0, "major": True, "landmark": "CHIL SEZ IT Park Junction"},
            {"stop_id": "R03_S02", "name": "Bharathi Nagar", "lat": 11.0550, "lon": 76.9890, "offset": 8, "major": False, "landmark": "Sathy Main Road"},
            {"stop_id": "R03_S03", "name": "Ganapathy Bus Stop", "lat": 11.0360, "lon": 76.9800, "offset": 17, "major": True, "landmark": "Ganapathy Police Station"},
            {"stop_id": "R03_S04", "name": "Gandhipuram Central Bus Stand", "lat": 11.0175, "lon": 76.9675, "offset": 28, "major": True, "landmark": "Cross Cut Road Signal"},
            {"stop_id": "R03_S05", "name": "Lakshmi Mills Junction", "lat": 11.0110, "lon": 76.9830, "offset": 37, "major": True, "landmark": "Avinashi Road Flyover"},
            {"stop_id": "R03_S06", "name": "Ramanathapuram Signal", "lat": 10.9980, "lon": 76.9870, "offset": 46, "major": True, "landmark": "Trichy Road Junction"},
            {"stop_id": "R03_S07", "name": "Podanur Railway Junction", "lat": 10.9630, "lon": 76.9900, "offset": 57, "major": False, "landmark": "Railway Station Road"},
            {"stop_id": "R03_S08", "name": "Eachanari Junction", "lat": 10.9275, "lon": 76.9740, "offset": 68, "major": True, "landmark": "NH-83 Bypass Junction"},
            {"stop_id": "R03_S09", "name": "Malumichampatti", "lat": 10.8980, "lon": 76.9880, "offset": 76, "major": False, "landmark": "Petrol Bunk"},
            {"stop_id": "R03_S10", "name": "SECE Campus Gate, Kondampatti", "lat": 10.8284, "lon": 77.0146, "offset": 88, "major": False, "landmark": "Sri Eshwar Main Entrance"},
        ]
    },
    {
        "route_id": "R04_KOVAIPUDUR",
        "route_number": "Bus 4",
        "route_name": "Kovaipudur to SECE via Kuniyamuthur & Sundarapuram",
        "origin_name": "Kovaipudur",
        "destination_name": "SECE Campus, Kinathukadavu",
        "departure_time": "07:10:00",
        "stops": [
            {"stop_id": "R04_S01", "name": "Kovaipudur Bus Stand", "lat": 10.9380, "lon": 76.9320, "offset": 0, "major": False, "landmark": "Kovaipudur 'T' Junction"},
            {"stop_id": "R04_S02", "name": "Kovaipudur Pirivu", "lat": 10.9480, "lon": 76.9420, "offset": 8, "major": False, "landmark": "Palakkad Main Road"},
            {"stop_id": "R04_S03", "name": "Kuniyamuthur Market", "lat": 10.9620, "lon": 76.9480, "offset": 17, "major": True, "landmark": "Kuniyamuthur Post Office"},
            {"stop_id": "R04_S04", "name": "Athupalam Bridge", "lat": 10.9780, "lon": 76.9530, "offset": 28, "major": True, "landmark": "Noyyal River Bridge"},
            {"stop_id": "R04_S05", "name": "Sundarapuram Junction", "lat": 10.9490, "lon": 76.9678, "offset": 40, "major": True, "landmark": "SIDCO Road Pirivu"},
            {"stop_id": "R04_S06", "name": "SIDCO Industrial Estate", "lat": 10.9360, "lon": 76.9710, "offset": 48, "major": False, "landmark": "SIDCO Substation"},
            {"stop_id": "R04_S07", "name": "Eachanari Temple", "lat": 10.9275, "lon": 76.9740, "offset": 55, "major": True, "landmark": "Temple Arch"},
            {"stop_id": "R04_S08", "name": "Kinathukadavu", "lat": 10.8250, "lon": 77.0195, "offset": 67, "major": False, "landmark": "Old Bus Stand"},
            {"stop_id": "R04_S09", "name": "SECE Campus Gate, Kondampatti", "lat": 10.8284, "lon": 77.0146, "offset": 74, "major": False, "landmark": "Sri Eshwar Main Entrance"},
        ]
    },
    {
        "route_id": "R05_VADAKKIPALAYAM",
        "route_number": "Bus 5",
        "route_name": "Vadakkipalayam to SECE via Sulakkal & Thamaraikulam",
        "origin_name": "Vadakkipalayam Village",
        "destination_name": "SECE Campus, Kinathukadavu",
        "departure_time": "07:20:00",
        "stops": [
            {"stop_id": "R05_S01", "name": "Vadakkipalayam Village", "lat": 10.7420, "lon": 76.9320, "offset": 0, "major": False, "landmark": "Village Panchayat Office"},
            {"stop_id": "R05_S02", "name": "Ponnapuram Pirivu", "lat": 10.7250, "lon": 76.9620, "offset": 10, "major": False, "landmark": "Rural Bank Stop"},
            {"stop_id": "R05_S03", "name": "Sulakkal Mariamman Temple", "lat": 10.7480, "lon": 76.9880, "offset": 20, "major": False, "landmark": "Temple Bazaar"},
            {"stop_id": "R05_S04", "name": "Vadakkipalayam Pirivu", "lat": 10.7710, "lon": 77.0050, "offset": 30, "major": False, "landmark": "Pollachi Highway Link"},
            {"stop_id": "R05_S05", "name": "Thamaraikulam Junction", "lat": 10.7780, "lon": 77.0175, "offset": 39, "major": False, "landmark": "Thamaraikulam Bus Stand"},
            {"stop_id": "R05_S06", "name": "Kinathukadavu", "lat": 10.8250, "lon": 77.0195, "offset": 49, "major": False, "landmark": "Overbridge Exit"},
            {"stop_id": "R05_S07", "name": "SECE Campus Gate, Kondampatti", "lat": 10.8284, "lon": 77.0146, "offset": 56, "major": False, "landmark": "Sri Eshwar Main Entrance"},
        ]
    },
    {
        "route_id": "R06_SULUR",
        "route_number": "Bus 6",
        "route_name": "Sulur to SECE via Singanallur & Vadasithur",
        "origin_name": "Sulur Bus Stand",
        "destination_name": "SECE Campus, Kinathukadavu",
        "departure_time": "07:00:00",
        "stops": [
            {"stop_id": "R06_S01", "name": "Sulur Bus Stand", "lat": 11.0260, "lon": 77.1260, "offset": 0, "major": True, "landmark": "Sulur Town Hall"},
            {"stop_id": "R06_S02", "name": "Ravathur Pirivu", "lat": 11.0180, "lon": 77.0980, "offset": 9, "major": False, "landmark": "Trichy Road HP Bunk"},
            {"stop_id": "R06_S03", "name": "Ondipudur Flyover", "lat": 11.0020, "lon": 77.0650, "offset": 19, "major": True, "landmark": "Ondipudur Bus Depot"},
            {"stop_id": "R06_S04", "name": "Singanallur Bus Stand", "lat": 10.9980, "lon": 77.0260, "offset": 29, "major": True, "landmark": "Singanallur Signal Junction"},
            {"stop_id": "R06_S05", "name": "Perks School / Uppilipalayam", "lat": 10.9950, "lon": 77.0090, "offset": 37, "major": False, "landmark": "Perks Campus Gate"},
            {"stop_id": "R06_S06", "name": "Podanur Market", "lat": 10.9630, "lon": 76.9900, "offset": 48, "major": False, "landmark": "Railway Workshop"},
            {"stop_id": "R06_S07", "name": "Chettipalayam Pirivu", "lat": 10.9150, "lon": 77.0100, "offset": 58, "major": False, "landmark": "Chettipalayam Ring Road"},
            {"stop_id": "R06_S08", "name": "Vadasithur Bus Stop", "lat": 10.8420, "lon": 77.0220, "offset": 70, "major": False, "landmark": "Vadasithur Post Office"},
            {"stop_id": "R06_S09", "name": "SECE Campus Gate, Kondampatti", "lat": 10.8284, "lon": 77.0146, "offset": 77, "major": False, "landmark": "Sri Eshwar Main Entrance"},
        ]
    },
    {
        "route_id": "R07_POLLACHI_CENTRAL",
        "route_number": "Bus 7",
        "route_name": "Pollachi Central Express to SECE via Kovilpalayam",
        "origin_name": "Pollachi Central Bus Stand",
        "destination_name": "SECE Campus, Kinathukadavu",
        "departure_time": "07:25:00",
        "stops": [
            {"stop_id": "R07_S01", "name": "Pollachi Central Bus Stand", "lat": 10.6655, "lon": 77.0080, "offset": 0, "major": True, "landmark": "Terminal 1 Gate"},
            {"stop_id": "R07_S02", "name": "Mahalingam College Gate", "lat": 10.6820, "lon": 77.0105, "offset": 8, "major": False, "landmark": "MCET Campus Bus Bay"},
            {"stop_id": "R07_S03", "name": "Achipatti Industrial Area", "lat": 10.6950, "lon": 77.0120, "offset": 15, "major": False, "landmark": "SIDCO Pollachi"},
            {"stop_id": "R07_S04", "name": "Kovilpalayam Bus Stop", "lat": 10.7350, "lon": 77.0150, "offset": 23, "major": False, "landmark": "Panchayat Board"},
            {"stop_id": "R07_S05", "name": "Thamaraikulam Market", "lat": 10.7780, "lon": 77.0175, "offset": 31, "major": False, "landmark": "Thamaraikulam High School"},
            {"stop_id": "R07_S06", "name": "Kinathukadavu Flyover", "lat": 10.8220, "lon": 77.0210, "offset": 41, "major": False, "landmark": "Kinathukadavu North Toll"},
            {"stop_id": "R07_S07", "name": "Kondampatti Pirivu", "lat": 10.8270, "lon": 77.0160, "offset": 47, "major": False, "landmark": "Kondampatti Road Sign"},
            {"stop_id": "R07_S08", "name": "SECE Campus Gate, Kondampatti", "lat": 10.8284, "lon": 77.0146, "offset": 51, "major": False, "landmark": "Sri Eshwar Main Entrance"},
        ]
    },
    {
        "route_id": "R08_PERIYANAICKENPALAYAM",
        "route_number": "Bus 8",
        "route_name": "Periyanaickenpalayam to SECE via Thudiyalur & Ukkadam",
        "origin_name": "Periyanaickenpalayam",
        "destination_name": "SECE Campus, Kinathukadavu",
        "departure_time": "06:45:00",
        "stops": [
            {"stop_id": "R08_S01", "name": "Periyanaickenpalayam Bus Stand", "lat": 11.1440, "lon": 76.9380, "offset": 0, "major": True, "landmark": "Ramakrishna Mission Gate"},
            {"stop_id": "R08_S02", "name": "Thudiyalur Junction", "lat": 11.0820, "lon": 76.9420, "offset": 15, "major": True, "landmark": "Mettupalayam Rd Junction"},
            {"stop_id": "R08_S03", "name": "Saibaba Colony Signal", "lat": 11.0330, "lon": 76.9480, "offset": 28, "major": True, "landmark": "NSR Road Cross"},
            {"stop_id": "R08_S04", "name": "Gandhipuram Town Bus Stand", "lat": 11.0175, "lon": 76.9675, "offset": 40, "major": True, "landmark": "Central Bus Stand Complex"},
            {"stop_id": "R08_S05", "name": "Ukkadam Bus Stand", "lat": 10.9892, "lon": 76.9582, "offset": 54, "major": True, "landmark": "Ukkadam Lake Flyover"},
            {"stop_id": "R08_S06", "name": "Sundarapuram", "lat": 10.9490, "lon": 76.9678, "offset": 66, "major": True, "landmark": "Pollachi Main Road"},
            {"stop_id": "R08_S07", "name": "Eachanari Temple", "lat": 10.9275, "lon": 76.9740, "offset": 74, "major": True, "landmark": "Vinayagar Temple Arch"},
            {"stop_id": "R08_S08", "name": "Malumichampatti", "lat": 10.8980, "lon": 76.9880, "offset": 82, "major": False, "landmark": "Bypass Intersection"},
            {"stop_id": "R08_S09", "name": "Kinathukadavu", "lat": 10.8250, "lon": 77.0195, "offset": 94, "major": False, "landmark": "Old Bus Stand"},
            {"stop_id": "R08_S10", "name": "SECE Campus Gate, Kondampatti", "lat": 10.8284, "lon": 77.0146, "offset": 102, "major": False, "landmark": "Sri Eshwar Main Entrance"},
        ]
    },
    {
        "route_id": "R09_PALLADAM",
        "route_number": "Bus 9",
        "route_name": "Palladam to SECE via Sulthanpet & Vadasithur",
        "origin_name": "Palladam Bus Stand",
        "destination_name": "SECE Campus, Kinathukadavu",
        "departure_time": "07:05:00",
        "stops": [
            {"stop_id": "R09_S01", "name": "Palladam Bus Stand", "lat": 10.9990, "lon": 77.2880, "offset": 0, "major": True, "landmark": "Palladam Town Center"},
            {"stop_id": "R09_S02", "name": "Lakshmi Mills Palladam", "lat": 10.9880, "lon": 77.2620, "offset": 8, "major": False, "landmark": "Mill Colony Stop"},
            {"stop_id": "R09_S03", "name": "Karanampettai Junction", "lat": 10.9650, "lon": 77.2250, "offset": 19, "major": True, "landmark": "Coimbatore Highway Pirivu"},
            {"stop_id": "R09_S04", "name": "Panapatti Pirivu", "lat": 10.9320, "lon": 77.1850, "offset": 29, "major": False, "landmark": "Panapatti Village Road"},
            {"stop_id": "R09_S05", "name": "Sulthanpet Bus Stop", "lat": 10.8920, "lon": 77.1420, "offset": 40, "major": False, "landmark": "Sulthanpet Union Office"},
            {"stop_id": "R09_S06", "name": "Senjerimalai Pirivu", "lat": 10.8650, "lon": 77.0980, "offset": 50, "major": False, "landmark": "Temple Hill Road"},
            {"stop_id": "R09_S07", "name": "Vadasithur Market", "lat": 10.8420, "lon": 77.0220, "offset": 62, "major": False, "landmark": "Vadasithur High School"},
            {"stop_id": "R09_S08", "name": "SECE Campus Gate, Kondampatti", "lat": 10.8284, "lon": 77.0146, "offset": 70, "major": False, "landmark": "Sri Eshwar Main Entrance"},
        ]
    },
    {
        "route_id": "R10_UDUMALPET",
        "route_number": "Bus 10",
        "route_name": "Udumalpet to SECE via Negamam & Kinathukadavu",
        "origin_name": "Udumalpet Central Bus Stand",
        "destination_name": "SECE Campus, Kinathukadavu",
        "departure_time": "06:50:00",
        "stops": [
            {"stop_id": "R10_S01", "name": "Udumalpet Central Bus Stand", "lat": 10.5850, "lon": 77.2480, "offset": 0, "major": True, "landmark": "Udumalpet Central Depot"},
            {"stop_id": "R10_S02", "name": "Bodipatti Junction", "lat": 10.6020, "lon": 77.2210, "offset": 9, "major": False, "landmark": "Bodipatti Checkpost"},
            {"stop_id": "R10_S03", "name": "Pukkulam Bus Stop", "lat": 10.6350, "lon": 77.1820, "offset": 19, "major": False, "landmark": "Pukkulam Panchayat"},
            {"stop_id": "R10_S04", "name": "Pethappampatti", "lat": 10.6720, "lon": 77.1450, "offset": 30, "major": False, "landmark": "Pethappampatti Roundana"},
            {"stop_id": "R10_S05", "name": "Negamam Bus Stand", "lat": 10.7450, "lon": 77.0850, "offset": 44, "major": True, "landmark": "Handloom Weavers Bazaar"},
            {"stop_id": "R10_S06", "name": "Devanampalayam", "lat": 10.7850, "lon": 77.0520, "offset": 54, "major": False, "landmark": "Rural Bus Bay"},
            {"stop_id": "R10_S07", "name": "Kinathukadavu", "lat": 10.8250, "lon": 77.0195, "offset": 66, "major": False, "landmark": "Kinathukadavu Old Bus Stand"},
            {"stop_id": "R10_S08", "name": "SECE Campus Gate, Kondampatti", "lat": 10.8284, "lon": 77.0146, "offset": 74, "major": False, "landmark": "Sri Eshwar Main Entrance"},
        ]
    }
]

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Accurate spherical distance in km between two coordinate pairs."""
    r = 6371.0 # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    # Multiply by road winding curvature factor (approx 1.22 for Coimbatore roads)
    return round(r * c * 1.22, 2)

def generate_college_routes_dataset():
    """Generates college_routes.csv with authentic stop sequences and verified coordinates."""
    route_rows = []
    
    for r_idx, route in enumerate(SECE_ROUTES, start=1):
        stops = route["stops"]
        cum_dist = 0.0
        
        for s_idx, stop in enumerate(stops, start=1):
            if s_idx == 1:
                seg_dist = 0.0
            else:
                prev_stop = stops[s_idx - 2]
                seg_dist = calculate_haversine_distance(
                    prev_stop["lat"], prev_stop["lon"],
                    stop["lat"], stop["lon"]
                )
            cum_dist = round(cum_dist + seg_dist, 2)
            
            route_rows.append({
                "route_id": route["route_id"],
                "route_number": route["route_number"],
                "route_name": route["route_name"],
                "origin_name": route["origin_name"],
                "destination_name": route["destination_name"],
                "scheduled_morning_departure": route["departure_time"],
                "stop_id": stop["stop_id"],
                "stop_name": stop["name"],
                "stop_sequence": s_idx,
                "latitude": stop["lat"],
                "longitude": stop["lon"],
                "segment_distance_km": seg_dist,
                "distance_from_origin_km": cum_dist,
                "scheduled_offset_minutes": stop["offset"],
                "is_major_junction": stop["major"],
                "landmark": stop["landmark"],
                "is_synthetic": False # The route geometry & published stops are authentic SECE transport records
            })
            
    df_routes = pd.DataFrame(route_rows)
    
    # Calculate total route distances and remaining distances
    route_totals = df_routes.groupby("route_id")["distance_from_origin_km"].max().to_dict()
    df_routes["total_route_distance_km"] = df_routes["route_id"].map(route_totals)
    df_routes["remaining_distance_km"] = (
        df_routes["total_route_distance_km"] - df_routes["distance_from_origin_km"]
    ).round(2)
    
    output_path = DATASETS_DIR / "college_routes.csv"
    df_routes.to_csv(output_path, index=False)
    print(f"[OK] Generated {output_path} with {len(df_routes)} stops across {len(SECE_ROUTES)} routes.")
    return df_routes

# ---------------------------------------------------------------------------
# 2. Simulated Trip History Generation (Documented Travel Dynamics)
# ---------------------------------------------------------------------------
def simulate_traffic_level(hour, minute, is_major_junction, day_of_week, rain_mm):
    """
    Realistic Coimbatore traffic state generator:
    Peak hours (07:30 - 08:45 AM, 16:30 - 17:45 PM),
    Urban bottlenecks (Ukkadam, Gandhipuram, Singanallur, Eachanari),
    Monsoon rains and day-of-week volume.
    """
    score = 0.0
    time_float = hour + minute / 60.0
    
    # Peak hour weight
    if 7.5 <= time_float <= 8.75:
        score += 2.2 # Morning college rush
    elif 16.5 <= time_float <= 17.75:
        score += 1.8 # Evening rush
    elif 8.75 < time_float <= 9.5:
        score += 1.2
    else:
        score += 0.5
        
    # Urban bottleneck weight
    if is_major_junction:
        score += 1.8
        
    # Weekday vs Saturday
    if day_of_week == "Monday":
        score += 0.6
    elif day_of_week == "Saturday":
        score -= 0.8
        
    # Rain impact
    if rain_mm > 10.0:
        score += 2.0
    elif rain_mm > 2.0:
        score += 1.0
        
    # Stochastic traffic fluctuations
    score += random.gauss(0, 0.4)
    
    if score >= 4.5:
        return "SEVERE"
    elif score >= 3.2:
        return "HIGH"
    elif score >= 1.8:
        return "MEDIUM"
    else:
        return "LOW"

def get_coimbatore_weather(trip_date):
    """
    Simulates seasonal Coimbatore meteorological conditions:
    Summer (March-May): 32-38°C, Dry
    Southwest Monsoon (June-August): 24-29°C, Moderate Rain
    Northeast Monsoon (October-November): 22-27°C, Heavy Rain spells
    Winter (December-February): 20-30°C, Pleasant
    """
    month = trip_date.month
    
    # Base temperatures
    if month in [3, 4, 5]:
        base_temp = random.uniform(30.0, 37.0)
        base_humidity = random.uniform(45.0, 65.0)
        rain_prob = 0.12
    elif month in [6, 7, 8]:
        base_temp = random.uniform(25.0, 30.0)
        base_humidity = random.uniform(70.0, 88.0)
        rain_prob = 0.35
    elif month in [9, 10, 11]:
        base_temp = random.uniform(23.0, 28.0)
        base_humidity = random.uniform(75.0, 95.0)
        rain_prob = 0.45
    else:
        base_temp = random.uniform(21.0, 29.0)
        base_humidity = random.uniform(50.0, 72.0)
        rain_prob = 0.08
        
    # Determine rain
    if random.random() < rain_prob:
        rainfall = round(float(np.random.exponential(scale=6.5)), 1)
        if rainfall > 15.0:
            weather = "HEAVY_RAIN"
        elif rainfall > 4.0:
            weather = "MODERATE_RAIN"
        else:
            weather = "LIGHT_RAIN"
    else:
        rainfall = 0.0
        weather = "CLOUDY" if random.random() < 0.35 else "CLEAR"
        
    return {
        "weather_condition": weather,
        "temperature": round(base_temp, 1),
        "rainfall": rainfall,
        "humidity": round(base_humidity, 1)
    }

def generate_trip_history_dataset(df_routes, num_trips=850):
    """
    Generates bus_trip_history.csv with 5,000 to 10,000 simulated trip-segment records.
    Explicitly labels every record as `is_synthetic = True`.
    """
    trip_records = []
    
    # Generate trips chronologically over 120 college calendar days
    start_date = date(2026, 6, 1) # Academic semester start
    active_buses = {
        "R01_BHARATHIAR": "TN-38-BZ-4501",
        "R02_KOTTAMPATTI_POLLACHI": "TN-38-BZ-4502",
        "R03_SARAVANAMPATTI": "TN-38-BZ-4503",
        "R04_KOVAIPUDUR": "TN-38-BZ-4504",
        "R05_VADAKKIPALAYAM": "TN-38-BZ-4505",
        "R06_SULUR": "TN-38-BZ-4506",
        "R07_POLLACHI_CENTRAL": "TN-38-BZ-4507",
        "R08_PERIYANAICKENPALAYAM": "TN-38-BZ-4508",
        "R09_PALLADAM": "TN-38-BZ-4509",
        "R10_UDUMALPET": "TN-38-BZ-4510"
    }
    
    routes_list = df_routes["route_id"].unique().tolist()
    calendar_days = []
    curr_date = start_date
    
    # Collect valid college days (Monday through Saturday, skip Sundays)
    while len(calendar_days) < 90:
        if curr_date.weekday() != 6: # 6 is Sunday
            calendar_days.append(curr_date)
        curr_date += timedelta(days=1)
        
    trip_counter = 1000
    
    for c_date in calendar_days:
        day_of_week = c_date.strftime("%A")
        weather = get_coimbatore_weather(c_date)
        
        # Each day, simulate operational college bus trips
        for route_id in routes_list:
            route_stops = df_routes[df_routes["route_id"] == route_id].sort_values("stop_sequence")
            num_stops = len(route_stops)
            bus_id = active_buses[route_id]
            trip_counter += 1
            trip_id = f"TRIP_{c_date.strftime('%Y%m%d')}_{route_id}_{trip_counter}"
            
            # Scheduled route departure
            base_dep_str = route_stops.iloc[0]["scheduled_morning_departure"]
            dep_hour, dep_min, _ = map(int, base_dep_str.split(":"))
            scheduled_origin_dt = datetime.combine(c_date, time(dep_hour, dep_min))
            
            # Initial origin departure delay (buses usually depart on time or 0-3 mins delay)
            initial_delay = max(0.0, round(random.gauss(0.8, 1.2), 1))
            actual_origin_dt = scheduled_origin_dt + timedelta(minutes=initial_delay)
            
            # State tracking across stops along this specific trip
            current_delay = initial_delay
            previous_stop_delay = 0.0
            total_route_km = route_stops["total_route_distance_km"].iloc[0]
            
            # Calculate actual trip segment timelines
            actual_arrival_times = []
            scheduled_arrival_times = []
            
            for idx, (_, stop) in enumerate(route_stops.iterrows()):
                seq = stop["stop_sequence"]
                sched_offset = stop["scheduled_offset_minutes"]
                sched_arrival_dt = scheduled_origin_dt + timedelta(minutes=sched_offset)
                scheduled_arrival_times.append(sched_arrival_dt)
                
                if seq == 1:
                    # Origin stop
                    act_arrival_dt = scheduled_origin_dt
                    actual_arrival_times.append(act_arrival_dt)
                    current_delay = 0.0
                else:
                    seg_km = stop["segment_distance_km"]
                    is_major = stop["is_major_junction"]
                    
                    # Localized traffic simulation
                    curr_time = sched_arrival_dt + timedelta(minutes=current_delay)
                    traffic_level = simulate_traffic_level(
                        curr_time.hour, curr_time.minute, is_major, day_of_week, weather["rainfall"]
                    )
                    
                    # Effective speed based on traffic
                    if traffic_level == "SEVERE":
                        speed_kmh = random.uniform(12.0, 18.0)
                        junction_penalty = random.uniform(4.0, 9.0) if is_major else random.uniform(1.0, 3.0)
                    elif traffic_level == "HIGH":
                        speed_kmh = random.uniform(18.0, 25.0)
                        junction_penalty = random.uniform(2.5, 5.0) if is_major else random.uniform(0.5, 1.5)
                    elif traffic_level == "MEDIUM":
                        speed_kmh = random.uniform(26.0, 35.0)
                        junction_penalty = random.uniform(1.0, 2.5) if is_major else 0.0
                    else: # LOW
                        speed_kmh = random.uniform(36.0, 48.0)
                        junction_penalty = 0.0
                        
                    # Rain friction penalty
                    if weather["rainfall"] > 10.0:
                        speed_kmh *= 0.78
                    elif weather["rainfall"] > 0.0:
                        speed_kmh *= 0.90
                        
                    # Calculate segment travel time
                    seg_travel_mins = (seg_km / speed_kmh) * 60.0 + junction_penalty
                    
                    # Scheduled duration for this segment
                    prev_offset = route_stops.iloc[idx - 1]["scheduled_offset_minutes"]
                    sched_seg_mins = sched_offset - prev_offset
                    
                    # Delay delta on this segment
                    delay_delta = seg_travel_mins - sched_seg_mins
                    
                    # Upstream delay propagation (buses absorb ~85% of previous delay)
                    current_delay = max(-2.0, round(current_delay * 0.88 + delay_delta, 1))
                    
                    # Slight chance of a breakdown or unexpected roadblock
                    if random.random() < 0.008:
                        incident_delay = random.uniform(8.0, 20.0)
                        current_delay += incident_delay
                        traffic_level = "SEVERE"
                        
                    act_arrival_dt = sched_arrival_dt + timedelta(minutes=current_delay)
                    actual_arrival_times.append(act_arrival_dt)
                    
            # Compute total actual trip duration and remaining travel times
            trip_total_actual_mins = (actual_arrival_times[-1] - actual_arrival_times[0]).total_seconds() / 60.0
            
            # Now build the segment records for this trip
            for idx, (_, stop) in enumerate(route_stops.iterrows()):
                seq = stop["stop_sequence"]
                sched_arr = scheduled_arrival_times[idx]
                act_arr = actual_arrival_times[idx]
                stop_delay = round((act_arr - sched_arr).total_seconds() / 60.0, 1)
                
                # Actual remaining travel time from this stop to SECE campus
                remaining_actual_mins = max(
                    0.0,
                    round((actual_arrival_times[-1] - act_arr).total_seconds() / 60.0, 1)
                )
                
                remaining_stops = num_stops - seq
                remaining_dist_km = stop["remaining_distance_km"]
                seg_km = stop["segment_distance_km"]
                
                # Traffic at this stop
                is_major = stop["is_major_junction"]
                traffic_at_stop = simulate_traffic_level(
                    act_arr.hour, act_arr.minute, is_major, day_of_week, weather["rainfall"]
                )
                
                # Actual departure from stop (dwell time: 30 to 90 seconds)
                dwell_sec = random.randint(30, 90) if seq < num_stops else 0
                act_dep = act_arr + timedelta(seconds=dwell_sec)
                sched_dep = sched_arr + timedelta(seconds=30)
                
                trip_records.append({
                    "trip_id": trip_id,
                    "bus_id": bus_id,
                    "route_id": route_id,
                    "stop_id": stop["stop_id"],
                    "stop_name": stop["stop_name"],
                    "stop_sequence": seq,
                    "trip_date": c_date.isoformat(),
                    "day_of_week": day_of_week,
                    "scheduled_departure_time": sched_dep.strftime("%H:%M:%S"),
                    "actual_departure_time": act_dep.strftime("%H:%M:%S"),
                    "scheduled_arrival_time": sched_arr.strftime("%H:%M:%S"),
                    "actual_arrival_time": act_arr.strftime("%H:%M:%S"),
                    "segment_distance_km": seg_km,
                    "remaining_distance_km": remaining_dist_km,
                    "number_of_remaining_stops": remaining_stops,
                    "traffic_level": traffic_at_stop,
                    "weather_condition": weather["weather_condition"],
                    "temperature": weather["temperature"],
                    "rainfall": weather["rainfall"],
                    "humidity": weather["humidity"],
                    "previous_trip_delay": previous_stop_delay,
                    "actual_delay_minutes": stop_delay,
                    "actual_remaining_travel_minutes": remaining_actual_mins,
                    "is_synthetic": True # Transparent simulated record tag
                })
                
                previous_stop_delay = stop_delay
                
    df_trips = pd.DataFrame(trip_records)
    output_path = DATASETS_DIR / "bus_trip_history.csv"
    df_trips.to_csv(output_path, index=False)
    print(f"[OK] Generated {output_path} with {len(df_trips)} trip-segment records.")
    return df_trips

if __name__ == "__main__":
    print("=== BusFlow Data Generation for SECE Coimbatore ===")
    routes_df = generate_college_routes_dataset()
    trips_df = generate_trip_history_dataset(routes_df)
    print(f"Total Routes Generated: {len(routes_df['route_id'].unique())}")
    print(f"Total Stops Generated: {len(routes_df)}")
    print(f"Total Trip Segments Generated: {len(trips_df)}")
    print("Completed successfully.")
