from .models import Clientes, Recibo, DetalleRecibo
from django.db import transaction
from decimal import Decimal

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
        """
        Crea un recibo para servicio de courier.
        
        LÓGICA PRINCIPAL: El costo es por libras (peso × precio_por_libra)
        SECUNDARIO: Si hay productos comprados, calcular saldo (precio - abono)
        
        items_data debe contener:
        - tracking_id (requerido)
        - tienda (opcional)
        - wr (opcional)
        - peso_libras (requerido para calcular flete)
        - precio_por_libra (requerido para calcular flete)
        - precio_producto (opcional, si se compró producto)
        - abono (opcional, si hubo adelanto)
        """
        cliente = Clientes.objects.get(codigo=cliente_codigo)
        
        # Inicializar totales
        subtotal_productos = Decimal('0.00')
        total_abonos = Decimal('0.00')
        subtotal_flete = Decimal('0.00')
        
        # Crear recibo
        recibo = Recibo.objects.create(cliente=cliente)
        
        # Crear detalles y calcular totales
        for item in items_data:
            peso = Decimal(str(item.get('peso_libra', 0)))
            precio_lb = Decimal(str(item.get('precio_libra', 0)))
            precio_prod = Decimal(str(item.get('precio', 0)))
            abono = Decimal(str(item.get('abono', 0)))
            
            # Crear detalle (el método save() calculará total_flete y saldo_producto)
            detalle = DetalleRecibo.objects.create(
                recibo=recibo,
                tracking_id=item.get('tracking_id', ''),
                tienda=item.get('tienda', ''),
                wr=item.get('wr', ''),
                peso_libras=peso,
                precio_por_libra=precio_lb,
                precio_producto=precio_prod,
                abono=abono
            )
            
            # Acumular totales
            subtotal_flete += detalle.total_flete  # PRINCIPAL: costo del flete
            subtotal_productos += detalle.saldo_producto  # SECUNDARIO: saldo de productos
            total_abonos += abono
        
        # Calcular total final
        # TOTAL = Flete + Saldo de productos pendientes
        total_final = subtotal_flete + subtotal_productos
        
        # Actualizar recibo con totales
        recibo.subtotal_productos = subtotal_productos
        recibo.total_abonos = total_abonos
        recibo.subtotal_flete = subtotal_flete
        recibo.total = total_final
        recibo.save()
        
        return recibo
