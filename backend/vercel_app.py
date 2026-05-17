import os
import sys
from io import BytesIO

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

def handler(event, context):
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {}) or {}
    body = event.get('body', '') or ''
    query_string = event.get('queryStringParameters') or {}

    static_extensions = ('.js', '.css', '.manifest', '.webmanifest')
    if path.endswith(static_extensions) or path.startswith('/static/'):
        frontend_dir = os.path.join(project_root, 'frontend')
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
                'body': content.decode('utf-8')
            }

    wsgi_input = BytesIO(body.encode('utf-8') if body else b'')

    environ = {
        'REQUEST_METHOD': http_method,
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join(f"{k}={v}" for k, v in query_string.items()) if query_string else '',
        'SERVER_NAME': headers.get('host', 'localhost'),
        'SERVER_PORT': headers.get('x-forwarded-port', '443'),
        'HTTP_HOST': headers.get('host', ''),
        'wsgi.input': wsgi_input,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': True,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'CONTENT_TYPE': headers.get('content-type', ''),
    }

    for key, value in headers.items():
        key_upper = key.upper().replace('-', '_')
        if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key_upper}'] = value

    if body:
        environ['CONTENT_LENGTH'] = str(len(body))

    response_status = [None]
    response_headers = [None]

    def start_response(status, headers, exc_info=None):
        response_status[0] = int(status.split()[0])
        response_headers[0] = dict(headers)
        return lambda x: None

    from django.core.handlers.wsgi import WSGIHandler
    response = WSGIHandler()(environ, start_response)

    return {
        'statusCode': response_status[0] or 200,
        'headers': response_headers[0] or {},
        'body': b''.join(response).decode('utf-8')
    }

app = handler