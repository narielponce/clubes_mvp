# Caso de Uso: Nueva Inscripción a una Disciplina

## Descripción
Este caso de uso permite a los coordinadores inscribir a socios en categorías específicas de disciplinas deportivas.

## Funcionalidades Implementadas

### 1. Formulario de Nueva Inscripción
- **URL**: `/disciplinas/inscripciones/nueva/`
- **Acceso**: Solo coordinadores y administradores
- **Funcionalidad**: Permite seleccionar un socio y una categoría para crear una nueva inscripción

### 2. Lista de Inscripciones
- **URL**: `/disciplinas/inscripciones/`
- **Acceso**: Solo coordinadores y administradores
- **Funcionalidad**: Muestra todas las inscripciones activas con opciones de gestión

### 3. Cancelación de Inscripciones
- **URL**: `/disciplinas/inscripciones/cancelar/<id>/`
- **Acceso**: Solo coordinadores y administradores
- **Funcionalidad**: Permite cancelar inscripciones activas

## Validaciones Implementadas

### En el Formulario
1. **Socio único por categoría**: No se puede inscribir al mismo socio en la misma categoría más de una vez
2. **Cupo disponible**: Verifica que la categoría no haya alcanzado su cupo máximo
3. **Socio activo**: Solo permite inscribir socios que estén activos en el sistema
4. **Categoría activa**: Solo permite inscribir en categorías de disciplinas activas

### En el Modelo
1. **Unique constraint**: Previene duplicados a nivel de base de datos
2. **Validación de cupo**: Se ejecuta en el método `save()` del modelo

## Flujo de Trabajo

### Para Crear una Nueva Inscripción:
1. El coordinador accede al dashboard
2. Hace clic en "Nueva Inscripción"
3. Selecciona un socio de la lista desplegable
4. Selecciona una categoría de la lista desplegable
5. Hace clic en "Crear Inscripción"
6. El sistema valida los datos y crea la inscripción
7. Redirige a la lista de inscripciones con mensaje de éxito

### Para Ver Inscripciones:
1. El coordinador accede al dashboard
2. Hace clic en "Ver Inscripciones"
3. Ve una tabla con todas las inscripciones activas
4. Puede ver detalles como socio, disciplina, categoría, fecha y estado

### Para Cancelar una Inscripción:
1. Desde la lista de inscripciones, hace clic en el botón de cancelar
2. Se muestra una página de confirmación
3. Confirma la cancelación
4. La inscripción se marca como inactiva

## Archivos Creados/Modificados

### Modelos
- `disciplinas/models.py`: Modelo `Inscripcion` ya existía, se mejoró con validaciones

### Formularios
- `disciplinas/forms.py`: Nuevo `InscripcionForm` con validaciones personalizadas

### Vistas
- `disciplinas/views.py`: Nuevas vistas:
  - `nueva_inscripcion()`
  - `lista_inscripciones()`
  - `cancelar_inscripcion_admin()`

### URLs
- `disciplinas/urls.py`: Nuevas rutas para gestión de inscripciones

### Templates
- `disciplinas/templates/disciplinas/form_inscripcion.html`: Formulario de inscripción
- `disciplinas/templates/disciplinas/lista_inscripciones.html`: Lista de inscripciones
- `disciplinas/templates/disciplinas/confirmar_cancelar_inscripcion.html`: Confirmación de cancelación

### Dashboard
- `usuarios/templates/usuarios/dash_coordinador.html`: Botones actualizados

### Comandos de Gestión
- `disciplinas/management/commands/test_inscripciones.py`: Datos de prueba

## Datos de Prueba

Para probar la funcionalidad, ejecuta:
```bash
python manage.py test_inscripciones
```

Esto creará:
- Usuarios de prueba (coordinador1, socio1, socio2, socio3)
- Una disciplina de fútbol con dos categorías
- Algunas inscripciones de ejemplo

**Credenciales de prueba:**
- Coordinador: `coordinador1` / `123456`
- Socio: `socio1` / `123456`

## Consideraciones Técnicas

### Seguridad
- Todas las vistas requieren autenticación
- Solo coordinadores y administradores pueden acceder
- Validaciones tanto en frontend como backend

### Rendimiento
- Uso de `select_related()` para optimizar consultas
- Filtrado de datos activos para reducir carga

### Usabilidad
- Interfaz intuitiva con Bulma CSS
- Mensajes de error claros y específicos
- Confirmaciones para acciones destructivas

## Próximas Mejoras Sugeridas

1. **Filtros avanzados**: Por disciplina, categoría, fecha, etc.
2. **Exportación**: Generar reportes en PDF/Excel
3. **Notificaciones**: Email automático al socio cuando se inscribe
4. **Historial**: Mantener registro de todas las inscripciones (activas e inactivas)
5. **Búsqueda**: Buscar socios por nombre o número de socio
6. **Inscripción masiva**: Inscribir múltiples socios a la vez 