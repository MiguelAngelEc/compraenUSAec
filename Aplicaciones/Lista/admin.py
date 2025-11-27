from django.contrib import admin
from .models import Clientes, Recibo, DetalleRecibo

class DetalleReciboInline(admin.TabularInline):
    model = DetalleRecibo
    extra = 0
    fields = ('tracking_id', 'tienda', 'wr', 'peso_libras', 'precio_por_libra', 'total_flete', 'precio_producto', 'abono', 'saldo_producto')
    readonly_fields = ('total_flete', 'saldo_producto')

@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'subtotal_flete', 'subtotal_productos', 'total')
    list_filter = ('fecha',)
    search_fields = ('cliente__Nombre_Apellido', 'cliente__codigo')
    readonly_fields = ('fecha', 'subtotal_productos', 'total_abonos', 'subtotal_flete', 'total')
    inlines = [DetalleReciboInline]

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'Nombre_Apellido', 'Ciudad', 'Telefono')
    search_fields = ('codigo', 'Nombre_Apellido')