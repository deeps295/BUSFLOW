from app.database.session import Base, engine
import app.models  # Ensure all models are registered on Base.metadata

def init_db():
    """Create all SQLite database tables for BusFlow."""
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")

if __name__ == "__main__":
    init_db()
