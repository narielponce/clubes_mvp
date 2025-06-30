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
from socios.models import Socio
from disciplinas.models import Disciplina, Categoria
from usuarios.decorators import tesorero_required

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
            transaccion.save()
            
            # Si es un pago de cuotas y se seleccionó un socio, actualizar su cuenta corriente
            socio_pago = form.cleaned_data.get('socio_pago')
            if transaccion.categoria == 'CUOTAS' and socio_pago and transaccion.tipo == 'INGRESO':
                # Aquí podrías actualizar la cuenta corriente del socio
                # Por ejemplo, marcar deudas como pagadas o actualizar saldo
                try:
                    # Buscar deudas pendientes del socio y marcarlas como pagadas
                    deudas_pendientes = Deuda.objects.filter(
                        socio=socio_pago,
                        estado='PENDIENTE'
                    ).order_by('fecha_vencimiento')
                    
                    monto_restante = transaccion.monto
                    for deuda in deudas_pendientes:
                        if monto_restante >= deuda.monto_total:
                            deuda.estado = 'PAGADA'
                            deuda.save()
                            monto_restante -= deuda.monto_total
                        else:
                            # Si no alcanza para pagar toda la deuda, crear una transacción parcial
                            break
                    
                    messages.success(request, f'Transacción registrada y aplicada a la cuenta de {socio_pago.perfil_usuario.usuario.get_full_name()}')
                except Exception as e:
                    messages.warning(request, f'Transacción registrada pero hubo un problema al actualizar la cuenta del socio: {str(e)}')
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
