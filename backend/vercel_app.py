import os
import sys
from urllib.parse import parse_qs

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.core.handlers.wsgi import WSGIHandler
from django.http import HttpRequest

def handler(event, context):
    http_method = event.get('httpMethod')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    query_string = event.get('queryStringParameters') or {}

    if path.startswith('/static/'):
        return {
            'statusCode': 404,
            'body': 'Static files must be served via Vercel build'
        }

    wsgi_handler = WSGIHandler()
    
    environ = {
        'REQUEST_METHOD': http_method,
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join(f"{k}={v}" for k, v in query_string.items()) if query_string else '',
        'SERVER_NAME': headers.get('host', 'localhost'),
        'SERVER_PORT': headers.get('x-forwarded-port', '443'),
        'HTTP_HOST': headers.get('host', ''),
        'wsgi.input': None,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': True,
        'wsgi.multiprocess': True,
    }

    for key, value in headers.items():
        key_upper = key.upper().replace('-', '_')
        if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key_upper}'] = value

    request = HttpRequest()
    request.method = http_method
    request.path = path
    request.META = environ
    request.GET = query_string

    response = wsgi_handler.get_response(request)

    return {
        'statusCode': response.status_code,
        'headers': {k: v for k, v in response.items()},
        'body': response.content.decode('utf-8')
    }