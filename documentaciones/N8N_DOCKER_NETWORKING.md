# n8n en Docker: Guía de Networking y Troubleshooting

## El Problema

Cuando n8n corre en un **contenedor Docker**, la dirección `localhost:5678` puede **NO funcionar** desde tu máquina host o desde Django.

Esto es porque:
- Docker crea una red aislada
- `localhost` dentro del contenedor es diferente a `localhost` en el host
- Las URLs necesitan ser diferentes según de dónde se llamen

---

## 🔧 SOLUCIÓN: Configurar URLs Correctamente

### PASO 1: Identifica tu Configuración de Docker

Ejecuta:
```bash
docker ps | grep n8n
```

Deberías ver algo como:
```
CONTAINER ID   IMAGE      PORTS
abc123def456   n8n:latest 0.0.0.0:5678->5678/tcp
```

### PASO 2: Encuentra la IP de tu Contenedor

#### Opción A: IP del Contenedor (Dentro de Docker Network)

```bash
docker inspect <CONTAINER_ID> | grep "IPAddress"
```

Resultado típico:
```json
"IPAddress": "172.17.0.2"
```

#### Opción B: IP del Host (desde el contenedor)

En Linux/Mac:
```bash
docker exec <CONTAINER_ID> host.docker.internal
```

En Windows (con Docker Desktop):
```bash
host.docker.internal
```

---

## 📍 URLs CORRECTAS Según el Contexto

### Contexto 1: Desde el Navegador (en tu PC)

```
http://localhost:5678
```
✅ **Esto funciona** - El navegador accede al host

---

### Contexto 2: Desde Django (en tu PC, no en Docker)

```
http://localhost:5678/webhook/Alumnos_settings
```
✅ **Esto funciona** - Django en host accede al container

---

### Contexto 3: Si Django TAMBIÉN estuviera en Docker

```
http://host.docker.internal:5678/webhook/Alumnos_settings  (Windows)
http://172.17.0.2:5678/webhook/Alumnos_settings            (Linux - IP del container)
```

---

## ✅ VERIFICACIÓN RÁPIDA

### Test 1: ¿Puede tu PC acceder a n8n?

```bash
# Desde tu terminal (PowerShell/CMD)
curl http://localhost:5678

# O en PowerShell:
Invoke-WebRequest http://localhost:5678
```

**Resultado esperado:**
```
StatusCode        : 200
Content           : <!DOCTYPE html>...
```

### Test 2: ¿Puede Django acceder al webhook?

```bash
# En una terminal de Django
python manage.py shell

from api.webhooks import WEBHOOKS_CONFIG
import requests

# Ver configuración actual
print(WEBHOOKS_CONFIG)

# Intentar conectar
response = requests.get('http://localhost:5678')
print(f"Status: {response.status_code}")
```

**Resultado esperado:**
```
Status: 200
```

---

## 🔴 ERRORES COMUNES Y SOLUCIONES

### Error 1: "Connection refused"

**Síntomas:**
```
ConnectionError: [Errno 111] Connection refused
```

**Causas posibles:**
1. n8n no está corriendo
2. n8n está corriendo pero en puerto diferente
3. Firewall bloqueando

**Solución:**
```bash
# Verificar que n8n está corriendo
docker ps | grep n8n

# Si no aparece, iniciar:
docker run -p 5678:5678 n8n

# Si aparece pero dice puerto diferente, actualizar la URL
# Ejemplo: si dice 5679:5678, usar http://localhost:5679
```

---

### Error 2: "Timeout"

**Síntomas:**
```
requests.exceptions.ConnectTimeout: ('Connection aborted.', TimeoutError(110, 'Connection timed out'))
```

**Causas posibles:**
1. n8n tarda en responder
2. Host.docker.internal configurado incorrectamente
3. Firewall de Windows bloqueando

**Solución:**
```python
# En webhooks.py, aumentar timeout:
WEBHOOKS_CONFIG = {
    'n8n_alumnos': {
        'timeout': 30,  # De 10 a 30 segundos
        'retry_attempts': 5  # Aumentar reintentos
    }
}
```

---

### Error 3: "404 Not Found"

**Síntomas:**
```
response.status_code = 404
```

**Causas:**
1. Webhook no existe en n8n
2. Ruta incorrecta
3. Flujo no está activo

**Solución:**
1. En n8n, verifica que el webhook tiene la ruta: `Alumnos_settings`
2. Activa el flujo (toggle verde)
3. Verifica la URL exacta en el nodo Webhook

---

### Error 4: "Host.docker.internal not working"

**Síntomas:**
```
Name or service not known: host.docker.internal
```

**Contexto:** Solo aplica si Django TAMBIÉN está en Docker

**Solución:**
```bash
# En docker-compose.yml, agregar:
services:
  django:
    extra_hosts:
      - "host.docker.internal:host-gateway"
  
  n8n:
    ports:
      - "5678:5678"
```

---

## 🛠️ CONFIGURACIÓN COMPLETA PARA DOCKER

### Opción 1: n8n en Docker, Django en Host (TU CASO)

**Archivo de configuración:** `api/webhooks.py`

```python
WEBHOOKS_CONFIG = {
    'n8n_alumnos': {
        'url': 'http://localhost:5678/webhook/Alumnos_settings',
        'timeout': 10,
        'retry_attempts': 3,
        'enabled': True
    }
}
```

**Por qué funciona:**
- Django corre en el host → puede acceder a `localhost:5678`
- Docker publica el puerto 5678 en el host

---

### Opción 2: Ambos en Docker

Si LUEGO quieres poner Django también en Docker:

**docker-compose.yml:**
```yaml
version: '3'

services:
  n8n:
    image: n8n:latest
    ports:
      - "5678:5678"
    environment:
      - NODE_ENV=production

  django:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - n8n
    environment:
      - N8N_URL=http://n8n:5678
```

**api/webhooks.py:**
```python
import os

WEBHOOKS_CONFIG = {
    'n8n_alumnos': {
        'url': os.getenv('N8N_URL', 'http://localhost:5678') + '/webhook/Alumnos_settings',
        'timeout': 10,
        'retry_attempts': 3,
        'enabled': True
    }
}
```

---

## 📋 CHECKLIST DE CONFIGURACION

Para que todo funcione con n8n en Docker:

- [ ] n8n corre en Docker: `docker ps | grep n8n` (debe mostrar algo)
- [ ] Puerto 5678 mapeado: `:5678` aparece en el output anterior
- [ ] Puedo acceder en navegador: `http://localhost:5678` (abre la UI)
- [ ] URL correcta en `webhooks.py`: `http://localhost:5678/webhook/Alumnos_settings`
- [ ] Webhook en n8n existe con ruta: `Alumnos_settings`
- [ ] Flujo en n8n está activo (toggle verde)
- [ ] Django corre fuera de Docker: `python manage.py runserver`

Si todos están ✅, todo debería funcionar.

---

## 🧪 PRUEBA COMPLETA CON DOCKER

### Paso 1: Verifica que n8n está corriendo

```bash
docker ps | grep n8n
```

Debe mostrar un contenedor activo.

### Paso 2: Inicia Django

```bash
python manage.py runserver
```

### Paso 3: Ejecuta la prueba

```bash
python edunuñez/test_n8n_webhook.py
```

### Paso 4: Verifica los logs

**Docker:**
```bash
docker logs <CONTAINER_ID> -f
```

**Django:**
Deberías ver:
```
Enviando resultado de actividad al webhook de n8n
Respuesta del webhook n8n: Status=200
```

---

## 🆘 DEBUGGING AVANZADO

### Ver logs del contenedor n8n

```bash
docker logs <CONTAINER_ID> --tail 50
```

### Conectar bash al contenedor n8n

```bash
docker exec -it <CONTAINER_ID> /bin/bash

# Dentro del contenedor, probar:
curl http://localhost:5678
```

### Verificar puertos mapeados

```bash
docker port <CONTAINER_ID>
```

Resultado esperado:
```
5678/tcp -> 0.0.0.0:5678
```

---

## 📞 RESUMEN RÁPIDO

| Pregunta | Respuesta |
|----------|-----------|
| ¿Dónde corre n8n? | En Docker |
| ¿Dónde corre Django? | En host (tu PC) |
| ¿URL correcta? | `http://localhost:5678/webhook/Alumnos_settings` |
| ¿Timeout? | Aumentar a 30 segundos |
| ¿Si Django fuera Docker? | Usar `http://n8n:5678` |

---

## 🎯 PRÓXIMO PASO

1. Verifica que `docker ps | grep n8n` muestre el contenedor
2. Ejecuta: `curl http://localhost:5678`
3. Si funciona, ejecuta: `python edunuñez/test_n8n_webhook.py`
4. Revisa los logs en ambas partes

**¡Debería funcionar! 🚀**
