import os
from pathlib import Path
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

# Base Directory paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BACKEND_DIR / ".env")

# Resolve DB URL
raw_db_url = os.getenv("DATABASE_URL", "")
if not raw_db_url or raw_db_url.startswith("sqlite:///."):
    # Anchor SQLite DB reliably to BACKEND_DIR/busflow.db
    resolved_db_url = f"sqlite:///{BACKEND_DIR / 'busflow.db'}"
else:
    resolved_db_url = raw_db_url

class Settings(BaseModel):
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "BusFlow – SECE Bus Arrival Delay Prediction")
    VERSION: str = "1.0.0"
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sece_busflow_super_secret_jwt_key_2026_coimbatore")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "525600"))
    PORT: int = int(os.getenv("PORT", "8001"))
    
    # Database
    DATABASE_URL: str = resolved_db_url
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Institution Info (Sri Eshwar College of Engineering)
    INSTITUTION_NAME: str = os.getenv("INSTITUTION_NAME", "Sri Eshwar College of Engineering")
    INSTITUTION_LOCATION: str = os.getenv(
        "INSTITUTION_LOCATION", 
        "Kondampatti Post, Vadasithur, Kinathukadavu, Coimbatore - 641 202"
    )
    SECE_LATITUDE: float = float(os.getenv("SECE_LATITUDE", "10.8284"))
    SECE_LONGITUDE: float = float(os.getenv("SECE_LONGITUDE", "77.0146"))
    
    # Weather API (Open-Meteo)
    OPEN_METEO_BASE_URL: str = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")

    # Directories
    DATASETS_DIR: Path = BACKEND_DIR / "datasets"
    TRAINED_MODELS_DIR: Path = BACKEND_DIR / "trained_models"

# Instantiate singleton
settings = Settings()
