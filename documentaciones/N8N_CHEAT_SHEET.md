# 🔥 REFERENCIA RÁPIDA: n8n Error Fix

## El Error
```
Unused Respond to Webhook node found in the workflow
UnicodeEncodeError: 'charmap' codec can't encode character
```

## La Solución (3 PASOS)

### 1. En n8n
```
Elimina: ResponseWebhook
Conecta: Webhook → CodeParse → AI Agent → Code JavaScript1 → Respond to Webhook
```

### 2. Configura Respond to Webhook
```
Status: 200
Body: = $json
```

### 3. Activa el Flujo
```
Toggle VERDE (arriba a la derecha)
```

## Test
```bash
python edunuñez/test_n8n_webhook.py
```

## Resultado
```
TODOS LOS TESTS PASARON!
```

---

**¿Necesitas más detalles?** Lee: [`N8N_SOLUCION_RAPIDA.md`](./N8N_SOLUCION_RAPIDA.md)
