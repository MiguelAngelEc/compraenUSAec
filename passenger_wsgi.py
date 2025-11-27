"""
WSGI config for compraenUSAec_Recibo project for Render deployment.
"""

import os
from django.core.wsgi import get_wsgi_application

# Configura el módulo de settings de producción
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "compraenUSAec_Recibo.settings_production"
)

# Crea la aplicación WSGI
application = get_wsgi_application()
