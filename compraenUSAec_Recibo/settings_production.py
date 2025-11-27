from .settings import *
import os

# ======================
# SEGURIDAD
# ======================
DEBUG = False

# Dominios permitidos (agrega tu dominio real y subdominios si los hay)
ALLOWED_HOSTS = [
    "recibo-compraenusaec.onrender.com",
    "compraenusaec.com",
    "www.compraenusaec.com",
]

# Clave secreta segura desde variable de entorno
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("La variable de entorno DJANGO_SECRET_KEY no está configurada!")

# ======================
# BASE DE DATOS
# ======================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),  # Más portable
    }
}

# ======================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ======================
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# WhiteNoise para servir archivos estáticos
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ======================
# SEGURIDAD HTTPS
# ======================
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# ======================
# LOGGING
# ======================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "django_errors.log"),
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
