# Solución: n8n en Docker + Problemas de Conectividad

## La Respuesta a tu Pregunta

**¿Puede afectar que n8n esté en Docker?**

**SÍ, DEFINITIVAMENTE.**

El error que estás viendo puede ser causado por:
1. Problemas de networking entre Docker y tu host
2. URL incorrecta en la configuración
3. Firewall de Windows bloqueando
4. Puerto mapeado incorrectamente

---

## 🎯 SOLUCIONES RÁPIDAS

### Solución 1: Verificar la URL (3 minutos)

Abre `api/webhooks.py` y verifica:

```python
WEBHOOKS_CONFIG = {
    'n8n_alumnos': {
        'url': 'http://localhost:5678/webhook/Alumnos_settings',
        # ↑ Esta debe ser la URL correcta
        'timeout': 10,
        'retry_attempts': 3,
        'enabled': True
    }
}
```

Si n8n está en Docker:
- ✅ `localhost:5678` funciona si Docker Desktop está corriendo
- ⚠️ Si el puerto es diferente (ej: 5679), cambiar aquí también

---

### Solución 2: Verificar que el Puerto está Mapeado (2 minutos)

```bash
docker ps | grep n8n
```

Deberías ver:
```
PORTS                    
0.0.0.0:5678->5678/tcp   ← El puerto DEBE estar mapeado así
```

Si no está así o no aparece n8n:
```bash
# Iniciar n8n correctamente
docker run -d -p 5678:5678 n8n
```

---

### Solución 3: Firewall de Windows (5 minutos)

Si tu Django no puede conectar a n8n:

**Opción A: Permitir Python en Firewall**
1. Windows Defender Firewall → Permitir aplicación
2. Busca Python → Marcar público y privado
3. OK

**Opción B: Permitir puerto 5678**
1. Reglas de entrada → Nueva regla
2. Puerto → TCP 5678
3. Permitir

---

### Solución 4: Diagnosticar Automáticamente

Ejecuta este script que creé para ti:

```bash
python edunuñez/diagnose_n8n_docker.py
```

Este script verifica:
- ✅ Docker instalado
- ✅ n8n corriendo
- ✅ Puerto mapeado
- ✅ Acceso desde navegador
- ✅ Acceso desde Django
- ✅ Webhook existe
- ✅ Configuración correcta
- ✅ Test de conexión

---

## 📊 ESCENARIOS COMUNES

### Escenario 1: n8n en Docker, Django en Host (TU CASO)

**Configuración correcta:**
```python
'url': 'http://localhost:5678/webhook/Alumnos_settings'
```

**Docker:**
```bash
docker run -d -p 5678:5678 n8n
```

**Resultado:**
- ✅ Funcionará correctamente

---

### Escenario 2: n8n en Docker, pero no veo el puerto

**Problema:**
```bash
$ docker ps | grep n8n
$ (sin output)
```

**Solución:**
```bash
# El contenedor no está corriendo, iniciarlo
docker run -d -p 5678:5678 n8n

# Verificar
docker ps | grep n8n
```

---

### Escenario 3: El puerto está mapeado a otro número

**Problema:**
```bash
$ docker ps | grep n8n
... 0.0.0.0:5679->5678/tcp ...
```

**Solución:**
Cambiar en `webhooks.py`:
```python
'url': 'http://localhost:5679/webhook/Alumnos_settings',  # Puerto 5679
```

---

### Escenario 4: Firewall bloqueando

**Síntoma:**
```
ConnectionError: [Errno 111] Connection refused
```

**Solución:**
Permitir Python en Windows Firewall (ver Solución 3 arriba)

---

## 🔍 VERIFICACION PASO A PASO

### Paso 1: ¿Está n8n corriendo?

```bash
docker ps | grep n8n
```

**Esperado:** Ver el contenedor

**Si no:** `docker run -d -p 5678:5678 n8n`

---

### Paso 2: ¿El puerto está mapeado correctamente?

```bash
docker port <CONTAINER_ID>
```

**Esperado:** `5678/tcp -> 0.0.0.0:5678`

---

### Paso 3: ¿Puedo acceder desde navegador?

```
http://localhost:5678
```

**Esperado:** Ver la UI de n8n

---

### Paso 4: ¿Configuración correcta en Django?

```python
# api/webhooks.py
'url': 'http://localhost:5678/webhook/Alumnos_settings'
```

**Esperado:** URL coincida con el paso anterior

---

### Paso 5: ¿El webhook existe en n8n?

En n8n:
1. Tu flujo
2. Nodo "Webhook"
3. Path debe ser: `Alumnos_settings`
4. Flujo debe estar activo (toggle verde)

---

### Paso 6: Ejecutar diagnóstico

```bash
python edunuñez/diagnose_n8n_docker.py
```

**Esperado:** Todos los checks pasen

---

## 📚 DOCUMENTACIÓN COMPLETA

Si necesitas más detalles:

1. **Para networking en Docker:**
   → Abre `N8N_DOCKER_NETWORKING.md`

2. **Para diagnosticar problemas:**
   → Abre `N8N_DOCKER_DIAGNOSTICO.md`

3. **Para ver toda la configuración:**
   → Abre `N8N_FLUJO_CORREGIDO.md` (si existe)

---

## ✅ CHECKLIST FINAL

- [ ] `docker ps | grep n8n` muestra el contenedor
- [ ] Puerto 5678 está mapeado
- [ ] Puedo acceder a `http://localhost:5678` en navegador
- [ ] URL en `webhooks.py` es `http://localhost:5678/webhook/Alumnos_settings`
- [ ] Webhook existe en n8n con ruta `Alumnos_settings`
- [ ] Flujo n8n está activo (toggle verde)
- [ ] Python está permitido en Firewall de Windows
- [ ] Ejecuté `diagnose_n8n_docker.py` sin errores

Si todos tienen ✅, ejecuta:
```bash
python edunuñez/test_n8n_webhook.py
```

---

## 🎯 PRÓXIMO PASO

1. Ejecuta: `python edunuñez/diagnose_n8n_docker.py`
2. Comparte el output conmigo si hay errores
3. Una vez que el diagnóstico pase, ejecuta: `python edunuñez/test_n8n_webhook.py`

**Debería mostrar:**
```
Total: 6/6 tests exitosos
Exito: TODOS LOS TESTS PASARON!
```

---

**¡La solución está en el diagnóstico automático! 🚀**
