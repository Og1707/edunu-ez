import api from './api';

export const getGameCategories = () => api.get('/api/juegos/categorias/');
export const getGames = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return api.get(`/api/juegos/listar/${query ? `?${query}` : ''}`);
};
export const startStudentActivity = (data) => api.post('/api/estudiante/actividades/iniciar/', data);
export const completeStudentActivity = (data) => api.post('/api/estudiante/actividades/completar/', data);
export const getStudentActivities = (userId) => api.get(`/api/estudiante/actividades/?user_id=${userId}`);
export const getStudentStats = (userId) => api.get(`/api/estudiante/estadisticas/?user_id=${userId}`);
