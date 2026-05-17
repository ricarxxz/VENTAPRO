import os
import sys

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

# Importar la aplicación WSGI de Django
from config.wsgi import application as app

# Vercel necesita que la aplicación se llame "app"
app = app