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

        LÓGICA: Calcula el costo total por item = (peso × precio_por_libra) + costo_envio
        TOTAL = Suma de todos los costos de items

        Args:
            cliente_codigo: Código del cliente
            items_data: Lista de items, cada uno con:
                - tracking_id (requerido)
                - peso_libra (requerido)
                - precio_libra (requerido)
                - empresa_envio (opcional)
                - num_paquetes (opcional)
                - costo_envio (opcional, costo adicional de envío)

        Returns:
            Diccionario con el recibo creado (incluye id)
        """
        # Verificar que el cliente existe
        cliente = get_cliente_by_codigo(cliente_codigo)
        if not cliente:
            raise ValueError(f"Cliente con código {cliente_codigo} no encontrado")

        # Inicializar totales
        subtotal_flete = Decimal("0.00")
        subtotal_envios = Decimal("0.00")
        total_final = Decimal("0.00")

        # Preparar detalles y calcular totales
        detalles_preparados = []

        for item in items_data:
            peso = Decimal(str(item.get("peso_libra", 0)))
            precio_lb = Decimal(str(item.get("precio_libra", 0)))
            costo_envio = Decimal(str(item.get("costo_envio", 0)))

            # Calcular costo base del flete
            costo_flete = peso * precio_lb

            # Costo total del item = flete + costo_envio
            costo_total_item = costo_flete + costo_envio

            detalle = {
                "tracking_id": item.get("tracking_id", ""),
                "tienda": item.get("tienda", ""),
                "wr": item.get("wr", ""),
                "peso_libras": float(peso),
                "precio_por_libra": float(precio_lb),
                "total_flete": float(costo_flete),
                "empresa_envio": item.get("empresa_envio", ""),
                "num_paquetes": int(item.get("num_paquetes", 0)),
                "costo_envio": float(costo_envio),
            }

            detalles_preparados.append(detalle)

            # Acumular totales
            subtotal_flete += costo_flete
            subtotal_envios += costo_envio
            total_final += costo_total_item

        # Crear recibo en Supabase
        totales = {
            "subtotal_flete": float(subtotal_flete),
            "subtotal_envios": float(subtotal_envios),
            "total": float(total_final),
        }

        recibo = create_recibo(cliente_codigo, totales)

        if not recibo:
            raise ValueError("Error al crear el recibo en Supabase")

        # Crear detalles del recibo
        for detalle in detalles_preparados:
            create_detalle_recibo(recibo["id"], detalle)

        return recibo
