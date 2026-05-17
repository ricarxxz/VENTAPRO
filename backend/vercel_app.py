import os
import sys

# Añadir el directorio raíz al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.core.handlers.wsgi import WSGIHandler

# Importar la aplicación WSGI de Django
app = WSGIHandler()