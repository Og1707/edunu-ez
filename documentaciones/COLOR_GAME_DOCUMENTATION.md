# 🎨 Juego de Reconocimiento de Colores - Documentación

## Descripción General

El juego de reconocimiento de colores es una actividad educativa interactiva integrada en la plataforma EduNúñez. Los estudiantes deben identificar correctamente los nombres de los colores que se muestran en la pantalla.

## Características Principales

### 1. **Cronómetro Progresivo** ⏱️
- El cronómetro comienza cuando el estudiante inicia el juego
- Muestra el tiempo en formato MM:SS (minutos:segundos)
- Registra el tiempo total de la sesión
- Calcula el tiempo promedio por acierto

### 2. **Sistema de Puntuación** 🎯
- Total de 10 rondas por juego
- 1 punto por respuesta correcta
- La puntuación se expresa como porcentaje (0-100%)
- Se registra el número exacto de aciertos

### 3. **Retroalimentación en Tiempo Real** 📊
- Feedback visual inmediato después de cada respuesta
- Indicación clara si la respuesta fue correcta ✅ o incorrecta ❌
- Muestra el color correcto si la respuesta fue incorrecta
- Pausa de 2 segundos antes de pasar al siguiente color

### 4. **Estadísticas Detalladas** 📈
- Aciertos / Total de preguntas (ej: 8/10)
- Porcentaje de precisión
- Tiempo total empleado
- Tiempo promedio por acierto

### 5. **Colores Disponibles** 🌈
El juego incluye 8 colores diferentes:
1. **Rojo** - #FF6B6B
2. **Azul** - #4ECDC4
3. **Verde** - #95E1D3
4. **Amarillo** - #FFE66D
5. **Morado** - #A29BFE
6. **Rosa** - #FD79A8
7. **Naranja** - #FDCB6E
8. **Cian** - #74B9FF

## Flujo de Juego

### 1. **Pantalla Inicial**
- Explicación clara del objetivo del juego
- Instrucciones de cómo jugar
- Información sobre la dificultad
- Botón "Comenzar Juego"

### 2. **Pantalla de Juego**
- Barra de progreso que muestra rondas completadas
- Estadísticas en tiempo real:
  - Ronda actual / Total de rondas
  - Aciertos acumulados
  - Cronómetro en ejecución
- Área de visualización del color
- 4 opciones de colores para seleccionar
- Retroalimentación inmediata

### 3. **Pantalla de Resultados**
- Resumen de desempeño con iconos visuales
- Tarjetas con:
  - Número de aciertos (8/10)
  - Porcentaje de precisión
  - Tiempo total
  - Tiempo promedio por acierto
- Mensaje personalizado según el desempeño:
  - 100%: "¡Excelente! ¡Identificaste todos los colores correctamente!"
  - 80-99%: "¡Muy bien! Tienes una excelente precisión."
  - 60-79%: "Buen trabajo. Puedes mejorar practicando más."
  - <60%: "Necesitas practicar más. ¡Inténtalo de nuevo!"
- Opciones:
  - Guardar resultados
  - Jugar de nuevo
  - Cerrar

## Integración con StudentActivities

### Cómo se activa el juego

El juego de reconocimiento de colores se activa automáticamente cuando:

1. La actividad tiene tipo `'quiz_ciencias'` 
2. La descripción o título de la actividad contiene la palabra "juego"

### Flujo de Usuario

1. Estudiante abre sus actividades
2. Selecciona una actividad de tipo quiz o juego
3. El modal muestra un botón "▶️ Jugar Reconocimiento de Colores"
4. Al hacer clic, el juego se inicia en modalidad pantalla completa dentro del modal
5. Al completar el juego y guardar, los resultados se envían al servidor
6. El modal se cierra y se muestra un mensaje de éxito

## Componentes Implicados

### 1. **ColorGame.js** 🎮
- Componente principal del juego
- Maneja toda la lógica del juego
- Estados: inicio, en progreso, finalización
- Calcula puntuaciones y tiempos

### 2. **StudentActivities.js** 📚
- Integra el componente ColorGame
- Maneja la apertura/cierre del modal de juego
- Envía resultados al backend
- Actualiza estadísticas después del juego

### 3. **ColorGame.css** 🎨
- Estilos visuales del juego
- Animaciones y transiciones
- Responsividad para diferentes dispositivos
- Gradientes y efectos visuales

### 4. **Backend - views.py** ⚙️
- Endpoint `completar_actividad_estudiante`
- Guarda puntuación y tiempo empleado
- Actualiza estado de la asignación

## Propiedades del Componente ColorGame

```javascript
<ColorGame 
  user={user}                    // Objeto usuario con usuario_id
  actividad={actividad}          // Objeto actividad con id
  onComplete={handleComplete}    // Callback al completar
  onClose={handleClose}          // Callback al cerrar
/>
```

### Props

- **user** (object, requerido): Usuario actual con `usuario_id`
- **actividad** (object, requerido): Actividad actual con `id`
- **onComplete** (function, opcional): Se ejecuta al guardar resultados
  - Retorna objeto con: `{ puntuacion, tiempoEmpleado, aciertos }`
- **onClose** (function, opcional): Se ejecuta al cerrar el juego

## Cálculos de Puntuación

```javascript
// Puntuación final (en porcentaje)
puntuacion = (aciertos / 10) * 100

// Tiempo promedio por acierto
tiempoPromedio = tiempoTotal / aciertos

// Tiempo total en minutos (para guardar)
tiempoEmpleado = Math.round(tiempoTotal / 60)
```

## Datos Enviados al Backend

Al completar el juego y guardar:

```javascript
{
  "user_id": 123,              // ID del estudiante
  "actividad_id": 456,         // ID de la actividad
  "puntuacion": 80,            // Porcentaje (0-100)
  "tiempo_empleado": 3         // En minutos (redondeado)
}
```

## Respuesta del Endpoint

```javascript
{
  "mensaje": "Actividad completada exitosamente",
  "progreso": {
    "completada": true,
    "fecha_completado": "2025-11-25T10:30:00Z",
    "puntuacion": 80,
    "tiempo_empleado": 3,
    "es_tardia": false,
    "estado": "completada"
  }
}
```

## Personalización del Juego

### Cambiar el número de rondas
En `ColorGame.js`, línea ~34:
```javascript
const MAX_ROUNDS = 10; // Cambiar a un número diferente
```

### Agregar más colores
En `ColorGame.js`, línea ~40:
```javascript
const COLORS = [
  { name: 'Nuevo Color', hex: '#XXXXXX', rgb: 'rgb(r, g, b)' },
  // ... más colores
];
```

### Cambiar el número de opciones
En `ColorGame.js`, línea ~93:
```javascript
const shuffledColors = COLORS.sort(() => Math.random() - 0.5).slice(0, 4);
// Cambiar el número 4 por el deseado
```

## Responsive Design

El juego está optimizado para:
- 📱 Dispositivos móviles (480px y más)
- 📱 Tablets (768px y más)
- 💻 Pantallas de escritorio (1024px y más)

El diseño se adapta automáticamente:
- La cuadrícula de colores cambia a una columna en móviles
- El tamaño de la esfera de color se reduce en dispositivos pequeños
- Los botones se ajustan al tamaño de la pantalla

## Animaciones Incluidas

1. **slideIn**: Entrada suave del contenido
2. **fadeIn**: Desvanecimiento de entrada para resultados
3. **slideInDown**: Entrada del color desde arriba
4. **slideInUp**: Entrada de mensajes desde abajo
5. **pulse**: Pulso para respuestas correctas
6. **shake**: Temblor para respuestas incorrectas

## Versión del Juego

- **Versión**: 1.0.0
- **Fecha de creación**: 25 de Noviembre de 2025
- **Tipos de actividad compatibles**: quiz_ciencias, actividades con tipo 'juego'
- **Navegadores soportados**: Chrome, Firefox, Safari, Edge (versiones recientes)

## Notas de Desarrollo

- El cronómetro se reinicia si el usuario cierra y abre el juego nuevamente
- Los resultados se guardan automáticamente al completar el juego
- El juego no permite pausar durante la ejecución
- No hay límite de tiempo para responder cada pregunta
- El juego se puede reintentar múltiples veces por actividad

## Troubleshooting

### El juego no aparece
- Verificar que `actividad.tipo === 'quiz_ciencias'`
- Verificar que el servidor esté corriendo en `http://127.0.0.1:8000`
- Verificar que `user.usuario_id` esté definido

### El tiempo no se registra correctamente
- Verificar que el navegador soporta `Date.now()`
- Revisar la consola del navegador para errores

### Las puntuaciones no se guardan
- Verificar que el endpoint `/api/estudiante/actividades/completar/` esté funcionando
- Revisar los logs del servidor Django

## Contacto y Soporte

Para reportar bugs o sugerencias sobre el juego, contactar al equipo de desarrollo de EduNúñez.
