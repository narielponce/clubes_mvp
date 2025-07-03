from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import Group
from .models import Disciplina, Categoria, Horario, Dia, Inscripcion
from .forms import DisciplinaForm, CategoriaForm, HorarioForm, DiaForm, InscripcionForm
from usuarios.decorators import is_admin, coordinador_required
from django.db import models
from socios.models import Socio

def is_admin_or_coordinador(user):
    """Verifica si el usuario es administrador o coordinador"""
    return user.groups.filter(name__in=['Administrador', 'Coordinador']).exists()

@login_required
@is_admin
def lista_disciplinas(request):
    disciplinas = Disciplina.objects.all()
    return render(request, 'disciplinas/lista_disciplinas.html', {'disciplinas': disciplinas})

@login_required
@is_admin
def detalle_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    categorias = Categoria.objects.filter(disciplina=disciplina)
    return render(request, 'disciplinas/disciplina_detalle.html', {
        'disciplina': disciplina,
        'categorias': categorias
    })

@login_required
@is_admin
def crear_disciplina(request):
    if request.method == 'POST':
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            disciplina = form.save()
            messages.success(request, 'Disciplina creada exitosamente.')
            return redirect('disciplinas:lista')
    else:
        form = DisciplinaForm()
    return render(request, 'disciplinas/form_disciplina.html', {'form': form})

@login_required
@is_admin
def editar_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    if request.method == 'POST':
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            disciplina = form.save()
            messages.success(request, 'Disciplina actualizada exitosamente.')
            return redirect('disciplinas:lista')
    else:
        form = DisciplinaForm(instance=disciplina)
    return render(request, 'disciplinas/form_disciplina.html', {'form': form})

@login_required
@is_admin
def eliminar_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    disciplina.activa = False
    disciplina.save()
    messages.success(request, 'Disciplina desactivada exitosamente.')
    return redirect('disciplinas:lista')

@login_required
@is_admin
def lista_categorias(request):
    categorias = Categoria.objects.select_related('disciplina').all()
    return render(request, 'disciplinas/lista_categorias.html', {'categorias': categorias})

@login_required
@is_admin
def crear_categoria(request):
    # Crear el grupo de profesores si no existe
    Group.objects.get_or_create(name='Profesor')
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('disciplinas:lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'disciplinas/form_categoria.html', {'form': form})

@login_required
@is_admin
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('disciplinas:lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'disciplinas/form_categoria.html', {'form': form})

@login_required
@is_admin
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    categoria.delete()
    messages.success(request, 'Categoría eliminada exitosamente.')
    return redirect('disciplinas:lista_categorias')

@login_required
def inscribirse_categoria(request, categoria_pk):
    categoria = get_object_or_404(Categoria, pk=categoria_pk)
    try:
        Inscripcion.objects.create(socio=request.user.perfil.socio, categoria=categoria)
        messages.success(request, 'Inscripción realizada exitosamente.')
    except ValueError as e:
        messages.error(request, str(e))
    except:
        messages.error(request, 'Error al realizar la inscripción.')
    return redirect('disciplinas:lista_categorias')

@login_required
def cancelar_inscripcion(request, inscripcion_pk):
    inscripcion = get_object_or_404(Inscripcion, pk=inscripcion_pk, socio=request.user.perfil.socio)
    inscripcion.activa = False
    inscripcion.save()
    messages.success(request, 'Inscripción cancelada exitosamente.')
    return redirect('disciplinas:lista_categorias')

@login_required
@user_passes_test(is_admin_or_coordinador)
def nueva_inscripcion(request):
    """
    Vista para que el coordinador pueda inscribir a un socio en una categoría
    """
    if request.method == 'POST':
        form = InscripcionForm(request.POST)
        if form.is_valid():
            inscripcion = form.save()
            messages.success(
                request, 
                f'Inscripción exitosa: {inscripcion.socio} en {inscripcion.categoria}'
            )
            return redirect('disciplinas:lista_inscripciones')
    else:
        form = InscripcionForm()
    
    return render(request, 'disciplinas/form_inscripcion.html', {
        'form': form,
        'title': 'Nueva Inscripción',
        'submit_text': 'Crear Inscripción'
    })

@login_required
@user_passes_test(is_admin_or_coordinador)
def lista_inscripciones(request):
    """
    Vista para listar todas las inscripciones activas
    """
    inscripciones = Inscripcion.objects.filter(activa=True).select_related(
        'socio__perfil_usuario__usuario',
        'categoria__disciplina'
    ).order_by('-fecha_inscripcion')
    
    return render(request, 'disciplinas/lista_inscripciones.html', {
        'inscripciones': inscripciones
    })

@login_required
@user_passes_test(is_admin_or_coordinador)
def cancelar_inscripcion_admin(request, inscripcion_pk):
    """
    Vista para que el coordinador pueda cancelar una inscripción
    """
    inscripcion = get_object_or_404(Inscripcion, pk=inscripcion_pk)
    if request.method == 'POST':
        inscripcion.activa = False
        inscripcion.save()
        messages.success(
            request, 
            f'Inscripción cancelada: {inscripcion.socio} en {inscripcion.categoria}'
        )
        return redirect('disciplinas:lista_inscripciones')
    
    return render(request, 'disciplinas/confirmar_cancelar_inscripcion.html', {
        'inscripcion': inscripcion
    })

@login_required
@coordinador_required
def lista_disciplinas_coordinador(request):
    user = request.user
    disciplinas = Disciplina.objects.filter(coordinador__usuario=user)
    # Convertir a lista para poder modificar los objetos
    disciplinas = list(disciplinas)
    for disciplina in disciplinas:
        categorias = list(disciplina.categorias.all())
        for cat in categorias:
            cat.cantidad_inscriptos = cat.inscritos.filter(activa=True).count()
        disciplina.categorias_list = categorias
    return render(request, 'disciplinas/lista_disciplinas_coordinador.html', {
        'disciplinas': disciplinas
    })

@login_required
@coordinador_required
def inscribir_socios(request, disciplina_pk):
    user = request.user
    disciplina = Disciplina.objects.get(pk=disciplina_pk, coordinador__usuario=user)
    categorias = disciplina.categorias.all()
    socios = Socio.objects.all()

    # Inscripciones activas agrupadas por categoría
    inscripciones_por_categoria = {}
    for cat in categorias:
        inscripciones_por_categoria[cat] = cat.inscritos.filter(activa=True).select_related('socio__perfil_usuario__usuario')

    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        socios_ids = request.POST.getlist('socios')
        if not categoria_id:
            messages.error(request, 'Debe seleccionar una categoría.')
        else:
            categoria = categorias.get(pk=categoria_id)
            for socio_id in socios_ids:
                socio = Socio.objects.get(pk=socio_id)
                Inscripcion.objects.get_or_create(socio=socio, categoria=categoria, activa=True)
            messages.success(request, 'Socios inscritos correctamente.')
            return redirect('disciplinas:lista_disciplinas_coordinador')

    return render(request, 'disciplinas/inscribir_socios.html', {
        'disciplina': disciplina,
        'categorias': categorias,
        'socios': socios,
        'inscripciones_por_categoria': inscripciones_por_categoria
    })

@login_required
@coordinador_required
def socios_inscriptos_categoria(request, categoria_pk):
    categoria = get_object_or_404(Categoria, pk=categoria_pk)
    inscripciones = Inscripcion.objects.filter(categoria=categoria, activa=True).select_related('socio__perfil_usuario__usuario')
    return render(request, 'disciplinas/socios_inscriptos_categoria.html', {
        'categoria': categoria,
        'inscripciones': inscripciones,
    })
