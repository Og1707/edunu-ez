# Cambios Implementados - Detalles de Respuestas en Webhook

## Resumen Rápido

✅ **ANTES**: Solo se enviaba `puntuacion` y `tiempo_empleado`  
✅ **AHORA**: Se envía toda la información de cada respuesta del estudiante

---

## Archivos Modificados

### 1. 🎮 Frontend: `ColorGame.js`
**Ubicación**: `edunuñez/visual_edu/src/components/ColorGame.js`

**Cambios**:
```javascript
// Se agregó un nuevo estado
const [respuestas, setRespuestas] = useState([]); // Guardar detalle de cada respuesta

// Cuando selecciona un color, se guarda:
setRespuestas([...respuestas, {
  numero_pregunta: round,
  color_mostrado: currentColor.name,
  hex_color: currentColor.hex,
  respuesta_estudiante: selectedOption.name,
  respuesta_correcta: currentColor.name,
  es_correcta: isCorrect,
  tiempo_respuesta: timeElapsed
}]);

// Al enviar resultados, se incluye respuestas_detalle
axios.post('/api/estudiante/actividades/completar/', {
  // ... datos anteriores
  respuestas_detalle: respuestas  // ← NUEVO
});
```

### 2. 🔧 Backend: `views.py`
**Ubicación**: `edunuñez/api/views.py` - función `completar_actividad_estudiante()`

**Cambios**:
```python
# Se recibe respuestas_detalle del frontend
respuestas_detalle = request.data.get('respuestas_detalle', [])  # ← NUEVO

# Se incluye en los datos del webhook
actividad_data = {
    # ... datos anteriores
    'respuestas_detalle': respuestas_detalle  # ← NUEVO
}
```

### 3. 📡 Webhook: `webhooks.py`
**Ubicación**: `edunuñez/api/webhooks.py` - función `enviar_resultado_actividad_a_n8n()`

**Cambios**:
```python
# El payload ahora incluye respuestas en resultados
'resultados': {
    'puntuacion': ...,
    'tiempo_empleado_minutos': ...,
    'fecha_entrega': ...,
    'estado': ...,
    'es_tardia': ...,
    'respuestas_detalle': actividad_completada_data.get('respuestas_detalle', [])  # ← NUEVO
}
```

---

## Flujo Completo

```
┌─────────────────────────────────────────────────────────────┐
│  ESTUDIANTE JUEGA COLOR GAME                                │
│  - Por cada color que aparece, selecciona la respuesta      │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (ColorGame.js) - GUARDA CADA RESPUESTA           │
│  {                                                          │
│    numero_pregunta: 1,                                      │
│    color_mostrado: "Rojo",                                  │
│    hex_color: "#FF6B6B",                                    │
│    respuesta_estudiante: "Rojo",                            │
│    respuesta_correcta: "Rojo",                              │
│    es_correcta: true,                                       │
│    tiempo_respuesta: 2                                      │
│  }                                                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼ (click en "Guardar Resultados")
┌─────────────────────────────────────────────────────────────┐
│  POST /api/estudiante/actividades/completar/               │
│  {                                                          │
│    user_id: 5,                                              │
│    actividad_id: 23,                                        │
│    puntuacion: 80,                                          │
│    tiempo_empleado: 1,                                      │
│    respuestas_detalle: [...]  ← NUEVO                      │
│  }                                                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND (views.py) - PROCESA Y PREPARA                    │
│  Crea objeto actividad_data con toda la información        │
│  incluyendo respuestas_detalle                             │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  WEBHOOK (webhooks.py) - CONSTRUYE PAYLOAD                 │
│  {                                                          │
│    "timestamp": "...",                                      │
│    "evento": "actividad_completada",                        │
│    "datos": {                                               │
│      "estudiante": {...},                                   │
│      "actividad": {...},                                    │
│      "curso": {...},                                        │
│      "resultados": {                                        │
│        "puntuacion": 80,                                    │
│        "tiempo_empleado_minutos": 1,                        │
│        "respuestas_detalle": [...]  ← NUEVO               │
│      }                                                      │
│    }                                                        │
│  }                                                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  POST a n8n: http://localhost:5678/webhook/...            │
│  ✅ n8n RECIBE INFORMACIÓN COMPLETA DE RESPUESTAS          │
└─────────────────────────────────────────────────────────────┘
```

---

## Estructura de Datos

### Array de Respuestas
```json
[
  {
    "numero_pregunta": 1,
    "color_mostrado": "Rojo",
    "hex_color": "#FF6B6B",
    "respuesta_estudiante": "Rojo",
    "respuesta_correcta": "Rojo",
    "es_correcta": true,
    "tiempo_respuesta": 2
  },
  {
    "numero_pregunta": 2,
    "color_mostrado": "Azul",
    "hex_color": "#4ECDC4",
    "respuesta_estudiante": "Verde",
    "respuesta_correcta": "Azul",
    "es_correcta": false,
    "tiempo_respuesta": 5
  }
]
```

---

## Cómo Usar en n8n

### Filtrar respuestas correctas
```javascript
// Contar cuántas fueron correctas
data.body.datos.resultados.respuestas_detalle.filter(r => r.es_correcta).length
// Resultado: 8
```

### Encontrar preguntas fallidas
```javascript
// Preguntas que respondió mal
data.body.datos.resultados.respuestas_detalle.filter(r => !r.es_correcta)
// Resultado: [{ numero_pregunta: 2, ... }]
```

### Estadísticas
```javascript
// Tiempo promedio por pregunta
const respuestas = data.body.datos.resultados.respuestas_detalle;
const tiempoPromedio = respuestas.reduce((a, b) => a + b.tiempo_respuesta, 0) / respuestas.length;
// Resultado: 2.75 segundos
```

### Crear feedback personalizado
```javascript
const fallidas = data.body.datos.resultados.respuestas_detalle.filter(r => !r.es_correcta);
if (fallidas.length > 0) {
  const feedback = `Tuviste dificultad con: ${fallidas.map(f => f.color_mostrado).join(', ')}`;
}
```

---

## Prueba de Funcionamiento

**1. Ingresa como Estudiante**
- Email: `estudiante1@example.com`
- Password: `estudiante123`

**2. Juega la actividad**
- Ve a "My Activities"
- Selecciona "Juego de Reconocimiento de Colores"
- Completa las 10 preguntas

**3. Revisa n8n**
- Abre http://localhost:5678
- Busca el webhook ejecutado
- Verifica que la sección `respuestas_detalle` esté llena

**4. En n8n podrás:**
- Ver cada respuesta individual
- Analizar patrones de error
- Generar reportes detallados
- Enviar retroalimentación personalizada

---

## Próximos Pasos Opcionales

Si quieres mejorar aún más, podrías:
1. Guardar las respuestas en la base de datos (tabla nueva)
2. Crear visualizaciones de errores comunes
3. Mostrar recomendaciones personalizadas al estudiante
4. Generar reportes para el profesor

---

**✅ Todo listo. Los datos completos ahora llegan a n8n.**
