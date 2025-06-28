from django.core.management.base import BaseCommand
from socios.models import Socio, TipoSocio
from usuarios.models import PerfilUsuario
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Debug: Verificar socios en la base de datos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DEBUG SOCIOS ==='))
        
        # Verificar tipos de socio
        tipos = TipoSocio.objects.all()
        self.stdout.write(f'Tipos de socio encontrados: {tipos.count()}')
        for tipo in tipos:
            self.stdout.write(f'  - {tipo.nombre}: {tipo.descripcion}')
        
        # Verificar usuarios
        usuarios = User.objects.all()
        self.stdout.write(f'Usuarios encontrados: {usuarios.count()}')
        for usuario in usuarios:
            self.stdout.write(f'  - {usuario.username}: {usuario.get_full_name()}')
        
        # Verificar perfiles de usuario
        perfiles = PerfilUsuario.objects.all()
        self.stdout.write(f'Perfiles de usuario encontrados: {perfiles.count()}')
        for perfil in perfiles:
            self.stdout.write(f'  - {perfil.usuario.username}: {perfil.usuario.get_full_name()} (activo: {perfil.esta_activo_sistema})')
        
        # Verificar socios
        socios = Socio.objects.all()
        self.stdout.write(f'Socios encontrados: {socios.count()}')
        for socio in socios:
            if socio.perfil_usuario:
                self.stdout.write(f'  - {socio.perfil_usuario.usuario.get_full_name()} ({socio.tipo_socio})')
            else:
                self.stdout.write(f'  - Socio sin perfil ({socio.tipo_socio})')
        
        # Verificar socios con queryset específico
        socios_queryset = Socio.objects.all()
        self.stdout.write(f'Queryset Socio.objects.all(): {socios_queryset.count()}')
        
        # Verificar si hay socios con perfil de usuario
        socios_con_perfil = Socio.objects.filter(perfil_usuario__isnull=False)
        self.stdout.write(f'Socios con perfil de usuario: {socios_con_perfil.count()}')
        
        # Verificar si hay socios sin perfil de usuario
        socios_sin_perfil = Socio.objects.filter(perfil_usuario__isnull=True)
        self.stdout.write(f'Socios sin perfil de usuario: {socios_sin_perfil.count()}')
        
        self.stdout.write(self.style.SUCCESS('=== FIN DEBUG ===')) 