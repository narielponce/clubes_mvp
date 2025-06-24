from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from usuarios.decorators import verificar_rol
from usuarios.models import PerfilUsuario
from .models import Socio, TipoSocio
from .forms import SocioForm

@login_required
def lista_socios(request):
    socios = Socio.objects.select_related('perfil_usuario', 'tipo_socio').all()
    return render(request, 'socios/lista_socios.html', {'socios': socios})

@login_required
def nuevo_socio(request):
    tipos_socio = TipoSocio.objects.all()
    if request.method == 'POST':
        form = SocioForm(request.POST)
        if form.is_valid():
            socio = form.save(commit=False)
            # Asociar con el usuario actual
            socio.usuario = request.user
            socio.save()
            messages.success(request, 'Socio creado exitosamente.')
            return redirect('socios:lista_socios')
    else:
        form = SocioForm()
    return render(request, 'socios/form_socio.html', {
        'form': form,
        'titulo': 'Nuevo Socio',
        'tipos_socio': tipos_socio
    })

@login_required
def editar_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == 'POST':
        form = SocioForm(request.POST, instance=socio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Socio actualizado exitosamente.')
            return redirect('socios:lista_socios')
    else:
        form = SocioForm(instance=socio)
    return render(request, 'socios/form_socio.html', {'form': form, 'titulo': 'Editar Socio'})

@login_required
def eliminar_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == 'POST':
        socio.delete()
        messages.success(request, 'Socio eliminado exitosamente.')
        return redirect('socios:lista_socios')
    return render(request, 'socios/confirmar_eliminar.html', {'socio': socio})

@login_required
def detalles_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    return render(request, 'socios/detalles_socio.html', {'socio': socio})

@verificar_rol('socio')
@login_required
def area_socio(request):
    """Muestra el área específica para socios"""
    # Obtener el socio del usuario actual
    socio = request.user.perfil.socio
    
    # Obtener información relevante del socio
    context = {
        'socio': socio,
        'nombre_completo': request.user.get_full_name(),
        'tipo_socio': socio.tipo_socio.get_nombre_display(),
        'fecha_afiliacion': socio.fecha_afiliacion,
        'tiempo_socio': socio.tiempo_socio,
        'esta_activo': socio.esta_activo
    }
    
    return render(request, 'socios/area_socio.html', context)
