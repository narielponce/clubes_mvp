from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Crea el grupo de Profesores'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Profesores')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo Profesores creado exitosamente'))
        else:
            self.stdout.write(self.style.WARNING('El grupo Profesores ya existía'))
