from django.db import models

# Create your models here.

class Clientes(models.Model):
    codigo=models.CharField(primary_key=True,max_length=15)
from django.db import models

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
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Recibo #{self.id} - {self.cliente.Nombre_Apellido}"

class DetalleRecibo(models.Model):
    recibo = models.ForeignKey(Recibo, related_name='detalles', on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)