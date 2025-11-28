import os
import json
from textwrap import dedent

try:
    import requests
except ImportError:
    raise SystemExit('requests package is required. Install with pip install requests')

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

SQL = dedent("""
CREATE TABLE IF NOT EXISTS \"Lista_clientes\" (
    codigo VARCHAR(15) PRIMARY KEY,
    \"Nombre_Apellido\" VARCHAR(50) NOT NULL,
    \"Direccion\" VARCHAR(50) NOT NULL,
    \"Ciudad\" VARCHAR(15) NOT NULL,
    \"Telefono\" VARCHAR(15) NOT NULL,
    email VARCHAR(254) NOT NULL
);

CREATE TABLE IF NOT EXISTS \"Lista_recibo\" (
    id BIGSERIAL PRIMARY KEY,
    cliente_id VARCHAR(15) REFERENCES \"Lista_clientes\"(codigo) ON DELETE CASCADE,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    subtotal_productos DECIMAL(10,2) DEFAULT 0.00,
    total_abonos DECIMAL(10,2) DEFAULT 0.00,
    subtotal_flete DECIMAL(10,2) DEFAULT 0.00,
    total DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS \"Lista_detallerecibo\" (
    id BIGSERIAL PRIMARY KEY,
    recibo_id BIGINT REFERENCES \"Lista_recibo\"(id) ON DELETE CASCADE,
    tracking_id VARCHAR(100) NOT NULL,
    tienda VARCHAR(100),
    wr VARCHAR(50),
    precio_producto DECIMAL(10,2) DEFAULT 0.00,
    abono DECIMAL(10,2) DEFAULT 0.00,
    saldo_producto DECIMAL(10,2) DEFAULT 0.00,
    peso_libras DECIMAL(10,2) DEFAULT 0.00,
    precio_por_libra DECIMAL(10,2) DEFAULT 0.00,
    total_flete DECIMAL(10,2) DEFAULT 0.00
);

CREATE INDEX IF NOT EXISTS idx_recibo_cliente ON \"Lista_recibo\"(cliente_id);
CREATE INDEX IF NOT EXISTS idx_recibo_fecha ON \"Lista_recibo\"(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_detalle_recibo ON \"Lista_detallerecibo\"(recibo_id);
""")


def main():
    if load_dotenv:
        load_dotenv()

    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

    if not url:
        raise SystemExit('SUPABASE_URL is not set')

    if not key:
        raise SystemExit('SUPABASE_SERVICE_ROLE_KEY is not set')

    endpoint = f"{url}/sql/v1"
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }

    response = requests.post(endpoint, headers=headers, json={'q': SQL}, timeout=30)
    print('Status:', response.status_code)
    print('Response:', response.text)


if __name__ == '__main__':
    main()
