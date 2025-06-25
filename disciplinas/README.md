# Sistema de Gestión de Disciplinas del Club

Este módulo permite gestionar las disciplinas deportivas del club, sus categorías y profesores.

## Funcionalidades Principales

### Gestión de Disciplinas
- Crear nuevas disciplinas deportivas
- Asignar coordinador a cada disciplina
- Establecer cupo máximo y costo mensual
- Definir lugar de práctica

### Gestión de Categorías
- Crear categorías dentro de cada disciplina (ej: Sub 14, Sub 16, etc.)
- Asignar múltiples profesores por categoría
- Definir horarios de práctica
- Establecer cupo máximo por categoría

### Gestión de Profesores
- Registrar profesores del club
- Asignar especialidades
- Asignar profesores a categorías

### Sistema de Inscripciones
- Permitir a los socios inscribirse en categorías
- Verificar disponibilidad de cupos
- Cancelar inscripciones
- Ver lista de inscritos por categoría

## Requisitos de Acceso

- Solo administradores pueden gestionar disciplinas, categorías y profesores
- Los socios pueden inscribirse en categorías disponibles
- Se verifica el cupo disponible antes de permitir inscripciones

## URLs Principales

- `/disciplinas/` - Lista de disciplinas
- `/disciplinas/nueva/` - Crear nueva disciplina
- `/categorias/` - Lista de categorías
- `/categorias/nueva/` - Crear nueva categoría
- `/profesores/` - Lista de profesores
- `/profesores/nuevo/` - Registrar nuevo profesor

## Modelos de Datos

- `Disciplina`: Información básica de la disciplina deportiva
- `Categoria`: Subdivisión de la disciplina con sus propias características
- `Profesor`: Información de los profesores del club
- `Horario`: Definición de los horarios de práctica
- `Dia`: Días de la semana para los horarios
- `Inscripcion`: Registro de inscripciones de socios a categorías
