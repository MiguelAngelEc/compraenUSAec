"""
Views para CompraEnUSAec
========================

Todas las vistas usan Supabase como backend de datos.
NO se usa Django ORM para datos de negocio.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .supabase_client import (
    get_all_clientes,
    get_cliente_by_codigo,
    create_cliente,
    update_cliente,
    delete_cliente,
    get_recibo_by_id,
)
from .services import ReciboService
from .pdf_service import generate_pdf, test_pdf_engines
import json
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# VISTAS DE CLIENTES
# =============================================================================


def home(request):
    """Vista principal - Lista de clientes."""
    try:
        clientes = get_all_clientes()
    except Exception as e:
        logger.error(f"Error obteniendo clientes: {e}")
        clientes = []
        messages.error(
            request, "Error al cargar los clientes. Verifique la conexión con Supabase."
        )

    return render(request, "gestionLista.html", {"listado": clientes})


def registro(request):
    """Vista para registrar un nuevo cliente."""
    if request.method == "POST":
        try:
            data = {
                "codigo": request.POST.get("codigo", "").strip(),
                "nombre_apellido": request.POST.get("nombre_apellido", "").strip(),
                "direccion": request.POST.get("direccion", "").strip(),
                "ciudad": request.POST.get("ciudad", "").strip(),
                "telefono": request.POST.get("telefono", "").strip(),
                "email": request.POST.get("email", "").strip(),
            }

            # Validación básica
            if not data["codigo"]:
                messages.error(request, "El código/cédula es obligatorio.")
                return render(request, "registro.html", {"form_data": data})

            if not data["nombre_apellido"]:
                messages.error(request, "El nombre es obligatorio.")
                return render(request, "registro.html", {"form_data": data})

            # Verificar si ya existe
            existing = get_cliente_by_codigo(data["codigo"])
            if existing:
                messages.error(
                    request, f"Ya existe un cliente con el código {data['codigo']}."
                )
                return render(request, "registro.html", {"form_data": data})

            # Crear cliente en Supabase
            create_cliente(data)
            messages.success(request, "Cliente registrado exitosamente!")
            return redirect("home")

        except Exception as e:
            logger.error(f"Error creando cliente: {e}")
            messages.error(request, f"Error al registrar cliente: {str(e)}")
            return render(request, "registro.html", {"form_data": data})

    return render(request, "registro.html", {"form_data": {}})


def edicionCliente(request, codigo):
    """Vista para editar un cliente existente."""
    cliente = get_cliente_by_codigo(codigo)

    if not cliente:
        messages.error(request, "Cliente no encontrado.")
        return redirect("home")

    return render(request, "edicionCliente.html", {"cliente": cliente})


@require_http_methods(["POST"])
def editarCliente(request):
    """Procesa la edición de un cliente."""
    codigo = request.POST.get("txtCodigo", "").strip()

    if not codigo:
        messages.error(request, "Código de cliente no proporcionado.")
        return redirect("home")

    try:
        data = {
            "nombre_apellido": request.POST.get("txtNombreApellido", "").strip(),
            "direccion": request.POST.get("txtDireccion", "").strip(),
            "ciudad": request.POST.get("txtCiudad", "").strip(),
            "telefono": request.POST.get("txtTelefono", "").strip(),
            "email": request.POST.get("txtEmail", "").strip(),
        }

        update_cliente(codigo, data)
        messages.success(request, "Cliente actualizado exitosamente!")

    except Exception as e:
        logger.error(f"Error actualizando cliente {codigo}: {e}")
        messages.error(request, f"Error al actualizar cliente: {str(e)}")

    return redirect("home")


def eliminarCliente(request, codigo):
    """Elimina un cliente."""
    try:
        result = delete_cliente(codigo)
        if result:
            messages.success(request, "Cliente eliminado exitosamente!")
        else:
            messages.warning(request, "No se pudo eliminar el cliente.")
    except Exception as e:
        logger.error(f"Error eliminando cliente {codigo}: {e}")
        messages.error(request, f"Error al eliminar cliente: {str(e)}")

    return redirect("home")


# =============================================================================
# VISTAS DE RECIBOS
# =============================================================================


def recibo_view(request):
    """Vista principal para generar recibos."""
    return render(request, "recibo_app.html")


def buscar_cliente_api(request):
    """API para buscar cliente por código/cédula via AJAX."""
    codigo = request.GET.get("codigo", "").strip()

    if not codigo:
        return JsonResponse({"found": False, "error": "Código no proporcionado"})

    try:
        cliente = get_cliente_by_codigo(codigo)

        if cliente:
            data = {
                "found": True,
                "nombre": cliente.get("nombre_apellido", ""),
                "direccion": cliente.get("direccion", ""),
                "ciudad": cliente.get("ciudad", ""),
                "telefono": cliente.get("telefono", ""),
                "email": cliente.get("email", ""),
            }
        else:
            data = {"found": False}

    except Exception as e:
        logger.error(f"Error buscando cliente {codigo}: {e}")
        data = {"found": False, "error": str(e)}

    return JsonResponse(data)


@require_http_methods(["POST"])
def guardar_recibo_api(request):
    """API para guardar el recibo generado."""
    try:
        data = json.loads(request.body)
        cliente_codigo = data.get("cliente_codigo")
        items = data.get("items", [])

        if not cliente_codigo:
            return JsonResponse({"success": False, "error": "Cliente no especificado"})

        if not items:
            return JsonResponse(
                {"success": False, "error": "No hay items en el recibo"}
            )

        # Crear recibo usando el servicio
        recibo = ReciboService.crear_recibo(cliente_codigo, items)

        return JsonResponse({"success": True, "recibo_id": recibo["id"]})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "JSON inválido"})
    except Exception as e:
        logger.error(f"Error guardando recibo: {e}")
        return JsonResponse({"success": False, "error": str(e)})


def ver_recibo(request, recibo_id):
    """Vista para ver un recibo."""
    recibo = get_recibo_by_id(recibo_id)

    if not recibo:
        raise Http404("Recibo no encontrado")

    return render(request, "recibo_print.html", {"recibo": recibo})


def recibo_pdf(request, recibo_id):
    """
    Genera el PDF del recibo.
    Soporta WeasyPrint (mejor calidad) y xhtml2pdf (más compatible).
    """
    recibo = get_recibo_by_id(recibo_id)

    if not recibo:
        raise Http404("Recibo no encontrado")

    try:
        return generate_pdf(
            template_name="recibo_print.html",
            context={"recibo": recibo},
            filename=f"recibo_{recibo_id}.pdf",
        )
    except RuntimeError as e:
        logger.error(f"Error generando PDF: {e}")
        return HttpResponse(
            "Error: No hay motor de PDF disponible. Contacte al administrador.",
            status=500,
        )


def pdf_status(request):
    """
    Vista de diagnóstico para verificar el estado de los motores PDF.
    Solo disponible en modo DEBUG.
    """
    status = test_pdf_engines()
    return JsonResponse(status)
