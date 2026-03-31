# Webhook con Respuestas Detalladas - Juego de Colores

## Nuevo JSON que llega a n8n

Con los cambios realizados, ahora el webhook enviará **información detallada de cada respuesta** del estudiante, no solo la puntuación final.

### Estructura del nuevo JSON:

```json
{
  "headers": {
    "host": "localhost:5678",
    "user-agent": "EduNuñez-Django/1.0",
    "accept-encoding": "gzip, deflate",
    "accept": "*/*",
    "connection": "keep-alive",
    "content-type": "application/json"
  },
  "params": {},
  "query": {},
  "body": {
    "timestamp": "2025-11-25T12:45:23.195702",
    "evento": "actividad_completada",
    "datos": {
      "estudiante": {
        "id": 5,
        "nombre": "osman perez gomez",
        "email": "osman0717@gmail.com"
      },
      "actividad": {
        "id": 23,
        "titulo": "Juego de Reconocimiento de Colores",
        "tipo": "quiz_ciencias"
      },
      "curso": {
        "id": 3,
        "nombre": "Matematicas II"
      },
      "resultados": {
        "puntuacion": 80,
        "tiempo_empleado_minutos": 1,
        "fecha_entrega": "2025-11-25 17:45:23.179570+00:00",
        "estado": "completada",
        "es_tardia": false,
        "respuestas_detalle": [
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
          },
          {
            "numero_pregunta": 3,
            "color_mostrado": "Verde",
            "hex_color": "#95E1D3",
            "respuesta_estudiante": "Verde",
            "respuesta_correcta": "Verde",
            "es_correcta": true,
            "tiempo_respuesta": 3
          },
          {
            "numero_pregunta": 4,
            "color_mostrado": "Amarillo",
            "hex_color": "#FFE66D",
            "respuesta_estudiante": "Amarillo",
            "respuesta_correcta": "Amarillo",
            "es_correcta": true,
            "tiempo_respuesta": 4
          },
          {
            "numero_pregunta": 5,
            "color_mostrado": "Morado",
            "hex_color": "#A29BFE",
            "respuesta_estudiante": "Morado",
            "respuesta_correcta": "Morado",
            "es_correcta": true,
            "tiempo_respuesta": 2
          },
          {
            "numero_pregunta": 6,
            "color_mostrado": "Rosa",
            "hex_color": "#FD79A8",
            "respuesta_estudiante": "Rosa",
            "respuesta_correcta": "Rosa",
            "es_correcta": true,
            "tiempo_respuesta": 3
          },
          {
            "numero_pregunta": 7,
            "color_mostrado": "Naranja",
            "hex_color": "#FDCB6E",
            "respuesta_estudiante": "Naranja",
            "respuesta_correcta": "Naranja",
            "es_correcta": true,
            "tiempo_respuesta": 2
          },
          {
            "numero_pregunta": 8,
            "color_mostrado": "Cian",
            "hex_color": "#74B9FF",
            "respuesta_estudiante": "Cian",
            "respuesta_correcta": "Cian",
            "es_correcta": true,
            "tiempo_respuesta": 1
          }
        ]
      }
    },
    "webhookUrl": "http://localhost:5678/webhook/Alumnos_settings",
    "executionMode": "production"
  }
}
```

## Cambios Realizados

### 1. **Frontend (ColorGame.js)**
- ✅ Agregado estado `respuestas` para guardar cada respuesta
- ✅ Cuando el estudiante selecciona un color, se guarda:
  - `numero_pregunta`: Número de la pregunta (1-10)
  - `color_mostrado`: Nombre del color mostrado
  - `hex_color`: Código hexadecimal del color
  - `respuesta_estudiante`: Color seleccionado por el estudiante
  - `respuesta_correcta`: Color correcto
  - `es_correcta`: Boolean si fue correcto
  - `tiempo_respuesta`: Segundos transcurridos cuando respondió
- ✅ Se envía `respuestas_detalle` junto con la puntuación

### 2. **Backend (views.py)**
- ✅ `completar_actividad_estudiante()` ahora recibe `respuestas_detalle`
- ✅ Pasa el array completo al webhook

### 3. **Webhooks (webhooks.py)**
- ✅ El payload del webhook ahora incluye `respuestas_detalle` en `resultados`
- ✅ Cada respuesta está estructurada con toda la información

## Uso en n8n

En tu workflow de n8n, ahora puedes:

### Acceder a las respuestas individuales:
```javascript
// Acceder a la primera respuesta
data.body.datos.resultados.respuestas_detalle[0]

// Contar respuestas correctas
data.body.datos.resultados.respuestas_detalle.filter(r => r.es_correcta).length

// Calcular tiempo promedio por pregunta
const tiempos = data.body.datos.resultados.respuestas_detalle.map(r => r.tiempo_respuesta);
const promedio = tiempos.reduce((a, b) => a + b, 0) / tiempos.length;

// Obtener preguntas fallidas
const fallidas = data.body.datos.resultados.respuestas_detalle.filter(r => !r.es_correcta);
```

### Posibles análisis en n8n:
1. **Identificar patrones de error**: ¿Qué colores confunde el estudiante?
2. **Análisis de tiempo**: ¿Qué preguntas le toman más tiempo?
3. **Retroalimentación personalizada**: Enviar mensajes según sus errores
4. **Estadísticas detalladas**: Crear reportes con gráficos

## Ejemplo de Procesamiento en n8n

```json
{
  "estudiante": "osman perez gomez",
  "puntuacion": 80,
  "aciertos": 8,
  "errores": 2,
  "preguntas_fallidas": [
    {
      "numero": 2,
      "respondio": "Verde",
      "era": "Azul"
    }
  ],
  "tiempo_promedio_por_pregunta": 2.75,
  "tiempo_total": 60
}
```

## Testing

Para probar con curl:

```bash
curl -X POST http://localhost:5678/webhook/Alumnos_settings \
  -H "Content-Type: application/json" \
  -d @payload.json
```

Donde `payload.json` contiene el JSON del cuerpo (body) mostrado arriba.

## Conclusión

Ahora tienes **acceso completo** a:
- ✅ Cada respuesta individual del estudiante
- ✅ Si fue correcta o incorrecta
- ✅ Qué respondió vs. qué era lo correcto
- ✅ Código hexadecimal para referencias visuales
- ✅ Tiempo de respuesta para análisis de velocidad

Esto permite crear análisis mucho más profundos en n8n.
