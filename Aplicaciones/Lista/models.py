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
        texto = "{0}({1})"
        return texto.format(self.Nombre_Apellido, self.codigo)    
    
    
    
    

    