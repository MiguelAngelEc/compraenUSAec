from django import forms
from .models import Clientes, DetalleRecibo

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['codigo', 'Nombre_Apellido', 'Direccion', 'Ciudad', 'Telefono', 'email']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500'}),
            'Nombre_Apellido': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500'}),
            'Direccion': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500'}),
            'Ciudad': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500'}),
            'Telefono': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500'}),
        }

class DetalleReciboForm(forms.ModelForm):
    class Meta:
        model = DetalleRecibo
        fields = ['tracking_id', 'tienda', 'wr', 'peso_libras', 'precio_por_libra', 'precio_producto', 'abono']
        widgets = {
            'tracking_id': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Tracking ID'}),
            'tienda': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Tienda'}),
            'wr': forms.TextInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'WR'}),
            'peso_libras': forms.NumberInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500', 'step': '0.01', 'placeholder': '0.00'}),
            'precio_por_libra': forms.NumberInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500', 'step': '0.01', 'placeholder': '0.00'}),
            'precio_producto': forms.NumberInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500', 'step': '0.01', 'placeholder': '0.00'}),
            'abono': forms.NumberInput(attrs={'class': 'w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500', 'step': '0.01', 'placeholder': '0.00'}),
        }
