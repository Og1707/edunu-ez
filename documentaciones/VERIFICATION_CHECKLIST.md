# ✅ Verificación de la Integración Webhook

## 🎯 Checklist Final

Usa esta guía para verificar que todo funciona correctamente.

---

## Paso 1: Verificar Archivos Creados

```bash
# Navega al directorio del proyecto
cd edunuñez_django

# Verifica que existan estos archivos
ls -la api/webhooks.py              # ✅ Debe existir
ls -la test_n8n_webhook.py          # ✅ Debe existir
ls -la N8N_WEBHOOK_INTEGRATION.md   # ✅ Debe existir
ls -la WEBHOOK_QUICK_START.md       # ✅ Debe existir
ls -la WEBHOOK_IMPLEMENTATION_SUMMARY.md  # ✅ Debe existir
```

**Resultado esperado**: Todos los archivos existen sin error

---

## Paso 2: Verificar Código en api/views.py

```bash
# Busca la función completar_actividad_estudiante
grep -n "enviar_resultado_actividad_a_n8n" api/views.py
```

**Resultado esperado**: 
```
Línea con: enviar_resultado_actividad_a_n8n(actividad_data)
```

---

## Paso 3: Verificar Imports en api/views.py

```python
# En Python shell
python manage.py shell

# Verifica que el import funciona
from api.webhooks import enviar_resultado_actividad_a_n8n
print("✅ Import exitoso")

# Verifica la configuración
from api.webhooks import WEBHOOKS_CONFIG
print(WEBHOOKS_CONFIG)
```

**Resultado esperado**:
```python
{
    'n8n_alumnos': {
        'url': 'http://localhost:5678/webhook/Alumnos_settings',
        'timeout': 10,
        'retry_attempts': 3,
        'enabled': True
    }
}
```

---

## Paso 4: Iniciar Servicios

### Terminal 1: n8n

```bash
# Opción A: Directamente
n8n start

# Opción B: Docker
docker run -it -p 5678:5678 n8nio/n8n
```

**Verificación**:
- Deberías ver: `n8n ready on 0.0.0.0, port 5678`
- Abre: http://localhost:5678
- Deberías ver la interfaz de n8n

### Terminal 2: Django

```bash
cd edunuñez_django
python manage.py runserver
```

**Verificación**:
- Deberías ver: `Starting development server at http://127.0.0.1:8000/`

### Terminal 3: React

```bash
cd edunuñez_django/edunuñez/visual_edu
npm start
```

**Verificación**:
- Deberías ver: `webpack compiled successfully`
- Abre: http://localhost:3000

---

## Paso 5: Crear Webhook en n8n

1. Abre http://localhost:5678
2. Crea workflow nuevo: "+" → "New Workflow"
3. Renombra: "Alumnos Settings"
4. Agrega nodo: "Webhook" (click en +)
5. Configura:
   - **Method**: POST
   - **Path**: `/Alumnos_settings`
   - Click en "Listen"

**Verificación**:
- El nodo debe mostrar: "Listening for POST requests"
- Copia la URL que se muestra

---

## Paso 6: Test Manual con curl

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

**Verificación**:
- n8n debe mostrar "Test webhook clicked" (en el nodo)
- Respuesta debe ser 200 OK
- Los datos deben aparecer en n8n

---

## Paso 7: Test Automático

```bash
python test_n8n_webhook.py
```

**Resultado esperado**:
```
╔════════════════════════════════════════════════════════════╗
║      🎯 Tests de Integración con n8n                     ║
╚════════════════════════════════════════════════════════════╝

CONFIGURACIÓN DE WEBHOOK
🔗 URL: http://localhost:5678/webhook/Alumnos_settings
⏱️ Timeout: 10 segundos
🔄 Reintentos: 3
✨ Habilitado: Sí ✅

TEST 1: Envío Básico de Resultado
📤 Enviando datos al webhook...
✅ Éxito: True
📝 Mensaje: Webhook enviado exitosamente (status 200)
📊 Código HTTP: 200

... (más tests)

📊 RESUMEN FINAL DE TESTS
  ✅ PASÓ: Test 1 - Envío Básico
  ✅ PASÓ: Test 2 - Puntuación Baja
  ✅ PASÓ: Test 3 - Entrega Tardía
  ✅ PASÓ: Test 4 - Puntuación Perfecta
  ✅ PASÓ: Test 5 - Manejo de Errores
  ✅ PASÓ: Test 6 - Múltiples Resultados

📈 Total: 6/6 tests exitosos
🎉 ¡TODOS LOS TESTS PASARON!
```

Si algo falla, revisa los logs de error.

---

## Paso 8: Test End-to-End

### 8.1 Inicia Sesión como Estudiante

1. Abre http://localhost:3000
2. Login como estudiante:
   - Email: `student@example.com` (o el que tengas)
   - Password: tu password

### 8.2 Completa una Actividad

1. Ve a "Mis Actividades"
2. Busca una actividad (Reconocimiento de Colores es ideal)
3. Click en "Iniciar Actividad"
4. Juega o completa la actividad
5. Click en "Completar Actividad"

### 8.3 Verifica en n8n

1. Abre http://localhost:5678
2. Ve a tu workflow "Alumnos Settings"
3. Deberías ver una nueva ejecución
4. Los datos deben estar en el JSON

**Resultado esperado**:
```json
{
  "timestamp": "2025-11-25T15:30:45",
  "evento": "actividad_completada",
  "datos": {
    "estudiante": {
      "id": 1,
      "nombre": "Juan Pérez López",
      "email": "juan@example.com"
    },
    ...
  }
}
```

### 8.4 Verifica en Logs de Django

En la terminal de Django deberías ver:

```
Enviando resultado de actividad al webhook de n8n: {...}
Respuesta del webhook n8n: Status=200
Resultado de actividad enviado exitosamente a n8n. Status: 200
```

---

## Paso 9: Verificar Respuesta del Frontend

Después de completar una actividad, en la respuesta deberías ver:

```json
{
  "mensaje": "Actividad completada exitosamente",
  "progreso": {
    "completada": true,
    "puntuacion": 85,
    ...
  },
  "webhook": {
    "enviado": true,
    "mensaje": "Webhook enviado exitosamente (status 200)",
    "codigo": 200
  }
}
```

---

## 🔍 Debugging

### Verifica que n8n recibe datos

En el nodo Webhook de n8n:
1. Click en "Inspect" 
2. Click en la ejecución más reciente
3. Deberías ver los datos completos

### Verifica logs de Django

```bash
# En la terminal de Django, deberías ver:
[2025-11-25 15:30:45] INFO: Enviando resultado de actividad al webhook de n8n
[2025-11-25 15:30:45] INFO: Respuesta del webhook n8n: Status=200
```

### Verifica que la conexión funciona

```bash
# Test de conectividad
python -c "import requests; requests.get('http://localhost:5678')"

# Si no error, la conexión funciona
```

---

## ✅ Tabla de Verificación

| Elemento | Verificar | Status |
|----------|-----------|--------|
| Archivo `webhooks.py` | Existe | ☐ |
| Archivo `test_n8n_webhook.py` | Existe | ☐ |
| Import en `views.py` | Funciona | ☐ |
| Configuración | Correcta | ☐ |
| n8n corriendo | Puerto 5678 | ☐ |
| Django corriendo | Puerto 8000 | ☐ |
| React corriendo | Puerto 3000 | ☐ |
| Webhook en n8n | Creado | ☐ |
| Test curl | 200 OK | ☐ |
| Test automático | 6/6 pasados | ☐ |
| Test end-to-end | Datos llegan | ☐ |
| Logs Django | Muestran envío | ☐ |
| Respuesta API | Incluye webhook | ☐ |

---

## 🎯 Resultado Final

Si todo pasó ✅:

```
✅ Archivos creados correctamente
✅ Código integrado en views.py
✅ n8n recibe datos correctamente
✅ Logs muestran envío exitoso
✅ Tests automáticos pasan
✅ Frontend muestra estado
✅ La integración funciona end-to-end
```

🎉 **¡El webhook está funcionando correctamente!**

---

## 🚨 Si algo falla

### No se envía al webhook

1. Verifica que n8n está corriendo
   ```bash
   lsof -i :5678
   ```

2. Verifica la URL en `api/webhooks.py`
   ```python
   from api.webhooks import WEBHOOKS_CONFIG
   print(WEBHOOKS_CONFIG['n8n_alumnos']['url'])
   ```

3. Prueba con curl
   ```bash
   curl http://localhost:5678/webhook/Alumnos_settings -X POST -d "{}"
   ```

### n8n no recibe datos

1. Verifica que el path es correcto en n8n
   - Debe ser: `/Alumnos_settings`

2. Verifica que el webhook está en "Listen"
   - Click en "Listen" en n8n

3. Revisa los logs de n8n
   - En la terminal donde corre n8n

### Test automático falla

1. Verifica que n8n esté corriendo
2. Revisa el error específico
3. Busca en `N8N_WEBHOOK_INTEGRATION.md` → Troubleshooting

---

## 📞 Contacto/Support

Si necesitas ayuda:

1. Revisa la documentación:
   - `WEBHOOK_QUICK_START.md` (5 min)
   - `N8N_WEBHOOK_INTEGRATION.md` (30 min)

2. Verifica los logs
   - Django: Terminal donde corre
   - n8n: Terminal donde corre

3. Prueba manualmente con curl
   - Ver paso 6 arriba

---

**Última actualización**: Noviembre 25, 2025
**Versión**: 1.0
