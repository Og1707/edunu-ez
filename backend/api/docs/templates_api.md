# API Documentation - Sistema de Plantillas de Actividades
## Paso 4: Endpoints REST Completos

### Base URL: `/api/`

---

## 📋 **Gestión de Plantillas**

### `GET /api/plantillas/`
**Listar todas las plantillas disponibles**

**Response:**
```json
{
  "plantillas": {
    "multimedia": {
      "nombre": "Actividad Multimedia",
      "descripcion": "Actividades con video/imagen y preguntas interactivas",
      "requiere_archivo": true,
      "tipos_archivo": ["image", "video", "audio"],
      "max_tamaño_mb": 100,
      "preguntas_requeridas": true,
      "min_preguntas": 1,
      "max_preguntas": 20
    },
    "texto": {
      "nombre": "Actividad de Texto",
      "descripcion": "Actividades basadas en texto con tiempo límite",
      "requiere_archivo": false,
      "tiempo_limite_opcional": true,
      "min_tiempo": 5,
      "max_tiempo": 180,
      "preguntas_requeridas": true,
      "min_preguntas": 1,
      "max_preguntas": 50
    },
    "legacy": {
      "nombre": "Actividad Heredada",
      "descripcion": "Formato tradicional de actividades",
      "requiere_archivo": false,
      "preguntas_requeridas": false
    }
  },
  "total": 3
}
```

---

### `GET /api/plantillas/preview/`
**Previsualizar estructura de actividad multimedia**

**Query Parameters:**
- `titulo` (string): Título de ejemplo
- `descripcion` (string): Descripción de ejemplo  
- `preguntas` (string): JSON de preguntas

**Response:**
```json
{
  "valido": true,
  "mensaje": "Estructura válida",
  "preview": { ... },
  "preguntas_count": 3,
  "opciones_total": 9
}
```

---

## 🎬 **Creación de Actividades Multimedia**

### `POST /api/actividades-multimedia/`
**Crear actividad multimedia con archivo**

**Request:** `multipart/form-data`
- `titulo` (string): Título de la actividad
- `descripcion` (string): Descripción
- `curso` (integer): ID del curso
- `preguntas` (string): JSON de preguntas y opciones
- `archivo_multimedia` (file): Archivo (image/video/audio)

**Response:**
```json
{
  "mensaje": "Actividad multimedia creada exitosamente",
  "actividad": {
    "id": 1,
    "titulo": "Actividad Multimedia Test",
    "template_type": "multimedia",
    "multimedia": {
      "archivo_url_cloudinary": "https://cloudinary.com/...",
      "tipo_archivo": "video",
      "duracion_segundos": 120
    },
    "preguntas": [...]
  },
  "cloudinary_info": { ... }
}
```

---

## 📝 **Creación de Actividades de Texto**

### `POST /api/actividades-texto/`
**Crear actividad de texto con tiempo límite**

**Request:** `application/json`
```json
{
  "titulo": "Actividad de Matemáticas",
  "descripcion": "Ejercicios de suma básica",
  "curso": 1,
  "tiempo_limite_minutos": 30,
  "preguntas": [
    {
      "enunciado": "¿Cuánto es 2 + 2?",
      "orden": 1,
      "opciones": [
        {"texto": "3", "es_correcta": false, "orden": 1},
        {"texto": "4", "es_correcta": true, "orden": 2},
        {"texto": "5", "es_correcta": false, "orden": 3}
      ]
    }
  ]
}
```

---

## 🔍 **Búsqueda y Gestión**

### `GET /api/actividades/buscar/`
**Buscar actividades con filtros**

**Query Parameters:**
- `q` (string): Término de búsqueda
- `template_type` (string): multimedia/texto/legacy
- `curso_id` (integer): ID del curso
- `page` (integer): Número de página

**Response (paginado):**
```json
{
  "count": 25,
  "next": "http://api/actividades/buscar/?page=2",
  "previous": null,
  "results": [...],
  "query": "matemáticas",
  "filtros": {
    "template_type": "texto",
    "curso_id": "1"
  }
}
```

### `POST /api/actividades/{id}/duplicar/`
**Duplicar una actividad existente**

**Response:**
```json
{
  "mensaje": "Actividad duplicada exitosamente",
  "actividad_original": { ... },
  "nueva_actividad": { ... }
}
```

---

## 📊 **Gestión de Preguntas**

### `POST /api/actividades/{actividad_id}/preguntas/`
**Agregar pregunta a actividad existente**

**Request:** `application/json`
```json
{
  "enunciado": "Nueva pregunta",
  "orden": 2,
  "opciones": [
    {"texto": "Opción A", "es_correcta": false, "orden": 1},
    {"texto": "Opción B", "es_correcta": true, "orden": 2}
  ]
}
```

### `DELETE /api/preguntas/{pregunta_id}/eliminar/`
**Eliminar pregunta específica**

---

## 📈 **Estadísticas y Utilidades**

### `GET /api/plantillas/estadisticas/`
**Estadísticas de uso de plantillas (solo admin)**

**Response:**
```json
{
  "generales": {
    "total_actividades": 150,
    "total_preguntas": 1200,
    "total_opciones": 3600,
    "promedio_preguntas_por_actividad": 8.0,
    "promedio_opciones_por_pregunta": 3.0
  },
  "por_tipo_plantilla": {
    "multimedia": 45,
    "texto": 85,
    "legacy": 20
  },
  "actividades_ultimos_6_meses": [
    {"month": "2026-01", "count": 25},
    {"month": "2026-02", "count": 30}
  ]
}
```

### `GET /api/cloudinary/firma/`
**Obtener firma para uploads directos**

**Response:**
```json
{
  "signature": "abc123...",
  "timestamp": "1672531200",
  "api_key": "your_api_key",
  "cloud_name": "your_cloud_name"
}
```

---

## 🔗 **Endpoints Existentes (Integrados)**

### `GET /api/actividades/{id}/completo/`
**Obtener actividad completa con preguntas**

### `GET /api/actividades/por-plantilla/`
**Filtrar actividades por tipo de plantilla**

---

## 🔐 **Autenticación y Permisos**

- **JWT Authentication**: Header `Authorization: Bearer <token>`
- **Session Authentication**: Cookies de sesión Django

**Permisos por rol:**
- **Profesor**: Crear/editar sus actividades, ver sus cursos
- **Administrador**: CRUD completo, estadísticas, todas las actividades
- **Estudiante**: Solo ver actividades asignadas

---

## 📝 **Formato de Preguntas**

### Estructura JSON para preguntas:
```json
{
  "enunciado": "Texto de la pregunta",
  "orden": 1,
  "opciones": [
    {
      "texto": "Opción 1",
      "es_correcta": false,
      "orden": 1
    },
    {
      "texto": "Opción 2", 
      "es_correcta": true,
      "orden": 2
    }
  ]
}
```

**Reglas de validación:**
- Mínimo 2 opciones por pregunta
- Exactamente 1 opción correcta
- Orden obligatorio para preguntas y opciones

---

## 🚀 **Próximos Pasos**

**Paso 5:** Componentes React
- `TemplateSelector.jsx` - Selector de plantillas
- `MultimediaActivityForm.jsx` - Formulario multimedia
- `TextActivityForm.jsx` - Formulario de texto
- `ActivityPreview.jsx` - Previsualización

**Paso 6:** Integración en `AddActivity.jsx`
- Integración con sistema existente
- Gestión de estado
- Navegación entre plantillas
