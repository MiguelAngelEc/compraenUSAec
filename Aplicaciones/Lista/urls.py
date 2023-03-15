from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('formularioClientes/', views.formularioClientes, name='formularioClientes'),
    path('reciboCliente/', views.reciboCliente, name='reciboCliente'),
    path('edicionCliente/<codigo>', views.edicionCliente),
    path('editarCliente/', views.editarCliente),
    path('eliminarCliente/<codigo>', views.eliminarCliente),
    path('registro/', views.registro),
    path('buscar-cliente/', views.buscar_cliente, name='buscar_cliente'),
]
