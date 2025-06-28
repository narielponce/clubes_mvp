from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
from socios.models import Socio, TipoSocio
from finanzas.models import Cuenta, Deuda, ItemDeuda, Transaccion
from disciplinas.models import Disciplina, Categoria
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Prueba el escenario de pago de deudas para identificar el problema'

    def handle(self, *args, **options):
        self.stdout.write('Creando escenario de prueba para deudas...')
        
        # Crear tipo de socio si no existe
        tipo_activo, _ = TipoSocio.objects.get_or_create(nombre='ACTIVO')
        
        # Crear usuario de prueba
        user, created = User.objects.get_or_create(
            username='socio_test',
            defaults={
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'email': 'juan@test.com'
            }
        )
        if created:
            user.set_password('123456')
            user.save()
            
            # Crear perfil de usuario
            perfil = PerfilUsuario.objects.create(
                usuario=user,
                esta_activo_sistema=True
            )
            
            # Crear socio
            socio = Socio.objects.create(
                perfil_usuario=perfil,
                tipo_socio=tipo_activo,
                fecha_afiliacion=timezone.now().date()
            )
        else:
            socio = user.perfil.socio
        
        # Crear cuentas
        cuenta_banco, _ = Cuenta.objects.get_or_create(
            nombre='Banco Principal',
            defaults={
                'tipo': 'BANCO',
                'saldo_actual': 0,
                'descripcion': 'Cuenta bancaria principal'
            }
        )
        
        cuenta_efectivo, _ = Cuenta.objects.get_or_create(
            nombre='Caja',
            defaults={
                'tipo': 'EFECTIVO',
                'saldo_actual': 0,
                'descripcion': 'Caja de efectivo'
            }
        )
        
        # Crear deuda de 45000
        deuda = Deuda.objects.create(
            socio=socio,
            fecha_vencimiento=date.today() + timedelta(days=30),
            monto_total=45000,
            estado='PENDIENTE',
            generada_por=User.objects.first()
        )
        
        # Crear item de deuda
        ItemDeuda.objects.create(
            deuda=deuda,
            tipo='CUOTA_SOCIETARIA',
            descripcion='Cuota societaria mensual',
            monto=45000
        )
        
        self.stdout.write(f'Deuda creada: {deuda} - Estado: {deuda.estado}')
        
        # Simular pago del 05/07 de 30000
        transaccion1 = Transaccion.objects.create(
            cuenta=cuenta_banco,
            tipo='INGRESO',
            categoria='CUOTAS',
            monto=30000,
            descripcion='Pago a cuenta de cuota societaria',
            fecha=date(2024, 7, 5),
            registrado_por=User.objects.first(),
            deuda_relacionada=deuda
        )
        
        self.stdout.write(f'Transacción 1 creada: {transaccion1}')
        
        # Simular pago del 09/07 de 15000
        transaccion2 = Transaccion.objects.create(
            cuenta=cuenta_efectivo,
            tipo='INGRESO',
            categoria='CUOTAS',
            monto=15000,
            descripcion='Pago final de cuota societaria',
            fecha=date(2024, 7, 9),
            registrado_por=User.objects.first(),
            deuda_relacionada=deuda
        )
        
        self.stdout.write(f'Transacción 2 creada: {transaccion2}')
        
        # Verificar estado actual de la deuda
        deuda.refresh_from_db()
        self.stdout.write(f'Estado final de la deuda: {deuda.estado}')
        
        # Calcular total pagado
        total_pagado = sum(t.monto for t in Transaccion.objects.filter(
            deuda_relacionada=deuda,
            tipo='INGRESO',
            categoria='CUOTAS'
        ))
        
        self.stdout.write(f'Total pagado: ${total_pagado}')
        self.stdout.write(f'Monto de la deuda: ${deuda.monto_total}')
        
        if total_pagado >= deuda.monto_total:
            self.stdout.write(
                self.style.WARNING(
                    'PROBLEMA IDENTIFICADO: La deuda debería estar PAGADA pero sigue PENDIENTE'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    'El sistema está funcionando correctamente'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nEscenario de prueba creado:\n'
                f'- Socio: {socio}\n'
                f'- Deuda: ${deuda.monto_total} (Estado: {deuda.estado})\n'
                f'- Total pagado: ${total_pagado}\n'
                f'- Transacciones: {Transaccion.objects.filter(deuda_relacionada=deuda).count()}'
            )
        ) 