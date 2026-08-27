import api from './api';

export const getGameCategories = () => api.get('/api/juegos/categorias/');
export const getGames = (params = {}) => {
  const query = new URLSearchParams(params).toString();
  return api.get(`/api/juegos/listar/${query ? `?${query}` : ''}`);
};
export const startStudentActivity = (data) => api.post('/api/estudiante/actividades/iniciar/', data);
export const completeStudentActivity = (data) => api.post('/api/estudiante/actividades/completar/', data);
export const getStudentActivities = () => api.get('/api/estudiante/actividades/');
export const getStudentStats = () => api.get('/api/estudiante/estadisticas/');
