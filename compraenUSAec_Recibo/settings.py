"""
Django settings for compraenUSAec_Recibo project.

Este archivo está configurado para funcionar tanto en desarrollo local
como en producción (Render, Hostinger, etc.) usando variables de entorno.

VARIABLES DE ENTORNO REQUERIDAS EN PRODUCCIÓN:
- DJANGO_SECRET_KEY: Clave secreta única y segura
- DATABASE_URL: URL de conexión a PostgreSQL (opcional, usa SQLite si no está)
- ALLOWED_HOSTS: Hosts permitidos separados por coma
- RENDER_EXTERNAL_HOSTNAME: Hostname automático de Render (opcional)

VARIABLES OPCIONALES:
- DEBUG: "True" o "False" (default: "True" en desarrollo)
- CSRF_TRUSTED_ORIGINS: Orígenes CSRF adicionales separados por coma
- DJANGO_LOG_LEVEL: Nivel de logging (default: "INFO")
"""

from pathlib import Path
import os
import sys

# =============================================================================
# CONFIGURACIÓN BASE
# =============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# DETECCIÓN DE ENTORNO
# =============================================================================

# Detectar si estamos en producción basado en variables de entorno
# Se considera producción si:
# 1. DEBUG está explícitamente en "False"
# 2. Existe RENDER_EXTERNAL_HOSTNAME (Render)
# 3. Existe DATABASE_URL (típico de PaaS)
IS_PRODUCTION = (
    os.environ.get("DEBUG", "True").lower() == "false"
    or os.environ.get("RENDER_EXTERNAL_HOSTNAME") is not None
    or os.environ.get("DATABASE_URL") is not None
)

# =============================================================================
# SEGURIDAD - SECRET_KEY
# =============================================================================

# CRÍTICO: En producción, SIEMPRE usar variable de entorno
# La clave por defecto SOLO debe usarse en desarrollo local
_DEFAULT_SECRET_KEY = "$_-01fz%$4g2+fn81z=4b1$2y(0lhj4-g&p^tjt%m8^xn!jq09"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", os.environ.get("SECRET_KEY"))

if not SECRET_KEY:
    if IS_PRODUCTION:
        raise ValueError(
            "⚠️ ERROR CRÍTICO: La variable de entorno DJANGO_SECRET_KEY o SECRET_KEY "
            "no está configurada. Esta es OBLIGATORIA en producción.\n"
            "Configure una clave secreta única en las variables de entorno."
        )
    else:
        # Solo en desarrollo local, usar clave por defecto
        SECRET_KEY = _DEFAULT_SECRET_KEY
        print("⚠️ ADVERTENCIA: Usando SECRET_KEY por defecto. NO usar en producción.")

# =============================================================================
# SEGURIDAD - DEBUG
# =============================================================================

# CRÍTICO: DEBUG debe ser False en producción
# Exponer DEBUG=True en producción revela información sensible
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

if IS_PRODUCTION and DEBUG:
    print(
        "⚠️ ADVERTENCIA: DEBUG=True detectado en entorno de producción. "
        "Esto es un riesgo de seguridad."
    )

# =============================================================================
# SEGURIDAD - ALLOWED_HOSTS
# =============================================================================

# Hosts permitidos - CRÍTICO para evitar DisallowedHost error
ALLOWED_HOSTS = []

# 1. Hosts por defecto para desarrollo
if DEBUG:
    ALLOWED_HOSTS.extend(["localhost", "127.0.0.1", "[::1]"])

# 2. Hostname automático de Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# 3. Hosts adicionales desde variable de entorno
EXTRA_HOSTS = os.environ.get("ALLOWED_HOSTS", "")
if EXTRA_HOSTS:
    ALLOWED_HOSTS.extend([h.strip() for h in EXTRA_HOSTS.split(",") if h.strip()])

# 4. Validación en producción
if IS_PRODUCTION and not ALLOWED_HOSTS:
    raise ValueError(
        "⚠️ ERROR: ALLOWED_HOSTS está vacío en producción.\n"
        "Configure la variable de entorno ALLOWED_HOSTS con los dominios permitidos.\n"
        "Ejemplo: ALLOWED_HOSTS=midominio.com,www.midominio.com"
    )

# =============================================================================
# APLICACIONES INSTALADAS
# =============================================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps del proyecto
    "Aplicaciones.Lista",
    # Apps de terceros
    "django_weasyprint",
]

# =============================================================================
# MIDDLEWARE
# =============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise para servir archivos estáticos en producción
    # Se inserta aquí para que esté después de SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =============================================================================
# CONFIGURACIÓN DE URLs Y WSGI
# =============================================================================

ROOT_URLCONF = "compraenUSAec_Recibo.urls"
WSGI_APPLICATION = "compraenUSAec_Recibo.wsgi.application"

# =============================================================================
# TEMPLATES
# =============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# =============================================================================
# BASE DE DATOS
# =============================================================================

# Intentar usar PostgreSQL si DATABASE_URL está configurada
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Producción: Usar PostgreSQL con dj-database-url
    try:
        import dj_database_url

        DATABASES = {
            "default": dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,  # Conexiones persistentes
                conn_health_checks=True,  # Verificar salud de conexiones
                ssl_require=not DEBUG,  # SSL en producción
            )
        }
        print(f"✓ Base de datos: PostgreSQL configurada")
    except ImportError:
        raise ImportError(
            "DATABASE_URL está configurada pero 'dj-database-url' no está instalado.\n"
            "Instálelo con: pip install dj-database-url"
        )
else:
    # Desarrollo: Usar SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
    if IS_PRODUCTION:
        print(
            "⚠️ ADVERTENCIA: Usando SQLite en producción. "
            "Configure DATABASE_URL para usar PostgreSQL."
        )

# =============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# =============================================================================
# INTERNACIONALIZACIÓN
# =============================================================================

LANGUAGE_CODE = "es-ec"  # Español de Ecuador
TIME_ZONE = "America/Guayaquil"  # Zona horaria de Ecuador
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =============================================================================
# ARCHIVOS ESTÁTICOS (CSS, JavaScript, Images)
# =============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Directorios adicionales de archivos estáticos
STATICFILES_DIRS = [
    # BASE_DIR / "static",  # Descomentar si tienes archivos estáticos globales
]

# WhiteNoise para servir archivos estáticos en producción
# Comprime y cachea archivos automáticamente
if IS_PRODUCTION:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
else:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# =============================================================================
# ARCHIVOS MEDIA (Uploads de usuarios)
# =============================================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =============================================================================
# SEGURIDAD HTTPS Y COOKIES (Solo en producción)
# =============================================================================

if IS_PRODUCTION:
    # Redirigir HTTP a HTTPS
    SECURE_SSL_REDIRECT = True

    # CRÍTICO: Necesario cuando hay un proxy/load balancer (Render, Hostinger, etc.)
    # Sin esto, puede haber bucles de redirección infinitos
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Cookies seguras (solo HTTPS)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Protección adicional de cookies
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False

    # Protección contra XSS y clickjacking
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

    # HSTS (HTTP Strict Transport Security)
    # Descomentar después de verificar que HTTPS funciona correctamente
    # SECURE_HSTS_SECONDS = 31536000  # 1 año
    # SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # SECURE_HSTS_PRELOAD = True

# =============================================================================
# CSRF TRUSTED ORIGINS (Requerido para Django 4.0+)
# =============================================================================

# Orígenes confiables para CSRF - CRÍTICO para formularios POST
CSRF_TRUSTED_ORIGINS = []

# 1. Agregar hostname de Render automáticamente
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# 2. Agregar orígenes adicionales desde variable de entorno
EXTRA_CSRF_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
if EXTRA_CSRF_ORIGINS:
    CSRF_TRUSTED_ORIGINS.extend(
        [o.strip() for o in EXTRA_CSRF_ORIGINS.split(",") if o.strip()]
    )

# 3. Agregar orígenes basados en ALLOWED_HOSTS
for host in ALLOWED_HOSTS:
    if host not in ["localhost", "127.0.0.1", "[::1]", "*"]:
        if not host.startswith("."):  # Ignorar wildcards como .example.com
            https_origin = f"https://{host}"
            if https_origin not in CSRF_TRUSTED_ORIGINS:
                CSRF_TRUSTED_ORIGINS.append(https_origin)

# =============================================================================
# LOGGING
# =============================================================================

# Configuración de logging compatible con PaaS (usa console, no archivos)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "console_verbose": {
            "level": "DEBUG",
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
        "django.request": {
            "handlers": ["console_verbose"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console_verbose"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# =============================================================================
# CONFIGURACIÓN ADICIONAL
# =============================================================================

# Tipo de campo de clave primaria por defecto (Django 3.2+)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# VERIFICACIÓN DE CONFIGURACIÓN EN PRODUCCIÓN
# =============================================================================

if IS_PRODUCTION:
    print("=" * 60)
    print("🚀 MODO PRODUCCIÓN DETECTADO")
    print("=" * 60)
    print(f"   DEBUG: {DEBUG}")
    print(f"   ALLOWED_HOSTS: {ALLOWED_HOSTS}")
    print(f"   CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
    print(f"   DATABASE: {'PostgreSQL' if DATABASE_URL else 'SQLite (⚠️)'}")
    print(f"   STATIC_STORAGE: {STATICFILES_STORAGE}")
    print("=" * 60)

# =============================================================================
# NOTAS DE DESPLIEGUE
# =============================================================================
"""
PARA RENDER:
1. Configurar variables de entorno en el dashboard:
   - SECRET_KEY o DJANGO_SECRET_KEY: (generar una clave segura)
   - DATABASE_URL: (se configura automáticamente con PostgreSQL)
   - DJANGO_SETTINGS_MODULE: compraenUSAec_Recibo.settings
   - DEBUG: False
   - ALLOWED_HOSTS: tu-app.onrender.com,tudominio.com

2. El RENDER_EXTERNAL_HOSTNAME se configura automáticamente

PARA HOSTINGER:
1. Configurar variables de entorno en el panel:
   - DJANGO_SECRET_KEY: (generar una clave segura)
   - DATABASE_URL: postgres://usuario:password@host:5432/database
   - DEBUG: False
   - ALLOWED_HOSTS: tudominio.com,www.tudominio.com
   - CSRF_TRUSTED_ORIGINS: https://tudominio.com,https://www.tudominio.com

PARA DESARROLLO LOCAL:
1. No se requieren variables de entorno
2. DEBUG=True por defecto
3. Usa SQLite automáticamente
4. ALLOWED_HOSTS incluye localhost por defecto
"""
