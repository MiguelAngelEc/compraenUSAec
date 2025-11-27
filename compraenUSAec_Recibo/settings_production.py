from .settings import *
import os

# ======================
# SEGURIDAD
# ======================
DEBUG = False

# Dominios permitidos (agrega tu dominio real y subdominios si los hay)
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "recibo-compraenusaec.onrender.com",
    "compraenusaec.com",
    "www.compraenusaec.com",
]

# Agregar hosts adicionales desde variable de entorno
EXTRA_HOSTS = os.environ.get("ALLOWED_HOSTS", "")
if EXTRA_HOSTS:
    ALLOWED_HOSTS.extend([h.strip() for h in EXTRA_HOSTS.split(",") if h.strip()])

# Clave secreta segura desde variable de entorno
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("La variable de entorno DJANGO_SECRET_KEY no está configurada!")

# ======================
# BASE DE DATOS
# ======================
# Para Hostinger con PostgreSQL, configurar DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback a SQLite solo si no hay DATABASE_URL
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ======================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ======================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# WhiteNoise para servir archivos estáticos
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ======================
# SEGURIDAD HTTPS
# ======================
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # CRÍTICO para proxies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# ======================
# CSRF TRUSTED ORIGINS (Requerido para Django 4.0+)
# ======================
CSRF_TRUSTED_ORIGINS = [
    "https://recibo-compraenusaec.onrender.com",
    "https://compraenusaec.com",
    "https://www.compraenusaec.com",
]

# ======================
# LOGGING (Console para compatibilidad con PaaS)
# ======================
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

# ======================
# CONFIGURACIÓN ADICIONAL
# ======================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
