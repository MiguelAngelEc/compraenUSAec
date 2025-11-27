from django.db import models
from decimal import Decimal

# Create your models here.

class Clientes(models.Model):
    codigo=models.CharField(primary_key=True,max_length=15)
    Nombre_Apellido=models.CharField(max_length=50)
    Direccion=models.CharField(max_length=50)
    Ciudad=models.CharField(max_length=15)
    Telefono=models.CharField(max_length=15)
    email=models.EmailField()
    
    def __str__(self):
        texto = "{0} ({1})"
        return texto.format(self.Nombre_Apellido, self.codigo)

class Recibo(models.Model):
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    subtotal_productos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Subtotal de productos comprados")
    total_abonos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total de abonos realizados")
    subtotal_flete = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Costo total del flete (peso × precio/lb)")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total final a pagar")

    def __str__(self):
        return f"Recibo #{self.id} - {self.cliente.Nombre_Apellido}"
    
    class Meta:
        ordering = ['-fecha']

class DetalleRecibo(models.Model):
    recibo = models.ForeignKey(Recibo, related_name='detalles', on_delete=models.CASCADE)
    tracking_id = models.CharField(max_length=100, verbose_name="Tracking ID")
    tienda = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tienda")
    wr = models.CharField(max_length=50, blank=True, null=True, verbose_name="WR")
    
    # Datos del producto (si se compró por el cliente)
    precio_producto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Precio del Producto")
    abono = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Abono")
    saldo_producto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Saldo del Producto")
    
    # Datos del flete (LO PRINCIPAL)
    peso_libras = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Peso en Libras")
    precio_por_libra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Precio por Libra")
    total_flete = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Flete")

    def save(self, *args, **kwargs):
        # Calcular saldo del producto (si aplica)
        self.saldo_producto = self.precio_producto - self.abono
        
        # CÁLCULO PRINCIPAL: Total del flete = Peso × Precio por libra
        self.total_flete = self.peso_libras * self.precio_por_libra
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.tracking_id} - {self.peso_libras}lb × ${self.precio_por_libra} = ${self.total_flete}"
    
    class Meta:
        ordering = ['id']
        verbose_name = "Detalle de Recibo"
        verbose_name_plural = "Detalles de Recibo"