"""
Supabase Client para Django - CompraEnUSAec
============================================

Cliente de Supabase configurado para operaciones CRUD con las tablas:
- clientes: Datos de clientes
- recibos: Cabecera de recibos
- detalle_recibo: Detalles de cada recibo

IMPORTANTE: Este módulo usa SERVICE_ROLE_KEY para bypass de RLS.
"""

import os
from functools import lru_cache
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

# Cargar variables de entorno
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class SupabaseClientError(Exception):
    """Excepción personalizada para errores del cliente Supabase."""

    pass


@lru_cache(maxsize=1)
def get_supabase_client():
    """
    Obtiene una instancia singleton del cliente Supabase con SERVICE_ROLE_KEY.

    Usa SERVICE_ROLE_KEY para bypass de Row Level Security (RLS).
    Esto es necesario para operaciones del servidor.

    Returns:
        supabase.Client: Cliente Supabase configurado

    Raises:
        SupabaseClientError: Si faltan variables de entorno
    """
    try:
        from supabase import create_client, Client
    except ImportError:
        raise SupabaseClientError(
            "El paquete 'supabase' no está instalado. "
            "Instálelo con: pip install supabase"
        )

    url: Optional[str] = os.environ.get("SUPABASE_URL")
    # Usar SERVICE_ROLE_KEY para operaciones del servidor (bypass RLS)
    key: Optional[str] = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    # Fallback a ANON_KEY si no hay SERVICE_ROLE_KEY
    if not key:
        key = os.environ.get("SUPABASE_ANON_KEY")

    if not url:
        raise SupabaseClientError(
            "SUPABASE_URL no está configurada. " "Agréguela al archivo .env"
        )

    if not key:
        raise SupabaseClientError(
            "SUPABASE_SERVICE_ROLE_KEY o SUPABASE_ANON_KEY no están configuradas. "
            "Agréguela al archivo .env"
        )

    return create_client(url, key)


# Cliente pre-inicializado (será None si hay error)
try:
    supabase = get_supabase_client()
except SupabaseClientError as e:
    supabase = None
    print(f"⚠️ Supabase no disponible: {e}")


# =============================================================================
# OPERACIONES CRUD PARA CLIENTES
# =============================================================================


def get_all_clientes() -> List[Dict[str, Any]]:
    """
    Obtiene todos los clientes de Supabase.

    Returns:
        Lista de diccionarios con datos de clientes
    """
    client = get_supabase_client()
    response = client.table("clientes").select("*").order("codigo").execute()
    return response.data or []


def get_cliente_by_codigo(codigo: str) -> Optional[Dict[str, Any]]:
    """
    Busca un cliente por su código/cédula.

    Args:
        codigo: Código o cédula del cliente

    Returns:
        Diccionario con datos del cliente o None si no existe
    """
    client = get_supabase_client()
    response = (
        client.table("clientes").select("*").eq("codigo", codigo).limit(1).execute()
    )
    return response.data[0] if response.data else None


def create_cliente(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea un nuevo cliente en Supabase.

    Args:
        data: Diccionario con campos del cliente:
            - codigo (str): Cédula/código único
            - nombre_apellido (str): Nombre completo
            - direccion (str): Dirección
            - ciudad (str): Ciudad
            - telefono (str): Teléfono
            - email (str): Correo electrónico

    Returns:
        Diccionario con el cliente creado
    """
    client = get_supabase_client()
    # Asegurar nombres snake_case para Supabase
    cliente_data = {
        "codigo": data.get("codigo"),
        "nombre_apellido": data.get("nombre_apellido") or data.get("Nombre_Apellido"),
        "direccion": data.get("direccion") or data.get("Direccion"),
        "ciudad": data.get("ciudad") or data.get("Ciudad"),
        "telefono": data.get("telefono") or data.get("Telefono"),
        "email": data.get("email"),
    }
    response = client.table("clientes").insert(cliente_data).execute()
    return response.data[0] if response.data else None


def update_cliente(codigo: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Actualiza un cliente existente.

    Args:
        codigo: Código del cliente a actualizar
        data: Diccionario con campos a actualizar

    Returns:
        Diccionario con el cliente actualizado
    """
    client = get_supabase_client()
    # Convertir nombres de campos si vienen en formato Django
    update_data = {}
    field_mapping = {
        "Nombre_Apellido": "nombre_apellido",
        "Direccion": "direccion",
        "Ciudad": "ciudad",
        "Telefono": "telefono",
    }

    for key, value in data.items():
        # Usar el nombre snake_case si existe mapeo
        new_key = field_mapping.get(key, key)
        update_data[new_key] = value

    response = (
        client.table("clientes").update(update_data).eq("codigo", codigo).execute()
    )
    return response.data[0] if response.data else None


def delete_cliente(codigo: str) -> bool:
    """
    Elimina un cliente por su código.

    Args:
        codigo: Código del cliente a eliminar

    Returns:
        True si se eliminó correctamente
    """
    client = get_supabase_client()
    response = client.table("clientes").delete().eq("codigo", codigo).execute()
    return len(response.data) > 0 if response.data else False


# =============================================================================
# OPERACIONES CRUD PARA RECIBOS
# =============================================================================


def create_recibo(cliente_codigo: str, totales: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea un nuevo recibo en Supabase.

    Args:
        cliente_codigo: Código del cliente
        totales: Diccionario con totales:
            - subtotal_flete
            - subtotal_envios
            - total

    Returns:
        Diccionario con el recibo creado (incluye id)
    """
    client = get_supabase_client()
    recibo_data = {
        "cliente_codigo": cliente_codigo,
        "subtotal_flete": float(totales.get("subtotal_flete", 0)),
        "subtotal_envios": float(totales.get("subtotal_envios", 0)),
        "total": float(totales.get("total", 0)),
    }
    response = client.table("recibos").insert(recibo_data).execute()
    return response.data[0] if response.data else None


def create_detalle_recibo(recibo_id: int, detalle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea un detalle de recibo en Supabase.

    Args:
        recibo_id: ID del recibo padre
        detalle: Diccionario con datos del detalle:
            - tracking_id
            - tienda
            - wr
            - peso_libras
            - precio_por_libra
            - total_flete
            - empresa_envio
            - num_paquetes
            - costo_envio

    Returns:
        Diccionario con el detalle creado
    """
    client = get_supabase_client()
    detalle_data = {
        "recibo_id": recibo_id,
        "tracking_id": detalle.get("tracking_id", ""),
        "tienda": detalle.get("tienda", ""),
        "wr": detalle.get("wr", ""),
        "peso_libras": float(detalle.get("peso_libras", 0)),
        "precio_por_libra": float(detalle.get("precio_por_libra", 0)),
        "total_flete": float(detalle.get("total_flete", 0)),
        "empresa_envio": detalle.get("empresa_envio", ""),
        "num_paquetes": int(detalle.get("num_paquetes", 0)),
        "costo_envio": float(detalle.get("costo_envio", 0)),
    }
    response = client.table("detalle_recibo").insert(detalle_data).execute()
    return response.data[0] if response.data else None


def get_recibo_by_id(recibo_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un recibo por su ID, incluyendo cliente y detalles.

    Args:
        recibo_id: ID del recibo

    Returns:
        Diccionario con el recibo, cliente y detalles
    """
    client = get_supabase_client()

    # Obtener recibo con datos del cliente
    response = (
        client.table("recibos")
        .select("*, clientes(*)")
        .eq("id", recibo_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    recibo = response.data[0]

    if isinstance(recibo.get("fecha"), str):
        recibo["fecha"] = datetime.fromisoformat(recibo["fecha"])

    # Obtener detalles del recibo
    detalles_response = (
        client.table("detalle_recibo")
        .select("*")
        .eq("recibo_id", recibo_id)
        .order("id")
        .execute()
    )

    recibo["detalles"] = detalles_response.data or []

    return recibo


def get_recibos_by_cliente(cliente_codigo: str) -> List[Dict[str, Any]]:
    """
    Obtiene todos los recibos de un cliente.

    Args:
        cliente_codigo: Código del cliente

    Returns:
        Lista de recibos
    """
    client = get_supabase_client()
    response = (
        client.table("recibos")
        .select("*")
        .eq("cliente_codigo", cliente_codigo)
        .order("fecha", desc=True)
        .execute()
    )

    data = response.data or []

    for r in data:
        if isinstance(r["fecha"], str):
            # Convierte ISO 8601 a datetime
            r["fecha"] = datetime.fromisoformat(r["fecha"])

    return data
