from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Clientes
from django.contrib import messages

# Create your views here.

def home(request):
       clientesListados = Clientes.objects.all()
       # Despliega informacion a la pagina principal
       return render(request, "gestionLista.html", {"listado": clientesListados})

def formularioClientes(request):
    # código de tu vista aquí
    return render(request, 'formularioClientes.html')

def reciboCliente(request):
    # código de tu vista aquí
    return render(request, 'reciboCliente.html')

def registro(request):
    if request.method == 'POST':
        codigo = request.POST.get('txtCodigo')
        nombre = request.POST.get('txtNombreApellido')
        direccion = request.POST.get('txtDireccion')
        ciudad = request.POST.get('txtCiudad')
        telefono = request.POST.get('txtTelefono')
        email = request.POST.get('txtEmail')
        
        # Comprueba si ya existe un registro con el mismo código
        if Clientes.objects.filter(codigo=codigo).exists():
            messages.warning(request, 'Ya existe un cliente con ese código')
        else:
            # Crea el registro en la base de datos
            listado = Clientes.objects.create(codigo=codigo, Nombre_Apellido=nombre, Direccion=direccion, Ciudad=ciudad, Telefono=telefono, email=email)
            messages.success(request, 'Cliente Ingresado!!')
            
        return redirect('/')
    
    # Si no se ha enviado un formulario, renderiza la plantilla del formulario
    return render(request, 'registro.html')

#Codigo para edicion
def edicionCliente(request, codigo):
       listado = Clientes.objects.get(codigo=codigo)
       return render(request, "edicionCliente.html", {"listado": listado})

def editarCliente(request):
       codigo=request.POST['txtCodigo']
       nombre=request.POST['txtNombreApellido']
       direccion=request.POST['txtDireccion']
       ciudad=request.POST['txtCiudad']
       telefono=request.POST['txtTelefono']
       email=request.POST['txtEmail']
       
       listado = Clientes.objects.get(codigo=codigo)
       listado.Nombre_Apellido = nombre
       listado.Direccion = direccion
       listado.Ciudad = ciudad
       listado.Telefono = telefono
       listado.email = email
       listado.save()
       
       return redirect('/')

#Codigo para eliminar
def eliminarCliente(request, codigo):
       listado = Clientes.objects.get(codigo=codigo)
       listado.delete()
       messages.success(request, 'Cliente Eliminado!!')
       return redirect('/')

# Codigo para Buscar Cliente
def buscar_cliente(request):
    if request.method == 'POST':
        codigo = request.POST['codigo']
        cliente = Clientes.objects.filter(codigo=codigo).first()
        if cliente:
            return render(request, 'reciboCliente.html', {'cliente': cliente})
        else:
            mensaje = f"No se encontró un cliente con el código {codigo}."
            return render(request, 'reciboCliente.html', {'mensaje': mensaje})
    else:
        return render(request, 'reciboCliente.html')

#Codigo para Multiplicar


 


  