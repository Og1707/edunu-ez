import api from './api';

// El interceptor en api.js adjunta automáticamente el header Authorization: Bearer <token>
// para todas las requests. No se necesita enviar user_id explícito.

export const getTeacherActivities = () => api.get('/api/actividades/profesor/');
export const getCourses = () => api.get('/api/cursos/');
export const getActivityTypes = () => api.get('/api/tipos-actividad/');
export const getCourseStudents = (cursoId) => api.get(`/api/estudiantes-curso/?curso_id=${cursoId}`);
export const assignActivityToCourse = (data) => api.post('/api/asignar-actividad-curso/', data);
export const addStudentToCourse = (data) => api.post('/api/estudiantes-curso/agregar/', data);
export const updateActivity = (actividadId, formData) => api.put(`/api/actividades/${actividadId}/gestionar/`, formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});
export const deleteActivity = (actividadId) => api.delete(`/api/actividades/${actividadId}/gestionar/`);
export const createActivity = (activityData, config) => api.post('/api/actividades/', activityData, config);
export const getScienceSubjects = () => api.get('/api/ciencias/materias/');

// ============= SERVICIOS PARA PLANTILLAS =============

/**
 * Crear una nueva actividad multimedia con preguntas
 * @param {FormData} formData - Datos multipart: archivo, titulo, descripcion, preguntas (JSON)
 * @returns {Promise} Respuesta con actividad creada
 */
export const createMultimediaActivity = (formData) =>
  api.post('/api/actividades/crear-multimedia/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

/**
 * Crear una nueva actividad de texto con preguntas
 * @param {Object} data - JSON con titulo, descripcion, tiempo_limite_minutos, preguntas
 * @returns {Promise} Respuesta con actividad creada
 */
export const createTextActivity = (data) =>
  api.post('/api/actividades/crear-texto/', data);

/**
 * Obtener una actividad completa con todas sus preguntas y opciones
 * @param {number} actividadId - ID de la actividad
 * @returns {Promise} Respuesta con actividad completa
 */
export const getCompleteActivity = (actividadId) =>
  api.get('/api/actividades/completa/', { params: { actividad_id: actividadId } });

/**
 * Obtener actividades filtradas por tipo de plantilla
 * @param {string} templateType - Tipo: 'multimedia' o 'texto'
 * @returns {Promise} Array de actividades del tipo especificado
 */
export const getActivitiesByTemplate = (templateType) =>
  api.get('/api/actividades/por-plantilla/', { params: { template_type: templateType } });

/**
 * Agregar una pregunta a una actividad existente
 * @param {number} actividadId - ID de la actividad
 * @param {Object} questionData - Datos: enunciado, opciones (array)
 * @returns {Promise} Respuesta con pregunta agregada
 */
export const addQuestionToActivity = (actividadId, questionData) =>
  api.post(`/api/actividades/${actividadId}/preguntas/`, questionData);

/**
 * Eliminar una pregunta de una actividad
 * @param {number} preguntaId - ID de la pregunta a eliminar
 * @returns {Promise} Respuesta de confirmación
 */
export const deleteQuestion = (preguntaId) =>
  api.delete(`/api/preguntas/${preguntaId}/eliminar/`);

/**
 * Obtener firma para upload directo a Cloudinary (client-side)
 * @returns {Promise} Objeto con { signature, timestamp, cloudinaryName, uploadPreset }
 */
export const getCloudinarySignature = () =>
  api.get('/api/cloudinary/firma/');

// ============= SERVICIOS LEGACY (Mantener por compatibilidad) =============
export const getTemplates = () => api.get('/api/plantillas/');
export const previewMultimediaTemplate = (data) => api.get('/api/plantillas/preview/', { params: data });
export const duplicateActivity = (actividadId) => api.post(`/api/actividades/${actividadId}/duplicar/`);
export const searchActivities = (params) => api.get('/api/actividades/buscar/', { params });
