#!/usr/bin/env bash
# Exit on error
set -o errexit

###############################################
# Script de Despliegue para Render
# CompraEnUSAec - Sistema de Recibos
###############################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 DESPLIEGUE EN RENDER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Upgrade pip
echo "🔄 Actualizando pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

# Collect static files
echo "📁 Colectando archivos estáticos..."
python manage.py collectstatic --no-input

# Run migrations
echo "🗄️ Aplicando migraciones..."
python manage.py migrate --no-input

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ BUILD COMPLETADO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"