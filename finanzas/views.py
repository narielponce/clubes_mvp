from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import date
from .models import Cuenta, Deuda, ItemDeuda, Transaccion, Comprobante
from .forms import (
    CuentaForm, DeudaForm, ItemDeudaForm, TransaccionForm, 
    ComprobanteForm, GenerarDeudasForm
)
from socios.models import Socio, TipoSocio
from disciplinas.models import Disciplina, Categoria
from usuarios.decorators import tesorero_required
from django.db.models import Q
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group # Ensure Group is imported
from django.db import models # Added for Min and F
from django.http import HttpResponse

# Vistas de Cuentas
@login_required
@tesorero_required
def lista_cuentas(request):
    cuentas = Cuenta.objects.all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        cuentas = cuentas.filter(tipo=tipo)
    
    activa = request.GET.get('activa')
    if activa is not None:
        activa_bool = activa == '1'
        cuentas = cuentas.filter(activa=activa_bool)
    
    # Ordenar por nombre
    cuentas = cuentas.order_by('nombre')
    
    # Paginación
    paginator = Paginator(cuentas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'finanzas/lista_cuentas.html', {
        'page_obj': page_obj,
        'cuentas': page_obj,
        'tipo_filtro': tipo,
        'activa_filtro': activa
    })

@login_required
@tesorero_required
def crear_cuenta(request):
    if request.method == 'POST':
        form = CuentaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta creada exitosamente.')
            return redirect('finanzas:lista_cuentas')
    else:
        form = CuentaForm()
    
    return render(request, 'finanzas/form_cuenta.html', {'form': form, 'titulo': 'Crear Cuenta'})

@login_required
@tesorero_required
def editar_cuenta(request, pk):
    cuenta = get_object_or_404(Cuenta, pk=pk)
    if request.method == 'POST':
        form = CuentaForm(request.POST, instance=cuenta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuenta actualizada exitosamente.')
            return redirect('finanzas:lista_cuentas')
    else:
        form = CuentaForm(instance=cuenta)
    
    return render(request, 'finanzas/form_cuenta.html', {
        'form': form, 
        'cuenta': cuenta,
        'titulo': 'Editar Cuenta'
    })

@login_required
@tesorero_required
def eliminar_cuenta(request, pk):
    cuenta = get_object_or_404(Cuenta, pk=pk)
    
    # Verificar si la cuenta tiene transacciones asociadas
    transacciones_count = cuenta.transacciones.count()
    
    if request.method == 'POST':
        if transacciones_count > 0:
            messages.error(request, f'No se puede eliminar la cuenta "{cuenta.nombre}" porque tiene {transacciones_count} transacción(es) asociada(s).')
        else:
            nombre_cuenta = cuenta.nombre
            cuenta.delete()
            messages.success(request, f'Cuenta "{nombre_cuenta}" eliminada exitosamente.')
        return redirect('finanzas:lista_cuentas')
    
    return render(request, 'finanzas/confirmar_eliminar_cuenta.html', {
        'cuenta': cuenta,
        'transacciones_count': transacciones_count
    })

# Vistas de Deudas
@login_required
@tesorero_required
def lista_deudas(request):
    deudas = Deuda.objects.all()
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        deudas = deudas.filter(estado=estado)
    
    socio_id = request.GET.get('socio')
    if socio_id:
        deudas = deudas.filter(socio_id=socio_id)
    
    # Paginación
    paginator = Paginator(deudas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    socios = Socio.objects.all()
    
    return render(request, 'finanzas/lista_deudas.html', {
        'page_obj': page_obj,
        'socios': socios,
        'estado_filtro': estado,
        'socio_filtro': socio_id
    })

@login_required
@tesorero_required
def crear_deuda(request):
    if request.method == 'POST':
        form = DeudaForm(request.POST)
        if form.is_valid():
            deuda = form.save(commit=False)
            deuda.generada_por = request.user
            deuda.save()
            messages.success(request, 'Deuda creada exitosamente.')
            return redirect('finanzas:editar_deuda', pk=deuda.pk)
    else:
        form = DeudaForm()
    
    return render(request, 'finanzas/form_deuda.html', {'form': form, 'titulo': 'Crear Deuda'})

@login_required
@tesorero_required
def editar_deuda(request, pk):
    deuda = get_object_or_404(Deuda, pk=pk)
    
    if request.method == 'POST':
        form = DeudaForm(request.POST, instance=deuda)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deuda actualizada exitosamente.')
            return redirect('finanzas:lista_deudas')
    else:
        form = DeudaForm(instance=deuda)
    
    # Formulario para agregar items
    item_form = ItemDeudaForm()
    
    return render(request, 'finanzas/form_deuda.html', {
        'form': form,
        'item_form': item_form,
        'deuda': deuda,
        'titulo': 'Editar Deuda'
    })

@login_required
@tesorero_required
def agregar_item_deuda(request, deuda_id):
    deuda = get_object_or_404(Deuda, pk=deuda_id)
    
    if request.method == 'POST':
        form = ItemDeudaForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.deuda = deuda
            item.save()
            deuda.calcular_total()
            messages.success(request, 'Item agregado exitosamente.')
        else:
            messages.error(request, 'Error al agregar el item.')
    
    return redirect('finanzas:editar_deuda', pk=deuda_id)

@login_required
@tesorero_required
def eliminar_item_deuda(request, item_id):
    item = get_object_or_404(ItemDeuda, pk=item_id)
    deuda = item.deuda
    item.delete()
    deuda.calcular_total()
    messages.success(request, 'Item eliminado exitosamente.')
    return redirect('finanzas:editar_deuda', pk=deuda.pk)

@login_required
@tesorero_required
def generar_deudas_masivas(request):
    if request.method == 'POST':
        form = GenerarDeudasForm(request.POST)
        if form.is_valid():
            socios_ids = form.cleaned_data['socios']
            fecha_vencimiento = form.cleaned_data['fecha_vencimiento']
            cuota_societaria = form.cleaned_data['cuota_societaria']
            incluir_disciplinas = form.cleaned_data['incluir_disciplinas']
            observaciones = form.cleaned_data['observaciones']
            
            # Convertir la cadena de IDs en una lista de socios
            ids_list = [int(id.strip()) for id in socios_ids.split(',') if id.strip()]
            socios = Socio.objects.filter(id__in=ids_list)
            
            deudas_creadas = 0
            
            with transaction.atomic():
                for socio in socios:
                    # Crear deuda
                    deuda = Deuda.objects.create(
                        socio=socio,
                        fecha_vencimiento=fecha_vencimiento,
                        observaciones=observaciones,
                        generada_por=request.user
                    )
                    
                    # Agregar cuota societaria si se especificó
                    if cuota_societaria and cuota_societaria > 0:
                        ItemDeuda.objects.create(
                            deuda=deuda,
                            tipo='CUOTA_SOCIETARIA',
                            descripcion='Cuota societaria mensual',
                            monto=cuota_societaria
                        )
                    
                    # Agregar cuotas de disciplinas si se solicitó
                    if incluir_disciplinas:
                        # Obtener las inscripciones activas del socio
                        inscripciones_activas = socio.inscripciones.filter(activa=True)
                        
                        if inscripciones_activas.exists():
                            # Agrupar por disciplina para evitar duplicados
                            disciplinas_unicas = {}
                            for inscripcion in inscripciones_activas:
                                disciplina = inscripcion.categoria.disciplina
                                if disciplina.id not in disciplinas_unicas:
                                    disciplinas_unicas[disciplina.id] = disciplina
                            
                            # Crear un item por cada disciplina única
                            for disciplina in disciplinas_unicas.values():
                                ItemDeuda.objects.create(
                                    deuda=deuda,
                                    tipo='CUOTA_DISCIPLINA',
                                    descripcion=f'Cuota mensual - {disciplina.nombre}',
                                    monto=disciplina.costo_mensual
                                )
                        else:
                            # Si no tiene inscripciones activas, crear un item vacío
                            ItemDeuda.objects.create(
                                deuda=deuda,
                                tipo='CUOTA_DISCIPLINA',
                                descripcion='Cuota por disciplinas practicadas',
                                monto=0
                            )
                    
                    deuda.calcular_total()
                    deudas_creadas += 1
            
            messages.success(request, f'Se generaron {deudas_creadas} deudas exitosamente.')
            return redirect('finanzas:lista_deudas')
    else:
        form = GenerarDeudasForm()
    
    # Pasar el queryset de socios al template para el JavaScript
    socios_queryset = form.get_socios_queryset()
    
    return render(request, 'finanzas/generar_deudas.html', {
        'form': form,
        'socios_queryset': socios_queryset
    })

# Vistas de Transacciones
@login_required
@tesorero_required
def lista_transacciones(request):
    transacciones = Transaccion.objects.all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    if tipo:
        transacciones = transacciones.filter(tipo=tipo)
    
    cuenta_id = request.GET.get('cuenta')
    if cuenta_id:
        transacciones = transacciones.filter(cuenta_id=cuenta_id)
    
    fecha_desde = request.GET.get('fecha_desde')
    if fecha_desde:
        transacciones = transacciones.filter(fecha__gte=fecha_desde)
    
    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_hasta:
        transacciones = transacciones.filter(fecha__lte=fecha_hasta)
    
    # Paginación
    paginator = Paginator(transacciones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    cuentas = Cuenta.objects.filter(activa=True)
    
    return render(request, 'finanzas/lista_transacciones.html', {
        'page_obj': page_obj,
        'cuentas': cuentas,
        'tipo_filtro': tipo,
        'cuenta_filtro': cuenta_id,
        'fecha_desde_filtro': fecha_desde,
        'fecha_hasta_filtro': fecha_hasta
    })

@login_required
@tesorero_required
def crear_transaccion(request):
    if request.method == 'POST':
        form = TransaccionForm(request.POST)
        if form.is_valid():
            transaccion = form.save(commit=False)
            transaccion.registrado_por = request.user
            deuda = form.cleaned_data.get('deuda_relacionada')
            if deuda:
                transaccion.deuda_relacionada = deuda
            transaccion.save()
            # Si es un pago de cuotas y se seleccionó una deuda, actualizar su estado
            if transaccion.categoria == 'CUOTAS' and deuda and transaccion.tipo == 'INGRESO':
                try:
                    if transaccion.monto >= deuda.monto_total:
                        deuda.estado = 'PAGADA'
                        deuda.save()
                    # Si se quiere soportar pagos parciales, aquí se puede agregar lógica adicional
                    messages.success(request, f'Transacción registrada y aplicada a la deuda de {deuda.socio.perfil_usuario.usuario.get_full_name()}')
                except Exception as e:
                    messages.warning(request, f'Transacción registrada pero hubo un problema al actualizar la deuda: {str(e)}')
            else:
                messages.success(request, 'Transacción registrada exitosamente.')
            return redirect('finanzas:lista_transacciones')
    else:
        form = TransaccionForm()
    return render(request, 'finanzas/form_transaccion.html', {
        'form': form,
        'titulo': 'Registrar Transacción'
    })

@login_required
@tesorero_required
def editar_transaccion(request, pk):
    transaccion = get_object_or_404(Transaccion, pk=pk)
    
    if request.method == 'POST':
        form = TransaccionForm(request.POST, instance=transaccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transacción actualizada exitosamente.')
            return redirect('finanzas:lista_transacciones')
    else:
        form = TransaccionForm(instance=transaccion)
    
    return render(request, 'finanzas/form_transaccion.html', {
        'form': form,
        'transaccion': transaccion,
        'titulo': 'Editar Transacción'
    })

# Vistas de Comprobantes
@login_required
@tesorero_required
def agregar_comprobante(request, transaccion_id):
    transaccion = get_object_or_404(Transaccion, pk=transaccion_id)
    
    if request.method == 'POST':
        form = ComprobanteForm(request.POST, request.FILES)
        if form.is_valid():
            comprobante = form.save(commit=False)
            comprobante.transaccion = transaccion
            comprobante.save()
            messages.success(request, 'Comprobante agregado exitosamente.')
            return redirect('finanzas:lista_transacciones')
    else:
        form = ComprobanteForm()
    
    return render(request, 'finanzas/form_comprobante.html', {
        'form': form,
        'transaccion': transaccion,
        'titulo': 'Agregar Comprobante'
    })

# Vistas de Dashboard y Reportes
@login_required
@tesorero_required
def dashboard_finanzas(request):
    # Estadísticas básicas
    total_cuentas = Cuenta.objects.count()
    cuentas_activas = Cuenta.objects.filter(activa=True).count()
    saldo_total = sum(cuenta.saldo_actual for cuenta in Cuenta.objects.filter(activa=True))
    
    # Deudas
    deudas_pendientes = Deuda.objects.filter(estado='PENDIENTE').count()
    deudas_vencidas = Deuda.objects.filter(estado='VENCIDA').count()
    total_deudas_pendientes = sum(deuda.monto_total for deuda in Deuda.objects.filter(estado='PENDIENTE'))
    
    # Transacciones del mes actual
    mes_actual = timezone.now().month
    año_actual = timezone.now().year
    transacciones_mes = Transaccion.objects.filter(
        fecha__month=mes_actual,
        fecha__year=año_actual
    )
    
    ingresos_mes = sum(t.monto for t in transacciones_mes.filter(tipo='INGRESO'))
    egresos_mes = sum(t.monto for t in transacciones_mes.filter(tipo='EGRESO'))
    
    # Últimas transacciones
    ultimas_transacciones = Transaccion.objects.all()[:5]
    
    context = {
        'total_cuentas': total_cuentas,
        'cuentas_activas': cuentas_activas,
        'saldo_total': saldo_total,
        'deudas_pendientes': deudas_pendientes,
        'deudas_vencidas': deudas_vencidas,
        'total_deudas_pendientes': total_deudas_pendientes,
        'ingresos_mes': ingresos_mes,
        'egresos_mes': egresos_mes,
        'ultimas_transacciones': ultimas_transacciones,
    }
    
    return render(request, 'finanzas/dashboard.html', context)

# API para obtener categorías de una disciplina
@login_required
def get_categorias_disciplina(request):
    disciplina_id = request.GET.get('disciplina_id')
    if disciplina_id:
        categorias = Categoria.objects.filter(disciplina_id=disciplina_id)
        data = [{'id': cat.id, 'nombre': cat.nombre} for cat in categorias]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@login_required
def lista_socios_finanzas(request):
    if not request.user.groups.filter(name__in=['Administrador', 'Tesoreria', 'Comision']).exists():
        messages.error(request, 'No tienes permisos para acceder a esta funcionalidad.')
        return redirect('usuarios:dashboard')
    query = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')

    socios = Socio.objects.select_related('perfil_usuario', 'tipo_socio').all()

    if query:
        socios = socios.filter(
            Q(perfil_usuario__usuario__first_name__icontains=query) |
            Q(perfil_usuario__usuario__last_name__icontains=query) |
            Q(tipo_socio__nombre__icontains=query) |
            Q(id__icontains=query)
        )
    if tipo:
        socios = socios.filter(tipo_socio__nombre=tipo)
    if estado:
        if estado == 'activo':
            socios = socios.filter(perfil_usuario__esta_activo_sistema=True)
        elif estado == 'inactivo':
            socios = socios.filter(perfil_usuario__esta_activo_sistema=False)

    tipos = TipoSocio.objects.all()
    return render(request, 'finanzas/lista_socios_finanzas.html', {
        'socios': socios,
        'tipos': tipos,
        'query': query,
        'tipo_selected': tipo,
        'estado_selected': estado,
    })

@login_required
def consultar_estado_cuenta(request, socio_id=None):
    """
    Vista para consultar el estado de cuenta de un socio específico.
    Los administradores, tesoreros y comisión pueden ver cualquier socio.
    Los socios solo pueden ver su propio estado de cuenta.
    """
    # Determinar qué socio consultar
    if socio_id:
        # Si se proporciona un socio_id, verificar permisos
        if request.user.groups.filter(name__in=['Administrador', 'Tesoreria', 'Comision']).exists():
            # Administradores, tesoreros y comisión pueden ver cualquier socio
            socio = get_object_or_404(Socio, id=socio_id)
        else:
            # Otros usuarios solo pueden ver su propio estado de cuenta
            if hasattr(request.user.perfil, 'socio') and request.user.perfil.socio.id == socio_id:
                socio = request.user.perfil.socio
            else:
                messages.error(request, 'No tienes permisos para ver el estado de cuenta de otro socio.')
                return redirect('usuarios:dashboard')
    else:
        # Si no se proporciona socio_id, mostrar el estado de cuenta del usuario actual
        if hasattr(request.user.perfil, 'socio'):
            socio = request.user.perfil.socio
        else:
            messages.error(request, 'No tienes un perfil de socio asociado.')
            return redirect('usuarios:dashboard')
    
    # Obtener deudas del socio
    deudas = socio.deudas.all().order_by('-fecha_generacion')
    
    # Obtener transacciones relacionadas con el socio
    transacciones = Transaccion.objects.filter(
        deuda_relacionada__socio=socio,
        categoria='CUOTAS',
        tipo='INGRESO'
    ).order_by('-fecha')
    
    # Calcular totales
    total_deudas = sum(deuda.monto_total for deuda in deudas if deuda.estado in ['PENDIENTE', 'VENCIDA'])
    total_pagado = sum(transaccion.monto for transaccion in transacciones)
    saldo_pendiente = total_deudas - total_pagado
    
    # Obtener deudas por estado
    deudas_pendientes = deudas.filter(estado='PENDIENTE')
    deudas_vencidas = deudas.filter(estado='VENCIDA')
    deudas_pagadas = deudas.filter(estado='PAGADA')
    
    # Crear listado cronológico combinando deudas y pagos
    movimientos = []
    
    # Agregar todas las deudas al listado (incluyendo pagadas)
    for deuda in deudas:
        for item in deuda.items.all():
            movimientos.append({
                'fecha': deuda.fecha_generacion,
                'concepto': item.descripcion,
                'importe': -item.monto,  # Negativo porque es una deuda
                'tipo': 'deuda',
                'deuda': deuda,
                'item': item
            })
    
    # Agregar pagos al listado
    for transaccion in transacciones:
        movimientos.append({
            'fecha': transaccion.fecha,
            'concepto': f"Pago de {transaccion.descripcion.lower()}",
            'importe': transaccion.monto,  # Positivo porque es un pago
            'tipo': 'pago',
            'transaccion': transaccion
        })
    
    # Ordenar movimientos por fecha (más reciente primero)
    movimientos.sort(key=lambda x: x['fecha'], reverse=True)
    
    # Información adicional para usuarios con roles de gestión
    es_usuario_actual = (request.user.perfil.socio == socio if hasattr(request.user.perfil, 'socio') else False)
    tiene_roles_gestion = request.user.groups.filter(name__in=['Administrador', 'Tesoreria', 'Comision', 'Coordinador']).exists()
    
    # Estadísticas adicionales
    total_deudas_generadas = deudas.count()
    deudas_ultimo_mes = deudas.filter(fecha_generacion__gte=timezone.now().date() - timezone.timedelta(days=30)).count()
    pagos_ultimo_mes = transacciones.filter(fecha__gte=timezone.now().date() - timezone.timedelta(days=30)).count()
    
    context = {
        'socio': socio,
        'deudas': deudas,
        'transacciones': transacciones,
        'movimientos': movimientos,
        'total_deudas': total_deudas,
        'total_pagado': total_pagado,
        'saldo_pendiente': saldo_pendiente,
        'deudas_pendientes': deudas_pendientes,
        'deudas_vencidas': deudas_vencidas,
        'deudas_pagadas': deudas_pagadas,
        'puede_editar': request.user.groups.filter(name__in=['Administrador', 'Tesoreria']).exists(),
        'es_usuario_actual': es_usuario_actual,
        'tiene_roles_gestion': tiene_roles_gestion,
        'total_deudas_generadas': total_deudas_generadas,
        'deudas_ultimo_mes': deudas_ultimo_mes,
        'pagos_ultimo_mes': pagos_ultimo_mes,
    }
    
    return render(request, 'finanzas/estado_cuenta.html', context)

@login_required
def lista_estados_cuenta(request):
    """
    Vista para listar todos los estados de cuenta (solo para administradores, tesoreros y comisión)
    """
    if not request.user.groups.filter(name__in=['Administrador', 'Tesoreria', 'Comision']).exists():
        messages.error(request, 'No tienes permisos para acceder a esta funcionalidad.')
        return redirect('usuarios:dashboard')
    
    # Filtros
    query = request.GET.get('q', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    tipo_filtro = request.GET.get('tipo', '').strip()
    
    socios = Socio.objects.select_related('perfil_usuario', 'tipo_socio').all()
    
    # Aplicar filtros
    if query:
        socios = socios.filter(
            Q(perfil_usuario__usuario__first_name__icontains=query) |
            Q(perfil_usuario__usuario__last_name__icontains=query) |
            Q(tipo_socio__nombre__icontains=query) |
            Q(id__icontains=query)
        )
    
    if tipo_filtro:
        socios = socios.filter(tipo_socio__nombre=tipo_filtro)
    
    if estado_filtro:
        if estado_filtro == 'activo':
            socios = socios.filter(perfil_usuario__esta_activo_sistema=True)
        elif estado_filtro == 'inactivo':
            socios = socios.filter(perfil_usuario__esta_activo_sistema=False)
        elif estado_filtro == 'con_deuda':
            socios = socios.filter(deudas__estado__in=['PENDIENTE', 'VENCIDA']).distinct()
        elif estado_filtro == 'sin_deuda':
            socios = socios.exclude(deudas__estado__in=['PENDIENTE', 'VENCIDA'])
    
    # Calcular información financiera para cada socio
    socios_con_info = []
    for socio in socios:
        deudas_pendientes = socio.deudas.filter(estado__in=['PENDIENTE', 'VENCIDA'])
        total_deudas = sum(deuda.monto_total for deuda in deudas_pendientes)
        transacciones = Transaccion.objects.filter(
            deuda_relacionada__socio=socio,
            categoria='CUOTAS',
            tipo='INGRESO'
        )
        total_pagado = sum(transaccion.monto for transaccion in transacciones)
        saldo_pendiente = total_deudas - total_pagado
        
        socios_con_info.append({
            'socio': socio,
            'total_deudas': total_deudas,
            'total_pagado': total_pagado,
            'saldo_pendiente': saldo_pendiente,
            'tiene_deudas_pendientes': total_deudas > 0,
            'tiene_deudas_vencidas': socio.deudas.filter(estado='VENCIDA').exists(),
        })
    
    # Ordenar por saldo pendiente (mayor a menor)
    socios_con_info.sort(key=lambda x: x['saldo_pendiente'], reverse=True)
    
    tipos = TipoSocio.objects.all()
    
    context = {
        'socios_con_info': socios_con_info,
        'tipos': tipos,
        'query': query,
        'estado_filtro': estado_filtro,
        'tipo_filtro': tipo_filtro,
    }
    
    return render(request, 'finanzas/lista_estados_cuenta.html', context)

def puede_ver_reportes(user):
    return user.is_authenticated and user.groups.filter(name__in=['Administrador', 'Tesoreria', 'Comision']).exists()

@login_required
@user_passes_test(puede_ver_reportes)
def reportes_view(request):
    return render(request, 'reportes.html')

@login_required
def reporte_financiero(request):
    # Calculate total ingresos and egresos for the financial report
    # This logic should mirror or be adapted from how it was calculated for reportes.html

    # For demonstration, let's assume a fixed period or get it from request
    # You might want to add filters for period_reporte in the future
    periodo_reporte = "Anual (2023)" # Example: replace with dynamic calculation
    
    total_ingresos = Transaccion.objects.filter(tipo='INGRESO').aggregate(Sum('monto'))['monto__sum'] or 0
    total_egresos = Transaccion.objects.filter(tipo='EGRESO').aggregate(Sum('monto'))['monto__sum'] or 0

    # --- NUEVO: Cuentas por cobrar (socios deudores) ---
    deudas_pendientes = Deuda.objects.filter(estado__in=['PENDIENTE', 'VENCIDA'])
    socios_deudores = (
        deudas_pendientes
        .values('socio')
        .annotate(
            nombre=models.F('socio__perfil_usuario__usuario__first_name'),
            apellido=models.F('socio__perfil_usuario__usuario__last_name'),
            monto_total=models.Sum('monto_total'),
            fecha_mas_antigua=models.Min('fecha_generacion')
        )
        .order_by('-monto_total')
    )
    # Calcular antigüedad en días
    for s in socios_deudores:
        if s['fecha_mas_antigua']:
            s['antiguedad'] = (date.today() - s['fecha_mas_antigua']).days
        else:
            s['antiguedad'] = None
        s['nombre_completo'] = f"{s['nombre']} {s['apellido']}".strip()

    socios_deudores = list(socios_deudores)
    total_deudores = len(socios_deudores)
    socios_deudores = socios_deudores[:5]

    context = {
        'periodo_reporte': periodo_reporte,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'socios_deudores': socios_deudores,
        'total_deudores': total_deudores,
    }
    return render(request, 'finanzas/reporte_financiero.html', context)

def cuentas_por_cobrar_placeholder(request):
    return HttpResponse("Vista de detalle de cuentas por cobrar próximamente.")
