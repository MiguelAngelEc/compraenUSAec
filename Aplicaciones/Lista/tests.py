from django.test import TestCase
from decimal import Decimal
from unittest.mock import patch, MagicMock
from .services import ReciboService


class ReciboServiceTestCase(TestCase):
    """Tests para ReciboService con nueva lógica de envío."""

    def setUp(self):
        self.cliente_codigo = "1234567890"

    @patch("Aplicaciones.Lista.services.get_cliente_by_codigo")
    @patch("Aplicaciones.Lista.services.create_recibo")
    @patch("Aplicaciones.Lista.services.create_detalle_recibo")
    def test_crear_recibo_con_costo_envio(
        self, mock_create_detalle, mock_create_recibo, mock_get_cliente
    ):
        """Test creación de recibo usando costo_envio directo."""
        # Mock cliente
        mock_get_cliente.return_value = {
            "codigo": self.cliente_codigo,
            "nombre": "Test",
        }

        # Mock recibo creado
        mock_recibo = {"id": 1}
        mock_create_recibo.return_value = mock_recibo

        # Items con costo_envio
        items = [
            {
                "tracking_id": "TRK123",
                "peso_libra": 5.0,
                "precio_libra": 2.0,
                "empresa_envio": "DHL",
                "num_paquetes": 2,
                "costo_envio": 15.0,
                "precio": 100.0,
                "abono": 20.0,
            }
        ]

        result = ReciboService.crear_recibo(self.cliente_codigo, items)

        # Verificar que se creó el recibo con subtotal_envios
        mock_create_recibo.assert_called_once()
        call_args = mock_create_recibo.call_args[0][0]
        self.assertEqual(call_args["subtotal_envios"], 15.0)
        self.assertEqual(call_args["subtotal_productos"], 80.0)  # 100 - 20
        self.assertEqual(call_args["total_abonos"], 20.0)
        self.assertEqual(call_args["total"], 95.0)  # 15 + 80

        # Verificar detalle
        mock_create_detalle.assert_called_once()
        detalle_args = mock_create_detalle.call_args[0][1]
        self.assertEqual(detalle_args["costo_envio"], 15.0)
        self.assertEqual(detalle_args["empresa_envio"], "DHL")
        self.assertEqual(detalle_args["num_paquetes"], 2)

    @patch("Aplicaciones.Lista.services.get_cliente_by_codigo")
    @patch("Aplicaciones.Lista.services.create_recibo")
    @patch("Aplicaciones.Lista.services.create_detalle_recibo")
    def test_crear_recibo_sin_costo_envio_fallback(
        self, mock_create_detalle, mock_create_recibo, mock_get_cliente
    ):
        """Test creación de recibo sin costo_envio, usando fallback de flete."""
        mock_get_cliente.return_value = {
            "codigo": self.cliente_codigo,
            "nombre": "Test",
        }
        mock_recibo = {"id": 1}
        mock_create_recibo.return_value = mock_recibo

        # Items sin costo_envio
        items = [
            {
                "tracking_id": "TRK456",
                "peso_libra": 10.0,
                "precio_libra": 3.0,
                "empresa_envio": "",
                "num_paquetes": 1,
                "costo_envio": 0.0,
                "precio": 50.0,
                "abono": 10.0,
            }
        ]

        result = ReciboService.crear_recibo(self.cliente_codigo, items)

        # Verificar subtotal_flete usado como subtotal_envios
        call_args = mock_create_recibo.call_args[0][0]
        self.assertEqual(call_args["subtotal_envios"], 30.0)  # 10 * 3
        self.assertEqual(call_args["subtotal_productos"], 40.0)  # 50 - 10
        self.assertEqual(call_args["total"], 70.0)  # 30 + 40

    @patch("Aplicaciones.Lista.services.get_cliente_by_codigo")
    @patch("Aplicaciones.Lista.services.create_recibo")
    @patch("Aplicaciones.Lista.services.create_detalle_recibo")
    def test_crear_recibo_sin_productos(
        self, mock_create_detalle, mock_create_recibo, mock_get_cliente
    ):
        """Test creación de recibo solo con envío, sin productos."""
        mock_get_cliente.return_value = {
            "codigo": self.cliente_codigo,
            "nombre": "Test",
        }
        mock_recibo = {"id": 1}
        mock_create_recibo.return_value = mock_recibo

        items = [
            {
                "tracking_id": "TRK789",
                "peso_libra": 2.0,
                "precio_libra": 1.0,
                "empresa_envio": "FedEx",
                "num_paquetes": 1,
                "costo_envio": 5.0,
                "precio": 0.0,
                "abono": 0.0,
            }
        ]

        result = ReciboService.crear_recibo(self.cliente_codigo, items)

        call_args = mock_create_recibo.call_args[0][0]
        self.assertEqual(call_args["subtotal_envios"], 5.0)
        self.assertEqual(call_args["subtotal_productos"], 0.0)
        self.assertEqual(call_args["total_abonos"], 0.0)
        self.assertEqual(call_args["total"], 5.0)

    def test_crear_recibo_cliente_no_existe(self):
        """Test error cuando cliente no existe."""
        with patch(
            "Aplicaciones.Lista.services.get_cliente_by_codigo", return_value=None
        ):
            with self.assertRaises(ValueError) as cm:
                ReciboService.crear_recibo("INVALID", [])
            self.assertIn("no encontrado", str(cm.exception))
