"""
Ultra-simple Vercel API handler for Tushle AI
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Tushle AI Dashboard API", 
        "status": "working",
        "platform": "vercel"
    }

@app.get("/health")
def health():
    import os
    return {
        "status": "healthy",
        "message": "API is working",
        "environment": {
            "DATABASE_URL": "set" if os.environ.get("DATABASE_URL") else "missing",
            "GROQ_API_KEY": "set" if os.environ.get("GROQ_API_KEY") else "missing", 
            "SECRET_KEY": "set" if os.environ.get("SECRET_KEY") else "missing"
        }
    }

@app.get("/test")
def test():
    return {"test": "working", "timestamp": "2025-10-02"}

# This is the handler Vercel will use
app
