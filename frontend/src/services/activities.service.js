import api from './api';

// El interceptor en api.js adjunta automáticamente el header Authorization: Bearer <token>
// para todas las requests. No se necesita enviar user_id explícito.

export const getTeacherActivities = () => api.get('/api/actividades/profesor/');
export const getActivities = () => api.get('/api/actividades/');
export const getActivityTypes = () => api.get('/api/tipos-actividad/');
export const assignActivityToCourse = (data) => api.post('/api/asignar-actividad-curso/', data);
export const updateActivity = (actividadId, data) => api.put(`/api/actividades/${actividadId}/gestionar/`, data);
export const deleteActivity = (actividadId) => api.delete(`/api/actividades/${actividadId}/gestionar/`);

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
  api.get(`/api/actividades/${actividadId}/completo/`);

export const getTemplates = () => api.get('/api/plantillas/');
export const previewMultimediaTemplate = (data) => api.get('/api/plantillas/preview/', { params: data });
