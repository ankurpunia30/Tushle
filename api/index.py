"""
Vercel API handler for Tushle AI Backend - Simple and Robust
"""
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create FastAPI app
app = FastAPI(title="Tushle AI Dashboard API", version="1.0.0")

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "Tushle AI Dashboard API", 
        "status": "active", 
        "version": "1.0.0",
        "platform": "vercel",
        "database": "prisma + postgresql"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Check environment variables
        env_vars = {
            "DATABASE_URL": bool(os.getenv("DATABASE_URL")),
            "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
            "SECRET_KEY": bool(os.getenv("SECRET_KEY"))
        }
        
        configured_count = sum(env_vars.values())
        total_vars = len(env_vars)
        
        return {
            "status": "healthy",
            "message": "API is running successfully",
            "database": "prisma",
            "environment_variables": {
                "configured": f"{configured_count}/{total_vars}",
                "DATABASE_URL": "✅ Set" if env_vars["DATABASE_URL"] else "❌ Missing",
                "GROQ_API_KEY": "✅ Set" if env_vars["GROQ_API_KEY"] else "❌ Missing",
                "SECRET_KEY": "✅ Set" if env_vars["SECRET_KEY"] else "❌ Missing"
            },
            "ready": configured_count == total_vars
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Health check failed: {str(e)}"
            }
        )

@app.get("/api/health")
async def api_health():
    """Alternative health endpoint for /api/health"""
    return await health()

@app.get("/features")
async def get_features():
    """List available features"""
    return {
        "features": [
            {
                "name": "15-Source Content Intelligence",
                "sources": ["Reddit", "TikTok", "Pinterest", "Instagram", "Medium", "GitHub", "ProductHunt"],
                "status": "available"
            },
            {
                "name": "AI-Powered PDF Reports",
                "description": "LLM-generated insights and recommendations",
                "status": "available"
            },
            {
                "name": "Field-Specific Trending",
                "categories": ["Fashion", "Technology", "Marketing"],
                "status": "available"
            },
            {
                "name": "Prisma Database",
                "type": "PostgreSQL",
                "status": "configured" if os.getenv("DATABASE_URL") else "needs_setup"
            }
        ]
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all uncaught exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "status": "error"
        }
    )

# Export for Vercel (this is the key part)
handler = app
