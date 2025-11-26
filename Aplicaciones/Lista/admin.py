from django.contrib import admin
from .models import Clientes, Recibo, DetalleRecibo

class DetalleReciboInline(admin.TabularInline):
    model = DetalleRecibo
    extra = 0

@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'total')
    list_filter = ('fecha',)
    search_fields = ('cliente__Nombre_Apellido', 'cliente__codigo')
    inlines = [DetalleReciboInline]

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'Nombre_Apellido', 'Ciudad', 'Telefono')
    search_fields = ('codigo', 'Nombre_Apellido')

# admin.site.register(Clientes, ClientesAdmin) # Ya registrado con decorador