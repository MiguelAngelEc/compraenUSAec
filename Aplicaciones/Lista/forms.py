from django import forms
from .models import Clientes, Recibo, DetalleRecibo

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['codigo', 'Nombre_Apellido', 'Direccion', 'Ciudad', 'Telefono', 'email']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula/Código'}),
            'Nombre_Apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Completo'}),
            'Direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'Ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'Telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}),
        }

class DetalleReciboForm(forms.ModelForm):
    class Meta:
        model = DetalleRecibo
        fields = ['descripcion', 'cantidad', 'precio_unitario']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción del producto'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }
