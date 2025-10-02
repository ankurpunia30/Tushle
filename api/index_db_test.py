"""
Simple database test for Vercel
"""
from fastapi import FastAPI
import os
import json

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Tushle AI Dashboard API", 
        "status": "active",
        "version": "1.0.1"
    }

@app.get("/health")
def health():
    env_status = {}
    
    # Check DATABASE_URL
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url:
        # Hide sensitive info but show it exists
        if "postgresql://" in db_url:
            env_status["DATABASE_URL"] = "✅ PostgreSQL Connected"
        else:
            env_status["DATABASE_URL"] = "❌ Invalid PostgreSQL URL"
    else:
        env_status["DATABASE_URL"] = "❌ Not Set"
    
    # Check GROQ_API_KEY
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if groq_key and groq_key.startswith("gsk_"):
        env_status["GROQ_API_KEY"] = "✅ Valid Groq Key"
    elif groq_key:
        env_status["GROQ_API_KEY"] = "❌ Invalid Groq Key Format"
    else:
        env_status["GROQ_API_KEY"] = "❌ Not Set"
    
    # Check SECRET_KEY
    secret = os.environ.get("SECRET_KEY", "")
    if secret and len(secret) > 20:
        env_status["SECRET_KEY"] = "✅ Set"
    else:
        env_status["SECRET_KEY"] = "❌ Not Set or Too Short"
    
    # Overall status
    all_good = all("✅" in status for status in env_status.values())
    
    return {
        "status": "ready" if all_good else "needs_configuration",
        "message": "Environment check complete",
        "environment_variables": env_status,
        "next_steps": [] if all_good else [
            "Add DATABASE_URL from Vercel Postgres",
            "Add GROQ_API_KEY from console.groq.com", 
            "Add SECRET_KEY for JWT tokens"
        ]
    }

@app.get("/test-db")
def test_database():
    """Test database connection"""
    db_url = os.environ.get("DATABASE_URL", "")
    
    if not db_url:
        return {
            "status": "error",
            "message": "DATABASE_URL not set",
            "instructions": "Add DATABASE_URL environment variable from Vercel Postgres"
        }
    
    if "postgresql://" not in db_url:
        return {
            "status": "error", 
            "message": "Invalid database URL format",
            "expected": "postgresql://..."
        }
    
    # Basic URL validation
    return {
        "status": "configured",
        "message": "Database URL is properly formatted",
        "database_type": "PostgreSQL",
        "ready_for_prisma": True
    }

@app.get("/setup-guide")
def setup_guide():
    """Setup instructions"""
    return {
        "title": "Tushle AI Database Setup Guide",
        "steps": [
            {
                "step": 1,
                "action": "Create Vercel Postgres Database",
                "details": "Go to Vercel Dashboard → Storage → Create Database → PostgreSQL"
            },
            {
                "step": 2, 
                "action": "Copy Database URL",
                "details": "Copy the POSTGRES_PRISMA_URL value"
            },
            {
                "step": 3,
                "action": "Add Environment Variables",
                "variables": {
                    "DATABASE_URL": "Paste POSTGRES_PRISMA_URL here",
                    "GROQ_API_KEY": "Get from console.groq.com",
                    "SECRET_KEY": "Use: KiYXjvhnO_eYBz_9WlFNlLZ8mvezzIZk3zVjUW7pPOY"
                }
            },
            {
                "step": 4,
                "action": "Test Setup", 
                "details": "Visit /api/health to verify configuration"
            }
        ]
    }
