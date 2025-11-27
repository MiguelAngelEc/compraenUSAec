"""
Configuración de Django para Producción en Render
CompraEnUSAec - Sistema de Recibos
"""

from .settings import *
import os
import dj_database_url

# ===========================================
# SEGURIDAD
# ===========================================
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Clave secreta desde variable de entorno
SECRET_KEY = os.environ.get("SECRET_KEY")

# Dominios permitidos
ALLOWED_HOSTS = []

# Obtener el hostname de Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Agregar hosts adicionales si se especifican
EXTRA_HOSTS = os.environ.get("ALLOWED_HOSTS", "")
if EXTRA_HOSTS:
    ALLOWED_HOSTS.extend(EXTRA_HOSTS.split(","))

# ===========================================
# BASE DE DATOS - PostgreSQL en Render
# ===========================================
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback a SQLite para desarrollo local
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "Aplicaciones.db",
        }
    }

# ===========================================
# ARCHIVOS ESTÁTICOS
# ===========================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise para servir archivos estáticos
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ===========================================
# ARCHIVOS MEDIA
# ===========================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ===========================================
# SEGURIDAD HTTPS (Render usa HTTPS por defecto)
# ===========================================
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Configuración de cookies
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# ===========================================
# CSRF TRUSTED ORIGINS
# ===========================================
CSRF_TRUSTED_ORIGINS = []
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# ===========================================
# LOGGING
# ===========================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}
