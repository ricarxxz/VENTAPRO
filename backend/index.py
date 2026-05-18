import os
import sys

handler_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, handler_dir)
sys.path.insert(0, os.path.join(handler_dir, 'config'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

# Add all possible Vercel domains to ALLOWED_HOSTS
from django.conf import settings
settings.ALLOWED_HOSTS = ['*']

frontend_dir = os.path.join(handler_dir, '..', 'frontend')
frontend_dir = os.path.normpath(frontend_dir)

def app(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    
    # Serve static frontend files
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
            
            status = '200 OK'
            headers = [('Content-Type', content_types.get(ext, 'text/plain'))]
            start_response(status, headers)
            return [content]

    # Let Django handle API, auth and admin routes
    if path.startswith('/api') or path.startswith('/auth') or path.startswith('/admin'):
        from django.core.handlers.wsgi import WSGIHandler
        wsgi_app = WSGIHandler()
        return wsgi_app(environ, start_response)
    
    # Serve index.html for all other routes (SPA)
    index_path = os.path.join(frontend_dir, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'rb') as f:
            content = f.read()
        
        status = '200 OK'
        headers = [('Content-Type', 'text/html')]
        start_response(status, headers)
        return [content]
    
    status = '404 Not Found'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)
    return [b'Not Found']