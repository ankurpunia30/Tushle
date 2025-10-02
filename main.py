"""
Vercel deployment entry point for Tushle AI Backend
"""
from backend.app.main import app

# Vercel expects the app to be available at module level
handler = app
