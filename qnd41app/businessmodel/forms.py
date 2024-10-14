from django import forms
from .models import Productos

class FiltroVentasForm(forms.Form):
    periodo_choices = [
        ('H', 'Hora'),
        ('D', 'Día'),
        ('M', 'Mes'),
        ('Y', 'Año'),
    ]
    categoria_choices = [
        ('M', 'Monto'),
        ('C', 'Cantidad'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener productos de la base de datos
        productos = Productos.objects.all()
        # Crear la lista de opciones para el campo productos
        productos_choices = [('__all__', 'Todos')] + [(p.id, p.nombre) for p in productos]
        # Establecer las opciones del campo productos
        self.fields['productos'].choices = productos_choices

    productos = forms.ChoiceField(choices=[], required=False, label='Productos')
    categoria = forms.ChoiceField(choices=categoria_choices, required=False, label='Categorías')
    periodo = forms.ChoiceField(choices=periodo_choices, required=False, label='Período')
    fecha_inicio = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Fecha y Hora de Inicio'
    )
    fecha_fin = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label='Fecha y Hora de Fin'
    )
    frecuencia = forms.ChoiceField(choices=[
        ('horas', 'Horas'),
        ('diario', 'Diario'),
        ('semanas', 'Semanas'),
        ('meses', 'Meses'),
        ('años', 'Años'),
    ], required=False)




    
  