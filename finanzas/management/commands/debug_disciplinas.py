from django.core.management.base import BaseCommand
from disciplinas.models import Disciplina, Categoria, Inscripcion
from socios.models import Socio

class Command(BaseCommand):
    help = 'Debug de disciplinas e inscripciones'

    def handle(self, *args, **options):
        self.stdout.write('=== DEBUG DISCIPLINAS ===')
        
        # Disciplinas
        disciplinas = Disciplina.objects.all()
        self.stdout.write(f'Disciplinas encontradas: {disciplinas.count()}')
        for disciplina in disciplinas:
            self.stdout.write(f'  - {disciplina.nombre}: ${disciplina.costo_mensual}')
        
        # Categorías
        categorias = Categoria.objects.all()
        self.stdout.write(f'\nCategorías encontradas: {categorias.count()}')
        for categoria in categorias:
            self.stdout.write(f'  - {categoria.disciplina.nombre} - {categoria.nombre}')
        
        # Inscripciones
        inscripciones = Inscripcion.objects.all()
        self.stdout.write(f'\nInscripciones encontradas: {inscripciones.count()}')
        for inscripcion in inscripciones:
            socio_nombre = inscripcion.socio.perfil_usuario.usuario.get_full_name()
            disciplina_nombre = inscripcion.categoria.disciplina.nombre
            categoria_nombre = inscripcion.categoria.nombre
            activa = "Activa" if inscripcion.activa else "Inactiva"
            self.stdout.write(f'  - {socio_nombre} en {disciplina_nombre} - {categoria_nombre} ({activa})')
        
        # Socios con inscripciones activas
        socios_con_inscripciones = Socio.objects.filter(
            inscripciones__activa=True
        ).distinct()
        
        self.stdout.write(f'\nSocios con inscripciones activas: {socios_con_inscripciones.count()}')
        for socio in socios_con_inscripciones:
            socio_nombre = socio.perfil_usuario.usuario.get_full_name()
            inscripciones_activas = socio.inscripciones.filter(activa=True)
            disciplinas = []
            for inscripcion in inscripciones_activas:
                disciplinas.append(inscripcion.categoria.disciplina.nombre)
            self.stdout.write(f'  - {socio_nombre}: {", ".join(disciplinas)}')
        
        self.stdout.write('=== FIN DEBUG ===') 