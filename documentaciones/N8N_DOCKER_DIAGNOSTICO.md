# Diagnóstico: n8n en Docker + Django

## 🔍 DIAGNÓSTICO RÁPIDO

Ejecuta estos comandos en orden y comparte los resultados:

### 1. ¿Está n8n corriendo en Docker?

```bash
docker ps | grep n8n
```

**Si ves algo como esto: ✅**
```
CONTAINER ID   IMAGE           PORTS                    NAMES
abc123def456   n8n:latest      0.0.0.0:5678->5678/tcp  n8n
```

**Si está vacío: ❌**
```
# Inicia n8n
docker run -p 5678:5678 n8n
```

---

### 2. ¿Puedes acceder a n8n desde tu navegador?

```bash
# En navegador:
http://localhost:5678
```

**Si ves la UI de n8n: ✅**

**Si no conecta: ❌**
```bash
# Verifica que el puerto está mapeado
docker port <CONTAINER_ID>

# Resultado esperado:
# 5678/tcp -> 0.0.0.0:5678
```

---

### 3. ¿Puede Django conectar a n8n?

```bash
# En terminal de Django
python manage.py shell

# Ejecuta esto:
import requests
response = requests.get('http://localhost:5678')
print(f"Status: {response.status_code}")
```

**Si ves "Status: 200": ✅**

**Si ves error de conexión: ❌**
- Firewall de Windows bloqueando
- Puerto no mapeado correctamente
- n8n no está corriendo

---

### 4. ¿El webhook existe en n8n?

```bash
# En n8n (navegador), verifica:
# 1. Ve a tu flujo
# 2. Busca el nodo "Webhook"
# 3. Revisa la URL base y path
```

**Debe verse:**
```
Base URL: http://localhost:5678
Path: Alumnos_settings
Full URL: http://localhost:5678/webhook/Alumnos_settings
```

---

### 5. Ejecuta la prueba

```bash
python edunuñez/test_n8n_webhook.py
```

**Resultado esperado:**
```
Total: 6/6 tests exitosos
Exito: TODOS LOS TESTS PASARON!
```

---

## 🐛 SI FALLA EN ALGUN PASO

### Falla en Paso 1: "n8n no está en docker ps"

```bash
# Iniciar n8n
docker run -d -p 5678:5678 n8n

# Verificar
docker ps | grep n8n
```

---

### Falla en Paso 2: "No puedo acceder a http://localhost:5678"

**Verifica puertos:**
```bash
docker port <CONTAINER_ID>
```

**Si dice `5679->5678` por ejemplo, usar:**
```
http://localhost:5679
```

**Actualizar en `webhooks.py`:**
```python
WEBHOOKS_CONFIG = {
    'n8n_alumnos': {
        'url': 'http://localhost:5679/webhook/Alumnos_settings',  # Puerto correcto
        'timeout': 10,
        'retry_attempts': 3,
        'enabled': True
    }
}
```

---

### Falla en Paso 3: "Connection refused desde Django"

**Causa más común:** Firewall de Windows

**Solución:**
```bash
# Temporalmente deshabilitar firewall (NO recomendado en producción)
netsh advfirewall set allprofiles state off

# O permitir Python:
# Windows Defender Firewall → Permitir aplicación → Python
```

---

### Falla en Paso 4: "Webhook no existe"

**En n8n:**
1. Crea un nuevo flujo o abre uno existente
2. Arrastra el nodo "Webhook"
3. Configura:
   - HTTP Method: POST
   - Path: `Alumnos_settings`
4. Activa el flujo (toggle verde)

---

### Falla en Paso 5: "Test falla - Connection timeout"

**Aumentar timeout en `webhooks.py`:**
```python
WEBHOOKS_CONFIG = {
    'n8n_alumnos': {
        'url': 'http://localhost:5678/webhook/Alumnos_settings',
        'timeout': 30,  # Aumentado de 10 a 30
        'retry_attempts': 5,  # Más reintentos
        'enabled': True
    }
}
```

---

## 📊 MATRIZ DE RESOLUCIÓN

```
¿En qué paso falla?
│
├─ Paso 1 (docker ps)
│  └─ n8n no aparece
│     └─ Solución: docker run -p 5678:5678 n8n
│
├─ Paso 2 (navegador)
│  └─ No conecta a localhost:5678
│     └─ Solución: Verificar docker port <ID>
│
├─ Paso 3 (Python/Django)
│  └─ ConnectionError
│     └─ Solución: Deshabilitar Firewall de Windows
│
├─ Paso 4 (Webhook en n8n)
│  └─ 404 Not Found
│     └─ Solución: Crear nodo Webhook con path correcto
│
└─ Paso 5 (Test script)
   └─ Timeout
      └─ Solución: Aumentar timeout a 30 segundos
```

---

## ✅ CHECKLIST FINAL

Marca las que funcionan:

- [ ] `docker ps | grep n8n` muestra el contenedor
- [ ] Navegador accede a `http://localhost:5678`
- [ ] Python conecta: `requests.get('http://localhost:5678')` → 200
- [ ] Webhook en n8n existe con ruta `Alumnos_settings`
- [ ] Flujo en n8n está activo (toggle verde)
- [ ] Django corre en host (no en Docker)
- [ ] Test script ejecuta sin errores de conexión

Si todas tienen ✅, **todo funciona correctamente**.

---

## 🆘 LOGS PARA DEBUGGING

### Log de n8n (Docker)

```bash
docker logs <CONTAINER_ID> -f --tail 100
```

Busca errores como:
```
Error: Connection refused
Error: Webhook not found
```

### Log de Django

```bash
python manage.py runserver
```

Busca:
```
Enviando resultado de actividad al webhook de n8n
Respuesta del webhook n8n: Status=200
```

### Log de Python (test)

```bash
python edunuñez/test_n8n_webhook.py 2>&1 | tee test_output.log
```

Busca:
```
[OK]: Test 1 - Envio Basico
Total: 6/6 tests exitosos
```

---

## 📞 SOPORTE RÁPIDO

Si aún falla, proporciona:

1. Output de: `docker ps | grep n8n`
2. Output de: `docker port <CONTAINER_ID>`
3. Output de: `python edunuñez/test_n8n_webhook.py` (completo)
4. Output de: `docker logs <CONTAINER_ID>` (últimas 50 líneas)
5. Output de: `python manage.py shell` + `requests.get('http://localhost:5678')`

Con esta info podré identificar el problema exacto. 🔧
