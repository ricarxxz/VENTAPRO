import os
import sys
from io import StringIO

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

# Importar la aplicación WSGI de Django
from django.core.handlers.wsgi import WSGIHandler

application = WSGIHandler()

def handler(request):
    return application(request)