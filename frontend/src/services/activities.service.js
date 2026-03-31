import api from './api';

export const getTeacherActivities = (userId) => api.get(`/api/actividades/profesor/?user_id=${userId}`);
export const getCourses = () => api.get('/api/cursos/');
export const getActivityTypes = () => api.get('/api/tipos-actividad/');
export const getCourseStudents = (cursoId, userId) => api.get(`/api/estudiantes-curso/?curso_id=${cursoId}&user_id=${userId}`);
export const assignActivityToCourse = (data) => api.post('/api/asignar-actividad-curso/', data);
export const addStudentToCourse = (data) => api.post('/api/estudiantes-curso/agregar/', data);
export const updateActivity = (actividadId, formData) => api.put(`/api/actividades/${actividadId}/gestionar/`, formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});
export const deleteActivity = (actividadId, userId) => api.delete(`/api/actividades/${actividadId}/gestionar/?user_id=${userId}`);
export const createActivity = (activityData, config) => api.post('/api/actividades/', activityData, config);
export const getScienceSubjects = () => api.get('/api/ciencias/materias/');
