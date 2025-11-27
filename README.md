# CompraEnUSAec - Sistema de Gestión de Recibos

Sistema de gestión de clientes y generación de recibos para servicio de courier/importación desde Estados Unidos.

![Django](https://img.shields.io/badge/Django-3.1+-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![WeasyPrint](https://img.shields.io/badge/PDF-WeasyPrint%20%7C%20xhtml2pdf-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Descripción

CompraEnUSAec es una aplicación web desarrollada en Django para gestionar:

- **Clientes**: Registro, edición y eliminación de clientes
- **Recibos**: Generación de recibos con detalles de productos y flete
- **PDF**: Exportación de recibos en formato PDF

## 🚀 Características

- ✅ Gestión completa de clientes (CRUD)
- ✅ Generación de recibos con múltiples items
- ✅ Cálculo automático de totales (productos + flete)
- ✅ Exportación a PDF con WeasyPrint
- ✅ Interfaz responsive con Tailwind CSS
- ✅ API REST para búsqueda de clientes

## 📁 Estructura del Proyecto

```
compraenUSAec/
├── manage.py                    # Script de gestión de Django
├── requirements.txt             # Dependencias del proyecto
├── README.md                    # Este archivo
├── .gitignore                   # Archivos ignorados por Git
├── .prettierignore              # Archivos ignorados por Prettier
├── Aplicaciones.db              # Base de datos SQLite
│
├── compraenUSAec_Recibo/        # Configuración del proyecto
│   ├── __init__.py
│   ├── settings.py              # Configuración de Django (desarrollo)
│   ├── settings_production.py   # Configuración de producción
│   ├── urls.py                  # URLs principales
│   ├── wsgi.py                  # Configuración WSGI
│   └── asgi.py                  # Configuración ASGI
│
├── passenger_wsgi.py            # WSGI para Hostinger
├── .htaccess                    # Configuración Apache
├── deploy.sh                    # Script de despliegue
│
└── Aplicaciones/
    └── Lista/                   # Aplicación principal
        ├── __init__.py
        ├── admin.py             # Configuración del admin
        ├── apps.py              # Configuración de la app
        ├── forms.py             # Formularios
        ├── models.py            # Modelos de datos
        ├── services.py          # Lógica de negocio
        ├── pdf_service.py       # Servicio de generación PDF
        ├── urls.py              # URLs de la app
        ├── views.py             # Vistas
        │
        ├── migrations/          # Migraciones de BD
        │
        ├── static/              # Archivos estáticos
        │   ├── css/
        │   │   ├── gestionClientes.css
        │   │   └── recibo_print.css    # Estilos del PDF
        │   ├── js/
        │   │   └── gestionClientes.js
        │   └── Img/
        │       └── Logo.png
        │
        └── templates/           # Plantillas HTML
            ├── Base.html
            ├── gestionLista.html
            ├── registro.html
            ├── edicionCliente.html
            ├── recibo_app.html
            └── recibo_print.html       # Template del PDF
```

## 🛠️ Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- GTK3 (requerido por WeasyPrint)

### Instalación de GTK3 (Windows)

WeasyPrint requiere GTK3 para funcionar. En Windows:

1. Descargar el instalador de [MSYS2](https://www.msys2.org/)
2. Ejecutar en la terminal MSYS2:
   ```bash
   pacman -S mingw-w64-x86_64-gtk3
   ```
3. Agregar al PATH: `C:\msys64\mingw64\bin`

### Pasos de Instalación

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/tu-usuario/compraenUSAec.git
   cd compraenUSAec
   ```

2. **Crear entorno virtual**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Aplicar migraciones**

   ```bash
   python manage.py migrate
   ```

5. **Crear superusuario (opcional)**

   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecutar servidor de desarrollo**

   ```bash
   python manage.py runserver
   ```

7. **Acceder a la aplicación**
   - Aplicación: http://localhost:8000/
   - Admin: http://localhost:8000/admin/

## 📖 Uso

### Gestión de Clientes

1. Ir a la página principal
2. Click en "Nuevo Cliente" para registrar
3. Completar el formulario con:
   - Código (cédula/identificación)
   - Nombre y Apellido
   - Dirección
   - Ciudad
   - Teléfono
   - Email

### Generación de Recibos

1. Ir a "Generar Recibo"
2. Buscar cliente por código
3. Agregar items con:
   - Tracking ID
   - Tienda (opcional)
   - WR (opcional)
   - Precio del producto
   - Abono
   - Peso en libras
   - Precio por libra
4. Click en "Generar Recibo"
5. El PDF se abrirá automáticamente

## 🗃️ Modelos de Datos

### Cliente

| Campo           | Tipo           | Descripción           |
| --------------- | -------------- | --------------------- |
| codigo          | CharField (PK) | Cédula/Identificación |
| Nombre_Apellido | CharField      | Nombre completo       |
| Direccion       | CharField      | Dirección de entrega  |
| Ciudad          | CharField      | Ciudad                |
| Telefono        | CharField      | Número de teléfono    |
| email           | EmailField     | Correo electrónico    |

### Recibo

| Campo              | Tipo           | Descripción           |
| ------------------ | -------------- | --------------------- |
| id                 | AutoField (PK) | ID único              |
| cliente            | ForeignKey     | Referencia al cliente |
| fecha              | DateTimeField  | Fecha de creación     |
| subtotal_productos | DecimalField   | Suma de productos     |
| total_abonos       | DecimalField   | Suma de abonos        |
| subtotal_flete     | DecimalField   | Costo total del flete |
| total              | DecimalField   | Total a pagar         |

### DetalleRecibo

| Campo            | Tipo         | Descripción          |
| ---------------- | ------------ | -------------------- |
| recibo           | ForeignKey   | Referencia al recibo |
| tracking_id      | CharField    | Número de tracking   |
| tienda           | CharField    | Tienda de origen     |
| wr               | CharField    | Warehouse Receipt    |
| precio_producto  | DecimalField | Precio del producto  |
| abono            | DecimalField | Abono realizado      |
| saldo_producto   | DecimalField | Saldo pendiente      |
| peso_libras      | DecimalField | Peso en libras       |
| precio_por_libra | DecimalField | Tarifa por libra     |
| total_flete      | DecimalField | Total del flete      |

## 🔗 API Endpoints

| Método | URL                             | Descripción            |
| ------ | ------------------------------- | ---------------------- |
| GET    | `/`                             | Lista de clientes      |
| GET    | `/registro/`                    | Formulario de registro |
| POST   | `/registro/`                    | Crear cliente          |
| GET    | `/edicion/<codigo>/`            | Editar cliente         |
| POST   | `/editar/`                      | Actualizar cliente     |
| GET    | `/eliminar/<codigo>/`           | Eliminar cliente       |
| GET    | `/recibo/`                      | Formulario de recibo   |
| GET    | `/api/buscar-cliente/?codigo=X` | Buscar cliente (JSON)  |
| POST   | `/api/guardar-recibo/`          | Guardar recibo (JSON)  |
| GET    | `/recibo/<id>/`                 | Ver recibo HTML        |
| GET    | `/recibo/<id>/pdf/`             | Descargar recibo PDF   |
| GET    | `/api/pdf-status/`              | Estado del motor PDF   |

## 🎨 Tecnologías Utilizadas

- **Backend**: Django 3.1+
- **Base de Datos**: SQLite (desarrollo), PostgreSQL/MySQL (producción)
- **Frontend**: HTML5, Tailwind CSS, JavaScript
- **PDF**: WeasyPrint (principal) / xhtml2pdf (fallback)
- **Estilos PDF**: CSS puro (semántico)
- **Servidor**: Gunicorn + WhiteNoise
- **Hosting**: Hostinger (Passenger WSGI)

## 📝 Notas de Desarrollo

### Generación de PDF

El sistema usa WeasyPrint para generar PDFs. Los estilos están en CSS puro (no Tailwind) porque:

- WeasyPrint no puede procesar Tailwind CDN
- CSS estático garantiza consistencia en el PDF
- Permite usar `@media print` y `@page`

### Archivos Importantes

- `recibo_print.html`: Template del PDF con clases semánticas
- `recibo_print.css`: Estilos CSS puros para el PDF
- `.prettierignore`: Evita que Prettier rompa los template tags de Django
- `pdf_service.py`: Servicio con fallback automático entre motores PDF

## 🚀 Despliegue en Producción (Hostinger)

### Archivos de Configuración

| Archivo                  | Descripción                                  |
| ------------------------ | -------------------------------------------- |
| `settings_production.py` | Configuración Django para producción         |
| `passenger_wsgi.py`      | Punto de entrada WSGI para Hostinger         |
| `.htaccess`              | Configuración Apache (SSL, caché, seguridad) |
| `deploy.sh`              | Script automatizado de despliegue            |

### Pasos de Despliegue

1. **Subir archivos a Hostinger**

   ```bash
   # Via FTP, SSH o File Manager de Hostinger
   # Destino: /home/u276243840/domains/compraenusaec.com/public_html/recibo/
   ```

2. **Configurar Python App en Hostinger**

   - Panel de Control → Advanced → Python
   - Crear nueva aplicación Python 3.11
   - Directorio: `/public_html/recibo`
   - Startup file: `passenger_wsgi.py`

3. **Ejecutar script de despliegue**

   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **Verificar instalación**
   ```bash
   # Probar motor PDF disponible
   curl https://recibo.compraenusaec.com/api/pdf-status/
   ```

### Nota sobre WeasyPrint

WeasyPrint requiere GTK3, que **puede no estar disponible** en hosting compartido. El sistema incluye:

- **Detección automática**: `pdf_service.py` detecta qué motor está disponible
- **Fallback a xhtml2pdf**: Si WeasyPrint falla, usa xhtml2pdf automáticamente
- **Endpoint de diagnóstico**: `/api/pdf-status/` muestra el motor activo

### Variables de Entorno (Producción)

```bash
export DJANGO_SETTINGS_MODULE=compraenUSAec_Recibo.settings_production
export DJANGO_SECRET_KEY="tu-clave-secreta-muy-larga-y-segura"
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Contacto

- **Empresa**: CompraEnUSAec
- **Dirección**: Pedro Moncayo 6-34 y Olmedo, Ibarra-Imbabura
- **Teléfono**: (+593) 0983050335
- **Instagram**: @compraenusaec

---

Desarrollado con ❤️ para CompraEnUSAec
