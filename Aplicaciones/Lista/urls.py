from django.urls import path
from . import views

urlpatterns = [
    # --- Clientes ---
    path("", views.home, name="home"),
    path("registro/", views.registro, name="registro"),
    path("edicionCliente/<codigo>", views.edicionCliente, name="edicionCliente"),
    path("editarCliente/", views.editarCliente, name="editarCliente"),
    path("eliminarCliente/<codigo>", views.eliminarCliente, name="eliminarCliente"),
    # --- Recibos ---
    path("recibo/", views.recibo_view, name="recibo_view"),
    path("recibo/<int:recibo_id>/", views.ver_recibo, name="ver_recibo"),
    path("recibo/<int:recibo_id>/pdf/", views.recibo_pdf, name="recibo_pdf"),
    # --- APIs ---
    path("api/buscar-cliente/", views.buscar_cliente_api, name="buscar_cliente_api"),
    path("api/guardar-recibo/", views.guardar_recibo_api, name="guardar_recibo_api"),
    # --- Diagnóstico (solo para debugging) ---
    path("api/pdf-status/", views.pdf_status, name="pdf_status"),
]
