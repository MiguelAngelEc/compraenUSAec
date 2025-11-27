"""
WSGI config for compraenUSAec_Recibo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Usar variable de entorno para determinar el módulo de settings
# Por defecto usa settings.py (desarrollo), pero en producción
# se debe configurar DJANGO_SETTINGS_MODULE apropiadamente
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.environ.get("DJANGO_SETTINGS_MODULE", "compraenUSAec_Recibo.settings"),
)

application = get_wsgi_application()
