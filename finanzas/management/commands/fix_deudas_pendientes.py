from django.core.management.base import BaseCommand
from finanzas.models import Deuda, Transaccion
from django.db import transaction

class Command(BaseCommand):
    help = 'Corrige el estado de deudas que deberían estar marcadas como pagadas'

    def handle(self, *args, **options):
        self.stdout.write('Verificando y corrigiendo estados de deudas...')
        
        deudas_pendientes = Deuda.objects.filter(estado='PENDIENTE')
        deudas_corregidas = 0
        
        for deuda in deudas_pendientes:
            total_pagado = deuda.calcular_total_pagado()
            
            if total_pagado >= deuda.monto_total:
                self.stdout.write(
                    f'Deuda {deuda.id}: ${deuda.monto_total} - Pagado: ${total_pagado} - '
                    f'Estado actual: {deuda.estado}'
                )
                
                with transaction.atomic():
                    deuda.estado = 'PAGADA'
                    deuda.save()
                    deudas_corregidas += 1
                    
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Corregida a PAGADA'
                    )
                )
            else:
                self.stdout.write(
                    f'Deuda {deuda.id}: ${deuda.monto_total} - Pagado: ${total_pagado} - '
                    f'Mantiene estado: {deuda.estado}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nProceso completado:\n'
                f'- Deudas verificadas: {deudas_pendientes.count()}\n'
                f'- Deudas corregidas: {deudas_corregidas}'
            )
        ) 