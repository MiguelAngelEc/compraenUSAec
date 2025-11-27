# Análisis Completo del Proyecto Django - Sistema de Recibos CompraEnUSAec

## Resumen Ejecutivo

Este documento presenta un análisis exhaustivo del proyecto Django "Sistema de Recibos" para CompraEnUSAec, identificando errores críticos, problemas de seguridad, y malas prácticas que pueden causar fallos en producción.

---

# FASE 1: DETECCIÓN DE ERRORES

## 🔴 ERRORES CRÍTICOS

### Error #1: Conflicto de Archivos WSGI - Configuración Inconsistente

**Tipo:** Configuración / Despliegue  
**Archivos afectados:**

- [`wsgi.py`](wsgi.py:9) (raíz del proyecto)
- [`compraenUSAec_Recibo/wsgi.py`](compraenUSAec_Recibo/wsgi.py:14)

**Descripción del problema:**
Existen DOS archivos `wsgi.py` con configuraciones DIFERENTES:

1. **`wsgi.py` (raíz)** - Línea 10:

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "compraenUSAec_Recibo.settings_production")
```

2. **`compraenUSAec_Recibo/wsgi.py`** - Línea 14:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compraenUSAec_Recibo.settings')
```

**Por qué es problemático:**

- Dependiendo de qué archivo WSGI use el servidor, se cargará una configuración diferente
- El archivo en la raíz apunta a `settings_production` (que usa SQLite)
- El archivo en el paquete apunta a `settings` (desarrollo)
- Render usa `settings_render` según `render.yaml`, pero Gunicorn podría cargar el WSGI incorrecto

**Síntomas visibles:**

- `DisallowedHost` si se carga settings.py (ALLOWED_HOSTS vacío)
- Errores de base de datos si se espera PostgreSQL pero se carga SQLite
- Comportamiento impredecible entre despliegues

---

### Error #2: SECRET_KEY Expuesta en Código Fuente

**Tipo:** Seguridad CRÍTICA  
**Archivo:** [`compraenUSAec_Recibo/settings.py`](compraenUSAec_Recibo/settings.py:24)

**Código problemático:**

```python
SECRET_KEY = "$_-01fz%$4g2+fn81z=4b1$2y(0lhj4-g&p^tjt%m8^xn!jq09"
```

**Por qué es problemático:**

- La SECRET_KEY está hardcodeada y visible en el repositorio
- Cualquier persona con acceso al código puede comprometer la seguridad
- Permite falsificar cookies de sesión, tokens CSRF, y firmas criptográficas
- Viola las mejores prácticas de Django y estándares de seguridad

**Síntomas visibles:**

- Vulnerabilidad de seguridad (no visible directamente pero explotable)
- Posible compromiso de sesiones de usuario
- Fallos en auditorías de seguridad

---

### Error #3: Inconsistencia en Nombres de Base de Datos SQLite

**Tipo:** Base de Datos / Configuración  
**Archivos afectados:**

- [`settings.py`](compraenUSAec_Recibo/settings.py:83): `"NAME": "Aplicaciones.db"`
- [`settings_production.py`](compraenUSAec_Recibo/settings_production.py:27): `"NAME": os.path.join(BASE_DIR, "db.sqlite3")`
- [`settings_render.py`](compraenUSAec_Recibo/settings_render.py:48): `"NAME": BASE_DIR / "Aplicaciones.db"`

**Por qué es problemático:**

- Tres archivos de configuración usan TRES nombres diferentes de base de datos
- Al cambiar entre entornos, los datos no se encontrarán
- Las migraciones pueden aplicarse a una base de datos diferente

**Síntomas visibles:**

- "Table does not exist" al cambiar de entorno
- Pérdida aparente de datos
- Errores de migración

---

### Error #4: ALLOWED_HOSTS Vacío en settings_render.py sin Fallback

**Tipo:** Configuración / Despliegue  
**Archivo:** [`compraenUSAec_Recibo/settings_render.py`](compraenUSAec_Recibo/settings_render.py:19)

**Código problemático:**

```python
ALLOWED_HOSTS = []

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
```

**Por qué es problemático:**

- Si `RENDER_EXTERNAL_HOSTNAME` no está configurada, ALLOWED_HOSTS queda vacío
- Con DEBUG=False, Django rechazará TODAS las peticiones
- No hay hosts de respaldo configurados

**Síntomas visibles:**

- Error 400 Bad Request
- `DisallowedHost at /` en logs
- Sitio completamente inaccesible

---

### Error #5: Falta SECURE_PROXY_SSL_HEADER en settings_production.py

**Tipo:** Seguridad / Configuración HTTPS  
**Archivo:** [`compraenUSAec_Recibo/settings_production.py`](compraenUSAec_Recibo/settings_production.py:47)

**Código actual:**

```python
SECURE_SSL_REDIRECT = True
# Falta: SECURE_PROXY_SSL_HEADER
```

**Por qué es problemático:**

- Hostinger y otros servicios usan proxies/load balancers
- Sin `SECURE_PROXY_SSL_HEADER`, Django no detecta correctamente HTTPS
- Puede causar bucles de redirección infinitos
- Las cookies seguras pueden no funcionar correctamente

**Síntomas visibles:**

- ERR_TOO_MANY_REDIRECTS en el navegador
- Bucle infinito de redirección HTTP → HTTPS
- Cookies de sesión que no se guardan

---

## 🟠 ERRORES IMPORTANTES

### Error #6: Logging a Archivo en Entorno Serverless/Contenedor

**Tipo:** Configuración / Logging  
**Archivo:** [`compraenUSAec_Recibo/settings_production.py`](compraenUSAec_Recibo/settings_production.py:64-67)

**Código problemático:**

```python
"handlers": {
    "file": {
        "level": "ERROR",
        "class": "logging.FileHandler",
        "filename": os.path.join(BASE_DIR, "django_errors.log"),
    },
},
```

**Por qué es problemático:**

- En Render (y muchos PaaS), el sistema de archivos es efímero
- Los logs se pierden en cada redeploy
- Puede causar errores de permisos de escritura
- No es la práctica recomendada para contenedores

**Síntomas visibles:**

- Logs que desaparecen
- Posibles errores de permisos
- Dificultad para debugging

---

### Error #7: Falta DEFAULT_AUTO_FIELD

**Tipo:** Configuración / Deprecación  
**Archivos:** Todos los settings

**Por qué es problemático:**

- Django 3.2+ requiere especificar `DEFAULT_AUTO_FIELD`
- Sin esta configuración, Django muestra warnings
- Puede causar problemas con migraciones futuras

**Síntomas visibles:**

- Warnings en consola: `WARNINGS: ?: (models.W042)`
- Posibles problemas de compatibilidad futura

---

### Error #8: Endpoint de Diagnóstico Expuesto en Producción

**Tipo:** Seguridad  
**Archivo:** [`Aplicaciones/Lista/urls.py`](Aplicaciones/Lista/urls.py:19)

**Código problemático:**

```python
path("api/pdf-status/", views.pdf_status, name="pdf_status"),
```

**Por qué es problemático:**

- Expone información del sistema (motores PDF disponibles, errores)
- No tiene autenticación ni restricción
- Puede revelar información útil para atacantes

**Síntomas visibles:**

- Información sensible accesible públicamente
- Posible vector de reconocimiento para ataques

---

### Error #9: Falta Validación de SECRET_KEY en settings_render.py

**Tipo:** Seguridad / Configuración  
**Archivo:** [`compraenUSAec_Recibo/settings_render.py`](compraenUSAec_Recibo/settings_render.py:16)

**Código actual:**

```python
SECRET_KEY = os.environ.get("SECRET_KEY")
# No hay validación si es None
```

**Comparar con settings_production.py:**

```python
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("La variable de entorno DJANGO_SECRET_KEY no está configurada!")
```

**Por qué es problemático:**

- Si SECRET_KEY no está configurada, será `None`
- Django puede fallar de formas inesperadas
- Diferente nombre de variable entre archivos (`SECRET_KEY` vs `DJANGO_SECRET_KEY`)

**Síntomas visibles:**

- Errores criptográficos
- Fallos en autenticación
- Comportamiento impredecible

---

### Error #10: Uso de SQLite en Producción (settings_production.py)

**Tipo:** Base de Datos / Escalabilidad  
**Archivo:** [`compraenUSAec_Recibo/settings_production.py`](compraenUSAec_Recibo/settings_production.py:24-29)

**Código problemático:**

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
```

**Por qué es problemático:**

- SQLite no es adecuado para producción con múltiples usuarios
- No soporta escrituras concurrentes eficientemente
- En Render/Hostinger, el archivo puede perderse en redeploys
- No es escalable

**Síntomas visibles:**

- "Database is locked" bajo carga
- Pérdida de datos en redeploys
- Rendimiento degradado

---

### Error #11: Falta CSRF_TRUSTED_ORIGINS en settings_production.py

**Tipo:** Seguridad / CSRF  
**Archivo:** [`compraenUSAec_Recibo/settings_production.py`](compraenUSAec_Recibo/settings_production.py)

**Por qué es problemático:**

- Django 4.0+ requiere `CSRF_TRUSTED_ORIGINS` para peticiones HTTPS
- Sin esta configuración, los formularios POST fallarán
- Afecta login, registro de clientes, guardado de recibos

**Síntomas visibles:**

- Error 403 Forbidden en formularios
- "CSRF verification failed"
- Formularios que no se envían

---

## 🟡 ADVERTENCIAS Y MALAS PRÁCTICAS

### Advertencia #12: Versión Antigua de Django

**Tipo:** Mantenimiento / Seguridad  
**Archivo:** [`requirements.txt`](requirements.txt:9)

**Código actual:**

```
Django>=3.1.3,<4.0
```

**Por qué es problemático:**

- Django 3.1 ya no recibe actualizaciones de seguridad
- Faltan características modernas
- Posibles vulnerabilidades conocidas

---

### Advertencia #13: Nombres de Campos con Mayúsculas Inconsistentes

**Tipo:** Convenciones / Mantenibilidad  
**Archivo:** [`Aplicaciones/Lista/models.py`](Aplicaciones/Lista/models.py:7-12)

**Código actual:**

```python
class Clientes(models.Model):
    codigo=models.CharField(primary_key=True,max_length=15)
    Nombre_Apellido=models.CharField(max_length=50)  # Mayúscula
    Direccion=models.CharField(max_length=50)        # Mayúscula
    Ciudad=models.CharField(max_length=15)           # Mayúscula
    Telefono=models.CharField(max_length=15)         # Mayúscula
    email=models.EmailField()                        # Minúscula
```

**Por qué es problemático:**

- Viola PEP 8 (snake_case para atributos)
- Inconsistencia entre campos
- Dificulta mantenimiento

---

### Advertencia #14: Falta Configuración de MEDIA en URLs

**Tipo:** Configuración  
**Archivo:** [`compraenUSAec_Recibo/urls.py`](compraenUSAec_Recibo/urls.py)

**Por qué es problemático:**

- Si se suben archivos media, no serán servidos
- Falta configuración para desarrollo y producción

---

### Advertencia #15: WeasyPrint Puede No Funcionar en Hosting Compartido

**Tipo:** Dependencias / Compatibilidad  
**Archivo:** [`requirements.txt`](requirements.txt:15-16)

**Por qué es problemático:**

- WeasyPrint requiere GTK3 y otras dependencias del sistema
- Hostinger compartido probablemente no las tiene
- Puede causar fallos en la generación de PDFs

---

---

# FASE 2: PROPUESTA DE SOLUCIONES

## Solución para Error #1: Unificar Archivos WSGI

### Opción A: Eliminar wsgi.py de la raíz (RECOMENDADA)

```bash
# Eliminar el archivo duplicado
rm wsgi.py
```

Modificar [`render.yaml`](render.yaml:17):

```yaml
startCommand: "gunicorn compraenUSAec_Recibo.wsgi:application"
```

### Opción B: Actualizar wsgi.py de la raíz para usar variable de entorno

```python
import os
from django.core.wsgi import get_wsgi_application

# Usar variable de entorno, con fallback a settings_render para Render
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.environ.get("DJANGO_SETTINGS_MODULE", "compraenUSAec_Recibo.settings_render")
)

application = get_wsgi_application()
```

**Impacto:** Bajo riesgo, alta compatibilidad  
**Requiere reinicio:** Sí

---

## Solución para Error #2: Proteger SECRET_KEY

### Modificar [`settings.py`](compraenUSAec_Recibo/settings.py:24):

```python
import os
from pathlib import Path

# Cargar desde variable de entorno, con fallback SOLO para desarrollo local
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "$_-01fz%$4g2+fn81z=4b1$2y(0lhj4-g&p^tjt%m8^xn!jq09"  # Solo desarrollo
)

# Advertir si se usa la clave por defecto
if SECRET_KEY == "$_-01fz%$4g2+fn81z=4b1$2y(0lhj4-g&p^tjt%m8^xn!jq09":
    import warnings
    warnings.warn("Usando SECRET_KEY por defecto. Configure DJANGO_SECRET_KEY en producción.")
```

**Impacto:** Crítico para seguridad  
**Requiere:** Configurar variable de entorno en producción

---

## Solución para Error #3: Unificar Nombre de Base de Datos

### Estandarizar en todos los settings:

```python
# Para SQLite (desarrollo)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # Usar Path consistentemente
    }
}
```

**Impacto:** Medio, requiere migrar datos existentes  
**Requiere:** Renombrar archivo de base de datos si existe

---

## Solución para Error #4: Agregar Hosts de Respaldo

### Modificar [`settings_render.py`](compraenUSAec_Recibo/settings_render.py:19-29):

```python
# Dominios permitidos con fallbacks
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]

# Obtener el hostname de Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Agregar hosts adicionales si se especifican
EXTRA_HOSTS = os.environ.get("ALLOWED_HOSTS", "")
if EXTRA_HOSTS:
    ALLOWED_HOSTS.extend([h.strip() for h in EXTRA_HOSTS.split(",") if h.strip()])

# Validación de seguridad
if not RENDER_EXTERNAL_HOSTNAME and not EXTRA_HOSTS:
    import warnings
    warnings.warn("No se configuró RENDER_EXTERNAL_HOSTNAME ni ALLOWED_HOSTS adicionales")
```

**Impacto:** Bajo riesgo  
**Requiere reinicio:** Sí

---

## Solución para Error #5: Agregar SECURE_PROXY_SSL_HEADER

### Modificar [`settings_production.py`](compraenUSAec_Recibo/settings_production.py:47):

```python
# ======================
# SEGURIDAD HTTPS
# ======================
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # AGREGAR ESTA LÍNEA
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

**Impacto:** Crítico para HTTPS  
**Requiere reinicio:** Sí

---

## Solución para Error #6: Usar Console Logging

### Modificar [`settings_production.py`](compraenUSAec_Recibo/settings_production.py:60-77):

```python
# ======================
# LOGGING (Compatible con PaaS)
# ======================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
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
```

**Impacto:** Bajo riesgo  
**Requiere reinicio:** Sí

---

## Solución para Error #7: Agregar DEFAULT_AUTO_FIELD

### Agregar a todos los archivos settings:

```python
# Al final del archivo
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

**Impacto:** Bajo riesgo  
**Requiere:** Posiblemente nuevas migraciones

---

## Solución para Error #8: Proteger Endpoint de Diagnóstico

### Opción A: Eliminar en producción

```python
# En urls.py, solo incluir en DEBUG
from django.conf import settings

urlpatterns = [
    # ... otras URLs
]

if settings.DEBUG:
    urlpatterns += [
        path("api/pdf-status/", views.pdf_status, name="pdf_status"),
    ]
```

### Opción B: Requerir autenticación de staff

```python
# En views.py
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def pdf_status(request):
    status = test_pdf_engines()
    return JsonResponse(status)
```

**Impacto:** Bajo riesgo  
**Requiere reinicio:** Sí

---

## Solución para Error #9: Validar SECRET_KEY en settings_render.py

### Modificar [`settings_render.py`](compraenUSAec_Recibo/settings_render.py:16):

```python
# Clave secreta desde variable de entorno (OBLIGATORIA)
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "La variable de entorno SECRET_KEY no está configurada. "
        "Configure esta variable en el panel de Render."
    )
```

**Impacto:** Crítico para seguridad  
**Requiere:** Variable de entorno configurada

---

## Solución para Error #10: Usar PostgreSQL en Producción

### Ya está configurado en settings_render.py, pero agregar validación:

```python
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
    raise ValueError(
        "DATABASE_URL no está configurada. "
        "Configure una base de datos PostgreSQL en Render."
    )
```

**Impacto:** Crítico para persistencia de datos  
**Requiere:** Base de datos PostgreSQL configurada

---

## Solución para Error #11: Agregar CSRF_TRUSTED_ORIGINS

### Modificar [`settings_production.py`](compraenUSAec_Recibo/settings_production.py):

```python
# ======================
# CSRF TRUSTED ORIGINS
# ======================
CSRF_TRUSTED_ORIGINS = [
    "https://recibo-compraenusaec.onrender.com",
    "https://compraenusaec.com",
    "https://www.compraenusaec.com",
]
```

**Impacto:** Crítico para formularios  
**Requiere reinicio:** Sí

---

---

# FASE 3: RECOMENDACIÓN FINAL

## Configuración Óptima Recomendada

### 1. Estructura de Archivos de Configuración

```
compraenUSAec_Recibo/
├── settings/
│   ├── __init__.py      # Importa el settings correcto según entorno
│   ├── base.py          # Configuración común
│   ├── development.py   # Desarrollo local
│   ├── production.py    # Producción genérica (Hostinger)
│   └── render.py        # Específico para Render
```

### 2. Archivo settings_render.py Corregido (Completo)

```python
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
DEBUG = False  # Siempre False en producción

# Clave secreta OBLIGATORIA
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no está configurada en las variables de entorno")

# Dominios permitidos
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

EXTRA_HOSTS = os.environ.get("ALLOWED_HOSTS", "")
if EXTRA_HOSTS:
    ALLOWED_HOSTS.extend([h.strip() for h in EXTRA_HOSTS.split(",") if h.strip()])

# ===========================================
# BASE DE DATOS - PostgreSQL OBLIGATORIO
# ===========================================
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurada. Use PostgreSQL en producción.")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ===========================================
# ARCHIVOS ESTÁTICOS
# ===========================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ===========================================
# SEGURIDAD HTTPS
# ===========================================
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

# ===========================================
# CSRF TRUSTED ORIGINS
# ===========================================
CSRF_TRUSTED_ORIGINS = []
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# ===========================================
# LOGGING (Console para PaaS)
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

# ===========================================
# CONFIGURACIÓN ADICIONAL
# ===========================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

### 3. Variables de Entorno Requeridas en Render

| Variable                   | Descripción          | Ejemplo                                   |
| -------------------------- | -------------------- | ----------------------------------------- |
| `SECRET_KEY`               | Clave secreta Django | (generada automáticamente)                |
| `DATABASE_URL`             | URL de PostgreSQL    | (desde base de datos Render)              |
| `DJANGO_SETTINGS_MODULE`   | Módulo de settings   | `compraenUSAec_Recibo.settings_render`    |
| `RENDER_EXTERNAL_HOSTNAME` | Hostname de Render   | (automático)                              |
| `ALLOWED_HOSTS`            | Hosts adicionales    | `compraenusaec.com,www.compraenusaec.com` |

### 4. Orden de Prioridad para Correcciones

| Prioridad | Error                         | Impacto | Tiempo Estimado |
| --------- | ----------------------------- | ------- | --------------- |
| 🔴 1      | Conflicto WSGI                | Crítico | 5 min           |
| 🔴 2      | SECRET_KEY expuesta           | Crítico | 10 min          |
| 🔴 3      | ALLOWED_HOSTS vacío           | Crítico | 5 min           |
| 🔴 4      | Falta SECURE_PROXY_SSL_HEADER | Crítico | 2 min           |
| 🔴 5      | Falta CSRF_TRUSTED_ORIGINS    | Crítico | 5 min           |
| 🟠 6      | Validar SECRET_KEY en render  | Alto    | 5 min           |
| 🟠 7      | SQLite en producción          | Alto    | 10 min          |
| 🟠 8      | Logging a archivo             | Medio   | 10 min          |
| 🟡 9      | DEFAULT_AUTO_FIELD            | Bajo    | 2 min           |
| 🟡 10     | Endpoint diagnóstico          | Bajo    | 5 min           |

### 5. Checklist de Despliegue

- [ ] Eliminar o unificar archivos WSGI duplicados
- [ ] Configurar SECRET_KEY como variable de entorno
- [ ] Verificar ALLOWED_HOSTS incluye todos los dominios
- [ ] Agregar SECURE_PROXY_SSL_HEADER
- [ ] Agregar CSRF_TRUSTED_ORIGINS
- [ ] Configurar PostgreSQL (no SQLite)
- [ ] Cambiar logging a console
- [ ] Agregar DEFAULT_AUTO_FIELD
- [ ] Proteger endpoint de diagnóstico
- [ ] Ejecutar `python manage.py check --deploy`
- [ ] Probar formularios POST después del despliegue

---

## Conclusión

El proyecto tiene una base sólida pero requiere correcciones críticas antes de producción. Los errores más urgentes son:

1. **Conflicto de archivos WSGI** - Puede causar comportamiento impredecible
2. **SECRET_KEY expuesta** - Vulnerabilidad de seguridad grave
3. **ALLOWED_HOSTS vacío** - Sitio inaccesible en producción
4. **Falta SECURE_PROXY_SSL_HEADER** - Bucles de redirección HTTPS

Implementando las soluciones propuestas, el sistema será seguro, estable y escalable para producción en Render o Hostinger.
