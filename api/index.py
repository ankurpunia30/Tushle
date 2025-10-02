"""
Main API endpoints for Tushle AI Dashboard
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Set response headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = {}
        
        # Route handling
        if path == '/api/dashboard':
            response_data = {
                'status': 'success',
                'data': {
                    'total_clients': 25,
                    'active_tasks': 12,
                    'revenue_this_month': 15750,
                    'pending_invoices': 3,
                    'recent_activities': [
                        {'type': 'task_completed', 'description': 'Social media posts generated for Client A', 'timestamp': '2025-10-02T10:30:00Z'},
                        {'type': 'invoice_sent', 'description': 'Invoice #INV-001 sent to Client B', 'timestamp': '2025-10-02T09:15:00Z'},
                        {'type': 'lead_created', 'description': 'New lead from contact form', 'timestamp': '2025-10-02T08:45:00Z'}
                    ]
                }
            }
        elif path == '/api/clients':
            response_data = {
                'status': 'success',
                'data': [
                    {'id': 1, 'name': 'TechCorp Inc', 'email': 'contact@techcorp.com', 'status': 'active', 'monthly_value': 2500},
                    {'id': 2, 'name': 'StartupXYZ', 'email': 'hello@startupxyz.com', 'status': 'active', 'monthly_value': 1800},
                    {'id': 3, 'name': 'RetailChain', 'email': 'marketing@retailchain.com', 'status': 'pending', 'monthly_value': 3200}
                ]
            }
        elif path == '/api/tasks':
            response_data = {
                'status': 'success',
                'data': [
                    {'id': 1, 'title': 'Generate social media content', 'client': 'TechCorp Inc', 'status': 'in_progress', 'due_date': '2025-10-05'},
                    {'id': 2, 'title': 'Create email campaign', 'client': 'StartupXYZ', 'status': 'pending', 'due_date': '2025-10-03'},
                    {'id': 3, 'title': 'Design landing page', 'client': 'RetailChain', 'status': 'completed', 'due_date': '2025-10-01'}
                ]
            }
        elif path == '/api/finance':
            response_data = {
                'status': 'success',
                'data': {
                    'total_revenue': 45250,
                    'monthly_recurring': 18600,
                    'outstanding_invoices': [
                        {'id': 'INV-001', 'client': 'TechCorp Inc', 'amount': 2500, 'due_date': '2025-10-15'},
                        {'id': 'INV-002', 'client': 'StartupXYZ', 'amount': 1800, 'due_date': '2025-10-10'}
                    ]
                }
            }
        elif path == '/api/ai/generate':
            response_data = {
                'status': 'success',
                'message': 'AI generation endpoint ready',
                'note': 'POST request required with prompt data'
            }
        else:
            response_data = {
                'status': 'success',
                'message': 'Tushle AI Dashboard API',
                'version': '1.0.0',
                'endpoints': [
                    '/api/dashboard - Dashboard overview',
                    '/api/clients - Client management',
                    '/api/tasks - Task management', 
                    '/api/finance - Financial data',
                    '/api/ai/generate - AI content generation',
                    '/api/health - Health check'
                ],
                'environment': {
                    'DATABASE_URL': 'configured' if os.environ.get('DATABASE_URL') else 'missing',
                    'GROQ_API_KEY': 'configured' if os.environ.get('GROQ_API_KEY') else 'missing',
                    'SECRET_KEY': 'configured' if os.environ.get('SECRET_KEY') else 'missing'
                }
            }
        
        # Send JSON response
        self.wfile.write(json.dumps(response_data, indent=2).encode('utf-8'))
        
    def do_POST(self):
        # Get content length
        content_length = int(self.headers.get('Content-Length', 0))
        
        # Read the request body
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                request_data = json.loads(post_data.decode('utf-8'))
            except:
                request_data = {}
        else:
            request_data = {}
            
        # Set response headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Parse the URL path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        response_data = {}
        
        if path == '/api/ai/generate':
            prompt = request_data.get('prompt', 'Default content prompt')
            content_type = request_data.get('type', 'social_media')
            
            response_data = {
                'status': 'success',
                'generated_content': f"AI-generated {content_type} content based on: {prompt}",
                'metadata': {
                    'type': content_type,
                    'word_count': len(prompt.split()) * 10,  # Simulated
                    'generated_at': __import__('datetime').datetime.now().isoformat()
                }
            }
        else:
            response_data = {
                'status': 'error',
                'message': 'Endpoint not found or method not supported'
            }
        
        # Send JSON response
        self.wfile.write(json.dumps(response_data, indent=2).encode('utf-8'))
        
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
