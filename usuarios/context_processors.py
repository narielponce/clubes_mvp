def user_role_context(request):
    """
    Context processor para determinar el rol principal del usuario
    y proporcionar el sidebar apropiado.
    """
    if request.user.is_authenticated:
        # Obtener todos los grupos del usuario
        user_groups = request.user.groups.all()
        
        # Determinar el rol principal (prioridad: Coordinador > Tesoreria > Comision > Administrador)
        if user_groups.filter(name='Coordinador').exists():
            user_role = 'Coordinador'
        elif user_groups.filter(name='Tesoreria').exists():
            user_role = 'Tesoreria'
        elif user_groups.filter(name='Comision').exists():
            user_role = 'Comision'
        elif user_groups.filter(name='Administrador').exists():
            user_role = 'Administrador'
        else:
            user_role = 'Default'
    else:
        user_role = 'Default'
    
    return {
        'user_role': user_role
    } 