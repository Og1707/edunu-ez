import api from './api';

export const getGameCategories = () => api.get('/api/juegos/categorias/');
export const getGames = (params = {}) => api.get('/api/juegos/listar/', { params });
export const startStudentActivity = (data) => api.post('/api/estudiante/actividades/iniciar/', data);
export const completeStudentActivity = (data) => api.post('/api/estudiante/actividades/completar/', data);
export const getStudentActivities = () => api.get('/api/estudiante/actividades/');
export const getStudentStats = () => api.get('/api/estudiante/estadisticas/');
export const startGameSession = (data) => api.post('/api/juegos/iniciar-partida/', data);
export const finishGameSession = (data) => api.post('/api/juegos/finalizar-partida/', data);
