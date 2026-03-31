# Integración Webhook con n8n

## 📋 Descripción General

El sistema EduNuñez ahora envía automáticamente los resultados de las actividades completadas por los estudiantes a un webhook de n8n para procesamiento adicional.

**Webhook URL**: `http://localhost:5678/webhook/Alumnos_settings`
**Método**: `POST`
**Contenido**: `application/json`

---

## 📊 Estructura de Datos Enviados

Cuando un estudiante completa una actividad, se envía un JSON con la siguiente estructura:

```json
{
  "timestamp": "2025-11-25T15:30:45.123456",
  "evento": "actividad_completada",
  "datos": {
    "estudiante": {
      "id": 1,
      "nombre": "Juan Pérez López",
      "email": "juan@example.com"
    },
    "actividad": {
      "id": 5,
      "titulo": "Reconocimiento de Colores",
      "tipo": "quiz_ciencias"
    },
    "curso": {
      "id": 2,
      "nombre": "Ciencias Naturales 5°"
    },
    "resultados": {
      "puntuacion": 85,
      "tiempo_empleado_minutos": 8,
      "fecha_entrega": "2025-11-25T15:30:45.654321",
      "estado": "completada",
      "es_tardia": false
    }
  }
}
```

---

## 🔑 Campos Principales

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `timestamp` | ISO DateTime | Marca de tiempo exacta del evento |
| `evento` | String | Tipo de evento (`actividad_completada`) |
| `datos.estudiante.id` | Integer | ID único del estudiante |
| `datos.estudiante.nombre` | String | Nombre completo del estudiante |
| `datos.estudiante.email` | String | Email del estudiante |
| `datos.actividad.id` | Integer | ID de la actividad |
| `datos.actividad.titulo` | String | Nombre/título de la actividad |
| `datos.actividad.tipo` | String | Tipo de actividad (`quiz_ciencias`, `juego`, etc) |
| `datos.curso.id` | Integer | ID del curso |
| `datos.curso.nombre` | String | Nombre del curso |
| `datos.resultados.puntuacion` | Float | Puntuación del 0-100 |
| `datos.resultados.tiempo_empleado_minutos` | Integer | Minutos que tardó en completar |
| `datos.resultados.fecha_entrega` | ISO DateTime | Fecha y hora de entrega |
| `datos.resultados.estado` | String | Estado (`completada`, `revisada`, etc) |
| `datos.resultados.es_tardia` | Boolean | `true` si se entregó después de la fecha límite |

---

## 🛠️ Configuración en n8n

### Paso 1: Crear un Webhook Trigger

1. En n8n, crea un nuevo workflow
2. Agrega un nodo "Webhook" como trigger
3. Configura:
   - **Method**: POST
   - **Path**: `/Alumnos_settings`
   - **Authentication**: None (si lo necesitas, configúralo en el backend)

### Paso 2: Procesar los Datos

Ejemplo de flujo en n8n:

```
Webhook Trigger
    ↓
Extract Estudiante Info
    ↓
Save to Database/Spreadsheet
    ↓
Send Email/Notification
    ↓
Update Google Sheet
    ↓
HTTP Response (200 OK)
```

### Paso 3: Testing

Para probar el webhook en n8n:

1. Haz clic en el nodo Webhook y copia la URL de test
2. En Django shell:
```python
from api.webhooks import enviar_resultado_actividad_a_n8n

# Datos de prueba
test_data = {
    'estudiante_id': 1,
    'estudiante_nombre': 'Test Student',
    'estudiante_email': 'test@example.com',
    'actividad_id': 1,
    'actividad_titulo': 'Test Activity',
    'actividad_tipo': 'quiz_ciencias',
    'curso_id': 1,
    'curso_nombre': 'Test Course',
    'puntuacion': 90,
    'tiempo_empleado': 10,
    'fecha_entrega': '2025-11-25T15:30:45',
    'estado': 'completada',
    'es_tardia': False
}

# Enviar
result = enviar_resultado_actividad_a_n8n(test_data)
print(result)
```

---

## 🔐 Seguridad

### Headers Incluidos

```
Content-Type: application/json
User-Agent: EduNuñez-Django/1.0
```

### Validación en n8n

Se recomienda validar en n8n:

```javascript
// Validar estructura
const timestamp = $input.first().json.timestamp;
const evento = $input.first().json.evento;
const datos = $input.first().json.datos;

if (!timestamp || evento !== 'actividad_completada' || !datos) {
  throw new Error('Invalid payload structure');
}
```

---

## 📝 Logging y Debugging

### Logs en Django

Los logs se guardan automáticamente. Revísalos:

```bash
# Tail de logs en tiempo real
tail -f /path/to/django/logs/django.log | grep webhook

# O en Django shell
from django.conf import settings
import logging
logger = logging.getLogger('api.webhooks')
```

### Estructura de Logs

```
[2025-11-25 15:30:45] Enviando resultado de actividad al webhook de n8n: {...}
[2025-11-25 15:30:45] Respuesta del webhook n8n: Status=200, Body={...}
[2025-11-25 15:30:45] Resultado de actividad enviado exitosamente a n8n. Status: 200
```

---

## ⚙️ Configuración Avanzada

### Modificar el Webhook URL

En `api/webhooks.py`:

```python
WEBHOOKS_CONFIG = {
    'n8n_alumnos': {
        'url': 'http://localhost:5678/webhook/Alumnos_settings',  # ← Cambia aquí
        'timeout': 10,
        'retry_attempts': 3,
        'enabled': True
    }
}
```

### Habilitar/Deshabilitar Webhook

```python
# En webhooks.py
WEBHOOKS_CONFIG['n8n_alumnos']['enabled'] = False  # Deshabilitar
```

### Cambiar Reintentos

```python
# En webhooks.py - Aumentar a 5 reintentos
'retry_attempts': 5
```

---

## 🚀 Casos de Uso en n8n

### 1. Guardar en Spreadsheet

```
Webhook → Google Sheets
Inserta automáticamente los resultados en una hoja
```

### 2. Notificar Profesor

```
Webhook → Conditional (if puntuacion < 60)
       ↓
    Send Email to Profesor
```

### 3. Actualizar CRM

```
Webhook → Split Fields
       ↓
    Update Student Record
       ↓
    Zapier/Make Integration
```

### 4. Análisis en Tiempo Real

```
Webhook → Aggregate
       ↓
    Database Update
       ↓
    Dashboard Notification
```

### 5. Generar Reportes

```
Webhook → Collect (agrupa datos)
       ↓
    PDF Generator
       ↓
    Send Email con PDF
```

---

## 🔗 Integración con Otros Servicios

### Via n8n (recomendado)

n8n puede conectar con:

- **Google Sheets**: Guardar resultados automáticamente
- **Slack**: Notificaciones en tiempo real
- **Email**: Avisos a profesores
- **Zapier**: Integración con otros servicios
- **Bases de datos**: PostgreSQL, MySQL, MongoDB
- **APIs**: Cualquier servicio externo

### Ejemplo: Notificar por Slack

```javascript
// En n8n - Slack Node
{
  "text": `🎓 ${$input.first().json.datos.estudiante.nombre} completó la actividad`,
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": `*Actividad*: ${$input.first().json.datos.actividad.titulo}\n*Puntuación*: ${$input.first().json.datos.resultados.puntuacion}/100\n*Tiempo*: ${$input.first().json.datos.resultados.tiempo_empleado_minutos} min`
      }
    }
  ]
}
```

---

## 🧪 Testing Completo

### Test 1: Envío Manual

```bash
curl -X POST http://localhost:5678/webhook/Alumnos_settings \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-11-25T15:30:45",
    "evento": "actividad_completada",
    "datos": {
      "estudiante": {
        "id": 1,
        "nombre": "Test User",
        "email": "test@example.com"
      },
      "actividad": {
        "id": 1,
        "titulo": "Test",
        "tipo": "quiz_ciencias"
      },
      "curso": {
        "id": 1,
        "nombre": "Test Course"
      },
      "resultados": {
        "puntuacion": 85,
        "tiempo_empleado_minutos": 10,
        "fecha_entrega": "2025-11-25T15:30:45",
        "estado": "completada",
        "es_tardia": false
      }
    }
  }'
```

### Test 2: Desde Django

```python
python manage.py shell

from api.webhooks import enviar_resultado_actividad_a_n8n

test_data = {
    'estudiante_id': 1,
    'estudiante_nombre': 'Juan Test',
    'estudiante_email': 'juan@test.com',
    'actividad_id': 1,
    'actividad_titulo': 'Color Game',
    'actividad_tipo': 'quiz_ciencias',
    'curso_id': 1,
    'curso_nombre': 'Ciencias',
    'puntuacion': 95,
    'tiempo_empleado': 5,
    'fecha_entrega': '2025-11-25T15:30:45',
    'estado': 'completada',
    'es_tardia': False
}

result = enviar_resultado_actividad_a_n8n(test_data)
print(f"Éxito: {result['success']}")
print(f"Mensaje: {result['message']}")
print(f"Código: {result['response_code']}")
```

### Test 3: Verificar en Logs

```bash
# En terminal Django
python manage.py runserver --verbosity 2

# Deberías ver:
# Enviando resultado de actividad al webhook de n8n: {...}
# Respuesta del webhook n8n: Status=200
```

---

## ✅ Checklist de Verificación

- [ ] El webhook URL es correcto: `http://localhost:5678/webhook/Alumnos_settings`
- [ ] El servicio n8n está corriendo en puerto 5678
- [ ] Django está enviando POST al completar actividades
- [ ] Logs muestran envío exitoso (status 200/201/202)
- [ ] n8n recibe y procesa los datos correctamente
- [ ] Los datos se guardan en el destino final (Sheets, DB, etc)
- [ ] Las notificaciones se envían correctamente
- [ ] Los reintentos funcionan en caso de falla

---

## 📞 Troubleshooting

### Problema: "Connection refused"

**Solución**: Verifica que n8n está corriendo:
```bash
lsof -i :5678  # Verificar si puerto 5678 está en uso
```

### Problema: "Timeout"

**Solución**: Aumenta el timeout en `webhooks.py`:
```python
'timeout': 30  # Cambiar de 10 a 30 segundos
```

### Problema: Datos no llegan

**Solución**: 
1. Revisa los logs en Django
2. Verifica el webhook URL en n8n
3. Prueba con curl manualmente

### Problema: Error 400 Bad Request

**Solución**: Valida que el JSON sea válido:
```python
import json
# Validar estructura
json.dumps(actividad_data)  # Debe no lanzar error
```

---

## 📈 Monitoreo

### Dashboards Recomendados en n8n

1. **Cantidad de Actividades**: Webhook Execution Count
2. **Promedio de Puntuaciones**: Average Score
3. **Tiempo Promedio**: Average Time Spent
4. **Entregas Tardías**: Late Submissions Count

---

## 🔄 Webhook Flow Diagram

```
┌─────────────────────────────────────┐
│   Estudiante completa actividad     │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  StudentActivities.js (Frontend)    │
│  Envía POST a Django                │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  completar_actividad_estudiante()   │
│  (Backend - views.py)               │
│  - Guarda en BD                     │
│  - Registra evento                  │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  enviar_resultado_actividad_a_n8n() │
│  (webhooks.py)                      │
│  - Formatea datos                   │
│  - Envía POST a n8n                 │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  n8n Webhook Trigger                │
│  POST /webhook/Alumnos_settings     │
└────────────┬────────────────────────┘
             │
             ↓
   ┌─────────┴──────────┬──────────┬──────────┐
   ↓                    ↓          ↓          ↓
┌─────────┐  ┌────────────────┐ ┌────────┐ ┌────────┐
│ Sheets  │  │ Notification   │ │ Email  │ │ Otros  │
│ (DB)    │  │ (Slack/Teams)  │ │ Grader │ │ Servicios
└─────────┘  └────────────────┘ └────────┘ └────────┘
```

---

## 📚 Recursos Adicionales

- [Documentación n8n](https://docs.n8n.io/)
- [n8n Webhook Trigger](https://docs.n8n.io/nodes/n8n-nodes-base.webhookTrigger/)
- [Testing Webhooks](https://webhook.site/)

---

**Última actualización**: Noviembre 25, 2025
**Versión**: 1.0
**Autor**: EduNuñez Development Team
