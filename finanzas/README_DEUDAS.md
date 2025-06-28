# Problema y Solución: Estado de Deudas

## Problema Identificado

**Escenario:** Un socio tiene una deuda de $45,000. El día 05/07 realiza un pago de $30,000 a cuenta en una cuenta bancaria y el día 09/07 cancela el saldo de $15,000 pagando en efectivo.

**Problema:** A pesar de que el socio pagó completamente la deuda ($30,000 + $15,000 = $45,000), la deuda seguía figurando como "Pendiente" en el sistema.

## Causa Raíz

El sistema no estaba actualizando automáticamente el estado de las deudas cuando se registraban transacciones de pago. La lógica para verificar si una deuda estaba completamente pagada no se ejecutaba al momento de registrar las transacciones.

## Solución Implementada

### 1. Nuevos Métodos en el Modelo Deuda

Se agregaron dos métodos al modelo `Deuda`:

#### `calcular_total_pagado()`
```python
def calcular_total_pagado(self):
    """Calcula el total pagado sumando todas las transacciones relacionadas"""
    return sum(
        transaccion.monto 
        for transaccion in self.transacciones.filter(tipo='INGRESO', categoria='CUOTAS')
    )
```

#### `verificar_y_actualizar_estado()`
```python
def verificar_y_actualizar_estado(self):
    """Verifica si la deuda está pagada y actualiza su estado"""
    total_pagado = self.calcular_total_pagado()
    
    if total_pagado >= self.monto_total:
        if self.estado != 'PAGADA':
            self.estado = 'PAGADA'
            self.save()
            return True
    else:
        # Verificar si está vencida
        if self.fecha_vencimiento < timezone.now().date() and self.estado == 'PENDIENTE':
            self.estado = 'VENCIDA'
            self.save()
            return True
    
    return False
```

### 2. Actualización Automática en Transacciones

Se modificó el método `save()` del modelo `Transaccion` para que automáticamente actualice el estado de la deuda:

```python
def save(self, *args, **kwargs):
    # ... lógica existente para actualizar saldo de cuenta ...
    
    super().save(*args, **kwargs)
    
    # Actualizar estado de la deuda si está relacionada
    if self.deuda_relacionada and self.tipo == 'INGRESO' and self.categoria == 'CUOTAS':
        self.deuda_relacionada.verificar_y_actualizar_estado()
```

## Comandos de Gestión

### 1. `test_deudas`
Crea un escenario de prueba para verificar el funcionamiento:
```bash
python manage.py test_deudas
```

### 2. `fix_deudas_pendientes`
Corrige deudas existentes que deberían estar marcadas como pagadas:
```bash
python manage.py fix_deudas_pendientes
```

## Flujo de Trabajo Corregido

### Antes (Problemático):
1. Se crea una deuda de $45,000 (Estado: PENDIENTE)
2. Se registra transacción de $30,000 (Deuda sigue PENDIENTE)
3. Se registra transacción de $15,000 (Deuda sigue PENDIENTE)
4. **Problema:** El estado no se actualiza automáticamente

### Después (Corregido):
1. Se crea una deuda de $45,000 (Estado: PENDIENTE)
2. Se registra transacción de $30,000 (Deuda sigue PENDIENTE - pago parcial)
3. Se registra transacción de $15,000 (Deuda se actualiza automáticamente a PAGADA)
4. **Solución:** El estado se actualiza automáticamente al completar el pago

## Validaciones Implementadas

### Verificación de Pago Completo
- Se suma el total de todas las transacciones de tipo "INGRESO" y categoría "CUOTAS"
- Si el total pagado >= monto de la deuda, se marca como "PAGADA"

### Verificación de Vencimiento
- Si la fecha de vencimiento ya pasó y la deuda está "PENDIENTE", se marca como "VENCIDA"

### Transacciones Válidas
- Solo se consideran transacciones de tipo "INGRESO" y categoría "CUOTAS"
- Se verifica que la transacción esté relacionada con una deuda específica

## Beneficios de la Solución

1. **Actualización Automática:** El estado de las deudas se actualiza automáticamente
2. **Consistencia de Datos:** Evita inconsistencias entre pagos y estados de deudas
3. **Trazabilidad:** Mantiene el historial completo de transacciones
4. **Flexibilidad:** Permite pagos parciales y múltiples transacciones
5. **Corrección Retroactiva:** Comando para corregir deudas existentes

## Casos de Uso Soportados

- ✅ Pago completo en una sola transacción
- ✅ Pago parcial con múltiples transacciones
- ✅ Pagos en diferentes cuentas (efectivo, banco, etc.)
- ✅ Actualización automática de estado
- ✅ Verificación de vencimiento
- ✅ Corrección de deudas existentes

## Próximas Mejoras Sugeridas

1. **Notificaciones:** Enviar notificaciones cuando una deuda se marca como pagada
2. **Reportes:** Generar reportes de deudas pagadas por período
3. **Auditoría:** Mantener log de cambios de estado
4. **Interfaz:** Mostrar progreso de pago en la interfaz de usuario
5. **Validaciones:** Validar que no se registren pagos mayores al monto de la deuda 