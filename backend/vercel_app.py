import os
import sys
from io import BytesIO

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.core.handlers.wsgi import WSGIHandler

def handler(event, context):
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {}) or {}
    body = event.get('body', '') or ''
    query_string = event.get('queryStringParameters') or {}

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
    }

    for key, value in headers.items():
        key_upper = key.upper().replace('-', '_')
        if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key_upper}'] = value

    if body:
        environ['CONTENT_LENGTH'] = str(len(body))

    response = WSGIHandler()(environ, start_response)

    return {
        'statusCode': response.status_code if hasattr(response, 'status_code') else 200,
        'headers': {k: v for k, v in response.items()},
        'body': b''.join(response).decode('utf-8')
    }

app = handler