from django.http import HttpResponseForbidden
from functools import wraps

def verificar_rol(rol_requerido):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Verificar si el usuario tiene el rol requerido
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Debes estar logueado")
            
            # Obtener el perfil del usuario
            try:
                perfil = request.user.perfil
            except:
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
