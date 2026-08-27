import api from './api';

export const listUsers = () => api.get('/api/usuarios/listar/');
export const createUser = (data) => api.post('/api/usuarios/crear/', data);
export const updateUser = (userId, data) => api.put(`/api/usuarios/${userId}/gestionar/`, data);
export const deleteUser = (userId) => api.delete(`/api/usuarios/${userId}/gestionar/`);
