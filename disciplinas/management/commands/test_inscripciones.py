from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from socios.models import Socio, TipoSocio
from disciplinas.models import Disciplina, Categoria, Horario, Dia, Inscripcion
from django.utils import timezone

class Command(BaseCommand):
    help = 'Crea datos de prueba para el sistema de inscripciones'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de prueba para inscripciones...')
        
        # Crear días de la semana
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        for nombre_dia in dias:
            Dia.objects.get_or_create(nombre=nombre_dia)
        
        # Crear horarios
        horario_manana = Horario.objects.create(
            hora_inicio='08:00',
            hora_fin='10:00'
        )
        horario_manana.dias.add(Dia.objects.get(nombre='Lunes'), Dia.objects.get(nombre='Miércoles'))
        
        horario_tarde = Horario.objects.create(
            hora_inicio='16:00',
            hora_fin='18:00'
        )
        horario_tarde.dias.add(Dia.objects.get(nombre='Martes'), Dia.objects.get(nombre='Jueves'))
        
        # Crear tipo de socio si no existe
        tipo_activo, _ = TipoSocio.objects.get_or_create(nombre='ACTIVO')
        
        # Crear usuarios de prueba
        usuarios_prueba = [
            {'username': 'coordinador1', 'first_name': 'Juan', 'last_name': 'Pérez', 'email': 'juan@test.com'},
            {'username': 'socio1', 'first_name': 'María', 'last_name': 'García', 'email': 'maria@test.com'},
            {'username': 'socio2', 'first_name': 'Carlos', 'last_name': 'López', 'email': 'carlos@test.com'},
            {'username': 'socio3', 'first_name': 'Ana', 'last_name': 'Martínez', 'email': 'ana@test.com'},
        ]
        
        for user_data in usuarios_prueba:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password('123456')
                user.save()
                
                # Crear perfil de usuario
                perfil = PerfilUsuario.objects.create(
                    usuario=user,
                    esta_activo_sistema=True
                )
                
                # Crear socio (excepto para el coordinador)
                if user_data['username'] != 'coordinador1':
                    Socio.objects.create(
                        perfil_usuario=perfil,
                        tipo_socio=tipo_activo,
                        fecha_afiliacion=timezone.now().date()
                    )
        
        # Crear disciplina
        coordinador = PerfilUsuario.objects.get(usuario__username='coordinador1')
        disciplina = Disciplina.objects.create(
            nombre='Fútbol',
            descripcion='Disciplina de fútbol para todas las edades',
            coordinador=coordinador,
            lugar='Cancha Principal',
            costo_mensual=50.00,
            activa=True
        )
        
        # Crear categorías
        categoria_principiantes = Categoria.objects.create(
            disciplina=disciplina,
            nombre='Principiantes',
            horario=horario_manana,
            cupo_maximo=20,
            especialidad='Nivel básico'
        )
        
        categoria_avanzados = Categoria.objects.create(
            disciplina=disciplina,
            nombre='Avanzados',
            horario=horario_tarde,
            cupo_maximo=15,
            especialidad='Nivel intermedio-avanzado'
        )
        
        # Crear algunas inscripciones de prueba
        socios = Socio.objects.all()
        if socios.exists():
            # Inscribir al primer socio en ambas categorías
            socio1 = socios.first()
            Inscripcion.objects.get_or_create(
                socio=socio1,
                categoria=categoria_principiantes
            )
            
            # Inscribir al segundo socio en categoría avanzados
            if socios.count() > 1:
                socio2 = socios[1]
                Inscripcion.objects.get_or_create(
                    socio=socio2,
                    categoria=categoria_avanzados
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Datos de prueba creados exitosamente:\n'
                f'- {Disciplina.objects.count()} disciplina(s)\n'
                f'- {Categoria.objects.count()} categoría(s)\n'
                f'- {Socio.objects.count()} socio(s)\n'
                f'- {Inscripcion.objects.count()} inscripción(es)\n'
                f'\nCredenciales de prueba:\n'
                f'- Coordinador: coordinador1 / 123456\n'
                f'- Socio: socio1 / 123456'
            )
        ) 