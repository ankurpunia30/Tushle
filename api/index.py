"""
Vercel API handler for Tushle AI Backend with Prisma
"""
import os
import sys
import asyncio
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
    return {"message": "Tushle AI Dashboard API", "status": "active", "database": "prisma"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "API with Prisma is running successfully"}

@app.get("/api/health") 
async def api_health():
    try:
        # Test database connection
        from app.db.prisma_service import db_service
        await db_service.connect()
        return {
            "status": "healthy", 
            "message": "API and Prisma database connected successfully",
            "database": "prisma"
        }
    except Exception as e:
        return {
            "status": "warning",
            "message": f"API running but database issue: {str(e)}",
            "database": "prisma"
        }

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    try:
        from app.db.prisma_service import init_database
        await init_database()
    except Exception as e:
        print(f"Database initialization warning: {e}")

@app.on_event("shutdown") 
async def shutdown():
    """Cleanup on shutdown"""
    try:
        from app.db.prisma_service import close_database
        await close_database()
    except Exception as e:
        print(f"Database cleanup warning: {e}")

try:
    # Try to import and setup the full app routes
    from app.main import app as main_app
    
    # Copy routes from main app
    for route in main_app.routes:
        if route.path not in ["/", "/health", "/api/health"]:
            app.router.routes.append(route)
        
except Exception as e:
    print(f"Warning: Could not load full app routes: {e}")

# Export for Vercel
handler = app
