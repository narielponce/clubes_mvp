from django.core.management.base import BaseCommand
from disciplinas.models import Horario, Dia

class Command(BaseCommand):
    help = 'Crea horarios de ejemplo'

    def handle(self, *args, **options):
        # Crear días si no existen
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        for dia in dias:
            Dia.objects.get_or_create(nombre=dia)

        # Crear horarios de ejemplo
        horarios = [
            {'dias': ['Lunes', 'Miércoles', 'Viernes'], 'hora_inicio': '16:00', 'hora_fin': '17:00'},
            {'dias': ['Martes', 'Jueves'], 'hora_inicio': '17:00', 'hora_fin': '18:00'},
            {'dias': ['Lunes', 'Miércoles', 'Viernes'], 'hora_inicio': '17:00', 'hora_fin': '18:00'},
            {'dias': ['Martes', 'Jueves'], 'hora_inicio': '18:00', 'hora_fin': '19:00'},
        ]

        for horario_data in horarios:
            horario = Horario.objects.create(
                hora_inicio=horario_data['hora_inicio'],
                hora_fin=horario_data['hora_fin']
            )
            dias_obj = Dia.objects.filter(nombre__in=horario_data['dias'])
            horario.dias.set(dias_obj)

        self.stdout.write(self.style.SUCCESS('Horarios creados exitosamente'))
