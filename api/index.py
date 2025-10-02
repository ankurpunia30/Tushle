"""
Vercel API handler for Tushle AI Backend
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set environment for Vercel
os.environ["VERCEL_DEPLOYMENT"] = "true"

try:
    from app.main import app
    # Initialize database on cold start
    from app.db.database import engine
    from app.models import Base
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Error initializing app: {e}")
    # Create a minimal app for error handling
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return {"status": "error", "message": str(e)}

# Vercel handler
def handler(request, response):
    return app(request, response)
