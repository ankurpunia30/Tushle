"""
Ultra-simple working API for Tushle AI
"""
import os

# Simple function-based approach for Vercel
def handler(request, response):
    import json
    
    if request.get('path', '/').endswith('/health'):
        # Health check
        env_check = {
            "DATABASE_URL": "✅ Set" if os.environ.get("DATABASE_URL") else "❌ Missing",
            "GROQ_API_KEY": "✅ Set" if os.environ.get("GROQ_API_KEY") else "❌ Missing",
            "SECRET_KEY": "✅ Set" if os.environ.get("SECRET_KEY") else "❌ Missing"
        }
        
        response_data = {
            "status": "healthy",
            "message": "Tushle AI API is working!",
            "environment": env_check,
            "timestamp": "2025-10-02"
        }
    else:
        # Default response
        response_data = {
            "message": "Tushle AI Dashboard API",
            "status": "active",
            "version": "1.0.2",
            "endpoints": ["/", "/health"]
        }
    
    response['statusCode'] = 200
    response['headers'] = {'Content-Type': 'application/json'}
    response['body'] = json.dumps(response_data)
    
    return response

# Also export for FastAPI compatibility
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Tushle AI Dashboard API",
        "status": "active", 
        "version": "1.0.2"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "API is working!",
        "environment": {
            "DATABASE_URL": "✅ Set" if os.environ.get("DATABASE_URL") else "❌ Missing",
            "GROQ_API_KEY": "✅ Set" if os.environ.get("GROQ_API_KEY") else "❌ Missing", 
            "SECRET_KEY": "✅ Set" if os.environ.get("SECRET_KEY") else "❌ Missing"
        }
    }
