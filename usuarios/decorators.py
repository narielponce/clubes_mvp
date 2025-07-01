from django.http import HttpResponseForbidden
from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from .models import PerfilUsuario

def verificar_rol(rol_requerido):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Debes estar logueado")
            
            # Obtener el perfil del usuario
            try:
                perfil = request.user.perfil
            except PerfilUsuario.DoesNotExist:
                return HttpResponseForbidden("Usuario sin perfil")
            
            # Verificar roles específicos
            if rol_requerido == 'socio':
                if not hasattr(perfil, 'socio'):
                    return HttpResponseForbidden("No tienes acceso a esta área")
            elif rol_requerido == 'tesorero':
                if not perfil.is_tesorero:
                    return HttpResponseForbidden("No tienes acceso a esta área")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def is_admin(user):
    # Verificar si el usuario está autenticado
    if not user.is_authenticated:
        return False
    
    # Verificar si pertenece al grupo Administrador
    return user.groups.filter(name='Administrador').exists()

def is_tesorero(user):
    # Verificar si el usuario está autenticado
    if not user.is_authenticated:
        return False
    
    # Verificar si pertenece al grupo Tesoreria
    return user.groups.filter(name='Tesoreria').exists()

def is_coordinador(user):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='Coordinador').exists()

# Convertir las funciones en decoradores de Django
is_admin = user_passes_test(is_admin)
tesorero_required = user_passes_test(is_tesorero)
coordinador_required = user_passes_test(is_coordinador)
