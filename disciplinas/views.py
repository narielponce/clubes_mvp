from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Disciplina, Categoria, Profesor, Horario, Dia, Inscripcion
from .forms import DisciplinaForm, CategoriaForm, ProfesorForm, HorarioForm, DiaForm
from usuarios.decorators import is_admin
from django.db import models

@login_required
@is_admin
def lista_disciplinas(request):
    disciplinas = Disciplina.objects.all()
    return render(request, 'disciplinas/lista_disciplinas.html', {'disciplinas': disciplinas})

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
@is_admin
def lista_profesores(request):
    profesores = Profesor.objects.select_related('perfil_usuario').all()
    return render(request, 'disciplinas/lista_profesores.html', {'profesores': profesores})

@login_required
@is_admin
def crear_profesor(request):
    if request.method == 'POST':
        form = ProfesorForm(request.POST)
        if form.is_valid():
            profesor = form.save()
            messages.success(request, 'Profesor creado exitosamente.')
            return redirect('disciplinas:lista_profesores')
    else:
        form = ProfesorForm()
    return render(request, 'disciplinas/form_profesor.html', {'form': form})

@login_required
@is_admin
def editar_profesor(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    if request.method == 'POST':
        form = ProfesorForm(request.POST, instance=profesor)
        if form.is_valid():
            profesor = form.save()
            messages.success(request, 'Profesor actualizado exitosamente.')
            return redirect('disciplinas:lista_profesores')
    else:
        form = ProfesorForm(instance=profesor)
    return render(request, 'disciplinas/form_profesor.html', {'form': form})

@login_required
@is_admin
def eliminar_profesor(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    profesor.delete()
    messages.success(request, 'Profesor eliminado exitosamente.')
    return redirect('disciplinas:lista_profesores')

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
