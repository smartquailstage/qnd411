import matplotlib
import qrcode
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.views.decorators.cache import cache_page
import pandas as pd
import numpy as np
from scipy import stats
from scipy.signal import argrelextrema
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from .models import SystemInfo,BusinessInfo,Venta,VentaItem
from .forms import FiltroVentasForm
from django.db.models import Max
from django.template.loader import render_to_string
import weasyprint

import time
import base64
from matplotlib.widgets import Cursor
from .forms import FiltroVentasForm
from scipy.interpolate import make_interp_spline
from django.db.models import Sum
from scipy.stats import linregress



matplotlib.use('Agg')  # Usa el backend Agg para renderizar gráficos en memoria

#App Registtro de ventas  

@staff_member_required
def inicio_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
       # Obtener el último objeto de BusinessInfo
    last_business_info = BusinessInfo.objects.last() 
    last_system_info = SystemInfo.objects.last()
    
    business_value = {
        'id_negocio': last_business_info.id_negocio,
        'sistema_version': last_business_info.sistema_version,
    } if last_business_info else None  # Manejo de caso si no hay registros

    systems_value = {
        'detalle_ventas': last_system_info.detalle_ventas,
        'historial_ventas': last_system_info.historial_ventas,
    } if last_business_info else None  # Manejo de caso si no hay registros

    return render(request,
                  'admin/businessmodel/Sales/inicio.html', {
                  'venta':venta,
                  'businessinfo': business_value,
                  'systeminfo': systems_value })

@staff_member_required
def inicio_venta_header(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
       # Obtener el último objeto de BusinessInfo
    last_business_info = BusinessInfo.objects.last() 
    last_system_info = SystemInfo.objects.last()
    
    business_value = {
        'id_negocio': last_business_info.id_negocio,
        'sistema_version': last_business_info.sistema_version,
    } if last_business_info else None  # Manejo de caso si no hay registros

    systems_value = {
        'detalle_ventas': last_system_info.detalle_ventas,
        'historial_ventas': last_system_info.historial_ventas,
    } if last_business_info else None  # Manejo de caso si no hay registros

    return render(request,
                  'admin/businessmodel/Sales/tools/header_detail.html',{'venta':venta,
                  'businessinfo': business_value,
                  'systeminfo': systems_value })

@staff_member_required
def admin_ventas_detail(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    return render(request,
                  'admin/businessmodel/ventas/introduccion/inicio_informacion.html',{'venta': venta,})

@staff_member_required
def informacion_venta(request, venta_id):
    # Obtener el último objeto de BusinessInfo
    last_business_info = BusinessInfo.objects.last() 
    last_system_info = SystemInfo.objects.last()
    
    business_value = {
        'id_negocio': last_business_info.id_negocio,
        'sistema_version': last_business_info.sistema_version,
    } if last_business_info else None  # Manejo de caso si no hay registros

    # Obtener la información de ventas filtrada por el ID proporcionado
    venta = get_object_or_404(Venta, id=venta_id)

    # Inicializar la lista de ventas
    lista_ventas = Venta.objects.all()

    # Filtros opcionales recibidos desde el request
    customer_name = request.GET.get('first_name', None)
    fecha_compra = request.GET.get('fecha_compra', None)
    ruc = request.GET.get('ruc', None)

    # Aplicar filtro por nombre de cliente, si está presente
    if customer_name :
        lista_ventas = lista_ventas.filter(first__name__icontains=first_name)

    # Aplicar filtro por fecha de compra, si está presente
    if fecha_compra:
        try:
            # Suponiendo que 'fecha_compra' se pasa en formato YYYY-MM-DD
            fecha_filtrada = datetime.strptime(fecha_compra, '%Y-%m-%d').date()
            lista_ventas = lista_ventas.filter(fecha_compra=fecha_filtrada)
        except ValueError:
            pass  # Si la fecha no tiene el formato correcto, ignoramos el filtro

    # Aplicar filtro por RUC, si está presente
    if ruc:
        lista_ventas = lista_ventas.filter(ruc=ruc)

    # Renderizar la plantilla con los datos filtrados
    return render(request, 'admin/businessmodel/Sales/tools/detail-income/detail.html', {
        'venta': venta,
        'lista_ventas': lista_ventas,
        'businessinfo': business_value,
        'customer_name ': customer_name ,
        'fecha_compra': fecha_compra,
        'ruc': ruc,
    })

@staff_member_required
def informacion_venta_productos(request, venta_id):
    # Obtener la información de ventas filtrada por el ID proporcionado
    venta = get_object_or_404(Venta, id=venta_id)
    return render(request,'admin/businessmodel/ventas/tools/informacion_productos.html',{'venta': venta,})

@staff_member_required
def admin_comprobante_pdf(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    html = render_to_string('admin/businessmodel/ventas/reportes/comprobante.html',
                            {'venta': venta })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=comprobante_{}.pdf"'.format(venta.id)
    weasyprint.HTML(string=html,  base_url=request.build_absolute_uri() ).write_pdf(response,stylesheets=[weasyprint.CSS('businessmodel/static/css/comprobante_venta.css')], presentational_hints=True)
    return response

 #App Historial de ventas------------------------------------ 


@staff_member_required
def admin_historial(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    return render(request,
                  'admin/businessmodel/ventas/introduccion/inicio_historial.html',{'venta': venta,})


@staff_member_required
def history_incomes_amount(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener fechas, horas, nombre de cliente y monto desde la solicitud
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')
    nombre_cliente = request.GET.get('nombre_cliente')
    nombre_producto = request.GET.get('nombre_producto')  # Filtro por nombre de producto
    monto_min = float(request.GET.get('monto_min', 0))
    monto_max = float(request.GET.get('monto_max', 1000000000))

    # Filtrar lista_ventas
    lista_ventas = Venta.objects.all()  # Obtener todas las ventas inicialmente

    # Filtrar por rango de fechas y horas
    if fecha_inicio and hora_inicio:
        inicio = datetime.strptime(f"{fecha_inicio} {hora_inicio}", "%Y-%m-%d %H:%M")
    else:
        inicio = None

    if fecha_fin and hora_fin:
        fin = datetime.strptime(f"{fecha_fin} {hora_fin}", "%Y-%m-%d %H:%M")
    else:
        fin = None

    if fecha_inicio and fecha_fin:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d") + timedelta(days=1)  # Incluir el último día
        lista_ventas = lista_ventas.filter(fecha__range=(inicio.date(), fin.date()))

    if inicio and fin:
        lista_ventas = lista_ventas.filter(fecha__range=(inicio, fin))  # Filtrar por rango de fechas y horas

    # Filtrar por nombre de cliente
    if nombre_cliente:
        lista_ventas = lista_ventas.filter(first_name__icontains=nombre_cliente)

    # Filtrar por nombre de producto
    if nombre_producto:
        lista_ventas = lista_ventas.filter(items__product__nombre__icontains=nombre_producto)

    # Filtrar por rango de monto
    if monto_min and monto_max:
        lista_ventas = lista_ventas.filter(monto__gte=monto_min, monto__lte=monto_max)
    elif monto_min:
        lista_ventas = lista_ventas.filter(monto__gte=monto_min)
    elif monto_max:
        lista_ventas = lista_ventas.filter(monto__lte=monto_max)

    # Calcular las diferencias en días y horas entre las ventas
    diferencias = []
    for i in range(1, len(lista_ventas)):
        fecha1 = lista_ventas[i-1].fecha
        fecha2 = lista_ventas[i].fecha
        diferencia = fecha2 - fecha1
        diferencias.append(diferencia)

    # Sumar todas las diferencias
    total_diferencia = sum(diferencias, timedelta())
    total_dias = total_diferencia.days
    total_horas = total_diferencia.total_seconds() // 3600

    # Calcular totales
    sub_totales = [v.sub_total() for v in lista_ventas]
    valores_iva = [v.valor_iva() for v in lista_ventas]
    totales = [v.total_a_pagar() for v in lista_ventas]

    suma_sub_totales = np.sum(sub_totales)
    suma_valor_iva = np.sum(valores_iva)
    suma_totales = np.sum(totales)

    cantidad_ventas = len(lista_ventas)

    # Manejo del ordenamiento
    sort = request.GET.get('sort', 'id')  # Por defecto ordenar por ID
    order = request.GET.get('order', 'asc')  # Por defecto orden ascendente

    if order == 'desc':
        lista_ventas = lista_ventas.order_by(f'-{sort}')
    else:
        lista_ventas = lista_ventas.order_by(sort)

    # Pasar las ventas y la suma al contexto de la plantilla
    return render(request, 'admin/businessmodel/Sales/tools/history-incomes/amount/history.html', {
        'venta': venta,
        'lista_ventas': lista_ventas,
        'suma_totales': suma_totales,
        'suma_sub_totales': suma_sub_totales,
        'suma_valor_iva': suma_valor_iva,
        'cantidad_ventas': cantidad_ventas,
        'total_dias': total_dias,
        'total_horas': total_horas,
    })


@staff_member_required
def history_incomes_product(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    
    # Obtener fechas, horas y montos desde la solicitud
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')
    nombre_producto = request.GET.get('nombre_producto')
    monto_minimo = request.GET.get('monto_minimo')  # Nuevo filtro
    monto_maximo = request.GET.get('monto_maximo')  # Nuevo filtro

    # Filtrar lista_ventas
    lista_ventas = Venta.objects.all()  # Obtener todas las ventas inicialmente

    # Filtrar las ventas según el rango de fechas y horas
    if fecha_inicio and hora_inicio:
        inicio = datetime.strptime(f"{fecha_inicio} {hora_inicio}", "%Y-%m-%d %H:%M")
    else:
        inicio = None

    if fecha_fin and hora_fin:
        fin = datetime.strptime(f"{fecha_fin} {hora_fin}", "%Y-%m-%d %H:%M")
    else:
        fin = None

    if fecha_inicio and fecha_fin:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d") + timedelta(days=1)  # Incluir el último día
        lista_ventas = lista_ventas.filter(fecha__range=(inicio.date(), fin.date()))

    if inicio and fin:
        lista_ventas = lista_ventas.filter(fecha__range=(inicio.date(), fin.date()))

    # Filtrar por nombre de producto
    if nombre_producto:
        lista_ventas = lista_ventas.filter(items__product__nombre__icontains=nombre_producto)

    # Filtrar por monto mínimo y máximo
    if monto_minimo:
        lista_ventas = lista_ventas.filter(total_a_pagar__gte=float(monto_minimo))  # Monto mínimo
    if monto_maximo:
        lista_ventas = lista_ventas.filter(total_a_pagar__lte=float(monto_maximo))  # Monto máximo

    # Calcular las diferencias en días y horas entre las ventas
    diferencias = []
    for i in range(1, len(lista_ventas)):
        fecha1 = lista_ventas[i-1].fecha
        fecha2 = lista_ventas[i].fecha
        diferencia = fecha2 - fecha1
        diferencias.append(diferencia)

    # Sumar todas las diferencias
    total_diferencia = sum(diferencias, timedelta())
    total_dias = total_diferencia.days
    total_horas = total_diferencia.total_seconds() // 3600

    # Calcular totales
    sub_totales = [v.sub_total() for v in lista_ventas]
    valores_iva = [v.valor_iva() for v in lista_ventas]
    totales = [v.total_a_pagar() for v in lista_ventas]

    suma_sub_totales = np.sum(sub_totales)
    suma_valor_iva = np.sum(valores_iva)
    suma_totales = np.sum(totales)

    cantidad_ventas = len(lista_ventas)

    # Pasar las ventas y la suma al contexto de la plantilla
    return render(request, 'admin/businessmodel/Sales/tools/history-incomes/product/history.html', {
        'venta': venta,
        'lista_ventas': lista_ventas,
        'suma_totales': suma_totales,
        'suma_sub_totales': suma_sub_totales,
        'suma_valor_iva': suma_valor_iva,
        'cantidad_ventas': cantidad_ventas,
        'total_dias': total_dias,
        'total_horas': total_horas,
    })

@staff_member_required
def history_incomes_category(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    
    # Obtener fechas, horas y montos desde la solicitud
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')
    nombre_categoria = request.GET.get('nombre_categoria')
    monto_minimo = request.GET.get('monto_minimo')  # Nuevo filtro
    monto_maximo = request.GET.get('monto_maximo')  # Nuevo filtro

    # Filtrar lista_ventas
    lista_ventas = Venta.objects.all()  # Obtener todas las ventas inicialmente

    # Filtrar las ventas según el rango de fechas y horas
    if fecha_inicio and hora_inicio:
        inicio = datetime.strptime(f"{fecha_inicio} {hora_inicio}", "%Y-%m-%d %H:%M")
    else:
        inicio = None

    if fecha_fin and hora_fin:
        fin = datetime.strptime(f"{fecha_fin} {hora_fin}", "%Y-%m-%d %H:%M")
    else:
        fin = None

    if fecha_inicio and fecha_fin:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d") + timedelta(days=1)  # Incluir el último día
        lista_ventas = lista_ventas.filter(fecha__range=(inicio.date(), fin.date()))

    if inicio and fin:
        lista_ventas = lista_ventas.filter(fecha__range=(inicio.date(), fin.date()))

    # Filtrar por nombre de producto
    if nombre_categoria:
        lista_ventas = lista_ventas.filter(items__category__category_name__icontains=nombre_categoria)

    # Filtrar por monto mínimo y máximo
    if monto_minimo:
        lista_ventas = lista_ventas.filter(total_a_pagar__gte=float(monto_minimo))  # Monto mínimo
    if monto_maximo:
        lista_ventas = lista_ventas.filter(total_a_pagar__lte=float(monto_maximo))  # Monto máximo

    # Calcular las diferencias en días y horas entre las ventas
    diferencias = []
    for i in range(1, len(lista_ventas)):
        fecha1 = lista_ventas[i-1].fecha
        fecha2 = lista_ventas[i].fecha
        diferencia = fecha2 - fecha1
        diferencias.append(diferencia)

    # Sumar todas las diferencias
    total_diferencia = sum(diferencias, timedelta())
    total_dias = total_diferencia.days
    total_horas = total_diferencia.total_seconds() // 3600

    # Calcular totales
    sub_totales = [v.sub_total() for v in lista_ventas]
    valores_iva = [v.valor_iva() for v in lista_ventas]
    totales = [v.total_a_pagar() for v in lista_ventas]

    suma_sub_totales = np.sum(sub_totales)
    suma_valor_iva = np.sum(valores_iva)
    suma_totales = np.sum(totales)

    cantidad_ventas = len(lista_ventas)

    # Pasar las ventas y la suma al contexto de la plantilla
    return render(request, 'admin/businessmodel/Sales/tools/history-incomes/category/history.html', {
        'venta': venta,
        'lista_ventas': lista_ventas,
        'suma_totales': suma_totales,
        'suma_sub_totales': suma_sub_totales,
        'suma_valor_iva': suma_valor_iva,
        'cantidad_ventas': cantidad_ventas,
        'total_dias': total_dias,
        'total_horas': total_horas,
    })



@staff_member_required
def admin_comprobante_historial_pdf(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener parámetros para filtrar
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')
    nombre_cliente = request.GET.get('nombre_cliente')
    monto_min = request.GET.get('monto_min', 0)
    monto_max = request.GET.get('monto_max', 1000000000)

    # Filtrar lista_ventas usando la misma lógica que en historial_ventas
    lista_ventas = Venta.objects.all()

    # Procesar fechas
    if fecha_inicio and hora_inicio:
        inicio = datetime.strptime(f"{fecha_inicio} {hora_inicio}", "%Y-%m-%d %H:%M")
    else:
        inicio = None

    if fecha_fin and hora_fin:
        fin = datetime.strptime(f"{fecha_fin} {hora_fin}", "%Y-%m-%d %H:%M")
    else:
        fin = None

    # Filtrar por rango de fechas
    if inicio and fin:
        lista_ventas = lista_ventas.filter(fecha__range=(inicio.date(), fin.date()))

    # Filtrar por nombre del cliente
    if nombre_cliente:
        lista_ventas = lista_ventas.filter(first_name__icontains=nombre_cliente)

    # Filtrar por rango de monto
    if monto_min and monto_max:
        lista_ventas = lista_ventas.filter(monto__gte=monto_min, monto__lte=monto_max)
    elif monto_min:
        lista_ventas = lista_ventas.filter(monto__gte=monto_min)
    elif monto_max:
        lista_ventas = lista_ventas.filter(monto__lte=monto_max)

    # Calcular totales para el PDF
    sub_totales = [v.sub_total() for v in lista_ventas]
    valores_iva = [v.valor_iva() for v in lista_ventas]
    totales = [v.total_a_pagar() for v in lista_ventas]

    suma_sub_totales = np.sum(sub_totales)
    suma_valor_iva = np.sum(valores_iva)
    suma_totales = np.sum(totales)

    cantidad_ventas = len(lista_ventas)

    # Renderizar HTML para el PDF
    html = render_to_string('admin/businessmodel/ventas/reportes/historial_comprobante.html',
                            {
                                'venta': venta,
                                'lista_ventas': lista_ventas,
                                'valores_iva': valores_iva,
                                'suma_totales': suma_totales,
                                'suma_sub_totales': suma_sub_totales,
                                'suma_valor_iva': suma_valor_iva,
                                'cantidad_ventas': cantidad_ventas,
                            })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=historial_comprobante_{}.pdf'.format(venta.id)

    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
        stylesheets=[weasyprint.CSS('businessmodel/static/css/comprobante_metricas_venta.css')],
        presentational_hints=True)

    return response


@staff_member_required
def admin_comprobante_historial_product_pdf(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener parámetros para filtrar
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')
    nombre_producto = request.GET.get('nombre_producto')
    monto_min = request.GET.get('monto_min', 0)
    monto_max = request.GET.get('monto_max', 1000000000)

    # Filtrar lista_ventas usando la misma lógica que en historial_ventas
    lista_ventas = Venta.objects.all()

    # Procesar fechas
    if fecha_inicio and hora_inicio:
        inicio = datetime.strptime(f"{fecha_inicio} {hora_inicio}", "%Y-%m-%d %H:%M")
    else:
        inicio = None

    if fecha_fin and hora_fin:
        fin = datetime.strptime(f"{fecha_fin} {hora_fin}", "%Y-%m-%d %H:%M")
    else:
        fin = None

    # Filtrar por rango de fechas
    if inicio and fin:
        lista_ventas = lista_ventas.filter(fecha__range=(inicio.date(), fin.date()))

    # # Filtrar por nombre de producto
    if nombre_producto:
        lista_ventas = lista_ventas.filter(items__product__nombre__icontains=nombre_producto)

    # Filtrar por rango de monto
    if monto_min and monto_max:
        lista_ventas = lista_ventas.filter(monto__gte=monto_min, monto__lte=monto_max)
    elif monto_min:
        lista_ventas = lista_ventas.filter(monto__gte=monto_min)
    elif monto_max:
        lista_ventas = lista_ventas.filter(monto__lte=monto_max)

    # Calcular totales para el PDF
    sub_totales = [v.sub_total() for v in lista_ventas]
    valores_iva = [v.valor_iva() for v in lista_ventas]
    totales = [v.total_a_pagar() for v in lista_ventas]

    suma_sub_totales = np.sum(sub_totales)
    suma_valor_iva = np.sum(valores_iva)
    suma_totales = np.sum(totales)

    cantidad_ventas = len(lista_ventas)

    # Renderizar HTML para el PDF
    html = render_to_string('admin/businessmodel/ventas/reportes/historial_comprobante_productos.html',
                            {
                                'venta': venta,
                                'lista_ventas': lista_ventas,
                                'valores_iva': valores_iva,
                                'suma_totales': suma_totales,
                                'suma_sub_totales': suma_sub_totales,
                                'suma_valor_iva': suma_valor_iva,
                                'cantidad_ventas': cantidad_ventas,
                            })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=historial_comprobante_{}.pdf'.format(venta.id)

    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
        stylesheets=[weasyprint.CSS('businessmodel/static/css/comprobante_metricas_venta.css')],
        presentational_hints=True)

    return response


@staff_member_required
def admin_comprobante_historial_category_pdf(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener parámetros para filtrar
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')
    nombre_categoria = request.GET.get('nombre_categoria')
    monto_min = request.GET.get('monto_min', 0)
    monto_max = request.GET.get('monto_max', 1000000000)

    # Filtrar lista_ventas usando la misma lógica que en historial_ventas
    lista_ventas = Venta.objects.all()

    # Procesar fechas
    if fecha_inicio and hora_inicio:
        inicio = datetime.strptime(f"{fecha_inicio} {hora_inicio}", "%Y-%m-%d %H:%M")
    else:
        inicio = None

    if fecha_fin and hora_fin:
        fin = datetime.strptime(f"{fecha_fin} {hora_fin}", "%Y-%m-%d %H:%M")
    else:
        fin = None

    # Filtrar por rango de fechas
    if inicio and fin:
        lista_ventas = lista_ventas.filter(fecha__range=(inicio.date(), fin.date()))

    # Filtrar por nombre de producto
    if nombre_categoria:
        lista_ventas = lista_ventas.filter(items__category__category_name__icontains=nombre_categoria)

    # Filtrar por rango de monto
    if monto_min and monto_max:
        lista_ventas = lista_ventas.filter(monto__gte=monto_min, monto__lte=monto_max)
    elif monto_min:
        lista_ventas = lista_ventas.filter(monto__gte=monto_min)
    elif monto_max:
        lista_ventas = lista_ventas.filter(monto__lte=monto_max)

    # Calcular totales para el PDF
    sub_totales = [v.sub_total() for v in lista_ventas]
    valores_iva = [v.valor_iva() for v in lista_ventas]
    totales = [v.total_a_pagar() for v in lista_ventas]

    suma_sub_totales = np.sum(sub_totales)
    suma_valor_iva = np.sum(valores_iva)
    suma_totales = np.sum(totales)

    cantidad_ventas = len(lista_ventas)

    # Renderizar HTML para el PDF
    html = render_to_string('admin/businessmodel/ventas/reportes/historial_comprobante_categorias.html',
                            {
                                'venta': venta,
                                'lista_ventas': lista_ventas,
                                'valores_iva': valores_iva,
                                'suma_totales': suma_totales,
                                'suma_sub_totales': suma_sub_totales,
                                'suma_valor_iva': suma_valor_iva,
                                'cantidad_ventas': cantidad_ventas,
                            })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=historial_comprobante_{}.pdf'.format(venta.id)

    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
        stylesheets=[weasyprint.CSS('businessmodel/static/css/comprobante_metricas_venta.css')],
        presentational_hints=True)

    return response




@staff_member_required
def historial_ventas_productos(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    # Obtener fechas y horas desde la solicitud
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')
    nombre_producto = request.GET.get('nombre_producto')

     # Filtrar lista_ventas
    lista_ventas = Venta.objects.all()  # Obtener todas las ventas inicialmente

    # Filtrar las ventas según el rango de fechas y horas
    if fecha_inicio and hora_inicio:
        inicio = datetime.strptime(f"{fecha_inicio} {hora_inicio}", "%Y-%m-%d %H:%M")
    else:
        inicio = None

    if fecha_fin and hora_fin:
        fin = datetime.strptime(f"{fecha_fin} {hora_fin}", "%Y-%m-%d %H:%M")
    else:
        fin = None

    if fecha_inicio and fecha_fin:
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d") + timedelta(days=1)  # Incluir el último día
        lista_ventas = lista_ventas.filter(fecha__range=(inicio.date(), fin.date()))

   

    if inicio and fin:
        lista_ventas = lista_ventas.filter(fecha__range=(inicio.date(), fin.date()))

    if nombre_producto:
        lista_ventas = lista_ventas.filter(items__product__nombre__icontains=nombre_producto)

    # Calcular las diferencias en días y horas entre las ventas
    diferencias = []
    for i in range(1, len(lista_ventas)):
        fecha1 = lista_ventas[i-1].fecha
        fecha2 = lista_ventas[i].fecha
        diferencia = fecha2 - fecha1
        diferencias.append(diferencia)

    # Sumar todas las diferencias
    total_diferencia = sum(diferencias, timedelta())
    total_dias = total_diferencia.days
    total_horas = total_diferencia.total_seconds() // 3600

    # Calcular totales
    sub_totales = [v.sub_total() for v in lista_ventas]
    valores_iva = [v.valor_iva() for v in lista_ventas]
    totales = [v.total_a_pagar() for v in lista_ventas]

    suma_sub_totales = np.sum(sub_totales)
    suma_valor_iva = np.sum(valores_iva)
    suma_totales = np.sum(totales)

    cantidad_ventas = len(lista_ventas)

    # Pasar las ventas y la suma al contexto de la plantilla
    return render(request, 'admin/businessmodel/ventas/tools/historial_ventas_productos.html', {
        'venta':venta,
        'lista_ventas': lista_ventas,
        'suma_totales': suma_totales,
        'suma_sub_totales': suma_sub_totales,
        'suma_valor_iva': suma_valor_iva,
        'cantidad_ventas': cantidad_ventas,
        'total_dias': total_dias,
        'total_horas': total_horas,
    })


#App metricas

@staff_member_required
def admin_metricas(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    return render(request,
                  'admin/businessmodel/ventas/introduccion/inicio_metricas.html',{'venta': venta,})



    #---------------------------------------------------------------------
   
@cache_page(60 * 1)  # Caché por 1 minuto
@staff_member_required
def income_scatter(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener el formulario y procesar la entrada
    form = FiltroVentasForm(request.GET or None)

    # Obtener los valores de fecha y hora del formulario
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')
    monto_min = request.GET.get('monto_min', 0)
    monto_max = request.GET.get('monto_max', 1000000000)

    # Inicializar variables
    total_dias = 0
    total_horas = 0
    total_monto = 0
    quince_por_ciento = 0
    venta_total = 0
    porcentaje_cantidad_ventas = 0
    cantidad_ventas = 0

    # Obtener datos de ventas usando Django ORM
    ventas = Venta.objects.all().values('id', 'fecha', 'hora', 'monto')

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(list(ventas))

    # Verificar si el DataFrame no está vacío
    if df.empty:
        return HttpResponse("No hay datos disponibles", status=204)

    # Crear un datetime combinando fecha y hora
    df['datetime'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

    # Filtrar por rango de fechas y horas
    if fecha_inicio and hora_inicio and fecha_fin and hora_fin:
        fecha_inicio_dt = pd.to_datetime(f"{fecha_inicio} {hora_inicio}")
        fecha_fin_dt = pd.to_datetime(f"{fecha_fin} {hora_fin}")
        # Calcular la diferencia de tiempo
        diferencia = fecha_fin_dt - fecha_inicio_dt
        total_dias = diferencia.days
        total_horas = diferencia.total_seconds() / 3600  # Convertir segundos a horas
        
        df_filtrado = df[(df['datetime'] >= fecha_inicio_dt) & (df['datetime'] <= fecha_fin_dt)]
    else:
        df_filtrado = df

    # Eliminar duplicados y asegurarse de que haya suficientes datos
    df_filtrado = df_filtrado.drop_duplicates(subset=['id', 'monto'])

    # Crear figura y ejes
    fig, ax = plt.subplots(figsize=(16, 8))
    fig.patch.set_facecolor('#161616')  # Color de fondo de la figura
    ax.set_facecolor('#161616')  # Color de fondo del eje

    # Verificar si hay datos en el rango filtrado
    if not df_filtrado.empty:
        ax.scatter(df_filtrado['id'], df_filtrado['monto'], color='blue', label='Monto por Venta', alpha=0.9)


        # Agrupar montos por ID único
        unique_montos = df_filtrado.groupby('id')['monto'].mean().reset_index()

        if len(unique_montos) >= 1:
            x_smooth = np.linspace(unique_montos['id'].min(), unique_montos['id'].max(), 300)
            spl = make_interp_spline(unique_montos['id'], unique_montos['monto'], k=2)  # Suavizado cúbico
            y_smooth = spl(x_smooth)

             # Encontrar máximos locales
            indices_maximos = argrelextrema(y_smooth, np.greater)[0]
            maximos_x = x_smooth[indices_maximos]
            maximos_y = y_smooth[indices_maximos]

            # Encontrar mínimos locales
            indices_minimos = argrelextrema(y_smooth, np.less)[0]
            minimos_x = x_smooth[indices_minimos]
            minimos_y = y_smooth[indices_minimos]

            # Contar máximos locales
            numero_maximos = len(indices_maximos)
            # Contar mínimos locales
            numero_minimos = len(indices_minimos)

            # Inicializar rapidez y rapidez_d
            rapidez = 0
            rapidez_d = 0

            # Calcular rapidez solo si hay máximos
            if numero_maximos > 0:
                rapidez = (numero_minimos / numero_maximos) * 100

           # Calcular rapidez_d solo si hay mínimos
            if numero_minimos > 0:
                rapidez_d = (numero_maximos / numero_minimos) * 100

            # Dibujar los máximos locales
          #  ax.scatter(maximos_x, maximos_y, color='yellow', label='Máximos Locales', s=100)
          #  ax.plot(maximos_x, maximos_y, color='yellow', linestyle='--')  # Línea entre máximos locales

            ax.fill_between(x_smooth, y_smooth, color='darkred', alpha=0.1)  # Área bajo la curva
            ax.plot(x_smooth, y_smooth, color='red', alpha=0.7, linestyle='-')

        for i in range(len(df_filtrado)):
            monto_str = f'${df_filtrado["monto"].iloc[i]}'
            ax.annotate(monto_str,
                        (df_filtrado['id'].iloc[i], df_filtrado['monto'].iloc[i]),
                        textcoords="offset points",
                        xytext=(2, 9),
                        ha='left',
                        fontsize=8,
                        rotation=90,
                        color='white')

    

        

        # Calcular el monto total en el rango seleccionado
        lista_ventas = Venta.objects.all() 
         # Contar máximos locales
        numero_maximos = len(indices_maximos)
            # Contar mínimos locales
        numero_minimos = len(indices_minimos)

            # Inicializar rapidez y rapidez_d
        rapidez = 0
        rapidez_d = 0

            # Calcular rapidez solo si hay máximos
        if numero_maximos > 0:
            rapidez = (numero_minimos / numero_maximos) * 100

           # Calcular rapidez_d solo si hay mínimos
        if numero_minimos > 0:
            rapidez_d = (numero_maximos / numero_minimos) * 100
       
        #cantidades netas
        sub_total_variable_cost = Decimal('0.00')

        # Suponiendo que tienes una relación con VentaItem
        venta_items = VentaItem.objects.filter(venta=venta)

        for item in venta_items:
            sub_total_variable_cost += item.get_variable_cost()

         # Filtrar por rango de monto
        # Filtrar por rango de monto
        if monto_min:
            df_filtrado = df_filtrado[df_filtrado['monto'] >= float(monto_min)]
        if monto_max:
            df_filtrado = df_filtrado[df_filtrado['monto'] <= float(monto_max)]

            


        cantidad_neta_ventas = len(lista_ventas)
        sub_total_variable_cost
        total_monto_neto = Venta.objects.aggregate(total=Sum('monto'))['total'] or 0  # Usa la función aggregate para sumar los montos
        total_monto_iva_neto = total_monto_neto*Decimal(0.15)
        sub_total_monto_neto = total_monto_neto - total_monto_iva_neto
        promedio_total_venta = ( total_monto_neto/cantidad_neta_ventas)
        
        #cantidades filtradas
        cantidad_ventas = len(df_filtrado)
        total_monto = df_filtrado['monto'].sum()
        promedio_venta = (total_monto/cantidad_ventas)

        

         # Calcular el 15% de total_monto filtrado
        quince_por_ciento = total_monto * Decimal(0.15)
        venta_total = total_monto - quince_por_ciento

          #Diferencia respecto a los valores totales
        dif_cantidad_ventas = cantidad_neta_ventas - cantidad_ventas
        dif_monto_ventas = sub_total_monto_neto - venta_total
        
        #porcentajes de venta
        porcentaje_cantidad_ventas = (cantidad_ventas / cantidad_neta_ventas) 
        porcentaje_monto_ventas = (venta_total / sub_total_monto_neto) * 100
        porcentaje_iva_ventas =(quince_por_ciento/total_monto_iva_neto) * 100
        porcentaje_promedio_venta = (promedio_venta /promedio_total_venta) * 100
        porcentaje_promedio_ingresos = (total_monto/total_monto_neto) * 100
        
        # Añadir el número de ventas al eje superior
        ax2 = ax.twiny()  # Crear un eje superior
        #ax2.set_xlabel('ID de Ventas', color='white')
        ax2.tick_params(axis='x', labelcolor='white')

        # Ajustar ticks del eje superior para mostrar los IDs de las ventas
        ax2.set_xticks(df_filtrado['id'])
        ax2.set_xticklabels(df_filtrado['id'], color='white')  # Mostrar ID de cada venta

        # Alinear el eje superior con los puntos
        ax2.set_xlim(ax.get_xlim())  # Asegurarse de que el rango del eje superior coincida con el eje principal

    else:
        ax.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')
        ax.set_xlim(df['id'].min(), df['id'].max())
        ax.set_ylim(0, float(df['monto'].max()) * 1.1)

    ax.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.set_xticks(df_filtrado['id'].unique())
    ax.set_xticklabels(df_filtrado['fecha'], rotation=45, ha='right', color='white',fontsize=7)  # Solo mostrar la fecha
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.axvline(x= venta.id  , color='green', linestyle='--', linewidth=1, label='cantidad de ventas')
    ax.axhline(y=promedio_venta, color='darkgray', linestyle='-', linewidth=1, label='promedio_venta')
    ax.axhline(y=promedio_total_venta, color='darkorange', linestyle='-', linewidth=1, label='promedio_total_venta')

    for label in ax.get_yticklabels():
        label.set_color('white')

    for spine in ax.spines.values():
        spine.set_color('black')  # Cambia el color del marco a blanco
        spine.set_linewidth(2)  

  

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)

    image_data = buf.getvalue()
    grafico_montos = base64.b64encode(image_data).decode('utf-8')
     # Renderizar HTML para el PDF
    html = render_to_string('admin/businessmodel/ventas/reportes/metricas_comprobante.html',
                            {
                                'venta': venta,
                                'grafico_montos': grafico_montos,
                                'form': form,
                                'fecha_inicio': fecha_inicio,
                                'hora_inicio': hora_inicio,
                                'fecha_fin': fecha_fin,
                                'hora_fin': hora_fin,
                                'total_monto': total_monto,
                                'total_dias': total_dias,
                                'total_horas': total_horas,
                                'cantidad_ventas': cantidad_ventas,
                                'cantidad_neta_ventas':cantidad_neta_ventas,
                                'quince_por_ciento': quince_por_ciento,
                                'venta_total': venta_total,
                                'porcentaje_cantidad_ventas': porcentaje_cantidad_ventas,
                                'total_monto_neto':total_monto_neto,
                                'porcentaje_monto_ventas':porcentaje_monto_ventas,
                                'porcentaje_iva_ventas':porcentaje_iva_ventas,
                                'promedio_venta':promedio_venta,
                                'total_monto_iva_neto':total_monto_iva_neto,
                                'porcentaje_promedio_venta':porcentaje_promedio_venta,
                                'promedio_total_venta':promedio_total_venta,
                                'total_monto':total_monto,
                                'porcentaje_promedio_ingresos':porcentaje_promedio_ingresos,
                                'numero_maximos':numero_maximos,
                                'numero_minimos':numero_minimos,
                                'rapidez':rapidez,
                                'rapidez_d':rapidez_d,
                                'sub_total_variable_cost':sub_total_variable_cost,
                            })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=metricas_comprobante_{}.pdf'.format(venta.id)

    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
        stylesheets=[weasyprint.CSS('businessmodel/static/css/comprobante_venta.css')],
        presentational_hints=True)

    

    return render(request, 'admin/businessmodel/Sales/tools/distributions-incomes/sales_distribution.html', {
        'response':response,
        'venta': venta,
        'grafico_montos': grafico_montos,
        'form': form,
        'fecha_inicio': fecha_inicio,
        'hora_inicio': hora_inicio,
        'fecha_fin': fecha_fin,
        'hora_fin': hora_fin,
        'total_monto': total_monto,
        'total_dias': total_dias,
        'total_horas': total_horas,
        'cantidad_ventas': cantidad_ventas,
        'cantidad_neta_ventas':cantidad_neta_ventas,
        'quince_por_ciento': quince_por_ciento,
        'venta_total': venta_total,
        'porcentaje_cantidad_ventas': porcentaje_cantidad_ventas,
        'total_monto_neto':total_monto_neto,
        'porcentaje_monto_ventas':porcentaje_monto_ventas,
        'porcentaje_iva_ventas':porcentaje_iva_ventas,
        'promedio_venta':promedio_venta,
        'total_monto_iva_neto':total_monto_iva_neto,
        'porcentaje_promedio_venta':porcentaje_promedio_venta,
        'promedio_total_venta':promedio_total_venta,
        'total_monto':total_monto,
        'porcentaje_promedio_ingresos':porcentaje_promedio_ingresos,
        'numero_maximos':numero_maximos,
        'numero_minimos':numero_minimos,
        'rapidez':rapidez,
        'rapidez_d':rapidez_d,
        'sub_total_variable_cost':sub_total_variable_cost,

    })
    
@cache_page(60 * 1)  # Caché por 1 minuto
@staff_member_required
def metricas_ventas_comprobante(request,venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener el formulario y procesar la entrada
    form = FiltroVentasForm(request.GET or None)

    # Obtener los valores de fecha y hora del formulario
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')

    # Inicializar variables
    total_dias = 0
    total_horas = 0
    total_monto = 0
    quince_por_ciento = 0
    venta_total = 0
    porcentaje_cantidad_ventas = 0
    cantidad_ventas = 0

    # Obtener datos de ventas usando Django ORM
    ventas = Venta.objects.all().values('id', 'fecha', 'hora', 'monto')

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(list(ventas))

    # Verificar si el DataFrame no está vacío
    if df.empty:
        return HttpResponse("No hay datos disponibles", status=204)

    # Crear un datetime combinando fecha y hora
    df['datetime'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

    # Filtrar por rango de fechas y horas
    if fecha_inicio and hora_inicio and fecha_fin and hora_fin:
        fecha_inicio_dt = pd.to_datetime(f"{fecha_inicio} {hora_inicio}")
        fecha_fin_dt = pd.to_datetime(f"{fecha_fin} {hora_fin}")
        # Calcular la diferencia de tiempo
        diferencia = fecha_fin_dt - fecha_inicio_dt
        total_dias = diferencia.days
        total_horas = diferencia.total_seconds() / 3600  # Convertir segundos a horas
        
        df_filtrado = df[(df['datetime'] >= fecha_inicio_dt) & (df['datetime'] <= fecha_fin_dt)]
    else:
        df_filtrado = df

    # Eliminar duplicados y asegurarse de que haya suficientes datos
    df_filtrado = df_filtrado.drop_duplicates(subset=['id', 'monto'])

    # Crear figura y ejes
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('white')  # Color de fondo de la figura
    ax.set_facecolor('white')  # Color de fondo del eje
    

    # Verificar si hay datos en el rango filtrado
    if not df_filtrado.empty:
        ax.scatter(df_filtrado['id'], df_filtrado['monto'], color='blue', label='Monto por Venta', alpha=0.9, s=50)

        # Agrupar montos por ID único
        unique_montos = df_filtrado.groupby('id')['monto'].mean().reset_index()

        if len(unique_montos) >= 1:
            x_smooth = np.linspace(unique_montos['id'].min(), unique_montos['id'].max(), 300)
            spl = make_interp_spline(unique_montos['id'], unique_montos['monto'], k=2)  # Suavizado cúbico
            y_smooth = spl(x_smooth)

             # Encontrar máximos locales
            indices_maximos = argrelextrema(y_smooth, np.greater)[0]
            maximos_x = x_smooth[indices_maximos]
            maximos_y = y_smooth[indices_maximos]

            # Encontrar mínimos locales
            indices_minimos = argrelextrema(y_smooth, np.less)[0]
            minimos_x = x_smooth[indices_minimos]
            minimos_y = y_smooth[indices_minimos]

            # Contar máximos locales
            numero_maximos = len(indices_maximos)
            # Contar mínimos locales
            numero_minimos = len(indices_minimos)

            # Inicializar rapidez y rapidez_d
            rapidez = 0
            rapidez_d = 0

            # Calcular rapidez solo si hay máximos
            if numero_maximos > 0:
                rapidez = (numero_minimos / numero_maximos) * 100

           # Calcular rapidez_d solo si hay mínimos
            if numero_minimos > 0:
                rapidez_d = (numero_maximos / numero_minimos) * 100

            # Dibujar los máximos locales
          #  ax.scatter(maximos_x, maximos_y, color='yellow', label='Máximos Locales', s=100)
          #  ax.plot(maximos_x, maximos_y, color='yellow', linestyle='--')  # Línea entre máximos locales

        
        #cantidades filtradas
            cantidad_ventas = len(df_filtrado)
            total_monto = df_filtrado['monto'].sum()
            promedio_venta = (total_monto/cantidad_ventas)

        # Cantidades totales calculadas para grafico
            lista_ventas = Venta.objects.all() 
            cantidad_neta_ventas = len(lista_ventas)
            total_monto_neto = Venta.objects.aggregate(total=Sum('monto'))['total'] or 0  # Usa la función aggregate para sumar los montos
            total_monto_iva_neto = total_monto_neto*Decimal(0.15)
            sub_total_monto_neto = total_monto_neto - total_monto_iva_neto
            promedio_total_venta = ( total_monto_neto/cantidad_neta_ventas)
            promedio_numero_venta = (cantidad_neta_ventas - cantidad_ventas)
        
            ax.fill_between(x_smooth, y_smooth, color='#b80505', alpha=1)  # Área bajo la curva
            ax.plot(x_smooth, y_smooth, color='black', alpha=0.8, linestyle='-')
            # Agregar etiquetas a los ejes
            ax.set_xlabel('ID de Venta', fontsize=12, color='black')  # Etiqueta del eje X
            ax.set_ylabel('Distribución de ventas ($)', fontsize=12, color='black')  
            ax.axhline(y=promedio_venta, color='darkgray', linestyle='-', linewidth=2, label='promedio_venta')
            ax.axhline(y=promedio_total_venta, color='darkorange', linestyle='-', linewidth=2, label='promedio_total_venta')
            ax.axvline(x= venta.id  , color='green', linestyle='--', linewidth=2, label='cantidad de ventas')
         
            


           

        for i in range(len(df_filtrado)):
            monto_str = f'${df_filtrado["monto"].iloc[i]}'
            ax.annotate(monto_str,
                        (df_filtrado['id'].iloc[i], df_filtrado['monto'].iloc[i]),
                        textcoords="offset points",
                        xytext=(2, 9),
                        ha='left',
                        fontsize=11,
                        rotation=90,
                        color='blue')

        

        # Calcular el monto total en el rango seleccionado
        lista_ventas = Venta.objects.all() 
         # Contar máximos locales
        numero_maximos = len(indices_maximos)
            # Contar mínimos locales
        numero_minimos = len(indices_minimos)

            # Inicializar rapidez y rapidez_d
        rapidez = 0
        rapidez_d = 0

            # Calcular rapidez solo si hay máximos
        if numero_maximos > 0:
            rapidez = (numero_minimos / numero_maximos) * 100

           # Calcular rapidez_d solo si hay mínimos
        if numero_minimos > 0:
            rapidez_d = (numero_maximos / numero_minimos) * 100
       
        #cantidades netas
        sub_total_variable_cost = Decimal('0.00')

        # Suponiendo que tienes una relación con VentaItem
        venta_items = VentaItem.objects.filter(venta=venta)

        for item in venta_items:
            sub_total_variable_cost += item.get_variable_cost()


        cantidad_neta_ventas = len(lista_ventas)
        sub_total_variable_cost
        total_monto_neto = Venta.objects.aggregate(total=Sum('monto'))['total'] or 0  # Usa la función aggregate para sumar los montos
        total_monto_iva_neto = total_monto_neto*Decimal(0.15)
        sub_total_monto_neto = total_monto_neto - total_monto_iva_neto
        promedio_total_venta = ( total_monto_neto/cantidad_neta_ventas)
        
        #cantidades filtradas
        cantidad_ventas = len(df_filtrado)
        total_monto = df_filtrado['monto'].sum()
        promedio_venta = (total_monto/cantidad_ventas)

        

         # Calcular el 15% de total_monto filtrado
        quince_por_ciento = total_monto * Decimal(0.15)
        venta_total = total_monto - quince_por_ciento

          #Diferencia respecto a los valores totales
        dif_cantidad_ventas = cantidad_neta_ventas - cantidad_ventas
        dif_monto_ventas = sub_total_monto_neto - venta_total
        
        #porcentajes de venta
        porcentaje_cantidad_ventas = (cantidad_ventas / cantidad_neta_ventas) * 100
        porcentaje_monto_ventas = (venta_total / sub_total_monto_neto) * 100
        porcentaje_iva_ventas =(quince_por_ciento/total_monto_iva_neto) * 100
        porcentaje_promedio_venta = (promedio_venta /promedio_total_venta) * 100
        porcentaje_promedio_ingresos = (total_monto/total_monto_neto) * 100
        
        # Añadir el número de ventas al eje superior
        ax2 = ax.twiny()  # Crear un eje superior
        #ax2.set_xlabel(f'Distribución de ventas, desde: {fecha_inicio} hasta {fecha_fin}', color='black')
        ax2.tick_params(axis='x', labelcolor='black')
       # ax2.set_xlabel('ID de Ventas', color='black')
        ax.set_xlabel('Tiempo ', color='black')
       

        # Aquí puedes definir los colores y valores que deseas mostrar
        valor1 = promedio_venta 
        valor2 = promedio_total_venta
        color1 = 'darkgray'  # Color para el primer recuadro
        color2 = 'orange'  # Color para el segundo recuadro

# Añadir recuadros y texto
        rect1 = plt.Rectangle((0, 0), 1, 1, color=color1, alpha=0.5, label='Promedio de venta global: ${:.2f}'.format(valor1))
        rect2 = plt.Rectangle((0, 0), 1, 1, color=color2, alpha=0.5, label='Promedio Venta local: ${:.2f}'.format(valor2))

# Agregar recuadros al gráfico
        ax.add_patch(rect1)
        ax.add_patch(rect2)

# Posicionar los recuadros y el texto
        ax.text(0.2, 1.2,  ' - Total Monto: ${:.2f}'.format(valor1), color=color1, fontsize=12, ha='left', va='bottom', transform=ax.transAxes)
        ax.text(0.2, 1.12, ' - Promedio Venta: ${:.2f}'.format(valor2), color=color2, fontsize=12, ha='left', va='bottom', transform=ax.transAxes)

        # Ajustar ticks del eje superior para mostrar los IDs de las ventas
        ax2.set_xticks(df_filtrado['id'])
        ax2.set_xticklabels(df_filtrado['id'], color='black')  # Mostrar ID de cada venta

        # Alinear el eje superior con los puntos
        ax2.set_xlim(ax.get_xlim())  # Asegurarse de que el rango del eje superior coincida con el eje principal

    else:
        ax.set_title('No hay suficientes datos para mostrar el gráfico.', color='black')
        ax.set_xlim(df['id'].min(), df['id'].max())
        ax.set_ylim(0, float(df['monto'].max()) * 1.1)

    ax.grid(color='darkgray', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.set_xticks(df_filtrado['id'].unique())
    ax.set_xticklabels(df_filtrado['fecha'], rotation=45, ha='right', color='black',fontsize=7)  # Solo mostrar la fecha
    ax.yaxis.label.set_color('black')
    ax.xaxis.label.set_color('black')

    for label in ax.get_yticklabels():
        label.set_color('black')

    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.tight_layout()

        # Generación del código QR
    usuario = {
        'nombre': 'Juan Pérez',
        'email': 'juan.perez@example.com',
        'telefono': '123456789'
    }
    
    data = f"Nombre: {usuario['nombre']}, Email: {usuario['email']}, Teléfono: {usuario['telefono']}"
    qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=2, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="#f2f2f2")
    buffer_qr = BytesIO()
    img_qr.save(buffer_qr, format='PNG')
    buffer_qr.seek(0)
    qr_img_str = base64.b64encode(buffer_qr.read()).decode()

    # Guardar el gráfico en un objeto BytesIO
    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    image_data = buf.getvalue()
    grafico_montos = base64.b64encode(image_data).decode('utf-8')

    html = render_to_string('admin/businessmodel/ventas/reportes/metricas_comprobante.html',
                            {
                                'venta': venta,
                                'grafico_montos': grafico_montos,
                                'qr_img_str': qr_img_str,
                                'form': form,
                                'fecha_inicio': fecha_inicio,
                                'hora_inicio': hora_inicio,
                                'fecha_fin': fecha_fin,
                                'hora_fin': hora_fin,
                                'total_monto': total_monto,
                                'total_dias': total_dias,
                                'total_horas': total_horas,
                                'cantidad_ventas': cantidad_ventas,
                                'cantidad_neta_ventas':cantidad_neta_ventas,
                                'quince_por_ciento': quince_por_ciento,
                                'venta_total': venta_total,
                                'porcentaje_cantidad_ventas': porcentaje_cantidad_ventas,
                                'total_monto_neto':total_monto_neto,
                                'porcentaje_monto_ventas':porcentaje_monto_ventas,
                                'porcentaje_iva_ventas':porcentaje_iva_ventas,
                                'promedio_venta':promedio_venta,
                                'total_monto_iva_neto':total_monto_iva_neto,
                                'porcentaje_promedio_venta':porcentaje_promedio_venta,
                                'promedio_total_venta':promedio_total_venta,
                                'total_monto':total_monto,
                                'porcentaje_promedio_ingresos':porcentaje_promedio_ingresos,
                                'numero_maximos':numero_maximos,
                                'numero_minimos':numero_minimos,
                                'rapidez':rapidez,
                                'rapidez_d':rapidez_d,
                                'sub_total_variable_cost':sub_total_variable_cost,
                            })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=metricas_comprobante_{}.pdf'.format(venta.id)

    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
        stylesheets=[weasyprint.CSS('businessmodel/static/css/comprobante_metricas_venta.css')],
        presentational_hints=True)

    
    return response



@cache_page(60 * 1)  # Caché por 1 minuto
@staff_member_required
def income_histogram_amount(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener el formulario y procesar la entrada
    form = FiltroVentasForm(request.GET or None)

    # Obtener los valores de fecha y hora del formulario
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')

    # Obtener datos de ventas usando Django ORM
    ventas = Venta.objects.all().values('id', 'fecha', 'hora', 'monto', 'payment_gateway')

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(list(ventas))

    # Verificar si el DataFrame no está vacío
    if df.empty:
        return HttpResponse("No hay datos disponibles", status=204)

    # Convertir la columna 'monto' a float si es decimal
    df['monto'] = df['monto'].astype(float)

    # Crear un datetime combinando fecha y hora
    df['datetime'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

    # Filtrar por rango de fechas y horas
    if fecha_inicio and hora_inicio and fecha_fin and hora_fin:
        fecha_inicio_dt = pd.to_datetime(f"{fecha_inicio} {hora_inicio}")
        fecha_fin_dt = pd.to_datetime(f"{fecha_fin} {hora_fin}")
        df_filtrado = df[(df['datetime'] >= fecha_inicio_dt) & (df['datetime'] <= fecha_fin_dt)]
    else:
        df_filtrado = df

    # Eliminar duplicados y asegurarse de que haya suficientes datos
    df_filtrado = df_filtrado.drop_duplicates(subset=['id', 'monto'])

    # Crear la columna 'fecha' en el DataFrame original
    df['fecha'] = df['datetime'].dt.date

    # Agrupar montos por fecha y calcular la suma de montos vendidos (filtrado)
    frecuencias_montos = df_filtrado.groupby('fecha')['monto'].sum().reset_index(name='total_vendidos')

    # Agrupar montos por fecha y calcular la suma de montos vendidos (sin filtrar)
    frecuencias_montos_total = df.groupby('fecha')['monto'].sum().reset_index(name='total_vendidos')

    # Agrupar montos por gateway_payment
    distribucion_gateway = df_filtrado.groupby('payment_gateway')['monto'].sum().reset_index(name='total_vendido_gateway')

    # Agrupar montos por gateway_payment (sin filtrar)
    distribucion_gateway_total = df.groupby('payment_gateway')['monto'].sum().reset_index(name='total_vendido_gateway_total')
    # Convertir a un formato que usa columnas en lugar de filas
    #distribucion_gateway_pivot = distribucion_gateway.pivot(index=None, columns='payment_gateway', values='total_vendido_gateway')
    # Convertir a un diccionario para pasar a la plantilla
    # Usar pivot_table para crear una tabla
    distribucion_gateway_pivot = distribucion_gateway.pivot_table(index=None, columns='payment_gateway', values='total_vendido_gateway', aggfunc='sum', fill_value=0)
    # Convertir a un diccionario para pasar a la plantilla
    distribucion_gateway_dict = distribucion_gateway_pivot.to_dict(orient='records')

    # Cálculo de estadísticas para los montos filtrados
    estadisticas_filtradas = {
        'promedio': frecuencias_montos['total_vendidos'].mean(),
        'std_dev': frecuencias_montos['total_vendidos'].std(),
        'mediana': frecuencias_montos['total_vendidos'].median(),
        'maximo': frecuencias_montos['total_vendidos'].max(),
        'minimo': frecuencias_montos['total_vendidos'].min(),
        'stability': (frecuencias_montos['total_vendidos'].std() / frecuencias_montos['total_vendidos'].mean())*100 if frecuencias_montos['total_vendidos'].mean() != 0 else 0
    }

    # Cálculo de estadísticas para los montos sin filtrar
    estadisticas_totales = {
        'promedio': frecuencias_montos_total['total_vendidos'].mean(),
        'std_dev': frecuencias_montos_total['total_vendidos'].std(),
        'mediana': frecuencias_montos_total['total_vendidos'].median(),
        'maximo': frecuencias_montos_total['total_vendidos'].max(),
        'minimo': frecuencias_montos_total['total_vendidos'].min(),
        'stability': (frecuencias_montos_total['total_vendidos'].std() / frecuencias_montos_total['total_vendidos'].mean())*100 if frecuencias_montos['total_vendidos'].mean() != 0 else 0
    }

    #Valores 

    promedio_filtrado = frecuencias_montos['total_vendidos'].mean()
    std_dev_filtrado = frecuencias_montos['total_vendidos'].std()
    mediana_filtrado = frecuencias_montos['total_vendidos'].median()
    maximo_filtrado = frecuencias_montos['total_vendidos'].max()
    minimo_filtrado = frecuencias_montos['total_vendidos'].min()

    promedio_total = frecuencias_montos_total['total_vendidos'].mean()
    std_dev_total = frecuencias_montos_total['total_vendidos'].std()
    mediana_total =  frecuencias_montos_total['total_vendidos'].median()
    maximo_total= frecuencias_montos_total['total_vendidos'].max()
    minimo_total = frecuencias_montos_total['total_vendidos'].min()

    porcentaje_promedio =  (promedio_total/promedio_filtrado)*100


    # Crear figura y ejes (2 filas y 1 columna)
    fig, axs = plt.subplots(2, 1, figsize=(20, 16))
    fig.patch.set_facecolor('#161616')  # Color de fondo de la figura

    # Histograma de total de montos vendidos por fecha (filtrado)
    ax1 = axs[0]
    if not frecuencias_montos.empty:
        bars1 = ax1.bar(frecuencias_montos['fecha'], frecuencias_montos['total_vendidos'], color='blue', alpha=0.7, label='Filtrado')
        
        if not frecuencias_montos_total.empty:
            bars2 = ax1.bar(frecuencias_montos_total['fecha'], frecuencias_montos_total['total_vendidos'], color='cyan', alpha=0.4, label='Total (Sin Filtrar)')

        ax1.set_title('Total de Montos Vendidos por Fecha', color='white')
        ax1.set_xlabel('Fecha', color='white')
        ax1.set_ylabel('Total Vendido', color='white')
        ax1.set_xticks(frecuencias_montos['fecha'])
        ax1.set_xticklabels(frecuencias_montos['fecha'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax1.bar_label(bars1, label_type='edge', padding=3, color='white')
        if not frecuencias_montos_total.empty:
            ax1.bar_label(bars2, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x = np.arange(len(frecuencias_montos))
        z = np.polyfit(x, frecuencias_montos['total_vendidos'], 1)  # Ajuste lineal
        p = np.polyval(z, x)
        ax1.plot(frecuencias_montos['fecha'], p, color='orange', label='Tendencia', linewidth=2)

        # Calcular la pendiente
        pendiente = z[0]  # La pendiente es el primer elemento de z

# Interpretar la tendencia
        if pendiente > 0:
            tendencia_texto = "La tendencia está en aumento."
        elif pendiente < 0:
            tendencia_texto = "La tendencia está en disminución."
        else:
            tendencia_texto = "La tendencia es constante."

# Añadir texto sobre la tendencia en la gráfica
        ax1.text(0.05, 0.85, tendencia_texto, ha='left', va='top', fontsize=12, color='yellow', transform=ax1.transAxes)

        # Texto para la leyenda
        stats_text1 = (
            f'Promedio (Filtrado): {estadisticas_filtradas["promedio"]:.2f}\n'
            f'Desviación Estándar (Filtrado): {estadisticas_filtradas["std_dev"]:.2f}\n'
            f'Mediana (Filtrado): {estadisticas_filtradas["mediana"]:.2f}\n'
            f'Máximo (Filtrado): {estadisticas_filtradas["maximo"]:.2f}\n'
            f'Mínimo (Filtrado): {estadisticas_filtradas["minimo"]:.2f}\n'
            f'Promedio (Total): {estadisticas_totales["promedio"]:.2f}\n'
            f'Desviación Estándar (Total): {estadisticas_totales["std_dev"]:.2f}\n'
            f'Mediana (Total): {estadisticas_totales["mediana"]:.2f}\n'
            f'Máximo (Total): {estadisticas_totales["maximo"]:.2f}\n'
            f'Mínimo (Total): {estadisticas_totales["minimo"]:.2f}'
        )
        
        # Leyenda con estadísticas
        ax1.text(0.05, 0.97, stats_text1, ha='left', va='top', fontsize=12, color='white', transform=ax1.transAxes)

        # Agregar la leyenda
        ax1.legend(loc='upper left', fontsize=10)

    else:
        ax1.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax1.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.set_facecolor('#161616')  # Color de fondo del eje

    # Histograma de distribución de montos por gateway_payment
    ax2 = axs[1]
    if not distribucion_gateway.empty:
        bars2 = ax2.bar(distribucion_gateway['payment_gateway'], distribucion_gateway['total_vendido_gateway'], color='green', alpha=0.7, label='Filtrado')
        
        # Superponer datos totales
        if not distribucion_gateway_total.empty:
            bars2_total = ax2.bar(distribucion_gateway_total['payment_gateway'], distribucion_gateway_total['total_vendido_gateway_total'], color='lightgreen', alpha=0.4, label='Total (Sin Filtrar)')

        ax2.set_title('Distribución de Montos de Venta por Gateway Payment', color='white')
        ax2.set_xlabel('Gateway Payment', color='white')
        ax2.set_ylabel('Total Vendido', color='white')
        ax2.set_xticks(distribucion_gateway['payment_gateway'])
        ax2.set_xticklabels(distribucion_gateway['payment_gateway'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax2.bar_label(bars2, label_type='edge', padding=3, color='white')
        if not distribucion_gateway_total.empty:
            ax2.bar_label(bars2_total, label_type='edge', padding=3, color='white')

        # Estadísticas
        promedio_gateway = distribucion_gateway['total_vendido_gateway'].mean()
        std_dev_gateway = distribucion_gateway['total_vendido_gateway'].std()
        maximo_gateway = distribucion_gateway['total_vendido_gateway'].max()
        minimo_gateway = distribucion_gateway['total_vendido_gateway'].min()

        # Texto para la leyenda
        stats_text2 = (
            f'Promedio (Filtrado): {promedio_gateway:.2f}\n'
            f'Desviación Estándar (Filtrado): {std_dev_gateway:.2f}\n'
            f'Máximo (Filtrado): {maximo_gateway:.2f}\n'
            f'Mínimo (Filtrado): {minimo_gateway:.2f}'
        )

        # Leyenda con estadísticas
        ax2.text(0.05, 0.97, stats_text2, ha='left', va='top', fontsize=12, color='white', transform=ax2.transAxes)

    else:
        ax2.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax2.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.set_facecolor('#161616')  # Color de fondo del eje

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)

    image_data = buf.getvalue()
    grafico_montos = base64.b64encode(image_data).decode('utf-8')

    return render(request, 'admin/businessmodel/Sales/tools/histogram-incomes/amount/sales_frequency.html', {
        'venta': venta,
        'grafico_montos': grafico_montos,
        'form': form,
        'fecha_inicio': fecha_inicio,
        'hora_inicio': hora_inicio,
        'fecha_fin': fecha_fin,
        'hora_fin': hora_fin,
        'estadisticas_filtradas': estadisticas_filtradas,
        'estadisticas_totales': estadisticas_totales,
        'distribucion_gateway': distribucion_gateway,  # Agrega esta línea
        'distribucion_gateway_total': distribucion_gateway_total,  
        'porcentaje_promedio':porcentaje_promedio, 
    })



@cache_page(60 * 1)  # Caché por 1 minuto
@staff_member_required
def income_histogram_amount_pdf(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener el formulario y procesar la entrada
    form = FiltroVentasForm(request.GET or None)

    # Obtener los valores de fecha y hora del formulario
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')

    # Obtener datos de ventas usando Django ORM
    ventas = Venta.objects.all().values('id', 'fecha', 'hora', 'monto', 'payment_gateway')

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(list(ventas))
    
    # Verificar si el DataFrame no está vacío
    if df.empty:
        return HttpResponse("No hay datos disponibles", status=204)

    # Convertir la columna 'monto' a float si es decimal
    df['monto'] = df['monto'].astype(float)

    # Crear un datetime combinando fecha y hora
    df['datetime'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

    # Filtrar por rango de fechas y horas
    if fecha_inicio and hora_inicio and fecha_fin and hora_fin:
        fecha_inicio_dt = pd.to_datetime(f"{fecha_inicio} {hora_inicio}")
        fecha_fin_dt = pd.to_datetime(f"{fecha_fin} {hora_fin}")
        df_filtrado = df[(df['datetime'] >= fecha_inicio_dt) & (df['datetime'] <= fecha_fin_dt)]
    else:
        df_filtrado = df

    # Eliminar duplicados y asegurarse de que haya suficientes datos
    df_filtrado = df_filtrado.drop_duplicates(subset=['id', 'monto'])

    # Crear la columna 'fecha' en el DataFrame original
    df['fecha'] = df['datetime'].dt.date

    # Agrupar montos por fecha y calcular la suma de montos vendidos (filtrado)
    frecuencias_montos = df_filtrado.groupby('fecha')['monto'].sum().reset_index(name='total_vendidos')

    # Agrupar montos por fecha y calcular la suma de montos vendidos (sin filtrar)
    frecuencias_montos_total = df.groupby('fecha')['monto'].sum().reset_index(name='total_vendidos')

    # Agrupar montos por gateway_payment
    distribucion_gateway = df_filtrado.groupby('payment_gateway')['monto'].sum().reset_index(name='total_vendido_gateway')

    # Agrupar montos por gateway_payment (sin filtrar)
    distribucion_gateway_total = df.groupby('payment_gateway')['monto'].sum().reset_index(name='total_vendido_gateway_total')

    # Crear figura y ejes (2 filas y 1 columna)
    fig, axs = plt.subplots(2, 1, figsize=(20, 16))
    fig.patch.set_facecolor('#161616')  # Color de fondo de la figura

    # Histograma de total de montos vendidos por fecha (filtrado)
    ax1 = axs[0]
    if not frecuencias_montos.empty:
        bars1 = ax1.bar(frecuencias_montos['fecha'], frecuencias_montos['total_vendidos'], color='blue', alpha=0.7, label='Filtrado')
        
        if not frecuencias_montos_total.empty:
            bars2 = ax1.bar(frecuencias_montos_total['fecha'], frecuencias_montos_total['total_vendidos'], color='cyan', alpha=0.4, label='Total (Sin Filtrar)')

        ax1.set_title('Total de Montos Vendidos por Fecha', color='white')
        ax1.set_xlabel('Fecha', color='white')
        ax1.set_ylabel('Total Vendido', color='white')
        ax1.set_xticks(frecuencias_montos['fecha'])
        ax1.set_xticklabels(frecuencias_montos['fecha'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax1.bar_label(bars1, label_type='edge', padding=3, color='white')
        if not frecuencias_montos_total.empty:
            ax1.bar_label(bars2, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x = np.arange(len(frecuencias_montos))
        z = np.polyfit(x, frecuencias_montos['total_vendidos'], 1)  # Ajuste lineal
        p = np.polyval(z, x)
        ax1.plot(frecuencias_montos['fecha'], p, color='orange', label='Tendencia', linewidth=2)

        # Texto para la leyenda
        stats_text1 = (
            f'Promedio: {frecuencias_montos["total_vendidos"].mean():.2f}\n'
            f'Desviación Estándar: {frecuencias_montos["total_vendidos"].std():.2f}\n'
            f'Mediana: {frecuencias_montos["total_vendidos"].median():.2f}\n'
            f'Máximo: {frecuencias_montos["total_vendidos"].max():.2f}\n'
            f'Mínimo: {frecuencias_montos["total_vendidos"].min():.2f}'
        )
        
        # Leyenda con estadísticas
        ax1.text(0.05, 0.97, stats_text1, ha='left', va='top', fontsize=12, color='white', transform=ax1.transAxes)

        # Agregar la leyenda
        ax1.legend(loc='upper left', fontsize=10)

    else:
        ax1.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax1.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.set_facecolor('#161616')  # Color de fondo del eje

    # Histograma de distribución de montos por gateway_payment
    ax2 = axs[1]
    if not distribucion_gateway.empty:
        bars2 = ax2.bar(distribucion_gateway['payment_gateway'], distribucion_gateway['total_vendido_gateway'], color='green', alpha=0.7, label='Filtrado')
        
        # Superponer datos totales
        if not distribucion_gateway_total.empty:
            bars2_total = ax2.bar(distribucion_gateway_total['payment_gateway'], distribucion_gateway_total['total_vendido_gateway_total'], color='lightgreen', alpha=0.4, label='Total (Sin Filtrar)')

        ax2.set_title('Distribución de Montos de Venta por Gateway Payment', color='white')
        ax2.set_xlabel('Gateway Payment', color='white')
        ax2.set_ylabel('Total Vendido', color='white')
        ax2.set_xticks(distribucion_gateway['payment_gateway'])
        ax2.set_xticklabels(distribucion_gateway['payment_gateway'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax2.bar_label(bars2, label_type='edge', padding=3, color='white')
        if not distribucion_gateway_total.empty:
            ax2.bar_label(bars2_total, label_type='edge', padding=3, color='white')

        # Estadísticas
        promedio_gateway = distribucion_gateway['total_vendido_gateway'].mean()
        std_dev_gateway = distribucion_gateway['total_vendido_gateway'].std()
        maximo_gateway = distribucion_gateway['total_vendido_gateway'].max()
        minimo_gateway = distribucion_gateway['total_vendido_gateway'].min()

        # Texto para la leyenda
        stats_text2 = (
            f'Promedio: {promedio_gateway:.2f}\n'
            f'Desviación Estándar: {std_dev_gateway:.2f}\n'
            f'Máximo: {maximo_gateway:.2f}\n'
            f'Mínimo: {minimo_gateway:.2f}'
        )

        # Leyenda con estadísticas
        ax2.text(0.05, 0.97, stats_text2, ha='left', va='top', fontsize=12, color='white', transform=ax2.transAxes)

    else:
        ax2.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax2.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.set_facecolor('#161616')  # Color de fondo del eje

    plt.tight_layout()

            # Generación del código QR
    usuario = {
        'nombre': 'Juan Pérez',
        'email': 'juan.perez@example.com',
        'telefono': '123456789'
    }
    
    data = f"Nombre: {usuario['nombre']}, Email: {usuario['email']}, Teléfono: {usuario['telefono']}"
    qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=2, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="#f2f2f2")
    buffer_qr = BytesIO()
    img_qr.save(buffer_qr, format='PNG')
    buffer_qr.seek(0)
    qr_img_str = base64.b64encode(buffer_qr.read()).decode()


    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)

    image_data = buf.getvalue()
    grafico_montos = base64.b64encode(image_data).decode('utf-8')

    html = render_to_string('admin/businessmodel/ventas/reportes/income_histogram_pdf.html',
                            {
                                'venta': venta,
                                'grafico_montos': grafico_montos,
                                'qr_img_str': qr_img_str,
                                'form': form,
                                'fecha_inicio': fecha_inicio,
                                'hora_inicio': hora_inicio,
                                'fecha_fin': fecha_fin,
                                'hora_fin': hora_fin,

                            })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=metricas_comprobante_{}.pdf'.format(venta.id)

    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
        stylesheets=[weasyprint.CSS('businessmodel/static/css/comprobante_metricas_venta.css')],
        presentational_hints=True)

    return response





@cache_page(60 * 1)  # Caché por 1 minuto
@staff_member_required
def income_histogram_product(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener el formulario y procesar la entrada
    form = FiltroVentasForm(request.GET or None)

    # Obtener los valores de fecha y hora del formulario
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')

    # Obtener datos de ventas usando Django ORM
    ventas = Venta.objects.all().values('id', 'fecha', 'hora', 'monto')

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(list(ventas))

    # Verificar si el DataFrame no está vacío
    if df.empty:
        return HttpResponse("No hay datos disponibles", status=204)

    # Crear un datetime combinando fecha y hora
    df['datetime'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

    # Filtrar por rango de fechas y horas
    if fecha_inicio and hora_inicio and fecha_fin and hora_fin:
        fecha_inicio_dt = pd.to_datetime(f"{fecha_inicio} {hora_inicio}")
        fecha_fin_dt = pd.to_datetime(f"{fecha_fin} {hora_fin}")
        df_filtrado = df[(df['datetime'] >= fecha_inicio_dt) & (df['datetime'] <= fecha_fin_dt)]
    else:
        df_filtrado = df


    # Eliminar duplicados y asegurarse de que haya suficientes datos
    df_filtrado = df_filtrado.drop_duplicates(subset=['id', 'monto'])

    # Agrupar productos vendidos por fecha
    df_productos = VentaItem.objects.filter(venta__in=df_filtrado['id']).values('product', 'venta__fecha', 'venta__hora', 'venta__monto')
    df_productos = pd.DataFrame(list(df_productos))

    # Calcular la cantidad de productos y montos totales
    if not df_productos.empty:
        df_productos['fecha'] = pd.to_datetime(df_productos['venta__fecha']).dt.date

        # Cantidad de productos vendidos
        cantidad_productos_vendidos = df_productos['product'].nunique()
        
        # Frecuencia de productos vendidos por fecha
        frecuencias_productos = df_productos.groupby('fecha')['product'].count().reset_index(name='cantidad_productos_vendidos')

        # Total de monto vendido por producto
        monto_por_producto = df_productos.groupby(['product', 'fecha']).agg(total_monto_vendido=('venta__monto', 'sum')).reset_index()
        ventas_por_producto = df_productos.groupby(['product', 'fecha']).size().reset_index(name='numero_ventas')
      

        # Datos totales (sin filtrar)
        monto_por_producto_total = df_productos.groupby(['product'])['venta__monto'].sum().reset_index(name='total_monto_vendido_total')
        ventas_totales = df_productos.groupby(['product']).size().reset_index(name='numero_ventas_totales')

    else:
        cantidad_productos_vendidos = 0
        frecuencias_productos = pd.DataFrame(columns=['fecha', 'cantidad_productos_vendidos'])
        monto_por_producto = pd.DataFrame(columns=['product', 'fecha', 'total_monto_vendido'])
        ventas_por_producto = pd.DataFrame(columns=['product', 'fecha', 'numero_ventas'])

        monto_por_producto_total = pd.DataFrame(columns=['product', 'total_monto_vendido_total'])
        ventas_totales = pd.DataFrame(columns=['product', 'numero_ventas_totales'])

    # Crear figura y ejes (3 filas y 1 columna)
    fig, axs = plt.subplots(3, 1, figsize=(20, 24))
    fig.patch.set_facecolor('#161616')  # Color de fondo de la figura

    # Histograma de frecuencia de productos vendidos por fecha
    ax1 = axs[0]
    if not frecuencias_productos.empty:
        bars1 = ax1.bar(frecuencias_productos['fecha'], frecuencias_productos['cantidad_productos_vendidos'], color='green', alpha=0.7, label='Filtrado')
        ax1.set_title('Frecuencia de Productos Vendidos por Fecha', color='white')
        ax1.set_xlabel('Fecha', color='white')
        ax1.set_ylabel('Frecuencia de Productos Vendidos', color='white')
        ax1.set_xticks(frecuencias_productos['fecha'])
        ax1.set_xticklabels(frecuencias_productos['fecha'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax1.bar_label(bars1, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x_products = np.arange(len(frecuencias_productos))
        z_products = np.polyfit(x_products, frecuencias_productos['cantidad_productos_vendidos'].astype(float), 1)
        p_products = np.polyval(z_products, x_products)
        ax1.plot(frecuencias_productos['fecha'], p_products, color='orange', label='Tendencia Filtrada', linewidth=2)

        # Datos totales
        bars_total = ax1.bar(frecuencias_productos['fecha'], df_productos.groupby('fecha')['product'].count(), color='lightgreen', alpha=0.5, label='Total (Sin Filtrar)')
        ax1.bar_label(bars_total, label_type='edge', padding=3, color='black')

        # Estadísticas
        std_dev_productos = frecuencias_productos['cantidad_productos_vendidos'].astype(float).std()
        stats_text1 = (
            f"Total de productos vendidos: {cantidad_productos_vendidos}\n"
            f"Promedio: {frecuencias_productos['cantidad_productos_vendidos'].mean():.2f}\n"
            f"Desviación Estándar: {std_dev_productos:.2f}\n"
            f"Mediana: {frecuencias_productos['cantidad_productos_vendidos'].median():.2f}\n"
            f"Máximo: {frecuencias_productos['cantidad_productos_vendidos'].max():.2f}\n"
            f"Mínimo: {frecuencias_productos['cantidad_productos_vendidos'].min():.2f}"
        )
        ax1.legend(title=stats_text1, fontsize='small')
    else:
        ax1.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax1.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.set_facecolor('#161616')  # Color de fondo del eje

    # Histograma de número de ventas por producto
    ax2 = axs[1]
    if not ventas_por_producto.empty:
        bars2 = ax2.bar(ventas_por_producto['product'], ventas_por_producto['numero_ventas'], color='blue', alpha=0.7, label='Filtrado')
        ax2.set_title('Número de Ventas por Producto', color='white')
        ax2.set_xlabel('Producto', color='white')
        ax2.set_ylabel('Número de Ventas', color='white')
        ax2.set_xticks(ventas_por_producto['product'])
        ax2.set_xticklabels(ventas_por_producto['product'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax2.bar_label(bars2, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x_sales = np.arange(len(ventas_por_producto))
        z_sales = np.polyfit(x_sales, ventas_por_producto['numero_ventas'].astype(float), 1)
        p_sales = np.polyval(z_sales, x_sales)
        ax2.plot(ventas_por_producto['product'], p_sales, color='orange', label='Tendencia Filtrada', linewidth=2)

        # Datos totales
        bars_total = ax2.bar(ventas_totales['product'], ventas_totales['numero_ventas_totales'], color='lightblue', alpha=0.5, label='Total (Sin Filtrar)')
        ax2.bar_label(bars_total, label_type='edge', padding=3, color='black')

        # Estadísticas
        std_dev_ventas = ventas_por_producto['numero_ventas'].astype(float).std()
        stats_text2 = (
            f"Promedio: {ventas_por_producto['numero_ventas'].mean():.2f}\n"
            f"Desviación Estándar: {std_dev_ventas:.2f}\n"
            f"Mediana: {ventas_por_producto['numero_ventas'].median():.2f}\n"
            f"Máximo: {ventas_por_producto['numero_ventas'].max():.2f}\n"
            f"Mínimo: {ventas_por_producto['numero_ventas'].min():.2f}"
        )
        ax2.legend(title=stats_text2, fontsize='small')
    else:
        ax2.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax2.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.set_facecolor('#161616')  # Color de fondo del eje

    # Histograma de monto vendido por nombre de producto
    ax3 = axs[2]
    if not monto_por_producto.empty:
        bars3 = ax3.bar(monto_por_producto['product'], monto_por_producto['total_monto_vendido'], color='purple', alpha=0.7, label='Filtrado')
        ax3.set_title('Monto Vendido por Nombre de Producto', color='white')
        ax3.set_xlabel('Producto', color='white')
        ax3.set_ylabel('Total Monto Vendido', color='white')
        ax3.set_xticks(monto_por_producto['product'])
        ax3.set_xticklabels(monto_por_producto['product'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax3.bar_label(bars3, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x_amount = np.arange(len(monto_por_producto))
        z_amount = np.polyfit(x_amount, monto_por_producto['total_monto_vendido'].astype(float), 1)
        p_amount = np.polyval(z_amount, x_amount)
        ax3.plot(monto_por_producto['product'], p_amount, color='orange', label='Tendencia Filtrada', linewidth=2)

        # Datos totales
        bars_total = ax3.bar(monto_por_producto_total['product'], monto_por_producto_total['total_monto_vendido_total'], color='red', alpha=0.5, label='Total (Sin Filtrar)')
        ax3.bar_label(bars_total, label_type='edge', padding=3, color='black')

        # Estadísticas
        std_dev_monto = monto_por_producto['total_monto_vendido'].astype(float).std()
        stats_text3 = (
            f"Promedio: {monto_por_producto['total_monto_vendido'].mean():.2f}\n"
            f"Desviación Estándar: {std_dev_monto:.2f}\n"
            f"Mediana: {monto_por_producto['total_monto_vendido'].median():.2f}\n"
            f"Máximo: {monto_por_producto['total_monto_vendido'].max():.2f}\n"
            f"Mínimo: {monto_por_producto['total_monto_vendido'].min():.2f}"
        )
        ax3.legend(title=stats_text3, fontsize='small')
    else:
        ax3.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax3.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax3.set_facecolor('#161616')  # Color de fondo del eje

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)

    image_data = buf.getvalue()
    grafico_productos = base64.b64encode(image_data).decode('utf-8')

    return render(request, 'admin/businessmodel/Sales/tools/histogram-incomes/product/sales_frequency.html', {
        'venta': venta,
        'grafico_productos': grafico_productos,
        'form': form,
        'fecha_inicio': fecha_inicio,
        'hora_inicio': hora_inicio,
        'fecha_fin': fecha_fin,
        'hora_fin': hora_fin,
    })


@cache_page(60 * 1)  # Caché por 1 minuto
@staff_member_required
def income_histogram_product_pdf(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener el formulario y procesar la entrada
    form = FiltroVentasForm(request.GET or None)

    # Obtener los valores de fecha y hora del formulario
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')

    # Obtener datos de ventas usando Django ORM
    ventas = Venta.objects.all().values('id', 'fecha', 'hora', 'monto')

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(list(ventas))

    # Verificar si el DataFrame no está vacío
    if df.empty:
        return HttpResponse("No hay datos disponibles", status=204)

    # Crear un datetime combinando fecha y hora
    df['datetime'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

    # Filtrar por rango de fechas y horas
    if fecha_inicio and hora_inicio and fecha_fin and hora_fin:
        fecha_inicio_dt = pd.to_datetime(f"{fecha_inicio} {hora_inicio}")
        fecha_fin_dt = pd.to_datetime(f"{fecha_fin} {hora_fin}")
        df_filtrado = df[(df['datetime'] >= fecha_inicio_dt) & (df['datetime'] <= fecha_fin_dt)]
    else:
        df_filtrado = df

    # Eliminar duplicados y asegurarse de que haya suficientes datos
    df_filtrado = df_filtrado.drop_duplicates(subset=['id', 'monto'])

    # Agrupar productos vendidos por fecha
    df_productos = VentaItem.objects.filter(venta__in=df_filtrado['id']).values('product', 'venta__fecha', 'venta__hora', 'venta__monto')
    df_productos = pd.DataFrame(list(df_productos))

    # Calcular la cantidad de productos y montos totales
    if not df_productos.empty:
        df_productos['fecha'] = pd.to_datetime(df_productos['venta__fecha']).dt.date

        # Cantidad de productos vendidos
        cantidad_productos_vendidos = df_productos['product'].nunique()
        
        # Frecuencia de productos vendidos por fecha
        frecuencias_productos = df_productos.groupby('fecha')['product'].count().reset_index(name='cantidad_productos_vendidos')

        # Total de monto vendido por producto
        monto_por_producto = df_productos.groupby(['product', 'fecha']).agg(total_monto_vendido=('venta__monto', 'sum')).reset_index()
        ventas_por_producto = df_productos.groupby(['product', 'fecha']).size().reset_index(name='numero_ventas')

    else:
        cantidad_productos_vendidos = 0
        frecuencias_productos = pd.DataFrame(columns=['fecha', 'cantidad_productos_vendidos'])
        monto_por_producto = pd.DataFrame(columns=['product', 'fecha', 'total_monto_vendido'])
        ventas_por_producto = pd.DataFrame(columns=['product', 'fecha', 'numero_ventas'])

    # Crear figura y ejes (3 filas y 1 columna)
    fig, axs = plt.subplots(3, 1, figsize=(20, 24))
    fig.patch.set_facecolor('#161616')  # Color de fondo de la figura

    # Histograma de frecuencia de productos vendidos por fecha
    ax1 = axs[0]
    if not frecuencias_productos.empty:
        bars1 = ax1.bar(frecuencias_productos['fecha'], frecuencias_productos['cantidad_productos_vendidos'], color='green', alpha=0.7)
        ax1.set_title('Frecuencia de Productos Vendidos por Fecha', color='white')
        ax1.set_xlabel('Fecha', color='white')
        ax1.set_ylabel('Frecuencia de Productos Vendidos', color='white')
        ax1.set_xticks(frecuencias_productos['fecha'])
        ax1.set_xticklabels(frecuencias_productos['fecha'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax1.bar_label(bars1, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x_products = np.arange(len(frecuencias_productos))
        z_products = np.polyfit(x_products, frecuencias_productos['cantidad_productos_vendidos'].astype(float), 1)
        p_products = np.polyval(z_products, x_products)
        ax1.plot(frecuencias_productos['fecha'], p_products, color='orange', label='Tendencia', linewidth=2)

        # Estadísticas
        std_dev_productos = frecuencias_productos['cantidad_productos_vendidos'].astype(float).std()
        stats_text1 = (
            f"Total de productos vendidos: {cantidad_productos_vendidos}\n"
            f"Promedio: {frecuencias_productos['cantidad_productos_vendidos'].mean():.2f}\n"
            f"Desviación Estándar: {std_dev_productos:.2f}\n"
            f"Mediana: {frecuencias_productos['cantidad_productos_vendidos'].median():.2f}\n"
            f"Máximo: {frecuencias_productos['cantidad_productos_vendidos'].max():.2f}\n"
            f"Mínimo: {frecuencias_productos['cantidad_productos_vendidos'].min():.2f}"
        )
        ax1.legend(title=stats_text1, fontsize='small')

        

    else:
        ax1.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax1.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.set_facecolor('#161616')  # Color de fondo del eje

    # Histograma de número de ventas por producto
    ax2 = axs[1]
    if not ventas_por_producto.empty:
        bars2 = ax2.bar(ventas_por_producto['product'], ventas_por_producto['numero_ventas'], color='blue', alpha=0.7)
        ax2.set_title('Número de Ventas por Producto', color='white')
        ax2.set_xlabel('Producto', color='white')
        ax2.set_ylabel('Número de Ventas', color='white')
        ax2.set_xticks(ventas_por_producto['product'])
        ax2.set_xticklabels(ventas_por_producto['product'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax2.bar_label(bars2, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x_sales = np.arange(len(ventas_por_producto))
        z_sales = np.polyfit(x_sales, ventas_por_producto['numero_ventas'].astype(float), 1)
        p_sales = np.polyval(z_sales, x_sales)
        ax2.plot(ventas_por_producto['product'], p_sales, color='orange', label='Tendencia', linewidth=2)

        # Estadísticas
        std_dev_ventas = ventas_por_producto['numero_ventas'].astype(float).std()
        stats_text2 = (
            f"Promedio: {ventas_por_producto['numero_ventas'].mean():.2f}\n"
            f"Desviación Estándar: {std_dev_ventas:.2f}\n"
            f"Mediana: {ventas_por_producto['numero_ventas'].median():.2f}\n"
            f"Máximo: {ventas_por_producto['numero_ventas'].max():.2f}\n"
            f"Mínimo: {ventas_por_producto['numero_ventas'].min():.2f}"
        )
        ax2.legend(title=stats_text2, fontsize='small')

    else:
        ax2.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax2.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.set_facecolor('#161616')  # Color de fondo del eje

    # Histograma de monto vendido por nombre de producto
    ax3 = axs[2]
    if not monto_por_producto.empty:
        bars3 = ax3.bar(monto_por_producto['product'], monto_por_producto['total_monto_vendido'], color='purple', alpha=0.7)
        ax3.set_title('Monto Vendido por Nombre de Producto', color='white')
        ax3.set_xlabel('Producto', color='white')
        ax3.set_ylabel('Total Monto Vendido', color='white')
        ax3.set_xticks(monto_por_producto['product'])
        ax3.set_xticklabels(monto_por_producto['product'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax3.bar_label(bars3, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x_amount = np.arange(len(monto_por_producto))
        z_amount = np.polyfit(x_amount, monto_por_producto['total_monto_vendido'].astype(float), 1)
        p_amount = np.polyval(z_amount, x_amount)
        ax3.plot(monto_por_producto['product'], p_amount, color='orange', label='Tendencia', linewidth=2)

        # Estadísticas
        std_dev_monto = monto_por_producto['total_monto_vendido'].astype(float).std()
        stats_text3 = (
            f"Promedio: {monto_por_producto['total_monto_vendido'].mean():.2f}\n"
            f"Desviación Estándar: {std_dev_monto:.2f}\n"
            f"Mediana: {monto_por_producto['total_monto_vendido'].median():.2f}\n"
            f"Máximo: {monto_por_producto['total_monto_vendido'].max():.2f}\n"
            f"Mínimo: {monto_por_producto['total_monto_vendido'].min():.2f}"
        )
        ax3.legend(title=stats_text3, fontsize='small')

    else:
        ax3.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax3.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax3.set_facecolor('#161616')  # Color de fondo del eje

    plt.tight_layout()

    usuario = {
        'nombre': 'Juan Pérez',
        'email': 'juan.perez@example.com',
        'telefono': '123456789'
    }

    data = f"Nombre: {usuario['nombre']}, Email: {usuario['email']}, Teléfono: {usuario['telefono']}"
    qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=2, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="#f2f2f2")
    buffer_qr = BytesIO()
    img_qr.save(buffer_qr, format='PNG')
    buffer_qr.seek(0)

    qr_img_str = base64.b64encode(buffer_qr.read()).decode()

    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)

    image_data = buf.getvalue()
    grafico_productos = base64.b64encode(image_data).decode('utf-8')

    html = render_to_string('admin/businessmodel/ventas/reportes/income_histogram_product_pdf.html',
                            {
                                'venta': venta,
                                'grafico_productos': grafico_productos,
                                'qr_img_str': qr_img_str,
                                'form': form,
                                'fecha_inicio': fecha_inicio,
                                'hora_inicio': hora_inicio,
                                'fecha_fin': fecha_fin,
                                'hora_fin': hora_fin,
                                'cantidad_productos_vendidos': cantidad_productos_vendidos,
                                'monto_por_producto':monto_por_producto ,

                            })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=metricas_comprobante_{}.pdf'.format(venta.id)

    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
        stylesheets=[weasyprint.CSS('businessmodel/static/css/comprobante_metricas_venta.css')],
        presentational_hints=True)

    return response

@cache_page(60 * 1)  # Caché por 1 minuto
@staff_member_required
def income_histogram_category(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener el formulario y procesar la entrada
    form = FiltroVentasForm(request.GET or None)

    # Obtener los valores de fecha y hora del formulario
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')

    # Obtener datos de ventas usando Django ORM
    ventas = Venta.objects.all().values('id', 'fecha', 'hora', 'monto')

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(list(ventas))

    # Verificar si el DataFrame no está vacío
    if df.empty:
        return HttpResponse("No hay datos disponibles", status=204)

    # Crear un datetime combinando fecha y hora
    df['datetime'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

    # Filtrar por rango de fechas y horas
    if fecha_inicio and hora_inicio and fecha_fin and hora_fin:
        fecha_inicio_dt = pd.to_datetime(f"{fecha_inicio} {hora_inicio}")
        fecha_fin_dt = pd.to_datetime(f"{fecha_fin} {hora_fin}")
        df_filtrado = df[(df['datetime'] >= fecha_inicio_dt) & (df['datetime'] <= fecha_fin_dt)]
    else:
        df_filtrado = df

    # Eliminar duplicados y asegurarse de que haya suficientes datos
    df_filtrado = df_filtrado.drop_duplicates(subset=['id', 'monto'])

    # Agrupar categorías vendidas por fecha
    df_categorias = VentaItem.objects.filter(venta__in=df_filtrado['id']).values('product__category', 'venta__fecha', 'venta__hora', 'venta__monto')
    df_categorias = pd.DataFrame(list(df_categorias))

    if not df_categorias.empty:
        df_categorias['fecha'] = pd.to_datetime(df_categorias['venta__fecha']).dt.date

        # Total de monto vendido por categoría (filtrado)
        monto_por_categoria = df_categorias.groupby(['product__category']).agg(total_monto_vendido=('venta__monto', 'sum')).reset_index()
        
        # Total de monto vendido por categoría (sin filtrar)
        df_categorias_total = VentaItem.objects.filter(venta__in=df['id']).values('product__category', 'venta__monto')
        df_categorias_total = pd.DataFrame(list(df_categorias_total))
        monto_por_categoria_total = df_categorias_total.groupby(['product__category']).agg(total_monto_vendido=('venta__monto', 'sum')).reset_index()

        # Número de ventas por categoría (filtrado)
        ventas_por_categoria = df_categorias.groupby(['product__category']).size().reset_index(name='numero_ventas')

        # Número de ventas por categoría (sin filtrar)
        ventas_por_categoria_total = df_categorias_total.groupby(['product__category']).size().reset_index(name='numero_ventas')

        # Frecuencia de categorías vendidas
        frecuencias_categorias = df_categorias.groupby('fecha')['product__category'].value_counts().reset_index(name='cantidad_categorias_vendidas')

    else:
        frecuencias_categorias = pd.DataFrame(columns=['fecha', 'cantidad_categorias_vendidas'])
        monto_por_categoria = pd.DataFrame(columns=['product__category', 'total_monto_vendido'])
        ventas_por_categoria = pd.DataFrame(columns=['product__category', 'numero_ventas'])
        ventas_por_categoria_total = pd.DataFrame(columns=['product__category', 'numero_ventas'])

    # Crear figura y ejes
    fig, axs = plt.subplots(3, 1, figsize=(20, 24))
    fig.patch.set_facecolor('#161616')  # Color de fondo de la figura

    # Colores para las barras
    colores_categorias = plt.cm.viridis(np.linspace(0, 1, len(monto_por_categoria['product__category'].unique())))

    # Histograma de monto vendido por categoría
    ax1 = axs[0]
    if not monto_por_categoria.empty:
        bars1 = ax1.bar(monto_por_categoria['product__category'], monto_por_categoria['total_monto_vendido'],
                         color=colores_categorias[:len(monto_por_categoria)], alpha=0.7, label='Filtrado')
        
        if not monto_por_categoria_total.empty:
            bars2 = ax1.bar(monto_por_categoria_total['product__category'], monto_por_categoria_total['total_monto_vendido'],
                             color='cyan', alpha=0.4, label='Total (Sin Filtrar)')

        ax1.set_title('Monto Vendido por Categoría', color='white')
        ax1.set_xlabel('Categoría', color='white')
        ax1.set_ylabel('Total Monto Vendido', color='white')
        ax1.set_xticks(monto_por_categoria['product__category'])
        ax1.set_xticklabels(monto_por_categoria['product__category'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax1.bar_label(bars1, label_type='edge', padding=3, color='white')
        if not monto_por_categoria_total.empty:
            ax1.bar_label(bars2, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x_amount = np.arange(len(monto_por_categoria))
        z_amount = np.polyfit(x_amount, monto_por_categoria['total_monto_vendido'].astype(float), 1)
        p_amount = np.polyval(z_amount, x_amount)
        ax1.plot(monto_por_categoria['product__category'], p_amount, color='orange', label='Tendencia', linewidth=2)

        # Estadísticas
        total_monto_vendido_float = monto_por_categoria['total_monto_vendido'].astype(float)
        mean_monto = total_monto_vendido_float.mean()
        std_dev_monto = total_monto_vendido_float.std()
        median_monto = total_monto_vendido_float.median()
        max_monto = total_monto_vendido_float.max()
        min_monto = total_monto_vendido_float.min()

        ax1.legend([f'Tendencia: {mean_monto:.2f} (Media), {std_dev_monto:.2f} (Desv. Est.), {median_monto:.2f} (Mediana), {max_monto:.2f} (Máx.), {min_monto:.2f} (Mín.)'])

    else:
        ax1.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax1.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.set_facecolor('#161616')  # Color de fondo del eje

    # Histograma de número de ventas por categoría
    ax2 = axs[1]
    if not ventas_por_categoria.empty:
        bars2 = ax2.bar(ventas_por_categoria['product__category'], ventas_por_categoria['numero_ventas'],
                         color=colores_categorias[:len(ventas_por_categoria['numero_ventas'])], alpha=0.7, label='Filtrado')
        
        # Superponer los datos totales
        if not ventas_por_categoria_total.empty:
            bars2_total = ax2.bar(ventas_por_categoria_total['product__category'], ventas_por_categoria_total['numero_ventas'],
                                   color='cyan', alpha=0.4, label='Total (Sin Filtrar)')

        ax2.set_title('Número de Ventas por Categoría', color='white')
        ax2.set_xlabel('Categoría', color='white')
        ax2.set_ylabel('Número de Ventas', color='white')
        ax2.set_xticks(ventas_por_categoria['product__category'])
        ax2.set_xticklabels(ventas_por_categoria['product__category'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax2.bar_label(bars2, label_type='edge', padding=3, color='white')
        if not ventas_por_categoria_total.empty:
            ax2.bar_label(bars2_total, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x_sales = np.arange(len(ventas_por_categoria))
        z_sales = np.polyfit(x_sales, ventas_por_categoria['numero_ventas'].astype(float), 1)
        p_sales = np.polyval(z_sales, x_sales)
        ax2.plot(ventas_por_categoria['product__category'], p_sales, color='orange', label='Tendencia', linewidth=2)

        # Estadísticas
        mean_sales = ventas_por_categoria['numero_ventas'].mean()
        std_dev_ventas = ventas_por_categoria['numero_ventas'].astype(float).std()
        median_sales = ventas_por_categoria['numero_ventas'].median()
        max_sales = ventas_por_categoria['numero_ventas'].max()
        min_sales = ventas_por_categoria['numero_ventas'].min()

        ax2.legend([f'Tendencia: {mean_sales:.2f} (Media), {std_dev_ventas:.2f} (Desv. Est.), {median_sales:.2f} (Mediana), {max_sales} (Máx.), {min_sales} (Mín.)'])

    else:
        ax2.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax2.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.set_facecolor('#161616')  # Color de fondo del eje

    # Histograma de frecuencia de categorías vendidas
    ax3 = axs[2]
    if not frecuencias_categorias.empty:
        bars3 = ax3.bar(frecuencias_categorias['product__category'], frecuencias_categorias['cantidad_categorias_vendidas'],
                         color=colores_categorias[:len(frecuencias_categorias)], alpha=0.7)
        ax3.set_title('Frecuencia de Categorías Vendidas', color='white')
        ax3.set_xlabel('Categoría', color='white')
        ax3.set_ylabel('Frecuencia', color='white')
        ax3.set_xticks(frecuencias_categorias['product__category'])
        ax3.set_xticklabels(frecuencias_categorias['product__category'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax3.bar_label(bars3, label_type='edge', padding=3, color='white')

        # Estadísticas
        mean_freq = frecuencias_categorias['cantidad_categorias_vendidas'].mean()
        std_dev_freq = frecuencias_categorias['cantidad_categorias_vendidas'].std()
        median_freq = frecuencias_categorias['cantidad_categorias_vendidas'].median()
        max_freq = frecuencias_categorias['cantidad_categorias_vendidas'].max()
        min_freq = frecuencias_categorias['cantidad_categorias_vendidas'].min()

        ax3.legend([f'Tendencia: {mean_freq:.2f} (Media), {std_dev_freq:.2f} (Desv. Est.), {median_freq:.2f} (Mediana), {max_freq} (Máx.), {min_freq} (Mín.)'])

    else:
        ax3.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax3.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax3.set_facecolor('#161616')  # Color de fondo del eje

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)

    image_data = buf.getvalue()
    grafico_categorias = base64.b64encode(image_data).decode('utf-8')

    return render(request, 'admin/businessmodel/Sales/tools/histogram-incomes/category/sales_frequency.html', {
        'venta': venta,
        'grafico_categorias': grafico_categorias,
        'form': form,
        'fecha_inicio': fecha_inicio,
        'hora_inicio': hora_inicio,
        'fecha_fin': fecha_fin,
        'hora_fin': hora_fin,
    })



@cache_page(60 * 1)  # Caché por 1 minuto
@staff_member_required
def income_histogram_category_pdf(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener el formulario y procesar la entrada
    form = FiltroVentasForm(request.GET or None)

    # Obtener los valores de fecha y hora del formulario
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')

    # Obtener datos de ventas usando Django ORM
    ventas = Venta.objects.all().values('id', 'fecha', 'hora', 'monto')

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(list(ventas))

    # Verificar si el DataFrame no está vacío
    if df.empty:
        return HttpResponse("No hay datos disponibles", status=204)

    # Crear un datetime combinando fecha y hora
    df['datetime'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

    # Filtrar por rango de fechas y horas
    if fecha_inicio and hora_inicio and fecha_fin and hora_fin:
        fecha_inicio_dt = pd.to_datetime(f"{fecha_inicio} {hora_inicio}")
        fecha_fin_dt = pd.to_datetime(f"{fecha_fin} {hora_fin}")
        df_filtrado = df[(df['datetime'] >= fecha_inicio_dt) & (df['datetime'] <= fecha_fin_dt)]
    else:
        df_filtrado = df

    # Eliminar duplicados y asegurarse de que haya suficientes datos
    df_filtrado = df_filtrado.drop_duplicates(subset=['id', 'monto'])

    # Agrupar productos vendidos por fecha
    df_productos = VentaItem.objects.filter(venta__in=df_filtrado['id']).values('product', 'venta__fecha', 'venta__hora', 'venta__monto')
    df_productos = pd.DataFrame(list(df_productos))

    # Calcular la cantidad de productos y montos totales
    if not df_productos.empty:
        df_productos['fecha'] = pd.to_datetime(df_productos['venta__fecha']).dt.date

        # Cantidad de productos vendidos
        cantidad_productos_vendidos = df_productos['product'].nunique()
        
        # Frecuencia de productos vendidos por fecha
        frecuencias_productos = df_productos.groupby('fecha')['product'].count().reset_index(name='cantidad_productos_vendidos')

        # Total de monto vendido por producto
        monto_por_producto = df_productos.groupby(['product', 'fecha']).agg(total_monto_vendido=('venta__monto', 'sum')).reset_index()
        ventas_por_producto = df_productos.groupby(['product', 'fecha']).size().reset_index(name='numero_ventas')

    else:
        cantidad_productos_vendidos = 0
        frecuencias_productos = pd.DataFrame(columns=['fecha', 'cantidad_productos_vendidos'])
        monto_por_producto = pd.DataFrame(columns=['product', 'fecha', 'total_monto_vendido'])
        ventas_por_producto = pd.DataFrame(columns=['product', 'fecha', 'numero_ventas'])

    # Crear figura y ejes (3 filas y 1 columna)
    fig, axs = plt.subplots(3, 1, figsize=(20, 24))
    fig.patch.set_facecolor('#161616')  # Color de fondo de la figura

    # Histograma de frecuencia de productos vendidos por fecha
    ax1 = axs[0]
    if not frecuencias_productos.empty:
        bars1 = ax1.bar(frecuencias_productos['fecha'], frecuencias_productos['cantidad_productos_vendidos'], color='green', alpha=0.7)
        ax1.set_title('Frecuencia de Productos Vendidos por Fecha', color='white')
        ax1.set_xlabel('Fecha', color='white')
        ax1.set_ylabel('Frecuencia de Productos Vendidos', color='white')
        ax1.set_xticks(frecuencias_productos['fecha'])
        ax1.set_xticklabels(frecuencias_productos['fecha'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax1.bar_label(bars1, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x_products = np.arange(len(frecuencias_productos))
        z_products = np.polyfit(x_products, frecuencias_productos['cantidad_productos_vendidos'].astype(float), 1)
        p_products = np.polyval(z_products, x_products)
        ax1.plot(frecuencias_productos['fecha'], p_products, color='orange', label='Tendencia', linewidth=2)

        # Estadísticas
        std_dev_productos = frecuencias_productos['cantidad_productos_vendidos'].astype(float).std()
        stats_text1 = (
            f"Total de productos vendidos: {cantidad_productos_vendidos}\n"
            f"Promedio: {frecuencias_productos['cantidad_productos_vendidos'].mean():.2f}\n"
            f"Desviación Estándar: {std_dev_productos:.2f}\n"
            f"Mediana: {frecuencias_productos['cantidad_productos_vendidos'].median():.2f}\n"
            f"Máximo: {frecuencias_productos['cantidad_productos_vendidos'].max():.2f}\n"
            f"Mínimo: {frecuencias_productos['cantidad_productos_vendidos'].min():.2f}"
        )
        ax1.legend(title=stats_text1, fontsize='small')

        

    else:
        ax1.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax1.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.set_facecolor('#161616')  # Color de fondo del eje

    # Histograma de número de ventas por producto
    ax2 = axs[1]
    if not ventas_por_producto.empty:
        bars2 = ax2.bar(ventas_por_producto['product'], ventas_por_producto['numero_ventas'], color='blue', alpha=0.7)
        ax2.set_title('Número de Ventas por Producto', color='white')
        ax2.set_xlabel('Producto', color='white')
        ax2.set_ylabel('Número de Ventas', color='white')
        ax2.set_xticks(ventas_por_producto['product'])
        ax2.set_xticklabels(ventas_por_producto['product'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax2.bar_label(bars2, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x_sales = np.arange(len(ventas_por_producto))
        z_sales = np.polyfit(x_sales, ventas_por_producto['numero_ventas'].astype(float), 1)
        p_sales = np.polyval(z_sales, x_sales)
        ax2.plot(ventas_por_producto['product'], p_sales, color='orange', label='Tendencia', linewidth=2)

        # Estadísticas
        std_dev_ventas = ventas_por_producto['numero_ventas'].astype(float).std()
        stats_text2 = (
            f"Promedio: {ventas_por_producto['numero_ventas'].mean():.2f}\n"
            f"Desviación Estándar: {std_dev_ventas:.2f}\n"
            f"Mediana: {ventas_por_producto['numero_ventas'].median():.2f}\n"
            f"Máximo: {ventas_por_producto['numero_ventas'].max():.2f}\n"
            f"Mínimo: {ventas_por_producto['numero_ventas'].min():.2f}"
        )
        ax2.legend(title=stats_text2, fontsize='small')

    else:
        ax2.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax2.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.set_facecolor('#161616')  # Color de fondo del eje

    # Histograma de monto vendido por nombre de producto
    ax3 = axs[2]
    if not monto_por_producto.empty:
        bars3 = ax3.bar(monto_por_producto['product'], monto_por_producto['total_monto_vendido'], color='purple', alpha=0.7)
        ax3.set_title('Monto Vendido por Nombre de Producto', color='white')
        ax3.set_xlabel('Producto', color='white')
        ax3.set_ylabel('Total Monto Vendido', color='white')
        ax3.set_xticks(monto_por_producto['product'])
        ax3.set_xticklabels(monto_por_producto['product'], rotation=45, ha='right', color='white', fontsize=8)

        # Agregar etiquetas de los valores sobre las barras
        ax3.bar_label(bars3, label_type='edge', padding=3, color='white')

        # Ajustar curva de tendencia
        x_amount = np.arange(len(monto_por_producto))
        z_amount = np.polyfit(x_amount, monto_por_producto['total_monto_vendido'].astype(float), 1)
        p_amount = np.polyval(z_amount, x_amount)
        ax3.plot(monto_por_producto['product'], p_amount, color='orange', label='Tendencia', linewidth=2)

        # Estadísticas
        std_dev_monto = monto_por_producto['total_monto_vendido'].astype(float).std()
        stats_text3 = (
            f"Promedio: {monto_por_producto['total_monto_vendido'].mean():.2f}\n"
            f"Desviación Estándar: {std_dev_monto:.2f}\n"
            f"Mediana: {monto_por_producto['total_monto_vendido'].median():.2f}\n"
            f"Máximo: {monto_por_producto['total_monto_vendido'].max():.2f}\n"
            f"Mínimo: {monto_por_producto['total_monto_vendido'].min():.2f}"
        )
        ax3.legend(title=stats_text3, fontsize='small')

    else:
        ax3.set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    ax3.grid(color='white', linestyle='--', linewidth=0.5, alpha=0.5)
    ax3.set_facecolor('#161616')  # Color de fondo del eje

    plt.tight_layout()

    usuario = {
        'nombre': 'Juan Pérez',
        'email': 'juan.perez@example.com',
        'telefono': '123456789'
    }

    data = f"Nombre: {usuario['nombre']}, Email: {usuario['email']}, Teléfono: {usuario['telefono']}"
    qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=2, border=4)
    qr.add_data(data)
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="#f2f2f2")
    buffer_qr = BytesIO()
    img_qr.save(buffer_qr, format='PNG')
    buffer_qr.seek(0)

    qr_img_str = base64.b64encode(buffer_qr.read()).decode()

    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)

    image_data = buf.getvalue()
    grafico_productos = base64.b64encode(image_data).decode('utf-8')

    html = render_to_string('admin/businessmodel/ventas/reportes/income_histogram_category_pdf.html',
                            {
                                'venta': venta,
                                'grafico_productos': grafico_productos,
                                'qr_img_str': qr_img_str,
                                'form': form,
                                'fecha_inicio': fecha_inicio,
                                'hora_inicio': hora_inicio,
                                'fecha_fin': fecha_fin,
                                'hora_fin': hora_fin,

                            })
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=metricas_comprobante_{}.pdf'.format(venta.id)

    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
        stylesheets=[weasyprint.CSS('businessmodel/static/css/comprobante_metricas_venta.css')],
        presentational_hints=True)

    return response


@staff_member_required
def pie_incomes_time(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener el formulario y procesar la entrada
    form = FiltroVentasForm(request.GET or None)

    # Obtener los valores de fecha y hora del formulario
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')

    # Obtener datos de ventas usando Django ORM
    ventas = Venta.objects.all().values('id', 'fecha', 'hora', 'monto')

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(list(ventas))

    # Verificar si el DataFrame no está vacío
    if df.empty:
        return HttpResponse("No hay datos disponibles", status=204)

    # Crear un datetime combinando fecha y hora
    df['datetime'] = pd.to_datetime(df['fecha'].astype(str) + ' ' + df['hora'].astype(str))

    # Filtrar por rango de fechas y horas
    if fecha_inicio and hora_inicio and fecha_fin and hora_fin:
        fecha_inicio_dt = pd.to_datetime(f"{fecha_inicio} {hora_inicio}")
        fecha_fin_dt = pd.to_datetime(f"{fecha_fin} {hora_fin}")
        
        df_filtrado = df[(df['datetime'] >= fecha_inicio_dt) & (df['datetime'] <= fecha_fin_dt)]
    else:
        df_filtrado = df

    # Eliminar duplicados
    df_filtrado = df_filtrado.drop_duplicates(subset=['id', 'monto'])

    # Agrupar montos por fecha y contar las ventas
    df_filtrado['fecha'] = df_filtrado['datetime'].dt.date
    frecuencias_tiempo = df_filtrado.groupby('fecha')['monto'].count().reset_index(name='frecuencia')
    frecuencias_montos = df_filtrado.groupby('fecha')['monto'].sum().reset_index(name='total_monto')

    # Crear figura y ejes en 1 fila y 2 columnas
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    fig.patch.set_facecolor('#161616')  # Color de fondo de la figura

    # Gráfico 1: Distribución de ventas por fecha
    if not frecuencias_tiempo.empty:
        axs[0].pie(frecuencias_tiempo['frecuencia'], labels=frecuencias_tiempo['fecha'], autopct='%1.1f%%', startangle=90, colors=plt.cm.tab10.colors)
        axs[0].axis('equal')  # Igualar el aspecto del gráfico
        axs[0].set_title('Distribución de Ventas por Fecha', color='white')
    else:
        axs[0].set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    # Gráfico 2: Distribución de montos por fecha
    if not frecuencias_montos.empty:
        axs[1].pie(frecuencias_montos['total_monto'], labels=frecuencias_montos['fecha'], autopct='%1.1f%%', startangle=90, colors=plt.cm.tab10.colors)
        axs[1].axis('equal')  # Igualar el aspecto del gráfico
        axs[1].set_title('Distribución de Montos por Fecha', color='white')
    else:
        axs[1].set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    for ax in axs.flat:
        for label in ax.texts:
            label.set_color('white')

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)

    image_data = buf.getvalue()
    grafico_montos = base64.b64encode(image_data).decode('utf-8')

    return render(request, 'admin/businessmodel/Sales/tools/pie-incomes/sales_pie.html', {
        'venta': venta,
        'grafico_montos': grafico_montos,
        'form': form,
        'fecha_inicio': fecha_inicio,
        'hora_inicio': hora_inicio,
        'fecha_fin': fecha_fin,
        'hora_fin': hora_fin,
    })



@staff_member_required
def pie_incomes_product(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)

    # Obtener el formulario y procesar la entrada
    form = FiltroVentasForm(request.GET or None)

    # Obtener los valores de fecha y hora del formulario
    fecha_inicio = request.GET.get('fecha_inicio')
    hora_inicio = request.GET.get('hora_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    hora_fin = request.GET.get('hora_fin')

    # Obtener datos de ventas usando Django ORM
    ventas = Venta.objects.all().values('id', 'fecha', 'hora', 'monto')
    productos = VentaItem.objects.values('product','quantity')  # Asegúrate de que 'product' sea el campo correcto

    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(list(ventas))

    # Verificar si el DataFrame no está vacío
    if df.empty:
        return HttpResponse("No hay datos disponibles", status=204)

    # Filtrar por rango de fechas y horas
    if fecha_inicio and hora_inicio and fecha_fin and hora_fin:
        fecha_inicio_dt = pd.to_datetime(f"{fecha_inicio} {hora_inicio}")
        fecha_fin_dt = pd.to_datetime(f"{fecha_fin} {hora_fin}")
        df_filtrado = df[(df['datetime'] >= fecha_inicio_dt) & (df['datetime'] <= fecha_fin_dt)]
    else:
        df_filtrado = df

    # Eliminar duplicados
    df_filtrado = df_filtrado.drop_duplicates(subset=['id', 'monto'])

    # Distribución de productos vendidos
    if productos.exists():
        df_productos = pd.DataFrame(list(productos))
        frecuencias_productos = df_productos['product'].value_counts().reset_index(name='quantity')
        frecuencias_productos.columns = ['product', 'quantity']
    else:
        frecuencias_productos = pd.DataFrame(columns=['product', 'quantity'])

    # Calcular la distribución de productos por monto
    # Suponiendo que hay una relación entre las ventas y los productos
    df_productos_ventas = VentaItem.objects.filter(venta__in=df_filtrado['id']).values('product', 'price')
    df_productos_montos = pd.DataFrame(list(df_productos_ventas))

    if not df_productos_montos.empty:
        frecuencias_montos = df_productos_montos.groupby('product')['price'].sum().reset_index()
    else:
        frecuencias_montos = pd.DataFrame(columns=['product', 'price'])

    # Crear figura y ejes en 1 fila y 2 columnas
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    fig.patch.set_facecolor('#161616')  # Color de fondo de la figura

    # Gráfico 1: Distribución de productos vendidos
    if not frecuencias_productos.empty:
        axs[0].pie(frecuencias_productos['quantity'], labels=frecuencias_productos['product'], autopct='%1.1f%%', startangle=90, colors=plt.cm.tab10.colors)
        axs[0].axis('equal')  # Igualar el aspecto del gráfico
        axs[0].set_title('Distribución de Productos Vendidos', color='white')
    else:
        axs[0].set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    # Gráfico 2: Distribución de productos por monto
    if not frecuencias_montos.empty:
        axs[1].pie(frecuencias_montos['price'], labels=frecuencias_montos['product'], autopct='%1.1f%%', startangle=90, colors=plt.cm.tab10.colors)
        axs[1].axis('equal')  # Igualar el aspecto del gráfico
        axs[1].set_title('Distribución de Productos por Monto', color='white')
    else:
        axs[1].set_title('No hay suficientes datos para mostrar el gráfico.', color='white')

    for ax in axs.flat:
        for label in ax.texts:
            label.set_color('white')

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)

    image_data = buf.getvalue()
    grafico_montos = base64.b64encode(image_data).decode('utf-8')

    return render(request, 'admin/businessmodel/Sales/tools/pie-incomes/sales_pie.html', {
        'venta': venta,
        'grafico_montos': grafico_montos,
        'form': form,
        'fecha_inicio': fecha_inicio,
        'hora_inicio': hora_inicio,
        'fecha_fin': fecha_fin,
        'hora_fin': hora_fin,
    })



@staff_member_required
def financieros_venta(request, venta_id):
    # Obtener la información de ventas filtrada por el ID proporcionado
    venta = get_object_or_404(Venta, id=venta_id)

    # Convertir a diccionario para que sea más fácil de manipular en la plantilla
    venta_info = {
        'fecha': venta.fecha,
        'monto': venta.monto,
        'cantidad': venta.cantidad,
        'producto': venta.producto,
        'costo_unitario': venta.costo_unitario,
        'descuentos': venta.descuentos,
        'devoluciones': venta.devoluciones
    }

    return render(request,
                  'admin/businessmodel/ventas/tools/financieros.html',
                  {
                      'venta_info': venta_info,
                  })

@staff_member_required
def estadisticas_venta(request, venta_id):
    # Obtener la información de ventas filtrada por el ID proporcionado
    venta = get_object_or_404(Venta, id=venta_id)

    # Convertir a diccionario para que sea más fácil de manipular en la plantilla
    venta_info = {
        'fecha': venta.fecha,
        'monto': venta.monto,
        'cantidad': venta.cantidad,
        'producto': venta.producto,
        'costo_unitario': venta.costo_unitario,
        'descuentos': venta.descuentos,
        'devoluciones': venta.devoluciones
    }

    return render(request,
                  'admin/businessmodel/ventas/tools/estadisticas.html',
                  {
                      'venta_info': venta_info,
                  })







def ventas_grafico(request):
    form = FiltroVentasForm(request.GET or None)
    
    # Validar formulario
    if not form.is_valid():
        return HttpResponse("Formulario inválido", status=400)
    
    periodo = request.GET.get('periodo', 'M').upper()
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    producto_id = request.GET.get('productos')
    
    # Validar el período
    if periodo not in ['H', 'D', 'M', 'Y']:
        return HttpResponse("Período inválido. Use 'H' para horas, 'D' para días, 'M' para meses, o 'Y' para años.", status=400)
    
    # Obtener la última fecha de modificación de los datos para el cache_key
    ultima_modificacion = Venta.objects.aggregate(max_fecha=Max('fecha'))['max_fecha']
    cache_key = f'ventas_grafico_image_{periodo}_{fecha_inicio}_{fecha_fin}_{producto_id}_{ultima_modificacion}'
    cached_image = cache.get(cache_key)
    
    if cached_image:
        return HttpResponse(cached_image, content_type='image/png')
    
    # Obtener datos de ventas usando Django ORM
    ventas = Venta.objects.all().values('fecha', 'monto', 'cantidad', 'producto', 'costo_unitario', 'descuentos', 'devoluciones')
    
    # Convertir los datos a un DataFrame de pandas
    df = pd.DataFrame(list(ventas))
    
    # Filtrar por producto si se especifica
    if producto_id and producto_id != '__all__':
        df = df[df['producto'] == producto_id]
    
    # Verificar si el DataFrame no está vacío
    if df.empty:
        return HttpResponse("No hay datos disponibles", status=204)
    
    # Asegurarse de que la columna 'fecha' es de tipo datetime
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    # Filtrar por fechas si se especifican
    if fecha_inicio:
        fecha_inicio = pd.to_datetime(fecha_inicio)
        df = df[df['fecha'] >= fecha_inicio]
    if fecha_fin:
        fecha_fin = pd.to_datetime(fecha_fin)
        df = df[df['fecha'] <= fecha_fin]
    
    # Crear una nueva columna que represente el período seleccionado
    if periodo == 'H':
        df['periodo'] = df['fecha'].dt.to_period('h')
    elif periodo == 'D':
        df['periodo'] = df['fecha'].dt.to_period('d')
    elif periodo == 'M':
        df['periodo'] = df['fecha'].dt.to_period('M')
    elif periodo == 'Y':
        df['periodo'] = df['fecha'].dt.to_period('Y')
    
    # Agrupar por período y sumar los montos y cantidades
    df_periodic = df.groupby('periodo').agg({'monto': 'sum', 'cantidad': 'sum'}).reset_index()
    
    # Convertir el período a fechas para la visualización
    df_periodic['periodo'] = df_periodic['periodo'].apply(lambda x: x.to_timestamp())
    
    # Agrupar por producto y sumar los montos y cantidades
    df_productos = df.groupby('producto').agg({'monto': 'sum', 'cantidad': 'sum'}).reset_index()
    
    # Crear figura y ejes en una cuadrícula 3x2
    fig, axs = plt.subplots(3, 2, figsize=(18, 24))
    axs = axs.flatten()
    
    def draw_gray_border(ax):
        for _, spine in ax.spines.items():
            spine.set_edgecolor('gray')
            spine.set_linewidth(2)
    
    try:
        # Primer gráfico: Línea de ventas por fecha
        axs[0].plot(df_periodic['periodo'], df_periodic['monto'], color='red', marker='o')
        axs[0].set_xlabel('Fecha', fontsize=14)
        axs[0].set_ylabel('Monto', fontsize=14)
        axs[0].set_title('Ventas por Fecha', fontsize=16)
        axs[0].xaxis.set_major_locator(plt.MaxNLocator(len(df_periodic)))
        axs[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: pd.to_datetime(x).strftime('%Y-%m-%d %H:%M:%S')))
        axs[0].tick_params(axis='x', rotation=45)
        axs[0].grid(True)
        draw_gray_border(axs[0])
        
        # Segundo gráfico: Línea de cantidad por fecha
        axs[1].plot(df_periodic['periodo'], df_periodic['cantidad'], color='blue', marker='o')
        axs[1].set_xlabel('Fecha', fontsize=14)
        axs[1].set_ylabel('Cantidad', fontsize=14)
        axs[1].set_title('Cantidad de Ventas por Fecha', fontsize=16)
        axs[1].xaxis.set_major_locator(plt.MaxNLocator(len(df_periodic)))
        axs[1].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: pd.to_datetime(x).strftime('%Y-%m-%d %H:%M:%S')))
        axs[1].tick_params(axis='x', rotation=45)
        axs[1].grid(True)
        draw_gray_border(axs[1])
        
        # Tercer gráfico: Histograma de ventas por período
        axs[2].bar(df_periodic['periodo'], df_periodic['monto'], color='red')
        axs[2].set_xlabel('Período', fontsize=14)
        axs[2].set_ylabel('Monto Total', fontsize=14)
        axs[2].set_title(f'Histograma de Ventas por Período ({periodo})', fontsize=16)
        axs[2].xaxis.set_major_locator(plt.MaxNLocator(len(df_periodic)))
        axs[2].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: pd.to_datetime(x).strftime('%Y-%m-%d %H:%M:%S')))
        axs[2].tick_params(axis='x', rotation=45)
        draw_gray_border(axs[2])
        
        # Cuarto gráfico: Histograma de cantidad por período
        axs[3].bar(df_periodic['periodo'], df_periodic['cantidad'], color='blue')
        axs[3].set_xlabel('Período', fontsize=14)
        axs[3].set_ylabel('Cantidad Total', fontsize=14)
        axs[3].set_title(f'Histograma de Cantidad por Período ({periodo})', fontsize=16)
        axs[3].xaxis.set_major_locator(plt.MaxNLocator(len(df_periodic)))
        axs[3].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: pd.to_datetime(x).strftime('%Y-%m-%d %H:%M:%S')))
        axs[3].tick_params(axis='x', rotation=45)
        draw_gray_border(axs[3])
        
        # Quinto gráfico: Gráfico de pastel de montos por producto
        axs[4].pie(df_productos['monto'], labels=df_productos['producto'], autopct='%1.1f%%', colors=plt.get_cmap('tab20').colors, textprops={'fontsize': 12})
        axs[4].set_title('Distribución de Montos por Producto', fontsize=16)
        draw_gray_border(axs[4])
        
        # Sexto gráfico: Gráfico de pastel de cantidades por producto
        axs[5].pie(df_productos['cantidad'], labels=df_productos['producto'], autopct='%1.1f%%', colors=plt.get_cmap('tab20').colors, textprops={'fontsize': 12})
        axs[5].set_title('Distribución de Cantidades por Producto', fontsize=16)
        draw_gray_border(axs[5])
        
        # Ajustar el espacio entre subgráficos
        plt.tight_layout()
        
        # Guardar la figura en un buffer de memoria
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        
        # Guardar la imagen en caché
        cache.set(cache_key, buffer.getvalue(), timeout=60 * 15)
        
        # Devolver la imagen
        return HttpResponse(buffer.getvalue(), content_type='image/png')
    except Exception as e:
        print(f"Error al generar el gráfico: {e}")
        return HttpResponse("Error al generar el gráfico", status=500)

