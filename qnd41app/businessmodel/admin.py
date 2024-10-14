import csv
import datetime
from django.contrib import admin
from django.http import HttpResponse
from .models import Productos, Venta, VentaItem
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import BusinessInfo,SystemInfo,CategoryProduct



class SystemInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('fecha_lanzamiento',)
        }),
        ('Información', {
            'fields': ('detalle_ventas', 'historial_ventas')
        }),
        ('Métricas', {
            'fields': ('distribucion_ventas', 'frecuencia_ventas', 'porcion_ventas')
        }),
    )

    list_display = ('fecha_lanzamiento', 'detalle_ventas', 'historial_ventas', 
                    'distribucion_ventas', 'frecuencia_ventas', 'porcion_ventas')
    search_fields = ('detalle_ventas', 'historial_ventas')

admin.site.register(SystemInfo, SystemInfoAdmin)


class BusinessInfoAdmin(admin.ModelAdmin):
    list_display = ('id_negocio', 'nombre', 'nombre_representante', 'constitucion', 'ruc', 'ciudad', 'pais', 'contacto', 'email', 'sistema_version')
    list_filter = ('constitucion', 'pais', 'ciudad', 'sistema_version')
    search_fields = ('nombre', 'nombre_representante', 'ruc', 'id_negocio')
    ordering = ('nombre',)
    fieldsets = (
        (None, {
            'fields': ('id_negocio', 'nombre', 'nombre_representante', 'constitucion', 'ruc', 'ciudad', 'pais')
        }),
        ('Contacto', {
            'fields': ('contacto', 'email')
        }),
        ('Finanzas', {
            'fields': ('numero_inicial_facturacion', 'monto_iniciales_de_ingresos_operativos', 'cantidad_de_accionistas', 'valor_accionario_empresa')
        }),
        ('Sistema', {
            'fields': ('sistema_version',)
        }),
    )

admin.site.register(BusinessInfo, BusinessInfoAdmin)


@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    # Define los campos que quieres mostrar en la lista de productos
    list_display = ('id', 'nombre','category', 'stock', 'precio_unitario','costo_de_producto_fijo','costo_de_producto_variable','depreciación_de_producto')

    # Define los campos que se pueden buscar en el panel de administración
    search_fields = ('nombre', 'id')

    # Agrega filtros en el panel de administración
    list_filter = ('nombre', 'stock')

    # Agrega campos que se pueden editar en la vista de detalle
    fields = ('category','nombre', 'stock', 'precio_unitario','costo_de_producto_fijo','costo_de_producto_variable','depreciación_de_producto')

@admin.register(CategoryProduct)
class CategoryProductAdmin(admin.ModelAdmin):
    # Define los campos que quieres mostrar en la lista de productos
    list_display = ('id', 'category_name')

    # Define los campos que se pueden buscar en el panel de administración
    search_fields = ('id', 'category_name')

    # Agrega filtros en el panel de administración
    list_filter = ('id', 'category_name')

    # Agrega campos que se pueden editar en la vista de detalle
    fields = ('category_name',)



    # Opcional: Exportar CSV
    def export_as_csv(self, request, queryset):
        # Implementa la lógica para exportar los datos a CSV aquí
        pass

    actions = ['export_as_csv']

def venta_detail(obj):
    # Asegúrate de que 'businessmodel:admin_ventas_detail' sea el nombre de URL correcto
    return mark_safe('<a href="{}">Ver</a>'.format(
        reverse('businessmodel:inicio_venta', args=[obj.id])))  # Usa 'admin:app_venta_change'



class VentaItemInline(admin.TabularInline):
    model = VentaItem
    raw_id_fields = ['product','category']

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    # Define los campos que quieres mostrar en la lista de ventas
    list_display = ('id', 'first_name', 'last_name', 'email', 'fecha','hora','payment_gateway','sub_total','total_a_pagar','monto', venta_detail)

    # Define los campos que se pueden buscar en el panel de administración
    search_fields = ('first_name', 'last_name', 'email','payment_gateway')

    # Agrega filtros en el panel de administración
    list_filter = ('fecha', 'paid','payment_gateway')

    # Agrega campos que se pueden editar en la vista de detalle
    fields = ('first_name', 'last_name', 'email', 'address', 'city', 'descuentos','payment_gateway', 'devoluciones', 'paid')

    # Define los campos que deben ser solo lectura
    readonly_fields = ('fecha',)
    inlines = [VentaItemInline]
