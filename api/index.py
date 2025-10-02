"""
Vercel API handler for Tushle AI Backend
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set environment for Vercel
os.environ["VERCEL_DEPLOYMENT"] = "true"

# Create FastAPI app
app = FastAPI(title="Tushle AI Dashboard API")

@app.get("/")
async def root():
    return {"message": "Tushle AI Dashboard API", "status": "active"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "API is running successfully"}

@app.get("/api/health") 
async def api_health():
    return {"status": "healthy", "message": "API is running successfully"}

try:
    # Try to import and setup the full app
    from app.main import app as main_app
    from app.db.database import engine
    from app.models import Base
    
    # Copy routes from main app
    for route in main_app.routes:
        app.router.routes.append(route)
        
except Exception as e:
    print(f"Warning: Could not load full app: {e}")
    # Continue with basic endpoints

# Export for Vercel
handler = app
