# Integración de Supabase con Django - CompraEnUSAec

Este documento describe cómo se ha configurado Supabase como base de datos para el proyecto Django.

## 📋 Resumen

Supabase proporciona:

1. **Base de datos PostgreSQL** - Conectada directamente a Django via `DATABASE_URL`
2. **API REST** - Para operaciones adicionales via el cliente Python de Supabase
3. **Autenticación** - Sistema de auth integrado (opcional)
4. **Storage** - Almacenamiento de archivos (opcional)
5. **Real-time** - Suscripciones en tiempo real (opcional)

## 🔧 Configuración

### 1. Variables de Entorno (.env)

```env
# Supabase API
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key

# Django Database (Supabase PostgreSQL)
DATABASE_URL=postgres://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres

# Django Settings
DJANGO_SECRET_KEY=tu-clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 2. Obtener Credenciales de Supabase

1. Ve a [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Selecciona tu proyecto
3. **Para API Keys** (Settings > API):
   - `SUPABASE_URL`: Project URL
   - `SUPABASE_ANON_KEY`: anon public key
   - `SUPABASE_SERVICE_ROLE_KEY`: service_role key
4. **Para Database URL** (Settings > Database):
   - Copia el "Connection string" (formato URI)
   - Reemplaza `[YOUR-PASSWORD]` con tu contraseña de base de datos

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

O individualmente:

```bash
pip install supabase psycopg2-binary dj-database-url python-dotenv
```

## 🗄️ Uso de la Base de Datos

### Opción 1: Django ORM (Recomendado para la mayoría de casos)

Django se conecta directamente a PostgreSQL de Supabase. Usa los modelos normalmente:

```python
from Aplicaciones.Lista.models import Clientes, Recibo, DetalleRecibo

# Crear cliente
cliente = Clientes.objects.create(
    codigo='CLI001',
    Nombre_Apellido='Juan Pérez',
    Direccion='Av. Principal 123',
    Ciudad='Guayaquil',
    Telefono='0991234567',
    email='juan@example.com'
)

# Consultar clientes
clientes = Clientes.objects.all()
cliente = Clientes.objects.get(codigo='CLI001')

# Actualizar
cliente.Telefono = '0997654321'
cliente.save()

# Eliminar
cliente.delete()
```

### Opción 2: Cliente Supabase Python (Para funciones avanzadas)

Usa el cliente Supabase para operaciones especiales:

```python
from Aplicaciones.Lista.supabase_client import (
    supabase,
    fetch_all,
    fetch_one,
    insert_record,
    update_record,
    delete_record
)

# Consultar todos los registros
clientes = fetch_all('clientes')

# Consultar con filtros
clientes_gye = fetch_all('clientes', filters={'ciudad': 'Guayaquil'})

# Obtener un registro específico
cliente = fetch_one('clientes', 'codigo', 'CLI001')

# Insertar
nuevo = insert_record('clientes', {
    'codigo': 'CLI002',
    'nombre_apellido': 'María García',
    'ciudad': 'Quito'
})

# Actualizar
actualizado = update_record('clientes', 'codigo', 'CLI001', {
    'telefono': '0991111111'
})

# Eliminar
eliminado = delete_record('clientes', 'codigo', 'CLI001')
```

### Opción 3: Cliente Supabase Directo

Para operaciones más complejas:

```python
from Aplicaciones.Lista.supabase_client import get_supabase_client

client = get_supabase_client()

# Consulta con múltiples filtros
response = client.table('clientes')\
    .select('codigo, nombre_apellido, ciudad')\
    .eq('ciudad', 'Guayaquil')\
    .order('nombre_apellido')\
    .limit(10)\
    .execute()

clientes = response.data

# Consulta con relaciones (si existen foreign keys)
response = client.table('recibos')\
    .select('*, clientes(*)')\
    .execute()
```

## 📁 Storage (Almacenamiento de Archivos)

```python
from Aplicaciones.Lista.supabase_client import upload_file, get_public_url, delete_file

# Subir archivo
with open('documento.pdf', 'rb') as f:
    result = upload_file('documentos', 'recibos/recibo_001.pdf', f, 'application/pdf')

# Obtener URL pública
url = get_public_url('documentos', 'recibos/recibo_001.pdf')

# Eliminar archivo
delete_file('documentos', ['recibos/recibo_001.pdf'])
```

## 🔐 Autenticación (Opcional)

Si deseas usar la autenticación de Supabase:

```python
from Aplicaciones.Lista.supabase_client import get_supabase_client

client = get_supabase_client()

# Registrar usuario
response = client.auth.sign_up({
    'email': 'usuario@example.com',
    'password': 'contraseña123'
})

# Iniciar sesión
response = client.auth.sign_in_with_password({
    'email': 'usuario@example.com',
    'password': 'contraseña123'
})

# Cerrar sesión
client.auth.sign_out()
```

## 🔄 Migraciones

### Sincronizar modelos Django con Supabase

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones a Supabase
python manage.py migrate
```

### Crear tablas manualmente en Supabase

Si prefieres crear las tablas directamente en Supabase SQL Editor:

```sql
-- Tabla Clientes
CREATE TABLE IF NOT EXISTS "Lista_clientes" (
    codigo VARCHAR(15) PRIMARY KEY,
    "Nombre_Apellido" VARCHAR(50) NOT NULL,
    "Direccion" VARCHAR(50) NOT NULL,
    "Ciudad" VARCHAR(15) NOT NULL,
    "Telefono" VARCHAR(15) NOT NULL,
    email VARCHAR(254) NOT NULL
);

-- Tabla Recibo
CREATE TABLE IF NOT EXISTS "Lista_recibo" (
    id BIGSERIAL PRIMARY KEY,
    cliente_id VARCHAR(15) REFERENCES "Lista_clientes"(codigo) ON DELETE CASCADE,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    subtotal_productos DECIMAL(10,2) DEFAULT 0.00,
    total_abonos DECIMAL(10,2) DEFAULT 0.00,
    subtotal_flete DECIMAL(10,2) DEFAULT 0.00,
    total DECIMAL(10,2) DEFAULT 0.00
);

-- Tabla DetalleRecibo
CREATE TABLE IF NOT EXISTS "Lista_detallerecibo" (
    id BIGSERIAL PRIMARY KEY,
    recibo_id BIGINT REFERENCES "Lista_recibo"(id) ON DELETE CASCADE,
    tracking_id VARCHAR(100) NOT NULL,
    tienda VARCHAR(100),
    wr VARCHAR(50),
    precio_producto DECIMAL(10,2) DEFAULT 0.00,
    abono DECIMAL(10,2) DEFAULT 0.00,
    saldo_producto DECIMAL(10,2) DEFAULT 0.00,
    peso_libras DECIMAL(10,2) DEFAULT 0.00,
    precio_por_libra DECIMAL(10,2) DEFAULT 0.00,
    total_flete DECIMAL(10,2) DEFAULT 0.00
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_recibo_cliente ON "Lista_recibo"(cliente_id);
CREATE INDEX IF NOT EXISTS idx_recibo_fecha ON "Lista_recibo"(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_detalle_recibo ON "Lista_detallerecibo"(recibo_id);
```

## 🧪 Probar la Conexión

### Verificar conexión a la base de datos:

```bash
python manage.py dbshell
```

### Script de prueba:

```python
# test_supabase.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compraenUSAec_Recibo.settings')
django.setup()

# Test Django ORM
from Aplicaciones.Lista.models import Clientes
print(f"Clientes en DB: {Clientes.objects.count()}")

# Test Supabase Client
from Aplicaciones.Lista.supabase_client import get_supabase_client
client = get_supabase_client()
print(f"Supabase conectado: {client.supabase_url}")
```

Ejecutar:

```bash
python test_supabase.py
```

## ⚠️ Consideraciones Importantes

### Row Level Security (RLS)

Supabase tiene RLS habilitado por defecto. Para que Django pueda acceder a las tablas:

1. **Opción A**: Deshabilitar RLS (solo para desarrollo)

   ```sql
   ALTER TABLE "Lista_clientes" DISABLE ROW LEVEL SECURITY;
   ```

2. **Opción B**: Crear políticas permisivas

   ```sql
   CREATE POLICY "Allow all" ON "Lista_clientes" FOR ALL USING (true);
   ```

3. **Opción C**: Usar el `service_role` key (recomendado para backend)
   - El `service_role` key bypasea RLS automáticamente

### Nombres de Tablas

Django usa el formato `app_model` para nombres de tablas (ej: `Lista_clientes`).
Asegúrate de que las tablas en Supabase coincidan con este formato.

### Conexión Pooling

Supabase ofrece connection pooling. Usa el puerto `6543` para pooling:

```
postgres://postgres.[ref]:[pass]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

O el puerto `5432` para conexión directa:

```
postgres://postgres.[ref]:[pass]@aws-0-us-west-1.pooler.supabase.com:5432/postgres
```

## 📚 Recursos

- [Documentación de Supabase](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Django Database Settings](https://docs.djangoproject.com/en/4.2/ref/settings/#databases)
- [dj-database-url](https://github.com/jazzband/dj-database-url)
