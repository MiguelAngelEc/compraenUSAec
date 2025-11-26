from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('edicionCliente/<codigo>', views.edicionCliente, name='edicionCliente'),
    path('editarCliente/', views.editarCliente, name='editarCliente'),
    path('eliminarCliente/<codigo>', views.eliminarCliente, name='eliminarCliente'),
    
    # Rutas de Recibos
    path('recibo/', views.recibo_view, name='recibo_view'),
    path('recibo/<int:recibo_id>/', views.ver_recibo, name='ver_recibo'),
    path('api/buscar-cliente/', views.buscar_cliente_api, name='buscar_cliente_api'),
    path('api/guardar-recibo/', views.guardar_recibo_api, name='guardar_recibo_api'),
]
