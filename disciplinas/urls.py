from django.urls import path
from . import views

app_name = 'disciplinas'

urlpatterns = [
    # Disciplinas
    path('disciplinas/', views.lista_disciplinas, name='lista'),
    path('disciplinas/nueva/', views.crear_disciplina, name='nueva_disciplina'),
    path('disciplinas/editar/<int:pk>/', views.editar_disciplina, name='editar_disciplina'),
    path('disciplinas/eliminar/<int:pk>/', views.eliminar_disciplina, name='eliminar_disciplina'),
    
    # Categorías
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/nueva/', views.crear_categoria, name='nueva_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # Profesores
    path('profesores/', views.lista_profesores, name='lista_profesores'),
    path('profesores/nuevo/', views.crear_profesor, name='nuevo_profesor'),
    path('profesores/editar/<int:pk>/', views.editar_profesor, name='editar_profesor'),
    path('profesores/eliminar/<int:pk>/', views.eliminar_profesor, name='eliminar_profesor'),
    
    # Inscripciones
    path('inscribirse/<int:categoria_pk>/', views.inscribirse_categoria, name='inscribirse_categoria'),
    path('cancelar-inscripcion/<int:inscripcion_pk>/', views.cancelar_inscripcion, name='cancelar_inscripcion'),
]
