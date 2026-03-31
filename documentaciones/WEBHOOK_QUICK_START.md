# Guía Rápida: Webhook n8n para Actividades

## 🚀 Inicio Rápido (5 minutos)

### Paso 1: Verificar que n8n esté corriendo

```bash
# En una terminal
n8n start

# O si está en Docker
docker run -it -p 5678:5678 n8nio/n8n
```

Deberías ver:
```
n8n ready on 0.0.0.0, port 5678
```

### Paso 2: Crear el Webhook en n8n

1. Abre http://localhost:5678
2. Crea un nuevo workflow
3. Agrega un nodo "Webhook" (trigger)
4. Configura:
   - **Method**: POST
   - **Path**: `/Alumnos_settings`
5. Copia la URL del webhook (aparecerá en el nodo)

### Paso 3: Verificar la Integración de Django

El backend ya está configurado. Solo verifica:

```python
# Archivo: api/webhooks.py
WEBHOOKS_CONFIG = {
    'n8n_alumnos': {
        'url': 'http://localhost:5678/webhook/Alumnos_settings',
        'timeout': 10,
        'retry_attempts': 3,
        'enabled': True
    }
}
```

### Paso 4: Probar el Webhook

#### Opción A: Prueba desde Django Shell

```bash
python manage.py shell
```

```python
from api.webhooks import enviar_resultado_actividad_a_n8n
from datetime import datetime

test_data = {
    'estudiante_id': 1,
    'estudiante_nombre': 'Test Student',
    'estudiante_email': 'test@example.com',
    'actividad_id': 1,
    'actividad_titulo': 'Test Activity',
    'actividad_tipo': 'quiz_ciencias',
    'curso_id': 1,
    'curso_nombre': 'Test Course',
    'puntuacion': 85,
    'tiempo_empleado': 10,
    'fecha_entrega': datetime.now(),
    'estado': 'completada',
    'es_tardia': False
}

result = enviar_resultado_actividad_a_n8n(test_data)
print(result)
```

Deberías ver:
```
{
    'success': True,
    'message': 'Webhook enviado exitosamente (status 200)',
    'response_code': 200
}
```

#### Opción B: Prueba automática

```bash
python test_n8n_webhook.py
```

Esto ejecutará 6 tests diferentes.

### Paso 5: Probar end-to-end

1. Inicia Django: `python manage.py runserver`
2. Inicia React: `cd visual_edu && npm start`
3. Abre http://localhost:3000
4. Inicia sesión como estudiante
5. Completa una actividad
6. **¡Los datos deberían llegar a n8n automáticamente!**

---

## 🎯 Verificar que Funciona

### En n8n

El nodo Webhook debe mostrar:
- Ejecuciones: ✅ (aumenta cuando completa una actividad)
- Última ejecución: timestamp reciente
- Datos recibidos: JSON con información del estudiante

### En Django

Revisa los logs:
```bash
# En la terminal donde corre Django
python manage.py runserver --verbosity 2

# O en logs
tail -f logs/django.log | grep webhook
```

Deberías ver:
```
Enviando resultado de actividad al webhook de n8n: {...}
Respuesta del webhook n8n: Status=200
Resultado de actividad enviado exitosamente a n8n. Status: 200
```

---

## 📊 Estructura de Datos Recibidos en n8n

Cuando un estudiante completa una actividad, n8n recibe:

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

## 🔧 Casos de Uso Comunes en n8n

### 1️⃣ Guardar en Google Sheets

```
Webhook Trigger
    ↓
Add Rows (Google Sheets Node)
    - Spreadsheet: Resultados Estudiantes
    - Sheet: Actividades
    - Columns: nombre, email, puntuacion, tiempo
    ↓
HTTP Response (200)
```

**Configurar Google Sheets Node:**
- Conecta tu cuenta Google
- Selecciona el spreadsheet
- Mapea campos del webhook

### 2️⃣ Notificar por Slack

```
Webhook Trigger
    ↓
Function (JavaScript)
    {
      "text": `${json.datos.estudiante.nombre} 
               completó ${json.datos.actividad.titulo}`
    }
    ↓
Slack Node (Send Message)
    - Channel: #actividades
    - Text: (del nodo anterior)
    ↓
HTTP Response (200)
```

### 3️⃣ Guardar en Base de Datos

```
Webhook Trigger
    ↓
Execute Query (PostgreSQL/MySQL)
    INSERT INTO resultados (estudiante_id, actividad_id, puntuacion, tiempo)
    VALUES ($1, $2, $3, $4)
    ↓
HTTP Response (200)
```

### 4️⃣ Enviar Email

```
Webhook Trigger
    ↓
Conditional (If puntuacion < 60)
    ↓
    YES → Send Email (al profesor)
    NO  → Continue
    ↓
HTTP Response (200)
```

### 5️⃣ Múltiples Destinos (Split)

```
Webhook Trigger
    ↓
Split (separa en 3 caminos)
    ├→ Google Sheets
    ├→ Slack
    └→ Database
    ↓
HTTP Response (200)
```

---

## 🧪 Test Manual con curl

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
        "titulo": "Test Activity",
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

Deberías recibir una respuesta 200 OK desde n8n.

---

## ⚙️ Troubleshooting

### ❌ "Connection refused"

```bash
# Verifica que n8n está corriendo en puerto 5678
lsof -i :5678

# Si no está corriendo, inicia n8n
n8n start
```

### ❌ "Webhook URL no coincide"

Asegúrate que en `api/webhooks.py` la URL sea exacta:

```python
'url': 'http://localhost:5678/webhook/Alumnos_settings',
```

### ❌ "Los datos no llegan"

1. Verifica los logs de Django:
   ```bash
   python manage.py runserver --verbosity 2
   ```

2. Verifica los logs de n8n en http://localhost:5678

3. Prueba con curl manualmente

### ❌ "Timeout"

Si tarda mucho:

1. Aumenta el timeout en `api/webhooks.py`:
   ```python
   'timeout': 30,  # Cambiar de 10 a 30 segundos
   ```

2. Asegúrate que n8n responda rápido (no haga queries largas)

---

## 📝 Documentación Completa

Para más detalles, ve a: `N8N_WEBHOOK_INTEGRATION.md`

---

## ✅ Checklist Final

- [ ] n8n está corriendo en puerto 5678
- [ ] Django está configurado con la URL correcta
- [ ] Webhook en n8n está configurado para POST
- [ ] Prueba manual funciona (curl)
- [ ] Prueba desde Django shell funciona
- [ ] Se reciben los datos en n8n
- [ ] Los datos se guardan/procesan correctamente

---

## 🎉 ¡Listo!

El webhook está configurado y funcionando. Los resultados de las actividades se enviarán automáticamente a n8n cuando los estudiantes las completen.

**Próximos pasos:**
1. Configurar el procesamiento en n8n (guardar en Sheets, enviar email, etc)
2. Monitorear en http://localhost:5678
3. Ajustar según tus necesidades

¡Que disfrutes de la automatización! 🚀
