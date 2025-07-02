from django.urls import path
from . import views

app_name = 'disciplinas'

urlpatterns = [
    # Disciplinas
    path('disciplinas/', views.lista_disciplinas, name='lista'),
    path('disciplinas/detalle/<int:pk>/', views.detalle_disciplina, name='detalle_disciplina'),
    path('disciplinas/nueva/', views.crear_disciplina, name='nueva_disciplina'),
    path('disciplinas/editar/<int:pk>/', views.editar_disciplina, name='editar_disciplina'),
    path('disciplinas/eliminar/<int:pk>/', views.eliminar_disciplina, name='eliminar_disciplina'),
    
    # Categorías
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/nueva/', views.crear_categoria, name='nueva_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # Inscripciones (para coordinadores)
    path('inscripciones/', views.lista_inscripciones, name='lista_inscripciones'),
    path('inscripciones/nueva/', views.nueva_inscripcion, name='nueva_inscripcion'),
    path('inscripciones/cancelar/<int:inscripcion_pk>/', views.cancelar_inscripcion_admin, name='cancelar_inscripcion_admin'),
    
    # Inscripciones (para usuarios)
    path('inscribirse/<int:categoria_pk>/', views.inscribirse_categoria, name='inscribirse_categoria'),
    path('cancelar-inscripcion/<int:inscripcion_pk>/', views.cancelar_inscripcion, name='cancelar_inscripcion'),
    path('mis-disciplinas/', views.lista_disciplinas_coordinador, name='lista_disciplinas_coordinador'),
    path('<int:disciplina_pk>/inscribir-socios/', views.inscribir_socios, name='inscribir_socios'),
]
