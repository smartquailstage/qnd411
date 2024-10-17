from django.db import models
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from django_countries.fields import CountryField
from cities_light import models as cities_light_models



class SystemInfo(models.Model):
    CHOICES = [
        ('+A', '+A'),
        ('+I+D', '+I+D'),
        ('+ML', '+ML'),
        ('+AI', '+AI'),
    ]

    fecha_lanzamiento = models.CharField(max_length=5, choices=CHOICES)
    detalle_ventas = models.CharField(max_length=5, choices=CHOICES)
    historial_ventas = models.CharField(max_length=5, choices=CHOICES)
    distribucion_ventas = models.CharField(max_length=5, choices=CHOICES)
    frecuencia_ventas = models.CharField(max_length=5, choices=CHOICES)
    porcion_ventas = models.CharField(max_length=5, choices=CHOICES)

    def __str__(self):
        return f'SystemInfo({self.fecha_lanzamiento}, {self.detalle_ventas}, {self.historial_ventas}, {self.distribucion_ventas}, {self.frecuencia_ventas}, {self.porcion_ventas})'


class BusinessInfo(models.Model):
    COMPANY_TYPE_CHOICES = [
        ('LTD', 'Compañía Limitada (LTD)'),
        ('SA', 'Sociedad Anónima (SA)'),
        ('SAS', 'Sociedad por Acciones Simplificadas (SAS)'),
        ('SLL', 'Sociedad Limitada Laboral (SLL)'),
        ('SL', 'Sociedad Limitada (SL)'),
        ('SC', 'Sociedad Colectiva (SC)'),
        ('SENC', 'Sociedad En Comandita (SENC)'),
        ('OTHER', 'Otros'),
    ]

    SYSTEM_VERSION_CHOICES = [
        ('QND-SBA-IT1-v.1.4.1', 'QND-SBA-IT1-v.1.4.1'),
        ('QND-SBA-IT2-v.1.4.0', 'QND-SBA-IT2-v.1.4.0'),
        ('QND-SBA-IT1(+A)-v.1.4.0', 'QND-SBA-IT1(+A)-v.1.4.0'),
        ('QND-SBA-IT2(+A)-v.1.4.0', 'QND-SBA-IT2(+A)-v.1.4.0'),
        ('QND-SBA-IT2(+A+I+D)-v.1.4.0', 'QND-SBA-IT2(+A+I+D)-v.1.4.0'),
        ('QND-SBA-IT2(+A+I+D+ML)-v.1.4.0', 'QND-SBA-IT2(+A+I+D+ML)-v.1.4.0'),
        ('QND-SBA-IT2(+A+I+D+ML+AI)-v.1.4.0', 'QND-SBA-IT2(+A+I+D+ML+AI)-v.1.4.0'),
        
    ]

    id_negocio = models.CharField(max_length=50, unique=True)  # Nuevo campo ID de negocio
    nombre = models.CharField(max_length=100)
    nombre_representante = models.CharField(max_length=100)
    constitucion = models.CharField(max_length=50, choices=COMPANY_TYPE_CHOICES)
    ruc = models.CharField(max_length=20)
    ciudad = models.ForeignKey(cities_light_models.City, on_delete=models.SET_NULL, null=True)
    pais = CountryField()
    contacto = models.CharField(max_length=100)
    email = models.EmailField()
    numero_inicial_facturacion = models.DecimalField(max_digits=10, decimal_places=2)
    monto_iniciales_de_ingresos_operativos = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_de_accionistas = models.IntegerField()
    valor_accionario_empresa = models.DecimalField(max_digits=10, decimal_places=2)
    sistema_version = models.CharField(max_length=50, choices=SYSTEM_VERSION_CHOICES)

    def __str__(self):
        tipo_constitucion = dict(self.COMPANY_TYPE_CHOICES).get(self.constitucion, 'Desconocido')
        return f"{self.nombre} ({tipo_constitucion})"

class CategoryProduct(models.Model):
        category_name = models.CharField(max_length=100)

        def __str__(self):
            return self.category_name

class Productos(models.Model):
    nombre = models.CharField(max_length=100)
    category = models.ForeignKey('CategoryProduct', related_name='category_items', on_delete=models.CASCADE, null=True, blank=True)
    stock = models.IntegerField(blank=True, null=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    costo_de_producto_fijo = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), null=True, blank=True, verbose_name='Costo fijo de producto')
    costo_de_producto_variable = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), null=True, blank=True, verbose_name='Costo variable de producto')
    depreciación_de_producto = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), null=True, blank=True, verbose_name='Depreciación de producto')

    def __str__(self):
        return self.nombre

    def get_field_values(self):
        return {
            'nombre': self.nombre,
            'stock': self.stock,
            'precio_unitario': self.precio_unitario,
            'costo_de_producto_fijo': self.costo_de_producto_fijo,
            'costo_de_producto_variable': self.costo_de_producto_variable,
            'depreciación_de_producto': self.depreciación_de_producto,
        }


class Venta(models.Model):
    GATEWAY = [
        ('Cash', 'Cash'),
        ('Bank transfer', 'Bank transfer'),
        ('local Credit Card', 'local Credit Card'),
        ('local Debit Card', 'local Debit Card'),
        ('Online Credit Card', 'Online Credit Card'),
        ('Online Debit Card', 'Online Debit Card'),   
    ]
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True)
    address = models.CharField(max_length=250, null=True)
    city = models.CharField(max_length=100, null=True)
    fecha = models.DateField(default=timezone.now)
    hora = models.TimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    ruc = models.CharField(max_length=20,null=True)
    paid = models.BooleanField(default=False)
    payment_gateway = models.CharField(max_length=50, choices=GATEWAY,null=True)
    
    descuentos = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    devoluciones = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('15.00'))
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)

    class Meta:
        ordering = ('-fecha',)

    def __str__(self):
        return f"Venta {self.id} - {self.first_name} {self.last_name}"

    def sub_total(self):
        # Solo se llama a sub_total si la venta ya tiene un ID
        if self.pk:
            return sum(item.get_cost() for item in self.items.all())
        return Decimal('0.00')

    def sub_total_fixed_cost(self):
        # Solo se llama a sub_total si la venta ya tiene un ID
        if self.pk:
            return sum(item.get_fixed_costt() for item in self.items.all())
        return Decimal('0.00')

    def sub_total_variable_cost(self):
        # Solo se llama a sub_total si la venta ya tiene un ID
        if self.pk:
            return sum(item.variable_cost() for item in self.items.all())
        return Decimal('0.00')

    def sub_total_depreciation_cost(self):
        # Solo se llama a sub_total si la venta ya tiene un ID
        if self.pk:
            return sum(item.depreciation_costt() for item in self.items.all())
        return Decimal('0.00')

    def valor_iva(self):
        return self.sub_total() * (self.iva_porcentaje / Decimal('100'))

    def total_a_pagar(self):
        return self.sub_total() + self.valor_iva() - self.descuentos + self.devoluciones


class VentaItem(models.Model):
    venta = models.ForeignKey('Venta', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Productos', related_name='venta_items_products', on_delete=models.CASCADE)
    category = models.ForeignKey('CategoryProduct', related_name ='venta_items_category', on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Item {self.id} - {self.product.nombre}'

    def get_cost(self):
        """Calcula el costo total del item."""
        return self.price * self.quantity
    
    def get_variable_cost(self):
        """Calcula el costo variable total del producto."""
        return self.product.costo_de_producto_variable * self.quantity

    def get_fixed_cost(self):
        """Calcula el costo fijo total del producto."""
        return self.product.costo_de_producto_fijo * self.quantity

    def get_depreciation_cost(self):
        """Calcula el costo de depreciación total del producto."""
        return self.product.depreciación_de_producto * self.quantity


@receiver(post_save, sender=Venta)
def calculate_monto(sender, instance, created, **kwargs):
    if created:
        # Calcular el monto al crear la venta
        instance.monto = instance.total_a_pagar()
        instance.save(update_fields=['monto'])


@receiver(post_save, sender=VentaItem)
def update_venta_monto(sender, instance, **kwargs):
    # Actualizar el monto de la venta asociada cuando se guarda un item
    venta = instance.venta
    venta.monto = venta.total_a_pagar()
    venta.save(update_fields=['monto'])


@receiver(post_save, sender=Venta)
@receiver(post_delete, sender=Venta)
def invalidate_cache(sender, **kwargs):
    cache_key = 'ventas_grafico_image'
    cache.delete(cache_key)


@receiver(post_save, sender=Productos)
@receiver(post_delete, sender=Productos)
def invalidate_cache_productos(sender, **kwargs):
    cache_key = 'productos_grafico_image'
    cache.delete(cache_key)
