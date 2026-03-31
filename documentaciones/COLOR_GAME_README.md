# 🎨 Juego de Reconocimiento de Colores - Guía Rápida

## ¿Qué es?

Un juego interactivo educativo donde los estudiantes deben identificar correctamente los colores mostrados en la pantalla. Incluye cronómetro automático, puntuación, y retroalimentación en tiempo real.

## 🚀 Inicio Rápido (3 pasos)

### Paso 1: Crear actividad de prueba

```bash
cd edunuñez_django
cd edunuñez
python manage.py shell
>>> exec(open('create_color_game_activity.py').read())
```

Este script:
- ✅ Crea profesor de prueba
- ✅ Crea curso de prueba
- ✅ Crea estudiantes de prueba
- ✅ Crea actividad del juego
- ✅ Asigna actividad a estudiantes

### Paso 2: Iniciar servidores

**Terminal 1 - Django:**
```bash
cd edunuñez_django
python manage.py runserver
```

**Terminal 2 - React:**
```bash
cd edunuñez_django/visual_edu
npm start
```

### Paso 3: Jugar

1. Ve a http://localhost:3000
2. Inicia sesión como estudiante (usa datos del script)
3. Ve a "Mis Actividades"
4. Selecciona "Juego de Reconocimiento de Colores"
5. Haz clic en "▶️ Jugar Reconocimiento de Colores"
6. ¡Comienza a jugar! 🎮

---

## 📋 Archivos Nuevos

```
ColorGame.js              ← Componente principal del juego
ColorGame.css             ← Estilos del juego
create_color_game_activity.py  ← Script para crear actividad de prueba
```

## 📝 Archivos Modificados

```
StudentActivities.js      ← Integración del juego
StudentActivities.css     ← Estilos adicionales
```

---

## 🎮 Características del Juego

| Característica | Detalles |
|---|---|
| **Rondas** | 10 preguntas |
| **Colores** | 8 colores diferentes |
| **Opciones** | 4 opciones por ronda |
| **Cronómetro** | Registra tiempo total |
| **Puntuación** | Basada en aciertos (0-100%) |
| **Retroalimentación** | Inmediata después de cada respuesta |

---

## 📊 Datos que se Guardan

Después de completar el juego:

```json
{
  "puntuacion": 80,          // Porcentaje (0-100)
  "tiempo_empleado": 3,      // En minutos
  "aciertos": 8,             // Número de respuestas correctas
  "fecha_completado": "2025-11-25T10:30:00Z"
}
```

---

## 🎨 Pantallas

### 1. Introducción
- Explicación del juego
- Instrucciones
- Botón para comenzar

### 2. Juego
- Color mostrado en la pantalla
- 4 opciones para seleccionar
- Cronómetro visible
- Retroalimentación después de cada respuesta

### 3. Resultados
- Aciertos / Total
- Porcentaje de precisión
- Tiempo total
- Tiempo promedio por acierto
- Opciones para guardar o reintentar

---

## 🔧 Personalización

### Cambiar número de rondas
`ColorGame.js` línea 34:
```javascript
const MAX_ROUNDS = 10;  // Cambiar a otro número
```

### Cambiar número de opciones
`ColorGame.js` línea 93:
```javascript
const shuffledColors = COLORS.sort(...).slice(0, 4);  // Cambiar 4
```

### Agregar más colores
`ColorGame.js` línea 40:
```javascript
const COLORS = [
  { name: 'Nuevo Color', hex: '#XXXXXX', rgb: 'rgb(r, g, b)' },
  // ...
];
```

---

## 📚 Documentación Completa

- 📖 `COLOR_GAME_DOCUMENTATION.md` - Documentación técnica detallada
- 🧪 `TESTING_GUIDE.md` - Guía de pruebas
- 📄 `RESUMEN_JUEGO.md` - Resumen visual del proyecto

---

## 🐛 Troubleshooting

### ¿El juego no aparece?
- Verifica que el tipo de actividad sea `'quiz_ciencias'`
- Recarga la página (F5)
- Abre la consola (F12) para ver errores

### ¿No se guardan los resultados?
- Verifica que Django esté corriendo
- Revisa http://127.0.0.1:8000/api/estudiante/actividades/completar/
- Mira la consola del navegador (F12)

### ¿El cronómetro no funciona?
- Recarga la aplicación
- Verifica que `Date.now()` funcione en tu navegador
- Comprueba que JavaScript esté habilitado

---

## 📱 Compatibilidad

✅ Chrome
✅ Firefox
✅ Safari
✅ Edge
✅ Móvil (iOS/Android)
✅ Tablet

---

## 📊 Estructura de Datos

### Actividad
```javascript
{
  id: 1,
  titulo: "Juego de Reconocimiento de Colores",
  tipo: "quiz_ciencias",
  descripcion: "...",
  curso: 1,
  fecha_limite: "2025-12-25"
}
```

### Resultado del Juego
```javascript
{
  user_id: 1,
  actividad_id: 1,
  puntuacion: 80,        // Porcentaje
  tiempo_empleado: 3     // Minutos
}
```

---

## 🎯 Casos de Uso

### Profesor
- Crea actividad de tipo "quiz_ciencias"
- Asigna a un curso
- Los estudiantes pueden jugar

### Estudiante
- Accede a actividades asignadas
- Juega el juego de colores
- Recibe puntuación inmediata
- Ve sus resultados guardados

---

## 📈 Próximas Mejoras

1. **Niveles de dificultad**
   - Fácil: 6 colores, 5 opciones
   - Medio: 8 colores, 4 opciones
   - Difícil: 10 colores, 3 opciones

2. **Más juegos**
   - Juego de formas
   - Juego de números
   - Juego de memoria

3. **Tabla de puntuaciones**
   - Top 10 por precisión
   - Comparación de tiempos

4. **Sonidos**
   - Sonido al acertar
   - Sonido al fallar

5. **Leaderboard**
   - Puntuaciones globales
   - Logros

---

## 🔐 Seguridad

- ✅ Validación en backend
- ✅ Verificación de permisos
- ✅ Datos encriptados en tránsito
- ✅ No hay acceso sin autenticación

---

## 📞 Ayuda

1. Lee la documentación en `COLOR_GAME_DOCUMENTATION.md`
2. Consulta la guía de pruebas en `TESTING_GUIDE.md`
3. Ejecuta el script de prueba: `python manage.py shell < create_color_game_activity.py`
4. Abre la consola del navegador (F12) para ver logs

---

## ✨ Lo que Incluye

```
✅ Componente React completamente funcional
✅ Estilos modernos y responsivos
✅ Cronómetro progresivo automático
✅ Sistema de puntuación inteligente
✅ Retroalimentación visual inmediata
✅ Integración con backend Django
✅ Guardado automático de resultados
✅ Documentación completa
✅ Script de prueba automatizado
✅ Guía de testing detallada
```

---

## 🚀 Versión

- **Versión**: 1.0.0
- **Fecha**: 25 de Noviembre, 2025
- **Estado**: Listo para producción

---

## 👨‍💻 Autor

Creado para la plataforma EduNúñez
Sistema de Gestión de Actividades Educativas

---

**¡Listo para usar! 🎮✨**

Para comenzar, sigue los 3 pasos en "Inicio Rápido"
