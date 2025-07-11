from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard_finanzas, name='dashboard'),
    
    # Cuentas
    path('cuentas/', views.lista_cuentas, name='lista_cuentas'),
    path('cuentas/crear/', views.crear_cuenta, name='crear_cuenta'),
    path('cuentas/<int:pk>/editar/', views.editar_cuenta, name='editar_cuenta'),
    path('cuentas/<int:pk>/eliminar/', views.eliminar_cuenta, name='eliminar_cuenta'),
    
    # Deudas
    path('deudas/', views.lista_deudas, name='lista_deudas'),
    path('deudas/crear/', views.crear_deuda, name='crear_deuda'),
    path('deudas/<int:pk>/editar/', views.editar_deuda, name='editar_deuda'),
    path('deudas/generar-masivas/', views.generar_deudas_masivas, name='generar_deudas_masivas'),
    path('deudas/<int:deuda_id>/agregar-item/', views.agregar_item_deuda, name='agregar_item_deuda'),
    path('items-deuda/<int:item_id>/eliminar/', views.eliminar_item_deuda, name='eliminar_item_deuda'),
    
    # Transacciones
    path('transacciones/', views.lista_transacciones, name='lista_transacciones'),
    path('transacciones/crear/', views.crear_transaccion, name='crear_transaccion'),
    path('transacciones/<int:pk>/editar/', views.editar_transaccion, name='editar_transaccion'),
    
    # Comprobantes
    path('transacciones/<int:transaccion_id>/comprobante/', views.agregar_comprobante, name='agregar_comprobante'),
    
    # Estado de Cuenta
    path('estado-cuenta/', views.consultar_estado_cuenta, name='estado_cuenta'),
    path('estado-cuenta/<int:socio_id>/', views.consultar_estado_cuenta, name='estado_cuenta_socio'),
    path('estados-cuenta/', views.lista_estados_cuenta, name='lista_estados_cuenta'),
    
    # API
    path('api/categorias-disciplina/', views.get_categorias_disciplina, name='get_categorias_disciplina'),
    path('socios/', views.lista_socios_finanzas, name='lista_socios_finanzas'),
    path('reporte_financiero/', views.reporte_financiero, name='reporte_financiero'),
    path('cuentas_por_cobrar/', views.cuentas_por_cobrar_placeholder, name='cuentas_por_cobrar'),

] 