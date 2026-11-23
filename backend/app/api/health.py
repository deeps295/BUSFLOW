from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect

from app.core.config import settings
from app.database.session import get_db, engine

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint confirming API status, DB connectivity, tables, and SECE config."""
    db_status = "unhealthy"
    tables_count = 0
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        tables_count = len(tables)
    except Exception as e:
        db_status = f"error: {str(e)}"
        
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_status,
        "tables_count": tables_count,
        "institution": {
            "name": settings.INSTITUTION_NAME,
            "location": settings.INSTITUTION_LOCATION,
            "coordinates": {
                "latitude": settings.SECE_LATITUDE,
                "longitude": settings.SECE_LONGITUDE
            }
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
