"""
Configuración de Django para Producción en Hostinger
"""

from .settings import *
import os

# SEGURIDAD
DEBUG = False

# Dominios permitidos
ALLOWED_HOSTS = [
    "recibo.compraenusaec.com",
    "www.recibo.compraenusaec.com",
]

# Clave secreta - CAMBIAR EN PRODUCCIÓN
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-insecure-CAMBIAR-ESTA-CLAVE-POR-UNA-SEGURA-Y-UNICA"
)

# Base de datos
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/home/u276243840/domains/compraenusaec.com/public_html/recibo/Aplicaciones.db",
    }
}

# Archivos estáticos
STATIC_URL = "/static/"
STATIC_ROOT = (
    "/home/u276243840/domains/compraenusaec.com/public_html/recibo/staticfiles/"
)

# Archivos media (uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = "/home/u276243840/domains/compraenusaec.com/public_html/recibo/media/"

# Agregar WhiteNoise para servir archivos estáticos
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Configuración de WhiteNoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Seguridad HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Configuración de cookies
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# Logging para debugging en producción
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "/home/u276243840/domains/compraenusaec.com/public_html/recibo/django_errors.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

# Configuración de correo (opcional - para notificaciones de error)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.hostinger.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'tu-email@compraenusaec.com'
# EMAIL_HOST_PASSWORD = 'tu-password'
# DEFAULT_FROM_EMAIL = 'tu-email@compraenusaec.com'
# ADMINS = [('Admin', 'admin@compraenusaec.com')]
