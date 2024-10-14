from django.urls import path
from . import views

app_name = 'businessmodel'

urlpatterns = [
    path('inicio/<int:venta_id>/',views.inicio_venta,name='inicio_venta'),

    path ('Información-de-venta/<int:venta_id>/', views.informacion_venta,name='informacion_venta'),
    path ('Informacioón-de-venta-productos/<int:venta_id>/',views.informacion_venta_productos ,name='informacion_venta_productos'),

    path('admin/ventas/<int:venta_id>/', views.admin_ventas_detail, name='admin_ventas_detail'),
    path('admin/ventas/<int:venta_id>/pdf/', views.admin_comprobante_pdf, name='admin_comprobante_pdf'),

    path('admin/ventas/historial/<int:venta_id>/', views.admin_historial, name='admin_historial'),
    path('historial-ventas-productos/<int:venta_id>/', views.historial_ventas_productos, name='historial_ventas_productos'),
    path('historical-incomes-amount/<int:venta_id>/', views.history_incomes_amount, name='history_incomes_amount'),
    path('historical-incomes-product/<int:venta_id>/', views.history_incomes_product, name='history_incomes_product'),
    path('admin/historial_ventas/<int:venta_id>/pdf/', views.admin_comprobante_historial_pdf, name='admin_comprobante_historial_pdf'),

    path('admin/ventas/metricas/<int:venta_id>/', views.admin_metricas, name='admin_metricas'),
    path('income-scatter/<int:venta_id>/', views.income_scatter, name='income_scatter'),
    path('metricas-ventas-pie/time/<int:venta_id>/', views.pie_incomes_time, name='pie_incomes_time'),
    path('metricas-ventas-pie/product/<int:venta_id>/', views.pie_incomes_product, name='pie_incomes_product'),
    path('histogram-income-amount/<int:venta_id>/', views.income_histogram_amount, name='income_histogram_amount'),
    path('histogram-income-product/<int:venta_id>/', views.income_histogram_product, name='income_histogram_product'),
    path('histogram-income-category/<int:venta_id>/', views.income_histogram_category, name='income_histogram_category'),
    path('admin/Distribución-de-ventas/<int:venta_id>/pdf/', views.metricas_ventas_comprobante, name='metricas_ventas_comprobante'),
]
