import api from './api';

export const listUsers = (userId) => api.get(`/api/usuarios/listar/?user_id=${userId}`);
export const createUser = (data) => api.post('/api/usuarios/crear/', data);
export const updateUser = (userId, data) => api.put(`/api/usuarios/${userId}/gestionar/`, data);
export const deleteUser = (userId, currentUserId) => api.delete(`/api/usuarios/${userId}/gestionar/?user_id=${currentUserId}`);
