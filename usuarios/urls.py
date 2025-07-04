from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # URLs de autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard principal
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Dashboards específicos por rol
    path('dashboard/coordinador/', views.dashboard_coordinador, name='dashboard_coordinador'),
    path('dashboard/tesorero/', views.dashboard_tesorero, name='dashboard_tesorero'),
    path('dashboard/comision/', views.dashboard_comision, name='dashboard_comision'),
    
    # Perfil de usuario
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    
    # Gestión de usuarios (solo admin)
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    
    # Gestión de grupos (solo admin)
    path('grupos/', views.lista_grupos, name='lista_grupos'),
    path('grupos/crear/', views.crear_grupo, name='crear_grupo'),
    path('grupos/<int:pk>/editar/', views.editar_grupo, name='editar_grupo'),
    path('grupos/<int:pk>/eliminar/', views.eliminar_grupo, name='eliminar_grupo'),
    

]
