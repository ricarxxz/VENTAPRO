import os
import sys
from base64 import b64encode

handler_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, handler_dir)
sys.path.insert(0, os.path.join(handler_dir, 'config'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

frontend_dir = os.path.join(handler_dir, '..', 'frontend')
frontend_dir = os.path.normpath(frontend_dir)

def vercel_handler(event, context):
    path = event.get('path', '/')
    
    static_extensions = ('.js', '.css', '.manifest', '.webmanifest')
    if path.endswith(static_extensions) or path.startswith('/static/'):
        file_path = os.path.join(frontend_dir, path.lstrip('/'))
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
            
            content_types = {
                '.js': 'application/javascript',
                '.css': 'text/css',
                '.manifest': 'application/manifest+json',
                '.webmanifest': 'application/manifest+json'
            }
            ext = os.path.splitext(path)[1]
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': content_types.get(ext, 'text/plain')},
                'body': b64encode(content).decode('utf-8'),
                'isBase64Encoded': True
            }

    if path == '/' or path == '':
        index_path = os.path.join(frontend_dir, 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'rb') as f:
                content = f.read()
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': b64encode(content).decode('utf-8'),
                'isBase64Encoded': True
            }
    
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'text/plain'},
        'body': 'Not Found'
    }

application = vercel_handler