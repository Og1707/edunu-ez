# Diagrama de Flujo: Respuestas Detalladas en Webhook

## 🎮 Antes vs Después

### ❌ ANTES (Solo puntuación)
```
Estudiante juega
    ↓
Completa 10 preguntas
    ↓
Sistema guarda: puntuacion=80, tiempo=1min
    ↓
Webhook a n8n:
{
  "puntuacion": 80,
  "tiempo_empleado": 1
}
    ↓
n8n: "¿Cómo fue en cada pregunta? No sé..."
```

### ✅ AHORA (Respuestas detalladas)
```
Estudiante juega
    ↓
Por CADA pregunta:
  • Color mostrado: Rojo
  • Respuesta: Rojo ✅
  • Tiempo: 2 segundos
    ↓
Por CADA pregunta:
  • Color mostrado: Azul
  • Respuesta: Verde ❌
  • Tiempo: 5 segundos
    ↓
... (8 preguntas totales)
    ↓
Webhook a n8n:
{
  "puntuacion": 80,
  "tiempo_empleado": 1,
  "respuestas_detalle": [
    {
      "numero_pregunta": 1,
      "color_mostrado": "Rojo",
      "respuesta_estudiante": "Rojo",
      "es_correcta": true,
      "tiempo_respuesta": 2
    },
    {
      "numero_pregunta": 2,
      "color_mostrado": "Azul",
      "respuesta_estudiante": "Verde",
      "es_correcta": false,
      "tiempo_respuesta": 5
    },
    ...
  ]
}
    ↓
n8n: "¡Puedo ver que confunde Azul con Verde! 
       Voy a enviar recursos sobre esos colores
       y notificar al profesor de la dificultad"
```

---

## 📊 Estructura de Datos Completa

### En el Frontend (ColorGame.js)
```
Estado: respuestas = [
  {
    numero_pregunta: 1,
    color_mostrado: "Rojo",
    hex_color: "#FF6B6B",
    respuesta_estudiante: "Rojo",
    respuesta_correcta: "Rojo",
    es_correcta: true,
    tiempo_respuesta: 2
  },
  {
    numero_pregunta: 2,
    color_mostrado: "Azul",
    hex_color: "#4ECDC4",
    respuesta_estudiante: "Verde",
    respuesta_correcta: "Azul",
    es_correcta: false,
    tiempo_respuesta: 5
  },
  // ... 8 más
]
```

### Enviado al Backend
```
POST /api/estudiante/actividades/completar/
{
  "user_id": 5,
  "actividad_id": 23,
  "puntuacion": 80,
  "tiempo_empleado": 1,
  "respuestas_detalle": [ ... ]  ← NUEVO
}
```

### En el Webhook a n8n
```
POST http://localhost:5678/webhook/Alumnos_settings
{
  "timestamp": "2025-11-25T12:45:23",
  "evento": "actividad_completada",
  "datos": {
    "estudiante": {...},
    "actividad": {...},
    "curso": {...},
    "resultados": {
      "puntuacion": 80,
      "tiempo_empleado_minutos": 1,
      "respuestas_detalle": [...]  ← AQUI LLEGA
    }
  }
}
```

---

## 🔄 Flujo Completo del Sistema

```
┌────────────────────────────────────────────────────────────────┐
│ 1. ESTUDIANTE INICIA SESION Y VE ACTIVIDAD ASIGNADA           │
│    [StudentActivities.js]                                      │
│    - Ve "Juego de Reconocimiento de Colores"                  │
│    - Hace clic en "Jugar"                                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│ 2. INICIO DEL JUEGO                                            │
│    [ColorGame.js - startGame()]                                │
│    - Inicializa: respuestas = [], score = 0                   │
│    - Muestra primer color                                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│ 3. RESPONDE A PREGUNTA 1                                       │
│    [ColorGame.js - handleColorSelect()]                        │
│    - Usuario selecciona "Rojo"                                 │
│    - Sistema verifica: correcto ✅                             │
│    - Guarda:                                                   │
│      {                                                         │
│        numero_pregunta: 1,                                     │
│        color_mostrado: "Rojo",                                 │
│        respuesta_estudiante: "Rojo",                           │
│        es_correcta: true,                                      │
│        tiempo_respuesta: 2                                     │
│      }                                                         │
│    - score = 1                                                 │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼ (Loop 10 veces)
┌────────────────────────────────────────────────────────────────┐
│ 4. RESPONDE PREGUNTAS 2-10 (igual que 3)                      │
│    - Cada respuesta se guarda en array                         │
│    - Se actualiza score                                        │
│    - respuestas.length = 10                                    │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│ 5. FINALIZACION DEL JUEGO                                      │
│    [ColorGame.js - finishGame()]                               │
│    - score = 8 (8 correctas)                                   │
│    - puntuacion = 80%                                          │
│    - timeElapsed = 60 segundos                                 │
│    - Muestra pantalla de resultados                            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│ 6. GUARDAR RESULTADOS (CLICK EN BOTON)                        │
│    [ColorGame.js - saveResults()]                              │
│    POST /api/estudiante/actividades/completar/                │
│    {                                                           │
│      "user_id": 5,                                             │
│      "actividad_id": 23,                                       │
│      "puntuacion": 80,                                         │
│      "tiempo_empleado": 1,                                     │
│      "respuestas_detalle": [...]  ← ENVIA TODAS LAS RESPUESTAS│
│    }                                                           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│ 7. BACKEND PROCESA                                             │
│    [views.py - completar_actividad_estudiante()]              │
│    - Recibe respuestas_detalle                                │
│    - Valida estudiante y actividad                             │
│    - Marca como completada                                     │
│    - Crea objeto actividad_data CON respuestas_detalle        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│ 8. PREPARA WEBHOOK                                             │
│    [webhooks.py - enviar_resultado_actividad_a_n8n()]         │
│    Construye JSON:                                             │
│    {                                                           │
│      "timestamp": "2025-11-25T12:45:23",                       │
│      "evento": "actividad_completada",                         │
│      "datos": {                                                │
│        "estudiante": { "id": 5, "nombre": "Osman", ... },     │
│        "actividad": { "id": 23, "titulo": "Colores", ... },   │
│        "curso": { "id": 3, "nombre": "Mat II", ... },         │
│        "resultados": {                                         │
│          "puntuacion": 80,                                     │
│          "tiempo_empleado_minutos": 1,                        │
│          "respuestas_detalle": [                              │
│            {                                                   │
│              "numero_pregunta": 1,                             │
│              "color_mostrado": "Rojo",                         │
│              "respuesta_estudiante": "Rojo",                   │
│              "es_correcta": true,                              │
│              ...                                               │
│            },                                                  │
│            ... (9 más)                                         │
│          ]                                                     │
│        }                                                       │
│      }                                                         │
│    }                                                           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│ 9. ENVIO A n8n                                                 │
│    POST http://localhost:5678/webhook/Alumnos_settings        │
│    Content-Type: application/json                              │
│    [JSON completo con respuestas_detalle]                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│ 10. n8n RECIBE Y PROCESA                                       │
│     ✅ Tiene todas las respuestas                              │
│     ✅ Puede analizar patrones de error                        │
│     ✅ Puede generar retroalimentación                         │
│     ✅ Puede crear reportes                                    │
│     ✅ Puede enviar notificaciones                             │
│     ✅ Puede guardar en base de datos                          │
└────────────────────────────────────────────────────────────────┘
```

---

## 💡 Ejemplos de Análisis en n8n

### 1. Identificar patrones de error
```javascript
// ¿Qué colores confunde?
const coloresConfundidos = {};
data.body.datos.resultados.respuestas_detalle
  .filter(r => !r.es_correcta)
  .forEach(r => {
    const key = `${r.color_mostrado} vs ${r.respuesta_estudiante}`;
    coloresConfundidos[key] = (coloresConfundidos[key] || 0) + 1;
  });
// Resultado: {"Azul vs Verde": 1, ...}
```

### 2. Generar retroalimentación
```javascript
const fallidas = data.body.datos.resultados.respuestas_detalle
  .filter(r => !r.es_correcta)
  .map(r => r.color_mostrado);

if (fallidas.length > 0) {
  const feedback = `Vimos que tuviste dificultad identificando: ${fallidas.join(', ')}. 
    Te recomendamos practicar con estos colores nuevamente.`;
}
```

### 3. Análisis de velocidad
```javascript
// ¿Qué preguntas tardó más?
const respuestas = data.body.datos.resultados.respuestas_detalle;
const masLentas = respuestas
  .sort((a, b) => b.tiempo_respuesta - a.tiempo_respuesta)
  .slice(0, 3);
// Las 3 preguntas donde tardó más
```

### 4. Generar reporte
```javascript
const total = data.body.datos.resultados.respuestas_detalle.length;
const correctas = data.body.datos.resultados.respuestas_detalle
  .filter(r => r.es_correcta).length;
const tiempo_promedio = data.body.datos.resultados.respuestas_detalle
  .map(r => r.tiempo_respuesta)
  .reduce((a, b) => a + b) / total;

const reporte = {
  estudiante: data.body.datos.estudiante.nombre,
  puntuacion: data.body.datos.resultados.puntuacion,
  aciertos: correctas + "/" + total,
  tiempo_promedio_por_pregunta: tiempo_promedio + " segundos",
  generado: new Date().toISOString()
};
```

---

## ✅ Checklist de Verificación

- [x] Frontend captura respuestas individuales
- [x] Backend recibe respuestas_detalle
- [x] Webhook incluye respuestas en JSON
- [x] n8n recibe el JSON completo
- [x] Respuestas están correctamente estructuradas
- [x] Se incluye: número, colores, respuesta, si fue correcta, tiempo
- [x] Documentación completa

---

## 🚀 Estado: ✅ LISTO

Ahora puedes:
1. Jugar la actividad
2. Ver todas las respuestas en n8n
3. Hacer análisis profundos
4. Generar reportes personalizados
5. Enviar retroalimentación específica

**¡Todo funciona! 🎉**
