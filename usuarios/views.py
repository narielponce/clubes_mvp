from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'usuarios/login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if request.user.groups.filter(name='Administrador').exists():
        return render(request, 'usuarios/dash_admin.html', {'rol': 'Administrador'})
    elif request.user.groups.filter(name='Coordinador').exists():
        return render(request, 'usuarios/dash_coordinador.html', {'rol': 'Coordinador'})
    elif request.user.groups.filter(name='Profesor').exists():
        return render(request, 'usuarios/dash_profesor.html', {'rol': 'Profesor'})
    elif request.user.groups.filter(name='Tesoreria').exists():
        return render(request, 'usuarios/dash_tesorero.html', {'rol': 'Tesoreria'})
    elif request.user.groups.filter(name='Comision').exists():
        return render(request, 'usuarios/dash_comision.html', {'rol': 'Comision'})
    else:
        rol = 'Sin Rol Asignado'
    return render(request, 'usuarios/dashboard.html', {'rol': rol})
