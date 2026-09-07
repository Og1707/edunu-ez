# Arquitectura del Frontend — EduNúñez

> Documentación técnica del frontend React de la plataforma educativa EduNúñez.  
> Generada automáticamente a partir del análisis del código fuente (septiembre 2026).

---

## Tabla de contenido

1. [Stack tecnológico](#1-stack-tecnológico)
2. [Estructura de directorios](#2-estructura-de-directorios)
3. [Punto de entrada](#3-punto-de-entrada)
4. [Enrutamiento — App.js](#4-enrutamiento--appjs)
5. [Páginas (pages/)](#5-páginas-pages)
6. [Features (features/)](#6-features-features)
7. [Componentes reutilizables (components/)](#7-componentes-reutilizables-components)
8. [Servicios HTTP (services/)](#8-servicios-http-services)
9. [Hooks personalizados (hooks/)](#9-hooks-personalizados-hooks)
10. [Utilidades (utils/)](#10-utilidades-utils)
11. [Estilos (styles/)](#11-estilos-styles)
12. [Flujo de autenticación](#12-flujo-de-autenticación)
13. [Diagrama de conexiones](#13-diagrama-de-conexiones)
14. [Mapeo de endpoints API](#14-mapeo-de-endpoints-api)

---

## 1. Stack tecnológico

| Tecnología | Versión | Rol |
|---|---|---|
| React | ^19.1.0 | Framework UI |
| React Router DOM | ^6.30.1 | Enrutamiento SPA |
| Axios | ^1.12.2 | Cliente HTTP |
| React Scripts (CRA) | 5.0.1 | Build toolchain |
| @testing-library/react | ^16.3.0 | Testing |

Sin Redux ni Context API: el estado se maneja localmente con `useState`/`useEffect` y con `localStorage` para la sesión de usuario.

---

## 2. Estructura de directorios

```
frontend/
├── public/                     # Archivos estáticos públicos (HTML raíz, íconos)
└── src/
    ├── index.js                # Punto de entrada React
    ├── index.css               # Estilos base globales
    ├── App.js                  # Router raíz con todas las rutas
    ├── App.test.js
    ├── reportWebVitals.js
    ├── setupTests.js
    │
    ├── pages/                  # Vistas de nivel ruta (páginas completas)
    │   ├── Home.jsx / .css
    │   ├── Login.jsx / .css
    │   ├── Register.jsx / .css
    │   ├── Dashboard.jsx / .css
    │   ├── MagicLink.jsx
    │   └── VerifyMagicLink.jsx
    │
    ├── features/               # Módulos de dominio (secciones del dashboard)
    │   ├── activities/
    │   │   ├── ActivityManagement.jsx / .css
    │   │   ├── AddActivity.jsx / .css
    │   │   └── StudentActivities.jsx / .css
    │   ├── courses/
    │   │   └── CourseManagement.jsx / .css
    │   ├── games/
    │   │   ├── GameExplorer.jsx / .css
    │   │   ├── ColorGame.jsx / .css
    │   │   └── ScienceQuizGame.jsx / .css
    │   └── users/
    │       └── UserManagement.jsx / .css
    │
    ├── components/             # Componentes reutilizables (atoms/molecules)
    │   ├── TemplateSelector.jsx / .css
    │   ├── MultimediaActivityForm.jsx / .css
    │   ├── TextActivityForm.jsx / .css
    │   ├── ActivityPreview.jsx / .css
    │   ├── QuestionForm.jsx / .css
    │   ├── OptionForm.jsx / .css
    │   └── MagicLinkForm.jsx
    │
    ├── services/               # Capa HTTP (abstracción de la API REST)
    │   ├── api.js              # Instancia Axios + interceptores
    │   ├── auth.service.js
    │   ├── activities.service.js
    │   ├── courses.service.js
    │   ├── games.service.js
    │   ├── users.service.js
    │   └── wiki.service.js
    │
    ├── hooks/
    │   └── useAuth.js          # Hook para leer la sesión del localStorage
    │
    ├── utils/
    │   └── axiosConfig.js      # Re-exportación legacy de api.js (deprecado)
    │
    └── styles/
        ├── global.css          # Variables y estilos globales (~104 KB)
        └── variables.css       # Variables CSS (colores, tipografía, spacing)
```

---

## 3. Punto de entrada

**`src/index.js`**  
Monta la aplicación React en el nodo `#root` del `public/index.html`. Importa el CSS global (`index.css`, `styles/global.css`) y renderiza `<App />` dentro de `<React.StrictMode>`.

---

## 4. Enrutamiento — App.js

`App.js` define todas las rutas de la SPA usando `BrowserRouter` y `Routes` de React Router v6.

| Ruta | Componente | Descripción |
|---|---|---|
| `/` | `Home` | Página de aterrizaje pública |
| `/register` | `Register` | Formulario de registro de usuario |
| `/login` | `Login` | Inicio de sesión email + contraseña |
| `/magic-link` | `MagicLink` | Solicitud de magic link |
| `/verify` | `VerifyMagicLink` | Verificación de token magic link |
| `/dashboard` | `Dashboard` | Panel principal (requiere auth) |
| `/courses` | `CourseManagement` | Gestión de cursos |
| `/activities` | `ActivityManagement` | Gestión de actividades |
| `/users` | `UserManagement` | Gestión de usuarios |
| `/games` | `GameExplorer` | Explorador de juegos educativos |

No hay rutas protegidas mediante wrappers: cada página verifica `localStorage.getItem('user')` y redirige con `useNavigate` si la sesión no existe.

---

## 5. Páginas (pages/)

### `Home.jsx`
Página de bienvenida pública. Muestra la propuesta de valor de EduNúñez con links a `/login` y `/register`.

### `Login.jsx`
- Formulario de login con email y contraseña.
- Llama a `auth.service.login()` → `POST /api/login/`.
- Al autenticarse exitosamente guarda el objeto de respuesta en `localStorage('user')` y navega a `/dashboard`.
- Incluye enlace hacia `/magic-link` como opción alternativa.

### `Register.jsx`
- Formulario de registro de nuevos usuarios.
- Llama a `auth.service.register()` → `POST /api/registro/`.
- Redirige a `/login` tras el registro exitoso.

### `MagicLink.jsx`
Página simple que renderiza el componente `MagicLinkForm`. Permite solicitar un enlace de acceso sin contraseña.

### `VerifyMagicLink.jsx`
- Lee el parámetro `?token=...` de la URL.
- Hace `fetch` a `GET /auth/magic-link/verify/?token=...` (nota: usa `fetch` nativo, no Axios).
- Si el token es válido, guarda `access` en `sessionStorage('AUTH_TOKEN')` y redirige a `/dashboard`.
- Si falla, muestra el mensaje de error del API.

### `Dashboard.jsx`
Panel principal de la aplicación. Es el hub central tras el login.

**Funcionalidades:**
- Lee `localStorage('user')` para obtener datos del usuario; redirige a `/login` si no existe.
- Renderiza una barra de navegación lateral con secciones dinámicas.
- Controla qué sección mostrar con el estado `activeSection`.
- Renderiza condicionalmente los features según el rol del usuario:
  - `AddActivity` (modal flotante)
  - `UserManagement`
  - `CourseManagement`
  - `ActivityManagement`
  - `StudentActivities`
- Botón de logout limpia `localStorage` y navega a `/`.

---

## 6. Features (features/)

Los features son módulos de dominio que encapsulan una sección completa del dashboard. Reciben `user` como prop desde `Dashboard`.

### `features/activities/ActivityManagement.jsx`
Gestión de actividades para el profesor/administrador.

**Responsabilidades:**
- Carga actividades del profesor (`GET /api/actividades/profesor/`).
- Lista cursos y tipos de actividad disponibles.
- Permite editar actividades con modal (`PUT /api/actividades/:id/gestionar/`).
- Permite eliminar actividades (`DELETE /api/actividades/:id/gestionar/`).
- Permite asignar una actividad a uno o varios estudiantes de un curso (`POST /api/asignar-actividad-curso/`).
- Filtros por curso, tipo y búsqueda de texto.

**Servicios usados:** `activities.service` → `getTeacherActivities`, `getCourses`, `getActivityTypes`, `getCourseStudents`, `assignActivityToCourse`, `addStudentToCourse`, `updateActivity`, `deleteActivity`.

---

### `features/activities/AddActivity.jsx`
Flujo de creación de actividades con soporte de plantillas. Es un modal/overlay lanzado desde `Dashboard`.

**Flujo de pasos (wizard):**
1. `template-selection` — El usuario selecciona una plantilla usando `TemplateSelector`.
2. `form` — Dependiendo de la plantilla elegida se renderiza:
   - `MultimediaActivityForm` (para plantillas multimedia)
   - `TextActivityForm` (para plantillas de texto)
   - Formulario legacy para actividades básicas
3. `preview` — `ActivityPreview` muestra la actividad antes de guardar.

**También contiene:**
- Integración con `ScienceQuizGame` y `GameExplorer` para actividades tipo juego.
- Carga de materias de ciencias (`getScienceSubjects`).

**Servicios usados:** `activities.service` → `createActivity`, `createMultimediaActivity`, `createTextActivity`, `getCourses`, `getActivityTypes`, `getScienceSubjects`, `assignActivityToCourse`.

---

### `features/activities/StudentActivities.jsx`
Vista de actividades para el rol estudiante.

**Responsabilidades:**
- Carga actividades asignadas al estudiante (`GET /api/estudiante/actividades/`).
- Carga estadísticas de progreso (`GET /api/estudiante/estadisticas/`).
- Permite filtrar actividades por estado (pendiente, en progreso, completada).
- Permite iniciar (`POST /api/estudiante/actividades/iniciar/`) y completar (`POST /api/estudiante/actividades/completar/`) actividades.
- Integra `ColorGame` cuando la actividad es de tipo juego de colores.

**Servicios usados:** `axiosConfig` (legacy) con llamadas directas + `games.service` → `startStudentActivity`, `completeStudentActivity`.

---

### `features/courses/CourseManagement.jsx`
Gestión de cursos (CRUD completo).

**Responsabilidades:**
- Lista todos los cursos (`GET /api/cursos/`).
- Crea nuevos cursos con modal (`POST /api/cursos/crear/`).
- Edita cursos existentes (`PUT /api/cursos/:id/gestionar/`).
- Elimina cursos (`DELETE /api/cursos/:id/gestionar/`).
- Gestiona estudiantes inscritos en un curso:
  - Listar estudiantes (`GET /api/estudiantes-curso/?curso_id=...`)
  - Agregar estudiante (`POST /api/estudiantes-curso/agregar/`)
  - Remover estudiante (`DELETE /api/estudiantes-curso/:id/remover/`)
- Si el usuario es administrador, carga la lista de profesores disponibles.

**Servicios usados:** `courses.service` → todos los exports.

---

### `features/users/UserManagement.jsx`
Gestión de usuarios (CRUD) para administrador/profesor.

**Responsabilidades:**
- Lista todos los usuarios (`GET /api/usuarios/listar/`).
- Crea nuevos usuarios con rol asignable (`POST /api/usuarios/crear/`).
- Edita usuarios (`PUT /api/usuarios/:id/gestionar/`).
- Elimina usuarios (`DELETE /api/usuarios/:id/gestionar/`).

**Servicios usados:** `users.service` → `listUsers`, `createUser`, `updateUser`, `deleteUser`.

---

### `features/games/GameExplorer.jsx`
Explorador de juegos educativos disponibles en la plataforma.

**Responsabilidades:**
- Carga categorías de juegos (`GET /api/juegos/categorias/`).
- Carga juegos con filtros por categoría, edad y dificultad (`GET /api/juegos/listar/`).
- Al seleccionar un juego lo pasa hacia arriba via `onGameSelect`.

---

### `features/games/ColorGame.jsx`
Juego interactivo de identificación de colores. Componente standalone que contiene su propia lógica de juego.

---

### `features/games/ScienceQuizGame.jsx`
Quiz de ciencias naturales integrado en el flujo de creación de actividades.

---

## 7. Componentes reutilizables (components/)

### `TemplateSelector.jsx`
Selector de plantillas para crear actividades. Carga las plantillas disponibles desde `GET /api/plantillas/` y emite el template seleccionado via `onTemplateSelect(templateKey, template)`.

### `MultimediaActivityForm.jsx`
Formulario para crear actividades de tipo multimedia. Gestiona:
- Upload de archivo multimedia (video, audio o imagen).
- Título, descripción, tiempo límite.
- Lista dinámica de preguntas y opciones usando `QuestionForm` y `OptionForm`.
- Llama a `createMultimediaActivity()` → `POST /api/actividades/crear-multimedia/` con `multipart/form-data`.

### `TextActivityForm.jsx`
Formulario para crear actividades de texto. Similar a `MultimediaActivityForm` pero sin archivo. Llama a `createTextActivity()` → `POST /api/actividades/crear-texto/`.

### `ActivityPreview.jsx`
Vista previa de una actividad antes de guardarla o al consultarla. Renderiza el contenido, las preguntas y opciones con sus estados. Carga datos via `getCompleteActivity()` → `GET /api/actividades/completa/`.

### `QuestionForm.jsx`
Formulario de una pregunta individual dentro de una actividad. Maneja el enunciado y la lista de opciones delegando a `OptionForm`.

### `OptionForm.jsx`
Formulario de una sola opción de respuesta. Permite marcarla como correcta. Es el componente hoja del sistema de preguntas.

### `MagicLinkForm.jsx`
Formulario para solicitar un magic link por email. Usado en la página `MagicLink.jsx`.

---

## 8. Servicios HTTP (services/)

### `api.js` — Instancia Axios central

```
baseURL: process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000'
```

**Interceptor de request:**  
Lee `localStorage('user')`, extrae `user.token` y lo adjunta como `Authorization: Bearer <token>` en todas las requests salientes (si no hay ya uno).

**Interceptor de response:**  
Captura errores 401 y emite `console.warn`. No hace logout automático; eso lo maneja cada componente.

---

### `auth.service.js`

| Función | Método | Endpoint |
|---|---|---|
| `login(credentials)` | POST | `/api/login/` |
| `register(data)` | POST | `/api/registro/` |

---

### `activities.service.js`

| Función | Método | Endpoint |
|---|---|---|
| `getTeacherActivities()` | GET | `/api/actividades/profesor/` |
| `getCourses()` | GET | `/api/cursos/` |
| `getActivityTypes()` | GET | `/api/tipos-actividad/` |
| `getCourseStudents(cursoId)` | GET | `/api/estudiantes-curso/?curso_id=...` |
| `assignActivityToCourse(data)` | POST | `/api/asignar-actividad-curso/` |
| `addStudentToCourse(data)` | POST | `/api/estudiantes-curso/agregar/` |
| `updateActivity(id, formData)` | PUT | `/api/actividades/:id/gestionar/` |
| `deleteActivity(id)` | DELETE | `/api/actividades/:id/gestionar/` |
| `createActivity(data, config)` | POST | `/api/actividades/` |
| `getScienceSubjects()` | GET | `/api/ciencias/materias/` |
| `createMultimediaActivity(formData)` | POST | `/api/actividades/crear-multimedia/` |
| `createTextActivity(data)` | POST | `/api/actividades/crear-texto/` |
| `getCompleteActivity(id)` | GET | `/api/actividades/completa/?actividad_id=...` |
| `getActivitiesByTemplate(type)` | GET | `/api/actividades/por-plantilla/?template_type=...` |
| `addQuestionToActivity(id, data)` | POST | `/api/actividades/:id/preguntas/` |
| `deleteQuestion(id)` | DELETE | `/api/preguntas/:id/eliminar/` |
| `getCloudinarySignature()` | GET | `/api/cloudinary/firma/` |
| `getTemplates()` | GET | `/api/plantillas/` |
| `previewMultimediaTemplate(data)` | GET | `/api/plantillas/preview/` |
| `duplicateActivity(id)` | POST | `/api/actividades/:id/duplicar/` |
| `searchActivities(params)` | GET | `/api/actividades/buscar/` |

---

### `courses.service.js`

| Función | Método | Endpoint |
|---|---|---|
| `getCourses()` | GET | `/api/cursos/` |
| `getUsers()` | GET | `/api/usuarios/listar/` |
| `createCourse(data)` | POST | `/api/cursos/crear/` |
| `updateCourse(id, data)` | PUT | `/api/cursos/:id/gestionar/` |
| `deleteCourse(id)` | DELETE | `/api/cursos/:id/gestionar/` |
| `getCourseStudents(id)` | GET | `/api/estudiantes-curso/?curso_id=...` |
| `addStudentToCourse(data)` | POST | `/api/estudiantes-curso/agregar/` |
| `removeStudentFromCourse(id)` | DELETE | `/api/estudiantes-curso/:id/remover/` |

---

### `games.service.js`

| Función | Método | Endpoint |
|---|---|---|
| `getGameCategories()` | GET | `/api/juegos/categorias/` |
| `getGames(params)` | GET | `/api/juegos/listar/` |
| `startStudentActivity(data)` | POST | `/api/estudiante/actividades/iniciar/` |
| `completeStudentActivity(data)` | POST | `/api/estudiante/actividades/completar/` |
| `getStudentActivities()` | GET | `/api/estudiante/actividades/` |
| `getStudentStats()` | GET | `/api/estudiante/estadisticas/` |

---

### `users.service.js`

| Función | Método | Endpoint |
|---|---|---|
| `listUsers()` | GET | `/api/usuarios/listar/` |
| `createUser(data)` | POST | `/api/usuarios/crear/` |
| `updateUser(id, data)` | PUT | `/api/usuarios/:id/gestionar/` |
| `deleteUser(id)` | DELETE | `/api/usuarios/:id/gestionar/` |

---

### `wiki.service.js`
Servicio para consultar contenido de Wikipedia (pendiente de implementación detallada). Conecta con `GET /api/wikipedia/...`.

---

## 9. Hooks personalizados (hooks/)

### `useAuth.js`

```js
const { user, logout } = useAuth();
```

- Lee y parsea `localStorage('user')` en el estado `user`.
- Escucha el evento `storage` para detectar cambios de sesión entre pestañas.
- `logout()` limpia `localStorage` y pone `user` en `null`.
- Nota: La mayoría de componentes leen el localStorage directamente; `useAuth` existe como abstracción pero no se usa extensivamente todavía.

---

## 10. Utilidades (utils/)

### `axiosConfig.js` _(deprecado)_

```js
// Re-exporta api.js para mantener compatibilidad con imports legacy
import api from '../services/api';
export default api;
```

Los componentes en `features/` todavía importan desde `../../utils/axiosConfig` en lugar de `../../services/api`. Ambos apuntan a la misma instancia.

---

## 11. Estilos (styles/)

- **`variables.css`**: Define las variables CSS del design system (colores, tipografía, espaciado, border-radius, etc.).
- **`global.css`**: Estilos globales de la aplicación, resets, clases utilitarias y estilos de componentes compartidos (~104 KB).
- Cada página/feature/component tiene su propio archivo `.css` colocado junto al `.jsx`.

---

## 12. Flujo de autenticación

### Login tradicional (email + contraseña)

```
Usuario → Login.jsx
  → auth.service.login()  →  POST /api/login/
  ← { token, usuario_id, rol, nombre, ... }
  → localStorage.setItem('user', JSON.stringify(response.data))
  → navigate('/dashboard')

Dashboard.jsx
  → JSON.parse(localStorage.getItem('user'))
  → Renderiza secciones según user.rol

api.js interceptor
  → Lee localStorage('user').token
  → Adjunta Authorization: Bearer <token> en cada request
```

### Magic Link

```
Usuario → MagicLink.jsx → MagicLinkForm.jsx
  → POST /auth/magic-link/  (email)
  ← { message: "Correo enviado" }

  [El usuario recibe email, hace click en el link]

Usuario → VerifyMagicLink.jsx  (?token=XXX)
  → GET /auth/magic-link/verify/?token=XXX  (fetch nativo)
  ← { access, refresh }
  → sessionStorage.setItem('AUTH_TOKEN', access)
  → navigate('/dashboard')
```

### Logout

```
Dashboard.jsx → handleLogout()
  → localStorage.removeItem('user')
  → navigate('/')
```

---

## 13. Diagrama de conexiones

```
index.js
  └── App.js (Router)
        ├── /                → Home.jsx
        ├── /register        → Register.jsx
        │     └── auth.service.register()
        ├── /login           → Login.jsx
        │     └── auth.service.login()
        ├── /magic-link      → MagicLink.jsx
        │     └── MagicLinkForm.jsx
        ├── /verify          → VerifyMagicLink.jsx
        │     └── fetch /auth/magic-link/verify/
        ├── /dashboard       → Dashboard.jsx
        │     ├── [modal]    AddActivity.jsx
        │     │     ├── TemplateSelector.jsx
        │     │     │     └── activities.service.getTemplates()
        │     │     ├── MultimediaActivityForm.jsx
        │     │     │     ├── QuestionForm.jsx
        │     │     │     │     └── OptionForm.jsx
        │     │     │     └── activities.service.createMultimediaActivity()
        │     │     ├── TextActivityForm.jsx
        │     │     │     └── activities.service.createTextActivity()
        │     │     ├── ActivityPreview.jsx
        │     │     │     └── activities.service.getCompleteActivity()
        │     │     ├── ScienceQuizGame.jsx
        │     │     └── GameExplorer.jsx
        │     │           └── api GET /api/juegos/...
        │     ├── [section]  ActivityManagement.jsx
        │     │     └── activities.service.*
        │     ├── [section]  StudentActivities.jsx
        │     │     ├── ColorGame.jsx
        │     │     └── api GET /api/estudiante/...
        │     ├── [section]  CourseManagement.jsx
        │     │     └── courses.service.*
        │     └── [section]  UserManagement.jsx
        │           └── users.service.*
        ├── /courses         → CourseManagement.jsx (standalone)
        ├── /activities      → ActivityManagement.jsx (standalone)
        ├── /users           → UserManagement.jsx (standalone)
        └── /games           → GameExplorer.jsx (standalone)
```

---

## 14. Mapeo de endpoints API

Resumen consolidado de todos los endpoints del backend Django que consume el frontend.

| Dominio | Endpoint | Método(s) | Consumidor frontend |
|---|---|---|---|
| **Auth** | `/api/login/` | POST | `Login.jsx` |
| **Auth** | `/api/registro/` | POST | `Register.jsx` |
| **Auth** | `/auth/magic-link/` | POST | `MagicLinkForm.jsx` |
| **Auth** | `/auth/magic-link/verify/` | GET | `VerifyMagicLink.jsx` |
| **Usuarios** | `/api/usuarios/listar/` | GET | `UserManagement`, `CourseManagement` |
| **Usuarios** | `/api/usuarios/crear/` | POST | `UserManagement` |
| **Usuarios** | `/api/usuarios/:id/gestionar/` | PUT, DELETE | `UserManagement` |
| **Cursos** | `/api/cursos/` | GET | `CourseManagement`, `AddActivity`, `ActivityManagement` |
| **Cursos** | `/api/cursos/crear/` | POST | `CourseManagement` |
| **Cursos** | `/api/cursos/:id/gestionar/` | PUT, DELETE | `CourseManagement` |
| **Cursos** | `/api/estudiantes-curso/` | GET | `CourseManagement`, `ActivityManagement` |
| **Cursos** | `/api/estudiantes-curso/agregar/` | POST | `CourseManagement`, `ActivityManagement` |
| **Cursos** | `/api/estudiantes-curso/:id/remover/` | DELETE | `CourseManagement` |
| **Actividades** | `/api/actividades/` | POST | `AddActivity` |
| **Actividades** | `/api/actividades/profesor/` | GET | `ActivityManagement` |
| **Actividades** | `/api/actividades/:id/gestionar/` | PUT, DELETE | `ActivityManagement` |
| **Actividades** | `/api/actividades/crear-multimedia/` | POST | `MultimediaActivityForm` |
| **Actividades** | `/api/actividades/crear-texto/` | POST | `TextActivityForm` |
| **Actividades** | `/api/actividades/completa/` | GET | `ActivityPreview` |
| **Actividades** | `/api/actividades/por-plantilla/` | GET | `AddActivity` |
| **Actividades** | `/api/actividades/:id/preguntas/` | POST | `MultimediaActivityForm`, `TextActivityForm` |
| **Actividades** | `/api/actividades/:id/duplicar/` | POST | `activities.service` (legacy) |
| **Actividades** | `/api/actividades/buscar/` | GET | `activities.service` |
| **Actividades** | `/api/asignar-actividad-curso/` | POST | `ActivityManagement`, `AddActivity` |
| **Actividades** | `/api/tipos-actividad/` | GET | `ActivityManagement`, `AddActivity` |
| **Preguntas** | `/api/preguntas/:id/eliminar/` | DELETE | `TextActivityForm`, `MultimediaActivityForm` |
| **Plantillas** | `/api/plantillas/` | GET | `TemplateSelector` |
| **Plantillas** | `/api/plantillas/preview/` | GET | `activities.service` (legacy) |
| **Estudiante** | `/api/estudiante/actividades/` | GET | `StudentActivities` |
| **Estudiante** | `/api/estudiante/actividades/iniciar/` | POST | `StudentActivities` |
| **Estudiante** | `/api/estudiante/actividades/completar/` | POST | `StudentActivities` |
| **Estudiante** | `/api/estudiante/estadisticas/` | GET | `StudentActivities` |
| **Juegos** | `/api/juegos/categorias/` | GET | `GameExplorer` |
| **Juegos** | `/api/juegos/listar/` | GET | `GameExplorer` |
| **Ciencias** | `/api/ciencias/materias/` | GET | `AddActivity` |
| **Cloudinary** | `/api/cloudinary/firma/` | GET | `MultimediaActivityForm` |

---

*Documento generado el 7 de septiembre de 2026.*
