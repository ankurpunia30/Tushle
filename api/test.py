"""
Simplest possible Vercel handler
"""

def handler(event, context):
    import json
    import os
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': 'Tushle AI API Working!',
            'status': 'success',
            'environment_check': {
                'DATABASE_URL': 'SET' if os.environ.get('DATABASE_URL') else 'MISSING',
                'GROQ_API_KEY': 'SET' if os.environ.get('GROQ_API_KEY') else 'MISSING',
                'SECRET_KEY': 'SET' if os.environ.get('SECRET_KEY') else 'MISSING'
            }
        })
    }
