from .models import Clientes, Recibo, DetalleRecibo
from django.db import transaction

class ClienteService:
    @staticmethod
    def buscar_por_codigo(codigo):
        return Clientes.objects.filter(codigo=codigo).first()

    @staticmethod
    def crear_cliente(data):
        return Clientes.objects.create(**data)

    @staticmethod
    def actualizar_cliente(codigo, data):
        cliente = Clientes.objects.get(codigo=codigo)
        for key, value in data.items():
            setattr(cliente, key, value)
        cliente.save()
        return cliente

class ReciboService:
    @staticmethod
    @transaction.atomic
    def crear_recibo(cliente_codigo, items_data):
        cliente = Clientes.objects.get(codigo=cliente_codigo)
        recibo = Recibo.objects.create(cliente=cliente)
        
        total = 0
        for item in items_data:
            detalle = DetalleRecibo(
                recibo=recibo,
                descripcion=item['descripcion'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_unitario']
            )
            detalle.save() # Calcula subtotal en save()
            total += detalle.subtotal
            
        recibo.total = total
        recibo.save()
        return recibo
