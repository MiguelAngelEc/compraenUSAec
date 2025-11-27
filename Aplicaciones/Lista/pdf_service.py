"""
Servicio de Generación de PDF
CompraEnUSAec - Sistema de Recibos

Este módulo proporciona una capa de abstracción para la generación de PDFs,
con soporte para múltiples motores (WeasyPrint, xhtml2pdf).

WeasyPrint requiere GTK3 que puede no estar disponible en hosting compartido.
xhtml2pdf es más compatible pero con menos características CSS.
"""

import logging
from django.template.loader import render_to_string
from django.http import HttpResponse
from io import BytesIO

logger = logging.getLogger(__name__)

# ===========================================
# DETECCIÓN DE MOTOR DISPONIBLE
# ===========================================

PDF_ENGINE = None

# Intentar importar WeasyPrint primero (mejor calidad)
try:
    from weasyprint import HTML, CSS
    from django.conf import settings

    PDF_ENGINE = "weasyprint"
    logger.info("Motor PDF: WeasyPrint disponible")
except ImportError as e:
    logger.warning(f"WeasyPrint no disponible: {e}")

# Si WeasyPrint no está disponible, intentar xhtml2pdf
if PDF_ENGINE is None:
    try:
        from xhtml2pdf import pisa

        PDF_ENGINE = "xhtml2pdf"
        logger.info("Motor PDF: xhtml2pdf disponible")
    except ImportError as e:
        logger.warning(f"xhtml2pdf no disponible: {e}")

# Si ninguno está disponible
if PDF_ENGINE is None:
    logger.error("No hay motor de PDF disponible. Instale weasyprint o xhtml2pdf.")


def get_pdf_engine():
    """Retorna el motor de PDF actualmente en uso."""
    return PDF_ENGINE


# ===========================================
# GENERACIÓN DE PDF CON WEASYPRINT
# ===========================================


def generate_pdf_weasyprint(template_name, context, filename="document.pdf"):
    """
    Genera un PDF usando WeasyPrint.

    Args:
        template_name: Nombre del template HTML
        context: Diccionario con el contexto para el template
        filename: Nombre del archivo PDF

    Returns:
        HttpResponse con el PDF
    """
    from django.conf import settings
    import os

    # Renderizar el HTML
    html_string = render_to_string(template_name, context)

    # Crear el PDF con base_url apuntando al directorio static
    static_dir = os.path.join(settings.BASE_DIR, "Aplicaciones", "Lista", "static")
    html = HTML(string=html_string, base_url=static_dir)

    # Obtener CSS personalizado si existe
    css_path = os.path.join(static_dir, "css", "recibo_print.css")

    stylesheets = []
    if os.path.exists(css_path):
        stylesheets.append(CSS(filename=css_path))

    # Generar PDF
    pdf_file = html.write_pdf(stylesheets=stylesheets)

    # Crear respuesta HTTP
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'

    return response


# ===========================================
# GENERACIÓN DE PDF CON XHTML2PDF
# ===========================================


def generate_pdf_xhtml2pdf(template_name, context, filename="document.pdf"):
    """
    Genera un PDF usando xhtml2pdf.

    Args:
        template_name: Nombre del template HTML
        context: Diccionario con el contexto para el template
        filename: Nombre del archivo PDF

    Returns:
        HttpResponse con el PDF
    """
    from django.conf import settings
    import os

    # Renderizar el HTML
    html_string = render_to_string(template_name, context)

    # Crear buffer para el PDF
    result = BytesIO()

    # Ruta base de archivos estáticos de la app
    app_static = os.path.join(settings.BASE_DIR, "Aplicaciones", "Lista", "static")

    # Función para resolver enlaces (imágenes, CSS)
    def link_callback(uri, rel):
        """
        Convierte URIs relativos a rutas absolutas del sistema de archivos.
        """
        import os

        # Si es una ruta relativa (como css/recibo_print.css o Img/Logo.png)
        if not uri.startswith(("http://", "https://", "/")):
            full_path = os.path.join(app_static, uri)
            if os.path.exists(full_path):
                return full_path

        # Manejar archivos estáticos con URL completa
        if uri.startswith(settings.STATIC_URL):
            path = uri.replace(settings.STATIC_URL, "")
            # Primero buscar en el static de la app
            full_path = os.path.join(app_static, path)
            if os.path.exists(full_path):
                return full_path
            # Buscar en STATICFILES_DIRS
            for static_dir in getattr(settings, "STATICFILES_DIRS", []):
                full_path = os.path.join(static_dir, path)
                if os.path.exists(full_path):
                    return full_path
            # Buscar usando finders
            from django.contrib.staticfiles import finders

            found = finders.find(path)
            if found:
                return found

        # Manejar archivos media
        if uri.startswith(settings.MEDIA_URL):
            path = uri.replace(settings.MEDIA_URL, "")
            return os.path.join(settings.MEDIA_ROOT, path)

        return uri

    # Generar PDF
    pdf = pisa.pisaDocument(
        BytesIO(html_string.encode("UTF-8")),
        result,
        link_callback=link_callback,
        encoding="UTF-8",
    )

    if pdf.err:
        logger.error(f"Error generando PDF con xhtml2pdf: {pdf.err}")
        return HttpResponse("Error generando PDF", status=500)

    # Crear respuesta HTTP
    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'

    return response


# ===========================================
# FUNCIÓN PRINCIPAL (AUTO-SELECCIÓN DE MOTOR)
# ===========================================


def generate_pdf(template_name, context, filename="document.pdf"):
    """
    Genera un PDF usando el motor disponible.

    Intenta usar WeasyPrint primero (mejor calidad CSS).
    Si no está disponible, usa xhtml2pdf como fallback.

    Args:
        template_name: Nombre del template HTML
        context: Diccionario con el contexto para el template
        filename: Nombre del archivo PDF

    Returns:
        HttpResponse con el PDF

    Raises:
        RuntimeError: Si no hay motor de PDF disponible
    """
    if PDF_ENGINE == "weasyprint":
        return generate_pdf_weasyprint(template_name, context, filename)
    elif PDF_ENGINE == "xhtml2pdf":
        return generate_pdf_xhtml2pdf(template_name, context, filename)
    else:
        raise RuntimeError(
            "No hay motor de PDF disponible. "
            "Instale 'weasyprint' o 'xhtml2pdf' con pip."
        )


# ===========================================
# UTILIDADES
# ===========================================


def test_pdf_engines():
    """
    Prueba qué motores de PDF están disponibles.
    Útil para diagnóstico en producción.

    Returns:
        dict: Estado de cada motor
    """
    results = {
        "weasyprint": {"available": False, "error": None},
        "xhtml2pdf": {"available": False, "error": None},
        "active_engine": PDF_ENGINE,
    }

    # Probar WeasyPrint
    try:
        from weasyprint import HTML

        results["weasyprint"]["available"] = True
    except ImportError as e:
        results["weasyprint"]["error"] = str(e)

    # Probar xhtml2pdf
    try:
        from xhtml2pdf import pisa

        results["xhtml2pdf"]["available"] = True
    except ImportError as e:
        results["xhtml2pdf"]["error"] = str(e)

    return results
