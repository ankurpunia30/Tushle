"""
Health check endpoint for Vercel
"""
from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set response headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Health check response
        response_data = {
            'status': 'healthy',
            'service': 'Tushle AI API',
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'environment': {
                'DATABASE_URL': 'configured' if os.environ.get('DATABASE_URL') else 'missing',
                'GROQ_API_KEY': 'configured' if os.environ.get('GROQ_API_KEY') else 'missing',
                'SECRET_KEY': 'configured' if os.environ.get('SECRET_KEY') else 'missing'
            }
        }
        
        # Send JSON response
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
