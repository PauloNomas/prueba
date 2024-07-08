from django.test import TestCase, Client
from django.contrib.auth.models import User,Group
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.messages import get_messages
from core.models import *
from core.form import *
from core.views import *
from unittest.mock import patch, MagicMock

#test models -----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------OK

class MarcaTest(TestCase):
    def setUp(self):
        # Crear una instancia del modelo Marca para usarla en las pruebas
        self.marca = Marca.objects.create(descripcion='TestMarca')

    def test_str_method(self):
        # Verificar que el método __str__ devuelva la descripción correctamente
        self.assertEqual(str(self.marca), 'TestMarca')
#----------------------------------------------------------------------------------------OK
class GeneroModelTest(TestCase):
    def setUp(self):
        # Crear una instancia del modelo Genero para usarla en las pruebas
        self.genero = Genero.objects.create(tipo='Accion')

    def test_genero_str(self):
        # Verificar que el método __str__ devuelva el tipo correctamente
        self.assertEqual(str(self.genero), 'Accion')
#---------------------------------------------------------------------------------------OK
class TipoEmpleadoModelTest(TestCase):
    def setUp(self):
        # Crear una instancia del modelo TipoEmpleado para usar en las pruebas
        self.tipo_empleado = TipoEmpleado.objects.create(tipo='Gerente')

    def test_tipo_empleado_str(self):
        # Verificar que el método __str__ devuelva el tipo correctamente
        self.assertEqual(str(self.tipo_empleado), 'Gerente')
#-----------------------------------------------------------------------------------------OK
class CategoriaProductoModelTest(TestCase):
    def setUp(self):
        # Crear una instancia del modelo CategoriaProducto para usar en las pruebas
        self.categoria_producto = CategoriaProducto.objects.create(categoria='Electrónica')

    def test_categoria_producto_str(self):
        # Verificar que el método __str__ devuelva la categoría correctamente
        self.assertEqual(str(self.categoria_producto), 'Electrónica')

#--------------------------------------------------------------------------------------------OK
class ProductoModelTest(TestCase):
    def setUp(self):
        # Crear una instancia de CategoriaProducto
        self.categoria_producto = CategoriaProducto.objects.create(categoria='Electrónica')

        # Crear una instancia del modelo Producto para usar en las pruebas
        self.producto = Producto.objects.create(
            nombre='Producto de prueba',
            categoria=self.categoria_producto,
            descripcion='Descripción del producto',
            precio=100,
            stock=10
        )

    def test_producto_str(self):
        # Verificar que el método __str__ devuelva el nombre del producto correctamente
        self.assertEqual(str(self.producto), 'Producto de prueba')

    def test_producto_categoria(self):
        # Verificar que la relación ForeignKey con CategoriaProducto funciona correctamente
        self.assertEqual(self.producto.categoria, self.categoria_producto)
#------------------------------------------------------------------------------------------------------OK
class EmpleadoModelTest(TestCase):
    def setUp(self):
        # Crear instancias de TipoEmpleado y Genero para usar en las pruebas
        self.tipo_empleado = TipoEmpleado.objects.create(tipo='Gerente')
        self.genero = Genero.objects.create(tipo='Masculino')

        # Crear una instancia del modelo Empleado para usar en las pruebas
        self.empleado = Empleado.objects.create(
            rut='12345678-9',
            Nombre='Juan',
            apellidoP='Pérez',
            apellidoM='González',
            puesto=self.tipo_empleado,
            genero=self.genero
        )

    def test_empleado_str(self):
        # Verificar que el método __str__ devuelva el nombre del empleado correctamente
        self.assertEqual(str(self.empleado), 'Juan')

    def test_empleado_puesto(self):
        # Verificar que la relación ForeignKey con TipoEmpleado funciona correctamente
        self.assertEqual(self.empleado.puesto, self.tipo_empleado)

    def test_empleado_genero(self):
        # Verificar que la relación ForeignKey con Genero funciona correctamente
        self.assertEqual(self.empleado.genero, self.genero)
#------------------------------------------------------------------------------------------------------------------2 FAILED
class CarritoModelTest(TestCase):
    def setUp(self):
        # Crear una instancia de usuario (User)
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

        # Crear una instancia del modelo Carrito para usar en las pruebas
        self.carrito = Carrito.objects.create(usuario=self.user)
#----------------------------FAILED-------------------------------------------------------------------------------------
    def test_carrito_str(self):
        # Verificar que el método __str__ devuelva la representación esperada del carrito
        expected_str = f"{self.user} - {self.carrito.creado_en}"
        self.assertEqual(str(self.carrito), expected_str)
#----------------------------FAILED---------------------------------------------------------------------------------------------
    def test_carrito_usuario(self):
        # Verificar que la relación ForeignKey con User funciona correctamen
        self.assertEqual(self.carrito.usuario, self.user)

#-----------------------------------------------------------------------------------------------------------------------------3 error
class CarritoItemModelTest(TestCase):
    def setUp(self):
        # Crear instancias de Carrito y Producto para usar en las pruebas
        self.carrito = Carrito.objects.create(usuario_id=1)  # Cambiar el valor según la configuración de tu User model
        self.producto = Producto.objects.create(
            nombre='Producto de prueba',
            categoria_id=10,  # Asegúrate de cambiar esto según tu configuración
            descripcion='Descripción del producto',
            precio=100,
            stock=10
        )

        # Crear una instancia del modelo CarritoItem para usar en las pruebas
        self.carrito_item = CarritoItem.objects.create(
            carrito=self.carrito,
            producto=self.producto,
            cantidad=2,
            precio=50
        )
#---------------------------------------error-----------------------------------------------------------------------------

    def test_carrito_item_precio_total(self):
        # Verificar que el método precio_total calcule correctamente el precio total del CarritoItem
        expected_precio_total = self.carrito_item.cantidad * self.carrito_item.precio
        self.assertEqual(self.carrito_item.precio_total(), expected_precio_total)
#---------------------------------------error-----------------------------------------------------------------------------

    def test_carrito_item_carrito(self):
        # Verificar que la relación ForeignKey con Carrito funciona correctamente
        self.assertEqual(self.carrito_item.carrito, self.carrito)
#---------------------------------------error-----------------------------------------------------------------------------
    def test_carrito_item_producto(self):
        # Verificar que la relación ForeignKey con Producto funciona correctamente
        self.assertEqual(self.carrito_item.producto, self.producto)

#--------------------------------------------------------------------------------------------------------------------------2 FAILED
class BoletaModelTest(TestCase):
    def setUp(self):
        # Crear una instancia de Boleta para usar en las pruebas
        self.boleta = Boleta.objects.create(total=500)
#-----------------------------------FAILED----------------------------------------------------------------------------
    def test_boleta_str(self):
        # Verificar que el método __str__ devuelva la representación esperada de la boleta
        expected_str = f"Boleta {self.boleta.id} - Total: {self.boleta.total} - Fecha: {self.boleta.fecha}"
        self.assertEqual(str(self.boleta), expected_str)
#-----------------------------------FAILED----------------------------------------------------------------------------
    def test_boleta_total_positive(self):
        # Verificar que el campo total sea un entero positivo
        self.assertGreaterEqual(self.boleta.total, 0)

    def test_boleta_fecha_auto_now_add(self):
        # Verificar que la fecha se establece automáticamente al crear la boleta
        self.assertIsNotNone(self.boleta.fecha)
#----------------------------------------------------------------------------------------------------------------------5 error
class DetalleBoletaModelTest(TestCase):
    def setUp(self):
        # Crear instancias de Boleta y Producto para usar en las pruebas
        self.boleta = Boleta.objects.create(total=500)
        self.producto = Producto.objects.create(
            nombre='Producto de prueba',
            categoria_id=10,  # Asegúrate de cambiar esto según tu configuración
            descripcion='Descripción del producto',
            precio=100,
            stock=10
        )

        # Crear una instancia del modelo DetalleBoleta para usar en las pruebas
        self.detalle_boleta = DetalleBoleta.objects.create(
            boleta=self.boleta,
            producto=self.producto,
            cantidad=2,
            subtotal=200
        )
#---------------------------------------error-----------------------------------------------------------------------------

    def test_detalle_boleta_str(self):
        # Verificar que el método __str__ devuelva la representación esperada del detalle de boleta
        expected_str = f"Detalle de Boleta {self.boleta.id} - Producto: {self.producto.nombre} - Cantidad: {self.detalle_boleta.cantidad} - Subtotal: {self.detalle_boleta.subtotal}"
        self.assertEqual(str(self.detalle_boleta), expected_str)
#---------------------------------------error-----------------------------------------------------------------------------

    def test_detalle_boleta_boleta(self):
        # Verificar que la relación ForeignKey con Boleta funciona correctamente
        self.assertEqual(self.detalle_boleta.boleta, self.boleta)
#---------------------------------------error-----------------------------------------------------------------------------

    def test_detalle_boleta_producto(self):
        # Verificar que la relación ForeignKey con Producto funciona correctamente
        self.assertEqual(self.detalle_boleta.producto, self.producto)
#---------------------------------------error-----------------------------------------------------------------------------

    def test_detalle_boleta_cantidad_positive(self):
        # Verificar que la cantidad sea un entero positivo
        self.assertGreaterEqual(self.detalle_boleta.cantidad, 0)
#---------------------------------------error-----------------------------------------------------------------------------

    def test_detalle_boleta_subtotal_positive(self):
        # Verificar que el subtotal sea un entero positivo
        self.assertGreaterEqual(self.detalle_boleta.subtotal, 0)


#test formulario------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------OK
class RegistroFormTest(TestCase):
    def test_registro_form_valid(self):
        # Datos válidos para el formulario
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'user_type': 'cliente'  # Ajusta según tus opciones de ChoiceField
        }
        
        form = RegistroForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Comprobación de la creación de usuario mediante el método save()
        user = form.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        
        # Verificación opcional de otros campos del usuario si es necesario
        
        # Verificación de que el usuario se haya guardado en la base de datos
        saved_user = User.objects.get(username='testuser')
        self.assertEqual(saved_user.email, 'testuser@example.com')

    def test_registro_form_invalid(self):
        # Datos inválidos para el formulario (ejemplo: contraseñas no coinciden)
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'testpassword123',
            'password2': 'differentpassword',  # Contraseña diferente a la primera
            'user_type': 'cliente'
        }
        
        form = RegistroForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)  # Verificar que hay un error en password2
        
        # Verificar que no se haya creado un usuario en la base de datos
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='testuser')
#----------------------------------------------------------------------------------------------------------------OK
class LoginFormTest(TestCase):
    def test_login_form_valid(self):
        # Datos válidos para el formulario
        form_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'testuser')
        self.assertEqual(form.cleaned_data['password'], 'testpassword123')

    def test_login_form_invalid(self):
        # Datos inválidos para el formulario (por ejemplo, campo requerido no proporcionado)
        form_data = {
            'username': '',  # Campo requerido no proporcionado
            'password': 'testpassword123'
        }
        
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)  # Verificar que hay un error en username
#test views-----------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------1 error
class GrupoBodegueroTest(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Crear un grupo "Bodeguero"
        self.bodeguero_group = Group.objects.create(name='Bodeguero')

    def test_grupo_bodeguero_con_usuario_en_grupo(self):
        # Agregar el usuario al grupo "Bodeguero"
        self.user.groups.add(self.bodeguero_group)

        # Llamar a la función grupo_bodeguero con el usuario
        result = grupo_bodeguero(self.user)

        # Verificar que la función devuelve True
        self.assertTrue(result)

    def test_grupo_bodeguero_con_usuario_sin_grupo(self):
        # Llamar a la función grupo_bodeguero con el usuario (sin agregar al grupo)
        result = grupo_bodeguero(self.user)

        # Verificar que la función devuelve False
        self.assertFalse(result)
#---------------------------------error---------------------------------------------------------------------------
    def test_grupo_bodeguero_con_usuario_inexistente(self):
        # Crear un usuario que no está en la base de datos (sin guardar)
        user_inexistente = User(username='userinexistente')

        # Llamar a la función grupo_bodeguero con el usuario inexistente
        result = grupo_bodeguero(user_inexistente)

        # Verificar que la función devuelve False (no existe en la base de datos)
        self.assertFalse(result)
#-------------------------------------------------------------------------------------------------------------------1 error
class GrupoContadorTest(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Crear un grupo "Contador"
        self.contador_group = Group.objects.create(name='Contador')

    def test_grupo_contador_con_usuario_en_grupo(self):
        # Agregar el usuario al grupo "Contador"
        self.user.groups.add(self.contador_group)

        # Llamar a la función grupo_contador con el usuario
        result = grupo_contador(self.user)

        # Verificar que la función devuelve True
        self.assertTrue(result)

    def test_grupo_contador_con_usuario_sin_grupo(self):
        # Llamar a la función grupo_contador con el usuario (sin agregar al grupo)
        result = grupo_contador(self.user)

        # Verificar que la función devuelve False
        self.assertFalse(result)

#---------------------------------error---------------------------------------------------------------------------
    def test_grupo_contador_con_usuario_inexistente(self):
        # Crear un usuario que no está en la base de datos (sin guardar)
        user_inexistente = User(username='userinexistente')

        # Llamar a la función grupo_contador con el usuario inexistente
        result = grupo_contador(user_inexistente)

        # Verificar que la función devuelve False (no existe en la base de datos)
        self.assertFalse(result)
#--------------------------------------------------------------------------------------------------------------------1 error
class GrupoTrabajadoresTest(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Crear un grupo "Trabajadores"
        self.trabajadores_group = Group.objects.create(name='Trabajadores')

    def test_grupo_trabajadores_con_usuario_en_grupo(self):
        # Agregar el usuario al grupo "Trabajadores"
        self.user.groups.add(self.trabajadores_group)

        # Llamar a la función grupo_trabajadores con el usuario
        result = grupo_trabajadores(self.user)

        # Verificar que la función devuelve True
        self.assertTrue(result)

    def test_grupo_trabajadores_con_usuario_sin_grupo(self):
        # Llamar a la función grupo_trabajadores con el usuario (sin agregar al grupo)
        result = grupo_trabajadores(self.user)

        # Verificar que la función devuelve False
        self.assertFalse(result)
#------------------------------error-------------------------------------------------
    def test_grupo_trabajadores_con_usuario_inexistente(self):
        # Crear un usuario que no está en la base de datos (sin guardar)
        user_inexistente = User(username='userinexistente')

        # Llamar a la función grupo_trabajadores con el usuario inexistente
        result = grupo_trabajadores(user_inexistente)

        # Verificar que la función devuelve False (no existe en la base de datos)
        self.assertFalse(result)
#-----------------------------------------------------------------------------------1 FAILED
class LoginViewTest(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_login_view_get(self):
        # Inicializar el cliente de prueba de Django
        client = Client()

        # Obtener la URL para la vista login
        url = reverse('login')

        # Hacer una solicitud GET a la vista login
        response = client.get(url)

        # Verificar que la respuesta tenga el código HTTP 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verificar que la plantilla 'core/login.html' se está utilizando
        self.assertTemplateUsed(response, 'core/login.html')

    def test_login_view_post_credenciales_correctas(self):
        # Inicializar el cliente de prueba de Django
        client = Client()

        # Obtener la URL para la vista login
        url = reverse('login')

        # Datos de formulario POST válidos
        data = {
            'username': 'testuser',
            'password': 'password123',
        }

        # Hacer una solicitud POST a la vista login
        response = client.post(url, data)

        # Verificar que la respuesta redirige a 'index'
        self.assertRedirects(response, reverse('index'))

    def test_login_view_post_credenciales_incorrectas(self):
        # Inicializar el cliente de prueba de Django
        client = Client()

        # Obtener la URL para la vista login
        url = reverse('login')

        # Datos de formulario POST con credenciales incorrectas
        data = {
            'username': 'testuser',
            'password': 'passwordincorrecta',
        }

        # Hacer una solicitud POST a la vista login
        response = client.post(url, data)

        # Verificar que la plantilla 'core/login.html' se está utilizando
        self.assertTemplateUsed(response, 'core/login.html')

        # Verificar que se agregaron errores al formulario
        self.assertIn('Contraseña incorrecta', response.content.decode())
#--------------------------------------FAILED------------------------------------
    def test_login_view_post_usuario_inexistente(self):
        # Inicializar el cliente de prueba de Django
        client = Client()


        # Obtener la URL para la vista login
        url = reverse('login')

        # Datos de formulario POST con usuario inexistente
        data = {
            'username': 'usuarioinexistente',
            'password': 'password123',
        }

        # Hacer una solicitud POST a la vista login
        response = client.post(url, data)

        # Verificar que la plantilla 'core/login.html' se está utilizando
        self.assertTemplateUsed(response, 'core/login.html')

        # Verificar que se agregaron errores al formulario
        self.assertIn('Nombre de usuario incorrecto', response.content.decode())
#--------------------------------------------------------------------------------------------1 error
class cerrar_sesionViewTest(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='password123')
#-----------------------------------------error-----------------------------------
    def test_cerrar_sesion(self):
        # Inicializar el cliente de prueba de Django
        client = Client()

        # Autenticar al usuario
        client.force_login(self.user)

        # Obtener la URL para la vista cerrar_sesion
        url = reverse('cerrar_sesion')

        # Hacer una solicitud GET a la vista cerrar_sesion
        response = client.get(url)

        # Verificar que la respuesta redirige a 'index'
        self.assertRedirects(response, reverse('index'))

        # Verificar que el usuario no está autenticado después de cerrar sesión
        user_authenticated = getattr(response.wsgi_request, 'user', None)
        self.assertFalse(user_authenticated.is_authenticated)
#---------------------------------------------------------------------------------------------------------OK
class RegistroViewTest(TestCase):
    def setUp(self):
        # Crear instancias de Cliente y Trabajador para usar en las pruebas
        self.cliente_group, _ = Group.objects.get_or_create(name='Clientes')
        self.trabajador_group, _ = Group.objects.get_or_create(name='Trabajadores')

    def test_registro_view_get(self):
        # Inicializar el cliente de prueba de Django
        client = Client()

        # Obtener la URL para la vista registro
        url = reverse('registro')

        # Hacer una solicitud GET a la vista registro
        response = client.get(url)

        # Verificar que la respuesta tenga el código HTTP 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verificar que la plantilla 'core/registro.html' se está utilizando
        self.assertTemplateUsed(response, 'core/registro.html')

    @patch('core.views.login_aut')
    @patch('core.views.logger')
    def test_registro_view_post_registro_exitoso(self, mock_logger, mock_login_aut):
        # Inicializar el cliente de prueba de Django
        client = Client()

        # Obtener la URL para la vista registro
        url = reverse('registro')

        # Datos de formulario POST válidos para registro de cliente
        data = {
            'username': 'nuevousuario',
            'email': 'nuevousuario@example.com',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'password1': 'contraseña123',
            'password2': 'contraseña123',
            'user_type': 'cliente',
        }

        # Hacer una solicitud POST a la vista registro
        response = client.post(url, data)

        # Verificar que la respuesta redirige a 'index'
        self.assertRedirects(response, reverse('index'))

        # Verificar que se llama a login_aut con el usuario creado
        mock_login_aut.assert_called()

        # Verificar que se registra un mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Registro exitoso. Bienvenido!')

        # Verificar que se llama a logger.info con el mensaje correcto
        mock_logger.info.assert_called_with('Usuario nuevousuario registrado y autenticado exitosamente')

    @patch('core.views.logger')
    def test_registro_view_post_registro_fallido(self, mock_logger):
        # Inicializar el cliente de prueba de Django
        client = Client()

        # Obtener la URL para la vista registro
        url = reverse('registro')

        # Datos de formulario POST inválidos (sin user_type)
        data = {
            'username': 'nuevousuario',
            'email': 'nuevousuario@example.com',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'password1': 'contraseña123',
            'password2': 'contraseña123',
        }

        # Hacer una solicitud POST a la vista registro
        response = client.post(url, data)

        # Verificar que la plantilla 'core/registro.html' se está utilizando
        self.assertTemplateUsed(response, 'core/registro.html')

        # Verificar que no se llama a login_aut ni se registra un mensaje de éxito
        self.assertNotIn('Registro exitoso', [str(msg) for msg in get_messages(response.wsgi_request)])
        mock_logger.info.assert_not_called()

    @patch('core.views.logger')
    def test_registro_view_post_excepcion(self, mock_logger):
        # Inicializar el cliente de prueba de Django
        client = Client()

        # Mockear el form.save() para simular una excepción
        form_mock = MagicMock()
        form_mock.save.side_effect = Exception('Error al guardar el usuario')

        with patch.object(RegistroForm, 'save', form_mock.save):
            # Obtener la URL para la vista registro
            url = reverse('registro')

            # Datos de formulario POST válidos para registro de cliente
            data = {
                'username': 'nuevousuario',
                'email': 'nuevousuario@example.com',
                'first_name': 'Nuevo',
                'last_name': 'Usuario',
                'password1': 'contraseña123',
                'password2': 'contraseña123',
                'user_type': 'cliente',
            }

            # Hacer una solicitud POST a la vista registro
            response = client.post(url, data)

            # Verificar que la plantilla 'core/registro.html' se está utilizando
            self.assertTemplateUsed(response, 'core/registro.html')

            # Verificar que se llama a logger.error con el mensaje de error
            mock_logger.error.assert_called_with('Error al registrar el usuario: Error al guardar el usuario')

    def test_registro_view_post_formulario_invalido(self):
        # Inicializar el cliente de prueba de Django
        client = Client()

        # Obtener la URL para la vista registro
        url = reverse('registro')

        # Datos de formulario POST inválidos (sin datos)
        data = {}

        # Hacer una solicitud POST a la vista registro
        response = client.post(url, data)

        # Verificar que la plantilla 'core/registro.html' se está utilizando
        self.assertTemplateUsed(response, 'core/registro.html')

        # Verificar que el formulario contiene errores
        self.assertTrue(response.context['form'].errors)

        # Verificar que no se llama a logger ni se registra ningún mensaje
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)
#------------------------------------------------------------------------------1 error
class IndicadoresViewTest(TestCase):
    @patch('core.views.requests.get')
    def test_indicadores_view_api_exitosa(self, mock_get):
        # Configurar el mock de requests.get() para simular una respuesta exitosa
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'uf': {'valor': 28500.12},
            'dolar': {'valor': 780.45},
            'euro': {'valor': 900.67},
            'ipc': {'valor': 0.3},
        }
        mock_get.return_value = mock_response

        # Inicializar el cliente de prueba de Django
        client = Client()

        # Obtener la URL para la vista indicadores
        url = reverse('indicadores')

        # Hacer una solicitud GET a la vista indicadores
        response = client.get(url)

        # Verificar que la respuesta tenga el código HTTP 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Verificar que la plantilla 'core/indicadores.html' se está utilizando
        self.assertTemplateUsed(response, 'core/indicadores.html')

        # Verificar que los indicadores se pasan correctamente al contexto de la plantilla
        self.assertIn('indicadores', response.context)
        indicadores = response.context['indicadores']
        self.assertEqual(indicadores['uf'], 28500.12)
        self.assertEqual(indicadores['dolar'], 780.45)
        self.assertEqual(indicadores['euro'], 900.67)
        self.assertEqual(indicadores['ipc'], 0.3)

    @patch('core.views.requests.get')
#------------------------------------------------error------------------------------------------------------------------------------------------
    def test_indicadores_view_api_fallida(self, mock_get):
        # Configurar el mock de requests.get() para simular una respuesta fallida
        mock_get.side_effect = Exception('Error en la solicitud a la API')

        # Inicializar el cliente de prueba de Django
        client = Client()

        # Obtener la URL para la vista indicadores
        url = reverse('indicadores')

        # Hacer una solicitud GET a la vista indicadores
        response = client.get(url)

        # Verificar que la plantilla 'core/indicadores.html' se está utilizando
        self.assertTemplateUsed(response, 'core/indicadores.html')

        # Verificar que los indicadores están vacíos en el contexto de la plantilla
        self.assertIn('indicadores', response.context)
        indicadores = response.context['indicadores']
        self.assertEqual(indicadores, {})

        # Verificar que se imprime un mensaje de error en la consola
        self.assertIn('Error al obtener los datos de la API', self._out.getvalue())

        # Verificar que no se registra ningún indicador en el contexto
        self.assertNotIn('uf', indicadores)
        self.assertNotIn('dolar', indicadores)
        self.assertNotIn('euro', indicadores)
        self.assertNotIn('ipc', indicadores)
#-------------------------------------------------------------------------------------------------------2 ERROR
class WebpayPlusCommitViewTest(TestCase):
    def setUp(self):
        # Configuración inicial para las pruebas
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.carrito = Carrito.objects.create(usuario=self.user)
        self.producto = Producto.objects.create(nombre='Producto de prueba', categoria_id=1, descripcion='Descripción del producto', precio=100, stock=10)
        self.carrito_item = CarritoItem.objects.create(carrito=self.carrito, producto=self.producto, cantidad=1, precio=self.producto.precio)

    @patch('core.views.Transaction.commit')

    def test_webpay_plus_commit_success(self, mock_commit):
        # Configurar el mock de Transaction.commit() para simular una respuesta autorizada
        mock_response = {
            'status': 'AUTHORIZED'
            # Agregar más campos de respuesta según sea necesario
        }
        mock_commit.return_value = mock_response

        # Configurar la solicitud GET simulada
        url = reverse('webpay_plus_commit')
        response = self.client.get(url, {'token_ws': 'dummytoken'})

        # Verificar que se llama a Transaction.commit() con el token_ws proporcionado
        mock_commit.assert_called_once_with(token='dummytoken')

        # Verificar que se crea una boleta y un detalle de boleta correctamente
        self.assertEqual(Boleta.objects.count(), 1)
        self.assertEqual(DetalleBoleta.objects.count(), 1)

        # Verificar la redirección y el contexto renderizado después de una transacción autorizada
        self.assertRedirects(response, expected_url=reverse('index'))
#----------------------------------------error--------------------------------------------------------------
    def test_webpay_plus_commit_cancel(self):
        # Configurar la solicitud POST simulada para cancelar la transacción
        url = reverse('webpay_plus_commit')
        response = self.client.post(url, {'action': 'cancel'})

        # Verificar que se limpia el carrito después de cancelar la transacción
        self.assertEqual(CarritoItem.objects.count(), 0)

        # Verificar la redirección después de cancelar
        self.assertRedirects(response, expected_url=reverse('carrito'))
#--------------------------------------------error-----------------------------------------------------------
    def test_webpay_plus_commit_error(self):
        # Configurar la solicitud POST simulada con errores en la transacción
        url = reverse('webpay_plus_commit')
        response = self.client.post(url, {'token_ws': 'dummytoken', 'action': 'dummyaction'})

        # Verificar que se muestra el template 'core/commit.html' con el contexto correcto
        self.assertTemplateUsed(response, 'core/commit.html')
        self.assertIn('response', response.context)
        self.assertIn('error', response.context)
        self.assertFalse(response.context['success'])

    @patch('core.views.Transaction.commit')
#----------------------------------------------error------------------------------------------------------------
    def test_webpay_plus_commit_transbank_error(self, mock_commit):
        # Configurar el mock de Transaction.commit() para simular un error de Transbank
        mock_commit.side_effect = TransbankError("Error en la transacción")

        # Configurar la solicitud GET simulada con token_ws
        url = reverse('webpay_plus_commit')
        response = self.client.get(url, {'token_ws': 'dummytoken'})

        # Verificar que se renderiza 'core/commit.html' con el contexto correcto después de un error
        self.assertTemplateUsed(response, 'core/commit.html')
        self.assertIn('error', response.context)
        self.assertFalse(response.context['success'])