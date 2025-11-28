"""
Services para CompraEnUSAec
===========================

Servicios de negocio que usan Supabase como backend.
"""

from decimal import Decimal
from typing import Dict, Any, List
from .supabase_client import (
    get_cliente_by_codigo,
    create_recibo,
    create_detalle_recibo,
)


class ClienteService:
    """Servicio para operaciones de clientes."""

    @staticmethod
    def buscar_por_codigo(codigo: str) -> Dict[str, Any]:
        """
        Busca un cliente por su código.

        Args:
            codigo: Código/cédula del cliente

        Returns:
            Diccionario con datos del cliente o None
        """
        return get_cliente_by_codigo(codigo)


class ReciboService:
    """Servicio para operaciones de recibos."""

    @staticmethod
    def crear_recibo(
        cliente_codigo: str, items_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Crea un recibo completo con sus detalles en Supabase.

        LÓGICA PRINCIPAL: El costo es por libras (peso × precio_por_libra)
        SECUNDARIO: Si hay productos comprados, calcular saldo (precio - abono)

        Args:
            cliente_codigo: Código del cliente
            items_data: Lista de items, cada uno con:
                - tracking_id (requerido)
                - tienda (opcional)
                - wr (opcional)
                - peso_libra (requerido para calcular flete)
                - precio_libra (requerido para calcular flete)
                - precio (opcional, si se compró producto)
                - abono (opcional, si hubo adelanto)

        Returns:
            Diccionario con el recibo creado (incluye id)
        """
        # Verificar que el cliente existe
        cliente = get_cliente_by_codigo(cliente_codigo)
        if not cliente:
            raise ValueError(f"Cliente con código {cliente_codigo} no encontrado")

        # Inicializar totales
        subtotal_productos = Decimal("0.00")
        total_abonos = Decimal("0.00")
        subtotal_flete = Decimal("0.00")

        # Preparar detalles y calcular totales
        detalles_preparados = []

        for item in items_data:
            peso = Decimal(str(item.get("peso_libra", 0)))
            precio_lb = Decimal(str(item.get("precio_libra", 0)))
            precio_prod = Decimal(str(item.get("precio", 0)))
            abono = Decimal(str(item.get("abono", 0)))

            # Calcular valores
            total_flete_item = peso * precio_lb
            saldo_producto = precio_prod - abono

            detalle = {
                "tracking_id": item.get("tracking_id", ""),
                "tienda": item.get("tienda", ""),
                "wr": item.get("wr", ""),
                "peso_libras": float(peso),
                "precio_por_libra": float(precio_lb),
                "total_flete": float(total_flete_item),
                "precio_producto": float(precio_prod),
                "abono": float(abono),
                "saldo_producto": float(saldo_producto),
            }

            detalles_preparados.append(detalle)

            # Acumular totales
            subtotal_flete += total_flete_item
            subtotal_productos += saldo_producto
            total_abonos += abono

        # Calcular total final
        # TOTAL = Flete + Saldo de productos pendientes
        total_final = subtotal_flete + subtotal_productos

        # Crear recibo en Supabase
        totales = {
            "subtotal_productos": float(subtotal_productos),
            "total_abonos": float(total_abonos),
            "subtotal_flete": float(subtotal_flete),
            "total": float(total_final),
        }

        recibo = create_recibo(cliente_codigo, totales)

        if not recibo:
            raise ValueError("Error al crear el recibo en Supabase")

        # Crear detalles del recibo
        for detalle in detalles_preparados:
            create_detalle_recibo(recibo["id"], detalle)

        return recibo
