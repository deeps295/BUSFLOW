"""
Open-Meteo Weather Service for Sri Eshwar College of Engineering, Coimbatore.
Fetches real-time localized weather conditions for SECE coordinates (10.85° N, 76.98° E).
Includes:
- In-memory 15-minute caching to eliminate redundant external calls
- Graceful offline fallback to Coimbatore seasonal climatology
- Official Open-Meteo API attribution (CC BY 4.0)
"""

import time
import requests
from typing import Dict, Any, Optional

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
SECE_WEATHER_LAT = 10.85
SECE_WEATHER_LON = 76.98

# WMO Weather code mapper
WEATHER_CODE_MAP = {
    0: "CLEAR",
    1: "CLEAR",
    2: "CLOUDY",
    3: "CLOUDY",
    45: "FOG",
    48: "FOG",
    51: "LIGHT_RAIN",
    53: "LIGHT_RAIN",
    55: "MODERATE_RAIN",
    61: "LIGHT_RAIN",
    63: "MODERATE_RAIN",
    65: "HEAVY_RAIN",
    80: "LIGHT_RAIN",
    81: "MODERATE_RAIN",
    82: "HEAVY_RAIN",
    95: "HEAVY_RAIN"
}

_cached_weather: Optional[Dict[str, Any]] = None
_cache_timestamp: float = 0.0
CACHE_TTL_SECONDS = 900.0  # 15 minutes

def get_current_sece_weather(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Fetches current weather for SECE area from Open-Meteo API.
    Falls back gracefully if network is unavailable or times out.
    """
    global _cached_weather, _cache_timestamp

    now = time.time()
    if _cached_weather is not None and not force_refresh and (now - _cache_timestamp) < CACHE_TTL_SECONDS:
        return _cached_weather

    attribution_data = {
        "source": "Open-Meteo (open-meteo.com)",
        "license": "CC BY 4.0",
        "area_note": "Area-level estimate for Sri Eshwar College / Kinathukadavu grid (10.85° N, 76.98° E)"
    }

    try:
        params = {
            "latitude": SECE_WEATHER_LAT,
            "longitude": SECE_WEATHER_LON,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,rain",
            "timezone": "Asia/Kolkata"
        }
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=1.5)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current", {})
            temp = float(curr.get("temperature_2m", 28.0))
            humidity = float(curr.get("relative_humidity_2m", 65.0))
            rain_mm = float(curr.get("precipitation", 0.0))
            w_code = int(curr.get("weather_code", 0))
            condition = WEATHER_CODE_MAP.get(w_code, "CLEAR")

            weather_obj = {
                "condition": condition,
                "temperature_c": temp,
                "precipitation_mm": rain_mm,
                "humidity_percent": humidity,
                "weather_code": w_code,
                "attribution": attribution_data,
                "is_live": True,
                "timestamp": curr.get("time", time.strftime("%Y-%m-%d %H:%M:%S"))
            }
            _cached_weather = weather_obj
            _cache_timestamp = now
            return weather_obj
    except Exception as e:
        # Graceful fallback: Network unreachable, timeout, or sandboxed test
        pass

    # Fallback to realistic Coimbatore daytime climatology
    fallback_obj = {
        "condition": "CLEAR",
        "temperature_c": 28.5,
        "precipitation_mm": 0.0,
        "humidity_percent": 62.0,
        "weather_code": 0,
        "attribution": attribution_data,
        "is_live": False,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "fallback_note": "Using climatological baseline due to API timeout or offline environment"
    }
    _cached_weather = fallback_obj
    _cache_timestamp = now
    return fallback_obj
