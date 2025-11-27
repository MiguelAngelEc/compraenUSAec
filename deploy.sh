#!/bin/bash

###############################################
# Script de Despliegue para Hostinger
# CompraEnUSAec - Sistema de Recibos
###############################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 DESPLIEGUE EN PRODUCCIÓN - Hostinger"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Variables de configuración
PROJECT_DIR="/home/u276243840/domains/compraenusaec.com/public_html/recibo"
VENV_DIR="/home/u276243840/virtualenv/recibo/3.11"
SETTINGS_MODULE="compraenUSAec_Recibo.settings_production"

# Cambiar al directorio del proyecto
cd $PROJECT_DIR || exit 1

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source $VENV_DIR/bin/activate

# Actualizar pip
echo "🔄 Actualizando pip..."
pip install --upgrade pip

# Instalar/Actualizar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

# Verificar instalación crítica
echo "✓ Verificando instalaciones críticas..."
python -c "import django; print(f'Django: {django.get_version()}')"
python -c "import weasyprint; print(f'WeasyPrint instalado')" 2>/dev/null || echo "⚠️ WeasyPrint puede no funcionar en Hostinger"

# Aplicar migraciones
echo ""
echo "🗄️ Aplicando migraciones de base de datos..."
python manage.py migrate --settings=$SETTINGS_MODULE --noinput

# Colectar archivos estáticos
echo ""
echo "📁 Colectando archivos estáticos..."
python manage.py collectstatic --settings=$SETTINGS_MODULE --noinput --clear

# Configurar permisos
echo ""
echo "🔐 Configurando permisos..."
chmod 664 Aplicaciones.db 2>/dev/null || echo "Base de datos se creará al primer acceso"
chmod 775 $PROJECT_DIR
chmod -R 755 staticfiles/ 2>/dev/null || echo "Directorio staticfiles será creado"
chmod -R 755 media/ 2>/dev/null || mkdir -p media && chmod -R 755 media/

# Crear directorio de logs si no existe
mkdir -p logs
chmod 775 logs

# Verificar configuración
echo ""
echo "🔍 Verificando configuración..."
python manage.py check --settings=$SETTINGS_MODULE --deploy

# Mensaje final
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DESPLIEGUE COMPLETADO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 PASOS SIGUIENTES:"
echo ""
echo "1. Crear superusuario (si es necesario):"
echo "   python manage.py createsuperuser --settings=$SETTINGS_MODULE"
echo ""
echo "2. Reiniciar la aplicación en el panel de Hostinger:"
echo "   Advanced > Python > Restart Application"
echo ""
echo "3. Verificar el sitio:"
echo "   https://recibo.compraenusaec.com/"
echo ""
echo "4. Revisar logs en caso de errores:"
echo "   tail -f django_errors.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"