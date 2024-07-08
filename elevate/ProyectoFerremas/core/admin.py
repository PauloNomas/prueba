from django.contrib import admin
from .models import *
from admin_confirm import AdminConfirmMixin



class ProductoAdmin(AdminConfirmMixin, admin.ModelAdmin):
        confirm_change = True
        confirmation_fields = ['nombre', 'categoria', 'descripcion', 'precio', 'stock', 'imagen']

class CategoriaProductoAdmin(AdminConfirmMixin, admin.ModelAdmin):
        confirm_change = True
        confirmation_fields = ['id', 'categoria']

# Register your models here.

admin.site.register(Marca)
admin.site.register(Genero)
admin.site.register(TipoEmpleado)
admin.site.register(Producto)
admin.site.register(Empleado)
admin.site.register(CategoriaProducto)