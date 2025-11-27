from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django_weasyprint import WeasyTemplateResponseMixin
from django_weasyprint.views import WeasyTemplateResponse
from .models import Clientes, Recibo
from .forms import ClienteForm
from .services import ClienteService, ReciboService
import json

# --- Vistas de Clientes ---


def home(request):
    clientes = Clientes.objects.all()
    return render(request, "gestionLista.html", {"listado": clientes})


def registro(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente registrado exitosamente!")
            return redirect("home")
        else:
            messages.warning(request, "Error en el formulario. Verifique los datos.")
    else:
        form = ClienteForm()

    return render(request, "registro.html", {"form": form})


def edicionCliente(request, codigo):
    cliente = get_object_or_404(Clientes, codigo=codigo)
    return render(request, "edicionCliente.html", {"cliente": cliente})


def editarCliente(request):
    if request.method == "POST":
        codigo = request.POST.get("txtCodigo")
        cliente = get_object_or_404(Clientes, codigo=codigo)

        cliente.Nombre_Apellido = request.POST.get("txtNombreApellido")
        cliente.Direccion = request.POST.get("txtDireccion")
        cliente.Ciudad = request.POST.get("txtCiudad")
        cliente.Telefono = request.POST.get("txtTelefono")
        cliente.email = request.POST.get("txtEmail")
        cliente.save()

        messages.success(request, "Cliente actualizado!")
        return redirect("home")


def eliminarCliente(request, codigo):
    cliente = get_object_or_404(Clientes, codigo=codigo)
    cliente.delete()
    messages.success(request, "Cliente eliminado!")
    return redirect("home")


# --- Vistas de Recibos (Nueva Lógica) ---


def recibo_view(request):
    """Vista principal para generar recibos"""
    return render(request, "recibo_app.html")


def buscar_cliente_api(request):
    """API para buscar cliente por código/cédula via AJAX"""
    codigo = request.GET.get("codigo")
    cliente = ClienteService.buscar_por_codigo(codigo)

    if cliente:
        data = {
            "found": True,
            "nombre": cliente.Nombre_Apellido,
            "direccion": cliente.Direccion,
            "telefono": cliente.Telefono,
            "email": cliente.email,
        }
    else:
        data = {"found": False}

    return JsonResponse(data)


def guardar_recibo_api(request):
    """API para guardar el recibo generado"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cliente_codigo = data.get("cliente_codigo")
            items = data.get("items")

            recibo = ReciboService.crear_recibo(cliente_codigo, items)

            return JsonResponse({"success": True, "recibo_id": recibo.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Método no permitido"})


def ver_recibo(request, recibo_id):
    recibo = get_object_or_404(Recibo, id=recibo_id)
    return render(request, "recibo_print.html", {"recibo": recibo})


def recibo_pdf(request, recibo_id):
    recibo = get_object_or_404(Recibo, id=recibo_id)
    return WeasyTemplateResponse(
        request=request,
        template="recibo_print.html",
        context={"recibo": recibo},
        filename=f"recibo_{recibo_id}.pdf",
    )
