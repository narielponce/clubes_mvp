from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import PerfilUsuario
from .forms import UsuarioForm, PerfilUsuarioForm, MiUsuarioForm, MiPerfilUsuarioForm
from django.db.models import Count, Sum
from django.db.models import Q
from .decorators import verificar_rol
from socios.models import Socio
from disciplinas.models import Disciplina, Categoria, Inscripcion
from finanzas.models import Cuenta, Deuda, Transaccion
from django.utils import timezone

def is_admin(user):
    return user.groups.filter(name='Administrador').exists()

def is_coordinador(user):
    return user.groups.filter(name='Coordinador').exists()

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('usuarios:dashboard')
        else:
            return render(request, 'usuarios/login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('usuarios:login')

@login_required
def dashboard(request):
    # Obtener el perfil del usuario
    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        return render(request, 'usuarios/dashboard.html', {'rol': 'Sin Perfil'})

    # Verificar roles de grupo
    grupos = request.user.groups.values_list('name', flat=True)
    
    # Verificar si es socio
    es_socio = hasattr(perfil, 'socio')
    
    # Definir roles administrativos
    roles_administrativos = ['Administrador', 'Coordinador', 'Profesor', 'Tesoreria', 'Comision']
    tiene_rol_administrativo = any(rol in grupos for rol in roles_administrativos)
    
    # Determinar el dashboard a mostrar
    if 'Administrador' in grupos:
        template = 'usuarios/admin_dash.html'
        rol = 'Administrador'
        
        # Agregar estadísticas para el dashboard de administrador
        context = {
            'rol': rol,
            'es_socio': es_socio,
            'perfil': perfil,
            'socio': perfil.socio if es_socio else None,
            'total_socios': Socio.objects.count(),
            'disciplinas_activas': Disciplina.objects.filter(activa=True).count(),
            'total_profesores': User.objects.filter(groups__name='Profesor').count(),
            'total_categorias': Categoria.objects.count(),
        }
        return render(request, template, context)
    elif 'Coordinador' in grupos:
        template = 'usuarios/dashboard.html'
        rol = 'Coordinador'
        
        # Agregar estadísticas para el dashboard de coordinador
        disciplinas_coordinadas = Disciplina.objects.filter(coordinador=perfil, activa=True)
        disciplinas_count = disciplinas_coordinadas.count()
        categorias_count = Categoria.objects.filter(disciplina__in=disciplinas_coordinadas).count()
        total_inscritos = Inscripcion.objects.filter(
            categoria__disciplina__in=disciplinas_coordinadas,
            activa=True
        ).count()
        eventos_count = 0  # Por ahora, se puede implementar más adelante
        
        context = {
            'rol': rol,
            'es_socio': es_socio,
            'perfil': perfil,
            'socio': perfil.socio if es_socio else None,
            'disciplinas_count': disciplinas_count,
            'categorias_count': categorias_count,
            'total_inscritos': total_inscritos,
            'eventos_count': eventos_count,
            'disciplinas_coordinadas': disciplinas_coordinadas,
        }
        return render(request, template, context)
    elif 'Profesor' in grupos:
        template = 'usuarios/dash_profesor.html'
        rol = 'Profesor'
    elif 'Tesoreria' in grupos:
        template = 'usuarios/dash_tesorero.html'
        rol = 'Tesoreria'
        
        # Agregar estadísticas financieras para el dashboard de tesorero
        total_cuentas = Cuenta.objects.count()
        cuentas_activas = Cuenta.objects.filter(activa=True).count()
        saldo_total = sum(cuenta.saldo_actual for cuenta in Cuenta.objects.filter(activa=True))
        deudas_pendientes = Deuda.objects.filter(estado='PENDIENTE').count()
        deudas_vencidas = Deuda.objects.filter(estado='VENCIDA').count()
        
        context = {
            'rol': rol,
            'es_socio': es_socio,
            'perfil': perfil,
            'socio': perfil.socio if es_socio else None,
            'total_cuentas': total_cuentas,
            'cuentas_activas': cuentas_activas,
            'saldo_total': saldo_total,
            'deudas_pendientes': deudas_pendientes,
            'deudas_vencidas': deudas_vencidas,
        }
        return render(request, template, context)
    elif 'Comision' in grupos:
        template = 'usuarios/dash_comision.html'
        rol = 'Comision'
        # Agregar estadísticas para el dashboard de comisión
        total_socios = Socio.objects.filter(perfil_usuario__estado_socio='ACTIVO', perfil_usuario__usuario__is_active=True).count()
        disciplinas_activas = Disciplina.objects.filter(activa=True).count()
        deudas_pendientes = Deuda.objects.filter(estado__in=['PENDIENTE', 'VENCIDA']).count()
        inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ingresos_mes = Transaccion.objects.filter(
            tipo='INGRESO',
            fecha__gte=inicio_mes
        ).aggregate(total=Sum('monto'))['total'] or 0
        socios_recientes = Socio.objects.filter(
            perfil_usuario__estado_socio='ACTIVO',
            perfil_usuario__usuario__is_active=True
        ).select_related('perfil_usuario__usuario', 'tipo_socio').order_by('-fecha_afiliacion')[:10]
        context = {
            'rol': rol,
            'es_socio': es_socio,
            'perfil': perfil,
            'socio': perfil.socio if es_socio else None,
            'total_socios': total_socios,
            'disciplinas_activas': disciplinas_activas,
            'deudas_pendientes': deudas_pendientes,
            'ingresos_mes': ingresos_mes,
            'socios_recientes': socios_recientes,
        }
        return render(request, template, context)
    else:
        # Si no tiene rol administrativo pero es socio, redirigir a su área de socio
        if es_socio:
            return redirect('socios:area')
        template = 'usuarios/dashboard.html'
        rol = 'Sin Rol Asignado'

    return render(request, template, {
        'rol': rol,
        'es_socio': es_socio,
        'perfil': perfil,
        'socio': perfil.socio if es_socio else None
    })

# Vistas para gestión de usuarios
@login_required
@user_passes_test(is_admin)
def lista_usuarios(request):
    usuarios = User.objects.all().prefetch_related('groups', 'perfil')
    grupos = Group.objects.all()
    
    # Filtros
    grupo_filtro = request.GET.get('grupo', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    busqueda = request.GET.get('busqueda', '').strip()
    
    # Aplicar filtros solo si tienen valores
    if grupo_filtro:
        usuarios = usuarios.filter(groups__name=grupo_filtro)
    if estado_filtro:
        usuarios = usuarios.filter(perfil__estado_socio=estado_filtro)
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )
    
    # Calcular estadísticas
    total_usuarios = usuarios.count()
    usuarios_activos = usuarios.filter(is_active=True).count()
    administradores = usuarios.filter(groups__name='Administrador').distinct().count()
    sin_grupos = usuarios.filter(groups__isnull=True).count()
    
    context = {
        'usuarios': usuarios,
        'grupos': grupos,
        'grupo_filtro': grupo_filtro,
        'estado_filtro': estado_filtro,
        'busqueda': busqueda,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'administradores': administradores,
        'sin_grupos': sin_grupos,
    }
    return render(request, 'usuarios/lista_usuarios.html', context)

@login_required
@user_passes_test(is_admin)
def crear_usuario(request):
    if request.method == 'POST':
        user_form = UsuarioForm(request.POST)
        perfil_form = PerfilUsuarioForm(request.POST)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            # Actualizar el perfil creado automáticamente por el signal
            perfil = user.perfil
            for field in ['tipo_documento', 'numero_documento', 'telefono', 'direccion', 'fecha_nacimiento', 'estado_socio']:
                setattr(perfil, field, perfil_form.cleaned_data[field])
            perfil.save()
            
            # Asignar grupos
            grupos = request.POST.getlist('grupos')
            user.groups.set(grupos)
            
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('usuarios:lista_usuarios')
    else:
        user_form = UsuarioForm()
        perfil_form = PerfilUsuarioForm()
    
    grupos = Group.objects.all()
    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'grupos': grupos,
    }
    return render(request, 'usuarios/crear_usuario.html', context)

@login_required
@user_passes_test(is_admin)
def editar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_form = UsuarioForm(request.POST, instance=user)
        perfil_form = PerfilUsuarioForm(request.POST, instance=user.perfil)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user = user_form.save()
            perfil_form.save()
            
            # Asignar grupos
            grupos = request.POST.getlist('grupos')
            user.groups.set(grupos)
            
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('usuarios:lista_usuarios')
    else:
        user_form = UsuarioForm(instance=user)
        perfil_form = PerfilUsuarioForm(instance=user.perfil)
    
    grupos = Group.objects.all()
    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'grupos': grupos,
        'usuario': user,
    }
    return render(request, 'usuarios/editar_usuario.html', context)

@login_required
@user_passes_test(is_admin)
def eliminar_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, 'No puedes eliminar tu propia cuenta.')
        else:
            user.delete()
            messages.success(request, 'Usuario eliminado exitosamente.')
        return redirect('usuarios:lista_usuarios')
    
    context = {'usuario': user}
    return render(request, 'usuarios/eliminar_usuario.html', context)

# Vistas para gestión de grupos
@login_required
@user_passes_test(is_admin)
def lista_grupos(request):
    # Use annotate to efficiently count users per group and avoid N+1 queries
    grupos = Group.objects.annotate(user_count=Count('user')).all()
    
    # Calcular estadísticas de manera más eficiente
    total_grupos = grupos.count()
    grupos_con_usuarios = grupos.filter(user_count__gt=0).count()
    grupos_vacios = total_grupos - grupos_con_usuarios
    
    # Calcular total de asignaciones usando annotate
    total_asignaciones = grupos.aggregate(total=Count('user'))['total'] or 0
    
    context = {
        'grupos': grupos,
        'total_grupos': total_grupos,
        'grupos_con_usuarios': grupos_con_usuarios,
        'grupos_vacios': grupos_vacios,
        'total_asignaciones': total_asignaciones,
    }
    return render(request, 'usuarios/lista_grupos.html', context)

@login_required
@user_passes_test(is_admin)
def crear_grupo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            grupo, created = Group.objects.get_or_create(name=nombre)
            if created:
                messages.success(request, 'Grupo creado exitosamente.')
            else:
                messages.warning(request, 'El grupo ya existe.')
            return redirect('usuarios:lista_grupos')
    
    return render(request, 'usuarios/crear_grupo.html')

@login_required
@user_passes_test(is_admin)
def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(Group.objects.annotate(user_count=Count('user')), id=grupo_id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre and nombre != grupo.name:
            # Verificar si el nombre ya existe
            if Group.objects.filter(name=nombre).exclude(id=grupo.id).exists():
                messages.error(request, 'Ya existe un grupo con ese nombre.')
            else:
                grupo.name = nombre
                grupo.save()
                messages.success(request, 'Grupo actualizado exitosamente.')
                return redirect('usuarios:lista_grupos')
    
    context = {'grupo': grupo}
    return render(request, 'usuarios/editar_grupo.html', context)

@login_required
@user_passes_test(is_admin)
def eliminar_grupo(request, grupo_id):
    grupo = get_object_or_404(Group.objects.annotate(user_count=Count('user')), id=grupo_id)
    
    if request.method == 'POST':
        if grupo.user_count > 0:
            messages.error(request, 'No se puede eliminar un grupo que tiene usuarios asignados.')
        else:
            grupo.delete()
            messages.success(request, 'Grupo eliminado exitosamente.')
        return redirect('usuarios:lista_grupos')
    
    context = {'grupo': grupo}
    return render(request, 'usuarios/eliminar_grupo.html', context)

# API para asignar/desasignar usuarios a grupos
@login_required
@user_passes_test(is_admin)
@require_POST
def asignar_grupo(request):
    user_id = request.POST.get('user_id')
    grupo_id = request.POST.get('grupo_id')
    accion = request.POST.get('accion')  # 'agregar' o 'quitar'
    
    try:
        user = User.objects.get(id=user_id)
        grupo = Group.objects.get(id=grupo_id)
        
        if accion == 'agregar':
            user.groups.add(grupo)
            mensaje = f'Usuario {user.username} agregado al grupo {grupo.name}'
        elif accion == 'quitar':
            user.groups.remove(grupo)
            mensaje = f'Usuario {user.username} removido del grupo {grupo.name}'
        
        return JsonResponse({'success': True, 'message': mensaje})
    except (User.DoesNotExist, Group.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Usuario o grupo no encontrado'})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Coordinador').exists())
def dashboard_coordinador(request):
    """Dashboard específico para coordinadores"""
    # Obtener información básica del coordinador
    disciplinas_count = Disciplina.objects.filter(profesores=request.user).count()
    total_inscritos = Inscripcion.objects.filter(
        categoria__disciplina__profesores=request.user
    ).count()
    categorias_count = Categoria.objects.filter(
        disciplina__profesores=request.user
    ).count()
    
    # Inscripciones recientes (últimas 5)
    inscripciones_recientes = Inscripcion.objects.filter(
        categoria__disciplina__profesores=request.user
    ).select_related('socio__perfil_usuario__usuario', 'categoria__disciplina').order_by('-fecha_inscripcion')[:5]
    
    # Categorías con cupo disponible
    categorias_con_cupo = []
    categorias_coordinador = Categoria.objects.filter(
        disciplina__profesores=request.user
    ).select_related('disciplina')
    
    for categoria in categorias_coordinador:
        inscritos_actuales = Inscripcion.objects.filter(categoria=categoria).count()
        cupo_disponible = categoria.cupo_maximo - inscritos_actuales
        if cupo_disponible > 0:
            categorias_con_cupo.append({
                'categoria': categoria,
                'inscritos_actuales': inscritos_actuales,
                'cupo_disponible': cupo_disponible
            })
    
    # Verificar si el usuario también es socio
    es_socio = hasattr(request.user.perfil, 'socio')
    socio = None
    if es_socio:
        socio = request.user.perfil.socio
    
    context = {
        'disciplinas_count': disciplinas_count,
        'total_inscritos': total_inscritos,
        'categorias_count': categorias_count,
        'eventos_count': 0,  # Placeholder para futuras implementaciones
        'inscripciones_recientes': inscripciones_recientes,
        'categorias_con_cupo': categorias_con_cupo,
        'es_socio': es_socio,
        'socio': socio,
    }
    
    return render(request, 'usuarios/dash_coordinador.html', context)

@login_required
def mi_perfil(request):
    """Vista para que cualquier usuario autenticado pueda editar su propio perfil"""
    user = request.user
    
    if request.method == 'POST':
        user_form = MiUsuarioForm(request.POST, instance=user)
        perfil_form = MiPerfilUsuarioForm(request.POST, instance=user.perfil)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user = user_form.save()
            perfil_form.save()
            
            # Si se proporcionó una nueva contraseña, actualizarla
            password = user_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
                user.save()
                # Re-autenticar al usuario después de cambiar la contraseña
                login(request, user)
            
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            return redirect('usuarios:dashboard')
    else:
        user_form = MiUsuarioForm(instance=user)
        perfil_form = MiPerfilUsuarioForm(instance=user.perfil)
    
    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'usuario': user,
    }
    return render(request, 'usuarios/mi_perfil.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Tesoreria').exists())
def dashboard_tesorero(request):
    """Dashboard específico para tesoreros"""
    # Obtener estadísticas financieras
    total_socios = Socio.objects.filter(perfil_usuario__estado_socio='ACTIVO', perfil_usuario__usuario__is_active=True).count()
    deudas_pendientes = Deuda.objects.filter(estado__in=['PENDIENTE', 'VENCIDA']).count()
    
    # Calcular ingresos del mes actual
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ingresos_mes = Transaccion.objects.filter(
        tipo='INGRESO',
        fecha__gte=inicio_mes
    ).aggregate(total=Sum('monto'))['total'] or 0
    
    cuentas_activas = Cuenta.objects.filter(activa=True).count()
    
    # Deudas recientes (últimas 10)
    deudas_recientes = Deuda.objects.filter(
        estado__in=['PENDIENTE', 'VENCIDA']
    ).select_related('socio__perfil_usuario__usuario').order_by('-fecha_generacion')[:10]
    
    # Verificar si el usuario también es socio
    es_socio = hasattr(request.user.perfil, 'socio')
    socio = None
    if es_socio:
        socio = request.user.perfil.socio
    
    context = {
        'total_socios': total_socios,
        'deudas_pendientes': deudas_pendientes,
        'ingresos_mes': ingresos_mes,
        'cuentas_activas': cuentas_activas,
        'deudas_recientes': deudas_recientes,
        'es_socio': es_socio,
        'socio': socio,
    }
    
    return render(request, 'usuarios/dash_tesorero.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Comision').exists())
def dashboard_comision(request):
    """Dashboard específico para comisión"""
    # Obtener estadísticas generales
    total_socios = Socio.objects.filter(perfil_usuario__estado_socio='ACTIVO', perfil_usuario__usuario__is_active=True).count()
    disciplinas_activas = Disciplina.objects.filter(activa=True).count()
    deudas_pendientes = Deuda.objects.filter(estado__in=['PENDIENTE', 'VENCIDA']).count()
    
    # Calcular ingresos del mes actual
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ingresos_mes = Transaccion.objects.filter(
        tipo='INGRESO',
        fecha__gte=inicio_mes
    ).aggregate(total=Sum('monto'))['total'] or 0
    
    # Socios recientes (últimos 10)
    socios_recientes = Socio.objects.filter(
        perfil_usuario__estado_socio='ACTIVO',
        perfil_usuario__usuario__is_active=True
    ).select_related('perfil_usuario__usuario', 'tipo_socio').order_by('-fecha_afiliacion')[:10]
    
    # Verificar si el usuario también es socio
    es_socio = hasattr(request.user.perfil, 'socio')
    socio = None
    if es_socio:
        socio = request.user.perfil.socio
    
    context = {
        'total_socios': total_socios,
        'disciplinas_activas': disciplinas_activas,
        'deudas_pendientes': deudas_pendientes,
        'ingresos_mes': ingresos_mes,
        'socios_recientes': socios_recientes,
        'es_socio': es_socio,
        'socio': socio,
    }
    
    return render(request, 'usuarios/dash_comision.html', context)

def puede_ver_reportes(user):
    return user.is_authenticated and user.groups.filter(name__in=['Administrador', 'Tesoreria', 'Comision']).exists()

@login_required
@user_passes_test(puede_ver_reportes)
def reportes_view(request):
    return render(request, 'reportes.html')
