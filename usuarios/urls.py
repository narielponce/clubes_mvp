from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('dash-coordinador/', views.dash_coordinador, name='dash_coordinador'),
    
    # Gestión de usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    
    # Gestión de grupos
    path('grupos/', views.lista_grupos, name='lista_grupos'),
    path('grupos/crear/', views.crear_grupo, name='crear_grupo'),
    path('grupos/<int:grupo_id>/editar/', views.editar_grupo, name='editar_grupo'),
    path('grupos/<int:grupo_id>/eliminar/', views.eliminar_grupo, name='eliminar_grupo'),
    
    # API para asignar grupos
    path('api/asignar-grupo/', views.asignar_grupo, name='asignar_grupo'),
]
