"""
Passenger WSGI Configuration for Hostinger
CompraEnUSAec - Sistema de Recibos
"""

import os
import sys

# ===========================================
# CONFIGURACIÓN DE RUTAS
# ===========================================

# Ruta al directorio del proyecto
PROJECT_DIR = "/home/u276243840/domains/compraenusaec.com/public_html/recibo"

# Ruta al entorno virtual
VENV_DIR = "/home/u276243840/virtualenv/recibo/3.11"

# Agregar el proyecto al path de Python
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Agregar el entorno virtual al path
VENV_SITE_PACKAGES = os.path.join(VENV_DIR, "lib", "python3.11", "site-packages")
if VENV_SITE_PACKAGES not in sys.path:
    sys.path.insert(0, VENV_SITE_PACKAGES)

# ===========================================
# CONFIGURACIÓN DE DJANGO
# ===========================================

# Configurar el módulo de settings para producción
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "compraenUSAec_Recibo.settings_production"
)

# ===========================================
# APLICACIÓN WSGI
# ===========================================

from django.core.wsgi import get_wsgi_application

# Crear la aplicación WSGI
application = get_wsgi_application()

# ===========================================
# NOTA: Si usas Passenger en Hostinger
# ===========================================
# Hostinger usa Passenger para aplicaciones Python.
# Este archivo debe estar en la raíz del proyecto.
#
# Si tienes problemas, verifica:
# 1. Las rutas PROJECT_DIR y VENV_DIR sean correctas
# 2. La versión de Python en VENV_DIR coincida con la instalada
# 3. El módulo de settings esté correctamente configurado
