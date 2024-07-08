from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Producto, Carrito, CarritoItem, Boleta, DetalleBoleta
import locale
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as login_aut
from .form import LoginForm, RegistroForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, authenticate, login as login_aut
import random
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.error.transbank_error import TransbankError
from django.http import HttpResponseBadRequest
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
import logging
from django.contrib import messages
from django.template import engines
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

logger = logging.getLogger(__name__)

def grupo_bodeguero(user):
    return user.groups.filter(name='Bodeguero').exists()

def grupo_contador(user):
    return user.groups.filter(name='Contador').exists()

def grupo_trabajadores(user):
    return user.groups.filter(name='Trabajadores').exists()

def index(request):
    return render(request, 'core/index.html', {'user': request.user})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_active:
                login_aut(request, user)
                return redirect('index')
            else:
                if User.objects.filter(username=username).exists():
                    form.add_error(None, 'Contraseña incorrecta')
                else:
                    form.add_error(None, 'Nombre de usuario incorrecto')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


def cerrar_sesion(request):
    logout(request)
    return redirect(to="index")

@login_required
@user_passes_test(grupo_bodeguero)
def bodeguero_view(request):
    pedidos_aprobados = Boleta.objects.filter(detalleboleta__producto__isnull=False).distinct()
    context = {
        'pedidos_aprobados': pedidos_aprobados,
        'user': request.user 
    }
    return render(request, 'core/bodeguero.html', context)

def producto(request):
    return render(request, 'core/producto.html')

def account_locked(request):
    return render(request, 'core/account_locked.html')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                user_type = form.cleaned_data['user_type']

                # Verificar si los grupos existen
                clientes_group, created = Group.objects.get_or_create(name='Clientes')
                trabajadores_group, created = Group.objects.get_or_create(name='Trabajadores')

                if user_type == 'cliente':
                    clientes_group.user_set.add(user)
                elif user_type == 'trabajador':
                    trabajadores_group.user_set.add(user)

                login_aut(request, user)
                messages.success(request, 'Registro exitoso. Bienvenido!')
                logger.info(f"Usuario {user.username} registrado y autenticado exitosamente")
                return redirect('index')
            except Exception as e:
                # Capturar más detalles del error
                error_message = f"Error al registrar el usuario: {e}"
                logger.error(error_message)
                form.add_error(None, error_message)
        else:
            logger.warning(f"Formulario de registro no válido: {form.errors.as_json()}")
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})
    
def tienda(request):
    productos = Producto.objects.all()
    ctx = {
        "productos": productos
    }
    return render(request, 'core/tienda.html', ctx)

# Carrito
def carrito(request):

    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

    carrito = Carrito.objects.get_or_create(usuario=request.user)[0]
    items_carrito = carrito.carritoitem_set.all()
    sub_total_items = sum(item.cantidad * item.producto.precio for item in items_carrito)
    total = sum(item.precio_total() for item in items_carrito)
    total_formateado = locale.format_string("%d", total, grouping=True)

    for item in items_carrito:
        item.total_item = item.cantidad * item.producto.precio

    ctx = {
        'items_carrito': items_carrito,
        'total': total,
        'total_formato': total_formateado,
        'sub_total': sub_total_items
    }
    return render(request, 'core/carrito.html', ctx)

# Métodos del Carrito
@login_required(login_url='/login/')
def agregar_al_carrito(request, id_producto):
    producto = Producto.objects.get(pk=id_producto)
    carrito = Carrito.objects.get_or_create(usuario=request.user)[0]
    item_existente = carrito.carritoitem_set.filter(producto=producto).first()
    
    if item_existente:
        # Si el producto ya está en el carrito, aumenta la cantidad
        item_existente.cantidad += 1
        item_existente.save()
    else:
        # Si el producto no está en el carrito, crea un nuevo ítem
        CarritoItem.objects.create(carrito=carrito, producto=producto, precio=producto.precio)
        
    return redirect('tienda')

@login_required(login_url='/login/')
def eliminar_del_carrito(request, id_item):
    item = CarritoItem.objects.get(pk=id_item)
    item.delete()
    return redirect('carrito')

@login_required(login_url='/login/')
def vaciar_carrito(request):
    carrito = Carrito.objects.get(usuario=request.user)
    carrito.carritoitem_set.all().delete()
    return redirect('carrito')

@login_required(login_url='/login/')
def aumentar_cantidad(request, id_item):
    item = get_object_or_404(CarritoItem, pk=id_item)
    item.cantidad += 1
    item.save()
    return redirect('carrito')

@login_required(login_url='/login/')
def disminuir_cantidad(request, id_item):
    item = get_object_or_404(CarritoItem, pk=id_item)
    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()
    else:
        item.delete()
    return redirect('carrito')

# Indicadores
def indicadores_view(request):
    url = 'https://mindicador.cl/api'
    try:
        response = requests.get(url)
        data = response.json()
        indicadores = {
            'uf': data.get('uf', {}).get('valor'),
            'dolar': data.get('dolar', {}).get('valor'),
            'euro': data.get('euro', {}).get('valor'),
            'ipc': data.get('ipc', {}).get('valor'),
        }
    except Exception as e:
        indicadores = {}
        print(f"Error al obtener los datos de la API: {e}")

    return render(request, 'core/indicadores.html', {'indicadores': indicadores})

@login_required
def perfil(request):
    return render(request, 'core/perfil.html', {'user': request.user})

# Transbank
def webpay_plus_commit(request):
    if request.method == 'GET':
        token = request.GET.get("token_ws")
        if token is None:
            return HttpResponseBadRequest("El parámetro 'token_ws' es requerido en la URL.")
        
        try:
            response = Transaction().commit(token=token)
            status = response.get('status', 'UNKNOWN')
            if status == 'AUTHORIZED':
                productos = []
                precio_total = 0
                carrito = Carrito.objects.get(usuario=request.user)
                items_carrito = carrito.carritoitem_set.all()
                precio_total = sum(item.cantidad * item.producto.precio for item in items_carrito)

                boleta = Boleta(total=precio_total)
                boleta.save()

                for item in items_carrito:
                    producto = item.producto
                    cantidad = item.cantidad
                    subtotal = cantidad * producto.precio
                    detalle = DetalleBoleta(boleta=boleta, producto=producto, cantidad=cantidad, subtotal=subtotal)
                    detalle.save()
                    productos.append({
                        'nombre': producto.nombre,
                        'cantidad': cantidad,
                        'subtotal': subtotal
                    })

                carrito.carritoitem_set.all().delete()

                context = {
                    'token': token,
                    'response': response,
                    'productos': productos,
                    'total': precio_total,
                    'success': True
                }

                return render(request, 'core/commit.html', context)
            else:
                return render(request, 'core/commit.html', {
                    'token': token,
                    'response': response,
                    'error': f"Estado de la transacción: {status}",
                    'success': False
                })
        
        except TransbankError as e:
            if "422" in str(e):  # Verifica si el error contiene el código 422
                return redirect('carrito')  # Redirecciona al carrito de compras
            else:
                return render(request, 'core/commit.html', {
                    'error': f"Error en la transacción: {str(e)}",
                    'success': False
                })

    elif request.method == 'POST':
        action = request.POST.get("action")
        if action == 'cancel':
            carrito = Carrito.objects.get(usuario=request.user)
            carrito.carritoitem_set.all().delete()
            return redirect('carrito')
        
        if action == 'confirm':
            return redirect('index')  # Redirecciona a la página de inicio después de confirmar el pago

        token = request.POST.get("token_ws")
        response = {"error": "Transacción con errores"}
        return render(request, 'core/commit.html', {'token': token, 'response': response})

def generar_boleta(request):
    if request.method == 'GET':
        carrito = Carrito.objects.get_or_create(usuario=request.user)[0]
        items_carrito = carrito.carritoitem_set.all()
        if not items_carrito:
            return render(request, 'core/error.html', {'error': 'El carrito está vacío'})

        precio_total = sum(item.cantidad * item.producto.precio for item in items_carrito)
        buy_order = str(random.randrange(1000000, 99999999))
        session_id = str(random.randrange(1000000, 99999999))
        return_url = request.build_absolute_uri(reverse('webpay_plus_commit'))

        try:
            response = Transaction().create(buy_order, session_id, precio_total, return_url)
            return render(request, 'core/create.html', {'response': response})
        except Exception as e:
            return render(request, 'core/error.html', {'error': str(e)})
    else:
        return render(request, 'core/error.html', {'error': 'Método HTTP no permitido'})
    
def webpay_plus_commit_error(request):
    return HttpResponse("Error en la transacción de pago")

def webpay_plus_refund(request):
    if request.method == 'POST':
        token = request.POST.get("token_ws")
        amount = request.POST.get("amount")

        try:
            response = Transaction().refund(token, amount)
            return render(request, "core/refund.html", {'token': token, 'amount': amount, 'response': response})
        except TransbankError as e:
            return render(request, 'core/error.html', {'error': str(e)})

def webpay_plus_refund_form(request):
    return render(request, 'core/refund-form.html')

def status(request):
    token_ws = request.POST.get('token_ws')
    tx = Transaction()
    resp = tx.status(token_ws)
    return render(request, 'core/status.html', {'response': resp, 'token': token_ws, 'req': request.POST})

def show_create(request):
    return render(request, 'core/status-form.html')

def webpay_plus_create(request):
    if request.method == 'GET':
        buy_order = str(random.randrange(1000000, 99999999))
        session_id = str(random.randrange(1000000, 99999999))
        amount = random.randrange(10000, 1000000)
        return_url = request.build_absolute_uri('core/commit')

        response = Transaction().create(buy_order, session_id, amount, return_url)
        return render(request, 'core/create.html', {'response': response})

@login_required
@user_passes_test(grupo_contador)
def vista_contador(request):
    boletas = Boleta.objects.all()
    if request.method == 'POST':
        if 'generar_pdf' in request.POST:
            return generar_pdf(request, boletas)
        if 'limpiar' in request.POST:
            limpiar_productos()
            return redirect('vista_contador')
    return render(request, 'core/vista_contador.html', {'boletas': boletas})

def generar_pdf(request, boletas):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_compras.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 40, "Reporte de Compras")

    y = height - 80
    total_general = 0

    for boleta in boletas:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y, f"Boleta ID: {boleta.id} - Fecha: {boleta.fecha.strftime('%Y-%m-%d %H:%M:%S')} - Total: ${boleta.total}")
        y -= 20

        detalles = DetalleBoleta.objects.filter(boleta=boleta)
        for detalle in detalles:
            p.setFont("Helvetica", 12)
            p.drawString(120, y, f"Producto: {detalle.producto.nombre} - Cantidad: {detalle.cantidad} - Subtotal: ${detalle.subtotal}")
            y -= 20
        
        total_general += boleta.total
        y -= 20

        if y < 100:
            p.showPage()
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, height - 40, "Reporte de Compras (cont.)")
            y = height - 80

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y, f"Total General de Ventas: ${total_general}")

    p.showPage()
    p.save()
    return response

def limpiar_productos():
    logger.info("Limpiando productos y boletas...")
    DetalleBoleta.objects.all().delete()
    Boleta.objects.all().delete()
    Producto.objects.all().update(stock=0)  # Actualiza el stock de todos los productos a 0
    logger.info("Productos y boletas limpiados correctamente.")

def buscar_productos(request):
    query = request.GET.get('q', '')
    productos = Producto.objects.all()

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(categoria__categoria__icontains=query) |
            Q(descripcion__icontains=query)
        )

    ctx = {
        'productos': productos,
        'query': query
    }
    return render(request, 'core/tienda.html', ctx)